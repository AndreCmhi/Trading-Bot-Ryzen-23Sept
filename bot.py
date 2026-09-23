import ccxt
import pandas as pd
import numpy as np
import time
import json
import os

class RyzenSpotBot:
    def __init__(self, config_path="config.json"):
        with open(config_path, "r") as f:
            self.config = json.load(f)
            
        self.exchange = getattr(ccxt, self.config['exchange'])({
            'apiKey': self.config['api_key'],
            'secret': self.config['api_secret'],
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })
        self.symbol = self.config['symbol']
        self.timeframe = self.config['timeframe']
        self.size = float(self.config.get('order_size', 10)) # in USDT

    def fetch_data(self):
        bars = self.exchange.fetch_ohlcv(self.symbol, timeframe=self.timeframe, limit=100)
        df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['close'] = df['close'].astype(float)
        return df

    def calculate_rsi(self, series, period=14):
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def get_signal(self):
        df = self.fetch_data()
        df['ema10'] = df['close'].ewm(span=10).mean()
        df['ema20'] = df['close'].ewm(span=20).mean()
        df['rsi'] = self.calculate_rsi(df['close'])
        
        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Strategy: EMA Cross + RSI Filter
        buy_cond = (prev['ema10'] < prev['ema20']) and (last['ema10'] > last['ema20']) and (last['rsi'] < 70)
        sell_cond = (prev['ema10'] > prev['ema20']) and (last['ema10'] < last['ema20']) and (last['rsi'] > 30)
        
        if buy_cond: return 'BUY'
        if sell_cond: return 'SELL'
        return 'HOLD'

    def run(self):
        print(f"Ryzen Bot Active: {self.symbol} ({self.timeframe})")
        while True:
            try:
                signal = self.get_signal()
                print(f"[{time.strftime('%H:%M:%S')}] Signal: {signal}")
                # Real execution logic would go here if keys are valid
                time.sleep(60)
            except Exception as e:
                print(f"Bot Error: {e}")
                time.sleep(10)

if __name__ == "__main__":
    RyzenSpotBot().run()
