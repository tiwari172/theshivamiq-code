@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set PY=python
where py >nul 2>nul && set PY=py
echo theshivamiq - CODE SYNC (laptop ^<-^> GitHub)
echo.
%PY% code_sync.py %*
echo.
pause
