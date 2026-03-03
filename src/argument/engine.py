"""
Unified Argumentation Engine
============================

Facade that unifies all argumentation modules into a single queryable interface:
- CritiqueAggregator: critique collection + vulnerability reports
- HierarchyAggregator: hierarchy evidence + pairwise comparisons
- MetaAnalyticAggregator: pooled effects, I², publication bias
- PaperRelation: inter-paper argument relations
- ArgumentQueryHandler: query routing + response formatting

Usage:
    from src.argument.engine import ArgumentationEngine
    engine = ArgumentationEngine()
    
    # What critiques exist for a paper?
    result = engine.query("What critiques exist for Ulrich 1991?")
    
    # How strong is the evidence for a hierarchy?
    result = engine.query("How strong is evidence for attention restoration?")
    
    # Get vulnerability report for a topic
    report = engine.vulnerability_report("biophilia")
    
    # Search for argumentation structure across findings
    args = engine.find_arguments("nature reduces stress")
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.argument.critique_aggregator import CritiqueAggregator
from src.argument.hierarchy_evidence import HierarchyAggregator
from src.argument.meta_analytic import MetaAnalyticAggregator
from src.argument.paper_relations import (
    PaperRelation,
    PaperRelationType,
    extract_paper_relations_from_citation_analysis,
)
from src.argument.qa_handlers import ArgumentQueryHandler

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent
EXTRACTION_DIR = PROJECT_ROOT / "data" / "extractions"


class ArgumentationEngine:
    """Unified argumentation engine that composes all argument modules.
    
    Provides a single interface for:
    - Querying critiques and vulnerabilities for any paper/claim
    - Assessing hierarchy evidence strength
    - Finding argument structures across the extraction corpus
    - Meta-analytic aggregation from study-level data
    """

    def __init__(self):
        self.critique_agg = CritiqueAggregator()
        self.hierarchy_agg = HierarchyAggregator()
        self.meta_agg = MetaAnalyticAggregator()
        self.query_handler = ArgumentQueryHandler(
            critique_aggregator=self.critique_agg,
            hierarchy_aggregator=self.hierarchy_agg,
        )
        self._extraction_cache: Optional[List[Dict]] = None
        self._loaded = False

    def _ensure_loaded(self):
        """Lazy-load extraction data for argumentation analysis."""
        if self._loaded:
            return
        self._loaded = True
        
        if not EXTRACTION_DIR.exists():
            return
            
        for fp in sorted(EXTRACTION_DIR.glob("*.json")):
            try:
                with open(fp) as f:
                    data = json.load(f)
                doi = data.get("doi", data.get("DOI", fp.stem))
                
                # Extract citation-based relations if present
                citations = data.get("citation_analysis", [])
                if citations:
                    relations = extract_paper_relations_from_citation_analysis(doi, citations)
                    self.critique_agg.add_relations(relations)
            except Exception:
                continue

    def query(self, question: str) -> Optional[Dict[str, Any]]:
        """Route an argumentation query to the appropriate handler.
        
        Handles:
        - "What critiques exist for X?" → critique aggregation
        - "How strong is the evidence for X?" → hierarchy evidence
        
        Returns None if the question doesn't match argumentation patterns.
        """
        self._ensure_loaded()
        
        import time
        query_id = f"arg_{int(time.time() * 1000)}"
        start = time.time()
        
        result = self.query_handler.handle_query(
            query_id=query_id,
            query_text=question,
            processing_time_ms=0,
        )
        
        if result:
            result["metadata"]["processing_time_ms"] = int((time.time() - start) * 1000)
        
        return result

    def vulnerability_report(self, target_id: str) -> Dict[str, Any]:
        """Get vulnerability report for a paper/claim."""
        self._ensure_loaded()
        return self.critique_agg.vulnerability_report(target_id)

    def find_arguments(self, topic: str, max_results: int = 10) -> Dict[str, Any]:
        """Search extraction findings for argument structures related to a topic.
        
        Looks for:
        - Conflicting findings (same antecedent, different directions)
        - Supporting chains (A→B, B→C)
        - Theory-mediated arguments
        """
        from src.services.arbitrary_qa_handler import _search_findings
        
        results = _search_findings(topic, max_results=50)
        
        if not results:
            return {
                "topic": topic,
                "arguments_found": 0,
                "supporting": [],
                "opposing": [],
                "tensions": [],
                "headline": f"No argumentation structures found for '{topic}'.",
            }
        
        # Classify by direction
        supporting = []
        opposing = []
        for f in results:
            direction = str(f.get("direction", "")).lower()
            entry = {
                "claim": f"{f.get('antecedent', '?')} → {f.get('consequent', '?')}",
                "direction": direction,
                "source": f.get("_source_doi", ""),
                "theories": f.get("theory_links") or f.get("theory_commitments") or [],
                "sample_size": f.get("sample_size"),
                "effect_size": f.get("effect_size"),
            }
            if direction in ("increase", "positive", "supports"):
                supporting.append(entry)
            elif direction in ("decrease", "negative", "contradicts", "reduces"):
                opposing.append(entry)
            else:
                supporting.append(entry)  # Default to supporting
        
        # Find tensions: same consequent, different directions
        tensions = []
        consequents_seen = {}
        for f in results:
            cons = f.get("consequent", "")
            direction = str(f.get("direction", "")).lower()
            if cons in consequents_seen:
                prev_dir = consequents_seen[cons]
                if prev_dir != direction:
                    tensions.append({
                        "consequent": cons,
                        "direction_a": prev_dir,
                        "direction_b": direction,
                    })
            else:
                consequents_seen[cons] = direction
        
        return {
            "topic": topic,
            "arguments_found": len(results),
            "supporting": supporting[:max_results],
            "opposing": opposing[:max_results],
            "tensions": tensions,
            "theory_coverage": list(set(
                str(t) for f in results
                for t in (f.get("theory_links") or f.get("theory_commitments") or [])
            ))[:10],
            "headline": (
                f"Found {len(supporting)} supporting and {len(opposing)} opposing "
                f"arguments for '{topic}' with {len(tensions)} tensions."
            ),
        }

    def summary(self) -> Dict[str, Any]:
        """Get overall argumentation system summary."""
        self._ensure_loaded()
        return {
            "critique_relations": len(self.critique_agg._relations),
            "capabilities": [
                "Critique aggregation (method, stimulus, population, assumption, interpretation, statistics)",
                "Hierarchy evidence assessment (ordered levels, pairwise comparisons, indirect chains)",
                "Meta-analytic aggregation (pooled effects, I², Q-stat, publication bias detection)",
                "Argument search across 33K+ extraction findings",
                "Tension detection (conflicting directions for same consequent)",
            ],
        }
