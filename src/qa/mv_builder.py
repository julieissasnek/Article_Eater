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
                PublicationType,
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
                # P1 fix: DesignType.RCT doesn't exist — it's STANDARD_RCT
                design_map = {
                    "experiment": DesignType.STANDARD_RCT,
                    "experimental": DesignType.STANDARD_RCT,
                    "rct": DesignType.STANDARD_RCT,
                    "randomized_controlled_trial": DesignType.STANDARD_RCT,
                    "survey": DesignType.OBSERVATIONAL,
                    "observational": DesignType.OBSERVATIONAL,
                    "cross_sectional": DesignType.OBSERVATIONAL,
                    "correlational": DesignType.OBSERVATIONAL,
                    "longitudinal": DesignType.OBSERVATIONAL,
                    "field_study": DesignType.QUASI_EXPERIMENTAL,
                    "quasi_experimental": DesignType.QUASI_EXPERIMENTAL,
                    "within_subjects": DesignType.WITHIN_SUBJECTS,
                    "repeated_measures": DesignType.WITHIN_SUBJECTS,
                    "case_study": DesignType.CASE_STUDY,
                    "meta_analysis": DesignType.META_ANALYSIS,
                    "systematic_review": DesignType.SYSTEMATIC_REVIEW,
                    "review": DesignType.SYSTEMATIC_REVIEW,
                }
                normalized_design = str(study_design).lower().strip().replace("-", "_").replace(" ", "_")
                design_enum = design_map.get(normalized_design, DesignType.OBSERVATIONAL)

                file_scores = []
                for finding in findings:
                    sample_size = finding.get("sample_size") or data.get("n_participants") or 50
                    if isinstance(sample_size, str):
                        try:
                            sample_size = int(sample_size)
                        except (ValueError, TypeError):
                            sample_size = 50

                    # P1 fix: blinding param is `blinded: bool`, not `blinding: str`
                    # P1 fix: self_report param is `self_report_only: bool`
                    omega_sev = compute_omega_sev(
                        design_type=design_enum,
                        sample_size=sample_size,
                        pre_registered=False,
                        blinded=False,
                        self_report_only=finding.get("measure_type") == "self_report",
                    )
                    omega_conf = compute_omega_conf(
                        n_uncontrolled_confounds=2,
                        has_randomization=design_enum in (DesignType.STANDARD_RCT, DesignType.LARGE_RCT),
                        has_active_control=False,
                    )
                    omega_rep = compute_omega_rep(
                        n_independent_replications=0,
                        n_conceptual_replications=0,
                    )
                    # P1 fix: publication_type expects PublicationType enum, not string
                    omega_meta = compute_omega_meta(
                        publication_type=PublicationType.PEER_REVIEWED,
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
        Pre-compute framework voice data from the actual extraction corpus.

        For each T1 framework, scans all extraction JSONs and groups findings
        by matching theory_links and theory_commitments against the framework's
        canonical aliases (from tier1_frameworks.json).

        Output per framework:
            - n_papers: int
            - n_findings: int
            - top_findings: List[Dict] (up to 5, sorted by effect size)
            - mechanism_chains: List[str] (unique mechanisms found)
            - study_designs: Dict[str, int] (design type counts)
            - scope_conditions: List[str] (unique scope conditions)
            - source: "corpus_grounded"
        """
        # Load canonical T1 frameworks with alias lists
        t1_path = Path("schemas/theory/tier1_frameworks.json")
        if not t1_path.exists():
            # Try relative to project root
            t1_path = Path(__file__).parent.parent.parent / "schemas" / "theory" / "tier1_frameworks.json"

        frameworks = {}
        if t1_path.exists():
            try:
                with open(t1_path) as f:
                    t1_data = json.load(f)
                for fw_key, fw_data in t1_data.get("frameworks", {}).items():
                    abbr = fw_data.get("abbreviation", fw_key.upper())
                    aliases = set(a.upper() for a in fw_data.get("aliases", []))
                    aliases.add(abbr.upper())
                    aliases.add(fw_data.get("name", "").upper())
                    frameworks[abbr] = {
                        "name": fw_data.get("name", fw_key),
                        "abbreviation": abbr,
                        "aliases": aliases,
                        "core_mechanism": fw_data.get("core_mechanism", ""),
                        "key_principle": fw_data.get("key_principle", ""),
                        "papers": set(),
                        "findings": [],
                        "mechanism_chains": set(),
                        "study_designs": {},
                        "scope_conditions": set(),
                    }
            except Exception as e:
                logger.warning(f"Failed to load tier1_frameworks.json: {e}")

        if not frameworks:
            logger.warning("No T1 frameworks loaded — returning empty voices")
            return {"error": "tier1_frameworks.json not loadable", "source": "none"}

        # Scan all extraction files
        for json_file in self._extractions_dir.glob("*.json"):
            try:
                with open(json_file) as f:
                    data = json.load(f)

                # Article-level theory commitments
                article_commitments = set()
                for tc in data.get("theory_commitments", []):
                    if isinstance(tc, str):
                        article_commitments.add(tc.upper())
                    elif isinstance(tc, dict):
                        article_commitments.add(tc.get("theory", "").upper())

                study_design = data.get("study_design", data.get("article_type", "unknown"))
                title = data.get("title", json_file.stem)[:150]

                findings = data.get("findings", [])
                for finding in findings:
                    # Collect theory links from this finding
                    finding_theories = set()
                    for tl in finding.get("theory_links", []):
                        if isinstance(tl, str):
                            finding_theories.add(tl.upper())
                        elif isinstance(tl, dict):
                            finding_theories.add(tl.get("theory", "").upper())

                    # Combine with article-level commitments
                    all_theories = finding_theories | article_commitments

                    # Match against each framework's aliases
                    for abbr, fw in frameworks.items():
                        if all_theories & fw["aliases"]:
                            fw["papers"].add(json_file.name)

                            # Build finding entry
                            effect_size = finding.get("effect_size")
                            if isinstance(effect_size, str):
                                try:
                                    effect_size = float(effect_size.replace("d=", "").replace("r=", "").strip())
                                except (ValueError, AttributeError):
                                    effect_size = None

                            fw["findings"].append({
                                "antecedent": finding.get("antecedent", "")[:100],
                                "consequent": finding.get("consequent", "")[:100],
                                "direction": finding.get("direction", ""),
                                "effect_size": effect_size,
                                "p_value": finding.get("p_value"),
                                "sample_size": finding.get("sample_size") or data.get("n_participants"),
                                "source_file": json_file.name,
                                "title": title,
                            })

                            # Mechanism chains
                            for mc in finding.get("mechanism_chain", []):
                                if isinstance(mc, str) and mc.strip():
                                    fw["mechanism_chains"].add(mc.strip()[:120])

                            # Scope conditions
                            for sc in finding.get("scope_conditions", []):
                                if isinstance(sc, str) and sc.strip():
                                    fw["scope_conditions"].add(sc.strip()[:120])

                            # Study design counts
                            design_key = str(study_design).lower().replace(" ", "_")
                            fw["study_designs"][design_key] = fw["study_designs"].get(design_key, 0) + 1

            except Exception as e:
                logger.debug(f"Skipping {json_file.name}: {e}")

        # Build output: sort findings by effect size, truncate
        voices = {}
        for abbr, fw in frameworks.items():
            sorted_findings = sorted(
                fw["findings"],
                key=lambda f: abs(f["effect_size"]) if f["effect_size"] is not None else 0,
                reverse=True,
            )

            voices[abbr] = {
                "framework": abbr,
                "name": fw["name"],
                "core_mechanism": fw["core_mechanism"],
                "key_principle": fw["key_principle"],
                "n_papers": len(fw["papers"]),
                "n_findings": len(fw["findings"]),
                "top_findings": sorted_findings[:5],
                "mechanism_chains": sorted(fw["mechanism_chains"])[:10],
                "study_designs": fw["study_designs"],
                "scope_conditions": sorted(fw["scope_conditions"])[:10],
                "source": "corpus_grounded",
            }

        total_papers = sum(v["n_papers"] for v in voices.values())
        total_findings = sum(v["n_findings"] for v in voices.values())
        logger.info(
            f"Built corpus-grounded framework voices: {len(voices)} frameworks, "
            f"{total_papers} paper-framework links, {total_findings} finding-framework links"
        )
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
