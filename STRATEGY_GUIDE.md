# Panduan Strategi Trading: High Win-Rate Scalping 24/7

Dokumen ini berisi dokumentasi konfigurasi dan strategi trading non-stop 24 jam dengan target win rate di atas 75% menggunakan multi-posisi aktif.

## 1. Ringkasan Strategi
Strategi ini dirancang dengan metode **Micro-Scalping** yang agresif namun aman. Bot mendeteksi peluang kecil pada pergerakan harga tren searah (EMA trend-following), lalu mengamankan profit dengan cepat sebelum pasar berbalik arah. Analisis sentimen dinilai secara real-time oleh kecerdasan buatan (Groq Llama 3.1 8B).

---

## 2. Detail Parameter Konfigurasi

Berikut adalah parameter optimal yang telah dipasang pada file `runtime_settings.json` dan `.env`:

### A. Volume & Frekuensi Transaksi (24/7 Aktif)
* **`max_open_positions` = 30**
  * Memungkinkan bot membuka hingga 30 posisi koin yang berbeda secara bersamaan untuk menyebarkan risiko (diversifikasi).
* **`max_trades_per_hour` = 15**
  * Limit transaksi per jam ditingkatkan agar bot aktif mengeksekusi sinyal baru saat pasar bergerak cepat.
* **`TOP_SYMBOL_LIMIT` = 50** *(di .env)*
  * Bot memindai 50 koin teratas berdasarkan volume transaksi di Binance Futures untuk mencari setup terbaik.
* **`SCAN_INTERVAL` = 30** *(di .env)*
  * Interval pemindaian pasar dilakukan setiap 30 detik untuk akurasi entri instan.

### B. Filter Tren & Kualitas Entri (Akurasi Tinggi)
* **`disable_trend_filter` = false**
  * Wajib aktif. Bot hanya akan melakukan **BUY** pada tren naik (Bullish) dan **SELL/SHORT** pada tren turun (Bearish). Ini menghindari posisi nyangkut akibat melawan arus pasar global.
* **`disable_pullback_filter` = false**
  * Memastikan bot membeli saat harga sedang diskon (pullback), bukan di pucuk harga tertinggi.
* **`ai_enabled` = true & `ai_provider` = "groq"**
  * Setiap setup teknikal yang terdeteksi wajib lolos sensor filter AI Groq sebelum dieksekusi ke bursa.

### C. Manajemen Pengaman & Kunci Profit (Win Rate >75%)
* **`strategy_mode` = "SCALPING"**
  * Mengaktifkan mode scalping dengan target profit cepat.
* **`auto_close_roi_percent` = 3.0%**
  * Target keuntungan per transaksi disetel di 3.0% (sangat realistis dicapai harian).
* **`fast_trailing_enabled` = true**
  * Mengaktifkan fitur pengunci profit instan.
  * **`fast_trailing_trigger_roi_percent` = 0.9%**
  * **`fast_trailing_callback_roi_percent` = 0.25%**
  * *Mekanisme:* Ketika posisi profit menyentuh `0.9%`, Stop Loss otomatis dipindah ke area profit terkunci (`+0.65%`). Jika harga langsung berbalik turun, transaksi ditutup dalam keadaan **tetap untung**, menjaga rasio kemenangan (win rate) di atas 75%.
* **`trailing_enabled` = true**
  * **`trailing_trigger_roi_percent` = 2.5%**
  * **`trailing_callback_roi_percent` = 0.8%**
  * Menjaga keuntungan jika harga melesat jauh melampaui target awal tanpa mengalami koreksi besar.

---

## 3. Cara Kerja Sistem Penilai AI (Groq)
1. **Penyaringan Pertama (Teknikal)**: Algoritma memeriksa EMA, slope indikator, dan ATR untuk koin dalam daftar pantau.
2. **Penyaringan Kedua (AI)**: Jika ada kecocokan teknikal, data dikirim ke Groq Llama 3.1 8B untuk dianalisis pola grafik dan momentumnya.
3. **Eksekusi**: Jika AI memberikan skor keyakinan di atas `0.55`, order posisi dikirim langsung ke Binance Testnet.

---

## 4. Tips Pemeliharaan & Pemantauan
1. **Akses Dashboard**: Buka browser Anda di `http://127.0.0.1:5000` menggunakan username `admin` dan password `Avada2404@`.
2. **Monitor Posisi Aktif**: Anda bisa memantau pergerakan floating PNL dan status trailing stop secara real-time pada tab dashboard utama.
3. **Cek Log**: Log aktivitas detail dicatat secara berkala pada file `out.log` dan setiap error dicatat pada `err.log`.
