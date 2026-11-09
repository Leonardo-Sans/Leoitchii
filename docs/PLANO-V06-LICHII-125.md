# Leoitchii v0.6 — pacote seletivo da atualização Lichii build 125

## Base e evidências

- v0.5 **compilou com sucesso**: [Actions #42528236989](https://github.com/Leonardo-Sans/Leoitchii/actions/runs/42528236989), ZIP Windows produzido. Usuário testou: ~30 FPS em dungeon, em velocidade anormal; vila com menos quedas; objetos pretos reaparecem menos, mas persistem; imagem às vezes parece perder resolução; intro/cutscene 11 FPS.
- Lichii [build 125](https://github.com/zortos293/Lichii/releases/tag/build-125), commit `cbb512ee7a9de9d9dbe2f865ec2e468888503214`, traz alterações úteis. **Não sincronizar o projeto inteiro**, para preservar Fritchii v4.1 e fallback mesh da GTX 1050 Ti.
- v0.3 `NoSharpening` causou queda severa de FPS. **Continuar com OoT AA = Game**.

## Código preparado (sem acionar uma build)

### Vídeo (AV1) — Lichii #879 + #912

- Em `src/video_core/host1x/ffmpeg.cpp`, preferir `libdav1d` para AV1 caso o FFmpeg o disponibilize, retornando ao decoder disponível se não estiver presente.
- Testar suporte de hardware **antes** de criar contextos CUDA/D3D/Vulkan inutilizáveis.
- Em `src/video_core/host1x/nx2_video_decoder.cpp`, registrar nome do decoder, CPU/GPU e duração da abertura no log.
- **Não limitar threads do dav1d**: Lichii [#912](https://github.com/zortos293/Lichii/commit/a957980a43ec27e9c590ea7b2060c144c1312f2d) reverteu o limite introduzido por [#879](https://github.com/zortos293/Lichii/commit/64b962aa1e94cbffc1c491dda46e9297babbd4ce) porque provocou mais frames perdidos na intro.
- A GTX 1050 Ti Pascal **não** tem decodificação AV1 por hardware. O Ryzen 5 5600 pode ser utilizado para decodificação por software, mas 11 FPS pode ter outras causas (apresentação/composição da GPU). Não prometer 60 FPS.

### Texturas sem VRAM — Lichii #880

- O caminho `TryCreateImage` retorna falha se a imagem comum não couber na VRAM, em vez de aceitar imagem Vulkan sparse sem backing. O coletor poderá tentar novamente após liberar recursos.
- Manter fallback sparse para imagens virtuais gigantes e chamadores que não podem falhar.
- Evitar assert em imagens GPU-modified cujo mapeamento guest já mudou durante `JoinImages`.
- [Origem #880](https://github.com/zortos293/Lichii/commit/25a28bb4ecbaf8e6110507b701ce89b35ef4ac32). O caso original é AMD; em Pascal o efeito é **hipótese**, não confirmação. Não resolve shader assíncrono pendente nem todos os objetos pretos.

## Outras investigações sem código novo por enquanto

1. **Jogo acelerado a ~30 FPS:** reproduz [Lichii issue #317](https://github.com/zortos293/Lichii/issues/317) com `Dynamic FPS` e CPU Clock Boost. Repetir na v0.5 com relógio em **Normal**, velocidade do emulador em **100%**, frame generation OFF. Depois comparar Dynamic FPS ligado/desligado nas propriedades do jogo; sem o mod pode ficar em câmera lenta a FPS baixo. **Não utilizar FPS exibido como indicador de velocidade real**.
2. **Resolução que cai e volta:** diferenciar *mip/LOD mais baixo recarregado* (VRAM) de escala interna, upscaler, resolução dinâmica do jogo ou frame generation. Não desligar todos indiscriminadamente. Registrar GPU dedicated/shared e frames.
3. **Fog, vegetação, iluminação, sombra e draw distance:** a v0.5 não removeu esses efeitos; incluiu somente lançadores experimentais. O workaround de fog do Fritchii muda um escalar e exposição, mas **não remove o passe**. A [issue Lichii #101](https://github.com/zortos293/Lichii/issues/101) identifica shaders que misturam neblina, brilho e superfície da água: desligá-los pode quebrar o ambiente. Só considerar opção off após identificar o efeito verdadeiro por frame dump e medir custo.
4. **#910 null image / #921 draw fast path:** ficam em triagem, por serem de estabilidade/caminhos de renderização e não ganharem FPS comprovado em Pascal. Port específico somente quando houver motivação e correspondência técnica.
5. **Não trocar memory layout emulado 8GB por 4GB**: não representa VRAM. Não editar conteúdo do jogo nem distribuir assets proprietários.

## Teste de regressão antes de compilação consolidada

- Verificar scripts em uma árvore Fritchii v4.1 + Lichii #569 + correções de MSVC + Eglantine v0.2.
- Uma única compilação Windows depois de fechar o lote, com shader cache antigo preservado e baseline v0.5.
- Verificar intro 11 FPS (imagem/áudio), Kokiri parado e girando câmera, porta/folhagem (sem desaparecer), dungeon com velocidade do jogo, texturas escuras/reupload, RAM/VRAM.
- Se v0.6 introduzir crashes/queda de FPS, retornar à v0.5. **Sem merge em main antes da validação.**
