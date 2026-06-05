path = r"C:\Users\Maria Oktavia\Documents\Bot Trading\app.py"
with open(path, encoding="utf-8") as f:
    content = f.read()

# Add more missing constants
more_consts = '''
# More trading constants
MAX_TRADES_PER_HOUR = 100
MAX_LOSSES_PER_HOUR = 5
HOURLY_LOSS_LIMIT_USDT = 50.0
LOSS_COOLDOWN_MINUTES = 30
AUTO_PAUSE_ON_GUARD_HALT = True
AUTO_CLOSE_POSITIONS_ON_GUARD_HALT = False
MAX_SYMBOL_TRADES_PER_DAY = 50
MAX_SYMBOL_LOSSES_PER_DAY = 5
MAX_SYMBOL_CONSECUTIVE_LOSSES = 5
SYMBOL_LOSS_COOLDOWN_MINUTES = 120
HARD_STOP_SYMBOL_COOLDOWN_MINUTES = 240
MAX_RISK_PER_TRADE_PERCENT = 2.0
MAX_RISK_AMOUNT_USDT = 10.0
MAX_MARGIN_PER_TRADE_USDT = 20.0
MAX_TOTAL_MARGIN_PERCENT = 10.0
DEFAULT_LEVERAGE = 10
'''

# Insert after the last constant we added
if "MAX_TRADES_PER_HOUR = 100" not in content:
    content = content.replace(
        "BEGINNER_MAX_LEVERAGE = 10\n",
        "BEGINNER_MAX_LEVERAGE = 10\n" + more_consts
    )
    open(path, "w", encoding="utf-8").write(content)
    print("More constants added")
else:
    print("Constants already exist")
