import re, requests, base64, json, time, os, sys
from pathlib import Path

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

def get_csrf():
    cv = sess.cookies.get("session", "")
    if not cv: return ""
    try:
        p = cv.split(".")[0]; pad = p + "=" * (-len(p) % 4)
        return json.loads(base64.urlsafe_b64decode(pad)).get("csrf_token", "")
    except: return ""

def login():
    sess.get(base + "/login")
    sess.post(base + "/login", data={"username": env.get("APP_USERNAME","admin"), "password": env.get("APP_PASSWORD","")},
        headers={"X-CSRF-Token": get_csrf()}, allow_redirects=False)

def close_pos(symbol):
    csrf = get_csrf()
    r = sess.post(base + "/api/close_position", json={"symbol": symbol},
        headers={"X-CSRF-Token": csrf, "Content-Type": "application/json", "Accept": "application/json"})
    return r.json()

print(">>> WIN CLOSE MONITOR STARTED")
login()

while True:
    try:
        r = sess.get(base + "/api/positions")
        if r.status_code == 401:
            login()
            r = sess.get(base + "/api/positions")
        
        positions = r.json() if r.ok else []
        for p in positions:
            symbol = p.get("symbol")
            pnl = float(p.get("pnl", 0) or 0)
            roi = float(p.get("roi", 0) or 0)
            # Hanya close kalau WIN (PNL > 0 dan ROI >= 0.1%)
            if pnl > 0 and roi >= 0.1:
                res = close_pos(symbol)
                print(f"[{time.strftime('%H:%M:%S')}] WIN CLOSE {symbol}: PNL={pnl:.2f} USDT ROI={roi:.2f}% -> {res.get('message','')}")
    except Exception as exc:
        print("Monitor error:", exc)
    
    time.sleep(5)
