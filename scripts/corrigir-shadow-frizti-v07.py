#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Fix frizti_settings.cpp MSVC /we4459 without suppressing diagnostics.
Fritchii v5.5's Settings::Frizti namespace imports Settings::values; local
parameters named 'values' are an error with this project's /we4459.
The patch only renames local variables; no emulation behavior is changed.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
p = root / "src/common/frizti_settings.cpp"
s = p.read_text(encoding="utf-8")
out = s

def scoped(begin, end, old, new, expected):
    global out
    assert out.count(begin) == 1, f"Missing function {begin}"
    a = out.index(begin)
    b = out.index(end, a + len(begin))
    segment = out[a:b]
    assert segment.count(old) == expected, (begin, old, segment.count(old))
    out = out[:a] + segment.replace(old, new) + out[b:]

scoped("std::vector<BasicSetting*> TunedSettings(Values& values) {",
       "\nstd::string SerializeRecord(", "values", "tuned_values", 18)
scoped("std::vector<Change> FixDockedController(Values& values) {",
       "\nstd::map<std::string, std::string> GlobalValues(", "values", "controller_values", 3)
scoped("std::map<std::string, std::string> GlobalValues(",
       "\nstd::map<std::string, std::string> PerGameValues(",
       "values", "collected", 3)
scoped("std::map<std::string, std::string> PerGameValues(",
       "\nstd::string FormatChanges(",
       "values", "collected", 3)
assert out != s and out.count("Values& values") == 0
p.write_text(out, encoding="utf-8", newline="\n")
print("Fritchii 5.5: MSVC C4459 shadowing fixes (local renames only).")
