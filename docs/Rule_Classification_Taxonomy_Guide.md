# Rule Classification and Taxonomy Guide

This guide formalizes the taxonomy for classifying Belief Network rules, findings, and knowledge graph constructs within the Article Eater Post-Quinean architecture. 

A structured classification system allows researchers to instantly generate specific meta-analyses across multiple dimensions, such as querying: *"Show me all large-effect findings related to visual processing of curved shapes explained by the Perceptual Fluency mechanism."*

Every extracted rule or finding must be classified along three fundamental dimensions:

## Dimension 1: Entity/Topic Hierarchies (The "What")
Findings are tagged by the specific environments they concern, up through their high-level modalities. Use the schemas in `src/services/environment_taxonomy.py` and `outcome_taxonomy.py`.

*   **Syntax:** Use dot-notation tags reflecting the taxonomy (e.g., `[domain].[category].[specific_attribute]`).
*   **Examples:**
    *   **Specific:** `spatial.shape.curved`, `spatial.shape.rectilinear`
    *   **Category:** `spatial.volume`, `aesthetic.biomorphic`
    *   **High-Level Modality:** `sensory.visual`, `sensory.acoustics`
*   **Implementation:** Add to the `tags` array on the `Belief` or `BetaBernoulliEdge` object.

## Dimension 2: Theoretical Explanations (The "Why")
Findings do not exist in a vacuum; they belong to overarching theories (T1/T1.5) and are driven by specific causal or biological mechanisms (T2).

*   **T1 / T1.5 Macro Theories:** Broad frameworks driving the prediction. 
    *   **Examples:** `ART` (Attention Restoration Theory), `SRT` (Stress Recovery Theory), `Predictive_Processing`, `Perceptual_Fluency`.
    *   **Implementation:** Stored natively in the `theory_id` string field of the extraction schema.
*   **T2 Mechanisms:** The biological or cognitive drivers.
    *   **Examples:** `mechanism:parasympathetic_activation`, `mechanism:reward_prediction_error`.
    *   **Implementation:** Prepend with `mechanism:` and add to the `tags` array.

## Dimension 3: Effect Size & Strength (The "How Much")
Meta-analyses are only valid if we can sort by effect sizes (Cohen's d, Pearson's r, Hedges' g) and the severity/quality of the evidence.

*   **Effect Size Magnitude:** Categorize findings by the magnitude of the measured effect.
    *   **Implementation:** Natively stored in the `strength.value` field or `evidence_effect_size`.
*   **Examples:** Small ($d<0.5$), Medium ($0.5 \le d < 0.8$), Large ($d \ge 0.8$).
*   **Quality/Severity:** Filter by how well the claim has survived empirical testing.
    *   **Implementation:** Stored natively in the `evidence_quality` (e.g. `SEVERELY_TESTED`, `MODERATELY_TESTED`).

---

### Example Valid JSON Representation
An extracted rule adhering to this taxonomy:

```json
{
  "rule_id": "example-paper-1042:finding_1",
  "status": "prima_facie",
  "rule_text": "Curved and biomorphic interior walls induce relaxation and positive aesthetic response compared to sharp boundaries.",
  "theory_id": "Perceptual_Fluency",
  "tags": [
    "sensory.visual",
    "spatial.shape.curved",
    "aesthetic.biomorphic",
    "mechanism:pattern_recognition_fluency"
  ],
  "strength": {
    "kind": "effect_size",
    "type": "cohens_d",
    "value": 0.85
  },
  "evidence_quality": "MODERATELY_TESTED"
}
```

### Querying the System
Using the companion script `scripts/query_rules.py`, you can filter records matching specific taxonomy queries (e.g., `--theory Perceptual_Fluency --tag spatial.shape.curved --min-effect 0.8`).
