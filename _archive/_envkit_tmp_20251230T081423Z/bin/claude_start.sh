#!/usr/bin/env bash
# EnvKit v0.2 — Claude Session Bootstrap
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "═══════════════════════════════════════════════════════════════════"
echo "  CLAUDE SESSION BOOTSTRAP"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "Project: $(basename "$ROOT")"
echo "Path: $ROOT"
echo "Version: $(./bin/version.sh check 2>/dev/null || echo 'unknown')"

[[ -d ".git" ]] && echo "Git: $(git branch --show-current 2>/dev/null || echo 'unknown')"

echo ""
echo "Regenerating context..."
./bin/context.sh >/dev/null 2>&1 && echo "  ✓ .aidev/context.md updated"

echo ""
echo "Key files:"
echo "  • AGENTS.md — Safety rules"
echo "  • .aidev/context.md — Project state"
echo "  • .aidev/known_errors.yaml — Error patterns"

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "Key commands:"
echo "  ./bin/prod_smoke.sh        ONE TRUTH COMMAND"
echo "  ./bin/test.sh              Run tests"
echo "  ./bin/version.sh bump      Increment version"
echo "  ./bin/claude_diagnose.sh   Diagnose errors"
echo "═══════════════════════════════════════════════════════════════════"
