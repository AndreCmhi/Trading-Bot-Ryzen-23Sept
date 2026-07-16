@echo off
setlocal
cd /d "%~dp0"

REM === Trading Bot Ryzen - Start Hidden ===
REM Jalankan app.py di background (fully hidden), lalu buka dashboard.

:: Cek apakah bot sudah jalan
tasklist /FI "IMAGENAME eq python.exe" 2>nul | findstr /I "python.exe" >nul
if not errorlevel 1 (
    echo Bot sudah jalan. Buka dashboard saja...
    start "" "http://127.0.0.1:5000"
    exit /b 0
)

:: Jalankan bot fully hidden via powershell
powershell -WindowStyle Hidden -Command ^
  "Start-Process -FilePath 'python' -ArgumentList 'app.py' -WorkingDirectory '%~dp0' -WindowStyle Hidden"

echo Bot starting...
timeout /t 4 /nobreak >nul

:: Buka dashboard di browser
start "" "http://127.0.0.1:5000"
echo Dashboard opened: http://127.0.0.1:5000

endlocal
