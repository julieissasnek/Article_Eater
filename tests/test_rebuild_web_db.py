#!/usr/bin/env python3
"""
Test Rebuild Web DB with Synthetic Data
=======================================

Verifies that scripts/rebuild_web_db.py correctly digests
tests/fixtures/synthetic_claims.jsonl and builds a valid web.
"""

import os
import sys
import unittest
import sqlite3
import shutil
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import logic from the script directly if possible, or run it as subprocess
# Importing is better for coverage and debugging
from scripts.rebuild_web_db import load_claims, convert_claim_to_belief, MASTER_WEB_ID
from src.services.web_persistence import WebPersistenceService
from src.services.web_of_belief import WebOfBelief, Belief

TEST_DB_PATH = PROJECT_ROOT / "tests" / "fixtures" / "test_web.db"
SYNTHETIC_DATA_PATH = PROJECT_ROOT / "tests" / "fixtures" / "synthetic_claims.jsonl"

class TestRebuildWebDB(unittest.TestCase):

    def setUp(self):
        # Clean up previous test runs
        if TEST_DB_PATH.exists():
            TEST_DB_PATH.unlink()
            
    def tearDown(self):
        # Clean up after test
        if TEST_DB_PATH.exists():
            TEST_DB_PATH.unlink()

    def test_load_claims(self):
        claims = load_claims(SYNTHETIC_DATA_PATH)
        self.assertEqual(len(claims), 10)
        self.assertEqual(claims[0]['claim_id'], 'synth_001')

    def test_conversion_logic(self):
        claims = load_claims(SYNTHETIC_DATA_PATH)
        
        # Test 1: Standard Claim
        c1 = claims[0]
        b1 = convert_claim_to_belief(c1)
        self.assertIsInstance(b1, Belief)
        self.assertIn("natural light", b1.content)
        self.assertIn("productivity", b1.content)
        self.assertIn("positive", b1.content)
        self.assertAlmostEqual(b1.credence.value, 0.6)

        # Test 2: Correlation with 'r'
        c3 = claims[2]
        b3 = convert_claim_to_belief(c3)
        self.assertIn("r=-0.4", b3.content)
        
        # Test 3: Null finding
        c6 = claims[5]
        b6 = convert_claim_to_belief(c6)
        self.assertIn("null finding", b6.content)

    def test_full_rebuild_process(self):
        """Simulate the main execution flow."""
        claims = load_claims(SYNTHETIC_DATA_PATH)
        web = WebOfBelief()
        
        for claim in claims:
            belief = convert_claim_to_belief(claim)
            web.add_belief(belief)
            
        self.assertEqual(len(web.beliefs), 10)
        
        # Persist
        persistence = WebPersistenceService(str(TEST_DB_PATH))
        persistence.create_or_get_master_web() # Fixed signature
        persistence.save_web(web, MASTER_WEB_ID)
        
        # Verify
        reloaded_web, _ = persistence.load_web(MASTER_WEB_ID)
        self.assertIsNotNone(reloaded_web)
        self.assertEqual(len(reloaded_web.beliefs), 10)
        
        # Check specific belief present
        # ID sanitization: synth_001 -> b_synth_001
        self.assertIn("b_synth_001", reloaded_web.beliefs)

if __name__ == '__main__':
    unittest.main()
