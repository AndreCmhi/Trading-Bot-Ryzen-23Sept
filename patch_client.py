with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add monkey patch right after client initialization
old = '''        break
    except Exception as _init_exc:'''

new = '''        # Monkey patch get_server_time to use futures endpoint since spot testnet is 502
        def custom_get_server_time():
            import requests
            url = "https://testnet.binancefuture.com/fapi/v1/time" if config.TESTNET else "https://fapi.binance.com/fapi/v1/time"
            try:
                res = requests.get(url, timeout=5)
                res.raise_for_status()
                return res.json()
            except Exception as e:
                print("Monkey server time error:", e)
                return {"serverTime": int(time.time() * 1000)}
        client.get_server_time = custom_get_server_time
        break
    except Exception as _init_exc:'''

content = content.replace(old, new)
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Monkey patched client.get_server_time')
