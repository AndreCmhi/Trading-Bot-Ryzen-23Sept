import json
import time
from datetime import datetime
from constants import SETTINGS_FILE, DATA_FILE, TESTNET_SHADOW_POSITIONS_FILE, MANUAL_ROI_FILE, MANUAL_TP_SL_FILE, AI_DECISIONS_FILE
import state

def write_json_atomic(path_obj, data):
    import os
    temp_path = str(path_obj) + ".tmp"
    with open(temp_path, "w") as f:
        json.dump(data, f, indent=4)
    os.replace(temp_path, str(path_obj))

def load_trades():
    try:
        if DATA_FILE.exists():
            with open(DATA_FILE, "r") as f:
                return json.load(f)
    except:
        pass
    return []

def save_trades(trades):
    with state.trades_lock:
        write_json_atomic(DATA_FILE, trades)

def load_runtime_settings():
    try:
        if SETTINGS_FILE.exists():
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
    except:
        pass
    return {}

def save_runtime_settings(data):
    with state.settings_lock:
        write_json_atomic(SETTINGS_FILE, data)

def get_runtime_settings():
    with state.settings_lock:
        return dict(state.runtime_settings)

def update_runtime_settings(new_values):
    with state.settings_lock:
        state.runtime_settings.update(new_values)
        save_runtime_settings(state.runtime_settings)
    return state.runtime_settings

def load_manual_roi():
    try:
        if MANUAL_ROI_FILE.exists():
            with open(MANUAL_ROI_FILE, "r") as f:
                return json.load(f)
    except:
        pass
    return {}

def save_manual_roi(data):
    with state.manual_roi_lock:
        write_json_atomic(MANUAL_ROI_FILE, data)

def load_manual_tp_sl():
    try:
        if MANUAL_TP_SL_FILE.exists():
            with open(MANUAL_TP_SL_FILE, "r") as f:
                return json.load(f)
    except:
        pass
    return {}

def save_manual_tp_sl(data):
    with state.manual_tp_sl_lock:
        write_json_atomic(MANUAL_TP_SL_FILE, data)

def load_ai_decisions():
    try:
        if AI_DECISIONS_FILE.exists():
            with open(AI_DECISIONS_FILE, "r") as f:
                return json.load(f)
    except:
        pass
    return []

def save_ai_decisions(decisions):
    write_json_atomic(AI_DECISIONS_FILE, decisions)

def add_ai_decision(decision):
    decisions = load_ai_decisions()
    decisions.append(decision)
    save_ai_decisions(decisions[-100:])

def get_bot_running():
    with state.status_lock:
        return state.bot_running

def set_bot_running(value, reason="", source="manual"):
    global bot_running, bot_stop_reason, bot_stop_source
    with state.status_lock:
        state.bot_running = value
        state.bot_stop_reason = reason
        state.bot_stop_source = source
    return value

def round_step_size(value, step):
    precision = int(round(-math.log10(float(step))))
    return round(float(value), precision)

def ceil_step_size(value, step):
    import math
    precision = int(round(-math.log10(float(step))))
    factor = 10**precision
    return math.ceil(float(value) * factor) / factor

def round_tick_size(price, tick):
    precision = int(round(-math.log10(float(tick))))
    return round(float(price), precision)

import math
def get_open_trade_record(symbol, adopt_if_missing=False, position=None):
    trades = load_trades()
    for trade in reversed(trades):
        if trade.get('symbol') == symbol and trade.get('status') == 'OPEN':
            return trade
    return None

def update_open_trade_record(symbol, updates):
    trades = load_trades()
    for trade in reversed(trades):
        if trade.get('symbol') == symbol and trade.get('status') == 'OPEN':
            trade.update(updates)
            save_trades(trades)
            return trade
    return None
import hmac
import secrets
from flask import session, request
from constants import APP_USERNAME, APP_PASSWORD

def credentials_valid(username, password):
    return hmac.compare_digest(username, APP_USERNAME) and hmac.compare_digest(password, APP_PASSWORD)

def ensure_csrf_token():
    token = session.get('csrf_token')
    if not token:
        token = secrets.token_urlsafe(32)
        session['csrf_token'] = token
    return token

def validate_csrf_request():
    session_token = session.get('csrf_token')
    request_token = request.headers.get('X-CSRF-Token') or request.form.get('csrf_token')
    return bool(session_token and request_token and hmac.compare_digest(str(session_token), str(request_token)))
