#!/usr/bin/env python3
import sys
import logging
from pathlib import Path
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.services.web_persistence import WebPersistenceService
from src.services.extraction_to_web import (
    infer_theory_relevance_enhanced,
    infer_epistemic_level,
    THEORY_THRESHOLD,
    _extract_domain
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main():
    db_path = PROJECT_ROOT / "data" / "web_persistence.db"
    service = WebPersistenceService(str(db_path))
    master_id = service.get_master_web_id()
    if not master_id:
        logger.error("No master web found.")
        return
        
    web, _ = service.load_web(master_id)
    if not web:
        logger.error("Failed to load master web.")
        return
        
    updates = 0
    theory_matched = 0
    stubs = 0
    
    for belief_id, belief in web.beliefs.items():
        # Get claim_type from tags if available
        claim_type = "unknown"
        for tag in belief.tags:
            if tag.startswith("claim_type:"):
                claim_type = tag.replace("claim_type:", "")
                break
                
        # Strip env. and out. prefixes which were added to the DB but not expected by extraction_to_web
        env_val = belief.environment_id[4:] if belief.environment_id and belief.environment_id.startswith("env.") else belief.environment_id
        out_val = belief.outcome_id[4:] if belief.outcome_id and belief.outcome_id.startswith("out.") else belief.outcome_id

        # Mock claim dictionary for the mapping functions
        claim = {
            "claim_id": belief.belief_id,
            "statement": belief.content,
            "claim_type": claim_type,
            "constructs": {
                "environment_factors": [{"id": env_val}] if env_val else [],
                "outcomes": [{"id": out_val}] if out_val else [],
            }
        }
        
        # 1. Map Epistemic Level
        new_level = infer_epistemic_level(claim_type)
        if belief.level != new_level:
            belief.level = new_level
            updates += 1
            
        # 2. Map Theory Relevance
        theory_result = infer_theory_relevance_enhanced(claim, None, use_embeddings=False) 
        # Using legacy/keyword/outcome matching to avoid slow embedding over 12k items, matching the original requirement
        
        theory_inferences = theory_result.relevance
        best_theory = None
        best_score = 0.0
        
        if theory_inferences:
            sorted_theories = sorted(theory_inferences.items(), key=lambda x: x[1], reverse=True)
            candidate, score = sorted_theories[0]
            if score >= THEORY_THRESHOLD:
                best_theory = candidate
                best_score = score
                
        if best_theory and belief.theory_id != best_theory:
            belief.theory_id = best_theory
            updates += 1
            theory_matched += 1
        elif not best_theory and not belief.theory_id:
            stubs += 1

        # 3. Domain mapped from outcome
        domain = _extract_domain(claim["constructs"])
        if domain and belief.domain != domain:
            belief.domain = domain
            updates += 1
            
    if updates > 0:
        logger.info(f"Made {updates} updates across 12k beliefs. Theories matched: {theory_matched}, Stubs remaining: {stubs}. Saving...")
        service.save_web(web, master_id)
        logger.info("Saved web_persistence.db successfully.")
    else:
        logger.info("No updates were necessary.")

if __name__ == "__main__":
    main()
