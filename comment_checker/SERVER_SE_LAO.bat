@echo off
chcp 65001 >nul
echo === Server se leaderboard.xlsx, verified.txt, answer_key.xlsx laptop par la raha hoon ===
echo (laptop wali answer_key ki copy answer_key_backup\ mein rakh di jaati hai)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0server_sync.ps1" down
pause
