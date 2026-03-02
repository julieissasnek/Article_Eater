"""
Integration Rollback — Paper-level undo via pre-integration snapshots
=====================================================================

Created: 2026-02-25
Sprint: INTEGRATION-1

Provides paper-level undo for the integration pipeline. When an older
interpretation of a paper is preferred, or a paper's integration was
erroneous, the system can be rolled back to its pre-integration state
for that specific paper.

Mechanism:
1. Look up the PaperIntegrationEvent for the target paper
2. Load the pre-integration snapshot
3. Diff current state against pre-snapshot
4. Remove only beliefs/constraints contributed by that paper
5. Re-invalidate affected molecule caches, BN params, tags
6. Record the rollback as a new integration event

This leverages web_persistence.py's existing snapshot system for
disaster recovery, repurposed for surgical paper-level rollback.

Design Decision (D-INT-1): We do NOT restore from snapshot wholesale.
Instead, we remove the specific paper's contributions. This preserves
other papers' contributions that may have been added since the integration.
"""

from __future__ import annotations

import logging
import sqlite3
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

from src.services.paper_integration.models import (
    PaperIntegrationEvent,
    IntegrationAction,
    IntegrationStatus,
    CascadeStep,
    CascadeStepStatus,
)

logger = logging.getLogger(__name__)


class IntegrationRollback:
    """
    Rolls back a paper's integration by removing its specific contributions.

    Uses the PaperIntegrationEvent audit record to know exactly which
    beliefs, constraints, tags, and BN edges were added during integration.
    """

    def __init__(self, db_conn: sqlite3.Connection):
        self.db_conn = db_conn

    def rollback_paper(
        self,
        paper_id: str,
        reason: str = "Manual rollback requested",
    ) -> PaperIntegrationEvent:
        """
        Roll back all integration effects for a given paper.

        Args:
            paper_id: The paper whose integration to undo
            reason: Why the rollback is being performed

        Returns:
            A new PaperIntegrationEvent with action=ROLLBACK

        Raises:
            ValueError: If no completed integration event found for paper
        """
        # Find the most recent COMPLETED integration for this paper
        original_event = self._find_integration_event(paper_id)
        if original_event is None:
            raise ValueError(
                f"No completed integration event found for paper {paper_id}"
            )

        logger.info(
            "Rolling back paper %s (event %s)", paper_id, original_event.event_id
        )

        # Create the rollback event
        rollback_event = PaperIntegrationEvent(
            paper_id=paper_id,
            action=IntegrationAction.ROLLBACK,
            rollback_of_event_id=original_event.event_id,
        )
        rollback_event.mark_in_progress()

        steps = []

        # Step 1: Remove beliefs added by this paper
        step_beliefs = CascadeStep(
            step_number=1,
            step_name="remove_beliefs",
            is_critical=True,
        )
        step_beliefs.start()
        try:
            removed = self._remove_beliefs(original_event.beliefs_added, paper_id)
            step_beliefs.complete(items_processed=removed)
            rollback_event.beliefs_retired = original_event.beliefs_added
        except Exception as e:
            step_beliefs.fail(str(e))
            rollback_event.mark_failed(f"Belief removal failed: {e}")
            steps.append(step_beliefs)
            rollback_event.cascade_steps = steps
            self._persist_event(rollback_event)
            return rollback_event
        steps.append(step_beliefs)

        # Step 2: Remove constraints added by this paper
        step_constraints = CascadeStep(
            step_number=2,
            step_name="remove_constraints",
            is_critical=True,
        )
        step_constraints.start()
        try:
            removed = self._remove_constraints(
                original_event.constraints_added, paper_id
            )
            step_constraints.complete(items_processed=removed)
            rollback_event.constraints_retired = original_event.constraints_added
        except Exception as e:
            step_constraints.fail(str(e))
        steps.append(step_constraints)

        # Step 3: Remove tag assignments from this paper
        step_tags = CascadeStep(
            step_number=3,
            step_name="remove_tags",
            is_critical=False,
        )
        step_tags.start()
        try:
            removed = self._remove_tags(paper_id)
            step_tags.complete(items_processed=removed)
        except Exception as e:
            step_tags.fail(str(e))
        steps.append(step_tags)

        # Step 4: Remove belief versions from this paper
        step_versions = CascadeStep(
            step_number=4,
            step_name="remove_belief_versions",
            is_critical=False,
        )
        step_versions.start()
        try:
            removed = self._remove_belief_versions(paper_id)
            step_versions.complete(items_processed=removed)
        except Exception as e:
            step_versions.fail(str(e))
        steps.append(step_versions)

        # Step 5: Mark supersession records as rolled back
        step_supersession = CascadeStep(
            step_number=5,
            step_name="rollback_supersessions",
            is_critical=False,
        )
        step_supersession.start()
        try:
            rolled = self._rollback_supersessions(paper_id)
            step_supersession.complete(items_processed=rolled)
        except Exception as e:
            step_supersession.fail(str(e))
        steps.append(step_supersession)

        # Step 6: Mark the original event as rolled back
        step_mark = CascadeStep(
            step_number=6,
            step_name="mark_original_rolled_back",
            is_critical=True,
        )
        step_mark.start()
        try:
            self._mark_event_rolled_back(original_event.event_id)
            step_mark.complete()
        except Exception as e:
            step_mark.fail(str(e))
        steps.append(step_mark)

        rollback_event.cascade_steps = steps
        rollback_event.molecules_affected = original_event.molecules_affected

        # Check if all critical steps succeeded
        critical_failures = [
            s for s in steps
            if s.is_critical and s.status == CascadeStepStatus.FAILED
        ]
        if critical_failures:
            rollback_event.mark_failed(
                f"Critical rollback step(s) failed: "
                f"{[s.step_name for s in critical_failures]}"
            )
        else:
            rollback_event.mark_completed()

            # Step 7: Post-rollback QA recheck (AG 2026-03-01, QA Spec integration)
            step_qa = CascadeStep(
                step_number=7,
                step_name="qa_recheck",
                is_critical=False,
            )
            step_qa.start()
            try:
                qa_result = self._post_rollback_qa_recheck(
                    original_event.beliefs_added, paper_id
                )
                step_qa.complete(items_processed=qa_result.get("checked", 0))
                rollback_event.cascade_steps.append(step_qa)
                logger.info(
                    "Post-rollback QA recheck: %s",
                    qa_result.get("summary", "completed"),
                )
            except Exception as e:
                step_qa.fail(str(e))
                rollback_event.cascade_steps.append(step_qa)
                logger.warning("Post-rollback QA recheck failed (non-critical): %s", e)

        self._persist_event(rollback_event)

        logger.info(
            "Rollback of paper %s %s (event %s)",
            paper_id,
            rollback_event.status.value,
            rollback_event.event_id,
        )

        return rollback_event

    def _find_integration_event(
        self, paper_id: str
    ) -> Optional[PaperIntegrationEvent]:
        """Find the most recent COMPLETED integration event for a paper."""
        cursor = self.db_conn.cursor()
        try:
            cursor.execute("""
                SELECT event_id, paper_id, timestamp, action, status,
                       pre_snapshot_id, post_snapshot_id,
                       beliefs_added, beliefs_retired,
                       constraints_added, constraints_retired,
                       bn_edges_updated, molecules_affected,
                       tags_assigned, cascade_log,
                       supersedes_paper_id, error_log, rollback_of_event_id
                FROM paper_integration_events
                WHERE paper_id = ? AND status = 'COMPLETED' AND action = 'INTEGRATE'
                ORDER BY timestamp DESC
                LIMIT 1
            """, (paper_id,))
            row = cursor.fetchone()
            if row is None:
                return None

            return PaperIntegrationEvent(
                event_id=row[0],
                paper_id=row[1],
                timestamp=row[2],
                action=IntegrationAction(row[3]),
                status=IntegrationStatus(row[4]),
                pre_snapshot_id=row[5],
                post_snapshot_id=row[6],
                beliefs_added=json.loads(row[7]) if row[7] else [],
                beliefs_retired=json.loads(row[8]) if row[8] else [],
                constraints_added=json.loads(row[9]) if row[9] else [],
                constraints_retired=json.loads(row[10]) if row[10] else [],
                bn_edges_updated=json.loads(row[11]) if row[11] else [],
                molecules_affected=json.loads(row[12]) if row[12] else [],
                tags_assigned=json.loads(row[13]) if row[13] else {},
                supersedes_paper_id=row[15],
                error_log=row[16],
                rollback_of_event_id=row[17],
            )
        except sqlite3.OperationalError:
            logger.debug("paper_integration_events table not found")
            return None

    def _remove_beliefs(self, belief_ids: List[str], paper_id: str) -> int:
        """
        Remove beliefs contributed by this paper.

        If a belief has contributions from multiple papers (via accumulation),
        we only remove this paper's contribution, not the belief entirely.
        For beliefs solely from this paper, we mark them as retired.
        """
        if not belief_ids:
            return 0

        cursor = self.db_conn.cursor()
        removed = 0

        for belief_id in belief_ids:
            # Check if other papers also contribute to this belief
            cursor.execute("""
                SELECT COUNT(*) FROM belief_versions
                WHERE belief_id = ? AND paper_id != ? AND is_current = 1
            """, (belief_id, paper_id))
            other_count = cursor.fetchone()[0]

            if other_count == 0:
                # This paper is the sole contributor — retire the belief
                # (We don't delete; we mark as retired for audit trail)
                cursor.execute("""
                    UPDATE beliefs SET status = 'RETIRED'
                    WHERE belief_id = ?
                """, (belief_id,))
            else:
                # Other papers contribute — just remove this paper's version
                cursor.execute("""
                    UPDATE belief_versions
                    SET is_current = 0
                    WHERE belief_id = ? AND paper_id = ?
                """, (belief_id, paper_id))
            removed += 1

        self.db_conn.commit()
        return removed

    def _remove_constraints(
        self, constraint_ids: List[str], paper_id: str
    ) -> int:
        """Remove constraints contributed by this paper."""
        if not constraint_ids:
            return 0

        cursor = self.db_conn.cursor()
        removed = 0

        for cid in constraint_ids:
            # Mark constraint as retired rather than deleting
            try:
                cursor.execute("""
                    UPDATE constraints SET active = 0
                    WHERE constraint_id = ?
                """, (cid,))
                removed += 1
            except sqlite3.OperationalError:
                # Column 'active' may not exist — try DELETE
                try:
                    cursor.execute("""
                        DELETE FROM constraints
                        WHERE constraint_id = ?
                    """, (cid,))
                    removed += 1
                except sqlite3.OperationalError:
                    pass

        self.db_conn.commit()
        return removed

    def _remove_tags(self, paper_id: str) -> int:
        """Remove all tag assignments from this paper."""
        cursor = self.db_conn.cursor()
        try:
            cursor.execute("""
                DELETE FROM tag_assignments WHERE paper_id = ?
            """, (paper_id,))
            removed = cursor.rowcount
            self.db_conn.commit()
            return removed
        except sqlite3.OperationalError:
            return 0

    def _remove_belief_versions(self, paper_id: str) -> int:
        """Mark all belief versions from this paper as non-current."""
        cursor = self.db_conn.cursor()
        try:
            cursor.execute("""
                UPDATE belief_versions
                SET is_current = 0
                WHERE paper_id = ?
            """, (paper_id,))
            updated = cursor.rowcount
            self.db_conn.commit()
            return updated
        except sqlite3.OperationalError:
            return 0

    def _rollback_supersessions(self, paper_id: str) -> int:
        """Mark supersession records involving this paper as rolled back."""
        cursor = self.db_conn.cursor()
        try:
            cursor.execute("""
                UPDATE supersession_records
                SET rolled_back = 1
                WHERE superseding_paper_id = ?
            """, (paper_id,))
            updated = cursor.rowcount
            self.db_conn.commit()
            return updated
        except sqlite3.OperationalError:
            return 0

    def _post_rollback_qa_recheck(
        self, affected_belief_ids: List[str], paper_id: str
    ) -> Dict[str, Any]:
        """Post-rollback QA: check if remaining beliefs lost support.

        After rolling back a paper's contributions, check whether any
        affected beliefs have become UNGROUNDED (lost all support) or
        have reduced support. Creates SENSITIVITY_FLAG annotations for
        impacted beliefs and reports to overseer.

        This is a non-critical step — failures here don't block rollback.
        """
        result: Dict[str, Any] = {
            "checked": 0,
            "newly_ungrounded": [],
            "reduced_support": [],
            "annotations_created": 0,
            "summary": "",
        }

        if not affected_belief_ids:
            result["summary"] = "no affected beliefs"
            return result

        cursor = self.db_conn.cursor()

        # Check each affected belief for remaining support
        for belief_id in affected_belief_ids:
            result["checked"] += 1
            try:
                # Count remaining active versions from other papers
                cursor.execute("""
                    SELECT COUNT(*) FROM belief_versions
                    WHERE belief_id = ? AND is_current = 1
                """, (belief_id,))
                remaining = cursor.fetchone()[0]

                # Check belief status
                cursor.execute("""
                    SELECT status FROM beliefs WHERE belief_id = ?
                """, (belief_id,))
                row = cursor.fetchone()
                status = row[0] if row else "UNKNOWN"

                if status == "RETIRED" or remaining == 0:
                    result["newly_ungrounded"].append(belief_id)
                elif remaining == 1:
                    # Down to single source — fragile
                    result["reduced_support"].append(belief_id)

            except sqlite3.OperationalError:
                pass

        # Create annotations for impacted beliefs
        try:
            from src.services.annotation_service import AnnotationService, AnnotationType
            ann_svc = AnnotationService()

            for belief_id in result["newly_ungrounded"]:
                try:
                    ann_svc.create_annotation(
                        type=AnnotationType.SENSITIVITY_FLAG,
                        target_type="belief",
                        target_id=belief_id,
                        content=(
                            f"Post-rollback QA: belief lost all support after "
                            f"rollback of paper {paper_id}. Now UNGROUNDED."
                        ),
                        author="qa_rollback_hook",
                        confidence=1.0,
                        metadata={"trigger": "rollback", "paper_id": paper_id},
                    )
                    result["annotations_created"] += 1
                except Exception as e:
                    logger.debug(f"Failed to create annotation for {belief_id}: {e}")

            for belief_id in result["reduced_support"]:
                try:
                    ann_svc.create_annotation(
                        type=AnnotationType.SENSITIVITY_FLAG,
                        target_type="belief",
                        target_id=belief_id,
                        content=(
                            f"Post-rollback QA: belief reduced to single source "
                            f"after rollback of paper {paper_id}. Fragile."
                        ),
                        author="qa_rollback_hook",
                        confidence=0.8,
                        metadata={"trigger": "rollback", "paper_id": paper_id},
                    )
                    result["annotations_created"] += 1
                except Exception as e:
                    logger.debug(f"Failed to create annotation for {belief_id}: {e}")
        except ImportError:
            logger.debug("AnnotationService not available for post-rollback annotations")

        # Report to overseer via reflex event logging
        try:
            from pathlib import Path
            log_dir = Path("logs") / "reflexes"
            log_dir.mkdir(parents=True, exist_ok=True)
            import datetime as _dt
            log_file = log_dir / f"rollback_qa_{_dt.date.today().isoformat()}.jsonl"
            with open(log_file, "a") as f:
                f.write(json.dumps({
                    "event": "post_rollback_qa_recheck",
                    "paper_id": paper_id,
                    "newly_ungrounded": result["newly_ungrounded"],
                    "reduced_support": result["reduced_support"],
                    "annotations_created": result["annotations_created"],
                    "timestamp": _dt.datetime.now(_dt.timezone.utc).isoformat(),
                }) + "\n")
        except Exception as e:
            logger.debug(f"Swallowed in {fpath}: {e}")

        n_ug = len(result["newly_ungrounded"])
        n_rs = len(result["reduced_support"])
        result["summary"] = (
            f"checked {result['checked']} beliefs: "
            f"{n_ug} newly ungrounded, {n_rs} reduced support, "
            f"{result['annotations_created']} annotations created"
        )

        return result

    def _mark_event_rolled_back(self, event_id: str) -> None:
        """Mark the original integration event as ROLLED_BACK."""
        cursor = self.db_conn.cursor()
        cursor.execute("""
            UPDATE paper_integration_events
            SET status = 'ROLLED_BACK'
            WHERE event_id = ?
        """, (event_id,))
        self.db_conn.commit()

    def _persist_event(self, event: PaperIntegrationEvent) -> None:
        """Save the rollback event to the database."""
        cursor = self.db_conn.cursor()
        d = event.to_dict()
        try:
            cursor.execute("""
                INSERT INTO paper_integration_events
                (event_id, paper_id, timestamp, action, status,
                 pre_snapshot_id, post_snapshot_id,
                 beliefs_added, beliefs_retired,
                 constraints_added, constraints_retired,
                 bn_edges_updated, molecules_affected,
                 tags_assigned, cascade_log,
                 supersedes_paper_id, error_log, rollback_of_event_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                d["event_id"], d["paper_id"], d["timestamp"],
                d["action"], d["status"],
                d["pre_snapshot_id"], d["post_snapshot_id"],
                json.dumps(d["beliefs_added"]),
                json.dumps(d["beliefs_retired"]),
                json.dumps(d["constraints_added"]),
                json.dumps(d["constraints_retired"]),
                json.dumps(d["bn_edges_updated"]),
                json.dumps(d["molecules_affected"]),
                json.dumps(d["tags_assigned"]),
                json.dumps(d["cascade_steps"]),
                d["supersedes_paper_id"],
                d["error_log"],
                d["rollback_of_event_id"],
            ))
            self.db_conn.commit()
        except sqlite3.OperationalError as e:
            logger.error("Failed to persist rollback event: %s", e)
