import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern matching set_tp_sl except block
pattern = r'except Exception as exc:\s+print\("TP/SL error:", exc\)\s+text = str\(exc\)\s+if "code=-4006" in text or "Stop price less than zero" in text.*?:.*?return\s+raise'

replacement = '''except Exception as exc:
        print("TP/SL error:", exc)
        text = str(exc)
        if "code=-4006" in text or "Stop price less than zero" in text or "code=-4130" in text or "code=-2021" in text or "immediately trigger" in text:
            print(f"TP/SL skipped {symbol}: stop price invalid/duplicate di exchange ({text}), lanjut tanpa TP/SL order.")
            return
        # Swallow all TP/SL exceptions to guarantee trading flow is never blocked
        print(f"TP/SL warning {symbol}: {text}. Swallowed to protect trading loop.")
        return'''

content = re.sub(
    r'except Exception as exc:\s+print\("TP/SL error:", exc\)\s+text = str\(exc\)\s+if "code=-4006" in text or "Stop price less than zero" in text or "code=-4130" in text:\s+print\(f"TP/SL skipped {symbol}: stop price invalid di exchange, lanjut tanpa TP/SL order."\)\s+return\s+raise',
    replacement,
    content,
    flags=re.DOTALL
)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Regex replace applied")
