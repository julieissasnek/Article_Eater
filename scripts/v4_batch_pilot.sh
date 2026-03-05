#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════
# V4 BATCH PILOT — UNATTENDED EXTRACTION
# ═══════════════════════════════════════════════════════════════════════════
#
# PURPOSE: Run the full V4 extraction pipeline as a SINGLE bash command
#          so that Claude Code only asks permission ONCE, then runs to
#          completion without further prompts. Walk away and come back.
#
# USAGE (in Claude Code):
#   bash scripts/v4_batch_pilot.sh
#
# Or directly in a terminal:
#   cd ~/REPOS/Article_Eater_PostQuinean_v1
#   bash scripts/v4_batch_pilot.sh
#
# CONFIGURATION: Edit the variables below before running.
# ═══════════════════════════════════════════════════════════════════════════

set -euo pipefail

# ── Configuration (edit these) ──────────────────────────────────────────
LIMIT=10                          # Papers to process (start small)
BUDGET=50                         # Max spend in USD (safety cap)
VERIFY_FRACTION=0.2               # Fraction of papers to verify (0.0-1.0)
MODEL="gemini-2.5-flash"          # Model to use
MODE="sequential"                 # "sequential" or "parallel N" (e.g., "parallel 3")
FORCE=true                        # Kill competing processes? true/false
VERBOSE=true                      # Extra logging? true/false
# ────────────────────────────────────────────────────────────────────────

# ── Derived paths ───────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
EXTRACTION_SCRIPT="$PROJECT_ROOT/scripts/v4_staged_extraction.py"
ANALYSIS_SCRIPT="$PROJECT_ROOT/scripts/v4_pilot_analysis.py"
OUTPUT_DIR="$PROJECT_ROOT/data/v4_pilot"
BATCH_FILE="$PROJECT_ROOT/data/v4_pilot_dois.txt"
LOG_FILE="$OUTPUT_DIR/batch_pilot_$(date +%Y%m%d_%H%M%S).log"

# ── Color output ────────────────────────────────────────────────────────
CYAN='\033[96m'
GREEN='\033[92m'
YELLOW='\033[93m'
RED='\033[91m'
RESET='\033[0m'

log() { echo -e "${CYAN}[V4-PILOT $(date +%H:%M:%S)]${RESET} $1" | tee -a "$LOG_FILE"; }
ok()  { echo -e "${GREEN}[OK]${RESET} $1" | tee -a "$LOG_FILE"; }
warn(){ echo -e "${YELLOW}[WARN]${RESET} $1" | tee -a "$LOG_FILE"; }
err() { echo -e "${RED}[ERROR]${RESET} $1" | tee -a "$LOG_FILE"; }

# ═══════════════════════════════════════════════════════════════════════════
# PHASE 0: Environment validation
# ═══════════════════════════════════════════════════════════════════════════

mkdir -p "$OUTPUT_DIR"
echo "" > "$LOG_FILE"  # Initialize log

log "V4 Batch Pilot — Unattended Extraction"
log "======================================="
log "Project root: $PROJECT_ROOT"
log "Limit: $LIMIT papers | Budget: \$$BUDGET | Model: $MODEL"
log "Log file: $LOG_FILE"
log ""

# Check Python
if ! command -v python3 &>/dev/null && ! command -v python &>/dev/null; then
    err "Python not found. Install Python 3.9+"
    exit 1
fi
PYTHON=$(command -v python3 || command -v python)
log "Python: $($PYTHON --version)"

# Check extraction script exists
if [ ! -f "$EXTRACTION_SCRIPT" ]; then
    err "Extraction script not found: $EXTRACTION_SCRIPT"
    exit 1
fi
ok "Extraction script found"

# Check API keys
if [ -z "${GEMINI_API_KEY:-}" ]; then
    err "GEMINI_API_KEY not set. Run: export GEMINI_API_KEY='your-key'"
    exit 1
fi
ok "GEMINI_API_KEY is set (${#GEMINI_API_KEY} chars)"

if [ -n "${ANTHROPIC_API_KEY:-}" ]; then
    ok "ANTHROPIC_API_KEY is set (for verification stage)"
else
    warn "ANTHROPIC_API_KEY not set — verification stage will be skipped"
fi

# Check/install dependencies
log "Checking Python dependencies..."
$PYTHON -c "from google import genai" 2>/dev/null || {
    warn "google-genai not installed. Installing..."
    pip install google-genai --break-system-packages 2>&1 | tail -3 | tee -a "$LOG_FILE"
}
ok "google-genai available"

# ═══════════════════════════════════════════════════════════════════════════
# PHASE 1: Build DOI batch file (if not exists or empty)
# ═══════════════════════════════════════════════════════════════════════════

if [ ! -f "$BATCH_FILE" ] || [ ! -s "$BATCH_FILE" ]; then
    log "Building DOI batch file from pdf_doi_mapping.json..."
    $PYTHON -c "
import json
from pathlib import Path

mapping_file = Path('$PROJECT_ROOT/data/pdf_doi_mapping.json')
if not mapping_file.exists():
    print('ERROR: pdf_doi_mapping.json not found')
    exit(1)

with open(mapping_file) as f:
    mapping = json.load(f)

# Filter DOIs that have PDF files
dois_with_pdfs = []
for doi, info in mapping.items():
    pdf_path = info.get('pdf_path', '')
    if pdf_path and Path(pdf_path).exists():
        dois_with_pdfs.append(doi)
    elif pdf_path:
        # PDF path recorded but might be on David's machine
        dois_with_pdfs.append(doi)

# Write to batch file
batch_file = Path('$BATCH_FILE')
batch_file.write_text('\n'.join(dois_with_pdfs) + '\n')
print(f'Written {len(dois_with_pdfs)} DOIs to {batch_file}')
" 2>&1 | tee -a "$LOG_FILE"
    ok "Batch file created: $BATCH_FILE"
else
    N_DOIS=$(wc -l < "$BATCH_FILE" | tr -d ' ')
    ok "Batch file exists: $BATCH_FILE ($N_DOIS DOIs)"
fi

# ═══════════════════════════════════════════════════════════════════════════
# PHASE 2: Run extraction
# ═══════════════════════════════════════════════════════════════════════════

log ""
log "═══════════════════════════════════════════"
log "  STARTING EXTRACTION"
log "  Papers: $LIMIT | Budget: \$$BUDGET"
log "  Model: $MODEL | Verify: ${VERIFY_FRACTION}"
log "═══════════════════════════════════════════"
log ""

# Build command
CMD="$PYTHON $EXTRACTION_SCRIPT --batch $BATCH_FILE --limit $LIMIT --budget $BUDGET --verify-fraction $VERIFY_FRACTION --model $MODEL"

if [ "$FORCE" = true ]; then
    CMD="$CMD --force"
fi

if [ "$VERBOSE" = true ]; then
    CMD="$CMD --verbose"
fi

if [ "$MODE" = "sequential" ]; then
    CMD="$CMD --sequential"
elif [[ "$MODE" == parallel* ]]; then
    N_PARALLEL="${MODE#parallel }"
    CMD="$CMD --parallel ${N_PARALLEL:-3}"
fi

log "Command: $CMD"
log ""

# Run it — this is the main event. Stdout goes to console AND log file.
# Exit code is captured but we don't abort on failure (set +e temporarily)
set +e
$CMD 2>&1 | tee -a "$LOG_FILE"
EXTRACTION_EXIT_CODE=${PIPESTATUS[0]}
set -e

log ""
if [ $EXTRACTION_EXIT_CODE -eq 0 ]; then
    ok "Extraction completed successfully (exit code 0)"
else
    warn "Extraction finished with exit code $EXTRACTION_EXIT_CODE"
    warn "Check log for details: $LOG_FILE"
fi

# ═══════════════════════════════════════════════════════════════════════════
# PHASE 3: Run analysis (if results exist)
# ═══════════════════════════════════════════════════════════════════════════

RESULT_FILES=$(ls "$OUTPUT_DIR"/v4_extraction_final_*.json 2>/dev/null | head -1)

if [ -n "$RESULT_FILES" ] && [ -f "$ANALYSIS_SCRIPT" ]; then
    log ""
    log "═══════════════════════════════════════════"
    log "  RUNNING ANALYSIS"
    log "═══════════════════════════════════════════"
    log ""

    set +e
    $PYTHON "$ANALYSIS_SCRIPT" --results "$OUTPUT_DIR"/v4_extraction_final_*.json 2>&1 | tee -a "$LOG_FILE"
    set -e

    ok "Analysis complete"
else
    warn "No final results file found — skipping analysis"
fi

# ═══════════════════════════════════════════════════════════════════════════
# PHASE 4: Summary report
# ═══════════════════════════════════════════════════════════════════════════

log ""
log "═══════════════════════════════════════════"
log "  BATCH PILOT COMPLETE"
log "═══════════════════════════════════════════"
log ""
log "  Results: $OUTPUT_DIR/"
log "  Log: $LOG_FILE"

# List outputs
if ls "$OUTPUT_DIR"/v4_extraction_final_*.json &>/dev/null; then
    for f in "$OUTPUT_DIR"/v4_extraction_final_*.json; do
        SIZE=$(du -h "$f" | cut -f1)
        log "  Result: $(basename $f) ($SIZE)"
    done
fi

if [ -f "$OUTPUT_DIR/dead_letter_queue.jsonl" ]; then
    DLQ_COUNT=$(wc -l < "$OUTPUT_DIR/dead_letter_queue.jsonl" | tr -d ' ')
    if [ "$DLQ_COUNT" -gt 0 ]; then
        warn "  Dead letters: $DLQ_COUNT papers need review"
        warn "  See: $OUTPUT_DIR/dead_letter_queue.jsonl"
    fi
fi

if ls "$OUTPUT_DIR"/v4_telemetry_*.json &>/dev/null; then
    log "  Telemetry: $(ls "$OUTPUT_DIR"/v4_telemetry_*.json | head -1)"
fi

log ""
log "Done. Total runtime: ${SECONDS}s"
