# Leoitchii v0.7 — retorno de testes GTX 1050 Ti / Zelda e Pokopia

**Registro de 09/11/2026 (Brasil); build testada:** [Windows run 42717709123](https://github.com/Leonardo-Sans/Leoitchii/actions/runs/42717709123), base Fritchii 5.5 + Lichii 130 #961/#957/#984. A compilação terminou com sucesso, mas **não foi aprovada como estável**. Não reescrever a baseline v0.7.

## Observações do teste real do usuário

| Alvo | Observação |
|---|---|
| Zelda, abertura, modo 30 FPS | Tela inicial/abertura parece em câmera lenta, apesar de o contador indicar 30 FPS |
| Zelda, abertura, modo 60 FPS | A lentidão da tela de título desapareceu |
| Zelda, jogo, modo 60 FPS | Pior desempenho que o modo de 30 FPS; nos prints do dungeon o valor efetivo é ~26 FPS |
| Zelda, jogo, modo 30 FPS | Dungeon ~25-28 FPS, cidade ~10-15 FPS; ritmo percebido como mais consistente |
| Zelda, handheld | Faixas horizontais brancas aparecem já no começo e continuam com a câmera parada, não são rasgos de imagem dependentes de movimento |
| Zelda, docked | As faixas somem ao alternar para Docked, sem necessidade de trocar shader cache |
| Zelda, Game / Sharp | Sem diferença perceptível para os sintomas |
| Zelda, objetos pretos | Persistem, causa ainda desconhecida |
| Pokopia, móveis | Diversos objetos desaparecem conforme a câmera se aproxima/olha para eles; uma mesa branca está continuamente invisível; aparentemente objetos com partes brancas são afetados |
| Pokopia, histórico | O mesmo problema já existia em outras versões/forks testados pelo usuário, não é regressão demonstrada v0.7 |

**Fonte upstream de alta relevância:** [Lichii issue #602 — Furniture most of the time invisible in Homes its shadows only](https://github.com/zortos293/Lichii/issues/602), aberto no build-95, com placa RTX série 50. Indica que o bug **não é exclusivo da GTX 1050 Ti nem da v0.7**, mas não determina a causa técnica. Qualquer correção deve ser comparada com o mesmo cenário e validada em ambos os perfis de GPU.

## Análise do vídeo Zelda

Na base Fritchii 5.5 (`src/core/hle/service/nx2_gsv.h`), `PaceToVblank` faz (1) escolhe intervalo solicitado, (2) aplica `EDEN_NX2_SWAP_INTERVAL` se definido, e (3) força `swap_interval >= 2` ao OoT quando `Settings::values.oot_30fps` está ativo.

O port `portar-eglantine-video-v07.py` original detectava quadro de vídeo recentemente decodificado, mas só suspendia (2); (3) ainda forçava dois vblanks. Isto tornava o teste de vídeo incompleto justamente para o usuário em 30 FPS. O A/B atualizado nesta branch:
- Mantém `LEOITCHII_VIDEO_VBLANK_FIX` **desligado por padrão** e preserva o comportamento original quando 0.
- Com a flag =1, se `OcarinaOfTimeProgramId` e houver quadro decodificado nos últimos 500ms, define `swap_interval=1` para apresentação **somente durante vídeo**. Logo após, volta a respeitar `oot_30fps`.
- **Não** remove quadros, não altera clock do CPU, save ou cachê; não garante que todos os vídeos sejam reconhecidos pelo decodificador, que o som seja restaurado ou que o FPS real seja 60.
- Ativar/desativar só com reinício, pela opção `Leoitchii > Zelda: video da abertura a 60 FPS (teste)` no Laboratório. **Esta opção só estará disponível com a próxima build após validação; a v0.7 baixada anteriormente não contém a correção.**

## Plano de teste mínimo, com a build já instalada

1. Zelda: **EDS2** mantido; mesma área/câmera, `Handheld` com faixas, alternar para `Docked`, registrar exatamente se as linhas somem imediatamente e retornam ao voltar. Manter outros ajustes fixos.
2. Zelda: manter **30 FPS no gameplay** para a GTX 1050 Ti, usar 60 FPS só para reprodução da abertura enquanto não houver novo experimento validado.
3. Zelda: testar `GPU Accuracy` **Normal** a partir de Low em mesma área com objetos pretos, 1 opção por vez. Se melhorar, tentar High por curto período; comparar FPS e estabilidade.
4. Pokopia: mesma mesa e câmera, fazer um teste Low -> Normal (e eventualmente High) de GPU Accuracy; inspecionar desaparecimento com câmera frontal e lateral. Não usar cor branca como causa confirmada sem evidência de material/shader.
5. Se persistir ou piorar, `Help > Export Log`, com nomes/caminhos confidenciais removidos. Não enviar jogos, chaves ou firmware.
6. Confirmar **se há música na abertura da v0.7**; a ausência era regressão da v0.6 e ainda não há confirmação no teste atual.

## Decisões

- Baseline e ZIP v0.7 preservados; `main` não alterada.
- Alteração de vídeo desenvolvida em branch separada **sem Windows build automática**; acumular outras correções validadas antes de gastar outra compilação Windows.
- Incluir o rastreio do Pokopia #602 na auditoria de shader, textura, depth/culling e imagem, **sem apontar causa como resolvida**.
- Não apagar cache de shaders ou saves. Manter histórico e evidências de A/B ao comparar.
