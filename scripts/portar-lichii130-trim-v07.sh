#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Reproduce the reviewed upstream Lichii #961 all-zero-page trimming port.
# Never guess source offsets or partially apply on a conflict.
set -euo pipefail
ROOT="\${1:-source}"
SHA="2b30c2cb1ceb8f9a6e385b7cea45705dca07b722"
LICHII_URL="https://github.com/zortos293/Lichii.git"
git -C "$ROOT" fetch --no-tags --depth=2 "$LICHII_URL" "$SHA"
if ! git -C "$ROOT" cat-file -e "$SHA^{commit}"; then
  echo "Lichii #961 commit não encontrado" >&2
  exit 4
fi
PATCH="$(mktemp)"
trap 'rm -f "$PATCH"' EXIT
git -C "$ROOT" show --format= --no-ext-diff "$SHA" -- \
  src/common/host_memory.cpp \
  src/common/host_memory.h \
  src/core/device_memory.cpp \
  src/core/device_memory.h \
  src/tests/common/host_memory.cpp > "$PATCH"
if ! git -C "$ROOT" apply --check --recount "$PATCH"; then
  echo "INCOMPATIVEL: Lichii #961 exige adaptacao de conflitos com Fritchii 5.5. Nenhum patch aplicado." >&2
  exit 5
fi
git -C "$ROOT" apply --recount "$PATCH"
python scripts/alternar-trim-zero-v07.py "$ROOT"
echo "Port Lichii #961 aplicado integralmente, com rollback por LEOITCHII_ZERO_TRIM=0."
