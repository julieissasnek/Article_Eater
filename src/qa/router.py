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
     Phase 3+: Routes user queries through a priority chain:
     1. Molecule lookup (cached, instant)
     2. Argument queries (critiques, evidence hierarchies)
     3. Arbitrary QA (catalog, surprise, dispute, design, AI-routed)
     All responses enriched with read-next suggestions and relevant images.
    """
    def __init__(self, molecule_dir: str = "data/molecules", cache_dir: str = "data/qa_cache"):
        self.molecule_dir = Path(molecule_dir)
        self.cache_dir = Path(cache_dir)
        self.molecule_registry: Dict[str, Molecule] = self._load_molecules()
        self.cache_index = self._load_cache_index()
        
        # Extended handlers (lazy init to avoid circular imports)
        self._arbitrary_handler = None
        self._read_next = None
        self._argument_handler = None

    @property
    def arbitrary_handler(self):
        if self._arbitrary_handler is None:
            try:
                from src.services.arbitrary_qa_handler import ArbitraryQAHandler
                self._arbitrary_handler = ArbitraryQAHandler()
            except Exception:
                pass
        return self._arbitrary_handler
    
    @property
    def read_next(self):
        if self._read_next is None:
            try:
                from src.services.read_next_engine import ReadNextEngine
                self._read_next = ReadNextEngine()
            except Exception:
                pass
        return self._read_next
    
    @property
    def argument_handler(self):
        if self._argument_handler is None:
            try:
                from src.argument.qa_handlers import ArgumentQueryHandler
                self._argument_handler = ArgumentQueryHandler()
            except Exception:
                pass
        return self._argument_handler

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
        Unified query routing:
        1. Molecule lookup (fast path — precomputed cache)
        2. Argument queries (critiques, evidence hierarchies)
        3. Arbitrary QA (catalog, extended annotations, AI-routed)
        
        All responses enriched with read-next suggestions and relevant images.
        """
        classified = self._classify_question(query)
        depth = requested_depth or classified.requested_depth
        
        response = None
        
        # 1. Molecule Lookup (Fast Path - Precomputed)
        if classified.target_type == "molecule" and classified.target_id:
            mol_id = classified.target_id
            cache_file = self.cache_dir / f"{mol_id}_QA.json"
            if cache_file.exists():
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)
                    response = {
                        "topic": self.molecule_registry[mol_id].name,
                        "query_type": "molecule_lookup",
                        "depth_returned": depth,
                        "content": cache_data.get(f"l{depth}_summary", cache_data.get("l2_summary")),
                        "status": self.cache_index.get(mol_id, {}).get("status", "UNKNOWN"),
                        "available_depths": [1, 2, 3] if "l3_summary" in cache_data else [1, 2]
                    }
        
        # 2. Argument Queries (critiques, evidence hierarchies)
        if response is None and self.argument_handler:
            try:
                arg_result = self.argument_handler.handle_query(
                    query_id=f"live_{hash(query) % 10000}",
                    query_text=query,
                    processing_time_ms=0,
                )
                if arg_result is not None:
                    response = arg_result
            except Exception:
                pass
        
        # 3. Arbitrary QA (catalog, extended annotations, AI-routed)
        if response is None and self.arbitrary_handler:
            try:
                response = self.arbitrary_handler.answer(query)
            except Exception:
                pass
        
        # 4. Final fallback
        if response is None:
            response = {
                "topic": "Unknown",
                "query_type": "unrouted",
                "headline": "Could not route this query. Try asking about theories, cultural differences, or design parameters.",
                "status": "NO_MATCH",
            }
        
        # Enrich with read-next suggestions and images
        if self.read_next:
            try:
                self.read_next.enrich_qa_response(response, query)
            except Exception:
                pass
        
        return response


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        router = MoleculeAwareRouter()
        result = router.route_query(query)
        print(json.dumps(result, indent=2, default=str))
    else:
        print("Usage: python3 -m src.qa.router 'What is Attention Restoration Theory?'")

