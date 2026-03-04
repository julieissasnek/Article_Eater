"""
Integrated Query Service — Templates + Articles + BN + Panel Discussion
========================================================================

Created: 2026-02-16
Purpose: Full integration of template knowledge with article evidence and BN confidence

This service builds on TemplateQueryService to add:
1. Article grounding — find extracted claims that support template mechanisms
2. BN confidence — pull calibrated posteriors (when available)
3. Semantic search — embedding-based template matching
4. T1 Panel Discussion — expert voices discussing the finding

The T1 Panel Discussion is the intellectually exciting part: each framework
(PP, SN, EC, etc.) has a "voice" that comments on findings from their perspective,
identifies complications, speculates about mechanisms, and notes limitations.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)

# Import the base template query service
from src.services.template_query_service import (
    TemplateQueryService, QueryResponse, TemplateAnswer,
    UserPersona
)

# Try to import WebOfBelief for article grounding
try:
    from src.services.web_of_belief import WebOfBelief, Belief, EpistemicLevel, BeliefStatus
    from src.services.web_accumulator import WebAccumulator
    WOB_AVAILABLE = True
except ImportError:
    WOB_AVAILABLE = False
    logger.warning("WebOfBelief not available - article grounding disabled")

# Try to import sentence transformers for semantic search
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    logger.warning("sentence-transformers not available - using keyword search")


# =============================================================================
# T1 FRAMEWORK VOICES
# =============================================================================

class T1Framework(Enum):
    """The 10 canonical T1 frameworks with their expert voices."""
    PP = "predictive_processing"      # Friston, Clark
    SN = "spatial_navigation"         # O'Keefe, Moser
    DP = "dual_process"               # Kahneman, Evans
    DT = "dmn_tpn_dynamics"           # Raichle, Fox
    NM = "neuromodulatory"            # Sapolsky, McEwen
    IC = "interoceptive"              # Barrett, Craig
    MS = "memory_systems"             # Squire, Eichenbaum
    EC = "embodied_cognition"         # Gibson, Varela
    CB = "chronobiological"           # Czeisler, Foster
    MSI = "multisensory"              # Stein, Ernst


# Expert voice characteristics for each framework
FRAMEWORK_VOICES = {
    T1Framework.PP: {
        "name": "Predictive Processing",
        "key_figures": ["Karl Friston", "Andy Clark"],
        "core_claim": "The brain is a prediction machine that minimizes surprise",
        "typical_questions": [
            "What prediction is being violated here?",
            "What prior is the brain using?",
            "Is this PE being minimized by updating beliefs or by action?",
            "What precision-weighting is involved?"
        ],
        "complications": [
            "PE magnitude depends on prior precision — same stimulus can produce different PE",
            "Active inference means the brain may change the world rather than update beliefs",
            "Hierarchical predictions mean different levels may conflict"
        ]
    },
    T1Framework.SN: {
        "name": "Spatial Navigation",
        "key_figures": ["John O'Keefe", "May-Britt & Edvard Moser"],
        "core_claim": "The hippocampus builds cognitive maps that support navigation and memory",
        "typical_questions": [
            "How does this affect place cell / grid cell encoding?",
            "Does this change the cognitive map?",
            "What's the spatial reference frame involved?",
            "Is egocentric or allocentric representation dominant?"
        ],
        "complications": [
            "Cognitive maps may be distorted by emotional significance",
            "Grid cell scaling varies with environmental size",
            "Spatial and episodic memory share hippocampal substrate — competition possible"
        ]
    },
    T1Framework.EC: {
        "name": "Embodied Cognition",
        "key_figures": ["J.J. Gibson", "Francisco Varela", "Alva Noë"],
        "core_claim": "Cognition is grounded in bodily interaction with the environment",
        "typical_questions": [
            "What affordances does this create?",
            "How does the body-environment coupling change?",
            "Is this effect preserved without proprioceptive feedback?",
            "What sensorimotor contingencies are involved?"
        ],
        "complications": [
            "VR studies strip embodiment — effects may differ from real environments",
            "Affordances are relational (body-dependent) not objective",
            "Cultural learning shapes affordance perception"
        ]
    },
    T1Framework.NM: {
        "name": "Neuromodulatory Systems",
        "key_figures": ["Robert Sapolsky", "Bruce McEwen"],
        "core_claim": "Stress, reward, and arousal systems shape cognition and health",
        "typical_questions": [
            "What's happening to the HPA axis?",
            "Is this acute or chronic stress?",
            "What's the cortisol time course?",
            "Is allostatic load increasing or decreasing?"
        ],
        "complications": [
            "Cortisol has a 20-minute lag — timing of measurement critical",
            "Chronic and acute stress have opposite effects on some outcomes",
            "Individual differences in stress reactivity are large"
        ]
    },
    T1Framework.IC: {
        "name": "Interoceptive / Constructionist",
        "key_figures": ["Lisa Feldman Barrett", "Bud Craig"],
        "core_claim": "Emotions are constructed from interoceptive signals + context",
        "typical_questions": [
            "What interoceptive signals are changing?",
            "How is context shaping the interpretation?",
            "What's the valence/arousal structure?",
            "Is this bottom-up interoception or top-down prediction?"
        ],
        "complications": [
            "Same physiological state can be constructed as different emotions",
            "Interoceptive accuracy varies greatly across individuals",
            "Alexithymia affects this entire pathway"
        ]
    },
    T1Framework.DT: {
        "name": "DMN/TPN Dynamics",
        "key_figures": ["Marcus Raichle", "Michael Fox"],
        "core_claim": "Anti-correlated default and task-positive networks alternate",
        "typical_questions": [
            "Is this engaging DMN or TPN?",
            "What's the toggle dynamics?",
            "Does this support internal or external focus?",
            "What's the salience network doing?"
        ],
        "complications": [
            "DMN isn't inactive — it's doing internal cognition",
            "Meditation training alters the toggle dynamics",
            "Some tasks require DMN-TPN co-activation"
        ]
    },
    T1Framework.MS: {
        "name": "Memory Systems",
        "key_figures": ["Larry Squire", "Howard Eichenbaum"],
        "core_claim": "Multiple memory systems serve different functions",
        "typical_questions": [
            "Which memory system is engaged?",
            "Is this episodic, semantic, or procedural?",
            "What's the consolidation process?",
            "Is pattern separation or completion dominant?"
        ],
        "complications": [
            "Sleep is critical for consolidation — timing matters",
            "Stress impairs hippocampal encoding",
            "Reconsolidation means memories change when retrieved"
        ]
    },
    T1Framework.CB: {
        "name": "Chronobiological Regulation",
        "key_figures": ["Charles Czeisler", "Russell Foster"],
        "core_claim": "Circadian rhythms regulate physiology and cognition",
        "typical_questions": [
            "What's the circadian phase?",
            "Is this affecting the SCN?",
            "What melanopsin pathway activation?",
            "Is the clock being entrained or disrupted?"
        ],
        "complications": [
            "Individual chronotypes vary (owls vs larks)",
            "Social jetlag is ubiquitous",
            "Blue light at night has different effects than daytime"
        ]
    },
    T1Framework.MSI: {
        "name": "Multisensory Integration",
        "key_figures": ["Barry Stein", "Marc Ernst"],
        "core_claim": "The brain optimally combines information across senses",
        "typical_questions": [
            "Which sensory channels are involved?",
            "Are they congruent or incongruent?",
            "What's the reliability weighting?",
            "Is there super-additivity?"
        ],
        "complications": [
            "Cross-modal plasticity means sensory weights can change",
            "Attention modulates integration",
            "Sensory dominance varies by task and individual"
        ]
    },
    T1Framework.DP: {
        "name": "Dual-Process Evaluation",
        "key_figures": ["Daniel Kahneman", "Jonathan Evans"],
        "core_claim": "Fast intuitive (System 1) and slow deliberate (System 2) processes",
        "typical_questions": [
            "Is this a System 1 or System 2 response?",
            "Is there conflict between fast and slow processing?",
            "What heuristics are being used?",
            "Is deliberation overriding intuition or vice versa?"
        ],
        "complications": [
            "The two-system distinction is a useful fiction — reality is messier",
            "Expertise can make slow processes fast",
            "Cognitive load shifts toward System 1"
        ]
    }
}


@dataclass
class ArticleEvidence:
    """Evidence from an extracted article claim.

    SUCCESS CONDITIONS:
    SC-AE-1: belief_id is a non-empty string
    SC-AE-2: content is a non-empty string (may be truncated)
    SC-AE-3: paper_ids is always a list (never None)
    SC-AE-4: credence is a float in [0.0, 1.0]
    SC-AE-5: credence_uncertainty is a float >= 0.0
    SC-AE-6: level is a non-empty string (from EpistemicLevel values)
    SC-AE-7: status is a non-empty string (from BeliefStatus values)
    SC-AE-8: relevance_score is a float in [0.0, 1.0]
    """
    belief_id: str
    content: str
    paper_ids: List[str]
    credence: float
    credence_uncertainty: float
    level: str
    status: str
    relevance_score: float  # How well this matches the template claim


@dataclass
class PanelComment:
    """A comment from a T1 framework expert voice.

    SUCCESS CONDITIONS:
    SC-PC-1: framework is a valid T1Framework enum member
    SC-PC-2: framework_name is a non-empty string matching FRAMEWORK_VOICES name
    SC-PC-3: perspective is a non-empty string (never "")
    SC-PC-4: complications is a list (may be empty); each element is a string
    SC-PC-5: speculation is a non-empty string
    SC-PC-6: limitations is a list (may be empty); each element is a string
    SC-PC-7: key_question is a non-empty string
    """
    framework: T1Framework
    framework_name: str
    perspective: str  # What this framework says about the finding
    complications: List[str]  # What makes this non-obvious
    speculation: str  # What the expert suspects but can't prove
    limitations: List[str]  # What we don't know from this framework's view
    key_question: str  # The question this framework would ask next


@dataclass
class IntegratedResponse:
    """Full integrated response with articles, BN, and panel discussion.

    SUCCESS CONDITIONS:
    SC-IR-1: template_response is always a valid QueryResponse (never None)
    SC-IR-2: article_evidence is always a list (never None); each element is ArticleEvidence
    SC-IR-3: total_supporting_papers is an int >= 0
    SC-IR-4: evidence_quality_summary is a non-empty string
    SC-IR-5: panel_comments is always a list; each element is PanelComment
    SC-IR-6: panel_synthesis is a string (may be empty when include_panel=False)
    SC-IR-7: panel_debates is always a list; each element is a string
    SC-IR-8: open_questions is always a list; each element is a string
    SC-IR-9: When total_supporting_papers == 0 and templates found, abstention is applied
             (evidence_quality_summary contains 'ABSTENTION')
    SC-IR-10: persona_enrichment is None when no persona specified
    """
    # Base response from templates
    template_response: QueryResponse

    # Article grounding
    article_evidence: List[ArticleEvidence]
    total_supporting_papers: int
    evidence_quality_summary: str

    # BN confidence (when available)
    bn_posterior: Optional[float]
    bn_prior: Optional[float]
    bn_likelihood_ratio: Optional[float]

    # T1 Panel Discussion
    panel_comments: List[PanelComment]
    panel_synthesis: str  # What the panel agrees on
    panel_debates: List[str]  # Where frameworks disagree
    open_questions: List[str]  # What no framework can answer

    # Sprint QA-2/QA-4: Persona-specific enrichment data
    persona_enrichment: Optional[Dict] = field(default_factory=lambda: None)  # type: ignore[assignment]


class IntegratedQueryService:
    """
    Full integration: Templates + Articles + BN + Panel Discussion
    """

    def __init__(
        self,
        templates_dir: str = "data/templates",
        use_embeddings: bool = True
    ):
        self.template_service = TemplateQueryService(templates_dir)
        self.templates = self.template_service.templates

        # Article grounding
        self._web = None
        self._accumulator = None

        # Semantic search
        self.use_embeddings = use_embeddings and EMBEDDINGS_AVAILABLE
        self._embedder = None
        self._template_embeddings = None

        # Card retriever fast-path (AG Round 14)
        # Checks precomputed cards before expensive live enrichment.
        # Cards are generated by CardGenerationOrchestrator + AG tab generators.
        self._card_retriever = None
        try:
            from src.qa.card_retriever import CardRetriever
            self._card_retriever = CardRetriever()
            if self._card_retriever.is_available:
                logger.info(
                    f"Card retriever loaded: {self._card_retriever.n_clusters} clusters"
                )
            else:
                self._card_retriever = None
        except Exception as e:
            logger.debug(f"Card retriever unavailable: {e}")

        if self.use_embeddings:
            self._init_embeddings()

    def _init_embeddings(self):
        """Initialize sentence transformer for semantic search.

        SUCCESS CONDITIONS:
        SC-IE-1: On success, self._embedder is a SentenceTransformer instance
        SC-IE-2: On success, self._template_embeddings is populated (dict)
        SC-IE-3: On failure, self.use_embeddings is set to False (graceful degradation)
        SC-IE-4: Never raises an exception to caller
        """
        try:
            self._embedder = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Initialized sentence transformer for semantic search")

            # Pre-compute template embeddings
            self._compute_template_embeddings()
        except Exception as e:
            logger.warning(f"Failed to initialize embeddings: {e}")
            self.use_embeddings = False

    def _compute_template_embeddings(self):
        """Pre-compute embeddings for all templates.

        SUCCESS CONDITIONS:
        SC-CTE-1: After call, self._template_embeddings is a dict
        SC-CTE-2: Each key in _template_embeddings corresponds to a template in self.templates
        SC-CTE-3: Returns early (no-op) if self._embedder is None
        SC-CTE-4: Only includes templates with 'display_id' field
        """
        if not self._embedder:
            return

        self._template_embeddings = {}
        texts = []
        ids = []

        for tid, template in self.templates.items():
            if not isinstance(template, dict) or 'display_id' not in template:
                continue

            # Combine searchable text
            text = ' '.join([
                template.get('name', ''),
                template.get('structural_pattern', ''),
                template.get('higher_order_principle', ''),
                template.get('short_description', ''),
            ])
            texts.append(text)
            ids.append(tid)

        if texts:
            embeddings = self._embedder.encode(texts, show_progress_bar=False)
            for i, tid in enumerate(ids):
                self._template_embeddings[tid] = embeddings[i]

            logger.info(f"Computed embeddings for {len(ids)} templates")

    @property
    def web(self) -> Optional['WebOfBelief']:
        """Lazy-load the web of belief."""
        if not WOB_AVAILABLE:
            return None

        if self._web is None:
            try:
                if self._accumulator is None:
                    self._accumulator = WebAccumulator()
                # V13 Audit Fix: get_master_web() returns (WebOfBelief, BridgeRegistry) tuple
                result = self._accumulator.get_master_web()
                if isinstance(result, tuple):
                    self._web = result[0]  # WebOfBelief
                else:
                    self._web = result
            except Exception as e:
                logger.warning(f"Could not load web of belief: {e}")
                return None

        return self._web

    def _semantic_search_templates(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """Search templates using semantic similarity.

        SUCCESS CONDITIONS:
        SC-SS-1: Returns a list of (template_id, similarity_score) tuples
        SC-SS-2: Each similarity_score is a float (cosine similarity)
        SC-SS-3: Results are sorted by descending similarity score
        SC-SS-4: len(result) <= top_k
        SC-SS-5: Returns empty list if embeddings unavailable (graceful degradation)
        SC-SS-6: Each template_id in result exists in self.templates
        """
        if not self.use_embeddings or not self._embedder:
            return []

        query_embedding = self._embedder.encode([query])[0]

        scores = []
        for tid, template_emb in self._template_embeddings.items():
            # Cosine similarity
            similarity = np.dot(query_embedding, template_emb) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(template_emb)
            )
            scores.append((tid, float(similarity)))

        scores.sort(key=lambda x: -x[1])
        return scores[:top_k]

    def _find_article_evidence(
        self,
        template: TemplateAnswer,
        max_articles: int = 10
    ) -> List[ArticleEvidence]:
        """Find article claims that support a template's mechanism.

        SUCCESS CONDITIONS:
        SC-FAE-1: Returns a list of ArticleEvidence (never None)
        SC-FAE-2: len(result) <= max_articles
        SC-FAE-3: Results are sorted by descending relevance_score
        SC-FAE-4: Each ArticleEvidence has valid paper_ids (list, max 3 entries)
        SC-FAE-5: Returns empty list if web of belief unavailable (graceful degradation)
        SC-FAE-6: Each evidence.content is truncated to <= 200 characters
        SC-FAE-7: relevance_score > 0 for all returned evidence (zero-match items excluded)
        """
        if not self.web:
            return []

        evidence = []

        # Extract keywords from template
        keywords = set()
        for pathway in template.how:
            keywords.add(pathway.from_entity.lower().replace('_', ' '))
            keywords.add(pathway.to_entity.lower().replace('_', ' '))

        # Search beliefs for matching content
        for belief_id, belief in self.web.beliefs.items():
            content_lower = belief.content.lower()

            # Score by keyword overlap
            matches = sum(1 for kw in keywords if kw in content_lower)
            if matches == 0:
                continue

            relevance = matches / len(keywords) if keywords else 0

            evidence.append(ArticleEvidence(
                belief_id=belief_id,
                content=belief.content[:200],
                paper_ids=belief.paper_ids[:3],
                credence=belief.credence.mean if hasattr(belief.credence, 'mean') else 0.5,
                credence_uncertainty=belief.credence.uncertainty if hasattr(belief.credence, 'uncertainty') else 0.3,
                level=belief.level.value if hasattr(belief.level, 'value') else str(belief.level),
                status=belief.status.value if hasattr(belief.status, 'value') else str(belief.status),
                relevance_score=relevance
            ))

        # Sort by relevance
        evidence.sort(key=lambda x: -x.relevance_score)
        return evidence[:max_articles]

    def _generate_panel_comments(
        self,
        template_response: QueryResponse
    ) -> List[PanelComment]:
        """Generate T1 panel discussion comments.

        SUCCESS CONDITIONS:
        SC-GPC-1: Returns a list of PanelComment (never None)
        SC-GPC-2: len(result) <= 4 (readability limit)
        SC-GPC-3: PP (predictive processing) is always included in frameworks
        SC-GPC-4: Each PanelComment has non-empty perspective, speculation, key_question
        SC-GPC-5: Framework names match FRAMEWORK_VOICES dictionary entries
        SC-GPC-6: complications list on each comment has <= 2 entries (from voice[:2])
        """
        comments = []

        # Get the frameworks referenced in the template
        relevant_frameworks = set()
        for ans in template_response.relevant_templates[:3]:
            template = self.templates.get(ans.display_id, {})
            framework_ids = template.get('framework_ids', [])
            for fid in framework_ids:
                # Map to T1Framework
                fid_lower = fid.lower().replace('_', '').replace('-', '')
                for fw in T1Framework:
                    if fw.value.replace('_', '') in fid_lower or fw.name.lower() in fid_lower:
                        relevant_frameworks.add(fw)

        # Always include PP (predictive processing) as it's the meta-framework
        relevant_frameworks.add(T1Framework.PP)

        # Limit to 4 frameworks for readability
        frameworks_to_include = list(relevant_frameworks)[:4]

        for framework in frameworks_to_include:
            voice = FRAMEWORK_VOICES.get(framework, {})

            # Generate perspective based on template content
            perspective = self._generate_framework_perspective(
                framework, voice, template_response
            )
            speculation = self._generate_speculation(framework, voice, template_response)
            limitations = self._identify_framework_limitations(framework, voice, template_response)

            comments.append(PanelComment(
                framework=framework,
                framework_name=voice.get('name', framework.value),
                perspective=perspective,
                complications=voice.get('complications', [])[:2],
                speculation=speculation,
                limitations=limitations,
                key_question=voice.get('typical_questions', ['What mechanism is involved?'])[0]
            ))

        return comments

    def _generate_framework_perspective(
        self,
        framework: T1Framework,
        voice: Dict,
        response: QueryResponse
    ) -> str:
        """Generate what this framework says about the finding.

        SUCCESS CONDITIONS:
        SC-GFP-1: Returns a non-empty string (never "" or None)
        SC-GFP-2: Return value contains framework-specific content (not generic for known frameworks)
        SC-GFP-3: Returns graceful fallback string when response has no relevant_templates
        SC-GFP-4: For unknown frameworks, uses voice['core_claim'] as fallback
        """
        if not response.relevant_templates:
            return "Insufficient data for framework-specific analysis"

        top = response.relevant_templates[0]
        mechanism = response.how

        if framework == T1Framework.PP:
            return (
                f"From a predictive processing view: {mechanism} can be understood as "
                f"prediction error at the {top.how[0].level if top.how else 'environmental'} level. "
                f"The brain has priors about spatial proportions, and violations of these priors "
                f"drive attention and potentially learning. The question is: what precision is "
                f"assigned to these predictions?"
            )
        elif framework == T1Framework.EC:
            return (
                f"From an embodied cognition view: This effect depends on the body-environment "
                f"relationship. The relevant question is what affordances are created or modified. "
                f"This may not replicate in VR or with images because proprioceptive feedback is absent."
            )
        elif framework == T1Framework.NM:
            return (
                f"From a neuromodulatory view: We should ask what's happening to the stress axis. "
                f"Is this acute or chronic? What's the cortisol time course? Individual differences "
                f"in stress reactivity will moderate this effect substantially."
            )
        elif framework == T1Framework.IC:
            return (
                f"From an interoceptive/constructionist view: The affective response is constructed "
                f"from interoceptive signals in context. The same physiological state could be "
                f"interpreted differently depending on prior experience and current context."
            )
        elif framework == T1Framework.SN:
            return (
                f"From a spatial navigation view: This may affect the cognitive map representation. "
                f"Place cells and grid cells in the hippocampus encode spatial structure; changes "
                f"to perceived space should alter these representations."
            )
        else:
            core = voice.get('core_claim', 'This framework provides a lens for understanding the mechanism')
            return f"From the {voice.get('name', framework.value)} perspective: {core}"

    def _generate_speculation(
        self,
        framework: T1Framework,
        voice: Dict,
        response: QueryResponse
    ) -> str:
        """Generate what the framework expert suspects but can't prove.

        SUCCESS CONDITIONS:
        SC-GS-1: Returns a non-empty string (never "" or None)
        SC-GS-2: Return contains speculative language (hedging, not assertions)
        SC-GS-3: For unknown frameworks, uses voice['name'] in fallback
        """
        if framework == T1Framework.PP:
            return (
                "I suspect the effect is mediated by precision-weighting — the brain assigns "
                "higher precision to spatial predictions in some contexts than others. This would "
                "explain individual differences and context-dependency. But we'd need computational "
                "modeling to test this properly."
            )
        elif framework == T1Framework.EC:
            return (
                "I suspect this effect would be much larger with actual movement through the space "
                "than with static observation. The sensorimotor contingencies matter. Most studies "
                "use static conditions, which may underestimate the real-world effect."
            )
        elif framework == T1Framework.NM:
            return (
                "I suspect there's a U-shaped function here — both very high and very low levels "
                "are problematic, with an optimal zone in between. This is typical of stress-related "
                "phenomena. We rarely test the full dose-response curve."
            )
        else:
            return (
                f"Based on {voice.get('name', framework.value)} principles, there may be "
                f"unexamined moderators that would reveal individual differences. "
                f"This warrants further investigation."
            )

    def _identify_framework_limitations(
        self,
        framework: T1Framework,
        voice: Dict,
        response: QueryResponse
    ) -> List[str]:
        """Identify what this framework can't explain.

        SUCCESS CONDITIONS:
        SC-IFL-1: Returns a list of strings (never None)
        SC-IFL-2: len(result) <= 3
        SC-IFL-3: Each string is non-empty
        SC-IFL-4: For unknown frameworks, returns generic limitations using voice['name']
        """
        limitations = []

        if framework == T1Framework.PP:
            limitations.extend([
                "PP doesn't specify WHICH predictions are active — needs empirical work",
                "Precision-weighting is inferred, not measured directly",
                "The theory is very flexible — hard to falsify"
            ])
        elif framework == T1Framework.EC:
            limitations.extend([
                "Affordances are relational — hard to quantify",
                "Most studies strip embodiment, limiting ecological validity",
                "The theory doesn't make precise quantitative predictions"
            ])
        elif framework == T1Framework.NM:
            limitations.extend([
                "Cortisol timing is critical but often ignored in studies",
                "Individual differences in reactivity are huge",
                "Acute vs chronic effects can be opposite — need longitudinal data"
            ])
        else:
            limitations.extend([
                f"{voice.get('name', framework.value)} provides a lens but not the full picture",
                "Integration with other frameworks is needed"
            ])

        return limitations[:3]

    def _synthesize_panel(
        self,
        comments: List[PanelComment]
    ) -> Tuple[str, List[str], List[str]]:
        """Synthesize panel discussion into agreements, debates, and open questions.

        SUCCESS CONDITIONS:
        SC-SP-1: Returns a 3-tuple (synthesis: str, debates: list, open_questions: list)
        SC-SP-2: synthesis is a non-empty string
        SC-SP-3: debates is a list of strings (may be empty)
        SC-SP-4: open_questions is a list of strings (may be empty)
        SC-SP-5: When comments is empty, returns graceful fallback ("No panel discussion available", [], [])
        SC-SP-6: synthesis mentions all framework names from input comments
        """
        if not comments:
            return "No panel discussion available", [], []

        # Agreements
        synthesis = (
            f"The panel ({', '.join(c.framework_name for c in comments)}) agrees that this is a "
            f"real phenomenon with neural substrates, but debates the primary mechanism. "
            f"All frameworks acknowledge significant individual differences and context-dependency."
        )

        # Debates
        debates = [
            "Is this primarily a perceptual phenomenon (PP) or an embodied one (EC)?",
            "Does the effect operate through conscious evaluation or subcortical processing?",
            "How much variance is explained by the mechanism vs. individual differences?",
        ]

        # Open questions
        open_questions = [
            "What's the minimal effective dose / threshold?",
            "Does the effect persist with adaptation or habituate?",
            "What individual difference measures predict who responds most?",
            "Can the mechanism be used therapeutically?",
        ]

        return synthesis, debates, open_questions

    def query(
        self,
        query_text: str,
        include_articles: bool = True,
        include_panel: bool = True,
        persona: UserPersona = None
    ) -> IntegratedResponse:
        """
        Full integrated query with articles, BN, and panel discussion.

        SUCCESS CONDITIONS:
        SC-Q-1: Returns a valid IntegratedResponse (never None, never raises on valid input)
        SC-Q-2: template_response is always populated (even if no templates match)
        SC-Q-3: article_evidence is empty list when include_articles=False
        SC-Q-4: panel_comments is empty list when include_panel=False
        SC-Q-5: total_supporting_papers == len(unique paper_ids across article_evidence)
        SC-Q-6: When total_supporting_papers == 0 and templates found, abstention applied:
                 confidence collapsed to <= 0.20, evidence_quality_summary contains 'ABSTENTION'
        SC-Q-7: persona_enrichment is None when persona is None
        SC-Q-8: article_evidence limited to 10 entries max
        SC-Q-9: evidence_quality_summary is always a non-empty string
        """
        # ── Card fast-path (AG Round 14) ──
        # Try precomputed card lookup first (~5-20ms vs 5000ms+ live)
        if self._card_retriever:
            try:
                card_hit = self._card_retriever.try_match_unified(query_text)
                if card_hit:
                    logger.info(
                        f"Card fast-path HIT for '{query_text[:50]}' "
                        f"({card_hit.get('card_metadata', {}).get('lookup_ms', '?')}ms)"
                    )
                    # Return a minimal IntegratedResponse wrapping the card hit.
                    # The card already has full evidence/provenance baked in.
                    from src.services.template_query_service import QueryResponse
                    stub_response = QueryResponse(
                        query=query_text,
                        relevant_templates=[],
                        how="See precomputed card",
                        overall_confidence=card_hit.get("confidence", 0.9),
                        headline=card_hit.get("headline", ""),
                    )
                    return IntegratedResponse(
                        template_response=stub_response,
                        article_evidence=[],
                        total_supporting_papers=0,
                        evidence_quality_summary="Precomputed card — full evidence embedded",
                        bn_posterior=None,
                        bn_prior=None,
                        bn_likelihood_ratio=None,
                        panel_comments=[],
                        panel_synthesis=card_hit.get("headline", ""),
                        panel_debates=[],
                        open_questions=card_hit.get("follow_ups", []),
                        persona_enrichment=card_hit,
                    )
            except Exception as e:
                logger.debug(f"Card fast-path failed, falling through: {e}")

        # ── Standard pipeline (live enrichment) ──
        # Get base template response
        if self.use_embeddings:
            # Use semantic search to find relevant templates
            semantic_matches = self._semantic_search_templates(query_text, top_k=5)
            # Extract keywords from top matches for the template service
            keywords = []
            for tid, score in semantic_matches[:3]:
                template = self.templates.get(tid, {})
                name = template.get('name', '')
                keywords.extend(name.lower().split()[:5])
            template_response = self.template_service.query(query_text, keywords=list(set(keywords)))
        else:
            template_response = self.template_service.query(query_text)

        # Find article evidence
        article_evidence = []
        if include_articles and template_response.relevant_templates:
            for ans in template_response.relevant_templates[:3]:
                evidence = self._find_article_evidence(ans)
                article_evidence.extend(evidence)

        # Count unique papers
        paper_ids = set()
        for ev in article_evidence:
            paper_ids.update(ev.paper_ids)

        # Evidence quality summary
        if not article_evidence:
            evidence_summary = "No article evidence found — template-based reasoning only"
        elif len(paper_ids) < 3:
            evidence_summary = f"Limited evidence: {len(paper_ids)} paper(s) found"
        else:
            avg_credence = sum(e.credence for e in article_evidence) / len(article_evidence)
            evidence_summary = f"Moderate evidence: {len(paper_ids)} papers, avg credence {avg_credence:.0%}"

        # Generate panel discussion
        panel_comments = []
        panel_synthesis = ""
        panel_debates = []
        open_questions = []

        if include_panel:
            panel_comments = self._generate_panel_comments(template_response)
            panel_synthesis, panel_debates, open_questions = self._synthesize_panel(panel_comments)

        # Sprint QA-2/QA-4: Generate persona enrichment if persona specified
        persona_enrichment = None
        if persona is not None:
            try:
                persona_enrichment = self.template_service.enrich_response(
                    template_response, persona
                )
            except Exception as e:
                logger.warning(f"Persona enrichment failed: {e}")

        # Fix 5 (Codex V13): Abstention for zero-evidence queries
        # When no article evidence supports the template answer, collapse confidence
        # and flag the response as evidence-unsupported to prevent hallucinated certainty.
        abstention_applied = False
        if len(paper_ids) == 0 and template_response.relevant_templates:
            original_conf = template_response.overall_confidence
            template_response.overall_confidence = min(original_conf, 0.20)
            evidence_summary = (
                f"⚠️ ABSTENTION: No article evidence found. "
                f"Template-based reasoning only (confidence collapsed from "
                f"{original_conf:.0%} to {template_response.overall_confidence:.0%}). "
                f"Treat as speculative."
            )
            abstention_applied = True
            logger.warning(
                f"Abstention triggered for query '{query_text[:50]}': "
                f"0 supporting papers, confidence collapsed {original_conf:.2f} → "
                f"{template_response.overall_confidence:.2f}"
            )

        return IntegratedResponse(
            template_response=template_response,
            article_evidence=article_evidence[:10],
            total_supporting_papers=len(paper_ids),
            evidence_quality_summary=evidence_summary,
            bn_posterior=None,  # TODO: Connect to BN
            bn_prior=None,
            bn_likelihood_ratio=None,
            panel_comments=panel_comments,
            panel_synthesis=panel_synthesis,
            panel_debates=panel_debates,
            open_questions=open_questions,
            persona_enrichment=persona_enrichment,
        )

    def format_full_response(self, response: IntegratedResponse) -> str:
        """Format the full integrated response with panel discussion.

        SUCCESS CONDITIONS:
        SC-FFR-1: Returns a non-empty string (never "" or None)
        SC-FFR-2: Output contains the query text from template_response
        SC-FFR-3: Output contains headline from template_response
        SC-FFR-4: Output contains evidence_quality_summary
        SC-FFR-5: When panel_comments present, output contains "T1 PANEL DISCUSSION" header
        SC-FFR-6: When article_evidence present, output contains "ARTICLE EVIDENCE" header
        SC-FFR-7: Output is valid text (no exceptions raised during formatting)
        """
        lines = []
        tr = response.template_response

        # Header
        lines.extend([
            "=" * 76,
            f"QUERY: {tr.query}",
            "=" * 76,
            "",
            f"HEADLINE: {tr.headline}",
            f"CONFIDENCE: {tr.overall_confidence:.0%}",
            f"EVIDENCE: {response.evidence_quality_summary}",
        ])

        # Core answer (Level 2)
        lines.extend([
            "",
            "─" * 76,
            "MECHANISM (HOW)",
            "─" * 76,
            f"  {tr.how}",
            "",
            f"  Chain: {tr.causal_chain}",
        ])

        lines.extend([
            "",
            "─" * 76,
            "PRINCIPLE (WHY)",
            "─" * 76,
        ])
        why = tr.why[:300] + "..." if len(tr.why) > 300 else tr.why
        for i in range(0, len(why), 70):
            lines.append(f"  {why[i:i+70]}")

        lines.extend([
            "",
            "─" * 76,
            "CONDITIONS (WHEN)",
            "─" * 76,
        ])
        for w in tr.when[:4]:
            lines.append(f"  • {w[:70]}{'...' if len(w) > 70 else ''}")

        lines.extend([
            "",
            "─" * 76,
            "INDIVIDUAL DIFFERENCES (FOR WHOM)",
            "─" * 76,
        ])
        for w in tr.for_whom[:4]:
            lines.append(f"  • {w[:70]}{'...' if len(w) > 70 else ''}")

        # Article evidence (Level 3)
        if response.article_evidence:
            lines.extend([
                "",
                "─" * 76,
                f"ARTICLE EVIDENCE ({response.total_supporting_papers} papers)",
                "─" * 76,
            ])
            for ev in response.article_evidence[:5]:
                lines.append(f"  [{ev.level}] {ev.content[:60]}...")
                lines.append(f"       Credence: {ev.credence:.0%} ± {ev.credence_uncertainty:.0%}")

        # Neuroscience (Level 4)
        if tr.neuroscience_details:
            lines.extend([
                "",
                "─" * 76,
                "NEUROSCIENCE DETAILS",
                "─" * 76,
            ])
            for detail in tr.neuroscience_details[:4]:
                lines.append(f"  • {detail.link_summary}")
                if detail.neural_substrate:
                    lines.append(f"    Neural: {detail.neural_substrate}")
                lines.append(f"    Maturity: {detail.maturity}")

        # Panel Discussion (the exciting part!)
        if response.panel_comments:
            lines.extend([
                "",
                "═" * 76,
                "T1 PANEL DISCUSSION",
                "═" * 76,
            ])

            for comment in response.panel_comments:
                lines.extend([
                    "",
                    f"┌─ {comment.framework_name.upper()} ─────────────────────────────────────",
                    f"│",
                ])
                # Perspective
                persp = comment.perspective
                for i in range(0, len(persp), 68):
                    lines.append(f"│ {persp[i:i+68]}")

                # Complications
                if comment.complications:
                    lines.append(f"│")
                    lines.append(f"│ COMPLICATIONS:")
                    for comp in comment.complications[:2]:
                        lines.append(f"│   ⚡ {comp[:65]}...")

                # Speculation
                lines.append(f"│")
                lines.append(f"│ SPECULATION:")
                spec = comment.speculation
                for i in range(0, min(len(spec), 140), 68):
                    lines.append(f"│   💭 {spec[i:i+68]}")

                # Limitations
                if comment.limitations:
                    lines.append(f"│")
                    lines.append(f"│ LIMITATIONS:")
                    for lim in comment.limitations[:2]:
                        lines.append(f"│   ⚠ {lim[:65]}...")

                lines.append(f"│")
                lines.append(f"│ KEY QUESTION: {comment.key_question}")
                lines.append(f"└" + "─" * 70)

            # Panel synthesis
            lines.extend([
                "",
                "─" * 76,
                "PANEL SYNTHESIS",
                "─" * 76,
            ])
            synth = response.panel_synthesis
            for i in range(0, len(synth), 70):
                lines.append(f"  {synth[i:i+70]}")

            if response.panel_debates:
                lines.extend(["", "DEBATES:"])
                for debate in response.panel_debates[:3]:
                    lines.append(f"  ⚔ {debate}")

            if response.open_questions:
                lines.extend(["", "OPEN QUESTIONS:"])
                for q in response.open_questions[:4]:
                    lines.append(f"  ? {q}")

        # Research gaps (Level 5)
        if tr.research_gaps_detailed:
            lines.extend([
                "",
                "─" * 76,
                "RESEARCH NEEDED",
                "─" * 76,
            ])
            for gap in tr.research_gaps_detailed[:4]:
                lines.append(f"  [{gap.priority.upper()}] {gap.description[:55]}...")
                lines.append(f"       Proposed: {gap.proposed_study[:55]}...")

        # Sprint QA-2/QA-4: Persona Enrichment
        if response.persona_enrichment:
            pe = response.persona_enrichment
            lines.extend([
                "",
                "─" * 76,
                f"PERSONA ENRICHMENT ({pe.get('persona', '?').upper()})",
                "─" * 76,
            ])
            # Display based on persona type
            if 'thresholds' in pe and pe['thresholds']:
                lines.append(f"  Quantitative thresholds: {pe.get('n_thresholds', 0)} extracted")
                for t in pe['thresholds'][:4]:
                    lines.append(
                        f"    • {t['parameter']}: {t['value']} {t['unit'][:30]}"
                        f"  [conf: {t['confidence']:.0%}]"
                    )
            if 'grade_ratings' in pe and pe['grade_ratings']:
                lines.append("  GRADE Evidence Ratings:")
                for gr in pe['grade_ratings'][:3]:
                    lines.append(f"    {gr['maturity_source']} → {gr['grade']}")
            if 'contraindications' in pe and pe['contraindications']:
                lines.append(f"  ⚠️  Contraindications: {len(pe['contraindications'])} flagged")
                for c in pe['contraindications'][:3]:
                    lines.append(f"    {c['severity'].upper()}: {c['condition']}")
            if 'proxy_metrics' in pe and pe['proxy_metrics']:
                lines.append("  Measurable KPIs:")
                for pm in pe['proxy_metrics'][:3]:
                    lines.append(f"    {pm['scientific_outcome']} → {', '.join(pm['measurable_kpis'][:2])}")
            if 'glossary' in pe and pe['glossary']:
                lines.append(f"  Glossary: {len(pe['glossary'])} terms defined")
            if 'standards' in pe and pe['standards']:
                lines.append(f"  Applicable standards: {len(pe['standards'])}")
                for s in pe['standards'][:3]:
                    lines.append(f"    • {s['standard']} ({s['jurisdiction']})")
            # Provenance
            if 'template_provenance' in pe:
                n_tmpl = len(pe['template_provenance'])
                lines.append(f"  Provenance: {n_tmpl} templates contributing")

        return "\n".join(lines)

    def get_theoretical_voices(self, topic: str, limit: int = 4) -> Dict:
        """
        Bridge method for AnswerEnrichmentOrchestrator Step 4.

        Returns a dictionary of framework perspectives keyed by framework name,
        each with 'perspective', 'complications', 'key_question', and 'speculation'.

        Args:
            topic: The topic to generate framework voices for
            limit: Maximum number of frameworks to include

        Returns:
            Dict[str, Dict] mapping framework abbreviation to its voice data
        """
        # Attempt 1: Load pre-computed corpus-grounded MV data
        try:
            from src.qa.mv_builder import MaterializedViewBuilder
            builder = MaterializedViewBuilder()
            mv_data = builder.get_view("framework_voices")

            if mv_data and "data" in mv_data and mv_data.get("status") == "FRESH":
                fw_voices = mv_data["data"]
                if isinstance(fw_voices, dict) and "error" not in fw_voices:
                    return self._select_relevant_frameworks(fw_voices, topic, limit)
        except Exception as e:
            logger.debug(f"MV framework voices not available: {e}")

        # Attempt 2: Build on-the-fly from corpus (slower but still grounded)
        try:
            from src.qa.mv_builder import MaterializedViewBuilder
            builder = MaterializedViewBuilder()
            fw_voices = builder.build_framework_voices()
            if isinstance(fw_voices, dict) and "error" not in fw_voices:
                return self._select_relevant_frameworks(fw_voices, topic, limit)
        except Exception as e:
            logger.debug(f"On-the-fly framework voice build failed: {e}")

        # Fallback: Use FRAMEWORK_VOICES dict with quarantine label
        logger.warning(
            "Framework voices falling back to templated mode — "
            "corpus-grounded data unavailable"
        )
        voices = {}
        frameworks = list(FRAMEWORK_VOICES.keys())[:limit]

        for fw in frameworks:
            voice = FRAMEWORK_VOICES[fw]
            voices[voice['name']] = {
                'perspective': (
                    f"From {voice['name']}: {voice['core_claim']}."
                ),
                'key_figures': voice.get('key_figures', []),
                'core_claim': voice.get('core_claim', ''),
                'complications': voice.get('complications', []),
                'key_question': voice.get('typical_questions', [''])[0],
                'implications': [],
                'n_papers': 0,
                'n_findings': 0,
                'source': 'framework_template',
                'quarantine_notice': (
                    '⚠️ TEMPLATED — This perspective is a generic framework '
                    'description, not grounded in corpus evidence for this topic.'
                ),
            }

        logger.info(f"Generated {len(voices)} TEMPLATED theoretical voices for topic: {topic[:50]}")
        return voices

    def _select_relevant_frameworks(
        self,
        fw_voices: Dict[str, Any],
        topic: str,
        limit: int,
    ) -> Dict[str, Dict]:
        """
        Select the most relevant frameworks for a given topic from
        pre-computed corpus-grounded voice data.

        Ranks frameworks by how many findings match topic keywords.
        """
        topic_words = set(topic.lower().split())

        scored = []
        for abbr, data in fw_voices.items():
            if not isinstance(data, dict):
                continue

            # Score by topic keyword overlap with top findings
            relevance = 0
            top_findings = data.get("top_findings", [])
            for finding in top_findings:
                ant = finding.get("antecedent", "").lower()
                cons = finding.get("consequent", "").lower()
                relevance += sum(1 for w in topic_words if w in ant or w in cons)

            # Bonus for frameworks with more evidence
            evidence_bonus = min(data.get("n_papers", 0) / 10, 2.0)

            scored.append((abbr, data, relevance + evidence_bonus))

        # Sort by relevance, then by n_papers as tiebreaker
        scored.sort(key=lambda x: (-x[2], -x[1].get("n_papers", 0)))

        voices = {}
        for abbr, data, score in scored[:limit]:
            voices[data.get("name", abbr)] = {
                'perspective': self._render_corpus_perspective(data),
                'core_mechanism': data.get("core_mechanism", ""),
                'key_principle': data.get("key_principle", ""),
                'n_papers': data.get("n_papers", 0),
                'n_findings': data.get("n_findings", 0),
                'top_findings': data.get("top_findings", [])[:3],
                'mechanism_chains': data.get("mechanism_chains", [])[:3],
                'scope_conditions': data.get("scope_conditions", [])[:3],
                'source': 'corpus_grounded',
                'relevance_score': round(score, 2),
            }

        logger.info(
            f"Selected {len(voices)} corpus-grounded voices for topic: {topic[:50]}"
        )
        return voices

    def _render_corpus_perspective(self, fw_data: Dict) -> str:
        """
        Render a structured perspective string from corpus-grounded data.
        This is the replacement for the hardcoded if/elif chain.
        """
        name = fw_data.get("name", "Unknown")
        n_papers = fw_data.get("n_papers", 0)
        n_findings = fw_data.get("n_findings", 0)

        if n_papers == 0:
            return (
                f"{name}: No papers in the corpus address this topic through "
                f"this framework. The framework's core mechanism is: "
                f"{fw_data.get('core_mechanism', 'unspecified')}."
            )

        # Build perspective from actual evidence
        parts = [f"{name} — {n_papers} paper(s), {n_findings} finding(s) address this."]

        top = fw_data.get("top_findings", [])
        if top:
            best = top[0]
            effect_str = ""
            if best.get("effect_size") is not None:
                effect_str = f" (d = {best['effect_size']:.2f})"
            parts.append(
                f"Key finding: {best.get('antecedent', '?')} → "
                f"{best.get('consequent', '?')}{effect_str}."
            )

        mechanisms = fw_data.get("mechanism_chains", [])
        if mechanisms:
            parts.append(f"Mechanism: {mechanisms[0]}.")

        conditions = fw_data.get("scope_conditions", [])
        if conditions:
            parts.append(f"Scope condition: {conditions[0]}.")

        return " ".join(parts)


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def ask_integrated(
    question: str,
    include_panel: bool = True,
    persona: UserPersona = None,
    verbose: bool = True
) -> IntegratedResponse:
    """
    Ask a question with full integration: templates + articles + panel discussion.

    Usage:
        from src.services.integrated_query_service import ask_integrated
        response = ask_integrated("When do high ceilings increase creativity?")
        # With persona enrichment:
        response = ask_integrated("...", persona=UserPersona.ARCHITECT)
    """
    service = IntegratedQueryService()
    response = service.query(question, include_panel=include_panel, persona=persona)

    if verbose:
        print(service.format_full_response(response))

    return response


if __name__ == "__main__":
    # Demo
    ask_integrated("When do high ceilings increase creativity and for whom?")

