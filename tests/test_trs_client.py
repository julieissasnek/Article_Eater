"""Tests for Sprint S-5: TRS Client with Fallback."""

import json
import sys
import sqlite3
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestLocalTaxonomyCache(unittest.TestCase):
    """Test the local taxonomy cache works independently."""
    
    def setUp(self):
        """Create cache with temp DB."""
        from src.services.trs_client import LocalTaxonomyCache
        self.test_db = Path("/tmp/test_trs_cache.db")
        if self.test_db.exists():
            self.test_db.unlink()
        self.cache = LocalTaxonomyCache(self.test_db)
    
    def tearDown(self):
        if self.test_db.exists():
            self.test_db.unlink()
    
    def test_cache_seeds_automatically(self):
        """Cache should seed with built-in tags on first init."""
        stats = self.cache.get_stats()
        self.assertGreater(stats["total_tags"], 20)
        self.assertEqual(stats["by_source"].get("seed", 0), stats["total_tags"])
    
    def test_get_tags_for_features(self):
        """Feature lookup returns matching tags."""
        tags = self.cache.get_tags_for_features({"visual_complexity": 0.8})
        self.assertGreater(len(tags), 0)
        self.assertTrue(any(t.tag_id == "complexity.visual" for t in tags))
    
    def test_get_tags_no_match(self):
        """Unknown features return empty list."""
        tags = self.cache.get_tags_for_features({"unknown_feature": 0.5})
        self.assertEqual(len(tags), 0)
    
    def test_get_all_tags(self):
        """Get all cached tags."""
        tags = self.cache.get_all_tags()
        self.assertGreater(len(tags), 20)
        categories = set(t.category for t in tags)
        self.assertIn("spatial", categories)
        self.assertIn("light", categories)
        self.assertIn("nature", categories)
    
    def test_upsert_tags(self):
        """Can insert new tags from TRS sync."""
        new_tags = [
            {"tag_id": "custom.test1", "category": "custom", "label": "Test Tag"},
            {"tag_id": "custom.test2", "category": "custom", "label": "Test Tag 2"},
        ]
        count = self.cache.upsert_tags(new_tags, source="trs")
        self.assertEqual(count, 2)
        
        stats = self.cache.get_stats()
        self.assertEqual(stats["by_source"].get("trs", 0), 2)
    
    def test_upsert_idempotent(self):
        """Upserting same tags twice doesn't create duplicates."""
        tag = [{"tag_id": "custom.idem", "category": "c", "label": "Idempotent"}]
        self.cache.upsert_tags(tag)
        self.cache.upsert_tags(tag)
        
        stats = self.cache.get_stats()
        # Count should include seed + 1 (not 2)
        all_tags = self.cache.get_all_tags()
        idem_count = sum(1 for t in all_tags if t.tag_id == "custom.idem")
        self.assertEqual(idem_count, 1)


class TestTRSHealthChecker(unittest.TestCase):
    """Test health checking with mock network."""
    
    def test_health_check_no_server(self):
        """Health check returns unhealthy when no server."""
        from src.services.trs_client import TRSHealthChecker
        checker = TRSHealthChecker("http://localhost:99999")
        status = checker.check(force=True)
        self.assertFalse(status.is_healthy)
        self.assertEqual(status.mode, "local")
    
    def test_health_check_caching(self):
        """Repeated checks use cached result within interval."""
        from src.services.trs_client import TRSHealthChecker
        checker = TRSHealthChecker("http://localhost:99999")
        s1 = checker.check(force=True)
        s2 = checker.check()  # Should use cached
        self.assertEqual(s1.last_checked, s2.last_checked)


class TestTRSClient(unittest.TestCase):
    """Test the unified TRS client."""
    
    def setUp(self):
        from src.services.trs_client import TRSClient
        self.test_db = Path("/tmp/test_trs_client.db")
        if self.test_db.exists():
            self.test_db.unlink()
        self.client = TRSClient(
            base_url="http://localhost:99999",  # Intentionally unavailable
            cache_db=self.test_db,
        )
    
    def tearDown(self):
        if self.test_db.exists():
            self.test_db.unlink()
    
    def test_fallback_to_local(self):
        """Client uses local cache when TRS is unavailable."""
        tags = self.client.get_tags("test.jpg", {"visual_complexity": 0.8})
        self.assertGreater(len(tags), 0)
        self.assertTrue(all(t.source == "local" for t in tags))
    
    def test_health_status(self):
        """Health status includes TRS and cache info."""
        status = self.client.health_status()
        self.assertIn("trs", status)
        self.assertIn("cache", status)
        self.assertIn("client_stats", status)
        self.assertFalse(status["trs"]["is_healthy"])
    
    def test_get_all_cached(self):
        """Can retrieve all cached tags."""
        tags = self.client.get_all_cached_tags()
        self.assertGreater(len(tags), 20)
    
    def test_sync_fails_gracefully(self):
        """Sync returns error info when TRS unavailable."""
        result = self.client.sync_from_trs()
        self.assertIn(result["status"], ["skipped", "error"])
    
    def test_tag_structure(self):
        """Tags have expected fields."""
        tags = self.client.get_tags("test.jpg", {"green_view_index": 0.5})
        for tag in tags:
            self.assertTrue(hasattr(tag, "tag_id"))
            self.assertTrue(hasattr(tag, "category"))
            self.assertTrue(hasattr(tag, "confidence"))
            self.assertTrue(hasattr(tag, "source"))
            d = tag.to_dict()
            self.assertIn("tag_id", d)


if __name__ == "__main__":
    unittest.main()
