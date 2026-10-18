@echo off
chcp 65001 >nul
echo === Server se Excel laptop par + naye scripts server par ===
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0server_sync.ps1" both
start "" "%~dp0leaderboard.xlsx"
pause
