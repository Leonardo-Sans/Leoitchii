@echo off
setlocal
cd /d "%~dp0"
if not exist "%~dp0lichii.exe" (
  echo ERRO: copie este CMD ao lado de lichii.exe da v0.6.
  pause
  exit /b 2
)
:MENU
cls
echo =====================================================
echo LEOITCHII v0.6 - ISOLAR CRASHES E AUDIO SEM RECOMPILAR
echo =====================================================
echo Rode testes na mesma cena/situacao, fechando jogo entre eles.
echo Nada e persistido; saves e shaders nao sao apagados.
echo.
echo [1] Log VRAM/cache de texturas (sem mudanca funcional)
echo [2] Desativar fast path de aliases de texturas
echo [3] Desativar liberacao antecipada da IR compute
echo [4] Desativar preload de Mesh fallback
echo [5] Desativar sincronismo opcional Eglantine do video
echo [6] Perfil conservador 2+3 juntos (se crashes continuam)
echo [Q] Sair
choice /C 123456Q /N /M "Opcao: "
if errorlevel 7 exit /b 0
if errorlevel 6 goto COMBINED
if errorlevel 5 goto NOPACE
if errorlevel 4 goto MESH
if errorlevel 3 goto IR
if errorlevel 2 goto ALIAS
goto MONITOR
:MONITOR
set "EDEN_NX2_TC_LOG=1"
echo Apenas monitora texture cache em log.
goto LAUNCH
:ALIAS
set "LEOITCHII_ALIAS_FAST=0"
echo Mantem caminho antigo de sincronia de alias.
goto LAUNCH
:IR
set "LEOITCHII_IR_EARLY_FREE=0"
echo Mantem IR ate o termino da compilacao do pipeline.
goto LAUNCH
:MESH
set "LEOITCHII_MESH_DISK_CACHE=0"
echo Desativa preload Mesh experimental, NAO a emulacao Mesh.
goto LAUNCH
:NOPACE
set "EDEN_NX2_VDEC_PACE=0"
echo Teste de pacing dos videos sem descarte; sincronismo pode piorar.
goto LAUNCH
:COMBINED
set "LEOITCHII_ALIAS_FAST=0"
set "LEOITCHII_IR_EARLY_FREE=0"
echo Perfis alias/IR experimentais desativados para comparacao.
goto LAUNCH
:LAUNCH
start "" /D "%~dp0" "%~dp0lichii.exe" %*
endlocal
