#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Add reversible A/B to Lichii #961 zero-page trim after verified port."""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
p = root / "src/core/device_memory.cpp"
s = p.read_text(encoding="utf-8")
old = """    zero_trim_thread = std::jthread{[this](std::stop_token stop) { TrimZeroPages(stop); }};"""
new = """    // Leoitchii v0.7: A/B da economia de RAM, sem precisar remover o port.
    const char* const trim_setting = std::getenv("LEOITCHII_ZERO_TRIM");
    if (trim_setting == nullptr || trim_setting[0] != '0') {
        zero_trim_thread = std::jthread{[this](std::stop_token stop) { TrimZeroPages(stop); }};
    }"""
if s.count(old) != 1 or s.count("#include <algorithm>") != 1:
    raise SystemExit("Port zero-page: ancora divergente, recusando edicao")
out = s.replace(old, new, 1).replace(
    "#include <algorithm>", "#include <algorithm>\n#include <cstdlib>", 1
)
p.write_text(out, encoding="utf-8", newline="\n")
print("Lichii #961: A/B opcional LEOITCHII_ZERO_TRIM=0 integrado")
