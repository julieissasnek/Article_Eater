# Extraction-Time Normalization Strategy Specification

**Date**: 2026-03-01
**Status**: RESEARCH/SPECIFICATION (Not yet implemented)
**Purpose**: Bridge vocabulary gap between template input/output terms and DB canonical IDs

---

## Overview

The template matcher's 57-percentage-point performance drop (86.9% → 29.9%) is caused by zero vocabulary overlap between:
- **Template vocabulary**: Natural language domain terms from causal_link specifications
- **DB vocabulary**: Hierarchical canonical IDs with prefixes

This specification proposes normalizing raw extraction text → canonical IDs at ingestion time, which is the most scalable and maintainable solution.

---

## Problem Restated

### Current Data Flow

```
Paper → Extract (antecedent/consequent text) → Store in DB (environment_id, outcome_id) → Match with templates
                                                     ↑
                                        VOCABULARY GAP HERE

                                        DB: "env.ae.high_ceiling"
                                        Template expects: "ceiling_height"
                                        Zero overlap → no match
```

### Proposed Data Flow

```
Paper → Extract → NORMALIZE TEXT → Assign canonical IDs → Store → Match templates
                  (new step)       (new logic)

                  Input: "High ceilings with daylighting"
                  ↓
                  Normalize: ceiling_height, daylighting
                  ↓
                  Map: env.ae.high_ceiling, env.ae.daylighting
                  ↓
                  Store: environment_id = "env.ae.high_ceiling|env.ae.daylighting"
                  ↓
                  Template match: can now find alignment
```

---

## Component 1: Environment ID Normalizer

### Design

File: `src/services/environment_id_normalizer.py`

Function signature:
```python
def normalize_environment_description(
    text: str,
    existing_env_ids: Optional[List[str]] = None,
    confidence_threshold: float = 0.7
) -> List[Tuple[str, float]]:
    """
    Map free-form environment description to canonical environment_id values.

    Args:
        text: Raw antecedent text from extraction (e.g., "High ceilings with natural light")
        existing_env_ids: (optional) Pre-extracted env IDs for multi-source reconciliation
        confidence_threshold: Minimum confidence to include mapping (0.0-1.0)

    Returns:
        List of (environment_id, confidence_score) tuples, sorted by confidence DESC

    Examples:
        normalize_environment_description("high ceilings")
        → [("env.ae.high_ceiling", 0.95)]

        normalize_environment_description("high ceilings with daylighting")
        → [("env.ae.high_ceiling", 0.85), ("env.ae.daylighting", 0.88)]

        normalize_environment_description("spatial complexity")
        → [("env.complexity.spatial_entropy", 0.72)]
    """
```

### Implementation Approach

#### 1. Token-to-Environment Mapper

```python
# Initialize mapping from outcome_lookup.json + new environment mappings

ENVIRONMENT_TOKEN_MAP = {
    # Natural language token → (environment_id, baseline_confidence)
    "ceiling": ("env.ae.ceiling_height", 0.6),      # Low confidence (ambiguous)
    "high ceiling": ("env.ae.high_ceiling", 0.95),  # High confidence (specific)
    "low ceiling": ("env.ae.low_ceiling", 0.95),
    "daylighting": ("env.ae.daylighting", 0.90),
    "daylight": ("env.ae.daylighting", 0.85),
    "natural light": ("env.ae.daylighting", 0.80),
    "dark": ("env.ae.low_illuminance", 0.75),
    "glare": ("env.ae.glare_present", 0.90),
    "noise": ("env.acoustic.ambient_noise_level", 0.6),  # Low (many types)
    "acoustic": ("env.acoustic.ambient_noise_level", 0.7),
    "thermal comfort": ("env.thermal.thermal_comfort", 0.85),
    "temperature": ("env.thermal.temperature", 0.65),
    "material": ("env.material.material_identity", 0.5),  # Very ambiguous
    "wood": ("env.material.wood_prominent", 0.90),
    "concrete": ("env.ae.concrete_prominent", 0.90),
    "glass": ("env.ae.glass_prominent", 0.90),
    "color": ("env.visual.color", 0.6),
    "warm color": ("env.ae.warm_color_palette", 0.90),
    "cool color": ("env.ae.cool_color_palette", 0.90),
    "fractal": ("env.ae.fractal_like_pattern", 0.95),
    "wayfinding": ("env.ae.clear_exits_wayfinding_signage", 0.85),
    "crowded": ("env.ae.crowded_space", 0.85),
    "spatial entropy": ("env.complexity.spatial_entropy", 0.95),
    # ... additional mappings from the 442 environment_ids
}
```

#### 2. Confidence Scoring

Adjust baseline confidence based on:
- **Exact phrase match**: +0.15 (whole phrase, not just token)
- **Multi-token presence**: +0.10 (e.g., "high" + "ceiling" together)
- **Negation context**: -0.30 (e.g., "NOT crowded" → lower confidence)
- **Composite usage**: Compound tokens (high + ceiling) increase both components' confidence
- **Frequency in corpus**: If "ceiling" appears in 60% of papers, lower its baseline confidence

```python
def _score_environment_mapping(
    text: str,
    token: str,
    base_confidence: float,
    env_id: str
) -> float:
    """Adjust base confidence based on context."""

    score = base_confidence

    # Exact phrase match
    if f" {token} " in f" {text.lower()} ":
        score = min(1.0, score + 0.15)

    # Multi-token mapping (e.g., "high ceiling" vs just "ceiling")
    if " " in token:
        for sub_token in token.split():
            if sub_token in text.lower():
                score = min(1.0, score + 0.05)

    # Negation check
    if _has_negation(text, token):
        score = max(0.0, score - 0.30)

    return score
```

#### 3. Ambiguity Resolution

For ambiguous cases (multiple mappings with similar scores):

```python
def _resolve_ambiguity(
    candidates: List[Tuple[str, float]]  # [(env_id, score), ...]
) -> List[Tuple[str, float]]:
    """
    When multiple env_ids score within 0.1 of top candidate, return all.
    Caller decides whether to:
    - Take all candidates (conservative)
    - Take top-N (e.g., top 3)
    - Prompt for manual review (low confidence)
    - Skip if below threshold
    """

    if not candidates:
        return []

    top_score = candidates[0][1]

    # Return all within 0.1 of top
    return [(env_id, score) for env_id, score in candidates
            if score >= top_score - 0.10]
```

### Testing Strategy

```python
# In tests/test_environment_normalizer.py

test_cases = [
    # (input_text, expected_env_ids, test_name)

    ("High ceiling", ["env.ae.high_ceiling"], "simple_height"),
    ("Low ceiling", ["env.ae.low_ceiling"], "low_height"),
    ("High ceiling with daylighting",
     ["env.ae.high_ceiling", "env.ae.daylighting"],
     "compound_high_daylight"),

    ("Noisy office",
     ["env.acoustic.ambient_noise_level"],
     "acoustic_noise"),

    ("NOT crowded space",
     [],  # Negation → no match
     "negation_filtering"),

    ("Spatial complexity and wayfinding",
     ["env.complexity.spatial_entropy", "env.ae.clear_exits_wayfinding_signage"],
     "compound_spatial"),

    ("Material unknown",
     [],  # Too ambiguous, below threshold
     "ambiguity_filtered"),
]
```

---

## Component 2: Outcome ID Normalizer

### Design

File: `src/services/outcome_id_normalizer.py`

Function signature:
```python
def normalize_outcome_description(
    text: str,
    existing_outcome_ids: Optional[List[str]] = None,
    confidence_threshold: float = 0.7
) -> List[Tuple[str, float]]:
    """
    Map free-form outcome/consequence text to canonical outcome_id values.

    Args:
        text: Raw consequent text from extraction (e.g., "Improved attention and mood")
        existing_outcome_ids: (optional) Pre-extracted outcome IDs for reconciliation
        confidence_threshold: Minimum confidence to include mapping (0.0-1.0)

    Returns:
        List of (outcome_id, confidence_score) tuples, sorted by confidence DESC

    Examples:
        normalize_outcome_description("improved attention")
        → [("out.cog.attention", 0.92)]

        normalize_outcome_description("better mood and sleep")
        → [("out.affect.mood", 0.88), ("out.behav.sleep", 0.85)]
    """
```

### Implementation Approach

#### 1. Leverage outcome_lookup.json

The existing outcome_lookup.json provides a **partial solution**:

```json
{
  "lookup": {
    "cognitive": "cog",
    "attention": "cog",
    "focus": "cog.attention",
    "mood": "affect",
    "emotion": "affect",
    "sleep": "behav.sleep",
    ...
  }
}
```

This maps natural language → domain abbreviation (e.g., "attention" → "cog").

#### 2. Extend with Sub-domain Mapping

Create additional mapping to add specificity:

```python
OUTCOME_SUBDOMAIN_MAP = {
    # (domain, token) → (outcome_id, confidence)

    # Attention outcomes
    ("cog", "attention"): "out.cog.attention",
    ("cog", "selective attention"): "out.cog.attention.selective",
    ("cog", "sustained attention"): "out.cog.attention.sustained",
    ("cog", "focus"): "out.cog.attention",
    ("cog", "concentration"): "out.cog.attention",

    # Memory outcomes
    ("cog", "memory"): "out.cog.memory",
    ("cog", "working memory"): "out.cog.memory.working",
    ("cog", "recall"): "out.cog.memory",
    ("cog", "episodic memory"): "out.cog.memory",

    # Mood outcomes
    ("affect", "mood"): "out.affect.mood",
    ("affect", "positive mood"): "out.affect.mood.positive",
    ("affect", "negative mood"): "out.affect.mood.negative",
    ("affect", "happiness"): "out.affect.mood.positive",
    ("affect", "sadness"): "out.affect.mood.negative",

    # Behavioral outcomes
    ("behav", "sleep"): "out.behav.sleep",
    ("behav", "productivity"): "out.behav.productivity",
    ("behav", "performance"): "out.cog.performance",  # Note: cognitive domain

    # Health outcomes
    ("health", "wellbeing"): "out.health.wellbeing",
    ("health", "stress"): "out.affect.stress",

    # Physiological
    ("physio", "alertness"): "out.physio.alertness",
    ("physio", "fatigue"): "out.physio.fatigue",

    # Social
    ("social", "interaction"): "out.social.interaction",
    ("social", "collaboration"): "out.social.collaboration",
}
```

#### 3. Multi-Step Resolution

```python
def normalize_outcome_description(text: str, confidence_threshold: float = 0.7):
    """Three-step resolution with fallback."""

    candidates = []
    text_lower = text.lower()

    # Step 1: Use outcome_lookup to find domain
    for lookup_key, domain_abbr in outcome_lookup["lookup"].items():
        if lookup_key in text_lower:
            confidence = _score_lookup_match(text_lower, lookup_key, domain_abbr)

            # Step 2: Use subdomain map for more specificity
            for (domain, token), outcome_id in OUTCOME_SUBDOMAIN_MAP.items():
                if domain == domain_abbr and token in text_lower:
                    # Refine to specific outcome_id
                    sub_confidence = confidence + 0.10
                    candidates.append((outcome_id, min(1.0, sub_confidence)))

            # Fallback: use generic outcome_id for domain
            if domain_abbr == "cog":
                candidates.append((f"out.generic.cognition", confidence * 0.8))
            elif domain_abbr == "affect":
                candidates.append((f"out.generic.mood", confidence * 0.8))
            # ... etc for other domains

    # Step 3: Deduplicate and filter by confidence
    final = {}
    for outcome_id, score in candidates:
        final[outcome_id] = max(final.get(outcome_id, 0.0), score)

    return [(oid, score) for oid, score in sorted(final.items(),
                                                   key=lambda x: -x[1])
            if score >= confidence_threshold]
```

### Testing Strategy

```python
# In tests/test_outcome_normalizer.py

test_cases = [
    ("improved attention", ["out.cog.attention"], "simple_attention"),
    ("better mood", ["out.affect.mood"], "simple_mood"),

    ("improved selective attention and working memory",
     ["out.cog.attention.selective", "out.cog.memory.working"],
     "compound_specific"),

    ("happy and alert",
     ["out.affect.mood.positive", "out.physio.alertness"],
     "emotion_and_physio"),

    ("focus improved",
     ["out.cog.attention"],
     "synonyms_focus"),

    ("sleeping better",
     ["out.behav.sleep"],
     "verb_form_sleep"),

    ("productivity increased",
     ["out.behav.productivity"],
     "generic_productivity"),
]
```

---

## Component 3: Augmented outcome_lookup.json

### Current Structure

```json
{
  "schema": "outcome_lookup.v2",
  "generated_at": "2026-02-28T...",
  "source_version": "outcome_vocab.json",
  "lookup": {
    "cognitive": "cog",
    "attention": "cog",
    ...
  },
  "terms": [...]
}
```

### Proposed Enhancement

Add new section for compound mappings:

```json
{
  "schema": "outcome_lookup.v2_extended",
  "generated_at": "2026-03-01T...",
  "lookup": {
    "cognitive": "cog",
    "attention": "cog",
    "focus": "cog.attention",              ← NEW: synonym mapping
    "concentration": "cog.attention",      ← NEW: synonym
    "working memory": "cog.memory.working", ← NEW: compound
    "episodic memory": "cog.memory",       ← NEW: type variant
    "short-term memory": "cog.memory.working",
    "mood": "affect",
    "positive affect": "affect.mood.positive", ← NEW: specific variant
    "negative affect": "affect.mood.negative", ← NEW: specific variant
    "sleep quality": "behav.sleep",        ← NEW: aspect
    "performance": "cog.performance",
    ...
  },
  "compound_mappings": {
    "working memory": "cog.memory.working",  ← NEW: explicit compounds
    "selective attention": "cog.attention.selective",
    "sustained attention": "cog.attention.sustained",
    ...
  },
  "synonyms": {
    "focus": "attention",
    "concentration": "attention",
    "memory retrieval": "memory",
    "recall ability": "memory",
    ...
  }
}
```

---

## Component 4: Integration Point

### Where to Apply Normalization

The normalization should occur **at extraction ingestion time**, before beliefs are stored in the database.

Current pipeline:
```
papers/ → extract_from_pdf() → store_beliefs() → DB
```

Proposed pipeline:
```
papers/ → extract_from_pdf() → normalize_ids() → store_beliefs() → DB
                                   ↑
                         environment_id_normalizer
                         outcome_id_normalizer
```

### Handling Multiple Values

If a single belief has multiple environments/outcomes, store as pipe-delimited:

```json
{
  "belief_id": "pdf:doi:10.1016_j.health...",
  "environment_id": "env.ae.high_ceiling|env.ae.daylighting",
  "outcome_id": "out.cog.attention|out.affect.mood",
  "content": "High ceiling with daylighting improved attention and mood",
  "credence_value": 0.75
}
```

### Confidence Metadata

Optionally store confidence scores in epistemic_v2:

```json
{
  "epistemic_v2": {
    "normalization_v1": {
      "environment_id": [
        {"value": "env.ae.high_ceiling", "confidence": 0.85},
        {"value": "env.ae.daylighting", "confidence": 0.88}
      ],
      "outcome_id": [
        {"value": "out.cog.attention", "confidence": 0.92},
        {"value": "out.affect.mood", "confidence": 0.80}
      ],
      "normalized_at": "2026-03-01T...",
      "normalizer_version": "1.0"
    }
  }
}
```

---

## Component 5: Validation & Coverage Testing

### Test Suite

```
tests/
├── test_environment_id_normalizer.py
│   ├── test_simple_tokens()
│   ├── test_compound_phrases()
│   ├── test_negation_filtering()
│   ├── test_ambiguity_resolution()
│   └── test_corpus_statistics()
├── test_outcome_id_normalizer.py
│   ├── test_synonym_resolution()
│   ├── test_compound_outcomes()
│   ├── test_domain_routing()
│   └── test_specificity_hierarchy()
└── test_integration.py
    ├── test_against_4888_beliefs()
    ├── test_coverage_percentage()
    ├── test_false_positive_rate()
    └── test_confidence_distribution()
```

### Coverage Metrics

Track:
1. **Coverage percentage**: Fraction of 4,888 beliefs successfully normalized
2. **Confidence distribution**: Mean, median, std-dev of confidence scores
3. **False positive rate**: Normalized IDs that don't align with actual text
4. **Ambiguity cases**: Beliefs requiring manual review (<0.7 confidence)
5. **Comparison to baseline**: Template matcher coverage before/after normalization

Target metrics:
- Coverage: ≥90% of beliefs with at least one environment_id
- Coverage: ≥90% of beliefs with at least one outcome_id
- False positive rate: <5%
- Ambiguous cases: <15% of total

---

## Implementation Timeline

### Phase 1: Design & Mapping (Weeks 1-2)
- Analyze all 442 environment_ids to identify patterns
- Extract natural language mappings from paper corpus
- Design token → outcome_id mapping hierarchy
- Create comprehensive test cases

### Phase 2: Core Implementation (Weeks 3-4)
- Implement `environment_id_normalizer.py`
- Implement `outcome_id_normalizer.py`
- Create ENVIRONMENT_TOKEN_MAP and extend outcome_lookup.json
- Add confidence scoring logic

### Phase 3: Testing & Validation (Week 5)
- Run normalizer against all 4,888 beliefs
- Measure coverage, false positives, ambiguous cases
- Identify and fix edge cases
- Document exceptions and limitations

### Phase 4: Integration (Week 6)
- Integrate normalizers into extraction pipeline
- Add to ingestion workflow
- Deploy to production
- Monitor performance

### Phase 5: Validation Against Template Matcher (Week 7)
- Re-run template matcher on normalized IDs
- Measure coverage improvement (target: ≥75%)
- Compare to raw-text baseline (86.9%)
- Document findings

---

## Success Criteria

1. **Coverage**: ≥75% Tier2 coverage (vs. 29.9% current, 86.9% raw text)
2. **Coverage improvement**: ≥45 percentage points improvement from baseline
3. **Maintainability**: Mappings documented and version-controlled
4. **Scalability**: Can handle new beliefs without remapping
5. **Transparency**: Confidence scores stored for audit trail

---

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Ambiguous mappings (e.g., "spatial" could be many env_ids) | Confidence thresholding; multi-value storage; manual review queue |
| Vocabulary coverage incomplete (442 env_ids, unknown mappings) | Iterative expansion; fallback to raw text matching; active learning |
| False positives (mapping incorrect text) | Negation detection; confidence scoring; review process |
| Maintainability (mappings diverge from reality) | Automated validation; version control; documentation |
| Integration complexity | Phased rollout; fallback to raw matching; monitoring |

---

## References

- `finding_template_relevance.py` (lines 577-602): Current DB loading logic
- `contracts/outcome_vocab/outcome_lookup.json`: Existing vocabulary mapping
- Data statistics: 4,888 beliefs, 442 environment_ids, 30 outcome_ids
- Performance baseline: 86.9% (raw text), 29.9% (DB fields)

---

**Specification Version**: 1.0
**Status**: RESEARCH / NOT YET IMPLEMENTED
**Next Step**: Initiate Phase 1 (Design & Mapping)
