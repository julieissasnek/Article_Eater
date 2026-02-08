#!/bin/bash
# =============================================================================
# ruthless_review.sh - Package Article Eater for External LLM Review
# =============================================================================
# Creates a minimal bundle for ChatGPT/Gemini/Codex ruthless critique
#
# Usage:
#   ./bin/ruthless_review.sh           # Create bundle for review
#   ./bin/ruthless_review.sh --test    # Run tests first, then create bundle
#   ./bin/ruthless_review.sh --quick   # Minimal bundle (core only)
#
# Output:
#   - ruthless_bundle_YYYY-MM-DD.zip in current directory
#   - Ready for upload to external LLM
# =============================================================================

set -e

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DATE=$(date +%Y-%m-%d)
BUNDLE_DIR="/tmp/ruthless_bundle_${DATE}"
OUTPUT_ZIP="${REPO_ROOT}/ruthless_bundle_${DATE}.zip"

echo "============================================="
echo "Article Eater Ruthless Review Bundle Creator"
echo "Date: ${DATE}"
echo "============================================="

# Parse arguments
RUN_TESTS=false
QUICK_MODE=false
for arg in "$@"; do
    case $arg in
        --test) RUN_TESTS=true ;;
        --quick) QUICK_MODE=true ;;
    esac
done

# Step 1: Run tests if requested
if [ "$RUN_TESTS" = true ]; then
    echo ""
    echo "[1/4] Running test suite..."
    cd "$REPO_ROOT"
    source venv/bin/activate 2>/dev/null || true

    # Run tests and capture summary
    TEST_OUTPUT=$(python -m pytest tests/ --tb=no -q 2>&1 | tail -5)
    echo "$TEST_OUTPUT"

    # Extract pass/fail counts
    PASSED=$(echo "$TEST_OUTPUT" | grep -oE '[0-9]+ passed' | head -1 || echo "0 passed")
    FAILED=$(echo "$TEST_OUTPUT" | grep -oE '[0-9]+ failed' | head -1 || echo "0 failed")

    echo ""
    echo "Test Summary: $PASSED, $FAILED"
    echo "$PASSED, $FAILED" > /tmp/test_summary.txt
else
    echo "[1/4] Skipping tests (use --test to run)"
fi

# Step 2: Create bundle directory
echo ""
echo "[2/4] Creating bundle directory..."
rm -rf "$BUNDLE_DIR"
mkdir -p "$BUNDLE_DIR"
mkdir -p "$BUNDLE_DIR/src/services"
mkdir -p "$BUNDLE_DIR/contracts/schemas"
mkdir -p "$BUNDLE_DIR/docs"
mkdir -p "$BUNDLE_DIR/tests"

# Step 3: Copy essential files
echo ""
echo "[3/4] Copying essential files..."

# Core documentation
cp "$REPO_ROOT/CLAUDE.md" "$BUNDLE_DIR/"
cp "$REPO_ROOT/TASKS.md" "$BUNDLE_DIR/"
cp "$REPO_ROOT/Project_Constitution.md" "$BUNDLE_DIR/" 2>/dev/null || true

# Key service files (the Quinean engine)
cp "$REPO_ROOT/src/services/web_of_belief.py" "$BUNDLE_DIR/src/services/"
cp "$REPO_ROOT/src/services/extraction_to_web.py" "$BUNDLE_DIR/src/services/"
cp "$REPO_ROOT/src/services/web_persistence.py" "$BUNDLE_DIR/src/services/"

if [ "$QUICK_MODE" = false ]; then
    # Sprint 1.5, 2.5 key files
    cp "$REPO_ROOT/src/services/epistemic_causal_bridge.py" "$BUNDLE_DIR/src/services/" 2>/dev/null || true
    cp "$REPO_ROOT/src/services/social_epistemology.py" "$BUNDLE_DIR/src/services/" 2>/dev/null || true
    cp "$REPO_ROOT/src/services/credibility_testing.py" "$BUNDLE_DIR/src/services/" 2>/dev/null || true
    cp "$REPO_ROOT/src/services/voi_search.py" "$BUNDLE_DIR/src/services/" 2>/dev/null || true
    cp "$REPO_ROOT/src/services/interpretive_intelligence.py" "$BUNDLE_DIR/src/services/" 2>/dev/null || true

    # Technical debt files
    cp "$REPO_ROOT/src/services/theory_matcher.py" "$BUNDLE_DIR/src/services/" 2>/dev/null || true
    cp "$REPO_ROOT/src/services/scope_extractor.py" "$BUNDLE_DIR/src/services/" 2>/dev/null || true
    cp "$REPO_ROOT/src/services/scalable_coherence.py" "$BUNDLE_DIR/src/services/" 2>/dev/null || true
    cp "$REPO_ROOT/src/services/incremental_bn.py" "$BUNDLE_DIR/src/services/" 2>/dev/null || true

    # Schemas
    cp "$REPO_ROOT/contracts/schemas/"*.json "$BUNDLE_DIR/contracts/schemas/" 2>/dev/null || true

    # Panel documents
    cp "$REPO_ROOT/docs/PANEL_"*.md "$BUNDLE_DIR/docs/" 2>/dev/null || true
    cp "$REPO_ROOT/docs/SPRINT_"*.md "$BUNDLE_DIR/docs/" 2>/dev/null || true
fi

# The ruthless review prompt
cp "$REPO_ROOT/docs/RUTHLESS_REVIEW_PROMPT_V5_${DATE}.md" "$BUNDLE_DIR/" 2>/dev/null || \
    cp "$REPO_ROOT/Post_Quinean Setup/ruthless_prompts/RUTHLESS_SYSTEM_REVIEW_PROMPT_v3_2026_01_22.md" "$BUNDLE_DIR/REVIEW_PROMPT.md" 2>/dev/null || true

# Test summary if available
if [ -f /tmp/test_summary.txt ]; then
    cp /tmp/test_summary.txt "$BUNDLE_DIR/"
fi

# Generate file manifest
echo ""
echo "Files included:"
find "$BUNDLE_DIR" -type f | sed "s|$BUNDLE_DIR/||" | sort

# Step 4: Create zip
echo ""
echo "[4/4] Creating zip bundle..."
cd /tmp
rm -f "$OUTPUT_ZIP"
zip -r "$OUTPUT_ZIP" "ruthless_bundle_${DATE}" -x "*.pyc" -x "__pycache__/*"

# Cleanup
rm -rf "$BUNDLE_DIR"

echo ""
echo "============================================="
echo "Bundle created: $OUTPUT_ZIP"
echo "Size: $(du -h "$OUTPUT_ZIP" | cut -f1)"
echo ""
echo "To use:"
echo "  1. Upload to ChatGPT/Gemini/Codex"
echo "  2. Include the REVIEW_PROMPT.md content"
echo "  3. Request ruthless critique"
echo "============================================="
