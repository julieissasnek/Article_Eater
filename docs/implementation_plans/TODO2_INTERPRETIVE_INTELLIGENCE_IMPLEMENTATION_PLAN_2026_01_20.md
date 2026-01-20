# Implementation Plan: TODO 2 — Interpretive Intelligence

**Date:** January 20, 2026
**Phase:** B (Implementation Plan)
**Status:** Ready for critique
**Incorporates:** Expert Panel Review 2026-01-20

---

## 1. Executive Summary

This plan details the implementation of an interpretive intelligence module that translates the web's epistemic structure into human-understandable explanations. The system implements seven explanation patterns, supports multiple user modes, and includes a vocabulary bridge for term translation.

**Core Design Principle (from Simon):** Progressive disclosure—start with summaries, let users drill down. Respect bounded rationality by tailoring detail to user needs.

---

## 2. Architecture Overview

```
                    ┌─────────────────────────┐
                    │      User Query         │
                    │  (natural language or   │
                    │   structured request)   │
                    └───────────┬─────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │    Query Classifier     │
                    │  - Pattern matching     │
                    │  - Intent detection     │
                    │  - Entity extraction    │
                    └───────────┬─────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │   Vocabulary Bridge     │
                    │  - Internal ↔ Academic  │
                    │  - Academic ↔ Practice  │
                    │  - Common → Internal    │
                    └───────────┬─────────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
                    ▼                       ▼
          ┌─────────────────┐    ┌─────────────────┐
          │  Pattern-Based  │    │   Fallback      │
          │  (7 patterns)   │    │   (generic)     │
          └────────┬────────┘    └────────┬────────┘
                   │                      │
                   └──────────┬───────────┘
                              │
                              ▼
                    ┌─────────────────────────┐
                    │    Web Traversal        │
                    │  - Follow constraints   │
                    │  - Gather evidence      │
                    │  - Compute metrics      │
                    └───────────┬─────────────┘
                              │
                              ▼
                    ┌─────────────────────────┐
                    │  Template Rendering     │
                    │  - User mode selection  │
                    │  - Depth adjustment     │
                    │  - Practical implications│
                    └───────────┬─────────────┘
                              │
                              ▼
                    ┌─────────────────────────┐
                    │   Explanation Output    │
                    │  - Structured data      │
                    │  - Natural language     │
                    │  - (Optional) Visuals   │
                    └─────────────────────────┘
```

---

## 2. Explanation Patterns

### 2.1 Pattern Specifications

```python
# Location: src/services/interpretive_intelligence.py

from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional, Any

class ExplanationPattern(Enum):
    """The seven explanation patterns (per panel synthesis)."""
    EVIDENCE_TRACE = "evidence_trace"        # What papers support this?
    CREDIBILITY_ASSESSMENT = "credibility"   # How confident should we be?
    MECHANISM_EXPLANATION = "mechanism"      # How does this work? (Pearl)
    SCOPE_SPECIFICATION = "scope"            # Where does this apply?
    CONTINGENCY_MAP = "contingency"          # What assumptions does this rest on?
    DISAGREEMENT_SUMMARY = "disagreement"    # Where do experts differ? (Cartwright)
    PRACTICAL_IMPLICATIONS = "practical"     # What does this mean for design? (Kaplan)

class UserMode(Enum):
    """User modes affecting explanation style (per Simon)."""
    QUICK = "quick"          # Brief summary only
    STANDARD = "standard"    # Default - balanced detail
    DEEP = "deep"            # Full detail for researchers
    NOVICE = "novice"        # Expanded explanations for students

@dataclass
class ExplanationRequest:
    """A request for explanation."""
    pattern: ExplanationPattern
    target_belief_id: Optional[str] = None
    query_text: Optional[str] = None
    user_mode: UserMode = UserMode.STANDARD
    include_practical: bool = True  # Per Kaplan: always include practical section
    max_depth: int = 3  # For contingency/mechanism chains
```

### 2.2 Pattern Implementations

#### Evidence Trace

```python
@dataclass
class EvidenceTraceResult:
    """Result of evidence trace traversal."""
    target_belief: Belief
    supporting_evidence: List[EvidenceItem]
    contradicting_evidence: List[EvidenceItem]
    total_studies: int
    strongest_support: Optional[EvidenceItem]

@dataclass
class EvidenceItem:
    """A single piece of evidence."""
    belief: Belief
    source_paper: str
    constraint_strength: float
    study_quality: float  # Methodology score
    sample_size: Optional[int]
    effect_size: Optional[float]
    summary: str

class EvidenceTracePattern:
    """Pattern: What evidence supports this belief?"""

    def traverse(self, web: WebOfBelief, belief_id: str) -> EvidenceTraceResult:
        """Traverse web to gather evidence for belief."""
        target = web.beliefs[belief_id]

        supporting = []
        contradicting = []

        for constraint in web.get_constraints_for_belief(belief_id):
            partner_id = (constraint.target_id
                         if constraint.source_id == belief_id
                         else constraint.source_id)
            partner = web.beliefs.get(partner_id)

            if partner and partner.level in [EpistemicLevel.EMPIRICAL, EpistemicLevel.OBSERVATIONAL]:
                item = EvidenceItem(
                    belief=partner,
                    source_paper=partner.source_paper or "unknown",
                    constraint_strength=constraint.strength,
                    study_quality=partner.methodology_score or 0.5,
                    sample_size=partner.sample_size,
                    effect_size=partner.effect_size,
                    summary=self._summarize_evidence(partner, constraint)
                )

                if constraint.constraint_type == ConstraintType.SUPPORTS:
                    supporting.append(item)
                elif constraint.constraint_type == ConstraintType.CONTRADICTS:
                    contradicting.append(item)

        # Sort by strength × quality
        supporting.sort(key=lambda e: e.constraint_strength * e.study_quality, reverse=True)
        contradicting.sort(key=lambda e: e.constraint_strength * e.study_quality, reverse=True)

        return EvidenceTraceResult(
            target_belief=target,
            supporting_evidence=supporting,
            contradicting_evidence=contradicting,
            total_studies=len(supporting) + len(contradicting),
            strongest_support=supporting[0] if supporting else None
        )

    def render(self, result: EvidenceTraceResult, mode: UserMode) -> str:
        """Render evidence trace to natural language."""
        template = TEMPLATES["evidence_trace"][mode.value]
        return template.render(result=result)
```

#### Mechanism Explanation (Pearl)

```python
@dataclass
class MechanismStep:
    """One step in a causal mechanism chain."""
    from_belief: Belief
    to_belief: Belief
    mechanism_type: str  # e.g., "causes", "enables", "mediates"
    confidence: float
    evidence_summary: str

@dataclass
class MechanismExplanationResult:
    """Result of mechanism explanation."""
    target_effect: Belief
    mechanism_chains: List[List[MechanismStep]]
    primary_chain: List[MechanismStep]
    alternative_mechanisms: List[str]
    mechanism_confidence: float

class MechanismExplanationPattern:
    """
    Pattern: How does this effect work?
    Per Pearl: Trace causal chains through intermediate beliefs.
    """

    def traverse(self, web: WebOfBelief, belief_id: str, max_depth: int = 3) -> MechanismExplanationResult:
        """Find causal mechanism chains leading to belief."""
        target = web.beliefs[belief_id]

        chains = []
        visited = set()

        def trace_backward(current_id: str, current_chain: List[MechanismStep], depth: int):
            if depth > max_depth or current_id in visited:
                return
            visited.add(current_id)

            current = web.beliefs.get(current_id)
            if not current:
                return

            # Find causal predecessors
            for constraint in web.get_constraints_for_belief(current_id):
                if constraint.target_id == current_id:  # Incoming edge
                    if constraint.constraint_type == ConstraintType.EXPLAINS:
                        source = web.beliefs.get(constraint.source_id)
                        if source:
                            step = MechanismStep(
                                from_belief=source,
                                to_belief=current,
                                mechanism_type="explains",
                                confidence=constraint.strength,
                                evidence_summary=self._summarize_link(source, current, constraint)
                            )
                            new_chain = [step] + current_chain

                            if source.level == EpistemicLevel.THEORETICAL:
                                # Reached a theoretical root
                                chains.append(new_chain)
                            else:
                                trace_backward(source.id, new_chain, depth + 1)

        trace_backward(belief_id, [], 0)

        # Sort chains by total confidence
        chains.sort(key=lambda c: sum(s.confidence for s in c) / len(c) if c else 0, reverse=True)

        return MechanismExplanationResult(
            target_effect=target,
            mechanism_chains=chains,
            primary_chain=chains[0] if chains else [],
            alternative_mechanisms=self._identify_alternatives(chains),
            mechanism_confidence=self._compute_mechanism_confidence(chains)
        )

    def render(self, result: MechanismExplanationResult, mode: UserMode) -> str:
        """Render mechanism as narrative."""
        if not result.primary_chain:
            return f"No mechanism pathway found for: {result.target_effect.content}"

        # Build narrative from chain
        narrative_parts = []
        for step in result.primary_chain:
            narrative_parts.append(
                f"{step.from_belief.content} → {step.to_belief.content} "
                f"(confidence: {step.confidence:.0%})"
            )

        template = TEMPLATES["mechanism"][mode.value]
        return template.render(result=result, narrative=narrative_parts)
```

#### Contingency Map (Cartwright)

```python
@dataclass
class Contingency:
    """An assumption the belief depends on."""
    assumption: str
    assumption_type: str  # "direct", "bridging", "theoretical", "methodological"
    confidence: float
    fragility: str  # "low", "medium", "high" - how easily could this be undermined?
    what_would_change: str  # If this assumption fails, what happens?

@dataclass
class ContingencyMapResult:
    """Result of contingency mapping."""
    target_belief: Belief
    direct_assumptions: List[Contingency]
    bridging_assumptions: List[Contingency]
    theoretical_assumptions: List[Contingency]
    methodological_assumptions: List[Contingency]
    fragility_summary: str

class ContingencyMapPattern:
    """
    Pattern: What assumptions does this belief rest on?
    Per Cartwright: Distinguish local from structural contingencies.
    """

    def traverse(self, web: WebOfBelief, belief_id: str, depth: int = 3) -> ContingencyMapResult:
        """Map assumptions the belief depends on."""
        target = web.beliefs[belief_id]

        direct = []
        bridging = []
        theoretical = []
        methodological = []

        # Direct assumptions from source studies
        for source_id in target.source_claim_ids:
            # Methodology assumptions
            direct.append(Contingency(
                assumption=f"Study {target.source_paper} methodology was sound",
                assumption_type="direct",
                confidence=target.credence.value,
                fragility="medium",
                what_would_change="Credence would drop significantly"
            ))

        # Scope assumptions
        if target.scope.population:
            direct.append(Contingency(
                assumption=f"Effect generalizes within population: {target.scope.population}",
                assumption_type="direct",
                confidence=0.7,  # Scope generalization is often uncertain
                fragility="medium",
                what_would_change="Would need to narrow scope claims"
            ))

        # Bridge assumptions
        for constraint in web.get_constraints_for_belief(belief_id):
            if constraint.constraint_type == ConstraintType.BRIDGES:
                bridge = web.bridges.get(constraint.bridge_id) if hasattr(constraint, 'bridge_id') else None
                if bridge:
                    bridging.append(Contingency(
                        assumption=f"Bridge between {bridge.source_theory} and {bridge.target_theory} is valid",
                        assumption_type="bridging",
                        confidence=bridge.confidence,
                        fragility="high" if bridge.confidence < 0.5 else "medium",
                        what_would_change=f"Would lose support from {bridge.source_theory} evidence"
                    ))

        # Theoretical assumptions
        for constraint in web.get_constraints_for_belief(belief_id):
            if constraint.constraint_type == ConstraintType.INSTANTIATES:
                theory_belief = web.beliefs.get(constraint.source_id)
                if theory_belief and theory_belief.level == EpistemicLevel.THEORETICAL:
                    theoretical.append(Contingency(
                        assumption=f"Theory is valid: {theory_belief.content[:50]}...",
                        assumption_type="theoretical",
                        confidence=theory_belief.credence.value,
                        fragility="low",  # Theoretical assumptions are more entrenched
                        what_would_change="Would undermine theoretical interpretation"
                    ))

        return ContingencyMapResult(
            target_belief=target,
            direct_assumptions=direct,
            bridging_assumptions=bridging,
            theoretical_assumptions=theoretical,
            methodological_assumptions=methodological,
            fragility_summary=self._summarize_fragility(direct + bridging + theoretical)
        )

    def _summarize_fragility(self, contingencies: List[Contingency]) -> str:
        """Summarize overall fragility."""
        high_fragility = sum(1 for c in contingencies if c.fragility == "high")
        if high_fragility > 2:
            return "HIGH - Multiple uncertain assumptions"
        elif high_fragility > 0:
            return "MEDIUM - Some uncertain assumptions"
        else:
            return "LOW - Assumptions are relatively secure"
```

---

## 3. Vocabulary Bridge

### 3.1 Vocabulary Structure

```yaml
# Location: contracts/vocab/vocabulary_bridge.yaml

# Per Bates: Map between internal, academic, practitioner, and common terms

concepts:
  stress_recovery:
    internal: "psych.stress.recovery"
    academic: ["stress recovery", "psychophysiological restoration", "recovery from stress"]
    practitioner: ["stress reduction", "calming effect", "relaxation"]
    common: ["helps you relax", "reduces stress", "calming"]

  attention_restoration:
    internal: "cognitive.attention.restoration"
    academic: ["attention restoration", "directed attention recovery", "cognitive restoration"]
    practitioner: ["helps focus", "improves concentration", "mental clarity"]
    common: ["helps you think", "clears your head", "refreshing"]

  natural_views:
    internal: "natural.views"
    academic: ["nature views", "natural scenery", "visual access to nature"]
    practitioner: ["windows with nature views", "views of trees/plants", "natural outlook"]
    common: ["view of trees", "looking at nature", "seeing plants"]

  biophilic_design:
    internal: "design.biophilic"
    academic: ["biophilic design", "nature-inspired design", "biophilia-based design"]
    practitioner: ["nature in buildings", "bringing nature inside", "natural elements"]
    common: ["plants and nature in buildings", "natural design"]

  # ... (20 core concepts per panel recommendation)
```

### 3.2 Vocabulary Bridge Implementation

```python
# Location: src/services/vocabulary_bridge.py

class VocabularyBridge:
    """Translate between vocabulary domains."""

    def __init__(self, vocab_path: str):
        self.vocab = self._load_vocab(vocab_path)
        self._build_indices()

    def _build_indices(self):
        """Build reverse indices for fast lookup."""
        self.common_to_internal = {}
        self.academic_to_internal = {}
        self.practitioner_to_internal = {}

        for concept_id, concept in self.vocab["concepts"].items():
            internal = concept["internal"]

            for term in concept.get("common", []):
                self.common_to_internal[term.lower()] = internal
            for term in concept.get("academic", []):
                self.academic_to_internal[term.lower()] = internal
            for term in concept.get("practitioner", []):
                self.practitioner_to_internal[term.lower()] = internal

    def query_to_internal(self, query: str) -> List[str]:
        """
        Map user query terms to internal IDs.
        Per Bates: Handle vocabulary mismatch gracefully.
        """
        query_lower = query.lower()
        matches = []

        # Check each index
        for index in [self.common_to_internal, self.practitioner_to_internal, self.academic_to_internal]:
            for term, internal in index.items():
                if term in query_lower:
                    matches.append(internal)

        return list(set(matches))

    def internal_to_user(self, internal_id: str, mode: UserMode) -> str:
        """
        Convert internal term to user-appropriate term.
        """
        for concept in self.vocab["concepts"].values():
            if concept["internal"] == internal_id:
                if mode == UserMode.NOVICE:
                    return concept.get("common", [concept["internal"]])[0]
                elif mode in [UserMode.QUICK, UserMode.STANDARD]:
                    return concept.get("practitioner", [concept["internal"]])[0]
                else:  # DEEP
                    return concept.get("academic", [concept["internal"]])[0]

        return internal_id  # Fallback

    def find_related_beliefs(self, query: str, web: WebOfBelief) -> List[Belief]:
        """Find beliefs related to query terms."""
        internal_ids = self.query_to_internal(query)

        related = []
        for belief in web.beliefs.values():
            if belief.environment_id in internal_ids or belief.outcome_id in internal_ids:
                related.append(belief)

        return related
```

---

## 4. Template System

### 4.1 Template Structure

```python
# Location: src/services/explanation_templates.py

from jinja2 import Environment, PackageLoader

TEMPLATES = {
    "evidence_trace": {
        "quick": """
**{{ result.target_belief.content }}**
Supported by {{ result.supporting_evidence|length }} studies{% if result.contradicting_evidence %}, contradicted by {{ result.contradicting_evidence|length }}{% endif %}.
Strongest: {{ result.strongest_support.source_paper }} ({{ result.strongest_support.summary }})
""",

        "standard": """
## Evidence for: {{ result.target_belief.content }}

**Confidence:** {{ "%.0f"|format(result.target_belief.credence.value * 100) }}% (± {{ "%.0f"|format(result.target_belief.credence.uncertainty * 100) }}%)

### Supporting Evidence ({{ result.supporting_evidence|length }} studies)
{% for item in result.supporting_evidence[:5] %}
- **{{ item.source_paper }}**: {{ item.summary }}
  - Strength: {{ "%.0f"|format(item.constraint_strength * 100) }}% | N={{ item.sample_size or "unreported" }}{% if item.effect_size %} | d={{ "%.2f"|format(item.effect_size) }}{% endif %}

{% endfor %}
{% if result.supporting_evidence|length > 5 %}
*...and {{ result.supporting_evidence|length - 5 }} more studies*
{% endif %}

{% if result.contradicting_evidence %}
### Contradicting Evidence ({{ result.contradicting_evidence|length }} studies)
{% for item in result.contradicting_evidence[:3] %}
- **{{ item.source_paper }}**: {{ item.summary }}
{% endfor %}
{% endif %}

### Summary
The strongest support comes from {{ result.strongest_support.source_paper }}.
{% if result.contradicting_evidence %}
Note: Some studies report contrary findings. See details above.
{% endif %}
""",

        "deep": """
## Comprehensive Evidence Trace: {{ result.target_belief.content }}

### Metadata
- Belief ID: {{ result.target_belief.id }}
- Epistemic Level: {{ result.target_belief.level.value }}
- Theory Association: {{ result.target_belief.theory or "None" }}
- Scope: {{ result.target_belief.scope.population or "Unspecified" }} / {{ result.target_belief.scope.setting or "Unspecified" }}

### Quantitative Summary
- Total Studies: {{ result.total_studies }}
- Supporting: {{ result.supporting_evidence|length }}
- Contradicting: {{ result.contradicting_evidence|length }}
- Weighted Support Ratio: {{ "%.2f"|format(result.supporting_evidence|length / result.total_studies if result.total_studies > 0 else 0) }}

### Full Evidence List
{% for item in result.supporting_evidence %}
#### {{ item.source_paper }}
- **Claim:** {{ item.belief.content }}
- **Constraint Strength:** {{ "%.3f"|format(item.constraint_strength) }}
- **Study Quality:** {{ "%.2f"|format(item.study_quality) }}
- **Sample Size:** {{ item.sample_size or "NR" }}
- **Effect Size:** {{ "%.3f"|format(item.effect_size) if item.effect_size else "NR" }}
- **Scope:** {{ item.belief.scope.to_dict() }}

{% endfor %}

### Methodological Notes
[Detailed analysis would go here]
"""
    },

    "practical": """
## Practical Implications

{% if implications %}
### Design Considerations
{% for imp in implications.design_considerations %}
- {{ imp }}
{% endfor %}

### What the Evidence Suggests
{% for sug in implications.suggestions %}
- {{ sug.action }} (evidence: {{ sug.evidence_strength }})
{% endfor %}

### Caveats for Implementation
{% for caveat in implications.caveats %}
- {{ caveat }}
{% endfor %}
{% else %}
*Insufficient evidence for specific design recommendations.*
{% endif %}
"""
}
```

### 4.2 Practical Implications Generator (Kaplan)

```python
@dataclass
class PracticalImplication:
    """A practical implication for design."""
    action: str
    evidence_strength: str  # "strong", "moderate", "preliminary"
    confidence: float
    caveats: List[str]

@dataclass
class PracticalImplicationsResult:
    """Practical implications for a belief."""
    design_considerations: List[str]
    suggestions: List[PracticalImplication]
    caveats: List[str]
    applicability_note: str

class PracticalImplicationsGenerator:
    """
    Generate practical design implications from beliefs.
    Per Kaplan: Every explanation should include actionable guidance.
    """

    def generate(self, belief: Belief, evidence: EvidenceTraceResult) -> PracticalImplicationsResult:
        """Generate practical implications."""

        considerations = []
        suggestions = []
        caveats = []

        # Determine evidence strength
        n_studies = len(evidence.supporting_evidence)
        avg_effect = self._average_effect_size(evidence.supporting_evidence)

        if n_studies >= 5 and avg_effect and avg_effect > 0.3:
            strength = "strong"
        elif n_studies >= 2:
            strength = "moderate"
        else:
            strength = "preliminary"

        # Generate implications based on belief content
        env_id = belief.environment_id
        outcome_id = belief.outcome_id

        if env_id and outcome_id:
            # Map to design action
            design_action = self._map_to_design_action(env_id, outcome_id, belief)
            if design_action:
                suggestions.append(PracticalImplication(
                    action=design_action,
                    evidence_strength=strength,
                    confidence=belief.credence.value,
                    caveats=[]
                ))

        # Add scope-based caveats
        if belief.scope.setting:
            caveats.append(f"Evidence primarily from {belief.scope.setting} settings")
        if belief.scope.population:
            caveats.append(f"Tested with {belief.scope.population}; may vary for other groups")

        # Lab-to-field caveat (per Kaplan)
        lab_studies = sum(1 for e in evidence.supporting_evidence
                        if "lab" in (e.belief.scope.setting or "").lower())
        if lab_studies > n_studies * 0.5:
            caveats.append("Most evidence from laboratory settings; field effects may differ")

        return PracticalImplicationsResult(
            design_considerations=considerations,
            suggestions=suggestions,
            caveats=caveats,
            applicability_note=f"Evidence strength: {strength} ({n_studies} studies)"
        )

    def _map_to_design_action(self, env_id: str, outcome_id: str, belief: Belief) -> Optional[str]:
        """Map environment-outcome pair to design recommendation."""

        # Simple rule-based mapping
        mappings = {
            ("natural.views", "psych.stress"): "Provide visual access to natural elements (trees, plants, water) in high-stress areas",
            ("natural.plants", "psych.stress"): "Incorporate live plants in spaces where stress reduction is important",
            ("spatial.ceiling_height", "cognitive.creativity"): "Consider higher ceilings in spaces intended for creative work",
            ("natural.lighting", "psych.mood"): "Maximize natural daylight access in occupied spaces",
            # ... more mappings
        }

        key = (env_id, outcome_id.split(".")[0] + "." + outcome_id.split(".")[1] if "." in outcome_id else outcome_id)
        return mappings.get(key)
```

---

## 5. Main Interface

```python
# Location: src/services/interpretive_intelligence.py

class InterpretiveEngine:
    """
    Main interface for interpretive intelligence.
    Coordinates patterns, vocabulary, and templates.
    """

    def __init__(self, web: WebOfBelief, vocab_path: str):
        self.web = web
        self.vocab = VocabularyBridge(vocab_path)
        self.patterns = {
            ExplanationPattern.EVIDENCE_TRACE: EvidenceTracePattern(),
            ExplanationPattern.MECHANISM_EXPLANATION: MechanismExplanationPattern(),
            ExplanationPattern.CONTINGENCY_MAP: ContingencyMapPattern(),
            ExplanationPattern.CREDIBILITY_ASSESSMENT: CredibilityAssessmentPattern(),
            ExplanationPattern.SCOPE_SPECIFICATION: ScopeSpecificationPattern(),
            ExplanationPattern.DISAGREEMENT_SUMMARY: DisagreementSummaryPattern(),
            ExplanationPattern.PRACTICAL_IMPLICATIONS: PracticalImplicationsPattern(),
        }
        self.practical_generator = PracticalImplicationsGenerator()

    def answer_question(
        self,
        question: str,
        mode: UserMode = UserMode.STANDARD
    ) -> ExplanationResponse:
        """
        Answer a natural language question.
        Per Wilson: Achieve cognitive effect with minimal processing effort.
        """
        # Classify question to pattern
        pattern, belief_ids = self._classify_question(question)

        if not belief_ids:
            return ExplanationResponse(
                success=False,
                message="I couldn't find relevant information for your question. "
                       "Try rephrasing or asking about a specific topic."
            )

        # Generate explanation
        return self.explain(
            pattern=pattern,
            belief_id=belief_ids[0],
            mode=mode
        )

    def explain(
        self,
        pattern: ExplanationPattern,
        belief_id: str,
        mode: UserMode = UserMode.STANDARD,
        include_practical: bool = True
    ) -> ExplanationResponse:
        """Generate explanation using specified pattern."""

        if belief_id not in self.web.beliefs:
            return ExplanationResponse(
                success=False,
                message=f"Belief not found: {belief_id}"
            )

        # Traverse
        pattern_impl = self.patterns[pattern]
        result = pattern_impl.traverse(self.web, belief_id)

        # Render
        explanation = pattern_impl.render(result, mode)

        # Add practical implications (per Kaplan)
        practical = None
        if include_practical and pattern != ExplanationPattern.PRACTICAL_IMPLICATIONS:
            evidence = self.patterns[ExplanationPattern.EVIDENCE_TRACE].traverse(self.web, belief_id)
            practical = self.practical_generator.generate(
                self.web.beliefs[belief_id],
                evidence
            )
            practical_text = TEMPLATES["practical"].render(implications=practical)
            explanation += "\n" + practical_text

        return ExplanationResponse(
            success=True,
            pattern=pattern,
            mode=mode,
            explanation=explanation,
            structured_data=result,
            practical_implications=practical
        )

    def _classify_question(self, question: str) -> Tuple[ExplanationPattern, List[str]]:
        """
        Classify question to pattern and identify relevant beliefs.
        Per Bates: Handle vocabulary mismatch.
        """
        q_lower = question.lower()

        # Pattern detection (simple keyword-based)
        if any(w in q_lower for w in ["evidence", "support", "studies", "research"]):
            pattern = ExplanationPattern.EVIDENCE_TRACE
        elif any(w in q_lower for w in ["how", "mechanism", "why does", "works"]):
            pattern = ExplanationPattern.MECHANISM_EXPLANATION
        elif any(w in q_lower for w in ["reliable", "confident", "trust", "sure"]):
            pattern = ExplanationPattern.CREDIBILITY_ASSESSMENT
        elif any(w in q_lower for w in ["assume", "depend", "rest on", "if"]):
            pattern = ExplanationPattern.CONTINGENCY_MAP
        elif any(w in q_lower for w in ["disagree", "controversy", "debate"]):
            pattern = ExplanationPattern.DISAGREEMENT_SUMMARY
        elif any(w in q_lower for w in ["apply", "where", "when", "population"]):
            pattern = ExplanationPattern.SCOPE_SPECIFICATION
        elif any(w in q_lower for w in ["recommend", "should", "design", "practical"]):
            pattern = ExplanationPattern.PRACTICAL_IMPLICATIONS
        else:
            pattern = ExplanationPattern.EVIDENCE_TRACE  # Default

        # Find relevant beliefs via vocabulary bridge
        beliefs = self.vocab.find_related_beliefs(question, self.web)

        return pattern, [b.id for b in beliefs]
```

---

## 6. Sprint Plan

### Sprint B: Core Patterns (2 weeks)

**Goals:**
- Implement Evidence Trace and Credibility Assessment patterns
- Build vocabulary bridge with 20 core concepts
- Create template library (quick, standard modes)
- Basic question classification

**Deliverables:**
- `src/services/interpretive_intelligence.py` (core)
- `src/services/vocabulary_bridge.py`
- `src/services/explanation_templates.py`
- `contracts/vocab/vocabulary_bridge.yaml`
- Tests for pattern traversal

**Decision Points to Track:**
- Template wording choices
- Confidence threshold for "strong" vs "moderate" vs "preliminary"
- How to handle beliefs with no evidence

### Sprint C: Extended Patterns (2 weeks)

**Goals:**
- Implement Mechanism Explanation, Contingency Map
- Implement Practical Implications generator
- Add deep mode templates
- Improve question classification

**Deliverables:**
- All seven patterns implemented
- Complete template library (all modes)
- Practical implications for all belief types
- Improved NLU for question classification

**Decision Points to Track:**
- Mechanism chain maximum depth
- What contingencies are "worth mentioning" (per Cartwright)
- Design recommendation mappings

### Sprint D: User Testing (2 weeks)

**Goals:**
- Test with 5-10 CNfA practitioners
- Measure comprehension, inference, action (per Wilson)
- Refine templates based on feedback
- Add novice mode

**Deliverables:**
- User test results
- Refined templates
- Novice mode explanations
- Documentation

**Decision Points to Track:**
- Which explanations confused users?
- What information was missing?
- What vocabulary needed adjustment?

---

## 7. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Comprehension | 80% correct answers | Post-explanation quiz |
| Inference | 70% draw correct conclusions | Scenario-based questions |
| Usefulness | 4/5 rating | User survey |
| Coverage | 90% of queries get responses | Query log analysis |
| Response time | <1 sec for standard mode | Benchmarks |
| No LLM calls | 90% of explanations | Processing logs |

---

## 8. Files to Create

```
src/services/interpretive_intelligence.py    # Main interface
src/services/vocabulary_bridge.py            # Term translation
src/services/explanation_templates.py        # Jinja templates
src/services/explanation_patterns/           # Pattern implementations
  __init__.py
  evidence_trace.py
  mechanism.py
  contingency.py
  credibility.py
  scope.py
  disagreement.py
  practical.py
contracts/vocab/vocabulary_bridge.yaml       # Vocabulary mappings
tests/test_interpretive_intelligence.py
tests/test_vocabulary_bridge.py
docs/INTERPRETIVE_INTELLIGENCE_USER_GUIDE.md
```

---

*Plan ready for critique*
*Next step: Review by team + world-class system designer*
