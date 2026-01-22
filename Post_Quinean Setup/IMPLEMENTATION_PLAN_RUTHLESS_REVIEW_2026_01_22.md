# Implementation Plan: Ruthless Review Findings

**Date**: January 22, 2026
**Source**: Expanded Expert Panel Review (10 experts)
**Status**: Planning

---

## Analysis of Panel Findings

### What the Panel Validated
1. **Core epistemology is sound** - Pearl approved the design-first causal classification
2. **Directional opposition is correct** - Not credence threshold
3. **Three tiers is right** - Simon confirmed this is good satisficing
4. **Conceptual integrity exists** - Brooks found no over-engineering
5. **Module boundaries are clean** - Liskov approved abstraction

### What Needs Work
1. **Domain vocabulary is incomplete** - Kaplan identified significant gaps
2. **Documentation lacks theory** - Naur found tacit knowledge not captured
3. **Invariants not documented** - Lamport concerned about formal rigor
4. **Bridge types incomplete** - Cartwright wants capacity bridges
5. **Keyword lists duplicated** - Parnas found maintenance burden

---

## Sprint Plan

### Sprint F1: Domain Vocabulary Expansion
**Owner**: Kaplan items
**Priority**: HIGH
**Estimated Scope**: 4-6 hours

#### F1.1: Expand Neuroarchitecture Causal Patterns
**File**: `src/services/causal_classifier.py`

Add to `NEUROARCH_CAUSAL_PATTERNS`:
```python
# Building certification/design
r'\bgreen\s+building\b',
r'\bWELL\s+certif',
r'\bLEED\b',
r'\bbiophilic\s+design\b',

# Lighting interventions
r'\bdaylighting\b',
r'\bglare\s+control\b',
r'\blighting\s+design\b',

# Environmental quality
r'\bthermal\s+comfort\b',
r'\bacoustic\s+comfort\b',
r'\bindoor\s+air\s+quality\b',
r'\bIAQ\b',
```

Add to `NEUROARCH_SUGGESTIVE_PATTERNS`:
```python
r'\bview\s+quality\b',
r'\bvisual\s+access\b',
r'\bnatural\s+ventilation\b',
r'\bdaylight\s+factor\b',
```

#### F1.2: Add Theoretical Framework Patterns
**File**: `src/services/causal_classifier.py`

New pattern group `THEORETICAL_FRAMEWORK_PATTERNS`:
```python
# Attention Restoration Theory (ART)
ATTENTION_RESTORATION_PATTERNS = [
    r'\bbeing\s+away\b',
    r'\bfascination\b',
    r'\bextent\b',  # ART component
    r'\bcompatibility\b',  # ART component
    r'\battention\s+restoration\s+theory\b',
    r'\bART\b',  # When in context of restoration
    r'\bKaplan\b',  # Rachel & Stephen Kaplan
]

# Prospect-Refuge Theory
PROSPECT_REFUGE_PATTERNS = [
    r'\bprospect\b',
    r'\brefuge\b',
    r'\bmystery\b',  # landscape preference
    r'\bcomplexity\b',  # landscape preference
    r'\bAppleton\b',  # Jay Appleton
]

# Stress Recovery Theory (SRT)
STRESS_RECOVERY_PATTERNS = [
    r'\bstress\s+recovery\s+theory\b',
    r'\bUlrich\b',  # Roger Ulrich
    r'\baffective\s+response\b',
    r'\bpsychophysiological\s+stress\b',
]
```

#### F1.3: Expand Fallback Outcomes
**File**: `src/services/reporting.py`

Update `_FALLBACK_OUTCOME_CATEGORIES`:
```python
_FALLBACK_OUTCOME_CATEGORIES = {
    # Existing
    'behav.productivity', 'cog.performance', 'affect.stress',
    'health.wellbeing', 'health', 'cog.attention', 'affect.mood',
    'physio.stress',
    # New per Kaplan
    'cog.creativity',       # Creative thinking
    'behav.collaboration',  # Teamwork, communication
    'physio.circadian',     # Circadian rhythm measures
    'affect.satisfaction',  # Job/space satisfaction
    'cog.focus',           # Concentration, focus
    'physio.cortisol',     # Stress hormone
    'behav.absenteeism',   # Attendance patterns
}
```

#### F1.4: Add Domain Confounders
**File**: `src/services/reporting.py`

Expand `_get_confounder_keywords()` with domain-specific:
```python
# Kaplan domain confounders
r'\boccupant\s+density\b',
r'\bcrowding\b',
r'\bcontrol\b',  # personal control
r'\bautonomy\b',
r'\bwork\s+type\b',
r'\bknowledge\s+work\b',
r'\bhabituation\b',
r'\bprior\s+exposure\b',
r'\badaptation\b',
```

---

### Sprint F2: Bridge & Measurement Enhancements
**Owner**: Cartwright items
**Priority**: HIGH
**Estimated Scope**: 3-4 hours

#### F2.1: Add Capacity Bridge Type
**File**: `src/services/bridge_warrants.py`

Add new bridge type:
```python
class BridgeType(Enum):
    MECHANISM = "mechanism"
    FUNCTIONAL = "functional"
    ANALOGICAL = "analogical"
    CONSTITUTIVE = "constitutive"
    CAPACITY = "capacity"  # NEW: Entity has stable capacity

# Update default P(bridge) values
DEFAULT_BRIDGE_PRIORS = {
    BridgeType.CONSTITUTIVE: 0.75,  # Reduced from 0.85 per Cartwright
    BridgeType.MECHANISM: 0.60,
    BridgeType.CAPACITY: 0.55,      # NEW
    BridgeType.FUNCTIONAL: 0.50,
    BridgeType.ANALOGICAL: 0.35,
}
```

Add capacity detection patterns:
```python
CAPACITY_PATTERNS = [
    r'\bhas\s+the\s+capacity\b',
    r'\bcapable\s+of\b',
    r'\bable\s+to\b',
    r'\btends\s+to\b',
    r'\bpropensity\s+to\b',
    r'\bdisposition\b',
]
```

#### F2.2: Expand Measurement Categories
**File**: `src/services/query_response.py`

Add to `_identify_disagreement_reasons()`:
```python
# Behavioral vs self-report
behavioral_keywords = ['task performance', 'observed behavior', 'actual', 'measured']
# Already have self_report_keywords

# Objective vs subjective
objective_keywords = ['lux', 'decibels', 'PPM', 'measured', 'sensor', 'meter']
subjective_keywords = ['perceived', 'rated', 'reported', 'felt', 'experienced']
```

#### F2.3: Add Implicit Confounder Patterns
**File**: `src/services/reporting.py`

Per Pearl - add patterns for implicit control:
```python
# Implicit confounder control (Pearl)
r'\badjusted\s+model\b',
r'\bModel\s+[2-9]\b',
r'\bafter\s+including\s+covariates\b',
r'\bfull\s+model\b',
r'\bmultivariate\b',
r'\bmultiple\s+regression\b',
```

---

### Sprint F3: Documentation & Governance
**Owner**: Naur, Lamport, Parnas items
**Priority**: HIGH
**Estimated Scope**: 4-5 hours

#### F3.1: Create Theory of the System Document
**File**: `docs/DESIGN_RATIONALE.md`

Contents:
1. **Quinean Commitment**: Why coherentist not foundationalist
2. **Three-Tier Decision**: Why not four tiers (Simon rationale)
3. **Directional Opposition**: Why not credence threshold (Pearl rationale)
4. **Pattern Selection**: Why these specific patterns
5. **Bridge Warrant Theory**: Cartwright's evidence portability
6. **Satisficing Principles**: Simon's bounded rationality throughout

#### F3.2: Document Invariants
**File**: `docs/INVARIANTS.md`

Contents:
```markdown
# System Invariants

## Belief Invariants
1. belief_id is unique across the web
2. credence.value ∈ [0.0, 1.0]
3. credence.uncertainty ∈ [0.0, 1.0]
4. source_depth ∈ {FULL_TEXT, ABSTRACT, METADATA}
5. level ∈ {EMPIRICAL, THEORETICAL, META, METHODOLOGICAL}

## Web Invariants
1. No circular dependencies in belief_dependencies
2. All paper_ids reference valid papers (when papers tracked)
3. contested flag implies either:
   - Explicit marking, OR
   - Directional opposition exists

## Consistency Model
- Queries operate on snapshot of web state
- Mutations are atomic at belief level
- No read-write locking currently implemented
- Recommended: copy-on-read for query operations
```

#### F3.3: Consolidate Keyword Lists
**Action**: Create `src/services/domain_vocabulary.py`

Single source of truth for:
- Causal language keywords
- Confounder keywords
- Measurement type keywords
- Domain-specific terms

All other files import from this module.

#### F3.4: Create Architecture Diagram
**File**: `docs/ARCHITECTURE_DIAGRAM.md`

ASCII diagram + description of:
- Data flow from PDF → Claims → Beliefs → Query Response
- Service dependencies
- API layer structure

---

### Sprint F4: Frontend & UX Enhancements
**Owner**: Bates items
**Priority**: MEDIUM
**Estimated Scope**: 3-4 hours

#### F4.1: Vocabulary Expansion Display
**File**: `frontend/evidence-explorer.html`

Add prominent section showing:
- Original query terms
- Expanded terms used
- Which expansions matched results

#### F4.2: Faceted Filtering
**File**: `frontend/evidence-explorer.html`

Add filter controls for:
- Source depth (Full-text / Abstract / Metadata)
- Causal tier (Causal / Suggestive / Associational)
- Credence range (slider)
- Contested status (Yes / No / All)

---

## Implementation Order

```
Week 1:
├── Sprint F1: Domain Vocabulary (HIGH)
│   ├── F1.1: Neuroarchitecture patterns
│   ├── F1.2: Theoretical frameworks
│   ├── F1.3: Fallback outcomes
│   └── F1.4: Domain confounders
│
├── Sprint F2: Bridge & Measurement (HIGH)
│   ├── F2.1: Capacity bridge type
│   ├── F2.2: Measurement categories
│   └── F2.3: Implicit confounder patterns

Week 2:
├── Sprint F3: Documentation (HIGH)
│   ├── F3.1: DESIGN_RATIONALE.md
│   ├── F3.2: INVARIANTS.md
│   ├── F3.3: Consolidate keywords
│   └── F3.4: Architecture diagram
│
└── Sprint F4: Frontend (MEDIUM)
    ├── F4.1: Vocabulary display
    └── F4.2: Faceted filtering
```

---

## Test Plan

### Sprint F1 Tests
- Test new neuroarchitecture patterns match expected strings
- Test theoretical framework detection
- Test expanded fallback outcomes appear in gap reports
- Test domain confounders are detected

### Sprint F2 Tests
- Test capacity bridge type creation and P(bridge) calculation
- Test new measurement categories in disagreement detection
- Test implicit confounder patterns reduce severity

### Sprint F3 Tests
- Documentation review (no code tests)
- Verify keyword imports work after consolidation

### Sprint F4 Tests
- Manual UI testing
- Verify filters produce correct results

---

## Success Criteria

1. **All HIGH items addressed** (6 items)
2. **Test count increases** (target: 260+ tests)
3. **Panel would re-approve** at higher confidence
4. **Documentation enables theory preservation** (Naur criterion)
5. **Invariants are documented and checkable** (Lamport criterion)

---

## Risks

| Risk | Mitigation |
|------|------------|
| Pattern expansion causes false positives | Add negative tests for each pattern |
| Keyword consolidation breaks imports | Run full test suite after refactor |
| Capacity bridge P(bridge) is miscalibrated | Start conservative (0.55), adjust based on review |
| Documentation becomes stale | Add doc update to PR checklist |

---

## Decision Points for Panel Review

After implementation, re-convene panel to review:
1. Are the new patterns appropriate? (Kaplan)
2. Is capacity bridge correctly specified? (Cartwright)
3. Does DESIGN_RATIONALE.md capture the theory? (Naur)
4. Are invariants sufficiently formal? (Lamport)
