@echo off
setlocal
if not exist "%~dp0lichii.exe" (
  echo ERRO: coloque este arquivo ao lado de lichii.exe.
  pause
  exit /b 2
)
rem A/B da v0.4: volta ao filtro antigo do Fritchii, sem alterar saves.
set "LEOITCHII_MESH_DISK_CACHE=0"
echo Leoitchii v0.4: mesh preload desabilitado temporariamente (como na v0.2).
start "" /D "%~dp0" "%~dp0lichii.exe" %*
endlocal
