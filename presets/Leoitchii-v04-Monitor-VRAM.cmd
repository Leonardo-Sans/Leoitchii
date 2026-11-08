@echo off
setlocal
if not exist "%~dp0lichii.exe" (
  echo ERRO: coloque este arquivo ao lado de lichii.exe.
  pause
  exit /b 2
)
rem Somente habilita estatisticas periodicas de cache de textura.
set "EDEN_NX2_TC_LOG=1"
echo Monitor de VRAM/texture cache habilitado (dados no log normal).
start "" /D "%~dp0" "%~dp0lichii.exe" %*
endlocal
