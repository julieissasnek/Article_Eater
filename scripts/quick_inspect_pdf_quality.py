
import csv
import sys
from collections import Counter
import statistics

FILE_PATH = 'data/production/realtime_pdf_confirmed_rows.csv'

def inspect_quality():
    print(f"Inspecting {FILE_PATH}...")
    
    try:
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    total_rows = len(rows)
    print(f"Total Rows: {total_rows}")
    if not rows:
        return

    # 1. Unique Papers
    if 'paper_id' in rows[0]:
        unique_papers = set(row['paper_id'] for row in rows if row.get('paper_id'))
        print(f"Unique Paper IDs: {len(unique_papers)}")
    
    # 2. Critical Columns Emptiness
    # Updated keys based on debug findings
    critical_cols = ['statement', 'environment_variable', 'outcome_variable', 'evidence_basis', 'relation_strength_hint', 'source_quote']
    print("\n--- Critical Column Fill Rates ---")
    for col in critical_cols:
        if col in rows[0]:
            filled = sum(1 for row in rows if row.get(col) and row.get(col).strip())
            fill_rate = (filled / total_rows) * 100
            print(f"{col}: {filled}/{total_rows} ({fill_rate:.1f}%)")
        else:
            print(f"{col}: COLUMN MISSING")

    # 3. Provenance Distribution
    if 'provenance_tier' in rows[0]:
        print("\n--- Provenance Tier Distribution ---")
        counts = Counter(row['provenance_tier'] for row in rows if row.get('provenance_tier'))
        for tier, count in counts.most_common():
            print(f"{tier}: {count}")
    
    # 4. Content length check
    if 'statement' in rows[0]:
        lengths = [len(row['statement']) for row in rows if row.get('statement')]
        if lengths:
            mean_len = statistics.mean(lengths)
            print(f"\nAverage Statement Length: {mean_len:.1f} chars")
        
    # 5. Significance/Strength distribution
    if 'relation_strength_hint' in rows[0]:
        print("\n--- Relation Strength Hint Distribution ---")
        counts = Counter(row['relation_strength_hint'] for row in rows if row.get('relation_strength_hint'))
        for sig, count in counts.most_common(10):
            print(f"{sig}: {count}")

if __name__ == "__main__":
    inspect_quality()
