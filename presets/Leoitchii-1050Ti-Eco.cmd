@echo off
REM Perfil EXPERIMENTAL GTX 1050 Ti — comparativo de transcodificacao ASTC.
REM Para usar o padrao sem perfil, abra lichii.exe normalmente.
setlocal
set "EDEN_NX2_TRANSCODE_THREADS=2"
set "EDEN_NX2_VDEC_PACE=1"
start "" "%~dp0lichii.exe" %*
endlocal
