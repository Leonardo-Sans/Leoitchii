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
echo Rode testes na mesma cena/situacao, fechando o jogo entre eles.
echo Nada e persistido; saves, shaders e configuracoes nao sao apagados.
echo Cada opcao inicia uma UNICA execucao; abra este CMD novamente para outra.
echo.
echo [1] Log VRAM/cache de texturas (sem mudanca funcional)
echo [2] Desativar fast path de aliases de texturas
echo [3] Desativar liberacao antecipada da IR compute
echo [4] Desativar preload de Mesh fallback
echo [5] Desativar sincronismo opcional Eglantine do video
echo [6] Perfil conservador 2+3 juntos (investigar crashes)
echo [7] Reversao ampla 2+3+4+5 (somente para diagnostico)
echo [8] Resumo de falhas Windows (Event ID 1000, ultimas 48h)
echo [Q] Sair
choice /C 12345678Q /N /M "Opcao: "
if errorlevel 9 exit /b 0
if errorlevel 8 goto EVENTS
if errorlevel 7 goto CONSERVATIVE
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
:CONSERVATIVE
set "LEOITCHII_ALIAS_FAST=0"
set "LEOITCHII_IR_EARLY_FREE=0"
set "LEOITCHII_MESH_DISK_CACHE=0"
set "EDEN_NX2_VDEC_PACE=0"
echo Reversao ampla de quatro otimizacoes v0.6 (nao e configuracao recomendada).
echo Preload foi desligado; fallback Mesh compute continua disponivel.
goto LAUNCH
:EVENTS
echo.
echo Resumo local e somente leitura do Event Log do Windows.
echo Nao exibe caminhos, nomes de usuario, chaves ou dados de jogos.
echo Apenas data, nome do executavel, modulo, codigo e offset de falha.
powershell.exe -NoProfile -Command ^
  "$events = @(Get-WinEvent -FilterHashtable @{LogName='Application'; Id=1000; StartTime=(Get-Date).AddDays(-2)} -ErrorAction SilentlyContinue); $hits = @($events | Where-Object { $_.Properties.Count -ge 8 -and [string]$_.Properties[0].Value -match '^(lichii|eden-cli)\.exe$' } | ForEach-Object { $v = $_.Properties; [pscustomobject]@{ Data = $_.TimeCreated.ToString('yyyy-MM-dd HH:mm:ss'); Executavel = [IO.Path]::GetFileName([string]$v[0].Value); Modulo = [IO.Path]::GetFileName([string]$v[3].Value); Excecao = [string]$v[6].Value; Offset = [string]$v[7].Value } }); if ($hits.Count -eq 0) { Write-Host 'Nenhum crash Event ID 1000 de lichii.exe ou eden-cli.exe nas ultimas 48 horas.' } else { $hits | Format-Table -AutoSize }"
if errorlevel 1 echo Aviso: nao foi possivel ler o log; confira no Monitor de Confiabilidade (Win+R, perfmon /rel).
echo.
echo Este resumo NAO substitui eden_log.txt ou dump de crash.
pause
goto MENU
:LAUNCH
start "" /D "%~dp0" "%~dp0lichii.exe" %*
endlocal