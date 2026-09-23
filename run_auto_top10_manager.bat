@echo off
setlocal
cd /d "%~dp0"

set MAX_OPEN_POSITIONS=5
set AUTO_TOP10_TARGET_OPEN_POSITIONS=5
set SYMBOL_SCAN_MODE=ALL
set GASING_MODE_ENABLED=true
set GASING_MIN_SCORE=4

where python >nul 2>nul
if errorlevel 1 (
    echo ERROR: Python tidak ditemukan di PATH.
    pause
    exit /b 1
)

powershell -NoProfile -Command "if (Get-NetTCPConnection -LocalPort 5000 -State Listen -ErrorAction SilentlyContinue) { exit 0 } else { exit 1 }" >nul 2>nul
if errorlevel 1 (
    echo Starting dashboard bot...
    powershell -NoProfile -WindowStyle Hidden -Command ^
        "Start-Process python -ArgumentList 'app.py' -WorkingDirectory '%~dp0' -WindowStyle Hidden -RedirectStandardOutput '%~dp0out.log' -RedirectStandardError '%~dp0err.log'"
    timeout /t 5 /nobreak >nul
)

echo Starting AUTO TOP10 manager...
echo Target open positions : 5
echo Take profit ROI       : above 0.5%%
echo Stop loss ROI         : -0.3%% or lower

powershell -NoProfile -WindowStyle Hidden -Command ^
    "Start-Process python -ArgumentList 'auto_top10_manager.py' -WorkingDirectory '%~dp0' -WindowStyle Hidden -RedirectStandardOutput '%~dp0auto_top10_manager.log' -RedirectStandardError '%~dp0auto_top10_manager_err.log'"

echo Running.
echo Dashboard : http://127.0.0.1:5000
echo Bot log   : %~dp0out.log
echo Top10 log : %~dp0auto_top10_manager.log
pause
endlocal
