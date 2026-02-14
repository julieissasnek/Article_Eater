# CODEBASE_MAP.md — Epistemic Tier 2 Discovery

**Date**: Friday, February 14, 2026
**Sprint**: 0 (Discovery)
**Task**: 0.1

---

## Baseline Test State (Task 0.2)

**Date**: 2026-02-14
**Command**: `pytest tests/ -v`

| Metric | Count |
|--------|-------|
| **Passed** | 2346 |
| **Failed** | 19 |
| **Skipped** | 10 |
| **Collection Errors** | 12 |
| **Warnings** | 30 |

**Collection Errors** (12 files with import issues):
- test_api_key_routes.py, test_api_smoke.py, test_full_integration.py
- test_gold_standard.py, test_subject_bn_*.py (3 files)
- test_ui_admin_surfaces.py, test_usage_admin_auth.py
- test_vocabulary_bridge.py, test_voi_search.py, test_web_of_belief_routes.py

**Failed Tests** (19):
- API extended tests (15): Theory/Entrenchment/Graph/Bundle/History endpoints
- Engine smoke test (1): ModuleNotFoundError
- Main wiring tests (4): ModuleNotFoundError (CORS, routes, health)

**Root Cause**: Missing modules or API wiring issues — **not related to Tier 2 work**.

**Baseline for Tier 2**: 2346 passing tests to preserve.

---

## Actual File Locations

| Component | Path | Notes |
|-----------|------|-------|
| **Node/Belief model** | `src/services/web_of_belief.py` | `Belief` dataclass (~line 485), core epistemic engine (1900+ lines) |
| **Edge/Constraint model** | `src/services/web_of_belief.py` | `Constraint` dataclass, `ConstraintType` enum (line 109) |
| **Enums** | `src/services/web_of_belief.py` | `EpistemicLevel` (87), `BeliefStatus` (100), `ConstraintType` (109), `InferenceType` (126), `BeliefKind` (145), `CausalDirection` (168) |
| **BN assembly** | `src/services/epistemic_causal_bridge.py` | ~132KB, Quinean→Pearlian bridge |
| **Extraction pipeline** | `app/tasks/pipeline.py` | Main extraction pipeline |
| **Extraction to web mapper** | `src/services/extraction_to_web.py` | Claims → Beliefs mapper (~66KB) |
| **Entrenchment/coherence** | `src/services/scalable_coherence.py` | Scalable coherence computation |
| **Entrenchment/coherence** | `src/services/web_of_belief.py` | `get_entrenchment()` method (emergent V23.0.0) |
| **Bridge warrants** | `src/services/bridge_warrants.py` | ~41KB, BridgeType enum, bridge warrant system |
| **Tests directory** | `tests/` | pytest, ~50+ test files |

---

## Key Enums (from web_of_belief.py)

```python
class EpistemicLevel(Enum):  # line 87
    THEORETICAL = "theoretical"
    INTERMEDIATE = "intermediate"
    EMPIRICAL = "empirical"
    OBSERVATIONAL = "observational"

class BeliefStatus(Enum):  # line 100
    ACTIVE = "active"
    SUSPENDED = "suspended"
    REJECTED = "rejected"
    STUB = "stub"

class ConstraintType(Enum):  # line 109
    SUPPORTS = "SUPPORTS"
    CONTRADICTS = "CONTRADICTS"
    EXPLAINS = "EXPLAINS"
    SHARED_EVIDENCE = "SHARED_EVIDENCE"
    PRECISION_BOUNDARY = "PRECISION_BOUNDARY"
    # ... (more values)

class CausalDirection(Enum):  # line 168
    UNKNOWN = "unknown"
    CORRELATIONAL = "correlational"
    FORWARD = "forward"
    REVERSE = "reverse"
    BIDIRECTIONAL = "bidirectional"
    COMMON_CAUSE = "common_cause"
    MEDIATED = "mediated"
```

---

## Key Services

| Service | Path | Purpose |
|---------|------|---------|
| `WebOfBelief` | `src/services/web_of_belief.py` | Core Quinean web, belief management |
| `EpistemicCausalBridge` | `src/services/epistemic_causal_bridge.py` | Epistemic → causal inference |
| `BridgeWarrants` | `src/services/bridge_warrants.py` | Theory-empirical bridge warrants |
| `ScalableCoherence` | `src/services/scalable_coherence.py` | Efficient coherence computation |
| `ExtractionToWeb` | `src/services/extraction_to_web.py` | Claims → beliefs integration |
| `SocialEpistemology` | `src/services/social_epistemology.py` | Community-relative credence |
| `ValidationService` | `src/services/validation.py` | Validation phases |
| `CredibilityTesting` | `src/services/credibility_testing.py` | Source credibility |
| `RankingService` | `src/services/ranking_service.py` | P2: Spohn ranks (ARCH-4) |
| `WarrantService` | `src/services/warrant_service.py` | P3: Pollock defeat (ARCH-4) |
| `GroundingService` | `src/services/grounding_service.py` | P4: Haack grounding (ARCH-4) |
| `GraphConfidenceService` | `src/services/graph_confidence_service.py` | P5: Pearl bridge (ARCH-4) |
| `EpistemicOrchestrator` | `src/services/epistemic_orchestrator.py` | P2-P6 integration (ARCH-4) |

---

## Test Framework

- **Framework**: pytest
- **Config**: `pytest.ini` (testpaths = tests)
- **Test count**: ~50+ test files in `tests/`

---

## Directory Structure (Top Level)

```
Article_Eater_PostQuinean_v1/
├── app/                    # FastAPI application
│   ├── tasks/pipeline.py   # Main extraction pipeline
│   ├── routes/             # API routes
│   └── cli/                # CLI tools
├── src/
│   └── services/           # Core services (60+ files)
│       ├── web_of_belief.py        # THE key file
│       ├── extraction_to_web.py    # Claims → beliefs
│       ├── bridge_warrants.py      # Bridge warrant system
│       ├── epistemic_causal_bridge.py  # Quinean→Pearl
│       └── ...
├── tests/                  # Test files
├── contracts/              # JSON schemas
├── docs/                   # Documentation
├── specs/                  # TLA+ specs (ARCH-4)
└── data/                   # Runtime data
```

---

## Notes for Epistemic Tier 2

1. **No separate NodeDomain enum exists** — will need to add `EPISTEMIC` domain
2. **No LinkType enum** — `ConstraintType` serves this role; will extend with epistemic link types
3. **No PathwayType enum** — will create new
4. **Belief model extensible** — uses dataclass with optional fields pattern
5. **Bridge warrant subtypes** — exist in `bridge_warrants.py`, will extend
6. **BN integration** — via `epistemic_causal_bridge.py`, not a separate BN assembly module

---

## Where to Add New Code

| New Component | Recommended Location |
|---------------|---------------------|
| New enums (PathwayType, etc.) | `src/services/web_of_belief.py` (alongside existing enums) |
| Epistemic BN nodes | `src/services/epistemic_causal_bridge.py` or new `src/epistemic/bn_nodes.py` |
| Reflexive monitors | New `src/services/monitors/` directory |
| Method registry | New `src/methods/registry.py` |
| Task-ecological validity | New `src/methods/task_ecology.py` |
