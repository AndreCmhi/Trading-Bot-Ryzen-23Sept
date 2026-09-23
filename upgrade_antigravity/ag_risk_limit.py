# upgrade_antigravity/ag_risk_limit.py
# Upgrade #5: Hourly loss limit berbasis % equity, bukan nilai flat
# Max open positions adaptif (kualitas > kuantitas)
# Fix: bot tidak freeze total saat saldo kecil

import os
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Env-configurable
HOURLY_LOSS_PCT_EQUITY  = float(os.getenv('AG_HOURLY_LOSS_PCT_EQUITY',  '1.5'))  # 1.5% equity/jam
DAILY_LOSS_PCT_EQUITY   = float(os.getenv('AG_DAILY_LOSS_PCT_EQUITY',   '4.0'))  # 4% equity/hari
MAX_OPEN_POSITIONS      = int(os.getenv('AG_MAX_OPEN_POSITIONS',        '8'))    # max posisi aktif
CONSEC_LOSS_HARD_STOP   = int(os.getenv('AG_CONSEC_LOSS_HARD_STOP',    '5'))    # stop total sementara
CONSEC_LOSS_REDUCE      = int(os.getenv('AG_CONSEC_LOSS_REDUCE',       '3'))    # mulai reduce size


def _safe_float(v, d=0.0):
    try:
        return float(v)
    except Exception:
        return d


def _trade_time(trade: dict):
    for k in ('closed_time', 'time'):
        v = trade.get(k)
        if not v:
            continue
        if isinstance(v, (int, float)):
            try:
                return datetime.fromtimestamp(v / 1000)
            except Exception:
                continue
        try:
            return datetime.strptime(str(v), '%Y-%m-%d %H:%M:%S')
        except Exception:
            continue
    return None


def evaluate_adaptive_limits(
    equity: float,
    closed_trades: List[dict],
    open_count: int,
    consecutive_losses: int,
) -> Dict[str, Any]:
    """
    Evaluasi limit adaptif berbasis equity.
    Return: {allowed, policy, risk_multiplier, leverage_cap, reason}
    """
    now = datetime.now()
    hourly_cut = now - timedelta(hours=1)
    daily_cut  = now - timedelta(hours=24)

    equity = max(_safe_float(equity), 1.0)
    net_pnl = sum(_safe_float(t.get('pnl'), 0.0) for t in closed_trades if (_trade_time(t) or datetime.min) >= daily_cut)
    # 25% dari PNL bersih jika profit, fallback ke % equity jika PNL belum positif
    if net_pnl > 0:
        hourly_limit = max(net_pnl * 0.25, 0.5)
    else:
        hourly_limit = equity * (HOURLY_LOSS_PCT_EQUITY / 100.0)
    daily_limit  = equity * (DAILY_LOSS_PCT_EQUITY  / 100.0)

    hourly_loss = abs(sum(
        min(_safe_float(t.get('pnl'), 0.0), 0.0)
        for t in closed_trades
        if (_trade_time(t) or datetime.min) >= hourly_cut
    ))
    daily_loss = abs(sum(
        min(_safe_float(t.get('pnl'), 0.0), 0.0)
        for t in closed_trades
        if (_trade_time(t) or datetime.min) >= daily_cut
    ))

    # Hard stop: consecutive losses terlalu banyak
    if consecutive_losses >= CONSEC_LOSS_HARD_STOP:
        return {
            'allowed': False,
            'policy': 'ag_consec_hard_stop',
            'risk_multiplier': 0.0,
            'leverage_cap': 1,
            'reason': (
                f'{consecutive_losses} loss beruntun melebihi batas {CONSEC_LOSS_HARD_STOP}. '
                'Istirahat wajib. Bot berhenti sampai manual reset atau sesi baru.'
            ),
        }

    # Hard stop: daily loss limit equity-based
    if daily_loss >= daily_limit:
        return {
            'allowed': False,
            'policy': 'ag_daily_loss_equity',
            'risk_multiplier': 0.0,
            'leverage_cap': 1,
            'reason': (
                f'Daily loss {daily_loss:.2f} USDT >= limit {daily_limit:.2f} USDT '
                f'({DAILY_LOSS_PCT_EQUITY}% dari equity {equity:.2f}). Stop trading hari ini.'
            ),
        }

    # Hard stop: hourly loss limit equity-based
    if hourly_loss >= hourly_limit:
        return {
            'allowed': False,
            'policy': 'ag_hourly_loss_equity',
            'risk_multiplier': 0.0,
            'leverage_cap': 1,
            'reason': (
                f'Hourly loss {hourly_loss:.2f} USDT >= limit {hourly_limit:.2f} USDT '
                f'({HOURLY_LOSS_PCT_EQUITY}% dari equity {equity:.2f}). Cooldown 1 jam.'
            ),
        }

    # Open position cap
    if open_count >= MAX_OPEN_POSITIONS:
        return {
            'allowed': False,
            'policy': 'ag_max_positions',
            'risk_multiplier': 0.0,
            'leverage_cap': 3,
            'reason': f'Open positions {open_count} >= max {MAX_OPEN_POSITIONS}. Tunggu posisi tutup.',
        }

    # Reduce size saat consecutive loss meningkat
    if consecutive_losses >= CONSEC_LOSS_REDUCE:
        reduction = max(0.25, 1.0 - (consecutive_losses - CONSEC_LOSS_REDUCE + 1) * 0.2)
        return {
            'allowed': True,
            'policy': 'ag_consec_reduce',
            'risk_multiplier': round(reduction, 2),
            'leverage_cap': 4,
            'reason': (
                f'{consecutive_losses} loss beruntun — size dikurangi ke {reduction*100:.0f}%. '
                f'Hourly loss: {hourly_loss:.2f}/{hourly_limit:.2f} USDT.'
            ),
        }

    # Warning zone hourly (>60% dari limit)
    if hourly_loss >= hourly_limit * 0.6:
        return {
            'allowed': True,
            'policy': 'ag_hourly_caution',
            'risk_multiplier': 0.6,
            'leverage_cap': 4,
            'reason': (
                f'Hourly loss {hourly_loss:.2f}/{hourly_limit:.2f} USDT (>60% limit). '
                'Size dikurangi 40% sebagai tindakan hati-hati.'
            ),
        }

    return {
        'allowed': True,
        'policy': 'ag_normal',
        'risk_multiplier': 1.0,
        'leverage_cap': 10,
        'reason': f'Semua limit aman. Loss jam ini: {hourly_loss:.2f}/{hourly_limit:.2f} USDT.',
    }
