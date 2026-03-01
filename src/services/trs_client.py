"""
TRS Client — Tag Registry Service Integration with Local Fallback
===================================================================

Sprint S-5: Fallback-first design pattern.
  - Local taxonomy cache works offline
  - TRS enriches tags when available (never blocks)
  - Health check before querying
  - Nightly delta sync (TRS → local)

Usage:
    from src.services.trs_client import TRSClient

    client = TRSClient()
    
    # Always returns tags (from TRS if healthy, local cache if not)
    tags = client.get_tags("facade_photograph.jpg", features={"complexity": 0.7})
    
    # Check status
    print(client.health_status())
"""

import json
import logging
import sqlite3
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent

# TRS Configuration
TRS_CONFIG = {
    "base_url": "http://localhost:8090/api/v1",  # Default TRS endpoint
    "schema_version": "0.2.8",
    "health_timeout_s": 2.0,
    "query_timeout_s": 5.0,
    "max_retries": 2,
    "cache_ttl_hours": 24,
}

# Local cache paths
LOCAL_CACHE_DIR = PROJECT_ROOT / "data" / "trs_cache"
LOCAL_CACHE_DB = LOCAL_CACHE_DIR / "trs_local.db"
SYNC_LOG_PATH = LOCAL_CACHE_DIR / "sync_log.json"


# =============================================================================
# Data Structures
# =============================================================================

@dataclass
class TRSTag:
    """A tag from TRS or local cache."""
    tag_id: str
    category: str
    label: str
    confidence: float = 0.0
    source: str = "local"  # "trs" or "local"
    cnfa_relevance: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "tag_id": self.tag_id,
            "category": self.category,
            "label": self.label,
            "confidence": self.confidence,
            "source": self.source,
            "cnfa_relevance": self.cnfa_relevance,
        }


@dataclass
class HealthStatus:
    """TRS service health status."""
    is_healthy: bool
    response_time_ms: float = 0.0
    last_checked: str = ""
    error: str = ""
    mode: str = "local"  # "trs", "local", "degraded"
    
    def to_dict(self) -> dict:
        return {
            "is_healthy": self.is_healthy,
            "response_time_ms": round(self.response_time_ms, 1),
            "last_checked": self.last_checked,
            "error": self.error,
            "mode": self.mode,
        }


# =============================================================================
# Local Taxonomy Cache
# =============================================================================

class LocalTaxonomyCache:
    """SQLite-backed local cache of tag taxonomy.
    
    Works completely offline. TRS enriches this cache when available.
    """
    
    def __init__(self, db_path: Path = LOCAL_CACHE_DB):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        self._seed_if_empty()
    
    def _init_db(self):
        """Create cache tables."""
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                tag_id TEXT PRIMARY KEY,
                category TEXT NOT NULL,
                label TEXT NOT NULL,
                cnfa_relevance TEXT,
                metadata TEXT DEFAULT '{}',
                source TEXT DEFAULT 'seed',
                synced_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tag_rules (
                rule_id INTEGER PRIMARY KEY AUTOINCREMENT,
                feature_name TEXT NOT NULL,
                feature_min REAL,
                feature_max REAL,
                tag_id TEXT NOT NULL,
                confidence REAL DEFAULT 0.5,
                FOREIGN KEY (tag_id) REFERENCES tags(tag_id)
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_tags_category ON tags(category)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_rules_feature ON tag_rules(feature_name)
        """)
        conn.commit()
        conn.close()
    
    def _seed_if_empty(self):
        """Seed with built-in architectural cognition tags."""
        conn = sqlite3.connect(str(self.db_path))
        count = conn.execute("SELECT COUNT(*) FROM tags").fetchone()[0]
        if count > 0:
            conn.close()
            return
        
        # Seed tags from our known taxonomy
        seed_tags = [
            # Spatial features
            ("spatial.openness", "spatial", "Spatial Openness", "cnfa.spatial_openness"),
            ("spatial.enclosure", "spatial", "Enclosure", "cnfa.enclosure"),
            ("spatial.ceiling_height", "spatial", "Ceiling Height", "cnfa.ceiling_height"),
            ("spatial.prospect", "spatial", "Prospect Quality", "cnfa.prospect"),
            ("spatial.refuge", "spatial", "Refuge Quality", "cnfa.refuge"),
            
            # Light features
            ("light.level", "light", "Light Level", "cnfa.light.level"),
            ("light.color_temp", "light", "Color Temperature", "cnfa.light.color_temperature"),
            ("light.daylight", "light", "Daylight Factor", "cnfa.light.daylight"),
            ("light.contrast", "light", "Light Contrast", "cnfa.light.contrast"),
            
            # Nature features
            ("nature.green_view", "nature", "Green View Index", "cnfa.green_view_index"),
            ("nature.biophilic", "nature", "Biophilic Elements", "cnfa.biophilic"),
            ("nature.water", "nature", "Water Features", "cnfa.water_features"),
            ("nature.natural_materials", "nature", "Natural Materials", "cnfa.natural_materials"),
            
            # Visual complexity
            ("complexity.visual", "complexity", "Visual Complexity", "cnfa.visual_complexity"),
            ("complexity.fractal", "complexity", "Fractal Dimension", "cnfa.fractal_dimension"),
            ("complexity.order", "complexity", "Visual Order", "cnfa.visual_order"),
            ("complexity.symmetry", "complexity", "Symmetry", "cnfa.symmetry"),
            
            # Material features
            ("material.warmth", "material", "Material Warmth", "cnfa.material_warmth"),
            ("material.texture", "material", "Surface Texture", "cnfa.surface_texture"),
            ("material.transparency", "material", "Transparency", "cnfa.transparency"),
            
            # Color features
            ("color.palette", "color", "Color Palette", "cnfa.color_palette"),
            ("color.saturation", "color", "Color Saturation", "cnfa.color_saturation"),
            ("color.temperature", "color", "Color Temperature", "cnfa.color_temperature"),
            
            # Social features
            ("social.density", "social", "Density/Occupancy", "cnfa.density_occupancy"),
            ("social.furniture", "social", "Furniture Layout", "cnfa.furniture_layout"),
            ("social.wayfinding", "social", "Wayfinding Cues", "cnfa.wayfinding_cues"),
            
            # Acoustic features
            ("acoustic.level", "acoustic", "Sound Level", "cnfa.sound_level"),
            ("acoustic.quality", "acoustic", "Acoustic Quality", "cnfa.acoustic_quality"),
            
            # Aesthetic features
            ("aesthetic.beauty", "aesthetic", "Beauty Rating", "cnfa.beauty_rating"),
            ("aesthetic.harmony", "aesthetic", "Visual Harmony", "cnfa.visual_harmony"),
            ("aesthetic.style", "aesthetic", "Architectural Style", "cnfa.arch_style"),
        ]
        
        for tag_id, category, label, cnfa in seed_tags:
            conn.execute(
                "INSERT INTO tags (tag_id, category, label, cnfa_relevance, source) VALUES (?, ?, ?, ?, 'seed')",
                (tag_id, category, label, cnfa)
            )
        
        # Seed feature→tag rules
        seed_rules = [
            ("visual_complexity", 0.0, 0.3, "complexity.visual", 0.7),
            ("visual_complexity", 0.7, 1.0, "complexity.visual", 0.9),
            ("green_view_index", 0.3, 1.0, "nature.green_view", 0.8),
            ("ceiling_height", 3.0, 100.0, "spatial.ceiling_height", 0.7),
            ("fractal_dimension", 1.2, 1.8, "complexity.fractal", 0.8),
            ("material_warmth", 0.5, 1.0, "material.warmth", 0.7),
            ("light_level", 0.0, 100.0, "light.level", 0.6),
            ("light_level", 300.0, 10000.0, "light.level", 0.6),
        ]
        
        for feature, fmin, fmax, tag_id, conf in seed_rules:
            conn.execute(
                "INSERT INTO tag_rules (feature_name, feature_min, feature_max, tag_id, confidence) VALUES (?, ?, ?, ?, ?)",
                (feature, fmin, fmax, tag_id, conf)
            )
        
        conn.commit()
        conn.close()
        logger.info(f"Seeded local cache with {len(seed_tags)} tags and {len(seed_rules)} rules")
    
    def get_tags_for_features(self, features: Dict[str, float]) -> List[TRSTag]:
        """Look up tags for a set of numeric image features."""
        conn = sqlite3.connect(str(self.db_path))
        tags = []
        
        for fname, fval in features.items():
            rows = conn.execute("""
                SELECT r.tag_id, r.confidence, t.category, t.label, t.cnfa_relevance
                FROM tag_rules r JOIN tags t ON r.tag_id = t.tag_id
                WHERE r.feature_name = ? AND r.feature_min <= ? AND r.feature_max >= ?
            """, (fname, fval, fval)).fetchall()
            
            for row in rows:
                tags.append(TRSTag(
                    tag_id=row[0],
                    confidence=row[1],
                    category=row[2],
                    label=row[3],
                    cnfa_relevance=row[4],
                    source="local",
                ))
        
        conn.close()
        return tags
    
    def get_all_tags(self) -> List[TRSTag]:
        """Get all cached tags."""
        conn = sqlite3.connect(str(self.db_path))
        rows = conn.execute(
            "SELECT tag_id, category, label, cnfa_relevance, source FROM tags"
        ).fetchall()
        conn.close()
        return [TRSTag(tag_id=r[0], category=r[1], label=r[2], 
                       cnfa_relevance=r[3], source=r[4]) for r in rows]
    
    def upsert_tags(self, tags: List[Dict[str, Any]], source: str = "trs"):
        """Insert or update tags from TRS sync."""
        conn = sqlite3.connect(str(self.db_path))
        now = datetime.now(timezone.utc).isoformat()
        
        for t in tags:
            conn.execute("""
                INSERT OR REPLACE INTO tags (tag_id, category, label, cnfa_relevance, metadata, source, synced_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                t["tag_id"], t.get("category", ""), t.get("label", ""),
                t.get("cnfa_relevance", ""), json.dumps(t.get("metadata", {})),
                source, now,
            ))
        
        conn.commit()
        conn.close()
        return len(tags)
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        conn = sqlite3.connect(str(self.db_path))
        total = conn.execute("SELECT COUNT(*) FROM tags").fetchone()[0]
        by_source = dict(conn.execute(
            "SELECT source, COUNT(*) FROM tags GROUP BY source"
        ).fetchall())
        rules = conn.execute("SELECT COUNT(*) FROM tag_rules").fetchone()[0]
        conn.close()
        return {"total_tags": total, "by_source": by_source, "total_rules": rules}


# =============================================================================
# TRS Health Checker
# =============================================================================

class TRSHealthChecker:
    """Monitor TRS service availability."""
    
    def __init__(self, base_url: str = TRS_CONFIG["base_url"],
                 timeout: float = TRS_CONFIG["health_timeout_s"]):
        self.base_url = base_url
        self.timeout = timeout
        self._last_status: Optional[HealthStatus] = None
        self._last_check_time: float = 0
        self._check_interval: float = 60.0  # Don't recheck within 60s
    
    def check(self, force: bool = False) -> HealthStatus:
        """Check TRS health. Uses cached result within interval."""
        now = time.time()
        if not force and self._last_status and (now - self._last_check_time) < self._check_interval:
            return self._last_status
        
        try:
            import urllib.request
            start = time.time()
            url = f"{self.base_url}/health"
            req = urllib.request.Request(url, method="GET")
            req.add_header("User-Agent", "ArticleEater-TRS/1.0")
            
            response = urllib.request.urlopen(req, timeout=self.timeout)
            elapsed_ms = (time.time() - start) * 1000
            
            if response.status == 200 and elapsed_ms < (self.timeout * 1000):
                status = HealthStatus(
                    is_healthy=True,
                    response_time_ms=elapsed_ms,
                    last_checked=datetime.now(timezone.utc).isoformat(),
                    mode="trs",
                )
            else:
                status = HealthStatus(
                    is_healthy=False,
                    response_time_ms=elapsed_ms,
                    last_checked=datetime.now(timezone.utc).isoformat(),
                    error=f"Slow response ({elapsed_ms:.0f}ms) or bad status ({response.status})",
                    mode="local",
                )
        except Exception as e:
            status = HealthStatus(
                is_healthy=False,
                last_checked=datetime.now(timezone.utc).isoformat(),
                error=str(e)[:200],
                mode="local",
            )
        
        self._last_status = status
        self._last_check_time = now
        return status


# =============================================================================
# TRS Client (Unified Interface)
# =============================================================================

class TRSClient:
    """Unified TRS client with local fallback.
    
    Design principle: local cache always works. TRS enriches when available.
    """
    
    def __init__(self, base_url: str = TRS_CONFIG["base_url"],
                 cache_db: Path = LOCAL_CACHE_DB):
        self.base_url = base_url
        self.cache = LocalTaxonomyCache(cache_db)
        self.health = TRSHealthChecker(base_url)
        self._stats = {"trs_queries": 0, "local_queries": 0, "trs_failures": 0}
    
    def get_tags(self, image_id: str, features: Dict[str, float] = None) -> List[TRSTag]:
        """Get tags for an image. Uses TRS if healthy, local cache otherwise.
        
        Args:
            image_id: Image identifier (filename, DOI-based ID, etc.)
            features: Numeric image features (e.g. {"visual_complexity": 0.7})
        
        Returns:
            List of TRSTag objects
        """
        features = features or {}
        
        # Check TRS health
        status = self.health.check()
        
        if status.is_healthy:
            # Try TRS first
            try:
                trs_tags = self._query_trs(image_id, features)
                self._stats["trs_queries"] += 1
                return trs_tags
            except Exception as e:
                logger.warning(f"TRS query failed, falling back to local: {e}")
                self._stats["trs_failures"] += 1
        
        # Fallback to local cache
        self._stats["local_queries"] += 1
        return self.cache.get_tags_for_features(features)
    
    def _query_trs(self, image_id: str, features: Dict[str, float]) -> List[TRSTag]:
        """Query TRS API for tags."""
        import urllib.request
        
        payload = json.dumps({
            "image_id": image_id,
            "features": features,
            "schema_version": TRS_CONFIG["schema_version"],
        }).encode("utf-8")
        
        url = f"{self.base_url}/tags/query"
        req = urllib.request.Request(url, data=payload, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("User-Agent", "ArticleEater-TRS/1.0")
        
        response = urllib.request.urlopen(req, timeout=TRS_CONFIG["query_timeout_s"])
        data = json.loads(response.read().decode("utf-8"))
        
        tags = []
        for t in data.get("tags", []):
            tags.append(TRSTag(
                tag_id=t.get("tag_id", ""),
                category=t.get("category", ""),
                label=t.get("label", ""),
                confidence=t.get("confidence", 0.5),
                source="trs",
                cnfa_relevance=t.get("cnfa_relevance"),
                metadata=t.get("metadata", {}),
            ))
        
        return tags
    
    def sync_from_trs(self) -> Dict[str, Any]:
        """Delta sync: pull new/updated tags from TRS into local cache.
        
        Designed for nightly cron execution.
        """
        status = self.health.check(force=True)
        if not status.is_healthy:
            return {"status": "skipped", "reason": status.error}
        
        try:
            import urllib.request
            
            # Get last sync timestamp
            last_sync = self._get_last_sync_time()
            
            url = f"{self.base_url}/tags/export"
            if last_sync:
                url += f"?since={last_sync}"
            
            req = urllib.request.Request(url, method="GET")
            req.add_header("User-Agent", "ArticleEater-TRS/1.0")
            
            response = urllib.request.urlopen(req, timeout=30)
            data = json.loads(response.read().decode("utf-8"))
            
            new_tags = data.get("tags", [])
            if new_tags:
                count = self.cache.upsert_tags(new_tags, source="trs")
                self._record_sync(count)
                return {"status": "synced", "tags_updated": count}
            
            return {"status": "no_updates"}
            
        except Exception as e:
            logger.error(f"TRS sync failed: {e}")
            return {"status": "error", "error": str(e)[:200]}
    
    def _get_last_sync_time(self) -> Optional[str]:
        """Get timestamp of last successful sync."""
        if SYNC_LOG_PATH.exists():
            with open(SYNC_LOG_PATH) as f:
                log = json.load(f)
            return log.get("last_sync")
        return None
    
    def _record_sync(self, count: int):
        """Record successful sync."""
        log = {
            "last_sync": datetime.now(timezone.utc).isoformat(),
            "tags_updated": count,
        }
        with open(SYNC_LOG_PATH, "w") as f:
            json.dump(log, f, indent=2)
    
    def health_status(self) -> Dict[str, Any]:
        """Get comprehensive status."""
        status = self.health.check()
        cache_stats = self.cache.get_stats()
        return {
            "trs": status.to_dict(),
            "cache": cache_stats,
            "client_stats": self._stats,
        }
    
    def get_all_cached_tags(self) -> List[TRSTag]:
        """Get all tags in local cache."""
        return self.cache.get_all_tags()
