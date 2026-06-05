# ═══════════════════════════════════════════════════════════════════
# 📘 CRYPTO FUTURES TRADING — COMPLETE STRATEGY & REFERENCE GUIDE
# ═══════════════════════════════════════════════════════════════════
# Disusun oleh: OWL Hermes Agent
# Sumber: Buku, paper, riset akademis, praktisi trading, dokumentasi exchange
# Lisensi: Educational Use — Bukan financial advice
# ═══════════════════════════════════════════════════════════════════

---

## DAFTAR ISI

1. [Fondasi Trading Futures Kripto](#1-fondasi)
2. [Analisis Teknikal](#2-teknikal)
3. [Strategi Trading](#3-strategi)
4. [Risk Management & Money Management](#4-risk)
5. [Order Flow & Market Microstructure](#5-orderflow)
6. [On-Chain Metrics & Sentiment](#6-onchain)
7. [Psikologi Trading](#7-psikologi)
8. [Rumus & Kalkulasi Penting](#8-rumus)
9. [Checklist Trading Harian](#9-checklist)
10. [Glossary](#10-glossary)

---

## 1. FONDASI TRADING FUTURES KRIPTO {#1-fondasi}

### 1.1 Apa Itu Futures?

Futures adalah kontrak derivatif yang mewajiblikan pembeli untuk membeli,
dan penjual untuk menjual suatu aset pada harga dan tanggal yang telah
disepakati. Di kripto, futures bisa bersifat:

- **Perpetual Futures (Perp)**: Tidak ada expiry, menggunakan funding rate
  untuk meng-anchor harga ke spot
- **Quarterly/Expiry Futures**: Punya tanggal expiry (contoh: BTC-25MAR27)
- **Inverse Futures**: Di-quote dalam USD, di-settle dalam kripto (BTC)
- **Linear Futures**: Di-quote dan di-settle dalam USDT/USDC

### 1.2 Istilah Kunci

| Istilah | Penjelasan |
|---------|------------|
| **Notional Value** | Nilai kontrak = Quantity × Entry Price |
| **Margin** | Jaminan yang dibuka untuk membuka posisi |
| **Initial Margin** | Margin minimum untuk membuka posisi |
| **Maintenance Margin** | Margin minimum untuk mempertahankan posisi |
| **Liquidation** | Penutupan paksa posisi ketika margin < maintenance margin |
| **Funding Rate** | Pembayaran periodik antara long/short (tiap 1-8 jam) |
| **Open Interest (OI)** | Jumlah kontrak yang masih terbuka |
| **Basis** | Selisih Futures Price − Spot Price |
| **Premium** | Basis positif (contango) atau negatif (backwardation) |
| **Mark Price** | Harga referensi untuk menghindari manipulasi liquidation |
| **Index Price** | Harga rata-rata dari multiple exchange spot |
| **Leverage** | Pengali posisi (contoh: 10x = kontrol 10× modal) |
| **Isolated Margin** | Margin terbatas per posisi |
| **Cross Margin** | Semua margin di-share antar posisi |
| **TP/SL** | Take Profit / Stop Loss |
| **Breakeven** | Harga di mana posisi = 0 PnL |
| **Max Drawdown** | Penurunan terbesar dari puncak equity |

### 1.3 Cara Kerja Leverage

```
Contoh: Modal $100, Leverage 10x, Long BTC di $100,000

Posisi Value = $100 × 10 = $1,000 (0.01 BTC)

Jika BTC naik 5% → $105,000:
  Profit = 0.01 × ($105,000 - $100,000) = $50 (50% gain)

Jika BTC turun 5% → $95,000:
  Loss = 0.01 × ($100,000 - $95,000) = $50 (50% loss)

Jika BTC turun 10% → $90,000:
  Loss = $100 = LIQUIDATED (seluruh margin hilang)
```

**Pelajaran**: Leverage 10x = 10% lawan arah = liquidation.
Semakin tinggi leverage, semakin kecil ruang untuk "salah".

### 1.4 Funding Rate

Funding rate adalah mekanisme untuk menjaga harga futures tetap dekat
dengan harga spot. Dibayarkan setiap 8 jam (umumnya pukul 04:00, 12:00, 20:00 UTC).

```
Funding Rate = Premium Index × clamp(Interest Rate − Premium Index, 0.05%, −0.05%)

Dimana:
  Premium Index = (Mark Price − Index Price) / Index Price
  Interest Rate = (Quote Interest − Base Interest) / Funding Interval

Jika Funding Rate POSITIF → Long bayar Short (bullish sentiment)
Jika Funding Rate NEGATIF → Short bayar Long (bearish sentiment)
```

**Strategi Funding Rate Arbitrage**:
- Ketika funding rate sangat tinggi (>0.1%), pertimbangkan short
- Ketika funding rate sangat rendah (<-0.1%), pertimbangkan long
- Bisa juga hedge: long spot + short futures = "cash and carry"

### 1.5 Liquidation Mechanics

```
Liquidation Price (Long) ≈ Entry × (1 − 1/Leverage + Maintenance Margin Rate)
Liquidation Price (Short) ≈ Entry × (1 + 1/Leverage − Maintenance Margin Rate)

Contoh Binance BTCUSDT, 10x leverage, entry $100,000:
  Liq Price (Long) ≈ $100,000 × (1 − 0.10 + 0.005) = $90,500
  Liq Price (Short) ≈ $100,000 × (1 + 0.10 − 0.005) = $109,500
```

**Liquidation Cascade**: Ketika banyak posisi liquidated secara bersamaan,
harga bergerak cepat dan bisa memicu lebih banyak liquidation → "long/short squeeze".

---

## 2. ANALISIS TEKNIKAL {#2-teknikal}

### 2.1 Moving Averages

#### Simple Moving Average (SMA)
```
SMA(n) = (P₁ + P₂ + ... + Pₙ) / n

Umum digunakan: SMA 20, 50, 100, 200
```

#### Exponential Moving Average (EMA)
```
EMA(t) = Price(t) × k + EMA(t-1) × (1 − k)
k = 2 / (n + 1)

Umum digunakan: EMA 9, 12, 21, 26, 50, 100, 200
```

#### Moving Average Crossover Strategies
- **Golden Cross**: SMA 50 cross di atas SMA 200 → Bullish signal
- **Death Cross**: SMA 50 cross di bawah SMA 200 → Bearish signal
- **EMA 9/21 Crossover**: Untuk timeframe lebih pendek (scalping)

#### MA sebagai Dynamic Support/Resistance
- Dalam uptrend: EMA 21/50 sering menjadi support
- Dalam downtrend: EMA 21/50 sering menjadi resistance
- Price bouncing off EMA + volume naik = konfirmasi

### 2.2 Relative Strength Index (RSI)

```
RSI = 100 − 100/(1 + RS)
RS = Average Gain / Average Loss (over n periods, typically 14)

Interpretasi:
  RSI > 70 → Overbought (potensi jual)
  RSI < 30 → Oversold (potensi beli)
  RSI 40-60 → Netral / ranging

RSI Divergence:
  Bullish: Price lower low, RSI higher low → reversal up
  Bearish: Price higher high, RSI lower high → reversal down
```

**RSI untuk Futures**:
- Di timeframe tinggi (4H, Divergence lebih reliable)
- Jangan jual hanya karena RSI > 70 di trending market
- Gunakan RSI divergence sebagai konfirmasi, bukan sinyal utama

### 2.3 MACD (Moving Average Convergence Divergence)

```
MACD Line = EMA(12) − EMA(26)
Signal Line = EMA(9) of MACD Line
Histogram = MACD Line − Signal Line

Sinyal:
  MACD cross above Signal → Bullish
  MACD cross below Signal → Bearish
  Histogram expanding → Momentum increasing
  Histogram contracting → Momentum weakening
  MACD divergence → Potential reversal
```

### 2.4 Bollinger Bands

```
Middle Band = SMA(20)
Upper Band = SMA(20) + (2 × Standard Deviation)
Lower Band = SMA(20) − (2 × Standard Deviation)

Strategi:
  "Squeeze" (band menyempit) → Breakout segera terjadi
  Price touch upper band → Overbought (dalam range)
  Price touch lower band → Oversold (dalam range)
  "Walking the bands" → Trend kuat (price terus di upper/lower band)
```

**%B Indicator**:
```
%B = (Price − Lower Band) / (Upper Band − Lower Band)
  %B > 1 → Above upper band
  %B < 0 → Below lower band
  %B = 0.5 → At middle band
```

### 2.5 Volume Profile & VWAP

#### VWAP (Volume Weighted Average Price)
```
VWAP = Σ(Price × Volume) / Σ(Volume)

Digunakan sebagai "fair value" intraday.
  Price > VWAP → Bullish bias
  Price < VWAP → Bearish bias
  Price = VWAP → Netral

VWAP Bands (seperti Bollinger):
  Upper = VWAP + (k × StdDev)
  Lower = VWAP − (k × StdDev)
```

#### Volume Profile
- **Point of Control (POC)**: Harga dengan volume tertinggi
- **Value Area (VA)**: Range harga di mana ~70% volume terjadi
- **HVN (High Volume Node)**: Area volume tinggi = support/resistance
- **LVN (Low Volume Node)**: Area volume rendah = harga bergerak cepat

### 2.6 Fibonacci Retracement & Extension

```
Key Levels: 0.236, 0.382, 0.500, 0.618, 0.786

Retracement (dari swing high ke swing low):
  Level = Swing Low + (Swing High − Swing Low) × Fib Ratio

Extension (untuk target profit):
  Level = Swing High + (Swing High − Swing Low) × Ext Ratio
  Key Extensions: 1.272, 1.618, 2.000, 2.618

Golden Zone: 0.5 − 0.618 retracement = area entry ideal
```

### 2.7 Candlestick Patterns

#### Single Candle
| Pattern | Bentuk | Sinyal |
|---------|--------|--------|
| **Doji** | Body kecil, shadow panjang | Indecision |
| **Hammer** | Body atas, shadow bawah panjang | Bullish reversal |
| **Shooting Star** | Body bawah, shadow atas panjang | Bearish reversal |
| **Marubozu** | Full body, no shadow | Strong momentum |
| **Spinning Top** | Body kecil, shadow sama | Indecision |

#### Multi-Candle Patterns
| Pattern | Formasi | Sinyal |
|---------|---------|--------|
| **Engulfing** | Candle 2 "memakan" candle 1 | Reversal |
| **Morning Star** | 3 candle: bearish → doji → bullish | Bullish reversal |
| **Evening Star** | 3 candle: bullish → doji → bearish | Bearish reversal |
| **Three White Soldiers** | 3 candle bullish berturut | Strong bullish |
| **Three Black Crows** | 3 candle bearish berturut | Strong bearish |
| **Tweezer Bottom** | 2 candle dengan low sama | Bullish reversal |
| **Tweezer Top** | 2 candle dengan high sama | Bearish reversal |

### 2.8 Chart Patterns

#### Reversal Patterns
- **Head & Shoulders (H&S)**: 3 puncak, tengah tertinggi
  Target = Neckline − (Head − Neckline)
- **Inverse H&S**: Kebalikan, bullish reversal
- **Double Top**: 2 puncak di level sama, bearish
- **Double Bottom**: 2 dasar di level sama, bullish
- **Triple Top/Bottom**: 3 touch di level sama

#### Continuation Patterns
- **Flag/Pennant**: Konsolidasi setelah move kuat
- **Triangle**: Ascending, Descending, Symmetrical
- **Wedge**: Rising wedge (bearish), Falling wedge (bullish)
- **Rectangle/Box**: Range-bound, breakout direction = trend

### 2.9 Multi-Timeframe Analysis (MTFA)

```
Framework "Top-Down":
  1. Monthly/Weekly → Tentukan trend utama
  2. Daily → Cari struktur (support/resistance, pattern)
  3. 4H/1H → Cari entry trigger
  4. 15m/5m → Execute entry dengan presisi

Aturan:
  - Hanya trade searah trend timeframe lebih tinggi
  - Jika weekly bullish, cari long di daily/4H
  - Jika daily ranging, jangan force directional trade
  - Confluence antar timeframe = higher probability
```

### 2.10 Confluence Framework

```
Skor Confluence (1-5):
  +1: Support/Resistance major
  +1: Trendline / Channel
  +1: Fibonacci level (0.5, 0.618)
  +1: Moving Average (EMA 50, 200)
  +1: Volume Profile (POC, HVN)
  +1: RSI divergence
  +1: Candlestick pattern
  +1: Round number / Psychological level

Minimum untuk entry: Skor ≥ 4
Ideal: Skor ≥ 5
```

---

## 3. STRATEGI TRADING {#3-strategi}

### 3.1 Scalping (1m - 15m)

**Profil**: Banyak trade, kecil profit, cepat keluar.
**Win rate target**: >60%. **RR**: 1:1 hingga 1:1.5.

#### Scalping Strategy A: EMA + VWAP Pullback
```
Setup:
  Timeframe: 1m, 5m
  Indikator: EMA 9, EMA 21, VWAP

Long Entry:
  1. Price di atas VWAP (bullish bias)
  2. EMA 9 di atas EMA 21
  3. Price pullbacks ke EMA 21 atau VWAP
  4. Candle reversal (engulfing/hammer) di area
  5. SL di bawah swing low terdekat
  6. TP1: 1:1 RR, TP2: resistance terdekat

Short Entry:
  1. Price di bawah VWAP
  2. EMA 9 di bawah EMA 21
  3. Price pullbacks ke EMA 21 atau VWAP
  4. Candle reversal (engulfing/shooting star)
  5. SL di atas swing high terdekat
  6. TP1: 1:1 RR, TP2: support terdekat

Leverage: 3x-5x (jangan lebih untuk scalping)
```

#### Scalping Strategy B: Orderbook Imbalance
```
Setup:
  Timeframe: 1m
  Tools: Order book depth, trade flow

Long Entry:
  1. Large bid wall di level support (2-5x normal)
  2. Buy volume spike di trade feed
  3. Price bouncing off support dengan volume
  4. SL di bawah bid wall
  5. TP: resistance terdekat atau 0.3-0.5% move

Short Entry:
  1. Large ask wall di level resistance
  2. Sell volume spike
  3. Price rejected dari resistance
  4. SL di atas ask wall
  5. TP: support terdekat

Leverage: 2x-3x
Risk per trade: 0.25-0.5% equity
```

#### Scalping Strategy C: Funding Rate Scalp
```
Setup:
  Ketika funding rate extreme (>0.15% atau <-0.15%)

Long (ketika funding sangat negatif):
  1. Funding rate < -0.15%
  2. Price di support + RSI oversold
  3. Entry long, hold hingga funding berubah
  4. Profit dari price rebound + funding earned

Short (ketika funding sangat positif):
  1. Funding rate > 0.15%
  2. Price di resistance + RSI overbought
  3. Entry short, hold hingga funding berubah
  4. Profit dari price drop + funding earned

Leverage: 2x-5x
Risk: 0.5% per trade
```

### 3.2 Day Trading (15m - 4H)

**Profil**: 1-5 trade per hari, hold beberapa jam.
**Win rate target**: >50%. **RR**: 1:2 hingga 1:3.

#### Day Trading Strategy A: Breakout + Retest
```
Setup:
  Timeframe: 15m, 1H (entry), 4H (trend)
  Indikator: VWAP, EMA 20, Volume

Long Entry:
  1. 4H trend bullish (higher highs, higher lows)
  2. Price breakout dari consolidation/range
  3. Tunggu retest breakout level (support jadi resistance)
  4. Entry saat candle konfirmasi di retest
  5. Volume harus naik saat breakout
  6. SL di bawah retest low
  7. TP1: 1:2 RR, TP2: 1:3 RR atau next resistance

Short Entry:
  1. 4H trend bearish
  2. Price breakdown dari support
  3. Retest breakdown level
  4. Entry saat konfirmasi
  5. SL di atas retest high
  6. TP1: 1:2 RR, TP2: 1:3 RR

Leverage: 3x-10x
Risk per trade: 1-2% equity
```

#### Day Trading Strategy B: London/New York Open
```
Setup:
  Sesi: London Open (15:00-16:00 UTC), NY Open (13:30-14:30 UTC)

Long Entry:
  1. Identifikasi range Asia session (00:00-08:00 UTC)
  2. Tunggu London/NY open
  3. Breakout dari range Asia dengan volume
  4. Entry saat retest range boundary
  5. SL di dalam range
  6. TP: 1.5-2x range size

Short Entry:
  1. Sama, tapi breakdown dari range
  2. Entry saat retest

Leverage: 3x-5x
Risk: 1% equity
```

#### Day Trading Strategy C: RSI Divergence + S/R
```
Setup:
  Timeframe: 1H, 4H
  Indikator: RSI(14), Support/Resistance

Long Entry:
  1. Price membuat lower low di 1H/4H
  2. RSI membuat higher low (bullish divergence)
  3. Divergence terjadi di area support major
  4. Entry saat candle bullish confirmation
  5. SL di bawah divergence low
  6. TP: resistance terdekat atau 1:2 RR

Short Entry:
  1. Price higher high, RSI lower high
  2. Divergence di area resistance
  3. Entry saat candle bearish confirmation
  4. SL di atas divergence high
  5. TP: support terdekat

Leverage: 3x-7x
Risk: 1-1.5% equity
```

### 3.3 Swing Trading (4H - Daily)

**Profil**: 1-3 trade per minggu, hold 1-7 hari.
**Win rate target**: >40%. **RR**: 1:3 hingga 1:5.

#### Swing Strategy A: Trend Following + EMA
```
Setup:
  Timeframe: 4H, Daily
  Indikator: EMA 21, EMA 50, EMA 200, Volume

Long Entry:
  1. EMA 21 > EMA 50 > EMA 200 (stacking bullish)
  2. Price di atas EMA 200
  3. Pullback ke EMA 21 atau EMA 50
  4. Candle reversal di EMA (hammer, engulfing)
  5. Volume rendah saat pullback, naik saat reversal
  6. SL di bawah EMA 50 atau swing low
  7. TP1: previous high, TP2: 1.618 Fib extension
  8. Trailing stop: EMA 21 atau parabolic SAR

Short Entry:
  1. EMA 21 < EMA 50 < EMA 200
  2. Price di bawah EMA 200
  3. Pullback ke EMA 21/50
  4. Candle reversal bearish
  5. SL di atas EMA 50 atau swing high
  6. TP: previous low / Fib extension

Leverage: 2x-5x
Risk per trade: 1-2% equity
Position sizing: Adjust agar SL = 1-2% equity
```

#### Swing Strategy B: Wyckoff Method
```
4 Fase Wyckoff:
  1. Accumulation (AAR → AR → ST → SOS → LPS)
  2. Markup (uptrend)
  3. Distribution (AR → ST → SOS → LPSY → SC)
  4. Markdown (downtrend)

Entry Signals:
  "Spring" (Accumulation):
    - Price breakdown support lalu cepat kembali
    - Volume rendah saat breakdown, tinggi saat reversal
    - Entry long saat price kembali ke range
    - SL di bawah spring low

  "Upthrust" (Distribution):
    - Price breakout resistance lalu cepat kembali
    - Volume rendah saat breakout
    - Entry short saat price kembali ke range
    - SL di atas upthrust high

Leverage: 2x-3x
Risk: 1-2% equity
RR: 1:3 hingga 1:5
```

#### Swing Strategy C: Elliott Wave
```
Impulse Wave: 5 gelombang searah trend
  Wave 1: Awal reversal, sering "tidak terlihat"
  Wave 2: Koreksi Wave 1 (tidak boleh < start Wave 1)
  Wave 3: Paling kuat dan panjang (never the shortest)
  Wave 4: Koreksi Wave 3 (tidak overlap Wave 1)
  Wave 5: Exhaustion, sering dengan divergence

Corrective Wave: 3 gelombang (A-B-C)
  Zigzag: 5-3-5
  Flat: 3-3-5
  Triangle: 3-3-3-3-3

Fibonacci Relationships:
  Wave 2 = 50-78.6% retracement Wave 1
  Wave 3 = 1.618-2.618 extension Wave 1
  Wave 4 = 23.6-50% retracement Wave 3
  Wave 5 = Wave 1 atau 0.618 × Wave 1-3

Entry: Wave 3 atau Wave 5 (setara)
SL: End of Wave 1 (untuk Wave 3 entry)
TP: Fib extension targets
```

### 3.4 Position Trading (Weekly - Monthly)

**Profil**: 1-2 trade per bulan, hold minggu-bulan.
**Win rate target**: >35%. **RR**: 1:5 hingga 1:10+.

#### Position Strategy A: Macro Trend + On-Chain
```
Setup:
  Timeframe: Weekly, Monthly
  Indicators: On-chain metrics, macro indicators

Long Entry:
  1. Bitcoin halving cycle (12-18 month post-halving = bull)
  2. MVRV Z-Score < 0 (undervalued)
  3. NUPL < 0 (capitulation)
  4. Exchange outflow increasing
  5. Weekly RSI turning up from oversold
  6. Entry: DCA over 2-4 weeks
  7. SL: Below cycle low or -30% from avg entry
  8. TP: Cycle top indicators (MVRV > 7, NUPL > 0.75)

Short Entry:
  1. Late cycle (18+ month post-halving)
  2. MVRV Z-Score > 7 (overvalued)
  3. NUPL > 0.75 (euphoria)
  4. Exchange inflow increasing
  5. Weekly RSI divergence bearish
  6. Entry: Scale in over 2-4 weeks
  7. SL: Above cycle high
  8. TP: 50-70% drawdown target

Leverage: 1x-3x (position trading = low leverage)
Risk: 2-5% equity per position
```

#### Position Strategy B: Mean Reversion (Extreme Fear)
```
Setup:
  Ketika market extreme fear (Fear & Greed Index < 10)

Long Entry:
  1. Fear & Greed Index < 10
  2. Social media sentiment sangat negatif
  3. Funding rate sangat negatif
  4. Long liquidation cascade baru saja terjadi
  5. Price di support major (weekly/monthly)
  6. DCA entry over 1-2 weeks
  7. SL: Below recent liquidation low
  8. TP: Return to mean (Fear & Greed > 50)

Leverage: 1x-2x
Risk: 2-3% equity
```

### 3.5 Mean Reversion / Range Trading

```
Setup:
  Market ranging (tidak trending)
  Indikator: Bollinger Bands, RSI, Support/Resistance

Long Entry:
  1. Price di lower Bollinger Band ATAU support range
  2. RSI < 30 (oversold)
  3. Candlestick reversal pattern
  4. Entry: Market atau limit order di support
  5. SL: Di bawah support range (1-2%)
  6. TP: Middle band ATAU resistance range

Short Entry:
  1. Price di upper Bollinger Band ATAU resistance range
  2. RSI > 70 (overbought)
  3. Candlestick reversal pattern
  4. SL: Di atas resistance range
  5. TP: Middle band ATAU support range

Leverage: 2x-5x
Risk: 0.5-1% equity
RR: 1:1.5 hingga 1:2

WARNING: Jangan gunakan di trending market!
```

### 3.6 Momentum / Trend Following

```
Setup:
  Market trending kuat
  Indikator: ADX, EMA, Volume

Long Entry:
  1. ADX > 25 (trend kuat)
  2. EMA 21 > EMA 50 > EMA 200
  3. Price di atas semua MA
  4. Entry: Breakout dari consolidation ATAU pullback ke EMA
  5. Volume naik searah trend
  6. SL: Di bawah EMA 50 atau swing low
  7. TP: Trailing stop (chandelier exit ATR-based)

Short Entry:
  1. ADX > 25
  2. EMA 21 < EMA 50 < EMA 200
  3. Price di bawah semua MA
  4. Entry: Breakdown ATAU pullback ke EMA
  5. SL: Di atas EMA 50 atau swing high
  6. TP: Trailing stop

Leverage: 3x-7x
Risk: 1-2% equity
```

### 3.7 Arbitrage Strategies

#### Funding Rate Arbitrage
```
Setup: Long spot + Short futures (atau sebaliknya)

Ketika funding rate tinggi (>0.05% per 8 jam):
  1. Buy BTC spot
  2. Short BTC futures (same notional)
  3. Earn funding rate setiap 8 jam
  4. Delta neutral (tidak terkena directional risk)
  5. Profit = Funding Rate × Position Size × 3 (per hari)

Annualized return: 0.1% × 3 × 365 = 109.5% (jika funding 0.1%)
Realistic: 10-30% annually

Risk: Exchange risk, execution risk, funding rate bisa berubah
```

#### Cross-Exchange Arbitrage
```
Setup: Buy di exchange A, sell di exchange B

Ketika price gap > fees:
  1. Buy BTC di exchange A (harga lebih rendah)
  2. Sell BTC di exchange B (harga lebih tinggi)
  3. Profit = Price Difference − Transfer Fees − Trading Fees

Challenges:
  - Transfer time (blockchain confirmation)
  - Price bisa bergerak selama transfer
  - KYC/withdrawal limits
  - Need capital di kedua exchange

Profit margin: 0.1-1% per trade
```

#### Basis Trading (Calendar Spread)
```
Setup: Long futures near-term + Short futures far-term (atau sebaliknya)

Ketika basis sangat tinggi (contango):
  1. Short near-term futures
  2. Long far-term futures
  3. Profit saat basis menyempit

Ketika basis sangat rendah (backwardation):
  1. Long near-term futures
  2. Short far-term futures
  3. Profit saat basis melebar
```

### 3.8 Grid Trading

```
Setup:
  Range-bound market
  Bot otomatis place buy/sell orders di grid

Long Grid:
  1. Set range: Support — Resistance
  2. Set jumlah grid (contoh: 20 grids)
  3. Bot place buy orders di setiap level grid
  4. Bot place sell orders di setiap level grid
  5. Profit dari setiap buy-sell cycle

Profit per grid = (Upper − Lower) / NumGrids − Fees

Risk: 
  - Price breakout range = stuck di satu sisi
  - Perlu monitoring dan adjustment range
  - Best untuk sideways market

Leverage: 1x-3x
```

### 3.9 Dollar Cost Averaging (DCA) Futures

```
Setup:
  Entry bertahap untuk mengurangi risiko timing

Long DCA:
  1. Tentukan total position size
  2. Split menjadi 3-5 entry
  3. Entry 1: 20% di harga sekarang
  4. Entry 2: 20% jika price turun 2-3%
  5. Entry 3: 20% jika price turun 5%
  6. Entry 4: 20% jika price turun 8%
  7. Entry 5: 20% jika price turun 12%
  8. SL: Rata-rata entry − 15%
  9. TP: Scale out di resistance

Keuntungan:
  - Average entry lebih baik
  - Tidak perlu timing sempurna
  - Emosi lebih terkontrol

Leverage: 1x-3x
Risk: 2-3% equity total
```

---

## 4. RISK MANAGEMENT & MONEY MANAGEMENT {#4-risk}

### 4.1 Golden Rules

```
1. NEVER risk more than 1-2% of equity per trade
2. ALWAYS use stop loss
3. NEVER average down on a losing trade (unless planned DCA)
4. NEVER trade with money you can't afford to lose
5. ALWAYS have a plan before entering a trade
6. NEVER chase a trade (FOMO)
7. NEVER revenge trade after a loss
8. ALWAYS take profits — money not taken is not profit
9. NEVER use maximum leverage
10. KEEP a trading journal
```

### 4.2 Position Sizing

#### Fixed Fractional (1% Rule)
```
Position Size = (Equity × Risk%) / (Entry − Stop Loss)

Contoh:
  Equity: $10,000
  Risk: 1% = $100
  Entry: $100,000
  SL: $98,000 (2% risk)
  
  Position Size = $100 / ($100,000 − $98,000) = 0.05 BTC
  Notional Value = 0.05 × $100,000 = $5,000
  Effective Leverage = $5,000 / $10,000 = 0.5x
```

#### Kelly Criterion
```
Kelly % = W − [(1 − W) / R]

Dimana:
  W = Win rate (decimal, contoh 0.55 untuk 55%)
  R = Average Win / Average Loss (Reward-Risk Ratio)

Contoh:
  W = 55% (0.55)
  R = 2 (avg win 2× avg loss)
  
  Kelly % = 0.55 − (0.45 / 2) = 0.55 − 0.225 = 0.325 = 32.5%

Half-Kelly (lebih konservatif) = 16.25%

Position Size = Equity × Kelly % / (Entry − SL)
```

#### Optimal f (Ralph Vince)
```
Optimal f = [(W × R) − L] / R

Dimana:
  W = Win rate
  R = Average Win / Average Loss
  L = Loss rate (1 − W)

Contoh:
  W = 0.50, R = 2.5, L = 0.50
  f = (0.50 × 2.5 − 0.50) / 2.5 = 0.75 / 2.5 = 0.30 = 30%
```

### 4.3 Risk-Reward Ratio (RR)

```
Minimum RR berdasarkan Win Rate:

  Win Rate 50% → Min RR 1:2 (break even)
  Win Rate 40% → Min RR 1:2.5
  Win Rate 33% → Min RR 1:3
  Win Rate 60% → Min RR 1:1.5
  Win Rate 25% → Min RR 1:4

Expected Value (EV):
  EV = (Win Rate × Avg Win) − (Loss Rate × Avg Loss)

  Contoh: WR 50%, Avg Win $200, Avg Loss $100
  EV = (0.5 × 200) − (0.5 × 100) = $50 per trade (positive EV)
```

### 4.4 Maximum Drawdown & Recovery

```
Drawdown Recovery Math:
  -10% loss → need +11.1% to recover
  -20% loss → need +25% to recover
  -30% loss → need +42.9% to recover
  -50% loss → need +100% to recover
  -70% loss → need +333% to recover
  -90% loss → need +1000% to recover

Max Drawdown Limits:
  Conservative: Max 10% drawdown → reduce size 50%
  Moderate: Max 20% drawdown → reduce size 50%
  Aggressive: Max 30% drawdown → reduce size 50%

Rule: After 3 consecutive losses → reduce position size 50%
      After 5 consecutive losses → stop trading for the day
```

### 4.5 Leverage Management

```
Recommended Leverage by Strategy:
  Scalping: 3x-5x
  Day Trading: 3x-10x
  Swing Trading: 2x-5x
  Position Trading: 1x-3x

Safe Leverage Formula:
  Max Leverage = 1 / (Stop Loss % + Buffer %)
  
  Contoh: SL 3%, Buffer 2%
  Max Leverage = 1 / (0.03 + 0.02) = 20x
  
  Tapi untuk safety, gunakan 50% dari max = 10x

Effective Leverage vs Nominal Leverage:
  Nominal: Leverage yang dipilih di exchange
  Effective: Notional Value / Equity
  
  Contoh: $1000 equity, $3000 position = 3x effective
  (meskipun exchange allow 100x)
```

### 4.6 Stop Loss Strategies

#### Fixed Percentage SL
```
SL = Entry × (1 − SL%) untuk long
SL = Entry × (1 + SL%) untuk short

Typical: 1-3% untuk day trading, 3-5% untuk swing
```

#### ATR-Based SL
```
ATR(14) = Average True Range over 14 periods

SL (Long) = Entry − (ATR × Multiplier)
SL (Short) = Entry + (ATR × Multiplier)

Multiplier: 1.5-2.5 untuk day trading, 2-3 untuk swing
```

#### Structure-Based SL
```
Long: SL di bawah swing low terdekat atau support
Short: SL di atas swing high terdekat atau resistance

Buffer: Tambah 0.5-1% buffer dari level struktur
```

#### Trailing Stop
```
Chandelier Exit (Long):
  Highest High(22) − ATR(22) × 3
  
  Ketika price turun di bawah ini → exit

Parabolic SAR:
  AF mulai 0.02, increment 0.02, max 0.20
  
  Ketika SAR berpindah ke atas price → exit long

EMA Trailing:
  Exit ketika price close di bawah EMA 21 (swing)
  Exit ketika price close di bawah EMA 9 (scalp)
```

### 4.7 Take Profit Strategies

#### Scale Out
```
50% di TP1 (1:1.5 RR)
30% di TP2 (1:2.5 RR)
20% di TP3 (1:4 RR atau runner)

Atau:
33% di TP1, 33% di TP2, 34% di TP3
```

#### Partial Profit + Breakeven
```
1. Entry dengan 100% size
2. TP1 (1:1 RR): Close 50%, pindahkan SL ke breakeven
3. TP2 (1:2 RR): Close 30%
4. TP3 (1:3+ RR): Close 20% atau trailing stop

Keuntungan: Setelah TP1, sisa posisi "free"
```

### 4.8 Portfolio Risk

```
Max Portfolio Risk:
  1 position: 1-2% risk
  2-3 positions: 3-5% total risk
  4+ positions: max 6-8% total risk

Correlation Risk:
  - Juga trade BTC + ETH + SOL = highly correlated
  - Effective risk bisa 2-3× individual risk
  - Diversify atau reduce size

Daily Loss Limit:
  - Max 3% loss per day
  - After hitting limit → stop trading for the day
  
Weekly Loss Limit:
  - Max 5-7% loss per week
  - After hitting limit → stop trading for the week

Monthly Loss Limit:
  - Max 10-15% loss per month
  - After hitting limit → review strategy, take break
```

---

## 5. ORDER FLOW & MARKET MICROSTRUCTURE {#5-orderflow}

### 5.1 Order Book Analysis

```
Bid-Ask Spread:
  Spread = Best Ask − Best Bid
  Spread % = Spread / Mid Price × 100
  
  Tight spread (<0.01%) = liquid, efficient
  Wide spread (>0.05%) = illiquid, cautious

Order Book Imbalance:
  Imbalance = (Bid Volume − Ask Volume) / (Bid Volume + Ask Volume)
  
  Imbalance > 0.3 → Bullish pressure
  Imbalance < −0.3 → Bearish pressure

Large Walls:
  Bid wall: Large buy orders di level tertentu → support
  Ask wall: Large sell orders di level tertentu → resistance
  
  WARNING: Walls bisa "spoofed" (dipasang lalu dicancel)
```

### 5.2 Volume Analysis

```
Volume Profile:
  - POC (Point of Control): Highest volume node
  - Value Area: 70% of volume
  - HVN: High Volume Node = support/resistance
  - LVN: Low Volume Node = fast price movement

Volume Divergence:
  Price up + Volume down → Weak rally, potential reversal
  Price down + Volume down → Weak dump, potential reversal
  Price up + Volume up → Strong rally, continuation
  Price down + Volume up → Strong dump, continuation

Volume Spike:
  2-3× average volume = significant event
  Could be: liquidation cascade, news, whale activity
```

### 5.3 Liquidation Heatmaps

```
Liquidation Clusters:
  - Area di mana banyak posisi akan liquidated
  - Hanya "magnet" untuk harga
  - Setelah liquidation cascade → reversal likely

Long Liquidation Zone:
  Di bawah support → banyak long SL
  Price bisa "sweep" zone lalu reverse

Short Liquidation Zone:
  Di atas resistance → banyak short SL
  Price bisa "squeeze" lalu reverse

Tools: Coinglass, Hyblock, Datamish
```

### 5.4 Open Interest (OI) Analysis

```
OI Rising + Price Rising → Strong bullish (new longs entering)
OI Rising + Price Falling → Strong bearish (new shorts entering)
OI Falling + Price Rising → Short covering (bearish reversal)
OI Falling + Price Falling → Long liquidation (capitulation)

OI Change > 10% in 24h = Significant event
OI All-Time High = Extreme positioning (risk of squeeze)

OI-Price Divergence:
  Price up + OI down = Bearish divergence (short covering rally)
  Price down + OI down = Bullish divergence (longs being flushed)
```

### 5.5 CVD (Cumulative Volume Delta)

```
CVD = Cumulative(Buy Volume − Sell Volume)

CVD Rising → More aggressive buyers
CVD Falling → More aggressive sellers

CVD Divergence:
  Price up + CVD flat/falling → Weak rally (sellers absorbing)
  Price down + CVD flat/rising → Weak dump (buyers absorbing)

CVD Reset: Reset di awal sesi (Asia, London, NY)
```

### 5.6 Funding Rate Analysis

```
Extreme Funding:
  > 0.1% per 8h = Very bullish (longs paying shorts)
  < −0.1% per 8h = Very bearish (shorts paying longs)

Funding + OI:
  High funding + Rising OI = Crowded long → squeeze risk
  Low funding + Rising OI = Crowded short → squeeze risk

Funding Reversal:
  Funding berubah arah = Sentiment shift
  Often precedes price reversal
```

---

## 6. ON-CHAIN METRICS & SENTIMENT {#6-onchain}

### 6.1 Key On-Chain Metrics

#### MVRV (Market Value to Realized Value)
```
MVRV = Market Cap / Realized Cap

  MVRV < 1 = Undervalued (below cost basis) → Accumulation zone
  MVRV 1-2 = Fair value
  MVRV > 3.7 = Overvalued → Distribution zone
  MVRV > 7 = Extreme euphoria → Cycle top

MVRV Z-Score:
  Z = (Market Cap − Realized Cap) / StdDev(Market Cap)
  
  Z < 0 = Undervalued
  Z > 7 = Overvalued
```

#### NUPL (Net Unrealized Profit/Loss)
```
NUPL = (Market Cap − Realized Cap) / Market Cap

  NUPL < 0 = Capitulation → Buy zone
  NUPL 0-0.25 = Fear → Accumulation
  NUPL 0.25-0.5 = Belief → Hold
  NUPL 0.5-0.75 = Euphoria → Caution
  NUPL > 0.75 = Greed → Distribution
```

#### SOPR (Spent Output Profit Ratio)
```
SOPR = Value of spent outputs / Value of created outputs

  SOPR > 1 = Profitable selling
  SOPR < 1 = Loss selling
  SOPR = 1 = Breakeven

SOPR < 1 for extended period = Capitulation → Reversal likely
SOPR > 1.02 for extended period = Profit taking → Distribution
```

#### Exchange Flows
```
Exchange Inflow ↑ = Selling pressure → Bearish
Exchange Outflow ↑ = Holding/accumulation → Bullish
Netflow = Inflow − Outflow

Large inflow spike = Whale preparing to sell
Sustained outflow = Strong accumulation
```

#### Active Addresses
```
Active Addresses ↑ = Growing adoption → Bullish
Active Addresses ↓ = Declining interest → Bearish

NVT Ratio (Network Value to Transactions):
  NVT = Market Cap / Daily Transaction Volume
  
  NVT > 95 = Overvalued (high cap, low usage)
  NVT < 40 = Undervalued
```

#### Hash Rate & Miner Activity
```
Hash Rate ↑ = Network security ↑ → Bullish long-term
Hash Rate ↓ = Miners leaving → Bearish

Miner Capitulation:
  Hash rate drops + miners selling = Bottom signal
  Often coincides with price bottom

Hash Ribbons:
  30-day MA hash rate crosses below 200-day = Miner capitulation
  After hash ribbon buy signal → Strong returns historically
```

### 6.2 Sentiment Indicators

#### Fear & Greed Index
```
Components: Volatility, Volume, Social Media, Surveys, Dominance, Trends

  0-25 = Extreme Fear → Potential buy
  26-45 = Fear → Cautious buy
  46-55 = Neutral
  56-75 = Greed → Cautious sell
  76-100 = Extreme Greed → Potential sell

Contrarian indicator:
  Extreme fear often = bottom
  Extreme greed often = top
```

#### Social Media Sentiment
```
Twitter/X Crypto Sentiment:
  High positive sentiment = Crowded long → Risk
  High negative sentiment = Capitulation → Opportunity

Google Trends:
  "Bitcoin" search volume ↑ = Retail interest ↑
  Often correlates with price tops

Reddit Activity:
  r/CryptoCurrency, r/Bitcoin activity spikes = Retail FOMO
```

#### Stablecoin Metrics
```
Stablecoin Supply ↑ = Dry powder ready to deploy → Bullish
Stablecoin Supply ↓ = Capital leaving → Bearish

Stablecoin Exchange Inflow:
  High = Ready to buy → Bullish
  Low = No buying pressure

USDT Market Cap:
  Growing USDT = New money entering crypto
  Often leads price by 1-2 weeks
```

### 6.3 Macro Factors

```
DXY (Dollar Index):
  DXY ↑ = Strong dollar → Bearish for crypto
  DXY ↓ = Weak dollar → Bullish for crypto
  Inverse correlation with BTC

S&P 500 / NASDAQ:
  Crypto correlates with tech stocks
  Risk-on = Both up, Risk-off = Both down

Fed Interest Rates:
  Rate cuts = Liquidity ↑ → Bullish for crypto
  Rate hikes = Liquidity ↓ → Bearish for crypto

Global M2 Money Supply:
  M2 ↑ = More liquidity → Bullish for crypto
  Leads BTC price by ~10-12 weeks
```

---

## 7. PSIKOLOGI TRADING {#7-psikologi}

### 7.1 Cognitive Biases

```
Confirmation Bias:
  - Hanya mencari info yang mendukung opini
  - Solusi: Cari counter-argument, dengar bearish view saat bullish

Loss Aversion:
  - Rasa sakit 2× loss > senang 2× gain
  - Solusi: Gunakan SL otomatis, jangan override

Recency Bias:
  - Terlalu weight recent events
  - Solusi: Lihat data jangka panjang, jangan overreact

Anchoring Bias:
  - Terlalu fokus di harga entry
  - Solusi: Evaluate berdasarkan current price, bukan entry

Gambler's Fallacy:
  - "Sudah 5× loss, pasti menang"
  - Solusi: Setiap trade independent, stick to plan

Hot Hand Fallacy:
  - "Lagi hoki, tambah size"
  - Solusi: Stick to position sizing rules

Sunk Cost Fallacy:
  - "Sudah loss $500, harus tunggu"
  - Solusi: Cut loss sesuai plan, jangan tambah
```

### 7.2 Emotional Management

```
Pre-Trade:
  - Review checklist
  - Confirm setup meets ALL criteria
  - Set SL and TP BEFORE entry
  - Accept the risk mentally

During Trade:
  - DO NOT move SL further away
  - DO NOT close early (unless planned)
  - DO NOT add to losing position
  - Trust your analysis

After Trade:
  - Journal the trade (entry, exit, emotions, lessons)
  - Win or lose → review process, not just outcome
  - Take a break after 3 consecutive losses
  - Take a break after big win (overconfidence)
```

### 7.3 Trading Journal Template

```
Date: ___________
Symbol: ___________
Direction: Long / Short
Timeframe: ___________

Setup:
  Strategy: ___________
  Confluence Score: ___/7
  Entry Reason: ___________

Execution:
  Entry Price: ___________
  Stop Loss: ___________
  Take Profit: ___________
  Position Size: ___________
  Leverage: ___________
  Risk: ___% of equity

Outcome:
  Exit Price: ___________
  P&L: ___________
  R-Multiple: ___________
  Duration: ___________

Review:
  Followed Plan? Y/N
  What went well: ___________
  What to improve: ___________
  Emotion (1-10): ___________
  Screenshot: [attached]
```

### 7.4 Common Mistakes

```
1. Overtrading
   - Trading tanpa setup yang jelas
   - Solusi: Max 3-5 trades per day

2. Overleveraging
   - Menggunakan leverage terlalu tinggi
   - Solusi: Max 5x untuk day trading, 3x untuk swing

3. No Stop Loss
   - "Nanti juga balik"
   - Solusi: ALWAYS set SL before entry

4. Moving Stop Loss
   - Memperluas SL saat loss
   - Solusi: Set SL dan JANGAN sentuh

5. Revenge Trading
   - Trading emosional setelah loss
   - Solusi: Stop trading setelah 3 loss berturut

6. FOMO (Fear of Missing Out)
   - Entry tanpa setup karena takut ketinggalan
   - Solusi: Tunggu setup berikutnya, selalu ada opportunity

7. Averaging Down
   - Menambah posisi yang loss
   - Solusi: Hanya average jika planned (DCA strategy)

8. Ignoring Fees
   - Tidak menghitung trading fees + funding
   - Solusi: Include fees dalam perhitungan RR

9. Trading Against Trend
   - Melawan trend utama
   - Solusi: "The trend is your friend"

10. Not Taking Profits
    - Greedy, tidak ambil profit
    - Solusi: Scale out sesuai plan
```

---

## 8. RUMUS & KALKULASI PENTING {#8-rumus}

### 8.1 Position Sizing

```
# Fixed Fractional
Position Size = (Equity × Risk%) / |Entry − SL|

# Kelly Criterion
Kelly% = W − [(1 − W) / R]
Half-Kelly = Kelly% / 2

# Optimal f
f = [(W × R) − L] / R

# Leverage Calculation
Effective Leverage = Notional Value / Equity
Nominal Leverage = 1 / Margin%

# Liquidation Price (Isolated, Long)
Liq Price = Entry × (1 − 1/Leverage + MM%)

# Liquidation Price (Isolated, Short)
Liq Price = Entry × (1 + 1/Leverage − MM%)
```

### 8.2 Profit/Loss

```
# PnL (Long)
PnL = (Exit − Entry) × Quantity

# PnL (Short)
PnL = (Entry − Exit) × Quantity

# PnL with Leverage
PnL = (Exit − Entry) × Quantity × Leverage

# ROI%
ROI% = (PnL / Margin) × 100

# Breakeven with Fees
Breakeven (Long) = Entry × (1 + Fee% × 2)
Breakeven (Short) = Entry × (1 − Fee% × 2)

# Funding Cost
Funding Cost = Position Size × Funding Rate × Num Periods
(3 periods per day for 8h funding)
```

### 8.3 Risk Metrics

```
# Risk-Reward Ratio
RR = |TP − Entry| / |Entry − SL|

# Expected Value
EV = (Win% × Avg Win) − (Loss% × Avg Loss)

# Sharpe Ratio
Sharpe = (Return − Risk Free Rate) / StdDev(Returns)

# Sortino Ratio
Sortino = (Return − Risk Free Rate) / Downside Deviation

# Max Drawdown
Max DD = (Trough − Peak) / Peak × 100%

# Recovery Factor
Recovery = Net Profit / Max Drawdown

# Profit Factor
Profit Factor = Gross Profit / Gross Loss
(Target: > 1.5)
```

### 8.4 Technical Indicators

```
# RSI
RSI = 100 − 100/(1 + RS)
RS = Avg Gain(14) / Avg Loss(14)

# MACD
MACD = EMA(12) − EMA(26)
Signal = EMA(9) of MACD
Histogram = MACD − Signal

# Bollinger Bands
Middle = SMA(20)
Upper = SMA(20) + 2 × σ(20)
Lower = SMA(20) − 2 × σ(20)

# ATR (Average True Range)
TR = max(High−Low, |High−PrevClose|, |Low−PrevClose|)
ATR = SMA(TR, 14) atau EMA(TR, 14)

# VWAP
VWAP = Σ(Price × Volume) / Σ(Volume)

# ADX (Average Directional Index)
+DM = Current High − Previous High (if positive)
−DM = Previous Low − Current Low (if positive)
+DI = 100 × Smoothed +DM / ATR
−DI = 100 × Smoothed −DM / ATR
DX = 100 × |+DI − −DI| / (+DI + −DI)
ADX = Smoothed DX

# Fibonacci
Retracement = Swing Low + (Swing High − Swing Low) × Ratio
Extension = Swing High + (Swing High − Swing Low) × Ratio
Key Ratios: 0.236, 0.382, 0.500, 0.618, 0.786
Key Extensions: 1.272, 1.618, 2.000, 2.618
```

### 8.5 Compounding

```
# Compound Growth
Final = Initial × (1 + r)^n

Dimana:
  r = return per trade (decimal)
  n = number of trades

# Contoh:
  $10,000, 2% per trade, 100 trades
  Final = $10,000 × (1.02)^100 = $72,446

# Rule of 72
  Years to double = 72 / Annual Return%
  Contoh: 10% return → 7.2 years to double

# Drawdown Impact
  After 50% loss → need 100% gain to recover
  After 30% loss → need 42.9% gain to recover
```

---

## 9. CHECKLIST TRADING HARIAN {#9-checklist}

### Pre-Market (Sebelum Trading)
```
□ Cek Fear & Greed Index
□ Cek Funding Rate (extreme?)
□ Cek Open Interest (rising/falling?)
□ Cek Liquidation Heatmap
□ Cek macro news (Fed, CPI, NFP, dll)
□ Cek BTC dominance trend
□ Identifikasi key S/R levels di Daily/4H
□ Tentukan bias: Bullish / Bearish / Neutral
□ Max risk untuk hari ini: ___% equity
□ Max trades untuk hari ini: ___
```

### Sebelum Entry
```
□ Setup memenuhi kriteria strategi? (Y/N)
□ Confluence score ≥ 4? (Y/N)
□ Searah trend timeframe lebih tinggi? (Y/N)
□ RR minimal 1:2? (Y/N)
□ SL sudah ditentukan? (Y/N)
□ TP sudah ditentukan? (Y/N)
□ Position size sudah dihitung? (Y/N)
□ Risk ≤ 2% equity? (Y/N)
□ Tidak sedang emosional? (Y/N)
□ Tidak FOMO? (Y/N)
□ Jika semua Y → EXECUTE
```

### Setelah Entry
```
□ SL sudah dipasang? (Y/N)
□ TP sudah dipasang? (Y/N)
□ Tidak override SL? (COMMIT)
□ Tidak tambah posisi loss? (COMMIT)
□ Monitor, tapi jangan over-monitor
```

### End of Day
```
□ Journal semua trades hari ini
□ Hitung P&L harian
□ Review: Apakah follow plan?
□ Jika loss → Apa lesson learned?
□ Jika win → Apa yang bisa diulang?
□ Total risk hari ini: ___% (within limit?)
□ Siap untuk besok? (Y/N)
```

### Weekly Review (Minggu Malam)
```
□ Total P&L minggu ini: ___
□ Win rate minggu ini: ___%
□ Profit factor: ___
□ Max drawdown minggu ini: ___%
□ Best trade: ___________
□ Worst trade: ___________
□ Most common mistake: ___________
□ Improvement for next week: ___________
□ Total risk within weekly limit? (Y/N)
```

---

## 10. GLOSSARY {#10-glossary}

| Term | Definition |
|------|-----------|
| **ATH** | All-Time High |
| **ATL** | All-Time Low |
| **Altcoin** | Any cryptocurrency other than Bitcoin |
| **Bag Holder** | Someone holding a coin that has lost significant value |
| **Bearish** | Expecting price to go down |
| **Bullish** | Expecting price to go up |
| **CEX** | Centralized Exchange (Binance, Bybit, OKX) |
| **DEX** | Decentralized Exchange (dYdX, GMX, Hyperliquid) |
| **DeFi** | Decentralized Finance |
| **DCA** | Dollar Cost Averaging |
| **DYOR** | Do Your Own Research |
| **FOMO** | Fear Of Missing Out |
| **FUD** | Fear, Uncertainty, Doubt |
| **HODL** | Hold On for Dear Life (long-term holding) |
| **KYC** | Know Your Customer |
| **LFG** | Let's F***ing Go |
| **Liquidation** | Forced closure of a leveraged position |
| **Long** | Betting on price going up |
| **Market Cap** | Total value of all circulating coins |
| **Moon** | Price going up significantly |
| **NFA** | Not Financial Advice |
| **NGMI** | Not Gonna Make It |
| **OI** | Open Interest |
| **P&D** | Pump and Dump |
| **Rekt** | Wrecked (lost a lot of money) |
| **ROI** | Return on Investment |
| **RR** | Risk-Reward Ratio |
| **Rug Pull** | Scam where developers abandon project |
| **Short** | Betting on price going down |
| **Spot** | Buying/selling actual cryptocurrency |
| **Stablecoin** | Token pegged to fiat (USDT, USDC, DAI) |
| **TP** | Take Profit |
| **TVL** | Total Value Locked |
| **Volatility** | How much price fluctuates |
| **WAGMI** | We're All Gonna Make It |
| **Whale** | Large holder of cryptocurrency |
| **YOLO** | You Only Live Once (risky trade) |

---

## PENUTUP

> **"The goal of a successful trader is to make the best trades.
> Money is secondary."** — Alexander Elder

> **"It's not whether you're right or wrong that's important,
> but how much money you make when you're right."** — George Soros

> **"Risk comes from not knowing what you're doing."** — Warren Buffett

### Prinsip Utama:
1. **Capital preservation first** — Jangan pernah kehilangan seluruh modal
2. **Consistency over home runs** — Profit kecil konsisten > kadang besar
3. **Process over outcome** — Good process = good results long-term
4. **Adapt or die** — Market berubah, strategi harus adapt
5. **Never stop learning** — Market selalu mengajarkan hal baru

### Disclaimer:
**Bukan financial advice.** Trading futures kripto memiliki risiko tinggi.
Anda bisa kehilangan seluruh modal. Hanya gunakan uang yang mampu Anda
hilangkan. Lakukan riset sendiri (DYOR) dan pertimbangkan konsultasi
dengan penasihat keuangan berlisensi.

---

*File ini dikompilasi dari berbagai sumber termasuk:*
- *Trading books (Alexander Elder, Mark Douglas, Van Tharp)*
- *Academic papers on risk management & position sizing*
- *Exchange documentation (Binance, Bybit, OKX)*
- *On-chain analytics (Glassnode, CryptoQuant, CoinMetrics)*
- *Market microstructure research*
- *Practitioner knowledge & best practices*

*Last updated: 2026-05-29*
*OWL Hermes Agent — Educational Reference*
