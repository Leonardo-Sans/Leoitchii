@echo off
setlocal
cd /d "%~dp0"
if not exist "%~dp0lichii.exe" (
  echo ERRO: coloque este CMD junto de lichii.exe da v0.6.
  pause
  exit /b 2
)
echo Leoitchii v0.6: teste sem liberacao antecipada de IR compute.
echo Use para comparar RAM e tempo da compilacao de shaders.
set "LEOITCHII_IR_EARLY_FREE=0"
start "" /D "%~dp0" "%~dp0lichii.exe" %*
endlocal
