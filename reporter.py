import csv
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
TRADES_FILE = BASE / "trades.json"
SETTINGS_FILE = BASE / "runtime_settings.json"
REPORT_DIR = BASE / "reports"

if not REPORT_DIR.exists():
    REPORT_DIR.mkdir()

def parse_float(value, default=0.0):
    try: return float(value or default)
    except: return default

def parse_dt(value):
    if not value:
        return None
    text = str(value).strip().replace("Z", "")
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f"):
        try: return datetime.strptime(text, fmt)
        except: continue
    for size, fmt in ((19, "%Y-%m-%d %H:%M:%S"), (19, "%Y-%m-%dT%H:%M:%S"), (26, "%Y-%m-%dT%H:%M:%S.%f")):
        try: return datetime.strptime(text[:size], fmt)
        except: continue
    return None

def summarize(trades):
    pnls = [parse_float(trade.get("pnl")) for trade in trades]
    total = len(pnls)
    wins = sum(1 for p in pnls if p > 0)
    losses = sum(1 for p in pnls if p < 0)
    be = total - wins - losses
    gp = sum(p for p in pnls if p > 0)
    gl = sum(p for p in pnls if p < 0)
    return {
        "trades": total,
        "wins": wins,
        "losses": losses,
        "breakeven": be,
        "win_rate": (wins/total*100) if total else 0.0,
        "total_pnl": sum(pnls),
        "avg_pnl": (sum(pnls)/total) if total else 0.0,
        "gross_profit": gp,
        "gross_loss": gl,
        "avg_win": gp/wins if wins else 0.0,
        "avg_loss": gl/losses if losses else 0.0,
        "profit_factor": gp/abs(gl) if gl else 0.0,
    }

def table(headers, rows):
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(item) for item in row) + " |")
    return "\n".join(lines)

def main():
    trades = json.loads(TRADES_FILE.read_text(encoding="utf-8")) if TRADES_FILE.exists() else []
    settings = json.loads(SETTINGS_FILE.read_text(encoding="utf-8")) if SETTINGS_FILE.exists() else {}
    closed = [t for t in trades if t.get("status") == "CLOSED"]
    open_trades = [t for t in trades if t.get("status") == "OPEN"]
    closed_sorted = sorted(closed, key=lambda t: parse_dt(t.get("closed_time")) or parse_dt(t.get("time")) or datetime.min)
    now = datetime.now()

    overall = summarize(closed_sorted)

    # Today
    today_start = datetime(now.year, now.month, now.day)
    today_trades = [t for t in closed_sorted if (parse_dt(t.get("closed_time")) or parse_dt(t.get("time")) or datetime.min) >= today_start]
    today_stats = summarize(today_trades)

    by_symbol = defaultdict(list)
    for t in closed_sorted:
        by_symbol[str(t.get("symbol") or "-")].append(t)

    symbol_rows = []
    for sym, items in by_symbol.items():
        r = summarize(items)
        symbol_rows.append([sym, r["trades"], f'{r["win_rate"]:.2f}%', f'{r["total_pnl"]:.2f}', f'{r["avg_pnl"]:.4f}'])
    symbol_rows.sort(key=lambda r: (float(r[3]), int(r[1])), reverse=True)

    last20 = closed_sorted[-20:]
    last20_stats = summarize(last20)

    total_margin = sum(
        parse_float(t.get("margin")) for t in trades if t.get("status") == "OPEN"
    )
    max_positions = settings.get("max_open_positions", "20")
    open_count = len(open_trades)

    report = []
    report.append(f"# Trading Bot Report - {now:%Y-%m-%d %H:%M}\n")
    report.append(f"**Generated**: {now:%Y-%m-%d %H:%M:%S}  ")
    report.append(f"**Bot Status**: RUNNING  ")
    report.append(f"**Uptime**: since {now:%H:%M}\n")

    report.append("---")
    report.append("## Current Status\n")
    report.append(table(["Metric", "Value"], [
        ["Open Positions", f"{open_count} / {max_positions}"],
        ["Active Margin", f"{total_margin:.2f} USDT"],
        ["Today PnL", f'{today_stats["total_pnl"]:.2f} USDT'],
        ["Today Win Rate", f'{today_stats["win_rate"]:.2f}%'],
        ["Today Trades", today_stats["trades"]],
        ["Today Wins", today_stats["wins"]],
        ["Today Losses", today_stats["losses"]],
        ["Strategy Mode", settings.get("strategy_mode", "-")],
        ["Min Score", settings.get("min_score", "-")],
        ["Leverage", settings.get("default_leverage", "-")],
    ]))

    report.append("\n## Overall Performance\n")
    report.append(table(["Metric", "Value"], [
        ["Total Closed Trades", overall["trades"]],
        ["Open Trades", len(open_trades)],
        ["Wins", overall["wins"]],
        ["Losses", overall["losses"]],
        ["Breakeven", overall["breakeven"]],
        ["Win Rate", f'{overall["win_rate"]:.2f}%'],
        ["Total PnL", f'{overall["total_pnl"]:.2f}'],
        ["Profit Factor", f'{overall["profit_factor"]:.2f}'],
        ["Avg Win", f'{overall["avg_win"]:.4f}'],
        ["Avg Loss", f'{overall["avg_loss"]:.4f}'],
    ]))

    report.append("\n## Last 20 Trades\n")
    report.append(table(["Metric", "Value"], [
        ["Trades", last20_stats["trades"]],
        ["Win Rate", f'{last20_stats["win_rate"]:.2f}%'],
        ["Total PnL", f'{last20_stats["total_pnl"]:.2f}'],
    ]))

    report.append("\n## Top Symbols by PnL\n")
    top = [r for r in symbol_rows if int(r[1]) >= 1][:10]
    report.append(table(["Symbol", "Trades", "Win Rate", "Total PnL", "Avg PnL"], top if top else [["-", "0", "0%", "0", "0"]]))

    # Recent trades
    report.append("\n## Recent Closed Trades (Last 10)\n")
    recent = closed_sorted[-10:]
    if recent:
        rows = []
        for t in reversed(recent):
            rows.append([
                t.get("symbol", "-"),
                t.get("side", "-"),
                f'{parse_float(t.get("pnl")):.2f}',
                t.get("close_reason", "-"),
            ])
        report.append(table(["Symbol", "Side", "PnL", "Reason"], rows))
    else:
        report.append("No trades yet.\n")

    report.append("\n## Configuration\n")
    cfg_keys = ["strategy_mode", "min_score", "default_leverage", "max_open_positions",
                "risk_per_trade_percent", "auto_close_roi_percent", "hard_stop_roi_percent",
                "trailing_enabled", "trading_style", "ai_min_confidence"]
    cfg_rows = [[k, settings.get(k, "-")] for k in cfg_keys if k in settings]
    report.append(table(["Setting", "Value"], cfg_rows))

    report.append("\n---")
    report.append("\n*Auto-generated every hour*\n")

    ts = now.strftime("%Y%m%d_%H%M%S")
    report_file = REPORT_DIR / f"report_{ts}.md"
    latest_file = BASE / "REPORT_LATEST.md"
    report_text = "\n".join(report) + "\n"
    report_file.write_text(report_text, encoding="utf-8")
    latest_file.write_text(report_text, encoding="utf-8")
    print(f"Report: {report_file}")
    print(f"Latest: {latest_file}")

if __name__ == "__main__":
    main()
