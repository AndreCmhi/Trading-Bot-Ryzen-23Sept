# Penjelasan Efek Penonaktifan Filter Tren & Pullback

Dokumen ini menjelaskan risiko dan konsekuensi teknis jika Anda menonaktifkan fitur pengaman utama pada bot trading Ryzen.

## 1. Jika Menonaktifkan Filter Tren (`disable_trend_filter` = true)
* **Melawan Arus Pasar**: Bot akan melakukan order **BUY/LONG** saat pasar sedang tren turun (Bearish) atau **SELL/SHORT** saat tren sedang naik tajam (Bullish).
* **Posisi Nyangkut / Floating Loss**: Tanpa filter arah tren global (seperti EMA), bot rentan membeli aset yang terus merosot nilainya (falling knife).
* **Win Rate Anjlok**: Rasio kemenangan yang ditargetkan di atas 75% akan turun drastis karena banyak posisi langsung terkena *Hard Stop Loss*.

## 2. Jika Menonaktifkan Filter Pullback (`disable_pullback_filter` = true)
* **Membeli di Pucuk / Short di Lembah**: Bot tidak akan menunggu harga "diskon" (koreksi sementara) sebelum masuk ke pasar. Order langsung dieksekusi saat mendeteksi tren aktif.
* **Drawdown Lebih Besar**: Karena masuk tanpa harga optimal, posisi Anda kemungkinan besar akan langsung mengalami *floating minus* besar sebelum/jika harga berlanjut searah tren.
* **Rasio Risk-to-Reward Buruk**: Jarak entri ke target profit menjadi kurang efisien, membuat performa scalping menjadi tidak stabil dan tidak konsisten.
