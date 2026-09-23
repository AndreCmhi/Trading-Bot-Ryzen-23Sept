@echo off
setlocal
cd /d "%~dp0"

:: Cek python tersedia
where python >nul 2>nul
if errorlevel 1 (
    echo ERROR: Python tidak ditemukan di PATH.
    pause
    exit /b 1
)

:: Cek apakah bot sudah jalan (port 5000 aktif)
powershell -NoProfile -Command "if (Get-NetTCPConnection -LocalPort 5000 -State Listen -ErrorAction SilentlyContinue) { exit 0 } else { exit 1 }" >nul 2>nul
if not errorlevel 1 (
    echo Bot sudah berjalan. Membuka dashboard...
    start "" "http://127.0.0.1:5000"
    exit /b 0
)

:: Jalankan bot di background - fully hidden, log ke out.log & err.log
powershell -NoProfile -WindowStyle Hidden -Command ^
    "Start-Process python -ArgumentList 'app.py' -WorkingDirectory '%~dp0' -WindowStyle Hidden ^
     -RedirectStandardOutput '%~dp0out.log' -RedirectStandardError '%~dp0err.log'"

:: Tunggu Flask siap (cek port 5000, max 15 detik)
set /a tries=0
:waitloop
powershell -NoProfile -Command "if (Get-NetTCPConnection -LocalPort 5000 -State Listen -ErrorAction SilentlyContinue) { exit 0 } else { exit 1 }" >nul 2>nul
if not errorlevel 1 goto ready
set /a tries+=1
if %tries% geq 15 goto timeout
timeout /t 1 /nobreak >nul
goto waitloop

:ready
echo Bot berjalan. Membuka dashboard...
start "" "http://127.0.0.1:5000"
echo Dashboard: http://127.0.0.1:5000
echo Log      : %~dp0out.log
goto done

:timeout
echo Bot lambat start - cek %~dp0err.log jika ada masalah.
start "" "http://127.0.0.1:5000"

:done
endlocal

