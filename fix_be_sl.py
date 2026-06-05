import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the breakeven SL move with a simpler version that uses set_tp_sl
old_be = '''                # MOVE SL TO ENTRY when breakeven armed and not yet moved
                if (breakeven_armed or pct >= breakeven_trigger) and not trade.get(\"breakeven_done\") and not partial_done:
                    try:
                        new_sl = entry * (0.999 if side == \"BUY\" else 1.001)  # SL at entry + tiny buffer
                        cancel_open_orders(symbol)
                        time.sleep(0.2)
                        call_binance(
                            \"futures_create_order\",
                            symbol=symbol,
                            side=\"SELL\" if side == \"BUY\" else \"BUY\",
                            type=\"STOP_MARKET\",
                            stopPrice=round(new_sl, 8),
                            closePosition=True,
                        )
                        update_open_trade_record(symbol, {\"breakeven_done\": True})
                        print(f\"BREAKEVEN SL MOVED {symbol}: SL moved to entry\")
                    except Exception as sl_err:
                        print(f\"BREAKEVEN SL MOVE ERROR {symbol}: {sl_err}\")'''

new_be = '''                # MOVE SL TO ENTRY when breakeven armed and not yet moved
                if (breakeven_armed or pct >= breakeven_trigger) and not trade.get(\"breakeven_done\"):
                    try:
                        safety_margin = 0.15  # 0.15% buffer above entry for BUY, below for SELL
                        pos_entry = float(pos.get(\"entryPrice\", 0) or 0)
                        pos_side = \"BUY\" if float(pos[\"positionAmt\"]) > 0 else \"SELL\"
                        new_sl_pct = abs((pos_entry - float(trade.get(\"sl_price\", pos_entry))) / max(pos_entry, 0.0001) * 100) * 0.5
                        new_sl_pct = max(new_sl_pct, 0.2)
                        cancel_open_orders(symbol)
                        time.sleep(0.3)
                        # Restore TP + SL entry
                        orig_tp_pct = float(trade.get(\"tp_percent\", 0) or 2.0)
                        set_tp_sl(symbol, pos_side, pos_entry, tp_percent=orig_tp_pct, sl_percent=new_sl_pct, leverage=leverage)
                        update_open_trade_record(symbol, {\"breakeven_done\": True, \"sl_percent\": new_sl_pct})
                        print(f\"BREAKEVEN SL MOVED {symbol}: SL moved to {round(new_sl_pct,2)}%\")
                    except Exception as sl_err:
                        print(f\"BREAKEVEN SL MOVE ERROR {symbol}: {sl_err}\")'''

content = content.replace(old_be, new_be)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Fixed breakeven SL move')
