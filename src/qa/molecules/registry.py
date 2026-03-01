"""
Molecule Registry
=================
Central registry that loads all Molecule definitions and provides lookup,
query, and integration services for the Web of Belief, QA engine, and
extraction pipeline.

Usage:
    registry = MoleculeRegistry()
    mol = registry.get("ART")
    mols = registry.find_by_framework("PP")
    mols = registry.find_by_template("T27")
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

from src.qa.molecules.schema import Molecule


class MoleculeRegistry:
    """Central registry for all Molecule definitions.
    
    This serves as the single source of truth for which Molecules exist,
    what templates they depend on, and how they relate to each other.
    
    Integration points:
    - QA Router: routes queries to pre-computed summaries
    - QA Cache Manager: invalidation when constituent templates change
    - Extraction Pipeline: molecule-aware classification and prompt selection
    - Incremental BN: theory-level coherence checking
    - Streamlit Frontend: sidebar taxonomy navigation
    """
    
    def __init__(self, molecule_dir: str = "data/molecules"):
        self.molecule_dir = Path(molecule_dir)
        self.molecules: Dict[str, Molecule] = {}
        self._template_index: Dict[str, List[str]] = {}  # template_id -> [molecule_ids]
        self._framework_index: Dict[str, List[str]] = {}  # framework_id -> [molecule_ids]
        self._load_all()
    
    def _load_all(self):
        """Load all molecule JSON files from the registry directory."""
        if not self.molecule_dir.exists():
            return
        
        for path in sorted(self.molecule_dir.glob("*.json")):
            try:
                with open(path) as f:
                    data = json.load(f)
                mol = Molecule.from_dict(data)
                self.molecules[mol.molecule_id] = mol
                
                # Build reverse indexes
                for tid in mol.constituent_templates:
                    self._template_index.setdefault(tid, []).append(mol.molecule_id)
                for fid in mol.framework_ids:
                    self._framework_index.setdefault(fid, []).append(mol.molecule_id)
            except Exception as e:
                print(f"Warning: Failed to load molecule from {path}: {e}")
    
    def get(self, molecule_id: str) -> Optional[Molecule]:
        """Get a molecule by its ID."""
        return self.molecules.get(molecule_id)
    
    def get_all(self) -> List[Molecule]:
        """Get all registered molecules."""
        return list(self.molecules.values())
    
    def find_by_template(self, template_id: str) -> List[Molecule]:
        """Find all molecules that depend on a given template.
        
        This is the key integration point for cache invalidation:
        when a template changes, which molecules need recomputation?
        """
        mol_ids = self._template_index.get(template_id, [])
        return [self.molecules[mid] for mid in mol_ids]
    
    def find_by_framework(self, framework_id: str) -> List[Molecule]:
        """Find all molecules belonging to a given framework."""
        mol_ids = self._framework_index.get(framework_id, [])
        return [self.molecules[mid] for mid in mol_ids]
    
    def find_by_domain(self, domain: str) -> List[Molecule]:
        """Find all molecules in a given domain (e.g., 'restoration', 'navigation')."""
        return [m for m in self.molecules.values() if m.domain == domain]
    
    def find_by_type(self, molecule_type: str) -> List[Molecule]:
        """Find all molecules of a given type (THEORY, MECHANISM, PHENOMENON, DESIGN_PATTERN)."""
        return [m for m in self.molecules.values() if m.molecule_type == molecule_type]
    
    def find_competing(self, molecule_id: str) -> List[Molecule]:
        """Find competing theories for a given molecule."""
        mol = self.get(molecule_id)
        if not mol:
            return []
        return [self.molecules[cid] for cid in mol.competing_theories if cid in self.molecules]
    
    def get_template_coverage(self) -> Dict[str, List[str]]:
        """Show which templates are covered by molecules and which are orphans.
        
        Returns dict with keys 'covered' and 'orphaned'.
        """
        return {
            "covered": list(self._template_index.keys()),
            "orphan_count_note": "Compare against template_id_aliases.json for full orphan analysis"
        }
    
    def get_taxonomy(self) -> Dict[str, List[Dict[str, str]]]:
        """Generate a hierarchical taxonomy for frontend navigation.
        
        Groups molecules by domain, returning a structure suitable
        for rendering in a sidebar or navigation tree.
        """
        taxonomy: Dict[str, List[Dict[str, str]]] = {}
        for mol in self.molecules.values():
            domain = mol.domain or "uncategorized"
            if domain not in taxonomy:
                taxonomy[domain] = []
            taxonomy[domain].append({
                "molecule_id": mol.molecule_id,
                "name": mol.name,
                "type": mol.molecule_type,
                "maturity": mol.overall_maturity,
                "empirical_support": mol.empirical_support,
                "n_templates": str(len(mol.constituent_templates)),
                "n_components": str(len(mol.components))
            })
        return taxonomy
    
    # --- T1.5	-aware queries [C5] ---
    
    def find_by_t1_5(self, theory_id: str) -> List[Molecule]:
        """Find all molecules that are children of a given T1.5 theory.
        
        Uses the parent_t1_5_theory field on molecules [HC].
        """
        return [
            m for m in self.molecules.values()
            if m.parent_t1_5_theory == theory_id
        ]
    
    def get_reduction_chain(self, template_id: str) -> Dict:
        """Trace a template's position in the hierarchy:
        template → T1.5 theories → molecules.
        
        Returns a dict with the template's T1.5 parents and
        molecules that include this template.
        """
        # Import here to avoid circular imports
        from src.qa.molecules.t1_5_registry import T1_5Registry
        
        t1_5_reg = T1_5Registry()
        t1_5_parents = t1_5_reg.find_by_template(template_id)
        molecules = self.find_by_template(template_id)
        
        return {
            "template_id": template_id,
            "t1_5_parents": [
                {
                    "theory_id": t.theory_id,
                    "name": t.name,
                    "coverage_pct": t.template_coverage_pct
                }
                for t in t1_5_parents
            ],
            "molecules": [
                {
                    "molecule_id": m.molecule_id,
                    "name": m.name
                }
                for m in molecules
            ]
        }
    
    def get_coverage_by_theory(self) -> Dict[str, Dict]:
        """For each T1.5 theory, show how many of its constituent
        templates are covered by molecules.
        
        Returns dict mapping theory_id -> {total_templates, covered, pct}.
        """
        from src.qa.molecules.t1_5_registry import T1_5Registry
        
        t1_5_reg = T1_5Registry()
        results = {}
        
        for theory in t1_5_reg.find_by_status("REDUCED"):
            theory_templates = set(theory.constituent_templates)
            covered = theory_templates & set(self._template_index.keys())
            results[theory.theory_id] = {
                "total_templates": len(theory_templates),
                "covered_by_molecules": len(covered),
                "coverage_pct": len(covered) / len(theory_templates) if theory_templates else 0.0
            }
        
        return results

    def summary(self) -> str:
        """Print a human-readable summary of the registry."""
        lines = [f"Molecule Registry: {len(self.molecules)} molecules loaded\n"]
        lines.append(f"{'ID':<30} {'Name':<40} {'Type':<15} {'Templates':>5} {'Support':<12}")
        lines.append("-" * 110)
        for mol in sorted(self.molecules.values(), key=lambda m: m.domain):
            lines.append(
                f"{mol.molecule_id:<30} {mol.name:<40} {mol.molecule_type:<15} "
                f"{len(mol.constituent_templates):>5} {mol.empirical_support:<12}"
            )
        return "\n".join(lines)
