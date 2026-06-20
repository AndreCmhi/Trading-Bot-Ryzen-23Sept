import state
from utils import load_trades, get_runtime_settings

def calculate_stats():
    trades = load_trades()
    # Filter closed trades
    closed = [t for t in trades if t.get('status') == 'CLOSED']
    total_pnl = sum(float(t.get('realized_pnl', 0)) for t in closed)
    win_count = sum(1 for t in closed if float(t.get('realized_pnl', 0)) > 0)
    winrate = (win_count / len(closed) * 100) if closed else 0
    return {
        'total_pnl': round(total_pnl, 2),
        'winrate': round(winrate, 2),
        'total_trades': len(closed),
        'active_positions': len(state.scan_symbols)
    }
