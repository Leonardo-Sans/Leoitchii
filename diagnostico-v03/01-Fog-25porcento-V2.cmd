@echo off
setlocal
if not exist "%~dp0lichii.exe" (
  echo ERRO: coloque este arquivo junto de lichii.exe DA V0.2.
  pause
  exit /b 2
)
echo ===================================================
echo Leoitchii v0.2 - TESTE FOG/EXPOSICAO 25/65
echo ===================================================
echo ESTE NAO E UM MOD PARA REMOVER NEBLINA.
echo Ativa workaround experimental de shader do proprio Fritchii:
echo - Fog identificado: multiplicador 0.25;
echo - Exposicao identificada: multiplicador 0.65.
echo Pode escurecer a cena. Pode NAO afetar a neblina no chao.
echo Sera revertido ao iniciar normalmente sem este arquivo.
echo.
choice /C SN /N /M "Ativar apenas nesta execucao? [S/N] "
if errorlevel 2 exit /b 0
set "EDEN_NX2_OOT_VISUAL_WORKAROUND=1"
start "" /D "%~dp0" "%~dp0lichii.exe" %*
endlocal
