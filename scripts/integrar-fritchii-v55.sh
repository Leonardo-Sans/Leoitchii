#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Leoitchii v0.7 consolidated build; upstream source pinned, no blind cherry-picks.
set -euo pipefail
ROOT="${1:-source}"
FORK="https://github.com/Frizti/Fritchii.git"
TAG="fritchii-v5.5"
COMMIT="4012e5271e278b21cf8f56b97481dac2b777cd0d"
if [[ -e "$ROOT" ]]; then
  echo "ERRO: destino $ROOT ja existe; recusando sobrescrever." >&2
  exit 2
fi
git clone --depth 1 --branch "$TAG" --single-branch "$FORK" "$ROOT"
resolved="$(git -C "$ROOT" rev-parse HEAD)"
if [[ "$resolved" != "$COMMIT" ]]; then
  echo "ERRO: tag Fritchii v5.5 inesperada: $resolved" >&2
  exit 3
fi
# v5.5 includes mesh fallback (#569/#642/#841), VRAM memory budgets and staging,
# shader precompilation, graphics and UI fixes. Do not reapply old v0.6 patches
# when the upstream code has already changed.
test -f "$ROOT/src/video_core/renderer_vulkan/mesh_fallback_limits.h"
grep -q 'mesh_emulation.emplace' "$ROOT/src/video_core/renderer_vulkan/vk_pipeline_cache.cpp"
grep -q 'bool may_fail' "$ROOT/src/video_core/vulkan_common/vulkan_memory_allocator.cpp"
grep -q 'EDEN_NX2_PRECOMPILE' "$ROOT/src/video_core/nx2_precompile.cpp"
grep -q 'EDEN_NX2_SPLIT' "$ROOT/src/video_core/gpu_split.cpp"
grep -q 'EDEN_NX2_TC_LOG' "$ROOT/src/video_core/texture_cache/texture_cache.h"
grep -q 'EDEN_NX2_RESETFIX' "$ROOT/dist/nx2_switches.txt"
grep -q 'EDEN_NX2_FENCE_BATCH' "$ROOT/dist/nx2_switches.txt"
# Fritchii v5.5 upstream uses local variables that collide with Settings::values
# when MSVC treats C4459 as an error. Fix exact identifiers, not warning level.
python scripts/corrigir-shadow-frizti-v07.py "$ROOT"
python scripts/corrigir-shadow-gpusplit-v07.py "$ROOT"
# Keep proven AV1 Pascal fallback from v0.6 (adapted to current upstream).
python scripts/portar-av1-pascal-v06.py "$ROOT"
# Video 60 fps cutscene optional A/B; never silently enable the old v0.6 frame drop.
python scripts/portar-eglantine-video-v07.py "$ROOT"
python scripts/gerar-icone-leoitchii-v07.py "$ROOT/dist/leoitchii.ico"
python scripts/aplicar-identidade-laboratorio-v07.py "$ROOT"
git -C "$ROOT" diff --check
echo "Leoitchii v0.7 source consolidated; testing and Windows build still required."
