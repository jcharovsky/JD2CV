#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK_DIR="${JD2CV_WORKDIR:-$HOME/.codex/tmp/jd2cv}"
VENV_DIR="$WORK_DIR/venv"
GENERATOR="$SKILL_DIR/scripts/generate_ats_cv.py"

if [[ $# -ne 1 ]]; then
  printf 'Usage: %s <source.md>\n' "$0" >&2
  exit 2
fi

SOURCE="$1"

mkdir -p "$WORK_DIR"

if [[ ! -x "$VENV_DIR/bin/python" ]]; then
  python3 -m venv "$VENV_DIR"
fi

if ! "$VENV_DIR/bin/python" - <<'PY'
import importlib.util
raise SystemExit(0 if importlib.util.find_spec("reportlab") else 1)
PY
then
  "$VENV_DIR/bin/python" -m pip install reportlab
fi

"$VENV_DIR/bin/python" "$GENERATOR" "$SOURCE"
