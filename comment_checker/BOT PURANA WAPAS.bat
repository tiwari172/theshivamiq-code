@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo theshivamiq - bot ka PURANA code wapas (sabse naye backup se)
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0server_update.ps1" wapas
echo.
pause
