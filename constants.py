import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = BASE_DIR / 'Templates'
DATA_FILE = BASE_DIR / 'trades.json'
TESTNET_SHADOW_POSITIONS_FILE = BASE_DIR / 'testnet_shadow_positions.json'
MANUAL_ROI_FILE = BASE_DIR / 'manual_roi.json'
MANUAL_TP_SL_FILE = BASE_DIR / 'manual_tp_sl.json'
AI_DECISIONS_FILE = BASE_DIR / 'ai_decisions.json'
SETTINGS_FILE = BASE_DIR / 'runtime_settings.json'

COOLDOWN = int(os.getenv('COOLDOWN', '15'))
SCAN_INTERVAL = int(os.getenv('SCAN_INTERVAL', '60'))
DEFAULT_LEVERAGE = 5
DEFAULT_FIXED_TRADE_NOTIONAL_USDT = float(os.getenv('DEFAULT_FIXED_TRADE_NOTIONAL_USDT', '3.0'))
DEFAULT_ACTIVE_MARGIN_BALANCE_PERCENT = float(os.getenv('DEFAULT_ACTIVE_MARGIN_BALANCE_PERCENT', '25.0'))
DEFAULT_RISK_PER_TRADE_PERCENT = float(os.getenv('DEFAULT_RISK_PER_TRADE_PERCENT', '0.75'))
FEE_BUFFER_FACTOR = float(os.getenv('FEE_BUFFER_FACTOR', '1.5'))
MAX_RISK_PER_TRADE_PERCENT = float(os.getenv('MAX_RISK_PER_TRADE_PERCENT', '2.0'))
DEFAULT_MIN_RISK_REWARD_RATIO = float(os.getenv('DEFAULT_MIN_RISK_REWARD_RATIO', '2.0'))
DEFAULT_TRADING_STYLE = str(os.getenv('DEFAULT_TRADING_STYLE', 'AUTO')).strip().upper()
DEFAULT_MARGIN_MODE = str(os.getenv('DEFAULT_MARGIN_MODE', 'ISOLATED')).strip().upper()

ADAPTIVE_PERFORMANCE_LOOKBACK_TRADES = int(os.getenv('ADAPTIVE_PERFORMANCE_LOOKBACK_TRADES', '24'))
BUY_SCALPING_PAUSE_MIN_TRADES = int(os.getenv('BUY_SCALPING_PAUSE_MIN_TRADES', '6'))
BUY_SCALPING_PAUSE_MAX_WINRATE = float(os.getenv('BUY_SCALPING_PAUSE_MAX_WINRATE', '20'))
BUY_SCALPING_PAUSE_MAX_TOTAL_PNL = float(os.getenv('BUY_SCALPING_PAUSE_MAX_TOTAL_PNL', '-10'))
BUY_SCALPING_PAUSE_MAX_HARD_STOP_RATE = float(os.getenv('BUY_SCALPING_PAUSE_MAX_HARD_STOP_RATE', '0.35'))

TEST_MINIMUM_TRADING_MODE = os.getenv('TEST_MINIMUM_TRADING_MODE', 'false').lower() == 'true'
TEST_TP_PERCENT = float(os.getenv('TEST_TP_PERCENT', '1.0'))
TEST_SL_PERCENT = float(os.getenv('TEST_SL_PERCENT', '3.0'))
TEST_TRAILING_TRIGGER_ROI_PERCENT = float(os.getenv('TEST_TRAILING_TRIGGER_ROI_PERCENT', '1.0'))
TEST_TRAILING_CALLBACK_ROI_PERCENT = float(os.getenv('TEST_TRAILING_CALLBACK_ROI_PERCENT', '0.35'))

AI_ENABLED = os.getenv('AI_ENABLED', 'false' if TEST_MINIMUM_TRADING_MODE else 'true').lower() == 'true'
AI_ADVISORY_ONLY = True if TEST_MINIMUM_TRADING_MODE else os.getenv('AI_ADVISORY_ONLY', 'false').lower() == 'true'
AI_MIN_CONFIDENCE = float(os.getenv('AI_MIN_CONFIDENCE', '0.62'))
RISK_GUARD_ENABLED = os.getenv('RISK_GUARD_ENABLED', 'true').lower() == 'true'
RELAXED_SETUP_MODE = os.getenv('RELAXED_SETUP_MODE', 'false').lower() == 'true'
UNRESTRICTED_SCAN_UNIVERSE = True
DISABLE_TREND_FILTER = os.getenv('DISABLE_TREND_FILTER', 'false').lower() == 'true'
DISABLE_PULLBACK_FILTER = os.getenv('DISABLE_PULLBACK_FILTER', 'false').lower() == 'true'

MAX_OPEN_POSITIONS = int(os.getenv('MAX_OPEN_POSITIONS', '5'))
MAX_DAILY_LOSS_USDT = float(os.getenv('MAX_DAILY_LOSS_USDT', '20'))
MAX_CONSECUTIVE_LOSSES = int(os.getenv('MAX_CONSECUTIVE_LOSSES', '3'))
MAX_TRADES_PER_HOUR = int(os.getenv('MAX_TRADES_PER_HOUR', '6'))
MAX_LOSSES_PER_HOUR = int(os.getenv('MAX_LOSSES_PER_HOUR', '1'))
HOURLY_LOSS_LIMIT_USDT = float(os.getenv('HOURLY_LOSS_LIMIT_USDT', '2.0'))
LOSS_COOLDOWN_MINUTES = int(os.getenv('LOSS_COOLDOWN_MINUTES', '60'))
MAX_SYMBOL_TRADES_PER_DAY = int(os.getenv('MAX_SYMBOL_TRADES_PER_DAY', '1'))
MAX_SYMBOL_LOSSES_PER_DAY = int(os.getenv('MAX_SYMBOL_LOSSES_PER_DAY', '1'))
MAX_SYMBOL_CONSECUTIVE_LOSSES = int(os.getenv('MAX_SYMBOL_CONSECUTIVE_LOSSES', '1'))
SYMBOL_LOSS_COOLDOWN_MINUTES = int(os.getenv('SYMBOL_LOSS_COOLDOWN_MINUTES', '240'))
HARD_STOP_SYMBOL_COOLDOWN_MINUTES = int(os.getenv('HARD_STOP_SYMBOL_COOLDOWN_MINUTES', '120'))

AUTO_PAUSE_ON_GUARD_HALT = os.getenv('AUTO_PAUSE_ON_GUARD_HALT', 'false').lower() == 'true'
AUTO_CLOSE_POSITIONS_ON_GUARD_HALT = os.getenv('AUTO_CLOSE_POSITIONS_ON_GUARD_HALT', 'true').lower() == 'true'
AUTO_CLOSE_ENABLED = os.getenv('AUTO_CLOSE_ENABLED', 'true').lower() == 'true'
AUTO_CLOSE_ROI_PERCENT = float(os.getenv('AUTO_CLOSE_ROI_PERCENT', '3.0'))
MAX_ALLOWED_ATR_PERCENT = float(os.getenv('MAX_ALLOWED_ATR_PERCENT', '1.8'))
TOP_SYMBOL_LIMIT = int(os.getenv('TOP_SYMBOL_LIMIT', '20'))
SYMBOL_RANK_REFRESH_SECONDS = int(os.getenv('SYMBOL_RANK_REFRESH_SECONDS', '900'))
MAX_ALLOWED_FUNDING_RATE = float(os.getenv('MAX_ALLOWED_FUNDING_RATE', '0.0008'))
PULLBACK_DISTANCE_PERCENT = float(os.getenv('PULLBACK_DISTANCE_PERCENT', '0.35'))
ENTRY_BREAKOUT_BUFFER_PERCENT = float(os.getenv('ENTRY_BREAKOUT_BUFFER_PERCENT', '0.03'))
MIN_EMA_SLOPE_5M = float(os.getenv('MIN_EMA_SLOPE_5M', '0.015'))
MIN_EMA_SLOPE_15M = float(os.getenv('MIN_EMA_SLOPE_15M', '0.02'))
MIN_EMA_SLOPE_1H = float(os.getenv('MIN_EMA_SLOPE_1H', '0.015'))
PARTIAL_TP_ROI_PERCENT = float(os.getenv('PARTIAL_TP_ROI_PERCENT', '4.0'))
PARTIAL_CLOSE_FRACTION = float(os.getenv('PARTIAL_CLOSE_FRACTION', '0.35'))
BREAKEVEN_TRIGGER_ROI_PERCENT = float(os.getenv('BREAKEVEN_TRIGGER_ROI_PERCENT', '2.5'))
TRAILING_TRIGGER_ROI_PERCENT = float(os.getenv('TRAILING_TRIGGER_ROI_PERCENT', '2.5'))
TRAILING_CALLBACK_ROI_PERCENT = float(os.getenv('TRAILING_CALLBACK_ROI_PERCENT', '0.8'))
FAST_TRAILING_TRIGGER_ROI_PERCENT = float(os.getenv('FAST_TRAILING_TRIGGER_ROI_PERCENT', '0.9'))
FAST_TRAILING_CALLBACK_ROI_PERCENT = float(os.getenv('FAST_TRAILING_CALLBACK_ROI_PERCENT', '0.25'))
HARD_STOP_ROI_PERCENT = float(os.getenv('HARD_STOP_ROI_PERCENT', '-2.5'))

SYMBOL_SCAN_MODE = os.getenv('SYMBOL_SCAN_MODE', 'ALL').strip().upper()
MANUAL_BLOCKED_SYMBOLS = {
    symbol.strip().upper()
    for symbol in os.getenv(
        'BLOCKED_SYMBOLS',
        'BASUSDT,RABUSDT,LRCUSDT,LABUSDT,PORT3USDT,FISUSDT,FXSUSDT,PLAYUSDT,BCHUSDT,TOKENUSDT,PONKEUSDT,TRBUSDT,SKYAIUSDT,SIRENUSDT,QUICKUSDT',
    ).split(',')
    if symbol.strip()
}

AUTO_BLACKLIST_ENABLED = os.getenv('AUTO_BLACKLIST_ENABLED', 'true').lower() == 'true'
AUTO_BLACKLIST_MIN_TRADES = int(os.getenv('AUTO_BLACKLIST_MIN_TRADES', '2'))
AUTO_BLACKLIST_MIN_LOSS_RATE = float(os.getenv('AUTO_BLACKLIST_MIN_LOSS_RATE', '0.65'))
AUTO_BLACKLIST_MAX_TOTAL_PNL = float(os.getenv('AUTO_BLACKLIST_MAX_TOTAL_PNL', '-0.03'))
AUTO_BLACKLIST_MIN_HARD_STOP_RATE = float(os.getenv('AUTO_BLACKLIST_MIN_HARD_STOP_RATE', '0.5'))
AUTO_BLACKLIST_MIN_CONSECUTIVE_LOSSES = int(os.getenv('AUTO_BLACKLIST_MIN_CONSECUTIVE_LOSSES', '2'))

DEFAULT_HOST = os.getenv('APP_HOST', '0.0.0.0')
DEFAULT_PORT = int(os.getenv('APP_PORT', '5000'))
APP_USERNAME = os.getenv('APP_USERNAME', 'admin')
APP_PASSWORD = os.getenv('APP_PASSWORD', 'ganti-password-ini')
APP_SECRET_KEY = os.getenv('APP_SECRET_KEY', 'ganti-secret-key-ini')

MARKET_REGIME_REFRESH_SECONDS = 180
HISTORY_MONITOR_REFRESH_SECONDS = 15

STRATEGY_PROFILES = {
    'AGGRESSIVE': {
        'min_score': 12,
        'ai_min_confidence': 0.62,
        'pullback_distance_percent': 0.42,
        'entry_breakout_buffer_percent': 0.02,
        'min_ema_slope_5m': 0.01,
        'min_ema_slope_15m': 0.015,
        'min_ema_slope_1h': 0.01,
        'buy_rsi_min': 44,
        'buy_rsi_max': 65,
        'sell_rsi_min': 35,
        'sell_rsi_max': 56,
        'auto_close_roi_percent': 3.0,
        'partial_tp_factor': 0.5,
        'breakeven_buffer': 0.55,
        'trailing_trigger_bonus': 0.55,
        'trailing_floor_factor': 0.3,
    },
    'BALANCED': {
        'min_score': 12,
        'ai_min_confidence': 0.65,
        'pullback_distance_percent': PULLBACK_DISTANCE_PERCENT,
        'entry_breakout_buffer_percent': ENTRY_BREAKOUT_BUFFER_PERCENT,
        'min_ema_slope_5m': MIN_EMA_SLOPE_5M,
        'min_ema_slope_15m': MIN_EMA_SLOPE_15M,
        'min_ema_slope_1h': MIN_EMA_SLOPE_1H,
        'buy_rsi_min': 45,
        'buy_rsi_max': 64,
        'sell_rsi_min': 36,
        'sell_rsi_max': 55,
        'auto_close_roi_percent': 4.2,
        'partial_tp_factor': 0.55,
        'breakeven_buffer': 0.7,
        'trailing_trigger_bonus': 0.7,
        'trailing_floor_factor': 0.35,
    },
    'SCALPING': {
        'min_score': 12,
        'ai_min_confidence': 0.70,
        'pullback_distance_percent': 0.20,
        'entry_breakout_buffer_percent': 0.05,
        'min_ema_slope_5m': 0.025,
        'min_ema_slope_15m': 0.03,
        'min_ema_slope_1h': 0.025,
        'buy_rsi_min': 49,
        'buy_rsi_max': 61,
        'sell_rsi_min': 39,
        'sell_rsi_max': 51,
        'auto_close_roi_percent': 4.5,
        'partial_tp_factor': 0.30,
        'breakeven_buffer': 0.35,
        'trailing_trigger_bonus': 0.2,
        'trailing_floor_factor': 0.25,
        'scalping_mode': True,
    },
    'PRECISION': {
        'min_score': 12,
        'ai_min_confidence': 0.68,
        'pullback_distance_percent': 0.28,
        'entry_breakout_buffer_percent': 0.04,
        'min_ema_slope_5m': 0.02,
        'min_ema_slope_15m': 0.025,
        'min_ema_slope_1h': 0.02,
        'buy_rsi_min': 48,
        'buy_rsi_max': 62,
        'sell_rsi_min': 38,
        'sell_rsi_max': 52,
        'auto_close_roi_percent': 4.8,
        'partial_tp_factor': 0.62,
        'breakeven_buffer': 0.85,
        'trailing_trigger_bonus': 0.9,
        'trailing_floor_factor': 0.45,
    },
    'TARGET_75': {
        'min_score': 12,
        'ai_min_confidence': 0.80,
        'pullback_distance_percent': 0.22,
        'entry_breakout_buffer_percent': 0.06,
        'min_ema_slope_5m': 0.03,
        'min_ema_slope_15m': 0.035,
        'min_ema_slope_1h': 0.03,
        'buy_rsi_min': 50,
        'buy_rsi_max': 60,
        'sell_rsi_min': 40,
        'sell_rsi_max': 50,
        'auto_close_roi_percent': 2.5,
        'partial_tp_factor': 0.5,
        'breakeven_buffer': 0.45,
        'trailing_trigger_bonus': 0.2,
        'trailing_floor_factor': 0.6,
        'high_target_mode': True,
    },
}
MAX_POSITIONS_PER_SECTOR = 3
MAX_SAMESIDE_CORRELATION = 10
