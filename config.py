import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"

def _load_env_file():
    if not ENV_FILE.exists():
        return
    for raw_line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ[key] = value

_load_env_file()

API_KEY = os.getenv("BINANCE_API_KEY", "")
API_SECRET = os.getenv("BINANCE_API_SECRET", "")
TESTNET = os.getenv("BINANCE_TESTNET", "true").lower() == "true"
SYMBOLS = os.getenv("SYMBOLS", "BTCUSDT,ETHUSDT,SOLUSDT").split(",")
MIN_SCORE = int(os.getenv("MIN_SCORE", "3"))

# Trading constants
MIN_RRR = float(os.getenv("MIN_RRR", "2.0"))
BEGINNER_MIN_LEVERAGE = int(os.getenv("BEGINNER_MIN_LEVERAGE", "2"))
BEGINNER_MAX_LEVERAGE = int(os.getenv("BEGINNER_MAX_LEVERAGE", "5"))
MIN_STOP_LOSS_PERCENT = float(os.getenv("MIN_STOP_LOSS_PERCENT", "0.3"))
MAX_STOP_LOSS_PERCENT = float(os.getenv("MAX_STOP_LOSS_PERCENT", "1.2"))
MAX_ALLOWED_ATR_PERCENT = float(os.getenv("MAX_ALLOWED_ATR_PERCENT", "3.0"))
MAX_ALLOWED_FUNDING_RATE = float(os.getenv("MAX_ALLOWED_FUNDING_RATE", "0.0006"))
PULLBACK_DISTANCE_PERCENT = float(os.getenv("PULLBACK_DISTANCE_PERCENT", "0.35"))
ENTRY_BREAKOUT_BUFFER_PERCENT = float(os.getenv("ENTRY_BREAKOUT_BUFFER_PERCENT", "0.03"))
MIN_EMA_SLOPE_5M = float(os.getenv("MIN_EMA_SLOPE_5M", "0.015"))
MIN_EMA_SLOPE_15M = float(os.getenv("MIN_EMA_SLOPE_15M", "0.02"))
MIN_EMA_SLOPE_1H = float(os.getenv("MIN_EMA_SLOPE_1H", "0.015"))
AUTO_CLOSE_ENABLED = os.getenv("AUTO_CLOSE_ENABLED", "true").lower() == "true"
AUTO_CLOSE_ROI_PERCENT = float(os.getenv("AUTO_CLOSE_ROI_PERCENT", "4.0"))
AUTO_BLACKLIST_ENABLED = os.getenv("AUTO_BLACKLIST_ENABLED", "true").lower() == "true"
AUTO_BLACKLIST_MIN_TRADES = int(os.getenv("AUTO_BLACKLIST_MIN_TRADES", "3"))
PARTIAL_TP_ROI_PERCENT = float(os.getenv("PARTIAL_TP_ROI_PERCENT", "2.0"))
BREAKEVEN_TRIGGER_ROI_PERCENT = float(os.getenv("BREAKEVEN_TRIGGER_ROI_PERCENT", "1.0"))
TRAILING_TRIGGER_ROI_PERCENT = float(os.getenv("TRAILING_TRIGGER_ROI_PERCENT", "3.0"))
TRAILING_CALLBACK_ROI_PERCENT = float(os.getenv("TRAILING_CALLBACK_ROI_PERCENT", "1.0"))
FAST_TRAILING_TRIGGER_ROI_PERCENT = float(os.getenv("FAST_TRAILING_TRIGGER_ROI_PERCENT", "0.10"))
FAST_TRAILING_CALLBACK_ROI_PERCENT = float(os.getenv("FAST_TRAILING_CALLBACK_ROI_PERCENT", "0.08"))
HARD_STOP_ROI_PERCENT = float(os.getenv("HARD_STOP_ROI_PERCENT", "-3.0"))
PARTIAL_CLOSE_FRACTION = float(os.getenv("PARTIAL_CLOSE_FRACTION", "0.5"))

