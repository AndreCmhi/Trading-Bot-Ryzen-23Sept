# upgrade_antigravity/ag_rrr_fee_guard.py
# Upgrade #3: Tolak trade jika RRR efektif setelah fee < minimum
# Pakai enhanced_risk.minimum_rrr_after_fees tapi enforce di pipeline

import os
from typing import Dict, Any

TAKER_FEE = 0.0004          # 0.04% per sisi Binance futures
MIN_EFFECTIVE_RRR = float(os.getenv('AG_MIN_EFFECTIVE_RRR', '1.8'))


def effective_rrr(tp_pct: float, sl_pct: float, leverage: int) -> float:
    """RRR setelah dikurangi round-trip fee pada margin."""
    fee_on_margin = TAKER_FEE * 2 * leverage * 100  # dalam %
    eff_tp = max(tp_pct - fee_on_margin, 0.0)
    eff_sl = sl_pct + fee_on_margin
    if eff_sl <= 0:
        return 0.0
    return round(eff_tp / eff_sl, 4)


def check_rrr_after_fees(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """
    Gate entry berdasarkan RRR efektif setelah fee.
    Baca tp_percent, sl_percent, suggested_leverage dari snapshot/decision.
    """
    tp  = float(snapshot.get('tp_percent', 0) or 0)
    sl  = float(snapshot.get('sl_percent', 0) or 0)
    lev = int(snapshot.get('suggested_leverage', 5) or 5)

    if sl <= 0 or tp <= 0:
        return {
            'allowed': False,
            'effective_rrr': 0.0,
            'reason': 'TP atau SL tidak valid (0). Trade ditolak.',
        }

    eff = effective_rrr(tp, sl, lev)
    raw_rrr = round(tp / sl, 4)

    if eff < MIN_EFFECTIVE_RRR:
        return {
            'allowed': False,
            'effective_rrr': eff,
            'raw_rrr': raw_rrr,
            'reason': (
                f'RRR efektif {eff:.2f} < minimum {MIN_EFFECTIVE_RRR} setelah fee '
                f'(TP {tp}%, SL {sl}%, lev {lev}x). Trade tidak worth.'
            ),
        }

    return {
        'allowed': True,
        'effective_rrr': eff,
        'raw_rrr': raw_rrr,
        'reason': f'RRR efektif {eff:.2f} — trade worth setelah fee.',
    }
