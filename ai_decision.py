import json
import os
import re
from typing import Any, Dict, List

import requests
import config

OLLAMA_ENABLED = os.getenv("OLLAMA_ENABLED", "false").strip().lower() == "true"
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/generate").strip()
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b").strip()
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "10"))
AI_PROVIDER = os.getenv("AI_PROVIDER", "heuristic").strip().lower()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant").strip()
GROQ_URL = os.getenv("GROQ_URL", "https://api.groq.com/openai/v1/chat/completions").strip()
GROQ_TIMEOUT = int(os.getenv("GROQ_TIMEOUT", "15"))


def get_ai_provider_status() -> Dict[str, Any]:
    provider = AI_PROVIDER or "heuristic"
    ollama_ready = bool(OLLAMA_URL and OLLAMA_MODEL)
    groq_ready = bool(GROQ_API_KEY and GROQ_MODEL)
    fallback_chain = ["heuristic"]
    if provider == "groq":
        fallback_chain = ["groq", "ollama", "heuristic"] if ollama_ready else ["groq", "heuristic"]
    elif provider == "ollama" or OLLAMA_ENABLED:
        fallback_chain = ["ollama", "heuristic"]
    return {
        "provider": provider,
        "groq_model": GROQ_MODEL if provider == "groq" else None,
        "groq_configured": groq_ready,
        "ollama_model": OLLAMA_MODEL if (provider == "ollama" or OLLAMA_ENABLED) else None,
        "ollama_configured": ollama_ready,
        "fallback_chain": fallback_chain,
    }


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_list(values: Any, limit: int = 120) -> List[float]:
    if not isinstance(values, list):
        return []
    cleaned = []
    for item in values[-limit:]:
        try:
            cleaned.append(float(item))
        except (TypeError, ValueError):
            continue
    return cleaned


def calculate_ema(prices, period=9):
    series = _safe_list(prices)
    if not series:
        return 0.0
    period = max(int(period or 1), 1)
    multiplier = 2 / (period + 1)
    ema = series[0]
    for price in series[1:]:
        ema = (price - ema) * multiplier + ema
    return round(ema, 8)


def calculate_atr_percent(prices, period=14):
    series = _safe_list(prices)
    if len(series) < 2:
        return 0.0
    period = max(int(period or 1), 1)
    moves = []
    for index in range(1, len(series)):
        prev_price = series[index - 1]
        current_price = series[index]
        if prev_price <= 0:
            continue
        moves.append(abs(current_price - prev_price) / prev_price * 100)
    if not moves:
        return 0.0
    window = moves[-period:]
    return round(sum(window) / len(window), 4)


def calculate_risk_amount(equity_usdt, risk_percent):
    equity = max(_safe_float(equity_usdt), 0.0)
    risk_pct = max(_safe_float(risk_percent), 0.0)
    return equity * (risk_pct / 100.0)


def calculate_position_size(equity_usdt, risk_percent, sl_percent):
    equity = max(_safe_float(equity_usdt), 0.0)
    risk_pct = max(_safe_float(risk_percent), 0.0)
    stop_pct = max(_safe_float(sl_percent), 0.0)
    if equity <= 0 or risk_pct <= 0 or stop_pct <= 0:
        return 0.0
    risk_amount = calculate_risk_amount(equity, risk_pct)
    return risk_amount / (stop_pct / 100.0)


def calculate_risk_reward_ratio(tp_percent, sl_percent):
    take_profit = max(_safe_float(tp_percent), 0.0)
    stop_loss = max(_safe_float(sl_percent), 0.0)
    if stop_loss <= 0:
        return 0.0
    return round(take_profit / stop_loss, 4)


def build_market_snapshot(symbol, closes=None, score=0, rsi=50, extras=None):
    series = _safe_list(closes)
    last_price = series[-1] if series else 0.0
    ema_fast = calculate_ema(series, 9)
    ema_slow = calculate_ema(series, 21)
    atr_percent = calculate_atr_percent(series, 14)

    # Tambahan data Slope untuk AI
    slope_5m = extras.get("slope_5m", 0.0) if extras else 0.0
    slope_15m = extras.get("slope_15m", 0.0) if extras else 0.0
   
    snapshot = {
        "symbol": str(symbol or "").upper(),
        "score": round(_safe_float(score), 4),
        "rsi": round(_safe_float(rsi, 50.0), 4),
        "last_price": round(last_price, 8),
        "ema_slope_5m": round(slope_5m, 4),
        "ema_slope_15m": round(slope_15m, 4),
        "atr_percent": atr_percent,
        "trend": "bullish" if ema_fast > ema_slow else "bearish",
        "market_regime": extras.get("market_regime", "UNKNOWN") if extras else "UNKNOWN"
    }
    if isinstance(extras, dict):
        snapshot.update(extras)
    return snapshot


def _extract_json_block(text: str) -> Dict[str, Any]:
    if not text:
        return {}
    text = text.strip()
    try:
        data = json.loads(text)
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return {}
    try:
        data = json.loads(match.group(0))
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}

def _block_trade(reason: str) -> Dict[str, Any]:
    return {
        "allow_trade": False,
        "action": "HOLD",
        "quality_gate_reason": reason,
    }

def _quality_gate(snapshot: Dict[str, Any], decision: Dict[str, Any]) -> Dict[str, Any]:
    action = str(decision.get("action", "HOLD") or "HOLD").upper()
    if action not in {"BUY", "SELL"}:
        return {}

    score = _safe_float(snapshot.get("score"), 0.0)
    min_score = _safe_float(snapshot.get("min_score"), 8.0)
    confidence = _safe_float(decision.get("confidence"), 0.0)
    min_confidence = _safe_float(snapshot.get("ai_min_confidence"), 0.75)
    rr_ratio = _safe_float(decision.get("risk_reward_ratio"), 0.0)
    min_rr = max(_safe_float(snapshot.get("min_risk_reward_ratio"), 2.0), 1.5)
    adx_val = _safe_float(snapshot.get("adx"), 0.0)
    min_adx = _safe_float(snapshot.get("min_adx"), 18.0)
    vol_ratio = _safe_float(snapshot.get("vol_ratio", snapshot.get("volume_ratio")), 0.0)
    min_volume_ratio = _safe_float(snapshot.get("min_volume_ratio"), 0.9)
    rsi = _safe_float(snapshot.get("rsi"), 50.0)
    candidate_side = str(snapshot.get("candidate_side", action) or action).upper()
    trend_5m = str(snapshot.get("trend_5m", "sideways") or "sideways").lower()
    trend_15m = str(snapshot.get("trend_15m", "sideways") or "sideways").lower()
    trend_1h = str(snapshot.get("trend_1h", "sideways") or "sideways").lower()
    expected_trend = "bullish" if action == "BUY" else "bearish"
    aligned_tfs = sum(1 for value in (trend_5m, trend_15m, trend_1h) if value == expected_trend)

    if candidate_side in {"BUY", "SELL"} and action != candidate_side:
        return _block_trade(f"quality-gate: AI side {action} beda dengan setup {candidate_side}")
    if score < min_score:
        return _block_trade(f"quality-gate: score {score:.1f} di bawah minimum {min_score:.1f}")
    if confidence < min_confidence:
        return _block_trade(f"quality-gate: confidence {confidence:.2f} di bawah minimum {min_confidence:.2f}")
    if rr_ratio < min_rr:
        return _block_trade(f"quality-gate: RR {rr_ratio:.2f} di bawah minimum {min_rr:.2f}")
    if adx_val < min_adx:
        return _block_trade(f"quality-gate: ADX {adx_val:.2f} di bawah minimum {min_adx:.2f}")
    if vol_ratio < min_volume_ratio:
        return _block_trade(f"quality-gate: volume ratio x{vol_ratio:.2f} di bawah minimum x{min_volume_ratio:.2f}")
    if aligned_tfs < 2:
        return _block_trade(f"quality-gate: trend alignment kurang ({aligned_tfs}/3 timeframe)")
    if action == "BUY" and not 42 <= rsi <= 66:
        return _block_trade(f"quality-gate: RSI BUY {rsi:.1f} di luar zona sehat 42-66")
    if action == "SELL" and not 34 <= rsi <= 58:
        return _block_trade(f"quality-gate: RSI SELL {rsi:.1f} di luar zona sehat 34-58")

    return {}


def _heuristic_decision(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    score = _safe_float(snapshot.get("score"), 0.0)
    rsi = _safe_float(snapshot.get("rsi"), 50.0)
    trend = str(snapshot.get("trend", "sideways")).lower()
    candidate_side = str(snapshot.get("candidate_side", "HOLD")).upper()
    atr_percent = max(_safe_float(snapshot.get("atr_percent"), 0.35), 0.1)
    min_rr = max(_safe_float(snapshot.get("min_risk_reward_ratio"), 2.0), 1.2)

    # Advanced context
    adx_val = _safe_float(snapshot.get("adx"), 0)
    macd_hist = _safe_float(snapshot.get("macd_histogram"), 0)
    stoch_k = _safe_float(snapshot.get("stoch_k"), 50)
    stoch_d = _safe_float(snapshot.get("stoch_d"), 50)
    vol_ratio = _safe_float(snapshot.get("vol_ratio"), 1.0)
    bb_position = str(snapshot.get("bb_position", "inside")).lower()
    trend_5m = str(snapshot.get("trend_5m", "sideways")).lower()
    trend_15m = str(snapshot.get("trend_15m", "sideways")).lower()
    trend_1h = str(snapshot.get("trend_1h", "sideways")).lower()
    funding_rate = _safe_float(snapshot.get("funding_rate"), 0)

    action = "HOLD"
    allow_trade = False
    confidence = 0.45
    suggested_leverage = 3
    risk_mode = "normal"

    if candidate_side in {"BUY", "SELL"}:
        action = candidate_side

    # Count trend alignment across timeframes
    tf_bullish = sum(1 for t in [trend_5m, trend_15m, trend_1h] if t == "bullish")
    tf_bearish = sum(1 for t in [trend_5m, trend_15m, trend_1h] if t == "bearish")

    # Multi-factor confidence calculation
    confidence_base = 0.45
    score_factor = min(score / 10.0, 1.0) * 0.25

    # Trend alignment bonus
    if action == "BUY":
        trend_bonus = tf_bullish * 0.05
        trend_penalty = tf_bearish * 0.04
    else:
        trend_bonus = tf_bearish * 0.05
        trend_penalty = tf_bullish * 0.04

    # ADX trend strength
    adx_bonus = 0
    if adx_val >= 25:
        adx_bonus = 0.08  # Strong trend
    elif adx_val >= 20:
        adx_bonus = 0.03  # Moderate
    elif adx_val < 15:
        adx_bonus = -0.05  # Weak trend, avoid

    # MACD confirmation
    if (action == "BUY" and macd_hist > 0) or (action == "SELL" and macd_hist < 0):
        adx_bonus += 0.05
    else:
        adx_bonus -= 0.03

    # RSI zone
    rsi_bonus = 0
    if action == "BUY":
        if 40 <= rsi <= 65:
            rsi_bonus = 0.06
        elif 30 <= rsi < 40 and stoch_k < 20:
            rsi_bonus = 0.08  # Oversold bounce
        elif rsi > 70:
            rsi_bonus = -0.06  # Overbought, risky
    else:
        if 35 <= rsi <= 60:
            rsi_bonus = 0.06
        elif 60 < rsi <= 70 and stoch_k > 80:
            rsi_bonus = 0.08  # Overbought
        elif rsi < 30:
            rsi_bonus = -0.06  # Oversold, risky for SELL

    # Bollinger bounce
    bb_bonus = 0
    if action == "BUY" and bb_position == "below_lower" and stoch_k < 25:
        bb_bonus = 0.06
    elif action == "SELL" and bb_position == "above_upper" and stoch_k > 75:
        bb_bonus = 0.06

    # Volume confirmation
    vol_bonus = 0.03 if vol_ratio > 1.5 else 0

    # Funding rate filter
    funding_bonus = 0
    if funding_rate != 0:
        if action == "BUY" and funding_rate > 0.0005:
            funding_bonus = -0.04
        elif action == "SELL" and funding_rate < -0.0005:
            funding_bonus = -0.04

    # Combine all factors
    raw_confidence = (
        confidence_base +
        score_factor +
        trend_bonus +
        adx_bonus +
        rsi_bonus +
        bb_bonus +
        vol_bonus +
        funding_bonus -
        trend_penalty
    )

    # Normalize to 0.05-0.95
    confidence = max(0.05, min(raw_confidence, 0.95))

    # Determine if trade is allowed
    min_conf = _safe_float(snapshot.get("ai_min_confidence"), 0.60)
    allow_trade = confidence >= min_conf

    # Dynamic SL/TP based on ADX and ATR
    trend_strong = adx_val >= 25
    trend_weak = adx_val < 20
    if trend_strong:
        sl_percent = round(max(atr_percent * 1.8, 0.6), 4)
        tp_percent = round(max(sl_percent * min_rr, sl_percent * 2.0), 4)
        suggested_leverage = 3
        risk_mode = "normal"
    elif trend_weak:
        sl_percent = round(max(atr_percent * 2.0, 0.7), 4)
        tp_percent = round(max(sl_percent * min_rr, sl_percent * 1.5), 4)
        suggested_leverage = 2
        risk_mode = "cautious"
    else:
        sl_percent = round(max(atr_percent * 2.0, 0.7), 4)
        tp_percent = round(max(sl_percent * min_rr, sl_percent * 1.8), 4)
        suggested_leverage = 3
        risk_mode = "normal"

    suggested_risk_percent = 0.5
    if allow_trade:
        if confidence >= 0.85:
            suggested_risk_percent = 1.2
            suggested_leverage = min(suggested_leverage + 1, 5)
        elif confidence >= 0.78:
            suggested_risk_percent = 0.9
        elif confidence >= 0.72:
            suggested_risk_percent = 0.75
        elif confidence >= 0.65:
            suggested_risk_percent = 0.6

    decision = {
        "provider": "local-heuristic",
        "mode": "enhanced",
        "allow_trade": allow_trade,
        "action": action,
        "confidence": round(confidence, 4),
        "suggested_risk_percent": suggested_risk_percent,
        "suggested_leverage": suggested_leverage,
        "recommended_margin_mode": "ISOLATED",
        "tp_percent": tp_percent,
        "sl_percent": sl_percent,
        "risk_reward_ratio": calculate_risk_reward_ratio(tp_percent, sl_percent),
        "risk_mode": risk_mode,
        "strategy_family": str(snapshot.get("trading_style", "SCALPING") or "SCALPING").upper(),
        "reason": (
            f"enhanced-heuristic: score={score} trend={trend} "
            f"adx={adx_val:.0f} macd_hist={macd_hist:.6f} "
            f"rsi={rsi:.0f} stoch=({stoch_k:.0f},{stoch_d:.0f}) "
            f"bb={bb_position} vol={vol_ratio:.1f}x "
            f"conf={confidence:.2f}"
        ),
    }
    gate = _quality_gate(snapshot, decision)
    if gate:
        decision.update(gate)
        decision["reason"] = f"{decision['reason']}; {gate['quality_gate_reason']}"
    return decision


def _normalize_decision(data: Dict[str, Any], snapshot: Dict[str, Any], provider: str, mode: str) -> Dict[str, Any]:
    fallback = _heuristic_decision(snapshot)
    action = str(data.get("action", fallback["action"]) or fallback["action"]).upper()
    if action not in {"BUY", "SELL", "HOLD"}:
        action = fallback["action"]

    sl_percent = max(_safe_float(data.get("sl_percent"), fallback["sl_percent"]), 0.1)
    tp_percent = max(_safe_float(data.get("tp_percent"), fallback["tp_percent"]), sl_percent * 1.1)
    rr_ratio = max(
        _safe_float(data.get("risk_reward_ratio"), 0.0),
        calculate_risk_reward_ratio(tp_percent, sl_percent),
    )

    confidence = _safe_float(data.get("confidence"), fallback["confidence"])
    confidence = max(0.05, min(confidence, 0.95))

    decision = {
        "provider": provider,
        "mode": mode,
        "allow_trade": bool(data.get("allow_trade", fallback["allow_trade"])),
        "action": action,
        "confidence": round(confidence, 4),
        "suggested_risk_percent": round(
            max(_safe_float(data.get("suggested_risk_percent"), fallback["suggested_risk_percent"]), 0.2),
            4,
        ),
        "suggested_leverage": max(int(_safe_float(data.get("suggested_leverage"), fallback["suggested_leverage"])), 1),
        "recommended_margin_mode": str(
            data.get("recommended_margin_mode", fallback["recommended_margin_mode"])
            or fallback["recommended_margin_mode"]
        ).upper(),
        "tp_percent": round(tp_percent, 4),
        "sl_percent": round(sl_percent, 4),
        "risk_reward_ratio": round(rr_ratio, 4),
        "risk_mode": str(data.get("risk_mode", fallback["risk_mode"]) or fallback["risk_mode"]),
        "strategy_family": str(
            data.get("strategy_family", fallback["strategy_family"]) or fallback["strategy_family"]
        ).upper(),
        "reason": str(data.get("reason", fallback["reason"]) or fallback["reason"]),
    }
    gate = _quality_gate(snapshot, decision)
    if gate:
        decision.update(gate)
        decision["reason"] = f"{decision['reason']}; {gate['quality_gate_reason']}"
    return decision


def _build_prompt(snapshot: Dict[str, Any]) -> str:
    payload = json.dumps(snapshot, ensure_ascii=False)
    return (
        "You are an elite institutional quantitative risk manager and master trader specializing in high-frequency scalping. "
        "Your absolute objective is to evaluate the provided market snapshot and protect capital while seeking a >75% win rate probability. "
        "Strictly analyze: "
        "1. Trend Alignment: If trend_5m, trend_15m, and trend_1h are conflicting, demand a strong reason or pullback confirmation before allowing trade. "
        "2. Momentum/RSI: Avoid buying tops (RSI > 70 for BUY) or selling bottoms (RSI < 30 for SELL) unless a strong breakout is clear. "
        "3. Volatility (ATR): Use ATR to calibrate SL. Set SL far enough from local noise but tight enough to protect capital. "
        "4. Risk Reward: Keep target TP at least 1.5 to 2.5x of SL unless scalping. "
        "Respect candidate_side if it matches momentum. If the setup is weak, conflicting, or lacks clear edge, you MUST set allow_trade: false and action: \"HOLD\". "
        "Output ONLY a raw JSON string matching this exact schema: "
        '{"allow_trade":true,"action":"BUY|SELL|HOLD","confidence":0.85,'
        '"suggested_risk_percent":0.75,"suggested_leverage":10,'
        '"recommended_margin_mode":"ISOLATED","tp_percent":1.5,'
        '"sl_percent":0.75,"risk_reward_ratio":2.0,"risk_mode":"conservative",'
        '"strategy_family":"SCALPING","reason":"detailed but concise trade thesis"}. '
        "Do not output markdown code blocks. Do not output any explanation outside the JSON block. "
        f"Snapshot Data: {payload}"
    )


def _request_ollama(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": _build_prompt(snapshot),
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.1,
            },
        },
        timeout=OLLAMA_TIMEOUT,
    )
    response.raise_for_status()
    payload = response.json()
    text = payload.get("response", "")
    parsed = _extract_json_block(text)
    if not parsed:
        raise ValueError("Ollama returned empty or invalid JSON")
    return parsed


def _request_groq(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY kosong")

    response = requests.post(
        GROQ_URL,
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": GROQ_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "You are trading risk assistant for crypto futures. Reply with JSON only.",
                },
                {
                    "role": "user",
                    "content": _build_prompt(snapshot),
                },
            ],
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
        },
        timeout=GROQ_TIMEOUT,
    )
    response.raise_for_status()
    payload = response.json()
    choices = payload.get("choices") or []
    if not choices:
        raise ValueError("Groq returned empty choices")
    message = choices[0].get("message") or {}
    text = message.get("content", "")
    parsed = _extract_json_block(text)
    if not parsed:
        raise ValueError("Groq returned empty or invalid JSON")
    return parsed


def decide_trade(snapshot):
    snapshot = snapshot if isinstance(snapshot, dict) else {}
    if AI_PROVIDER == "groq":
        try:
            groq_data = _request_groq(snapshot)
            return _normalize_decision(groq_data, snapshot, provider=f"groq:{GROQ_MODEL}", mode="groq")
        except Exception as exc:
            if OLLAMA_URL and OLLAMA_MODEL:
                try:
                    ollama_data = _request_ollama(snapshot)
                    decision = _normalize_decision(ollama_data, snapshot, provider=f"ollama:{OLLAMA_MODEL}", mode="ollama-fallback")
                    decision["reason"] = f"Groq failed: {exc} | {decision['reason']}"
                    return decision
                except Exception as ollama_exc:
                    fallback = _heuristic_decision(snapshot)
                    fallback["reason"] = f"Groq failed: {exc} | Ollama failed: {ollama_exc}"
                    return fallback
            fallback = _heuristic_decision(snapshot)
            fallback["reason"] = f"Groq fallback: {exc}"
            return fallback
    if OLLAMA_ENABLED or AI_PROVIDER == "ollama":
        try:
            ollama_data = _request_ollama(snapshot)
            return _normalize_decision(ollama_data, snapshot, provider=f"ollama:{OLLAMA_MODEL}", mode="ollama")
        except Exception as exc:
            fallback = _heuristic_decision(snapshot)
            fallback["reason"] = f"Ollama fallback: {exc}"
            return fallback
    return _heuristic_decision(snapshot)

