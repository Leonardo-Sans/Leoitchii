@echo off
setlocal
cd /d "%~dp0"
if not exist "%~dp0Leoitchii.exe" (
  echo ERROR: Place this .cmd in the same folder as Leoitchii.exe.
  pause
  exit /b 2
)
:MENU
cls
echo ================================================
echo LEOITCHII v0.7 - SAFE A/B (NO REBUILD)
echo ================================================
echo Only affects the emulator launched by this file.
echo Does not delete saves, cache, firmware or settings.
echo.
echo 1 - Normal (same defaults as normal Leoitchii.exe)
echo 2 - Texture cache diagnostics (log, may cost FPS)
echo 3 - Disable zero-page RAM trimming for this run
echo 4 - Combine texture log and RAM trim off
echo Q - Exit
echo.
choice /C 1234Q /N /M "Choose: "
if errorlevel 5 exit /b 0
if errorlevel 4 goto BOTH
if errorlevel 3 goto TRIMOFF
if errorlevel 2 goto LOG
goto RUN
:LOG
set "EDEN_NX2_TC_LOG=1"
goto RUN
:TRIMOFF
set "LEOITCHII_ZERO_TRIM=0"
goto RUN
:BOTH
set "EDEN_NX2_TC_LOG=1"
set "LEOITCHII_ZERO_TRIM=0"
goto RUN
:RUN
echo Starting Leoitchii v0.7; changes only last until close.
start "" /D "%~dp0" "%~dp0Leoitchii.exe" %*
endlocal
