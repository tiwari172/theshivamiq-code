@echo off
cd /d "%~dp0"
REM CLAUDE.md wale saare command "py" se chalte hain -> yahan bhi wahi (py na ho to python)
set PY=python
where py >nul 2>nul && set PY=py
echo theshivamiq - cases folder ki saari nayi reels ban rahi hain...
echo.
%PY% make_reel.py %*
echo.
pause
