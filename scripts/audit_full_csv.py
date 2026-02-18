import pandas as pd
import sys
import os
import re
from collections import Counter

# Set input and output paths
INPUT_CSV = 'data/production/realtime_pdf_confirmed_rows.csv'
OUTPUT_REPORT = 'docs/full_csv_audit_report.md'

def main():
    print(f"Loading {INPUT_CSV}...")
    try:
        df = pd.read_csv(INPUT_CSV, low_memory=False)
    except Exception as e:
        print(f"Error loading CSV: {e}")
        sys.exit(1)

    print(f"Loaded {len(df)} rows.")

    # Initialize metrics dictionary
    metrics = {}
    
    # 1. Source Analysis
    print("Analyzing sources...")
    source_counts = df['source'].value_counts().to_dict()
    metrics['source_counts'] = source_counts

    # 2. Table Analysis
    print("Analyzing tables...")
    # Filter for table rows (usually source=pdfplumber or similar, but let's check 'source_table_id')
    # Assuming 'source_table_id' is populated for table extractions
    table_df = df[df['source_table_id'].notna()]
    metrics['total_table_rows'] = len(table_df)
    metrics['unique_tables'] = table_df['source_table_id'].nunique()
    
    if metrics['unique_tables'] > 0:
        rows_per_table = table_df['source_table_id'].value_counts()
        metrics['avg_rows_per_table'] = rows_per_table.mean()
    else:
        metrics['avg_rows_per_table'] = 0

    # Tables with at least one resolved environment variable
    # We look for rows where environment_variable is not null/empty and not "unresolved" if that's a value
    resolved_env_vars = table_df[
        (table_df['environment_variable'].notna()) & 
        (table_df['environment_variable'] != 'unresolved')
    ]
    metrics['tables_with_env_vars'] = resolved_env_vars['source_table_id'].nunique()
    
    # 3. OCR Quality & Anomalies
    print("Checking OCR quality...")
    
    # Check for doubled characters (e.g., "ttable", "ffindings") - naive check on 'statement'
    # We'll just take a sample or count occurrences of common double typos
    double_char_pattern = re.compile(r'\b(tt|ff|dd|ww)[a-z]+') 
    
    def has_doubled_typos(text):
        if not isinstance(text, str): return False
        # Simple heuristic: words starting with double letters that usually don't
        # e.g., ttable, ffindings, bbut
        # This is hard to do perfectly without a dictionary, but let's look for specific tell-tales
        # mentioned in the docs if any. 
        # For now, let's look for known OCR artifact patterns if we can find them.
        # Actually, let's just count rows where env_var == outcome_var as a proxy for bad extraction
        return False

    # Rows where env_var is same as outcome_var (common parsing error)
    same_var_rows = df[
        (df['environment_variable'].notna()) &
        (df['outcome_variable'].notna()) &
        (df['environment_variable'] == df['outcome_variable'])
    ]
    metrics['same_var_rows'] = len(same_var_rows)

    # Low confidence resolutions
    if 'environment_resolution_confidence' in df.columns:
        low_conf_env = df[
            (df['environment_resolution_confidence'].notna()) & 
            (df['environment_resolution_confidence'] < 0.3)
        ]
        metrics['low_conf_env_resolutions'] = len(low_conf_env)
    
    # Domain inferred
    # Assuming 'provenance_tier' or similar might have 'domain_inferred'? 
    # Or checking if 'environment_variable' contains "domain_inferred" string?
    # Let's check the 'environment_resolution_match_type' column if it exists
    if 'environment_resolution_match_type' in df.columns:
        domain_inferred = df[df['environment_resolution_match_type'] == 'domain_inferred']
        metrics['domain_inferred_resolutions'] = len(domain_inferred)

    # 4. Discourse Analysis
    print("Analyzing discourse...")
    if 'claim_type' in df.columns:
        metrics['claim_type_counts'] = df['claim_type'].value_counts().to_dict()

    # 5. Paper Coverage
    print("Analyzing paper coverage...")
    metrics['unique_papers'] = df['paper_id'].nunique()
    
    # Papers with zero tables
    papers_with_tables = set(table_df['paper_id'].unique())
    all_papers = set(df['paper_id'].unique())
    metrics['papers_without_tables'] = len(all_papers - papers_with_tables)

    # 6. "Good" Variable Pairs
    print("Finding good variable pairs...")
    # Both present, high confidence
    good_pairs = df[
        (df['environment_variable'].notna()) &
        (df['outcome_variable'].notna()) &
        (df['environment_resolution_confidence'] >= 0.5) &
        (df['outcome_resolution_confidence'] >= 0.5)
    ]
    metrics['high_conf_pairs_count'] = len(good_pairs)
    
    top_pairs = []
    if not good_pairs.empty:
        pair_counts = good_pairs.groupby(['environment_variable', 'outcome_variable']).size().nlargest(20)
        for (env, out), count in pair_counts.items():
            top_pairs.append(f"- {env} -> {out}: {count}")
            
    metrics['top_pairs'] = top_pairs

    # Generate Report
    print("Generating report...")
    with open(OUTPUT_REPORT, 'w') as f:
        f.write("# Sprint D.4: Full CSV Audit Report\n\n")
        
        f.write("## 1. Overview\n")
        f.write(f"- **Total Rows:** {len(df)}\n")
        f.write(f"- **Total Papers:** {metrics['unique_papers']}\n")
        f.write(f"- **Source File:** `{INPUT_CSV}`\n\n")
        
        f.write("## 2. Source Breakdown\n")
        for source, count in metrics['source_counts'].items():
            f.write(f"- **{source}:** {count} ({count/len(df)*100:.1f}%)\n")
        f.write("\n")
        
        f.write("## 3. Table Extraction Health\n")
        f.write(f"- **Unique Tables Detected:** {metrics['unique_tables']}\n")
        f.write(f"- **Avg Rows Per Table:** {metrics['avg_rows_per_table']:.2f}\n")
        f.write(f"- **Tables with ≥1 Resolved Env Variable:** {metrics['tables_with_env_vars']}\n")
        f.write(f"- **Papers WITHOUT Extracted Tables:** {metrics['papers_without_tables']}\n\n")
        
        f.write("## 4. Data Quality Issues\n")
        f.write(f"- **Rows where Env Var == Outcome Var:** {metrics.get('same_var_rows', 0)}\n")
        f.write(f"- **Low Confidence Env Resolutions (<0.3):** {metrics.get('low_conf_env_resolutions', 0)}\n")
        f.write(f"- **Domain Inferred Resolutions:** {metrics.get('domain_inferred_resolutions', 0)}\n\n")
        
        f.write("## 5. Discourse Classification\n")
        if 'claim_type_counts' in metrics:
            for ctype, count in metrics['claim_type_counts'].items():
                f.write(f"- **{ctype}:** {count}\n")
        f.write("\n")
        
        f.write("## 6. High Confidence Variable Pairs (Sample)\n")
        f.write(f"Total High Confidence Pairs (both > 0.5): {metrics['high_conf_pairs_count']}\n")
        if metrics['top_pairs']:
            f.write("Top 20 frequent pairs:\n")
            for pair in metrics['top_pairs']:
                f.write(f"{pair}\n")
        else:
            f.write("No high confidence pairs found.\n")

    print(f"Report generated at {OUTPUT_REPORT}")

if __name__ == "__main__":
    main()
