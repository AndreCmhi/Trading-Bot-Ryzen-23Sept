with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
# Add a fallback so if API fails, check if we already have a cached offset from earlier attempt
for i, line in enumerate(lines):
    if 'print(f\"BINANCE TIME SYNC ERROR: {exc}\")' in line:
        lines[i] = '        if not binance_time_synced_at:\n'
        lines[i+1] = '            client.timestamp_offset = 0\n'
        lines[i+2] = '        print(f\"BINANCE TIME SYNC ERROR: {exc}\")\n'
        break
with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Fix 2 done')
