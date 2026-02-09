# Panel Consultation: Sprint 3.0 Implementation Decisions (Consolidated)
**Date**: 2026-02-09
**Panel IDs**: P-S3-A, P-S3-B, P-S3-C, P-S3-D, P-S3-E
**Scope**: 27 decisions across 10 modules

---

## Panel P-S3-A: LLM Integration (llm_query_bridge.py)

### Decisions Under Review

| ID | Decision | Current Value | Risk |
|----|----------|---------------|------|
| D5 | 4-tier model hierarchy | NONE/FAST/CAPABLE/BEST | HIGH |
| D6 | Model-to-phase routing | Implicit | HIGH |
| D7 | Hardcoded LLM costs | Per-1k rates | MED |
| D8 | Temperature | 0.0 | LOW |
| D9 | No LLM in retrieval | Structured only | MED |
| D10 | LLM for synthesis | Yes | HIGH |
| D11 | Cost target distribution | 80/15/5% | MED |

### Panel Responses

#### Dr. Dario Amodei (LLM Scaling, Cost-Capability)
*Constructed from Anthropic research and scaling laws papers*

The 4-tier hierarchy (NONE/FAST/CAPABLE/BEST) is reasonable but the implicit routing is problematic. You need **explicit decision rules** for tier selection, not implicit patterns.

**D5 (Hierarchy)**: APPROVE with documentation
- Make tier selection explicit: query complexity → tier mapping

**D6 (Routing)**: MODIFY
- Create explicit routing table:
  ```python
  QUERY_TO_TIER = {
      QueryType.SIMPLE_LOOKUP: ModelTier.NONE,      # Template-based
      QueryType.EVIDENCE_RETRIEVAL: ModelTier.NONE, # Structured search
      QueryType.INTERPRETATION: ModelTier.FAST,     # Haiku for initial parsing
      QueryType.SYNTHESIS: ModelTier.CAPABLE,       # Sonnet for combination
      QueryType.EXPLANATION: ModelTier.BEST,        # Opus for complex explanation
  }
  ```

**D7 (Costs)**: MODIFY
- Make costs configurable via environment variables
- Add staleness warning if costs haven't been updated in 90 days

**D11 (Cost Target)**: APPROVE
- 80/15/5 is reasonable for a research tool

#### Dr. Percy Liang (LLM Limitations, HELM Benchmarks)
*Constructed from HELM and LLM evaluation research*

**D8 (Temperature = 0.0)**: APPROVE for retrieval/parsing
- Deterministic is correct for structured outputs
- Consider temperature > 0 ONLY for exploratory synthesis

**D9 (No LLM in Retrieval)**: APPROVE
- Structured search is more reliable than LLM semantic matching
- LLMs hallucinate; structured search doesn't

**D10 (LLM for Synthesis)**: APPROVE with guard rails
- Add explicit hallucination checks:
  - All cited beliefs must exist in web
  - All quoted text must match source
  - Flag any claims not grounded in retrieved evidence

#### Dr. Herbert Simon (Bounded Rationality)
*Constructed from "Administrative Behavior", "Sciences of the Artificial"*

The tiering is a form of **satisficing**—use just enough model capability for the task. This is correct.

**Recommendation**: Add a **cost ceiling per query** to prevent runaway spending:
```python
MAX_COST_PER_QUERY = 0.50  # Never spend more than $0.50 on a single query
```

### P-S3-A Panel Resolutions

| Decision | Verdict | Action |
|----------|---------|--------|
| D5 | APPROVE | Document tier hierarchy |
| D6 | MODIFY | Create explicit routing table |
| D7 | MODIFY | Make costs configurable |
| D8 | APPROVE | Keep temperature = 0.0 |
| D9 | APPROVE | No LLM in retrieval |
| D10 | APPROVE | Add hallucination guard rails |
| D11 | APPROVE | 80/15/5 distribution |

---

## Panel P-S3-B: Search & Prioritization (voi_search.py)

*Note: D1-D4 were already addressed in P-VOI Panel*

### Additional Decision Under Review

| ID | Decision | Current Value | Risk |
|----|----------|---------------|------|
| D19 | Default gap priority | 0.5 | LOW |

### Panel Response

#### Dr. Jon Kleinberg (Network Algorithms)
*Constructed from "Networks, Crowds, and Markets"*

**D19 (Default Priority 0.5)**: MODIFY
- Default priority should be **relative to queue**, not fixed
- Use percentile ranking:
  ```python
  def compute_default_priority(gap: VOIGap, existing_gaps: List[VOIGap]) -> float:
      """Priority based on VOI percentile among existing gaps."""
      if not existing_gaps:
          return 0.5
      voi_scores = [g.predicted_voi for g in existing_gaps]
      percentile = sum(1 for v in voi_scores if v < gap.predicted_voi) / len(voi_scores)
      return percentile
  ```

### P-S3-B Panel Resolution

| Decision | Verdict | Action |
|----------|---------|--------|
| D19 | MODIFY | Use percentile-based priority |

---

## Panel P-S3-C: Evidence Synthesis (evidence_summarizer.py)

### Decisions Under Review

| ID | Decision | Current Value | Risk |
|----|----------|---------------|------|
| D12 | High heterogeneity threshold | I² > 0.5 | MED |
| D13 | Credence thresholds | 0.4/0.7 | MED |
| D14 | Pooling method | Inverse-variance | MED |
| D15 | Strength mapping | 0.75/0.5 | MED |

### Panel Responses

#### Dr. Julian Higgins (Cochrane, Meta-Analysis)
*Constructed from Cochrane Handbook for Systematic Reviews*

**D12 (Heterogeneity I² > 0.5)**: APPROVE
- I² > 50% is the standard threshold for "substantial heterogeneity"
- However, add interpretive guidance:
  ```python
  HETEROGENEITY_INTERPRETATION = {
      (0.0, 0.25): "low",
      (0.25, 0.50): "moderate",
      (0.50, 0.75): "substantial",
      (0.75, 1.0): "considerable",
  }
  ```

**D14 (Inverse-Variance)**: APPROVE with enhancement
- DerSimonian-Laird is standard for random-effects
- Add option for **Hartung-Knapp-Sidik-Jonkman** (HKSJ) for small samples:
  ```python
  pooling_method: Literal["dersimonian_laird", "hksj"] = "dersimonian_laird"
  ```

#### Dr. Nancy Cartwright (Evidence, External Validity)
*Constructed from "Evidence-Based Policy" and "Hunting Causes"*

**D13 (Credence Thresholds 0.4/0.7)**: MODIFY
- Thresholds should be **level-dependent**:
  ```python
  CREDENCE_THRESHOLDS = {
      EpistemicLevel.THEORETICAL: {"low": 0.5, "high": 0.8},  # Stricter for theory
      EpistemicLevel.INTERMEDIATE: {"low": 0.4, "high": 0.7},
      EpistemicLevel.EMPIRICAL: {"low": 0.3, "high": 0.6},    # More lenient for data
      EpistemicLevel.OBSERVATIONAL: {"low": 0.2, "high": 0.5},
  }
  ```

**D15 (Strength Mapping)**: MODIFY
- Strength should account for **uncertainty**, not just mean credence:
  ```python
  def assess_strength(credence: Credence) -> str:
      # Adjust for uncertainty using lower bound of credible interval
      effective = credence.value - credence.uncertainty * 0.5
      if effective >= 0.65:
          return "strong"
      elif effective >= 0.40:
          return "moderate"
      else:
          return "weak"
  ```

#### Dr. Deborah Mayo (Error Statistics)
*Constructed from "Statistical Inference as Severe Testing"*

**D15 (Strength Mapping)**: Additional guidance
- Strength claims should require **severe testing**, not just high credence
- Add severity qualifier:
  ```python
  @dataclass
  class EvidenceStrength:
      strength: str  # "strong", "moderate", "weak"
      severity: float  # How severely tested? (0-1)
      n_studies: int
      heterogeneity: str
  ```

### P-S3-C Panel Resolutions

| Decision | Verdict | Action |
|----------|---------|--------|
| D12 | APPROVE | Add interpretive guidance |
| D13 | MODIFY | Level-dependent thresholds |
| D14 | APPROVE | Add HKSJ option |
| D15 | MODIFY | Account for uncertainty in strength |

---

## Panel P-S3-D: Visualization & Export (network_service.py, export_formats.py)

### Decisions Under Review

| ID | Decision | Current Value | Risk |
|----|----------|---------------|------|
| D17 | Transferability thresholds | 0.7/0.4 | MED |
| D18 | Default scope confidence | 0.5 | MED |
| D21 | Min credence for visualization | 0.0 | LOW |
| D22 | Node size multiplier | 1.5x | LOW |
| D23 | Default clustering mode | Theory-based | MED |
| D24 | JSONL vs JSON | Implicit | LOW |
| D25 | Parquet fallback | Silent | MED |

### Panel Responses

#### Dr. Tamara Munzner (Visualization Design)
*Constructed from "Visualization Analysis and Design"*

**D21 (Min Credence 0.0)**: MODIFY
- Showing all beliefs regardless of credence is **visual clutter**
- Default to min_credence = 0.3 (hide very uncertain beliefs)
- Make configurable in UI

**D22 (Node Size 1.5x)**: MODIFY
- Fixed multiplier doesn't scale with belief count
- Use **logarithmic scaling** for entrenchment:
  ```python
  def node_size(entrenchment: float, base_size: float = 20) -> float:
      return base_size * (1 + math.log1p(entrenchment * 5))
  ```

**D23 (Default Clustering)**: APPROVE
- Theory-based clustering is most semantically meaningful
- Add **clustering mode selector** in UI

#### Dr. Bas van Fraassen (Contrast Classes)
*Constructed from "The Scientific Image"*

**D17 (Transferability 0.7/0.4)**: MODIFY
- Transferability is **context-dependent**, not absolute
- Require explicit specification of **target context**:
  ```python
  def assess_transferability(
      scope: ScopeConditions,
      source_context: str,
      target_context: str
  ) -> TransferabilityAssessment:
      """Assess transferability between explicit contexts."""
      ...
  ```

**D18 (Default Scope Confidence 0.5)**: MODIFY
- 0.5 is uninformative (maximally uncertain)
- Default to **lower confidence (0.3)** for inferred scopes:
  ```python
  # Explicit scopes (stated in paper): confidence = 0.7
  # Inferred scopes (from methods): confidence = 0.5
  # Default scopes (no information): confidence = 0.3
  ```

#### Data Engineering Perspective

**D24 (JSONL vs JSON)**: APPROVE current implementation
- JSONL for streaming/large files, JSON for structured
- Document the choice in function docstrings

**D25 (Parquet Fallback)**: MODIFY
- **Log warning** when falling back from Parquet:
  ```python
  logger.warning("pyarrow not available, falling back to JSON export")
  ```

### P-S3-D Panel Resolutions

| Decision | Verdict | Action |
|----------|---------|--------|
| D17 | MODIFY | Require explicit target context |
| D18 | MODIFY | Lower default (0.3 for inferred) |
| D21 | MODIFY | Default min_credence = 0.3 |
| D22 | MODIFY | Use logarithmic scaling |
| D23 | APPROVE | Add UI selector |
| D24 | APPROVE | Document choice |
| D25 | MODIFY | Add warning log |

---

## Panel P-S3-E: Discovery Funnel (discovery_funnel.py)

### Decisions Under Review

| ID | Decision | Current Value | Risk |
|----|----------|---------------|------|
| D19 | Default gap priority | 0.5 | LOW |
| D20 | Closure classification | 4 types | MED |

### Panel Responses

#### Dr. Judea Pearl (Causal Attribution)
*Constructed from "Causality" and causal inference work*

**D20 (Closure Classification)**: APPROVE with quantitative thresholds
- 4 categories (FULL, PARTIAL, NONE, NEGATIVE) need clear boundaries:
  ```python
  def classify_closure(voi_before: float, voi_after: float) -> ClosureType:
      reduction = voi_before - voi_after
      reduction_pct = reduction / voi_before if voi_before > 0 else 0

      if voi_after < 0.1:  # Gap essentially closed
          return ClosureType.FULL
      elif reduction_pct >= 0.3:  # ≥30% reduction
          return ClosureType.PARTIAL
      elif reduction_pct >= -0.1:  # Minor change either way
          return ClosureType.NONE
      else:  # VOI increased
          return ClosureType.NEGATIVE
  ```

### P-S3-E Panel Resolutions

| Decision | Verdict | Action |
|----------|---------|--------|
| D19 | MODIFY | (See P-S3-B - percentile-based) |
| D20 | APPROVE | Add quantitative thresholds |

---

## Summary: All Approved Changes

### Critical (Implement Immediately)

1. **LLM Routing Table** (D6) - Create explicit query type → tier mapping
2. **Level-Dependent Credence Thresholds** (D13) - Different standards for theoretical vs. empirical
3. **Adaptive Epsilon** - Already implemented in P-VOI

### High Priority

4. **Hallucination Guard Rails** (D10) - Verify all LLM outputs against source data
5. **Strength with Uncertainty** (D15) - Use effective credence, not raw mean
6. **Closure Type Thresholds** (D20) - Quantify FULL/PARTIAL/NONE/NEGATIVE

### Medium Priority

7. **Configurable LLM Costs** (D7) - Environment variables + staleness warning
8. **Percentile-Based Gap Priority** (D19)
9. **Lower Default Scope Confidence** (D18) - 0.3 for inferred scopes
10. **Min Credence Visualization** (D21) - Default 0.3
11. **Logarithmic Node Scaling** (D22)

### Low Priority (Documentation)

12. **Document Tier Hierarchy** (D5)
13. **Document JSON/JSONL Choice** (D24)
14. **Add Parquet Fallback Warning** (D25)
15. **Add Heterogeneity Interpretation** (D12)

---

## Implementation Priority Matrix

| Change | Risk if Skipped | Effort | Priority |
|--------|-----------------|--------|----------|
| Explicit LLM routing | HIGH | LOW | P1 |
| Level-dependent thresholds | MEDIUM | LOW | P1 |
| Hallucination guards | HIGH | MEDIUM | P1 |
| Closure quantification | MEDIUM | LOW | P2 |
| Strength with uncertainty | MEDIUM | LOW | P2 |
| Configurable costs | LOW | LOW | P3 |
| Node scaling | LOW | LOW | P3 |

---

*Panel consultation completed: 2026-02-09*
*Participating experts: Amodei, Liang, Simon, Kleinberg, Higgins, Cartwright, Mayo, Munzner, van Fraassen, Pearl*
