"""
Article Eater - Epistemic Status Model
ARCH-4 Sprint 1.2: Data Model Implementation

Combines Spohn's ranking theory with Pollock's warrant semantics.
Per panel consultation (Spohn, Pollock, Haack, 2026-02-12).

Reference: contracts/schemas/epistemic_status.v1.schema.json
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime


# ============================================================
# ENUMS
# ============================================================

class WarrantStatus(Enum):
    """
    Pollock warrant status for a belief.

    WARRANTED: Justified and undefeated - this belief should be accepted
    DEFEATED: Has an undefeated rebutting or undercutting defeater
    SUSPENDED: In a defeat cycle - neither warranted nor defeated
    UNGROUNDED: Lacks any chain to experiential basis (per Haack)
    """
    WARRANTED = "WARRANTED"
    DEFEATED = "DEFEATED"
    SUSPENDED = "SUSPENDED"
    UNGROUNDED = "UNGROUNDED"


class DefeatType(Enum):
    """
    Type of defeat per Pollock's defeasible reasoning.

    REBUTTING: Attacks the conclusion directly (provides reason to believe ~P)
    UNDERCUTTING: Attacks the inference link (provides reason to doubt P→Q)
    BOTH: Both rebutting and undercutting defeat present
    """
    REBUTTING = "REBUTTING"
    UNDERCUTTING = "UNDERCUTTING"
    BOTH = "BOTH"


# ============================================================
# DATA CLASSES
# ============================================================

@dataclass
class RankPair:
    """
    Spohn rank pair representing degree of belief/disbelief.

    IMPORTANT: Ranks represent degree of DISBELIEF, not belief.
    - rank = 0 means "not disbelieved" (i.e., believed)
    - Higher rank = more disbelieved

    A belief B is believed iff neg_rank > rank
    A belief B is disbelieved iff rank > neg_rank
    A belief B is suspended iff rank == neg_rank

    Firmness = |rank - neg_rank| indicates strength of commitment.
    """
    rank: int = 0  # κ(B) - degree of disbelief in B
    neg_rank: int = 0  # κ(¬B) - degree of disbelief in negation of B

    def __post_init__(self):
        """Validate ranks are non-negative."""
        if self.rank < 0:
            raise ValueError(f"rank must be non-negative, got {self.rank}")
        if self.neg_rank < 0:
            raise ValueError(f"neg_rank must be non-negative, got {self.neg_rank}")

    @property
    def firmness(self) -> int:
        """
        Firmness of belief = |rank - neg_rank|.
        Higher firmness = more committed (either to belief or disbelief).
        """
        return abs(self.rank - self.neg_rank)

    @property
    def believed(self) -> bool:
        """True if B is believed (neg_rank > rank)."""
        return self.neg_rank > self.rank

    @property
    def disbelieved(self) -> bool:
        """True if B is disbelieved (rank > neg_rank)."""
        return self.rank > self.neg_rank

    @property
    def suspended(self) -> bool:
        """True if belief is suspended (rank == neg_rank)."""
        return self.rank == self.neg_rank

    def to_dict(self) -> Dict[str, Any]:
        return {
            'rank': self.rank,
            'neg_rank': self.neg_rank,
            'firmness': self.firmness,
            'believed': self.believed
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RankPair':
        return cls(
            rank=data.get('rank', 0),
            neg_rank=data.get('neg_rank', 0)
        )

    @classmethod
    def from_credence(cls, credence: float, uncertainty: float) -> 'RankPair':
        """
        Convert legacy credence/uncertainty to rank pair.
        Used for migration from v1 to v2.

        Mapping logic:
        - credence < 0.5 → disbelieved (rank > neg_rank)
        - credence > 0.5 → believed (neg_rank > rank)
        - credence = 0.5 → suspended (rank = neg_rank)

        Uncertainty affects firmness (difference between ranks).
        Per migration strategy: max firmness of 5 for migrated beliefs.
        """
        MAX_FIRMNESS = 5  # Per panel review

        if credence >= 0.5:
            # Believed
            strength = credence - 0.5  # [0, 0.5]
            firmness = int(strength * 10 * (1 - uncertainty))
            firmness = min(MAX_FIRMNESS, firmness)
            return cls(rank=0, neg_rank=firmness)
        else:
            # Disbelieved
            strength = 0.5 - credence  # [0, 0.5]
            firmness = int(strength * 10 * (1 - uncertainty))
            firmness = min(MAX_FIRMNESS, firmness)
            return cls(rank=firmness, neg_rank=0)


@dataclass
class RankHistoryEntry:
    """A single entry in rank history for debugging and explanation."""
    timestamp: datetime
    old_rank: int
    new_rank: int
    old_neg_rank: int
    new_neg_rank: int
    reason: str
    evidence_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'old_rank': self.old_rank,
            'new_rank': self.new_rank,
            'old_neg_rank': self.old_neg_rank,
            'new_neg_rank': self.new_neg_rank,
            'reason': self.reason,
            'evidence_id': self.evidence_id
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RankHistoryEntry':
        return cls(
            timestamp=datetime.fromisoformat(data['timestamp']),
            old_rank=data['old_rank'],
            new_rank=data['new_rank'],
            old_neg_rank=data['old_neg_rank'],
            new_neg_rank=data['new_neg_rank'],
            reason=data['reason'],
            evidence_id=data.get('evidence_id')
        )


@dataclass
class DefeatInfo:
    """Details about defeat status when warrant_status is DEFEATED or SUSPENDED."""
    defeater_ids: List[str] = field(default_factory=list)
    defeat_type: Optional[DefeatType] = None
    attack_point: Optional[str] = None  # For undercutting: what inference is attacked
    cycle_members: List[str] = field(default_factory=list)  # For SUSPENDED: cycle participants

    def to_dict(self) -> Dict[str, Any]:
        result = {
            'defeater_ids': self.defeater_ids
        }
        if self.defeat_type:
            result['defeat_type'] = self.defeat_type.value
        if self.attack_point:
            result['attack_point'] = self.attack_point
        if self.cycle_members:
            result['cycle_members'] = self.cycle_members
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DefeatInfo':
        defeat_type = None
        if 'defeat_type' in data:
            defeat_type = DefeatType(data['defeat_type'])
        return cls(
            defeater_ids=data.get('defeater_ids', []),
            defeat_type=defeat_type,
            attack_point=data.get('attack_point'),
            cycle_members=data.get('cycle_members', [])
        )


@dataclass
class EpistemicStatus:
    """
    Complete epistemic status of a belief.

    Combines:
    - Spohn ranking (degree of belief/disbelief)
    - Pollock warrant (defeasible justification)

    This class represents HOW STRONGLY a belief is held and
    WHETHER it is justified, separate from WHAT is believed
    (PropositionalContent) and WHERE it comes from (Provenance).
    """
    ranks: RankPair = field(default_factory=RankPair)
    warrant_status: WarrantStatus = WarrantStatus.UNGROUNDED
    defeat_info: Optional[DefeatInfo] = None
    prima_facie_warranted: bool = False
    reinstatement_chain: List[str] = field(default_factory=list)
    rank_history: List[RankHistoryEntry] = field(default_factory=list)
    last_computed: Optional[datetime] = None

    # Per panel review: max 100 history entries
    MAX_HISTORY_SIZE = 100

    def __post_init__(self):
        """Ensure warrant_status is enum."""
        if isinstance(self.warrant_status, str):
            self.warrant_status = WarrantStatus(self.warrant_status)

    @property
    def rank(self) -> int:
        """Convenience accessor for rank."""
        return self.ranks.rank

    @property
    def neg_rank(self) -> int:
        """Convenience accessor for neg_rank."""
        return self.ranks.neg_rank

    @property
    def firmness(self) -> int:
        """Convenience accessor for firmness."""
        return self.ranks.firmness

    @property
    def believed(self) -> bool:
        """Convenience accessor for believed status."""
        return self.ranks.believed

    @property
    def is_warranted(self) -> bool:
        """Check if belief is currently warranted."""
        return self.warrant_status == WarrantStatus.WARRANTED

    @property
    def is_defeated(self) -> bool:
        """Check if belief is currently defeated."""
        return self.warrant_status == WarrantStatus.DEFEATED

    @property
    def is_suspended(self) -> bool:
        """Check if belief is in a defeat cycle."""
        return self.warrant_status == WarrantStatus.SUSPENDED

    @property
    def is_grounded(self) -> bool:
        """Check if belief has grounding (not UNGROUNDED)."""
        return self.warrant_status != WarrantStatus.UNGROUNDED

    def update_ranks(self, new_rank: int, new_neg_rank: int,
                     reason: str, evidence_id: Optional[str] = None):
        """
        Update ranks with history tracking.
        """
        # Record history
        entry = RankHistoryEntry(
            timestamp=datetime.now(),
            old_rank=self.ranks.rank,
            new_rank=new_rank,
            old_neg_rank=self.ranks.neg_rank,
            new_neg_rank=new_neg_rank,
            reason=reason,
            evidence_id=evidence_id
        )
        self.rank_history.append(entry)

        # Purge old history if needed
        if len(self.rank_history) > self.MAX_HISTORY_SIZE:
            self.rank_history = self.rank_history[-self.MAX_HISTORY_SIZE:]

        # Update ranks
        self.ranks = RankPair(rank=new_rank, neg_rank=new_neg_rank)
        self.last_computed = datetime.now()

    def apply_defeat(self, defeater_id: str, defeat_type: DefeatType,
                     attack_point: Optional[str] = None):
        """
        Apply defeat to this belief.
        """
        if self.defeat_info is None:
            self.defeat_info = DefeatInfo()

        if defeater_id not in self.defeat_info.defeater_ids:
            self.defeat_info.defeater_ids.append(defeater_id)

        self.defeat_info.defeat_type = defeat_type
        if attack_point:
            self.defeat_info.attack_point = attack_point

        self.warrant_status = WarrantStatus.DEFEATED
        self.last_computed = datetime.now()

    def clear_defeat(self, defeater_id: str):
        """
        Remove a defeater (e.g., if the defeater is itself defeated).
        May trigger reinstatement.
        """
        if self.defeat_info and defeater_id in self.defeat_info.defeater_ids:
            self.defeat_info.defeater_ids.remove(defeater_id)

            # If no more defeaters, potentially reinstate
            if not self.defeat_info.defeater_ids:
                if self.prima_facie_warranted:
                    self.warrant_status = WarrantStatus.WARRANTED
                    self.reinstatement_chain.append(defeater_id)
                self.defeat_info = None

        self.last_computed = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = {
            'rank': self.ranks.rank,
            'neg_rank': self.ranks.neg_rank,
            'firmness': self.ranks.firmness,
            'believed': self.ranks.believed,
            'warrant_status': self.warrant_status.value,
            'prima_facie_warranted': self.prima_facie_warranted,
        }

        if self.defeat_info:
            result['defeat_info'] = self.defeat_info.to_dict()
        if self.reinstatement_chain:
            result['reinstatement_chain'] = self.reinstatement_chain
        if self.rank_history:
            result['rank_history'] = [e.to_dict() for e in self.rank_history]
        if self.last_computed:
            result['last_computed'] = self.last_computed.isoformat()

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EpistemicStatus':
        """Create from dictionary."""
        ranks = RankPair(
            rank=data.get('rank', 0),
            neg_rank=data.get('neg_rank', 0)
        )

        defeat_info = None
        if 'defeat_info' in data:
            defeat_info = DefeatInfo.from_dict(data['defeat_info'])

        rank_history = []
        if 'rank_history' in data:
            rank_history = [RankHistoryEntry.from_dict(e) for e in data['rank_history']]

        last_computed = None
        if 'last_computed' in data:
            last_computed = datetime.fromisoformat(data['last_computed'])

        return cls(
            ranks=ranks,
            warrant_status=WarrantStatus(data.get('warrant_status', 'UNGROUNDED')),
            defeat_info=defeat_info,
            prima_facie_warranted=data.get('prima_facie_warranted', False),
            reinstatement_chain=data.get('reinstatement_chain', []),
            rank_history=rank_history,
            last_computed=last_computed
        )

    @classmethod
    def from_legacy_credence(cls, credence_value: float, uncertainty: float,
                             level: str = None) -> 'EpistemicStatus':
        """
        Create EpistemicStatus from legacy credence format.
        Used for migration from v1 to v2.
        """
        ranks = RankPair.from_credence(credence_value, uncertainty)

        # Infer initial warrant from level
        # Observational beliefs are prima facie warranted
        prima_facie = level == 'OBSERVATIONAL' if level else False
        warrant = WarrantStatus.WARRANTED if prima_facie else WarrantStatus.WARRANTED

        return cls(
            ranks=ranks,
            warrant_status=warrant,
            prima_facie_warranted=prima_facie,
            last_computed=datetime.now()
        )


# ============================================================
# SPOHN CONDITIONALIZATION
# ============================================================

def conditionalize(ranks: RankPair, evidence_rank: int, firmness: int) -> RankPair:
    """
    Spohn conditionalization on new evidence.

    Formula: κ_new(B) = min(κ(B|E), κ(B|¬E) + n)

    Where:
    - E is the evidence
    - n is the firmness of E (how strongly we accept E)
    - κ(B|E) = κ(B∧E) - κ(E) is the conditional rank

    This is a simplified version for single-proposition update.
    Full implementation requires the entire ranking function.

    Args:
        ranks: Current rank pair for belief B
        evidence_rank: Rank of evidence E (how disbelieved E is)
        firmness: How firmly we accept the evidence (n in Spohn's formula)

    Returns:
        New RankPair after conditionalization
    """
    # Simplified: if evidence supports B, decrease rank of B
    # if evidence contradicts B, increase rank of B
    # This is an approximation pending full ranking function implementation

    if evidence_rank == 0:
        # Evidence is believed - it supports the update
        # Decrease disbelief in B, increase disbelief in ¬B
        new_rank = max(0, ranks.rank - firmness)
        new_neg_rank = ranks.neg_rank + firmness
    else:
        # Evidence is disbelieved - weak update
        # Slight increase in disbelief of B
        new_rank = ranks.rank + max(0, firmness - evidence_rank)
        new_neg_rank = max(0, ranks.neg_rank - 1)

    return RankPair(rank=new_rank, neg_rank=new_neg_rank)


def conditional_rank(rank_b: int, rank_e: int, rank_b_and_e: int) -> int:
    """
    Compute conditional rank κ(B|E).

    Formula: κ(B|E) = κ(B∧E) - κ(E)

    This requires knowing the rank of the conjunction,
    which in turn requires the full ranking function.
    """
    return max(0, rank_b_and_e - rank_e)
