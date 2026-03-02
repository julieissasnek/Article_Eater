"""
Read-Next Engine — Structured Exploration Suggestions
======================================================

Generates "What To Read Next" suggestions organized by:
  - Theory (T1/T1.5/T2)
  - Mechanism (how things work)
  - Cultural variant
  - Surprising findings
  - Design implications
  - Open questions

Also attaches relevant stimulus images to QA responses so users
can see what a "prospect-refuge environment" or "biophilic design"
actually looks like.

Panel Review (Robin Wall Kimmerer, Merlin Sheldrake, Anil Seth,
Ed Yong, Saidiya Hartman):
- Every answer should offer multiple paths forward
- Organize suggestions by cognitive mode (explore, deepen, challenge)
- Images make abstract theory concrete; prioritize real environments
- Don't just suggest more reading — suggest different ANGLES

Usage:
    from src.services.read_next_engine import ReadNextEngine
    engine = ReadNextEngine()
    suggestions = engine.suggest(topic="biophilia", context=qa_response)
"""

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent
MOLECULES_DIR = PROJECT_ROOT / "data" / "molecules"
EXT_ANN_DIR = PROJECT_ROOT / "data" / "extended_annotations"
IMAGE_REPORTS_DIR = PROJECT_ROOT / "data" / "image_extraction_reports"


# =============================================================================
# Topic ↔ Theory/Molecule/Cultural Mapping
# =============================================================================

TOPIC_MAP = {
    # Topic keywords → {theories, molecules, cultural_dims, mechanisms}
    "attention": {
        "theories": ["ART"],
        "molecules": ["art", "M_GOLDILOCKS_STIM"],
        "mechanisms": ["directed_attention_fatigue", "fascination", "involuntary_attention"],
        "cultural_dims": ["Temporal & Circadian Patterns"],
        "image_queries": ["natural landscape", "park bench reading", "forest path"],
    },
    "stress": {
        "theories": ["SRT", "ART"],
        "molecules": ["srt", "allostatic_regulation"],
        "mechanisms": ["cortisol_response", "parasympathetic_activation", "affective_restoration"],
        "cultural_dims": ["Nature Connection"],
        "image_queries": ["hospital garden", "healing garden", "calm water feature"],
    },
    "biophil": {
        "theories": ["BIOPHILIA", "ART", "SRT"],
        "molecules": ["biophilia", "M_BEAUTY_COMPRESSION"],
        "mechanisms": ["nature_affiliation", "evolutionary_preference", "biophilic_response"],
        "cultural_dims": ["Nature Connection", "Beauty & Aesthetic Judgment"],
        "image_queries": ["living wall", "indoor plants", "natural light workspace", "green building"],
    },
    "prospect": {
        "theories": ["PROSPECT_REFUGE"],
        "molecules": ["prospect_refuge"],
        "mechanisms": ["threat_detection", "habitat_selection", "spatial_preference"],
        "cultural_dims": ["Prospect-Refuge Preferences"],
        "image_queries": ["panoramic view", "corner booth restaurant", "window seat", "open vista"],
    },
    "beauty": {
        "theories": ["KAPLAN_PREFERENCE"],
        "molecules": ["M_BEAUTY_COMPRESSION", "M_RASA_AESTHETIC"],
        "mechanisms": ["peak_shift", "processing_fluency", "aesthetic_emotion"],
        "cultural_dims": ["Beauty & Aesthetic Judgment", "Color Meaning & Preference"],
        "image_queries": ["beautiful architecture", "ornate ceiling", "symmetrical building"],
    },
    "complex": {
        "theories": ["KAPLAN_PREFERENCE", "COGNITIVE_LOAD"],
        "molecules": ["M_GOLDILOCKS_STIM", "M_BEAUTY_COMPRESSION"],
        "mechanisms": ["inverted_U", "optimal_stimulation", "information_rate"],
        "cultural_dims": ["Beauty & Aesthetic Judgment"],
        "image_queries": ["ornate facade", "minimal interior", "complex pattern"],
    },
    "light": {
        "theories": ["COGNITIVE_LOAD"],
        "molecules": ["circadian_architecture"],
        "mechanisms": ["circadian_entrainment", "melatonin_suppression", "spectral_sensitivity"],
        "cultural_dims": ["Temporal & Circadian Patterns"],
        "image_queries": ["natural daylight office", "warm lighting bedroom", "dynamic lighting"],
    },
    "wayfind": {
        "theories": ["COGNITIVE_LOAD", "KAPLAN_PREFERENCE"],
        "molecules": ["wayfinding"],
        "mechanisms": ["cognitive_map", "spatial_legibility", "landmark_recognition"],
        "cultural_dims": [],
        "image_queries": ["clear signage", "hospital corridor", "building entrance"],
    },
    "social": {
        "theories": ["PROSPECT_REFUGE"],
        "molecules": ["social_architecture"],
        "mechanisms": ["social_density", "privacy_regulation", "interaction_affordance"],
        "cultural_dims": ["Social Space & Privacy"],
        "image_queries": ["open office", "collaborative space", "private booth"],
    },
    "awe": {
        "theories": [],
        "molecules": ["awe_architecture"],
        "mechanisms": ["self_diminishment", "vastness_perception", "meaning_making"],
        "cultural_dims": ["Beauty & Aesthetic Judgment"],
        "image_queries": ["cathedral interior", "vast atrium", "towering ceiling"],
    },
    "creativ": {
        "theories": [],
        "molecules": ["creative_environments"],
        "mechanisms": ["divergent_thinking", "cognitive_flexibility", "environmental_autonomy"],
        "cultural_dims": [],
        "image_queries": ["creative workspace", "colorful office", "maker space"],
    },
}


# =============================================================================
# Suggestion Types
# =============================================================================

class SuggestionCategory:
    DEEPEN = "deepen"        # Go deeper into current topic
    BROADEN = "broaden"      # Explore related theories
    CHALLENGE = "challenge"  # See counterevidence/disputes
    APPLY = "apply"          # Get design guidance
    VISUALIZE = "visualize"  # See images/real examples
    FRONTIER = "frontier"    # See what's unknown


# =============================================================================
# Read Next Engine
# =============================================================================

class ReadNextEngine:
    """Generates structured 'what to read next' suggestions."""
    
    def __init__(self):
        self._molecules = self._load_molecules()
        self._hooks = self._load_seed_file("_hooks.json")
        self._disputes = self._load_seed_file("_disputes.json")
        self._unanswered = self._load_seed_file("_unanswered.json")
    
    def suggest(self, topic: str = "", context: Dict = None,
                max_per_category: int = 3) -> Dict[str, Any]:
        """Generate structured read-next suggestions.
        
        Args:
            topic: Topic keyword (e.g. "biophilia", "stress")
            context: QA response context for relevance boosting
            max_per_category: Max suggestions per category
            
        Returns:
            Structured suggestions organized by category
        """
        # Find matching topic entries
        matched_topics = self._match_topics(topic)
        
        suggestions = {
            "by_theory": self._suggest_by_theory(matched_topics, max_per_category),
            "by_mechanism": self._suggest_by_mechanism(matched_topics, max_per_category),
            "by_molecule": self._suggest_by_molecule(matched_topics, max_per_category),
            "by_cultural": self._suggest_by_cultural(matched_topics, max_per_category),
            "challenges": self._suggest_challenges(matched_topics, max_per_category),
            "design_actions": self._suggest_design_actions(matched_topics, max_per_category),
            "frontier_questions": self._suggest_frontiers(matched_topics, max_per_category),
            "images": self._suggest_images(matched_topics, max_per_category),
        }
        
        # Add executable queries for each suggestion
        self._add_executable_queries(suggestions)
        
        return {
            "topic": topic,
            "total_suggestions": sum(len(v) for v in suggestions.values()),
            "categories": suggestions,
        }
    
    def enrich_qa_response(self, response: Dict, question: str) -> Dict:
        """Add read-next suggestions and images to a QA response.
        
        Mutates the response dict in-place, adding:
        - read_next: structured suggestions
        - relevant_images: image references for the topic
        """
        # Extract topic from question
        topic = self._extract_topic(question)
        
        # Generate suggestions
        read_next = self.suggest(topic, context=response)
        response["read_next"] = read_next
        
        # Find relevant images
        images = self._find_relevant_images(topic)
        if images:
            response["relevant_images"] = images
        
        return response
    
    # ----- Theory / Mechanism / Molecule suggestions -----
    
    def _suggest_by_theory(self, matched: List[Dict], max_n: int) -> List[Dict]:
        """Suggest related theories to explore."""
        from src.services.knowledge_catalog import T1_THEORIES, T15_FRAMEWORKS
        
        # Collect theory IDs from matched topics
        theory_ids = set()
        for m in matched:
            theory_ids.update(m.get("theories", []))
        
        suggestions = []
        for t in T1_THEORIES:
            if t["id"] in theory_ids:
                suggestions.append({
                    "category": SuggestionCategory.DEEPEN,
                    "type": "theory",
                    "title": t["name"],
                    "subtitle": f"{t['authors']}, {t['year']}",
                    "summary": t["summary"][:120],
                    "level": t["level"],
                    "query": f"What is {t['name']}?",
                })
        
        # Also suggest related frameworks
        mol_ids = set()
        for m in matched:
            mol_ids.update(m.get("molecules", []))
        
        for fw in T15_FRAMEWORKS:
            if fw["molecule_id"] in mol_ids:
                suggestions.append({
                    "category": SuggestionCategory.BROADEN,
                    "type": "framework",
                    "title": fw["name"],
                    "summary": fw["summary"][:120],
                    "level": "T1.5",
                    "query": f"What is {fw['name']}?",
                })
        
        return suggestions[:max_n]
    
    def _suggest_by_mechanism(self, matched: List[Dict], max_n: int) -> List[Dict]:
        """Suggest mechanism explorations."""
        mechanisms = []
        for m in matched:
            for mech in m.get("mechanisms", []):
                mechanisms.append({
                    "category": SuggestionCategory.DEEPEN,
                    "type": "mechanism",
                    "title": mech.replace("_", " ").title(),
                    "query": f"How does {mech.replace('_', ' ')} work?",
                })
        
        # Deduplicate
        seen = set()
        unique = []
        for m in mechanisms:
            if m["title"] not in seen:
                seen.add(m["title"])
                unique.append(m)
        
        return unique[:max_n]
    
    def _suggest_by_molecule(self, matched: List[Dict], max_n: int) -> List[Dict]:
        """Suggest relevant T2 molecules."""
        mol_ids = set()
        for m in matched:
            mol_ids.update(m.get("molecules", []))
        
        suggestions = []
        for mol_id in mol_ids:
            if mol_id in self._molecules:
                mol = self._molecules[mol_id]
                name = mol.get("name", mol.get("title", mol_id))
                suggestions.append({
                    "category": SuggestionCategory.DEEPEN,
                    "type": "molecule",
                    "title": name,
                    "mol_id": mol_id,
                    "summary": mol.get("summary", mol.get("description", ""))[:120],
                    "level": "T2",
                    "query": f"What is {name}?",
                })
        
        return suggestions[:max_n]
    
    def _suggest_by_cultural(self, matched: List[Dict], max_n: int) -> List[Dict]:
        """Suggest cultural perspective explorations."""
        dims = set()
        for m in matched:
            dims.update(m.get("cultural_dims", []))
        
        suggestions = []
        for dim in dims:
            suggestions.append({
                "category": SuggestionCategory.BROADEN,
                "type": "cultural",
                "title": f"Cultural Lens: {dim}",
                "query": f"How do cultural differences affect {dim.lower()}?",
            })
        
        return suggestions[:max_n]
    
    def _suggest_challenges(self, matched: List[Dict], max_n: int) -> List[Dict]:
        """Suggest disputes and counterevidence."""
        suggestions = []
        
        # Match disputes to topics
        for d in self._disputes:
            keywords = d.get("keywords", [])
            for m in matched:
                for mech in m.get("mechanisms", []) + m.get("theories", []):
                    if any(kw in mech.lower() for kw in keywords):
                        suggestions.append({
                            "category": SuggestionCategory.CHALLENGE,
                            "type": "dispute",
                            "title": d["claim"],
                            "status": d.get("status", "active"),
                            "query": f"Is {d['claim'].lower()} controversial?",
                        })
                        break
        
        # Add surprise suggestions
        if matched:
            topic = matched[0].get("_key", "this topic")
            suggestions.append({
                "category": SuggestionCategory.CHALLENGE,
                "type": "surprise",
                "title": f"Surprising findings about {topic}",
                "query": f"What's surprising about {topic}?",
            })
        
        return suggestions[:max_n]
    
    def _suggest_design_actions(self, matched: List[Dict], max_n: int) -> List[Dict]:
        """Suggest actionable design explorations."""
        suggestions = []
        topic_keys = [m.get("_key", "") for m in matched]
        
        design_questions = {
            "light": "What lighting parameters should I use?",
            "biophil": "How do I incorporate biophilic design?",
            "prospect": "How do I balance prospect and refuge in a space?",
            "complex": "What's the right level of visual complexity?",
            "social": "How do I design for both collaboration and privacy?",
            "wayfind": "How do I improve wayfinding in my building?",
            "stress": "How do I design a stress-reducing environment?",
            "awe": "How do I create an awe-inspiring space?",
        }
        
        for key in topic_keys:
            if key in design_questions:
                suggestions.append({
                    "category": SuggestionCategory.APPLY,
                    "type": "design",
                    "title": design_questions[key],
                    "query": design_questions[key],
                })
        
        if not suggestions:
            suggestions.append({
                "category": SuggestionCategory.APPLY,
                "type": "design",
                "title": "What design parameters are available?",
                "query": "What specific design parameters exist?",
            })
        
        return suggestions[:max_n]
    
    def _suggest_frontiers(self, matched: List[Dict], max_n: int) -> List[Dict]:
        """Suggest frontier/unanswered questions."""
        suggestions = []
        
        theory_ids = set()
        for m in matched:
            theory_ids.update(m.get("theories", []))
        
        for q in self._unanswered:
            related = q.get("related_theories", [])
            if any(t in theory_ids for t in related):
                suggestions.append({
                    "category": SuggestionCategory.FRONTIER,
                    "type": "unanswered",
                    "title": q["question"][:100],
                    "difficulty": q.get("estimated_difficulty", "?"),
                    "query": f"What don't we know about {q.get('domain', 'this topic')}?",
                })
        
        return suggestions[:max_n]
    
    def _suggest_images(self, matched: List[Dict], max_n: int) -> List[Dict]:
        """Suggest image queries that illustrate the topic."""
        suggestions = []
        for m in matched:
            for query in m.get("image_queries", [])[:2]:
                suggestions.append({
                    "category": SuggestionCategory.VISUALIZE,
                    "type": "image_search",
                    "title": f"See examples: {query}",
                    "image_query": query,
                })
        return suggestions[:max_n]
    
    # ----- Image Finding -----
    
    def _find_relevant_images(self, topic: str) -> List[Dict]:
        """Find relevant images from extraction reports and image pool."""
        images = []
        
        # Search extraction manifests for related images
        for manifest in IMAGE_REPORTS_DIR.glob("extraction_manifest_*.json"):
            try:
                with open(manifest) as f:
                    data = json.load(f)
                for img in data.get("extractions", []):
                    caption = img.get("caption", "").lower()
                    classification = img.get("classification", "").lower()
                    
                    if topic.lower() in caption or topic.lower() in classification:
                        images.append({
                            "source": "extracted",
                            "source_file": img.get("source_pdf", ""),
                            "page": img.get("page_number", 0),
                            "caption": img.get("caption", "")[:150],
                            "classification": classification,
                            "image_path": img.get("output_path", ""),
                            "relevance": "direct_match",
                        })
            except Exception as e:
                logger.debug(f"Skipped: {e}")
                continue
        
        # Search environment image DB
        try:
            from src.services.environment_image_db import EnvironmentImageDB
            env_db = EnvironmentImageDB()
            constraint_map = {
                "biophil": "biophilia", "prospect": "prospect_refuge",
                "complex": "complexity", "light": "lighting",
                "social": "social", "wayfind": "wayfinding",
            }
            for key, constraint in constraint_map.items():
                if key in topic.lower():
                    results = env_db.search_by_constraints([constraint], limit=3)
                    for r in results:
                        images.append({
                            "source": "environment_db",
                            "caption": r.get("caption", "")[:150],
                            "constraint_tags": r.get("constraint_tags", []),
                            "image_path": r.get("image_path", ""),
                            "relevance": "constraint_match",
                        })
                    break
        except Exception as e:
            logger.debug(f"Non-critical: {e}")
        
        return images[:5]  # Cap at 5 most relevant
    
    # ----- Helpers -----
    
    def _match_topics(self, topic: str) -> List[Dict]:
        """Find all matching topic entries."""
        if not topic:
            return list(TOPIC_MAP.values())[:3]
        
        matched = []
        t_lower = topic.lower()
        for key, entry in TOPIC_MAP.items():
            if key in t_lower or t_lower in key:
                entry_copy = dict(entry)
                entry_copy["_key"] = key
                matched.append(entry_copy)
        
        if not matched:
            # Fuzzy: check theory names
            for key, entry in TOPIC_MAP.items():
                for theory in entry.get("theories", []):
                    if t_lower in theory.lower():
                        entry_copy = dict(entry)
                        entry_copy["_key"] = key
                        matched.append(entry_copy)
                        break
        
        return matched or [{"_key": topic, "theories": [], "molecules": [],
                           "mechanisms": [], "cultural_dims": [], "image_queries": []}]
    
    def _extract_topic(self, question: str) -> str:
        """Extract the main topic from a question."""
        # Remove question words
        q = re.sub(r'^(?:what|how|why|show|list|tell|is|are|do|does|can)\s+', '', 
                   question.lower())
        q = re.sub(r'\b(?:the|a|an|all|me|about|in|this|system|does?|is|it)\b', '', q)
        q = re.sub(r'\s+', ' ', q).strip('? ')
        
        # Try to match known topic keywords
        for key in TOPIC_MAP:
            if key in q:
                return key
        
        # Return cleaned query
        return q[:30] if q else "general"
    
    def _add_executable_queries(self, suggestions: Dict) -> None:
        """Add executable_query field for one-click follow-up."""
        for category, items in suggestions.items():
            for item in items:
                if "query" not in item:
                    item["query"] = item.get("title", "Tell me more")
    
    def _load_molecules(self) -> Dict[str, dict]:
        molecules = {}
        for mp in MOLECULES_DIR.glob("*.json"):
            try:
                with open(mp) as f:
                    molecules[mp.stem] = json.load(f)
            except Exception as e:
                logger.debug(f"Non-critical: {e}")
        return molecules
    
    def _load_seed_file(self, name: str) -> List[Dict]:
        path = EXT_ANN_DIR / name
        if path.exists():
            with open(path) as f:
                return json.load(f)
        return []
