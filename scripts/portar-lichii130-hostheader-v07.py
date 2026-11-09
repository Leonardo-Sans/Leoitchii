#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Port only API declarations of Lichii #961 onto Fritchii 5.5's extended host_memory.h."""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
p = root / "src/common/host_memory.h"
s = p.read_text(encoding="utf-8")
before = """    void HintCold(size_t physical_offset, size_t length,
                  std::optional<size_t> virtual_offset) const;
"""
after = before + """    /// Lichii #961: zero guest pages leave Windows working set, preserving contents.
    /// Returns {resident bytes scanned, bytes trimmed}.
    std::pair<size_t, size_t> TrimZeroPages() const;

    /// Bytes zero-filled by ClearBackingRegion since process start.
    static u64 ZeroFilledBytes() noexcept;
"""
if s.count(before) != 1 or s.count("#include <utility>") != 1:
    raise SystemExit("Lichii #961: Fritchii host_memory.h inesperado; nao alterar")
p.write_text(s.replace(before, after, 1), encoding="utf-8", newline="\n")
print("Lichii #961 header declarations adapted (Fritchii already includes utility).")
