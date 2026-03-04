"""
Follow-Up Suggestion Service
=============================

Generates VOI-ranked follow-up questions for enriched answer cards.

Uses three sources (in priority order):
1. GapPredictor — identifies holes in the evidence base
2. MoleculeRegistry — identifies adjacent molecules worth exploring
3. Extraction corpus — identifies under-explored findings

This replaces the inline template-based fallback that was in the
enrichment orchestrator, which generated generic "what are boundary
conditions" questions without any corpus grounding.

SUCCESS CONDITIONS:
SC-FUS-1: generate_follow_ups returns a list of dicts
SC-FUS-2: Each dict has keys: question, voi, difficulty, source
SC-FUS-3: Results are sorted by VOI descending
SC-FUS-4: Uses GapPredictor when available for corpus-grounded gaps
SC-FUS-5: Uses MoleculeRegistry for "explore adjacent molecule" suggestions
SC-FUS-6: Falls back gracefully to templates only if no data sources available
SC-FUS-7: Respects max_results limit
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class FollowUpSuggestionService:
    """Generates corpus-grounded follow-up questions for enriched answers."""

    def __init__(
        self,
        extractions_dir: str = "data/extractions",
        molecule_dir: str = "data/molecules",
    ):
        self._extractions_dir = Path(extractions_dir)
        self._molecule_dir = Path(molecule_dir)

        # Lazy-loaded services
        self._gap_predictor = None
        self._molecule_registry = None

    @property
    def gap_predictor(self):
        if self._gap_predictor is None:
            try:
                from src.services.gap_predictor import GapPredictor
                self._gap_predictor = GapPredictor()
            except Exception as e:
                logger.debug(f"GapPredictor not available: {e}")
        return self._gap_predictor

    @property
    def molecule_registry(self):
        if self._molecule_registry is None:
            try:
                from src.qa.molecules.registry import MoleculeRegistry
                self._molecule_registry = MoleculeRegistry(
                    molecule_dir=str(self._molecule_dir)
                )
            except Exception as e:
                logger.debug(f"MoleculeRegistry not available: {e}")
        return self._molecule_registry

    def generate_follow_ups(
        self,
        topic: str,
        beliefs: Optional[List[Dict]] = None,
        gaps: Optional[List[Dict]] = None,
        max_results: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Generate VOI-ranked follow-up questions grounded in the corpus.

        Args:
            topic: The topic being answered
            beliefs: Enriched beliefs from the answer card
            gaps: Gap analysis results (if already computed)
            max_results: Maximum number of follow-ups to return

        Returns:
            List of {question, voi, difficulty, source} dicts, VOI-sorted
        """
        follow_ups: List[Dict[str, Any]] = []

        # Source 1: Gap predictor (most valuable — corpus-grounded)
        follow_ups.extend(self._from_gap_predictor(topic, max_results))

        # Source 2: Pre-computed gaps from earlier in the pipeline
        if gaps:
            follow_ups.extend(self._from_existing_gaps(gaps, max_results))

        # Source 3: Adjacent molecules (explore related theories)
        follow_ups.extend(self._from_adjacent_molecules(topic, beliefs, max_results))

        # Source 4: Under-explored findings in the corpus
        follow_ups.extend(self._from_underexplored_findings(topic, beliefs, max_results))

        # Source 5: Templates (always available, lowest priority)
        if len(follow_ups) < max_results:
            follow_ups.extend(self._from_templates(topic, max_results - len(follow_ups)))

        # Deduplicate by question text (case-insensitive)
        seen = set()
        unique = []
        for fu in follow_ups:
            key = fu["question"].lower().strip()
            if key not in seen:
                seen.add(key)
                unique.append(fu)

        # Sort by VOI descending, return top N
        unique.sort(key=lambda x: x.get("voi", 0), reverse=True)
        return unique[:max_results]

    def _from_gap_predictor(self, topic: str, max_n: int) -> List[Dict]:
        """Use GapPredictor to find evidence gaps related to the topic."""
        if not self.gap_predictor:
            return []

        try:
            gap_report = self.gap_predictor.find_all_gaps(max_gaps=max_n)
            results = []
            topic_words = set(re.findall(r'\w+', topic.lower()))
            topic_words -= {"the", "of", "and", "in", "on", "for", "a", "is", "to"}

            for gap in gap_report.gaps:
                gap_text = str(getattr(gap, 'description', '') or getattr(gap, 'gap_type', ''))
                gap_words = set(re.findall(r'\w+', gap_text.lower()))
                # Keep gaps that overlap with the topic
                if topic_words and len(topic_words & gap_words) >= 1:
                    question = getattr(gap, 'question', None) or f"What do we know about {gap_text}?"
                    results.append({
                        "question": question,
                        "voi": getattr(gap, 'voi_score', 0.7),
                        "difficulty": "moderate",
                        "source": "gap_predictor",
                    })
            return results[:max_n]
        except Exception as e:
            logger.debug(f"Gap predictor follow-ups failed: {e}")
            return []

    def _from_existing_gaps(self, gaps: List[Dict], max_n: int) -> List[Dict]:
        """Convert pre-computed gap analysis results to follow-ups."""
        results = []
        for gap in gaps[:max_n]:
            q = gap.get("question") or gap.get("description", "")
            if q:
                results.append({
                    "question": q,
                    "voi": gap.get("voi", 0.6),
                    "difficulty": gap.get("difficulty", "moderate"),
                    "source": "gap_analysis",
                })
        return results

    def _from_adjacent_molecules(
        self, topic: str, beliefs: Optional[List[Dict]], max_n: int
    ) -> List[Dict]:
        """Find molecules adjacent to the topic and suggest exploration."""
        if not self.molecule_registry:
            return []

        try:
            topic_lower = topic.lower()
            results = []

            for mol_id, mol in self.molecule_registry.molecules.items():
                # Skip if this IS the topic
                if mol.name.lower() in topic_lower or topic_lower in mol.name.lower():
                    continue

                # Check for keyword overlap with topic
                mol_words = set(re.findall(r'\w+', mol.name.lower() + " " + mol.short_description.lower()))
                topic_words = set(re.findall(r'\w+', topic_lower))
                topic_words -= {"the", "of", "and", "in", "on", "for", "a", "is", "to"}

                overlap = len(topic_words & mol_words)
                if overlap >= 2:
                    results.append({
                        "question": f"How does {mol.name} relate to {topic}?",
                        "voi": min(0.5 + overlap * 0.1, 0.8),
                        "difficulty": "moderate",
                        "source": "adjacent_molecule",
                        "molecule_id": mol_id,
                    })

            results.sort(key=lambda x: x["voi"], reverse=True)
            return results[:max_n]
        except Exception as e:
            logger.debug(f"Adjacent molecule follow-ups failed: {e}")
            return []

    def _from_underexplored_findings(
        self, topic: str, beliefs: Optional[List[Dict]], max_n: int
    ) -> List[Dict]:
        """Find findings in the corpus that are related but under-explored."""
        if not self._extractions_dir.exists():
            return []

        try:
            topic_words = set(re.findall(r'\w+', topic.lower()))
            topic_words -= {"the", "of", "and", "in", "on", "for", "a", "is", "to"}
            if not topic_words:
                return []

            # Already-answered content (from beliefs)
            covered = set()
            if beliefs:
                for b in beliefs:
                    if isinstance(b, dict):
                        stmt = b.get("statement", "") or b.get("content", "")
                        covered.update(re.findall(r'\w+', stmt.lower()))

            results = []
            for json_file in sorted(self._extractions_dir.glob("*.json"))[:300]:
                if len(results) >= max_n:
                    break
                try:
                    with open(json_file) as f:
                        data = json.load(f)

                    title = (data.get("title") or "").lower()
                    if len(topic_words & set(re.findall(r'\w+', title))) < 2:
                        continue

                    for finding in data.get("findings", []):
                        ant = (finding.get("antecedent") or "").lower()
                        con = (finding.get("consequent") or "").lower()
                        finding_words = set(re.findall(r'\w+', ant + " " + con))

                        # Must overlap with topic but NOT with already-covered content
                        topic_overlap = len(topic_words & finding_words)
                        covered_overlap = len(covered & finding_words) if covered else 0

                        if topic_overlap >= 2 and covered_overlap < 3:
                            q = f"What is the relationship between {finding.get('antecedent', '')} and {finding.get('consequent', '')}?"
                            results.append({
                                "question": q,
                                "voi": 0.55,
                                "difficulty": "moderate",
                                "source": "underexplored_finding",
                                "paper": data.get("title", json_file.stem),
                            })
                except Exception:
                    continue

            return results[:max_n]
        except Exception as e:
            logger.debug(f"Underexplored findings search failed: {e}")
            return []

    def _from_templates(self, topic: str, n: int) -> List[Dict]:
        """Last-resort templates — always available."""
        templates = [
            ("What are the boundary conditions where {topic} does NOT hold?",
             0.45, "moderate"),
            ("What competing theories explain the same phenomena as {topic}?",
             0.40, "moderate"),
            ("What is the strongest evidence against {topic}?",
             0.42, "hard"),
            ("How does {topic} interact with individual differences (age, culture, expertise)?",
             0.35, "moderate"),
            ("What mechanisms explain WHY {topic} works at the neural level?",
             0.38, "hard"),
        ]
        results = []
        for tmpl, voi, diff in templates[:n]:
            results.append({
                "question": tmpl.format(topic=topic),
                "voi": voi,
                "difficulty": diff,
                "source": "template",
            })
        return results
