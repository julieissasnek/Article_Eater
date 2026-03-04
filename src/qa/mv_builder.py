"""
Materialized View Builder — Offline Pre-Computation Engine
============================================================

Pre-computes all enrichment data offline so query-time pipeline
runs in <100ms (cache lookup + personalize) instead of 5+ seconds.

Extends the FRESH/STALE cache pattern from MolecularQAPrecomputer.

Materialized Views:
  1. mv_omega_scores     — All ω components per belief
  2. mv_evidence_index   — Belief → source paper → finding → quote
  3. mv_gap_analysis     — Knowledge gaps per topic cluster
  4. mv_framework_voices — Framework perspectives per topic
  5. mv_user_adapted     — Pre-rendered answers per (user_type, topic)

Usage:
    builder = MaterializedViewBuilder()
    builder.build_all()              # Full rebuild
    builder.build_all(incremental=True)  # Only STALE views

    # In nightly pipeline:
    builder.mark_stale("topic_cluster_id")  # On new article
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Cache tracking
# ---------------------------------------------------------------------------

@dataclass
class ViewEntry:
    """A single cached materialized view entry."""
    view_id: str
    data: Dict[str, Any]
    content_hash: str
    status: str = "FRESH"  # FRESH | STALE
    last_computed: str = ""
    compute_time_ms: float = 0.0

    def to_dict(self) -> Dict:
        return {
            "view_id": self.view_id,
            "data": self.data,
            "content_hash": self.content_hash,
            "status": self.status,
            "last_computed": self.last_computed,
            "compute_time_ms": self.compute_time_ms,
        }


# ---------------------------------------------------------------------------
# Materialized View Builder
# ---------------------------------------------------------------------------

class MaterializedViewBuilder:
    """
    Pre-computes all enrichment data offline.

    All views are stored as JSON files in data/materialized_views/
    with FRESH/STALE tracking via content hashing.
    """

    def __init__(
        self,
        extractions_dir: str = "data/extractions",
        output_dir: str = "data/materialized_views",
    ):
        self._extractions_dir = Path(extractions_dir)
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)
        self._stale_clusters: Set[str] = set()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def build_all(self, incremental: bool = False) -> Dict[str, Any]:
        """
        Build all materialized views.

        Args:
            incremental: If True, only rebuild STALE views.

        Returns:
            Dict with build statistics per view.
        """
        stats = {}
        views = [
            ("omega_scores", self.build_omega_scores),
            ("evidence_index", self.build_evidence_index),
            ("gap_analysis", self.build_gap_analysis),
            ("framework_voices", self.build_framework_voices),
        ]

        for view_name, builder_fn in views:
            if incremental and not self._is_stale(view_name):
                logger.info(f"MV {view_name}: FRESH, skipping")
                stats[view_name] = {"status": "FRESH", "skipped": True}
                continue

            logger.info(f"MV {view_name}: building...")
            start = time.time()
            try:
                result = builder_fn()
                elapsed = (time.time() - start) * 1000
                self._save_view(view_name, result, elapsed)
                stats[view_name] = {
                    "status": "BUILT",
                    "entries": len(result) if isinstance(result, (list, dict)) else 1,
                    "elapsed_ms": round(elapsed, 1),
                }
                logger.info(
                    f"MV {view_name}: built {stats[view_name]['entries']} entries "
                    f"in {elapsed:.1f}ms"
                )
            except Exception as e:
                elapsed = (time.time() - start) * 1000
                logger.error(f"MV {view_name}: FAILED — {e}")
                stats[view_name] = {
                    "status": "FAILED",
                    "error": str(e),
                    "elapsed_ms": round(elapsed, 1),
                }

        # Save build manifest
        manifest = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "incremental": incremental,
            "views": stats,
        }
        manifest_path = self._output_dir / "_build_manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        return stats

    def mark_stale(self, cluster_id: str):
        """Mark a topic cluster as STALE (triggers rebuild on next run)."""
        self._stale_clusters.add(cluster_id)
        # Also mark all views as stale
        for view_file in self._output_dir.glob("*.json"):
            if view_file.name.startswith("_"):
                continue
            try:
                with open(view_file) as f:
                    data = json.load(f)
                data["status"] = "STALE"
                with open(view_file, "w") as f:
                    json.dump(data, f, indent=2)
            except Exception:
                pass

    def get_view(self, view_name: str) -> Optional[Dict]:
        """Retrieve a pre-computed materialized view."""
        view_path = self._output_dir / f"{view_name}.json"
        if not view_path.exists():
            return None
        try:
            with open(view_path) as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load MV {view_name}: {e}")
            return None

    # ------------------------------------------------------------------
    # View builders
    # ------------------------------------------------------------------

    def build_omega_scores(self) -> Dict[str, Any]:
        """
        Compute all ω components (severity, confound, replication, meta)
        for every finding in the extraction corpus.

        Uses warrant_strength.compute_omega_sev/conf/rep/meta.
        """
        try:
            from src.services.warrant_strength import (
                compute_omega_sev,
                compute_omega_conf,
                compute_omega_rep,
                compute_omega_meta,
                DesignType,
            )
        except ImportError:
            logger.warning("warrant_strength not available, using defaults")
            return {"error": "warrant_strength module not available"}

        scores = {}
        count = 0

        for json_file in self._extractions_dir.glob("*.json"):
            try:
                with open(json_file) as f:
                    data = json.load(f)

                findings = data.get("findings", [])
                if not findings:
                    continue

                article_type = data.get("article_type", "unknown")
                study_design = data.get("study_design", "observational")

                # Map study design to DesignType enum
                design_map = {
                    "experiment": DesignType.RCT,
                    "rct": DesignType.RCT,
                    "survey": DesignType.OBSERVATIONAL,
                    "observational": DesignType.OBSERVATIONAL,
                    "field_study": DesignType.QUASI_EXPERIMENTAL,
                    "quasi_experimental": DesignType.QUASI_EXPERIMENTAL,
                    "case_study": DesignType.CASE_STUDY,
                    "meta_analysis": DesignType.META_ANALYSIS,
                }
                design_enum = design_map.get(study_design, DesignType.OBSERVATIONAL)

                file_scores = []
                for finding in findings:
                    sample_size = finding.get("sample_size") or data.get("n_participants") or 50
                    if isinstance(sample_size, str):
                        try:
                            sample_size = int(sample_size)
                        except (ValueError, TypeError):
                            sample_size = 50

                    omega_sev = compute_omega_sev(
                        design_type=design_enum,
                        sample_size=sample_size,
                        pre_registered=False,
                        blinding="none",
                        self_report=finding.get("measure_type") == "self_report",
                    )
                    omega_conf = compute_omega_conf(
                        n_uncontrolled_confounds=2,
                        has_randomization=design_enum == DesignType.RCT,
                        has_active_control=False,
                    )
                    omega_rep = compute_omega_rep(
                        n_independent_replications=0,
                        n_conceptual_replications=0,
                    )
                    omega_meta = compute_omega_meta(
                        publication_type="peer_reviewed",
                        is_pre_registered=False,
                    )

                    file_scores.append({
                        "finding_id": finding.get("id", count),
                        "antecedent": finding.get("antecedent", ""),
                        "consequent": finding.get("consequent", ""),
                        "omega_sev": round(omega_sev, 4),
                        "omega_conf": round(omega_conf, 4),
                        "omega_rep": round(omega_rep, 4),
                        "omega_meta": round(omega_meta, 4),
                        "omega_total": round(
                            omega_sev * omega_conf * omega_rep * omega_meta, 4
                        ),
                    })
                    count += 1

                scores[json_file.stem] = {
                    "article_type": article_type,
                    "n_findings": len(file_scores),
                    "scores": file_scores,
                }

            except Exception as e:
                logger.debug(f"Skipping {json_file.name}: {e}")

        logger.info(f"Computed omega scores for {count} findings across {len(scores)} articles")
        return scores

    def build_evidence_index(self) -> Dict[str, Any]:
        """
        Build evidence index: finding → source paper → quote.

        This is the lookup table for tracing any claim to its source.
        """
        index = {}
        count = 0

        for json_file in self._extractions_dir.glob("*.json"):
            try:
                with open(json_file) as f:
                    data = json.load(f)

                findings = data.get("findings", []) or data.get("pooled_effects", [])
                if not findings:
                    continue

                title = data.get("title", json_file.stem)
                article_type = data.get("article_type", "unknown")

                for finding in findings:
                    antecedent = finding.get("antecedent", "")
                    consequent = finding.get("consequent", "")
                    if not antecedent and not consequent:
                        continue

                    # Build a content key for de-duplication
                    content_key = f"{antecedent}|{consequent}".lower().strip()
                    entry = {
                        "source_file": json_file.name,
                        "title": title[:200],
                        "article_type": article_type,
                        "antecedent": antecedent,
                        "consequent": consequent,
                        "direction": finding.get("direction", ""),
                        "p_value": finding.get("p_value"),
                        "effect_size": finding.get("effect_size"),
                        "theory_links": finding.get("theory_links", []),
                        "quote": finding.get("quote", "")[:200],
                        "source_ref": finding.get("source", ""),
                    }

                    if content_key not in index:
                        index[content_key] = []
                    index[content_key].append(entry)
                    count += 1

            except Exception as e:
                logger.debug(f"Skipping {json_file.name}: {e}")

        logger.info(f"Built evidence index: {count} entries, {len(index)} unique claims")
        return {"total_entries": count, "unique_claims": len(index), "index": index}

    def build_gap_analysis(self) -> Dict[str, Any]:
        """
        Pre-compute gap analysis per theory link / domain.

        Groups findings by theory_links and identifies coverage gaps.
        """
        theory_coverage: Dict[str, List[str]] = {}
        domain_coverage: Dict[str, List[str]] = {}

        for json_file in self._extractions_dir.glob("*.json"):
            try:
                with open(json_file) as f:
                    data = json.load(f)

                findings = data.get("findings", [])
                domains = data.get("domains", [])

                # Track which theories have coverage
                for finding in findings:
                    for theory in finding.get("theory_links", []):
                        if theory not in theory_coverage:
                            theory_coverage[theory] = []
                        theory_coverage[theory].append(json_file.name)

                # Track domain coverage
                for domain in domains:
                    if domain not in domain_coverage:
                        domain_coverage[domain] = []
                    domain_coverage[domain].append(json_file.name)

            except Exception:
                continue

        # Identify gaps: theories with few papers
        all_theories = [
            "PP", "SN", "DP", "DT", "NM", "IC", "MS", "EC", "CB", "MSI",
            "ART", "SRT", "Biophilia", "Prospect-Refuge", "Privacy Regulation",
        ]
        all_domains = [f"A{i}" for i in range(1, 11)]

        gaps = {
            "theory_gaps": [
                {
                    "theory": t,
                    "n_papers": len(theory_coverage.get(t, [])),
                    "gap_severity": "high" if len(theory_coverage.get(t, [])) < 5
                                    else "medium" if len(theory_coverage.get(t, [])) < 15
                                    else "low",
                }
                for t in all_theories
            ],
            "domain_gaps": [
                {
                    "domain": d,
                    "n_papers": len(domain_coverage.get(d, [])),
                    "gap_severity": "high" if len(domain_coverage.get(d, [])) < 5
                                    else "medium" if len(domain_coverage.get(d, [])) < 15
                                    else "low",
                }
                for d in all_domains
            ],
            "theory_coverage": {t: len(v) for t, v in theory_coverage.items()},
            "domain_coverage": {d: len(v) for d, v in domain_coverage.items()},
        }

        return gaps

    def build_framework_voices(self) -> Dict[str, Any]:
        """
        Pre-compute framework voice perspectives per theory link.

        Uses the same FRAMEWORK_VOICES data that IntegratedQueryService uses,
        but pre-renders it for each theory so query-time is a simple lookup.
        """
        try:
            from src.services.integrated_query_service import FRAMEWORK_VOICES
        except ImportError:
            logger.warning("FRAMEWORK_VOICES not available")
            return {"error": "FRAMEWORK_VOICES not importable"}

        # FRAMEWORK_VOICES is a dict of {framework_name: {perspective, ...}}
        voices = {}
        for framework_name, details in FRAMEWORK_VOICES.items():
            voices[framework_name] = {
                "framework": framework_name,
                "perspective": details.get("perspective", ""),
                "key_figures": details.get("key_figures", []),
                "core_claim": details.get("core_claim", ""),
                "typical_questions": details.get("typical_questions", []),
                "complications": details.get("complications", []),
            }

        return voices

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _is_stale(self, view_name: str) -> bool:
        """Check if a view is STALE and needs rebuild."""
        view_path = self._output_dir / f"{view_name}.json"
        if not view_path.exists():
            return True  # Missing = needs build
        try:
            with open(view_path) as f:
                data = json.load(f)
            return data.get("status") == "STALE"
        except Exception:
            return True

    def _save_view(self, view_name: str, data: Any, elapsed_ms: float):
        """Save a materialized view to disk."""
        content = json.dumps(data, default=str)
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]

        view = {
            "view_name": view_name,
            "status": "FRESH",
            "content_hash": content_hash,
            "last_computed": datetime.now(timezone.utc).isoformat(),
            "compute_time_ms": round(elapsed_ms, 1),
            "data": data,
        }

        view_path = self._output_dir / f"{view_name}.json"
        with open(view_path, "w") as f:
            json.dump(view, f, indent=2)

    def _compute_hash(self, data: Any) -> str:
        """Compute content hash for staleness detection."""
        content = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(content.encode()).hexdigest()[:16]
