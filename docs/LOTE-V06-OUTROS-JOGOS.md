# Leoitchii — otimização adicional do lote v0.6 (Bananza, Pokopia, Zelda)

## Evidência observada (GTX 1050 Ti 4GB, Ryzen 5 5600, 16GB RAM)

- **Donkey Kong Bananza**: screenshot mostrando **Game 15 FPS, 69,78 ms**, modo FAST, HANDHELD, Vulkan, NO AA, escala **1×**. Usuário relata que antes tinha muitos objetos que não carregavam, e agora está *praticamente jogável*, apesar de 14 FPS.
- **Pokopia**: usuário informa **60 FPS**; não inferir configuração que não foi mostrada.
- **Zelda Ocarina of Time**: em ambientes abertos ~8–14 FPS a escala 0,5×; dungeon até ~30 FPS; velocidade acelerada diminuiu com ajustes de timing. V0.3 com NoSharpening foi rejeitada.
- **Implicação:** não impor resolução 0,5× ou desligamento geral de efeitos no executável. Usar configurações **por jogo** e preservar Pokopia.

## Mais duas otimizações de baixo impacto de código

**1. Evitar trabalho repetitivo de aliases**: [Lichii #858](https://github.com/zortos293/Lichii/commit/c7e807d61709868ee6a467d051d468d914729706) incorpora a otimização limitada da textura alias [6d71b4f](https://github.com/zortos293/Lichii/commit/6d71b4f9078fe0aad2fd53353c83412ff605cb3c). O upstream mediu **17,5 → 18,7 FPS** em uma cena de Bananza (outro hardware). Mantemos só a otimização de ticks em três arquivos, NÃO importamos o módulo experimental de Fast Draw com 39 arquivos e centenas de mudanças. **Rollback A/B**: `LEOITCHII_ALIAS_FAST=0`.

**2. Preparação de ASTC mais barata**: [Lichii #296](https://github.com/zortos293/Lichii/commit/d590d51820f9) evita copiar bytes ASTC antes de analisar opacidade, e otimiza um compute shader ASTC. A versão de shader no pacote foi verificada byte a byte: Fritchii v4.1 + patch #296 == shader Lichii. O script valida o hash Git do shader original antes de aplicar, sem modificar shaders de outros jogos.

**Outras correções da v0.6**: Lichii #880 (imagem sem VRAM), #879 com #912 (AV1/dav1d sem limitar threads), fallback mesh compute v0.2/v0.4, Eglantine pacing. A verificação rápida anterior passou; repetir após essas alterações. Nenhum ganho adicional pode ser garantido até teste na GTX.

## Perfis recomendados para comparar, sem defaults globais

| Título | Baseline confirmado / meta | Experimento inicial |
|---|---|---|
| Zelda | Game AA, Handheld, 0,5×, FAST, texturas BC3, VRAM Conservative | verificar o impacto dos novos aliases, ASTC e AV1; preservar clock normal |
| DK Bananza | ~15 FPS a 1×, Handheld, Fast, sem AA | testar 0,75×, depois 0,5× em mesma cena; se FPS não cresce, investigar draw calls |
| Pokopia | 60 FPS segundo usuário | **manter configurações atuais** e só realizar teste rápido de regressão da nova build |

Comparar `Game FPS` e frame time do canto direito; 30 FPS na barra esquerda pode ser limitador. A imagem do Bananza não mostrou configurações de fallback de textura, não inferir.

## Critérios de aprovação

1. Não causar perda de folhas/portas, HUD, rios, água ou sombras indispensáveis.
2. Bananza não pode voltar a ter grande volume de objetos invisíveis. Zelda não pode ficar acelerado ou perder substancialmente seu desempenho atual.
3. Pokopia precisa continuar chegando a 60 FPS e com gráficos equivalentes.
4. Se o fast alias tiver regressão, desabilitar pelo launcher de teste sem recompilar.
5. Se a v0.6 ficar pior que a v0.5, manter a v0.5 intacta e não fazer merge à main.
6. Continuar sem retirar a fog do chão por suposição; isolar o passe por captura gráfica antes.
