#!/usr/bin/env bash
# Runner nativo detectado por el gate Codex QA.
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"

cd "$BACKEND_DIR"

if [[ -x ".venv/bin/python" ]]; then
    exec .venv/bin/python -m pytest tests/ -q
fi

if command -v python3 >/dev/null 2>&1; then
    exec python3 -m pytest tests/ -q
fi

echo "No se encontró un intérprete Python ejecutable para el runner backend" >&2
exit 127
