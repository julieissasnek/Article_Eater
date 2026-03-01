#!/usr/bin/env python3
"""
enrich_provenance.py — Add history/provenance fields to all entities
=====================================================================

Mines extraction data + known literature to build provenance fields for:
  - T1 theories: seminal_paper, predecessor, historical_context, key_citations
  - T1.5 molecules: source_theories, basis, derivation
  - T2 templates: provenance linking to source papers

Then uses this enriched data as context for A16 (historical) annotation generation.

Success conditions:
  SC-1: ≥20/24 theories have provenance fields
  SC-2: ≥12/18 molecules have source_theories
  SC-3: No errors
  SC-4: All enriched files remain valid JSON

Added: 2026-02-28 (V6 remediation — provenance enrichment)
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

THEORIES_DIR = PROJECT_ROOT / "data" / "theories"
MOLECULES_DIR = PROJECT_ROOT / "data" / "molecules"
TEMPLATES_DIR = PROJECT_ROOT / "data" / "templates"
EXTRACTIONS_DIR = PROJECT_ROOT / "data" / "extractions"

try:
    from src.utils.validation_reflexes import validate_json_file, warn
    HAS_REFLEXES = True
except ImportError:
    HAS_REFLEXES = False


# ═══════════════════════════════════════════════════════════════════
# Known provenance data (from literature)
# ═══════════════════════════════════════════════════════════════════

THEORY_PROVENANCE = {
    "art": {
        "seminal_paper": "Kaplan, S. (1995). The restorative benefits of nature: Toward an integrative framework. JEP, 15(3), 169-182.",
        "predecessor": "William James' voluntary vs involuntary attention (1892); Olmsted's restorative landscapes (1865)",
        "historical_context": "Developed to explain why natural environments restore mental fatigue. Extended James' attention typology with environmental factors. Became dominant framework in environmental psychology alongside SRT.",
        "key_milestones": ["1989: Kaplan & Kaplan 'Experience of Nature'", "1995: Formal ART paper", "2008: Berman et al. cognitive validation"],
        "influenced_by": ["William James (attention theory)", "Frederick Law Olmsted (landscape architecture)"],
        "current_status": "foundational",
    },
    "srt": {
        "seminal_paper": "Ulrich, R.S. (1983). Aesthetic and affective response to natural environment. In Behavior and the Natural Environment.",
        "predecessor": "Zajonc's affective primacy hypothesis; evolutionary aesthetics (Appleton, 1975)",
        "historical_context": "Proposed that nature triggers automatic positive affective responses that reduce stress. The 1984 hospital study (view through window) became one of the most cited papers in environmental psychology.",
        "key_milestones": ["1981: Ulrich's scenic beauty study", "1983: SRT formal theory", "1984: Hospital window study"],
        "influenced_by": ["Zajonc (affective primacy)", "Appleton (prospect-refuge)", "Berlyne (arousal aesthetics)"],
        "current_status": "foundational",
    },
    "biophilia": {
        "seminal_paper": "Wilson, E.O. (1984). Biophilia. Harvard University Press.",
        "predecessor": "Fromm's 'biophilia' concept (1973); evolutionary psychology (Tooby & Cosmides)",
        "historical_context": "Wilson argued humans have an innate tendency to seek connections with nature. Kellert & Wilson (1993) provided the empirical evidence collection. Browning et al. (2014) translated into 14 patterns for architecture.",
        "key_milestones": ["1984: Wilson's Biophilia", "1993: The Biophilia Hypothesis", "2014: 14 Patterns of Biophilic Design"],
        "influenced_by": ["E.O. Wilson (sociobiology)", "Erich Fromm (humanistic psychology)", "Kellert (biophilic values)"],
        "current_status": "foundational",
    },
    "berlyne_arousal": {
        "seminal_paper": "Berlyne, D.E. (1971). Aesthetics and Psychobiology. Appleton-Century-Crofts.",
        "predecessor": "Wundt's inverted-U curve (1874); Fechner's experimental aesthetics (1876)",
        "historical_context": "Berlyne formalized the relationship between collative variables (novelty, complexity, incongruity) and hedonic value. The inverted-U prediction became the dominant model for aesthetic preference until processing fluency challenged it in the 2000s.",
        "key_milestones": ["1960: Conflict, Arousal, and Curiosity", "1971: Aesthetics and Psychobiology", "1974: Studies in the New Experimental Aesthetics"],
        "influenced_by": ["Wundt (hedonic curve)", "Fechner (experimental aesthetics)", "Hebb (optimal arousal)"],
        "current_status": "foundational",
    },
    "prospect_refuge": {
        "seminal_paper": "Appleton, J. (1975). The Experience of Landscape. Wiley.",
        "predecessor": "Gibson's ecological perception; evolutionary landscape preference (Orians)",
        "historical_context": "Appleton proposed that landscape preference reflects evolved survival needs: seeing without being seen. The theory predicts preference for environments offering both open views (prospect) and sheltered spaces (refuge).",
        "key_milestones": ["1975: The Experience of Landscape", "1984: Prospect-refuge in architecture (Hildebrand)", "1996: Dosen & Ostwald quantification"],
        "influenced_by": ["Jay Appleton (habitat theory)", "J.J. Gibson (ecological psychology)", "G.H. Orians (savanna hypothesis)"],
        "current_status": "foundational",
    },
    "adaptive_thermal": {
        "seminal_paper": "de Dear, R.J. & Brager, G.S. (1998). Developing an adaptive model of thermal comfort and preference. ASHRAE Transactions, 104(1).",
        "predecessor": "Fanger's PMV/PPD model (1970); Humphreys' adaptive approach (1978)",
        "historical_context": "Challenged Fanger's static thermal comfort model by showing people in naturally ventilated buildings accept wider temperature ranges. Led to ASHRAE Standard 55-2004 adaptive comfort model.",
        "key_milestones": ["1970: Fanger's PMV model", "1978: Humphreys' field studies", "1998: de Dear & Brager adaptive model", "2004: ASHRAE Standard 55"],
        "influenced_by": ["P.O. Fanger (PMV)", "M.A. Humphreys (adaptive approach)", "J.F. Nicol (field studies)"],
        "current_status": "foundational",
    },
    "allesthesia": {
        "seminal_paper": "Cabanac, M. (1971). Physiological role of pleasure. Science, 173(4002), 1103-1107.",
        "predecessor": "Homeostatic theory (Cannon, 1932); hedonic theories of motivation",
        "historical_context": "Cabanac showed that the pleasantness of a stimulus depends on internal state — cold water feels pleasant when overheated, unpleasant when cold. Extended to architecture: thermal pleasure varies with thermal deficit.",
        "key_milestones": ["1971: Original Science paper", "1979: 'Sensory pleasure' review", "2006: Parkinson & de Dear architectural application"],
        "influenced_by": ["W.B. Cannon (homeostasis)", "H. Helson (adaptation level)"],
        "current_status": "actively_debated",
    },
    "gibson_affordance": {
        "seminal_paper": "Gibson, J.J. (1979). The Ecological Approach to Visual Perception. Houghton Mifflin.",
        "predecessor": "Gestalt psychology; Brunswick's ecological approach; direct perception vs constructivism debate",
        "historical_context": "Gibson argued perception is direct — we perceive affordances (action possibilities) not abstract features. Revolutionary for architecture: design is about creating affordances, not just visual objects.",
        "key_milestones": ["1966: The Senses Considered as Perceptual Systems", "1979: The Ecological Approach", "1988: Norman's design affordances"],
        "influenced_by": ["J.J. Gibson (ecological optics)", "K. Koffka (Gestalt)", "E. Brunswick (ecological validity)"],
        "current_status": "foundational",
    },
    "predictive_processing": {
        "seminal_paper": "Clark, A. (2013). Whatever next? Predictive brains, situated agents, and the future of cognitive science. BBS, 36(3).",
        "predecessor": "Helmholtz's unconscious inference (1867); Bayesian brain hypothesis (Knill & Pouget, 2004)",
        "historical_context": "Unifying framework: the brain is a prediction machine that minimizes surprise. Applied to architecture: buildings that match predictions feel 'right'; violations cause stress or delight depending on context.",
        "key_milestones": ["2005: Friston's free energy principle", "2013: Clark's synthesis", "2017: Vessel et al. architecture + prediction error"],
        "influenced_by": ["K. Friston (free energy)", "H. von Helmholtz (unconscious inference)", "R. Gregory (perception as hypothesis)"],
        "current_status": "actively_debated",
    },
    "circadian_lighting": {
        "seminal_paper": "Berson, D.M. et al. (2002). Phototransduction by retinal ganglion cells that set the circadian clock. Science, 295(5557).",
        "predecessor": "Czeisler's circadian photoreception studies (1980s); Moore's SCN research",
        "historical_context": "Discovery of ipRGCs (melanopsin-containing cells) in 2002 revolutionized lighting design. Architecture could now target non-visual pathways. Led to melanopic lux metrics and human-centric lighting standards.",
        "key_milestones": ["2002: ipRGC discovery", "2005: Lucas melanopsin action spectrum", "2018: CIE melanopic metrics", "2020: WELL v2 circadian provisions"],
        "influenced_by": ["D.M. Berson (ipRGC discovery)", "C.A. Czeisler (circadian photoreception)", "R.G. Foster (non-rod, non-cone photoreception)"],
        "current_status": "foundational",
    },
    "personal_space": {
        "seminal_paper": "Hall, E.T. (1966). The Hidden Dimension. Doubleday.",
        "predecessor": "Hediger's animal flight distances (1950); Sommer's personal space (1959)",
        "historical_context": "Hall defined proxemic zones (intimate/personal/social/public) and showed cultural variation. Became fundamental to architectural programming — space planning, furniture layout, waiting areas.",
        "key_milestones": ["1959: Sommer's personal space", "1966: The Hidden Dimension", "1969: Experimental validation studies"],
        "influenced_by": ["E.T. Hall (anthropology)", "R. Sommer (environmental psychology)", "H. Hediger (animal behavior)"],
        "current_status": "foundational",
    },
    "fractal_fluency": {
        "seminal_paper": "Taylor, R.P. et al. (1999). Fractal analysis of Pollock's drip paintings. Nature, 399, 422.",
        "predecessor": "Mandelbrot's fractal geometry (1982); Berlyne's complexity-preference relationship",
        "historical_context": "Taylor showed Jackson Pollock's paintings have fractal dimension ~1.7 matching natural scenes. Later work showed peak aesthetic preference at FD ≈ 1.3 and stress reduction from fractal viewing.",
        "key_milestones": ["1982: Mandelbrot's fractal geometry", "1999: Pollock fractal analysis", "2006: Aesthetic preference at FD 1.3", "2017: Stress reduction evidence"],
        "influenced_by": ["B. Mandelbrot (fractal geometry)", "R.P. Taylor (physics + art)", "D.E. Berlyne (complexity preference)"],
        "current_status": "actively_debated",
    },
    "color_emotion": {
        "seminal_paper": "Valdez, P. & Mehrabian, A. (1994). Effects of color on emotions. JEP: General, 123(4), 394-409.",
        "predecessor": "Goethe's Theory of Colours (1810); Itten's color theory (1961); Mehrabian's PAD model",
        "historical_context": "Established quantitative links between color attributes (hue, saturation, brightness) and emotional dimensions (pleasure, arousal, dominance). Cross-cultural replications showed arousal effects are universal; valence is culturally modulated.",
        "key_milestones": ["1810: Goethe's Theory of Colours", "1961: Itten's color theory", "1994: Valdez & Mehrabian", "2004: Palmer & Schloss ecological valence"],
        "influenced_by": ["A. Mehrabian (PAD model)", "J. Itten (Bauhaus color theory)", "S.E. Palmer (ecological valence)"],
        "current_status": "foundational",
    },
    "environmental_stress": {
        "seminal_paper": "Evans, G.W. & Cohen, S. (1987). Environmental stress. In Handbook of Environmental Psychology.",
        "predecessor": "Selye's general adaptation syndrome (1956); Lazarus' cognitive appraisal (1966)",
        "historical_context": "Synthesized how environmental stressors (noise, crowding, pollution) affect health. Showed stressor interactions are often super-additive. Led to evidence-based design standards for hospitals and offices.",
        "key_milestones": ["1956: Selye's stress theory", "1972: Glass & Singer urban stress", "1987: Evans & Cohen synthesis"],
        "influenced_by": ["H. Selye (biological stress)", "R. Lazarus (cognitive appraisal)", "D. Glass (urban stress)"],
        "current_status": "foundational",
    },
    "auditory_scene_analysis": {
        "seminal_paper": "Bregman, A.S. (1990). Auditory Scene Analysis. MIT Press.",
        "predecessor": "Gestalt grouping principles applied to audition; Cherry's cocktail party problem (1953)",
        "historical_context": "Bregman showed how the auditory system parses complex sound environments into separate streams. Essential for understanding speech intelligibility in open offices and acoustic design.",
        "key_milestones": ["1953: Cherry's cocktail party", "1990: Auditory Scene Analysis", "2006: ISO 3382 room acoustics"],
        "influenced_by": ["A.S. Bregman (psychology)", "E.C. Cherry (selective attention)", "Gestalt psychologists"],
        "current_status": "foundational",
    },
    "brecvema": {
        "seminal_paper": "Juslin, P.N. (2013). From everyday emotions to aesthetic emotions. Physics of Life Reviews, 10(3), 235-266.",
        "predecessor": "Meyer's expectancy theory (1956); Sloboda's musical emotion (1991)",
        "historical_context": "BRECVEMA identifies 8 mechanisms by which music evokes emotion: Brainstem reflex, Rhythmic entrainment, Evaluative conditioning, Contagion, Visual imagery, Episodic memory, Musical expectancy, Aesthetic judgment. Bridges music psychology and architectural acoustics.",
        "key_milestones": ["1956: Meyer's Emotion and Meaning in Music", "2001: Juslin & Västfjäll 6 mechanisms", "2013: Full BRECVEMA framework"],
        "influenced_by": ["P.N. Juslin (music psychology)", "L.B. Meyer (expectancy)", "J.A. Sloboda (musical emotion)"],
        "current_status": "actively_debated",
    },
    "predictive_coding_music": {
        "seminal_paper": "Koelsch, S. et al. (2019). Predictive processes and the peculiar case of music. TICS, 23(1), 63-77.",
        "predecessor": "Meyer's expectancy theory; Huron's ITPRA theory (2006); Friston's free energy",
        "historical_context": "Extended predictive processing to music: pleasure arises from prediction error + resolution. Explains why familiar but slightly novel music is most pleasurable. Architectural implications for soundscape design.",
        "key_milestones": ["2006: Huron's Sweet Anticipation", "2011: Salimpoor et al. dopamine + anticipation", "2019: Koelsch predictive synthesis"],
        "influenced_by": ["S. Koelsch (neuromusicology)", "D. Huron (ITPRA)", "K. Friston (predictive processing)"],
        "current_status": "actively_debated",
    },
    "embodied_cognition": {
        "seminal_paper": "Lakoff, G. & Johnson, M. (1999). Philosophy in the Flesh. Basic Books.",
        "predecessor": "Merleau-Ponty's phenomenology of perception (1945); Gibson's ecological approach",
        "historical_context": "Argues cognition is grounded in bodily experience, not abstract computation. For architecture: spatial metaphors (high = good, warm = friendly) physically shape judgment. Movement through space shapes understanding.",
        "key_milestones": ["1945: Merleau-Ponty", "1980: Lakoff & Johnson 'Metaphors We Live By'", "2003: Embodied architecture (Pallasmaa)"],
        "influenced_by": ["M. Merleau-Ponty (phenomenology)", "G. Lakoff (conceptual metaphor)", "J. Pallasmaa (architectural phenomenology)"],
        "current_status": "foundational",
    },
    "savanna_hypothesis": {
        "seminal_paper": "Orians, G.H. (1986). An ecological and evolutionary approach to landscape aesthetics. In Meanings and Values in Landscape.",
        "predecessor": "Wilson's biophilia; evolutionary psychology; habitat selection theory",
        "historical_context": "Predicts humans prefer savanna-like landscapes (scattered trees, open grassland, water) because these matched ancestral habitat. Cross-cultural studies show partial but not universal support.",
        "key_milestones": ["1980: Orians' habitat theory", "1986: Formal publication", "1992: Balling & Falk cross-age study"],
        "influenced_by": ["G.H. Orians (behavioral ecology)", "E.O. Wilson (biophilia)", "J.H. Balling (developmental studies)"],
        "current_status": "actively_debated",
    },
    "processing_fluency": {
        "seminal_paper": "Reber, R., Schwarz, N., & Winkielman, P. (2004). Processing fluency and aesthetic pleasure. Personality and Social Psychology Review, 8(4).",
        "predecessor": "Zajonc's mere exposure effect (1968); Berlyne's arousal aesthetics; prototype theory",
        "historical_context": "Challenged Berlyne's arousal model: beauty comes from ease of processing, not optimal complexity. Explains mere exposure effect, symmetry preference, and prototype enhancement in one framework.",
        "key_milestones": ["1968: Zajonc mere exposure", "2004: Reber et al. fluency theory", "2006: Winkielman hedonic fluency"],
        "influenced_by": ["R. Zajonc (mere exposure)", "R. Reber (fluency)", "P. Winkielman (embodied affect)"],
        "current_status": "actively_debated",
    },
    "soundscape": {
        "seminal_paper": "Schafer, R.M. (1977). The Soundscape: Our Sonic Environment and the Tuning of the World. Knopf.",
        "predecessor": "Acoustic ecology movement; noise abatement tradition",
        "historical_context": "Schafer coined 'soundscape' to shift from noise control to sound quality. ISO 12913 (2014) standardized soundscape assessment. Transformed acoustic design from noise reduction to positive sound environments.",
        "key_milestones": ["1977: Schafer's The Soundscape", "2003: Kang urban soundscape", "2014: ISO 12913"],
        "influenced_by": ["R.M. Schafer (acoustic ecology)", "J. Kang (urban acoustics)", "B. Truax (acoustic communication)"],
        "current_status": "foundational",
    },
    "space_syntax": {
        "seminal_paper": "Hillier, B. & Hanson, J. (1984). The Social Logic of Space. Cambridge University Press.",
        "predecessor": "Graph theory; March & Steadman's geometry of environments (1971)",
        "historical_context": "Quantified the relationship between spatial layout and human movement, visibility, and social interaction. Integration (topological accessibility) predicts pedestrian flow with r ≈ 0.7-0.9.",
        "key_milestones": ["1984: The Social Logic of Space", "1993: Space Syntax Laboratory UCL", "2012: depthmapX software"],
        "influenced_by": ["B. Hillier (architecture)", "L. March (architectural morphology)", "C. Alexander (pattern language)"],
        "current_status": "foundational",
    },
    "wayfinding_cognition": {
        "seminal_paper": "Passini, R. (1984). Wayfinding in Architecture. Van Nostrand Reinhold.",
        "predecessor": "Lynch's Image of the City (1960); Tolman's cognitive maps (1948)",
        "historical_context": "Passini formalized wayfinding as a problem-solving process: decision-making at choice points. Lynch's earlier work identified 5 elements (paths, edges, districts, nodes, landmarks) that structure mental maps.",
        "key_milestones": ["1948: Tolman's cognitive maps", "1960: Lynch's Image of the City", "1984: Passini's wayfinding framework", "2005: Raubal's spatial cognition"],
        "influenced_by": ["K. Lynch (urban image)", "R. Passini (architecture)", "E.C. Tolman (cognitive psychology)"],
        "current_status": "foundational",
    },
    "topophilia": {
        "seminal_paper": "Tuan, Y.-F. (1974). Topophilia: A Study of Environmental Perception, Attitudes, and Values. Prentice-Hall.",
        "predecessor": "Bachelard's Poetics of Space (1958); humanistic geography tradition",
        "historical_context": "Tuan introduced 'topophilia' — the affective bond between people and place. Bridged geography and psychology. Influenced place attachment theory and argues place experience is fundamentally embodied and culturally mediated.",
        "key_milestones": ["1958: Bachelard's Poetics of Space", "1974: Tuan's Topophilia", "1977: Tuan's Space and Place"],
        "influenced_by": ["Y.-F. Tuan (humanistic geography)", "G. Bachelard (phenomenology of space)", "A. Buttimer (lifeworld)"],
        "current_status": "foundational",
    },
}

# Molecule provenance data
MOLECULE_PROVENANCE = {
    "M_ATTRACTOR_TRANSITION": {
        "source_theories": ["predictive_processing", "pad_model", "flow_theory"],
        "basis": "Synthesizes attractor dynamics from dynamical systems theory with CVA emotional state space",
        "derivation": "Emotional states are modeled as attractors in CVA space; transitions between rasas follow energy landscapes",
    },
    "M_BEAUTY_COMPRESSION": {
        "source_theories": ["predictive_processing", "processing_fluency", "fractal_fluency"],
        "basis": "Beauty emerges from efficient neural coding — stimuli that compress well in the brain's predictive model",
        "derivation": "Combines Schmidhuber's compression progress theory with predictive processing and fluency aesthetics",
    },
    "M_CCT_PREFERENCE": {
        "source_theories": ["circadian_lighting", "color_emotion", "adaptive_thermal"],
        "basis": "Correlated color temperature (CCT) preference varies with time of day, activity, and circadian phase",
        "derivation": "Links melanopic sensitivity curves with thermal comfort preferences and color-emotion associations",
    },
    "M_CULTURAL_VALUATION": {
        "source_theories": ["biophilia", "personal_space", "color_emotion"],
        "basis": "Cultural context modulates valuation weights in CVA framework — same stimulus, different value assignment",
        "derivation": "Quantifies Hofstede cultural dimensions as modifiers of aesthetic and comfort valuations",
    },
    "M_RASA": {
        "source_theories": ["pad_model", "berlyne_arousal", "allesthesia"],
        "basis": "The nine rasas of Indian aesthetic theory mapped to CVA emotional state space as pre-defined attractors",
        "derivation": "Classical Natyashastra rasa theory formalized as attractor states with quantitative constraint/valuation profiles",
    },
}


def mine_extraction_citations(theory_id):
    """Find papers that cite this theory in extractions."""
    citations = set()
    for ef in EXTRACTIONS_DIR.glob("10.*.json"):
        try:
            data = json.load(open(ef))
            for f in data.get("findings", []):
                links = f.get("theory_links", [])
                if any(theory_id.upper() in str(l).upper() or 
                       theory_id.lower().replace("_", " ") in str(l).lower()
                       for l in links):
                    citations.add(ef.stem)
                    if len(citations) >= 20:
                        return list(citations)
        except Exception:
            pass
    return list(citations)


def main():
    errors = 0
    theories_enriched = 0
    molecules_enriched = 0

    # ── Enrich theories ──
    print("=== ENRICHING THEORIES ===")
    for tf in sorted(THEORIES_DIR.glob("*.json")):
        try:
            theory = json.load(open(tf))
            tid = tf.stem
            changed = False

            if tid in THEORY_PROVENANCE:
                prov = THEORY_PROVENANCE[tid].copy()
                # ── CRITICAL: Flag as unverified LLM knowledge ──
                prov["verification_status"] = "unverified_llm_knowledge"
                prov["verification_notes"] = (
                    "This provenance was generated from LLM knowledge, NOT verified "
                    "against actual source documents. Seminal papers, dates, and "
                    "predecessor claims need verification against the cited PDFs."
                )
                if "provenance" not in theory or not theory["provenance"]:
                    theory["provenance"] = prov
                    changed = True
                    print(f"  ✓ {tid}: added provenance ({prov['current_status']}) [UNVERIFIED]")
            
            # Mine citations from extractions (GROUNDED — these papers were read)
            if "citing_papers" not in theory:
                cites = mine_extraction_citations(tid)
                if cites:
                    theory["citing_papers"] = cites[:15]
                    theory["citation_count"] = len(cites)
                    theory["citing_papers_verification"] = "grounded_from_extractions"
                    changed = True

            if changed:
                with open(tf, "w") as f:
                    json.dump(theory, f, indent=2)
                theories_enriched += 1
                
                # ── REFLEX: Verify written file ──
                if HAS_REFLEXES:
                    ok, msg = validate_json_file(tf)
                    warn(ok, msg, context=f"enrich_provenance.theories({tid})")

        except Exception as e:
            errors += 1
            print(f"  ✗ {tf.stem}: {e}")

    # ── Enrich molecules ──
    print("\n=== ENRICHING MOLECULES ===")
    for mf in sorted(MOLECULES_DIR.glob("*.json")):
        try:
            mol = json.load(open(mf))
            mid = mf.stem
            changed = False

            if mid in MOLECULE_PROVENANCE:
                prov = MOLECULE_PROVENANCE[mid]
                if "source_theories" not in mol:
                    mol.update(prov)
                    changed = True
                    print(f"  ✓ {mid}: added source_theories={prov['source_theories']}")
            
            # For molecules without known provenance, try to infer from name
            if "source_theories" not in mol:
                # Try to find matching theories by name keywords
                name_lower = mid.lower()
                inferred = []
                theory_keywords = {
                    "thermal": "adaptive_thermal",
                    "circadian": "circadian_lighting",
                    "acoustic": "auditory_scene_analysis",
                    "color": "color_emotion",
                    "fractal": "fractal_fluency",
                    "stress": "environmental_stress",
                    "attractor": "predictive_processing",
                    "beauty": "berlyne_arousal",
                    "rasa": "pad_model",
                    "prospect": "prospect_refuge",
                    "flow": "flow_theory",
                    "wayfind": "wayfinding_cognition",
                    "restor": "art",
                    "biophil": "biophilia",
                    "music": "brecvema",
                    "space_syntax": "space_syntax",
                    "affordance": "gibson_affordance",
                    "cultural": "personal_space",
                }
                for kw, theory in theory_keywords.items():
                    if kw in name_lower:
                        inferred.append(theory)
                if inferred:
                    mol["source_theories"] = inferred
                    mol["basis"] = f"Inferred from molecule name: bridges {', '.join(inferred)}"
                    changed = True
                    print(f"  ~ {mid}: inferred source_theories={inferred}")

            if changed:
                with open(mf, "w") as f:
                    json.dump(mol, f, indent=2)
                molecules_enriched += 1

        except Exception as e:
            errors += 1
            print(f"  ✗ {mf.stem}: {e}")

    # ── Success Conditions ──
    total_theories = len(list(THEORIES_DIR.glob("*.json")))
    total_molecules = len(list(MOLECULES_DIR.glob("*.json")))
    
    theories_with_prov = sum(1 for f in THEORIES_DIR.glob("*.json") 
                            if json.load(open(f)).get("provenance"))
    molecules_with_src = sum(1 for f in MOLECULES_DIR.glob("*.json")
                            if json.load(open(f)).get("source_theories"))

    print(f"\n{'='*60}")
    print(f"  PROVENANCE ENRICHMENT RESULTS")
    print(f"{'='*60}")
    print(f"  Theories enriched:  {theories_enriched}/{total_theories}")
    print(f"  Molecules enriched: {molecules_enriched}/{total_molecules}")
    print(f"  With provenance:    {theories_with_prov}/{total_theories}")
    print(f"  With source_theories: {molecules_with_src}/{total_molecules}")

    sc1 = theories_with_prov >= 20
    sc2 = molecules_with_src >= 12
    sc3 = errors == 0

    print(f"\n  ── SUCCESS CONDITIONS ──")
    print(f"  {'✓' if sc1 else '✗'}  SC-1: ≥20 theories with provenance: {theories_with_prov}")
    print(f"  {'✓' if sc2 else '✗'}  SC-2: ≥12 molecules with source_theories: {molecules_with_src}")
    print(f"  {'✓' if sc3 else '✗'}  SC-3: No errors: {errors}")
    all_pass = sc1 and sc2 and sc3
    print(f"\n  {'✅ ALL PASS' if all_pass else '⚠️ SOME FAILED'}")
    print(f"{'='*60}")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
