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
    trend = "sideways"
    if last_price and ema_fast and ema_slow:
        if ema_fast > ema_slow and last_price >= ema_fast:
            trend = "bullish"
        elif ema_fast < ema_slow and last_price <= ema_fast:
            trend = "bearish"
    snapshot = {
        "symbol": str(symbol or "").upper(),
        "score": round(_safe_float(score), 4),
        "rsi": round(_safe_float(rsi, 50.0), 4),
        "last_price": round(last_price, 8),
        "ema_fast": round(ema_fast, 8),
        "ema_slow": round(ema_slow, 8),
        "atr_percent": atr_percent,
        "trend": trend,
        "close_count": len(series),
        "recent_closes": [round(value, 8) for value in series[-20:]],
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


def _heuristic_decision(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    score = _safe_float(snapshot.get("score"), 0.0)
    rsi = _safe_float(snapshot.get("rsi"), 50.0)
    trend = str(snapshot.get("trend", "sideways")).lower()
    candidate_side = str(snapshot.get("candidate_side", "HOLD")).upper()
    atr_percent = max(_safe_float(snapshot.get("atr_percent"), 0.35), 0.1)
    min_rr = max(_safe_float(snapshot.get("min_risk_reward_ratio"), 2.0), 1.2)

    action = "HOLD"
    allow_trade = False
    confidence = 0.45

    if candidate_side in {"BUY", "SELL"}:
        action = candidate_side

    if action == "BUY" and trend == "bullish" and score >= 6 and rsi < 72:
        allow_trade = True
        confidence = 0.68 + min(max((score - 6) * 0.03, 0.0), 0.17)
    elif action == "SELL" and trend == "bearish" and score >= 6 and rsi > 28:
        allow_trade = True
        confidence = 0.68 + min(max((score - 6) * 0.03, 0.0), 0.17)
    else:
        action = action if action in {"BUY", "SELL"} else "HOLD"
        confidence = 0.42 if action != "HOLD" else 0.35

    sl_percent = round(max(atr_percent * 1.15, 0.35), 4)
    tp_percent = round(max(sl_percent * min_rr, sl_percent * 1.8), 4)
    suggested_risk_percent = 0.5
    if allow_trade and confidence >= 0.78:
        suggested_risk_percent = 1.0
    elif allow_trade and confidence >= 0.7:
        suggested_risk_percent = 0.75

    return {
        "provider": "local-heuristic",
        "mode": "fallback",
        "allow_trade": allow_trade,
        "action": action,
        "confidence": round(confidence, 4),
        "suggested_risk_percent": suggested_risk_percent,
        "suggested_leverage": 10,
        "recommended_margin_mode": "ISOLATED",
        "tp_percent": tp_percent,
        "sl_percent": sl_percent,
        "risk_reward_ratio": calculate_risk_reward_ratio(tp_percent, sl_percent),
        "risk_mode": "normal",
        "strategy_family": str(snapshot.get("trading_style", "SCALPING") or "SCALPING").upper(),
        "reason": "Fallback heuristic decision used.",
    }


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

    return {
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

