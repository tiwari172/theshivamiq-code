@echo off
REM Sirf cover:  make_cover SS-001 1
cd /d "%~dp0"
py -u sps.py cover %*
pause
