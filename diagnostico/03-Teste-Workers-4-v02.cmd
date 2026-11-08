@echo off
setlocal
cd /d "%~dp0"
if not exist "%~dp0lichii.exe" (
  echo ERRO: copie este CMD para a mesma pasta de lichii.exe.
  pause
  exit /b 2
)
rem Ryzen 5 5600: 12 threads logicas. No Fritchii v4.1 o padrao sao 3 workers.
rem Este A/B apenas testa 4; GPU ASTC->BCn continua ativa.
set "EDEN_NX2_TC_LOG=1"
set "EDEN_NX2_TRANSCODE_THREADS=4"
echo Teste com 4 threads de conversao de texturas.
echo Se aparecerem mais engasgos, use lichii.exe normalmente.
start "" /D "%~dp0" "%~dp0lichii.exe" %*
endlocal
