"""
Source Data Completeness Auditor — Proactive Gap Detection
============================================================

When a tab generator receives thin or empty data from upstream layers,
this auditor diagnoses WHY and traces the gap to the responsible upstream
service. Instead of silently producing [DRAFT] placeholders, generators
call the auditor to generate actionable diagnostic reports.

Architecture:
    Tab Generator → SourceDataCompletenessAuditor.audit(source_data)
        → for each missing layer:
            → identify the upstream service responsible
            → check if that service has been run for this entity
            → produce a DataGap with actionable remediation

Upstream service map (entity_type → expected data → responsible service):

    Layer           | source_data keys             | Upstream Service
    ================|==============================|=================
    Extraction      | mechanism_chain, theory_links| extraction_to_web.py
    Provenance      | provenance.anchors, .sq      | provenance.py
    Argumentation   | argumentation.vulnerabilities| argumentation_graph.py
    Interpretation  | interpretation.closure_results| interpretive_intelligence.py
    Annotation      | annotations[]                | annotation_service.py

Success Conditions:
    SC-SDA-1: Every entity gets an audit (no silent thin data)
    SC-SDA-2: Each gap identifies the upstream service by name
    SC-SDA-3: Each gap includes a remediation action (function to call)
    SC-SDA-4: Audit results are logged and can be aggregated by overseer
    SC-SDA-5: No false positives: optional layers are not flagged as gaps
    SC-SDA-6: Severity grading: CRITICAL (required, empty), WARNING
              (expected, empty), INFO (optional, empty)

Author: AG (Antigravity)
Date: 2026-03-04

⚠️ CW REVIEW (MT-20): CW must verify upstream service function names
and source_data key contracts match what agents actually populate.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, FrozenSet, List, Optional

logger = logging.getLogger(__name__)


# ===========================================================================
# Gap Severity
# ===========================================================================

class GapSeverity(str, Enum):
    """How serious the data gap is."""
    CRITICAL = "critical"   # Required layer is empty — card cannot be correct
    WARNING = "warning"     # Expected layer is empty — card is incomplete
    INFO = "info"           # Optional layer is empty — nice to have


# ===========================================================================
# Data Gap
# ===========================================================================

@dataclass
class DataGap:
    """A diagnosed gap in source_data for a specific entity.

    Each gap traces back to the upstream service that should have
    populated the data, and includes an actionable remediation.
    """
    layer_name: str           # e.g., "provenance", "argumentation"
    severity: GapSeverity
    expected_keys: List[str]  # Keys that should be in source_data
    present_keys: List[str]   # Keys that ARE in source_data (may be empty)
    missing_keys: List[str]   # Keys that are absent or empty

    # Upstream tracing
    upstream_service: str     # Module path, e.g., "src.models.provenance"
    upstream_function: str    # Function to call, e.g., "compute_justification_status"
    upstream_class: str       # Class name, e.g., "ProvenanceTracer"

    # Remediation
    remediation: str          # Human-readable action, e.g., "Run ProvenanceTracer..."
    remediation_code: str     # Python snippet to fix the gap

    def to_dict(self) -> Dict[str, Any]:
        return {
            "layer": self.layer_name,
            "severity": self.severity.value,
            "missing_keys": self.missing_keys,
            "present_keys": self.present_keys,
            "upstream_service": self.upstream_service,
            "upstream_function": self.upstream_function,
            "remediation": self.remediation,
        }


@dataclass
class AuditResult:
    """Complete audit result for a single entity's source_data."""
    entity_id: str
    card_type: str
    total_layers_checked: int
    total_gaps: int
    critical_gaps: int
    warning_gaps: int
    info_gaps: int
    gaps: List[DataGap]
    coverage_score: float     # 0.0 = all empty, 1.0 = fully populated
    is_generation_ready: bool  # True if no CRITICAL gaps

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "card_type": self.card_type,
            "coverage_score": round(self.coverage_score, 3),
            "is_generation_ready": self.is_generation_ready,
            "total_gaps": self.total_gaps,
            "critical": self.critical_gaps,
            "warning": self.warning_gaps,
            "info": self.info_gaps,
            "gaps": [g.to_dict() for g in self.gaps],
        }

    @property
    def summary(self) -> str:
        """One-line summary for logging."""
        if self.total_gaps == 0:
            return f"{self.entity_id}: COMPLETE (coverage={self.coverage_score:.0%})"
        return (
            f"{self.entity_id}: {self.total_gaps} gaps "
            f"({self.critical_gaps}C/{self.warning_gaps}W/{self.info_gaps}I) "
            f"coverage={self.coverage_score:.0%}"
        )


# ===========================================================================
# Layer Definitions — maps each layer to expected keys and upstream service
# ===========================================================================

@dataclass(frozen=True)
class LayerExpectation:
    """What we expect a specific layer to contribute to source_data."""
    layer_name: str
    expected_keys: FrozenSet[str]  # Keys this layer should populate
    required: bool              # True = CRITICAL if missing, False = WARNING
    upstream_module: str        # Python module path
    upstream_class: str         # Class to instantiate
    upstream_function: str      # Method to call
    remediation_template: str   # How to fix, with {entity_id} placeholder


# The canonical layer expectations
LAYER_EXPECTATIONS: List[LayerExpectation] = [
    # ── Core extraction (always required) ──
    LayerExpectation(
        layer_name="extraction",
        expected_keys=frozenset({
            "mechanism_chain", "theory_links", "n_findings", "n_papers",
        }),
        required=True,
        upstream_module="src.services.extraction_to_web",
        upstream_class="ExtractionToWeb",
        upstream_function="extract_and_integrate",
        remediation_template=(
            "Run extraction pipeline for {entity_id}: "
            "ExtractionToWeb().extract_and_integrate('{entity_id}')"
        ),
    ),

    # ── Provenance (required for epistemic quality) ──
    LayerExpectation(
        layer_name="provenance",
        expected_keys=frozenset({
            "provenance",   # Dict with anchors, source_quality, justification_status
        }),
        required=True,
        upstream_module="src.models.provenance",
        upstream_class="ProvenanceTracer (via web_persistence)",
        upstream_function="compute_justification_status",
        remediation_template=(
            "Provenance data missing for {entity_id}. The provenance tracer "
            "should populate anchors, source_quality, and justification_status "
            "via web_persistence.get_belief_provenance('{entity_id}'). "
            "This requires beliefs to exist in the web_persistence DB."
        ),
    ),

    # ── Argumentation (expected for mechanism + debate tabs) ──
    LayerExpectation(
        layer_name="argumentation",
        expected_keys=frozenset({
            "argumentation",  # Dict with vulnerabilities, critique_summary
        }),
        required=False,
        upstream_module="src.services.argumentation_graph",
        upstream_class="ArgumentationGraph",
        upstream_function="build_from_extractions + get_debate_clusters",
        remediation_template=(
            "Argumentation data missing for {entity_id}. Build the "
            "argumentation graph: "
            "ag = ArgumentationGraph(); "
            "ag.build_from_extractions(Path('data/extractions')); "
            "clusters = ag.get_debate_clusters()"
        ),
    ),

    # ── Interpretation (expected for mechanism + design tabs) ──
    LayerExpectation(
        layer_name="interpretation",
        expected_keys=frozenset({
            "interpretation",  # Dict with closure_results (R₁-R₄)
        }),
        required=False,
        upstream_module="src.services.interpretive_intelligence",
        upstream_class="ExplanationEngine",
        upstream_function="explain_belief (evidence + practical patterns)",
        remediation_template=(
            "Interpretation data missing for {entity_id}. Run the "
            "explanation engine: "
            "engine = ExplanationEngine(web); "
            "result = engine.explain_belief('{entity_id}', "
            "ExplanationPattern.EVIDENCE)"
        ),
    ),

    # ── Annotations (optional enrichment) ──
    LayerExpectation(
        layer_name="annotations",
        expected_keys=frozenset({
            "annotations",  # List of annotation dicts
        }),
        required=False,
        upstream_module="src.services.annotation_service",
        upstream_class="AnnotationService",
        upstream_function="get_active_annotations(target_type, target_id)",
        remediation_template=(
            "No annotations found for {entity_id}. Query the annotation "
            "service: "
            "svc = AnnotationService(); "
            "anns = svc.get_active_annotations('belief', '{entity_id}')"
        ),
    ),
]


# ===========================================================================
# The Auditor
# ===========================================================================

class SourceDataCompletenessAuditor:
    """Audits source_data for completeness and traces gaps to upstream services.

    Usage:
        auditor = SourceDataCompletenessAuditor()
        result = auditor.audit("LIGHT-01", "t2-mechanism", source_data)
        if not result.is_generation_ready:
            for gap in result.gaps:
                logger.warning(f"GAP: {gap.remediation}")

    The auditor is designed to be called by tab generators BEFORE they
    produce content. If critical data is missing, the generator can include
    the diagnostic in its output instead of a silent [DRAFT] placeholder.
    """

    def __init__(
        self,
        layer_expectations: Optional[List[LayerExpectation]] = None,
    ):
        self._expectations = layer_expectations or LAYER_EXPECTATIONS

    def audit(
        self,
        entity_id: str,
        card_type: str,
        source_data: Dict[str, Any],
    ) -> AuditResult:
        """Audit source_data for completeness.

        Args:
            entity_id: The entity being audited (e.g., "LIGHT-01")
            card_type: The card type (e.g., "t2-mechanism")
            source_data: The data dict being passed to tab generators

        Returns:
            AuditResult with gaps and coverage score
        """
        gaps: List[DataGap] = []

        for expectation in self._expectations:
            layer_gaps = self._check_layer(
                entity_id, source_data, expectation
            )
            gaps.extend(layer_gaps)

        # Coverage score
        total_expected = sum(
            len(e.expected_keys) for e in self._expectations
        )
        total_present = total_expected - sum(
            len(g.missing_keys) for g in gaps
        )
        coverage = total_present / total_expected if total_expected > 0 else 0.0

        critical = sum(1 for g in gaps if g.severity == GapSeverity.CRITICAL)
        warning = sum(1 for g in gaps if g.severity == GapSeverity.WARNING)
        info = sum(1 for g in gaps if g.severity == GapSeverity.INFO)

        result = AuditResult(
            entity_id=entity_id,
            card_type=card_type,
            total_layers_checked=len(self._expectations),
            total_gaps=len(gaps),
            critical_gaps=critical,
            warning_gaps=warning,
            info_gaps=info,
            gaps=gaps,
            coverage_score=max(0.0, min(1.0, coverage)),
            is_generation_ready=(critical == 0),
        )

        # Log the result
        if critical > 0:
            logger.warning(f"SOURCE DATA AUDIT: {result.summary}")
        elif warning > 0:
            logger.info(f"SOURCE DATA AUDIT: {result.summary}")
        else:
            logger.debug(f"SOURCE DATA AUDIT: {result.summary}")

        return result

    def _check_layer(
        self,
        entity_id: str,
        source_data: Dict[str, Any],
        expectation: LayerExpectation,
    ) -> List[DataGap]:
        """Check a single layer's data presence."""
        gaps = []
        present_keys = []
        missing_keys = []

        for key in expectation.expected_keys:
            value = source_data.get(key)
            if self._is_populated(value):
                present_keys.append(key)
            else:
                missing_keys.append(key)

        if missing_keys:
            severity = (
                GapSeverity.CRITICAL if expectation.required
                else GapSeverity.WARNING
            )
            # Downgrade to INFO if the layer is optional and fully empty
            if not expectation.required and len(missing_keys) == len(expectation.expected_keys):
                severity = GapSeverity.INFO

            remediation = expectation.remediation_template.format(
                entity_id=entity_id
            )

            gaps.append(DataGap(
                layer_name=expectation.layer_name,
                severity=severity,
                expected_keys=list(expectation.expected_keys),
                present_keys=present_keys,
                missing_keys=missing_keys,
                upstream_service=expectation.upstream_module,
                upstream_function=expectation.upstream_function,
                upstream_class=expectation.upstream_class,
                remediation=remediation,
                remediation_code=remediation,  # Same for now
            ))

        return gaps

    @staticmethod
    def _is_populated(value: Any) -> bool:
        """Check if a value is meaningfully populated (not empty/None)."""
        if value is None:
            return False
        if isinstance(value, (str, list, dict)) and len(value) == 0:
            return False
        if isinstance(value, dict):
            # A dict with all-None values is not populated
            return any(v is not None for v in value.values())
        return True

    def format_diagnostic(self, result: AuditResult) -> str:
        """Format audit result as a human-readable diagnostic for inclusion in card prose.

        Instead of [DRAFT], cards include this diagnostic so users/CW can
        see exactly what's missing and how to fix it.
        """
        if result.total_gaps == 0:
            return ""

        lines = [
            f"## ⚠️ Data Completeness: {result.coverage_score:.0%}",
            "",
            f"This card has {result.total_gaps} data gap(s) affecting "
            f"content quality. The following upstream processes have not "
            f"populated their expected data:",
            "",
        ]

        for gap in result.gaps:
            icon = {"critical": "🔴", "warning": "🟡", "info": "🔵"}[gap.severity.value]
            lines.append(
                f"- {icon} **{gap.layer_name}** ({gap.severity.value}): "
                f"missing `{', '.join(gap.missing_keys)}`"
            )
            lines.append(f"  - Upstream: `{gap.upstream_service}.{gap.upstream_class}`")
            lines.append(f"  - Fix: {gap.remediation}")
            lines.append("")

        return "\n".join(lines)


# ===========================================================================
# Convenience: singleton auditor
# ===========================================================================

_AUDITOR: Optional[SourceDataCompletenessAuditor] = None


def get_auditor() -> SourceDataCompletenessAuditor:
    """Get or create the singleton auditor."""
    global _AUDITOR
    if _AUDITOR is None:
        _AUDITOR = SourceDataCompletenessAuditor()
    return _AUDITOR


def audit_source_data(
    entity_id: str,
    card_type: str,
    source_data: Dict[str, Any],
) -> AuditResult:
    """Convenience function for auditing source data.

    Tab generators call this as:
        from src.qa.source_data_auditor import audit_source_data
        result = audit_source_data(entity_id, card_type, data)
        if not result.is_generation_ready:
            prose += auditor.format_diagnostic(result)
    """
    return get_auditor().audit(entity_id, card_type, source_data)
