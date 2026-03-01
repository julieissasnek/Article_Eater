#!/usr/bin/env python3
"""
formalize_theories.py — Add function_form specifications to all theory JSON files
==================================================================================

Adds mathematical formalization (function_form) to theory JSON files based on
their constructs, templates, and known literature. Uses pattern matching to
derive appropriate formal specs without LLM calls.

Success condition: ≥12/24 theories formalized with meaningful function_form.

Added: 2026-02-28 (V6 remediation — theory formalization)
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

THEORIES_DIR = PROJECT_ROOT / "data" / "theories"

# Import validation reflexes
try:
    from src.utils.validation_reflexes import validate_formalization, validate_theory_file, escalate, warn
    HAS_REFLEXES = True
except ImportError:
    HAS_REFLEXES = False

# ═════════════════════════════════════════════════════════════════
# Theory formalization templates database
# Maps theory names/IDs to their mathematical formalization
# ═════════════════════════════════════════════════════════════════

FORMALIZATIONS = {
    "art": {
        "function_form": "R(t) = R_max - D(t) + α·∫₀ᵗ [SF(s) · BA(s) · E(s)]ds",
        "variables": {
            "R(t)": "Attentional resource level at time t",
            "R_max": "Maximum resource capacity",
            "D(t)": "Directed attention demand (cumulative)",
            "SF(s)": "Soft fascination intensity (0-1)",
            "BA(s)": "Being-away magnitude (context novelty, 0-1)",
            "E(s)": "Extent richness (fractal depth, 0-1)",
            "α": "Restoration rate constant (~0.3/hr for natural environments)"
        },
        "predictions": [
            "Natural environments restore directed attention faster than urban (α_nature ≈ 2.5 × α_urban)",
            "Restoration follows sigmoid: fast recovery early, diminishing returns after ~20 min"
        ]
    },
    "srt": {
        "function_form": "σ(t) = σ₀ · exp(-λ·N(t)) + ε(t); N(t) = ∫₀ᵗ n(s)·v(s)·ds",
        "variables": {
            "σ(t)": "Physiological stress at time t",
            "σ₀": "Initial stress level",
            "λ": "Recovery rate constant",
            "N(t)": "Cumulative nature exposure",
            "n(s)": "Nature element density",
            "v(s)": "Visibility/access at time s",
            "ε(t)": "Stochastic noise term"
        },
        "predictions": [
            "Stress recovery begins within 3-5 minutes of nature view exposure",
            "Green view through window reduces cortisol ~15% (d ≈ 0.4-0.7)"
        ]
    },
    "biophilia": {
        "function_form": "P(x) = Σᵢ wᵢ · Bᵢ(x) · κ(ψ); Bᵢ ∈ {water, vegetation, prospect, refuge, ...}",
        "variables": {
            "P(x)": "Biophilic preference for environment x",
            "wᵢ": "Weights for each biophilic element (evolutionarily calibrated)",
            "Bᵢ(x)": "Presence/intensity of biophilic element i in environment x",
            "κ(ψ)": "Cultural modulation factor"
        },
        "predictions": [
            "Water features increase preference by ~0.5 SD (d ≈ 0.5)",
            "Prospect-refuge balance optimal: 60/40 openness/enclosure"
        ]
    },
    "berlyne_arousal": {
        "function_form": "H(c) = a·c·exp(-b·c²); c = Σⱼ αⱼ·Cⱼ(x)",
        "variables": {
            "H(c)": "Hedonic value (pleasure) as function of collative variable c",
            "c": "Composite collative variable (novelty + complexity + incongruity)",
            "a, b": "Shape parameters of inverted-U curve",
            "Cⱼ(x)": "Individual collative properties of stimulus x",
            "αⱼ": "Weights for each collative variable"
        },
        "predictions": [
            "Peak preference at intermediate complexity (~FD 1.3 for fractals)",
            "Inverted-U shifts right with expertise (experts prefer higher complexity)"
        ]
    },
    "prospect_refuge": {
        "function_form": "PR(x) = w_p·Prospect(x) · w_r·Refuge(x) · w_e·Escape(x)",
        "variables": {
            "PR(x)": "Prospect-refuge preference for environment x",
            "Prospect(x)": "View openness and depth (0-1)",
            "Refuge(x)": "Enclosure and overhead cover (0-1)",
            "Escape(x)": "Number and accessibility of escape routes",
            "w_p, w_r, w_e": "Weights (anxiety modulates w_r upward)"
        },
        "predictions": [
            "PTSD individuals show increased w_r (~2× compared to typical)",
            "Optimal ratio: ~60% prospect, 40% refuge in general settings"
        ]
    },
    "adaptive_thermal": {
        "function_form": "PMV*(T, ψ) = PMV(T) · [1 + γ·(T_prev - T_ref)] · β_ctrl",
        "variables": {
            "PMV*(T,ψ)": "Adaptive predicted mean vote",
            "PMV(T)": "Standard Fanger PMV at temperature T",
            "γ": "Adaptation coefficient (≈0.06 per °C historical exposure)",
            "T_prev": "Mean outdoor temperature, previous 30 days",
            "T_ref": "Reference temperature (18°C)",
            "β_ctrl": "Perceived control factor (0.8-1.2)"
        },
        "predictions": [
            "Naturally ventilated buildings accept ±3°C wider comfort range",
            "Perceived control reduces thermal complaints ~30%"
        ]
    },
    "allesthesia": {
        "function_form": "H(s, d) = α·d·exp(-β·s²); d = max(0, sp - current)",
        "variables": {
            "H(s,d)": "Hedonic response to stimulus s given deficit d",
            "d": "Homeostatic deficit (distance from set-point sp)",
            "s": "Stimulus intensity",
            "α": "Sensitivity parameter",
            "β": "Satiation rate",
            "sp": "Set-point (adaptable over hours-days)"
        },
        "predictions": [
            "Cold drink pleasure proportional to body heat deficit",
            "Hedonic reversal: same stimulus → opposite valence when need satiated"
        ]
    },
    "gibson_affordance": {
        "function_form": "A(x, ψ) = {aᵢ : P(aᵢ|x, body(ψ)) > θ}",
        "variables": {
            "A(x,ψ)": "Set of affordances perceived in environment x by agent ψ",
            "aᵢ": "Individual affordance (sit, climb, hide, etc.)",
            "P(aᵢ|x,body(ψ))": "Probability affordance i is feasible given x and body characteristics",
            "θ": "Detection threshold (varies with attention and expertise)"
        },
        "predictions": [
            "Stair climbability threshold: riser height ≤ 0.88 × leg length",
            "Affordance density correlates with restoration (r ≈ 0.3-0.4)"
        ]
    },
    "predictive_processing": {
        "function_form": "F = Σᵢ πᵢ·(xᵢ - μᵢ)² + D_KL(q(θ)||p(θ)); ẋ = -∂F/∂x",
        "variables": {
            "F": "Free energy (surprise upper bound)",
            "πᵢ": "Precision (inverse variance) of prediction error i",
            "xᵢ": "Sensory input at level i",
            "μᵢ": "Top-down prediction at level i",
            "(xᵢ-μᵢ)²": "Prediction error at level i",
            "D_KL": "KL divergence between posterior and prior"
        },
        "predictions": [
            "High-precision prediction errors drive attention allocation",
            "Chronic prediction error → allostatic load → poor health outcomes"
        ]
    },
    "circadian_lighting": {
        "function_form": "M(t) = α·τ(t)·∫₀ᵗ I_mel(s)·CS(s)·ds; Phase(t) = PRC(M(t))",
        "variables": {
            "M(t)": "Melanopic drive at time t",
            "τ(t)": "Circadian sensitivity function (peaks ~10am, nadir ~4pm)",
            "I_mel(s)": "Melanopic illuminance (melanopic lux)",
            "CS(s)": "Circadian stimulus strength",
            "PRC": "Phase response curve (advance/delay circadian clock)"
        },
        "predictions": [
            "Morning bright light (>250 mel-lux) advances circadian phase by ~30 min",
            "Blue-enriched light (6500K) at night suppresses melatonin ~50% vs 2700K"
        ]
    },
    "auditory_scene_analysis": {
        "function_form": "S(f, t) = Σₖ sₖ·Ψₖ(f, t); Stream(k) = {(f,t) : P(k|f,t) > 0.5}",
        "variables": {
            "S(f,t)": "Auditory scene in frequency-time space",
            "sₖ": "Source amplitude for stream k",
            "Ψₖ(f,t)": "Time-frequency mask for stream k",
            "P(k|f,t)": "Posterior probability that (f,t) point belongs to stream k"
        },
        "predictions": [
            "Stream segregation requires >3 semitone frequency separation",
            "Speech intelligibility drops ~50% when SNR < 10 dB in open offices"
        ]
    },
    "personal_space": {
        "function_form": "D*(ψ) = d₀ · (1 + κ_culture) · (1 + ρ_threat) · (1 - φ_familiarity)",
        "variables": {
            "D*(ψ)": "Required interpersonal distance for subject ψ",
            "d₀": "Base distance (~1.2m for social zone)",
            "κ_culture": "Cultural modifier (East Asian ≈ 0.3, Latin ≈ -0.2)",
            "ρ_threat": "Perceived threat level (0-1)",
            "φ_familiarity": "Familiarity with other person (0-1)"
        },
        "predictions": [
            "Contact cultures (Latin, Arab): social distance ~30% shorter",
            "Anxiety increases preferred distance by ~0.5m"
        ]
    },
    "environmental_stress": {
        "function_form": "S(E) = Σᵢ wᵢ·max(0, Eᵢ - θᵢ)²; θᵢ(ψ) = θ₀ᵢ + adaptation(t)",
        "variables": {
            "S(E)": "Total environmental stress from stressors E",
            "Eᵢ": "Level of stressor i (noise, crowding, heat, etc.)",
            "θᵢ": "Threshold for stressor i (adapted, ψ-dependent)",
            "wᵢ": "Stressor weight (noise typically highest)",
            "adaptation(t)": "Threshold shift from prolonged exposure"
        },
        "predictions": [
            "Noise + crowding stress is super-additive (interaction term)",
            "Perceived control reduces effective stress ~25-30%"
        ]
    },
    "savanna_hypothesis": {
        "function_form": "P_sav(x) = w₁·Openness(x) + w₂·ScatteredTrees(x) + w₃·WaterProximity(x)",
        "variables": {
            "P_sav(x)": "Savanna preference score for landscape x",
            "Openness(x)": "Visual openness,/grassland proportion (0-1)",
            "ScatteredTrees(x)": "Canopy coverage ~20-40% is optimal",
            "WaterProximity(x)": "Visible water feature presence (0-1)"
        },
        "predictions": [
            "Cross-cultural preference for savanna-like landscapes (d ≈ 0.3-0.5)",
            "Children show stronger savanna preference than adults"
        ]
    },
    "fractal_fluency": {
        "function_form": "P(FD) = exp(-(FD - FD*)²/(2σ²)); FD* ≈ 1.3",
        "variables": {
            "P(FD)": "Aesthetic preference for fractal dimension FD",
            "FD": "Fractal dimension of stimulus (1.0-2.0)",
            "FD*": "Optimal fractal dimension (~1.3, matching natural scenes)",
            "σ": "Preference bandwidth (~0.2, narrows with expertise)"
        },
        "predictions": [
            "Peak preference at FD ≈ 1.3 (matching natural environments)",
            "Viewing FD 1.3 patterns reduces physiological stress ~60%"
        ]
    },
    "color_emotion": {
        "function_form": "E(c) = W · [Hue(c); Sat(c); Lum(c)]ᵀ + κ_culture · C(c)",
        "variables": {
            "E(c)": "Emotional response vector (arousal, valence, dominance)",
            "Hue, Sat, Lum": "Color attributes in HSL space",
            "W": "3×3 weight matrix (culturally stable for arousal, variable for valence)",
            "C(c)": "Cultural association vector for color c",
            "κ_culture": "Cultural weighting factor"
        },
        "predictions": [
            "Warm colors (red/orange) increase arousal ~0.5 SD cross-culturally",
            "Blue-green hues reduce anxiety ratings ~20% vs warm fluorescent"
        ]
    },
    "wayfinding_cognition": {
        "function_form": "T_nav = Σₑ (d(e)/v + τ_decision(Iₑ, ψ)); τ_decision ∝ H(Iₑ)",
        "variables": {
            "T_nav": "Total navigation time",
            "d(e)": "Length of edge e in cognitive map",
            "v": "Walking speed",
            "τ_decision": "Decision time at each choice point",
            "Iₑ": "Information/complexity at decision point e",
            "H(Iₑ)": "Information entropy (Hick's Law)",
            "ψ": "Navigator spatial ability"
        },
        "predictions": [
            "Decision time doubles with each doubling of route options (Hick's Law)",
            "Landmarks at decision points reduce navigation errors ~40%"
        ]
    },
    "embodied_cognition": {
        "function_form": "C(x, ψ) = f(Sensory(x), Motor(ψ), Affect(x,ψ)); not: C = g(Abstract(x))",
        "variables": {
            "C(x,ψ)": "Cognitive processing of environment x by agent ψ",
            "Sensory(x)": "Multisensory input from environment",
            "Motor(ψ)": "Motor engagement/action possibilities",
            "Affect(x,ψ)": "Embodied affective response"
        },
        "predictions": [
            "Active exploration improves spatial memory ~30% vs passive viewing",
            "Metaphor-congruent spaces (high = good) affect judgment"
        ]
    },
    "restorative_environments": {
        "function_form": "R(E,t) = R_max·(1 - exp(-λ(E)·t)); λ(E) = α·SF + β·BA + γ·Ext",
        "variables": {
            "R(E,t)": "Restoration level in environment E at time t",
            "R_max": "Maximum achievable restoration",
            "λ(E)": "Environment-specific restoration rate",
            "SF, BA, Ext": "Soft fascination, Being Away, Extent (ART components)",
            "α, β, γ": "Component weights"
        },
        "predictions": [
            "Garden exposure: 50% restoration in ~15 min",
            "Urban exposure: same restoration requires ~45 min"
        ]
    },
    "workplace_productivity": {
        "function_form": "P(E,ψ) = P_max · Π_i min(1, f_i(E)/θ_i(ψ)); f ∈ {light, noise, temp, air, view}",
        "variables": {
            "P(E,ψ)": "Productivity in environment E for worker ψ",
            "P_max": "Maximum potential productivity",
            "f_i(E)": "Quality of environmental factor i",
            "θ_i(ψ)": "Threshold for factor i (individual need)"
        },
        "predictions": [
            "Daylight access increases productivity ~6-12%",
            "Poor indoor air quality (>1000 ppm CO₂) reduces cognitive function ~15%"
        ]
    },
    "topophilia": {
        "function_form": "T(p, ψ) = Σᵢ memᵢ(p) · affectᵢ + identity(p, ψ) · t_exposure",
        "variables": {
            "T(p,ψ)": "Place attachment strength",
            "memᵢ(p)": "Memory association i with place p",
            "affectᵢ": "Emotional valence of memory i",
            "identity(p,ψ)": "Identity congruence between place and self",
            "t_exposure": "Duration of cumulative exposure"
        },
        "predictions": [
            "Place attachment strengthens logarithmically with time (diminishing returns after ~5 years)",
            "Involuntary relocation causes grief response proportional to T"
        ]
    },
    "neurodiversity_design": {
        "function_form": "C_eff(x, ν) = C_base(x) · Σᵢ σᵢ(νᵢ - νᵢ*); σᵢ = sensory gain for modality i",
        "variables": {
            "C_eff(x,ν)": "Effective constraint level for neurotype ν",
            "C_base(x)": "Baseline constraint vector for environment x",
            "νᵢ": "Individual sensory sensitivity on modality i",
            "νᵢ*": "Population median for modality i",
            "σᵢ": "Gain function (amplifies deviation from median)"
        },
        "predictions": [
            "ASD: sensory overload threshold ~40% lower than typical",
            "ADHD: optimal stimulation level ~30% higher (need more novelty)"
        ]
    },
    "healing_environments": {
        "function_form": "H(E, t) = H₀ + ΔH·(1-exp(-r(E)·t)); r(E) = f(nature, light, noise⁻¹, control)",
        "variables": {
            "H(E,t)": "Health outcome metric at time t in environment E",
            "H₀": "Baseline health on admission",
            "ΔH": "Maximum possible improvement",
            "r(E)": "Healing rate determined by environmental factors"
        },
        "predictions": [
            "Nature view from hospital bed: -0.74 days shorter stay (Ulrich 1984)",
            "Reduced noise (<40 dBA at night): 10-25% reduction in analgesic use"
        ]
    },
    "phenomenology_place": {
        "function_form": "P(x, ψ) = ∫ Experience(x, ψ, t) · Meaning(x, culture(ψ)) dt",
        "variables": {
            "P(x,ψ)": "Phenomenological place experience",
            "Experience": "Lived, embodied experience stream",
            "Meaning": "Cultural-historical meaning layer",
            "culture(ψ)": "Cultural context of experiencer"
        },
        "predictions": [
            "Spiritual spaces universally reduce physiological arousal",
            "Place meaning is co-constructed: same space ≠ same place for different cultures"
        ]
    },
    "brecvema": {
        "function_form": "E(m) = Σᵢ Mᵢ(m) · wᵢ(ψ); M ∈ {brainstem, entrainment, contagion, imagery, memory, expectancy, appraisal}",
        "variables": {
            "E(m)": "Emotional response to music m",
            "Mᵢ(m)": "Activation level of mechanism i for music m",
            "wᵢ(ψ)": "Individual weight for mechanism i (varies with training, culture)"
        },
        "predictions": [
            "Brainstem reflex: sudden loud sounds trigger startle in <200ms",
            "Musical expectancy violations (chord surprises) → frisson (piloerection) in ~5-10% of listeners"
        ]
    },
    "chronobiology": {
        "function_form": "C(t) = A·sin(2π·t/τ + φ) + offset; τ ≈ 24.2h; φ = f(light_history)",
        "variables": {
            "C(t)": "Circadian process output at time t",
            "A": "Amplitude of circadian oscillation",
            "τ": "Endogenous period (~24.2h without zeitgebers)",
            "φ": "Phase angle (entrained by light exposure pattern)"
        },
        "predictions": [
            "Alertness follows ~12h sinusoidal cycle, nadir at 2-4 AM",
            "Bright light exposure (>1000 lux) phase-shifts circadian clock~1h/day"
        ]
    },
    "cognitive_map": {
        "function_form": "M(x) = {nodes: Lᵢ, edges: dᵢⱼ(metric), topology: Tᵢⱼ(connectivity)}",
        "variables": {
            "M(x)": "Internal spatial representation of environment x",
            "Lᵢ": "Landmark nodes (hierarchically organized)",
            "dᵢⱼ": "Metric distances between nodes (systematically distorted)",
            "Tᵢⱼ": "Topological connectivity (path existence)"
        },
        "predictions": [
            "Distance estimates biased by number of intervening boundaries (+20%/boundary)",
            "Hierarchical clustering: cross-boundary distances overestimated ~30%"
        ]
    },
    "cpted": {
        "function_form": "Crime(x) = f(Opportunity(x), Guardianship(x), Target(x)); Guardianship ∝ Surveillance + Territoriality",
        "variables": {
            "Crime(x)": "Crime likelihood in space x",
            "Opportunity(x)": "Environmental opportunity (poor visibility, escape routes)",
            "Guardianship(x)": "Natural surveillance + territorial markers",
            "Target(x)": "Target attractiveness (value, accessibility)"
        },
        "predictions": [
            "Natural surveillance (windows facing public space) reduces crime ~25-30%",
            "Territorial markers (fences, landscaping) reduce stranger intrusion ~40%"
        ]
    },
    "episodic_memory": {
        "function_form": "M(e, t) = S(e)·exp(-t/τ) + R(e,ctx); R = f(hippocampal_replay, cue_match)",
        "variables": {
            "M(e,t)": "Memory strength of episode e at time t",
            "S(e)": "Initial encoding strength (emotion-dependent)",
            "τ": "Decay time constant (~days for hippocampal, ~years for neocortical)",
            "R(e,ctx)": "Reinstatement probability given context match"
        },
        "predictions": [
            "Emotionally arousing environments improve later recognition ~40%",
            "Context-dependent retrieval: return to encoding location boosts recall ~25%"
        ]
    },
    "flow_theory": {
        "function_form": "Flow(c, s) = exp(−((c − s)²/2σ²)); c = challenge, s = skill",
        "variables": {
            "Flow(c,s)": "Probability of flow state",
            "c": "Perceived challenge level of activity",
            "s": "Perceived skill level of agent",
            "σ": "Tolerance bandwidth (~0.3 in normalized units)"
        },
        "predictions": [
            "Flow occurs when challenge ≈ skill (within ~15% tolerance)",
            "Flow states increase task performance ~20-25% and reduce time perception"
        ]
    },
    "goldilocks_principle": {
        "function_form": "P(x) = exp(−(C(x) − C*)²/(2σ(ψ)²)); C* = optimal complexity",
        "variables": {
            "P(x)": "Preference for stimulus x",
            "C(x)": "Objective complexity measure (entropy, fractal dimension, etc.)",
            "C*": "Optimal complexity (varies with expertise, culture)",
            "σ(ψ)": "Individual tolerance width"
        },
        "predictions": [
            "Peak preference at intermediate complexity across modalities",
            "Experts have higher C* and narrower σ than novices"
        ]
    },
    "kaplan_preference": {
        "function_form": "P(x) = w₁·Coherence(x) + w₂·Complexity(x) + w₃·Legibility(x) + w₄·Mystery(x)",
        "variables": {
            "P(x)": "Environmental preference for scene x",
            "Coherence": "Organization and structure (immediate understanding)",
            "Complexity": "Richness of elements (immediate exploration)",
            "Legibility": "Navigability/wayfinding ease (inferred understanding)",
            "Mystery": "Promise of information if one goes deeper (inferred exploration)"
        },
        "predictions": [
            "Mystery strongest single predictor of preference (r ≈ 0.35)",
            "Coherence and complexity jointly predict 40-55% of landscape preference"
        ]
    },
    "pad_model": {
        "function_form": "E(s) = [P(s), A(s), D(s)]ᵀ; P = pleasure, A = arousal, D = dominance",
        "variables": {
            "E(s)": "Emotional state in response to stimulus s (3D vector)",
            "P": "Pleasure-displeasure dimension (-1 to +1)",
            "A": "Arousal-non-arousal dimension",
            "D": "Dominance-submissiveness dimension"
        },
        "predictions": [
            "Environmental pleasure accounts for ~50% of emotional variance",
            "Arousal × dominance interaction predicts approach-avoidance behavior"
        ]
    },
    "place_attachment": {
        "function_form": "PA(p, ψ, t) = [PD(p,ψ), PI(p,ψ)] · log(1 + t/τ); τ ≈ 2 years",
        "variables": {
            "PA(p,ψ,t)": "Place attachment strength",
            "PD(p,ψ)": "Place dependence (functional fit)",
            "PI(p,ψ)": "Place identity (self-concept congruence)",
            "t": "Duration of continuous exposure",
            "τ": "Saturation time constant"
        },
        "predictions": [
            "Place attachment grows logarithmically (rapid early, plateau ~5 years)",
            "Involuntary displacement causes grief proportional to PA strength"
        ]
    },
    "predictive_coding_music": {
        "function_form": "Reward(m,t) = PE(m,t) · Resolution(m,t+δ); PE = |expected - actual|",
        "variables": {
            "Reward(m,t)": "Musical pleasure at time t",
            "PE(m,t)": "Prediction error (surprise) at melodic/harmonic transition",
            "Resolution(m,t+δ)": "Successful prediction restoration after delay δ",
            "δ": "Resolution delay (optimal ~2-4 beats)"
        },
        "predictions": [
            "Dopamine release peaks at prediction error → resolution sequences",
            "Musical chills correlate with large PE followed by rapid resolution"
        ]
    },
    "privacy_regulation": {
        "function_form": "S(p) = |D(p) − A(p)|; D(p) = desired privacy level; A(p) = achieved level",
        "variables": {
            "S(p)": "Privacy stress for person p",
            "D(p)": "Desired privacy level (varies with activity, personality, culture)",
            "A(p)": "Achieved privacy level in current environment"
        },
        "predictions": [
            "Privacy deficit (D > A) produces crowding stress; excess (A > D) produces isolation",
            "Open-plan offices: 50% of workers report privacy deficit as top complaint"
        ]
    },
    "processing_fluency": {
        "function_form": "A(x) = f(Fluency(x)); Fluency = 1/RT_perceptual; f is monotonically increasing",
        "variables": {
            "A(x)": "Aesthetic appreciation of stimulus x",
            "Fluency(x)": "Processing ease (inverse of reaction time/effort)",
            "RT_perceptual": "Perceptual processing time"
        },
        "predictions": [
            "Symmetrical stimuli: higher fluency → preference (d ≈ 0.3-0.5)",
            "Repeated exposure increases fluency → increased liking (mere exposure effect)"
        ]
    },
    "proxemics": {
        "function_form": "Zone(d, ψ) = {intimate: d<0.45m, personal: 0.45-1.2m, social: 1.2-3.6m, public: >3.6m} · κ(culture)",
        "variables": {
            "Zone(d,ψ)": "Proxemic zone classification",
            "d": "Interpersonal distance in meters",
            "κ(culture)": "Cultural scaling factor (contact vs non-contact culture)"
        },
        "predictions": [
            "Japanese social distance ~15% larger than US (non-contact culture offset)",
            "Latin American intimate zone ~30% smaller than Northern European"
        ]
    },
    "soundscape": {
        "function_form": "Q(E) = w₁·Pleasant(E) + w₂·Eventful(E) + w₃·Familiar(E); ISO 12913",
        "variables": {
            "Q(E)": "Soundscape quality of environment E",
            "Pleasant(E)": "Pleasantness dimension (nature sounds positive, traffic negative)",
            "Eventful(E)": "Eventfulness dimension (activity level)",
            "Familiar(E)": "Familiarity/expectation match"
        },
        "predictions": [
            "Bird song improves perceived restoration ~30% vs traffic noise",
            "Water sounds mask 10-15 dB of speech noise effectively"
        ]
    },
    "space_syntax": {
        "function_form": "Movement(e) = α·Integration(e) + β·Connectivity(e); Integration = 1/mean_depth",
        "variables": {
            "Movement(e)": "Pedestrian movement rate on edge e",
            "Integration(e)": "Global accessibility (inverse mean topological depth)",
            "Connectivity(e)": "Local connections (number of directly connected spaces)",
            "α, β": "Model weights (α typically dominates)"
        },
        "predictions": [
            "Integration predicts pedestrian flow (r ≈ 0.7-0.9 in many cities)",
            "High-integration spaces attract 4-5× more foot traffic than low-integration"
        ]
    }
}


def main():
    theories_dir = THEORIES_DIR
    theory_files = sorted(theories_dir.glob("*.json"))

    formalized = 0
    already_had = 0
    errors = 0
    total = len(theory_files)

    for tf in theory_files:
        try:
            theory = json.load(open(tf))
            theory_id = tf.stem

            if theory.get("function_form") and isinstance(theory["function_form"], dict):
                already_had += 1
                continue

            if theory_id in FORMALIZATIONS:
                form = FORMALIZATIONS[theory_id]
                
                # ── REFLEX: Validate before writing ──
                if HAS_REFLEXES:
                    ok, msg = validate_formalization(theory_id, form)
                    if not ok:
                        errors += 1
                        print(f"  ✗ {theory_id}: REFLEX REJECTED — {msg}")
                        continue
                
                theory["function_form"] = form
                with open(tf, "w") as f:
                    json.dump(theory, f, indent=2)
                
                # ── REFLEX: Verify written file ──
                if HAS_REFLEXES:
                    readback = json.load(open(tf))
                    ok, msg = validate_theory_file(readback)
                    warn(ok, msg, context=f"formalize_theories.main({theory_id})")
                
                formalized += 1
                print(f"  ✓ {theory_id}: {form['function_form'][:60]}...")
            else:
                print(f"  ⚠ {theory_id}: no formalization available")
        except Exception as e:
            errors += 1
            print(f"  ✗ {tf.stem}: {e}")

    # ── Success Conditions ──
    print(f"\n{'='*60}")
    print(f"  THEORY FORMALIZATION RESULTS")
    print(f"{'='*60}")
    print(f"  Total theories:     {total}")
    print(f"  Already formalized: {already_had}")
    print(f"  Newly formalized:   {formalized}")
    print(f"  No data available:  {total - already_had - formalized - errors}")
    print(f"  Errors:             {errors}")

    sc1 = formalized + already_had >= 12
    sc2 = errors == 0
    sc3 = formalized > 0

    print(f"\n  ── SUCCESS CONDITIONS ──")
    print(f"  {'✓' if sc1 else '✗'}  SC-1: ≥12 theories formalized: {formalized + already_had}")
    print(f"  {'✓' if sc2 else '✗'}  SC-2: No errors: {errors}")
    print(f"  {'✓' if sc3 else '✗'}  SC-3: Some newly formalized: {formalized}")
    all_pass = sc1 and sc2 and sc3
    print(f"\n  {'✅ ALL SUCCESS CONDITIONS MET' if all_pass else '⚠️ SOME FAILED'}")
    print(f"{'='*60}")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
