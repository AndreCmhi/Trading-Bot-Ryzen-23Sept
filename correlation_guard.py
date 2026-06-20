SECTOR_MAP = {
    'BTCUSDT': 'MARKET_LEADER',
    'ETHUSDT': 'MARKET_LEADER',
    'SOLUSDT': 'LAYER_1',
    'DOGEUSDT': 'MEME',
    'PEPEUSDT': 'MEME',
    'RNDRUSDT': 'AI',
    'FETUSDT': 'AI'
}

def get_sector(symbol):
    return SECTOR_MAP.get(symbol.upper(), 'OTHER')

def check_correlation_risk(symbol, side, open_positions, max_per_sector=3, max_total_same_side=10):
    sector = get_sector(symbol)
    same_side_count = sum(1 for p in open_positions if (float(p['positionAmt']) > 0 and side == 'BUY') or (float(p['positionAmt']) < 0 and side == 'SELL'))
    if same_side_count >= max_total_same_side: return False, f'Global limit reached'
    sector_count = sum(1 for p in open_positions if get_sector(p['symbol']) == sector and ((float(p['positionAmt']) > 0 and side == 'BUY') or (float(p['positionAmt']) < 0 and side == 'SELL')))
    if sector_count >= max_per_sector: return False, f'Sector {sector} limit reached'
    return True, 'Passed'
