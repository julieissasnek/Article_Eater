"""
Article Eater - Theory Registry Bootstrap Data
Sprint TH-1: Theory Data Model & Registry

Contains the initial set of theories for the environmental psychology /
neuroarchitecture domain. These theories are seeded into the registry
to provide theory-derived priors for predictions.

Bootstrap theories:
1. Attention Restoration Theory (ART)
2. Stress Recovery Theory (SRT)
3. Predictive Processing / Active Inference
4. Biophilia Hypothesis
5. Fractal Fluency Hypothesis
6. Prospect-Refuge Theory
7. Allostatic Load Model
8. Perceptual Fluency / Hedonic Marking
9. Arousal Theory / Optimal Stimulation
10. Circadian Rhythm Theory
"""

from src.models.theory_models import (
    Theory, TheoryClaim, TheoryAssumption, TheoryBoundary,
    Prediction, Originator, DerivationStep, QuantitativePrediction,
    TheoryLevel, PredictionType, Direction, Magnitude, TestingStatus,
    SupportLevel, ReplicationStatus, Necessity, Testability,
    RelationType, Generality, UncertaintyType,
    generate_theory_id, generate_prediction_id, generate_claim_id,
    compute_derivation_confidence
)


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
        scope_description="Explains how natural environments restore depleted directed attention through soft fascination",
        level=TheoryLevel.THEORY,
        core_claims=claims,
        assumptions=assumptions,
        boundary_conditions=boundaries,
        explicit_predictions=explicit_predictions,
        derived_predictions=derived_predictions,
        overall_confidence=0.75,
        confidence_rationale="Well-established theory with extensive empirical support, though some boundary conditions and replication concerns",
        quantitative_precision="low",
        parent_theories=[],
        child_theories=[],
        compatible_theories=["theory:stress_recovery", "theory:biophilia"],
        competing_theories=[],
        replication_status=ReplicationStatus.MODERATE,
        extraction_source="Kaplan, S., & Kaplan, R. (1989). The Experience of Nature",
        extracted_by="bootstrap",
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
        scope_description="Explains how natural environments produce rapid stress recovery through evolutionarily-based affective responses",
        level=TheoryLevel.THEORY,
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
        scope_description="General theory of brain function based on prediction error minimization; applies to environmental perception and preference",
        level=TheoryLevel.THEORY,
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
        scope_description="Proposes an innate human need to affiliate with other living systems and natural processes",
        level=TheoryLevel.THEORY,
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
        scope_description="Explains aesthetic preferences for fractal patterns based on visual system tuning to natural statistics",
        level=TheoryLevel.PRINCIPLE,
        core_claims=claims,
        explicit_predictions=explicit_predictions,
        derived_predictions=derived_predictions,
        overall_confidence=0.65,
        confidence_rationale="Interesting hypothesis with some empirical support; specific D values vary across studies",
        quantitative_precision="medium",
        parent_theories=["theory:predictive_processing"],
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
        scope_description="Explains how chronic stress accumulates physiological wear and produces long-term health consequences",
        level=TheoryLevel.THEORY,
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


def get_all_bootstrap_theories() -> list[Theory]:
    """Return all bootstrap theories for initial registry population."""
    return [
        create_attention_restoration_theory(),
        create_stress_recovery_theory(),
        create_predictive_processing_theory(),
        create_biophilia_hypothesis(),
        create_fractal_fluency_hypothesis(),
        create_allostatic_load_theory(),
    ]


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
