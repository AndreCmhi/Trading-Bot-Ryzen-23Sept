@echo off
cd /d "%~dp0"
"C:\Users\Maria Oktavia\AppData\Local\Microsoft\WindowsApps\pwsh.exe" -NoProfile -ExecutionPolicy Bypass -File ".\check_no_new_position_once.ps1" -StateFile ".\watch_no_new_position_30m_state.json"
