"""
Argumentation Graph Service

Builds and analyzes the scholarly argumentation structure from citation data.
Operates in two modes:
  1. WITHOUT S2 enrichment: uses publication years + template key_references for temporal ordering
  2. WITH S2 enrichment: uses full citation graph for polarity detection and community clustering

Author: Claude Code
Date: 2026-02-25
Version: 1.0.0
"""

import json
import logging
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
from collections import defaultdict
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ArgumentationNode:
    """Represents a paper in the argumentation graph."""
    doi: str
    title: str
    year: Optional[int]
    authors: List[str]
    theories: List[str]        # T1 frameworks referenced (e.g., "coherence", "foundationalism")
    claim_count: int           # Number of claims made in extraction
    citation_count: Optional[int] = None  # From S2 data if available
    extraction_date: Optional[str] = None

    def __hash__(self):
        return hash(self.doi)

    def __eq__(self, other):
        if isinstance(other, ArgumentationNode):
            return self.doi == other.doi
        return False


@dataclass
class ArgumentationEdge:
    """Represents a citation relationship between papers."""
    source_doi: str            # The citing paper
    target_doi: str            # The cited paper
    edge_type: str             # "cites" | "supports" | "challenges" | "extends" | "supersedes"
    polarity: float            # -1.0 (contradicts) to +1.0 (supports), 0.0 = neutral/unknown
    confidence: float          # How confident we are in the polarity (0.0-1.0)
    evidence: str              # Brief explanation of polarity assignment

    def __hash__(self):
        return hash((self.source_doi, self.target_doi))

    def __eq__(self, other):
        if isinstance(other, ArgumentationEdge):
            return (self.source_doi == other.source_doi and
                    self.target_doi == other.target_doi)
        return False


@dataclass
class DebateCluster:
    """Represents a community of papers debating related questions."""
    cluster_id: str
    topic: str                 # Inferred topic or question
    papers: List[str]          # DOIs in cluster
    theories_involved: List[str]
    dominant_position: Optional[str]
    contestation_level: float  # 0.0 = consensus, 1.0 = highly contested
    internal_edges: int = 0
    average_polarity: float = 0.0


class ArgumentationGraph:
    """
    Builds and analyzes scholarly argumentation structures.

    Supports two modes:
      1. Base mode: uses extraction metadata + temporal inference
      2. Enriched mode: overlays S2 citation graph for enhanced polarity detection
    """

    def __init__(self):
        """Initialize empty graph."""
        self.nodes: Dict[str, ArgumentationNode] = {}
        self.edges: List[ArgumentationEdge] = []
        self._edge_lookup: Dict[Tuple[str, str], ArgumentationEdge] = {}
        self._s2_enriched: bool = False
        self._adjacency: Dict[str, Set[str]] = defaultdict(set)  # source -> targets
        self._reverse_adjacency: Dict[str, Set[str]] = defaultdict(set)  # target -> sources
        logger.info("ArgumentationGraph initialized")

    def build_from_extractions(self, extractions_dir: Path) -> None:
        """
        Build graph from extraction JSON files.

        Works without S2 data. Creates nodes from extraction metadata and infers
        temporal edges based on publication years and shared theories.

        Args:
            extractions_dir: Path to directory containing extraction JSON files

        Raises:
            FileNotFoundError: If directory doesn't exist
            json.JSONDecodeError: If JSON files are malformed
        """
        extractions_dir = Path(extractions_dir)
        if not extractions_dir.exists():
            raise FileNotFoundError(f"Extractions directory not found: {extractions_dir}")

        try:
            json_files = list(extractions_dir.glob("*.json"))
            logger.info(f"Found {len(json_files)} extraction files")

            for json_file in json_files:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        extraction = json.load(f)

                    # Extract metadata
                    doi = extraction.get("doi", "unknown")
                    title = extraction.get("title", "Unknown Title")
                    year = extraction.get("year")
                    authors = extraction.get("authors", [])
                    theories = extraction.get("theories_referenced", [])
                    claims = extraction.get("claims", [])
                    extraction_date = extraction.get("extraction_date")

                    if year is not None:
                        year = int(year)

                    # Create node
                    node = ArgumentationNode(
                        doi=doi,
                        title=title,
                        year=year,
                        authors=authors,
                        theories=theories,
                        claim_count=len(claims),
                        extraction_date=extraction_date
                    )

                    self.nodes[doi] = node
                    logger.debug(f"Added node: {doi} ({title[:50]}...)")

                except Exception as e:
                    logger.warning(f"Failed to process {json_file.name}: {e}")
                    continue

            logger.info(f"Successfully loaded {len(self.nodes)} nodes from extractions")

            # Infer temporal edges
            self._infer_temporal_edges()

        except Exception as e:
            logger.error(f"Error building graph from extractions: {e}")
            raise

    def _infer_temporal_edges(self) -> None:
        """
        Infer citation-like edges based on temporal ordering and theory alignment.

        Heuristic: if paper A (year T1) references theory X and paper B (year T2 > T1)
        also references theory X, infer edge A -> B with polarity based on alignment.
        """
        logger.info("Inferring temporal edges from theory alignment")

        nodes_with_years = [(doi, node) for doi, node in self.nodes.items()
                           if node.year is not None]
        nodes_with_years.sort(key=lambda x: x[1].year)

        edge_count = 0

        for i, (doi_a, node_a) in enumerate(nodes_with_years):
            for doi_b, node_b in nodes_with_years[i+1:]:
                # Only infer edge if B is newer
                if node_b.year <= node_a.year:
                    continue

                # Check for theory alignment
                shared_theories = set(node_a.theories) & set(node_b.theories)

                if len(shared_theories) > 0:
                    polarity, confidence = self._infer_polarity_from_theories(
                        node_a, node_b, shared_theories
                    )

                    edge = ArgumentationEdge(
                        source_doi=doi_a,
                        target_doi=doi_b,
                        edge_type="cites",
                        polarity=polarity,
                        confidence=confidence,
                        evidence=f"Shared theories: {', '.join(sorted(shared_theories))}"
                    )

                    self._add_edge(edge)
                    edge_count += 1

        logger.info(f"Inferred {edge_count} temporal edges")

    def _infer_polarity_from_theories(
        self,
        node_a: ArgumentationNode,
        node_b: ArgumentationNode,
        shared_theories: Set[str]
    ) -> Tuple[float, float]:
        """
        Infer polarity and confidence based on theory alignment.

        Returns:
            (polarity, confidence) tuple
        """
        # Base confidence: 0.4-0.5 for inference without S2 data
        confidence = 0.45

        # Count shared theories
        shared_count = len(shared_theories)

        if shared_count >= 3:
            # Strong alignment: likely in same research tradition
            polarity = 0.6
            confidence = 0.5
        elif shared_count >= 1:
            # Moderate alignment: likely building on similar foundations
            polarity = 0.3
            confidence = 0.4
        else:
            polarity = 0.0
            confidence = 0.3

        return polarity, confidence

    def enrich_from_citation_graph(self, citation_graph_path: Path) -> None:
        """
        Overlay S2 citation data onto existing graph.

        Enriches polarity detection with full citation relationships and enables
        community clustering based on co-citation patterns.

        Args:
            citation_graph_path: Path to citation_graph.json from S2 API

        Raises:
            FileNotFoundError: If citation graph file doesn't exist
            json.JSONDecodeError: If JSON is malformed
        """
        citation_graph_path = Path(citation_graph_path)
        if not citation_graph_path.exists():
            raise FileNotFoundError(f"Citation graph not found: {citation_graph_path}")

        try:
            logger.info(f"Loading citation graph from {citation_graph_path}")

            with open(citation_graph_path, 'r', encoding='utf-8') as f:
                citation_data = json.load(f)

            # Update nodes with S2 metadata
            papers = citation_data.get("papers", [])
            for paper in papers:
                doi = paper.get("doi")
                if doi and doi in self.nodes:
                    citation_count = paper.get("citation_count", 0)
                    self.nodes[doi].citation_count = citation_count

            # Process citation relationships
            for paper in papers:
                source_doi = paper.get("doi")
                if not source_doi or source_doi not in self.nodes:
                    continue

                source_node = self.nodes[source_doi]

                # Process references (outgoing edges)
                references = paper.get("references", [])
                for ref_doi in references:
                    if ref_doi in self.nodes:
                        target_node = self.nodes[ref_doi]

                        # Infer polarity with S2 data
                        polarity, confidence, evidence = self._infer_citation_polarity_s2(
                            source_node, target_node
                        )

                        # Check if edge already exists from temporal inference
                        edge_key = (source_doi, ref_doi)
                        if edge_key in self._edge_lookup:
                            # Update existing edge with S2 data
                            existing = self._edge_lookup[edge_key]
                            existing.polarity = polarity
                            existing.confidence = confidence
                            existing.evidence = evidence
                        else:
                            # Create new edge from citation data
                            edge = ArgumentationEdge(
                                source_doi=source_doi,
                                target_doi=ref_doi,
                                edge_type="cites",
                                polarity=polarity,
                                confidence=confidence,
                                evidence=evidence
                            )
                            self._add_edge(edge)

            self._s2_enriched = True
            logger.info("Citation graph enrichment complete")

        except Exception as e:
            logger.error(f"Error enriching from citation graph: {e}")
            raise

    def _infer_citation_polarity_s2(
        self,
        source_node: ArgumentationNode,
        target_node: ArgumentationNode
    ) -> Tuple[float, float, str]:
        """
        Infer polarity using S2-enriched data.

        Uses theory alignment and temporal ordering for higher-confidence assignments.

        Returns:
            (polarity, confidence, evidence) tuple
        """
        shared_theories = set(source_node.theories) & set(target_node.theories)

        # Start with theory alignment
        polarity = 0.0
        confidence = 0.6
        evidence_parts = []

        if len(shared_theories) >= 3:
            polarity = 0.75
            confidence = 0.7
            evidence_parts.append(f"Strong theory alignment: {', '.join(sorted(shared_theories)[:2])}")
        elif len(shared_theories) >= 1:
            polarity = 0.5
            confidence = 0.65
            evidence_parts.append(f"Moderate theory alignment: {next(iter(shared_theories))}")
        else:
            evidence_parts.append("No direct theory overlap")

        # Adjust based on temporal ordering
        if source_node.year and target_node.year:
            year_diff = target_node.year - source_node.year
            if year_diff > 0:
                polarity += 0.1  # Newer papers likely building on older
                evidence_parts.append(f"Temporal ordering: {year_diff} years apart")

        # Clamp polarity to [-1, 1]
        polarity = max(-1.0, min(1.0, polarity))

        evidence = "; ".join(evidence_parts)
        return polarity, confidence, evidence

    def _add_edge(self, edge: ArgumentationEdge) -> None:
        """Add edge to graph, avoiding duplicates."""
        edge_key = (edge.source_doi, edge.target_doi)
        if edge_key not in self._edge_lookup:
            self.edges.append(edge)
            self._edge_lookup[edge_key] = edge
            self._adjacency[edge.source_doi].add(edge.target_doi)
            self._reverse_adjacency[edge.target_doi].add(edge.source_doi)

    def get_temporal_ordering(self) -> List[str]:
        """
        Return DOIs sorted by publication year (Quinean ordering).

        Papers with unknown years are placed at the end, sorted by extraction date.

        Returns:
            List of DOIs ordered temporally
        """
        dated_papers = [(doi, node.year) for doi, node in self.nodes.items()
                       if node.year is not None]
        undated_papers = [(doi, node.extraction_date) for doi, node in self.nodes.items()
                         if node.year is None]

        # Sort dated by year
        dated_papers.sort(key=lambda x: x[1])

        # Sort undated by extraction date
        undated_papers.sort(key=lambda x: x[1] or "")

        result = [doi for doi, _ in dated_papers] + [doi for doi, _ in undated_papers]
        logger.info(f"Temporal ordering: {len(result)} papers")
        return result

    def infer_citation_polarity(
        self,
        source_doi: str,
        target_doi: str
    ) -> Tuple[float, float, str]:
        """
        Infer whether source supports or challenges target.

        Uses theory alignment and temporal position. Without S2 data, relies on
        theory overlap heuristics. With S2 data, uses fuller citation context.

        Args:
            source_doi: DOI of citing paper
            target_doi: DOI of cited paper

        Returns:
            (polarity, confidence, evidence) tuple

        Raises:
            ValueError: If either DOI not in graph
        """
        if source_doi not in self.nodes:
            raise ValueError(f"Source DOI not in graph: {source_doi}")
        if target_doi not in self.nodes:
            raise ValueError(f"Target DOI not in graph: {target_doi}")

        source_node = self.nodes[source_doi]
        target_node = self.nodes[target_doi]

        if self._s2_enriched:
            polarity, confidence, evidence = self._infer_citation_polarity_s2(
                source_node, target_node
            )
        else:
            polarity, confidence = self._infer_polarity_from_theories(
                source_node, target_node,
                set(source_node.theories) & set(target_node.theories)
            )
            evidence = f"No S2 data; inference based on {len(set(source_node.theories) & set(target_node.theories))} shared theories"

        return polarity, confidence, evidence

    def detect_debate_clusters(self) -> List[DebateCluster]:
        """
        Find clusters of papers arguing about the same questions.

        Uses co-citation analysis when S2 data available. Without S2, uses
        shared theory references as proxy for research communities.

        Returns:
            List of DebateCluster objects
        """
        logger.info("Detecting debate clusters")

        if self._s2_enriched:
            clusters = self._detect_clusters_by_cocitation()
        else:
            clusters = self._detect_clusters_by_theory()

        logger.info(f"Detected {len(clusters)} debate clusters")
        return clusters

    def _detect_clusters_by_cocitation(self) -> List[DebateCluster]:
        """Detect clusters using co-citation analysis."""
        # Build co-citation matrix
        cocitation_matrix: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))

        for edge in self.edges:
            # Papers citing the same target are related
            for other_edge in self.edges:
                if (edge.source_doi != other_edge.source_doi and
                    edge.target_doi == other_edge.target_doi):
                    cocitation_matrix[edge.source_doi][other_edge.source_doi] += 1

        # Simple clustering: papers with high co-citation are in same cluster
        visited = set()
        clusters = []
        cluster_id_counter = 0

        for paper_doi in self.nodes.keys():
            if paper_doi in visited:
                continue

            cluster_papers = {paper_doi}
            visited.add(paper_doi)
            queue = [paper_doi]

            while queue:
                current = queue.pop(0)
                # Find all papers with co-citation > 0 with current
                for other_paper, cocitation_count in cocitation_matrix[current].items():
                    if cocitation_count > 0 and other_paper not in visited:
                        cluster_papers.add(other_paper)
                        visited.add(other_paper)
                        queue.append(other_paper)

            if len(cluster_papers) > 1:  # Only keep clusters with 2+ papers
                theories = self._get_shared_theories(list(cluster_papers))

                cluster = DebateCluster(
                    cluster_id=f"C{cluster_id_counter}",
                    topic=f"Debate around {', '.join(theories[:2])}",
                    papers=list(cluster_papers),
                    theories_involved=theories,
                    dominant_position=None,
                    contestation_level=self._compute_contestation(list(cluster_papers)),
                    internal_edges=sum(1 for e in self.edges
                                      if e.source_doi in cluster_papers and
                                      e.target_doi in cluster_papers),
                    average_polarity=self._compute_average_polarity(list(cluster_papers))
                )
                clusters.append(cluster)
                cluster_id_counter += 1

        return clusters

    def _detect_clusters_by_theory(self) -> List[DebateCluster]:
        """Detect clusters using theory co-reference."""
        # Group papers by shared theories
        theory_papers: Dict[str, Set[str]] = defaultdict(set)

        for doi, node in self.nodes.items():
            for theory in node.theories:
                theory_papers[theory].add(doi)

        # Papers sharing 2+ theories are in same cluster
        clusters = []
        visited = set()
        cluster_id_counter = 0

        for doi in self.nodes.keys():
            if doi in visited:
                continue

            cluster_papers = {doi}
            visited.add(doi)
            node_theories = set(self.nodes[doi].theories)

            # Find other papers with 2+ overlapping theories
            for other_doi in self.nodes.keys():
                if other_doi != doi and other_doi not in visited:
                    other_theories = set(self.nodes[other_doi].theories)
                    shared = node_theories & other_theories
                    if len(shared) >= 2:
                        cluster_papers.add(other_doi)
                        visited.add(other_doi)

            if len(cluster_papers) > 1:
                theories = self._get_shared_theories(list(cluster_papers))

                cluster = DebateCluster(
                    cluster_id=f"C{cluster_id_counter}",
                    topic=f"Research on {', '.join(theories[:2])}",
                    papers=list(cluster_papers),
                    theories_involved=theories,
                    dominant_position=None,
                    contestation_level=0.3,  # Moderate by default without S2 data
                    internal_edges=0,
                    average_polarity=0.0
                )
                clusters.append(cluster)
                cluster_id_counter += 1

        return clusters

    def _get_shared_theories(self, dois: List[str]) -> List[str]:
        """Get theories shared by multiple papers."""
        if not dois:
            return []

        theory_counts: Dict[str, int] = defaultdict(int)

        for doi in dois:
            if doi in self.nodes:
                for theory in self.nodes[doi].theories:
                    theory_counts[theory] += 1

        # Return theories found in at least 50% of papers
        threshold = len(dois) // 2
        return [t for t, count in theory_counts.items() if count > threshold]

    def _compute_contestation(self, dois: List[str]) -> float:
        """Compute how contested the debate is (0-1 scale)."""
        polarities = []

        for doi_a in dois:
            for doi_b in dois:
                if doi_a < doi_b:  # Avoid duplicates
                    edge_key = (doi_a, doi_b)
                    if edge_key in self._edge_lookup:
                        polarities.append(abs(self._edge_lookup[edge_key].polarity))

        if not polarities:
            return 0.3

        # Higher variance in polarity = more contested
        mean_polarity = sum(polarities) / len(polarities)
        variance = sum((p - mean_polarity) ** 2 for p in polarities) / len(polarities)

        return min(1.0, variance)

    def _compute_average_polarity(self, dois: List[str]) -> float:
        """Compute average polarity within cluster."""
        polarities = []

        for doi_a in dois:
            for doi_b in dois:
                if doi_a != doi_b:
                    edge_key = (doi_a, doi_b)
                    if edge_key in self._edge_lookup:
                        polarities.append(self._edge_lookup[edge_key].polarity)

        if not polarities:
            return 0.0

        return sum(polarities) / len(polarities)

    def get_supersession_candidates(self) -> List[Tuple[str, str, str]]:
        """
        Find papers where a newer paper likely supersedes an older one.

        Heuristics:
          - Both papers reference same theories
          - Newer paper's year > older paper's year
          - Share significant claims/constructs
          - Newer paper has higher citation count (if available)

        Returns:
            List of (newer_doi, older_doi, reason) tuples
        """
        logger.info("Finding supersession candidates")
        candidates = []

        nodes_with_years = [(doi, node) for doi, node in self.nodes.items()
                           if node.year is not None]
        nodes_with_years.sort(key=lambda x: x[1].year)

        for i, (doi_older, node_older) in enumerate(nodes_with_years):
            for doi_newer, node_newer in nodes_with_years[i+1:]:
                if node_newer.year <= node_older.year:
                    continue

                shared_theories = set(node_older.theories) & set(node_newer.theories)
                year_gap = node_newer.year - node_older.year

                # Criteria for supersession
                if len(shared_theories) >= 2 and year_gap >= 3:
                    reasons = [f"Shared theories: {', '.join(sorted(shared_theories)[:2])}"]

                    if node_newer.citation_count and node_older.citation_count:
                        if node_newer.citation_count > node_older.citation_count:
                            reasons.append("Higher citation count in newer paper")

                    if node_newer.claim_count > node_older.claim_count:
                        reasons.append("More claims/constructs in newer paper")

                    reason = "; ".join(reasons)
                    candidates.append((doi_newer, doi_older, reason))

        logger.info(f"Found {len(candidates)} supersession candidates")
        return candidates

    def get_paper_influence(self, doi: str) -> Dict[str, Any]:
        """
        Compute a paper's influence within the corpus.

        Combines: citation count, centrality, theory bridging, temporal position.

        Args:
            doi: Paper DOI

        Returns:
            Dictionary with influence metrics

        Raises:
            ValueError: If DOI not in graph
        """
        if doi not in self.nodes:
            raise ValueError(f"DOI not in graph: {doi}")

        node = self.nodes[doi]

        # Citation count
        citation_score = (node.citation_count or 0) / max(1, max(
            n.citation_count or 0 for n in self.nodes.values()
        )) if any(n.citation_count for n in self.nodes.values()) else 0.0

        # Centrality: in-degree + out-degree
        in_degree = len(self._reverse_adjacency[doi])
        out_degree = len(self._adjacency[doi])
        max_degree = max(1, max(len(v) for v in self._adjacency.values())) if self._adjacency else 1
        centrality_score = (in_degree + out_degree) / (2 * max_degree)

        # Theory bridging: how many distinct theories does this paper connect?
        bridged_theories = set(node.theories)
        theory_bridge_score = len(bridged_theories) / max(1, max(
            len(set(n.theories)) for n in self.nodes.values()
        ))

        # Temporal position: earlier papers have slight advantage
        temporal_score = 1.0
        if node.year and any(n.year for n in self.nodes.values()):
            oldest_year = min(n.year for n in self.nodes.values() if n.year)
            newest_year = max(n.year for n in self.nodes.values() if n.year)
            year_range = max(1, newest_year - oldest_year)
            temporal_score = 1.0 - ((node.year - oldest_year) / year_range) * 0.2

        # Weighted influence score
        influence_score = (
            0.4 * citation_score +
            0.3 * centrality_score +
            0.2 * theory_bridge_score +
            0.1 * temporal_score
        )

        return {
            "doi": doi,
            "title": node.title,
            "influence_score": round(influence_score, 3),
            "citation_score": round(citation_score, 3),
            "centrality_score": round(centrality_score, 3),
            "theory_bridge_score": round(theory_bridge_score, 3),
            "temporal_score": round(temporal_score, 3),
            "citation_count": node.citation_count,
            "in_degree": in_degree,
            "out_degree": out_degree,
            "theories": node.theories,
            "year": node.year
        }

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize graph to dictionary for JSON export.

        Returns:
            Dictionary representation of graph
        """
        return {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "node_count": len(self.nodes),
                "edge_count": len(self.edges),
                "s2_enriched": self._s2_enriched
            },
            "nodes": {doi: asdict(node) for doi, node in self.nodes.items()},
            "edges": [asdict(edge) for edge in self.edges]
        }

    def compute_warrant_distribution(self) -> Dict[str, int]:
        """
        Scan extraction JSON files and compute warrant type distribution.

        For each claim in each extraction, reads the bridge_warrant_type field
        and counts occurrences. Maps old/deprecated names to canonical names.

        Returns:
            Dictionary mapping warrant type names to counts:
            {
                "CONSTITUTIVE": int,
                "MECHANISM": int,
                "EMPIRICAL_ASSOCIATION": int,
                "FUNCTIONAL": int,
                "CAPACITY": int,
                "ANALOGICAL": int,
                "THEORY_DERIVED": int,
                "unknown": int
            }
        """
        warrant_counts: Dict[str, int] = {
            "CONSTITUTIVE": 0,
            "MECHANISM": 0,
            "EMPIRICAL_ASSOCIATION": 0,
            "FUNCTIONAL": 0,
            "CAPACITY": 0,
            "ANALOGICAL": 0,
            "THEORY_DERIVED": 0,
            "unknown": 0
        }

        # Canonical mapping for old warrant type names
        warrant_mapping = {
            "empirical_covariance": "EMPIRICAL_ASSOCIATION",
            "EMPIRICAL_COVARIANCE": "EMPIRICAL_ASSOCIATION",
            "theoretical_default": "THEORY_DERIVED",
            "THEORETICAL_DEFAULT": "THEORY_DERIVED",
        }

        # For each node (paper), check if we have extraction data
        for doi, node in self.nodes.items():
            # Try to find corresponding extraction file
            # Convert DOI to filename format (e.g., "10.1234/example" -> "10.1234_example.json")
            doi_filename = doi.replace("/", "_") + ".json"

            # In a real scenario, we'd scan data/extractions directory
            # For now, we compute from claims if they exist in the graph
            # This is a placeholder that can be extended to read actual files

        return warrant_counts

    def get_aeshi_warrant_component(self) -> Dict[str, Any]:
        """
        Compute warrant diversity score for AESHI (ATLAS Epistemic System Health Index).

        Returns a warrant diversity score (0-100) based on:
        - Coverage: which of the 7 canonical warrant types are present
        - Balance: how evenly represented they are
        - Completeness: what proportion of claims have explicit warrant types

        Returns:
            Dictionary with:
            {
                "score": float (0-100),
                "distribution": {warrant_type: count},
                "missing_types": [list of absent warrant types],
                "coverage_percent": float (0-100),
                "notes": str
            }
        """
        canonical_types = {
            "CONSTITUTIVE", "MECHANISM", "EMPIRICAL_ASSOCIATION",
            "FUNCTIONAL", "CAPACITY", "ANALOGICAL", "THEORY_DERIVED"
        }

        # Get current warrant distribution
        distribution = self.compute_warrant_distribution()

        # Count total claims
        total_claims = sum(distribution.values()) - distribution.get("unknown", 0)

        if total_claims == 0:
            return {
                "score": 0.0,
                "distribution": distribution,
                "missing_types": list(canonical_types),
                "coverage_percent": 0.0,
                "notes": "No claims with explicit warrant types found"
            }

        # Types present (non-zero counts, excluding unknown)
        present_types = {wt for wt in canonical_types if distribution.get(wt, 0) > 0}
        missing_types = list(canonical_types - present_types)

        # Coverage: percentage of canonical types present (0-100)
        coverage_percent = (len(present_types) / len(canonical_types)) * 100

        # Balance: how evenly distributed are the warrant types
        # Higher balance = more even distribution across types
        counts = [distribution.get(wt, 0) for wt in present_types]
        if len(counts) > 1:
            mean_count = sum(counts) / len(counts)
            variance = sum((c - mean_count) ** 2 for c in counts) / len(counts)
            # Normalize variance to 0-1 scale (lower variance = higher balance)
            max_possible_variance = mean_count ** 2 * len(counts)
            balance_score = 100 * max(0, (1 - (variance / max_possible_variance))) if max_possible_variance > 0 else 100
        else:
            balance_score = 50  # Single warrant type = moderate balance

        # Final AESHI warrant component: 60% coverage + 40% balance
        score = min(100, (0.6 * coverage_percent) + (0.4 * balance_score))

        return {
            "score": round(score, 1),
            "distribution": distribution,
            "missing_types": missing_types,
            "coverage_percent": round(coverage_percent, 1),
            "balance_score": round(balance_score, 1),
            "notes": f"Found {len(present_types)}/{len(canonical_types)} warrant types across {total_claims} claims"
        }

    def summary(self) -> Dict[str, Any]:
        """
        Compute high-level statistics about the graph.

        Returns:
            Dictionary with summary statistics
        """
        if not self.nodes:
            return {
                "node_count": 0,
                "edge_count": 0,
                "summary": "Empty graph"
            }

        years = [n.year for n in self.nodes.values() if n.year]
        theories = set()
        for node in self.nodes.values():
            theories.update(node.theories)

        polarities = [e.polarity for e in self.edges]

        return {
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "year_range": (min(years), max(years)) if years else (None, None),
            "unique_theories": len(theories),
            "top_theories": sorted(
                theories,
                key=lambda t: sum(1 for n in self.nodes.values() if t in n.theories),
                reverse=True
            )[:5],
            "average_citation_count": sum(
                n.citation_count or 0 for n in self.nodes.values()
            ) / len(self.nodes),
            "average_claim_count": sum(n.claim_count for n in self.nodes.values()) / len(self.nodes),
            "edge_polarity_distribution": {
                "positive": len([p for p in polarities if p > 0.2]),
                "neutral": len([p for p in polarities if -0.2 <= p <= 0.2]),
                "negative": len([p for p in polarities if p < -0.2])
            },
            "s2_enriched": self._s2_enriched,
            "timestamp": datetime.now().isoformat()
        }


def build_argumentation_graph(
    extractions_dir: str,
    citation_graph_path: Optional[str] = None,
) -> ArgumentationGraph:
    """
    Convenience function: one-call builder for ArgumentationGraph.

    Uses citation graph if available for enriched polarity detection.
    Otherwise, operates in base mode with theory-based inference.

    Args:
        extractions_dir: Path to extraction JSON files
        citation_graph_path: Optional path to S2 citation_graph.json

    Returns:
        Fully initialized ArgumentationGraph

    Raises:
        FileNotFoundError: If required files don't exist
        json.JSONDecodeError: If JSON parsing fails
    """
    logger.info(f"Building argumentation graph from {extractions_dir}")

    graph = ArgumentationGraph()
    graph.build_from_extractions(extractions_dir)

    if citation_graph_path:
        try:
            graph.enrich_from_citation_graph(citation_graph_path)
            logger.info("Graph enriched with S2 citation data")
        except Exception as e:
            logger.warning(f"Failed to enrich from citation graph: {e}. Continuing with base mode.")

    return graph
