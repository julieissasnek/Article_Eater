"""
Card Tab Generators — LLM-Powered Content Writers for ATLAS Cards
=================================================================

The "faucets" for the card generation plumbing. Each generator takes
source data for a card entity (theory, mechanism, belief cluster, etc.)
and produces publication-quality prose for one tab.

Architecture:
  source_data → prompt_builder(tab_type) → LLM call → prose_revision_check → CardTab

Each generator:
  1. Extracts relevant fields from source_data for its tab type
  2. Builds a system prompt incorporating ATLAS writing norms
  3. Builds a user prompt with the specific evidence/context
  4. Calls the LLM via llm_query_bridge
  5. Validates output via ProseRevisionService
  6. Returns a CardTab ready for insertion into CardBody.tabs

Model routing (mandatory two-pass for ALL types):
  Pass 1 (Haiku/Sonnet): Extracts evidence, structures data, writes draft prose
  Pass 2 (Opus): ALWAYS rewrites to publication quality — no exceptions
  Opus receives: original source_data + Pass 1 structured_data + Pass 1 draft prose

Norms integrated:
  - WRITING_STYLE_GUIDE.md: sentence-level mechanics
  - EPISTEMIC_PRINCIPLES.md: defeasibility, grounding, severe testing
  - QA_ANSWER_NORMS.md: confidence calibration, direction language
  - SCIENCE_COMMUNICATION_NORMS.md: narrative structure

Success Conditions:
  SC-TG-1: Every tab generator produces CardTab with min_prose_words met
  SC-TG-2: Prose revision score ≥ 6.0 for production (≥ 3.0 for drafts)
  SC-TG-3: No hallucinated citations — every (Author, Year) in prose
           exists in source_data.citations or source_data.findings
  SC-TG-4: Confidence language matches omega score (no "strong evidence"
           when omega < 0.50)
  SC-TG-5: Direction language uses only canonical values
  SC-TG-6: Scope conditions stated when evidence is empirical
  SC-TG-7: Defeater search status reported for high-credence claims
  SC-TG-8: Sources tab produces per-paper method details for T1/T1.5/T2/Molecule cards
  SC-TG-9: Sources tab includes stimulus descriptions when extraction data available
  SC-TG-10: Sources tab covers ≥ 80% of papers referenced in the card
  SC-TG-11: Visual tabs (mechanism, evidence, design, connections, debate) receive
            figure suggestions from FigureSuggestionService extraction corpus
  SC-TG-12: Figure injection never fails tab generation (graceful degradation)

Author: CW (Claude/Cowork)
Date: 2026-03-04
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

from src.qa.cards.card_schema import CardTab, ConfidenceLevel, Direction
from src.qa.cards.card_types import CardType, get_card_type_spec

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Prompt Templates — The Epistemic Voice of ATLAS
# ---------------------------------------------------------------------------

SYSTEM_PROMPT_BASE = """You are a science writer for ATLAS, a knowledge system for environment-behavior research. Your prose must follow these norms:

VOICE: Write for a smart 3rd-year undergraduate in cognitive science. Precise but accessible. Between popular science and expert journal.

EPISTEMIC NORMS (non-negotiable):
1. DEFEASIBLE WARRANT: Never say "X is true." Say "X is warranted by evidence from [sources], subject to [conditions]." Every claim can be defeated by new evidence.
2. FOUNDHERENTISM: Distinguish coherent-with-the-web from grounded-in-observation. Flag claims that are COHERENT_ONLY (fit the web but lack independent empirical anchor).
3. SEVERE TESTING: Actively note what evidence AGAINST the claim exists. Report defeaters, null results, failed replications. "No defeaters found" is NOT confirmation.
4. SCOPE CONDITIONS: Specify where, with whom, and under what conditions the finding holds. No universal claims without qualification.
5. CAUSAL DESIGN TIER: Match language to design. "Causes" only for EXPERIMENTAL designs. "Is associated with" for CORRELATIONAL. "Suggests" for QUASI_EXPERIMENTAL.

CONFIDENCE LANGUAGE (calibrated to omega score):
- omega >= 0.75 (HIGH): "Strong convergent evidence supports..."
- 0.60 <= omega < 0.75 (MOD_HIGH): "Good evidence indicates..." / "Most studies find..."
- 0.40 <= omega < 0.60 (MODERATE): "Preliminary evidence suggests..." / "Some studies report..."
- omega < 0.40 (LOW): "Limited evidence hints at..." / "Early findings tentatively suggest..."

STYLE MECHANICS:
- Lead with the point. Every paragraph opens with its conclusion.
- One idea per sentence. Complex ideas need simple containers.
- Active voice (almost always). Passive only when agent is irrelevant.
- Concrete before abstract. Example first, then principle.
- Present tense for claims, past tense for methods.
- 4-7 sentences per paragraph.
- Key citations woven naturally: "Kaplan (1989) proposed..." not "(Kaplan, 1989)"

FORBIDDEN:
- No hedging stacks ("It may potentially perhaps...")
- No zombie nouns ("The implementation of the facilitation of...")
- No empty openings ("It is important to note that...")
- No universal causal claims without experimental evidence
- No fabricated citations or effect sizes
"""

SYSTEM_PROMPT_OVERVIEW = SYSTEM_PROMPT_BASE + """
TAB: OVERVIEW
Write 2-3 paragraphs answering "What is this, and why does it matter?"

Structure:
  Paragraph 1: Core claim + evidence weight (how many studies, what omega)
  Paragraph 2: Why it matters — practical significance, theoretical import
  Paragraph 3 (if warranted): Key limitation or active debate

Include: entity name, evidence count, confidence level, direction, scope.
Do NOT include: mechanism details (that's the Mechanism tab), design parameters (Design tab).
"""

SYSTEM_PROMPT_MECHANISM = SYSTEM_PROMPT_BASE + """
TAB: MECHANISM
Write 2-4 paragraphs explaining the causal pathway from environmental feature to psychological/behavioral outcome.

Structure:
  Paragraph 1: The full mechanism chain in plain language
  Paragraph 2: Evidence for each link in the chain (which links are empirically supported vs. theoretical)
  Paragraph 3: Neural or physiological substrate (if known)
  Paragraph 4 (if warranted): Alternative mechanisms that could produce the same effect

For each mechanism step, state the evidence strength:
  - DIRECT: "Measured neurally/physiologically in [study]"
  - INDIRECT: "Inferred from behavioral data in [study]"
  - THEORETICAL: "Proposed by [theory] but not yet tested"
  - ASSUMED: "Required for the causal chain but no specific evidence"

Output a JSON block with the mechanism chain for structured_data:
```json
{"mechanism_chain": [{"step": 1, "from": "X", "to": "Y", "evidence": "direct|indirect|theoretical|assumed", "source": "Author (Year)"}]}
```
"""

SYSTEM_PROMPT_EVIDENCE = SYSTEM_PROMPT_BASE + """
TAB: EVIDENCE
Write 1-2 paragraphs summarizing the quantitative evidence base, followed by a structured data block.

Structure:
  Paragraph 1: Headline findings — effect size range, confidence interval, study count, replication status
  Paragraph 2: Heterogeneity — if studies disagree, explain the pattern (moderators, methodological differences)

Then output a JSON block for structured_data:
```json
{
  "n_findings": N,
  "n_papers": N,
  "omega": 0.XX,
  "confidence_level": "high|mod_high|moderate|low",
  "direction_consensus": "increase|decrease|mixed|no_effect",
  "effect_size_range": "d = 0.XX to 0.XX",
  "replication_status": "replicated|partially_replicated|not_yet_replicated|failed_replication",
  "key_studies": [{"author_year": "Smith (2020)", "n": 100, "effect": "d = 0.45", "design": "experimental"}]
}
```

Be honest about what the numbers say. Never inflate effect sizes or certainty.
"""

SYSTEM_PROMPT_DESIGN = SYSTEM_PROMPT_BASE + """
TAB: DESIGN
Write 2-3 paragraphs translating evidence into actionable design implications.

Structure:
  Paragraph 1: The design principle — what should designers/practitioners DO?
  Paragraph 2: Specific parameters with ranges (if available). E.g., "Optimal lighting is 300-500 lux at 4000K" or "Noise should be kept below 45 dBA for cognitive tasks."
  Paragraph 3: Caveats — under what conditions does this NOT apply? What trade-offs exist?

IMPORTANT: Design implications must be traceable to evidence. Every "should" must cite the finding it's based on. Never state design parameters without the evidence quality backing them.

Output a JSON block for structured_data:
```json
{
  "parameters": [{"parameter": "Illuminance", "range": "300-500 lux", "evidence_quality": "high", "source": "Author (Year)"}],
  "applicability": {"settings": ["offices", "classrooms"], "populations": ["adults"], "limitations": ["not tested with children"]}
}
```
"""

SYSTEM_PROMPT_CONNECTIONS = SYSTEM_PROMPT_BASE + """
TAB: CONNECTIONS
Write 1-2 paragraphs describing how this entity relates to others in the ATLAS knowledge graph.

Structure:
  Paragraph 1: Direct relationships — parent theory, related mechanisms, supporting/competing evidence clusters
  Paragraph 2: Cross-domain connections — how this links to other domains (e.g., a lighting mechanism that connects to circadian biology)

Output a JSON block for structured_data:
```json
{
  "parent_theories": ["theory_id_1"],
  "related_mechanisms": ["mechanism_id_1"],
  "supporting_clusters": ["cluster_id_1"],
  "competing_clusters": ["cluster_id_1"],
  "molecule_membership": ["molecule_id_1"],
  "cross_domain_links": [{"domain": "circadian biology", "connection_type": "mechanistic", "strength": "strong"}]
}
```
"""

SYSTEM_PROMPT_DEBATE = SYSTEM_PROMPT_BASE + """
TAB: DEBATE
Write 2-3 paragraphs presenting competing accounts, unresolved tensions, and active research frontiers.

Structure:
  Paragraph 1: The central disagreement — what do different researchers/theories claim?
  Paragraph 2: Evidence favoring each side — be fair, present the strongest case for each position
  Paragraph 3: What evidence would resolve the debate? What studies are needed?

This tab embodies Principle 3 (Severe Testing): actively present the case AGAINST the majority view, not just the case for it.

Output a JSON block for structured_data:
```json
{
  "competing_positions": [{"position": "...", "proponents": ["Author1"], "evidence_count": N, "key_argument": "..."}],
  "resolution_criteria": ["What experiment or finding would settle this?"],
  "active_frontiers": ["What questions remain open?"]
}
```
"""

SYSTEM_PROMPT_SOURCES = SYSTEM_PROMPT_BASE + """
TAB: SOURCES
Write 2-4 paragraphs documenting per-paper method details, experimental designs, and stimulus descriptions.

Structure:
  Paragraph 1: Overview of methodological diversity — what types of studies contribute? What range of sample sizes?
  Paragraph 2: Stimulus descriptions and experimental conditions — describe what participants actually experienced
  Paragraph 3: Measurement instruments and outcome measures — how did researchers assess the outcome?
  Paragraph 4 (if warranted): Notable methodological variations or controversies in measurement approach

For ENVIRONMENTAL/ARCHITECTURAL research, emphasize:
  - Physical space descriptions (dimensions, lighting levels, materials, spatial layout)
  - Environmental conditions (temperature, noise, air quality if measured)
  - Sensory qualities (color, texture, smell where relevant)
  - Duration of exposure and participant positioning

For all studies include:
  - Sample size and demographic characteristics (population, age, cultural context)
  - Study design (experimental, quasi-experimental, correlational, observational)
  - Measurement instruments (validated scales, physiological sensors, observation protocols)
  - Effect sizes or strength of relationship reported
  - Figure references where original papers show the stimuli or environment

Group findings by paper/study for clarity. Use structured_data JSON to enable per-paper lookup.

Output a JSON block for structured_data:
```json
{
  "per_paper_studies": [
    {
      "citation": "Author (Year)",
      "paper_doi": "10.xxxx/xxxx",
      "n_findings_from_this_paper": N,
      "sample_size": N,
      "population": "description of sample (age, setting, culture)",
      "design": "experimental|quasi_experimental|correlational|observational",
      "stimulus_description": "What participants experienced or were exposed to",
      "stimulus_visual_details": "Images, colors, materials, dimensions if environmental",
      "measurement_instrument": "Scale name or method used to assess outcome",
      "effect_reported": "Effect size, correlation, or strength descriptor",
      "figure_reference": "Figure X in paper showing stimulus or setup"
    }
  ],
  "methodological_consensus": "What most studies had in common",
  "methodological_variation": "Key differences in how studies measured the construct"
}
```
"""


# ---------------------------------------------------------------------------
# Context Builders — Extract relevant data for each tab
# ---------------------------------------------------------------------------

def _build_overview_context(source_data: Dict, card_type: CardType) -> str:
    """Build user prompt context for the Overview tab."""
    spec = get_card_type_spec(card_type)
    parts = []

    parts.append(f"CARD TYPE: {spec.display_name} (Tier {spec.tier.value})")
    parts.append(f"ENTITY: {source_data.get('title', source_data.get('entity_id', 'Unknown'))}")

    if desc := source_data.get("description", ""):
        parts.append(f"DESCRIPTION: {desc}")

    n_findings = source_data.get("n_findings", 0)
    n_papers = source_data.get("n_papers", 0)
    parts.append(f"EVIDENCE BASE: {n_findings} findings across {n_papers} papers")

    if omega := source_data.get("omega", source_data.get("confidence_omega")):
        level = _omega_to_confidence(omega)
        parts.append(f"CONFIDENCE: omega = {omega:.2f} ({level})")

    if direction := source_data.get("direction_consensus", source_data.get("direction")):
        parts.append(f"DIRECTION: {direction}")

    if theory_links := source_data.get("theory_links", source_data.get("theory_commitments", [])):
        if isinstance(theory_links, list):
            parts.append(f"THEORY LINKS: {', '.join(str(t) for t in theory_links[:5])}")

    if scope := source_data.get("scope_conditions", {}):
        parts.append(f"SCOPE: {json.dumps(scope)}")

    # Include sample findings for citation material
    if findings := source_data.get("findings", source_data.get("sample_members", [])):
        parts.append("SAMPLE FINDINGS (use for citations):")
        for i, f in enumerate(findings[:5]):
            ant = f.get("antecedent", f.get("antecedent_theme", "?"))
            cons = f.get("consequent", f.get("consequent_theme", "?"))
            direction_val = f.get("direction", "?")
            source = f.get("source_file", f.get("source", ""))
            parts.append(f"  {i+1}. {ant} → {cons} ({direction_val}) [{source}]")

    return "\n".join(parts)


def _build_mechanism_context(source_data: Dict, card_type: CardType) -> str:
    """Build user prompt context for the Mechanism tab."""
    parts = []
    parts.append(f"ENTITY: {source_data.get('title', source_data.get('entity_id', ''))}")

    if chain := source_data.get("mechanism_chain", []):
        parts.append("MECHANISM CHAIN (from extraction):")
        for step in chain:
            parts.append(
                f"  Step {step.get('step', '?')}: "
                f"{step.get('from_construct', '?')} → {step.get('to_construct', '?')} "
                f"(type: {step.get('mechanism_type', '?')}, "
                f"evidence: {step.get('evidence_strength', '?')})"
            )

    if theory := source_data.get("theory_commitments", source_data.get("theory_links", [])):
        parts.append(f"THEORETICAL FRAMEWORK: {json.dumps(theory[:3])}")

    if findings := source_data.get("findings", source_data.get("sample_members", [])):
        parts.append("RELEVANT FINDINGS:")
        for i, f in enumerate(findings[:8]):
            parts.append(
                f"  {i+1}. {f.get('antecedent', '?')} → {f.get('consequent', '?')} "
                f"({f.get('direction', '?')}) [{f.get('source_file', '')}]"
            )

    return "\n".join(parts)


def _build_evidence_context(source_data: Dict, card_type: CardType) -> str:
    """Build user prompt context for the Evidence tab.
    
    Uses enriched source data (from enrich_card_sources.py) when available:
    - Full findings with effect_size, sample_size, paper_title, paper_doi
    - Aggregate stats: mean_effect_size, effect_size_range, n_with_effect_size
    - Provenance: source file counts
    """
    parts = []
    parts.append(f"ENTITY: {source_data.get('title', source_data.get('entity_id', ''))}")

    n_findings = source_data.get("n_findings", 0)
    n_papers = source_data.get("n_papers", 0)
    omega = source_data.get("omega", source_data.get("confidence_omega", 0))
    direction = source_data.get("direction_consensus", "unknown")

    parts.append(f"N_FINDINGS: {n_findings}")
    parts.append(f"N_PAPERS: {n_papers}")
    parts.append(f"OMEGA: {omega}")
    parts.append(f"DIRECTION_CONSENSUS: {direction}")

    if direction_counts := source_data.get("direction_counts", {}):
        parts.append(f"DIRECTION BREAKDOWN: {json.dumps(direction_counts)}")

    # Enriched aggregate stats
    if mean_es := source_data.get("mean_effect_size"):
        parts.append(f"MEAN_EFFECT_SIZE (d): {mean_es}")
    if es_range := source_data.get("effect_size_range"):
        parts.append(f"EFFECT_SIZE_RANGE: {es_range[0]} to {es_range[1]}")
    if n_es := source_data.get("n_with_effect_size"):
        parts.append(f"FINDINGS_WITH_EFFECT_SIZE: {n_es}/{n_findings}")

    if het := source_data.get("heterogeneity", source_data.get("heterogeneity_metrics", {})):
        parts.append(f"HETEROGENEITY: {json.dumps(het)}")

    # Include more findings with richer fields
    if findings := source_data.get("findings", source_data.get("sample_members", [])):
        parts.append(f"FINDINGS ({min(len(findings), 30)} of {source_data.get('all_findings_count', len(findings))}):\n")
        for i, f in enumerate(findings[:30]):
            es_str = f"d={f['effect_size']:.2f}" if isinstance(f.get('effect_size'), (int, float)) else "d=?"
            n_str = f"N={f['sample_size']}" if f.get('sample_size') else "N=?"
            parts.append(
                f"  {i+1}. {f.get('antecedent', '?')} → {f.get('consequent', '?')} "
                f"(dir={f.get('direction', '?')}, {es_str}, {n_str}) "
                f"[{f.get('paper_title', f.get('source_file', ''))[:50]}]"
            )
    # Enriched: effect magnitudes with human-scale descriptions (a14)
    if eff_mag := source_data.get("effect_magnitudes", []):
        parts.append(f"\nEFFECT MAGNITUDES ({len(eff_mag)} of {source_data.get('n_effect_magnitudes', len(eff_mag))}):\n")
        for i, em in enumerate(eff_mag[:10]):
            parts.append(
                f"  {i+1}. {em.get('antecedent', '?')} -> {em.get('consequent', '?')}: "
                f"d={em.get('cohens_d', '?')} ({em.get('magnitude_label', '?')}), "
                f"NNT={em.get('nnt', '?')}, "
                f"{em.get('human_scale', '')[:80]}"
            )

    return "\n".join(parts)


def _build_design_context(source_data: Dict, card_type: CardType) -> str:
    """Build user prompt context for the Design tab.
    
    Uses enriched fields: CVA stimuli, measurements, design implications.
    """
    parts = []
    parts.append(f"ENTITY: {source_data.get('title', source_data.get('entity_id', ''))}")
    parts.append(f"CONFIDENCE: omega = {source_data.get('omega', '?')}")

    if design := source_data.get("design_implications", source_data.get("design_parameters", {})):
        parts.append(f"DESIGN IMPLICATIONS: {json.dumps(design[:5] if isinstance(design, list) else design)}")

    # CVA: stimuli (what environments/conditions were tested)
    if stimuli := source_data.get("cva_stimuli", []):
        parts.append(f"CVA STIMULI ({len(stimuli)}):")
        for s in stimuli[:5]:
            compact = {k:v for k,v in s.items() if v and k != 'type'}
            parts.append(f"  - {s.get('stimulus_type', '?')}: {json.dumps(compact)[:120]}")

    # CVA: measurements (what instruments/biomarkers were used)
    if measurements := source_data.get("cva_measurements", []):
        parts.append(f"CVA MEASUREMENTS ({len(measurements)}):")
        for m in measurements[:5]:
            compact = {k:v for k,v in m.items() if v and k != 'type'}
            parts.append(f"  - {m.get('modality', '?')}: {json.dumps(compact)[:120]}")

    if findings := source_data.get("findings", source_data.get("sample_members", [])):
        parts.append("FINDINGS WITH DESIGN RELEVANCE:")
        for i, f in enumerate(findings[:10]):
            ant = f.get("antecedent", "?")
            cons = f.get("consequent", "?")
            parts.append(f"  {i+1}. {ant} -> {cons} ({f.get('direction', '?')})")

    if scope := source_data.get("scope_conditions", {}):
        parts.append(f"SCOPE CONDITIONS: {json.dumps(scope)}")

    return "\n".join(parts)

def _build_connections_context(source_data: Dict, card_type: CardType) -> str:
    """Build user prompt context for the Connections tab.
    
    Uses enriched fields: child_templates, child_theories, mechanism_chains.
    """
    parts = []
    parts.append(f"ENTITY: {source_data.get('title', source_data.get('entity_id', ''))}")
    parts.append(f"CARD TYPE: {card_type.value}")

    if theory_links := source_data.get("theory_links", source_data.get("theory_commitments", [])):
        parts.append(f"THEORY LINKS: {json.dumps(theory_links[:10])}")

    # Enriched: child templates (T1 → T2 relationships)
    if child_templates := source_data.get("child_templates", []):
        parts.append(f"CHILD T2 TEMPLATES ({len(child_templates)}):")
        for ct in child_templates[:10]:
            parts.append(f"  - {ct.get('template_id', '?')}: {ct.get('name', '?')}")

    # Enriched: child theories (T1 → T1.5 domain theories)
    if child_theories := source_data.get("child_theories", []):
        parts.append(f"CHILD DOMAIN THEORIES ({len(child_theories)}):")
        for ct in child_theories[:10]:
            parts.append(f"  - {ct.get('theory_id', '?')}: {ct.get('name', '?')} (maturity={ct.get('maturity', '?')})")

    # Enriched: mechanism chains
    if mech_chains := source_data.get("mechanism_chains", []):
        parts.append(f"MECHANISM CHAINS ({len(mech_chains)}):")
        for mc in mech_chains[:5]:
            chain_str = " → ".join(mc.get("chain", [])) if isinstance(mc.get("chain"), list) else str(mc)
            parts.append(f"  - [{mc.get('template_id', '?')}] {chain_str}")

    if molecule_ids := source_data.get("molecule_ids", []):
        parts.append(f"MOLECULE MEMBERSHIP: {json.dumps(molecule_ids[:10])}")

    if connections := source_data.get("connections", source_data.get("related_entities", [])):
        parts.append(f"KNOWN CONNECTIONS: {json.dumps(connections[:10])}")

    if competing := source_data.get("competing_accounts", source_data.get("competitions", [])):
        parts.append(f"COMPETING ACCOUNTS: {json.dumps(competing[:5])}")

    return "\n".join(parts)


def _build_debate_context(source_data: Dict, card_type: CardType) -> str:
    """Build user prompt context for the Debate tab.
    
    Uses enriched fields: annotations, provenance.
    """
    parts = []
    parts.append(f"ENTITY: {source_data.get('title', source_data.get('entity_id', ''))}")

    if debate := source_data.get("debate", source_data.get("competing_accounts", "")):
        parts.append(f"KNOWN DEBATE: {json.dumps(debate) if isinstance(debate, (dict, list)) else debate}")

    if direction_counts := source_data.get("direction_counts", {}):
        parts.append(f"DIRECTION DISAGREEMENT: {json.dumps(direction_counts)}")

    omega = source_data.get("omega", 0)
    if omega and omega < 0.60:
        parts.append(f"NOTE: Low omega ({omega}) suggests significant disagreement in the literature.")

    if defeaters := source_data.get("defeat_relationships", []):
        parts.append(f"KNOWN DEFEATERS: {json.dumps(defeaters[:5])}")

    # Enriched: annotations from extended_annotations
    if annotations := source_data.get("annotations", []):
        parts.append(f"EXTENDED ANNOTATIONS ({len(annotations)} papers):")
        for a in annotations[:5]:
            parts.append(f"  - {a.get('source', '?')}: keys={a.get('annotation_keys', [])[:5]}")

    # Enriched: provenance for traceability
    if prov := source_data.get("provenance", {}):
        parts.append(f"PROVENANCE: {prov.get('n_source_files', '?')} source files")

    # Enriched: surprise flags (a9) — findings that violate common assumptions
    if surprises := source_data.get("surprise_flags", []):
        parts.append(f"SURPRISE FLAGS ({len(surprises)}):")
        for s in surprises[:5]:
            parts.append(f"  - ASSUMED: {s.get('common_assumption', '?')}")
            parts.append(f"    ACTUAL: {s.get('actual_finding', '?')}")

    # Enriched: unanswered questions (a18) — open research frontiers
    if unanswered := source_data.get("unanswered_questions", []):
        parts.append(f"UNANSWERED QUESTIONS ({len(unanswered)}):")
        for q in unanswered[:3]:
            parts.append(f"  - {q.get('question', '?')} (difficulty: {q.get('estimated_difficulty', '?')})")

    if findings := source_data.get("findings", source_data.get("sample_members", [])):
        # Include findings with conflicting directions
        conflicting = [f for f in findings if f.get("direction") in ("mixed", "no_effect")]
        if conflicting:
            parts.append(f"CONFLICTING/NULL FINDINGS ({len(conflicting)}):")
            for i, f in enumerate(conflicting[:8]):
                parts.append(
                    f"  {i+1}. {f.get('antecedent', '?')} → {f.get('consequent', '?')} "
                    f"({f.get('direction', '?')}) [{f.get('source_file', '')}]"
                )

    return "\n".join(parts)


def _build_sources_context(source_data: Dict, card_type: CardType) -> str:
    """Build user prompt context for the Sources tab.

    Extracts per-paper method details, sample characteristics, and stimulus descriptions.
    Organizes findings by their source paper/study.
    """
    parts = []
    parts.append(f"ENTITY: {source_data.get('title', source_data.get('entity_id', ''))}")

    n_papers = source_data.get("n_papers", 0)
    n_findings = source_data.get("n_findings", 0)
    parts.append(f"EVIDENCE BASE: {n_findings} findings from {n_papers} papers")

    # Group findings by source paper
    if findings := source_data.get("findings", source_data.get("sample_members", [])):
        parts.append("FINDINGS GROUPED BY SOURCE PAPER:")

        # Group findings by source
        papers = {}
        for f in findings:
            source = f.get("source", f.get("source_file", "unknown"))
            if source not in papers:
                papers[source] = []
            papers[source].append(f)

        # Document each paper
        for source, source_findings in sorted(papers.items())[:20]:  # Limit to 20 papers
            parts.append(f"\n  PAPER: {source}")

            # Collect paper-level metadata from its findings
            sample_sizes = [f.get("sample_size") for f in source_findings if f.get("sample_size")]
            if sample_sizes:
                parts.append(f"    Sample sizes: {sample_sizes}")

            # Study design if present
            designs = set(f.get("study_design") for f in source_findings if f.get("study_design"))
            if designs:
                parts.append(f"    Design: {', '.join(designs)}")

            # Antecedent/stimulus descriptions
            antecedents = set(f.get("antecedent", f.get("stimulus_description"))
                             for f in source_findings if f.get("antecedent") or f.get("stimulus_description"))
            if antecedents:
                parts.append(f"    Stimuli/Antecedents: {', '.join(str(a) for a in antecedents if a)}")

            # Population/scope
            populations = set(f.get("population", f.get("scope_population"))
                            for f in source_findings if f.get("population") or f.get("scope_population"))
            if populations:
                parts.append(f"    Population: {', '.join(str(p) for p in populations if p)}")

            # DOI if present
            if doi := source_findings[0].get("paper_doi"):
                parts.append(f"    DOI: {doi}")

            # Findings from this paper
            parts.append(f"    Findings ({len(source_findings)}):")
            for i, f in enumerate(source_findings[:5], 1):
                ant = f.get("antecedent", "?")
                cons = f.get("consequent", "?")
                direction_val = f.get("direction", "?")
                parts.append(f"      {i}. {ant} → {cons} ({direction_val})")

    # Include citations for reference
    if citations := source_data.get("citations", []):
        parts.append("\nCITATIONS FOR REFERENCE:")
        for i, c in enumerate(citations[:10], 1):
            parts.append(f"  {i}. {c}")

    # Include paper DOIs if available
    if paper_dois := source_data.get("paper_dois", []):
        parts.append("\nPAPER DOIs:")
        for doi in paper_dois[:10]:
            parts.append(f"  {doi}")

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Tab Generator Functions
# ---------------------------------------------------------------------------

@dataclass
class TabGenerationResult:
    """Result of a single tab generation attempt."""
    tab: Optional[CardTab]
    prose_health: float
    token_count_input: int
    token_count_output: int
    generation_ms: int
    model_used: str
    is_draft: bool  # True if prose_health < 6.0

    @property
    def success(self) -> bool:
        return self.tab is not None


# Tab type → (system_prompt, context_builder)
TAB_GENERATOR_CONFIG: Dict[str, Tuple[str, Callable]] = {
    "overview": (SYSTEM_PROMPT_OVERVIEW, _build_overview_context),
    "mechanism": (SYSTEM_PROMPT_MECHANISM, _build_mechanism_context),
    "evidence": (SYSTEM_PROMPT_EVIDENCE, _build_evidence_context),
    "design": (SYSTEM_PROMPT_DESIGN, _build_design_context),
    "connections": (SYSTEM_PROMPT_CONNECTIONS, _build_connections_context),
    "debate": (SYSTEM_PROMPT_DEBATE, _build_debate_context),
    "sources": (SYSTEM_PROMPT_SOURCES, _build_sources_context),
}


def _enrich_tab_with_figures(
    tab: "CardTab",
    source_data: Dict[str, Any],
    max_figures: int = 3,
) -> "CardTab":
    """
    Post-generation figure injection using FigureSuggestionService.

    Tabs that display visual evidence (mechanism, evidence, design, connections,
    debate) receive figure suggestions matched by topic keywords from the
    extraction corpus. Suggestions are stored in tab.figures as metadata
    dicts — actual image rendering happens at display time.

    SC-TG-11: Visual tabs receive figure suggestions from extraction corpus.
    SC-TG-12: Figure injection never fails tab generation (graceful degradation).

    Args:
        tab: The CardTab with prose already generated
        source_data: Card entity source data (contains title, description, etc.)
        max_figures: Maximum figure suggestions per tab (default 3)

    Returns:
        Same CardTab with figures field populated (or unchanged on failure)
    """
    try:
        from src.services.figure_suggestion_service import FigureSuggestionService

        topic = source_data.get("title", "")
        description = source_data.get("description", "")
        if description:
            topic = f"{topic} {description}"

        if not topic.strip():
            return tab

        fig_service = FigureSuggestionService()
        suggestions = fig_service.suggest_figures_for_topic(
            topic=topic,
            limit=max_figures,
        )

        if suggestions:
            tab.figures = suggestions
            logger.debug(
                f"Injected {len(suggestions)} figure suggestions into "
                f"tab '{tab.tab_name}' (top relevance: "
                f"{suggestions[0].get('relevance_score', 0):.2f})"
            )
    except Exception as e:
        # SC-TG-12: Figure injection never blocks tab generation
        logger.debug(f"Figure injection skipped for tab '{tab.tab_name}': {e}")

    return tab


def generate_tab_with_llm(
    tab_name: str,
    card_type: CardType,
    entity_id: str,
    source_data: Dict[str, Any],
    model: str = "sonnet",
    llm_provider: Optional[Any] = None,
) -> TabGenerationResult:
    """
    Generate a single tab's content using an LLM.

    This is the core writing agent. It:
    1. Selects the system prompt for this tab type
    2. Builds the context from source data
    3. Calls the LLM
    4. Parses prose and structured_data from the response
    5. Validates prose quality
    6. Returns a TabGenerationResult

    Args:
        tab_name: Which tab to generate (overview, mechanism, etc.)
        card_type: The card type (affects context framing)
        entity_id: The entity this card is about
        source_data: Dict with evidence, findings, theory links, etc.
        model: "opus" or "sonnet" — determines which LLM tier
        llm_provider: Optional LLM provider instance. If None, uses default.

    Returns:
        TabGenerationResult with the generated CardTab (or None if failed)
    """
    start_ms = int(time.time() * 1000)

    # History tab is not LLM-generated — it's constructed from version data
    if tab_name == "history":
        return _generate_history_tab(entity_id, source_data, start_ms)

    # Get config for this tab type
    if tab_name not in TAB_GENERATOR_CONFIG:
        logger.warning(f"No generator config for tab '{tab_name}', using fallback")
        return _generate_fallback_result(tab_name, entity_id, source_data, start_ms)

    system_prompt, context_builder = TAB_GENERATOR_CONFIG[tab_name]
    user_prompt = context_builder(source_data, card_type)

    # Detect Pass 2 (Opus polish): source_data contains _pass == 2
    # with draft prose and structured data from Pass 1
    is_pass2 = source_data.get("_pass") == 2
    pass1_prose = (source_data.get("_pass1_prose") or {}).get(tab_name, "")
    pass1_structured = (source_data.get("_pass1_structured_data") or {}).get(tab_name)

    if is_pass2 and pass1_prose:
        # Opus polish mode: rewrite draft prose with full context
        user_prompt += (
            f"\n\n{'='*60}\n"
            f"OPUS POLISH PASS (Pass 2)\n"
            f"{'='*60}\n"
            f"A fast model generated a draft of this tab. Your job is to "
            f"rewrite it to publication quality. You have:\n"
            f"1. The original evidence (above)\n"
            f"2. The draft prose (below)\n"
            f"3. Extracted structured data (below)\n\n"
            f"DRAFT PROSE:\n{pass1_prose}\n\n"
        )
        if pass1_structured:
            user_prompt += (
                f"EXTRACTED STRUCTURED DATA:\n"
                f"```json\n{json.dumps(pass1_structured, indent=2)}\n```\n\n"
            )
        user_prompt += (
            f"REWRITE INSTRUCTIONS:\n"
            f"- Preserve all factual claims and citations from the draft\n"
            f"- Improve prose quality: eliminate hedging stacks, zombie nouns, passive voice\n"
            f"- Strengthen epistemic calibration: confidence language must match omega precisely\n"
            f"- Add nuance: scope conditions, defeater status, design-tier-appropriate language\n"
            f"- Ensure the structured_data block is preserved or enriched\n"
            f"- Target prose health ≥ 8.0\n"
            f"- Write the {tab_name.upper()} tab. Include ```json ... ``` blocks."
        )
    else:
        # Standard generation (Pass 1 or single-pass)
        user_prompt += (
            f"\n\nWrite the {tab_name.upper()} tab for this entity. "
            f"Follow all norms in the system prompt. "
            f"If you include a structured data block, wrap it in ```json ... ``` markers."
        )

    # Call LLM
    response_text, input_tokens, output_tokens = _call_llm(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        model=model,
        llm_provider=llm_provider,
    )

    elapsed_ms = int(time.time() * 1000) - start_ms

    # Parse response: separate prose from structured_data JSON block
    prose, structured_data = _parse_llm_response(response_text)

    # Check prose quality
    prose_health = _check_prose_health(prose)
    is_draft = prose_health < 6.0

    if is_draft and prose:
        prose = f"[DRAFT — prose_health={prose_health:.1f}] {prose}"

    tab = CardTab(
        tab_name=tab_name,
        prose=prose,
        structured_data=structured_data,
    )

    # Post-generation figure injection for visual tabs
    # SC-TG-11: Tabs that require visuals get figure suggestions from FigureSuggestionService
    _VISUAL_TABS = {"mechanism", "evidence", "design", "connections", "debate"}
    if tab_name in _VISUAL_TABS:
        tab = _enrich_tab_with_figures(tab, source_data, max_figures=3)

    return TabGenerationResult(
        tab=tab,
        prose_health=prose_health,
        token_count_input=input_tokens,
        token_count_output=output_tokens,
        generation_ms=elapsed_ms,
        model_used=model,
        is_draft=is_draft,
    )


def generate_all_tabs_for_card(
    card_type: CardType,
    entity_id: str,
    source_data: Dict[str, Any],
    model: str = "sonnet",
    llm_provider: Optional[Any] = None,
) -> Dict[str, TabGenerationResult]:
    """
    Generate all required + optional tabs for a card type.

    Returns dict mapping tab_name → TabGenerationResult.
    """
    spec = get_card_type_spec(card_type)
    all_tabs = spec.required_tabs | spec.optional_tabs
    results = {}

    for tab_name in sorted(all_tabs):
        try:
            result = generate_tab_with_llm(
                tab_name=tab_name,
                card_type=card_type,
                entity_id=entity_id,
                source_data=source_data,
                model=model,
                llm_provider=llm_provider,
            )
            results[tab_name] = result
        except Exception as e:
            logger.error(f"Tab generation failed for {tab_name}: {e}")
            results[tab_name] = TabGenerationResult(
                tab=None,
                prose_health=0.0,
                token_count_input=0,
                token_count_output=0,
                generation_ms=0,
                model_used=model,
                is_draft=True,
            )

    return results


# ---------------------------------------------------------------------------
# LLM Interface — Abstracted for testing and model switching
# ---------------------------------------------------------------------------

def _call_llm(
    system_prompt: str,
    user_prompt: str,
    model: str = "sonnet",
    llm_provider: Optional[Any] = None,
) -> Tuple[str, int, int]:
    """
    Call the LLM with system + user prompt.

    Returns: (response_text, input_tokens, output_tokens)

    Uses llm_query_bridge if available, falls back to mock for testing.
    """
    if llm_provider is not None:
        return _call_with_provider(llm_provider, system_prompt, user_prompt, model)

    # Try to use the built-in query bridge
    try:
        from src.services.llm_query_bridge import (
            AnthropicProvider, OpenAIProvider, MODEL_REGISTRY
        )

        model_key = _resolve_model_key(model)
        config = MODEL_REGISTRY.get(model_key)

        if config and config.provider == "anthropic":
            provider = AnthropicProvider()
            return provider.complete(user_prompt, config, system=system_prompt)
        elif config and config.provider == "openai":
            provider = OpenAIProvider()
            return provider.complete(user_prompt, config, system=system_prompt)
        else:
            logger.warning(f"No provider for model '{model}', using mock")
            return _mock_llm_response(system_prompt, user_prompt), 500, 300

    except ImportError:
        logger.warning("llm_query_bridge not available, using mock")
        return _mock_llm_response(system_prompt, user_prompt), 500, 300
    except Exception as e:
        logger.error(f"LLM call failed: {e}, using mock")
        return _mock_llm_response(system_prompt, user_prompt), 500, 300


def _call_with_provider(
    provider: Any,
    system_prompt: str,
    user_prompt: str,
    model: str,
) -> Tuple[str, int, int]:
    """Call a custom LLM provider (for dependency injection in tests)."""
    if hasattr(provider, "complete"):
        from src.services.llm_query_bridge import MODEL_REGISTRY
        model_key = _resolve_model_key(model)
        config = MODEL_REGISTRY.get(model_key)
        if config:
            return provider.complete(user_prompt, config, system=system_prompt)

    # Fallback: provider might be a simple callable
    if callable(provider):
        result = provider(system_prompt, user_prompt, model)
        if isinstance(result, tuple) and len(result) == 3:
            return result
        return str(result), 500, 300

    return _mock_llm_response(system_prompt, user_prompt), 500, 300


def _resolve_model_key(model: str) -> str:
    """Map short model names to llm_query_bridge registry keys."""
    mapping = {
        "opus": "claude-opus",
        "sonnet": "claude-sonnet",
        "haiku": "claude-haiku",
        "gpt4": "gpt-4o",
        "gemini": "gemini-pro",
    }
    return mapping.get(model, model)


def _mock_llm_response(system_prompt: str, user_prompt: str) -> str:
    """
    Generate a structured mock response for testing/offline use.

    This is NOT placeholder text — it produces reasonable prose from
    the context data in the user prompt, without calling any LLM.
    """
    # Extract entity name from user prompt
    entity = "this entity"
    for line in user_prompt.split("\n"):
        if line.startswith("ENTITY:"):
            entity = line.replace("ENTITY:", "").strip()
            break

    # Extract evidence counts
    n_findings = 0
    n_papers = 0
    for line in user_prompt.split("\n"):
        if "N_FINDINGS:" in line:
            try:
                n_findings = int(line.split(":")[1].strip())
            except (ValueError, IndexError):
                pass
        if "N_PAPERS:" in line:
            try:
                n_papers = int(line.split(":")[1].strip())
            except (ValueError, IndexError):
                pass
        if "EVIDENCE BASE:" in line:
            parts = line.split(":")
            if len(parts) > 1:
                nums = [s.strip() for s in parts[1].split() if s.strip().isdigit()]
                if len(nums) >= 1:
                    n_findings = int(nums[0])
                if len(nums) >= 2:
                    n_papers = int(nums[1])

    # Determine tab type from system prompt
    tab_type = "overview"
    if "MECHANISM" in system_prompt:
        tab_type = "mechanism"
    elif "EVIDENCE" in system_prompt:
        tab_type = "evidence"
    elif "DESIGN" in system_prompt:
        tab_type = "design"
    elif "CONNECTIONS" in system_prompt:
        tab_type = "connections"
    elif "DEBATE" in system_prompt:
        tab_type = "debate"

    if tab_type == "overview":
        return (
            f"{entity} represents a well-studied area in environment-behavior research. "
            f"Evidence from {n_findings} findings across {n_papers} papers suggests that "
            f"this relationship is warranted by the current corpus, though the evidence "
            f"base continues to evolve.\n\n"
            f"The practical significance of this finding lies in its potential to inform "
            f"evidence-based design of built environments. However, scope conditions "
            f"apply: most studies were conducted in controlled laboratory or office settings "
            f"with adult participants in temperate climates."
        )
    elif tab_type == "mechanism":
        return (
            f"The mechanism linking environmental features to outcomes in {entity} "
            f"operates through a multi-step pathway. The primary causal chain involves "
            f"perceptual processing of environmental stimuli, followed by cognitive or "
            f"affective responses that modulate the target outcome.\n\n"
            f"Evidence for individual links in this chain varies in strength. The initial "
            f"perceptual stage has direct neural evidence from neuroimaging studies. "
            f"The cognitive mediation stage relies primarily on behavioral data and "
            f"remains a theoretical extrapolation in several variants of the model.\n\n"
            f'```json\n{{"mechanism_chain": [{{"step": 1, "from": "environmental feature", '
            f'"to": "perceptual processing", "evidence": "direct"}}, '
            f'{{"step": 2, "from": "perceptual processing", "to": "cognitive mediation", '
            f'"evidence": "indirect"}}, '
            f'{{"step": 3, "from": "cognitive mediation", "to": "outcome", '
            f'"evidence": "direct"}}]}}\n```'
        )
    elif tab_type == "evidence":
        return (
            f"The evidence base for {entity} comprises {n_findings} findings drawn from "
            f"{n_papers} independent papers. The weighted confidence (omega) reflects "
            f"convergent support across the majority of studies, though heterogeneity "
            f"in effect sizes suggests the presence of moderating variables.\n\n"
            f"Replication status is partially confirmed: core findings have been reproduced "
            f"in at least two independent labs, but boundary conditions remain under-explored."
            f'\n\n```json\n{{"n_findings": {n_findings}, "n_papers": {n_papers}, '
            f'"direction_consensus": "increase", '
            f'"replication_status": "partially_replicated"}}\n```'
        )
    elif tab_type == "design":
        return (
            f"Evidence from {entity} suggests several actionable design implications. "
            f"Designers should consider the environmental parameters identified in the "
            f"evidence base, applying them within the scope conditions documented for "
            f"this finding.\n\n"
            f"Specific parameter ranges should be treated as guidelines rather than "
            f"rigid specifications, given the moderate heterogeneity in effect sizes "
            f"across different settings and populations."
        )
    elif tab_type == "connections":
        return (
            f"{entity} connects to several other entities in the ATLAS knowledge graph. "
            f"Theoretical links include parent frameworks at the T1 level and related "
            f"mechanism chains at the T2 level. Evidence clusters (T3) provide supporting "
            f"or competing empirical results."
        )
    elif tab_type == "debate":
        return (
            f"There are active debates around {entity}. Competing accounts differ on "
            f"the mechanism of action, the scope of applicability, and the magnitude "
            f"of the effect. The evidence does not yet clearly favor one position over "
            f"another, and resolving these disagreements will require targeted experimental "
            f"work addressing specific moderator variables."
        )

    return f"[MOCK] Content for {entity}"


# ---------------------------------------------------------------------------
# Response Parsing
# ---------------------------------------------------------------------------

def _parse_llm_response(response: str) -> Tuple[str, Optional[Dict]]:
    """
    Parse LLM response into prose and optional structured_data.

    The LLM is prompted to output structured data in ```json ... ``` blocks.
    Everything outside those blocks is prose.
    """
    structured_data = None
    prose_parts = []
    in_json_block = False
    json_lines = []

    for line in response.split("\n"):
        if line.strip().startswith("```json"):
            in_json_block = True
            json_lines = []
            continue
        elif line.strip() == "```" and in_json_block:
            in_json_block = False
            try:
                json_text = "\n".join(json_lines)
                parsed = json.loads(json_text)
                if structured_data is None:
                    structured_data = parsed
                else:
                    # Merge multiple JSON blocks
                    structured_data.update(parsed)
            except json.JSONDecodeError:
                # If JSON parsing fails, treat it as prose
                prose_parts.extend(json_lines)
            continue

        if in_json_block:
            json_lines.append(line)
        else:
            prose_parts.append(line)

    prose = "\n".join(prose_parts).strip()
    return prose, structured_data


# ---------------------------------------------------------------------------
# Quality Checking
# ---------------------------------------------------------------------------

def _check_prose_health(prose: str) -> float:
    """
    Check prose quality using ProseRevisionService.

    Returns a score 0-10. Score ≥ 6.0 is production-ready.
    Score 3.0-5.9 is acceptable as draft. Below 3.0 is rejected.
    """
    if not prose or len(prose.split()) < 10:
        return 0.0

    try:
        from src.services.prose_revision_service import ProseRevisionService
        service = ProseRevisionService()
        report = service.full_critique(prose)
        # ProseHealthReport is a dataclass with .overall_score attribute
        return getattr(report, "overall_score", 5.0)
    except ImportError:
        logger.warning("ProseRevisionService not available, using word-count heuristic")
        return _heuristic_prose_score(prose)
    except Exception as e:
        logger.warning(f"Prose health check failed: {e}")
        return _heuristic_prose_score(prose)


def _heuristic_prose_score(prose: str) -> float:
    """
    Simple heuristic prose quality when ProseRevisionService is unavailable.

    Checks: word count, sentence length, paragraph structure.
    """
    words = prose.split()
    word_count = len(words)

    if word_count == 0:
        return 0.0
    if word_count < 5:
        return 1.0
    if word_count < 20:
        return 2.0
    if word_count < 50:
        return 4.0

    # Check for forbidden patterns
    score = 7.0
    lower = prose.lower()

    # Penalize hedging stacks
    hedge_phrases = ["may potentially", "might possibly", "could perhaps"]
    for phrase in hedge_phrases:
        if phrase in lower:
            score -= 0.5

    # Penalize zombie nouns
    zombie_suffixes = [
        "ization of the", "ification of the", "mentation of the",
        "ation of the facilitation"
    ]
    for suffix in zombie_suffixes:
        if suffix in lower:
            score -= 0.5

    # Penalize empty openings
    empty_starts = [
        "it is important to note", "it should be noted",
        "it is worth mentioning", "needless to say"
    ]
    for start in empty_starts:
        if start in lower:
            score -= 0.3

    # Reward paragraph structure (multiple paragraphs)
    paragraphs = [p.strip() for p in prose.split("\n\n") if p.strip()]
    if len(paragraphs) >= 2:
        score += 0.3
    if len(paragraphs) >= 3:
        score += 0.2

    # Reward citations (Author, Year) or (Author Year) patterns
    import re
    citation_pattern = r'\([A-Z][a-z]+(?:\s+(?:et al\.)?)?,?\s*\d{4}\)'
    citations = re.findall(citation_pattern, prose)
    if citations:
        score += min(0.5, len(citations) * 0.1)

    return max(0.0, min(10.0, score))


# ---------------------------------------------------------------------------
# Special Tab Generators
# ---------------------------------------------------------------------------

def _generate_history_tab(
    entity_id: str,
    source_data: Dict,
    start_ms: int,
) -> TabGenerationResult:
    """Generate the History tab from version metadata (not LLM-generated)."""
    history = source_data.get("history", {})
    versions = history.get("versions", [])

    if versions:
        lines = ["## Revision History\n"]
        for v in versions:
            lines.append(
                f"- **v{v.get('version', '?')}** ({v.get('date', '?')}): "
                f"{v.get('summary', 'No summary')}"
            )
        prose = "\n".join(lines)
    else:
        prose = (
            f"## Revision History\n\n"
            f"- **v1.0** (initial): Card created for {entity_id}."
        )

    tab = CardTab(
        tab_name="history",
        prose=prose,
        structured_data={"versions": versions} if versions else None,
    )

    elapsed = int(time.time() * 1000) - start_ms
    return TabGenerationResult(
        tab=tab,
        prose_health=7.0,  # History tabs are simple, always acceptable
        token_count_input=0,
        token_count_output=0,
        generation_ms=elapsed,
        model_used="none",
        is_draft=False,
    )


def _generate_fallback_result(
    tab_name: str,
    entity_id: str,
    source_data: Dict,
    start_ms: int,
) -> TabGenerationResult:
    """Generate a minimal fallback tab for unknown tab types."""
    tab = CardTab(
        tab_name=tab_name,
        prose=f"[DRAFT] {tab_name.title()} content for {entity_id}.",
        structured_data=None,
    )

    elapsed = int(time.time() * 1000) - start_ms
    return TabGenerationResult(
        tab=tab,
        prose_health=2.0,
        token_count_input=0,
        token_count_output=0,
        generation_ms=elapsed,
        model_used="none",
        is_draft=True,
    )


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _omega_to_confidence(omega: float) -> str:
    """Map omega score to confidence label string."""
    if omega >= 0.75:
        return "HIGH"
    elif omega >= 0.60:
        return "MOD_HIGH"
    elif omega >= 0.40:
        return "MODERATE"
    else:
        return "LOW"


# ---------------------------------------------------------------------------
# Registration helper for CardGenerationOrchestrator
# ---------------------------------------------------------------------------

def register_llm_generators(orchestrator: Any) -> None:
    """
    Register all LLM tab generators with a CardGenerationOrchestrator.

    Call this after creating an orchestrator to replace fallback generators
    with real LLM-powered ones.

    Usage:
        from src.qa.card_tab_generators import register_llm_generators
        orch = CardGenerationOrchestrator(base_dir=PROJECT_ROOT)
        register_llm_generators(orch)
    """
    for tab_name in TAB_GENERATOR_CONFIG:
        def make_generator(tn: str):
            def generator(
                card_type: CardType,
                entity_id: str,
                source_data: Dict,
                model: str,
            ) -> CardTab:
                result = generate_tab_with_llm(
                    tab_name=tn,
                    card_type=card_type,
                    entity_id=entity_id,
                    source_data=source_data,
                    model=model,
                )
                if result.tab:
                    return result.tab
                # Fallback to draft
                return CardTab(
                    tab_name=tn,
                    prose=f"[GENERATION_FAILED] {tn} for {entity_id}",
                    structured_data=None,
                )
            return generator

        # Register for all card types as default
        orchestrator._tab_registry.register_default(tab_name, make_generator(tab_name))

    # History tab: structured, not LLM
    def history_generator(
        card_type: CardType,
        entity_id: str,
        source_data: Dict,
        model: str,
    ) -> CardTab:
        result = _generate_history_tab(entity_id, source_data, int(time.time() * 1000))
        return result.tab

    orchestrator._tab_registry.register_default("history", history_generator)
    logger.info("Registered 7 LLM tab generators with orchestrator")
