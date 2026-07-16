# Advanced Technical Indicators for Trading Bot
# Based on Crypto Futures Trading Guide

import math
from typing import Tuple, Dict, List, Any


def calculate_sma(prices, period=20):
    """Calculate Simple Moving Average"""
    series = [float(p) for p in prices if p]
    if len(series) < period:
        return 0.0
    window = series[-period:]
    return round(sum(window) / len(window), 8)


def calculate_std_dev(prices, period=20):
    """Calculate Standard Deviation"""
    series = [float(p) for p in prices if p]
    if len(series) < period:
        return 0.0
    window = series[-period:]
    mean = sum(window) / len(window)
    variance = sum((x - mean) ** 2 for x in window) / len(window)
    return round(math.sqrt(variance), 8)


def calculate_bollinger_bands(prices, period=20, std_dev=2):
    """Calculate Bollinger Bands (Middle, Upper, Lower)"""
    middle = calculate_sma(prices, period)
    if middle == 0.0:
        return {"upper": 0.0, "middle": 0.0, "lower": 0.0, "bandwidth": 0.0}
    
    std = calculate_std_dev(prices, period)
    upper = round(middle + (std_dev * std), 8)
    lower = round(middle - (std_dev * std), 8)
    bandwidth = round((upper - lower) / middle * 100, 4) if middle > 0 else 0.0
    
    return {
        "upper": upper,
        "middle": middle,
        "lower": lower,
        "bandwidth": bandwidth
    }


def calculate_macd(prices, fast=12, slow=26, signal=9):
    """Calculate MACD (Line, Signal, Histogram)"""
    if not prices or len(prices) < slow:
        return {"macd": 0.0, "signal": 0.0, "histogram": 0.0}
    
    ema_fast = calculate_ema(prices, fast)
    ema_slow = calculate_ema(prices, slow)
    macd_line = round(ema_fast - ema_slow, 8)
    
    # Calculate signal line (EMA of MACD)
    # For simplicity, using approximate signal
    signal_line = round(macd_line * 0.8, 8)  # Simplified
    histogram = round(macd_line - signal_line, 8)
    
    return {
        "macd": macd_line,
        "signal": signal_line,
        "histogram": histogram
    }


def calculate_rsi(prices, period=14):
    """Calculate Relative Strength Index"""
    series = [float(p) for p in prices if p]
    if len(series) < period + 1:
        return 50.0
    
    gains = []
    losses = []
    
    for i in range(1, len(series)):
        change = series[i] - series[i-1]
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))
    
    if len(gains) < period:
        return 50.0
    
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    
    if avg_loss == 0:
        return 100.0
    
    rs = avg_gain / avg_loss
    rsi = round(100 - (100 / (1 + rs)), 4)
    return rsi


def calculate_vwap(prices, volumes):
    """Calculate Volume Weighted Average Price"""
    if not prices or not volumes or len(prices) != len(volumes):
        return 0.0
    
    price_list = []
    volume_list = []
    for price, volume in zip(prices, volumes):
        if price is None or volume is None:
            continue
        try:
            price_list.append(float(price))
            volume_list.append(max(float(volume), 0.0))
        except (TypeError, ValueError):
            continue
    
    if len(price_list) != len(volume_list) or not volume_list:
        return 0.0
    
    total_pv = sum(p * v for p, v in zip(price_list, volume_list))
    total_volume = sum(volume_list)
    
    if total_volume == 0:
        return 0.0
    
    return round(total_pv / total_volume, 8)


def calculate_adx(highs, lows=None, closes=None, period=14):
    """Calculate Wilder ADX on the standard 0-100 scale."""
    if lows is None or closes is None:
        closes = [float(p) for p in highs if p is not None]
        highs = closes
        lows = closes
    else:
        highs = [float(p) for p in highs if p is not None]
        lows = [float(p) for p in lows if p is not None]
        closes = [float(p) for p in closes if p is not None]

    length = min(len(highs), len(lows), len(closes))
    if length < (period * 2) + 1:
        return 0.0

    highs = highs[-length:]
    lows = lows[-length:]
    closes = closes[-length:]
    true_ranges = []
    plus_dm = []
    minus_dm = []

    for i in range(1, length):
        high_diff = highs[i] - highs[i - 1]
        low_diff = lows[i - 1] - lows[i]
        true_range = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i - 1]),
            abs(lows[i] - closes[i - 1]),
        )
        true_ranges.append(true_range)
        plus_dm.append(high_diff if high_diff > low_diff and high_diff > 0 else 0.0)
        minus_dm.append(low_diff if low_diff > high_diff and low_diff > 0 else 0.0)

    atr = sum(true_ranges[:period])
    plus_smoothed = sum(plus_dm[:period])
    minus_smoothed = sum(minus_dm[:period])
    dx_values = []

    for i in range(period, len(true_ranges)):
        atr = atr - (atr / period) + true_ranges[i]
        plus_smoothed = plus_smoothed - (plus_smoothed / period) + plus_dm[i]
        minus_smoothed = minus_smoothed - (minus_smoothed / period) + minus_dm[i]
        if atr <= 0:
            dx_values.append(0.0)
            continue

        plus_di = 100.0 * (plus_smoothed / atr)
        minus_di = 100.0 * (minus_smoothed / atr)
        di_total = plus_di + minus_di
        dx_values.append(0.0 if di_total <= 0 else 100.0 * abs(plus_di - minus_di) / di_total)

    if len(dx_values) < period:
        return 0.0

    adx = sum(dx_values[:period]) / period
    for dx in dx_values[period:]:
        adx = ((adx * (period - 1)) + dx) / period

    return round(max(0.0, min(adx, 100.0)), 4)


def calculate_stochastic(prices, period=14, smooth=3):
    """Calculate Stochastic Oscillator (%K, %D)"""
    series = [float(p) for p in prices if p]
    if len(series) < period:
        return {"k": 50.0, "d": 50.0}
    
    window = series[-period:]
    high = max(window)
    low = min(window)
    current = series[-1]
    
    if high == low:
        return {"k": 50.0, "d": 50.0}
    
    k = round(((current - low) / (high - low)) * 100, 4)
    d = round(k * 0.9, 4)  # Simplified smoothing
    
    return {"k": k, "d": d}


def calculate_ema(prices, period=9):
    """Calculate Exponential Moving Average"""
    series = [float(p) for p in prices if p]
    if not series:
        return 0.0
    period = max(int(period or 1), 1)
    multiplier = 2 / (period + 1)
    ema = series[0]
    for price in series[1:]:
        ema = (price - ema) * multiplier + ema
    return round(ema, 8)

