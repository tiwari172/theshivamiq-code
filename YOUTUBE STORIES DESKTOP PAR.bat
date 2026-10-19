@echo off
chcp 65001 >nul
cd /d "%~dp0"
rem "youtube stories" folder ko Desktop par copy karta hai (purani files overwrite nahi, sirf nayi/badli files)
set "DEST=%USERPROFILE%\Desktop\youtube stories"
if not exist "%DEST%" mkdir "%DEST%"
robocopy "youtube stories" "%DEST%" /E /XO /NFL /NDL /NJH /NJS >nul
echo.
echo Ho gaya! Desktop par "youtube stories" folder dekho.
echo.
pause
