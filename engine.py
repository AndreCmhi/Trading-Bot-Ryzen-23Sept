import time
import state
import config
from datetime import datetime
from shared import logger
from exchange_logic import call_binance, get_klines
import strategy_entry as entry
import risk_guard
from constants import *

# === ANTIGRAVITY UPGRADE ===
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from upgrade_antigravity.ag_pipeline import antigravity_gate
from upgrade_antigravity.ag_volume_fetch import get_real_volumes
from risk_guard import count_consecutive_losses


def _get_equity():
    try:
        account = call_binance('futures_account')
        return float(account.get('totalWalletBalance', 100.0))
    except Exception:
        return 100.0


def _get_closed_trades():
    try:
        return state.trades if hasattr(state, 'trades') else []
    except Exception:
        return []


def _get_open_count():
    try:
        positions = call_binance('futures_position_information')
        return sum(1 for p in positions if float(p.get('positionAmt', 0)) != 0)
    except Exception:
        return 0


def execute_confluence_trading():
    symbols = config.SYMBOLS
    equity = _get_equity()
    closed_trades = _get_closed_trades()
    open_count = _get_open_count()
    consecutive_losses = count_consecutive_losses(closed_trades)

    for symbol in symbols:
        try:
            # 1. Fetch klines
            k1h  = get_klines(symbol, interval='1h',  limit=50)
            k15m = get_klines(symbol, interval='15m', limit=30)

            # 2. Fetch volume NYATA (bukan dummy)
            v15m = get_real_volumes(symbol, interval='15m', limit=30)
            if not v15m:
                v15m = [100.0] * 30  # fallback jika API gagal

            # 3. Check konfluensi entry
            decision = entry.check_confluence_entry(symbol, k1h, k15m, v15m)

            if not decision.get('allow'):
                continue

            # 4. Build snapshot untuk Antigravity gate
            snapshot = {
                'symbol':  symbol,
                'action':  decision.get('side', 'HOLD'),
                'adx':     decision.get('adx', 0),
                'rsi':     decision.get('rsi', 50),
                'tp_percent':         decision.get('tp_percent', 2.0),
                'sl_percent':         decision.get('sl_percent', 1.0),
                'suggested_leverage': decision.get('leverage', 5),
            }

            # 5. ANTIGRAVITY GATE (semua 5 filter)
            ag = antigravity_gate(
                snapshot=snapshot,
                decision=decision,
                equity=equity,
                closed_trades=closed_trades,
                open_count=open_count,
                consecutive_losses=consecutive_losses,
                symbol=symbol,
                volumes=v15m,
            )

            if not ag['allowed']:
                print(f"[AG BLOCK] {symbol}: {ag['reason']} (gate: {ag['block_gate']})")
                continue

            # 6. Legacy risk_guard (tetap aktif sebagai lapisan tambahan)
            risk = risk_guard.evaluate_pre_trade(symbol, config=vars(config))
            if not risk.get('allowed', True):
                print(f"[RISK GUARD] {symbol}: {risk.get('reason')}")
                continue

            # 7. Apply risk multiplier dari Antigravity
            effective_risk_mult = ag.get('risk_multiplier', 1.0)
            leverage_cap        = ag.get('leverage_cap', 10)

            print(
                f"[TRADE] {symbol}: {decision['side']} | "
                f"Score {decision.get('score', 0)} | "
                f"RiskMult {effective_risk_mult:.2f} | "
                f"LevCap {leverage_cap} | "
                f"Bonus conf +{ag.get('confidence_bonus', 0):.3f} | "
                f"{ag['reason'][:80]}"
            )
            # <<< Logika open_position(symbol, decision, effective_risk_mult, leverage_cap) di sini >>>

        except Exception as exc:
            print(f'[ENGINE ERROR] {symbol}: {exc}')


def run_engine_loop():
    state.init_client()
    print('--- RYZEN BOT ENGINE READY [ANTIGRAVITY v1.0] ---')
    while True:
        execute_confluence_trading()
        time.sleep(60)
