import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from .molecules.schema import Molecule

@dataclass
class ClassifiedQuestion:
    raw_query: str
    target_type: str  # "molecule", "component", "template", "design_synthesis"
    target_id: Optional[str] = None
    target_component: Optional[str] = None
    requested_depth: int = 2  # L1 = 1, L2 = 2, L3 = 3

@dataclass
class QueryPlan:
    target_type: str
    molecule_id: Optional[str] = None
    component: Optional[str] = None
    molecules: List[str] = None
    depth: int = 2

class MoleculeAwareRouter:
    """
     Phase 3: Routes user queries to the appropriate Pre-Computed QA cache
    or falls back to live synthesis for complex design questions.
    """
    def __init__(self, molecule_dir: str = "data/molecules", cache_dir: str = "data/qa_cache"):
        self.molecule_dir = Path(molecule_dir)
        self.cache_dir = Path(cache_dir)
        self.molecule_registry: Dict[str, Molecule] = self._load_molecules()
        self.cache_index = self._load_cache_index()

    def _load_molecules(self) -> Dict[str, Molecule]:
        molecules = {}
        if self.molecule_dir.exists():
            for file in self.molecule_dir.glob("*.json"):
                try:
                    with open(file, 'r') as f:
                        data = json.load(f)
                        mol = Molecule.from_dict(data)
                        molecules[mol.molecule_id] = mol
                except Exception:
                    pass
        return molecules
        
    def _load_cache_index(self) -> Dict[str, dict]:
        idx_path = self.cache_dir / "cache_index.json"
        if idx_path.exists():
            with open(idx_path, 'r') as f:
                return json.load(f)
        return {}

    def _classify_question(self, question: str) -> ClassifiedQuestion:
        """
        Simple keyword-based classifier for MVP. 
        In production, this would use an LLM or regex (like qa_handlers.py)
        to map natural language to exact Node IDs.
        """
        lower_q = question.lower()
        
        # Check for explicit molecule mentions
        for mol_id, mol in self.molecule_registry.items():
            if mol.name.lower() in lower_q or mol_id.lower() in lower_q:
                
                # Check for specific components
                for comp in mol.components:
                    if comp.name.lower() in lower_q:
                        return ClassifiedQuestion(question, "component", mol_id, comp.name)
                        
                # Default to whole molecule
                depth = 3 if "how" in lower_q or "mechanism" in lower_q else 2
                return ClassifiedQuestion(question, "molecule", mol_id, requested_depth=depth)
                
        # Fallback to Design Synthesis
        return ClassifiedQuestion(question, "design_synthesis")

    def route_query(self, query: str, requested_depth: int = None) -> Dict[str, Any]:
        """
        Takes a natural language query, routes it to the specific molecule,
        and returns the precomputed summary for the website UI.
        """
        classified = self._classify_question(query)
        depth = requested_depth or classified.requested_depth
        
        # 1. Molecule Lookup (Fast Path - Precomputed)
        if classified.target_type == "molecule" and classified.target_id:
            mol_id = classified.target_id
            
            # Check cache
            cache_file = self.cache_dir / f"{mol_id}_QA.json"
            if cache_file.exists():
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)
                    
                    # Return progressive disclosure response
                    response = {
                        "topic": self.molecule_registry[mol_id].name,
                        "query_type": "molecule_lookup",
                        "depth_returned": depth,
                        "content": cache_data.get(f"l{depth}_summary", cache_data.get("l2_summary")),
                        "status": self.cache_index.get(mol_id, {}).get("status", "UNKNOWN"),
                        "available_depths": [1, 2, 3] if "l3_summary" in cache_data else [1, 2]
                    }
                    return response
            else:
                return {"error": f"Molecule {mol_id} found but cache not computed yet. Run precompute_pipeline.py"}
                
        # 2. Design Synthesis (Slow Path - Live LLM)
        elif classified.target_type == "design_synthesis":
            # Here we would hit the LLM live to route through multiple molecules
            return {
                "topic": "Custom Design Synthesis",
                "query_type": "synthesis",
                "content": "This feature requires hitting the live LLM endpoint to synthesize multiple molecules.",
                "status": "LIVE"
            }
            
        return {"error": "Could not understand or route query."}

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        router = MoleculeAwareRouter()
        result = router.route_query(query)
        print(json.dumps(result, indent=2))
    else:
        print("Usage: python3 -m src.qa.router 'What is Attention Restoration Theory?'")
