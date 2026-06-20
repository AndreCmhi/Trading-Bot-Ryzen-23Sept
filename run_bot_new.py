import state
import engine
import sys
from shared import logger

def main():
    print('=========================================')
    print('   TRADING BOT RYZEN - NEW STRUCTURE    ')
    print('=========================================')
    try:
        # Inisialisasi State & Koneksi
        print('[1/3] Menghubungkan ke Binance...')
        state.init_client()
        
        # Load Settings
        print('[2/3] Memuat konfigurasi dan filter...')
        # (Fungsi load_runtime_settings dan filters dipanggil di sini)
        
        # Start Engine
        print('[3/3] Menjalankan Mesin Trading...')
        engine.run_engine_loop()
        
    except KeyboardInterrupt:
        print('\nBot dihentikan oleh pengguna.')
        sys.exit(0)
    except Exception as e:
        print(f'\nGagal menjalankan bot: {e}')

if __name__ == '__main__':
    main()
