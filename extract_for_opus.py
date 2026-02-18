#!/usr/bin/env python3
"""
Extract everything Opus needs to diagnose the PDF data quality gap.
Run from repo root:  python3 scripts/extract_for_opus.py > docs/opus_data_audit.md
"""

import csv
import os
import glob
import json
import sys
import importlib

OUTPUT = []

def section(title):
    OUTPUT.append(f"\n{'='*80}")
    OUTPUT.append(f"## {title}")
    OUTPUT.append('='*80 + "\n")

def subsection(title):
    OUTPUT.append(f"\n### {title}\n")

# ============================================================
# PART 1: CSV STRUCTURE AND SAMPLES
# ============================================================
section("PART 1: CSV STRUCTURE AND SAMPLES")

CSV_PATH = "data/production/realtime_pdf_confirmed_rows.csv"
if not os.path.exists(CSV_PATH):
    # Try other likely locations
    for candidate in glob.glob("data/**/realtime_pdf*.csv", recursive=True):
        CSV_PATH = candidate
        break

if not os.path.exists(CSV_PATH):
    OUTPUT.append(f"ERROR: Cannot find CSV. Searched: data/production/ and data/**/")
    OUTPUT.append(f"Files in data/: {os.listdir('data/') if os.path.exists('data/') else 'NO DATA DIR'}")
else:
    OUTPUT.append(f"**CSV Path:** `{CSV_PATH}`")
    OUTPUT.append(f"**CSV Size:** {os.path.getsize(CSV_PATH) / 1e6:.1f} MB")

    with open(CSV_PATH, newline='', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        all_columns = reader.fieldnames
        OUTPUT.append(f"**Columns ({len(all_columns)}):** {all_columns}\n")

        structured = []
        unstructured = []
        all_env_vars = set()
        all_out_vars = set()
        all_evidence_types = set()
        row_count = 0

        for row in reader:
            row_count += 1
            env = (row.get('environment_variable') or '').strip()
            out = (row.get('outcome_variable') or '').strip()
            ev = (row.get('evidence_basis') or row.get('evidence_type') or '').strip()

            if env:
                all_env_vars.add(env)
            if out:
                all_out_vars.add(out)
            if ev:
                all_evidence_types.add(ev)

            if env and out:
                if len(structured) < 30:
                    structured.append(row)
            else:
                if len(unstructured) < 30:
                    unstructured.append(row)

            # Don't read entire 154MB — sample first 10k rows, count rest
            if row_count >= 10000 and len(structured) >= 30 and len(unstructured) >= 30:
                break

    OUTPUT.append(f"**Rows scanned:** {row_count}")
    OUTPUT.append(f"**Unique environment_variable values found:** {len(all_env_vars)}")
    OUTPUT.append(f"**Unique outcome_variable values found:** {len(all_out_vars)}")
    OUTPUT.append(f"**Unique evidence types found:** {len(all_evidence_types)}")

    subsection("All unique environment_variable values (from first 10k rows)")
    for v in sorted(all_env_vars):
        OUTPUT.append(f"  - `{v}`")

    subsection("All unique outcome_variable values (from first 10k rows)")
    for v in sorted(all_out_vars):
        OUTPUT.append(f"  - `{v}`")

    subsection("All unique evidence types (from first 10k rows)")
    for v in sorted(all_evidence_types):
        OUTPUT.append(f"  - `{v}`")

    subsection("SAMPLE: 20 STRUCTURED rows (environment_variable present)")
    for i, row in enumerate(structured[:20]):
        OUTPUT.append(f"\n**Row {i+1}:**")
        for k, v in row.items():
            val = (v or '').strip()
            if val:
                # Truncate long values
                if len(val) > 300:
                    val = val[:300] + "..."
                OUTPUT.append(f"  {k}: {val}")

    subsection("SAMPLE: 20 UNSTRUCTURED rows (no environment_variable)")
    for i, row in enumerate(unstructured[:20]):
        OUTPUT.append(f"\n**Row {i+1}:**")
        for k, v in row.items():
            val = (v or '').strip()
            if val:
                if len(val) > 300:
                    val = val[:300] + "..."
                OUTPUT.append(f"  {k}: {val}")

# ============================================================
# PART 2: CONSTRAINT / BELIEF / BRIDGE SCHEMAS
# ============================================================
section("PART 2: DATABASE MODEL SCHEMAS")

model_files = (
    glob.glob("src/services/web_persistence.py") +
    glob.glob("src/models/*.py") +
    glob.glob("src/services/models.py") +
    glob.glob("src/**/models.py", recursive=True) +
    glob.glob("src/cmr/models.py")
)

for mf in sorted(set(model_files)):
    if os.path.exists(mf):
        subsection(f"Schema from `{mf}`")
        with open(mf) as f:
            content = f.read()
        # Extract class definitions with their columns
        in_class = False
        class_lines = []
        for line in content.split('\n'):
            if line.strip().startswith('class ') and ('Base' in line or 'Model' in line or 'db.Model' in line):
                if class_lines:
                    OUTPUT.append('\n'.join(class_lines))
                    OUTPUT.append('')
                class_lines = [line]
                in_class = True
            elif in_class:
                if line.strip() and not line[0].isspace() and not line.strip().startswith('#'):
                    in_class = False
                    OUTPUT.append('\n'.join(class_lines))
                    OUTPUT.append('')
                    class_lines = []
                else:
                    # Only keep Column definitions, relationships, and docstrings
                    stripped = line.strip()
                    if any(kw in stripped for kw in ['Column', 'relationship', 'ForeignKey', 
                           '__tablename__', 'class ', '"""', "'''", '# ']):
                        class_lines.append(line)
                    elif 'def ' in stripped:
                        # Skip method bodies but note the method exists
                        class_lines.append(f"    # method: {stripped}")
                        in_class = True  # keep going
        if class_lines:
            OUTPUT.append('\n'.join(class_lines))

# Also check for Belief/Constraint/Bridge specifically
subsection("Grep for Belief/Constraint/Bridge/ReductionClaim definitions")
for pattern in ['Belief', 'Constraint', 'Bridge', 'ReductionClaim', 
                'TemplateRecord', 'CMREvaluation']:
    hits = []
    for root, dirs, files in os.walk('src/'):
        dirs[:] = [d for d in dirs if d != '__pycache__']
        for fn in files:
            if fn.endswith('.py'):
                fpath = os.path.join(root, fn)
                with open(fpath) as f:
                    for i, line in enumerate(f, 1):
                        if f'class {pattern}' in line:
                            hits.append(f"  {fpath}:{i}: {line.strip()}")
    if hits:
        OUTPUT.append(f"\n**{pattern}:**")
        for h in hits:
            OUTPUT.append(h)

# ============================================================
# PART 3: TEMPLATE INPUT/OUTPUT VOCABULARY
# ============================================================
section("PART 3: TEMPLATE INPUT/OUTPUT VOCABULARY")

subsection("Feature-to-template mappings (from src/cmr/)")
for root, dirs, files in os.walk('src/cmr/'):
    dirs[:] = [d for d in dirs if d != '__pycache__']
    for fn in files:
        if fn.endswith('.py'):
            fpath = os.path.join(root, fn)
            with open(fpath) as f:
                content = f.read()
            # Look for dispatch maps, feature mappings, vocabulary
            for marker in ['DISPATCH', 'FEATURE_TO_TEMPLATE', 'TEMPLATE_DISPATCH',
                          'FEATURE_MAP', 'INPUT_MAP', 'VALID_IV', 'VALID_DV',
                          'VARIABLE_VOCAB', 'SYNONYM']:
                if marker in content:
                    OUTPUT.append(f"\n**Found `{marker}` in `{fpath}`**")
                    # Extract the dict/list definition
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if marker in line:
                            # Print surrounding context (up to 60 lines)
                            start = max(0, i)
                            end = min(len(lines), i + 60)
                            for j in range(start, end):
                                OUTPUT.append(f"  {j+1}: {lines[j]}")
                                # Stop if we hit a line that closes the dict at indent 0
                                if j > i and lines[j].strip() and not lines[j][0].isspace() and lines[j].strip() != '}':
                                    break
                            break

subsection("Template JSON sample: first 3 template files")
template_dirs = glob.glob("data/templates/") + glob.glob("data/template*/")
for td in template_dirs:
    if os.path.isdir(td):
        json_files = sorted([f for f in os.listdir(td) if f.endswith('.json')])[:3]
        for jf in json_files:
            jpath = os.path.join(td, jf)
            OUTPUT.append(f"\n**{jpath}:**")
            with open(jpath) as f:
                data = json.load(f)
            # Print structure, not full content
            def summarize(obj, depth=0, max_depth=3):
                indent = "  " * depth
                if depth >= max_depth:
                    return f"{indent}..."
                if isinstance(obj, dict):
                    lines = []
                    for k, v in list(obj.items())[:20]:
                        if isinstance(v, (dict, list)):
                            lines.append(f"{indent}{k}:")
                            lines.append(summarize(v, depth+1, max_depth))
                        else:
                            val_str = str(v)
                            if len(val_str) > 100:
                                val_str = val_str[:100] + "..."
                            lines.append(f"{indent}{k}: {val_str}")
                    return '\n'.join(lines)
                elif isinstance(obj, list):
                    if len(obj) == 0:
                        return f"{indent}[]"
                    lines = [f"{indent}[{len(obj)} items]"]
                    for item in obj[:3]:
                        lines.append(summarize(item, depth+1, max_depth))
                    if len(obj) > 3:
                        lines.append(f"{indent}  ... +{len(obj)-3} more")
                    return '\n'.join(lines)
                else:
                    return f"{indent}{obj}"
            OUTPUT.append(summarize(data))
        break

# ============================================================
# PART 4: WEB OF BELIEF CONTENTS SAMPLE
# ============================================================
section("PART 4: WEB OF BELIEF SAMPLE")

subsection("Attempting to query web of belief for sample beliefs/constraints")
try:
    # Try to import and query
    sys.path.insert(0, '.')
    from src.services.web_persistence import (
        get_or_create_master_web, get_beliefs_for_web, 
        get_constraints_for_web
    )
    web = get_or_create_master_web()
    
    beliefs = get_beliefs_for_web(web.id, limit=10)
    OUTPUT.append(f"\n**Sample beliefs ({len(beliefs)}):**")
    for b in beliefs[:10]:
        OUTPUT.append(f"  {vars(b) if hasattr(b, '__dict__') else str(b)}")
    
    constraints = get_constraints_for_web(limit=10)
    OUTPUT.append(f"\n**Sample constraints ({len(constraints)}):**")
    for c in constraints[:10]:
        OUTPUT.append(f"  {vars(c) if hasattr(c, '__dict__') else str(c)}")
        
except Exception as e:
    OUTPUT.append(f"Could not query web of belief: {e}")
    OUTPUT.append("Falling back to file inspection...")
    
    # Look for SQLite DB
    for db_file in glob.glob("**/*.db", recursive=True) + glob.glob("**/*.sqlite", recursive=True):
        OUTPUT.append(f"\n**Found DB: {db_file}** ({os.path.getsize(db_file)/1e6:.1f} MB)")
        try:
            import sqlite3
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            OUTPUT.append(f"  Tables: {[t[0] for t in tables]}")
            for table_name in [t[0] for t in tables]:
                cursor.execute(f"SELECT COUNT(*) FROM [{table_name}]")
                count = cursor.fetchone()[0]
                cursor.execute(f"PRAGMA table_info([{table_name}])")
                cols = cursor.fetchall()
                OUTPUT.append(f"\n  **{table_name}** ({count} rows)")
                OUTPUT.append(f"  Columns: {[c[1] for c in cols]}")
                if count > 0:
                    cursor.execute(f"SELECT * FROM [{table_name}] LIMIT 3")
                    rows = cursor.fetchall()
                    for row in rows:
                        row_str = str(row)
                        if len(row_str) > 500:
                            row_str = row_str[:500] + "..."
                        OUTPUT.append(f"    {row_str}")
            conn.close()
        except Exception as e2:
            OUTPUT.append(f"  Could not read: {e2}")

# ============================================================
# PART 5: WHAT THE PIPELINE ACTUALLY NEEDS
# ============================================================
section("PART 5: WHAT THE PIPELINE CONSUMES")

subsection("Paper eval claim structure (from src/cmr/)")
for root, dirs, files in os.walk('src/cmr/'):
    dirs[:] = [d for d in dirs if d != '__pycache__']
    for fn in files:
        if fn.endswith('.py'):
            fpath = os.path.join(root, fn)
            with open(fpath) as f:
                content = f.read()
            # Look for structured_claims, extract_claims, claim schema
            for marker in ['structured_claims', 'extract_claims', 'ClaimSchema',
                          'def evaluate_paper', 'def extract_claims', 'def match_claims',
                          'def process_paper']:
                if marker in content:
                    OUTPUT.append(f"\n**Found `{marker}` in `{fpath}`**")
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if marker in line:
                            start = max(0, i - 2)
                            end = min(len(lines), i + 40)
                            for j in range(start, end):
                                OUTPUT.append(f"  {j+1}: {lines[j]}")
                            OUTPUT.append("  ...")
                            break

subsection("Building eval feature structure")
for fpath in glob.glob("src/cmr/building_eval.py"):
    with open(fpath) as f:
        content = f.read()
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'def evaluate_building' in line:
            start = i
            end = min(len(lines), i + 30)
            for j in range(start, end):
                OUTPUT.append(f"  {j+1}: {lines[j]}")
            break

# ============================================================
# OUTPUT
# ============================================================
print('\n'.join(OUTPUT))
