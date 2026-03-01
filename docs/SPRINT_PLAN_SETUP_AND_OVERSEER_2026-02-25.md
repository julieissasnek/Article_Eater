# Article Eater PostQuinean v1: Sprint Plan
## SETUP FUNCTION & OVERSEER IMPLEMENTATION
### February 25 – March 2, 2026

**Status**: READY FOR EXECUTION
**Scope**: 6 concurrent sprints consolidating system initialization, monitoring, and calibration
**Estimated Duration**: ~18 hours engineering + ~6 hours expert panel calibration
**Approval Authority**: Professor David Kirsh, UCSD Cognitive Science

---

## Executive Summary

This sprint plan codifies the 18-person expert panel's recommendations (O-1 through O-8) into an operational development pipeline. The plan coordinates **six sequential sprints** that transition Article Eater from *eagerly wired* (Session 7) to *fully initialized and monitored* (OPERATIONAL state). Each sprint includes:

1. Concrete engineering tasks with estimated LOC
2. Dependencies and test coverage
3. Decision tracking (with panel rationale)
4. Risk assessment and mitigation
5. Integration points with existing services

The plan assumes:
- **~850 papers** already extracted via Gemini pipeline
- **~100 extraction JSONs** in data/extractions/
- **208 templates** (103 calibrated, 79 scaffold) with full field coverage
- **14 T1.5 theories** formally reduced, ready for integration
- **27/27 integration pipeline tests** passing (eager wiring complete)
- **No external dependencies** on BN_graphical (independent deployment path)

---

## System State Diagram

```
UNINITIALIZED
    ↓
  setup() invoked
    ↓
INITIALIZING (12-phase execution, non-blocking)
    ├─ Phase 0: Metadata enrichment
    ├─ Phase 1: Scaffold & theory setup
    ├─ Phase 2: Bulk load extractions
    ├─ Phase 3: Batch provenance construction
    ├─ Phase 4: Batch web insertion
    ├─ Phase 5: Global reflective equilibrium (convergence loop)
    ├─ Phase 6: BN structure learning
    ├─ Phase 7: BN parameterization
    ├─ Phase 8: Global coherence baseline
    ├─ Phase 9: Batch QA cache generation
    ├─ Phase 10: Social epistemology baseline
    ├─ Phase 11: VOI gap initialization
    └─ Phase 12: OVERSEER baseline snapshot
    ↓
  OPERATIONAL (Dijkstra invariant established)
    ├─ POST_INTEGRATION checks (5–10 sec per paper)
    ├─ PERIODIC audits (nightly, 5–15 min)
    └─ ALERT handlers (< 1 sec on threshold violation)
```

**Invariant INV-0 (Dijkstra)**: System enters OPERATIONAL state only after:
- All 850 papers integrated
- Global reflective equilibrium converged (coherence delta < 0.001)
- OVERSEER baseline snapshot created and verified

---

## Sprint 0: METADATA ENRICHMENT
**Target Date**: 2026-02-25 (today)
**Duration**: ~30 minutes
**Owner**: Claude Code

### Objective
Enrich ~850 extracted papers with Semantic Scholar metadata (publication dates, citation counts, author affiliations). This establishes temporal ordering and citation topology before bulk system initialization.

### Tasks

| Task | Command | Expected Output | Acceptance Criterion |
|------|---------|-----------------|----------------------|
| Repair metadata for existing extractions | `python scripts/semantic_scholar_enrichment.py --repair` | ENRICHED_COUNT, FAILED_COUNT | ≥ 95% coverage (≥ 808/850) |
| Repair batch extraction metadata | `python scripts/semantic_scholar_enrichment.py --repair-batches` | BATCH_ENRICHED_COUNT | ≥ 90% batch coverage |
| Build citation graph | `python scripts/semantic_scholar_enrichment.py --build-graph` | citation_graph.json (DAG of papers) | Valid JSON; no cycles; ≥ 500 edges |
| Verify graph statistics | Python inspection | edge_count, citation_density, temporal_span | Node count = enriched count ± 5% |

### Dependencies
- `scripts/semantic_scholar_enrichment.py` (existing, Session 7)
- Semantic Scholar API key in `.env`
- ~850 extraction JSON files in data/extractions/

### Testing
```bash
# Unit: Validate citation_graph.json structure
pytest tests/test_metadata_enrichment.py -v

# Integration: Confirm all papers have publication_year
python scripts/verify_citation_graph.py --check-temporal
```

### Files to Modify/Create
- Create: `data/metadata/citation_graph.json`
- Modify: `src/services/paper_integration/orchestrator.py` (add Phase 0 hook)

### Key Decision: D0.1 — Citation Graph Sparsity
- **Context**: Not all 850 papers will be cited by others (esp. recent ones)
- **Options**:
  - A) Include isolated nodes (citation-neutral papers)
  - B) Filter to papers with ≥ 1 citation (temporal cohesion)
  - C) Augment with co-author graph (less direct than citation)
- **Rationale**: Select **Option A** — isolated papers are still temporally ordered; argument reconstruction doesn't require citation links
- **Risk**: Low (metadata only; no integration impact)
- **Panelist Concern**: Cartwright (citation clustering may hide methodological homogeneity; monitor)

### Output
- `data/metadata/citation_graph.json` (enriched, 850 nodes, citation topology)
- `data/metadata/temporal_ordering.json` (papers sorted by publication_year)
- Metadata enrichment report: `docs/METADATA_ENRICHMENT_REPORT_2026-02-25.txt`

---

## Sprint 1: SETUP FUNCTION
**Target Date**: 2026-02-25 → 2026-02-26
**Duration**: ~4 hours
**Owner**: Claude Code
**Dependencies**: Sprint 0 (citation_graph.json)

### Objective
Implement `SystemSetup` class with 12-phase initialization pipeline. This function transitions the system from UNINITIALIZED → OPERATIONAL in one coherent operation, establishing baselines for health monitoring, coherence detection, and expert calibration.

### Architecture

**File**: `src/services/system_setup.py`

**Main Classes**:
```python
class SystemSetup:
    """12-phase initialization pipeline."""

    async def setup(self) -> SetupResult:
        """Primary initialization. Non-blocking."""

    async def re_setup(self) -> SetupResult:
        """Archive current state, re-initialize, preserve manual overrides."""

    def _verify_invariants(self) -> bool:
        """Dijkstra invariant check (INV-0)."""
```

**SetupResult Dataclass**:
```python
@dataclass
class SetupResult:
    status: Literal["SUCCESS", "PARTIAL", "FAILED"]
    phases_completed: int  # 0–12
    phase_timings: dict  # e.g., {"Phase 0": 0.3, "Phase 5": 45.2}
    convergence_achieved: bool
    coherence_delta: float  # Pre/post difference (Phase 8)
    papers_integrated: int
    beliefs_created: int
    bn_nodes: int
    bn_edges: int
    errors: list[dict]  # Phase-level failures
    baseline_snapshot_id: str  # UUID for OVERSEER reference
```

### 12-Phase Breakdown

#### Phase 0: Metadata Enrichment (5 min)
**Idempotent**: Runs if any paper unenriched.

```python
async def _phase_0_metadata(self) -> PhaseResult:
    """Ensure all 850 papers have temporal + citation metadata."""
    await enrichment_service.repair_metadata()
    citation_graph = await enrichment_service.build_graph()
    return PhaseResult(
        phase=0,
        records_processed=len(citation_graph['nodes']),
        errors=[]
    )
```

**Acceptance**: ≥ 95% papers enriched; citation_graph.json valid.

---

#### Phase 1: Scaffold & Theory Setup (10 min)
**Idempotent**: Verifies theory/construct/template hierarchy exists.

```python
async def _phase_1_scaffold(self) -> PhaseResult:
    """Create/verify 14 T1.5 theories, 8 T1 frameworks, 208 templates."""
    theories = await theory_service.list_all()
    missing_theories = [t for t in CANONICAL_T1_5_ROSTER if t not in theories]
    if missing_theories:
        await theory_service.bulk_create(missing_theories)

    constructs = await construct_service.verify_hierarchy()
    templates = await template_service.verify_scaffold_attachment()

    return PhaseResult(
        phase=1,
        theories_created=len(missing_theories),
        constructs_verified=len(constructs),
        templates_scaffold_verified=208,
        errors=[]
    )
```

**Acceptance**: All 14 T1.5 theories present; 208 templates attached; 79 scaffold templates verified.

---

#### Phase 2: Bulk Load Extractions (15 min)
**Idempotent**: Stages all ~850 extractions; detects duplicates.

```python
async def _phase_2_bulk_load(self) -> PhaseResult:
    """Load all extractions from data/extractions/ into staging."""
    extraction_files = glob.glob("data/extractions/extraction_*.json")
    papers = []
    duplicates = set()

    for filepath in extraction_files:
        data = json.load(open(filepath))
        if data['paper_id'] in [p['paper_id'] for p in papers]:
            duplicates.add(data['paper_id'])
        else:
            papers.append(data)

    # Sort by publication_year (temporal ordering)
    papers.sort(key=lambda p: p.get('metadata', {}).get('publication_year', 9999))

    for paper in papers:
        await staging_service.stage_paper(paper)

    return PhaseResult(
        phase=2,
        papers_staged=len(papers),
        duplicates_detected=len(duplicates),
        errors=[{"type": "duplicate", "count": len(duplicates)}] if duplicates else []
    )
```

**Acceptance**: ≥ 800 unique papers staged; temporal ordering verified.

---

#### Phase 3: Batch Provenance Construction (30 min)
**Haack Foundherentism**: Construct Provenance objects synchronously.

```python
async def _phase_3_batch_provenance(self) -> PhaseResult:
    """For each staged paper, build full Provenance objects."""
    papers = await staging_service.list_papers()
    provenance_count = 0

    # Parallel batch processing (max 10 concurrent)
    async for paper in batch_async(papers, batch_size=10):
        # Per paper: extract all findings, map to claims
        findings = paper['findings']  # From Gemini extraction

        for finding in findings:
            provenance = Provenance(
                belief_id=finding['claim_id'],
                paper_id=paper['paper_id'],
                source_type=finding.get('study_type', 'Unknown').map_to_source(),
                study_type=finding['study_design'].map_to_study_type(),
                # E.g., "RCT" → StudyType.EXPERIMENTAL
                directness=finding['measurement_method'].map_to_directness(),
                # E.g., cortisol sensor → DIRECT; self-report → PROXY
                grounding_chain=find_grounding_chain(finding),  # Lazy computation
                justification_status=compute_justification_status(finding)
                # FOUNDATIONAL, COHERENT_ONLY, DEFEATED, AMBIGUOUS
            )
            await belief_provenance_service.persist(provenance)
            provenance_count += 1

    return PhaseResult(
        phase=3,
        provenances_created=provenance_count,
        errors=[]
    )
```

**Acceptance**: ≥ 2,000 Provenance objects created; justification_status computed for each.

**Panel Rationale** (O-5): Haack requires synchronous provenance computation (not deferred). Grounding chains are lazy (computed on demand, cached).

---

#### Phase 4: Batch Web Insertion (45 min)
**Credence Computation**: Full Quinean integration—theory inference, reflective equilibrium, provenance coupling.

```python
async def _phase_4_batch_web_insertion(self) -> PhaseResult:
    """Insert all beliefs into web_of_belief with full credence computation."""
    papers = await staging_service.list_papers()
    beliefs_created = 0

    for paper in papers:
        findings = paper['findings']

        for finding in findings:
            # Full credence pipeline:
            # 1. Base credence from extraction
            base_credence = finding['ae_confidence']

            # 2. Theory inference (diminishing returns formula)
            theories = finding['theory_links']  # From Panel 6 extraction
            if len(theories) > 1:
                credence = 1.0
                for theory in theories:
                    credence = 1 - (1 - credence) * (1 - base_credence * 0.5)
            else:
                credence = base_credence

            # 3. Mechanistic entrenchment boost (Spohn-grounded)
            if is_mechanistically_grounded(finding, theories):
                credence += 0.15  # Derived from entrenchment theory

            # 4. Accumulate into web (DerSimonian-Laird meta-analytic)
            credence = await web_persistence.accumulate_belief(
                belief_type=finding['claim_type'],
                credence=credence,
                provenance=provenances[finding['claim_id']],
                paper_id=paper['paper_id']
            )

            beliefs_created += 1

    return PhaseResult(
        phase=4,
        beliefs_created=beliefs_created,
        errors=[]
    )
```

**Acceptance**: ≥ 2,000 beliefs inserted; credences in [0, 1]; no NaN/Inf values.

**Panel Rationale** (O-1, A): Quine + Haack + DerSimonian consensus—full pipeline required (not stub).

---

#### Phase 5: Global Reflective Equilibrium (120 min)
**Convergence Loop**: Iterate until coherence delta < 0.001 (not fixed 5 iterations).

```python
async def _phase_5_reflective_equilibrium(self) -> PhaseResult:
    """Iterate web beliefs to mutual support equilibrium (Quinean holism)."""
    max_iterations = 20  # Safety bound
    convergence_threshold = 0.001
    iteration = 0
    prev_coherence = None

    while iteration < max_iterations:
        # Round: allow each belief to update based on coherence with others
        for belief in await web_of_belief.list_all():
            # Compute neighbors (theories, constructs, related beliefs)
            neighbors = await web_of_belief.find_coherent_neighborhood(belief)

            # Adjust credence via reflective equilibrium
            new_credence = compute_equilibrium_credence(belief, neighbors)
            await web_of_belief.update_credence(belief, new_credence)

        # Check convergence
        coherence = await coherence_manager.compute_global_coherence()
        iteration += 1

        if prev_coherence is not None:
            delta = abs(coherence - prev_coherence)
            if delta < convergence_threshold:
                return PhaseResult(
                    phase=5,
                    iterations_completed=iteration,
                    converged=True,
                    final_coherence=coherence,
                    coherence_delta=delta,
                    errors=[]
                )

        prev_coherence = coherence

    # Max iterations reached without convergence
    return PhaseResult(
        phase=5,
        iterations_completed=iteration,
        converged=False,  # Log as warning, continue
        final_coherence=coherence,
        coherence_delta=delta,
        errors=[{"type": "no_convergence", "threshold": convergence_threshold}]
    )
```

**Acceptance**: Converged (delta < 0.001) OR partial (max iterations, delta < 0.05).

**Panel Rationale** (O-H): Reflective equilibrium and coherence are compatible; measure pre/post to capture integration dynamics.

**Risk**: Medium — may loop if coherence landscape is non-convex. Mitigation: Safety bound + partial acceptance.

---

#### Phase 6: BN Structure Learning (20 min)
**Causal DAG Inference**: Learn constraint-based BN structure from extracted rules + coherence.

```python
async def _phase_6_bn_structure(self) -> PhaseResult:
    """Induce BN structure from constraints + coherence relationships."""
    constraints = await constraint_service.list_all()  # From extractions
    coherence_pairs = await coherence_manager.find_correlated_beliefs()

    # Convert to skeleton: undirected graph
    skeleton = {}
    for constraint in constraints:
        iv, dv = constraint['iv'], constraint['dv']
        skeleton.setdefault(iv, set()).add(dv)

    # PC algorithm: conditional independence tests to orient edges
    dag, separating_sets = pc_algorithm(skeleton, coherence_pairs)

    # Persist structure
    await bn_service.set_structure(dag)

    return PhaseResult(
        phase=6,
        bn_nodes=len(dag),
        bn_edges=sum(len(neighbors) for neighbors in dag.values()),
        errors=[]
    )
```

**Acceptance**: Valid DAG (no cycles); ≥ 50 edges; no isolated variables.

**Panel Rationale** (O-4): Pearl's recommendation—constraint-based structure learning respects causal assumptions.

---

#### Phase 7: BN Parameterization (30 min)
**Edge Weight Computation**: Map web credences → Beta edge parameters (hierarchical coupling).

```python
async def _phase_7_bn_parameterization(self) -> PhaseResult:
    """Update BetaBernoulliEdge parameters from web credences."""
    edges = await bn_service.list_edges()
    updated_count = 0

    for edge in edges:
        source, target = edge['source'], edge['target']

        # Compute support direction + quality weight
        support_beliefs = await web_of_belief.find_beliefs(
            f"({source} → {target})"
        )

        quality_weight = compute_quality_weight(
            support_beliefs,
            papers=True,  # From paper quality
            coherence=True  # From coherence score
        )

        # Update Beta parameters (conjugate prior update)
        edge.update(
            supports=True,
            weight=quality_weight,
            evidence_type=infer_evidence_type(support_beliefs)
        )

        # Persist: α' = α + weight, β' = β + (1 - weight)
        await bn_service.persist_edge(edge)
        updated_count += 1

    return PhaseResult(
        phase=7,
        edges_parameterized=updated_count,
        errors=[]
    )
```

**Acceptance**: All edges have β-updated parameters; α ≥ 1, β ≥ 1.

**Panel Rationale** (O-4): Hierarchical coupling (web → BN priors, no feedback) selected by panel consensus (Pearl, Cartwright, Good).

---

#### Phase 8: Global Coherence Baseline (10 min)
**Reference Metric**: Compute full-system coherence; becomes OVERSEER baseline for alert thresholds.

```python
async def _phase_8_coherence_baseline(self) -> PhaseResult:
    """Compute global coherence pre/post reflective equilibrium."""
    coherence = await coherence_manager.compute_global_coherence()

    # Per-theory coherence (Cartwright multi-metric)
    per_theory = {}
    for theory in await theory_service.list_all():
        per_theory[theory.id] = await coherence_manager.compute_per_theory(theory)

    # Conflict rate
    conflicts = await web_of_belief.detect_conflicts()
    conflict_rate = len(conflicts) / (beliefs_count + 1)

    baseline = SystemCoherenceBaseline(
        global_coherence=coherence,
        per_theory_coherence=per_theory,
        conflict_rate=conflict_rate,
        timestamp=datetime.now()
    )

    await overseer_service.persist_baseline(baseline)

    return PhaseResult(
        phase=8,
        global_coherence=coherence,
        per_theory_coherence=per_theory,
        conflict_rate=conflict_rate,
        baseline_recorded=True,
        errors=[]
    )
```

**Acceptance**: Coherence ∈ [0, 1]; per-theory scores recorded; baseline persisted.

**Panel Rationale** (O-2): Cartwright's multi-metric approach—global + per-theory + conflict rate establishes thresholds for alerts.

---

#### Phase 9: Batch QA Cache Generation (40 min)
**Single LLM Batch Operation**: Generate cached QA answers for all "molecules" (belief clusters).

```python
async def _phase_9_qa_cache(self) -> PhaseResult:
    """Batch recompute QA caches for all belief molecules."""
    molecules = await molecule_service.list_all()

    # Batch LLM call (e.g., Claude Batch API)
    batch_requests = [
        QACacheRequest(
            molecule_id=mol['id'],
            question=f"What does {mol['theory']} say about {mol['construct']}?",
            context=mol['beliefs']
        )
        for mol in molecules
    ]

    results = await llm_service.batch_qa_request(batch_requests)

    # Persist cached answers + mark FRESH
    cache_count = 0
    for result in results:
        await qa_cache_service.set_fresh(
            molecule_id=result.molecule_id,
            answer=result.answer,
            timestamp=datetime.now()
        )
        cache_count += 1

    return PhaseResult(
        phase=9,
        caches_generated=cache_count,
        errors=[]
    )
```

**Acceptance**: ≥ 500 cache entries; all marked FRESH; no stale entries.

**Panel Rationale** (O-6): Batched (nightly) strategy balances cost/freshness. Initial setup uses single eager batch.

---

#### Phase 10: Social Epistemology Baseline (15 min)
**Community Identification**: Detect co-author + citation clusters; compute consensus credences.

```python
async def _phase_10_social_epistemology(self) -> PhaseResult:
    """Identify research communities; compute community-relative credences."""
    papers = await paper_service.list_all()

    # Co-authorship graph + citation clustering
    communities = community_detection(
        papers,
        edge_type='coauthor'  # Or 'citation'
    )

    for community in communities:
        registry_entry = CommunityRegistry(
            community_id=uuid.uuid4(),
            member_ids=[p['author_id'] for p in community['members']],
            consensus_credence=compute_consensus(community),
            monoculture_risk=assess_methodological_homogeneity(community)
        )
        await social_epistemology_service.persist(registry_entry)

    return PhaseResult(
        phase=10,
        communities_identified=len(communities),
        avg_community_size=np.mean([len(c['members']) for c in communities]),
        errors=[]
    )
```

**Acceptance**: ≥ 10 communities detected; consensus credences computed; monoculture risk assessed.

**Panel Rationale** (O-F): Surface contestation explicitly; Haack requires awareness of community disagreements.

---

#### Phase 11: VOI Gap Initialization (10 min)
**Discovery Funnel Seeding**: Identify known gaps; compute initial gap closure estimates.

```python
async def _phase_11_voi_gaps(self) -> PhaseResult:
    """Seed discovery funnel with high-VOI questions."""
    # Expert panel identifies priority gaps (domain-specific)
    gaps = await discovery_funnel_service.identify_gaps()

    for gap in gaps:
        voi = compute_voi(gap)  # Informativeness vs. formal VOI
        closure = GapClosure(
            gap_id=gap['id'],
            voi=voi,
            closure_probability=estimate_closure_rate(gap)
        )
        await discovery_funnel_service.persist(closure)

    return PhaseResult(
        phase=11,
        gaps_identified=len(gaps),
        high_voi_gaps=len([g for g in gaps if g.voi > 0.7]),
        errors=[]
    )
```

**Acceptance**: ≥ 20 gaps identified; VOI scores computed; closure rates estimated.

**Panel Rationale** (O-G): Expert panel to define high-VOI questions; discovery funnel initially empty until manual calibration.

---

#### Phase 12: OVERSEER Baseline Snapshot (5 min)
**System Readiness Certification**: Create baseline snapshot; record INV-0 verification.

```python
async def _phase_12_overseer_snapshot(self) -> PhaseResult:
    """Create OVERSEER baseline snapshot; certify OPERATIONAL state."""
    snapshot = OverseerSnapshot(
        id=uuid.uuid4(),
        timestamp=datetime.now(),
        system_state={
            'papers_integrated': papers_count,
            'beliefs_created': beliefs_count,
            'bn_structure': bn_structure,
            'global_coherence': baseline_coherence,
            'per_theory_coherence': per_theory_coherence,
            'conflict_rate': conflict_rate,
            'cache_freshness': 1.0  # All just generated
        },
        dijkstra_invariant_verified=True
    )

    await overseer_service.persist_snapshot(snapshot)

    return PhaseResult(
        phase=12,
        snapshot_id=snapshot.id,
        invariant_verified=True,
        errors=[]
    )
```

**Acceptance**: Snapshot persisted; INV-0 verified; system transition to OPERATIONAL.

---

### Overall Phase Testing

**Test Suite**: `tests/test_system_setup.py`

```python
class TestSystemSetup:
    async def test_setup_completes(self, system_setup):
        result = await system_setup.setup()
        assert result.status == "SUCCESS"
        assert result.phases_completed == 12

    async def test_phase_5_convergence(self, system_setup):
        """Verify reflective equilibrium reaches < 0.001 delta."""
        result = await system_setup._phase_5_reflective_equilibrium()
        assert result.converged or result.coherence_delta < 0.05

    async def test_invariant_verification(self, system_setup):
        """Dijkstra invariant: coherence decline ≤ 5%."""
        pre_coherence = initial_state.coherence
        result = await system_setup.setup()
        post_coherence = result.coherence_delta
        assert (1 - post_coherence / pre_coherence) <= 0.05
```

### Re-initialization (`re_setup()`)

```python
async def re_setup(self) -> SetupResult:
    """Archive current state, re-initialize, preserve overrides."""
    # 1. Archive current beliefs, BN, etc.
    archive = await archival_service.create_archive()

    # 2. Mark any manually-curated beliefs as DO_NOT_REVISE
    overrides = await override_service.list_all()

    # 3. Re-run 12 phases (full reset except overrides)
    result = await self.setup()

    # 4. Restore overrides post-setup
    for override in overrides:
        await override_service.apply(override)

    return result
```

### Files to Create
- `src/services/system_setup.py` (main class, 500 LOC)
- `src/services/setup_phases.py` (phase implementations, 1000 LOC)
- `tests/test_system_setup.py` (12 test cases, 400 LOC)

### Integration Points
- Calls: `extraction_to_web.py`, `web_persistence.py`, `coherence_manager.py`, `bn_service.py`, `overseer_service.py`, `semantic_scholar_enrichment.py`
- Called by: `orchestrator.py` on system startup OR explicitly via CLI

---

## Sprint 2: OVERSEER CORE
**Target Date**: 2026-02-26 → 2026-02-27
**Duration**: ~6 hours
**Owner**: Claude Code
**Dependencies**: Sprint 1 (SetupResult baseline snapshot)

### Objective
Implement OverseerService with 6 sub-components (HealthMonitor, IntegrityChecker, CompletenessAuditor, MaintenanceEngine, Scheduler, Reporter). This module continuously monitors system health and responds to anomalies.

### Architecture

**File**: `src/services/overseer.py`

**Main Class**:
```python
class OverseerService:
    """System oversight module. Monitors health, detects violations, triggers maintenance."""

    def __init__(self, config: OverseerConfig):
        self.health_monitor = HealthMonitor(config)
        self.integrity_checker = IntegrityChecker(config)
        self.completeness_auditor = CompletenessAuditor(config)
        self.maintenance_engine = MaintenanceEngine(config)
        self.scheduler = Scheduler(config)
        self.reporter = OverseerReporter(config)

    async def audit(self, scope: str = 'global') -> AuditReport:
        """On-demand full audit."""

    async def handle_post_integration(self, event: IntegrationEvent) -> None:
        """Non-blocking check after paper integration."""

    async def handle_periodic(self) -> None:
        """Nightly full audit + maintenance."""
```

### Sub-Component 1: HealthMonitor

```python
class HealthMonitor:
    """Track coherence trends, conflict rates, cache freshness, BN stability."""

    async def record_metric(self, metric_type: str, value: float, theory_id: str = None) -> None:
        """Log metric to health_metrics table."""

    async def compute_trends(self, theory_id: str = None, window: timedelta = timedelta(days=7)) -> TrendAnalysis:
        """Compute mean ± 1σ coherence over past N days."""

    async def check_thresholds(self) -> list[HealthAlert]:
        """Detect anomalies: coherence decline, high conflict, stale cache."""
```

**Database Schema**:
```sql
CREATE TABLE IF NOT EXISTS health_metrics (
    id UUID PRIMARY KEY,
    recorded_at TIMESTAMP NOT NULL,
    metric_type VARCHAR(50) NOT NULL,  -- coherence, conflict_rate, cache_freshness, bn_stability
    value FLOAT NOT NULL,
    theory_id UUID,  -- Per-theory metrics
    FOREIGN KEY (theory_id) REFERENCES theories(id)
);
```

**Alert Rules** (O-2):
| Metric | Alert Threshold | Action |
|--------|-----------------|--------|
| Coherence decline | δ < (mean - 1σ) | ALERT |
| Conflict rate | > 20% | ALERT |
| Cache stale | > 24 hours | MAINTENANCE |
| BN stability | structure changed | AUDIT_REQUIRED |

---

### Sub-Component 2: IntegrityChecker

```python
class IntegrityChecker:
    """Verify invariants INV-1..5, provenance chains, BN-web sync, contract compliance."""

    async def check_invariants(self) -> list[InvariantViolation]:
        """Verify Dijkstra invariants."""
        violations = []

        # INV-1: All beliefs have provenance
        unprovenanced = await web_of_belief.find_beliefs_without_provenance()
        if unprovenanced:
            violations.append(InvariantViolation(
                invariant="INV-1",
                count=len(unprovenanced),
                severity="MEDIUM"
            ))

        # INV-2: BN structure = web constraints (acyclicity, direction)
        bn_dag = await bn_service.get_structure()
        constraints = await constraint_service.list_all()
        constraint_dag = build_dag_from_constraints(constraints)
        if not dag_equal(bn_dag, constraint_dag):
            violations.append(InvariantViolation(
                invariant="INV-2",
                description="BN-web mismatch",
                severity="HIGH"
            ))

        # INV-3: Coherence ≥ baseline - 0.05 (Dijkstra: decline ≤ 5%)
        current_coherence = await coherence_manager.compute_global_coherence()
        baseline_coherence = await overseer_service.get_baseline().global_coherence
        if current_coherence < baseline_coherence - 0.05:
            violations.append(InvariantViolation(
                invariant="INV-3",
                description=f"Coherence declined {baseline_coherence - current_coherence:.3f} (max 0.05)",
                severity="HIGH"
            ))

        # INV-4: No circular defeater chains
        defeater_cycles = await web_of_belief.find_defeater_cycles()
        if defeater_cycles:
            violations.append(InvariantViolation(
                invariant="INV-4",
                count=len(defeater_cycles),
                severity="CRITICAL"
            ))

        # INV-5: Extraction→Integration contract satisfied (ClaimV2 schema)
        bad_claims = await extraction_service.find_schema_violations()
        if bad_claims:
            violations.append(InvariantViolation(
                invariant="INV-5",
                count=len(bad_claims),
                severity="HIGH"
            ))

        return violations
```

---

### Sub-Component 3: CompletenessAuditor

```python
class CompletenessAuditor:
    """Check template coverage, theory attachment, evidence gaps, provenance chains."""

    async def audit_template_coverage(self) -> CoverageReport:
        """Are all 208 templates instantiated in web?"""
        templates = await template_service.list_all()
        coverage = {}
        for template in templates:
            beliefs = await web_of_belief.find_beliefs_by_template(template.id)
            coverage[template.id] = len(beliefs)
        return CoverageReport(
            total_templates=len(templates),
            instantiated=len([c for c in coverage.values() if c > 0]),
            coverage_rate=len([c for c in coverage.values() if c > 0]) / len(templates)
        )

    async def audit_evidence_gaps(self) -> GapReport:
        """Which core beliefs lack experimental evidence?"""
        gaps = []
        for theory in await theory_service.list_all():
            beliefs = await web_of_belief.find_beliefs_by_theory(theory.id)
            for belief in beliefs:
                provenances = await belief_provenance_service.list_for_belief(belief.id)
                experimental = [p for p in provenances if p.study_type == StudyType.EXPERIMENTAL]
                if not experimental:
                    gaps.append(EvidenceGap(
                        belief_id=belief.id,
                        theory_id=theory.id,
                        gap_type="NO_EXPERIMENTAL"
                    ))
        return GapReport(gaps=gaps)
```

---

### Sub-Component 4: MaintenanceEngine

```python
class MaintenanceEngine:
    """Stale cache refresh, orphan cleanup, snapshot rotation, entrenchment recalc."""

    async def refresh_stale_caches(self, max_age: timedelta = timedelta(days=1)) -> MaintenanceResult:
        """Batch recompute stale QA caches."""
        stale = await qa_cache_service.find_stale(max_age)
        batch_requests = [QACacheRequest(...) for cache in stale]
        results = await llm_service.batch_qa_request(batch_requests)
        return MaintenanceResult(caches_refreshed=len(results))

    async def cleanup_orphans(self) -> MaintenanceResult:
        """Remove beliefs not attached to any theory."""
        orphans = await web_of_belief.find_orphans()
        for orphan in orphans:
            await web_of_belief.mark_for_quarantine(orphan.id)  # Not deletion
        return MaintenanceResult(orphans_quarantined=len(orphans))

    async def rotate_snapshots(self, keep_count: int = 7) -> MaintenanceResult:
        """Archive old OVERSEER snapshots; keep N most recent."""
        all_snapshots = await overseer_service.list_snapshots(order='desc')
        to_archive = all_snapshots[keep_count:]
        for snapshot in to_archive:
            await archival_service.archive_snapshot(snapshot)
        return MaintenanceResult(snapshots_archived=len(to_archive))
```

---

### Sub-Component 5: Scheduler

```python
class Scheduler:
    """POST_INTEGRATION, PERIODIC, ALERT, ON_DEMAND execution modes."""

    async def schedule_post_integration(self, event: IntegrationEvent, delay_sec: float = 5) -> None:
        """Non-blocking check after paper integration (5–10 sec delay)."""
        async def post_check():
            await asyncio.sleep(delay_sec)
            violations = await self.integrity_checker.check_invariants()
            if violations:
                await self.reporter.alert(violations)

        # Fire and forget
        asyncio.create_task(post_check())

    async def schedule_periodic(self, interval: timedelta = timedelta(hours=24)) -> None:
        """Nightly full audit (5–15 min)."""
        while True:
            await asyncio.sleep(interval.total_seconds())
            result = await self.run_full_audit()
            await self.reporter.emit_nightly_report(result)

    async def schedule_alert(self, alert: HealthAlert, delay_sec: float = 0.5) -> None:
        """Immediate alert handler (< 1 sec)."""
        await asyncio.sleep(delay_sec)
        await self.reporter.escalate_alert(alert)
```

---

### Sub-Component 6: OverseerReporter

```python
class OverseerReporter:
    """Dashboard data, health reports, alert log."""

    async def generate_dashboard_data(self) -> DashboardPayload:
        """Return metrics for Streamlit visualization."""
        return DashboardPayload(
            global_coherence=await coherence_manager.compute_global_coherence(),
            per_theory_coherence=await health_monitor.compute_trends(),
            conflict_rate=await web_of_belief.compute_conflict_rate(),
            cache_freshness=await qa_cache_service.compute_freshness(),
            bn_stability=await bn_service.assess_stability()
        )

    async def alert(self, violations: list[InvariantViolation]) -> None:
        """Log violations + emit to reporter queue."""
        for violation in violations:
            await overseer_db.log_violation(violation)
            if violation.severity == "CRITICAL":
                await self.escalate_alert(violation)
```

**Database Schema**:
```sql
CREATE TABLE IF NOT EXISTS invariant_violations (
    id UUID PRIMARY KEY,
    detected_at TIMESTAMP NOT NULL,
    invariant VARCHAR(10) NOT NULL,  -- INV-1, INV-2, ...
    description TEXT,
    severity VARCHAR(20) NOT NULL,  -- LOW, MEDIUM, HIGH, CRITICAL
    resolution_status VARCHAR(20) DEFAULT 'OPEN'  -- OPEN, QUARANTINE, RESOLVED
);

CREATE TABLE IF NOT EXISTS snapshot_index (
    id UUID PRIMARY KEY,
    created_at TIMESTAMP NOT NULL,
    system_state JSONB NOT NULL,
    dijkstra_invariant_verified BOOLEAN DEFAULT FALSE
);
```

---

### Quarantine Protocol (O-3)

Violations are NOT auto-retired; instead:

```python
class QuarantineProtocol:
    async def quarantine_belief(self, belief_id: UUID, reason: str, review_window: timedelta = timedelta(days=7)) -> None:
        """Mark belief QUARANTINED; require manual review before retire."""
        await web_of_belief.set_status(belief_id, "QUARANTINED")
        await overseer_db.create_quarantine_record(
            belief_id=belief_id,
            reason=reason,
            quarantine_until=datetime.now() + review_window
        )

    async def review_quarantine(self, quarantine_id: UUID, decision: Literal['RETIRE', 'RESTORE']) -> None:
        """Expert decision: retire or restore."""
```

---

### Files to Create
- `src/services/overseer.py` (main class, 300 LOC)
- `src/services/overseer_components/health_monitor.py` (200 LOC)
- `src/services/overseer_components/integrity_checker.py` (300 LOC)
- `src/services/overseer_components/completeness_auditor.py` (200 LOC)
- `src/services/overseer_components/maintenance_engine.py` (200 LOC)
- `src/services/overseer_components/scheduler.py` (150 LOC)
- `src/services/overseer_components/reporter.py` (150 LOC)
- `tests/test_overseer.py` (800 LOC, comprehensive)

### Integration with Orchestrator
```python
# In src/services/paper_integration/orchestrator.py
async def integrate_paper(self, paper_id: str) -> IntegrationResult:
    """... 13 steps ... then POST_INTEGRATION check."""
    result = await self._execute_steps()

    # Non-blocking OVERSEER check (daemon thread)
    asyncio.create_task(
        overseer_service.scheduler.schedule_post_integration(result.event)
    )

    return result
```

---

## Sprint 3: COHERENCE DASHBOARD
**Target Date**: 2026-02-27
**Duration**: ~3 hours
**Owner**: Claude Code
**Dependencies**: Sprint 2 (OverseerReporter)

### Objective
Implement Cartwright's multi-metric dashboard. Visualize system health in real-time; establish statistical baselines for alerting.

### Metrics

1. **Global Coherence**: Single scalar [0, 1]
   - Formula: average pairwise belief compatibility
   - Baseline: from Phase 8 (Setup)

2. **Per-Theory Coherence**: One score per T1.5 theory
   - Formula: mean belief coherence within theory network
   - Alert: δ < (theory_mean - 1σ)

3. **Conflict Rate**: Fraction of belief pairs in contradiction
   - Formula: conflicting_pairs / (total_pairs)
   - Threshold: > 20% → ALERT

4. **Orphan Count**: Beliefs not attached to any theory
   - Threshold: > 5 → ALERT

5. **Methodological Diversity Index**: Fraction of non-experimental evidence
   - Formula: (observational + theoretical) / total_beliefs
   - Risk: > 0.8 (≥ 80% non-experimental) → MONOCULTURE_RISK

### Streamlit Page

**File**: `streamlit_app.py` (new page or integrated)

```python
import streamlit as st
from datetime import timedelta
import pandas as pd
import plotly.graph_objects as go

@st.cache_resource
async def load_overseer():
    return OverseerService(config)

async def dashboard_page():
    st.set_page_config(page_title="Article Eater: Health Dashboard", layout="wide")
    st.title("System Health & Coherence Monitor")

    overseer = await load_overseer()
    payload = await overseer.reporter.generate_dashboard_data()

    # Row 1: KPIs
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Global Coherence",
            f"{payload.global_coherence:.3f}",
            delta=f"{payload.global_coherence - payload.baseline_coherence:+.3f}",
            delta_color="inverse"  # Red if negative
        )

    with col2:
        st.metric(
            "Conflict Rate",
            f"{payload.conflict_rate:.1%}",
            delta="🔴 ALERT" if payload.conflict_rate > 0.2 else "🟢 OK"
        )

    with col3:
        st.metric("Cache Freshness", f"{payload.cache_freshness:.1%}")

    with col4:
        st.metric("BN Stability", payload.bn_stability)

    # Row 2: Per-theory coherence (line chart + table)
    st.subheader("Per-Theory Coherence Trends")

    # Historical data (last 7 days)
    trends = await overseer.health_monitor.compute_trends(window=timedelta(days=7))

    fig = go.Figure()
    for theory_id, data in payload.per_theory_coherence.items():
        fig.add_trace(go.Scatter(
            x=data['timestamps'],
            y=data['values'],
            name=theory_id,
            mode='lines+markers'
        ))

    fig.update_layout(
        title="7-Day Coherence History",
        xaxis_title="Time",
        yaxis_title="Coherence Score"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Alert rules table
    st.subheader("Alert Rules (Cartwright Baseline)")
    alert_rules = pd.DataFrame([
        {"Metric": "Coherence Decline", "Rule": "δ < (mean - 1σ)", "Action": "ALERT"},
        {"Metric": "Conflict Rate", "Rule": "> 20%", "Action": "ALERT"},
        {"Metric": "Cache Stale", "Rule": "> 24 hours", "Action": "MAINTENANCE"},
        {"Metric": "Methodological Diversity", "Rule": "< 20% experimental", "Action": "MONOCULTURE_RISK"}
    ])
    st.table(alert_rules)

    # Row 3: Invariant status
    st.subheader("Dijkstra Invariant Status")
    violations = await overseer.integrity_checker.check_invariants()

    if violations:
        st.warning(f"⚠️ {len(violations)} violations detected")
        for violation in violations:
            st.error(f"**{violation.invariant}**: {violation.description} (Severity: {violation.severity})")
    else:
        st.success("✅ All invariants satisfied")

    # Row 4: Maintenance log
    st.subheader("Recent Maintenance")
    logs = await overseer.reporter.get_maintenance_log(limit=10)
    st.dataframe(pd.DataFrame(logs))
```

### Testing
```bash
# Unit: Verify metric computation
pytest tests/test_dashboard_metrics.py -v

# Integration: Streamlit visual inspection
streamlit run streamlit_app.py
```

### Files to Create
- `streamlit_app.py` (new page or module, 300 LOC)
- `src/services/overseer_components/dashboard_metrics.py` (200 LOC)
- `tests/test_dashboard_metrics.py` (200 LOC)

---

## Sprint 4: ARGUMENTATION GRAPH
**Target Date**: 2026-02-27 → 2026-02-28
**Duration**: ~3 hours
**Owner**: Claude Code
**Dependencies**: Sprint 0 (citation_graph.json), Sprint 2 (IntegrityChecker)

### Objective
Build ArgumentationGraph from citation_graph.json. Model how papers respond to each other (supportive vs. critical citations). Integrate with social_epistemology.py and supersession.py.

### Architecture

**File**: `src/services/argumentation_graph.py`

```python
class ArgumentationGraph:
    """Temporal + citation + polarity integration."""

    async def build_from_citations(self, citation_graph: dict) -> None:
        """Load citation_graph.json; infer polarity."""

    async def infer_citation_polarity(self, citing_paper: dict, cited_paper: dict) -> CitationPolarity:
        """Supportive or critical? Uses text analysis + belief alignment."""

    async def detect_temporal_supersession(self, belief_id: UUID) -> SupersessionRelationship:
        """Which later papers undermine or improve on earlier claims?"""

    async def find_debate_clusters(self) -> list[DebateCluster]:
        """Identify clusters of papers arguing about the same question."""
```

**Key Classes**:
```python
@dataclass
class CitationPolarity:
    citing_paper_id: str
    cited_paper_id: str
    polarity: Literal['SUPPORTIVE', 'CRITICAL', 'NEUTRAL', 'UNKNOWN']
    confidence: float  # [0, 1]
    evidence: str  # E.g., "cited with disagreement markers"

@dataclass
class SupersessionRelationship:
    earlier_belief_id: UUID
    later_belief_id: UUID
    type: Literal['IMPROVED', 'CONTRADICTED', 'REFINED']
    publication_gap_years: int

@dataclass
class DebateCluster:
    cluster_id: str
    question: str  # E.g., "Does natural light affect mood?"
    papers: list[str]  # Paper IDs in debate
    positions: dict  # paper_id → position (pro/con/neutral)
    temporal_span: tuple  # (earliest, latest publication year)
```

### Integration Points

1. **Citation Polarity Detection** (NLP + belief alignment):
   ```python
   async def infer_polarity(citing, cited):
       # Heuristic 1: Citation context (markers like "contradicting", "supporting")
       context = extract_citation_context(citing, cited)
       if "contradict" in context or "disagree" in context:
           return CitationPolarity(..., polarity='CRITICAL')

       # Heuristic 2: Belief alignment (do extracted claims align?)
       citing_beliefs = await web_of_belief.find_beliefs_by_paper(citing['id'])
       cited_beliefs = await web_of_belief.find_beliefs_by_paper(cited['id'])

       alignment = compute_belief_alignment(citing_beliefs, cited_beliefs)
       if alignment < 0.3:  # Low alignment → critical
           return CitationPolarity(..., polarity='CRITICAL')
       elif alignment > 0.7:  # High alignment → supportive
           return CitationPolarity(..., polarity='SUPPORTIVE')
       else:
           return CitationPolarity(..., polarity='NEUTRAL')
   ```

2. **Temporal Supersession** (calls `supersession.py`):
   ```python
   async def detect_supersession(belief_id):
       belief = await web_of_belief.get(belief_id)
       provenances = await belief_provenance_service.list_for_belief(belief_id)

       # Find papers citing the foundational paper
       citing_papers = citation_graph['citing'][provenances[0].paper_id]

       for later_paper in citing_papers:
           later_beliefs = await web_of_belief.find_beliefs_by_paper(later_paper)

           # Check supersession.compute_supersession() logic
           supersession = await supersession_service.compute_supersession(
               earlier_belief_id=belief_id,
               later_paper_id=later_paper
           )

           if supersession.type != 'NONE':
               return SupersessionRelationship(...)
   ```

3. **Community Detection** (calls `social_epistemology.py`):
   ```python
   async def find_debate_clusters():
       # Use co-citation + co-authorship to find clusters
       communities = await social_epistemology_service.detect_communities()

       clusters = []
       for community in communities:
           # For each theory in the community, find papers with opposing positions
           debates = await identify_debates_within_community(community)
           clusters.extend(debates)

       return clusters
   ```

### Files to Create
- `src/services/argumentation_graph.py` (400 LOC)
- `tests/test_argumentation_graph.py` (300 LOC)

### Database Schema
```sql
CREATE TABLE IF NOT EXISTS citation_polarities (
    id UUID PRIMARY KEY,
    citing_paper_id VARCHAR(100) NOT NULL,
    cited_paper_id VARCHAR(100) NOT NULL,
    polarity VARCHAR(20) NOT NULL,  -- SUPPORTIVE, CRITICAL, NEUTRAL
    confidence FLOAT NOT NULL,
    evidence TEXT,
    UNIQUE(citing_paper_id, cited_paper_id)
);

CREATE TABLE IF NOT EXISTS supersession_relationships (
    id UUID PRIMARY KEY,
    earlier_belief_id UUID NOT NULL,
    later_belief_id UUID NOT NULL,
    relationship_type VARCHAR(20) NOT NULL,  -- IMPROVED, CONTRADICTED, REFINED
    publication_gap_years INT,
    FOREIGN KEY (earlier_belief_id) REFERENCES beliefs(id),
    FOREIGN KEY (later_belief_id) REFERENCES beliefs(id)
);
```

---

## Sprint 5: NIGHTLY BATCH INFRASTRUCTURE
**Target Date**: 2026-02-28 → 2026-03-01
**Duration**: ~2 hours
**Owner**: Claude Code
**Dependencies**: Sprint 2 (Scheduler), Sprint 4 (ArgumentationGraph)

### Objective
Implement nightly maintenance pipeline: batched QA cache recomputation, integrity audits, snapshot rotation, health report generation.

### Components

**File**: `scripts/overseer_nightly.py`

```python
import asyncio
from src.services.overseer import OverseerService

async def nightly_pipeline():
    """Run every 24 hours (e.g., 2 AM)."""
    overseer = OverseerService(config)

    # 1. Full integrity audit (5 min)
    violations = await overseer.integrity_checker.check_invariants()
    completeness = await overseer.completeness_auditor.audit_template_coverage()
    gaps = await overseer.completeness_auditor.audit_evidence_gaps()

    # 2. Batch QA cache refresh (5–10 min)
    maintenance = await overseer.maintenance_engine.refresh_stale_caches()

    # 3. Orphan cleanup (1 min)
    orphan_result = await overseer.maintenance_engine.cleanup_orphans()

    # 4. Snapshot rotation (1 min)
    snapshot_result = await overseer.maintenance_engine.rotate_snapshots(keep_count=7)

    # 5. Health report generation (2 min)
    report = await overseer.reporter.generate_health_report(
        violations=violations,
        completeness=completeness,
        gaps=gaps,
        maintenance=maintenance
    )

    # 6. Emit report + alerts
    await overseer.reporter.emit_nightly_report(report)

    return report

if __name__ == "__main__":
    report = asyncio.run(nightly_pipeline())
    print(f"Nightly maintenance complete: {report}")
```

### Scheduler Configuration

**File**: `.env` or `config/overseer_config.yaml`

```yaml
overseer:
  nightly_schedule: "02:00 UTC"  # 2 AM UTC
  post_integration_delay: 5      # seconds
  periodic_interval: 86400       # 24 hours
  alert_threshold_coherence_delta: -0.05  # 5% decline
  alert_threshold_conflict: 0.2  # 20% conflicts
  cache_staleness_max_age: 86400 # 24 hours
  quarantine_review_window: 604800  # 7 days
```

### ACTIVE_TASKS.md Coordination (O-8)

For parallel maintenance work:

```markdown
## OVERSEER-MAINT Lane

| Work Item | Owner | Status | Completed |
|-----------|-------|--------|-----------|
| Cache recomputation | OVERSEER-MAINT-1 | IN_PROGRESS | - |
| Integrity audit | OVERSEER-MAINT-2 | PENDING | - |
| Snapshot rotation | OVERSEER-MAINT-3 | PENDING | - |
```

### Files to Create
- `scripts/overseer_nightly.py` (200 LOC)
- `config/overseer_config.yaml` (50 LOC)
- `tests/test_overseer_nightly.py` (200 LOC)

---

## Sprint 6: EXPERT CALIBRATION PREP
**Target Date**: 2026-03-01 → 2026-03-02
**Duration**: ~2 hours
**Owner**: Claude Code
**Dependencies**: Sprint 1 (SetupResult baseline), Sprint 2 (HealthMonitor)

### Objective
Prepare inputs for panel expert calibration. Generate reports on per-theory coherence, community structure, VOI gaps, and citation topology. These inform threshold settings and manual overrides.

### Calibration Inputs

| Input | Source | Panel Use |
|-------|--------|-----------|
| Per-theory coherence baselines | Phase 8 (Setup) | Spohn + Cartwright: calibrate per-theory alert thresholds |
| Community identification results | Phase 10 (Social Epistemology) | Haack + Simon: identify monoculture risk; assess expertise diversity |
| VOI gap initial assessment | Phase 11 (Discovery Funnel) | Pearl + Cartwright: prioritize high-impact research directions |
| Citation graph statistics | Sprint 0 + 4 (ArgumentationGraph) | Sackett: assess evidence quality distribution across methodologies |
| Methodological diversity | Health Monitor | Cartwright: verify we're not over-weighting single methodology |

### Calibration Report

**File**: `docs/EXPERT_CALIBRATION_REPORT_2026-03-02.md`

```markdown
# Expert Calibration Report
**Date**: 2026-03-02
**System Version**: V22.0.0 + Setup + OVERSEER baseline

## I. Per-Theory Coherence Baselines

| Theory ID | Baseline Coherence | Mean (7d) | StdDev (7d) | Alert Threshold (mean - 1σ) |
|-----------|-------------------|-----------|------------|---------------------------|
| T1.5-01 (ART) | 0.78 | 0.77 | 0.04 | 0.73 |
| T1.5-02 (SRT) | 0.72 | 0.71 | 0.05 | 0.66 |
| T1.5-03 (Biophilia) | 0.82 | 0.81 | 0.03 | 0.78 |
| ... | ... | ... | ... | ... |

**Interpretation**: Theory with baseline 0.78 should alert if coherence drops below 0.73 (one standard deviation decline).

**Panel Action**: Review thresholds; adjust if empirically unreasonable.
```

### Community Structure Report

```markdown
## II. Community Identification Results

**Total Communities**: 15
**Avg Community Size**: 8.3 papers
**Largest Community**: 24 papers (Environmental Psychology Empiricists)
**Smallest**: 2 papers (Methodological Isolates)

### Top 3 Communities by Consensus Strength

| Community | Size | Consensus Credence | Methodological Diversity | Monoculture Risk |
|-----------|------|-------------------|------------------------|-----------------|
| EP-Empiricists | 24 | 0.82 | 45% RCT / 35% QE / 20% Observational | LOW |
| Space-Syntax-Formalists | 12 | 0.71 | 15% RCT / 70% Computational / 15% Observational | MEDIUM |
| Neuroscience-Behaviorists | 8 | 0.79 | 60% RCT / 30% Observational / 10% Theoretical | LOW |

**Panel Action**: Examine "Space-Syntax-Formalists" for methodological homogeneity. Consider upweighting RCT-based community claims.
```

### VOI Gap Initial Assessment

```markdown
## III. Value of Information (VOI) Gaps

**High-VOI Gaps Identified**: 18
**Medium-VOI**: 34
**Low-VOI**: 12

### Top 5 High-VOI Gaps (expert panel to prioritize)

1. **Natural Light & Circadian Synchrony**
   - Current evidence: Mostly observational, small sample RCTs
   - Gap: Need controlled RCT with circadian biomarkers (cortisol, melatonin)
   - VOI: 0.85 (high impact if resolved)

2. **Space Syntax & Wayfinding Confidence**
   - Current evidence: Correlational (architecture students)
   - Gap: Need longitudinal follow-up; real building wayfinding
   - VOI: 0.78

... [full list]

**Panel Action**: David's panel to rank; assign highest VOI scores to discovery funnel.
```

### Citation Graph Statistics

```markdown
## IV. Citation Topology & Methodological Reach

**Total Papers**: 850
**Citation Density**: 0.42 (42% of possible edges present)
**Temporal Span**: 1985–2026 (41 years)
**Citation Polarity Breakdown**:
- Supportive: 58% of citations
- Critical: 22% of citations
- Neutral: 20% of citations

### Methodological Distribution (Citation-Weighted)

| Methodology | Count | Avg In-Degree | Avg Credence (web) |
|------------|-------|---|---|
| RCT | 95 | 12.4 | 0.78 |
| Quasi-Experimental | 110 | 9.1 | 0.71 |
| Observational | 340 | 5.8 | 0.63 |
| Phenomenological | 180 | 3.2 | 0.55 |
| Computational | 85 | 4.5 | 0.58 |
| Theoretical | 40 | 2.1 | 0.50 |

**Insight**: RCT-based claims have highest in-degree (citation count) AND highest credence in web. Indicates good alignment between citation patterns + coherence-based credence.

**Panel Action**: Verify that DerSimonian-Laird weighting respects this ordering; consider quality-weight coefficient.
```

### Calibration Review Checklist

```markdown
## V. Calibration Review Checklist

**For Panel Review** (David + domain experts):

- [ ] Do per-theory alert thresholds (mean ± 1σ) seem reasonable?
- [ ] Are identified communities epistemically coherent, or do they hide internal disagreements?
- [ ] Which VOI gaps should be top priority? (Assign numerical VOI scores.)
- [ ] Citation polarity inference (58% supportive)—does this match domain knowledge?
- [ ] Methodological diversity index: Are we over-weighting observational studies?
- [ ] Any theories over-represented by single authors/institutions? (Monoculture risk.)

**Output**: Updated config with:
- Finalized alert thresholds per theory
- Approved VOI gap rankings
- Manual overrides for problematic beliefs
```

### Files to Create
- `docs/EXPERT_CALIBRATION_REPORT_2026-03-02.md` (1000+ lines, data-rich)
- `scripts/generate_calibration_report.py` (300 LOC)

---

## Cross-Sprint Dependencies & Risk Assessment

### Dependency Chain

```
Sprint 0 (Metadata)
    ↓
Sprint 1 (Setup)
    ├─→ Sprint 2 (OVERSEER) → Sprint 3 (Dashboard) ─────→ Sprint 6 (Calibration)
    ├─→ Sprint 4 (Argumentation) → Sprint 5 (Nightly)
    └─→ Sprint 3 (Dashboard)
```

### Risk Register

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| Phase 5 (Eq.) doesn't converge | MEDIUM | HIGH | Safety bound (20 iters); partial acceptance |
| Citation graph incomplete (< 95% coverage) | LOW | MEDIUM | Fallback to temporal ordering alone |
| LLM batch failure (Sprint 9) | LOW | MEDIUM | Fallback to lazy (on-demand) QA computation |
| Coherence collapse (INV-3 violation) | LOW | CRITICAL | Quarantine mode; require manual expert review |
| Provenance computation O(n²) complexity | MEDIUM | LOW | Batch processing + lazy grounding chains |

### Testing & Validation

**Comprehensive Test Suite**:
```bash
# Unit tests per sprint
pytest tests/test_system_setup.py -v
pytest tests/test_overseer.py -v
pytest tests/test_dashboard_metrics.py -v
pytest tests/test_argumentation_graph.py -v

# Integration tests
pytest tests/integration/ -v

# Full system initialization (dry run)
python -m pytest tests/test_system_setup.py::TestSystemSetup::test_setup_completes --tb=short

# Load test (1000 papers)
python scripts/load_test_setup.py --papers 1000
```

---

## Delivery Timeline

| Sprint | Dates | Duration | Owner | Status |
|--------|-------|----------|-------|--------|
| 0: Metadata Enrichment | Feb 25 | 0.5 hr | Claude Code | READY |
| 1: Setup Function | Feb 25–26 | 4 hrs | Claude Code | READY |
| 2: OVERSEER Core | Feb 26–27 | 6 hrs | Claude Code | READY |
| 3: Dashboard | Feb 27 | 3 hrs | Claude Code | READY |
| 4: Argumentation Graph | Feb 27–28 | 3 hrs | Claude Code | READY |
| 5: Nightly Batch | Feb 28–Mar 1 | 2 hrs | Claude Code | READY |
| 6: Calibration Prep | Mar 1–2 | 2 hrs | Claude Code | READY |
| **Panel Review** | **Mar 2–3** | **~4 hrs** | **David + Panel** | **PENDING** |

**Total Engineering**: ~20.5 hours
**Total Expert Input**: ~6 hours (panel calibration review)
**System Operational Target**: March 3, 2026 (OPERATIONAL state achieved)

---

## Key Decisions Embedded (Panel Consensus)

### O-1: Credence Computation (Web of Belief)
**Decision**: Full pipeline (theory inference + reflective equilibrium + DerSimonian-Laird)
**Panelists**: Quine, Haack, Spohn, DerSimonian
**Rationale**: Holism + foundherentism + meta-analytic rigor

### O-2: Coherence Alert Threshold
**Decision**: Statistical baseline (mean ± 1σ per theory)
**Panelist**: Cartwright
**Rationale**: Respect methodological diversity; don't assume single monotonic scale

### O-3: Invariant Violation Handling
**Decision**: Quarantine (7-day review window), not auto-retire
**Panelist**: Haack
**Rationale**: Preserve epistemic due diligence; expert judgment required

### O-4: BN Coupling
**Decision**: Hierarchical one-directional (web → BN priors, no feedback)
**Panelists**: Pearl, Cartwright, Good
**Rationale**: Simplicity + Pearl's do-calculus assumptions

### O-5: Provenance Timing
**Decision**: Synchronous (Step 5), not deferred
**Panelist**: Haack
**Rationale**: Foundherentism demands grounding chains; can't be lazy

### O-6: QA Cache Strategy
**Decision**: Batched nightly (Option C)
**Panelist**: Good
**Rationale**: Balances computational cost ($) vs. freshness (hours) vs. responsiveness (low latency)

### O-7: OVERSEER Database
**Decision**: Separate (overseer.db), not shared with main belief store
**Panelist**: Parnas
**Rationale**: Information hiding; OVERSEER is auditor, not participant

### O-8: Maintenance Work Lanes
**Decision**: Parallel OVERSEER-MAINT lanes in ACTIVE_TASKS.md
**Panelist**: Simon (organizational design)
**Rationale**: Explicit coordination prevents duplicate work; maintains accountability

---

## Success Criteria

### Functional
- [ ] All 12 setup phases complete without error
- [ ] System enters OPERATIONAL state (Dijkstra INV-0 verified)
- [ ] 850 papers integrated, ≥ 2,000 beliefs created
- [ ] OVERSEER detects invariant violations correctly
- [ ] Dashboard updates in real-time (< 5 sec latency)
- [ ] Nightly pipeline completes in ≤ 15 min
- [ ] Citation graph built; polarity inferred for ≥ 95% edges
- [ ] Calibration report delivered to panel

### Non-Functional
- [ ] Setup completes in < 2 hours (target: 90 min)
- [ ] Per-paper integration time ≤ 30 sec (with OVERSEER)
- [ ] Memory usage ≤ 4 GB (web + BN + cache)
- [ ] Test coverage ≥ 85% (new code)
- [ ] All 27 existing tests still pass

### Epistemic
- [ ] Global coherence baseline established (≥ 0.65 target)
- [ ] Reflective equilibrium converges (delta < 0.001 OR partial acceptance)
- [ ] BN structure respects causal constraints (no spurious edges)
- [ ] Provenance chains trace all beliefs to experiential grounding
- [ ] Panel reviews calibration inputs; approves thresholds

---

## References

### Panel Theoretical Commitments

1. **Quine, W. V. O.** (1951). "Two Dogmas of Empiricism." *Philosophical Review*, 60(1), 20–43.
2. **Haack, S.** (1993). *Evidence and Inquiry*. Blackwell Publishers.
3. **Spohn, W.** (2012). *The Laws of Belief*. Oxford University Press.
4. **Pearl, J.** (2009). *Causality: Models, Reasoning, and Inference*. Cambridge University Press.
5. **Cartwright, N.** (2007). *Hunting Causes and Using Them*. Cambridge University Press.
6. **Dijkstra, E. W.** (1968). "The Structure of the 'THE' Multiprogramming System." *Commun. ACM*, 11(5), 341–346.
7. **DerSimonian, R., & Laird, N.** (1986). "Meta-analysis in clinical trials." *Controlled Clinical Trials*, 7(3), 177–188.

---

## Approval & Sign-Off

**Prepared by**: Claude Code
**Date**: 2026-02-25
**Status**: READY FOR DAVID KIRSH REVIEW & APPROVAL

**Panel Recommendations Incorporated**: O-1 through O-8 (all 8 design questions resolved)
**Next Step**: David reviews plan; authorizes Sprint 0 start or requests modifications

---

**Document Version**: V1.0
**Last Updated**: 2026-02-25
**Maintained by**: Claude Code (Article_Eater_PostQuinean_v1 project)
