
# CNfA Aesthetics Appraisal Framework
## Dynamical Model + Ontology Tiering + Internal Critique

Version: Recreated Edition

---

# Part A — Dynamical Interaction Model

## A1. State Vector

Let appraisal/constraint hubs be:

a(t) = [F, C, S, T, P, R, A, G]^T

F = Fluency  
C = Complexity regulation (load/arousal pressure)  
S = Predictability/Surprise (prediction error)  
T = Threat/Safety (higher = more threat)  
P = Prospect/Refuge/Control  
R = Restorativeness  
A = Affordance Fit  
G = Social Signaling  

Features: x  
Moderators: m  

Initial activation:

a(0) = σ(Wx x + Wm m + b)

σ = bounded nonlinearity (logistic/tanh)

---

## A2. Coupled Dynamics

da/dt = −D a + φ(K a + U u(t))

D = decay (habituation)  
K = hub↔hub coupling matrix  
u(t) = time-varying inputs  
φ = bounded nonlinearity  

Example signed structure in K:

F → T : negative  
P → T : negative  
S → T : positive at high levels  
T → F : negative  
C → F : negative  
F → C : negative  
R → T : negative  
A → F : positive  

---

## A3. Affect Layer

y(t) = ψ(Wa a(t) + c)

Pleasure ↑ with F, P, R, A  
Pleasure ↓ with T  

Interest = exp(-(S-μS)^2 / 2σS^2) + exp(-(C-μC)^2 / 2σC^2)

Calm ↑ with R, P, F  
Arousal ↑ with C, S, T  

---

## A4. Behavioral Outputs

Approach ≈ logistic(Pleasure − Threat + AffordanceFit)

Dwell time: hazard decreases with Interest, increases with boredom

EDA ↑ with Arousal, Threat  
HRV ↓ with Threat  

---

# Part B — Ontology Tiering for Master Repo

## Tier 0 (Reports / Outputs)

Beauty_report  
Preference_report  
Aesthetic_rating  

Not causal hubs — measurement nodes only.

---

## Tier 1A (Core Mechanistic Hubs)

ThreatSafety  
ProcessingFluency  
PredictabilitySurprise  
ComplexityRegulation  
AffordanceFit  

---

## Tier 1B (Core but Context-Heavier)

Restorativeness  
ProspectRefugeControl  
SocialSignaling  

---

## Tier 2 (Stable Subfactors)

Under Fluency:
- Coherence
- Symmetry grouping
- Schema congruence

Under Threat:
- Darkness
- Escape clarity
- Entrapment cues

Under Complexity:
- Multiscale entropy
- Clutter density

Under Predictability:
- Prediction error magnitude

Under AffordanceFit:
- Wayfinding clarity
- Action invitation strength

Under SocialSignaling:
- Monumentality
- Craft precision
- Material cost cues

---

## Tier 3 (Feature Families)

Geometry metrics  
Visibility graph metrics  
Entropy/fractal measures  
Light metrics  
Material proxies  
Biophilic indices  
Acoustic metrics  

---

## Elevation Rule

Promote to Tier 1 only if:

1. Cross-context  
2. Intervention leverage  
3. Measurable proxy  
4. Adds BN predictive power  

---

# Part C — Internal Critique

## C1. “These are constraints, not appraisals.”

Define evaluation functionally:
A process is evaluative if it generates direction-sensitive control signals (approach/avoid, attention allocation, resource conservation).

Rename optionally:
AppraisalHub ↔ ConstraintHub.

---

## C2. “Beauty has independent explanatory force.”

Test:
If two spaces produce identical appraisal vectors but different beauty ratings, framework incomplete.

---

## C3. Cultural variability challenge

Address via hierarchical moderators and CPD shifts.

---

## C4. Non-separability challenge

Test selective manipulation per hub.
If no selective manipulation possible → decomposition flawed.

---

## C5. Vision-centric bias

Extend feature vector x to multimodal inputs (acoustic, thermal, social density).

---

# Minimal Definitions

Constraint Hub:
System-level variable summarizing how multiple low-level computations bias attention, affect, and action.

Functional Evaluation:
Process that generates direction-sensitive modulation relative to goals.

Dynamic BN:
Bayesian network unrolled across time slices with temporal edges.
