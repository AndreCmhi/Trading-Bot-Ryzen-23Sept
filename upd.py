path = r"C:\Users\Maria Oktavia\Documents\Bot Trading\app.py"
content = open(path, encoding="utf-8").read()

# 1. Add TRAILING constants after AUTO_CLOSE_ROI_PERCENT
if "TRAILING_TRIGGER_ROI_PERCENT = float" not in content:
    auto_close = 'AUTO_CLOSE_ROI_PERCENT = float(os.getenv("AUTO_CLOSE_ROI_PERCENT", "4.0"))'
    trailing = '''AUTO_CLOSE_ROI_PERCENT = float(os.getenv("AUTO_CLOSE_ROI_PERCENT", "4.0"))
TRAILING_TRIGGER_ROI_PERCENT = float(os.getenv("TRAILING_TRIGGER_ROI_PERCENT", "3.0"))
TRAILING_CALLBACK_ROI_PERCENT = float(os.getenv("TRAILING_CALLBACK_ROI_PERCENT", "1.0"))
FAST_TRAILING_TRIGGER_ROI_PERCENT = float(os.getenv("FAST_TRAILING_TRIGGER_ROI_PERCENT", "0.10"))
FAST_TRAILING_CALLBACK_ROI_PERCENT = float(os.getenv("FAST_TRAILING_CALLBACK_ROI_PERCENT", "0.08"))'''
    content = content.replace(auto_close, trailing)
    print("1. Added TRAILING constants")

# 2. Add to get_default_settings
if '"trailing_enabled": True' not in content:
    old = '"hard_stop_symbol_cooldown_minutes": HARD_STOP_SYMBOL_COOLDOWN_MINUTES,'
    new = '''"hard_stop_symbol_cooldown_minutes": HARD_STOP_SYMBOL_COOLDOWN_MINUTES,
        "trailing_enabled": True,
        "trailing_trigger_roi_percent": TRAILING_TRIGGER_ROI_PERCENT,
        "trailing_callback_roi_percent": TRAILING_CALLBACK_ROI_PERCENT,
        "fast_trailing_enabled": False,
        "fast_trailing_trigger_roi_percent": FAST_TRAILING_TRIGGER_ROI_PERCENT,
        "fast_trailing_callback_roi_percent": FAST_TRAILING_CALLBACK_ROI_PERCENT,'''
    content = content.replace(old, new)
    print("2. Added to get_default_settings")

# 3. Add trailing vars extraction in update_settings_api
if 'trailing_enabled = bool' not in content:
    old = 'hard_stop_symbol_cooldown_minutes = int(payload.get("hard_stop_symbol_cooldown_minutes",'
    new = '''hard_stop_symbol_cooldown_minutes = int(payload.get("hard_stop_symbol_cooldown_minutes",
                current_settings.get("hard_stop_symbol_cooldown_minutes", HARD_STOP_SYMBOL_COOLDOWN_MINUTES),
            ))
        trailing_enabled = bool(payload.get("trailing_enabled", current_settings.get("trailing_enabled", True)))
        trailing_trigger_roi_percent = float(payload.get("trailing_trigger_roi_percent", current_settings.get("trailing_trigger_roi_percent", TRAILING_TRIGGER_ROI_PERCENT)))
        trailing_callback_roi_percent = float(payload.get("trailing_callback_roi_percent", current_settings.get("trailing_callback_roi_percent", TRAILING_CALLBACK_ROI_PERCENT)))
        fast_trailing_enabled = bool(payload.get("fast_trailing_enabled", current_settings.get("fast_trailing_enabled", False)))
        fast_trailing_trigger_roi_percent = float(payload.get("fast_trailing_trigger_roi_percent", current_settings.get("fast_trailing_trigger_roi_percent", FAST_TRAILING_TRIGGER_ROI_PERCENT)))
        fast_trailing_callback_roi_percent = float(payload.get("fast_trailing_callback_roi_percent", current_settings.get("fast_trailing_callback_roi_percent", FAST_TRAILING_CALLBACK_ROI_PERCENT)))'''
    content = content.replace(old, new)
    print("3. Added trailing vars to update_settings_api")

# 4. Add trailing to settings dict
if '"trailing_enabled": trailing_enabled' not in content:
    old = '"hard_stop_symbol_cooldown_minutes": hard_stop_symbol_cooldown_minutes,'
    new = '''"hard_stop_symbol_cooldown_minutes": hard_stop_symbol_cooldown_minutes,
            "trailing_enabled": trailing_enabled,
            "trailing_trigger_roi_percent": round(trailing_trigger_roi_percent, 2),
            "trailing_callback_roi_percent": round(trailing_callback_roi_percent, 2),
            "fast_trailing_enabled": fast_trailing_enabled,
            "fast_trailing_trigger_roi_percent": round(fast_trailing_trigger_roi_percent, 2),
            "fast_trailing_callback_roi_percent": round(fast_trailing_callback_roi_percent, 2),'''
    content = content.replace(old, new)
    print("4. Added trailing to settings dict")

# 5. Add trailing_enabled check in auto_close
if 'if trailing_enabled and (trailing_armed' not in content:
    content = content.replace(
        'if (trailing_armed or pct >= trailing_trigger) and pct <= (peak_roi - trailing_floor):',
        'if trailing_enabled and (trailing_armed or pct >= trailing_trigger) and pct <= (peak_roi - trailing_floor):'
    )
    print("5. Added trailing_enabled check")

# 6. Add trailing settings loading in auto_close
if 'trailing_enabled = bool(settings.get' not in content:
    old_block = '''auto_close_enabled = bool(settings.get("auto_close_enabled", True))
            if not auto_close_enabled:
                time.sleep(5)
                continue'''
    new_block = '''auto_close_enabled = bool(settings.get("auto_close_enabled", True))
            if not auto_close_enabled:
                time.sleep(5)
                continue
            trailing_enabled = bool(settings.get("trailing_enabled", True))
            fast_trailing_enabled = bool(settings.get("fast_trailing_enabled", False))
            if fast_trailing_enabled:
                trailing_trigger_roi = float(settings.get("fast_trailing_trigger_roi_percent", FAST_TRAILING_TRIGGER_ROI_PERCENT))
                trailing_callback_roi = float(settings.get("fast_trailing_callback_roi_percent", FAST_TRAILING_CALLBACK_ROI_PERCENT))
            else:
                trailing_trigger_roi = float(settings.get("trailing_trigger_roi_percent", TRAILING_TRIGGER_ROI_PERCENT))
                trailing_callback_roi = float(settings.get("trailing_callback_roi_percent", TRAILING_CALLBACK_ROI_PERCENT))'''
    content = content.replace(old_block, new_block)
    print("6. Added trailing settings loading")

# 7. Add get_margin_balance
if 'def get_margin_balance():' not in content:
    old = '''def get_balance():
    try:
        balances = client.futures_account_balance()
        for balance in balances:
            if balance["asset"] == "USDT":
                return float(balance["balance"])
        return 0
    except Exception:
        return 0'''
    new = '''def get_margin_balance():
    try:
        balances = client.futures_account_balance()
        for balance in balances:
            if balance["asset"] == "USDT":
                return float(balance["balance"])
        return 0
    except Exception:
        return 0

''' + old
    content = content.replace(old, new)
    print("7. Added get_margin_balance")

# 8. Add margin_balance to stats
if '"margin_balance":' not in content:
    content = content.replace(
        '"total_open_margin": round(total_open_margin, 2),',
        '"total_open_margin": round(total_open_margin, 2),\n        "margin_balance": round(get_margin_balance(), 2),'
    )
    print("8. Added margin_balance to stats")

open(path, "w", encoding="utf-8").write(content)
print("Done!")
