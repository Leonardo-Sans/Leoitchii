# Validação da build Leoitchii (GTX 1050 Ti)

## Proveniência (08/11/2026)
- Fritchii v4.1, tag imutável verificada pelo SHA `f6d42b87150678e001dbeb84679a9595935ce951`.
- Lichii PR #569, commit `b7ff181f20a1a397999151b84750f65f417f2b45`.
- O Lichii deriva do Eglantine. **Não há, nesta etapa, port adicional selecionado do Eglantine**.

## Critérios de aceitação
1. A correção é aplicada ao Fritchii sem conflitos.
2. Compilação Windows Release completa e entrega `lichii.exe`/dependências.
3. Executável abre em sistema Windows x64 e reconhece a GTX 1050 Ti.
4. Porta da casa do Link, paredes e vegetação aparecem na mesma cena onde eram invisíveis.
5. Medir FPS real com geração de quadros desligada (mesma cena e resolução); comparar Fritchii original e Leoitchii.
6. Monitorar pico de RAM, VRAM, uso de GPU e CPU com 16 GB totais.
7. Garantir que saves/configurações anteriores permaneçam íntegros (fazer backup).

## Falhas conhecidas / riscos
- Cherry-pick entre forks divergentes pode encontrar conflitos; nesse caso a pipeline falha de propósito.
- O fallback de Mesh Shaders pode aumentar o custo gráfico, especialmente em GTX Pascal.
- A etapa de build pode exigir adaptação às dependências das versões originais.
- Artefato verde **não equivale** a testes em hardware real.

## Evolução
Após a validação, avaliar outras correções do Eglantine e do Lichii uma de cada vez, documentando fonte, licença, impacto e medições. Não misturar tudo em uma única etapa.
