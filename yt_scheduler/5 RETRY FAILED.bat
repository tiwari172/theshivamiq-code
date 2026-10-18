@echo off
cd /d "%~dp0"
py scheduler.py --retry-failed
pause
