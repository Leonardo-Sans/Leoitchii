# Leoitchii v0.7 — integração seletiva Lichii build 130

Base consolidada: **Fritchii v5.5 (SHA 4012e527)** com identidade, menu de Laboratório, fallback Mesh GTX Pascal, AV1 software e correções de vídeo experimental da v0.7.

Upstream adicional: **Lichii build 130** ([release](https://github.com/zortos293/Lichii/releases/tag/build-130), commit 3dae119). **Esta branch é um lote de integração da v0.7, não uma build concluída ou aprovada.**

## Já portado com validação de integração

| Port | Código | Comportamento |
|---|---|---|
| [#961](https://github.com/zortos293/Lichii/pull/961) | Varredura de páginas zeradas em memória guest, Windows, e trim periódico | Ativo por padrão, opção `LEOITCHII_ZERO_TRIM=0` em **Leoitchii → Laboratório** para A/B após reinício. Não altera o conteúdo ou saves. |
| [#957](https://github.com/zortos293/Lichii/pull/957) | Corrige `MultiLevelPageTable::ReserveRange` no limite máximo e tamanho zero | Sempre ativo. Fix de limites, não flag de performance. |
| [#984](https://github.com/zortos293/Lichii/pull/984) | Geração única por `DeviceMemoryManager` para impedir reaproveitar tradução de um objeto destruído | Sempre ativo. Correção de use-after-free, não flag de performance. |

A importação de #961 é feita por diff exato do commit upstream `2b30c2c`, com cabeçalho adaptado porque Fritchii já incluía `<utility>`. No primeiro teste de integração, o cabeçalho conflitava; foi corrigido na origem do patch e o [CI subsequente passou](https://github.com/Leonardo-Sans/Leoitchii/actions/runs/42705559531).

**Os testes no CI garantem aplicação dos patches à fonte pinada, mas ainda não garantem compilação, desempenho ou estabilidade.**

## Portas grandes investigadas, ainda NÃO incorporadas

O CI fez uma sondagem real de `git apply --check` sem alterar arquivos:
[Auditoria completa do CI](https://github.com/Leonardo-Sans/Leoitchii/actions/runs/42705894050).

| Upstream Lichii 130 | Conflitos aproximados no Git patch | Decisão |
|---|---:|---|
| [#979](https://github.com/zortos293/Lichii/pull/979) espelho de semáforos | 8 | Exige adaptar funções de puller, query cache e `nx2.h` a Fritchii; #1014 depende dele |
| [#1014](https://github.com/zortos293/Lichii/pull/1014) semáforos sem limite 32 | 2 | Não aplicar isoladamente sem #979 |
| [#949](https://github.com/zortos293/Lichii/pull/949) espera/descritores Bananza | 44 | Muda 28 arquivos e depende de estruturas diferentes de GPU, alto risco de corromper desenho |
| [#1028](https://github.com/zortos293/Lichii/pull/1028) read-back assíncrono | 34 | Muda 26 arquivos, altera ownership de downloads |
| [#1056](https://github.com/zortos293/Lichii/pull/1056) macros de GPU back-thread | 13 | Depende de estruturas de split, incluindo `nx2_async_readback.h`, ausente na base Fritchii |
| [#1036](https://github.com/zortos293/Lichii/pull/1036) cache de shaders v2 | 41 | Formato novo em 79 arquivos e gestão de cache diferente; não trocar versão sem migração/rollback testados |
| [#1016](https://github.com/zortos293/Lichii/pull/1016) HostTiming OS sleep | 2 | Fritchii v5.5 **já usa** `Common::Windows::WaitHighResolution`, portanto não copiar outro temporizador e arriscar áudio |

**Conflitos são de integração textual (hunks), não bugs confirmados.** Não dizer que #949/#1028/#1036 estão no executável Leoitchii até que sejam adaptados e compilados.

## Cache, saves e reversibilidade

O Lichii build 130 informa que seu cache v2 pode exigir a remoção de pipeline caches anteriores, embora migração automática esteja presente no código. **O Leoitchii v0.7 deste lote continua usando o cache Fritchii v5.5** — não executa apagamento automático, não substitui `vulkan.fork-v54.bin` por `lichii-cache.v2.bin` e não altera saves.

Para testes no Windows: usar pasta de binários separada, backup de saves e caches, testar Zelda com música e cutscene separadas e Bananza no mesmo local, Pokopia como controle. Usar o Laboratório para desligar temporariamente economia de RAM se houver instabilidade; reiniciar para aplicar.

## Gates antes de release

1. Windows C++/MSVC com os ports Lichii 130. Antes disso, o CI Linux **apenas** confirma patches.
2. Verificar música e efeitos de Zelda (problema na v0.6), cutscene, crashes e objetos pretos.
3. Medir RAM privada, working set e VRAM ao longo de 15+ minutos; resultados do Lichii #961 (13,4 -> 7,2 GB em outro PC) **não são resultado garantido** na GTX 1050 Ti/16GB.
4. Comparar logs/frametimes v0.5, v0.6, v0.7 para Zelda, DK e Pokopia; não prometer melhorias de fps vindas de benchmarks em RTX 3080.
5. Se o lote estiver regressivo, retirar somente o port responsável; nunca apagar o histórico dos testes/branch main antes da validação.

**A v0.7 permanece experimental, e as melhorias que exigem reengenharia de GPU devem continuar documentadas sem forçar um merge incompleto.**
