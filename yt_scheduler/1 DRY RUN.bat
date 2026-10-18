@echo off
cd /d "%~dp0"
py scheduler.py --dry-run
pause
