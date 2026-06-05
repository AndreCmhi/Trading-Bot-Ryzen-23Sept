import requests
import urllib3

urllib3.disable_warnings()

def get_top_30_min_notional():
    print("Mengambil data exchange info Binance Futures...")
    try:
        # Ambil tickers untuk disortir berdasarkan volume (tanpa verifikasi ssl di environment ini)
        ticker_resp = requests.get('https://fapi.binance.com/fapi/v1/ticker/24hr', verify=False)
        tickers = ticker_resp.json()
        
        # Ambil aturan min_notional dan lot_size
        exchange_resp = requests.get('https://fapi.binance.com/fapi/v1/exchangeInfo', verify=False)
        exchange_info = exchange_resp.json()
        
        # Filter koin USDT, status TRADING
        symbols_info = { s['symbol']: s for s in exchange_info['symbols'] if s['quoteAsset'] == 'USDT' and s['status'] == 'TRADING' }
        
        # Urutkan berdasarkan volume USDT tertinggi (quoteVolume)
        usdt_tickers = [t for t in tickers if t['symbol'] in symbols_info]
        usdt_tickers.sort(key=lambda x: float(x.get('quoteVolume', 0)), reverse=True)
        
        top_30 = usdt_tickers[:30]
        
        output_lines = [
            "==================================================",
            " TOP 30 SYMBOL BINANCE FUTURES (USDT) - MIN TRADE",
            "==================================================",
            "Diurutkan berdasarkan Volume Transaksi (24 Jam)",
            ""
        ]
        
        for idx, t in enumerate(top_30, 1):
            symbol = t['symbol']
            s_info = symbols_info[symbol]
            
            # Cari filter MIN_NOTIONAL dan LOT_SIZE
            min_notional = "Tidak diketahui"
            min_qty = "Tidak diketahui"
            
            for f in s_info['filters']:
                if f['filterType'] == 'MIN_NOTIONAL':
                    min_notional = f.get('notional', 'N/A')
                elif f['filterType'] == 'LOT_SIZE':
                    min_qty = f.get('minQty', 'N/A')
                    
            output_lines.append(f"{idx:02d}. {symbol}")
            output_lines.append(f"    Min Transaksi (Notional) : {min_notional} USDT")
            output_lines.append(f"    Min Koin (Lot Size)      : {min_qty} Koin")
            output_lines.append("")
            
        with open("C:\\Users\\Maria Oktavia\\Documents\\Bot Trading\\Top30_Min_Transaction.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(output_lines))
            
        print("Data berhasil disimpan ke Top30_Min_Transaction.txt")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_top_30_min_notional()
