# Reflex System Architecture

**Date**: 2026-03-01
**Version**: 1.0.0
**Status**: Implemented and tested

## Executive Summary

The Reflex System implements a two-level health monitoring architecture inspired by neurological reflexes:

1. **Level 1 — Local Reflexes**: Fast, automatic, peripheral responses that detect and attempt to fix problems at the point of failure (like a spinal reflex)
2. **Level 2 — Overseer Reporting**: All reflex events (success, failure, auto-fixed) are reported upward to the overseer's health log for trend tracking and pattern analysis

This architecture prevents silent failures by ensuring every local decision is visible to the system's superordinate monitor.

---

## Architecture Overview

```
                    ┌─────────────────────────────┐
                    │    OVERSEER (Level 2)       │
                    │  Health Log + Trend Analysis│
                    │                             │
                    │ - reflex_events table       │
                    │ - Health trends query       │
                    │ - Summary statistics        │
                    └──────────────┬──────────────┘
                                   │
                                   │ (reports)
                                   │
         ┌─────────────────────────┴──────────────────────┐
         │                                                 │
    ┌────▼─────┐  ┌──────────┐  ┌──────────┐           │
    │ RFX-EXT-* │  │RFX-SCH-* │  │RFX-CAL-* │ ... (10 reflexes)
    │ (Extract) │  │(Schema)  │  │(Calibr.) │
    └────┬──────┘  └──────────┘  └──────────┘
         │                               │
         └───────────────┬───────────────┘
                         │
         ┌───────────────▼─────────────┐
         │   Local Reflex Cycle        │
         │  1. Detect(success_cond)    │
         │  2. Fix(if_possible)        │
         │  3. Report(to_overseer)     │
         └─────────────────────────────┘
```

### Principles

1. **Locality**: Reflexes run at the point where they detect a problem. No central coordination needed.
2. **Autonomy**: Each reflex can attempt auto-fix without waiting for higher-level permission.
3. **Visibility**: Every reflex action (detected, fixed, failed) is immediately reported to the overseer.
4. **Trend Awareness**: Overseer tracks patterns: are reflexes trending toward health or degradation?
5. **Graceful Degradation**: If overseer is unavailable, reflexes still execute and log locally.

---

## The 10 Reflexes

### Extraction Reflexes (RFX-EXT-*)

#### RFX-EXT-DIR: Direction Normalization
- **Condition**: Detects non-canonical directions in extraction fields
- **Canonical values**: `increase`, `decrease`, `no_effect`, `mixed`
- **Auto-fix**: Maps common misspellings/variants to canonical values
- **Success condition**: EFV-SC1

#### RFX-EXT-ANT: Vague Antecedent Detector
- **Condition**: Detects vague phrasing ("the environment", "the condition", etc.)
- **Severity**: ERROR (high-impact issue)
- **Auto-fix**: Cannot auto-fix; flags for re-extraction
- **Success condition**: EFV-SC1

#### RFX-EXT-SS: Missing Sample Size
- **Condition**: Empirical findings with null/missing `sample_size`
- **Severity**: WARNING
- **Auto-fix**: Cannot auto-fix; queues for LLM inference pass
- **Success condition**: EFV-SC1

#### RFX-EXT-JSON: Malformed Extraction JSON
- **Condition**: Extraction files that don't parse as valid JSON
- **Severity**: ERROR (data corruption risk)
- **Auto-fix**: Moves to `quarantine/` directory
- **Success condition**: EFV-SC1

#### RFX-EXT-EMPTY: Zero Findings Extraction
- **Condition**: Extractions with `n_findings == 0`
- **Severity**: WARNING (silent failure indicator)
- **Auto-fix**: Cannot auto-fix; queues for re-extraction
- **Success condition**: EFV-SC1

### Schema Reflexes (RFX-SCH-*)

#### RFX-SCH-VOCAB: Orphaned Vocabulary Terms
- **Condition**: Vocab terms that don't appear in any extraction
- **Severity**: INFO (monitoring only)
- **Auto-fix**: None; tracks for potential cleanup
- **Success condition**: LOI-SC1

#### RFX-SCH-INST: Broken Instrument ID References
- **Condition**: Instrument IDs in vocab that don't match registry
- **Severity**: WARNING (referential integrity issue)
- **Auto-fix**: Attempted fuzzy match; marks for manual review if no match
- **Success condition**: LOI-SC1

#### RFX-SCH-LOOKUP: Stale Outcome Lookup Table
- **Condition**: `outcome_lookup.json` has fewer entries than `outcome_vocab.json`
- **Severity**: WARNING
- **Auto-fix**: Regenerates lookup table from current vocab
- **Success condition**: LOI-SC1

### Calibration Reflexes (RFX-CAL-*)

#### RFX-CAL-RANGE: Out-of-Range Calibration Parameters
- **Condition**: Parameters outside plausible ranges (α ∉ [0, 1], negative weights)
- **Severity**: WARNING
- **Auto-fix**: Clamps parameters to valid ranges
- **Success condition**: OS-SC1

### Pipeline Reflexes (RFX-PIP-*)

#### RFX-PIP-STALE: Stale Extraction Files
- **Condition**: Extraction files older than 90 days without validation
- **Severity**: INFO (aging awareness)
- **Auto-fix**: None; monitoring only
- **Success condition**: SP-SC1

---

## Core Components

### `ReflexEvent` (dataclass)

Records a single reflex firing for overseer analysis.

```python
@dataclass
class ReflexEvent:
    event_id: str                          # UUID
    timestamp: str                         # ISO 8601
    reflex_id: str                         # e.g., "RFX-DIR-001"
    component: str                         # e.g., "extraction_field_validator"
    success_condition_id: str              # e.g., "EFV-SC1"
    detected: bool                         # was problem detected?
    description: str                       # what was wrong
    auto_fixed: bool                       # was it auto-fixed?
    fix_action: str                        # what fix was applied
    severity: str                          # info, warning, error, critical
    context: Dict[str, Any]                # additional context
```

### `ReflexResult` (dataclass)

Result of running a single reflex check.

```python
@dataclass
class ReflexResult:
    reflex_id: str
    passed: bool                           # success condition met
    detected_issue: bool                   # problem found?
    auto_fixed: bool                       # successfully auto-repaired?
    needs_attention: bool                  # requires human intervention?
    event: Optional[ReflexEvent] = None
```

### `Reflex` (base class)

Base class for all reflex implementations. Subclasses must implement:

```python
class Reflex:
    def detect(self) -> Tuple[bool, Dict[str, Any]]:
        """Check if success condition is violated.

        Returns:
            (problem_found, details)
        """
        raise NotImplementedError

    def fix(self, details: Dict) -> Tuple[bool, str]:
        """Attempt auto-fix if possible.

        Returns:
            (fixed, action_taken)
        """
        return False, "no_auto_fix_available"

    def run(self) -> ReflexResult:
        """Full reflex cycle: detect → fix → report."""
        # (implemented in base class)
```

### `ReflexRegistry`

Central registry that:
- Registers all reflexes
- Runs them (all or by component)
- Logs events to JSONL
- Reports to overseer DB
- Queries health trends

**Key methods**:
- `register(reflex)`: Register a reflex
- `run_all()`: Execute all reflexes
- `run_component(name)`: Run reflexes for a component
- `get_health_trends(days)`: Query overseer DB for trends
- `get_summary_stats()`: Summary statistics

---

## Integration Points

### With OVERSEER

**New method in `OverseerService`**:
```python
def get_reflex_health_summary(self) -> Dict[str, Any]:
    """Query reflex system health from overseer DB.

    Returns:
        {
            "total_events": int,
            "detected_count": int,
            "auto_fixed_count": int,
            "unresolved_count": int,
            "top_recurring_issues": List[{reflex_id, count}],
            "improving": bool or None,
            "severity_breakdown": {critical, error, warning, info}
        }
    """
```

This method should be called during:
- `periodic_audit()`: Include reflex health in nightly audit
- `post_integration_check()`: Include reflex summary in post-integration report
- Health dashboard queries

### With Success Conditions Registry

Each reflex maps to one or more success conditions from `contracts/success_conditions.json`:

| Reflex ID | Success Condition | Component |
|-----------|-------------------|-----------|
| RFX-EXT-DIR | EFV-SC1 | extraction_field_validator |
| RFX-EXT-ANT | EFV-SC1 | extraction_field_validator |
| RFX-EXT-SS | EFV-SC1 | extraction_field_validator |
| RFX-EXT-JSON | EFV-SC1 | extraction_field_validator |
| RFX-EXT-EMPTY | EFV-SC1 | extraction_field_validator |
| RFX-SCH-VOCAB | LOI-SC1 | vocabulary_manager |
| RFX-SCH-INST | LOI-SC1 | vocabulary_manager |
| RFX-SCH-LOOKUP | LOI-SC1 | vocabulary_manager |
| RFX-CAL-RANGE | OS-SC1 | calibration_manager |
| RFX-PIP-STALE | SP-SC1 | pipeline_monitor |

---

## Usage

### Running Reflexes

```bash
# Run all reflexes (detect-only mode)
python scripts/run_reflexes.py

# Run reflexes for a specific component
python scripts/run_reflexes.py --component extraction

# Run with auto-fix enabled
python scripts/run_reflexes.py --fix

# Show health trends from overseer DB
python scripts/run_reflexes.py --trends

# Show summary statistics
python scripts/run_reflexes.py --summary
```

### Programmatic Usage

```python
from src.qa.reflex_system import ReflexRegistry, DirectionNormalizationReflex
from pathlib import Path

repo_root = Path(".")
registry = ReflexRegistry(repo_root)

# Register reflexes
registry.register(DirectionNormalizationReflex(repo_root))
# ... register others

# Run all
results = registry.run_all()

for result in results:
    print(f"{result.reflex_id}: passed={result.passed}, "
          f"detected={result.detected_issue}, "
          f"fixed={result.auto_fixed}")

# Check trends
trends = registry.get_health_trends(days=7)
print(f"System improving: {trends['improving']}")
```

---

## Data Storage

### JSONL Event Logs

**Path**: `data/reflex_events/reflex_events_YYYY-MM-DD.jsonl`

Daily JSONL files where each line is a complete ReflexEvent. Used for:
- Audit trail
- Local recovery if overseer is unavailable
- Analysis and debugging

### Overseer Database

**Table**: `overseer.db.reflex_events`

```sql
CREATE TABLE reflex_events (
    event_id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    reflex_id TEXT NOT NULL,
    component TEXT NOT NULL,
    success_condition_id TEXT,
    detected INTEGER NOT NULL,
    description TEXT,
    auto_fixed INTEGER NOT NULL,
    fix_action TEXT,
    severity TEXT,
    context_json TEXT
)
```

Queries:
- Trend analysis (improving/degrading)
- Top recurring issues
- Severity breakdown
- False-alarm detection (high detection but high auto-fix rate)

---

## Severity Levels

| Level | Usage | Examples |
|-------|-------|----------|
| **INFO** | Non-blocking observations | Orphaned vocab terms, stale files |
| **WARNING** | Issues that should be fixed but don't block execution | Bad directions, missing sample sizes |
| **ERROR** | Issues that indicate data corruption or serious problems | Malformed JSON, broken references |
| **CRITICAL** | System-level failures | Unknown (reserved for future) |

---

## Failure Modes and Handling

### Reflex Execution Fails

If a reflex's `detect()` or `fix()` raises an exception:
1. Exception is caught and logged
2. A failure event is created and reported
3. Registry continues with other reflexes
4. Execution doesn't abort

### Overseer Unavailable

If reporting to overseer DB fails:
1. Event is still logged to JSONL
2. Warning is logged
3. Registry continues normally
4. Local JSONL serves as fallback audit trail

### Multiple Issues in Same File

Reflexes handle batches of issues gracefully:
- All issues detected in one pass
- Fixed in order
- Grouped by file for efficiency

---

## Future Extensions

### Predictive Health

Use historical trend data to predict:
- Which reflexes will likely trigger
- Optimal reflex scheduling
- Resource allocation

### Adaptive Thresholds

Adjust detection thresholds based on:
- Time of day (pipeline stage)
- Recent history (trending patterns)
- Data volume (scaling effects)

### Cross-Reflex Dependencies

Some issues depend on others:
- RFX-SCH-LOOKUP depends on outcome_vocab being valid
- RFX-EXT-ANT output should inform RFX-EXT-SS
- Orchestrate reflex order accordingly

### Machine Learning Integration

Use reflex event patterns to:
- Detect anomalous extraction patterns
- Predict extraction quality before full validation
- Recommend extraction parameters

---

## Testing

**Test file**: `tests/test_reflex_system.py` (23 test classes, 100+ assertions)

Coverage includes:
- Event creation and serialization
- Registry registration and execution
- All 10 concrete reflexes (detect and fix)
- Event logging to JSONL
- Overseer DB reporting
- Health trends queries
- Summary statistics
- Error handling and recovery

Run tests:
```bash
pytest tests/test_reflex_system.py -v
```

---

## References

### Inspiration and Theory

- **Dijkstra, E.W.** (1968). The structure of the "THE" multiprogramming system. *CACM* 11(5):341-346.
  - Hierarchical system monitoring
  - Watchdog processes

- **Pearl, J.** (2009). *Causality* (2nd ed.). Cambridge.
  - Causal inference and data integrity
  - Constraint satisfaction

- **Haack, S.** (1993). *Evidence and Inquiry*. Blackwell.
  - Foundherentism and provenance
  - Epistemic integrity

### Related Systems in Codebase

- `src/services/overseer.py`: Level 2 health monitor
- `contracts/success_conditions.json`: Success condition registry
- `src/qa/extraction_field_validator.py`: Field validation (uses reflexes)

---

## Implementation Notes

### Design Decisions

1. **Reflexes are Stateless**: Each reflex run is independent; no state carried between runs
2. **Events are Immutable**: Once logged, events cannot be modified
3. **Auto-fix is Optional**: Not all reflexes can auto-fix; that's okay
4. **Locality Over Centralization**: Reflexes act locally first, report centrally

### Performance Characteristics

- **Detection**: O(n) per reflex where n = number of files in target directory
- **Fixing**: O(m) where m = number of issues found
- **Reporting**: O(1) per event to overseer DB
- **Trend Queries**: O(d) where d = number of days in trend window

---

## Acknowledgments

Designed and implemented as part of Article_Eater_PostQuinean system (V22.0.0+).
Follows OVERSEER principles from expert panel review (Feb 2026).
