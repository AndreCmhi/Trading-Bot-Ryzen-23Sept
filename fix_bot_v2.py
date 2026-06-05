import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add 'breakeven_done' field to update_open_trade_record call
old_update = '''                update_open_trade_record(
                    symbol,
                    {
                        "peak_roi": round(peak_roi, 2),
                        "breakeven_armed": breakeven_armed or pct >= breakeven_trigger,
                        "trailing_armed": trailing_armed or pct >= trailing_trigger,
                    },
                )'''

new_update = '''                newly_breakeven_armed = (breakeven_armed or pct >= breakeven_trigger) and not breakeven_armed
                update_open_trade_record(
                    symbol,
                    {
                        "peak_roi": round(peak_roi, 2),
                        "breakeven_armed": breakeven_armed or pct >= breakeven_trigger,
                        "trailing_armed": trailing_armed or pct >= trailing_trigger,
                        "breakeven_done": bool(trade.get("breakeven_done")),
                    },
                )'''

content = content.replace(old_update, new_update)

# 2. Insert breakeven SL move logic after update_open_trade_record
old_be_move = '''                if scalping_mode and pct >= partial_trigger:'''

new_be_move = '''                # MOVE SL TO ENTRY when breakeven armed and not yet moved
                if (breakeven_armed or pct >= breakeven_trigger) and not trade.get("breakeven_done") and not partial_done:
                    try:
                        new_sl = entry * (0.999 if side == "BUY" else 1.001)  # SL at entry + tiny buffer
                        cancel_open_orders(symbol)
                        time.sleep(0.2)
                        call_binance(
                            "futures_create_order",
                            symbol=symbol,
                            side="SELL" if side == "BUY" else "BUY",
                            type="STOP_MARKET",
                            stopPrice=round(new_sl, 8),
                            closePosition=True,
                        )
                        update_open_trade_record(symbol, {"breakeven_done": True})
                        print(f"BREAKEVEN SL MOVED {symbol}: SL moved to entry")
                    except Exception as sl_err:
                        print(f"BREAKEVEN SL MOVE ERROR {symbol}: {sl_err}")

                if scalping_mode and pct >= partial_trigger:'''

content = content.replace(old_be_move, new_be_move)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Applied breakeven SL move fix')
