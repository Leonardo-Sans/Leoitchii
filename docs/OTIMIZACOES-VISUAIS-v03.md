# Leoitchii — avaliação de efeitos visuais (v0.3)

**Objetivo:** FPS real em GTX 1050 Ti 4 GB, sem perder geometria nem sincronismo do OoT.

## Auditoria de origem

- Fritchii `fritchii-v4.1`, `src/common/settings.h`: as opções `resolution_setup`, `anti_aliasing`, `scaling_filter` e `oot_anti_aliasing` já existem e são configuráveis.
- `src/video_core/oot_network.h`: `NoSharpening` ativa bypass **apenas** para title ID `0400486024DEC000`, com tentativa de cópia da imagem tonemapped, sem remover mesh/cena.
- `src/shader_recompiler/ir_opt/oot_visual_workaround.h`: identifica compute shader `780c0536b89fc89e` como fog, mas sua rotina **muda intensidade visual** e não demonstra ganhos de FPS. O teste de rejeição de shader é opt-in e de alto risco.
- `src/video_core/shader_environment.cpp`: `EDEN_NX2_REJECT_HASH` rejeita chaves/hashes quando shaders são compilados; não é filtro semântico de efeitos e pode não influenciar shader já em cache.
- Fritchii já inicia com `AstcRecompression::Bc3`, `VramUsageMode::Conservative`, `MemoryLayout::Memory_8Gb`. **Memory layout não é VRAM**.
- Hookshot low-vram usa ASTC comprimido BC3, não portado: pipeline e renderizador distintos.
- GTX 1050 Ti não tem suporte RT dedicado; não existe RT por hardware confirmado para ser desligado.

## Política

1. Primeiro: bypass da rede de anti-aliasing (única mudança provavelmente significativa no processamento do OoT) e redução de resolução.
2. Depois: teste de fog desligado via launcher efêmero, com confirmação explícita. Se visual quebra ou não há ganho, abandonar; não introduzir no padrão.
3. Shadow map, SSR, iluminação global, volumetric fog: **não desativar cegamente sem hash/estágio medidos e relatório de regressão.**
4. Não alterar arquivos do jogo, chaves ou saves.
5. Defaults podem ser sobrepostos pelas preferências já persistidas no `qt-config.ini`. O valor real deve ser confirmado pela UI.

## Teste A/B

Manter driver/área/resolução/frametime, aquecer shader cache e medir:
- `v0.1`: referência funcional.
- `v0.2`: movie pacing e Eco opcional.
- `v0.3`: `NoSharpening` + 0.75x + AA off + bilinear.
- `v0.3 + teste fog`: apenas diagnóstico (se a imagem continuar válida).
- Acompanhar FPS (média e pior 1%), VRAM (4 GB limite), stutters, luz, folhagem, faces, água, porta da casa e cenas de interior.

Se `NoSharpening` causar quadros pretos ou regressão de geometria, altere-o no menu de volta a **Game**. Todo o trabalho de v0.3 está isolado no PR de testes de efeitos.
