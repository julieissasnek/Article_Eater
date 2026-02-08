"""
Galleries API Routes
====================

API routes for ClaimGallery visual evidence system.

Sprint G1: Visual Evidence Layer (2026-01-22)

Per expert panel:
- Pearl: Separate causal tier from credence visually
- Cartwright: Show bridge warrant strength, portability via context_shift
- Simon: Role-based presets (persona configs)
- Ng: Feedback collection for ML improvement
- Norvig: Selection explanation via SelectionLog

Date: January 22, 2026
Version: V22.0.0 (Post-Quinean)
"""

from fastapi import APIRouter, HTTPException, Query, Path, Body
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path as FilePath
import json
import logging

from src.services.claim_gallery_builder import (
    ClaimGalleryBuilder,
    ClaimGallery,
    ClaimInfo,
    ClaimFeature,
    ClaimOutcome,
    ClaimModerator,
    EvidenceQuality,
    GalleryScope,
    PersonaProfile,
    SelectionLog,
    save_gallery,
    save_selection_log,
    SCHEMA_VERSION,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/galleries", tags=["galleries"])


# =============================================================================
# Data Directory
# =============================================================================

DATA_DIR = FilePath("data/galleries")
LOGS_DIR = DATA_DIR / "logs"
FEEDBACK_FILE = FilePath("data/feedback/image_feedback.jsonl")


# =============================================================================
# Request/Response Models
# =============================================================================

class ClaimFeatureRequest(BaseModel):
    """Feature (design element) specification."""
    feature_id: str = Field(..., description="Unique feature identifier")
    feature_name: str = Field(..., description="Human-readable feature name")
    feature_definition: Optional[str] = Field(None, description="Definition of the feature")
    feature_aliases: List[str] = Field(default_factory=list, description="Alternative names")


class ClaimOutcomeRequest(BaseModel):
    """Outcome (effect) specification."""
    outcome_id: str = Field(..., description="Unique outcome identifier")
    outcome_name: str = Field(..., description="Human-readable outcome name")
    outcome_definition: Optional[str] = Field(None, description="Definition of the outcome")
    valence: str = Field(
        "unknown",
        description="Outcome valence: higher_is_better, higher_is_worse, neutral_or_contextual, unknown"
    )


class ClaimRequest(BaseModel):
    """Claim specification for gallery building."""
    claim_id: str = Field(..., description="Unique claim identifier")
    statement: str = Field(..., min_length=10, description="The claim statement")
    feature: ClaimFeatureRequest
    outcome: ClaimOutcomeRequest
    moderators_expected: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Expected moderators that affect the claim"
    )


class EvidenceQualityRequest(BaseModel):
    """Evidence quality metrics."""
    design_strength: float = Field(..., ge=0, le=1, description="Study design strength (0-1)")
    consistency: float = Field(..., ge=0, le=1, description="Cross-study consistency (0-1)")
    portability: float = Field(..., ge=0, le=1, description="Generalizability across contexts (0-1)")
    notes: Optional[str] = Field(None, description="Additional quality notes")
    top_citations: List[Dict[str, Any]] = Field(default_factory=list, description="Key citations")


class ScopeRequest(BaseModel):
    """Scope within which the claim applies."""
    population: str = Field(..., description="Target population")
    setting: str = Field(..., description="Physical setting")
    task_context: str = Field(..., description="Task/activity context")
    measurement_context: str = Field(..., description="How outcomes are measured")
    duration: Optional[str] = Field(None, description="Time frame")
    exclusions: List[str] = Field(default_factory=list, description="Scope exclusions")


class ImagePoolItem(BaseModel):
    """A candidate image in the pool."""
    image_id: str
    uri_or_path: str
    feature_score: float = Field(..., ge=0, le=1, description="Feature presence score")
    confidence_basis: str = Field("model_prediction", description="How score was determined")
    outcome_status: str = Field("unknown", description="Outcome evidence status")
    building_type: Optional[str] = None
    culture_region: Optional[str] = None
    project_id: Optional[str] = None
    source: str = "unknown"
    license: str = "unknown"
    attribution: str = ""
    cues: List[str] = Field(default_factory=list)
    feature_tags: List[str] = Field(default_factory=list)
    context_tags: List[str] = Field(default_factory=list)
    moderator_flags: List[str] = Field(default_factory=list)
    study_id: Optional[str] = None
    paper_doi: Optional[str] = None
    thumbnail_uri: Optional[str] = None


class BuildGalleryRequest(BaseModel):
    """Request to build a gallery."""
    claim: ClaimRequest
    image_pool: List[ImagePoolItem] = Field(..., min_length=1, description="Candidate images")
    evidence_quality: EvidenceQualityRequest
    scope: ScopeRequest
    persona: str = Field("default", description="User persona: architect, student, researcher, default")
    feature_threshold_tau: float = Field(0.65, ge=0, le=1, description="Feature threshold")
    near_miss_band: float = Field(0.15, ge=0, le=0.5, description="Near-miss band width")
    random_seed: int = Field(42, description="Random seed for deterministic selection")
    config_id: Optional[str] = Field(None, description="Configuration identifier")
    snapshot_id: Optional[str] = Field(None, description="Image pool snapshot identifier")


class GalleryResponse(BaseModel):
    """Response containing a gallery."""
    gallery_id: str
    schema_version: str
    claim_id: str
    claim_statement: str
    generated_at: str
    evidence_quality: Dict[str, Any]
    slot_counts: Dict[str, int]
    total_images: int
    warnings: List[Dict[str, Any]] = Field(default_factory=list)
    gallery_url: str


class SelectionLogResponse(BaseModel):
    """Response containing a selection log."""
    log_id: str
    gallery_id: str
    build_meta: Dict[str, Any]
    stats: Dict[str, Any]
    warnings: List[Dict[str, Any]]


class ImageFeedbackRequest(BaseModel):
    """Request to submit image feedback.

    Per Ng panel critique: web_snapshot_id is critical for tracing feedback
    to the epistemic state that generated the gallery.
    """
    gallery_id: str = Field(..., description="Gallery containing the image")
    claim_id: str = Field(..., description="Claim the gallery illustrates")
    image_id: str = Field(..., description="Image being annotated")
    slot_role: str = Field(..., description="Original slot assignment")
    # Panel fix (Ng): Add web_snapshot_id for epistemic traceability
    web_snapshot_id: Optional[str] = Field(
        None,
        description="Web of belief snapshot ID - critical for tracing feedback to epistemic context"
    )
    event_type: str = Field(
        ...,
        description="Type: construct_label, slot_reassignment, moderator_annotation, rationale_correction, provenance_issue, duplicate_or_redundant"
    )
    before_state: Dict[str, Any] = Field(default_factory=dict, description="State before correction")
    after_state: Dict[str, Any] = Field(..., description="Corrected state")
    confidence: float = Field(..., ge=0, le=1, description="Confidence in correction")
    reason_text: str = Field(..., min_length=3, description="Explanation")
    cue_terms: List[str] = Field(default_factory=list, description="Key terms")
    actor_id: Optional[str] = Field(None, description="Who submitted feedback")
    actor_role: str = Field("unknown", description="Role: student, architect, researcher, etc.")


class FeedbackResponse(BaseModel):
    """Response after submitting feedback."""
    feedback_id: str
    status: str
    message: str


# =============================================================================
# Routes
# =============================================================================

@router.post("/build", response_model=GalleryResponse)
async def build_gallery(request: BuildGalleryRequest):
    """
    Build a visual evidence gallery for a claim.

    The gallery is deterministic: same inputs produce identical outputs.
    This enables reproducibility and governance auditing.
    """
    try:
        # Convert request to domain objects
        claim = ClaimInfo(
            claim_id=request.claim.claim_id,
            statement=request.claim.statement,
            feature=ClaimFeature(
                feature_id=request.claim.feature.feature_id,
                feature_name=request.claim.feature.feature_name,
                feature_definition=request.claim.feature.feature_definition,
                feature_aliases=request.claim.feature.feature_aliases
            ),
            outcome=ClaimOutcome(
                outcome_id=request.claim.outcome.outcome_id,
                outcome_name=request.claim.outcome.outcome_name,
                outcome_definition=request.claim.outcome.outcome_definition,
                valence=request.claim.outcome.valence
            ),
            moderators_expected=[
                ClaimModerator(
                    moderator_id=m.get("moderator_id", "unknown"),
                    moderator_name=m.get("moderator_name", "Unknown"),
                    notes=m.get("notes")
                )
                for m in request.claim.moderators_expected
            ]
        )

        evidence_quality = EvidenceQuality(
            design_strength=request.evidence_quality.design_strength,
            consistency=request.evidence_quality.consistency,
            portability=request.evidence_quality.portability,
            notes=request.evidence_quality.notes,
            top_citations=request.evidence_quality.top_citations
        )

        scope = GalleryScope(
            population=request.scope.population,
            setting=request.scope.setting,
            task_context=request.scope.task_context,
            measurement_context=request.scope.measurement_context,
            duration=request.scope.duration,
            exclusions=request.scope.exclusions
        )

        # Convert image pool to dicts
        image_pool = [img.model_dump() for img in request.image_pool]

        # Build gallery
        builder = ClaimGalleryBuilder(
            persona=PersonaProfile(request.persona),
            feature_threshold_tau=request.feature_threshold_tau,
            near_miss_band=request.near_miss_band,
            random_seed=request.random_seed
        )

        gallery = builder.build_gallery(
            claim=claim,
            image_pool=image_pool,
            evidence_quality=evidence_quality,
            scope=scope,
            config_id=request.config_id,
            snapshot_id=request.snapshot_id
        )

        # Save gallery
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        gallery_path = save_gallery(gallery, DATA_DIR)

        # Save selection log
        selection_log = builder.get_selection_log()
        if selection_log:
            LOGS_DIR.mkdir(parents=True, exist_ok=True)
            save_selection_log(selection_log, DATA_DIR)

        # Build response
        slots = gallery.slots
        slot_counts = {
            "central_positive": len(slots.central_positive),
            "central_negative": len(slots.central_negative),
            "near_miss": len(slots.near_miss),
            "likely_failure": len(slots.likely_failure),
            "context_shift": len(slots.context_shift),
            "confusion_set": len(slots.confusion_set),
            "controlled_comparison": len(slots.controlled_comparison)
        }

        total_images = sum(slot_counts.values())

        return GalleryResponse(
            gallery_id=gallery.gallery_id,
            schema_version=SCHEMA_VERSION,
            claim_id=gallery.claim.claim_id,
            claim_statement=gallery.claim.statement,
            generated_at=gallery.generated_at.isoformat(),
            evidence_quality={
                "design_strength": gallery.evidence_quality.design_strength,
                "consistency": gallery.evidence_quality.consistency,
                "portability": gallery.evidence_quality.portability
            },
            slot_counts=slot_counts,
            total_images=total_images,
            warnings=selection_log.warnings if selection_log else [],
            gallery_url=f"/api/v1/galleries/{gallery.gallery_id}"
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Error building gallery")
        raise HTTPException(status_code=500, detail=f"Failed to build gallery: {str(e)}")


@router.get("/{gallery_id}")
async def get_gallery(
    gallery_id: str = Path(..., description="Gallery ID to retrieve")
):
    """
    Retrieve a previously built gallery.
    """
    gallery_path = DATA_DIR / f"{gallery_id}.json"

    if not gallery_path.exists():
        raise HTTPException(status_code=404, detail=f"Gallery {gallery_id} not found")

    try:
        with open(gallery_path) as f:
            return json.load(f)
    except Exception as e:
        logger.exception(f"Error reading gallery {gallery_id}")
        raise HTTPException(status_code=500, detail=f"Failed to read gallery: {str(e)}")


@router.get("/{gallery_id}/log", response_model=SelectionLogResponse)
async def get_selection_log(
    gallery_id: str = Path(..., description="Gallery ID")
):
    """
    Get the selection log for a gallery, explaining why each image was selected or excluded.
    """
    log_path = LOGS_DIR / f"log_{gallery_id}.json"

    if not log_path.exists():
        raise HTTPException(status_code=404, detail=f"Selection log for {gallery_id} not found")

    try:
        with open(log_path) as f:
            log_data = json.load(f)

        return SelectionLogResponse(
            log_id=log_data["log_id"],
            gallery_id=gallery_id,
            build_meta=log_data["build_meta"],
            stats=log_data["stats"],
            warnings=log_data["warnings"]
        )
    except Exception as e:
        logger.exception(f"Error reading selection log for {gallery_id}")
        raise HTTPException(status_code=500, detail=f"Failed to read selection log: {str(e)}")


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(request: ImageFeedbackRequest):
    """
    Submit feedback for an image in a gallery.

    Feedback is used for active learning to improve classification.
    Stored in append-only JSONL format per governance requirements.
    """
    import uuid

    feedback_id = f"fb_{uuid.uuid4().hex[:12]}"

    # Warn if web_snapshot_id is missing (Ng panel critique)
    if not request.web_snapshot_id:
        logger.warning(
            f"Feedback {feedback_id} missing web_snapshot_id - "
            "cannot trace to epistemic context"
        )

    feedback_record = {
        "schema_version": "image_feedback.v1",
        "feedback_id": feedback_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "actor": {
            "actor_id": request.actor_id or "anonymous",
            "role": request.actor_role
        },
        "target": {
            "gallery_id": request.gallery_id,
            "claim_id": request.claim_id,
            "image_id": request.image_id,
            "slot_role": request.slot_role,
            "web_snapshot_id": request.web_snapshot_id  # Panel fix (Ng)
        },
        "event_type": request.event_type,
        "before": request.before_state,
        "after": request.after_state,
        "confidence": request.confidence,
        "reason": {
            "free_text": request.reason_text,
            "cue_terms": request.cue_terms
        }
    }

    try:
        # Ensure directory exists
        FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)

        # Append to JSONL (append-only per governance)
        with open(FEEDBACK_FILE, "a") as f:
            f.write(json.dumps(feedback_record) + "\n")

        logger.info(f"Recorded feedback {feedback_id} for image {request.image_id}")

        return FeedbackResponse(
            feedback_id=feedback_id,
            status="recorded",
            message="Feedback recorded successfully. Thank you for improving the system."
        )

    except Exception as e:
        logger.exception("Error recording feedback")
        raise HTTPException(status_code=500, detail=f"Failed to record feedback: {str(e)}")


@router.get("/")
async def list_galleries(
    limit: int = Query(20, ge=1, le=100, description="Maximum galleries to return"),
    claim_id: Optional[str] = Query(None, description="Filter by claim ID")
):
    """
    List available galleries.
    """
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)

        galleries = []
        for gallery_file in DATA_DIR.glob("gal_*.json"):
            try:
                with open(gallery_file) as f:
                    data = json.load(f)

                if claim_id and data.get("claim", {}).get("claim_id") != claim_id:
                    continue

                galleries.append({
                    "gallery_id": data.get("gallery_id"),
                    "claim_id": data.get("claim", {}).get("claim_id"),
                    "claim_statement": data.get("claim", {}).get("statement", "")[:100],
                    "generated_at": data.get("generated_at"),
                    "url": f"/api/v1/galleries/{data.get('gallery_id')}"
                })

            except Exception as e:
                logger.warning(f"Could not read gallery file {gallery_file}: {e}")
                continue

        # Sort by generation time (newest first)
        galleries.sort(key=lambda g: g.get("generated_at", ""), reverse=True)

        return {
            "galleries": galleries[:limit],
            "total": len(galleries),
            "limit": limit
        }

    except Exception as e:
        logger.exception("Error listing galleries")
        raise HTTPException(status_code=500, detail=f"Failed to list galleries: {str(e)}")
