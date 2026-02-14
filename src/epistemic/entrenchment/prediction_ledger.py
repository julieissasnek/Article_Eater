"""
Prediction Tracking Ledger (Sprint 6b / Task 6b.4).

Maintains a ledger for tracking confirmation/disconfirmation of
DERIVED_HYPOTHESEs, implementing theory evaluation per spec §5.5.

Per spec:
"The system should maintain a ledger for each DERIVED_HYPOTHESIS:
hypothesis_id, text, derived_from, confirmed_by, disconfirmed_by,
current_entrenchment. This ledger is how the system implements
theory evaluation."

Reference: Non_Empirical_Web_Integration_Spec_V1.0.md §5.5
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime
import json

from .theory_updating import update_theory_entrenchment, CONFIRMATION_BONUS, DISCONFIRMATION_PENALTY


@dataclass
class PredictionLedgerEntry:
    """
    Tracks confirmation/disconfirmation of a derived hypothesis.

    Example from spec:
        hypothesis_id: "kaplan_1995_h3"
        text: "Exposure to natural settings restores directed attention capacity"
        derived_from: "kaplan_1995_prop2"  # ART's core proposition
        confirmed_by: ["berman_2008", "berto_2005", "hartig_2003"]
        disconfirmed_by: []
        current_entrenchment: 0.62
    """
    hypothesis_id: str
    hypothesis_text: str
    derived_from: str  # Parent THEORETICAL_PROPOSITION id
    confirmed_by: List[str] = field(default_factory=list)
    disconfirmed_by: List[str] = field(default_factory=list)
    current_entrenchment: float = 0.35  # Base for derived hypotheses
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)

    @property
    def confirmation_count(self) -> int:
        """Number of confirming studies."""
        return len(self.confirmed_by)

    @property
    def disconfirmation_count(self) -> int:
        """Number of disconfirming studies."""
        return len(self.disconfirmed_by)

    @property
    def total_tests(self) -> int:
        """Total number of empirical tests."""
        return self.confirmation_count + self.disconfirmation_count

    @property
    def success_rate(self) -> Optional[float]:
        """Proportion of confirmations, or None if no tests."""
        if self.total_tests == 0:
            return None
        return self.confirmation_count / self.total_tests

    def add_confirmation(self, study_id: str) -> bool:
        """
        Add a confirming study.

        Args:
            study_id: ID of the confirming study

        Returns:
            True if added (not duplicate), False otherwise
        """
        if study_id in self.confirmed_by:
            return False

        self.confirmed_by.append(study_id)
        self._update_entrenchment()
        self.last_updated = datetime.now()
        return True

    def add_disconfirmation(self, study_id: str) -> bool:
        """
        Add a disconfirming study.

        Args:
            study_id: ID of the disconfirming study

        Returns:
            True if added (not duplicate), False otherwise
        """
        if study_id in self.disconfirmed_by:
            return False

        self.disconfirmed_by.append(study_id)
        self._update_entrenchment()
        self.last_updated = datetime.now()
        return True

    def _update_entrenchment(self) -> None:
        """Recompute entrenchment based on current confirmation state."""
        base = 0.35  # Base entrenchment for derived hypotheses
        self.current_entrenchment = update_theory_entrenchment(
            base,
            confirmations=self.confirmation_count,
            disconfirmations=self.disconfirmation_count
        )

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "hypothesis_id": self.hypothesis_id,
            "hypothesis_text": self.hypothesis_text,
            "derived_from": self.derived_from,
            "confirmed_by": self.confirmed_by,
            "disconfirmed_by": self.disconfirmed_by,
            "current_entrenchment": self.current_entrenchment,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PredictionLedgerEntry":
        """Deserialize from dictionary."""
        entry = cls(
            hypothesis_id=data["hypothesis_id"],
            hypothesis_text=data["hypothesis_text"],
            derived_from=data["derived_from"],
            confirmed_by=data.get("confirmed_by", []),
            disconfirmed_by=data.get("disconfirmed_by", []),
            current_entrenchment=data.get("current_entrenchment", 0.35),
        )
        if "created_at" in data:
            entry.created_at = datetime.fromisoformat(data["created_at"])
        if "last_updated" in data:
            entry.last_updated = datetime.fromisoformat(data["last_updated"])
        return entry


class PredictionLedger:
    """
    Maintains prediction tracking for all derived hypotheses.

    This ledger is the mechanism for theory evaluation:
    - A theory with many confirmed predictions gains entrenchment
    - A theory with accumulating disconfirmations loses entrenchment
    """

    def __init__(self):
        self._entries: Dict[str, PredictionLedgerEntry] = {}
        self._by_theory: Dict[str, List[str]] = {}  # theory_id -> [hypothesis_ids]

    def register_hypothesis(
        self,
        hypothesis_id: str,
        text: str,
        parent_prop_id: str
    ) -> PredictionLedgerEntry:
        """
        Register a new derived hypothesis.

        Args:
            hypothesis_id: Unique ID for the hypothesis
            text: The hypothesis text
            parent_prop_id: ID of the parent THEORETICAL_PROPOSITION

        Returns:
            The created entry
        """
        entry = PredictionLedgerEntry(
            hypothesis_id=hypothesis_id,
            hypothesis_text=text,
            derived_from=parent_prop_id
        )
        self._entries[hypothesis_id] = entry

        # Track by parent theory
        if parent_prop_id not in self._by_theory:
            self._by_theory[parent_prop_id] = []
        self._by_theory[parent_prop_id].append(hypothesis_id)

        return entry

    def record_confirmation(self, hypothesis_id: str, study_id: str) -> bool:
        """
        Record a confirmation for a hypothesis.

        Args:
            hypothesis_id: ID of the hypothesis
            study_id: ID of the confirming study

        Returns:
            True if recorded, False if hypothesis not found
        """
        if hypothesis_id not in self._entries:
            return False

        return self._entries[hypothesis_id].add_confirmation(study_id)

    def record_disconfirmation(self, hypothesis_id: str, study_id: str) -> bool:
        """
        Record a disconfirmation for a hypothesis.

        Args:
            hypothesis_id: ID of the hypothesis
            study_id: ID of the disconfirming study

        Returns:
            True if recorded, False if hypothesis not found
        """
        if hypothesis_id not in self._entries:
            return False

        return self._entries[hypothesis_id].add_disconfirmation(study_id)

    def get_entry(self, hypothesis_id: str) -> Optional[PredictionLedgerEntry]:
        """Get entry for a hypothesis."""
        return self._entries.get(hypothesis_id)

    def get_hypotheses_for_theory(self, theory_id: str) -> List[PredictionLedgerEntry]:
        """Get all hypotheses derived from a theory."""
        hypothesis_ids = self._by_theory.get(theory_id, [])
        return [self._entries[hid] for hid in hypothesis_ids if hid in self._entries]

    def compute_theory_track_record(self, theory_id: str) -> Dict:
        """
        Compute aggregate track record for a theory.

        Args:
            theory_id: ID of the parent theory

        Returns:
            Dict with confirmation/disconfirmation statistics
        """
        hypotheses = self.get_hypotheses_for_theory(theory_id)

        if not hypotheses:
            return {
                "theory_id": theory_id,
                "hypothesis_count": 0,
                "total_confirmations": 0,
                "total_disconfirmations": 0,
                "success_rate": None,
                "status": "no_predictions"
            }

        total_conf = sum(h.confirmation_count for h in hypotheses)
        total_disconf = sum(h.disconfirmation_count for h in hypotheses)
        total_tests = total_conf + total_disconf

        return {
            "theory_id": theory_id,
            "hypothesis_count": len(hypotheses),
            "total_confirmations": total_conf,
            "total_disconfirmations": total_disconf,
            "success_rate": total_conf / total_tests if total_tests > 0 else None,
            "status": self._assess_theory_status(total_conf, total_disconf)
        }

    def _assess_theory_status(self, confirmations: int, disconfirmations: int) -> str:
        """Assess theory status based on track record."""
        total = confirmations + disconfirmations
        if total == 0:
            return "untested"

        rate = confirmations / total
        if rate >= 0.8:
            return "well_supported"
        if rate >= 0.6:
            return "moderately_supported"
        if rate >= 0.4:
            return "needs_revision"
        return "problematic"

    def count(self) -> int:
        """Total number of hypotheses in ledger."""
        return len(self._entries)

    def to_dict(self) -> dict:
        """Serialize entire ledger."""
        return {
            "entries": {k: v.to_dict() for k, v in self._entries.items()},
            "by_theory": self._by_theory
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PredictionLedger":
        """Deserialize ledger."""
        ledger = cls()
        for hid, entry_data in data.get("entries", {}).items():
            ledger._entries[hid] = PredictionLedgerEntry.from_dict(entry_data)
        ledger._by_theory = data.get("by_theory", {})
        return ledger

    def save(self, filepath: str) -> None:
        """Save ledger to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, filepath: str) -> "PredictionLedger":
        """Load ledger from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)
