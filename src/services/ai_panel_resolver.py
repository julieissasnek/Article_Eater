"""
AI Panel Resolution Framework
==============================

Reusable framework for multi-agent panel resolution across ATLAS use cases:
- outcome_vocab: Canonical outcome vocabulary classification
- image_classification: Image type and relevance classification
- taxonomy_reconciliation: Overlapping taxonomy entry resolution
- annotation_qa: Annotation quality assessment

Architecture:
- Each panel has n panelists with different roles (domain expert, skeptic, etc.)
- Panelists vote on constrained or open-ended options
- Consensus detection follows social epistemology rules (SE-2)
- Disputes escalate to a capable model for final resolution
- All decisions logged for audit and analysis

Philosophy:
This framework operationalizes social epistemology by:
1. Encoding role-based perspectives (domain expert, skeptic, methodologist)
2. Detecting disagreement types (within-paradigm consensus vs. incommensurable)
3. Applying SE-2 rule: Average only for same-method, same-paradigm disputes
4. Escalating contested items to higher-tier models for resolution
5. Maintaining audit trail of all votes and reasoning

Date: 2026-02-28
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import json
from datetime import datetime

from src.agents.agent_core import call_llm, LLMConfig


class PanelistRole(Enum):
    """Role-based perspectives on the panel."""
    DOMAIN_EXPERT = "domain_expert"      # Deep domain knowledge
    METHODOLOGIST = "methodologist"      # Methods and validity focus
    SKEPTIC = "skeptic"                 # Questions assumptions, ~30% challenge rate
    INTEGRATOR = "integrator"           # Synthesis and coherence
    CALIBRATOR = "calibrator"           # Precision and edge cases


@dataclass
class PanelConfig:
    """Configuration for a panel resolution task."""
    panel_type: str  # "outcome_vocab", "image_classification", "taxonomy_reconciliation", "annotation_qa"
    n_panelists: int = 5  # Must be odd for majority voting
    consensus_threshold: float = 0.6  # Fraction of panelists that must agree
    confidence_floor: float = 0.3  # Minimum confidence score to count vote
    bulk_model: str = "gemini-2.5-flash"  # Fast model for bulk panelist work
    dispute_model: str = "claude-sonnet-4-20250514"  # Capable model for disputes
    max_retries: int = 2
    dry_run: bool = False

    def __post_init__(self):
        """Validate config."""
        if self.n_panelists % 2 == 0:
            raise ValueError(f"n_panelists must be odd; got {self.n_panelists}")
        if not (0.0 < self.consensus_threshold <= 1.0):
            raise ValueError(f"consensus_threshold must be in (0, 1]; got {self.consensus_threshold}")
        if not (0.0 <= self.confidence_floor < 1.0):
            raise ValueError(f"confidence_floor must be in [0, 1); got {self.confidence_floor}")


@dataclass
class PanelistVote:
    """A single panelist's vote on a resolution item."""
    panelist_id: str
    role: PanelistRole
    decision: str  # The chosen option/classification
    confidence: float  # 0-1, how confident the panelist is
    reasoning: str
    dissent_note: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict."""
        return {
            "panelist_id": self.panelist_id,
            "role": self.role.value,
            "decision": self.decision,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "dissent_note": self.dissent_note,
        }


@dataclass
class ResolutionResult:
    """Outcome of resolving a single item through the panel."""
    item_id: str
    decision: str  # The winning decision
    confidence: float  # Aggregate confidence 0-1
    consensus_type: str  # "unanimous", "majority", "disputed", "escalated"
    votes: List[PanelistVote]
    dissenting_views: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    resolved_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict."""
        return {
            "item_id": self.item_id,
            "decision": self.decision,
            "confidence": self.confidence,
            "consensus_type": self.consensus_type,
            "votes": [v.to_dict() for v in self.votes],
            "dissenting_views": self.dissenting_views,
            "metadata": self.metadata,
            "resolved_at": self.resolved_at,
        }


class PanelResolver:
    """
    Multi-agent panel for resolving items through consensus voting.

    Usage:
        config = PanelConfig(panel_type="outcome_vocab")
        resolver = PanelResolver(config)
        results = resolver.resolve_batch(items)
    """

    # Prompt templates keyed by panel_type
    PROMPT_TEMPLATES = {
        "outcome_vocab": """You are a {role} on a panel evaluating outcome vocabulary.

CONTEXT:
- Item ID: {item_id}
- Raw outcome term: {term}
- Context: {context}

CANONICAL OUTCOMES (choose exactly one):
{options}

INSTRUCTIONS:
As a {role_description}, evaluate which canonical outcome this raw term should map to.
Consider specificity, semantic fit, and scope of applicability.

Respond in JSON format:
{{
  "decision": "the_chosen_outcome",
  "confidence": 0.85,
  "reasoning": "Your 2-3 sentence explanation"
}}
""",

        "image_classification": """You are a {role} on a panel evaluating image classification.

CONTEXT:
- Item ID: {item_id}
- Image metadata: {image_metadata}
- Context: {context}

IMAGE TYPES:
{options}

INSTRUCTIONS:
As a {role_description}, classify this image into the appropriate type and assess CVA relevance.

Respond in JSON format:
{{
  "decision": "image_type",
  "confidence": 0.75,
  "reasoning": "Your 2-3 sentence explanation"
}}
""",

        "taxonomy_reconciliation": """You are a {role} on a panel evaluating taxonomy reconciliation.

CONTEXT:
- Item ID: {item_id}
- Entry 1: {entry1}
- Entry 2: {entry2}
- Scope/Usage: {context}

RECONCILIATION OPTIONS:
{options}

INSTRUCTIONS:
As a {role_description}, decide whether these entries should be merged, kept separate, or one deprecated.

Respond in JSON format:
{{
  "decision": "merge|keep_separate|deprecate_entry1|deprecate_entry2",
  "confidence": 0.80,
  "reasoning": "Your 2-3 sentence explanation"
}}
""",

        "annotation_qa": """You are a {role} on a panel evaluating annotation quality.

CONTEXT:
- Item ID: {item_id}
- Annotation: {annotation}
- Source text: {source_text}
- Question: {context}

QUALITY RATINGS:
{options}

INSTRUCTIONS:
As a {role_description}, rate the quality of this annotation against the source text.

Respond in JSON format:
{{
  "decision": "GOOD|FAIR|POOR",
  "confidence": 0.90,
  "reasoning": "Your 2-3 sentence explanation"
}}
""",
    }

    # Role-specific system prompts
    ROLE_PROMPTS = {
        PanelistRole.DOMAIN_EXPERT: """You are a domain expert with deep knowledge of the subject area.
Your votes should emphasize semantic accuracy, domain conventions, and scope appropriateness.
Prioritize correctness over edge cases.""",

        PanelistRole.METHODOLOGIST: """You are a methodologist focused on rigor and validity.
Your votes should emphasize proper evidence, replicability, and sound reasoning.
Challenge claims that lack sufficient basis.""",

        PanelistRole.SKEPTIC: """You are a principled skeptic who questions assumptions.
Your votes should be cautiously critical: challenge easy answers, look for hidden assumptions.
You should dissent from consensus ~30% of the time when you have epistemic grounds.""",

        PanelistRole.INTEGRATOR: """You are an integrator seeking coherence and synthesis.
Your votes should consider how this decision fits with adjacent decisions and the broader system.
Prefer options that reduce fragmentation.""",

        PanelistRole.CALIBRATOR: """You are a calibrator focused on precision and edge cases.
Your votes should be meticulous: careful with boundary conditions, clear on exceptions.
Mark high uncertainty when warranted.""",
    }

    def __init__(self, config: PanelConfig):
        """Initialize the panel resolver with config."""
        self.config = config
        self.session_decisions: List[ResolutionResult] = []
        self._validate_config()

    def _validate_config(self):
        """Validate that panel type is supported."""
        if self.config.panel_type not in self.PROMPT_TEMPLATES:
            raise ValueError(
                f"Unsupported panel_type '{self.config.panel_type}'. "
                f"Supported: {list(self.PROMPT_TEMPLATES.keys())}"
            )

    def resolve_batch(
        self,
        items: List[Dict[str, Any]],
        dry_run: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Resolve a batch of items through panel voting.

        Each item dict should contain:
        - 'id': unique identifier
        - 'term'/'image'/'text': the content to resolve
        - 'context': optional context string
        - 'options': optional list of constrained choices

        Args:
            items: List of items to resolve
            dry_run: Override config.dry_run if provided

        Returns:
            Dict with 'decisions' (list of ResolutionResult) and 'stats'
        """
        dry_run = dry_run if dry_run is not None else self.config.dry_run
        decisions = []

        for item in items:
            result = self._resolve_item(item, dry_run=dry_run)
            decisions.append(result)
            self.session_decisions.append(result)

        stats = self._compute_stats(decisions)
        return {
            "decisions": decisions,
            "stats": stats,
        }

    def _resolve_item(self, item: Dict[str, Any], dry_run: bool = False) -> ResolutionResult:
        """Resolve a single item."""
        item_id = item.get("id", "unknown")
        votes = []

        # Generate panelist roles for this item
        roles = self._assign_roles()

        # Collect votes from all panelists
        for idx, role in enumerate(roles):
            panelist_id = f"{item_id}_panelist_{idx}_{role.value}"
            vote = self._get_panelist_vote(item, panelist_id, role, dry_run=dry_run)
            votes.append(vote)

        # Compute consensus
        has_consensus, winning_decision, aggregate_confidence = self._compute_consensus(votes)

        # Determine consensus type
        if len(set(v.decision for v in votes if v.confidence >= self.config.confidence_floor)) == 1:
            consensus_type = "unanimous"
        elif has_consensus:
            consensus_type = "majority"
        else:
            consensus_type = "disputed"

        # Escalate if disputed and not dry_run
        if consensus_type == "disputed" and not dry_run:
            result = self.resolve_dispute(item, votes)
            return result

        # Collect dissenting views
        dissenting_views = [
            f"{v.role.value}: {v.dissent_note or v.reasoning}"
            for v in votes
            if v.decision != winning_decision and v.dissent_note
        ]

        result = ResolutionResult(
            item_id=item_id,
            decision=winning_decision,
            confidence=aggregate_confidence,
            consensus_type=consensus_type,
            votes=votes,
            dissenting_views=dissenting_views,
            metadata={
                "panel_type": self.config.panel_type,
                "n_panelists": len(votes),
            },
        )

        return result

    def resolve_dispute(self, item: Dict[str, Any], votes: List[PanelistVote]) -> ResolutionResult:
        """
        Escalate a disputed item to the dispute_model for resolution.

        The model receives full context of disagreement and reasoning.
        """
        item_id = item.get("id", "unknown")

        # Build dispute context
        dispute_prompt = self._build_dispute_prompt(item, votes)

        # Call dispute model
        try:
            llm_config = LLMConfig(
                provider="anthropic",
                model=self.config.dispute_model,
            )
            response = call_llm(dispute_prompt, llm_config)
            decision, confidence, reasoning = self._parse_dispute_response(response)
        except Exception as e:
            # Fallback: choose winning vote by confidence
            best_vote = max(votes, key=lambda v: v.confidence)
            decision = best_vote.decision
            confidence = best_vote.confidence
            reasoning = f"Dispute resolution failed ({e}); using highest-confidence vote"

        # Create escalated result
        dissenting_views = [
            f"{v.role.value} ({v.confidence:.2f}): {v.reasoning}"
            for v in votes
            if v.decision != decision
        ]

        result = ResolutionResult(
            item_id=item_id,
            decision=decision,
            confidence=confidence,
            consensus_type="escalated",
            votes=votes,
            dissenting_views=dissenting_views,
            metadata={
                "panel_type": self.config.panel_type,
                "escalation_reason": "disputed",
                "dispute_resolution": reasoning,
            },
        )

        return result

    def _get_panelist_vote(
        self,
        item: Dict[str, Any],
        panelist_id: str,
        role: PanelistRole,
        dry_run: bool = False,
    ) -> PanelistVote:
        """Get a single panelist's vote."""
        prompt = self._build_panelist_prompt(item, role)

        if dry_run:
            # Return mock vote with decision from item options
            options = item.get("options", ["option_a", "option_b"])
            decision = options[0] if options else "mock_decision"
            return PanelistVote(
                panelist_id=panelist_id,
                role=role,
                decision=decision,
                confidence=0.7,
                reasoning="[DRY RUN: mock vote]",
            )

        # Call LLM
        try:
            llm_config = LLMConfig(
                provider="gemini",
                model=self.config.bulk_model,
            )
            response = call_llm(prompt, llm_config)
            decision, confidence, reasoning = self._parse_vote(response, panelist_id, role)
        except Exception as e:
            decision = "UNRESOLVED"
            confidence = 0.0
            reasoning = f"Vote parsing error: {e}"

        return PanelistVote(
            panelist_id=panelist_id,
            role=role,
            decision=decision,
            confidence=confidence,
            reasoning=reasoning,
        )

    def _build_panelist_prompt(self, item: Dict[str, Any], role: PanelistRole) -> str:
        """Build a role-specific prompt for a panelist."""
        template = self.PROMPT_TEMPLATES[self.config.panel_type]
        role_description = self.ROLE_PROMPTS[role]

        # Extract item fields
        item_id = item.get("id", "unknown")
        term = item.get("term", item.get("image", item.get("text", "unknown")))
        context = item.get("context", "")
        options = item.get("options", [])

        # Format options
        if options:
            if isinstance(options[0], dict):
                options_text = "\n".join([f"- {opt.get('id', opt)}: {opt.get('label', opt)}" for opt in options])
            else:
                options_text = "\n".join([f"- {opt}" for opt in options])
        else:
            options_text = "(Open-ended; provide your best judgment)"

        # Handle different item types
        if self.config.panel_type == "outcome_vocab":
            prompt = template.format(
                role=role.value,
                role_description=role_description,
                item_id=item_id,
                term=term,
                context=context,
                options=options_text,
            )
        elif self.config.panel_type == "image_classification":
            image_metadata = item.get("metadata", {})
            prompt = template.format(
                role=role.value,
                role_description=role_description,
                item_id=item_id,
                image_metadata=json.dumps(image_metadata, indent=2),
                context=context,
                options=options_text,
            )
        elif self.config.panel_type == "taxonomy_reconciliation":
            prompt = template.format(
                role=role.value,
                role_description=role_description,
                item_id=item_id,
                entry1=item.get("entry1", ""),
                entry2=item.get("entry2", ""),
                context=context,
                options=options_text,
            )
        elif self.config.panel_type == "annotation_qa":
            prompt = template.format(
                role=role.value,
                role_description=role_description,
                item_id=item_id,
                annotation=item.get("annotation", ""),
                source_text=item.get("source_text", ""),
                context=context,
                options=options_text,
            )
        else:
            prompt = template.format(
                role=role.value,
                role_description=role_description,
                item_id=item_id,
                term=term,
                context=context,
                options=options_text,
            )

        return prompt

    def _parse_vote(
        self,
        response: str,
        panelist_id: str,
        role: PanelistRole,
    ) -> Tuple[str, float, str]:
        """Parse LLM response into (decision, confidence, reasoning)."""
        try:
            # Try to extract JSON
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)
                decision = data.get("decision", "UNKNOWN")
                confidence = float(data.get("confidence", 0.5))
                reasoning = data.get("reasoning", "No reasoning provided")
                return decision, min(1.0, max(0.0, confidence)), reasoning
        except (json.JSONDecodeError, ValueError, AttributeError):
            pass

        # Fallback: extract from text
        return "UNPARSEABLE", 0.3, response[:200]

    def _parse_dispute_response(self, response: str) -> Tuple[str, float, str]:
        """Parse dispute model response."""
        try:
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)
                return (
                    data.get("decision", "UNRESOLVED"),
                    float(data.get("confidence", 0.5)),
                    data.get("reasoning", ""),
                )
        except (json.JSONDecodeError, ValueError, AttributeError):
            pass

        return "UNRESOLVED", 0.3, response[:200]

    def _compute_consensus(self, votes: List[PanelistVote]) -> Tuple[bool, str, float]:
        """
        Compute consensus using social epistemology rules (SE-2).

        Returns:
            (has_consensus, winning_decision, aggregate_confidence)

        Rules:
        - Unanimous (all agree): high confidence
        - Supermajority (≥80%): medium-high confidence
        - Majority (≥consensus_threshold): medium confidence
        - Split: no consensus, escalate
        - Confidence-weighted: weight votes by panelist confidence
        """
        # Filter votes above confidence floor
        valid_votes = [v for v in votes if v.confidence >= self.config.confidence_floor]
        if not valid_votes:
            # No valid votes; fall back to highest-confidence vote
            best = max(votes, key=lambda v: v.confidence) if votes else None
            if best:
                return False, best.decision, best.confidence
            return False, "UNRESOLVED", 0.0

        # Count decisions
        decision_counts = {}
        decision_confidence = {}
        for vote in valid_votes:
            decision_counts[vote.decision] = decision_counts.get(vote.decision, 0) + 1
            if vote.decision not in decision_confidence:
                decision_confidence[vote.decision] = []
            decision_confidence[vote.decision].append(vote.confidence)

        # Find winning decision (most votes)
        winning_decision = max(decision_counts.keys(), key=lambda d: decision_counts[d])
        vote_count = decision_counts[winning_decision]
        vote_fraction = vote_count / len(valid_votes)

        # Determine consensus type and compute aggregate confidence
        if vote_fraction == 1.0:
            # Unanimous
            confidence = sum(decision_confidence[winning_decision]) / len(valid_votes)
            has_consensus = True
        elif vote_fraction >= 0.8:
            # Supermajority
            confidence = (sum(decision_confidence[winning_decision]) / len(valid_votes)) * 0.95
            has_consensus = True
        elif vote_fraction >= self.config.consensus_threshold:
            # Majority
            confidence = (sum(decision_confidence[winning_decision]) / len(valid_votes)) * 0.8
            has_consensus = True
        else:
            # Split; no consensus
            confidence = (sum(decision_confidence[winning_decision]) / len(valid_votes)) * 0.6
            has_consensus = False

        return has_consensus, winning_decision, min(1.0, max(0.0, confidence))

    def _assign_roles(self) -> List[PanelistRole]:
        """Assign n_panelists roles, distributed across the role types."""
        roles = [PanelistRole.DOMAIN_EXPERT, PanelistRole.METHODOLOGIST,
                 PanelistRole.SKEPTIC, PanelistRole.INTEGRATOR, PanelistRole.CALIBRATOR]
        result = []
        for i in range(self.config.n_panelists):
            result.append(roles[i % len(roles)])
        return result

    def _build_dispute_prompt(self, item: Dict[str, Any], votes: List[PanelistVote]) -> str:
        """Build a dispute resolution prompt."""
        item_id = item.get("id", "unknown")
        term = item.get("term", item.get("image", item.get("text", "unknown")))
        context = item.get("context", "")

        vote_summary = "\n".join([
            f"- {v.role.value} (confidence {v.confidence:.2f}): "
            f"decided '{v.decision}' — {v.reasoning}"
            for v in votes
        ])

        prompt = f"""You are resolving a dispute on a panel that has been unable to reach consensus.

ITEM: {item_id}
CONTENT: {term}
CONTEXT: {context}

PANELIST VOTES:
{vote_summary}

INSTRUCTIONS:
Review the disagreement carefully. The panelists represent different epistemic perspectives:
- Domain Expert: subject matter depth
- Methodologist: rigor and validity
- Skeptic: critical questioning
- Integrator: coherence and synthesis
- Calibrator: precision and edge cases

Choose the decision that best reconciles these perspectives, or that is most defensible
given the evidence and reasoning provided.

Respond in JSON format:
{{
  "decision": "the_chosen_option",
  "confidence": 0.75,
  "reasoning": "Your explanation for choosing this decision over the others"
}}
"""

        return prompt

    def _compute_stats(self, decisions: List[ResolutionResult]) -> Dict[str, Any]:
        """Compute statistics about the panel's work."""
        if not decisions:
            return {
                "total_resolved": 0,
                "unanimous": 0,
                "majority": 0,
                "disputed": 0,
                "escalated": 0,
                "consensus_rate": 0.0,
                "avg_confidence": 0.0,
            }

        consensus_count = sum(
            1 for d in decisions
            if d.consensus_type in ["unanimous", "majority"]
        )
        disputed_count = sum(1 for d in decisions if d.consensus_type == "disputed")
        escalated_count = sum(1 for d in decisions if d.consensus_type == "escalated")
        unanimous_count = sum(1 for d in decisions if d.consensus_type == "unanimous")
        majority_count = sum(1 for d in decisions if d.consensus_type == "majority")

        avg_confidence = (
            sum(d.confidence for d in decisions) / len(decisions)
            if decisions else 0.0
        )

        return {
            "total_resolved": len(decisions),
            "unanimous": unanimous_count,
            "majority": majority_count,
            "disputed": disputed_count,
            "escalated": escalated_count,
            "consensus_rate": consensus_count / len(decisions) if decisions else 0.0,
            "avg_confidence": avg_confidence,
        }

    def get_panel_report(self) -> Dict[str, Any]:
        """Get a comprehensive report of panel operations."""
        stats = self._compute_stats(self.session_decisions)
        return {
            "session_stats": stats,
            "decisions_made": [d.to_dict() for d in self.session_decisions],
            "generated_at": datetime.utcnow().isoformat(),
        }
