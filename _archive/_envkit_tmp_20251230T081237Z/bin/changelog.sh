#!/usr/bin/env bash
# EnvKit v0.2 — Changelog Automation
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

CHANGELOG="$ROOT/CHANGELOG.md"
VERSION="$(./bin/version.sh check 2>/dev/null || echo '0.0.0')"
DATE="$(date +%Y-%m-%d)"
MSG="${1:-No description}"

if [[ ! -f "$CHANGELOG" ]]; then
  printf "# Changelog\n\n" > "$CHANGELOG"
fi

if grep -q "^## \\[$VERSION\\]" "$CHANGELOG"; then
  section="$(awk -v ver="$VERSION" '
    $0 ~ "^## \\["ver"\\]" {in_section=1; next}
    $0 ~ "^## \\[" {if (in_section) exit}
    {if (in_section) print}
  ' "$CHANGELOG")"
  if printf "%s\n" "$section" | grep -q "TODO"; then
    echo "NO-GO: changelog for $VERSION has TODOs; fill them in $CHANGELOG" >&2
    exit 1
  fi
  echo "Changelog OK: $VERSION"
  exit 0
fi

ENTRY="
## [$VERSION] - $DATE

### Added
- TODO: describe additions

### Changed
- TODO: describe changes

### Fixed
- TODO: describe fixes

### Notes
- $MSG
"

{ head -2 "$CHANGELOG"; echo "$ENTRY"; tail -n +3 "$CHANGELOG"; } > "$CHANGELOG.tmp"
mv "$CHANGELOG.tmp" "$CHANGELOG"
echo "Changelog template added for $VERSION; fill TODOs in $CHANGELOG" >&2
exit 1
