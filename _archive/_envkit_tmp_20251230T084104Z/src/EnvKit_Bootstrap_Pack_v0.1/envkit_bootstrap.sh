#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

ts="$(date +%Y%m%d_%H%M%S)"
ARCH="_archive/envkit/${ts}"
mkdir -p "$ARCH"

put_file() {
  local src="$1"
  local dst="$2"
  if [[ -e "$dst" ]]; then
    mkdir -p "$ARCH/$(dirname "$dst")"
    cp -a "$dst" "$ARCH/$dst"
  fi
  mkdir -p "$(dirname "$dst")"
  cp -a "$src" "$dst"
}

echo "== EnvKit bootstrap =="
echo "Repo: $ROOT"
echo "Archive: $ARCH"

mkdir -p bin envkit templates _archive/envkit _archive/_smoke

if [[ ! -f envkit.yml ]]; then
  put_file "envkit.yml" "envkit.yml"
fi
if [[ ! -f AGENTS.md ]]; then
  put_file "AGENTS.md" "AGENTS.md"
fi

put_file "bin/prod_smoke.sh" "bin/prod_smoke.sh"
put_file "bin/release_and_smoke.sh" "bin/release_and_smoke.sh"

chmod +x bin/prod_smoke.sh bin/release_and_smoke.sh envkit_bootstrap.sh || true

echo "OK: EnvKit installed."
echo "Next: ./bin/prod_smoke.sh"
