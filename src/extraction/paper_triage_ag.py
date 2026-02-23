"""
Paper triage classifier - Antigravity rule-based approach (Sprint D Task D.2).

Alternative implementation for comparison with dataclass-based approach.
"""

import pandas as pd
import json
import os
import re
from collections import Counter

# Inputs/Outputs
CSV_PATH = "data/production/realtime_pdf_confirmed_rows.csv"
TRIAGE_OUTPUT_PATH = "data/production/paper_triage.json"

def triage_papers():
    if not os.path.exists(CSV_PATH):
        print(f"Error: CSV not found at {CSV_PATH}")
        return

    print(f"Loading {CSV_PATH}...")

    # 1. First Pass: Detect columns using a safer read
    try:
        # Read just the header
        header_df = pd.read_csv(CSV_PATH, nrows=0)
        available_cols = set(header_df.columns)
        print(f"Columns found in CSV: {list(available_cols)}")
    except Exception as e:
        print(f"Error reading header: {e}")
        return

    # 2. Determine which desired columns are actually present
    desired_cols = ['paper_id', 'title', 'content', 'claim_type', 'article_type_predicted_family']
    use_cols = [c for c in desired_cols if c in available_cols]

    if not use_cols:
        print("Error: None of the required columns found!")
        return

    print(f"Reading columns: {use_cols}")

    # 3. Read the file comfortably
    try:
        # engine='python' is slower but more robust to bad lines/quoting than 'c'
        # on_bad_lines='warn' skips bad lines
        df = pd.read_csv(
            CSV_PATH,
            usecols=use_cols,
            engine='python',
            on_bad_lines='warn'
        )
    except Exception as e:
        print(f"Critical error reading CSV: {e}")
        # Last ditch: try reading without usecols
        try:
            print("Retrying without column filter...")
            df = pd.read_csv(CSV_PATH, engine='python', on_bad_lines='warn')
        except Exception as e2:
             print(f"Failed to read CSV: {e2}")
             return

    # Ensure missing columns exist in DF (filled with NaN) for logic safety
    for col in desired_cols:
        if col not in df.columns:
            df[col] = "" # Fill missing cols with empty string/NaN

    print(f"Loaded {len(df)} rows. Grouping by paper...")

    paper_groups = df.groupby('paper_id')
    triage_results = {}

    count_empirical = 0
    count_review = 0
    count_other = 0

    for paper_id, group in paper_groups:
        # Aggregate logic

        # 1. Metadata Signals
        # Predicted family from original scraping (if available/reliable)
        predicted_families = group['article_type_predicted_family'].dropna().unique()
        pred_family = predicted_families[0] if len(predicted_families) > 0 else "unknown"

        # Title (take first non-null)
        titles = group['title'].dropna().unique()
        title = titles[0] if len(titles) > 0 else ""
        title_lower = str(title).lower()

        # 2. Content Signals
        all_content = " ".join(group['content'].fillna("").astype(str).tolist()).lower()

        # Claim types
        claim_types = group['claim_type'].fillna("unknown").tolist()
        claim_counts = Counter(claim_types)
        total_rows = len(group)

        # 3. Rules
        is_empirical = False
        is_review = False
        confidence = 0.0

        # RULE A: Explicit exclusions
        if "editorial" in title_lower or "correction" in title_lower or "table of contents" in title_lower:
             triage_results[paper_id] = {
                "type": "other",
                "confidence": 0.9,
                "reason": "Explicit exclusion term in title"
            }
             count_other += 1
             continue

        # RULE B: Review/Meta-Analysis detection
        if "review" in title_lower or "meta-analysis" in title_lower:
            is_review = True
            confidence = 0.9
        elif claim_counts.get('inter_article_relation', 0) / total_rows > 0.8:
            # If >80% of rows are citations/relations, likely a review
            is_review = True
            confidence = 0.7

        # RULE C: Empirical detection
        # Look for empirical keywords in content
        empirical_keywords = ["participants", "n =", "n=", "anova", "regression", " correlation ", "experiment", "methodology", "results"]
        keyword_hits = sum(1 for k in empirical_keywords if k in all_content)

        if not is_review:
            if keyword_hits >= 2:
                is_empirical = True
                confidence = 0.5 + (0.1 * min(keyword_hits, 4)) # Cap bonus
            elif pred_family == 'empirical':
                 is_empirical = True
                 confidence = 0.6

        # Final Decision
        final_type = "other"

        if is_review:
            final_type = "review"
            count_review += 1
        elif is_empirical:
            final_type = "empirical"
            count_empirical += 1
        else:
            # Default to other, but if it has table rows it might be empirical but poorly parsed
            # If it has > 10 rows and wasn't flagged as review, lean empirical weak
            if total_rows > 10:
                final_type = "empirical"
                confidence = 0.4 # Low confidence fallback
                count_empirical += 1
            else:
                count_other += 1

        triage_results[paper_id] = {
            "type": final_type,
            "confidence": round(confidence, 2),
            "n_rows": total_rows,
            "title_snippet": title[:50]
        }

    print(f"Triage Complete.")
    print(f"Empirical: {count_empirical}")
    print(f"Review: {count_review}")
    print(f"Other: {count_other}")

    with open(TRIAGE_OUTPUT_PATH, "w") as f:
        json.dump(triage_results, f, indent=2)
    print(f"Saved to {TRIAGE_OUTPUT_PATH}")

if __name__ == "__main__":
    triage_papers()
