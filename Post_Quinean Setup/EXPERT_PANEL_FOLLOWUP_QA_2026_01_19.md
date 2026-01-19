# Expert Panel Follow-up: Recommendations on Open Questions

**Date**: Sunday, January 19, 2026
**Context**: Panel raised three questions in their plan review. We now ask for their recommendations.

---

## Question 1: How should we handle papers that span multiple theories?

*Example: A paper that tests both ART predictions (attention restoration) and SRT predictions (stress reduction) in the same study.*

---

### Dr. Pearl

**Recommendation: Create separate beliefs, linked by shared-evidence constraint.**

```python
class ConstraintType(Enum):
    # ... existing ...
    SHARED_EVIDENCE = "shared_evidence"  # Same study supports both beliefs
```

When a single paper supports multiple theories:
1. Extract separate beliefs for each theory
2. Link them with `SHARED_EVIDENCE` constraint
3. This constraint should NOT increase credence propagation (it's not independent replication)

**Rationale**: A single study finding that nature reduces both attention fatigue AND stress is one piece of evidence, not two. If you let it boost both beliefs independently, you're double-counting.

**Implementation**:
```python
@dataclass
class Belief:
    # ... existing ...
    evidence_cluster_id: Optional[str] = None  # Groups beliefs from same study

# When merging:
def _merge_credences(self, c1, c2):
    # Check if from same evidence cluster
    if c1.evidence_cluster_id == c2.evidence_cluster_id:
        # Don't treat as independent - no credence boost
        return c1  # or weighted by recency
```

---

### Dr. Cartwright

**Recommendation: Treat as opportunity for bridge detection.**

A paper testing multiple theories is explicitly probing cross-theory relationships. Your system should:

1. Extract beliefs for each theory
2. **Automatically generate bridge candidates** between the theories tested
3. Mark these bridges as `empirically_tested` (higher confidence than analogical)

**Example**:
```yaml
# From a paper testing ART + SRT together
bridge:
  source_theory: "ART"
  target_theory: "SRT"
  bridge_type: "empirical_covariance"  # New type
  confidence: 0.6  # Higher than analogical (0.35)
  evidence: "paper_xyz found both effects in same sample"
```

**New bridge type needed**:
```python
class BridgeType(Enum):
    # ... existing ...
    EMPIRICAL_COVARIANCE = "empirical_covariance"  # Co-occurrence in same study
```

---

### Dr. Simon

**Recommendation: Flag for special handling in LOO validation.**

Multi-theory papers are problematic for leave-one-out because removing them affects multiple theories simultaneously.

**Protocol**:
1. Tag papers as `single_theory` or `multi_theory`
2. In LOO validation:
   - Run standard LOO on `single_theory` papers
   - Run separate analysis on `multi_theory` papers
   - Report both metrics

**Metric addition**:
```python
@dataclass
class LOOReport:
    # ... existing ...
    single_theory_mae: float
    multi_theory_mae: float
    theory_coupling_detected: List[Tuple[str, str]]  # Theories that co-occur
```

If `multi_theory_mae` is much worse than `single_theory_mae`, the system struggles with integrative papers—worth knowing.

---

### Dr. Bates

**Recommendation: Use multi-theory papers to validate ontology mappings.**

These papers are gold for testing whether your environment and outcome taxonomies work:

1. The paper explicitly links constructs across theories
2. Your taxonomies should map both to canonical IDs
3. If the paper says "spaciousness reduces both attention fatigue and stress," your system should:
   - Map to `spatial.openness`
   - Map to both `psych.attention.fatigue` and `psych.stress`
   - Recognize these as related outcomes (not independent)

**Test case**: If a multi-theory paper uses different terminology for the same construct across its ART and SRT sections, can the system recognize it?

---

### Dr. Kaplan

**Recommendation: These are the most valuable papers—prioritize them.**

In CNFA, the most important papers are those that test boundary conditions across theories. They tell us:
- Where theories agree (convergent validity)
- Where theories make different predictions (discriminant opportunities)
- Which theory better explains the data (competitive testing)

**For Gold Standard corpus**: Include at least 2 multi-theory papers:

| Paper | Theories Tested | Expected Output |
|-------|-----------------|-----------------|
| Hartig et al. (2003) | ART + SRT | Should extract beliefs for both; should generate `EMPIRICAL_COVARIANCE` bridge |
| Berto (2005) | ART + Preference | Should distinguish attention restoration from aesthetic preference |

---

### Consensus on Question 1

**Implementation requirements**:

1. Add `evidence_cluster_id` to Belief (prevents double-counting)
2. Add `SHARED_EVIDENCE` constraint type
3. Add `EMPIRICAL_COVARIANCE` bridge type (confidence 0.55-0.65)
4. Tag papers as `single_theory` / `multi_theory`
5. Report separate LOO metrics for each category
6. Include 2+ multi-theory papers in Gold Standard

---

## Question 2: What's the minimum paper count for meaningful LOO validation?

*Panel suggested N≥30. Is this correct? How should we handle smaller corpora?*

---

### Dr. Simon

**Recommendation: N≥30 for statistical validity, but stratified.**

The N≥30 suggestion comes from central limit theorem considerations. But raw count isn't sufficient—you need coverage:

**Minimum viable corpus**:
- N ≥ 30 papers total
- ≥ 5 papers per major theory (ART, SRT, Biophilia, Prospect-Refuge)
- ≥ 3 papers per environment domain (spatial, natural, sensory, configurational)
- ≥ 2 null/weak result papers
- ≥ 2 methodologically weak papers

**If corpus is smaller**:
- N = 15-29: Report LOO metrics but mark as "preliminary—low statistical power"
- N < 15: Do not run LOO; use only direct annotation comparison

**Stratified LOO**:
```python
def stratified_loo(papers: List[Paper]) -> StratifiedLOOReport:
    """Run LOO within each stratum to avoid systematic bias."""
    reports = {}
    for theory in get_theories(papers):
        theory_papers = [p for p in papers if p.primary_theory == theory]
        if len(theory_papers) >= 5:
            reports[theory] = run_loo(theory_papers)
    return StratifiedLOOReport(reports)
```

---

### Dr. Pearl

**Recommendation: Focus on graph connectivity, not paper count.**

30 papers producing 30 isolated beliefs is useless. 15 papers producing a connected web is valuable.

**Connectivity requirement**:
- Mean constraint degree ≥ 2 (each belief connected to ≥2 others on average)
- Largest connected component ≥ 70% of beliefs
- No theory should be entirely isolated

**Metric**:
```python
def corpus_sufficient_for_loo(web: WebOfBelief) -> Tuple[bool, str]:
    avg_degree = sum(len(get_constraints(b)) for b in web.beliefs) / len(web.beliefs)
    lcc_size = len(largest_connected_component(web)) / len(web.beliefs)

    if avg_degree < 2:
        return False, f"Insufficient connectivity (degree={avg_degree:.1f})"
    if lcc_size < 0.7:
        return False, f"Fragmented web (LCC={lcc_size:.0%})"
    return True, "Sufficient for LOO"
```

---

### Dr. Cartwright

**Recommendation: Distinguish validation goals.**

Different questions require different N:

| Question | Minimum N | Rationale |
|----------|-----------|-----------|
| "Does extraction work?" | 10 | Annotation comparison only |
| "Is credence calibrated?" | 20 | Need variance in expected credences |
| "Does LOO predict?" | 30 | Statistical power for prediction |
| "Are cross-theory bridges valid?" | 40+ | Need multiple papers per theory pair |

**Phased validation**:
- Phase 1 (N=10): Gold Standard annotation comparison
- Phase 2 (N=20): Credence calibration
- Phase 3 (N=30+): LOO validation
- Phase 4 (N=50+): Bridge validation

Don't wait for N=30 to start validation. Run what you can with what you have.

---

### Consensus on Question 2

**Requirements**:

1. **Minimum for LOO**: N≥30 papers with connectivity check
2. **Stratification**: ≥5 papers per theory, ≥3 per environment domain
3. **Phased approach**: Start validation at N=10, add tests as corpus grows
4. **Connectivity gate**: Don't run LOO if mean degree < 2 or LCC < 70%
5. **Report confidence**: Mark results as "preliminary" if N < 30

---

## Question 3: Will you version the Gold Standard corpus?

*Should the test corpus evolve over time? How do we handle changes?*

---

### Dr. Bates

**Recommendation: Yes, version strictly. Freeze for comparison.**

The Gold Standard corpus IS your measurement instrument. Changing it without versioning is like recalibrating a scale mid-experiment.

**Versioning protocol**:
```
gold_standard/
├── v1.0/
│   ├── manifest.yaml       # List of papers + annotators
│   ├── annotations/
│   │   ├── kaplan_1989.yaml
│   │   └── ...
│   └── baseline_results.json  # System performance on this version
├── v1.1/
│   ├── manifest.yaml
│   ├── CHANGELOG.md        # What changed from v1.0
│   └── ...
└── current -> v1.1/        # Symlink to active version
```

**Rules**:
1. Never modify a released version (v1.0 is immutable)
2. All changes create new version (v1.1, v1.2, ...)
3. Always report which version was used for validation
4. Keep baseline_results for each version to track progress

---

### Dr. Simon

**Recommendation: Distinguish corpus expansion from annotation revision.**

Two types of changes:

**Type A: Adding papers** (expansion)
- Add new papers to increase coverage
- Low risk—previous validation still valid
- Version as minor increment (v1.0 → v1.1)

**Type B: Changing annotations** (revision)
- Revise expected credences, constraints, etc.
- Higher risk—may invalidate previous comparisons
- Version as major increment (v1.x → v2.0)
- Document WHY annotations changed

**Annotation revision triggers**:
- Expert disagreement resolved
- New evidence about paper quality
- Construct definitions updated
- Errors discovered

---

### Dr. Kaplan

**Recommendation: Plan for living corpus with frozen snapshots.**

The CNFA field evolves. New papers become seminal. Old findings get revised. Your Gold Standard should evolve too—but carefully.

**Annual review cycle**:
1. Each year, review Gold Standard for:
   - Papers that should be added (new influential work)
   - Papers that should be removed (retracted, superseded)
   - Annotations that need revision (field consensus changed)
2. Release new major version annually (v1.0, v2.0, v3.0)
3. Maintain ability to test against any historical version

**Migration testing**:
When releasing new version, run system against both old and new:
- If performance drops on new version, investigate why
- May reveal system was overfitting to old corpus

---

### Dr. Pearl

**Recommendation: Track annotation provenance.**

Every annotation should record:
- Who made it (which expert, or consensus)
- When (date)
- Confidence (how sure is the annotator?)
- Basis (what evidence supports this annotation?)

```yaml
# In annotation file
beliefs:
  - id: "art_nature_restoration"
    content: "Natural environments facilitate attention restoration"
    expected_credence: [0.5, 0.7]
    annotation_metadata:
      annotator: "panel_consensus"
      date: "2026-01-19"
      confidence: "high"
      basis: "Core ART claim, well-cited, moderate empirical support"
```

This allows future reviewers to understand WHY annotations were made, not just WHAT they are.

---

### Consensus on Question 3

**Requirements**:

1. **Strict versioning**: Immutable releases (v1.0, v1.1, v2.0)
2. **Version semantics**: Minor = paper additions; Major = annotation changes
3. **Provenance tracking**: Every annotation records who, when, confidence, basis
4. **Frozen baselines**: Each version stores system performance at release
5. **Annual review**: Planned major version updates, not ad-hoc changes
6. **Migration testing**: Compare performance across versions when updating

---

## Summary: All Three Questions Answered

| Question | Key Recommendation | Implementation Impact |
|----------|-------------------|----------------------|
| Multi-theory papers | Separate beliefs + evidence clustering + bridge generation | New constraint type, bridge type, LOO stratification |
| Minimum N for LOO | N≥30 with connectivity check; phased validation starting at N=10 | Validation phases, connectivity gate |
| Corpus versioning | Strict versioning, provenance tracking, annual review | Directory structure, annotation schema, migration tests |

---

*Panel follow-up complete. Ready for incorporation into revised plan.*
