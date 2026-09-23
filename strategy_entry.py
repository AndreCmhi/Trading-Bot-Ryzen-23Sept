# strategy_entry.py
# Modul konfluensi untuk Win Rate & PNL Tinggi
# Prinsip: Trend (1H) + Pullback (15M) + Momentum (RSI) + Volume
# PATCHED: return adx, rsi, tp_percent, sl_percent untuk Antigravity pipeline

import advanced_indicators as ind


def _pct_distance(price_a, price_b):
    if price_b <= 0:
        return 0.0
    return abs(price_a - price_b) / price_b * 100


def check_confluence_entry(symbol, klines_1h, klines_15m, volumes_15m):
    """
    Mengecek apakah setup memenuhi kriteria konfluensi:
    1. Trend Filter (1H): EMA 20 > EMA 50 (Uptrend) atau sebaliknya.
    2. Pullback (15M): Harga menyentuh/dekat EMA 20.
    3. Momentum (15M): RSI > 50 (Long) atau < 50 (Short).
    4. Volume: Volume candle konfirmasi > rata-rata volume sebelumnya.
    Juga hitung ADX 1H untuk Antigravity gate.
    """
    if len(klines_1h) < 50 or len(klines_15m) < 20:
        return {"allow": False, "reason": "Data klines tidak cukup"}

    # 1. Trend Filter (1H)
    ema20_1h = ind.calculate_ema(klines_1h, 20)
    ema50_1h = ind.calculate_ema(klines_1h, 50)
    adx_1h   = ind.calculate_adx(klines_1h)  # ADX dari 1H closes

    trend = "NONE"
    if ema20_1h > ema50_1h:
        trend = "UP"
    elif ema20_1h < ema50_1h:
        trend = "DOWN"

    if trend == "NONE":
        return {"allow": False, "reason": "Trend 1H tidak jelas (Sideways)"}

    # 2. Pullback & Entry Confirmation (15M)
    price_now = klines_15m[-1]
    ema20_15m = ind.calculate_ema(klines_15m, 20)
    rsi_15m   = ind.calculate_rsi(klines_15m, 14)

    # 3. Volume Confirmation
    if len(volumes_15m) >= 6:
        avg_vol  = sum(volumes_15m[-6:-1]) / 5
        curr_vol = volumes_15m[-1]
        vol_ok   = curr_vol > avg_vol
    else:
        vol_ok = False

    # === Logika Konfluensi Long ===
    if trend == "UP":
        is_pullback = price_now <= (ema20_15m * 1.002)
        is_momentum = rsi_15m > 50
        score = sum([is_pullback, is_momentum, vol_ok])

        if score >= 2:
            sl_price = min(klines_15m[-5:])
            tp_price = price_now + abs(price_now - sl_price) * 2.5
            sl_pct   = _pct_distance(price_now, sl_price)
            tp_pct   = _pct_distance(tp_price, price_now)
            return {
                "allow":      True,
                "side":       "BUY",
                "action":     "BUY",
                "score":      score + 1,
                "rsi":        round(rsi_15m, 2),
                "adx":        round(adx_1h, 4),
                "sl_price":   sl_price,
                "tp_price":   tp_price,
                "sl_percent": round(max(sl_pct, 0.1), 4),
                "tp_percent": round(tp_pct, 4),
                "leverage":   5,
                "reason":     f"Uptrend 1H. ADX {adx_1h:.1f}. Pullback: {is_pullback}, RSI: {rsi_15m:.2f}, Vol: {vol_ok}",
            }

    # === Logika Konfluensi Short ===
    if trend == "DOWN":
        is_pullback = price_now >= (ema20_15m * 0.998)
        is_momentum = rsi_15m < 50
        score = sum([is_pullback, is_momentum, vol_ok])

        if score >= 2:
            sl_price = max(klines_15m[-5:])
            tp_price = price_now - abs(price_now - sl_price) * 2.5
            sl_pct   = _pct_distance(price_now, sl_price)
            tp_pct   = _pct_distance(price_now, tp_price)
            return {
                "allow":      True,
                "side":       "SELL",
                "action":     "SELL",
                "score":      score + 1,
                "rsi":        round(rsi_15m, 2),
                "adx":        round(adx_1h, 4),
                "sl_price":   sl_price,
                "tp_price":   tp_price,
                "sl_percent": round(max(sl_pct, 0.1), 4),
                "tp_percent": round(tp_pct, 4),
                "leverage":   5,
                "reason":     f"Downtrend 1H. ADX {adx_1h:.1f}. Pullback: {is_pullback}, RSI: {rsi_15m:.2f}, Vol: {vol_ok}",
            }

    return {"allow": False, "reason": "Konfluensi tidak terpenuhi"}
