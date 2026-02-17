
import pytest
import json
import glob
import os
import sys
from pathlib import Path

# Ensure src is in path
sys.path.append(os.getcwd())

from src.services.web_persistence import WebPersistenceService
from src.services.web_of_belief import EpistemicLevel

class TestTemplateTheoryDependencies:
    """
    Task 11.27: Verify that every active template correctly references 
    a Theory ID (Tier 1) that actually exists in the Web of Belief.
    """
    
    @classmethod
    def setup_class(cls):
        # 1. Initialize Web Persistence
        db_path = "data/web_persistence.db"
        if not os.path.exists(db_path):
             # Fallback if running from root
             if os.path.exists("web_persistence.db"):
                 db_path = "web_persistence.db"
        
        cls.service = WebPersistenceService(db_path=db_path)
        cls.web_id = cls.service.get_master_web_id()
        if not cls.web_id:
             cls.web_id = "master:web:accumulated"
             
        # 2. Load Valid Theory IDs from Web
        # We look for beliefs with level=THEORETICAL
        beliefs = cls.service.get_beliefs_for_web(cls.web_id)
        
        cls.valid_theory_ids = set()
        cls.theory_id_map = {} # mapping raw -> full for debugging
        
        print(f"\n[DEBUG] Loading theories from Web {cls.web_id}...")
        for b in beliefs:
            if b.level == EpistemicLevel.THEORETICAL:
                cls.valid_theory_ids.add(b.belief_id)
                # Also index simpler forms if needed, but let's stick to strict ID first
                print(f"  - Found Theory: {b.belief_id}")
                
        print(f"[DEBUG] Total Valid Theories: {len(cls.valid_theory_ids)}")

    def test_active_templates_map_to_existing_theories(self):
        """
        Walk all active templates and verify framework_ids match valid theories.
        """
        template_dir = Path("data/templates")
        json_files = list(template_dir.glob("*.json"))
        
        assert len(json_files) > 0, "No template files found in data/templates"
        
        missing_dependencies = []
        checked_count = 0
        
        for json_file in json_files:
            try:
                data = json.loads(json_file.read_text(encoding='utf-8'))
            except Exception as e:
                print(f"[WARN] Failed to read {json_file}: {e}")
                continue
                
            # Filter for ACTIVE templates
            if data.get("dedup_status") != "active":
                continue
                
            checked_count += 1
            template_id = data.get("template_id", json_file.stem)
            display_id = data.get("display_id", "UNKNOWN")
            
            # Check framework_ids
            frameworks = data.get("framework_ids", [])
            
            if not frameworks:
                # Is it acceptable for an active template to have NO framework?
                # Probably should warn, but technically not a "broken reference".
                # For this test, we verify references that DO exist.
                # print(f"[INFO] Template {display_id} has no framework_ids")
                pass
                
            for fid in frameworks:
                # Framework IDs in JSON often omit "theory:" prefix
                # e.g. "embodied_cognition" -> "theory:embodied_cognition"
                
                # Check exact match
                if fid in self.valid_theory_ids:
                    continue
                    
                # Check with prefix
                prefixed = f"theory:{fid}"
                if prefixed in self.valid_theory_ids:
                    continue
                    
                # Reference broken
                missing_dependencies.append({
                    "template": display_id,
                    "file": json_file.name,
                    "invalid_ref": fid,
                    "tried": [fid, prefixed]
                })

        # Report failures
        if missing_dependencies:
            print("\n[ERROR] Found Orphaned Theory Dependencies:")
            unique_missing = set()
            for miss in missing_dependencies:
                unique_missing.add(miss['invalid_ref'])
                # print(f"  - {miss['template']} ({miss['file']}) refs '{miss['invalid_ref']}' -> Not found in Web")
            
            print(f"Unique missing theories ({len(unique_missing)}):")
            for ref in sorted(unique_missing):
                print(f"  - {ref}")

            pytest.fail(f"Found {len(missing_dependencies)} templates with invalid theory references. {len(unique_missing)} unique missing theories.")
            
        print(f"\n[SUCCESS] Verified {checked_count} active templates. All theory references valid.")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
