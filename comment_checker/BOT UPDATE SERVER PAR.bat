@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo theshivamiq - bot ka naya code server par (backup pehle)
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0server_update.ps1" update
echo.
pause
