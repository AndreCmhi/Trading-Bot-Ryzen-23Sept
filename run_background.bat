@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0"

set LOG_FILE=bot_%date:~-4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%%time:~6,2%.log
set LOG_FILE=!LOG_FILE: =0!
set LOG_FILE=!LOG_FILE:/=-!

echo Starting Trading Bot in background...
echo Log file: !LOG_FILE!

start "Trading Bot Ryzen" /MIN cmd /c "python app.py >> !LOG_FILE! 2>&1"

timeout /t 5 /nobreak >nul

echo Bot started in background.
echo Check dashboard: http://127.0.0.1:5000
echo Log file: !LOG_FILE!

endlocal
