"""
Tab Generators — Corpus-Grounded Content Producers for Card Tabs
=================================================================

These functions transform raw corpus data (extraction findings, cluster
statistics, theory taxonomy, template definitions) into CardTab objects.
They are designed to be registered with the CardGenerationOrchestrator's
TabGeneratorRegistry.

Generator contract:
    fn(card_type: CardType, entity_id: str, data: Dict, model: str) -> CardTab

Each generator:
1. Reads from source_data (the Dict passed by the orchestrator)
2. Produces prose grounded in actual corpus evidence (no hallucination)
3. Populates structured_data for downstream rendering (tables, diagrams)
4. Never calls an LLM — produces data-grounded scaffolds

CW may later wrap these generators with LLM refinement in the content
agents. These generators are the factual "grounding layer" that agents
build upon.

Author: AG (Antigravity)
Date: 2026-03-04

⚠️ CW REVIEW REQUIRED (MT-20): CW must review this file against
the content agent spec to ensure generator outputs are compatible
with the agent pipeline. See COORDINATION.md MT-20.
"""

from __future__ import annotations

import logging
from collections import Counter
from typing import Any, Dict, List, Optional

from src.qa.cards.card_schema import CardTab
from src.qa.cards.card_types import CardType, get_card_type_spec
from src.qa.source_data_auditor import audit_source_data, get_auditor

logger = logging.getLogger(__name__)


# ===========================================================================
# MECHANISM TAB GENERATOR
# ===========================================================================

def generate_mechanism_tab(
    card_type: CardType,
    entity_id: str,
    data: Dict[str, Any],
    model: str,
) -> CardTab:
    """Generate a mechanism tab from corpus data.

    Sources:
        - data['mechanism_chain']: List of steps [{from, to, process}]
        - data['theory_links']: List of theory names
        - data['neural_substrate']: str description
        - data['causal_pathway']: str
        - data['mediators']: List of mediating variables
        - data['moderators']: List of moderating variables

    For T2 Mechanism Cards, this is the core tab.
    """
    spec = get_card_type_spec(card_type)
    mechanism = data.get("mechanism_chain", data.get("mechanism", []))
    theory_links = data.get("theory_links", [])
    neural = data.get("neural_substrate", "")
    causal = data.get("causal_pathway", "")
    mediators = data.get("mediators", [])
    moderators = data.get("moderators", [])

    # Layer hooks: provenance, argumentation, interpretation, annotation
    # These fields are populated by CW's content agents from the
    # respective system layers. Generators format them if present.
    provenance = data.get("provenance", {})        # From provenance tracer
    argumentation = data.get("argumentation", {})  # From ArgumentationEngine
    interpretation = data.get("interpretation", {})  # From R₁-R₄ closures
    annotations = data.get("annotations", [])      # From annotation service

    # Build prose from available data
    sections = []

    # Section 1: Causal pathway
    if isinstance(mechanism, list) and mechanism:
        chain_str = _format_mechanism_chain(mechanism)
        sections.append(f"## Causal Pathway\n\n{chain_str}")
    elif causal:
        sections.append(f"## Causal Pathway\n\n{causal}")

    # Section 2: Neural substrate
    if neural:
        sections.append(f"## Neural Substrate\n\n{neural}")

    # Section 3: Mediators and moderators
    if mediators or moderators:
        med_mod = "## Mediating and Moderating Variables\n\n"
        if mediators:
            med_mod += "**Mediators**: " + ", ".join(str(m) for m in mediators) + "\n\n"
        if moderators:
            med_mod += "**Moderators**: " + ", ".join(str(m) for m in moderators)
        sections.append(med_mod)

    # Section 3b: Provenance — source quality and anchors
    if provenance:
        prov_section = "## Provenance\n\n"
        anchors = provenance.get("anchors", [])
        sq = provenance.get("source_quality")
        justification = provenance.get("justification_status", "")
        if anchors:
            prov_section += f"**Experiential anchors**: {len(anchors)} "
            prov_section += "(" + ", ".join(str(a) for a in anchors[:5]) + ")\n\n"
        if sq is not None:
            prov_section += f"**Source quality**: {sq:.2f}\n\n"
        if justification:
            prov_section += f"**Justification**: {justification}\n"
        sections.append(prov_section)

    # Section 3c: Argumentation — vulnerability and critique
    if argumentation:
        arg_section = "## Argumentation Analysis\n\n"
        vulnerabilities = argumentation.get("vulnerabilities", [])
        critique = argumentation.get("critique_summary", "")
        if vulnerabilities:
            arg_section += "**Known vulnerabilities**:\n"
            arg_section += "\n".join(f"- {v}" for v in vulnerabilities[:5]) + "\n\n"
        if critique:
            arg_section += f"{critique}\n"
        sections.append(arg_section)

    # Section 3d: Interpretation — R₁-R₄ closure results
    if interpretation:
        interp_section = "## Interpretive Context\n\n"
        closures = interpretation.get("closure_results", {})
        for op_name, result in closures.items():
            interp_section += f"**{op_name}**: {result}\n"
        sections.append(interp_section)

    # Section 3e: User annotations
    if annotations:
        ann_section = "## Community Annotations\n\n"
        for ann in annotations[:5]:
            if isinstance(ann, dict):
                ann_section += f"- {ann.get('content', ann)}\n"
            else:
                ann_section += f"- {ann}\n"
        sections.append(ann_section)

    # Section 4: Theory links
    if theory_links:
        theory_str = ", ".join(theory_links[:10])
        sections.append(
            f"## Theoretical Anchoring\n\nGrounded in: {theory_str}"
        )

    # Fallback: run completeness audit instead of silent [DRAFT]
    if not sections:
        audit = audit_source_data(entity_id, card_type.value, data)
        diagnostic = get_auditor().format_diagnostic(audit)
        if diagnostic:
            sections.append(diagnostic)
            _notify_overseer_gaps(entity_id, "mechanism", audit)
        else:
            sections.append(
                f"## Mechanism\n\nMechanism data for {entity_id} "
                f"fully audited — no gaps detected but no data available."
            )

    prose = "\n\n".join(sections)

    # Structured data for downstream rendering
    structured = {
        "mechanism_chain": mechanism if isinstance(mechanism, list) else [],
        "theory_links": theory_links,
        "mediators": mediators,
        "moderators": moderators,
        "has_provenance": bool(provenance),
        "has_argumentation": bool(argumentation),
        "has_interpretation": bool(interpretation),
        "n_annotations": len(annotations),
    }
    if spec.has_mechanism_diagram:
        structured["diagram_needed"] = True
        structured["diagram_type"] = "causal_dag"

    return CardTab(
        tab_name="mechanism",
        prose=prose,
        structured_data=structured,
    )


def _format_mechanism_chain(chain: List[Any]) -> str:
    """Format a mechanism chain into readable prose."""
    if not chain:
        return ""

    lines = []
    for i, step in enumerate(chain, 1):
        if isinstance(step, dict):
            from_c = step.get("from_construct", step.get("from", "?"))
            to_c = step.get("to_construct", step.get("to", "?"))
            process = step.get("process", step.get("via", ""))
            if process:
                lines.append(f"{i}. **{from_c}** → _{process}_ → **{to_c}**")
            else:
                lines.append(f"{i}. **{from_c}** → **{to_c}**")
        elif isinstance(step, str):
            lines.append(f"{i}. {step}")

    return "\n".join(lines)


# ===========================================================================
# DESIGN TAB GENERATOR
# ===========================================================================

def generate_design_tab(
    card_type: CardType,
    entity_id: str,
    data: Dict[str, Any],
    model: str,
) -> CardTab:
    """Generate a design implications tab from corpus data.

    Sources:
        - data['design_implications']: str or List
        - data['parameter_ranges']: Dict of parameter → {min, max, optimal}
        - data['application_examples']: List
        - data['design_guidelines']: List
        - data['dose_response']: Dict with threshold info
    """
    spec = get_card_type_spec(card_type)
    implications = data.get("design_implications", data.get("design", ""))
    params = data.get("parameter_ranges", {})
    examples = data.get("application_examples", [])
    guidelines = data.get("design_guidelines", [])
    dose = data.get("dose_response", {})

    sections = []

    # Section 1: Design implications
    if implications:
        if isinstance(implications, list):
            impl_str = "\n".join(f"- {i}" for i in implications)
            sections.append(f"## Design Implications\n\n{impl_str}")
        else:
            sections.append(f"## Design Implications\n\n{implications}")

    # Section 2: Parameter ranges (table)
    if params:
        table = _format_parameter_table(params)
        sections.append(f"## Parameter Ranges\n\n{table}")

    # Section 3: Dose-response
    if dose:
        threshold = dose.get("threshold", "not specified")
        relationship = dose.get("relationship", "unknown")
        sections.append(
            f"## Dose-Response Relationship\n\n"
            f"**Relationship**: {relationship}\n"
            f"**Threshold**: {threshold}"
        )

    # Section 4: Guidelines
    if guidelines:
        guide_str = "\n".join(f"- {g}" for g in guidelines[:10])
        sections.append(f"## Design Guidelines\n\n{guide_str}")

    # Section 5: Application examples
    if examples:
        ex_str = "\n".join(f"- {e}" for e in examples[:5])
        sections.append(f"## Application Examples\n\n{ex_str}")

    if not sections:
        audit = audit_source_data(entity_id, card_type.value, data)
        diagnostic = get_auditor().format_diagnostic(audit)
        if diagnostic:
            sections.append(diagnostic)
            _notify_overseer_gaps(entity_id, "design", audit)
        else:
            sections.append(
                f"## Design Implications\n\nDesign data for {entity_id} "
                f"fully audited — no gaps detected but no data available."
            )

    prose = "\n\n".join(sections)

    structured = {
        "parameter_ranges": params,
        "guidelines_count": len(guidelines),
        "examples_count": len(examples),
    }
    if spec.has_design_parameters:
        structured["parameter_table_needed"] = True

    return CardTab(
        tab_name="design",
        prose=prose,
        structured_data=structured,
    )


def _format_parameter_table(params: Dict) -> str:
    """Format parameter ranges as a markdown table."""
    if not params:
        return ""

    header = "| Parameter | Min | Max | Optimal | Unit |\n"
    header += "|-----------|-----|-----|---------|------|\n"
    rows = []
    for name, vals in params.items():
        if isinstance(vals, dict):
            mn = vals.get("min", "—")
            mx = vals.get("max", "—")
            opt = vals.get("optimal", "—")
            unit = vals.get("unit", "—")
            rows.append(f"| {name} | {mn} | {mx} | {opt} | {unit} |")
        else:
            rows.append(f"| {name} | — | — | {vals} | — |")

    return header + "\n".join(rows)


# ===========================================================================
# CONNECTIONS TAB GENERATOR
# ===========================================================================

def generate_connections_tab(
    card_type: CardType,
    entity_id: str,
    data: Dict[str, Any],
    model: str,
) -> CardTab:
    """Generate a connections tab from corpus data.

    Sources:
        - data['connections']: List of connected entity IDs
        - data['related_entities']: List[Dict] with type and relationship
        - data['parent_theories']: List of T1 framework names
        - data['child_beliefs']: List of T3 belief IDs
        - data['cross_level_constraints']: List of constraint descriptions
        - data['template_ids']: List of T2 template IDs
    """
    connections = data.get("connections", data.get("related_entities", []))
    parents = data.get("parent_theories", [])
    children = data.get("child_beliefs", [])
    cross_level = data.get("cross_level_constraints", [])
    templates = data.get("template_ids", [])

    sections = []

    # Section 1: Hierarchical position
    if parents or children:
        hier = "## Hierarchical Position\n\n"
        if parents:
            parent_str = ", ".join(str(p) for p in parents[:10])
            hier += f"**Parent frameworks**: {parent_str}\n\n"
        if children:
            hier += f"**Child beliefs**: {len(children)} T3 beliefs\n\n"
        if templates:
            hier += f"**Related templates**: {len(templates)} T2 templates"
        sections.append(hier)

    # Section 2: Cross-level constraints
    if cross_level:
        cl_str = "\n".join(f"- {c}" for c in cross_level[:10])
        sections.append(f"## Cross-Level Constraints\n\n{cl_str}")

    # Section 3: Related entities
    if connections:
        if isinstance(connections[0], dict) if connections else False:
            # Structured connections
            grouped = _group_connections(connections)
            conn_str = ""
            for rel_type, entities in grouped.items():
                conn_str += f"### {rel_type.title()}\n\n"
                conn_str += "\n".join(f"- {e}" for e in entities[:10])
                conn_str += "\n\n"
            sections.append(f"## Related Entities\n\n{conn_str}")
        else:
            conn_str = "\n".join(f"- {c}" for c in [str(c) for c in connections[:15]])
            sections.append(f"## Related Entities\n\n{conn_str}")

    if not sections:
        audit = audit_source_data(entity_id, card_type.value, data)
        diagnostic = get_auditor().format_diagnostic(audit)
        if diagnostic:
            sections.append(diagnostic)
            _notify_overseer_gaps(entity_id, "connections", audit)
        else:
            sections.append(
                f"## Connections\n\nConnection data for {entity_id} "
                f"fully audited — no gaps detected."
            )

    prose = "\n\n".join(sections)

    return CardTab(
        tab_name="connections",
        prose=prose,
        structured_data={
            "n_connections": len(connections),
            "n_parents": len(parents),
            "n_children": len(children),
            "n_cross_level": len(cross_level),
            "n_templates": len(templates),
        },
    )


def _group_connections(connections: List[Dict]) -> Dict[str, List[str]]:
    """Group connections by relationship type."""
    grouped: Dict[str, List[str]] = {}
    for c in connections:
        rel = c.get("relationship", c.get("type", "related"))
        name = c.get("name", c.get("id", str(c)))
        grouped.setdefault(rel, []).append(name)
    return grouped


# ===========================================================================
# DEBATE TAB GENERATOR
# ===========================================================================

def generate_debate_tab(
    card_type: CardType,
    entity_id: str,
    data: Dict[str, Any],
    model: str,
) -> CardTab:
    """Generate a debate tab from corpus data.

    Sources:
        - data['competing_accounts']: List[Dict] with position, evidence
        - data['tensions']: List of tension descriptions
        - data['contradicting_findings']: List of finding dicts
        - data['debate']: str (legacy free-text)
        - data['conflict_type']: str
        - data['resolution_scenarios']: List of possible resolutions
    """
    accounts = data.get("competing_accounts", [])
    tensions = data.get("tensions", [])
    contradictions = data.get("contradicting_findings", [])
    debate_text = data.get("debate", "")
    conflicts = data.get("conflict_type", "")
    resolutions = data.get("resolution_scenarios", [])

    sections = []

    # Section 1: Competing accounts
    if accounts:
        acct_str = ""
        for i, acct in enumerate(accounts[:5], 1):
            position = acct.get("position", acct.get("name", f"Account {i}"))
            evidence = acct.get("evidence", acct.get("support", ""))
            acct_str += f"### Position {i}: {position}\n\n"
            if evidence:
                acct_str += f"{evidence}\n\n"
        sections.append(f"## Competing Accounts\n\n{acct_str}")

    # Section 2: Tensions
    if tensions:
        ten_str = "\n".join(f"- {t}" for t in tensions[:10])
        sections.append(f"## Key Tensions\n\n{ten_str}")

    # Section 3: Contradicting findings
    if contradictions:
        contra_str = ""
        for c in contradictions[:5]:
            if isinstance(c, dict):
                paper = c.get("paper_id", "unknown")
                claim = c.get("content", c.get("claim", ""))
                contra_str += f"- **{paper}**: {claim}\n"
            else:
                contra_str += f"- {c}\n"
        sections.append(f"## Contradicting Evidence\n\n{contra_str}")

    # Section 4: Resolution scenarios
    if resolutions:
        res_str = "\n".join(f"- {r}" for r in resolutions[:5])
        sections.append(f"## Resolution Scenarios\n\n{res_str}")

    # Fallback to free text
    if not sections and debate_text:
        sections.append(f"## Debate\n\n{debate_text}")

    if not sections:
        audit = audit_source_data(entity_id, card_type.value, data)
        diagnostic = get_auditor().format_diagnostic(audit)
        if diagnostic:
            sections.append(diagnostic)
            _notify_overseer_gaps(entity_id, "debate", audit)
        else:
            sections.append(
                f"## Debate\n\nNo competing accounts identified for "
                f"{entity_id}. This finding may have consensus support."
            )

    prose = "\n\n".join(sections)

    return CardTab(
        tab_name="debate",
        prose=prose,
        structured_data={
            "n_competing_accounts": len(accounts),
            "n_tensions": len(tensions),
            "n_contradictions": len(contradictions),
            "n_resolutions": len(resolutions),
            "conflict_type": conflicts or None,
        },
    )


# ===========================================================================
# REGISTRATION FUNCTION
# ===========================================================================

def register_corpus_generators(orchestrator) -> None:
    """Register all corpus-grounded tab generators with the orchestrator.

    Call this after creating a CardGenerationOrchestrator:

        from src.qa.tab_generators import register_corpus_generators
        orch = CardGenerationOrchestrator(base_dir=".")
        register_corpus_generators(orch)

    This registers generators as defaults (apply to all card types).
    Type-specific overrides can be registered after this call.

    ⚠️ CW: When content agents are ready, wrap these generators
    with LLM refinement. The generators produce factual scaffolds;
    agents add insight, synthesis, and polished prose.
    """
    registry = orchestrator._tab_registry

    # Corpus-grounded generators for tabs not covered by builtins
    registry.register_default("mechanism", generate_mechanism_tab)
    registry.register_default("design", generate_design_tab)
    registry.register_default("connections", generate_connections_tab)
    registry.register_default("debate", generate_debate_tab)

    logger.info(
        "Registered 4 corpus-grounded tab generators: "
        "mechanism, design, connections, debate"
    )


# ===========================================================================
# OVERSEER NOTIFICATION
# ===========================================================================

def _notify_overseer_gaps(entity_id: str, tab_name: str, audit_result) -> None:
    """Notify the overseer of data completeness gaps.

    Reports gaps via report_pipeline_run() so the overseer tracks
    which entities have thin source data and which upstream services
    need to run.

    SC-SDA-4: Audit results are logged and can be aggregated by overseer.
    """
    try:
        from src.services.overseer import OverseerService
        overseer = OverseerService()
        overseer.report_pipeline_run(
            pipeline_id="source_data_completeness_audit",
            status="gap_detected" if audit_result.total_gaps > 0 else "complete",
            duration_ms=0,
            error=None,
            metadata={
                "entity_id": entity_id,
                "tab_name": tab_name,
                "coverage_score": audit_result.coverage_score,
                "total_gaps": audit_result.total_gaps,
                "critical_gaps": audit_result.critical_gaps,
                "warning_gaps": audit_result.warning_gaps,
                "is_generation_ready": audit_result.is_generation_ready,
                "gap_details": [g.to_dict() for g in audit_result.gaps],
            },
        )
    except Exception as e:
        # Overseer notification is best-effort — never block generation
        logger.debug(f"Overseer notification failed (non-blocking): {e}")
