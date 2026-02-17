
import pytest
import sys
import os

# Ensure src is in path
sys.path.append(os.getcwd())

from src.services.web_persistence import WebPersistenceService
from src.services.web_of_belief import ConstraintType

class TestWebOfBeliefIntegration:
    """
    Integration tests for the Web of Belief system (Task 11.23).
    Verifies that theory links (constraints) are correctly loaded and mapped.
    """
    
    @classmethod
    def setup_class(cls):
        db_path = "data/web_persistence.db"
        if not os.path.exists(db_path):
             # Fallback if running from root
             if os.path.exists("web_persistence.db"):
                 db_path = "web_persistence.db"
        
        cls.service = WebPersistenceService(db_path=db_path)
        cls.web_id = cls.service.get_master_web_id()
        
        # Explicit fallback to the known ID from sqlite analysis
        if not cls.web_id:
             cls.web_id = "master:web:accumulated"
             
        print(f"\n[DEBUG] Using Web ID: {cls.web_id}")
        
        # Verify it exists
        with cls.service._get_connection() as conn:
            row = conn.execute("SELECT count(*) FROM constraints WHERE web_id=?", (cls.web_id,)).fetchone()
            print(f"[DEBUG] Constraints for this Web ID in DB: {row[0]}")

    def test_staging_links_loaded(self):
        """
        Verify that the expected number of Tier 2 theory links are loaded.
        """
        assert self.web_id, "No master web found in DB"
        
        constraints = self.service.get_constraints_for_web(self.web_id)
        
        # Filter for tier2_theory_link
        # Note: constraint_type might be an Enum or converted string
        links = []
        for c in constraints:
            c_type = str(c.constraint_type)
            # Checked mapped type (EPISTEMIC_DERIVATION) or legacy for robustness
            if "tier2" in c_type.lower() or "theory_link" in c_type.lower() or "epistemic_derivation" in c_type.lower():
                links.append(c)
                
        count = len(links)
        print(f"\nLoaded {count} theory links (from total {len(constraints)} constraints).")
        
        # Expectation: ~1361 links were loaded in staging
        assert count >= 1300, f"Expected > 1300 theory links, got {count}"

    def test_staging_links_have_theory_ids(self):
        """
        Verify that loaded links have valid theory_id attributes 
        mapping to the core theories (ART, Biophilia, SRT).
        """
        if not self.web_id:
            pytest.skip("No web found")

        constraints = self.service.get_constraints_for_web(self.web_id)
        links = [c for c in constraints if "tier2" in str(c.constraint_type).lower() or "epistemic_derivation" in str(c.constraint_type).lower()]
        
        # In the staging loader, theory_id was likely stored in a specific way.
        # The Constraint object might not have 'theory_id' directly unless it was monkey-patched 
        # or stored in 'provenance'/'warrant_type'.
        # However, the previous verification test checked `getattr(l, 'theory_id', None)`.
        # Let's check attributes and also target_id (which might be 'theory:art')
        
        theory_targets = set()
        has_theory_attr = False
        
        for link in links:
            if hasattr(link, 'theory_id'):
                theory_targets.add(link.theory_id)
                has_theory_attr = True
            
            # Also check target_id convention
            if str(link.target_id).startswith("theory:"):
                theory_targets.add(link.target_id)
        
        print(f"\nFound Theory Identifiers: {theory_targets}")
        
        # We need to find ART and Biophilia
        found_art = any("art" in t.lower() for t in theory_targets)
        found_bio = any("biophilia" in t.lower() for t in theory_targets)
        
        assert found_art, "ART constraints missing (no theory:art target or theory_id)"
        assert found_bio, "Biophilia constraints missing"

    def test_constraint_integrity(self):
        """
        Spot check that source nodes for constraints actually exist as Beliefs.
        """
        if not self.web_id:
            pytest.skip("No web found")
            
        constraints = self.service.get_constraints_for_web(self.web_id)
        links = [c for c in constraints if "tier2" in str(c.constraint_type).lower() or "epistemic_derivation" in str(c.constraint_type).lower()]
        
        beliefs = {b.belief_id: b for b in self.service.get_beliefs_for_web(self.web_id)}
        
        # Check a sample
        sample = links[:20] if len(links) > 20 else links
        missing_sources = []
        
        for link in sample:
            if link.source_id not in beliefs:
                 missing_sources.append(link.source_id)
        
        assert not missing_sources, f"Constraints typically reference existing beliefs. Missing sources: {missing_sources}"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
