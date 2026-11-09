# Leoitchii v0.5 — teste de hardware a 0,5×, GTX 1050 Ti 4 GB

**Relato e três capturas enviadas pelo usuário (08/11/2026).** As capturas são evidências visuais; não foram copiadas ao repositório. Não deduzir métricas de GPU que não foram medidas. Última versão jogável relatada: v0.5. V0.6 continua em preparação, sem build Windows.

## Condições gráficas visíveis nas três capturas

- Vulkan, GPU Accuracy **FAST**, **HANDHELD**, filtro **BILINEAR**, **NO AA**, **Scale: 0.5×**, **Volume 100%**.
- O texto **30 FPS** na região inferior esquerda parece indicar limite/estado configurado, **não** a taxa real; o canto inferior direito mostra `Game: N FPS` e `Frame: N ms`.
- Captura A, dungeon fechada: **Game 28 FPS**, **36,74 ms/frame**. O jogo anteriormente ficava acelerado nesse intervalo; depois de ajustes de clock/velocidade, usuário relata que a aceleração **diminuiu** (não confirmou correção completa). HUD parcialmente escuro e minimapa apresentado como bloco marrom na captura.
- Captura B, caminho externo com neblina, vegetação e iluminação intensa: **Game 8 FPS**, **126,26 ms/frame**. Alguns elementos do HUD estão escuros/incompletos.
- Captura C, área externa/vila florestal: **Game 10 FPS**, **100,10 ms/frame**. HUD, corações e minimapa aparecem completos.
- Relato de uso externo habitual: **12–14 FPS**, poucas vezes ~20; não muito diferente da v0.2, apesar de diminuição de algumas quedas. Esses valores variam por cena/condições.
- O usuário relata que a velocidade acelerada melhorou após ajuste de CPU Clock/limite, mas **não isolamos experimentalmente qual ajuste** resolveu; manter investigação do complemento Dynamic FPS [Lichii #317](https://github.com/zortos293/Lichii/issues/317).

## Interpretação — hipóteses, não diagnósticos fechados

1. **0,5× ainda cai a 8–10 FPS ao ar livre**: reduzir mais resolução provavelmente terá retorno baixo se a principal carga vier de compute, Mesh emulado, textura/VRAM, sincronização ou número de objetos. Medir 0,5× vs 0,75× na **mesma câmera** confirma ou descarta sensibilidade de fill-rate. Não tirar conclusão apenas de duas áreas distintas.
2. **HUD temporariamente incompleto (corações e minimapa)** e geometria que chega preta até aparecer: sugere problema mais amplo que LOD/distância de visão. A associação com textura/recurso não residente é plausível; pipeline assíncrono continua possível. Não é evidência definitiva de falta de VRAM.
3. Névoa em camadas no chão, brilho do céu e folhagem densa são visíveis na captura externa. Não assumir que reduzir opacidade de fog elimina o trabalho do shader, ou que toda essa névoa é um único shader.
4. Resolução aparente oscilando não prova que a configuração `Scale: 0.5x` se alterou; pode ser nível mip/LOD, composição, upscaler ou recurso temporário.

## Trabalho já em v0.6 antes de compilar

- AV1: Lichii #879 com revisão #912 — `libdav1d` escolhido quando presente; não limitar suas threads; registrar o decodificador.
- VRAM: Lichii #880 — `TryCreateImage` não aceita imagem comum sem backing sob OOM; poderá reavaliar após liberação de memória.
- [Validação rápida do lote v0.6](https://github.com/Leonardo-Sans/Leoitchii/actions/runs/42543679477) passou; **não compilou o executável**.

## Teste adicional opcional que roda no binário v0.5, sem compilar

Arquivo `presets/LEOITCHII-V05-Bloom-TESTE.cmd`, colocar ao lado do `lichii.exe` da v0.5. Ele ativa `EDEN_NX2_REJECT_HASH=f2b14c43ca0e4300,96dd01c5b0361fcb` para pular o par de upsample de bloom da [issue Lichii #101](https://github.com/zortos293/Lichii/issues/101).

**Muito importante:** os hashes foram estudados em outra GPU, RTX 5070 Ti. Não foi demonstrado ganho de FPS ou segurança visual na GTX 1050 Ti. A perda de bloom/brilho pode vir junto com água/rios ou outros efeitos ausentes. Testar somente para diagnóstico na mesma cena, com confirmação explícita, e comparar início normal. Não elimina necessariamente fog dinâmica, não elimina folhagem e não se torna padrão. O processo não altera save nem configuração; fechar e rodar `lichii.exe` limpa a variável.

## Protocolo mínimo da próxima rodada

1. Na **mesma vista externa** após aquecer shader cache, comparar 0,5× vs 0,75× com demais condições iguais, registrando `Game FPS` e `Frame ms`.
2. Se quiser: comparar normal v0.5 vs `Bloom-TESTE` na mesma câmera e registrar diferença visual (céu, água, plantas, HUD) e FPS. Se quebra imagem ou não ganha FPS, rejeitar.
3. Para objetos pretos: `EDEN_NX2_TC_LOG=1` (laboratório v0.5, opção B), observando pressão dedicada/compartilhada da GPU; `EDEN_NX2_ASYNC_DISCARD=0` somente em teste separado de alto risco (pode travar na compilação).
4. Velocidade de gameplay não é igual a FPS. Manter CPU Clock Normal, speed 100%, anti-aliasing de OoT Game. Evitar `NoSharpening`.
5. Não fazer build extra sem fechar o lote v0.6. Manter main e v0.5 preservadas.
