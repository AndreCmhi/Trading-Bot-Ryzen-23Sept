import sys
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add flush to all print statements in auto_scan
old = '''def auto_scan():
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
            if len(candidate_symbols) == 0:
                print("AUTO SCAN: No candidates, sleeping 30s...")
                time.sleep(30)
                continue
            print(f"AUTO SCAN: Processing {len(candidate_symbols)} candidates now...")
        except Exception as _scan_exc:
            print(f"AUTO SCAN ERROR: {_scan_exc}")
            time.sleep(10)
        for symbol in candidate_symbols:'''

new = '''def auto_scan():
    print(">>> AUTO SCAN THREAD STARTED")
    sys.stdout.flush()
    while True:
        try:
            if not get_bot_running():
                print("auto_scan: bot not running, sleeping 1s...")
                sys.stdout.flush()
                time.sleep(1)
                continue

            if not symbol_filters:
                print("auto_scan: symbol_filters empty, sleeping 5s...")
                sys.stdout.flush()
                time.sleep(5)
                continue

            print("auto_scan: calling build_ranked_trade_candidates...")
            sys.stdout.flush()
            candidate_symbols = build_ranked_trade_candidates(get_scan_symbols())
            print(f"AUTO SCAN: {len(candidate_symbols)} candidates, scanning...")
            sys.stdout.flush()
            if len(candidate_symbols) == 0:
                print("AUTO SCAN: No candidates, sleeping 30s...")
                sys.stdout.flush()
                time.sleep(30)
                continue
            print(f"AUTO SCAN: Processing {len(candidate_symbols)} candidates now...")
            sys.stdout.flush()
        except Exception as _scan_exc:
            print(f"AUTO SCAN ERROR: {_scan_exc}")
            sys.stdout.flush()
            time.sleep(10)
        for symbol in candidate_symbols:'''

content = content.replace(old, new)
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Added flush statements')
