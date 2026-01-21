"""
Causal Classifier Service
==========================

H1: Three-tier causal classification per Pearl panel recommendation.

Classifies evidence claims into:
- CAUSAL: Clear causal language with mechanism or experimental evidence
- SUGGESTIVE: Hints at causation but not definitive
- ASSOCIATIONAL: Purely correlational language

Per expert panel (Pearl):
"Distinguish causal from correlational evidence explicitly.
The system should use proper causal language distinctions."

Date: January 21, 2026
Sprint E1 (Panel HIGH Priority)
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple
from enum import Enum
import re


# =============================================================================
# Causal Tier Enumeration
# =============================================================================

class CausalTier(Enum):
    """
    Three-tier causal classification hierarchy.

    Per Pearl: Clear distinction between causal and correlational evidence.
    """
    CAUSAL = "causal"           # Clear causal claim with mechanism/experimental support
    SUGGESTIVE = "suggestive"   # Suggests causation but not definitive
    ASSOCIATIONAL = "associational"  # Correlation only, no causal claim


# =============================================================================
# Classification Result
# =============================================================================

@dataclass
class CausalClassification:
    """Result of causal classification."""
    tier: CausalTier
    confidence: float  # 0-1 confidence in classification
    evidence_type: str  # experimental, quasi-experimental, observational, correlational
    matched_patterns: List[str]  # Which patterns triggered this classification
    warnings: List[str] = field(default_factory=list)  # Any concerns
    confounder_mentioned: bool = False  # H3: Does it mention confounders?
    mechanism_mentioned: bool = False  # E1.D5: Separate indicator, not confidence booster
    is_quasi_experimental: bool = False  # E1.D5: Quasi-experimental design detected

    def to_dict(self) -> Dict[str, Any]:
        return {
            'tier': self.tier.value,
            'confidence': self.confidence,
            'evidence_type': self.evidence_type,
            'matched_patterns': self.matched_patterns,
            'warnings': self.warnings,
            'confounder_mentioned': self.confounder_mentioned,
            'mechanism_mentioned': self.mechanism_mentioned,
            'is_quasi_experimental': self.is_quasi_experimental
        }


# =============================================================================
# Pattern Definitions
# =============================================================================

# Strong causal language patterns (indicates CAUSAL tier)
CAUSAL_PATTERNS = [
    # Direct causation
    r'\bcause[sd]?\b',
    r'\bcausing\b',
    r'\bresult[s]?\s+in\b',
    r'\bresult[s]?\s+from\b',
    r'\blead[s]?\s+to\b',
    r'\bled\s+to\b',
    r'\bproduces?\b',
    r'\bdetermine[sd]?\b',
    r'\bdetermining\b',
    # Experimental language
    r'\brandomized\b',
    r'\brandomisation\b',
    r'\bexperimental\b',
    r'\bintervention\b',
    r'\bmanipulated\b',
    r'\btreatment\s+effect\b',
    r'\bcausal\s+effect\b',
    r'\bcausal\s+mechanism\b',
    r'\bcausal\s+pathway\b',
    # Strong effect language
    r'\bdirectly\s+affect[s]?\b',
    r'\bdirectly\s+impact[s]?\b',
    r'\bdirectly\s+influence[s]?\b',
]

# Suggestive causal language patterns (indicates SUGGESTIVE tier)
SUGGESTIVE_PATTERNS = [
    # Moderate causal language
    r'\baffect[s]?\b',
    r'\baffecting\b',
    r'\bimpact[s]?\b',
    r'\bimpacting\b',
    r'\binfluence[s]?\b',
    r'\binfluencing\b',
    r'\bimprove[s]?\b',
    r'\bimproving\b',
    r'\breduce[s]?\b',
    r'\breducing\b',
    r'\bincrease[s]?\b',
    r'\bincreasing\b',
    r'\bdecrease[s]?\b',
    r'\bdecreasing\b',
    r'\benhance[s]?\b',
    r'\benhancing\b',
    r'\bdiminish(es)?\b',
    # Conditional causal language
    r'\bmay\s+cause\b',
    r'\bmight\s+cause\b',
    r'\bcould\s+cause\b',
    r'\bappears?\s+to\s+affect\b',
    r'\bseems?\s+to\s+affect\b',
    r'\bsuggests?\s+(that\s+)?.*\baffect',
    r'\bindicates?\s+(that\s+)?.*\baffect',
    # Dose-response language
    r'\bhigher\s+levels?\s+.*\b(result|lead|associate)',
    r'\blower\s+levels?\s+.*\b(result|lead|associate)',
]

# Associational language patterns (indicates ASSOCIATIONAL tier)
ASSOCIATIONAL_PATTERNS = [
    # Correlation language
    r'\bcorrelat(e[sd]?|ion)\b',
    r'\bassociat(e[sd]?|ion)\b',
    r'\brelat(e[sd]?|ion)\b',
    r'\blink(ed|s)?\s+to\b',
    r'\bconnect(ed|s)?\s+(with|to)\b',
    # Co-occurrence
    r'\bco-occur\b',
    r'\bcoincide[sd]?\b',
    r'\bwhen\s+.*\s+(also|simultaneously)\b',
    # Observational only
    r'\bobserved\s+(that\s+)?\w+\s+(and|with)\b',
    r'\bnoted\s+(that\s+)?\w+\s+(and|with)\b',
    r'\bfound\s+(that\s+)?\w+\s+(and|with)\b',
]

# Confounder acknowledgment patterns
CONFOUNDER_PATTERNS = [
    r'\bconfounder[s]?\b',
    r'\bconfounding\b',
    r'\bcontrolled?\s+for\b',
    r'\bcontrolling\s+for\b',
    r'\badjusted?\s+for\b',
    r'\badjusting\s+for\b',
    r'\bcovariate[s]?\b',
    r'\bmediator[s]?\b',
    r'\bmediating\b',
    r'\bmoderator[s]?\b',
    r'\bmoderating\b',
    r'\bheld\s+constant\b',
    r'\baccounted\s+for\b',
    r'\bindependent\s+of\b',
    r'\bafter\s+adjusting\b',
    r'\bafter\s+controlling\b',
    r'\bnet\s+of\b',
    r'\bspurious\b',
    r'\bthird\s+variable\b',
]

# Mechanism description patterns
MECHANISM_PATTERNS = [
    r'\bmechanism\b',
    r'\bpathway\b',
    r'\bmediated?\s+by\b',
    r'\bmediates?\b',
    r'\bthrough\s+(the\s+)?(action|process|effect)\b',
    r'\bvia\b',
    r'\bby\s+(way\s+of|means\s+of)\b',
    r'\bprocess\s+(by\s+which|whereby)\b',
    r'\bhow\s+\w+\s+(affect|cause|produce|lead)',
    r'\b(physiological|biological|cognitive)\s+mechanism\b',
    r'\b(neural|hormonal|behavioral)\s+pathway\b',
]

# E1.D5 Panel: Quasi-experimental design patterns (per Pearl)
# These are between experimental and observational
QUASI_EXPERIMENTAL_PATTERNS = [
    r'\bnatural\s+experiment\b',
    r'\bquasi-experiment(al)?\b',
    r'\bregression\s+discontinuity\b',
    r'\bdifference-in-differences?\b',
    r'\bdiff-in-diff\b',
    r'\bpropensity\s+score\b',
    r'\binstrumental\s+variable\b',
    r'\bmatched\s+(sample|pairs|groups)\b',
    r'\bbefore-after\b',
    r'\bpre-post\s+design\b',
    r'\binterrupted\s+time\s+series\b',
]

# E1.D5 Panel: Neuroarchitecture-specific patterns (per Kaplan)
NEUROARCH_CAUSAL_PATTERNS = [
    r'\bdesign\s+intervention\b',
    r'\bbuilt\s+environment\s+manipulation\b',
    r'\blighting\s+intervention\b',
    r'\barchitectural\s+intervention\b',
    r'\benvironmental\s+manipulation\b',
]

NEUROARCH_SUGGESTIVE_PATTERNS = [
    r'\brestorative\s+effect\b',
    r'\brestorative\s+environment\b',
    r'\bbiophilic\s+response\b',
    r'\battention\s+restoration\b',
    r'\bstress\s+recovery\b',
]

NEUROARCH_ASSOCIATIONAL_PATTERNS = [
    r'\bpreference\s+for\b',
    r'\bpreferred\b',
    r'\brated\s+(higher|lower|as)\b',
    r'\brating\s+study\b',
    r'\bsubjective\s+assessment\b',
]


# =============================================================================
# Causal Classifier Service
# =============================================================================

class CausalClassifier:
    """
    Three-tier causal claim classifier per Pearl panel recommendation.

    Uses pattern matching and linguistic analysis to classify claims
    into CAUSAL, SUGGESTIVE, or ASSOCIATIONAL tiers.
    """

    def __init__(self):
        """Initialize classifier with compiled patterns."""
        # Core patterns
        self.causal_patterns = [re.compile(p, re.IGNORECASE) for p in CAUSAL_PATTERNS]
        self.suggestive_patterns = [re.compile(p, re.IGNORECASE) for p in SUGGESTIVE_PATTERNS]
        self.associational_patterns = [re.compile(p, re.IGNORECASE) for p in ASSOCIATIONAL_PATTERNS]
        self.confounder_patterns = [re.compile(p, re.IGNORECASE) for p in CONFOUNDER_PATTERNS]
        self.mechanism_patterns = [re.compile(p, re.IGNORECASE) for p in MECHANISM_PATTERNS]

        # E1.D5 Panel additions
        self.quasi_experimental_patterns = [
            re.compile(p, re.IGNORECASE) for p in QUASI_EXPERIMENTAL_PATTERNS
        ]

        # Neuroarchitecture domain-specific (per Kaplan)
        self.neuroarch_causal = [
            re.compile(p, re.IGNORECASE) for p in NEUROARCH_CAUSAL_PATTERNS
        ]
        self.neuroarch_suggestive = [
            re.compile(p, re.IGNORECASE) for p in NEUROARCH_SUGGESTIVE_PATTERNS
        ]
        self.neuroarch_associational = [
            re.compile(p, re.IGNORECASE) for p in NEUROARCH_ASSOCIATIONAL_PATTERNS
        ]

    def classify(self, content: str, context: Optional[Dict[str, Any]] = None) -> CausalClassification:
        """
        Classify a claim's causal strength.

        E1.D5 Panel restructure (per Pearl):
        - Design-first: experimental/quasi-experimental status takes precedence
        - Language-second: causal/suggestive/associational patterns
        - Mechanism is separate indicator, not confidence booster (per Cartwright)

        Args:
            content: The text content to classify
            context: Optional context (e.g., source_depth, study_type)

        Returns:
            CausalClassification with tier, confidence, and details
        """
        context = context or {}

        # Match core patterns
        causal_matches = self._match_patterns(content, self.causal_patterns)
        suggestive_matches = self._match_patterns(content, self.suggestive_patterns)
        associational_matches = self._match_patterns(content, self.associational_patterns)
        confounder_matches = self._match_patterns(content, self.confounder_patterns)
        mechanism_matches = self._match_patterns(content, self.mechanism_patterns)

        # E1.D5: Match quasi-experimental patterns (per Pearl)
        quasi_experimental_matches = self._match_patterns(
            content, self.quasi_experimental_patterns
        )

        # E1.D5: Match neuroarchitecture domain patterns (per Kaplan)
        neuroarch_causal_matches = self._match_patterns(content, self.neuroarch_causal)
        neuroarch_suggestive_matches = self._match_patterns(content, self.neuroarch_suggestive)
        neuroarch_associational_matches = self._match_patterns(content, self.neuroarch_associational)

        # Combine domain-specific matches with general matches
        all_causal_matches = causal_matches + neuroarch_causal_matches
        all_suggestive_matches = suggestive_matches + neuroarch_suggestive_matches
        all_associational_matches = associational_matches + neuroarch_associational_matches

        # Check for hedged causal language (e.g., "may cause", "might cause")
        # These should be suggestive, not causal, even though they contain "cause"
        hedged_causal = self._has_hedged_causal_language(content)

        # Adjust counts if hedged language detected
        effective_causal = len(all_causal_matches)
        effective_suggestive = len(all_suggestive_matches)
        if hedged_causal and len(all_causal_matches) > 0:
            # Don't count bare "cause" when it's hedged
            effective_causal = max(0, len(all_causal_matches) - 1)
            effective_suggestive = len(all_suggestive_matches) + 1

        # Check context for experimental indicators
        is_experimental = self._check_experimental_context(content, context)

        # E1.D5: Check for quasi-experimental design (per Pearl)
        is_quasi_experimental = len(quasi_experimental_matches) > 0

        # E1.D5 Restructure: Determine tier using design-first approach (per Pearl)
        tier, confidence, evidence_type = self._determine_tier_pearl(
            effective_causal,
            effective_suggestive,
            len(all_associational_matches),
            is_experimental,
            is_quasi_experimental,
            len(mechanism_matches) > 0,
            len(confounder_matches) > 0,
            context
        )

        # Collect all matched patterns for transparency
        matched_patterns = []
        if all_causal_matches:
            matched_patterns.extend([f"causal:{m}" for m in all_causal_matches])
        if all_suggestive_matches:
            matched_patterns.extend([f"suggestive:{m}" for m in all_suggestive_matches])
        if all_associational_matches:
            matched_patterns.extend([f"associational:{m}" for m in all_associational_matches])
        if quasi_experimental_matches:
            matched_patterns.extend([f"quasi-exp:{m}" for m in quasi_experimental_matches])

        # Generate warnings
        warnings = self._generate_warnings(
            tier, all_causal_matches, all_suggestive_matches, all_associational_matches,
            len(confounder_matches) > 0, context
        )

        return CausalClassification(
            tier=tier,
            confidence=confidence,
            evidence_type=evidence_type,
            matched_patterns=matched_patterns[:10],  # Limit for display
            warnings=warnings,
            confounder_mentioned=len(confounder_matches) > 0,
            mechanism_mentioned=len(mechanism_matches) > 0,
            is_quasi_experimental=is_quasi_experimental
        )

    def _match_patterns(self, content: str, patterns: List[re.Pattern]) -> List[str]:
        """Match patterns against content and return matched strings."""
        matches = []
        for pattern in patterns:
            found = pattern.findall(content)
            matches.extend(found if isinstance(found, list) else [found])
        return [m for m in matches if m]  # Filter empty

    def _has_hedged_causal_language(self, content: str) -> bool:
        """
        Check if the content has hedged causal language.

        Phrases like "may cause", "might cause", "could cause" should be
        treated as suggestive, not as strong causal claims.
        """
        hedged_patterns = [
            r'\bmay\s+cause\b',
            r'\bmight\s+cause\b',
            r'\bcould\s+cause\b',
            r'\bcan\s+cause\b',
            r'\bpossibly\s+cause\b',
            r'\bpotentially\s+cause\b',
            r'\bappears?\s+to\s+cause\b',
            r'\bseems?\s+to\s+cause\b',
        ]
        content_lower = content.lower()
        return any(re.search(p, content_lower) for p in hedged_patterns)

    def _check_experimental_context(self, content: str, context: Dict[str, Any]) -> bool:
        """Check if evidence is from experimental study."""
        # Check explicit context
        if context.get('study_type') in ['RCT', 'randomized', 'experimental', 'intervention']:
            return True
        if context.get('is_experimental'):
            return True

        # Check content for experimental indicators
        experimental_terms = [
            'randomized', 'randomised', 'RCT', 'experiment', 'intervention',
            'treatment group', 'control group', 'manipulated', 'randomly assigned'
        ]
        content_lower = content.lower()
        return any(term in content_lower for term in experimental_terms)

    def _determine_tier_pearl(
        self,
        causal_count: int,
        suggestive_count: int,
        associational_count: int,
        is_experimental: bool,
        is_quasi_experimental: bool,
        has_mechanism: bool,
        has_confounder_control: bool,
        context: Dict[str, Any]
    ) -> Tuple[CausalTier, float, str]:
        """
        E1.D5 Panel: Determine causal tier using Pearl's design-first approach.

        Per Pearl panel recommendation:
        1. Design takes precedence over language
        2. Experimental → CAUSAL (with appropriate confidence by language)
        3. Quasi-experimental → boost toward CAUSAL but not fully
        4. Mechanism is separate indicator, not confidence booster (per Cartwright)
        5. Causal language alone requires mechanism OR confounder control for CAUSAL

        Logic flow:
        IF experimental_design THEN
            IF causal_language THEN CAUSAL (high confidence)
            ELIF suggestive_language THEN CAUSAL (medium confidence)
            ELSE ASSOCIATIONAL
        ELIF quasi_experimental THEN
            IF causal_language THEN CAUSAL (medium-high confidence)
            ELIF suggestive_language THEN SUGGESTIVE (high confidence, near CAUSAL)
            ELSE SUGGESTIVE
        ELIF causal_language AND (mechanism OR confounder_control) THEN CAUSAL
        ELIF causal_language THEN SUGGESTIVE (would be CAUSAL-INSUFFICIENT per Pearl,
                                              but keeping 3 tiers per Simon)
        ELIF suggestive_language THEN SUGGESTIVE
        ELSE ASSOCIATIONAL

        Returns:
            Tuple of (tier, confidence, evidence_type)
        """
        # CASE 1: Experimental design (RCT, intervention, etc.)
        if is_experimental:
            if causal_count > 0:
                # Experimental + causal language = CAUSAL (high confidence)
                confidence = min(0.95, 0.75 + (causal_count * 0.1))
                return CausalTier.CAUSAL, confidence, "experimental"
            elif suggestive_count > 0:
                # Experimental + suggestive language = CAUSAL (medium confidence)
                confidence = min(0.85, 0.65 + (suggestive_count * 0.1))
                return CausalTier.CAUSAL, confidence, "experimental"
            else:
                # Experimental but only associational language = stay ASSOCIATIONAL
                # (rare edge case - experimental study using only correlational language)
                confidence = 0.5 + (associational_count * 0.1)
                return CausalTier.ASSOCIATIONAL, min(0.7, confidence), "experimental"

        # CASE 2: Quasi-experimental design (per Pearl - between experimental and observational)
        if is_quasi_experimental:
            if causal_count > 0:
                # Quasi-exp + causal language = CAUSAL (medium-high confidence)
                confidence = min(0.85, 0.60 + (causal_count * 0.1))
                return CausalTier.CAUSAL, confidence, "quasi-experimental"
            elif suggestive_count > 0:
                # Quasi-exp + suggestive language = SUGGESTIVE (high confidence)
                # Per Simon: keep 3 tiers, but this is strong suggestive
                confidence = min(0.80, 0.55 + (suggestive_count * 0.1))
                return CausalTier.SUGGESTIVE, confidence, "quasi-experimental"
            else:
                # Quasi-exp but only associational = SUGGESTIVE
                confidence = 0.45
                return CausalTier.SUGGESTIVE, confidence, "quasi-experimental"

        # CASE 3: Observational/other - language-driven
        # Per Pearl: Causal language needs mechanism OR confounder control for CAUSAL tier
        if causal_count > 0:
            if has_mechanism or has_confounder_control:
                # Causal language + mechanism/confounder = CAUSAL
                confidence = min(0.75, 0.50 + (causal_count * 0.1))
                if has_confounder_control:
                    confidence = min(0.80, confidence + 0.1)
                return CausalTier.CAUSAL, confidence, "observational"
            else:
                # Causal language without mechanism/confounder = SUGGESTIVE
                # (This would be CAUSAL-INSUFFICIENT per Pearl, but per Simon
                # we keep 3 tiers and use warnings to convey this)
                confidence = min(0.65, 0.45 + (causal_count * 0.05))
                return CausalTier.SUGGESTIVE, confidence, "observational"

        # CASE 4: Suggestive language only
        if suggestive_count > 0:
            confidence = min(0.70, 0.40 + (suggestive_count * 0.1))
            return CausalTier.SUGGESTIVE, confidence, "observational"

        # CASE 5: Associational language only
        if associational_count > 0:
            confidence = min(0.80, 0.50 + (associational_count * 0.1))
            return CausalTier.ASSOCIATIONAL, confidence, "correlational"

        # CASE 6: No clear language patterns - default to ASSOCIATIONAL
        return CausalTier.ASSOCIATIONAL, 0.30, "unclear"

    def _generate_warnings(
        self,
        tier: CausalTier,
        causal_matches: List[str],
        suggestive_matches: List[str],
        associational_matches: List[str],
        has_confounder_mention: bool,
        context: Dict[str, Any]
    ) -> List[str]:
        """Generate warnings about the classification."""
        warnings = []

        # Warn about causal claims without confounder acknowledgment
        if tier == CausalTier.CAUSAL and not has_confounder_mention:
            warnings.append(
                "Causal claim without explicit confounder acknowledgment (Pearl)"
            )

        # Warn about mixed signals
        if causal_matches and associational_matches:
            warnings.append(
                "Mixed causal and correlational language detected"
            )

        # Warn about abstract-only causal claims
        if tier == CausalTier.CAUSAL and context.get('source_depth') == 'abstract':
            warnings.append(
                "Causal claim from abstract only - requires full-text verification (Cartwright)"
            )

        # Warn about observational studies making causal claims
        if tier == CausalTier.CAUSAL and context.get('study_type') == 'observational':
            warnings.append(
                "Causal language in observational study - interpret with caution"
            )

        return warnings

    def classify_belief(self, belief: 'Belief') -> CausalClassification:
        """
        Convenience method to classify a Belief object.

        Args:
            belief: A Belief from the web of belief

        Returns:
            CausalClassification
        """
        context = {
            'source_depth': belief.source_depth.value if belief.source_depth else None,
            'has_scope': belief.scope is not None,
        }
        return self.classify(belief.content, context)


# =============================================================================
# Convenience Functions
# =============================================================================

def classify_causal_tier(content: str, context: Optional[Dict[str, Any]] = None) -> CausalClassification:
    """Classify the causal tier of a content string."""
    classifier = CausalClassifier()
    return classifier.classify(content, context)


def get_causal_tier(content: str) -> CausalTier:
    """Quick helper to get just the tier."""
    return classify_causal_tier(content).tier
