import app
import time

def cleanup():
    app.refresh_scan_symbols(force=True)
    top10 = [s.upper() for s in app.get_scan_symbols()[:10]]
    positions = app.get_current_positions()
    active_symbols = [p['symbol'] for p in positions]
    
    # Keep 5 that are in Top 10, or just first 5 if not enough
    to_keep = [s for s in active_symbols if s in top10][:5]
    if len(to_keep) < 5:
        needed = 5 - len(to_keep)
        for s in active_symbols:
            if s not in to_keep and len(to_keep) < 5:
                to_keep.append(s)
                
    to_close = [s for s in active_symbols if s not in to_keep]
    print(f'Keeping: {to_keep}')
    print(f'Closing: {to_close}')
    
    for s in to_close:
        print(f'Closing {s}...')
        app.close_position(s, reason='MANUAL_CLEANUP_BATCH')
        time.sleep(2) # Jeda untuk menghindari timeout/API limit

if __name__ == '__main__':
    cleanup()
