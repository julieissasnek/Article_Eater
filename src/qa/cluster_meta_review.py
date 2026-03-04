"""
Cluster Meta-Review — Live Mini Meta-Reviews for Evidence Clusters
=====================================================================

Each belief cluster gets a structured meta-review that lives in the
annotation space. This is NOT just a lookup card — it's an intellectual
product that does real analytical work:

  1. Clear belief statement (norm-compliant, confidence-calibrated)
  2. Direction consensus with heterogeneity analysis
  3. Mechanism candidates (why might this effect exist?)
  4. Latent variable hypotheses (what unmeasured factors explain variance?)
  5. VOI-ranked research needs (what would most advance this belief?)
  6. Cross-cluster connections (where does this belief connect to others?)

Written according to WRITING_STYLE_GUIDE.md and SCIENCE_COMMUNICATION_NORMS.md.

These annotations can be used for:
  - QA: pre-computed answers grounded in real evidence
  - Discovery: latent variables and mechanism hypotheses generate research leads
  - Science: mini meta-reviews are publishable analytical summaries
  - Design: design implications are actionable for architects

Pipeline integration:
  Article ingested → clustering (2s) → meta-review generation → annotation write
  Total: < 10 seconds. No batch needed.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from collections import Counter

from src.qa.answer_renderer import (
    ConfidenceLevel,
    CONFIDENCE_LANGUAGE,
    build_thermometer,
    compute_confidence_level,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# The Meta-Review data model
# ---------------------------------------------------------------------------

@dataclass
class MechanismCandidate:
    """A plausible mechanism explaining the cluster's effect."""
    pathway: str           # e.g. "stress → cortisol → attention"
    theory_support: str    # Which theory predicts this
    evidence_count: int    # How many findings implicate this mechanism
    confidence: str        # high | moderate | speculative


@dataclass
class LatentVariable:
    """An unmeasured construct that may explain variance in the cluster."""
    name: str              # e.g. "individual stress sensitivity"
    rationale: str         # Why we think this matters
    type: str              # mediator | moderator | confounder
    testable: bool         # Can this be measured?
    suggested_measure: str # How to operationalize it


@dataclass
class ResearchNeed:
    """A VOI-ranked research question to advance the belief."""
    question: str          # The research question
    voi_rank: int          # 1 = highest value of information
    rationale: str         # Why this would be valuable
    study_type: str        # RCT | longitudinal | meta-analysis | measurement


@dataclass
class ClusterMetaReview:
    """
    A structured mini meta-review for one evidence cluster.

    This is the core intellectual product of the pre-computation system.
    """
    cluster_id: str
    antecedent_theme: str
    consequent_theme: str

    # --- The Belief ---
    belief_statement: str          # Clear, norm-compliant, confidence-calibrated
    confidence_level: str          # high | mod_high | moderate | low
    confidence_label: str          # "Mod-High (ω = 0.62)"
    confidence_color: str

    # --- Evidence Summary ---
    n_findings: int
    n_papers: int
    direction_consensus: str       # increase | decrease | mixed | no_effect
    direction_detail: str          # "73% increase, 15% mixed, 12% decrease"
    heterogeneity: str             # high | moderate | low
    article_types: Dict[str, int]  # {"empirical_v2": 30, "systematic_review": 5}
    theory_links: List[str]

    # --- Mechanism Analysis ---
    mechanisms: List[MechanismCandidate] = field(default_factory=list)

    # --- Discovery ---
    latent_variables: List[LatentVariable] = field(default_factory=list)
    research_needs: List[ResearchNeed] = field(default_factory=list)

    # --- Cross-Cluster ---
    related_clusters: List[str] = field(default_factory=list)  # cluster IDs
    contradicting_clusters: List[str] = field(default_factory=list)

    # --- Metadata ---
    generated_at: str = ""
    generation_time_ms: float = 0.0

    def to_dict(self) -> Dict:
        return {
            "cluster_id": self.cluster_id,
            "antecedent_theme": self.antecedent_theme,
            "consequent_theme": self.consequent_theme,
            "belief_statement": self.belief_statement,
            "confidence": {
                "level": self.confidence_level,
                "label": self.confidence_label,
                "color": self.confidence_color,
            },
            "evidence": {
                "n_findings": self.n_findings,
                "n_papers": self.n_papers,
                "direction_consensus": self.direction_consensus,
                "direction_detail": self.direction_detail,
                "heterogeneity": self.heterogeneity,
                "article_types": self.article_types,
                "theory_links": self.theory_links,
            },
            "mechanisms": [
                {
                    "pathway": m.pathway,
                    "theory_support": m.theory_support,
                    "evidence_count": m.evidence_count,
                    "confidence": m.confidence,
                }
                for m in self.mechanisms
            ],
            "latent_variables": [
                {
                    "name": lv.name,
                    "rationale": lv.rationale,
                    "type": lv.type,
                    "testable": lv.testable,
                    "suggested_measure": lv.suggested_measure,
                }
                for lv in self.latent_variables
            ],
            "research_needs": [
                {
                    "question": rn.question,
                    "voi_rank": rn.voi_rank,
                    "rationale": rn.rationale,
                    "study_type": rn.study_type,
                }
                for rn in self.research_needs
            ],
            "related_clusters": self.related_clusters,
            "contradicting_clusters": self.contradicting_clusters,
            "generated_at": self.generated_at,
            "generation_time_ms": self.generation_time_ms,
        }

    def to_annotation_content(self) -> str:
        """Format as annotation content for the annotation service."""
        parts = [self.belief_statement, ""]

        if self.mechanisms:
            parts.append("Mechanisms:")
            for m in self.mechanisms:
                parts.append(f"  • {m.pathway} ({m.confidence}, {m.theory_support})")
            parts.append("")

        if self.latent_variables:
            parts.append("Latent variables:")
            for lv in self.latent_variables:
                parts.append(f"  • {lv.name} ({lv.type}): {lv.rationale}")
            parts.append("")

        if self.research_needs:
            parts.append("Research needs (by VOI):")
            for rn in self.research_needs:
                parts.append(f"  {rn.voi_rank}. {rn.question} ({rn.study_type})")

        return "\n".join(parts)


# ---------------------------------------------------------------------------
# Theory → Mechanism mapping
# ---------------------------------------------------------------------------

THEORY_MECHANISMS = {
    "SRT": {
        "name": "Stress Recovery Theory (Ulrich)",
        "pathway": "natural_stimuli → parasympathetic activation → cortisol reduction → stress relief",
        "mediators": ["autonomic arousal", "attention capture"],
    },
    "ART": {
        "name": "Attention Restoration Theory (Kaplan)",
        "pathway": "soft_fascination → involuntary attention → directed attention recovery",
        "mediators": ["cognitive fatigue", "attentional capacity"],
    },
    "Biophilia": {
        "name": "Biophilia Hypothesis (Wilson)",
        "pathway": "nature_elements → evolutionary preference → positive affect",
        "mediators": ["evolutionary fitness signals", "aesthetic preference"],
    },
    "NM": {
        "name": "Neurological Mechanisms",
        "pathway": "sensory_input → neural processing → behavioral/affective response",
        "mediators": ["neural adaptation", "sensory sensitivity"],
    },
    "PP": {
        "name": "Psychophysics / Perception",
        "pathway": "physical_stimulus → sensory transduction → perceptual judgment",
        "mediators": ["stimulus intensity", "adaptation level"],
    },
    "CB": {
        "name": "Circadian Biology",
        "pathway": "light_exposure → melanopsin_activation → circadian_entrainment → sleep/wake",
        "mediators": ["melatonin suppression", "circadian phase"],
    },
    "IC": {
        "name": "Individual/Cultural Differences",
        "pathway": "personal_history + culture → appraisal → differential response",
        "mediators": ["prior experience", "cultural norms", "personality"],
    },
    "DT": {
        "name": "Distraction Theory",
        "pathway": "irrelevant_stimuli → attentional capture → task interference",
        "mediators": ["task complexity", "stimulus salience"],
    },
    "MSI": {
        "name": "Multisensory Integration",
        "pathway": "cross_modal_inputs → binding → unified percept",
        "mediators": ["temporal synchrony", "spatial congruency"],
    },
    "DP": {
        "name": "Design Principles",
        "pathway": "spatial_configuration → affordance → behavior",
        "mediators": ["enclosure", "prospect", "refuge"],
    },
}


# ---------------------------------------------------------------------------
# Meta-Review Generator
# ---------------------------------------------------------------------------

class MetaReviewGenerator:
    """
    Generates mini meta-reviews from belief clusters.

    Each meta-review is a structured intellectual product containing:
    - Norm-compliant belief statement
    - Mechanism analysis
    - Latent variable hypotheses
    - VOI-ranked research needs
    """

    def __init__(self):
        pass

    def generate(self, cluster: Dict) -> ClusterMetaReview:
        """Generate a meta-review from a cluster dict."""
        start = time.time()

        ant = cluster.get("antecedent_theme", "unknown")
        cons = cluster.get("consequent_theme", "unknown")
        n_findings = cluster.get("n_findings", 0)
        n_papers = cluster.get("n_papers", 0)
        direction_counts = cluster.get("direction_counts", {})
        consensus = cluster.get("direction_consensus", "unknown")
        theories = cluster.get("theory_links", [])
        article_types = cluster.get("article_types", {})

        # 1. Compute confidence
        omega = self._estimate_omega(n_findings, n_papers, direction_counts)
        thermometer = build_thermometer(omega, n_findings=n_findings, n_replications=n_papers)
        conf_lang = CONFIDENCE_LANGUAGE[thermometer.level]

        # 2. Build belief statement (norm-compliant)
        belief = self._build_belief_statement(
            ant, cons, consensus, thermometer.level, conf_lang, n_findings, n_papers
        )

        # 3. Direction detail
        total_dir = sum(direction_counts.values()) or 1
        direction_detail = ", ".join(
            f"{int(v/total_dir*100)}% {k}" for k, v in
            sorted(direction_counts.items(), key=lambda x: -x[1])
        )

        # 4. Heterogeneity
        heterogeneity = self._assess_heterogeneity(direction_counts)

        # 5. Mechanisms
        mechanisms = self._identify_mechanisms(theories, ant, cons, n_findings)

        # 6. Latent variables
        latent_vars = self._identify_latent_variables(
            ant, cons, theories, heterogeneity, mechanisms
        )

        # 7. Research needs
        research_needs = self._identify_research_needs(
            ant, cons, n_findings, n_papers, heterogeneity,
            latent_vars, mechanisms, thermometer.level
        )

        elapsed_ms = (time.time() - start) * 1000

        return ClusterMetaReview(
            cluster_id=cluster.get("cluster_id", ""),
            antecedent_theme=ant,
            consequent_theme=cons,
            belief_statement=belief,
            confidence_level=thermometer.level.value,
            confidence_label=thermometer.label,
            confidence_color=thermometer.color,
            n_findings=n_findings,
            n_papers=n_papers,
            direction_consensus=consensus,
            direction_detail=direction_detail,
            heterogeneity=heterogeneity,
            article_types=article_types,
            theory_links=theories,
            mechanisms=mechanisms,
            latent_variables=latent_vars,
            research_needs=research_needs,
            generated_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            generation_time_ms=round(elapsed_ms, 2),
        )

    # ------------------------------------------------------------------
    # Belief Statement
    # ------------------------------------------------------------------

    def _build_belief_statement(
        self, ant: str, cons: str, consensus: str,
        level: ConfidenceLevel, conf_lang: Dict,
        n_findings: int, n_papers: int,
    ) -> str:
        """
        Build a norm-compliant belief statement.

        Follows WRITING_STYLE_GUIDE §1.1 (lead with point) and
        SCIENCE_COMMUNICATION_NORMS Norm 9 (confidence spectrum).
        """
        ant_readable = ant.replace("_", " ")
        cons_readable = cons.replace("_", " ")

        if consensus == "increase":
            verb = conf_lang["verbs"][0]
            direction_phrase = f"{verb} {cons_readable}"
        elif consensus == "decrease":
            verb = conf_lang["verbs"][0]
            direction_phrase = f"reduces {cons_readable}"
        elif consensus == "no_effect":
            direction_phrase = f"does not reliably affect {cons_readable}"
        else:  # mixed
            direction_phrase = f"has inconsistent effects on {cons_readable}"

        if level in (ConfidenceLevel.HIGH, ConfidenceLevel.MOD_HIGH):
            statement = (
                f"{ant_readable.capitalize()} {direction_phrase}. "
                f"This conclusion draws on {n_findings} findings from "
                f"{n_papers} independent studies."
            )
        elif level == ConfidenceLevel.MODERATE:
            prefix = conf_lang.get("prefix", "Preliminary evidence indicates")
            statement = (
                f"{prefix} that {ant_readable} {direction_phrase}. "
                f"The evidence base ({n_findings} findings, {n_papers} studies) "
                f"is growing but not yet conclusive."
            )
        else:  # LOW
            prefix = conf_lang.get("prefix", "One possibility is")
            statement = (
                f"{prefix} that {ant_readable} {direction_phrase}, "
                f"but the evidence is limited ({n_findings} findings, "
                f"{n_papers} studies). Further research is needed."
            )

        return statement

    # ------------------------------------------------------------------
    # Heterogeneity
    # ------------------------------------------------------------------

    def _assess_heterogeneity(self, direction_counts: Dict) -> str:
        """Assess direction heterogeneity across findings."""
        if not direction_counts:
            return "unknown"
        total = sum(direction_counts.values())
        if total == 0:
            return "unknown"
        dominant = max(direction_counts.values())
        ratio = dominant / total
        if ratio >= 0.8:
            return "low"
        elif ratio >= 0.6:
            return "moderate"
        else:
            return "high"

    # ------------------------------------------------------------------
    # Mechanism Identification
    # ------------------------------------------------------------------

    def _identify_mechanisms(
        self, theories: List[str], ant: str, cons: str, n_findings: int,
    ) -> List[MechanismCandidate]:
        """Identify plausible mechanisms from theory links."""
        mechanisms = []

        for theory_code in theories[:5]:
            if theory_code in THEORY_MECHANISMS:
                t = THEORY_MECHANISMS[theory_code]
                # Estimate evidence count (rough: proportional to theory frequency)
                evidence_est = max(1, n_findings // max(len(theories), 1))

                confidence = "moderate"
                if evidence_est > 20:
                    confidence = "high"
                elif evidence_est < 5:
                    confidence = "speculative"

                mechanisms.append(MechanismCandidate(
                    pathway=t["pathway"],
                    theory_support=t["name"],
                    evidence_count=evidence_est,
                    confidence=confidence,
                ))

        # If no theories, provide a generic mechanism hypothesis
        if not mechanisms:
            mechanisms.append(MechanismCandidate(
                pathway=f"{ant.replace('_', ' ')} → [unknown mechanism] → {cons.replace('_', ' ')}",
                theory_support="No specific theory",
                evidence_count=0,
                confidence="speculative",
            ))

        return mechanisms

    # ------------------------------------------------------------------
    # Latent Variable Discovery
    # ------------------------------------------------------------------

    def _identify_latent_variables(
        self, ant: str, cons: str, theories: List[str],
        heterogeneity: str, mechanisms: List[MechanismCandidate],
    ) -> List[LatentVariable]:
        """
        Identify unmeasured constructs that may explain variance.

        This is the discovery engine — it generates testable hypotheses
        about what factors might be modulating the relationship.
        """
        latent_vars = []

        # 1. If heterogeneity is high, there MUST be a moderator
        if heterogeneity == "high":
            latent_vars.append(LatentVariable(
                name="Individual sensitivity differences",
                rationale=(
                    f"High heterogeneity ({heterogeneity}) across findings suggests "
                    f"an unmeasured individual-difference variable moderates the "
                    f"effect of {ant.replace('_', ' ')} on {cons.replace('_', ' ')}."
                ),
                type="moderator",
                testable=True,
                suggested_measure="Pre-screening for trait sensitivity or prior exposure",
            ))

        # 2. If IC (Individual/Cultural) theory is implicated
        if "IC" in theories:
            latent_vars.append(LatentVariable(
                name="Cultural background",
                rationale=(
                    "Individual/cultural differences theory is implicated. "
                    "Cultural norms around nature, noise, or space may moderate effects."
                ),
                type="moderator",
                testable=True,
                suggested_measure="Cultural background questionnaire + cross-cultural replication",
            ))

        # 3. If multiple mechanisms exist, there may be a mediator
        if len(mechanisms) > 1:
            m_names = [m.theory_support for m in mechanisms[:3]]
            latent_vars.append(LatentVariable(
                name="Mechanism selection",
                rationale=(
                    f"Multiple mechanisms are implicated ({', '.join(m_names)}). "
                    f"A latent variable may determine which pathway is activated."
                ),
                type="mediator",
                testable=True,
                suggested_measure="Process tracing or mediation analysis",
            ))

        # 4. Dose-response: almost always unmeasured
        latent_vars.append(LatentVariable(
            name="Dose and duration",
            rationale=(
                f"Most studies measure presence/absence of {ant.replace('_', ' ')}, "
                f"not dose-response curves. Duration and intensity likely matter."
            ),
            type="moderator",
            testable=True,
            suggested_measure="Parametric variation of intensity and exposure duration",
        ))

        return latent_vars

    # ------------------------------------------------------------------
    # Research Needs (VOI-ranked)
    # ------------------------------------------------------------------

    def _identify_research_needs(
        self, ant: str, cons: str, n_findings: int, n_papers: int,
        heterogeneity: str, latent_vars: List[LatentVariable],
        mechanisms: List[MechanismCandidate], level: ConfidenceLevel,
    ) -> List[ResearchNeed]:
        """
        Generate VOI-ranked research needs.

        Higher VOI = would most change the confidence level of this belief.
        """
        needs = []
        voi = 1

        # 1. If confidence is low/moderate, replication is highest VOI
        if level in (ConfidenceLevel.LOW, ConfidenceLevel.MODERATE):
            needs.append(ResearchNeed(
                question=(
                    f"Does the effect of {ant.replace('_', ' ')} on "
                    f"{cons.replace('_', ' ')} replicate in a pre-registered RCT?"
                ),
                voi_rank=voi,
                rationale=(
                    f"Current confidence is {level.value}. A well-powered "
                    f"pre-registered replication would most efficiently "
                    f"resolve the status of this belief."
                ),
                study_type="RCT",
            ))
            voi += 1

        # 2. If heterogeneity is high, moderator search is key
        if heterogeneity == "high":
            needs.append(ResearchNeed(
                question=(
                    f"What moderates the effect of {ant.replace('_', ' ')} on "
                    f"{cons.replace('_', ' ')}?"
                ),
                voi_rank=voi,
                rationale="High heterogeneity suggests an unmeasured moderator.",
                study_type="meta-analysis",
            ))
            voi += 1

        # 3. Mechanism disambiguation
        if len(mechanisms) > 1:
            needs.append(ResearchNeed(
                question=(
                    f"Which mechanism best explains {ant.replace('_', ' ')} → "
                    f"{cons.replace('_', ' ')}?"
                ),
                voi_rank=voi,
                rationale=(
                    f"{len(mechanisms)} candidate mechanisms exist. "
                    f"Process tracing would identify the active pathway."
                ),
                study_type="measurement",
            ))
            voi += 1

        # 4. Dose-response (always valuable)
        needs.append(ResearchNeed(
            question=(
                f"What is the dose-response curve for {ant.replace('_', ' ')} "
                f"effects on {cons.replace('_', ' ')}?"
            ),
            voi_rank=voi,
            rationale="Dose-response data enables design guidelines with specific thresholds.",
            study_type="RCT",
        ))
        voi += 1

        # 5. Longitudinal persistence
        if level in (ConfidenceLevel.HIGH, ConfidenceLevel.MOD_HIGH):
            needs.append(ResearchNeed(
                question=(
                    f"Do the effects of {ant.replace('_', ' ')} on "
                    f"{cons.replace('_', ' ')} persist over weeks/months?"
                ),
                voi_rank=voi,
                rationale="Most findings are from acute studies. Long-term effects are unknown.",
                study_type="longitudinal",
            ))

        return needs

    # ------------------------------------------------------------------
    # Omega Estimation
    # ------------------------------------------------------------------

    def _estimate_omega(
        self, n_findings: int, n_papers: int, direction_counts: Dict
    ) -> float:
        """Heuristic omega from cluster statistics."""
        consensus_ratio = (
            max(direction_counts.values()) / max(sum(direction_counts.values()), 1)
            if direction_counts else 0
        )
        return min(1.0, (
            0.3 * min(n_findings / 50, 1.0) +
            0.3 * min(n_papers / 20, 1.0) +
            0.4 * consensus_ratio
        ))


# ---------------------------------------------------------------------------
# Real-Time Ingestion Pipeline
# ---------------------------------------------------------------------------

class IngestionPipeline:
    """
    Real-time pipeline triggered on article ingestion.

    NOT a nightly batch. Runs in < 10 seconds:
      1. Re-cluster affected topics (2s)
      2. Generate meta-reviews for affected clusters
      3. Write annotations
      4. Regenerate answer cards for affected clusters
    """

    def __init__(
        self,
        extractions_dir: str = "data/extractions",
        output_dir: str = "data/materialized_views",
    ):
        self._extractions_dir = Path(extractions_dir)
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)
        self._meta_dir = self._output_dir / "meta_reviews"
        self._meta_dir.mkdir(exist_ok=True)
        self._generator = MetaReviewGenerator()

    def on_article_ingested(self, extraction_path: str) -> Dict[str, Any]:
        """
        Trigger full pipeline on new article.

        Args:
            extraction_path: Path to the new extraction JSON file.

        Returns:
            Stats dict with timing, affected clusters, etc.
        """
        start = time.time()
        stats = {"extraction": extraction_path, "steps": []}

        # Step 1: Identify affected clusters
        step_start = time.time()
        from src.qa.belief_clustering import normalize_term
        affected_keys = self._find_affected_clusters(extraction_path)
        stats["steps"].append({
            "name": "identify_affected",
            "ms": round((time.time() - step_start) * 1000, 1),
            "affected_clusters": len(affected_keys),
        })

        # Step 2: Re-cluster (incremental)
        step_start = time.time()
        clusters = self._incremental_recluster(affected_keys)
        stats["steps"].append({
            "name": "recluster",
            "ms": round((time.time() - step_start) * 1000, 1),
            "clusters_updated": len(clusters),
        })

        # Step 3: Generate meta-reviews
        step_start = time.time()
        reviews = []
        for cluster in clusters:
            review = self._generator.generate(cluster)
            reviews.append(review)
        stats["steps"].append({
            "name": "meta_reviews",
            "ms": round((time.time() - step_start) * 1000, 1),
            "reviews_generated": len(reviews),
        })

        # Step 4: Save meta-reviews
        step_start = time.time()
        self._save_meta_reviews(reviews)
        stats["steps"].append({
            "name": "save",
            "ms": round((time.time() - step_start) * 1000, 1),
        })

        stats["total_ms"] = round((time.time() - start) * 1000, 1)
        logger.info(
            f"Ingestion pipeline complete: {len(reviews)} meta-reviews "
            f"in {stats['total_ms']:.0f}ms"
        )

        return stats

    def generate_all_meta_reviews(self, max_clusters: int = 0) -> Dict[str, Any]:
        """
        Generate meta-reviews for all existing clusters.

        Args:
            max_clusters: If > 0, limit to this many clusters.

        Returns:
            Stats with timing and counts.
        """
        start = time.time()

        # Load clusters
        clusters_path = self._output_dir / "belief_clusters.json"
        with open(clusters_path) as f:
            data = json.load(f)
        clusters = data.get("clusters", [])

        if max_clusters > 0:
            clusters = clusters[:max_clusters]

        reviews = []
        for i, cluster in enumerate(clusters):
            review = self._generator.generate(cluster)
            reviews.append(review)
            if (i + 1) % 500 == 0:
                elapsed = time.time() - start
                logger.info(
                    f"  Progress: {i+1}/{len(clusters)} reviews, "
                    f"{(i+1)/elapsed:.0f}/s"
                )

        elapsed = time.time() - start

        # Save all
        self._save_meta_reviews(reviews)

        # Save summary
        stats = {
            "total_clusters": len(clusters),
            "reviews_generated": len(reviews),
            "elapsed_seconds": round(elapsed, 2),
            "reviews_per_second": round(len(reviews) / max(elapsed, 0.001), 1),
            "high_confidence": sum(1 for r in reviews if r.confidence_level == "high"),
            "mod_high_confidence": sum(1 for r in reviews if r.confidence_level == "mod_high"),
            "moderate_confidence": sum(1 for r in reviews if r.confidence_level == "moderate"),
            "low_confidence": sum(1 for r in reviews if r.confidence_level == "low"),
            "high_heterogeneity": sum(1 for r in reviews if r.heterogeneity == "high"),
            "avg_mechanisms": round(sum(len(r.mechanisms) for r in reviews) / max(len(reviews), 1), 1),
            "avg_latent_vars": round(sum(len(r.latent_variables) for r in reviews) / max(len(reviews), 1), 1),
            "avg_research_needs": round(sum(len(r.research_needs) for r in reviews) / max(len(reviews), 1), 1),
        }

        stats_path = self._meta_dir / "meta_review_stats.json"
        with open(stats_path, "w") as f:
            json.dump(stats, f, indent=2)

        logger.info(
            f"Generated {len(reviews)} meta-reviews in {elapsed:.1f}s "
            f"({stats['reviews_per_second']}/s)"
        )
        return stats

    def _find_affected_clusters(self, extraction_path: str) -> Set[str]:
        """Find cluster keys affected by a new extraction."""
        from src.qa.belief_clustering import normalize_term

        affected = set()
        try:
            with open(extraction_path) as f:
                data = json.load(f)
            for finding in data.get("findings", []):
                ant = finding.get("antecedent", "").strip()
                cons = finding.get("consequent", "").strip()
                if ant and cons:
                    key = f"{normalize_term(ant)}|{normalize_term(cons)}"
                    affected.add(key)
        except Exception as e:
            logger.warning(f"Failed to parse extraction: {e}")
        return affected

    def _incremental_recluster(self, affected_keys: Set[str]) -> List[Dict]:
        """
        Incrementally update only affected clusters.

        For now, loads the full cluster file and returns affected clusters.
        A production version would maintain an in-memory index.
        """
        clusters_path = self._output_dir / "belief_clusters.json"
        if not clusters_path.exists():
            return []

        with open(clusters_path) as f:
            data = json.load(f)

        # Return all clusters that share tokens with affected keys
        affected_tokens = set()
        for key in affected_keys:
            parts = key.split("|")
            for part in parts:
                affected_tokens.update(part.split("_"))

        result = []
        for cluster in data.get("clusters", []):
            ant_tokens = set(cluster.get("antecedent_theme", "").split("_"))
            cons_tokens = set(cluster.get("consequent_theme", "").split("_"))
            if ant_tokens & affected_tokens or cons_tokens & affected_tokens:
                result.append(cluster)

        return result

    def _save_meta_reviews(self, reviews: List[ClusterMetaReview]):
        """Save meta-reviews as JSON files."""
        # Save individual reviews
        for review in reviews:
            review_path = self._meta_dir / f"{review.cluster_id}.json"
            with open(review_path, "w") as f:
                json.dump(review.to_dict(), f, indent=2, default=str)

        # Save master index
        index = {
            r.cluster_id: {
                "belief": r.belief_statement[:100],
                "confidence": r.confidence_level,
                "n_findings": r.n_findings,
                "heterogeneity": r.heterogeneity,
                "n_mechanisms": len(r.mechanisms),
                "n_latent_vars": len(r.latent_variables),
                "n_research_needs": len(r.research_needs),
            }
            for r in reviews
        }
        index_path = self._meta_dir / "meta_review_index.json"
        with open(index_path, "w") as f:
            json.dump(index, f, indent=1)
