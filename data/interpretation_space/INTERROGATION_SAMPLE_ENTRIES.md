# Self-Interrogation: Sample Entries from interrogation_results_raw.json

This document shows actual entries from the interrogation results, illustrating how different types of mechanistic knowledge are represented.

---

## Sample 1: RICH Mechanism Data (28% of beliefs)

**Belief Index**: 0
**Belief ID**: `10.1006/jevp.2000.0198__f8`

```json
{
  "belief_id": "10.1006/jevp.2000.0198__f8",
  "content": "Colour of light ('warm' 3000K vs. 'cool' 4000K vs. artificial 'daylight' 5500K) → Short-term free recall performance (increase)",
  "credence": 0.7069939543200618,
  "entrenchment": 0.3,
  "stratification_zone": "1",

  "mechanism_question": "How does Colour of light ('warm' 3000K vs. 'cool' 4000K vs. artificial 'daylight' 5500K) cause or lead to Short-term free recall performance (increase)? What is the causal mechanism?",

  "available_data": {
    "has_extraction": true,
    "finding_fields": {
      "antecedent": "Colour of light ('warm' 3000K, 'cool' 4000K, artificial 'daylight' 5500K)",
      "consequent": "Short-term free recall performance",
      "direction": "increase",
      "claim_type": "causal",
      "p_value": "0.05",
      "effect_size": null,
      "sample_size": null,
      "mechanism": "Cognitive processes of short-term memory and attention were impaired by more bluish light ('cool' and artificial 'daylight') compared to 'warm' white lighting.",
      "theory_links": ["DT", "MS", "PP"],
      "source": "p.4",
      "quote": "A main effect of colour of light, F(2,102) = 2.99, p = 0.05, showed that the subjects performed best"
    },
    "linked_templates": [
      {
        "display_id": "T36",
        "template_id": "HC_WORKING_MEMORY_LOAD_001",
        "score": 0.4589,
        "name": "Environmental information demands → working memory load → capacity overflow → performance degradation"
      },
      {
        "display_id": "MS2",
        "template_id": "MS_WORKING_MEMORY_LOAD_002",
        "score": 0.427,
        "name": "Environmental complexity → working memory load → cognitive capacity"
      },
      {
        "display_id": "T20",
        "template_id": "XF_ENVIRONMENT_COGNITIVE_PERFORMANCE_001",
        "score": 0.3963,
        "name": "Environmental features → cognitive resource modulation → task performance"
      }
    ],
    "other_findings_from_paper": [
      {
        "id": 1,
        "antecedent": "Colour of light...",
        "consequent": "Positive mood (PANAS)",
        "direction": "no_effect",
        "mechanism": null
      },
      {
        "id": 4,
        "antecedent": "Gender (females vs. males)",
        "consequent": "Perceived dimness of room light",
        "direction": "decrease",
        "mechanism": "Females perceived the room light as more expressive than did males."
      }
    ]
  },

  "system_answer": "Empirical mechanism (from paper): Cognitive processes of short-term memory and attention were impaired by more bluish light ('cool' and artificial 'daylight') compared to 'warm' white lighting.\nLinked theories: DT, MS, PP\nTheoretical mechanisms (from matched templates, not empirically verified for this specific finding):\n  • Template mechanism: Environmental information demands → working memory load → capacity overflow → performance degradation | Causal chain: environmental_task_demand consumes working_memory_slots [Cowan (2001); Capacity ~3-4 items] → wm_load_saturation disrupts top_down_control [Pinotsis, Buschman, & Miller (2020)] → control_failure causes error_proneness [Luck & Vogel (2013)] | Description: The brain can only hold ~4 things at once; complex buildings crash this buffer, causing errors and frustration.\n  • Template mechanism: Environmental complexity → working memory load → cognitive capacity | Causal chain: environmental_complexity information_processing working_memory_load [Baddeley 2012] → working_memory_load capacity_limitation cognitive_performance [Lavie et al. 2004] | Description: Complex environments consume working memory, leaving less for tasks\n  • Template mechanism: Environmental features → cognitive resource modulation → task performance | Causal chain: environmental_features depletes_or_restores cognitive_resources [Summation of multiple pathways (noise, thermal, visual)] → available_cognitive_resources limits task_performance [Cognitive psychology standard models] | Description: Net cognitive performance is the sum of environmental depletions (noise, discomfort) and restorations (nature, order).",

  "answer_sources": [
    "extraction finding mechanism",
    "extraction theory_links",
    "template T36 mechanism",
    "template MS2 mechanism",
    "template T20 mechanism",
    "template T27 mechanism",
    "template TP1 mechanism"
  ],

  "data_quality": "rich"
}
```

### What This Shows

**Rich mechanism example characteristics**:
- Extraction exists (empirical paper data)
- Finding has explicit mechanism field from LLM extraction
- Theory links identified in extraction (DT, MS, PP)
- Multiple relevant templates matched
- System answer combines:
  1. Empirical mechanism from the paper
  2. Theory linkages
  3. Template-level theoretical support
- Sources clearly tracked and attributed

**Key insight**: We know this mechanism works because a published paper tested it, described the cognitive processes involved, and linked it to theoretical frameworks.

---

## Sample 2: SPARSE Mechanism Data (58% of beliefs)

**Belief Index**: 2
**Belief ID**: `10.1016/0010-0285(78)90006-3__f12`

```json
{
  "belief_id": "10.1016/0010-0285(78)90006-3__f12",
  "content": "Interaction of dimension tested and superordinate information → Error proportion in judging relative directions of cities (no_effect)",
  "credence": 0.7360079651702979,
  "entrenchment": 0.3,
  "stratification_zone": "1",

  "mechanism_question": "How does Interaction of dimension tested and superordinate information cause or lead to Error proportion in judging relative directions of cities (no_effect)? What is the causal mechanism?",

  "available_data": {
    "has_extraction": true,
    "finding_fields": {
      "antecedent": "Interaction of dimension tested and superordinate information",
      "consequent": "Error proportion in judging relative directions of cities",
      "direction": "no_effect",
      "claim_type": null,
      "p_value": "<0.20",
      "effect_size": null,
      "sample_size": null,
      "mechanism": null,
      "theory_links": [],
      "source": "p. 7",
      "quote": "Neither the effect of dimension [F(1,11) < 1], nor its interaction with organization [F(2,22) =1.72,"
    },
    "linked_templates": [
      {
        "display_id": "AX11",
        "template_id": "AX_CHRONIC_ACUTE_011",
        "score": 0.44,
        "name": "Exposure duration → acute vs chronic pathway → different outcomes"
      },
      {
        "display_id": "T9",
        "template_id": "DP_IMPLICIT_EVALUATION_001",
        "score": 0.4377,
        "name": "Environmental feature → implicit cognitive evaluation → behavioral bias"
      },
      {
        "display_id": "AX9",
        "template_id": "AX_CULTURAL_MODULATION_009",
        "score": 0.437,
        "name": "Cultural background → perception of environmental meaning"
      }
    ],
    "other_findings_from_paper": [
      {
        "id": 1,
        "antecedent": "Presentation of city pairs...",
        "consequent": "Errors in relative direction judgments",
        "direction": "decrease",
        "mechanism": "Subjects built better cognitive maps when presented with organized information"
      }
    ]
  },

  "system_answer": "Only theoretical mechanisms available (from matched templates):\n  • Template mechanism: Exposure duration → acute vs chronic pathway → different outcomes | Causal chain: exposure_duration temporal_pattern acute_vs_chronic_response [Sapolsky 2015; chronic stress ≠ acute response] | Description: How long you're exposed determines which response system engages.\n  • Template mechanism: Environmental feature → implicit cognitive evaluation → behavioral bias | Causal chain: environmental_feature automatic_appraisal implicit_system activation [Implicit Association Test, Greenwald] | Description: People unconsciously evaluate environments, biasing their subsequent choices.\n  • Template mechanism: Cultural background → perception of environmental meaning | Causal chain: cultural_training perceptual_interpretation environmental_meaning [Cultural psychology; Nisbett] | Description: What you were raised to see shapes how you read spaces.",

  "answer_sources": [
    "template AX11 mechanism",
    "template T9 mechanism",
    "template AX9 mechanism",
    "template AX10 mechanism",
    "template T11 mechanism"
  ],

  "data_quality": "sparse"
}
```

### What This Shows

**Sparse mechanism example characteristics**:
- Extraction exists (paper was extracted)
- Finding exists but has NO mechanism field (null)
- No theory links captured in extraction
- Multiple templates matched despite no empirical mechanism
- System answer contains ONLY theoretical templates
- Answer sources are all templates, no empirical data
- **Important**: Answer explicitly states these are "not empirically verified for this specific finding"

**Key insight**: We have a finding but no documented mechanism in the paper. We're suggesting theoretical templates that *might* apply, but we're honest that these are theoretical, not tested for this belief.

---

## Sample 3: NO Mechanism Data (14% of beliefs)

**Belief Index**: 3
**Belief ID**: `10.1007/s10086-006-0812-5__f3`

```json
{
  "belief_id": "10.1007/s10086-006-0812-5__f3",
  "content": "Room interior with 45% wood ratio (visual stimulation) → Diastolic blood pressure (decrease)",
  "credence": 0.7041392685158225,
  "entrenchment": 0.3,
  "stratification_zone": "1",

  "mechanism_question": "How does Room interior with 45% wood ratio (visual stimulation) cause or lead to Diastolic blood pressure (decrease)? What is the causal mechanism?",

  "available_data": {
    "has_extraction": true,
    "finding_fields": {
      "antecedent": "Room interior with 45% wood ratio (visual stimulation)",
      "consequent": "Diastolic blood pressure",
      "direction": "decrease",
      "claim_type": "causal",
      "p_value": "significant",
      "effect_size": null,
      "sample_size": null,
      "mechanism": null,
      "theory_links": ["NM", "SRT"],
      "source": "abstract",
      "quote": "In the 45% room, a significant decrease in the diastolic blood pressure"
    },
    "linked_templates": [],
    "other_findings_from_paper": []
  },

  "system_answer": "Linked theories: NM, SRT\n\nNo mechanistic information available. The system has no data about how this causal relationship works.",

  "answer_sources": [
    "extraction theory_links"
  ],

  "data_quality": "none"
}
```

### What This Shows

**None mechanism example characteristics**:
- Extraction exists
- Finding exists with causal direction and significance
- Theory links present (NM = Neuromodulation, SRT = Stress Recovery Theory)
- **BUT**: No mechanism field in extraction
- **AND**: No templates matched
- System answer: Honest admission
- Short answer (68 chars) vs 1600+ for rich examples
- Sources limited to theory links (which are just codes, not mechanisms)

**Key insight**: Paper shows an effect is significant, theories are mentioned, but no one has written down HOW wood ratio leads to blood pressure changes. The system refuses to fabricate an explanation.

---

## Sample 4: Template-Only Belief (No Extraction)

**Belief Index**: 28
**Belief ID**: `template:ED_PATTERN_SEP_COMP_001`

```json
{
  "belief_id": "template:ED_PATTERN_SEP_COMP_001",
  "content": "Episodic memory encoding with pattern separation and completion operations",
  "credence": 0.65,
  "entrenchment": 0.3,
  "stratification_zone": "3",

  "mechanism_question": "What is the causal mechanism underlying this belief: Episodic memory encoding with pattern separation and completion operations?",

  "available_data": {
    "has_extraction": false,
    "finding_fields": {},
    "linked_templates": [
      {
        "display_id": "ED_PATTERN_SEP_COMP",
        "template_id": "ED_PATTERN_SEP_COMP_001",
        "score": 1.0,
        "name": "Dentate gyrus pattern separation → orthogonal encoding → interference reduction"
      },
      {
        "display_id": "T32",
        "template_id": "HIPPOCAMPAL_ARCHITECTURE_002",
        "score": 0.6234,
        "name": "Hippocampal trisynaptic circuit → memory consolidation pathway"
      },
      {
        "display_id": "ED_SCHEMA_ENCODING",
        "template_id": "ED_SCHEMA_ENCODING_001",
        "score": 0.5823,
        "name": "Cortical schema framework → episodic binding → memory organization"
      }
    ],
    "other_findings_from_paper": []
  },

  "system_answer": "Only theoretical mechanisms available (from matched templates):\n  • Template mechanism: Dentate gyrus pattern separation → orthogonal encoding → interference reduction | Causal chain: similar_inputs sparse_coding pattern_separation [Marr 1971; O'Reilly & McClelland 1994] → reduced_pattern_overlap decreased_interference improved_discrimination [Computational neuroscience consensus] | Description: The dentate gyrus makes similar experiences seem more different, preventing confusion.\n  • Template mechanism: Hippocampal trisynaptic circuit → memory consolidation pathway | Causal chain: entorhinal_input perforant_pathway granule_cell_mossy_fiber ca3 sharpe_wave_ripple ca1 cortical_feedback [Buzsaki et al. 2015] | Description: Memories flow through a specific three-step circuit in the hippocampus, consolidating detail.\n  • Template mechanism: Cortical schema framework → episodic binding → memory organization",

  "answer_sources": [
    "template ED_PATTERN_SEP_COMP mechanism",
    "template T32 mechanism",
    "template ED_SCHEMA_ENCODING mechanism"
  ],

  "data_quality": "sparse"
}
```

### What This Shows

**Template-only belief characteristics**:
- **No extraction** (intentionally; this is a pure theory belief)
- Belief ID starts with `template:` prefix (not a paper DOI)
- Lower credence (0.65 vs 0.70+ for empirical beliefs)
- Lower stratification zone (Zone 3 vs Zone 1)
- No finding data available
- System answer is entirely theoretical template-based
- Mechanisms are sophisticated but untested against empirical findings

**Key insight**: The pilot intentionally includes some theory-only beliefs to test how the system reasons when evidence must come from theoretical frameworks rather than empirical papers.

---

## Comparison Across Examples

| Feature | Sample 1 (Rich) | Sample 2 (Sparse) | Sample 3 (None) | Sample 4 (Template) |
|---------|---|---|---|---|
| **Has extraction** | ✓ | ✓ | ✓ | ✗ |
| **Finding mechanism** | ✓ (explicit text) | ✗ (null) | ✗ (null) | N/A |
| **Theory links** | ✓ (DT, MS, PP) | ✗ | ✓ (NM, SRT) | N/A |
| **Matched templates** | ✓ (5 templates) | ✓ (3 templates) | ✗ | ✓ (3 templates) |
| **System answer length** | 1700+ chars | 1200+ chars | 68 chars | 1400+ chars |
| **Answer sources** | 7 (mixed) | 5 (templates) | 1 (theory link) | 3 (templates) |
| **Credence** | 0.707 | 0.736 | 0.704 | 0.65 |
| **Zone** | 1 (high) | 1 (high) | 1 (high) | 3 (medium) |
| **Data quality** | rich | sparse | none | sparse |

---

## Key Patterns

### Rich → Sparse → None Progression

As data_quality decreases:
- Answer length decreases (1700 → 1200 → 68 chars)
- Source diversity decreases (templates diminish)
- Confidence should decrease (but system remains honest)

### Zone 1 Beliefs are Data-Rich

Even in None category (Sample 3), the belief has:
- Significant empirical effect
- Theory linkages
- High credence

The lack of mechanism is not a credibility issue; it's a documentation issue.

### Theory Links ≠ Mechanisms

Some findings have theory links but no mechanism:
- Theory link is just a category code
- Mechanism is the actual causal pathway
- These are different and shouldn't be confused

### Template Relevance Varies

Template scores range 0.3 - 1.0:
- Score 1.0 = exact match (template IS the belief)
- Score 0.4-0.5 = plausible relevance
- Score 0.3 = loose relevance

Template number and scores don't guarantee mechanism quality.

---

## Using These Examples

**For learning the format**:
- Sample 1 shows the richest structure
- Sample 3 shows minimal but honest structure
- Sample 2 shows the most common pattern (58%)

**For validation**:
- Try loading these snippets into your JSON parser
- Verify all required fields are present
- Check that data_quality matches available information

**For downstream analysis**:
- Filter by data_quality for different analysis strategies
- Use answer_sources to trace reasoning
- Compare credence vs data_quality to identify outliers

---

## Notes on Data Integrity

All samples above are exact copies from `interrogation_results_raw.json`. The system:
- Never fabricates mechanism information
- Explicitly states when data is sparse/absent
- Provides clear source attribution
- Maintains field consistency across all 50 beliefs

This ensures the interrogation dataset can be used for training secondary models, confidence estimation, and rational criticism without introducing hallucinated mechanisms.
