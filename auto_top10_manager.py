import os
import sys
import time
import json
import base64
from pathlib import Path

import requests


BASE_DIR = Path(__file__).resolve().parent
os.chdir(BASE_DIR)
os.environ.setdefault("APP_SKIP_BOOTSTRAP", "true")

import app  # noqa: E402


TARGET_OPEN_POSITIONS = min(int(os.getenv("AUTO_TOP10_TARGET_OPEN_POSITIONS", "5")), 5)
TOP_SYMBOL_LIMIT = int(os.getenv("TOP_SYMBOL_LIMIT", "10"))
TAKE_PROFIT_ROI_PERCENT = float(os.getenv("AUTO_TOP10_TAKE_PROFIT_ROI_PERCENT", "0.5"))
STOP_LOSS_ROI_PERCENT = float(os.getenv("AUTO_TOP10_STOP_LOSS_ROI_PERCENT", "-0.3"))
LOOP_SECONDS = int(os.getenv("AUTO_TOP10_LOOP_SECONDS", "8"))
OPEN_DELAY_SECONDS = float(os.getenv("AUTO_TOP10_OPEN_DELAY_SECONDS", "1.0"))
BASE_URL = os.getenv("AUTO_TOP10_BASE_URL", "http://127.0.0.1:5000").rstrip("/")
SESSION = requests.Session()


def log(message):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}", flush=True)


def bootstrap():
    while True:
        try:
            app.load_exchange_filters()
            app.refresh_market_regime(force=True)
            app.refresh_scan_symbols(force=True)
            log(f"AUTO TOP10 READY: {len(app.get_scan_symbols())} symbols ranked")
            return
        except Exception as exc:
            log(f"BOOTSTRAP ERROR: {exc}")
            time.sleep(15)


def get_csrf():
    cookie_value = SESSION.cookies.get("session", "")
    if not cookie_value:
        return ""
    try:
        payload = cookie_value.split(".")[0]
        payload += "=" * (-len(payload) % 4)
        return json.loads(base64.urlsafe_b64decode(payload)).get("csrf_token", "")
    except Exception:
        return ""


def login_dashboard():
    try:
        SESSION.get(BASE_URL + "/login", timeout=10)
        SESSION.post(
            BASE_URL + "/login",
            data={"username": app.APP_USERNAME, "password": app.APP_PASSWORD},
            headers={"X-CSRF-Token": get_csrf()},
            allow_redirects=False,
            timeout=10,
        )
    except Exception as exc:
        log(f"LOGIN ERROR: {exc}")


def pick_side(symbol):
    if getattr(app, "MARKET_TYPE", "FUTURES") == "SPOT":
        return "BUY"
    majority_side = app.get_recent_trade_majority_side(symbol)
    if majority_side in {"BUY", "SELL"}:
        return majority_side
    try:
        setup = app.evaluate_strategy_setup(symbol)
        side = str(setup.get("side") or setup.get("action") or "").upper()
        if side in {"BUY", "SELL"}:
            return side
    except Exception:
        pass
    try:
        closes = app.get_klines(symbol, interval="5m", limit=12)
        return "BUY" if closes and closes[-1] >= closes[0] else "SELL"
    except Exception:
        return "BUY"


def api_open_position(symbol):
    payload = {
        "symbol": symbol,
        "side": pick_side(symbol),
        "leverage": int(app.get_runtime_settings().get("default_leverage", app.DEFAULT_LEVERAGE)),
    }
    response = SESSION.post(
        BASE_URL + "/api/open_position",
        json=payload,
        headers={"X-CSRF-Token": get_csrf(), "Content-Type": "application/json"},
        timeout=30,
    )
    if response.status_code == 401:
        login_dashboard()
        response = SESSION.post(
            BASE_URL + "/api/open_position",
            json=payload,
            headers={"X-CSRF-Token": get_csrf(), "Content-Type": "application/json"},
            timeout=30,
        )
    try:
        data = response.json()
    except Exception:
        data = {"message": response.text[:200]}
    return response.ok and data.get("status") == "ok", payload, data.get("message", "")


def close_positions_by_roi(positions):
    closed_symbols = set()
    for position in positions:
        symbol = str(position.get("symbol") or "").upper()
        if not symbol:
            continue

        try:
            roi = float(position.get("roi", 0) or 0)
            pnl = float(position.get("pnl", 0) or 0)
        except (TypeError, ValueError):
            continue

        if roi > TAKE_PROFIT_ROI_PERCENT:
            success, message = app.close_position(symbol, reason="AUTO_TOP10_TAKE_PROFIT")
            log(f"TAKE PROFIT {symbol}: ROI={roi:.2f}% PNL={pnl:.2f} -> {message}")
            if success:
                closed_symbols.add(symbol)
        elif roi <= STOP_LOSS_ROI_PERCENT:
            success, message = app.close_position(symbol, reason="AUTO_TOP10_STOP_LOSS")
            log(f"STOP LOSS {symbol}: ROI={roi:.2f}% PNL={pnl:.2f} -> {message}")
            if success:
                closed_symbols.add(symbol)

    return closed_symbols


def refill_positions(active_symbols):
    shortage = max(0, TARGET_OPEN_POSITIONS - len(active_symbols))
    if shortage <= 0:
        return

    app.refresh_scan_symbols(force=True)
    ranked_symbols = app.get_scan_symbols()
    candidates = app.build_ranked_trade_candidates(ranked_symbols[:TOP_SYMBOL_LIMIT])
    candidates = candidates[:shortage]
    if not candidates:
        log("REFILL SKIP: no AI-approved candidates")
        return
    log(f"REFILL NEEDED: active={len(active_symbols)} target={TARGET_OPEN_POSITIONS} candidates={len(candidates)}")

    for symbol in candidates:
        if shortage <= 0:
            break
        symbol = str(symbol or "").upper()
        if not symbol or symbol in active_symbols:
            continue

        try:
            before_count = app.get_open_position_count(trackable_only=True)
            app.execute_trade(symbol)
            after_positions = app.get_current_positions()
            after_symbols = {str(pos.get("symbol") or "").upper() for pos in after_positions}
            if symbol in after_symbols or app.get_open_position_count(trackable_only=True) > before_count:
                active_symbols.add(symbol)
                shortage -= 1
                log(f"OPENED {symbol}: active={len(active_symbols)}/{TARGET_OPEN_POSITIONS}")
                time.sleep(OPEN_DELAY_SECONDS)
                continue

            ok, payload, message = api_open_position(symbol)
            after_positions = app.get_current_positions()
            after_symbols = {str(pos.get("symbol") or "").upper() for pos in after_positions}
            if ok or symbol in after_symbols:
                active_symbols.add(symbol)
                shortage -= 1
                log(f"OPENED MANUAL {symbol} {payload['side']}: active={len(active_symbols)}/{TARGET_OPEN_POSITIONS}")
                time.sleep(OPEN_DELAY_SECONDS)
            else:
                log(f"OPEN SKIP {symbol} {payload['side']}: {message}")
        except Exception as exc:
            log(f"OPEN ERROR {symbol}: {exc}")


def run():
    bootstrap()
    login_dashboard()
    while True:
        try:
            positions = app.get_current_positions()
            active_symbols = {str(pos.get("symbol") or "").upper() for pos in positions if pos.get("symbol")}
            closed_symbols = close_positions_by_roi(positions)
            active_symbols.difference_update(closed_symbols)
            refill_positions(active_symbols)
        except KeyboardInterrupt:
            log("STOPPED BY USER")
            raise
        except Exception as exc:
            log(f"LOOP ERROR: {exc}")
        time.sleep(LOOP_SECONDS)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(line_buffering=True)
    run()
