@echo off
chcp 65001 >nul
setlocal
echo ===============================================================
echo LEOITCHII - EXPERIMENTO DE NEBLINA / SHADER COMPUTE (ALTO RISCO)
echo ===============================================================
echo Este teste NAO remove automaticamente somente a neblina.
echo O shader identificado como fog tambem pode fazer composicao.
echo Pode causar ceu escuro, efeitos ausentes ou falha visual.
echo Nao altera saves, configuracoes ou arquivos do jogo.
echo Nao use como perfil padrao. Compare a mesma cena com lichii.exe.
echo.
choice /C SN /N /M "Deseja ativar o teste SOMENTE nesta inicializacao? [S/N] "
if errorlevel 2 exit /b 0
set "EDEN_NX2_REJECT_HASH=780c0536b89fc89e"
set "EDEN_NX2_TRANSCODE_THREADS=2"
set "EDEN_NX2_VDEC_PACE=1"
start "" /D "%~dp0" "%~dp0lichii.exe" %*
endlocal
