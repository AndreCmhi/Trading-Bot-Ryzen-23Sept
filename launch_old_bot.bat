@echo off
cd /d "%~dp0"
echo Starting Trading Bot OLD version...
echo Dashboard: http://127.0.0.1:5000
echo Jangan jalankan bersamaan dengan versi Improved pada port yang sama.
start "Trading Bot OLD" cmd /k "python app.py"
