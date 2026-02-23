# Quality-Weighted Entrenchment Specification

**Date**: February 4, 2026
**Version**: V1.0
**Status**: DRAFT - Pending Panel Review
**Sprint**: Post-Sprint 9 Enhancement

## 1. Overview

This specification extends the `paper_quality` system in `web_persistence.py` to include:
- **Extended citation scale** (>2K, >3K, >5K, >10K thresholds)
- **Institutional quality** (university/department tier)
- **Author quality** (individual h-index, citation counts, career stage)

These factors contribute to **entrenchment**—how resistant a belief is to revision in the Quinean web. Highly-cited papers from prestigious institutions with established authors should be more entrenched than obscure papers from unknown sources.

## 2. Current State (What We Have)

From `src/services/web_persistence.py`:

```sql
CREATE TABLE IF NOT EXISTS paper_quality (
    paper_id TEXT PRIMARY KEY,
    sample_size_score REAL,      -- normalized 0-1
    methodology_score REAL,       -- from extraction
    journal_impact_factor REAL,   -- if available
    citation_count INTEGER,       -- current citations
    preregistered BOOLEAN,
    replication_status TEXT,      -- 'original', 'replicated', 'failed_replication'
    overall_quality REAL,         -- composite score
    created_at TEXT,
    updated_at TEXT
);
```

Currently `overall_quality` is computed from methodology, preregistration, and replication only. Citation count is stored but not incorporated into the composite.

## 3. Extended Citation Scale

### 3.1 Citation Tiers

Replace the simple citation_count integer with a tiered bonus system:

| Tier | Citation Count | Entrenchment Bonus | Interpretation |
|------|----------------|-------------------|----------------|
| 0 | 0-9 | 0.00 | Uncited or new |
| 1 | 10-99 | +0.05 | Some impact |
| 2 | 100-499 | +0.10 | Moderate impact |
| 3 | 500-999 | +0.15 | High impact |
| 4 | 1,000-1,999 | +0.20 | Field-shaping |
| 5 | 2,000-2,999 | +0.25 | Major influence |
| 6 | 3,000-4,999 | +0.30 | Landmark paper |
| 7 | 5,000-9,999 | +0.35 | Classic |
| 8 | 10,000+ | +0.40 | Foundational text |

### 3.2 Implementation

```python
def citation_entrenchment_bonus(citation_count: int) -> float:
    """
    Convert citation count to entrenchment bonus.

    Rationale: More-cited papers have survived more scrutiny and
    been found useful by more researchers. They should be harder
    to dislodge from the web of belief.
    """
    thresholds = [
        (10000, 0.40),  # Foundational
        (5000, 0.35),   # Classic
        (3000, 0.30),   # Landmark
        (2000, 0.25),   # Major influence
        (1000, 0.20),   # Field-shaping
        (500, 0.15),    # High impact
        (100, 0.10),    # Moderate
        (10, 0.05),     # Some impact
    ]

    for threshold, bonus in thresholds:
        if citation_count >= threshold:
            return bonus
    return 0.0
```

### 3.3 Data Source

Citation counts can be obtained from:
- **Semantic Scholar API** (free, comprehensive)
- **OpenAlex API** (free, open data)
- **Crossref** (DOI-based lookup)
- **Zotero** (stores citation count in `extra` field if imported from Google Scholar)

## 4. Institutional Quality

### 4.1 University Tier

Environmental psychology, architecture, and cognitive science programs vary enormously in quality. We propose a 5-tier system:

| Tier | Description | Examples | Quality Multiplier |
|------|-------------|----------|-------------------|
| 1 | Elite research university | MIT, Stanford, Berkeley, Cambridge, ETH Zurich | 1.2 |
| 2 | Top research university | Michigan, Wisconsin, Toronto, TU Delft, Sydney | 1.1 |
| 3 | Strong research university | Arizona State, Eindhoven, Sheffield, UNSW | 1.0 |
| 4 | Regional university | Most state universities, regional institutions | 0.9 |
| 5 | Unknown/unranked | No ranking data available | 0.8 |

### 4.2 Department-Specific Ranking

For CNFA-relevant fields, we maintain a **domain-specific ranking** rather than using overall university rank.

**TIER SELECTION RULE**: Use the **more favorable** of overall university tier or domain-specific tier. A UCSD cognitive science paper uses Tier 1 (domain), not Tier 2 (overall). A cognitive science paper from a Tier 1 overall university with no CogSci program uses overall tier.

```python
def effective_institution_tier(
    overall_tier: int,
    domain_tier: Optional[int],
    paper_domain: str
) -> int:
    """
    Return the more favorable (lower number = better) tier.
    Domain tier only applies if paper matches that domain.
    """
    if domain_tier is not None:
        return min(overall_tier, domain_tier)
    return overall_tier
```

### 4.2.1 CNFA-Relevant Tier 1 Departments (Seed List)

**Cognitive Science** (embodied cognition, situated action, distributed cognition):
| Institution | Notes |
|-------------|-------|
| UCSD | Founding department (1986); Norman, Hutchins, Kirsh, Nunez |
| CMU | Simon, Anderson, Newell legacy; strong AI/cog modeling |
| Indiana University | Dynamical systems, language evolution |
| Edinburgh | Informatics + philosophy of mind |
| MIT (BCS) | Computational cognitive science |
| Stanford (SymSys) | Interdisciplinary symbolic systems |
| UC Berkeley | Lakoff, embodied metaphor |

**Environmental Psychology** (person-environment relations, restorative environments):
| Institution | Notes |
|-------------|-------|
| Eindhoven (TU/e) | Built environment, lighting research |
| Cornell | Environmental behavior, Kaplan students |
| Surrey | Environmental psychology programme |
| Chalmers | Architecture + environmental psychology |
| CUNY Graduate Center | Environmental psychology PhD program |
| University of Michigan | Rachel & Stephen Kaplan (ART founders) |
| Texas A&M | Environment-behavior research |

**Architecture/Design Research** (evidence-based design, spatial cognition):
| Institution | Notes |
|-------------|-------|
| MIT | Design computation, space syntax |
| TU Delft | Architecture + environmental research |
| ETH Zurich | Design informatics |
| AA London | Architectural Association; experimental |
| UCL Bartlett | Space syntax originators (Hillier) |
| Georgia Tech | Design computing |
| Harvard GSD | Design research methods |

**Neuroscience/Neuroarchitecture** (neural basis of spatial experience):
| Institution | Notes |
|-------------|-------|
| Harvard | Visual neuroscience |
| UCL | O'Keefe (place cells), navigation |
| MIT | Systems neuroscience |
| Stanford | Human neuroscience |
| Salk Institute | Vision, spatial cognition |
| Max Planck Institutes | Multiple relevant programs |
| Princeton (PNI) | Cognitive neuroscience |

**Landscape Architecture / Urban Design**:
| Institution | Notes |
|-------------|-------|
| Harvard GSD | Landscape urbanism |
| Penn (Weitzman) | Ian McHarg legacy, ecological design |
| Berkeley (CED) | Environmental design |
| Cornell (AAP) | Landscape + planning |
| Edinburgh (ESALA) | Landscape architecture research |

### 4.3 Schema Extension

```sql
CREATE TABLE IF NOT EXISTS institution_quality (
    institution_id TEXT PRIMARY KEY,      -- normalized name
    institution_name TEXT NOT NULL,       -- display name
    country TEXT,
    overall_tier INTEGER DEFAULT 3,       -- 1-5
    env_psych_rank INTEGER,               -- domain-specific (null if not ranked)
    architecture_rank INTEGER,
    cognitive_science_rank INTEGER,
    neuroscience_rank INTEGER,
    ranking_source TEXT,                  -- 'QS', 'THE', 'ARWU', 'manual'
    ranking_year INTEGER,
    created_at TEXT,
    updated_at TEXT
);
```

### 4.4 Author-Institution Link

```sql
CREATE TABLE IF NOT EXISTS author_institution (
    author_id TEXT,
    institution_id TEXT,
    affiliation_type TEXT,    -- 'primary', 'adjunct', 'visiting', 'former'
    start_year INTEGER,
    end_year INTEGER,         -- null if current
    PRIMARY KEY (author_id, institution_id, start_year)
);
```

## 5. Author Quality

### 5.1 Author Metrics

Individual authors contribute to paper quality through their track record:

| Metric | Source | Weight |
|--------|--------|--------|
| h-index | Semantic Scholar, Google Scholar | 0.35 |
| Total citations | Semantic Scholar | 0.25 |
| Publication count | Semantic Scholar | 0.15 |
| Career stage | Computed from first publication | 0.15 |
| Field-specific impact | Domain citation analysis | 0.10 |

### 5.2 Author h-index Tiers

| h-index | Tier | Interpretation | Quality Bonus |
|---------|------|----------------|---------------|
| 0-5 | Early career | Graduate student, new faculty | 0.0 |
| 6-15 | Establishing | Assistant professor level | +0.05 |
| 16-30 | Established | Associate professor level | +0.10 |
| 31-50 | Influential | Full professor, recognized expert | +0.15 |
| 51-80 | Leader | Field leader, major contributor | +0.20 |
| 81+ | Luminary | Citation giant (Kahneman, Pinker level) | +0.25 |

### 5.3 Career Stage Adjustment

Age/career stage moderates interpretation of other metrics:

```python
def career_stage_factor(first_pub_year: int, current_year: int = 2026) -> float:
    """
    Career stage affects how we interpret citation counts.

    A paper with 500 citations from 1984 is less remarkable than
    a paper with 500 citations from 2019.

    Returns a multiplier for citation impact.
    """
    years_active = current_year - first_pub_year

    if years_active <= 5:
        return 1.5   # Citations are impressive for someone new
    elif years_active <= 15:
        return 1.2   # Still relatively early
    elif years_active <= 30:
        return 1.0   # Normal
    else:
        return 0.9   # Expected to have high citations
```

### 5.4 Author Schema

```sql
CREATE TABLE IF NOT EXISTS author_quality (
    author_id TEXT PRIMARY KEY,          -- ORCID if available, else normalized name
    display_name TEXT NOT NULL,
    orcid TEXT,                           -- ORCID identifier
    h_index INTEGER,
    total_citations INTEGER,
    publication_count INTEGER,
    first_publication_year INTEGER,

    -- Field-specific metrics (CNFA-relevant)
    env_psych_publications INTEGER,
    architecture_publications INTEGER,
    cognitive_science_publications INTEGER,

    -- Computed scores
    overall_quality_score REAL,           -- composite 0-1
    career_stage TEXT,                    -- 'early', 'establishing', 'established', 'senior', 'emeritus'

    -- Data provenance
    data_source TEXT,                     -- 'semantic_scholar', 'manual', 'zotero'
    last_updated TEXT,
    created_at TEXT
);
```

### 5.5 Paper-Author Link

```sql
CREATE TABLE IF NOT EXISTS paper_authors (
    paper_id TEXT,
    author_id TEXT,
    author_position INTEGER,              -- 1 = first author, -1 = last author (senior)
    is_corresponding BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (paper_id, author_id)
);
```

## 6. Composite Quality Score

### 6.1 Computing Overall Quality

```python
def compute_overall_quality(
    methodology_score: float,          # 0-1 from extraction
    citation_count: int,
    institution_tier: int,             # 1-5
    lead_author_h_index: int,
    senior_author_h_index: int,
    preregistered: bool,
    replication_status: str,
    sample_size_normalized: float      # 0-1
) -> float:
    """
    Compute composite quality score for a paper.

    Weights reflect relative importance for epistemic confidence.
    """
    weights = {
        'methodology': 0.25,
        'citations': 0.20,
        'institution': 0.15,
        'author_quality': 0.20,
        'preregistration': 0.10,
        'sample_size': 0.10
    }

    # Normalize components to 0-1 scale
    scores = {
        'methodology': methodology_score,
        'citations': citation_quality_normalized(citation_count),  # 0-1
        'institution': (5 - institution_tier) / 4,  # Tier 1 → 1.0, Tier 5 → 0.0
        'author_quality': author_quality_normalized(
            lead_author_h_index, senior_author_h_index
        ),
        'preregistration': 1.0 if preregistered else 0.5,
        'sample_size': sample_size_normalized
    }

    # Replication adjustment (multiplicative)
    replication_multiplier = {
        'replicated': 1.2,
        'original': 1.0,
        'failed_replication': 0.5,
        'contested': 0.7
    }.get(replication_status, 1.0)

    # Weighted sum
    composite = sum(
        weights[k] * scores[k] for k in weights
    )

    # Apply replication multiplier, cap at 1.0
    return min(1.0, composite * replication_multiplier)
```

### 6.2 Quality → Entrenchment Mapping

```python
def quality_to_entrenchment(overall_quality: float) -> float:
    """
    Map overall quality score to entrenchment value.

    Base entrenchment is 0.3 (from CLAUDE.md).
    Quality adjusts this within [0.1, 0.7] range.

    Theoretical/core beliefs can have higher entrenchment (up to 0.95)
    independent of paper quality.
    """
    # Linear mapping: quality 0.0 → 0.1, quality 1.0 → 0.7
    base = 0.1
    range_size = 0.6

    return base + (overall_quality * range_size)
```

## 7. Data Acquisition Strategy

### 7.1 Automatic Sources

| Source | What It Provides | API Cost | Reliability |
|--------|------------------|----------|-------------|
| **Semantic Scholar** | Citations, h-index, author IDs | Free | High |
| **OpenAlex** | Citations, institutions, concepts | Free | High |
| **Crossref** | DOI metadata, references | Free | High |
| **ORCID** | Author disambiguation | Free | Medium |

### 7.2 Zotero Integration

Zotero can provide initial metadata. The `extra` field often contains:
```
Citation Count: 1234
PMCID: PMC12345
ORCID: 0000-0001-2345-6789
```

Parse this during import to seed the quality tables.

### 7.3 Manual Override

For CNFA-core papers, allow manual quality override:

```sql
CREATE TABLE IF NOT EXISTS quality_overrides (
    paper_id TEXT PRIMARY KEY,
    override_reason TEXT NOT NULL,
    override_quality REAL,            -- null to use computed
    override_entrenchment REAL,       -- null to use computed
    overridden_by TEXT,               -- 'david', 'panel'
    created_at TEXT
);
```

## 8. Impact on Web of Belief

### 8.1 How Quality Affects Entrenchment

In `extraction_to_web.py`, entrenchment is currently set to:
- 0.3 for normal claims
- 0.1 for stubs
- +0.15 bonus for mechanistic claims

With quality weighting, this becomes:

```python
def compute_belief_entrenchment(
    claim_type: str,
    is_stub: bool,
    paper_quality: float,       # 0-1 composite
    citation_bonus: float       # from citation_entrenchment_bonus()
) -> float:
    """
    Compute entrenchment for a belief from a specific paper.
    """
    # Base entrenchment by claim type
    if is_stub:
        base = 0.1
    elif claim_type == "theoretical":
        base = 0.5
    elif claim_type == "mechanistic":
        base = 0.45  # (0.3 base + 0.15 mechanistic bonus)
    else:
        base = 0.3

    # Quality adjustment (±0.2 from base)
    quality_adjustment = (paper_quality - 0.5) * 0.4

    # Citation bonus (additive, 0 to 0.4)
    adjusted = base + quality_adjustment + citation_bonus

    # Clamp to valid range
    return max(0.05, min(0.95, adjusted))
```

### 8.2 Inverse-Variance Weighting

In `web_persistence.py`, credence merging already uses paper quality:

```python
def _merge_credences(self, c1, c2, paper_quality=None):
    # Lower quality = higher effective uncertainty
    if paper_quality is not None and paper_quality > 0:
        quality_adjustment = 1.0 / paper_quality
        u2 = u2 * quality_adjustment
```

This means low-quality papers contribute less to merged credence, which is the correct behavior.

### 8.3 Conflict Resolution

When beliefs conflict, quality affects whose credence "wins" in merge:

- High-quality contradicting evidence → serious tension
- Low-quality contradicting evidence → minor concern
- Very low-quality evidence → consider discounting entirely

## 9. Panel Consultation Needed

The following decisions require expert panel review:

| ID | Decision | Alternatives | Risk |
|----|----------|--------------|------|
| Q1 | Citation thresholds (10K, 5K, 3K, etc.) | Different breakpoints | Low |
| Q2 | Institution tier assignments | Use ranking services vs manual | Medium |
| Q3 | h-index tier boundaries | Different cutoffs | Low |
| Q4 | Weighting of quality components | Different distributions | Medium |
| Q5 | Career stage adjustment | Ignore age entirely | Low |
| Q6 | Quality → entrenchment mapping | Non-linear mapping | Medium |

## 10. Implementation Priority

1. **Phase 1**: Extended citation scale (schema + computation)
2. **Phase 2**: Author quality table with h-index
3. **Phase 3**: Institution tier lookup
4. **Phase 4**: Semantic Scholar API integration
5. **Phase 5**: Composite quality computation
6. **Phase 6**: Update extraction_to_web.py to use new quality

## 11. Testing Strategy

```python
def test_citation_entrenchment_bonus():
    assert citation_entrenchment_bonus(5) == 0.0
    assert citation_entrenchment_bonus(50) == 0.05
    assert citation_entrenchment_bonus(500) == 0.15
    assert citation_entrenchment_bonus(1500) == 0.20
    assert citation_entrenchment_bonus(2500) == 0.25
    assert citation_entrenchment_bonus(4000) == 0.30
    assert citation_entrenchment_bonus(7000) == 0.35
    assert citation_entrenchment_bonus(15000) == 0.40

def test_quality_ranking():
    """Papers with same methodology but different citations should rank differently."""
    q1 = compute_overall_quality(methodology=0.8, citations=100, ...)
    q2 = compute_overall_quality(methodology=0.8, citations=5000, ...)
    assert q2 > q1

def test_institution_matters():
    """MIT paper should have higher quality than unknown institution."""
    q_mit = compute_overall_quality(..., institution_tier=1, ...)
    q_unknown = compute_overall_quality(..., institution_tier=5, ...)
    assert q_mit > q_unknown
```

## 12. References

- Bornmann, L., & Daniel, H. D. (2008). What do citation counts measure? A review of studies on citing behavior. *Journal of Documentation*, 64(1), 45-80. https://doi.org/10.1108/00220410810844150

- Hirsch, J. E. (2005). An index to quantify an individual's scientific research output. *PNAS*, 102(46), 16569-16572. https://doi.org/10.1073/pnas.0507655102

- Quine, W. V., & Ullian, J. S. (1978). *The Web of Belief* (2nd ed.). McGraw-Hill.

---

*This specification extends the quality system established in Sprint 5 (web_persistence.py) to incorporate citation impact, institutional prestige, and author reputation as factors in belief entrenchment.*
