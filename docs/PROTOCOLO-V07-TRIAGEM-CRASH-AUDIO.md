# Leoitchii — protocolo de triagem v0.6 → v0.7 (GTX 1050 Ti)

**Status:** diagnóstico, não validação. Nenhuma compilação ou alteração da main foi autorizada neste lote. Base de comparação: v0.5 preservada. Alvo de análise: v0.6, que melhorou FPS/carregamento de objetos, mas apresentou 3 crashes (2 na abertura, 1 após save) e perdeu a música de abertura.

## Ambiente e limites do experimento

- GTX 1050 Ti 4 GiB, Ryzen 5 5600, 16 GiB RAM. Evitar pressupor que ganhos de uma RTX 4080 ou VRAM >= 6 GiB do Fritchii v5 se repetem neste PC.
- Manter **o mesmo jogo, atualização, mods, save, cena, driver, saída de áudio e configurações** entre v0.5 e v0.6, sempre que possível; anotar diferenças conhecidas.
- **Não limpar shader cache nem dados do usuário**, não baixar firmware ou chaves e não enviar nenhum desses itens.
- Fechar a execução anterior antes de iniciar outra. Cada escolha do CMD abre apenas uma execução, com variáveis de ambiente temporárias.
- Não executar o jogo repetidamente se houver suspeita de corrupção de saves; manter cópia de segurança feita pelo usuário.
- Na v0.6, copiar o script diagnostico-v07/Leoitchii-V06-Isolar-Crash-Audio.cmd ao lado de lichii.exe. Não usar o script como perfil padrão; é ferramenta de isolamento.
- O script não promete corrigir falhas nem garantir que toda regressão dependa dessas quatro flags.

## Sequência de menor custo (não repetir todos os FPS)

| Ordem | Execução | Foco | Registrar |
|---|---|---|---|
| A | v0.5, execução normal, sem mudar caches | Controle de áudio e estabilidade | Música da tela de abertura (sim/não); crash (sim/não); cutscene |
| B | v0.6, execução normal, abrindo diretamente o EXE | Reprodução da regressão | Mesmo áudio e mesmo ponto; crash e estágio (boot / load / jogo) |
| C | v0.6, script opção **5** | Separar sincronismo de vídeo Eglantine de outras mudanças | Música retorna? vídeo piora? algum crash? |
| D | v0.6, script opção **6** | Separar risco de alias rápido + descarte antecipado de IR | Crash persiste ao abrir e ao carregar save? |
| E | v0.6, script opção **7** **somente se** C/D inconclusivos | Reverter as quatro otimizações experimentais temporariamente | Crashes e áudio mudam? |
| F | v0.6, script opções **2**, **3** e **4** em execuções separadas **somente se** E produzir melhoria | Atribuir a regressão a uma opção específica | Qual flag desativada melhora de forma repetível? |

Em caso de crash, executar **opção 8** após o fechamento, ou usar *Win + R → perfmon /rel* se o Windows não registrar Event ID 1000. O resumo da opção 8 é somente leitura e **não extrai caminhos, usernames nem logs completos**. Event ID 1000 pode não existir para travamentos, encerramentos normais ou OOM tratado pelo app.

**Critério mínimo para triagem:** três tentativas bem-sucedidas na mesma configuração constituem indício, **não prova** de estabilidade. Não declarar correção de crash só porque ele não se repetiu uma vez. Se D e E funcionarem, isolar flags individualmente antes de mudar o padrão da próxima compilação.

## Verificações adicionais de áudio/vídeo

- Na mesma cena, comparar saída de áudio, volume de sistema e configuração de som entre as versões. Verificar se os **efeitos sonoros** também sumiram ou se somente a **música** não toca.
- Na v0.6, comparar **CPU Video Decoding** e **GPU Video Decoding** nas configurações da aplicação, fechando e reabrindo o jogo a cada troca. A GTX 1050 Ti Pascal não decodifica AV1 em hardware; a opção GPU não garante AV1 por NVDEC.
- Se o som já falhar na v0.5 com mesmas configurações, investigar dispositivos e ambiente antes de atribuir culpa à v0.6.
- **Não concluir causalidade só a partir da opção 5.** A ausência de música pode ser consequência indireta de atraso de vídeo, travamento do pipeline ou outro subsistema.

## Evidência a enviar (texto sem dados pessoais)

Preencher apenas para os casos que forem executados:

~~~text
Teste: [A/B/C/D/E/F]
Versão: [0.5/0.6]
Opção CMD: [EXE/2/3/4/5/6/7]
Início: [abre tela? demora aproximada?]
Música na abertura: [sim/não/intermitente]
Efeitos sonoros: [sim/não/intermitente]
Cutscene: [carrega / lenta / congela]
Save: [não testei / carrega / fecha ao carregar]
Crash: [não / sim, em qual etapa?]
Windows Event 1000: [módulo, código de exceção, offset, hora, ou não encontrado]
Trecho final do eden_log.txt: [apenas linhas relevantes, revisadas]
~~~

Antes de compartilhar log completo, remover caminhos locais, nomes, UUIDs, títulos de biblioteca privados, contas e qualquer chave/firmware. Em eventos de **código de exceção 0xc0000005** pensar em violação de acesso; **não determinar o culpado apenas pelo código**. Se o evento indicar GPU driver ou DLL, correlacionar com últimos erros do log.

## Gate de v0.7

- **P0:** música funcional e ausência de crashes reproduzíveis nas cenas inicialmente problemáticas; sem introduzir corrupção de saves.
- **P1:** manutenção do fallback Mesh Compute na GTX Pascal (terrain/doors/folhagem) e da melhoria de carregamento, sem agravamento de OOM.
- **P2:** portar seletivamente melhorias do Fritchii v5 com teste de compatibilidade e flags de rollback, sem precompilação global e sem desabilitar bloom/fog como suposta otimização.
- Só solicitar **uma build consolidada v0.7** após ter evidência de qual mudança causou a regressão ou após preparar uma correção robusta e isolada que possa ser revertida. Manter v0.5, v0.2 e main.
