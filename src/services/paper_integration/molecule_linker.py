"""
Molecule Linker — Belief → Template → Molecule → T1.5 Hookup
=============================================================

Created: 2026-02-25
Sprint: INTEGRATION-1

When new beliefs enter the web of belief, this module:

1. Template matching: Compares belief constructs against CMR template
   fields (construct_name, dependent_variable, independent_variable)
   using keyword and embedding similarity.

2. Molecule propagation: If a belief matches a template in a molecule's
   constituent_templates, marks that molecule's QA cache as stale.

3. T1.5 linkage: If the matched template has t1_5_parent_theories,
   records the belief → T1.5 connection in provenance.

4. T1 linkage: Via the template's t1_frameworks field (always populated).

5. Staleness cascade: Triggers QACacheManager recomputation for affected
   molecules.

Reuses:
- src/qa/molecules/registry.py: MoleculeRegistry.find_by_template()
- src/qa/molecules/t1_5_registry.py: T1_5Registry.find_by_template()
- src/qa/qa_cache_manager.py: QACacheManager for staleness detection
"""

from __future__ import annotations

import logging
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Tuple

logger = logging.getLogger(__name__)


# =============================================================================
# TEMPLATE MATCH RESULT
# =============================================================================

@dataclass
class TemplateMatch:
    """Result of matching a belief against the template library."""
    template_id: str
    match_score: float            # 0.0-1.0
    match_method: str             # "keyword" | "embedding" | "construct_id"
    t1_frameworks: List[str] = field(default_factory=list)
    t1_5_theories: List[str] = field(default_factory=list)
    molecules: List[str] = field(default_factory=list)


@dataclass
class LinkageResult:
    """Complete linkage result for a single belief."""
    belief_id: str
    paper_id: str
    template_matches: List[TemplateMatch] = field(default_factory=list)
    molecules_affected: List[str] = field(default_factory=list)
    t1_5_theories_linked: List[str] = field(default_factory=list)
    t1_frameworks_linked: List[str] = field(default_factory=list)
    stale_molecules: List[str] = field(default_factory=list)


# =============================================================================
# MOLECULE LINKER
# =============================================================================

class MoleculeLinker:
    """
    Links new beliefs to the CMR template/molecule/T1.5 hierarchy.

    Architecture:
        Belief (text) → Template (matched by construct) → Molecule (containing template)
            → T1.5 Theory (parent of molecule) → T1 Framework (parent of T1.5)
    """

    # Minimum match score to consider a template match valid
    MATCH_THRESHOLD = 0.50

    def __init__(
        self,
        template_dir: str = "data/templates",
        molecule_dir: str = "data/molecules",
        theory_dir: str = "data/theories",
    ):
        self.template_dir = Path(template_dir)
        self.molecule_dir = Path(molecule_dir)
        self.theory_dir = Path(theory_dir)

        # Lazy-loaded caches
        self._templates: Optional[Dict[str, dict]] = None
        self._molecules: Optional[Dict[str, dict]] = None
        self._theories: Optional[Dict[str, dict]] = None

        # Inverted indices (built on first use)
        self._template_to_molecules: Optional[Dict[str, List[str]]] = None
        self._template_to_theories: Optional[Dict[str, List[str]]] = None

    # -------------------------------------------------------------------------
    # PUBLIC API
    # -------------------------------------------------------------------------

    def link_belief(
        self,
        belief_id: str,
        paper_id: str,
        statement: str,
        construct_id: Optional[str] = None,
        dependent_variable: Optional[str] = None,
        independent_variable: Optional[str] = None,
    ) -> LinkageResult:
        """
        Link a single belief to the CMR hierarchy.

        Args:
            belief_id: The belief being linked
            paper_id: The paper that produced this belief
            statement: The belief's text statement
            construct_id: Explicit construct ID (if available from extraction)
            dependent_variable: DV from claim (e.g., "cortisol")
            independent_variable: IV from claim (e.g., "nature exposure")

        Returns:
            LinkageResult with all template matches and hierarchy links
        """
        self._ensure_caches()

        result = LinkageResult(belief_id=belief_id, paper_id=paper_id)

        # Step 1: Find matching templates
        matches = self._match_templates(
            statement, construct_id, dependent_variable, independent_variable
        )

        for match in matches:
            result.template_matches.append(match)

            # Step 2: Propagate to molecules
            mol_ids = self._template_to_molecules.get(match.template_id, [])
            match.molecules = mol_ids
            for mid in mol_ids:
                if mid not in result.molecules_affected:
                    result.molecules_affected.append(mid)
                if mid not in result.stale_molecules:
                    result.stale_molecules.append(mid)

            # Step 3: Propagate to T1.5 theories
            theory_ids = self._template_to_theories.get(match.template_id, [])
            match.t1_5_theories = theory_ids
            for tid in theory_ids:
                if tid not in result.t1_5_theories_linked:
                    result.t1_5_theories_linked.append(tid)

            # Step 4: Propagate to T1 frameworks
            for fw in match.t1_frameworks:
                if fw not in result.t1_frameworks_linked:
                    result.t1_frameworks_linked.append(fw)

        return result

    def link_beliefs_batch(
        self,
        beliefs: List[Dict[str, Any]],
        paper_id: str,
    ) -> List[LinkageResult]:
        """
        Link multiple beliefs in batch (more efficient than individual calls).

        Each belief dict should have: belief_id, statement, and optionally
        construct_id, dependent_variable, independent_variable.
        """
        self._ensure_caches()
        results = []
        for b in beliefs:
            result = self.link_belief(
                belief_id=b.get("belief_id", ""),
                paper_id=paper_id,
                statement=b.get("statement", ""),
                construct_id=b.get("construct_id"),
                dependent_variable=b.get("dependent_variable"),
                independent_variable=b.get("independent_variable"),
            )
            results.append(result)
        return results

    def get_stale_molecules(
        self, linkage_results: List[LinkageResult]
    ) -> List[str]:
        """Extract unique stale molecule IDs from a batch of linkage results."""
        stale = set()
        for r in linkage_results:
            stale.update(r.stale_molecules)
        return sorted(stale)

    # -------------------------------------------------------------------------
    # TEMPLATE MATCHING
    # -------------------------------------------------------------------------

    def _match_templates(
        self,
        statement: str,
        construct_id: Optional[str],
        dependent_variable: Optional[str],
        independent_variable: Optional[str],
    ) -> List[TemplateMatch]:
        """
        Match a belief against the template library.

        Priority:
        1. Exact construct_id match (highest confidence)
        2. DV/IV keyword match
        3. Statement keyword match (lowest confidence)
        """
        matches = []
        statement_lower = statement.lower()

        for tid, template in self._templates.items():
            score = 0.0
            method = "keyword"

            # Exact construct_id match
            t_construct = template.get("construct_name", "").lower()
            if construct_id and t_construct:
                if construct_id.lower() == t_construct:
                    score = 0.95
                    method = "construct_id"

            # DV/IV match (if not already matched)
            if score < self.MATCH_THRESHOLD:
                t_dv = template.get("dependent_variable", "").lower()
                t_iv = template.get("independent_variable", "").lower()

                dv_match = (
                    dependent_variable
                    and t_dv
                    and dependent_variable.lower() in t_dv
                )
                iv_match = (
                    independent_variable
                    and t_iv
                    and independent_variable.lower() in t_iv
                )

                if dv_match and iv_match:
                    score = 0.85
                    method = "keyword"
                elif dv_match or iv_match:
                    score = 0.65
                    method = "keyword"

            # Statement keyword match (fallback)
            if score < self.MATCH_THRESHOLD:
                keywords = self._extract_template_keywords(template)
                if keywords:
                    hits = sum(1 for kw in keywords if kw in statement_lower)
                    if hits >= 2:
                        score = min(0.70, 0.3 + hits * 0.10)
                        method = "keyword"

            if score >= self.MATCH_THRESHOLD:
                t1_frameworks = list(
                    template.get("t1_frameworks", {}).keys()
                )
                matches.append(TemplateMatch(
                    template_id=tid,
                    match_score=score,
                    match_method=method,
                    t1_frameworks=t1_frameworks,
                ))

        # Sort by score descending, take top 5
        matches.sort(key=lambda m: m.match_score, reverse=True)
        return matches[:5]

    def _extract_template_keywords(self, template: dict) -> List[str]:
        """Extract searchable keywords from a template definition."""
        keywords = []
        for field_name in [
            "construct_name", "dependent_variable", "independent_variable",
            "short_description",
        ]:
            val = template.get(field_name, "")
            if val:
                # Split on common delimiters and take meaningful words
                words = val.lower().replace("_", " ").split()
                keywords.extend(w for w in words if len(w) > 3)
        return keywords

    # -------------------------------------------------------------------------
    # CACHE MANAGEMENT
    # -------------------------------------------------------------------------

    def _ensure_caches(self) -> None:
        """Load and index templates, molecules, and theories."""
        if self._templates is not None:
            return

        self._templates = self._load_json_dir(self.template_dir)
        self._molecules = self._load_json_dir(self.molecule_dir)
        self._theories = self._load_json_dir(self.theory_dir)

        # Build inverted indices
        self._template_to_molecules = {}
        for mol_id, mol in self._molecules.items():
            for tid in mol.get("constituent_templates", []):
                self._template_to_molecules.setdefault(tid, []).append(mol_id)

        self._template_to_theories = {}
        for theory_id, theory in self._theories.items():
            for tid in theory.get("constituent_templates", []):
                self._template_to_theories.setdefault(tid, []).append(theory_id)

        logger.info(
            "MoleculeLinker loaded: %d templates, %d molecules, %d theories",
            len(self._templates),
            len(self._molecules),
            len(self._theories),
        )

    def _load_json_dir(self, directory: Path) -> Dict[str, dict]:
        """Load all JSON files from a directory into a dict keyed by filename stem."""
        result = {}
        if not directory.exists():
            logger.warning("Directory not found: %s", directory)
            return result

        for path in directory.glob("*.json"):
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                # Use the ID field if available, else filename stem
                key = (
                    data.get("template_id")
                    or data.get("molecule_id")
                    or data.get("theory_id")
                    or path.stem
                )
                result[key] = data
            except (json.JSONDecodeError, OSError) as e:
                logger.warning("Failed to load %s: %s", path, e)

        return result

    def invalidate_caches(self) -> None:
        """Force reload of all caches on next use."""
        self._templates = None
        self._molecules = None
        self._theories = None
        self._template_to_molecules = None
        self._template_to_theories = None
