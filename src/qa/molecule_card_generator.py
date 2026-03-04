#!/usr/bin/env python3
"""
Molecule Card Generator — Corpus-Grounded L1 Cards for All Entity Types
=========================================================================

Complements the existing CardGenerator (which handles belief cluster → cards)
by generating L1 answer cards for the molecule layer:
1. All 38 molecules (18 regular + 20 functional circuits)
2. All 6 T2 archetypes

L1 cards contain evidence-based data from the extraction corpus — no LLM needed:
- Evidence count, key findings, study design distribution
- Component descriptions, linked archetypes
- L2/L3 summaries marked PENDING for MolecularQAPrecomputer

Usage:
    from src.qa.molecule_card_generator import MoleculeCardGenerator
    gen = MoleculeCardGenerator()
    gen.generate_all()  # All uncovered entities

    # After new paper integration (real-time cascade):
    affected = gen.invalidate_affected_molecules("data/extractions/new.json")
    for mol_id in affected:
        gen.generate_for_molecule(mol_id)
"""

from __future__ import annotations

import json
import logging
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Set

logger = logging.getLogger(__name__)

# T2 Archetypes — from router.py
_ARCHETYPES = {
    "PREDICTIVE_CODING": {
        "name": "Predictive Coding",
        "aliases": ["predictive coding", "prediction error", "bayesian brain", "free energy"],
        "description": "Neural circuits that maintain and update predictions about sensory input, generating prediction errors when expectations are violated.",
    },
    "HOMEOSTATIC_REGULATION": {
        "name": "Homeostatic Regulation",
        "aliases": ["homeostatic", "homeostasis", "set point", "regulatory"],
        "description": "Circuits that maintain physiological and psychological variables within optimal ranges through feedback and feedforward control.",
    },
    "ACCUMULATION_TO_BOUND": {
        "name": "Accumulation to Bound",
        "aliases": ["accumulation to bound", "drift diffusion", "evidence accumulation", "threshold"],
        "description": "Decision circuits where evidence is integrated over time until a threshold triggers action or state transition.",
    },
    "COMPETITIVE_SELECTION": {
        "name": "Competitive Selection",
        "aliases": ["competitive selection", "winner take all", "lateral inhibition", "competition"],
        "description": "Circuits where multiple representations compete for dominance through mutual inhibition.",
    },
    "GATED_PROPAGATION": {
        "name": "Gated Propagation",
        "aliases": ["gated propagation", "gating", "thalamic gate", "gain control"],
        "description": "Circuits that control information flow by amplifying or suppressing signals based on context, attention, or arousal state.",
    },
    "CONVERGENT_STATE_MONITORING": {
        "name": "Convergent State Monitoring",
        "aliases": ["convergent state", "state monitoring", "fluency monitor", "coherence monitor"],
        "description": "Circuits that track processing coherence and signal when processing converges or diverges.",
    },
}


class MoleculeCardGenerator:
    """
    Generates corpus-grounded L1 answer cards for molecules, FCs,
    and T2 archetypes. No LLM needed.
    """

    def __init__(
        self,
        molecule_dir: str = "data/molecules",
        extractions_dir: str = "data/extractions",
        cache_dir: str = "data/qa_cache",
    ):
        self._molecule_dir = Path(molecule_dir)
        self._extractions_dir = Path(extractions_dir)
        self._cache_dir = Path(cache_dir)
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._molecules: Optional[Dict[str, dict]] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_all(self, force: bool = False) -> Dict[str, str]:
        """
        Generate L1 cards for all molecules + archetypes.

        Returns:
            Dict mapping entity_id -> status ("generated", "exists", "failed")
        """
        molecules = self._load_molecules()
        results = {}

        for mol_id in sorted(molecules):
            cache_path = self._cache_dir / f"{mol_id.upper()}_QA.json"
            if cache_path.exists() and not force:
                results[mol_id] = "exists"
                continue
            try:
                self.generate_for_molecule(mol_id)
                results[mol_id] = "generated"
            except Exception as e:
                logger.error(f"Failed card for {mol_id}: {e}")
                results[mol_id] = "failed"

        # Archetype cards
        for arch_id, arch_info in _ARCHETYPES.items():
            cache_path = self._cache_dir / f"ARCHETYPE_{arch_id}_QA.json"
            if cache_path.exists() and not force:
                results[f"archetype_{arch_id}"] = "exists"
                continue
            try:
                self._generate_archetype_card(arch_id, arch_info, molecules)
                results[f"archetype_{arch_id}"] = "generated"
            except Exception as e:
                logger.error(f"Failed archetype {arch_id}: {e}")
                results[f"archetype_{arch_id}"] = "failed"

        return results

    def generate_for_molecule(self, molecule_id: str) -> dict:
        """Generate a corpus-grounded L1 card for a single molecule."""
        molecules = self._load_molecules()
        mol_id_lower = molecule_id.lower()
        if mol_id_lower not in molecules:
            raise ValueError(f"Unknown molecule: {molecule_id}")

        mol = molecules[mol_id_lower]
        keywords = self._molecule_keywords(mol)
        evidence = self._search_corpus(keywords)
        card = self._build_card(mol_id_lower, mol, evidence)

        cache_path = self._cache_dir / f"{mol_id_lower.upper()}_QA.json"
        with open(cache_path, "w") as f:
            json.dump(card, f, indent=2)

        logger.info(
            f"Card for {mol.get('name', mol_id_lower)}: "
            f"{evidence['n_findings']} findings / {evidence['n_papers']} papers"
        )
        return card

    def invalidate_affected_molecules(self, extraction_path: str) -> List[str]:
        """
        Given a new extraction, find which molecule cards need regeneration.
        Used by PaperIntegrationOrchestrator for real-time cascade.
        """
        try:
            with open(extraction_path) as f:
                data = json.load(f)
        except Exception as e:
            logger.error(f"Cannot read extraction: {e}")
            return []

        molecules = self._load_molecules()
        text = " ".join([
            data.get("title", ""),
            data.get("abstract", ""),
            " ".join(
                (f.get("antecedent") or "") + " " + (f.get("consequent") or "")
                for f in data.get("findings", [])
            ),
        ]).lower()

        affected = []
        for mol_id, mol in molecules.items():
            keywords = self._molecule_keywords(mol)
            if sum(1 for kw in keywords if kw in text) >= 2:
                affected.append(mol_id)

        return affected

    # ------------------------------------------------------------------
    # Internal: corpus search
    # ------------------------------------------------------------------

    def _search_corpus(self, keywords: Set[str], max_papers: int = 50) -> dict:
        findings = []
        papers = set()
        designs = Counter()

        if not self._extractions_dir.exists():
            return {"n_findings": 0, "n_papers": 0, "top_findings": [],
                    "design_distribution": {}, "summary": {}}

        for jf in sorted(self._extractions_dir.glob("*.json")):
            try:
                with open(jf) as f:
                    data = json.load(f)

                text = ((data.get("title") or "") + " " + (data.get("abstract") or "")).lower()
                if sum(1 for kw in keywords if kw in text) < 2:
                    continue

                papers.add(jf.stem)
                for finding in data.get("findings", []):
                    ft = ((finding.get("antecedent") or "") + " " + (finding.get("consequent") or "")).lower()
                    rel = sum(1 for kw in keywords if kw in ft)
                    if rel >= 1:
                        findings.append({
                            "paper_id": jf.stem,
                            "paper_title": data.get("title", ""),
                            "antecedent": finding.get("antecedent", ""),
                            "consequent": finding.get("consequent", ""),
                            "direction": finding.get("direction", ""),
                            "effect_size": finding.get("effect_size"),
                            "sample_size": finding.get("sample_size"),
                            "p_value": finding.get("p_value"),
                            "design_type": finding.get("claim_type", "observational"),
                            "relevance": rel,
                        })
                        designs[finding.get("claim_type", "unknown")] += 1

                if len(papers) >= max_papers:
                    break
            except Exception:
                continue

        findings.sort(key=lambda f: (f["relevance"], abs(f.get("effect_size") or 0)), reverse=True)

        es = [f["effect_size"] for f in findings if f.get("effect_size")]
        ss = [f["sample_size"] for f in findings if f.get("sample_size")]

        return {
            "n_findings": len(findings),
            "n_papers": len(papers),
            "top_findings": findings[:10],
            "design_distribution": dict(designs),
            "summary": {
                "with_effect_size": len(es),
                "with_sample_size": len(ss),
                "median_sample_size": sorted(ss)[len(ss)//2] if ss else None,
            },
        }

    # ------------------------------------------------------------------
    # Internal: card building
    # ------------------------------------------------------------------

    def _build_card(self, mol_id: str, mol: dict, evidence: dict) -> dict:
        name = mol.get("name", mol_id)
        components = mol.get("components", [])
        comp_names = [c.get("name", "") for c in components if isinstance(c, dict)]
        n = evidence["n_findings"]
        np_ = evidence["n_papers"]
        dd = evidence.get("design_distribution", {})
        top_design = max(dd, key=dd.get) if dd else "various"

        # Build L1 summary
        parts = [f"{name} is supported by {n} findings from {np_} papers in the corpus."]
        if comp_names:
            parts.append(f"Components: {', '.join(comp_names)}.")
        if dd:
            parts.append(f"Primary evidence: {top_design} studies ({dd.get(top_design, 0)}/{n}).")
        top = evidence.get("top_findings", [])
        if top:
            f = top[0]
            detail = f"{f.get('antecedent', '')} → {f.get('consequent', '')} ({f.get('direction', 'positive')}"
            if f.get("effect_size"): detail += f", d={f['effect_size']}"
            if f.get("sample_size"): detail += f", N={f['sample_size']}"
            parts.append(f"Key finding: {detail}).")

        return {
            "molecule_id": mol_id.upper(),
            "entity_type": mol.get("molecule_type", "molecule"),
            "name": name,
            "l1_summary": " ".join(parts),
            "l2_summary": "[PENDING — requires LLM via MolecularQAPrecomputer]",
            "l3_summary": "[PENDING — requires LLM via MolecularQAPrecomputer]",
            "dependent_templates": mol.get("constituent_templates", []),
            "components": [
                {"name": c.get("name", ""), "description": c.get("description", "")}
                for c in components if isinstance(c, dict)
            ],
            "evidence": {
                "n_findings": evidence["n_findings"],
                "n_papers": evidence["n_papers"],
                "design_distribution": evidence.get("design_distribution", {}),
                "top_findings": evidence.get("top_findings", [])[:5],
                "summary": evidence.get("summary", {}),
            },
            "last_computed": datetime.now(timezone.utc).isoformat(),
            "kb_hash_at_computation": "",
            "status": "L1_ONLY",
        }

    def _generate_archetype_card(
        self, arch_id: str, arch_info: dict, molecules: Dict[str, dict]
    ) -> dict:
        linked = []
        for mid, mol in molecules.items():
            mol_text = json.dumps(mol).lower()
            if any(alias in mol_text for alias in arch_info["aliases"]):
                linked.append({"molecule_id": mid, "name": mol.get("name", mid)})

        evidence = self._search_corpus(set(arch_info["aliases"]), max_papers=30)

        card = {
            "entity_type": "archetype",
            "archetype_id": arch_id,
            "name": arch_info["name"],
            "l1_summary": (
                f"{arch_info['name']}: {arch_info['description']} "
                f"Found in {len(linked)} molecules. "
                f"Supported by {evidence['n_findings']} findings from {evidence['n_papers']} papers."
            ),
            "l2_summary": "[PENDING — requires LLM]",
            "l3_summary": "[PENDING — requires LLM]",
            "linked_molecules": linked,
            "evidence": {
                "n_findings": evidence["n_findings"],
                "n_papers": evidence["n_papers"],
                "design_distribution": evidence.get("design_distribution", {}),
                "top_findings": evidence.get("top_findings", [])[:5],
            },
            "last_computed": datetime.now(timezone.utc).isoformat(),
            "status": "L1_ONLY",
        }

        path = self._cache_dir / f"ARCHETYPE_{arch_id}_QA.json"
        with open(path, "w") as f:
            json.dump(card, f, indent=2)

        logger.info(f"Archetype card {arch_info['name']}: {len(linked)} molecules, {evidence['n_findings']} findings")
        return card

    # ------------------------------------------------------------------
    # Internal: helpers
    # ------------------------------------------------------------------

    def _load_molecules(self) -> Dict[str, dict]:
        if self._molecules is not None:
            return self._molecules
        self._molecules = {}
        if not self._molecule_dir.exists():
            return self._molecules
        for f in self._molecule_dir.glob("*.json"):
            try:
                with open(f) as fh:
                    data = json.load(fh)
                self._molecules[data.get("molecule_id", f.stem).lower()] = data
            except Exception as e:
                logger.error(f"Failed to load molecule {f}: {e}")
        return self._molecules

    def _molecule_keywords(self, mol: dict) -> Set[str]:
        keywords = set()
        name = mol.get("name", "")
        keywords.add(name.lower())
        for word in re.findall(r'\w+', name.lower()):
            if len(word) > 3:
                keywords.add(word)
        for comp in mol.get("components", []):
            if isinstance(comp, dict):
                keywords.add(comp.get("name", "").lower())
        domain = mol.get("domain", "")
        if domain:
            keywords.add(domain.lower())
        keywords -= {"the", "and", "for", "with", "from", "that", "this", "which",
                      "have", "been", "than", "more", "also", "into"}
        return keywords


# =============================================================================
# CLI
# =============================================================================
if __name__ == "__main__":
    import argparse
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [MOLCARD] %(levelname)s %(message)s")

    parser = argparse.ArgumentParser(description="Generate corpus-grounded L1 molecule cards")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--molecule", type=str, default=None)
    args = parser.parse_args()

    gen = MoleculeCardGenerator()
    if args.molecule:
        card = gen.generate_for_molecule(args.molecule)
        print(json.dumps(card, indent=2))
    else:
        results = gen.generate_all(force=args.force)
        for eid, status in sorted(results.items()):
            sym = "✓" if status == "generated" else "·" if status == "exists" else "✗"
            print(f"  {sym} {eid}: {status}")
        g = sum(1 for s in results.values() if s == "generated")
        e = sum(1 for s in results.values() if s == "exists")
        f = sum(1 for s in results.values() if s == "failed")
        print(f"\nTotal: {g} generated, {e} existed, {f} failed")
