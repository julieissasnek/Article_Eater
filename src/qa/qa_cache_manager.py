import json
import os
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class CacheEntry:
    molecule_id: str
    l1_summary: str
    l2_summary: str
    l3_summary: str
    dependent_templates: List[str]
    last_computed: str
    kb_hash_at_computation: str
    status: str = "FRESH" # "FRESH", "STALE", "RECOMPUTING"

class QACacheManager:
    """
    Manages pre-computed Progressive Disclosure summaries for Molecules.
    Monitors the underlying Web of Belief (Templates/BN) for changes and
    flags specific QA caches as STALE when new PDFs alter their dependencies.
    """
    
    def __init__(self, cache_dir: str = "data/qa_cache", template_dir: str = "data/templates"):
        self.cache_dir = Path(cache_dir)
        self.template_dir = Path(template_dir)
        self.index_file = self.cache_dir / "cache_index.json"
        
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._cache_index: Dict[str, dict] = self._load_index()

    def _load_index(self) -> Dict[str, dict]:
        if self.index_file.exists():
            with open(self.index_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_index(self):
        with open(self.index_file, 'w') as f:
            json.dump(self._cache_index, f, indent=2)

    def _compute_dependency_hash(self, template_ids: List[str]) -> str:
        """
        Computes a composite hash of all templates that a Molecule depends on.
        If a new PDF extraction updates one of these templates, the hash changes.
        """
        hasher = hashlib.md5()
        # Sort to ensure deterministic hashing
        for tid in sorted(template_ids):
            t_path = self.template_dir / f"{tid}.json"
            if t_path.exists():
                with open(t_path, 'rb') as f:
                    hasher.update(f.read())
            else:
                hasher.update(tid.encode('utf-8')) # Fallback if missing
        return hasher.hexdigest()

    def get_summary(self, molecule_id: str) -> Optional[Dict]:
        """Returns the cached summary if it exists."""
        entry_path = self.cache_dir / f"{molecule_id}_QA.json"
        if entry_path.exists():
            with open(entry_path, 'r') as f:
                return json.load(f)
        return None

    def save_summary(self, cache_entry: CacheEntry):
        """Saves a newly computed QA summary and updates the index."""
        # Save payload
        entry_path = self.cache_dir / f"{cache_entry.molecule_id}_QA.json"
        with open(entry_path, 'w') as f:
            json.dump(asdict(cache_entry), f, indent=2)
        
        # Update index
        self._cache_index[cache_entry.molecule_id] = {
            "last_computed": cache_entry.last_computed,
            "hash": cache_entry.kb_hash_at_computation,
            "status": "FRESH"
        }
        self._save_index()

    def check_for_stale_caches(self, molecule_registry: Dict[str, dict]) -> List[str]:
        """
        Runs exactly what you asked for: checks if the Web of Belief/Templates
        have been significantly modified since the last pre-computation.
        Returns a list of molecule_ids that are STALE and need recomputation.
        """
        stale_molecules = []
        
        for mol_id, mol_data in molecule_registry.items():
            if mol_id not in self._cache_index:
                stale_molecules.append(mol_id)
                continue
                
            idx_entry = self._cache_index[mol_id]
            current_hash = self._compute_dependency_hash(mol_data.get("constituent_templates", []))
            
            if current_hash != idx_entry["hash"]:
                # The underlying KB has changed! Alert the QA system.
                idx_entry["status"] = "STALE"
                stale_molecules.append(mol_id)
                print(f"[ALERT] KB Updates detected for Molecule {mol_id}. Cache is now STALE.")
                
        self._save_index()
        return stale_molecules

    def notify_qa_system(self, stale_molecules: List[str]):
        """
        Placeholder for the alerting process that would hook into an event queue
        or trigger the LLM re-computation pipeline for the affected molecules.
        """
        if not stale_molecules:
            return
            
        print(f"[{datetime.now().isoformat()}] QA Alert: {len(stale_molecules)} molecules require QA reconstruction due to KB drift.")
        for mol in stale_molecules:
            print(f" -> Re-queueing QA Generation for: {mol}")
