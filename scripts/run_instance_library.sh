#!/bin/bash
# ─────────────────────────────────────────────────────────────
# CMR Instance Library Builder — On-Demand Runner
# ─────────────────────────────────────────────────────────────
# Rebuilds the instance library from:
#   1. Extracted findings (data/extracted_findings/*.jsonl)
#   2. Test paper claims (data/test_papers/*.json)
#   3. Template calibrated parameters (data/templates/*.json)
#   4. Literature seed instances (hard-coded from published databases)
#
# Outputs:
#   - CMR_Instance_Library_Report_<DATE>.txt (human-readable)
#   - CMR_Instance_Library_<DATE>.json (machine-readable)
#
# Usage:
#   ./scripts/run_instance_library.sh
# ─────────────────────────────────────────────────────────────

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
OUTPUT_DIR="${REPO_DIR}/.."
DATE=$(date +%Y-%m-%d)

echo "=== CMR Instance Library Builder ==="
echo "Date: $DATE"
echo "Repo: $REPO_DIR"
echo ""

cd "$REPO_DIR"

# Generate report
python3 scripts/instance_library_builder.py \
    --report \
    --data-dir data \
    --templates-dir data/templates \
    --output "${OUTPUT_DIR}/CMR_Instance_Library_Report_${DATE}.txt"

# Generate JSON
python3 scripts/instance_library_builder.py \
    --json \
    --data-dir data \
    --templates-dir data/templates \
    --output "${OUTPUT_DIR}/CMR_Instance_Library_${DATE}.json"

echo ""
echo "=== Instance Library Complete ==="
echo "Report: ${OUTPUT_DIR}/CMR_Instance_Library_Report_${DATE}.txt"
echo "JSON:   ${OUTPUT_DIR}/CMR_Instance_Library_${DATE}.json"
