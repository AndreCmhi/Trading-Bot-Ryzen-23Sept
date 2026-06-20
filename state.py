import threading
import time
import requests
from binance.client import Client
import config
from constants import MARKET_REGIME_REFRESH_SECONDS, HISTORY_MONITOR_REFRESH_SECONDS

# Binance Client setup
client = None

def init_client():
    global client
    for _init_attempt in range(10):
        try:
            client = Client(
                config.API_KEY,
                config.API_SECRET,
                testnet=config.TESTNET,
                requests_params={'timeout': 20},
                ping=False,
            )
            if config.TESTNET:
                client.FUTURES_URL = 'https://testnet.binancefuture.com/fapi'
                client.FUTURES_DATA_URL = 'https://testnet.binancefuture.com/futures/data'

            def custom_get_server_time():
                url = 'https://testnet.binancefuture.com/fapi/v1/time' if config.TESTNET else 'https://fapi.binance.com/fapi/v1/time'
                try:
                    res = requests.get(url, timeout=5)
                    res.raise_for_status()
                    return res.json()
                except Exception as e:
                    print('Monkey server time error:', e)
                    return {'serverTime': int(time.time() * 1000)}
            
            client.get_server_time = custom_get_server_time
            return client
        except Exception as _init_exc:
            print(f'Binance connect attempt {_init_attempt+1}/10 failed: {_init_exc}')
            if _init_attempt < 9:
                time.sleep(10)
            else:
                raise RuntimeError('Binance API unreachable after 10 attempts')

# Global State
bot_running = True
bot_stop_reason = ""
bot_stop_source = "system"
last_trade_time = {}
symbol_filters = {}
scan_symbols = []
runtime_settings = {}
scan_symbols_updated_at = 0.0
auto_blocked_symbols = set()
auto_blacklist_details = {}

market_regime_state = {
    'label': 'UNKNOWN',
    'summary': 'Menunggu data market.',
    'avg_atr_5m': 0.0,
    'avg_atr_15m': 0.0,
    'avg_momentum_15m': 0.0,
    'updated_at': '',
}
market_regime_updated_at = 0.0

history_monitor_state = {
    'updated_at': '',
    'analysis_window_trades': 0,
    'closed_trades': 0,
    'recent_closed_trades': 0,
    'recent_pnl': 0.0,
    'recent_winrate': 0.0,
    'recent_loss_rate': 0.0,
    'recent_hard_stop_rate': 0.0,
    'recent_manual_loss_closes': 0,
    'recent_profit_leaks': 0,
    'recommendations': [],
    'suggested_settings': None,
    'has_setting_changes': False,
    'suggested_blocked_symbols': [],
    'suggested_avoid_hours': [],
    'best_symbols': [],
    'worst_symbols': [],
    'best_hours': [],
    'worst_hours': [],
    'close_reasons': [],
    'score_bands': [],
}
history_monitor_updated_at = 0.0

risk_guard_state = {
    'policy': 'idle',
    'symbol': '',
    'reason': 'Risk guard belum mengevaluasi trade.',
    'checked_at': '',
    'risk_multiplier': 1.0,
    'confidence_boost': 0.0,
    'leverage_cap': None,
}
risk_guard_history = []
symbol_error_cooldowns = {}

# Locks
status_lock = threading.Lock()
settings_lock = threading.Lock()
trades_lock = threading.RLock()
manual_roi_lock = threading.RLock()
manual_tp_sl_lock = threading.RLock()
trade_execution_lock = threading.RLock()
market_regime_lock = threading.Lock()
history_monitor_lock = threading.Lock()
risk_guard_lock = threading.Lock()
symbol_error_lock = threading.Lock()
