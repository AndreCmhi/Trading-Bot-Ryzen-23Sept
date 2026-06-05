@echo off
setlocal
cd /d "%~dp0"

set "DASHBOARD_URL=http://127.0.0.1:5000"

where python >nul 2>nul
if errorlevel 1 (
    echo Python tidak ditemukan di PATH.
    echo Install Python 3.12+, lalu coba lagi.
    pause
    exit /b 1
)

python -m pip show flask >nul 2>nul
if errorlevel 1 (
    echo Install dependency...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Gagal install dependency.
        pause
        exit /b 1
    )
)

start "" "%DASHBOARD_URL%"
python app.py
if errorlevel 1 (
    echo.
    echo App berhenti karena error.
    pause
)

endlocal
