# Vocabulary Mismatch Investigation Report

**Date**: 2026-03-01
**Repository**: Article_Eater_PostQuinean_v1
**Problem**: Template relevance matcher achieves 86.9% Tier2 coverage via raw extraction text, but only 29.9% via DB fields (environment_id, outcome_id)
**Root Cause**: Complete vocabulary disjunction between template input/output terms and DB field values

---

## Executive Summary

The template matcher's 57-percentage-point performance cliff (86.9% → 29.9%) is caused by **zero vocabulary overlap** between:
- **Template vocabulary** (51 environmental inputs, 115 outcome outputs): expert-curated natural language terms
- **DB vocabulary** (442 environment_ids, 30 outcome_ids): hierarchical notation with standardized prefixes

The raw extraction text works because it contains the mechanism descriptions that templates extract during linking. The DB field values never intersect with template vocabulary, making direct matching impossible.

---

## Section 1: Quantitative Gap Analysis

### 1.1 Template Input/Output Vocabulary

From 166 template JSON files in `/data/templates/`:

| Metric | Count |
|--------|-------|
| Total templates | 166 |
| Unique input_terms (environmental) | 51 |
| Unique output_terms (cognitive/affective/behavioral/etc) | 115 |
| **Total unique terms** | **166** |

**Sample template input_terms** (environmental):
- `acoustic_event`, `acoustic_features`, `ambient_noise_level`
- `ceiling_height`, `ceiling_height_proportional_ratio`
- `color_saturation_and_brightness`, `display_surface_density`
- `environmental_complexity`, `environmental_demand`
- `thermal_radiation`, `visual_contrast_ratio`
- (all extracted from `causal_links[].from_entity` where `from_level == "environmental"`)

**Sample template output_terms** (psychological):
- `aesthetic_emotion`, `affective_comfort`, `affective_state`
- `approach_behavior`, `arousal_pe`, `associative_segmentation`
- `auditory_motor_white_matter`, `autobiographical_memory`
- `mood_valence_shift`, `working_memory_capacity`
- (all extracted from `causal_links[].to_entity` where `to_level in {cognitive, affective, behavioral, ...}`)

### 1.2 Database Field Vocabulary

From `/data/web_persistence.db` beliefs table (4,888 records):

| Metric | Count |
|--------|-------|
| Total beliefs | 4,888 |
| Unique environment_id | 442 |
| Unique outcome_id | 30 |

**All outcome_id values** (complete list):
```
out.affect                      out.affect.anxiety            out.affect.mood
out.affect.mood.negative        out.affect.mood.positive      out.affect.stress
out.behav                       out.behav.productivity        out.behav.sleep
out.cog                         out.cog.attention             out.cog.attention.selective
out.cog.attention.sustained     out.cog.memory                out.cog.memory.working
out.cog.performance             out.generic.attention         out.generic.cognition
out.generic.mood                out.generic.productivity      out.generic.sleep
out.generic.stress              out.health                    out.health.wellbeing
out.physio                      out.physio.alertness          out.physio.fatigue
out.social                      out.social.collaboration      out.social.interaction
```

**Sample environment_id values** (hierarchical namespace pattern):
```
env.ae.barriers_guards_present           env.ae.clear_exits_wayfinding_signage
env.ae.compartmentalized_plan            env.ae.concrete_prominent
env.ae.cool_color_palette                env.ae.cool_lighting_high_cct
env.ae.crowded_space                     env.ae.curvilinear_forms
env.ae.daylighting                       env.ae.dynamic_lighting
env.ae.fractal_like_pattern              env.ae.glare_present
env.complexity.spatial_entropy           env.cognitive.error
env.unresolved.approach_avoidance_*      env.unresolved.emotional_expressions_*
...and 418 more
```

---

## Section 2: Vocabulary Overlap Analysis

### 2.1 Exact-Match Overlap

**Null intersection across all vectors:**

| Vocabulary Pair | Overlap | Template % | DB % |
|-----------------|---------|-----------|------|
| input_terms ∩ environment_id | **0 / 51** | **0.0%** | 0.0% |
| output_terms ∩ outcome_id | **0 / 115** | **0.0%** | 0.0% |

No single template term (e.g., "ceiling_height") matches any DB environment_id.
No single template term (e.g., "mood_valence_shift") matches any DB outcome_id.

### 2.2 Directional Gaps

**Template→DB direction** (what templates cannot reach):
- All 51 template input_terms are missing from DB environment_id
- All 115 template output_terms are missing from DB outcome_id

**DB→Template direction** (what DB has but templates never mention):
- 442 environment_ids not in template vocabulary (100%)
- 30 outcome_ids not in template vocabulary (100%)

---

## Section 3: Root Cause Analysis

### 3.1 Two Vocabularies, Two Standards

#### Template Vocabulary (Source: causal_links in template JSONs)

Templates use **natural language domain terms** extracted from expert model descriptions:

```json
{
  "template_id": "CREA1_creative_network_dynamics",
  "causal_links": [
    {
      "from_entity": "environmental_complexity",        ← input_term
      "from_level": "environmental",
      "to_entity": "divergent_thinking_capacity",       ← output_term
      "to_level": "cognitive"
    }
  ]
}
```

These terms come from:
- Domain literature (e.g., "ceiling_height" from environmental psychology)
- Mechanistic descriptions (e.g., "arousal_pe" from predictive processing)
- Physiological processes (e.g., "hpa_axis_dysregulation" from stress theory)

#### Database Vocabulary (Source: beliefs table)

Database uses **hierarchical canonical identifiers**:

```sql
INSERT INTO beliefs (environment_id, outcome_id, content)
VALUES (
  'env.ae.high_ceiling',              ← hierarchical ID
  'out.cog.attention',                ← hierarchical ID
  'Participants in a high-ceiling room showed improved attention'
)
```

Format: `env.[namespace].[descriptor]` and `out.[domain].[subdomain].[specific]`

This vocabulary appears to be:
- **Independently designed** (not derived from templates)
- **Normalized/canonical** (forcing all natural language into a prefixed schema)
- **Exhaustive** (442 environment_ids to cover all possible conditions found in papers)

### 3.2 Why Raw Extraction Text Achieves 86.9%

The `finding_template_relevance.py` matcher uses **content-based matching** for the 86.9% case:

```python
# From _score_template_for_finding() line 678-680:
env_terms = _expand_with_bridges(finding.environment_id, ENV_BRIDGES)  # DB field
out_terms = _expand_with_bridges(finding.outcome_id, OUTCOME_BRIDGES)  # DB field
content_terms = _tokenize(finding.content)                             # Raw text!
```

When matching against **raw extraction content**, the matcher can:

1. **Tokenize antecedent/consequent text** from extraction JSON
2. **Extract mechanism_terms** from template descriptions:
   ```python
   mechanism_terms.update(_tokenize(payload.get("short_description")))
   mechanism_terms.update(_tokenize(payload.get("structural_pattern")))
   ```
3. **Find overlap** in natural language (e.g., both mention "attention", "ceiling", "color")

**Example from extractions**:
```json
{
  "antecedent": "High ceilings with ample daylighting",
  "consequent": "Improved attention and divergent thinking"
}
```

Tokens: `{high, ceilings, ample, daylighting, improved, attention, divergent, thinking}`

These overlap with mechanism_terms extracted from templates (e.g., "attention", "ceiling" from names/descriptions), achieving decent coverage via content.

But when the **same finding is stored in DB** with normalized IDs:
```sql
environment_id = 'env.ae.high_ceiling'      (↔ template input_terms: 0/51 match)
outcome_id = 'out.cog.attention'            (↔ template output_terms: 0/115 match)
```

The structured IDs share **no vocabulary** with template causal_link specifications.

### 3.3 Missing Infrastructure

**No bridge exists** from raw text → canonical DB fields:

| What Exists | What's Missing |
|------------|-----------------|
| `outcome_lookup.json` with keys like "cognitive", "attention", "focus" | Mapping from template output_terms to `out.cog.attention` format |
| `outcome_vocab.json` with hierarchical outcome structures | Mapping from raw consequent text to outcome_id |
| `ENV_BRIDGES` dict in matcher (hard-coded bridges) | Comprehensive environment_id mapping strategy |
| Raw extraction files with antecedent/consequent text | Canonical mapping from text → environment_id, outcome_id |

The lookup files appear designed for **outcome_id → description** (reverse direction), not for matching.

---

## Section 4: Detailed Examples

### 4.1 Environment Mismatch Examples

**Template specifies:**
```
input_term: "ceiling_height"
```

**DB has various related values:**
```
env.ae.high_ceiling                    ✓ Related (could match "height")
env.ae.low_ceiling                     ✓ Related
env.complexity.spatial_entropy         ✗ Different domain (complexity vs. height)
env.unresolved.spatial_cognition       ✗ Different domain
```

But the matcher cannot connect "ceiling_height" → "env.ae.high_ceiling" because:
1. No token overlap: "ceiling_height" (1 token post-normalization) vs "env.ae.high_ceiling" (contains "high", "ceiling")
2. No bridge rule in `ENV_BRIDGES` covers this mapping
3. The prefix "env.ae." is entirely orthogonal to domain expertise

### 4.2 Outcome Mismatch Examples

**Template specifies:**
```
output_term: "aesthetic_emotion"
output_term: "divergent_thinking"
output_term: "working_memory_capacity"
```

**DB has only:**
```
out.affect.mood
out.cog.attention
out.cog.memory
out.cog.memory.working      ← Might relate to "working_memory" but no bridge exists
```

The matcher cannot connect:
- "aesthetic_emotion" → "out.affect.mood" (different constructs)
- "divergent_thinking" → "out.cog.attention" (no overlap)
- "working_memory_capacity" → "out.cog.memory.working" (token overlap but not in matching logic)

---

## Section 5: Most Efficient Normalization Strategy

### 5.1 Option A: Reverse Bridge (DB → Template)
**Create mappings from outcome_id/environment_id to template terms**

Pros:
- Protects existing DB schema
- Non-destructive to current extraction pipeline
- Can be implemented as a lookup table

Cons:
- Requires manual curation: 442 environment_ids × 51 template input_terms
- Many-to-many mappings needed (env.ae.high_ceiling maps to "ceiling_height", "spatial_volume", "environmental_demand")
- Cannot discover new mappings without re-curation
- Expensive maintenance as templates expand

**Effort**: ~2,000+ mapping decisions; 40-60 hours of manual work

### 5.2 Option B: Extraction-Time Normalization ⭐ RECOMMENDED
**Normalize environment_id/outcome_id during extraction ingestion, not post-hoc**

Pros:
- Maps at the source (raw text → canonical ID)
- Aligns with template vocabulary naturally
- One-time cost per paper extraction
- Enables future template additions without rework
- Preserves raw text in `content` field for auditing

Cons:
- Requires modifying extraction pipeline
- Must define canonical ID assignment rules
- Needs to handle ambiguous cases (one phrase → multiple IDs)

**Implementation strategy:**

1. **Create `environment_id_normalizer.py`** that maps raw antecedent tokens to environment_ids:
   - Token: "ceiling" → environment_id: "env.ae.high_ceiling" or "env.ae.low_ceiling"
   - Token: "daylighting" → environment_id: "env.ae.daylighting"
   - Compound: "high ceilings with daylighting" → [env.ae.high_ceiling, env.ae.daylighting]

2. **Create `outcome_id_normalizer.py`** that maps raw consequent tokens to outcome_ids:
   - Token: "attention" → outcome_id: "out.cog.attention" or "out.generic.attention"
   - Token: "mood" → outcome_id: "out.affect.mood" or "out.generic.mood"
   - Compound: "attention and memory" → [out.cog.attention, out.cog.memory]

3. **Use existing outcome_lookup.json** as the ground truth:
   ```json
   {
     "cognitive": "cog",                    ← outcome_lookup key → domain
     "attention": "cog",                    ← lookup key → domain
     "mood": "affect",
     "working memory": "cog.memory",        ← compound mappings
     ...
   }
   ```

4. **Implement confidence scoring** for ambiguous mappings:
   - High confidence: "ceiling" alone is rare; usually "high ceiling" → env.ae.high_ceiling
   - Low confidence: "spatial" appears in many contexts (spatial_entropy, wayfinding, layout)
   - Option: Store as multi-valued JSON in DB or pick highest-confidence mapping

**Effort**: ~300-500 hours (design normalizer, test against all 4,888 beliefs, handle edge cases)

### 5.3 Option C: Template Realignment
**Rewrite template causal_links to use DB field formats**

Pros:
- Direct vocabulary alignment
- No bridge logic needed
- Simplest matching logic

Cons:
- Destructive to current template design (166 templates affected)
- Loses domain semantic information
- Cannot use in other contexts
- High risk of introducing errors

**Not recommended**: Too expensive, too lossy.

---

## Section 6: Findings Summary

| Finding | Evidence |
|---------|----------|
| **Complete vocabulary disjunction** | 0% overlap on both input and output terms |
| **Two independent standards** | Templates use natural language; DB uses hierarchical IDs |
| **Raw text works (86.9%)** | Content tokenization finds semantic overlap |
| **DB fields don't work (29.9%)** | No token overlap; no bridge rules; no normalization |
| **Missing infrastructure** | No environment_id mapping; outcome_lookup is insufficient |
| **442 environment_ids never linked** | No template input_terms match any env.* value |
| **115 output_terms never matched** | Template output_terms have no counterpart in 30 outcome_ids |
| **Scale of gap** | 557 distinct vocabulary items (166 + 442 - 51) with zero intersection |

---

## Section 7: Recommended Next Steps

1. **Implement Option B (Extraction-Time Normalization)** as the primary solution
   - Design normalizer logic to map raw text → canonical IDs
   - Test against all 4,888 beliefs to validate coverage
   - Document any ambiguous cases requiring manual review

2. **Augment outcome_lookup.json** to support the normalizer
   - Add compound term mappings (e.g., "working memory" → "cog.memory")
   - Add synonyms (e.g., "focus" → "cog.attention")
   - Version the mapping for future expansion

3. **Create environment_id mapping** (new file)
   - Design namespace ontology (what does "env.ae" mean vs "env.complexity"?)
   - Build token → environment_id mapper
   - Document discovered patterns from 442 IDs

4. **Validate coverage post-normalization**
   - Re-run template matcher on normalized environment_id/outcome_id
   - Target: restore coverage to ≥75% (vs. 29.9% current)
   - Compare to raw-text baseline (86.9%) to identify remaining gaps

5. **Long-term: Reconcile vocabularies**
   - Templates and DB should use common underlying constructs
   - Consider migrating to a unified schema that supports both expert terminology and canonical notation

---

## Files Analyzed

- `/src/services/finding_template_relevance.py` — Template matching logic
- `/data/templates/*.json` — 166 template definitions (input_terms, output_terms)
- `/data/web_persistence.db` — 4,888 beliefs with environment_id, outcome_id
- `/contracts/outcome_vocab/outcome_vocab.json` — Outcome vocabulary structure
- `/contracts/outcome_vocab/outcome_lookup.json` — Outcome ID lookup (insufficient)
- `/data/extractions/*.json` — Sample extraction files showing antecedent/consequent

---

## Appendix: Template Bridging Mechanism

The matcher includes hard-coded bridges for some environment/outcome pairs:

```python
ENV_BRIDGES = {
    "has_nature_view": {"nature_scene_exposure", "nature_view", "green_view", ...},
    "ceiling_height_m": {"ceiling_height", "spatial_volume", "perceived_confinement"},
    "illuminance_lux": {"light_intensity", "luminance", "light_exposure", ...},
    ...  # 9 bridges total
}

OUTCOME_BRIDGES = {
    "attention": {"directed_attention", "attention_control", ...},
    "stress": {"hpa_axis_dysregulation", "cortisol", "allostatic_load", ...},
    ...  # 12 bridges total
}
```

These bridges provide **local vocabulary expansion** but:
- Only 21 mappings total (vs. 442 + 115 needed)
- Manually curated; cannot scale
- Assume a DB field matching one of the keys (which never happens due to hierarchical format)
- Do not address the core issue: no DB field matches even the bridge source keys

---

**Report completed**: 2026-03-01 17:45 UTC
**Investigator**: Claude Code Analysis Agent
