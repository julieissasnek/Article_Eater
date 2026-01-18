#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "== RELEASE + SMOKE =="

if [[ -x "./bin/tc" ]]; then
  VER="vUNKNOWN"
  [[ -f "VERSION.txt" ]] && VER="$(tr -d ' \r\n\t' < VERSION.txt)"
  ./bin/tc release "$VER"
else
  echo "NOTE: no ./bin/tc found; skipping release gate"
fi

./bin/prod_smoke.sh
