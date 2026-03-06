#!/usr/bin/env python3
"""
compare_extractions.py — Gold Standard Comparison Framework

Compares automated extraction results (e.g., Gemini pipeline) against
gold standard extractions (e.g., Claude Opus manual extraction) to
evaluate extraction quality.

Scoring dimensions:
  1. Classification accuracy — Did the pipeline get the article type right?
  2. Finding recall — How many gold standard findings were captured?
  3. Finding precision — How many pipeline findings are real (not hallucinated)?
  4. Field completeness — For matched findings, what % of fields are filled?
  5. Field accuracy — For matched findings with filled fields, what % match?
  6. Statistical precision — Are p-values, effect sizes, test stats correct?

Usage:
  python3 scripts/compare_extractions.py \
      --gold data/gold_standard/ \
      --pipeline data/v4_pilot/ \
      [--output data/comparison_report.json]

Author: Article Eater QA
Date: 2026-03-05
"""

import json
import argparse
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


# ── Finding Matching ────────────────────────────────────────────────────

def normalize_text(s: str) -> str:
    """Lowercase, strip whitespace, remove punctuation for fuzzy matching."""
    if not s:
        return ""
    import re
    return re.sub(r'[^\w\s]', '', s.lower().strip())


def finding_similarity(gold_finding: dict, pipe_finding: dict) -> float:
    """
    Score how similar two findings are (0.0 to 1.0).
    Uses antecedent + consequent + direction matching.
    """
    score = 0.0
    weights = 0.0

    # Antecedent overlap (word-level Jaccard)
    ga = set(normalize_text(str(gold_finding.get('antecedent', ''))).split())
    pa = set(normalize_text(str(pipe_finding.get('antecedent', ''))).split())
    if ga and pa:
        jaccard_a = len(ga & pa) / len(ga | pa)
        score += 0.4 * jaccard_a
    weights += 0.4

    # Consequent overlap
    gc = set(normalize_text(str(gold_finding.get('consequent', ''))).split())
    pc = set(normalize_text(str(pipe_finding.get('consequent', ''))).split())
    if gc and pc:
        jaccard_c = len(gc & pc) / len(gc | pc)
        score += 0.4 * jaccard_c
    weights += 0.4

    # Direction match
    gd = str(gold_finding.get('direction', '')).lower()
    pd = str(pipe_finding.get('direction', '')).lower()
    if gd and pd:
        score += 0.2 * (1.0 if gd == pd else 0.0)
    weights += 0.2

    return score / weights if weights > 0 else 0.0


def match_findings(gold_findings: list, pipe_findings: list, threshold: float = 0.3) -> list:
    """
    Match pipeline findings to gold standard findings using greedy best-match.
    Returns list of (gold_idx, pipe_idx, similarity_score) tuples.
    Unmatched gold findings → (gold_idx, None, 0.0)
    Unmatched pipe findings → (None, pipe_idx, 0.0)
    """
    n_gold = len(gold_findings)
    n_pipe = len(pipe_findings)

    # Compute similarity matrix
    sim_matrix = []
    for gi in range(n_gold):
        for pi in range(n_pipe):
            sim = finding_similarity(gold_findings[gi], pipe_findings[pi])
            if sim >= threshold:
                sim_matrix.append((sim, gi, pi))

    # Greedy matching (highest similarity first)
    sim_matrix.sort(reverse=True)
    matched_gold = set()
    matched_pipe = set()
    matches = []

    for sim, gi, pi in sim_matrix:
        if gi not in matched_gold and pi not in matched_pipe:
            matches.append((gi, pi, sim))
            matched_gold.add(gi)
            matched_pipe.add(pi)

    # Unmatched gold (missed findings = recall failures)
    for gi in range(n_gold):
        if gi not in matched_gold:
            matches.append((gi, None, 0.0))

    # Unmatched pipe (hallucinated or extra findings)
    for pi in range(n_pipe):
        if pi not in matched_pipe:
            matches.append((None, pi, 0.0))

    return matches


# ── Field Comparison ────────────────────────────────────────────────────

CRITICAL_FIELDS = ['antecedent', 'consequent', 'direction', 'claim_type', 'statement']
STAT_FIELDS = ['p_value', 'effect_size', 'effect_size_type', 'test_statistic']
CONTEXT_FIELDS = ['sample_size', 'measure_type', 'causal_tier', 'source_zone']
ALL_COMPARED_FIELDS = CRITICAL_FIELDS + STAT_FIELDS + CONTEXT_FIELDS


def compare_field(gold_val, pipe_val, field_name: str) -> dict:
    """Compare a single field between gold and pipeline."""
    result = {
        'field': field_name,
        'gold': gold_val,
        'pipeline': pipe_val,
        'gold_present': gold_val is not None,
        'pipe_present': pipe_val is not None,
        'match': False,
        'category': 'missing'
    }

    if gold_val is None and pipe_val is None:
        result['match'] = True
        result['category'] = 'both_null'
        return result

    if gold_val is None and pipe_val is not None:
        result['category'] = 'pipeline_extra'
        return result

    if gold_val is not None and pipe_val is None:
        result['category'] = 'pipeline_missing'
        return result

    # Both present — compare
    # Numeric comparison (with tolerance)
    if field_name in ('p_value', 'effect_size'):
        try:
            g = float(gold_val) if not isinstance(gold_val, (int, float)) else gold_val
            p = float(pipe_val) if not isinstance(pipe_val, (int, float)) else pipe_val
            # 10% tolerance or 0.01 absolute
            if abs(g - p) <= max(0.01, abs(g) * 0.10):
                result['match'] = True
                result['category'] = 'match_numeric'
            else:
                result['category'] = 'mismatch_numeric'
            return result
        except (ValueError, TypeError):
            pass

    # String comparison (normalized)
    g_str = normalize_text(str(gold_val))
    p_str = normalize_text(str(pipe_val))

    if g_str == p_str:
        result['match'] = True
        result['category'] = 'match_exact'
    elif g_str in p_str or p_str in g_str:
        result['match'] = True
        result['category'] = 'match_substring'
    else:
        # Word overlap
        g_words = set(g_str.split())
        p_words = set(p_str.split())
        if g_words and p_words:
            overlap = len(g_words & p_words) / len(g_words | p_words)
            if overlap > 0.5:
                result['match'] = True
                result['category'] = 'match_fuzzy'
            else:
                result['category'] = 'mismatch'
        else:
            result['category'] = 'mismatch'

    return result


def compare_findings(gold_finding: dict, pipe_finding: dict) -> dict:
    """Compare all fields between a matched pair of findings."""
    comparisons = {}
    for field in ALL_COMPARED_FIELDS:
        comparisons[field] = compare_field(
            gold_finding.get(field),
            pipe_finding.get(field),
            field
        )
    return comparisons


# ── Paper-Level Comparison ──────────────────────────────────────────────

def compare_paper(gold_path: Path, pipe_data: dict) -> dict:
    """Compare a single paper's extraction against gold standard."""
    with open(gold_path) as f:
        gold = json.load(f)

    doi = gold.get('doi', 'unknown')
    gold_type = gold.get('article_type', 'unknown')
    pipe_type = pipe_data.get('article_type', pipe_data.get('classification', {}).get('article_type', 'unknown'))

    gold_findings = gold.get('findings', [])
    pipe_findings = pipe_data.get('findings', [])

    # 1. Classification accuracy
    type_match = normalize_text(gold_type) == normalize_text(str(pipe_type))

    # 2. Match findings
    matches = match_findings(gold_findings, pipe_findings)

    matched_pairs = [(gi, pi, sim) for gi, pi, sim in matches if gi is not None and pi is not None]
    missed_gold = [(gi, pi, sim) for gi, pi, sim in matches if pi is None]
    extra_pipe = [(gi, pi, sim) for gi, pi, sim in matches if gi is None]

    recall = len(matched_pairs) / max(len(gold_findings), 1)
    precision = len(matched_pairs) / max(len(pipe_findings), 1) if pipe_findings else 0.0
    f1 = 2 * recall * precision / max(recall + precision, 0.001)

    # 3. Field-level analysis for matched pairs
    field_comparisons = []
    for gi, pi, sim in matched_pairs:
        fc = compare_findings(gold_findings[gi], pipe_findings[pi])
        fc['_match_similarity'] = sim
        fc['_gold_id'] = gold_findings[gi].get('id', f'G{gi}')
        fc['_pipe_id'] = pipe_findings[pi].get('id', f'P{pi}')
        field_comparisons.append(fc)

    # Aggregate field accuracy
    field_stats = {}
    for field in ALL_COMPARED_FIELDS:
        matches_for_field = [fc[field] for fc in field_comparisons if field in fc]
        n_compared = len([m for m in matches_for_field if m['gold_present']])
        n_matched = len([m for m in matches_for_field if m['match'] and m['gold_present']])
        n_pipe_present = len([m for m in matches_for_field if m['pipe_present']])
        field_stats[field] = {
            'gold_present': n_compared,
            'pipe_present': n_pipe_present,
            'matched': n_matched,
            'accuracy': n_matched / max(n_compared, 1),
            'completeness': n_pipe_present / max(n_compared, 1) if n_compared > 0 else None
        }

    # 4. Stat precision
    stat_correct = sum(field_stats[f]['matched'] for f in STAT_FIELDS)
    stat_total = sum(field_stats[f]['gold_present'] for f in STAT_FIELDS)

    return {
        'doi': doi,
        'gold_article_type': gold_type,
        'pipe_article_type': pipe_type,
        'classification_correct': type_match,
        'gold_n_findings': len(gold_findings),
        'pipe_n_findings': len(pipe_findings),
        'matched_findings': len(matched_pairs),
        'missed_findings': len(missed_gold),
        'extra_findings': len(extra_pipe),
        'recall': round(recall, 3),
        'precision': round(precision, 3),
        'f1': round(f1, 3),
        'stat_accuracy': round(stat_correct / max(stat_total, 1), 3),
        'field_stats': field_stats,
        'matched_details': [
            {
                'gold_id': gold_findings[gi].get('id', f'G{gi}'),
                'pipe_id': pipe_findings[pi].get('id', f'P{pi}'),
                'similarity': round(sim, 3),
                'gold_antecedent': str(gold_findings[gi].get('antecedent', ''))[:80],
                'pipe_antecedent': str(pipe_findings[pi].get('antecedent', ''))[:80],
            }
            for gi, pi, sim in matched_pairs
        ],
        'missed_details': [
            {
                'gold_id': gold_findings[gi].get('id', f'G{gi}'),
                'antecedent': str(gold_findings[gi].get('antecedent', ''))[:80],
                'consequent': str(gold_findings[gi].get('consequent', ''))[:80],
            }
            for gi, _, _ in missed_gold
        ]
    }


# ── Main ────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Compare extractions against gold standard")
    parser.add_argument('--gold', required=True, help='Directory with gold standard JSONs')
    parser.add_argument('--pipeline', required=True, help='Directory with pipeline results OR single JSON')
    parser.add_argument('--output', default=None, help='Output comparison report JSON')
    args = parser.parse_args()

    gold_dir = Path(args.gold)
    pipe_path = Path(args.pipeline)

    # Load gold standard files
    gold_files = sorted(gold_dir.glob("paper*.json"))
    if not gold_files:
        print("ERROR: No gold standard files found in", gold_dir)
        sys.exit(1)

    # Load pipeline results
    pipe_results = {}
    if pipe_path.is_file():
        with open(pipe_path) as f:
            pipe_data = json.load(f)
        # Could be a single extraction or a batch result
        if 'results' in pipe_data:
            for r in pipe_data['results']:
                if r.get('status') != 'failed' and 'findings' in r:
                    pipe_results[r['doi']] = r
        elif 'doi' in pipe_data:
            pipe_results[pipe_data['doi']] = pipe_data
    elif pipe_path.is_dir():
        for f in pipe_path.glob("*.json"):
            try:
                with open(f) as fh:
                    d = json.load(fh)
                if 'results' in d:
                    for r in d['results']:
                        if r.get('findings'):
                            pipe_results[r['doi']] = r
                elif d.get('doi') and d.get('findings'):
                    pipe_results[d['doi']] = d
            except (json.JSONDecodeError, KeyError):
                continue

    print(f"Gold standard: {len(gold_files)} papers")
    print(f"Pipeline results: {len(pipe_results)} papers with findings")
    print()

    # Compare each gold standard paper
    comparisons = []
    for gf in gold_files:
        with open(gf) as f:
            gold = json.load(f)
        doi = gold.get('doi', '')

        if doi in pipe_results:
            comp = compare_paper(gf, pipe_results[doi])
            comparisons.append(comp)
            status = "COMPARED"
        else:
            # Pipeline has no result for this paper
            comparisons.append({
                'doi': doi,
                'gold_article_type': gold.get('article_type', '?'),
                'pipe_article_type': None,
                'classification_correct': False,
                'gold_n_findings': len(gold.get('findings', [])),
                'pipe_n_findings': 0,
                'matched_findings': 0,
                'missed_findings': len(gold.get('findings', [])),
                'extra_findings': 0,
                'recall': 0.0,
                'precision': 0.0,
                'f1': 0.0,
                'stat_accuracy': 0.0,
                'status': 'pipeline_missing'
            })
            status = "MISSING FROM PIPELINE"

        print(f"  {doi}: {status}")

    # Summary
    print()
    print("=" * 70)
    print("COMPARISON SUMMARY")
    print("=" * 70)

    n_papers = len(comparisons)
    n_classified = sum(1 for c in comparisons if c.get('classification_correct'))
    avg_recall = sum(c['recall'] for c in comparisons) / max(n_papers, 1)
    avg_precision = sum(c['precision'] for c in comparisons) / max(n_papers, 1)
    avg_f1 = sum(c['f1'] for c in comparisons) / max(n_papers, 1)
    total_gold = sum(c['gold_n_findings'] for c in comparisons)
    total_matched = sum(c['matched_findings'] for c in comparisons)
    total_missed = sum(c['missed_findings'] for c in comparisons)

    print(f"  Papers compared:        {n_papers}")
    print(f"  Classification correct: {n_classified}/{n_papers} ({100*n_classified//max(n_papers,1)}%)")
    print(f"  Total gold findings:    {total_gold}")
    print(f"  Total matched:          {total_matched}")
    print(f"  Total missed:           {total_missed}")
    print(f"  Avg recall:             {avg_recall:.1%}")
    print(f"  Avg precision:          {avg_precision:.1%}")
    print(f"  Avg F1:                 {avg_f1:.1%}")
    print()

    for c in comparisons:
        doi_short = c['doi'][-30:]
        print(f"  {doi_short:30s}  Recall={c['recall']:.0%}  Prec={c['precision']:.0%}  "
              f"F1={c['f1']:.0%}  Gold={c['gold_n_findings']}  Pipe={c['pipe_n_findings']}")

    # Save report
    report = {
        'timestamp': datetime.now().isoformat(),
        'gold_standard_dir': str(gold_dir),
        'pipeline_dir': str(pipe_path),
        'summary': {
            'n_papers': n_papers,
            'classification_accuracy': n_classified / max(n_papers, 1),
            'avg_recall': round(avg_recall, 3),
            'avg_precision': round(avg_precision, 3),
            'avg_f1': round(avg_f1, 3),
            'total_gold_findings': total_gold,
            'total_matched_findings': total_matched,
            'total_missed_findings': total_missed,
        },
        'papers': comparisons
    }

    output_path = args.output or str(gold_dir / "comparison_report.json")
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    print(f"\n  Report saved: {output_path}")


if __name__ == '__main__':
    main()
