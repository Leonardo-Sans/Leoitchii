@echo off
setlocal
cd /d "%~dp0"
if not exist "%~dp0lichii.exe" (
  echo ERRO: copie este CMD para a mesma pasta de lichii.exe.
  pause
  exit /b 2
)
rem Diagnostico, sem modificar como o jogo roda.
set "EDEN_NX2_TC_LOG=1"
echo Leoitchii - diagnostico do cache de texturas ativado.
echo Carregue um save, observe Kokiri por ao menos 60 segundos, vire a camera
echo varias vezes e anote FPS, uso de VRAM dedicada e memoria compartilhada.
echo A execucao normal do jogo nao e alterada.
start "" /D "%~dp0" "%~dp0lichii.exe" %*
endlocal
