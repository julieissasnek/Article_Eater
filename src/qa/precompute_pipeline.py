import argparse
import json
import logging
import os
from pathlib import Path
from typing import Dict, List
import time

# Use the existing LLM infrastructure from extraction
from google import generativeai as genai

from .molecules.schema import Molecule, MoleculeComponent
from .qa_cache_manager import QACacheManager, CacheEntry

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MolecularQAPrecomputer:
    def __init__(self, molecule_dir: str = "data/molecules", cache_dir: str = "data/qa_cache"):
        self.molecule_dir = Path(molecule_dir)
        self.cache_mgr = QACacheManager(cache_dir=cache_dir)
        
        # Pull API key securely via environment (like extraction module)
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY environment variable required")
            
        genai.configure(api_key=api_key)
        self.model_name = "gemini-2.5-flash"  # Defaulting to fast, high-context model
        self.model = genai.GenerativeModel(self.model_name)

        self.molecules: Dict[str, Molecule] = self._load_molecules()

    def _load_molecules(self) -> Dict[str, Molecule]:
        molecules = {}
        if not self.molecule_dir.exists():
            return molecules
            
        for file in self.molecule_dir.glob("*.json"):
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                    mol = Molecule.from_dict(data)
                    molecules[mol.molecule_id] = mol
            except Exception as e:
                logger.error(f"Error loading {file}: {e}")
        return molecules

    def _generate_prompts(self, molecule: Molecule) -> str:
        """
        Creates the prompt to ask the LLM to write L1, L2, and L3 
        progressive disclosure summaries based on the molecule definition.
        """
        # In a full system, we would inject the *actual text* of the constituent_templates
        # here to ground the LLM's response in the Web of Belief exactly.
        # For Phase X.1, we rely on the formal definitions parsed in the molecule JSON.
        
        components_text = "\n".join([f"- {c.name}: {c.description}" for c in molecule.components])
        
        prompt = f"""
        You are an expert theoretical architect and environmental psychologist.
        
        Your task is to generate progressive disclosure summaries for the following theoretical construct:
        **{molecule.name} ({molecule.molecule_id})**
        
        Domain: {molecule.domain}
        Empirical Support Level: {molecule.empirical_support}
        
        Components:
        {components_text}
        
        Write three distinct summaries strictly adhering to the following formats:
        
        LEVEL 1 (Direct Answer): 1 or 2 sentences providing a direct definition and the main effect.
        
        LEVEL 2 (Contextualized): 1 paragraph (3-5 sentences) summarizing the effect, key mechanisms, and evidence quality.
        
        LEVEL 3 (Mechanistic): 3-5 paragraphs detailing exactly *how* the components work together to produce the effect. 
        Be sure to mention the specific components listed above.
        
        Output your response as a valid JSON object with keys "l1_summary", "l2_summary", "l3_summary".
        Do not include markdown codeblocks around the JSON.
        """
        return prompt

    def compute_all(self, force_recompute: bool = False):
        """
        Main loop to scan molecules, check the cache Tracker, and hit the LLM
        for any missing or STALE molecules.
        """
        logger.info(f"Checking cache manager for STALE molecules among {len(self.molecules)} loaded definitions...")
        
        # Determine what needs computation
        needs_compute = []
        for mol_id, mol in self.molecules.items():
            if force_recompute:
                needs_compute.append(mol)
                continue
                
            entry = self.cache_mgr.get_summary(mol_id)
            if entry is None or entry.get("status") == "STALE":
                needs_compute.append(mol)
        
        # Check Tracker invalidations
        mol_dicts = {k: v.to_dict() for k, v in self.molecules.items()}
        stale_ids = self.cache_mgr.check_for_stale_caches(mol_dicts)
        for s_id in stale_ids:
            if s_id in self.molecules and self.molecules[s_id] not in needs_compute:
                needs_compute.append(self.molecules[s_id])

        if not needs_compute:
            logger.info("All QA caches are FRESH. No computation needed.")
            return

        logger.info(f"Computing QA Summaries for {len(needs_compute)} molecules...")
        
        for idx, molecule in enumerate(needs_compute):
            logger.info(f"[{idx+1}/{len(needs_compute)}] Processing {molecule.name}...")
            prompt = self._generate_prompts(molecule)
            
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(temperature=0.2)
                )
                
                # Parse JSON output
                raw_text = response.text.strip()
                if raw_text.startswith("```json"):
                    raw_text = raw_text[7:-3]
                elif raw_text.startswith("```"):
                    raw_text = raw_text[3:-3]
                    
                result = json.loads(raw_text)
                
                # Construct Cache Entry
                from datetime import datetime
                entry = CacheEntry(
                    molecule_id=molecule.molecule_id,
                    l1_summary=result.get("l1_summary", ""),
                    l2_summary=result.get("l2_summary", ""),
                    l3_summary=result.get("l3_summary", ""),
                    dependent_templates=molecule.constituent_templates,
                    last_computed=datetime.now(datetime.UTC).isoformat(),
                    kb_hash_at_computation=self.cache_mgr._compute_dependency_hash(molecule.constituent_templates),
                    status="FRESH"
                )
                
                self.cache_mgr.save_summary(entry)
                logger.info(f"✓ Saved pre-computed summaries for {molecule.molecule_id}")
                
                # Rate limit safety
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Failed to generate summaries for {molecule.molecule_id}: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pre-compute QA Summaries for the Molecule Layer.")
    parser.add_argument("--force", action="store_true", help="Force recomputation of all molecules even if FRESH")
    args = parser.parse_args()
    
    precomputer = MolecularQAPrecomputer()
    precomputer.compute_all(force_recompute=args.force)

