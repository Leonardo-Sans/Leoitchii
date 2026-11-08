# Leoitchii — diagnóstico de VRAM e texturas na GTX 1050 Ti (v0.2)

**Objetivo:** investigar os objetos que permanecem pretos por segundos e reaparecem ao girar a câmera, e as quedas na vila. Estes arquivos **não são uma build** e **não alteram o emulador**.

**Versão de referência:** Leoitchii v0.2 (branch `experimentos-1050ti-v02`, commit `e411ee78b111b700f2524095f968349e87254b81`). Usuário informou: ~30 FPS em interiores/dungeons, ~20 FPS na vila com quedas fortes, intro ainda lenta, objetos pretos recorrentes, 16 GB RAM e GTX 1050 Ti 4GB; Ryzen 5 5600 com folga aparente.

## Como usar

1. **Não reinstale e não apague caches/saves.** Faça backup dos saves.
2. Copie os três arquivos `.cmd` desta pasta para **a mesma pasta do `lichii.exe` da v0.2**. Não os copie para a pasta de jogos.
3. Feche o emulador entre os testes. Rode `01-Diagnostico-VRAM-v02.cmd` e permaneça **60 a 90 segundos** na mesma vista da vila; depois gire a câmera 180° por 30 segundos. Capture o FPS e, pelo Gerenciador de Tarefas, memória da GPU **dedicada** e **compartilhada**.
4. Opcionalmente compare com `02-Teste-Cache-90-frames-v02.cmd`: mantém texturas usadas recentemente por mais tempo e testa se isso reduz a repetição de objetos pretos. **Se a VRAM ficar saturada, voltar imediatamente para execução normal**. Esse valor não é uma configuração recomendada sem análise dos logs.
5. Opcionalmente `03-Teste-Workers-4-v02.cmd` testa quatro workers de transcodificação, contra os três aproximados do Fritchii em Ryzen 5 5600. Pode causar mais disputa por CPU e piorar desempenho.
6. Execute `lichii.exe` diretamente para voltar à configuração anterior. As variáveis usadas pelos `.cmd` são locais a cada processo.

## Diagnóstico de shaders, sem criar outra build

No menu de configurações por jogo, teste **Compilação de shaders assíncrona** ligada e desligada na mesma cena, reabrindo o jogo entre mudanças. Com ela ligada, certos draws não preparados podem ser omitidos até a compilação. Com ela desligada, é possível que a imagem apareça completa, mas com travamentos prolongados. Se os objetos pretos **não** mudarem, o cache/texturas fica como hipótese mais forte. Não mexer em `EDEN_NX2_REJECT_HASH` na análise inicial.

## Logs e dados relevantes

O Fritchii possui `EDEN_NX2_TC_LOG=1` em `src/video_core/texture_cache/texture_cache.h`; gera periodicamente linhas do tipo `Texture cache: device memory ... (expected ..., critical ...), ... images ...`, `Slow upload ...` e estatísticas de evicções. Consultar o log de execução do emulador (pasta de logs acessível pelo menu de dados, se disponível). A cada 600 quadros, a linha de cache pode levar aproximadamente **30 segundos a 20 FPS**.

Registre apenas trechos do log relacionados a `Texture cache`, `Memory margins`, `Slow upload`, `Out of device memory`, `image` e `shader`. Remova caminhos pessoais, chaves, IDs locais e quaisquer dados privados antes de compartilhar. **Não compartilhar jogo, firmware, keys ou saves.**

## Como distinguir a causa

- **VRAM dedicated lotada e shared crescendo + muitas evicções/reuploads:** provável thrashing de texturas. Retenção maior pode piorar o problema; investigar tamanhos de imagens, mínimos de mip e alocação.
- **Objetos reaparecem somente depois de recompilação de pipelines / ao mexer no async shaders:** provável pipeline/shader não pronto. Aumentar retenção do cache de texturas não será a solução.
- **Uso alto de GPU, mas reduzir resolução não aumenta FPS:** pode indicar gargalo de sincronização/compute (Mesh Shader fallback), e não de pixels. Comparar também com v0.3 `NoSharpening` e analisar tempos de GPU.
- **CPU total baixo:** não exclui saturação de uma única thread, nem bloqueios por fila/sincronização. Consultar processadores lógicos por núcleo no Gerenciador de Tarefas.
- **Vídeo pré-renderizado:** pacing de frames evita áudio distante da imagem; não corrige FPS físico de decodificação nem cutscene 3D. Distinguir pelo conteúdo.

## Segurança dos testes

Não mudar memória emulada de 8 GB para 4 GB: não representa VRAM. Evitar `CpuAsynchronous` para ASTC como solução padrão: o código do Fritchii documenta que o caminho GPU ASTC→BC1/BC3 garante texturas já no primeiro uso; transcodificação assíncrona na CPU pode demorar e mostrar placeholders. Não alterar automaticamente neblina, sombras ou ray tracing sem medir; um shader de fog pode participar de composição de outros efeitos.

## Próxima alteração de código

Somente após análise dos logs: selecionar uma estratégia testável (por exemplo, retenção adaptativa à VRAM ou melhorias no ciclo de vida de texturas) e compilar **uma** build consolidada. A v0.3 (redução de resolução, AA e rede neural do OoT) está em CI separado; não reabrir builds antigas repetidamente.
