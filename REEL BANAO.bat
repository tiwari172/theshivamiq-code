@echo off
cd /d "%~dp0"
echo theshivamiq - cases folder ki saari nayi reels ban rahi hain...
echo.
python make_reel.py %*
echo.
pause
