"""
CVA QA Enricher — CVA→QA Bridge (Sprint S-6)
==============================================

Enriches QA query responses with CVA analysis when the query
touches on CVA-relevant topics. Integrates with the existing
ArgumentQueryHandler pipeline.

Usage:
    from src.services.cva_qa_enricher import CVAQAEnricher
    
    enricher = CVAQAEnricher()
    
    # Called after standard QA processing
    enriched = enricher.enrich_response(query_text, base_response)
"""

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent
MOLECULES_DIR = PROJECT_ROOT / "data" / "molecules"
CVA_MAPPING_PATH = PROJECT_ROOT / "data" / "feature_cva_mapping.json"
ANNOTATION_STORE = PROJECT_ROOT / "data" / "cva_annotations"


# =============================================================================
# CVA Query Patterns
# =============================================================================

CVA_PATTERNS = {
    "beauty": re.compile(
        r'\b(?:beaut|aesthet|visual\s+appeal|attractive|ugly|visual\s+preference)', re.I),
    "restoration": re.compile(
        r'\b(?:restor|ART\b|attention\s+restoration|recover|stress\s+re(?:duction|covery|lief))', re.I),
    "complexity": re.compile(
        r'\b(?:complex|fractal|visual\s+richness|entropy|information\s+density)', re.I),
    "prospect_refuge": re.compile(
        r'\b(?:prospect|refuge|enclosure|open\s+space|shelter|vista|overlook)', re.I),
    "wayfinding": re.compile(
        r'\b(?:wayfinding|navigat|orient|legib|get\s+lost)', re.I),
    "biophilia": re.compile(
        r'\b(?:biophil|nature\s+connect|green\s+design|natural\s+elements|vegetation)', re.I),
    "cultural": re.compile(
        r'\b(?:cultur|cross[\s-]*cultur|eastern|western|individ|collectiv)', re.I),
    "safety": re.compile(
        r'\b(?:safety|danger|threat|crime|fear|secure|surveillance)', re.I),
}


class CVAQAEnricher:
    """Enriches QA responses with CVA analysis."""
    
    def __init__(self):
        self._molecules = self._load_molecules()
        self._feature_map = self._load_feature_mapping()
    
    def enrich_response(self, query_text: str, 
                        base_response: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich a QA response with CVA analysis if relevant.
        
        Args:
            query_text: The original user query
            base_response: The response from standard QA pipeline
            
        Returns:
            Enriched response with CVA section added (or original if not relevant)
        """
        # Check if query touches CVA topics
        cva_topics = self._detect_cva_topics(query_text)
        if not cva_topics:
            return base_response
        
        # Build CVA enrichment
        enrichment = self._build_enrichment(query_text, cva_topics)
        
        # Merge into response
        response = dict(base_response)
        response["cva_analysis"] = enrichment
        
        # Add CVA follow-up questions
        follow_ups = response.get("follow_ups", [])
        follow_ups.extend(self._generate_cva_followups(cva_topics))
        response["follow_ups"] = follow_ups
        
        return response
    
    def _detect_cva_topics(self, text: str) -> List[str]:
        """Detect which CVA topics a query touches."""
        topics = []
        for topic, pattern in CVA_PATTERNS.items():
            if pattern.search(text):
                topics.append(topic)
        return topics
    
    def _build_enrichment(self, query: str, topics: List[str]) -> Dict[str, Any]:
        """Build CVA enrichment section for response."""
        enrichment = {
            "cva_relevant": True,
            "topics_detected": topics,
            "constraints_relevant": [],
            "valuations_relevant": [],
            "molecules_relevant": [],
            "image_features_relevant": [],
            "cultural_variants": [],
            "summary": "",
        }
        
        # Map topics to constraints
        constraint_map = {
            "beauty": ["C_BEAUTY", "C_COMPLEXITY", "C_COHERENCE"],
            "restoration": ["C_BIOPHILIA", "C_FASCINATION"],
            "complexity": ["C_COMPLEXITY", "C_COHERENCE"],
            "prospect_refuge": ["C_PROSPECT_REFUGE", "C_SAFETY"],
            "wayfinding": ["C_LEGIBILITY", "C_COHERENCE"],
            "biophilia": ["C_BIOPHILIA", "C_FASCINATION"],
            "cultural": [],  # Cultural modulates all constraints
            "safety": ["C_SAFETY", "C_PROSPECT_REFUGE"],
        }
        
        valuation_map = {
            "beauty": ["V_BEAUTY", "V_NOVELTY"],
            "restoration": ["V_COMFORT", "V_NATURE"],
            "complexity": ["V_NOVELTY", "V_BEAUTY"],
            "prospect_refuge": ["V_SAFETY", "V_COMFORT"],
            "wayfinding": ["V_FUNCTION", "V_SAFETY"],
            "biophilia": ["V_NATURE", "V_COMFORT"],
            "cultural": ["V_MEANING", "V_SOCIAL"],
            "safety": ["V_SAFETY"],
        }
        
        for topic in topics:
            enrichment["constraints_relevant"].extend(
                constraint_map.get(topic, []))
            enrichment["valuations_relevant"].extend(
                valuation_map.get(topic, []))
        
        # Deduplicate
        enrichment["constraints_relevant"] = sorted(set(enrichment["constraints_relevant"]))
        enrichment["valuations_relevant"] = sorted(set(enrichment["valuations_relevant"]))
        
        # Find relevant molecules
        molecule_map = {
            "beauty": "M_BEAUTY_COMPRESSION",
            "restoration": "M_RASA",
            "cultural": "M_CULTURAL_VALUATION",
            "complexity": "M_ATTRACTOR_TRANSITION",
        }
        for topic in topics:
            if topic in molecule_map:
                mol_id = molecule_map[topic]
                mol = self._molecules.get(mol_id)
                if mol:
                    enrichment["molecules_relevant"].append({
                        "id": mol_id,
                        "name": mol.get("name", mol_id),
                        "summary": mol.get("summary", "")[:150],
                    })
        
        # Find relevant image features
        if self._feature_map:
            for constraint in enrichment["constraints_relevant"]:
                features = self._feature_map.get("cva_to_feature", {}).get(constraint, [])
                enrichment["image_features_relevant"].extend(features)
            enrichment["image_features_relevant"] = sorted(set(
                enrichment["image_features_relevant"]))
        
        # Cultural variant note
        if "cultural" in topics:
            enrichment["cultural_variants"] = [
                {"culture": "Western (individualist)", "note": "Beauty emphasis, prospect preference"},
                {"culture": "East Asian (collectivist)", "note": "Harmony emphasis, enclosure comfort"},
                {"culture": "Islamic", "note": "Geometric complexity, water features valued"},
                {"culture": "Scandinavian", "note": "Nature integration, minimalist order"},
            ]
        
        # Build summary
        enrichment["summary"] = self._build_summary(topics, enrichment)
        
        return enrichment
    
    def _build_summary(self, topics: List[str], enrichment: Dict) -> str:
        """Generate a natural-language CVA summary."""
        parts = []
        
        if enrichment["constraints_relevant"]:
            cnames = ", ".join(c.replace("C_", "").replace("_", " ").title() 
                             for c in enrichment["constraints_relevant"][:3])
            parts.append(f"CVA constraints relevant: {cnames}")
        
        if enrichment["molecules_relevant"]:
            mnames = ", ".join(m["name"] for m in enrichment["molecules_relevant"])
            parts.append(f"Related molecules: {mnames}")
        
        if "cultural" in topics:
            parts.append("Cultural valuation variants apply — preferences may differ across cultures")
        
        if enrichment["image_features_relevant"]:
            parts.append(
                f"{len(enrichment['image_features_relevant'])} image features "
                f"can be measured for this construct"
            )
        
        return ". ".join(parts) + "." if parts else "No specific CVA analysis applicable."
    
    def _generate_cva_followups(self, topics: List[str]) -> List[Dict]:
        """Generate CVA-specific follow-up questions."""
        followups = []
        
        if "beauty" in topics:
            followups.append({
                "question": "How does visual complexity interact with beauty judgments across cultures?",
                "type": "cva_deeper",
                "cva_topic": "beauty",
            })
        
        if "restoration" in topics:
            followups.append({
                "question": "What image features predict restorative potential of a space?",
                "type": "cva_deeper",
                "cva_topic": "restoration",
            })
        
        if "wayfinding" in topics:
            followups.append({
                "question": "How do legibility and complexity trade off in wayfinding performance?",
                "type": "cva_deeper",
                "cva_topic": "wayfinding",
            })
        
        return followups
    
    def _load_molecules(self) -> Dict[str, dict]:
        """Load molecule definitions."""
        molecules = {}
        for mp in MOLECULES_DIR.glob("*.json"):
            try:
                with open(mp) as f:
                    mol = json.load(f)
                mol_id = mp.stem
                molecules[mol_id] = mol
            except Exception as e:
                logger.debug(f"Non-critical: {e}")
        return molecules
    
    def _load_feature_mapping(self) -> Dict:
        """Load feature ↔ CVA mapping."""
        if CVA_MAPPING_PATH.exists():
            with open(CVA_MAPPING_PATH) as f:
                return json.load(f)
        return {}


def enrich_qa_response(query_text: str, response: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function for pipeline integration."""
    enricher = CVAQAEnricher()
    return enricher.enrich_response(query_text, response)
