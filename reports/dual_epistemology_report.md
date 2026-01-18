# Dual Epistemology Analysis
## Comparing Foundationalist vs Coherentist Frameworks
### Corpus: 17 papers

---

## 1. Theory Credences

| Theory | Foundationalist | Coherentist | Difference |
|--------|-----------------|-------------|------------|
| ART                  | 0.94 | 0.75 | ↓ 0.19 |
| SRT                  | 0.95 | 0.87 | ↓ 0.08 |
| Biophilia            | 0.95 | 0.80 | ↓ 0.15 |
| Perceptual_Fluency   | 0.94 | 0.85 | ↓ 0.09 |
| Predictive_Processing | 0.64 | 0.78 | ↑ 0.14 |
| Embodied_Cognition   | 0.95 | 0.70 | ↓ 0.25 |

## 2. Research Priority Rankings

| Rank | Foundationalist | Coherentist |
|------|-----------------|-------------|
| 1 | Predictive_Processing | ART |
| 2 | ART | Embodied_Cognition |
| 3 | Perceptual_Fluency | Biophilia |
| 4 | Embodied_Cognition | Predictive_Processing |
| 5 | Biophilia | Perceptual_Fluency |
| 6 | SRT | SRT |

## 3. Key Divergences

### Credence Divergences
- **Embodied_Cognition**: foundationalist higher by 0.25
- **ART**: foundationalist higher by 0.19
- **Biophilia**: foundationalist higher by 0.15

### Priority Divergences
- **Predictive_Processing**: ranked #1 (found.) vs #4 (coher.)
- **Perceptual_Fluency**: ranked #3 (found.) vs #5 (coher.)
- **Embodied_Cognition**: ranked #4 (found.) vs #2 (coher.)

## 4. Philosophical Implications

- The foundationalist model yields higher average credences. This may occur when the coherentist model detects tensions between theories that the foundationalist model doesn't track.
- The frameworks disagree most about Predictive_Processing: foundationalist ranks it #1 while coherentist ranks it #4. This suggests the frameworks would recommend different experiments.
- Embodied_Cognition shows lower credence in the coherentist model (0.70 vs 0.95). This may indicate tension with other beliefs in the web.

---

## 5. What This Means for Research

The two frameworks would recommend different next studies:

**Foundationalist recommendation:** Study Predictive_Processing
  - Reason: Evidence count: 1, Support ratio: 1.00
  - Logic: Prioritize theories with least evidence (simple counting)

**Coherentist recommendation:** Study ART
  - Reason: Credence: 0.75, Entrenchment: 0.21
  - Logic: Prioritize where belief revision would most affect the web

---

## 6. Teaching Point

This comparison demonstrates that **epistemological assumptions are not neutral**.
The choice between foundationalism and coherentism affects:

1. How we aggregate evidence
2. Which theories we consider well-supported
3. What research we prioritize
4. How we handle findings that don't fit existing theories

Neither framework is 'correct' — they embody different philosophical commitments
about how knowledge is structured and justified.

---

# Expert Panel Commentary


## Key Finding: Systematic Credence Gap

The foundationalist model gives HIGHER credences to most theories (0.94-0.95) 
while the coherentist model is more conservative (0.70-0.87).

### Glymour (Philosophy of Science):

"This is exactly what you'd expect. The foundationalist counts evidence 
additively — each supporting paper raises confidence. But the coherentist 
asks: 'Does this theory cohere with everything else we believe?' 

Embodied Cognition shows the largest gap (0.95 vs 0.70). Why? In the 
foundationalist model, 4 papers citing it = high confidence. But the 
coherentist notes that Embodied Cognition makes claims that sit uneasily 
with the more reductionist assumptions of SRT (which grounds stress 
recovery in autonomic physiology, not body-environment coupling).

The coherentist model is detecting a latent tension the foundationalist 
model ignores."

### Hartmann (Bayesian Epistemology):

"The priority divergence is pedagogically valuable. Consider:

- Foundationalist says: 'Study Predictive Processing — only 1 paper!'
- Coherentist says: 'Study ART — moderate credence, low entrenchment'

These reflect different research strategies:

1. FOUNDATIONALIST: Fill gaps in evidence coverage (sampling logic)
2. COHERENTIST: Maximize information gain for the whole web (VOI logic)

The foundationalist treats each theory independently. The coherentist 
recognizes that a result on ART would propagate through the web — it 
would affect Biophilia (which shares evolutionary grounding) and 
potentially SRT (via shared attention/stress mechanisms)."

### Solomon (Social Epistemology):

"I'm struck by the Predictive Processing case. Foundationalist ranks it #1 
priority (least evidence), coherentist ranks it #4.

Why? The coherentist model assigns it 0.78 credence despite only 1 paper 
in this corpus. That's because Predictive Processing is a FRAMEWORK belief 
in the coherentist model — it has high prior credence from outside this 
domain (neuroscience, cognitive science) that the foundationalist model 
doesn't capture.

This illustrates that coherentism naturally handles cross-domain evidence 
flow, while foundationalism is trapped within the corpus."

### Ulrich (Domain Expert):

"From a practical standpoint, the coherentist recommendation to study ART 
makes more sense. We have good reason to believe ART is true (Kaplan's 
original work, decades of environmental psychology), but the CNFA-specific 
evidence in this corpus is sparse.

The foundationalist is right that Predictive Processing has little direct 
evidence, but that's partly because it's newer and partly because it's 
imported from another field. Rushing to test it in CNFA might be premature 
if we haven't established the basic phenomena it's meant to explain."

## Summary Table

| Divergence | What It Reveals |
|------------|-----------------|
| Higher foundationalist credences | Coherentist detects cross-theory tensions |
| Embodied Cognition gap (0.25) | Tension with physiological reductionism of SRT |
| Predictive Processing priority flip | Cross-domain priors vs. within-corpus counting |
| ART as coherentist priority | Low entrenchment = high potential for web-wide updates |

## Lecture Takeaway

When we teach students to synthesize evidence, we're implicitly teaching 
them an epistemology. The choice matters:

- If you think evidence accumulates independently → use meta-analysis
- If you think beliefs constrain each other → use coherence methods
- If you think some beliefs are more revisable → track entrenchment
- If you want to plan research → compute VOI, not just count gaps

The Article Eater system makes these choices explicit and computable.
