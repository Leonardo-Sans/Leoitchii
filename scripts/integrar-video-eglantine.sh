#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Port isolado da correção de sincronismo dos vídeos do Eglantine.
set -euo pipefail

SOURCE_DIR="${1:-source}"
EGLANTINE_REPO="https://github.com/Eglantine-Community/Eglantine.git"
MOVIE_FIX_SHA="1f52ac7e2efe7c4b3c8b93facfc0208b4378f6f4"

test -d "$SOURCE_DIR/.git" || { echo "Fonte não encontrada: $SOURCE_DIR"; exit 2; }

git -C "$SOURCE_DIR" remote add eglantine "$EGLANTINE_REPO"
git -C "$SOURCE_DIR" fetch --no-tags --depth=2 eglantine "$MOVIE_FIX_SHA"

echo "Aplicando drop de quadros atrasados nos vídeos da NX2, sem alterar a velocidade do jogo..."
if ! git -C "$SOURCE_DIR" cherry-pick -x "$MOVIE_FIX_SHA"; then
  echo "ERRO: conflito no port de vídeo; intervenção manual necessária." >&2
  git -C "$SOURCE_DIR" diff --name-only --diff-filter=U || true
  git -C "$SOURCE_DIR" status --short || true
  exit 4
fi
if ! grep -q 'EDEN_NX2_VDEC_PACE' "$SOURCE_DIR/src/core/hle/service/nx2_gsv.h"; then
  echo "ERRO: patch de pacing não foi integrado como previsto." >&2
  exit 5
fi
echo "Port Eglantine aplicado: sincroniza filmes descartando quadros atrasados; não aumenta FPS 3D."
