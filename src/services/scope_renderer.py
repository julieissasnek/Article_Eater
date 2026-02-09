"""
Scope-Aware Output Renderer
============================

Renders evidence with explicit scope conditions per Cartwright's philosophy.

Per expert panel (Cartwright, Sprint 3.0.2-C):
- Every finding has boundary conditions
- Generalization claims must be explicit
- Transferability warnings are mandatory
- Scope metadata drives output formatting

Key principles:
1. NEVER present findings without scope context
2. WARN when scope is under-specified
3. HIGHLIGHT scope mismatches between query and evidence
4. GRADE transferability confidence

Date: February 9, 2026
Sprint: 3.0.2-C
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Set, Tuple
from enum import Enum
import re


class ScopeConfidence(Enum):
    """How confident we are about scope transferability."""
    HIGH = "high"           # Scope explicitly stated and matches
    MODERATE = "moderate"   # Scope partially stated or partial match
    LOW = "low"             # Scope inferred or weak match
    UNKNOWN = "unknown"     # Scope not available


class GeneralizabilityLevel(Enum):
    """How generalizable is the finding?"""
    UNIVERSAL = "universal"       # Applies broadly (rare in social science)
    DOMAIN_SPECIFIC = "domain"    # Applies within a domain
    CONTEXT_BOUND = "context"     # Requires specific context
    SAMPLE_SPECIFIC = "sample"    # Only applies to studied sample


@dataclass
class ScopeCondition:
    """A single scope condition with metadata."""
    dimension: str              # population, setting, duration, methodology, etc.
    value: str                  # The actual condition
    explicit: bool              # Was this explicitly stated?
    source: str                 # Where this came from (paper_id, belief_id)
    confidence: float = 0.5    # How confident in this scope condition


@dataclass
class ScopeMismatch:
    """Represents a mismatch between query scope and evidence scope."""
    dimension: str
    query_value: Optional[str]
    evidence_value: str
    severity: str              # minor, moderate, major
    explanation: str


@dataclass
class TransferabilityAssessment:
    """Assessment of whether evidence transfers to query context."""
    transferable: bool
    confidence: ScopeConfidence
    generalizability: GeneralizabilityLevel
    mismatches: List[ScopeMismatch] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    supporting_factors: List[str] = field(default_factory=list)


@dataclass
class ScopedEvidence:
    """Evidence item with full scope annotation."""
    belief_id: str
    content: str
    credence: float

    # Scope conditions
    population: Optional[ScopeCondition] = None
    setting: Optional[ScopeCondition] = None
    duration: Optional[ScopeCondition] = None
    methodology: Optional[ScopeCondition] = None
    measurement: Optional[ScopeCondition] = None

    # Additional scope dimensions for CNfA
    nature_type: Optional[ScopeCondition] = None      # Type of nature exposure
    dosage: Optional[ScopeCondition] = None           # Amount/intensity
    outcome_measure: Optional[ScopeCondition] = None  # How outcome measured

    # Transferability
    transferability: Optional[TransferabilityAssessment] = None

    # Rendering hints
    scope_completeness: float = 0.0  # 0-1, how complete is scope info
    requires_warning: bool = False
    warning_messages: List[str] = field(default_factory=list)


@dataclass
class ScopeContext:
    """The scope context from a query."""
    population: Optional[str] = None
    setting: Optional[str] = None
    duration: Optional[str] = None
    methodology_preference: Optional[str] = None
    nature_type: Optional[str] = None

    def is_specified(self) -> bool:
        """Check if any scope is specified."""
        return any([
            self.population, self.setting, self.duration,
            self.methodology_preference, self.nature_type
        ])


@dataclass
class ScopedResponse:
    """Response with scope-aware formatting."""
    # Core content
    headline: str
    main_finding: str
    evidence: List[ScopedEvidence]

    # Scope summary
    scope_summary: Dict[str, Any]
    transferability_summary: str

    # Warnings (Cartwright: mandatory)
    scope_warnings: List[str]
    generalization_limits: List[str]

    # For practitioners
    applies_when: List[str]
    does_not_apply_when: List[str]

    # Metadata
    overall_scope_confidence: ScopeConfidence
    scope_coverage: float  # 0-1, how much scope info available


class ScopeRenderer:
    """
    Renders evidence with explicit scope conditions.

    Per Cartwright: "All generalizations are local."
    Every claim must come with its boundary conditions.
    """

    # Scope dimension patterns for extraction
    POPULATION_PATTERNS = [
        r'(?:adults|children|elderly|students|workers|patients|employees)',
        r'(?:men|women|male|female)',
        r'(?:healthy|clinical|stressed|depressed)',
        r'(?:urban|rural|suburban)',
        r'(?:western|asian|european|american)',
        r'age(?:d?)?\s*(\d+[-–]\d+)',
    ]

    SETTING_PATTERNS = [
        r'(?:office|hospital|school|home|laboratory|field)',
        r'(?:indoor|outdoor)',
        r'(?:workplace|residential|healthcare|educational)',
        r'(?:urban|rural|suburban)\s+(?:setting|environment)',
    ]

    DURATION_PATTERNS = [
        r'(\d+)\s*(?:minutes?|mins?)',
        r'(\d+)\s*(?:hours?|hrs?)',
        r'(\d+)\s*(?:days?)',
        r'(\d+)\s*(?:weeks?)',
        r'(\d+)\s*(?:months?)',
        r'(?:short-term|long-term|acute|chronic)',
    ]

    METHODOLOGY_PATTERNS = [
        r'(?:RCT|randomized|randomised|experiment)',
        r'(?:quasi-experiment|observational)',
        r'(?:cross-sectional|longitudinal)',
        r'(?:survey|interview|focus group)',
        r'(?:lab(?:oratory)?|field)\s+study',
    ]

    NATURE_TYPE_PATTERNS = [
        r'(?:plants?|vegetation|greenery|indoor plants)',
        r'(?:window|view|vista)',
        r'(?:natural light|daylight|sunlight)',
        r'(?:water|aquatic|blue space)',
        r'(?:forest|woodland|park|garden)',
        r'(?:biophilic|nature)',
    ]

    def __init__(self):
        """Initialize the scope renderer."""
        # Compile patterns for efficiency
        self._population_re = [re.compile(p, re.I) for p in self.POPULATION_PATTERNS]
        self._setting_re = [re.compile(p, re.I) for p in self.SETTING_PATTERNS]
        self._duration_re = [re.compile(p, re.I) for p in self.DURATION_PATTERNS]
        self._methodology_re = [re.compile(p, re.I) for p in self.METHODOLOGY_PATTERNS]
        self._nature_type_re = [re.compile(p, re.I) for p in self.NATURE_TYPE_PATTERNS]

    def extract_scope_from_belief(
        self,
        belief_id: str,
        content: str,
        existing_scope: Optional[Dict[str, Any]] = None
    ) -> Dict[str, ScopeCondition]:
        """
        Extract scope conditions from belief content.

        Uses pattern matching + existing scope metadata.
        """
        scope = {}

        # Use existing scope if available (must be dict)
        if existing_scope and isinstance(existing_scope, dict):
            if existing_scope.get('population'):
                scope['population'] = ScopeCondition(
                    dimension='population',
                    value=existing_scope['population'],
                    explicit=True,
                    source=belief_id,
                    confidence=0.9
                )
            if existing_scope.get('setting'):
                scope['setting'] = ScopeCondition(
                    dimension='setting',
                    value=existing_scope['setting'],
                    explicit=True,
                    source=belief_id,
                    confidence=0.9
                )
            if existing_scope.get('duration'):
                scope['duration'] = ScopeCondition(
                    dimension='duration',
                    value=existing_scope['duration'],
                    explicit=True,
                    source=belief_id,
                    confidence=0.9
                )

        # Extract from content using patterns
        content_lower = content.lower()

        # Population
        if 'population' not in scope:
            for pattern in self._population_re:
                match = pattern.search(content_lower)
                if match:
                    scope['population'] = ScopeCondition(
                        dimension='population',
                        value=match.group(0),
                        explicit=False,
                        source=belief_id,
                        confidence=0.6
                    )
                    break

        # Setting
        if 'setting' not in scope:
            for pattern in self._setting_re:
                match = pattern.search(content_lower)
                if match:
                    scope['setting'] = ScopeCondition(
                        dimension='setting',
                        value=match.group(0),
                        explicit=False,
                        source=belief_id,
                        confidence=0.6
                    )
                    break

        # Duration
        if 'duration' not in scope:
            for pattern in self._duration_re:
                match = pattern.search(content_lower)
                if match:
                    scope['duration'] = ScopeCondition(
                        dimension='duration',
                        value=match.group(0),
                        explicit=False,
                        source=belief_id,
                        confidence=0.6
                    )
                    break

        # Methodology
        for pattern in self._methodology_re:
            match = pattern.search(content_lower)
            if match:
                scope['methodology'] = ScopeCondition(
                    dimension='methodology',
                    value=match.group(0),
                    explicit=False,
                    source=belief_id,
                    confidence=0.7
                )
                break

        # Nature type (CNfA specific)
        for pattern in self._nature_type_re:
            match = pattern.search(content_lower)
            if match:
                scope['nature_type'] = ScopeCondition(
                    dimension='nature_type',
                    value=match.group(0),
                    explicit=False,
                    source=belief_id,
                    confidence=0.7
                )
                break

        return scope

    def assess_transferability(
        self,
        evidence_scope: Dict[str, ScopeCondition],
        query_scope: ScopeContext
    ) -> TransferabilityAssessment:
        """
        Assess whether evidence transfers to the query context.

        Per Cartwright: Check if capacities transfer across contexts.
        """
        mismatches = []
        warnings = []
        supporting = []

        # Check each dimension
        if query_scope.population and 'population' in evidence_scope:
            ev_pop = evidence_scope['population'].value.lower()
            q_pop = query_scope.population.lower()
            if not self._populations_compatible(ev_pop, q_pop):
                mismatches.append(ScopeMismatch(
                    dimension='population',
                    query_value=query_scope.population,
                    evidence_value=evidence_scope['population'].value,
                    severity='moderate',
                    explanation=f"Evidence from {ev_pop} may not transfer to {q_pop}"
                ))
            else:
                supporting.append(f"Population match: {ev_pop}")

        if query_scope.setting and 'setting' in evidence_scope:
            ev_set = evidence_scope['setting'].value.lower()
            q_set = query_scope.setting.lower()
            if not self._settings_compatible(ev_set, q_set):
                mismatches.append(ScopeMismatch(
                    dimension='setting',
                    query_value=query_scope.setting,
                    evidence_value=evidence_scope['setting'].value,
                    severity='moderate',
                    explanation=f"Evidence from {ev_set} may not transfer to {q_set}"
                ))
            else:
                supporting.append(f"Setting match: {ev_set}")

        # Check for lab vs field mismatch (common issue)
        if 'methodology' in evidence_scope:
            meth = evidence_scope['methodology'].value.lower()
            if 'lab' in meth or 'experiment' in meth:
                warnings.append(
                    "Evidence from controlled settings may not generalize to real-world contexts"
                )

        # Check scope completeness
        scope_specified = len(evidence_scope)
        if scope_specified < 2:
            warnings.append(
                "Limited scope information available; transferability uncertain"
            )

        # Determine overall transferability
        major_mismatches = [m for m in mismatches if m.severity == 'major']
        moderate_mismatches = [m for m in mismatches if m.severity == 'moderate']

        if major_mismatches:
            transferable = False
            confidence = ScopeConfidence.LOW
            generalizability = GeneralizabilityLevel.SAMPLE_SPECIFIC
        elif moderate_mismatches:
            transferable = True
            confidence = ScopeConfidence.MODERATE
            generalizability = GeneralizabilityLevel.CONTEXT_BOUND
            warnings.append("Some scope conditions differ from query context")
        elif supporting:
            transferable = True
            confidence = ScopeConfidence.HIGH
            generalizability = GeneralizabilityLevel.DOMAIN_SPECIFIC
        else:
            transferable = True
            confidence = ScopeConfidence.UNKNOWN
            generalizability = GeneralizabilityLevel.CONTEXT_BOUND
            warnings.append("Scope match could not be verified")

        return TransferabilityAssessment(
            transferable=transferable,
            confidence=confidence,
            generalizability=generalizability,
            mismatches=mismatches,
            warnings=warnings,
            supporting_factors=supporting
        )

    def _populations_compatible(self, pop1: str, pop2: str) -> bool:
        """Check if two population descriptions are compatible."""
        # Simple compatibility check - could be more sophisticated
        if pop1 == pop2:
            return True

        # Check for subset relationships
        general_pops = {'adults', 'people', 'participants', 'individuals'}
        if pop1 in general_pops or pop2 in general_pops:
            return True

        # Check for conflicting specifics
        conflicting_pairs = [
            ('children', 'elderly'),
            ('healthy', 'clinical'),
            ('men', 'women'),
            ('students', 'workers'),
            ('students', 'elderly'),
            ('children', 'adults'),
        ]
        for p1, p2 in conflicting_pairs:
            if (p1 in pop1 and p2 in pop2) or (p2 in pop1 and p1 in pop2):
                return False

        return True  # Default to compatible if uncertain

    def _settings_compatible(self, set1: str, set2: str) -> bool:
        """Check if two setting descriptions are compatible."""
        if set1 == set2:
            return True

        # Check for subset relationships
        if 'indoor' in set1 and 'indoor' in set2:
            return True
        if 'outdoor' in set1 and 'outdoor' in set2:
            return True

        # Lab vs field is a common transferability concern
        if ('lab' in set1 or 'laboratory' in set1) and 'field' in set2:
            return False
        if ('lab' in set2 or 'laboratory' in set2) and 'field' in set1:
            return False

        return True

    def render_scoped_evidence(
        self,
        belief_id: str,
        content: str,
        credence: float,
        existing_scope: Optional[Dict[str, Any]] = None,
        query_scope: Optional[ScopeContext] = None
    ) -> ScopedEvidence:
        """
        Render a single piece of evidence with full scope annotation.
        """
        # Extract scope
        scope = self.extract_scope_from_belief(belief_id, content, existing_scope)

        # Assess transferability if query scope provided
        transferability = None
        if query_scope and query_scope.is_specified():
            transferability = self.assess_transferability(scope, query_scope)

        # Calculate scope completeness
        key_dimensions = ['population', 'setting', 'methodology']
        completeness = sum(1 for d in key_dimensions if d in scope) / len(key_dimensions)

        # Determine warnings
        warnings = []
        requires_warning = False

        if completeness < 0.5:
            warnings.append("Limited scope information; generalization uncertain")
            requires_warning = True

        if transferability and not transferability.transferable:
            warnings.append("Evidence may not transfer to your context")
            requires_warning = True

        if transferability and transferability.warnings:
            warnings.extend(transferability.warnings)
            requires_warning = True

        return ScopedEvidence(
            belief_id=belief_id,
            content=content,
            credence=credence,
            population=scope.get('population'),
            setting=scope.get('setting'),
            duration=scope.get('duration'),
            methodology=scope.get('methodology'),
            measurement=scope.get('measurement'),
            nature_type=scope.get('nature_type'),
            dosage=scope.get('dosage'),
            outcome_measure=scope.get('outcome_measure'),
            transferability=transferability,
            scope_completeness=completeness,
            requires_warning=requires_warning,
            warning_messages=warnings
        )

    def render_scoped_response(
        self,
        headline: str,
        main_finding: str,
        evidence_items: List[Dict[str, Any]],
        query_scope: Optional[ScopeContext] = None
    ) -> ScopedResponse:
        """
        Render a complete response with scope-aware formatting.

        Per Cartwright: Every response must include:
        1. Explicit scope conditions
        2. Transferability assessment
        3. Generalization limits
        4. When/where it applies
        """
        # Process each evidence item
        scoped_evidence = []
        for item in evidence_items:
            existing_scope = {}
            if 'scope' in item:
                existing_scope = item['scope']

            scoped = self.render_scoped_evidence(
                belief_id=item.get('belief_id', 'unknown'),
                content=item.get('content', ''),
                credence=item.get('credence', 0.5),
                existing_scope=existing_scope,
                query_scope=query_scope
            )
            scoped_evidence.append(scoped)

        # Aggregate scope information
        scope_summary = self._aggregate_scope(scoped_evidence)

        # Generate transferability summary
        transferability_summary = self._generate_transferability_summary(
            scoped_evidence, query_scope
        )

        # Collect all warnings
        scope_warnings = []
        for ev in scoped_evidence:
            scope_warnings.extend(ev.warning_messages)
        scope_warnings = list(set(scope_warnings))  # Deduplicate

        # Generate generalization limits
        generalization_limits = self._generate_generalization_limits(scoped_evidence)

        # Generate applies/does not apply
        applies_when, does_not_apply = self._generate_applicability(
            scoped_evidence, scope_summary
        )

        # Calculate overall confidence
        if not scoped_evidence:
            overall_confidence = ScopeConfidence.UNKNOWN
            scope_coverage = 0.0
        else:
            avg_completeness = sum(e.scope_completeness for e in scoped_evidence) / len(scoped_evidence)
            scope_coverage = avg_completeness

            if avg_completeness >= 0.7:
                overall_confidence = ScopeConfidence.HIGH
            elif avg_completeness >= 0.4:
                overall_confidence = ScopeConfidence.MODERATE
            else:
                overall_confidence = ScopeConfidence.LOW

        return ScopedResponse(
            headline=headline,
            main_finding=main_finding,
            evidence=scoped_evidence,
            scope_summary=scope_summary,
            transferability_summary=transferability_summary,
            scope_warnings=scope_warnings,
            generalization_limits=generalization_limits,
            applies_when=applies_when,
            does_not_apply_when=does_not_apply,
            overall_scope_confidence=overall_confidence,
            scope_coverage=scope_coverage
        )

    def _aggregate_scope(
        self,
        evidence: List[ScopedEvidence]
    ) -> Dict[str, Any]:
        """Aggregate scope conditions across evidence items."""
        populations = set()
        settings = set()
        durations = set()
        methodologies = set()
        nature_types = set()

        for ev in evidence:
            if ev.population:
                populations.add(ev.population.value)
            if ev.setting:
                settings.add(ev.setting.value)
            if ev.duration:
                durations.add(ev.duration.value)
            if ev.methodology:
                methodologies.add(ev.methodology.value)
            if ev.nature_type:
                nature_types.add(ev.nature_type.value)

        return {
            'populations': list(populations) if populations else ['not specified'],
            'settings': list(settings) if settings else ['not specified'],
            'durations': list(durations) if durations else ['not specified'],
            'methodologies': list(methodologies) if methodologies else ['not specified'],
            'nature_types': list(nature_types) if nature_types else ['not specified'],
            'n_evidence': len(evidence),
            'scope_diversity': len(populations) + len(settings)
        }

    def _generate_transferability_summary(
        self,
        evidence: List[ScopedEvidence],
        query_scope: Optional[ScopeContext]
    ) -> str:
        """Generate summary of evidence transferability."""
        if not query_scope or not query_scope.is_specified():
            return "No specific context provided; transferability not assessed."

        transferable = [e for e in evidence if e.transferability and e.transferability.transferable]
        not_transferable = [e for e in evidence if e.transferability and not e.transferability.transferable]
        unknown = [e for e in evidence if not e.transferability]

        parts = []
        if transferable:
            parts.append(f"{len(transferable)} evidence items likely transfer to your context")
        if not_transferable:
            parts.append(f"{len(not_transferable)} items may not transfer due to scope mismatch")
        if unknown:
            parts.append(f"{len(unknown)} items have unknown transferability")

        return "; ".join(parts) if parts else "Transferability assessment not available."

    def _generate_generalization_limits(
        self,
        evidence: List[ScopedEvidence]
    ) -> List[str]:
        """Generate explicit generalization limits per Cartwright."""
        limits = []

        # Check for lab-only evidence
        lab_evidence = [e for e in evidence if e.methodology and
                       ('lab' in e.methodology.value.lower() or
                        'experiment' in e.methodology.value.lower())]
        if lab_evidence and len(lab_evidence) == len(evidence):
            limits.append(
                "All evidence from controlled/laboratory settings; "
                "real-world effectiveness may differ"
            )

        # Check for narrow population
        pops = set(e.population.value for e in evidence if e.population)
        if len(pops) == 1 and pops != {'not specified'}:
            pop = list(pops)[0]
            limits.append(
                f"Evidence primarily from {pop}; "
                f"may not generalize to other populations"
            )

        # Check for short-term only
        short_term_keywords = ['minutes', 'hours', 'acute', 'brief']
        short_term = [e for e in evidence if e.duration and
                     any(k in e.duration.value.lower() for k in short_term_keywords)]
        if short_term and len(short_term) == len([e for e in evidence if e.duration]):
            limits.append(
                "Evidence from short-term exposures only; "
                "long-term effects unknown"
            )

        # Check for single setting
        settings = set(e.setting.value for e in evidence if e.setting)
        if len(settings) == 1 and settings != {'not specified'}:
            setting = list(settings)[0]
            limits.append(
                f"Evidence from {setting} settings; "
                f"may not generalize to other environments"
            )

        if not limits:
            limits.append("No major generalization limits identified, but always verify scope match")

        return limits

    def _generate_applicability(
        self,
        evidence: List[ScopedEvidence],
        scope_summary: Dict[str, Any]
    ) -> Tuple[List[str], List[str]]:
        """Generate when findings apply and don't apply."""
        applies_when = []
        does_not_apply = []

        # Based on aggregated scope
        pops = scope_summary['populations']
        if pops != ['not specified']:
            applies_when.append(f"Population: {', '.join(pops)}")
            # Infer what it doesn't apply to
            if all('adult' in p.lower() for p in pops):
                does_not_apply.append("May not apply to: children, adolescents")
            if all('healthy' in p.lower() or 'student' in p.lower() for p in pops):
                does_not_apply.append("May not apply to: clinical populations")

        settings = scope_summary['settings']
        if settings != ['not specified']:
            applies_when.append(f"Setting: {', '.join(settings)}")
            if all('office' in s.lower() or 'workplace' in s.lower() for s in settings):
                does_not_apply.append("May not apply to: residential, healthcare settings")

        methodologies = scope_summary['methodologies']
        if 'RCT' in str(methodologies) or 'randomized' in str(methodologies).lower():
            applies_when.append("Methodology: Experimentally validated")
        elif 'observational' in str(methodologies).lower():
            does_not_apply.append("Caution: Observational evidence only; causal claims limited")

        if not applies_when:
            applies_when.append("Scope conditions not fully specified in evidence")
        if not does_not_apply:
            does_not_apply.append("No specific exclusions identified")

        return applies_when, does_not_apply


# =============================================================================
# Convenience Functions
# =============================================================================

_renderer: Optional[ScopeRenderer] = None


def get_scope_renderer() -> ScopeRenderer:
    """Get or create the scope renderer singleton."""
    global _renderer
    if _renderer is None:
        _renderer = ScopeRenderer()
    return _renderer


def render_with_scope(
    headline: str,
    main_finding: str,
    evidence_items: List[Dict[str, Any]],
    query_population: Optional[str] = None,
    query_setting: Optional[str] = None
) -> ScopedResponse:
    """
    Convenience function to render response with scope.

    Args:
        headline: One-sentence answer
        main_finding: Main finding text
        evidence_items: List of evidence dicts with belief_id, content, credence
        query_population: Optional population from query
        query_setting: Optional setting from query

    Returns:
        ScopedResponse with full scope annotation
    """
    query_scope = ScopeContext(
        population=query_population,
        setting=query_setting
    )

    renderer = get_scope_renderer()
    return renderer.render_scoped_response(
        headline=headline,
        main_finding=main_finding,
        evidence_items=evidence_items,
        query_scope=query_scope
    )


def format_scope_for_display(scoped_response: ScopedResponse) -> Dict[str, Any]:
    """
    Format scoped response for UI display.

    Returns dict suitable for JSON serialization.
    """
    return {
        'headline': scoped_response.headline,
        'main_finding': scoped_response.main_finding,
        'scope': {
            'confidence': scoped_response.overall_scope_confidence.value,
            'coverage': scoped_response.scope_coverage,
            'summary': scoped_response.scope_summary,
            'transferability': scoped_response.transferability_summary
        },
        'warnings': scoped_response.scope_warnings,
        'generalization_limits': scoped_response.generalization_limits,
        'applies_when': scoped_response.applies_when,
        'does_not_apply_when': scoped_response.does_not_apply_when,
        'evidence': [
            {
                'belief_id': e.belief_id,
                'content': e.content,
                'credence': e.credence,
                'scope': {
                    'population': e.population.value if e.population else None,
                    'setting': e.setting.value if e.setting else None,
                    'duration': e.duration.value if e.duration else None,
                    'methodology': e.methodology.value if e.methodology else None,
                    'nature_type': e.nature_type.value if e.nature_type else None
                },
                'completeness': e.scope_completeness,
                'warnings': e.warning_messages,
                'transferability': {
                    'transferable': e.transferability.transferable,
                    'confidence': e.transferability.confidence.value,
                    'mismatches': [
                        {
                            'dimension': m.dimension,
                            'query': m.query_value,
                            'evidence': m.evidence_value,
                            'severity': m.severity
                        }
                        for m in e.transferability.mismatches
                    ]
                } if e.transferability else None
            }
            for e in scoped_response.evidence
        ]
    }
