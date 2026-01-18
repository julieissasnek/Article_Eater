#!/usr/bin/env bash
set -euo pipefail

# Deploy EnvKit release ZIP into a target repo (non-destructive: archives collisions)
# Usage:
#   ~/REPOS/EnvKit/src/deploy_envkit.sh /path/to/REPO [v0.1]
# Optional:
#   ZIP override via ENVKIT_ZIP=/path/to/zip

TARGET="${1:-}"
VER="${2:-v0.1}"

if [[ -z "$TARGET" ]]; then
  echo "Usage: $0 /path/to/TARGET_REPO [v0.1]" >&2
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

cd "$TARGET"

# Archive any colliding files/dirs (no deletions)
TS="$(date +%Y%m%d_%H%M%S)"
ARCH="_archive/envkit_deploy/$TS"
mkdir -p "$ARCH"

# Things the zip may add/overwrite
CANDIDATES=(
  "bin/prod_smoke.sh"
  "bin/release_and_smoke.sh"
  "envkit_bootstrap.sh"
  "envkit.yml"
  "AGENTS.md"
  "PROJECT_CONSTITUTION.md"
  "README.md"
  "envkit"
  "templates"
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

# Deploy
echo "Unzipping EnvKit into repo root..."
unzip -o "$ZIP" >/dev/null

# Run bootstrap (idempotent; repo-specific setup)
if [[ -x "./envkit_bootstrap.sh" ]]; then
  echo "Running ./envkit_bootstrap.sh ..."
  ./envkit_bootstrap.sh
else
  echo "NO-GO: envkit_bootstrap.sh missing or not executable after unzip" >&2
  exit 2
fi

echo
echo "OK: EnvKit deployed."
echo "Next:"
echo "  ./bin/prod_smoke.sh"
