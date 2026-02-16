"""
Learning Theory Agent — Agents that update their scope understanding over time.

The agent starts with a baseline profile but learns from:
1. Expert corrections ("you said ORTHOGONAL but this is actually CONFIRMS")
2. Paper evidence ("the paper used aged WOOD, not rusty steel")
3. Clustered patterns ("multiple aged wood claims → add to includes")

This implements active learning where the agent builds its theory profile
incrementally from reviewed decisions.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json
from pathlib import Path
from enum import Enum

from .theory_agent_council import TheoryAgent, AgentVerdict, Judgment


class CorrectionType(str, Enum):
    """Type of correction to agent's judgment."""
    SHOULD_INCLUDE = "should_include"      # Agent said ORTHOGONAL, was wrong
    SHOULD_EXCLUDE = "should_exclude"      # Agent said CONFIRMS, was wrong
    SCOPE_EXTENSION = "scope_extension"    # New type of stimulus now included
    SCOPE_RESTRICTION = "scope_restriction"  # Previously included now excluded
    EDGE_RESOLVED = "edge_resolved"        # Edge case now has clear judgment


@dataclass
class DecisionRecord:
    """Record of a single decision and its outcome."""
    claim_id: str
    claim_statement: str
    lhs_vars: List[str]
    rhs_var: str
    polarity: str
    paper_id: str

    # Agent's original decision
    original_judgment: Judgment
    original_confidence: float
    original_reasoning: str
    decision_timestamp: datetime

    # Correction (if any)
    was_corrected: bool = False
    corrected_judgment: Optional[Judgment] = None
    correction_type: Optional[CorrectionType] = None
    correction_reason: str = ""
    correction_timestamp: Optional[datetime] = None
    corrected_by: str = ""  # "expert", "paper_evidence", "auto"

    # Evidence from paper (if reviewed)
    paper_stimuli_used: List[str] = field(default_factory=list)
    paper_outcome_measured: str = ""
    paper_context: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "claim_statement": self.claim_statement,
            "lhs_vars": self.lhs_vars,
            "rhs_var": self.rhs_var,
            "polarity": self.polarity,
            "paper_id": self.paper_id,
            "original_judgment": self.original_judgment.value,
            "original_confidence": self.original_confidence,
            "original_reasoning": self.original_reasoning,
            "decision_timestamp": self.decision_timestamp.isoformat(),
            "was_corrected": self.was_corrected,
            "corrected_judgment": self.corrected_judgment.value if self.corrected_judgment else None,
            "correction_type": self.correction_type.value if self.correction_type else None,
            "correction_reason": self.correction_reason,
            "correction_timestamp": self.correction_timestamp.isoformat() if self.correction_timestamp else None,
            "corrected_by": self.corrected_by,
            "paper_stimuli_used": self.paper_stimuli_used,
            "paper_outcome_measured": self.paper_outcome_measured,
            "paper_context": self.paper_context,
        }


@dataclass
class LearnedRule:
    """A rule learned from corrections."""
    rule_id: str
    rule_type: str  # "stimulus_include", "stimulus_exclude", "outcome_include", etc.
    pattern: str    # The variable pattern this rule applies to
    condition: str  # When this rule applies
    learned_from: List[str]  # Claim IDs that taught this
    confidence: float
    created_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "rule_type": self.rule_type,
            "pattern": self.pattern,
            "condition": self.condition,
            "learned_from": self.learned_from,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat(),
        }


class LearningTheoryAgent(TheoryAgent):
    """
    A theory agent that learns from corrections and extends its scope.

    Learning mechanisms:
    1. Decision logging: Every decision is recorded
    2. Correction feedback: Experts can correct wrong decisions
    3. Pattern extraction: Similar corrections become new rules
    4. Confidence updating: Confidence increases with confirmed decisions
    """

    def __init__(self, profile_module, learning_dir: str = None):
        super().__init__(profile_module)

        # Learning state
        self.decision_log: List[DecisionRecord] = []
        self.learned_rules: List[LearnedRule] = []
        self.learned_includes: List[str] = []
        self.learned_excludes: List[str] = []
        self.learned_edge_cases: List[Dict[str, str]] = []

        # Persistence
        self.learning_dir = Path(learning_dir) if learning_dir else None
        if self.learning_dir:
            self._load_learning_state()

    def evaluate_claim(
        self,
        claim_id: str,
        claim_statement: str,
        lhs_vars: List[str],
        rhs_var: str,
        polarity: str,
        paper_id: str = "",
    ) -> AgentVerdict:
        """
        Evaluate claim using base profile + learned rules.
        """
        # First check learned rules
        learned_verdict = self._check_learned_rules(lhs_vars, rhs_var, polarity)
        if learned_verdict:
            verdict = AgentVerdict(
                theory_id=self.theory_id,
                theory_name=self.theory_name,
                judgment=learned_verdict[0],
                confidence=learned_verdict[1],
                reasoning=f"Learned rule: {learned_verdict[2]}",
            )
        else:
            # Fall back to base profile
            verdict = super().evaluate_claim(
                claim_id, claim_statement, lhs_vars, rhs_var, polarity, paper_id
            )

        # Log the decision
        self._log_decision(
            claim_id, claim_statement, lhs_vars, rhs_var, polarity, paper_id, verdict
        )

        return verdict

    def _check_learned_rules(
        self, lhs_vars: List[str], rhs_var: str, polarity: str
    ) -> Optional[Tuple[Judgment, float, str]]:
        """Check if learned rules apply to this claim."""
        lhs_text = " ".join(lhs_vars).lower()

        # Check learned includes
        for incl in self.learned_includes:
            if incl.lower() in lhs_text:
                if polarity == "positive":
                    return (Judgment.CONFIRMS, 0.8, f"Learned: '{incl}' is included")
                elif polarity == "negative":
                    return (Judgment.DISCONFIRMS, 0.8, f"Learned: '{incl}' is included")

        # Check learned excludes
        for excl in self.learned_excludes:
            if excl.lower() in lhs_text:
                return (Judgment.ORTHOGONAL, 0.8, f"Learned: '{excl}' is excluded")

        return None

    def _log_decision(
        self,
        claim_id: str,
        claim_statement: str,
        lhs_vars: List[str],
        rhs_var: str,
        polarity: str,
        paper_id: str,
        verdict: AgentVerdict,
    ) -> None:
        """Log a decision for future learning."""
        record = DecisionRecord(
            claim_id=claim_id,
            claim_statement=claim_statement,
            lhs_vars=lhs_vars,
            rhs_var=rhs_var,
            polarity=polarity,
            paper_id=paper_id,
            original_judgment=verdict.judgment,
            original_confidence=verdict.confidence,
            original_reasoning=verdict.reasoning,
            decision_timestamp=datetime.now(),
        )
        self.decision_log.append(record)

    def receive_correction(
        self,
        claim_id: str,
        correct_judgment: Judgment,
        reason: str,
        corrected_by: str = "expert",
        paper_stimuli: List[str] = None,
        paper_outcome: str = "",
    ) -> bool:
        """
        Receive a correction for a previous decision.

        This updates the decision log and may learn new rules.

        Args:
            claim_id: ID of the claim being corrected
            correct_judgment: What the judgment should have been
            reason: Why this is the correct judgment
            corrected_by: Who/what made the correction
            paper_stimuli: Specific stimuli used in the paper
            paper_outcome: Specific outcome measured

        Returns:
            True if correction was applied
        """
        # Find the decision
        record = None
        for r in self.decision_log:
            if r.claim_id == claim_id:
                record = r
                break

        if not record:
            return False

        # Skip if already corrected
        if record.was_corrected:
            return False

        # Record the correction
        record.was_corrected = True
        record.corrected_judgment = correct_judgment
        record.correction_reason = reason
        record.correction_timestamp = datetime.now()
        record.corrected_by = corrected_by
        if paper_stimuli:
            record.paper_stimuli_used = paper_stimuli
        if paper_outcome:
            record.paper_outcome_measured = paper_outcome

        # Determine correction type
        if record.original_judgment == Judgment.ORTHOGONAL and correct_judgment in (Judgment.CONFIRMS, Judgment.DISCONFIRMS):
            record.correction_type = CorrectionType.SHOULD_INCLUDE
            self._learn_from_inclusion(record)
        elif record.original_judgment in (Judgment.CONFIRMS, Judgment.DISCONFIRMS) and correct_judgment == Judgment.ORTHOGONAL:
            record.correction_type = CorrectionType.SHOULD_EXCLUDE
            self._learn_from_exclusion(record)
        elif record.original_judgment == Judgment.EDGE_CASE:
            record.correction_type = CorrectionType.EDGE_RESOLVED
            self._learn_from_edge_resolution(record)

        self._save_learning_state()
        return True

    def _learn_from_inclusion(self, record: DecisionRecord) -> None:
        """Learn from a correction that something should be included."""
        # Extract the key stimulus term
        if record.paper_stimuli_used:
            # Use the specific stimulus from paper
            for stim in record.paper_stimuli_used:
                if stim not in self.learned_includes:
                    self.learned_includes.append(stim)
                    print(f"Learned: '{stim}' should be INCLUDED in {self.theory_name}")
        else:
            # Use the variable names
            for var in record.lhs_vars:
                var_clean = var.split(".")[-1].replace("_", " ")
                if var_clean not in self.learned_includes:
                    self.learned_includes.append(var_clean)
                    print(f"Learned: '{var_clean}' should be INCLUDED in {self.theory_name}")

    def _learn_from_exclusion(self, record: DecisionRecord) -> None:
        """Learn from a correction that something should be excluded."""
        for var in record.lhs_vars:
            var_clean = var.split(".")[-1].replace("_", " ")
            if var_clean not in self.learned_excludes:
                self.learned_excludes.append(var_clean)
                print(f"Learned: '{var_clean}' should be EXCLUDED from {self.theory_name}")

    def _learn_from_edge_resolution(self, record: DecisionRecord) -> None:
        """Learn from resolving an edge case."""
        if record.corrected_judgment in (Judgment.CONFIRMS, Judgment.DISCONFIRMS):
            self._learn_from_inclusion(record)
        elif record.corrected_judgment == Judgment.ORTHOGONAL:
            self._learn_from_exclusion(record)

    def get_learning_summary(self) -> Dict[str, Any]:
        """Get summary of what the agent has learned."""
        total_decisions = len(self.decision_log)
        corrections = [r for r in self.decision_log if r.was_corrected]

        return {
            "theory_id": self.theory_id,
            "theory_name": self.theory_name,
            "total_decisions": total_decisions,
            "total_corrections": len(corrections),
            "accuracy": (total_decisions - len(corrections)) / total_decisions if total_decisions > 0 else 1.0,
            "learned_includes": self.learned_includes,
            "learned_excludes": self.learned_excludes,
            "learned_edge_cases": self.learned_edge_cases,
        }

    def _save_learning_state(self) -> None:
        """Save learning state to disk."""
        if not self.learning_dir:
            return

        self.learning_dir.mkdir(parents=True, exist_ok=True)

        state = {
            "theory_id": self.theory_id,
            "learned_includes": self.learned_includes,
            "learned_excludes": self.learned_excludes,
            "learned_edge_cases": self.learned_edge_cases,
            "decision_log": [r.to_dict() for r in self.decision_log],
            "learned_rules": [r.to_dict() for r in self.learned_rules],
        }

        state_file = self.learning_dir / f"{self.theory_id.replace(':', '_')}_learning.json"
        with open(state_file, "w") as f:
            json.dump(state, f, indent=2)

    def _load_learning_state(self) -> None:
        """Load learning state from disk."""
        if not self.learning_dir:
            return

        state_file = self.learning_dir / f"{self.theory_id.replace(':', '_')}_learning.json"
        if not state_file.exists():
            return

        with open(state_file, "r") as f:
            state = json.load(f)

        self.learned_includes = state.get("learned_includes", [])
        self.learned_excludes = state.get("learned_excludes", [])
        self.learned_edge_cases = state.get("learned_edge_cases", [])
        # Note: decision_log and learned_rules would need proper deserialization


# =============================================================================
# EXAMPLE: Learning in action
# =============================================================================

def demo_learning():
    """Demonstrate learning agent in action."""
    import importlib.util

    # Load biophilia profile
    profile_path = Path("src/theories/profiles/biophilia_profile.py")
    spec = importlib.util.spec_from_file_location("biophilia_profile", profile_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Create learning agent
    agent = LearningTheoryAgent(module, learning_dir="data/theory_learning")

    print(f"Created learning agent: {agent.theory_name}")
    print(f"  Base includes: {len(agent.stimulus_includes)}")
    print(f"  Learned includes: {agent.learned_includes}")

    # Make a decision
    verdict = agent.evaluate_claim(
        claim_id="test_aged_wood",
        claim_statement="Aged wood panels improve emotional response",
        lhs_vars=["env.aged_wood_panels"],
        rhs_var="aff.emotional_response",
        polarity="positive",
        paper_id="test_paper_001",
    )

    print(f"\nDecision for 'aged wood panels':")
    print(f"  Judgment: {verdict.judgment.value}")
    print(f"  Reasoning: {verdict.reasoning}")

    # Expert corrects: aged wood IS biophilia
    print("\n--- Expert correction: Aged wood IS biophilia ---")
    agent.receive_correction(
        claim_id="test_aged_wood",
        correct_judgment=Judgment.CONFIRMS,
        reason="Aged wood shows organic process, connects to biophilia's living systems",
        corrected_by="expert",
        paper_stimuli=["aged oak panels", "weathered cedar"],
    )

    # Now try another aged wood claim
    verdict2 = agent.evaluate_claim(
        claim_id="test_aged_oak",
        claim_statement="Aged oak improves preference",
        lhs_vars=["env.aged_oak"],
        rhs_var="aff.preference",
        polarity="positive",
        paper_id="test_paper_002",
    )

    print(f"\nDecision for 'aged oak' (after learning):")
    print(f"  Judgment: {verdict2.judgment.value}")
    print(f"  Reasoning: {verdict2.reasoning}")

    # Show learning summary
    print(f"\nLearning summary:")
    summary = agent.get_learning_summary()
    print(f"  Total decisions: {summary['total_decisions']}")
    print(f"  Corrections: {summary['total_corrections']}")
    print(f"  Learned includes: {summary['learned_includes']}")


if __name__ == "__main__":
    demo_learning()
