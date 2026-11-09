@echo off
setlocal
cd /d "%~dp0"
if not exist "%~dp0lichii.exe" (
  echo ERRO: copie este arquivo na pasta da V0.5, ao lado de lichii.exe.
  pause
  exit /b 2
)
echo ============================================================
echo LEOITCHII GTX 1050 Ti - TESTE DE BLOOM SEM NOVA COMPILACAO
echo ============================================================
echo Testa remover apenas os shaders de upsample de bloom que foram
echo identificados em um relatorio da comunidade Lichii (issue #101).
echo.
echo ATENCAO: NAO e remover toda a neblina do chao.
echo Pode alterar brilho, agua/rios, transparencias ou outros efeitos.
echo O ganho de FPS nao foi confirmado; apenas um teste A/B.
echo Nenhuma mudanca e salva nas preferencias ou no jogo.
echo Fechar e iniciar lichii.exe normalmente reverte o experimento.
echo.
choice /C SN /N /M "Iniciar teste experimental de bloom? [S/N] "
if errorlevel 2 exit /b 0
set "EDEN_NX2_REJECT_HASH=f2b14c43ca0e4300,96dd01c5b0361fcb"
start "" /D "%~dp0" "%~dp0lichii.exe" %*
endlocal
