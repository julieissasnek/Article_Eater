
import json
import glob
import os
import sys
from pathlib import Path

# Ensure src is in path
sys.path.append(os.getcwd())

from src.services.web_persistence import WebPersistenceService
from src.services.web_of_belief import Belief, EpistemicLevel, BeliefStatus, Credence
from src.models.theory_models import Theory, TheoryLevel, generate_theory_id
from src.services.db_locator import get_web_db

def seed_missing_theories():
    """
    Scan all active templates for framework_ids and create missing Theory beliefs.
    """
    print("Initializing Web Persistence...")
    db_path = str(get_web_db())  # Centralized: was hardcoded
    service = WebPersistenceService(db_path=db_path)
    web_id = service.get_master_web_id()
    if not web_id:
        print("Master web not found. Creating default.")
        web = service.create_web("Master Web", "Accumulated Knowledge")
        web_id = web.web_id
    else:
        print(f"Using Master Web: {web_id}")

    # Load existing theories
    beliefs = service.get_beliefs_for_web(web_id)
    valid_theory_ids = set()
    for b in beliefs:
        if b.level == EpistemicLevel.THEORETICAL:
            valid_theory_ids.add(b.belief_id)

    print(f"Found {len(valid_theory_ids)} existing theories.")

    # Scan templates
    template_dir = Path("data/templates")
    json_files = list(template_dir.glob("*.json"))
    
    missing_frameworks = set()

    print(f"Scanning {len(json_files)} templates...")
    for json_file in json_files:
        try:
            data = json.loads(json_file.read_text(encoding='utf-8'))
        except Exception:  
            continue
            
        if data.get("dedup_status") != "active":
            continue
            
        frameworks = data.get("framework_ids", [])
        for fid in frameworks:
            tid = f"theory:{fid}"
            # Check if fid is already a full ID (rare but possible)
            if fid.startswith("theory:"):
                tid = fid
                
            if tid not in valid_theory_ids:
                missing_frameworks.add(fid)

    print(f"Found {len(missing_frameworks)} unique missing frameworks.")
    
    if not missing_frameworks:
        print("No missing theories found. Exiting.")
        return

    # Create stubs
    web, _ = service.load_web(web_id)
    if not web:
        print(f"Error: Could not load web {web_id}")
        return
        
    count = 0
    for fid in sorted(missing_frameworks):
        tid = f"theory:{fid}"
        if fid.startswith("theory:"):
            tid = fid
            fid = fid.replace("theory:", "")
            
        name = fid.replace("_", " ").title()
        print(f"Creating stub theory: {tid} ({name})")
        
        # Create Theory object (optional, but good for metadata)
        # We store it primarily as a Belief in the Web
        
        belief = Belief(
            belief_id=tid,
            content=f"Stub for framework: {name}",
            level=EpistemicLevel.THEORETICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.5, 0.5), # Neutral
            theory_id=tid, # It is a theory
            domain="environmental_psychology" # Default
        )
        # Add tags
        belief.tags.append("stub")
        belief.tags.append("auto_generated")
        
        web.add_belief(belief)
        count += 1
        
    print(f"Saving {count} new theories to Web...")
    service.save_web(web, web_id)
    print("Done.")

if __name__ == "__main__":
    seed_missing_theories()
