#!/usr/bin/env bash
# EnvKit v0.2 — Generate AI Context Document
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

CONTEXT="$ROOT/.aidev/context.md"
mkdir -p "$(dirname "$CONTEXT")"

VERSION="$(./bin/version.sh check 2>/dev/null || echo 'unknown')"
TIMESTAMP="$(date '+%Y-%m-%d %H:%M:%S')"

cat > "$CONTEXT" << EOF
# Project Context (Auto-Generated)

Generated: $TIMESTAMP

## Current State
- Version: $VERSION
- Path: $ROOT

## Directory Structure
\`\`\`
$(find . -maxdepth 2 -type f -not -path './_archive/*' -not -path './.git/*' -not -path './node_modules/*' -not -name '*.pyc' 2>/dev/null | sort | head -30)
\`\`\`

## Key Commands
- \`./bin/prod_smoke.sh\` — verify everything
- \`./bin/test.sh\` — run tests
- \`./bin/version.sh bump\` — increment version
EOF

echo "Context generated: $CONTEXT"
