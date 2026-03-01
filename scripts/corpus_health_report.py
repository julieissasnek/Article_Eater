#!/usr/bin/env python3
"""
CORPUS HEALTH REPORT
====================

Generates a comprehensive health report for the Article Eater corpus:
- Template coverage: which templates have supporting papers?
- Domain balance: are any domains under-represented?
- QA cache gaps: which molecules lack L1/L2/L3 summaries?
- Citation density: papers with most/fewest inbound citations
- Bridge warrant distribution

Usage:
    python scripts/corpus_health_report.py

Author: AG (Pipeline Sprint)
Date: 2026-02-25
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from qa_browse.config import (
    DOMAIN_CONFIG,
    BRIDGE_WARRANT_LABELS,
    TEMPLATES_DIR,
    MOLECULES_DIR,
    EXTRACTIONS_DIR,
    QA_CACHE_DIR,
)
from qa_browse.topic_index import TopicIndex


def main():
    idx = TopicIndex()
    stats = idx.get_stats()

    print("=" * 70)
    print("  CORPUS HEALTH REPORT")
    print(f"  Generated: {__import__('datetime').datetime.now()}")
    print("=" * 70)

    # ── 1. Overview ──
    print(f"\n{'─'*60}")
    print("1. OVERVIEW")
    print(f"{'─'*60}")
    print(f"  Templates:         {stats['templates']}")
    print(f"  Molecules:         {stats['molecules']}")
    print(f"  MASTER_DOC sects:  {stats['master_doc_sections']}")
    print(f"  Papers:            {stats['papers']}")
    print(f"  Citation edges:    {stats['citation_edges']}")
    print(f"  QA caches:         {stats['qa_caches']}")
    print(f"  Domains:           {len(stats['domains'])}")
    total_classified = sum(stats['domains'].values())
    print(f"  Classified:        {total_classified}/{stats['templates']} ({100*total_classified//stats['templates']}%)")

    # ── 2. Domain Distribution ──
    print(f"\n{'─'*60}")
    print("2. DOMAIN DISTRIBUTION")
    print(f"{'─'*60}")
    domains = stats['domains']
    total = sum(domains.values())
    avg = total / len(domains) if domains else 0
    for domain, count in sorted(domains.items(), key=lambda x: -x[1]):
        cfg = DOMAIN_CONFIG.get(domain, {})
        emoji = cfg.get("emoji", "")
        bar = "█" * count + "░" * (50 - count)
        print(f"  {emoji} {domain:15s} {count:3d} {bar}")
    print(f"\n  Average: {avg:.1f} per domain, Median: {sorted(domains.values())[len(domains)//2]}")

    # Flag sparse domains
    sparse = {d: c for d, c in domains.items() if c < 5}
    if sparse:
        print(f"\n  ⚠️  SPARSE DOMAINS (<5 templates):")
        for d, c in sorted(sparse.items(), key=lambda x: x[1]):
            print(f"      {d}: {c}")

    # ── 3. Template Coverage ──
    print(f"\n{'─'*60}")
    print("3. TEMPLATE REFERENCE COVERAGE")
    print(f"{'─'*60}")
    ref_counts = defaultdict(int)
    no_refs = []
    few_refs = []

    for tid, t in idx.templates.items():
        if tid != t.display_id:
            continue
        n_refs = len(t.key_references) if t.key_references else 0
        ref_counts[n_refs] += 1
        if n_refs == 0:
            no_refs.append(tid)
        elif n_refs < 3:
            few_refs.append((tid, n_refs))

    print(f"  Reference distribution:")
    for n_ref in sorted(ref_counts.keys()):
        count = ref_counts[n_ref]
        print(f"    {n_ref:2d} refs: {count:3d} templates {'⚠️' if n_ref < 3 else ''}")

    if no_refs:
        print(f"\n  🔴 TEMPLATES WITH NO REFERENCES ({len(no_refs)}):")
        for tid in sorted(no_refs)[:15]:
            t = idx.get_template(tid)
            print(f"      {tid}: {t.name[:50] if t else '?'}")
        if len(no_refs) > 15:
            print(f"      ... and {len(no_refs)-15} more")

    if few_refs:
        print(f"\n  🟡 TEMPLATES WITH <3 REFERENCES ({len(few_refs)}):")
        for tid, n in sorted(few_refs, key=lambda x: x[1])[:10]:
            t = idx.get_template(tid)
            print(f"      {tid}: {n} refs — {t.name[:40] if t else '?'}")

    # ── 4. Bridge Warrant Distribution ──
    print(f"\n{'─'*60}")
    print("4. BRIDGE WARRANT DISTRIBUTION")
    print(f"{'─'*60}")
    bw_counts = Counter()
    bw_missing = 0
    for tid, t in idx.templates.items():
        if tid != t.display_id:
            continue
        if t.bridge_warrant:
            bw_counts[t.bridge_warrant] += 1
        else:
            bw_missing += 1

    for bw, count in sorted(bw_counts.items(), key=lambda x: -x[1]):
        label = BRIDGE_WARRANT_LABELS.get(bw, ("", 0, ""))
        print(f"  {label[0]} {bw:25s} {count:3d}")
    if bw_missing:
        print(f"  ❓ Missing bridge warrant:  {bw_missing}")

    # ── 5. Confidence Distribution ──
    print(f"\n{'─'*60}")
    print("5. CONFIDENCE DISTRIBUTION")
    print(f"{'─'*60}")
    conf_buckets = {"high (≥0.5)": 0, "moderate (0.35-0.5)": 0,
                    "low (0.2-0.35)": 0, "speculative (<0.2)": 0, "missing": 0}
    conf_sum = 0
    conf_n = 0

    for tid, t in idx.templates.items():
        if tid != t.display_id:
            continue
        c = t.confidence
        if c is None or c == 0:
            conf_buckets["missing"] += 1
        elif c >= 0.5:
            conf_buckets["high (≥0.5)"] += 1
            conf_sum += c; conf_n += 1
        elif c >= 0.35:
            conf_buckets["moderate (0.35-0.5)"] += 1
            conf_sum += c; conf_n += 1
        elif c >= 0.2:
            conf_buckets["low (0.2-0.35)"] += 1
            conf_sum += c; conf_n += 1
        else:
            conf_buckets["speculative (<0.2)"] += 1
            conf_sum += c; conf_n += 1

    for label, count in conf_buckets.items():
        print(f"  {label:25s} {count:3d}")
    if conf_n:
        print(f"\n  Mean confidence: {conf_sum/conf_n:.3f}")

    # ── 6. Ceiling Violations ──
    print(f"\n{'─'*60}")
    print("6. CEILING VIOLATIONS (confidence > bridge_prior + 0.05)")
    print(f"{'─'*60}")
    violations = []
    for tid, t in idx.templates.items():
        if tid != t.display_id:
            continue
        if t.confidence and t.bridge_prior and t.confidence > t.bridge_prior + 0.05:
            violations.append((tid, t.confidence, t.bridge_prior, t.bridge_warrant))

    if violations:
        print(f"  🚩 {len(violations)} violations found:")
        for tid, conf, prior, bw in sorted(violations, key=lambda x: x[1]-x[2], reverse=True):
            delta = conf - prior
            print(f"    {tid:25s} conf={conf:.2f} prior={prior:.2f} Δ={delta:+.2f} ({bw})")
    else:
        print("  ✅ No ceiling violations detected!")

    # ── 7. QA Cache Coverage ──
    print(f"\n{'─'*60}")
    print("7. QA CACHE COVERAGE (L1/L2/L3 Summaries)")
    print(f"{'─'*60}")
    all_mols = sorted(idx.molecules.keys())
    cached = sorted(idx.qa_caches.keys())
    missing = [m for m in all_mols if m not in cached]

    print(f"  Cached:  {len(cached)}/{len(all_mols)} molecules")
    for m in cached:
        qa = idx.qa_caches[m]
        levels = []
        if qa.get("l1_summary"): levels.append("L1")
        if qa.get("l2_summary"): levels.append("L2")
        if qa.get("l3_summary"): levels.append("L3")
        print(f"    ✅ {m:35s} [{', '.join(levels)}]")

    if missing:
        print(f"\n  ❌ Missing ({len(missing)}):")
        for m in missing:
            mol = idx.get_molecule(m)
            n_t = len(mol.constituent_templates) if mol else 0
            print(f"    {m:35s} ({n_t} templates)")

    # ── 8. Unclassified Templates ──
    print(f"\n{'─'*60}")
    print("8. UNCLASSIFIED TEMPLATES")
    print(f"{'─'*60}")
    unclassified = []
    for tid, t in idx.templates.items():
        if tid != t.display_id:
            continue
        domain = idx._classify_domain(t.template_id)
        if not domain:
            unclassified.append(tid)

    if unclassified:
        print(f"  {len(unclassified)} templates without domain assignment:")
        for tid in sorted(unclassified):
            t = idx.get_template(tid)
            print(f"    {tid:35s} {t.name[:40] if t else '?'}")
    else:
        print("  ✅ All templates have domain assignments!")

    # ── 9. Top Papers by Citation ──
    print(f"\n{'─'*60}")
    print("9. TOP 10 PAPERS BY CITATION COUNT")
    print(f"{'─'*60}")
    sorted_papers = sorted(
        idx.paper_index.items(),
        key=lambda x: x[1].get("citation_count") or 0,
        reverse=True
    )
    for doi, p in sorted_papers[:10]:
        cites = p.get("citation_count") or 0
        title = p.get("title", "")[:55]
        year = p.get("year", "?")
        print(f"  {cites:6,d} cites | {year} | {title}")

    print(f"\n{'='*70}")
    print("  END OF REPORT")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
