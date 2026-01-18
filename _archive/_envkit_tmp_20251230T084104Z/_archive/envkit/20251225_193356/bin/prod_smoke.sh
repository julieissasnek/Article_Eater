#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

VER="vUNKNOWN"
[[ -f "VERSION.txt" ]] && VER="$(tr -d ' \r\n\t' < VERSION.txt)"

echo "== PROD SMOKE =="
echo "Repo: $ROOT"
echo "Version: $VER"

mkdir -p _archive/_smoke
FP_FILE="_archive/_smoke/last_fingerprint.txt"

FP="$(
  ( \
    shasum -a 256 Dockerfile.api Dockerfile.ui docker-compose.yml VERSION.txt \
      backend/requirements.txt frontend_streamlit/requirements.txt 2>/dev/null || true; \
    find backend/app core frontend_streamlit -type f -print0 2>/dev/null \
      | LC_ALL=C sort -z \
      | xargs -0 shasum -a 256 2>/dev/null || true \
  ) | shasum -a 256 | awk '{print $1}'
)"
PREV_FP="$(cat "$FP_FILE" 2>/dev/null || true)"

if [[ "${FORCE_REBUILD:-0}" = "1" || "$FP" != "$PREV_FP" ]]; then
  echo "Rebuild: YES (changed inputs or FORCE_REBUILD=1)"
  if [[ -x "./install.sh" ]]; then
    ./install.sh
  else
    docker compose up -d --build
  fi
  echo "$FP" > "$FP_FILE"
else
  echo "Rebuild: NO (inputs unchanged)"
  docker compose up -d --no-build
fi

if [[ -x "./bin/tc" ]]; then
  ./bin/tc doctor --prod || true
  ./bin/tc health || true
fi

docker compose ps || true

if command -v curl >/dev/null 2>&1 && [[ -f "envkit.yml" ]]; then
  endpoints="$(grep -E '^\s*-\s*"http' envkit.yml 2>/dev/null | sed -E 's/^\s*-\s*"([^"]+)".*$/\1/g' || true)"
  if [[ -n "$endpoints" ]]; then
    while IFS= read -r url; do
      [[ -z "$url" ]] && continue
      echo "curl $url"
      curl -sS "$url" || true
      echo
    done <<< "$endpoints"
  fi
fi

echo "OK: prod smoke complete"
