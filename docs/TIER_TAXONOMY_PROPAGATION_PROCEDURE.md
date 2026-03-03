# Tier Taxonomy Propagation Procedure
# =====================================
# 
# PURPOSE: When any tier definition changes (T1, T1.5, T2, T3, or Molecules),
# this procedure ensures ALL subsystems are updated consistently.
#
# CANONICAL SOURCES OF TRUTH (March 2, 2026):
#   T1  = 10 frameworks    → schemas/theory/tier1_frameworks.json
#   T1.5= 13 domain theories → schemas/theory/tier1_5_domain_theories.json
#   T2  = ~166 templates   → schemas/theory/tier2_mechanisms.json
#   Molecules = 18         → schemas/theory/molecule_taxonomy.json
#   T3  = DYNAMIC          → empirical beliefs in Web of Belief (grows with EN/BN)
#
# RESOLUTION (March 2, 2026):
#   The master doc had contradictory T1.5 counts (4 in §50, 10 in §122, 12 in §78, 
#   13 including Goldilocks in §78 table). RESOLVED: 13 T1.5 theories total:
#     1. ART (Kaplan), 2. SRT (Ulrich), 3. Biophilia (Wilson/Kellert), 
#     4. Prospect-Refuge (Appleton), 5. Privacy Regulation (Altman),
#     6. Kaplan Preference Matrix (Kaplan & Kaplan), 7. Adaptive Thermal Comfort (de Dear & Brager),
#     8. Space Syntax (Hillier & Hanson), 9. Soundscape Theory (Schafer),
#     10. Place Attachment (Scannell & Gifford), 11. BRECVEMA (Juslin),
#     12. Flow Theory (Csikszentmihalyi), 13. Goldilocks Principle (Berlyne originator; Kirsh extended)
#   Berlyne's New Experimental Aesthetics is SUBSUMED by Goldilocks Principle.
#
# SUCCESS CONDITIONS:
#   1. All code files that reference tier counts load dynamically from canonical JSONs, NOT hardcode
#   2. Where hardcoded counts exist, they match the canonical sources
#   3. The verification test (test_tier_taxonomy_consistency.py) passes
#   4. No file in src/ uses the old abbreviation-only names (PP, IC, NM) as PRIMARY identifiers
#      (abbreviations are acceptable in alias/compatibility mappings like warrant_strength._LEGACY_KEY_MAP)
#   5. T3 counts are NEVER hardcoded (always queried dynamically from DB/extractions)
#
# SUBSYSTEMS TO CHECK WHEN TIER TAXONOMY CHANGES:
#
# ┌─────────────────────────────────────────────────────────────────────────────┐
# │ LAYER 1: CANONICAL SCHEMAS (source of truth — change these first)         │
# ├─────────────────────────────────────────────────────────────────────────────┤
# │ schemas/theory/tier1_frameworks.json         — 10 T1 frameworks           │
# │ schemas/theory/tier1_5_domain_theories.json  — 13 T1.5 domain theories    │
# │ schemas/theory/tier2_mechanisms.json         — ~166 T2 templates          │
# │ schemas/theory/molecule_taxonomy.json        — 18 molecules               │
# └─────────────────────────────────────────────────────────────────────────────┘
#
# ┌─────────────────────────────────────────────────────────────────────────────┐
# │ LAYER 2: CODE THAT READS SCHEMAS (should load dynamically — verify)       │
# ├─────────────────────────────────────────────────────────────────────────────┤
# │ src/services/finding_template_relevance.py   — loads T1+T1.5 from JSON ✅ │
# │ src/services/arbitrary_qa_handler.py         — loads T1+T1.5 from JSON ✅ │
# │ src/services/paper_integration/molecule_linker.py — T1.5 linking          │
# │ src/services/paper_integration/orchestrator.py    — T1.5 linking          │
# │ src/queue/service.py                         — references T1 taxonomy     │
# └─────────────────────────────────────────────────────────────────────────────┘
#
# ┌─────────────────────────────────────────────────────────────────────────────┐
# │ LAYER 3: CODE WITH KEYWORD MATCHING (uses names/abbreviations)            │
# ├─────────────────────────────────────────────────────────────────────────────┤
# │ src/services/paper_integration/tag_engine.py — T1_KEYWORDS dict (kebab)   │
# │ src/services/warrant_strength.py             — _LEGACY_KEY_MAP (compat)   │
# │ src/services/extraction_to_web.py            — outcome→theory mapping     │
# │ src/data/theory_bootstrap.py                 — Theory objects with aliases │
# └─────────────────────────────────────────────────────────────────────────────┘
#
# ┌─────────────────────────────────────────────────────────────────────────────┐
# │ LAYER 4: LLM PROMPTS (guide extraction — abbreviations acceptable here)   │
# ├─────────────────────────────────────────────────────────────────────────────┤
# │ src/extraction/revised_prompts_v2.py         — template matching guide    │
# │ src/extraction/revised_prompts_v3.py         — template matching guide    │
# │ NOTE: Abbreviations (PP, SN, etc.) are acceptable in LLM prompts because │
# │ they are the common citation format in the scientific literature.          │
# └─────────────────────────────────────────────────────────────────────────────┘
#
# ┌─────────────────────────────────────────────────────────────────────────────┐
# │ LAYER 5: QA AND DISPLAY (user-facing counts — must match canonical)       │
# ├─────────────────────────────────────────────────────────────────────────────┤
# │ src/services/arbitrary_qa_handler.py         — format_theory_catalog ✅    │
# │ src/services/arbitrary_qa_handler.py         — format_meta_system_answer  │
# │ src/services/arbitrary_qa_handler.py         — build_ai_context           │
# │ src/qa/molecules/t1_5_theory_schema.py       — comment (docstring only)   │
# │ src/qa/molecules/registry.py                 — docstring example          │
# │ src/qa/molecules/t1_5_registry.py            — docstring example          │
# └─────────────────────────────────────────────────────────────────────────────┘
#
# ┌─────────────────────────────────────────────────────────────────────────────┐
# │ LAYER 6: DOCUMENTATION (tell Claude to update these)                      │
# ├─────────────────────────────────────────────────────────────────────────────┤
# │ docs/TIER_ARCHITECTURE_SPEC_2026-03-01.md    — says 4 T1.5 → needs 13    │
# │ docs/MASTER_DOC_CMR_2026-02-25.md            — ambiguous (4/10/12/13)     │
# │ docs/RUTHLESS_AUDIT_REPORT_2026-02-23.md     — says 14                   │
# │ docs/SPRINT_PLAN_SETUP_AND_OVERSEER.md       — says 14                   │
# │ docs/DOCUMENTATION_VISUALIZATION_PLAN.md     — says 14                   │
# │ docs/SPRINT_CREDENCE_WARRANT_COMPLETION.md   — says 14                   │
# │ docs/AG_SESSION_WALKTHROUGH_2026-03-01.md    — says 4                    │
# │                                                                           │
# │ ACTION FOR CLAUDE: Update master doc to resolve T1.5 ambiguity:          │
# │   - §50 summary → 13 T1.5 domain theories                               │
# │   - §50.6 heading → "T1.5: Domain Theories (13)"                        │
# │   - §78 table → confirm 13 (rows 1-13, Goldilocks = Berlyne+Kirsh)      │
# │   - §122 table → update to match                                        │
# │   - Paper draft → update count                                           │
# │   - TIER_ARCHITECTURE_SPEC → update to 13                               │
# │   - All other docs → harmonize to 13                                    │
# └─────────────────────────────────────────────────────────────────────────────┘
