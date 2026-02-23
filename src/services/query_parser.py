"""
Query Parser Service
====================

Natural language query parsing for the Web of Belief.

Per expert panel:
- Hybrid approach: rule-based first, LLM fallback for unparseable (Q1)
- Show vocabulary expansion transparently (Bates, Q3)

Sprint 3.0.2 additions (per Pearl):
- Causal level detection: associational, interventional, counterfactual
- Query type must distinguish question semantics from causal semantics

Date: January 21, 2026 (original)
Updated: February 9, 2026 (Sprint 3.0.2-A)
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# Query Types
# =============================================================================

class QueryType(Enum):
    """Types of queries the system can handle."""
    # Factual queries about beliefs
    WHAT_IS = "what_is"              # "What is the effect of X on Y?"
    DOES_X_AFFECT_Y = "does_affect"  # "Does natural light affect productivity?"
    HOW_MUCH = "how_much"            # "How much does X affect Y?"

    # Exploratory queries
    WHAT_DO_WE_KNOW = "what_know"    # "What do we know about biophilic design?"
    WHAT_EVIDENCE = "what_evidence"  # "What evidence supports X?"

    # Comparative queries
    COMPARE = "compare"              # "Compare X and Y effects"
    WHICH_IS_BETTER = "which_better" # "Which is better for Z: X or Y?"

    # Meta queries
    HOW_CONFIDENT = "confidence"     # "How confident are we about X?"
    WHY_BELIEVE = "why_believe"      # "Why do we believe X?"
    WHAT_CONTRADICTS = "contradicts" # "What contradicts X?"

    # Gap queries
    WHAT_DONT_KNOW = "what_unknown"  # "What don't we know about X?"

    # Scope queries
    WHEN_DOES = "when_does"          # "When does X work?"
    FOR_WHOM = "for_whom"            # "For whom does X work?"

    # Unknown (needs LLM or clarification)
    UNKNOWN = "unknown"


class CausalLevel(Enum):
    """
    Causal level of a query (per Pearl's ladder of causation).

    This is orthogonal to QueryType—a WHAT_IS query can be at any causal level:
    - "What is correlated with stress?" → ASSOCIATIONAL
    - "What would happen if we added plants?" → INTERVENTIONAL
    - "Would stress have reduced without the windows?" → COUNTERFACTUAL
    """
    # Rung 1: Observation/correlation
    ASSOCIATIONAL = "associational"      # "What is correlated with X?"

    # Rung 2: Intervention
    INTERVENTIONAL = "interventional"    # "What would happen if we do X?"

    # Rung 3: Counterfactual
    COUNTERFACTUAL = "counterfactual"    # "Would Y have happened if we hadn't done X?"

    # Descriptive/definitional (not causal)
    DESCRIPTIVE = "descriptive"          # "What is biophilia?"

    # Unable to determine
    UNKNOWN = "unknown"


@dataclass
class QueryIntent:
    """Parsed query intent."""
    query_type: QueryType
    confidence: float  # 0-1 confidence in parse

    # Causal level per Pearl (Sprint 3.0.2)
    causal_level: CausalLevel = CausalLevel.UNKNOWN

    # Extracted entities
    subject: Optional[str] = None          # Main topic/variable
    object: Optional[str] = None           # Secondary topic/outcome
    modifier: Optional[str] = None         # Qualifiers (e.g., "significantly")

    # Expanded terms (vocabulary bridge)
    subject_expansions: List[str] = field(default_factory=list)
    object_expansions: List[str] = field(default_factory=list)

    # Original query
    original_query: str = ""
    normalized_query: str = ""

    # Parse metadata
    matched_pattern: Optional[str] = None
    parse_method: str = "rule_based"

    def to_dict(self) -> Dict[str, Any]:
        return {
            'query_type': self.query_type.value,
            'causal_level': self.causal_level.value,
            'confidence': self.confidence,
            'subject': self.subject,
            'object': self.object,
            'modifier': self.modifier,
            'subject_expansions': self.subject_expansions,
            'object_expansions': self.object_expansions,
            'original_query': self.original_query,
            'normalized_query': self.normalized_query,
            'matched_pattern': self.matched_pattern,
            'parse_method': self.parse_method
        }


@dataclass
class ParseResult:
    """Complete parse result with alternatives."""
    primary: QueryIntent
    alternatives: List[QueryIntent] = field(default_factory=list)
    vocabulary_expansions: Dict[str, List[str]] = field(default_factory=dict)
    needs_clarification: bool = False
    clarification_options: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'primary': self.primary.to_dict(),
            'alternatives': [a.to_dict() for a in self.alternatives],
            'vocabulary_expansions': self.vocabulary_expansions,
            'needs_clarification': self.needs_clarification,
            'clarification_options': self.clarification_options
        }


# =============================================================================
# Vocabulary Bridge (per Bates)
# =============================================================================

# Domain-specific synonym mappings
VOCABULARY_BRIDGE = {
    # Environment terms
    'natural light': ['daylight', 'sunlight', 'daylighting', 'natural lighting'],
    'daylight': ['natural light', 'sunlight', 'daylighting'],
    'plants': ['vegetation', 'greenery', 'indoor plants', 'biophilia'],
    'greenery': ['plants', 'vegetation', 'green spaces'],
    'noise': ['sound', 'acoustic', 'auditory'],
    'temperature': ['thermal', 'heat', 'cold', 'thermal comfort'],
    'open office': ['open plan', 'open-plan office', 'open workspace'],
    'views': ['windows', 'visual access', 'prospect'],
    'nature': ['biophilia', 'natural elements', 'natural environment'],

    # Material / texture terms (biophilic design)
    'wood': ['timber', 'wooden', 'wood prominent', 'wood treatment', 'natural wood',
             'wood paneling', 'wood grain', 'grained wood', 'wood surface',
             'natural materials', 'wood_prominent'],
    'timber': ['wood', 'wooden', 'natural wood', 'wood prominent'],
    'grained wood': ['wood', 'timber', 'wood grain', 'wood prominent', 'natural wood'],
    'beautiful wood': ['wood', 'timber', 'wood prominent', 'natural wood', 'wood grain'],
    'natural materials': ['wood', 'timber', 'stone', 'natural wood',
                          'natural_materials_wood_stone'],
    'stone': ['natural materials', 'natural stone', 'rock'],
    'biophilic design': ['nature', 'natural elements', 'wood', 'plants',
                         'natural materials', 'biophilia'],

    # Outcome terms
    'productivity': ['performance', 'work output', 'efficiency', 'task performance'],
    'stress': ['anxiety', 'tension', 'psychological stress', 'cortisol'],
    'wellbeing': ['well-being', 'wellness', 'health', 'satisfaction'],
    'mood': ['affect', 'emotional state', 'feelings'],
    'attention': ['focus', 'concentration', 'cognitive focus'],
    'creativity': ['creative thinking', 'innovation', 'divergent thinking'],
    'sleep': ['sleep quality', 'circadian', 'rest'],
    'recovery': ['healing', 'recuperation', 'restoration'],
    'restorative': ['restoration', 'recovery', 'stress recovery', 'healing',
                    'attention restoration', 'ART'],
    'restoration': ['restorative', 'recovery', 'stress recovery',
                    'attention restoration', 'ART', 'recuperation'],

    # Population terms
    'workers': ['employees', 'office workers', 'staff'],
    'students': ['learners', 'pupils', 'schoolchildren'],
    'patients': ['hospital patients', 'healthcare recipients'],
    'elderly': ['older adults', 'seniors', 'aging population'],
    'children': ['kids', 'youth', 'minors'],
}


def expand_term(term: str) -> List[str]:
    """
    Expand a term using vocabulary bridge.

    Per Bates (Q3): Show vocabulary expansion transparently.
    """
    term_lower = term.lower().strip()
    expansions = []

    # Direct match
    if term_lower in VOCABULARY_BRIDGE:
        expansions.extend(VOCABULARY_BRIDGE[term_lower])

    # Partial match (term contains a key)
    for key, synonyms in VOCABULARY_BRIDGE.items():
        if key in term_lower and key != term_lower:
            expansions.extend(synonyms)
        # Or term is a synonym
        if term_lower in synonyms:
            expansions.append(key)
            expansions.extend([s for s in synonyms if s != term_lower])

    return list(set(expansions))


# =============================================================================
# Query Patterns
# =============================================================================

# Pattern definitions: (regex, query_type, subject_group, object_group)
QUERY_PATTERNS = [
    # WHAT_IS patterns
    (r"what\s+(?:is|are)\s+(?:the\s+)?(?:effect|effects|impact|impacts)\s+of\s+(.+?)\s+on\s+(.+?)(?:\?|$)",
     QueryType.WHAT_IS, 1, 2),
    (r"what\s+(?:does|do)\s+(.+?)\s+(?:do|affect|impact)\s+(?:to|on|for)\s+(.+?)(?:\?|$)",
     QueryType.WHAT_IS, 1, 2),
    (r"what\s+(?:is|are)\s+(.+?)(?:\?|$)",
     QueryType.WHAT_IS, 1, None),

    # DOES_X_AFFECT_Y patterns
    (r"(?:does|do|can|will)\s+(.+?)\s+(?:affect|impact|influence|improve|reduce|increase|decrease)\s+(.+?)(?:\?|$)",
     QueryType.DOES_X_AFFECT_Y, 1, 2),
    (r"(?:is|are)\s+(.+?)\s+(?:related|linked|connected)\s+to\s+(.+?)(?:\?|$)",
     QueryType.DOES_X_AFFECT_Y, 1, 2),

    # HOW_MUCH patterns
    (r"how\s+(?:much|strongly|significantly)\s+(?:does|do)\s+(.+?)\s+(?:affect|impact|influence)\s+(.+?)(?:\?|$)",
     QueryType.HOW_MUCH, 1, 2),
    (r"(?:what|how)\s+(?:is|are)\s+(?:the\s+)?(?:magnitude|size|strength)\s+of\s+(?:the\s+)?(?:effect|relationship)\s+(?:of|between)\s+(.+?)\s+(?:on|and)\s+(.+?)(?:\?|$)",
     QueryType.HOW_MUCH, 1, 2),

    # WHAT_DO_WE_KNOW patterns
    (r"what\s+(?:do\s+we\s+know|is\s+known)\s+about\s+(.+?)(?:\?|$)",
     QueryType.WHAT_DO_WE_KNOW, 1, None),
    (r"(?:tell\s+me|summarize|overview)\s+(?:about|of)\s+(.+?)(?:\?|$)",
     QueryType.WHAT_DO_WE_KNOW, 1, None),

    # WHAT_EVIDENCE patterns
    (r"what\s+(?:evidence|research|studies|papers)\s+(?:support|supports|show|shows|demonstrate|demonstrates|suggest|suggests)\s+(?:the\s+claim\s+that\s+)?(.+?)(?:\?|$)",
     QueryType.WHAT_EVIDENCE, 1, None),
    (r"(?:is\s+there|what\s+is\s+the)\s+evidence\s+(?:for|that|about)\s+(.+?)(?:\?|$)",
     QueryType.WHAT_EVIDENCE, 1, None),

    # COMPARE patterns
    (r"compare\s+(.+?)\s+(?:and|with|to|vs\.?)\s+(.+?)(?:\?|$)",
     QueryType.COMPARE, 1, 2),
    (r"(?:what\s+(?:is|are)\s+)?(?:the\s+)?difference(?:s)?\s+between\s+(.+?)\s+and\s+(.+?)(?:\?|$)",
     QueryType.COMPARE, 1, 2),

    # WHICH_IS_BETTER patterns
    (r"which\s+is\s+(?:better|more\s+effective|preferable)\s+(?:for\s+(.+?)\s*[:\-]?\s*)?(.+?)\s+or\s+(.+?)(?:\?|$)",
     QueryType.WHICH_IS_BETTER, 2, 3),  # Note: group 1 is optional context
    (r"(?:should\s+I|is\s+it\s+better\s+to)\s+(?:use|choose|prefer)\s+(.+?)\s+or\s+(.+?)(?:\?|$)",
     QueryType.WHICH_IS_BETTER, 1, 2),
    # "which is more [adjective] X or Y?" — comparative quality queries
    (r"which\s+is\s+more\s+\w+\s+(.+?)\s+or\s+(.+?)(?:\?|$)",
     QueryType.WHICH_IS_BETTER, 1, 2),
    (r"(?:is|are)\s+(.+?)\s+(?:more|less)\s+\w+\s+than\s+(.+?)(?:\?|$)",
     QueryType.WHICH_IS_BETTER, 1, 2),

    # HOW_CONFIDENT patterns
    (r"how\s+(?:confident|certain|sure)\s+(?:are\s+we|is\s+the\s+evidence)\s+(?:about|that|in)\s+(.+?)(?:\?|$)",
     QueryType.HOW_CONFIDENT, 1, None),
    (r"(?:what|how)\s+(?:is|strong)\s+(?:is\s+)?(?:the\s+)?(?:confidence|certainty|evidence\s+quality)\s+(?:for|about|in)\s+(.+?)(?:\?|$)",
     QueryType.HOW_CONFIDENT, 1, None),

    # WHY_BELIEVE patterns
    (r"why\s+(?:do\s+we|should\s+I)\s+(?:believe|think|accept)\s+(?:that\s+)?(.+?)(?:\?|$)",
     QueryType.WHY_BELIEVE, 1, None),
    (r"(?:what|where)\s+(?:is|are)\s+(?:the\s+)?(?:basis|grounds|reasons?)\s+for\s+(?:believing\s+)?(.+?)(?:\?|$)",
     QueryType.WHY_BELIEVE, 1, None),

    # MECHANISM patterns — "what mechanism explains why X?", "how does X cause Y?"
    # "why is wood restorative?", "do plants and wood share the same mechanism?"
    (r"(?:what|which)\s+mechanism\s+(?:explains?|underlies?|accounts?\s+for)\s+(?:why\s+)?(.+?)(?:\?|$)",
     QueryType.WHY_BELIEVE, 1, None),
    (r"how\s+does\s+(.+?)\s+(?:cause|produce|lead to|result in|trigger|mediate)\s+(.+?)(?:\?|$)",
     QueryType.DOES_X_AFFECT_Y, 1, 2),
    (r"why\s+(?:is|are|does|do)\s+(.+?)\s+(?:restorative|calming|stress.reducing|beneficial|helpful)(?:\?|$)",
     QueryType.WHY_BELIEVE, 1, None),
    (r"(?:do|does)\s+(.+?)\s+and\s+(.+?)\s+(?:share|use|work through)\s+(?:the\s+)?same\s+(?:mechanism|route|pathway|process)(?:\?|$)",
     QueryType.COMPARE, 1, 2),
    (r"(?:is|are)\s+(?:the\s+)?(?:mechanism|route|pathway|process)\s+(?:for|behind)\s+(.+?)\s+(?:the\s+)?same\s+as\s+(?:for\s+)?(.+?)(?:\?|$)",
     QueryType.COMPARE, 1, 2),

    # WHAT_CONTRADICTS patterns
    (r"what\s+(?:contradicts|conflicts\s+with|challenges|disputes)\s+(.+?)(?:\?|$)",
     QueryType.WHAT_CONTRADICTS, 1, None),
    (r"(?:is|are)\s+there\s+(?:any\s+)?(?:contradictions?|conflicts?|disagreements?)\s+(?:about|with|regarding)\s+(.+?)(?:\?|$)",
     QueryType.WHAT_CONTRADICTS, 1, None),

    # WHAT_DONT_KNOW patterns (gap queries)
    (r"what\s+(?:don't|do\s+not)\s+we\s+know\s+about\s+(.+?)(?:\?|$)",
     QueryType.WHAT_DONT_KNOW, 1, None),
    (r"what\s+(?:are\s+)?(?:the\s+)?(?:gaps|unknowns|uncertainties)\s+(?:in|about|regarding)\s+(.+?)(?:\?|$)",
     QueryType.WHAT_DONT_KNOW, 1, None),

    # WHEN_DOES patterns (scope queries)
    (r"when\s+does\s+(.+?)\s+(?:work|apply|hold|happen)(?:\?|$)",
     QueryType.WHEN_DOES, 1, None),
    (r"under\s+what\s+(?:conditions|circumstances)\s+does\s+(.+?)(?:\?|$)",
     QueryType.WHEN_DOES, 1, None),

    # FOR_WHOM patterns (scope queries)
    (r"(?:for\s+whom|who)\s+does\s+(.+?)\s+(?:work|apply|benefit)(?:\?|$)",
     QueryType.FOR_WHOM, 1, None),
    (r"(?:which|what)\s+(?:populations?|groups?|people)\s+(?:does|do)\s+(.+?)\s+(?:affect|benefit|help)(?:\?|$)",
     QueryType.FOR_WHOM, 1, None),
]


# =============================================================================
# Query Parser
# =============================================================================

class QueryParser:
    """
    Natural language query parser.

    Uses rule-based pattern matching with vocabulary expansion.
    Falls back to UNKNOWN type for unparseable queries (LLM fallback in future).
    """

    def __init__(self, vocabulary_bridge: Optional[Dict[str, List[str]]] = None):
        """
        Initialize parser.

        Args:
            vocabulary_bridge: Custom vocabulary mappings (uses default if None)
        """
        self.vocabulary = vocabulary_bridge or VOCABULARY_BRIDGE
        self.patterns = [(re.compile(p, re.IGNORECASE), qt, sg, og)
                         for p, qt, sg, og in QUERY_PATTERNS]

    def parse(self, query: str) -> ParseResult:
        """
        Parse a natural language query.

        Args:
            query: The user's query string

        Returns:
            ParseResult with primary intent and alternatives
        """
        # Normalize query
        normalized = self._normalize(query)

        # Try all patterns
        matches = []
        for pattern, query_type, subject_group, object_group in self.patterns:
            match = pattern.search(normalized)
            if match:
                intent = self._build_intent(
                    query, normalized, match, query_type,
                    subject_group, object_group, pattern.pattern
                )
                matches.append(intent)

        # If no matches, return UNKNOWN
        if not matches:
            # Still try to detect causal level even if query type is unknown
            causal_level = self._detect_causal_level(query, QueryType.UNKNOWN)
            unknown_intent = QueryIntent(
                query_type=QueryType.UNKNOWN,
                causal_level=causal_level,
                confidence=0.0,
                original_query=query,
                normalized_query=normalized,
                parse_method="rule_based"
            )
            # Try to extract any noun phrases as potential subjects
            unknown_intent.subject = self._extract_main_topic(normalized)

            return ParseResult(
                primary=unknown_intent,
                needs_clarification=True,
                clarification_options=self._generate_clarifications(query)
            )

        # Sort by confidence and select primary
        matches.sort(key=lambda x: x.confidence, reverse=True)
        primary = matches[0]
        alternatives = matches[1:3]  # Keep top 3 alternatives

        # Collect all vocabulary expansions
        all_expansions = {}
        if primary.subject:
            exps = expand_term(primary.subject)
            if exps:
                all_expansions[primary.subject] = exps
        if primary.object:
            exps = expand_term(primary.object)
            if exps:
                all_expansions[primary.object] = exps

        return ParseResult(
            primary=primary,
            alternatives=alternatives,
            vocabulary_expansions=all_expansions,
            needs_clarification=primary.confidence < 0.6
        )

    def _normalize(self, query: str) -> str:
        """Normalize query for matching."""
        # Lowercase
        normalized = query.lower().strip()
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized)
        # Standardize punctuation
        normalized = re.sub(r'["""]', '"', normalized)
        normalized = re.sub(r"[''']", "'", normalized)
        return normalized

    def _build_intent(
        self,
        original: str,
        normalized: str,
        match: re.Match,
        query_type: QueryType,
        subject_group: Optional[int],
        object_group: Optional[int],
        pattern: str
    ) -> QueryIntent:
        """Build QueryIntent from regex match."""
        subject = None
        obj = None

        try:
            if subject_group is not None:
                subject = match.group(subject_group).strip()
            if object_group is not None:
                obj = match.group(object_group).strip()
        except IndexError:
            pass

        # Calculate confidence based on match quality
        confidence = self._calculate_confidence(normalized, match, query_type)

        # Detect causal level (Sprint 3.0.2-A per Pearl)
        causal_level = self._detect_causal_level(original, query_type)

        # Expand vocabulary
        subject_expansions = expand_term(subject) if subject else []
        object_expansions = expand_term(obj) if obj else []

        return QueryIntent(
            query_type=query_type,
            causal_level=causal_level,
            confidence=confidence,
            subject=subject,
            object=obj,
            subject_expansions=subject_expansions,
            object_expansions=object_expansions,
            original_query=original,
            normalized_query=normalized,
            matched_pattern=pattern,
            parse_method="rule_based"
        )

    def _calculate_confidence(
        self,
        normalized: str,
        match: re.Match,
        query_type: QueryType
    ) -> float:
        """Calculate confidence score for a match."""
        # Start with base confidence
        confidence = 0.7

        # Higher confidence for longer matches (more specific)
        match_length = match.end() - match.start()
        query_length = len(normalized)
        coverage = match_length / query_length if query_length > 0 else 0
        confidence += coverage * 0.2

        # Higher confidence for specific query types
        specific_types = {
            QueryType.DOES_X_AFFECT_Y,
            QueryType.HOW_MUCH,
            QueryType.COMPARE
        }
        if query_type in specific_types:
            confidence += 0.05

        # Cap at 0.95
        return min(confidence, 0.95)

    def _extract_main_topic(self, query: str) -> Optional[str]:
        """Extract main topic from unparsed query."""
        # Remove common question words
        cleaned = re.sub(
            r'^(what|how|why|when|where|who|does|do|is|are|can|will|should)\s+',
            '', query, flags=re.IGNORECASE
        )
        cleaned = re.sub(r'\?$', '', cleaned).strip()

        # Return first significant chunk
        if cleaned:
            # Take first noun phrase (simplified)
            words = cleaned.split()
            if len(words) <= 5:
                return cleaned
            else:
                return ' '.join(words[:5])
        return None

    def _generate_clarifications(self, query: str) -> List[str]:
        """Generate clarification options for ambiguous queries."""
        clarifications = [
            "What specific effect are you asking about?",
            "Are you looking for evidence supporting or contradicting something?",
            "Would you like a summary of what we know, or specific confidence levels?"
        ]
        return clarifications

    def _detect_causal_level(self, query: str, query_type: QueryType) -> CausalLevel:
        """
        Detect the causal level of a query per Pearl's ladder of causation.

        Rung 1 (Associational): Observing correlations
        Rung 2 (Interventional): What happens if we act
        Rung 3 (Counterfactual): What would have happened

        Per Pearl (Sprint 3.0 panel): The query engine must distinguish these
        fundamentally different question types.
        """
        query_lower = query.lower()

        # Counterfactual indicators (Rung 3)
        counterfactual_patterns = [
            r'would\s+(?:have|not\s+have)',
            r'if\s+(?:we|they|it)\s+had(?:n\'t|n\'t|\s+not)',
            r'had\s+(?:we|they|it)\s+(?:not\s+)?',
            r'what\s+if\s+(?:we|they|it)\s+had',
            r'without\s+(?:the|that|this)',
            r'in\s+the\s+absence\s+of',
            r'suppose\s+(?:we|they|it)\s+had(?:n\'t)?',
            r'imagine\s+(?:we|they|it)\s+had(?:n\'t)?',
        ]
        for pattern in counterfactual_patterns:
            if re.search(pattern, query_lower):
                return CausalLevel.COUNTERFACTUAL

        # Interventional indicators (Rung 2)
        interventional_patterns = [
            r'what\s+(?:would|will)\s+happen\s+if',
            r'if\s+(?:we|I|you)\s+(?:add|remove|change|implement|install|use)',
            r'(?:should|would)\s+(?:we|I|you)\s+(?:add|use|implement)',
            r'what\s+(?:is|are)\s+the\s+effect(?:s)?\s+of\s+(?:adding|removing|using)',
            r'(?:does|do|will|would)\s+(?:adding|removing|using|implementing)',
            r'if\s+(?:we|I|you)\s+(?:were\s+to|did)',
            r'(?:by|through)\s+(?:adding|removing|implementing)',
        ]
        for pattern in interventional_patterns:
            if re.search(pattern, query_lower):
                return CausalLevel.INTERVENTIONAL

        # Descriptive/definitional queries
        descriptive_patterns = [
            r'^what\s+is\s+(?:the\s+definition\s+of\s+)?[a-z]+\??$',
            r'^define\s+',
            r'^what\s+does\s+.+\s+mean',
            r'^explain\s+(?:what\s+)?[a-z]+\s+(?:is|means)',
        ]
        for pattern in descriptive_patterns:
            if re.search(pattern, query_lower):
                return CausalLevel.DESCRIPTIVE

        # Query types that are typically associational
        associational_types = {
            QueryType.WHAT_IS,
            QueryType.DOES_X_AFFECT_Y,
            QueryType.HOW_MUCH,
            QueryType.WHAT_EVIDENCE,
            QueryType.COMPARE,
            QueryType.HOW_CONFIDENT,
            QueryType.WHAT_CONTRADICTS,
        }

        # Default: check for general correlational language
        associational_patterns = [
            r'(?:is|are)\s+(?:there\s+)?(?:a\s+)?(?:correlation|relationship|association|link)',
            r'(?:what|which)\s+(?:is|are)\s+(?:associated|correlated|linked|related)',
            r'does\s+.+\s+(?:correlate|relate|associate)\s+with',
            r'evidence\s+(?:for|that|about)',
            r'what\s+(?:do\s+)?(?:we\s+)?know\s+about',
        ]
        for pattern in associational_patterns:
            if re.search(pattern, query_lower):
                return CausalLevel.ASSOCIATIONAL

        # If query type is typically associational, default to that
        if query_type in associational_types:
            return CausalLevel.ASSOCIATIONAL

        # Scope/gap queries are typically at associational level
        if query_type in {QueryType.WHEN_DOES, QueryType.FOR_WHOM, QueryType.WHAT_DONT_KNOW}:
            return CausalLevel.ASSOCIATIONAL

        return CausalLevel.UNKNOWN

    def get_search_terms(self, intent: QueryIntent) -> List[str]:
        """
        Get search terms for querying the web of belief.

        Includes original terms and vocabulary expansions.
        """
        terms = []

        if intent.subject:
            terms.append(intent.subject)
            terms.extend(intent.subject_expansions)

        if intent.object:
            terms.append(intent.object)
            terms.extend(intent.object_expansions)

        # Deduplicate while preserving order
        seen = set()
        unique_terms = []
        for term in terms:
            if term.lower() not in seen:
                seen.add(term.lower())
                unique_terms.append(term)

        return unique_terms


# =============================================================================
# Convenience Functions
# =============================================================================

def parse_query(query: str) -> ParseResult:
    """Parse a query using default parser."""
    parser = QueryParser()
    return parser.parse(query)


def get_query_type(query: str) -> QueryType:
    """Get just the query type for a query."""
    result = parse_query(query)
    return result.primary.query_type


def get_causal_level(query: str) -> CausalLevel:
    """
    Get the causal level for a query (per Pearl).

    Returns:
        CausalLevel: ASSOCIATIONAL, INTERVENTIONAL, COUNTERFACTUAL, or DESCRIPTIVE
    """
    result = parse_query(query)
    return result.primary.causal_level


def classify_query(query: str) -> Dict[str, str]:
    """
    Classify a query by both type and causal level.

    Returns:
        Dict with 'query_type', 'causal_level', and 'confidence'
    """
    result = parse_query(query)
    return {
        'query_type': result.primary.query_type.value,
        'causal_level': result.primary.causal_level.value,
        'confidence': result.primary.confidence
    }
