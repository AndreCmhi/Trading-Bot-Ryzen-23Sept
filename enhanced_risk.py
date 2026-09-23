# ENHANCED RISK MANAGEMENT MODULE
# Based on Crypto Futures Trading Guide - Advanced Risk Rules
# Line count: 65 lines (WELL UNDER 350 LIMIT)

import math
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional


def calculate_kelly_criterion(win_rate: float, avg_win: float, avg_loss: float) -> float:
    """Calculate Kelly Criterion for optimal position sizing
    Formula: f* = (bp - q) / b
    where: b = avg_win/avg_loss, p = win_rate, q = 1-p
    """
    if avg_loss <= 0 or win_rate <= 0 or win_rate >= 1:
        return 0.1  # Default conservative position
    
    b = avg_win / avg_loss
    p = win_rate
    q = 1 - p
    kelly = (b * p - q) / b
    
    # Use fractional Kelly (half) for safety
    return max(0.01, min(kelly * 0.5, 0.2))


def calculate_daily_loss_limit(balance: float) -> Tuple[float, float]:
    """Calculate daily loss limits based on equity
    Golden Rule: Max 3% daily loss, stop trading if hit
    """
    daily_limit_percent = 3.0  # Max 3% loss per day
    daily_limit_usdt = balance * (daily_limit_percent / 100.0)
    warning_threshold = daily_limit_usdt * 0.5  # Warn at 50% of limit
    return round(daily_limit_usdt, 2), round(warning_threshold, 2)


def calculate_drawdown_protection(balance: float, peak_balance: float) -> Dict[str, float]:
    """Calculate drawdown protection levels
    Critical levels: 10% warning, 15% reduce size, 20% stop trading
    """
    if peak_balance <= 0:
        return {"drawdown_pct": 0.0, "risk_multiplier": 1.0, "should_stop": False}
    
    drawdown_pct = ((peak_balance - balance) / peak_balance) * 100
    
    risk_multiplier = 1.0
    should_stop = False
    
    if drawdown_pct >= 20.0:
        risk_multiplier = 0.0  # Stop trading
        should_stop = True
    elif drawdown_pct >= 15.0:
        risk_multiplier = 0.25  # Reduce position to 25%
    elif drawdown_pct >= 10.0:
        risk_multiplier = 0.5  # Reduce position to 50%
    
    return {
        "drawdown_pct": round(drawdown_pct, 2),
        "risk_multiplier": risk_multiplier,
        "should_stop": should_stop
    }


def calculate_position_size_kelly(
    balance: float, 
    win_rate: float, 
    avg_win: float, 
    avg_loss: float,
    risk_per_trade: float = 0.01
) -> Dict[str, float]:
    """Calculate position size using Kelly Criterion with safety limits
    Returns optimal position size and risk amount
    """
    # Calculate Kelly fraction
    kelly_fraction = calculate_kelly_criterion(win_rate, avg_win, avg_loss)
    
    # Apply multiple constraints
    max_position = balance * kelly_fraction
    
    # Never risk more than 2% per trade (conservative)
    max_risk = balance * risk_per_trade
    
    # Never risk more than 10% of balance even with Kelly
    absolute_max = balance * 0.1
    
    final_position = min(max_position, max_risk, absolute_max)
    final_risk_pct = (final_position / balance) * 100 if balance > 0 else 0.0
    
    return {
        "position_size_usdt": round(final_position, 2),
        "risk_percent": round(final_risk_pct, 2),
        "kelly_fraction": round(kelly_fraction, 4),
        "max_position": round(max_position, 2),
        "max_risk": round(max_risk, 2)
    }


def calculate_consecutive_loss_protection(
    consecutive_losses: int, 
    max_allowed: int = 3
) -> Dict[str, any]:
    """Adjust trading based on consecutive losses
    Strategy: Reduce position size or stop after too many losses
    """
    if consecutive_losses >= max_allowed:
        return {
            "allow_trade": False,
            "reason": f"Max consecutive losses reached ({consecutive_losses}/{max_allowed})",
            "cooldown_minutes": 60 * consecutive_losses  # Longer cooldown for more losses
        }
    
    # Gradually reduce position size
    reduction_factor = 1.0 / (1 + consecutive_losses * 0.5)
    
    return {
        "allow_trade": True,
        "reason": f"{consecutive_losses} consecutive losses, position reduced by {round((1-reduction_factor)*100)}%",
        "reduction_factor": round(reduction_factor, 2)
    }


def check_funding_rate_risk(funding_rate: float) -> bool:
    """Check if funding rate is too extreme for safe trading
    High positive funding (>0.1%): Be cautious of long
    High negative funding (<-0.1%): Be cautious of short
    """
    if abs(funding_rate) > 0.001:  # 0.1%
        return False  # High risk
    return True  # Acceptable risk

def check_market_sentiment(btc_trend: str, trade_side: str) -> bool:
    """Filter korelasi: Jangan melawan tren BTC"""
    btc_trend = str(btc_trend or "sideways").lower()
    trade_side = str(trade_side or "HOLD").upper()
    if btc_trend == "bearish" and trade_side == "BUY": return False
    if btc_trend == "bullish" and trade_side == "SELL": return False
    return True

def is_exposure_safe(positions, new_trade_notional, balance, max_exposure_ratio=3.0):
    """Proteksi Exposure: Batasi total nilai posisi agar tidak overload"""
    current_notional = sum(abs(float(p.get("positionAmt", 0)) * float(p.get("entryPrice", 0))) for p in positions if float(p.get("positionAmt", 0)) != 0)
    total_potential = current_notional + new_trade_notional
    if balance <= 0: return {"allowed": False, "reason": "Saldo tidak cukup"}
    ratio = total_potential / balance
    return {"allowed": ratio <= max_exposure_ratio, "ratio": round(ratio, 2), "reason": f"Leverage total {ratio:.2f}x (Batas: {max_exposure_ratio}x)"}
def calculate_atr_position_size(balance, risk_pct, price, atr, risk_reward=2.5):
    """
    Menghitung ukuran posisi berdasarkan volatilitas (ATR).
    Rumus: Qty = (Balance * Risk%) / (ATR * Multiplier)
    """
    risk_amount = balance * (risk_pct / 100)
    # Stop Loss biasanya 1.5x - 2x ATR
    sl_distance = atr * 1.5
    if sl_distance <= 0: return 0
    
    qty = risk_amount / sl_distance
    return {
        "qty": round(qty, 4),
        "sl_price": round(price - sl_distance, 2), # Contoh untuk Long
        "tp_price": round(price + (sl_distance * risk_reward), 2)
    }

BINANCE_FUTURES_TAKER_FEE = 0.0004  # 0.04% per side = 0.08% round trip


def minimum_rrr_after_fees(tp_percent, sl_percent, leverage=5):
    """Calculate effective RRR after accounting for round-trip trading fees.
    Entry and exit both use taker fee. With leverage, fee impact on margin is multiplied.
    """
    fee_pct_on_margin = BINANCE_FUTURES_TAKER_FEE * 2 * leverage * 100
    effective_tp = max(tp_percent - fee_pct_on_margin, 0.0)
    effective_sl = sl_percent + fee_pct_on_margin
    if effective_sl <= 0:
        return 0.0
    return round(effective_tp / effective_sl, 4)


def is_trade_worth_after_fees(tp_percent, sl_percent, leverage=5, min_rrr=2.0):
    """Return True only if trade is profitable after fees with required RRR."""
    rrr = minimum_rrr_after_fees(tp_percent, sl_percent, leverage)
    return rrr >= min_rrr

