"""
Theory Agent Council — Multi-Agent Architecture for Claim Matching.

Each theory has an "expert agent" that embodies its perspective.
When a claim arrives, the council convenes and each agent votes on
whether the claim falls within its theory's scope.

This architecture captures:
1. Theory-specific scope knowledge
2. Competing claims between theories (a claim might be "owned" by multiple theories)
3. Epistemic disagreements (when agents disagree, that's interesting data)

Usage:
    council = TheoryAgentCouncil()
    verdicts = council.evaluate_claim(claim)

    # verdicts is a dict: {theory_id: {judgment, reasoning, confidence}}
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import importlib
import os
from pathlib import Path


class Judgment(str, Enum):
    """Theory agent judgment on a claim."""
    CONFIRMS = "confirms"          # Positive evidence for theory predictions
    DISCONFIRMS = "disconfirms"    # Negative evidence against theory predictions
    CHALLENGES = "challenges"       # Methodological/theoretical critique
    ORTHOGONAL = "orthogonal"      # Outside this theory's scope
    EDGE_CASE = "edge_case"        # Requires reading paper to judge
    NEEDS_INFO = "needs_info"      # Missing critical information


@dataclass
class AgentVerdict:
    """A single theory agent's verdict on a claim."""
    theory_id: str
    theory_name: str
    judgment: Judgment
    confidence: float  # 0-1, how confident the agent is
    reasoning: str
    relevant_scope_items: List[str] = field(default_factory=list)
    competing_theories: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "theory_id": self.theory_id,
            "theory_name": self.theory_name,
            "judgment": self.judgment.value,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "relevant_scope_items": self.relevant_scope_items,
            "competing_theories": self.competing_theories,
        }


@dataclass
class CouncilVerdict:
    """The full council's verdict on a claim."""
    claim_id: str
    claim_statement: str
    agent_verdicts: List[AgentVerdict]
    consensus: Optional[str] = None  # If all agents agree
    contested_by: List[str] = field(default_factory=list)  # Theories that claim ownership

    @property
    def has_consensus(self) -> bool:
        """True if all non-orthogonal verdicts agree."""
        relevant = [v for v in self.agent_verdicts if v.judgment != Judgment.ORTHOGONAL]
        if not relevant:
            return True  # All orthogonal = consensus (nothing claims it)
        judgments = set(v.judgment for v in relevant)
        return len(judgments) == 1

    @property
    def claiming_theories(self) -> List[str]:
        """Theories that claim this falls under their scope."""
        return [v.theory_id for v in self.agent_verdicts
                if v.judgment in (Judgment.CONFIRMS, Judgment.DISCONFIRMS)]

    @property
    def is_contested(self) -> bool:
        """True if multiple theories claim the claim."""
        return len(self.claiming_theories) > 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "claim_statement": self.claim_statement,
            "agent_verdicts": [v.to_dict() for v in self.agent_verdicts],
            "has_consensus": self.has_consensus,
            "claiming_theories": self.claiming_theories,
            "is_contested": self.is_contested,
        }


class TheoryAgent:
    """
    An agent that embodies a single theory's perspective.

    The agent knows:
    - What mechanisms the theory posits
    - What stimuli fall under its scope
    - What outcomes it predicts
    - What it does NOT claim to explain
    """

    def __init__(self, profile_module):
        """
        Initialize from a theory profile module.

        Args:
            profile_module: A module with THEORY_ID, THEORY_NAME,
                           EXPLAINS, DOES_NOT_EXPLAIN, etc.
        """
        self.theory_id = profile_module.THEORY_ID
        self.theory_name = profile_module.THEORY_NAME
        self.core_mechanism = profile_module.CORE_MECHANISM
        self.explains = profile_module.EXPLAINS
        self.does_not_explain = profile_module.DOES_NOT_EXPLAIN
        self.stimulus_includes = profile_module.STIMULUS_INCLUDES
        self.stimulus_excludes = profile_module.STIMULUS_EXCLUDES
        self.stimulus_edge_cases = profile_module.STIMULUS_EDGE_CASES
        self.predicted_outcomes = profile_module.PREDICTED_OUTCOMES
        self.not_predicted_outcomes = profile_module.NOT_PREDICTED_OUTCOMES
        self.matching_prompt = profile_module.MATCHING_PROMPT
        self.few_shot_examples = profile_module.FEW_SHOT_EXAMPLES

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
        Evaluate whether a claim falls under this theory's scope.

        This is a rule-based implementation. For production, this would
        call an LLM with self.matching_prompt and self.few_shot_examples.

        Args:
            claim_id: Claim identifier
            claim_statement: The claim text
            lhs_vars: Left-hand side variables (stimulus/antecedent)
            rhs_var: Right-hand side variable (outcome/consequent)
            polarity: positive/negative/null
            paper_id: Paper identifier

        Returns:
            AgentVerdict with judgment and reasoning
        """
        # Simple rule-based matching (placeholder for LLM call)

        # Check if stimulus is in our scope
        stimulus_match = self._check_stimulus_scope(lhs_vars)
        outcome_match = self._check_outcome_scope(rhs_var)

        # Determine judgment
        if stimulus_match == "excluded" or outcome_match == "excluded":
            return AgentVerdict(
                theory_id=self.theory_id,
                theory_name=self.theory_name,
                judgment=Judgment.ORTHOGONAL,
                confidence=0.8,
                reasoning=f"Stimulus or outcome outside {self.theory_name} scope",
            )

        if stimulus_match == "edge_case" or outcome_match == "edge_case":
            return AgentVerdict(
                theory_id=self.theory_id,
                theory_name=self.theory_name,
                judgment=Judgment.EDGE_CASE,
                confidence=0.5,
                reasoning=f"Requires checking paper for specific stimuli/measures",
            )

        if stimulus_match == "included" and outcome_match == "included":
            if polarity == "positive":
                return AgentVerdict(
                    theory_id=self.theory_id,
                    theory_name=self.theory_name,
                    judgment=Judgment.CONFIRMS,
                    confidence=0.7,
                    reasoning=f"Stimulus and outcome within {self.theory_name} scope, positive finding",
                )
            elif polarity == "negative":
                return AgentVerdict(
                    theory_id=self.theory_id,
                    theory_name=self.theory_name,
                    judgment=Judgment.DISCONFIRMS,
                    confidence=0.7,
                    reasoning=f"Stimulus and outcome within {self.theory_name} scope, negative finding",
                )
            else:
                return AgentVerdict(
                    theory_id=self.theory_id,
                    theory_name=self.theory_name,
                    judgment=Judgment.EDGE_CASE,
                    confidence=0.5,
                    reasoning=f"Within scope but polarity unclear",
                )

        # Default: uncertain
        return AgentVerdict(
            theory_id=self.theory_id,
            theory_name=self.theory_name,
            judgment=Judgment.NEEDS_INFO,
            confidence=0.3,
            reasoning="Insufficient information to determine scope match",
        )

    def _check_stimulus_scope(self, lhs_vars: List[str]) -> str:
        """Check if stimulus variables are in scope."""
        lhs_text = " ".join(lhs_vars).lower()

        # Check exclusions first
        for excl in self.stimulus_excludes:
            if any(word in lhs_text for word in excl.lower().split()):
                return "excluded"

        # Check edge cases
        for ec in self.stimulus_edge_cases:
            if ec["item"].lower() in lhs_text:
                return "edge_case"

        # Check inclusions
        for incl in self.stimulus_includes:
            if any(word in lhs_text for word in incl.lower().split()[:2]):
                return "included"

        return "unknown"

    def _check_outcome_scope(self, rhs_var: str) -> str:
        """Check if outcome variable is in scope."""
        rhs_text = rhs_var.lower()

        # Check exclusions first
        for excl in self.not_predicted_outcomes:
            if any(word in rhs_text for word in excl.lower().split()[:2]):
                return "excluded"

        # Check inclusions
        for incl in self.predicted_outcomes:
            if any(word in rhs_text for word in incl.lower().split()[:2]):
                return "included"

        return "unknown"


class TheoryAgentCouncil:
    """
    A council of theory agents that collectively evaluate claims.

    Usage:
        council = TheoryAgentCouncil()
        council.load_agents_from_profiles()
        verdict = council.evaluate_claim(claim)
    """

    def __init__(self):
        self.agents: Dict[str, TheoryAgent] = {}

    def add_agent(self, agent: TheoryAgent) -> None:
        """Add a theory agent to the council."""
        self.agents[agent.theory_id] = agent

    def load_agents_from_profiles(self, profiles_dir: str = None) -> int:
        """
        Load all theory agents from profile modules.

        Args:
            profiles_dir: Directory containing profile modules

        Returns:
            Number of agents loaded
        """
        if profiles_dir is None:
            profiles_dir = Path(__file__).parent / "profiles"
        else:
            profiles_dir = Path(profiles_dir)

        loaded = 0
        for profile_file in profiles_dir.glob("*_profile.py"):
            module_name = profile_file.stem
            try:
                # Import the profile module
                spec = importlib.util.spec_from_file_location(module_name, profile_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Create agent from profile
                agent = TheoryAgent(module)
                self.add_agent(agent)
                loaded += 1
            except Exception as e:
                print(f"Warning: Could not load {profile_file}: {e}")

        return loaded

    def evaluate_claim(
        self,
        claim_id: str,
        claim_statement: str,
        lhs_vars: List[str],
        rhs_var: str,
        polarity: str,
        paper_id: str = "",
    ) -> CouncilVerdict:
        """
        Convene the council to evaluate a claim.

        Each agent votes on whether the claim falls under its theory's scope.

        Returns:
            CouncilVerdict with all agent verdicts and consensus info
        """
        verdicts = []

        for agent in self.agents.values():
            verdict = agent.evaluate_claim(
                claim_id=claim_id,
                claim_statement=claim_statement,
                lhs_vars=lhs_vars,
                rhs_var=rhs_var,
                polarity=polarity,
                paper_id=paper_id,
            )
            verdicts.append(verdict)

        council_verdict = CouncilVerdict(
            claim_id=claim_id,
            claim_statement=claim_statement,
            agent_verdicts=verdicts,
        )

        return council_verdict

    def list_agents(self) -> List[str]:
        """List all registered theory agents."""
        return list(self.agents.keys())


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

def demo():
    """Demonstrate the theory agent council."""
    # Create council
    council = TheoryAgentCouncil()

    # Load agents from profiles
    n_loaded = council.load_agents_from_profiles()
    print(f"Loaded {n_loaded} theory agents: {council.list_agents()}")

    # Example claim
    verdict = council.evaluate_claim(
        claim_id="test_claim_1",
        claim_statement="Indoor plants positively affect office worker wellbeing",
        lhs_vars=["env.indoor_plants"],
        rhs_var="aff.wellbeing",
        polarity="positive",
        paper_id="test_paper",
    )

    print(f"\nClaim: {verdict.claim_statement}")
    print(f"Has consensus: {verdict.has_consensus}")
    print(f"Claiming theories: {verdict.claiming_theories}")
    print(f"Is contested: {verdict.is_contested}")

    for v in verdict.agent_verdicts:
        print(f"\n  {v.theory_name}:")
        print(f"    Judgment: {v.judgment.value}")
        print(f"    Confidence: {v.confidence}")
        print(f"    Reasoning: {v.reasoning}")


if __name__ == "__main__":
    demo()
