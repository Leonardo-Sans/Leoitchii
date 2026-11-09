#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Port mínimo Lichii #878: solta IR de compute antes de compilação síncrona.

O driver Vulkan compila um pipeline síncrono depois que o SPIR-V já está pronto.
Conservar IR e vetor SPIR-V nesse intervalo aumenta memória de pico; no Lichii
eles são liberados ANTES do driver entrar na compilação (até centenas de MiB).
Oportunidade para 16 GiB RAM. Não muda o shader resultante.

Rollback do fast path: LEOITCHII_IR_EARLY_FREE=0 (só desabilita o free,
não desfaz outras melhorias). Trechos devem corresponder ao Fritchii v4.1.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
pool = root / "src/shader_recompiler/object_pool.h"
cache = root / "src/video_core/renderer_vulkan/vk_pipeline_cache.cpp"
data = {p: p.read_text(encoding="utf-8") for p in (pool, cache)}

def patch(path, before, after, label):
    n = data[path].count(before)
    if n != 1:
        raise SystemExit(
            f"IR #878 {label}: esperado trecho único, achados {n}; não gravado."
        )
    data[path] = data[path].replace(before, after, 1)

patch(
    pool,
    """    void ReleaseContents() {""",
    """    /// Destrói objetos e devolve blocos de memória para compilação síncrona.
    /// Lichii #878: ReleaseContents apenas reaproveita a capacidade.
    void Free() {
        chunks.clear();
        chunks.shrink_to_fit();
        node = &chunks.emplace_back(new_chunk_size);
    }

    void ReleaseContents() {""",
    "ObjectPool.Free",
)
patch(
    cache,
    "    const std::vector<u32> code{EmitSPIRV(profile, program)};",
    "    std::vector<u32> code{EmitSPIRV(profile, program)};",
    "SPIRV mutável",
)
patch(
    cache,
    """    Common::ThreadWorker* const thread_worker{build_in_parallel ? &workers : nullptr};
    return {.pipeline = std::make_unique<ComputePipeline>(
                device, scheduler, vulkan_pipeline_cache, descriptor_pool, guest_descriptor_queue,
                descriptor_buffer_ring, thread_worker, statistics, &shader_notify, program.info,
                std::move(spv_module), key.unique_hash),""",
    """    Common::ThreadWorker* const thread_worker{build_in_parallel ? &workers : nullptr};
    // É preciso mover Info para não depender da IR destruída enquanto o driver compila.
    const Shader::Info info{std::move(program.info)};
    static const bool early_free_enabled = [] {
        const char* const setting = std::getenv("LEOITCHII_IR_EARLY_FREE");
        return setting == nullptr || setting[0] != '0';
    }();
    if (!thread_worker && early_free_enabled) {
        program = {};
        code = std::vector<u32>{};
        pools.block.Free();
        pools.inst.Free();
    }
    return {.pipeline = std::make_unique<ComputePipeline>(
                device, scheduler, vulkan_pipeline_cache, descriptor_pool, guest_descriptor_queue,
                descriptor_buffer_ring, thread_worker, statistics, &shader_notify, info,
                std::move(spv_module), key.unique_hash),""",
    "liberação antes do driver",
)
for path, new in data.items():
    path.write_text(new, encoding="utf-8", newline="\n")
print("IR compute (#878): liberação pré-driver adicionada; rollback por LEOITCHII_IR_EARLY_FREE=0.")
