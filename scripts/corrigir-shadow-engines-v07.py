#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Fix four MSVC /we4457 /we4458 errors from Fritchii 5.5 upstream.
Only rename local identifiers inside exact functions. Never turn off compiler checks.
"""
from pathlib import Path
import re
import sys

root = Path(sys.argv[1]).resolve()
kepler = root / "src/video_core/engines/kepler_compute.cpp"
maxwell = root / "src/video_core/engines/maxwell_3d.cpp"
changes = {p: p.read_text(encoding="utf-8") for p in [kepler, maxwell]}

def function_section(path, start, end, old, new, n, label):
    text = changes[path]
    if text.count(start) != 1 or text.count(end) != 1:
        raise SystemExit(f"{label}: function anchors changed; no files written")
    p = text.index(start)
    q = text.index(end, p + len(start))
    section = text[p:q]
    if section.count(old) != n:
        raise SystemExit(f"{label}: expected {n} occurrences; got {section.count(old)}")
    changes[path] = text[:p] + section.replace(old, new) + text[q:]


# KeplerCompute: member "state" shadows pointer used by the OoT network bypass.
start_k = "bool KeplerCompute::BypassOotNetwork(u64 program_id, u64 native_key) {"
end_k = "\nstd::atomic<u32> g_nx2_trace_draws_after_upscale{};"
content_k = changes[kepler]
if content_k.count(start_k) != 1 or content_k.count(end_k) != 1:
    raise SystemExit("Kepler bypass anchors changed; nothing written")
a = content_k.index(start_k)
b = content_k.index(end_k, a)
part = content_k[a:b]
if part.count("auto* const state = rasterizer->OotNetworkBypass();") != 1:
    raise SystemExit("Kepler bypass variable no longer matches")
if len(re.findall(r"\bstate\b", part)) != 7:
    raise SystemExit("Kepler bypass unexpected state identifiers")
part = re.sub(r"\bstate\b", "bypass_state", part)
changes[kepler] = content_k[:a] + part + content_k[b:]

# Maxwell3D::FrontDmaRead: avoid reusing function parameter "count" in diagnostics.
function_section(
    maxwell,
    "void Maxwell3D::FrontDmaRead(VideoCommon::GpuSplit& split, FrontState& fs, u32 macro,",
    "\nbool Maxwell3D::FrontDmaReadEarly(",
    "for (const u64 count : dispatch_checks) {\n                            dispatch_drains += count;\n                        }",
    "for (const u64 dispatch_count : dispatch_checks) {\n"
    "                            dispatch_drains += dispatch_count;\n                        }",
    1,
    "Maxwell FrontDmaRead diagnostics dispatch_checks",
)
function_section(
    maxwell,
    "void Maxwell3D::FrontDmaRead(VideoCommon::GpuSplit& split, FrontState& fs, u32 macro,",
    "\nbool Maxwell3D::FrontDmaReadEarly(",
    "for (const u64 count : dispatches.unbounded) {\n                            dispatches_unbounded += count;\n                        }",
    "for (const u64 dispatch_count : dispatches.unbounded) {\n"
    "                            dispatches_unbounded += dispatch_count;\n                        }",
    1,
    "Maxwell FrontDmaRead diagnostics unbounded",
)

# Maxwell3D::RunDrawBatch: member "state" shadows local reference; rename locally.
start_m = "void Maxwell3D::RunDrawBatch(Core::System& system, const u64* writes, u32 count, u32 repeats) {"
end_m = "\nbool Maxwell3D::FrontBatchWrite("
content_m = changes[maxwell]
if content_m.count(start_m) != 1 or content_m.count(end_m) != 1:
    raise SystemExit("Maxwell RunDrawBatch anchors changed; nothing written")
a = content_m.index(start_m)
b = content_m.index(end_m, a)
part = content_m[a:b]
if part.count("auto& state = draw_manager.draw_state;") != 1:
    raise SystemExit("Maxwell DrawBatch local state declaration changed")
if len(re.findall(r"\bstate\b", part)) != 11:
    raise SystemExit("Maxwell DrawBatch unexpected state identifiers")
part = re.sub(r"\bstate\b", "draw_batch_state", part)
changes[maxwell] = content_m[:a] + part + content_m[b:]

# Write only after all anchors and expected counts have passed.
for path, content in changes.items():
    path.write_text(content, encoding="utf-8", newline="\n")
print("Fritchii 5.5 MSVC errors C4457/C4458: four local shadowing sites corrected.")
