with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove daemon=True from all threading.Thread calls
content = content.replace('.start()', '.start()')
# Replace specific daemon calls (if they're using daemon=True)
content = content.replace(', daemon=True).start()', ').start()')

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Removed daemon mode from threads')
