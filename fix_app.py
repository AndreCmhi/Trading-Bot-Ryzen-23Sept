import re
with open('app.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()
# Fix 1: handle -4130 error
content = content.replace(
    'if "code=-4006" in text or "Stop price less than zero" in text:',
    'if "code=-4006" in text or "Stop price less than zero" in text or "code=-4130" in text:'
)
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Fix 1 done')
