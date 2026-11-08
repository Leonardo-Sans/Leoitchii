# Leoitchii v0.5 — lote consolidado de melhorias pequenas para GTX 1050 Ti

## Estado e disciplina de builds

- Compilação Windows leva aproximadamente **40 minutos** para o usuário.
- Base testada: **v0.2** `e411ee78` — ~20 FPS na vila com quedas e até 30 FPS em dungeon.
- v0.3 rejeitada: NoSharpening derrubou FPS para ~5 na vila; Game recuperou desempenho.
- v0.4: preload de Mesh Shader via compute, CI iniciado; **não há teste de hardware confirmado**.
- v0.5: **branch de preparação sem disparar Actions em push**. Nenhum executável é criado nesta etapa.
- O lote deverá ser compilado **uma única vez** após revisão das mudanças, com cenários opcionais selecionados em tempo de execução.

## Mudanças de código

1. **Vulkan Mesh descriptor limits (estabilidade)** — port restrito da correção Lichii [#642](https://github.com/zortos293/Lichii/commit/7d3b3a5266c274f70140845b47c5023e0011d5de), contando 1 buffer extra (mesh) ou 4 (task+mesh), com checagem sem overflow. Não prometer ganho de FPS.
2. **Preload Mesh da v0.4** — herdado. Confirmado que a Lichii [#841](https://github.com/zortos293/Lichii/commit/f35b64d24a03a3ae87ad4f00ee8c4ca6623750b4) corrigiu o mesmo filtro obsoleto; em Leoitchii há chave de rollback por driver NVIDIA.
3. **Nenhuma mudança irreversível no tratamento de fog, sombras, texturas ou na resolução default.** Os experimentos são `setlocal` em um único lançador .cmd, sem recompilar nem modificar saves.

## Experimentos de baixo risco relativo

| Opção | Mecanismo real identificado no Fritchii | Hipótese | Possível efeito contrário |
|---|---|---|---|
| ASTC 128 MiB | `EDEN_NX2_ASTC_ARRAY_MIB` em `vk_texture_cache.cpp` | diminui imagens enormes na VRAM | perda de detalhe, artefatos |
| 4 workers | `EDEN_NX2_TRANSCODE_THREADS` em `workers.cpp` | Ryzen folgado pode ajudar a preparar assets | mais contenção de threads |
| Pipeline Clean | `EDEN_NX2_PIPELINE_CLEAN=1` em `vk_pipeline_cache.cpp` | reduz trabalho de lookup/estado | novo caminho pode regredir |
| Pipeline 3500 | `EDEN_NX2_PIPELINE_EVICT_ABOVE` em `vk_pipeline_cache.cpp` | limita gasto de memória de driver com pipelines | recompila ao revisitar |
| Combinação | todas as três primeiras | melhorias complementares | perda de causalidade; usar depois do A/B |

## Diagnósticos de alto risco / não padrão

- `EDEN_NX2_ASYNC_DISCARD=0` — espera por pipelines não prontos; reduz draws omitidos, mas pode gerar pausas prolongadas.
- `EDEN_NX2_TC_MIN_AGE=60` — retém texturas recentes por mais tempo; pode causar pressão de VRAM de 4 GB.
- `LEOITCHII_MESH_DISK_CACHE=0` — restaura comportamento v0.2 quanto a preload.
- `EDEN_NX2_TC_LOG=1` — registra a cada 600 frames: `Texture cache`, uploads, evicções.
- `EDEN_NX2_OOT_VISUAL_WORKAROUND=1` — reduz expressão de fog a 25% e exposição a 65% em shaders conhecidos; **não elimina toda a fog e não reduz trabalho de compute**, portanto apenas diagnóstico visual.

## Ordem única de teste com métricas

Em Kokiri Village (mesmo save, clima, hora, câmera, cache quente), testar: baseline v0.2; v0.4/v0.5 sem flags; ASTC 128; workers 4; CLEAN; combinado; se RAM perto do limite, pipeline 3500; diagnósticos de shader e VRAM por último. Medir média, quedas, 1% low, memória dedicada/compartilhada da GPU, memória do sistema e visibilidade de portas/vegetação.

### Cutscenes

No Switch 2, `Nx2VideoDecoder` usa FFmpeg e inicializa hardware se `nvdec_emulation=Gpu`; para AV1 na GTX Pascal pode retornar a CPU. O pacing da Eglantine evita atraso acumulado, mas não acelera por si só cenas 3D. Comparar `NvdecEmulation::Gpu` e `Cpu` pelo menu, e checar logs de inicialização. Não introduzir frame generation para maquiar FPS real.

### Por que não cortar sombras/fog cegamente

O hash de fog existente no Fritchii representa apenas um shader compute e não foi confirmado que seja a neblina dinâmica visível ao nível do chão. Rejeitar o programa inteiro pode destruir pós-processamento, composição e geometria indireta. É necessário capturar o draw/pass antes de implementar exclusão real e segura.

## Condições para gerar próxima build

- Integrador `scripts/limites-descritores-mesh.py` valida trecho exato e sentinelas do Lichii antes de patch.
- Revisar o workflow v0.5 e habilitar `push` **somente quando o lote estiver fechado**.
- Uma compilação Windows Release por lote, sem builds separadas para opções de benchmark.
- Nunca mesclar em `main` antes de benchmark real e ausência de regressões.
