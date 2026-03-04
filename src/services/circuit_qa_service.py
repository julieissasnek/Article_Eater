"""
Functional Circuit QA Service — Epistemically Framed Circuit Presentation
=========================================================================
Created: 2026-03-03
Updated: 2026-03-04 — Latent variable reframing (DK directive)

This service answers questions about functional circuits with the epistemic
care that David Kirsh requires: every circuit presentation must state its
ontological status, justify its existence, distinguish causal claims from
organizational principles, and offer appropriate follow-on questions.

Ontological Position (revised 2026-03-04):
  Functional circuits are best understood as LATENT VARIABLES — dimensions
  of structured covariance in neural-behavioral data. They may not correspond
  to any localized neural module, but they capture a real statistical regularity:
  the tendency of certain component processes to co-vary in predictable ways
  during specific tasks. Think of them as factors in a factor analysis of
  what the brain does when, say, it encounters something unexpected. The
  "sensory prediction error circuit" is the dimension along which prediction,
  comparison, and error-signaling co-vary. Whether that dimension has a single
  neural address is a separate question — and one we can test.

  This reframing resolves the Barrett (2017) vs. Batterman (2002) tension:
  circuits are not fictive neural modules (Barrett is right about that), but
  they are not mere pedagogical metaphors either (Batterman is right that
  computational universality classes are real). The latent variable framing
  says: the covariance structure is real and testable; the localization
  question is empirical, not definitional.

Epistemic Status Framework:
  STRONG       — The latent variable has been recovered across multiple
                 paradigms and labs. Factor structure is replicable. Some
                 intervention evidence (TMS, pharmacology) exists.
  MODERATE     — Components co-vary as predicted, but the full factor
                 structure has not been tested as a unit. Cross-paradigm
                 generalization is assumed, not demonstrated.
  HYPOTHETICAL — The latent variable is predicted by theory but has not
                 been extracted from data. It is a research target.

Author: Claude Code (CW) for Prof. David Kirsh, UCSD Cognitive Science
"""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# =============================================================================
# Epistemic Status Assessment
# =============================================================================

# Evidence levels for individual circuits (hand-curated based on literature)
# Keys match the molecule_id fields in data/molecules/fc_*.json
CIRCUIT_EVIDENCE_LEVELS = {
    # STRONG: Multiple labs, neural plausibility, interaction effects documented
    "FC_SENSORY_PE": "STRONG",
    "FC_REWARD_PE": "STRONG",
    "FC_AROUSAL_REGULATION": "STRONG",
    "FC_ATTENTIONAL_SELECTION": "STRONG",
    "FC_FAMILIARITY_DETECTION": "STRONG",

    # MODERATE: Components supported, interaction inferred
    "FC_SOCIAL_PE": "MODERATE",
    "FC_COGNITIVE_LOAD_REG": "MODERATE",
    "FC_THREAT_MONITORING": "MODERATE",
    "FC_COHERENCE_MONITORING": "MODERATE",
    "FC_ACTION_SELECTION": "MODERATE",
    "FC_DREAD_ACCUMULATION": "MODERATE",
    "FC_CONTEXT_GATED_THREAT": "MODERATE",
    "FC_AFFECTIVE_MEMORY_GATING": "MODERATE",
    "FC_THERMOREG_AFFECT": "MODERATE",
    "FC_VITALITY_MONITORING": "MODERATE",

    # HYPOTHETICAL: Theoretically motivated, evidence sparse
    "FC_AESTHETIC_VIOLATION": "HYPOTHETICAL",
    "FC_CURIOSITY_ACCUMULATION": "HYPOTHETICAL",
    "FC_INTERPRETIVE_SELECTION": "HYPOTHETICAL",
    "FC_EXPERTISE_GATED_AESTHETICS": "HYPOTHETICAL",
    "FC_SOCIAL_SAFETY_MONITORING": "HYPOTHETICAL",
}

# Legacy aliases for backward compatibility (long names → short names)
_LEGACY_CIRCUIT_ID_MAP = {
    "FC_SENSORY_PREDICTION_ERROR": "FC_SENSORY_PE",
    "FC_REWARD_PREDICTION_ERROR": "FC_REWARD_PE",
    "FC_SOCIAL_PREDICTION_ERROR": "FC_SOCIAL_PE",
    "FC_COGNITIVE_LOAD_REGULATION": "FC_COGNITIVE_LOAD_REG",
    "FC_THERMOREGULATORY_AFFECT": "FC_THERMOREG_AFFECT",
    "FC_AESTHETIC_EXPECTATION_VIOLATION": "FC_AESTHETIC_VIOLATION",
}

# Archetype descriptions — what the computational pattern IS
ARCHETYPE_DESCRIPTIONS = {
    "PREDICTIVE_CODING": {
        "name": "Predictive Coding",
        "computation": "Generate top-down predictions, compare with bottom-up input, propagate prediction errors upward for model updating",
        "formal": "PE = x_observed - x_predicted; update: Δw ∝ precision × PE",
        "key_refs": "Rao & Ballard (1999); Friston (2010); Clark (2013)",
        "neural_basis": "Hierarchical cortical processing; superficial pyramidal cells (errors), deep pyramidal cells (predictions)",
        "causal_status": "Computational motif with strong neural evidence in sensory cortex; extension to affect and social cognition is theoretically motivated but less directly confirmed",
    },
    "HOMEOSTATIC_REGULATION": {
        "name": "Homeostatic Regulation",
        "computation": "Sense current state, compare to setpoint, apply corrective signal proportional to deviation",
        "formal": "error = setpoint - current; correction = gain × error",
        "key_refs": "Cannon (1929); Sterling (2012); Damasio (1994)",
        "neural_basis": "Hypothalamus, brainstem autonomic nuclei, insula (interoception)",
        "causal_status": "Well-established for physiological regulation (temperature, glucose). Extension to psychological constructs (arousal, cognitive load) is a productive analogy whose limits are not yet clear",
    },
    "ACCUMULATION_TO_BOUND": {
        "name": "Accumulation to Bound",
        "computation": "Integrate noisy evidence over time until accumulated evidence reaches a decision threshold",
        "formal": "dx/dt = drift + noise; fire when x ≥ threshold",
        "key_refs": "Usher & McClelland (2001); Gold & Shadlen (2007); Ratcliff & McKoon (2008)",
        "neural_basis": "LIP, FEF, SC (saccadic decisions); caudate, STN (action selection); ACC (conflict monitoring)",
        "causal_status": "One of the most well-confirmed computational motifs in neuroscience. Neural correlates in primate single-unit recording directly match the mathematical model. Extension to emotional accumulation (dread, curiosity) is theoretically motivated but less directly tested",
    },
    "COMPETITIVE_SELECTION": {
        "name": "Competitive Selection",
        "computation": "Multiple candidates compete for representation; strongest signal wins via lateral inhibition and divisive normalization",
        "formal": "r_i = x_i / (σ² + Σ_j x_j); winner = argmax(r)",
        "key_refs": "Desimone & Duncan (1995); Carandini & Heeger (2012); Reynolds & Heeger (2009)",
        "neural_basis": "V4, IT (visual attention); basal ganglia (action selection); prefrontal cortex (working memory gating)",
        "causal_status": "Divisive normalization is described as 'a canonical neural computation' (Carandini & Heeger, 2012). The competitive selection framework is strongly supported for attention and action selection. Application to interpretive bistability is more speculative",
    },
    "GATED_PROPAGATION": {
        "name": "Gated Propagation",
        "computation": "Signal is blocked or passed depending on a gating variable controlled by context, familiarity, or expertise",
        "formal": "output = gate(context) × signal; gate ∈ [0, 1]",
        "key_refs": "Sherman & Guillery (2006); O'Reilly & Frank (2006); Hochreiter & Schmidhuber (1997)",
        "neural_basis": "Thalamic relay nuclei (thalamocortical gating); basal ganglia → thalamus → PFC (working memory gating)",
        "causal_status": "Thalamic gating is well-established neurally. Extension to affective memory gating and expertise-gated aesthetics draws on analogy rather than direct circuit-level evidence",
    },
    "CONVERGENT_STATE_MONITORING": {
        "name": "Convergent State Monitoring",
        "computation": "Distributed signals from multiple sources converge to produce a unified assessment of a global state (fluency, coherence, safety, vitality)",
        "formal": "state = f(Σ_i w_i × signal_i); alert if |state - expected| > threshold",
        "key_refs": "Reber et al. (2004); Barrett & Simmons (2015); Damasio (1994)",
        "neural_basis": "Insula (interoception), ACC (conflict/error), OFC (value integration); diffuse neuromodulatory systems",
        "causal_status": "The individual signals are well-documented. Whether they truly 'converge' into a single monitoring state is debated — Barrett (2017) argues against discrete monitoring circuits. This archetype may be better understood as a functional description than a neural architecture",
    },
}


@dataclass
class CircuitQACard:
    """Structured QA response for a functional circuit query.

    This is the pedagogical unit — what the system presents when someone
    asks about a circuit. It must always include epistemic framing.
    """
    circuit_id: str
    circuit_name: str

    # Epistemic framing (ALWAYS shown)
    epistemic_status: str               # STRONG / MODERATE / HYPOTHETICAL
    ontological_statement: str           # What kind of thing is this?
    causal_status: str                   # Is it causal? How?

    # Content
    what_it_does: str                    # 2-3 sentence description
    archetype: str                       # Which T2 archetype
    archetype_description: str           # What the archetype means
    inputs: List[str]
    outputs: List[str]
    components: List[Dict[str, str]]     # name, description, evidence_status

    # Context
    participating_theories: List[str]    # Which T1.5 theories use this circuit
    domain: str
    related_circuits: List[str]          # Other circuits sharing archetype or theory

    # Evidence
    key_references: List[str]
    evidence_summary: str
    neural_plausibility: str             # Assessment of neural evidence

    # Pedagogy
    follow_up_questions: List[str]       # Suggested next questions
    competing_accounts: List[str]        # Alternative explanations
    what_we_dont_know: List[str]         # Honest gaps

    # Testability (added 2026-03-04)
    testability: Dict[str, Any] = field(default_factory=dict)
    # Structure: {
    #   "latent_variable_prediction": str,    # What the LV hypothesis predicts
    #   "how_to_test": List[str],             # Accessible descriptions of methods
    #   "data_requirements": str,             # What data you'd need
    #   "search_targets": List[str],          # Article search queries to find evidence
    #   "existing_evidence_status": str,      # What we already know
    # }

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for QA response formatting."""
        return {
            "circuit_id": self.circuit_id,
            "circuit_name": self.circuit_name,
            "epistemic_status": self.epistemic_status,
            "ontological_statement": self.ontological_statement,
            "causal_status": self.causal_status,
            "what_it_does": self.what_it_does,
            "archetype": self.archetype,
            "archetype_description": self.archetype_description,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "components": self.components,
            "participating_theories": self.participating_theories,
            "domain": self.domain,
            "related_circuits": self.related_circuits,
            "key_references": self.key_references,
            "evidence_summary": self.evidence_summary,
            "neural_plausibility": self.neural_plausibility,
            "follow_up_questions": self.follow_up_questions,
            "competing_accounts": self.competing_accounts,
            "what_we_dont_know": self.what_we_dont_know,
            "testability": self.testability,
        }


class CircuitQAService:
    """Service that generates epistemically framed QA cards for functional circuits.

    This is the primary interface between the QA system and the functional
    circuit infrastructure. Every response it produces carries:
    1. A clear statement of what the circuit IS (organizing principle, not neural reality)
    2. The evidence status of each component
    3. Honest acknowledgment of what we don't know
    4. Pedagogically structured follow-up questions

    SUCCESS CONDITIONS:
    SC-CQS-1: Every QA card has non-empty epistemic_status
    SC-CQS-2: Every QA card has non-empty ontological_statement
    SC-CQS-3: Every QA card has ≥2 follow_up_questions
    SC-CQS-4: Every QA card has ≥1 competing_accounts entry
    SC-CQS-5: Every QA card has ≥1 what_we_dont_know entry
    SC-CQS-6: get_circuit_card returns None for unknown circuit IDs
    """

    def __init__(self, molecule_dir: str = "data/molecules"):
        self.molecule_dir = Path(molecule_dir)
        self._circuits: Dict[str, Dict] = {}
        self._load_circuits()

    def _load_circuits(self):
        """Load all functional circuit molecules."""
        if not self.molecule_dir.exists():
            return
        for path in sorted(self.molecule_dir.glob("fc_*.json")):
            try:
                with open(path) as f:
                    data = json.load(f)
                if data.get("molecule_type") == "FUNCTIONAL_CIRCUIT":
                    self._circuits[data["molecule_id"]] = data
            except Exception as e:
                logger.warning(f"Failed to load circuit from {path}: {e}")

    def get_circuit_card(self, circuit_id: str) -> Optional[CircuitQACard]:
        """Build a full QA card for a circuit, with epistemic framing.

        This is the core method. It assembles the circuit data with
        appropriate epistemic cautions, follow-up questions, and
        competing accounts.
        """
        data = self._circuits.get(circuit_id)
        if not data:
            return None

        archetypes = data.get("linked_archetypes", [])
        primary_archetype = archetypes[0] if archetypes else "UNKNOWN"
        arch_info = ARCHETYPE_DESCRIPTIONS.get(primary_archetype, {})

        evidence_level = CIRCUIT_EVIDENCE_LEVELS.get(circuit_id, "HYPOTHETICAL")

        # Build ontological statement based on evidence level
        ontological = self._build_ontological_statement(
            data["name"], primary_archetype, evidence_level
        )

        # Build component list with evidence assessment
        components = []
        for comp in data.get("components", []):
            components.append({
                "name": comp.get("name", ""),
                "description": comp.get("description", ""),
                "template_ids": comp.get("template_ids", []),
                "interaction_type": comp.get("interaction_type", "SYNERGISTIC"),
            })

        # Find related circuits (same archetype)
        related = [
            cid for cid, cdata in self._circuits.items()
            if cid != circuit_id
            and primary_archetype in cdata.get("linked_archetypes", [])
        ]

        # Find participating T1.5 theories
        theories = []
        parent = data.get("parent_t1_5_theory")
        if parent:
            theories.append(parent)
        # Also check domain for theory associations
        domain = data.get("domain", "")

        # Build follow-up questions
        follow_ups = self._build_follow_ups(data, primary_archetype, evidence_level)

        # Build competing accounts
        competing = self._build_competing_accounts(primary_archetype, evidence_level)

        # Build "what we don't know"
        gaps = self._build_knowledge_gaps(data, evidence_level)

        # Build testability section
        testability = self._build_testability_section(data, primary_archetype, evidence_level)

        return CircuitQACard(
            circuit_id=circuit_id,
            circuit_name=data["name"],
            epistemic_status=evidence_level,
            ontological_statement=ontological,
            causal_status=arch_info.get("causal_status", "Causal status not yet assessed"),
            what_it_does=data.get("short_description", ""),
            archetype=primary_archetype,
            archetype_description=arch_info.get("computation", ""),
            inputs=data.get("inputs", []),
            outputs=data.get("outputs", []),
            components=components,
            participating_theories=theories,
            domain=domain,
            related_circuits=related,
            key_references=data.get("key_references", []),
            evidence_summary=self._build_evidence_summary(data, evidence_level),
            neural_plausibility=arch_info.get("neural_basis", "Not assessed"),
            follow_up_questions=follow_ups,
            competing_accounts=competing,
            what_we_dont_know=gaps,
            testability=testability,
        )

    def _build_ontological_statement(self, name: str, archetype: str,
                                      evidence: str) -> str:
        """Generate the ontological framing statement.

        This is the most important piece — it tells the reader what
        kind of thing this circuit IS, epistemically speaking.

        Written in ATLAS voice: concrete first, accessible, honest
        about what we know and don't know. Follows Sagan (honest
        uncertainty), Yong (slow complexity building), and Pinker
        (classic style — show, don't lecture).
        """
        arch_name = ARCHETYPE_DESCRIPTIONS.get(archetype, {}).get("name", archetype)

        if evidence == "STRONG":
            return (
                f"The {name} is a latent variable — a hidden dimension along which "
                f"several brain processes reliably co-vary. When you encounter "
                f"a situation that engages {arch_name.lower()}, these processes "
                f"tend to rise and fall together, like instruments in an orchestra "
                f"playing the same phrase. Multiple labs have recovered this pattern "
                f"independently, and there is some evidence from brain stimulation "
                f"studies that perturbing one component affects the others. "
                f"The circuit does not live at a single address in the brain — "
                f"it is a statistical regularity, not an anatomical structure — "
                f"but the regularity is well-documented and replicable."
            )
        elif evidence == "MODERATE":
            return (
                f"The {name} is a hypothesized latent variable. The individual "
                f"component processes have solid empirical support, and they co-occur "
                f"in the situations you would expect if a {arch_name.lower()} pattern "
                f"were operating. But nobody has yet run the factor analysis that would "
                f"confirm they form a single coherent dimension. Think of it this way: "
                f"we can hear the instruments playing similar phrases, but we have not "
                f"yet confirmed they are reading from the same score. The circuit is "
                f"a well-motivated bet about how these processes hang together — not "
                f"a claim about a dedicated piece of neural hardware."
            )
        else:  # HYPOTHETICAL
            return (
                f"The {name} is a prediction, not a finding. Theory suggests that "
                f"a {arch_name.lower()} pattern should operate in this domain, but "
                f"the evidence is thin. We have not extracted this latent variable "
                f"from data — we have predicted it from computational principles. "
                f"It belongs on the research agenda, not in the textbook. Barrett "
                f"(2017) rightly warns against treating theoretical circuit diagrams "
                f"as if they described actual neural wiring. This one is a target "
                f"for future empirical work."
            )

    def _build_evidence_summary(self, data: Dict, evidence_level: str) -> str:
        """Build a narrative summary of the evidence base."""
        refs = data.get("key_references", [])
        n_refs = len(refs)
        components = data.get("components", [])
        n_components = len(components)

        if evidence_level == "STRONG":
            return (
                f"This circuit is supported by {n_refs} key references across its "
                f"{n_components} components. The constituent T2 templates have been "
                f"independently validated in empirical studies, and the archetype pattern "
                f"has direct neural correlates."
            )
        elif evidence_level == "MODERATE":
            return (
                f"This circuit draws on {n_refs} references. Its {n_components} components "
                f"are individually supported, but the specific interaction pattern "
                f"(how they combine as a circuit) is a theoretical inference. Additional "
                f"studies testing co-activation would strengthen the evidence."
            )
        else:
            return (
                f"This circuit is theoretically motivated, drawing on {n_refs} references. "
                f"The evidence for its {n_components} components is incomplete. The circuit "
                f"represents a research hypothesis about computational structure in this "
                f"domain, and should be tested rather than assumed."
            )

    def _build_follow_ups(self, data: Dict, archetype: str,
                           evidence_level: str) -> List[str]:
        """Generate pedagogically structured follow-up questions."""
        name = data.get("name", "this circuit")
        arch_name = ARCHETYPE_DESCRIPTIONS.get(archetype, {}).get("name", archetype)
        follow_ups = []

        # Always: evidence question
        follow_ups.append(
            f"What empirical evidence supports {name}?"
        )

        # Always: archetype question
        follow_ups.append(
            f"What other circuits use {arch_name}? How are they similar and different?"
        )

        # If moderate/hypothetical: testing question
        if evidence_level in ("MODERATE", "HYPOTHETICAL"):
            follow_ups.append(
                f"How could we test whether {name} is a real computational pattern?"
            )

        # Domain question
        domain = data.get("domain", "")
        if domain:
            follow_ups.append(
                f"What other circuits operate in {domain}?"
            )

        # Neural basis question
        follow_ups.append(
            f"What is the neural plausibility of {name}?"
        )

        # Design implication
        follow_ups.append(
            f"What are the design implications of {name} for architecture?"
        )

        return follow_ups[:5]  # Cap at 5

    def _build_competing_accounts(self, archetype: str,
                                   evidence_level: str) -> List[str]:
        """Identify competing or alternative explanations."""
        competing = []

        # Barrett's constructionist critique applies to all circuits
        competing.append(
            "Barrett (2017) argues against discrete functional circuits, proposing "
            "instead that psychological phenomena emerge from domain-general "
            "population-coded neural activity. On this view, the circuit is a "
            "convenient abstraction, not a neural reality."
        )

        # Archetype-specific competing accounts
        if archetype == "PREDICTIVE_CODING":
            competing.append(
                "Some researchers question whether prediction error is computed "
                "explicitly or is an epiphenomenon of Bayesian inference (Kogo & "
                "Trengove, 2015). The circuit may describe the computation without "
                "revealing the implementation."
            )
        elif archetype == "HOMEOSTATIC_REGULATION":
            competing.append(
                "Sterling (2012) argues that allostasis (predictive regulation) is "
                "more accurate than homeostasis (reactive regulation). The circuit's "
                "setpoint-comparison structure may be too simple for phenomena that "
                "involve anticipatory regulation."
            )
        elif archetype == "CONVERGENT_STATE_MONITORING":
            competing.append(
                "Whether 'fluency' or 'coherence' are monitored as unified states "
                "or emerge from distributed processing without a central monitor is "
                "an open question. The convergent monitoring metaphor may reify what "
                "is actually a distributed process (Cleeremans, 2011)."
            )

        if evidence_level == "HYPOTHETICAL":
            competing.append(
                "Given the speculative nature of this circuit, the null hypothesis — "
                "that no such computational pattern exists in this domain — should be "
                "taken seriously. The pattern may be an artifact of our classification "
                "scheme rather than a feature of cognition."
            )

        return competing

    def _build_knowledge_gaps(self, data: Dict,
                               evidence_level: str) -> List[str]:
        """Honest acknowledgment of what we don't know."""
        gaps = []

        gaps.append(
            "We do not know whether the component processes co-activate "
            "simultaneously (as the circuit metaphor implies) or operate "
            "at different timescales with only indirect interaction."
        )

        if evidence_level != "STRONG":
            gaps.append(
                "The interaction effects between circuit components have not been "
                "directly tested. The circuit structure is inferred from component "
                "co-occurrence and theoretical plausibility, not from interaction studies."
            )

        gaps.append(
            "Individual differences in circuit operation are unknown. The same "
            "architectural feature may activate different circuits depending on "
            "the person's developmental history, cultural background, and current state."
        )

        inputs = data.get("inputs", [])
        if inputs:
            gaps.append(
                f"The input variables ({', '.join(inputs[:3])}) are theoretical "
                f"constructs. Their precise measurement in empirical studies varies "
                f"across labs and paradigms."
            )

        return gaps

    def _build_testability_section(self, data: Dict, archetype: str,
                                    evidence_level: str) -> Dict[str, Any]:
        """Build the testability section — how could we check whether this
        latent variable is real?

        Written in ATLAS voice: accessible, concrete, honest about
        difficulty. For HYPOTHETICAL circuits, generates article search
        targets that the recommendation loop can pick up.
        """
        name = data.get("name", "this circuit")
        arch_name = ARCHETYPE_DESCRIPTIONS.get(archetype, {}).get("name", archetype)
        inputs = data.get("inputs", [])
        domain = data.get("domain", "")

        # --- Latent variable prediction ---
        lv_prediction = (
            f"If {name} is a real latent variable, then the component "
            f"processes should load on a single factor when you measure "
            f"them simultaneously. Concretely: record neural or behavioral "
            f"signatures of each component during a task that should engage "
            f"this circuit, run a factor analysis, and look for a dimension "
            f"that captures their shared variance."
        )

        # --- How to test (accessible descriptions) ---
        how_to_test = []

        # Method 1: Factor extraction (always relevant)
        how_to_test.append(
            f"Measure the component processes simultaneously — for example, "
            f"using fMRI, EEG, or behavioral proxies — during a task that "
            f"should engage {arch_name.lower()}. Apply dimensionality "
            f"reduction (factor analysis, PCA, or GPFA for neural data). "
            f"The circuit predicts a factor that loads preferentially on "
            f"the hypothesized components."
        )

        # Method 2: Cross-paradigm generalization
        how_to_test.append(
            f"Test whether the same factor appears across different "
            f"experimental paradigms. If {name} is real, it should "
            f"show up whether you measure it with one task or another — "
            f"just as IQ emerges across different cognitive tests. "
            f"A factor that only appears in one paradigm is probably "
            f"an artifact of that paradigm."
        )

        # Method 3: Behavioral covariance (more accessible)
        if inputs:
            input_str = ", ".join(inputs[:3])
            how_to_test.append(
                f"A less demanding approach: collect behavioral ratings "
                f"or physiological measures of {input_str} across many "
                f"architectural environments and check whether they "
                f"co-vary as the circuit predicts. This does not require "
                f"neuroimaging — just careful measurement design."
            )

        # Method 4: Intervention (for STRONG circuits)
        if evidence_level == "STRONG":
            how_to_test.append(
                f"The strongest test: perturb one component (e.g., via "
                f"TMS or pharmacological manipulation) and check whether "
                f"the other components change as predicted. If they do, "
                f"the latent variable has causal status, not just "
                f"statistical status."
            )

        # --- Data requirements ---
        if evidence_level == "STRONG":
            data_reqs = (
                f"Multi-method datasets with simultaneous measurement "
                f"of the component processes already exist for some "
                f"components. The gap is in testing co-activation "
                f"patterns specifically."
            )
        elif evidence_level == "MODERATE":
            data_reqs = (
                f"Existing studies measure the components separately. "
                f"What is needed is a study that measures them together "
                f"in the same participants, in the same sessions, during "
                f"tasks designed to engage this specific circuit."
            )
        else:
            data_reqs = (
                f"The component processes have limited empirical coverage. "
                f"Before testing the circuit as a whole, individual "
                f"component evidence needs strengthening. This is a "
                f"two-step research program."
            )

        # --- Article search targets ---
        # These feed into the recommendation loop for evidence acquisition
        search_targets = []

        # Always search for factor analysis / dimensionality reduction
        # applied to the relevant domain
        if domain:
            search_targets.append(
                f"factor analysis {arch_name.lower()} {domain}"
            )
            search_targets.append(
                f"latent variable {domain} neural population"
            )

        # Component co-activation
        components = data.get("components", [])
        if len(components) >= 2:
            comp_names = [c.get("name", "") for c in components[:3] if c.get("name")]
            if comp_names:
                search_targets.append(
                    f"co-activation {' '.join(comp_names[:2])} {domain}"
                )

        # Archetype-specific searches
        archetype_searches = {
            "PREDICTIVE_CODING": [
                "prediction error factor analysis neural",
                "predictive coding latent dimensions fMRI",
            ],
            "HOMEOSTATIC_REGULATION": [
                "homeostatic regulation latent variable physiological",
                "allostatic load factor structure",
            ],
            "ACCUMULATION_TO_BOUND": [
                "drift diffusion model latent states neural",
                "evidence accumulation factor analysis decision",
            ],
            "COMPETITIVE_SELECTION": [
                "divisive normalization population coding attention",
                "biased competition latent dimensions visual cortex",
            ],
            "GATED_PROPAGATION": [
                "thalamocortical gating latent variable",
                "gating mechanisms factor analysis working memory",
            ],
            "CONVERGENT_STATE_MONITORING": [
                "interoceptive inference latent variable insula",
                "convergent monitoring distributed processing fMRI",
            ],
        }
        search_targets.extend(archetype_searches.get(archetype, []))

        # For HYPOTHETICAL, add explicit gap searches
        if evidence_level == "HYPOTHETICAL":
            search_targets.append(f"{name} empirical evidence")
            search_targets.append(
                f"{arch_name.lower()} {domain} experimental validation"
            )

        # --- Existing evidence status ---
        if evidence_level == "STRONG":
            existing = (
                f"Multiple independent labs have documented the component "
                f"processes. Some co-activation evidence exists. The main "
                f"gap is a formal latent variable analysis that confirms "
                f"the factor structure."
            )
        elif evidence_level == "MODERATE":
            existing = (
                f"The components are individually supported, but co-activation "
                f"has not been directly tested. The latent variable is "
                f"plausible but unconfirmed."
            )
        else:
            existing = (
                f"Evidence is sparse. The circuit is a theoretical "
                f"prediction awaiting empirical test. Article search "
                f"targets have been generated to find relevant evidence."
            )

        return {
            "latent_variable_prediction": lv_prediction,
            "how_to_test": how_to_test,
            "data_requirements": data_reqs,
            "search_targets": search_targets,
            "existing_evidence_status": existing,
        }

    # --- QA Integration Methods ---

    def format_circuit_answer(self, question: str) -> Optional[Dict[str, Any]]:
        """Format a QA response for a circuit query.

        This is the entry point from the QA handler. It identifies
        which circuit the user is asking about and builds a full
        epistemically-framed response.

        SUCCESS CONDITIONS:
        SC-FCA-1: Response always has question_type = "functional_circuit"
        SC-FCA-2: Response always has epistemic_status section
        SC-FCA-3: Response always has follow_up_questions
        """
        # Extract circuit reference from question
        circuit_id = self._identify_circuit(question)
        if not circuit_id:
            return None

        card = self.get_circuit_card(circuit_id)
        if not card:
            return None

        # Format into QA response structure
        sections = []

        # Section 1: Epistemic framing (ALWAYS first)
        sections.append({
            "heading": "Epistemic Status",
            "items": [
                f"**Status**: {card.epistemic_status}",
                card.ontological_statement,
            ]
        })

        # Section 2: What it does
        sections.append({
            "heading": f"What {card.circuit_name} Does",
            "items": [
                card.what_it_does,
                f"**Archetype**: {card.archetype} — {card.archetype_description}",
                f"**Inputs**: {', '.join(card.inputs)}",
                f"**Outputs**: {', '.join(card.outputs)}",
            ]
        })

        # Section 3: Components
        comp_items = []
        for comp in card.components:
            comp_items.append(
                f"**{comp['name']}**: {comp.get('description', '')} "
                f"(templates: {', '.join(comp.get('template_ids', []))})"
            )
        if comp_items:
            sections.append({
                "heading": "Components",
                "items": comp_items,
            })

        # Section 4: Causal status
        sections.append({
            "heading": "Causal Status",
            "items": [
                card.causal_status,
                f"**Neural plausibility**: {card.neural_plausibility}",
            ]
        })

        # Section 5: Evidence
        sections.append({
            "heading": "Evidence Base",
            "items": [
                card.evidence_summary,
                f"**Key references**: {'; '.join(card.key_references[:5])}",
            ]
        })

        # Section 6: Competing accounts (epistemic honesty)
        sections.append({
            "heading": "Competing Accounts",
            "items": card.competing_accounts,
        })

        # Section 7: What we don't know
        sections.append({
            "heading": "What We Don't Know",
            "items": card.what_we_dont_know,
        })

        # Section 8: Testability — how would we know if this is real?
        if card.testability:
            test_items = [card.testability.get("latent_variable_prediction", "")]
            test_items.extend(card.testability.get("how_to_test", [])[:2])
            test_items.append(
                f"**Data needed**: {card.testability.get('data_requirements', '')}"
            )
            test_items.append(
                f"**Current status**: {card.testability.get('existing_evidence_status', '')}"
            )
            sections.append({
                "heading": "How Would We Test This?",
                "items": [item for item in test_items if item],
            })

            # If there are search targets, include them as a subsection
            search_targets = card.testability.get("search_targets", [])
            if search_targets:
                sections.append({
                    "heading": "Suggested Article Searches",
                    "items": [f'"{t}"' for t in search_targets[:5]],
                    "meta": {"action": "article_search", "queries": search_targets[:5]},
                })

        # Related circuits
        if card.related_circuits:
            sections.append({
                "heading": "Related Circuits (Same Archetype)",
                "items": [
                    f"{cid}: {self._circuits.get(cid, {}).get('name', cid)}"
                    for cid in card.related_circuits[:5]
                ]
            })

        return {
            "question_type": "functional_circuit",
            "headline": f"{card.circuit_name} ({card.epistemic_status}): {card.what_it_does[:120]}",
            "sections": sections,
            "follow_ups": card.follow_up_questions,
            "epistemic_status": card.epistemic_status,
            "circuit_id": card.circuit_id,
            "archetype": card.archetype,
            "search_targets": card.testability.get("search_targets", []),
        }

    def format_archetype_answer(self, archetype_name: str) -> Optional[Dict[str, Any]]:
        """Format a QA response for an archetype query.

        When someone asks "what uses predictive coding?" we should explain
        the archetype first, then list circuits with evidence levels.
        """
        arch_info = ARCHETYPE_DESCRIPTIONS.get(archetype_name)
        if not arch_info:
            return None

        # Find all circuits using this archetype
        circuits = [
            (cid, cdata) for cid, cdata in self._circuits.items()
            if archetype_name in cdata.get("linked_archetypes", [])
        ]

        sections = []

        # Section 1: What is this archetype?
        sections.append({
            "heading": f"T2 Archetype: {arch_info['name']}",
            "items": [
                f"**Computation**: {arch_info['computation']}",
                f"**Formal**: {arch_info['formal']}",
                f"**Neural basis**: {arch_info['neural_basis']}",
                f"**Key references**: {arch_info['key_refs']}",
            ]
        })

        # Section 2: Causal status of the archetype
        sections.append({
            "heading": "Epistemic Status of This Archetype",
            "items": [
                arch_info["causal_status"],
                (
                    "Note: The archetype describes a computational pattern, not a "
                    "specific neural circuit. The same pattern may be implemented "
                    "differently across domains (Marder & Goaillard, 2006 on degeneracy)."
                ),
            ]
        })

        # Section 3: Circuits using this archetype (with evidence levels)
        circuit_items = []
        for cid, cdata in sorted(circuits, key=lambda x: x[1].get("name", "")):
            evidence = CIRCUIT_EVIDENCE_LEVELS.get(cid, "HYPOTHETICAL")
            circuit_items.append(
                f"**{cdata.get('name', cid)}** [{evidence}]: "
                f"{cdata.get('short_description', '')[:100]}"
            )

        if circuit_items:
            sections.append({
                "heading": f"Circuits Instantiating {arch_info['name']} ({len(circuits)} total)",
                "items": circuit_items,
            })

        # Follow-ups
        follow_ups = [
            f"Tell me more about [specific circuit name]",
            f"Is {arch_info['name']} a universality class?",
            f"What neural evidence supports {arch_info['name']}?",
            f"What are the competing accounts for {arch_info['name']}?",
        ]

        return {
            "question_type": "archetype_guide",
            "headline": (
                f"{arch_info['name']}: {arch_info['computation'][:100]}. "
                f"{len(circuits)} circuits instantiate this pattern."
            ),
            "sections": sections,
            "follow_ups": follow_ups,
            "archetype": archetype_name,
        }

    def _identify_circuit(self, question: str) -> Optional[str]:
        """Identify which circuit a question refers to."""
        q_lower = question.lower()
        for cid, cdata in self._circuits.items():
            name = cdata.get("name", "").lower()
            if name and name in q_lower:
                return cid
            # Also check molecule_id without FC_ prefix
            short_id = cid.lower().replace("fc_", "").replace("_", " ")
            if short_id in q_lower:
                return cid
        return None

    def get_all_circuits_summary(self) -> Dict[str, Any]:
        """Catalog summary of all circuits, organized by archetype."""
        by_archetype: Dict[str, List] = {}
        for cid, cdata in self._circuits.items():
            for arch in cdata.get("linked_archetypes", []):
                by_archetype.setdefault(arch, []).append({
                    "circuit_id": cid,
                    "name": cdata.get("name", cid),
                    "evidence": CIRCUIT_EVIDENCE_LEVELS.get(cid, "HYPOTHETICAL"),
                    "domain": cdata.get("domain", ""),
                })

        return {
            "total_circuits": len(self._circuits),
            "by_archetype": by_archetype,
            "evidence_distribution": {
                "STRONG": sum(1 for v in CIRCUIT_EVIDENCE_LEVELS.values() if v == "STRONG"),
                "MODERATE": sum(1 for v in CIRCUIT_EVIDENCE_LEVELS.values() if v == "MODERATE"),
                "HYPOTHETICAL": sum(1 for v in CIRCUIT_EVIDENCE_LEVELS.values() if v == "HYPOTHETICAL"),
            },
        }

    @property
    def circuit_count(self) -> int:
        return len(self._circuits)
