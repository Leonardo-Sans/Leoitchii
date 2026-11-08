#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Troca somente nomes locais que acionam C4459 no MSVC (Fritchii v4.1).

A alteração preserva o comportamento e falha se o upstream modificar as
ocorrências previstas. Não modifica as opções do compilador.
"""
import pathlib
import sys

root = pathlib.Path(sys.argv[1]).resolve()
target = root / "src/common/frizti_settings.cpp"
original = target.read_text(encoding="utf-8")
current = original

replacements = (
    ("TunedSettings(Values& values)", "TunedSettings(Values& settings_values)", 1),
    ("&values.", "&settings_values.", 15),
    ("FixDockedController(Values& values)", "FixDockedController(Values& settings_values)", 1),
    ("auto& player = values.players.GetValue(true)[0];",
     "auto& player = settings_values.players.GetValue(true)[0];", 1),
    ("if (values.use_docked_mode.GetValue(true)",
     "if (settings_values.use_docked_mode.GetValue(true)", 1),
    ("std::map<std::string, std::string> values;",
     "std::map<std::string, std::string> mapped_values;", 2),
    ("values.emplace(", "mapped_values.emplace(", 2),
    ("return values;", "return mapped_values;", 2),
)
for before, after, expected in replacements:
    actual = current.count(before)
    if actual != expected:
        raise SystemExit(
            f"{target.name}: esperado {expected} ocorrência(s) de {before!r}, recebido {actual};"
            " código mudou, correção não aplicada"
        )
    current = current.replace(before, after)

if current == original:
    raise SystemExit("Nenhuma alteração foi necessária, revisar pressupostos.")
target.write_text(current, encoding="utf-8", newline="\n")
print("C4459: variáveis locais renomeadas, sem desativar warnings; comportamento preservado.")
