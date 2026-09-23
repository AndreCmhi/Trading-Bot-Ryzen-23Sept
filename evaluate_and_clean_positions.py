import os
from pathlib import Path
import app

BASE_DIR = Path(__file__).resolve().parent
os.chdir(BASE_DIR)
os.environ.setdefault("APP_SKIP_BOOTSTRAP", "true")

def evaluate():
    print("Refreshing market data...")
    app.load_exchange_filters()
    app.refresh_market_regime(force=True)
    app.refresh_scan_symbols(force=True)
    
    top_symbols = [s.upper() for s in app.get_scan_symbols()[:10]]
    print(f"Top 10 symbols: {top_symbols}")
    
    positions = app.get_current_positions()
    if not positions:
        print("No active positions found.")
        return

    active_symbols = []
    for pos in positions:
        symbol = pos.get('symbol', '').upper()
        if symbol:
            active_symbols.append({
                'symbol': symbol,
                'roi': float(pos.get('roi', 0)),
                'is_top10': symbol in top_symbols
            })

    print(f"Current active positions: {len(active_symbols)}")
    
    # Sort: Top 10 first, then by ROI descending
    active_symbols.sort(key=lambda x: (x['is_top10'], x['roi']), reverse=True)
    
    keep_count = 5
    to_keep = active_symbols[:keep_count]
    to_close = active_symbols[keep_count:]
    
    print(f"Keeping: {[p['symbol'] for p in to_keep]}")
    
    for pos in to_close:
        symbol = pos['symbol']
        print(f"Closing {symbol}...")
        success, message = app.close_position(symbol, reason="EVAL_CLEANUP")
        print(f"Result for {symbol}: {message}")

if __name__ == '__main__':
    evaluate()
