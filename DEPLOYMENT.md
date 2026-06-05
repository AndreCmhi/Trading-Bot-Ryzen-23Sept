# Trading Bot Ryzen - Deployment Instructions

## Requirements
- Python 3.12+
- Windows (bat file provided)

## Quick Start

1. **Install Dependencies**
```powershell
pip install flask flask-socketio binance-connector requests urllib3 python-dotenv
```

2. **Configure .env**
- Edit file `.env` dengan API key Binance kamu
- `BINANCE_TESTNET=true` untuk testnet, `false` untuk real account

3. **Run Bot**
```powershell
start_bot_trading.bat
```
Atau langsung:
```powershell
python app.py
```

4. **Access Dashboard**
- URL: `http://127.0.0.1:5000`
- Username: `admin`
- Password: `Avada2404@`


## Configuration (.env)

| Variable | Default | Description |
|----------|---------|-------------|
| `BINANCE_TESTNET` | true | Testnet/Real |
| `SYMBOLS` | BTCUSDT,ETHUSDT,... | Coins to trade |
| `MIN_SCORE` | 8 | Min signal score |
| `AI_ENABLED` | true | Enable AI decisions |
| `AI_PROVIDER` | groq | groq/ollama |
| `RISK_PER_TRADE_PERCENT` | 1.0 | Risk per trade % |
| `MAX_OPEN_POSITIONS` | 5 | Max concurrent trades |
| `SCAN_INTERVAL` | 30 | Scan interval (seconds) |

## Files

- `app.py` - Main Flask app + trading logic
- `ai_decision.py` - AI trading decisions
- `risk_guard.py` - Risk management
- `config.py` - Configuration loader
- `start_bot_trading.bat` - Launcher script
- `trades.json` - Trade history
- `out.log` / `err.log` - Logs

## Security

- Change `APP_PASSWORD` and `APP_SECRET_KEY` in .env
- Never commit `.env` to git (already in .gitignore)
- Use testnet first to verify
