"""
Article Eater - Theory Registry Bootstrap Data
Sprint TH-1: Theory Data Model & Registry

RESTRUCTURED 2026-02-14 per THEORY_TIER_ARCHITECTURE_V1.0

The original design incorrectly placed domain-specific theories (ART, SRT, Biophilia)
at Tier 1. These are phenomenological descriptions of *what happens*, not mechanistic
accounts of *why* at a level connecting to neural implementation. They are now demoted
to Tier 2 with explicit derivation links to their parent Tier 1 frameworks.

=============================================================================
TIER 1: FRAMEWORK THEORIES (10 total) — Neurally grounded, cross-domain
=============================================================================
1.1 Predictive Processing / Active Inference / Free Energy Principle
1.2 Spatial Navigation and Cognitive Mapping (hippocampal-entorhinal)
1.3 Dual-Process Theory / Implicit vs. Explicit Processing
1.4 Default Mode Network vs. Task-Positive Network Dynamics
1.5 Neuromodulatory Systems and the Neurochemistry of Affect
1.6 Interoception and the Construction of Affect
1.7 Memory Systems: Hippocampal-Cortical Consolidation
1.8 Embodied Cognition and Sensorimotor Contingencies
1.9 Chronobiological Regulation (CB) — added by Panel II
1.10 Multisensory Integration (MSI) — added by Panel III

=============================================================================
TIER 2: DOMAIN-SPECIFIC THEORIES (demoted) — Phenomenological, domain-specific
=============================================================================
2.1 Attention Restoration Theory (ART) — parent: DMN/TPN, PP
2.2 Stress Recovery Theory (SRT) — parent: Neuromodulatory, PP
2.3 Biophilia Hypothesis — parent: PP (evolutionary priors)
2.4 Prospect-Refuge Theory — parent: Neuromodulatory (explore-exploit)
2.5 Environmental Preference / Complexity-Liking (Berlyne) — parent: PP, Neuromodulatory
2.6 Wayfinding Theory (Lynch) — parent: Spatial Navigation
2.7 Fractal Fluency — parent: PP (visual statistics)

=============================================================================
TIER 2b: METHODOLOGICAL — Handled separately in method_registry
=============================================================================

Three criteria for Tier 1 status:
1. Mechanistic specificity — connects to neural implementation
2. Cross-domain generativity — generates predictions across domains
3. Convergent multi-method support — fMRI, EEG, lesion, computational, behavioral
"""

from src.models.theory_models import (
    Theory, TheoryClaim, TheoryAssumption, TheoryBoundary,
    Prediction, Originator, DerivationStep, QuantitativePrediction,
    TheoryLevel, PredictionType, Direction, Magnitude, TestingStatus,
    SupportLevel, ReplicationStatus, Necessity, Testability,
    Generality
)


# =============================================================================
# TIER 1: FRAMEWORK THEORIES — Neurally grounded, cross-domain
# =============================================================================

def create_predictive_processing_framework() -> Theory:
    """
    TIER 1.1: Predictive Processing / Active Inference / Free Energy Principle.

    The brain maintains a hierarchical generative model of its environment and
    minimizes prediction error through perception (updating the model) and action
    (changing the environment to match predictions).

    Neural implementation: Cortical hierarchies with ascending prediction error
    signals and descending prediction signals. Precision modulated by neuromodulatory
    systems. Superficial pyramidal neurons encode prediction errors; deep pyramidal
    neurons encode predictions (Bastos et al., 2012).
    """
    theory_id = "framework:predictive_processing"

    claims = [
        TheoryClaim(
            claim_id=f"{theory_id}:claim:01",
            theory_id=theory_id,
            statement="The brain is fundamentally a prediction machine that constructs hierarchical generative models to minimize prediction error",
            formalization="brain_function = argmin(prediction_error); model = hierarchical_generative_model()",
            necessity=Necessity.CORE,
            testability=Testability.INDIRECTLY_TESTABLE,
        ),
        TheoryClaim(
            claim_id=f"{theory_id}:claim:02",
            theory_id=theory_id,
            statement="Perception is inference: what we perceive is the brain's best prediction about the causes of sensory input",
            formalization="perception = argmax P(cause | sensory_input)",
            necessity=Necessity.CORE,
            testability=Testability.DIRECTLY_TESTABLE,
        ),
        TheoryClaim(
            claim_id=f"{theory_id}:claim:03",
            theory_id=theory_id,
            statement="Chronic high prediction error generates stress and negative affect through metabolic cost and uncertainty",
            formalization="chronic(high_prediction_error) → metabolic_cost + uncertainty → stress + negative_affect",
            necessity=Necessity.CORE,
            testability=Testability.DIRECTLY_TESTABLE,
        ),
        TheoryClaim(
            claim_id=f"{theory_id}:claim:04",
            theory_id=theory_id,
            statement="Environments with learnable structure (moderate complexity) are preferred over chaotic or monotonous environments",
            formalization="preference(env) ∝ learnability(env) = moderate_complexity ∈ Goldilocks_zone",
            necessity=Necessity.AUXILIARY,
            testability=Testability.DIRECTLY_TESTABLE,
        ),
        TheoryClaim(
            claim_id=f"{theory_id}:claim:05",
            theory_id=theory_id,
            statement="Precision weighting modulates the influence of prediction errors, controlled by attention and neuromodulation",
            formalization="effective_PE = precision_weight × raw_PE; precision ← attention + neuromodulation",
            necessity=Necessity.CORE,
            testability=Testability.DIRECTLY_TESTABLE,
        ),
    ]

    assumptions = [
        TheoryAssumption(
            assumption_id=f"{theory_id}:assumption:01",
            theory_id=theory_id,
            statement="The brain implements approximate Bayesian inference through hierarchical message passing",
            dependent_claims=[f"{theory_id}:claim:01", f"{theory_id}:claim:02"],
            violation_consequence="If processing is not Bayesian, prediction error minimization may not be the organizing principle",
        ),
    ]

    boundaries = [
        TheoryBoundary(
            boundary_id=f"{theory_id}:boundary:01",
            theory_id=theory_id,
            condition_description="Extreme novelty can be rewarding despite high prediction error (exploration/epistemic value)",
            mechanism_of_failure="Epistemic value of reducing uncertainty can outweigh prediction error costs",
            confidence_penalty=0.1,
        ),
    ]

    predictions = [
        Prediction(
            prediction_id=f"{theory_id}:pred:001",
            source_theory_id=theory_id,
            statement="Familiar environments should be processed more fluently and feel more positive",
            prediction_type=PredictionType.DERIVED,
            consequent_outcome="positive_affect",
            consequent_direction=Direction.POSITIVE,
            consequent_magnitude=Magnitude.MODERATE,
            testing_status=TestingStatus.WELL_TESTED,
            overall_support=SupportLevel.STRONGLY_SUPPORTED,
            prior_confidence=0.85,
            current_confidence=0.85,
        ),
        Prediction(
            prediction_id=f"{theory_id}:pred:002",
            source_theory_id=theory_id,
            statement="Mid-range complexity (moderate prediction error) should be preferred and engaging",
            prediction_type=PredictionType.DERIVED,
            consequent_outcome="engagement_and_preference",
            consequent_direction=Direction.INVERTED_U,
            consequent_magnitude=Magnitude.MODERATE,
            testing_status=TestingStatus.WELL_TESTED,
            overall_support=SupportLevel.SUPPORTED,
            prior_confidence=0.80,
            current_confidence=0.80,
        ),
        Prediction(
            prediction_id=f"{theory_id}:pred:003",
            source_theory_id=theory_id,
            statement="Natural scenes with 1/f spectral structure should be processed more fluently than artificial scenes",
            prediction_type=PredictionType.DERIVED,
            consequent_outcome="processing_fluency",
            consequent_direction=Direction.POSITIVE,
            consequent_magnitude=Magnitude.MODERATE,
            testing_status=TestingStatus.PARTIALLY_TESTED,
            overall_support=SupportLevel.SUPPORTED,
            prior_confidence=0.75,
            current_confidence=0.75,
        ),
    ]

    return Theory(
        theory_id=theory_id,
        name="Predictive Processing",
        aliases=["PP", "Active Inference", "Predictive Coding", "Free Energy Principle"],
        originators=[
            Originator(name="Karl Friston", year=2010, doi="10.1038/nrn2787"),
            Originator(name="Andy Clark", year=2013),
            Originator(name="Jakob Hohwy", year=2013),
        ],
        year_introduced=2010,
        domain=["perception", "cognition", "affect", "learning", "neuroscience", "architecture"],
        scope_description="General theory of brain function based on hierarchical prediction error minimization; "
                          "provides mechanistic basis for understanding environmental preferences and wellbeing",
        level=TheoryLevel.FRAMEWORK_THEORY,
        core_claims=claims,
        assumptions=assumptions,
        boundary_conditions=boundaries,
        explicit_predictions=[predictions[0]],
        derived_predictions=predictions[1:],
        overall_confidence=0.85,
        confidence_rationale="Widely influential framework with strong neurophysiological support; concerns about unfalsifiability addressed by specific architectural predictions",
        quantitative_precision="medium",
        parent_theories=[],  # Tier 1: no parents
        child_theories=["theory:fractal_fluency", "theory:perceptual_fluency"],
        compatible_theories=["framework:embodied_cognition", "framework:interoception"],
        replication_status=ReplicationStatus.STRONG,
        extraction_source="Friston (2010); Clark (2013); Hohwy (2013)",
        extracted_by="bootstrap_v2_2026-02-14",
    )


def create_spatial_navigation_framework() -> Theory:
    """
    TIER 1.2: Spatial Navigation and Cognitive Mapping.

    The hippocampal-entorhinal system constructs an allocentric cognitive map of
    spatial structure using place cells, grid cells, head direction cells, border
    cells, and speed cells — supporting navigation, planning, memory, and imagination.

    2014 Nobel Prize to O'Keefe and the Mosers. One of the most well-characterized
    neural systems in neuroscience.
    """
    theory_id = "framework:spatial_navigation"

    claims = [
        TheoryClaim(
            claim_id=f"{theory_id}:claim:01",
            theory_id=theory_id,
            statement="The hippocampal-entorhinal system constructs allocentric cognitive maps using specialized cell types",
            formalization="hippocampus(place_cells) + entorhinal(grid_cells) → cognitive_map(allocentric)",
            necessity=Necessity.CORE,
            testability=Testability.DIRECTLY_TESTABLE,
        ),
        TheoryClaim(
            claim_id=f"{theory_id}:claim:02",
            theory_id=theory_id,
            statement="Architecture's legibility, complexity, and structure directly affect cognitive map quality and stability",
            formalization="spatial_legibility(building) → map_coherence(hippocampus) → navigation_ease",
            necessity=Necessity.CORE,
            testability=Testability.DIRECTLY_TESTABLE,
        ),
        TheoryClaim(
            claim_id=f"{theory_id}:claim:03",
            theory_id=theory_id,
            statement="Buildings hard to navigate produce unstable cognitive maps leading to measurable stress increases",
            formalization="poor_legibility → unstable_map → ↑cortisol + ↑hippocampal_theta",
            necessity=Necessity.CORE,
            testability=Testability.DIRECTLY_TESTABLE,
        ),
    ]

    predictions = [
        Prediction(
            prediction_id=f"{theory_id}:pred:001",
            source_theory_id=theory_id,
            statement="Buildings with clear spatial hierarchies should produce more coherent hippocampal representations and lower stress",
            prediction_type=PredictionType.DERIVED,
            consequent_outcome="stress_markers",
            consequent_direction=Direction.NEGATIVE,
            consequent_magnitude=Magnitude.MODERATE,
            testing_status=TestingStatus.PARTIALLY_TESTED,
            overall_support=SupportLevel.SUPPORTED,
            prior_confidence=0.80,
            current_confidence=0.75,
        ),
        Prediction(
            prediction_id=f"{theory_id}:pred:002",
            source_theory_id=theory_id,
            statement="Landmarks at decision points should stabilize cognitive maps and improve wayfinding",
            prediction_type=PredictionType.DERIVED,
            consequent_outcome="wayfinding_performance",
            consequent_direction=Direction.POSITIVE,
            consequent_magnitude=Magnitude.MODERATE,
            testing_status=TestingStatus.WELL_TESTED,
            overall_support=SupportLevel.STRONGLY_SUPPORTED,
            prior_confidence=0.85,
            current_confidence=0.85,
        ),
    ]

    return Theory(
        theory_id=theory_id,
        name="Spatial Navigation and Cognitive Mapping",
        aliases=["Cognitive Mapping", "Hippocampal Spatial System", "Place Cell Theory"],
        originators=[
            Originator(name="John O'Keefe", year=1971, doi="10.1016/0006-8993(71)90358-1"),
            Originator(name="Lynn Nadel", year=1978),
            Originator(name="Edvard Moser", year=2005),
            Originator(name="May-Britt Moser", year=2005),
        ],
        year_introduced=1971,
        domain=["navigation", "spatial_cognition", "memory", "architecture", "wayfinding"],
        scope_description="The hippocampal-entorhinal system as the primary neural substrate for experiencing "
                          "and representing architectural space",
        level=TheoryLevel.FRAMEWORK_THEORY,
        core_claims=claims,
        explicit_predictions=[predictions[0]],
        derived_predictions=predictions[1:],
        overall_confidence=0.90,
        confidence_rationale="2014 Nobel Prize; one of most well-characterized neural systems; direct relevance to architecture",
        quantitative_precision="high",
        parent_theories=[],
        child_theories=["theory:wayfinding"],
        compatible_theories=["framework:predictive_processing", "framework:embodied_cognition"],
        replication_status=ReplicationStatus.STRONG,
        extraction_source="O'Keefe & Nadel (1978); Moser et al. (2008); Behrens et al. (2018)",
        extracted_by="bootstrap_v2_2026-02-14",
    )


def create_dual_process_framework() -> Theory:
    """
    TIER 1.3: Dual-Process Theory / Implicit vs. Explicit Processing.

    Fast, automatic, implicit processing (System 1 / Type 1) and slow, deliberate,
    explicit processing (System 2 / Type 2) operate through different neural systems
    and interact constantly.
    """
    theory_id = "framework:dual_process"

    claims = [
        TheoryClaim(
            claim_id=f"{theory_id}:claim:01",
            theory_id=theory_id,
            statement="Implicit processing relies on subcortical circuits (amygdala, basal ganglia) and sensory cortices; explicit processing recruits prefrontal cortex",
            formalization="implicit → subcortical + sensory_cortex; explicit → PFC + working_memory",
            necessity=Necessity.CORE,
            testability=Testability.DIRECTLY_TESTABLE,
        ),
        TheoryClaim(
            claim_id=f"{theory_id}:claim:02",
            theory_id=theory_id,
            statement="Most environmental experience is processed implicitly — first affective response within hundreds of milliseconds",
            formalization="architectural_encounter → implicit_evaluation(<500ms) → explicit_override(optional)",
            necessity=Necessity.CORE,
            testability=Testability.DIRECTLY_TESTABLE,
        ),
        TheoryClaim(
            claim_id=f"{theory_id}:claim:03",
            theory_id=theory_id,
            statement="Discrepancy between implicit and explicit responses is meaningful — conflict between systems",
            formalization="self_report ≠ physiology → implicit_explicit_conflict",
            necessity=Necessity.AUXILIARY,
            testability=Testability.DIRECTLY_TESTABLE,
        ),
    ]

    predictions = [
        Prediction(
            prediction_id=f"{theory_id}:pred:001",
            source_theory_id=theory_id,
            statement="Physiological measures (cortisol, HRV) should detect environmental effects missed by self-report",
            prediction_type=PredictionType.DERIVED,
            consequent_outcome="implicit_explicit_dissociation",
            consequent_direction=Direction.POSITIVE,
            consequent_magnitude=Magnitude.MODERATE,
            testing_status=TestingStatus.WELL_TESTED,
            overall_support=SupportLevel.STRONGLY_SUPPORTED,
            prior_confidence=0.85,
            current_confidence=0.85,
        ),
    ]

    return Theory(
        theory_id=theory_id,
        name="Dual-Process Theory",
        aliases=["System 1/System 2", "Implicit vs Explicit Processing", "Type 1/Type 2 Processing"],
        originators=[
            Originator(name="Daniel Kahneman", year=2011),
            Originator(name="Keith Stanovich", year=2013),
            Originator(name="Jonathan Evans", year=2013),
        ],
        year_introduced=2011,
        domain=["cognition", "decision_making", "affect", "measurement"],
        scope_description="Explains how environmental effects operate primarily through implicit channels, "
                          "requiring both physiological and self-report measurement",
        level=TheoryLevel.FRAMEWORK_THEORY,
        core_claims=claims,
        derived_predictions=predictions,
        overall_confidence=0.90,
        confidence_rationale="Kahneman (2011) cited ~60,000 times; explains implicit-explicit dissociations in environmental research",
        quantitative_precision="medium",
        parent_theories=[],
        compatible_theories=["framework:interoception", "framework:neuromodulatory"],
        replication_status=ReplicationStatus.STRONG,
        extraction_source="Kahneman (2011); Evans & Stanovich (2013)",
        extracted_by="bootstrap_v2_2026-02-14",
    )


def create_dmn_tpn_framework() -> Theory:
    """
    TIER 1.4: Default Mode Network vs. Task-Positive Network Dynamics.

    The DMN (midline and lateral parietal regions) is anti-correlated with task-positive
    networks. The balance between them is critical for wellbeing, creativity, and
    cognitive restoration. DMN suppression = "directed attention fatigue."
    """
    theory_id = "framework:dmn_tpn"

    claims = [
        TheoryClaim(
            claim_id=f"{theory_id}:claim:01",
            theory_id=theory_id,
            statement="DMN and TPN are anti-correlated; sustained TPN engagement suppresses DMN",
            formalization="TPN_engagement → DMN_suppression; DMN_engagement → TPN_suppression",
            necessity=Necessity.CORE,
            testability=Testability.DIRECTLY_TESTABLE,
        ),
        TheoryClaim(
            claim_id=f"{theory_id}:claim:02",
            theory_id=theory_id,
            statement="Chronic DMN suppression is associated with increased cortisol and reduced immune function",
            formalization="chronic(DMN_suppression) → ↑cortisol + ↓immune_function",
            necessity=Necessity.CORE,
            testability=Testability.DIRECTLY_TESTABLE,
        ),
        TheoryClaim(
            claim_id=f"{theory_id}:claim:03",
            theory_id=theory_id,
            statement="DMN can be understood as the generative model in maintenance mode — running simulations, consolidating predictions",
            formalization="DMN_active → model_maintenance(simulation + consolidation + update)",
            necessity=Necessity.AUXILIARY,
            testability=Testability.INDIRECTLY_TESTABLE,
        ),
    ]

    predictions = [
        Prediction(
            prediction_id=f"{theory_id}:pred:001",
            source_theory_id=theory_id,
            statement="Environments demanding sustained attention (complex navigation, threat monitoring) should suppress DMN and produce fatigue",
            prediction_type=PredictionType.DERIVED,
            consequent_outcome="directed_attention_fatigue",
            consequent_direction=Direction.POSITIVE,
            consequent_magnitude=Magnitude.MODERATE,
            testing_status=TestingStatus.PARTIALLY_TESTED,
            overall_support=SupportLevel.SUPPORTED,
            prior_confidence=0.80,
            current_confidence=0.75,
        ),
        Prediction(
            prediction_id=f"{theory_id}:pred:002",
            source_theory_id=theory_id,
            statement="Restful, safe, familiar environments should allow DMN engagement and support restoration",
            prediction_type=PredictionType.DERIVED,
            consequent_outcome="cognitive_restoration",
            consequent_direction=Direction.POSITIVE,
            consequent_magnitude=Magnitude.MODERATE,
            testing_status=TestingStatus.PARTIALLY_TESTED,
            overall_support=SupportLevel.SUPPORTED,
            prior_confidence=0.80,
            current_confidence=0.80,
        ),
    ]

    return Theory(
        theory_id=theory_id,
        name="Default Mode Network Dynamics",
        aliases=["DMN/TPN", "Default Mode Network", "Task-Positive Network Dynamics"],
        originators=[
            Originator(name="Marcus Raichle", year=2001, doi="10.1073/pnas.98.2.676"),
            Originator(name="Michael Fox", year=2005),
            Originator(name="Randy Buckner", year=2008),
        ],
        year_introduced=2001,
        domain=["neuroscience", "attention", "restoration", "wellbeing", "creativity"],
        scope_description="Explains mechanistically what ART describes phenomenologically as 'directed attention fatigue' "
                          "and 'soft fascination' through DMN/TPN balance",
        level=TheoryLevel.FRAMEWORK_THEORY,
        core_claims=claims,
        derived_predictions=predictions,
        overall_confidence=0.85,
        confidence_rationale="Raichle (2001) cited ~15,000; provides neural mechanism for ART phenomena",
        quantitative_precision="high",
        parent_theories=[],
        child_theories=["theory:attention_restoration"],  # ART is explained BY this
        compatible_theories=["framework:predictive_processing", "framework:neuromodulatory"],
        replication_status=ReplicationStatus.STRONG,
        extraction_source="Raichle et al. (2001); Fox et al. (2005); Buckner et al. (2008)",
        extracted_by="bootstrap_v2_2026-02-14",
    )


def create_neuromodulatory_framework() -> Theory:
    """
    TIER 1.5: Neuromodulatory Systems and the Neurochemistry of Affect.

    The brain's major neuromodulatory systems — dopamine, serotonin, norepinephrine,
    acetylcholine, cortisol/HPA axis, oxytocin, endogenous opioids — modulate cognition,
    affect, and behavior through well-characterized anatomy and pharmacology.

    This subsumes the old "Allostatic Load Model" which focused only on HPA/cortisol.
    """
    theory_id = "framework:neuromodulatory"

    claims = [
        TheoryClaim(
            claim_id=f"{theory_id}:claim:01",
            theory_id=theory_id,
            statement="Dopamine encodes reward prediction error; architectural novelty and beauty modulate dopaminergic signaling",
            formalization="reward_PE = actual_reward - predicted_reward → dopamine_release",
            necessity=Necessity.CORE,
            testability=Testability.DIRECTLY_TESTABLE,
        ),
        TheoryClaim(
            claim_id=f"{theory_id}:claim:02",
            theory_id=theory_id,
            statement="Locus coeruleus-norepinephrine system modulates gain of neural processing and explore-exploit tradeoff",
            formalization="LC_NE → precision_modulation + explore_exploit_balance",
            necessity=Necessity.CORE,
            testability=Testability.DIRECTLY_TESTABLE,
        ),
        TheoryClaim(
            claim_id=f"{theory_id}:claim:03",
            theory_id=theory_id,
            statement="HPA axis chronic activation produces allostatic load with downstream effects on hippocampus and immune function",
            formalization="chronic(HPA_activation) → allostatic_load → ↓hippocampal_neurogenesis + ↓immune_function",
            necessity=Necessity.CORE,
            testability=Testability.DIRECTLY_TESTABLE,
        ),
        TheoryClaim(
            claim_id=f"{theory_id}:claim:04",
            theory_id=theory_id,
            statement="Moderate noradrenergic tone = optimal function; extremes produce drowsiness or anxiety",
            formalization="optimal_function ← moderate(NE_tone) ∈ Goldilocks_zone",
            necessity=Necessity.CORE,
            testability=Testability.DIRECTLY_TESTABLE,
        ),
    ]

    predictions = [
        Prediction(
            prediction_id=f"{theory_id}:pred:001",
            source_theory_id=theory_id,
            statement="Chronic environmental stressors should produce cumulative health effects through allostatic load",
            prediction_type=PredictionType.EXPLICIT,
            antecedent_temporal={"exposure_type": "chronic", "duration": "months_to_years"},
            consequent_outcome="health_markers",
            consequent_direction=Direction.NEGATIVE,
            consequent_magnitude=Magnitude.MODERATE,
            testing_status=TestingStatus.WELL_TESTED,
            overall_support=SupportLevel.STRONGLY_SUPPORTED,
            prior_confidence=0.85,
            current_confidence=0.85,
        ),
        Prediction(
            prediction_id=f"{theory_id}:pred:002",
            source_theory_id=theory_id,
            statement="Alarming or uncertain environments should shift from exploitation to exploration via LC-NE",
            prediction_type=PredictionType.DERIVED,
            consequent_outcome="explore_exploit_balance",
            consequent_direction=Direction.POSITIVE,
            consequent_magnitude=Magnitude.MODERATE,
            testing_status=TestingStatus.PARTIALLY_TESTED,
            overall_support=SupportLevel.SUPPORTED,
            prior_confidence=0.80,
            current_confidence=0.75,
        ),
    ]

    return Theory(
        theory_id=theory_id,
        name="Neuromodulatory Systems",
        aliases=["Neurochemistry of Affect", "Neuromodulation", "Allostatic Load Framework"],
        originators=[
            Originator(name="Wolfram Schultz", year=1997),
            Originator(name="Gary Aston-Jones", year=2005),
            Originator(name="Bruce McEwen", year=2007),
            Originator(name="Angela Yu", year=2005),
        ],
        year_introduced=1997,
        domain=["neuroscience", "affect", "stress", "reward", "arousal"],
        scope_description="Explains how environmental features modulate cognition and affect through "
                          "dopamine, norepinephrine, cortisol, acetylcholine, and serotonin systems",
        level=TheoryLevel.FRAMEWORK_THEORY,
        core_claims=claims,
        explicit_predictions=[predictions[0]],
        derived_predictions=predictions[1:],
        overall_confidence=0.90,
        confidence_rationale="Schultz (1997) cited ~12,000; McEwen (2007) cited ~5,500; well-characterized pharmacology",
        quantitative_precision="high",
        parent_theories=[],
        child_theories=["theory:stress_recovery", "theory:prospect_refuge"],
        compatible_theories=["framework:predictive_processing", "framework:interoception"],
        replication_status=ReplicationStatus.STRONG,
        extraction_source="Schultz et al. (1997); Aston-Jones & Cohen (2005); McEwen (2007)",
        extracted_by="bootstrap_v2_2026-02-14",
    )


def create_interoception_framework() -> Theory:
    """
    TIER 1.6: Interoception and the Construction of Affect.

    Affective experience is *constructed* through integration of interoceptive signals
    (from the body), exteroceptive signals (from the environment), and prior beliefs.
    Interoceptive prediction error drives affective experience.
    """
    theory_id = "framework:interoception"

    claims = [
        TheoryClaim(
            claim_id=f"{theory_id}:claim:01",
            theory_id=theory_id,
            statement="Affective experience is constructed through integration of interoceptive signals, exteroceptive signals, and prior beliefs",
            formalization="affect = construct(interoception, exteroception, priors)",
            necessity=Necessity.CORE,
            testability=Testability.DIRECTLY_TESTABLE,
        ),
        TheoryClaim(
            claim_id=f"{theory_id}:claim:02",
            theory_id=theory_id,
            statement="Interoceptive prediction error — mismatch between predicted and actual body state — is a primary driver of affect",
            formalization="interoceptive_PE = predicted_body_state - actual_body_state → affective_valence",
            necessity=Necessity.CORE,
            testability=Testability.DIRECTLY_TESTABLE,
        ),
        TheoryClaim(
            claim_id=f"{theory_id}:claim:03",
            theory_id=theory_id,
            statement="Architecture modulates bodily state; the brain constructs affect by integrating these changes with predictions",
            formalization="architecture → body_state_change → interoceptive_PE → constructed_affect",
            necessity=Necessity.CORE,
            testability=Testability.DIRECTLY_TESTABLE,
        ),
    ]

    predictions = [
        Prediction(
            prediction_id=f"{theory_id}:pred:001",
            source_theory_id=theory_id,
            statement="Same environment should produce different affective experiences in people with different interoceptive sensitivity",
            prediction_type=PredictionType.DERIVED,
            consequent_outcome="individual_differences_in_affect",
            consequent_direction=Direction.POSITIVE,
            consequent_magnitude=Magnitude.MODERATE,
            testing_status=TestingStatus.PARTIALLY_TESTED,
            overall_support=SupportLevel.SUPPORTED,
            prior_confidence=0.80,
            current_confidence=0.75,
        ),
        Prediction(
            prediction_id=f"{theory_id}:pred:002",
            source_theory_id=theory_id,
            statement="Individuals with interoceptive insensitivity (alexithymia) should show reduced environmental affect effects",
            prediction_type=PredictionType.DERIVED,
            consequent_outcome="environmental_affect_sensitivity",
            consequent_direction=Direction.NEGATIVE,
            consequent_magnitude=Magnitude.MODERATE,
            testing_status=TestingStatus.UNTESTED,
            overall_support=SupportLevel.UNTESTED,
            prior_confidence=0.70,
            current_confidence=0.70,
        ),
    ]

    return Theory(
        theory_id=theory_id,
        name="Interoception and Constructed Affect",
        aliases=["Constructed Emotion", "Interoceptive Inference", "Predictive Interoception"],
        originators=[
            Originator(name="Lisa Feldman Barrett", year=2017),
            Originator(name="Anil Seth", year=2013),
            Originator(name="Bud Craig", year=2009),
        ],
        year_introduced=2013,
        domain=["affect", "emotion", "interoception", "individual_differences"],
        scope_description="Explains how environmental features get translated into subjective feelings "
                          "through interoceptive prediction error",
        level=TheoryLevel.FRAMEWORK_THEORY,
        core_claims=claims,
        derived_predictions=predictions,
        overall_confidence=0.80,
        confidence_rationale="Barrett (2017) cited ~4,000; Craig (2009) cited ~6,000; explains cultural and individual variation",
        quantitative_precision="medium",
        parent_theories=[],
        compatible_theories=["framework:predictive_processing", "framework:neuromodulatory"],
        replication_status=ReplicationStatus.MODERATE,
        extraction_source="Barrett (2017); Seth (2013); Craig (2009)",
        extracted_by="bootstrap_v2_2026-02-14",
    )


def create_memory_systems_framework() -> Theory:
    """
    TIER 1.7: Memory Systems: Hippocampal-Cortical Consolidation.

    Rapid hippocampal encoding interacts with slow cortical learning to produce
    episodic and semantic memory. Semantic knowledge constitutes the generative
    model's priors — the predictions brought to any architectural encounter.
    """
    theory_id = "framework:memory_systems"

    claims = [
        TheoryClaim(
            claim_id=f"{theory_id}:claim:01",
            theory_id=theory_id,
            statement="Rapid hippocampal encoding of episodes interacts with slow cortical learning of regularities",
            formalization="hippocampus(rapid_episodic) + cortex(slow_statistical) → memory_consolidation",
            necessity=Necessity.CORE,
            testability=Testability.DIRECTLY_TESTABLE,
        ),
        TheoryClaim(
            claim_id=f"{theory_id}:claim:02",
            theory_id=theory_id,
            statement="Semantic architectural knowledge constitutes the generative model's priors for new encounters",
            formalization="semantic_architecture_knowledge = generative_model_priors → predictions(new_building)",
            necessity=Necessity.CORE,
            testability=Testability.INDIRECTLY_TESTABLE,
        ),
        TheoryClaim(
            claim_id=f"{theory_id}:claim:03",
            theory_id=theory_id,
            statement="Cultural variation in architectural experience reflects different semantic architectural knowledge (different priors)",
            formalization="cultural_variation → different_semantic_priors → different_predictions → different_responses",
            necessity=Necessity.AUXILIARY,
            testability=Testability.DIRECTLY_TESTABLE,
        ),
    ]

    predictions = [
        Prediction(
            prediction_id=f"{theory_id}:pred:001",
            source_theory_id=theory_id,
            statement="First impressions of buildings should persist strongly due to rapid hippocampal encoding",
            prediction_type=PredictionType.DERIVED,
            consequent_outcome="first_impression_persistence",
            consequent_direction=Direction.POSITIVE,
            consequent_magnitude=Magnitude.MODERATE,
            testing_status=TestingStatus.PARTIALLY_TESTED,
            overall_support=SupportLevel.SUPPORTED,
            prior_confidence=0.75,
            current_confidence=0.75,
        ),
    ]

    return Theory(
        theory_id=theory_id,
        name="Memory Systems",
        aliases=["Hippocampal-Cortical Consolidation", "Complementary Learning Systems"],
        originators=[
            Originator(name="James McClelland", year=1995),
            Originator(name="Bruce McNaughton", year=1995),
            Originator(name="Susanne Diekelmann", year=2010),
        ],
        year_introduced=1995,
        domain=["memory", "learning", "culture", "individual_differences"],
        scope_description="Explains how architectural experience involves both episodic memory and semantic "
                          "architectural knowledge that shapes predictions",
        level=TheoryLevel.FRAMEWORK_THEORY,
        core_claims=claims,
        derived_predictions=predictions,
        overall_confidence=0.85,
        confidence_rationale="McClelland et al. (1995) cited ~5,000; well-established computational theory",
        quantitative_precision="medium",
        parent_theories=[],
        compatible_theories=["framework:predictive_processing", "framework:spatial_navigation"],
        replication_status=ReplicationStatus.STRONG,
        extraction_source="McClelland et al. (1995); Diekelmann & Born (2010)",
        extracted_by="bootstrap_v2_2026-02-14",
    )


def create_embodied_cognition_framework() -> Theory:
    """
    TIER 1.8: Embodied Cognition and Sensorimotor Contingencies.

    Cognition is constitutively shaped by the body's morphology, sensorimotor capacities,
    and interaction with the environment. Includes Gibson's affordances but extends to
    the broader claim that spatial, social, and abstract cognition are grounded in
    sensorimotor experience.
    """
    theory_id = "framework:embodied_cognition"

    claims = [
        TheoryClaim(
            claim_id=f"{theory_id}:claim:01",
            theory_id=theory_id,
            statement="Cognition is shaped by the body's morphology, sensorimotor capacities, and environmental interaction",
            formalization="cognition ← body_morphology + sensorimotor_capacity + environment_interaction",
            necessity=Necessity.CORE,
            testability=Testability.DIRECTLY_TESTABLE,
        ),
        TheoryClaim(
            claim_id=f"{theory_id}:claim:02",
            theory_id=theory_id,
            statement="Architectural affordances are perceived properties specifying possibilities for action",
            formalization="affordance(feature) = action_possibility(agent, environment)",
            necessity=Necessity.CORE,
            testability=Testability.DIRECTLY_TESTABLE,
        ),
        TheoryClaim(
            claim_id=f"{theory_id}:claim:03",
            theory_id=theory_id,
            statement="Body's engagement with affordances is a primary channel through which buildings affect cognition and affect",
            formalization="body_affordance_engagement → cognition_affect_modulation",
            necessity=Necessity.CORE,
            testability=Testability.DIRECTLY_TESTABLE,
        ),
    ]

    predictions = [
        Prediction(
            prediction_id=f"{theory_id}:pred:001",
            source_theory_id=theory_id,
            statement="Posture and locomotion should affect cognitive processing in architectural spaces",
            prediction_type=PredictionType.DERIVED,
            consequent_outcome="posture_cognition_interaction",
            consequent_direction=Direction.POSITIVE,
            consequent_magnitude=Magnitude.MODERATE,
            testing_status=TestingStatus.PARTIALLY_TESTED,
            overall_support=SupportLevel.SUPPORTED,
            prior_confidence=0.75,
            current_confidence=0.75,
        ),
        Prediction(
            prediction_id=f"{theory_id}:pred:002",
            source_theory_id=theory_id,
            statement="Ceiling height effects should be mediated by postural responses and perceived affordances",
            prediction_type=PredictionType.DERIVED,
            consequent_outcome="ceiling_height_mediation",
            consequent_direction=Direction.POSITIVE,
            consequent_magnitude=Magnitude.MODERATE,
            testing_status=TestingStatus.PARTIALLY_TESTED,
            overall_support=SupportLevel.SUPPORTED,
            prior_confidence=0.70,
            current_confidence=0.70,
        ),
    ]

    return Theory(
        theory_id=theory_id,
        name="Embodied Cognition",
        aliases=["Sensorimotor Contingencies", "Ecological Psychology", "Affordance Theory"],
        originators=[
            Originator(name="James Gibson", year=1979),
            Originator(name="Francisco Varela", year=1991),
            Originator(name="Evan Thompson", year=1991),
            Originator(name="Kevin O'Regan", year=2001),
            Originator(name="Alva Noë", year=2001),
        ],
        year_introduced=1979,
        domain=["perception", "action", "affordances", "architecture", "design"],
        scope_description="Architectural experience is inescapably embodied — movement through buildings, "
                          "postural responses, engagement with affordances",
        level=TheoryLevel.FRAMEWORK_THEORY,
        core_claims=claims,
        derived_predictions=predictions,
        overall_confidence=0.85,
        confidence_rationale="Gibson (1979) cited ~35,000; Varela et al. (1991) cited ~15,000; foundational for architecture",
        quantitative_precision="low",
        parent_theories=[],
        compatible_theories=["framework:predictive_processing", "framework:spatial_navigation"],
        replication_status=ReplicationStatus.STRONG,
        extraction_source="Gibson (1979); Varela et al. (1991); O'Regan & Noë (2001)",
        extracted_by="bootstrap_v2_2026-02-14",
    )


def create_chronobiological_framework() -> Theory:
    """
    TIER 1.9: Chronobiological Regulation (CB).

    Added per Panel II (docs/02-15_02_Neuroscience_Panel_Templates_and_Taxonomy_V1.0.md).
    The circadian system, anchored by the suprachiasmatic nucleus (SCN), regulates
    sleep-wake cycles, hormone rhythms, immune function, and cognitive performance
    timing — all heavily influenced by light exposure in buildings.

    Neural implementation: SCN receives direct retinal input via melanopsin-expressing
    ipRGCs. SCN synchronizes peripheral oscillators in every organ. Light spectrum,
    intensity, timing, and duration all affect circadian entrainment.
    """
    theory_id = "framework:chronobiological_regulation"

    claims = [
        TheoryClaim(
            claim_id=f"{theory_id}:claim:01",
            theory_id=theory_id,
            statement="The suprachiasmatic nucleus (SCN) is the master circadian pacemaker, synchronized by light input via melanopsin ipRGCs",
            formalization="light → ipRGCs → SCN → systemic_circadian_entrainment",
            necessity=Necessity.CORE,
            testability=Testability.DIRECTLY_TESTABLE,
        ),
        TheoryClaim(
            claim_id=f"{theory_id}:claim:02",
            theory_id=theory_id,
            statement="Circadian disruption impairs sleep, cognitive performance, mood, immune function, and metabolic regulation",
            formalization="circadian_misalignment → sleep_disruption + cognitive_impairment + mood_dysregulation",
            necessity=Necessity.CORE,
            testability=Testability.DIRECTLY_TESTABLE,
        ),
        TheoryClaim(
            claim_id=f"{theory_id}:claim:03",
            theory_id=theory_id,
            statement="Architectural lighting (spectrum, intensity, timing) directly affects circadian entrainment quality",
            formalization="lighting(spectrum, intensity, timing) → SCN_entrainment_quality",
            necessity=Necessity.CORE,
            testability=Testability.DIRECTLY_TESTABLE,
        ),
    ]

    predictions = [
        Prediction(
            prediction_id=f"{theory_id}:pred:001",
            source_theory_id=theory_id,
            statement="Blue-enriched morning light exposure should improve circadian alignment and daytime alertness",
            prediction_type=PredictionType.DERIVED,
            consequent_outcome="circadian_alignment",
            consequent_direction=Direction.POSITIVE,
            consequent_magnitude=Magnitude.MODERATE,
            testing_status=TestingStatus.WELL_TESTED,
            overall_support=SupportLevel.STRONGLY_SUPPORTED,
            prior_confidence=0.85,
            current_confidence=0.85,
        ),
        Prediction(
            prediction_id=f"{theory_id}:pred:002",
            source_theory_id=theory_id,
            statement="Evening light exposure should delay circadian phase and impair sleep onset",
            prediction_type=PredictionType.DERIVED,
            consequent_outcome="sleep_onset_delay",
            consequent_direction=Direction.NEGATIVE,
            consequent_magnitude=Magnitude.MODERATE,
            testing_status=TestingStatus.WELL_TESTED,
            overall_support=SupportLevel.STRONGLY_SUPPORTED,
            prior_confidence=0.85,
            current_confidence=0.85,
        ),
    ]

    return Theory(
        theory_id=theory_id,
        name="Chronobiological Regulation",
        aliases=["CB", "Circadian Biology", "Circadian Neuroscience"],
        originators=[
            Originator(name="Jeffrey Hall", year=2017, doi="10.1038/nature24558"),
            Originator(name="Michael Rosbash", year=2017),
            Originator(name="Michael Young", year=2017),
            Originator(name="Russell Foster", year=2011),
        ],
        year_introduced=1972,
        domain=["circadian", "sleep", "light", "architecture", "health"],
        scope_description="Circadian timing affects nearly every aspect of human physiology and psychology; "
                          "architectural lighting is a primary environmental synchronizer",
        level=TheoryLevel.FRAMEWORK_THEORY,
        core_claims=claims,
        derived_predictions=predictions,
        overall_confidence=0.90,
        confidence_rationale="2017 Nobel Prize to Hall/Rosbash/Young; extremely well-characterized molecular mechanisms",
        quantitative_precision="high",
        parent_theories=[],  # Tier 1: no parents
        compatible_theories=["framework:neuromodulatory", "framework:interoception"],
        replication_status=ReplicationStatus.STRONG,
        extraction_source="Hall et al. (2017); Foster & Kreitzman (2011)",
        extracted_by="bootstrap_v3_2026-02-15",
    )


def create_multisensory_integration_framework() -> Theory:
    """
    TIER 1.10: Multisensory Integration (MSI).

    Added per Panel III (docs/02-15_03_Panel_III_Multimodal_Senses_HigherCognition_V1.0.md).
    The brain integrates information across sensory modalities using principles like
    inverse effectiveness (weak unisensory signals benefit most from combination),
    temporal and spatial congruence, and reliability weighting.

    Neural implementation: Superior colliculus, parietal cortex, and superior temporal
    sulcus mediate multisensory integration. Crossmodal plasticity allows compensation
    when modalities are degraded.
    """
    theory_id = "framework:multisensory_integration"

    claims = [
        TheoryClaim(
            claim_id=f"{theory_id}:claim:01",
            theory_id=theory_id,
            statement="The brain integrates multisensory signals using reliability weighting and congruence detection",
            formalization="percept = Σ(modality_signal × reliability_weight) subject to congruence constraints",
            necessity=Necessity.CORE,
            testability=Testability.DIRECTLY_TESTABLE,
        ),
        TheoryClaim(
            claim_id=f"{theory_id}:claim:02",
            theory_id=theory_id,
            statement="Inverse effectiveness: weak unisensory signals benefit most from multisensory combination",
            formalization="enhancement = f(1/unisensory_strength); max_enhancement when unisensory weak",
            necessity=Necessity.CORE,
            testability=Testability.DIRECTLY_TESTABLE,
        ),
        TheoryClaim(
            claim_id=f"{theory_id}:claim:03",
            theory_id=theory_id,
            statement="Crossmodal congruence enhances environmental coherence percept and comfort",
            formalization="congruent_multisensory → enhanced_coherence_percept + increased_comfort",
            necessity=Necessity.CORE,
            testability=Testability.DIRECTLY_TESTABLE,
        ),
    ]

    predictions = [
        Prediction(
            prediction_id=f"{theory_id}:pred:001",
            source_theory_id=theory_id,
            statement="Congruent visual-auditory environments should be rated more comfortable than incongruent ones",
            prediction_type=PredictionType.DERIVED,
            consequent_outcome="environmental_comfort",
            consequent_direction=Direction.POSITIVE,
            consequent_magnitude=Magnitude.MODERATE,
            testing_status=TestingStatus.PARTIALLY_TESTED,
            overall_support=SupportLevel.SUPPORTED,
            prior_confidence=0.75,
            current_confidence=0.75,
        ),
        Prediction(
            prediction_id=f"{theory_id}:pred:002",
            source_theory_id=theory_id,
            statement="Visual-thermal crossmodal effects should be strongest under ambiguous thermal conditions",
            prediction_type=PredictionType.DERIVED,
            consequent_outcome="thermal_perception_modulation",
            consequent_direction=Direction.POSITIVE,
            consequent_magnitude=Magnitude.MODERATE,
            testing_status=TestingStatus.PARTIALLY_TESTED,
            overall_support=SupportLevel.SUPPORTED,
            prior_confidence=0.70,
            current_confidence=0.70,
        ),
    ]

    return Theory(
        theory_id=theory_id,
        name="Multisensory Integration",
        aliases=["MSI", "Crossmodal Integration", "Multimodal Perception"],
        originators=[
            Originator(name="Barry Stein", year=1993),
            Originator(name="Alex Meredith", year=1993),
            Originator(name="Charles Spence", year=2004),
        ],
        year_introduced=1993,
        domain=["perception", "multisensory", "architecture", "crossmodal"],
        scope_description="Architectural experience is inherently multisensory; visual-auditory, visual-thermal, "
                          "and visual-haptic interactions shape environmental perception",
        level=TheoryLevel.FRAMEWORK_THEORY,
        core_claims=claims,
        derived_predictions=predictions,
        overall_confidence=0.80,
        confidence_rationale="Well-established principles; Stein & Meredith (1993) foundational; Spence extends to architectural domains",
        quantitative_precision="medium",
        parent_theories=[],  # Tier 1: no parents
        compatible_theories=["framework:predictive_processing", "framework:interoception"],
        replication_status=ReplicationStatus.STRONG,
        extraction_source="Stein & Meredith (1993); Spence (2004); Driver & Spence (2000)",
        extracted_by="bootstrap_v3_2026-02-15",
    )


# =============================================================================
# TIER 2: DOMAIN-SPECIFIC THEORIES — Phenomenological, explained BY Tier 1
# =============================================================================

def create_attention_restoration_theory() -> Theory:
    """Create Attention Restoration Theory (Kaplan & Kaplan)."""
    theory_id = "theory:attention_restoration"
    
    # Core claims
    claims = [
        TheoryClaim(
            claim_id=f"{theory_id}:claim:01",
            theory_id=theory_id,
            statement="Directed attention is a limited cognitive resource that can be fatigued through sustained use",
            formalization="capacity(directed_attention) < ∞; use(directed_attention, duration) → depletion",
            necessity=Necessity.CORE,
            testability=Testability.DIRECTLY_TESTABLE,
        ),
        TheoryClaim(
            claim_id=f"{theory_id}:claim:02",
            theory_id=theory_id,
            statement="Natural environments contain stimuli that engage involuntary attention (soft fascination) without requiring directed attention",
            formalization="natural_environment → soft_fascination_stimuli",
            necessity=Necessity.CORE,
            testability=Testability.DIRECTLY_TESTABLE,
        ),
        TheoryClaim(
            claim_id=f"{theory_id}:claim:03",
            theory_id=theory_id,
            statement="Engaging involuntary attention through soft fascination allows directed attention to recover",
            formalization="soft_fascination → ¬use(directed_attention) → recovery(directed_attention)",
            necessity=Necessity.CORE,
            testability=Testability.DIRECTLY_TESTABLE,
        ),
        TheoryClaim(
            claim_id=f"{theory_id}:claim:04",
            theory_id=theory_id,
            statement="Restorative environments have four properties: being away (psychological distance), extent (scope/coherence), fascination (effortless attention), and compatibility (fit with inclinations)",
            formalization="restorative ↔ (being_away ∧ extent ∧ fascination ∧ compatibility)",
            necessity=Necessity.AUXILIARY,
            testability=Testability.DIRECTLY_TESTABLE,
        ),
    ]
    
    # Assumptions
    assumptions = [
        TheoryAssumption(
            assumption_id=f"{theory_id}:assumption:01",
            theory_id=theory_id,
            statement="Directed and involuntary attention are functionally distinct cognitive systems",
            dependent_claims=[f"{theory_id}:claim:02", f"{theory_id}:claim:03"],
            violation_consequence="If attention is unitary, the proposed restoration mechanism cannot work as described",
        ),
        TheoryAssumption(
            assumption_id=f"{theory_id}:assumption:02",
            theory_id=theory_id,
            statement="Attentional fatigue is caused by use of directed attention, not by general arousal or stress",
            dependent_claims=[f"{theory_id}:claim:01", f"{theory_id}:claim:03"],
            violation_consequence="If fatigue is stress-based, nature might restore via stress reduction rather than attention mechanism",
        ),
    ]
    
    # Boundary conditions
    boundaries = [
        TheoryBoundary(
            boundary_id=f"{theory_id}:boundary:01",
            theory_id=theory_id,
            condition_description="Restoration requires prior depletion of directed attention",
            evidence_for_boundary=["Studies showing no restoration effect in non-fatigued participants"],
            mechanism_of_failure="Nothing to restore if not depleted",
            confidence_penalty=0.3,
        ),
        TheoryBoundary(
            boundary_id=f"{theory_id}:boundary:02",
            theory_id=theory_id,
            condition_description="Threat or demands in natural setting may prevent restoration",
            evidence_for_boundary=["Studies in uncomfortable or unsafe outdoor settings"],
            mechanism_of_failure="Threat engages directed attention, preventing recovery",
            confidence_penalty=0.2,
        ),
    ]
    
    # Explicit predictions
    explicit_predictions = [
        Prediction(
            prediction_id=f"{theory_id}:pred:001",
            source_theory_id=theory_id,
            statement="Exposure to natural environments improves directed attention performance in fatigued individuals",
            prediction_type=PredictionType.EXPLICIT,
            antecedent_env_conditions=[{"type": "natural_environment", "features": ["vegetation", "water", "sky"]}],
            antecedent_state=[{"state": "attentional_fatigue", "required": True}],
            consequent_outcome="directed_attention_performance",
            consequent_direction=Direction.POSITIVE,
            consequent_magnitude=Magnitude.MODERATE,
            generality=Generality.DOMAIN_SPECIFIC,
            testing_status=TestingStatus.WELL_TESTED,
            overall_support=SupportLevel.SUPPORTED,
            prior_confidence=0.85,
            current_confidence=0.80,
            theory_contribution=0.4,
            empirical_contribution=0.4,
        ),
        Prediction(
            prediction_id=f"{theory_id}:pred:002",
            source_theory_id=theory_id,
            statement="The four components of restorative environments (being away, extent, fascination, compatibility) each contribute independently to restoration",
            prediction_type=PredictionType.EXPLICIT,
            consequent_outcome="attention_restoration",
            consequent_direction=Direction.POSITIVE,
            consequent_magnitude=Magnitude.MODERATE,
            generality=Generality.UNIVERSAL,
            testing_status=TestingStatus.PARTIALLY_TESTED,
            overall_support=SupportLevel.MIXED,
            prior_confidence=0.70,
            current_confidence=0.60,
        ),
    ]
    
    # Derived predictions
    derived_predictions = [
        Prediction(
            prediction_id=f"{theory_id}:pred:003",
            source_theory_id=theory_id,
            statement="Forest walks should restore directed attention more than urban walks",
            prediction_type=PredictionType.DERIVED,
            derivation_chain=[
                DerivationStep(claim_id=f"{theory_id}:claim:02", inference_type="deductive"),
                DerivationStep(claim_id=f"{theory_id}:claim:03", inference_type="deductive"),
            ],
            antecedent_env_conditions=[{"type": "forest", "activity": "walking"}],
            antecedent_state=[{"state": "attentional_fatigue", "required": True}],
            consequent_outcome="directed_attention_performance",
            consequent_direction=Direction.POSITIVE,
            consequent_magnitude=Magnitude.MODERATE,
            testing_status=TestingStatus.WELL_TESTED,
            overall_support=SupportLevel.STRONGLY_SUPPORTED,
            prior_confidence=0.75,
            current_confidence=0.85,
        ),
        Prediction(
            prediction_id=f"{theory_id}:pred:004",
            source_theory_id=theory_id,
            statement="Urban parks with natural elements should provide some restoration, less than wilderness",
            prediction_type=PredictionType.DERIVED,
            derivation_chain=[
                DerivationStep(claim_id=f"{theory_id}:claim:02", inference_type="deductive"),
                DerivationStep(claim_id=f"{theory_id}:claim:04", inference_type="inductive"),
            ],
            antecedent_env_conditions=[{"type": "urban_park", "features": ["trees", "grass"]}],
            consequent_outcome="attention_restoration",
            consequent_direction=Direction.POSITIVE,
            consequent_magnitude=Magnitude.WEAK,
            testing_status=TestingStatus.PARTIALLY_TESTED,
            overall_support=SupportLevel.SUPPORTED,
            prior_confidence=0.65,
            current_confidence=0.70,
        ),
        Prediction(
            prediction_id=f"{theory_id}:pred:005",
            source_theory_id=theory_id,
            statement="Indoor plants and nature views should provide partial restoration benefits",
            prediction_type=PredictionType.DERIVED,
            derivation_chain=[
                DerivationStep(claim_id=f"{theory_id}:claim:02", inference_type="analogical"),
                DerivationStep(claim_id=f"{theory_id}:claim:03", inference_type="deductive"),
            ],
            antecedent_env_conditions=[{"type": "indoor", "features": ["plants", "nature_view"]}],
            consequent_outcome="attention_restoration",
            consequent_direction=Direction.POSITIVE,
            consequent_magnitude=Magnitude.WEAK,
            testing_status=TestingStatus.PARTIALLY_TESTED,
            overall_support=SupportLevel.MIXED,
            prior_confidence=0.55,
            current_confidence=0.55,
        ),
        Prediction(
            prediction_id=f"{theory_id}:pred:006",
            source_theory_id=theory_id,
            statement="Restoration effects should be absent or minimal in non-fatigued individuals",
            prediction_type=PredictionType.DERIVED,
            derivation_chain=[
                DerivationStep(claim_id=f"{theory_id}:claim:01", inference_type="deductive"),
            ],
            auxiliary_assumptions=["boundary:01"],
            antecedent_state=[{"state": "attentional_fatigue", "required": False}],
            consequent_outcome="attention_restoration",
            consequent_direction=Direction.NULL,
            consequent_magnitude=Magnitude.UNSPECIFIED,
            testing_status=TestingStatus.PARTIALLY_TESTED,
            overall_support=SupportLevel.SUPPORTED,
            prior_confidence=0.75,
            current_confidence=0.70,
        ),
    ]
    
    return Theory(
        theory_id=theory_id,
        name="Attention Restoration Theory",
        aliases=["ART", "Kaplan's ART", "Restorative Environments Theory"],
        originators=[
            Originator(name="Rachel Kaplan", year=1989),
            Originator(name="Stephen Kaplan", year=1989),
        ],
        year_introduced=1989,
        domain=["attention", "cognition", "natural_environments", "restoration"],
        scope_description=(
            "TIER 2: Phenomenological description of attentional restoration in natural environments. "
            "TIER 1 REINTERPRETATION: What ART calls 'soft fascination' is explained mechanistically as "
            "DMN engagement (Tier 1.4) when TPN suppression is released in environments with low prediction "
            "error demands (Tier 1.1). The theory accurately describes the phenomenology but lacks neural "
            "mechanism connecting 'soft fascination' to brain processes."
        ),
        level=TheoryLevel.DOMAIN_THEORY,  # DEMOTED from THEORY — explained BY Tier 1
        core_claims=claims,
        assumptions=assumptions,
        boundary_conditions=boundaries,
        explicit_predictions=explicit_predictions,
        derived_predictions=derived_predictions,
        overall_confidence=0.75,
        confidence_rationale="Phenomenology well-established; lacks mechanistic depth. Tier 1 frameworks (DMN/TPN, PP) provide the underlying mechanism.",
        quantitative_precision="low",
        parent_theories=["framework:dmn_tpn", "framework:predictive_processing"],  # DERIVED FROM Tier 1
        child_theories=[],
        compatible_theories=["theory:stress_recovery", "theory:biophilia"],
        competing_theories=[],
        replication_status=ReplicationStatus.MODERATE,
        extraction_source="Kaplan, S., & Kaplan, R. (1989). The Experience of Nature",
        extracted_by="bootstrap_v2_2026-02-14",
    )


def create_stress_recovery_theory() -> Theory:
    """Create Stress Recovery Theory (Ulrich)."""
    theory_id = "theory:stress_recovery"
    
    claims = [
        TheoryClaim(
            claim_id=f"{theory_id}:claim:01",
            theory_id=theory_id,
            statement="Viewing natural scenes triggers rapid, automatic affective responses that reduce physiological stress",
            formalization="natural_scene_viewing → autonomic_response → stress_reduction",
            necessity=Necessity.CORE,
            testability=Testability.DIRECTLY_TESTABLE,
        ),
        TheoryClaim(
            claim_id=f"{theory_id}:claim:02",
            theory_id=theory_id,
            statement="Stress recovery from nature is evolutionarily based, involving innate responses to savanna-like environments",
            formalization="evolutionary_adaptation(savanna_features) → innate_preference → stress_reduction",
            necessity=Necessity.CORE,
            testability=Testability.INDIRECTLY_TESTABLE,
        ),
        TheoryClaim(
            claim_id=f"{theory_id}:claim:03",
            theory_id=theory_id,
            statement="Nature exposure produces measurable reductions in cortisol, blood pressure, heart rate, and muscle tension",
            necessity=Necessity.CORE,
            testability=Testability.DIRECTLY_TESTABLE,
        ),
    ]
    
    assumptions = [
        TheoryAssumption(
            assumption_id=f"{theory_id}:assumption:01",
            theory_id=theory_id,
            statement="Humans have evolved specific psychophysiological responses to natural environments",
            dependent_claims=[f"{theory_id}:claim:02"],
            violation_consequence="If responses are learned rather than innate, cultural variation would be much larger than observed",
        ),
    ]
    
    boundaries = [
        TheoryBoundary(
            boundary_id=f"{theory_id}:boundary:01",
            theory_id=theory_id,
            condition_description="Natural environments perceived as threatening do not reduce stress",
            evidence_for_boundary=["Studies on fear-inducing natural scenes"],
            mechanism_of_failure="Threat perception activates stress rather than reducing it",
            confidence_penalty=0.2,
        ),
    ]
    
    explicit_predictions = [
        Prediction(
            prediction_id=f"{theory_id}:pred:001",
            source_theory_id=theory_id,
            statement="Viewing nature images produces faster stress recovery than viewing urban images",
            prediction_type=PredictionType.EXPLICIT,
            antecedent_env_conditions=[{"type": "visual", "content": "nature_images"}],
            antecedent_state=[{"state": "acute_stress", "required": True}],
            consequent_outcome="physiological_stress_markers",
            consequent_direction=Direction.NEGATIVE,
            consequent_magnitude=Magnitude.MODERATE,
            testing_status=TestingStatus.WELL_TESTED,
            overall_support=SupportLevel.STRONGLY_SUPPORTED,
            prior_confidence=0.85,
            current_confidence=0.85,
        ),
    ]
    
    derived_predictions = [
        Prediction(
            prediction_id=f"{theory_id}:pred:002",
            source_theory_id=theory_id,
            statement="Hospital patients with nature views should recover faster than those with urban views",
            prediction_type=PredictionType.DERIVED,
            derivation_chain=[
                DerivationStep(claim_id=f"{theory_id}:claim:01", inference_type="deductive"),
                DerivationStep(claim_id=f"{theory_id}:claim:03", inference_type="deductive"),
            ],
            antecedent_env_conditions=[{"type": "window_view", "content": "nature"}],
            consequent_outcome="recovery_time",
            consequent_direction=Direction.NEGATIVE,
            consequent_magnitude=Magnitude.MODERATE,
            testing_status=TestingStatus.WELL_TESTED,
            overall_support=SupportLevel.STRONGLY_SUPPORTED,
            prior_confidence=0.75,
            current_confidence=0.85,
            test_summary="Ulrich's classic 1984 study and subsequent replications",
        ),
        Prediction(
            prediction_id=f"{theory_id}:pred:003",
            source_theory_id=theory_id,
            statement="Savanna-like landscapes should be particularly effective for stress recovery",
            prediction_type=PredictionType.DERIVED,
            derivation_chain=[
                DerivationStep(claim_id=f"{theory_id}:claim:02", inference_type="deductive"),
            ],
            antecedent_env_conditions=[{"type": "landscape", "features": ["open", "scattered_trees", "water"]}],
            consequent_outcome="stress_recovery",
            consequent_direction=Direction.POSITIVE,
            consequent_magnitude=Magnitude.STRONG,
            testing_status=TestingStatus.PARTIALLY_TESTED,
            overall_support=SupportLevel.SUPPORTED,
            prior_confidence=0.70,
            current_confidence=0.65,
        ),
    ]
    
    return Theory(
        theory_id=theory_id,
        name="Stress Recovery Theory",
        aliases=["SRT", "Ulrich's Stress Recovery Theory", "Psychoevolutionary Theory"],
        originators=[
            Originator(name="Roger Ulrich", year=1983, doi="10.1016/0272-4944(83)90016-1"),
        ],
        year_introduced=1983,
        domain=["stress", "health", "natural_environments", "physiology"],
        scope_description=(
            "TIER 2: Phenomenological description of how natural environments produce rapid "
            "stress recovery through evolutionarily-based affective responses. SRT describes "
            "what happens (nature triggers parasympathetic activation) but not why neural systems "
            "respond this way. "
            "TIER 1 REINTERPRETATION: What SRT calls 'affective response' is explained by "
            "Predictive Processing as rapid uncertainty reduction (natural scenes have learnable "
            "statistics) plus Neuromodulatory Framework as parasympathetic dominance shift. "
            "The evolutionary framing is an ultimate-level description; proximate mechanisms "
            "are specified by Tier 1 frameworks."
        ),
        level=TheoryLevel.DOMAIN_THEORY,  # DEMOTED from THEORY — Tier 2
        parent_theories=["framework:neuromodulatory", "framework:predictive_processing"],
        core_claims=claims,
        assumptions=assumptions,
        boundary_conditions=boundaries,
        explicit_predictions=explicit_predictions,
        derived_predictions=derived_predictions,
        overall_confidence=0.80,
        confidence_rationale="Strong empirical support from multiple physiological measures; evolutionary claims harder to test directly",
        quantitative_precision="medium",
        compatible_theories=["theory:attention_restoration", "theory:biophilia"],
        replication_status=ReplicationStatus.STRONG,
        extraction_source="Ulrich, R. S. (1983). Aesthetic and affective response to natural environment",
        extracted_by="bootstrap",
    )


def create_predictive_processing_theory() -> Theory:
    """Create Predictive Processing / Active Inference theory."""
    theory_id = "theory:predictive_processing"
    
    claims = [
        TheoryClaim(
            claim_id=f"{theory_id}:claim:01",
            theory_id=theory_id,
            statement="The brain is fundamentally a prediction machine that constructs models of the world to minimize prediction error",
            formalization="brain_function = minimize(prediction_error)",
            necessity=Necessity.CORE,
            testability=Testability.INDIRECTLY_TESTABLE,
        ),
        TheoryClaim(
            claim_id=f"{theory_id}:claim:02",
            theory_id=theory_id,
            statement="Perception is inference: what we perceive is the brain's best prediction about the causes of sensory input",
            formalization="perception = argmax P(cause | sensory_input)",
            necessity=Necessity.CORE,
            testability=Testability.DIRECTLY_TESTABLE,
        ),
        TheoryClaim(
            claim_id=f"{theory_id}:claim:03",
            theory_id=theory_id,
            statement="Chronic high prediction error generates stress and negative affect",
            formalization="chronic(high_prediction_error) → stress + negative_affect",
            necessity=Necessity.CORE,
            testability=Testability.DIRECTLY_TESTABLE,
        ),
        TheoryClaim(
            claim_id=f"{theory_id}:claim:04",
            theory_id=theory_id,
            statement="Environments with learnable structure (moderate complexity) are preferred over chaotic or monotonous environments",
            formalization="preference(env) ∝ learnability(env) = moderate_complexity",
            necessity=Necessity.AUXILIARY,
            testability=Testability.DIRECTLY_TESTABLE,
        ),
    ]
    
    assumptions = [
        TheoryAssumption(
            assumption_id=f"{theory_id}:assumption:01",
            theory_id=theory_id,
            statement="The brain implements approximate Bayesian inference",
            dependent_claims=[f"{theory_id}:claim:01", f"{theory_id}:claim:02"],
            violation_consequence="If processing is not Bayesian, prediction error minimization may not be the organizing principle",
        ),
    ]
    
    boundaries = [
        TheoryBoundary(
            boundary_id=f"{theory_id}:boundary:01",
            theory_id=theory_id,
            condition_description="Extreme novelty can be rewarding despite high prediction error (exploration)",
            mechanism_of_failure="Epistemic value of reducing uncertainty can outweigh prediction error costs",
            confidence_penalty=0.1,
        ),
    ]
    
    explicit_predictions = [
        Prediction(
            prediction_id=f"{theory_id}:pred:001",
            source_theory_id=theory_id,
            statement="Unpredictable environments should generate chronic stress",
            prediction_type=PredictionType.EXPLICIT,
            antecedent_env_conditions=[{"type": "unpredictable", "features": ["random_noise", "irregular_patterns"]}],
            consequent_outcome="chronic_stress",
            consequent_direction=Direction.POSITIVE,
            consequent_magnitude=Magnitude.MODERATE,
            testing_status=TestingStatus.PARTIALLY_TESTED,
            overall_support=SupportLevel.SUPPORTED,
            prior_confidence=0.80,
            current_confidence=0.75,
        ),
    ]
    
    derived_predictions = [
        Prediction(
            prediction_id=f"{theory_id}:pred:002",
            source_theory_id=theory_id,
            statement="Environments with moderate novelty should be engaging without being stressful",
            prediction_type=PredictionType.DERIVED,
            derivation_chain=[
                DerivationStep(claim_id=f"{theory_id}:claim:03", inference_type="deductive"),
                DerivationStep(claim_id=f"{theory_id}:claim:04", inference_type="deductive"),
            ],
            antecedent_env_conditions=[{"type": "moderate_novelty"}],
            consequent_outcome="engagement",
            consequent_direction=Direction.POSITIVE,
            consequent_magnitude=Magnitude.MODERATE,
            testing_status=TestingStatus.PARTIALLY_TESTED,
            overall_support=SupportLevel.SUPPORTED,
            prior_confidence=0.75,
            current_confidence=0.70,
        ),
        Prediction(
            prediction_id=f"{theory_id}:pred:003",
            source_theory_id=theory_id,
            statement="Mid-range fractal dimension (D≈1.3-1.5) should be preferred as it matches natural statistics the visual system is tuned to",
            prediction_type=PredictionType.DERIVED,
            derivation_chain=[
                DerivationStep(claim_id=f"{theory_id}:claim:02", inference_type="deductive"),
                DerivationStep(claim_id=f"{theory_id}:claim:04", inference_type="analogical"),
            ],
            antecedent_env_conditions=[{"type": "visual_pattern", "fractal_dimension": [1.3, 1.5]}],
            consequent_outcome="aesthetic_preference",
            consequent_direction=Direction.POSITIVE,
            consequent_magnitude=Magnitude.MODERATE,
            testing_status=TestingStatus.PARTIALLY_TESTED,
            overall_support=SupportLevel.SUPPORTED,
            prior_confidence=0.65,
            current_confidence=0.70,
        ),
        Prediction(
            prediction_id=f"{theory_id}:pred:004",
            source_theory_id=theory_id,
            statement="Familiar environments should be processed more fluently and feel more positive",
            prediction_type=PredictionType.DERIVED,
            derivation_chain=[
                DerivationStep(claim_id=f"{theory_id}:claim:01", inference_type="deductive"),
                DerivationStep(claim_id=f"{theory_id}:claim:03", inference_type="deductive"),
            ],
            antecedent_env_conditions=[{"type": "familiar_environment"}],
            consequent_outcome="positive_affect",
            consequent_direction=Direction.POSITIVE,
            consequent_magnitude=Magnitude.WEAK,
            testing_status=TestingStatus.WELL_TESTED,
            overall_support=SupportLevel.STRONGLY_SUPPORTED,
            prior_confidence=0.80,
            current_confidence=0.85,
        ),
    ]
    
    # DEPRECATED: This function is superseded by create_predictive_processing_framework()
    # which is the canonical Tier 1 Framework Theory. This version is retained for
    # backwards compatibility but should not be used for new code.
    # See: framework:predictive_processing for the Tier 1 version.
    return Theory(
        theory_id=theory_id,
        name="Predictive Processing",
        aliases=["PP", "Active Inference", "Predictive Coding", "Free Energy Principle"],
        originators=[
            Originator(name="Karl Friston", year=2010),
            Originator(name="Andy Clark", year=2013),
            Originator(name="Jakob Hohwy", year=2013),
        ],
        year_introduced=2010,
        domain=["perception", "cognition", "affect", "learning", "neuroscience"],
        scope_description=(
            "DEPRECATED: See framework:predictive_processing for canonical Tier 1 version. "
            "This entry retained for backwards compatibility only. "
            "General theory of brain function based on prediction error minimization; "
            "applies to environmental perception and preference."
        ),
        level=TheoryLevel.FRAMEWORK_THEORY,  # Upgraded to proper tier
        core_claims=claims,
        assumptions=assumptions,
        boundary_conditions=boundaries,
        explicit_predictions=explicit_predictions,
        derived_predictions=derived_predictions,
        overall_confidence=0.75,
        confidence_rationale="Widely influential framework with growing empirical support; some concerns about unfalsifiability",
        quantitative_precision="low",
        parent_theories=["theory:bayesian_brain"],
        child_theories=["theory:perceptual_fluency"],
        compatible_theories=["theory:fractal_fluency", "theory:perceptual_fluency"],
        replication_status=ReplicationStatus.MODERATE,
        extraction_source="Clark, A. (2013). Whatever next? Predictive brains, situated agents, and the future of cognitive science",
        extracted_by="bootstrap",
    )


def create_biophilia_hypothesis() -> Theory:
    """Create Biophilia Hypothesis (Wilson)."""
    theory_id = "theory:biophilia"
    
    claims = [
        TheoryClaim(
            claim_id=f"{theory_id}:claim:01",
            theory_id=theory_id,
            statement="Humans have an innate tendency to seek connections with nature and other forms of life",
            formalization="innate_tendency(humans, affiliate_with_life)",
            necessity=Necessity.CORE,
            testability=Testability.INDIRECTLY_TESTABLE,
        ),
        TheoryClaim(
            claim_id=f"{theory_id}:claim:02",
            theory_id=theory_id,
            statement="This affiliation has evolutionary origins and contributes to human wellbeing",
            formalization="biophilia → wellbeing",
            necessity=Necessity.CORE,
            testability=Testability.DIRECTLY_TESTABLE,
        ),
    ]
    
    explicit_predictions = [
        Prediction(
            prediction_id=f"{theory_id}:pred:001",
            source_theory_id=theory_id,
            statement="Humans across cultures should show preference for natural environments",
            prediction_type=PredictionType.EXPLICIT,
            consequent_outcome="nature_preference",
            consequent_direction=Direction.POSITIVE,
            consequent_magnitude=Magnitude.MODERATE,
            generality=Generality.UNIVERSAL,
            testing_status=TestingStatus.WELL_TESTED,
            overall_support=SupportLevel.STRONGLY_SUPPORTED,
            prior_confidence=0.85,
            current_confidence=0.80,
        ),
    ]
    
    derived_predictions = [
        Prediction(
            prediction_id=f"{theory_id}:pred:002",
            source_theory_id=theory_id,
            statement="Biophilic design elements in buildings should improve occupant wellbeing",
            prediction_type=PredictionType.DERIVED,
            derivation_chain=[
                DerivationStep(claim_id=f"{theory_id}:claim:01", inference_type="deductive"),
                DerivationStep(claim_id=f"{theory_id}:claim:02", inference_type="deductive"),
            ],
            antecedent_env_conditions=[{"type": "built_environment", "features": ["plants", "natural_materials", "water", "daylight"]}],
            consequent_outcome="occupant_wellbeing",
            consequent_direction=Direction.POSITIVE,
            consequent_magnitude=Magnitude.MODERATE,
            testing_status=TestingStatus.PARTIALLY_TESTED,
            overall_support=SupportLevel.SUPPORTED,
            prior_confidence=0.70,
            current_confidence=0.70,
        ),
    ]
    
    return Theory(
        theory_id=theory_id,
        name="Biophilia Hypothesis",
        aliases=["Biophilia", "Biophilic Design Theory"],
        originators=[
            Originator(name="Edward O. Wilson", year=1984),
        ],
        year_introduced=1984,
        domain=["nature_affiliation", "wellbeing", "evolution", "design"],
        scope_description=(
            "TIER 2: Phenomenological description proposing an innate human need to affiliate "
            "with other living systems and natural processes. Biophilia describes WHAT we prefer "
            "(nature connection) and offers evolutionary rationale, but does not specify HOW "
            "the brain generates these responses. "
            "TIER 1 REINTERPRETATION: What Wilson calls 'biophilia' is explained by Predictive "
            "Processing as nature having learnable statistics matching our evolved visual priors "
            "(fractals, 1/f noise, prospect-refuge layouts). The 'innate' component reflects "
            "developmental canalization of predictive models, not a specialized 'biophilia module'."
        ),
        level=TheoryLevel.DOMAIN_THEORY,  # DEMOTED from THEORY — Tier 2
        parent_theories=["framework:predictive_processing"],
        core_claims=claims,
        explicit_predictions=explicit_predictions,
        derived_predictions=derived_predictions,
        overall_confidence=0.70,
        confidence_rationale="Widely influential but difficult to test the 'innate' component; good evidence for nature-wellbeing links",
        quantitative_precision="low",
        compatible_theories=["theory:attention_restoration", "theory:stress_recovery"],
        replication_status=ReplicationStatus.MODERATE,
        extraction_source="Wilson, E.O. (1984). Biophilia",
        extracted_by="bootstrap",
    )


def create_fractal_fluency_hypothesis() -> Theory:
    """Create Fractal Fluency Hypothesis (Taylor)."""
    theory_id = "theory:fractal_fluency"
    
    claims = [
        TheoryClaim(
            claim_id=f"{theory_id}:claim:01",
            theory_id=theory_id,
            statement="The visual system is tuned to the fractal statistics commonly found in nature (D≈1.3)",
            formalization="visual_tuning(fractal_statistics, D≈1.3)",
            necessity=Necessity.CORE,
            testability=Testability.DIRECTLY_TESTABLE,
        ),
        TheoryClaim(
            claim_id=f"{theory_id}:claim:02",
            theory_id=theory_id,
            statement="Mid-range fractal patterns (D≈1.3-1.5) are processed more fluently and rated as more beautiful",
            formalization="mid_D_fractals → fluent_processing → aesthetic_preference",
            necessity=Necessity.CORE,
            testability=Testability.DIRECTLY_TESTABLE,
        ),
        TheoryClaim(
            claim_id=f"{theory_id}:claim:03",
            theory_id=theory_id,
            statement="Viewing mid-D fractals produces physiological relaxation (reduced alpha wave activity)",
            necessity=Necessity.AUXILIARY,
            testability=Testability.DIRECTLY_TESTABLE,
        ),
    ]
    
    explicit_predictions = [
        Prediction(
            prediction_id=f"{theory_id}:pred:001",
            source_theory_id=theory_id,
            statement="Peak aesthetic preference should occur at fractal dimension D≈1.3-1.5",
            prediction_type=PredictionType.EXPLICIT,
            antecedent_env_conditions=[{"type": "fractal_pattern", "D_range": [1.3, 1.5]}],
            consequent_outcome="aesthetic_preference",
            consequent_direction=Direction.POSITIVE,
            consequent_magnitude=Magnitude.MODERATE,
            quantitative=QuantitativePrediction(point_estimate=1.35, ci_lower=1.2, ci_upper=1.5),
            testing_status=TestingStatus.WELL_TESTED,
            overall_support=SupportLevel.SUPPORTED,
            prior_confidence=0.75,
            current_confidence=0.75,
        ),
    ]
    
    derived_predictions = [
        Prediction(
            prediction_id=f"{theory_id}:pred:002",
            source_theory_id=theory_id,
            statement="Architecture incorporating mid-D fractal patterns should be more aesthetically pleasing",
            prediction_type=PredictionType.DERIVED,
            derivation_chain=[
                DerivationStep(claim_id=f"{theory_id}:claim:02", inference_type="analogical"),
            ],
            antecedent_env_conditions=[{"type": "architecture", "features": ["fractal_facade", "natural_materials"]}],
            consequent_outcome="aesthetic_rating",
            consequent_direction=Direction.POSITIVE,
            consequent_magnitude=Magnitude.MODERATE,
            testing_status=TestingStatus.PARTIALLY_TESTED,
            overall_support=SupportLevel.SUPPORTED,
            prior_confidence=0.65,
            current_confidence=0.65,
        ),
        Prediction(
            prediction_id=f"{theory_id}:pred:003",
            source_theory_id=theory_id,
            statement="Exposure to mid-D fractals should reduce physiological stress markers",
            prediction_type=PredictionType.DERIVED,
            derivation_chain=[
                DerivationStep(claim_id=f"{theory_id}:claim:03", inference_type="deductive"),
            ],
            antecedent_env_conditions=[{"type": "visual", "content": "mid_D_fractals"}],
            consequent_outcome="stress_markers",
            consequent_direction=Direction.NEGATIVE,
            consequent_magnitude=Magnitude.WEAK,
            testing_status=TestingStatus.PARTIALLY_TESTED,
            overall_support=SupportLevel.MIXED,
            prior_confidence=0.60,
            current_confidence=0.55,
        ),
    ]
    
    return Theory(
        theory_id=theory_id,
        name="Fractal Fluency Hypothesis",
        aliases=["Fractal Fluency", "Visual Fluency to Fractals"],
        originators=[
            Originator(name="Richard Taylor", year=2006),
        ],
        year_introduced=2006,
        domain=["visual_perception", "aesthetics", "fractals", "architecture"],
        scope_description=(
            "TIER 2: Domain-specific instantiation of Predictive Processing for fractal visual "
            "statistics. Fractal Fluency describes WHAT patterns are preferred (D≈1.3-1.5) and "
            "proposes that visual system tuning to natural statistics underlies aesthetic response. "
            "TIER 1 REINTERPRETATION: The 'fluency' component is precision-weighted prediction "
            "error minimization. Mid-D fractals match evolved priors for natural scene statistics, "
            "reducing prediction error and generating positive valence via Neuromodulatory Framework."
        ),
        level=TheoryLevel.DOMAIN_THEORY,  # DEMOTED from PRINCIPLE — Tier 2
        core_claims=claims,
        explicit_predictions=explicit_predictions,
        derived_predictions=derived_predictions,
        overall_confidence=0.65,
        confidence_rationale="Interesting hypothesis with some empirical support; specific D values vary across studies",
        quantitative_precision="medium",
        parent_theories=["framework:predictive_processing"],  # Updated to framework ID
        compatible_theories=["theory:predictive_processing", "theory:perceptual_fluency"],
        replication_status=ReplicationStatus.MIXED,
        extraction_source="Taylor, R.P. et al. (2006). Perceptual and physiological responses to Jackson Pollock's fractals",
        extracted_by="bootstrap",
    )


def create_allostatic_load_theory() -> Theory:
    """Create Allostatic Load Model (McEwen)."""
    theory_id = "theory:allostatic_load"
    
    claims = [
        TheoryClaim(
            claim_id=f"{theory_id}:claim:01",
            theory_id=theory_id,
            statement="Physiological regulation has metabolic costs; the body maintains stability through change (allostasis)",
            formalization="regulation → metabolic_cost; allostasis = stability_through_change",
            necessity=Necessity.CORE,
            testability=Testability.DIRECTLY_TESTABLE,
        ),
        TheoryClaim(
            claim_id=f"{theory_id}:claim:02",
            theory_id=theory_id,
            statement="Chronic stress causes cumulative physiological wear (allostatic load)",
            formalization="chronic_stress → cumulative(physiological_wear) = allostatic_load",
            necessity=Necessity.CORE,
            testability=Testability.DIRECTLY_TESTABLE,
        ),
        TheoryClaim(
            claim_id=f"{theory_id}:claim:03",
            theory_id=theory_id,
            statement="Allostatic overload occurs when load exceeds recovery capacity, producing health consequences",
            formalization="allostatic_load > recovery_capacity → allostatic_overload → health_consequences",
            necessity=Necessity.CORE,
            testability=Testability.DIRECTLY_TESTABLE,
        ),
    ]
    
    boundaries = [
        TheoryBoundary(
            boundary_id=f"{theory_id}:boundary:01",
            theory_id=theory_id,
            condition_description="Individual differences in recovery capacity affect load thresholds",
            mechanism_of_failure="Same stressor produces different load in different individuals",
            confidence_penalty=0.1,
        ),
    ]
    
    explicit_predictions = [
        Prediction(
            prediction_id=f"{theory_id}:pred:001",
            source_theory_id=theory_id,
            statement="Chronic environmental stressors should produce cumulative health effects",
            prediction_type=PredictionType.EXPLICIT,
            antecedent_env_conditions=[{"type": "chronic_stressor", "examples": ["noise", "crowding", "pollution"]}],
            antecedent_temporal={"exposure_type": "chronic", "duration": "months_to_years"},
            consequent_outcome="health_markers",
            consequent_direction=Direction.NEGATIVE,
            consequent_magnitude=Magnitude.MODERATE,
            testing_status=TestingStatus.WELL_TESTED,
            overall_support=SupportLevel.STRONGLY_SUPPORTED,
            prior_confidence=0.85,
            current_confidence=0.85,
        ),
    ]
    
    derived_predictions = [
        Prediction(
            prediction_id=f"{theory_id}:pred:002",
            source_theory_id=theory_id,
            statement="Multiple mild stressors in built environments should combine to increase allostatic load",
            prediction_type=PredictionType.DERIVED,
            derivation_chain=[
                DerivationStep(claim_id=f"{theory_id}:claim:02", inference_type="deductive"),
            ],
            antecedent_env_conditions=[{"type": "multiple_stressors", "examples": ["noise", "poor_lighting", "crowding"]}],
            consequent_outcome="allostatic_load_markers",
            consequent_direction=Direction.POSITIVE,
            consequent_magnitude=Magnitude.MODERATE,
            testing_status=TestingStatus.PARTIALLY_TESTED,
            overall_support=SupportLevel.SUPPORTED,
            prior_confidence=0.75,
            current_confidence=0.70,
        ),
        Prediction(
            prediction_id=f"{theory_id}:pred:003",
            source_theory_id=theory_id,
            statement="Environmental interventions that reduce stressor exposure should reduce allostatic load over time",
            prediction_type=PredictionType.DERIVED,
            derivation_chain=[
                DerivationStep(claim_id=f"{theory_id}:claim:02", inference_type="deductive"),
                DerivationStep(claim_id=f"{theory_id}:claim:03", inference_type="deductive"),
            ],
            antecedent_env_conditions=[{"type": "intervention", "effect": "reduced_stressor_exposure"}],
            antecedent_temporal={"exposure_type": "chronic", "duration": "weeks_to_months"},
            consequent_outcome="allostatic_load",
            consequent_direction=Direction.NEGATIVE,
            consequent_magnitude=Magnitude.MODERATE,
            testing_status=TestingStatus.PARTIALLY_TESTED,
            overall_support=SupportLevel.SUPPORTED,
            prior_confidence=0.70,
            current_confidence=0.65,
        ),
    ]
    
    return Theory(
        theory_id=theory_id,
        name="Allostatic Load Model",
        aliases=["Allostatic Load", "Allostasis Theory"],
        originators=[
            Originator(name="Bruce McEwen", year=1998),
            Originator(name="Eliot Stellar", year=1993),
        ],
        year_introduced=1993,
        domain=["stress", "health", "physiology", "chronic_exposure"],
        scope_description=(
            "TIER 2: Domain-specific instantiation of Neuromodulatory and Interoceptive Frameworks "
            "for chronic stress. Allostatic Load describes WHAT happens (cumulative physiological "
            "wear from repeated stress activation) but relies on Tier 1 frameworks for HOW: "
            "TIER 1 REINTERPRETATION: Allostatic load is the cumulative cost of Neuromodulatory "
            "Framework's stress-response cascade (HPA axis, sympathetic activation) when repeatedly "
            "triggered. Interoception Framework explains individual differences in allostatic "
            "trajectory via interoceptive sensitivity to accumulating load."
        ),
        level=TheoryLevel.DOMAIN_THEORY,  # DEMOTED from THEORY — Tier 2
        parent_theories=["framework:neuromodulatory", "framework:interoception"],
        core_claims=claims,
        boundary_conditions=boundaries,
        explicit_predictions=explicit_predictions,
        derived_predictions=derived_predictions,
        overall_confidence=0.85,
        confidence_rationale="Well-established in stress physiology; strong empirical support for chronic stress effects",
        quantitative_precision="medium",
        compatible_theories=["theory:stress_recovery"],
        replication_status=ReplicationStatus.STRONG,
        extraction_source="McEwen, B.S. (1998). Stress, adaptation, and disease: Allostasis and allostatic load",
        extracted_by="bootstrap",
    )


def get_tier1_frameworks() -> list[Theory]:
    """
    Return Tier 1 Framework Theories (neurally grounded, cross-domain).

    These are the foundational theories that meet three criteria:
    1. Mechanistic Specificity: Specify neural systems, pathways, and computational principles
    2. Cross-Domain Generativity: Generate testable predictions across multiple phenomena
    3. Convergent Multi-Method Support: Supported by multiple independent measurement methods

    Per Canonical Decisions Record (02-15_09), Decision 3:
    10 frameworks total (8 original + CB + MSI added by Panel II/III).

    Returns:
        List of 10 Tier 1 Framework Theory objects
    """
    return [
        create_predictive_processing_framework(),     # 1. PP
        create_spatial_navigation_framework(),        # 2. SN
        create_dual_process_framework(),              # 3. DP
        create_dmn_tpn_framework(),                   # 4. DT
        create_neuromodulatory_framework(),           # 5. NM
        create_interoception_framework(),             # 6. IC
        create_memory_systems_framework(),            # 7. MS
        create_embodied_cognition_framework(),        # 8. EC
        create_chronobiological_framework(),          # 9. CB (Panel II)
        create_multisensory_integration_framework(),  # 10. MSI (Panel III)
    ]


def get_tier2_domain_theories() -> list[Theory]:
    """
    Return Tier 2 Domain-Specific Theories (phenomenological descriptions).

    These theories describe WHAT happens (e.g., nature restores attention) but rely on
    Tier 1 frameworks to explain HOW (neural mechanisms, computational principles).
    Each has parent_theories linking to Tier 1 frameworks that provide mechanistic grounding.

    Returns:
        List of Tier 2 Domain Theory objects
    """
    return [
        create_attention_restoration_theory(),
        create_stress_recovery_theory(),
        create_biophilia_hypothesis(),
        create_fractal_fluency_hypothesis(),
        create_allostatic_load_theory(),
    ]


def get_all_bootstrap_theories() -> list[Theory]:
    """
    Return all bootstrap theories for initial registry population.

    Returns theories in tier order: Tier 1 frameworks first, then Tier 2 domain theories.
    The deprecated create_predictive_processing_theory() is excluded since it's superseded
    by create_predictive_processing_framework().
    """
    return get_tier1_frameworks() + get_tier2_domain_theories()


# Alias for compatibility
get_bootstrap_theories = get_all_bootstrap_theories


def bootstrap_registry(registry) -> dict:
    """
    Populate a TheoryRegistry with the bootstrap theories.
    
    Args:
        registry: TheoryRegistry instance
        
    Returns:
        Summary of what was added
    """
    theories = get_all_bootstrap_theories()
    
    added = []
    errors = []
    
    for theory in theories:
        try:
            registry.add_theory(theory)
            added.append({
                'theory_id': theory.theory_id,
                'name': theory.name,
                'n_claims': len(theory.core_claims),
                'n_predictions': len(theory.all_predictions),
            })
        except Exception as e:
            errors.append({
                'theory_id': theory.theory_id,
                'error': str(e),
            })
    
    return {
        'added': added,
        'errors': errors,
        'theories_added': len(added),
        'total_predictions': sum(t['n_predictions'] for t in added),
    }
