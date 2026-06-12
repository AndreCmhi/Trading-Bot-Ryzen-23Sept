def try_grid(symbol):
    try:
        s=json.load(open("runtime_settings.json"))
        if not s.get("grid_enabled"): return
        lvs=int(s.get("grid_levels",5))
        rng=float(s.get("grid_range_pct",4.0))
        bq=float(s.get("grid_base_qty_usdt",2.0))
        k=client.futures_klines(symbol=symbol,interval="1m",limit=1)
        if not k: return
        price=float(k[-1][4])
        if price<=0: return
        info=client.futures_exchange_info()
        sym_info=None
        for s2 in info.get("symbols",[]):
            if s2.get("symbol")==symbol: sym_info=s2; break
        if not sym_info: return
        step=0.001; tick=0.01
        for f in sym_info.get("filters",[]):
            if f.get("filterType")==chr(76)+chr(79)+chr(84)+chr(95)+chr(83)+chr(73)+chr(90)+chr(69): step=float(f.get("stepSize",0.001))
            if f.get("filterType")==chr(80)+chr(82)+chr(73)+chr(67)+chr(69)+chr(95)+chr(70)+chr(73)+chr(76)+chr(84)+chr(69)+chr(82): tick=float(f.get("tickSize",0.01))
        qty=round(bq/price/step)*step
        qty=max(qty,step)
        bl,sl=generate_grid_levels(price,rng,lvs)
        print('GRID placing ' + symbol + '...')
        for b in bl:
            try:
                bp=round(b/tick)*tick
                client.futures_create_order(symbol=symbol,side="BUY",type="LIMIT",price=bp,quantity=qty,timeInForce="GTC")
                print('  BUY order: ' + str(bp))
            except: pass
        for s2 in sl:
            try:
                sp=round(s2/tick)*tick
                client.futures_create_order(symbol=symbol,side="SELL",type="LIMIT",price=sp,quantity=qty,timeInForce="GTC")
                print('  SELL order: ' + str(sp))
            except: pass
    except Exception as e:
        print('Grid error ' + symbol + ': ' + str(e))
