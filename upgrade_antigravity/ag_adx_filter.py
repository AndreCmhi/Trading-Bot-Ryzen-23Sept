# upgrade_antigravity/ag_adx_filter.py
# Upgrade #1: Wajib ADX >= 20 sebelum entry
# Tanpa trend kuat = skip, bukan gamble

from typing import Dict, Any

MIN_ADX_TRENDING = float(__import__('os').getenv('AG_MIN_ADX_TRENDING', '20'))
MIN_ADX_STRONG   = float(__import__('os').getenv('AG_MIN_ADX_STRONG',   '25'))


def classify_adx(adx: float) -> str:
    """Return: 'strong' | 'trending' | 'weak'"""
    if adx >= MIN_ADX_STRONG:
        return 'strong'
    if adx >= MIN_ADX_TRENDING:
        return 'trending'
    return 'weak'


def check_adx_entry(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """
    Gate entry berdasarkan ADX.
    Return dict: {allowed, adx_class, adx, reason}
    """
    adx = float(snapshot.get('adx', 0) or 0)
    cls = classify_adx(adx)

    if cls == 'weak':
        return {
            'allowed': False,
            'adx_class': cls,
            'adx': adx,
            'reason': f'ADX {adx:.1f} terlalu lemah (min {MIN_ADX_TRENDING}). Skip — tidak ada trend.',
        }

    bonus = 0.05 if cls == 'strong' else 0.02
    return {
        'allowed': True,
        'adx_class': cls,
        'adx': adx,
        'confidence_bonus': bonus,
        'reason': f'ADX {adx:.1f} ({cls}) — trend valid untuk entry.',
    }
