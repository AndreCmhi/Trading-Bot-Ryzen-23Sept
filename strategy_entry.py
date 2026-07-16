# strategy_entry.py
# Modul konfluensi untuk Win Rate & PNL Tinggi
# Prinsip: Trend (1H) + Pullback (15M) + Momentum (RSI) + Volume

import advanced_indicators as ind

def check_confluence_entry(symbol, klines_1h, klines_15m, volumes_15m):
    """
    Mengecek apakah setup memenuhi kriteria konfluensi:
    1. Trend Filter (1H): EMA 20 > EMA 50 (Uptrend) atau sebaliknya.
    2. Pullback (15M): Harga menyentuh/dekat EMA 20.
    3. Momentum (15M): RSI > 50 (Long) atau < 50 (Short).
    4. Volume: Volume candle konfirmasi > rata-rata volume sebelumnya.
    """
    
    if len(klines_1h) < 50 or len(klines_15m) < 20:
        return {"allow": False, "reason": "Data klines tidak cukup"}

    # 1. Trend Filter (1H)
    ema20_1h = ind.calculate_ema(klines_1h, 20)
    ema50_1h = ind.calculate_ema(klines_1h, 50)
    
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
    rsi_15m = ind.calculate_rsi(klines_15m, 14)
    
    # 3. Volume Confirmation
    avg_vol = sum(volumes_15m[-6:-1]) / 5
    curr_vol = volumes_15m[-1]
    vol_ok = curr_vol > avg_vol

    # Logika Konfluensi Long
    if trend == "UP":
        # Pullback: Harga mendekati EMA 20 (toleransi 0.2%)
        is_pullback = price_now <= (ema20_15m * 1.002)
        is_momentum = rsi_15m > 50
        
        score = sum([is_pullback, is_momentum, vol_ok])
        
        if score >= 2: # Minimal 3 konfluensi (Trend + 2 lainnya)
            return {
                "allow": True,
                "side": "BUY",
                "score": score + 1, # +1 untuk trend
                "reason": f"Uptrend 1H. Pullback: {is_pullback}, RSI: {rsi_15m:.2f}, Vol: {vol_ok}",
                "sl_price": min(klines_15m[-5:]), # SL di swing low terdekat
                "tp_price": price_now + (abs(price_now - min(klines_15m[-5:])) * 2.5) # RR 1:2.5
            }

    # Logika Konfluensi Short
    if trend == "DOWN":
        is_pullback = price_now >= (ema20_15m * 0.998)
        is_momentum = rsi_15m < 50
        
        score = sum([is_pullback, is_momentum, vol_ok])
        
        if score >= 2:
            return {
                "allow": True,
                "side": "SELL",
                "score": score + 1,
                "reason": f"Downtrend 1H. Pullback: {is_pullback}, RSI: {rsi_15m:.2f}, Vol: {vol_ok}",
                "sl_price": max(klines_15m[-5:]), # SL di swing high terdekat
                "tp_price": price_now - (abs(price_now - max(klines_15m[-5:])) * 2.5) # RR 1:2.5
            }

    return {"allow": False, "reason": "Konfluensi tidak terpenuhi"}
