import sys
import re, requests, base64, json, time, os
from pathlib import Path

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"
env = {}
if ENV_FILE.exists():
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line: continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")

base = "http://127.0.0.1:5000"
sess = requests.Session()
sess.timeout = 30

def get_csrf():
    cv = sess.cookies.get("session", "")
    if not cv: return ""
    try:
        p = cv.split(".")[0]; pad = p + "=" * (-len(p) % 4)
        return json.loads(base64.urlsafe_b64decode(pad)).get("csrf_token", "")
    except: return ""

def login():
    try:
        sess.get(base + "/login", timeout=10)
        sess.post(base + "/login", data={"username": env.get("APP_USERNAME","admin"), "password": env.get("APP_PASSWORD","")},
            headers={"X-CSRF-Token": get_csrf()}, allow_redirects=False, timeout=10)
    except: pass

def api_post(path, body):
    return sess.post(base + path, json=body, timeout=20,
        headers={"X-CSRF-Token": get_csrf(), "Content-Type": "application/json", "Accept": "application/json"})

print(">>> WIN CLOSE + AUTO REFILL MONITOR STARTED", flush=True)
login()

targets = [
    ("BTCUSDT", "BUY"), ("COMPUSDT", "BUY"), ("ETHUSDT", "SELL"), 
    ("LINKUSDT", "SELL"), ("CRVUSDT", "SELL"), ("BNBUSDT", "SELL"), 
    ("SOLUSDT", "BUY"), ("LUNA2USDT", "SELL"), ("XLMUSDT", "SELL"), 
    ("XRPUSDT", "SELL"), ("APTUSDT", "SELL"), ("GMXUSDT", "SELL"), 
    ("UNIUSDT", "SELL"), ("DOGEUSDT", "SELL")
]

while True:
    try:
        r = sess.get(base + "/api/positions", timeout=10)
        if r.status_code == 401:
            login()
            r = sess.get(base + "/api/positions", timeout=10)
        
        positions = r.json() if r.ok else []
        active_symbols = set()
        
        for p in positions:
            symbol = p.get("symbol")
            active_symbols.add(symbol)
            pnl = float(p.get("pnl", 0) or 0)
            roi = float(p.get("roi", 0) or 0)
            
            if pnl > 0 and roi >= 0.1:
                res = api_post("/api/close_position", {"symbol": symbol}).json()
                print(f"[{time.strftime('%H:%M:%S')}] WIN CLOSE {symbol}: PNL={pnl:.2f} USDT -> {res.get('message','')}", flush=True)
                active_symbols.discard(symbol)
        
        if len(active_symbols) < 10:
            shortage = 10 - len(active_symbols)
            for sym, side in targets:
                if shortage <= 0: break
                if sym not in active_symbols:
                    print(f"[{time.strftime('%H:%M:%S')}] REFILL OPEN {sym} {side}...", flush=True)
                    res = api_post("/api/open_position", {"symbol": sym, "side": side, "leverage": 3}).json()
                    if res.get("status") == "ok":
                        active_symbols.add(sym)
                        shortage -= 1
                        time.sleep(1)
                    
    except Exception as exc:
        print("Monitor error:", exc, flush=True)
    
    time.sleep(8)
