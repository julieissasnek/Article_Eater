#!/usr/bin/env python3
"""
Part 2: Comprehensive integration validation script.
Validates JSON schemas, extraction files, cross-references, and calibration data.
"""
import json
import os
from pathlib import Path

repo = Path(".")
errors = []

print("\n=== INTEGRATION TEST RESULTS ===\n")

# Check all JSON files in contracts/
print("1. Validating contract JSONs...")
contract_dir = Path("contracts")
contract_valid = 0
contract_files = list(contract_dir.rglob("*.json"))
for jf in contract_files:
    try:
        json.loads(jf.read_text())
        contract_valid += 1
    except Exception as e:
        errors.append(f"INVALID JSON: {jf}: {e}")

print(f"   Contracts: {contract_valid}/{len(contract_files)} valid")

# Check all extraction files
print("2. Validating extraction files...")
ext_dir = Path("data/extractions")
n_ext = 0
n_valid = 0
n_empty = 0
n_with_findings = 0
total_findings = 0

if ext_dir.exists():
    for jf in ext_dir.glob("*.json"):
        n_ext += 1
        try:
            data = json.loads(jf.read_text(errors='replace'))
            n_valid += 1
            nf = data.get("n_findings", 0)
            if nf == 0:
                n_empty += 1
            else:
                n_with_findings += 1
                total_findings += nf
        except Exception as e:
            errors.append(f"BAD EXTRACTION: {jf.name}")
else:
    print("   WARNING: data/extractions directory not found")

print(f"   Extractions: {n_ext} total, {n_valid} valid JSON")
print(f"   Coverage: {n_with_findings} articles with findings, {n_empty} empty")
if n_with_findings > 0:
    print(f"   Mean findings/article: {total_findings/n_with_findings:.1f}")

# Check cross-references: vocab -> instruments
print("3. Validating cross-references...")
vocab_file = Path("contracts/outcome_vocab/outcome_vocab.json")
registry_file = Path("contracts/instruments/instruments_registry.json")

broken_refs = []
try:
    if vocab_file.exists() and registry_file.exists():
        vocab = json.loads(vocab_file.read_text())
        registry = json.loads(registry_file.read_text())

        registry_ids = set()
        for cat in registry.get("categories", registry.get("instruments", [])):
            if isinstance(cat, dict):
                for inst in cat.get("instruments", [cat]):
                    registry_ids.add(inst.get("id", ""))
                    registry_ids.add(inst.get("abbreviation", ""))

        for term in vocab.get("terms", []):
            for iid in term.get("instrument_ids", []):
                if iid and iid not in registry_ids:
                    broken_refs.append(f"{term['id']} -> {iid}")

        if broken_refs:
            print(f"   BROKEN: {len(broken_refs)} cross-references")
            for ref in broken_refs[:5]:
                print(f"      - {ref}")
        else:
            print(f"   VALID: All vocab->instruments cross-refs OK")
    else:
        print(f"   WARNING: vocab or registry files not found")
except Exception as e:
    errors.append(f"CROSS_REF_ERROR: {e}")

# Check calibration files
print("4. Validating calibration files...")
cal_dir = Path("data/calibration")
cal_files = list(cal_dir.glob("*.json")) if cal_dir.exists() else []
cal_valid = 0
for cf in cal_files:
    try:
        json.loads(cf.read_text())
        cal_valid += 1
    except Exception as e:
        errors.append(f"BAD CALIBRATION: {cf.name}")

print(f"   Calibration: {cal_valid}/{len(cal_files)} valid")

# Summary
print("\n=== VALIDATION SUMMARY ===")
print(f"Contract JSONs: {contract_valid}/{len(contract_files)} valid")
print(f"Extractions: {n_valid}/{n_ext} valid (coverage: {n_with_findings} articles)")
print(f"Cross-refs: {'BROKEN' if broken_refs else 'ALL VALID'}")
print(f"Calibration: {cal_valid}/{len(cal_files)} valid")
print(f"Total errors: {len(errors)}")

if errors:
    print("\nErrors found:")
    for e in errors[:10]:
        print(f"  - {e}")
    if len(errors) > 10:
        print(f"  ... and {len(errors) - 10} more")

# Score extraction health
extraction_score = 100 if n_ext > 0 else 0
if n_ext > 0:
    extraction_score = int((n_valid / n_ext) * 100)

coverage_score = 0
if n_ext > 0:
    coverage_score = int((n_with_findings / n_ext) * 100)

print(f"\n=== EXTRACTION HEALTH SCORES ===")
print(f"Validity Score: {extraction_score}%")
print(f"Coverage Score: {coverage_score}%")
print(f"Mean findings: {total_findings/max(n_with_findings, 1):.1f}")
