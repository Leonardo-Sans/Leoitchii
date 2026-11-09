# Leoitchii — auditoria de atualizações upstream (09/11/2026)

**Objetivo:** escolher correções úteis antes da primeira build Windows da v0.7 e preservar baseline v0.5/v0.6, menu reversível (#10), fallback Mesh Compute da GTX 1050 Ti e saves. **Este documento registra análise de upstream, não integração de código ou validação em GTX 1050 Ti.**

## Versões e bases conferidas

| Projeto | Estado consultado em 09/11/2026 | Código do Leoitchii |
|---|---|---|
| [Fritchii](https://github.com/Frizti/Fritchii/releases/tag/fritchii-v5.4) | v5.4, 09/11/2026 12:32 UTC. A v5.2 introduziu fallback Mesh Compute para GTX 10 series e anteriores | Base atual ainda é **Fritchii v4.1** em commit fixo f6d42b8 |
| [Lichii](https://github.com/zortos293/Lichii/releases/tag/build-125) | build-125 é último release examinado; branch nx2 já tem **13 commits posteriores**, incluindo #1014, #1016, #1028 | Ports seletivos #569/#642/#879/#880/#858/#296/#878, não upgrade completo |
| [Eglantine](https://github.com/Eglantine-Community/Eglantine/releases/tag/daily-20261109) | daily-20261109 (release de 09/11) e alteração para vídeo Zelda de 60 FPS, ainda experimental | Somente cherry-pick de pacing 1f52ac7 integrado à v0.6 |
| [Eden](https://git.eden-emu.dev/eden-emu/eden/releases) | v0.2.1 estável publicada 01/06/2026; mais antigo e genérico para esta triagem | Não migrar base |

**Diferença estrutural:** Fritchii v4.1 -> v5.4 contém **272 commits à frente, 4 atrás e 274 arquivos alterados na comparação do GitHub**. Um rebase completo exigiria readaptação de scripts de Fritchii v4.1 e do menu Leoitchii; **não assumir compatibilidade só porque os dois possuem Mesh fallback**.

## Matriz de decisões para a v0.7

| Prioridade | Origem, evidência | Benefício pretendido | Dependências e decisão |
|---|---|---|---|
| **P0 — investigar e preparar port seletivo** | [Fritchii v5.2](https://github.com/Frizti/Fritchii/releases/tag/fritchii-v5.2), [commit 464fbb](https://github.com/Frizti/Fritchii/commit/464fbb45bb6b3010db9ebf0e5bf987a9a8e1ad9c) | Recuperar de falha de alocação de staging buffers quando sistema aproxima limite de memória; plausível no Ryzen/16 GB e 4 GB VRAM | Verificar políticas de memória no v4.1/v0.6: já existe #880 para imagens, diferente de staging **buffers**. Portar apenas se possível, com logs e limite de tentativas. Over-budget pode paginar e reduzir FPS; não prometer fim dos crashes. |
| **P0 — testar A/B e portar se reproduzir** | [Eglantine commit f7a902](https://github.com/Eglantine-Community/Eglantine/commit/f7a9027ff17b2e31f8e3d0dccb316b7244de128d) | Não aplicar intervalo forçado de 2 vblanks durante vídeo de 60 FPS (pode ajudar cutscene lenta) | É chamado de **LOCAL TEST** no commit. Já há patch Eglantine de pacing aplicado no arquivo nx2_gsv.h da v0.6; revisar conflito e adicionar rollback específico. **Não há evidência de correção da música**. |
| **P1 — verificar par de commits e evitar port parcial** | [Lichii #979](https://github.com/zortos293/Lichii/pull/979) + [#1014](https://github.com/zortos293/Lichii/pull/1014) | Fim do limite fixo de 32 regiões de semáforos; bug relatado em Bananza e Mario Kart World (140 regiões em 4,4 s no teste upstream) | #1014 **depende de #979**, que restaura Nx2SemaphoreMirror. Fritchii v4.1 e v5.4 **não têm** Nx2SemaphoreMirror no src/video_core/nx2.h; não portar #1014 sozinho. Upstream testou lógica, **ainda sem teste no jogo**. |
| **P1 — triagem e possível port seletivo** | [Fritchii v5.1](https://github.com/Frizti/Fritchii/releases/tag/fritchii-v5.1) e [v5](https://github.com/Frizti/Fritchii/releases/tag/fritchii-v5) | Corrigir fragmentos/sujeira em texto e geometria ausente por clip distances, uso de memória e descarte de cópias | Na GTX 1050 Ti com 4 GB, port de cache e limpeza exige inspeção de ownership/sync, pois pode causar texturas pretas ou crashes. v5.1 também **reverteu uma alteração de GPU writes da v5** por dados obsoletos; não copiar um patch já revertido. |
| **P1 — interface/diagnóstico** | [Fritchii v5](https://github.com/Frizti/Fritchii/releases/tag/fritchii-v5) e [Lichii #951](https://github.com/zortos293/Lichii/commit/b29ef4b583761bdf0ca8a041bdf0ab033a87d281) | Exportar log pelo menu e correlacionar RAM/VRAM do processo, textura, staging e DXGI | Priorizar diagnóstico de baixo impacto e **sem registrar caminhos, chaves e saves**, ligado somente quando pedido. O novo menu Leoitchii v0.7 já tem toggles básicos, mas **não traz ainda exportador nem EDEN_NX2_MEM_TRACE**. |
| **P2 — estudo, não integrar na primeira correção** | [Lichii #1028](https://github.com/zortos293/Lichii/pull/1028) | Async read-back: +17% FPS em OoT num Ryzen 5900X/RTX 3080 no ponto upstream; Bananza praticamente sem ganho | Port extenso de buffer cache/threads, alterações obrigatórias e testes importantes. Não extrapolar +17% para a GTX Pascal; após estabilizar, comparar A/B em build separada ou futura. |
| **P2 — risco de áudio** | [Lichii #1016](https://github.com/zortos293/Lichii/pull/1016) | HostTiming deixa de ocupar quase um núcleo inteiro do PC com timer em sleep OS | Upstream ainda não havia validado áudio; o Leoitchii **já perdeu música na v0.6**. Não incluir até estabilidade/áudio investigados. |
| **P2 — memória e precompile** | [Lichii #961](https://github.com/zortos293/Lichii/commit/2b30c2cb1ceb8f9a6e385b7cea45705dca07b722) e [Fritchii v5](https://github.com/Frizti/Fritchii/releases/tag/fritchii-v5) | Trim de páginas guest zero / preparação antecipada de shaders | Avaliar opt-in, limites de RAM/disco, arquivos de cache versionados, custo no Ryzen 5 5600. O Fritchii v5.4 usa **EDEN_NX2_PRECOMPILE=0** para desativar a precompilação. Evitar impor precompile global para Zelda, Pokopia ou Bananza. |
| **Fora do alvo da GTX** | [Fritchii v5.4](https://github.com/Frizti/Fritchii/releases/tag/fritchii-v5.4) | Adaptação da precompilação de shaders para AMD | Release diz explicitamente **sem alterações na NVIDIA**. Não introduzir patch por versão sem benefício aplicável. |
| **Fora do lote** | [Lichii build 116/117](https://github.com/zortos293/Lichii/releases/tag/build-117) | Problemas específicos AMD e DLSS em RTX | GTX 1050 Ti não tem hardware RTX/DLSS; não ativar recursos não suportados. |

## Decisão recomendada antes de qualquer nova build

1. **Preservar a v0.6 e a v0.5** para A/B. Manter main e branches de teste intactas. A v0.6 ainda não foi aprovada, e o PR #10 tem só validação textual/integrativa do menu, **não build C++ Windows**.
2. **Continuar a v0.7 sobre a base atual Fritchii v4.1**, enquanto isolamos música e crash pelos toggles já preparados. Fazer **análise de compatibilidade em fonte, sem compilar**, dos ports prioritários de buffer OOM (v5.2) e vídeo de 60 FPS (Eglantine f7a902). Só aplicar se as dependências/âncoras e a reversibilidade forem verificadas.
3. **Fritchii v5.4 é uma candidata real à base futura** (já há fallback Mesh Compute da GTX 10; `mesh_emulation.emplace` foi encontrado no código). Para promovê-la a base da v0.7 é preciso antes um **protótipo de integração sem build** que verifique todas as funções do Leoitchii: patches de OOM/cache/ASTC, pacing Eglantine, menu Qt e ícone, caches, arquivos de configuração e ausência de duplicações. Se isso aumentar muito o risco, manter base antiga na v0.7.
4. Somente após fechamento dos ports/gates, habilitar **uma** compilação Windows com metadados Leoitchii e menu, e pedir testes guiados em Zelda (áudio, cutscene, HUD, vila/floresta, RAM/VRAM), Bananza (terreno) e Pokopia (preservar ~60 FPS). Coletar logs do emulador, não apenas eventos genéricos de Sistema.
5. **Não gerar duas builds para comparar fontes** antes de tentar análise de dependências/compatibilidade no CI Linux; não mesclar mudanças enormes de shader/GPU numa etapa sem rollback.

## Fontes e limites

- Fritchii v5.4 tem mesh fallback comprovado na fonte e nas notas, mas **não comprovado no nosso hardware**.
- Eglantine f7a902 foi marcado como **LOCAL TEST**; pode aliviar metade de velocidade em vídeo de 60 FPS, mas o problema atual de música ausente segue aberto.
- Lichii #1014 tem testes automatizados e depende de #979; não foi validado em Bananza no PR consultado.
- Lichii #1028 tem benchmark de 5900X/RTX 3080, não de GTX 1050 Ti.
- Os ganhos de VRAM (8,8 -> 6,4 GB) do Fritchii v5 em RTX 4080 ainda são maiores do que os **4 GB físicos** da nossa GTX: não prometer FPS ou estabilidade a partir deles.
