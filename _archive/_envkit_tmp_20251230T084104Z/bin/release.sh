#!/usr/bin/env bash
# EnvKit v0.2 — Create Release
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

VERSION="$(./bin/version.sh check)"
RELEASES_DIR="$ROOT/Releases"
RELEASE_ZIP="$RELEASES_DIR/EnvKit_Bootstrap_Pack_v${VERSION}.zip"

echo "Creating release v$VERSION..."

./bin/test.sh >/dev/null 2>&1 || { echo "Tests failed"; exit 1; }

./bin/changelog.sh "Release v$VERSION"

mkdir -p "$RELEASES_DIR"
[[ -f "$RELEASE_ZIP" ]] && { echo "v$VERSION exists. Bump version first."; exit 1; }

zip -r "$RELEASE_ZIP" . \
  -x "*.git*" \
  -x "_archive/*" \
  -x ".aidev/*" \
  -x "releases/*" \
  -x "Releases/*" \
  -x "EnvKit_Bootstrap_Pack_*.zip" \
  -x "EnvKit_Patch_*.zip" \
  -x "*.pyc" \
  -x "*__pycache__*" \
  -x "node_modules/*" \
  -x "venv/*" >/dev/null

echo "Created: $RELEASE_ZIP ($(du -h "$RELEASE_ZIP" | cut -f1))"
