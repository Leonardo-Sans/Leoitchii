# Leoitchii — v0.2, auditoria de desempenho para GTX 1050 Ti (08/11/2026)

**Base VALIDADA pelo usuário:** `fcc5c20fcd3253fe2da641c2fe66d9c65a9db367`.
Branch congelada: `base-validada-gtx1050ti-v01`. Não modificar.
Branch nova: `experimentos-1050ti-v02`.

## Fontes inspecionadas e decisões

1. **Cutscenes/vídeos:** Eglantine `1f52ac7e2efe7c4b3c8b93facfc0208b4378f6f4` corrige atraso de imagens em filmes pré-renderizados AV1 descartando frames vencidos. Integrar como cherry-pick rastreável; `EDEN_NX2_VDEC_PACE=0` reverte para A/B. Não promete aumentar taxa de frames 3D. Se o problema de 8 FPS for numa cutscene desenhada em 3D, essa correção não basta.
2. **4 GB VRAM:** Fritchii v4.1 já declara `astc_recompression=Bc3` (compressão 4:1 vs RGBA8), `vram_usage_mode=Conservative`, ASTC GPU, vídeo GPU. Hookshot `low-vram` também usa BC3, mas implementa no renderizador próprio, incompatível com port binário. Não duplicar o código. Testar se configurações persistidas pela instalação anterior sobrescrevem defaults.
3. **Trabalhadores de transcodificação:** Fritchii usa `hardware_concurrency()/4` (Ryzen 5 5600 12 threads -> 3); Eglantine `32e5578d7a19aaf4ebca4e25eb0dbf87a7ab0ab9` usa /8 (mínimo 2). Em vez de alterar configuração global, fornecer .cmd que ativa `EDEN_NX2_TRANSCODE_THREADS=2`, comparando com padrão.
4. **Ray tracing:** GTX 1050 Ti Pascal não tem aceleração RT dedicada. Não há prova de que Leoitchii esteja executando ray tracing; não criar desligamento fictício.
5. **Fog/névoa:** desligar shaders cegamente pode eliminar composição/água/iluminação e criar bugs. Prioridade é identificar passes reais, medir e preservar opção original. NÃO desligada nesta build.
6. **Resolução e AA:** validar 0.75x e 0.5x e AA Off via interface, sem impor valores globais que poderiam afetar outros títulos.

## Matriz mínima de teste

| Cena | v0.1 normal | v0.2 normal | v0.2 Eco |
|---|---|---|---|
| Intro pré-renderizada AV1 | FPS, atraso áudio/vídeo | mesma métrica | mesma métrica |
| Cutscene 3D | FPS real | FPS real | FPS real |
| Casa do Link (porta/vegetação) | geometria visível | idem | idem |
| Kokiri (câmera parada e andando) | FPS, VRAM, RAM | idem | idem |
| Área pesada (se acessível) | FPS, GPU memory budget | idem | idem |

Usar mesmo driver, resolução, shader cache quente, sem frame generation, e preferir médias e 1% lows. Não comparar warmup com cache novo.

## Ações pendentes

- CI Windows v0.2 verde; se conflito de cherry-pick, resolver manualmente com revisão dos hunks, jamais `-X theirs` global.
- Confirmação do usuário de melhora/ausência de regressão.
- Depois, perfil automático por GPU e diagnóstico opcional de passes de fog, se realmente houver ganho.

## Referências

- Eglantine movie pacing: https://github.com/Eglantine-Community/Eglantine/commit/1f52ac7e2efe7c4b3c8b93facfc0208b4378f6f4
- Hookshot low-vram: https://github.com/NotRexed/Hookshot/releases/tag/low-vram
- Fritchii v4.1: https://github.com/Frizti/Fritchii/releases/tag/fritchii-v4.1
- Eglantine workers: https://github.com/Eglantine-Community/Eglantine/commit/32e5578d7a19aaf4ebca4e25eb0dbf87a7ab0ab9
