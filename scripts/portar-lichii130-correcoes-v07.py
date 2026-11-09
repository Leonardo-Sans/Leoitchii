#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Ports exatos dos Lichii #957 e #984 sobre Fritchii v5.5.

#957: ReserveRange nunca acessa indice alem do limite superior da GPU VA.
#984: evita use-after-free na translation cache quando DeviceMemoryManager recicla endereco.
Falha antes de escrever se a base divergir.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
table = root / "src/common/multi_level_page_table.inc"
manager = root / "src/core/device_memory_manager.h"
original = {p: p.read_text(encoding="utf-8") for p in (table, manager)}
data = dict(original)


def once(path, old, new, label):
    matches = data[path].count(old)
    if matches != 1:
        raise SystemExit(f"Lichii #957/#984 {label}: esperado 1 trecho, encontrado {matches}. Nenhum arquivo salvo.")
    data[path] = data[path].replace(old, new, 1)


once(
    table,
    """void MultiLevelPageTable<BaseAddr>::ReserveRange(u64 start, std::size_t size) {
    const u64 new_start = start >> first_level_shift;
    const u64 new_end = (start + size) >> first_level_shift;""",
    """void MultiLevelPageTable<BaseAddr>::ReserveRange(u64 start, std::size_t size) {
    // Lichii #957: o intervalo e semiaberto; nao reservar alem do ultimo indice.
    if (size == 0) {
        return;
    }
    const u64 new_start = start >> first_level_shift;
    const u64 new_end = (start + size - 1) >> first_level_shift;""",
    "page table overflow",
)
once(
    manager,
    "    std::atomic<u64> translation_generation{1}; ///< Bumped by Map and Unmap",
    """    // Lichii #984: prevenir traducoes obsoletas quando o manager reutiliza endereco.
    static inline std::atomic<u64> next_generation_base{1};
    std::atomic<u64> translation_generation{next_generation_base.fetch_add(1ULL << 32)};""",
    "translation use-after-free",
)
for path, content in data.items():
    path.write_text(content, encoding="utf-8", newline="\n")
print("Lichii #957 e #984 aplicados: limites da page table e geracoes de traducao.")
