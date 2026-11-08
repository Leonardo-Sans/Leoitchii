#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Correção restrita de divergências entre o Fritchii v4.1 e o fallback PR #569.

Fritchii usa draw_pipeline na assinatura de UpdateDynamicStates, onde o Lichii
usa pipeline. Outro 'device' local na lógica DMA do Fritchii oculta o membro.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
target = root / "src/video_core/renderer_vulkan/vk_rasterizer.cpp"
original = target.read_text(encoding="utf-8")

changes = [
    (
        """if (const auto device = gpu_memory->GpuToCpuAddress(*indirect)) {
                split.RecordDispatchWrite(*device, 12);
            }""",
        """if (const auto host_address = gpu_memory->GpuToCpuAddress(*indirect)) {
                split.RecordDispatchWrite(*host_address, 12);
            }""",
    ),
    (
        """const bool emulated_mesh{pipeline != nullptr && pipeline->IsEmulatedMesh()};""",
        """const bool emulated_mesh{draw_pipeline != nullptr && draw_pipeline->IsEmulatedMesh()};""",
    ),
]
current = original
for before, after in changes:
    count = current.count(before)
    if count != 1:
        raise SystemExit(
            f"Ajuste recusado em {target.name}: esperado 1 trecho exato, encontrado {count}: {before!r}"
        )
    current = current.replace(before, after)

if current.count("void RasterizerVulkan::UpdateDynamicStates(GraphicsPipeline* draw_pipeline)") != 1:
    raise SystemExit("Assinatura do UpdateDynamicStates não corresponde à base Fritchii.")
target.write_text(current, encoding="utf-8", newline="\n")
print("Rasterizer: nomes de variáveis da integração ajustados, sem desativar warnings.")
