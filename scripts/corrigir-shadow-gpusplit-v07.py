#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""MSVC /we4458 fix in Fritchii v5.5 GPU split, without changing code behavior.
The parameter 'writes' in DrawBatch shadows GpuSplit::writes member.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
p = root / "src/video_core/gpu_split.h"
src = p.read_text(encoding="utf-8")
before = """    void DrawBatch(Tegra::Engines::EngineInterface* engine, const u64* writes, u32 count,
                   u32 repeats, Effect effect) {
        SelectEngine(engine);
        u64* const entry = Reserve(1 + size_t{count});
        entry[0] = static_cast<u64>(Kind::DrawBatch) | (u64{count & 0xff} << 8) |
                   (u64{repeats} << 32);
        std::memcpy(entry + 1, writes, size_t{count} * sizeof(u64));"""
after = """    void DrawBatch(Tegra::Engines::EngineInterface* engine, const u64* batch_writes, u32 count,
                   u32 repeats, Effect effect) {
        SelectEngine(engine);
        u64* const entry = Reserve(1 + size_t{count});
        entry[0] = static_cast<u64>(Kind::DrawBatch) | (u64{count & 0xff} << 8) |
                   (u64{repeats} << 32);
        std::memcpy(entry + 1, batch_writes, size_t{count} * sizeof(u64));"""
count = src.count(before)
if count != 1:
    raise SystemExit(f"GpuSplit::DrawBatch: esperado 1 bloco, achados {count}; nada alterado")
p.write_text(src.replace(before, after, 1), encoding="utf-8", newline="\n")
print("MSVC C4458 in gpu_split.h: only parameter rename, no behavior change")
