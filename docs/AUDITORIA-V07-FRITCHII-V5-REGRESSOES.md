# Leoitchii — auditoria de regressões v0.6 e Fritchii v5 (09/11/2026)

## Status

- A [v0.6 compilou](https://github.com/Leonardo-Sans/Leoitchii/actions/runs/42547525016) e foi testada pelo usuário com GTX 1050 Ti 4 GB, Ryzen 5 5600 e 16 GB RAM. **Não aprovada para merge**: três crashes e perda de música na abertura.
- **V0.5 é a referência de estabilidade mais recente**, embora já tivesse problemas de stutter e objetos pretos. A v0.2 continua preservada; `main` não deve mudar.
- **Não gerar build de 40 minutos enquanto causas dos crashes e do áudio forem desconhecidas.** Não fazer checkout de base v5 sem revalidar o fallback Mesh.
- Em seis capturas da v0.6 (diferentes câmeras), valores Game FPS no canto inferior direito: **26** a 0,75× área fechada; **16 e 10** a 0,75× exteriores; **8, 8 e 21** a 0,5× em outras áreas/tela de título. Portanto **não** é um A/B controlado no mesmo ângulo; não afirmar que resolução não tem efeito.
- Usuário relata melhora de FPS e de velocidade de carregamento dos elementos pretos; não houve melhora aparente em Donkey Kong Bananza e não se observou remoção de efeitos (não era default). Na comparação Game vs NoSharpening, não notou ganho; é diferente da regressão v0.3, portanto NÃO torná-lo default.
- **Três crashes:** duas vezes ao abrir o jogo e uma após carregar save; áudio da tela inicial/cutscene deixou de tocar, vídeo continua lento. Não atribuir a AV1 sem log; o programa também modificou cache ASTC, aliases, pool de IR, allocator OOM.
- Capturas têm HUD e mapa que aparecem incompletos/preto em algumas cenas; isso pode envolver cache de texturas/VRAM OU shader pipeline ainda pendente. Precisamos de log.

## Atualização oficial Fritchii

[Fritchii v5](https://github.com/Frizti/Fritchii/releases/tag/fritchii-v5), publicada 09/11/2026. A comparação GitHub entre v4.1 e v5 contém **240 commits à frente** (branches divergentes) e 264 arquivos alterados visíveis na resposta. Não portar tudo de uma vez.

Propostas prioritárias e riscos:
1. **Correção de VRAM/texture cache e limpeza de cópias obsoletas**: upstream relata redução de 8,8 GB para 6,4 GB em *Castle Town* em RTX 4080; isso é **relato em outro hardware** e, mesmo 6,4 GB excede a VRAM física da GTX 1050 Ti. Investigar port modular, não prometer 2,4 GB de economia em Pascal.
2. **Preparação antecipada de shaders**: upstream constrói shaders do Zelda antes da jogabilidade. Pode ajudar a evitar draw omitido, mas startup mais lento, consumo de cache extra (~1,2 GB na primeira migração) e memória/driver podem ser desvantagem em 4 GB VRAM/16 GB RAM. Implementar futuramente como opt-in e com limitação de memória; não obrigar Pokopia e Bananza a precompilar Zelda.
3. **Fastmem, timer preciso Win11 e clip distances**: examinar patches individuais e dependências.
4. **Atualização de base v5**: `vk_pipeline_cache.cpp` mudou profundamente; não foi encontrado `mesh_emulation.emplace` que a nossa adaptação da Lichii #569 depende. **Não substituir a base inteira sem port do fallback** para não perder terreno, portas e vegetação.
5. **Áudio**: o release v5 não menciona correção específica para o desaparecimento da música da abertura na v0.6. A base `src/audio_core/audio_core.cpp` é idêntica entre v4.1 e v5, mas não exclui mudança em outros serviços de áudio; não presumir correção.

## Diagnóstico sem nova compilação Windows

Novo script **`diagnostico-v07/Leoitchii-V06-Isolar-Crash-Audio.cmd`**, para copiar ao lado do `lichii.exe` v0.6 e comparar:
- [1] Apenas `EDEN_NX2_TC_LOG=1`: observação do cache.
- [2] `LEOITCHII_ALIAS_FAST=0`: reverte o novo caminho rápido de aliases, preserva outras mudanças.
- [3] `LEOITCHII_IR_EARLY_FREE=0`: desativa o novo caminho de liberação antecipada de memória na compilação compute.
- [4] `LEOITCHII_MESH_DISK_CACHE=0`: desativa apenas preload Mesh do cache (não a emulação via compute).
- [5] `EDEN_NX2_VDEC_PACE=0`: diagnostica se o pacing dos vídeos do Eglantine influencia ausência de música/atraso. Pode piorar sincronismo.
- [6] Desativa [2]+[3] juntos para reduzir suspeitos de crash.

Outro teste **pela UI**: no Zelda, comparar NVDEC `GPU Video Decoding` e `CPU Video Decoding`, reabrindo o jogo em cada teste. Na GTX Pascal, AV1 não é decodificado em hardware. Se a música só sumiu na v0.6, conferir se v0.5 ainda a reproduz, com o mesmo ajuste de volume e dispositivo de áudio no Windows. Não mexer em chaves, saves ou cache.

Recolher somente trechos do log após crash (últimas 100–200 linhas) e blocos contendo `ERROR`, `Audio`, `nx2 video`, `dav1d`, `av1`, `Vulkan`, `OOM`, `shader`, `Texture cache`. Omitir nomes e caminhos pessoais, IDs, chaves e outras informações privadas. Fritchii v5 possui `Help > Export Log`; a v0.6 é baseada em v4.1, portanto esse menu **não deve ser presumido**. Usar o log existente da v0.6.

## Aceitação do lote futuro v0.7

- Prioridade P0: música de abertura normal; zero crash na abertura e nos testes de save; reproduzir av1 funcionalmente.
- Prioridade P1: visibilidade, especialmente HUD e terreno em streaming e framerate da floresta.
- Prioridade P2: ganhos de memória/tempos de shader (v5) com perfis seletivos; preservar Bananza e Pokopia 60 FPS.
- Sem mudanças de qualidade global, sem desbloqueio de NoSharpening por padrão, sem remoção de fog/sombras sem identificar pass real.
- Não chamar teste de desktop GTX 1050 Ti de validado sem métricas.
