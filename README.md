# Leoitchii — laboratório experimental de compatibilidade GTX 1050 Ti

Projeto **não oficial**, derivado por integração seletiva de [Fritchii](https://github.com/Frizti/Fritchii), [Lichii](https://github.com/zortos293/Lichii) e correções pontuais de [Eglantine](https://github.com/Eglantine-Community/Eglantine).

O Leoitchii estuda a execução de jogos no **Windows x64**, especialmente em **GTX 1050 Ti 4 GB, Ryzen 5 5600 e 16 GB de RAM**, preservando a emulação de Mesh Shaders por compute necessária à arquitetura NVIDIA Pascal.

## Estado atual — 09/11/2026

| Versão | Estado | Observações |
|---|---|---|
| v0.2 | Experimento anterior preservado | Referência histórica funcional, não integração aprovada |
| v0.3 | Regressão rejeitada | Perfil visual e desempenho ruim; não recuperar o default NoSharpening |
| v0.5 | Referência de comparação | Menos problemas de estabilidade relatados, mas ainda com stutter, vídeo lento e objetos escuros |
| v0.6 | **Experimental / não aprovada** | FPS e carregamento visual melhoraram; 3 crashes (2 na abertura, 1 após save), perda da música de abertura |
| v0.7 | **Auditoria e preparação, sem build** | Isolar regressões, analisar ports seletivos do Fritchii v5, não fazer merge prematuro |

A branch **main permanece intacta**. A v0.7 está no [PR #9](https://github.com/Leonardo-Sans/Leoitchii/pull/9), sobre a branch v0.6. As versões de teste e seus PRs anteriores não foram apagados.

**Decisão:** nenhuma nova compilação longa enquanto não houver evidências suficientes sobre os crashes e a falta de música. Não confundir compilação aprovada no GitHub Actions com estabilidade em hardware real.

## O que há neste repositório

Este não é um espelho completo do código do Fritchii. O workflow Windows obtém uma revisão fixa da base do emulador e aplica scripts e patches deste repositório. O conteúdo inclui:

- Scripts de integração, compatibilidade Mesh Shader (Lichii #569) e experiências com vídeo, ASTC, caches, VRAM e compilação de shaders.
- Presets para comparação local sem mudar configurações salvas.
- Evidências, protocolos e planos de continuidade em docs.

O **Fritchii v5** (09/11/2026) relata memória menor, preparação antecipada de shaders e outras correções, **testadas principalmente em RTX 4080**. Não trocar toda a base v4.1 por v5: o fallback Mesh Compute existente deve ser mantido e revalidado. Não extrapolar ganhos de FPS/RAM/VRAM para a GTX Pascal sem testes.

## Próximo teste sem build

1. Na v0.6 já instalada, copiar o arquivo [Leoitchii-V06-Isolar-Crash-Audio.cmd](diagnostico-v07/Leoitchii-V06-Isolar-Crash-Audio.cmd) para a **mesma pasta de lichii.exe**.
2. Abrir o CMD e seguir o [protocolo A/B de estabilidade e áudio](docs/PROTOCOLO-V07-TRIAGEM-CRASH-AUDIO.md): v0.5 como controle; v0.6 normal; opção 5 para o vídeo; opção 6 para otimizações de memória; opção 7 apenas se necessário.
3. Após crash, executar a opção 8 para consultar um **resumo de eventos locais do Windows** (somente leitura, sem caminhos pessoais). Na ausência de evento, obter apenas o trecho relevante do log do emulador, retirando informações privadas.
4. Com a causa isolada, consolidar o menor patch possível para a v0.7 e só então avaliar uma única build de testes.

Veja também a [auditoria das regressões e Fritchii v5](docs/AUDITORIA-V07-FRITCHII-V5-REGRESSOES.md).

## Segurança, dados e licenças

- **Não compartilhar nem adicionar ao repositório:** firmware, chaves, jogos, saves, ROMs, caches com conteúdo sensível ou caminhos pessoais.
- Fazer backup dos saves antes de novos testes. Usar pastas de binários separadas para cada versão; atenção ao possível compartilhamento de pastas de dados do emulador.
- Não apagar caches de shader para investigar FPS ou crashes sem uma justificativa e cópia de segurança.
- Respeitar as licenças e avisos dos projetos de origem, incluindo as obrigações de fornecer código-fonte correspondente ao distribuir binários derivados. Este projeto não é afiliado aos desenvolvedores originais ou à Nintendo.
