#!/usr/bin/env bash
set -euo pipefail

# Deploy EnvKit release ZIP into a target repo (non-destructive: archives collisions)
#
# Usage:
#   ./bin/deploy_envkit.sh /path/to/TARGET_REPO [v0.2.2] [--smoke]
#
# Notes:
# - Override ZIP location via ENVKIT_ZIP=/full/path/to/EnvKit_Bootstrap_Pack_v0.2.2.zip
# - --smoke runs ./bin/prod_smoke.sh after deployment (requires runtime deps, e.g., Docker)

TARGET="${1:-}"
VER="${2:-v0.2.2}"
FLAG_SMOKE="${3:-}"

if [[ -z "$TARGET" ]]; then
  echo "Usage: $0 /path/to/TARGET_REPO [v0.2.1] [--smoke]" >&2
  exit 2
fi

TARGET="$(cd "$TARGET" && pwd)"
if [[ "$TARGET" == "/" || "$TARGET" == "$HOME" ]]; then
  echo "NO-GO: refusing to deploy into $TARGET" >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENVKIT_HOME="$(cd "$SCRIPT_DIR/.." && pwd)"

ZIP_DEFAULT="$ENVKIT_HOME/Releases/EnvKit_Bootstrap_Pack_${VER}.zip"
ZIP="${ENVKIT_ZIP:-$ZIP_DEFAULT}"

if [[ ! -f "$ZIP" ]]; then
  echo "NO-GO: EnvKit ZIP not found: $ZIP" >&2
  echo "Tip: set ENVKIT_ZIP=/full/path/to/zip" >&2
  exit 2
fi

echo "== EnvKit Deploy =="
echo "EnvKit home: $ENVKIT_HOME"
echo "Zip:         $ZIP"
echo "Target repo:  $TARGET"
echo ""

cd "$TARGET"

# Archive any colliding files/dirs (no deletions)
TS="$(date +%Y%m%d_%H%M%S)"
ARCH="_archive/envkit_deploy/$TS"
mkdir -p "$ARCH"

CANDIDATES=(
  "bin/deploy_envkit.sh"
  "bin/prod_smoke.sh"
  "bin/release_and_smoke.sh"
  "bin/test.sh"
  "bin/self_test.sh"
  "bin/context.sh"
  "bin/version.sh"
  "bin/changelog.sh"
  "bin/release.sh"
  "envkit_bootstrap.sh"
  "envkit.yml"
  "AGENTS.md"
  "PROJECT_CONSTITUTION.md"
  "README.md"
  "CHANGELOG.md"
  "VERSION.txt"
  "envkit"
  "templates"
  ".aidev"
  "deconcat.py"
)

moved=0
for p in "${CANDIDATES[@]}"; do
  if [[ -e "$p" ]]; then
    mkdir -p "$ARCH/$(dirname "$p")"
    echo "ARCHIVE: $p -> $ARCH/$p"
    mv "$p" "$ARCH/$p"
    moved=$((moved+1))
  fi
done

if [[ "$moved" -gt 0 ]]; then
  echo "OK: archived $moved colliding path(s) under $ARCH"
else
  echo "OK: no collisions to archive"
fi

echo ""
echo "Unzipping EnvKit into repo root..."
unzip -o "$ZIP" >/dev/null

chmod +x envkit_bootstrap.sh bin/*.sh 2>/dev/null || true

echo "Running ./envkit_bootstrap.sh ..."
./envkit_bootstrap.sh

echo ""
echo "Running ./bin/version.sh check ..."
./bin/version.sh check || true

echo ""
echo "Running ./bin/test.sh ..."
./bin/test.sh

if [[ "$FLAG_SMOKE" == "--smoke" ]]; then
  echo ""
  echo "Running ./bin/prod_smoke.sh ..."
  ./bin/prod_smoke.sh
fi

echo ""
echo "OK: EnvKit deployed."
echo "Next:"
echo "  ./bin/test.sh"
echo "  ./bin/prod_smoke.sh"
