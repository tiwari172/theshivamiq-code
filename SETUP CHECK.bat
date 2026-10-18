@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set PY=python
where py >nul 2>nul && set PY=py
echo theshivamiq - SETUP CHECK
echo.
%PY% doctor.py
echo.
echo   music nahi hai aur Common se copy karni ho to "fix" likho, warna bas Enter dabao.
set /p FIX="> "
if /i "%FIX%"=="fix" %PY% doctor.py --fix
echo.
pause
