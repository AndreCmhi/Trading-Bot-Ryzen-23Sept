import json
from pathlib import Path
from datetime import datetime, timedelta

BASE = Path(__file__).resolve().parent
TRADES = BASE / "trades.json"
OUT = BASE / "performance_summary.txt"


def parse_dt(value):
    if not value:
        return None
    text = str(value).strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f"):
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


def summarize(minutes=30):
    if not TRADES.exists():
        return "trades.json tidak ditemukan"
    data = json.loads(TRADES.read_text(encoding="utf-8"))
    now = datetime.now()
    cutoff = now - timedelta(minutes=minutes)

    closed = []
    for t in data:
        if t.get("status") != "CLOSED":
            continue
        closed_time = parse_dt(t.get("closed_time")) or parse_dt(t.get("time"))
        if closed_time and closed_time >= cutoff:
            closed.append(t)

    total = len(closed)
    if total == 0:
        return f"[{now:%Y-%m-%d %H:%M:%S}] {minutes}m: belum ada trade CLOSED"

    pnl_list = [float(t.get("pnl", 0) or 0) for t in closed]
    wins = sum(1 for p in pnl_list if p > 0)
    losses = sum(1 for p in pnl_list if p < 0)
    be = total - wins - losses
    win_rate = (wins / total) * 100
    total_pnl = sum(pnl_list)
    avg_pnl = total_pnl / total

    streak = 0
    max_streak = 0
    for p in pnl_list:
        if p < 0:
            streak += 1
            max_streak = max(max_streak, streak)
        else:
            streak = 0

    return (
        f"[{now:%Y-%m-%d %H:%M:%S}] {minutes}m | closed={total} | "
        f"win={wins} loss={losses} be={be} | winrate={win_rate:.2f}% | "
        f"total_pnl={total_pnl:.2f} | avg_pnl={avg_pnl:.4f} | max_loss_streak={max_streak}"
    )


if __name__ == "__main__":
    line = summarize(30)
    print(line)
    with OUT.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
