#!/usr/bin/env bash
# EnvKit v0.2.1 — Self-test (safe, fast, no network)
# This is intended as the default testing.command for the bootstrap pack.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "═══════════════════════════════════════════════════════════════════"
echo "  ENVKIT SELF-TEST"
echo "═══════════════════════════════════════════════════════════════════"

echo "PWD: $ROOT"
echo "Version: $(cat VERSION.txt 2>/dev/null || echo 'unknown')"
echo ""

# Basic file presence
REQ=(
  "envkit_bootstrap.sh"
  "envkit.yml"
  "bin/version.sh"
  "bin/test.sh"
  "bin/context.sh"
  "bin/prod_smoke.sh"
  "envkit/cli.py"
  "PROJECT_CONSTITUTION.md"
  "AGENTS.md"
)
missing=0
for f in "${REQ[@]}"; do
  if [[ ! -e "$f" ]]; then
    echo "MISSING: $f"
    missing=$((missing+1))
  fi
done
if [[ "$missing" -gt 0 ]]; then
  echo ""
  echo "NO-GO: missing $missing required path(s)"
  exit 2
fi

# Executable bits (best-effort; on some filesystems unzip may preserve)
chmod +x envkit_bootstrap.sh bin/*.sh 2>/dev/null || true

# Python syntax check (no deps)
if command -v python3 >/dev/null 2>&1; then
  echo "Python: $(python3 --version 2>/dev/null || true)"
  python3 -m py_compile envkit/cli.py
else
  echo "WARN: python3 not found; skipping py_compile"
fi

echo ""
echo "Running version check..."
./bin/version.sh check || true

echo ""
echo "Generating context doc..."
./bin/context.sh || true

echo ""
echo "OK: self-test completed."
