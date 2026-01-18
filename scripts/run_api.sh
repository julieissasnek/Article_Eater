#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PORTS_JSON="$ROOT_DIR/contracts/ports.json"

PORT=8000
if [ -f "$PORTS_JSON" ]; then
  PORT=$(python3 - <<'PY'
import json
from pathlib import Path
p=Path("/Users/davidusa/REPOS/Article_Eater_v20_7_43/contracts/ports.json")
try:
    data=json.loads(p.read_text(encoding='utf-8'))
    print(int(data.get('ports',{}).get('api',{}).get('host',8000)))
except Exception:
    print(8000)
PY
)
fi

echo "Starting Article Eater API on http://127.0.0.1:${PORT}"
exec python -m uvicorn app.main:app --host 0.0.0.0 --port "$PORT" "$@"
