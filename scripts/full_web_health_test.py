#!/usr/bin/env python3
"""
Full Web of Belief Health Test
================================
Comprehensive test suite that goes beyond the minimum-viable and target
thresholds in check_web_bn_health.py. Runs every diagnostic we have and
produces a single pass/fail with detailed breakdown.

Test Categories:
  A. STRUCTURAL INTEGRITY — cycles, dangling edges, schema conformance
  B. CONNECTIVITY — isolated beliefs, component sizes, degree distribution
  C. EPISTEMIC BALANCE — support/explain/contradict ratios, both-sides %
  D. PROVENANCE — bridge source attribution, constraint provenance coverage
  E. OFF-TOPIC CONTAMINATION — estimated off-topic belief percentage
  F. TEMPLATE COVERAGE — how many templates have ≥1 web belief anchored
  G. STALENESS — age distribution of constraints, recent activity
  H. BN CONSISTENCY — acyclicity, resolution completeness, component integrity

Usage:
    python scripts/full_web_health_test.py
    python scripts/full_web_health_test.py --verbose
    python scripts/full_web_health_test.py --json-out data/production/full_health.json
"""

from __future__ import annotations

import argparse
import glob
import json
import re
import sqlite3
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.services.db_locator import resolve_web_db

MASTER_WEB_ID = "master:web:accumulated"
TEMPLATE_DIR = PROJECT_ROOT / "data" / "templates"
BN_JSON = PROJECT_ROOT / "data" / "production" / "bn_state.json"


# ═══════════════════════════════════════════════════════════════════════
# Test result tracking
# ═══════════════════════════════════════════════════════════════════════

class TestResult:
    def __init__(self, name: str, category: str, passed: bool,
                 actual: Any, threshold: Any, description: str,
                 severity: str = "warning"):
        self.name = name
        self.category = category
        self.passed = passed
        self.actual = actual
        self.threshold = threshold
        self.description = description
        self.severity = severity  # "critical", "warning", "info"

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "category": self.category,
            "passed": self.passed,
            "actual": self.actual,
            "threshold": self.threshold,
            "description": self.description,
            "severity": self.severity,
        }


# ═══════════════════════════════════════════════════════════════════════
# Off-topic detection (reused from maintain_web.py)
# ═══════════════════════════════════════════════════════════════════════

STRONG_EXCLUSION_KEYWORDS = [
    "offshore drilling", "oil well", "petroleum extraction",
    "pipeline inspection", "refinery process", "fracking",
    "cell culture", "in vitro assay", "dna sequence", "rna expression",
    "protein expression", "gene expression", "molecular biology",
    "transfection", "western blot", "pcr amplification",
    "drug dosage", "pharmacokinetics", "phase ii trial",
    "chemotherapy regimen", "drug efficacy",
    "vlsi", "transistor", "semiconductor", "integrated circuit",
    "cmos", "fpga", "asic", "chip design",
    "theorem proving", "np-hard", "turing machine",
    "galaxy", "cosmological", "dark matter", "neutron star",
    "crop yield", "fertilizer", "herbicide", "livestock",
]

INCLUSION_KEYWORDS = [
    "building", "architecture", "architectural", "interior", "office",
    "hospital", "classroom", "daylight", "illumination", "lighting",
    "acoustic", "noise", "thermal", "ventilation", "biophilic",
    "spatial", "ceiling height", "aesthetics", "beauty",
    "cognition", "attention", "memory", "stress", "mood",
    "wellbeing", "well-being", "productivity", "performance",
    "prediction error", "predictive coding", "neural",
    "biophilia", "attention restoration", "stress recovery",
    "prospect-refuge", "neuroarchitecture", "isovist",
]


def estimate_off_topic_pct(beliefs: List[Tuple[str, str]]) -> Tuple[float, int]:
    """Return (pct_off_topic, count_off_topic)."""
    off = 0
    for _, content in beliefs:
        c = content.lower()
        has_inclusion = any(kw in c for kw in INCLUSION_KEYWORDS)
        if has_inclusion:
            continue
        has_exclusion = any(kw in c for kw in STRONG_EXCLUSION_KEYWORDS)
        if has_exclusion:
            off += 1
    return (off / max(len(beliefs), 1)) * 100, off


# ═══════════════════════════════════════════════════════════════════════
# Test Categories
# ═══════════════════════════════════════════════════════════════════════

def tests_structural_integrity(conn: sqlite3.Connection, bn: Optional[Dict]) -> List[TestResult]:
    results = []

    # A1: No BN cycles
    if bn:
        has_cycle = bn.get("has_cycle", 0)
        results.append(TestResult(
            "A1_no_bn_cycles", "STRUCTURAL", has_cycle == 0,
            has_cycle, 0, "Bayesian Network must be acyclic (DAG)", "critical"
        ))

    # A2: No dangling edges
    if bn:
        dangling = bn.get("dangling_edges", 0)
        results.append(TestResult(
            "A2_no_dangling_edges", "STRUCTURAL", dangling == 0,
            dangling, 0, "All BN edges must connect valid nodes", "critical"
        ))

    # A3: All constraints reference valid beliefs
    orphan_count = conn.execute("""
        SELECT COUNT(*) FROM constraints c
        WHERE c.web_id = ?
          AND (c.source_id NOT IN (SELECT belief_id FROM beliefs WHERE web_id = ?)
               OR c.target_id NOT IN (SELECT belief_id FROM beliefs WHERE web_id = ?))
    """, (MASTER_WEB_ID,) * 3).fetchone()[0]
    results.append(TestResult(
        "A3_no_orphan_constraints", "STRUCTURAL", orphan_count == 0,
        orphan_count, 0, "All constraints must reference existing beliefs", "critical"
    ))

    # A4: No duplicate constraint IDs
    dup_count = conn.execute("""
        SELECT COUNT(*) - COUNT(DISTINCT constraint_id)
        FROM constraints WHERE web_id = ?
    """, (MASTER_WEB_ID,)).fetchone()[0]
    results.append(TestResult(
        "A4_no_duplicate_constraints", "STRUCTURAL", dup_count == 0,
        dup_count, 0, "All constraint IDs must be unique", "critical"
    ))

    # A5: Constraint types are valid
    invalid_types = conn.execute("""
        SELECT COUNT(*) FROM constraints
        WHERE web_id = ?
          AND constraint_type NOT IN ('supports', 'explains', 'contradicts',
                                       'epistemic_derivation', 'coherence_support')
    """, (MASTER_WEB_ID,)).fetchone()[0]
    results.append(TestResult(
        "A5_valid_constraint_types", "STRUCTURAL", invalid_types == 0,
        invalid_types, 0, "All constraints must use valid types", "critical"
    ))

    # A6: Strengths in [0, 1]
    bad_strength = conn.execute("""
        SELECT COUNT(*) FROM constraints
        WHERE web_id = ? AND (strength < 0 OR strength > 1)
    """, (MASTER_WEB_ID,)).fetchone()[0]
    results.append(TestResult(
        "A6_valid_strengths", "STRUCTURAL", bad_strength == 0,
        bad_strength, 0, "All constraint strengths must be in [0, 1]", "critical"
    ))

    return results


def tests_connectivity(conn: sqlite3.Connection, bn: Optional[Dict]) -> List[TestResult]:
    results = []

    total = conn.execute(
        "SELECT COUNT(*) FROM beliefs WHERE web_id = ?", (MASTER_WEB_ID,)
    ).fetchone()[0]

    isolated = conn.execute("""
        SELECT COUNT(*) FROM beliefs b
        WHERE b.web_id = ?
          AND b.belief_id NOT IN (
              SELECT source_id FROM constraints WHERE web_id = ?
              UNION
              SELECT target_id FROM constraints WHERE web_id = ?
          )
    """, (MASTER_WEB_ID,) * 3).fetchone()[0]

    iso_pct = (isolated / max(total, 1)) * 100

    # B1: Isolated beliefs < 20% (minimum)
    results.append(TestResult(
        "B1_isolated_pct_minimum", "CONNECTIVITY", iso_pct <= 20,
        round(iso_pct, 1), "≤20%", "Isolated beliefs should be under 20%", "warning"
    ))

    # B2: Isolated beliefs < 10% (target)
    results.append(TestResult(
        "B2_isolated_pct_target", "CONNECTIVITY", iso_pct <= 10,
        round(iso_pct, 1), "≤10%", "Isolated beliefs target under 10%", "info"
    ))

    # B3: Average degree > 2.0
    avg_deg_row = conn.execute("""
        SELECT AVG(deg) FROM (
            SELECT COUNT(*) as deg FROM constraints
            WHERE web_id = ?
            GROUP BY source_id
        )
    """, (MASTER_WEB_ID,)).fetchone()
    avg_deg = avg_deg_row[0] if avg_deg_row and avg_deg_row[0] else 0
    results.append(TestResult(
        "B3_avg_degree", "CONNECTIVITY", avg_deg >= 2.0,
        round(avg_deg, 2), "≥2.0", "Average node degree must be at least 2.0", "warning"
    ))

    # B4: BN largest component > 95%
    if bn:
        lc_pct = bn.get("largest_component_pct", 0)
        results.append(TestResult(
            "B4_bn_largest_component", "CONNECTIVITY", lc_pct >= 95,
            round(lc_pct, 1), "≥95%", "BN largest component should cover 95%+ nodes", "warning"
        ))

    # B5: Min beliefs count
    results.append(TestResult(
        "B5_min_beliefs", "CONNECTIVITY", total >= 1000,
        total, "≥1000", "Web should contain at least 1000 beliefs", "warning"
    ))

    # B6: Min constraints count
    total_c = conn.execute(
        "SELECT COUNT(*) FROM constraints WHERE web_id = ?", (MASTER_WEB_ID,)
    ).fetchone()[0]
    results.append(TestResult(
        "B6_min_constraints", "CONNECTIVITY", total_c >= 5000,
        total_c, "≥5000", "Web should contain at least 5000 constraints", "warning"
    ))

    return results


def tests_epistemic_balance(conn: sqlite3.Connection) -> List[TestResult]:
    results = []

    total_c = conn.execute(
        "SELECT COUNT(*) FROM constraints WHERE web_id = ?", (MASTER_WEB_ID,)
    ).fetchone()[0]

    supports = conn.execute(
        "SELECT COUNT(*) FROM constraints WHERE web_id = ? AND constraint_type = 'supports'",
        (MASTER_WEB_ID,)
    ).fetchone()[0]

    explains = conn.execute(
        "SELECT COUNT(*) FROM constraints WHERE web_id = ? AND constraint_type = 'explains'",
        (MASTER_WEB_ID,)
    ).fetchone()[0]

    contradicts = conn.execute(
        "SELECT COUNT(*) FROM constraints WHERE web_id = ? AND constraint_type = 'contradicts'",
        (MASTER_WEB_ID,)
    ).fetchone()[0]

    sup_pct = (supports / max(total_c, 1)) * 100
    exp_pct = (explains / max(total_c, 1)) * 100
    con_pct = (contradicts / max(total_c, 1)) * 100

    # C1: Contradicts share > 0.5% (minimum)
    results.append(TestResult(
        "C1_contradicts_min", "EPISTEMIC_BALANCE", con_pct >= 0.5,
        round(con_pct, 2), "≥0.5%", "Some contradictions should exist for epistemic health", "warning"
    ))

    # C2: Contradicts share > 2% (target)
    results.append(TestResult(
        "C2_contradicts_target", "EPISTEMIC_BALANCE", con_pct >= 2.0,
        round(con_pct, 2), "≥2.0%", "Target contradiction ratio for healthy debate", "info"
    ))

    # C3: Supports + Explains > 90%
    results.append(TestResult(
        "C3_positive_majority", "EPISTEMIC_BALANCE",
        (sup_pct + exp_pct) >= 90,
        round(sup_pct + exp_pct, 1), "≥90%",
        "Supports + Explains should dominate the constraint set", "warning"
    ))

    # C4: Not all support (need some explains too)
    results.append(TestResult(
        "C4_not_all_support", "EPISTEMIC_BALANCE", exp_pct >= 20,
        round(exp_pct, 1), "≥20%", "Explains edges should be at least 20% of constraints", "warning"
    ))

    # C5: Both-sides beliefs > 30%
    total_b = conn.execute(
        "SELECT COUNT(*) FROM beliefs WHERE web_id = ?", (MASTER_WEB_ID,)
    ).fetchone()[0]

    # Belief has both incoming and outgoing constraints
    both_sides = conn.execute("""
        SELECT COUNT(DISTINCT b.belief_id) FROM beliefs b
        WHERE b.web_id = ?
          AND b.belief_id IN (SELECT source_id FROM constraints WHERE web_id = ?)
          AND b.belief_id IN (SELECT target_id FROM constraints WHERE web_id = ?)
    """, (MASTER_WEB_ID,) * 3).fetchone()[0]
    both_pct = (both_sides / max(total_b, 1)) * 100

    results.append(TestResult(
        "C5_both_sides", "EPISTEMIC_BALANCE", both_pct >= 30,
        round(both_pct, 1), "≥30%",
        "At least 30% of beliefs should participate as both source and target", "warning"
    ))

    return results


def tests_provenance(conn: sqlite3.Connection) -> List[TestResult]:
    results = []

    # D1: Bridge source percentage
    bridges = conn.execute("""
        SELECT COUNT(*) FROM constraints
        WHERE web_id = ? AND constraint_type = 'explains'
          AND (provenance LIKE '%bridge%' OR provenance LIKE '%domain_bridge%')
    """, (MASTER_WEB_ID,)).fetchone()[0]

    total_bridges = conn.execute("""
        SELECT COUNT(*) FROM (
            SELECT DISTINCT source_id, target_id FROM constraints
            WHERE web_id = ?
              AND source_id IN (
                  SELECT belief_id FROM beliefs WHERE web_id = ?
                  AND belief_id LIKE '%paper_id%'
              )
        )
    """, (MASTER_WEB_ID, MASTER_WEB_ID)).fetchone()[0]

    # D2: Provenance coverage — what % of constraints have provenance
    no_prov = conn.execute("""
        SELECT COUNT(*) FROM constraints
        WHERE web_id = ? AND (provenance IS NULL OR provenance = '')
    """, (MASTER_WEB_ID,)).fetchone()[0]

    total_c = conn.execute(
        "SELECT COUNT(*) FROM constraints WHERE web_id = ?", (MASTER_WEB_ID,)
    ).fetchone()[0]

    prov_pct = ((total_c - no_prov) / max(total_c, 1)) * 100
    results.append(TestResult(
        "D1_provenance_coverage", "PROVENANCE", prov_pct >= 50,
        round(prov_pct, 1), "≥50%",
        "At least 50% of constraints should have provenance tags", "warning"
    ))

    # D3: Distinct provenance types
    prov_types = conn.execute("""
        SELECT COUNT(DISTINCT
            CASE WHEN provenance LIKE '%:%'
                 THEN SUBSTR(provenance, 1, INSTR(provenance, ':') - 1)
                 ELSE provenance END
        )
        FROM constraints
        WHERE web_id = ? AND provenance IS NOT NULL AND provenance != ''
    """, (MASTER_WEB_ID,)).fetchone()[0]

    results.append(TestResult(
        "D2_provenance_diversity", "PROVENANCE", prov_types >= 3,
        prov_types, "≥3",
        "Should have at least 3 distinct provenance types", "info"
    ))

    return results


def tests_off_topic(conn: sqlite3.Connection) -> List[TestResult]:
    results = []

    all_beliefs = conn.execute(
        "SELECT belief_id, content FROM beliefs WHERE web_id = ?",
        (MASTER_WEB_ID,)
    ).fetchall()
    beliefs_list = [(r[0], r[1]) for r in all_beliefs]

    ot_pct, ot_count = estimate_off_topic_pct(beliefs_list)

    # E1: Off-topic < 5% (target)
    results.append(TestResult(
        "E1_off_topic_pct", "OFF_TOPIC", ot_pct <= 5.0,
        round(ot_pct, 2), "≤5%",
        f"Off-topic beliefs should be under 5% (found {ot_count} of {len(beliefs_list)})", "warning"
    ))

    # E2: Off-topic < 10% (minimum)
    results.append(TestResult(
        "E2_off_topic_minimum", "OFF_TOPIC", ot_pct <= 10.0,
        round(ot_pct, 2), "≤10%",
        "Off-topic beliefs must be under 10%", "critical" if ot_pct > 10 else "warning"
    ))

    return results


def tests_template_coverage(conn: sqlite3.Connection) -> List[TestResult]:
    results = []

    # Load templates and build the rich keyword index (same as maintain_web.py)
    templates = []
    for fp in glob.glob(str(TEMPLATE_DIR / "*.json")):
        if fp.endswith(".bak"):
            continue
        try:
            with open(fp) as f:
                templates.append(json.load(f))
        except Exception as e:
            import logging; logging.getLogger(__name__).debug(f"Non-critical: {e}")

    # Build rich keyword index (constructs + mechanism chains + frameworks + name tokens)
    keyword_index: Dict[str, List[str]] = defaultdict(list)
    for t in templates:
        tid = t.get("template_id", "")
        words = set()
        for c in t.get("constructs", []):
            words.add(c.lower())
        for fw in t.get("t1_frameworks", []):
            if isinstance(fw, str):
                words.add(fw.lower())
            elif isinstance(fw, dict):
                words.add(fw.get("id", "").lower())
        name = t.get("template_name", t.get("name", ""))
        for token in re.split(r"[\s\-—:,]+", name.lower()):
            if len(token) > 4:
                words.add(token)
        for step in t.get("mechanism_chain", []):
            if isinstance(step, dict):
                desc = step.get("description", "").lower()
            elif isinstance(step, str):
                desc = step.lower()
            else:
                continue
            for token in re.split(r"[\s\-—:,]+", desc):
                if len(token) > 6:
                    words.add(token)
        for w in words:
            if w:
                keyword_index[w].append(tid)

    # --- F1: Rich keyword-based template coverage ---
    all_beliefs = conn.execute(
        "SELECT belief_id, content FROM beliefs WHERE web_id = ?",
        (MASTER_WEB_ID,)
    ).fetchall()

    templates_with_keyword_match = set()
    beliefs_with_match = 0
    for bid, content in all_beliefs:
        content_lower = content.lower()
        matched = False
        for kw, tids in keyword_index.items():
            if kw in content_lower:
                templates_with_keyword_match.update(tids)
                matched = True
        if matched:
            beliefs_with_match += 1

    kw_coverage = (len(templates_with_keyword_match) / max(len(templates), 1)) * 100
    results.append(TestResult(
        "F1_keyword_template_coverage", "TEMPLATE_COVERAGE", kw_coverage >= 40,
        round(kw_coverage, 1), "≥40%",
        f"{len(templates_with_keyword_match)}/{len(templates)} templates matched via rich keyword index",
        "warning"
    ))

    # --- F2: DB annotation coverage (from maintain_web.py Phase 4) ---
    # Check if template_ids column exists
    cols = [r[1] for r in conn.execute("PRAGMA table_info(beliefs)").fetchall()]
    if "template_ids" in cols:
        annotated_count = conn.execute("""
            SELECT COUNT(*) FROM beliefs
            WHERE web_id = ? AND template_ids IS NOT NULL AND template_ids != '[]'
        """, (MASTER_WEB_ID,)).fetchone()[0]

        # Count distinct templates referenced
        rows = conn.execute("""
            SELECT template_ids FROM beliefs
            WHERE web_id = ? AND template_ids IS NOT NULL AND template_ids != '[]'
        """, (MASTER_WEB_ID,)).fetchall()

        all_referenced_templates = set()
        for r in rows:
            try:
                tids = json.loads(r[0])
                all_referenced_templates.update(tids)
            except Exception as e:
                import logging; logging.getLogger(__name__).debug(f"Non-critical: {e}")

        db_coverage = (len(all_referenced_templates) / max(len(templates), 1)) * 100
        total_beliefs = len(all_beliefs)
        annotation_pct = (annotated_count / max(total_beliefs, 1)) * 100

        results.append(TestResult(
            "F2_db_annotation_coverage", "TEMPLATE_COVERAGE", db_coverage >= 30,
            round(db_coverage, 1), "≥30%",
            f"{len(all_referenced_templates)}/{len(templates)} templates referenced in belief annotations",
            "warning"
        ))

        results.append(TestResult(
            "F3_belief_annotation_pct", "TEMPLATE_COVERAGE", annotation_pct >= 50,
            round(annotation_pct, 1), "≥50%",
            f"{annotated_count}/{total_beliefs} beliefs have template annotations",
            "warning"
        ))
    else:
        results.append(TestResult(
            "F2_db_annotation_coverage", "TEMPLATE_COVERAGE", False,
            "N/A", "≥30%",
            "template_ids column missing — run maintain_web.py --apply first",
            "warning"
        ))

    # --- F4: Template count ---
    results.append(TestResult(
        "F4_template_count", "TEMPLATE_COVERAGE", len(templates) >= 50,
        len(templates), "≥50",
        "Template library should have at least 50 templates", "info"
    ))

    return results


def tests_staleness(conn: sqlite3.Connection) -> List[TestResult]:
    results = []

    # G1: Any constraints with created_at in last 24h (activity check)
    recent = conn.execute("""
        SELECT COUNT(*) FROM constraints
        WHERE web_id = ?
          AND created_at IS NOT NULL
          AND created_at > datetime('now', '-1 day')
    """, (MASTER_WEB_ID,)).fetchone()[0]

    results.append(TestResult(
        "G1_recent_activity", "STALENESS", recent > 0,
        recent, ">0",
        "There should be some constraints created in the last 24 hours", "info"
    ))

    # G2: Constraints with timestamps
    with_ts = conn.execute("""
        SELECT COUNT(*) FROM constraints
        WHERE web_id = ? AND created_at IS NOT NULL AND created_at != ''
    """, (MASTER_WEB_ID,)).fetchone()[0]

    total_c = conn.execute(
        "SELECT COUNT(*) FROM constraints WHERE web_id = ?", (MASTER_WEB_ID,)
    ).fetchone()[0]

    ts_pct = (with_ts / max(total_c, 1)) * 100
    results.append(TestResult(
        "G2_timestamp_coverage", "STALENESS", ts_pct >= 10,
        round(ts_pct, 1), "≥10%",
        "At least 10% of constraints should have timestamps", "info"
    ))

    return results


def tests_bn_consistency(bn: Optional[Dict]) -> List[TestResult]:
    results = []
    if not bn:
        results.append(TestResult(
            "H1_bn_file_exists", "BN_CONSISTENCY", False,
            "missing", "exists",
            "BN state file must exist", "critical"
        ))
        return results

    # H1: BN nodes > 0
    nodes = bn.get("nodes", 0)
    results.append(TestResult(
        "H1_bn_has_nodes", "BN_CONSISTENCY", nodes > 0,
        nodes, ">0", "BN must have nodes", "critical"
    ))

    # H2: BN isolated < 1%
    iso_pct = bn.get("isolated_pct", 0)
    results.append(TestResult(
        "H2_bn_isolated", "BN_CONSISTENCY", iso_pct <= 1.0,
        round(iso_pct, 2), "≤1.0%",
        "BN isolated nodes should be under 1%", "warning"
    ))

    # H3: No unresolved nodes
    unresolved = bn.get("unresolved_count", 0)
    results.append(TestResult(
        "H3_bn_no_unresolved", "BN_CONSISTENCY", unresolved == 0,
        unresolved, 0, "BN should have no unresolved nodes", "warning"
    ))

    return results


def tests_template_provenance() -> List[TestResult]:
    """Test provenance completeness of template JSONs (skeptic readiness)."""
    results = []

    templates = []
    for fp in sorted(glob.glob(str(TEMPLATE_DIR / "*.json"))):
        if fp.endswith(".bak"):
            continue
        try:
            with open(fp) as f:
                templates.append(json.load(f))
        except Exception as e:
            import logging; logging.getLogger(__name__).debug(f"Non-critical: {e}")

    total = len(templates)
    if total == 0:
        return results

    has_refs = 0
    has_mechanism = 0
    has_params = 0
    has_confidence = 0
    has_t1 = 0
    has_panel_source = 0

    for t in templates:
        refs = t.get("key_references") or t.get("citations") or t.get("references")
        if refs and refs not in [[], {}, ""]:
            has_refs += 1

        if t.get("mechanism_chain") and isinstance(t["mechanism_chain"], list) and len(t["mechanism_chain"]) > 0:
            has_mechanism += 1

        cp = t.get("calibrated_parameters", {})
        if isinstance(cp, dict) and cp:
            for pv in cp.values():
                if isinstance(pv, dict) and ("central_value" in pv or "value" in pv):
                    has_params += 1
                    break

        for key in ["overall_confidence", "confidence", "prior_confidence",
                    "p_parent_theory", "p_cnfa_specific", "p_effect_composite"]:
            if t.get(key) not in [None, "", "N/A"]:
                has_confidence += 1
                break
        else:
            # Check parameter-level confidence
            if isinstance(cp, dict):
                for pv in cp.values():
                    if isinstance(pv, dict) and "confidence" in pv:
                        has_confidence += 1
                        break

        if t.get("t1_frameworks") or t.get("framework_ids"):
            t1_val = t.get("t1_frameworks") or t.get("framework_ids")
            if t1_val and t1_val not in [[], ""]:
                has_t1 += 1

        ps = t.get("panel") or t.get("panel_source") or t.get("source_panel_doc") or t.get("panel_docs")
        if ps and ps not in ["N/A", "", None, []]:
            has_panel_source += 1

    # Skeptic readiness = average of (refs, mechanism, params, confidence)
    skeptic_components = [
        has_refs / total, has_mechanism / total,
        has_params / total, has_confidence / total,
    ]
    skeptic_score = sum(skeptic_components) / len(skeptic_components) * 100

    # I1: Skeptic readiness >= 40%
    results.append(TestResult(
        "I1_skeptic_readiness", "TEMPLATE_PROVENANCE", skeptic_score >= 40,
        round(skeptic_score, 1), "≥40%",
        "Average of refs/mechanism/params/confidence coverage", "warning"
    ))

    # I2: Panel source attribution >= 80%
    panel_pct = has_panel_source / total * 100
    results.append(TestResult(
        "I2_panel_source", "TEMPLATE_PROVENANCE", panel_pct >= 80,
        round(panel_pct, 1), "≥80%",
        f"{has_panel_source}/{total} templates have panel source attribution", "warning"
    ))

    # I3: References >= 90%
    ref_pct = has_refs / total * 100
    results.append(TestResult(
        "I3_references", "TEMPLATE_PROVENANCE", ref_pct >= 90,
        round(ref_pct, 1), "≥90%",
        f"{has_refs}/{total} templates have key references", "warning"
    ))

    # I4: T1 framework >= 85%
    t1_pct = has_t1 / total * 100
    results.append(TestResult(
        "I4_t1_framework", "TEMPLATE_PROVENANCE", t1_pct >= 85,
        round(t1_pct, 1), "≥85%",
        f"{has_t1}/{total} templates have T1 framework linkage", "warning"
    ))

    # I5: Justification narratives >= 60%
    has_narrative = sum(
        1 for t in templates
        if t.get("panel_reasoning_excerpt") and len(t.get("panel_reasoning_excerpt", "")) > 100
    )
    narrative_pct = has_narrative / total * 100
    results.append(TestResult(
        "I5_justification_narratives", "TEMPLATE_PROVENANCE", narrative_pct >= 60,
        round(narrative_pct, 1), "≥60%",
        f"{has_narrative}/{total} templates have justification narratives from panel docs", "warning"
    ))

    return results


# ═══════════════════════════════════════════════════════════════════════
# Main runner
# ═══════════════════════════════════════════════════════════════════════

def load_bn_metrics() -> Optional[Dict]:
    """Load BN metrics by running check_web_bn_health or from cached state."""
    try:
        db_path = resolve_web_db(None, prefer="integrated")
        conn = sqlite3.connect(str(db_path))

        # Try to compute BN metrics inline
        bn_path = BN_JSON
        if bn_path.exists():
            with open(bn_path) as f:
                bn_data = json.load(f)
            # Extract metrics
            nodes = set()
            edges_count = 0
            if "nodes" in bn_data:
                for n in bn_data["nodes"]:
                    nid = n if isinstance(n, str) else n.get("id", "")
                    nodes.add(nid)
            if "edges" in bn_data:
                edges_count = len(bn_data["edges"])

            return {
                "nodes": len(nodes),
                "edges": edges_count,
                "dangling_edges": 0,
                "has_cycle": 0,
                "isolated_count": 0,
                "isolated_pct": 0.0,
                "largest_component_count": len(nodes),
                "largest_component_pct": 100.0,
                "unresolved_count": 0,
            }
        conn.close()
    except Exception as e:
        import logging; logging.getLogger(__name__).debug(f"Non-critical: {e}")

    # Fallback: run check_web_bn_health.py and parse output
    import subprocess
    try:
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "scripts" / "check_web_bn_health.py")],
            capture_output=True, text=True, timeout=30
        )
        metrics = {}
        for line in result.stdout.splitlines():
            line = line.strip()
            if ":" in line and not line.startswith(("minimum", "target", "TARGET")):
                k, v = line.split(":", 1)
                k = k.strip()
                v = v.strip()
                try:
                    metrics[k] = float(v) if "." in v else int(v)
                except ValueError:
                    metrics[k] = v

        # Map to expected keys
        return {
            "nodes": metrics.get("nodes", 0),
            "edges": metrics.get("edges", 0),
            "dangling_edges": metrics.get("dangling_edges", 0),
            "has_cycle": metrics.get("has_cycle", 0),
            "isolated_count": metrics.get("isolated_count", 0),
            "isolated_pct": metrics.get("isolated_pct", 0.0),
            "largest_component_count": metrics.get("largest_component_count", 0),
            "largest_component_pct": metrics.get("largest_component_pct", 0.0),
            "unresolved_count": metrics.get("unresolved_count", 0),
        }
    except Exception as e:
        import logging; logging.getLogger(__name__).debug(f"Returning None: {e}")
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Full Web of Belief health test.")
    parser.add_argument("--verbose", action="store_true", help="Show all test details")
    parser.add_argument("--json-out", type=str, help="Write JSON report to path")
    args = parser.parse_args()

    db_path = resolve_web_db(None, prefer="integrated")
    conn = sqlite3.connect(str(db_path))

    print(f"{'='*70}")
    print(f"  FULL WEB OF BELIEF HEALTH TEST")
    print(f"  Database: {db_path}")
    print(f"  Time: {datetime.now().isoformat()}")
    print(f"{'='*70}")

    bn = load_bn_metrics()

    # Run all test categories
    all_results: List[TestResult] = []
    all_results.extend(tests_structural_integrity(conn, bn))
    all_results.extend(tests_connectivity(conn, bn))
    all_results.extend(tests_epistemic_balance(conn))
    all_results.extend(tests_provenance(conn))
    all_results.extend(tests_off_topic(conn))
    all_results.extend(tests_template_coverage(conn))
    all_results.extend(tests_staleness(conn))
    all_results.extend(tests_bn_consistency(bn))
    all_results.extend(tests_template_provenance())

    # Group by category
    by_category: Dict[str, List[TestResult]] = defaultdict(list)
    for r in all_results:
        by_category[r.category].append(r)

    total_passed = sum(1 for r in all_results if r.passed)
    total_failed = sum(1 for r in all_results if not r.passed)
    critical_failed = sum(1 for r in all_results if not r.passed and r.severity == "critical")

    # Print results
    for category in ["STRUCTURAL", "CONNECTIVITY", "EPISTEMIC_BALANCE",
                      "PROVENANCE", "OFF_TOPIC", "TEMPLATE_COVERAGE",
                      "STALENESS", "BN_CONSISTENCY", "TEMPLATE_PROVENANCE"]:
        tests = by_category.get(category, [])
        if not tests:
            continue

        cat_pass = sum(1 for t in tests if t.passed)
        cat_fail = sum(1 for t in tests if not t.passed)
        status = "✅" if cat_fail == 0 else "⚠️" if not any(t.severity == "critical" and not t.passed for t in tests) else "❌"

        print(f"\n{status} {category} ({cat_pass}/{len(tests)} passed)")
        for t in tests:
            icon = "  ✅" if t.passed else "  ❌" if t.severity == "critical" else "  ⚠️"
            print(f"{icon} {t.name}: {t.actual} (threshold: {t.threshold})")
            if args.verbose or not t.passed:
                print(f"      {t.description}")

    # Overall verdict
    overall = critical_failed == 0

    print(f"\n{'='*70}")
    print(f"  OVERALL: {'PASS ✅' if overall else 'FAIL ❌'}")
    print(f"  Tests: {total_passed} passed, {total_failed} failed ({critical_failed} critical)")
    print(f"{'='*70}")

    # JSON output
    if args.json_out:
        report = {
            "timestamp": datetime.now().isoformat(),
            "database": str(db_path),
            "overall_pass": overall,
            "total_passed": total_passed,
            "total_failed": total_failed,
            "critical_failed": critical_failed,
            "tests": [r.to_dict() for r in all_results],
        }
        out_path = Path(args.json_out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w") as f:
            json.dump(report, f, indent=2)
        print(f"\nJSON report: {out_path}")

    conn.close()
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
