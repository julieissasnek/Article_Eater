# Operationalizing Tier 1.5 Theories in Article Eater

**Version 1.0 — February 20, 2026**

This document outlines the standard operating procedure for "operationalizing" a new Tier 1.5 domain theory within the Article Eater system so that incoming empirical literature is correctly mapped and bridged to the theory.

## 1. What Does "Operationalizing" Mean in this Architecture?

In the Article Eater, Tier 1.5 theories (like ART, SRT, Biophilia, and now Privacy Regulation or Adaptive Thermal Comfort) are **not** hardcoded nodes in the Bayesian Network. 

Instead, they are **theoretical extraction tags** (`theory_id`) attached to Belief nodes in the Web of Belief. To operationalize a new theory, you must register it in the extraction pipeline's cognitive ontology so that the LLM and rule-engine can automatically tag empirical claims with the correct parent theory.

## 2. Step-by-Step Implementation Guide

To bring a new T1.5 theory online, you must modify the core mapping dictionaries located in `/src/services/extraction_to_web.py`. 

### Step 2.1: Register Semantic Outcomes (`OUTCOME_DOMAIN_TO_THEORY`)

The primary mapping mechanism is the outcome domain. When an empirical claim affects a known domain (e.g., `physio.thermal`), the system infers the overarching theory.

```python
# Example from src/services/extraction_to_web.py
OUTCOME_DOMAIN_TO_THEORY: Dict[str, List[str]] = {
    # Existing
    "physio.alertness": ["SRT", "ART"],
    "health.wellbeing": ["SRT", "Biophilia"],
    
    # NEW MAPPINGS FOR T1.5 EXPANSION:
    "physio.thermal": ["Adaptive_Thermal_Comfort"],
    "behav.adaptive": ["Adaptive_Thermal_Comfort", "Privacy_Regulation"],
    "social": ["Biophilia", "Privacy_Regulation"],
    "social.privacy": ["Privacy_Regulation"],
    "social.crowding": ["Privacy_Regulation"],
    "social.interaction": ["Privacy_Regulation"],
    "affect.preference": ["Kaplan_Preference_Matrix"],
    "affect.aesthetics": ["Kaplan_Preference_Matrix"],
    "affect.comfort.thermal": ["Adaptive_Thermal_Comfort"],
}
```

### Step 2.2: Register Literal Keywords (`THEORY_KEYWORDS`)

As a fallback inference mechanism, the system scans the text of the empirical claim or paper abstract for literal keywords strongly associated with the theory. 

```python
# Example from src/services/extraction_to_web.py
THEORY_KEYWORDS: Dict[str, List[str]] = {
    # NEW FALLBACKS FOR T1.5 EXPANSION:
    "Privacy_Regulation": [
        "privacy regulation", "altman", "crowding", "personal space",
        "territoriality", "social contact", "boundary regulation"
    ],
    "Kaplan_Preference_Matrix": [
        "kaplan preference", "environmental preference", "coherence",
        "complexity", "legibility", "mystery"
    ],
    "Adaptive_Thermal_Comfort": [
        "adaptive thermal", "thermal comfort", "de dear", "brager",
        "pmv", "natural ventilation", "temperature preference"
    ],
}
```

## 3. Retroactive Application (Backfilling)

If you have already processed millions of constraints through Article Eater (like the 12,628 base claims inside `data/web_persistence.db`), you do not need to re-run the LLM extraction PDF pipeline.

You can retroactively apply the new T1.5 operationalizations using the patch script:
```bash
python3 scripts/patch_web_theories_and_levels.py
```
This script iterates through the existing database, runs the claims back through the updated `infer_theory_relevance_enhanced` function, and hooks up the dormant empirical evidence to the newly registered T1.5 theories!

For example, when `Privacy_Regulation`, `Kaplan_Preference_Matrix`, and `Adaptive_Thermal_Comfort` were added on Feb 20, 2026, running the patch script immediately hooked up 37 dormant claims directly to the three new theories.

## 4. How the Bridged Credence Formula Responds

Once the theory is hooked up, any empirical claim pointing to it will now utilize the theory's overarching credence via the bridge mechanism:

`P(CNFA effect) = P(parent theory) x P(bridge) x P(CNFA-specific)`

If the Kaplan Preference Matrix gains high parent-credence derived from hundreds of supporting papers, any single low-N study about "mystery in corridors" automatically receives an inherited confidence boost via its structural grounding!
