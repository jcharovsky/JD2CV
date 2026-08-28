#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GENERATOR="$SKILL_DIR/scripts/generate_ats_cv.py"

if [[ $# -ne 1 ]]; then
  printf 'Usage: %s <source.md>\n' "$0" >&2
  exit 2
fi

SOURCE="$1"

exec uv run --project "$SKILL_DIR" --locked python "$GENERATOR" "$SOURCE"
