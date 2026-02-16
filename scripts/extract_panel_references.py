#!/usr/bin/env python3
"""
Master Reference Inventory Builder (Doc 43)

Extracts APA references from all panel documents, deduplicates by
first_author + year + title_keyword, and outputs a consolidated JSON.

Usage: python3 scripts/extract_panel_references.py
Output: docs/43_Master_Reference_Inventory.json
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Optional

# Panel documents to process
PANEL_FILES = [
    # Cognitive/Neuroscience panels
    "02-15_14_Panel_IV_Cognitive_Control_Reward_V1_0.md",
    "02-15_18_Panel_D1_ReductionClaim_Architecture_V1_0.md",
    "02-15_19_Panel_D1b_Neuroscience_Validation_V1_0.md",
    "02-15_20_Panel_V_Social_Brain_V1_0.md",
    "02-15_21_Panel_T2A_ART_Reduction_V1_0.md",
    "02-15_22_Panel_T2B_SRT_Reduction_V1_0.md",
    "02-15_23_Panel_T2C_Biophilia_Reduction_V1_0.md",
    "02-15_25_Panel_VI_Gap_Closure_V1_0.md",
    "02-15_27_Panel_EI_Memory_Encoding_V1_0.md",
    # Music panels
    "28_Panel_MI_Auditory_Predictive_Processing_V1_0.md",
    "29_Panel_MII_Rhythm_Groove_Motor_V1_0.md",
    "30_Panel_MIII_Musical_Emotion_Mechanisms_V1_0.md",
    # Dual Index
    "33_Dual_Index_Cross_Reference_Layer_V1_0.md",
    # Attribute-domain panels
    "34_Panel_LI_Light_Luminance.md",
    "37_Panel_MAT_I_Materials.md",
    "38_Panel_SC_I_Spatial_Config.md",
    "39_Panel_VF_I_Visual_Form.md",
    "42_Panel_TP_I_Temporal.md",
]

# Map filenames to doc numbers for citing_panels field
DOC_NUMBER_MAP = {
    "02-15_14_Panel_IV": "14",
    "02-15_18_Panel_D1_Reduction": "18",
    "02-15_19_Panel_D1b": "19",
    "02-15_20_Panel_V": "20",
    "02-15_21_Panel_T2A": "T2A",
    "02-15_22_Panel_T2B": "T2B",
    "02-15_23_Panel_T2C": "T2C",
    "02-15_25_Panel_VI": "25",
    "02-15_27_Panel_EI": "27",
    "28_Panel_MI": "28",
    "29_Panel_MII": "29",
    "30_Panel_MIII": "30",
    "33_Dual_Index": "33",
    "34_Panel_LI": "34",
    "37_Panel_MAT": "37",
    "38_Panel_SC": "38",
    "39_Panel_VF": "39",
    "42_Panel_TP": "42",
}

def get_doc_number(filename: str) -> str:
    """Extract doc number from filename."""
    for prefix, doc_num in DOC_NUMBER_MAP.items():
        if filename.startswith(prefix):
            return doc_num
    return filename.split("_")[0]

def extract_year(citation: str) -> Optional[str]:
    """Extract year from APA citation."""
    # Match patterns like (2007), (1984), (2013), (1971/2011)
    year_match = re.search(r'\((\d{4})(?:/\d{4})?\)', citation)
    if year_match:
        return year_match.group(1)
    # Try without parentheses
    year_match = re.search(r'\b(19\d{2}|20\d{2})\b', citation)
    if year_match:
        return year_match.group(1)
    return None

def extract_first_author(citation: str) -> Optional[str]:
    """Extract first author's last name from APA citation."""
    # Handle various formats:
    # "Smith, J." -> "Smith"
    # "Smith, J., & Jones" -> "Smith"
    # "Smith et al." -> "Smith"

    # Remove leading bullet points, numbers, dashes
    citation = re.sub(r'^[\s\-\*\d\.]+', '', citation)

    # Match first word that looks like a name (starts with capital, may have hyphen)
    name_match = re.match(r'^([A-Z][a-zA-Z\-\']+)', citation)
    if name_match:
        return name_match.group(1)
    return None

def extract_title_keyword(citation: str) -> Optional[str]:
    """Extract first significant title word for deduplication."""
    # Look for title after year
    title_match = re.search(r'\(\d{4}[a-z]?\)\.\s*([^\.]+)', citation)
    if title_match:
        title = title_match.group(1)
        # Get first significant word (skip articles)
        words = title.split()
        skip_words = {'the', 'a', 'an', 'of', 'in', 'on', 'for', 'to', 'and'}
        for word in words:
            clean_word = re.sub(r'[^\w]', '', word.lower())
            if clean_word and clean_word not in skip_words:
                return clean_word
    return None

def extract_google_scholar_count(citation: str) -> Optional[int]:
    """Extract Google Scholar citation count if present."""
    # Match patterns like "~1,500 citations", "[~500 citations]", "3000 citations"
    count_match = re.search(r'[\[\(~]*(\d{1,2}),?(\d{3})[\s]*citations?', citation, re.IGNORECASE)
    if count_match:
        return int(count_match.group(1)) * 1000 + int(count_match.group(2))
    count_match = re.search(r'[\[\(~]*(\d+)[\s]*citations?', citation, re.IGNORECASE)
    if count_match:
        return int(count_match.group(1))
    return None

def extract_references_from_file(filepath: Path, doc_number: str) -> List[Dict]:
    """Extract all references from a panel markdown file."""
    references = []

    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception as e:
        print(f"  Warning: Could not read {filepath}: {e}")
        return []

    # Find references section
    ref_section_patterns = [
        r'##\s*References\s*\n(.*?)(?=\n##|\Z)',
        r'##\s*Key References\s*\n(.*?)(?=\n##|\Z)',
        r'\*\*References\*\*\s*\n(.*?)(?=\n\*\*|\Z)',
        r'key_references:\s*\n(.*?)(?=\n[a-z_]+:|\Z)',
    ]

    ref_sections = []
    for pattern in ref_section_patterns:
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
        ref_sections.extend(matches)

    # Also look for inline citations in yaml blocks
    yaml_refs = re.findall(r'citation:\s*["\']?([^"\'}\n]+)["\']?', content)

    # Parse reference lines
    all_ref_lines = []

    for section in ref_sections:
        # Split into lines and filter
        lines = section.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Skip headers and formatting
            if line.startswith('#') or line.startswith('|') or line.startswith('---'):
                continue
            # Look for citation-like lines
            if re.search(r'\(\d{4}\)', line) or re.search(r'\d{4}[a-z]?\)', line):
                all_ref_lines.append(line)

    # Add yaml references
    all_ref_lines.extend(yaml_refs)

    # Find which templates cite each reference
    template_patterns = re.findall(r'(?:template_id|display_id)["\s:=]+["\']?([A-Z]+\d*)["\']?', content, re.IGNORECASE)
    current_templates = list(set(template_patterns))

    # Parse each reference
    for ref_line in all_ref_lines:
        # Clean up the line
        ref_line = re.sub(r'^[\s\-\*\d\.]+', '', ref_line)
        ref_line = re.sub(r'\s+', ' ', ref_line).strip()

        if len(ref_line) < 20:  # Too short to be a real reference
            continue

        first_author = extract_first_author(ref_line)
        year = extract_year(ref_line)
        title_keyword = extract_title_keyword(ref_line)
        gs_count = extract_google_scholar_count(ref_line)

        if first_author and year:
            # Clean citation text (remove citation count for cleaner storage)
            clean_citation = re.sub(r'\s*[\[\(]?~?\d+,?\d*\s*citations?\]?\)?\.?$', '', ref_line, flags=re.IGNORECASE)
            clean_citation = clean_citation.strip().rstrip('.')

            references.append({
                'citation_apa': clean_citation,
                'first_author': first_author,
                'year': year,
                'title_keyword': title_keyword,
                'google_scholar_count': gs_count,
                'citing_panel': doc_number,
                'citing_templates': current_templates,
            })

    return references

def generate_dedup_key(ref: Dict) -> str:
    """Generate deduplication key from first_author + year + title_keyword."""
    author = (ref.get('first_author') or '').lower()
    year = ref.get('year') or ''
    title = (ref.get('title_keyword') or '').lower()
    return f"{author}_{year}_{title}"

def merge_references(refs: List[Dict]) -> Dict:
    """Merge multiple references with the same dedup key."""
    merged = {
        'citation_apa': '',
        'first_author': '',
        'year': '',
        'google_scholar_count': None,
        'citing_panels': set(),
        'citing_templates': set(),
    }

    # Take the most complete citation
    longest_citation = ''
    for ref in refs:
        if len(ref.get('citation_apa', '')) > len(longest_citation):
            longest_citation = ref['citation_apa']
            merged['citation_apa'] = longest_citation
            merged['first_author'] = ref.get('first_author', '')
            merged['year'] = ref.get('year', '')

        # Take highest Google Scholar count
        gs_count = ref.get('google_scholar_count')
        if gs_count and (merged['google_scholar_count'] is None or gs_count > merged['google_scholar_count']):
            merged['google_scholar_count'] = gs_count

        # Collect all citing panels and templates
        if ref.get('citing_panel'):
            merged['citing_panels'].add(ref['citing_panel'])
        if ref.get('citing_templates'):
            merged['citing_templates'].update(ref['citing_templates'])

    # Convert sets to sorted lists
    merged['citing_panels'] = sorted(merged['citing_panels'])
    merged['citing_templates'] = sorted(merged['citing_templates'])

    return merged

def main():
    docs_dir = Path(__file__).parent.parent / "docs"
    output_file = docs_dir / "43_Master_Reference_Inventory.json"

    print("=" * 60)
    print("Master Reference Inventory Builder (Doc 43)")
    print("=" * 60)

    # Collect all references
    all_refs = []
    panels_processed = []

    for panel_file in PANEL_FILES:
        filepath = docs_dir / panel_file
        if not filepath.exists():
            # Try in panels subdirectory
            filepath = docs_dir / "panels" / panel_file

        if not filepath.exists():
            print(f"  [SKIP] {panel_file} - not found")
            continue

        doc_num = get_doc_number(panel_file)
        refs = extract_references_from_file(filepath, doc_num)
        all_refs.extend(refs)
        panels_processed.append(panel_file)
        print(f"  [OK] {panel_file} - {len(refs)} references")

    print(f"\nTotal raw references extracted: {len(all_refs)}")

    # Deduplicate
    dedup_groups = defaultdict(list)
    for ref in all_refs:
        key = generate_dedup_key(ref)
        dedup_groups[key].append(ref)

    # Merge and build final list
    final_refs = []
    near_duplicates = []

    for key, group in dedup_groups.items():
        merged = merge_references(group)

        # Flag near-duplicates (same author+year but different title keywords)
        if len(group) > 1:
            variants = set(ref.get('citation_apa', '')[:100] for ref in group)
            if len(variants) > 1:
                near_duplicates.append({
                    'key': key,
                    'count': len(group),
                    'variants': list(variants)[:3]  # Keep first 3 variants
                })

        final_refs.append(merged)

    # Sort by first author, then year
    final_refs.sort(key=lambda x: (x.get('first_author', '').lower(), x.get('year', '')))

    # Assign ref_ids
    for i, ref in enumerate(final_refs, 1):
        ref['ref_id'] = f"REF_{i:03d}"
        ref['pdf_status'] = "not_acquired"
        ref['doi'] = ""

    # Build output
    output = {
        'metadata': {
            'generated': '2026-02-16',
            'total_references': len(final_refs),
            'panels_processed': panels_processed,
            'near_duplicates_flagged': len(near_duplicates),
        },
        'near_duplicates': near_duplicates,
        'references': final_refs,
    }

    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"\nDeduplication complete:")
    print(f"  - Unique references: {len(final_refs)}")
    print(f"  - Near-duplicates flagged: {len(near_duplicates)}")
    print(f"\nOutput written to: {output_file}")

    # Summary stats
    print("\n" + "=" * 60)
    print("Reference Statistics")
    print("=" * 60)

    # Top cited
    refs_with_counts = [r for r in final_refs if r.get('google_scholar_count')]
    refs_with_counts.sort(key=lambda x: x.get('google_scholar_count', 0), reverse=True)
    print("\nTop 10 by Google Scholar citations:")
    for ref in refs_with_counts[:10]:
        print(f"  {ref['google_scholar_count']:,} - {ref['first_author']} ({ref['year']})")

    # Most cross-referenced
    multi_panel_refs = [r for r in final_refs if len(r.get('citing_panels', [])) > 1]
    multi_panel_refs.sort(key=lambda x: len(x.get('citing_panels', [])), reverse=True)
    print(f"\nReferences cited in multiple panels: {len(multi_panel_refs)}")
    for ref in multi_panel_refs[:10]:
        print(f"  {len(ref['citing_panels'])} panels - {ref['first_author']} ({ref['year']}): {ref['citing_panels']}")

if __name__ == "__main__":
    main()
