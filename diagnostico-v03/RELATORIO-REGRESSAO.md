# Leoitchii v0.3 — regressão confirmada no teste do usuário

## Resultado observado em 08/11/2026
- **v0.2:** até 30 FPS em dungeons; ~20 FPS na vila com quedas, intro e cutscenes ainda lentas, objetos pretos temporários.
- **v0.3:** ~5 FPS na mesma vila; objetos pretos e cutscenes não resolvidos.
- **Neblina dinâmica ao nível do chão:** continua presente.
- **Não promover a v0.3 nem mesclar o PR #3**. Preservar a v0.2 e a v0.1.

## Diferenças de código entre v0.2 e v0.3
v0.3 muda **apenas DEFAULTS** ao compilar `src/common/settings.h`:
1. `oot_anti_aliasing` Game → NoSharpening (bypass de rede AA do próprio OoT, usa AccelerateSurfaceCopy).
2. `resolution_setup` 1x → 0,75x.
3. `anti_aliasing` FXAA → Off.
4. `scaling_filter` ScaleForce → Bilinear.

**Importante:** configurações previamente salvas podem sobrepor defaults; não presumir que cada mudança foi aplicada no teste. Código e shader cache diferem entre sessões. Verificar valores REAIS na interface antes de atribuir causa.

Fritchii `docs/nx2/oot-network-bypass.md` mediu ganho de 41→50 FPS usando NoSharpening num **RTX 5090 a 1x**, mas não valida ganhos na GPU GTX 1050 Ti (Pascal). O bypass depende de imagens/formatos/tamanho compatíveis: quando falha, a rede neural roda normalmente. Na v0.3 foi combinado com 0,75x, combinação não validada.

## O que **não foi feito** na v0.3
- A neblina dinâmica **não foi desligada**.
- O launcher `Leoitchii-1050Ti-Fog-OFF-TESTE.cmd` é um experimento OPCIONAL que rejeita shader; não é um removedor seguro de neblina.
- Sombra/iluminação global/ray tracing não sofreram alteração.

## Diagnóstico A/B recomendado (sem outra build)
1. Usar v0.2 como baseline confiável; 30–60 s na mesma vista de Kokiri, sem geração de quadros. Registrar resolução, antialiasing do OoT e antialiasing comum.
2. Na v0.3, **voltar apenas** `Ocarina of Time anti-aliasing` para `Game`. Reiniciar o jogo; comparar FPS na vila. Registrar se recupera de 5 para ~20 FPS.
3. Na v0.3, se estiver em 0,75×, testar resolução **1x mantendo Game** e reabrir o jogo. Se aumentar FPS, há uma regressão no caminho de escala; se diminuir, bottleneck fill-rate pode ser relevante.
4. Só depois, se fizer sentido, ativar `No sharpening` na resolução **1x** para testar o bypass isolado; voltar `Game` se cair FPS.
5. Em cada versão guardar configurações, não limpar cache entre etapas sem registrar; preferir mesmos saves/câmera/clima/horário. Se uma configuração alterada por uma versão persistir na outra, restaurar explicitamente as anotações.

## Experimentos de neblina sobre v0.2, sem recompilar
- `01-Fog-25porcento-V2.cmd`: ativa `EDEN_NX2_OOT_VISUAL_WORKAROUND=1` do Fritchii v4.1. O código **multiplica por 0,25 uma expressão em shader compute identificado como fog** e por 0,65 outra expressão em shader fragment de exposição. Isso pode alterar a aparência, não garante remover a fog dinâmica ao nível do chão, nem aliviar processamento de GPU. Não é otimização comprovada.
- `02-Fog-Shader-Skip-ALTO-RISCO-V2.cmd`: usa `EDEN_NX2_REJECT_HASH=780c0536b89fc89e` para rejeitar um shader compute. Pode deixar outros efeitos ausentes ou causar telas pretas; serve apenas para medir se esse pass afeta FPS. Não garante que um cache previamente compilado receba a rejeição; **não limpe o cache nem saves para forçar o teste sem necessidade**.
- Se nenhum teste afetar a névoa visível no chão, o shader identificado não é a causa completa, e precisamos capturar a cena/passes e identificar seu hash ou draw real.

## Decisão para próximo código
**Não** fazer nova build grande antes de separar a causa da v0.3 e distinguir objetos pretos de shader ainda sendo compilado versus recarga VRAM. Coletar dados de `EDEN_NX2_TC_LOG` e VRAM. Manter fog off como opção futura implementada a nível de pass alvo **somente quando identificarmos e validarmos o shader correto**.

Referências:
- https://github.com/Frizti/Fritchii/blob/fritchii-v4.1/docs/nx2/oot-network-bypass.md
- https://github.com/Frizti/Fritchii/blob/fritchii-v4.1/src/shader_recompiler/ir_opt/oot_visual_workaround.h
- https://github.com/Frizti/Fritchii/blob/fritchii-v4.1/src/video_core/shader_environment.cpp
- https://github.com/Leonardo-Sans/Leoitchii/pull/3
