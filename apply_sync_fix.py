import sys
sys.stdout.reconfigure(encoding='utf-8')
path = 'C:/Users/Maria Oktavia/Documents/Trading-Bot-Ryzen'
with open(path + '/app.py', 'r', encoding='utf-8') as f:
    content = f.read()
# Read the helper function
with open(path + '/sync_helper.py', 'r', encoding='utf-8') as f:
    helper = f.read()
# Insert helper before sync_closed_trades
content = content.replace('def sync_closed_trades():', helper + '\n\n\ndef sync_closed_trades():')
# Replace the SYNC_CLOSE string literal
content = content.replace(
    'trade.get( close_reason) or SYNC_CLOSE',
    'trade.get(close_reason) or _infer_close_reason(trade)'
)
with open(path + '/app.py', 'w', encoding='utf-8') as f:
    f.write(content)
import py_compile
py_compile.compile(path + '/app.py', doraise=True)
print('Fix applied successfully')
