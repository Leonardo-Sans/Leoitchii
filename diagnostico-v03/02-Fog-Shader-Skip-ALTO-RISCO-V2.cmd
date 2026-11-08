@echo off
setlocal
if not exist "%~dp0lichii.exe" (
  echo ERRO: coloque este arquivo junto de lichii.exe DA V0.2.
  pause
  exit /b 2
)
echo ==========================================================
echo Leoitchii v0.2 - EXPERIMENTO DE REJEICAO DE SHADER (RISCO)
echo ==========================================================
echo NAO remove a neblina com seguranca.
echo Rejeita UM shader COMPUTE 780c0536b89fc89e, associado
echo a fog no codigo original. Pode quebrar composicao, agua,
echo ceu, cor ou causar tela preta; tambem pode nao fazer nada.
echo.
echo Use SOMENTE para identificar se esse shader custa FPS.
echo Nao use no seu perfil normal. Feche e abra lichii.exe
echo normalmente para desativar. Nao apague shaders nem saves.
echo.
choice /C SN /N /M "Prosseguir com o teste de alto risco? [S/N] "
if errorlevel 2 exit /b 0
set "EDEN_NX2_REJECT_HASH=780c0536b89fc89e"
start "" /D "%~dp0" "%~dp0lichii.exe" %*
endlocal
