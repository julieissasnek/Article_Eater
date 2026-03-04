"""
Recommendation Loop Service

Orchestrates the continuous article recommendation cycle:

1. Interpretation space operators discover gaps/frontier questions
2. Gaps are scored with VOI and inserted into suggestions table
3. Research queue picks up highest-VOI suggestions
4. Automated searcher executes searches
5. Results feed back to interpretation space (closing gaps)
6. Discovery funnel tracks lifecycle

Can run as:
- Single pass (for batch/nightly use)
- Continuous daemon (for live operation alongside interpretation envelope)

This service bridges interpretation space operators (which identify gaps/frontier
questions) and the research queue/automated searcher pipeline (which finds articles
to address those gaps).
"""

from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Optional
import sqlite3

logger = logging.getLogger(__name__)


class RecommendationLoopService:
    """Orchestrates the continuous article recommendation cycle."""

    def __init__(
        self,
        db_path: str,
        web_db_path: str,
        interpretation_space_dir: str | Path = "data/interpretation_space",
    ):
        """
        Initialize the recommendation loop service.

        Args:
            db_path: Path to web_persistence_v2.db or similar
            web_db_path: Path to article_eater.db
            interpretation_space_dir: Base directory for interpretation space outputs
        """
        self.db_path = Path(db_path)
        self.web_db_path = Path(web_db_path)
        self.interpretation_space_dir = Path(interpretation_space_dir)
        self.phase4_dir = self.interpretation_space_dir / "phase4"

    def run_single_pass(self, top_n: int = 5) -> dict:
        """
        Execute one full cycle: detect gaps → score → queue → search → report.

        Args:
            top_n: Number of top suggestions to dispatch for searching

        Returns:
            Dictionary with cycle metrics
        """
        cycle_start = datetime.now(timezone.utc)
        logger.info("=" * 80)
        logger.info("RECOMMENDATION LOOP: SINGLE PASS")
        logger.info(f"Started at {cycle_start.isoformat()}")
        logger.info("=" * 80)

        report = {
            "timestamp": cycle_start.isoformat(),
            "cycle_stage": "starting",
            "steps": {},
        }

        # Step 1: Harvest interpretation space gaps
        logger.info("\n[Step 1] Harvesting interpretation space gaps...")
        gaps = self._harvest_interpretation_space_gaps()
        report["steps"]["harvest_gaps"] = {
            "count": len(gaps),
            "gaps": gaps[:5],  # Include first 5 for visibility
        }
        logger.info(f"Harvested {len(gaps)} frontier question suggestions")

        # Step 2: Harvest QA backlog
        logger.info("\n[Step 2] Harvesting QA backlog...")
        qa_suggestions = self._harvest_qa_backlog()
        report["steps"]["harvest_qa"] = {
            "count": len(qa_suggestions),
        }
        logger.info(f"Harvested {len(qa_suggestions)} QA follow-up suggestions")

        # Step 2b: Harvest circuit QA search targets
        logger.info("\n[Step 2b] Harvesting circuit QA search targets...")
        circuit_suggestions = self._harvest_circuit_qa_targets()
        report["steps"]["harvest_circuit_qa"] = {
            "count": len(circuit_suggestions),
        }
        logger.info(f"Harvested {len(circuit_suggestions)} circuit QA search targets")

        # Step 3: Score and prioritize
        logger.info("\n[Step 3] Scoring and prioritizing suggestions...")
        all_suggestions = gaps + qa_suggestions + circuit_suggestions
        prioritized = self._score_and_prioritize(all_suggestions)
        report["steps"]["prioritize"] = {
            "total_suggestions": len(prioritized),
            "high_voi": sum(1 for s in prioritized if s.get("voi_bucket") == "high"),
            "medium_voi": sum(1 for s in prioritized if s.get("voi_bucket") == "medium"),
            "low_voi": sum(1 for s in prioritized if s.get("voi_bucket") == "low"),
        }
        logger.info(
            f"Prioritized {len(prioritized)} suggestions: "
            f"{report['steps']['prioritize']['high_voi']} high, "
            f"{report['steps']['prioritize']['medium_voi']} medium, "
            f"{report['steps']['prioritize']['low_voi']} low"
        )

        # Step 4: Insert into suggestions table
        logger.info("\n[Step 4] Inserting into interpretation_space_suggestions...")
        inserted = self._insert_suggestions_into_table(prioritized)
        report["steps"]["insert"] = {
            "inserted_count": inserted,
        }
        logger.info(f"Inserted {inserted} suggestions into recommendation pipeline")

        # Step 5: Dispatch top-N for searching
        logger.info(f"\n[Step 5] Dispatching top-{top_n} suggestions for searching...")
        dispatch_result = self._dispatch_searches(top_n=top_n)
        report["steps"]["dispatch"] = dispatch_result
        logger.info(
            f"Dispatched {dispatch_result['dispatched_count']} searches "
            f"({dispatch_result['total_targets']} total targets in queue)"
        )

        # Step 6: Cycle health report
        logger.info("\n[Step 6] Generating cycle health metrics...")
        health = self._report_cycle_health(cycle_start)
        report["steps"]["health"] = health
        logger.info(f"Cycle health: {health['status']}")

        report["cycle_stage"] = "completed"
        report["duration_seconds"] = (
            datetime.now(timezone.utc) - cycle_start
        ).total_seconds()

        logger.info("\n" + "=" * 80)
        logger.info("CYCLE COMPLETED")
        logger.info(f"Duration: {report['duration_seconds']:.1f}s")
        logger.info("=" * 80)

        return report

    def run_continuous(self, interval_seconds: int = 300, max_cycles: Optional[int] = None):
        """
        Run the loop continuously with configurable interval.

        Args:
            interval_seconds: Seconds between cycles (default 5 minutes)
            max_cycles: Max cycles to run (None = infinite)
        """
        logger.info("=" * 80)
        logger.info("RECOMMENDATION LOOP: CONTINUOUS DAEMON")
        logger.info(f"Starting continuous loop (interval={interval_seconds}s)")
        logger.info("=" * 80)

        cycle_count = 0
        try:
            while max_cycles is None or cycle_count < max_cycles:
                cycle_count += 1
                logger.info(f"\n\n>>> CYCLE {cycle_count} <<<")

                try:
                    self.run_single_pass()
                except Exception as e:
                    logger.error(f"Cycle {cycle_count} failed: {e}", exc_info=True)

                if max_cycles is None or cycle_count < max_cycles:
                    logger.info(f"Sleeping for {interval_seconds}s before next cycle...")
                    time.sleep(interval_seconds)

        except KeyboardInterrupt:
            logger.info(f"\nContinuous loop interrupted after {cycle_count} cycles")
        except Exception as e:
            logger.error(f"Continuous loop error: {e}", exc_info=True)

    # ========================================================================
    # Private methods
    # ========================================================================

    def _harvest_interpretation_space_gaps(self) -> list[dict]:
        """
        Read interpretation space Phase 4 outputs and convert to suggestions.

        Returns:
            List of suggestion dicts with frontier questions
        """
        suggestions = []

        if not self.phase4_dir.exists():
            logger.warning(f"Phase 4 directory not found: {self.phase4_dir}")
            return suggestions

        # Read prioritized frontier questions
        frontier_file = self.phase4_dir / "prioritized_frontier_questions.json"
        if frontier_file.exists():
            try:
                with open(frontier_file) as f:
                    phase4_data = json.load(f)

                questions_list = phase4_data.get("questions", [])
                logger.info(f"Loaded {len(questions_list)} frontier questions from Phase 4")

                for item in questions_list:
                    belief_id = item.get("belief_id", "unknown")
                    questions = item.get("questions", [])
                    voi_score = item.get("voi_score", 0.5)
                    voi_bucket = item.get("voi_bucket", "low")

                    # Convert frontier questions to search suggestions
                    # Each question becomes a suggested search query
                    for idx, question in enumerate(questions, 1):
                        suggestion = {
                            "source": "interpretation_space",
                            "status": "identified",
                            "description": f"Frontier question for {belief_id}: {question}",
                            "suggested_search": self._question_to_search_query(
                                question, belief_id
                            ),
                            "priority_score": voi_score,
                            "voi_bucket": voi_bucket,
                            "belief_id": belief_id,
                            "phase4_question_index": idx,
                            "phase4_voi_rank": item.get("voi_rank", 999),
                        }
                        suggestions.append(suggestion)

                logger.info(
                    f"Converted {len(suggestions)} frontier questions to search suggestions"
                )

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse frontier questions: {e}")
            except Exception as e:
                logger.error(f"Error reading frontier questions: {e}")

        return suggestions

    def _harvest_qa_backlog(self) -> list[dict]:
        """
        Check for unprocessed QA follow-ups in the database.

        Returns:
            List of QA suggestion dicts
        """
        suggestions = []

        try:
            with sqlite3.connect(str(self.web_db_path)) as conn:
                cursor = conn.cursor()

                # Query for unprocessed QA follow-ups
                cursor.execute("""
                    SELECT id, follow_up_question, article_id
                    FROM qa_results
                    WHERE follow_up_question IS NOT NULL
                    AND follow_up_processed = 0
                    ORDER BY created_at DESC
                    LIMIT 50
                """)

                rows = cursor.fetchall()
                logger.info(f"Found {len(rows)} unprocessed QA follow-ups")

                for row_id, question, article_id in rows:
                    suggestion = {
                        "source": "qa",
                        "status": "identified",
                        "description": f"QA follow-up: {question[:80]}",
                        "suggested_search": question,
                        "priority_score": 0.6,
                        "voi_bucket": "medium",
                        "qa_result_id": row_id,
                        "article_id": article_id,
                    }
                    suggestions.append(suggestion)

        except sqlite3.OperationalError as e:
            logger.warning(f"QA backlog query failed (table may not exist): {e}")
        except Exception as e:
            logger.error(f"Error harvesting QA backlog: {e}")

        return suggestions

    def _harvest_circuit_qa_targets(self) -> list[dict]:
        """
        Harvest search targets queued by circuit QA responses.

        Circuit answers for HYPOTHETICAL or under-evidenced circuits emit
        search targets (article queries) that should feed the recommendation
        loop. These are inserted into the suggestions table by the QA handler
        with source='circuit_qa'. This method picks up any that haven't
        been dispatched yet.

        Returns:
            List of suggestion dicts from circuit QA
        """
        suggestions = []
        try:
            with sqlite3.connect(str(self.web_db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, description, suggested_search, priority_score
                    FROM interpretation_space_suggestions
                    WHERE source = 'circuit_qa'
                    AND status IN ('proposed', 'identified')
                    ORDER BY priority_score DESC
                    LIMIT 30
                """)
                rows = cursor.fetchall()
                for row_id, desc, search, score in rows:
                    suggestions.append({
                        "source": "circuit_qa",
                        "status": "identified",
                        "description": desc,
                        "suggested_search": search,
                        "priority_score": score or 0.65,
                        "voi_bucket": "medium" if (score or 0.65) < 0.7 else "high",
                        "suggestion_id": row_id,
                    })
                logger.info(
                    f"Found {len(suggestions)} pending circuit QA search targets"
                )
        except sqlite3.OperationalError as e:
            logger.warning(f"Circuit QA target query failed: {e}")
        except Exception as e:
            logger.error(f"Error harvesting circuit QA targets: {e}")
        return suggestions

    def _score_and_prioritize(self, suggestions: list[dict]) -> list[dict]:
        """
        Apply VOI scoring and prioritization to suggestions.

        Args:
            suggestions: List of suggestion dicts

        Returns:
            List of suggestions sorted by VOI score
        """
        # Ensure all have priority_score
        for suggestion in suggestions:
            if "priority_score" not in suggestion:
                suggestion["priority_score"] = 0.5

            # Set voi_bucket if not already set
            if "voi_bucket" not in suggestion:
                score = suggestion.get("priority_score", 0.5)
                if score >= 0.6:
                    suggestion["voi_bucket"] = "high"
                elif score >= 0.3:
                    suggestion["voi_bucket"] = "medium"
                else:
                    suggestion["voi_bucket"] = "low"

        # Sort by priority score descending
        suggestions.sort(key=lambda s: s.get("priority_score", 0.0), reverse=True)

        return suggestions

    def _insert_suggestions_into_table(self, suggestions: list[dict]) -> int:
        """
        Insert suggestions into interpretation_space_suggestions table.

        Args:
            suggestions: List of suggestion dicts

        Returns:
            Count of inserted suggestions
        """
        count = 0

        try:
            from src.services.interpretation_space_suggestions import (
                InterpretationSpaceSuggestionsManager,
                SuggestionRecord,
            )

            mgr = InterpretationSpaceSuggestionsManager(str(self.web_db_path))

            for suggestion in suggestions:
                record = SuggestionRecord(
                    source=suggestion.get("source", "interpretation_space"),
                    status=suggestion.get("status", "identified"),
                    description=suggestion.get(
                        "description",
                        suggestion.get("suggested_search", ""),
                    ),
                    suggested_search=suggestion.get("suggested_search", ""),
                    priority_score=suggestion.get("priority_score", 0.5),
                    article_id=suggestion.get("article_id"),
                )

                try:
                    mgr.insert_suggestion(record)
                    count += 1
                except Exception as e:
                    logger.warning(f"Failed to insert suggestion: {e}")

        except ImportError as e:
            logger.error(f"InterpretationSpaceSuggestionsManager not available: {e}")
        except Exception as e:
            logger.error(f"Error inserting suggestions: {e}")

        return count

    def _dispatch_searches(self, top_n: int = 5) -> dict:
        """
        Send top-N suggestions to automated searcher via research queue.

        Args:
            top_n: Number of top suggestions to dispatch

        Returns:
            Dict with dispatch metrics
        """
        result = {
            "dispatched_count": 0,
            "total_targets": 0,
            "high_priority_targets": 0,
            "message": "Dispatch not available",
        }

        try:
            from src.queue.service import ResearchQueueService

            queue = ResearchQueueService(db_path=str(self.web_db_path))

            # Refresh queue from gap predictor + theory
            queue.refresh_queue(max_gaps=50, include_theory=True)

            targets = queue.get_prioritized_targets()
            result["total_targets"] = len(targets)
            result["high_priority_targets"] = sum(
                1 for t in targets if t.priority.value == "high"
            )

            # Run automated searcher on top-N targets
            try:
                from src.queue.automated_searcher import AutomatedQueueSearcher

                searcher = AutomatedQueueSearcher(queue_service=queue)
                runs = searcher.run_once(max_targets=top_n)
                result["dispatched_count"] = len(runs)
                result["message"] = f"Dispatched {len(runs)} searches"
                logger.info(f"Automated searcher ran {len(runs)} searches")

            except Exception as e:
                logger.warning(f"Automated searcher not available: {e}")
                result["message"] = f"Queue refresh done; searcher unavailable: {e}"

        except Exception as e:
            logger.error(f"Error dispatching searches: {e}")
            result["message"] = f"Error: {e}"

        return result

    def _report_cycle_health(self, cycle_start: datetime) -> dict:
        """
        Generate health metrics for this cycle.

        Args:
            cycle_start: Cycle start timestamp

        Returns:
            Dict with health metrics
        """
        duration = (datetime.now(timezone.utc) - cycle_start).total_seconds()

        health = {
            "status": "healthy",
            "duration_seconds": round(duration, 1),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        try:
            # Check suggestion table health
            with sqlite3.connect(str(self.web_db_path)) as conn:
                cursor = conn.cursor()

                # Count unacted suggestions
                cursor.execute("""
                    SELECT COUNT(*) FROM interpretation_space_suggestions
                    WHERE status IN ('proposed', 'identified')
                """)
                unacted = cursor.fetchone()[0] or 0
                health["unacted_suggestions"] = unacted

                # Count stale suggestions
                cutoff = (
                    datetime.now(timezone.utc) - timedelta(days=7)
                ).isoformat()
                cursor.execute("""
                    SELECT COUNT(*) FROM interpretation_space_suggestions
                    WHERE status NOT IN ('resolved', 'stale')
                    AND created_at < ?
                """, (cutoff,))
                stale = cursor.fetchone()[0] or 0
                health["stale_suggestions"] = stale

                # Suggestion source distribution
                cursor.execute("""
                    SELECT source, COUNT(*) as count
                    FROM interpretation_space_suggestions
                    WHERE status IN ('proposed', 'identified')
                    GROUP BY source
                """)
                health["suggestions_by_source"] = {
                    row[0]: row[1] for row in cursor.fetchall()
                }

        except sqlite3.OperationalError as e:
            logger.warning(f"Suggestion health check failed: {e}")
            health["status"] = "database_unavailable"
        except Exception as e:
            logger.error(f"Error in cycle health check: {e}")
            health["status"] = "error"

        return health

    def _question_to_search_query(self, question: str, belief_id: str) -> str:
        """
        Convert a frontier question to a search query.

        Args:
            question: The question text
            belief_id: The belief this question is about

        Returns:
            Search query string
        """
        # Extract key terms from question
        # Common patterns: "For which populations...", "In which settings...", etc.

        if "population" in question.lower():
            return f"{belief_id} population scope generalizability"
        elif "setting" in question.lower():
            return f"{belief_id} setting context boundary conditions"
        elif "cultural" in question.lower():
            return f"{belief_id} cultural differences cross-cultural"
        elif "replication" in question.lower():
            return f"{belief_id} replication meta-analysis validation"
        else:
            # Default: use belief ID and first few words of question
            words = question.split()[:4]
            return f"{belief_id} {' '.join(words)}"


__all__ = ["RecommendationLoopService"]
