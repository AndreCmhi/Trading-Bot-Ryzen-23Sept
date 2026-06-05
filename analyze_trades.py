import json
with open('trades.json') as f:
    trades = json.load(f)
closed = [t for t in trades if t.get('status') == 'CLOSED']
real = [t for t in closed if t.get('ai_mode') != 'sync-adopt']
print('=== REAL BOT TRADES ===')
print('Total: ' + str(len(real)))
if real:
    wins = sum(1 for t in real if float(t.get('pnl',0) or 0) > 0)
    losses = sum(1 for t in real if float(t.get('pnl',0) or 0) < 0)
    be = sum(1 for t in real if float(t.get('pnl',0) or 0) == 0)
    pnl = sum(float(t.get('pnl',0) or 0) for t in real)
    print('Wins: ' + str(wins) + ', Losses: ' + str(losses) + ', BE: ' + str(be))
    print('Winrate: ' + str(round(wins/len(real)*100, 2)) + '%')
    print('Total PnL: ' + str(round(pnl, 2)) + ' USDT')
    print()
    print('=== Last 10 Real Trades ===')
    for t in real[-10:]:
        p = float(t.get('pnl',0) or 0)
        print('  ' + str(t.get('symbol','?')) + ' ' + str(t.get('side','?')) + ' | PnL: ' + str(round(p,2)) + ' | Close: ' + str(t.get('close_reason','?')) + ' | Score: ' + str(t.get('score','?')) + ' | ' + str(t.get('closed_time', t.get('time','?'))))
    print()
    from collections import Counter
    reasons = Counter(t.get('close_reason','UNKNOWN') for t in real)
    print('Close Reasons:')
    for r, c in reasons.most_common():
        print('  ' + str(r) + ': ' + str(c))
