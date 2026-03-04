"""
Answer Card Generator — Render Norm-Compliant Cards from Belief Clusters
=========================================================================

Reads belief_clusters.json and generates pre-computed answer cards
for each cluster × user_type. Each card includes:
  - Norm-compliant prose (per user type rendering constraints)
  - Confidence thermometer (ATLAS palette, 4 levels)
  - Direction consensus and evidence stats
  - Theory links

Pipeline:
  belief_clusters.json → card_generator.py → answer_cards/

Tracks:
  - Wall-clock time per card
  - Total generation time
  - Cards per second throughput
  - Storage per user type

Usage:
    generator = CardGenerator()
    stats = generator.run()
    print(f"Generated {stats['total_cards']} cards in {stats['elapsed_seconds']:.1f}s")
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.qa.answer_renderer import (
    AnswerRenderer,
    ConfidenceLevel,
    USER_TYPE_CONFIGS,
    build_thermometer,
    compute_confidence_level,
    CONFIDENCE_LANGUAGE,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Card data model
# ---------------------------------------------------------------------------

@dataclass
class AnswerCard:
    """A single pre-computed answer card for one cluster + one user type."""
    cluster_id: str
    antecedent_theme: str
    consequent_theme: str
    user_type: str
    prose: str
    confidence_level: str         # high | mod_high | moderate | low
    confidence_label: str         # "Mod-High (ω = 0.62)"
    confidence_color: str         # ATLAS color hex
    direction_consensus: str      # increase | decrease | mixed | no_effect
    n_findings: int
    n_papers: int
    theory_links: List[str]
    word_count: int
    quality_score: float

    def to_dict(self) -> Dict:
        return {
            "cluster_id": self.cluster_id,
            "antecedent_theme": self.antecedent_theme,
            "consequent_theme": self.consequent_theme,
            "user_type": self.user_type,
            "prose": self.prose,
            "confidence": {
                "level": self.confidence_level,
                "label": self.confidence_label,
                "color": self.confidence_color,
            },
            "direction_consensus": self.direction_consensus,
            "n_findings": self.n_findings,
            "n_papers": self.n_papers,
            "theory_links": self.theory_links,
            "word_count": self.word_count,
            "quality_score": round(self.quality_score, 3),
        }


# ---------------------------------------------------------------------------
# Card Generator Pipeline
# ---------------------------------------------------------------------------

class CardGenerator:
    """
    Generates answer cards from belief clusters.

    Reads belief_clusters.json, renders cards per cluster × user_type,
    saves to data/materialized_views/answer_cards/.
    """

    # User types to generate cards for
    USER_TYPES = [
        "general_public", "student", "clinician",
        "architect_designer", "researcher", "deep_researcher",
    ]

    def __init__(
        self,
        clusters_path: str = "data/materialized_views/belief_clusters.json",
        output_dir: str = "data/materialized_views/answer_cards",
        min_findings: int = 2,
    ):
        self._clusters_path = Path(clusters_path)
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)
        self._min_findings = min_findings
        self._renderer = AnswerRenderer()

    def run(self, max_clusters: int = 0) -> Dict[str, Any]:
        """
        Generate all answer cards.

        Args:
            max_clusters: If > 0, only process this many clusters (for testing).

        Returns:
            Stats dict with timing, counts, storage info.
        """
        start = time.time()

        # Load clusters
        with open(self._clusters_path) as f:
            data = json.load(f)
        clusters = data.get("clusters", [])
        logger.info(f"Loaded {len(clusters)} clusters")

        if max_clusters > 0:
            clusters = clusters[:max_clusters]

        # Generate cards
        all_cards: List[AnswerCard] = []
        per_type_stats: Dict[str, Dict] = {t: {"count": 0, "total_words": 0} for t in self.USER_TYPES}
        card_times: List[float] = []

        for i, cluster in enumerate(clusters):
            if cluster.get("n_findings", 0) < self._min_findings:
                continue

            for user_type in self.USER_TYPES:
                card_start = time.time()
                card = self._generate_card(cluster, user_type)
                card_time = time.time() - card_start
                card_times.append(card_time)

                all_cards.append(card)
                per_type_stats[user_type]["count"] += 1
                per_type_stats[user_type]["total_words"] += card.word_count

            if (i + 1) % 500 == 0:
                elapsed = time.time() - start
                rate = len(all_cards) / elapsed
                logger.info(
                    f"  Progress: {i+1}/{len(clusters)} clusters, "
                    f"{len(all_cards)} cards, {rate:.0f} cards/s"
                )

        elapsed = time.time() - start

        # Save cards (one file per user type for fast retrieval)
        storage_bytes = self._save_cards(all_cards)

        # Compile stats
        stats = {
            "total_clusters_processed": len(set(c.cluster_id for c in all_cards)),
            "total_cards": len(all_cards),
            "user_types": len(self.USER_TYPES),
            "elapsed_seconds": round(elapsed, 2),
            "cards_per_second": round(len(all_cards) / max(elapsed, 0.001), 1),
            "avg_card_time_ms": round(
                (sum(card_times) / len(card_times) * 1000) if card_times else 0, 2
            ),
            "storage_bytes": storage_bytes,
            "storage_mb": round(storage_bytes / (1024 * 1024), 2),
            "per_user_type": {
                t: {
                    "cards": s["count"],
                    "avg_words": round(s["total_words"] / max(s["count"], 1)),
                }
                for t, s in per_type_stats.items()
            },
        }

        # Save stats
        stats_path = self._output_dir / "generation_stats.json"
        with open(stats_path, "w") as f:
            json.dump(stats, f, indent=2)
        logger.info(
            f"Generated {stats['total_cards']} cards in {elapsed:.1f}s "
            f"({stats['cards_per_second']} cards/s, {stats['storage_mb']} MB)"
        )

        return stats

    def _generate_card(self, cluster: Dict, user_type: str) -> AnswerCard:
        """Generate a single answer card for one cluster + user type."""
        config = USER_TYPE_CONFIGS.get(user_type, USER_TYPE_CONFIGS["researcher"])

        # Build evidence data from cluster
        members = cluster.get("sample_members", [])
        evidence_data = {
            "findings": [
                {
                    "antecedent": m.get("antecedent", ""),
                    "consequent": m.get("consequent", ""),
                    "direction": m.get("direction", ""),
                    "source_file": m.get("source", ""),
                }
                for m in members
            ]
        }

        # Estimate omega from cluster stats
        n_findings = cluster.get("n_findings", 0)
        n_papers = cluster.get("n_papers", 0)
        direction_counts = cluster.get("direction_counts", {})
        consensus = cluster.get("direction_consensus", "unknown")

        # Heuristic omega: more findings + papers + consensus = higher
        consensus_ratio = max(direction_counts.values()) / max(sum(direction_counts.values()), 1) if direction_counts else 0
        omega_estimate = min(1.0, (
            0.3 * min(n_findings / 50, 1.0) +   # Volume: 50 findings → max
            0.3 * min(n_papers / 20, 1.0) +      # Breadth: 20 papers → max
            0.4 * consensus_ratio                  # Consensus: higher = better
        ))

        omega_scores = {
            "scores": [{"omega_total": omega_estimate}]
        }

        # Use the renderer
        ant_theme = cluster.get("antecedent_theme", "unknown")
        cons_theme = cluster.get("consequent_theme", "unknown")
        rendered = self._renderer.render(
            topic_cluster=f"{ant_theme}_to_{cons_theme}",
            evidence_data=evidence_data,
            omega_scores=omega_scores,
            user_type=user_type,
        )

        return AnswerCard(
            cluster_id=cluster.get("cluster_id", ""),
            antecedent_theme=ant_theme,
            consequent_theme=cons_theme,
            user_type=user_type,
            prose=rendered.prose,
            confidence_level=rendered.thermometer.level.value,
            confidence_label=rendered.thermometer.label,
            confidence_color=rendered.thermometer.color,
            direction_consensus=consensus,
            n_findings=n_findings,
            n_papers=n_papers,
            theory_links=cluster.get("theory_links", []),
            word_count=rendered.word_count,
            quality_score=rendered.quality_score,
        )

    def _save_cards(self, cards: List[AnswerCard]) -> int:
        """
        Save cards organized by user type (one file per type for fast retrieval).

        Returns total bytes written.
        """
        total_bytes = 0

        # Group by user type
        by_type: Dict[str, List[Dict]] = {t: [] for t in self.USER_TYPES}
        for card in cards:
            by_type[card.user_type].append(card.to_dict())

        for user_type, type_cards in by_type.items():
            output_path = self._output_dir / f"cards_{user_type}.json"
            content = {
                "user_type": user_type,
                "n_cards": len(type_cards),
                "cards": type_cards,
            }
            with open(output_path, "w") as f:
                json.dump(content, f, indent=1, ensure_ascii=False)
            file_size = output_path.stat().st_size
            total_bytes += file_size
            logger.info(f"  {user_type}: {len(type_cards)} cards, {file_size/1024:.0f} KB")

        # Also save a master index for fast lookup by cluster_id
        index = {}
        for card in cards:
            if card.cluster_id not in index:
                index[card.cluster_id] = {
                    "antecedent": card.antecedent_theme,
                    "consequent": card.consequent_theme,
                    "confidence_level": card.confidence_level,
                    "n_findings": card.n_findings,
                    "n_papers": card.n_papers,
                    "user_types": [],
                }
            index[card.cluster_id]["user_types"].append(card.user_type)

        index_path = self._output_dir / "card_index.json"
        with open(index_path, "w") as f:
            json.dump(index, f, indent=1)
        total_bytes += index_path.stat().st_size

        return total_bytes
