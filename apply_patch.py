path = r"C:\Users\Maria Oktavia\Documents\Trading-Bot-Ryzen\app.py"
with open(path, "r", encoding="utf-8") as f:
    code = f.read()

target = 'if not disable_trend_filter and trend_5m != "mixed" and trend_5m != side.lower():'
replacement = 'if not disable_trend_filter and trend_5m != "mixed" and trend_5m != ("bullish" if side == "BUY" else "bearish"):'

if target in code:
    code = code.replace(target, replacement)
    with open(path, "w", encoding="utf-8") as f:
        f.write(code)
    print("PATCH SUCCESS")
else:
    print("TARGET NOT FOUND")
