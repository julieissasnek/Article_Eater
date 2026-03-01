#!/bin/bash
# ============================================================
# PLACEMENT COMMANDS — Run from your Article Eater repo root
# ============================================================
# Assumes you downloaded these files from Claude to ~/Downloads/
# Adjust the source path if you saved them elsewhere.

# The repo root is wherever you have:
#   src/extraction/article_type_contract.py
#   scripts/gemini_extraction_queue.py
#   data/templates/*.json

REPO_ROOT="/Users/davidusa/REPOS/article_extraction"
# ^^^ CHANGE THIS if your repo is at a different path

SRC="$HOME/Downloads"
# ^^^ CHANGE THIS if you saved the files somewhere else

# --- Place the two Python files ---
cp "$SRC/revised_prompts_v2.py"  "$REPO_ROOT/src/extraction/revised_prompts_v2.py"
cp "$SRC/pipeline_repairs.py"    "$REPO_ROOT/src/extraction/pipeline_repairs.py"

# --- Place the AG prompt ---
cp "$SRC/02-24_04_AG_Panel_Prompt.md"  "$REPO_ROOT/docs/02-24_04_AG_Panel_Prompt.md"

# --- Place the integration guide ---
cp "$SRC/02-24_03_Pipeline_Repair_Integration_Guide_V2.md"  "$REPO_ROOT/docs/02-24_03_Pipeline_Repair_Integration_Guide_V2.md"

# --- Place the audit doc ---
cp "$SRC/02-24_01_Extraction_Pipeline_Audit_and_Improved_AG_Prompt.md"  "$REPO_ROOT/docs/02-24_01_Extraction_Pipeline_Audit_and_Improved_AG_Prompt.md"

# --- Create the partial_extractions directory ---
mkdir -p "$REPO_ROOT/data/extraction_pipeline/partial_extractions"

# --- Verify ---
echo "=== Verification ==="
ls -la "$REPO_ROOT/src/extraction/revised_prompts_v2.py"
ls -la "$REPO_ROOT/src/extraction/pipeline_repairs.py"
ls -la "$REPO_ROOT/docs/02-24_04_AG_Panel_Prompt.md"
echo "=== Done ==="
