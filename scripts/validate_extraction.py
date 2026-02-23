
import json
import pandas as pd
import os
import sys
import re
from collections import defaultdict

# Constants
GOLD_CSV_PATH = "data/table_gold/codex_gold_v1/codex_gold_rows.csv"
EXTRACTED_JSON_PATH = "data/production/structured_claims.json"
REPORT_PATH = "docs/extraction_validation_report.md"

def load_gold_standard():
    """Lengths the gold standard CSV and filters for findings."""
    if not os.path.exists(GOLD_CSV_PATH):
        print(f"Error: Gold standard CSV not found at {GOLD_CSV_PATH}")
        return None
    
    df = pd.read_csv(GOLD_CSV_PATH)
    # Filter for 'finding' claim type as these are the core extractions
    findings = df[df['claim_type'] == 'finding'].copy()
    return findings

def load_extracted_claims():
    """Loads the extracted claims JSON if it exists."""
    if not os.path.exists(EXTRACTED_JSON_PATH):
        print(f"Warning: Extracted claims file not found at {EXTRACTED_JSON_PATH}. This is expected if D.10 is not complete.")
        return []
    
    try:
        with open(EXTRACTED_JSON_PATH, 'r') as f:
            data = json.load(f)
            return data.get('claims', [])
    except Exception as e:
        print(f"Error reading extracted claims: {e}")
        return []

def normalize_text(text):
    """Basic text normalization for fuzzy matching."""
    if not isinstance(text, str):
        return ""
    return " ".join(text.lower().split())


def infer_direction_from_text(text):
    """Heuristic direction parsing for gold rows and extracted quotes."""
    t = normalize_text(text)
    if not t:
        return "unknown"
    if any(tok in t for tok in ["↓", "decrease", "decreased", "reduced", "lower", "negative"]):
        return "decrease"
    if any(tok in t for tok in ["↑", "increase", "increased", "improved", "higher", "positive"]):
        return "increase"
    if any(tok in t for tok in ["no effect", "non-significant", "non significant", "ns", "p > .05", "p >= 0.05"]):
        return "no_effect"
    return "unknown"

def evaluate_extraction(gold_df, extracted_claims):
    """
    Compares gold standard rows with extracted claims.
    Matching strategy:
    - Primary key: paper_id (must match)
    - Logic: Check if gold 'content' or variable names are 'covered' by extraction.
    
    Since we don't have perfect alignment keys yet, we'll using a simple containment check 
    for the 'content' field as a proxy for a "match".
    """
    
    # 1. Group by Paper
    gold_by_paper = gold_df.groupby('paper_id')
    extracted_by_paper = defaultdict(list)
    for claim in extracted_claims:
        if 'paper_id' in claim:
            extracted_by_paper[claim['paper_id']].append(claim)
            
    metrics = {
        'tp': 0, 'fp': 0, 'fn': 0,
        'papers_with_gold': len(gold_by_paper),
        'papers_with_extraction': len(extracted_by_paper),
        'direction_eval_pairs': 0,
        'direction_matches': 0,
        'direction_mismatches': 0,
        'direction_unknown_either': 0,
    }
    
    details = []
    
    for paper_id, group in gold_by_paper:
        gold_rows = group.to_dict('records')
        extracted_rows = extracted_by_paper.get(paper_id, [])
        
        # Simple pairwise match
        # We assume one gold finding map to one extracted claim (1:1 ideal)
        # We'll use a greedy matching approach based on text overlap
        
        matched_gold_indices = set()
        matched_extracted_indices = set()
        
        for g_idx, gold in enumerate(gold_rows):
            gold_content = normalize_text(gold.get('content', ''))
            
            best_match_idx = -1
            best_score = 0
            
            for e_idx, claim in enumerate(extracted_rows):
                if e_idx in matched_extracted_indices:
                    continue
                
                # Check for claim content or IV/DV match
                claim_content = normalize_text(claim.get('iv_raw', '') + " " + claim.get('dv_raw', '') + " " + claim.get('source_quote', ''))
                
                # Simple Jaccard-ish overlap
                set_g = set(gold_content.split())
                set_c = set(claim_content.split())
                if not set_g: continue
                
                overlap = len(set_g.intersection(set_c)) / len(set_g)
                
                if overlap > 0.3: # Threshold
                    if overlap > best_score:
                        best_score = overlap
                        best_match_idx = e_idx
            
            if best_match_idx != -1:
                matched_gold_indices.add(g_idx)
                matched_extracted_indices.add(best_match_idx)
                metrics['tp'] += 1
                matched_claim = extracted_rows[best_match_idx]
                gold_direction = infer_direction_from_text(gold.get('content', ''))
                extracted_direction = normalize_text(matched_claim.get('direction', '')).strip() or "unknown"
                if extracted_direction == "positive":
                    extracted_direction = "increase"
                elif extracted_direction == "negative":
                    extracted_direction = "decrease"
                if gold_direction == "unknown" or extracted_direction == "unknown":
                    metrics['direction_unknown_either'] += 1
                else:
                    metrics['direction_eval_pairs'] += 1
                    if gold_direction == extracted_direction:
                        metrics['direction_matches'] += 1
                    else:
                        metrics['direction_mismatches'] += 1
                        details.append(
                            f"DIR-MISMATCH [Paper {paper_id[-8:]}]: gold={gold_direction} extracted={extracted_direction} "
                            f"| gold='{gold_content[:70]}...'"
                        )
            else:
                metrics['fn'] += 1
                details.append(f"MISS [Paper {paper_id[-8:]}]: {gold_content[:100]}...")
                
        metrics['fp'] += len(extracted_rows) - len(matched_extracted_indices)

    return metrics, details

def generate_report(metrics, details):
    lines = []
    lines.append("# Extraction Validation Report")
    lines.append(f"**Date:** {pd.Timestamp.now()}\n")
    
    lines.append("## Executive Summary")
    if metrics['papers_with_extraction'] == 0:
        lines.append("> **WARNING:** No extracted claims found. Pipeline D.10 likely not run yet.")
    
    tp = metrics['tp']
    fp = metrics['fp']
    fn = metrics['fn']
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    lines.append(f"- **Precision:** {precision:.2f}")
    lines.append(f"- **Recall:** {recall:.2f}")
    lines.append(f"- **F1 Score:** {f1:.2f}\n")
    dir_pairs = metrics.get('direction_eval_pairs', 0)
    dir_match = metrics.get('direction_matches', 0)
    dir_acc = dir_match / dir_pairs if dir_pairs else 0
    lines.append("## Direction Quality")
    lines.append(f"- Direction pairs evaluated: {dir_pairs}")
    lines.append(f"- Direction matches: {dir_match}")
    lines.append(f"- Direction mismatches: {metrics.get('direction_mismatches', 0)}")
    lines.append(f"- Direction unknown in gold or extraction: {metrics.get('direction_unknown_either', 0)}")
    lines.append(f"- Direction accuracy (evaluated pairs): {dir_acc:.2f}\n")
    
    lines.append("## Counts")
    lines.append(f"- True Positives (Matched Claims): {tp}")
    lines.append(f"- False Positives (Spurious/Unmatched): {fp}")
    lines.append(f"- False Negatives (Missed Gold Claims): {fn}")
    lines.append(f"- Papers in Gold Standard: {metrics['papers_with_gold']}")
    lines.append(f"- Papers with Extractions: {metrics['papers_with_extraction']}\n")
    
    lines.append("## Missed Claims (Sample)")
    if details:
        for d in details[:20]:
            lines.append(f"- {d}")
    else:
        lines.append("None.")
        
    with open(REPORT_PATH, "w") as f:
        f.write("\n".join(lines))
    print(f"Report generated at {REPORT_PATH}")

def main():
    print("Loading Gold Standard...")
    gold_df = load_gold_standard()
    if gold_df is None: return
    
    print("Loading Extracted Claims...")
    extracted_claims = load_extracted_claims()
    
    print("Evaluating...")
    metrics, details = evaluate_extraction(gold_df, extracted_claims)
    
    print("Generating Report...")
    generate_report(metrics, details)

if __name__ == "__main__":
    main()
