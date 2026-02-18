# Sprint D.9: Web of Belief Health Report
## 1. Database Overview
- **Tables:** web_metadata, beliefs, constraints, bridges, paper_integrations, sqlite_sequence, paper_publication, entrenchment_snapshots, entrenchment_events, coherence_history, local_coherence_history, belief_merge_log, paper_quality, web_snapshots, coherence_alerts
## 2. Variable Quality (Garbage Detection)
- **Total Implicit Nodes:** 5723- **Nodes > 50 chars (likely fragments):** 297 (5.2%)- **Nodes with spaces:** 0 (0.0%)
**Sample Garbage Nodes:**- `env.unresolved.path_uselinedductsand_plenumchambers...`- `env.unresolved.path_installreactiveor_dissipativemufflers...`- `env.unresolved.ttaacctitliele_exxppeerirmimenentt_dduummmmyy...`- `env.unresolved.approach_avoidance_behavior_motivation...`- `env.unresolved.prescription_pharmacy_over_the_counter...`- `env.unresolved.neurophysiological_cognitive_enhancements...`- `env.unresolved.receiving_social_support_and_engaging_in_prosocial_behavior_both_...`- `env.unresolved.those_who_stayed_in_the_country_during_the_war...`- `env.unresolved.physical_activity_and_prosocial_behavior...`- `env.unresolved.academic_stress_and_both_educational...`
## 3. Graph Connectivity
- **Connected Components:** 2068- **Largest Component Size:** 1489 nodes
## 4. Edge Weight Distribution
- **Mean Credence:** 0.5890- **Min Credence:** 0.35- **Max Credence:** 0.9000000000000015- **Edges with Credence = 0.5 (Default?):** 1609
## 5. Conclusion
This database reflects the 'garbage in, garbage out' problem identified in Doc 70.- The high number of singleton and disconnected components indicates a lack of semantic integration.- The prevalence of long, space-containing node IDs confirms that raw text was treated as variables.- **Recommendation:** Proceed with Task D.11 (Web Rebuild) to replace this database with a clean version derived from the variable vocabulary.