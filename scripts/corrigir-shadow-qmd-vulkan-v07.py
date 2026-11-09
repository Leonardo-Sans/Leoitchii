#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Correct Fritchii v5.5 MSVC C4458 locals discovered by Windows run 42710304332.

No suppression of /we4458. Strict matching and atomic validation of both files.
# QMD local matched hides a data member; Vulkan local device hides class member.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
qmd = root / "src/video_core/nx2_qmd_prediction.cpp"
vulkan = root / "src/video_core/renderer_vulkan/vk_rasterizer.cpp"
original = {p: p.read_text(encoding="utf-8") for p in (qmd, vulkan)}
changes = dict(original)

def replace_section(path, begin, end, old, new, expected, label):
    s = changes[path]
    if s.count(begin) != 1:
        raise SystemExit(f"{label}: beginning anchor count {s.count(begin)}")
    start = s.index(begin)
    stop = s.find(end, start + len(begin))
    if stop == -1:
        raise SystemExit(f"{label}: end anchor missing")
    part = s[start:stop]
    if part.count(old) != expected:
        raise SystemExit(f"{label}: expected {expected} occurrences, saw {part.count(old)}")
    changes[path] = s[:start] + part.replace(old, new) + s[stop:]

replace_section(
    qmd,
    "void ScanAudit(const AuditKey* key) {",
    "    /// An unpredicted back release",
    "u32 matched = 0;", "u32 matched_audits = 0;", 1, "QMD C4458 declaration",
)
replace_section(
    qmd,
    "void ScanAudit(const AuditKey* key) {",
    "    /// An unpredicted back release",
    "++matched;", "++matched_audits;", 1, "QMD C4458 increment",
)
replace_section(
    qmd,
    "void ScanAudit(const AuditKey* key) {",
    "    /// An unpredicted back release",
    "key->device, matched,", "key->device, matched_audits,", 1, "QMD C4458 log",
)
replace_section(
    vulkan,
    "if (const auto indirect = kepler_compute->GetIndirectComputeAddress()) {",
    "        split.ConfirmDispatch();",
    "if (const auto device = gpu_memory->GpuToCpuAddress(*indirect)) {",
    "if (const auto indirect_device = gpu_memory->GpuToCpuAddress(*indirect)) {",
    1, "Vulkan C4458 declaration",
)
replace_section(
    vulkan,
    "if (const auto indirect = kepler_compute->GetIndirectComputeAddress()) {",
    "        split.ConfirmDispatch();",
    "split.RecordDispatchWrite(*device, 12);",
    "split.RecordDispatchWrite(*indirect_device, 12);",
    1, "Vulkan C4458 call",
)
for path, changed in changes.items():
    if changed == original[path]:
        raise SystemExit(f"No changes in {path}")
for path, changed in changes.items():
    path.write_text(changed, encoding="utf-8", newline="\n")
print("MSVC C4458: QMD matched and Vulkan device locals renamed, no semantic changes.")
