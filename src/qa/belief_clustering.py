"""
Belief Clustering Pipeline — Group 33K Findings into Topic Clusters
=====================================================================

Clusters raw extraction findings by (antecedent_theme × consequent_theme)
pairs using keyword-based similarity. Produces ~300-800 clusters, each
representing "what the evidence says about X → Y".

Each cluster becomes the basis for a pre-computed answer card.

Pipeline stages:
  1. Load all findings from data/extractions/
  2. Normalize antecedent/consequent terms
  3. Cluster by similarity (keyword overlap + theory link overlap)
  4. Merge near-duplicate clusters
  5. Compute cluster-level statistics (n papers, omega, direction consensus)
  6. Save clusters to data/materialized_views/belief_clusters.json

Usage:
    pipeline = BeliefClusteringPipeline()
    clusters = pipeline.run()
    print(f"Grouped {pipeline.total_findings} findings into {len(clusters)} clusters")
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Term normalization
# ---------------------------------------------------------------------------

# Common synonym groups for antecedent/consequent normalization
TERM_SYNONYMS = {
    # Lighting
    "daylight": "natural_light", "natural light": "natural_light",
    "sunlight": "natural_light", "daylighting": "natural_light",
    "artificial light": "artificial_light", "electric light": "artificial_light",
    "fluorescent": "artificial_light",
    "colour temperature": "color_temperature", "color temperature": "color_temperature",
    "correlated colour temperature": "color_temperature",
    "illuminance": "light_level", "illumination": "light_level",
    "luminance": "light_level", "lux": "light_level",

    # Nature / greenery
    "vegetation": "greenery", "plants": "greenery", "greenness": "greenery",
    "green space": "green_space", "park": "green_space", "garden": "green_space",
    "tree": "trees", "trees": "trees", "street tree": "trees",
    "nature": "nature_exposure", "natural environment": "nature_exposure",
    "biophilic": "biophilic_design", "biophilic design": "biophilic_design",

    # Views / windows
    "window": "window_view", "window view": "window_view",
    "view": "window_view", "outlook": "window_view",

    # Thermal
    "temperature": "thermal", "thermal comfort": "thermal",
    "heat": "thermal", "cold": "thermal",

    # Acoustics
    "noise": "noise", "sound": "sound_environment",
    "acoustic": "acoustic_quality", "soundscape": "sound_environment",

    # Space
    "ceiling height": "ceiling_height", "room height": "ceiling_height",
    "open plan": "open_plan", "open-plan": "open_plan",
    "enclosure": "spatial_enclosure", "openness": "spatial_openness",
    "spatial layout": "spatial_layout", "floor plan": "spatial_layout",
    "density": "density", "crowding": "density",

    # Outcomes
    "stress": "stress", "cortisol": "stress",
    "anxiety": "anxiety",
    "mood": "mood", "affect": "mood", "positive affect": "mood",
    "wellbeing": "wellbeing", "well-being": "wellbeing",
    "satisfaction": "satisfaction", "preference": "preference",
    "comfort": "comfort",
    "productivity": "productivity", "performance": "performance",
    "task performance": "performance",
    "cognitive": "cognitive_performance", "attention": "cognitive_performance",
    "concentration": "cognitive_performance", "focus": "cognitive_performance",
    "creativity": "creativity",
    "sleep": "sleep_quality", "circadian": "circadian",
    "restoration": "restoration", "restorative": "restoration",
    "wayfinding": "wayfinding", "navigation": "wayfinding",
    "depression": "depression",
    "pain": "pain",
    "healing": "healing", "recovery": "healing",
    "social": "social_behavior", "interaction": "social_behavior",
    "privacy": "privacy",
}

STOP_WORDS = frozenset([
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "of", "in", "to", "for", "with", "on", "at", "by", "from", "and",
    "but", "or", "not", "that", "this", "it", "its", "do", "does", "did",
    "will", "would", "could", "should", "can", "may", "might", "has", "have",
    "had", "more", "less", "than", "very", "most", "also", "other", "such",
    "each", "all", "both", "some", "any", "these", "those", "no", "non",
    "vs", "between", "during", "after", "before", "while",
])


def normalize_term(text: str) -> str:
    """Normalize a finding term to a canonical form."""
    text = text.lower().strip()
    # Check full-phrase synonyms first
    for phrase, norm in TERM_SYNONYMS.items():
        if phrase in text:
            return norm
    # Extract meaningful words
    words = re.findall(r'[a-z]+', text)
    words = [w for w in words if w not in STOP_WORDS and len(w) >= 3]
    # Check individual word synonyms
    for i, w in enumerate(words):
        if w in TERM_SYNONYMS:
            words[i] = TERM_SYNONYMS[w]
    return "_".join(sorted(set(words[:4])))  # max 4 terms, sorted for consistency


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class ClusterMember:
    """A single finding that belongs to a cluster."""
    antecedent: str
    consequent: str
    direction: str
    source_file: str
    theory_links: List[str] = field(default_factory=list)
    p_value: Optional[str] = None
    effect_size: Optional[float] = None
    article_type: str = "unknown"
    sample_size: Optional[int] = None


@dataclass
class BeliefCluster:
    """A group of related findings forming a single evidence cluster."""
    cluster_id: str
    antecedent_theme: str        # Normalized antecedent
    consequent_theme: str        # Normalized consequent
    members: List[ClusterMember] = field(default_factory=list)

    # Computed stats
    n_findings: int = 0
    n_papers: int = 0
    direction_consensus: str = ""  # "increase", "decrease", "mixed", "no_effect"
    direction_counts: Dict[str, int] = field(default_factory=dict)
    theory_links: List[str] = field(default_factory=list)
    mean_effect_size: Optional[float] = None
    article_types: Dict[str, int] = field(default_factory=dict)

    def compute_stats(self):
        """Compute cluster-level statistics from members."""
        self.n_findings = len(self.members)
        self.n_papers = len(set(m.source_file for m in self.members))

        # Direction consensus
        dir_counts = Counter(m.direction for m in self.members if m.direction)
        self.direction_counts = dict(dir_counts)
        if dir_counts:
            most_common = dir_counts.most_common(1)[0]
            total = sum(dir_counts.values())
            if most_common[1] / total >= 0.6:
                self.direction_consensus = most_common[0]
            else:
                self.direction_consensus = "mixed"
        else:
            self.direction_consensus = "unknown"

        # Theory links
        all_theories = Counter()
        for m in self.members:
            all_theories.update(m.theory_links)
        self.theory_links = [t for t, _ in all_theories.most_common(5)]

        effects = []
        for m in self.members:
            if m.effect_size is not None:
                try:
                    effects.append(float(m.effect_size))
                except (ValueError, TypeError):
                    pass
        self.mean_effect_size = sum(effects) / len(effects) if effects else None

        # Article types
        self.article_types = dict(Counter(m.article_type for m in self.members))

    def to_dict(self) -> Dict:
        self.compute_stats()
        return {
            "cluster_id": self.cluster_id,
            "antecedent_theme": self.antecedent_theme,
            "consequent_theme": self.consequent_theme,
            "n_findings": self.n_findings,
            "n_papers": self.n_papers,
            "direction_consensus": self.direction_consensus,
            "direction_counts": self.direction_counts,
            "theory_links": self.theory_links,
            "mean_effect_size": self.mean_effect_size,
            "article_types": self.article_types,
            "sample_members": [
                {
                    "antecedent": m.antecedent[:100],
                    "consequent": m.consequent[:100],
                    "direction": m.direction,
                    "source": m.source_file,
                }
                for m in self.members[:5]  # Save space: only first 5 examples
            ],
        }


# ---------------------------------------------------------------------------
# Clustering Pipeline
# ---------------------------------------------------------------------------

class BeliefClusteringPipeline:
    """
    Groups 33K findings into evidence clusters.

    Each cluster represents one (antecedent_theme → consequent_theme) pair
    with aggregated statistics across all papers.
    """

    def __init__(
        self,
        extractions_dir: str = "data/extractions",
        output_dir: str = "data/materialized_views",
        min_cluster_size: int = 2,
    ):
        self._extractions_dir = Path(extractions_dir)
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)
        self._min_cluster_size = min_cluster_size
        self.total_findings = 0
        self.total_clustered = 0

    def run(self) -> List[BeliefCluster]:
        """
        Run the full clustering pipeline.

        Returns:
            List of BeliefClusters, each with computed stats.
        """
        start = time.time()
        logger.info("Starting belief clustering pipeline...")

        # Stage 1: Load all findings
        findings = self._load_all_findings()
        self.total_findings = len(findings)
        logger.info(f"Stage 1: Loaded {len(findings)} findings")

        # Stage 2: Normalize and assign cluster keys
        cluster_map = self._cluster_findings(findings)
        logger.info(f"Stage 2: Created {len(cluster_map)} raw clusters")

        # Stage 3: Merge near-duplicate clusters
        merged = self._merge_similar_clusters(cluster_map)
        logger.info(f"Stage 3: Merged into {len(merged)} clusters")

        # Stage 4: Filter by minimum size and compute stats
        clusters = []
        for cluster in merged.values():
            cluster.compute_stats()
            if cluster.n_findings >= self._min_cluster_size:
                clusters.append(cluster)
            else:
                # Singletons go into an "other" bucket
                pass

        # Sort by size (largest first)
        clusters.sort(key=lambda c: c.n_findings, reverse=True)
        self.total_clustered = sum(c.n_findings for c in clusters)

        elapsed = time.time() - start
        logger.info(
            f"Pipeline complete: {self.total_findings} findings → "
            f"{len(clusters)} clusters ({self.total_clustered} clustered) "
            f"in {elapsed:.1f}s"
        )

        # Stage 5: Save results
        self._save_clusters(clusters, elapsed)

        return clusters

    # ------------------------------------------------------------------
    # Pipeline stages
    # ------------------------------------------------------------------

    def _load_all_findings(self) -> List[Dict]:
        """Load all findings from extraction JSON files."""
        findings = []
        for json_file in self._extractions_dir.glob("*.json"):
            try:
                with open(json_file) as f:
                    data = json.load(f)
                article_type = data.get("article_type", "unknown")
                sample_size = data.get("n_participants")

                for finding in data.get("findings", []):
                    ant = finding.get("antecedent", "").strip()
                    cons = finding.get("consequent", "").strip()
                    if not ant or not cons:
                        continue
                    findings.append({
                        "antecedent": ant,
                        "consequent": cons,
                        "direction": finding.get("direction", ""),
                        "theory_links": finding.get("theory_links", []),
                        "p_value": finding.get("p_value"),
                        "effect_size": finding.get("effect_size"),
                        "source_file": json_file.stem,
                        "article_type": article_type,
                        "sample_size": sample_size,
                    })
            except Exception:
                continue
        return findings

    def _cluster_findings(self, findings: List[Dict]) -> Dict[str, BeliefCluster]:
        """Assign findings to clusters by normalized (ant, cons) key."""
        cluster_map: Dict[str, BeliefCluster] = {}

        for f in findings:
            ant_norm = normalize_term(f["antecedent"])
            cons_norm = normalize_term(f["consequent"])

            if not ant_norm or not cons_norm:
                continue

            cluster_key = f"{ant_norm}|{cons_norm}"
            cluster_id = hashlib.md5(cluster_key.encode()).hexdigest()[:12]

            if cluster_key not in cluster_map:
                cluster_map[cluster_key] = BeliefCluster(
                    cluster_id=cluster_id,
                    antecedent_theme=ant_norm,
                    consequent_theme=cons_norm,
                )

            cluster_map[cluster_key].members.append(ClusterMember(
                antecedent=f["antecedent"],
                consequent=f["consequent"],
                direction=f["direction"],
                source_file=f["source_file"],
                theory_links=f.get("theory_links", []),
                p_value=f.get("p_value"),
                effect_size=f.get("effect_size"),
                article_type=f.get("article_type", "unknown"),
                sample_size=f.get("sample_size"),
            ))

        return cluster_map

    def _merge_similar_clusters(
        self, cluster_map: Dict[str, BeliefCluster]
    ) -> Dict[str, BeliefCluster]:
        """
        Merge clusters with similar themes using inverted token index.

        Uses token→cluster_keys index to find candidates in O(n) instead of O(n²).
        Two clusters merge if their antecedent AND consequent themes
        share > 50% of normalized tokens.
        """
        # Build inverted index: token → set of cluster keys containing it
        ant_index: Dict[str, Set[str]] = defaultdict(set)
        cons_index: Dict[str, Set[str]] = defaultdict(set)

        for key, cluster in cluster_map.items():
            for token in cluster.antecedent_theme.split("_"):
                if len(token) >= 3:
                    ant_index[token].add(key)
            for token in cluster.consequent_theme.split("_"):
                if len(token) >= 3:
                    cons_index[token].add(key)

        # Use Union-Find for efficient merging
        parent: Dict[str, str] = {k: k for k in cluster_map}

        def find(x: str) -> str:
            while parent[x] != x:
                parent[x] = parent[parent[x]]  # path compression
                x = parent[x]
            return x

        def union(a: str, b: str):
            ra, rb = find(a), find(b)
            if ra != rb:
                # Merge smaller into larger
                if len(cluster_map[ra].members) >= len(cluster_map[rb].members):
                    parent[rb] = ra
                else:
                    parent[ra] = rb

        # For each cluster, find candidates via shared tokens (O(n) average)
        for key_i, cluster_i in cluster_map.items():
            ant_i = set(cluster_i.antecedent_theme.split("_"))
            cons_i = set(cluster_i.consequent_theme.split("_"))

            # Find candidate clusters that share antecedent tokens
            ant_candidates: Set[str] = set()
            for token in ant_i:
                if len(token) >= 3:
                    ant_candidates.update(ant_index.get(token, set()))

            # For each candidate, check both ant AND cons overlap
            for key_j in ant_candidates:
                if key_j <= key_i:  # avoid duplicate checks
                    continue
                if find(key_i) == find(key_j):  # already merged
                    continue

                cluster_j = cluster_map[key_j]
                ant_j = set(cluster_j.antecedent_theme.split("_"))
                cons_j = set(cluster_j.consequent_theme.split("_"))

                ant_overlap = len(ant_i & ant_j) / max(len(ant_i | ant_j), 1)
                cons_overlap = len(cons_i & cons_j) / max(len(cons_i | cons_j), 1)

                if ant_overlap > 0.5 and cons_overlap > 0.5:
                    union(key_i, key_j)

        # Collect merged clusters
        groups: Dict[str, BeliefCluster] = {}
        for key in cluster_map:
            root = find(key)
            if root not in groups:
                groups[root] = BeliefCluster(
                    cluster_id=cluster_map[root].cluster_id,
                    antecedent_theme=cluster_map[root].antecedent_theme,
                    consequent_theme=cluster_map[root].consequent_theme,
                )
            groups[root].members.extend(cluster_map[key].members)

        return groups

    def _save_clusters(self, clusters: List[BeliefCluster], elapsed: float):
        """Save clusters to JSON file."""
        output = {
            "total_findings": self.total_findings,
            "total_clustered": self.total_clustered,
            "n_clusters": len(clusters),
            "compute_time_seconds": round(elapsed, 2),
            "clusters": [c.to_dict() for c in clusters],
        }

        output_path = self._output_dir / "belief_clusters.json"
        with open(output_path, "w") as f:
            json.dump(output, f, indent=2, default=str)
        logger.info(f"Saved {len(clusters)} clusters to {output_path}")

        # Also save summary stats
        summary = {
            "total_findings": self.total_findings,
            "total_clustered": self.total_clustered,
            "n_clusters": len(clusters),
            "top_20_clusters": [
                {
                    "id": c.cluster_id,
                    "theme": f"{c.antecedent_theme} → {c.consequent_theme}",
                    "n_findings": c.n_findings,
                    "n_papers": c.n_papers,
                    "consensus": c.direction_consensus,
                    "theories": c.theory_links[:3],
                }
                for c in clusters[:20]
            ],
            "size_distribution": {
                "2-5": sum(1 for c in clusters if 2 <= c.n_findings <= 5),
                "6-10": sum(1 for c in clusters if 6 <= c.n_findings <= 10),
                "11-20": sum(1 for c in clusters if 11 <= c.n_findings <= 20),
                "21-50": sum(1 for c in clusters if 21 <= c.n_findings <= 50),
                "51+": sum(1 for c in clusters if c.n_findings > 50),
            },
        }
        summary_path = self._output_dir / "cluster_summary.json"
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2)
