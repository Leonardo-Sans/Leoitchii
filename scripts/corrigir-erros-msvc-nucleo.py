#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Corrige sombreamento de variáveis locais (MSVC C4457/C4458) no Fritchii 4.1.

Somente três declarações específicas; preserva a semântica e rejeita entradas divergentes.
"""
import pathlib
import re
import sys

root = pathlib.Path(sys.argv[1]).resolve()

kepler = root / "src/video_core/engines/kepler_compute.cpp"
content = kepler.read_text(encoding="utf-8")
start = "bool KeplerCompute::BypassOotNetwork(u64 program_id, u64 native_key) {"
end = "std::atomic<u32> g_nx2_trace_draws_after_upscale{};"
if content.count(start) != 1 or content.count(end) != 1:
    raise SystemExit("Fritchii BypassOotNetwork mudou: não foi possível corrigir com segurança.")
prefix, rest = content.split(start, 1)
method, suffix = rest.split(end, 1)
if method.count("auto* const state = rasterizer->OotNetworkBypass();") != 1:
    raise SystemExit("Declaração inesperada do estado do bypass.")
uses = len(re.findall(r"\bstate\b", method))
if uses != 7:
    raise SystemExit(f"Ocorrências de state no método mudaram (esperado 7, atual {uses}).")
method = re.sub(r"\bstate\b", "bypass_state", method)
kepler_patched = prefix + start + method + end + suffix

maxwell = root / "src/video_core/engines/maxwell_3d.cpp"
original = maxwell.read_text(encoding="utf-8")
old_a = """for (const u64 count : dispatch_checks) {
                            dispatch_drains += count;
                        }"""
new_a = """for (const u64 dispatch_count : dispatch_checks) {
                            dispatch_drains += dispatch_count;
                        }"""
old_b = """for (const u64 count : dispatches.unbounded) {
                            dispatches_unbounded += count;
                        }"""
new_b = """for (const u64 dispatch_count : dispatches.unbounded) {
                            dispatches_unbounded += dispatch_count;
                        }"""
if original.count(old_a) != 1 or original.count(old_b) != 1:
    raise SystemExit("Laços de Maxwell3D mudaram: não foi possível corrigir com segurança.")
maxwell_patched = original.replace(old_a, new_a).replace(old_b, new_b)

kepler.write_text(kepler_patched, encoding="utf-8", newline="\n")
maxwell.write_text(maxwell_patched, encoding="utf-8", newline="\n")
print("MSVC C4457/C4458: renomeadas três variáveis locais sem mudar a lógica.")
