#!/usr/bin/env python3
"""
Provenance & Justification Audit
===================================
Generates a "skeptic-facing" report on how well each template, T1 framework,
and T1.5 parent theory is justified by evidence.

Audit criteria for each template:
  ① KEY REFERENCES    — Does it cite specific empirical papers?
  ② MECHANISM CHAIN   — Is the causal pathway specified step-by-step?
  ③ CALIBRATED PARAMS — Are effect sizes/parameters quantified with CIs?
  ④ T1 FRAMEWORK      — Is it anchored to a recognized theory?
  ⑤ T1.5 THEORY       — Is the bridging parent theory specified?
  ⑥ BRIDGE WARRANT    — What type of inferential warrant justifies it?
  ⑦ CONFIDENCE        — Is there a calibrated confidence score?
  ⑧ PANEL SOURCE      — Was it produced by a named expert panel?

Usage:
    python scripts/audit_provenance.py                    # Full report
    python scripts/audit_provenance.py --format markdown  # Markdown table
    python scripts/audit_provenance.py --json-out data/production/provenance_audit.json
    python scripts/audit_provenance.py --template T1      # Audit one template
"""

from __future__ import annotations

import argparse
import glob
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = PROJECT_ROOT / "data" / "templates"

# ═══════════════════════════════════════════════════════════════════════
# Provenance checks
# ═══════════════════════════════════════════════════════════════════════

CRITERIA = [
    "references",
    "mechanism_chain",
    "calibrated_params",
    "t1_framework",
    "t1_5_theory",
    "bridge_warrant",
    "confidence",
    "panel_source",
]


def audit_template(t: Dict[str, Any]) -> Dict[str, Any]:
    """Audit a single template for provenance completeness."""
    tid = t.get("template_id", "???")
    name = t.get("name", t.get("template_name", ""))

    result = {
        "template_id": tid,
        "name": name,
        "checks": {},
        "score": 0,
        "max_score": len(CRITERIA),
        "details": {},
    }

    # 1. KEY REFERENCES
    refs = t.get("key_references") or t.get("citations") or t.get("references") or t.get("apa_references")
    has_refs = bool(refs) and refs not in [[], {}, ""]
    ref_count = len(refs) if isinstance(refs, list) else (len(refs) if isinstance(refs, dict) else 0)
    result["checks"]["references"] = has_refs
    result["details"]["references"] = f"{ref_count} references" if has_refs else "MISSING"
    if has_refs:
        result["score"] += 1

    # 2. MECHANISM CHAIN
    mc = t.get("mechanism_chain", [])
    has_mc = bool(mc) and isinstance(mc, list) and len(mc) > 0
    result["checks"]["mechanism_chain"] = has_mc
    result["details"]["mechanism_chain"] = f"{len(mc)} steps" if has_mc else "MISSING"
    if has_mc:
        result["score"] += 1

    # 3. CALIBRATED PARAMETERS
    cp = t.get("calibrated_parameters", {})
    has_cp = False
    param_details = []
    if isinstance(cp, dict) and cp:
        for pk, pv in cp.items():
            if isinstance(pv, dict):
                has_ci = "CI_95" in pv or "range" in pv
                has_val = "central_value" in pv or "value" in pv
                has_warrant = "warrant" in pv
                if has_val:
                    has_cp = True
                    detail = pk
                    if has_ci:
                        detail += " (CI)"
                    if has_warrant:
                        detail += f" [{pv.get('warrant', '')}]"
                    param_details.append(detail)
    result["checks"]["calibrated_params"] = has_cp
    result["details"]["calibrated_params"] = "; ".join(param_details[:3]) if has_cp else "MISSING"
    if has_cp:
        result["score"] += 1

    # 4. T1 FRAMEWORK
    t1 = t.get("t1_frameworks") or t.get("framework_ids")
    has_t1 = bool(t1) and t1 not in [[], ""]
    t1_list = t1 if isinstance(t1, list) else [t1] if t1 else []
    result["checks"]["t1_framework"] = has_t1
    result["details"]["t1_framework"] = ", ".join(str(x) for x in t1_list[:3]) if has_t1 else "MISSING"
    if has_t1:
        result["score"] += 1

    # 5. T1.5 PARENT THEORY
    t15 = t.get("t1_5_parent_theories") or t.get("parent_theories")
    has_t15 = bool(t15) and t15 not in [[], "", {}]
    result["checks"]["t1_5_theory"] = has_t15
    if has_t15:
        if isinstance(t15, list):
            result["details"]["t1_5_theory"] = ", ".join(str(x)[:40] for x in t15[:3])
        elif isinstance(t15, dict):
            result["details"]["t1_5_theory"] = ", ".join(list(t15.keys())[:3])
        else:
            result["details"]["t1_5_theory"] = str(t15)[:60]
        result["score"] += 1
    else:
        result["details"]["t1_5_theory"] = "MISSING"

    # 6. BRIDGE WARRANT
    bw = t.get("bridge_warrant") or t.get("warrant_type") or t.get("warrant")
    has_bw = bool(bw) and bw not in ["", "N/A", None]
    result["checks"]["bridge_warrant"] = has_bw
    result["details"]["bridge_warrant"] = str(bw)[:60] if has_bw else "MISSING"
    if has_bw:
        result["score"] += 1

    # 7. CONFIDENCE SCORE
    has_conf = False
    conf_detail = "MISSING"

    # Template-level confidence
    for key in ["overall_confidence", "confidence", "prior_confidence"]:
        val = t.get(key)
        if val and val not in ["N/A", "", None]:
            has_conf = True
            conf_detail = f"{key}: {val}"
            break

    # Parameter-level confidence
    if not has_conf and isinstance(cp, dict):
        for pk, pv in cp.items():
            if isinstance(pv, dict) and "confidence" in pv:
                has_conf = True
                conf_detail = f"{pk}: confidence={pv['confidence']}"
                break

    # Probability fields from calibrated templates
    for key in ["p_parent_theory", "p_cnfa_specific", "p_effect_composite"]:
        val = t.get(key)
        if val and val not in [None, "", "N/A"]:
            has_conf = True
            conf_detail = f"{key}: {val}"
            break

    result["checks"]["confidence"] = has_conf
    result["details"]["confidence"] = conf_detail
    if has_conf:
        result["score"] += 1

    # 8. PANEL SOURCE
    panel = t.get("panel") or t.get("panel_source") or t.get("source_panel_doc")
    panel_docs = t.get("panel_docs", [])
    has_panel = bool(panel) and panel not in ["N/A", ""]
    if not has_panel and panel_docs:
        has_panel = True
        panel = f"{len(panel_docs)} panel doc(s)"
    result["checks"]["panel_source"] = has_panel
    result["details"]["panel_source"] = str(panel)[:60] if has_panel else "MISSING"
    if has_panel:
        result["score"] += 1

    # Maturity
    result["maturity"] = t.get("maturity") or t.get("overall_maturity") or "unknown"

    return result


# ═══════════════════════════════════════════════════════════════════════
# Aggregate analysis
# ═══════════════════════════════════════════════════════════════════════

def build_t1_framework_report(audits: List[Dict]) -> Dict[str, Any]:
    """Analyze T1 framework coverage across all templates."""
    framework_templates: Dict[str, List[str]] = defaultdict(list)
    for a in audits:
        t1_detail = a["details"].get("t1_framework", "MISSING")
        if t1_detail != "MISSING":
            for fw in t1_detail.split(", "):
                fw = fw.strip()
                if fw:
                    framework_templates[fw].append(a["template_id"])

    return {
        "total_frameworks": len(framework_templates),
        "frameworks": {
            fw: {"count": len(tids), "templates": tids[:5]}
            for fw, tids in sorted(framework_templates.items(), key=lambda x: -len(x[1]))
        },
    }


def build_t15_theory_report(audits: List[Dict]) -> Dict[str, Any]:
    """Analyze T1.5 parent theory coverage."""
    theory_templates: Dict[str, List[str]] = defaultdict(list)
    for a in audits:
        t15_detail = a["details"].get("t1_5_theory", "MISSING")
        if t15_detail != "MISSING":
            for th in t15_detail.split(", "):
                th = th.strip()
                if th:
                    theory_templates[th].append(a["template_id"])

    return {
        "total_theories": len(theory_templates),
        "theories": {
            th: {"count": len(tids), "templates": tids[:5]}
            for th, tids in sorted(theory_templates.items(), key=lambda x: -len(x[1]))
        },
    }


# ═══════════════════════════════════════════════════════════════════════
# Output formatting
# ═══════════════════════════════════════════════════════════════════════

def print_console_report(audits: List[Dict], t1_report: Dict, t15_report: Dict):
    """Print human-readable report."""
    total = len(audits)

    # Overall statistics
    criterion_counts = Counter()
    score_dist = Counter()
    maturity_counts = Counter()

    for a in audits:
        for crit, passed in a["checks"].items():
            if passed:
                criterion_counts[crit] += 1
        score_dist[a["score"]] += 1
        maturity_counts[a["maturity"]] += 1

    print(f"\n{'='*70}")
    print(f"  PROVENANCE & JUSTIFICATION AUDIT")
    print(f"  Templates audited: {total}")
    print(f"{'='*70}")

    # Criterion-level stats
    print(f"\n📊 CRITERION COVERAGE (% of templates passing each check):")
    print(f"{'─'*55}")
    for crit in CRITERIA:
        count = criterion_counts.get(crit, 0)
        pct = count / max(total, 1) * 100
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        status = "✅" if pct >= 80 else "⚠️" if pct >= 30 else "❌"
        print(f"  {status} {crit:<20s} {bar} {count:>3d}/{total} ({pct:.0f}%)")

    # Score distribution
    print(f"\n📈 PROVENANCE SCORE DISTRIBUTION (0-{len(CRITERIA)}):")
    print(f"{'─'*55}")
    for score in range(len(CRITERIA) + 1):
        count = score_dist.get(score, 0)
        if count > 0:
            bar = "█" * count
            label = "🔴" if score <= 2 else "🟡" if score <= 4 else "🟢"
            print(f"  {label} Score {score}: {bar} ({count})")

    avg_score = sum(a["score"] for a in audits) / max(total, 1)
    print(f"\n  Average score: {avg_score:.1f}/{len(CRITERIA)}")

    # Maturity breakdown
    print(f"\n🏗️ MATURITY LEVELS:")
    for mat, count in sorted(maturity_counts.items(), key=lambda x: -x[1]):
        print(f"  {mat}: {count}")

    # Bottom 10 — most poorly justified
    print(f"\n⚠️  LEAST JUSTIFIED TEMPLATES (lowest provenance scores):")
    print(f"{'─'*70}")
    for a in sorted(audits, key=lambda x: x["score"])[:10]:
        missing = [c for c, v in a["checks"].items() if not v]
        print(f"  [{a['score']}/{a['max_score']}] {a['template_id']}")
        print(f"       Missing: {', '.join(missing)}")

    # Top 5 — best justified
    print(f"\n✅ BEST JUSTIFIED TEMPLATES:")
    for a in sorted(audits, key=lambda x: -x["score"])[:5]:
        present = [c for c, v in a["checks"].items() if v]
        print(f"  [{a['score']}/{a['max_score']}] {a['template_id']}")
        print(f"       Has: {', '.join(present)}")

    # T1 Framework report
    print(f"\n📚 T1 FRAMEWORKS ({t1_report['total_frameworks']} distinct):")
    print(f"{'─'*55}")
    for fw, data in list(t1_report["frameworks"].items())[:10]:
        print(f"  {fw}: {data['count']} templates")

    # T1.5 Theory report
    print(f"\n🧬 T1.5 PARENT THEORIES ({t15_report['total_theories']} distinct):")
    print(f"{'─'*55}")
    if t15_report["total_theories"] == 0:
        print(f"  ❌ NO T1.5 theories are documented yet!")
        print(f"     This is the weakest link for skeptic reviews.")
    else:
        for th, data in list(t15_report["theories"].items())[:10]:
            print(f"  {th}: {data['count']} templates")

    # Skeptic readiness score
    skeptic_criteria = {
        "references": criterion_counts.get("references", 0) / max(total, 1),
        "mechanism_chain": criterion_counts.get("mechanism_chain", 0) / max(total, 1),
        "calibrated_params": criterion_counts.get("calibrated_params", 0) / max(total, 1),
        "confidence": criterion_counts.get("confidence", 0) / max(total, 1),
    }
    skeptic_score = sum(skeptic_criteria.values()) / len(skeptic_criteria) * 100

    print(f"\n{'='*70}")
    print(f"  SKEPTIC READINESS SCORE: {skeptic_score:.0f}%")
    print(f"{'='*70}")
    if skeptic_score >= 70:
        print(f"  ✅ Most templates have sufficient justification for peer review")
    elif skeptic_score >= 40:
        print(f"  ⚠️ Many templates need stronger evidence chains")
    else:
        print(f"  ❌ Significant provenance gaps — not ready for external review")

    # Actionable recommendations
    print(f"\n📋 PRIORITY ACTIONS:")
    actions = []
    if criterion_counts.get("mechanism_chain", 0) / max(total, 1) < 0.5:
        actions.append(f"  1. Add mechanism chains to {total - criterion_counts.get('mechanism_chain', 0)} templates")
    if criterion_counts.get("calibrated_params", 0) / max(total, 1) < 0.3:
        actions.append(f"  2. Add calibrated parameters to {total - criterion_counts.get('calibrated_params', 0)} templates")
    if criterion_counts.get("t1_5_theory", 0) / max(total, 1) < 0.2:
        actions.append(f"  3. Document T1.5 parent theories for {total - criterion_counts.get('t1_5_theory', 0)} templates")
    if criterion_counts.get("confidence", 0) / max(total, 1) < 0.3:
        actions.append(f"  4. Add confidence scores to {total - criterion_counts.get('confidence', 0)} templates")
    if criterion_counts.get("bridge_warrant", 0) / max(total, 1) < 0.3:
        actions.append(f"  5. Specify bridge warrants for {total - criterion_counts.get('bridge_warrant', 0)} templates")

    for a in actions:
        print(a)
    if not actions:
        print("  None — all criteria above 50%!")


def print_markdown_report(audits: List[Dict]):
    """Print markdown table format."""
    print("| Template ID | Score | Refs | Mech | Params | T1 | T1.5 | Warrant | Conf | Panel |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for a in sorted(audits, key=lambda x: (-x["score"], x["template_id"])):
        cells = [a["template_id"], f"{a['score']}/{a['max_score']}"]
        for crit in CRITERIA:
            cells.append("✅" if a["checks"].get(crit) else "❌")
        print("| " + " | ".join(cells) + " |")


# ═══════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════

def main() -> int:
    parser = argparse.ArgumentParser(description="Provenance & justification audit.")
    parser.add_argument("--format", choices=["console", "markdown"], default="console")
    parser.add_argument("--json-out", type=str, help="Write JSON report")
    parser.add_argument("--template", type=str, help="Audit a single template")
    args = parser.parse_args()

    # Load all templates
    templates = []
    for fp in sorted(glob.glob(str(TEMPLATE_DIR / "*.json"))):
        if fp.endswith(".bak"):
            continue
        try:
            with open(fp) as f:
                templates.append(json.load(f))
        except Exception as e:
            import logging; logging.getLogger(__name__).debug(f"Non-critical: {e}")

    if args.template:
        templates = [t for t in templates if t.get("template_id", "").startswith(args.template)]
        if not templates:
            print(f"No templates matching '{args.template}'")
            return 1

    # Audit each template
    audits = [audit_template(t) for t in templates]

    # Build aggregate reports
    t1_report = build_t1_framework_report(audits)
    t15_report = build_t15_theory_report(audits)

    # Output
    if args.format == "markdown":
        print_markdown_report(audits)
    else:
        print_console_report(audits, t1_report, t15_report)

    # JSON output
    if args.json_out:
        report = {
            "total_templates": len(audits),
            "avg_score": round(sum(a["score"] for a in audits) / max(len(audits), 1), 2),
            "criterion_coverage": {
                crit: sum(1 for a in audits if a["checks"].get(crit)) / max(len(audits), 1) * 100
                for crit in CRITERIA
            },
            "t1_frameworks": t1_report,
            "t1_5_theories": t15_report,
            "templates": audits,
        }
        out_path = Path(args.json_out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w") as f:
            json.dump(report, f, indent=2)
        print(f"\nJSON report: {out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
