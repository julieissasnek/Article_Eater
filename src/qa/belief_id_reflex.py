"""
Belief ID Reflex — Auto-detect and fix null environment_id and outcome_id.

RFX-BEL-OUTID: Detects beliefs with null outcome_id and auto-fixes by running
outcome_lookup mapping from the original extraction consequents.

RFX-BEL-ENVID: Detects beliefs with null environment_id and auto-fixes by
hashing belief_id to create deterministic environment identifiers.
"""

import json
import logging
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Tuple

from src.qa.reflex_system import Reflex, ReflexSeverity
from src.services.db_locator import get_web_db

logger = logging.getLogger(__name__)


class BeliefOutcomeIdReflex(Reflex):
    """RFX-BEL-OUTID: Fix null outcome_id by mapping from outcome_lookup."""

    def __init__(self, repo_root: Path = None):
        super().__init__(
            reflex_id="RFX-BEL-OUTID",
            component="belief_id_backfill",
            success_condition_id="BEL-SC2",
            description="Beliefs with null outcome_id (should be >=90% mapped)",
            severity=ReflexSeverity.WARNING,
            repo_root=repo_root or Path.cwd()
        )
        self.web_db = get_web_db()
        self.outcome_lookup = self.repo_root / "contracts" / "outcome_vocab" / "outcome_lookup.json"
        self.backfill_script = self.repo_root / "scripts" / "backfill_belief_ids.py"

    def detect(self) -> Tuple[bool, Dict[str, Any]]:
        """Check if >10% of beliefs have null outcome_id."""
        if not self.web_db.exists():
            return False, {}

        try:
            conn = sqlite3.connect(str(self.web_db))
            total = conn.execute("SELECT COUNT(*) FROM beliefs").fetchone()[0]
            with_outcome = conn.execute(
                "SELECT COUNT(*) FROM beliefs WHERE outcome_id IS NOT NULL"
            ).fetchone()[0]
            conn.close()

            if total == 0:
                return False, {}

            coverage = with_outcome / total
            problem = coverage < 0.90  # Target is >=90%

            return problem, {
                "total_beliefs": total,
                "with_outcome_id": with_outcome,
                "coverage": coverage,
                "threshold": 0.90
            }
        except Exception as e:
            logger.error(f"Failed to detect belief outcome_id coverage: {e}")
            return False, {"error": str(e)}

    def fix(self, details: Dict[str, Any]) -> Tuple[bool, str]:
        """Run backfill_belief_ids.py to fix null outcome_ids."""
        if not self.backfill_script.exists():
            return False, f"backfill script not found: {self.backfill_script}"

        if not self.outcome_lookup.exists():
            return False, f"outcome_lookup not found: {self.outcome_lookup}"

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    str(self.backfill_script),
                    "--web-db", str(self.web_db),
                    "--outcome-lookup", str(self.outcome_lookup)
                ],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                cwd=str(self.repo_root)
            )

            if result.returncode != 0:
                return False, f"backfill script failed: {result.stderr[:200]}"

            # Verify the fix worked
            fixed, coverage = self._verify_fix()
            if fixed:
                return True, f"backfill completed; outcome_id coverage now {100*coverage:.1f}%"
            else:
                return False, f"backfill ran but coverage still low: {100*coverage:.1f}%"

        except subprocess.TimeoutExpired:
            return False, "backfill script timed out (>5min)"
        except Exception as e:
            return False, f"backfill execution failed: {str(e)[:100]}"

    def _verify_fix(self) -> Tuple[bool, float]:
        """Check if fix was successful."""
        try:
            conn = sqlite3.connect(str(self.web_db))
            total = conn.execute("SELECT COUNT(*) FROM beliefs").fetchone()[0]
            with_outcome = conn.execute(
                "SELECT COUNT(*) FROM beliefs WHERE outcome_id IS NOT NULL"
            ).fetchone()[0]
            conn.close()

            coverage = with_outcome / max(1, total)
            return coverage >= 0.90, coverage
        except Exception:
            return False, 0.0


class BeliefEnvironmentIdReflex(Reflex):
    """RFX-BEL-ENVID: Fix null environment_id by hashing belief_id."""

    def __init__(self, repo_root: Path = None):
        super().__init__(
            reflex_id="RFX-BEL-ENVID",
            component="belief_id_backfill",
            success_condition_id="BEL-SC1",
            description="Beliefs with null environment_id (should be 100%)",
            severity=ReflexSeverity.ERROR,
            repo_root=repo_root or Path.cwd()
        )
        self.web_db = get_web_db()
        self.backfill_script = self.repo_root / "scripts" / "backfill_belief_ids.py"

    def detect(self) -> Tuple[bool, Dict[str, Any]]:
        """Check if any belief has null environment_id."""
        if not self.web_db.exists():
            return False, {}

        try:
            conn = sqlite3.connect(str(self.web_db))
            total = conn.execute("SELECT COUNT(*) FROM beliefs").fetchone()[0]
            with_env = conn.execute(
                "SELECT COUNT(*) FROM beliefs WHERE environment_id IS NOT NULL"
            ).fetchone()[0]
            conn.close()

            if total == 0:
                return False, {}

            coverage = with_env / total
            problem = coverage < 0.99  # Target is ~100% (99% allows rounding)

            return problem, {
                "total_beliefs": total,
                "with_environment_id": with_env,
                "null_count": total - with_env,
                "coverage": coverage,
                "threshold": 0.99
            }
        except Exception as e:
            logger.error(f"Failed to detect belief environment_id coverage: {e}")
            return False, {"error": str(e)}

    def fix(self, details: Dict[str, Any]) -> Tuple[bool, str]:
        """Run backfill_belief_ids.py to fix null environment_ids."""
        if not self.backfill_script.exists():
            return False, f"backfill script not found: {self.backfill_script}"

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    str(self.backfill_script),
                    "--web-db", str(self.web_db)
                ],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                cwd=str(self.repo_root)
            )

            if result.returncode != 0:
                return False, f"backfill script failed: {result.stderr[:200]}"

            # Verify the fix worked
            fixed, coverage = self._verify_fix()
            if fixed:
                return True, f"backfill completed; environment_id coverage now {100*coverage:.1f}%"
            else:
                return False, f"backfill ran but coverage still low: {100*coverage:.1f}%"

        except subprocess.TimeoutExpired:
            return False, "backfill script timed out (>5min)"
        except Exception as e:
            return False, f"backfill execution failed: {str(e)[:100]}"

    def _verify_fix(self) -> Tuple[bool, float]:
        """Check if fix was successful."""
        try:
            conn = sqlite3.connect(str(self.web_db))
            total = conn.execute("SELECT COUNT(*) FROM beliefs").fetchone()[0]
            with_env = conn.execute(
                "SELECT COUNT(*) FROM beliefs WHERE environment_id IS NOT NULL"
            ).fetchone()[0]
            conn.close()

            coverage = with_env / max(1, total)
            return coverage >= 0.99, coverage
        except Exception:
            return False, 0.0
