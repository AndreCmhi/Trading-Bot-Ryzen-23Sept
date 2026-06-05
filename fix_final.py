with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''def auto_scan():
    while True:
        if not get_bot_running():
            time.sleep(1)
            continue

        candidate_symbols = build_ranked_trade_candidates(get_scan_symbols())'''

new = '''def auto_scan():
    print(">>> AUTO SCAN THREAD STARTED")
    while True:
        try:
            if not get_bot_running():
                time.sleep(1)
                continue

            if not symbol_filters:
                time.sleep(5)
                continue

            candidate_symbols = build_ranked_trade_candidates(get_scan_symbols())
            print(f"AUTO SCAN: {len(candidate_symbols)} candidates, scanning...")
        except Exception as _scan_exc:
            print(f"AUTO SCAN ERROR: {_scan_exc}")
            time.sleep(10)'''

content = content.replace(old, new)
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Fixed auto_scan with proper exception handling')
