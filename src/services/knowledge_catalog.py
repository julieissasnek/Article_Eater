"""
Knowledge Catalog — Browsable Index of All Theoretical Knowledge
=================================================================

Generates structured catalogs of:
  - T1 Theories (Kaplan ART, Ulrich SRT, Wilson Biophilia, etc.)
  - T1.5 Frameworks (prospect-refuge, cognitive load, etc.)
  - T2 Molecules (M_BEAUTY_COMPRESSION, M_RASA, etc.)
  - Cultural Variants (Western, East Asian, Islamic, Scandinavian)
  - Measurement Modalities across the corpus
  - CVA Constraint/Valuation dimensions

These catalogs power "show me all theories" type QA queries.

Usage:
    from src.services.knowledge_catalog import KnowledgeCatalog
    catalog = KnowledgeCatalog()
    theories = catalog.get_theories()
    cultural = catalog.get_cultural_differences()
    everything = catalog.full_catalog()
"""

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from collections import Counter, defaultdict

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent
MOLECULES_DIR = PROJECT_ROOT / "data" / "molecules"
TEMPLATES_DIR = PROJECT_ROOT / "data" / "templates"
EXTRACTIONS_DIR = PROJECT_ROOT / "data" / "extractions"
THEORY_LINKS_PATH = PROJECT_ROOT / "data" / "production" / "finding_template_theory_links.json"
OUTCOME_VOCAB_PATH = PROJECT_ROOT / "contracts" / "outcome_vocab" / "outcome_vocab.json"


# =============================================================================
# T1 Theory Definitions (curated)
# =============================================================================

T1_THEORIES = [
    {
        "id": "ART",
        "name": "Attention Restoration Theory",
        "authors": "Rachel & Stephen Kaplan",
        "year": 1989,
        "level": "T1",
        "summary": "Exposure to natural environments restores directed attention via fascination (involuntary attention), which gives the directed attention system a chance to recover.",
        "key_constructs": ["fascination", "being_away", "extent", "compatibility"],
        "cva_constraints": ["processing_cost", "load_rate"],
        "molecule_id": "art",
        "outcome_domains": ["cog", "affect", "health"],
    },
    {
        "id": "SRT",
        "name": "Stress Recovery Theory",
        "authors": "Roger Ulrich",
        "year": 1983,
        "level": "T1",
        "summary": "Natural environments promote stress recovery through positive affective responses triggered by unthreatening visual features (moderate complexity, spatial openness, presence of water/vegetation).",
        "key_constructs": ["stress_recovery", "affective_response", "approach_behavior"],
        "cva_constraints": ["prediction_error", "control_efficacy"],
        "molecule_id": "srt",
        "outcome_domains": ["affect", "physio", "health"],
    },
    {
        "id": "BIOPHILIA",
        "name": "Biophilia Hypothesis",
        "authors": "Edward O. Wilson, Stephen Kellert",
        "year": 1984,
        "level": "T1",
        "summary": "Humans have an innate tendency to seek connections with nature and other forms of life, shaped by evolutionary history.",
        "key_constructs": ["nature_affiliation", "biophilic_elements", "evolutionary_preference"],
        "cva_constraints": ["prediction_error", "social_signal"],
        "molecule_id": "biophilia",
        "outcome_domains": ["affect", "health", "cog"],
    },
    {
        "id": "PROSPECT_REFUGE",
        "name": "Prospect-Refuge Theory",
        "authors": "Jay Appleton",
        "year": 1975,
        "level": "T1",
        "summary": "Humans prefer environments offering both prospect (open views allowing surveillance) and refuge (enclosed spaces offering protection), reflecting evolutionary habitat selection.",
        "key_constructs": ["prospect", "refuge", "hazard", "control"],
        "cva_constraints": ["control_efficacy", "prediction_error"],
        "molecule_id": "prospect_refuge",
        "outcome_domains": ["affect", "behav"],
    },
    {
        "id": "KAPLAN_PREFERENCE",
        "name": "Kaplan Preference Matrix",
        "authors": "Stephen & Rachel Kaplan",
        "year": 1989,
        "level": "T1",
        "summary": "Environmental preference depends on four informational factors: complexity (immediate), coherence (immediate), mystery (inferred), and legibility (inferred).",
        "key_constructs": ["complexity", "coherence", "mystery", "legibility"],
        "cva_constraints": ["prediction_error", "processing_cost"],
        "molecule_id": None,
        "outcome_domains": ["affect", "cog"],
    },
    {
        "id": "COGNITIVE_LOAD",
        "name": "Cognitive Load Theory in Architecture",
        "authors": "Sweller (adapted by env psych)",
        "year": 1988,
        "level": "T1",
        "summary": "Environmental complexity imposes cognitive load; optimal design reduces extraneous load (wayfinding confusion, visual clutter) while maintaining germane load (meaningful spatial information).",
        "key_constructs": ["intrinsic_load", "extraneous_load", "germane_load"],
        "cva_constraints": ["processing_cost", "load_rate", "salience_competition"],
        "molecule_id": "cognitive_load_architecture",
        "outcome_domains": ["cog", "behav"],
    },
]

# =============================================================================
# T1.5 Frameworks
# =============================================================================

T15_FRAMEWORKS = [
    {"id": "ALLOSTATIC", "name": "Allostatic Regulation", "molecule_id": "allostatic_regulation",
     "summary": "Environment modulates allostatic load through cumulative physiological demands."},
    {"id": "AWE_ARCH", "name": "Architectural Awe", "molecule_id": "awe_architecture",
     "summary": "Vast, powerful architectural features induce awe, reframing self-concept."},
    {"id": "CIRCADIAN", "name": "Circadian Architecture", "molecule_id": "circadian_architecture",
     "summary": "Lighting design supports circadian rhythms through spectral and temporal properties."},
    {"id": "CREATIVE_ENV", "name": "Creative Environments", "molecule_id": "creative_environments",
     "summary": "Environmental features (moderate complexity, nature, autonomy) facilitate creative cognition."},
    {"id": "GOLDILOCKS", "name": "Goldilocks Principle", "molecule_id": "goldilocks_principle",
     "summary": "Optimal stimulation exists at intermediate levels across multiple modalities."},
    {"id": "MULTISENSORY", "name": "Multisensory Design", "molecule_id": "multisensory_design",
     "summary": "Cross-modal sensory interactions shape spatial experience beyond any single modality."},
    {"id": "SOCIAL_ARCH", "name": "Social Architecture", "molecule_id": "social_architecture",
     "summary": "Spatial configuration shapes social interaction patterns, privacy, and community."},
    {"id": "WAYFINDING", "name": "Spatial Navigation & Cognitive Mapping", "molecule_id": "wayfinding",
     "summary": "Environmental legibility enables cognitive map formation and wayfinding success."},
]

# =============================================================================
# Cultural Difference Catalog
# =============================================================================

CULTURAL_DIFFERENCES = [
    {
        "dimension": "Beauty & Aesthetic Judgment",
        "variants": [
            {"culture": "Western (individualist)", "pattern": "Peak shift, symmetry, golden ratio emphasis; beauty as individual emotional response"},
            {"culture": "East Asian (collectivist)", "pattern": "Wabi-sabi, imperfection, asymmetry valued; beauty as harmony with nature and context"},
            {"culture": "Islamic", "pattern": "Geometric complexity, infinite patterns, aniconism; beauty as reflection of divine order"},
            {"culture": "Scandinavian", "pattern": "Minimalist order, funktionalism, nature integration; beauty as simplicity and purpose"},
        ],
        "cva_impact": "ValuationVector weights differ by up to 0.4 across cultural presets",
    },
    {
        "dimension": "Prospect-Refuge Preferences",
        "variants": [
            {"culture": "Western", "pattern": "Strong prospect preference; open plans, panoramic windows"},
            {"culture": "Japanese", "pattern": "Enclosure comfort (engawa, shoji screens); refuge weighted higher"},
            {"culture": "Mediterranean", "pattern": "Courtyard model — enclosed prospect; inward-facing openness"},
        ],
        "cva_impact": "control_efficacy and prediction_error weights shift with cultural enclosure norms",
    },
    {
        "dimension": "Nature Connection",
        "variants": [
            {"culture": "Western", "pattern": "Biophilia through views and potted plants; nature as decoration"},
            {"culture": "Japanese", "pattern": "Borrowed scenery (shakkei), garden integration, seasonal awareness"},
            {"culture": "Chinese", "pattern": "Feng shui principles; qi flow; water and mountain balance"},
            {"culture": "Nordic", "pattern": "Friluftsliv (outdoor living); direct nature immersion prioritized over visual"},
        ],
        "cva_impact": "green_view_index interpretation varies; not all cultures respond to the same 'nature signals'",
    },
    {
        "dimension": "Social Space & Privacy",
        "variants": [
            {"culture": "Western individualist", "pattern": "Private offices, personal space buffers, introvert accommodation"},
            {"culture": "East Asian collectivist", "pattern": "Shared spaces, lower privacy expectations, group harmony over individual comfort"},
            {"culture": "Middle Eastern", "pattern": "Gender-segregated spaces, family-oriented design, hospitality architecture"},
        ],
        "cva_impact": "social_signal constraint interpretation depends on cultural norms around proximity",
    },
    {
        "dimension": "Color Meaning & Preference",
        "variants": [
            {"culture": "Western", "pattern": "Blue = calm, Red = danger/passion; white = purity"},
            {"culture": "Chinese", "pattern": "Red = luck/prosperity; white = mourning; yellow = royalty"},
            {"culture": "Islamic", "pattern": "Green = sacred; geometric patterns in color carry spiritual meaning"},
            {"culture": "Japanese", "pattern": "Natural materials preferred; subdued palettes; seasonal color awareness"},
        ],
        "cva_impact": "Color-based valuation tags must be culturally qualified or risk systematic bias",
    },
    {
        "dimension": "Temporal & Circadian Patterns",
        "variants": [
            {"culture": "Northern Europe", "pattern": "Seasonal affective responses; summer/winter lighting critical"},
            {"culture": "Equatorial", "pattern": "Consistent day/night cycles; shade and ventilation prioritized"},
            {"culture": "Mediterranean", "pattern": "Siesta culture; midday refuge; evening social spaces"},
        ],
        "cva_impact": "circadian_architecture constraints vary by latitude and cultural activity patterns",
    },
]


class KnowledgeCatalog:
    """Browsable index of all theoretical knowledge in the system."""
    
    def __init__(self):
        self._molecules = self._load_molecules()
        self._theory_links = self._load_theory_links()
        self._outcome_vocab = self._load_outcome_vocab()
    
    # ----- Public API -----
    
    def get_theories(self) -> List[Dict]:
        """Get all T1 theories with evidence counts."""
        theories = []
        for t in T1_THEORIES:
            evidence = self._count_evidence_for(t["id"])
            entry = {**t, "evidence_count": evidence}
            # Add molecule details if available
            if t.get("molecule_id") and t["molecule_id"] in self._molecules:
                mol = self._molecules[t["molecule_id"]]
                entry["molecule_summary"] = mol.get("summary", mol.get("description", ""))[:200]
            theories.append(entry)
        return theories
    
    def get_frameworks(self) -> List[Dict]:
        """Get all T1.5 frameworks."""
        frameworks = []
        for fw in T15_FRAMEWORKS:
            entry = dict(fw)
            if fw["molecule_id"] in self._molecules:
                mol = self._molecules[fw["molecule_id"]]
                entry["full_summary"] = mol.get("summary", mol.get("description", ""))[:300]
                entry["key_predictions"] = mol.get("key_predictions", mol.get("predictions", []))[:5]
            frameworks.append(entry)
        return frameworks
    
    def get_molecules(self) -> List[Dict]:
        """Get all T2 molecules with metadata."""
        molecules = []
        for mol_id, mol_data in sorted(self._molecules.items()):
            molecules.append({
                "id": mol_id,
                "name": mol_data.get("name", mol_data.get("title", mol_id)),
                "summary": mol_data.get("summary", mol_data.get("description", ""))[:200],
                "key_predictions": mol_data.get("key_predictions", mol_data.get("predictions", []))[:3],
                "constraints_modeled": mol_data.get("constraints_modeled", []),
                "source_theory": mol_data.get("source_theory", ""),
            })
        return molecules
    
    def get_cultural_differences(self) -> List[Dict]:
        """Get all recognized cultural differences."""
        # Enrich with evidence counts from extractions
        enriched = []
        for cd in CULTURAL_DIFFERENCES:
            entry = dict(cd)
            entry["evidence_files"] = self._count_cultural_evidence(cd["dimension"])
            enriched.append(entry)
        return enriched
    
    def get_outcome_domains(self) -> Dict[str, Any]:
        """Get outcome taxonomy overview."""
        if not self._outcome_vocab:
            return {}
        
        domains = defaultdict(list)
        for term in self._outcome_vocab.get("terms", []):
            domains[term["domain"]].append({
                "id": term["term_id"],
                "name": term["name"],
            })
        
        return {
            "total_terms": len(self._outcome_vocab.get("terms", [])),
            "domains": {d: {"count": len(ts), "sample": [t["name"] for t in ts[:5]]} 
                       for d, ts in sorted(domains.items())},
        }
    
    def get_measurement_modalities(self) -> List[Dict]:
        """Get recognized measurement modalities."""
        from src.models.cva_annotations import MeasurementModality
        return [
            {"id": m.value, "name": m.name.replace("_", " ").title()}
            for m in MeasurementModality
        ]
    
    def get_cva_dimensions(self) -> Dict[str, List[str]]:
        """Get CVA constraint and valuation dimensions."""
        return {
            "constraints": [
                "C_SAFETY — Environmental safety/threat signals",
                "C_BIOPHILIA — Nature/biophilic element presence",
                "C_COMPLEXITY — Visual complexity/information density",
                "C_PROSPECT_REFUGE — Spatial openness vs. enclosure balance",
                "C_COHERENCE — Visual order/organization",
                "C_LEGIBILITY — Wayfinding clarity/spatial readability",
                "C_MYSTERY — Curiosity/exploration invitation",
                "C_FASCINATION — Effortless attention engagement",
            ],
            "valuations": [
                "V_SAFETY — Perceived security and protection value",
                "V_BEAUTY — Aesthetic pleasure and attraction value",
                "V_COMFORT — Physical and psychological ease value",
                "V_MEANING — Significance, symbolism, and identity value",
                "V_SOCIAL — Community, belonging, and social value",
                "V_FUNCTION — Efficiency, productivity, and utility value",
                "V_NOVELTY — Surprise, discovery, and creativity value",
                "V_NATURE — Nature connection and biophilic value",
            ],
        }
    
    def full_catalog(self) -> Dict[str, Any]:
        """Get complete knowledge catalog."""
        return {
            "theories_T1": self.get_theories(),
            "frameworks_T15": self.get_frameworks(),
            "molecules_T2": self.get_molecules(),
            "cultural_differences": self.get_cultural_differences(),
            "outcome_domains": self.get_outcome_domains(),
            "measurement_modalities": self.get_measurement_modalities(),
            "cva_dimensions": self.get_cva_dimensions(),
        }
    
    def search(self, query: str) -> Dict[str, Any]:
        """Search across all catalogs."""
        q = query.lower()
        results = {"theories": [], "frameworks": [], "molecules": [], 
                   "cultural": [], "outcomes": []}
        
        for t in T1_THEORIES:
            if q in t["name"].lower() or q in t["summary"].lower() or q in t["id"].lower():
                results["theories"].append(t)
        
        for fw in T15_FRAMEWORKS:
            if q in fw["name"].lower() or q in fw["summary"].lower():
                results["frameworks"].append(fw)
        
        for mol_id, mol in self._molecules.items():
            name = mol.get("name", mol.get("title", mol_id)).lower()
            summary = mol.get("summary", mol.get("description", "")).lower()
            if q in name or q in summary:
                results["molecules"].append({"id": mol_id, "name": name})
        
        for cd in CULTURAL_DIFFERENCES:
            if q in cd["dimension"].lower() or any(q in v["pattern"].lower() for v in cd["variants"]):
                results["cultural"].append(cd)
        
        return results
    
    # ----- Private helpers -----
    
    def _load_molecules(self) -> Dict[str, dict]:
        molecules = {}
        for mp in MOLECULES_DIR.glob("*.json"):
            try:
                with open(mp) as f:
                    molecules[mp.stem] = json.load(f)
            except Exception:
                pass
        return molecules
    
    def _load_theory_links(self) -> Dict:
        if THEORY_LINKS_PATH.exists():
            with open(THEORY_LINKS_PATH) as f:
                return json.load(f)
        return {}
    
    def _load_outcome_vocab(self) -> Dict:
        if OUTCOME_VOCAB_PATH.exists():
            with open(OUTCOME_VOCAB_PATH) as f:
                return json.load(f)
        return {}
    
    def _count_evidence_for(self, theory_id: str) -> int:
        """Count how many beliefs link to this theory."""
        resolutions = self._theory_links.get("resolutions", [])
        if not isinstance(resolutions, list):
            return 0
        # Theory links use template relevance scores
        count = 0
        theory_lower = theory_id.lower()
        for r in resolutions:
            templates = r.get("top_templates", [])
            for t in templates:
                if theory_lower in t.get("template_id", "").lower():
                    count += 1
                    break
        return count
    
    def _count_cultural_evidence(self, dimension: str) -> int:
        """Count extraction files with cultural evidence for this dimension."""
        keywords = {
            "Beauty": ["beauty", "aesthetic", "preference"],
            "Prospect": ["prospect", "refuge", "enclosure", "open"],
            "Nature": ["nature", "biophil", "green", "vegetation"],
            "Social": ["social", "privacy", "crowding"],
            "Color": ["color", "colour", "palette"],
            "Temporal": ["circadian", "seasonal", "lighting"],
        }
        kws = []
        for key, words in keywords.items():
            if key.lower() in dimension.lower():
                kws = words
                break
        if not kws:
            return 0
        
        count = 0
        for ef in EXTRACTIONS_DIR.glob("*.json"):
            try:
                with open(ef) as f:
                    text = f.read()[:2000].lower()
                if "cultur" in text and any(kw in text for kw in kws):
                    count += 1
            except Exception:
                pass
        return count
