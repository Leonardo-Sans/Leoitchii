# Leoitchii v0.7 — menu de laboratório e identidade visual

**Projeto experimental.** A base e a compilação Windows continuam sujeitas aos testes de regressão do PR #9. Este lote de interface **não é uma correção comprovada de crashes/áudio**.

## O que muda em relação à v0.6

- O executável GUI passa a se chamar **Leoitchii.exe** (o executável CLI eden-cli.exe mantém seu nome).
- O título da janela passa a mostrar **Leoitchii v0.7 (experimental)**.
- O recurso de ícone da janela, a propriedade do executável no Windows e a tela Sobre passam a apontar para Leoitchii; o ícone é um coração vermelho de fantasia, **desenhado sem copiar sprites de Zelda ou de terceiros**.
- Um novo menu superior **Leoitchii** possui cinco opções experimentais de ligar/desligar. O menu armazena preferências fora da configuração global do Fritchii.

## Como usar o menu

1. Abra **Leoitchii → Laboratório** (é um menu na barra superior; não é uma nova tela inicial).
2. Marque ou desmarque qualquer opção experimental.
3. **Feche o emulador por completo e abra novamente.** As flags atuais só são lidas quando o processo inicializa.
4. Compare a mesma cena e registre música, efeitos sonoros, cutscene e crashes.
5. Para desfazer mudanças, reative individualmente o recurso ou use **Restaurar configuração experimental padrão** e reinicie.

**Importante:** a emulação de Mesh Shaders por compute da GTX Pascal não é desligada ao desmarcar o preload Mesh.

## Opções disponíveis

| Controle | Variável | Padrão | Efeito do desligamento |
|---|---|---:|---|
| Sincronização rápida de aliases | LEOITCHII_ALIAS_FAST | Ligado | Volta ao caminho de sincronização anterior |
| Liberação antecipada de IR | LEOITCHII_IR_EARLY_FREE | Ligado | Mantém memória de shader por mais tempo |
| Preload Mesh | LEOITCHII_MESH_DISK_CACHE | Ligado | Não prepara o cache antecipadamente; fallback Mesh permanece |
| Sincronismo de vídeo | EDEN_NX2_VDEC_PACE | Ligado | Não aplica descarte de quadros atrasados |
| Log de cache de texturas | EDEN_NX2_TC_LOG | Desligado | Mantém nível de log normal |

A aplicação salva as opções em **configuração independente da base** por QSettings, sob a organização Leoitchii e aplicação Laboratorio (no Windows, formato INI em diretório do usuário). Não edita arquivos de save, shader cache, keys ou firmware. Variáveis de ambiente definidas externamente têm prioridade, inclusive lançadores CMD antigos.

O diagnóstico de eventos do Windows (opção 8 do CMD anterior) continua um **procedimento externo de leitura** neste lote; não afirmar que já está incorporado ao menu.

## Arquitetura e fluxo de CI

- `assets/v07/leoitchii_lab.h`: fonte do menu Qt, flags e persistência.
- `scripts/aplicar-identidade-laboratorio-v07.py`: altera *somente* os trechos esperados da base Fritchii v4.1, após os ports existentes; falha em mudanças inesperadas.
- `scripts/gerar-icone-leoitchii-v07.py`: constrói ICO com resoluções Windows, somente Python standard library e arte procedural original.
- O fluxo **validar-patches-v06** tem uma etapa curta para v0.7 (sintaxe, integração e verificação de textos/ícone), sem compilar Windows.
- A compilação Windows longa é habilitada para esta branch **somente por acionamento manual**, depois do gate de qualidade. A branch não foi incluída na lista de gatilhos de push do workflow de build.
- A base inicial para v0.7 ainda é **Fritchii v4.1 + Lichii Mesh Compute + ports v0.6 + Eglantine**; não se considera migrada para Fritchii v5.
- `main` e as versões antigas **não devem ser alteradas** até validação funcional.

## Critérios para aceitar a futura build

- Executável Leoitchii.exe com ícone do coração e propriedades corretas no Explorer.
- Menu visível sem ação que altere jogos/saves/configs existentes.
- Alternar flag, reiniciar e verificar no log/experimento que o processo aplicou a opção.
- Música presente na abertura, nenhum crash reproduzível no mesmo cenário após várias execuções, fallback Mesh e texturas/portas preservados.
- Pokopia, Bananza e Zelda sem regressões inesperadas.
- Se o menu não compilar ou causar erros, reverter apenas o patch de interface; não perder base funcional v0.6 e não mesclar na main.

## Atribuição

Leoitchii não é produto oficial Nintendo nem é afiliado aos autores dos emuladores originais. Respeitar GPL e licenças de origem em qualquer distribuição. Não incluir jogos, BIOS, firmware, chaves ou conteúdo protegido.
