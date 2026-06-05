with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the sync_binance_time function to use futures endpoint
old_func = '''def sync_binance_time(force=False):
    global binance_time_offset_ms, binance_time_synced_at
    now = time.time()
    if not force and binance_time_synced_at and (now - binance_time_synced_at) < 300:
        return binance_time_offset_ms
    try:
        server_time_payload = client.get_server_time()
        server_time = int(server_time_payload.get("serverTime", 0) or 0)
        local_time = int(time.time() * 1000)
        binance_time_offset_ms = server_time - local_time
        client.timestamp_offset = binance_time_offset_ms
        binance_time_synced_at = now
    except Exception as exc:
        if not binance_time_synced_at:
            client.timestamp_offset = 0
        print(f"BINANCE TIME SYNC ERROR: {exc}")'''

new_func = '''def sync_binance_time(force=False):
    global binance_time_offset_ms, binance_time_synced_at
    now = time.time()
    if not force and binance_time_synced_at and (now - binance_time_synced_at) < 300:
        return binance_time_offset_ms
    try:
        import requests
        futures_url = "https://testnet.binancefuture.com/fapi/v1/time" if config.TESTNET else "https://fapi.binance.com/fapi/v1/time"
        r = requests.get(futures_url, timeout=5)
        r.raise_for_status()
        server_time = int(r.json().get("serverTime", 0) or 0)
        local_time = int(time.time() * 1000)
        binance_time_offset_ms = server_time - local_time
        client.timestamp_offset = binance_time_offset_ms
        binance_time_synced_at = now
    except Exception as exc:
        if not binance_time_synced_at:
            client.timestamp_offset = 0
        print(f"BINANCE TIME SYNC ERROR: {exc}")'''

content = content.replace(old_func, new_func)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Fixed sync_binance_time')
