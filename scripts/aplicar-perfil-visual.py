#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Perfil visual v0.3 para GTX 1050 Ti, aplicando só defaults reversíveis.

O código do Fritchii é reconstruído em cada workflow; por isso esta etapa
adapta defaults do settings.h na árvore de build. Configuração já salva pelo
jogador pode sobrescrever estes defaults, intencionalmente.
Não mexe em shader de iluminação, sombras, geometria, mesh fallback, ou
no layout 8GB do sistema emulado.
"""
from pathlib import Path
import sys

source = Path(sys.argv[1]).resolve()
settings = source / "src/common/settings.h"
original = settings.read_text(encoding="utf-8")
changes = [
    # É o processamento neural anti-aliasing do próprio OoT, que o Fritchii
    # já sabe substituir pela imagem tonemapped, se o jogo for o título certo.
    (
        "SwitchableSetting<OotAntiAliasing> oot_anti_aliasing{linkage, OotAntiAliasing::Game,",
        "SwitchableSetting<OotAntiAliasing> oot_anti_aliasing{linkage, OotAntiAliasing::NoSharpening,",
    ),
    # Diminuir trabalho de fill rate; o usuário pode escolher resolução no menu.
    (
        "SwitchableSetting<ResolutionSetup> resolution_setup{linkage, ResolutionSetup::Res1X,",
        "SwitchableSetting<ResolutionSetup> resolution_setup{linkage, ResolutionSetup::Res3_4X,",
    ),
    (
        "AntiAliasing::Fxaa,\n                                                  \"anti_aliasing\",",
        "AntiAliasing::None,\n                                                  \"anti_aliasing\",",
    ),
    (
        "ScalingFilter::ScaleForce,\n",
        "ScalingFilter::Bilinear,\n",
    ),
]
updated = original
for before, after in changes:
    found = updated.count(before)
    if found != 1:
        raise SystemExit(
            f"Configuração padrão inesperada no settings.h: {before[:90]!r}, "
            f"encontradas {found} ocorrências. Nenhuma alteração gravada."
        )
    updated = updated.replace(before, after, 1)

# Os defaults críticos de memória, textura e vídeos devem continuar como estão.
required = (
    "MemoryLayout::Memory_8Gb,",
    "AstcRecompression::Bc3,",
    "VramUsageMode::Conservative,",
    "NvdecEmulation::Gpu,",
)
for sentinel in required:
    if sentinel not in updated:
        raise SystemExit(f"Sentinela ausente {sentinel}: verificação interrompida")
settings.write_text(updated, encoding="utf-8", newline="\n")
print("Perfil v0.3 aplicado: rede AA OoT bypass, 0.75x, FXAA off, scaling bilinear.")
print("AVISO: defaults não substituem preferências já persistidas. Sem remoção de fog/shadows.")
