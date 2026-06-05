with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''        candidate_symbols = build_ranked_trade_candidates(get_scan_symbols())
            print(f"AUTO SCAN: {len(candidate_symbols)} candidates, scanning...")
        for symbol in candidate_symbols:'''

new = '''        candidate_symbols = build_ranked_trade_candidates(get_scan_symbols())
            print(f"AUTO SCAN: {len(candidate_symbols)} candidates, scanning...")
            if len(candidate_symbols) == 0:
                print("AUTO SCAN: No candidates, sleeping 30s...")
                time.sleep(30)
                continue
            print(f"AUTO SCAN: Iterating {len(candidate_symbols)} symbols...")
        for idx, symbol in enumerate(candidate_symbols):
            if idx == 0:
                print(f"AUTO SCAN: Checking first symbol: {symbol}")'''

content = content.replace(old, new)
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Added more scan debug')
