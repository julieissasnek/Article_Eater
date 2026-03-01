"""
T1.5 Theory Registry
====================
Loads all T1.5 theory definitions from data/theories/ and provides
lookup, query, and validation services.

Usage:
    registry = T1_5Registry()
    theory = registry.get("ART")
    reduced = registry.find_by_status("REDUCED")
    fw_theories = registry.find_by_framework("PP")
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from src.qa.molecules.t1_5_theory_schema import T1_5Theory

logger = logging.getLogger(__name__)


class T1_5Registry:
    """Central registry for T1.5 theory definitions.
    
    Loads JSON files from data/theories/ and indexes them by status,
    parent T1 framework, and constituent templates.
    """
    
    def __init__(self, theories_dir: str = "data/theories"):
        self.theories_dir = Path(theories_dir)
        self.theories: Dict[str, T1_5Theory] = {}
        self._framework_index: Dict[str, List[str]] = {}     # fw_id -> [theory_ids]
        self._template_index: Dict[str, List[str]] = {}       # template_id -> [theory_ids]
        self._status_index: Dict[str, List[str]] = {}         # status -> [theory_ids]
        self._load_all()
    
    def _load_all(self):
        """Load all theory JSON files from the registry directory."""
        if not self.theories_dir.exists():
            logger.warning(f"Theories directory not found: {self.theories_dir}")
            return
        
        for path in sorted(self.theories_dir.glob("*.json")):
            try:
                with open(path) as f:
                    data = json.load(f)
                theory = T1_5Theory.from_dict(data)
                
                # Validate
                errors = theory.validate()
                if errors:
                    for err in errors:
                        logger.warning(f"Validation warning in {path.name}: {err}")
                
                self.theories[theory.theory_id] = theory
                
                # Build indexes
                self._status_index.setdefault(theory.status, []).append(theory.theory_id)
                
                for fw_id in theory.parent_t1_frameworks:
                    self._framework_index.setdefault(fw_id, []).append(theory.theory_id)
                
                for tid in theory.constituent_templates:
                    self._template_index.setdefault(tid, []).append(theory.theory_id)
                    
            except Exception as e:
                logger.error(f"Failed to load theory from {path}: {e}")
    
    def get(self, theory_id: str) -> Optional[T1_5Theory]:
        """Get a theory by its ID."""
        return self.theories.get(theory_id)
    
    def get_all(self) -> List[T1_5Theory]:
        """Get all registered theories."""
        return list(self.theories.values())
    
    def find_by_status(self, status: str) -> List[T1_5Theory]:
        """Find theories by status (REDUCED, REJECTED, DEFERRED, CANDIDATE)."""
        ids = self._status_index.get(status, [])
        return [self.theories[tid] for tid in ids]
    
    def find_by_framework(self, framework_id: str) -> List[T1_5Theory]:
        """Find all T1.5 theories that reference a given T1 framework."""
        ids = self._framework_index.get(framework_id, [])
        return [self.theories[tid] for tid in ids]
    
    def find_by_template(self, template_id: str) -> List[T1_5Theory]:
        """Find all T1.5 theories that include a given template."""
        ids = self._template_index.get(template_id, [])
        return [self.theories[tid] for tid in ids]
    
    def get_constituent_templates(self, theory_id: str) -> List[str]:
        """Get all templates belonging to a specific T1.5 theory."""
        theory = self.get(theory_id)
        return theory.constituent_templates if theory else []
    
    def get_framework_contribution(self, theory_id: str) -> Dict[str, int]:
        """Get T1 framework percentage contributions for a theory."""
        theory = self.get(theory_id)
        return theory.parent_t1_frameworks if theory else {}
    
    def validate_all(self) -> Dict[str, List[str]]:
        """Validate all theories and return errors by theory_id."""
        results: Dict[str, List[str]] = {}
        for theory in self.theories.values():
            errors = theory.validate()
            if errors:
                results[theory.theory_id] = errors
        return results
    
    def summary(self) -> str:
        """Print a human-readable summary of the registry."""
        lines = [f"T1.5 Theory Registry: {len(self.theories)} theories loaded\n"]
        
        # Status counts
        for status in ["REDUCED", "CANDIDATE", "DEFERRED", "REJECTED"]:
            count = len(self._status_index.get(status, []))
            if count:
                lines.append(f"  {status}: {count}")
        lines.append("")
        
        # Detailed table for REDUCED theories
        lines.append(f"{'ID':<25} {'Name':<35} {'Coverage':>8} {'Maturity':<15} {'T1 Parents'}")
        lines.append("-" * 110)
        
        for theory in sorted(
            self.find_by_status("REDUCED"),
            key=lambda t: t.template_coverage_pct,
            reverse=True
        ):
            parents = ", ".join(f"{k}:{v}%" for k, v in theory.parent_t1_frameworks.items())
            lines.append(
                f"{theory.theory_id:<25} {theory.name:<35} "
                f"{theory.template_coverage_pct:>7.0%} {theory.maturity:<15} {parents}"
            )
        
        # Validation
        errors = self.validate_all()
        if errors:
            lines.append(f"\n⚠ {len(errors)} theories with validation warnings")
            for tid, errs in errors.items():
                for e in errs:
                    lines.append(f"  - {e}")
        else:
            lines.append("\n✓ All theories pass validation")
        
        return "\n".join(lines)
