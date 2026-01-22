#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck disable=SC1091
source "$ROOT_DIR/.venv/bin/activate"
if [ -f "$ROOT_DIR/.env" ]; then
  # Load repo defaults (DB_URL, OLLAMA_MODEL, etc.).
  # shellcheck disable=SC1091
  set -a
  source "$ROOT_DIR/.env"
  set +a
fi
export OLLAMA_MODEL="${OLLAMA_MODEL:-mistral}"
python "$ROOT_DIR/app/cli/article_eater_contract_cli.py" "$@"
