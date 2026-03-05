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
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timezone

# Initialize logger immediately (before any other imports that might use it)
logger = logging.getLogger(__name__)

from src.services.theory_guide_service import TheoryGuideService
from src.services.interpretation_space_suggestions import InterpretationSpaceSuggestionsManager

# Enrichment orchestrator (graceful degradation if unavailable)
try:
    from src.services.answer_enrichment_orchestrator import AnswerEnrichmentOrchestrator
    _orchestrator = AnswerEnrichmentOrchestrator()
    _HAS_ORCHESTRATOR = True
except ImportError as e:
    logger.warning(f"Enrichment orchestrator not available: {e}")
    _orchestrator = None
    _HAS_ORCHESTRATOR = False
except Exception as e:
    logger.warning(f"Failed to initialize enrichment orchestrator: {e}")
    _orchestrator = None
    _HAS_ORCHESTRATOR = False

# Prose revision service (graceful degradation if unavailable)
try:
    from src.services.prose_revision_service import ProseRevisionService
    _prose_reviewer = ProseRevisionService(context="qa_response")
    _HAS_PROSE_REVIEWER = True
except ImportError as e:
    logger.warning(f"Prose revision service not available: {e}")
    _prose_reviewer = None
    _HAS_PROSE_REVIEWER = False
except Exception as e:
    logger.warning(f"Failed to initialize prose revision service: {e}")
    _prose_reviewer = None
    _HAS_PROSE_REVIEWER = False

# Functional circuit QA service (graceful degradation if unavailable)
try:
    from src.services.circuit_qa_service import CircuitQAService
    _circuit_qa_service = CircuitQAService()
    _HAS_CIRCUIT_QA = _circuit_qa_service.circuit_count > 0
    if _HAS_CIRCUIT_QA:
        logger.info(f"Circuit QA service loaded: {_circuit_qa_service.circuit_count} circuits")
except ImportError as e:
    logger.warning(f"Circuit QA service not available: {e}")
    _circuit_qa_service = None
    _HAS_CIRCUIT_QA = False
except Exception as e:
    logger.warning(f"Failed to initialize circuit QA service: {e}")
    _circuit_qa_service = None
    _HAS_CIRCUIT_QA = False

# Precomputed answer card retriever (graceful degradation if unavailable)
try:
    from src.qa.card_retriever import CardRetriever
    _card_retriever = CardRetriever()
    _HAS_CARD_RETRIEVER = _card_retriever.is_available
    if _HAS_CARD_RETRIEVER:
        logger.info(f"Card retriever loaded: {_card_retriever.n_clusters} clusters")
except ImportError as e:
    logger.warning(f"Card retriever not available: {e}")
    _card_retriever = None
    _HAS_CARD_RETRIEVER = False
except Exception as e:
    logger.warning(f"Failed to initialize card retriever: {e}")
    _card_retriever = None
    _HAS_CARD_RETRIEVER = False

PROJECT_ROOT = Path(__file__).parent.parent.parent

# Initialize theory guide service (lazy load on first use)
_theory_guide_service: Optional[TheoryGuideService] = None


def _get_theory_guide_service() -> TheoryGuideService:
    """Get or initialize theory guide service (lazy loading)."""
    global _theory_guide_service
    if _theory_guide_service is None:
        _theory_guide_service = TheoryGuideService(
            guides_dir=str(PROJECT_ROOT / "docs" / "theory_guides"),
            theories_dir=str(PROJECT_ROOT / "data" / "theories"),
        )
    return _theory_guide_service


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
    
    # Theory guide queries
    THEORY_GUIDE = "theory_guide"              # "explain ART" / "guide to prospect-refuge"
    
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
    FUNCTIONAL_CIRCUIT = "functional_circuit"  # "tell me about sensory prediction error circuit"
    ARCHETYPE_GUIDE = "archetype_guide"        # "what uses predictive coding?"

    # Paper-level drill-down queries
    PAPER_METHODS = "paper_methods"            # "show me methods from Smith (2020)"
    PAPER_STIMULUS = "paper_stimulus"          # "what stimulus did they use in paper X?"


QUESTION_PATTERNS = [
    # Functional circuit queries (high priority — before catalog)
    (QuestionType.FUNCTIONAL_CIRCUIT, re.compile(
        r'(?:tell\s+me\s+about|explain|what\s+is|how\s+does?|describe)\s+(?:the\s+)?'
        r'(?:sensory\s+prediction|reward\s+prediction|social\s+prediction|arousal\s+regulation|'
        r'attentional\s+selection|familiarity\s+detection|cognitive\s+load|threat\s+monitoring|'
        r'coherence\s+monitoring|action\s+selection|dread\s+accumulation|context.gated|'
        r'affective\s+memory|thermoregulatory|vitality\s+monitoring|aesthetic\s+expectation|'
        r'curiosity\s+accumulation|interpretive\s+selection|expertise.gated|social\s+safety)'
        r'\s*(?:circuit|motif|pattern)?', re.I)),
    (QuestionType.FUNCTIONAL_CIRCUIT, re.compile(
        r'(?:functional\s+circuit|FC_)\w*', re.I)),
    (QuestionType.ARCHETYPE_GUIDE, re.compile(
        r'(?:what\s+(?:circuits?\s+)?use[sd]?|tell\s+me\s+about\s+(?:the\s+)?|explain\s+(?:the\s+)?)'
        r'(?:predictive\s+coding|homeostatic\s+regulation|accumulation\s+to\s+bound|'
        r'competitive\s+selection|gated\s+propagation|convergent\s+state\s+monitoring)'
        r'\s*(?:archetype|pattern)?', re.I)),
    (QuestionType.ARCHETYPE_GUIDE, re.compile(
        r'(?:list|show|what\s+are)\s+(?:all\s+)?(?:the\s+)?(?:circuits?|archetypes?)', re.I)),
    # Paper-level drill-down queries (SC-PM-1: classify paper reference)
    (QuestionType.PAPER_METHODS, re.compile(
        r'(?:show|list|what)\s+(?:are\s+)?(?:the\s+)?(?:method|technique|design|procedure|'
        r'measure|instrument|stimul|material|protocol)'
        r'.*?(?:from|in|used\s+(?:in|by))\s+'
        r'(?:(?:paper|study|article|experiment)\s+)?'
        r'(?:(?:by\s+)?[A-Z][a-z]+(?:\s+(?:et\s+al\.?|&\s+[A-Z][a-z]+))?\s*'
        r'[\(\[]?\d{4}[\)\]]?'  # Author (2020) pattern
        r'|doi[:\s]*10\.\d+)',  # or DOI
        re.I)),
    (QuestionType.PAPER_STIMULUS, re.compile(
        r'(?:what\s+(?:stimulus|stimuli|image|visual|environment|condition)'
        r'|describe\s+(?:the\s+)?(?:stimulus|stimuli|image|experimental\s+setup))'
        r'.*?(?:from|in|used\s+(?:in|by))\s+'
        r'(?:(?:by\s+)?[A-Z][a-z]+(?:\s+(?:et\s+al\.?|&\s+[A-Z][a-z]+))?\s*'
        r'[\(\[]?\d{4}[\)\]]?'
        r'|doi[:\s]*10\.\d+)',
        re.I)),
    (QuestionType.PAPER_METHODS, re.compile(
        r'(?:methods?|stimul|procedure|design)\s+(?:of|from|in)\s+(?:the\s+)?'
        r'(?:(?:by\s+)?[A-Z][a-z]+(?:\s+(?:et\s+al\.?))?'
        r'\s*[\(\[]?\d{4}[\)\]]?)',
        re.I)),

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
    
    # Theory guide queries (high priority — before A9-A18)
    (QuestionType.THEORY_GUIDE, re.compile(
        r'(?:explain|tell\s+me\s+about|guide\s+(?:to|for)|deep\s+dive\s+(?:on|into)?|'
        r'what\s+is\s+(?:the\s+)?(?:theory\s+of|framework\s+of)?|teach\s+me\s+(?:about)?)\s*'
        r'(?:attention\s+restoration|ART|stress\s+recover|SRT|biophilia|prospect[\s-]?refuge|'
        r'chronobiolog|cognitive\s+map|CPTED|episodic\s+memor|flow\s+theor|goldilocks|'
        r'kaplan|preference\s+matrix|PAD\s+model|place\s+attach|privacy\s+regulat|proxemics)', re.I)),
    
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

    SUCCESS CONDITIONS:
    - SC-CQ-1: Returns a 2-tuple (question_type: str, confidence: float)
    - SC-CQ-2: question_type is a valid QuestionType constant
    - SC-CQ-3: confidence is in [0.0, 1.0]
    - SC-CQ-4: Never raises exception (returns fallback on error)
    """
    try:
        for qtype, pattern in QUESTION_PATTERNS:
            if pattern.search(text):
                return (qtype, 0.85)

        return (QuestionType.ARBITRARY, 0.3)
    except Exception as e:
        logger.warning(f"classify_question failed on text '{text[:50]}...': {e}")
        return (QuestionType.ARBITRARY, 0.0)


# =============================================================================
# Answer Formatters
# =============================================================================

def format_theory_catalog(catalog) -> Dict[str, Any]:
    """Format comprehensive theory catalog answer per TIER_ARCHITECTURE_SPEC_2026-03-01.

    SUCCESS CONDITIONS:
    - SC-FTC-1: Returns a dict
    - SC-FTC-2: Dict has 'answer' key with string value OR 'sections' key with list of dicts
    - SC-FTC-3: Dict has 'sources' key with list value OR sources computed from catalog
    - SC-FTC-4: Dict has 'question_type' key matching QuestionType.CATALOG_THEORIES
    - SC-FTC-5: Dict has 'headline' key with non-empty string
    """
    try:
        theories = catalog.get_theories()   # These are actually T1.5 domain theories
        frameworks = catalog.get_frameworks()  # Bridging frameworks
        molecules = catalog.get_molecules()    # 18 molecules (latent variables)

        sections = []

        # T1 Frameworks — loaded from canonical schemas/theory/tier1_frameworks.json
        t1_items = []
        t1_json_path = Path(__file__).resolve().parent.parent.parent / "schemas" / "theory" / "tier1_frameworks.json"
        if t1_json_path.exists():
            try:
                t1_data = json.load(open(t1_json_path))
                for fid, info in t1_data.get("frameworks", {}).items():
                    name = info.get("name", fid)
                    mechanism = info.get("core_mechanism", "")
                    # Truncate mechanism to first sentence for readability
                    first_sentence = mechanism.split(";")[0].split(".")[0] + "." if mechanism else ""
                    t1_items.append(f"**{name}**: {first_sentence}")
            except Exception as e:
                logger.debug(f"Non-critical T1 load: {e}")
        # Fallback if JSON not found
        if not t1_items:
            t1_items = [
                "**Predictive Processing**: The brain continuously generates predictions about sensory input; mismatches drive learning and attention.",
                "**Spatial Navigation / Cognitive Mapping**: Hippocampal place cells and grid cells encode spatial experience.",
                "**Dual-Process Evaluation**: System 1 (fast, automatic) vs System 2 (slow, deliberate) compete for behavioral control.",
                "**DMN/TPN Dynamics**: Default Mode Network and Task-Positive Network reciprocally inhibit.",
                "**Neuromodulatory Systems**: Dopamine, serotonin, norepinephrine, and cortisol modulate arousal, reward, and stress.",
                "**Interoceptive / Constructionist Affect**: The brain constructs emotions from interoceptive signals + environmental context.",
                "**Memory Systems**: Episodic, semantic, and procedural memory systems encode environmental experiences.",
                "**Embodied Cognition**: Cognition is grounded in sensorimotor experience.",
                "**Chronobiological Regulation**: Circadian rhythms entrained by light affect melatonin, cortisol, alertness, and sleep.",
                "**Multisensory Integration**: The brain combines information across sensory modalities.",
            ]
        sections.append({
            "heading": "T1 — Framework Theories (10)",
            "description": "Neurally grounded, cross-domain frameworks. The fundamental explanatory level.",
            "items": t1_items,
        })

        # T1.5 Domain Theories — loaded from canonical schemas/theory/tier1_5_domain_theories.json
        t1_5_items = []
        t15_json_path = Path(__file__).resolve().parent.parent.parent / "schemas" / "theory" / "tier1_5_domain_theories.json"
        if t15_json_path.exists():
            try:
                t15_data = json.load(open(t15_json_path))
                for tid, info in t15_data.get("domain_theories", {}).items():
                    name = info.get("name", tid)
                    originator = info.get("originator", "")
                    phenomena = info.get("phenomena_organized", "")
                    coverage = info.get("coverage", 0)
                    maturity = info.get("maturity", "")
                    # Truncate phenomena to first sentence
                    short_desc = phenomena.split(".")[0] + "." if phenomena else ""
                    t1_5_items.append(
                        f"**{name}** ({originator})\n"
                        f"  {short_desc} Coverage: {coverage:.0%}, maturity: {maturity}."
                    )
            except Exception as e:
                logger.debug(f"Non-critical T1.5 load: {e}")
        # Fallback if JSON not found or empty
        if not t1_5_items:
            for t in theories:
                name = t['name']
                evidence_note = f" ({t['evidence_count']} linked beliefs)" if t.get('evidence_count') else ""
                t1_5_items.append(
                    f"**{t['name']}** ({t['authors']}, {t['year']}){evidence_note}\n"
                    f"  {t['summary']}"
                )
        n_t15 = len(t1_5_items)
        sections.append({
            "heading": f"T1.5 — Domain Theories ({n_t15})",
            "description": "Author-attributed phenomenological theories. Explained BY T1 frameworks, each with formal reduction mappings.",
            "items": t1_5_items,
        })

        # Molecules — 18 latent variables (includes T1.5 as subset)
        mol_lines = [f"**{m['name']}** (`{m['id']}`): {m['summary']}" for m in molecules]
        sections.append({
            "heading": f"Molecules — Latent Variables ({len(molecules)})",
            "description": "Compositional effect bundles. T1.5 are a subset. Discoverable via factor analysis of T2 template co-activation.",
            "items": mol_lines,
        })

        # T2 Templates and T3 Beliefs (counts only — too many to list)
        sections.append({
            "heading": "T2 — CMR Templates (~166) & T3 — Empirical Beliefs",
            "description": "T2: Specific mechanism chains (Arch Feature → Neural Process → Psych Outcome). T3: Ground-level evidence in Web of Belief.",
            "items": [
                "**T2 Templates**: ~166 defined mechanism chains, each declaring which T1 frameworks it invokes",
                "**T3 Beliefs**: Specific environment→outcome claims supported by multiple articles in the extraction corpus",
            ],
        })

        # Bridging frameworks from catalog
        if frameworks:
            fw_lines = [f"**{fw['name']}**: {fw['summary']}" for fw in frameworks]
            sections.append({
                "heading": f"Bridging Frameworks ({len(frameworks)})",
                "description": "Additional domain-specific frameworks connecting T1 theories to design applications",
                "items": fw_lines,
            })
    
        return {
            "question_type": QuestionType.CATALOG_THEORIES,
            "headline": f"ATLAS theory architecture: 10 T1 framework theories, {n_t15} T1.5 domain theories, "
                        f"~166 T2 CMR templates, {len(molecules)} molecules, T3 empirical beliefs.",
            "sections": sections,
            "total_items": 10 + n_t15 + len(molecules),
            "follow_ups": [
                "How does Attention Restoration Theory reduce to T1 frameworks?",
                "What evidence supports the Biophilia Hypothesis?",
                "Show me all cultural differences this system recognizes.",
            ],
            "sources": [],
        }
    except Exception as e:
        logger.warning(f"format_theory_catalog failed: {e}")
        return {
            "question_type": QuestionType.CATALOG_THEORIES,
            "headline": "ATLAS theory architecture unavailable",
            "sections": [{"heading": "Error", "items": ["Failed to generate theory catalog. Please try again."]}],
            "total_items": 0,
            "follow_ups": [],
            "sources": [],
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
# Theory Guide Handler
# =============================================================================

THEORY_GUIDE_DIR = PROJECT_ROOT / "docs" / "theory_guides"

# Mapping from keywords → guide file basenames
_GUIDE_ALIASES = {
    "attention restoration": "flow_theory_guide",  # ART is covered in flow
    "art": "flow_theory_guide",
    "stress recovery": "kaplan_preference_guide",  # SRT via Kaplan
    "srt": "kaplan_preference_guide",
    "biophilia": "goldilocks_principle_guide",
    "prospect refuge": "kaplan_preference_guide",
    "prospect-refuge": "kaplan_preference_guide",
    "chronobiology": "chronobiology_guide",
    "chronobiolog": "chronobiology_guide",
    "cognitive map": "cognitive_map_guide",
    "cpted": "cpted_guide",
    "episodic memory": "episodic_memory_guide",
    "episodic memor": "episodic_memory_guide",
    "flow theory": "flow_theory_guide",
    "flow": "flow_theory_guide",
    "goldilocks": "goldilocks_principle_guide",
    "kaplan": "kaplan_preference_guide",
    "preference matrix": "kaplan_preference_guide",
    "pad model": "pad_model_guide",
    "pad": "pad_model_guide",
    "place attachment": "place_attachment_guide",
    "place attach": "place_attachment_guide",
    "privacy regulation": "privacy_regulation_guide",
    "privacy regulat": "privacy_regulation_guide",
    "proxemics": "proxemics_guide",
}


class _HTMLTextExtractor(HTMLParser):
    """Minimal HTML→text extractor for theory guides."""
    def __init__(self):
        super().__init__()
        self._parts = []
        self._tag_stack = []
    
    def handle_starttag(self, tag, attrs):
        self._tag_stack.append(tag)
        if tag in ("h1", "h2", "h3"):
            self._parts.append("\n")
        elif tag == "li":
            self._parts.append("\n• ")
        elif tag == "p":
            self._parts.append("\n")
    
    def handle_endtag(self, tag):
        if self._tag_stack and self._tag_stack[-1] == tag:
            self._tag_stack.pop()
        if tag in ("h1", "h2", "h3", "p"):
            self._parts.append("\n")
    
    def handle_data(self, data):
        # Skip style/script content
        if self._tag_stack and self._tag_stack[-1] in ("style", "script"):
            return
        self._parts.append(data.strip())
    
    def get_text(self):
        return " ".join(self._parts).strip()


def _load_theory_guide(guide_basename: str) -> Optional[Dict[str, Any]]:
    """Load and parse a theory guide HTML file."""
    path = THEORY_GUIDE_DIR / f"{guide_basename}.html"
    if not path.exists():
        return None
    
    html = path.read_text(errors='replace')
    
    # Extract title from <title> or first <h1>
    title_match = re.search(r'<title>(.*?)</title>', html)
    title = title_match.group(1) if title_match else guide_basename.replace('_', ' ').title()
    
    # Extract sections by <h2> tags
    sections = []
    h2_parts = re.split(r'<h2[^>]*>(.*?)</h2>', html)
    
    for i in range(1, len(h2_parts), 2):
        heading = re.sub(r'<[^>]+>', '', h2_parts[i]).strip()
        body_html = h2_parts[i+1] if i+1 < len(h2_parts) else ""
        
        # Extract text from body
        extractor = _HTMLTextExtractor()
        extractor.feed(body_html)
        body_text = extractor.get_text()
        
        # Split into bullet items
        items = [line.strip() for line in body_text.split('\n') if line.strip()]
        if items:
            sections.append({"heading": heading, "items": items[:8]})  # Cap at 8 items per section
    
    return {"title": title, "sections": sections, "path": str(path)}


def format_theory_guide_answer(question: str) -> Dict[str, Any]:
    """Answer theory guide queries using TheoryGuideService.

    Routes to appropriate detail level based on question intent:
    - Simple "what is" questions → quick
    - Standard explanation questions → standard
    - "deep dive", "comprehensive", "detailed" → technical
    """
    q_lower = question.lower()
    service = _get_theory_guide_service()

    # Determine detail level based on question language
    detail_level = "quick"  # default
    if any(word in q_lower for word in ["deep dive", "comprehensive", "detailed", "full", "complete", "all the"]):
        detail_level = "technical"
    elif any(word in q_lower for word in ["how", "mechanism", "explain", "describe", "tell"]):
        detail_level = "standard"

    # Extract theory name from question (rough approximation)
    # More sophisticated extraction could use NER or predefined patterns
    theory_name = q_lower
    for word in ["explain", "tell me about", "guide to", "deep dive on", "what is", "teach me about"]:
        if word in theory_name:
            theory_name = theory_name.replace(word, "").strip()
    theory_name = theory_name.strip('? ')

    # Get guide using service
    guide = service.get_guide(theory_name, detail_level=detail_level)

    if not guide:
        # Fallback: build a guide from extraction data + catalog
        return _build_extraction_theory_guide(theory_name, question)

    # Format content as sections (break into paragraphs for readability)
    sections = []
    paragraphs = guide.content.split('\n\n')

    # First section is the guide content itself
    sections.append({
        "heading": f"{guide.display_name} — {detail_level.capitalize()} Guide",
        "items": [p.strip() for p in paragraphs[:5] if p.strip()],  # Cap at 5 paragraphs
    })

    # Add constructs if available
    if guide.constructs:
        sections.append({
            "heading": "Key Constructs",
            "items": [f"**{c}**" for c in guide.constructs[:5]],
        })

    # Add maturity/status info
    if guide.maturity or guide.atlas_status:
        status_items = []
        if guide.maturity:
            status_items.append(f"**Maturity**: {guide.maturity}")
        if guide.atlas_status:
            status_items.append(f"**ATLAS Status**: {guide.atlas_status}")
        if status_items:
            sections.append({
                "heading": "Assessment",
                "items": status_items,
            })

    return {
        "question_type": "theory_guide",
        "headline": f"Theory Guide: {guide.display_name}",
        "sections": sections,
        "guide_path": guide.guide_path,
        "detail_level": detail_level,
        "follow_ups": [
            f"What evidence supports {guide.display_name}?",
            f"What's surprising about {guide.display_name}?",
            "Show me all theories in this system.",
        ],
    }


def _build_extraction_theory_guide(theory_name: str, question: str) -> Dict[str, Any]:
    """Build a theory guide from extraction findings when no HTML guide exists."""
    results = _search_findings(theory_name, max_results=20)

    # Collect evidence summary
    antecedents = set()
    consequents = set()
    theories_seen = set()
    mechanisms = []
    paper_count = set()

    for f in results:
        ant = f.get("antecedent", "")
        cons = f.get("consequent", "")
        if ant:
            antecedents.add(ant)
        if cons:
            consequents.add(cons)
        paper_count.add(f.get("_source_doi", ""))
        for t in (f.get("theory_links") or f.get("theory_commitments") or []):
            theories_seen.add(str(t))
        mech = f.get("mechanism") or f.get("mechanism_chain")
        if mech and str(mech) != "not specified":
            mechanisms.append(str(mech)[:200])

    sections = []
    if results:
        # Summary section
        summary_items = [
            f"**Appears in**: {len(paper_count)} papers with {len(results)} findings",
        ]
        if theories_seen:
            summary_items.append(f"**Related theories**: {', '.join(sorted(theories_seen)[:8])}")
        if mechanisms:
            summary_items.append(f"**Key mechanism**: {mechanisms[0]}")
        sections.append({
            "heading": f"What We Know About '{theory_name}'",
            "items": summary_items,
        })

        # Key findings
        finding_items = []
        for f in results[:8]:
            ant = f.get("antecedent", "?")
            cons = f.get("consequent", "?")
            direction = f.get("direction", "?")
            doi = f.get("_source_doi", "")
            title = f.get("_source_title", "")
            line = f"**{ant}** → {cons} ({direction})"
            line += f"\n  Source: {doi}"
            if title:
                line += f" — *{title[:60]}*"
            finding_items.append(line)
        sections.append({
            "heading": f"Key Findings ({min(8, len(results))} shown)",
            "items": finding_items,
        })

        # Scope
        if antecedents:
            sections.append({
                "heading": "As Antecedent (causes)",
                "items": [f"• {a}" for a in sorted(antecedents)[:6]],
            })
        if consequents:
            sections.append({
                "heading": "As Consequent (effects)",
                "items": [f"• {c}" for c in sorted(consequents)[:6]],
            })
    else:
        available = _get_theory_guide_service().list_available_guides()
        sections = [{
            "heading": f"No findings for '{theory_name}'",
            "items": [f"Try: {', '.join(available[:5])}"],
        }]

    return {
        "question_type": "theory_guide",
        "headline": f"'{theory_name}': {len(results)} findings from {len(paper_count)} papers (no dedicated guide yet).",
        "sections": sections,
        "follow_ups": [
            f"What evidence supports {theory_name}?",
            f"What mechanisms underlie {theory_name}?",
            f"Is {theory_name} controversial?",
        ],
    }


def format_meta_coverage_answer(question: str) -> Dict[str, Any]:
    """Answer 'what do you know about X?' with corpus coverage stats."""
    topic = re.sub(
        r'(?:what\s+do\s+you\s+know\s+about|what\s+does\s+the\s+system\s+know|coverage\s+of)\s*',
        '', question, flags=re.I
    ).strip('? ')

    results = _search_findings(topic, max_results=50)
    all_findings = _load_extraction_findings()

    papers = set(f.get("_source_doi", "") for f in results)
    theories = set()
    with_quant = 0
    for f in results:
        for t in (f.get("theory_links") or f.get("theory_commitments") or []):
            theories.add(str(t))
        if f.get("sample_size") or f.get("effect_size"):
            with_quant += 1

    items = [
        f"**Matching findings**: {len(results)} (from {len(all_findings):,} total)",
        f"**Unique papers**: {len(papers)}",
        f"**Theories referenced**: {', '.join(sorted(theories)[:6]) or 'none'}",
        f"**With quantitative data**: {with_quant}/{len(results)}",
        f"**Coverage strength**: {'Strong' if len(results) > 20 else 'Moderate' if len(results) > 5 else 'Sparse'}",
    ]

    return {
        "question_type": "meta_coverage",
        "headline": f"System knows {len(results)} findings about '{topic}' from {len(papers)} papers.",
        "sections": [{"heading": f"Coverage for '{topic}'", "items": items}],
        "follow_ups": [
            f"What evidence supports {topic}?",
            f"What don't you know about {topic}?",
            f"Tell me about {topic}",
        ],
    }


def format_meta_system_answer(question: str) -> Dict[str, Any]:
    """Answer 'how does this system work?' with architecture summary."""
    all_findings = _load_extraction_findings()
    papers = set(f.get("_source_doi", "") for f in all_findings)
    theories = set()
    for f in all_findings:
        for t in (f.get("theory_links") or f.get("theory_commitments") or []):
            theories.add(str(t))

    items = [
        f"**Extraction corpus**: {len(all_findings):,} findings from {len(papers):,} papers",
        f"**Theories tracked**: {len(theories)} (10 T1 frameworks, 13 T1.5 domain theories, 18 molecules, ~166 T2 templates)",
        "**Query types handled**: Evidence, Mechanism, Comparison, Definition, Theory Guides, Design Guidance, Effect Sizes, Surprises, Disputes, Cross-Domain, History, Catalogs",
        "**Argumentation engine**: Critique aggregation, hierarchy evidence, meta-analytic pooling, tension detection",
        "**Provenance**: DOI → paper title → finding → theory → sample size → effect size",
        "**No AI needed**: 9/10 query types answered directly from data",
    ]

    return {
        "question_type": "meta_system",
        "headline": f"ATLAS Article Eater: {len(all_findings):,} findings, {len(papers):,} papers, {len(theories)} theories.",
        "sections": [{"heading": "System Architecture", "items": items}],
        "follow_ups": [
            "Show me all theories",
            "What do you know about biophilia?",
            "What evidence supports stress recovery?",
        ],
    }


def format_meta_gaps_answer(question: str) -> Dict[str, Any]:
    """Answer 'what don't you know?' with gap analysis."""
    topic = re.sub(
        r'(?:what\s+(?:don\'?t|do\s+not)\s+you\s+know|gaps?\s+(?:in|about)|missing|unknown)\s*(?:about)?\s*',
        '', question, flags=re.I
    ).strip('? ')

    if topic:
        results = _search_findings(topic, max_results=50)
        all_findings = _load_extraction_findings()
        without_sample = sum(1 for f in results if not f.get("sample_size"))
        without_effect = sum(1 for f in results if not f.get("effect_size"))
        without_mechanism = sum(1 for f in results if not (f.get("mechanism") or f.get("mechanism_chain")))

        items = [
            f"**Findings without sample size**: {without_sample}/{len(results)}",
            f"**Findings without effect size**: {without_effect}/{len(results)}",
            f"**Findings without mechanism**: {without_mechanism}/{len(results)}",
        ]
        if len(results) < 5:
            items.append(f"**⚠️ Sparse coverage**: Only {len(results)} findings for '{topic}' (from {len(all_findings):,} total)")
    else:
        all_findings = _load_extraction_findings()
        without_sample = sum(1 for f in all_findings if not f.get("sample_size"))
        without_effect = sum(1 for f in all_findings if not f.get("effect_size"))
        without_theory = sum(1 for f in all_findings if not (f.get("theory_links") or f.get("theory_commitments")))

        items = [
            f"**Findings without sample size**: {without_sample}/{len(all_findings):,} ({100*without_sample//max(1,len(all_findings))}%)",
            f"**Findings without effect size**: {without_effect}/{len(all_findings):,} ({100*without_effect//max(1,len(all_findings))}%)",
            f"**Findings without theory link**: {without_theory}/{len(all_findings):,} ({100*without_theory//max(1,len(all_findings))}%)",
            "**BN integration**: 0% of findings mapped to environment_id/outcome_id",
            "**Interpretive layer**: R₁-R₄ closures not yet implemented",
        ]

    return {
        "question_type": "meta_gaps",
        "headline": f"Knowledge gaps{' for ' + repr(topic) if topic else ''}",
        "sections": [{"heading": "Known Gaps & Missing Data", "items": items}],
        "follow_ups": [
            "How does this system work?",
            "What evidence supports biophilia?",
        ],
    }


def format_design_guidance_answer(question: str) -> Dict[str, Any]:
    """Answer 'how should I design X?' using extraction findings + argumentation."""
    topic = re.sub(
        r'(?:how\s+should\s+I\s+design|design\s+guidance\s+for|design\s+recommendations\s+for)\s*',
        '', question, flags=re.I
    ).strip('? ')

    results = _search_findings(topic, max_results=30)

    # Find actionable findings (those with clear direction)
    actionable = []
    for f in results:
        direction = f.get("direction", "")
        if direction:
            ant = f.get("antecedent", "?")
            cons = f.get("consequent", "?")
            actionable.append({
                "guidance": f"**{ant}** → {cons} ({direction})",
                "sample": f.get("sample_size"),
                "effect": f.get("effect_size"),
                "source": f.get("_source_doi", ""),
            })

    sections = []
    if actionable:
        guidance_items = []
        for a in actionable[:10]:
            line = a["guidance"]
            quals = []
            if a["sample"]:
                quals.append(f"n={a['sample']}")
            if a["effect"]:
                quals.append(f"d={a['effect']}")
            if quals:
                line += f"  [{', '.join(quals)}]"
            guidance_items.append(line)

        sections.append({
            "heading": f"Evidence-Based Design Guidance ({len(actionable)} findings)",
            "items": guidance_items,
        })
    else:
        sections.append({
            "heading": "Design Guidance",
            "items": [f"No specific design guidance found for '{topic}'. Try broader terms."],
        })

    return {
        "question_type": "design_guidance",
        "headline": f"Found {len(actionable)} evidence-based design recommendations for '{topic}'.",
        "sections": sections,
        "follow_ups": [
            f"What effect sizes matter for {topic}?",
            f"What evidence supports {topic}?",
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
        except Exception as e:
            logger.debug(f"Non-critical: {e}")
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
        except Exception as e:
            logger.debug(f"Non-critical: {e}")
    
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
        except Exception as e:
            logger.debug(f"Non-critical: {e}")
    
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
        except Exception as e:
            logger.debug(f"Non-critical: {e}")
    
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
        except Exception as e:
            logger.debug(f"Non-critical: {e}")
    
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
# Extraction-Backed Evidence Search (33K findings from JSON files)
# =============================================================================

_EXTRACTION_DIR = PROJECT_ROOT / "data" / "extractions"
_extraction_cache: Optional[List[Dict]] = None


def _load_extraction_findings(limit: int = 50000) -> List[Dict]:
    """Load findings from extraction JSON files. Cached after first call."""
    global _extraction_cache
    if _extraction_cache is not None:
        return _extraction_cache

    findings = []
    if not _EXTRACTION_DIR.exists():
        return findings

    for fp in sorted(_EXTRACTION_DIR.glob("*.json"))[:limit]:
        try:
            with open(fp) as f:
                data = json.load(f)
            doi = data.get("doi", data.get("DOI", fp.stem))
            title = data.get("title", "")
            for finding in data.get("findings", []):
                finding["_source_doi"] = doi
                finding["_source_title"] = title
                finding["_source_file"] = fp.name
                findings.append(finding)
        except Exception:
            continue

    _extraction_cache = findings
    return findings


def _search_findings(query: str, max_results: int = 15) -> List[Dict]:
    """Search extraction findings by keyword match across key fields."""
    findings = _load_extraction_findings()
    query_lower = query.lower()
    keywords = [w for w in query_lower.split() if len(w) > 2]

    scored = []
    for f in findings:
        # Build searchable text from key fields
        searchable = " ".join([
            str(f.get("antecedent", "")),
            str(f.get("consequent", "")),
            str(f.get("direction", "")),
            str(f.get("mechanism", "")),
            " ".join(str(t) for t in (f.get("theory_links") or [])),
            " ".join(str(t) for t in (f.get("theory_commitments") or [])),
            str(f.get("mechanism_chain", "")),
            str(f.get("_source_title", "")),
        ]).lower()

        # Score: count keyword matches
        score = sum(1 for kw in keywords if kw in searchable)
        if score > 0:
            scored.append((score, f))

    scored.sort(key=lambda x: -x[0])
    return [f for _, f in scored[:max_results]]


def format_evidence_answer(question: str, direction: str = "supports") -> Dict[str, Any]:
    """Answer evidence queries by searching extraction findings with provenance trace."""
    # Extract topic from question
    topic = re.sub(
        r'(?:what\s+)?evidence\s+(?:support|for|confirm|verif|against|contradict|refut|weaken)\w*\s*',
        '', question, flags=re.I
    ).strip('? ')

    results = _search_findings(topic)

    items = []
    unique_sources = set()
    with_sample = 0
    with_effect = 0
    theories_seen = set()

    for f in results:
        antecedent = f.get("antecedent", "?")
        consequent = f.get("consequent", "?")
        direction_val = f.get("direction", "?")
        sample = f.get("sample_size", "")
        effect = f.get("effect_size", "")
        doi = f.get("_source_doi", "")
        title = f.get("_source_title", "")
        theories = f.get("theory_links") or f.get("theory_commitments") or []

        unique_sources.add(doi)
        if sample:
            with_sample += 1
        if effect:
            with_effect += 1
        for t in theories:
            theories_seen.add(str(t))

        evidence_line = f"**{antecedent}** → {consequent} ({direction_val})"
        if theories:
            evidence_line += f"\n  Theory: {', '.join(str(t) for t in theories[:3])}"
        if sample:
            evidence_line += f"\n  Sample: n={sample}"
        if effect:
            evidence_line += f", Effect: {effect}"
        evidence_line += f"\n  Source: {doi}"
        if title:
            evidence_line += f" — *{title[:80]}*"

        items.append(evidence_line)

    # Provenance summary section
    provenance_items = [
        f"**Unique papers**: {len(unique_sources)}",
        f"**Findings with sample size**: {with_sample}/{len(results)}",
        f"**Findings with effect size**: {with_effect}/{len(results)}",
        f"**Theories referenced**: {', '.join(sorted(theories_seen)[:5]) or 'none'}",
    ]

    sections = [
        {
            "heading": f"Evidence {'Supporting' if direction == 'supports' else 'Against'} (top {len(items)})",
            "items": items or ["No matching findings found. Try different keywords."],
        },
    ]
    if items:
        sections.append({
            "heading": "Provenance Summary",
            "items": provenance_items,
        })

        # Epistemic Notes per EPISTEMIC_PRINCIPLES.md (Principles 1, 4, 5, 15)
        epistemic_items = []

        # Pollock (P1): Defeasibility caveat
        if len(unique_sources) < 5:
            epistemic_items.append(
                f"**Defeasibility (Pollock)**: Evidence is currently *warranted* but thin "
                f"({len(unique_sources)} papers). New contradictory evidence could defeat this finding."
            )
        else:
            epistemic_items.append(
                f"**Defeasibility (Pollock)**: Evidence is *warranted* across {len(unique_sources)} independent papers. "
                f"Warrant remains defeasible — new evidence could still undercut or rebut."
            )

        # Pearl (P5): Causal tier note
        epistemic_items.append(
            "**Causal status (Pearl)**: These are *associations*, not confirmed causal claims, "
            "unless the source study used experimental or quasi-experimental designs."
        )

        # Cartwright (P4): Scope note
        if with_sample > 0:
            epistemic_items.append(
                f"**Scope (Cartwright)**: {with_sample}/{len(results)} findings report sample sizes. "
                f"Unknown scope ≠ universal scope — check settings, populations, and durations."
            )

        # Gawande (P15): Name the gap
        gap_parts = []
        if with_effect == 0:
            gap_parts.append("no effect sizes reported")
        if with_sample < len(results) // 2:
            gap_parts.append(f"only {with_sample}/{len(results)} have sample sizes")
        if gap_parts:
            epistemic_items.append(
                f"**Gap (Gawande)**: {'; '.join(gap_parts)}. "
                f"Quantitative strength of this evidence is difficult to assess."
            )

        if epistemic_items:
            sections.append({
                "heading": "Epistemic Notes (per ATLAS norms)",
                "items": epistemic_items,
            })

    return {
        "question_type": "evidence",
        "headline": f"Found {len(results)} findings related to '{topic}' "
                    f"from {len(unique_sources)} papers ({len(_load_extraction_findings())} total findings).",
        "sections": sections,
        "total_count": len(results),
        "follow_ups": [
            f"What's surprising about {topic}?",
            f"How big is the effect of {topic}?",
            f"What don't we know about {topic}?",
        ],
    }


def format_mechanism_answer(question: str) -> Dict[str, Any]:
    """Answer mechanism/causal queries by searching extraction findings."""
    # Extract topic
    topic = re.sub(
        r'(?:how\s+does?|why\s+does?|what\s+(?:mechanism|cause|explain)\w*)\s*',
        '', question, flags=re.I
    ).strip('? ')

    results = _search_findings(topic)

    # Filter for findings with mechanism info
    with_mechanism = [f for f in results if f.get("mechanism") or f.get("mechanism_chain")]
    display = with_mechanism[:10] if with_mechanism else results[:10]

    items = []
    for f in display:
        antecedent = f.get("antecedent", "?")
        consequent = f.get("consequent", "?")
        mechanism = f.get("mechanism", f.get("mechanism_chain", "not specified"))
        theories = f.get("theory_links") or f.get("theory_commitments") or []

        item = f"**{antecedent}** → {consequent}"
        if mechanism and mechanism != "not specified":
            item += f"\n  Mechanism: {str(mechanism)[:200]}"
        if theories:
            item += f"\n  Theory: {', '.join(str(t) for t in theories[:3])}"
        items.append(item)

    return {
        "question_type": "mechanism",
        "headline": f"Found {len(with_mechanism)} findings with mechanism data "
                    f"out of {len(results)} matches for '{topic}'.",
        "sections": [{
            "heading": f"Causal Mechanisms ({len(items)} shown)",
            "items": items or ["No mechanism data found. Try asking about specific antecedent→consequent pairs."],
        }],
        "follow_ups": [
            f"What evidence supports {topic}?",
            f"Is {topic} controversial?",
        ],
    }


def format_comparison_answer(question: str) -> Dict[str, Any]:
    """Answer comparison queries using argumentation engine's find_arguments."""
    from src.argument.engine import ArgumentationEngine
    
    # Extract topic
    topic = re.sub(
        r'(?:compare|contrast|difference|versus|vs\.?|between)\s*',
        '', question, flags=re.I
    ).strip('? ')
    
    engine = ArgumentationEngine()
    args = engine.find_arguments(topic, max_results=8)
    
    sections = []
    if args["supporting"]:
        sections.append({
            "heading": f"Supporting Evidence ({len(args['supporting'])})",
            "items": [
                f"**{a['claim'][:120]}**\n  Source: {a['source']}"
                + (f"\n  Theory: {', '.join(str(t) for t in a['theories'][:3])}" if a['theories'] else "")
                for a in args["supporting"][:8]
            ],
        })
    if args["opposing"]:
        sections.append({
            "heading": f"Opposing Evidence ({len(args['opposing'])})",
            "items": [
                f"**{a['claim'][:120]}**\n  Source: {a['source']}"
                for a in args["opposing"][:8]
            ],
        })
    if args["tensions"]:
        sections.append({
            "heading": f"Detected Tensions ({len(args['tensions'])})",
            "items": [
                f"**{t['consequent']}**: {t['direction_a']} vs {t['direction_b']}"
                for t in args["tensions"][:5]
            ],
        })
    if not sections:
        sections = [{"heading": "Results", "items": ["No comparison data found. Try different terms."]}]
    
    return {
        "question_type": "comparison",
        "headline": args["headline"],
        "sections": sections,
        "follow_ups": [
            f"What evidence supports {topic}?",
            f"How does {topic} work mechanistically?",
        ],
    }


def format_definition_answer(question: str) -> Dict[str, Any]:
    """Answer definition queries by searching findings and theory catalog."""
    topic = re.sub(
        r'(?:what\s+is|define|meaning\s+of|explain)\s*',
        '', question, flags=re.I
    ).strip('? ')
    
    results = _search_findings(topic, max_results=20)
    
    # Extract unique theories, antecedents, consequents
    theories = set()
    antecedents = set()
    consequents = set()
    for f in results:
        for t in (f.get("theory_links") or f.get("theory_commitments") or []):
            theories.add(str(t))
        antecedents.add(f.get("antecedent", ""))
        consequents.add(f.get("consequent", ""))
    
    items = []
    if theories:
        items.append(f"**Related theories**: {', '.join(sorted(theories)[:5])}")
    if antecedents:
        items.append(f"**As antecedent in**: {', '.join(sorted(a for a in antecedents if a)[:5])}")
    if consequents:
        items.append(f"**As consequent in**: {', '.join(sorted(c for c in consequents if c)[:5])}")
    items.append(f"**Appears in**: {len(results)} findings from {len(set(f.get('_source_doi','') for f in results))} papers")
    
    return {
        "question_type": "definition",
        "headline": f"'{topic}' appears in {len(results)} findings across the extraction corpus.",
        "sections": [{
            "heading": f"Definition Context for '{topic}'",
            "items": items or [f"No findings for '{topic}'. Try broader terms."],
        }],
        "follow_ups": [
            f"What evidence supports {topic}?",
            f"How does {topic} reduce stress?",
        ],
    }


# =============================================================================
# AI Context Builder (for arbitrary questions)
# =============================================================================

def build_ai_context(question: str, catalog, max_tokens: int = 2000) -> str:
    """Build a focused context package for AI answering.

    Searches catalog + annotations to find relevant knowledge,
    then formats as a compact context prompt.

    SUCCESS CONDITIONS:
    - SC-BAC-1: Returns a string (never None)
    - SC-BAC-2: Result length roughly bounded by max_tokens * 4 chars (±10%)
    - SC-BAC-3: Contains relevant information from catalog (theories, frameworks, molecules)
    - SC-BAC-4: Never raises exception (returns fallback on error)
    """
    try:
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
            context_parts.append(f"- 10 T1 framework theories, 13 T1.5 domain theories, ~166 T2 templates, 18 molecules")
            context_parts.append(f"- 103 outcome terms across 8 domains")
            context_parts.append(f"- 8 CVA constraint dimensions, 8 valuation axes")
            context_parts.append(f"- 6 cultural difference dimensions")
            context_parts.append(f"- 717 extracted images, 17,330+ annotated findings")

        # Truncate to max tokens (rough estimate: 4 chars per token)
        context = "\n".join(context_parts)
        if len(context) > max_tokens * 4:
            context = context[:max_tokens * 4]

        return context
    except Exception as e:
        logger.warning(f"build_ai_context failed: {e}")
        return f"SYSTEM OVERVIEW: 10 T1 framework theories, 13 T1.5 domain theories, ~166 T2 templates, 18 molecules."


def build_ai_prompt(question: str, context: str) -> str:
    """Build the prompt for AI answering.

    SUCCESS CONDITIONS:
    - SC-BAP-1: Returns a string (never None)
    - SC-BAP-2: Result contains the question text verbatim
    - SC-BAP-3: Result contains the context text
    - SC-BAP-4: Never raises exception
    """
    try:
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
    except Exception as e:
        logger.warning(f"build_ai_prompt failed: {e}")
        return f"USER QUESTION: {question}\n\nANSWER:"


# =============================================================================
# Main Handler
# =============================================================================

class ArbitraryQAHandler:
    """Handles arbitrary user questions about the system's knowledge.
    
    Uses pattern-based classification for catalog queries (free, instant)
    and AI routing for complex/novel questions (cheap API call).
    """
    
    def __init__(self, llm_fn=None, db_path: Optional[str] = None, user_type: str = "researcher", enable_enrichment: bool = True, enable_prose_review: bool = False):
        """
        Args:
            llm_fn: Optional LLM function with signature (prompt: str) -> str.
                    If None, AI-routed questions return context + prompt for external processing.
            db_path: Optional path to web.db for tracking suggestions.
                     If provided, follow-ups are recorded in interpretation_space_suggestions table.
            user_type: User persona type for language adaptation ("researcher", "student", "clinician", etc).
            enable_enrichment: Whether to apply enrichment orchestrator to answers.
            enable_prose_review: Whether to run prose quality diagnostics on AI-generated answers.
                    When enabled, adds a 'prose_review' field to the response with quality metrics.
        """
        from src.services.knowledge_catalog import KnowledgeCatalog
        self.catalog = KnowledgeCatalog()
        self.llm_fn = llm_fn
        self._user_type = user_type
        self._enable_enrichment = enable_enrichment
        self._enable_prose_review = enable_prose_review
        self._stats = {"classified": 0, "ai_routed": 0, "catalog_served": 0, "card_served": 0}
        self.suggestions_mgr: Optional[InterpretationSpaceSuggestionsManager] = None
        if db_path:
            try:
                self.suggestions_mgr = InterpretationSpaceSuggestionsManager(db_path)
            except Exception as e:
                logger.warning(f"Failed to initialize suggestions manager: {e}")

    def _wrap_response(self, response: Dict[str, Any], question: str, qtype: str) -> Dict[str, Any]:
        """Wrap a response dict to ensure all required fields are present.

        Ensures SC-ANS-2 through SC-ANS-8 success conditions.
        """
        # Ensure required fields
        if "question" not in response:
            response["question"] = question
        if "answer" not in response:
            response["answer"] = response.get("headline", "")
        if "question_type" not in response:
            response["question_type"] = qtype
        if "confidence" not in response:
            response["confidence"] = 0.5
        if "sources" not in response:
            response["sources"] = []
        if "timestamp" not in response:
            response["timestamp"] = datetime.now(timezone.utc).isoformat()

        return response

    def _apply_enrichment(self, base_answer: Dict[str, Any], question: str) -> Dict[str, Any]:
        """Apply enrichment orchestrator to a base answer if enabled.

        Args:
            base_answer: Answer dict from handler or AI router
            question: Original user question

        Returns:
            Same base_answer with enrichment applied, or unchanged if enrichment fails

        SUCCESS CONDITIONS:
        - SC-AE-1: Returns a dict (always, even on failure)
        - SC-AE-2: Original answer preserved even when enrichment fails
        - SC-AE-3: On success, result has 'enrichment_metadata' key or 'enrichment' key
        - SC-AE-4: On failure, result has 'enriched' key set to False
        """
        if not _HAS_ORCHESTRATOR or not self._enable_enrichment:
            base_answer["enriched"] = False
            return base_answer

        try:
            enriched = _orchestrator.enrich(
                base_answer=base_answer,
                question=question,
                user_type=self._user_type
            )
            base_answer["enrichment"] = enriched.to_dict()
            base_answer["enriched"] = True
            return base_answer
        except Exception as e:
            logger.warning(f"Enrichment failed (returning base answer): {e}")
            base_answer["enriched"] = False
            return base_answer

    def _apply_prose_review(self, base_answer: Dict[str, Any]) -> Dict[str, Any]:
        """Apply prose revision diagnostics to answer text if enabled.

        Runs the 3-pass revision protocol (Doumont structural, Lanham+Williams
        sentence-level, Pinker knowledge-curse) on the answer's text content.
        Adds a 'prose_review' field with score, verdict, and top suggestions.

        Args:
            base_answer: Answer dict from handler or AI router

        Returns:
            Same base_answer with prose_review field added

        SUCCESS CONDITIONS:
        - SC-APR-1: Returns a dict (always, even on failure)
        - SC-APR-2: Original answer preserved even when review fails
        - SC-APR-3: On success, result has 'prose_review' key with score, verdict, suggestions
        - SC-APR-4: On failure, result has 'prose_reviewed' key set to False
        """
        if not _HAS_PROSE_REVIEWER or not self._enable_prose_review:
            base_answer["prose_reviewed"] = False
            return base_answer

        try:
            # Extract text from sections
            text_parts = []
            for section in base_answer.get("sections", []):
                heading = section.get("heading", "")
                if heading:
                    text_parts.append(f"## {heading}")
                for item in section.get("items", []):
                    if isinstance(item, str):
                        text_parts.append(item)
            full_text = "\n\n".join(text_parts)

            if len(full_text) < 50:
                base_answer["prose_reviewed"] = False
                return base_answer

            report = _prose_reviewer.full_critique(full_text)
            top_suggestions = _prose_reviewer.suggest_revisions(full_text, max_suggestions=5)

            base_answer["prose_review"] = {
                "score": round(report.overall_score, 1),
                "verdict": report.verdict,
                "summary": report.summary,
                "writers_diet": report.writers_diet.as_dict() if report.writers_diet else None,
                "lard_factor": round(report.lard_factor_estimate, 1),
                "passive_voice_pct": round(report.passive_voice_pct, 1),
                "nominalization_density": round(report.nominalization_density, 1),
                "critical_issues": report.critical_count,
                "warnings": report.warning_count,
                "top_suggestions": [
                    {
                        "severity": d.severity.value,
                        "message": d.message,
                        "suggestion": d.suggestion,
                        "norm": d.norm_reference,
                    }
                    for d in top_suggestions
                ],
            }
            base_answer["prose_reviewed"] = True
            return base_answer
        except Exception as e:
            logger.warning(f"Prose review failed (returning base answer): {e}")
            base_answer["prose_reviewed"] = False
            return base_answer

    def answer(self, question: str) -> Dict[str, Any]:
        """Answer any question about the system's knowledge.

        Returns structured response dict with:
        - question: the input question text
        - answer: the main answer text (for simple cases)
        - question_type: classified type
        - confidence: confidence in classification
        - headline: one-line answer
        - sections: detailed structured content
        - follow_ups: suggested follow-up questions
        - ai_generated: True if AI was used
        - enriched: True if enrichment was applied
        - timestamp: ISO 8601 timestamp of response

        SUCCESS CONDITIONS:
        - SC-ANS-1: Returns a dict (never None)
        - SC-ANS-2: Dict always has keys: question, answer, question_type, confidence, sources
        - SC-ANS-3: question field matches input question
        - SC-ANS-4: answer is a non-empty string (or headline if answer not present)
        - SC-ANS-5: sources is a list
        - SC-ANS-6: Never raises exception on any question string (catches internally)
        - SC-ANS-7: enrichment_metadata present when enrichment enabled
        - SC-ANS-8: timestamp is present
        """
        try:
            # Classify
            qtype, confidence = classify_question(question)
            self._stats["classified"] += 1

            # V13 Audit Fix: Check precomputed answer cards FIRST.
            # If a cluster matches the query, return the precomputed card
            # immediately — no live enrichment needed.
            if _HAS_CARD_RETRIEVER:
                card_response = _card_retriever.try_match(
                    question, user_type=self._user_type
                )
                if card_response is not None:
                    self._stats["card_served"] += 1
                    card_response["question_type_classified"] = qtype
                    card_response = self._apply_prose_review(card_response)
                    self._track_followups(card_response.get("follow_ups", []))
                    return self._wrap_response(card_response, question, qtype)

            # Route to handler
            handler_map = {
                QuestionType.CATALOG_THEORIES: lambda: format_theory_catalog(self.catalog),
                QuestionType.CATALOG_CULTURAL: lambda: format_cultural_catalog(self.catalog),
                QuestionType.CATALOG_MOLECULES: lambda: format_molecule_catalog(self.catalog),
                QuestionType.CATALOG_OUTCOMES: lambda: format_outcome_catalog(self.catalog),
                QuestionType.CATALOG_METHODS: lambda: format_methods_catalog(self.catalog),
                QuestionType.CATALOG_CVA: lambda: format_cva_catalog(self.catalog),
                # Theory guide handler
                QuestionType.THEORY_GUIDE: lambda: format_theory_guide_answer(question),
                # A9-A18 handlers
                QuestionType.SURPRISE: lambda: format_surprise_answer(question),
                QuestionType.DISPUTE: lambda: format_dispute_answer(question),
                QuestionType.DESIGN_PARAMS: lambda: format_design_params_answer(question),
                QuestionType.FRONTIER_GAPS: lambda: format_frontier_answer(question),
                QuestionType.HOOKS: lambda: format_hooks_answer(question),
                QuestionType.EFFECT_SIZE: lambda: format_effect_size_answer(question),
                QuestionType.CROSS_DOMAIN: lambda: format_cross_domain_answer(question),
                QuestionType.HISTORY: lambda: format_history_answer(question),
                # Extraction-backed handlers
                QuestionType.EVIDENCE_FOR: lambda: format_evidence_answer(question, "supports"),
                QuestionType.EVIDENCE_AGAINST: lambda: format_evidence_answer(question, "against"),
                QuestionType.MECHANISM: lambda: format_mechanism_answer(question),
                QuestionType.COMPARISON: lambda: format_comparison_answer(question),
                QuestionType.DEFINITION: lambda: format_definition_answer(question),
                # Meta handlers
                QuestionType.META_SYSTEM: lambda: format_meta_system_answer(question),
                QuestionType.META_COVERAGE: lambda: format_meta_coverage_answer(question),
                QuestionType.META_GAPS: lambda: format_meta_gaps_answer(question),
                # Design guidance
                QuestionType.DESIGN_GUIDANCE: lambda: format_design_guidance_answer(question),
                # Functional circuit handlers
                QuestionType.FUNCTIONAL_CIRCUIT: lambda: self._handle_circuit_query(question),
                QuestionType.ARCHETYPE_GUIDE: lambda: self._handle_archetype_query(question),
                # Paper-level drill-down handlers
                QuestionType.PAPER_METHODS: lambda: self._handle_paper_methods_query(question),
                QuestionType.PAPER_STIMULUS: lambda: self._handle_paper_methods_query(question),
            }

            handler = handler_map.get(qtype)
            if handler:
                self._stats["catalog_served"] += 1
                response = handler()
                response["confidence"] = confidence
                response["ai_generated"] = False
                response = self._apply_enrichment(response, question)
                response = self._apply_prose_review(response)
                self._track_followups(response.get("follow_ups", []))
                return self._wrap_response(response, question, qtype)

            # AI-routed for everything else
            response = self._ai_answer(question, qtype, confidence)
            response = self._apply_enrichment(response, question)
            response = self._apply_prose_review(response)
            self._track_followups(response.get("follow_ups", []))
            return self._wrap_response(response, question, qtype)

        except Exception as e:
            logger.exception(f"answer() failed for question: {question[:100]}")
            return {
                "question": question,
                "answer": f"Error: {str(e)[:100]}",
                "question_type": QuestionType.ARBITRARY,
                "confidence": 0.0,
                "sources": [],
                "sections": [{"heading": "Error", "items": ["Unable to answer this question at this time."]}],
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def _handle_circuit_query(self, question: str) -> Dict[str, Any]:
        """Handle functional circuit queries using CircuitQAService."""
        if _HAS_CIRCUIT_QA and _circuit_qa_service:
            result = _circuit_qa_service.format_circuit_answer(question)
            if result:
                # Queue search targets for the recommendation loop
                search_targets = result.get("search_targets", [])
                if search_targets:
                    self._queue_circuit_search_targets(search_targets, question)
                return result
        # Fallback: try catalog-based answer
        return {
            "question_type": QuestionType.FUNCTIONAL_CIRCUIT,
            "headline": "Functional circuit not found in the current registry.",
            "sections": [{
                "heading": "Circuit Query",
                "items": [
                    "This question appears to be about a functional circuit, but "
                    "no matching circuit was found. Try asking about a specific circuit "
                    "by name (e.g., 'Sensory Prediction Error Circuit') or ask "
                    "'list all circuits' to see what's available."
                ],
            }],
            "follow_ups": [
                "List all functional circuits",
                "What are the T2 archetypes?",
                "How do circuits relate to molecules?",
            ],
        }

    def _handle_archetype_query(self, question: str) -> Dict[str, Any]:
        """Handle archetype guide queries using CircuitQAService."""
        if _HAS_CIRCUIT_QA and _circuit_qa_service:
            # Identify which archetype
            q_lower = question.lower()
            archetype_map = {
                "predictive coding": "PREDICTIVE_CODING",
                "homeostatic regulation": "HOMEOSTATIC_REGULATION",
                "homeostatic": "HOMEOSTATIC_REGULATION",
                "accumulation to bound": "ACCUMULATION_TO_BOUND",
                "competitive selection": "COMPETITIVE_SELECTION",
                "gated propagation": "GATED_PROPAGATION",
                "convergent state": "CONVERGENT_STATE_MONITORING",
                "convergent state monitoring": "CONVERGENT_STATE_MONITORING",
            }
            for keyword, archetype_id in archetype_map.items():
                if keyword in q_lower:
                    result = _circuit_qa_service.format_archetype_answer(archetype_id)
                    if result:
                        return result

            # If "list all circuits/archetypes" query
            if any(w in q_lower for w in ["list", "show", "all"]):
                summary = _circuit_qa_service.get_all_circuits_summary()
                sections = []
                for arch, circuits in summary.get("by_archetype", {}).items():
                    arch_info = _circuit_qa_service.__class__.__dict__.get("ARCHETYPE_DESCRIPTIONS", {})
                    # Use the module-level constant
                    from src.services.circuit_qa_service import ARCHETYPE_DESCRIPTIONS
                    arch_name = ARCHETYPE_DESCRIPTIONS.get(arch, {}).get("name", arch)
                    items = [
                        f"**{c['name']}** [{c['evidence']}]: {c.get('domain', '')}"
                        for c in circuits
                    ]
                    sections.append({
                        "heading": f"{arch_name} ({len(circuits)} circuits)",
                        "items": items,
                    })
                dist = summary.get("evidence_distribution", {})
                return {
                    "question_type": QuestionType.ARCHETYPE_GUIDE,
                    "headline": (
                        f"ATLAS contains {summary['total_circuits']} functional circuits across "
                        f"6 T2 archetypes: {dist.get('STRONG', 0)} strong, "
                        f"{dist.get('MODERATE', 0)} moderate, {dist.get('HYPOTHETICAL', 0)} hypothetical."
                    ),
                    "sections": sections,
                    "follow_ups": [
                        "Tell me about the Sensory Prediction Error Circuit",
                        "What uses competitive selection?",
                        "How do circuits relate to T1.5 theories?",
                    ],
                }

        # Fallback
        return {
            "question_type": QuestionType.ARCHETYPE_GUIDE,
            "headline": "Circuit QA service not available",
            "sections": [{"heading": "Unavailable", "items": ["Circuit data not loaded."]}],
            "follow_ups": ["Show me all theories", "What molecules exist?"],
        }

    def _handle_paper_methods_query(self, question: str) -> Dict[str, Any]:
        """
        Handle per-paper method drill-down queries.

        Extracts paper reference (Author Year or DOI) from the question,
        searches the extraction corpus, and returns structured method details
        including sample size, study design, stimulus description, and
        measurement instruments.

        SUCCESS CONDITIONS:
            SC-PM-1: Identifies paper reference from question
            SC-PM-2: Returns findings from extraction database when available
            SC-PM-3: Response includes method, stimulus, sample details
            SC-PM-7: Graceful degradation if paper not found
        """
        q_lower = question.lower()

        # Extract paper reference: Author (Year), Author et al. (Year), or DOI
        paper_ref = None
        doi_match = re.search(r'(?:doi[:\s]*)(10\.\d+[^\s,;)]+)', question, re.I)
        author_year_match = re.search(
            r'([A-Z][a-z]+(?:\s+(?:et\s+al\.?|&\s+[A-Z][a-z]+))?)\s*[\(\[]?(\d{4})[\)\]]?',
            question
        )

        if doi_match:
            paper_ref = doi_match.group(1)
        elif author_year_match:
            paper_ref = f"{author_year_match.group(1)} ({author_year_match.group(2)})"

        if not paper_ref:
            return {
                "question_type": QuestionType.PAPER_METHODS,
                "headline": "Could not identify which paper you mean.",
                "sections": [{
                    "heading": "Try a more specific reference",
                    "items": [
                        "Include author and year: 'methods from Bratman (2015)'",
                        "Include DOI: 'methods from doi:10.1016/j.ypmed.2015.07.007'",
                        "Or paper title: 'methods from the nature experience study'",
                    ],
                }],
                "follow_ups": [
                    "What methods are used in Kaplan (1995)?",
                    "Show me stimulus from Appleton (1975)",
                ],
            }

        # Search extraction corpus for this paper
        found_findings = []
        paper_metadata = {}
        extractions_dir = Path("data/extractions")

        if extractions_dir.exists():
            search_terms = set(re.findall(r'\w{3,}', paper_ref.lower()))
            for json_file in extractions_dir.glob("*.json"):
                try:
                    with open(json_file) as f:
                        data = json.load(f)

                    title = (data.get("title") or "").lower()
                    authors = (data.get("authors") or "").lower()
                    doi = (data.get("doi") or "").lower()

                    # Match by DOI, author+year, or title keywords
                    if doi_match and paper_ref.lower() in doi:
                        pass  # Exact DOI match
                    elif len(search_terms & set(re.findall(r'\w{3,}', f"{title} {authors}"))) < 2:
                        continue

                    # Found a matching paper
                    paper_metadata = {
                        "title": data.get("title", json_file.stem),
                        "authors": data.get("authors", ""),
                        "doi": data.get("doi", ""),
                        "year": data.get("year"),
                        "article_type": data.get("article_type", ""),
                    }

                    for finding in data.get("findings", []):
                        found_findings.append(finding)

                    break  # Stop after first match
                except Exception:
                    continue

        if not found_findings:
            return {
                "question_type": QuestionType.PAPER_METHODS,
                "headline": f"No extraction data found for '{paper_ref}'.",
                "sections": [{
                    "heading": "Paper not in corpus",
                    "items": [
                        f"The paper '{paper_ref}' has not yet been extracted.",
                        "It may be in the wishlist or not yet discovered.",
                    ],
                }],
                "follow_ups": [
                    "What theories does ATLAS cover?",
                    "Show me all measurement methods",
                ],
            }

        # Build structured response
        sections = []

        # Study design
        designs = set(f.get("study_design") for f in found_findings if f.get("study_design"))
        sample_sizes = [f.get("sample_size") for f in found_findings if f.get("sample_size")]
        populations = set(f.get("population", f.get("scope_population"))
                        for f in found_findings
                        if f.get("population") or f.get("scope_population"))

        if designs or sample_sizes or populations:
            design_items = []
            if designs:
                design_items.append(f"Design: {', '.join(str(d) for d in designs)}")
            if sample_sizes:
                design_items.append(f"Sample sizes: {sample_sizes}")
            if populations:
                design_items.append(
                    f"Population: {', '.join(str(p) for p in populations if p)}"
                )
            sections.append({"heading": "Study Design", "items": design_items})

        # Stimulus/conditions
        stimuli = set()
        stim_details = []
        for f in found_findings:
            ant = f.get("antecedent")
            if ant:
                stimuli.add(str(ant))
            stim_desc = f.get("stimulus_description")
            if stim_desc and isinstance(stim_desc, dict):
                stim_details.append(
                    f"{stim_desc.get('primary_type', '')}: "
                    f"{', '.join(c.get('name', '') for c in stim_desc.get('components', []))}"
                )

        if stimuli or stim_details:
            stim_items = []
            if stim_details:
                stim_items.extend(stim_details[:5])
            elif stimuli:
                stim_items.extend(list(stimuli)[:8])
            sections.append({
                "heading": "Stimuli & Experimental Conditions",
                "items": stim_items,
            })

        # Findings summary
        finding_items = []
        for f in found_findings[:8]:
            ant = f.get("antecedent", "?")
            cons = f.get("consequent", "?")
            direction = f.get("direction", "?")
            es = f.get("effect_size")
            line = f"{ant} → {cons} ({direction})"
            if es:
                line += f" [d = {es}]"
            finding_items.append(line)

        if finding_items:
            sections.append({
                "heading": f"Key Findings ({len(found_findings)} total)",
                "items": finding_items,
            })

        # Measurement instruments
        instruments = set(f.get("measure_type") or f.get("instrument")
                         for f in found_findings
                         if f.get("measure_type") or f.get("instrument"))
        if instruments:
            sections.append({
                "heading": "Measurement Instruments",
                "items": [str(i) for i in instruments if i],
            })

        headline = (
            f"Methods from {paper_metadata.get('title', paper_ref)}"
            f" ({paper_metadata.get('article_type', 'unknown type')})"
        )

        return {
            "question_type": QuestionType.PAPER_METHODS,
            "headline": headline,
            "sections": sections,
            "sources": [paper_metadata.get("doi", paper_ref)],
            "follow_ups": [
                f"What evidence supports findings from {paper_ref}?",
                f"What stimulus was used in {paper_ref}?",
                "Show me all measurement methods",
            ],
        }

    def _queue_circuit_search_targets(
        self, search_targets: list, source_question: str
    ) -> int:
        """
        Insert circuit QA search targets into the suggestion pipeline.

        When a circuit answer includes suggested article searches (especially
        for HYPOTHETICAL circuits), those queries feed directly into the
        recommendation loop so the system actively seeks missing evidence.

        Args:
            search_targets: List of search query strings from circuit QA
            source_question: The user question that triggered the circuit answer

        Returns:
            Number of suggestions inserted
        """
        count = 0
        try:
            from src.services.interpretation_space_suggestions import (
                InterpretationSpaceSuggestionsManager,
                SuggestionRecord,
            )
            # Use the web_db_path from config if available, else default
            db_path = getattr(self, "_db_path", None)
            if db_path is None:
                # Try common locations
                from pathlib import Path
                candidates = [
                    Path("data/article_eater.db"),
                    Path("article_eater.db"),
                ]
                for p in candidates:
                    if p.exists():
                        db_path = str(p)
                        break
            if db_path is None:
                logger.debug("No DB path for circuit search target queueing")
                return 0

            mgr = InterpretationSpaceSuggestionsManager(db_path)
            for query in search_targets:
                record = SuggestionRecord(
                    source="circuit_qa",
                    status="identified",
                    description=(
                        f"Circuit testability search: {query[:120]} "
                        f"(triggered by: {source_question[:60]})"
                    ),
                    suggested_search=query,
                    priority_score=0.65,  # Moderate-high: evidence gaps matter
                )
                try:
                    mgr.insert_suggestion(record)
                    count += 1
                except Exception as e:
                    logger.debug(f"Failed to queue circuit search target: {e}")
        except ImportError:
            logger.debug("Suggestion manager not available for circuit search targets")
        except Exception as e:
            logger.debug(f"Circuit search target queueing failed: {e}")
        if count > 0:
            logger.info(
                f"Queued {count} circuit search targets for recommendation loop"
            )
        return count

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
        
        # Smart fallback: try extraction search before catalog
        extraction_results = _search_findings(question, max_results=10)
        sections = []
        
        if extraction_results:
            items = []
            for f in extraction_results[:8]:
                ant = f.get("antecedent", "?")
                cons = f.get("consequent", "?")
                direction = f.get("direction", "?")
                doi = f.get("_source_doi", "")
                title = f.get("_source_title", "")
                line = f"**{ant}** → {cons} ({direction})"
                line += f"\n  Source: {doi}"
                if title:
                    line += f" — *{title[:60]}*"
                items.append(line)
            sections.append({"heading": f"Related Findings ({len(extraction_results)} matches)", "items": items})
        
        # Also check catalog
        search_results = self.catalog.search(question.lower())
        for category, cat_items in search_results.items():
            if cat_items:
                section_items = []
                for item in cat_items[:5]:
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
                    "No matching data found in the extraction corpus or catalog.",
                    "Try rephrasing with different keywords.",
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

    def _track_followups(self, followups: List[str]) -> None:
        """Record follow-up suggestions to interpretation_space_suggestions table.

        Args:
            followups: List of follow-up question strings
        """
        if not self.suggestions_mgr or not followups:
            return

        try:
            self.suggestions_mgr.insert_qa_followups(followups, priority_score=0.6)
        except Exception as e:
            logger.warning(f"Failed to track QA follow-ups: {e}")

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
