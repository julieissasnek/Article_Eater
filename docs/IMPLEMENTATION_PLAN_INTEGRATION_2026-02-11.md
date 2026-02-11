# Implementation Plan: Web-BN Integration

**Date**: 2026-02-11
**Based on**: INTEGRATION_ARCHITECTURE_WEB_BN_2026-02-11.md
**Panel Approved**: P-VIS, P-LAYER

---

## Overview

Six sprints to implement the 12-layer integration architecture. Each sprint is self-contained with testable deliverables.

---

## Sprint INT-1: Edge Justification Foundation

**Goal**: Create the bridge data structure that links BN edges to epistemic beliefs.

**Deliverables**:
1. `contracts/schemas/integration.edge_justification.v1.schema.json`
2. `src/services/edge_justification.py` — EdgeJustificationService
3. API endpoint: `GET /api/v1/integration/edge/{edge_id}/justification`
4. Tests: `tests/test_edge_justification.py`

**Key Classes**:
```python
@dataclass
class EdgeJustification:
    edge_id: str
    source_node: str
    target_node: str
    aggregate_credence: float
    aggregate_uncertainty: float
    supporting_beliefs: List[BeliefSummary]
    conflicting_beliefs: List[ConflictSummary]
    net_support: float
    key_theories: List[str]
    provenance: ProvenanceSummary

class EdgeJustificationService:
    def get_justification(self, source_var: str, target_var: str) -> EdgeJustification
    def get_all_justifications(self) -> List[EdgeJustification]
    def get_unjustified_edges(self) -> List[str]  # Edges without belief support
```

**Acceptance Criteria**:
- [ ] Schema validates against JSON Schema draft 2020-12
- [ ] Service finds beliefs that match BN edge variables
- [ ] Aggregate credence computed correctly (inverse-variance weighting)
- [ ] API returns EdgeJustification JSON

---

## Sprint INT-2: Gap Prediction Engine

**Goal**: Implement algorithm to predict knowledge gaps from argument structure.

**Deliverables**:
1. `src/services/gap_predictor.py` — GapPredictor class
2. Schema: `contracts/schemas/integration.gap_prediction.v1.schema.json`
3. Integration with QueryEngine gap reports
4. Tests: `tests/test_gap_predictor.py`

**Gap Types to Implement**:
| Gap Type | Detection Method |
|----------|------------------|
| Mediation | Find A→X→Y paths without A→Y |
| Mechanism | Edges with empirical but no theoretical beliefs |
| Boundary | Edges with narrow scope conditions |
| Direction | Edges with conflicting causal directions |
| Interaction | Independent effects without interaction beliefs |
| Validation | Edges with theoretical but no empirical beliefs |

**Key Classes**:
```python
@dataclass
class PredictedGap:
    gap_id: str
    gap_type: GapType
    description: str
    affected_edge: Optional[str]
    implied_by: List[str]  # Belief IDs that imply this gap
    voi_score: float
    suggested_search: str
    resolution_approach: str

class GapPredictor:
    def find_mediation_gaps(self) -> List[PredictedGap]
    def find_mechanism_gaps(self) -> List[PredictedGap]
    def find_boundary_gaps(self) -> List[PredictedGap]
    def find_direction_gaps(self) -> List[PredictedGap]
    def find_all_gaps(self) -> List[PredictedGap]
```

**Acceptance Criteria**:
- [ ] Each gap type has working detection
- [ ] VOI scores computed for prioritization
- [ ] Gaps link back to source beliefs
- [ ] Integration with existing gap_report schema

---

## Sprint INT-3: BN Frontend — Edge Confidence & Evidence Panel

**Goal**: Modify BN_graphical frontend to show belief-backed confidence.

**Deliverables** (in BN_graphical repo):
1. Modified `CausalGraphView.tsx` — Edge opacity from credence
2. New `EvidencePanel.tsx` — Slide-in panel for edge details
3. API client updates to fetch justification
4. Tests: Component tests

**UI Changes**:
```
┌─────────────────────────────────────────────────────────────────┐
│  BN Graph View                                          [≡] [?] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [Attributes] ───────────────► [Mediators] ─────────► [Outcomes]│
│                    │                                            │
│               click edge                                        │
│                    ▼                                            │
│  ┌─────────────────────────────────────────┐                   │
│  │ EVIDENCE PANEL                     [×]  │                   │
│  │                                         │                   │
│  │ Edge: daylight → stress                 │                   │
│  │ Confidence: 0.72 ± 0.15                 │                   │
│  │                                         │                   │
│  │ Supporting Evidence (5):                │                   │
│  │ • Natural light reduces cortisol (0.81) │                   │
│  │ • Daylight improves mood states (0.75)  │                   │
│  │ [Show more...]                          │                   │
│  │                                         │                   │
│  │ Conflicts (1):                          │                   │
│  │ • Artificial light equally effective... │                   │
│  │                                         │                   │
│  │ [View in Epistemic Web]                 │                   │
│  └─────────────────────────────────────────┘                   │
└─────────────────────────────────────────────────────────────────┘
```

**Acceptance Criteria**:
- [ ] Edges render with opacity based on credence
- [ ] Click on edge opens Evidence Panel
- [ ] Panel shows supporting and conflicting beliefs
- [ ] "View in Epistemic Web" button (placeholder for INT-4)

---

## Sprint INT-4: Epistemic Web Visualization Component

**Goal**: Create React component for visualizing the epistemic web.

**Deliverables** (in BN_graphical repo):
1. `src/features/epistemic/WebView.tsx` — Main component
2. `src/features/epistemic/BeliefNode.tsx` — Custom node
3. `src/features/epistemic/ConstraintEdge.tsx` — Custom edge
4. Integration with existing React Flow setup
5. Tests: Component tests

**Features**:
- Clustering by theory (Tufte recommendation)
- Node shapes by epistemic level (Haack recommendation)
- Edge colors by constraint polarity (green=support, red=tension)
- Filtering by theory, level, status
- Focus mode: Show only beliefs for a specific BN edge

**Node Visual Encoding**:
| Epistemic Level | Shape | Color |
|-----------------|-------|-------|
| THEORETICAL | Diamond | Purple |
| EMPIRICAL | Circle | Blue |
| OBSERVATIONAL | Square | Green |

**Acceptance Criteria**:
- [ ] Web renders with correct node shapes/colors
- [ ] Constraints render with correct polarity colors
- [ ] Filter controls work
- [ ] Can focus on beliefs for a specific BN edge
- [ ] Navigation back to BN view works

---

## Sprint INT-5: Cross-Layer Query API

**Goal**: Unified API for all cross-layer query patterns.

**Deliverables**:
1. `src/services/cross_layer_query.py` — CrossLayerQueryService
2. API endpoints:
   - `GET /api/v1/integration/provenance/{belief_id}`
   - `GET /api/v1/integration/theories/{belief_id}`
   - `GET /api/v1/integration/community/{belief_id}`
   - `GET /api/v1/integration/causal/{belief_id}`
   - `GET /api/v1/integration/gaps?topic={topic}`
3. Tests: `tests/test_cross_layer_query.py`

**Query Types**:
```python
class CrossLayerQueryService:
    def trace_provenance(self, belief_id: str) -> ProvenanceTrace
    def get_theory_grounding(self, belief_id: str) -> TheoryGrounding
    def get_community_perspectives(self, belief_id: str) -> CommunityPerspectives
    def get_causal_implications(self, belief_id: str) -> CausalImplications
    def discover_gaps(self, topic: str) -> List[PredictedGap]
```

**Acceptance Criteria**:
- [ ] Each query type returns structured response
- [ ] Provenance traces back to source documents
- [ ] Community perspectives show per-community credence
- [ ] Causal implications show BN edge consistency
- [ ] Gap discovery uses GapPredictor from INT-2

---

## Sprint INT-6: User Modes & Integration Testing

**Goal**: Implement three user modes and end-to-end testing.

**Deliverables**:
1. Mode switcher UI component
2. Mode-specific views:
   - Knowledge Mode: Query answers with confidence
   - Prediction Mode: BN visualization with predictions
   - Expert Mode: Full layer access
3. End-to-end integration tests
4. User documentation updates

**Mode Switching**:
```
┌─────────────────────────────────────────────────────────────────┐
│  [Knowledge] [Prediction] [Expert]           Article Eater MVP  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  (Content changes based on selected mode)                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Acceptance Criteria**:
- [ ] Mode switcher in header
- [ ] Each mode shows appropriate content
- [ ] Cross-mode navigation works (drill from Knowledge to Expert)
- [ ] End-to-end test: Paper → Extraction → Belief → BN Edge → Query → Answer
- [ ] Documentation updated

---

## Sprint Dependencies

```
INT-1 (Edge Justification)
   │
   ├──► INT-2 (Gap Prediction) ──┐
   │                             │
   └──► INT-3 (BN Frontend) ─────┼──► INT-6 (Modes & Testing)
                                 │
        INT-4 (Web Component) ───┤
                                 │
        INT-5 (Cross-Layer API) ─┘
```

**Parallelization**:
- INT-1 must complete first (foundation)
- INT-2, INT-3, INT-4 can run in parallel after INT-1
- INT-5 can run in parallel with INT-3, INT-4
- INT-6 depends on all others

---

## Estimated Effort

| Sprint | Complexity | Files | Tests |
|--------|------------|-------|-------|
| INT-1 | Medium | 3 | 15 |
| INT-2 | High | 2 | 20 |
| INT-3 | Medium | 4 | 10 |
| INT-4 | High | 4 | 10 |
| INT-5 | Medium | 2 | 15 |
| INT-6 | Medium | 3 | 20 |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| BN variable names don't match belief terms | Create vocabulary mapping in INT-1 |
| React Flow performance with large webs | Implement virtualization in INT-4 |
| Cross-repo coordination | Define API contracts first (INT-1, INT-5) |
| Circular justification (BN→Web→BN) | Mark MODEL_DERIVED beliefs distinctly |

---

*Plan created: 2026-02-11*
*Ready for implementation*
