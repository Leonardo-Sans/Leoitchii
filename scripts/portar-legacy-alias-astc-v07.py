#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Selective, reversible v0.6 Lichii #858 alias ticks + #296 ASTC guest scan.

Fritchii v5.5 changed the ASTC shader and image cache. Retain all those
improvements; do not overwrite the ASTC shader with the old v0.6 file.
Patch only guarded source anchors. Fail atomically on any source divergence.

Both optimizations default OFF while black textures / invisible furniture
are investigated. Enable separately in Leoitchii's Laboratory for A/B.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
paths = {
    "header": root / "src/video_core/texture_cache/image_base.h",
    "alias": root / "src/video_core/texture_cache/image_base.cpp",
    "cache": root / "src/video_core/texture_cache/texture_cache.h",
    "base": root / "src/video_core/texture_cache/texture_cache_base.h",
}
data = {key: path.read_text(encoding="utf-8") for key, path in paths.items()}


def once(key, before, after, name):
    n = data[key].count(before)
    if n != 1:
        raise SystemExit(f"v0.7 legacy-port {name}: expected one anchor, saw {n}; no files changed")
    data[key] = data[key].replace(before, after, 1)


once(
    "header",
    "    u64 modification_tick = 0;\n    size_t lru_index = SIZE_MAX;",
    """    u64 modification_tick = 0;
    /// Last modification tick of another image sharing this allocation (Lichii #858).
    u64 newest_alias_tick = 0;
    size_t lru_index = SIZE_MAX;""",
    "image alias tick",
)
once(
    "alias",
    """    lhs.aliased_images.push_back(std::move(lhs_alias));
    rhs.aliased_images.push_back(std::move(rhs_alias));""",
    """    lhs.aliased_images.push_back(std::move(lhs_alias));
    rhs.aliased_images.push_back(std::move(rhs_alias));
    // Newly linked images may already contain newer GPU writes.
    lhs.newest_alias_tick = (std::max)(lhs.newest_alias_tick, rhs.modification_tick);
    rhs.newest_alias_tick = (std::max)(rhs.newest_alias_tick, lhs.modification_tick);""",
    "alias links",
)
once(
    "cache",
    "namespace VideoCommon {\n",
    """namespace VideoCommon {

// Leoitchii v0.6/Lichii #858: optional fast alias synchronization.
// OFF by default until black textures and furniture are regression-tested.
[[nodiscard]] inline bool LeoitchiiAliasFastEnabled() {
    static const bool enabled = [] {
        const char* value = std::getenv("LEOITCHII_ALIAS_FAST");
        return value != nullptr && value[0] == '1';
    }();
    return enabled;
}

// Leoitchii v0.6/Lichii #296: optional ASTC guest scan with no ReadBlock copy.
// The original Fritchii 5.5 path is preserved for rollback.
[[nodiscard]] inline bool LeoitchiiAstcDirectScanEnabled() {
    static const bool enabled = [] {
        const char* value = std::getenv("LEOITCHII_ASTC_DIRECT_SCAN");
        return value != nullptr && value[0] == '1';
    }();
    return enabled;
}
""",
    "A/B runtime flags",
)
once(
    "cache",
    """    image.modification_tick = ++modification_tick;
    image.last_write_frame = RenderFrame();
    if (!clearing_render_targets) {
        image.drawn_since_clear = true;
    }
}""",
    """    image.modification_tick = ++modification_tick;
    image.last_write_frame = RenderFrame();
    if (!clearing_render_targets) {
        image.drawn_since_clear = true;
    }
    if (LeoitchiiAliasFastEnabled()) {
        for (const AliasedImage& alias : image.aliased_images) {
            slot_images[alias.id].newest_alias_tick = image.modification_tick;
        }
    }
}""",
    "MarkModification v5.5",
)
once(
    "cache",
    """void TextureCache<P>::SynchronizeAliases(ImageId image_id) {
    boost::container::small_vector<const AliasedImage*, 8> aliased_images;
    Image& image = slot_images[image_id];
    bool any_rescaled = True(image.flags & ImageFlagBits::Rescaled);""",
    """void TextureCache<P>::SynchronizeAliases(ImageId image_id) {
    boost::container::small_vector<const AliasedImage*, 8> aliased_images;
    Image& image = slot_images[image_id];
    if (LeoitchiiAliasFastEnabled() &&
        image.newest_alias_tick <= image.modification_tick) {
        return;
    }
    bool any_rescaled = True(image.flags & ImageFlagBits::Rescaled);""",
    "alias unchanged early exit",
)
once(
    "cache",
    """    image.modification_tick = most_recent_tick;
    if (any_modified) {""",
    """    image.modification_tick = most_recent_tick;
    if (LeoitchiiAliasFastEnabled()) {
        for (const AliasedImage& alias : image.aliased_images) {
            ImageBase& other = slot_images[alias.id];
            other.newest_alias_tick = (std::max)(other.newest_alias_tick, most_recent_tick);
        }
    }
    if (any_modified) {""",
    "alias propagation on synchronization",
)
once(
    "base",
    "    std::vector<u8> astc_scan_buffer;",
    "    Common::ScratchBuffer<u8> astc_scan_buffer;",
    "ASTC scratch buffer",
)
once(
    "cache",
    """                astc_scan_buffer.resize(scan_bytes);
                gpu_memory->ReadBlockUnsafe(gpu_addr, astc_scan_buffer.data(), scan_bytes);
                new_info.astc_opaque = AstcDataLooksOpaque(astc_scan_buffer);""",
    """                if (LeoitchiiAstcDirectScanEnabled()) {
                    // GuestMemory uses the direct mapped span when available; ScratchBuffer
                    // backs the read when it is not contiguous. Avoid unconditional copying.
                    Tegra::Memory::GpuGuestMemory<u8, Tegra::Memory::GuestMemoryFlags::UnsafeRead>
                        scan_data(*gpu_memory, gpu_addr, scan_bytes, &astc_scan_buffer);
                    new_info.astc_opaque = AstcDataLooksOpaque(
                        std::span<const u8>{scan_data.data(), scan_data.size()});
                } else {
                    // Exact Fritchii v5.5 behavior, preserved as a rollback path.
                    astc_scan_buffer.resize(scan_bytes);
                    gpu_memory->ReadBlockUnsafe(gpu_addr, astc_scan_buffer.data(), scan_bytes);
                    new_info.astc_opaque = AstcDataLooksOpaque(
                        std::span<const u8>{astc_scan_buffer.data(), scan_bytes});
                }""",
    "ASTC zero-copy guest scan",
)

# The old ASTC decoder from Lichii #296 is intentionally NOT imported.
# It predates the later Fritchii v5.5 image extent and bounds fixes.
for key, path in paths.items():
    path.write_text(data[key], encoding="utf-8", newline="\n")
print("v0.6 #858 alias ticks + #296 ASTC guest scan ported over v5.5, both OFF by default.")
