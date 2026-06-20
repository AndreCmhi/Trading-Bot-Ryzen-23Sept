from datetime import datetime, timedelta


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _trade_dt(trade):
    for key in ("closed_time", "time"):
        value = trade.get(key)
        if not value:
            continue
        try:
            return datetime.strptime(str(value), "%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
    return None


def _closed_trades(trades):
    items = []
    for trade in trades or []:
        if str(trade.get("status", "")).upper() != "CLOSED":
            continue
        items.append(trade)
    items.sort(key=lambda item: _trade_dt(item) or datetime.min)
    return items


def _is_loss(trade):
    return _safe_float(trade.get("pnl"), 0.0) < 0


def count_consecutive_losses(trades):
    losses = 0
    for trade in reversed(_closed_trades(trades)):
        pnl = _safe_float(trade.get("pnl"), 0.0)
        if pnl < 0:
            losses += 1
            continue
        if pnl > 0:
            break
    return losses


def evaluate_pre_trade(symbol, balance=None, open_positions=None, stats=None, config=None, market_regime=None):
    cfg = config or {}
    symbol = str(symbol or "").upper()
    trades = cfg.get("trades") or []
    now = datetime.now()
    closed = _closed_trades(trades)
    daily_cutoff = now - timedelta(hours=24)
    hourly_cutoff = now - timedelta(hours=1)

    max_daily_loss_usdt = max(_safe_float(cfg.get("max_daily_loss_usdt"), 25.0), 0.01)
    hard_daily_loss_multiplier = max(_safe_float(cfg.get("hard_daily_loss_multiplier"), 2.5), 1.0)
    max_consecutive_losses = max(_safe_int(cfg.get("max_consecutive_losses"), 3), 1)
    max_trades_per_hour = max(_safe_int(cfg.get("max_trades_per_hour"), 6), 1)
    max_losses_per_hour = max(_safe_int(cfg.get("max_losses_per_hour"), 3), 1)
    hourly_loss_limit_usdt = max(_safe_float(cfg.get("hourly_loss_limit_usdt"), 10.0), 0.01)
    loss_cooldown_minutes = max(_safe_int(cfg.get("loss_cooldown_minutes"), 30), 0)
    max_symbol_trades_per_day = max(_safe_int(cfg.get("max_symbol_trades_per_day"), 4), 1)
    max_symbol_losses_per_day = max(_safe_int(cfg.get("max_symbol_losses_per_day"), 3), 1)
    max_symbol_consecutive_losses = max(_safe_int(cfg.get("max_symbol_consecutive_losses"), 2), 1)
    symbol_loss_cooldown_minutes = max(_safe_int(cfg.get("symbol_loss_cooldown_minutes"), 60), 0)
    hard_stop_symbol_cooldown_minutes = max(_safe_int(cfg.get("hard_stop_symbol_cooldown_minutes"), 180), 0)
    recent_closed_count = max(_safe_int(cfg.get("recent_closed_count"), 0), 0)
    recent_winrate = _safe_float(cfg.get("recent_winrate"), 0.0)
    recent_hard_stop_rate = _safe_float(cfg.get("recent_hard_stop_rate"), 0.0)
    recent_profit_leaks = max(_safe_int(cfg.get("recent_profit_leaks"), 0), 0)
    candidate_side = str(cfg.get("candidate_side", "") or "").upper()
    buy_scalping_pause_active = bool(cfg.get("buy_scalping_pause_active", False))

    recent_daily = [trade for trade in closed if (_trade_dt(trade) or datetime.min) >= daily_cutoff]
    recent_hourly = [trade for trade in closed if (_trade_dt(trade) or datetime.min) >= hourly_cutoff]
    symbol_daily = [trade for trade in recent_daily if str(trade.get("symbol", "")).upper() == symbol]
    symbol_closed = [trade for trade in closed if str(trade.get("symbol", "")).upper() == symbol]

    daily_loss = abs(sum(min(_safe_float(trade.get("pnl"), 0.0), 0.0) for trade in recent_daily))
    hourly_loss = abs(sum(min(_safe_float(trade.get("pnl"), 0.0), 0.0) for trade in recent_hourly))
    hourly_losses = sum(1 for trade in recent_hourly if _is_loss(trade))
    consecutive_losses = count_consecutive_losses(closed)
    symbol_losses_today = sum(1 for trade in symbol_daily if _is_loss(trade))
    symbol_consecutive_losses = count_consecutive_losses(symbol_closed)
    symbol_hard_stop = next(
        (
            trade for trade in reversed(symbol_closed)
            if str(trade.get("close_reason", "")).upper() == "HARD_STOP"
        ),
        None,
    )
    latest_symbol_loss = next((trade for trade in reversed(symbol_closed) if _is_loss(trade)), None)

    result = {
        "allowed": True,
        "reason": "Risk guard mengizinkan entry.",
        "policy": "allow",
        "halt_bot": False,
        "risk_multiplier": 1.0,
        "confidence_boost": 0.0,
        "leverage_cap": None,
    }

    if daily_loss >= (max_daily_loss_usdt * hard_daily_loss_multiplier):
        result.update({
            "allowed": False,
            "policy": "daily_loss_hard_stop",
            "halt_bot": False,
            "risk_multiplier": 0.0,
            "reason": (
                f"Daily loss {daily_loss:.2f} USDT melewati hard limit "
                f"{(max_daily_loss_usdt * hard_daily_loss_multiplier):.2f} USDT. Entry ditahan tanpa auto-pause bot."
            ),
        })
        return result

    if daily_loss >= max_daily_loss_usdt:
        result.update({
            "allowed": True,
            "policy": "daily_loss_recovery",
            "halt_bot": False,
            "risk_multiplier": 0.25,
            "confidence_boost": 0.08,
            "leverage_cap": 2,
            "reason": (
                f"Daily loss {daily_loss:.2f} USDT melewati soft limit {max_daily_loss_usdt:.2f} USDT. "
                "Bot masuk recovery: size 25%, leverage max 2x, confidence wajib lebih tinggi."
            ),
        })
        return result

    if consecutive_losses >= max_consecutive_losses:
        result.update({
            "allowed": False,
            "policy": "halt",
            "halt_bot": True,
            "risk_multiplier": 0.0,
            "reason": f"Loss beruntun {consecutive_losses}x melewati batas {max_consecutive_losses}x.",
        })
        return result

    if len(recent_hourly) >= max_trades_per_hour:
        result.update({
            "allowed": False,
            "policy": "cooldown",
            "risk_multiplier": 0.0,
            "reason": f"Trade 1 jam terakhir {len(recent_hourly)}x melewati batas {max_trades_per_hour}x.",
        })
        return result

    if hourly_losses >= max_losses_per_hour:
        result.update({
            "allowed": False,
            "policy": "cooldown",
            "risk_multiplier": 0.0,
            "reason": f"Loss 1 jam terakhir {hourly_losses}x melewati batas {max_losses_per_hour}x.",
        })
        return result

    if hourly_loss >= hourly_loss_limit_usdt:
        result.update({
            "allowed": False,
            "policy": "cooldown",
            "risk_multiplier": 0.0,
            "reason": f"Rugi 1 jam terakhir {hourly_loss:.2f} USDT melewati batas {hourly_loss_limit_usdt:.2f} USDT.",
        })
        return result

    if latest_symbol_loss is not None:
        latest_symbol_loss_dt = _trade_dt(latest_symbol_loss)
        if latest_symbol_loss_dt and symbol_loss_cooldown_minutes > 0:
            elapsed = (now - latest_symbol_loss_dt).total_seconds() / 60
            if elapsed < symbol_loss_cooldown_minutes:
                result.update({
                    "allowed": False,
                    "policy": "symbol_cooldown",
                    "risk_multiplier": 0.0,
                    "reason": f"{symbol} cooldown loss aktif {symbol_loss_cooldown_minutes} menit.",
                })
                return result

    if symbol_hard_stop is not None:
        hard_stop_dt = _trade_dt(symbol_hard_stop)
        if hard_stop_dt and hard_stop_symbol_cooldown_minutes > 0:
            elapsed = (now - hard_stop_dt).total_seconds() / 60
            if elapsed < hard_stop_symbol_cooldown_minutes:
                result.update({
                    "allowed": False,
                    "policy": "symbol_hard_stop_cooldown",
                    "risk_multiplier": 0.0,
                    "reason": f"{symbol} cooldown HARD_STOP aktif {hard_stop_symbol_cooldown_minutes} menit.",
                })
                return result

    if len(symbol_daily) >= max_symbol_trades_per_day:
        result.update({
            "allowed": False,
            "policy": "symbol_limit",
            "risk_multiplier": 0.0,
            "reason": f"Trade {symbol} hari ini {len(symbol_daily)}x melewati batas {max_symbol_trades_per_day}x.",
        })
        return result

    if symbol_losses_today >= max_symbol_losses_per_day:
        result.update({
            "allowed": False,
            "policy": "symbol_limit",
            "risk_multiplier": 0.0,
            "reason": f"Loss {symbol} hari ini {symbol_losses_today}x melewati batas {max_symbol_losses_per_day}x.",
        })
        return result

    if symbol_consecutive_losses >= max_symbol_consecutive_losses:
        result.update({
            "allowed": False,
            "policy": "symbol_limit",
            "risk_multiplier": 0.0,
            "reason": f"Loss beruntun {symbol} {symbol_consecutive_losses}x melewati batas {max_symbol_consecutive_losses}x.",
        })
        return result

    if buy_scalping_pause_active and candidate_side == "BUY":
        result.update({
            "allowed": False,
            "policy": "adaptive_pause",
            "risk_multiplier": 0.0,
            "reason": "BUY scalping dipause karena pola recent lemah dan hard stop tinggi.",
        })
        return result

    if recent_closed_count >= 6 and recent_winrate < 15:
        if _safe_int(open_positions, 0) >= 2 and candidate_side == "BUY":
            result.update({
                "allowed": False,
                "policy": "recovery_block",
                "risk_multiplier": 0.0,
                "reason": "Recovery mode aktif: winrate recent terlalu rendah, tahan BUY baru saat posisi aktif masih ada.",
            })
            return result
        result.update({
            "policy": "recovery",
            "risk_multiplier": 0.35,
            "confidence_boost": -0.08,
            "leverage_cap": 3,
            "reason": "Recovery mode aktif karena winrate recent rendah.",
        })
        return result

    if recent_closed_count >= 4 and recent_hard_stop_rate >= 0.6:
        result.update({
            "policy": "hard_stop_recovery",
            "risk_multiplier": 0.4,
            "confidence_boost": -0.06,
            "leverage_cap": 4,
            "reason": "Recovery hard-stop aktif karena rasio HARD_STOP recent tinggi.",
        })
        return result

    if recent_profit_leaks >= 5:
        result.update({
            "policy": "disabled_profit_lock",
            "risk_multiplier": 0.6,
            "confidence_boost": -0.03,
            "leverage_cap": 5,
            "reason": "Mode kunci profit aktif karena ada winner yang bocor kembali.",
        })
        return result

    if hourly_losses > 0 or symbol_losses_today > 0:
        result.update({
            "policy": "cautious",
            "risk_multiplier": 0.5,
            "confidence_boost": -0.05,
            "leverage_cap": 5,
            "reason": "Risk guard mode hati-hati karena ada loss terbaru.",
        })
        return result

    if open_positions is not None and _safe_int(open_positions, 0) >= 2:
        result.update({
            "policy": "throttle",
            "risk_multiplier": 0.75,
            "confidence_boost": -0.03,
            "leverage_cap": 5,
            "reason": "Open position sudah padat, size diperkecil.",
        })
        return result

    if market_regime and str(market_regime).upper() == "SLUGGISH":
        result.update({
            "policy": "sluggish_market",
            "risk_multiplier": 0.5,
            "confidence_boost": -0.05,
            "leverage_cap": 3,
            "reason": "Market SLUGGISH: ukuran posisi dikurangi 50%.",
        })
        return result

    return result
