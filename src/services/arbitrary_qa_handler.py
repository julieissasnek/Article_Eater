"""
Arbitrary QA Handler — AI-Routed Question Answering
=====================================================

Handles arbitrary user questions about the system's knowledge through:

1. **Question Classification**: Categorizes questions into types (catalog, 
   evidence, comparison, mechanism, definition, meta) using pattern matching
   + optional cheap AI fallback.

2. **Static Handlers**: For catalog/browse queries ("show all theories"),
   returns pre-computed structured answers from KnowledgeCatalog.

3. **AI-Routed Handlers**: For complex/novel questions, builds a context
   package from relevant annotations and sends to cheapest sufficient LLM.

4. **Response Formatting**: Produces structured, list-rich answers with
   theory/framework distinctions, cultural variants, evidence counts.

Panel Deliberation Notes (Search/NLP/Erotetic/Argumentation/Rhetoric):
- Search Expert: Use inverted index over annotations for recall
- NLP Expert: Question type classification determines handler routing
- Erotetic Logic: Questions have presuppositions; validate them first
- Argumentation: Show warrant structure, not just conclusions
- Rhetoric: Progressive disclosure — headline → summary → detail

Usage:
    from src.services.arbitrary_qa_handler import ArbitraryQAHandler
    handler = ArbitraryQAHandler()
    response = handler.answer("Show me all the theories in this system")
"""

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent


# =============================================================================
# Question Classification
# =============================================================================

class QuestionType:
    """Types of questions the system can handle."""
    CATALOG_THEORIES = "catalog_theories"      # "show me all theories"
    CATALOG_CULTURAL = "catalog_cultural"      # "show cultural differences"
    CATALOG_MOLECULES = "catalog_molecules"    # "what molecules exist?"
    CATALOG_OUTCOMES = "catalog_outcomes"      # "what outcomes do you track?"
    CATALOG_METHODS = "catalog_methods"        # "what measurement methods?"
    CATALOG_CVA = "catalog_cva"               # "what are CVA dimensions?"
    
    # A9-A18 enabled queries
    SURPRISE = "surprise"                      # "what's surprising about X?"
    DISPUTE = "dispute"                        # "is X controversial?"
    DESIGN_PARAMS = "design_params"            # "what design params for X?"
    FRONTIER_GAPS = "frontier_gaps"            # "what don't we know about X?"
    HOOKS = "hooks"                            # "why should I care about X?"
    EFFECT_SIZE = "effect_size"                # "how big is the effect of X?"
    CROSS_DOMAIN = "cross_domain"              # "what connects X to Y?"
    HISTORY = "history"                        # "what's the history of X?"
    
    EVIDENCE_FOR = "evidence_for"             # "what evidence supports X?"
    EVIDENCE_AGAINST = "evidence_against"     # "what evidence contradicts X?"
    COMPARISON = "comparison"                  # "how does X compare to Y?"
    MECHANISM = "mechanism"                    # "how does X cause Y?"
    DEFINITION = "definition"                  # "what is X?"
    DESIGN_GUIDANCE = "design_guidance"        # "how should I design X?"
    
    META_COVERAGE = "meta_coverage"           # "what do you know about X?"
    META_GAPS = "meta_gaps"                    # "what don't you know?"
    META_SYSTEM = "meta_system"               # "how does this system work?"
    
    ARBITRARY = "arbitrary"                    # Anything else → AI route


QUESTION_PATTERNS = [
    # Catalog queries
    (QuestionType.CATALOG_THEORIES, re.compile(
        r'(?:show(?:\s+me)?|list|what\s+are|tell\s+me|give\s+me)\s+(?:all\s+)?(?:the\s+)?'
        r'(?:theor|framework|model|T1|T2|T1\.5|molecule)', re.I)),
    (QuestionType.CATALOG_CULTURAL, re.compile(
        r'(?:show(?:\s+me)?|list|what)\s+(?:are\s+)?(?:all\s+)?(?:the\s+)?'
        r'(?:cultur|cross[\s-]?cultur|cultural\s+differ)', re.I)),
    (QuestionType.CATALOG_MOLECULES, re.compile(
        r'(?:show|list|what)\s+(?:are\s+)?(?:all\s+)?(?:the\s+)?'
        r'(?:molecule|T2\s+(?:model|theor))', re.I)),
    (QuestionType.CATALOG_OUTCOMES, re.compile(
        r'(?:show|list|what)\s+(?:are\s+)?(?:all\s+)?(?:the\s+)?'
        r'(?:outcome|dependent\s+variable|what\s+.*\b(?:measure|track))', re.I)),
    (QuestionType.CATALOG_METHODS, re.compile(
        r'(?:show|list|what)\s+(?:are\s+)?(?:all\s+)?(?:the\s+)?'
        r'(?:measurement|method|modali|instrument)', re.I)),
    (QuestionType.CATALOG_CVA, re.compile(
        r'(?:what\s+are\s+)?(?:the\s+)?(?:CVA|constraint|valuation)\s+'
        r'(?:dimension|axis|variable)', re.I)),
    
    # A9-A18 queries (before general evidence/mechanism to get priority)
    (QuestionType.SURPRISE, re.compile(
        r'(?:what.s|what\s+is)\s+(?:the\s+most\s+)?(?:surpris|counterintuitiv|unexpect)', re.I)),
    (QuestionType.SURPRISE, re.compile(
        r'(?:surpris|counterintuitiv|unexpect)\s+(?:finding|result|fact)', re.I)),
    (QuestionType.DISPUTE, re.compile(
        r'(?:is\s+.+\s+controversial|do\s+researchers?\s+(?:agree|disagree)|what.s\s+controversial)', re.I)),
    (QuestionType.DISPUTE, re.compile(
        r'(?:debat|disput|controvers|disagree)', re.I)),
    (QuestionType.DESIGN_PARAMS, re.compile(
        r'(?:what\s+(?:CCT|lux|height|temperature|param)|specific\s+(?:design|number)|how\s+(?:much|many|bright|high|warm)\s+should)', re.I)),
    (QuestionType.FRONTIER_GAPS, re.compile(
        r'(?:what\s+(?:don.t|do\s+not)\s+we\s+know|unanswered\s+question|research\s+(?:gap|need|frontier)|what\s+.*\s+missing)', re.I)),
    (QuestionType.HOOKS, re.compile(
        r'(?:why\s+(?:should\s+I|does\s+.+\s+matter)|tell\s+me\s+(?:a\s+)?story|hook|why\s+care)', re.I)),
    (QuestionType.EFFECT_SIZE, re.compile(
        r'(?:how\s+big\s+(?:is|are)|effect\s+size|how\s+(?:strong|large|significant)\s+is)', re.I)),
    (QuestionType.CROSS_DOMAIN, re.compile(
        r'(?:what\s+connect|how\s+(?:does?|is)\s+.+\s+(?:relate|connect)\s+to|'
        r'cross[\s-]?domain|interdisciplin|analog|bridge\s+between|connection\s+between)', re.I)),
    (QuestionType.HISTORY, re.compile(
        r'(?:histor|origin|when\s+(?:was|did)\s+.+\s+(?:develop|creat|propos)|'
        r'who\s+(?:came\s+up|develop|creat|found)|background\s+of|evolution\s+of)', re.I)),
    
    # Evidence queries
    (QuestionType.EVIDENCE_FOR, re.compile(
        r'(?:what\s+)?evidence\s+(?:support|for|confirm|verif)', re.I)),
    (QuestionType.EVIDENCE_AGAINST, re.compile(
        r'(?:what\s+)?evidence\s+(?:against|contradict|refut|weaken)', re.I)),
    
    # Comparison
    (QuestionType.COMPARISON, re.compile(
        r'(?:how\s+does?\s+.+\s+(?:compare|differ|vs|versus)|'
        r'(?:compare|differences?\s+between)\s+)', re.I)),
    
    # Mechanism
    (QuestionType.MECHANISM, re.compile(
        r'(?:how\s+does?|why\s+does?|what\s+(?:mechanism|cause|explain))', re.I)),
    
    # Definition
    (QuestionType.DEFINITION, re.compile(
        r'(?:what\s+is\s+(?:a\s+|the\s+)?|define\s+|explain\s+(?:what\s+)?)', re.I)),
    
    # Design guidance
    (QuestionType.DESIGN_GUIDANCE, re.compile(
        r'(?:how\s+(?:should|can|to)\s+(?:I\s+)?design|design\s+(?:for|guidanc|recommend))', re.I)),
    
    # Meta queries
    (QuestionType.META_COVERAGE, re.compile(
        r'(?:what\s+do\s+you\s+know|what\s+.*\s+cover|how\s+much\s+.*\s+know)', re.I)),
    (QuestionType.META_GAPS, re.compile(
        r'(?:what\s+(?:don.t|do\s+not)\s+you\s+know|what.*gaps|what.*missing)', re.I)),
    (QuestionType.META_SYSTEM, re.compile(
        r'(?:how\s+does\s+this\s+system|what\s+is\s+this\s+system|how\s+.*\s+work)', re.I)),
]


def classify_question(text: str) -> Tuple[str, float]:
    """Classify question type using pattern matching.
    
    Returns: (question_type, confidence)
    """
    for qtype, pattern in QUESTION_PATTERNS:
        if pattern.search(text):
            return (qtype, 0.85)
    
    return (QuestionType.ARBITRARY, 0.3)


# =============================================================================
# Answer Formatters
# =============================================================================

def format_theory_catalog(catalog) -> Dict[str, Any]:
    """Format comprehensive theory catalog answer."""
    theories = catalog.get_theories()
    frameworks = catalog.get_frameworks()
    molecules = catalog.get_molecules()
    
    # Build structured response
    sections = []
    
    # T1 Theories
    theory_lines = []
    for t in theories:
        evidence_note = f" ({t['evidence_count']} linked beliefs)" if t.get('evidence_count') else ""
        theory_lines.append(
            f"**{t['name']}** ({t['authors']}, {t['year']}){evidence_note}\n"
            f"  {t['summary']}"
        )
    sections.append({
        "heading": f"T1 Theories — Foundational ({len(theories)})",
        "description": "Major theoretical frameworks with broad empirical support",
        "items": theory_lines,
    })
    
    # T1.5 Frameworks
    fw_lines = [f"**{fw['name']}**: {fw['summary']}" for fw in frameworks]
    sections.append({
        "heading": f"T1.5 Frameworks — Bridging ({len(frameworks)})",
        "description": "Domain-specific frameworks connecting theories to design",
        "items": fw_lines,
    })
    
    # T2 Molecules
    mol_lines = [f"**{m['name']}** (`{m['id']}`): {m['summary']}" for m in molecules]
    sections.append({
        "heading": f"T2 Molecules — Computational ({len(molecules)})",
        "description": "Formal models with testable quantitative predictions",
        "items": mol_lines,
    })
    
    return {
        "question_type": QuestionType.CATALOG_THEORIES,
        "headline": f"This system contains {len(theories)} T1 theories, "
                    f"{len(frameworks)} T1.5 frameworks, and {len(molecules)} T2 molecules.",
        "sections": sections,
        "total_items": len(theories) + len(frameworks) + len(molecules),
        "follow_ups": [
            "How does Attention Restoration Theory compare to Stress Recovery Theory?",
            "What evidence supports the Biophilia Hypothesis?",
            "Show me all cultural differences this system recognizes.",
        ],
    }


def format_cultural_catalog(catalog) -> Dict[str, Any]:
    """Format cultural differences answer."""
    cultural = catalog.get_cultural_differences()
    
    sections = []
    for cd in cultural:
        variant_lines = [
            f"**{v['culture']}**: {v['pattern']}" for v in cd["variants"]
        ]
        evidence = cd.get("evidence_files", 0)
        sections.append({
            "heading": cd["dimension"],
            "cva_impact": cd["cva_impact"],
            "evidence_count": evidence,
            "items": variant_lines,
        })
    
    total_variants = sum(len(cd["variants"]) for cd in cultural)
    
    return {
        "question_type": QuestionType.CATALOG_CULTURAL,
        "headline": f"This system recognizes cultural differences across "
                    f"{len(cultural)} dimensions with {total_variants} cultural variants.",
        "sections": sections,
        "follow_ups": [
            "How do beauty judgments differ between Japanese and Western cultures?",
            "What is the CVA impact of cultural differences on prospect-refuge?",
            "Show me all theories in this system.",
        ],
    }


def format_molecule_catalog(catalog) -> Dict[str, Any]:
    """Format molecule catalog answer."""
    molecules = catalog.get_molecules()
    
    items = []
    for m in molecules:
        preds = ", ".join(str(p)[:60] for p in (m.get("key_predictions") or [])[:2])
        items.append(
            f"**{m['name']}** (`{m['id']}`)\n"
            f"  {m['summary']}"
            + (f"\n  Key predictions: {preds}" if preds else "")
        )
    
    return {
        "question_type": QuestionType.CATALOG_MOLECULES,
        "headline": f"This system contains {len(molecules)} T2 molecules — "
                    f"formal computational models with testable predictions.",
        "sections": [{"heading": "T2 Molecules", "items": items}],
        "follow_ups": [
            "How does the Beauty as Compression molecule work?",
            "What predictions does the Rasa Aesthetic States model make?",
        ],
    }


def format_outcome_catalog(catalog) -> Dict[str, Any]:
    """Format outcome domains answer."""
    outcomes = catalog.get_outcome_domains()
    
    items = []
    for domain, info in outcomes.get("domains", {}).items():
        sample = ", ".join(info["sample"][:3])
        items.append(f"**{domain}** ({info['count']} terms): {sample}...")
    
    return {
        "question_type": QuestionType.CATALOG_OUTCOMES,
        "headline": f"This system tracks {outcomes.get('total_terms', 0)} outcome terms "
                    f"across {len(outcomes.get('domains', {}))} domains.",
        "sections": [{"heading": "Outcome Domains", "items": items}],
    }


def format_methods_catalog(catalog) -> Dict[str, Any]:
    """Format measurement methods answer."""
    modalities = catalog.get_measurement_modalities()
    
    items = [f"**{m['name']}** (`{m['id']}`)" for m in modalities]
    
    return {
        "question_type": QuestionType.CATALOG_METHODS,
        "headline": f"This system recognizes {len(modalities)} measurement modalities.",
        "sections": [{"heading": "Measurement Modalities", "items": items}],
    }


def format_cva_catalog(catalog) -> Dict[str, Any]:
    """Format CVA dimensions answer."""
    dims = catalog.get_cva_dimensions()
    
    return {
        "question_type": QuestionType.CATALOG_CVA,
        "headline": f"The CVA system operates on {len(dims['constraints'])} constraint "
                    f"dimensions and {len(dims['valuations'])} valuation axes.",
        "sections": [
            {"heading": "Constraint Dimensions", "items": dims["constraints"]},
            {"heading": "Valuation Axes", "items": dims["valuations"]},
        ],
    }


# =============================================================================
# Extended Annotation Formatters (A9-A18)
# =============================================================================

EXT_ANN_DIR = PROJECT_ROOT / "data" / "extended_annotations"
AUTO_ANN_DIR = PROJECT_ROOT / "data" / "annotations"  # Auto-generated A9/A13/A14

def _load_ext_annotations(keyword: str = "") -> List[Dict]:
    """Load and optionally filter extended annotation files."""
    results = []
    if not EXT_ANN_DIR.exists():
        return results
    for fp in EXT_ANN_DIR.glob("*.json"):
        if fp.name.startswith("_"):
            continue
        try:
            with open(fp) as f:
                data = json.load(f)
            if keyword:
                text = json.dumps(data).lower()
                if keyword.lower() not in text:
                    continue
            results.append(data)
        except Exception:
            pass
    return results

def _load_seed_file(name: str) -> List[Dict]:
    """Load a seed file (_disputes.json, _hooks.json, etc.)."""
    path = EXT_ANN_DIR / name
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return []


def format_surprise_answer(question: str) -> Dict[str, Any]:
    """Answer 'what's surprising about X?' queries using A9 annotations."""
    topic = re.sub(r'(?:what.s|what\s+is)\s+(?:the\s+most\s+)?(?:surprising|counterintuitive|unexpected)\s+(?:about|regarding|for)?\s*', '', question, flags=re.I).strip('? ')
    
    # Load from auto-generated A9 data (primary) + extended annotations (secondary)
    surprises = []
    a9_path = AUTO_ANN_DIR / "a9_surprise_flags.json"
    if a9_path.exists():
        try:
            a9_data = json.load(open(a9_path))
            for s in a9_data:
                if topic and topic.lower() not in json.dumps(s).lower():
                    continue
                surprises.append(s)
        except Exception:
            pass
    
    # Also check extended annotations for manually curated surprises
    all_anns = _load_ext_annotations(topic if topic else "")
    for ann in all_anns:
        for s in ann.get("surprises", []):
            s["source"] = ann.get("target_id", "")
            surprises.append(s)
    
    surprises.sort(key=lambda x: x.get("surprise_level", 0), reverse=True)
    
    items = []
    for s in surprises[:10]:
        items.append(
            f"**Surprise** (level: {s.get('surprise_level', 0):.1f}, "
            f"group: {s.get('group_size', '?')} studies)\n"
            f"  Common assumption: {s.get('common_assumption', '')}\n"
            f"  Actual finding: {s.get('actual_finding', '')[:150]}"
        )
    
    topic_label = topic or "the research corpus"
    return {
        "question_type": "surprise",
        "headline": f"Found {len(surprises)} surprising findings" + (f" related to '{topic_label}'" if topic else "") + ".",
        "sections": [{"heading": f"Surprising Findings ({len(items)} shown)", "items": items or ["No surprises found for this topic."]}],
        "total_count": len(surprises),
        "follow_ups": [
            "Is this finding controversial?",
            "How big is this effect?",
            "What don't we know about this topic?",
        ],
    }


def format_dispute_answer(question: str) -> Dict[str, Any]:
    """Answer controversy/dispute queries using A11 annotations."""
    disputes = _load_seed_file("_disputes.json")
    
    items = []
    for d in disputes:
        positions = " vs ".join(
            f"{p['position']} ({', '.join(p.get('proponents', [])[:2])})" 
            for p in d.get("positions", [])[:2]
        )
        items.append(
            f"**{d['claim']}** [{d.get('status', 'active')}]\n"
            f"  {positions}\n"
            f"  *Would resolve with*: {d.get('what_would_resolve', 'Unknown')}"
        )
    
    return {
        "question_type": "dispute",
        "headline": f"This system tracks {len(disputes)} active scientific disputes.",
        "sections": [{"heading": "Active Disputes", "items": items or ["No disputes cataloged."]}],
        "follow_ups": [
            "What's surprising about this topic?",
            "Show me all theories in this system.",
        ],
    }


def format_design_params_answer(question: str) -> Dict[str, Any]:
    """Answer design parameter queries using A10 annotations."""
    all_anns = _load_ext_annotations("")
    params = []
    for ann in all_anns:
        for p in ann.get("design_implications", []):
            if p.get("parameter") and p["parameter"] != "recommendation":
                p["source"] = ann.get("target_id", "")
                params.append(p)
    
    # Group by parameter type
    by_type = {}
    for p in params:
        ptype = p.get("parameter", "unknown")
        by_type.setdefault(ptype, []).append(p)
    
    sections = []
    for ptype, items in sorted(by_type.items(), key=lambda x: len(x[1]), reverse=True)[:5]:
        sample = items[:3]
        section_items = [
            f"{p.get('value', '?')} {p.get('unit', '')} — {p.get('context', '')[:80]}"
            for p in sample
        ]
        sections.append({
            "heading": f"{ptype.replace('_', ' ').title()} ({len(items)} values found)",
            "items": section_items,
        })
    
    return {
        "question_type": "design_params",
        "headline": f"Found {len(params)} design parameter values across {len(by_type)} parameter types.",
        "sections": sections or [{"heading": "Parameters", "items": ["No specific parameters found."]}],
        "follow_ups": ["What evidence supports these recommendations?"],
    }


def format_frontier_answer(question: str) -> Dict[str, Any]:
    """Answer 'what don't we know?' queries using A18 annotations."""
    questions = _load_seed_file("_unanswered.json")
    
    items = []
    for q in questions:
        items.append(
            f"**{q['question']}** [{q.get('estimated_difficulty', '?')}]\n"
            f"  *Why it matters*: {q.get('why_important', '')}\n"
            f"  *What it would take*: {q.get('what_would_it_take', '')}"
        )
    
    return {
        "question_type": "frontier_gaps",
        "headline": f"This system has identified {len(questions)} frontier questions.",
        "sections": [{"heading": "Unanswered Research Questions", "items": items or ["No gaps cataloged."]}],
        "follow_ups": [
            "Is this topic controversial?",
            "Show me all theories.",
        ],
    }


def format_hooks_answer(question: str) -> Dict[str, Any]:
    """Answer 'why should I care?' with narrative hooks (A17)."""
    hooks = _load_seed_file("_hooks.json")
    
    items = []
    for h in hooks:
        items.append(
            f"**{h.get('theory', 'Unknown')}** [{h.get('hook_type', '').replace('_', ' ')}]\n"
            f"  \"{h['hook']}\""
        )
    
    return {
        "question_type": "hooks",
        "headline": f"{len(hooks)} narrative entry points into this system's knowledge.",
        "sections": [{"heading": "Narrative Hooks", "items": items or ["No hooks available."]}],
        "follow_ups": [
            "Tell me more about this theory.",
            "What's surprising about this?",
        ],
    }


def format_effect_size_answer(question: str) -> Dict[str, Any]:
    """Answer 'how big is this effect?' using A14 annotations."""
    # Load from auto-generated A14 data (primary)
    effects = []
    a14_path = AUTO_ANN_DIR / "a14_effect_magnitude.json"
    if a14_path.exists():
        try:
            effects = json.load(open(a14_path))
        except Exception:
            pass
    
    # Also check extended annotations
    all_anns = _load_ext_annotations("")
    for ann in all_anns:
        for e in ann.get("effect_magnitudes", []):
            e["source"] = ann.get("target_id", "")
            effects.append(e)
    
    # Group by significance
    by_sig = {}
    for e in effects:
        sig = e.get("practical_significance", e.get("magnitude_label", "unknown"))
        by_sig.setdefault(sig, []).append(e)
    
    items = []
    for sig in ["massive", "very large", "large", "medium", "small", "negligible"]:
        group = by_sig.get(sig, [])
        if group:
            example = group[0]
            items.append(
                f"**{sig.title()}** ({len(group)} findings)\n"
                f"  {example.get('human_scale', '')}\n"
                f"  Example: d={example.get('cohens_d', '?')}, "
                f"NNT={example.get('nnt', '?')}: {example.get('nnt_explanation', '')}"
            )
    
    return {
        "question_type": "effect_size",
        "headline": f"Found {len(effects)} effect size measurements across the corpus.",
        "sections": [{"heading": "Effect Sizes by Practical Significance", "items": items or ["No effect sizes found."]}],
        "follow_ups": [
            "What's the strongest evidence in this system?",
            "What's surprising about these effects?",
        ],
    }


def format_cross_domain_answer(question: str) -> Dict[str, Any]:
    """Answer cross-domain connection queries using A15 annotations."""
    connections = []
    a15_path = AUTO_ANN_DIR / "a15_cross_domain_connections.json"
    if a15_path.exists():
        try:
            connections = json.load(open(a15_path))
        except Exception:
            pass
    
    items = []
    for c in connections:
        items.append(
            f"**{c.get('domain_a', '?')} ↔ {c.get('domain_b', '?')}** "
            f"[{c.get('connection_type', '').replace('_', ' ')}]\n"
            f"  {c.get('description', '')}\n"
            f"  _Design implication_: {c.get('design_implication', 'N/A')}"
        )
    
    return {
        "question_type": "cross_domain",
        "headline": f"Found {len(connections)} cross-domain connections.",
        "sections": [{"heading": "Cross-Domain Bridges", "items": items or ["No cross-domain connections available yet."]}],
        "follow_ups": [
            "What's surprising about these connections?",
            "How should I design for these interactions?",
        ],
    }


def format_history_answer(question: str) -> Dict[str, Any]:
    """Answer historical context queries using A16 annotations."""
    histories = []
    a16_path = AUTO_ANN_DIR / "a16_historical_contexts.json"
    if a16_path.exists():
        try:
            histories = json.load(open(a16_path))
        except Exception:
            pass
    
    items = []
    for h in histories:
        items.append(
            f"**{h.get('theory', '?')}** ({h.get('year_range', '?')})\n"
            f"  Problem: {h.get('historical_problem', 'N/A')}\n"
            f"  Replaced: {h.get('predecessor', 'N/A')}\n"
            f"  Turning point: {h.get('key_turning_point', 'N/A')}\n"
            f"  Status: _{h.get('current_status', 'unknown')}_"
        )
    
    return {
        "question_type": "history",
        "headline": f"Historical context for {len(histories)} theories.",
        "sections": [{"heading": "Theory Origins & Evolution", "items": items or ["No historical context available yet."]}],
        "follow_ups": [
            "What's the current status of this theory?",
            "What replaced this approach?",
        ],
    }


# =============================================================================
# AI Context Builder (for arbitrary questions)
# =============================================================================

def build_ai_context(question: str, catalog, max_tokens: int = 2000) -> str:
    """Build a focused context package for AI answering.
    
    Searches catalog + annotations to find relevant knowledge,
    then formats as a compact context prompt.
    """
    # Search catalog for relevant items
    results = catalog.search(question.lower())
    
    context_parts = []
    
    # Add matching theories
    if results.get("theories"):
        context_parts.append("RELEVANT THEORIES:")
        for t in results["theories"][:3]:
            context_parts.append(f"- {t['name']} ({t['authors']}): {t['summary']}")
    
    # Add matching frameworks
    if results.get("frameworks"):
        context_parts.append("\nRELEVANT FRAMEWORKS:")
        for fw in results["frameworks"][:3]:
            context_parts.append(f"- {fw['name']}: {fw['summary']}")
    
    # Add matching molecules
    if results.get("molecules"):
        context_parts.append("\nRELEVANT MOLECULES:")
        for m in results["molecules"][:3]:
            context_parts.append(f"- {m['name']} ({m['id']})")
    
    # Add matching cultural info
    if results.get("cultural"):
        context_parts.append("\nCULTURAL CONTEXT:")
        for cd in results["cultural"][:2]:
            context_parts.append(f"- {cd['dimension']}:")
            for v in cd["variants"][:3]:
                context_parts.append(f"  - {v['culture']}: {v['pattern']}")
    
    # If nothing matched, provide system overview
    if not any(results.values()):
        context_parts.append("SYSTEM OVERVIEW:")
        context_parts.append(f"- 6 T1 theories, 8 T1.5 frameworks, 18 T2 molecules")
        context_parts.append(f"- 103 outcome terms across 8 domains")
        context_parts.append(f"- 8 CVA constraint dimensions, 8 valuation axes")
        context_parts.append(f"- 6 cultural difference dimensions")
        context_parts.append(f"- 717 extracted images, 17,330+ annotated findings")
    
    # Truncate to max tokens (rough estimate: 4 chars per token)
    context = "\n".join(context_parts)
    if len(context) > max_tokens * 4:
        context = context[:max_tokens * 4]
    
    return context


def build_ai_prompt(question: str, context: str) -> str:
    """Build the prompt for AI answering."""
    return f"""You are a knowledge assistant for an architectural cognition research system.
Answer the user's question using ONLY the context provided below. Be specific and cite theories/frameworks/molecules by name.

If the question asks for lists, provide well-structured lists distinguishing:
- T1 Theories (foundational, named after researchers)
- T1.5 Frameworks (bridging theory to design)
- T2 Molecules (formal computational models)

If asking about cultural differences, list each dimension with specific cultural variants.

Be concise but thorough. Use bullet points. If the context doesn't contain enough information, say so.

CONTEXT:
{context}

USER QUESTION: {question}

ANSWER:"""


# =============================================================================
# Main Handler
# =============================================================================

class ArbitraryQAHandler:
    """Handles arbitrary user questions about the system's knowledge.
    
    Uses pattern-based classification for catalog queries (free, instant)
    and AI routing for complex/novel questions (cheap API call).
    """
    
    def __init__(self, llm_fn=None):
        """
        Args:
            llm_fn: Optional LLM function with signature (prompt: str) -> str.
                    If None, AI-routed questions return context + prompt for external processing.
        """
        from src.services.knowledge_catalog import KnowledgeCatalog
        self.catalog = KnowledgeCatalog()
        self.llm_fn = llm_fn
        self._stats = {"classified": 0, "ai_routed": 0, "catalog_served": 0}
    
    def answer(self, question: str) -> Dict[str, Any]:
        """Answer any question about the system's knowledge.
        
        Returns structured response dict with:
        - question_type: classified type
        - headline: one-line answer
        - sections: detailed structured content
        - follow_ups: suggested follow-up questions
        - ai_generated: True if AI was used
        """
        # Classify
        qtype, confidence = classify_question(question)
        self._stats["classified"] += 1
        
        # Route to handler
        handler_map = {
            QuestionType.CATALOG_THEORIES: lambda: format_theory_catalog(self.catalog),
            QuestionType.CATALOG_CULTURAL: lambda: format_cultural_catalog(self.catalog),
            QuestionType.CATALOG_MOLECULES: lambda: format_molecule_catalog(self.catalog),
            QuestionType.CATALOG_OUTCOMES: lambda: format_outcome_catalog(self.catalog),
            QuestionType.CATALOG_METHODS: lambda: format_methods_catalog(self.catalog),
            QuestionType.CATALOG_CVA: lambda: format_cva_catalog(self.catalog),
            # A9-A18 handlers
            QuestionType.SURPRISE: lambda: format_surprise_answer(question),
            QuestionType.DISPUTE: lambda: format_dispute_answer(question),
            QuestionType.DESIGN_PARAMS: lambda: format_design_params_answer(question),
            QuestionType.FRONTIER_GAPS: lambda: format_frontier_answer(question),
            QuestionType.HOOKS: lambda: format_hooks_answer(question),
            QuestionType.EFFECT_SIZE: lambda: format_effect_size_answer(question),
            QuestionType.CROSS_DOMAIN: lambda: format_cross_domain_answer(question),
            QuestionType.HISTORY: lambda: format_history_answer(question),
        }
        
        handler = handler_map.get(qtype)
        if handler:
            self._stats["catalog_served"] += 1
            response = handler()
            response["confidence"] = confidence
            response["ai_generated"] = False
            return response
        
        # AI-routed for everything else
        return self._ai_answer(question, qtype, confidence)
    
    def _ai_answer(self, question: str, qtype: str, 
                   confidence: float) -> Dict[str, Any]:
        """Route question to AI with assembled context."""
        self._stats["ai_routed"] += 1
        
        # Build context
        context = build_ai_context(question, self.catalog)
        prompt = build_ai_prompt(question, context)
        
        # Call LLM if available
        if self.llm_fn:
            try:
                ai_response = self.llm_fn(prompt)
                return {
                    "question_type": qtype,
                    "headline": ai_response.split("\n")[0][:200],
                    "sections": [{"heading": "Answer", "items": [ai_response]}],
                    "confidence": confidence,
                    "ai_generated": True,
                    "model_used": "gemini-2.5-flash",
                    "context_tokens": len(context) // 4,
                    "follow_ups": self._suggest_followups(question, qtype),
                }
            except Exception as e:
                logger.warning(f"AI call failed: {e}")
        
        # Fallback: return context + searchable results
        search_results = self.catalog.search(question.lower())
        sections = []
        
        for category, items in search_results.items():
            if items:
                section_items = []
                for item in items[:5]:
                    if isinstance(item, dict):
                        name = item.get("name", item.get("dimension", str(item)))
                        summary = item.get("summary", item.get("pattern", ""))
                        section_items.append(f"**{name}**: {summary[:100]}")
                    else:
                        section_items.append(str(item))
                sections.append({"heading": category.title(), "items": section_items})
        
        if not sections:
            sections = [{
                "heading": "Answer",
                "items": [
                    "This question requires AI analysis. Relevant context has been assembled.",
                    f"Context contains {len(context)} chars from the knowledge catalog.",
                    "To get a full answer, connect an LLM (gemini-2.5-flash recommended).",
                ],
            }]
        
        return {
            "question_type": qtype,
            "headline": f"Found relevant knowledge across {sum(len(v) for v in search_results.values())} items",
            "sections": sections,
            "confidence": confidence,
            "ai_generated": False,
            "ai_prompt_ready": prompt,
            "context_tokens": len(context) // 4,
            "follow_ups": self._suggest_followups(question, qtype),
        }
    
    def _suggest_followups(self, question: str, qtype: str) -> List[str]:
        """Generate contextual follow-up questions."""
        followups = []
        q_lower = question.lower()
        
        if any(w in q_lower for w in ["theory", "theor", "framework"]):
            followups.append("Show me all cultural differences this system recognizes.")
            followups.append("What T2 molecules exist?")
        
        if any(w in q_lower for w in ["cultur", "eastern", "western"]):
            followups.append("How does this cultural difference affect design guidance?")
            followups.append("Show me all theories in this system.")
        
        if any(w in q_lower for w in ["design", "build", "architect"]):
            followups.append("What evidence supports this design approach?")
            followups.append("What cultural considerations apply?")
        
        if not followups:
            followups = [
                "Show me all theories in this system.",
                "What cultural differences does this system recognize?",
                "What measurement methods are used?",
            ]
        
        return followups[:3]
    
    def get_stats(self) -> Dict[str, int]:
        """Get handler usage stats."""
        return dict(self._stats)


def create_cheap_llm_fn():
    """Create an LLM function using the cheapest available model.
    
    Tries models in order of cost:
    1. gemini-2.5-flash (cheapest, ~$0.075/1M tokens)
    2. gemini-1.5-flash (~$0.075/1M tokens)
    3. Falls back to None (no AI)
    
    Returns:
        Callable or None if no model available
    """
    try:
        from src.agents.agent_core import call_llm, LLMConfig
        
        # Try cheapest model
        config = LLMConfig(model="gemini-2.5-flash", temperature=0.3, max_tokens=1000)
        
        def llm_fn(prompt: str) -> str:
            return call_llm(prompt, config=config)
        
        # Quick test
        test = llm_fn("Say 'ok' if you can hear me.")
        if test and len(test) > 0:
            logger.info("Using gemini-2.5-flash for arbitrary QA")
            return llm_fn
            
    except Exception as e:
        logger.warning(f"Could not initialize LLM for QA: {e}")
    
    return None
