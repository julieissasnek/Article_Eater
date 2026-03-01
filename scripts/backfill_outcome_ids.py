#!/usr/bin/env python3
"""
Sprint S-3: Outcome Backfill & Lookup Regeneration
====================================================

1. Regenerates outcome_lookup.json from the expanded outcome_vocab.json
2. Backfills existing extraction JSONs with canonical outcome_ids
3. Reports coverage improvement

Usage:
    python scripts/backfill_outcome_ids.py                 # Full analysis + backfill
    python scripts/backfill_outcome_ids.py --regen-only    # Only regenerate lookup
    python scripts/backfill_outcome_ids.py --dry-run       # Report only, no writes
"""

import argparse
import json
import sys
from pathlib import Path
from collections import Counter
from difflib import SequenceMatcher
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

VOCAB_PATH = PROJECT_ROOT / "contracts" / "outcome_vocab" / "outcome_vocab.json"
LOOKUP_PATH = PROJECT_ROOT / "contracts" / "outcome_vocab" / "outcome_lookup.json"
EXTRACTIONS_DIR = PROJECT_ROOT / "data" / "extractions"
TEMPLATES_DIR = PROJECT_ROOT / "data" / "templates"


# =============================================================================
# Step 1: Regenerate outcome_lookup.json
# =============================================================================

def regenerate_lookup():
    """Rebuild lookup table from vocab, including all cognates."""
    with open(VOCAB_PATH) as f:
        vocab = json.load(f)
    
    lookup = {}
    terms_dict = {}
    
    for term in vocab["terms"]:
        tid = term["term_id"]
        terms_dict[tid] = {
            "name": term["name"],
            "domain": term["domain"],
            "level": term.get("level", 1),
            "parent_id": term.get("parent_id"),
            "operationalizations": term.get("operationalizations", []),
        }
        
        # Add to lookup: name + all cognates
        lookup[term["name"].lower()] = tid
        for cognate in term.get("cognates", []):
            lookup[cognate.lower()] = tid
    
    data = {
        "schema": "outcome_lookup.v2",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_version": vocab.get("version", "1.0.0"),
        "lookup": lookup,
        "terms": terms_dict,
    }
    
    with open(LOOKUP_PATH, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Regenerated lookup: {len(lookup)} entries from {len(terms_dict)} terms")
    return data


# =============================================================================
# Step 2: Backfill extractions with canonical outcome_ids
# =============================================================================

def backfill_extractions(lookup_data, dry_run=False):
    """Scan extraction JSONs and add/update outcome_id fields."""
    lookup = lookup_data["lookup"]
    terms = lookup_data["terms"]
    stats = Counter()
    
    extraction_files = sorted(EXTRACTIONS_DIR.glob("*.json"))
    print(f"\nProcessing {len(extraction_files)} extractions...")
    
    for i, ef in enumerate(extraction_files):
        try:
            with open(ef) as f:
                data = json.load(f)
            
            modified = False
            findings = data.get("findings", data.get("claims", []))
            if not isinstance(findings, list):
                stats["skip_no_findings"] += 1
                continue
            
            for finding in findings:
                if not isinstance(finding, dict):
                    continue
                
                # Check if already has canonical outcome_id
                existing_oid = finding.get("outcome_id", "")
                if existing_oid and not existing_oid.startswith("UNRESOLVED:"):
                    stats["already_canonical"] += 1
                    continue
                
                # Try to resolve from consequent text
                raw = finding.get("consequent", finding.get("outcome", ""))
                if not raw or not isinstance(raw, str):
                    stats["no_consequent"] += 1
                    continue
                
                resolved = _resolve(raw, lookup, terms)
                if resolved:
                    finding["outcome_id"] = resolved["canonical_id"]
                    finding["outcome_domain"] = resolved["domain"]
                    finding["outcome_match_type"] = resolved["match_type"]
                    finding["outcome_confidence"] = resolved["confidence"]
                    modified = True
                    stats["resolved"] += 1
                    stats[f"domain_{resolved['domain']}"] += 1
                else:
                    stats["unresolved"] += 1
            
            if modified and not dry_run:
                with open(ef, "w") as f:
                    json.dump(data, f, indent=2)
                stats["files_modified"] += 1
            
        except Exception as e:
            stats["errors"] += 1
        
        if (i + 1) % 200 == 0:
            print(f"  {i+1}/{len(extraction_files)}...")
    
    return stats


def _resolve(raw_term, lookup, terms, fuzzy_threshold=0.7):
    """Resolve a raw term against the lookup table."""
    raw_lower = raw_term.lower().strip()
    
    # Exact match
    if raw_lower in lookup:
        tid = lookup[raw_lower]
        return {
            "canonical_id": tid,
            "domain": terms.get(tid, {}).get("domain", ""),
            "match_type": "exact",
            "confidence": 1.0,
        }
    
    # Substring match (if raw term contains a lookup key)
    for key, tid in lookup.items():
        if len(key) > 4 and key in raw_lower:
            return {
                "canonical_id": tid,
                "domain": terms.get(tid, {}).get("domain", ""),
                "match_type": "substring",
                "confidence": 0.8,
            }
    
    # Fuzzy match
    best_tid = None
    best_score = 0
    for key, tid in lookup.items():
        score = SequenceMatcher(None, raw_lower, key).ratio()
        if score > best_score:
            best_score = score
            best_tid = tid
    
    if best_score >= fuzzy_threshold:
        return {
            "canonical_id": best_tid,
            "domain": terms.get(best_tid, {}).get("domain", ""),
            "match_type": "fuzzy",
            "confidence": round(best_score, 3),
        }
    
    return None


# =============================================================================
# Step 3: Backfill Templates
# =============================================================================

def backfill_templates(lookup_data, dry_run=False):
    """Add outcome dimensions to templates based on their content."""
    lookup = lookup_data["lookup"]
    terms = lookup_data["terms"]
    stats = Counter()
    
    template_files = sorted(TEMPLATES_DIR.glob("*.json"))
    print(f"\nProcessing {len(template_files)} templates...")
    
    for tf in template_files:
        try:
            with open(tf) as f:
                data = json.load(f)
            
            # If template already has outcome_domains, skip
            if data.get("outcome_domains"):
                stats["already_tagged"] += 1
                continue
            
            # Scan template text for outcome-relevant terms
            text = " ".join([
                data.get("name", ""),
                data.get("bridge_warrant", ""),
                data.get("description", ""),
            ]).lower()
            
            found_domains = set()
            found_outcomes = []
            
            for key, tid in lookup.items():
                if len(key) > 4 and key in text:
                    domain = terms.get(tid, {}).get("domain", "")
                    if domain and domain not in found_domains:
                        found_domains.add(domain)
                        found_outcomes.append(tid)
            
            if found_outcomes:
                if not dry_run:
                    data["outcome_domains"] = sorted(found_domains)
                    data["outcome_terms"] = sorted(found_outcomes)[:5]  # Top 5
                    with open(tf, "w") as f:
                        json.dump(data, f, indent=2)
                
                stats["templates_tagged"] += 1
                for d in found_domains:
                    stats[f"template_domain_{d}"] += 1
            else:
                stats["templates_no_match"] += 1
                
        except Exception:
            stats["template_errors"] += 1
    
    return stats


def main():
    parser = argparse.ArgumentParser(description="Backfill outcome IDs")
    parser.add_argument("--regen-only", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    
    # Step 1: Regenerate lookup
    lookup_data = regenerate_lookup()
    
    if args.regen_only:
        return
    
    # Step 2: Backfill extractions
    ext_stats = backfill_extractions(lookup_data, dry_run=args.dry_run)
    
    # Step 3: Backfill templates
    tmpl_stats = backfill_templates(lookup_data, dry_run=args.dry_run)
    
    # Report
    print(f"\n{'='*60}")
    print(f"OUTCOME BACKFILL COMPLETE {'(DRY RUN)' if args.dry_run else ''}")
    print(f"{'='*60}")
    print(f"\nExtractions:")
    for k, v in sorted(ext_stats.items()):
        print(f"  {k}: {v}")
    
    total = ext_stats.get("resolved", 0) + ext_stats.get("already_canonical", 0) + ext_stats.get("unresolved", 0)
    if total > 0:
        coverage = (ext_stats.get("resolved", 0) + ext_stats.get("already_canonical", 0)) / total
        print(f"\n  Coverage: {coverage:.1%}")
    
    print(f"\nTemplates:")
    for k, v in sorted(tmpl_stats.items()):
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
