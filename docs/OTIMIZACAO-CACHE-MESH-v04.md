# Leoitchii v0.4 — correção focalizada de cache para Mesh Shader emulado

**Base:** v0.2 testada pelo usuário (commit `e411ee78b111b700f2524095f968349e87254b81`). Não incluir a regressão `NoSharpening` da v0.3. Não mesclar na `main` sem teste.

## Evidência

1. Em `Frizti/Fritchii` `fritchii-v4.1`, `vk_pipeline_cache.cpp` rejeita registros com estágio `Task`/`Mesh` no carregamento do cache de disco quando `VK_EXT_mesh_shader` não existe, **antes** de chegar em `CreateGraphicsPipeline`.
2. O port da correção Lichii PR [#569](https://github.com/zortos293/Lichii/pull/569) adiciona `mesh_emulation` via compute para parte desses estágios mesmo sem a extensão Vulkan.
3. Na GTX 1050 Ti (Pascal/NVIDIA) essas duas políticas entram em conflito: as execuções emulam alguns draws, mas o carregamento do cache os descarta. **Hipótese técnica verificável**, não ainda uma melhoria de FPS medida.
4. No Fritchii a flag `EDEN_NX2_ASYNC_DISCARD=0` existe e instrui a aguardar pipelines que ainda estão sendo compilados; isto diferencia desenho omitido temporariamente de problemas de cache de textura.

## Implementação

`scripts/adaptar-preload-mesh-pascal.py` reescreve exclusivamente o filtro de preload com confirmação exata do trecho e sentinelas da emulação Lichii. No driver NVIDIA proprietário **sem** extensão Mesh, permite que os registros cheguem à tentativa de compilação (que possui validação de elegibilidade e pode devolver `nullptr`). Outros drivers mantêm o comportamento da v0.2. Pode reverter com `LEOITCHII_MESH_DISK_CACHE=0`.

Nenhum shader do jogo é removido. Não há alterações em texturas, cores, neblina, jogo, VRAM ou RAM. Isso não transforma a GTX 1050 Ti em GPU com Mesh Shader nativo.

## Matriz A/B obrigatória

| Teste | Cena | Resultado esperado a avaliar |
|---|---|---|
| v0.2 original | Kokiri, primeira/segunda abertura | FPS, objetos pretos, pré-compilação |
| v0.4 padrão | Mesma cena, primeira/segunda abertura | Se pipelines emulados são recuperados do disco |
| v0.4 com `LEOITCHII_MESH_DISK_CACHE=0` | Mesma cena | Se o novo filtro é mesmo responsável por alguma diferença |
| v0.4 com `EDEN_NX2_ASYNC_DISCARD=0` | Mesma cena | Se objetos pretos são draws assíncronos ignorados (pode travar) |
| v0.4 com `EDEN_NX2_TC_LOG=1` | Mesma cena | Se expulsa/recodifica texturas em excesso |

Conferir no log: `Leoitchii: mesh compute fallback eligible`, `Async shaders: ... pipeline lookups skipped`, `Runtime pipelines in the last 10 s`, `Texture cache`, `Slow upload`, `Out of device memory`.

## Outras frentes ainda não implementadas

- **Fog dinâmica** no chão: hash do workaround de fog não foi identificado como único shader que desenha o efeito. Não desativar cegamente.
- **RAM de 16 GB:** não aumentar retenção de texturas indiscriminadamente; analisar paging/compartilhamento de GPU primeiro.
- **Cutscenes:** Eglantine pacing da v0.2 pode manter áudio sincronizado, mas não cria capacidade de decodificação AV1 por hardware na GTX 1050 Ti; testar NVDEC CPU vs GPU na interface.
- **Offload CPU:** não mudar GPU ASTC→BCn para CPU sem dados; no Fritchii a conversão GPU pode preparar as texturas no próprio frame de uso.
- **Métricas FPS:** confirmar resultados no hardware real antes de considerar esta v0.4 apta a substituir v0.2.
