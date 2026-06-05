with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add more debug prints
old = '''        candidate_symbols = build_ranked_trade_candidates(get_scan_symbols())
            print(f"AUTO SCAN: {len(candidate_symbols)} candidates, scanning...")
            if len(candidate_symbols) == 0:
                print("AUTO SCAN: No candidates, sleeping 30s...")
                time.sleep(30)
                continue'''

new = '''        candidate_symbols = build_ranked_trade_candidates(get_scan_symbols())
            print(f"AUTO SCAN loop: {len(candidate_symbols)} candidates, scanning...")
            if len(candidate_symbols) == 0:
                print("AUTO SCAN: No candidates, sleeping 30s...")
                time.sleep(30)
                continue
            print(f"AUTO SCAN: Processing {len(candidate_symbols)} candidates now...")'''

content = content.replace(old, new)
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('More debug')
