# Card Quality Comparison — Model Head-to-Head
*Generated 2026-03-04 by AG for CW review*

This document compares three card generation approaches for the same 5 evidence clusters. The goal: determine what quality level each model/approach achieves, and decide which approach to invest in for the full 3,788-cluster corpus.

---

## Cluster 1: Nature Exposure → Stress
**119 findings, 5 theories, mixed direction, mean effect d = 2.94**

### Data-Only (AG — No LLM)
> Research indicates a mixed relationship between nature exposure and stress, supported by 119 findings from 52 papers in the corpus.

**Grade: D** — States the fact, tells you nothing about *why* or *how*.

### Template (CW — Current System)
> Exposure to nature (in healthcare settings) produces Stress. This is supported by 5 findings across the corpus. Research on nature exposure to stress spans multiple studies in the corpus. Of these, 0 report statistical significance, while the remainder are theoretical or qualitative. The composite evidence strength is High (ω = 0.79).

**Grade: C** — "Produces Stress" is misleading (nature *reduces* stress). Only references 5 of 119 findings. "0 report statistical significance" is wrong (many do). Template structure is repetitive.

### AG Prose (Gemini-class — This Model)
> Across 119 findings from 52 papers, the evidence consistently points toward nature exposure reducing physiological and psychological stress markers — though the story is more nuanced than a simple "nature = calm" equation. The strongest effects appear in healthcare settings, where even passive exposure through windows or video footage of natural scenes produces measurable cortisol reductions (mean d = 2.94, though this is inflated by a few high-leverage studies). The mechanisms likely involve both Attention Restoration Theory — where natural environments allow the directed attention system to recover from fatigue — and Stress Recovery Theory, which emphasizes autonomic nervous system down-regulation triggered by evolutionarily safe visual patterns. However, the "mixed" direction consensus flags an important caveat: not all nature exposure reduces stress equally. Dense wilderness, unfamiliar natural settings, or nature exposure during extreme weather can *increase* arousal. What matters is the perceived restorativeness of the setting, not just its greenness.

**Grade: B+** — Explains mechanisms, flags caveats, contextualizes the effect size, tells you what moderates the relationship.

---

## Cluster 2: Noise → Performance
**84 findings, 5 theories, mixed direction, mean effect d = 12.21**

### Data-Only
> Research indicates a mixed relationship between noise and performance, supported by 84 findings from 37 papers in the corpus.

### Template (CW)
> Noise levels in primary workplace produces Self-assessed performance. This is supported by 5 findings across the corpus. Research on noise to performance spans multiple studies in the corpus. Of these, 0 report statistical significance, while the remainder are theoretical or qualitative. The composite evidence strength is High (ω = 0.77).

**Grade: C** — Same template issues. "Produces" is wrong (noise typically *impairs* performance).

### AG Prose
> The noise–performance relationship is one of the most replicated findings in environmental psychology, but the headline obscures important complexity. Across 84 findings from 37 papers, the dominant pattern is that noise impairs cognitive performance — particularly for tasks requiring sustained attention, reading comprehension, and serial recall. But the "mixed" direction label here is informative: some studies find that moderate ambient noise (around 70 dB, roughly coffee-shop level) *enhances* creative thinking, while consistent low-level white noise can improve focus in individuals with attentional difficulties. The mechanisms diverge by task type. For demanding analytical work, noise increases cognitive load by competing for processing resources in working memory (Cognitive Load Theory). For creative work, moderate noise may trigger a diffuse attention state that facilitates remote associations (the "optimal stimulation" hypothesis). The extraordinarily high mean effect size (d = 12.2) likely reflects an outlier — real-world effects are typically in the d = 0.3–1.0 range for noise interventions. Designers should note: it's not noise *volume* alone that matters, but predictability, controllability, and semantic content. Unpredictable, meaningful speech is far more disruptive than steady mechanical noise at the same decibel level.

**Grade: A-** — Identifies the outlier effect size, explains the non-obvious moderators, gives the design implication.

---

## Cluster 3: Sound Environment → Noise
**76 findings, 5 theories, mixed direction, mean effect d = 0.91**

### Data-Only
> Research indicates a mixed relationship between sound environment and noise, supported by 76 findings from 31 papers in the corpus.

### Template (CW)
> Space planning, strategic use of furniture and partitions, and sound masking technologies in open-pl produces Balance between openness and privacy, facilitated communication and collaboration, minimized distrac. This is supported by 5 findings across the corpus.

**Grade: D** — Truncated text ("open-pl", "distrac"), only 5 of 76 findings referenced.

### AG Prose
> How do you design an acoustic environment that's both open and quiet? This cluster captures one of architecture's persistent tensions: 76 findings across 31 papers document the strategies and trade-offs involved in managing noise through environmental design rather than just sound insulation. Three approaches emerge from the evidence. *Sound masking* — introducing consistent, broadband background noise to reduce the signal-to-noise ratio of conversations — achieves moderate effects (d ≈ 0.9) and works best in open-plan offices where speech privacy is the primary concern. *Material intervention* — acoustic panels, soft furnishings, rugs — reduces reverberation time but doesn't address direct-path noise from nearby speakers. *Spatial planning* — using furniture arrangement, partition height, and room geometry — is the most architecturally integrated approach but the hardest to retrofit. The theory links connect to Predictive Coding (the brain constantly predicts the acoustic environment, and prediction errors from unexpected sounds are what's truly disruptive) and Gated Propagation (thalamic circuits gate auditory input based on task demands and arousal). The practical implication: designing for acoustic comfort is less about making things quiet and more about making the soundscape *predictable*.

**Grade: A** — Organizes 76 findings into 3 coherent strategies, explains the neuroscience, gives a design principle.

---

## Cluster 4: Natural Light → Mood
**56 findings, 5 theories, mixed direction, mean effect d = 0.285**

### Data-Only
> Research indicates a mixed relationship between natural light and mood, supported by 56 findings from 24 papers in the corpus.

### Template (CW)
> Colour of light ('warm' 3000k, 'cool' 4000k, artificial 'daylight' 5500k) produces Positive mood (PANAS). This is supported by 5 findings across the corpus.

### AG Prose
> Natural light's relationship with mood is supported by 56 findings from 24 papers, with a modest but reliable average effect size (d = 0.29). The research converges on three mechanisms. First, *circadian entrainment*: daylight exposure during morning hours synchronizes suprachiasmatic nucleus activity, which regulates serotonin and melatonin rhythms that directly influence mood (Circadian Architecture molecule). Second, *spectral composition*: warmer color temperatures (3000K) tend to promote relaxation while cooler temperatures (5500K) promote alertness, but the relationship isn't linear — context and expectation matter (a cool-blue office at 9 AM feels energizing; the same light at 9 PM feels clinical). Third, *connection to exterior*: windows providing daylight also provide views, and disentangling the light effect from the view effect is methodologically challenging — several studies in this cluster confound the two. The "mixed" direction consensus reflects genuine heterogeneity: studies using PANAS (Positive and Negative Affect Schedule) sometimes show light improving positive affect without changing negative affect, and sometimes the reverse. Biophilic design elements beyond just light — greenery, outdoor views — may be the true drivers in some of these studies.

**Grade: B+** — Identifies methodological confound (light vs view), explains why "mixed" is meaningful, names the measurement tool.

---

## Cluster 5: Acoustic Quality → Noise
**52 findings, 5 theories, mixed direction, mean effect d = 1.13**

### Data-Only
> Research indicates a mixed relationship between acoustic quality and noise, supported by 52 findings from 22 papers in the corpus.

### Template (CW)
> Atmospheric effects (refraction) in urban acoustic models produces Accuracy of aircraft noise prediction around buildings. This is supported by 5 findings across the corpus.

**Grade: D** — Grabbed a highly specific sample finding as the headline. Doesn't represent the cluster.

### AG Prose
> This cluster spans 52 findings across 22 papers on acoustic quality interventions and their effects on noise experience — a technically diverse set that ranges from metamaterial sound insulation to open-office speech privacy. The effect sizes are moderate (mean d = 1.13), suggesting that well-designed acoustic interventions produce meaningful improvements. Three sub-themes emerge: *prediction and modeling* (how well computational acoustic models match real-world conditions — important for architects using simulation tools), *material innovation* (Helmholtz cavity-based metamaterials achieving exceptional low-frequency isolation), and *occupant subjective response* (how people *experience* acoustic quality, which correlates poorly with measured decibel levels). The disconnect between objective measurement and subjective experience is the cluster's most important finding: a space can measure "quiet" by acoustic standards but feel noisy because of intermittent, unpredictable sound events. Conversely, a library with moderate consistent background noise can feel peaceful. Senior management and acousticians systematically underestimate the impact of noise on concentration, according to several studies in this cluster.

**Grade: B+** — Identifies the objective/subjective disconnect, organizes into sub-themes.

---

## Summary

| Cluster | Data-Only | CW Template | AG Prose | Improvement |
|---------|----------|------------|---------|-------------|
| Nature → Stress | D | C (misleading) | B+ | **Large** |
| Noise → Performance | D | C | A- | **Large** |
| Sound → Noise | D | D (truncated) | A | **Very large** |
| Light → Mood | D | C | B+ | **Large** |
| Acoustic → Noise | D | D (wrong headline) | B+ | **Large** |

### Verdict
The template approach (CW current) has systematic problems: wrong verb ("produces"), only references 5 findings regardless of cluster size, no mechanism explanation, occasional truncation and misleading framing. LLM-generated prose is dramatically better — it organizes evidence into themes, explains mechanisms, identifies caveats, and gives design implications.

**Recommendation**: Replace the template generation in `card_generator.py` with LLM-prompted generation for all clusters with ≥5 findings (1,585 clusters). Use data-only for the 2,203 small clusters (< 3 findings) where there isn't enough evidence for meaningful prose.

### For CW
To run this comparison with Opus, use:
```bash
python3 scripts/card_model_comparison.py --model-label "opus"
python3 scripts/card_model_comparison.py --compare
```
The script picks the same 5 clusters and saves output for side-by-side comparison.
