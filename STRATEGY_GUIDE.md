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
---

## 3. 5 Indikator Konfirmasi Trade

Gunakan indikator ini sebagai konfirmasi, bukan keputusan tunggal.

### 1. Volume
* Volume tinggi = move kuat.
* Volume rendah = potensi fake move.
* Aturan kerja: bandingkan volume candle sekarang dengan volume rata-rata candle sebelumnya.

### 2. VWAP (Volume Weighted Average Price)
* Harga di atas VWAP = bullish.
* Harga di bawah VWAP = bearish.
* Aturan kerja: `price > VWAP` untuk bias naik, `price < VWAP` untuk bias turun.

### 3. RSI (Relative Strength Index)
* RSI di atas 50 = bullish momentum.
* RSI di bawah 50 = bearish momentum.
* Aturan kerja: `RSI > 50` validasi long, `RSI < 50` validasi short.

### 4. EMA 20/50 (Exponential Moving Average)
* Harga di atas EMA = uptrend.
* Harga di bawah EMA = downtrend.
* Aturan kerja: `price > EMA20` dan `price > EMA50` untuk trend naik, kebalikannya untuk trend turun.

### 5. ADX (Average Directional Index)
* ADX di bawah 20 = weak trend.
* 20 - 25 = average.
* Di atas 25 = strong trend.
* Aturan kerja: pakai ADX untuk nilai kekuatan trend, bukan arah.

### Golden Rule
**PRICE ACTION = DECISION**
**INDICATORS = CONFIRMATION**

---

## 4. Cara Kerja Sistem Penilai AI (Groq)
1. **Penyaringan Pertama (Teknikal)**: Algoritma memeriksa EMA, slope indikator, dan ATR untuk koin dalam daftar pantau.
2. **Penyaringan Kedua (AI)**: Jika ada kecocokan teknikal, data dikirim ke Groq Llama 3.1 8B untuk dianalisis pola grafik dan momentumnya.
3. **Eksekusi**: Jika AI memberikan skor keyakinan di atas `0.55`, order posisi dikirim langsung ke Binance Testnet.

---

## 5. Tips Pemeliharaan & Pemantauan
1. **Akses Dashboard**: Buka browser Anda di `http://127.0.0.1:5000` menggunakan username `admin` dan password `Avada2404@`.
2. **Monitor Posisi Aktif**: Anda bisa memantau pergerakan floating PNL dan status trailing stop secara real-time pada tab dashboard utama.
3. **Cek Log**: Log aktivitas detail dicatat secara berkala pada file `out.log` dan setiap error dicatat pada `err.log`.

