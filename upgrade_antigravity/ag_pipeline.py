# upgrade_antigravity/ag_pipeline.py
# ANTIGRAVITY UPGRADE PIPELINE
# Drop-in integrator: panggil satu fungsi ini sebelum open_position
#
# Urutan gate (henti lebih awal jika gagal):
#   1. ADX filter       -> trend strength wajib
#   2. Volume check     -> likuiditas nyata
#   3. RSI zone check   -> kontekstual (trending vs ranging)
#   4. RRR fee guard    -> trade harus worth setelah biaya
#   5. Adaptive limits  -> equity-based loss limit & position cap
#
# Cara pakai di engine/strategy_runner:
#   from upgrade_antigravity.ag_pipeline import antigravity_gate
#   result = antigravity_gate(snapshot, decision, equity, closed_trades, open_count, consecutive_losses, symbol)
#   if not result['allowed']:
#       log(result['reason']); skip entry

from typing import Dict, Any, List

from upgrade_antigravity.ag_adx_filter   import check_adx_entry
from upgrade_antigravity.ag_volume_fetch import get_real_volumes, check_volume_entry
from upgrade_antigravity.ag_rsi_zone     import check_rsi_zone
from upgrade_antigravity.ag_rrr_fee_guard import check_rrr_after_fees
from upgrade_antigravity.ag_risk_limit   import evaluate_adaptive_limits


def antigravity_gate(
    snapshot: Dict[str, Any],
    decision: Dict[str, Any],
    equity: float,
    closed_trades: List[dict],
    open_count: int,
    consecutive_losses: int,
    symbol: str = '',
    volumes: List[float] = None,
    min_volume_ratio: float = 0.9,
) -> Dict[str, Any]:
    """
    Jalankan semua gate Antigravity secara berurutan.
    Return dict dengan keys:
      allowed         bool
      reason          str
      confidence_bonus float  (accumulated dari gate yang lulus)
      risk_multiplier float
      leverage_cap    int
      gate_results    dict  (detail tiap gate)
    """
    gates = {}
    confidence_bonus = 0.0

    # --- Merge snapshot + decision untuk context lengkap ---
    ctx = {**snapshot, **decision}
    action = str(ctx.get('action', 'HOLD') or 'HOLD').upper()

    # Jika HOLD, lewati semua filter teknikal
    if action == 'HOLD':
        return _pass_all(gates, 'HOLD — tidak ada gate yang perlu dilewati.', 0.0, 1.0, 10)

    # === GATE 1: ADX ===
    adx_res = check_adx_entry(ctx)
    gates['adx'] = adx_res
    if not adx_res['allowed']:
        return _block(gates, adx_res['reason'], 'adx_weak')
    confidence_bonus += adx_res.get('confidence_bonus', 0.0)
    # Simpan adx_class ke ctx untuk gate RSI
    ctx['adx_class'] = adx_res.get('adx_class', 'weak')

    # === GATE 2: VOLUME ===
    if volumes is None:
        volumes = get_real_volumes(symbol, interval='15m', limit=30) if symbol else []
    vol_res = check_volume_entry(volumes, min_ratio=min_volume_ratio)
    gates['volume'] = vol_res
    if not vol_res['allowed']:
        return _block(gates, vol_res['reason'], 'volume_low')
    confidence_bonus += vol_res.get('confidence_bonus', 0.0)

    # === GATE 3: RSI ZONE ===
    rsi_res = check_rsi_zone(ctx)
    gates['rsi'] = rsi_res
    if not rsi_res['allowed']:
        return _block(gates, rsi_res['reason'], 'rsi_zone')
    confidence_bonus += rsi_res.get('confidence_bonus', 0.0)

    # === GATE 4: RRR FEE GUARD ===
    rrr_res = check_rrr_after_fees(ctx)
    gates['rrr'] = rrr_res
    if not rrr_res['allowed']:
        return _block(gates, rrr_res['reason'], 'rrr_insufficient')

    # === GATE 5: ADAPTIVE RISK LIMITS ===
    lim_res = evaluate_adaptive_limits(equity, closed_trades, open_count, consecutive_losses)
    gates['risk_limits'] = lim_res
    if not lim_res['allowed']:
        return _block(gates, lim_res['reason'], lim_res.get('policy', 'risk_limit'))

    # Semua gate lulus
    return {
        'allowed': True,
        'reason': (
            f'Antigravity OK: ADX {adx_res["adx"]:.1f} ({adx_res["adx_class"]}), '
            f'Vol {vol_res["volume_ratio"]:.2f}x, '
            f'RSI valid, RRR eff {rrr_res["effective_rrr"]:.2f}. '
            + lim_res["reason"]
        ),
        'confidence_bonus': round(confidence_bonus, 4),
        'risk_multiplier': lim_res.get('risk_multiplier', 1.0),
        'leverage_cap': lim_res.get('leverage_cap', 10),
        'gate_results': gates,
        'block_gate': None,
    }


def _block(gates, reason, gate_name) -> Dict[str, Any]:
    return {
        'allowed': False,
        'reason': reason,
        'confidence_bonus': 0.0,
        'risk_multiplier': 0.0,
        'leverage_cap': 1,
        'gate_results': gates,
        'block_gate': gate_name,
    }


def _pass_all(gates, reason, conf, risk_mult, lev_cap) -> Dict[str, Any]:
    return {
        'allowed': True,
        'reason': reason,
        'confidence_bonus': conf,
        'risk_multiplier': risk_mult,
        'leverage_cap': lev_cap,
        'gate_results': gates,
        'block_gate': None,
    }
