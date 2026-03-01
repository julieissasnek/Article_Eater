"""
Environment Image Database — Sprint S-6
==========================================

Manages the collection of environment/architectural images linked to
CVA annotations. Provides queries like:
- "Show me images of high-prospect spaces"
- "Find stimuli used in biophilia studies"
- "Match this space description to known images"

Uses SQLite for fast local querying + integrates with image_pool_manager
and CVA annotation service.

Usage:
    from src.services.environment_image_db import EnvironmentImageDB
    
    db = EnvironmentImageDB()
    db.ingest_extraction_images("data/extracted_images/10.1016_j.buildenv.2024.111798/")
    results = db.search(constraints={"C_BIOPHILIA": 0.5}, modality="photograph")
"""

import json
import logging
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent
DB_PATH = PROJECT_ROOT / "data" / "environment_images.db"
EXTRACTED_DIR = PROJECT_ROOT / "data" / "extracted_images"
REPORT_DIR = PROJECT_ROOT / "data" / "image_extraction_reports"


class EnvironmentImageDB:
    """Database of environment/architectural images with CVA metadata."""
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Create database schema."""
        conn = sqlite3.connect(str(self.db_path))
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS images (
                image_id TEXT PRIMARY KEY,
                doi TEXT,
                filename TEXT NOT NULL,
                filepath TEXT,
                classification TEXT,
                caption TEXT,
                page_num INTEGER,
                width INTEGER,
                height INTEGER,
                size_bytes INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS image_cva_tags (
                image_id TEXT NOT NULL,
                tag_type TEXT NOT NULL,
                tag_name TEXT NOT NULL,
                score REAL DEFAULT 0.5,
                source TEXT DEFAULT 'auto',
                FOREIGN KEY (image_id) REFERENCES images(image_id),
                PRIMARY KEY (image_id, tag_type, tag_name)
            );
            
            CREATE TABLE IF NOT EXISTS image_finding_links (
                image_id TEXT NOT NULL,
                doi TEXT NOT NULL,
                finding_index INTEGER,
                figure_ref TEXT,
                context TEXT,
                FOREIGN KEY (image_id) REFERENCES images(image_id)
            );
            
            CREATE INDEX IF NOT EXISTS idx_images_doi ON images(doi);
            CREATE INDEX IF NOT EXISTS idx_images_class ON images(classification);
            CREATE INDEX IF NOT EXISTS idx_tags_name ON image_cva_tags(tag_name);
            CREATE INDEX IF NOT EXISTS idx_tags_type ON image_cva_tags(tag_type);
            CREATE INDEX IF NOT EXISTS idx_links_doi ON image_finding_links(doi);
        """)
        conn.commit()
        conn.close()
    
    # ----- Ingestion -----
    
    def ingest_from_manifest(self, manifest_path: Path = None) -> Dict[str, int]:
        """Ingest images from the batch extraction manifest.
        
        Reads the latest extraction_manifest_*.json and imports all images.
        """
        if manifest_path is None:
            manifests = sorted(REPORT_DIR.glob("extraction_manifest_*.json"))
            if not manifests:
                return {"error": "No manifests found"}
            manifest_path = manifests[-1]
        
        with open(manifest_path) as f:
            manifest = json.load(f)
        
        conn = sqlite3.connect(str(self.db_path))
        stats = {"images_ingested": 0, "links_ingested": 0, "tags_added": 0}
        
        # Ingest images
        for img in manifest.get("images", []):
            image_id = img.get("filename", "").replace(".", "_")
            try:
                conn.execute("""
                    INSERT OR REPLACE INTO images 
                    (image_id, doi, filename, filepath, classification, caption, 
                     page_num, width, height, size_bytes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    image_id, img.get("doi"), img.get("filename"),
                    img.get("path"), img.get("classification"),
                    img.get("caption"), img.get("page"),
                    img.get("width"), img.get("height"), img.get("size_bytes"),
                ))
                stats["images_ingested"] += 1
                
                # Auto-tag based on classification and caption
                tags = self._auto_tag_image(img)
                for tag_type, tag_name, score in tags:
                    conn.execute("""
                        INSERT OR REPLACE INTO image_cva_tags 
                        (image_id, tag_type, tag_name, score, source)
                        VALUES (?, ?, ?, ?, 'auto')
                    """, (image_id, tag_type, tag_name, score))
                    stats["tags_added"] += 1
                    
            except Exception as e:
                logger.warning(f"Failed to ingest {image_id}: {e}")
        
        # Ingest finding links
        for link in manifest.get("figure_finding_links", []):
            try:
                image_id = link.get("image", "").replace(".", "_")
                conn.execute("""
                    INSERT INTO image_finding_links
                    (image_id, doi, finding_index, figure_ref, context)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    image_id,
                    link.get("doi", ""),
                    link.get("finding_index"),
                    link.get("figure_ref"),
                    link.get("finding_text", "")[:300],
                ))
                stats["links_ingested"] += 1
            except Exception:
                pass
        
        conn.commit()
        conn.close()
        return stats
    
    def _auto_tag_image(self, img: dict) -> List[tuple]:
        """Generate CVA tags for an image based on classification and caption."""
        tags = []
        caption = (img.get("caption") or "").lower()
        classification = img.get("classification", "")
        
        # Classification → base tag
        if classification == "stimulus":
            tags.append(("type", "stimulus", 0.8))
        elif classification == "photograph":
            tags.append(("type", "photograph", 0.7))
        elif classification == "floor_plan":
            tags.append(("type", "floor_plan", 0.9))
        elif classification == "chart":
            tags.append(("type", "chart", 0.9))
        
        # Caption keywords → CVA constraint tags
        constraint_keywords = {
            "C_BIOPHILIA": ["nature", "green", "plant", "biophil", "tree", "garden"],
            "C_PROSPECT_REFUGE": ["open", "enclos", "vista", "shelter", "refuge"],
            "C_COMPLEXITY": ["complex", "fractal", "detail", "pattern"],
            "C_SAFETY": ["safe", "danger", "dark", "crime"],
            "C_COHERENCE": ["order", "symmetric", "harmon"],
            "C_BEAUTY": ["beaut", "aesthet", "attracat"],
        }
        
        for constraint, keywords in constraint_keywords.items():
            matches = sum(1 for kw in keywords if kw in caption)
            if matches:
                tags.append(("constraint", constraint, min(0.9, matches * 0.3)))
        
        return tags
    
    # ----- Search -----
    
    def search(self, 
               constraints: Dict[str, float] = None,
               valuations: Dict[str, float] = None,
               classification: str = None,
               doi: str = None,
               limit: int = 20) -> List[Dict[str, Any]]:
        """Search for images matching CVA criteria.
        
        Args:
            constraints: CVA constraint requirements (e.g. {"C_BIOPHILIA": 0.5})
            valuations: CVA valuation requirements
            classification: Image type filter (stimulus/photograph/chart/etc.)
            doi: Filter by source DOI
            limit: Max results
        """
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        
        query = "SELECT DISTINCT i.* FROM images i"
        conditions = []
        params = []
        
        # Join with tags if constraint/valuation filter
        if constraints:
            for i, (cname, min_score) in enumerate(constraints.items()):
                alias = f"ct{i}"
                query += f" JOIN image_cva_tags {alias} ON i.image_id = {alias}.image_id"
                conditions.append(f"{alias}.tag_name = ? AND {alias}.score >= ?")
                params.extend([cname, min_score])
        
        if classification:
            conditions.append("i.classification = ?")
            params.append(classification)
        
        if doi:
            conditions.append("i.doi = ?")
            params.append(doi)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += f" LIMIT {limit}"
        
        rows = conn.execute(query, params).fetchall()
        results = []
        for row in rows:
            result = dict(row)
            # Fetch tags
            tags = conn.execute(
                "SELECT tag_type, tag_name, score FROM image_cva_tags WHERE image_id = ?",
                (row["image_id"],)
            ).fetchall()
            result["cva_tags"] = [dict(t) for t in tags]
            results.append(result)
        
        conn.close()
        return results
    
    def find_similar(self, image_id: str, limit: int = 10) -> List[Dict]:
        """Find images with similar CVA tags."""
        conn = sqlite3.connect(str(self.db_path))
        
        # Get tags for reference image
        ref_tags = conn.execute(
            "SELECT tag_name, score FROM image_cva_tags WHERE image_id = ?",
            (image_id,)
        ).fetchall()
        
        if not ref_tags:
            conn.close()
            return []
        
        # Find images sharing tags, ordered by overlap
        tag_names = [t[0] for t in ref_tags]
        placeholders = ",".join("?" * len(tag_names))
        
        rows = conn.execute(f"""
            SELECT image_id, COUNT(*) as overlap, SUM(score) as total_score
            FROM image_cva_tags
            WHERE tag_name IN ({placeholders}) AND image_id != ?
            GROUP BY image_id
            ORDER BY overlap DESC, total_score DESC
            LIMIT ?
        """, tag_names + [image_id, limit]).fetchall()
        
        conn.close()
        return [{"image_id": r[0], "overlap": r[1], "total_score": r[2]} for r in rows]
    
    # ----- Analytics -----
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        conn = sqlite3.connect(str(self.db_path))
        
        total = conn.execute("SELECT COUNT(*) FROM images").fetchone()[0]
        by_class = dict(conn.execute(
            "SELECT classification, COUNT(*) FROM images GROUP BY classification"
        ).fetchall())
        by_tag = dict(conn.execute(
            "SELECT tag_name, COUNT(*) FROM image_cva_tags GROUP BY tag_name ORDER BY COUNT(*) DESC LIMIT 10"
        ).fetchall())
        links = conn.execute("SELECT COUNT(*) FROM image_finding_links").fetchone()[0]
        dois = conn.execute("SELECT COUNT(DISTINCT doi) FROM images").fetchone()[0]
        
        conn.close()
        return {
            "total_images": total,
            "unique_dois": dois,
            "by_classification": by_class,
            "top_tags": by_tag,
            "finding_links": links,
        }
