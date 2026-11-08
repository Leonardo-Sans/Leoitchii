#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Resolução limitada às 3 divergências examinadas no Fritchii v4.1 e PR Lichii #569.
Falha fechada se a forma ou a lista de conflitos mudar.
"""
import pathlib
import re
import subprocess
import sys

root = pathlib.Path(sys.argv[1]).resolve()
expected = {
    "src/video_core/renderer_vulkan/vk_graphics_pipeline.cpp": (
        ("[[maybe_unused]] auto& stage_ci", "mesh_emulation && mesh_emulation->has_task"), "theirs"),
    "src/video_core/renderer_vulkan/vk_pipeline_cache.cpp": (
        ("return nullptr;", "mesh_unsupported = true;"), "theirs"),
    "src/video_core/renderer_vulkan/vk_rasterizer.h": (
        ("VideoCommon::OotNetwork::BypassState oot_network_bypass;", "struct MeshArena"), "combine"),
}

actual = subprocess.check_output(
    ["git", "-C", str(root), "diff", "--name-only", "--diff-filter=U"], text=True
).splitlines()
if set(actual) != set(expected):
    raise SystemExit(f"Conflitos diferentes do previsto. Esperados: {sorted(expected)}; atuais: {actual}")

pattern = re.compile(r"(?m)^<<<<<<< HEAD\n(.*?)^=======\n(.*?)^>>>>>>> [^\n]*\n", re.S | re.M)
replacement = {}
for relative, (checks, action) in expected.items():
    p = root / relative
    original = p.read_text(encoding="utf-8")
    matches = list(pattern.finditer(original))
    if len(matches) != 1:
        raise SystemExit(f"Esperado 1 bloco de conflito em {relative}, recebido {len(matches)}")
    m = matches[0]
    ours, theirs = m.group(1), m.group(2)
    if checks[0] not in ours or checks[1] not in theirs:
        raise SystemExit(f"Conteúdo inesperado no conflito de {relative}")
    if "<<<<<<< " in ours + theirs or ">>>>>>> " in ours + theirs:
        raise SystemExit(f"Marcadores de conflito aninhados em {relative}")
    # Na pipeline: novo caminho de emulação substitui o salto antigo.
    # No cache: mantém sinalização de emulação em vez de descartar a pipeline.
    # No rasterizer: guarda o estado do bypass OoT e acrescenta o estado do fallback.
    resolved = (ours + theirs) if action == "combine" else theirs
    candidate = original[:m.start()] + resolved + original[m.end():]
    if "<<<<<<< " in candidate or ">>>>>>> " in candidate:
        raise SystemExit(f"Marcadores restantes após tentativa em {relative}")
    replacement[p] = candidate
for p, value in replacement.items():
    p.write_text(value, encoding="utf-8", newline="\n")
print("Três blocos esperados resolvidos sem ignorar outros conflitos.")
