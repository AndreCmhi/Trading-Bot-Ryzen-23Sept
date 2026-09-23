# TRADING BOT EVALUATION REPORT
# Updated: 2026-08-12 — Upgrade Anti-Negative PNL

## PREVIOUS PERFORMANCE (Pre-Upgrade)

### Critical Issues Found:
1. **Win Rate: 22.86%** — Far below target (>55%)
2. **Total PnL: -8.10 USDT** — Negative returns
3. **Profit Factor: 0.19** — Extremely poor (target: >1.5)
4. **Average Loss: -0.1561** — Losses 2.6x larger than wins (0.0591)

## ROOT CAUSES IDENTIFIED

### Entry Quality
- `min_adx` default was **0.8** (effectively disabled!) — fixed to **20.0**
- `min_volume_ratio` default **0.5** (too lax) — fixed to **1.2**
- RSI BUY gate **42-66** too wide — tightened to **45-65**
- No candle rejection filter — shooting stars / doji allowed entries
- `ai_min_confidence` across profiles too low (0.58-0.66) — raised to 0.62-0.80

### Risk Management
- `HARD_STOP_ROI_PERCENT = -4.0%` — let losses run too long, changed to **-2.5%**
- `BREAKEVEN_TRIGGER_ROI_PERCENT = 6.0%` — winners reverted to loss before trigger, changed to **2.5%**
- `PARTIAL_TP_ROI_PERCENT = 10.0%` — almost never triggered, changed to **4.0%**
- `RISK_GUARD_ENABLED = false` by default — guard never ran, changed to **true**
- No drawdown protection — added equity-based drawdown levels (10%/15%/20%)
- No fee cost check — trade could be unprofitable after fees, added `is_trade_worth_after_fees()`

### Exposure / Position Sizing
- `MAX_OPEN_POSITIONS = 30` — overexposure, changed to **5**
- `MAX_CONSECUTIVE_LOSSES = 5` — too lenient, changed to **3**
- `MAX_TRADES_PER_HOUR = 15` — overtrading, changed to **6**
- `MAX_DAILY_LOSS_USDT = 100` — too large for small accounts, changed to **20**
- `DEFAULT_RISK_PER_TRADE_PERCENT = 1.0%` — changed to **0.75%**
- `HARD_STOP_SYMBOL_COOLDOWN = 45 min` — too short, changed to **120 min**

### MACD Bug
- Signal line was `macd_line * 0.8` (incorrect) — fixed to proper EMA-of-MACD
- Stochastic %D was `k * 0.9` (incorrect) — fixed to proper SMA(k, period)

## UPGRADES APPLIED (2026-08-12)

### 1. advanced_indicators.py
- Fixed `calculate_macd()`: proper EMA-of-MACD signal line
- Fixed `calculate_stochastic()`: proper SMA smoothing for %D

### 2. ai_decision.py
- Tightened RSI gate: BUY 45-65, SELL 35-57
- Min RRR floor: 2.0 (was 1.5 bypass possible)
- AI prompt leverage cap: 5x (was 10x in prompt)

### 3. risk_guard.py
- Added equity drawdown protection:
  - >=10%: size -50%, leverage cap 3
  - >=15%: size -75%, leverage cap 2
  - >=20%: HARD STOP all new entries

### 4. constants.py
- HARD_STOP_ROI_PERCENT: -4.0 -> **-2.5**
- BREAKEVEN_TRIGGER_ROI_PERCENT: 6.0 -> **2.5**
- PARTIAL_TP_ROI_PERCENT: 10.0 -> **4.0**
- MAX_OPEN_POSITIONS: 30 -> **5**
- MAX_DAILY_LOSS_USDT: 100 -> **20**
- MAX_CONSECUTIVE_LOSSES: 5 -> **3**
- MAX_TRADES_PER_HOUR: 15 -> **6**
- HOURLY_LOSS_LIMIT_USDT: 0.5 -> **2.0**
- SYMBOL_LOSS_COOLDOWN_MINUTES: 180 -> **240**
- HARD_STOP_SYMBOL_COOLDOWN_MINUTES: 45 -> **120**
- RISK_GUARD_ENABLED: false -> **true**
- AI_MIN_CONFIDENCE: 0.55 -> **0.62**
- DEFAULT_RISK_PER_TRADE_PERCENT: 1.0 -> **0.75**
- Strategy profile min_score: 10 -> **12**
- Strategy profile ai_min_confidence raised across all profiles

### 5. app.py
- min_adx default: 0.8 -> **20.0** (bug fix)
- min_volume_ratio: 0.5 -> **1.2**
- min_edge_quality_score: 0.72 -> **0.75**
- RISK_GUARD_ENABLED: true by default
- Fee-aware RRR check in build_order_plan
- Candle rejection filter (doji/shooting star) pre-entry
- Hard stop cap: -3.0 -> **-2.5** in safety profile

### 6. enhanced_risk.py
- Added `minimum_rrr_after_fees()` — calculates effective RRR accounting for taker fees
- Added `is_trade_worth_after_fees()` — gate: reject trades not profitable after fees

## EXPECTED IMPROVEMENT

| Metric | Before | Target |
|--------|--------|--------|
| Win Rate | 22.86% | >55% |
| Profit Factor | 0.19 | >1.5 |
| Max Single Loss ROI | -4.0% | -2.5% |
| Consecutive Loss Limit | 5 | 3 |
| Max Open Positions | 30 | 5 |
| ADX Threshold | 0.8 (bug) | 20.0 |

## RECOMMENDED .env OVERRIDES

```
RISK_GUARD_ENABLED=true
HARD_STOP_ROI_PERCENT=-2.5
BREAKEVEN_TRIGGER_ROI_PERCENT=2.5
PARTIAL_TP_ROI_PERCENT=4.0
MAX_OPEN_POSITIONS=5
MAX_DAILY_LOSS_USDT=20
MAX_CONSECUTIVE_LOSSES=3
AI_MIN_CONFIDENCE=0.62
DEFAULT_RISK_PER_TRADE_PERCENT=0.75
MAX_RISK_PER_TRADE_PERCENT=1.5
HARD_STOP_SYMBOL_COOLDOWN_MINUTES=120
```
