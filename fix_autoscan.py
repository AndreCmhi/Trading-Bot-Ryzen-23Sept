with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add try/except wrapper to auto_scan loop
old = '''def auto_scan():
    while True:
        if not get_bot_running():
            time.sleep(1)
            continue

        candidate_symbols = build_ranked_trade_candidates(get_scan_symbols())'''

new = '''def auto_scan():
    while True:
        try:
            if not get_bot_running():
                time.sleep(1)
                continue

            if not symbol_filters:
                time.sleep(5)
                continue

            candidate_symbols = build_ranked_trade_candidates(get_scan_symbols())'''

content = content.replace(old, new)

# Add the closing try/except after time.sleep(SCAN_INTERVAL)
old2 = '''        time.sleep(SCAN_INTERVAL)


def auto_close():'''

new2 = '''        except Exception as _scan_exc:
            print(f"Auto scan error: {_scan_exc}")
        time.sleep(SCAN_INTERVAL)


def auto_close():'''

content = content.replace(old2, new2)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Fixed auto_scan')
