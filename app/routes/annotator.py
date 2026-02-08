"""
Article Annotator API Routes
============================

API routes for the Article Annotation GUI.

Supports:
- Loading articles from Article Finder PDF collection
- Loading articles from ae.db
- Saving annotations to database
- Managing theory registry

Date: January 23, 2026
Version: V22.0.0 (Post-Quinean)
"""

from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import hashlib
from datetime import datetime
from pathlib import Path
import json
import logging
import sqlite3
import os

logger = logging.getLogger(__name__)

router = APIRouter(tags=["annotator"])  # Prefix is added when mounted in main.py

# Paths
AF_DATA_PATH = Path("/Users/davidusa/REPOS/Article_Finder_v3_2_3/data")
AE_DB_PATH = Path("/Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/ae.db")
ANNOTATIONS_DIR = Path("/Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/data/annotations")


# =============================================================================
# Request/Response Models
# =============================================================================

class ArticleSummary(BaseModel):
    """Summary of an article for the list view."""
    id: str
    title: str
    year: Optional[int] = None
    authors: Optional[str] = None
    annotated: bool = False
    quality: Optional[str] = None
    pdf_path: Optional[str] = None


class ArticleAnnotation(BaseModel):
    """Full article annotation."""
    article_id: str
    title: str
    doi: Optional[str] = None
    authors: Optional[str] = None
    year: Optional[int] = None
    pdf_path: Optional[str] = None

    # Quality and type
    quality_tier: str = Field(..., description="gold, high, moderate, low, training")
    study_type: str = Field(..., description="meta-analysis, rct, etc.")

    # Theories
    theories: List[str] = Field(default_factory=list)
    primary_theory: Optional[str] = None

    # Typology
    typology_scope: str = Field("general", description="general, specific, comparative")
    typologies: List[str] = Field(default_factory=list)

    # Scope
    population: Optional[str] = None
    setting: Optional[str] = None
    sample_size: Optional[int] = None
    geography: Optional[str] = None

    # Assessment
    methodology_score: float = Field(0.5, ge=0, le=1)
    annotation_confidence: float = Field(0.75, ge=0, le=1)

    # Notes
    key_findings: Optional[str] = None
    concerns: Optional[str] = None
    additional_notes: Optional[str] = None

    # Metadata
    annotated_at: Optional[str] = None
    annotated_by: str = "human"


class TheoryInfo(BaseModel):
    """Theory information."""
    theory_id: str
    name: str
    author: Optional[str] = None
    year: Optional[int] = None
    mechanism: Optional[str] = None  # The explanatory mechanism
    key_elements: List[str] = Field(default_factory=list)
    observed_effects: List[str] = Field(default_factory=list)
    key_references: List[str] = Field(default_factory=list)


# =============================================================================
# Theory Registry (from CNfA document)
# =============================================================================

CNFA_THEORIES: Dict[str, TheoryInfo] = {
    "affordance": TheoryInfo(
        theory_id="affordance",
        name="Affordance Theory",
        author="Gibson",
        year=1979,
        mechanism="Perception is shaped by what the environment affords the organism—i.e., the possibilities for action it enables.",
        key_elements=["Stairs", "doors", "benches", "ledges", "handles", "ramps"],
        observed_effects=["Perception of action possibilities"],
        key_references=["Gibson, J. J. (1979). The ecological approach to visual perception."]
    ),
    "enactivism": TheoryInfo(
        theory_id="enactivism",
        name="Enactivism",
        author="Noë",
        year=2004,
        mechanism="Perception emerges from sensorimotor engagement with the world, not from passive representation.",
        key_elements=["Handrails", "walkable paths", "manipulables", "haptic surfaces"],
        observed_effects=["Perception-action coupling", "embodied sense of space"],
        key_references=["Noë, A. (2004). Action in perception. MIT Press."]
    ),
    "env_load": TheoryInfo(
        theory_id="env_load",
        name="Environmental Load Theory",
        author="Milgram",
        year=1970,
        mechanism="Excessive sensory input or complexity overwhelms cognitive processing, leading to stress or withdrawal.",
        key_elements=["Crowding", "cluttered space", "low ceilings", "noise levels"],
        observed_effects=["Overstimulation", "fatigue", "withdrawal"],
        key_references=["Milgram, S. (1970). The experience of living in cities. Science."]
    ),
    "prospect_refuge": TheoryInfo(
        theory_id="prospect_refuge",
        name="Prospect-Refuge Theory",
        author="Appleton",
        year=1975,
        mechanism="People prefer environments where they can see without being seen (prospect + refuge).",
        key_elements=["Alcoves", "overhangs", "windows with views", "bay windows", "balconies"],
        observed_effects=["Comfort", "preference", "vigilance", "safety"],
        key_references=["Appleton, J. (1975). The experience of landscape. Wiley."]
    ),
    "biophilia": TheoryInfo(
        theory_id="biophilia",
        name="Biophilia Hypothesis",
        author="Kellert & Wilson",
        year=1993,
        mechanism="Humans have an evolved affinity for life and life-like forms.",
        key_elements=["Plants", "wood", "views of nature", "living walls", "water features"],
        observed_effects=["Stress reduction", "well-being"],
        key_references=["Kellert, S. R., & Wilson, E. O. (Eds.). (1993). The biophilia hypothesis."]
    ),
    "srt": TheoryInfo(
        theory_id="srt",
        name="Stress Recovery Theory",
        author="Ulrich",
        year=1984,
        mechanism="Natural environments enable faster recovery from stress than urban or artificial settings.",
        key_elements=["Green space", "natural forms", "garden views"],
        observed_effects=["Lowered HR", "reduced cortisol", "improved mood"],
        key_references=["Ulrich, R. S. (1984). View through a window may influence recovery from surgery. Science."]
    ),
    "art": TheoryInfo(
        theory_id="art",
        name="Attention Restoration Theory",
        author="Kaplan & Kaplan",
        year=1989,
        mechanism="Certain environments restore attention by engaging involuntary attention ('soft fascination') and allowing voluntary attention to replenish.",
        key_elements=["Fascinating natural stimuli", "quiet gardens", "water features", "complex textures"],
        observed_effects=["Improved cognitive performance", "attention restoration"],
        key_references=["Kaplan, R., & Kaplan, S. (1989). The experience of nature. Cambridge."]
    ),
    "spatial_legibility": TheoryInfo(
        theory_id="spatial_legibility",
        name="Spatial Legibility",
        author="Lynch",
        year=1960,
        mechanism="A 'legible' environment is one whose layout is easily understood and navigated.",
        key_elements=["Paths", "landmarks", "nodes", "edges", "districts"],
        observed_effects=["Ease of navigation", "comfort", "lower anxiety"],
        key_references=["Lynch, K. (1960). The image of the city. MIT Press."]
    ),
    "spatial_syntax": TheoryInfo(
        theory_id="spatial_syntax",
        name="Spatial Syntax Theory",
        author="Hillier & Hanson",
        year=1984,
        mechanism="The spatial configuration of buildings predicts movement and interaction patterns.",
        key_elements=["Visibility", "connectivity", "integration", "axial lines"],
        observed_effects=["Social interaction", "wayfinding", "movement patterns"],
        key_references=["Hillier, B., & Hanson, J. (1984). The social logic of space. Cambridge."]
    ),
    "predictive_processing": TheoryInfo(
        theory_id="predictive_processing",
        name="Predictive Processing",
        author="Clark",
        year=2013,
        mechanism="The brain constantly predicts sensory input; mismatch leads to cognitive load or interest depending on context.",
        key_elements=["Repetitive patterns", "novel patterns", "unexpected geometries"],
        observed_effects=["Ease vs. disruption of perception", "prediction error"],
        key_references=["Clark, A. (2013). Whatever next? Behavioral and Brain Sciences."]
    ),
    "embodied_sim": TheoryInfo(
        theory_id="embodied_sim",
        name="Embodied Simulation",
        author="Vartanian et al.",
        year=2013,
        mechanism="The body simulates perceived forms, particularly those resembling movement or affectively salient shapes.",
        key_elements=["Curved surfaces", "angular surfaces", "rounded ceilings", "non-orthogonal geometries"],
        observed_effects=["Motor resonance", "aesthetic experience"],
        key_references=["Vartanian, O. et al. (2013). Impact of contour on aesthetic judgments. PNAS."]
    ),
    "mirror_neuron": TheoryInfo(
        theory_id="mirror_neuron",
        name="Mirror Neuron Theory",
        author="Rizzolatti",
        year=1996,
        mechanism="Observation of others' actions activates neural circuits involved in performing those actions—supporting social cognition.",
        key_elements=["Communal areas", "co-visibility zones", "shared workspaces"],
        observed_effects=["Empathic simulation", "social cognition"],
        key_references=["de Borst et al. (2019). fMRI evidence for imagined navigation. Frontiers."]
    ),
    "entrainment": TheoryInfo(
        theory_id="entrainment",
        name="Entrainment",
        author="Franěk et al.",
        year=2018,
        mechanism="Rhythmic environmental cues (e.g., light, sound, movement) synchronize physiological states like heart rate or attention cycles.",
        key_elements=["Rhythmic lighting", "soundscapes", "paving textures", "spatial modules"],
        observed_effects=["Synchronization", "comfort", "gait patterns"],
        key_references=["Franěk, M. et al. (2018). Walking in a rhythmically structured environment. Frontiers."]
    ),
    "thermal_allostasis": TheoryInfo(
        theory_id="thermal_allostasis",
        name="Thermal Allostasis",
        author="Zhang et al.",
        year=2010,
        mechanism="Humans regulate comfort by actively adjusting behavior and environmental variables; spaces should support such regulation.",
        key_elements=["Adjustable HVAC", "operable windows", "radiant floors"],
        observed_effects=["Comfort", "agency", "perceived control"],
        key_references=["Zhang, H., Arens, E., Huizenga, C., & Han, T. (2010). Thermal sensation and comfort models. Building and Environment, 45(2), 387-394. https://doi.org/10.1016/j.buildenv.2009.06.015"]
    ),
    "neuroaesthetics": TheoryInfo(
        theory_id="neuroaesthetics",
        name="Neuroaesthetics",
        author="Zeki",
        year=1999,
        mechanism="Aesthetic experience correlates with activation in specific neural circuits, modulated by form, symmetry, and context.",
        key_elements=["Ornament", "symmetry", "proportion", "refined materials"],
        observed_effects=["Pleasure", "attention", "curiosity"],
        key_references=["Brielmann, A. A., & Pelli, D. G. (2017). Beauty requires thought. Current Biology, 27(10), 1506-1513. https://doi.org/10.1016/j.cub.2017.04.018"]
    ),
    "territoriality": TheoryInfo(
        theory_id="territoriality",
        name="Territoriality",
        author="Altman",
        year=1975,
        mechanism="Humans demarcate zones of control; violation of these zones in architecture can provoke stress or defensive behavior.",
        key_elements=["Personal zones", "shared/public space", "thresholds", "visual markers"],
        observed_effects=["Boundary behavior", "stress", "satisfaction"],
        key_references=["Ruonavaara, H. (2005). Territoriality in housing. Housing, Theory and Society, 22(2), 92-108. https://doi.org/10.1080/14036090510032796"]
    ),
    "social_density": TheoryInfo(
        theory_id="social_density",
        name="Social Density Theory",
        author="Evans",
        year=2007,
        mechanism="The ratio of people to space affects stress, aggression, and comfort.",
        key_elements=["Room size", "furniture spacing", "visibility"],
        observed_effects=["Aggression", "withdrawal", "comfort", "well-being"],
        key_references=["Evans, G. W., & Wener, R. E. (2007). Crowding and personal space invasion on the train. Journal of Environmental Psychology, 27(1), 90-94. https://doi.org/10.1016/j.jenvp.2006.10.002"]
    ),
    "circadian": TheoryInfo(
        theory_id="circadian",
        name="Circadian Entrainment",
        author="Ghosh et al.",
        year=2015,
        mechanism="Light cues synchronize circadian rhythms; architectural lighting can disrupt or reinforce this.",
        key_elements=["Daylight", "light color temperature", "smart windows", "tunable LEDs"],
        observed_effects=["Sleep quality", "alertness", "circadian rhythm"],
        key_references=["Ghosh, A., Kaushik, A., & Ghosh, S. (2015). Influence of circadian rhythm in architectural lighting. Lighting Research & Technology, 47(6), 712-730. https://doi.org/10.1177/1477153515578915"]
    ),
    "semiosis": TheoryInfo(
        theory_id="semiosis",
        name="Meaning Construction / Semiosis",
        author="Lindstrom et al.",
        year=2016,
        mechanism="People derive meaning from architectural symbols; environments are semiotic systems with layered cultural codes.",
        key_elements=["Cultural motifs", "symbolic elements", "domes", "arches", "script"],
        observed_effects=["Identity", "belonging", "memory", "emotional resonance"],
        key_references=["Lindstrom, M., Shanks, M., & Papadopoulos, C. (2016). Archaeology and architecture: Memory, meaning and place. International Journal of Heritage Studies, 22(8), 635-647. https://doi.org/10.1080/13527258.2015.1117117"]
    ),
    "arch_narrative": TheoryInfo(
        theory_id="arch_narrative",
        name="Architectural Narrative",
        author="Loomis & Montello",
        year=2022,
        mechanism="Spaces unfold sequentially and suggest a storyline—cognitive maps form in part through this narrative experience.",
        key_elements=["Sequenced space", "axial planning", "entry sequences", "thresholds"],
        observed_effects=["Anticipation", "understanding of space", "cognitive mapping"],
        key_references=["Loomis, J. M., & Montello, D. R. (2022). Spatial narratives in the brain: A neurocognitive framework. Journal of Environmental Psychology, 82, 101832. https://doi.org/10.1016/j.jenvp.2022.101832"]
    ),
    "cognitive_load": TheoryInfo(
        theory_id="cognitive_load",
        name="Cognitive Load Theory",
        author="Sweller",
        year=1988,
        mechanism="Excessive information increases mental effort, reducing performance and increasing stress.",
        key_elements=["Signage", "wayfinding clutter", "simplified layouts"],
        observed_effects=["Error", "stress", "efficiency"],
        key_references=["Kalff, C., Pauen, S., & Staudte, M. (2020). The cognitive cost of disorientation in buildings. Cognitive Research: Principles and Implications, 5(1), 1-14. https://doi.org/10.1186/s41235-020-00228-3"]
    ),
    "emotion_congruent": TheoryInfo(
        theory_id="emotion_congruent",
        name="Emotion-Congruent Processing",
        author="Knez",
        year=2008,
        mechanism="Emotional states shape how environments are perceived and remembered.",
        key_elements=["Color", "light warmth", "acoustic tones", "warm materials"],
        observed_effects=["Memory encoding", "emotional regulation", "mood"],
        key_references=["Knez, I., & Niedenthal, P. M. (2008). Lighting in the home and cognitive-emotional processes. Environment and Behavior, 40(6), 715-735. https://doi.org/10.1177/0013916507301035"]
    ),
    "social_facilitation": TheoryInfo(
        theory_id="social_facilitation",
        name="Social Facilitation and Inhibition",
        author="Zajonc",
        year=1965,
        mechanism="The presence of others can enhance or impair task performance depending on complexity and privacy.",
        key_elements=["Open plans", "seating arrangements", "transparent partitions", "alcoves"],
        observed_effects=["Productivity", "anxiety", "inhibition"],
        key_references=["Xu, Y., Li, Y., Wang, H., & Zhang, H. (2020). The effect of spatial openness on social facilitation. Frontiers in Psychology, 11, 1665. https://doi.org/10.3389/fpsyg.2020.01665"]
    ),
}

# Architectural typologies
ARCHITECTURAL_TYPOLOGIES = {
    "residential": {
        "residential_single": "Single Family Home",
        "residential_multi": "Multi-Family / Apartment",
        "residential_senior": "Senior Living",
    },
    "commercial": {
        "office": "Office",
        "retail": "Retail / Commercial",
        "hospitality": "Hotel / Hospitality",
    },
    "institutional": {
        "healthcare": "Healthcare / Hospital",
        "education_k12": "School (K-12)",
        "education_higher": "Higher Education",
        "library": "Library",
        "museum": "Museum / Gallery",
    },
    "recreation": {
        "recreation": "Recreation / Sports",
        "religious": "Religious",
    },
    "industrial": {
        "industrial": "Industrial / Factory",
        "laboratory": "Laboratory / Research",
    },
    "urban": {
        "urban_space": "Urban Public Space",
        "transit": "Transit / Transportation",
    }
}


# =============================================================================
# Routes
# =============================================================================

@router.get("/theories", response_model=Dict[str, TheoryInfo])
async def get_theories():
    """Get all CNfA theories."""
    return CNFA_THEORIES


@router.get("/theories/{theory_id}", response_model=TheoryInfo)
async def get_theory(theory_id: str):
    """Get a specific theory."""
    if theory_id not in CNFA_THEORIES:
        raise HTTPException(status_code=404, detail=f"Theory {theory_id} not found")
    return CNFA_THEORIES[theory_id]


@router.get("/typologies")
async def get_typologies():
    """Get architectural typologies."""
    return ARCHITECTURAL_TYPOLOGIES


@router.get("/load-af-articles", response_model=List[ArticleSummary])
async def load_af_articles():
    """Load articles from Article Finder PDF collection."""
    articles = []

    if not AF_DATA_PATH.exists():
        logger.warning(f"AF data path not found: {AF_DATA_PATH}")
        return []

    # Load existing annotations to check status
    annotations = _load_annotations()

    for pdf_file in AF_DATA_PATH.glob("*.pdf"):
        # Skip job bundles
        if "job_bundles" in str(pdf_file):
            continue

        # Parse filename for metadata
        filename = pdf_file.stem
        article_id = _filename_to_id(filename)

        # Try to extract year from filename
        year = None
        import re
        year_match = re.search(r'\((\d{4})\)', filename)
        if year_match:
            year = int(year_match.group(1))

        # Check if annotated
        annotated = article_id in annotations
        quality = annotations.get(article_id, {}).get('quality_tier')

        articles.append(ArticleSummary(
            id=article_id,
            title=_clean_title(filename),
            year=year,
            annotated=annotated,
            quality=quality,
            pdf_path=str(pdf_file)
        ))

    # Sort by annotated status, then title
    articles.sort(key=lambda a: (a.annotated, a.title))

    return articles


@router.get("/load-db-articles", response_model=List[ArticleSummary])
async def load_db_articles():
    """Load articles from ae.db."""
    if not AE_DB_PATH.exists():
        raise HTTPException(status_code=404, detail="Database not found")

    annotations = _load_annotations()
    articles = []

    try:
        conn = sqlite3.connect(AE_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT article_id, title, authors, year
            FROM articles
            ORDER BY year DESC, title
            LIMIT 200
        """)

        for row in cursor.fetchall():
            article_id = row['article_id']
            annotated = article_id in annotations
            quality = annotations.get(article_id, {}).get('quality_tier')

            articles.append(ArticleSummary(
                id=article_id,
                title=row['title'],
                authors=row['authors'],
                year=row['year'],
                annotated=annotated,
                quality=quality
            ))

        conn.close()

    except Exception as e:
        logger.exception("Error loading from database")
        raise HTTPException(status_code=500, detail=str(e))

    return articles


@router.post("/save")
async def save_annotation(annotation: ArticleAnnotation):
    """Save an article annotation."""
    ANNOTATIONS_DIR.mkdir(parents=True, exist_ok=True)

    # Save to JSONL (append-only)
    annotations_file = ANNOTATIONS_DIR / "annotations.jsonl"

    annotation_dict = annotation.model_dump()
    annotation_dict['saved_at'] = datetime.utcnow().isoformat() + "Z"

    try:
        with open(annotations_file, "a") as f:
            f.write(json.dumps(annotation_dict) + "\n")

        logger.info(f"Saved annotation for {annotation.article_id}")

        return {"status": "success", "article_id": annotation.article_id}

    except Exception as e:
        logger.exception("Error saving annotation")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/annotation/{article_id}")
async def get_annotation(article_id: str):
    """Get annotation for a specific article."""
    annotations = _load_annotations()

    if article_id not in annotations:
        raise HTTPException(status_code=404, detail="Annotation not found")

    return annotations[article_id]


@router.get("/stats")
async def get_annotation_stats():
    """Get annotation statistics."""
    annotations = _load_annotations()

    stats = {
        "total_annotated": len(annotations),
        "by_quality": {},
        "by_study_type": {},
        "by_theory": {},
        "by_typology": {}
    }

    for ann in annotations.values():
        # Quality
        q = ann.get('quality_tier', 'unknown')
        stats["by_quality"][q] = stats["by_quality"].get(q, 0) + 1

        # Study type
        st = ann.get('study_type', 'unknown')
        stats["by_study_type"][st] = stats["by_study_type"].get(st, 0) + 1

        # Theories
        for t in ann.get('theories', []):
            stats["by_theory"][t] = stats["by_theory"].get(t, 0) + 1

        # Typologies
        for t in ann.get('typologies', []):
            stats["by_typology"][t] = stats["by_typology"].get(t, 0) + 1

    return stats


# =============================================================================
# PDF Upload Endpoints
# =============================================================================

# Directory for uploaded PDFs
PDF_UPLOAD_DIR = Path("/Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/data/pdfs")


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF file for annotation.

    The file is stored in data/pdfs/ and registered in the articles database.
    Returns the article ID and path for immediate use.
    """

    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Create upload directory if needed
    PDF_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # Generate unique filename to avoid collisions
    content = await file.read()
    file_hash = hashlib.md5(content).hexdigest()[:8]
    safe_filename = _safe_filename(file.filename)
    unique_filename = f"{safe_filename[:-4]}_{file_hash}.pdf"
    file_path = PDF_UPLOAD_DIR / unique_filename

    # Save file
    try:
        with open(file_path, "wb") as f:
            f.write(content)

        logger.info(f"Uploaded PDF: {unique_filename} ({len(content)} bytes)")

        # Generate article ID from filename
        article_id = _filename_to_id(safe_filename)

        # Try to extract metadata from filename
        title = _clean_title(safe_filename)
        year = _extract_year(safe_filename)

        # Register in database (optional - if DB exists)
        try:
            _register_pdf_in_db(article_id, title, year, str(file_path))
        except Exception as db_err:
            logger.warning(f"Could not register in DB (non-fatal): {db_err}")

        return {
            "status": "success",
            "article_id": article_id,
            "filename": unique_filename,
            "path": str(file_path),
            "title": title,
            "year": year,
            "size_bytes": len(content)
        }

    except Exception as e:
        logger.exception("Upload failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-batch")
async def upload_pdfs_batch(files: List[UploadFile] = File(...)):
    """
    Upload multiple PDF files at once.

    Returns a list of results for each file.
    """

    results = []
    for file in files:
        try:
            result = await upload_pdf(file)
            results.append({"filename": file.filename, "status": "success", **result})
        except HTTPException as e:
            results.append({"filename": file.filename, "status": "error", "error": e.detail})
        except Exception as e:
            results.append({"filename": file.filename, "status": "error", "error": str(e)})

    return {
        "total": len(files),
        "successful": sum(1 for r in results if r["status"] == "success"),
        "failed": sum(1 for r in results if r["status"] == "error"),
        "results": results
    }


@router.get("/uploaded-pdfs")
async def list_uploaded_pdfs():
    """List all uploaded PDFs."""
    if not PDF_UPLOAD_DIR.exists():
        return []

    pdfs = []
    for pdf_file in PDF_UPLOAD_DIR.glob("*.pdf"):
        stat = pdf_file.stat()
        pdfs.append({
            "filename": pdf_file.name,
            "path": str(pdf_file),
            "size_bytes": stat.st_size,
            "uploaded_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
        })

    # Sort by upload time, newest first
    pdfs.sort(key=lambda x: x["uploaded_at"], reverse=True)
    return pdfs


# =============================================================================
# Helper Functions
# =============================================================================

# =============================================================================
# Zotero PDF Endpoint (local storage + API fallback)
# =============================================================================

@router.get("/zotero/pdf/{item_key}")
async def get_zotero_pdf(
    item_key: str,
    api_key: str = Query(..., description="Zotero API key"),
    user_id: str = Query(None, description="Zotero user ID"),
    group_id: str = Query(None, description="Zotero group ID")
):
    """
    Serve a PDF for a Zotero item.

    LOOKUP ORDER:
    1. Check local Zotero storage (~/Zotero/storage/{attachment_key}/)
    2. Fall back to Zotero API (if files are synced to cloud)

    For local-only Zotero libraries, this uses the local storage directly.
    For server deployment, PDFs should be migrated to the server first.
    """
    import httpx
    from fastapi.responses import FileResponse, StreamingResponse
    from app.config.pdf_storage import find_pdf_by_zotero_key, get_config

    if not user_id and not group_id:
        raise HTTPException(status_code=400, detail="Either user_id or group_id required")

    base_url = f"https://api.zotero.org/groups/{group_id}" if group_id else f"https://api.zotero.org/users/{user_id}"

    # First, get the item's children to find PDF attachment key
    children_url = f"{base_url}/items/{item_key}/children?format=json"

    try:
        async with httpx.AsyncClient() as client:
            children_resp = await client.get(
                children_url,
                headers={
                    "Zotero-API-Key": api_key,
                    "Zotero-API-Version": "3"
                },
                timeout=30.0
            )

            if children_resp.status_code != 200:
                raise HTTPException(status_code=children_resp.status_code, detail="Failed to get Zotero attachments")

            children = children_resp.json()

            # Find PDF attachment
            pdf_attachment = None
            for child in children:
                if child.get("data", {}).get("contentType") == "application/pdf":
                    pdf_attachment = child
                    break

            if not pdf_attachment:
                raise HTTPException(status_code=404, detail="No PDF attachment found for this item")

            attachment_key = pdf_attachment["key"]
            filename = pdf_attachment.get("data", {}).get("filename", f"{item_key}.pdf")

            # STEP 1: Try local Zotero storage first
            local_pdf = find_pdf_by_zotero_key(attachment_key)
            if local_pdf and local_pdf.exists():
                logger.info(f"Serving PDF from local Zotero storage: {local_pdf}")
                return FileResponse(
                    path=str(local_pdf),
                    media_type="application/pdf",
                    filename=filename
                )

            # STEP 2: Fall back to Zotero API (for cloud-synced files)
            logger.info(f"PDF not in local storage, trying Zotero API for {attachment_key}")
            file_url = f"{base_url}/items/{attachment_key}/file"
            pdf_resp = await client.get(
                file_url,
                headers={"Zotero-API-Key": api_key},
                timeout=60.0,
                follow_redirects=True
            )

            if pdf_resp.status_code == 200:
                return StreamingResponse(
                    iter([pdf_resp.content]),
                    media_type="application/pdf",
                    headers={
                        "Content-Disposition": f'inline; filename="{filename}"',
                        "Content-Length": str(len(pdf_resp.content))
                    }
                )
            elif pdf_resp.status_code == 404:
                # PDF not in cloud either - it's local-only but not found
                config = get_config()
                raise HTTPException(
                    status_code=404,
                    detail=f"PDF not found. Expected at: {config.zotero_storage_path}/{attachment_key}/"
                )
            else:
                raise HTTPException(status_code=pdf_resp.status_code, detail="Failed to download PDF from Zotero")

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Zotero request timed out")
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Failed to connect to Zotero: {str(e)}")


@router.get("/zotero/collections")
async def get_zotero_collections(
    api_key: str = Query(..., description="Zotero API key"),
    user_id: str = Query(None, description="Zotero user ID"),
    group_id: str = Query(None, description="Zotero group ID")
):
    """Get list of Zotero collections for the user/group."""
    import httpx

    if not user_id and not group_id:
        raise HTTPException(status_code=400, detail="Either user_id or group_id required")

    base_url = f"https://api.zotero.org/groups/{group_id}" if group_id else f"https://api.zotero.org/users/{user_id}"
    url = f"{base_url}/collections?format=json"

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                url,
                headers={
                    "Zotero-API-Key": api_key,
                    "Zotero-API-Version": "3"
                },
                timeout=30.0
            )

            if resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code, detail="Failed to get Zotero collections")

            collections = resp.json()
            return [
                {
                    "key": c["key"],
                    "name": c["data"]["name"],
                    "parent": c["data"].get("parentCollection"),
                    "num_items": c["meta"].get("numItems", 0)
                }
                for c in collections
            ]

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Zotero request timed out")
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Failed to connect to Zotero: {str(e)}")


# =============================================================================
# Helper Functions
# =============================================================================

def _safe_filename(filename: str) -> str:
    """Make filename safe for filesystem."""
    import re
    # Keep only safe characters
    safe = re.sub(r'[^a-zA-Z0-9_\-\. ]', '_', filename)
    # Collapse multiple underscores/spaces
    safe = re.sub(r'[_\s]+', '_', safe)
    return safe.strip('_')


def _extract_year(filename: str) -> Optional[int]:
    """Try to extract year from filename."""
    import re
    # Common patterns: (2024), _2024_, 2024.pdf
    patterns = [
        r'\((\d{4})\)',      # (2024)
        r'_(\d{4})_',        # _2024_
        r'_(\d{4})\.pdf',    # _2024.pdf
        r'\b(19\d{2}|20\d{2})\b'  # Any 4-digit year
    ]
    for pattern in patterns:
        match = re.search(pattern, filename)
        if match:
            year = int(match.group(1))
            if 1900 <= year <= 2030:
                return year
    return None


def _register_pdf_in_db(article_id: str, title: str, year: Optional[int], pdf_path: str):
    """Register uploaded PDF in the articles database."""
    import sqlite3

    if not AE_DB_PATH.exists():
        return

    conn = sqlite3.connect(AE_DB_PATH)
    cursor = conn.cursor()

    try:
        # Check if article already exists
        cursor.execute("SELECT article_id FROM articles WHERE article_id = ?", (article_id,))
        if cursor.fetchone():
            # Update path only
            cursor.execute(
                "UPDATE articles SET pdf_path = ? WHERE article_id = ?",
                (pdf_path, article_id)
            )
        else:
            # Insert new article
            cursor.execute("""
                INSERT INTO articles (article_id, title, year, pdf_path, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (article_id, title, year, pdf_path, datetime.utcnow().isoformat()))

        conn.commit()
    finally:
        conn.close()

def _load_annotations() -> Dict[str, Dict[str, Any]]:
    """Load all annotations from JSONL file."""
    annotations = {}
    annotations_file = ANNOTATIONS_DIR / "annotations.jsonl"

    if not annotations_file.exists():
        return annotations

    try:
        with open(annotations_file) as f:
            for line in f:
                if line.strip():
                    ann = json.loads(line)
                    # Keep most recent annotation per article
                    annotations[ann['article_id']] = ann
    except Exception as e:
        logger.warning(f"Error loading annotations: {e}")

    return annotations


def _filename_to_id(filename: str) -> str:
    """Convert filename to article ID."""
    import re
    # Remove special characters, keep alphanumeric and underscores
    clean = re.sub(r'[^a-zA-Z0-9_]', '_', filename)
    # Collapse multiple underscores
    clean = re.sub(r'_+', '_', clean)
    return clean.lower()[:100]


def _clean_title(filename: str) -> str:
    """Clean filename to readable title."""
    import re
    # Remove extension
    title = filename.replace('.pdf', '')
    # Replace underscores with spaces
    title = title.replace('_', ' ')
    # Remove author formatting patterns
    title = re.sub(r'^[A-Z][a-z]+,\s*[A-Z]\.\s*(\([0-9]{4}\)\.\s*)?', '', title)
    # Truncate if too long
    if len(title) > 100:
        title = title[:97] + "..."
    return title.strip()
