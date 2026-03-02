"""
Theory Agent Service — Theory Profile Loading and Panel Simulation

Loads all 10 T1 framework profiles. Provides methods for:
- Profile retrieval by framework ID
- Panel persona simulation (how would framework X evaluate finding Y?)
- Competing prediction identification
- Framework relevance to template
- Structured panel discussion generation

Usage:
    service = TheoryAgentService()
    profile = service.get_profile("predictive-processing")
    persona = service.get_panel_persona("predictive-processing")
    panel_discussion = service.simulate_panel_discussion(finding_dict, ["predictive-processing", "neuromodulatory-systems"])
"""

import json
import logging
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent


# =============================================================================
# Data Classes for Return Values
# =============================================================================

@dataclass
class PanelPersona:
    """Panel persona for a theory framework."""
    framework_id: str
    voice: str
    typical_critiques: List[str]
    blind_spots: List[str]
    complementary_frameworks: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class EnvironmentalPrediction:
    """A prediction from a theory about environmental effects."""
    prediction_id: str
    statement: str
    mechanism: str
    testable: bool
    relevant_templates: List[str]
    competing_predictions: Optional[List[Dict[str, str]]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class TheoryProfile:
    """Complete profile for a T1 framework."""
    framework_id: str
    full_name: str
    core_claim: str
    key_theorists: List[str]
    seminal_works: List[Dict[str, Any]]
    core_constructs: List[str]
    epistemic_commitments: Dict[str, Any]
    environmental_predictions: List[Dict[str, Any]]
    characteristic_questions: List[str]
    panel_persona: Dict[str, Any]
    molecule_affinities: List[str]
    meta: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class FindingEvaluation:
    """How a framework evaluates a finding."""
    framework_id: str
    framework_name: str
    evaluation_summary: str
    warrant_types: List[str]
    mechanism_explanation: Optional[str]
    confidence: float
    critiques: List[str]
    next_questions: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class PanelDiscussion:
    """Structured discussion from multiple frameworks."""
    finding_id: str
    finding_description: str
    frameworks_represented: List[str]
    individual_evaluations: List[FindingEvaluation] = field(default_factory=list)
    convergence_summary: str = ""
    tensions_identified: List[str] = field(default_factory=list)
    next_experiments_proposed: List[str] = field(default_factory=list)
    generated_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = asdict(self)
        result["individual_evaluations"] = [
            e.to_dict() if isinstance(e, FindingEvaluation) else e
            for e in self.individual_evaluations
        ]
        return result


# =============================================================================
# Theory Agent Service
# =============================================================================

class TheoryAgentService:
    """Load and serve theory agent profiles."""

    def __init__(self, profiles_dir: str = "data/theory_profiles"):
        """Initialize service and load all profiles."""
        self.profiles_dir = Path(profiles_dir) if not Path(profiles_dir).is_absolute() else Path(profiles_dir)
        if not self.profiles_dir.is_absolute():
            self.profiles_dir = PROJECT_ROOT / self.profiles_dir

        self._profiles: Dict[str, Dict[str, Any]] = {}
        self._framework_ids: List[str] = []

        self._load_profiles()

    def _load_profiles(self) -> None:
        """Load all theory profile JSON files."""
        if not self.profiles_dir.exists():
            logger.warning(f"Profiles directory not found: {self.profiles_dir}")
            return

        # Expected framework IDs (hyphenated)
        expected_frameworks = [
            "predictive-processing",
            "spatial-navigation",
            "dual-process-evaluation",
            "default-mode-dynamics",
            "neuromodulatory-systems",
            "interoceptive-construction",
            "multisensory-integration",
            "ecological-dynamics",
            "circadian-biology",
            "motor-simulation-embodiment"
        ]

        for fw_id in expected_frameworks:
            filepath = self.profiles_dir / f"{fw_id}.json"
            if filepath.exists():
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        profile = json.load(f)
                    self._profiles[fw_id] = profile
                    self._framework_ids.append(fw_id)
                    logger.info(f"Loaded profile: {fw_id}")
                except Exception as e:
                    logger.error(f"Failed to load profile {fw_id}: {e}")
            else:
                logger.warning(f"Profile file not found: {filepath}")

        logger.info(f"Loaded {len(self._profiles)} theory profiles")

    def get_profile(self, framework_id: str) -> Optional[TheoryProfile]:
        """
        Get complete profile for a framework.

        Args:
            framework_id: Hyphenated framework ID (e.g., "predictive-processing")

        Returns:
            TheoryProfile if found, None otherwise
        """
        if framework_id not in self._profiles:
            logger.warning(f"Profile not found: {framework_id}")
            return None

        profile_dict = self._profiles[framework_id]
        return TheoryProfile(**profile_dict)

    def get_panel_persona(self, framework_id: str) -> Optional[PanelPersona]:
        """
        Get panel simulation persona for a framework.

        Args:
            framework_id: Framework ID

        Returns:
            PanelPersona if found, None otherwise
        """
        if framework_id not in self._profiles:
            return None

        profile = self._profiles[framework_id]
        persona_dict = profile.get("panel_persona", {})

        return PanelPersona(
            framework_id=framework_id,
            voice=persona_dict.get("voice", ""),
            typical_critiques=persona_dict.get("typical_critiques", []),
            blind_spots=persona_dict.get("blind_spots", []),
            complementary_frameworks=persona_dict.get("complementary_frameworks", [])
        )

    def evaluate_finding(self, framework_id: str, finding: Dict[str, Any]) -> Optional[FindingEvaluation]:
        """
        How would a framework evaluate a finding?

        Args:
            framework_id: Framework to evaluate from
            finding: Dictionary with at least 'id', 'description', and ideally 'mechanism_explanation'

        Returns:
            FindingEvaluation if framework found, None otherwise
        """
        profile = self.get_profile(framework_id)
        if not profile:
            return None

        # Determine warrant types the framework would prefer
        warrant_types = profile.epistemic_commitments.get("preferred_warrant_types", [])

        # Try to match finding to framework's predictions
        mechanism_explanation = finding.get("mechanism_explanation")
        confidence = self._estimate_confidence(framework_id, finding)

        # Generate critiques from persona
        persona = self.get_panel_persona(framework_id)
        critiques = persona.typical_critiques if persona else []

        # Generate next questions
        next_questions = profile.characteristic_questions[:3] if profile else []

        return FindingEvaluation(
            framework_id=framework_id,
            framework_name=profile.full_name if profile else framework_id,
            evaluation_summary=f"Evaluation from {profile.full_name if profile else framework_id} perspective",
            warrant_types=warrant_types,
            mechanism_explanation=mechanism_explanation,
            confidence=confidence,
            critiques=critiques,
            next_questions=next_questions
        )

    def get_competing_predictions(self, prediction_id: str) -> List[Dict[str, str]]:
        """
        Find predictions that compete with a given prediction.

        Args:
            prediction_id: ID of a prediction (e.g., "pp-pred-001")

        Returns:
            List of competing predictions from other frameworks
        """
        competing = []

        for fw_id, profile_dict in self._profiles.items():
            predictions = profile_dict.get("environmental_predictions", [])
            for pred in predictions:
                if pred.get("prediction_id") == prediction_id:
                    competitors = pred.get("competing_predictions")
                    if competitors:
                        competing.extend(competitors)

        return competing

    def get_relevant_frameworks(self, template_id: str) -> List[str]:
        """
        Which frameworks care about this template?

        Args:
            template_id: Template ID (e.g., "PP_VISUAL_STATISTICS_001")

        Returns:
            List of framework IDs with relevant predictions
        """
        relevant = []

        for fw_id, profile_dict in self._profiles.items():
            predictions = profile_dict.get("environmental_predictions", [])
            for pred in predictions:
                if template_id in pred.get("relevant_templates", []):
                    relevant.append(fw_id)
                    break

        return list(set(relevant))

    def simulate_panel_discussion(
        self,
        finding: Dict[str, Any],
        framework_ids: Optional[List[str]] = None
    ) -> Optional[PanelDiscussion]:
        """
        Generate structured perspective from multiple frameworks.

        Args:
            finding: Dictionary with 'id', 'description', and optionally other fields
            framework_ids: List of frameworks to include; if None, use all

        Returns:
            PanelDiscussion with individual evaluations and synthesis
        """
        if framework_ids is None:
            framework_ids = self._framework_ids

        finding_id = finding.get("id", "unknown")
        finding_desc = finding.get("description", "")

        discussion = PanelDiscussion(
            finding_id=finding_id,
            finding_description=finding_desc,
            frameworks_represented=framework_ids,
            generated_at=datetime.utcnow().isoformat()
        )

        # Get individual evaluations
        for fw_id in framework_ids:
            evaluation = self.evaluate_finding(fw_id, finding)
            if evaluation:
                discussion.individual_evaluations.append(evaluation)

        # Synthesize convergence and tensions
        discussion = self._synthesize_panel_discussion(discussion)

        return discussion

    def _synthesize_panel_discussion(self, discussion: PanelDiscussion) -> PanelDiscussion:
        """Add synthesis layer to panel discussion."""
        if not discussion.individual_evaluations:
            return discussion

        # Check for convergence
        mechanisms_proposed = [
            e.mechanism_explanation for e in discussion.individual_evaluations
            if e.mechanism_explanation
        ]

        if mechanisms_proposed:
            # Simple convergence detection: count how many frameworks propose compatible mechanisms
            discussion.convergence_summary = (
                f"{len(mechanisms_proposed)}/{len(discussion.individual_evaluations)} frameworks "
                f"propose mechanistic explanations. This suggests moderate convergence."
            )

        # Identify tensions (frameworks with conflicting predictions)
        frameworks_set = {e.framework_id for e in discussion.individual_evaluations}
        for fw_id in frameworks_set:
            profile = self.get_profile(fw_id)
            if profile:
                persona = self.get_panel_persona(fw_id)
                if persona and persona.complementary_frameworks:
                    for complement_fw in persona.complementary_frameworks:
                        if complement_fw in frameworks_set:
                            discussion.tensions_identified.append(
                                f"Potential integration opportunity: {fw_id} and {complement_fw} may be complementary"
                            )

        # Propose next experiments
        all_questions = []
        for fw_id in discussion.frameworks_represented:
            profile = self.get_profile(fw_id)
            if profile:
                all_questions.extend(profile.characteristic_questions[:2])

        discussion.next_experiments_proposed = all_questions[:5]

        return discussion

    def _estimate_confidence(self, framework_id: str, finding: Dict[str, Any]) -> float:
        """
        Estimate framework confidence in a finding.

        Heuristic: confidence is 0.5 baseline, raised by mechanism match, lowered by scope mismatch.
        """
        profile = self.get_profile(framework_id)
        if not profile:
            return 0.5

        confidence = 0.5

        # Boost for mechanism explanation
        if finding.get("mechanism_explanation"):
            confidence += 0.1

        # Check against framework's characteristic questions
        finding_text = finding.get("description", "").lower()
        matching_questions = sum(
            1 for q in profile.characteristic_questions
            if any(word in finding_text for word in q.lower().split()[:3])
        )
        confidence += 0.1 * min(matching_questions / 3, 0.1)

        # Normalize
        confidence = min(confidence, 0.95)
        confidence = max(confidence, 0.3)

        return round(confidence, 2)

    def list_frameworks(self) -> List[str]:
        """List all loaded framework IDs."""
        return sorted(self._framework_ids)

    def list_profiles_summary(self) -> List[Dict[str, Any]]:
        """Get summary of all profiles."""
        summaries = []
        for fw_id in self._framework_ids:
            profile = self.get_profile(fw_id)
            if profile:
                summaries.append({
                    "framework_id": profile.framework_id,
                    "full_name": profile.full_name,
                    "core_claim": profile.core_claim,
                    "key_theorists": profile.key_theorists,
                    "prediction_count": len(profile.environmental_predictions)
                })
        return summaries

    def get_prediction_by_id(self, prediction_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific prediction by ID."""
        for fw_id, profile_dict in self._profiles.items():
            predictions = profile_dict.get("environmental_predictions", [])
            for pred in predictions:
                if pred.get("prediction_id") == prediction_id:
                    return pred
        return None

    def search_profiles_by_construct(self, construct_name: str) -> List[Tuple[str, List[str]]]:
        """
        Search frameworks by construct name.

        Args:
            construct_name: Construct to search for (case-insensitive substring match)

        Returns:
            List of (framework_id, matching_constructs) tuples
        """
        results = []
        construct_lower = construct_name.lower()

        for fw_id in self._framework_ids:
            profile = self.get_profile(fw_id)
            if profile:
                matching = [
                    c for c in profile.core_constructs
                    if construct_lower in c.lower()
                ]
                if matching:
                    results.append((fw_id, matching))

        return results

    def get_framework_by_name(self, name: str) -> Optional[str]:
        """
        Get framework ID by full name (fuzzy match).

        Args:
            name: Full name or partial name of framework

        Returns:
            Framework ID if found, None otherwise
        """
        name_lower = name.lower()

        for fw_id in self._framework_ids:
            profile = self.get_profile(fw_id)
            if profile:
                if name_lower in profile.full_name.lower():
                    return fw_id

        return None
