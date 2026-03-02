# ATLAS System Map
*Generated: 2026-03-02 06:42 UTC*

This document provides a programmatic structural overview of the ATLAS
(Architecture for Typed, Layered Assessment of Science) system.

## 1. Module Dependency Graph

Total Python modules: **674**
Internal import edges: **705**
Packages: acquire_pdfs_unpaywall, acquisition_digest, add_multi_i_toulmin, ae_home, ae_streamlit_control_room, agents, ambience_activity_priors, analyze_distilled_beliefs, analyze_interactions, analyze_table_rule_root_cause, analyze_translation_failure_causes, analyze_web_health, apply_reflex_fixes, apply_remaining_ceiling_decisions, apply_toulmin_justification, architectural_typology_priors, argument, assign_formal_t1_5, assign_scaffold_t1_frameworks, atlas_system_map, audit_full_csv, audit_provenance, audit_rule_type_coverage, audit_t1_5, audit_table_rule_gold_standard, audit_template_compliance, auto_register_variables, backfill_argument_constraints, backfill_belief_ids, backfill_canonical_outcomes, backfill_confirmed_row_article_types, backfill_env_outcome, backfill_env_outcome_v2, backfill_operationalizations, backfill_outcome_ids, backfill_outcome_polarity_conflicts, backfill_pdf_completion_queue, backfill_provenance, backup_databases, batch_annotate_measurements, batch_annotate_stimuli, batch_extract_pdf_images, batch_fix_db_paths, batch_integrate_papers, bn_unresolved_repair, bn_web_extraction, break_bn_cycles, bridge_template_worlds, build_abstract_reduced_tables, build_antigravity_installer, build_article_type_tables, build_canonical_env_out_registry, build_empirical_v2_sentence_training_set, build_table_extraction_queue, build_table_gold_pack, build_table_remake_paper_queue, build_vocab_bridge, bulk_integrate_extractions, calibrate_credibility, calibrate_templates, ceiling_adjudicator, centrality_weighting, check_enum_drift, check_governance, check_mechanisms, check_notifications, check_repo_health, check_rule_contract_quality, check_table_extraction_quality, check_web_bn_health, classify_and_extract, classify_grounding, cli, cmr, compare_d10_outputs, compare_docx_vs_pdf_claims, compare_gold_vs_model_tables, compare_models, compute_overlap, compute_system_health, config, contracts, conversation_guard, convert_findings_to_rules, core, corpus_health_report, create_pdf_backfill_shards, cx_v12_validate_and_audit, data, debug_csv_keys, deconcat, dedup_templates, demo_layered_network, demo_layered_network_real, demo_theory_system, denoise_table_statements, diagnose_db_corruption, discover_mechanism_gaps, discover_modality_gaps, drain_pdf_queue_with_timeout_skip, enrich_crossref, enrich_findings_with_tier2, enrich_provenance, enrich_template_json_fields, ensure_gap_template_stubs, enterprise_go_smoke, epistemic, evaluate_docx_table_quality, expand_outcome_vocab, expand_t1_5_coverage, expert_calibration_prep, explain_mechanism_derivation, extract_crea_templates, extract_ie_dpt_templates, extract_justification_narratives, extract_panel_json, extract_panel_references, extract_pdf_images, extract_thermal_templates, extract_toulmin_memory, extract_toulmin_multi, extract_toulmin_social, extraction, filter_off_topic_papers, find_csv_keys, fix_empty_vars, fix_molecule_ids, fix_molecule_ids_v2, fix_remaining_gaps, fix_scaffold_templates, fix_validation_errors, force_bn_components, force_bn_rebuild, formalize_theories, full_web_health_test, gap_tracker, gemini_extraction_queue, gemini_triage_papers, generate_ai_search_prompts, generate_annotations_a9_a13_a14, generate_annotations_llm, generate_batch_15_queue, generate_calibration_report, generate_causal_attributes, generate_completeness_report, generate_dashboard, generate_evidence_gap_map, generate_python_catalog, generate_system_report, generate_website_pptx, get_isolated_beliefs, gui_style_guard, identify_reextraction_tiers, import_outcomes_to_oc, improve_web_health, infer_template_images, inspect_rulegraph_v2, install_or_update, instance_library_builder, integrated_prediction_pipeline, interrogation_phase1, interrogation_phase2, interrogation_phase3, interrogation_phase3_v2, interrogation_phase4, investigate_dbs, job_status_inspector, kirsh_decision_tree_analysis, link_local, link_outcomes_to_instruments, link_theories_molecules, lint_bridge_ceilings, lint_ceilings, lint_variables, list_all_keys, llm_field_discovery, load_extraction_csv_to_db, load_staging_links, load_template_theory_links, load_tranche80_theory_links, local_runner, maintain_bn, maintain_web, maintenance, manifest_sha256, merge_pdf_backfill_shards, merge_table_remake_into_production, methods, migrate_annotations_to_unified, migrate_article_type, migrate_beliefs_to_v24, migrate_ci_shape, migrate_claim_type, migrate_evidence_type, migrate_gap_type, migrate_rules_to_web, migrate_templates, migrate_v20, migrate_variables, models, monitor_batch_progress, monitor_queue, nightly_integration_pipeline, offline_pipeline_smoke, offline_pipeline_v2_smoke, optional_archive_then_replace_agent_stubs_v2063, orphan_sweep, overseer_nightly, overseer_nightly_v2, overseer_nightly_v3, parallel_extract_v2, parallel_extraction, patch_schemas_v206, patch_thermal_json, patch_web_theories_and_levels, patch_wire_admin_v206, persist_finding_annotations, populate_remaining_interactions, populate_t1_5_theories, prediction_discovery_engine, preprocess_pdf_queue, print_bridge_types, print_csv_columns, prioritize_and_requeue_article_type_tranche, probe_finding_template_relevance_health, probe_web_of_belief_health, process_af_abstracts, process_papers, process_realtime_pdf_completion_queue, propagate_constraints, prune_unresolved_beliefs, public_surface_ledger, qa, quarantine, query_rules, queue, quick_inspect_pdf_quality, rebuild_web_db, reclassify_pdf_queue_article_types, reconcile_counts, reconcile_queue_with_audit, reconcile_step_mismatches, reconcile_tier2_theory_links, recover_timeout_pdfs_with_tracking, reextract_zero_findings, register_unmapped, remediate_cx_v12_reverse_links, remediate_remaining_errors, remove_bn_cycles, repair_interactions, repair_pdf_confirmed_rules, repair_problem_pdfs, repair_templates, reprocess_article_type_tranche_safe, reprocess_web_relations_and_bridges, resolve_fields, resolve_unknown_direction_from_abstract, restore_clamped_values, resume_extraction, review_extractions, root, run_acquisition_pipeline, run_all_checks, run_all_tests, run_batch_integration, run_bbn_calibration_demo, run_direction_rag_ladder, run_do_calculus, run_entrenchment_replay_safe, run_finding_template_relevance, run_finding_template_relevance_streaming, run_full_extraction, run_image_extraction_batch, run_image_pipeline, run_llm_abstract_pilot, run_llm_table_ladder_agent, run_llm_table_pilot, run_migrations_v20_6, run_open_plan_office_example, run_panel_1_outcomes, run_pdf_queue_until_empty, run_post_tagger, run_primary_school_classroom_example, run_realtime_production_worker, run_realtime_table_rule_intake, run_reflexes, run_visual_tracker, run_web_of_belief_health_baseline, safe_improve_web_health, sanity_check, scan_figures_in_articles, scheduled_pipeline, scholar_query_expander, score_claim_risk, security, security_sql_lint, seed_annotations, seed_beliefs_from_templates, seed_extended_annotations, seed_mechanism_beliefs, seed_missing_theories, seed_modality_stimuli, seed_outcome_attributes, semantic_scholar_enrichment, services, site_content_synthesizer, smoke_test, snowball_expand_corpus, sprint10_quick_sweep, sprint10_validation_sweep, sprint_c_verification, subject_coverage_report, sync_documentation, task_signal, task_signal_backfill_completed, task_signal_dashboard, task_signal_watchdog, taxonomy_cross_reference, test_db, test_do_calculus_bridge, test_extract_7panel_parsing, test_gemini_extraction, test_gemini_extraction_v2, theories, theory, tools, triage_papers_keywords, triage_score, two_pass_extraction, ulrich_1984_full_pipeline, update_safe, upgrade_placeholder_rules_from_tables, upgrade_to_v19_1_4, upgrade_to_v19_1_5, utils, v3_reextraction, v3_reextraction_gemini, v3_surgical_update, validate_all_templates, validate_empirical_v2_output, validate_extraction, validate_ie_dpt_overlaps, validate_mechanism_integration, validate_templates, validate_tier2_reductions, validate_toulmin, verify_pipeline_expectations, vision, web_health_diagnostic, zotero_push

### Hub Modules (most imported)

| Module | Imported By |
|--------|------------|
| `src.services.db_locator` | 53 |
| `src.services.web_of_belief` | 48 |
| `src.cmr.models` | 18 |
| `src.services.web_persistence` | 16 |
| `src.services.web_accumulator` | 16 |
| `src.epistemic.edge_types` | 13 |
| `src.epistemic.node_types` | 12 |
| `src.models.provenance` | 10 |
| `src.cmr.building_eval` | 9 |
| `scripts.gemini_extraction_queue` | 9 |

### Orphan Modules (20 never imported)

- `src.tools.bn_suggest_outcome_templates`
- `src.tools.bn_export_to_csv`
- `src.methods`
- `src.methods.seed_data`
- `src.core`
- `src.epistemic`
- `src.epistemic.api_extensions`
- `src.config`
- `src.config.validate`
- `src.config.settings`

## 2. Web of Belief Structure

Database: `/Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/data/web_of_belief.db`
Tables: web_metadata, beliefs, constraints, bridges, paper_integrations, sqlite_sequence, paper_publication, entrenchment_snapshots, entrenchment_events, coherence_history, local_coherence_history, belief_merge_log, paper_quality, web_snapshots, coherence_alerts
Total beliefs: **0**
Total constraints: **0**
Orphan beliefs: **query_failed**
Stubs: **0**

### Beliefs by Epistemic Level

| Level | Count |
|-------|-------|

## 3. Bayesian Network Structure

Total epistemic variables: **10**
Pathway defaults: **33**
BN database: `not_found`

### Pathways by Type

| Pathway Type | Count |
|-------------|-------|
| subpersonal | 9 |
| personal_epistemic | 12 |
| mixed | 12 |

### Variables by Category

- **uncategorized** (10): environmental_legibility, belief_coherence, epistemic_fluency, epistemic_affect, functional_PE...

## 4. Pipeline Architecture

Flow: `discovery → triage → extraction → [HITL approval] → integration → overseer`
Total stages across all pipelines: **37**
HITL gates: approval

### Article Discovery

- Input: `research_gaps + wishlist`
- Output: `data/extraction_pipeline/extraction_queue.json`
- Stages: gap_prediction → wishlist_check → doi_auto_lookup → unpaywall_oa_check → ag_acquisition_pipeline → zotero_watcher
- Script: `scripts/scheduled_pipeline.py (discovery stage)` (exists)
- Script: `scripts/run_acquisition_pipeline.py` (exists)

### Article Triage

- Input: `extraction_queue (status=pending)`
- Output: `extraction_queue (status=triaged)`
- Stages: gemini_classification → article_type_detection → priority_scoring
- Script: `scripts/gemini_triage_papers.py` (exists)

### Claim Extraction

- Input: `extraction_queue (status=triaged)`
- Output: `extraction_queue (status=accepted)`
- Stages: gemini_extraction → claim_validation → claimv2_normalization
- Script: `scripts/gemini_extraction_queue.py` (exists)

### Human Approval (HITL) [HITL]

- Input: `extraction_queue (status=accepted)`
- Output: `extraction_queue (status=approved|rejected)`
- Stages: review_summary → human_review → approve_or_reject
- Script: `scripts/review_extractions.py` (exists)

### 14-Step Integration Cascade

- Input: `extraction_queue (status=approved)`
- Output: `web_of_belief.db + bn updates`
- Stages: schema_validation → node_classification → warrant_assignment → ceiling_enforcement → bridge_construction → credence_computation → web_insertion → constraint_wiring → coherence_assessment → entrenchment_update → bn_projection → theory_world_update → post_integration_check → notification
- Script: `src/services/paper_integration/orchestrator.py` (exists)
- Script: `src/services/extraction_approval.py` (exists)

### Overseer Nightly

- Input: `all databases + previous reports`
- Output: `docs/overseer_reports/unified_health_{date}.md`
- Stages: system_health → web_bn_health → ceiling_lint → corpus_health → periodic_audit → pipeline_registry → trend_comparison → notifications
- Script: `scripts/overseer_nightly_v2.py` (exists)

## 5. Data Stores

| Path | Format | Description | Exists | Size |
|------|--------|-------------|--------|------|
| `data/extraction_pipeline/extraction_queue.json` | JSON | Pipeline queue | yes | 10.1 MB |
| `data/notifications/queue.json` | JSON | Notification queue | yes | 3.2 KB |
| `data/notifications/approval_log.json` | JSON | Approval audit trail | NO |  |
| `data/web_of_belief.db` | SQLite | Web of belief (primary) | yes | 213.0 KB |
| `data/production/web_of_belief.db` | SQLite | Web of belief (production) | NO |  |
| `data/overseer.db` | SQLite | Overseer governance DB | yes | 0 B |
| `data/extractions/` | JSON files | Raw extraction results | yes | 102.9 MB |
| `data/pdfs/` | PDF files | Downloaded papers | yes | 79.7 MB |
