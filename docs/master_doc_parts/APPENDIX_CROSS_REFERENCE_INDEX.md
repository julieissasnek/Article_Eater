# APPENDIX: CROSS-REFERENCE INDEX

**Last Updated**: March 5, 2026
**Version**: V24.0.0
**Purpose**: Comprehensive mapping of key concepts, theories, and system components across master doc sections, source code, tests, schemas, and panel reviews.

---

## How to Use This Index

This appendix maps concepts to their locations across the ATLAS system. For any major concept:

1. **Master Doc Sections**: Where the concept is explained theoretically (§XX notation)
2. **Core Code Files**: Python implementations in `/src/`
3. **Test Files**: Validation and integration tests in `/tests/`
4. **Contracts/Schemas**: JSON schemas and markdown contracts in `/contracts/`
5. **Panel Reviews**: Expert consultation documents in `/docs/PANEL_*`

Each row includes canonical references to support knowledge discovery, teaching, and system modification.

---

## DOMAIN 1: EPISTEMOLOGICAL FRAMEWORK

### Core Epistemic Structures

| Concept | Master Doc Section(s) | Core Code File(s) | Test File(s) | Contract/Schema | Panel Review |
|---------|----------------------|-------------------|--------------|-----------------|--------------|
| **Web of Belief** | §84–89 (Part IX: WEB_OF_BELIEF) | `src/epistemic/web_of_belief.py`, `src/epistemic/web_of_belief_state.py`, `src/epistemic/web_of_belief_mutation.py` | `test_web_of_belief.py`, `test_web_of_belief_invariants.py`, `test_web_of_belief_health_baseline_runner.py`, `test_web_of_belief_analysis_ops.py`, `test_web_of_belief_mutation_safeguards.py` | `contracts/schemas/propositional_content.v1.schema.json`, `contracts/ae_af/schemas/ae.web_state.v1.schema.json` | PANEL_INFRA_DECISIONS_LOG.md |
| **Credence Intervals** | §48–53 (Part IV: CREDENCE) | `src/epistemic/credence_interval.py`, `src/epistemic/credence_calculator.py`, `src/epistemic/credence_projection.py` | `test_credence_intervals.py`, `test_credence_intervals_integration.py` | `contracts/schemas/epistemic_status.v1.schema.json` | PANEL_CALIBRATION_REVIEW_2026-03-02.md |
| **Bridge Warrants** | §48.1–48.3 (Part IV), §55 (Part V implied) | `src/services/bridge_warrants.py`, `src/epistemic/warrant_types.py` | `test_bridge_warrants.py`, `test_bridge_ceilings.py`, `test_warrant_strength.py` | (Embedded in extraction templates) | PANEL_CALIBRATION_REVIEW_2026-03-02.md |
| **Defeasible Reasoning** | §49–50, §84–89 (Parts IV, IX) | `src/argument/engine.py`, `src/argument/hierarchy_evidence.py`, `src/epistemic/revision_engine.py` | `test_argument_structure.py`, `test_argument_attack.py`, `test_evidence_accumulation.py` | `contracts/rule_interactions_api.contract.md` | PANEL_DELIBERATION_NOTES_2026-03-02.md |
| **Transfer Reliability** | §48.1A–48.1B (Part IV) | `src/epistemic/transfer_reliability.py`, `src/epistemic/credence_projection.py` | `test_credence_intervals_integration.py` | (Part of warrant projection calculus) | PANEL_CALIBRATION_REVIEW_2026-03-02.md |
| **Epistemic Status** | §49.6 (Part IV) | `src/epistemic/epistemic_status.py`, `src/epistemic/warrant_types.py` | `test_epistemic_services.py`, `test_epistemic_causal_integration.py` | `contracts/schemas/epistemic_status.v1.schema.json` | PANEL_A_SCHEMA_REVIEW_2026-03-01.md |
| **Entrenchment (Theory)** | §49.1–49.3 (Part IV), §127–130 (Part XVII Meta-Epistemology) | `src/epistemic/entrenchment_tracker.py`, `src/epistemic/web_of_belief_state.py` | `test_entrenchment_tracker.py`, `test_entrenchment_replay_safe.py` | (Implicit in web state schema) | PANEL_INFRA_DECISIONS_LOG.md |
| **Coherence (Quinean)** | §84–86 (Part IX), §49.5–49.6 (Part IV) | `src/epistemic/coherence_engine.py`, `src/epistemic/scalable_coherence.py` | `test_scalable_coherence.py`, `test_scalable_coherence_benchmark.py`, `test_bn_coherence_client.py` | (Implicit in web state operations) | PANEL_COHERENCE_THRESHOLDS_2026-03-02.md |

---

## DOMAIN 2: EXTRACTION PIPELINE & DATA INGESTION

### Extraction Stages & Template System

| Concept | Master Doc Section(s) | Core Code File(s) | Test File(s) | Contract/Schema | Panel Review |
|---------|----------------------|-------------------|--------------|-----------------|--------------|
| **V3 Extraction** | §35–42 (Part VI: DOMAIN_PANELS) | `src/extraction/v3_extractor.py`, `src/extraction/abstract_extractor.py` | `test_abstract_extractor.py`, `test_sprint4_extraction.py` | `contracts/ae_af/schemas/ae.claim.v1.schema.json` | (Historical; superseded by V4) |
| **V4 Staged Extraction** | §35–42 (Part VI), §16–20 (Part II implied) | `src/extraction/v4_extractor.py`, `src/extraction/extraction_orchestrator.py` | `test_sprint4_extraction.py`, `test_extraction_field_validator.py` | `contracts/ae_af/schemas/ae.claim.v2.schema.json` | PANEL_A_SCHEMA_REVIEW_2026-03-01.md |
| **Template Library** | §102–114 (Part X: TEMPLATE_LIBRARY) | `src/templates/template_registry.py`, `src/templates/template_loader.py`, `src/templates/template_hierarchy_registry.py` | `test_template_record.py`, `test_template_matching_module.py`, `test_template_query_service.py` | (See finding templates; outcome vocab) | PANEL_C_THEORY_MOLECULE_2026-03-01.md |
| **Schema Fields** | §16–24 (Part II: THEORETICAL), §45–47 (Part IV implied) | `src/models/extraction_schema.py`, `src/models/field_validator.py` | `test_extraction_field_validator.py`, `test_field_validation.py`, `test_input_validation.py` | `contracts/schemas/extraction_template.v2.schema.json`, `contracts/ae_af/schemas/ae.claim.v2.schema.json` | PANEL_A_SCHEMA_REVIEW_2026-03-01.md |
| **Finding Templates** | §102–114 (Part X: TEMPLATE_LIBRARY) | `src/services/finding_template_service.py`, `src/services/finding_template_matcher.py` | `test_finding_template_fixes.py`, `test_finding_template_relevance.py`, `test_mechanism_templates.py` | `contracts/findings_v20.contract.md`, `contracts/outcome_vocab/outcome_lookup.json` | PANEL_IMPLEMENTATION_2026-03-01.md |
| **Outcome Vocabulary** | §103–105 (Part X) | `src/models/outcome_model.py`, `src/services/outcome_vocabulary_service.py` | `test_outcome_taxonomy.py`, `test_outcome_extraction.py` | `contracts/outcome_vocab/outcome_vocab.json`, `contracts/outcome_vocab/outcome_lookup.json`, `contracts/outcome_vocab/template_to_db_bridge.json` | PANEL_D_VISION_ATTRIBUTES_2026-03-01.md |
| **Bibtex Ingestion** | §11–15 (Part I implied) | `src/ingestion/bibtex_ingester.py`, `src/ingestion/bibtex_parser.py`, `src/ingestion/bibtex_generator.py` | `test_bibtex_ingestion.py`, `test_bibtex_generator.py`, `test_bibtex_e2e_flow.py` | (JSON formats from BibTeX) | (Embedded in extraction) |
| **Paper Fetcher** | §35 (Part VI implied) | `src/ingestion/paper_fetcher.py`, `src/ingestion/paper_history.py` | `test_paper_fetcher.py`, `test_paper_history.py`, `test_paper_integration.py` | `contracts/ae_af/schemas/ae.paper.v1.schema.json` | (Historical; replaced by CMR) |

---

## DOMAIN 3: KNOWLEDGE ARTIFACTS & REPRESENTATION

### Card System & Argumentation

| Concept | Master Doc Section(s) | Core Code File(s) | Test File(s) | Contract/Schema | Panel Review |
|---------|----------------------|-------------------|--------------|-----------------|--------------|
| **Nine Card Types** | §115–126 (Part XI: ARCH_TYPOLOGY) | `src/models/card_model.py`, `src/services/card_generators/` (9 generator classes) | `test_card_schema.py`, `test_card_integration_e2e.py`, `test_card_retrieval.py` | `contracts/ae_af/schemas/ae.rule.v1.schema.json` (proto; v2 recommended) | PANEL_IMPLEMENTATION_2026-03-01.md |
| **Interpretation Space** | §67–71 (Part VIII: IE_DPT), §120 (Part XI) | `src/models/interpretation_space.py`, `src/services/interpretation_space_service.py` | `test_interpretation_space.py`, `test_interpretation_space_suggestions.py` | `contracts/schemas/social_epistemology.v1.schema.json` | PANEL_C_THEORY_MOLECULE_2026-03-01.md |
| **Argumentation Graph** | §128–130 (Part XVII: META_EPISTEMOLOGY) | `src/argument/engine.py`, `src/argument/paper_relations.py` | `test_argument_structure.py`, `test_argument_tracing.py`, `test_graph_api.py` | `contracts/rule_interactions_api.contract.md` | PANEL_DELIBERATION_NOTES_2026-03-02.md |
| **Claim Extraction** | §35–42 (Part VI) | `src/extraction/claim_extractor.py`, `src/services/claim_gallery_builder.py` | `test_claim_extraction.py`, `test_claim_extractor.py`, `test_claim_gallery_builder.py` | `contracts/ae_af/schemas/claim_gallery.v1.schema.json`, `contracts/ae_af/schemas/ae.claim.v2.schema.json` | PANEL_A_SCHEMA_REVIEW_2026-03-01.md |
| **Annotation Service** | §45–47 (Part IV implied) | `src/services/annotation_service.py`, `src/models/annotation_model.py` | `test_annotation_service.py`, `test_annotation_card_integration.py` | `contracts/ae_af/schemas/image_feedback.v1.schema.json` | PANEL_IMPLEMENTATION_2026-03-01.md |
| **Bridge (Concept)** | §55 (Part V implied), §48.3–48.4 (Part IV) | `src/epistemic/bridge_warrant.py`, `src/services/bridge_warrants.py` | `test_bridge_warrants.py`, `test_bridge_ceilings.py` | `contracts/ae_af/schemas/ae.bridge.v1.schema.json` | PANEL_CALIBRATION_REVIEW_2026-03-02.md |
| **Rule Format** | §102–114 (Part X: TEMPLATE_LIBRARY) | `src/models/rule_model.py`, `src/services/rule_to_claim_mapper.py` | `test_rule_to_claim_mapper.py` | `contracts/ae_af/schemas/ae.rule.v2.schema.json`, `contracts/rules_v1.md` | PANEL_IMPLEMENTATION_2026-03-01.md |

---

## DOMAIN 4: QUALITY ASSURANCE & SUCCESS CRITERIA

### Oversight, Metrics, & Validation

| Concept | Master Doc Section(s) | Core Code File(s) | Test File(s) | Contract/Schema | Panel Review |
|---------|----------------------|-------------------|--------------|-----------------|--------------|
| **Overseer System** | §131–140 (Part XVII: META_EPISTEMOLOGY) | `src/qa/overseer.py`, `src/qa/overseer_inv4.py`, `src/qa/overseer_management.py` | `test_overseer_coverage.py`, `test_overseer_inv4.py`, `test_overseer_management.py` | (Implicit in QA contracts) | PANEL_B_QUALITY_THRESHOLDS_2026-03-01.md |
| **AESHI Score** | §138–140 (Part XVII) | `src/qa/aeshi_calculator.py`, `src/services/effect_size_converter.py` | `test_aeshi_blocker_fixes.py`, `test_effect_size_converter.py`, `test_effect_size_validator.py` | (JSON format in quality gate contracts) | PANEL_B_QUALITY_THRESHOLDS_2026-03-01.md |
| **Success Conditions** | §131–137 (Part XVII) | `src/qa/success_conditions_orchestrator.py`, `src/qa/success_conditions.py` | `test_success_conditions.py`, `test_success_conditions_orchestrator.py`, `test_success_conditions_iqs.py`, `test_success_conditions_qa_handler.py` | `contracts/success_conditions.json` | PANEL_B_QUALITY_THRESHOLDS_2026-03-01.md |
| **Nightly Pipeline** | §141 (Part XVII implied) | `src/qa/nightly_pipeline.py`, `src/qa/pipeline_monitor.py`, `src/qa/realtime_pipeline_guardrails.py` | `test_nightly_qa_quality_gate.py`, `test_realtime_pipeline_guardrails.py` | (Contracts embedded in orchestrator) | (Part of CI/CD) |
| **Validation Gates** | §35–42 (Part VI), §131–137 (Part XVII) | `src/qa/extraction_gate.py`, `src/qa/grounding_gate.py`, `src/qa/phase_1b_validator_gate.py` | `test_extraction_gate.py`, `test_grounding_gate.py`, `test_phase_1b_validator_gate.py` | (Implicit in validation contracts) | PANEL_B_QUALITY_THRESHOLDS_2026-03-01.md |
| **Evidence Risk Assessment** | §49–51 (Part IV) | `src/qa/evidence_risk_checker.py`, `src/qa/confounder_risk_checker.py` | `test_evidence_risk.py`, `test_confounder_risk_checker.py` | (Implicit in coherence contracts) | PANEL_JUSTIFICATION_PROVENANCE_2026-03-02.md |
| **Credibility Testing** | §48–53 (Part IV) | `src/qa/credibility_feedback.py`, `src/qa/credibility_testing.py` | `test_credibility_feedback.py`, `test_credibility_testing.py` | (Part of epistemic status schema) | PANEL_CALIBRATION_REVIEW_2026-03-02.md |
| **Systematic Failure Modes** | §140–142 (Part XVII) | `src/qa/systemic_failure_detector.py`, `src/qa/failure_mode_catalogue.py` | `test_systemic_failure_modes.py` | (Catalogue in JSON) | PANEL_DELIBERATION_NOTES_2026-03-02.md |

---

## DOMAIN 5: QA SYSTEM & QUESTION HANDLING

### Query Processing & Answer Enrichment

| Concept | Master Doc Section(s) | Core Code File(s) | Test File(s) | Contract/Schema | Panel Review |
|---------|----------------------|-------------------|--------------|-----------------|--------------|
| **Question Classification** | §58–66 (Part VII: T15_REDUCTIONS) | `src/qa/question_classifier.py`, `src/qa/query_parser.py` | `test_query_parser.py`, `test_quick_assess.py` | (Implicit in QA contracts) | (Part of T15 system) |
| **QA Handlers** | §58–66 (Part VII), §115–126 (Part XI) | `src/argument/qa_handlers.py`, `src/qa/handler_orchestrator.py` | `test_success_conditions_qa_handler.py`, `test_e2e_qa_pipeline.py` | (Part of handler registry) | PANEL_IMPLEMENTATION_2026-03-01.md |
| **Answer Enrichment** | §67–71 (Part VIII: IE_DPT) | `src/qa/answer_enrichment_orchestrator.py`, `src/qa/language_adaptation_service.py`, `src/qa/prose_revision_service.py` | `test_answer_enrichment_orchestrator.py`, `test_language_adaptation_service.py`, `test_prose_revision_service.py` | (Implicit in handler contracts) | (Part of prose standards) |
| **Query Routes** | §58 (Part VII) | `src/api/query_routes.py`, `src/cli/query.py` | `test_query_routes.py`, `test_cli_web_flags.py` | (Implicit in API contracts) | (API documentation) |
| **Query Engine** | §58–66 (Part VII) | `src/qa/query_engine.py`, `src/qa/streamlit_query_service.py` | `test_query_engine.py`, `test_streamlit_query_service.py`, `test_cross_layer_query.py` | `contracts/ae_af/schemas/ae.query_request.v1.schema.json`, `contracts/ae_af/schemas/ae.query_response.v1.schema.json` | (Part of API contracts) |
| **Evidence Summarizer** | §128–130 (Part XVII) | `src/qa/evidence_summarizer.py`, `src/argument/meta_analytic.py` | `test_evidence_summarizer.py`, `test_meta_analytic.py` | (Part of argumentation contracts) | (Part of prose standards) |
| **Response Formatting** | §58–66 (Part VII) | `src/qa/answer_renderer.py`, `src/qa/output_serializer.py` | `test_answer_renderer.py`, `test_output_serializer.py` | `contracts/ae_af/schemas/ae.query_response.v1.schema.json` | (Part of API contracts) |
| **Circuit QA Service** | §67–71 (Part VIII) | `src/qa/circuit_qa_service.py` | `test_circuit_qa_service.py`, `test_functional_circuits.py` | (Implicit in IE-DPT service contracts) | PANEL_C_THEORY_MOLECULE_2026-03-01.md |

---

## DOMAIN 6: THEORETICAL FRAMEWORKS

### Environmental Psychology & Theory

| Concept | Master Doc Section(s) | Core Code File(s) | Test File(s) | Contract/Schema | Panel Review |
|---------|----------------------|-------------------|--------------|-----------------|--------------|
| **Implicit-Explicit Dual Processing (IE-DPT)** | §67–71 (Part VIII: IE_DPT) | `src/theory/implicit_explicit_theory.py`, `src/qa/circuit_qa_service.py` | `test_phase1_refined_epistemic.py`, `test_circuit_qa_service.py`, `test_functional_circuits.py` | (Implicit in theory service contracts) | PANEL_C_THEORY_MOLECULE_2026-03-01.md |
| **Allostatic Load** | §89 (Part IX) | `src/models/allostasis_model.py`, `src/theory/allostatic_framework.py` | (Implicit in load-reduction tests) | (Implicit in template library) | PANEL_D_VISION_ATTRIBUTES_2026-03-01.md |
| **Prospect-Refuge Theory** | §72–74 (Part VIII implied) | `src/templates/prospect_refuge_template.py` | `test_interpretation_space_suggestions.py` | (Part of template library definitions) | PANEL_C_THEORY_MOLECULE_2026-03-01.md |
| **Biophilia** | §74–75 (Part VIII implied) | `src/templates/biophilia_template.py`, `src/services/biophilia_reduction.py` | `test_biophilia_reduction.py` | (Part of template library definitions) | PANEL_D_VISION_ATTRIBUTES_2026-03-01.md |
| **Attention Restoration Theory** | §75–76 (Part VIII implied) | `src/templates/attention_restoration_template.py`, `src/services/art_reduction.py` | `test_art_reduction.py` | (Part of template library definitions) | PANEL_D_VISION_ATTRIBUTES_2026-03-01.md |
| **Social Epistemology** | §127–130 (Part XVII: META_EPISTEMOLOGY) | `src/epistemic/social_epistemology.py`, `src/models/social_epistemology_model.py` | `test_social_epistemology.py` | `contracts/schemas/social_epistemology.v1.schema.json` | PANEL_DELIBERATION_NOTES_2026-03-02.md |
| **Coherence Theory** | §49.5–49.6, §84–86 | `src/epistemic/coherence_engine.py`, `src/epistemic/web_of_belief_state.py` | `test_scalable_coherence.py`, `test_web_of_belief_analysis_ops.py` | (Implicit in web state operations) | PANEL_COHERENCE_THRESHOLDS_2026-03-02.md |

---

## DOMAIN 7: ARCHITECTURAL TYPOLOGY & DOMAIN KNOWLEDGE

### Architecture Types & Domain Panels

| Concept | Master Doc Section(s) | Core Code File(s) | Test File(s) | Contract/Schema | Panel Review |
|---------|----------------------|-------------------|--------------|-----------------|--------------|
| **Domain Panels** | §29–43 (Part VI: DOMAIN_PANELS) | `src/agents/agent_panels_v2.py`, `src/cmr/architect_report.py` | `test_cmr_paper_eval.py`, `test_cmr_building_eval.py` | (Panel literature summaries in master doc) | PANEL_2_EXECUTIVE_BRIEFING_2026-02-27.md |
| **T15 Reductions** | §56–66 (Part VII: T15_REDUCTIONS) | `src/theory/t15_reduction_engine.py`, `src/services/claim_gallery_builder.py` | `test_gap_template_computations.py`, `test_gap_template_stubs.py` | (Implicit in template library) | PANEL_E02_T1_FRAMEWORK_ASSIGNMENT_2026-02-23.md |
| **Institution Tiers** | §44–47 (Part IV implied) | `src/models/institution_tier.py` | `test_tier1_data_model.py`, `test_tier2_scores.py`, `test_tier_taxonomy_consistency.py` | `contracts/vocab/institution_tiers.json` | (Part of domain typology) |
| **Building Evaluation** | §29–43 (Part VI) | `src/cmr/building_eval.py`, `src/cmr/building_eval_regression.py` | `test_building_eval.py`, `test_building_eval_regression.py`, `test_cmr_building_eval.py` | (Implicit in CMR architecture) | PANEL_IMPLEMENTATION_2026-03-01.md |
| **Mechanism Chain Validation** | §88 (Part IX) | `src/models/mechanism_chain.py`, `src/services/mechanism_chain_validation.py` | `test_mechanism_chain_validation.py`, `test_mechanism_tracing_module.py` | (Implicit in bridge warrant contracts) | PANEL_CALIBRATION_REVIEW_2026-03-02.md |

---

## DOMAIN 8: BAYESIAN NETWORK & CAUSAL INFERENCE

### Causal Modeling & Probabilistic Reasoning

| Concept | Master Doc Section(s) | Core Code File(s) | Test File(s) | Contract/Schema | Panel Review |
|---------|----------------------|-------------------|--------------|-----------------|--------------|
| **Bayesian Network** | §44–53 (Part IV), §85–87 (Part IX) | `src/causal/bayesian_network.py`, `src/causal/bn_builder.py`, `src/causal/incremental_bn.py` | `test_incremental_bn.py`, `test_bn_coherence_client.py`, `test_bn_health.py`, `test_bn_unresolved_repair.py` | (Implicit in causal modeling contracts) | (Part of causal infrastructure) |
| **Causal Classifier** | §58–66 (Part VII) | `src/services/causal_classifier.py`, `src/services/iv_dv_classifier.py` | `test_causal_classifier.py`, `test_iv_dv_classifier.py` | (Implicit in extraction templates) | (Part of extraction pipeline) |
| **Coherence-BN Bridge** | §48–53 (Part IV), §85–87 (Part IX) | `src/epistemic/coherence_to_bn_bridge.py`, `src/causal/epistemic_to_causal.py` | `test_epistemic_causal_integration.py` | (Implicit in bridge warrant contracts) | PANEL_CALIBRATION_REVIEW_2026-03-02.md |
| **Causal API** | §58–66 (Part VII) | `src/api/causal_routes.py` | `test_api_causal.py` | `contracts/ae_af/schemas/ae.bridge.v1.schema.json` | (API documentation) |
| **Subject BN Pipeline** | §85–87 (Part IX) | `src/causal/subject_bn_pipeline.py`, `src/causal/subject_bn_csv_pack.py`, `src/causal/subject_bn_export.py` | `test_subject_bn_pipeline.py`, `test_subject_bn_csv_pack.py`, `test_subject_bn_export.py` | (Implicit in BN export contracts) | (Part of export infrastructure) |
| **Uncertainty in Causal Reasoning** | §49–51 (Part IV) | `src/causal/uncertainty_handling.py` | `test_uncertainty_wis.py` | (Part of epistemic status schema) | PANEL_CALIBRATION_REVIEW_2026-03-02.md |

---

## DOMAIN 9: RESEARCH INFRASTRUCTURE & EVIDENCE MANAGEMENT

### Literature, Papers, and Evidence Tracking

| Concept | Master Doc Section(s) | Core Code File(s) | Test File(s) | Contract/Schema | Panel Review |
|---------|----------------------|-------------------|--------------|-----------------|--------------|
| **Research Queue** | §11–15 (Part I implied) | `src/research_queue/research_queue_service.py`, `src/research_queue/automated_searcher.py`, `src/research_queue/zotero_sync.py` | `test_research_queue_service.py`, `test_research_queue_automated_searcher.py`, `test_research_queue_zotero_sync.py` | `contracts/research_queue.contract.md` | PANEL_INFRA_DECISIONS_LOG.md |
| **Paper Triage** | §35 (Part VI) | `src/cmr/paper_triage.py`, `src/services/paper_evaluator.py` | `test_paper_triage.py`, `test_cmr_paper_eval.py`, `test_paper_eval_pipeline.py` | (Implicit in CMR contracts) | PANEL_IMPLEMENTATION_2026-03-01.md |
| **Paper Evidence Auditor** | §129–130 (Part XVII) | `src/qa/paper_evidence_auditor.py`, `src/cmr/paper_evidence_auditor.py` | `test_paper_evidence_auditor.py` | (Implicit in auditing contracts) | PANEL_JUSTIFICATION_PROVENANCE_2026-03-02.md |
| **Paper Report** | §35–42 (Part VI) | `src/cmr/paper_report.py` | `test_paper_report.py`, `test_cmr_report.py` | `contracts/ae_af/schemas/ae.result.v1.schema.json` | (Part of reporting standards) |
| **Provenance (Evidence)** | §46–47 (Part IV) | `src/models/provenance_model.py`, `src/services/provenance_builder.py` | `test_provenance_paper.py`, `test_provenance_building.py` | `contracts/ae_af/schemas/ae.provenance.v1.schema.json` | PANEL_JUSTIFICATION_PROVENANCE_2026-03-02.md |
| **Audit Event** | §131–137 (Part XVII) | `src/qa/audit_event.py`, `src/qa/export_audit.py` | `test_export_audit.py` | `contracts/ae_af/schemas/ae.audit_event.v1.schema.json` | (Part of QA infrastructure) |
| **Value of Information (VOI)** | §52–53 (Part IV) | `src/research_infrastructure/voi_scoring.py`, `src/research_infrastructure/voi_search.py`, `src/research_infrastructure/researcher_voi.py` | `test_voi_scoring.py`, `test_voi_search.py`, `test_voi_integration.py`, `test_researcher_voi.py` | (Implicit in research strategy contracts) | (Part of research planning) |

---

## DOMAIN 10: API, INTEGRATION & EXTERNAL SYSTEMS

### API Routes, Integration Points, and External Services

| Concept | Master Doc Section(s) | Core Code File(s) | Test File(s) | Contract/Schema | Panel Review |
|---------|----------------------|-------------------|--------------|-----------------|--------------|
| **API Key Routes** | §58 (Part VII) | `src/api/api_key_routes.py`, `src/api/usage_admin_auth.py` | `test_api_key_routes.py`, `test_usage_admin_auth.py` | (Implicit in auth contracts) | (Security documentation) |
| **Query Routes** | §58 (Part VII) | `src/api/query_routes.py` | `test_query_routes.py` | `contracts/ae_af/schemas/ae.query_request.v1.schema.json`, `contracts/ae_af/schemas/ae.query_response.v1.schema.json` | (API documentation) |
| **Reports Routes** | §141 (Part XVII implied) | `src/api/reports_routes.py` | `test_reports_routes.py` | (Implicit in reporting contracts) | (API documentation) |
| **Ingestion Routes** | §35 (Part VI) | `src/api/ingestion_routes.py` | `test_ingestion_routes.py` | (Implicit in ingestion contracts) | (API documentation) |
| **Batch Processing** | §35–42 (Part VI) | `src/cmr/batch_process.py` | `test_batch_extract_d15.py`, `test_batch_processing.py`, `test_api_batch.py` | (Implicit in batch contracts) | (Part of CMR infrastructure) |
| **Cross-Process Communication** | (§141 implied) | `src/cross_process/xproc_coordinator.py` | `test_cross_process_xproc.py`, `test_cross_pipeline.py` | (Implicit in infrastructure contracts) | PANEL_INFRA_DECISIONS_LOG.md |
| **Image Pipeline Service** | §74–75 (Part VIII implied) | `src/services/image_pipeline_service.py`, `src/services/image_tag_service.py`, `src/services/figure_suggestion_service.py` | `test_image_pipeline_service.py`, `test_image_tag_service.py`, `test_figure_suggestion_service.py` | `contracts/ae_af/schemas/image_feedback.v1.schema.json` | (Part of template visual support) |

---

## DOMAIN 11: SPECIALIZED SERVICES & UTILITIES

### Domain-Specific Tools and Support Services

| Concept | Master Doc Section(s) | Core Code File(s) | Test File(s) | Contract/Schema | Panel Review |
|---------|----------------------|-------------------|--------------|-----------------|--------------|
| **Language Adaptation Service** | §67–71 (Part VIII) | `src/services/language_adaptation_service.py` | `test_language_adaptation_service.py`, `test_success_conditions_language_adaptation.py` | (Implicit in enrichment contracts) | (Part of prose standards) |
| **Prose Revision Service** | §67–71 (Part VIII) | `src/services/prose_revision_service.py` | `test_prose_revision_service.py`, `test_success_conditions_prose_revision.py` | (Implicit in enrichment contracts) | (Part of prose standards) |
| **Math Explanation Service** | §58–66 (Part VII) | `src/services/math_explanation_service.py` | `test_math_explanation_service.py` | `contracts/MATH_EXPLANATION_NORMS.md` | (Part of prose standards) |
| **Theory Matcher** | §102–114 (Part X) | `src/services/theory_matcher.py`, `src/services/theory_link_extraction.py`, `src/services/theory_guide_service.py` | `test_theory_matcher.py`, `test_theory_link_extraction.py`, `test_theory_guide_service.py`, `test_theory_system.py` | (Implicit in template library contracts) | PANEL_C_THEORY_MOLECULE_2026-03-01.md |
| **Mechanism Tracing** | §88 (Part IX) | `src/services/mechanism_tracing_module.py`, `src/argument/hierarchy_evidence.py` | `test_mechanism_tracing_module.py`, `test_hierarchy_relations.py` | (Implicit in argumentation contracts) | PANEL_JUSTIFICATION_PROVENANCE_2026-03-02.md |
| **Critique Aggregator** | §128–130 (Part XVII) | `src/argument/critique_aggregator.py` | (Implicit in argumentation tests) | (Part of argumentation contracts) | PANEL_DELIBERATION_NOTES_2026-03-02.md |
| **Network Service** | §84–89 (Part IX) | `src/services/network_service.py` | `test_network_service.py` | (Implicit in web state contracts) | (Part of infrastructure) |

---

## DOMAIN 12: DATA MODELS & SCHEMA INTEGRATION

### Core Data Structures and Validation

| Concept | Master Doc Section(s) | Core Code File(s) | Test File(s) | Contract/Schema | Panel Review |
|---------|----------------------|-------------------|--------------|-----------------|--------------|
| **Card Model** | §115–126 (Part XI) | `src/models/card_model.py` | `test_card_schema.py` | `contracts/ae_af/schemas/ae.rule.v1.schema.json`, `contracts/ae_af/schemas/ae.rule.v2.schema.json` | PANEL_A_SCHEMA_REVIEW_2026-03-01.md |
| **Outcome Model** | §103–105 (Part X) | `src/models/outcome_model.py` | `test_outcome_taxonomy.py` | `contracts/outcome_vocab/outcome_vocab.json` | PANEL_D_VISION_ATTRIBUTES_2026-03-01.md |
| **Template Record** | §102–114 (Part X) | `src/models/template_record.py` | `test_template_record.py` | (Implicit in template registry) | PANEL_C_THEORY_MOLECULE_2026-03-01.md |
| **Rule Model** | §102–114 (Part X) | `src/models/rule_model.py` | (Implicit in template tests) | `contracts/ae_af/schemas/ae.rule.v2.schema.json` | PANEL_IMPLEMENTATION_2026-03-01.md |
| **Epistemic Status** | §49.6 (Part IV) | `src/epistemic/epistemic_status.py` | `test_epistemic_services.py` | `contracts/schemas/epistemic_status.v1.schema.json` | PANEL_A_SCHEMA_REVIEW_2026-03-01.md |
| **Propositional Content** | §84–86 (Part IX) | `src/models/propositional_content.py` | (Implicit in web state tests) | `contracts/schemas/propositional_content.v1.schema.json` | PANEL_A_SCHEMA_REVIEW_2026-03-01.md |
| **Canonical Variables** | §16–24 (Part II) | `src/models/canonical_variables.py`, `src/models/environment_outcome_taxonomy.py` | `test_canonical_variables.py`, `test_environment_taxonomy.py`, `test_outcome_taxonomy.py` | `contracts/vocab/canonical_enums.json`, `contracts/vocab/environment_lookup.json`, `contracts/vocab/outcome_lookup.json` | PANEL_D_VISION_ATTRIBUTES_2026-03-01.md |

---

## DOMAIN 13: SPECIALIZED REDUCTIONS & ANALYSIS

### Domain-Specific Extraction and Analysis

| Concept | Master Doc Section(s) | Core Code File(s) | Test File(s) | Contract/Schema | Panel Review |
|---------|----------------------|-------------------|--------------|-----------------|--------------|
| **SRT Reduction** | §56–66 (Part VII: T15_REDUCTIONS) | `src/services/srt_reduction.py` | `test_srt_reduction.py` | (Implicit in T15 contracts) | (Part of T15 system) |
| **Biophilia Reduction** | §74–75 (Part VIII) | `src/services/biophilia_reduction.py` | `test_biophilia_reduction.py` | (Implicit in template library) | PANEL_D_VISION_ATTRIBUTES_2026-03-01.md |
| **ART Reduction** | §75–76 (Part VIII) | `src/services/art_reduction.py` | `test_art_reduction.py` | (Implicit in template library) | PANEL_D_VISION_ATTRIBUTES_2026-03-01.md |
| **Belief-Env-Outcome Extractor** | §45–47 (Part IV) | `src/extraction/belief_env_outcome_extractor.py` | `test_belief_env_outcome_extractor.py` | (Implicit in extraction templates) | PANEL_A_SCHEMA_REVIEW_2026-03-01.md |
| **Direction Expectation** | §49–51 (Part IV) | `src/services/direction_expectation.py` | `test_direction_expectation.py` | (Implicit in bridge warrant contracts) | (Part of warrant assignment) |
| **Scope Extractor** | §35–42 (Part VI) | `src/extraction/scope_extractor.py`, `src/extraction/scope_renderer.py` | `test_scope_extractor.py`, `test_scope_renderer.py` | (Implicit in extraction templates) | (Part of extraction pipeline) |

---

## DOMAIN 14: MONITORING & SYSTEM HEALTH

### Health Checks, Monitoring, and Diagnostics

| Concept | Master Doc Section(s) | Core Code File(s) | Test File(s) | Contract/Schema | Panel Review |
|---------|----------------------|-------------------|--------------|-----------------|--------------|
| **System Health** | §141 (Part XVII implied) | `src/monitoring/system_health_monitor.py`, `src/monitoring/compute_system_health.py`, `src/qa/pipeline_monitor.py` | `test_compute_system_health.py`, `test_pipeline_logging.py`, `test_pipeline_integrity.py` | `contracts/SUBSYSTEM_HEALTH_CONTRACTS.md` | PANEL_INFRA_DECISIONS_LOG.md |
| **Web of Belief Health** | §84–89 (Part IX) | `src/epistemic/web_of_belief_health_baseline_runner.py` | `test_web_of_belief_health_baseline_runner.py` | (Implicit in web state contracts) | PANEL_COHERENCE_THRESHOLDS_2026-03-02.md |
| **Entrenchment Tracker** | §49.1–49.3 (Part IV), §127–130 (Part XVII) | `src/epistemic/entrenchment_tracker.py` | `test_entrenchment_tracker.py`, `test_entrenchment_replay_safe.py` | (Implicit in web state schema) | PANEL_INFRA_DECISIONS_LOG.md |
| **Reachability Audit** | §128–130 (Part XVII) | `src/qa/reachability_audit.py` | `test_reachability_audit.py` | (Implicit in auditing contracts) | (Part of QA infrastructure) |

---

## DOMAIN 15: EXPORT & REPORTING

### Output Formats, Reporting, and Distribution

| Concept | Master Doc Section(s) | Core Code File(s) | Test File(s) | Contract/Schema | Panel Review |
|---------|----------------------|-------------------|--------------|-----------------|--------------|
| **Export Formats** | §141 (Part XVII implied) | `src/export/export_formats.py`, `src/export/export_bundles.py` | `test_export_formats.py`, `test_export_bundles.py` | (Implicit in export contracts) | (Part of infrastructure) |
| **Export Checklists** | §141 (Part XVII implied) | `src/export/export_checklist.py` | `test_export_checklists.py` | (Implicit in QA contracts) | (Part of QA infrastructure) |
| **Report Generator** | §141 (Part XVII implied) | `src/reporting/report_generator.py`, `src/cmr/architect_report.py` | `test_report_generator.py`, `test_architect_report.py` | (Implicit in reporting contracts) | (Part of reporting standards) |
| **Answer Renderer** | §58–66 (Part VII) | `src/qa/answer_renderer.py` | `test_answer_renderer.py` | `contracts/ae_af/schemas/ae.query_response.v1.schema.json` | (Part of API contracts) |
| **Bibtex Generator** | §11–15 (Part I implied) | `src/ingestion/bibtex_generator.py` | `test_bibtex_generator.py` | (JSON to BibTeX export) | (Part of export infrastructure) |

---

## DOMAIN 16: EXPERIMENTAL & EXPLORATORY

### Cutting-Edge Features and Research Prototypes

| Concept | Master Doc Section(s) | Core Code File(s) | Test File(s) | Contract/Schema | Panel Review |
|---------|----------------------|-------------------|--------------|-----------------|--------------|
| **CVA (Core-Vulnerability-Attractor)** | (Research prototype; see sprint docs) | `src/experimental/cva_engine.py`, `src/experimental/cva_attractor.py`, `src/experimental/cva_models.py` | `test_cva_attractor.py`, `test_cva_e2e.py`, `test_cva_engines.py`, `test_cva_post_remediation.py`, `test_cva_three_hard_problems.py` | (Implicit in experimental contracts) | (Part of advanced research) |
| **Relational Analysis** | §128–130 (Part XVII) | `src/analysis/relational_analysis.py` | `test_relational_analysis.py` | `contracts/relational_analysis.contract.md` | PANEL_DELIBERATION_NOTES_2026-03-02.md |
| **Recommendation Loop** | (Feature development) | `src/services/recommendation_loop.py` | `test_recommendation_loop.py` | (Implicit in service contracts) | (Part of user experience) |
| **VOI Collector** | §52–53 (Part IV) | `src/services/voi_collector.py` | `test_research_queue_collectors.py` | `contracts/voi_collector.contract.md` | (Part of research planning) |
| **Research Opportunity Registry** | (Feature development) | `src/services/research_opportunity_registry.py` | `test_research_opportunity_registry.py` | (Implicit in VOI contracts) | (Part of research strategy) |

---

## CROSS-CUTTING CONCERNS

### Architectural Patterns and Shared Infrastructure

| Concept | Master Doc Section(s) | Core Code File(s) | Test File(s) | Contract/Schema | Panel Review |
|---------|----------------------|-------------------|--------------|-----------------|--------------|
| **Pipeline Registry** | §141 (Part XVII implied) | `src/infrastructure/pipeline_registry.py` | `test_pipeline_registry.py` | (Implicit in infrastructure contracts) | PANEL_INFRA_DECISIONS_LOG.md |
| **Logging Configuration** | (§141 implied) | `src/infrastructure/logging_config.py` | `test_logging_config.py` | (Implicit in infrastructure contracts) | (Part of DevOps) |
| **Database Locator** | §141 (Part XVII implied) | `src/infrastructure/db_locator.py`, `src/infrastructure/db_path_contracts.py` | `test_db_locator.py`, `test_db_path_contracts.py` | (Implicit in infrastructure contracts) | PANEL_INFRA_DECISIONS_LOG.md |
| **Feedback Store** | §141 (Part XVII implied) | `src/services/feedback_store.py` | `test_feedback_store.py` | (Implicit in service contracts) | (Part of user feedback) |
| **Main Wiring** | (§141 implied) | `src/main.py`, `src/infrastructure/main_wiring.py` | `test_main_wiring.py` | (Implicit in architecture contracts) | PANEL_INFRA_DECISIONS_LOG.md |
| **Cross-Boundary Contracts** | §141 (Part XVII implied) | (Implicit in all modules) | `test_cross_boundary_contracts.py` | `contracts/ae_af/README.md`, `contracts/ae_af/CLAUDE_HANDOFF_PROMPT.md` | (Part of API contracts) |
| **Governance & Architecture** | §115–126 (Part XI: ARCH_TYPOLOGY) | (Implicit in all modules) | `test_governance_sanity.py`, `test_enum_consistency.py`, `test_function_signatures.py` | (Implicit in all contracts) | PANEL_IMPLEMENTATION_2026-03-01.md |

---

## APPENDIX: SECTION NUMBER RANGES

Quick reference for finding concepts by master doc section:

| Sections | Topic | Part |
|----------|-------|------|
| 1–10 | Introduction, scope, and motivation | Frontmatter & Part I |
| 11–27 | Conceptual foundations and theoretical grounding | Parts II–III |
| 28–53 | Credence calculus, warrants, and epistemic projection | Part IV |
| 54–81 | Causal reasoning, reduction, and IE-DPT | Parts V–VIII |
| 82–90 | Web of belief architecture and operationalization | Part IX |
| 91–114 | Template library and domain panels | Parts X |
| 115–126 | Architectural typology and card system | Part XI |
| 127–142 | Meta-epistemology, oversight, and system governance | Parts XVI–XVII |
| 143–150 | Infrastructure, contracts, and limitations | Parts XVIII–XIX |
| 151–200 | Applications, extensions, and future work | Parts XIV–XXI |

---

## APPENDIX: KEY FILE GROUPS

### Epistemic Core (Web of Belief)
- `src/epistemic/web_of_belief.py` — Main state machine
- `src/epistemic/credence_interval.py` — Confidence representation
- `src/epistemic/coherence_engine.py` — Holistic belief networks
- Tests: `test_web_of_belief.py`, `test_credence_intervals.py`, `test_scalable_coherence.py`

### Extraction & Templates
- `src/extraction/v4_extractor.py` — Main pipeline
- `src/templates/template_registry.py` — Library access
- `src/services/finding_template_service.py` — Finding matching
- Tests: `test_sprint4_extraction.py`, `test_template_record.py`, `test_finding_template_fixes.py`

### QA & Success Conditions
- `src/qa/overseer.py` — Quality gate orchestrator
- `src/qa/success_conditions_orchestrator.py` — Outcome validation
- `src/qa/nightly_pipeline.py` — Continuous monitoring
- Tests: `test_overseer_inv4.py`, `test_success_conditions.py`, `test_nightly_qa_quality_gate.py`

### API & Integration
- `src/api/query_routes.py` — Question-answering endpoint
- `src/api/causal_routes.py` — Causal inference endpoint
- `src/cli/query.py` — Command-line interface
- Tests: `test_query_routes.py`, `test_api_causal.py`, `test_cli_web_flags.py`

---

## APPENDIX: DECISION REFERENCES

Key architectural decisions documented in panel reviews:

| Decision | Panel Review | Location |
|----------|--------------|----------|
| Transfer Reliability values (d) | PANEL_CALIBRATION_REVIEW_2026-03-02.md | §48.1a |
| Success condition thresholds | PANEL_B_QUALITY_THRESHOLDS_2026-03-01.md | §131–137 |
| Card type definitions | PANEL_IMPLEMENTATION_2026-03-01.md | §115–126 |
| Outcome vocabulary mapping | PANEL_D_VISION_ATTRIBUTES_2026-03-01.md | §103–105 |
| IE-DPT modulation parameters | PANEL_C_THEORY_MOLECULE_2026-03-01.md | §67–71 |
| Entrenchment calculation | PANEL_INFRA_DECISIONS_LOG.md | §49.1–49.3 |
| Coherence thresholds | PANEL_COHERENCE_THRESHOLDS_2026-03-02.md | §49.5–49.6 |
| Warrant justification rules | PANEL_JUSTIFICATION_PROVENANCE_2026-03-02.md | §128–130 |

---

## END OF APPENDIX

This cross-reference index is maintained as part of the master doc. For updates, corrections, or additions, see the MASTER_DOC_UPDATE_PROTOCOL in `/contracts/`.
