# upgrade_antigravity/ag_rsi_zone.py
# Upgrade #4: RSI zone berbeda untuk trending vs ranging
# ADX kuat -> boleh RSI tinggi (momentum continuation)
# ADX lemah -> zona ketat (reversal territory berbahaya)

from typing import Dict, Any


def check_rsi_zone(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validasi RSI berdasarkan konteks ADX (trending vs ranging).
    Return: {allowed, rsi_class, reason, confidence_bonus}
    """
    rsi        = float(snapshot.get('rsi', 50) or 50)
    adx        = float(snapshot.get('adx', 0) or 0)
    action     = str(snapshot.get('action', 'HOLD') or 'HOLD').upper()
    adx_class  = snapshot.get('adx_class', 'weak')  # diisi ag_adx_filter

    if action not in ('BUY', 'SELL'):
        return {'allowed': True, 'rsi_class': 'neutral', 'reason': 'HOLD — RSI check skip.', 'confidence_bonus': 0.0}

    trending = adx_class in ('strong', 'trending')  # ADX >= 20

    if action == 'BUY':
        if trending:
            # Trending: momentum continuation valid sampai RSI 80
            # Overbought ekstrem (>82) tetap blok
            if rsi > 82:
                return _block(rsi, 'BUY overbought ekstrem RSI>82 (trending)', adx_class)
            if 45 <= rsi <= 80:
                return _pass(rsi, adx_class, bonus=0.06 if rsi <= 65 else 0.03)
            if rsi < 45:
                return _pass(rsi, adx_class, bonus=0.04, note='RSI pullback saat trending')
            # 80 < rsi <= 82
            return _pass(rsi, adx_class, bonus=0.01, note='RSI tinggi tapi masih momentum trending')
        else:
            # Ranging: zona ketat 42-62
            if 42 <= rsi <= 62:
                return _pass(rsi, adx_class, bonus=0.05)
            return _block(rsi, f'BUY RSI {rsi:.1f} di luar zona ranging 42-62 (ADX lemah)', adx_class)

    else:  # SELL
        if trending:
            if rsi < 18:
                return _block(rsi, 'SELL oversold ekstrem RSI<18 (trending)', adx_class)
            if 20 <= rsi <= 55:
                return _pass(rsi, adx_class, bonus=0.06 if rsi >= 35 else 0.03)
            if rsi > 55:
                return _pass(rsi, adx_class, bonus=0.04, note='RSI pullback saat downtrend')
            # 18 <= rsi < 20
            return _pass(rsi, adx_class, bonus=0.01, note='RSI rendah tapi masih momentum bearish')
        else:
            if 38 <= rsi <= 58:
                return _pass(rsi, adx_class, bonus=0.05)
            return _block(rsi, f'SELL RSI {rsi:.1f} di luar zona ranging 38-58 (ADX lemah)', adx_class)


def _pass(rsi, adx_class, bonus=0.0, note='') -> Dict[str, Any]:
    msg = f'RSI {rsi:.1f} valid zona {adx_class}'
    if note:
        msg += f' — {note}'
    return {'allowed': True, 'rsi_class': adx_class, 'confidence_bonus': bonus, 'reason': msg}


def _block(rsi, why, adx_class) -> Dict[str, Any]:
    return {
        'allowed': False,
        'rsi_class': adx_class,
        'confidence_bonus': 0.0,
        'reason': f'RSI gate: {why}.',
    }
