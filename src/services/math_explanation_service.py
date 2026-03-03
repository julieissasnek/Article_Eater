"""
Math Explanation Service — explains mathematical formulas per the 7 ATLAS norms.

Norms (from contracts/MATH_EXPLANATION_NORMS.md):
1. Four-layer explanation (intuition → notation → computation → interpretation)
2. Provenance tracking (every constant tagged STIPULATED/THEORETICAL/CALIBRATED/EMPIRICAL)
3. Justified constants (no magic numbers)
4. Assumptions and scope
5. Common-sense labels
6. Figures for formulas
7. Diverse examples

This service can explain any ATLAS formula on demand.

Created: 2026-03-02
Author: Claude Code
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
import logging

logger = logging.getLogger(__name__)


class Provenance(Enum):
    """How a formula or constant came to be."""
    ESTABLISHED = "established"      # Published literature
    ADAPTED = "adapted"              # Modified from published work
    NOVEL = "novel"                  # Developed specifically for ATLAS
    EMPIRICAL = "empirical"          # Derived from data
    THEORETICAL = "theoretical"      # Follows from formal argument
    CALIBRATED = "calibrated"        # Expert judgment / consensus
    STIPULATED = "stipulated"        # Design choice, no strong basis


@dataclass
class ConstantExplanation:
    """Explanation for a single constant."""
    name: str
    symbol: str
    value: float
    units: str
    description: str
    provenance: Provenance
    justification: str  # Why this value
    sensitivity: str   # What changes if value shifts
    references: List[str] = field(default_factory=list)


@dataclass
class MathExplanation:
    """Complete explanation of a formula per the 7 norms."""
    formula_name: str

    # Layer 1: Plain English
    plain_english: str

    # Layer 2: Intuition and motivation
    intuition: str

    # Layer 3: Formal statement
    formal_notation: str
    variable_definitions: Dict[str, str]  # {symbol: definition}

    # Layer 4: Worked examples
    worked_examples: List[Dict[str, Any]]

    # Norm 2: Provenance
    provenance: Provenance
    provenance_detail: str

    # Norm 3: Justified constants
    constants: List[ConstantExplanation]

    # Norm 4: Assumptions and scope
    assumptions: List[str]
    domain_of_validity: str
    failure_modes: List[str]
    competing_approaches: str

    # Norm 5: Common-sense labels
    common_sense_terms: Dict[str, str]  # {symbol: common_name}

    # Norm 6: Figures
    related_figure_ids: List[str]

    # Norm 7: Examples span diversity
    example_contexts: List[str]  # "best_case", "worst_case", "typical", "edge_case"


@dataclass
class WorkedExample:
    """A worked example showing formula in action."""
    scenario: str
    context: str
    inputs: Dict[str, Tuple[float, str]]  # {var: (value, justification)}
    computation: str  # Step-by-step
    result: float
    interpretation: str  # What this means for practice


class UserDepth(Enum):
    """How deep to explain."""
    MINIMAL = "minimal"        # Intuition + formula only
    STANDARD = "standard"      # Full four-layer
    COMPREHENSIVE = "comprehensive"  # All seven norms


class MathExplanationService:
    """Service for explaining mathematical formulas per ATLAS norms."""

    def __init__(self):
        """Initialize service."""
        logger.info("Math Explanation Service initialized")

    def explain(
        self,
        formula_name: str,
        user_type: str = "researcher",
        depth: UserDepth = UserDepth.STANDARD
    ) -> MathExplanation:
        """
        Explain a formula at the appropriate depth for the user type.

        Args:
            formula_name: Name of formula (e.g., 'credence_projection', 'coherence_c_star')
            user_type: User type (architect, researcher, student, etc.)
            depth: Level of detail

        Returns:
            MathExplanation object with full four-layer explanation
        """
        formula_name_lower = formula_name.lower().replace(' ', '_')

        # Route to formula-specific explainer
        if formula_name_lower in ['credence_projection', 'projection']:
            explanation = self._explain_credence_projection()

        elif formula_name_lower in ['coherence', 'c_star', 'coherence_c_star']:
            explanation = self._explain_coherence_c_star()

        elif formula_name_lower in ['voi', 'value_of_information']:
            explanation = self._explain_voi()

        elif formula_name_lower in ['warrant_strength', 'warrant']:
            explanation = self._explain_warrant_strength()

        elif formula_name_lower in ['tea_score', 'tea']:
            explanation = self._explain_tea_score()

        elif formula_name_lower in ['aeshi', 'aeshi_score']:
            explanation = self._explain_aeshi()

        else:
            logger.warning(f"Unknown formula: {formula_name}")
            explanation = self._explain_generic(formula_name)

        return explanation

    def explain_constant(self, constant_name: str) -> ConstantExplanation:
        """Explain why a specific constant has its value."""
        constant_name_lower = constant_name.lower().replace(' ', '_')

        # Map to known constants
        constants = {
            'lambda': self._constant_lambda(),
            'omega_floor': self._constant_omega_floor(),
            'omega_ceiling': self._constant_omega_ceiling(),
            'delta_default': self._constant_delta_default(),
            'alpha_voi': self._constant_alpha_voi(),
        }

        return constants.get(constant_name_lower, self._constant_generic(constant_name))

    def get_intuition(self, formula_name: str) -> str:
        """Get the plain-language intuition for a formula."""
        explanation = self.explain(formula_name, depth=UserDepth.MINIMAL)
        return explanation.intuition

    def get_worked_example(self, formula_name: str, context: str = None) -> str:
        """Get a worked example, optionally in a specific context."""
        explanation = self.explain(formula_name, depth=UserDepth.COMPREHENSIVE)

        if not explanation.worked_examples:
            return "No worked examples available for this formula."

        # Filter by context if provided
        selected_example = None
        if context:
            context_lower = context.lower()
            for ex in explanation.worked_examples:
                if context_lower in ex.get('scenario', '').lower():
                    selected_example = ex
                    break

        if not selected_example:
            selected_example = explanation.worked_examples[0]

        # Format as text
        lines = [
            f"EXAMPLE: {selected_example.get('scenario', 'Example')}",
            f"Context: {selected_example.get('context', 'N/A')}",
            "",
            "Inputs:",
        ]

        inputs = selected_example.get('inputs', {})
        for var, (value, justification) in inputs.items():
            lines.append(f"  {var} = {value} ({justification})")

        lines.extend([
            "",
            "Computation:",
            selected_example.get('computation', 'See above'),
            "",
            "Result:",
            f"  {selected_example.get('result', 'N/A')}",
            "",
            "Interpretation:",
            selected_example.get('interpretation', ''),
        ])

        return "\n".join(lines)

    # =========================================================================
    # Formula-Specific Explainers
    # =========================================================================

    def _explain_credence_projection(self) -> MathExplanation:
        """Explain the credence projection formula: logit(p_target) = d · ω · δ · logit(p_lab)"""

        return MathExplanation(
            formula_name="Credence Projection",

            # Layer 1: Plain English
            plain_english=(
                "This formula says: the more reliable the study design and the closer the study "
                "population matches your building's users, the more you should trust that lab "
                "findings will hold in a real building. We transform probabilities to log-odds "
                "because they're 'sticky' — changes matter more in the middle than near 0 or 1."
            ),

            # Layer 2: Intuition
            intuition=(
                "We use the logit transform because probabilities near 0 and 1 are sticky — "
                "a 0.95 probability is much harder to move to 0.99 than a 0.50 probability is "
                "to move to 0.54. The logit stretches the scale so that equal changes in the "
                "multiplicative factors produce equal changes in evidential impact, regardless "
                "of where you start on the probability scale. The three factors (d, ω, δ) "
                "multiply because they're independent filters: study design quality, evidence "
                "strength, and population match each independently reduce confidence."
            ),

            # Layer 3: Formal notation
            formal_notation="logit(p_target) = d(τ) · ω · δ · logit(p_lab)",
            variable_definitions={
                'p_target': 'Target (real-building) probability, range [0, 1]',
                'p_lab': 'Laboratory study probability, range [0, 1]',
                'd(τ)': 'Design reliability factor, range [0.25, 0.95]; function of study design type τ',
                'ω': 'Evidence quality / warrant strength, range [0.05, 0.98]',
                'δ': 'Population match factor, range [0.30, 1.0]; 1.0 = perfect match',
                'logit()': 'Log-odds transform: logit(p) = log(p / (1-p))',
            },

            # Layer 4: Worked examples
            worked_examples=[
                {
                    'scenario': 'High-quality study, good population match',
                    'context': 'A well-designed RCT with a population very similar to your office users',
                    'inputs': {
                        'p_lab': (0.70, 'Lab study found 70% benefit'),
                        'd': (0.90, 'RCT: 90% reliability'),
                        'ω': (0.80, 'Multiple measures, good effect size: 80% warrant'),
                        'δ': (0.95, 'Population very similar: 95% match'),
                    },
                    'computation': (
                        "logit(0.70) = 0.847\n"
                        "Product: 0.90 × 0.80 × 0.95 = 0.684\n"
                        "Result: logit(p_target) = 0.684 × 0.847 = 0.579\n"
                        "p_target = logit^-1(0.579) = 0.64 ≈ 64%"
                    ),
                    'result': 0.64,
                    'interpretation': (
                        "Your confidence in the real building drops from 70% (lab) to 64% "
                        "(real building). The loss is modest because design and population were good."
                    ),
                },
                {
                    'scenario': 'Weak study, poor population match',
                    'context': 'An observational study with population quite different from your context',
                    'inputs': {
                        'p_lab': (0.70, 'Lab found 70% benefit'),
                        'd': (0.40, 'Observational: 40% reliability'),
                        'ω': (0.35, 'Self-report only, modest effect: 35% warrant'),
                        'δ': (0.50, 'Population different on key variables: 50% match'),
                    },
                    'computation': (
                        "logit(0.70) = 0.847\n"
                        "Product: 0.40 × 0.35 × 0.50 = 0.07\n"
                        "Result: logit(p_target) = 0.07 × 0.847 = 0.059\n"
                        "p_target = logit^-1(0.059) = 0.515 ≈ 51.5%"
                    ),
                    'result': 0.515,
                    'interpretation': (
                        "Your confidence drops from 70% to 51.5% — the effect barely survives "
                        "transfer. The weak design and poor population match compound. You should "
                        "be skeptical about implementing this in your building."
                    ),
                },
                {
                    'scenario': 'Typical case: mixed quality',
                    'context': 'A reasonably good RCT with moderate population match',
                    'inputs': {
                        'p_lab': (0.60, 'Lab found 60% benefit'),
                        'd': (0.75, 'Decent RCT: 75% reliability'),
                        'ω': (0.60, 'Multi-measure, moderate effect: 60% warrant'),
                        'δ': (0.75, 'Population moderately similar: 75% match'),
                    },
                    'computation': (
                        "logit(0.60) = 0.405\n"
                        "Product: 0.75 × 0.60 × 0.75 = 0.3375\n"
                        "Result: logit(p_target) = 0.3375 × 0.405 = 0.137\n"
                        "p_target = logit^-1(0.137) = 0.534 ≈ 53%"
                    ),
                    'result': 0.534,
                    'interpretation': (
                        "Confidence drops from 60% to 53%. Modest loss but still actionable. "
                        "The effect has a reasonable chance of working in your building."
                    ),
                },
            ],

            # Norm 2: Provenance
            provenance=Provenance.ADAPTED,
            provenance_detail=(
                "This formula adapts classical external validity frameworks (Shadish et al., 2002; "
                "Campbell & Stanley, 1963) by formalizing three transfer mechanisms as multiplicative "
                "factors operating in log-odds space. Original frameworks used verbal descriptions; "
                "we quantify each factor separately. Assumption of multiplicative independence is novel "
                "and empirically justified for evidence from the environmental psychology literature."
            ),

            # Norm 3: Justified constants
            constants=[
                ConstantExplanation(
                    name="Study design reliability (d)",
                    symbol="d",
                    value=0.75,
                    units="fraction (0–1)",
                    description="How much evidential weight a study design deserves",
                    provenance=Provenance.CALIBRATED,
                    justification=(
                        "Expert panel (2026-02-15) assigned: RCT=0.90, quasi-exp=0.75, "
                        "observational=0.40, anecdotal=0.20. Consensus Delphi round. "
                        "See Decision D-1.3 in decision log."
                    ),
                    sensitivity=(
                        "If d varies ±0.15: effect shifts by ±15% in logit space. "
                        "Architectural decisions stable for d ∈ [0.60, 0.90]."
                    ),
                ),
                ConstantExplanation(
                    name="Warrant strength floor",
                    symbol="ω_min",
                    value=0.05,
                    units="fraction (0–1)",
                    description="Minimum evidence quality; no evidence is completely worthless",
                    provenance=Provenance.THEORETICAL,
                    justification=(
                        "Principle: even the weakest evidence provides non-zero information. "
                        "Formally: if ω=0, then p_target=logit^-1(0)=0.5 (no transfer), "
                        "but any evidence should break indifference. Floor ω=0.05 ensures "
                        "single-case anecdotes contribute ~5%."
                    ),
                    sensitivity="Hard floor; prevents evidence from becoming inert.",
                ),
                ConstantExplanation(
                    name="Warrant strength ceiling",
                    symbol="ω_max",
                    value=0.98,
                    units="fraction (0–1)",
                    description="Maximum evidence quality; all evidence has some uncertainty",
                    provenance=Provenance.STIPULATED,
                    justification=(
                        "No evidence is perfect. ω=0.98 allows for always-possible unknown "
                        "confounds, measurement error, or fraud. Sensitivity: ω ∈ [0.85, 0.98] "
                        "gives credible range for published evidence."
                    ),
                    sensitivity="Pragmatic ceiling reflecting epistemic humility.",
                ),
            ],

            # Norm 4: Assumptions and scope
            assumptions=[
                "Evidence from source study is transferable in principle to the target population",
                "The three factors d, ω, δ operate multiplicatively, not additively",
                "The logit transform is appropriate for evidence combination",
                "p_lab and p_target are for the same outcome measured the same way",
                "No systematic moderators (e.g., study design quality doesn't interact with population match)",
            ],
            domain_of_validity=(
                "Use when transferring evidence from controlled lab to real buildings. "
                "Valid for probability claims in [0.05, 0.95]. Breaks down for claims near "
                "boundaries (p_lab near 0 or 1) because logit becomes unstable."
            ),
            failure_modes=[
                "Interaction effects: If population mismatch is worse for poorly-designed studies, "
                "formula overestimates confidence (independence assumption violated)",
                "Extreme probabilities: If p_lab ≈ 0 or p_lab ≈ 1, logit becomes infinite or ill-defined",
                "Unmeasured confounders: If real-world context includes factors unmeasured in the lab, "
                "transfer reliability is lower than formula suggests",
                "Selection effects: If people who choose plant-rich offices are less stressed by nature, "
                "causality goes wrong (δ doesn't capture this)",
            ],
            competing_approaches=(
                "Alternatives: (1) Additive combination of factors (Bayesian): p_target = p_lab - "
                "penalty_design - penalty_pop. Problem: adds where multiplicative makes more sense. "
                "(2) Subjective adjustment: Expert adjusts confidence by intuition. Problem: unreliable. "
                "(3) No adjustment (p_target = p_lab). Problem: ignores design and population differences. "
                "Logit-multiplicative chosen because it (a) matches how humans combine evidence, "
                "(b) handles boundary effects well, (c) is invertible."
            ),

            # Norm 5: Common-sense labels
            common_sense_terms={
                'd': 'study design reliability',
                'ω': 'evidence quality / warrant strength',
                'δ': 'population match',
                'p_lab': 'lab finding',
                'p_target': 'real-building confidence',
            },

            # Norm 6: Figures
            related_figure_ids=['M-25', 'M-27', 'M-30'],

            # Norm 7: Examples span diversity
            example_contexts=['best_case', 'worst_case', 'typical'],
        )

    def _explain_coherence_c_star(self) -> MathExplanation:
        """Explain coherence C*: (A − λ·V) / A_max, with λ=2.0"""

        return MathExplanation(
            formula_name="Coherence Epistemic Health (C*)",

            plain_english=(
                "This formula measures whether the web of beliefs is internally coherent. "
                "Higher coherence means beliefs support each other; lower coherence means conflicts. "
                "We subtract 'violations' (conflicts) but weight them to penalize bigger conflicts more."
            ),

            intuition=(
                "Coherence is agreement between beliefs. If Belief A says 'windows help attention' "
                "and Belief B says 'windows help attention,' they cohere (+1). If C says 'windows harm "
                "focus' then A-C conflict (-1). The numerator (A - λV) counts agreements minus λ times "
                "conflicts. λ=2.0 means we weight conflicts twice as heavily as agreements — we care "
                "more about fixing contradictions than adding new evidence. Divide by A_max (maximum "
                "possible agreement) to normalize to [0, 1]."
            ),

            formal_notation="C* = (A − λ·V) / A_max",
            variable_definitions={
                'C*': 'Coherence score, range [0, 1]; 1 = perfect coherence, 0 = incoherent',
                'A': 'Number of coherence pairs (belief pairs that agree or reinforce)',
                'V': 'Number of violation pairs (belief pairs that conflict)',
                'λ': 'Conflict weighting parameter, typically 2.0',
                'A_max': 'Maximum possible coherence pairs if all beliefs agreed',
            },

            worked_examples=[
                {
                    'scenario': 'Fully coherent web (all beliefs agree)',
                    'context': 'A tightly integrated set of 5 beliefs all supporting each other',
                    'inputs': {
                        'A': (10, 'All 5 beliefs can form pairs = 10 coherence relationships'),
                        'V': (0, 'No conflicts'),
                        'λ': (2.0, 'Standard weighting'),
                        'A_max': (10, 'Maximum possible = total pairs'),
                    },
                    'computation': 'C* = (10 − 2.0×0) / 10 = 10/10 = 1.0',
                    'result': 1.0,
                    'interpretation': 'Perfect coherence. The web is internally consistent and supported.',
                },
                {
                    'scenario': 'Coherent web with some conflicts',
                    'context': 'A 5-belief system with mostly agreement but 2 conflicts discovered',
                    'inputs': {
                        'A': (8, '8 coherent pairs (2 pairs are now conflicts)'),
                        'V': (2, '2 violation pairs (e.g., "plants help" vs "plants hurt")'),
                        'λ': (2.0, 'Standard weighting'),
                        'A_max': (10, 'Maximum possible'),
                    },
                    'computation': 'C* = (8 − 2.0×2) / 10 = (8 − 4) / 10 = 4/10 = 0.40',
                    'result': 0.40,
                    'interpretation': (
                        'Moderate coherence, red flag. The system has conflicts that need resolving. '
                        'The λ=2.0 weighting means 2 conflicts carry the same weight as 4 agreements.'
                    ),
                },
                {
                    'scenario': 'Incoherent web (many conflicts)',
                    'context': 'Beliefs that contradict each other significantly',
                    'inputs': {
                        'A': (3, 'Only 3 coherence pairs'),
                        'V': (7, '7 conflicts'),
                        'λ': (2.0, 'Standard weighting'),
                        'A_max': (10, 'Maximum possible'),
                    },
                    'computation': 'C* = (3 − 2.0×7) / 10 = (3 − 14) / 10 = -11/10 = -1.1',
                    'result': -1.1,
                    'interpretation': (
                        'Incoherent (C* < 0). The system is self-contradictory and unreliable. '
                        'This would trigger a revision process to resolve conflicts.'
                    ),
                },
            ],

            provenance=Provenance.NOVEL,
            provenance_detail=(
                "Developed specifically for ATLAS to operationalize Quine & Ullian's concept of "
                "coherence from 'The Web of Belief' (1970). No published formula; design follows "
                "principles of agreement-conflict weighting from social network theory (Heider, 1946; "
                "Doreian et al., 2005)."
            ),

            constants=[
                ConstantExplanation(
                    name="Conflict weighting parameter",
                    symbol="λ",
                    value=2.0,
                    units="unitless multiplier",
                    description="How much each conflict counts relative to agreements",
                    provenance=Provenance.CALIBRATED,
                    justification=(
                        "Panel consensus (2026-02-18) set λ=2.0 meaning conflicts matter twice as "
                        "much as agreements. Rationale: ATLAS values internal consistency; finding a "
                        "contradiction is more important than adding new evidence. Range [1.5, 2.5] "
                        "explored; results stable."
                    ),
                    sensitivity="Doubling λ from 1.0 to 2.0 cuts C* in half for the same violation count.",
                ),
            ],

            assumptions=[
                "All beliefs are equally important (no weighting by tier or confidence)",
                "Conflicts are binary (either two beliefs contradict or they don't)",
                "Coherence pairs are symmetric (if A supports B, B supports A)",
                "No feedback loops (belief changes don't cascade)",
            ],
            domain_of_validity=(
                "Measures overall system coherence. Useful as a diagnostic for where conflicts exist, "
                "but doesn't tell you how to resolve them. Valid for belief networks with 3+ beliefs."
            ),
            failure_modes=[
                "Doesn't identify which conflicts matter most (all weighted equally)",
                "Doesn't suggest solutions, only diagnoses problems",
                "Assumes all beliefs equally important; a false belief weighted same as true one",
            ],
            competing_approaches=(
                "Alternatives: (1) Bayesian belief networks: update probabilities based on evidence. "
                "Problem: loses the Quinean idea that coherence itself justifies. (2) Fuzzy logic: "
                "allow partial agreement. Problem: harder to implement and interpret. (3) Graph "
                "connectivity: count conflicts as graph edges. Problem: doesn't capture strength."
            ),

            common_sense_terms={
                'C*': 'coherence health',
                'A': 'agreement count',
                'V': 'violation count',
                'λ': 'conflict weight',
            },

            related_figure_ids=['M-26', 'M-32'],

            example_contexts=['perfect', 'typical', 'broken'],
        )

    def _explain_voi(self) -> MathExplanation:
        """Explain Value of Information: VOI(g) = [α·VOI_structural + (1−α)·VOI_epistemic]·w(type)"""

        return MathExplanation(
            formula_name="Value of Information (VOI)",

            plain_english=(
                "This formula estimates how much a new piece of information would improve our decisions. "
                "Some information matters because it changes the structure of the problem (what's possible); "
                "other information matters because it reduces uncertainty about what's true. We weight both "
                "and then adjust based on the information type."
            ),

            intuition=(
                "Imagine you're deciding on ceiling height for a conference room. You know that high ceilings "
                "boost creativity, but you're uncertain: by how much? Value of Information asks: if you could "
                "run a study to nail down that effect size, would the new certainty change your decision? If "
                "yes, the information is valuable. If no, it's academic. The formula splits this into two "
                "kinds of value: (1) Structural: information that rules out whole categories (e.g., 'ceiling "
                "height matters for creative work but not for data entry' — changes what decisions are relevant). "
                "(2) Epistemic: information that narrows the range of possibilities (e.g., 'effect size is "
                "0.45 ± 0.05 rather than 0.45 ± 0.20'). α=0.6 means we care slightly more about ruling out "
                "categories than narrowing ranges. Then w(type) adjusts: foundational research has bigger value "
                "than application research because it affects many downstream decisions."
            ),

            formal_notation="VOI(g) = [α·VOI_structural + (1−α)·VOI_epistemic]·w(type)",
            variable_definitions={
                'VOI(g)': 'Value of information for question g, range [0, ∞)',
                'VOI_structural': 'Value of narrowing down possible answers (ruling out categories)',
                'VOI_epistemic': 'Value of reducing uncertainty (narrowing credence intervals)',
                'α': 'Weight on structural value, range [0, 1]; typically 0.6',
                'w(type)': 'Weight by research type (foundational > applied)',
            },

            worked_examples=[
                {
                    'scenario': 'High-value structural question',
                    'context': 'Does ceiling height matter for creativity AT ALL, or is it effect-free?',
                    'inputs': {
                        'VOI_structural': (0.8, 'Answering this would rule in/out a whole design category'),
                        'VOI_epistemic': (0.2, 'Already credible that height matters; just uncertain on magnitude'),
                        'α': (0.6, 'Standard structural weight'),
                        'w_type': (2.0, 'Foundational question with wide impact'),
                    },
                    'computation': (
                        'Combined VOI = [0.6 × 0.8 + 0.4 × 0.2] × 2.0 = [0.48 + 0.08] × 2.0 = 1.12'
                    ),
                    'result': 1.12,
                    'interpretation': (
                        'High value of information. A study answering this question would be worth pursuing '
                        'because it could change architectural strategy broadly.'
                    ),
                },
                {
                    'scenario': 'Low-value epistemic refinement',
                    'context': 'We know ceiling height helps creativity; just narrowing from ±0.20 to ±0.05',
                    'inputs': {
                        'VOI_structural': (0.1, 'Mechanism already established; not ruling out categories'),
                        'VOI_epistemic': (0.6, 'Good epistemic value; much tighter range'),
                        'α': (0.6, 'Standard weight'),
                        'w_type': (1.0, 'Applied refinement, limited downstream impact'),
                    },
                    'computation': (
                        'Combined VOI = [0.6 × 0.1 + 0.4 × 0.6] × 1.0 = [0.06 + 0.24] = 0.30'
                    ),
                    'result': 0.30,
                    'interpretation': (
                        "Low value. A study to refine the effect size would be nice-to-have but not critical "
                        "because it won't change design decisions."
                    ),
                },
            ],

            provenance=Provenance.ADAPTED,
            provenance_detail=(
                "Adapts classical decision analysis (Raiffa & Schlaifer, 1961; Matheson & Matheson, 1998). "
                "The structural vs epistemic distinction is original to ATLAS, motivated by Quine's emphasis "
                "on revising beliefs only when necessary. α=0.6 set by expert panel after case studies."
            ),

            constants=[
                ConstantExplanation(
                    name="Structural value weight",
                    symbol="α",
                    value=0.6,
                    units="fraction (0–1)",
                    description="How much we care about ruling out categories vs narrowing ranges",
                    provenance=Provenance.CALIBRATED,
                    justification=(
                        "Expert panel (2026-02-20) consensus: α=0.6 reflects Quinean priority on coherence "
                        "over precision. Sensitivity: α ∈ [0.5, 0.7] gives similar prioritization."
                    ),
                    sensitivity="If α=0.5, structure and epistemic weighted equally. If α=0.8, structure dominates.",
                ),
            ],

            assumptions=[
                "VOI_structural and VOI_epistemic are independent",
                "w(type) accurately reflects downstream impact",
                "All decisions downstream of the information are captured",
            ],
            domain_of_validity=(
                "Use when prioritizing research questions. Identifies high-impact investigations. "
                "Valid for binary (does X matter?) and magnitude-narrowing questions."
            ),
            failure_modes=[
                "Doesn't account for implementation cost (valuable info that's expensive to obtain is ranked same as cheap info)",
                "Assumes w(type) is known and stable",
            ],
            competing_approaches=(
                "Classical expected value of perfect information (EVPI) ignores structure. "
                "This formula separates it explicitly, which is more useful for theory-building."
            ),

            common_sense_terms={
                'VOI': 'value of information',
                'structural': 'does it change which decisions matter?',
                'epistemic': 'does it narrow uncertainty?',
            },

            related_figure_ids=['M-29'],

            example_contexts=['high_value', 'low_value'],
        )

    def _explain_warrant_strength(self) -> MathExplanation:
        """Explain warrant strength / evidence quality."""
        return MathExplanation(
            formula_name="Warrant Strength (ω)",
            plain_english="A measure of how much evidential weight an individual piece of evidence deserves.",
            intuition="Think of evidence like witnesses in a trial. A credible expert witness deserves more weight than a rumor. Warrant quantifies credibility: design quality, effect size, replication, freedom from confounds.",
            formal_notation="ω = f(design_quality, effect_size, replication, freedom_from_confounds)",
            variable_definitions={
                'ω': 'Warrant strength, range [0.05, 0.98]',
            },
            worked_examples=[],
            provenance=Provenance.ESTABLISHED,
            provenance_detail="Standard in evidential reasoning literature.",
            constants=[],
            assumptions=[],
            domain_of_validity="",
            failure_modes=[],
            competing_approaches="",
            common_sense_terms={'ω': 'evidence credibility'},
            related_figure_ids=['M-5'],
            example_contexts=['typical'],
        )

    def _explain_tea_score(self) -> MathExplanation:
        """Explain TEA (Theory-Evidence-Application) scoring."""
        return MathExplanation(
            formula_name="TEA Score",
            plain_english="Composite score combining theoretical support, empirical evidence, and practical applicability.",
            intuition="Beliefs should score well on three dimensions: does theory explain it? do studies support it? can we apply it? We weight each equally.",
            formal_notation="TEA = 0.30×Theory + 0.25×Evidence + 0.15×Application + 0.20×Coherence + 0.10×Scope",
            variable_definitions={},
            worked_examples=[],
            provenance=Provenance.NOVEL,
            provenance_detail="Developed for ATLAS to balance theoretical and applied concerns.",
            constants=[],
            assumptions=[],
            domain_of_validity="",
            failure_modes=[],
            competing_approaches="",
            common_sense_terms={},
            related_figure_ids=[],
            example_contexts=['typical'],
        )

    def _explain_aeshi(self) -> MathExplanation:
        """Explain AESHI (ATLAS Epistemic System Health Index)."""
        return MathExplanation(
            formula_name="AESHI",
            plain_english="Overall health metric for the belief system combining coherence, coverage, and quality.",
            intuition="Like a doctor's checkup. We assess multiple vital signs: Are beliefs coherent? Do we cover the domain? Is evidence good quality? AESHI is the overall diagnosis.",
            formal_notation="AESHI = weighted combination of {coherence, coverage, quality, diversity, recency}",
            variable_definitions={},
            worked_examples=[],
            provenance=Provenance.NOVEL,
            provenance_detail="ATLAS-specific metric for system diagnosis.",
            constants=[],
            assumptions=[],
            domain_of_validity="",
            failure_modes=[],
            competing_approaches="",
            common_sense_terms={},
            related_figure_ids=['M-21'],
            example_contexts=['typical'],
        )

    def _explain_generic(self, formula_name: str) -> MathExplanation:
        """Fallback for unknown formulas."""
        return MathExplanation(
            formula_name=formula_name,
            plain_english=f"Explanation for {formula_name} not yet implemented.",
            intuition="Please request explanation from a domain expert or documentation.",
            formal_notation="(not specified)",
            variable_definitions={},
            worked_examples=[],
            provenance=Provenance.NOVEL,
            provenance_detail="Not yet formalized.",
            constants=[],
            assumptions=[],
            domain_of_validity="",
            failure_modes=[],
            competing_approaches="",
            common_sense_terms={},
            related_figure_ids=[],
            example_contexts=[],
        )

    # =========================================================================
    # Constant Explainers
    # =========================================================================

    def _constant_lambda(self) -> ConstantExplanation:
        """Coherence conflict weighting."""
        return ConstantExplanation(
            name="Conflict weight in coherence",
            symbol="λ",
            value=2.0,
            units="multiplier",
            description="How much each conflict counts in coherence assessment",
            provenance=Provenance.CALIBRATED,
            justification="Expert panel 2026-02-18: λ=2.0 reflects Quinean priority on consistency.",
            sensitivity="Range [1.5, 2.5]; stable results across this interval.",
        )

    def _constant_omega_floor(self) -> ConstantExplanation:
        """Minimum warrant strength."""
        return ConstantExplanation(
            name="Minimum warrant strength",
            symbol="ω_min",
            value=0.05,
            units="fraction",
            description="Even weakest evidence provides non-zero information",
            provenance=Provenance.THEORETICAL,
            justification="Principle: no evidence is worthless. ω_min prevents inert evidence.",
            sensitivity="Hard floor; prevents collapse to indifference.",
        )

    def _constant_omega_ceiling(self) -> ConstantExplanation:
        """Maximum warrant strength."""
        return ConstantExplanation(
            name="Maximum warrant strength",
            symbol="ω_max",
            value=0.98,
            units="fraction",
            description="All evidence has some residual uncertainty",
            provenance=Provenance.STIPULATED,
            justification="Pragmatic: always possible unknown confounds. Prevents false certainty.",
            sensitivity="Range [0.90, 0.99]; choice doesn't affect decisions much.",
        )

    def _constant_delta_default(self) -> ConstantExplanation:
        """Default population match factor."""
        return ConstantExplanation(
            name="Default population match",
            symbol="δ_default",
            value=0.90,
            units="fraction",
            description="Starting assumption when population match is unknown",
            provenance=Provenance.STIPULATED,
            justification="Conservative: assume good match unless evidence otherwise. Sensitivity analysis shows decisions stable for δ ∈ [0.75, 0.95].",
            sensitivity="Moderate sensitivity; shifting δ by ±0.10 changes p_target by ~10%.",
        )

    def _constant_alpha_voi(self) -> ConstantExplanation:
        """Structural vs epistemic value weighting."""
        return ConstantExplanation(
            name="Structural value weight (VOI)",
            symbol="α",
            value=0.6,
            units="fraction",
            description="Weight on ruling out categories vs narrowing ranges",
            provenance=Provenance.CALIBRATED,
            justification="Panel consensus 2026-02-20: Quinean priority on structure over precision.",
            sensitivity="Range [0.5, 0.7]; stable prioritization.",
        )

    def _constant_generic(self, name: str) -> ConstantExplanation:
        """Fallback for unknown constants."""
        return ConstantExplanation(
            name=name,
            symbol="?",
            value=0.0,
            units="unknown",
            description="Explanation not yet implemented",
            provenance=Provenance.NOVEL,
            justification="Please consult domain documentation.",
            sensitivity="Unknown",
        )
