#!/bin/bash
# ─────────────────────────────────────────────────────────────
# CMR Integrated Prediction Pipeline — On-Demand Runner
# ─────────────────────────────────────────────────────────────
# Runs the full prediction generation pipeline:
#   1. Type-level predictions from 103 calibrated templates
#   2. Instance matching from the 649-instance library
#   3. Situated predictions across 11 canonical scenarios
#   4. Lighting × time × task interactions (Kruithof + circadian)
#   5. Noise × activity interactions
#   6. Interior typology conditional probabilities
#
# Outputs:
#   - CMR_Integrated_Predictions_Report_<DATE>.txt (human-readable)
#   - CMR_Integrated_Predictions_<DATE>.json (machine-readable, top 50)
#
# Usage:
#   ./scripts/run_integrated_predictions.sh
#   ./scripts/run_integrated_predictions.sh --top 100
# ─────────────────────────────────────────────────────────────

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
OUTPUT_DIR="${REPO_DIR}/.."
DATE=$(date +%Y-%m-%d)
TOP_N=${1:-50}

echo "=== CMR Integrated Prediction Pipeline ==="
echo "Date: $DATE"
echo "Repo: $REPO_DIR"
echo "Top predictions: $TOP_N"
echo ""

cd "$REPO_DIR"

# Generate human-readable report
python3 scripts/integrated_prediction_pipeline.py \
    --run \
    --data-dir data \
    --templates-dir data/templates \
    --output "${OUTPUT_DIR}/CMR_Integrated_Predictions_Report_${DATE}.txt"

# Generate JSON
python3 scripts/integrated_prediction_pipeline.py \
    --run --json \
    --data-dir data \
    --templates-dir data/templates \
    --top "$TOP_N" \
    --output "${OUTPUT_DIR}/CMR_Integrated_Predictions_${DATE}.json"

echo ""
echo "=== Integrated Predictions Complete ==="
echo "Report: ${OUTPUT_DIR}/CMR_Integrated_Predictions_Report_${DATE}.txt"
echo "JSON:   ${OUTPUT_DIR}/CMR_Integrated_Predictions_${DATE}.json"
