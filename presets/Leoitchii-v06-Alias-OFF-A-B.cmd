@echo off
setlocal
cd /d "%~dp0"
if not exist "%~dp0lichii.exe" (
  echo ERRO: coloque este CMD ao lado do lichii.exe da v0.6.
  pause
  exit /b 2
)
echo =======================================================
echo Leoitchii v0.6 - TESTE de alias acelerado (OFF)
echo =======================================================
echo Esse teste desliga apenas a otimizacao de alias Lichii #858.
echo Mantem o decoder ASTC, VRAM, AV1 e fallback mesh da v0.6.
echo Use a mesma cena de DK Bananza para A/B e compare Game FPS.
echo Fechar e iniciar lichii.exe normalmente restaura o fast alias.
set "LEOITCHII_ALIAS_FAST=0"
start "" /D "%~dp0" "%~dp0lichii.exe" %*
endlocal
