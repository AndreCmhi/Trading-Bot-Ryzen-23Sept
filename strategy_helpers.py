def check_dca_opportunity(symbol, trade, settings):
    if not settings.get('dca_enabled', False):
        return None
    dca_buy_levels = int(settings.get('dca_buy_levels', 3))
    dca_deviation_pct = float(settings.get('dca_buy_price_deviation_pct', 2.0))
    dca_count = trade.get('dca_count', 0)
    if dca_count >= dca_buy_levels:
        return None
    entry_price = float(trade.get('price', 0))
    if entry_price <= 0:
        return None
    return None  # Simplified for now


def check_btd_opportunity(symbol, closes_1m, closes_15m, rsi, settings):
    if not settings.get('btd_enabled', False):
        return None
    rsi_threshold = float(settings.get('btd_rsi_threshold', 30))
    price_drop_pct = float(settings.get('btd_price_drop_pct', 3.0))
    current_price = closes_1m[-1] if closes_1m else 0
    peak_price = max(closes_15m) if closes_15m else current_price
    price_drop = abs((peak_price - current_price) / peak_price * 100) if peak_price > 0 else 0
    if rsi < rsi_threshold and price_drop >= price_drop_pct:
        return {'action': 'BTD_BUY', 'rsi': rsi, 'price_drop': round(price_drop, 2)}
    return None


def check_qfl_opportunity(symbol, closes_1m, closes_5m, rsi, settings):
    if not settings.get('qfl_enabled', False):
        return None
    rsi_threshold = float(settings.get('qfl_rsi_threshold', 35))
    support_zone_pct = float(settings.get('qfl_support_zone_pct', 1.5))
    if len(closes_5m) < 20:
        return None
    current_price = closes_1m[-1] if closes_1m else 0
    support = min(closes_5m[-20:])
    distance_from_support = abs((current_price - support) / support * 100) if support > 0 else 100
    if rsi < rsi_threshold and distance_from_support <= support_zone_pct:
        return {'action': 'QFL_BUY', 'rsi': rsi, 'support': support}
    return None


# ===== GRID TRADING =====#

def generate_grid_levels(entry_price, range_pct, levels):
    """Generate buy/sell grid levels around entry price."""
    half_range = range_pct / 100 / 2
    grid_gap = (range_pct / 100) / levels
    buy_levels = []
    sell_levels = []
    for i in range(1, levels + 1):
        buy_levels.append(round(entry_price * (1 - grid_gap * i), 8))
        sell_levels.append(round(entry_price * (1 + grid_gap * i), 8))
    return buy_levels, sell_levels


def init_grid_state(symbol, price, range_pct, levels, qty, step_size, settings):
    """Initialize grid state dictionary."""
    buy_levels, sell_levels = generate_grid_levels(price, range_pct, levels)
    return {
        'symbol': symbol,
        'entry_price': price,
        'range_pct': range_pct,
        'levels': levels,
        'base_qty': qty,
        'step_size': step_size,
        'buy_levels': [round(b, 8) for b in buy_levels],
        'sell_levels': [round(s, 8) for s in sell_levels],
        'filled_buy_levels': [],
        'filled_sell_levels': [],
        'active': True,
        'created_at': None,
        'total_pnl': 0.0,
        'total_trades': 0,
    }


def place_grid_orders_on_exchange(symbol, side, levels, qty, step_size, call_fn):
    """Place grid limit orders on exchange."""
    placed = []
    for price in levels:
        try:
            adj_qty = round(qty / step_size) * step_size
            adj_qty = max(adj_qty, step_size)
            order = call_fn(
                'futures_create_order',
                symbol=symbol,
                side=side,
                type='LIMIT',
                price=price,
                quantity=adj_qty,
                timeInForce='GTC'
            )
            placed.append({'price': price, 'side': side, 'qty': adj_qty, 'order_id': order.get('orderId')})
        except Exception as e:
            print(f'Grid order error {symbol} at {price}: {e}')
    return placed


def monitor_grid_state(grid_state, open_orders, call_fn):
    """Monitor grid and return grid with updated filled levels."""
    if not grid_state or not grid_state.get('active'):
        return grid_state

    filled_buy_prices = {o['price'] for o in open_orders if o['side'] == 'SELL'}
    filled_sell_prices = {o['price'] for o in open_orders if o['side'] == 'BUY'}

    changes = False
    for bl in grid_state['buy_levels']:
        if bl not in filled_buy_prices and bl not in grid_state['filled_buy_levels']:
            grid_state['filled_buy_levels'].append(bl)
            grid_state['total_trades'] += 1
            changes = True

    for sl in grid_state['sell_levels']:
        if sl not in filled_sell_prices and sl not in grid_state['filled_sell_levels']:
            grid_state['filled_sell_levels'].append(sl)
            grid_state['total_trades'] += 1
            changes = True

    if changes:

        buys_filled = len(grid_state['filled_buy_levels'])
        buys_total = len(grid_state['buy_levels'])
        sells_filled = len(grid_state['filled_sell_levels'])
        sells_total = len(grid_state['sell_levels'])
        print(f'Grid progress: buys {buys_filled}/{buys_total} sells {sells_filled}/{sells_total}')

        return grid_state


def check_grid_breakout(grid_state, current_price, call_fn):
    """Check if price broke out of grid range - triggers recovery."""
    if not grid_state or not grid_state.get('active'):
        return False
    max_sell = max(grid_state['sell_levels']) if grid_state['sell_levels'] else 0
    min_buy = min(grid_state['buy_levels']) if grid_state['buy_levels'] else float('inf')
    if current_price > max_sell * 1.02 or current_price < min_buy * 0.98:
        return True
    max_sell = max(grid_state["sell_levels"]) if grid_state["sell_levels"] else 0
    min_buy = min(grid_state["buy_levels"]) if grid_state["buy_levels"] else float("inf")
    if current_price > max_sell * 1.02 or current_price < min_buy * 0.98:
        sym = grid_state.get("symbol", "?")
        msg = "Grid breakout for " + str(sym) + ": price " + str(current_price) + " outside grid range"
        print(msg)
        return True
    return False
def cancel_all_grid_orders(symbol, call_fn):
    """Cancel all open orders for a symbol (grid recovery)."""
    try:
        call_fn('futures_cancel_all_open_orders', symbol=symbol)
        print(f'All grid orders cancelled for {symbol}')
        return True
    except Exception as e:
        print(f'Cancel grid orders error {symbol}: {e}')
        return False
