# Trading Bot Ryzen - Summary

## Bot Info
- **Type**: Binance Futures Crypto Trading Bot
- **Framework**: Flask + Flask-SocketIO
- **AI Integration**: Groq (Llama 3.1) / Ollama (Llama 3.2)
- **Platform**: Windows (bat launcher)

## Current Config (.env)
| Setting | Value |
|---------|-------|
| Mode | Testnet (`BINANCE_TESTNET=true`) |
| Symbols | 30 coins (BTC, ETH, SOL, XAU, etc.) |
| Min Score | 8 |
| AI Enabled | true |
| AI Provider | groq |
| Risk/Trade | 1.0% |
| Max Positions | 5 |
| Scan Interval | 30s |

## Key Files
- `app.py` (main) - Flask server + trading loop
- `ai_decision.py` - AI decision engine
- `risk_guard.py` - Risk management
- `enhanced_risk.py` - Advanced risk (Kelly criterion)
- `advanced_indicators.py` - Technical indicators (RSI, MACD, Bollinger, ADX)
- `config.py` - ENV loader

## Dependencies
```
flask
flask-socketio
binance-connector
requests
urllib3
python-dotenv
```

## Status
- Last run: Unknown (check `out.log`)
- Trades executed: 0 (from trades.json)
- Dashboard: `http://127.0.0.1:5000`

## Deployment
- See `DEPLOYMENT.md` for full instructions
