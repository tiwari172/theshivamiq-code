@echo off
cd /d "%~dp0"
py scheduler.py --max 1
pause
