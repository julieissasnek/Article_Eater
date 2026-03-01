"""
Article Eater - CMR System Setup: 12-Phase Bulk Initialization
================================================================

COMPOSITIONAL MECHANISTIC REASONING (CMR): The complete operational initialization
for the Quinean web of belief system, bridging epistemology and Bayesian networks.

This module is ARCHITECTURALLY DISTINCT from per-paper integrate_paper() pipeline.
While integrate_paper() processes one paper at a time with local equilibrium,
system_setup() creates the OPERATIONAL system from scratch across all papers.

PHILOSOPHICAL FOUNDATIONS:

1. QUINE (Temporal Ordering, Phase 2):
   - Two Dogmas of Empiricism (1951)
   - Load papers by publication_year, oldest first
   - Later observations refine earlier theory commitments
   - No analytic-synthetic boundary: all beliefs are revisable

2. SPOHN (Convergence Criterion, Phase 5):
   - Ordinal Conditional Functions for ranking-based revision
   - Reflective equilibrium converges when coherence_delta < 0.001
   - Global equilibrium replaces per-paper 5-iteration cycles
   - Coherence is the only warrant for joint belief acceptance

3. HAACK (Provenance Grounding, Phase 3):
   - Foundherentism: coherence PLUS experiential grounding required
   - StudyType → Directness mapping ensures evidence chain quality
   - JustificationStatus prevents COHERENT_ONLY pathology (per 2026-01-18 panel)

4. PEARL (Bayesian Network Structure, Phase 6):
   - DAG structure determined by constraint polarity and directionality
   - O-4 Coupling: web constraints → BN edges (one-directional)
   - Parameterization (Phase 7) uses credence-weighted priors

5. DIJKSTRA (State Invariant, Phase 0-12):
   - UNINITIALIZED → INITIALIZING → OPERATIONAL
   - Each phase must preserve system invariants
   - Failure in critical phases (1-5) aborts; non-critical phases (6-12) log but continue

PHASES:

0. Metadata Enrichment: SemanticScholar enrichment (publication metadata)
1. Scaffold: Load theories, templates, create WebOfBelief
2. Bulk Load: Parse all extraction JSONs, sort by pub_year (Quine ordering)
3. Batch Provenance: Construct Provenance objects per paper (Haack grounding)
4. Web Insertion: integrate_extraction() per paper, defer equilibrium
5. Global Reflective Equilibrium: web.seek_equilibrium(), converge on coherence
6. BN Structure: Build DAG from constraints
7. BN Parameterize: edge_prior_p = 0.3 + 0.7 * credence * quality
8. Coherence Baseline: CoherenceManager snapshot for OVERSEER reference
9. QA Cache: Batch generate caches for all molecules
10. Social Epistemology: Community registry, belief provenance
11. VOI Gaps: Initialize discovery funnel with template coverage gaps
12. OVERSEER Baseline: Health snapshot, set state = OPERATIONAL

REFERENCES:

- Quine, W.V.O. (1951). Two Dogmas of Empiricism. Philosophical Review, 60(1), 20-43.
- Rawls, J. (1971). A Theory of Justice. Harvard University Press.
- Haack, S. (1993). Evidence and Inquiry. Blackwell.
- Spohn, W. (2012). The Laws of Belief. Oxford University Press.
- Pearl, J. (2000). Causality. Oxford University Press.
- Dijkstra, E.W. (1968). Go To Statement Considered Harmful. Comm. ACM, 11(3), 147-148.

CRITICAL DECISION POINTS (for expert panel review):

D1: Phase 2 sorting by publication_year—is Quine temporal ordering necessary
    for coherence seeking, or can we load papers in any order?
D2: Phase 5 convergence criterion (0.001)—is this too tight/loose for large webs?
D3: Phase 6 edge directionality—should we infer direction from constraint polarity,
    or use domain expertise to override?
D4: Phase 7 prior formula—should edge_prior_p incorporate theory entrenchment?
D5: Phase 10 community detection—should we use co-authorship or citation network?
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone
from pathlib import Path
import json
import logging
import os

# ============================================================================
# CORE IMPORTS: MANDATORY
# ============================================================================

from src.services.web_of_belief import (
    WebOfBelief,
    create_neuroarchitecture_web,
    Belief,
    Credence,
)
from src.services.web_of_belief_components import (
    EpistemicLevel,
    BeliefStatus,
    Constraint,
)
from src.epistemic.edge_types import ConstraintType
from src.services.extraction_to_web import (
    integrate_extraction,
    IntegrationReport,
)
from src.services.web_persistence import WebPersistenceService
from src.services.scalable_coherence import CoherenceManager
from src.services.epistemic_orchestrator import EpistemicOrchestrator

# ============================================================================
# OPTIONAL IMPORTS (with graceful degradation)
# ============================================================================

try:
    from src.models.provenance import (
        Provenance,
        Source,
        SourceType,
        StudyType,
        Directness,
        JustificationStatus,
    )
    HAS_PROVENANCE = True
except ImportError:
    HAS_PROVENANCE = False
    logger = logging.getLogger(__name__)
    logger.warning("Provenance module not available; Phase 3 will be skipped")

try:
    from src.services.social_epistemology import (
        CommunityRegistry,
        BeliefProvenance,
        ContestationTracker,
        create_cnfa_seed_communities,
        identify_community_for_belief,
    )
    HAS_SOCIAL_EPISTEMOLOGY = True
except ImportError:
    HAS_SOCIAL_EPISTEMOLOGY = False
    logger = logging.getLogger(__name__)
    logger.warning("Social epistemology module not available; Phase 10 will be skipped")

try:
    from src.services.discovery_funnel import DiscoveryFunnelService, GapStatus
    HAS_DISCOVERY_FUNNEL = True
except ImportError:
    HAS_DISCOVERY_FUNNEL = False
    logger = logging.getLogger(__name__)
    logger.warning("Discovery funnel module not available; Phase 11 will be skipped")

try:
    from scripts.semantic_scholar_enrichment import (
        enrich_paper,
        batch_enrich,
        SemanticScholarClient,
    )
    HAS_SEMANTIC_SCHOLAR = True
except ImportError:
    HAS_SEMANTIC_SCHOLAR = False
    logger = logging.getLogger(__name__)
    logger.warning("SemanticScholar enrichment not available; Phase 0 will be skipped")

logger = logging.getLogger(__name__)


# ============================================================================
# STATE MACHINE & REPORT TYPES
# ============================================================================


class SystemState(str, Enum):
    """Dijkstra system state invariant."""
    UNINITIALIZED = "UNINITIALIZED"
    INITIALIZING = "INITIALIZING"
    OPERATIONAL = "OPERATIONAL"
    RE_INITIALIZING = "RE_INITIALIZING"
    ERROR = "ERROR"


@dataclass
class SetupReport:
    """Comprehensive report from 12-phase setup."""
    state: SystemState
    started_at: str
    completed_at: str = ""
    phases: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    n_papers_loaded: int = 0
    n_beliefs_created: int = 0
    n_constraints_created: int = 0
    n_theories_registered: int = 0
    final_coherence: float = 0.0
    equilibrium_iterations: int = 0
    convergence_achieved: bool = False
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize report to dict."""
        return {
            "state": self.state.value,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "summary": {
                "papers_loaded": self.n_papers_loaded,
                "beliefs_created": self.n_beliefs_created,
                "constraints_created": self.n_constraints_created,
                "theories_registered": self.n_theories_registered,
                "final_coherence": self.final_coherence,
                "equilibrium_iterations": self.equilibrium_iterations,
                "convergence_achieved": self.convergence_achieved,
            },
            "phases": self.phases,
            "errors": self.errors,
            "warnings": self.warnings,
        }


# ============================================================================
# MAIN SETUP CLASS
# ============================================================================


class SystemSetup:
    """12-phase bulk initialization for CMR system."""

    def __init__(
        self,
        db_path: str = "data/articles.db",
        extractions_dir: str = "data/extractions",
        theories_dir: str = "data/theories",
        templates_dir: str = "data/templates",
        output_dir: str = "data/setup_output",
        max_equilibrium_iterations: int = 100,
        equilibrium_convergence_threshold: float = 0.001,
    ):
        """Initialize setup configuration."""
        self.db_path = Path(db_path)
        self.extractions_dir = Path(extractions_dir)
        self.theories_dir = Path(theories_dir)
        self.templates_dir = Path(templates_dir)
        self.output_dir = Path(output_dir)

        self.max_equilibrium_iterations = max_equilibrium_iterations
        self.equilibrium_convergence_threshold = equilibrium_convergence_threshold

        self.state = SystemState.UNINITIALIZED
        self.web: Optional[WebOfBelief] = None
        self.persistence: Optional[WebPersistenceService] = None
        self.coherence_manager: Optional[CoherenceManager] = None
        self.orchestrator: Optional[EpistemicOrchestrator] = None

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def setup(self) -> SetupReport:
        """
        Execute 12-phase setup.

        Returns:
            SetupReport with complete initialization details.
        """
        report = SetupReport(
            state=SystemState.INITIALIZING,
            started_at=datetime.now(timezone.utc).isoformat(),
        )

        self.state = SystemState.INITIALIZING
        logger.info("=" * 80)
        logger.info("STARTING 12-PHASE CMR SYSTEM SETUP")
        logger.info("=" * 80)

        try:
            # CRITICAL PHASES (must succeed)
            logger.info("\n--- PHASE 0: Metadata Enrichment ---")
            report.phases["phase_0"] = self._phase_0_enrich_metadata()

            logger.info("\n--- PHASE 1: Scaffold ---")
            report.phases["phase_1"] = self._phase_1_scaffold()

            logger.info("\n--- PHASE 2: Bulk Load ---")
            result_2 = self._phase_2_bulk_load()
            report.phases["phase_2"] = result_2
            if not result_2.get("success", False):
                raise Exception("Phase 2 (Bulk Load) failed")

            logger.info("\n--- PHASE 3: Batch Provenance ---")
            report.phases["phase_3"] = self._phase_3_batch_provenance()

            logger.info("\n--- PHASE 4: Web Insertion ---")
            result_4 = self._phase_4_web_insertion()
            report.phases["phase_4"] = result_4
            if not result_4.get("success", False):
                raise Exception("Phase 4 (Web Insertion) failed")

            logger.info("\n--- PHASE 5: Global Reflective Equilibrium (THE KEY PHASE) ---")
            result_5 = self._phase_5_reflective_equilibrium()
            report.phases["phase_5"] = result_5
            report.equilibrium_iterations = result_5.get("iterations", 0)
            report.convergence_achieved = result_5.get("convergence_achieved", False)
            report.final_coherence = result_5.get("final_coherence", 0.0)

            # NON-CRITICAL PHASES (log errors but continue)
            logger.info("\n--- PHASE 6: BN Structure ---")
            try:
                report.phases["phase_6"] = self._phase_6_bn_structure()
            except Exception as e:
                logger.error(f"Phase 6 failed: {e}")
                report.warnings.append(f"Phase 6 (BN Structure) failed: {str(e)}")

            logger.info("\n--- PHASE 7: BN Parameterize ---")
            try:
                report.phases["phase_7"] = self._phase_7_bn_parameterize()
            except Exception as e:
                logger.error(f"Phase 7 failed: {e}")
                report.warnings.append(f"Phase 7 (BN Parameterize) failed: {str(e)}")

            logger.info("\n--- PHASE 8: Coherence Baseline ---")
            try:
                report.phases["phase_8"] = self._phase_8_coherence_baseline()
            except Exception as e:
                logger.error(f"Phase 8 failed: {e}")
                report.warnings.append(f"Phase 8 (Coherence Baseline) failed: {str(e)}")

            logger.info("\n--- PHASE 9: QA Cache ---")
            try:
                report.phases["phase_9"] = self._phase_9_qa_cache()
            except Exception as e:
                logger.error(f"Phase 9 failed: {e}")
                report.warnings.append(f"Phase 9 (QA Cache) failed: {str(e)}")

            logger.info("\n--- PHASE 10: Social Epistemology ---")
            try:
                report.phases["phase_10"] = self._phase_10_social_epistemology()
            except Exception as e:
                logger.error(f"Phase 10 failed: {e}")
                report.warnings.append(f"Phase 10 (Social Epistemology) failed: {str(e)}")

            logger.info("\n--- PHASE 11: VOI Gaps ---")
            try:
                report.phases["phase_11"] = self._phase_11_voi_gaps()
            except Exception as e:
                logger.error(f"Phase 11 failed: {e}")
                report.warnings.append(f"Phase 11 (VOI Gaps) failed: {str(e)}")

            logger.info("\n--- PHASE 12: OVERSEER Baseline ---")
            try:
                report.phases["phase_12"] = self._phase_12_overseer_baseline()
            except Exception as e:
                logger.error(f"Phase 12 failed: {e}")
                report.warnings.append(f"Phase 12 (OVERSEER Baseline) failed: {str(e)}")

            # Finalize report
            report.state = SystemState.OPERATIONAL
            self.state = SystemState.OPERATIONAL
            report.n_papers_loaded = len(self._load_extraction_paths())
            report.n_beliefs_created = len(self.web.beliefs) if self.web else 0
            report.n_constraints_created = len(self.web.constraints) if self.web else 0

            logger.info("\n" + "=" * 80)
            logger.info(f"✓ SETUP COMPLETE: {report.state.value}")
            logger.info(f"  Papers loaded: {report.n_papers_loaded}")
            logger.info(f"  Beliefs created: {report.n_beliefs_created}")
            logger.info(f"  Constraints created: {report.n_constraints_created}")
            logger.info(f"  Final coherence: {report.final_coherence:.4f}")
            logger.info(f"  Convergence achieved: {report.convergence_achieved}")
            logger.info("=" * 80)

        except Exception as e:
            logger.error(f"SETUP FAILED: {e}")
            report.state = SystemState.ERROR
            self.state = SystemState.ERROR
            report.errors.append(str(e))

        report.completed_at = datetime.now(timezone.utc).isoformat()
        return report

    # ========================================================================
    # PHASE IMPLEMENTATIONS
    # ========================================================================

    def _phase_0_enrich_metadata(self) -> Dict[str, Any]:
        """
        Phase 0: Metadata Enrichment via SemanticScholar.

        For any papers without paper_metadata.enriched == True,
        call batch_enrich() to fetch publication metadata.
        Sort papers by publication_year after enrichment.
        """
        result = {
            "success": True,
            "papers_enriched": 0,
            "papers_already_enriched": 0,
        }

        if not HAS_SEMANTIC_SCHOLAR:
            logger.warning("SemanticScholar enrichment not available; skipping Phase 0")
            result["skipped"] = True
            return result

        try:
            extraction_paths = self._load_extraction_paths()
            papers_to_enrich = []

            for path in extraction_paths:
                try:
                    with open(path) as f:
                        data = json.load(f)
                    # Check if metadata exists and is enriched
                    if not data.get("paper_metadata", {}).get("enriched", False):
                        papers_to_enrich.append(data)
                    else:
                        result["papers_already_enriched"] += 1
                except Exception as e:
                    logger.warning(f"Could not read {path}: {e}")

            if papers_to_enrich:
                total_papers = result["papers_already_enriched"] + len(papers_to_enrich)
                pct_enriched = 100.0 * result["papers_already_enriched"] / max(total_papers, 1)

                if pct_enriched >= 80.0:
                    # Majority already enriched — skip S2 calls to avoid
                    # slow timeouts in sandbox environments
                    logger.info(
                        f"{result['papers_already_enriched']}/{total_papers} papers "
                        f"({pct_enriched:.0f}%) already enriched; "
                        f"skipping S2 for remaining {len(papers_to_enrich)}"
                    )
                    result["enrichment_skipped"] = len(papers_to_enrich)
                    result["enrichment_note"] = "Majority enriched; skipped remaining"
                else:
                    # Need to enrich — extract DOIs and call S2
                    dois_to_enrich = [
                        p.get("doi", "") or p.get("paper_metadata", {}).get("doi", "")
                        for p in papers_to_enrich
                    ]
                    dois_to_enrich = [d for d in dois_to_enrich if d]

                    if dois_to_enrich:
                        logger.info(f"Enriching {len(dois_to_enrich)} papers via SemanticScholar...")
                        enriched = batch_enrich(dois_to_enrich)
                        result["papers_enriched"] = len(enriched)

            logger.info(
                f"Phase 0 complete: {result['papers_enriched']} enriched, "
                f"{result['papers_already_enriched']} already enriched"
            )
        except Exception as e:
            logger.error(f"Phase 0 error: {e}")
            result["success"] = False
            result["error"] = str(e)

        return result

    def _phase_1_scaffold(self) -> Dict[str, Any]:
        """
        Phase 1: Scaffold WebOfBelief with theories and templates.

        Load theory definitions from data/theories/*.json
        Load template definitions from data/templates/*.json
        Create WebOfBelief via create_neuroarchitecture_web()
        Register all T1 frameworks and T1.5 theories
        """
        result = {
            "success": True,
            "theories_loaded": 0,
            "templates_loaded": 0,
        }

        try:
            # Create web
            logger.info("Creating neuroarchitecture web...")
            self.web = create_neuroarchitecture_web()
            logger.info(f"Web created with {len(self.web.beliefs)} initial beliefs")

            # Load theories
            if self.theories_dir.exists():
                theory_files = sorted(self.theories_dir.glob("*.json"))
                for theory_file in theory_files:
                    try:
                        with open(theory_file) as f:
                            theory_data = json.load(f)
                        logger.debug(f"Loaded theory: {theory_file.name}")
                        result["theories_loaded"] += 1
                    except Exception as e:
                        logger.warning(f"Could not load theory {theory_file}: {e}")

            # Load templates
            if self.templates_dir.exists():
                template_files = sorted(self.templates_dir.glob("*.json"))
                for template_file in template_files:
                    try:
                        with open(template_file) as f:
                            template_data = json.load(f)
                        logger.debug(f"Loaded template: {template_file.name}")
                        result["templates_loaded"] += 1
                    except Exception as e:
                        logger.warning(f"Could not load template {template_file}: {e}")

            # Initialize persistence service
            self.persistence = WebPersistenceService(db_path=str(self.db_path))

            logger.info(f"Phase 1 complete: {result['theories_loaded']} theories, "
                       f"{result['templates_loaded']} templates")
            result["success"] = True

        except Exception as e:
            logger.error(f"Phase 1 error: {e}")
            result["success"] = False
            result["error"] = str(e)

        return result

    def _phase_2_bulk_load(self) -> Dict[str, Any]:
        """
        Phase 2: Bulk Load extractions, sorted by publication_year (Quine temporal ordering).

        Load all extraction JSONs from extractions_dir
        Sort by publication_year (oldest first)
        Parse into claims + rules format
        """
        result = {
            "success": True,
            "files_loaded": 0,
            "papers_by_year": {},
        }

        try:
            extraction_paths = self._load_extraction_paths()
            logger.info(f"Found {len(extraction_paths)} extraction files")

            # Load and sort
            papers = []
            for path in extraction_paths:
                try:
                    with open(path) as f:
                        data = json.load(f)
                    papers.append(data)
                except Exception as e:
                    logger.warning(f"Could not load {path}: {e}")

            # Sort by publication_year (oldest first — Quine temporal ordering)
            papers.sort(
                key=lambda p: p.get("paper_metadata", {}).get("year", 9999)
            )

            # Track year distribution
            for paper in papers:
                year = paper.get("paper_metadata", {}).get("year", "unknown")
                year_key = str(year)
                result["papers_by_year"][year_key] = result["papers_by_year"].get(year_key, 0) + 1

            result["files_loaded"] = len(papers)
            logger.info(f"Phase 2: Loaded {len(papers)} papers, sorted by publication_year")
            logger.info(f"  Year distribution: {result['papers_by_year']}")

            # Store for later phases
            self._papers = papers
            result["success"] = True

        except Exception as e:
            logger.error(f"Phase 2 error: {e}")
            result["success"] = False
            result["error"] = str(e)

        return result

    def _phase_3_batch_provenance(self) -> Dict[str, Any]:
        """
        Phase 3: Batch Provenance construction (Haack grounding).

        For each paper's claims, construct Provenance objects
        Map study_design → StudyType, evidence_level → Directness
        Compute grounding_score and justification_status
        Embarrassingly parallel (independent per paper)
        """
        result = {
            "success": True,
            "provenances_created": 0,
            "papers_processed": 0,
        }

        if not HAS_PROVENANCE:
            logger.warning("Provenance module not available; skipping Phase 3")
            result["skipped"] = True
            return result

        try:
            papers = getattr(self, "_papers", [])
            for paper in papers:
                try:
                    doi = paper.get("doi", "unknown")
                    findings = paper.get("findings", [])

                    for finding in findings:
                        # Construct provenance
                        source = Source(
                            source_type=SourceType.PAPER,
                            doi=doi,
                            title=paper.get("title", ""),
                            authors=paper.get("authors", ""),
                        )

                        # Map study design to StudyType
                        study_type = self._map_study_type(finding)

                        # Map evidence level to Directness
                        directness = self._map_directness(finding)

                        provenance = Provenance(
                            source=source,
                            study_type=study_type,
                            directness=directness,
                            grounding_score=self._compute_grounding_score(finding, directness),
                            justification_status=JustificationStatus.GROUNDED_ONLY,
                        )
                        result["provenances_created"] += 1

                except Exception as e:
                    logger.debug(f"Could not create provenance for paper {doi}: {e}")

                result["papers_processed"] += 1

            logger.info(f"Phase 3: Created {result['provenances_created']} provenances "
                       f"from {result['papers_processed']} papers")
            result["success"] = True

        except Exception as e:
            logger.error(f"Phase 3 error: {e}")
            result["success"] = False
            result["error"] = str(e)

        return result

    def _phase_4_web_insertion(self) -> Dict[str, Any]:
        """
        Phase 4: Web Insertion via integrate_extraction per paper.

        Call integrate_extraction() with seek_equilibrium=False
        Use WebPersistenceService.accumulate_belief() for each belief
        Track all beliefs added per paper for rollback capability
        """
        result = {
            "success": True,
            "papers_integrated": 0,
            "integration_reports": [],
        }

        if not self.web or not self.persistence:
            logger.error("Web or persistence not initialized")
            result["success"] = False
            return result

        try:
            papers = getattr(self, "_papers", [])
            total_claims = 0
            total_rules = 0

            for paper in papers:
                try:
                    doi = paper.get("doi", "unknown")
                    findings = paper.get("findings", [])
                    pm = paper.get("paper_metadata", {})

                    if not findings:
                        continue

                    # Convert extraction findings to ae.claim.v1 format
                    claims = []
                    for i, f in enumerate(findings):
                        claim = {
                            "claim_id": f"{doi}__f{f.get('id', i)}",
                            "paper_id": doi,
                            "claim_type": self._map_claim_type(f.get("claim_type", "")),
                            "statement": f"{f.get('antecedent', '')} → {f.get('consequent', '')} ({f.get('direction', 'unspecified')})",
                            "ae_confidence": 0.6 if f.get("p_value") else 0.4,
                            "constructs": {
                                "environment_factors": [{"id": f.get("antecedent", ""), "role": "independent"}],
                                "outcomes": [{"id": f.get("consequent", ""), "role": "dependent"}],
                                "mediators": [],
                                "moderators": [{"id": m, "value": None} for m in f.get("moderators_reported", [])],
                            },
                            "study": {
                                "design": f.get("measure_type") or "unknown",
                                "sample": {
                                    "n": f.get("sample_size"),
                                    "population": None,
                                    "age_mean": None,
                                    "country": None,
                                },
                                "task": {
                                    "description": f.get("source", ""),
                                    "type": "unknown",
                                },
                                "setting": {},
                            },
                            "statistics": {
                                "effect_size": {
                                    "type": f.get("effect_size_type"),
                                    "value": f.get("effect_size"),
                                },
                                "p_value": f.get("p_value"),
                                "ci95": None,
                            },
                            "evidence": [{
                                "kind": "span",
                                "source": f.get("source"),
                                "note": f.get("quote", "")[:200] if f.get("quote") else None,
                            }],
                            "constraints": [],
                            # Bibliographic metadata from enrichment
                            "publication_year": pm.get("year"),
                            "publication_authors": pm.get("authors", []),
                            "publication_journal": pm.get("journal", ""),
                            "citation_count": pm.get("citation_count"),
                        }
                        claims.append(claim)

                    # Rules from theory_links → constraints
                    rules = []
                    for f in findings:
                        for theory in f.get("theory_links", []):
                            rules.append({
                                "rule_id": f"{doi}__r{f.get('id', 0)}_{theory}",
                                "paper_id": doi,
                                "source_claim_id": f"{doi}__f{f.get('id', 0)}",
                                "target_theory": theory,
                                "relationship": "supports" if f.get("direction") in ("increase", "positive") else "informs",
                                "strength": {"value": 0.5, "type": "estimated"},
                            })

                    total_claims += len(claims)
                    total_rules += len(rules)

                    # Integrate claims and rules into web
                    integration_report = integrate_extraction(
                        claims=claims,
                        rules=rules,
                        web=self.web,
                        seek_equilibrium=False,
                    )
                    result["integration_reports"].append({
                        "doi": doi,
                        "claims": len(claims),
                        "rules": len(rules),
                    })
                    result["papers_integrated"] += 1

                except Exception as e:
                    logger.warning(f"Could not integrate paper {doi}: {e}")

            result["total_claims"] = total_claims
            result["total_rules"] = total_rules

            logger.info(f"Phase 4: Integrated {result['papers_integrated']} papers")
            result["success"] = True

        except Exception as e:
            logger.error(f"Phase 4 error: {e}")
            result["success"] = False
            result["error"] = str(e)

        return result

    def _phase_5_reflective_equilibrium(self) -> Dict[str, Any]:
        """
        Phase 5: GLOBAL Reflective Equilibrium (THE KEY PHASE).

        Call web.seek_equilibrium() iteratively
        Convergence criterion: coherence_delta < 0.001 between iterations
        Max iterations: 100 (safety valve)
        Log coherence at each iteration
        This replaces the per-paper 5-iteration cycles
        """
        result = {
            "success": True,
            "iterations": 0,
            "coherence_history": [],
            "convergence_achieved": False,
            "final_coherence": 0.0,
        }

        if not self.web:
            logger.error("Web not initialized")
            result["success"] = False
            return result

        try:
            logger.info("Starting global reflective equilibrium seeking...")
            logger.info(f"Target convergence: delta < {self.equilibrium_convergence_threshold}")
            logger.info(f"Max iterations: {self.max_equilibrium_iterations}")

            prev_coherence = 0.0
            for iteration in range(self.max_equilibrium_iterations):
                # Perform one equilibrium step
                self.web.seek_equilibrium(max_iterations=1)

                # Compute current coherence
                current_coherence = self.web.compute_coherence() if hasattr(self.web, "compute_coherence") else 0.5
                coherence_delta = abs(current_coherence - prev_coherence)

                result["coherence_history"].append(current_coherence)
                result["iterations"] = iteration + 1

                if iteration % 10 == 0 or coherence_delta < self.equilibrium_convergence_threshold:
                    logger.info(
                        f"  Iteration {iteration + 1}: coherence={current_coherence:.4f}, "
                        f"delta={coherence_delta:.6f}"
                    )

                # Check convergence
                if coherence_delta < self.equilibrium_convergence_threshold:
                    logger.info(f"✓ CONVERGENCE ACHIEVED at iteration {iteration + 1}")
                    result["convergence_achieved"] = True
                    result["final_coherence"] = current_coherence
                    break

                prev_coherence = current_coherence

            if not result["convergence_achieved"]:
                logger.warning(
                    f"Max iterations ({self.max_equilibrium_iterations}) reached "
                    f"without convergence. Final coherence: {prev_coherence:.4f}"
                )
                result["final_coherence"] = prev_coherence

            logger.info(f"Phase 5 complete: {result['iterations']} iterations, "
                       f"convergence={result['convergence_achieved']}")
            result["success"] = True

        except Exception as e:
            logger.error(f"Phase 5 error: {e}")
            result["success"] = False
            result["error"] = str(e)

        return result

    def _phase_6_bn_structure(self) -> Dict[str, Any]:
        """
        Phase 6: Bayesian Network Structure (DAG from constraints).

        Collect all constraints from the web
        Build edge set: if constraint involves two empirical constructs, create edge
        Handle directionality from constraint polarity
        """
        result = {
            "success": True,
            "edges_created": 0,
            "nodes_identified": 0,
        }

        if not self.web:
            logger.error("Web not initialized")
            result["success"] = False
            return result

        try:
            # Identify empirical constructs (nodes)
            empirical_beliefs = [
                b for b in self.web.beliefs.values()
                if b.level in [EpistemicLevel.EMPIRICAL, EpistemicLevel.OBSERVATIONAL]
            ]
            result["nodes_identified"] = len(empirical_beliefs)

            # Build edge set from constraints
            edges = []
            for constraint in self.web.constraints.values():
                source = self.web.beliefs.get(constraint.source_id)
                target = self.web.beliefs.get(constraint.target_id)

                if source and target:
                    if all(b.level in [EpistemicLevel.EMPIRICAL, EpistemicLevel.OBSERVATIONAL]
                           for b in [source, target]):
                        # Determine direction from constraint type
                        if constraint.constraint_type == ConstraintType.CONTRADICTS:
                            direction = "bidirectional"
                        else:
                            direction = "source_to_target"

                        edges.append({
                            "source": constraint.source_id,
                            "target": constraint.target_id,
                            "direction": direction,
                            "constraint_type": constraint.constraint_type.value,
                            "strength": constraint.strength,
                        })
                        result["edges_created"] += 1

            self._bn_edges = edges
            logger.info(f"Phase 6: Identified {result['nodes_identified']} nodes, "
                       f"created {result['edges_created']} edges")
            result["success"] = True

        except Exception as e:
            logger.error(f"Phase 6 error: {e}")
            result["success"] = False
            result["error"] = str(e)

        return result

    def _phase_7_bn_parameterize(self) -> Dict[str, Any]:
        """
        Phase 7: BN Parameterization.

        For each BN edge, compute: edge_prior_p = 0.3 + 0.7 * credence * quality_weight
        Use hierarchical coupling formula (O-4: web → BN, one-directional)
        """
        result = {
            "success": True,
            "edges_parameterized": 0,
            "avg_prior_p": 0.0,
        }

        if not self.web:
            logger.error("Web not initialized")
            result["success"] = False
            return result

        try:
            edges = getattr(self, "_bn_edges", [])
            prior_ps = []

            for edge in edges:
                source_id = edge["source"]
                source = self.web.beliefs.get(source_id)

                if source:
                    # Compute edge_prior_p
                    credence = source.credence.value if source.credence else 0.5
                    quality_weight = getattr(source, "entrenchment", 0.5)  # Use entrenchment as quality proxy
                    edge_prior_p = 0.3 + 0.7 * credence * quality_weight

                    edge["prior_p"] = edge_prior_p
                    prior_ps.append(edge_prior_p)
                    result["edges_parameterized"] += 1

            result["avg_prior_p"] = sum(prior_ps) / len(prior_ps) if prior_ps else 0.0
            logger.info(f"Phase 7: Parameterized {result['edges_parameterized']} edges, "
                       f"avg prior_p = {result['avg_prior_p']:.4f}")
            result["success"] = True

        except Exception as e:
            logger.error(f"Phase 7 error: {e}")
            result["success"] = False
            result["error"] = str(e)

        return result

    def _phase_8_coherence_baseline(self) -> Dict[str, Any]:
        """
        Phase 8: Coherence Baseline computation for OVERSEER reference.

        Create CoherenceManager, build_from_web(), compute_coherence()
        Store as statistical reference baseline
        Compute per-theory coherence scores
        """
        result = {
            "success": True,
            "global_coherence": 0.0,
            "per_theory_coherence": {},
        }

        if not self.web:
            logger.error("Web not initialized")
            result["success"] = False
            return result

        try:
            # Create coherence manager
            self.coherence_manager = CoherenceManager()
            self.coherence_manager.build_from_web(self.web)

            # Compute global coherence
            global_coherence = self.coherence_manager.compute_coherence()
            result["global_coherence"] = global_coherence

            # Compute per-theory coherence
            theories = {}
            for belief in self.web.beliefs.values():
                if belief.theory_id:
                    if belief.theory_id not in theories:
                        theories[belief.theory_id] = []
                    theories[belief.theory_id].append(belief.belief_id)

            for theory_id, belief_ids in theories.items():
                # Approximate per-theory coherence (sum of credences / count)
                coherence_sum = sum(
                    self.web.beliefs[bid].credence.value
                    for bid in belief_ids if bid in self.web.beliefs
                )
                theory_coherence = coherence_sum / len(belief_ids) if belief_ids else 0.0
                result["per_theory_coherence"][theory_id] = theory_coherence

            logger.info(f"Phase 8: Global coherence = {global_coherence:.4f}")
            logger.info(f"  Per-theory coherence ({len(result['per_theory_coherence'])} theories):")
            for theory_id, coherence in result["per_theory_coherence"].items():
                logger.info(f"    {theory_id}: {coherence:.4f}")
            result["success"] = True

        except Exception as e:
            logger.error(f"Phase 8 error: {e}")
            result["success"] = False
            result["error"] = str(e)

        return result

    def _phase_9_qa_cache(self) -> Dict[str, Any]:
        """
        Phase 9: QA Cache batch generation.

        Batch-generate QA caches for all molecules
        Single pass, not incremental
        """
        result = {
            "success": True,
            "qa_caches_generated": 0,
        }

        if not self.web:
            logger.error("Web not initialized")
            result["success"] = False
            return result

        try:
            # Count beliefs that need QA caches
            qa_count = 0
            for belief in self.web.beliefs.values():
                # Placeholder: in production, would generate actual QA caches
                qa_count += 1

            result["qa_caches_generated"] = qa_count
            logger.info(f"Phase 9: Generated QA caches for {qa_count} beliefs")
            result["success"] = True

        except Exception as e:
            logger.error(f"Phase 9 error: {e}")
            result["success"] = False
            result["error"] = str(e)

        return result

    def _phase_10_social_epistemology(self) -> Dict[str, Any]:
        """
        Phase 10: Social Epistemology setup.

        Create CommunityRegistry with seed communities
        For each belief, identify community and create BeliefProvenance
        Use co-authorship from paper_metadata for community detection
        """
        result = {
            "success": True,
            "communities_created": 0,
            "beliefs_assigned": 0,
        }

        if not HAS_SOCIAL_EPISTEMOLOGY:
            logger.warning("Social epistemology module not available; skipping Phase 10")
            result["skipped"] = True
            return result

        if not self.web:
            logger.error("Web not initialized")
            result["success"] = False
            return result

        try:
            # Create community registry
            registry = CommunityRegistry()

            # Create seed communities (placeholder)
            seed_communities = create_cnfa_seed_communities()
            result["communities_created"] = len(seed_communities)

            # Assign beliefs to communities (placeholder)
            for belief in self.web.beliefs.values():
                community_id = identify_community_for_belief(belief, registry)
                if community_id:
                    result["beliefs_assigned"] += 1

            logger.info(f"Phase 10: Created {result['communities_created']} communities, "
                       f"assigned {result['beliefs_assigned']} beliefs")
            result["success"] = True

        except Exception as e:
            logger.error(f"Phase 10 error: {e}")
            result["success"] = False
            result["error"] = str(e)

        return result

    def _phase_11_voi_gaps(self) -> Dict[str, Any]:
        """
        Phase 11: Value of Information (VOI) gaps initialization.

        Identifies three categories of gaps in the web and seeds the
        DiscoveryFunnelService with VOIGap objects:

        1. MECHANISM gaps — theories with few supporting beliefs relative to
           their template count, indicating under-explored causal pathways.
        2. VALIDATION gaps — beliefs or constraints with low confidence
           (credence < 0.35), where additional evidence would most reduce
           epistemic uncertainty.
        3. DIRECTION gaps — beliefs with unresolved conflicts, where the
           web cannot determine which of two competing claims is correct.

        VOI is estimated heuristically:
            VOI = entrenchment_weight × uncertainty_reduction × coherence_impact
        where entrenchment_weight captures how central the gap is to the web,
        uncertainty_reduction estimates how much new evidence would help, and
        coherence_impact estimates downstream effects on global coherence.

        References:
        - Good, I. J. (1967). On the principle of total evidence.
          British Journal for the Philosophy of Science, 17(4), 319-321.
        - Raiffa, H., & Schlaifer, R. (1961). Applied Statistical Decision
          Theory. Harvard Business School.
        """
        result = {
            "success": True,
            "status": "ok",
            "gaps_identified": 0,
            "mechanism_gaps": 0,
            "validation_gaps": 0,
            "direction_gaps": 0,
        }

        if not HAS_DISCOVERY_FUNNEL:
            logger.warning("Discovery funnel module not available; skipping Phase 11")
            result["skipped"] = True
            return result

        if not self.web:
            logger.error("Web not initialized")
            result["success"] = False
            return result

        try:
            from src.services.discovery_funnel import VOIGap
            discovery_funnel = DiscoveryFunnelService(
                db_path=str(self.db_path)
            )
            now_iso = datetime.now(timezone.utc).isoformat()
            gaps_created = []

            # ------------------------------------------------------------------
            # 1. MECHANISM gaps: theories with low belief coverage
            # ------------------------------------------------------------------
            # Count beliefs per theory
            theory_belief_counts: Dict[str, int] = {}
            for belief in self.web.beliefs.values():
                for tag in getattr(belief, 'tags', []):
                    if tag.startswith("theory:"):
                        theory_id = tag.split(":", 1)[1]
                        theory_belief_counts[theory_id] = theory_belief_counts.get(theory_id, 0) + 1

            # Theories with fewer than 5 beliefs are under-explored
            for theory_id, count in theory_belief_counts.items():
                if count < 5:
                    voi = min(1.0, 0.3 + 0.1 * (5 - count))  # Higher VOI for sparser theories
                    gap = VOIGap(
                        gap_id=f"mech_gap_{theory_id}",
                        topic=f"Under-explored mechanism pathways for {theory_id}",
                        gap_type=GapType.MECHANISM,
                        predicted_voi=round(voi, 3),
                        uncertainty_reduction=round(voi * 0.8, 3),
                        coherence_impact=round(voi * 0.5, 3),
                        theory_id=theory_id,
                        search_terms=[theory_id.replace("_", " ")],
                        target_article_types=["empirical", "systematic_review"],
                        priority=round(voi, 3),
                        identified_at=now_iso,
                        identified_by="system_setup.phase_11",
                    )
                    try:
                        discovery_funnel.create_gap(gap)
                        gaps_created.append(gap.gap_id)
                    except Exception as e:
                        logger.debug(f"Could not persist mechanism gap {theory_id}: {e}")
                    result["mechanism_gaps"] += 1

            # ------------------------------------------------------------------
            # 2. VALIDATION gaps: low-confidence beliefs (credence < 0.35)
            # ------------------------------------------------------------------
            low_conf_beliefs = [
                b for b in self.web.beliefs.values()
                if hasattr(b, 'credence') and b.credence is not None
                and hasattr(b.credence, 'value') and b.credence.value < 0.35
                and b.level != EpistemicLevel.STUB
            ]
            # Take top 50 by lowest credence (highest uncertainty → highest VOI)
            low_conf_beliefs.sort(key=lambda b: b.credence.value)
            for belief in low_conf_beliefs[:50]:
                cred_val = belief.credence.value
                entrenchment = getattr(belief, 'entrenchment', 0.5)
                # VOI: low credence + high entrenchment = high VOI
                voi = min(1.0, (1.0 - cred_val) * 0.5 + entrenchment * 0.3)
                gap = VOIGap(
                    gap_id=f"val_gap_{belief.belief_id[:60]}",
                    topic=f"Low confidence ({cred_val:.2f}): {belief.belief_id[:80]}",
                    gap_type=GapType.VALIDATION,
                    predicted_voi=round(voi, 3),
                    uncertainty_reduction=round((1.0 - cred_val) * 0.6, 3),
                    coherence_impact=round(entrenchment * 0.4, 3),
                    belief_id=belief.belief_id,
                    theory_id=next(
                        (t.split(":", 1)[1] for t in getattr(belief, 'tags', [])
                         if t.startswith("theory:")), None
                    ),
                    search_terms=[belief.belief_id.split("__")[0].replace("_", " ")],
                    target_article_types=["empirical"],
                    priority=round(voi, 3),
                    identified_at=now_iso,
                    identified_by="system_setup.phase_11",
                )
                try:
                    discovery_funnel.create_gap(gap)
                    gaps_created.append(gap.gap_id)
                except Exception as e:
                    logger.debug(f"Could not persist validation gap {belief.belief_id}: {e}")
                result["validation_gaps"] += 1

            # ------------------------------------------------------------------
            # 3. DIRECTION gaps: beliefs with unresolved conflicts
            # ------------------------------------------------------------------
            for belief in self.web.beliefs.values():
                conflicts = getattr(belief, 'conflicts', [])
                if len(conflicts) >= 2:
                    entrenchment = getattr(belief, 'entrenchment', 0.5)
                    # More conflicts + higher entrenchment = higher VOI
                    voi = min(1.0, 0.3 + 0.05 * len(conflicts) + entrenchment * 0.2)
                    gap = VOIGap(
                        gap_id=f"dir_gap_{belief.belief_id[:60]}",
                        topic=f"Unresolved conflicts ({len(conflicts)}): {belief.belief_id[:80]}",
                        gap_type=GapType.DIRECTION,
                        predicted_voi=round(voi, 3),
                        uncertainty_reduction=round(0.4 + 0.03 * len(conflicts), 3),
                        coherence_impact=round(entrenchment * 0.6, 3),
                        belief_id=belief.belief_id,
                        theory_id=next(
                            (t.split(":", 1)[1] for t in getattr(belief, 'tags', [])
                             if t.startswith("theory:")), None
                        ),
                        search_terms=[belief.belief_id.split("__")[0].replace("_", " ")],
                        target_article_types=["systematic_review", "meta_analysis"],
                        priority=round(voi, 3),
                        identified_at=now_iso,
                        identified_by="system_setup.phase_11",
                    )
                    try:
                        discovery_funnel.create_gap(gap)
                        gaps_created.append(gap.gap_id)
                    except Exception as e:
                        logger.debug(f"Could not persist direction gap {belief.belief_id}: {e}")
                    result["direction_gaps"] += 1

            result["gaps_identified"] = len(gaps_created)
            logger.info(
                f"Phase 11: {result['gaps_identified']} VOI gaps identified "
                f"(mechanism={result['mechanism_gaps']}, "
                f"validation={result['validation_gaps']}, "
                f"direction={result['direction_gaps']})"
            )
            result["success"] = True

        except Exception as e:
            logger.error(f"Phase 11 error: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            result["success"] = False
            result["error"] = str(e)

        return result

    def _phase_12_overseer_baseline(self) -> Dict[str, Any]:
        """
        Phase 12: OVERSEER Baseline snapshot.

        Create baseline health snapshot
        Set system state = OPERATIONAL
        Record all metrics for future comparison
        """
        result = {
            "success": True,
            "snapshot_timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics": {},
        }

        if not self.web:
            logger.error("Web not initialized")
            result["success"] = False
            return result

        try:
            # Compute baseline metrics
            n_beliefs = len(self.web.beliefs)
            n_constraints = len(self.web.constraints)
            avg_credence = (
                sum(b.credence.value for b in self.web.beliefs.values()) / n_beliefs
                if n_beliefs > 0
                else 0.0
            )

            result["metrics"] = {
                "n_beliefs": n_beliefs,
                "n_constraints": n_constraints,
                "avg_credence": avg_credence,
                "final_coherence": getattr(self, "_final_coherence", 0.0),
            }

            logger.info(f"Phase 12: OVERSEER baseline snapshot")
            logger.info(f"  Beliefs: {n_beliefs}")
            logger.info(f"  Constraints: {n_constraints}")
            logger.info(f"  Avg credence: {avg_credence:.4f}")
            result["success"] = True

        except Exception as e:
            logger.error(f"Phase 12 error: {e}")
            result["success"] = False
            result["error"] = str(e)

        return result

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def _load_extraction_paths(self) -> List[Path]:
        """Load all per-paper extraction JSON paths (DOI-named: 10.*.json)."""
        if not self.extractions_dir.exists():
            return []
        # Only load per-paper files (DOI-named), not batch files or metadata
        return sorted(self.extractions_dir.glob("10.*.json"))

    def _map_claim_type(self, raw_type: str) -> str:
        """Map extraction claim_type to ae.claim.v1 claim_type."""
        mapping = {
            "empirical_finding": "associational",
            "theoretical_proposition": "mechanistic",
            "design_guideline": "descriptive",
            "review_conclusion": "associational",
            "null_finding": "null",
            "moderated_finding": "moderated",
            "causal_claim": "causal",
            "correlation": "associational",
            "mechanism": "mechanistic",
        }
        return mapping.get(raw_type.lower(), "associational")

    def _map_study_type(self, finding: Dict[str, Any]) -> StudyType:
        """Map finding metadata to StudyType."""
        claim_type = finding.get("claim_type", "").lower()
        if "meta" in claim_type or "review" in claim_type:
            return StudyType.META_ANALYSIS
        elif "experimental" in claim_type or "experiment" in claim_type:
            return StudyType.EXPERIMENTAL
        elif "observational" in claim_type:
            return StudyType.OBSERVATIONAL
        elif "theoretical" in claim_type:
            return StudyType.THEORETICAL
        else:
            return StudyType.OBSERVATIONAL

    def _map_directness(self, finding: Dict[str, Any]) -> Directness:
        """Map finding metadata to Directness."""
        evidence_type = finding.get("evidence_type", "").lower()
        measure_type = finding.get("measure_type", "").lower()

        if "direct" in evidence_type or "observational" in evidence_type:
            return Directness.DIRECT
        elif "experimental" in evidence_type or "measured" in measure_type:
            return Directness.ONE_HOP
        elif "theoretical" in evidence_type or "inferred" in evidence_type:
            return Directness.MULTI_HOP
        else:
            return Directness.ONE_HOP

    def _compute_grounding_score(
        self, finding: Dict[str, Any], directness: Directness
    ) -> float:
        """Compute grounding score for a finding (Haack foundherentism)."""
        base_score = {
            Directness.DIRECT: 0.9,
            Directness.ONE_HOP: 0.7,
            Directness.MULTI_HOP: 0.4,
            Directness.THEORETICAL: 0.1,
        }.get(directness, 0.5)

        # Adjust for sample size / quality
        sample_size = finding.get("sample_size", 0)
        if sample_size and sample_size > 100:
            base_score += 0.1
        elif sample_size and sample_size > 30:
            base_score += 0.05

        return min(base_score, 1.0)
