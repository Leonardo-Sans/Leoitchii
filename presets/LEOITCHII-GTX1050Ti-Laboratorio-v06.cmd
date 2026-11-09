@echo off
setlocal
cd /d "%~dp0"
if not exist "%~dp0lichii.exe" (
  echo ERRO: copie este arquivo para a mesma pasta de lichii.exe da v0.5.
  pause
  exit /b 2
)
:MENU
cls
echo ======================================================
echo LEOITCHII GTX 1050 TI / 4GB - LABORATORIO DE TESTES
echo ======================================================
echo Cada opcao vale somente ate fechar o jogo.
echo Nao modifica saves, firmware, shader cache ou INI.
echo Deixe OoT anti-aliasing em GAME, nunca NoSharpening.
echo.
echo [1] Original / comparacao
echo [2] Texturas grandes mais leves (limite ASTC 128 MiB)
echo [3] Mais CPU para transcodificacao (4 workers)
echo [4] Consulta de pipelines otimizada (CLEAN)
echo [5] Menos RAM para pipelines antigos (3500 max)
echo [6] Perfil combinado: 128 MiB + 4 workers + CLEAN
echo [7] Diagnostico: shader pendente, esperar (pode travar!)
echo [8] Diagnostico: reter textura por 60 frames (VRAM!)
echo [9] Comparar sem preload Mesh v0.4 (reversao)
echo [A] Neblina experimental Fritchii (pode mudar exposicao)
echo [B] Apenas registrar uso de VRAM / texturas
echo [C] Teste reversivel: desabilitar alias otimizado
echo [D] Teste reversivel: desabilitar economia de RAM na compilacao IR
echo [E] Teste visual: remover bloom (alto risco de imagem alterada)
echo [Q] Sair
echo.
choice /C 123456789ABCDEQ /N /M "Escolha: "
if errorlevel 15 exit /b 0
if errorlevel 14 goto BLOOM
if errorlevel 13 goto IROFF
if errorlevel 12 goto ALIASOFF
if errorlevel 11 goto MEMORYLOG
if errorlevel 10 goto FOG
if errorlevel 9 goto DISABLECACHE
if errorlevel 8 goto TEXTURERETAIN
if errorlevel 7 goto SHADERWAIT
if errorlevel 6 goto COMBINED
if errorlevel 5 goto PIPELINELOW
if errorlevel 4 goto CLEAN
if errorlevel 3 goto WORKERS
if errorlevel 2 goto ASTC128
goto BASE

:ASTC128
set "EDEN_NX2_ASTC_ARRAY_MIB=128"
echo Teste: texturas ASTC enormes limitadas a 128 MiB em vez de 256 MiB.
echo Pode perder nitidez dos mipmaps, ou ter problemas visuais. Nao modifica saves.
goto LAUNCH
:WORKERS
set "EDEN_NX2_TRANSCODE_THREADS=4"
echo Teste: 4 threads na transcodificacao vs 3 no padrao do Ryzen 5 5600.
goto LAUNCH
:CLEAN
set "EDEN_NX2_PIPELINE_CLEAN=1"
echo Teste: evitar trabalho redundante na selecao de pipelines Vulkan.
goto LAUNCH
:PIPELINELOW
set "EDEN_NX2_PIPELINE_EVICT_ABOVE=3500"
echo Teste: liberar pipelines antigos quando ha mais de 3500.
echo Pode aumentar recompilacao ao revisitar areas.
goto LAUNCH
:COMBINED
set "EDEN_NX2_ASTC_ARRAY_MIB=128"
set "EDEN_NX2_TRANSCODE_THREADS=4"
set "EDEN_NX2_PIPELINE_CLEAN=1"
echo Perfil combinado SOMENTE para comparar depois dos testes isolados.
goto LAUNCH
:SHADERWAIT
echo Pode causar paradas longas.
choice /C SN /N /M "Aguardar shaders em vez de omitir draw temporario? [S/N] "
if errorlevel 2 goto MENU
set "EDEN_NX2_ASYNC_DISCARD=0"
goto LAUNCH
:TEXTURERETAIN
echo Pode saturar os 4 GB de VRAM e provocar falhas de alocacao.
choice /C SN /N /M "Reter texturas 60 frames? [S/N] "
if errorlevel 2 goto MENU
set "EDEN_NX2_TC_MIN_AGE=60"
goto LAUNCH
:DISABLECACHE
set "LEOITCHII_MESH_DISK_CACHE=0"
echo Preload do fallback Mesh desativado temporariamente para A/B.
goto LAUNCH
:FOG
echo Este workaround modifica opacidade de um shader fog e exposicao.
echo NAO desliga o pass nem garante eliminar a fog dinamica do chao.
echo Pode alterar cores sem ganhar FPS.
choice /C SN /N /M "Ativar efeito visual de diagnostico? [S/N] "
if errorlevel 2 goto MENU
set "EDEN_NX2_OOT_VISUAL_WORKAROUND=1"
goto LAUNCH
:MEMORYLOG
set "EDEN_NX2_TC_LOG=1"
echo Log de VRAM e texturas ativado (a cada 600 frames).
goto LAUNCH
:ALIASOFF
set "LEOITCHII_ALIAS_FAST=0"
echo Desativa o fast path de aliases da v0.6 (teste A/B, nao remove ASTC).
goto LAUNCH
:IROFF
set "LEOITCHII_IR_EARLY_FREE=0"
echo Desativa apenas a liberacao antecipada de IR nos shaders compute.
goto LAUNCH
:BLOOM
echo Remove shaders de bloom identificados em outro hardware.
echo Pode alterar agua, brilho, cena e nao garante FPS. NAO remove neblina.
choice /C SN /N /M "Experimentar desativacao temporaria de bloom? [S/N] "
if errorlevel 2 goto MENU
set "EDEN_NX2_REJECT_HASH=f2b14c43ca0e4300,96dd01c5b0361fcb"
goto LAUNCH
:BASE
echo Execucao padrao, sem alteracoes.
:LAUNCH
start "" /D "%~dp0" "%~dp0lichii.exe" %*
endlocal
