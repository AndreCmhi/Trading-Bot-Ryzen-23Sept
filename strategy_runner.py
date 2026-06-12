import sys, json, time, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(__file__))
import config
from binance.client import Client
from strategy_helpers import *
from datetime import datetime

client = Client(config.API_KEY, config.API_SECRET, testnet=config.TESTNET, requests_params={'timeout': 10})

def get_klines(symbol, interval, limit):
    try:
        k = client.futures_klines(symbol=symbol, interval=interval, limit=limit)
        return [float(x[4]) for x in k]
    except: return []

def calc_rsi(closes):
    if len(closes) < 14: return 50
    g=0; l=0
    for i in range(1,len(closes)):
        d=closes[i]-closes[i-1]
        if d>0: g+=d
        else: l-=d
    ag=g/14; al=l/14
    if al==0: return 100
    return round(100-(100/(1+(ag/al))),2)

def try_grid(symbol):
    try:
        s=json.load(open('runtime_settings.json'))
        if not s.get('grid_enabled'): return
        lvs=int(s.get('grid_levels',5))
        rng=float(s.get('grid_range_pct',4.0))
        bq=float(s.get('grid_base_qty_usdt',2.0))
        k=client.futures_klines(symbol=symbol,interval='1m',limit=1)
        if not k: return
        price=float(k[-1][4])
        if price<=0: return
        info=client.futures_exchange_info()
        sym_info=None
        for s2 in info.get('symbols',[]):
            if s2.get('symbol')==symbol: sym_info=s2; break
        if not sym_info: return
        step=0.001; tick=0.01
        for f in sym_info.get('filters',[]):
            if f.get('filterType')=='LOT_SIZE': step=float(f.get('stepSize',0.001))
            if f.get('filterType')=='PRICE_FILTER': tick=float(f.get('tickSize',0.01))
        qty=round(bq/price/step)*step
        qty=max(qty,step)
        bl,sl=generate_grid_levels(price,rng,lvs)
        print(f'GRID placing {symbol}...')
        # Place BUY limit orders
        for b in bl:
            try:
                bp=round(b/tick)*tick
                client.futures_create_order(symbol=symbol,side='BUY',type='LIMIT',price=bp,quantity=qty,timeInForce='GTC')
                print(f'  BUY @ {bp}')
                time.sleep(0.2)
            except Exception as e:
                print(f'  BUY fail @ {b}: {e}')
        # Place SELL limit orders
        for s2 in sl:
            try:
                sp=round(s2/tick)*tick
                client.futures_create_order(symbol=symbol,side='SELL',type='LIMIT',price=sp,quantity=qty,timeInForce='GTC')
                print(f'  SELL @ {sp}')
                time.sleep(0.2)
            except Exception as e:
                print(f'  SELL fail @ {s2}: {e}')
    except Exception as e:
        print(f'Grid error {symbol}: {e}')

print('Strategy Runner started')
while True:
    try:
        settings=json.load(open('runtime_settings.json'))
        pos=client.futures_position_information()
        active=[p['symbol'] for p in pos if float(p['positionAmt'])!=0]
        for sym in active[:3]:
            k1=get_klines(sym,'1m',100)
            k15=get_klines(sym,'15m',50)
            k5=get_klines(sym,'5m',50)
            if len(k1)<14: continue
            r=calc_rsi(k1)
            if check_btd_opportunity(sym,k1,k15,r,settings):
                print(f'BTD: {sym} RSI={r}')
            if check_qfl_opportunity(sym,k1,k5,r,settings):
                print(f'QFL: {sym} RSI={r}')
            if settings.get('grid_enabled'):
                try_grid(sym)
                break
        time.sleep(60)
    except Exception as e:
        print(f'Loop error: {e}')
        time.sleep(120)
