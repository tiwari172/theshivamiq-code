@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo theshivamiq - ElevenLabs
echo.
echo   test   = key aur credits check
echo   fixed  = CTA + Signature (Common folder)
echo   sfx    = sound effects (sfx_list.txt se)
echo   ya category number likho (jaise 1)
echo.
set /p CAT="Kya karna hai: "
if /i "%CAT%"=="test" goto run1
if /i "%CAT%"=="fixed" goto run1
if /i "%CAT%"=="sfx" goto run1
set /p STORY="Story number (jaise 9 ya 9-12): "
python eleven_voice.py %CAT% %STORY%
goto end
:run1
python eleven_voice.py %CAT%
:end
echo.
pause
