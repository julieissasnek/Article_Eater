"""
Article Eater - Web Accumulator (MVP Integration)
==================================================

Created: 2026-02-11
Purpose: Simple wrapper for persistent accumulated web state

This module provides:
1. JSON export of accumulated web state (for inspection/demo)
2. Event logging (events.jsonl) for debugging
3. Simple interface for MVP batch processing

The heavy lifting is done by WebPersistenceService - this is a thin wrapper
that makes it easy to use for the MVP demo.

Data Authority (per Panel Review 2026-02-11):
- SQLite (via WebPersistenceService) is the AUTHORITATIVE source of truth
- JSON export is a best-effort snapshot for inspection/debugging
- events.jsonl is append-only audit log for debugging/replay

Usage:
    from src.services.web_accumulator import WebAccumulator

    accumulator = WebAccumulator()

    # After processing a paper
    accumulator.integrate_paper(paper_web, paper_id)

    # Export for inspection
    accumulator.export_to_json()

    # Get statistics
    stats = accumulator.get_stats()
"""

import json
import logging
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

from src.services.db_locator import resolve_web_db

logger = logging.getLogger(__name__)

# Default paths
try:
    DEFAULT_DB_PATH = resolve_web_db(prefer="integrated")
except Exception:
    DEFAULT_DB_PATH = Path(os.environ.get("AE_DB_PATH", Path(__file__).parent.parent.parent / "data" / "web_persistence_v2.db"))
DEFAULT_JSON_PATH = Path(__file__).parent.parent.parent / "data" / "accumulated_web.json"
DEFAULT_EVENTS_PATH = Path(__file__).parent.parent.parent / "data" / "events.jsonl"


@dataclass
class AccumulatorEvent:
    """Event record for audit trail."""
    timestamp: str
    event_type: str  # paper_processed, belief_added, constraint_added, error, etc.
    paper_id: Optional[str]
    details: Dict[str, Any]

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)


@dataclass
class AccumulatorStats:
    """Statistics about the accumulated web."""
    total_papers_processed: int
    total_beliefs: int
    total_constraints: int
    total_bridges: int
    coherence_score: float
    last_updated: str
    beliefs_by_level: Dict[str, int]
    beliefs_by_domain: Dict[str, int]
    papers_processed: List[str] = None  # List of paper IDs

    def __post_init__(self):
        if self.papers_processed is None:
            self.papers_processed = []


class WebAccumulator:
    """
    Simple wrapper for persistent web accumulation.

    Provides MVP-friendly interface on top of WebPersistenceService.
    """

    def __init__(
        self,
        db_path: Optional[Path] = None,
        json_path: Optional[Path] = None,
        events_path: Optional[Path] = None
    ):
        """
        Initialize the accumulator.

        Args:
            db_path: Path to SQLite database (default: data/web_persistence.db)
            json_path: Path for JSON export (default: data/accumulated_web.json)
            events_path: Path for event log (default: data/events.jsonl)
        """
        self.db_path = db_path or DEFAULT_DB_PATH
        self.json_path = json_path or DEFAULT_JSON_PATH
        self.events_path = events_path or DEFAULT_EVENTS_PATH

        # Ensure data directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Lazy-load persistence service
        self._persistence = None
        self._papers_processed: List[str] = []

    @property
    def persistence(self):
        """Lazy-load WebPersistenceService."""
        if self._persistence is None:
            from src.services.web_persistence import WebPersistenceService
            self._persistence = WebPersistenceService(str(self.db_path))
            logger.info(f"Initialized WebPersistenceService at {self.db_path}")
        return self._persistence

    def _utc_now(self) -> str:
        """Get current UTC timestamp."""
        return datetime.now(timezone.utc).isoformat()

    def _log_event(self, event: AccumulatorEvent) -> None:
        """Append event to events.jsonl."""
        try:
            with open(self.events_path, 'a', encoding='utf-8') as f:
                f.write(event.to_json() + '\n')
        except Exception as e:
            logger.warning(f"Failed to log event: {e}")

    def integrate_paper(
        self,
        paper_web,  # WebOfBelief
        paper_id: str,
        bridge_registry=None,
        publication_year: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Integrate a paper's web into the accumulated master web.

        Args:
            paper_web: WebOfBelief instance from extraction
            paper_id: Paper identifier (DOI or internal ID)
            bridge_registry: Optional BridgeRegistry
            publication_year: Optional publication year

        Returns:
            Integration report dict
        """
        try:
            # Call the existing integration method
            report = self.persistence.integrate_paper_web(
                paper_web=paper_web,
                paper_id=paper_id,
                bridge_registry=bridge_registry,
                publication_year=publication_year
            )

            # Track processed papers
            if paper_id not in self._papers_processed:
                self._papers_processed.append(paper_id)

            # Log event
            event = AccumulatorEvent(
                timestamp=self._utc_now(),
                event_type="paper_processed",
                paper_id=paper_id,
                details={
                    "beliefs_added": report.n_beliefs_added,
                    "beliefs_updated": report.n_beliefs_updated,
                    "beliefs_conflicted": report.n_beliefs_conflicted,
                    "constraints_added": report.n_constraints_added,
                    "bridges_added": report.n_bridges_added,
                    "coherence_before": report.coherence_before,
                    "coherence_after": report.coherence_after,
                }
            )
            self._log_event(event)

            # Auto-export JSON after each integration
            self.export_to_json()

            logger.info(
                f"Integrated {paper_id}: +{report.n_beliefs_added} beliefs, "
                f"coherence {report.coherence_before:.3f} -> {report.coherence_after:.3f}"
            )

            return {
                "status": "success",
                "paper_id": paper_id,
                "beliefs_added": report.n_beliefs_added,
                "beliefs_updated": report.n_beliefs_updated,
                "constraints_added": report.n_constraints_added,
                "coherence_after": report.coherence_after,
            }

        except Exception as e:
            logger.error(f"Failed to integrate paper {paper_id}: {e}")

            # Log error event
            event = AccumulatorEvent(
                timestamp=self._utc_now(),
                event_type="error",
                paper_id=paper_id,
                details={"error": str(e), "error_type": type(e).__name__}
            )
            self._log_event(event)

            return {
                "status": "error",
                "paper_id": paper_id,
                "error": str(e)
            }

    def integrate_web_state_file(self, web_state_path: Path) -> Dict[str, Any]:
        """
        Integrate a web_state.json file into the accumulated web.

        Args:
            web_state_path: Path to web_state.json from pipeline run

        Returns:
            Integration report dict
        """
        from src.services.web_of_belief import (
            Belief, Constraint, Credence,
            EpistemicLevel, BeliefStatus, ConstraintType,
            create_neuroarchitecture_web
        )

        with open(web_state_path, 'r', encoding='utf-8') as f:
            state = json.load(f)

        if state.get("status") != "success":
            logger.warning(f"Skipping failed web state: {web_state_path}")
            return {"status": "skipped", "reason": "source_failed"}

        paper_id = state.get("paper_id", web_state_path.stem)

        # Reconstruct WebOfBelief from JSON
        web = create_neuroarchitecture_web()
        web.beliefs.clear()
        web.constraints.clear()

        # Load beliefs
        for bid, bdata in state.get("beliefs", {}).items():
            credence_data = bdata.get("credence", {})
            credence = Credence(
                value=credence_data.get("value", 0.5),
                uncertainty=credence_data.get("uncertainty", 0.2),  # Default meta-uncertainty
                n_supporting=credence_data.get("n_supporting", 0),
                n_contradicting=credence_data.get("n_contradicting", 0),
                n_observations=credence_data.get("n_observations", 0)
            )

            belief = Belief(
                belief_id=bdata["belief_id"],
                content=bdata["content"],
                level=EpistemicLevel[bdata["level"]],
                status=BeliefStatus[bdata["status"]],
                credence=credence,
                theory_id=bdata.get("theory_id"),
                paper_ids=bdata.get("paper_ids", []),
                domain=bdata.get("domain"),
                tags=bdata.get("tags", [])
            )
            web.beliefs[bid] = belief

        # Load constraints
        for cid, cdata in state.get("constraints", {}).items():
            constraint = Constraint(
                constraint_id=cdata["constraint_id"],
                source_id=cdata["source_id"],
                target_id=cdata["target_id"],
                constraint_type=ConstraintType[cdata["constraint_type"]],
                strength=cdata.get("strength", 0.5),
                bidirectional=cdata.get("bidirectional", False),
                evidence_ids=cdata.get("evidence_ids", []),
                warrant_type=cdata.get("warrant_type"),
                provenance=cdata.get("provenance")
            )
            web.constraints[cid] = constraint

        return self.integrate_paper(web, paper_id)

    def get_master_web(self):
        """
        Load and return the current master accumulated web.

        Returns:
            (WebOfBelief, BridgeRegistry) tuple
        """
        master_id = self.persistence.create_or_get_master_web()
        return self.persistence.load_web(master_id)

    def get_processed_paper_ids(self) -> List[str]:
        """
        Get list of paper IDs that have been successfully processed.

        Reads from the events.jsonl file to find all paper_processed events.

        Returns:
            List of paper IDs
        """
        paper_ids = set()

        # Also add in-memory tracking
        paper_ids.update(self._papers_processed)

        # Read from events log
        if self.events_path.exists():
            try:
                with open(self.events_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            try:
                                event = json.loads(line)
                                if event.get('event_type') == 'paper_processed':
                                    paper_id = event.get('paper_id')
                                    if paper_id:
                                        paper_ids.add(paper_id)
                            except json.JSONDecodeError:
                                continue
            except Exception as e:
                logger.warning(f"Error reading events log: {e}")

        return sorted(paper_ids)

    def get_stats(self) -> AccumulatorStats:
        """Get statistics about the accumulated web."""
        master_id = self.persistence.get_master_web_id()

        if not master_id:
            return AccumulatorStats(
                total_papers_processed=0,
                total_beliefs=0,
                total_constraints=0,
                total_bridges=0,
                coherence_score=0.0,
                last_updated=self._utc_now(),
                beliefs_by_level={},
                beliefs_by_domain={},
                papers_processed=self.get_processed_paper_ids()
            )

        web, bridges = self.persistence.load_web(master_id)

        if not web:
            return AccumulatorStats(
                total_papers_processed=0,
                total_beliefs=0,
                total_constraints=0,
                total_bridges=0,
                coherence_score=0.0,
                last_updated=self._utc_now(),
                beliefs_by_level={},
                beliefs_by_domain={},
                papers_processed=self.get_processed_paper_ids()
            )

        # Count by level
        beliefs_by_level = {}
        beliefs_by_domain = {}
        for belief in web.beliefs.values():
            level = belief.level.name if hasattr(belief.level, 'name') else str(belief.level)
            beliefs_by_level[level] = beliefs_by_level.get(level, 0) + 1

            domain = getattr(belief, 'domain', None) or 'unknown'
            beliefs_by_domain[domain] = beliefs_by_domain.get(domain, 0) + 1

        # Count papers from integration log
        stats_dict = self.persistence.get_statistics(master_id)
        total_papers = stats_dict.get("n_papers_integrated", len(self._papers_processed))

        coherence = web.coherence_score() if hasattr(web, 'coherence_score') else 0.0

        # Get list of processed paper IDs
        processed_papers = self.get_processed_paper_ids()

        return AccumulatorStats(
            total_papers_processed=total_papers,
            total_beliefs=len(web.beliefs),
            total_constraints=len(web.constraints),
            total_bridges=len(bridges.all()) if bridges else 0,
            coherence_score=coherence,
            last_updated=self._utc_now(),
            beliefs_by_level=beliefs_by_level,
            beliefs_by_domain=beliefs_by_domain,
            papers_processed=processed_papers
        )

    def export_to_json(self, path: Optional[Path] = None) -> Path:
        """
        Export accumulated web to JSON for inspection.

        Args:
            path: Output path (default: data/accumulated_web.json)

        Returns:
            Path to exported file
        """
        output_path = path or self.json_path
        master_id = self.persistence.get_master_web_id()

        if not master_id:
            # No accumulated web yet
            export = {
                "schema": "ae.accumulated_web.v1",
                "exported_at": self._utc_now(),
                "status": "empty",
                "n_beliefs": 0,
                "n_constraints": 0,
                "beliefs": {},
                "constraints": {}
            }
        else:
            web, bridges = self.persistence.load_web(master_id)

            if not web:
                export = {
                    "schema": "ae.accumulated_web.v1",
                    "exported_at": self._utc_now(),
                    "status": "empty",
                    "n_beliefs": 0,
                    "n_constraints": 0,
                    "beliefs": {},
                    "constraints": {}
                }
            else:
                # Serialize beliefs
                beliefs_dict = {}
                for bid, belief in web.beliefs.items():
                    beliefs_dict[bid] = {
                        "belief_id": belief.belief_id,
                        "content": belief.content,
                        "level": belief.level.name if hasattr(belief.level, 'name') else str(belief.level),
                        "status": belief.status.name if hasattr(belief.status, 'name') else str(belief.status),
                        "credence": {
                            "value": belief.credence.value,
                            "uncertainty": belief.credence.uncertainty,
                            "n_supporting": belief.credence.n_supporting,
                            "n_contradicting": belief.credence.n_contradicting,
                        },
                        "theory_id": belief.theory_id,
                        "paper_ids": getattr(belief, 'paper_ids', []),
                        "domain": getattr(belief, 'domain', None),
                        "tags": getattr(belief, 'tags', []),
                    }

                # Serialize constraints
                constraints_dict = {}
                for cid, constraint in web.constraints.items():
                    constraints_dict[cid] = {
                        "constraint_id": constraint.constraint_id,
                        "source_id": constraint.source_id,
                        "target_id": constraint.target_id,
                        "constraint_type": constraint.constraint_type.name if hasattr(constraint.constraint_type, 'name') else str(constraint.constraint_type),
                        "strength": constraint.strength,
                        "bidirectional": constraint.bidirectional,
                    }

                coherence = web.coherence_score() if hasattr(web, 'coherence_score') else 0.0
                stats = self.get_stats()

                export = {
                    "schema": "ae.accumulated_web.v1",
                    "exported_at": self._utc_now(),
                    "status": "success",
                    "master_web_id": master_id,
                    "n_papers_processed": stats.total_papers_processed,
                    "n_beliefs": len(beliefs_dict),
                    "n_constraints": len(constraints_dict),
                    "coherence_score": coherence,
                    "beliefs_by_level": stats.beliefs_by_level,
                    "beliefs_by_domain": stats.beliefs_by_domain,
                    "beliefs": beliefs_dict,
                    "constraints": constraints_dict,
                }

        # Write JSON
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export, f, indent=2, ensure_ascii=False)

        logger.info(f"Exported accumulated web to {output_path}")
        return output_path

    def clear(self, confirm: bool = False) -> bool:
        """
        Clear the accumulated web (use with caution).

        Args:
            confirm: Must be True to actually clear

        Returns:
            True if cleared, False otherwise
        """
        if not confirm:
            logger.warning("Clear requires confirm=True")
            return False

        master_id = self.persistence.get_master_web_id()
        if master_id:
            # Delete from database
            # For now, just log - actual deletion would require more code
            logger.warning(f"Would clear master web {master_id} - not implemented in MVP")

        # Clear events
        if self.events_path.exists():
            self.events_path.unlink()

        # Clear JSON export
        if self.json_path.exists():
            self.json_path.unlink()

        self._papers_processed.clear()

        event = AccumulatorEvent(
            timestamp=self._utc_now(),
            event_type="web_cleared",
            paper_id=None,
            details={}
        )
        self._log_event(event)

        return True


# =============================================================================
# CLI / UTILITY FUNCTIONS
# =============================================================================

def get_accumulator(
    db_path: Optional[str] = None,
    json_path: Optional[str] = None
) -> WebAccumulator:
    """
    Factory function to get configured accumulator.

    Args:
        db_path: Optional custom database path
        json_path: Optional custom JSON export path

    Returns:
        Configured WebAccumulator instance
    """
    return WebAccumulator(
        db_path=Path(db_path) if db_path else None,
        json_path=Path(json_path) if json_path else None
    )


def integrate_directory(
    input_dir: Path,
    accumulator: Optional[WebAccumulator] = None,
    pattern: str = "web_state*.json"
) -> Dict[str, Any]:
    """
    Integrate all web_state files from a directory.

    Args:
        input_dir: Directory containing web_state.json files
        accumulator: Optional accumulator instance
        pattern: Glob pattern for finding files

    Returns:
        Summary report
    """
    acc = accumulator or WebAccumulator()

    files = list(input_dir.glob(pattern))
    logger.info(f"Found {len(files)} web state files to integrate")

    results = {
        "total_files": len(files),
        "success": 0,
        "failed": 0,
        "skipped": 0,
        "details": []
    }

    for f in files:
        result = acc.integrate_web_state_file(f)
        results["details"].append({"file": str(f), **result})

        if result.get("status") == "success":
            results["success"] += 1
        elif result.get("status") == "skipped":
            results["skipped"] += 1
        else:
            results["failed"] += 1

    return results


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)

    acc = WebAccumulator()

    if len(sys.argv) > 1:
        cmd = sys.argv[1]

        if cmd == "stats":
            stats = acc.get_stats()
            print(f"Papers processed: {stats.total_papers_processed}")
            print(f"Total beliefs: {stats.total_beliefs}")
            print(f"Total constraints: {stats.total_constraints}")
            print(f"Coherence: {stats.coherence_score:.3f}")
            print(f"By level: {stats.beliefs_by_level}")
            print(f"By domain: {stats.beliefs_by_domain}")

        elif cmd == "export":
            path = acc.export_to_json()
            print(f"Exported to: {path}")

        elif cmd == "integrate" and len(sys.argv) > 2:
            input_path = Path(sys.argv[2])
            if input_path.is_dir():
                results = integrate_directory(input_path, acc)
                print(f"Integrated {results['success']}/{results['total_files']} files")
            elif input_path.is_file():
                result = acc.integrate_web_state_file(input_path)
                print(f"Result: {result}")
        else:
            print("Usage: python -m src.services.web_accumulator [stats|export|integrate <path>]")
    else:
        # Default: show stats
        stats = acc.get_stats()
        print(f"Accumulated Web Stats:")
        print(f"  Beliefs: {stats.total_beliefs}")
        print(f"  Constraints: {stats.total_constraints}")
        print(f"  Coherence: {stats.coherence_score:.3f}")
