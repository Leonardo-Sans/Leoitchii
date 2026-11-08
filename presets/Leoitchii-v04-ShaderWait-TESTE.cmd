@echo off
setlocal
if not exist "%~dp0lichii.exe" (
  echo ERRO: coloque este arquivo ao lado de lichii.exe.
  pause
  exit /b 2
)
echo ============================================================
echo TESTE DIAGNOSTICO: esperas por shaders em compilacao
echo ============================================================
echo Pode diminuir objetos ausentes ou pretos, mas causar pausas
echo muito longas quando shaders novos aparecem. Teste apenas
echo depois de fazer backup e anotar o FPS da v0.2 e v0.4 normal.
echo Basta fechar e iniciar lichii.exe normalmente para reverter.
echo.
choice /C SN /N /M "Executar teste de espera de shaders? [S/N] "
if errorlevel 2 exit /b 0
set "EDEN_NX2_ASYNC_DISCARD=0"
start "" /D "%~dp0" "%~dp0lichii.exe" %*
endlocal
