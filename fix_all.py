import re
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()
# 1. Fix ai_decision.py SL (already applied? we'll ensure)
# Actually we need to modify ai_decision.py separately
# But we already did earlier; let's just verify
with open('ai_decision.py', 'r', encoding='utf-8') as f:
    ai_content = f.read()
if 'sl_percent = round(max(atr_percent * 1.5, 0.5), 4)' not in ai_content:
    ai_content = ai_content.replace(
        'sl_percent = round(max(atr_percent * 1.15, 0.35), 4)',
        'sl_percent = round(max(atr_percent * 1.5, 0.5), 4)'
    )
    with open('ai_decision.py', 'w', encoding='utf-8') as f:
        f.write(ai_content)
    print('Updated ai_decision.py SL')
else:
    print('ai_decision.py SL already ok')
# 2. Fix app.py breakeven trigger (scalping mode)
content = re.sub(
    r'breakeven_trigger = max\(0\.45, partial_trigger - float\(profile\["breakeven_buffer"\]\)\)',
    'breakeven_trigger = max(1.5, partial_trigger - float(profile["breakeven_buffer"]))',
    content
)
# 3. Fix breakeven giveback
content = re.sub(
    r'breakeven_giveback = max\(0\.25 if recovery_guard_active else 0\.35, breakeven_trigger \\* \(0\.4 if recovery_guard_active else 0\.5\)\)',
    'breakeven_giveback = max(0.5 if recovery_guard_active else 0.6, breakeven_trigger * (0.6 if recovery_guard_active else 0.7))',
    content
)
# 4. Fix recovery mode thresholds (BUY side)
content = re.sub(
    r'side == "BUY"\s+and\s+int\(overall_recent_bucket\.get\("count", 0\) or 0\) >= 4\s+and\s+int\(overall_recent_bucket\.get\("consecutive_losses", 0\) or 0\) >= 2',
    r'side == "BUY" and int(overall_recent_bucket.get("count", 0) or 0) >= 6 and int(overall_recent_bucket.get("consecutive_losses", 0) or 0) >= 3',
    content
)
# 5. Fix risk guard thresholds
with open('risk_guard.py', 'r', encoding='utf-8') as f:
    rg_content = f.read()
rg_content = re.sub(r'recent_winrate < 20', 'recent_winrate < 15', rg_content)
rg_content = re.sub(r'recent_hard_stop_rate >= 0\.4', 'recent_hard_stop_rate >= 0.6', rg_content)
rg_content = re.sub(r'if recent_profit_leaks >= 2:', 'if recent_profit_leaks >= 5:', rg_content)
with open('risk_guard.py', 'w', encoding='utf-8') as f:
    f.write(rg_content)
print('Updated risk_guard.py')
# 6. Fix app.py recent_profit_leaks thresholds
content = re.sub(r'if recent_profit_leaks >= 2:', 'if recent_profit_leaks >= 5:', content)
content = re.sub(r'if safe_float\(trade\.get\("peak_roi", 0\)\) >= 1\.5', 'if safe_float(trade.get("peak_roi", 0)) >= 3.0', content)
# 7. Fix app.py history monitor recent_winrate threshold (line ~1780? we'll replace)
content = re.sub(r'recent_winrate < 25\.0', 'recent_winrate < 15.0', content)
# 8. Fix client init with retry and ping=False
client_init_pattern = r'client = Client\(\s*\n\s*config\.API_KEY,\s*\n\s*config\.API_SECRET,\s*\n\s*testnet=config\.TESTNET,\s*\n\s*requests_params=\{"timeout": 20\},\s*\n\s*\)'
client_init_replacement = '''for _init_attempt in range(10):
    try:
        client = Client(
            config.API_KEY,
            config.API_SECRET,
            testnet=config.TESTNET,
            requests_params={"timeout": 20},
            ping=False,
        )
        break
    except Exception as _init_exc:
        print(f"Binance connect attempt {_init_attempt+1}/10 failed: {_init_exc}")
        if _init_attempt < 9:
            time.sleep(10)
        else:
            raise RuntimeError("Binance API unreachable after 10 attempts") from _init_exc'''
content = re.sub(client_init_pattern, client_init_replacement, content, flags=re.DOTALL)
# 9. Ensure binance_time_offset_ms and binance_time_synced_at are present before bot_running
# We'll do a simple insert: if we see 'bot_running = True' and the two lines are not immediately before, insert them.
# But let's just ensure they exist somewhere before bot_running.
# We'll do a more robust: replace the block from socketio = ... up to bot_running = True with a clean block.
# Instead, let's just do a simple: after the socketio line, we add the two lines if not present.
lines = content.split('\n')
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    new_lines.append(line)
    if line.strip() == 'socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")':
        # Check if next two lines are the time vars; if not, insert them.
        if i+1 < len(lines) and 'binance_time_offset_ms = 0' in lines[i+1]:
            i += 1
            new_lines.append(lines[i])  # already added
            if i+1 < len(lines) and 'binance_time_synced_at = 0.0' in lines[i+1]:
                i += 1
                new_lines.append(lines[i])
            else:
                new_lines.append('binance_time_synced_at = 0.0')
        else:
            # Insert both
            new_lines.append('binance_time_offset_ms = 0')
            new_lines.append('binance_time_synced_at = 0.0')
    i += 1
content = '\n'.join(new_lines)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('All fixes applied to app.py')
