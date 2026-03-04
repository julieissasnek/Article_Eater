"""
T1 Atom Registry
================
Central registry for all T1 Atom definitions.

This registry implements the panel's Recommendation #1: "Separate canonical
from hypothetical T1 atoms" by providing stratified access to the ~30
computational primitives that underlie T1 frameworks.

The registry serves three main functions:
1. **Indexing**: Quick lookup by atom_id, framework, or maturity level
2. **Stratification**: Separate CANONICAL, ESTABLISHED, HYPOTHETICAL atoms
3. **Querying**: Find atoms by framework, maturity, or cross-domain status

Usage:
    registry = T1AtomRegistry()
    atom = registry.get("lateral_inhibition")
    canonical_atoms = registry.find_canonical()
    atoms = registry.find_by_framework("predictive-processing")
    print(registry.summary())
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

from src.qa.molecules.t1_atom_schema import T1Atom


class T1AtomRegistry:
    """Central registry for all T1 Atom definitions.

    Loads ~30 atoms from JSON files, indexes them by framework and maturity,
    and provides query methods for the ATLAS system.

    Attributes:
    -----------
    atoms: Dict[str, T1Atom]
        All loaded atoms, indexed by atom_id.

    _framework_index: Dict[str, List[str]]
        framework_id -> [atom_ids] for reverse lookup.

    _maturity_index: Dict[str, List[str]]
        maturity_level -> [atom_ids] for stratification queries.
    """

    def __init__(self, atoms_dir: str = "data/atoms"):
        """Initialize the registry by loading all atoms from disk.

        Args:
            atoms_dir: Path to directory containing atom JSON files.
        """
        self.atoms_dir = Path(atoms_dir)
        self.atoms: Dict[str, T1Atom] = {}
        self._framework_index: Dict[str, List[str]] = {}
        self._maturity_index: Dict[str, List[str]] = {}
        self._load_all()

    def _load_all(self):
        """Load all atom JSON files from atoms_dir.

        Silently skips missing directory; prints warnings on load failures.
        """
        if not self.atoms_dir.exists():
            return

        for path in sorted(self.atoms_dir.glob("*.json")):
            try:
                with open(path) as f:
                    data = json.load(f)
                atom = T1Atom.from_dict(data)

                # Validate before adding
                errors = atom.validate()
                if errors:
                    print(f"Warning: Atom {path} has validation errors: {errors}")
                    continue

                self.atoms[atom.atom_id] = atom

                # Build reverse indexes
                for framework in atom.t1_frameworks:
                    self._framework_index.setdefault(framework, []).append(atom.atom_id)

                maturity = atom.maturity
                self._maturity_index.setdefault(maturity, []).append(atom.atom_id)

            except Exception as e:
                print(f"Warning: Failed to load atom from {path}: {e}")

    def get(self, atom_id: str) -> Optional[T1Atom]:
        """Get a single atom by ID.

        Args:
            atom_id: The atom's unique identifier.

        Returns:
            T1Atom if found, None otherwise.
        """
        return self.atoms.get(atom_id)

    def get_all(self) -> List[T1Atom]:
        """Get all registered atoms."""
        return list(self.atoms.values())

    def find_by_framework(self, framework_id: str) -> List[T1Atom]:
        """Find all atoms used by a given T1 framework.

        Args:
            framework_id: The framework's ID (e.g., "predictive-processing").

        Returns:
            List of T1Atoms belonging to this framework.
        """
        atom_ids = self._framework_index.get(framework_id, [])
        return [self.atoms[aid] for aid in atom_ids if aid in self.atoms]

    def find_by_maturity(self, maturity: str) -> List[T1Atom]:
        """Find all atoms at a given maturity level.

        Args:
            maturity: One of CANONICAL, ESTABLISHED, HYPOTHETICAL.

        Returns:
            List of T1Atoms at this maturity level.
        """
        if maturity not in ("CANONICAL", "ESTABLISHED", "HYPOTHETICAL"):
            return []
        atom_ids = self._maturity_index.get(maturity, [])
        return [self.atoms[aid] for aid in atom_ids if aid in self.atoms]

    def find_canonical(self) -> List[T1Atom]:
        """Get all CANONICAL atoms (neurally grounded, mechanistically understood).

        Returns:
            List of T1Atoms with maturity=CANONICAL.
        """
        return self.find_by_maturity("CANONICAL")

    def find_established(self) -> List[T1Atom]:
        """Get all ESTABLISHED atoms (good evidence, some domain limitations).

        Returns:
            List of T1Atoms with maturity=ESTABLISHED.
        """
        return self.find_by_maturity("ESTABLISHED")

    def find_hypothetical(self) -> List[T1Atom]:
        """Get all HYPOTHETICAL atoms (theoretically motivated, limited evidence).

        Returns:
            List of T1Atoms with maturity=HYPOTHETICAL.
        """
        return self.find_by_maturity("HYPOTHETICAL")

    def find_cross_domain(self) -> List[T1Atom]:
        """Get all atoms confirmed across multiple domains.

        Returns:
            List of T1Atoms with cross_domain_confirmed=True.
        """
        return [a for a in self.atoms.values() if a.cross_domain_confirmed]

    def summary(self) -> str:
        """Generate a human-readable summary of the registry.

        Returns a formatted table with atom_id, name, maturity, domains, and frameworks.

        Returns:
            Multi-line string suitable for printing.
        """
        lines = [f"T1 Atom Registry: {len(self.atoms)} atoms loaded\n"]

        # Count by maturity
        canonical = self.find_canonical()
        established = self.find_established()
        hypothetical = self.find_hypothetical()

        lines.append(
            f"Stratification: {len(canonical)} CANONICAL, {len(established)} ESTABLISHED, {len(hypothetical)} HYPOTHETICAL\n"
        )

        lines.append(f"{'ID':<30} {'Name':<35} {'Maturity':<12} {'Cross-Domain':<12} {'Frameworks':<30}")
        lines.append("-" * 120)

        for atom in sorted(self.atoms.values(), key=lambda a: (a.maturity, a.atom_id)):
            cross_domain = "YES" if atom.cross_domain_confirmed else "NO"
            frameworks = ", ".join(atom.t1_frameworks[:2])
            if len(atom.t1_frameworks) > 2:
                frameworks += f" +{len(atom.t1_frameworks) - 2}"
            lines.append(
                f"{atom.atom_id:<30} {atom.name:<35} {atom.maturity:<12} {cross_domain:<12} {frameworks:<30}"
            )

        return "\n".join(lines)

    def get_framework_coverage(self) -> Dict[str, Dict[str, int]]:
        """Analyze which atoms are used by which frameworks.

        Returns:
            Dict mapping framework_id -> {"total": count, "by_maturity": {...}}
        """
        coverage = {}
        for framework_id, atom_ids in self._framework_index.items():
            atoms = [self.atoms[aid] for aid in atom_ids if aid in self.atoms]
            maturity_counts = {
                "CANONICAL": len([a for a in atoms if a.maturity == "CANONICAL"]),
                "ESTABLISHED": len([a for a in atoms if a.maturity == "ESTABLISHED"]),
                "HYPOTHETICAL": len([a for a in atoms if a.maturity == "HYPOTHETICAL"]),
            }
            coverage[framework_id] = {
                "total": len(atoms),
                "by_maturity": maturity_counts
            }
        return coverage

    def validate_registry(self) -> Dict[str, List[str]]:
        """Validate all atoms and the registry as a whole.

        Returns:
            Dict with keys 'errors' and 'warnings' containing validation messages.
        """
        errors = []
        warnings = []

        # Check maturity counts
        canonical = self.find_canonical()
        established = self.find_established()
        hypothetical = self.find_hypothetical()

        if len(canonical) < 10:
            warnings.append(f"Only {len(canonical)} CANONICAL atoms; recommend ~10")
        if len(established) < 10:
            warnings.append(f"Only {len(established)} ESTABLISHED atoms; recommend ~10")
        if len(hypothetical) < 10:
            warnings.append(f"Only {len(hypothetical)} HYPOTHETICAL atoms; recommend ~10")

        # Check that all CANONICAL atoms are cross-domain
        non_cross_domain_canonical = [a for a in canonical if not a.cross_domain_confirmed]
        if non_cross_domain_canonical:
            errors.append(
                f"CANONICAL atoms without cross_domain_confirmed=True: "
                f"{[a.atom_id for a in non_cross_domain_canonical]}"
            )

        # Check that all atoms have frameworks
        atoms_without_frameworks = [a for a in self.atoms.values() if not a.t1_frameworks]
        if atoms_without_frameworks:
            warnings.append(
                f"Atoms without frameworks: {[a.atom_id for a in atoms_without_frameworks]}"
            )

        # Validate individual atoms
        for atom in self.atoms.values():
            atom_errors = atom.validate()
            if atom_errors:
                errors.extend([f"{atom.atom_id}: {err}" for err in atom_errors])

        return {
            "errors": errors,
            "warnings": warnings
        }
