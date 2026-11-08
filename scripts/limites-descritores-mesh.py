#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Port mínimo, reversível no Git, do cheque de limites de descritores do Lichii #642.

A versão inicial do fallback conta os storage buffers usados pelos shaders do
jogo, mas não os 1 (mesh) ou 4 (task+mesh) buffers auxiliares do compute
fallback. Em placas de orçamento baixo isso pode exceder o limite Vulkan.
Esta correção NÃO melhora FPS por si só; impede construir pipelines inválidos.

Upstream: zortos293/Lichii commit 7d3b3a5266c274f70140845b47c5023e0011d5de.
"""
from pathlib import Path
import sys

source = Path(sys.argv[1]).resolve()
file = source / "src/video_core/renderer_vulkan/vk_pipeline_cache.cpp"
before = file.read_text(encoding="utf-8")
old = """        if (storage_buffers > set_limit) {
            throw Shader::NotImplementedException(
                "Binding {} storage buffers to a pipeline whose descriptor set binds {}",
                storage_buffers, set_limit);
        }"""
new = """        // Lichii #642: o fallback adiciona buffers ao mesmo descriptor set.
        // Cheque sem overflow (nao some storage_buffers + aux antes de validar).
        const size_t auxiliary_buffers{
            mesh_emulation ? (mesh_emulation->has_task ? 4U : 1U) : 0U};
        if (auxiliary_buffers > set_limit ||
            storage_buffers > set_limit - auxiliary_buffers) {
            throw Shader::NotImplementedException(
                "Binding {} storage buffers ({} for mesh fallback) to a descriptor set limited to {}",
                storage_buffers + auxiliary_buffers, auxiliary_buffers, set_limit);
        }"""
if before.count(old) != 1:
    raise SystemExit(
        f"Não localizado limite original de storage buffers exatamente uma vez: "
        f"{before.count(old)}. Patch rejeitado."
    )
for feature in ("mesh_emulation.emplace();", "mesh_emulation->has_task",
                "host_info.max_descriptor_set_storage_buffers"):
    if feature not in before:
        raise SystemExit(f"Não foi encontrado o fallback do Lichii: {feature}")
after = before.replace(old, new, 1)
file.write_text(after, encoding="utf-8", newline="\n")
print("Limites Mesh: os buffers adicionais do fallback agora contam para o descriptor set.")
