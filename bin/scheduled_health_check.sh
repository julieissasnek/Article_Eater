#!/bin/bash
# =============================================================================
# scheduled_health_check.sh - Automated Health Check for Article Eater
# =============================================================================
# Runs tests, checks for regressions, and logs results.
# Designed for cron or launchd scheduling.
#
# Usage:
#   ./bin/scheduled_health_check.sh              # Run health check
#   ./bin/scheduled_health_check.sh --notify     # Send notification on failure
#   ./bin/scheduled_health_check.sh --bundle     # Create ruthless bundle if tests fail
#
# Cron example (run daily at 3am):
#   0 3 * * * /path/to/Article_Eater_PostQuinean_v1/bin/scheduled_health_check.sh >> /tmp/ae_health.log 2>&1
#
# LaunchAgent example: see docs/HEALTH_CHECK_LAUNCHD.plist
# =============================================================================

set -e

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DATE=$(date +%Y-%m-%d)
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
LOG_DIR="${REPO_ROOT}/logs"
LOG_FILE="${LOG_DIR}/health_check_${DATE}.log"
HISTORY_FILE="${LOG_DIR}/test_history.csv"

# Parse arguments
NOTIFY=false
CREATE_BUNDLE=false
for arg in "$@"; do
    case $arg in
        --notify) NOTIFY=true ;;
        --bundle) CREATE_BUNDLE=true ;;
    esac
done

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Header
echo "=============================================" | tee -a "$LOG_FILE"
echo "Article Eater Health Check" | tee -a "$LOG_FILE"
echo "Timestamp: $TIMESTAMP" | tee -a "$LOG_FILE"
echo "=============================================" | tee -a "$LOG_FILE"

cd "$REPO_ROOT"

# Activate virtual environment
source venv/bin/activate 2>/dev/null || {
    echo "ERROR: Could not activate venv" | tee -a "$LOG_FILE"
    exit 1
}

# =============================================================================
# 1. Run Test Suite
# =============================================================================
echo "" | tee -a "$LOG_FILE"
echo "[1/5] Running test suite..." | tee -a "$LOG_FILE"

TEST_START=$(date +%s)
TEST_OUTPUT=$(python -m pytest tests/ --tb=no -q 2>&1) || true
TEST_END=$(date +%s)
TEST_DURATION=$((TEST_END - TEST_START))

echo "$TEST_OUTPUT" >> "$LOG_FILE"

# Parse test results (ensure defaults if grep returns empty)
PASSED=$(echo "$TEST_OUTPUT" | grep -oE '[0-9]+ passed' | grep -oE '[0-9]+' | head -1)
PASSED=${PASSED:-0}
FAILED=$(echo "$TEST_OUTPUT" | grep -oE '[0-9]+ failed' | grep -oE '[0-9]+' | head -1)
FAILED=${FAILED:-0}
ERRORS=$(echo "$TEST_OUTPUT" | grep -oE '[0-9]+ error' | grep -oE '[0-9]+' | head -1)
ERRORS=${ERRORS:-0}
TOTAL=$((PASSED + FAILED + ERRORS))

echo "Results: $PASSED passed, $FAILED failed, $ERRORS errors (${TEST_DURATION}s)" | tee -a "$LOG_FILE"

# Append to history
if [ ! -f "$HISTORY_FILE" ]; then
    echo "date,timestamp,passed,failed,errors,duration_s" > "$HISTORY_FILE"
fi
echo "$DATE,$TIMESTAMP,$PASSED,$FAILED,$ERRORS,$TEST_DURATION" >> "$HISTORY_FILE"

# =============================================================================
# 2. Check for Regressions
# =============================================================================
echo "" | tee -a "$LOG_FILE"
echo "[2/5] Checking for regressions..." | tee -a "$LOG_FILE"

# Get previous run stats
PREV_LINE=$(tail -2 "$HISTORY_FILE" | head -1)
if [ -n "$PREV_LINE" ] && [ "$PREV_LINE" != "date,timestamp,passed,failed,errors,duration_s" ]; then
    PREV_PASSED=$(echo "$PREV_LINE" | cut -d',' -f3)
    PREV_PASSED=${PREV_PASSED:-0}
    PREV_FAILED=$(echo "$PREV_LINE" | cut -d',' -f4)
    PREV_FAILED=${PREV_FAILED:-0}

    if [ "${PASSED:-0}" -lt "${PREV_PASSED:-0}" ]; then
        echo "WARNING: Regression detected! Passed tests decreased: $PREV_PASSED -> $PASSED" | tee -a "$LOG_FILE"
        REGRESSION=true
    elif [ "${FAILED:-0}" -gt "${PREV_FAILED:-0}" ]; then
        echo "WARNING: Regression detected! Failed tests increased: $PREV_FAILED -> $FAILED" | tee -a "$LOG_FILE"
        REGRESSION=true
    else
        echo "No regression detected" | tee -a "$LOG_FILE"
        REGRESSION=false
    fi
else
    echo "No previous run to compare (first run)" | tee -a "$LOG_FILE"
    REGRESSION=false
fi

# =============================================================================
# 3. Check Key Files Exist
# =============================================================================
echo "" | tee -a "$LOG_FILE"
echo "[3/5] Checking key files..." | tee -a "$LOG_FILE"

KEY_FILES=(
    "src/services/web_of_belief.py"
    "src/services/extraction_to_web.py"
    "src/services/web_persistence.py"
    "src/services/social_epistemology.py"
    "src/services/epistemic_causal_bridge.py"
    "CLAUDE.md"
    "TASKS.md"
)

MISSING_FILES=0
for file in "${KEY_FILES[@]}"; do
    if [ ! -f "$REPO_ROOT/$file" ]; then
        echo "MISSING: $file" | tee -a "$LOG_FILE"
        MISSING_FILES=$((MISSING_FILES + 1))
    fi
done

if [ $MISSING_FILES -eq 0 ]; then
    echo "All ${#KEY_FILES[@]} key files present" | tee -a "$LOG_FILE"
else
    echo "WARNING: $MISSING_FILES key files missing!" | tee -a "$LOG_FILE"
fi

# =============================================================================
# 4. Web/BN Health Gates
# =============================================================================
echo "" | tee -a "$LOG_FILE"
echo "[4/5] Checking Web/BN health gates..." | tee -a "$LOG_FILE"

GRAPH_HEALTH_OUTPUT=$(python scripts/check_web_bn_health.py 2>&1) || true
echo "$GRAPH_HEALTH_OUTPUT" | tee -a "$LOG_FILE"

if echo "$GRAPH_HEALTH_OUTPUT" | grep -q "minimum_viable: PASS"; then
    GRAPH_HEALTH_OK=true
    echo "Web/BN minimum health gates: PASS" | tee -a "$LOG_FILE"
else
    GRAPH_HEALTH_OK=false
    echo "WARNING: Web/BN minimum health gates: FAIL" | tee -a "$LOG_FILE"
fi

# =============================================================================
# 5. Generate Summary
# =============================================================================
echo "" | tee -a "$LOG_FILE"
echo "[5/5] Summary..." | tee -a "$LOG_FILE"

# Determine overall health
if [ "${FAILED:-0}" -gt 0 ] || [ "${ERRORS:-0}" -gt 0 ] || [ "${MISSING_FILES:-0}" -gt 0 ] || [ "$GRAPH_HEALTH_OK" = false ]; then
    HEALTH="UNHEALTHY"
    EXIT_CODE=1
elif [ "$REGRESSION" = true ]; then
    HEALTH="DEGRADED"
    EXIT_CODE=1
else
    HEALTH="HEALTHY"
    EXIT_CODE=0
fi

echo "" | tee -a "$LOG_FILE"
echo "=============================================" | tee -a "$LOG_FILE"
echo "HEALTH STATUS: $HEALTH" | tee -a "$LOG_FILE"
echo "Tests: $PASSED passed, $FAILED failed, $ERRORS errors" | tee -a "$LOG_FILE"
echo "Web/BN minimum gates: $([ "$GRAPH_HEALTH_OK" = true ] && echo PASS || echo FAIL)" | tee -a "$LOG_FILE"
echo "Duration: ${TEST_DURATION}s" | tee -a "$LOG_FILE"
echo "=============================================" | tee -a "$LOG_FILE"

# =============================================================================
# Optional: Create Ruthless Bundle on Failure
# =============================================================================
if [ "$CREATE_BUNDLE" = true ] && [ "$HEALTH" != "HEALTHY" ]; then
    echo "" | tee -a "$LOG_FILE"
    echo "Creating ruthless review bundle for investigation..." | tee -a "$LOG_FILE"
    "$REPO_ROOT/bin/ruthless_review.sh" >> "$LOG_FILE" 2>&1
    echo "Bundle created: ruthless_bundle_${DATE}.zip" | tee -a "$LOG_FILE"
fi

# =============================================================================
# Optional: Send Notification on Failure
# =============================================================================
if [ "$NOTIFY" = true ] && [ "$HEALTH" != "HEALTHY" ]; then
    # macOS notification
    if command -v osascript &> /dev/null; then
        osascript -e "display notification \"$PASSED passed, $FAILED failed\" with title \"Article Eater: $HEALTH\" sound name \"Basso\""
    fi

    # Could add email, Slack, etc. here
    echo "Notification sent" | tee -a "$LOG_FILE"
fi

# =============================================================================
# Save latest status for quick access
# =============================================================================
cat > "${LOG_DIR}/latest_status.json" << EOF
{
    "date": "$DATE",
    "timestamp": "$TIMESTAMP",
    "health": "$HEALTH",
    "passed": ${PASSED:-0},
    "failed": ${FAILED:-0},
    "errors": ${ERRORS:-0},
    "duration_s": ${TEST_DURATION:-0},
    "regression": ${REGRESSION:-false}
}
EOF

exit $EXIT_CODE
