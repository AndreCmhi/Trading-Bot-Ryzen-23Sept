
import re

with open(r"C:\\Users\\Maria Oktavia\\Documents\\Trading-Bot-Ryzen\\app.py", "r", encoding="utf-8") as f:
    content = f.read()

old = 'DEFAULT_RISK_PER_TRADE_PERCENT = float(os.getenv("DEFAULT_RISK_PER_TRADE_PERCENT", "1.0"))'
new = 'DEFAULT_RISK_PER_TRADE_PERCENT = float(os.getenv("DEFAULT_RISK_PER_TRADE_PERCENT", "1.0"))\nFEE_BUFFER_FACTOR = float(os.getenv("FEE_BUFFER_FACTOR", "1.5"))'

if old in content:
    content = content.replace(old, new)
    with open(r"C:\\Users\\Maria Oktavia\\Documents\\Trading-Bot-Ryzen\\app.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("REPLACED: FEE_BUFFER_FACTOR")
else:
    print("FAIL")
    idx = content.find("DEFAULT_RISK_PER_TRADE_PERCENT")
    if idx >= 0:
        print(repr(content[idx:idx+85]))
