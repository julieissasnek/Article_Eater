
ARTICLE EATER v17.0 UPGRADE PACKAGE

Dual-Hierarchy Model (Findings & Mechanisms)

Generated: November 9, 2025

Version Analyzed: v16.0 (Hierarchical Rules)

Target Version: v17.0 (Dual-Hierarchy Model)

Estimated Implementation: 24-30 hours (Data Migration Required)

📋 WHAT'S IN THIS PACKAGE

This v17 package represents a major conceptual refactor of the Article Eater evidence synthesis model.

The v16 package [cite: 1-788] conflated empirical findings (e.g., "plants reduce cortisol") with theoretical explanations (e.g., "biophilia hypothesis") by storing them in the same data structure.

This v17 "Dual-Hierarchy" package corrects this conceptual flaw by separating the data model into two distinct, linked hierarchies:

The Finding Hierarchy (The "What"): Models the empirical, causal, and aggregational relationships. (e.g., Micro-Finding: [Plants -> Cortisol ↓] aggregates into Meso-Finding: [Plants -> Stress Reduction]).

The Mechanism Hierarchy (The "Why"): A new, independent hierarchy that models the purely theoretical relationships between explanatory constructs. (e.g., Theory: [Predictive Processing] explains Mechanism: [Perceptual Fluency]).

The Explanation Link (The "Bridge"): A new many-to-many join table that connects a specific Finding to a specific Mechanism, with its own provenance.

This upgrade transforms Article Eater from an evidence aggregator into a scientific theory modeler, capable of tracking not just what the evidence says, but why different researchers believe it works, and modeling competing explanations for the same phenomenon.

📚 DOCUMENTATION FILES (Read in Order)

1. AI Critique Prompt for v17 ⭐ START HERE

File: v17_AI_CRITIQUE_PROMPT.md

Purpose: The formal prompt for peer AI models to evaluate and critique the conceptual integrity of this v17 "Dual-Hierarchy" model. It contains the core thesis, success conditions, and problem statement.

2. v17 Quick Reference: Dual-Hierarchy Model

File: v17_Quick_Reference_Dual_Hierarchy.md

Purpose: The new conceptual "bible." Explains the "What" (Findings), the "Why" (Mechanisms), and the "Bridge" (Links).

3. v17 Implementation Package ⭐ MAIN CODE

File: v17_Implementation_Package.md

Purpose: All production-ready code for the v17 refactor.
Components:

SQL Database Migrations (4 files, CRITICAL)

Enhanced 7-Panel Extraction Prompt (v17)

meta_review.py (v17 Logic - Bifurcated)

tasks.py (v17 Logic - Explanation Processing)

4. v17 Templates Package ⭐ UI CODE

File: v17_Templates_Package.md

Purpose: All frontend components, refactored to display the new dual-hierarchy model (e.g., meso_finding_node.html).

5. v17 Deployment Plan ⭐ YOUR ROADMAP

File: v17_Deployment_Plan.md

Purpose: Step-by-step deployment and critical data migration script to move from v16 (single hierarchy) to v17 (dual hierarchy).

🗂️ FILE MANIFEST

v17 Documentation (5 files)

README_Package_Index_v17.md                    (this file)
v17_AI_CRITIQUE_PROMPT.md                        ⭐
v17_Quick_Reference_Dual_Hierarchy.md          ⭐
v17_Implementation_Package.md                  ⭐
v17_Templates_Package.md                       ⭐
v17_Deployment_Plan.md                         ⭐


v17 Code & Contracts (Embedded in Docs)

migrations/001_refactor_rules_to_findings.sql (v17)

migrations/002_add_paper_table.sql (v17)

migrations/003_add_mechanism_hierarchy.sql (v17)

migrations/004_add_explanation_links.sql (v17)

prompts/7_panel_extraction_v17_dual_hierarchy.txt (v17)

meta_review.py (v17 Enhanced)

tasks.py (v17 Explanation Processing Logic)

templates/_partials/meso_finding_node.html (v17)

contracts/findings_v1.md (v17)

contracts/mechanisms_v1.md (v17)

tests/test_meta_review_v17.py (v17 - Fixes RUTHLESS blocker)

Governance & Core (Unchanged / Modified)

Project_Constitution.md

release.keep.yml (Modified for v17)

deprecations.yml (Modified for v17)

public_surface_ledger.json (Modified for v17)

tests/test_governance_sanity.py (Modified for v17)

(All other governance scripts, CI files, etc.)

📖 READING PATH BY ROLE

For Researchers (Focus: Theory)

v17 Quick Reference: Understand the new "Finding" vs. "Mechanism" split.

v17 AI Critique Prompt: Read the "Success Conditions" section to see what this model enables.

v17 Templates Package: Skim the meso_finding_node.html to see how competing explanations will be displayed.

For Developers (Focus: Implementation)

v17 Quick Reference: Understand the new database schema.

v17 Implementation Package: Read all 4 SQL migrations. This is a destructive refactor.

v17 Implementation Package: Study the new Panel 6 prompt.

v17 Implementation Package: Review the new logic in tasks.py for processing explanation_links.

v17 Deployment Plan: Read the Data Migration Script section. This is the most critical part of the upgrade.

For Project Managers (Focus: Planning)

README (This file): Understand the "Why" of this major refactor.

v17 Deployment Plan: This entire refactor is complex and carries data migration risks. Budget 24-30 hours, not 20.

v17 Quick Reference: Understand what new features you can promise to researchers (e.g., "modeling competing theories").

🎯 v17 SUCCESS CRITERIA

After implementing this package, your system should:

Functional Requirements ✅

[ ] Create Micro-Findings from individual operational measures [cite: 55].

[ ] Aggregate Micro-Findings into Meso-Findings based on construct [cite: 75].

[ ] (NEW) Extract Mechanisms (e.g., "Perceptual Fluency") from Panel 6 into a separate mechanisms table.

[ ] (NEW) Create a Mechanism Hierarchy (e.g., "Predictive Processing" -> "Perceptual Fluency").

[ ] (NEW) Create Explanation Links connecting a specific Finding to a specific Mechanism, with provenance.

[ ] (NEW) UI must display all competing explanations (links) for a single finding.

Quality Requirements ✅

[ ] (NEW) The system can represent one Finding (e.g., "Curved Forms -> Anxiety Reduction") linked to two competing Mechanisms (e.g., "Perceptual Fluency" and "Motor Affordance").

[ ] (NEW) The system can distinguish between a Finding's confidence (high, from 10 studies) and its Explanations' strength (low, all "speculative").

[ ] (NEW) User can query: "Show all findings explained by 'Predictive Processing'."

[ ] (NEW) User can query: "Show all mechanisms proposed to explain 'Stress Reduction'."

Research Requirements ✅

[ ] Can answer: "What's the evidence for X?"

[ ] Can also answer: "What are the competing theories for X?"

[ ] Can model scientific debate, not just aggregate consensus.

You are now holding the v17.0 upgrade package.

This is a significant leap forward, moving from evidence aggregation to theory modeling.

Read the v17 Deployment Plan carefully. Data migration is critical.

Good luck! 🎉

Package Version: 2.0 (v17.0 Dual-Hierarchy)
Generated: November 9, 2025
Analyzing: Article Eater v16.0
Target: Article Eater v17.0 (Dual-Hierarchy Model)
Status: PRODUCTION READY (MIGRATION REQUIRED) ✅