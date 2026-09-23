# upgrade_antigravity/ag_volume_fetch.py
# Upgrade #2: Fetch volume NYATA dari exchange
# Gantikan dummy v15m = [100]*20 di engine.py

from typing import List


def get_real_volumes(symbol: str, interval: str = '15m', limit: int = 30) -> List[float]:
    """
    Fetch volume nyata dari Binance futures klines.
    Return list float (volume candle). Kosong jika gagal.
    """
    try:
        import state
        if not state.client:
            state.init_client()
        klines = state.client.futures_klines(symbol=symbol, interval=interval, limit=limit)
        return [float(k[5]) for k in klines]  # index 5 = volume
    except Exception as exc:
        print(f'[ag_volume_fetch] Error {symbol}: {exc}')
        return []


def volume_ratio(volumes: List[float], lookback: int = 10) -> float:
    """
    Ratio volume candle terakhir vs rata-rata {lookback} candle sebelumnya.
    > 1.0 = volume di atas rata-rata.
    """
    if len(volumes) < lookback + 1:
        return 1.0
    avg = sum(volumes[-(lookback + 1):-1]) / lookback
    if avg <= 0:
        return 1.0
    return round(volumes[-1] / avg, 4)


def check_volume_entry(volumes: List[float], min_ratio: float = 0.9) -> dict:
    """
    Gate entry berdasarkan volume ratio.
    min_ratio 0.9 = volume minimal 90% dari rata-rata (tidak sepi).
    """
    ratio = volume_ratio(volumes)
    if ratio < min_ratio:
        return {
            'allowed': False,
            'volume_ratio': ratio,
            'reason': f'Volume ratio {ratio:.2f}x di bawah minimum {min_ratio}x. Likuiditas sepi.',
        }
    bonus = min(0.05, (ratio - 1.0) * 0.03) if ratio > 1.0 else 0.0
    return {
        'allowed': True,
        'volume_ratio': ratio,
        'confidence_bonus': bonus,
        'reason': f'Volume ratio {ratio:.2f}x — likuiditas cukup.',
    }
