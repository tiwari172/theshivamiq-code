@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set PY=python
where py >nul 2>nul && set PY=py
echo theshivamiq - CLEANUP (sirf output\ aur work\ ki purani CHECK / contact sheet / temp files)
echo.
%PY% cleanup.py %*
echo.
set /p DEL="Recycle Bin mein bhejna hai? haan likho (warna Enter): "
if /i "%DEL%"=="haan" %PY% cleanup.py --delete --yes %*
echo.
pause
