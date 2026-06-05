with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''def auto_scan():
    while True:
        try:
            if not get_bot_running():
                time.sleep(1)
                continue

            if not symbol_filters:
                time.sleep(5)
                continue

            candidate_symbols = build_ranked_trade_candidates(get_scan_symbols())'''

new = '''def auto_scan():
    print("AUTO SCAN LOOP STARTED")
    while True:
        try:
            if not get_bot_running():
                time.sleep(1)
                continue

            if not symbol_filters:
                print("auto_scan: symbol_filters is empty, waiting...")
                time.sleep(5)
                continue

            print("auto_scan: fetching scan symbols...")
            scan_syms = get_scan_symbols()
            print(f"auto_scan: scan symbols fetched ({len(scan_syms)}). building candidates...")
            candidate_symbols = build_ranked_trade_candidates(scan_syms)
            print(f"auto_scan: candidates built ({len(candidate_symbols)})")'''

content = content.replace(old, new)
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Added scan debug prints')
