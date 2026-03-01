# Extraction Field Quality Framework v1.0

**Date**: 2026-02-28
**Status**: Specification (for panel review)
**Author**: Claude (Opus architecture)
**Audience**: David Kirsh, Expert Panel (P-TC), QA Infrastructure Developers
**Version**: 1.0

---

## Executive Summary

The Article Eater extraction pipeline (1,043 articles, ~50,000 findings) exhibits systematic quality problems across multiple extraction fields. This framework defines:

1. **Success conditions** for each finding field (empirically grounded in 100-file quality audit)
2. **Validation rules** (programmatic checks per APA reporting standards)
3. **Quality scoring system** (per-field, per-finding, per-article levels)
4. **Cleanup/re-extraction pipeline** (detection, flagging, scheduling, verification)
5. **Metrics dashboard** (track extraction quality over time)

**Key Findings from Quality Audit** (100-file sample, N=2,865 findings):
- Mean article quality score: 0.722 (SD: 0.146)
- Direction field chaos: 169+ unique values (should be 4: increase/decrease/no_effect/mixed)
- Direction↔effect_size inconsistencies: 66 instances in sample (direction says "increase", effect_size is negative)
- Vague antecedents: 32% of articles contain at least one antecedent like "Environmental features" or "Various conditions"
- Mixed direction + numeric effect_size: 31 instances (contradictory: if mixed, effect_size should be null)
- Quality action tracking is nascent (96/97 "accept", 1 "requeue" in sample)

**Critical Insight**: The stimulus field (antecedent) is just the tip of the iceberg. The Gemini-based extraction produces findings with systematic problems across *all* major fields (direction, effect_size, claim_type, measure_type, statistical fields). This framework addresses the whole extraction.

---

## Part 1: Success Conditions for Each Field

Each field below specifies what constitutes "good" and what constitutes "bad" based on:
- APA 7th edition reporting standards
- Domain-specific conventions (cognitive science, environmental psychology)
- Empirical analysis of observed extraction failures
- Logical consistency checks

### 1.1 **antecedent** (Independent Variable / Stimulus Description)

**What "Good" Looks Like:**
- Describes an environmental condition, architectural feature, or manipulated variable
- Specific enough to be actionable (e.g., "window size (3.5 m²)" not "window")
- Not a demographic category (age, gender, education) used as IV
- Not a dependent variable disguised as IV
- Not vague/catch-all (no "environmental features", "various", "multiple factors")
- If compound (multiple factors), each component is clearly environmental (not outcome-related)

**What "Bad" Looks Like:**
- "Environmental features" (too vague)
- "Various unisensory features (e.g., auditory pitch, visual size, ...)" (lists outcomes, not conditions)
- "Implantable cuff electrodes in forearm" in plants_greenery category (misclassified source)
- Confuses IV and DV (e.g., "mental health as IV")
- Contains outcome language (e.g., "improved well-being" as antecedent)
- Null/empty

**Validation Rules:**

```python
def validate_antecedent(antecedent: str, consequent: str, domains: list[str],
                        claim_type: str) -> tuple[bool, list[str]]:
    """
    Returns (is_valid, list_of_errors)
    """
    errors = []

    # Rule A1: Must not be null or empty
    if not antecedent or not isinstance(antecedent, str) or not antecedent.strip():
        errors.append("A1_NULL_ANTECEDENT")

    # Rule A2: Check vagueness markers
    vague_patterns = [
        r'environmental features',
        r'various\s+\w+',
        r'multiple\s+factors',
        r'different\s+\w+',
        r'various\s+conditions',
        r'^conditions?$',
        r'^factors?$',
        r'features',  # bare, without specifying type
    ]
    for pattern in vague_patterns:
        if re.search(pattern, antecedent, re.IGNORECASE):
            errors.append(f"A2_VAGUE_ANTECEDENT:{pattern}")
            break

    # Rule A3: Check for outcome language in antecedent
    # Common outcome words that shouldn't appear as antecedents
    outcome_markers = [
        'improved', 'increased well-being', 'better', 'worse', 'reduced stress',
        'better performance', 'higher anxiety', 'lower depression'
    ]
    for marker in outcome_markers:
        if marker.lower() in antecedent.lower():
            errors.append(f"A3_OUTCOME_IN_ANTECEDENT:{marker}")
            break

    # Rule A4: Check for demographic misuse
    # Some demographics can be legitimate IVs (e.g., architectural style preference by age),
    # but bare demographics are problematic
    demographic_patterns = [
        r'^age\s+group',
        r'^gender',
        r'^education\s+level',
        r'^socioeconomic',
    ]
    # Only flag if claim_type is 'causal' or 'empirical_finding' (not correlational)
    if claim_type in ['causal', 'empirical_finding']:
        for pattern in demographic_patterns:
            if re.search(pattern, antecedent, re.IGNORECASE):
                errors.append(f"A4_BARE_DEMOGRAPHIC:{pattern}")
                break

    # Rule A5: Consistency with domains
    # If antecedent describes something from domains, make sense
    # E.g., if domain is 'A6_Visual_Form' and antecedent is about acoustic, flag
    domain_keywords = {
        'A1_Materials': ['material', 'surface', 'texture', 'brick', 'wood', 'stone'],
        'A2_Spatial_Layout': ['layout', 'density', 'open', 'closed', 'integration'],
        'A3_Lighting': ['light', 'daylight', 'illumination', 'luminance', 'CCT'],
        'A6_Visual_Form': ['visual', 'complexity', 'proportion', 'symmetry', 'form'],
        'A7_Haptic_Thermal': ['temperature', 'thermal', 'haptic', 'touch', 'warmth'],
    }
    # Simple check: if antecedent has strong domain markers, at least one domain should match
    # This is a warning (not error) if no match
    # Omitted for now (too complex without external vocab)

    # Rule A6: Length/specificity check
    # Antecedents should be 5-200 characters (not too vague, not word salad)
    if len(antecedent.strip()) < 5:
        errors.append(f"A6_TOO_SHORT:{len(antecedent)}")
    if len(antecedent.strip()) > 500:
        errors.append(f"A6_TOO_LONG:{len(antecedent)}")

    return len(errors) == 0, errors
```

**Severity**: Critical — Vague or incorrect antecedents invalidate evidence extraction.

**APA Relevance**: APA 7th ed. §3.6 requires clear specification of variables. Antecedents must meet the "variables were operationalized as..." standard.

---

### 1.2 **consequent** (Dependent Variable / Outcome Description)

**What "Good" Looks Like:**
- Describes a measured outcome or dependent variable
- Maps to outcome vocabulary (health, affect, cognition, behavior, perception, physiology)
- Specific outcome name or construct (e.g., "self-reported stress" not just "stress")
- Consistent with outcome_domain and outcome_match_type fields
- Not a restatement or synonym of antecedent
- If multiple outcomes reported, each distinct

**What "Bad" Looks Like:**
- Null/empty
- Restatement of IV (e.g., "exposure to more windows" when antecedent is "window area")
- Vague (e.g., "perception" without specifying what aspect)
- Outcome vocabulary mismatch (consequent says "cognitive performance" but outcome_domain says "physiological")
- Impossible outcome for context (e.g., "cortisol levels" for a purely behavioral study)

**Validation Rules:**

```python
def validate_consequent(consequent: str, antecedent: str, outcome_domain: str,
                       measure_type: str) -> tuple[bool, list[str]]:
    """
    Returns (is_valid, list_of_errors)
    """
    errors = []

    # Rule C1: Must not be null or empty
    if not consequent or not isinstance(consequent, str) or not consequent.strip():
        errors.append("C1_NULL_CONSEQUENT")
        return False, errors

    # Rule C2: No restatement of antecedent
    # Simple string similarity check
    antecedent_tokens = set(antecedent.lower().split())
    consequent_tokens = set(consequent.lower().split())
    overlap = antecedent_tokens & consequent_tokens
    if len(overlap) > len(consequent_tokens) * 0.6:  # >60% overlap
        errors.append(f"C2_RESTATEMENT_OF_ANTECEDENT:overlap={len(overlap)}/{len(consequent_tokens)}")

    # Rule C3: Outcome vocabulary check
    # Define canonical outcome domains
    valid_outcome_domains = {
        'health': ['health', 'well-being', 'wellbeing', 'illness', 'disease'],
        'affect': ['mood', 'emotion', 'affect', 'anxiety', 'depression', 'stress', 'happiness'],
        'cognition': ['memory', 'attention', 'working memory', 'cognitive', 'mental',
                     'learning', 'comprehension', 'performance'],
        'behavior': ['behavior', 'action', 'activity', 'engagement', 'avoidance', 'approach'],
        'perception': ['perception', 'aesthetic', 'preference', 'liking', 'judgment', 'beauty'],
        'physiology': ['cortisol', 'heart rate', 'blood pressure', 'EEG', 'fMRI', 'pupil',
                      'galvanic', 'respiration', 'HPA axis'],
    }

    if outcome_domain and outcome_domain in valid_outcome_domains:
        domain_keywords = valid_outcome_domains[outcome_domain]
        if not any(kw in consequent.lower() for kw in domain_keywords):
            errors.append(f"C3_DOMAIN_MISMATCH:stated={outcome_domain},keywords_not_found")

    # Rule C4: Consistency with measure_type
    # If measure_type is 'physiological', consequent should contain physiological terms
    if measure_type == 'physiological':
        physio_markers = ['cortisol', 'heart rate', 'EEG', 'fMRI', 'pupil', 'respiration',
                         'blood pressure', 'galvanic', 'HPA', 'amygdala']
        if not any(marker in consequent.lower() for marker in physio_markers):
            errors.append(f"C4_MEASURE_TYPE_MISMATCH:type=physiological,no_physio_terms")

    # Rule C5: Length check
    if len(consequent.strip()) < 3:
        errors.append(f"C5_TOO_SHORT:{len(consequent)}")
    if len(consequent.strip()) > 300:
        errors.append(f"C5_TOO_LONG:{len(consequent)}")

    return len(errors) == 0, errors
```

**Severity**: Critical — Invalid outcomes break the evidence model.

---

### 1.3 **direction** (Effect Direction)

**What "Good" Looks Like:**
- One of exactly 4 canonical values: `increase`, `decrease`, `no_effect`, `mixed`
- Consistent with reported effect_size (positive effect_size → increase, negative → decrease)
- Consistent with p_value and statistical significance
- Aligns with quoted mechanism/interpretation from paper

**What "Bad" Looks Like:**
- Non-canonical value (169 unique values found in audit: "cause", "modulates", "enhance", "Leads to", "causal", "associated", etc.)
- `mixed` paired with numeric effect_size (contradictory)
- Contradicts effect_size sign (direction="increase", effect_size=-0.45)
- Null/missing for empirical findings
- Claims effect direction but p_value indicates non-significance

**Validation Rules:**

```python
def validate_direction(direction: str, effect_size: float | None,
                      p_value: float | None, claim_type: str) -> tuple[bool, list[str]]:
    """
    Returns (is_valid, list_of_errors)
    """
    errors = []
    warnings = []

    # Rule D1: Canonical values only
    canonical_directions = {'increase', 'decrease', 'no_effect', 'mixed', None}
    if direction not in canonical_directions:
        errors.append(f"D1_INVALID_DIRECTION:{direction}")
        return False, errors

    # Rule D2: Mixed direction must have null effect_size
    if direction == 'mixed' and effect_size is not None:
        errors.append(f"D2_MIXED_WITH_EFFECT_SIZE:effect_size={effect_size}")

    # Rule D3: Effect size / direction consistency
    # Allow small tolerance for rounding (e.g., effect_size=-0.001)
    if effect_size is not None and direction is not None:
        tolerance = 0.01
        if direction == 'increase':
            if effect_size < -tolerance:
                errors.append(f"D3_DIRECTION_EFFECT_MISMATCH:direction=increase,effect_size={effect_size}")
        elif direction == 'decrease':
            if effect_size > tolerance:
                errors.append(f"D3_DIRECTION_EFFECT_MISMATCH:direction=decrease,effect_size={effect_size}")
        elif direction == 'no_effect':
            if abs(effect_size) > 0.05:  # Small effect size acceptable for "no_effect"
                warnings.append(f"D3_WARNING_NO_EFFECT_WITH_ES:effect_size={effect_size}")

    # Rule D4: P-value consistency (for empirical findings only)
    if claim_type in ['causal', 'empirical_finding', 'associational']:
        if p_value is not None:
            if p_value < 0.05 and direction == 'no_effect':
                errors.append(f"D4_SIGNIFICANCE_MISMATCH:p={p_value},direction=no_effect")
            if p_value >= 0.05 and direction in ['increase', 'decrease']:
                warnings.append(f"D4_WARNING:p={p_value}>=0.05,direction={direction}")

    # Rule D5: Required for empirical claims
    if claim_type in ['causal', 'empirical_finding'] and direction is None:
        errors.append(f"D5_NULL_DIRECTION_FOR_EMPIRICAL_CLAIM")

    return len(errors) == 0, errors, warnings
```

**Severity**: Critical — Direction is core to evidence synthesis.

**Note on 169 Unique Values**: This is not a parsing problem (Gemini is correctly filling `direction`). Rather, the extraction prompt may be under-constraining the field, or the training data contained non-canonical values. Recommend adding explicit instruction to Gemini: "direction MUST be one of: increase, decrease, no_effect, mixed. Do not use synonyms like 'enhance', 'facilitate', 'cause', 'modulate'."

---

### 1.4 **claim_type** (Classification of Claim)

**What "Good" Looks Like:**
- One of canonical values: `empirical_finding`, `theoretical_proposition`, `causal`, `associational`, `synthesized`, `narrative`, `qualitative_theme`, `null`, others (per article_type_contract.py)
- Consistent with presence/absence of statistics (empirical_finding should have p_value or effect_size)
- Consistent with article type (review articles should have more synthesized/narrative claims)
- Aligned with evidence_type if present

**What "Bad" Looks Like:**
- Non-canonical value
- `empirical_finding` with no statistics (p_value, effect_size, test_statistic all null)
- `theoretical_proposition` in empirical article extract claiming empirical results
- Null when claim is clearly classified elsewhere
- Inconsistent with article metadata

**Validation Rules:**

```python
def validate_claim_type(claim_type: str, p_value: float | None,
                       effect_size: float | None, test_statistic: str | None,
                       article_type: str) -> tuple[bool, list[str]]:
    """
    Returns (is_valid, list_of_errors)
    """
    errors = []
    warnings = []

    # Rule CT1: Canonical values
    canonical_claim_types = {
        'empirical_finding', 'theoretical_proposition', 'causal', 'associational',
        'synthesized', 'narrative', 'qualitative_theme', 'null', 'moderated',
        'pooled_effect', 'cited', 'vote_count', 'methodological', 'derived_guideline',
        'claimed', 'statistical', 'comparative', 'limitation', 'theoretical_critique'
    }
    if claim_type and claim_type not in canonical_claim_types:
        errors.append(f"CT1_INVALID_CLAIM_TYPE:{claim_type}")

    # Rule CT2: Empirical findings must have statistics
    if claim_type == 'empirical_finding':
        has_stats = any([p_value is not None, effect_size is not None, test_statistic is not None])
        if not has_stats:
            errors.append(f"CT2_EMPIRICAL_WITHOUT_STATS")

    # Rule CT3: Coherence with article type
    # Empirical articles (RCT, observational) should have mostly empirical/causal claims
    if article_type in ['empirical_research', 'experimental']:
        if claim_type in ['narrative', 'theoretical_proposition']:
            warnings.append(f"CT3_ARTICLE_CLAIM_TYPE_MISMATCH:article={article_type},claim={claim_type}")

    # Rule CT4: Null claim type for clearly classified claims
    if claim_type == 'null':
        # This is acceptable for ambiguous findings, but flag if pattern is high
        pass

    return len(errors) == 0, errors, warnings
```

**Severity**: Warning (when inconsistent with article type) / Critical (when canonical value violated).

---

### 1.5 **measure_type** (How outcome was measured)

**What "Good" Looks Like:**
- One of: `self_report`, `behavioral`, `physiological`, `cognitive_task`, `observational`, `mixed`, `null`
- Consistent with consequent field (e.g., "self_report" if consequent is "perceived stress")
- Consistent with measurement_instrument if available
- Aligns with claim_type (empirical_findings should have measure_type ≠ null)

**What "Bad" Looks Like:**
- Non-canonical value
- Physiological measure claimed but no physiological term in consequent
- Self-report claimed but outcome is objective (memory encoding time)
- Null for empirical_finding claims

**Validation Rules:**

```python
def validate_measure_type(measure_type: str, consequent: str, claim_type: str) -> tuple[bool, list[str]]:
    """
    Returns (is_valid, list_of_errors)
    """
    errors = []
    warnings = []

    # Rule MT1: Canonical values
    canonical_measures = {
        'self_report', 'behavioral', 'physiological', 'cognitive_task',
        'observational', 'mixed', None
    }
    if measure_type not in canonical_measures:
        errors.append(f"MT1_INVALID_MEASURE_TYPE:{measure_type}")

    # Rule MT2: Empirical findings should have measure_type
    if claim_type in ['empirical_finding', 'causal'] and measure_type is None:
        errors.append(f"MT2_NULL_MEASURE_FOR_EMPIRICAL")

    # Rule MT3: Consistency with consequent
    # Sanity check: does measure type make sense for the outcome?
    if measure_type == 'physiological':
        physio_terms = ['cortisol', 'heart rate', 'EEG', 'blood pressure', 'pupil']
        if not any(term in consequent.lower() for term in physio_terms):
            warnings.append(f"MT3_MEASURE_CONSEQUENT_MISMATCH:measure=physiological,no_physio_in_consequent")

    if measure_type == 'behavioral':
        # Behavioral outcomes should describe actions, movements, choices
        behavioral_terms = ['behavior', 'action', 'movement', 'choice', 'approach', 'avoidance']
        if not any(term in consequent.lower() for term in behavioral_terms):
            warnings.append(f"MT3_MEASURE_CONSEQUENT_MISMATCH:measure=behavioral,weak_behavioral_language")

    return len(errors) == 0, errors, warnings
```

**Severity**: Warning for mismatches, Critical if null for empirical claims.

---

### 1.6 **p_value** (Statistical Significance)

**What "Good" Looks Like:**
- Numeric value in range [0, 1]
- Typically reported as decimals: p < 0.05, p = 0.032, etc.
- Consistent with direction and effect_size (p < 0.05 suggests meaningful effect, not no_effect)
- Present for empirical_finding and causal claims
- Consistent with test_statistic if available

**What "Bad" Looks Like:**
- Non-numeric (e.g., "< 0.05" stored as string, not float)
- Out of range (p = 1.5, p = -0.02)
- Contradicts direction (p = 0.8, direction = "increase")
- Present but claim_type is "narrative" or "theoretical"
- Null for empirical findings

**Validation Rules:**

```python
def validate_p_value(p_value: float | str | None, direction: str,
                    claim_type: str, test_statistic: str | None) -> tuple[bool, list[str]]:
    """
    Returns (is_valid, list_of_errors)
    """
    errors = []
    warnings = []

    # Rule PV1: Type and range
    if p_value is not None:
        try:
            pv = float(p_value)
            if pv < 0 or pv > 1:
                errors.append(f"PV1_OUT_OF_RANGE:p={pv}")
        except (TypeError, ValueError):
            if isinstance(p_value, str):
                # Try to parse strings like "< 0.05" or "<0.001"
                match = re.search(r'<?\s*(0\.\d+)', str(p_value))
                if match:
                    warnings.append(f"PV1_STRING_FORMAT:consider_converting_to_float")
                else:
                    errors.append(f"PV1_UNPARSEABLE:p={p_value}")
            else:
                errors.append(f"PV1_INVALID_TYPE:{type(p_value)}")

    # Rule PV2: Consistency with direction
    if p_value is not None and direction is not None:
        try:
            pv = float(p_value)
            if pv >= 0.05:  # Not significant
                if direction in ['increase', 'decrease']:
                    warnings.append(f"PV2_DIRECTION_MISMATCH:p={pv}>=0.05,direction={direction}")
            elif pv < 0.05 and direction == 'no_effect':
                errors.append(f"PV2_SIGNIFICANCE_MISMATCH:p={pv}<0.05,direction=no_effect")
        except (TypeError, ValueError):
            pass  # Skip if p_value couldn't be converted

    # Rule PV3: Empirical findings should have p_value
    if claim_type in ['empirical_finding', 'causal'] and p_value is None:
        errors.append(f"PV3_NULL_P_FOR_EMPIRICAL")

    # Rule PV4: Non-empirical claims should not have p_value
    if claim_type in ['narrative', 'theoretical_proposition'] and p_value is not None:
        warnings.append(f"PV4_P_VALUE_IN_NARRATIVE_CLAIM")

    # Rule PV5: Consistency with test_statistic (if present)
    # This is weak (hard to check without full ANOVA table), just flag if contradictory
    if test_statistic and p_value is not None:
        # E.g., if test_statistic includes "ns" or "not significant" but p < 0.05
        if 'ns' in str(test_statistic).lower() and float(p_value) < 0.05:
            warnings.append(f"PV5_TEST_STAT_P_MISMATCH:ts_says_ns,p_says_significant")

    return len(errors) == 0, errors, warnings
```

**Severity**: Critical for empirical findings.

**APA Relevance**: APA 7th ed. §6.6 mandates p-value reporting. Format should be "p = .032" (not "p < 0.05" unless that's what paper reported).

---

### 1.7 **effect_size** (Magnitude of Effect)

**What "Good" Looks Like:**
- Numeric value
- In reasonable range for stated effect_size_type:
  - Cohen's d: typically |d| ≤ 2.0 (|d| > 3 is extreme)
  - eta-squared (η²): [0, 1]
  - r (correlation): [-1, 1]
  - odds ratio: [0, ∞) (typically 0.1 to 10)
  - Cohen's f: [0, ∞) typically [0, 0.5]
- Sign consistent with direction (positive ES → "increase", negative → "decrease")
- Present for empirical_finding claims
- Paired with effect_size_type

**What "Bad" Looks Like:**
- Out of range (η² = 1.5, r = 2.3)
- Sign mismatched with direction (direction="increase", ES=-0.45)
- Null for empirical findings
- Paired with direction="mixed" (makes no sense)
- Implausible for context (Cohen's d = 5.2 for questionnaire item)

**Validation Rules:**

```python
def validate_effect_size(effect_size: float | None, effect_size_type: str | None,
                        direction: str, claim_type: str) -> tuple[bool, list[str]]:
    """
    Returns (is_valid, list_of_errors)
    """
    errors = []
    warnings = []

    # Rule ES1: Type and range checks
    if effect_size is not None:
        try:
            es = float(effect_size)

            # Validate against effect_size_type
            if effect_size_type == "eta_squared" or effect_size_type == "eta-squared":
                if es < 0 or es > 1:
                    errors.append(f"ES1_RANGE:type={effect_size_type},value={es},expected=[0,1]")

            elif effect_size_type == "r_correlation" or effect_size_type == "r":
                if es < -1 or es > 1:
                    errors.append(f"ES1_RANGE:type={effect_size_type},value={es},expected=[-1,1]")

            elif effect_size_type in ["cohen_d", "Cohen's d", "d"]:
                # Cohen's d can theoretically go higher, but >3 is extreme
                if abs(es) > 3:
                    warnings.append(f"ES1_EXTREME:type={effect_size_type},value={es},>3_is_unusual")

            elif effect_size_type == "odds_ratio":
                # Odds ratio should be positive
                if es <= 0:
                    errors.append(f"ES1_RANGE:type={effect_size_type},value={es},expected>0")
                if es > 100:
                    warnings.append(f"ES1_EXTREME:type={effect_size_type},value={es},>100_is_unusual")

            elif effect_size_type in ["cohen_f", "f"]:
                if es < 0:
                    errors.append(f"ES1_RANGE:type={effect_size_type},value={es},expected>=0")
                if es > 1:
                    warnings.append(f"ES1_RANGE:type={effect_size_type},value={es},typically<=0.5")

        except (TypeError, ValueError):
            errors.append(f"ES1_INVALID_TYPE:{type(effect_size)}")

    # Rule ES2: Direction consistency
    if effect_size is not None and direction is not None:
        es = float(effect_size)
        tolerance = 0.01
        if direction == 'increase':
            if es < -tolerance:
                errors.append(f"ES2_DIRECTION_MISMATCH:direction=increase,es={es}")
        elif direction == 'decrease':
            if es > tolerance:
                errors.append(f"ES2_DIRECTION_MISMATCH:direction=decrease,es={es}")
        elif direction == 'no_effect':
            if abs(es) > 0.05:
                warnings.append(f"ES2_WARNING:direction=no_effect,but_es={es}")
        elif direction == 'mixed':
            errors.append(f"ES2_MIXED_WITH_EFFECT_SIZE:direction=mixed,es={es}")

    # Rule ES3: Empirical claims should have effect_size
    if claim_type in ['empirical_finding', 'causal'] and effect_size is None:
        errors.append(f"ES3_NULL_ES_FOR_EMPIRICAL")

    # Rule ES4: Type should be paired with effect_size
    if effect_size is not None and effect_size_type is None:
        errors.append(f"ES4_NULL_ES_TYPE_WITH_ES")

    return len(errors) == 0, errors, warnings
```

**Severity**: Critical for empirical findings.

**APA Relevance**: APA 7th ed. §6.8 mandates effect size reporting. Must include both ES value and type (d, η², r, etc.).

---

### 1.8 **effect_size_type** (Name of the Effect Size Statistic)

**What "Good" Looks Like:**
- One of: `Cohen's d`, `eta_squared`, `r`, `odds_ratio`, `Cohen's f`, `Cramer's V`, `partial eta-squared`, others (standardized)
- Paired with effect_size value
- Consistent with study design (e.g., ANOVA → η² or f, t-test → d)
- Formatted consistently

**What "Bad" Looks Like:**
- Non-standard name (e.g., "d" vs "Cohen's d" vs "cohen_d" — three versions for same thing)
- Null when effect_size is provided
- Type doesn't match design (ANOVA reported with Cohen's d as primary)
- Misspelled (e.g., "cohens d" instead of "Cohen's d")

**Validation Rules:**

```python
def validate_effect_size_type(effect_size_type: str | None, effect_size: float | None,
                             test_statistic: str | None) -> tuple[bool, list[str]]:
    """
    Returns (is_valid, list_of_errors)
    """
    errors = []
    warnings = []

    # Rule EST1: Required if effect_size present
    if effect_size is not None and effect_size_type is None:
        errors.append(f"EST1_NULL_TYPE_WITH_ES")

    # Rule EST2: Canonical/normalized values
    canonical_es_types = {
        "Cohen's d", "eta_squared", "partial_eta_squared", "eta-squared",
        "r", "r_correlation", "correlation_coefficient",
        "odds_ratio", "Cohen's f", "Cramer's V", "phi",
        "Hedges' g", "Cliff's delta", "Glass' delta"
    }

    if effect_size_type:
        # Normalize common variants
        normalized = effect_size_type.strip().lower()

        # Check for common typos/variants
        if normalized in ['cohens d', 'cohen d', 'd']:
            warnings.append(f"EST2_NON_STANDARD:est={effect_size_type},consider=Cohen's d")
        elif normalized in ['eta squared', 'eta2', 'eta^2']:
            warnings.append(f"EST2_NON_STANDARD:est={effect_size_type},consider=eta_squared")
        elif normalized in ['partial eta squared', 'partial_eta2']:
            warnings.append(f"EST2_NON_STANDARD:est={effect_size_type},consider=partial_eta_squared")

        if effect_size_type not in canonical_es_types:
            # Allow if clearly identifiable as variant
            if normalized not in [x.lower() for x in canonical_es_types]:
                warnings.append(f"EST2_UNUSUAL_TYPE:{effect_size_type}")

    return len(errors) == 0, errors, warnings
```

**Severity**: Warning (standardization) to Critical (consistency).

---

### 1.9 **sample_size** (N or number of participants)

**What "Good" Looks Like:**
- Positive integer (N ≥ 1)
- Reasonable for study design (N ≥ 10 for empirical, N = null for narrative)
- Consistent with reported statistics (e.g., F(1,30) implies N ≥ 32)
- If meta-analysis, should match k (number of studies) and n_total

**What "Bad" Looks Like:**
- Non-integer (N = 32.5)
- Negative or zero
- Implausible (N = 1000 for qualitative interview study)
- Null for empirical_finding
- Inconsistent with test_statistic (F(1,30) but N = 20)

**Validation Rules:**

```python
def validate_sample_size(sample_size: int | float | None, k: int | None,
                        claim_type: str) -> tuple[bool, list[str]]:
    """
    Returns (is_valid, list_of_errors)
    """
    errors = []
    warnings = []

    # Rule SS1: Type and range
    if sample_size is not None:
        try:
            n = int(sample_size)
            if n <= 0:
                errors.append(f"SS1_NON_POSITIVE:n={n}")
            elif n > 100000:
                errors.append(f"SS1_IMPLAUSIBLE:n={n},likely_data_entry_error")
        except (TypeError, ValueError):
            errors.append(f"SS1_NON_INTEGER:{sample_size}")

    # Rule SS2: Empirical findings should have sample_size
    if claim_type in ['empirical_finding', 'causal'] and sample_size is None:
        warnings.append(f"SS2_NULL_N_FOR_EMPIRICAL")

    # Rule SS3: For meta-analyses, sample_size should equal sum of k studies' Ns (if k present)
    # This is hard to validate without full data, skip for now

    # Rule SS4: Narrative/theoretical claims should not have sample_size
    if claim_type in ['narrative', 'theoretical_proposition'] and sample_size is not None:
        warnings.append(f"SS4_N_IN_NARRATIVE_CLAIM")

    return len(errors) == 0, errors, warnings
```

**Severity**: Warning for empirical findings without N, Critical if invalid type.

**APA Relevance**: APA 7th ed. §7.1 requires N reporting for all empirical studies.

---

### 1.10 **confidence_interval** (CI for Effect Estimate)

**What "Good" Looks Like:**
- Array/list of [lower, upper] bounds
- lower < upper
- Both numeric
- Typically narrow (width reflects precision)
- Consistent with effect_size (ES within [lower, upper])
- Present for large empirical studies

**What "Bad" Looks Like:**
- Not an array/list format
- lower ≥ upper
- Non-numeric values
- Null for major findings
- CI doesn't contain effect_size (e.g., ES=0.5, CI=[0.1, 0.3])
- Implausible width (CI=[0.001, 0.999])

**Validation Rules:**

```python
def validate_confidence_interval(ci: list | tuple | None, effect_size: float | None) -> tuple[bool, list[str]]:
    """
    Returns (is_valid, list_of_errors)
    """
    errors = []
    warnings = []

    # Rule CI1: Format and structure
    if ci is not None:
        if not isinstance(ci, (list, tuple)):
            errors.append(f"CI1_INVALID_TYPE:{type(ci)}")
            return False, errors

        if len(ci) != 2:
            errors.append(f"CI1_WRONG_LENGTH:len={len(ci)},expected=2")
            return False, errors

        try:
            lower, upper = float(ci[0]), float(ci[1])

            # Rule CI2: Ordering
            if lower >= upper:
                errors.append(f"CI2_BAD_ORDER:lower={lower},upper={upper}")

            # Rule CI3: Consistency with effect_size
            if effect_size is not None:
                es = float(effect_size)
                if not (lower <= es <= upper):
                    warnings.append(f"CI3_ES_OUTSIDE_CI:es={es},ci=[{lower},{upper}]")

            # Rule CI4: Plausibility (width shouldn't be enormous)
            width = upper - lower
            if width > 100:
                warnings.append(f"CI4_VERY_WIDE:width={width},may_indicate_low_precision")

        except (TypeError, ValueError):
            errors.append(f"CI1_NON_NUMERIC:ci={ci}")

    return len(errors) == 0, errors, warnings
```

**Severity**: Warning (precision) to Critical (consistency).

**APA Relevance**: APA 7th ed. §6.8 recommends CI reporting for effect size (increasingly standard, though not mandatory in all fields).

---

### 1.11 **test_statistic** (Name and Value of Statistical Test)

**What "Good" Looks Like:**
- String format: "test_name(df1, df2) = value, p = ..."
- Examples: "t(30) = 2.45", "F(2, 60) = 5.32", "χ²(3) = 7.21"
- Test name corresponds to design (t for t-test, F for ANOVA, χ² for chi-square)
- Degrees of freedom consistent with reported N
- Value consistent with reported p_value

**What "Bad" Looks Like:**
- Bare number (32.5 with no test name)
- Non-standard format
- Test doesn't match design
- DF inconsistent with N (t(50) with N=30)
- Null for empirical findings from tables
- Contradicts p_value (t = 0.5, p < 0.001)

**Validation Rules:**

```python
def validate_test_statistic(test_statistic: str | None, p_value: float | None,
                           sample_size: int | None) -> tuple[bool, list[str]]:
    """
    Returns (is_valid, list_of_errors)
    """
    errors = []
    warnings = []

    # Rule TS1: Format/structure
    if test_statistic is not None:
        ts = str(test_statistic).strip()

        # Should contain a test name or abbreviation
        # Common patterns: t(df), F(df1, df2), χ²(df), z, r, etc.
        test_patterns = [r't\(\d+\)', r'F\(\d+,\s*\d+\)', r'χ²\(\d+\)', r'chi\d*\(\d+\)',
                        r'z\s*=', r'r\s*=', r'Z\(\d+\)']

        has_test_pattern = any(re.search(pattern, ts) for pattern in test_patterns)
        if not has_test_pattern:
            # Could still be valid (just unusual format), warn only
            warnings.append(f"TS1_UNUSUAL_FORMAT:{ts}")

        # Rule TS2: Extract and validate degrees of freedom
        # Look for patterns like (df) or (df1, df2)
        df_match = re.search(r'\((\d+)(?:,\s*(\d+))?\)', ts)
        if df_match and sample_size is not None:
            df1, df2 = df_match.groups()
            df1 = int(df1)
            n = int(sample_size)
            # Rough check: df should be <= n
            if df1 > n:
                warnings.append(f"TS2_DF_VS_N:df={df1},n={n}")

        # Rule TS3: Consistency with p_value (if both present)
        if p_value is not None:
            # Extract numeric value from test_statistic
            # E.g., "t(30) = 2.45" → extract 2.45
            value_match = re.search(r'=\s*([\d\.\-]+)', ts)
            if value_match:
                try:
                    ts_value = float(value_match.group(1))
                    pv = float(p_value)

                    # Very weak check: if p is highly significant (<0.001),
                    # test statistic should be substantial (|value| > 1.96 for z)
                    # This is rough because different tests have different scales
                    if pv < 0.001 and abs(ts_value) < 1:
                        warnings.append(f"TS3_VALUE_P_MISMATCH:ts={ts_value},p={pv}")
                except (ValueError, AttributeError):
                    pass

    # Rule TS4: Empirical findings from tables should have test_statistic
    if test_statistic is None and sample_size is not None:
        warnings.append(f"TS4_NULL_TS_WITH_DATA")

    return len(errors) == 0, errors, warnings
```

**Severity**: Warning (consistency) to Critical (consistency with p).

**APA Relevance**: APA 7th ed. §6.7 mandates test statistic reporting. Format: "t(df) = value, p = .xxx"

---

## Part 2: Field-Level Quality Scoring System

For each finding, compute a **field-level score** based on validation results.

```python
def compute_field_scores(finding: dict) -> dict[str, float]:
    """
    For each field, return a quality score in [0, 1].
    1.0 = no errors or warnings
    0.7 = warnings only (data usable with caveats)
    0.3 = errors (field unreliable)
    0.0 = critical error (field invalid)
    """
    field_scores = {}

    # Antecedent
    valid, errors = validate_antecedent(finding.get('antecedent'),
                                       finding.get('consequent'),
                                       finding.get('domains', []),
                                       finding.get('claim_type'))
    if not valid:
        field_scores['antecedent'] = 0.0 if 'A1_NULL' in str(errors) else 0.3
    else:
        field_scores['antecedent'] = 1.0

    # Consequent
    valid, errors = validate_consequent(finding.get('consequent'),
                                       finding.get('antecedent'),
                                       finding.get('outcome_domain'),
                                       finding.get('measure_type'))
    if not valid:
        field_scores['consequent'] = 0.0 if 'C1_NULL' in str(errors) else 0.3
    else:
        field_scores['consequent'] = 1.0

    # Direction (critical field)
    valid, errors, warnings = validate_direction(finding.get('direction'),
                                                 finding.get('effect_size'),
                                                 finding.get('p_value'),
                                                 finding.get('claim_type'))
    if not valid:
        field_scores['direction'] = 0.0
    elif warnings:
        field_scores['direction'] = 0.7
    else:
        field_scores['direction'] = 1.0

    # Effect size
    valid, errors, warnings = validate_effect_size(finding.get('effect_size'),
                                                   finding.get('effect_size_type'),
                                                   finding.get('direction'),
                                                   finding.get('claim_type'))
    if not valid:
        field_scores['effect_size'] = 0.0
    elif warnings:
        field_scores['effect_size'] = 0.7
    else:
        field_scores['effect_size'] = 1.0

    # P-value
    valid, errors, warnings = validate_p_value(finding.get('p_value'),
                                              finding.get('direction'),
                                              finding.get('claim_type'),
                                              finding.get('test_statistic'))
    if not valid:
        field_scores['p_value'] = 0.0
    elif warnings:
        field_scores['p_value'] = 0.7
    else:
        field_scores['p_value'] = 1.0

    # ... similarly for other fields ...

    return field_scores
```

---

## Part 3: Finding-Level and Article-Level Quality Scores

**Finding-level score**: Weighted mean of field scores.

```python
def compute_finding_quality_score(finding: dict) -> float:
    """
    Weighted average of field scores.
    Critical fields (antecedent, consequent, direction) = weight 3
    Empirical fields (effect_size, p_value, sample_size) = weight 2
    Supporting fields (measure_type, confidence_interval, test_stat) = weight 1
    """
    field_scores = compute_field_scores(finding)

    critical_fields = ['antecedent', 'consequent', 'direction']
    empirical_fields = ['effect_size', 'p_value', 'sample_size']
    supporting_fields = ['measure_type', 'confidence_interval', 'test_statistic']

    total_weight = 0
    weighted_sum = 0

    for field, score in field_scores.items():
        if field in critical_fields:
            weight = 3
        elif field in empirical_fields:
            weight = 2
        elif field in supporting_fields:
            weight = 1
        else:
            weight = 1

        weighted_sum += score * weight
        total_weight += weight

    return weighted_sum / total_weight if total_weight > 0 else 0.5
```

**Article-level score**: Median of finding-level scores (robust to outliers).

```python
def compute_article_quality_score(article: dict) -> float:
    """
    Median finding quality score for the article.
    """
    findings = article.get('findings', [])
    if not findings:
        return 0.5  # Unknown if no findings

    finding_scores = [compute_finding_quality_score(f) for f in findings]
    return statistics.median(finding_scores)
```

---

## Part 4: Quality Action Logic (Detection & Flagging)

**Quality thresholds**:
- **0.9-1.0**: Accept (excellent)
- **0.75-0.89**: Accept with flag (good, minor issues)
- **0.5-0.74**: Requeue (needs re-extraction or manual fix)
- **< 0.5**: Reject (broken, requires re-extraction)

```python
def recommend_quality_action(article_score: float, findings: list[dict]) -> str:
    """
    Recommend action based on article quality score and finding patterns.
    """
    # Count findings by quality band
    finding_scores = [compute_finding_quality_score(f) for f in findings]

    excellent = sum(1 for s in finding_scores if s >= 0.9)
    good = sum(1 for s in finding_scores if 0.75 <= s < 0.9)
    needs_repair = sum(1 for s in finding_scores if 0.5 <= s < 0.75)
    broken = sum(1 for s in finding_scores if s < 0.5)

    total = len(finding_scores)
    broken_pct = broken / total if total > 0 else 0
    repair_pct = needs_repair / total if total > 0 else 0

    # Action logic
    if broken_pct > 0.3:
        return 'reject'  # > 30% broken findings
    elif broken_pct > 0.1 or repair_pct > 0.5:
        return 'requeue'  # Significant issues
    elif repair_pct > 0.2:
        return 'flag_for_manual_review'  # Some issues, but salvageable
    elif article_score < 0.75:
        return 'flag_for_manual_review'
    else:
        return 'accept'
```

---

## Part 5: Re-extraction Pipeline

When an article is flagged for re-extraction:

### 5.1 Detection Phase (Nightly QA Scan)

```python
def scan_extraction_for_issues(article_path: str) -> dict[str, bool]:
    """
    Scan a single extraction file for quality issues.
    Return dict of flags indicating what needs attention.
    """
    with open(article_path) as f:
        article = json.load(f)

    flags = {
        'has_vague_antecedents': False,
        'has_direction_inconsistencies': False,
        'has_null_critical_fields': False,
        'has_out_of_range_values': False,
        'quality_score_below_threshold': False,
    }

    findings = article.get('findings', [])
    for finding in findings:
        # Check for vague antecedent
        if 'environmental features' in finding.get('antecedent', '').lower():
            flags['has_vague_antecedents'] = True

        # Check direction consistency
        direction = finding.get('direction')
        effect_size = finding.get('effect_size')
        if direction == 'mixed' and effect_size is not None:
            flags['has_direction_inconsistencies'] = True

        # Check for critical nulls
        if not finding.get('antecedent') or not finding.get('consequent'):
            flags['has_null_critical_fields'] = True

        # Check ranges
        if effect_size is not None:
            es_type = finding.get('effect_size_type')
            if es_type == 'eta_squared' and (effect_size < 0 or effect_size > 1):
                flags['has_out_of_range_values'] = True

    # Overall quality
    article_score = compute_article_quality_score(article)
    if article_score < 0.75:
        flags['quality_score_below_threshold'] = True

    return flags
```

### 5.2 Flagging Phase

Articles with `quality_score_below_threshold=True` or other critical flags go into a **re-extraction queue**:

```
data/extraction_queue/requeue_candidates_2026-02-28.jsonl
```

Each line:
```json
{
  "doi": "10.1016/j.buildenv.2023.110985",
  "reason": "direction_inconsistencies",
  "quality_score": 0.62,
  "n_findings": 53,
  "n_problematic_findings": 5,
  "queued_at": "2026-02-28T10:30:00Z",
  "priority": "high"
}
```

### 5.3 Re-extraction Scheduling

The Overseer (nightly job) processes the queue:

```python
def schedule_reextraction(requeue_candidates: list[dict], batch_size: int = 10) -> dict:
    """
    Schedule batch re-extraction with Gemini.
    """
    scheduled = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'batches': []
    }

    for i in range(0, len(requeue_candidates), batch_size):
        batch = requeue_candidates[i:i+batch_size]
        batch_id = f"REEXT_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i//batch_size}"

        scheduled['batches'].append({
            'batch_id': batch_id,
            'dois': [c['doi'] for c in batch],
            'strategy': 'field_specific_prompts',  # New prompts targeting problematic fields
            'status': 'scheduled',
            'scheduled_at': datetime.now(timezone.utc).isoformat(),
        })

    return scheduled
```

### 5.4 Field-Specific Re-extraction Prompts

For articles flagged with specific issues, use targeted prompts:

**For vague antecedents:**
```
Prompt variant: "EXTRACTION_ANTECEDENT_CLARIFICATION"
Instruction: "The antecedent field in a prior extraction was too vague.
Re-extract the antecedent more specifically:
- Do NOT use catch-all terms like 'environmental features' or 'various conditions'
- Be specific: name the exact architectural or environmental feature
- Example: Instead of 'Environmental quality', specify 'Daylight availability
  (measured as Daylight Factor %)'
"
```

**For direction inconsistencies:**
```
Prompt variant: "EXTRACTION_DIRECTION_VALIDATION"
Instruction: "The direction field had inconsistencies with effect_size.
Direction MUST be one of:
- increase (effect_size > 0)
- decrease (effect_size < 0)
- no_effect (p >= 0.05, or effect_size ≈ 0)
- mixed (cannot pair with numeric effect_size)
Do not use synonyms like 'enhance', 'facilitate', 'modulate', 'affect'.
"
```

### 5.5 Verification Phase

After re-extraction, compare new vs. old quality scores:

```python
def verify_reextraction_improvement(old_article: dict, new_article: dict) -> dict:
    """
    Assess whether re-extraction improved quality.
    """
    old_score = compute_article_quality_score(old_article)
    new_score = compute_article_quality_score(new_article)

    improvement = new_score - old_score

    return {
        'doi': old_article.get('doi'),
        'old_score': round(old_score, 3),
        'new_score': round(new_score, 3),
        'improvement': round(improvement, 3),
        'improved': improvement > 0.05,  # Threshold for meaningful improvement
        'old_findings_count': len(old_article.get('findings', [])),
        'new_findings_count': len(new_article.get('findings', [])),
        'verified_at': datetime.now(timezone.utc).isoformat(),
    }
```

---

## Part 6: Quality Metrics Dashboard

Track these metrics nightly:

```python
def compute_quality_metrics(articles: list[dict]) -> dict:
    """
    Compute system-level quality metrics.
    """
    scores = [compute_article_quality_score(a) for a in articles]

    all_findings = []
    for article in articles:
        all_findings.extend(article.get('findings', []))

    field_issues = defaultdict(int)
    for finding in all_findings:
        field_scores = compute_field_scores(finding)
        for field, score in field_scores.items():
            if score < 0.75:
                field_issues[field] += 1

    return {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'total_articles': len(articles),
        'total_findings': len(all_findings),
        'article_quality': {
            'mean': round(statistics.mean(scores), 3),
            'median': round(statistics.median(scores), 3),
            'stdev': round(statistics.stdev(scores), 3),
            'min': round(min(scores), 3),
            'max': round(max(scores), 3),
        },
        'distribution': {
            'excellent_90_100': sum(1 for s in scores if s >= 0.9),
            'good_75_89': sum(1 for s in scores if 0.75 <= s < 0.9),
            'fair_50_74': sum(1 for s in scores if 0.5 <= s < 0.75),
            'poor_0_49': sum(1 for s in scores if s < 0.5),
        },
        'field_issues': dict(field_issues),  # Count of issues per field
        'action_recommendations': {
            'accept': sum(1 for s in scores if s >= 0.75),
            'flag_for_review': sum(1 for s in scores if 0.5 <= s < 0.75),
            'requeue': sum(1 for s in scores if s < 0.5),
        }
    }
```

Output to `data/quality_metrics/metrics_2026-02-28.json` daily.

---

## Part 7: Integration with Overseer

### New Overseer Stage: QA_QUALITY_GATE (Nightly)

Add this to the Overseer's scheduled stages:

```yaml
stages:
  - name: "QA_QUALITY_GATE"
    schedule: "0 2 * * *"  # 2 AM UTC daily
    description: "Scan extraction quality, flag articles for re-extraction"
    tasks:
      - scan_all_extractions_for_issues
      - generate_requeue_candidates
      - compute_quality_metrics
      - generate_dashboard_report
      - log_to_quality_ledger
```

### New Invariants

Add to `config/overseer_invariants.json`:

```json
{
  "quality_gate_invariants": {
    "max_articles_broken_per_batch": 0.1,
    "min_article_quality_score": 0.7,
    "max_direction_non_canonical_rate": 0.05,
    "max_effect_size_direction_mismatch_rate": 0.05,
    "max_vague_antecedent_rate": 0.1
  }
}
```

If invariants are violated, Overseer logs alert and may pause pipeline.

---

## Part 8: Machine-Readable Validation Rules

See companion file: `contracts/schemas/extraction_quality_rules.json`

This JSON defines all validation rules in a format that can be loaded by a Python QA service:

```json
{
  "version": "1.0",
  "fields": {
    "antecedent": {
      "criticality": "critical",
      "rules": [
        {
          "rule_id": "A1_NULL_ANTECEDENT",
          "description": "Antecedent must not be null or empty",
          "check": "not_null_or_empty"
        },
        {
          "rule_id": "A2_VAGUE_ANTECEDENT",
          "description": "Antecedent must not contain vague terms",
          "check": "regex_pattern_not_match",
          "patterns": ["environmental features", "various conditions", ...]
        }
      ]
    },
    "direction": {
      "criticality": "critical",
      "rules": [
        {
          "rule_id": "D1_INVALID_DIRECTION",
          "description": "Direction must be one of: increase, decrease, no_effect, mixed",
          "check": "enum_value",
          "allowed_values": ["increase", "decrease", "no_effect", "mixed", null]
        },
        {
          "rule_id": "D3_DIRECTION_EFFECT_MISMATCH",
          "description": "Direction must be consistent with effect_size sign",
          "check": "consistency_check",
          "dependent_fields": ["effect_size"]
        }
      ]
    }
  }
}
```

---

## Part 9: Decision Log for Panel Review

### Key Decisions Made in This Framework

#### D1: Quality Score Weighting (Critical Fields = 3x)

**Context**: Articles contain 30-100 findings each. Which fields matter most for overall quality?

**Alternatives**:
- Equal weighting (all fields = 1): Doesn't capture that antecedent/consequent/direction are foundational
- Empirical-only weighting (statistics only matter): Would accept articles with good antecedents but broken statistics

**Rationale**: Antecedent, consequent, direction are the **semantic core** of a finding. Missing or vague these makes the entire finding non-interpretable, regardless of perfect statistics. Empirical fields (effect_size, p_value) are essential for empirical claims but may be null for narrative claims. Supporting fields (measure_type, CI) are evidence quality modifiers but not deal-breakers.

**Risk**: Medium. If weighted heavily toward semantics, we might accept findings with broken statistics. Mitigate by always requiring p_value + effect_size for "empirical_finding" claims.

**Panelist Concerns**: Haack (coherence: antecedent/consequent coherence as fundamental), Pollock (empirical rigor: effect_size/p_value consistency).

---

#### D2: Direction Field Normalization (4 Canonical Values)

**Context**: Audit found 169 unique values in direction field (increase, enhance, facilitate, modulate, cause, etc.). This is extraction noise.

**Alternatives**:
- Accept all synonyms, normalize in post-processing: Defers problem, harder to catch
- Restrict Gemini prompt to 4 canonical values: Risks losing nuance (e.g., some effects are truly "mixed")

**Rationale**: The 4 canonical values (increase/decrease/no_effect/mixed) are **logically exhaustive** for effect direction. Synonyms like "enhance", "facilitate", "modulate" are *linguistic variation*, not semantic difference. Normalizing in the extraction prompt (not post-processing) catches the issue early.

**Risk**: Low. Gemini can easily be instructed to use only 4 values. We lose no semantic information.

**Panelist Concerns**: Russell (clarity/logical form), Spohn (ranking: direction as ranking over possible worlds).

---

#### D3: Mixed Direction + Effect Size = Error (Not Warning)

**Context**: Found 31 cases where direction="mixed" AND effect_size is numeric (e.g., d=0.45).

**Alternatives**:
- Flag as warning: Allows both, interpretation is ambiguous
- Flag as error, reject finding: Harsh, might reject salvageable data

**Rationale**: "Mixed" means the effect varies by condition/population (increases for some, decreases for others). Reporting a *single* numeric effect_size contradicts this. Either:
- Report separately per condition (creates separate findings)
- Use "mixed" with null effect_size (meaning: unclear direction, needs investigation)
- Report one primary direction with caveats (use direction="increase", mechanism="moderately by population")

**Risk**: Low. This is a data quality check, not a filtering rule. We can still re-extract or manually disambiguate.

**Panelist Concerns**: Pollock (clarity in statistical reporting).

---

#### D4: Vague Antecedent Detection via Regex Patterns

**Context**: Pattern matching is brittle (false positives/negatives). Should we use NLP instead?

**Alternatives**:
- Rule-based regex patterns (current): Fast, transparent, failures are debuggable
- Embedding similarity (cosine distance to "vague_antecedent" examples): Requires training, less transparent

**Rationale**: Vagueness for this task is **definitional**, not distributional. "Environmental features" is vague because it's *semantically generic*, not because it's different from a corpus. Regex captures this. Regex also makes false positives/negatives explicitly visible (easy to debug).

**Risk**: Medium. Regex will miss creative ways to be vague (e.g., "aspects of the space"). Recommend periodic manual audits to update patterns.

**Panelist Concerns**: Haack (clarity: what counts as sufficiently specific?), Kirsh (operationalization: can we define "vague" formally?).

---

## Part 10: Open Questions for Panel

| Q# | Question | Context | Panel Input Needed |
|---|---------|---------|-------------------|
| Q1 | Should antecedent specificity be measured against outcome vocabulary or independently? | Some antecedents (e.g., "blue vs. red color") are simple but specific. Others ("environmental quality") are complex but vague. | Clarity: Is specificity relative to the outcome, or absolute? |
| Q2 | For mixed-direction findings, should we create separate findings per condition or flag for re-extraction? | Current proposal: flag for manual review. Alternative: auto-split into multiple findings if conditions are listed. | Decision: Are auto-split findings preferable, or too lossy? |
| Q3 | What is the tolerance for effect_size/direction consistency given rounding/approximation in reporting? | Current tolerance: 0.01. But some papers round ES to 2 decimals, losing information. | Decision: Should tolerance vary by ES type? |
| Q4 | Should null p_value be allowed for causal claims if direction and effect_size are clearly reported? | Theoretical argument: if ES and direction are unambiguous, p_value is redundant. But APA mandates it. | Decision: APA compliance vs. pragmatism? |
| Q5 | How should we handle claims that span multiple outcome domains (e.g., "exposure to nature improves both stress and cognitive performance")? | Current model: one finding per claim. Alternative: decompose into multiple findings. | Decision: Atomicity level of findings? |

---

## References

- American Psychological Association (2020). *Publication Manual of the American Psychological Association* (7th ed.).
- Cumming, G. (2014). *The New Statistics: Why and How*. Psychological Science, 25(1), 7–29.
- Haack, S. (1993). *Evidence and Inquiry*. Blackwell.
- Pollock, J. L. (1995). *Cognitive Carpentry*. MIT Press.
- Spohn, W. (2012). *The Laws of Belief*. Oxford University Press.

---

**Next Actions**:
1. Implement validation rules in Python (QA module)
2. Create `contracts/schemas/extraction_quality_rules.json`
3. Schedule nightly quality scans
4. Begin re-extraction of flagged articles
5. Convene panel review session (recommend: 90 min, focused on Q1-Q5 above)

