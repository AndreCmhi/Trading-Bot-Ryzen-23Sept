with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix: When adopting position, cancel existing TP/SL first before setting new ones
old = '''def set_tp_sl(symbol, side, entry, atr_percent=None, risk_mode="normal", tp_percent=None, sl_percent=None, leverage=None):
    try:
        tp, sl = get_tp_sl_prices('''

new = '''def set_tp_sl(symbol, side, entry, atr_percent=None, risk_mode="normal", tp_percent=None, sl_percent=None, leverage=None, force=False):
    try:
        # Cancel existing TP/SL before setting new ones (prevent -4130 duplicate order error)
        if not force:
            try:
                existing_orders = call_binance("futures_get_open_orders", symbol=symbol)
                if existing_orders:
                    print(f"Found {len(existing_orders)} existing orders for {symbol}, canceling first...")
                    call_binance("futures_cancel_all_open_orders", symbol=symbol)
                    time.sleep(0.3)
            except Exception as cancel_err:
                print(f"Cancel check error {symbol}: {cancel_err}")
        
        tp, sl = get_tp_sl_prices('''

content = content.replace(old, new)
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Fixed set_tp_sl to cancel existing orders first')
