import csv
import json
from collections import Counter, defaultdict
from datetime import datetime

FORWARD_TEST_START = datetime(2026, 5, 27, 4, 12, 0)
from pathlib import Path

BASE = Path(__file__).resolve().parent
TRADES_FILE = BASE / "trades.json"
SETTINGS_FILE = BASE / "runtime_settings.json"
REPORT_FILE = BASE / "trade_report.md"
CSV_FILE = BASE / "trade_report_by_symbol.csv"


def parse_float(value, default=0.0):
    try:
        return float(value or default)
    except (TypeError, ValueError):
        return default


def parse_dt(value):
    if not value:
        return None
    text = str(value).strip().replace("Z", "")
    formats = ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f")
    for fmt in formats:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    for size, fmt in ((19, "%Y-%m-%d %H:%M:%S"), (19, "%Y-%m-%dT%H:%M:%S"), (26, "%Y-%m-%dT%H:%M:%S.%f")):
        try:
            return datetime.strptime(text[:size], fmt)
        except ValueError:
            continue
    return None


def summarize(trades):
    pnls = [parse_float(trade.get("pnl")) for trade in trades]
    total = len(pnls)
    wins = sum(1 for pnl in pnls if pnl > 0)
    losses = sum(1 for pnl in pnls if pnl < 0)
    breakeven = total - wins - losses
    gross_profit = sum(pnl for pnl in pnls if pnl > 0)
    gross_loss = sum(pnl for pnl in pnls if pnl < 0)
    avg_win = gross_profit / wins if wins else 0.0
    avg_loss = gross_loss / losses if losses else 0.0
    profit_factor = gross_profit / abs(gross_loss) if gross_loss else 0.0
    return {
        "trades": total,
        "wins": wins,
        "losses": losses,
        "breakeven": breakeven,
        "win_rate": (wins / total * 100) if total else 0.0,
        "total_pnl": sum(pnls),
        "avg_pnl": (sum(pnls) / total) if total else 0.0,
        "gross_profit": gross_profit,
        "gross_loss": gross_loss,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "profit_factor": profit_factor,
    }


def fmt(value):
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def table(headers, rows):
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(item) for item in row) + " |")
    return "\n".join(lines)


def main():
    trades = json.loads(TRADES_FILE.read_text(encoding="utf-8")) if TRADES_FILE.exists() else []
    settings = json.loads(SETTINGS_FILE.read_text(encoding="utf-8")) if SETTINGS_FILE.exists() else {}
    closed = [trade for trade in trades if trade.get("status") == "CLOSED"]
    open_trades = [trade for trade in trades if trade.get("status") == "OPEN"]
    closed_sorted = sorted(closed, key=lambda trade: parse_dt(trade.get("closed_time")) or parse_dt(trade.get("time")) or datetime.min)

    overall = summarize(closed_sorted)
    by_reason = defaultdict(list)
    by_symbol = defaultdict(list)
    for trade in closed_sorted:
        by_reason[str(trade.get("close_reason") or "-")].append(trade)
        by_symbol[str(trade.get("symbol") or "-")].append(trade)

    symbol_rows = []
    for symbol, items in by_symbol.items():
        result = summarize(items)
        symbol_rows.append([
            symbol,
            result["trades"],
            f'{result["win_rate"]:.2f}%',
            f'{result["total_pnl"]:.2f}',
            f'{result["avg_pnl"]:.4f}',
        ])
    symbol_rows.sort(key=lambda row: (float(row[3]), int(row[1])), reverse=True)

    reason_rows = []
    for reason, items in by_reason.items():
        result = summarize(items)
        reason_rows.append([
            reason,
            result["trades"],
            f'{result["win_rate"]:.2f}%',
            f'{result["total_pnl"]:.2f}',
            f'{result["avg_pnl"]:.4f}',
        ])
    reason_rows.sort(key=lambda row: int(row[1]), reverse=True)

    bad_symbols = [row for row in symbol_rows if int(row[1]) >= 2 and float(row[3]) < 0][:15]
    good_symbols = [row for row in symbol_rows if int(row[1]) >= 2 and float(row[3]) > 0][:15]
    last20 = closed_sorted[-20:]
    last20_stats = summarize(last20)
    forward_trades = [
        trade for trade in closed_sorted
        if (parse_dt(trade.get("closed_time")) or parse_dt(trade.get("time")) or datetime.min) >= FORWARD_TEST_START
    ]
    forward_stats = summarize(forward_trades)

    report = []
    report.append(f"# Trading Bot Report\n")
    report.append(f"Generated: {datetime.now():%Y-%m-%d %H:%M:%S}\n")
    report.append("## Current Runtime Settings")
    report.append(table(["Setting", "Value"], [[key, settings.get(key)] for key in [
        "strategy_mode", "min_score", "auto_close_roi_percent", "trailing_enabled",
        "trailing_trigger_roi_percent", "trailing_callback_roi_percent", "fast_trailing_enabled",
        "fast_trailing_trigger_roi_percent", "fast_trailing_callback_roi_percent",
        "hard_stop_roi_percent", "max_trades_per_hour", "max_symbol_trades_per_day",
    ]]))
    report.append("\n## Overall Closed Trades")
    report.append(table(["Metric", "Value"], [[
        "Closed trades", overall["trades"]], ["Open trades", len(open_trades)], ["Wins", overall["wins"]],
        ["Losses", overall["losses"]], ["Breakeven", overall["breakeven"]], ["Win rate", f'{overall["win_rate"]:.2f}%'],
        ["Total PnL", f'{overall["total_pnl"]:.2f}'], ["Average PnL", f'{overall["avg_pnl"]:.4f}'],
        ["Profit factor", f'{overall["profit_factor"]:.2f}'], ["Avg win", f'{overall["avg_win"]:.4f}'],
        ["Avg loss", f'{overall["avg_loss"]:.4f}'],
    ]))
    report.append("\n## Last 20 Closed Trades")
    report.append(table(["Metric", "Value"], [["Closed trades", last20_stats["trades"]], ["Win rate", f'{last20_stats["win_rate"]:.2f}%'], ["Total PnL", f'{last20_stats["total_pnl"]:.2f}']]))
    report.append(f"\n## Forward Test Since {FORWARD_TEST_START:%Y-%m-%d %H:%M:%S}")
    report.append(table(["Metric", "Value"], [["Closed trades", forward_stats["trades"]], ["Wins", forward_stats["wins"]], ["Losses", forward_stats["losses"]], ["Breakeven", forward_stats["breakeven"]], ["Win rate", f'{forward_stats["win_rate"]:.2f}%'], ["Total PnL", f'{forward_stats["total_pnl"]:.2f}']]))
    if forward_trades:
        report.append("\n" + table(["Closed", "Symbol", "PnL", "Reason"], [[trade.get("closed_time"), trade.get("symbol"), trade.get("pnl"), trade.get("close_reason")] for trade in forward_trades[-20:]]))
    report.append("\n## Close Reason Performance")
    report.append(table(["Reason", "Trades", "Win Rate", "Total PnL", "Avg PnL"], reason_rows))
    report.append("\n## Best Symbols")
    report.append(table(["Symbol", "Trades", "Win Rate", "Total PnL", "Avg PnL"], good_symbols))
    report.append("\n## Worst Symbols")
    report.append(table(["Symbol", "Trades", "Win Rate", "Total PnL", "Avg PnL"], bad_symbols))
    report.append("\n## Recommendation")
    report.append("- Forward-test only on Binance Testnet until at least 30 new closed trades after SCALPING patch.")
    report.append("- Pass condition: new closed trades >= 30, win rate > 55%, total PnL >= 0, no hard-stop cluster.")
    report.append("- Keep trend and pullback filters enabled; do not raise max trades per hour before pass condition.")
    REPORT_FILE.write_text("\n".join(report) + "\n", encoding="utf-8")

    with CSV_FILE.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["symbol", "trades", "win_rate", "total_pnl", "avg_pnl"])
        writer.writerows(symbol_rows)

    print(f"Wrote {REPORT_FILE}")
    print(f"Wrote {CSV_FILE}")
    print(f"closed={overall['trades']} winrate={overall['win_rate']:.2f}% pnl={overall['total_pnl']:.2f}")
    print(f"last20_winrate={last20_stats['win_rate']:.2f}% last20_pnl={last20_stats['total_pnl']:.2f}")


if __name__ == "__main__":
    main()
