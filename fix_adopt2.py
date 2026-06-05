with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix adopt function to not set TP/SL if already exists
old = '''        add_trade(trade)
        set_tp_sl(symbol, side, entry, atr_percent=setup.get("atr_percent"), risk_mode=risk_mode, tp_percent=order_plan["tp_percent"], sl_percent=order_plan["sl_percent"], leverage=effective_leverage)'''

new = '''        add_trade(trade)
        # Check if TP/SL already exists on exchange before setting new ones
        try:
            existing = call_binance("futures_get_open_orders", symbol=symbol)
            if existing:
                print(f"{symbol} already has TP/SL orders on exchange, skipping set_tp_sl")
                # Just load existing TP/SL prices
                tp_price = None
                sl_price = None
                for o in existing:
                    if o.get('type') == 'TAKE_PROFIT_MARKET':
                        tp_price = o.get('stopPrice')
                    elif o.get('type') == 'STOP_MARKET':
                        sl_price = o.get('stopPrice')
                trade['tp_price'] = float(tp_price or 0)
                trade['sl_price'] = float(sl_price or 0)
            else:
                set_tp_sl(symbol, side, entry, atr_percent=setup.get("atr_percent"), risk_mode=risk_mode, tp_percent=order_plan["tp_percent"], sl_percent=order_plan["sl_percent"], leverage=effective_leverage, force=True)
        except Exception as e:
            print(f"TP/SL check error {symbol}: {e}")
            set_tp_sl(symbol, side, entry, atr_percent=setup.get("atr_percent"), risk_mode=risk_mode, tp_percent=order_plan["tp_percent"], sl_percent=order_plan["sl_percent"], leverage=effective_leverage, force=True)'''

content = content.replace(old, new)
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Fixed adopt to check existing TP/SL first')
