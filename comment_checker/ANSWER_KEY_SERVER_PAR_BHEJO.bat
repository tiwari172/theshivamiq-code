@echo off
chcp 65001 >nul
echo === answer_key.xlsx (aapke badlaav) aur reel_case_fix.txt server par bhej raha hoon ===
echo (Pehle SERVER_SE_LAO.bat chala kar latest answer_key lo, phir badlo, phir ye chalao)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0server_sync.ps1" up
pause
