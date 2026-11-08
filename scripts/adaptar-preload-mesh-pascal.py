#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Leoitchii v0.4: permite preload de pipelines mesh emulados na GPU Pascal.

Fritchii v4.1 descartava todos os registros task/mesh ao ler o cache de disco
quando VK_EXT_mesh_shader nao estava presente. O port do Lichii PR #569 agora
suporta um subconjunto por compute, mas o filtro antigo impediria o preload.
Deixamos a validacao real de elegibilidade em CreateGraphicsPipeline(), que ja
aceita/rejeita o fallback conforme recursos exigidos.

Escopo: apenas drivers NVIDIA sem VK_EXT_mesh_shader. Demais GPUs continuam com
o comportamento da v0.2. Variavel LEOITCHII_MESH_DISK_CACHE=0 restaura o filtro.
Nao altera resolucao, shaders do jogo, saves, nem modo NoSharpening.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
p = root / "src/video_core/renderer_vulkan/vk_pipeline_cache.cpp"
before = p.read_text(encoding="utf-8")
old = """        if (!device.IsExtMeshShaderSupported() &&
            std::ranges::any_of(envs, [](const FileEnvironment& env) {
                return env.ShaderStage() == Shader::Stage::Task ||
                       env.ShaderStage() == Shader::Stage::Mesh;
            })) {
            return;
        }"""
new = """        // Leoitchii: NVIDIA Pascal nao possui VK_EXT_mesh_shader, mas o port
        // do Lichii PR #569 compila parte desses pipelines via compute. O filtro
        // original do Fritchii descartava-os ANTES de tentar o fallback, forçando
        // recompilacao apos reiniciar o emulador. Deixe CreateGraphicsPipeline
        // validar individualmente a elegibilidade durante o preload.
        if (!device.IsExtMeshShaderSupported() &&
            std::ranges::any_of(envs, [](const FileEnvironment& env) {
                return env.ShaderStage() == Shader::Stage::Task ||
                       env.ShaderStage() == Shader::Stage::Mesh;
            })) {
            static const bool mesh_disk_cache_enabled = [] {
                const char* value = std::getenv("LEOITCHII_MESH_DISK_CACHE");
                return value == nullptr || value[0] != '0';
            }();
            if (device.GetDriverID() != VK_DRIVER_ID_NVIDIA_PROPRIETARY ||
                !mesh_disk_cache_enabled) {
                return;
            }
            static std::atomic<bool> logged_mesh_preload{};
            if (!logged_mesh_preload.exchange(true, std::memory_order_relaxed)) {
                LOG_INFO(Render_Vulkan,
                         "Leoitchii: mesh compute fallback eligible for NVIDIA disk preload; "
                         "LEOITCHII_MESH_DISK_CACHE=0 disables the experiment");
            }
        }"""
if before.count(old) != 1:
    raise SystemExit(f"Filtro mesh do Fritchii mudou (achados {before.count(old)}): recusando patch")
# Verify imported compute-mesh emulation exists, before touching the source.
sentinels = (
    "mesh_emulation.emplace();",
    "mesh_unsupported = true;",
    "ReportUnsupportedMeshPipeline(key, programs);",
)
for required in sentinels:
    if required not in before:
        raise SystemExit("Fallback Lichii nao identificado: " + required)
after = before.replace(old, new, 1)
assert after.count("LEOITCHII_MESH_DISK_CACHE") == 2
assert after.count("VK_DRIVER_ID_NVIDIA_PROPRIETARY") >= 1
p.write_text(after, encoding="utf-8", newline="\n")
print("Preload mesh da NVIDIA habilitado sob teste. Outros drivers intocados.")
