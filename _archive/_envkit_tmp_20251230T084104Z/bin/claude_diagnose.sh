#!/usr/bin/env bash
# EnvKit v0.2 — Claude Error Diagnosis
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ERROR_INPUT="${1:-}"

[[ -z "$ERROR_INPUT" ]] && { echo "Usage: $0 'error message'"; exit 1; }

echo "═══════════════════════════════════════════════════════════════════"
echo "  ERROR DIAGNOSIS"
echo "═══════════════════════════════════════════════════════════════════"
echo "Input: $ERROR_INPUT"
echo ""

ERROR_LOWER="$(echo "$ERROR_INPUT" | tr '[:upper:]' '[:lower:]')"

declare -A PATTERNS
PATTERNS["externally-managed"]="PEP 668: Use venv|python3 -m venv venv && source venv/bin/activate"
PATTERNS["no module named"]="Missing module|pip install -r requirements.txt"
PATTERNS["ssl.*certificate"]="SSL certs missing|/Applications/Python*/Install Certificates.command"
PATTERNS["address already in use"]="Port occupied|lsof -ti:PORT | xargs kill -9"
PATTERNS["permission denied"]="Permission issue|Check: ls -la"
PATTERNS["command not found"]="Missing command|Install the required tool"

MATCHED=0
for pattern in "${!PATTERNS[@]}"; do
    if echo "$ERROR_LOWER" | grep -qi "$pattern"; then
        MATCHED=1
        IFS='|' read -r diagnosis fix <<< "${PATTERNS[$pattern]}"
        echo "MATCHED: $pattern"
        echo "Diagnosis: $diagnosis"
        echo "Fix: $fix"
        echo ""
    fi
done

[[ $MATCHED -eq 0 ]] && echo "No known pattern matched. Check .aidev/known_errors.yaml"
