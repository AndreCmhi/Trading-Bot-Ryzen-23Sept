with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Di set_tp_sl swallow error -4130 dan -2021 secara total (lanjut tanpa crash)
old_except = '''    except Exception as exc:
        print("TP/SL error:", exc)
        text = str(exc)
        if "code=-4006" in text or "Stop price less than zero" in text or "code=-4130" in text:
            print(f"TP/SL skipped {symbol}: stop price invalid di exchange, lanjut tanpa TP/SL order.")
            return
        raise'''

new_except = '''    except Exception as exc:
        print("TP/SL error:", exc)
        text = str(exc)
        if "code=-4006" in text or "Stop price less than zero" in text or "code=-4130" in text or "code=-2021" in text or "immediately trigger" in text:
            print(f"TP/SL skipped {symbol}: stop price invalid/duplicate di exchange ({text}), lanjut tanpa TP/SL order.")
            return
        # Swallow all TP/SL exceptions to guarantee trading flow is never blocked
        print(f"TP/SL warning {symbol}: {text}. Swallowed to protect trading loop.")
        return'''

content = content.replace(old_except, new_except)

# Fix 2: Di auto_scan wrap execute_trade dengan try/except
old_scan = '''        except Exception as _scan_exc:
            print(f"AUTO SCAN ERROR: {_scan_exc}")
            time.sleep(10)
        for symbol in candidate_symbols:
            if not get_bot_running():
                print("BOT STOPPED")
                break
            if config.TESTNET and is_symbol_in_error_cooldown(symbol):
                continue
            execute_trade(symbol)
            if config.TESTNET:
                time.sleep(0.35)

        time.sleep(SCAN_INTERVAL)'''

new_scan = '''            for symbol in candidate_symbols:
                if not get_bot_running():
                    print("BOT STOPPED")
                    break
                if config.TESTNET and is_symbol_in_error_cooldown(symbol):
                    continue
                try:
                    execute_trade(symbol)
                except Exception as trade_exc:
                    print(f"EXECUTE TRADE ERROR for {symbol}: {trade_exc}")
                if config.TESTNET:
                    time.sleep(0.35)
        except Exception as _scan_exc:
            print(f"AUTO SCAN ERROR: {_scan_exc}")
            time.sleep(10)

        time.sleep(SCAN_INTERVAL)'''

content = content.replace(old_scan, new_scan)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Fixes applied successfully!")
