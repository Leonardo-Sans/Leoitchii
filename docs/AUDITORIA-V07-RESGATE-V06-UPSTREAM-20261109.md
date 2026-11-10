# Leoitchii v0.7 — resgate v0.6 e pesquisa upstream (09/11/2026)

**Base:** [PR #13](https://github.com/Leonardo-Sans/Leoitchii/pull/13), Fritchii v5.5 fixado em `4012e5271e278b21cf8f56b97481dac2b777cd0d`, Lichii build-130 #961/#957/#984 e portas próprias do Leoitchii. Branch de trabalho: `lote-v07-resgate-v06-astc-alias`. Não mesclar em main nem substituir a [v0.7 compilada](https://github.com/Leonardo-Sans/Leoitchii/actions/runs/42717709123).

## Comparação concreta dos ports da v0.6 com Fritchii v5.5

| Recurso da v0.6 | Verificado diretamente na fonte v5.5 | Ação |
|---|---|---|
| Lichii #858: `newest_alias_tick` e atalho `SynchronizeAliases` | Não contém campo nem atalho | **Port seletivo nesta branch**; `LEOITCHII_ALIAS_FAST=1` ativa, padrão **0**, desligamento imediato após reinício |
| Lichii #296: leitura ASTC com `GpuGuestMemory` e `ScratchBuffer` | Faz `ReadBlockUnsafe` incondicional no scan | **Port seletivo nesta branch**; `LEOITCHII_ASTC_DIRECT_SCAN=1` ativa, padrão **0** |
| Lichii #296: substituir shader `astc_decoder.comp` | Shader novo da base tem alterações de extents e limites; hash do shader é diferente da v0.6 | **Não sobrescrever shader novo**. O #296 resgatado se limita ao scan sem cópia |
| Lichii #878: `ShaderPools::Free` e liberação de `code` antes de compilação compute síncrona | Já possui `Free`, `std::move(program.info)`, limpa IR e código antes do driver | **Já implementado** pela base, não duplicar; flag antiga `LEOITCHII_IR_EARLY_FREE=0` não serve para desativar o mecanismo Fritchii |
| Lichii #880: queda de memória em imagens comuns | `AllocateImage(..., bool may_fail, ...)` e reintento sem orçamento, backing de RAM antes de desistir; evita imagens inexistentes e controla pressão | **Tratamento novo e diferente**; não porta patch antigo incompatível, não afirma equivalência exata |
| Lichii #642: limite de buffers para fallback Mesh | Base checa buffers por estágio e descriptor set, lança erro específico quando excede | **Já implementado**, não duplicar |
| Fallback Mesh #569 e correções posteriores | `mesh_emulation.emplace`, suporte compute GTX10 | **Já implementado**, preservado |
| Preload Mesh personalizado `LEOITCHII_MESH_DISK_CACHE` v0.4–v0.6 | Base nova prepara shaders e guarda pipeline em formato diferente; recusa registros Mesh se sem extensão porque não são precompiled pipelines reutilizáveis | **Não reaplicar** antiga remoção de filtro: pode criar muito trabalho de shaders sem ganho ou corromper cache |
| Port Eglantine com descarte de quadros da v0.6 | Música da abertura ausente em teste anterior; causa não isolada | **Não reaplicar**. PR #13 tem experimento diferente e desligado de apresentação de vídeo |

**Melhoria externa nova incorporada:** Lichii #807 (diagnóstico de falta de memória no driver): alerta no log quando o compilador Vulkan recebe `VK_ERROR_OUT_OF_HOST_MEMORY` e mostra o uso/limite de memória reportado pelo SO. Esse alerta não libera RAM e não corrige sozinho objetos pretos, mas ajuda a identificar uma possível causa. Só será executado na nova build.\n\n**Política de risco:** atalho de aliases e leitura ASTC não tiveram teste real no Fritchii 5.5; o primeiro pode alterar sincronização de texturas visíveis. Por isso ambos ficam desligados por padrão e são ativados um por vez pelo menu `Leoitchii`, com reinício. Sem apagamento de cache/saves e sem copiar shader antigo.

## Atualizações externas verificadas (9/11/2026)

Fontes: [Fritchii 5.5](https://github.com/Frizti/Fritchii/releases/tag/fritchii-v5.5), [Lichii build-130](https://github.com/zortos293/Lichii/releases/tag/build-130), [Lichii nx2 pós-130](https://github.com/zortos293/Lichii/compare/build-130...nx2), [Eglantine 0.1.0-rc3](https://github.com/Eglantine-Community/Eglantine/releases/tag/v0.1.0-rc3).

- Lichii build-130 ainda é a release mais recente encontrada. A branch `nx2` estava **20 commits à frente** ao consultar (sem release oficial adicional). Não presumir que essa branch esteja testada.
- **Lichii #1079 (6bb6eb4):** evita upload de textura quando as cópias de camadas dos overlaps cobrem integralmente o destino; o relato mediu 13–31ms economizados por array no Mario Kart World. **Fritchii 5.5 não tem `MarkSubresourcesWrittenWhole` nem `CopiesWriteWholeImage` equivalentes**. Prioridade P1 e requer adaptar os utilitários e contratos de `JoinImages`; não portado ainda, cuidado para não perder conteúdo se cobertura for incompleta.
- **Lichii #1143 (d2eaae4):** mantém registros de pointers de storage buffer em gráficos após evict e retradução, evitando ler 0 quando o guest descarta temporariamente o buffer. Possível relevância para desaparecimento de objetos em PCs com VRAM restrita, **não comprovado no Pokopia**. Base Fritchii v5.5 tem outro modelo de shader cache/eviction; requer port robusto de cache, shader environments, pipeline class e testes. Prioridade P1; não portado.
- **Lichii #807 (ffb12c4):** identifica `VK_ERROR_OUT_OF_HOST_MEMORY` em pipelines e imprime RAM commit/limit no Windows. Muito relevante a PCs com 16GB RAM; pode distinguir falha de pipeline e objeto invisível, sem assumir causa. **Port diagnóstico nesta branch**: helper inline `leoitchii_host_memory_failure.h`, chamado nos caminhos de falha de compute e graphics, logado apenas na primeira ocorrência. Não altera o comportamento da GPU; compilação Windows pendente.
- **Lichii #1058 (8086b7f):** libera threads esperando GPU sync após parada. **Já incorporado ao Fritchii 5.5** (`sync_requests_dropped` em `gpu.cpp`), sem novo port.
- FSR3/FSR4/DLSS recentes no Lichii focam hardware AMD/RTX, **não priorizar para GTX 1050 Ti**.
- **Eglantine 688c6fa:** reconstrói compute shader quando slot de ponteiro constante que era nulo passa a apontar para buffer. Upstream documenta vegetação sem folhas no Zelda; pode ser útil no problema de objetos invisíveis, mas é **patch de múltiplos arquivos com sistema de cache divergente** e sem confirmação no Pokopia; P1 para adaptação isolada.
- **Eglantine rc3:** alterações de lowering shader e mesh/warp e novas rotinas. Prioridade P2, dependerá de comparação de pipeline e testes; não aplicar pacote inteiro às cegas.

**Problema Pokopia:** [Lichii issue #602](https://github.com/zortos293/Lichii/issues/602) permanece aberto para móveis invisíveis inclusive em GPU RTX. Não associar a cor branca como causa confirmada sem logs/capturas de pipeline. **Zelda:** em v0.7 Handheld mostra linhas horizontais estáticas, Docked não; intro em 30 FPS parece lenta, 60 FPS corrige vídeo mas piora jogo; PR #13 preparado como A/B sem build.

## Arquivos que o usuário pode reaproveitar diretamente da v0.6

| Tipo | Transferível para a v0.7? | Observação |
|---|---|---|
| Anotações, capturas, logs, documentos e perfis de comparação | Sim | Não mudam emulação |
| `.cmd` de teste com `EDEN_NX2_TC_LOG=1` | **Após trocar** `lichii.exe` por `Leoitchii.exe` | Ligar log pode reduzir FPS; não copiar cegamente o menu completo |
| `.cmd` antigos com `LEOITCHII_ALIAS_FAST=0`, `LEOITCHII_IR_EARLY_FREE=0`, `LEOITCHII_MESH_DISK_CACHE=0` | **Não como port de código** | Na v0.7 compilada os dois últimos não controlam o mecanismo novo; o primeiro só terá significado após nova build com #858 |
| Executáveis `.exe`, DLLs Vulkan/FFmpeg/Qt, drivers, `plugins` de Qt, shaders antigos | **Não** | Versões incompatíveis podem impedir boot, causar regressões e corromper resultado de teste |
| Shader caches e pipelines compilados v0.6 | **Não forçar cópia** | Fritchii v5.5 usa formato e política novos; migração gerenciada pelo programa; preserve caches antigos para rollback |
| `.ini` de configuração gráfica/per-game da v0.6 | **Evitar substituir o arquivo** | Pode reativar EDS3/Disabled, clock errado, resolução e opções antigas; reaplicar valores individualmente após backup |
| Saves, arquivos de mods próprios | Fazer backup; não sobrescrever | As builds podem compartilhar armazenamento do Eden em AppData, e mods podem depender da versão do jogo; não é port de otimização |

**Ferramenta imediata sem recompilar:** [`LEOITCHII-v07-A-B-COMPATIVEL.cmd`](https://github.com/Leonardo-Sans/Leoitchii/blob/lote-v07-resgate-v06-astc-alias/presets/LEOITCHII-v07-A-B-COMPATIVEL.cmd). Baixar como arquivo .cmd e colocar **ao lado do `Leoitchii.exe` atual**. Menu permite execução normal, log de texturas e desligar trim de páginas zeradas; recursos já presentes na v0.7 testada. Não toca em binários, saves ou caches.

## Gates para próxima build consolidada

1. Validação de aplicação dos ports e sintaxe (CI Linux leve).
2. A/B individual na GTX 1050 Ti, com FPS real e imagem. Depois considerar portar #807 e #1079/#1143 em lotes testáveis por código; só construir Windows quando integração consolidada.
3. Comparar mesma cena Zelda (30 FPS gameplay, intro), cidade/dungeon e Pokopia mesa invisível; EDS2, modo Docked, CPU normal, Speed 100%, Game FPS efetivo.
4. Recuperar logs de `VK_ERROR_OUT_OF_HOST_MEMORY`, `VK_ERROR_OUT_OF_DEVICE_MEMORY`, pipeline faltando, decode ASTC/alias, antes de atribuir causa a falta de VRAM.
5. `main` permanece sem alteração e **ZIP v0.7 original não é sobrescrito**. Não eliminar as versões testadas.
