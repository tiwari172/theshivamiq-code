@echo off
chcp 65001 >nul
cd /d "%~dp0"
REM CLAUDE.md wale saare command "py" se chalte hain -> yahan bhi wahi (py na ho to python)
set PY=python
where py >nul 2>nul && set PY=py
set CAT=
set STORY=
echo theshivamiq - ElevenLabs
echo.
echo   test   = key aur credits check
echo   fixed  = CTA + Signature (Common folder) - sirf tab banta hai jab file na ho
echo   sfx    = sound effects (sfx_list.txt se)
echo   ya category number likho (jaise 1)
echo.
set /p CAT="Kya karna hai: "
if "%CAT%"=="" goto run1
if /i "%CAT%"=="test" goto run1
if /i "%CAT%"=="fixed" goto run1
if /i "%CAT%"=="sfx" goto run1
set /p STORY="Story number (jaise 9 ya 9-12): "
%PY% eleven_voice.py %CAT% %STORY%
goto end
:run1
%PY% eleven_voice.py %CAT%
:end
echo.
pause
