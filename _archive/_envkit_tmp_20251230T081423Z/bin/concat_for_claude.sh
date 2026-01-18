#!/usr/bin/env bash
# EnvKit v0.2 — Concatenate files for Claude context
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT="${1:-/tmp/project_context.txt}"

{
    echo "═══════════════════════════════════════════════════════════════════"
    echo "PROJECT CONTEXT — $(date)"
    echo "═══════════════════════════════════════════════════════════════════"
    
    for f in AGENTS.md .aidev/context.md VERSION.txt envkit.yml; do
        [[ -f "$ROOT/$f" ]] && {
            echo ""
            echo "----- FILE: $f -----"
            cat "$ROOT/$f"
        }
    done
} > "$OUTPUT"

echo "Created: $OUTPUT ($(wc -l < "$OUTPUT") lines)"
echo "Copy: cat $OUTPUT | pbcopy"
