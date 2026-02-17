#!/bin/bash
# =============================================================================
# Article Eater V22.0.0 - System Test Script
# =============================================================================
# Tests server startup, APIs, GUIs, and Gallery builder
# Run with: ./bin/test_system.sh
# =============================================================================

set -e

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASS=0
FAIL=0

echo "=============================================="
echo "Article Eater V22.0.0 - System Test"
echo "=============================================="
echo ""

# Helper functions
pass() {
    echo -e "${GREEN}✓ PASS${NC}: $1"
    PASS=$((PASS + 1))
}

fail() {
    echo -e "${RED}✗ FAIL${NC}: $1"
    FAIL=$((FAIL + 1))
}

warn() {
    echo -e "${YELLOW}⚠ WARN${NC}: $1"
}

section() {
    echo ""
    echo "----------------------------------------------"
    echo "$1"
    echo "----------------------------------------------"
}

# =============================================================================
# TEST 1: Python Environment
# =============================================================================
section "1. Python Environment"

if [ -f "./venv/bin/python3" ]; then
    PYTHON="./venv/bin/python3"
    PYTHON_VERSION=$($PYTHON --version 2>&1)
    pass "venv exists ($PYTHON_VERSION)"
else
    fail "venv not found - run: python3 -m venv venv"
    exit 1
fi

# =============================================================================
# TEST 2: Core Imports
# =============================================================================
section "2. Core Imports"

$PYTHON -c "from app.main import app" 2>/dev/null && pass "app.main imports" || fail "app.main import failed"
$PYTHON -c "from app.routes.galleries import router" 2>/dev/null && pass "galleries router imports" || fail "galleries router import failed"
$PYTHON -c "from app.routes.annotator import router" 2>/dev/null && pass "annotator router imports" || fail "annotator router import failed"
$PYTHON -c "from src.services.claim_gallery_builder import ClaimGalleryBuilder" 2>/dev/null && pass "ClaimGalleryBuilder imports" || fail "ClaimGalleryBuilder import failed"

# =============================================================================
# TEST 3: Gallery Builder Functionality
# =============================================================================
section "3. Gallery Builder"

$PYTHON << 'EOF'
import sys
from src.services.claim_gallery_builder import (
    ClaimGalleryBuilder, ClaimInfo, ClaimFeature, ClaimOutcome,
    EvidenceQuality, GalleryScope, PersonaProfile
)

# Create test data
claim = ClaimInfo(
    claim_id="test_claim",
    statement="Test claim about feature X affecting outcome Y in environment Z",
    feature=ClaimFeature(feature_id="feat_x", feature_name="Feature X"),
    outcome=ClaimOutcome(outcome_id="out_y", outcome_name="Outcome Y")
)

image_pool = [
    {"image_id": f"img_{i}", "uri_or_path": f"/img_{i}.jpg",
     "feature_score": 0.1 + (i * 0.05), "source": "test", "license": "CC BY"}
    for i in range(15)
]

evidence = EvidenceQuality(design_strength=0.7, consistency=0.6, portability=0.5)
scope = GalleryScope(population="Adults", setting="Office", task_context="Work", measurement_context="Survey")

# Build gallery
builder = ClaimGalleryBuilder(persona=PersonaProfile.DEFAULT)
gallery = builder.build_gallery(claim, image_pool, evidence, scope)

# Verify
assert gallery.gallery_id.startswith("gal_"), "Gallery ID format wrong"
assert len(gallery.slots.central_positive) > 0, "No positive images"
assert len(gallery.slots.central_negative) > 0, "No negative images"

log = builder.get_selection_log()
assert log is not None, "No selection log"

print("Gallery built successfully:")
print(f"  - ID: {gallery.gallery_id}")
print(f"  - Positives: {len(gallery.slots.central_positive)}")
print(f"  - Negatives: {len(gallery.slots.central_negative)}")
print(f"  - Near-miss: {len(gallery.slots.near_miss)}")
sys.exit(0)
EOF

if [ $? -eq 0 ]; then
    pass "Gallery builder works"
else
    fail "Gallery builder failed"
fi

# =============================================================================
# TEST 4: Determinism
# =============================================================================
section "4. Determinism Test"

$PYTHON << 'EOF'
import sys
from src.services.claim_gallery_builder import (
    ClaimGalleryBuilder, ClaimInfo, ClaimFeature, ClaimOutcome,
    EvidenceQuality, GalleryScope
)

claim = ClaimInfo(
    claim_id="det_test",
    statement="Determinism test claim for reproducibility verification",
    feature=ClaimFeature(feature_id="feat_det", feature_name="Det Feature"),
    outcome=ClaimOutcome(outcome_id="out_det", outcome_name="Det Outcome")
)

pool = [
    {"image_id": f"d{i}", "uri_or_path": f"/d{i}.jpg",
     "feature_score": 0.1 + (i * 0.06), "source": "test", "license": "CC BY"}
    for i in range(12)
]

evidence = EvidenceQuality(design_strength=0.7, consistency=0.6, portability=0.5)
scope = GalleryScope(population="Adults", setting="Office", task_context="Work", measurement_context="Survey")

# Build twice with same seed
b1 = ClaimGalleryBuilder(random_seed=42)
b2 = ClaimGalleryBuilder(random_seed=42)

g1 = b1.build_gallery(claim, pool, evidence, scope, config_id="det", snapshot_id="snap1")
g2 = b2.build_gallery(claim, pool, evidence, scope, config_id="det", snapshot_id="snap1")

# Must be identical
assert g1.gallery_id == g2.gallery_id, f"IDs differ: {g1.gallery_id} vs {g2.gallery_id}"

ids1 = [img.image_id for img in g1.slots.central_positive]
ids2 = [img.image_id for img in g2.slots.central_positive]
assert ids1 == ids2, f"Selected images differ: {ids1} vs {ids2}"

print("Determinism verified: same inputs → same outputs")
sys.exit(0)
EOF

if [ $? -eq 0 ]; then
    pass "Determinism works"
else
    fail "Determinism failed"
fi

# =============================================================================
# TEST 5: pytest (if available)
# =============================================================================
section "5. Unit Tests (pytest)"

if $PYTHON -c "import pytest" 2>/dev/null; then
    echo "Running pytest on gallery builder tests..."
    if $PYTHON -m pytest tests/test_claim_gallery_builder.py -q --tb=no 2>/dev/null; then
        pass "pytest tests pass"
    else
        fail "pytest tests failed"
    fi
else
    warn "pytest not installed, skipping unit tests"
fi

# =============================================================================
# TEST 6: Server Startup (quick check)
# =============================================================================
section "6. Server Startup Test"

# Start server in background
echo "Starting server on port 8765..."
$PYTHON -m uvicorn app.main:app --port 8765 &
SERVER_PID=$!
sleep 3

# Check if server is running
if kill -0 $SERVER_PID 2>/dev/null; then
    pass "Server started (PID: $SERVER_PID)"

    # Test health endpoint
    if curl -s http://localhost:8765/healthz | grep -q "ok\|healthy" 2>/dev/null; then
        pass "Health endpoint responds"
    else
        warn "Health endpoint didn't return expected response"
    fi

    # Test API docs
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8765/docs | grep -q "200"; then
        pass "API docs accessible"
    else
        warn "API docs not accessible"
    fi

    # Test GUI pages
    for page in "article-annotator" "claim-gallery" "evidence-explorer"; do
        CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8765/$page" 2>/dev/null)
        if [ "$CODE" = "200" ]; then
            pass "/$page page loads"
        else
            fail "/$page returned $CODE"
        fi
    done

    # Test galleries API
    CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8765/api/v1/galleries/" 2>/dev/null)
    if [ "$CODE" = "200" ]; then
        pass "Galleries API responds"
    else
        fail "Galleries API returned $CODE"
    fi

    # Stop server
    kill $SERVER_PID 2>/dev/null
    # uvicorn exits via SIGTERM here; do not fail the harness on expected 143.
    wait $SERVER_PID 2>/dev/null || true
    echo "Server stopped."
else
    fail "Server failed to start"
fi

# =============================================================================
# TEST 7: Schema Files
# =============================================================================
section "7. Schema Files"

SCHEMA_DIR="contracts/ae_af/schemas"
for schema in "claim_gallery.v1" "gallery_selection_config.v1" "image_feedback.v1" "selection_log.v1"; do
    if [ -f "$SCHEMA_DIR/${schema}.schema.json" ]; then
        pass "$schema schema exists"
    else
        fail "$schema schema missing"
    fi
done

# Check for missing schema from spec
if [ -f "$SCHEMA_DIR/image_pool_snapshot.v1.schema.json" ]; then
    pass "image_pool_snapshot schema exists"
else
    warn "image_pool_snapshot schema not yet created (in todo list)"
fi

# =============================================================================
# TEST 8: Frontend Files
# =============================================================================
section "8. Frontend Files"

for file in "article-annotator.html" "claim-gallery.html" "evidence-explorer.html"; do
    if [ -f "frontend/$file" ]; then
        pass "$file exists"
    else
        fail "$file missing"
    fi
done

if [ -f "frontend/css/gallery-streamlit.css" ]; then
    pass "Gallery CSS exists"
else
    fail "Gallery CSS missing"
fi

# =============================================================================
# SUMMARY
# =============================================================================
echo ""
echo "=============================================="
echo "TEST SUMMARY"
echo "=============================================="
echo -e "${GREEN}Passed: $PASS${NC}"
echo -e "${RED}Failed: $FAIL${NC}"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed. Review output above.${NC}"
    exit 1
fi
