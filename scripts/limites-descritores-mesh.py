#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Port restrito do Lichii #642 para a base Fritchii v4.1 + mesh fallback #569.

O Fritchii v4.1 nao possui a guarda de descriptor-set do Lichii; por isso
nao devemos procurar o bloco do Lichii anterior a #642 para substitui-lo.
Insere uma guarda APENAS para o fallback mesh, antes da criacao dos modulos
SPIR-V. Sem mudancas em pipelines convencionais ou no jogo.

Referencia: zortos293/Lichii commit 7d3b3a5266c274f70140845b47c5023e0011d5de
"""
from pathlib import Path
import sys

source = Path(sys.argv[1]).resolve()
file = source / "src/video_core/renderer_vulkan/vk_pipeline_cache.cpp"
original = file.read_text(encoding="utf-8")

anchor = "    std::array<const Shader::Info*, Maxwell::MaxShaderStage> infos{};"
if original.count(anchor) != 1:
    raise SystemExit(
        f"Guarda #642: esperado 1 ponto de insercao, encontrados "
        f"{original.count(anchor)}. Nenhuma alteracao efetuada."
    )
for expected in (
    "mesh_emulation.emplace();",
    "mesh_emulation->has_task",
    "host_info.max_descriptor_set_storage_buffers",
    "Shader::NumDescriptors",
):
    # Shader::NumDescriptors is introduced by the fallback #569.
    if expected not in original:
        raise SystemExit(f"Guarda #642: pre-condicao ausente {expected!r}")

guard = """    // Leoitchii: port de Lichii #642. O fallback mesh emulado usa 1
    // storage buffer extra (mesh) ou 4 (task+mesh) no mesmo descriptor set.
    // A base Fritchii nao possui a checagem antiga do Lichii; guardamos
    // apenas o caminho emulado, para nao mudar pipelines convencionais.
    if (mesh_emulation) {
        const u32 set_limit = host_info.max_descriptor_set_storage_buffers;
        if (set_limit != 0) {
            size_t guest_storage_buffers{};
            for (size_t index = uses_vertex_a && uses_vertex_b ? 1 : 0;
                 index < Maxwell::MaxShaderProgram; ++index) {
                if (key.unique_hashes[index] != 0) {
                    guest_storage_buffers +=
                        Shader::NumDescriptors(programs[index].info.storage_buffers_descriptors);
                }
            }
            const size_t auxiliary_buffers{mesh_emulation->has_task ? 4U : 1U};
            if (auxiliary_buffers > set_limit ||
                guest_storage_buffers > set_limit - auxiliary_buffers) {
                throw Shader::NotImplementedException(
                    "Mesh fallback descriptor set exceeds limit: {} guest, {} auxiliary, max {}",
                    guest_storage_buffers, auxiliary_buffers, set_limit);
            }
        }
    }
"""
if original.count("Mesh fallback descriptor set exceeds limit") != 0:
    raise SystemExit("Guarda #642 ja inserida; falhando para evitar duplicata")
if original.index("mesh_emulation.emplace();") > original.index(anchor):
    raise SystemExit("Ordem do fallback inesperada; patch recusado")
candidate = original.replace(anchor, guard + anchor, 1)
if candidate.count("Mesh fallback descriptor set exceeds limit") != 1:
    raise SystemExit("Guarda #642 nao inserida corretamente")
file.write_text(candidate, encoding="utf-8", newline="\n")
print("Guarda Lichii #642 inserida somente para fallback mesh; Fritchii convencional intacto.")
