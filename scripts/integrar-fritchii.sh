#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Integração rastreável; não resolve conflitos automaticamente.
set -euo pipefail

FRITCHII_REPO="https://github.com/Frizti/Fritchii.git"
FRITCHII_TAG="fritchii-v4.1"
FRITCHII_SHA="f6d42b87150678e001dbeb84679a9595935ce951"
LICHII_REPO="https://github.com/zortos293/Lichii.git"
LICHII_FIX_SHA="b7ff181f20a1a397999151b84750f65f417f2b45"
SOURCE_DIR="${1:-source}"

if [[ -e "$SOURCE_DIR" ]]; then
  echo "ERRO: '$SOURCE_DIR' ja existe; nao sobrescrever fontes." >&2
  exit 2
fi

echo "Clonando Fritchii da tag $FRITCHII_TAG..."
git clone --depth 1 --branch "$FRITCHII_TAG" --single-branch "$FRITCHII_REPO" "$SOURCE_DIR"
resolved_sha="$(git -C "$SOURCE_DIR" rev-parse HEAD)"
if [[ "$resolved_sha" != "$FRITCHII_SHA" ]]; then
  echo "ERRO: tag mudou! Esperado $FRITCHII_SHA, recebido $resolved_sha" >&2
  exit 3
fi

git -C "$SOURCE_DIR" checkout -B leoitchii-experimento "$FRITCHII_SHA"
git -C "$SOURCE_DIR" remote add lichii "$LICHII_REPO"
echo "Obtendo exclusivamente o commit de correção gráfica..."
git -C "$SOURCE_DIR" fetch --no-tags --depth=2 lichii "$LICHII_FIX_SHA"

git -C "$SOURCE_DIR" config user.name "Leoitchii Integration"
git -C "$SOURCE_DIR" config user.email "integration@users.noreply.github.com"

echo "Tentando portar a correção do Lichii..."
if ! git -C "$SOURCE_DIR" cherry-pick -x "$LICHII_FIX_SHA"; then
  echo "Conflitos detectados. Tentando resolução RESTRITA e verificada dos três trechos já auditados..."
  if python scripts/resolver_conflitos.py "$SOURCE_DIR"; then
    git -C "$SOURCE_DIR" add -- \
      src/video_core/renderer_vulkan/vk_graphics_pipeline.cpp \
      src/video_core/renderer_vulkan/vk_pipeline_cache.cpp \
      src/video_core/renderer_vulkan/vk_rasterizer.h
    GIT_EDITOR=true git -C "$SOURCE_DIR" cherry-pick --continue
    echo "Resolução restrita concluída; nenhuma outra divergência foi ignorada."
  else
  echo "ERRO: a correção não pôde ser aplicada sem conflitos."
  echo "Arquivos em conflito:"
  git -C "$SOURCE_DIR" diff --name-only --diff-filter=U || true
  git -C "$SOURCE_DIR" status --short || true
  echo "======= TRECHOS CONFLITANTES (diagnóstico, não execução) ======="
  while IFS= read -r file; do
    [[ -z "$file" ]] && continue
    echo "------- $file -------"
    (awk '/^<<<<<<< /{show=1} show{print NR ":" $0} /^>>>>>>> /{show=0}' "$SOURCE_DIR/$file" | head -n 500) || true
  done < <(git -C "$SOURCE_DIR" diff --name-only --diff-filter=U)
  echo "Nenhuma resolução automática foi aplicada."
  exit 4
  fi
fi

echo "Integração aplicada no commit local:"
git -C "$SOURCE_DIR" log -1 --format='%h %s'
echo "Aplicando correção mínima de nomes para compilador MSVC (/we4459)..."
python scripts/corrigir-frizti-settings.py "$SOURCE_DIR"
echo "Corrigindo nomes locais adicionais do núcleo gráfico para MSVC..."
python scripts/corrigir-erros-msvc-nucleo.py "$SOURCE_DIR"
echo "Adaptando RasterizerVulkan para nomes e assinatura da base Fritchii..."
python scripts/corrigir-rasterizer-fritchii.py "$SOURCE_DIR"
echo "Pronto para tentar compilar, ainda não validado em hardware real."
