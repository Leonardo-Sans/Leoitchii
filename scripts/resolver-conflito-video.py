#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Resolução restrita de nx2_gsv.h Fritchii 4.1 vs Eglantine 1f52ac7.
Preserva m_end_queued e Nx2VideoInputQueue (gestão de pré-carregamento Fritchii),
adicionando o relógio de pacing de vídeo. Recusa divergências desconhecidas.
"""
from pathlib import Path
import re
import subprocess
import sys

source = Path(sys.argv[1]).resolve()
relative = "src/core/hle/service/nx2_gsv.h"
conflicts = subprocess.check_output(
    ["git", "-C", str(source), "diff", "--name-only", "--diff-filter=U"],
    text=True,
).splitlines()
if conflicts != [relative]:
    raise SystemExit(f"Conflitos inesperados, cancelando: {conflicts}")
target = source / relative
data = target.read_text(encoding="utf-8")
pat = re.compile(r"^<<<<<<< HEAD\n(.*?)^=======\n(.*?)^>>>>>>> [^\n]*\n", re.M | re.S)
matches = list(pat.finditer(data))
if len(matches) != 2:
    raise SystemExit(f"Esperados dois conflitos em {relative}, encontrados {len(matches)}")
first, second = matches
ours1, theirs1 = first.group(1), first.group(2)
ours2, theirs2 = second.group(1), second.group(2)
if ours1.strip() != "m_end_queued = false;" or theirs1.strip() != "m_clock_offset.reset();":
    raise SystemExit(f"Conflito A diferente do esperado: {ours1!r} vs {theirs1!r}")
if "m_decoded_frames{};" not in ours2 or "Nx2VideoInputQueue m_inputs;" not in ours2:
    raise SystemExit("Conflito B sem os campos Fritchii esperados")
if "u64 m_frames_dropped{};" not in theirs2 or "std::deque<Input> m_inputs;" not in theirs2:
    raise SystemExit("Conflito B sem os campos Eglantine esperados")

# Fritchii tem fila customizada com Empty()/Pop(), não std::deque<Input>.
replacement1 = ours1 + theirs1
replacement2 = ours2 + theirs2.replace("    std::deque<Input> m_inputs;\n", "")
out = data[:first.start()] + replacement1 + data[first.end():second.start()] + replacement2 + data[second.end():]
if out.count("m_inputs.empty()") != 1:
    raise SystemExit("Pacing não usa m_inputs.empty() exatamente uma vez; revisar implementação")
out = out.replace("m_inputs.empty()", "m_inputs.Empty()")
if any(x in out for x in ("<<<<<<< HEAD", "=======", ">>>>>>> ")):
    raise SystemExit("Marcadores de conflito remanescentes")
if out.count("Nx2VideoInputQueue m_inputs;") != 1 or out.count("m_clock_offset") < 4:
    raise SystemExit("Estruturas obrigatórias da fila e do relógio ausentes")
target.write_text(out, encoding="utf-8", newline="\n")
print("Resolvidos 2 conflitos: mantidos controle de EOS/fila Fritchii e pacing Eglantine.")
