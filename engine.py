import time
import state
import config
from datetime import datetime
from shared import logger
from exchange_logic import call_binance, get_klines
import strategy_entry as entry
import risk_guard
from constants import *

def execute_confluence_trading():
    symbols = config.SYMBOLS
    for symbol in symbols:
        try:
            # 1. Fetch data
            k1h = get_klines(symbol, interval='1h', limit=50)
            k15m = get_klines(symbol, interval='15m', limit=20)
            # Dummy volume logic (sebaiknya diupdate di exchange_logic)
            v15m = [100] * 20 

            # 2. Check Strategy
            decision = entry.check_confluence_entry(symbol, k1h, k15m, v15m)
            
            if decision['allow']:
                # 3. Check Risk Guard
                risk = risk_guard.evaluate_pre_trade(symbol, config=vars(config))
                if not risk.get('allowed', True):
                    print(f"Skipping {symbol}: {risk.get('reason')}")
                    continue

                print(f"TRADING {symbol}: {decision['side']} based on confluence score {decision['score']}")
                # Logika pembukaan posisi Binance bisa ditambahkan di sini
                
        except Exception as e:
            print(f"Error processing {symbol}: {e}")

def run_engine_loop():
    state.init_client()
    print('--- RYZEN BOT ENGINE READY WITH CONFLUENCE ---')
    while True:
        execute_confluence_trading()
        time.sleep(60) # Scan setiap menit
