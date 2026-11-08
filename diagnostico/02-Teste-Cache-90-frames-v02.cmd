@echo off
setlocal
cd /d "%~dp0"
if not exist "%~dp0lichii.exe" (
  echo ERRO: copie este CMD para a mesma pasta de lichii.exe.
  pause
  exit /b 2
)
echo ===============================================================
echo TESTE DE VRAM - retencao de texturas recentes por 90 frames
echo ===============================================================
echo Este teste pode reduzir recargas ao virar a camera, MAS em 4 GB
echo tambem pode esgotar a VRAM e causar travamentos/imagens pretas.
echo Nao e recomendado como configuracao permanente. Em caso de piora,
echo feche e execute lichii.exe normalmente.
echo.
choice /C SN /N /M "Ativar apenas nesta execucao? [S/N] "
if errorlevel 2 exit /b 0
set "EDEN_NX2_TC_LOG=1"
set "EDEN_NX2_TC_MIN_AGE=90"
start "" /D "%~dp0" "%~dp0lichii.exe" %*
endlocal
