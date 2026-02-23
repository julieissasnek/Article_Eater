#!/bin/bash
# Master script to run all remaining Toulmin retrofits

echo "Running CC assigned panels..."
python3 scripts/apply_toulmin_justification.py --panel LIGHT-I
python3 scripts/apply_toulmin_justification.py --panel STRESS-I

echo "Checking validation..."
python3 scripts/validate_toulmin.py

echo "Done. SOCIAL, MEMORY, and MULTI will require custom extraction scripts."

echo "Running custom extractions (requires CC to populate data fields first)..."
# python3 scripts/extract_toulmin_social.py
# python3 scripts/extract_toulmin_memory.py
# python3 scripts/extract_toulmin_multi.py

echo "Final Validation Check..."
python3 scripts/validate_toulmin.py
