@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set PY=python
where py >nul 2>nul && set PY=py
echo theshivamiq - REEL STATUS (kuch nahi badalta, sirf dekhta hai)
echo.
%PY% reel_status.py --report %*
echo.
if exist "output\REEL STATUS.html" start "" "output\REEL STATUS.html"
pause
