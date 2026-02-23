"""
Structural Bias Detection (Sprint T3-3.3).

Checks whether supporting evidence for a claim comes from diverse,
independent sources. Flags claims where evidence is clustered by:
- Lab/author (lack of independence)
- Theoretical paradigm (paradigm lock-in)
- Measurement method (method bias)

This addresses the "same lab, same method, same paradigm" problem in CNFA
where replication may be nominal rather than genuine.

References:
- Longino, H. (1990). Science as Social Knowledge
- Ioannidis, J.P.A. (2005). Why Most Published Research Findings Are False
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Any
from enum import Enum
from collections import defaultdict


class BiasFlag(str, Enum):
    """Types of structural bias flags."""
    LOW_INDEPENDENCE = "low_independence"      # Same lab cluster
    LOW_PARADIGM_DIVERSITY = "low_paradigm_diversity"  # Same theoretical tradition
    LOW_METHOD_DIVERSITY = "low_method_diversity"      # Same measurement approach
    SINGLE_SOURCE = "single_source"            # Only one study


@dataclass
class BiasDetectionResult:
    """Result of structural bias detection for a single node."""
    node_id: str
    evidence_independence: float   # [0, 1] — 1 = fully independent labs
    paradigm_diversity: float      # [0, 1] — 1 = diverse theoretical traditions
    method_diversity: float        # [0, 1] — 1 = diverse measurement methods
    flags: List[BiasFlag]
    details: str
    evidence_count: int = 0
    lab_clusters: int = 0
    paradigm_count: int = 0
    method_count: int = 0

    def to_dict(self) -> Dict:
        return {
            "node_id": self.node_id,
            "evidence_independence": self.evidence_independence,
            "paradigm_diversity": self.paradigm_diversity,
            "method_diversity": self.method_diversity,
            "flags": [f.value for f in self.flags],
            "details": self.details,
            "evidence_count": self.evidence_count,
            "summary": {
                "lab_clusters": self.lab_clusters,
                "paradigm_count": self.paradigm_count,
                "method_count": self.method_count,
            },
        }

    @property
    def has_flags(self) -> bool:
        return len(self.flags) > 0

    @property
    def overall_diversity_score(self) -> float:
        """Composite diversity score (average of all dimensions)."""
        return (self.evidence_independence + self.paradigm_diversity + self.method_diversity) / 3.0


def run_structural_bias_detection(
    web: Any,
    node_id: str,
    independence_threshold: float = 0.3,
    paradigm_threshold: float = 0.2,
    method_threshold: float = 0.2,
    evidence_metadata: Optional[List[Dict]] = None,
) -> BiasDetectionResult:
    """
    Check whether supporting evidence comes from diverse, independent sources.

    Analyzes three dimensions of evidence diversity:
    1. Lab independence: Are studies from different research groups?
    2. Paradigm diversity: Are studies from different theoretical traditions?
    3. Method diversity: Are different measurement approaches used?

    Args:
        web: The web-of-belief graph. Can be None if evidence_metadata provided.
        node_id: ID of the claim node to analyze.
        independence_threshold: Minimum independence score to avoid flag (0.3)
        paradigm_threshold: Minimum paradigm diversity to avoid flag (0.2)
        method_threshold: Minimum method diversity to avoid flag (0.2)
        evidence_metadata: Optional list of evidence dictionaries with:
            - author_affiliations: List[str]
            - paradigm: str (e.g., "ART", "SRT", "Biophilia")
            - method: str (e.g., "EEG", "fMRI", "self_report", "behavioral")
            - lab_id: Optional[str]

    Returns:
        BiasDetectionResult with diversity scores and flags.

    Example:
        >>> evidence = [
        ...     {"lab_id": "lab_A", "paradigm": "ART", "method": "self_report"},
        ...     {"lab_id": "lab_A", "paradigm": "ART", "method": "self_report"},
        ...     {"lab_id": "lab_A", "paradigm": "ART", "method": "cortisol"},
        ... ]
        >>> result = run_structural_bias_detection(None, "claim_1",
        ...                                         evidence_metadata=evidence)
        >>> # Should flag low_independence (all same lab)
        >>> # Should flag low_paradigm_diversity (all same paradigm)
    """
    # Get evidence metadata
    if evidence_metadata is None:
        evidence_metadata = _extract_evidence_metadata(web, node_id)

    if not evidence_metadata:
        return BiasDetectionResult(
            node_id=node_id,
            evidence_independence=0.0,
            paradigm_diversity=0.0,
            method_diversity=0.0,
            flags=[BiasFlag.SINGLE_SOURCE],
            details="No supporting evidence found for this claim.",
            evidence_count=0,
        )

    evidence_count = len(evidence_metadata)

    if evidence_count == 1:
        return BiasDetectionResult(
            node_id=node_id,
            evidence_independence=0.0,
            paradigm_diversity=0.0,
            method_diversity=0.0,
            flags=[BiasFlag.SINGLE_SOURCE],
            details="Only one study supports this claim. No diversity possible.",
            evidence_count=1,
            lab_clusters=1,
            paradigm_count=1,
            method_count=1,
        )

    # Compute independence score
    independence, lab_clusters = _compute_independence(evidence_metadata)

    # Compute paradigm diversity
    paradigm_diversity, paradigm_count = _compute_paradigm_diversity(evidence_metadata)

    # Compute method diversity
    method_diversity, method_count = _compute_method_diversity(evidence_metadata)

    # Determine flags
    flags: List[BiasFlag] = []
    details_parts: List[str] = []

    if independence < independence_threshold:
        flags.append(BiasFlag.LOW_INDEPENDENCE)
        details_parts.append(f"Low lab independence ({independence:.2f} < {independence_threshold})")

    if paradigm_diversity < paradigm_threshold:
        flags.append(BiasFlag.LOW_PARADIGM_DIVERSITY)
        details_parts.append(f"Low paradigm diversity ({paradigm_diversity:.2f} < {paradigm_threshold})")

    if method_diversity < method_threshold:
        flags.append(BiasFlag.LOW_METHOD_DIVERSITY)
        details_parts.append(f"Low method diversity ({method_diversity:.2f} < {method_threshold})")

    details = "; ".join(details_parts) if details_parts else "Evidence shows adequate diversity."

    return BiasDetectionResult(
        node_id=node_id,
        evidence_independence=independence,
        paradigm_diversity=paradigm_diversity,
        method_diversity=method_diversity,
        flags=flags,
        details=details,
        evidence_count=evidence_count,
        lab_clusters=lab_clusters,
        paradigm_count=paradigm_count,
        method_count=method_count,
    )


def _compute_independence(evidence: List[Dict]) -> tuple:
    """
    Compute evidence independence based on lab/author clustering.

    Uses a simple heuristic: independence = 1 - (largest_cluster / total)

    Returns:
        (independence_score, num_clusters)
    """
    # Extract lab identifiers
    lab_ids: List[str] = []
    for e in evidence:
        lab_id = e.get('lab_id')
        if not lab_id:
            # Try to derive from affiliations
            affiliations = e.get('author_affiliations', [])
            if affiliations:
                lab_id = affiliations[0]  # Use first affiliation as proxy
            else:
                lab_id = f"unknown_{len(lab_ids)}"
        lab_ids.append(lab_id)

    if not lab_ids:
        return 0.0, 0

    # Count cluster sizes
    cluster_counts = defaultdict(int)
    for lab_id in lab_ids:
        cluster_counts[lab_id] += 1

    num_clusters = len(cluster_counts)
    largest_cluster = max(cluster_counts.values())
    total = len(lab_ids)

    # Independence: 1 when all from different labs, 0 when all from same lab
    independence = 1.0 - (largest_cluster / total)

    return independence, num_clusters


def _compute_paradigm_diversity(evidence: List[Dict]) -> tuple:
    """
    Compute paradigm diversity.

    Returns:
        (diversity_score, num_paradigms)
    """
    paradigms: Set[str] = set()
    for e in evidence:
        paradigm = e.get('paradigm', 'unknown')
        paradigms.add(paradigm.lower())

    num_paradigms = len(paradigms)
    total = len(evidence)

    # Diversity: approaches 1 as paradigms approach evidence count
    # Cap at 5 paradigms for normalization (more than 5 is rare)
    diversity = min(1.0, num_paradigms / min(total, 5))

    return diversity, num_paradigms


def _compute_method_diversity(evidence: List[Dict]) -> tuple:
    """
    Compute measurement method diversity.

    Returns:
        (diversity_score, num_methods)
    """
    methods: Set[str] = set()
    for e in evidence:
        method = e.get('method', 'unknown')
        methods.add(method.lower())

    num_methods = len(methods)
    total = len(evidence)

    # Diversity: approaches 1 as methods approach evidence count
    # Cap at 5 methods for normalization
    diversity = min(1.0, num_methods / min(total, 5))

    return diversity, num_methods


def _extract_evidence_metadata(web: Any, node_id: str) -> List[Dict]:
    """
    Extract evidence metadata for a node from the web object.
    """
    evidence: List[Dict] = []

    if web is None:
        return evidence

    # Try to get supporting beliefs/studies
    if hasattr(web, 'get_supporting_evidence'):
        try:
            return web.get_supporting_evidence(node_id)
        except Exception:
            pass

    # Try to extract from constraints
    if hasattr(web, 'constraints'):
        try:
            for constraint in web.constraints:
                target = getattr(constraint, 'target_belief_id', None)
                if target == node_id:
                    source_id = getattr(constraint, 'source_belief_id', None)
                    if source_id and hasattr(web, 'get_belief'):
                        source = web.get_belief(source_id)
                        if source:
                            evidence.append({
                                'lab_id': getattr(source, 'lab_id', None),
                                'paradigm': getattr(source, 'paradigm', getattr(source, 'theory_id', 'unknown')),
                                'method': getattr(source, 'method', 'unknown'),
                                'author_affiliations': getattr(source, 'author_affiliations', []),
                            })
        except Exception:
            pass

    return evidence


def run_bulk_bias_detection(
    web: Any,
    node_ids: Optional[List[str]] = None,
    independence_threshold: float = 0.3,
    paradigm_threshold: float = 0.2,
    method_threshold: float = 0.2,
) -> Dict[str, BiasDetectionResult]:
    """
    Run bias detection on multiple nodes.

    Args:
        web: The web-of-belief graph.
        node_ids: List of node IDs to check. If None, checks all claim nodes.
        independence_threshold: Threshold for independence flag.
        paradigm_threshold: Threshold for paradigm diversity flag.
        method_threshold: Threshold for method diversity flag.

    Returns:
        Dict mapping node_id to BiasDetectionResult.
    """
    results: Dict[str, BiasDetectionResult] = {}

    if node_ids is None and web is not None:
        # Try to get all claim node IDs
        if hasattr(web, 'get_claim_ids'):
            node_ids = web.get_claim_ids()
        elif hasattr(web, 'beliefs'):
            node_ids = [getattr(b, 'belief_id', getattr(b, 'id', None))
                       for b in web.beliefs]
            node_ids = [n for n in node_ids if n]

    if not node_ids:
        return results

    for node_id in node_ids:
        results[node_id] = run_structural_bias_detection(
            web, node_id,
            independence_threshold=independence_threshold,
            paradigm_threshold=paradigm_threshold,
            method_threshold=method_threshold,
        )

    return results
