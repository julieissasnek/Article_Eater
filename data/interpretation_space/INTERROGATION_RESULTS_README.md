# Interpretation Space Phase 1: Self-Interrogation Results

**Generated**: 2026-03-01
**Phase**: Pilot (50 beliefs)
**Script**: `/scripts/interrogation_phase1.py`

---

## Overview

The self-interrogation script assesses what the ATLAS QA system **actually knows** about causal mechanisms across the 50 pilot beliefs. Rather than generating or fabricating mechanism information, the script compiles an honest inventory of:

1. **What mechanism data exists** (empirical findings vs. theoretical templates)
2. **What sources contributed** to the system's mechanistic answers
3. **Where gaps exist** (beliefs with no mechanism information)

This evaluation dataset will be used to:
- Train a secondary model to detect and flag mechanistic confidence
- Identify which beliefs have "rich" vs. "sparse" mechanistic grounding
- Design targeted interrogation follow-ups for beliefs lacking depth
- Evaluate the coherence between claimed mechanisms and underlying evidence

---

## Output Files

### 1. `interrogation_results_raw.json`

**Structure**: Array of 50 objects (one per belief)

Each object contains:

```json
{
  "belief_idx": 0,                        // 0-indexed position in pilot
  "belief_id": "10.1006/jevp.2000.0198__f8",  // Unique identifier
  "content": "Colour of light... → Performance",  // Belief statement
  "credence": 0.707,                      // Bayesian credence value
  "entrenchment": 0.3,                    // Epistemic entrenchment
  "stratification_zone": "1",             // Zone 1-4 (credence-based)

  "mechanism_question": "How does...",    // Auto-generated interrogation

  "available_data": {
    "has_extraction": true,               // Was paper extracted?
    "finding_fields": {                   // Fields from extraction.findings[N]
      "antecedent": "...",
      "consequent": "...",
      "direction": "increase|decrease|mixed|no_effect",
      "claim_type": "causal|associational|null",
      "p_value": "0.05|ns|...",
      "effect_size": null,
      "mechanism": "Cognitive processes of...",  // KEY: Empirical mechanism
      "theory_links": ["DT", "MS", "PP"],  // Theory codes
      "source": "p.4",                     // Paper location
      "quote": "..."                       // Quoted text
    },

    "linked_templates": [                 // Matched theoretical templates
      {
        "display_id": "T36",
        "template_id": "HC_WORKING_MEMORY_LOAD_001",
        "score": 0.4589,                  // Relevance score
        "name": "Environmental information demands → working memory..."
      }
    ],

    "linked_theories": [],                // Theories referenced

    "other_findings_from_paper": [        // Context from same paper
      {
        "id": 1,
        "antecedent": "...",
        "consequent": "...",
        "direction": "...",
        "mechanism": "..."
      }
    ]
  },

  "system_answer": "Empirical mechanism (from paper): Cognitive processes...

Theoretical mechanisms (from matched templates, not empirically verified):
  • Template mechanism: Environmental information demands...
  • ...",

  "answer_sources": [                     // Provenance tracking
    "extraction finding mechanism",
    "extraction theory_links",
    "template T36 mechanism",
    "template MS2 mechanism",
    ...
  ],

  "data_quality": "rich"                  // "rich" | "sparse" | "none"
}
```

**Data Quality Tiers**:

- **Rich** (28%): Finding has explicit mechanism from extraction layer
- **Sparse** (58%): Only theoretical templates match; no empirical mechanism
- **None** (14%): No mechanism data from extraction OR templates

### 2. `interrogation_data_summary.md`

Human-readable summary showing:

- Total beliefs processed: 50
- Distribution by stratification zone
- Data quality breakdown by zone
- Top templates by usage frequency
- Interpretive observations and recommendations

---

## Key Insights

### Mechanism Data Distribution

| Category | Count | % | Interpretation |
|----------|-------|---|---|
| **Rich** (empirical) | 14 | 28% | LLM extraction captured finding-level mechanisms |
| **Sparse** (theoretical) | 29 | 58% | Templates provide theoretical framing, not empirical verification |
| **None** | 7 | 14% | No mechanistic information available |

### By Stratification Zone

**Zone 1** (highest credence, n=12):
- Rich: 8 (67%) — Well-studied phenomena with documented mechanisms
- Sparse: 2 (17%)
- None: 2 (17%)

**Zone 2** (n=15):
- Rich: 5 (33%) — Mixed; some mechanisms documented, some not
- Sparse: 9 (60%)
- None: 1 (7%)

**Zone 3** (n=13):
- Rich: 0 (0%) — Lower-credence beliefs tend to lack mechanism data
- Sparse: 9 (69%)
- None: 4 (31%)

**Zone 4** (lower credence, n=10):
- Rich: 1 (10%)
- Sparse: 9 (90%)
- None: 0 (0%)

**Interpretation**: High-credence beliefs (Zone 1) are much more likely to have empirical mechanisms documented in the papers. This is expected: stronger beliefs have better empirical support, including more detailed mechanistic accounts.

### Top Templates

Templates most frequently linked to beliefs (providing theoretical grounding):

1. **IC2** (Interoceptive Affect Construction): 14 beliefs
2. **T12** (Interoceptive Affect Construction): 11 beliefs
3. **T9** (Implicit Evaluation): 8 beliefs
4. **T5** (Threat HPA): 8 beliefs

These templates are meta-level theoretical frameworks (e.g., how emotions are constructed from bodily signals, how the HPA axis responds to threat). When a belief is linked to IC2, the system is saying: "We don't have a specific mechanism, but this fits the broader interoceptive construction pattern."

---

## Honest Epistemology

The `system_answer` field represents what the system **actually knows**, not what it could theoretically know:

**Example 1: Rich mechanistic knowledge**

```
Empirical mechanism (from paper): Cognitive processes of short-term memory
and attention were impaired by more bluish light ('cool' and artificial
'daylight') compared to 'warm' white lighting.

Linked theories: DT, MS, PP

Theoretical mechanisms (from matched templates, not empirically verified
for this specific finding):
  • Template T36: Environmental information demands → working memory load
    → capacity overflow...
```

Here the system is honest: "We have an empirical mechanism. We also have theoretical framings that might apply, but those are general templates, not tested for this specific finding."

**Example 2: Sparse mechanistic knowledge**

```
Only theoretical mechanisms available (from matched templates):
  • Template AX11: Exposure duration → acute vs chronic pathway...
  • Template T9: Environmental feature → implicit evaluation...
```

Here the system admits: "We have no empirical mechanism from the paper. We can suggest theoretical templates, but those aren't empirically verified for this belief."

**Example 3: No mechanistic knowledge**

```
No mechanistic information available. The system has no data about how
this causal relationship works.
```

Total honesty: "We know nothing about the mechanism."

---

## Usage

### Loading the Results

```python
import json

with open('interrogation_results_raw.json') as f:
    results = json.load(f)

# Access a specific belief's interrogation
belief = results[0]
print(belief['mechanism_question'])
print(belief['system_answer'])
print(belief['answer_sources'])
```

### Filtering by Data Quality

```python
# Find beliefs with rich mechanistic data
rich_beliefs = [r for r in results if r['data_quality'] == 'rich']
print(f"Rich mechanisms: {len(rich_beliefs)}")

# Find beliefs with no mechanism data
gap_beliefs = [r for r in results if r['data_quality'] == 'none']
print(f"Knowledge gaps: {len(gap_beliefs)}")
for belief in gap_beliefs:
    print(f"  - {belief['belief_id']}: {belief['content'][:60]}")
```

### Filtering by Zone

```python
# High-credence beliefs
zone1 = [r for r in results if r['stratification_zone'] == '1']
print(f"Zone 1 beliefs: {len(zone1)}")
print(f"  Average mechanism richness: {sum(1 for b in zone1 if b['data_quality']=='rich')/len(zone1):.1%}")
```

---

## Next Steps: Deeper Interrogation

The Phase 1 self-interrogation provides a **baseline inventory**. Follow-up interrogations could:

### 1. **Mechanism Quality Assessment** (Phase 2)

For each belief, ask:
- Is the mechanism **specific** to this antecedent/consequent pair, or generic?
- Is it **testable** (falsifiable)?
- Is it **grounded in theory** or just a description?

Example: "The mechanism is: light color affects circadian rhythms" is too vague. "More bluish light suppresses melatonin release via melanopsin-expressing ipRGCs, reducing nighttime circadian consolidation, impairing short-term memory encoding" is testable and grounded.

### 2. **Template Validation** (Phase 2)

For sparse-data beliefs, validate:
- Are the matched templates actually relevant to this finding?
- Could the template mechanism apply to the antecedent/consequent pair?
- What would it take to "upgrade" from template-level to finding-specific mechanism?

### 3. **Extraction Failure Analysis** (Phase 2)

For beliefs with `data_quality == 'none'`:
- Did the paper actually report a mechanism, but the LLM missed it?
- Is the mechanism implicit (not explicitly stated)?
- Is this a finding that genuinely lacks mechanistic explanation?

### 4. **Coherence Check** (Phase 2)

Cross-reference multiple beliefs from the same paper:
- Do related findings have consistent mechanisms?
- Are there contradictions or tensions?
- Can findings within a paper cross-validate each other?

---

## Script Metadata

**File**: `/scripts/interrogation_phase1.py`

**Key Functions**:

- `load_pilot_beliefs()` — Loads `pilot_beliefs_50.json`
- `load_extraction(doi)` — Loads empirical extraction data
- `extract_finding_from_extraction()` — Maps belief to specific finding
- `load_template(template_id)` — Loads theoretical template
- `extract_mechanism_chain()` — Extracts mechanism description from template
- `construct_system_answer()` — Assembles honest system response
- `generate_mechanism_question()` — Creates interrogation prompt
- `process_belief()` — Processes single belief through pipeline

**Execution**: `python3 scripts/interrogation_phase1.py`

**Output**:
1. Console progress (50 beliefs processed)
2. `interrogation_results_raw.json` (221 KB)
3. `interrogation_data_summary.md` (2.6 KB)

---

## Definitions

**Belief**: A causal claim (antecedent → consequent) with credence value and theoretical templates.

**Stratification Zone**: 1-4 grouping by credence value (Zone 1 = highest credence).

**Extraction**: LLM-extracted structured data from a published paper (finding ID, mechanism, p-value, etc.).

**Finding**: A single empirical result within a paper (identified by index N in belief_id `{doi}__f{N}`).

**Mechanism**: The causal pathway or process explaining how antecedent causes consequent.

**Template**: A reusable theoretical schema (e.g., "environmental demand → cognitive load → performance decline") linking mechanisms to theory.

**System Answer**: The honest, evidence-based answer about what the system knows about the mechanism.

---

## Contact & Questions

For questions about:
- **Data interpretation**: See `SELECTION_REPORT_2026-03-01.md` (belief selection rationale)
- **Template framework**: See `/contracts/vocab/argument_schemes.json`
- **Extraction format**: See `/data/extractions/*.json` (example: `10.1006_jevp.2000.0198.json`)
- **Theoretical linkages**: See `/data/theories/*.json`
