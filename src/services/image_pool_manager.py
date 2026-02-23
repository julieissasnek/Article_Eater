"""
Image Pool Manager
==================

Manages a local database of Creative Commons images for gallery building.
Supports downloading from Unsplash, Pexels, and Pixabay.

Date: February 8, 2026
Version: V23.0.0 (Post-Quinean, Foundherentist)
"""

import sqlite3
import hashlib
import json
import logging
import os
import requests
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)

# =============================================================================
# Configuration
# =============================================================================

IMAGE_POOL_DB = Path("data/image_pool/image_pool.db")
IMAGE_STORAGE_DIR = Path("data/image_pool/images")
THUMBNAIL_DIR = Path("data/image_pool/thumbnails")

# API Keys (environment variables override these defaults)
# David's Unsplash app ID: 865406
UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY", "xXH78GMO2pWR9dJEK--B7ri1URY6GILqOdLPJ_eImPI")
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")
PIXABAY_API_KEY = os.environ.get("PIXABAY_API_KEY", "")


# =============================================================================
# Query Presets for Environmental Psychology
# =============================================================================

QUERY_PRESETS = {
    "refuge": {
        "label": "Refuge (Enclosure/Safety)",
        "queries": [
            "alcove seating",
            "reading nook",
            "window seat cozy",
            "booth seating restaurant",
            "semi-private workspace",
            "cubicle office",
            "canopy shelter",
            "covered patio",
            "enclosed garden",
            "library carrel",
        ],
        "feature_tags": ["refuge", "enclosure", "shelter", "privacy"],
    },
    "prospect": {
        "label": "Prospect (Views/Openness)",
        "queries": [
            "panoramic view office",
            "floor to ceiling windows",
            "open plan office",
            "atrium lobby",
            "rooftop terrace city view",
            "balcony overlook",
            "mezzanine view",
            "glass wall building",
            "observation deck",
            "open landscape office",
        ],
        "feature_tags": ["prospect", "vista", "openness", "view"],
    },
    "biophilia": {
        "label": "Biophilia (Nature Connection)",
        "queries": [
            "indoor plants office",
            "living wall interior",
            "natural light workspace",
            "wood interior design",
            "water feature lobby",
            "green building interior",
            "biophilic office design",
            "nature view window",
            "courtyard garden",
            "skylight natural",
        ],
        "feature_tags": ["biophilia", "nature", "plants", "natural_materials"],
    },
    "wayfinding": {
        "label": "Wayfinding (Navigation)",
        "queries": [
            "building lobby signage",
            "corridor wayfinding",
            "airport terminal navigation",
            "hospital corridor",
            "museum gallery path",
            "open staircase",
            "atrium circulation",
            "building entrance",
            "landmark interior",
            "clear sightlines building",
        ],
        "feature_tags": ["wayfinding", "navigation", "circulation", "legibility"],
    },
    "complexity": {
        "label": "Complexity (Visual Interest)",
        "queries": [
            "ornate interior design",
            "detailed ceiling architecture",
            "patterned floor tile",
            "textured wall interior",
            "varied materials interior",
            "eclectic interior design",
            "layered interior space",
            "rich texture interior",
            "decorative architecture",
            "visual complexity building",
        ],
        "feature_tags": ["complexity", "visual_interest", "detail", "ornamentation"],
    },
    "coherence": {
        "label": "Coherence (Order/Unity)",
        "queries": [
            "minimalist interior",
            "clean modern office",
            "unified interior design",
            "monochrome interior",
            "simple workspace",
            "orderly office space",
            "symmetrical interior",
            "harmonious interior",
            "consistent design interior",
            "calm workspace",
        ],
        "feature_tags": ["coherence", "order", "unity", "simplicity"],
    },
    "mystery": {
        "label": "Mystery (Exploration Promise)",
        "queries": [
            "curved corridor",
            "partial view interior",
            "layered space architecture",
            "depth interior design",
            "winding staircase",
            "hidden room",
            "glimpse interior",
            "unfolding space",
            "sequential reveal architecture",
            "intriguing interior",
        ],
        "feature_tags": ["mystery", "exploration", "curiosity", "depth"],
    },
    "office_types": {
        "label": "Office Types",
        "queries": [
            "open plan office modern",
            "private office executive",
            "coworking space",
            "hot desk office",
            "conference room",
            "meeting room glass",
            "phone booth office",
            "collaboration space",
            "focus room office",
            "breakout space office",
        ],
        "feature_tags": ["office", "workspace", "commercial"],
    },
    "building_types": {
        "label": "Building Types",
        "queries": [
            "hospital interior",
            "school classroom",
            "library interior",
            "museum gallery",
            "hotel lobby",
            "retail store interior",
            "restaurant interior",
            "airport terminal",
            "train station interior",
            "residential living room",
        ],
        "feature_tags": ["building_type"],
    },
    "lighting": {
        "label": "Lighting Conditions",
        "queries": [
            "natural daylight interior",
            "dim ambient lighting",
            "bright office lighting",
            "warm lighting interior",
            "cool lighting modern",
            "dramatic lighting architecture",
            "indirect lighting ceiling",
            "task lighting desk",
            "accent lighting interior",
            "mixed lighting office",
        ],
        "feature_tags": ["lighting", "illumination", "ambiance"],
    },
}


# =============================================================================
# Data Classes
# =============================================================================

class ImageSource(Enum):
    UNSPLASH = "unsplash"
    PEXELS = "pexels"
    PIXABAY = "pixabay"
    MANUAL = "manual"
    UNKNOWN = "unknown"


class LicenseType(Enum):
    CC0 = "CC0"
    CC_BY = "CC-BY"
    CC_BY_SA = "CC-BY-SA"
    CC_BY_NC = "CC-BY-NC"
    UNSPLASH = "Unsplash License"
    PEXELS = "Pexels License"
    PIXABAY = "Pixabay License"
    UNKNOWN = "Unknown"


@dataclass
class PoolImage:
    """An image in the local pool."""
    image_id: str
    source: ImageSource
    source_id: str  # ID from the source API
    source_url: str  # Original URL at source
    local_path: str  # Local file path
    thumbnail_path: str

    # Metadata
    query_used: str
    width: int
    height: int
    photographer: str
    photographer_url: str
    license_type: LicenseType
    attribution: str

    # Tags and features
    feature_tags: List[str] = field(default_factory=list)
    context_tags: List[str] = field(default_factory=list)
    user_tags: List[str] = field(default_factory=list)

    # Scores (0-1, set during tagging)
    feature_scores: Dict[str, float] = field(default_factory=dict)

    # Metadata
    downloaded_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tagged_at: Optional[datetime] = None
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "image_id": self.image_id,
            "source": self.source.value,
            "source_id": self.source_id,
            "source_url": self.source_url,
            "local_path": self.local_path,
            "thumbnail_path": self.thumbnail_path,
            "query_used": self.query_used,
            "width": self.width,
            "height": self.height,
            "photographer": self.photographer,
            "photographer_url": self.photographer_url,
            "license_type": self.license_type.value,
            "attribution": self.attribution,
            "feature_tags": self.feature_tags,
            "context_tags": self.context_tags,
            "user_tags": self.user_tags,
            "feature_scores": self.feature_scores,
            "downloaded_at": self.downloaded_at.isoformat(),
            "tagged_at": self.tagged_at.isoformat() if self.tagged_at else None,
            "notes": self.notes,
        }

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "PoolImage":
        return cls(
            image_id=row["image_id"],
            source=ImageSource(row["source"]),
            source_id=row["source_id"],
            source_url=row["source_url"],
            local_path=row["local_path"],
            thumbnail_path=row["thumbnail_path"],
            query_used=row["query_used"],
            width=row["width"],
            height=row["height"],
            photographer=row["photographer"],
            photographer_url=row["photographer_url"],
            license_type=LicenseType(row["license_type"]),
            attribution=row["attribution"],
            feature_tags=json.loads(row["feature_tags"]) if row["feature_tags"] else [],
            context_tags=json.loads(row["context_tags"]) if row["context_tags"] else [],
            user_tags=json.loads(row["user_tags"]) if row["user_tags"] else [],
            feature_scores=json.loads(row["feature_scores"]) if row["feature_scores"] else {},
            downloaded_at=datetime.fromisoformat(row["downloaded_at"]),
            tagged_at=datetime.fromisoformat(row["tagged_at"]) if row["tagged_at"] else None,
            notes=row["notes"] or "",
        )


# =============================================================================
# Database Management
# =============================================================================

def init_database():
    """Initialize the image pool database."""
    IMAGE_POOL_DB.parent.mkdir(parents=True, exist_ok=True)
    IMAGE_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(IMAGE_POOL_DB))
    conn.row_factory = sqlite3.Row

    conn.executescript("""
        CREATE TABLE IF NOT EXISTS images (
            image_id TEXT PRIMARY KEY,
            source TEXT NOT NULL,
            source_id TEXT NOT NULL,
            source_url TEXT NOT NULL,
            local_path TEXT NOT NULL,
            thumbnail_path TEXT,
            query_used TEXT,
            width INTEGER,
            height INTEGER,
            photographer TEXT,
            photographer_url TEXT,
            license_type TEXT,
            attribution TEXT,
            feature_tags TEXT,  -- JSON array
            context_tags TEXT,  -- JSON array
            user_tags TEXT,     -- JSON array
            feature_scores TEXT, -- JSON object
            downloaded_at TEXT NOT NULL,
            tagged_at TEXT,
            notes TEXT,
            UNIQUE(source, source_id)
        );

        CREATE INDEX IF NOT EXISTS idx_images_source ON images(source);
        CREATE INDEX IF NOT EXISTS idx_images_query ON images(query_used);
        CREATE INDEX IF NOT EXISTS idx_images_downloaded ON images(downloaded_at);

        CREATE TABLE IF NOT EXISTS download_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            source TEXT NOT NULL,
            count_requested INTEGER,
            count_downloaded INTEGER,
            timestamp TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS tags (
            tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
            tag_name TEXT UNIQUE NOT NULL,
            tag_category TEXT,  -- feature, context, user
            description TEXT,
            created_at TEXT NOT NULL
        );
    """)

    conn.commit()
    conn.close()
    logger.info(f"Image pool database initialized at {IMAGE_POOL_DB}")


def get_connection() -> sqlite3.Connection:
    """Get a database connection."""
    if not IMAGE_POOL_DB.exists():
        init_database()
    conn = sqlite3.connect(str(IMAGE_POOL_DB))
    conn.row_factory = sqlite3.Row
    return conn


# =============================================================================
# Image Download Functions
# =============================================================================

def download_from_unsplash(query: str, count: int = 10) -> List[Dict[str, Any]]:
    """Download images from Unsplash API."""
    if not UNSPLASH_ACCESS_KEY:
        logger.warning("UNSPLASH_ACCESS_KEY not set. Using demo mode.")
        return _demo_images(query, count, "unsplash")

    results = []
    url = "https://api.unsplash.com/search/photos"
    headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
    params = {
        "query": query,
        "per_page": min(count, 30),
        "orientation": "landscape",
    }

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        for photo in data.get("results", [])[:count]:
            results.append({
                "source": "unsplash",
                "source_id": photo["id"],
                "source_url": photo["links"]["html"],
                "download_url": photo["urls"]["regular"],
                "thumbnail_url": photo["urls"]["thumb"],
                "width": photo["width"],
                "height": photo["height"],
                "photographer": photo["user"]["name"],
                "photographer_url": photo["user"]["links"]["html"],
                "license_type": "Unsplash License",
                "attribution": f"Photo by {photo['user']['name']} on Unsplash",
            })
    except Exception as e:
        logger.error(f"Unsplash API error: {e}")

    return results


def download_from_pexels(query: str, count: int = 10) -> List[Dict[str, Any]]:
    """Download images from Pexels API."""
    if not PEXELS_API_KEY:
        logger.warning("PEXELS_API_KEY not set. Using demo mode.")
        return _demo_images(query, count, "pexels")

    results = []
    url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": PEXELS_API_KEY}
    params = {
        "query": query,
        "per_page": min(count, 80),
        "orientation": "landscape",
    }

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        for photo in data.get("photos", [])[:count]:
            results.append({
                "source": "pexels",
                "source_id": str(photo["id"]),
                "source_url": photo["url"],
                "download_url": photo["src"]["large"],
                "thumbnail_url": photo["src"]["medium"],
                "width": photo["width"],
                "height": photo["height"],
                "photographer": photo["photographer"],
                "photographer_url": photo["photographer_url"],
                "license_type": "Pexels License",
                "attribution": f"Photo by {photo['photographer']} on Pexels",
            })
    except Exception as e:
        logger.error(f"Pexels API error: {e}")

    return results


def download_from_pixabay(query: str, count: int = 10) -> List[Dict[str, Any]]:
    """Download images from Pixabay API."""
    if not PIXABAY_API_KEY:
        logger.warning("PIXABAY_API_KEY not set. Using demo mode.")
        return _demo_images(query, count, "pixabay")

    results = []
    url = "https://pixabay.com/api/"
    params = {
        "key": PIXABAY_API_KEY,
        "q": query,
        "per_page": min(count, 200),
        "orientation": "horizontal",
        "image_type": "photo",
        "safesearch": "true",
    }

    try:
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        for photo in data.get("hits", [])[:count]:
            results.append({
                "source": "pixabay",
                "source_id": str(photo["id"]),
                "source_url": photo["pageURL"],
                "download_url": photo["largeImageURL"],
                "thumbnail_url": photo["previewURL"],
                "width": photo["imageWidth"],
                "height": photo["imageHeight"],
                "photographer": photo["user"],
                "photographer_url": f"https://pixabay.com/users/{photo['user']}-{photo['user_id']}/",
                "license_type": "Pixabay License",
                "attribution": f"Image by {photo['user']} from Pixabay",
            })
    except Exception as e:
        logger.error(f"Pixabay API error: {e}")

    return results


def _demo_images(query: str, count: int, source: str) -> List[Dict[str, Any]]:
    """Generate demo image entries using picsum.photos (for testing without API keys)."""
    results = []
    query_hash = hashlib.md5(query.encode()).hexdigest()[:8]

    for i in range(count):
        seed = f"{query_hash}_{i}"
        results.append({
            "source": source,
            "source_id": f"demo_{seed}",
            "source_url": f"https://picsum.photos/seed/{seed}/info",
            "download_url": f"https://picsum.photos/seed/{seed}/800/600",
            "thumbnail_url": f"https://picsum.photos/seed/{seed}/300/200",
            "width": 800,
            "height": 600,
            "photographer": "Lorem Picsum",
            "photographer_url": "https://picsum.photos/",
            "license_type": "CC0",
            "attribution": f"Demo image for query: {query}",
        })

    return results


def save_image_to_pool(
    image_data: Dict[str, Any],
    query: str,
    feature_tags: List[str] = None
) -> Optional[PoolImage]:
    """Download an image and save it to the local pool."""
    conn = get_connection()

    try:
        source = image_data["source"]
        source_id = image_data["source_id"]

        # Check if already exists
        existing = conn.execute(
            "SELECT image_id FROM images WHERE source = ? AND source_id = ?",
            (source, source_id)
        ).fetchone()

        if existing:
            logger.info(f"Image {source}/{source_id} already in pool")
            return None

        # Generate image ID
        image_id = f"img_{hashlib.md5(f'{source}_{source_id}'.encode()).hexdigest()[:12]}"

        # Download image
        img_ext = ".jpg"
        local_filename = f"{image_id}{img_ext}"
        local_path = IMAGE_STORAGE_DIR / local_filename
        thumb_path = THUMBNAIL_DIR / f"thumb_{local_filename}"

        # Download main image
        try:
            resp = requests.get(image_data["download_url"], timeout=60)
            resp.raise_for_status()
            with open(local_path, "wb") as f:
                f.write(resp.content)
        except Exception as e:
            logger.error(f"Failed to download image: {e}")
            return None

        # Download thumbnail
        try:
            resp = requests.get(image_data["thumbnail_url"], timeout=30)
            resp.raise_for_status()
            with open(thumb_path, "wb") as f:
                f.write(resp.content)
        except Exception as e:
            logger.warning(f"Failed to download thumbnail: {e}")
            thumb_path = local_path  # Use main image as fallback

        # Create pool image
        pool_image = PoolImage(
            image_id=image_id,
            source=ImageSource(source),
            source_id=source_id,
            source_url=image_data["source_url"],
            local_path=str(local_path),
            thumbnail_path=str(thumb_path),
            query_used=query,
            width=image_data["width"],
            height=image_data["height"],
            photographer=image_data["photographer"],
            photographer_url=image_data["photographer_url"],
            license_type=LicenseType(image_data["license_type"]),
            attribution=image_data["attribution"],
            feature_tags=feature_tags or [],
        )

        # Insert into database
        conn.execute("""
            INSERT INTO images (
                image_id, source, source_id, source_url, local_path, thumbnail_path,
                query_used, width, height, photographer, photographer_url,
                license_type, attribution, feature_tags, context_tags, user_tags,
                feature_scores, downloaded_at, tagged_at, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            pool_image.image_id,
            pool_image.source.value,
            pool_image.source_id,
            pool_image.source_url,
            pool_image.local_path,
            pool_image.thumbnail_path,
            pool_image.query_used,
            pool_image.width,
            pool_image.height,
            pool_image.photographer,
            pool_image.photographer_url,
            pool_image.license_type.value,
            pool_image.attribution,
            json.dumps(pool_image.feature_tags),
            json.dumps(pool_image.context_tags),
            json.dumps(pool_image.user_tags),
            json.dumps(pool_image.feature_scores),
            pool_image.downloaded_at.isoformat(),
            None,
            pool_image.notes,
        ))

        conn.commit()
        logger.info(f"Saved image {image_id} to pool")
        return pool_image

    except Exception as e:
        logger.error(f"Error saving image: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()


def search_and_download(
    query: str,
    source: str = "unsplash",
    count: int = 10,
    feature_tags: List[str] = None
) -> List[PoolImage]:
    """Search for images and download them to the local pool."""
    init_database()

    # Get images from source
    if source == "unsplash":
        images = download_from_unsplash(query, count)
    elif source == "pexels":
        images = download_from_pexels(query, count)
    elif source == "pixabay":
        images = download_from_pixabay(query, count)
    else:
        logger.error(f"Unknown source: {source}")
        return []

    # Save each image
    saved = []
    for img_data in images:
        pool_img = save_image_to_pool(img_data, query, feature_tags)
        if pool_img:
            saved.append(pool_img)
        time.sleep(0.5)  # Rate limiting

    # Log the download
    conn = get_connection()
    conn.execute("""
        INSERT INTO download_log (query, source, count_requested, count_downloaded, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (query, source, count, len(saved), datetime.now(timezone.utc).isoformat()))
    conn.commit()
    conn.close()

    return saved


# =============================================================================
# Query Functions
# =============================================================================

def get_all_images(
    limit: int = 100,
    offset: int = 0,
    source: str = None,
    query: str = None,
    tagged_only: bool = False
) -> List[PoolImage]:
    """Get images from the pool with optional filters."""
    conn = get_connection()

    sql = "SELECT * FROM images WHERE 1=1"
    params = []

    if source:
        sql += " AND source = ?"
        params.append(source)

    if query:
        sql += " AND query_used LIKE ?"
        params.append(f"%{query}%")

    if tagged_only:
        sql += " AND tagged_at IS NOT NULL"

    sql += " ORDER BY downloaded_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    rows = conn.execute(sql, params).fetchall()
    conn.close()

    return [PoolImage.from_row(row) for row in rows]


def get_image_by_id(image_id: str) -> Optional[PoolImage]:
    """Get a single image by ID."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM images WHERE image_id = ?", (image_id,)
    ).fetchone()
    conn.close()

    if row:
        return PoolImage.from_row(row)
    return None


def update_image_tags(
    image_id: str,
    feature_tags: List[str] = None,
    context_tags: List[str] = None,
    user_tags: List[str] = None,
    feature_scores: Dict[str, float] = None,
    notes: str = None
) -> bool:
    """Update tags and scores for an image."""
    conn = get_connection()

    updates = []
    params = []

    if feature_tags is not None:
        updates.append("feature_tags = ?")
        params.append(json.dumps(feature_tags))

    if context_tags is not None:
        updates.append("context_tags = ?")
        params.append(json.dumps(context_tags))

    if user_tags is not None:
        updates.append("user_tags = ?")
        params.append(json.dumps(user_tags))

    if feature_scores is not None:
        updates.append("feature_scores = ?")
        params.append(json.dumps(feature_scores))

    if notes is not None:
        updates.append("notes = ?")
        params.append(notes)

    if updates:
        updates.append("tagged_at = ?")
        params.append(datetime.now(timezone.utc).isoformat())

        sql = f"UPDATE images SET {', '.join(updates)} WHERE image_id = ?"
        params.append(image_id)

        conn.execute(sql, params)
        conn.commit()

    conn.close()
    return True


def delete_image(image_id: str) -> bool:
    """Delete an image from the pool."""
    conn = get_connection()

    # Get paths first
    row = conn.execute(
        "SELECT local_path, thumbnail_path FROM images WHERE image_id = ?",
        (image_id,)
    ).fetchone()

    if row:
        # Delete files
        try:
            if row["local_path"] and Path(row["local_path"]).exists():
                Path(row["local_path"]).unlink()
            if row["thumbnail_path"] and Path(row["thumbnail_path"]).exists():
                Path(row["thumbnail_path"]).unlink()
        except Exception as e:
            logger.warning(f"Could not delete image files: {e}")

        # Delete from DB
        conn.execute("DELETE FROM images WHERE image_id = ?", (image_id,))
        conn.commit()

    conn.close()
    return True


def get_pool_stats() -> Dict[str, Any]:
    """Get statistics about the image pool."""
    conn = get_connection()

    stats = {
        "total_images": 0,
        "tagged_images": 0,
        "by_source": {},
        "by_query": {},
        "recent_downloads": [],
    }

    # Total counts
    row = conn.execute("SELECT COUNT(*) as total FROM images").fetchone()
    stats["total_images"] = row["total"]

    row = conn.execute(
        "SELECT COUNT(*) as tagged FROM images WHERE tagged_at IS NOT NULL"
    ).fetchone()
    stats["tagged_images"] = row["tagged"]

    # By source
    for row in conn.execute(
        "SELECT source, COUNT(*) as count FROM images GROUP BY source"
    ):
        stats["by_source"][row["source"]] = row["count"]

    # By query (top 20)
    for row in conn.execute("""
        SELECT query_used, COUNT(*) as count
        FROM images
        GROUP BY query_used
        ORDER BY count DESC
        LIMIT 20
    """):
        stats["by_query"][row["query_used"]] = row["count"]

    # Recent downloads
    for row in conn.execute("""
        SELECT query, source, count_downloaded, timestamp
        FROM download_log
        ORDER BY timestamp DESC
        LIMIT 10
    """):
        stats["recent_downloads"].append({
            "query": row["query"],
            "source": row["source"],
            "count": row["count_downloaded"],
            "timestamp": row["timestamp"],
        })

    conn.close()
    return stats


def get_query_presets() -> Dict[str, Any]:
    """Get the predefined query presets."""
    return QUERY_PRESETS


def export_for_gallery(
    image_ids: List[str] = None,
    tagged_only: bool = True
) -> List[Dict[str, Any]]:
    """Export images in format suitable for ClaimGalleryBuilder."""
    conn = get_connection()

    if image_ids:
        placeholders = ",".join("?" * len(image_ids))
        sql = f"SELECT * FROM images WHERE image_id IN ({placeholders})"
        rows = conn.execute(sql, image_ids).fetchall()
    elif tagged_only:
        rows = conn.execute(
            "SELECT * FROM images WHERE tagged_at IS NOT NULL"
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM images").fetchall()

    conn.close()

    # Convert to gallery format
    gallery_format = []
    for row in rows:
        img = PoolImage.from_row(row)

        # Get the primary feature score (highest one)
        primary_score = 0.5  # default
        if img.feature_scores:
            primary_score = max(img.feature_scores.values())

        gallery_format.append({
            "image_id": img.image_id,
            "uri_or_path": f"/api/v1/image-pool/image/{img.image_id}",
            "feature_score": primary_score,
            "confidence_basis": "human_tagged" if img.tagged_at else "untagged",
            "outcome_status": "literature_link_only",
            "building_type": _extract_building_type(img.context_tags),
            "culture_region": "unknown",
            "project_id": img.query_used,  # Use query as project grouping
            "source": img.source.value,
            "license": img.license_type.value,
            "attribution": img.attribution,
            "cues": img.feature_tags[:5],  # Top 5 feature tags as cues
            "feature_tags": img.feature_tags,
            "context_tags": img.context_tags,
            "moderator_flags": [],
            "thumbnail_uri": f"/api/v1/image-pool/thumbnail/{img.image_id}",
        })

    return gallery_format


def _extract_building_type(context_tags: List[str]) -> str:
    """Extract building type from context tags."""
    building_types = [
        "office", "hospital", "school", "library", "museum",
        "hotel", "retail", "restaurant", "airport", "residential"
    ]
    for tag in context_tags:
        tag_lower = tag.lower()
        for bt in building_types:
            if bt in tag_lower:
                return bt
    return "unknown"


# =============================================================================
# Initialize on import
# =============================================================================

if __name__ == "__main__":
    init_database()
    print(f"Database initialized at {IMAGE_POOL_DB}")
    print(f"Query presets: {list(QUERY_PRESETS.keys())}")
