#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Port diagnostic intent of Lichii #807 to Fritchii v5.5, no GPU behavior changed.

Logs VK_ERROR_OUT_OF_HOST_MEMORY once per session with the OS-reported
committed memory figures. Inline helper avoids modifying upstream CMake target.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
vulkan = root / "src/video_core/renderer_vulkan"
compute = vulkan / "vk_compute_pipeline.cpp"
graphics = vulkan / "vk_graphics_pipeline.cpp"
header = vulkan / "leoitchii_host_memory_failure.h"
if header.exists():
    raise SystemExit("Lichii #807 diagnostic header already exists, refusing duplicate")
initial = {compute: compute.read_text(encoding="utf-8"),
           graphics: graphics.read_text(encoding="utf-8")}
changes = dict(initial)

def once(path, before, after, desc):
    n = changes[path].count(before)
    if n != 1:
        raise SystemExit(f"Lichii #807 {desc}: expected exactly one anchor, found {n}")
    changes[path] = changes[path].replace(before, after, 1)

include = '#include "video_core/renderer_vulkan/leoitchii_host_memory_failure.h"\n'
for p in (compute, graphics):
    once(p,
         '#include "video_core/renderer_vulkan/pipeline_helper.h"\n',
         include + '#include "video_core/renderer_vulkan/pipeline_helper.h"\n',
         "include")

once(
    compute,
    '            LOG_CRITICAL(Render_Vulkan, "Adreno rejected compute shader {:016X}: {}", shader_hash,\n                         exception.what());',
    '            LOG_CRITICAL(Render_Vulkan, "Driver rejected compute shader {:016X}: {}", shader_hash,\n                         exception.what());\n'
    '            ReportLeoitchiiHostMemoryFailure(exception.GetResult());',
    "compute failure",
)
once(
    graphics,
    """                         device.GetMaxTessellationPatchSize());
            throw;
        }
        if (pipeline_statistics && pipeline) {""",
    """                         device.GetMaxTessellationPatchSize());
            ReportLeoitchiiHostMemoryFailure(exception.GetResult());
            throw;
        }
        if (pipeline_statistics && pipeline) {""",
    "graphics failure",
)
body = r"""// SPDX-License-Identifier: GPL-3.0-or-later
// Leoitchii v0.7: diagnostic port of Lichii #807 (ffb12c4).
// Logs only: no changes to pipeline allocation, fallback, or exception handling.
#pragma once

#include <atomic>
#include <vulkan/vulkan_core.h>
#include "common/logging.h"
#include "common/memory_detect.h"

namespace Vulkan {

inline void ReportLeoitchiiHostMemoryFailure(VkResult result) {
    if (result != VK_ERROR_OUT_OF_HOST_MEMORY) {
        return;
    }
    static std::atomic_flag reported = ATOMIC_FLAG_INIT;
    if (reported.test_and_set(std::memory_order_relaxed)) {
        return;
    }
#ifdef _WIN32
    const Common::ProcessMemoryUsage usage = Common::GetProcessMemoryUsage();
    if (usage.system_commit_limit != 0) {
        constexpr double GiB = 1024.0 * 1024.0 * 1024.0;
        LOG_CRITICAL(Render_Vulkan,
                     "Leoitchii: driver returned VK_ERROR_OUT_OF_HOST_MEMORY building a "
                     "pipeline. OS reports committed {:.1f} / limit {:.1f} GiB. "
                     "If committed is close to limit, check Windows pagefile settings. "
                     "Missing shader pipelines may leave objects invisible.",
                     static_cast<double>(usage.system_commit) / GiB,
                     static_cast<double>(usage.system_commit_limit) / GiB);
        return;
    }
#endif
    LOG_CRITICAL(Render_Vulkan,
                 "Leoitchii: driver returned VK_ERROR_OUT_OF_HOST_MEMORY building a "
                 "shader pipeline. Check RAM and system commit/pagefile limit.");
}

} // namespace Vulkan
"""
for p, text in changes.items():
    p.write_text(text, encoding="utf-8", newline="\n")
header.write_text(body, encoding="utf-8", newline="\n")
print("Lichii #807: diagnostic log on host-memory pipeline errors, without GPU behavior changes")
