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



