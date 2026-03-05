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

Success Conditions (SC-CRED):
    SC-CRED-1: Every cluster has a cluster_credence value (or None with reason)
    SC-CRED-2: Credence is in [0.05, 0.95] range (no false certainty)
    SC-CRED-3: Mixed-direction clusters have credence pulled toward 0.5
    SC-CRED-4: Per-finding credence uses full formula when d+N+p available
    SC-CRED-5: Aggregation is inverse-variance weighted, paper-clustered
    SC-CRED-6: credence_band matches ConfidenceLevel enum values
    SC-CRED-7: credence_data_tier reports which tier drove the estimate
    SC-CRED-8: Cluster credence flows through to card enrichment
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

# Effect size sanity bounds — values outside are extraction errors
EFFECT_SIZE_CAP = 5.0


def _article_type_omega(article_type: str) -> float:
    """Heuristic omega (warrant strength) from article type.

    This is a coarse stand-in for the full warrant_strength.py computation
    when we lack design-level metadata (randomization, blinding, etc.).
    Maps directly from article_type strings found in extractions.
    """
    at = (article_type or "unknown").lower()
    omega_map = {
        "meta-analysis": 0.90,
        "meta_analysis": 0.90,
        "systematic_review": 0.85,
        "systematic-review": 0.85,
        "rct": 0.80,
        "randomized_controlled_trial": 0.80,
        "experimental": 0.75,
        "quasi-experimental": 0.65,
        "quasi_experimental": 0.65,
        "longitudinal": 0.65,
        "cross-sectional": 0.55,
        "cross_sectional": 0.55,
        "observational": 0.55,
        "correlational": 0.50,
        "survey": 0.50,
        "case_study": 0.40,
        "case-study": 0.40,
        "review": 0.60,
        "theoretical": 0.45,
        "commentary": 0.35,
        "unknown": 0.50,
    }
    return omega_map.get(at, 0.50)


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
    mechanism: Optional[str] = None
    evidence_type: Optional[str] = None
    measure_type: Optional[str] = None
    claim_type: Optional[str] = None


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
    median_effect_size: Optional[float] = None
    effect_size_iqr: Optional[Tuple[float, float]] = None
    n_with_effect_size: int = 0
    n_with_sample_size: int = 0
    n_effect_capped: int = 0       # How many effect sizes were capped
    i_squared: Optional[float] = None  # Meta-analytic heterogeneity
    direction_entropy: float = 0.0
    article_types: Dict[str, int] = field(default_factory=dict)
    # Credence aggregation (Phase 7)
    cluster_credence: Optional[float] = None       # Aggregated credence [0, 1]
    credence_uncertainty: Optional[float] = None    # Pooled uncertainty
    credence_band: str = ""                         # HIGH/MOD_HIGH/MODERATE/LOW
    credence_n_inputs: int = 0                      # Findings that contributed
    credence_data_tier: str = ""                    # Which tier drove the credence

    def compute_stats(self):
        """Compute cluster-level statistics from members.

        Fixes applied:
          - Effect sizes capped at [-5, +5]
          - Uses median, not mean
          - Computes I² heterogeneity where possible
          - Computes direction entropy
        """
        import math

        self.n_findings = len(self.members)
        self.n_papers = len(set(m.source_file for m in self.members))

        # Direction consensus + entropy
        dir_counts = Counter(m.direction for m in self.members if m.direction)
        self.direction_counts = dict(dir_counts)
        total_dirs = sum(dir_counts.values())
        if dir_counts and total_dirs > 0:
            most_common = dir_counts.most_common(1)[0]
            if most_common[1] / total_dirs >= 0.6:
                self.direction_consensus = most_common[0]
            else:
                self.direction_consensus = "mixed"
            # Shannon entropy of direction distribution
            probs = [c / total_dirs for c in dir_counts.values()]
            self.direction_entropy = -sum(p * math.log2(p) for p in probs if p > 0)
        else:
            self.direction_consensus = "unknown"
            self.direction_entropy = 0.0

        # Theory links
        all_theories = Counter()
        for m in self.members:
            all_theories.update(m.theory_links)
        self.theory_links = [t for t, _ in all_theories.most_common(5)]

        # Effect sizes: cap at [-5, +5], use median
        raw_effects = []
        capped = 0
        for m in self.members:
            if m.effect_size is not None:
                try:
                    d = float(m.effect_size)
                    if abs(d) > EFFECT_SIZE_CAP:
                        capped += 1
                        d = max(-EFFECT_SIZE_CAP, min(EFFECT_SIZE_CAP, d))
                    raw_effects.append(d)
                except (ValueError, TypeError):
                    pass
        self.n_with_effect_size = len(raw_effects)
        self.n_effect_capped = capped
        if raw_effects:
            raw_effects.sort()
            mid = len(raw_effects) // 2
            self.median_effect_size = raw_effects[mid] if len(raw_effects) % 2 else \
                (raw_effects[mid - 1] + raw_effects[mid]) / 2
            q1 = raw_effects[len(raw_effects) // 4]
            q3 = raw_effects[3 * len(raw_effects) // 4]
            self.effect_size_iqr = (round(q1, 3), round(q3, 3))
        else:
            self.median_effect_size = None
            self.effect_size_iqr = None

        # Sample size stats
        self.n_with_sample_size = sum(
            1 for m in self.members if m.sample_size is not None
        )

        # I² heterogeneity (requires ≥3 findings with d + N)
        self.i_squared = self._compute_i_squared()

        # Cluster-level credence (Phase 7)
        self._compute_cluster_credence()

        # Article types
        self.article_types = dict(Counter(m.article_type for m in self.members))

    def _compute_i_squared(self) -> Optional[float]:
        """Compute I² heterogeneity statistic.

        I² = max(0, (Q - (k-1)) / Q) * 100
        where Q = Σ w_i * (d_i - d_pooled)²
        and w_i = 1 / SE_i²
        and SE_i ≈ √(4/N_i + d_i²/(2*N_i))

        Returns None if fewer than 3 findings have both d and N.
        """
        pairs = []  # (d, n) pairs
        for m in self.members:
            if m.effect_size is not None and m.sample_size is not None:
                try:
                    d = float(m.effect_size)
                    n = int(m.sample_size)
                    if n > 1 and abs(d) <= EFFECT_SIZE_CAP:
                        pairs.append((d, n))
                except (ValueError, TypeError):
                    pass
        if len(pairs) < 3:
            return None

        # Compute weights and pooled d
        weights = []
        for d, n in pairs:
            se_sq = 4.0 / n + d * d / (2.0 * n)
            if se_sq > 0:
                weights.append(1.0 / se_sq)
            else:
                weights.append(0.0)

        total_w = sum(weights)
        if total_w == 0:
            return None

        d_pooled = sum(w * d for w, (d, _) in zip(weights, pairs)) / total_w
        q_stat = sum(w * (d - d_pooled) ** 2 for w, (d, _) in zip(weights, pairs))
        k = len(pairs)
        if q_stat == 0:
            return 0.0
        return max(0.0, (q_stat - (k - 1)) / q_stat) * 100.0

    def _compute_cluster_credence(self):
        """Compute cluster-level credence via tiered per-finding estimation
        and inverse-variance weighted aggregation.

        Tiered per-finding credence:
          Tier A (full formula):  has effect_size + sample_size + p_value
                                 logit(p_target) = d · ω · δ · logit(p_lab)
          Tier B (p-value only):  derive p_lab from significance, use defaults
          Tier C (direction only): heuristic baseline from direction consensus

        Aggregation: inverse-variance weighted average, clustered by paper
        (per edge_justification.py D1-2), with heterogeneity penalty.
        """
        import math

        # --- Step 1: Compute per-finding credence + uncertainty ---
        finding_credences = []  # (credence, uncertainty, source_file, tier)

        for m in self.members:
            cred, unc, tier = self._finding_credence(m)
            if cred is not None:
                finding_credences.append((cred, unc, m.source_file, tier))

        if not finding_credences:
            self.cluster_credence = None
            self.credence_uncertainty = None
            self.credence_band = "unknown"
            self.credence_n_inputs = 0
            self.credence_data_tier = "none"
            return

        # --- Step 2: Cluster by paper (Pearl D0a) ---
        paper_groups: Dict[str, list] = {}
        for cred, unc, src, tier in finding_credences:
            paper_groups.setdefault(src, []).append((cred, unc, tier))

        # Take highest-credence finding per paper (per edge_justification.py)
        representatives = []
        for src, entries in paper_groups.items():
            best = max(entries, key=lambda x: x[0])
            representatives.append(best)

        # --- Step 3: Inverse-variance weighted aggregation ---
        weights = []
        creds = []
        for cred, unc, tier in representatives:
            var = max(unc ** 2, 0.01)  # floor to prevent div-by-zero
            weights.append(1.0 / var)
            creds.append(cred)

        total_w = sum(weights)
        if total_w == 0:
            agg = sum(creds) / len(creds)
            agg_unc = 0.5
        else:
            agg = sum(w * c for w, c in zip(weights, creds)) / total_w
            agg_unc = (1.0 / total_w) ** 0.5

        # --- Step 4: Heterogeneity penalty ---
        # Mixed-direction clusters get credence pulled toward 0.5
        if self.direction_entropy > 0:
            max_entropy = math.log2(max(len(self.direction_counts), 2))
            penalty = self.direction_entropy / max_entropy if max_entropy > 0 else 0
            # penalty ∈ [0, 1]; at 1 (max disagreement), credence → 0.5
            agg = agg * (1 - penalty) + 0.5 * penalty
            agg_unc = min(1.0, agg_unc + penalty * 0.2)

        # Clamp to [0.05, 0.95]
        agg = max(0.05, min(0.95, agg))
        agg_unc = max(0.01, min(1.0, agg_unc))

        # --- Step 5: Assign band ---
        if agg >= 0.75:
            band = "HIGH"
        elif agg >= 0.60:
            band = "MOD_HIGH"
        elif agg >= 0.40:
            band = "MODERATE"
        else:
            band = "LOW"

        # Determine dominant tier
        tier_counts = Counter(t for _, _, t in representatives)
        dominant_tier = tier_counts.most_common(1)[0][0]

        self.cluster_credence = round(agg, 3)
        self.credence_uncertainty = round(agg_unc, 3)
        self.credence_band = band
        self.credence_n_inputs = len(representatives)
        self.credence_data_tier = dominant_tier

    @staticmethod
    def _finding_credence(m: ClusterMember) -> Tuple[Optional[float], float, str]:
        """Compute per-finding credence from available data.

        Returns (credence, uncertainty, tier_label) or (None, ...) if unusable.
        """
        import math

        # --- Tier A: full formula (d + N + p) ---
        if m.effect_size is not None and m.sample_size is not None and m.p_value is not None:
            try:
                d_val = float(m.effect_size)
                n_val = int(m.sample_size)
                d_val = max(-EFFECT_SIZE_CAP, min(EFFECT_SIZE_CAP, d_val))

                # Derive p_lab from p-value
                p_str = str(m.p_value).strip().lstrip('<>= ')
                p_num = float(p_str)
                # Convert two-tailed p to effect probability
                p_lab = max(0.05, min(0.95, 1.0 - p_num))

                # Heuristic omega based on article_type
                omega = _article_type_omega(m.article_type)
                delta = 1.0  # default population transfer
                discount = 0.85  # default discount factor

                logit_p_lab = math.log(p_lab / (1.0 - p_lab))
                logit_p_target = discount * omega * delta * logit_p_lab
                p_target = 1.0 / (1.0 + math.exp(-logit_p_target))

                # Uncertainty: smaller N → higher uncertainty
                se = (4.0 / n_val + d_val ** 2 / (2.0 * n_val)) ** 0.5
                unc = max(0.1, min(0.5, se))

                return max(0.05, min(0.95, p_target)), unc, "A_full"
            except (ValueError, TypeError, ZeroDivisionError):
                pass

        # --- Tier B: p-value only ---
        if m.p_value is not None:
            try:
                p_str = str(m.p_value).strip().lstrip('<>= ')
                p_num = float(p_str)
                if p_num <= 0 or p_num >= 1:
                    raise ValueError
                # Simple conversion: low p → high credence
                p_lab = max(0.05, min(0.95, 1.0 - p_num))
                omega = _article_type_omega(m.article_type)
                # Simpler projection without full formula
                credence = 0.5 + (p_lab - 0.5) * omega * 0.8
                return max(0.05, min(0.95, credence)), 0.30, "B_pvalue"
            except (ValueError, TypeError):
                pass

        # --- Tier C: direction only ---
        if m.direction and m.direction.lower() not in ("", "unknown", "na", "none"):
            # We have a direction claim but no statistical support
            # Base credence: slightly above 0.5 (someone claimed it)
            base = 0.55
            # Boost slightly if has theory links or mechanism
            if m.theory_links:
                base += 0.03
            if m.mechanism:
                base += 0.02
            return min(0.65, base), 0.40, "C_direction"

        # --- Tier D: nothing useful ---
        return None, 1.0, "D_none"

    def to_dict(self) -> Dict:
        """Serialize cluster with ALL members and full computed stats."""
        self.compute_stats()
        return {
            "cluster_id": self.cluster_id,
            "antecedent_theme": self.antecedent_theme,
            "consequent_theme": self.consequent_theme,
            "n_findings": self.n_findings,
            "n_papers": self.n_papers,
            "direction_consensus": self.direction_consensus,
            "direction_counts": self.direction_counts,
            "direction_entropy": round(self.direction_entropy, 3),
            "theory_links": self.theory_links,
            "median_effect_size": round(self.median_effect_size, 3) if self.median_effect_size is not None else None,
            "effect_size_iqr": self.effect_size_iqr,
            "n_with_effect_size": self.n_with_effect_size,
            "n_with_sample_size": self.n_with_sample_size,
            "n_effect_capped": self.n_effect_capped,
            "i_squared": round(self.i_squared, 1) if self.i_squared is not None else None,
            "cluster_credence": self.cluster_credence,
            "credence_uncertainty": self.credence_uncertainty,
            "credence_band": self.credence_band,
            "credence_n_inputs": self.credence_n_inputs,
            "credence_data_tier": self.credence_data_tier,
            "article_types": self.article_types,
            # ALL members with full fields — not just 5
            "sample_members": [
                {
                    "antecedent": m.antecedent[:150],
                    "consequent": m.consequent[:150],
                    "direction": m.direction,
                    "source": m.source_file,
                    "effect_size": round(min(EFFECT_SIZE_CAP, max(-EFFECT_SIZE_CAP, float(m.effect_size))), 3)
                        if m.effect_size is not None else None,
                    "sample_size": m.sample_size,
                    "p_value": m.p_value,
                    "article_type": m.article_type,
                    "mechanism": m.mechanism,
                    "theory_links": m.theory_links[:3] if m.theory_links else [],
                }
                for m in self.members
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
                    # Pull sample_size from finding if present, else article-level
                    n = finding.get("sample_size") or finding.get("sample_n") or sample_size
                    try:
                        n = int(n) if n is not None else None
                    except (ValueError, TypeError):
                        n = None
                    findings.append({
                        "antecedent": ant,
                        "consequent": cons,
                        "direction": finding.get("direction", ""),
                        "theory_links": finding.get("theory_links", []),
                        "p_value": finding.get("p_value"),
                        "effect_size": finding.get("effect_size"),
                        "source_file": json_file.stem,
                        "article_type": article_type,
                        "sample_size": n,
                        "mechanism": finding.get("mechanism"),
                        "evidence_type": finding.get("evidence_type"),
                        "measure_type": finding.get("measure_type"),
                        "claim_type": finding.get("claim_type"),
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
                mechanism=f.get("mechanism"),
                evidence_type=f.get("evidence_type"),
                measure_type=f.get("measure_type"),
                claim_type=f.get("claim_type"),
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
