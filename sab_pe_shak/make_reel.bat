@echo off
REM Ek Part ki reel:  make_reel SS-001 1
cd /d "%~dp0"
py -u sps.py %*
pause
