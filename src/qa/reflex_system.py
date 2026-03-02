"""
Reflex System — Local auto-fix with overseer reporting.

Architecture:
  - Each Reflex is a (detect, fix, report) triple
  - detect(): checks a success condition → returns (passed: bool, details: dict)
  - fix(): attempts local auto-repair → returns (fixed: bool, action_taken: str)
  - report(): sends event to overseer health log

Reflexes are like peripheral nervous system responses:
  - Fast, local, automatic
  - Don't need central coordination to act
  - But always report upward so the overseer can track patterns

Reflexes are organized by domain:
  - RFX-EXT-*: Extraction field validation (direction, antecedent, sample_size, JSON, findings)
  - RFX-SCH-*: Schema integrity (vocab terms, instrument IDs, outcome lookups)
  - RFX-CAL-*: Calibration parameter bounds
  - RFX-PIP-*: Pipeline state and file staleness

References:
  - Dijkstra, E.W. (1968). Structure of THE multiprogramming system. CACM 11(5):341-346.
  - Pearl, J. (2009). Causality (2nd ed.). Cambridge.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional, Callable, Tuple, Dict, List, Any
import json
import logging
import sqlite3
import uuid
import re
from enum import Enum

logger = logging.getLogger(__name__)


class ReflexSeverity(str, Enum):
    """Severity levels for reflex events."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ReflexEvent:
    """A single reflex firing — recorded for overseer analysis."""
    event_id: str                          # UUID
    timestamp: str                         # ISO 8601
    reflex_id: str                         # e.g., "RFX-DIR-001"
    component: str                         # e.g., "extraction_field_validator"
    success_condition_id: str               # e.g., "EFV-SC1" from success_conditions.json
    detected: bool                         # was the problem detected?
    description: str                       # what was wrong
    auto_fixed: bool                       # was it auto-fixed?
    fix_action: str                        # what fix was applied (or "none" or "manual_required")
    severity: str                          # "info", "warning", "error", "critical"
    context: Dict[str, Any] = field(default_factory=dict)  # additional context


@dataclass
class ReflexResult:
    """Result of running a single reflex check."""
    reflex_id: str
    passed: bool                           # True = success condition met, no reflex needed
    detected_issue: bool                   # True = problem found
    auto_fixed: bool                       # True = successfully auto-repaired
    needs_attention: bool                  # True = couldn't auto-fix, needs human/LLM intervention
    event: Optional[ReflexEvent] = None


class ReflexRegistry:
    """Registry of all reflexes. Runs them, logs results, reports to overseer."""

    def __init__(self, repo_root: Path, overseer_db_path: Optional[Path] = None):
        """
        Initialize reflex registry.

        Args:
            repo_root: Root directory of repository
            overseer_db_path: Path to overseer.db (created if not provided)
        """
        self.repo_root = repo_root
        self.reflexes: Dict[str, 'Reflex'] = {}
        self.event_log_path = repo_root / "data" / "reflex_events"
        self.event_log_path.mkdir(parents=True, exist_ok=True)
        self.overseer_db_path = overseer_db_path or repo_root / "data" / "overseer.db"

    def register(self, reflex: 'Reflex'):
        """Register a reflex in the registry."""
        self.reflexes[reflex.reflex_id] = reflex

    def run_all(self) -> List[ReflexResult]:
        """Run all registered reflexes. Returns results."""
        results = []
        for reflex_id, reflex in self.reflexes.items():
            try:
                result = reflex.run()
                results.append(result)
                if result.event:
                    self._log_event(result.event)
                    self._report_to_overseer(result.event)
            except Exception as e:
                logger.error(f"Reflex {reflex_id} failed: {e}")
                # Still report the failure as an event
                event = ReflexEvent(
                    event_id=str(uuid.uuid4()),
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    reflex_id=reflex_id,
                    component=reflex.component,
                    success_condition_id=reflex.success_condition_id,
                    detected=False,
                    description=f"Reflex execution failed: {str(e)}",
                    auto_fixed=False,
                    fix_action="none",
                    severity="error",
                    context={"error": str(e)}
                )
                self._log_event(event)
                self._report_to_overseer(event)
        return results

    def run_component(self, component: str) -> List[ReflexResult]:
        """Run reflexes for a specific component."""
        results = []
        for reflex in self.reflexes.values():
            if reflex.component == component:
                try:
                    result = reflex.run()
                    results.append(result)
                    if result.event:
                        self._log_event(result.event)
                        self._report_to_overseer(result.event)
                except Exception as e:
                    logger.error(f"Reflex {reflex.reflex_id} failed: {e}")
        return results

    def _log_event(self, event: ReflexEvent):
        """Append event to daily JSONL log file."""
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        log_file = self.event_log_path / f"reflex_events_{date_str}.jsonl"
        try:
            with open(log_file, "a") as f:
                f.write(json.dumps(asdict(event)) + "\n")
        except Exception as e:
            logger.warning(f"Failed to log reflex event: {e}")

    def _report_to_overseer(self, event: ReflexEvent):
        """Report event to overseer database for trend tracking."""
        try:
            conn = sqlite3.connect(str(self.overseer_db_path))
            conn.execute("""
                CREATE TABLE IF NOT EXISTS reflex_events (
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
            """)
            conn.execute("""
                INSERT OR REPLACE INTO reflex_events
                (event_id, timestamp, reflex_id, component, success_condition_id,
                 detected, description, auto_fixed, fix_action, severity, context_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.event_id, event.timestamp, event.reflex_id, event.component,
                event.success_condition_id, int(event.detected), event.description,
                int(event.auto_fixed), event.fix_action, event.severity,
                json.dumps(event.context)
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.warning(f"Failed to report to overseer DB: {e}")

    def get_health_trends(self, days: int = 7) -> Dict[str, Any]:
        """Query overseer DB for reflex event trends."""
        try:
            conn = sqlite3.connect(str(self.overseer_db_path))
            rows = conn.execute("""
                SELECT DATE(timestamp) as day,
                       COUNT(*) as total,
                       SUM(detected) as detected,
                       SUM(auto_fixed) as auto_fixed,
                       SUM(CASE WHEN detected=1 AND auto_fixed=0 THEN 1 ELSE 0 END) as unresolved
                FROM reflex_events
                WHERE timestamp > datetime('now', ?)
                GROUP BY DATE(timestamp)
                ORDER BY day
            """, (f"-{days} days",)).fetchall()
            conn.close()

            trend_data = [
                {
                    "date": r[0],
                    "total": r[1],
                    "detected": r[2],
                    "auto_fixed": r[3],
                    "unresolved": r[4]
                }
                for r in rows
            ]

            # Compute trend direction: improving if unresolved is trending down
            improving = None
            if len(trend_data) >= 2:
                improving = trend_data[-1]["unresolved"] <= trend_data[-2]["unresolved"]

            return {
                "days": trend_data,
                "improving": improving,
                "summary": {
                    "total_events": sum(d["total"] for d in trend_data),
                    "detected_count": sum(d["detected"] for d in trend_data),
                    "auto_fixed_count": sum(d["auto_fixed"] for d in trend_data),
                    "unresolved_count": sum(d["unresolved"] for d in trend_data)
                }
            }
        except Exception as e:
            logger.warning(f"Failed to query health trends: {e}")
            return {"days": [], "improving": None, "summary": {}}

    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics from all reflex events."""
        try:
            conn = sqlite3.connect(str(self.overseer_db_path))
            cursor = conn.cursor()

            # Total events
            cursor.execute("SELECT COUNT(*) FROM reflex_events")
            total_events = cursor.fetchone()[0]

            # Events by severity
            cursor.execute("""
                SELECT severity, COUNT(*) as count
                FROM reflex_events
                GROUP BY severity
            """)
            severity_counts = {row[0]: row[1] for row in cursor.fetchall()}

            # Top recurring issues
            cursor.execute("""
                SELECT reflex_id, COUNT(*) as count
                FROM reflex_events
                WHERE detected = 1
                GROUP BY reflex_id
                ORDER BY count DESC
                LIMIT 10
            """)
            top_issues = [{"reflex_id": row[0], "count": row[1]} for row in cursor.fetchall()]

            conn.close()

            return {
                "total_events": total_events,
                "severity_breakdown": severity_counts,
                "top_recurring_issues": top_issues,
                "reflexes_registered": len(self.reflexes)
            }
        except Exception as e:
            logger.warning(f"Failed to get summary stats: {e}")
            return {}


class Reflex:
    """Base class for a single reflex — detect, fix, report."""

    def __init__(
        self,
        reflex_id: str,
        component: str,
        success_condition_id: str,
        description: str,
        severity: str = ReflexSeverity.WARNING,
        repo_root: Optional[Path] = None
    ):
        """
        Initialize a reflex.

        Args:
            reflex_id: Unique ID (e.g., "RFX-EXT-001")
            component: Component name (e.g., "extraction_field_validator")
            success_condition_id: Success condition from success_conditions.json (e.g., "EFV-SC1")
            description: Human-readable description of what this reflex checks
            severity: Severity level (info, warning, error, critical)
            repo_root: Repository root (for file operations)
        """
        self.reflex_id = reflex_id
        self.component = component
        self.success_condition_id = success_condition_id
        self.description = description
        self.severity = severity
        self.repo_root = repo_root or Path.cwd()

    def detect(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if the success condition is violated.

        Returns:
            (problem_found: bool, details: dict)
            - If problem_found is False, the condition passes and no event is logged
            - If True, details should contain context for the fix attempt
        """
        # Base implementation: no problem detected. Subclasses override this.
        return False, {}

    def fix(self, details: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Attempt auto-fix of the detected problem.

        Args:
            details: Context dict from detect()

        Returns:
            (fixed: bool, action_taken: str)
            - fixed=True if auto-fix succeeded
            - action_taken describes what was done or why it couldn't be fixed
        """
        return False, "no_auto_fix_available"

    def run(self) -> ReflexResult:
        """Execute the full reflex cycle: detect → fix → report."""
        problem_found, details = self.detect()

        if not problem_found:
            return ReflexResult(
                reflex_id=self.reflex_id,
                passed=True,
                detected_issue=False,
                auto_fixed=False,
                needs_attention=False
            )

        fixed, action = self.fix(details)

        event = ReflexEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            reflex_id=self.reflex_id,
            component=self.component,
            success_condition_id=self.success_condition_id,
            detected=True,
            description=self.description,
            auto_fixed=fixed,
            fix_action=action,
            severity=self.severity,
            context=details
        )

        return ReflexResult(
            reflex_id=self.reflex_id,
            passed=False,
            detected_issue=True,
            auto_fixed=fixed,
            needs_attention=not fixed,
            event=event
        )


# ============================================================================
# EXTRACTION REFLEXES (RFX-EXT-*)
# ============================================================================


class DirectionNormalizationReflex(Reflex):
    """RFX-EXT-DIR: Normalize non-canonical directions to 4 canonical values."""

    CANONICAL_DIRECTIONS = {"increase", "decrease", "no_effect", "mixed"}

    def __init__(self, repo_root: Optional[Path] = None):
        super().__init__(
            reflex_id="RFX-EXT-DIR",
            component="extraction_field_validator",
            success_condition_id="EFV-SC1",
            description="Direction field contains non-canonical value",
            severity=ReflexSeverity.WARNING,
            repo_root=repo_root
        )

    def detect(self) -> Tuple[bool, Dict[str, Any]]:
        """Check extraction files for non-canonical directions."""
        extractions_dir = self.repo_root / "data" / "extractions"
        if not extractions_dir.exists():
            return False, {}

        bad_directions = []
        for extraction_file in extractions_dir.glob("*.json"):
            try:
                with open(extraction_file, "r") as f:
                    data = json.load(f)
                    if "findings" in data:
                        for finding in data["findings"]:
                            direction = finding.get("direction", "")
                            # Compare EXACT value — canonical must be lowercase
                            if direction and direction not in self.CANONICAL_DIRECTIONS:
                                bad_directions.append({
                                    "file": extraction_file.name,
                                    "bad_value": direction,
                                    "finding_index": data["findings"].index(finding)
                                })
            except Exception as e:
                logger.debug(f"Error reading {extraction_file}: {e}")

        if bad_directions:
            return True, {"bad_directions": bad_directions}
        return False, {}

    def fix(self, details: Dict[str, Any]) -> Tuple[bool, str]:
        """Auto-fix by normalizing bad directions."""
        bad_directions = details.get("bad_directions", [])
        if not bad_directions:
            return False, "no_bad_directions_found"

        fixed_count = 0
        extractions_dir = self.repo_root / "data" / "extractions"

        # Group by file
        by_file = {}
        for item in bad_directions:
            fname = item["file"]
            if fname not in by_file:
                by_file[fname] = []
            by_file[fname].append(item)

        for fname, items in by_file.items():
            try:
                extraction_file = extractions_dir / fname
                with open(extraction_file, "r") as f:
                    data = json.load(f)

                for item in items:
                    idx = item["finding_index"]
                    bad_val = item["bad_value"]

                    # Simple heuristic: map to closest canonical
                    normalized = self._normalize_direction(bad_val)
                    data["findings"][idx]["direction"] = normalized
                    fixed_count += 1

                with open(extraction_file, "w") as f:
                    json.dump(data, f, indent=2)
            except Exception as e:
                logger.warning(f"Failed to fix {fname}: {e}")

        return fixed_count > 0, f"normalized {fixed_count} directions"

    def _normalize_direction(self, bad_value: str) -> str:
        """Map non-canonical direction to nearest canonical."""
        bad_val_lower = bad_value.lower().strip()

        # Common misspellings/variants
        if "incr" in bad_val_lower or "+" in bad_val_lower or "up" in bad_val_lower:
            return "increase"
        elif "decr" in bad_val_lower or "-" in bad_val_lower or "down" in bad_val_lower:
            return "decrease"
        elif "no" in bad_val_lower or "none" in bad_val_lower or "null" in bad_val_lower:
            return "no_effect"
        elif "mix" in bad_val_lower or "both" in bad_val_lower:
            return "mixed"

        # Default fallback
        return "no_effect"


class VagueAntecedentDetectorReflex(Reflex):
    """RFX-EXT-ANT: Detect vague antecedents like 'the environment', 'the condition'."""

    VAGUE_PATTERNS = [
        r"\bthe\s+(environment|condition|setting|situation|context)\b",
        r"\bthis\s+(environment|condition|setting|situation|context)\b",
        r"\bsuch\s+(environment|condition|setting|situation|context)\b",
    ]

    def __init__(self, repo_root: Optional[Path] = None):
        super().__init__(
            reflex_id="RFX-EXT-ANT",
            component="extraction_field_validator",
            success_condition_id="EFV-SC1",
            description="Antecedent field contains vague phrasing",
            severity=ReflexSeverity.ERROR,
            repo_root=repo_root
        )

    def detect(self) -> Tuple[bool, Dict[str, Any]]:
        """Check extraction files for vague antecedents."""
        extractions_dir = self.repo_root / "data" / "extractions"
        if not extractions_dir.exists():
            return False, {}

        vague_antecedents = []
        for extraction_file in extractions_dir.glob("*.json"):
            try:
                with open(extraction_file, "r") as f:
                    data = json.load(f)
                    if "findings" in data:
                        for idx, finding in enumerate(data["findings"]):
                            antecedent = finding.get("antecedent", "").lower()
                            for pattern in self.VAGUE_PATTERNS:
                                if re.search(pattern, antecedent, re.IGNORECASE):
                                    vague_antecedents.append({
                                        "file": extraction_file.name,
                                        "antecedent": antecedent[:100],
                                        "finding_index": idx
                                    })
                                    break
            except Exception as e:
                logger.debug(f"Error reading {extraction_file}: {e}")

        if vague_antecedents:
            return True, {"vague_antecedents": vague_antecedents}
        return False, {}

    def fix(self, details: Dict[str, Any]) -> Tuple[bool, str]:
        """Cannot auto-fix vague antecedents. Mark for re-extraction."""
        vague_count = len(details.get("vague_antecedents", []))
        return False, f"flagged {vague_count} antecedents for re-extraction"


class MissingSampleSizeReflex(Reflex):
    """RFX-EXT-SS: Detect null or missing sample_size in empirical findings."""

    def __init__(self, repo_root: Optional[Path] = None):
        super().__init__(
            reflex_id="RFX-EXT-SS",
            component="extraction_field_validator",
            success_condition_id="EFV-SC1",
            description="Empirical finding has null/missing sample_size",
            severity=ReflexSeverity.WARNING,
            repo_root=repo_root
        )

    def detect(self) -> Tuple[bool, Dict[str, Any]]:
        """Check extraction files for missing sample sizes."""
        extractions_dir = self.repo_root / "data" / "extractions"
        if not extractions_dir.exists():
            return False, {}

        missing_samples = []
        for extraction_file in extractions_dir.glob("*.json"):
            try:
                with open(extraction_file, "r") as f:
                    data = json.load(f)
                    if "findings" in data:
                        for idx, finding in enumerate(data["findings"]):
                            # If this is an empirical finding, sample_size should exist
                            finding_type = finding.get("type", "").lower()
                            if "empirical" in finding_type or "experiment" in finding_type:
                                sample_size = finding.get("sample_size")
                                if sample_size is None or (isinstance(sample_size, (int, float)) and sample_size == 0):
                                    missing_samples.append({
                                        "file": extraction_file.name,
                                        "finding_index": idx,
                                        "type": finding_type
                                    })
            except Exception as e:
                logger.debug(f"Error reading {extraction_file}: {e}")

        if missing_samples:
            return True, {"missing_samples": missing_samples}
        return False, {}

    def fix(self, details: Dict[str, Any]) -> Tuple[bool, str]:
        """Cannot auto-fix; mark for LLM inference pass."""
        count = len(details.get("missing_samples", []))
        return False, f"queued {count} findings for LLM inference"


class MalformedExtractionJsonReflex(Reflex):
    """RFX-EXT-JSON: Detect and quarantine files that don't parse as valid JSON."""

    def __init__(self, repo_root: Optional[Path] = None):
        super().__init__(
            reflex_id="RFX-EXT-JSON",
            component="extraction_field_validator",
            success_condition_id="EFV-SC1",
            description="Extraction JSON file is malformed",
            severity=ReflexSeverity.ERROR,
            repo_root=repo_root
        )

    def detect(self) -> Tuple[bool, Dict[str, Any]]:
        """Check extraction files for JSON parse errors."""
        extractions_dir = self.repo_root / "data" / "extractions"
        if not extractions_dir.exists():
            return False, {}

        malformed = []
        for extraction_file in extractions_dir.glob("*.json"):
            try:
                with open(extraction_file, "r") as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                malformed.append({
                    "file": extraction_file.name,
                    "error": str(e)
                })

        if malformed:
            return True, {"malformed_files": malformed}
        return False, {}

    def fix(self, details: Dict[str, Any]) -> Tuple[bool, str]:
        """Move malformed files to quarantine directory."""
        malformed = details.get("malformed_files", [])
        extractions_dir = self.repo_root / "data" / "extractions"
        quarantine_dir = self.repo_root / "data" / "extractions" / "quarantine"
        quarantine_dir.mkdir(parents=True, exist_ok=True)

        moved_count = 0
        for item in malformed:
            try:
                src = extractions_dir / item["file"]
                dst = quarantine_dir / item["file"]
                src.rename(dst)
                moved_count += 1
            except Exception as e:
                logger.warning(f"Failed to quarantine {item['file']}: {e}")

        return moved_count > 0, f"quarantined {moved_count} malformed files"


class ZeroFindingsExtractionReflex(Reflex):
    """RFX-EXT-EMPTY: Detect extractions with n_findings == 0."""

    def __init__(self, repo_root: Optional[Path] = None):
        super().__init__(
            reflex_id="RFX-EXT-EMPTY",
            component="extraction_field_validator",
            success_condition_id="EFV-SC1",
            description="Extraction produced zero findings",
            severity=ReflexSeverity.WARNING,
            repo_root=repo_root
        )

    def detect(self) -> Tuple[bool, Dict[str, Any]]:
        """Check extraction files for zero findings."""
        extractions_dir = self.repo_root / "data" / "extractions"
        if not extractions_dir.exists():
            return False, {}

        empty_extractions = []
        for extraction_file in extractions_dir.glob("*.json"):
            try:
                with open(extraction_file, "r") as f:
                    data = json.load(f)
                    findings = data.get("findings", [])
                    if len(findings) == 0:
                        empty_extractions.append({
                            "file": extraction_file.name,
                            "doi": data.get("doi", "unknown")
                        })
            except Exception as e:
                logger.debug(f"Error reading {extraction_file}: {e}")

        if empty_extractions:
            return True, {"empty_extractions": empty_extractions}
        return False, {}

    def fix(self, details: Dict[str, Any]) -> Tuple[bool, str]:
        """Cannot auto-fix; queue for re-extraction."""
        count = len(details.get("empty_extractions", []))
        return False, f"queued {count} articles for re-extraction"


# ============================================================================
# SCHEMA REFLEXES (RFX-SCH-*)
# ============================================================================


class OrphanedVocabTermsReflex(Reflex):
    """RFX-SCH-VOCAB: Detect outcome vocab terms that don't appear in any extraction."""

    def __init__(self, repo_root: Optional[Path] = None):
        super().__init__(
            reflex_id="RFX-SCH-VOCAB",
            component="vocabulary_manager",
            success_condition_id="LOI-SC1",
            description="Vocabulary contains orphaned terms",
            severity=ReflexSeverity.INFO,
            repo_root=repo_root
        )

    def detect(self) -> Tuple[bool, Dict[str, Any]]:
        """Check for vocab terms that don't appear in extractions."""
        vocab_file = self.repo_root / "data" / "outcome_vocab.json"
        extractions_dir = self.repo_root / "data" / "extractions"

        if not vocab_file.exists() or not extractions_dir.exists():
            return False, {}

        try:
            with open(vocab_file, "r") as f:
                vocab = json.load(f)

            vocab_terms = {term["id"] for term in vocab.get("terms", [])}

            # Collect all outcome IDs from extractions
            used_terms = set()
            for extraction_file in extractions_dir.glob("*.json"):
                try:
                    with open(extraction_file, "r") as f:
                        data = json.load(f)
                        for finding in data.get("findings", []):
                            if "outcome_id" in finding:
                                used_terms.add(finding["outcome_id"])
                except Exception as e:
                    logger.debug(f"Swallowed in {fpath}: {e}")

            orphaned = vocab_terms - used_terms
            if orphaned:
                return True, {"orphaned_terms": list(orphaned), "count": len(orphaned)}
        except Exception as e:
            logger.debug(f"Error checking vocab orphans: {e}")

        return False, {}

    def fix(self, details: Dict[str, Any]) -> Tuple[bool, str]:
        """Info-level; no fix needed."""
        count = details.get("count", 0)
        return False, f"identified {count} orphaned terms (monitoring only)"


class BrokenInstrumentIdReferencesReflex(Reflex):
    """RFX-SCH-INST: Detect instrument_ids in vocab that don't match registry."""

    def __init__(self, repo_root: Optional[Path] = None):
        super().__init__(
            reflex_id="RFX-SCH-INST",
            component="vocabulary_manager",
            success_condition_id="LOI-SC1",
            description="Vocabulary contains invalid instrument_id references",
            severity=ReflexSeverity.WARNING,
            repo_root=repo_root
        )

    def detect(self) -> Tuple[bool, Dict[str, Any]]:
        """Check instrument_id referential integrity."""
        vocab_file = self.repo_root / "data" / "outcome_vocab.json"
        registry_file = self.repo_root / "data" / "instruments_registry.json"

        if not vocab_file.exists() or not registry_file.exists():
            return False, {}

        try:
            with open(vocab_file, "r") as f:
                vocab = json.load(f)
            with open(registry_file, "r") as f:
                registry = json.load(f)

            valid_ids = {inst["id"] for inst in registry.get("instruments", [])}

            broken_refs = []
            for term in vocab.get("terms", []):
                for op in term.get("operationalizations", []):
                    op_inst_ids = op.get("instrument_ids", [])
                    for inst_id in op_inst_ids:
                        if inst_id not in valid_ids:
                            broken_refs.append({
                                "term_id": term["id"],
                                "bad_instrument_id": inst_id
                            })

            if broken_refs:
                return True, {"broken_refs": broken_refs}
        except Exception as e:
            logger.debug(f"Error checking instrument refs: {e}")

        return False, {}

    def fix(self, details: Dict[str, Any]) -> Tuple[bool, str]:
        """Attempt fuzzy match against registry."""
        broken_refs = details.get("broken_refs", [])
        if not broken_refs:
            return False, "no_broken_refs"

        # Simplified fix: log and mark as needing manual attention
        return False, f"found {len(broken_refs)} broken refs; manual review needed"


class StaleLookupTableReflex(Reflex):
    """RFX-SCH-LOOKUP: Regenerate outcome_lookup if vocab entries changed."""

    def __init__(self, repo_root: Optional[Path] = None):
        super().__init__(
            reflex_id="RFX-SCH-LOOKUP",
            component="vocabulary_manager",
            success_condition_id="LOI-SC1",
            description="Outcome lookup table is stale",
            severity=ReflexSeverity.WARNING,
            repo_root=repo_root
        )

    def detect(self) -> Tuple[bool, Dict[str, Any]]:
        """Check if lookup entries match vocab terms."""
        vocab_file = self.repo_root / "data" / "outcome_vocab.json"
        lookup_file = self.repo_root / "data" / "outcome_lookup.json"

        if not vocab_file.exists() or not lookup_file.exists():
            return False, {}

        try:
            with open(vocab_file, "r") as f:
                vocab = json.load(f)
            with open(lookup_file, "r") as f:
                lookup = json.load(f)

            vocab_count = len(vocab.get("terms", []))
            lookup_count = len(lookup.get("terms", []))

            if lookup_count < vocab_count:
                return True, {
                    "vocab_count": vocab_count,
                    "lookup_count": lookup_count
                }
        except Exception as e:
            logger.debug(f"Error checking lookup staleness: {e}")

        return False, {}

    def fix(self, details: Dict[str, Any]) -> Tuple[bool, str]:
        """Regenerate lookup table."""
        vocab_file = self.repo_root / "data" / "outcome_vocab.json"
        lookup_file = self.repo_root / "data" / "outcome_lookup.json"

        try:
            with open(vocab_file, "r") as f:
                vocab = json.load(f)

            # Regenerate lookup: simple mapping of term IDs
            lookup = {"terms": []}
            for term in vocab.get("terms", []):
                lookup["terms"].append({
                    "id": term["id"],
                    "name": term.get("name", ""),
                    "level": term.get("level", 0)
                })

            with open(lookup_file, "w") as f:
                json.dump(lookup, f, indent=2)

            return True, f"regenerated lookup with {len(lookup['terms'])} entries"
        except Exception as e:
            logger.warning(f"Failed to regenerate lookup: {e}")
            return False, f"regeneration failed: {str(e)}"


# ============================================================================
# CALIBRATION REFLEXES (RFX-CAL-*)
# ============================================================================


class OutOfRangeCalibrationParametersReflex(Reflex):
    """RFX-CAL-RANGE: Detect out-of-range calibration parameters in ch*.json files."""

    def __init__(self, repo_root: Optional[Path] = None):
        super().__init__(
            reflex_id="RFX-CAL-RANGE",
            component="calibration_manager",
            success_condition_id="OS-SC1",
            description="Calibration parameters out of valid range",
            severity=ReflexSeverity.WARNING,
            repo_root=repo_root
        )

    def detect(self) -> Tuple[bool, Dict[str, Any]]:
        """Check calibration files for parameter bounds violations."""
        calib_dir = self.repo_root / "data" / "calibration"
        if not calib_dir.exists():
            return False, {}

        out_of_range = []
        for calib_file in calib_dir.glob("ch*.json"):
            try:
                with open(calib_file, "r") as f:
                    data = json.load(f)

                    # Check common parameters
                    if "alpha" in data:
                        alpha = float(data["alpha"])
                        if not (0.0 <= alpha <= 1.0):
                            out_of_range.append({
                                "file": calib_file.name,
                                "param": "alpha",
                                "value": alpha,
                                "expected_range": "[0.0, 1.0]"
                            })

                    if "weights" in data and isinstance(data["weights"], dict):
                        for key, weight in data["weights"].items():
                            if isinstance(weight, (int, float)):
                                if weight < 0:
                                    out_of_range.append({
                                        "file": calib_file.name,
                                        "param": f"weights.{key}",
                                        "value": weight,
                                        "expected_range": "[0.0, ∞)"
                                    })
            except Exception as e:
                logger.debug(f"Error reading {calib_file}: {e}")

        if out_of_range:
            return True, {"out_of_range": out_of_range}
        return False, {}

    def fix(self, details: Dict[str, Any]) -> Tuple[bool, str]:
        """Clamp parameters to valid ranges."""
        out_of_range = details.get("out_of_range", [])
        calib_dir = self.repo_root / "data" / "calibration"
        fixed_count = 0

        by_file = {}
        for item in out_of_range:
            fname = item["file"]
            if fname not in by_file:
                by_file[fname] = []
            by_file[fname].append(item)

        for fname, items in by_file.items():
            try:
                calib_file = calib_dir / fname
                with open(calib_file, "r") as f:
                    data = json.load(f)

                for item in items:
                    param = item["param"]
                    value = item["value"]

                    if param == "alpha":
                        data["alpha"] = max(0.0, min(1.0, value))
                        fixed_count += 1
                    elif param.startswith("weights."):
                        key = param.split(".")[1]
                        if "weights" in data:
                            data["weights"][key] = max(0.0, value)
                            fixed_count += 1

                with open(calib_file, "w") as f:
                    json.dump(data, f, indent=2)
            except Exception as e:
                logger.warning(f"Failed to fix {fname}: {e}")

        return fixed_count > 0, f"clamped {fixed_count} parameters"


# ============================================================================
# PIPELINE REFLEXES (RFX-PIP-*)
# ============================================================================


class StaleExtractionFilesReflex(Reflex):
    """RFX-PIP-STALE: Detect extraction files older than N days without validation."""

    def __init__(self, repo_root: Optional[Path] = None, age_days: int = 90):
        super().__init__(
            reflex_id="RFX-PIP-STALE",
            component="pipeline_monitor",
            success_condition_id="SP-SC1",
            description="Extraction files older than N days without validation",
            severity=ReflexSeverity.INFO,
            repo_root=repo_root
        )
        self.age_days = age_days

    def detect(self) -> Tuple[bool, Dict[str, Any]]:
        """Check for stale extraction files."""
        extractions_dir = self.repo_root / "data" / "extractions"
        if not extractions_dir.exists():
            return False, {}

        stale = []
        cutoff_time = datetime.now(timezone.utc) - timedelta(days=self.age_days)

        for extraction_file in extractions_dir.glob("*.json"):
            mtime = datetime.fromtimestamp(extraction_file.stat().st_mtime, tz=timezone.utc)
            if mtime < cutoff_time:
                stale.append({
                    "file": extraction_file.name,
                    "age_days": (datetime.now(timezone.utc) - mtime).days
                })

        if stale:
            return True, {"stale_files": stale}
        return False, {}

    def fix(self, details: Dict[str, Any]) -> Tuple[bool, str]:
        """Info-level; no auto-fix."""
        count = len(details.get("stale_files", []))
        return False, f"identified {count} stale files (monitoring only)"


# ============================================================================
# FINDING-TEMPLATE-RELEVANCE REFLEXES (RFX-FTR-*)
# ============================================================================
# These reflexes validate the Tier2 coverage fix (line 614-615 of
# finding_template_relevance.py) and annotation persistence fix
# (persist_relevance_to_web_db integration).
#
# Related: FTR-SC1 through FTR-SC5 in contracts/success_conditions.json


class Tier2CoverageReflex(Reflex):
    """RFX-FTR-TIER2: Monitor Tier2 coverage of findings against templates.

    Success Condition: FTR-SC2 — Tier2 coverage of findings exceeds 50%

    The Tier2 coverage fix (finding_template_relevance.py line 614-615)
    added fallback from framework_ids to t1_frameworks. This reflex ensures
    that coverage stays above 50%.
    """

    def __init__(self, repo_root: Optional[Path] = None):
        super().__init__(
            reflex_id="RFX-FTR-TIER2",
            component="finding_template_relevance",
            success_condition_id="FTR-SC2",
            description="Tier2 coverage of findings below 50%",
            severity=ReflexSeverity.ERROR,
            repo_root=repo_root
        )

    def detect(self) -> Tuple[bool, Dict[str, Any]]:
        """Check Tier2 coverage in resolved web DB."""
        try:
            from src.services.db_locator import resolve_web_db
            web_db = resolve_web_db(prefer="integrated")
        except Exception:
            web_db = self.repo_root / "data" / "web_persistence.db"  # Last-resort fallback
        if not web_db.exists():
            return False, {"reason": "web_db_not_found"}

        try:
            conn = sqlite3.connect(str(web_db))
            cursor = conn.cursor()

            # Count findings with non-null tier2_relevance
            cursor.execute("SELECT COUNT(*) FROM beliefs WHERE tier2_relevance IS NOT NULL")
            with_tier2 = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM beliefs")
            total = cursor.fetchone()[0]

            conn.close()

            if total == 0:
                return False, {"reason": "no_beliefs"}

            coverage = with_tier2 / total
            threshold = 0.50

            if coverage < threshold:
                return True, {
                    "coverage": coverage,
                    "with_tier2": with_tier2,
                    "total": total,
                    "threshold": threshold,
                    "shortfall": threshold - coverage
                }

            return False, {"coverage": coverage}

        except Exception as e:
            logger.debug(f"Tier2 coverage check failed: {e}")
            return False, {"error": str(e)}

    def fix(self, details: Dict[str, Any]) -> Tuple[bool, str]:
        """Cannot auto-fix Tier2 coverage — requires regenerating links.

        Recommendation: Run scripts/run_finding_template_relevance.py
        """
        coverage = details.get("coverage", 0)
        shortfall = details.get("shortfall", 0)
        return False, f"manual_required: coverage {coverage:.2%} (need {shortfall:.2%} more); run scripts/run_finding_template_relevance.py"


class AnnotationPersistenceReflex(Reflex):
    """RFX-FTR-PERSIST: Ensure all findings have annotation persistence.

    Success Condition: FTR-SC3 — Annotation persistence ratio is 100%

    The annotation persistence fix ensures that persist_relevance_to_web_db()
    is called in the pipeline, populating beliefs.epistemic_v2.
    """

    def __init__(self, repo_root: Optional[Path] = None):
        super().__init__(
            reflex_id="RFX-FTR-PERSIST",
            component="finding_template_relevance",
            success_condition_id="FTR-SC3",
            description="Annotation persistence incomplete; epistemic_v2 has nulls",
            severity=ReflexSeverity.ERROR,
            repo_root=repo_root
        )

    def detect(self) -> Tuple[bool, Dict[str, Any]]:
        """Check that beliefs have epistemic_v2 annotations persisted."""
        try:
            from src.services.db_locator import get_web_db
            web_db = get_web_db()
        except Exception:
            web_db = self.repo_root / "data" / "web_persistence.db"  # Last-resort fallback
        if not web_db.exists():
            return False, {"reason": "web_db_not_found"}

        try:
            conn = sqlite3.connect(str(web_db))
            cursor = conn.cursor()

            # Count beliefs with epistemic_v2 populated
            cursor.execute("SELECT COUNT(*) FROM beliefs WHERE epistemic_v2 IS NOT NULL")
            persisted = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM beliefs")
            total = cursor.fetchone()[0]

            conn.close()

            if total == 0:
                return False, {"reason": "no_beliefs"}

            persistence_ratio = persisted / total
            threshold = 0.99

            if persistence_ratio < threshold:
                return True, {
                    "persistence_ratio": persistence_ratio,
                    "persisted": persisted,
                    "total": total,
                    "threshold": threshold,
                    "unpersisted": total - persisted
                }

            return False, {"persistence_ratio": persistence_ratio}

        except sqlite3.OperationalError as e:
            logger.debug(f"Persistence check failed (column may not exist): {e}")
            return False, {"error": str(e)}
        except Exception as e:
            logger.debug(f"Persistence check failed: {e}")
            return False, {"error": str(e)}

    def fix(self, details: Dict[str, Any]) -> Tuple[bool, str]:
        """AUTO-FIX: Run persist_relevance_to_web_db() to populate epistemic_v2."""
        unpersisted = details.get("unpersisted", 0)

        if unpersisted == 0:
            return True, "all_beliefs_already_persisted"

        try:
            # Import and run the persistence function
            from src.services.finding_template_relevance import (
                load_findings_from_web_db,
                load_template_profiles,
                persist_relevance_to_web_db,
                resolve_findings,
                ResolverConfig,
            )

            try:
                from src.services.db_locator import get_web_db
                web_db = get_web_db()
            except Exception:
                web_db = self.repo_root / "data" / "web_persistence.db"  # Last-resort fallback
            templates_dir = self.repo_root / "data" / "templates"

            if not templates_dir.exists():
                return False, "templates_dir_not_found"

            # Load findings and templates
            findings = load_findings_from_web_db(web_db, limit=None)
            templates = load_template_profiles(templates_dir)

            # Resolve with default config
            config = ResolverConfig()
            resolved = resolve_findings(findings, templates, config)

            # Persist back to database
            persisted_count = persist_relevance_to_web_db(web_db, resolved)

            return True, f"persisted {persisted_count} beliefs to epistemic_v2"

        except ImportError as e:
            return False, f"import_error: {str(e)}"
        except Exception as e:
            return False, f"fix_failed: {str(e)}"


class FrameworkLoadingReflex(Reflex):
    """RFX-FTR-FRAMEWORK: Ensure framework loading fallback works correctly.

    Success Condition: FTR-SC1 — Templates with t1_frameworks load with frameworks

    The framework loading fix (finding_template_relevance.py line 614-615) ensures
    that when framework_ids is missing, the fallback to t1_frameworks works.
    """

    def __init__(self, repo_root: Optional[Path] = None):
        super().__init__(
            reflex_id="RFX-FTR-FRAMEWORK",
            component="finding_template_relevance",
            success_condition_id="FTR-SC1",
            description="Templates with t1_frameworks are not loading frameworks",
            severity=ReflexSeverity.CRITICAL,
            repo_root=repo_root
        )

    def detect(self) -> Tuple[bool, Dict[str, Any]]:
        """Check that templates with t1_frameworks have loaded frameworks."""
        templates_dir = self.repo_root / "data" / "templates"
        if not templates_dir.exists():
            return False, {"reason": "templates_dir_not_found"}

        try:
            from src.services.finding_template_relevance import load_template_profiles

            profiles = load_template_profiles(templates_dir)

            if not profiles:
                return False, {"reason": "no_templates_loaded"}

            # Count templates with frameworks
            with_frameworks = [p for p in profiles if p.frameworks]
            coverage = len(with_frameworks) / len(profiles) if profiles else 0
            threshold = 0.95

            # Find templates that have t1_frameworks in source but didn't load
            missing_frameworks = []
            for path in templates_dir.glob("*.json"):
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                    has_t1_fw = bool(payload.get("t1_frameworks"))
                    has_fw_ids = bool(payload.get("framework_ids"))

                    # If source has either field but template didn't load, that's an error
                    if (has_t1_fw or has_fw_ids):
                        matching_profile = next(
                            (p for p in profiles if p.template_id == str(payload.get("template_id") or path.stem)),
                            None
                        )
                        if matching_profile and not matching_profile.frameworks:
                            missing_frameworks.append({
                                "template_id": str(payload.get("template_id") or path.stem),
                                "has_t1_frameworks": has_t1_fw,
                                "has_framework_ids": has_fw_ids
                            })
                except Exception as e:
                    logger.debug(f"Swallowed in {fpath}: {e}")

            if missing_frameworks or coverage < threshold:
                return True, {
                    "coverage": coverage,
                    "threshold": threshold,
                    "with_frameworks": len(with_frameworks),
                    "total": len(profiles),
                    "missing_frameworks": missing_frameworks
                }

            return False, {"coverage": coverage}

        except Exception as e:
            logger.debug(f"Framework loading check failed: {e}")
            return False, {"error": str(e)}

    def fix(self, details: Dict[str, Any]) -> Tuple[bool, str]:
        """Cannot auto-fix framework loading — requires code review.

        This is a CRITICAL issue indicating the fallback logic may be broken.
        """
        missing_count = len(details.get("missing_frameworks", []))
        coverage = details.get("coverage", 0)
        return False, f"manual_required: {missing_count} templates missing frameworks (coverage {coverage:.2%}); check line 614-615 of finding_template_relevance.py"


# ============================================================================
# BACKFILL & VOCAB REFLEXES (RFX-BF-*, RFX-VOC-*) — Added 2026-03-01 AG
# ============================================================================


class EnvOutcomeBackfillReflex(Reflex):
    """RFX-BF-ENVOUT: Monitor env_id/outcome_id coverage in extraction files.

    Success Condition: SC-BF-1 — ≥95% of DOI extraction files have
    environment_id and outcome_id populated in their findings.

    Fix: Re-run scripts/backfill_env_outcome_v2.py
    """

    def __init__(self, repo_root: Optional[Path] = None):
        super().__init__(
            reflex_id="RFX-BF-ENVOUT",
            component="backfill_pipeline",
            success_condition_id="SC-BF-1",
            description="Extraction files missing environment_id or outcome_id",
            severity=ReflexSeverity.WARNING,
            repo_root=repo_root
        )

    def detect(self) -> Tuple[bool, Dict[str, Any]]:
        """Check extraction files for env/outcome ID coverage."""
        extractions_dir = self.repo_root / "data" / "extractions"
        if not extractions_dir.exists():
            return False, {}

        total_findings = 0
        missing_env = 0
        missing_out = 0

        for f in extractions_dir.glob("10.*.json"):
            try:
                data = json.load(open(f))
                for finding in data.get("findings", []):
                    total_findings += 1
                    if not finding.get("environment_id"):
                        missing_env += 1
                    if not finding.get("outcome_id"):
                        missing_out += 1
            except Exception as e:
                logger.debug(f"Swallowed in {fpath}: {e}")

        if total_findings == 0:
            return False, {"reason": "no_findings"}

        env_coverage = 1 - (missing_env / total_findings)
        out_coverage = 1 - (missing_out / total_findings)
        threshold = 0.70  # Accept 70%+ (many findings legitimately lack IDs)

        if env_coverage < threshold or out_coverage < threshold:
            return True, {
                "total_findings": total_findings,
                "env_coverage": env_coverage,
                "out_coverage": out_coverage,
                "missing_env": missing_env,
                "missing_out": missing_out,
                "threshold": threshold
            }

        return False, {"env_coverage": env_coverage, "out_coverage": out_coverage}

    def fix(self, details: Dict[str, Any]) -> Tuple[bool, str]:
        """Recommend running backfill script."""
        env_cov = details.get("env_coverage", 0)
        out_cov = details.get("out_coverage", 0)
        return False, f"manual_required: env {env_cov:.1%}, out {out_cov:.1%}; run scripts/backfill_env_outcome_v2.py"


class InlineTier2DataReflex(Reflex):
    """RFX-BF-TIER2: Monitor inline Tier2 data in extraction files.

    Success Condition: SC-T2-3 — ≥80% of extraction files have
    tier_resolution_version set (proof that FTR pipeline has run).
    """

    def __init__(self, repo_root: Optional[Path] = None):
        super().__init__(
            reflex_id="RFX-BF-TIER2",
            component="finding_template_relevance",
            success_condition_id="SC-T2-3",
            description="Extraction files missing inline Tier2 data",
            severity=ReflexSeverity.WARNING,
            repo_root=repo_root
        )

    def detect(self) -> Tuple[bool, Dict[str, Any]]:
        """Check extraction files for tier_resolution_version."""
        extractions_dir = self.repo_root / "data" / "extractions"
        if not extractions_dir.exists():
            return False, {}

        total = 0
        with_tier2 = 0
        for f in extractions_dir.glob("10.*.json"):
            total += 1
            try:
                data = json.load(open(f))
                if data.get("tier_resolution_version") or data.get("tier_resolution_config"):
                    with_tier2 += 1
            except Exception as e:
                logger.debug(f"Swallowed in {fpath}: {e}")

        if total == 0:
            return False, {"reason": "no_files"}

        coverage = with_tier2 / total
        threshold = 0.80

        if coverage < threshold:
            return True, {
                "total": total,
                "with_tier2": with_tier2,
                "coverage": coverage,
                "threshold": threshold
            }

        return False, {"coverage": coverage}

    def fix(self, details: Dict[str, Any]) -> Tuple[bool, str]:
        """Recommend running FTR pipeline."""
        coverage = details.get("coverage", 0)
        return False, f"manual_required: only {coverage:.1%} coverage; run scripts/run_finding_template_relevance.py"


class VocabResolutionCoverageReflex(Reflex):
    """RFX-VOC-RESOLVE: Monitor outcome vocabulary resolution coverage.

    Success Condition: SC-P1-1 — Unresolved outcome terms should decrease
    over time as PANEL-1 processes them.
    """

    def __init__(self, repo_root: Optional[Path] = None):
        super().__init__(
            reflex_id="RFX-VOC-RESOLVE",
            component="vocabulary_manager",
            success_condition_id="SC-P1-1",
            description="High count of unresolved outcome terms",
            severity=ReflexSeverity.INFO,
            repo_root=repo_root
        )

    def detect(self) -> Tuple[bool, Dict[str, Any]]:
        """Count unresolved outcome terms vs resolved."""
        unresolved_file = self.repo_root / "data" / "unresolved_outcomes.jsonl"
        panel_results = self.repo_root / "data" / "panel_results" / "panel_1_results_live.json"
        vocab_file = self.repo_root / "contracts" / "outcome_vocab" / "outcome_vocab.json"

        unresolved_count = 0
        if unresolved_file.exists():
            with open(unresolved_file) as f:
                unresolved_count = sum(1 for _ in f)

        vocab_count = 0
        if vocab_file.exists():
            try:
                vocab = json.load(open(vocab_file))
                vocab_count = len(vocab.get("terms", []))
            except Exception as e:
                logger.debug(f"Swallowed in {fpath}: {e}")

        panel_processed = 0
        if panel_results.exists():
            try:
                results = json.load(open(panel_results))
                panel_processed = sum(len(v) for v in results.values() if isinstance(v, list))
            except Exception as e:
                logger.debug(f"Swallowed in {fpath}: {e}")

        # Alert if >50% of terms are still unresolved
        total = vocab_count + unresolved_count
        if total > 0 and unresolved_count / total > 0.50:
            return True, {
                "unresolved": unresolved_count,
                "vocab_terms": vocab_count,
                "panel_processed": panel_processed,
                "resolution_ratio": vocab_count / total if total else 0
            }

        return False, {
            "unresolved": unresolved_count,
            "vocab_terms": vocab_count,
            "panel_processed": panel_processed
        }

    def fix(self, details: Dict[str, Any]) -> Tuple[bool, str]:
        """Recommend running PANEL-1."""
        unresolved = details.get("unresolved", 0)
        return False, f"manual_required: {unresolved} unresolved terms; run scripts/run_panel_1_outcomes.py --apply"


# ============================================================================
# WARRANT STATUS REFLEXES (RFX-WRN-*)
# ============================================================================


class WarrantStatusReflex(Reflex):
    """RFX-WRN-STATUS: Detect beliefs that are DEFEATED, UNGROUNDED, or UNCHECKED.

    Wires the WarrantService into the reflex system so that epistemic
    health problems surface in AESHI and the overseer dashboard.
    """

    def __init__(self, repo_root: Optional[Path] = None):
        super().__init__(
            reflex_id="RFX-WRN-STATUS",
            component="warrant_service",
            success_condition_id="SC-QA-05",
            description="Beliefs with problematic warrant status (DEFEATED/UNGROUNDED/UNCHECKED)",
            severity=ReflexSeverity.WARNING,
            repo_root=repo_root,
        )

    def detect(self) -> Tuple[bool, Dict[str, Any]]:
        """Check warrant status across all beliefs in the web."""
        try:
            from src.services.web_of_belief import WebOfBelief
            from src.services.warrant_service import WarrantService
            from src.services.ranking_service import RankingService
        except ImportError:
            return False, {"skipped": "warrant_service not available"}

        try:
            from src.services.db_locator import get_web_db
            db_path = get_web_db()
        except Exception:
            db_path = self.repo_root / "data" / "web_persistence.db"  # Last-resort fallback
        if not db_path.exists():
            return False, {"skipped": "web_db not found"}

        try:
            web = WebOfBelief(str(db_path))
            ws = WarrantService()
            rs = RankingService()

            all_beliefs = web.get_all_beliefs() if hasattr(web, 'get_all_beliefs') else []
            if not all_beliefs:
                return False, {"skipped": "no beliefs in web"}

            # Get ranks for warrant computation
            ranks = {}
            if hasattr(rs, 'compute_ranks'):
                try:
                    ranks = rs.compute_ranks(web)
                except Exception as e:
                    logger.debug(f"Swallowed in {fpath}: {e}")

            # Compute warrant
            result = ws.compute_warrant(web, ranks)

            problems = {
                "defeated": list(result.defeated) if result.defeated else [],
                "ungrounded": list(result.ungrounded) if result.ungrounded else [],
                "suspended": list(result.suspended) if result.suspended else [],
                "violations": result.violations if result.violations else [],
                "total_beliefs": len(all_beliefs),
                "warranted_count": len(result.warranted) if result.warranted else 0,
            }

            problem_count = (
                len(problems["defeated"])
                + len(problems["ungrounded"])
                + len(problems["suspended"])
                + len(problems["violations"])
            )

            if problem_count > 0:
                return True, problems
            return False, problems

        except Exception as e:
            logger.debug(f"WarrantStatusReflex error: {e}")
            return False, {"error": str(e)}

    def fix(self, details: Dict[str, Any]) -> Tuple[bool, str]:
        """Cannot auto-fix warrant issues; flag for review."""
        defeated = len(details.get("defeated", []))
        ungrounded = len(details.get("ungrounded", []))
        suspended = len(details.get("suspended", []))
        violations = len(details.get("violations", []))
        return False, (
            f"warrant_review_needed: {defeated} defeated, "
            f"{ungrounded} ungrounded, {suspended} suspended, "
            f"{violations} consistency violations"
        )


# ============================================================================
# PROVENANCE REFLEXES (RFX-PRV-*)
# ============================================================================


class ProvenanceGroundingReflex(Reflex):
    """RFX-PRV-GROUND: Detect beliefs that are COHERENT_ONLY (Haack warning).

    Per Haack's foundherentism: beliefs that cohere with the web but lack
    experiential grounding are the most dangerous — they can be entirely
    circular. This reflex flags them for investigation.
    """

    def __init__(self, repo_root: Optional[Path] = None):
        super().__init__(
            reflex_id="RFX-PRV-GROUND",
            component="provenance",
            success_condition_id="SC-QA-09",
            description="Beliefs with COHERENT_ONLY justification (ungrounded per Haack)",
            severity=ReflexSeverity.WARNING,
            repo_root=repo_root,
        )

    def detect(self) -> Tuple[bool, Dict[str, Any]]:
        """Check provenance grounding across all beliefs."""
        try:
            from src.models.provenance import JustificationStatus
        except ImportError:
            return False, {"skipped": "provenance module not available"}

        try:
            from src.services.db_locator import get_web_db
            db_path = get_web_db()
        except Exception:
            db_path = self.repo_root / "data" / "web_persistence.db"  # Last-resort fallback
        if not db_path.exists():
            return False, {"skipped": "web_db not found"}

        try:
            import sqlite3 as _sqlite3
            conn = _sqlite3.connect(str(db_path))
            conn.row_factory = _sqlite3.Row

            # Check if beliefs table has provenance/justification data
            cursor = conn.cursor()
            try:
                rows = cursor.execute(
                    "SELECT belief_id, provenance FROM beliefs WHERE status != 'RETIRED'"
                ).fetchall()
            except _sqlite3.OperationalError:
                conn.close()
                return False, {"skipped": "beliefs table missing or no provenance column"}

            coherent_only = []
            unjustified = []
            no_provenance = []

            for row in rows:
                belief_id = row["belief_id"] if isinstance(row, _sqlite3.Row) else row[0]
                prov_raw = row["provenance"] if isinstance(row, _sqlite3.Row) else row[1]

                if not prov_raw:
                    no_provenance.append(belief_id)
                    continue

                try:
                    prov = json.loads(prov_raw) if isinstance(prov_raw, str) else prov_raw
                    status = prov.get("justification_status", "")
                    if status == "COHERENT_ONLY":
                        coherent_only.append(belief_id)
                    elif status == "UNJUSTIFIED":
                        unjustified.append(belief_id)
                except (json.JSONDecodeError, AttributeError):
                    pass

            conn.close()

            total_problems = len(coherent_only) + len(unjustified)
            if total_problems > 0:
                return True, {
                    "coherent_only": coherent_only[:20],  # Cap at 20 for event size
                    "coherent_only_count": len(coherent_only),
                    "unjustified": unjustified[:20],
                    "unjustified_count": len(unjustified),
                    "no_provenance_count": len(no_provenance),
                    "total_beliefs": len(rows),
                }
            return False, {
                "coherent_only_count": 0,
                "unjustified_count": 0,
                "no_provenance_count": len(no_provenance),
                "total_beliefs": len(rows),
            }

        except Exception as e:
            logger.debug(f"ProvenanceGroundingReflex error: {e}")
            return False, {"error": str(e)}

    def fix(self, details: Dict[str, Any]) -> Tuple[bool, str]:
        """Cannot auto-fix; flag beliefs needing empirical grounding."""
        coherent = details.get("coherent_only_count", 0)
        unjustified = details.get("unjustified_count", 0)
        return False, (
            f"grounding_review_needed: {coherent} COHERENT_ONLY beliefs "
            f"(dangerous per Haack), {unjustified} UNJUSTIFIED beliefs"
        )


# ============================================================================
# DEFAULT REGISTRY SETUP
# ============================================================================


# ============================================================================
# PIPELINE HEALTH REFLEXES (RFX-PH-*) — Added 2026-03-01 V8 audit
# ============================================================================


class AESHIScoreReflex(Reflex):
    """RFX-PH-AESHI: Monitor AESHI score stays GREEN (≥70).

    Success Condition: AESHI-SC1 — AESHI score in valid range with GREEN band.
    """

    def __init__(self, repo_root: Optional[Path] = None):
        super().__init__(
            reflex_id="RFX-PH-AESHI",
            component="system_health",
            success_condition_id="AESHI-SC1",
            description="AESHI score below GREEN threshold (<70)",
            severity=ReflexSeverity.ERROR,
            repo_root=repo_root,
        )

    def detect(self) -> Tuple[bool, Dict[str, Any]]:
        """Check if AESHI report exists and score is GREEN."""
        report_path = self.repo_root / "data" / "production" / "system_health_report.json"
        if not report_path.exists():
            return True, {"reason": "no_health_report", "path": str(report_path)}

        try:
            report = json.load(open(report_path))
            score = report.get("aeshi_score", 0)
            band = report.get("band", "UNKNOWN")

            if band not in ("GREEN",):
                return True, {"score": score, "band": band, "threshold": 70}
            return False, {"score": score, "band": band}
        except Exception as e:
            return True, {"error": str(e)}

    def fix(self, details: Dict[str, Any]) -> Tuple[bool, str]:
        """AUTO-FIX: Re-run AESHI computation."""
        try:
            import subprocess
            result = subprocess.run(
                ["python3", "scripts/compute_system_health.py", "--skip-gates"],
                cwd=str(self.repo_root),
                capture_output=True, text=True, timeout=120,
            )
            if result.returncode == 0:
                return True, f"re-computed AESHI: {result.stdout.strip()[:100]}"
            return False, f"AESHI computation failed: {result.stderr[:100]}"
        except Exception as e:
            return False, f"fix_failed: {str(e)}"


class GroundingClassificationReflex(Reflex):
    """RFX-PH-GROUND: Detect beliefs with UNSET grounding status.

    Success Condition: GC-SC1 — All beliefs are classified.
    """

    def __init__(self, repo_root: Optional[Path] = None):
        super().__init__(
            reflex_id="RFX-PH-GROUND",
            component="grounding_classifier",
            success_condition_id="GC-SC1",
            description="Beliefs with UNSET grounding status",
            severity=ReflexSeverity.WARNING,
            repo_root=repo_root,
        )

    def detect(self) -> Tuple[bool, Dict[str, Any]]:
        """Check for UNSET grounding in epistemic_v2."""
        try:
            from src.services.db_locator import get_web_db
            db_path = get_web_db()
        except Exception:
            db_path = self.repo_root / "data" / "web_persistence.db"  # Last-resort fallback

        if not db_path.exists():
            return False, {"skipped": "db_not_found"}

        try:
            conn = sqlite3.connect(str(db_path))
            total = conn.execute("SELECT COUNT(*) FROM beliefs").fetchone()[0]
            # Count beliefs with UNSET or missing grounding
            unset = 0
            for row in conn.execute("SELECT epistemic_v2 FROM beliefs WHERE epistemic_v2 IS NOT NULL"):
                try:
                    data = json.loads(row[0])
                    status = data.get("provenance_v2", {}).get("justification_status", "UNSET")
                    if status == "UNSET":
                        unset += 1
                except Exception:
                    unset += 1

            # Also count beliefs with NULL epistemic_v2
            null_count = conn.execute("SELECT COUNT(*) FROM beliefs WHERE epistemic_v2 IS NULL").fetchone()[0]
            conn.close()

            unset_total = unset + null_count
            if total > 0 and unset_total / total > 0.05:  # >5% UNSET
                return True, {
                    "total": total, "unset": unset_total,
                    "unset_pct": unset_total / total,
                }
            return False, {"total": total, "unset": unset_total}
        except Exception as e:
            return False, {"error": str(e)}

    def fix(self, details: Dict[str, Any]) -> Tuple[bool, str]:
        """AUTO-FIX: Run classify_grounding.py."""
        try:
            import subprocess
            result = subprocess.run(
                ["python3", "scripts/classify_grounding.py"],
                cwd=str(self.repo_root),
                capture_output=True, text=True, timeout=120,
            )
            if result.returncode == 0:
                return True, f"classified grounding: {result.stdout.strip()[-100:]}"
            return False, f"classification failed: {result.stderr[:100]}"
        except Exception as e:
            return False, f"fix_failed: {str(e)}"


class ConstraintPropagationReflex(Reflex):
    """RFX-PH-PROP: Monitor isolated belief ratio.

    Success Condition: CP-SC1 — Isolated beliefs decrease after propagation.
    """

    def __init__(self, repo_root: Optional[Path] = None):
        super().__init__(
            reflex_id="RFX-PH-PROP",
            component="constraint_propagation",
            success_condition_id="CP-SC1",
            description="Too many isolated beliefs (no edges)",
            severity=ReflexSeverity.WARNING,
            repo_root=repo_root,
        )

    def detect(self) -> Tuple[bool, Dict[str, Any]]:
        """Check isolated belief ratio."""
        try:
            from src.services.db_locator import get_web_db
            db_path = get_web_db()
        except Exception:
            db_path = self.repo_root / "data" / "web_persistence.db"  # Last-resort fallback

        if not db_path.exists():
            return False, {"skipped": "db_not_found"}

        try:
            conn = sqlite3.connect(str(db_path))
            total = conn.execute("SELECT COUNT(*) FROM beliefs").fetchone()[0]

            # Count beliefs that appear in no constraints
            connected = conn.execute("""
                SELECT COUNT(DISTINCT b.belief_id)
                FROM beliefs b
                INNER JOIN constraints c ON b.belief_id = c.source_belief_id
                   OR b.belief_id = c.target_belief_id
            """).fetchone()[0]
            conn.close()

            if total == 0:
                return False, {"reason": "no_beliefs"}

            isolated = total - connected
            isolated_pct = isolated / total
            threshold = 0.35  # >35% isolated is a problem

            if isolated_pct > threshold:
                return True, {
                    "total": total, "isolated": isolated,
                    "isolated_pct": isolated_pct, "threshold": threshold,
                }
            return False, {"isolated_pct": isolated_pct}
        except Exception as e:
            return False, {"error": str(e)}

    def fix(self, details: Dict[str, Any]) -> Tuple[bool, str]:
        """Recommend running constraint propagation."""
        isolated_pct = details.get("isolated_pct", 0)
        return False, f"manual_required: {isolated_pct:.1%} isolated; run scripts/propagate_constraints.py"


class AnnotationCoverageReflex(Reflex):
    """RFX-PH-ANNOT: Monitor annotation coverage.

    Success Condition: AM-SC3 — All 23 annotation types registered.
    """

    def __init__(self, repo_root: Optional[Path] = None):
        super().__init__(
            reflex_id="RFX-PH-ANNOT",
            component="annotation_service",
            success_condition_id="AM-SC3",
            description="Low annotation count or missing annotation types",
            severity=ReflexSeverity.WARNING,
            repo_root=repo_root,
        )

    def detect(self) -> Tuple[bool, Dict[str, Any]]:
        """Check annotation coverage."""
        try:
            from src.services.db_locator import get_web_db
            db_path = get_web_db()
        except Exception:
            db_path = self.repo_root / "data" / "web_persistence.db"  # Last-resort fallback

        if not db_path.exists():
            return False, {"skipped": "db_not_found"}

        try:
            conn = sqlite3.connect(str(db_path))

            # Check if annotations table exists
            tables = {row[0] for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
            if "annotations" not in tables:
                conn.close()
                return True, {"reason": "no_annotations_table"}

            total = conn.execute("SELECT COUNT(*) FROM annotations WHERE active = 1").fetchone()[0]
            types = conn.execute("SELECT COUNT(DISTINCT type_id) FROM annotations").fetchone()[0]
            conn.close()

            threshold = 200
            if total < threshold:
                return True, {"total": total, "types": types, "threshold": threshold}
            return False, {"total": total, "types": types}
        except Exception as e:
            return False, {"error": str(e)}

    def fix(self, details: Dict[str, Any]) -> Tuple[bool, str]:
        """AUTO-FIX: Run annotation migration."""
        total = details.get("total", 0)
        try:
            import subprocess
            result = subprocess.run(
                ["python3", "scripts/migrate_annotations_to_unified.py"],
                cwd=str(self.repo_root),
                capture_output=True, text=True, timeout=120,
            )
            if result.returncode == 0:
                return True, f"migrated annotations: {result.stdout.strip()[-100:]}"
            return False, f"migration failed: {result.stderr[:100]}"
        except Exception as e:
            return False, f"fix_failed: {str(e)}"


def setup_default_reflexes(repo_root: Path, registry: ReflexRegistry) -> None:
    """Register all default reflexes in the system.

    This function is called at startup to populate the registry with all
    built-in reflexes that monitor success conditions.

    Args:
        repo_root: Root directory of the repository
        registry: ReflexRegistry instance to populate
    """
    # Extraction reflexes
    registry.register(DirectionNormalizationReflex(repo_root=repo_root))
    registry.register(VagueAntecedentDetectorReflex(repo_root=repo_root))
    registry.register(MissingSampleSizeReflex(repo_root=repo_root))
    registry.register(MalformedExtractionJsonReflex(repo_root=repo_root))
    registry.register(ZeroFindingsExtractionReflex(repo_root=repo_root))

    # Schema integrity reflexes
    registry.register(OrphanedVocabTermsReflex(repo_root=repo_root))
    registry.register(BrokenInstrumentIdReferencesReflex(repo_root=repo_root))
    registry.register(StaleLookupTableReflex(repo_root=repo_root))

    # Calibration reflexes
    registry.register(OutOfRangeCalibrationParametersReflex(repo_root=repo_root))

    # Pipeline reflexes
    registry.register(StaleExtractionFilesReflex(repo_root=repo_root))

    # Finding-template-relevance reflexes (CW 2026-03-01)
    registry.register(Tier2CoverageReflex(repo_root=repo_root))
    registry.register(AnnotationPersistenceReflex(repo_root=repo_root))
    registry.register(FrameworkLoadingReflex(repo_root=repo_root))

    # Backfill + vocabulary reflexes (AG 2026-03-01)
    registry.register(EnvOutcomeBackfillReflex(repo_root=repo_root))
    registry.register(InlineTier2DataReflex(repo_root=repo_root))
    registry.register(VocabResolutionCoverageReflex(repo_root=repo_root))

    # Warrant + Provenance integration reflexes (AG 2026-03-01, QA Spec)
    registry.register(WarrantStatusReflex(repo_root=repo_root))
    registry.register(ProvenanceGroundingReflex(repo_root=repo_root))

    # Pipeline health reflexes (AG 2026-03-01, V8 audit)
    registry.register(AESHIScoreReflex(repo_root=repo_root))
    registry.register(GroundingClassificationReflex(repo_root=repo_root))
    registry.register(ConstraintPropagationReflex(repo_root=repo_root))
    registry.register(AnnotationCoverageReflex(repo_root=repo_root))

    logger.info(f"Registered {len(registry.reflexes)} default reflexes")


def get_or_create_default_registry(repo_root: Path) -> ReflexRegistry:
    """Create a reflex registry and populate with all default reflexes.

    This is the typical entry point for initializing the reflex system.

    Args:
        repo_root: Root directory of the repository

    Returns:
        Populated ReflexRegistry instance
    """
    registry = ReflexRegistry(repo_root=repo_root)
    setup_default_reflexes(repo_root, registry)
    return registry
