# Leoitchii — protótipo GTX 1050 Ti

Experimento **não oficial** de integração entre [Fritchii](https://github.com/Frizti/Fritchii), [Lichii](https://github.com/zortos293/Lichii) e, em etapas futuras, [Eglantine](https://github.com/Djihads80/Eglantine).

## Objetivo

Testar uma compilação **Windows x64** para NVIDIA **GTX 1050 Ti (4 GB)**, Ryzen 5 5600 e 16 GB de RAM, priorizando:
- Retornar objetos ausentes (portas/vegetação), potencialmente causados pela falta de suporte nativo a `VK_EXT_mesh_shader` na arquitetura Pascal.
- Preservar, se possível, o desempenho observado no Fritchii.
- Manter os saves originais intocados e tratar separadamente o uso elevado de RAM.

## Primeiro experimento (sem garantia de sucesso)

1. Base exata do Fritchii v4.1: commit `f6d42b87150678e001dbeb84679a9595935ce951`.
2. Tentar portar **somente** a implementação alternativa de Mesh Shaders do Lichii: commit `b7ff181f20a1a397999151b84750f65f417f2b45` (PR #569).
3. A integração é interrompida em caso de conflitos: não usa resolução automática arriscada (`-X theirs`).
4. Se integrar, compilar em Windows no GitHub Actions e publicar o ZIP como artefato do fluxo.
5. Eglantine: avaliar e portar outras correções **depois** do teste da primeira build; nenhuma alteração específica do Eglantine está incluída ainda.

### Como acompanhar

Abra **Actions** → `Leoitchii - prototipo GTX1050Ti Windows`. Pode iniciar pelo `Run workflow` da branch `prototipo-gtx1050ti`, caso a execução inicial ainda não exista.

- Etapa `Integrar...` em vermelho: corrigir conflitos de código; **não há build** válida.
- Etapa `Compilar...` em vermelho: analisar o erro de compilação; **não há build** válida.
- Tudo verde: baixar `Leoitchii-gtx1050ti-windows-experimental` em **Artifacts**. Ainda exige teste real no PC e não garante FPS ou gráficos corretos.

### Segurança e licenças

Não compartilhe chaves, firmware, ROMs ou saves. **Nenhum deles é incluído no repositório ou no ZIP.** Faça backup dos saves e use a instalação compilada em pasta separada. A compilação pode usar a mesma pasta de dados do Fritchii; verifique o comportamento antes de iniciar qualquer jogo.

Este código de integração acompanha os projetos de origem, que possuem licenças próprias; o código do Fritchii/Lichii é apresentado como GPL-3.0-or-later. Em caso de distribuição de um binário derivado, forneça o código-fonte correspondente e preserve avisos e condições de licença.

**Status:** integração e compilação experimentais, não comprovadas. Este repositório não é o SecDeck.
