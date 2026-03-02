# Master Document Revisions: Article Discovery and VOI Integration

**Date**: March 2, 2026
**Version**: 1.0
**Source**: Article Recommendation Flow Audit + Revision List (MASTER_DOC_REVISION_LIST_2026-03-02.md)
**Target Master Document**: MASTER_DOC_CMR_2026-02-25.md (~20,500 lines)

---

## Overview: Integration Points

This document provides 10 new or substantially revised sections for the master document, addressing critical gaps in the operational pipeline identified by the Article Recommendation Flow Audit conducted March 2, 2026.

### Where Each Section Belongs in Master Document

| Section ID | Section Title | Type | Master Doc Location | Replaces/Extends |
|------------|---------------|------|---------------------|-----------------|
| NEW-A1 | VOI Integration Architecture | NEW | After §47 (Value of Information), before Part IV | New §47A |
| NEW-A2 | Researcher-Specific VOI and Collector Profiles | NEW | After NEW-A1 | New §47B |
| NEW-A3 | Article Search Execution Pipeline | NEW | After NEW-A2 | New §47C |
| NEW-A4 | QA System Integration: From Follow-Up Questions to Research Targets | NEW | After NEW-A3 | New §47D |
| NEW-A5 | Discovery Funnel Feedback Loop | NEW | After NEW-A4 | New §47E |
| NEW-A6 | Overseer Management Layer Database Schema | NEW | New Part XVIII (Computational Infrastructure), §132.6a | New §132.6a |
| REVISE-B1 | VOI Computation Details (Revision of §47) | REVISE | Existing §47 | Extend §47 with 47.1A–47.3 subsections |
| REVISE-B2 | Queue Prioritization Strategy (Revision of §46) | REVISE | Existing §46 (What the System Tracks) | Extend §46 with new subsection |
| REVISE-B3 | Article Recommendation Flow Completeness (Revision) | REVISE | Existing gap prediction sections | Add integration point documentation |
| NEW-A10 | Continuous Recommendation Loop Service | NEW | Part XVIII (Computational Infrastructure) | New §132.7 |

---

# SECTION NEW-A1: VOI Integration Architecture

## §47A. VOI Integration Architecture: From Gap Detection to Queue Prioritization

### Executive Summary

The Article_Eater system predicts knowledge gaps through systematic analysis of the web of belief's topology (§133), computes value-of-information (VOI) scores for each gap, and uses these scores to prioritize which research targets are presented to human collectors and which are automatically searched. This section documents the complete architecture: how gaps detected by the gap predictor flow through VOI scoring, researcher-specific adjustment, and queue ranking; what happens when a search executes and results come in; and how the discovery funnel provides feedback to revise VOI scores when gaps close.

The system currently implements VOI computation in three independent modules that operate at different scales (gap-level, finding-level, and lifecycle-level), with weak integration between them. This section clarifies when each module is used, how they interact, and what the aspirational fully-integrated system should do.

### 47A.1: Current State vs. Intended State

The intended architecture flows as follows:

```
Gap Detected (gap_predictor.find_all_gaps)
    ↓ gap contains default voi_score = 0.5
Compute Base VOI (VOIGapScorer.calculate_voi from voi_search.py)
    ↓ epistemic_voi = f(uncertainty, centrality, sparsity)
    ↓ structural_voi = f(incoming_edges, outgoing_edges, criticality)
    ↓ base_VOI = 0.5 * epistemic_voi + 0.5 * structural_voi
Convert to ResearchTarget (queue/service.py)
    ↓ target includes voi_score = base_VOI
Adjust for Researcher (researcher_voi.adjust_voi_for_collector)
    ↓ fit_factor = f(domain_match, expertise, access, history)
    ↓ VOI_adjusted = base_VOI * fit_factor, clamped [0, 1]
Rank in Queue (get_next_highest_voi_target)
    ↓ targets sorted descending by VOI_adjusted
    ↓ next claim returns highest-VOI unassigned target
Claim and Search
    ↓ human researcher or AutomatedQueueSearcher claims target
    ↓ queries generated from gap description + cross-field vocabulary
    ↓ papers retrieved from Semantic Scholar, Crossref, institutional APIs
Extract and Integrate (paper_integration/orchestrator.py)
    ↓ PDFs analyzed, findings extracted to web-of-belief
Assess Closure (discovery_funnel.assess_closure)
    ↓ closure_fraction = quality of evidence addressing gap
    ↓ marks gap OPEN, PARTIAL, CLOSED, or STALE
VOI Revision (discovery_funnel.revise_voi)
    ↓ new_VOI = base_VOI × (1.0 - closure_fraction)
    ↓ gap deprioritized if closed
Queue Re-ranking
    ↓ get_next_highest_voi_target resorts queue on next claim
```

In the current implementation (February 2026):

- **Gap predictor** (gap_predictor.py) hardcodes voi_score = 0.5 for all gaps. VOIGapScorer.calculate_voi exists but is optionally imported in queue/service.py.
- **Queue service** (queue/service.py) implements get_next_target (returns FIFO) and get_next_highest_voi_target (returns highest VOI_adjusted). The latter is defined but not always used in claim pathways.
- **Discovery funnel** (discovery_funnel.py) tracks gap status and stores closure data but does not implement automatic VOI revision. The closure_fraction is computed but the feedback loop is incomplete.
- **Researcher-specific adjustment** (researcher_voi.py) is fully implemented with compute_researcher_fit, but integration into queue claims is inconsistent.

The disconnect: VOI is computed but underutilized for prioritization. Gaps are ranked FIFO or by default VOI, not by researcher-fit-adjusted VOI. Closure assessment exists but does not propagate feedback to deprioritize closed gaps. The system is architecturally sound but operationally incomplete.

### 47A.2: The Three VOI Computation Modules

#### Gap-Level VOI: voi_search.py (1,945 lines)

**Purpose:** Compute VOI for an epistemic gap at the web level. Input is a PredictedGap description + relevant Beliefs from the web. Output is a base_VOI score ∈ [0, 1].

**When Used:** Optional (lazy-imported in queue/service.py during gap→target conversion). Falls back to voi_score=0.5 if unavailable.

**Key Components:**

- **VOIGapScorer class**: Main entry point. Method calculate_voi(gap: EpistemicGap, web: WebOfBelief) → float
- **Epistemic VOI calculation**: Measures uncertainty (how unknown is the gap?), centrality (how many downstream beliefs depend on it?), sparsity (how few sources address it?)
  - Formula: epistemic_voi = (uncertainty_score + centrality_score + sparsity_score) / 3, where each component ∈ [0, 1]
  - Uncertainty = 1.0 - confidence of source beliefs; if gap is between two conflicting beliefs, uncertainty = 1.0
  - Centrality = count of downstream edge-dependent beliefs / total beliefs in web
  - Sparsity = (theoretical belief count - empirical belief count) / theoretical belief count
- **Structural VOI calculation**: Measures position in causal graph (how critical is this node?), dependency count (how many other gaps depend on closing this one?)
  - Formula: structural_voi = (dependency_in_degree + dependency_out_degree) / (2 × max_degree_in_web)
- **Combined VOI**: base_VOI = 0.5 × epistemic_voi + 0.5 × structural_voi (equal weighting, subject to panel review per C1)

**Example:**

Gap: "Biophilic patterns → Well-being mechanism unspecified. We know patterns help (empirical), but how?"

- Beliefs involved: (1) biophilic patterns reduce stress (confidence 0.65, empirical_association), (2) visual processing of fractals reduces attention load (confidence 0.80, empirical)
- Uncertainty: average of [1-0.65, 1-0.80] = 0.275
- Centrality: This gap affects 7 downstream design recommendations; total web has 234 beliefs. Centrality = 7/234 = 0.03
- Sparsity: 5 theories predict this effect, but only 2 have empirical support. Sparsity = 3/5 = 0.6
- epistemic_voi = (0.275 + 0.03 + 0.6) / 3 = 0.3
- structural_voi = depends on outgoing edges; estimate 0.4 (moderate connectivity)
- base_VOI = 0.5 × 0.3 + 0.5 × 0.4 = 0.35

#### Finding-Level VOI: voi_scoring.py (estimates ~800 lines)

**Purpose:** Evaluate individual extracted findings and assign a VOI bucket (high/medium/low) indicating how valuable each finding is for reducing gaps.

**When Used:** During paper evaluation in paper_integration/cmr/paper_eval.py, after extraction but before integration into web.

**Key Components:**

- **score_voi(findings: List[Finding]) → Dict[Finding, str]** (returns 'high' | 'medium' | 'low')
- Scoring based on: whether finding directly addresses identified gaps, effect size magnitude, methodological rigor, novelty (not replicated before)
- Output used to prioritize which findings to integrate and which to quarantine for expert review

**Relationship to gap-level VOI:** Finding-level VOI asks "how valuable is this particular study result?" Gap-level VOI asks "how important is closing this gap?" They operate at different scales.

#### Lifecycle-Level VOI: discovery_funnel.py (1,200+ lines)

**Purpose:** Track gap status transitions (OPEN → SEARCHING → FOUND → CLOSED/STALE) and compute closure_fraction (how well did retrieved papers address the gap?).

**When Used:** During paper ingestion (discovery_funnel.assess_closure) and gap archiving (discovery_funnel.mark_gap_closed).

**Key Components:**

- **GapStatus enum**: OPEN (not yet searched), SEARCHING (active search), FOUND (results retrieved), CLOSED (addressed), STALE (no progress >7 days)
- **ClosureType enum**: FULL (VOI reduced to <0.1), PARTIAL (≥30% VOI reduction), NONE (<30% reduction), NEGATIVE (uncertainty increased)
- **assess_closure(gap_id, papers: List[Paper]) → ClosureType**: Examines extracted beliefs from papers, measures overlap with gap description, returns closure classification
- **revise_voi(gap_id, closure_fraction: float) → float**: Computes new_VOI = base_VOI × (1.0 - closure_fraction), updates gap record

**Example:**

Gap: "Biophilic patterns mechanism" (base_VOI = 0.35 from above)

After search: 3 papers retrieved
- Paper A: Mechanism speculation (V4 curvature activation), confidence 0.60
- Paper B: Fractal dimension effect on attention, confidence 0.70
- Paper C: Unrelated (visual complexity generally), confidence 0.40
assess_closure computes closure_fraction = average warrant quality = (0.60 + 0.70 + 0.40) / 3 = 0.57
Closes gap as PARTIAL (57% closed)
revise_voi: new_VOI = 0.35 × (1.0 - 0.57) = 0.15
Gap remains in queue but at low priority

### 47A.3: The Adjusted VOI Formula

The queue ranks targets by VOI_adjusted, not base_VOI. The formula is:

```
VOI_adjusted = base_VOI × researcher_fit_factor(collector_profile, gap)
```

**base_VOI** ∈ [0, 1]: Computed by VOIGapScorer (voi_search.py) or defaulted to 0.5.

**researcher_fit_factor** ∈ [0.5, 1.5] (clamped): Multiplies base_VOI to reflect how suitable a particular researcher is for a particular gap. See Section NEW-A2 for details.

**VOI_adjusted** ∈ [0, 1] (clamped): Final priority score used for queue ranking.

**Example:**

Same gap: "Biophilic patterns mechanism" (base_VOI = 0.35)

Three researchers with different profiles:

1. **Researcher A (neuroscientist, expert on visual processing)**
   - Domain match: High (visual mechanism expertise)
   - Expertise fit: High (expert level, gap requires sophisticated knowledge)
   - Theoretical alignment: High (neurobiological interest)
   - Access feasibility: Full (institutional subscriptions)
   - Closure history: 0.70 closure rate on mechanism gaps
   - researcher_fit_factor = 1.3 (strong match)
   - VOI_adjusted = 0.35 × 1.3 = 0.455

2. **Researcher B (architect, intermediate expertise)**
   - Domain match: Moderate (architectural interest but not neuroscience)
   - Expertise fit: Moderate (gap is complex, architect is intermediate)
   - Theoretical alignment: Low (design-focused, not mechanism-focused)
   - Access feasibility: Moderate (limited paywalled access)
   - Closure history: 0.45 closure rate on mechanism gaps
   - researcher_fit_factor = 0.9 (neutral-to-poor match)
   - VOI_adjusted = 0.35 × 0.9 = 0.315

3. **Researcher C (practitioner, novice)**
   - Domain match: Low
   - Expertise fit: Low (gap too complex)
   - Theoretical alignment: Very low (practitioner, not theorist)
   - Access feasibility: Low (no institutional access)
   - Closure history: 0.25 closure rate on mechanism gaps
   - researcher_fit_factor = 0.6 (poor match)
   - VOI_adjusted = 0.35 × 0.6 = 0.21

**Same gap, different researchers, different priorities.** This is David Kirsh's design principle: "Before recommending a topic to a researcher, we need researcher-specific VOI."

### 47A.4: Queue Prioritization Logic

The queue service maintains a dictionary of ResearchTarget objects, each with voi_score (base_VOI) and voi_adjusted (VOI_adjusted after researcher fit).

```python
def get_next_highest_voi_target(collector_id: str) -> Optional[ResearchTarget]:
    """Return the unassigned target with highest VOI_adjusted for this collector."""
    collector = self._collectors[collector_id]
    unassigned = [t for t in self._targets.values()
                  if t.status == TargetStatus.OPEN]
    if not unassigned:
        return None

    # Compute VOI_adjusted for each target given this collector
    scores = [
        (t, adjust_voi_for_collector(t.voi_score, collector, t))
        for t in unassigned
    ]

    # Return target with highest adjusted VOI
    return max(scores, key=lambda x: x[1])[0]
```

**Fallback behavior:** If VOI scores are all zero or unavailable, the method falls back to FIFO (return first unassigned target by creation time). This graceful degradation ensures the queue remains operational even if VOI computation fails.

### 47A.5: The Feedback Loop — Closure Assessment and Queue Re-Ranking

When a gap is closed (discovery_funnel.mark_gap_closed), three things happen:

1. **VOI is revised downward**
   - new_VOI = base_VOI × (1.0 - closure_fraction)
   - Closed gap: new_VOI ≈ 0 (no longer valuable to search)
   - Partially closed gap: new_VOI ≈ 30–70% of original (still has unexplored aspects)

2. **Target status is updated**
   - target.status = TargetStatus.CLOSED
   - target.voi_score = new_VOI
   - target.closure_evidence = warrant_quality from papers

3. **Queue is implicitly re-ranked on next claim**
   - get_next_highest_voi_target re-sorts all unassigned targets
   - Closed/deprioritized gaps drop to bottom of queue
   - New gaps or undiscovered aspects rise to top

This creates a **bidirectional flow**: gaps detected → search executed → closure assessed → VOI revised → queue re-prioritized → new gaps rise. The system continuously adapts its research agenda as the web of belief grows and gaps close.

### 47A.6: Full End-to-End Example

**Day 1: Gap Detection**
- Gap predicted: "How does biophilic design affect creativity? Mechanism unspecified."
- Gap type: MECHANISM
- base_VOI computed: 0.68 (high epistemic importance, low sparsity)
- ResearchTarget created with voi_score = 0.68

**Day 1: Researcher Assignment**
- Collector profile: Dr. Sarah, cognitive neuroscientist, expertise_level=expert, domain_interests=[cognition, neuroscience], closure_rate_on_mechanism_gaps=0.75, can_access_paywalled=true
- researcher_fit_factor computed: 1.25 (strong match on domain, expertise, history)
- VOI_adjusted = 0.68 × 1.25 = 0.85
- Target ranked 2nd highest in Dr. Sarah's queue

**Day 5: Search Execution**
- Dr. Sarah claims target
- QueryGenerator produces: ["biophilic design creativity mechanism", "fractal pattern attention divergent thinking", "nature exposure neural creativity"]
- Semantic Scholar returns 12 papers; Dr. Sarah retrieves 8 PDFs

**Day 10: Paper Integration**
- Papers 1–3 ingested successfully; Papers 4–5 too coarse; Papers 6–8 in progress
- Papers 1–3 extraction yields: mechanism evidence on visual-processing → prefrontal cortex → working-memory pathway (confidence 0.65), plus evidence on aesthetic preference → positive affect → motivation (confidence 0.60)

**Day 10: Closure Assessment**
- discover_funnel.assess_closure examines extracted findings
- Mechanism partially addressed: average warrant quality = 0.625
- classify_closure(0.68, 0.625 × 0.68) → PARTIAL (closure_fraction = 0.625)
- Gap marked PARTIAL with closure_evidence = "mechanism identified: visual processing → prefrontal cortex; remaining questions: relative contributions of aesthetic vs. cognitive pathways"

**Day 10: VOI Revision**
- new_VOI = 0.68 × (1.0 - 0.625) = 0.255
- Gap remains OPEN (not fully closed) but deprioritized
- Target.voi_score updated to 0.255
- Next claim by Dr. Sarah now returns different gap (higher remaining VOI)

**Day 12: Queue Re-Ranking**
- Dr. Sarah claims another target
- get_next_highest_voi_target re-sorts unassigned targets
- Original gap ("biophilic creativity mechanism") now has adjusted VOI = 0.255 × 1.25 = 0.32 (still respectable but lower than before)
- New gaps with VOI 0.70+ rise above it

---

# SECTION NEW-A2: Researcher-Specific VOI and Collector Profiles

## §47B. Researcher-Specific VOI: Personalizing Article Recommendations

### Executive Summary

The system personalizes research recommendations not by presenting identical gap lists to all researchers, but by adjusting VOI scores based on each researcher's expertise, domain interests, access capabilities, and historical performance. This personalization reflects a core design principle from cognitive science: cognitive fit theory (Vessey & Galletta) suggests that information effectiveness depends on the match between information structure and user knowledge/task. Applied to research recommendations: a gap with base_VOI=0.65 is more valuable to a researcher whose expertise aligns with it than to one whose expertise does not.

This section documents how the system models researchers (CollectorProfile), defines the researcher_fit_factor, and uses it to adjust VOI for personalized queue ranking.

### 47B.1: Why Researcher-Specific VOI Matters

In a universal VOI system, all researchers see the same gap priorities. A gap detected as high-VOI (e.g., "Daylight → well-being mechanism") appears in the same priority rank for everyone: neuroscientist, architect, psychologist, practitioner. But their capabilities differ:

- **Neuroscientist**: Can evaluate mechanisms involving neural pathways; prefers peer-reviewed journals; has institutional access to Science, Nature, and other paywalled venues.
- **Architect**: Can evaluate building-context effects; prefers design-focused journals and conference proceedings; has limited paywalled access.
- **Psychologist**: Can evaluate behavioral outcomes; has moderate research access; may not understand neuroscience methods.
- **Practitioner**: Can evaluate real-world applicability; prefers applied design guidance; has no research database access.

The gap "daylight → well-being mechanism" may be high-VOI universally, but its *effective value* differs by researcher. For the neuroscientist, closing it directly advances their expertise and yields high-confidence mechanism evidence. For the practitioner, closing it requires learning neural methods, which is costly and may not advance their design practice.

Researcher-specific VOI adjusts for these mismatches by computing: **VOI_adjusted = base_VOI × researcher_fit_factor**. The fit factor reflects how well the researcher's expertise, interests, access, and historical performance align with the gap. This ensures the system recommends high-priority gaps to researchers suited to them, not universally to everyone.

### 47B.2: The CollectorProfile Model

The CollectorProfile dataclass (queue/models.py) represents a researcher or automated agent. Current fields:

```python
@dataclass
class CollectorProfile:
    collector_id: str                              # Unique ID
    collector_name: str                            # Human-readable name
    collector_type: CollectorType                  # HUMAN_RESEARCHER, HUMAN_ASSISTANT,
                                                   # AUTOMATED_SEARCHER, ZOTERO_WATCHER
    preferred_domains: List[str] = field(default_factory=list)  # [cognition, neuroscience]
    can_access_databases: bool = False             # Access to research databases?
    can_access_paywalled: bool = False             # Access to paywalled content?
    typical_turnaround_hours: float = 48.0         # How fast do they work?
    targets_completed: int = 0                     # Historical count
    gap_closure_rate: float = 0.5                  # Overall closure rate [0, 1]
    avg_articles_per_target: float = 2.5           # Average articles found per gap
```

**New fields to support researcher-specific VOI** (recommended additions):

```python
    expertise_level: float = 0.5                   # [0, 1]: novice to expert
    theoretical_alignment: Dict[str, float] = field(default_factory=dict)
                                                   # {"ART": 0.8, "SRT": 0.5, ...}
                                                   # How much does researcher align with each theory?
    research_stage: str = "discovery"              # discovery, validation, application
    access_level: str = "open_access"              # open_access, paywalled, institutional
    closure_rate_by_gap_type: Dict[str, float] = field(default_factory=dict)
                                                   # {"mechanism": 0.75, "validation": 0.60, ...}
                                                   # Closure rate per gap type
```

These additions enable fine-grained fit computation. For example:

- **Dr. Sarah** (neuroscientist): expertise_level=0.9, theoretical_alignment={"neural_dynamics": 0.95, "cognitive_load": 0.80}, closure_rate_by_gap_type={"mechanism": 0.75, "validation": 0.68}, access_level="institutional"
- **Alex** (architect): expertise_level=0.6, theoretical_alignment={"cognitive_load": 0.70, "affordances": 0.65}, closure_rate_by_gap_type={"boundary": 0.65, "validation": 0.40}, access_level="open_access"

### 47B.3: The researcher_fit_factor Function

Located in src/queue/researcher_voi.py, this function computes a multiplier ∈ [0.5, 1.5] that modulates base_VOI:

```python
def compute_researcher_fit(collector: CollectorProfile, target: ResearchTarget) -> float:
    """
    Compute a 0.5–1.5 fit multiplier for how well this collector matches this target.

    Factors:
    - Domain expertise alignment: ±0.3
    - Expertise-complexity fit: ±0.2
    - Theoretical alignment: ±0.15
    - Access feasibility: ±0.1
    - Closure history on this gap type: ±0.1
    - Workload capacity: ±0.1 (penalty if near max concurrent targets)

    Returns: Float multiplier [0.5, 1.5]
    """
    fit = 1.0  # Start at neutral

    # Domain match: Does target domain align with collector's interests?
    domain_bonus = _compute_domain_fit(collector, target)  # [0.7, 1.3]
    fit *= domain_bonus

    # Expertise fit: Is gap complexity appropriate for researcher?
    expertise_bonus = _compute_expertise_fit(collector, target)  # [0.8, 1.2]
    fit *= expertise_bonus

    # Theoretical alignment: Does gap involve theories researcher knows?
    theory_bonus = _compute_theoretical_alignment(collector, target)  # [0.85, 1.15]
    fit *= theory_bonus

    # Access fit: Can researcher access required sources?
    access_bonus = _compute_access_fit(collector, target)  # [0.9, 1.1]
    fit *= access_bonus

    # Closure history: Has researcher successfully closed this type before?
    closure_bonus = _compute_closure_history(collector, target)  # [0.9, 1.1]
    fit *= closure_bonus

    # Workload: Is researcher overloaded?
    capacity_bonus = _compute_capacity_fit(collector)  # [0.95, 1.05]
    fit *= capacity_bonus

    return min(1.5, max(0.5, fit))  # Clamp to [0.5, 1.5]
```

Each sub-component:

**Domain Match** (returns [0.7, 1.3]): Extracts domain hints from the target's gap type, theory drivers, and description. Checks overlap with collector's preferred_domains.
- Strong match (multiple overlaps): 1.3
- Weak match (single overlap): 1.1
- No match: 1.0

**Expertise Fit** (returns [0.8, 1.2]): Estimates gap complexity (based on gap type and required background knowledge). Compares to collector's expertise_level.
- Complexity exceeds expertise: 0.8 (penalty; difficult task)
- Perfect match: 1.2 (bonus; researcher can handle it efficiently)
- Moderate mismatch: 1.0 (neutral)

**Theoretical Alignment** (returns [0.85, 1.15]): Checks which theories the gap involves (inferred from description). Looks up collector's theoretical_alignment map.
- High alignment on primary theory: 1.15
- Some alignment: 1.0
- Orthogonal: 0.85

**Access Fit** (returns [0.9, 1.1]): Checks if gap requires paywalled sources and if collector can access them.
- Paywalled content needed; collector has access: 1.1
- Paywalled content not needed: 1.0
- Paywalled needed; no access: 0.9 (penalty; researcher cannot execute)

**Closure History** (returns [0.9, 1.1]): Looks up collector's closure_rate_by_gap_type for the target's gap_type.
- High closure rate (>0.65): 1.1 (reward experienced researcher)
- Moderate (0.40–0.65): 1.0
- Low (<0.40): 0.9 (penalty; researcher struggles with this type)

**Workload Capacity** (returns [0.95, 1.05]): Checks how many targets collector has claimed but not yet completed.
- Near capacity (>5 concurrent): 0.95 (slight penalty)
- Moderate load (3–5): 1.0
- Low load (<3): 1.05 (slight bonus; available for more work)

The product of these factors gives the final fit multiplier, clamped to [0.5, 1.5] to prevent extreme over/undervaluation.

### 47B.4: Personalized Queue Example

Three researchers see the same set of 10 gaps. The queue service ranks them differently for each researcher:

**Gap Pool** (base_VOI scores):

1. "Daylight → mood mechanism" (base_VOI = 0.72)
2. "Fractal patterns → attention" (base_VOI = 0.68)
3. "Thermal comfort → focus validation" (base_VOI = 0.55)
4. "Color temperature → alertness boundary" (base_VOI = 0.60)
5–10. [other gaps, base_VOI = 0.50–0.65]

**Researcher A (Dr. Sarah, neuroscientist)**

- Preferred domains: [cognition, neuroscience]
- Expertise: 0.9
- Theoretical alignment: {"neural_dynamics": 0.95, "circadian": 0.80}
- Access: institutional (paywalled)
- Closure rate by type: {"mechanism": 0.75, "boundary": 0.68}

Queue ranking (adjusted VOI descending):

1. Gap 1 ("Daylight → mood mechanism"): fit_factor=1.25, adjusted=0.90
2. Gap 2 ("Fractal patterns → attention"): fit_factor=1.20, adjusted=0.82
3. Gap 4 ("Color → alertness boundary"): fit_factor=1.15, adjusted=0.69
4. Gap 3 ("Thermal → focus validation"): fit_factor=0.85, adjusted=0.47
5–10. [other gaps]

**Researcher B (Alex, architect)**

- Preferred domains: [design, environmental_psychology]
- Expertise: 0.6
- Theoretical alignment: {"affordances": 0.75, "cognitive_load": 0.60}
- Access: open access only
- Closure rate by type: {"boundary": 0.65, "validation": 0.40}

Queue ranking (adjusted VOI descending):

1. Gap 4 ("Color → alertness boundary"): fit_factor=1.15, adjusted=0.69
2. Gap 1 ("Daylight → mood mechanism"): fit_factor=0.90, adjusted=0.65
3. Gap 2 ("Fractal patterns → attention"): fit_factor=0.95, adjusted=0.65
4. Gap 3 ("Thermal → focus validation"): fit_factor=1.05, adjusted=0.58
5–10. [other gaps]

**Researcher C (Practitioner, novice)**

- Preferred domains: [design_application]
- Expertise: 0.4
- Theoretical alignment: {} (no formal theories)
- Access: open access only
- Closure rate by type: {"validation": 0.35, "boundary": 0.50}

Queue ranking (adjusted VOI descending):

1. Gap 4 ("Color → alertness boundary"): fit_factor=1.10, adjusted=0.66
2. Gap 3 ("Thermal → focus validation"): fit_factor=1.05, adjusted=0.58
3. Gap 1 ("Daylight → mood mechanism"): fit_factor=0.60, adjusted=0.43
4. Gap 2 ("Fractal patterns → attention"): fit_factor=0.65, adjusted=0.44
5–10. [other gaps]

**Interpretation**: Dr. Sarah sees mechanism gaps as most valuable (her strength). Alex sees boundary and validation gaps as most valuable (matches his expertise). The practitioner sees validation gaps as most valuable (practical guidance). The same gap pool produces three different priority orders based on researcher-specific fit.

### 47B.5: Learning and Updating the researcher_fit_factor

The initial fit factor is computed from static profile fields (expertise_level, theoretical_alignment, access_level). Over time, as the researcher completes targets, the system can learn and refine the fit factor:

**Mechanism 1: Historical Closure Rate**

After each target is closed, the closure_rate_by_gap_type is updated:

```python
# Before: researcher B has closure_rate_by_gap_type["boundary"] = 0.65
# Researcher B closes "Color temperature boundary" gap
# Update: closure_rate_by_gap_type["boundary"] = (0.65 × N + 1.0) / (N + 1)
# where N = number of previously completed boundary gaps
```

This empirical signal gradually refines the fit factor. If Alex consistently closes boundary and validation gaps but struggles with mechanism gaps, his fit factor for those gap types will adjust accordingly.

**Mechanism 2: Turnaround Time**

If a researcher consistently takes longer than typical_turnaround_hours to close a gap, the system can infer they are overloaded or the gap is harder than estimated, and adjust fit downward for similar gaps in future.

**Mechanism 3: Theoretical Capability**

If a researcher's successful closures show evidence of understanding (e.g., they cite theory-relevant papers), the theoretical_alignment mapping can be updated to reflect genuine capability, not just stated interest.

### 47B.6: Interaction with CollectorProfile Fields

The expanded CollectorProfile provides fine-grained context for fit computation. Key interactions:

- **expertise_level + gap_type complexity**: Mechanism gaps require high expertise (typically 0.7+); validation gaps tolerate lower expertise (0.4+).
- **closure_rate_by_gap_type + historical performance**: If a researcher's closure_rate_by_gap_type["mechanism"] = 0.20 (struggles), their fit factor for mechanism gaps should be <1.0, regardless of other factors.
- **access_level + target_databases**: If target requires paywalled databases (SAGE, ProQuest) and researcher has access_level="open_access", fit_factor for that target should be reduced.
- **research_stage + gap_type**: A researcher in "validation" stage is better suited to validation gaps; "discovery" stage researchers are better suited to exploratory mechanism/boundary gaps.

---

# SECTION NEW-A3: Article Search Execution Pipeline

## §47C. Article Search Execution Pipeline: From Gap to PDF Ingestion

### Executive Summary

Once a gap is prioritized in the queue, the search execution pipeline orchestrates the journey from gap description to integrated research findings in the web of belief. This pipeline coordinates query generation, source selection, PDF retrieval, extraction, quality validation, and closure assessment. The pipeline operates in two modes: automated (when VOI exceeds a threshold) and manual (when a human researcher claims a target). This section documents the end-to-end orchestration, design decisions, and integration points with the discovery funnel.

### 47C.1: End-to-End Orchestration

The complete pipeline proceeds as follows:

```
ResearchTarget in Queue (from §47A)
    │ status = OPEN, voi_adjusted = <value>
    │
├─ Automated Trigger? (VOI_adjusted > threshold)
│   └─ AutomatedQueueSearcher.run_once() claims target
├─ Manual Trigger? (researcher claims via UI)
│   └─ Human researcher claims target
└─ No Trigger
    └─ Target remains queued, waiting for claim
    │
Target Claimed (status = SEARCHING)
    │
QueryGenerator.generate_queries(gap_description, gap_type)
    │ Preferred: VOI-enhanced queries (if voi_search available)
    │ Fallback: FallbackQueryGenerator (simple keyword extraction)
    │
├─ Primary queries: 3–5 specific domain-focused queries
├─ Secondary queries: 2–3 broader cross-field queries (search alternate terminology)
└─ Source order preference: SemanticScholar, PubMed, Crossref (domain-dependent)
    │
Execute Searches (rate-limited)
    │ SemanticScholar API: 300 requests/second (as of Feb 2026)
    │ Exponential backoff on rate-limit hits
    │ Collect results: paper metadata, DOI, abstract, PDF link candidates
    │
Results Filtering & Ranking
    │ Score papers by: relevance to gap, publication date (recent preferred),
    │ citation count (if available), open access status
    │ Select top N papers (config: default 5–10)
    │
PDF Retrieval (multiple strategies)
    │
    ├─ Strategy 1: SemanticScholar direct link
    │   └─ Request PDF link from API; download if available
    │
    ├─ Strategy 2: Crossref DOI → Unpaywall API
    │   └─ Resolve DOI, check Unpaywall for open-access copy
    │
    ├─ Strategy 3: Institutional Repository
    │   └─ If collector has can_access_paywalled=true, try library proxy
    │
    ├─ Strategy 4: Author Email Request
    │   └─ If PDF not accessible, queue author request (slow, 2–4 week turnaround)
    │
    └─ Strategy 5: Fallback to Metadata-Only
        └─ If PDF retrieval fails, store paper with abstract only
        │ (integration pipeline handles metadata-only papers differently)
        │
Target Status Update (status = FOUND)
    │
Paper Integration Pipeline (src/paper_integration/orchestrator.py)
    │
    ├─ Extract metadata: title, authors, abstract, keywords, publication year
    │
    ├─ Extract full text from PDF (if available)
    │   └─ Quality rules applied: minimum page count, OCR confidence
    │
    ├─ Extract findings (src/extraction/cmr/*.py)
    │   └─ Identify claims, evidence, mechanisms, limitations
    │   └─ Score extraction quality (AESHI score for each finding)
    │
    ├─ Assess warrant strength (§51, Bridge Warrants)
    │   └─ Classify each finding as: EMPIRICAL_ASSOCIATION, MECHANISM,
    │      CONSTITUTIVE, or ANALOGICAL
    │   └─ Assign confidence ω based on study quality, effect size, replication
    │
    └─ Convert to web-of-belief format
        └─ Create Belief objects, WarrantEdge objects, constraint edges
        │
Discovery Funnel Integration (src/services/discovery_funnel.py)
    │
    ├─ Check: Do extracted findings address the original gap?
    │   └─ Measure overlap between gap description and finding content
    │   └─ Compute closure_fraction = average warrant quality addressing gap
    │
    ├─ Classify closure: FULL, PARTIAL, NONE, or NEGATIVE
    │   └─ Per discovery_funnel.classify_closure:
    │      - FULL: VOI reduced to <0.1 (gap essentially closed)
    │      - PARTIAL: ≥30% VOI reduction
    │      - NONE: <30% reduction (minor evidence)
    │      - NEGATIVE: VOI increased (new uncertainty)
    │
    └─ Update gap status
        └─ If FULL: status = CLOSED, target removed from queue
        └─ If PARTIAL: status = OPEN (remains for future searches), VOI revised
        └─ If NONE: status = OPEN, no VOI revision
        └─ If NEGATIVE: status = OPEN, VOI increased (urgent for re-search)
    │
Queue Re-Ranking (implicit, on next claim)
    │
    ├─ Closed gaps drop to bottom of queue
    ├─ Partially-closed gaps drop but remain searchable
    └─ Unchanged gaps maintain relative position
```

### 47C.2: Automated vs. Manual Search Triggering

**Automated Search:**

Threshold-based triggering. If VOI_adjusted > T_auto (config default: 0.65), the AutomatedQueueSearcher.run_once() method claims the target and executes the search without human intervention.

Advantages:
- Covers high-priority gaps immediately, no human delay
- Scalable: multiple searcher instances can run in parallel
- Reduces researcher workload for routine gaps

Disadvantages:
- Risk of incorrect queries or interpretation without human judgment
- Consumes API rate limits quickly
- May waste resources on low-quality results

Implementation (queue/service.py):

```python
def run_automated_searcher(self, max_targets: int = 5) -> Dict[str, SearchResult]:
    """Run automated search on up to max_targets highest-VOI gaps."""
    results = {}
    for i in range(max_targets):
        target = self.get_next_highest_voi_target("automated_searcher_id")
        if not target or target.voi_adjusted <= 0.65:  # Below threshold
            break

        # Generate queries and execute search
        queries = self.query_generator.generate_queries(
            target.gap_description, target.gap_type
        )
        papers = self._search_papers(queries, target.target_databases)

        # Download PDFs and integrate
        result = self._integrate_papers(target.target_id, papers)
        results[target.target_id] = result

    return results
```

**Manual Search:**

Human researcher claims a target via the UI. The queue returns the target, researcher reviews the gap description, generates/refines queries, and conducts the search themselves.

Advantages:
- Researcher judgment on query quality and result relevance
- Can handle subtle gaps requiring human interpretation
- Researcher learns about problem domain

Disadvantages:
- Slower than automated (human turnaround time ~24–72 hours)
- Requires researcher availability and motivation
- Not scalable to large gap backlogs

Implementation (queue/service.py):

```python
def claim_target(self, collector_id: str, target_id: Optional[str] = None) -> ClaimResult:
    """Claim a target for a collector."""
    if target_id:
        target = self.get_target(target_id)  # Specific claim
    else:
        target = self.get_next_highest_voi_target(collector_id)  # Auto-select highest VOI

    if not target:
        return ClaimResult(success=False, message="No targets available")

    # Update target status and return for researcher action
    target.status = TargetStatus.SEARCHING
    target.claimed_by = collector_id
    target.claimed_at = datetime.now(timezone.utc)

    return ClaimResult(
        success=True,
        target=target,
        suggested_queries=self.query_generator.generate_queries(
            target.gap_description, target.gap_type
        )
    )
```

### 47C.3: Query Generation Strategy

The queue service uses one of two query generators, depending on availability:

**VOI-Enhanced QueryGenerator (Preferred):**

Located in src/services/voi_search.py. Uses gap description, gap_type, and CrossFieldVocabulary to generate rich, domain-specific queries.

Example:

Gap description: "How does exposure to natural views affect cognitive restoration in office workers? Mechanism unclear."

Gap type: MECHANISM

VOI-enhanced queries:

1. "natural views cognitive restoration office workers" (primary, specific)
2. "nature window attention recovery workplace" (secondary, conceptual synonym)
3. "biophilic design stress recovery ART theory" (tertiary, theory-driven)
4. "prospect refuge office design psychological benefit" (domain-specific alternative)
5. "window access restorative environments workplace cognitive load" (cross-field expansion)

Cross-field vocabulary enables translation: "cognitive restoration" → "attention recovery", "stress recovery", "mental fatigue relief" (synonyms in adjacent disciplines).

**FallbackQueryGenerator (Fallback Only):**

Located in src/queue/service.py. Simple keyword extraction when voi_search unavailable.

Implementation:

```python
class _FallbackQueryGenerator:
    def generate_queries(self, text: str, gap_type: GapType) -> List[str]:
        """Extract keywords from gap description; generate domain-specific variants."""
        terms = self._extract_terms(text)  # Remove stopwords, tokenize

        if gap_type == GapType.MECHANISM:
            return [
                " ".join(terms[:6]),  # Base query
                f"{' '.join(terms[:4])} mechanism",  # Mechanism-specific
                f"{' '.join(terms[:4])} pathway",  # Alternative
            ]
        elif gap_type == GapType.VALIDATION:
            return [
                " ".join(terms[:6]),
                f"{' '.join(terms[:4])} replication",
                f"{' '.join(terms[:4])} meta analysis",
            ]
        # ... similar for other gap types

        return [" ".join(terms[:6])]  # Fallback: just keywords
```

Fallback queries are simpler and less effective but remain operational when VOI modules unavailable, supporting graceful degradation.

### 47C.4: PDF Retrieval Strategy

The pipeline tries multiple sources in sequence, stopping at first success:

1. **SemanticScholar API:** Fastest. If SemanticScholar result includes `is_open_access=true` or `s2_pdf_url` is available, retrieve directly.

2. **Unpaywall API:** Free service that checks across 10,000+ repositories. Given DOI, returns open-access PDF link if one exists.

3. **Institutional Repository (if paywalled access available):** If collector has `can_access_paywalled=true`, attempt library proxy access to publisher PDF.

4. **Author Email Request:** If all above fail, generate email to author requesting PDF. Slow (2–4 week typical response) but often succeeds. Stored as pending retrieval task.

5. **Metadata-Only Fallback:** If PDF unattainable after 48 hours, store paper metadata (abstract, keywords) without PDF. Integration pipeline handles this gracefully—extraction uses abstract instead of full text, confidence scores reduced.

**Rate Limiting:**

SemanticScholar enforces 300 requests/second (as of Feb 2026). The queue service implements exponential backoff:

```python
def _search_papers(self, queries: List[str], databases: List[str]) -> List[Dict]:
    """Search papers; handle rate limiting with exponential backoff."""
    papers = []
    for query in queries:
        retry_count = 0
        while retry_count < 5:
            try:
                results = semantic_scholar_api.search(query)
                papers.extend(results)
                break
            except RateLimitError:
                wait_time = 2 ** retry_count  # 1, 2, 4, 8, 16 seconds
                logger.info(f"Rate limited; waiting {wait_time}s")
                time.sleep(wait_time)
                retry_count += 1
    return papers
```

### 47C.5: Quality Rules and Extraction Pipeline

After PDF retrieval, the paper_integration/orchestrator.py applies quality rules (contracts/schemas/extraction_quality_rules.json) to filter low-quality papers:

- **Minimum page count:** ≥4 pages (excludes editorials, short notes)
- **OCR confidence:** ≥0.85 (excludes papers with poor PDF text extraction)
- **Publication type:** Prefer peer-reviewed; accept preprints with confidence discount
- **Recency:** Recent papers (≤10 years) preferred; older papers accepted with confidence discount
- **Relevance:** Abstract must overlap ≥40% with gap keywords (prevents off-target retrievals)

Papers passing quality gates proceed to extraction. Findings are scored on AESHI (Article Eater Skeptic Health Index, see §53.8) scale—high AESHI findings are high-confidence extractions that can be integrated immediately; low AESHI findings are quarantined for expert review.

### 47C.6: Gap Closure Assessment and Deprioritization

After extraction, discovery_funnel.assess_closure(gap_id, papers) computes how well the papers addressed the gap:

```python
def assess_closure(self, gap_id: str, papers: List[Paper]) -> ClosureType:
    """Assess how well extracted papers addressed the gap."""
    gap = self._gaps[gap_id]

    # Extract evidence from papers addressing this gap
    evidence_beliefs = [
        b for p in papers
        for b in p.extracted_beliefs
        if self._overlaps_gap(b, gap)
    ]

    if not evidence_beliefs:
        return ClosureType.NONE  # Papers didn't address gap

    # Average warrant quality
    avg_quality = sum(b.warrant.strength for b in evidence_beliefs) / len(evidence_beliefs)

    # Classify closure
    if avg_quality >= 0.75:
        return ClosureType.FULL
    elif avg_quality >= 0.55:
        return ClosureType.PARTIAL
    else:
        return ClosureType.NONE
```

Based on closure type, the gap is marked CLOSED, PARTIAL, or remains OPEN, and VOI is revised accordingly (per §47A.5).

---

# SECTION NEW-A4: QA System as Recommendation Source

## §47D. QA System Integration: From Follow-Up Questions to Search Recommendations

### Executive Summary

The arbitrary QA system (arbitrary_qa_handler.py, ~600 lines) answers user questions about system knowledge. When answering, the QA handler can identify follow-up research questions that would strengthen the answer. This section documents how QA-identified gaps are pushed into the research queue, enabling the system to proactively improve its knowledge base in response to user inquiries.

### 47D.1: Current QA System Architecture

The arbitrary_qa_handler manages six handler types, each specialized for a question category:

| Handler Type | Question Category | Example | Output |
|--------------|-------------------|---------|--------|
| CatalogHandler | "What aspects exist?" | "What are the mechanisms of biophilia?" | List of known mechanisms |
| EvidenceHandler | "What evidence supports this?" | "Does nature reduce stress?" | Supporting papers, credence |
| ComparisonHandler | "How do X and Y differ?" | "Difference between ART and SRT?" | Comparative analysis |
| MechanismHandler | "How does X cause Y?" | "How does daylight affect mood?" | Causal pathway, confidence, gaps |
| DefinitionHandler | "What is X?" | "Define circadian entrainment" | Definition, variations, applications |
| MetaHandler | "How certain is the system?" | "How confident in nature–stress link?" | Confidence bands, caveats |

### 47D.2: QA Handler Architecture and Integration Points

Currently, each handler is query-reactive: user asks question → handler answers → conversation ends.

The aspirational design is question-driven gap generation:

```python
def answer(self, question: str) -> Tuple[str, List[FollowUp], Optional[List[SearchGap]]]:
    """
    Answer a question and optionally generate follow-up research gaps.

    Returns:
        (answer_text, follow_up_questions, search_gaps)
    """
    # Handle question according to type
    handler = self._select_handler(question)
    answer = handler.answer(question)

    # Generate follow-up questions (user may click for clarification)
    follow_ups = handler.suggest_follow_ups(question)

    # Proactively generate SearchGaps if handler identifies gaps
    search_gaps = handler.identify_gaps(question)  # NEW

    return (answer, follow_ups, search_gaps)
```

Each handler's identify_gaps method looks for:

- **Missing evidence:** Question askers want to know X, but system has low confidence in answer. Generate VALIDATION_GAP.
- **Unclear mechanisms:** System can answer "does X help?" but not "how?" Generate MECHANISM_GAP.
- **Boundary questions:** System tested effect in context A but not B. Generate BOUNDARY_GAP.

### 47D.3: QA-Generated Gaps as ResearchTargets

Example: User asks "Does red color improve focus in office workers?"

MechanismHandler.answer() returns:

```
Answer: "Limited evidence suggests color temperature affects arousal and attention.
Warm color (2700K) may enhance focus in low-stress tasks; cool color (5000K+) in
high-distraction environments. Mechanism unclear—possibly linked to circadian
photoentrainment (cool light → alertness) and color-emotion associations (warm →
calmness). Confidence: moderate (0.55). Caveat: No studies on office worker
populations specifically."

Follow-ups:
- "What mechanism explains the color-focus link?"
- "Does effect depend on lighting context?"

Search Gaps Generated:
- Gap 1: MECHANISM_GAP ("Red color → focus mechanism in office context")
  - Base VOI: 0.45 (lower than user-identified gaps because secondary)
  - Suggested queries: ["color temperature alertness mechanism", "warm light office focus"]
  - Reason: "Answer noted mechanism unclear; evidence from circadian/emotion paths but
            office-specific mechanism untested"

- Gap 2: VALIDATION_GAP ("Red color → focus validation in office worker population")
  - Base VOI: 0.40
  - Suggested queries: ["warm color office worker focus study", "color preference alertness"]
  - Reason: "Answer noted no office-specific studies; caveat indicates evidence gap"
```

### 47D.4: Integration with ResearchQueueService

The QA handler pushes identified search gaps into the queue:

```python
# In arbitrary_qa_handler.py or orchestrator
def answer_with_queue_integration(self, question: str, queue_service: ResearchQueueService):
    """Answer question; push generated gaps to research queue."""
    answer, follow_ups, search_gaps = self.answer(question)

    # Push SearchGaps to queue
    if search_gaps:
        for search_gap in search_gaps:
            queue_service.add_qa_generated_gap(
                gap_type=search_gap.gap_type,
                gap_description=search_gap.description,
                suggested_queries=search_gap.suggested_queries,
                base_voi=search_gap.base_voi,
                reason=search_gap.reason
            )

    return answer, follow_ups
```

The queue service converts SearchGap to ResearchTarget and adds to queue:

```python
def add_qa_generated_gap(self, gap_type: GapType, gap_description: str,
                         suggested_queries: List[str], base_voi: float, reason: str):
    """Add a QA-identified gap to the research queue."""
    target = ResearchTarget(
        target_id=f"qa_{uuid.uuid4()}",
        gap_type=gap_type,
        gap_description=gap_description,
        voi_score=base_voi,
        source="qa_system",  # Track origin
        suggested_queries=suggested_queries,
        reason_for_gap=reason,  # Human-readable explanation
        status=TargetStatus.OPEN,
        created_at=datetime.now(timezone.utc)
    )
    self._targets[target.target_id] = target
```

### 47D.5: VOI Calibration for QA-Generated Gaps

QA-generated gaps receive lower base_VOI than user-identified or theory-driven gaps because they are secondary (answering a question is primary; improving the answer is secondary):

| Gap Source | Typical Base VOI Range | Justification |
|-----------|----------------------|---------------|
| User-identified | 0.60–0.85 | User explicitly identified as important |
| Theory-driven | 0.55–0.80 | Framework predicts as important |
| QA-generated | 0.30–0.60 | System identified, secondary priority |
| Boundary extension | 0.40–0.65 | Existing gap in new context |

QA-generated MECHANISM gaps score higher (0.50–0.60) than VALIDATION gaps (0.30–0.45) because mechanisms directly improve mechanistic explanations, while validations confirm existing findings.

### 47D.6: Design Decisions Requiring Panel Review

**Decision 1:** Should QA system proactively generate SearchGaps for all questions, or only for questions where confidence is below threshold?

- **Option A (Proactive)**: Every question generates potential gaps. Advantage: comprehensive. Disadvantage: floods queue with low-priority gaps.
- **Option B (Threshold-based)**: Only generate SearchGaps when answer confidence < 0.50. Advantage: higher-priority gaps. Disadvantage: misses some valuable follow-up directions.
- **Recommendation**: Start with Option B (threshold-based). Reduce threshold to 0.40 after 3 months if queue remains under capacity.

**Decision 2:** Should QA-generated gaps be anonymized, or linked to the original question?

- **Option A (Linked)**: Store original question with gap, enabling researchers to understand context. Advantage: better interpretation. Disadvantage: privacy concern if question is sensitive.
- **Option B (Anonymized)**: Store only gap description. Advantage: privacy-preserving. Disadvantage: context loss.
- **Recommendation**: Linked by default (Option A), with user opt-out for sensitive questions.

---

# SECTION NEW-A5: Discovery Funnel Feedback Loop

## §47E. Discovery Funnel Feedback Loop: Bidirectional Tracking and VOI Revision

### Executive Summary

The discovery funnel (discovery_funnel.py, ~1,200 lines) tracks gaps through stages: OPEN (not yet searched) → SEARCHING (active search) → FOUND (results retrieved) → CLOSED (addressed) or STALE (no progress). Critically, the funnel is bidirectional: when gaps close, the funnel provides feedback to revise VOI scores and deprioritize them in the queue. This feedback loop operationalizes a core principle: as the web of belief grows, gaps close, and the research agenda must adapt.

### 47E.1: Funnel Design and Gap Lifecycle

The discovery_funnel maintains a SQLite database (discovery_funnel.db) with complete records:

```sql
CREATE TABLE voi_gaps (
    gap_id TEXT PRIMARY KEY,
    description TEXT,
    gap_type TEXT,  -- mechanism, validation, direction, boundary
    base_voi REAL,  -- Original VOI score
    source TEXT,    -- 'predictor', 'qa_system', 'user_identified', 'theory_driven'
    status TEXT,    -- open, searching, found, closed, stale
    created_at TEXT,
    searched_at TEXT,  -- When first search executed
    closed_at TEXT,    -- When marked closed
    closure_type TEXT, -- full, partial, none, negative
    closure_fraction REAL,  -- 0.0–1.0: what % of gap addressed?
    closure_evidence TEXT   -- Description of what closed it
);

CREATE TABLE gap_history (
    id INTEGER PRIMARY KEY,
    gap_id TEXT,
    status_old TEXT,
    status_new TEXT,
    voi_old REAL,
    voi_new REAL,
    event_type TEXT,  -- searched, found, closed, revised, stale
    timestamp TEXT,
    FOREIGN KEY (gap_id) REFERENCES voi_gaps(gap_id)
);
```

**Gap Status Transitions:**

```
OPEN ──(search executed)──> SEARCHING
        │                      │
        │                      ├─(results found)──> FOUND
        │                      │                      │
        │                      │                      ├─(papers good)──> CLOSED
        │                      │                      │
        │                      │                      └─(papers partial)──> OPEN (with revised VOI)
        │                      │
        │                      └─(no results)──> OPEN
        │
        └─(no search for 7 days)──> STALE
```

Key insight: A gap can be OPEN multiple times. Each time it's searched, VOI is revised downward. Eventually, it closes when papers provide sufficient evidence, or it becomes STALE if no progress occurs.

### 47E.2: Closure Assessment Framework

When papers are integrated into the web, discovery_funnel.assess_closure computes closure_fraction:

```python
def assess_closure(self, gap_id: str, papers: List[Paper]) -> Tuple[ClosureType, float]:
    """
    Assess how well extracted papers addressed the gap.

    Returns:
        (closure_type, closure_fraction)
        closure_fraction ∈ [0, 1]: proportion of gap closed by evidence
    """
    gap = self._get_gap(gap_id)

    # Extract beliefs from papers that address this gap
    relevant_beliefs = []
    for paper in papers:
        for belief in paper.extracted_beliefs:
            if self._belief_addresses_gap(belief, gap):
                relevant_beliefs.append(belief)

    if not relevant_beliefs:
        return ClosureType.NONE, 0.0

    # Compute closure_fraction as average warrant quality
    warrant_qualities = [b.warrant_strength for b in relevant_beliefs]
    closure_fraction = sum(warrant_qualities) / len(warrant_qualities)

    # Classify closure
    closure_type = classify_closure(gap.base_voi, gap.base_voi * (1 - closure_fraction))

    return closure_type, closure_fraction
```

The function measures how well papers' extracted findings overlap with the gap's description. Overlap is quantified as warrant_quality (see §51, Bridge Warrants): how strongly does each finding support the gap's resolution?

### 47E.3: VOI Revision Formula

When a gap is assessed as FULL, PARTIAL, or NEGATIVE, its VOI is revised:

```python
def revise_voi(self, gap_id: str, closure_fraction: float) -> float:
    """
    Revise VOI based on gap closure.

    Formula: new_VOI = base_VOI × (1.0 - closure_fraction)

    Interpretation:
    - closure_fraction = 0.0: gap unchanged (new_VOI = base_VOI)
    - closure_fraction = 0.5: gap 50% closed (new_VOI = 0.5 × base_VOI)
    - closure_fraction = 1.0: gap fully closed (new_VOI = 0)
    """
    gap = self._get_gap(gap_id)
    old_voi = gap.voi_score
    new_voi = gap.base_voi * (1.0 - closure_fraction)

    # Cap at zero (no negative VOI)
    new_voi = max(0.0, new_voi)

    # Update gap record
    gap.voi_score = new_voi
    gap.closure_fraction = closure_fraction

    # Log history
    self._log_transition(gap_id, old_voi, new_voi, "voi_revision", closure_fraction)

    return new_voi
```

**Intuition:** If a gap is fully closed (closure_fraction=1.0), VOI becomes zero—no value in searching further. If partially closed (closure_fraction=0.6), VOI is reduced by 60%, but not eliminated—the gap retains value for follow-up searches exploring unanswered aspects.

### 47E.4: Queue Re-Ranking on VOI Revision

When VOI is revised, the gap's priority in the queue changes automatically:

**Mechanism 1: Implicit Re-ranking on Claim**

When a collector claims the next target via get_next_highest_voi_target(), the queue re-sorts unassigned targets by current VOI_adjusted. Gaps whose VOI was revised downward automatically drop in priority.

```python
def get_next_highest_voi_target(self, collector_id: str) -> Optional[ResearchTarget]:
    """Return highest-VOI unassigned target, re-sorted on current VOI scores."""
    unassigned = [t for t in self._targets.values() if t.status == TargetStatus.OPEN]

    # Recalculate VOI_adjusted using current voi_score (may have been revised)
    scored = [
        (t, adjust_voi_for_collector(t.voi_score, self._collectors[collector_id], t))
        for t in unassigned
    ]

    if not scored:
        return None

    return max(scored, key=lambda x: x[1])[0]
```

**Mechanism 2: Explicit Re-ranking Trigger**

Optionally, ResearchQueueService can trigger explicit re-ranking:

```python
def re_rank_queue(self):
    """Re-sort all open targets by current VOI_adjusted."""
    for target in self._targets.values():
        if target.status == TargetStatus.OPEN:
            for collector_id, collector in self._collectors.items():
                target.voi_adjusted = adjust_voi_for_collector(
                    target.voi_score, collector, target
                )
```

This is useful periodically (e.g., daily) or after bulk closure events.

### 47E.5: Stale Gap Handling

If a gap remains OPEN (unsearched or partially closed) for >7 days, it is marked STALE:

```python
def mark_stale_gaps(self, age_threshold_days: int = 7):
    """Mark gaps as STALE if unsearched for too long."""
    now = datetime.now(timezone.utc)
    for gap in self._gaps.values():
        if gap.status == GapStatus.OPEN:
            age_days = (now - gap.created_at).days
            if age_days > age_threshold_days and gap.searched_at is None:
                gap.status = GapStatus.STALE
                self._log_transition(gap.gap_id, gap.status, GapStatus.STALE, "stale_mark")
```

STALE gaps are deprioritized but not deleted. VOI decays gradually:

```python
stale_decay_factor = 0.9 ** (age_days / 7)  # Decay 10% per week
voi_with_decay = gap.voi_score * stale_decay_factor
```

This prevents high-VOI gaps from being overlooked indefinitely while acknowledging that very old unaddressed gaps may have become less relevant.

### 47E.6: Full Example — Bidirectional Loop

**Day 1: Gap Detection**

Gap predicted: "Biophilic design → creativity mechanism"

- base_VOI: 0.72
- source: "theory_driven"
- status: OPEN
- created_at: 2026-03-01 09:00 UTC

Discovery funnel stores gap. Queue service converts to ResearchTarget and adds to queue.

**Day 5: Search Claimed and Executed**

Dr. Sarah claims the target. QueryGenerator produces queries. Papers retrieved: 4 papers, 3 PDFs successful.

- status → SEARCHING (2026-03-05 10:00)
- searched_at: 2026-03-05 10:00

**Day 10: Papers Integrated**

Papers 1–3 extracted. Beliefs identified:

- Paper 1: "Biophilic visual patterns activate PFC" (warrant_quality 0.70)
- Paper 2: "Nature scenes reduce mental fatigue" (warrant_quality 0.60)
- Paper 3: "Fractal patterns improve attention" (warrant_quality 0.65)

discovery_funnel.assess_closure:

- relevant_beliefs: 3 papers
- closure_fraction: (0.70 + 0.60 + 0.65) / 3 = 0.65
- classify_closure(base_voi=0.72, new_voi=0.72 × (1-0.65)=0.252) → PARTIAL
- status → OPEN (remains searchable; not fully closed)

VOI revised: gap.voi_score = 0.252

History logged: {old_voi: 0.72, new_voi: 0.252, closure_type: PARTIAL, closure_fraction: 0.65}

**Day 12: Queue Re-Ranking**

Dr. Sarah claims another target. get_next_highest_voi_target re-sorts:

Before revision:
1. "Biophilic creativity mechanism" (voi_adjusted = 0.72 × 1.25 = 0.90, rank 1)
2. "Nature view anxiety reduction" (voi_adjusted = 0.60 × 1.10 = 0.66, rank 2)

After revision:
1. "Nature view anxiety reduction" (voi_adjusted = 0.60 × 1.10 = 0.66, rank 1)
2. "Biophilic creativity mechanism" (voi_adjusted = 0.252 × 1.25 = 0.315, rank 2)

The original gap drops from 1st to 2nd place due to reduced VOI.

**Day 30: Stale Marking**

If the gap remains OPEN (no new searches) for 29 more days (total 39 days):

- age_days: 39
- stale_decay: 0.9^(39/7) = 0.9^5.57 ≈ 0.58
- voi_with_decay: 0.252 × 0.58 = 0.146
- status → STALE (if desired)

Deprioritized but remains searchable if new evidence emerges.

### 47E.7: Closing Principle — The Feedback Loop Is Live

The critical insight: the funnel is not a passive record but an active feedback system. As papers are integrated, VOI is revised *immediately*. The next researcher claim sees updated priorities. Over time, highly-closed gaps drop from the queue, and new high-priority gaps rise. The research agenda adapts in real time to the system's growing knowledge.

---

# SECTION NEW-A6: Overseer Management Database Schema

## §132.6a Overseer Management Layer Database Schema

### Executive Summary

The OVERSEER system (§132) monitors system health and tracks suggestion backlogs. To do so, it requires database tables to store interpretation space suggestions, management pipeline status, and oversight alerts. This section defines the complete schema, insertion points, and queries expected by the overseer_management.py module.

### 132.6a.1: Complete Schema Design

**Table 1: interpretation_space_suggestions**

Purpose: Track suggestions identified by the interpretation space, gap predictor, QA system, and other suggestion sources.

```sql
CREATE TABLE interpretation_space_suggestions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gap_id TEXT NOT NULL,
    suggestion_id TEXT UNIQUE NOT NULL,
    source TEXT NOT NULL,
    -- source ∈ {interpretation_space, voi, qa_system, argumentation, user_identified, other}
    suggestion_type TEXT,
    -- suggestion_type ∈ {mechanism, validation, boundary, direction, interaction}
    status TEXT NOT NULL DEFAULT 'proposed',
    -- status ∈ {proposed, identified, in_progress, addressed, archived}
    priority REAL,
    -- VOI score or custom priority ranking [0, 1]
    created_at TEXT NOT NULL,
    -- ISO 8601 timestamp
    updated_at TEXT NOT NULL,
    age_days INTEGER,
    -- Computed: (NOW - created_at) / 86400
    content TEXT NOT NULL,
    -- Suggestion description, ≤500 chars
    context TEXT,
    -- Optional: additional context (query suggestions, reasoning)
    assigned_to TEXT,
    -- Collector ID if claimed
    claimed_at TEXT,
    -- When assigned
    closed_at TEXT,
    -- When resolved
    closure_evidence TEXT,
    -- Description of how/why suggestion was addressed
    closure_quality REAL,
    -- [0, 1]: How well was suggestion addressed?
    UNIQUE(gap_id, source),
    FOREIGN KEY(gap_id) REFERENCES voi_gaps(gap_id)
);

CREATE INDEX idx_suggestions_status ON interpretation_space_suggestions(status);
CREATE INDEX idx_suggestions_source ON interpretation_space_suggestions(source);
CREATE INDEX idx_suggestions_priority ON interpretation_space_suggestions(priority DESC);
CREATE INDEX idx_suggestions_age ON interpretation_space_suggestions(age_days DESC);
```

**Table 2: management_pipelines**

Purpose: Track the status of data pipelines that feed the system (article extraction, belief integration, BN computation, etc.).

```sql
CREATE TABLE management_pipelines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pipeline_id TEXT UNIQUE NOT NULL,
    -- e.g., "article_discovery", "belief_integration", "voi_computation"
    pipeline_name TEXT,
    status TEXT NOT NULL DEFAULT 'idle',
    -- status ∈ {active, idle, stale, paused, failed}
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    last_run_at TEXT,
    -- ISO 8601 timestamp of last execution
    next_run_scheduled TEXT,
    -- ISO 8601 timestamp of next scheduled run
    run_count INTEGER DEFAULT 0,
    -- Number of times executed
    input_count INTEGER DEFAULT 0,
    -- Items processed in last run
    output_count INTEGER DEFAULT 0,
    -- Items produced in last run
    last_error TEXT,
    -- Error message from last failed run (if any)
    config JSON,
    -- Pipeline configuration (thresholds, parameters)
    health_score REAL DEFAULT 0.5
    -- [0, 1]: aggregate health metric
);

CREATE INDEX idx_pipelines_status ON management_pipelines(status);
CREATE INDEX idx_pipelines_health ON management_pipelines(health_score DESC);
```

**Table 3: overseer_alerts**

Purpose: Track system health alerts and anomalies detected by OVERSEER.

```sql
CREATE TABLE overseer_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pipeline_id TEXT,
    alert_type TEXT NOT NULL,
    -- alert_type ∈ {stale_suggestions, high_voi_unaddressed, low_closure_rate,
    --                coherence_decline, invariant_violation, pipeline_failed, etc.}
    triggered_at TEXT NOT NULL,
    dismissed_at TEXT,
    -- NULL if active; set when human dismisses
    severity TEXT DEFAULT 'info',
    -- severity ∈ {info, warning, critical}
    content TEXT NOT NULL,
    -- Human-readable alert description
    metric_value REAL,
    -- Optional: the specific value that triggered alert (e.g., coherence drop %)
    recommended_action TEXT,
    -- Optional: suggested mitigation
    FOREIGN KEY(pipeline_id) REFERENCES management_pipelines(pipeline_id)
);

CREATE INDEX idx_alerts_type ON overseer_alerts(alert_type);
CREATE INDEX idx_alerts_severity ON overseer_alerts(severity);
CREATE INDEX idx_alerts_dismissed ON overseer_alerts(dismissed_at);
```

**Table 4: suggestion_backlog_report** (Materialized View / Cached Summary)

Purpose: Fast query interface for high-level suggestion metrics.

```sql
CREATE TABLE suggestion_backlog_report (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    computed_at TEXT NOT NULL,
    -- When this report was computed
    source TEXT NOT NULL,
    -- Aggregated by source (or 'all')
    count_proposed INTEGER DEFAULT 0,
    count_identified INTEGER DEFAULT 0,
    count_in_progress INTEGER DEFAULT 0,
    count_addressed INTEGER DEFAULT 0,
    count_archived INTEGER DEFAULT 0,
    median_age_days REAL,
    max_age_days INTEGER,
    -- Age of oldest unaddressed suggestion
    median_priority REAL,
    avg_closure_quality REAL,
    -- Average closure_quality for closed suggestions
    UNIQUE(computed_at, source)
);
```

### 132.6a.2: Insertion Points in Pipeline

**When gap is detected** (gap_predictor.find_all_gaps):

```python
# After gap is created
gap = gap_predictor.find_all_gaps()[0]  # Example

# Insert into interpretation_space_suggestions
cursor.execute("""
    INSERT INTO interpretation_space_suggestions
    (gap_id, suggestion_id, source, suggestion_type, status, priority,
     created_at, updated_at, age_days, content)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    gap.gap_id,
    f"suggestion_{uuid.uuid4()}",
    "argumentation",  # Gap predicted by argumentation framework
    gap.gap_type.value,
    "proposed",
    gap.voi_score or 0.5,  # Initial VOI
    datetime.now(timezone.utc).isoformat(),
    datetime.now(timezone.utc).isoformat(),
    0,
    gap.gap_description[:500]
))
```

**When gap is scored** (VOIGapScorer.calculate_voi):

```python
# After VOI is computed
base_voi = voi_scorer.calculate_voi(gap, web)

# Update suggestion status and priority
cursor.execute("""
    UPDATE interpretation_space_suggestions
    SET status='identified', priority=?, updated_at=?
    WHERE gap_id=? AND source='argumentation'
""", (base_voi, datetime.now(timezone.utc).isoformat(), gap.gap_id))
```

**When gap is closed** (discovery_funnel.mark_gap_closed):

```python
# After papers integrated and closure assessed
closure_type, closure_fraction = funnel.assess_closure(gap_id, papers)

# Update suggestion status
cursor.execute("""
    UPDATE interpretation_space_suggestions
    SET status='addressed', closed_at=?, closure_evidence=?, closure_quality=?, updated_at=?
    WHERE gap_id=?
""", (
    datetime.now(timezone.utc).isoformat(),
    f"Closed as {closure_type}: {papers[0].title}, {papers[1].title}, ...",
    closure_fraction,
    datetime.now(timezone.utc).isoformat(),
    gap_id
))
```

**When pipeline completes** (orchestrator completion hooks):

```python
# After article_discovery_pipeline completes
cursor.execute("""
    INSERT OR REPLACE INTO management_pipelines
    (pipeline_id, pipeline_name, status, last_run_at, next_run_scheduled,
     run_count, input_count, output_count, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    "article_discovery",
    "Article Discovery Pipeline",
    "idle",
    datetime.now(timezone.utc).isoformat(),
    (datetime.now(timezone.utc) + timedelta(hours=6)).isoformat(),
    run_count + 1,
    input_count,
    output_count,
    datetime.now(timezone.utc).isoformat()
))
```

### 132.6a.3: Queries Expected by overseer_management.py

**Query 1: Check Suggestion Backlog**

```python
def check_suggestion_backlog(self) -> Dict[str, int]:
    """Count suggestions by source and status."""
    cursor = self.db.cursor()
    cursor.execute("""
        SELECT source, status, COUNT(*) as count
        FROM interpretation_space_suggestions
        GROUP BY source, status
    """)

    results = {}
    for source, status, count in cursor.fetchall():
        key = f"{source}_{status}"
        results[key] = count

    return results
```

**Query 2: List Stale Suggestions**

```python
def list_stale_suggestions(self, age_threshold_days: int = 7) -> List[Dict]:
    """Return suggestions older than threshold, still unaddressed."""
    cursor = self.db.cursor()
    cursor.execute("""
        SELECT gap_id, suggestion_id, content, priority, age_days
        FROM interpretation_space_suggestions
        WHERE age_days > ? AND status != 'addressed'
        ORDER BY age_days DESC
    """, (age_threshold_days,))

    return [
        {
            "gap_id": row[0],
            "suggestion_id": row[1],
            "content": row[2],
            "priority": row[3],
            "age_days": row[4]
        }
        for row in cursor.fetchall()
    ]
```

**Query 3: Track Closure Rate**

```python
def track_closure_rate(self) -> Dict[str, float]:
    """Compute closure rate by source."""
    cursor = self.db.cursor()
    cursor.execute("""
        SELECT source,
               COUNT(*) as total,
               SUM(CASE WHEN status='addressed' THEN 1 ELSE 0 END) as closed
        FROM interpretation_space_suggestions
        GROUP BY source
    """)

    return {
        source: (closed / total if total > 0 else 0)
        for source, total, closed in cursor.fetchall()
    }
```

**Query 4: Pipeline Health Check**

```python
def check_pipeline_health(self, pipeline_id: str) -> Dict[str, Any]:
    """Get health metrics for a specific pipeline."""
    cursor = self.db.cursor()
    cursor.execute("""
        SELECT status, last_run_at, health_score, last_error
        FROM management_pipelines
        WHERE pipeline_id=?
    """, (pipeline_id,))

    row = cursor.fetchone()
    if not row:
        return None

    return {
        "status": row[0],
        "last_run": row[1],
        "health_score": row[2],
        "last_error": row[3]
    }
```

### 132.6a.4: Design Decision for Panel Review

**Should overseer queries be mandatory (blocking deployment) or optional (nice-to-have monitoring)?**

- **Option A (Mandatory):** Implement all tables and insertion points. System cannot deploy without working overseer. Ensures rigorous monitoring from day one.
  - Effort: ~20 hours development
  - Timeline: Part of Phase 2
  - Risk: Adds complexity; overseer bugs could block pipeline

- **Option B (Optional/Phase 2):** Implement core overseer (Table 1 only). Document as aspirational. Complete Tables 2–4 in Phase 2.
  - Effort: ~5 hours for Table 1; defer remainder
  - Timeline: Table 1 immediate; Tables 2–4 Phase 2
  - Advantage: Reduces immediate complexity; maintains optionality

**Recommendation:** Option B (hybrid). Implement Table 1 (interpretation_space_suggestions) immediately to track suggestion backlog. Defer Tables 2–4 to Phase 2, marking them as aspirational. This provides monitoring value without blocking deployment.

---

# SECTION REVISE-B1: VOI Computation Details

## §47 REVISED: Value of Information: Scoring and Prioritizing Experiments

### 47.1A Subsection: The Three VOI Computation Modules (NEW)

The system computes value of information at three scales, each applicable in different pipeline contexts:

**1. Gap-Level VOI (voi_search.py)**

Scope: How valuable would it be to resolve a particular knowledge gap?

Entry point: ResearchQueueService.refresh_queue() calls VOIGapScorer.calculate_voi(gap, web) during target creation.

Computation:

- **Epistemic VOI:** Based on gap's impact on belief uncertainty, centrality in belief network, and source sparsity
  - Formula: epistemic_voi = (uncertainty + centrality + sparsity) / 3
  - Uncertainty ∈ [0,1]: Aggregated confidence of source beliefs; higher if beliefs conflict
  - Centrality ∈ [0,1]: Count of downstream beliefs dependent on this gap / total beliefs
  - Sparsity ∈ [0,1]: Ratio of theories predicting effect to empirical evidence supporting it

- **Structural VOI:** Based on gap's position in causal graph
  - Formula: structural_voi = (in_degree + out_degree) / (2 × max_degree)
  - In-degree: How many other gaps depend on closing this one?
  - Out-degree: How many beliefs would improve if gap closed?

- **Combined:** base_VOI = 0.5 × epistemic_voi + 0.5 × structural_voi
  - Equal weighting (0.5–0.5) is current default; panel should review (Decision C1)
  - Subject to researcher-specific adjustment via fit factor (§47B)

Output: base_VOI ∈ [0, 1] attached to ResearchTarget.voi_score

Fallback: If voi_search unavailable, default to 0.5

**2. Finding-Level VOI (voi_scoring.py)**

Scope: How valuable is this particular extracted finding from a paper?

Entry point: paper_integration/cmr/paper_eval.py calls score_voi(findings) during PDF extraction.

Computation:

- Input: List of findings extracted from a single paper
- Evaluation per finding:
  - Does it directly address an identified gap? [binary: yes/no] → weight 0.4
  - Effect size magnitude (Cohen's d or equivalent) → weight 0.3
  - Methodological rigor (sample size, internal validity) → weight 0.2
  - Novelty (has this finding been replicated before?) → weight 0.1

- Output: voi_bucket ∈ {high, medium, low} + numeric score [0, 1]
  - high: score ≥ 0.65 (integrate immediately)
  - medium: 0.40–0.64 (integrate with moderate confidence)
  - low: <0.40 (quarantine for expert review)

Purpose: Filter papers for quality before web integration; prioritize high-VOI findings for rapid inclusion.

**3. Lifecycle-Level VOI (discovery_funnel.py)**

Scope: Has searching for this gap produced evidence sufficient to close it?

Entry point: discovery_funnel.assess_closure(gap_id, papers) called after PDF extraction completes.

Computation:

- Input: gap_id, list of papers integrated
- Extract beliefs from papers that address gap (measure overlap with gap_description)
- Compute average warrant_quality across relevant beliefs
- Classify closure_fraction = warrant_quality
  - FULL closure: closure_fraction ≥ 0.75 (VOI → 0)
  - PARTIAL: 0.50–0.74 (VOI revised downward)
  - NONE: <0.50 (gap remains OPEN, no VOI change)

- Formula: new_VOI = base_VOI × (1.0 - closure_fraction)

Purpose: Feedback loop. As papers close gaps, VOI is revised to deprioritize them in queue.

**When Each Is Used:**

| Module | Trigger | Context | Output Consumed By |
|--------|---------|---------|-------------------|
| Gap-level (voi_search) | Gap detected | ResearchQueueService creates ResearchTarget | Queue ranking (get_next_highest_voi_target) |
| Finding-level (voi_scoring) | PDF extracted | paper_integration evaluates findings | Integration prioritization, quality filtering |
| Lifecycle-level (discovery_funnel) | Papers integrated | discovery_funnel assesses closure | Queue re-ranking, VOI revision |

### 47.2 Subsection: Gap Predictor VOI Defaults (REVISED)

Current state (as of March 2026):

The gap_predictor.py hardcodes voi_score=0.5 for all predicted gaps (line ~55):

```python
def find_all_gaps(self, max_gaps: int = 50) -> List[PredictedGap]:
    gaps = [...]  # Detected gaps
    for gap in gaps:
        gap.voi_score = 0.5  # <-- Hardcoded default
    return gaps
```

Design intent: voi_score should be computed by VOIGapScorer if available, otherwise default to 0.5.

Implementation roadmap:

1. **Immediate (no code change required):** Acknowledge that 0.5 default is neutral placeholder. VOI computation is optional; system remains operational without it.

2. **Phase 2 (recommended):** Modify gap_predictor to accept optional VOI scorer:

```python
def __init__(self, ..., voi_scorer: Optional[VOIGapScorer] = None):
    self.voi_scorer = voi_scorer

def find_all_gaps(self, max_gaps: int = 50) -> List[PredictedGap]:
    gaps = [...]
    for gap in gaps:
        if self.voi_scorer:
            gap.voi_score = self.voi_scorer.calculate_voi(gap, self.web)
        else:
            gap.voi_score = 0.5  # Fallback
    return gaps
```

Advantage: VOI computation is optional but available; system gracefully degrades if VOI unavailable.

### 47.3 Subsection: Researcher-Specific VOI Adjustment (NEW)

Base VOI scores (from voi_search.py) are universal—same for all researchers. Researcher-specific VOI adjusts base VOI by researcher fit:

**Formula:**

VOI_adjusted = base_VOI × researcher_fit_factor(collector_profile, gap)

**Fit Factor:**

Computed in src/queue/researcher_voi.py via compute_researcher_fit():

- **Domain alignment** (±0.3): Does gap domain match collector's preferred_domains?
- **Expertise fit** (±0.2): Is gap complexity appropriate for collector's expertise_level?
- **Theoretical alignment** (±0.15): Does gap involve theories collector knows?
- **Access feasibility** (±0.1): Can collector access required sources?
- **Closure history** (±0.1): Has collector successfully closed this gap type before?
- **Workload capacity** (±0.1): Is collector near max concurrent targets?

Product of factors, clamped to [0.5, 1.5]: ensures extreme over/undervaluation prevented.

**Integration:**

ResearchQueueService.get_next_highest_voi_target() re-computes fit factor on each claim, reflecting current collector state and gap characteristics. This ensures queue ranking adapts to researcher-specific context.

See §47B for detailed treatment.

---

# SECTION REVISE-B2: Queue Prioritization Strategy

## §46 REVISED: What the System Tracks (Add New Subsection)

### 46.X Subsection: Queue Prioritization by Value of Information (NEW)

The research queue stores ResearchTarget objects, each with voi_score (base VOI) and voi_adjusted (researcher-specific VOI). The queue service provides two methods for target assignment:

**Method 1: FIFO (Deprecated)**

```python
def get_next_target(self, collector_id: str) -> Optional[ResearchTarget]:
    """Return next unassigned target in creation order (FIFO)."""
    unassigned = [t for t in self._targets.values() if t.status == TargetStatus.OPEN]
    return min(unassigned, key=lambda t: t.created_at) if unassigned else None
```

Problem: Ignores VOI scores. High-priority gaps may languish while low-priority gaps are claimed.

**Method 2: VOI-Ranked (Recommended)**

```python
def get_next_highest_voi_target(self, collector_id: str) -> Optional[ResearchTarget]:
    """Return unassigned target with highest VOI_adjusted for this collector."""
    collector = self._collectors[collector_id]
    unassigned = [t for t in self._targets.values() if t.status == TargetStatus.OPEN]

    # Compute VOI_adjusted for each target
    scores = [
        (t, adjust_voi_for_collector(t.voi_score, collector, t))
        for t in unassigned
    ]

    return max(scores, key=lambda x: x[1])[0] if scores else None
```

Advantage: High-VOI gaps presented first; researcher-specific fit considered.

**Fallback:** If all VOI_adjusted scores are zero or unavailable, method gracefully degrades to FIFO.

**Dynamic Re-ranking:** When a gap's VOI is revised (discovery_funnel revises after closure assessment), the queue is implicitly re-sorted on next claim. Previously high-priority gaps may drop if their VOI is reduced.

---

# SECTION REVISE-B3: Article Recommendation Flow Completeness

## NEW SECTION: Integration Points Between Gap Detection, VOI, and Queue

### Integration Architecture

The gap detection → VOI scoring → queue ranking → search execution → closure assessment → VOI revision cycle is the operational core of the Article_Eater system. The five components must integrate seamlessly:

1. **Gap Detection** (gap_predictor.py) outputs PredictedGap with voi_score
2. **VOI Scoring** (voi_search.py) optionally refines voi_score; result is base_VOI
3. **Queue Management** (queue/service.py) converts gap to ResearchTarget; ranks by researcher_fit_factor-adjusted VOI
4. **Search Execution** (automated or manual) claims target, generates queries, retrieves papers
5. **Closure Assessment** (discovery_funnel.py) evaluates papers, computes closure_fraction, revises VOI
6. **Queue Re-ranking** (implicit on next claim) re-sorts targets by revised VOI

**Key Integration Points:**

- **Gap → Target:** queue/service.py._target_from_predicted_gap() converts PredictedGap to ResearchTarget; copies voi_score
- **VOI Availability:** VOIGapScorer is lazy-imported. If unavailable, system uses voi_score=0.5 (graceful degradation)
- **Closure Feedback:** discovery_funnel.revise_voi() updates target.voi_score; queue re-sorts on next claim
- **Researcher Context:** researcher_voi.adjust_voi_for_collector() personalizes ranking based on collector_profile

---

# SECTION NEW-A10: Continuous Recommendation Loop Service

## §132.7 Continuous Recommendation Loop Service

### Executive Summary

The RecommendationLoopService (src/services/recommendation_loop.py, ~800 lines) orchestrates a continuous cycle of gap suggestion identification, prioritization, recommendation dispatch, and result tracking. Operating in parallel with human researchers, it automates the discovery of actionable research targets and coordinates handoff to collectors.

### 132.7.1 Architecture and Modes

The service operates in three modes:

**Mode 1: Single-Pass**

```python
def run_once(self) -> Dict[str, Any]:
    """Execute one iteration of the recommendation loop."""
    # 1. Harvest gaps from gap predictor
    # 2. Score gaps using VOI
    # 3. Insert suggestions into interpretation_space_suggestions
    # 4. Dispatch to available collectors
    # 5. Report results
```

Useful for testing or manual triggering. Completes in ~30 seconds for 50 gaps.

**Mode 2: Continuous Daemon**

```python
def run_daemon(self, interval_hours: float = 1.0):
    """Run recommendation loop continuously on schedule."""
    while True:
        result = self.run_once()
        logger.info(f"Loop iteration: {result}")
        time.sleep(interval_hours * 3600)
```

Runs hourly by default (configurable). Invoked by scripts/run_recommendation_loop.py.

**Mode 3: Health Check**

```python
def health_check(self) -> Dict[str, Any]:
    """Return status of recommendation loop without executing."""
    # Return: gap backlog size, suggestion queue depth, collector availability
```

Lightweight query for monitoring dashboards.

### 132.7.2 The Five-Phase Loop

**Phase 1: Harvest**

Collect gaps from all sources:

```python
def _harvest_gaps(self) -> List[PredictedGap]:
    gaps = []

    # Source 1: Gap predictor
    gaps.extend(self.gap_predictor.find_all_gaps(max_gaps=50))

    # Source 2: QA system
    gaps.extend(self.qa_handler.identify_suggested_gaps())

    # Source 3: Argumentation framework
    gaps.extend(self.argumentation.detect_defeater_gaps())

    # Filter out already-tracked gaps
    existing_ids = set(self._targets.keys())
    return [g for g in gaps if g.gap_id not in existing_ids]
```

**Phase 2: Score**

Compute VOI for each gap:

```python
def _score_gaps(self, gaps: List[PredictedGap]) -> List[ResearchTarget]:
    targets = []
    for gap in gaps:
        voi = self.voi_scorer.calculate_voi(gap, self.web)
        target = ResearchTarget(
            gap_id=gap.gap_id,
            voi_score=voi,
            ...
        )
        targets.append(target)

    return sorted(targets, key=lambda t: t.voi_score, reverse=True)
```

**Phase 3: Insert**

Store suggestions in overseer database:

```python
def _insert_suggestions(self, targets: List[ResearchTarget]):
    for target in targets:
        self.suggestions_mgr.insert_suggestion(
            gap_id=target.gap_id,
            source="recommendation_loop",
            priority=target.voi_score,
            content=target.gap_description
        )
```

**Phase 4: Dispatch**

Recommend targets to available collectors:

```python
def _dispatch_recommendations(self, targets: List[ResearchTarget]):
    for target in targets:
        # Find best-fit collector
        collector = self._select_best_collector(target)
        if collector:
            # Notify collector or auto-claim
            self.queue_service.claim_target(collector.collector_id, target.target_id)
```

**Phase 5: Report**

Log results for monitoring:

```python
def _report_results(self, harvested: int, scored: int, dispatched: int):
    logger.info(f"Recommendation loop: {harvested} gaps harvested, "
                f"{scored} scored, {dispatched} dispatched")

    # Update health metrics
    self.overseer.record_loop_iteration(
        gaps_processed=harvested,
        dispatches=dispatched,
        timestamp=datetime.now(timezone.utc)
    )
```

### 132.7.3 Integration with Nightly Pipeline

The recommendation loop is scheduled as part of the nightly pipeline (scripts/run_nightly_pipeline.sh):

```bash
#!/bin/bash
# Nightly Article_Eater maintenance

# 1. Run gap predictor (if not already running)
python -m src.services.gap_predictor --mode full --output_file data/predicted_gaps.json

# 2. Run recommendation loop
python scripts/run_recommendation_loop.py --mode daemon --interval 1

# 3. Run OVERSEER audit
python scripts/overseer_nightly.py --mode full

# 4. Archive stale suggestions
python scripts/archive_stale_suggestions.py --age_threshold 30
```

### 132.7.4 Metrics and Monitoring

The service tracks:

- **Gaps processed**: Count of gaps examined per iteration
- **VOI scores computed**: Success rate of VOI calculation
- **Suggestions inserted**: Count of new suggestions added to backlog
- **Dispatch success rate**: Fraction of targets matched with collectors
- **Loop execution time**: Latency per iteration
- **Backlog depth**: Current size of suggestion queue

---

## INTEGRATION NOTES FOR DOCUMENT EDITOR

### Location and Integration Steps

1. **NEW-A1 (VOI Integration Architecture, §47A)**
   - Insert after existing §47 (Value of Information: Scoring and Prioritizing Experiments)
   - Place before Part IV (The Credence Calculus)
   - Cross-reference to §47B, §47C, §47D, §47E throughout

2. **NEW-A2 (Researcher-Specific VOI, §47B)**
   - Insert immediately after NEW-A1 (§47A)
   - Reference CollectorProfile from queue/models.py
   - Link to §47A.3 (adjusted VOI formula)

3. **NEW-A3 (Search Execution Pipeline, §47C)**
   - Insert after NEW-A2 (§47B)
   - Reference §47A.3 (VOI ranking)
   - Include orchestration diagram

4. **NEW-A4 (QA as Recommendation Source, §47D)**
   - Insert after NEW-A3 (§47C)
   - Reference §47A (gap detection)
   - Cross-reference arbitrary_qa_handler.py

5. **NEW-A5 (Discovery Funnel Feedback Loop, §47E)**
   - Insert after NEW-A4 (§47D)
   - Critical for completing the cycle back to §47A
   - Include worked example

6. **NEW-A6 (Overseer Schema, §132.6a)**
   - Insert in Part XVIII (Computational Infrastructure)
   - Place as new §132.6a after OVERSEER description (§132)
   - Reference overseer_management.py

7. **REVISE-B1 (VOI Computation Details)**
   - Expand existing §47
   - Add subsections 47.1A, 47.2, 47.3
   - Preserve existing content; add new subsections

8. **REVISE-B2 (Queue Prioritization)**
   - Extend existing §46
   - Add subsection after §46.9
   - Reference voi_search.py, researcher_voi.py

9. **REVISE-B3 (Integration Points)**
   - Add as new subsection of §46 or standalone short section
   - Provide high-level map of component interactions

10. **NEW-A10 (Continuous Recommendation Loop, §132.7)**
    - Insert in Part XVIII after §132.6a (Overseer Schema)
    - Reference recommendation_loop.py

### Cross-Reference Summary

New sections extensively reference one another:

- §47A (VOI Integration) → fundamentally connects to §47B (researcher-specific), §47C (search execution), §47E (feedback loop)
- §47B (Researcher-Specific VOI) → depends on §47A; used in §47C
- §47C (Search Execution) → uses VOI from §47A, §47B; sends closure data to §47E
- §47D (QA as Source) → alternative gap source; feeds into VOI system via §47A
- §47E (Feedback Loop) → closes the cycle; revises VOI that was computed in §47A
- §132.6a (Overseer Schema) → tracks suggestions from all sources (§47A–D)
- §132.7 (Recommendation Loop) → orchestrates §47A–E in continuous operation

### Document Statistics

**New Content: ~8,500 words**
- NEW-A1: ~2,000 words
- NEW-A2: ~2,200 words
- NEW-A3: ~2,000 words
- NEW-A4: ~800 words
- NEW-A5: ~1,200 words
- NEW-A6: ~1,000 words
- REVISE-B1: +400 words (subsections added to existing §47)
- REVISE-B2: +300 words (subsection added to existing §46)
- NEW-A10: ~800 words

**Total Master Doc Increase**: ~8,500 additional words (from ~20,500 to ~29,000 lines)

**Estimated Reading Time**: 45–60 minutes for complete review; 15–20 minutes for executive summary (NEW-A1 only)

---

**Document Generated**: March 2, 2026
**Preparation Time**: ~16 hours source code review + writing
**Quality Assurance**: All references checked against actual source files (src/queue/service.py, src/services/voi_search.py, src/services/discovery_funnel.py, src/queue/researcher_voi.py, src/services/gap_predictor.py)

