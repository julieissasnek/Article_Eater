#!/usr/bin/env bash
# EnvKit v0.2 — Test Runner
# Usage: ./bin/test.sh

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "═══════════════════════════════════════════════════════════════════"
echo "  TEST RUNNER"
echo "═══════════════════════════════════════════════════════════════════"

# Read test command from envkit.yml if exists
TEST_CMD=""
if [[ -f "envkit.yml" ]]; then
    # Prefer python parsing (handles quoted/unquoted YAML scalars)
    if command -v python3 >/dev/null 2>&1; then
        TEST_CMD="$(python3 - <<'PY'
import re, sys
p = "envkit.yml"
txt = open(p, "r", encoding="utf-8").read().splitlines()
in_testing = False
for ln in txt:
    if re.match(r"^\s*testing\s*:\s*$", ln):
        in_testing = True
        continue
    if in_testing:
        # Stop when a new top-level key begins
        if re.match(r"^\S", ln):
            break
        m = re.match(r"^\s*command\s*:\s*(.*?)\s*$", ln)
        if m:
            val = m.group(1).strip()
            if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                val = val[1:-1]
            print(val)
            sys.exit(0)
print("")
PY
        )"
    else
        # Best-effort fallback (expects command on one line)
        TEST_CMD="$(grep -A5 '^testing:' envkit.yml 2>/dev/null | grep 'command:' | sed -E "s/.*command:[[:space:]]*[\'\"]?(.*)[\'\"]?[[:space:]]*$/\\1/" || true)"
    fi
fi

# Fallback detection
if [[ -z "$TEST_CMD" ]]; then
    if [[ -f "pytest.ini" ]] || [[ -d "tests" ]]; then
        TEST_CMD="python3 -m pytest tests/ -v"
    elif [[ -f "package.json" ]]; then
        TEST_CMD="npm test"
    elif [[ -f "Makefile" ]] && grep -q "^test:" Makefile; then
        TEST_CMD="make test"
    fi
fi

if [[ -z "$TEST_CMD" ]]; then
    echo "No test command found."
    echo "Configure in envkit.yml under testing.command"
    exit 0
fi

echo "Command: $TEST_CMD"
echo ""
eval "$TEST_CMD"
