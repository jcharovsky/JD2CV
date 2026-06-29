#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK_DIR="${JD2CV_WORKDIR:-$HOME/.codex/tmp/jd2cv}"
VENV_DIR="$WORK_DIR/venv"
GENERATOR="${1:-$SKILL_DIR/assets/en/generate_ats_cv_en.py}"
OUTPUT="${2:-$WORK_DIR/ATS_CV_Template.pdf}"

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

CV_OUTPUT="$OUTPUT" "$VENV_DIR/bin/python" "$GENERATOR"
printf '%s\n' "$OUTPUT"
