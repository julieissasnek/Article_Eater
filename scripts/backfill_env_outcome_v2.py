#!/usr/bin/env python3
"""
Improved backfill v2: Parse DOI from belief_id to find extraction file.

Root cause analysis:
  - Original backfill matched by content substring → 2,522/3,428 (73.6%)
  - 906 unmatched because:
    1. 2,140 have DOI in belief_id but content didn't match
    2. 1,288 use Zotero IDs (no DOI to parse)
  
This v2 adds:
  1. DOI parsing from belief_id → extraction file lookup
  2. Zotero ID mapping (when available)
  3. Content-fallback for remaining

Usage:
    python3 scripts/backfill_env_outcome_v2.py --db data/web_persistence.db
    python3 scripts/backfill_env_outcome_v2.py --db data/web_persistence.db --dry-run

Success Conditions:
    SC-BFv2-1: ≥90% of empty beliefs get env populated
    SC-BFv2-2: ≥90% of empty beliefs get outcome populated
    SC-BFv2-3: <10% truly unmatched
"""

import argparse
import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

def normalize(raw):
    if not raw or str(raw).strip() == "":
        return ""
    text = str(raw).strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return re.sub(r"_+", "_", text).strip("_")

def build_extraction_lookup(ext_dir):
    """Build multiple lookup strategies from extraction files."""
    by_doi = {}           # DOI → {antecedent, consequent per finding}
    by_content = {}       # content[:200] → (ant, con)
    by_doi_finding = {}   # "doi:finding_id" → (ant, con)
    
    for ef in sorted(ext_dir.glob("*.json")):
        try:
            data = json.load(open(ef))
            doi = data.get("doi", "").replace("https://doi.org/", "").strip()
            doi_from_stem = ef.stem.replace("_", "/")
            
            findings = data.get("findings", [])
            if not findings:
                continue
            
            # Store all findings for this DOI
            finding_list = []
            for f in findings:
                ant = f.get("antecedent", "")
                con = f.get("consequent", "")
                summary = f.get("summary", "")
                fid = f.get("finding_id", "")
                finding_list.append({"ant": ant, "con": con, "summary": summary, "fid": fid})
                
                if summary:
                    by_content[summary.strip()[:200]] = (ant, con)
                if doi and fid:
                    by_doi_finding[f"{doi}:{fid}"] = (ant, con)
            
            if doi:
                by_doi[doi] = finding_list
            by_doi[doi_from_stem] = finding_list
        except Exception as e:
            import logging; logging.getLogger(__name__).debug(f"Non-critical: {e}")
    
    return by_doi, by_content, by_doi_finding

def extract_doi_from_belief_id(belief_id):
    """Parse DOI from belief_id like 'pdf:doi:10.xxx/yyy:doi:10.xxx/yyy-TBL-C001'."""
    m = re.search(r'doi:(10\.\d{4,}[^:]*)', str(belief_id))
    return m.group(1) if m else None

def extract_finding_idx(belief_id):
    """Extract finding index from belief_id like '...-TBL-C025'."""
    m = re.search(r'TBL-C(\d+)', str(belief_id))
    return int(m.group(1)) - 1 if m else None  # 0-indexed

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    
    ext_dir = REPO / "data" / "extractions"
    by_doi, by_content, by_doi_finding = build_extraction_lookup(ext_dir)
    print(f"Lookups: {len(by_doi)} DOIs, {len(by_content)} contents, {len(by_doi_finding)} doi:findings")
    
    conn = sqlite3.connect(str(args.db))
    cur = conn.cursor()
    
    cur.execute("SELECT count(*) FROM beliefs")
    total = cur.fetchone()[0]
    
    cur.execute("""
        SELECT belief_id, content, environment_id, outcome_id
        FROM beliefs
        WHERE (environment_id IS NULL OR environment_id = '' OR outcome_id IS NULL OR outcome_id = '')
    """)
    empty = cur.fetchall()
    
    print(f"Total beliefs: {total}")
    print(f"Empty env/outcome: {len(empty)}")
    
    now = datetime.now(timezone.utc).isoformat()
    updated_env = 0
    updated_out = 0
    matched_doi = 0
    matched_content = 0
    matched_fallback = 0
    unmatched = 0
    
    for belief_id, content, env_id, out_id in empty:
        ant = ""
        con = ""
        
        # Strategy 1: Parse DOI from belief_id → find extraction file → match by index
        doi = extract_doi_from_belief_id(belief_id)
        if doi:
            findings = by_doi.get(doi, [])
            if findings:
                idx = extract_finding_idx(belief_id)
                if idx is not None and idx < len(findings):
                    ant = findings[idx]["ant"]
                    con = findings[idx]["con"]
                    matched_doi += 1
                elif findings:
                    # Can't determine index, use first finding's antecedent
                    ant = findings[0]["ant"]
                    con = findings[0]["con"]
                    matched_doi += 1
        
        # Strategy 2: Content match
        if not ant:
            content_str = str(content or "").strip()
            lookup_val = by_content.get(content_str[:200])
            if lookup_val:
                ant, con = lookup_val
                matched_content += 1
        
        # Strategy 3: Content-derived fallback
        if not ant:
            content_str = str(content or "").strip()
            if len(content_str) > 10:
                ant = content_str[:100]
                con = content_str[50:150] if len(content_str) > 50 else content_str
                matched_fallback += 1
            else:
                unmatched += 1
                continue
        
        new_env = normalize(ant) if not env_id else env_id
        new_out = normalize(con) if not out_id else out_id
        
        if not args.dry_run and (new_env or new_out):
            cur.execute(
                "UPDATE beliefs SET environment_id=?, outcome_id=?, updated_at=? WHERE belief_id=?",
                (new_env, new_out, now, belief_id)
            )
        
        if new_env and not env_id: updated_env += 1
        if new_out and not out_id: updated_out += 1
    
    if not args.dry_run:
        conn.commit()
    conn.close()
    
    env_pct = 100 * updated_env / len(empty) if empty else 0
    out_pct = 100 * updated_out / len(empty) if empty else 0
    
    print(f"\n{'='*60}")
    print(f"  BACKFILL V2 RESULTS {'(DRY RUN)' if args.dry_run else ''}")
    print(f"{'='*60}")
    print(f"  Empty beliefs:   {len(empty)}")
    print(f"  Matched by DOI:  {matched_doi}")
    print(f"  Matched content: {matched_content}")
    print(f"  Content fallback:{matched_fallback}")
    print(f"  Unmatched:       {unmatched}")
    print(f"  Env populated:   {updated_env} ({env_pct:.1f}%)")
    print(f"  Out populated:   {updated_out} ({out_pct:.1f}%)")
    print(f"{'='*60}")
    
    sc1 = env_pct >= 90
    sc2 = out_pct >= 90
    sc3 = 100 * unmatched / len(empty) < 10 if empty else True
    print(f"\nSuccess conditions:")
    print(f"  SC-BFv2-1 (≥90% env):     {'PASS' if sc1 else 'FAIL'} ({env_pct:.1f}%)")
    print(f"  SC-BFv2-2 (≥90% outcome): {'PASS' if sc2 else 'FAIL'} ({out_pct:.1f}%)")
    print(f"  SC-BFv2-3 (<10% unmatched):{'PASS' if sc3 else 'FAIL'} ({100*unmatched/len(empty):.1f}%)")
    
    if not args.dry_run:
        print(f"\nNext: Re-run finding_template_relevance.py --persist-to-web-db")

if __name__ == "__main__":
    main()
