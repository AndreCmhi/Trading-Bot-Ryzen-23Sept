import time
import state
from shared import logger
import config
from constants import DEFAULT_LEVERAGE, DEFAULT_MARGIN_MODE, TEST_MINIMUM_TRADING_MODE, TEST_TRAILING_TRIGGER_ROI_PERCENT

def call_binance(method, *args, **kwargs):
    if not state.client:
        state.init_client()
    try:
        func = getattr(state.client, method)
        return func(*args, **kwargs)
    except Exception as exc:
        print(f'Binance API Error ({method}): {exc}')
        raise

def set_leverage(symbol, leverage=5):
    try:
        call_binance('futures_change_leverage', symbol=symbol, leverage=leverage)
    except Exception as exc:
        print(f'Leverage error {symbol}:', exc)

def ensure_margin_mode(symbol, margin_mode='ISOLATED'):
    try:
        call_binance('futures_change_margin_type', symbol=symbol, marginType=margin_mode)
    except Exception as exc:
        message = str(exc)
        if 'No need to change margin type' in message or '-4046' in message:
            return
        print(f'Margin mode error {symbol}:', exc)

def get_current_positions():
    try:
        positions = call_binance('futures_position_information')
        return [p for p in positions if float(p.get('positionAmt', 0)) != 0]
    except:
        return []

def get_klines(symbol, interval='1m', limit=100):
    try:
        klines = call_binance('futures_klines', symbol=symbol, interval=interval, limit=limit)
        return [float(k[4]) for k in klines]
    except Exception as exc:
        print(f'Error fetching klines for {symbol}: {exc}')
        return []

def cancel_all_orders(symbol):
    try:
        call_binance('futures_cancel_all_open_orders', symbol=symbol)
    except Exception as exc:
        print(f'Error canceling orders for {symbol}: {exc}')

def close_position(symbol, reason='MANUAL'):
    try:
        positions = call_binance('futures_position_information', symbol=symbol)
        pos = next((p for p in positions if float(p['positionAmt']) != 0), None)
        if not pos: return True, 'No position'
        amt = float(pos['positionAmt'])
        side = 'SELL' if amt > 0 else 'BUY'
        call_binance('futures_create_order', symbol=symbol, side=side, type='MARKET', quantity=abs(amt), reduceOnly=True)
        cancel_all_orders(symbol)
        return True, 'Closed'
    except Exception as exc:
        return False, str(exc)
