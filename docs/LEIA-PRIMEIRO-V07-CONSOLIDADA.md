# Leoitchii v0.7 — Pacote consolidado Fritchii 5.5 (Windows x64)

**Estado:** BUILD EXPERIMENTAL, não aprovada para main. Preservar a v0.5 e a v0.6 para A/B. **Não apagar saves, chaves, firmware ou shader caches**. Fazer backup dos saves e usar uma pasta de binários separada.

## O que foi integrado na fonte

A base agora é o **Fritchii v5.5**, fixada em `4012e5271e278b21cf8f56b97481dac2b777cd0d` (release de 09/11/2026). Isso inclui cumulativamente as mudanças Fritchii v5-v5.5: correções de VRAM, staging buffer sob orçamento de memória, limpeza de cópias, gerenciamento de memória, pré-compilação de shaders, cache, correções de texto e clip distances, fallback Mesh Compute para placas GTX 10 e antigas, desativação de frame generation herdado, EDS2, cache NVIDIA por aplicativo, interface atual e diagnósticos. Ganhos numéricos em RTX 4080 **não são resultados da GTX 1050 Ti**.

Além da base:
- **AV1 Pascal:** port seletivo Leoitchii da v0.6 (libdav1d preferencial e checagem de capacidade de decoder antes de criar contexto GPU, com log do decoder). GTX 1050 Ti **não decodifica AV1 por hardware**.
- **Cutscene experimental:** trecho localizado do [Eglantine f7a902](https://github.com/Eglantine-Community/Eglantine/commit/f7a9027ff17b2e31f8e3d0dccb316b7244de128d), ajustado para a base Fritchii v5.5; pode evitar um intervalo de vblank forçado durante vídeo de 60 FPS, se esta condição estiver presente. **Desligado por padrão**.
- **Não portar o antigo vídeo Eglantine 1f52ac7:** a v0.6 perdeu música depois desse port. A causa não está isolada. Copiar o pacing por descarte de quadros para a base nova de forma cega seria regressão potencial.
- **Identidade Leoitchii:** nome `Leoitchii.exe`, coração original .ico, título e Sobre, metadados do executável no Windows.
- **Laboratório:** menu `Leoitchii` com configurações guardadas em INI separada e aplicadas na próxima inicialização. **Variáveis de ambiente definidas externamente ganham prioridade.**

## O menu que substitui os antigos CMDs

| Opção | Padrão | Função |
|---|---|---|
| Preparar shaders antes do jogo (`EDEN_NX2_PRECOMPILE`) | Ligado | Preparação antes de entrar no jogo; pode consumir muitos minutos na primeira execução |
| Processamento de GPU dividido (`EDEN_NX2_SPLIT`) | Ligado, modo 2 | Caminho de GPU dividido; desligar pode reduzir muito FPS |
| Agrupar sincronizações de GPU (`EDEN_NX2_FENCE_BATCH`) | Ligado | Agrupa submissões de fences |
| Correção de desenho indireto, Bananza (`EDEN_NX2_RESETFIX`) | Ligado | Workaround existente na base Fritchii |
| Teste de cutscene 60 FPS (`LEOITCHII_VIDEO_VBLANK_FIX`) | **Desligado** | A/B de apresentação de vídeo com intervalo de vblank forçado |
| Log detalhado do cache de texturas (`EDEN_NX2_TC_LOG`) | **Desligado** | Telemetria; ligar só para investigar |

As antigas flags de v0.6 `LEOITCHII_ALIAS_FAST`, `LEOITCHII_IR_EARLY_FREE` e `LEOITCHII_MESH_DISK_CACHE` **não existem na base v5.5**. O menu não as mostra; Fritchii 5.5 tem implementações próprias de otimização e preload. Não prometer que são a mesma implementação. O fallback Mesh **não é desligável** pelo laboratório.

## O que NÃO foi mesclado na primeira build consolidada

- **Lichii #979 + #1014:** correção da tabela de regiões de semáforos do Bananza depende de ambos os PRs e difere profundamente do código Fritchii 5.5. Prioridade para próximo lote após triagem de Bananza.
- **Lichii #1028:** leitura assíncrona com ganhos em outro hardware, mas toca muitos arquivos de buffer cache e GPU. Não testado na GTX Pascal.
- **Lichii #1016:** espera do HostTiming via SO; ainda exige teste de áudio, que na v0.6 está regressivo.
- **Eglantine 1f52ac:** descarte de quadros atrasados, suspeita ainda não demonstrada de relação com perda de música. Mantido fora da base nova.
- Otimizações dependentes de RTX/DLSS: Fritchii expõe as opções, mas GTX 1050 Ti não tem hardware para executá-las.

Estes itens são **candidatos documentados, não funcionalidades já incorporadas**. Não ativar tudo ao mesmo tempo por engano. A base Fritchii v5.5 já incorporou muitas outras melhorias relevantes sem precisar de cherry-picks individuais.

## Checklist mínimo de execução no computador GTX 1050 Ti

1. Extrair a v0.7 em **pasta nova**, sem sobrescrever os executáveis antigos. Fazer backup dos saves. Lembrar que configurações e shader caches podem compartilhar a pasta de dados do emulador.
2. Confirmar o ícone de coração, o executável `Leoitchii.exe`, o menu `Leoitchii`, a tela Sobre e a versão v0.7.
3. Primeiro teste **com padrões do laboratório**. No Zelda: comparar a abertura (música e efeitos sonoros separadamente), cutscene, HUD, objetos pretos carregando, floresta e se consegue abrir/carregar saves três vezes.
4. Se não houver música, verificar CPU/GPU Video Decoding na interface, confirmar saída de áudio e comparar a v0.5. Não assumir que a opção de cutscene recupera som.
5. Bananza: confirmar terreno, vegetação, objetos e FPS no mesmo local da v0.6. Pokopia: confirmar que continua funcionando próximo ao resultado antigo de 60 FPS, sem garantia de fps fixo.
6. Se ocorrer crash, **Help → Export Log** (do Fritchii v5.5), ou Monitor de Confiabilidade do Windows. Remover nomes pessoais, caminhos, IDs e dados confidenciais antes de enviar. Não compartilhar chaves, ROMs ou firmware.
7. Só testar uma opção do laboratório por vez; para aplicar, fechar e reabrir o emulador. **Não limpar o cache para comparar FPS** sem backup e motivo comprovado.

## Critério de aceite

- Build Windows do GitHub Actions com C++/Qt/WinRC válida.
- Login, configurações e saves preservados; sem crashes reproduzíveis no boot ou load.
- Áudio da abertura e efeitos corretos.
- Fallback Mesh na GTX 1050 Ti, textura, portas, HUD e folhagem presentes; sem regressão severa em DK/Pokopia.
- Versões v0.5 e v0.6 continuam disponíveis para rollback.
- Sem aprovação de merge na `main` até os testes reais.

**Fonte:** [Fritchii 5.5](https://github.com/Frizti/Fritchii/releases/tag/fritchii-v5.5), [Lichii build-125](https://github.com/zortos293/Lichii/releases/tag/build-125), [Eglantine 09/11/2026](https://github.com/Eglantine-Community/Eglantine/releases/tag/daily-20261109). Leoitchii é projeto experimental independente; respeitar as licenças dos projetos de origem e não distribuir material protegido de jogos.
