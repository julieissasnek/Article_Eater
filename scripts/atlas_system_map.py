#!/usr/bin/env python3
"""
ATLAS System Map — Programmatic Visualization of Web & BN Organization
======================================================================

Created: 2026-02-27
Sprint: COMPLETENESS-1

Generates a comprehensive structural map of the ATLAS system:
1. Module dependency graph (who imports whom)
2. Web of Belief structure (beliefs × constraints × theories)
3. BN node/edge topology (epistemic variables × causal pathways)
4. Pipeline flow diagram (discovery → triage → extraction → integration)
5. Data flow audit (where data lives, what format, who reads/writes)

Outputs:
    - docs/system_maps/atlas_module_graph.dot      (Graphviz DOT)
    - docs/system_maps/atlas_module_graph.json      (D3-ready JSON)
    - docs/system_maps/atlas_system_report.md        (Markdown report)
    - docs/system_maps/web_structure_summary.json    (Web topology)
    - docs/system_maps/bn_structure_summary.json     (BN topology)

Usage:
    python scripts/atlas_system_map.py                  # Full report
    python scripts/atlas_system_map.py --modules        # Module graph only
    python scripts/atlas_system_map.py --web            # Web structure only
    python scripts/atlas_system_map.py --bn             # BN structure only
    python scripts/atlas_system_map.py --pipelines      # Pipeline map only
    python scripts/atlas_system_map.py --data           # Data flow audit only
"""

import ast
import json
import os
import sys
import argparse
import sqlite3
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

# Add repo root to path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

OUTPUT_DIR = REPO_ROOT / "docs" / "system_maps"


# =============================================================================
# 1. MODULE DEPENDENCY GRAPH
# =============================================================================

def build_module_graph(root: Path = None) -> Dict[str, Any]:
    """
    Walk all .py files under src/ and scripts/, extract import statements,
    build a directed dependency graph of internal modules.

    Returns:
        {
            "nodes": [{"id": "src.services.overseer", "package": "services", ...}],
            "edges": [{"source": "src.services.overseer", "target": "src.services.web_of_belief"}],
            "stats": {"n_modules": N, "n_edges": M, "orphans": [...], "hubs": [...]}
        }
    """
    root = root or REPO_ROOT
    src_dir = root / "src"
    scripts_dir = root / "scripts"

    nodes = {}
    edges = []
    import_counts = defaultdict(int)  # how many modules import this one

    # Collect all Python files
    py_files = []
    for search_dir in [src_dir, scripts_dir]:
        if search_dir.exists():
            py_files.extend(search_dir.rglob("*.py"))

    for py_file in py_files:
        rel = py_file.relative_to(root)
        mod_id = str(rel).replace("/", ".").replace(".py", "")
        if mod_id.endswith(".__init__"):
            mod_id = mod_id[: -len(".__init__")]

        # Determine package
        parts = mod_id.split(".")
        package = parts[1] if len(parts) > 1 else "root"

        nodes[mod_id] = {
            "id": mod_id,
            "package": package,
            "path": str(rel),
            "size_bytes": py_file.stat().st_size,
        }

        # Parse imports
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            targets = set()
            if isinstance(node, ast.Import):
                for alias in node.names:
                    targets.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    targets.add(node.module)

            for target in targets:
                # Only track internal imports (src.* or scripts.*)
                if target.startswith("src.") or target.startswith("scripts."):
                    edges.append({"source": mod_id, "target": target})
                    import_counts[target] += 1

    # Compute stats
    orphans = [
        n for n in nodes if import_counts[n] == 0 and n.startswith("src.")
    ]
    hubs = sorted(
        [(mod, cnt) for mod, cnt in import_counts.items() if cnt >= 3],
        key=lambda x: -x[1],
    )

    return {
        "nodes": list(nodes.values()),
        "edges": edges,
        "stats": {
            "n_modules": len(nodes),
            "n_edges": len(edges),
            "orphan_modules": orphans[:20],
            "hub_modules": [{"module": m, "imported_by": c} for m, c in hubs[:15]],
            "packages": sorted(set(n["package"] for n in nodes.values())),
        },
    }


def module_graph_to_dot(graph: Dict[str, Any]) -> str:
    """Convert module graph to Graphviz DOT format."""
    lines = [
        'digraph ATLAS_Modules {',
        '  rankdir=LR;',
        '  node [shape=box, style="rounded,filled", fontsize=10];',
        '  edge [color="#666666", arrowsize=0.6];',
        '',
    ]

    # Color by package
    palette = {
        "services": "#d4edda",
        "epistemic": "#fff3cd",
        "api": "#cce5ff",
        "models": "#f8d7da",
        "scripts": "#e0ffff",
    }

    # Add nodes grouped by package
    packages = defaultdict(list)
    for n in graph["nodes"]:
        packages[n["package"]].append(n)

    for pkg, members in sorted(packages.items()):
        color = palette.get(pkg, "#f0f0f0")
        lines.append(f'  subgraph cluster_{pkg} {{')
        lines.append(f'    label="{pkg}";')
        lines.append(f'    style=filled; color="{color}";')
        for m in members:
            short = m["id"].split(".")[-1]
            kb = m["size_bytes"] / 1024
            lines.append(f'    "{m["id"]}" [label="{short}\\n({kb:.0f}KB)"];')
        lines.append('  }')
        lines.append('')

    # Add edges
    for e in graph["edges"]:
        if e["source"] in {n["id"] for n in graph["nodes"]}:
            lines.append(f'  "{e["source"]}" -> "{e["target"]}";')

    lines.append('}')
    return '\n'.join(lines)


# =============================================================================
# 2. WEB OF BELIEF STRUCTURE
# =============================================================================

def analyze_web_structure(db_path: Path = None) -> Dict[str, Any]:
    """
    Query the web of belief database for structural statistics.

    Returns topology: belief counts by level/status, constraint counts by type,
    theory world membership, stub count, orphan beliefs, coherence metrics.
    """
    if db_path is None:
        # Try common locations
        candidates = [
            REPO_ROOT / "data" / "web_of_belief.db",
            REPO_ROOT / "data" / "production" / "web_of_belief.db",
            REPO_ROOT / "app" / "streamlit" / "db" / "contracts" / "web_of_belief.db",
        ]
        db_path = next((p for p in candidates if p.exists()), None)

    if not db_path or not db_path.exists():
        return {
            "status": "no_database",
            "message": f"Web of belief database not found. Searched: {[str(c) for c in candidates]}",
            "candidates": [str(c) for c in candidates],
        }

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    result = {"status": "ok", "db_path": str(db_path)}

    # Get table list
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    result["tables"] = tables

    # Beliefs
    if "beliefs" in tables:
        cursor.execute("SELECT COUNT(*) FROM beliefs")
        result["total_beliefs"] = cursor.fetchone()[0]

        # By level
        try:
            cursor.execute(
                "SELECT level, COUNT(*) as n FROM beliefs GROUP BY level ORDER BY n DESC"
            )
            result["beliefs_by_level"] = {
                row["level"]: row["n"] for row in cursor.fetchall()
            }
        except Exception:
            result["beliefs_by_level"] = "column_not_found"

        # By status
        try:
            cursor.execute(
                "SELECT status, COUNT(*) as n FROM beliefs GROUP BY status ORDER BY n DESC"
            )
            result["beliefs_by_status"] = {
                row["status"]: row["n"] for row in cursor.fetchall()
            }
        except Exception:
            result["beliefs_by_status"] = "column_not_found"

        # Stubs
        try:
            cursor.execute(
                "SELECT COUNT(*) FROM beliefs WHERE status='stub'"
            )
            result["stub_count"] = cursor.fetchone()[0]
        except Exception:
            result["stub_count"] = "unknown"

    # Constraints
    if "constraints" in tables:
        cursor.execute("SELECT COUNT(*) FROM constraints")
        result["total_constraints"] = cursor.fetchone()[0]

        try:
            cursor.execute(
                "SELECT type, COUNT(*) as n FROM constraints GROUP BY type ORDER BY n DESC"
            )
            result["constraints_by_type"] = {
                row["type"]: row["n"] for row in cursor.fetchall()
            }
        except Exception:
            result["constraints_by_type"] = "column_not_found"

    # Theory worlds
    if "theory_worlds" in tables:
        cursor.execute("SELECT COUNT(*) FROM theory_worlds")
        result["total_theory_worlds"] = cursor.fetchone()[0]

        try:
            cursor.execute("SELECT id, name FROM theory_worlds LIMIT 20")
            result["theory_worlds_sample"] = [
                dict(row) for row in cursor.fetchall()
            ]
        except Exception:
            pass

    # Orphan beliefs (no constraints)
    if "beliefs" in tables and "constraints" in tables:
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM beliefs b
                WHERE NOT EXISTS (
                    SELECT 1 FROM constraints c
                    WHERE c.source_id = b.id OR c.target_id = b.id
                )
            """)
            result["orphan_beliefs"] = cursor.fetchone()[0]
        except Exception:
            result["orphan_beliefs"] = "query_failed"

    conn.close()
    return result


# =============================================================================
# 3. BAYESIAN NETWORK STRUCTURE
# =============================================================================

def analyze_bn_structure() -> Dict[str, Any]:
    """
    Analyze the BN structure from code definitions (bn_nodes.py, bn_edges.py)
    and any existing BN database.
    """
    result = {"status": "ok"}

    # Load from code definitions
    try:
        from src.epistemic.bn_nodes import (
            EPISTEMIC_VARIABLES,
            get_pe_variables,
            get_environmental_variables,
            get_source_quality_variables,
        )

        all_vars = EPISTEMIC_VARIABLES
        result["total_variables"] = len(all_vars)
        result["variables_by_category"] = defaultdict(list)
        for var_id, var in all_vars.items():
            cat = getattr(var, "category", "uncategorized")
            result["variables_by_category"][cat].append(var_id)
        result["variables_by_category"] = dict(result["variables_by_category"])

        result["pe_variables"] = [v.var_id for v in get_pe_variables()]
        result["environmental_variables"] = [
            v.var_id for v in get_environmental_variables()
        ]
        result["source_quality_variables"] = [
            v.var_id for v in get_source_quality_variables()
        ]

    except ImportError as e:
        result["bn_nodes_error"] = str(e)

    # Load edges
    try:
        from src.epistemic.bn_edges import (
            PATHWAY_DEFAULTS,
            PathwayType,
        )

        pathway_counts = defaultdict(int)
        for keyword, ptype in PATHWAY_DEFAULTS.items():
            pathway_counts[ptype.value] += 1

        result["pathway_defaults_count"] = len(PATHWAY_DEFAULTS)
        result["pathways_by_type"] = dict(pathway_counts)
        result["pathway_keywords_sample"] = list(PATHWAY_DEFAULTS.keys())[:15]

    except ImportError as e:
        result["bn_edges_error"] = str(e)

    # Check for BN database
    bn_db_candidates = [
        REPO_ROOT / "data" / "bn.db",
        REPO_ROOT / "data" / "production" / "bn.db",
        REPO_ROOT / "data" / "bayesian_network.db",
    ]
    for candidate in bn_db_candidates:
        if candidate.exists():
            result["bn_db_path"] = str(candidate)
            try:
                conn = sqlite3.connect(str(candidate))
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
                result["bn_db_tables"] = [r[0] for r in cursor.fetchall()]
                conn.close()
            except Exception as e:
                result["bn_db_error"] = str(e)
            break
    else:
        result["bn_db_path"] = "not_found"

    return result


# =============================================================================
# 4. PIPELINE FLOW MAP
# =============================================================================

def map_pipelines() -> Dict[str, Any]:
    """
    Document all registered pipelines and their flow.
    """
    pipelines = [
        {
            "id": "discovery",
            "name": "Article Discovery",
            "stages": [
                "gap_prediction",
                "wishlist_check",
                "doi_auto_lookup",
                "unpaywall_oa_check",
                "ag_acquisition_pipeline",
                "zotero_watcher",
            ],
            "input": "research_gaps + wishlist",
            "output": "data/extraction_pipeline/extraction_queue.json",
            "scripts": [
                "scripts/scheduled_pipeline.py (discovery stage)",
                "scripts/run_acquisition_pipeline.py",
            ],
            "hitl": False,
        },
        {
            "id": "triage",
            "name": "Article Triage",
            "stages": [
                "gemini_classification",
                "article_type_detection",
                "priority_scoring",
            ],
            "input": "extraction_queue (status=pending)",
            "output": "extraction_queue (status=triaged)",
            "scripts": ["scripts/gemini_triage_papers.py"],
            "hitl": False,
        },
        {
            "id": "extraction",
            "name": "Claim Extraction",
            "stages": [
                "gemini_extraction",
                "claim_validation",
                "claimv2_normalization",
            ],
            "input": "extraction_queue (status=triaged)",
            "output": "extraction_queue (status=accepted)",
            "scripts": ["scripts/gemini_extraction_queue.py"],
            "hitl": False,
        },
        {
            "id": "approval",
            "name": "Human Approval (HITL)",
            "stages": [
                "review_summary",
                "human_review",
                "approve_or_reject",
            ],
            "input": "extraction_queue (status=accepted)",
            "output": "extraction_queue (status=approved|rejected)",
            "scripts": ["scripts/review_extractions.py"],
            "hitl": True,
            "notification": "EXTRACTION_REVIEW",
        },
        {
            "id": "integration",
            "name": "14-Step Integration Cascade",
            "stages": [
                "schema_validation",
                "node_classification",
                "warrant_assignment",
                "ceiling_enforcement",
                "bridge_construction",
                "credence_computation",
                "web_insertion",
                "constraint_wiring",
                "coherence_assessment",
                "entrenchment_update",
                "bn_projection",
                "theory_world_update",
                "post_integration_check",
                "notification",
            ],
            "input": "extraction_queue (status=approved)",
            "output": "web_of_belief.db + bn updates",
            "scripts": [
                "src/services/paper_integration/orchestrator.py",
                "src/services/extraction_approval.py",
            ],
            "hitl": False,
        },
        {
            "id": "overseer",
            "name": "Overseer Nightly",
            "stages": [
                "system_health",
                "web_bn_health",
                "ceiling_lint",
                "corpus_health",
                "periodic_audit",
                "pipeline_registry",
                "trend_comparison",
                "notifications",
            ],
            "input": "all databases + previous reports",
            "output": "docs/overseer_reports/unified_health_{date}.md",
            "scripts": ["scripts/overseer_nightly_v2.py"],
            "hitl": False,
        },
    ]

    # Check which scripts actually exist
    for p in pipelines:
        for i, script in enumerate(p["scripts"]):
            path = REPO_ROOT / script.split(" (")[0]  # strip comments
            p["scripts"][i] = {
                "path": script,
                "exists": path.exists(),
            }

    return {
        "pipelines": pipelines,
        "flow": "discovery → triage → extraction → [HITL approval] → integration → overseer",
        "total_stages": sum(len(p["stages"]) for p in pipelines),
        "hitl_gates": [p["id"] for p in pipelines if p["hitl"]],
    }


# =============================================================================
# 5. DATA FLOW AUDIT
# =============================================================================

def audit_data_flow() -> Dict[str, Any]:
    """
    Document all data stores, their format, and read/write ownership.
    """
    data_dir = REPO_ROOT / "data"
    stores = []

    # Check known data paths
    known_paths = [
        ("extraction_pipeline/extraction_queue.json", "JSON", "Pipeline queue"),
        ("notifications/queue.json", "JSON", "Notification queue"),
        ("notifications/approval_log.json", "JSON", "Approval audit trail"),
        ("web_of_belief.db", "SQLite", "Web of belief (primary)"),
        ("production/web_of_belief.db", "SQLite", "Web of belief (production)"),
        ("overseer.db", "SQLite", "Overseer governance DB"),
        ("extractions/", "JSON files", "Raw extraction results"),
        ("pdfs/", "PDF files", "Downloaded papers"),
    ]

    for rel_path, fmt, desc in known_paths:
        full_path = data_dir / rel_path
        exists = full_path.exists()
        size = None
        if exists and full_path.is_file():
            size = full_path.stat().st_size
        elif exists and full_path.is_dir():
            size = sum(f.stat().st_size for f in full_path.rglob("*") if f.is_file())

        stores.append({
            "path": f"data/{rel_path}",
            "format": fmt,
            "description": desc,
            "exists": exists,
            "size_bytes": size,
        })

    return {
        "data_stores": stores,
        "data_dir": str(data_dir),
        "data_dir_exists": data_dir.exists(),
    }


# =============================================================================
# REPORT GENERATION
# =============================================================================

def generate_markdown_report(
    module_graph: Dict = None,
    web_structure: Dict = None,
    bn_structure: Dict = None,
    pipeline_map: Dict = None,
    data_flow: Dict = None,
) -> str:
    """Generate a comprehensive markdown system report."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        "# ATLAS System Map",
        f"*Generated: {now}*",
        "",
        "This document provides a programmatic structural overview of the ATLAS",
        "(Architecture for Typed, Layered Assessment of Science) system.",
        "",
    ]

    # --- Module Graph ---
    if module_graph:
        stats = module_graph["stats"]
        lines.extend([
            "## 1. Module Dependency Graph",
            "",
            f"Total Python modules: **{stats['n_modules']}**",
            f"Internal import edges: **{stats['n_edges']}**",
            f"Packages: {', '.join(stats['packages'])}",
            "",
        ])
        if stats.get("hub_modules"):
            lines.append("### Hub Modules (most imported)")
            lines.append("")
            lines.append("| Module | Imported By |")
            lines.append("|--------|------------|")
            for h in stats["hub_modules"][:10]:
                lines.append(f"| `{h['module']}` | {h['imported_by']} |")
            lines.append("")

        if stats.get("orphan_modules"):
            lines.append(f"### Orphan Modules ({len(stats['orphan_modules'])} never imported)")
            lines.append("")
            for o in stats["orphan_modules"][:10]:
                lines.append(f"- `{o}`")
            lines.append("")

    # --- Web of Belief ---
    if web_structure:
        lines.extend([
            "## 2. Web of Belief Structure",
            "",
        ])
        if web_structure.get("status") == "no_database":
            lines.append(f"*Database not found.* {web_structure.get('message', '')}")
        else:
            lines.append(f"Database: `{web_structure.get('db_path', '?')}`")
            lines.append(f"Tables: {', '.join(web_structure.get('tables', []))}")
            lines.append(f"Total beliefs: **{web_structure.get('total_beliefs', '?')}**")
            lines.append(f"Total constraints: **{web_structure.get('total_constraints', '?')}**")
            lines.append(f"Orphan beliefs: **{web_structure.get('orphan_beliefs', '?')}**")
            lines.append(f"Stubs: **{web_structure.get('stub_count', '?')}**")
            lines.append("")

            if isinstance(web_structure.get("beliefs_by_level"), dict):
                lines.append("### Beliefs by Epistemic Level")
                lines.append("")
                lines.append("| Level | Count |")
                lines.append("|-------|-------|")
                for level, count in web_structure["beliefs_by_level"].items():
                    lines.append(f"| {level} | {count} |")
                lines.append("")

            if isinstance(web_structure.get("constraints_by_type"), dict):
                lines.append("### Constraints by Type")
                lines.append("")
                lines.append("| Type | Count |")
                lines.append("|------|-------|")
                for ctype, count in web_structure["constraints_by_type"].items():
                    lines.append(f"| {ctype} | {count} |")
                lines.append("")

    # --- Bayesian Network ---
    if bn_structure:
        lines.extend([
            "## 3. Bayesian Network Structure",
            "",
        ])
        lines.append(f"Total epistemic variables: **{bn_structure.get('total_variables', '?')}**")
        lines.append(f"Pathway defaults: **{bn_structure.get('pathway_defaults_count', '?')}**")
        lines.append(f"BN database: `{bn_structure.get('bn_db_path', 'not found')}`")
        lines.append("")

        if bn_structure.get("pathways_by_type"):
            lines.append("### Pathways by Type")
            lines.append("")
            lines.append("| Pathway Type | Count |")
            lines.append("|-------------|-------|")
            for ptype, count in bn_structure["pathways_by_type"].items():
                lines.append(f"| {ptype} | {count} |")
            lines.append("")

        if bn_structure.get("variables_by_category"):
            lines.append("### Variables by Category")
            lines.append("")
            for cat, vars in bn_structure["variables_by_category"].items():
                lines.append(f"- **{cat}** ({len(vars)}): {', '.join(vars[:5])}{'...' if len(vars) > 5 else ''}")
            lines.append("")

    # --- Pipeline Map ---
    if pipeline_map:
        lines.extend([
            "## 4. Pipeline Architecture",
            "",
            f"Flow: `{pipeline_map['flow']}`",
            f"Total stages across all pipelines: **{pipeline_map['total_stages']}**",
            f"HITL gates: {', '.join(pipeline_map['hitl_gates'])}",
            "",
        ])
        for p in pipeline_map["pipelines"]:
            hitl_badge = " [HITL]" if p["hitl"] else ""
            lines.append(f"### {p['name']}{hitl_badge}")
            lines.append("")
            lines.append(f"- Input: `{p['input']}`")
            lines.append(f"- Output: `{p['output']}`")
            lines.append(f"- Stages: {' → '.join(p['stages'])}")
            for s in p["scripts"]:
                if isinstance(s, dict):
                    exists = "exists" if s["exists"] else "MISSING"
                    lines.append(f"- Script: `{s['path']}` ({exists})")
            lines.append("")

    # --- Data Flow ---
    if data_flow:
        lines.extend([
            "## 5. Data Stores",
            "",
            "| Path | Format | Description | Exists | Size |",
            "|------|--------|-------------|--------|------|",
        ])
        for store in data_flow["data_stores"]:
            size_str = ""
            if store["size_bytes"] is not None:
                if store["size_bytes"] > 1_000_000:
                    size_str = f"{store['size_bytes'] / 1_000_000:.1f} MB"
                elif store["size_bytes"] > 1_000:
                    size_str = f"{store['size_bytes'] / 1_000:.1f} KB"
                else:
                    size_str = f"{store['size_bytes']} B"
            exists_str = "yes" if store["exists"] else "NO"
            lines.append(
                f"| `{store['path']}` | {store['format']} | "
                f"{store['description']} | {exists_str} | {size_str} |"
            )
        lines.append("")

    return "\n".join(lines)


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="ATLAS System Map — structural visualization"
    )
    parser.add_argument("--modules", action="store_true", help="Module dependency graph only")
    parser.add_argument("--web", action="store_true", help="Web of belief structure only")
    parser.add_argument("--bn", action="store_true", help="BN structure only")
    parser.add_argument("--pipelines", action="store_true", help="Pipeline map only")
    parser.add_argument("--data", action="store_true", help="Data flow audit only")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of markdown")
    args = parser.parse_args()

    # If no flags, run all
    run_all = not any([args.modules, args.web, args.bn, args.pipelines, args.data])

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    results = {}

    if run_all or args.modules:
        print("Analyzing module dependencies...")
        graph = build_module_graph()
        results["module_graph"] = graph

        # Write DOT file
        dot = module_graph_to_dot(graph)
        (OUTPUT_DIR / "atlas_module_graph.dot").write_text(dot, encoding="utf-8")

        # Write JSON
        (OUTPUT_DIR / "atlas_module_graph.json").write_text(
            json.dumps(graph, indent=2, default=str), encoding="utf-8"
        )
        print(f"  {graph['stats']['n_modules']} modules, {graph['stats']['n_edges']} edges")

    if run_all or args.web:
        print("Analyzing web of belief structure...")
        web = analyze_web_structure()
        results["web_structure"] = web
        (OUTPUT_DIR / "web_structure_summary.json").write_text(
            json.dumps(web, indent=2, default=str), encoding="utf-8"
        )
        if web.get("status") == "ok":
            print(f"  {web.get('total_beliefs', '?')} beliefs, {web.get('total_constraints', '?')} constraints")
        else:
            print(f"  {web.get('message', 'No database found')}")

    if run_all or args.bn:
        print("Analyzing BN structure...")
        bn = analyze_bn_structure()
        results["bn_structure"] = bn
        (OUTPUT_DIR / "bn_structure_summary.json").write_text(
            json.dumps(bn, indent=2, default=str), encoding="utf-8"
        )
        print(f"  {bn.get('total_variables', '?')} variables, {bn.get('pathway_defaults_count', '?')} pathway defaults")

    if run_all or args.pipelines:
        print("Mapping pipelines...")
        pipes = map_pipelines()
        results["pipeline_map"] = pipes
        (OUTPUT_DIR / "pipeline_map.json").write_text(
            json.dumps(pipes, indent=2, default=str), encoding="utf-8"
        )
        print(f"  {len(pipes['pipelines'])} pipelines, {pipes['total_stages']} total stages")

    if run_all or args.data:
        print("Auditing data flow...")
        data = audit_data_flow()
        results["data_flow"] = data
        (OUTPUT_DIR / "data_flow_audit.json").write_text(
            json.dumps(data, indent=2, default=str), encoding="utf-8"
        )
        existing = sum(1 for s in data["data_stores"] if s["exists"])
        print(f"  {existing}/{len(data['data_stores'])} data stores present")

    if args.json:
        print(json.dumps(results, indent=2, default=str))
    else:
        # Generate unified markdown report
        report = generate_markdown_report(
            module_graph=results.get("module_graph"),
            web_structure=results.get("web_structure"),
            bn_structure=results.get("bn_structure"),
            pipeline_map=results.get("pipeline_map"),
            data_flow=results.get("data_flow"),
        )
        report_path = OUTPUT_DIR / "atlas_system_report.md"
        report_path.write_text(report, encoding="utf-8")
        print(f"\nReport written to: {report_path}")
        print(f"All outputs in: {OUTPUT_DIR}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
