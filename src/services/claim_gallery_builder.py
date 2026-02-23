"""
Article Eater - Claim Gallery Builder
=====================================

Sprint G1: Visual Evidence Layer (Post-Expert Panel Review 2026-01-22)

This module builds visual evidence galleries for claims, showing positive,
negative, and near-miss exemplars that help users understand what a claim
means in practice.

Core Insight (from Panel):
Many CNFA findings are *image-grounded* (fluency, refuge edges, glare,
biophilic cues). Text alone is inadequate. Users need to *see* what claims
mean and where they break.

Key Design Decisions (Panel Integration):
- Pearl: Separate construct_confidence (visual) from outcome_evidence (literature)
- Cartwright: context_shift slot shows portability across building types
- Simon: Persona configs for cognitive load management (architect/student/researcher)
- Ng: ImageFeedback for active learning, append-only JSONL
- Sutskever: likely_failure slot + moderator warnings + "literature-link-only" badges
- Norvig: SelectionLog with full audit trail

Gallery Slots:
- central_positive: Images clearly showing the feature
- central_negative: Images clearly NOT showing the feature
- near_miss: Borderline cases revealing decision boundaries
- likely_failure: Feature present but outcome may not follow (moderators active)
- context_shift: Feature in different building types (portability test)

Determinism Guarantee:
Same (claim_id, snapshot_id, config_id, random_seed) -> identical gallery

References:
- Kaplan, R. (1989). The Experience of Nature. Cambridge University Press.
- Appleton, J. (1975). The Experience of Landscape. Wiley.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
from datetime import datetime, timezone
from pathlib import Path
import json
import logging
import uuid
import hashlib
import random

logger = logging.getLogger(__name__)

SCHEMA_VERSION = "claim_gallery.v1"


# =============================================================================
# ENUMS AND CONSTANTS
# =============================================================================

class SlotRole(Enum):
    """Roles for images in a gallery."""
    CENTRAL_POSITIVE = "central_positive"
    CENTRAL_NEGATIVE = "central_negative"
    NEAR_MISS = "near_miss"
    LIKELY_FAILURE = "likely_failure"
    CONTEXT_SHIFT = "context_shift"
    CONFUSION_SET = "confusion_set"
    CONTROLLED_COMPARISON = "controlled_comparison"


class PersonaProfile(Enum):
    """User personas with different gallery configurations."""
    ARCHITECT = "architect"      # Fewer, clearer examples
    STUDENT = "student"          # Learning-focused, more near-misses
    RESEARCHER = "researcher"    # Full discrimination, all failure modes
    DEFAULT = "default"          # Balanced view


class ConfidenceBasis(Enum):
    """How construct confidence was determined."""
    HUMAN_LABEL = "human_label"
    MODEL_PREDICTION = "model_prediction"
    HYBRID = "hybrid"


class OutcomeStatus(Enum):
    """How outcome evidence was obtained."""
    MEASURED_ON_THIS_IMAGE = "measured_on_this_image"
    MEASURED_ON_SIMILAR_CONTEXT = "measured_on_similar_context"
    LITERATURE_LINK_ONLY = "literature_link_only"
    UNKNOWN = "unknown"


class PairType(Enum):
    """Types of image pairs for comparison."""
    CONFUSABLE_BUT_DIFFERENT = "confusable_but_different"
    CONTROLLED_DIFFERENCE = "controlled_difference"
    NEAR_BOUNDARY_FLIP = "near_boundary_flip"


# Default slot targets by persona (from spec)
PERSONA_SLOT_TARGETS: Dict[PersonaProfile, Dict[SlotRole, Dict[str, int]]] = {
    PersonaProfile.ARCHITECT: {
        SlotRole.CENTRAL_POSITIVE: {"min": 4, "target": 6, "max": 8},
        SlotRole.CENTRAL_NEGATIVE: {"min": 2, "target": 4, "max": 6},
        SlotRole.NEAR_MISS: {"min": 2, "target": 4, "max": 6},
        SlotRole.LIKELY_FAILURE: {"min": 0, "target": 2, "max": 4},
        SlotRole.CONTEXT_SHIFT: {"min": 2, "target": 4, "max": 6},
    },
    PersonaProfile.STUDENT: {
        SlotRole.CENTRAL_POSITIVE: {"min": 6, "target": 8, "max": 10},
        SlotRole.CENTRAL_NEGATIVE: {"min": 4, "target": 6, "max": 8},
        SlotRole.NEAR_MISS: {"min": 6, "target": 8, "max": 10},  # More for learning
        SlotRole.LIKELY_FAILURE: {"min": 2, "target": 4, "max": 6},
        SlotRole.CONTEXT_SHIFT: {"min": 4, "target": 6, "max": 8},
    },
    PersonaProfile.RESEARCHER: {
        SlotRole.CENTRAL_POSITIVE: {"min": 8, "target": 12, "max": 16},
        SlotRole.CENTRAL_NEGATIVE: {"min": 6, "target": 10, "max": 14},
        SlotRole.NEAR_MISS: {"min": 8, "target": 12, "max": 16},
        SlotRole.LIKELY_FAILURE: {"min": 6, "target": 10, "max": 14},  # Full failure analysis
        SlotRole.CONTEXT_SHIFT: {"min": 6, "target": 10, "max": 14},
    },
    PersonaProfile.DEFAULT: {
        SlotRole.CENTRAL_POSITIVE: {"min": 4, "target": 8, "max": 12},
        SlotRole.CENTRAL_NEGATIVE: {"min": 4, "target": 8, "max": 12},
        SlotRole.NEAR_MISS: {"min": 4, "target": 8, "max": 12},
        SlotRole.LIKELY_FAILURE: {"min": 2, "target": 4, "max": 8},
        SlotRole.CONTEXT_SHIFT: {"min": 2, "target": 4, "max": 8},
    },
}


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class ConstructConfidence:
    """Confidence that an image exhibits the construct."""
    score: float  # 0.0 to 1.0
    basis: ConfidenceBasis
    explanatory_cues: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "score": self.score,
            "basis": self.basis.value,
            "explanatory_cues": self.explanatory_cues
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'ConstructConfidence':
        return cls(
            score=d["score"],
            basis=ConfidenceBasis(d["basis"]),
            explanatory_cues=d.get("explanatory_cues", [])
        )


@dataclass
class MeasuredOutcome:
    """An outcome measured on or linked to an image."""
    outcome_id: str
    measure: str
    direction: str  # increase, decrease, no_effect, mixed, unknown

    def to_dict(self) -> Dict[str, Any]:
        return {
            "outcome_id": self.outcome_id,
            "measure": self.measure,
            "direction": self.direction
        }


@dataclass
class OutcomeEvidence:
    """Evidence linking an image to claim outcomes."""
    status: OutcomeStatus
    measured_outcomes: List[MeasuredOutcome] = field(default_factory=list)
    citations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "measured_outcomes": [m.to_dict() for m in self.measured_outcomes],
            "citations": self.citations
        }


@dataclass
class ImageProvenance:
    """Provenance information for an image."""
    source: str
    license: str
    attribution: str
    study_id: Optional[str] = None
    paper_doi: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "source": self.source,
            "license": self.license,
            "attribution": self.attribution
        }
        if self.study_id:
            result["study_id"] = self.study_id
        if self.paper_doi:
            result["paper_doi"] = self.paper_doi
        return result


@dataclass
class ImageTags:
    """Tags for an image."""
    feature_tags: List[str] = field(default_factory=list)
    context_tags: List[str] = field(default_factory=list)
    moderator_flags: List[str] = field(default_factory=list)
    building_type: Optional[str] = None
    culture_region: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "feature_tags": self.feature_tags,
            "context_tags": self.context_tags,
            "moderator_flags": self.moderator_flags
        }
        if self.building_type:
            result["building_type"] = self.building_type
        if self.culture_region:
            result["culture_region"] = self.culture_region
        return result


@dataclass
class ImageEntry:
    """A single image in a gallery."""
    image_id: str
    uri_or_path: str
    selection_reason: str
    construct_confidence: ConstructConfidence
    outcome_evidence: OutcomeEvidence
    tags: ImageTags
    provenance: ImageProvenance
    thumbnail_uri: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "image_id": self.image_id,
            "uri_or_path": self.uri_or_path,
            "selection_reason": self.selection_reason,
            "construct_confidence": self.construct_confidence.to_dict(),
            "outcome_evidence": self.outcome_evidence.to_dict(),
            "tags": self.tags.to_dict(),
            "provenance": self.provenance.to_dict()
        }
        if self.thumbnail_uri:
            result["thumbnail_uri"] = self.thumbnail_uri
        return result


@dataclass
class ImagePair:
    """A pair of images for comparison."""
    a: ImageEntry
    b: ImageEntry
    pair_type: PairType
    pair_explanation: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pair_type": self.pair_type.value,
            "pair_explanation": self.pair_explanation,
            "a": self.a.to_dict(),
            "b": self.b.to_dict()
        }


@dataclass
class GallerySlots:
    """The image slots in a gallery."""
    central_positive: List[ImageEntry] = field(default_factory=list)
    central_negative: List[ImageEntry] = field(default_factory=list)
    near_miss: List[ImageEntry] = field(default_factory=list)
    likely_failure: List[ImageEntry] = field(default_factory=list)
    context_shift: List[ImageEntry] = field(default_factory=list)
    confusion_set: List[ImagePair] = field(default_factory=list)
    controlled_comparison: List[ImagePair] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "central_positive": [img.to_dict() for img in self.central_positive],
            "central_negative": [img.to_dict() for img in self.central_negative],
            "near_miss": [img.to_dict() for img in self.near_miss]
        }
        if self.likely_failure:
            result["likely_failure"] = [img.to_dict() for img in self.likely_failure]
        if self.context_shift:
            result["context_shift"] = [img.to_dict() for img in self.context_shift]
        if self.confusion_set:
            result["confusion_set"] = [pair.to_dict() for pair in self.confusion_set]
        if self.controlled_comparison:
            result["controlled_comparison"] = [pair.to_dict() for pair in self.controlled_comparison]
        return result


@dataclass
class ClaimFeature:
    """The feature (design element) in a claim."""
    feature_id: str
    feature_name: str
    feature_definition: Optional[str] = None
    feature_aliases: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "feature_id": self.feature_id,
            "feature_name": self.feature_name
        }
        if self.feature_definition:
            result["feature_definition"] = self.feature_definition
        if self.feature_aliases:
            result["feature_aliases"] = self.feature_aliases
        return result


@dataclass
class ClaimOutcome:
    """The outcome (effect) in a claim."""
    outcome_id: str
    outcome_name: str
    outcome_definition: Optional[str] = None
    valence: str = "unknown"  # higher_is_better, higher_is_worse, neutral_or_contextual, unknown

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "outcome_id": self.outcome_id,
            "outcome_name": self.outcome_name,
            "valence": self.valence
        }
        if self.outcome_definition:
            result["outcome_definition"] = self.outcome_definition
        return result


@dataclass
class ClaimModerator:
    """A moderator that affects claim applicability."""
    moderator_id: str
    moderator_name: str
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "moderator_id": self.moderator_id,
            "moderator_name": self.moderator_name
        }
        if self.notes:
            result["notes"] = self.notes
        return result


@dataclass
class ClaimInfo:
    """The claim a gallery illustrates."""
    claim_id: str
    statement: str
    feature: ClaimFeature
    outcome: ClaimOutcome
    moderators_expected: List[ClaimModerator] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "claim_id": self.claim_id,
            "statement": self.statement,
            "feature": self.feature.to_dict(),
            "outcome": self.outcome.to_dict()
        }
        if self.moderators_expected:
            result["moderators_expected"] = [m.to_dict() for m in self.moderators_expected]
        return result


@dataclass
class EvidenceQuality:
    """Quality metrics for the claim's evidence base."""
    design_strength: float  # 0.0 to 1.0
    consistency: float      # 0.0 to 1.0
    portability: float      # 0.0 to 1.0
    notes: Optional[str] = None
    top_citations: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "design_strength": self.design_strength,
            "consistency": self.consistency,
            "portability": self.portability
        }
        if self.notes:
            result["notes"] = self.notes
        if self.top_citations:
            result["top_citations"] = self.top_citations
        return result


@dataclass
class GalleryScope:
    """The scope within which the claim applies."""
    population: str
    setting: str
    task_context: str
    measurement_context: str
    duration: Optional[str] = None
    exclusions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "population": self.population,
            "setting": self.setting,
            "task_context": self.task_context,
            "measurement_context": self.measurement_context
        }
        if self.duration:
            result["duration"] = self.duration
        if self.exclusions:
            result["exclusions"] = self.exclusions
        return result


@dataclass
class ProvenanceSummary:
    """Summary of provenance for the gallery."""
    image_sources: List[str]
    license_notes: str
    selection_method: str
    model_versions: List[str] = field(default_factory=list)
    config_id: Optional[str] = None
    snapshot_hash: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "image_sources": self.image_sources,
            "license_notes": self.license_notes,
            "selection_method": self.selection_method
        }
        if self.model_versions:
            result["model_versions"] = self.model_versions
        if self.config_id:
            result["config_id"] = self.config_id
        if self.snapshot_hash:
            result["snapshot_hash"] = self.snapshot_hash
        return result


@dataclass
class ClaimGallery:
    """A complete visual evidence gallery for a claim."""
    gallery_id: str
    claim: ClaimInfo
    evidence_quality: EvidenceQuality
    scope: GalleryScope
    slots: GallerySlots
    provenance_summary: ProvenanceSummary
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "gallery_id": self.gallery_id,
            "generated_at": self.generated_at.isoformat(),
            "claim": self.claim.to_dict(),
            "evidence_quality": self.evidence_quality.to_dict(),
            "scope": self.scope.to_dict(),
            "slots": self.slots.to_dict(),
            "provenance_summary": self.provenance_summary.to_dict()
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


# =============================================================================
# SELECTION LOG DATA CLASSES
# =============================================================================

@dataclass
class SelectionEntry:
    """Record of why an image was selected."""
    image_id: str
    rank: int
    feature_score: float
    reason_codes: List[str]
    reason_text: str
    diversity_cluster: Optional[str] = None
    dedupe_key: Optional[str] = None
    moderator_risk: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "image_id": self.image_id,
            "rank": self.rank,
            "feature_score": self.feature_score,
            "reason_codes": self.reason_codes,
            "reason_text": self.reason_text
        }
        if self.diversity_cluster:
            result["diversity_cluster"] = self.diversity_cluster
        if self.dedupe_key:
            result["dedupe_key"] = self.dedupe_key
        if self.moderator_risk is not None:
            result["moderator_risk"] = self.moderator_risk
        return result


@dataclass
class ExclusionEntry:
    """Record of why an image was excluded."""
    image_id: str
    excluded_because: List[str]
    feature_score: Optional[float] = None
    note: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "image_id": self.image_id,
            "excluded_because": self.excluded_because
        }
        if self.feature_score is not None:
            result["feature_score"] = self.feature_score
        if self.note:
            result["note"] = self.note
        return result


@dataclass
class SlotLog:
    """Log for a single slot's selection process."""
    tau: float  # Threshold used
    candidate_count: int
    selected: List[SelectionEntry]
    excluded_top: List[ExclusionEntry]
    band: Optional[float] = None
    diversity_outcome: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "tau": self.tau,
            "candidate_count": self.candidate_count,
            "selected": [s.to_dict() for s in self.selected],
            "excluded_top": [e.to_dict() for e in self.excluded_top]
        }
        if self.band is not None:
            result["band"] = self.band
        if self.diversity_outcome:
            result["diversity_outcome"] = self.diversity_outcome
        return result


@dataclass
class SelectionLog:
    """Complete log of gallery selection process."""
    log_id: str
    build_meta: Dict[str, Any]
    slots: Dict[str, SlotLog]
    warnings: List[Dict[str, Any]]
    stats: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": "selection_log.v1",
            "log_id": self.log_id,
            "build_meta": self.build_meta,
            "slots": {k: v.to_dict() for k, v in self.slots.items()},
            "warnings": self.warnings,
            "stats": self.stats
        }


# =============================================================================
# GALLERY BUILDER
# =============================================================================

class ClaimGalleryBuilder:
    """
    Builds visual evidence galleries for claims.

    The builder is deterministic: same inputs produce identical galleries.
    This enables reproducibility and governance auditing.
    """

    def __init__(
        self,
        persona: PersonaProfile = PersonaProfile.DEFAULT,
        feature_threshold_tau: float = 0.65,
        near_miss_band: float = 0.15,
        random_seed: int = 42
    ):
        """
        Initialize the gallery builder.

        Args:
            persona: User persona affecting slot targets
            feature_threshold_tau: Threshold for positive/negative classification
            near_miss_band: Band around tau for near-miss classification
            random_seed: Seed for deterministic selection
        """
        # Validate tau and band (ChatGPT-4 panel critique)
        if not (0 < feature_threshold_tau < 1):
            raise ValueError(f"feature_threshold_tau must be in (0, 1), got {feature_threshold_tau}")
        if not (0 < near_miss_band < feature_threshold_tau):
            raise ValueError(f"near_miss_band must be in (0, tau), got {near_miss_band}")

        self.persona = persona
        self.feature_threshold_tau = feature_threshold_tau
        self.near_miss_band = near_miss_band
        self.random_seed = random_seed
        self._rng = random.Random(random_seed)
        self._slot_targets = PERSONA_SLOT_TARGETS[persona]
        self._selection_log: Optional[SelectionLog] = None
        self._max_pool_size = 10000  # Configurable limit

    def _validate_inputs(self, image_pool: List[Dict[str, Any]]) -> None:
        """Validate inputs before building gallery.

        Per ChatGPT-4 panel: prevent degenerate cases and attacks.

        Raises:
            ValueError: If inputs are invalid
        """
        if not image_pool:
            raise ValueError("image_pool cannot be empty")

        if len(image_pool) > self._max_pool_size:
            raise ValueError(
                f"image_pool size {len(image_pool)} exceeds maximum {self._max_pool_size}"
            )

        # Check for valid feature scores
        for i, img in enumerate(image_pool):
            score = img.get("feature_score")
            if score is not None and not (0 <= score <= 1):
                raise ValueError(
                    f"Image {img.get('image_id', i)} has invalid feature_score: {score}"
                )

    def build_gallery(
        self,
        claim: ClaimInfo,
        image_pool: List[Dict[str, Any]],
        evidence_quality: EvidenceQuality,
        scope: GalleryScope,
        config_id: Optional[str] = None,
        snapshot_id: Optional[str] = None
    ) -> ClaimGallery:
        """
        Build a visual evidence gallery for a claim.

        Args:
            claim: The claim to illustrate
            image_pool: Pool of candidate images with feature scores and metadata
            evidence_quality: Quality metrics for the claim's evidence
            scope: The scope within which the claim applies
            config_id: ID of the selection configuration
            snapshot_id: ID of the image pool snapshot

        Returns:
            A ClaimGallery with selected images

        Raises:
            ValueError: If inputs are invalid (empty pool, bad tau, etc.)
        """
        # Input validation (ChatGPT-4 panel critique)
        self._validate_inputs(image_pool)

        # Reset RNG for deterministic selection
        self._rng = random.Random(self.random_seed)

        # Generate IDs
        gallery_id = self._generate_gallery_id(claim.claim_id, config_id, snapshot_id)
        log_id = f"log_{gallery_id}"

        # Initialize selection log
        build_meta = {
            "claim_id": claim.claim_id,
            "snapshot_id": snapshot_id or "unknown",
            "snapshot_hash": self._compute_pool_hash(image_pool),
            "config_id": config_id or "default",
            "random_seed": self.random_seed,
            "built_at": datetime.now(timezone.utc).isoformat(),
            "builder_version": "1.0.0",
            "persona_profile": self.persona.value
        }

        warnings: List[Dict[str, Any]] = []
        slot_logs: Dict[str, SlotLog] = {}

        # Select images for each slot
        slots = GallerySlots()

        # Central positives: high feature score (above tau)
        slots.central_positive, slot_logs["central_positive"] = self._select_for_slot(
            SlotRole.CENTRAL_POSITIVE,
            image_pool,
            lambda img: img.get("feature_score", 0) >= self.feature_threshold_tau,
            sort_key=lambda img: -img.get("feature_score", 0),
            reason_prefix="High feature score"
        )

        # Central negatives: low feature score (below tau - band)
        slots.central_negative, slot_logs["central_negative"] = self._select_for_slot(
            SlotRole.CENTRAL_NEGATIVE,
            image_pool,
            lambda img: img.get("feature_score", 0) <= self.feature_threshold_tau - self.near_miss_band,
            sort_key=lambda img: img.get("feature_score", 0),
            reason_prefix="Low feature score"
        )

        # Near misses: within band around tau
        slots.near_miss, slot_logs["near_miss"] = self._select_for_slot(
            SlotRole.NEAR_MISS,
            image_pool,
            lambda img: abs(img.get("feature_score", 0) - self.feature_threshold_tau) <= self.near_miss_band,
            sort_key=lambda img: abs(img.get("feature_score", 0) - self.feature_threshold_tau),
            reason_prefix="Near decision boundary"
        )

        # Likely failures: high feature score but moderator flags
        slots.likely_failure, slot_logs["likely_failure"] = self._select_for_slot(
            SlotRole.LIKELY_FAILURE,
            image_pool,
            lambda img: (
                img.get("feature_score", 0) >= self.feature_threshold_tau and
                len(img.get("moderator_flags", [])) > 0
            ),
            sort_key=lambda img: -len(img.get("moderator_flags", [])),
            reason_prefix="Feature present but moderators active"
        )

        # Context shift: different building types
        slots.context_shift = self._select_context_shift(
            image_pool,
            claim.feature.feature_id
        )
        slot_logs["context_shift"] = SlotLog(
            tau=self.feature_threshold_tau,
            candidate_count=len([img for img in image_pool if img.get("building_type")]),
            selected=[SelectionEntry(
                image_id=img.image_id,
                rank=i,
                feature_score=img.construct_confidence.score,
                reason_codes=["context_shift"],
                reason_text=f"Shows feature in {img.tags.building_type or 'different'} context"
            ) for i, img in enumerate(slots.context_shift)],
            excluded_top=[]
        )

        # Check coverage and add warnings
        for slot_name, slot_images in [
            ("central_positive", slots.central_positive),
            ("central_negative", slots.central_negative),
            ("near_miss", slots.near_miss)
        ]:
            slot_role = SlotRole(slot_name)
            target = self._slot_targets.get(slot_role, {}).get("min", 4)
            if len(slot_images) < target:
                warnings.append({
                    "code": "insufficient_coverage",
                    "detail": f"Slot '{slot_name}' has {len(slot_images)} images, target minimum is {target}",
                    "slot": slot_name,
                    "severity": "warning"
                })

        # Compute stats
        stats = self._compute_stats(slots, image_pool)

        # Store selection log
        self._selection_log = SelectionLog(
            log_id=log_id,
            build_meta=build_meta,
            slots=slot_logs,
            warnings=warnings,
            stats=stats
        )

        # Build provenance summary
        sources = list(set(img.get("source", "unknown") for img in image_pool))
        provenance = ProvenanceSummary(
            image_sources=sources,
            license_notes="See individual image provenance",
            selection_method=f"claim_gallery_builder.v1 (persona={self.persona.value}, tau={self.feature_threshold_tau})",
            model_versions=["claim_gallery_builder:1.0.0"],
            config_id=config_id,
            snapshot_hash=build_meta["snapshot_hash"]
        )

        return ClaimGallery(
            gallery_id=gallery_id,
            claim=claim,
            evidence_quality=evidence_quality,
            scope=scope,
            slots=slots,
            provenance_summary=provenance
        )

    def get_selection_log(self) -> Optional[SelectionLog]:
        """Get the selection log from the last build."""
        return self._selection_log

    def _select_for_slot(
        self,
        slot_role: SlotRole,
        image_pool: List[Dict[str, Any]],
        filter_fn,
        sort_key,
        reason_prefix: str
    ) -> Tuple[List[ImageEntry], SlotLog]:
        """Select images for a slot with logging."""
        targets = self._slot_targets.get(slot_role, {"min": 4, "target": 8, "max": 12})
        target_count = targets["target"]
        max_count = targets["max"]

        # Filter candidates
        candidates = [img for img in image_pool if filter_fn(img)]

        # Sort by relevance
        candidates.sort(key=sort_key)

        # Apply diversity constraint (max 2 per project)
        selected_by_project: Dict[str, int] = {}
        selected_images: List[ImageEntry] = []
        excluded: List[ExclusionEntry] = []

        for i, img in enumerate(candidates):
            project_id = img.get("project_id", "unknown")

            if selected_by_project.get(project_id, 0) >= 2:
                excluded.append(ExclusionEntry(
                    image_id=img.get("image_id", f"img_{i}"),
                    excluded_because=["diversity_limit:max_per_project"],
                    feature_score=img.get("feature_score"),
                    note=f"Project {project_id} already has 2 images"
                ))
                continue

            if len(selected_images) >= max_count:
                excluded.append(ExclusionEntry(
                    image_id=img.get("image_id", f"img_{i}"),
                    excluded_because=["slot_full"],
                    feature_score=img.get("feature_score")
                ))
                continue

            # Convert to ImageEntry
            image_entry = self._pool_image_to_entry(
                img,
                rank=len(selected_images),
                reason=f"{reason_prefix}: score={img.get('feature_score', 0):.2f}"
            )
            selected_images.append(image_entry)
            selected_by_project[project_id] = selected_by_project.get(project_id, 0) + 1

        # Create selection entries for log
        selection_entries = [
            SelectionEntry(
                image_id=img.image_id,
                rank=i,
                feature_score=img.construct_confidence.score,
                reason_codes=[slot_role.value],
                reason_text=img.selection_reason,
                dedupe_key=img.provenance.source
            )
            for i, img in enumerate(selected_images)
        ]

        slot_log = SlotLog(
            tau=self.feature_threshold_tau,
            band=self.near_miss_band if slot_role == SlotRole.NEAR_MISS else None,
            candidate_count=len(candidates),
            selected=selection_entries,
            excluded_top=excluded[:10]  # Top 10 excluded
        )

        return selected_images, slot_log

    def _select_context_shift(
        self,
        image_pool: List[Dict[str, Any]],
        feature_id: str
    ) -> List[ImageEntry]:
        """Select images showing the feature in different building types."""
        targets = self._slot_targets.get(SlotRole.CONTEXT_SHIFT, {"target": 4})
        target_count = targets["target"]

        # Group by building type
        by_building_type: Dict[str, List[Dict[str, Any]]] = {}
        for img in image_pool:
            if img.get("feature_score", 0) >= self.feature_threshold_tau:
                bt = img.get("building_type", "unknown")
                if bt not in by_building_type:
                    by_building_type[bt] = []
                by_building_type[bt].append(img)

        # Select one from each building type
        selected: List[ImageEntry] = []
        building_types = list(by_building_type.keys())
        self._rng.shuffle(building_types)

        for bt in building_types[:target_count]:
            candidates = by_building_type[bt]
            if candidates:
                # Pick highest-scoring from this building type
                best = max(candidates, key=lambda x: x.get("feature_score", 0))
                entry = self._pool_image_to_entry(
                    best,
                    rank=len(selected),
                    reason=f"Context shift: feature in {bt} setting"
                )
                selected.append(entry)

        return selected

    def _pool_image_to_entry(
        self,
        pool_img: Dict[str, Any],
        rank: int,
        reason: str
    ) -> ImageEntry:
        """Convert a pool image dict to an ImageEntry.

        Per expert panel (Pearl, Ng): validates outcome_status against measured_outcomes.
        If status claims "measured_on_this_image" but no outcomes provided,
        downgrades to "literature_link_only" and logs warning.
        """
        # Extract measured outcomes from pool if present
        raw_outcomes = pool_img.get("measured_outcomes", [])
        measured_outcomes = [
            MeasuredOutcome(
                outcome_id=o.get("outcome_id", "unknown"),
                measure=o.get("measure", "unknown"),
                direction=o.get("direction", "unknown")
            )
            for o in raw_outcomes
            if isinstance(o, dict)
        ]

        # Validate outcome_status against measured_outcomes (Pearl critique)
        claimed_status = pool_img.get("outcome_status", "unknown")
        if claimed_status == "measured_on_this_image" and not measured_outcomes:
            # Downgrade: can't claim measured without actual measurements
            logger.warning(
                f"Image {pool_img.get('image_id', 'unknown')}: claimed 'measured_on_this_image' "
                f"but no measured_outcomes provided. Downgrading to 'literature_link_only'."
            )
            actual_status = OutcomeStatus.LITERATURE_LINK_ONLY
        else:
            actual_status = OutcomeStatus(claimed_status)

        return ImageEntry(
            image_id=pool_img.get("image_id", str(uuid.uuid4())[:8]),
            uri_or_path=pool_img.get("uri_or_path", pool_img.get("path", "")),
            selection_reason=reason,
            construct_confidence=ConstructConfidence(
                score=pool_img.get("feature_score", 0.0),
                basis=ConfidenceBasis(pool_img.get("confidence_basis", "model_prediction")),
                explanatory_cues=pool_img.get("cues", [])
            ),
            outcome_evidence=OutcomeEvidence(
                status=actual_status,
                measured_outcomes=measured_outcomes,
                citations=pool_img.get("citations", [])
            ),
            tags=ImageTags(
                feature_tags=pool_img.get("feature_tags", []),
                context_tags=pool_img.get("context_tags", []),
                moderator_flags=pool_img.get("moderator_flags", []),
                building_type=pool_img.get("building_type"),
                culture_region=pool_img.get("culture_region")
            ),
            provenance=ImageProvenance(
                source=pool_img.get("source", "unknown"),
                license=pool_img.get("license", "unknown"),
                attribution=pool_img.get("attribution", ""),
                study_id=pool_img.get("study_id"),
                paper_doi=pool_img.get("paper_doi")
            ),
            thumbnail_uri=pool_img.get("thumbnail_uri")
        )

    def _compute_pool_hash(self, image_pool: List[Dict[str, Any]]) -> str:
        """Compute a deterministic hash of the image pool."""
        # Sort by image_id for determinism
        sorted_pool = sorted(image_pool, key=lambda x: x.get("image_id", ""))
        pool_str = json.dumps(sorted_pool, sort_keys=True)
        return hashlib.sha256(pool_str.encode()).hexdigest()[:16]

    def _generate_gallery_id(
        self,
        claim_id: str,
        config_id: Optional[str],
        snapshot_id: Optional[str]
    ) -> str:
        """Generate a deterministic gallery ID."""
        components = [
            claim_id,
            config_id or "default",
            snapshot_id or "unknown",
            str(self.random_seed)
        ]
        hash_input = ":".join(components)
        return f"gal_{hashlib.sha256(hash_input.encode()).hexdigest()[:12]}"

    def _compute_stats(
        self,
        slots: GallerySlots,
        image_pool: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compute statistics for the gallery."""
        total_selected = (
            len(slots.central_positive) +
            len(slots.central_negative) +
            len(slots.near_miss) +
            len(slots.likely_failure) +
            len(slots.context_shift)
        )

        # Compute slot coverage
        slots_coverage: Dict[str, Dict[str, Any]] = {}
        for slot_role in [SlotRole.CENTRAL_POSITIVE, SlotRole.CENTRAL_NEGATIVE,
                         SlotRole.NEAR_MISS, SlotRole.LIKELY_FAILURE, SlotRole.CONTEXT_SHIFT]:
            targets = self._slot_targets.get(slot_role, {"min": 0, "target": 4})
            slot_images = getattr(slots, slot_role.value, [])
            actual = len(slot_images)
            slots_coverage[slot_role.value] = {
                "target": targets["target"],
                "actual": actual,
                "sufficient": actual >= targets.get("min", 0)
            }

        # Count unique sources
        all_images = (
            slots.central_positive + slots.central_negative +
            slots.near_miss + slots.likely_failure + slots.context_shift
        )
        unique_sources = len(set(img.provenance.source for img in all_images))
        unique_studies = len(set(
            img.provenance.study_id for img in all_images
            if img.provenance.study_id
        ))

        # Count measured outcomes
        measured = sum(
            1 for img in all_images
            if img.outcome_evidence.status == OutcomeStatus.MEASURED_ON_THIS_IMAGE
        )
        pct_measured = measured / len(all_images) if all_images else 0.0

        # Check for insufficient coverage
        insufficient = any(
            not cov["sufficient"]
            for cov in slots_coverage.values()
        )

        return {
            "total_candidates": len(image_pool),
            "total_selected": total_selected,
            "slots_coverage": slots_coverage,
            "diversity_summary": {
                "unique_sources": unique_sources,
                "unique_studies": unique_studies
            },
            "pct_measured_outcomes": pct_measured,
            "insufficient_coverage": insufficient
        }


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def build_gallery_from_claim_and_pool(
    claim_id: str,
    claim_statement: str,
    feature_id: str,
    feature_name: str,
    outcome_id: str,
    outcome_name: str,
    image_pool: List[Dict[str, Any]],
    persona: str = "default",
    tau: float = 0.65
) -> ClaimGallery:
    """
    Convenience function to build a gallery with minimal setup.

    Args:
        claim_id: ID of the claim
        claim_statement: The claim text
        feature_id: ID of the feature
        feature_name: Name of the feature
        outcome_id: ID of the outcome
        outcome_name: Name of the outcome
        image_pool: Pool of candidate images
        persona: User persona (architect, student, researcher, default)
        tau: Feature threshold

    Returns:
        A ClaimGallery
    """
    builder = ClaimGalleryBuilder(
        persona=PersonaProfile(persona),
        feature_threshold_tau=tau
    )

    claim = ClaimInfo(
        claim_id=claim_id,
        statement=claim_statement,
        feature=ClaimFeature(feature_id=feature_id, feature_name=feature_name),
        outcome=ClaimOutcome(outcome_id=outcome_id, outcome_name=outcome_name)
    )

    # Default evidence quality and scope
    evidence_quality = EvidenceQuality(
        design_strength=0.5,
        consistency=0.5,
        portability=0.5
    )

    scope = GalleryScope(
        population="General adult population",
        setting="Built environments",
        task_context="Various activities",
        measurement_context="Self-report and behavioral"
    )

    return builder.build_gallery(
        claim=claim,
        image_pool=image_pool,
        evidence_quality=evidence_quality,
        scope=scope
    )


def save_gallery(gallery: ClaimGallery, output_dir: Path) -> Path:
    """
    Save a gallery to disk.

    Args:
        gallery: The gallery to save
        output_dir: Directory to save to

    Returns:
        Path to the saved gallery file
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"{gallery.gallery_id}.json"
    with open(output_path, "w") as f:
        f.write(gallery.to_json(indent=2))

    logger.info(f"Saved gallery to {output_path}")
    return output_path


def save_selection_log(log: SelectionLog, output_dir: Path) -> Path:
    """
    Save a selection log to disk.

    Args:
        log: The selection log
        output_dir: Directory to save to

    Returns:
        Path to the saved log file
    """
    output_dir = Path(output_dir)
    logs_dir = output_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    output_path = logs_dir / f"{log.log_id}.json"
    with open(output_path, "w") as f:
        json.dump(log.to_dict(), f, indent=2)

    logger.info(f"Saved selection log to {output_path}")
    return output_path
