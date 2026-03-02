#!/usr/bin/env python3
"""
T3 Belief DAG Visualization — Wave 8h
======================================

Generates a directed acyclic graph (DAG) from T3 established beliefs.
Output: Mermaid diagram (markdown-embeddable) + DOT format for Graphviz.

Expert Panel (#13 Bayesian Network Expert):
  "Generate DAG from T3 established beliefs for visual inspection."

Usage:
    python3 scripts/visualize_belief_dag.py
    python3 scripts/visualize_belief_dag.py --output data/reports/
    python3 scripts/visualize_belief_dag.py --format mermaid
    python3 scripts/visualize_belief_dag.py --format dot
    python3 scripts/visualize_belief_dag.py --min-confidence 0.7
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def build_dag(min_confidence=0.6, min_findings=2):
    """Build DAG from T3 beliefs."""
    from src.services.generalization_tree import GeneralizationEngine, Finding

    # Load findings from extractions
    ext_dir = PROJECT_ROOT / "data" / "extractions"
    findings = []
    finding_id = 0

    for ext_file in ext_dir.glob("*.json"):
        try:
            data = json.loads(ext_file.read_text(errors='replace'))
            if not isinstance(data, dict):
                continue
            doi = data.get("doi", ext_file.stem)
            for f in data.get("findings", []):
                if not f.get("antecedent") or not f.get("consequent"):
                    continue
                # Classify IV/DV
                try:
                    from src.services.iv_dv_classifier import get_classifier
                    classifier = get_classifier()
                    iv_class = classifier.classify_iv(f["antecedent"])
                    dv_class = classifier.classify_dv(f["consequent"])
                    findings.append(Finding(
                        finding_id=f"f_{finding_id}",
                        iv_node=iv_class.node_id,
                        dv_node=dv_class.node_id,
                        effect_direction=f.get("direction", "positive"),
                        effect_size=f.get("effect_size"),
                        sample_size=f.get("sample_size", 0) or 0,
                        source_doi=doi,
                    ))
                    finding_id += 1
                except Exception:
                    pass
        except Exception:
            pass

    if not findings:
        print("No findings loaded. Check data/extractions/ directory.")
        return None, []

    # Build T3 beliefs
    engine = GeneralizationEngine()
    engine.add_findings(findings)
    engine.aggregate()

    # Filter to high-confidence beliefs
    beliefs = [
        b for b in engine.beliefs.values()
        if b.confidence >= min_confidence and b.n_total >= min_findings
    ]

    # Build edges: IV → DV
    edges = []
    iv_nodes = set()
    dv_nodes = set()
    for b in beliefs:
        iv_nodes.add(b.iv_node)
        dv_nodes.add(b.dv_node)
        edges.append({
            "from": b.iv_node,
            "to": b.dv_node,
            "direction": b.effect_direction,
            "confidence": b.confidence,
            "n_total": b.n_total,
            "status": b.status.value,
            "t3_id": b.t3_id,
        })

    return {
        "iv_nodes": sorted(iv_nodes),
        "dv_nodes": sorted(dv_nodes),
        "edges": edges,
        "n_beliefs": len(beliefs),
        "n_established": sum(1 for b in beliefs if b.status.value == "established"),
        "n_contested": sum(1 for b in beliefs if b.status.value == "contested"),
    }, beliefs


def to_mermaid(dag):
    """Convert DAG to Mermaid diagram format."""
    lines = ["graph LR"]

    # Style classes
    lines.append("    classDef iv fill:#4a90d9,stroke:#1a5fa3,color:#fff")
    lines.append("    classDef dv fill:#47b347,stroke:#2d8a2d,color:#fff")
    lines.append("    classDef contested fill:#e8a838,stroke:#b88320,color:#fff")

    # Nodes
    for iv in dag["iv_nodes"]:
        safe_id = iv.replace(".", "_").replace("-", "_")
        label = iv.split(".")[-1] if "." in iv else iv
        lines.append(f"    {safe_id}[\"{label}\"]:::iv")

    for dv in dag["dv_nodes"]:
        safe_id = dv.replace(".", "_").replace("-", "_")
        label = dv.split(".")[-1] if "." in dv else dv
        lines.append(f"    {safe_id}[\"{label}\"]:::dv")

    # Edges
    for edge in dag["edges"]:
        from_id = edge["from"].replace(".", "_").replace("-", "_")
        to_id = edge["to"].replace(".", "_").replace("-", "_")
        arrow = "-->" if edge["direction"] == "positive" else "-.->|neg|"
        conf = f"{edge['confidence']:.0%}"
        n = edge["n_total"]
        if edge["status"] == "contested":
            lines.append(f"    {from_id} -.->|\"?({n})\"| {to_id}")
        else:
            lines.append(f"    {from_id} {arrow}|\"({n}) {conf}\"| {to_id}")

    return "\n".join(lines)


def to_dot(dag):
    """Convert DAG to Graphviz DOT format."""
    lines = [
        "digraph T3_Beliefs {",
        "    rankdir=LR;",
        "    node [shape=box, style=rounded, fontname=\"Helvetica\"];",
        "    graph [fontname=\"Helvetica\", fontsize=12];",
        "",
    ]

    # IV nodes
    for iv in dag["iv_nodes"]:
        safe_id = iv.replace(".", "_").replace("-", "_")
        label = iv.replace(".", "\\n")
        lines.append(f'    {safe_id} [label="{label}", fillcolor="#4a90d9", style="rounded,filled", fontcolor=white];')

    lines.append("")

    # DV nodes
    for dv in dag["dv_nodes"]:
        safe_id = dv.replace(".", "_").replace("-", "_")
        label = dv.replace(".", "\\n")
        lines.append(f'    {safe_id} [label="{label}", fillcolor="#47b347", style="rounded,filled", fontcolor=white];')

    lines.append("")

    # Edges
    for edge in dag["edges"]:
        from_id = edge["from"].replace(".", "_").replace("-", "_")
        to_id = edge["to"].replace(".", "_").replace("-", "_")
        width = max(1, min(4, edge["n_total"] / 3))
        color = "#2d2d2d" if edge["direction"] == "positive" else "#cc3333"
        style = "dashed" if edge["status"] == "contested" else "solid"
        label = f'n={edge["n_total"]}, {edge["confidence"]:.0%}'
        lines.append(f'    {from_id} -> {to_id} [label="{label}", penwidth={width:.1f}, color="{color}", style="{style}"];')

    lines.append("}")
    return "\n".join(lines)


def to_json_summary(dag, beliefs):
    """Produce a JSON summary of the DAG."""
    return {
        "generated": datetime.now().isoformat(),
        "n_iv_nodes": len(dag["iv_nodes"]),
        "n_dv_nodes": len(dag["dv_nodes"]),
        "n_edges": len(dag["edges"]),
        "n_established": dag["n_established"],
        "n_contested": dag["n_contested"],
        "top_connected_ivs": sorted(
            [(iv, sum(1 for e in dag["edges"] if e["from"] == iv)) for iv in dag["iv_nodes"]],
            key=lambda x: x[1], reverse=True
        )[:10],
        "top_connected_dvs": sorted(
            [(dv, sum(1 for e in dag["edges"] if e["to"] == dv)) for dv in dag["dv_nodes"]],
            key=lambda x: x[1], reverse=True
        )[:10],
    }


def main():
    parser = argparse.ArgumentParser(description="T3 Belief DAG Visualization")
    parser.add_argument("--output", type=str, help="Output directory", default="data/reports")
    parser.add_argument("--format", choices=["mermaid", "dot", "both"], default="both")
    parser.add_argument("--min-confidence", type=float, default=0.6)
    parser.add_argument("--min-findings", type=int, default=2)
    args = parser.parse_args()

    print(f"Building T3 belief DAG (min_confidence={args.min_confidence}, min_findings={args.min_findings})...")
    dag, beliefs = build_dag(args.min_confidence, args.min_findings)

    if not dag:
        print("No DAG generated.")
        return

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n📊 DAG Summary:")
    print(f"   IV nodes: {len(dag['iv_nodes'])}")
    print(f"   DV nodes: {len(dag['dv_nodes'])}")
    print(f"   Edges: {len(dag['edges'])}")
    print(f"   Established: {dag['n_established']}")
    print(f"   Contested: {dag['n_contested']}")

    if args.format in ("mermaid", "both"):
        mermaid = to_mermaid(dag)
        mermaid_path = out_dir / "t3_belief_dag.md"
        with open(mermaid_path, "w") as f:
            f.write(f"# T3 Belief DAG\n\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")
            f.write(f"```mermaid\n{mermaid}\n```\n")
        print(f"   Mermaid: {mermaid_path}")

    if args.format in ("dot", "both"):
        dot = to_dot(dag)
        dot_path = out_dir / "t3_belief_dag.dot"
        with open(dot_path, "w") as f:
            f.write(dot)
        print(f"   DOT: {dot_path}")
        print(f"   Render: dot -Tpng {dot_path} -o {dot_path.with_suffix('.png')}")

    summary_path = out_dir / "t3_belief_dag.json"
    summary = to_json_summary(dag, beliefs)
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"   JSON: {summary_path}")


if __name__ == "__main__":
    main()
