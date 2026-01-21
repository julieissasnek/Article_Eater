# Implementation Plan: Expert Panel HIGH Priority Changes

**Date**: January 21, 2026
**Source**: Expert Panel Review Phase C-D (2026-01-21)
**Scope**: 5 HIGH priority items
**Estimated Effort**: Sprint E1 (2-3 days)

---

## Overview

The expert panel identified 5 HIGH priority changes that should be implemented before the next release. This plan provides detailed specifications for each change.

| Item | Decision | Change | Complexity |
|------|----------|--------|------------|
| H1 | D3 | Three-tier causal classification | High |
| H2 | D7 | Outcome categories from taxonomy | Medium |
| H3 | D9 | Confounder coverage gap | Medium |
| H4 | D11 | Clickable follow-up queries | Low |
| H5 | D12 | Contested evidence section | Low |

---

## H1: Three-Tier Causal Classification

**Panel Lead**: Pearl
**Rationale**: Current keyword detection conflates correlation with causation, potentially misleading users about evidence strength.

### Current State
```python
# src/services/query_response.py:310-318
causal_keywords = [
    'cause', 'effect', 'affect', 'impact', 'influence',
    'improve', 'reduce', 'increase', 'decrease', 'lead to',
    'result in', 'because', 'due to'
]
# Returns boolean: is_causal = True/False
```

### Target State
```python
class CausalStrength(Enum):
    """Three-tier causal classification per Pearl."""
    CAUSAL = "causal"           # Explicit causal language + experimental design
    SUGGESTIVE = "suggestive"   # Directional language, observational design
    ASSOCIATIONAL = "associational"  # Correlation only, no causal implication
    UNKNOWN = "unknown"         # Insufficient information to classify
```

### Implementation Steps

#### Step 1: Create CausalClassifier service
**File**: `src/services/causal_classifier.py` (NEW)

```python
"""
Causal Claim Classifier
=======================

Three-tier classification of causal claims per Pearl's framework.

Tiers:
- CAUSAL: Explicit causal language + experimental/interventional design
- SUGGESTIVE: Directional language, observational design
- ASSOCIATIONAL: Correlation only

Date: January 2026
Sprint E1 - Panel Response H1
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, List, Tuple

class CausalStrength(Enum):
    CAUSAL = "causal"
    SUGGESTIVE = "suggestive"
    ASSOCIATIONAL = "associational"
    UNKNOWN = "unknown"

@dataclass
class CausalClassification:
    strength: CausalStrength
    confidence: float  # 0-1 confidence in classification
    evidence: List[str]  # Keywords/phrases that led to classification
    requires_verification: bool  # True if abstract-only
    study_design: Optional[str]  # RCT, quasi-experimental, observational, etc.

# Keyword tiers
CAUSAL_KEYWORDS = ['causes', 'caused by', 'causal effect', 'intervention']
SUGGESTIVE_KEYWORDS = ['affects', 'improves', 'reduces', 'increases', 'decreases',
                       'leads to', 'results in', 'impacts']
ASSOCIATIONAL_KEYWORDS = ['associated with', 'correlated with', 'linked to',
                          'predicts', 'related to']
HEDGING_KEYWORDS = ['may', 'might', 'could', 'potentially', 'suggests']

class CausalClassifier:
    def classify(self, content: str, study_design: Optional[str] = None,
                 source_depth: str = "abstract") -> CausalClassification:
        """Classify causal strength of a belief."""
        # Implementation details...
```

#### Step 2: Update Belief model
**File**: `src/services/web_of_belief.py`

Add field:
```python
@dataclass
class Belief:
    # ... existing fields ...
    causal_strength: Optional[CausalStrength] = None
    study_design: Optional[str] = None  # RCT, quasi-experimental, observational, survey
```

#### Step 3: Update query_response.py
**File**: `src/services/query_response.py`

Replace `_is_causal_claim()` with classifier integration:
```python
def _classify_causal_strength(self, belief: Belief) -> CausalClassification:
    """Classify causal strength using three-tier system."""
    classifier = CausalClassifier()
    return classifier.classify(
        content=belief.content,
        study_design=belief.study_design,
        source_depth=belief.source_depth.value if belief.source_depth else "unknown"
    )
```

#### Step 4: Update EvidenceItem
**File**: `src/services/query_response.py`

```python
@dataclass
class EvidenceItem:
    # ... existing fields ...
    # Replace:
    # is_causal: bool
    # With:
    causal_strength: str  # causal, suggestive, associational, unknown
    study_design: Optional[str]
```

#### Step 5: Update ingestion warnings
**File**: `app/routes/ingestion.py`

Add tier-specific warnings:
```python
if classification.strength == CausalStrength.CAUSAL and source_depth == "abstract":
    warnings.append("CAUSAL claim from abstract requires full-text verification of study design.")
elif classification.strength == CausalStrength.SUGGESTIVE:
    warnings.append("SUGGESTIVE: Directional language detected. Verify if causal inference is warranted.")
```

#### Step 6: Tests
**File**: `tests/test_causal_classifier.py` (NEW)

Test cases:
- Explicit causal language → CAUSAL
- "Improves" with RCT design → CAUSAL
- "Improves" with observational design → SUGGESTIVE
- "Associated with" → ASSOCIATIONAL
- Hedged language ("may affect") → SUGGESTIVE (downgraded)
- Abstract-only CAUSAL → requires_verification=True

**Expected**: 25+ tests

---

## H2: Outcome Categories from Taxonomy

**Panel Lead**: Bates/Kaplan
**Rationale**: Hardcoded outcomes create synchronization bugs and miss domain-relevant categories.

### Current State
```python
# src/services/reporting.py:311-314
expected_outcomes = {
    'productivity', 'cognition', 'stress', 'wellbeing',
    'health', 'creativity', 'attention', 'mood'
}
```

### Target State
- Derive from `src/services/outcome_taxonomy.py` (Sprint 4)
- Add missing categories: sleep, social, wayfinding, restoration

### Implementation Steps

#### Step 1: Extend outcome_taxonomy.py
**File**: `src/services/outcome_taxonomy.py`

Add missing outcomes per Kaplan:
```python
# Add to CNFA_OUTCOMES or equivalent structure
DOMAIN_OUTCOMES = {
    # Existing
    'productivity': {...},
    'cognition': {...},
    'stress': {...},
    'wellbeing': {...},
    'health': {...},
    'creativity': {...},
    'attention': {...},
    'mood': {...},
    # NEW per Kaplan
    'sleep': {
        'description': 'Sleep quality and circadian rhythm',
        'indicators': ['sleep duration', 'sleep quality', 'circadian alignment'],
        'related_constructs': ['melatonin', 'alertness', 'fatigue']
    },
    'social': {
        'description': 'Social behavior and interaction',
        'indicators': ['collaboration', 'communication', 'social presence'],
        'related_constructs': ['team cohesion', 'spontaneous interaction']
    },
    'wayfinding': {
        'description': 'Spatial navigation and orientation',
        'indicators': ['navigation time', 'orientation accuracy', 'cognitive mapping'],
        'related_constructs': ['legibility', 'spatial cognition']
    },
    'restoration': {
        'description': 'Restorative experience and recovery',
        'indicators': ['attention restoration', 'stress recovery', 'mental fatigue reduction'],
        'related_constructs': ['ART', 'nature contact', 'prospect-refuge']
    }
}

def get_expected_outcomes() -> Set[str]:
    """Return set of expected outcome categories for gap analysis."""
    return set(DOMAIN_OUTCOMES.keys())
```

#### Step 2: Update reporting.py
**File**: `src/services/reporting.py`

Replace hardcoded set:
```python
# OLD
expected_outcomes = {
    'productivity', 'cognition', 'stress', 'wellbeing',
    'health', 'creativity', 'attention', 'mood'
}

# NEW
from src.services.outcome_taxonomy import get_expected_outcomes
expected_outcomes = get_expected_outcomes()
```

#### Step 3: Update ingestion.py
**File**: `app/routes/ingestion.py`

Replace hardcoded OUTCOME_CATEGORIES:
```python
# OLD
OUTCOME_CATEGORIES = {
    'productivity': 'Worker productivity...',
    # ...hardcoded
}

# NEW
from src.services.outcome_taxonomy import DOMAIN_OUTCOMES
OUTCOME_CATEGORIES = {k: v['description'] for k, v in DOMAIN_OUTCOMES.items()}
```

#### Step 4: Tests
**File**: `tests/test_outcome_taxonomy.py`

Add tests:
- `get_expected_outcomes()` returns all 12 categories
- New outcomes have required fields (description, indicators)
- Gap analysis uses taxonomy outcomes

**Expected**: 8+ new tests

---

## H3: Confounder Coverage Gap

**Panel Lead**: Pearl
**Rationale**: For causal claims, we should flag when known confounders haven't been addressed.

### Current State
Gap analysis has 5 categories but no confounder tracking.

### Target State
Add 6th gap category: "Confounder Coverage" for causal claims.

### Implementation Steps

#### Step 1: Define domain confounders
**File**: `src/services/outcome_taxonomy.py`

Add confounder mappings:
```python
# Known confounders for neuroarchitecture causal claims
DOMAIN_CONFOUNDERS = {
    'light_productivity': ['temperature', 'noise', 'time_of_day', 'task_type', 'individual_differences'],
    'temperature_cognition': ['humidity', 'air_quality', 'clothing', 'acclimatization'],
    'noise_concentration': ['noise_type', 'task_complexity', 'habituation', 'control'],
    'plants_stress': ['maintenance_burden', 'allergies', 'visual_access', 'other_nature'],
    # ... domain-specific confounder sets
}

def get_confounders_for_claim(subject: str, object: str) -> List[str]:
    """Return known confounders for a causal claim."""
    key = f"{subject}_{object}".lower().replace(' ', '_')
    return DOMAIN_CONFOUNDERS.get(key, [])
```

#### Step 2: Update gap analysis
**File**: `src/services/reporting.py`

Add confounder gap detection in `_generate_gap_analysis()`:
```python
# 6. Confounder coverage (for causal claims) - NEW
causal_beliefs = [b for b in beliefs if self._is_causal_claim(b)]
if causal_beliefs:
    unaddressed_confounders = self._check_confounder_coverage(causal_beliefs)
    if unaddressed_confounders:
        gaps.append(ReportSection(
            title="Unaddressed Confounders",
            content="Causal claims may be confounded by:\n" +
                    "\n".join(f"• {c}" for c in unaddressed_confounders[:10]),
            data={'confounders': unaddressed_confounders}
        ))

def _check_confounder_coverage(self, causal_beliefs: List[Belief]) -> List[str]:
    """Check which known confounders are not addressed in evidence."""
    from src.services.outcome_taxonomy import get_confounders_for_claim

    all_confounders = set()
    addressed = set()

    for belief in causal_beliefs:
        # Get expected confounders for this claim
        confounders = get_confounders_for_claim(
            belief.subject if hasattr(belief, 'subject') else '',
            belief.outcome_id or ''
        )
        all_confounders.update(confounders)

        # Check if belief content mentions any confounders
        content_lower = belief.content.lower()
        for conf in confounders:
            if conf.replace('_', ' ') in content_lower:
                addressed.add(conf)

    return list(all_confounders - addressed)
```

#### Step 3: Tests
**File**: `tests/test_reporting.py`

Add tests:
- Causal claim without confounder mention → gap flagged
- Causal claim with confounder controlled → no gap
- Non-causal claims don't trigger confounder check

**Expected**: 6+ new tests

---

## H4: Clickable Follow-up Queries

**Panel Lead**: Bates
**Rationale**: Follow-ups should be executable, not just displayed text.

### Current State
```python
@dataclass
class FollowUp:
    question: str
    type: str  # deeper, broader, uncertainty
    rationale: str
```

### Target State
```python
@dataclass
class FollowUp:
    question: str
    type: str
    rationale: str
    # NEW
    query_url: str  # URL-encoded query for direct execution
    query_params: Dict[str, Any]  # Parameters to pre-fill search
```

### Implementation Steps

#### Step 1: Update FollowUp model
**File**: `src/services/query_response.py`

```python
@dataclass
class FollowUp:
    question: str
    type: str
    rationale: str
    query_url: Optional[str] = None  # e.g., "/api/query/search?query=..."
    query_params: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'question': self.question,
            'type': self.type,
            'rationale': self.rationale,
            'query_url': self.query_url,
            'query_params': self.query_params
        }
```

#### Step 2: Update follow-up generation
**File**: `src/services/query_response.py`

```python
def _generate_follow_ups(self, intent: QueryIntent, relevant: List[Belief]) -> List[FollowUp]:
    """Generate exactly 3 follow-up questions with executable queries."""
    import urllib.parse

    follow_ups = []
    subject = intent.subject or "this topic"
    obj = intent.object or "outcomes"

    # 1. DEEPER
    deeper_q = f"What are the mechanisms by which {subject} affects {obj}?"
    deeper = FollowUp(
        question=deeper_q,
        type="deeper",
        rationale="Understand the underlying causal pathway",
        query_url=f"/api/query/search?query={urllib.parse.quote(deeper_q)}",
        query_params={'query': deeper_q, 'include_expansions': True}
    )
    follow_ups.append(deeper)

    # ... similar for broader and uncertainty
```

#### Step 3: Update frontend
**File**: `frontend/evidence-explorer.html`

Add click handler for follow-ups:
```javascript
function renderFollowUps(followUps) {
    return followUps.map(f => `
        <div class="followup-item" onclick="executeFollowUp('${encodeURIComponent(f.query_url)}')">
            <span class="followup-type">${f.type}</span>
            <span class="followup-question">${f.question}</span>
            <span class="followup-rationale">${f.rationale}</span>
        </div>
    `).join('');
}

async function executeFollowUp(queryUrl) {
    // Execute the follow-up query
    const response = await fetch(decodeURIComponent(queryUrl), {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({})  // params already in URL or use query_params
    });
    const result = await response.json();
    displaySearchResults(result);
}
```

#### Step 4: Tests
**File**: `tests/test_query_response.py`

Add tests:
- Follow-ups include query_url
- query_url is properly URL-encoded
- query_params match the question

**Expected**: 4+ new tests

---

## H5: Contested Evidence Section

**Panel Lead**: Cartwright
**Rationale**: Contested beliefs should be visible regardless of relevance score.

### Current State
Evidence sorted by relevance → credence, contested items may be hidden.

### Target State
Two sections in response:
1. "Top Evidence" (sorted by relevance)
2. "Contested Evidence" (all contested, regardless of relevance)

### Implementation Steps

#### Step 1: Update QueryResponse model
**File**: `src/services/query_response.py`

```python
@dataclass
class QueryResponse:
    # ... existing fields ...
    evidence_items: List[EvidenceItem] = field(default_factory=list)
    # NEW
    contested_items: List[EvidenceItem] = field(default_factory=list)
```

#### Step 2: Update response building
**File**: `src/services/query_response.py`

In `_build_response()`:
```python
# Build main evidence items (top N by relevance)
evidence_items = []
for belief in relevant[:max_evidence]:
    if not belief.contested:  # Exclude contested from main list
        evidence_items.append(self._create_evidence_item(belief))

# Build contested items (ALL contested, regardless of relevance)
contested_items = []
for belief in relevant:
    if belief.contested:
        contested_items.append(self._create_evidence_item(belief))

# Also search beyond top N for contested beliefs
for belief in self.web.beliefs.values():
    if belief.contested and belief not in relevant:
        # Check if minimally relevant
        if self._is_minimally_relevant(belief, intent):
            contested_items.append(self._create_evidence_item(belief))
```

#### Step 3: Update API response
**File**: `app/routes/query.py`

Add contested_items to FullQueryResponse:
```python
class FullQueryResponse(BaseModel):
    # ... existing fields ...
    evidence_items: List[EvidenceItemResponse]
    contested_items: List[EvidenceItemResponse] = Field(default_factory=list)  # NEW
```

#### Step 4: Update frontend
**File**: `frontend/evidence-explorer.html`

Display contested section:
```javascript
function displaySearchResults(response) {
    // Main evidence
    let html = '<h3>Top Evidence</h3>';
    html += renderEvidenceItems(response.evidence_items);

    // Contested section (NEW)
    if (response.contested_items && response.contested_items.length > 0) {
        html += '<h3 class="contested-header">⚠️ Contested Evidence</h3>';
        html += '<p class="contested-note">These findings have conflicting evidence:</p>';
        html += renderEvidenceItems(response.contested_items, {highlight: 'contested'});
    }

    document.getElementById('results').innerHTML = html;
}
```

#### Step 5: Tests
**File**: `tests/test_query_response.py`

Add tests:
- Contested beliefs appear in contested_items
- Contested beliefs excluded from main evidence_items
- Contested beliefs found even if low relevance
- Empty contested_items when no contested beliefs

**Expected**: 6+ new tests

---

## Implementation Order

```
Day 1:
├── H4: Clickable follow-ups (Low complexity, quick win)
├── H5: Contested evidence section (Low complexity)
└── H2: Outcome categories (Medium, foundational)

Day 2:
├── H3: Confounder coverage gap (Medium, depends on H2)
└── H1: Causal classification - Part 1 (classifier service)

Day 3:
├── H1: Causal classification - Part 2 (integration)
└── Testing and integration
```

## Test Summary

| Item | New Tests | Modified Tests |
|------|-----------|----------------|
| H1 | 25+ | 10+ |
| H2 | 8+ | 4+ |
| H3 | 6+ | 2+ |
| H4 | 4+ | 2+ |
| H5 | 6+ | 3+ |
| **Total** | **49+** | **21+** |

## Success Criteria

1. All existing 181 tests continue to pass
2. 49+ new tests added and passing
3. Causal classification correctly identifies tier for test cases
4. Gap analysis shows confounder gaps for causal claims
5. Follow-ups are clickable in frontend
6. Contested evidence visible regardless of relevance
7. Outcome categories derived from single source (taxonomy)

---

## Rollback Plan

Each change is isolated:
- H1: Feature flag `USE_CAUSAL_TIERS` (default: True)
- H2: Fallback to hardcoded if taxonomy import fails
- H3: Skip confounder check if confounders not defined
- H4: Graceful degradation (show question without URL)
- H5: Merge contested into main list if flag disabled

---

*Plan created January 21, 2026*
*Ready for Sprint E1 implementation*
