#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Compare production ports from Lichii 130 to the already patched Fritchii 5.5.
# Audit only. No changes; no runtime claims; source remains unchanged.
set -euo pipefail
ROOT="${1:-source}"
REPO="https://github.com/zortos293/Lichii.git"
git -C "$ROOT" fetch --no-tags --depth=32 "$REPO" refs/tags/build-130
echo "===== Lichii 130 forward-compatibility check (no file modified) ====="
(
  echo "[PR #979]"
  patch="$(mktemp)"
  git -C "$ROOT" show --format= --no-ext-diff "5837d06467fd50c0314185650f4ca3748d5df7ad" -- src/video_core > "$patch"
  if [[ ! -s "$patch" ]]; then
    echo "NO_RELEVANT_PATCH"
  elif output=$(git -C "$ROOT" apply --check --recount "$patch" 2>&1); then
    echo "APPLIES_CLEANLY (still requires dependency and behavior audit)"
  else
    echo "CONFLICTS: $(echo "$output" | grep -c '^error:' || true) portions"
    echo "$output" | grep '^error:' | head -n 14 || true
  fi
  rm -f "$patch"
)
(
  echo "[PR #1014]"
  patch="$(mktemp)"
  git -C "$ROOT" show --format= --no-ext-diff "a551b80888dacfc71bbdc2b2d0b81702d656c04e" -- src/video_core > "$patch"
  if [[ ! -s "$patch" ]]; then
    echo "NO_RELEVANT_PATCH"
  elif output=$(git -C "$ROOT" apply --check --recount "$patch" 2>&1); then
    echo "APPLIES_CLEANLY (still requires dependency and behavior audit)"
  else
    echo "CONFLICTS: $(echo "$output" | grep -c '^error:' || true) portions"
    echo "$output" | grep '^error:' | head -n 14 || true
  fi
  rm -f "$patch"
)
(
  echo "[PR #949]"
  patch="$(mktemp)"
  git -C "$ROOT" show --format= --no-ext-diff "a4f62873277556960b5edc4c000f8ad482e5fac6" -- src/video_core > "$patch"
  if [[ ! -s "$patch" ]]; then
    echo "NO_RELEVANT_PATCH"
  elif output=$(git -C "$ROOT" apply --check --recount "$patch" 2>&1); then
    echo "APPLIES_CLEANLY (still requires dependency and behavior audit)"
  else
    echo "CONFLICTS: $(echo "$output" | grep -c '^error:' || true) portions"
    echo "$output" | grep '^error:' | head -n 14 || true
  fi
  rm -f "$patch"
)
(
  echo "[PR #1028]"
  patch="$(mktemp)"
  git -C "$ROOT" show --format= --no-ext-diff "0b83798bf6e7e2440568b7cf69646ae45d681b11" -- src/video_core > "$patch"
  if [[ ! -s "$patch" ]]; then
    echo "NO_RELEVANT_PATCH"
  elif output=$(git -C "$ROOT" apply --check --recount "$patch" 2>&1); then
    echo "APPLIES_CLEANLY (still requires dependency and behavior audit)"
  else
    echo "CONFLICTS: $(echo "$output" | grep -c '^error:' || true) portions"
    echo "$output" | grep '^error:' | head -n 14 || true
  fi
  rm -f "$patch"
)
(
  echo "[PR #1056]"
  patch="$(mktemp)"
  git -C "$ROOT" show --format= --no-ext-diff "1a5e995a38679e0f4f7e320f9ec6a5a2f4e4ef1e" -- src/video_core > "$patch"
  if [[ ! -s "$patch" ]]; then
    echo "NO_RELEVANT_PATCH"
  elif output=$(git -C "$ROOT" apply --check --recount "$patch" 2>&1); then
    echo "APPLIES_CLEANLY (still requires dependency and behavior audit)"
  else
    echo "CONFLICTS: $(echo "$output" | grep -c '^error:' || true) portions"
    echo "$output" | grep '^error:' | head -n 14 || true
  fi
  rm -f "$patch"
)
(
  echo "[PR #1016]"
  patch="$(mktemp)"
  git -C "$ROOT" show --format= --no-ext-diff "b9bb5a09929b2656a0857e0d3ae743f1661b0f14" -- src/common/thread.cpp src/common/thread.h src/core/core_timing.cpp src/core/core_timing.h > "$patch"
  if [[ ! -s "$patch" ]]; then
    echo "NO_RELEVANT_PATCH"
  elif output=$(git -C "$ROOT" apply --check --recount "$patch" 2>&1); then
    echo "APPLIES_CLEANLY (still requires dependency and behavior audit)"
  else
    echo "CONFLICTS: $(echo "$output" | grep -c '^error:' || true) portions"
    echo "$output" | grep '^error:' | head -n 14 || true
  fi
  rm -f "$patch"
)
(
  echo "[PR #1036]"
  patch="$(mktemp)"
  git -C "$ROOT" show --format= --no-ext-diff "0ab7736df9dba2b396d2c7a26bd26fbb9b7b0dc0" -- src/video_core > "$patch"
  if [[ ! -s "$patch" ]]; then
    echo "NO_RELEVANT_PATCH"
  elif output=$(git -C "$ROOT" apply --check --recount "$patch" 2>&1); then
    echo "APPLIES_CLEANLY (still requires dependency and behavior audit)"
  else
    echo "CONFLICTS: $(echo "$output" | grep -c '^error:' || true) portions"
    echo "$output" | grep '^error:' | head -n 14 || true
  fi
  rm -f "$patch"
)
echo "===== end audit; nothing applied ====="
