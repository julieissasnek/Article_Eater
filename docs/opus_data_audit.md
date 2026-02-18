
================================================================================
## PART 1: CSV STRUCTURE AND SAMPLES
================================================================================

**CSV Path:** `data/production/realtime_pdf_confirmed_rows.csv`
**CSV Size:** 154.8 MB
**Columns (74):** ['paper_id', 'claim_id', 'claim_type', 'node_id', 'statement', 'ae_confidence', 'node_type', 'article_type_family', 'template_version', 'environment_variable', 'outcome_variable', 'environment_candidates', 'outcome_candidates', 'environment_canonical_id', 'outcome_canonical_id', 'environment_resolution_confidence', 'outcome_resolution_confidence', 'environment_resolution_match_type', 'outcome_resolution_match_type', 'environment_node_id', 'outcome_node_id', 'effect_direction', 'edge_id', 'edge_type', 'source_node_id', 'target_node_id', 'weight', 'evidence_basis', 'needs_verification', 'justification', 'relation_type_hint', 'relation_strength_hint', 'relation_provenance_hint', 'argument_relation_type', 'causal_level', 'argument_scheme', 'theory_name', 'target_paper_id', 'citation_text', 'citation_doi', 'citation_context', 'citation_match_confidence', 'citation_match_type', 'source_section', 'source_page_start', 'source_page_end', 'source_quote', 'source_quote_hash', 'source_table_id', 'source_table_row', 'quality_flag', 'source', 'evidence_level', 'provenance_tier', 'requires_pdf_confirmation', 'source_zone', 'extraction_difficulty', 'processed_at', 'article_type_classifier_version', 'article_type_confidence', 'article_type_diagnostics', 'article_type_margin', 'article_type_needs_review', 'article_type_predicted_family', 'article_type_runner_up', 'article_type_signals', 'confidence', 'content', 'argument_relation', 'translation_status', 'translation_confidence', 'translation_warnings', 'environment_candidate_scores', 'outcome_candidate_scores']

**Rows scanned:** 10000
**Unique environment_variable values found:** 38
**Unique outcome_variable values found:** 39
**Unique evidence types found:** 0

### All unique environment_variable values (from first 10k rows)

  - `appendix figurea1 samplephotoofroomwithhighsalience`
  - `blu`
  - `blue`
  - `ceiling height`
  - `common value s5a`
  - `csihpipless aobrsdtrera csttrbuicotluorge`
  - `developed expressive-sensorial atlas`
  - `deviation contributors temperature`
  - `dirty`
  - `ffititttiningg thhee sseennssoorrss`
  - `fitting sensors rest`
  - `francesca ostuzzi design`
  - `francesca ostuzzi her`
  - `francesca ostuzzi politecnico`
  - `francesca ostuzzi processes`
  - `francesca ostuzzi started`
  - `francesca ostuzzi technologies`
  - `green light`
  - `half-life half-life`
  - `indicators`
  - `instruction`
  - `interests include teaching`
  - `ivory mango yel`
  - `material tactile experiment`
  - `meanings materials`
  - `politecnico milano her`
  - `pure white chocolate`
  - `pure white lightgray`
  - `pure white mango`
  - `pure white ruby`
  - `pure white yellow`
  - `sample suburban development`
  - `table1 iveigrouppresencequestionnaireresults inthevr-generatedworld`
  - `table1 iveigrouppresencequestionnaireresults questionsonsenseofpresence`
  - `ttaacctitliele exxppeerirmimenentt dduummmmyy`
  - `visualproperties auditoryproperties`
  - `visualproperties olfactory properties`
  - `visualproperties tactual properties`

### All unique outcome_variable values (from first 10k rows)

  - `appendix figurea1 samplephotoofroomwithhighsalience`
  - `attributing meanings materials`
  - `become old dirty`
  - `common indicators criterion`
  - `common value s5a`
  - `csihpipless aobrsdtrera csttrbuicotluorge`
  - `developed expressive-sensorial atlas`
  - `ffititttiningg thhee sseennssoorrss`
  - `fitting sensors rest`
  - `francesca ostuzzi design`
  - `francesca ostuzzi her`
  - `francesca ostuzzi politecnico`
  - `francesca ostuzzi processes`
  - `francesca ostuzzi started`
  - `francesca ostuzzi technologies`
  - `half-life half-life`
  - `ice blue mango`
  - `instruction instruction open`
  - `instruction instruction return`
  - `interests include teaching`
  - `ite green light`
  - `ivory mango yel`
  - `material tactile experiment`
  - `politecnico milano her`
  - `productivity`
  - `pure white blu`
  - `pure white chocolate`
  - `pure white lightgray`
  - `pure white mango`
  - `pure white ruby`
  - `pure white yellow`
  - `sample suburban development`
  - `table1 iveigrouppresencequestionnaireresults inthevr-generatedworld`
  - `table1 iveigrouppresencequestionnaireresults questionsonsenseofpresence`
  - `ttaacctitliele exxppeerirmimenentt dduummmmyy`
  - `visualproperties auditoryproperties`
  - `visualproperties olfactory properties`
  - `visualproperties tactual properties`
  - `well-being`

### All unique evidence types (from first 10k rows)


### SAMPLE: 20 STRUCTURED rows (environment_variable present)


**Row 1:**
  paper_id: doi:10.3390/ijerph7031036
  claim_id: doi:10.3390/ijerph7031036-TBL-C001
  claim_type: finding
  statement: b1 = 0.1626 b2 = 0.3428 b3 =-0.1387 x = 101.3 Half-life : Half-life 
  node_type: EMPIRICAL_FINDING
  article_type_family: unknown
  environment_variable: half-life half-life
  outcome_variable: half-life half-life
  environment_candidates: ['half-life half-life']
  outcome_candidates: ['half-life half-life']
  environment_canonical_id: env.inferred.design_factor
  outcome_canonical_id: out.inferred.general
  environment_resolution_confidence: 0.25
  outcome_resolution_confidence: 0.25
  environment_resolution_match_type: domain_inferred
  outcome_resolution_match_type: domain_inferred
  environment_node_id: env.unresolved.half_life_half_life
  outcome_node_id: out.unresolved.half_life_half_life
  effect_direction: positive
  edge_type: COHERENCE_SUPPORT
  needs_verification: true
  relation_type_hint: explains
  relation_strength_hint: 0.4
  relation_provenance_hint: argument:default_contextual
  argument_relation_type: table_claim
  source_section: table
  source_page_start: 8
  source_page_end: 8
  source_quote: b1 = 0.1626 b2 = 0.3428 b3 =-0.1387 x = 101.3 Half-life : Half-life 
  source_quote_hash: cea6d1b8309ac09d
  source_table_id: TBL-20260214092226-002
  source_table_row: 0
  quality_flag: ok
  source: codex_pdfplumber
  evidence_level: pdf_table_extracted
  provenance_tier: pdf_confirmed
  requires_pdf_confirmation: no
  processed_at: 2026-02-14T08:22:27.720014+00:00
  article_type_classifier_version: paper_classifier_v2
  article_type_confidence: 0.5455
  article_type_diagnostics: downgraded_to_unknown_low_confidence
  article_type_margin: 1.5000
  article_type_needs_review: true
  article_type_predicted_family: empirical_v2
  article_type_runner_up: observational_field
  article_type_signals: section:results
  confidence: 0.6
  content: b1 = 0.1626
b2 = 0.3428
b3 =-0.1387
x = 101.3
Half-life : Half-life 
  argument_relation: explains
  translation_status: inferred
  translation_confidence: 0.45

**Row 2:**
  paper_id: doi:10.3390/ijerph7031036
  claim_id: doi:10.3390/ijerph7031036-TBL-C002
  claim_type: finding
  statement: b1 = 0.2054 b2 = 0.3071 b3 =-0.1185 x = 159.8 Half-life : Half-life 
  node_type: EMPIRICAL_FINDING
  article_type_family: unknown
  environment_variable: half-life half-life
  outcome_variable: half-life half-life
  environment_candidates: ['half-life half-life']
  outcome_candidates: ['half-life half-life']
  environment_canonical_id: env.inferred.design_factor
  outcome_canonical_id: out.inferred.general
  environment_resolution_confidence: 0.25
  outcome_resolution_confidence: 0.25
  environment_resolution_match_type: domain_inferred
  outcome_resolution_match_type: domain_inferred
  environment_node_id: env.unresolved.half_life_half_life
  outcome_node_id: out.unresolved.half_life_half_life
  effect_direction: positive
  edge_type: COHERENCE_SUPPORT
  needs_verification: true
  relation_type_hint: explains
  relation_strength_hint: 0.4
  relation_provenance_hint: argument:default_contextual
  argument_relation_type: table_claim
  source_section: table
  source_page_start: 8
  source_page_end: 8
  source_quote: b1 = 0.2054 b2 = 0.3071 b3 =-0.1185 x = 159.8 Half-life : Half-life 
  source_quote_hash: 9b98e5ea574ee785
  source_table_id: TBL-20260214092226-003
  source_table_row: 0
  quality_flag: ok
  source: codex_pdfplumber
  evidence_level: pdf_table_extracted
  provenance_tier: pdf_confirmed
  requires_pdf_confirmation: no
  processed_at: 2026-02-14T08:22:28.160451+00:00
  article_type_classifier_version: paper_classifier_v2
  article_type_confidence: 0.5455
  article_type_diagnostics: downgraded_to_unknown_low_confidence
  article_type_margin: 1.5000
  article_type_needs_review: true
  article_type_predicted_family: empirical_v2
  article_type_runner_up: observational_field
  article_type_signals: section:results
  confidence: 0.6
  content: b1 = 0.2054
b2 = 0.3071
b3 =-0.1185
x = 159.8
Half-life : Half-life 
  argument_relation: explains
  translation_status: inferred
  translation_confidence: 0.45

**Row 3:**
  paper_id: doi:10.3390/ijerph7031036
  claim_id: doi:10.3390/ijerph7031036-TBL-C003
  claim_type: finding
  statement: b1 = 0.1822 b2 = 0.3366 b3 =-0.1394 x = 111.4 Half-life : Half-life 
  node_type: EMPIRICAL_FINDING
  article_type_family: unknown
  environment_variable: half-life half-life
  outcome_variable: half-life half-life
  environment_candidates: ['half-life half-life']
  outcome_candidates: ['half-life half-life']
  environment_canonical_id: env.inferred.design_factor
  outcome_canonical_id: out.inferred.general
  environment_resolution_confidence: 0.25
  outcome_resolution_confidence: 0.25
  environment_resolution_match_type: domain_inferred
  outcome_resolution_match_type: domain_inferred
  environment_node_id: env.unresolved.half_life_half_life
  outcome_node_id: out.unresolved.half_life_half_life
  effect_direction: positive
  edge_type: COHERENCE_SUPPORT
  needs_verification: true
  relation_type_hint: explains
  relation_strength_hint: 0.4
  relation_provenance_hint: argument:default_contextual
  argument_relation_type: table_claim
  source_section: table
  source_page_start: 8
  source_page_end: 8
  source_quote: b1 = 0.1822 b2 = 0.3366 b3 =-0.1394 x = 111.4 Half-life : Half-life 
  source_quote_hash: d963b83c3a05b787
  source_table_id: TBL-20260214092226-004
  source_table_row: 0
  quality_flag: ok
  source: codex_pdfplumber
  evidence_level: pdf_table_extracted
  provenance_tier: pdf_confirmed
  requires_pdf_confirmation: no
  processed_at: 2026-02-14T08:22:28.904379+00:00
  article_type_classifier_version: paper_classifier_v2
  article_type_confidence: 0.5455
  article_type_diagnostics: downgraded_to_unknown_low_confidence
  article_type_margin: 1.5000
  article_type_needs_review: true
  article_type_predicted_family: empirical_v2
  article_type_runner_up: observational_field
  article_type_signals: section:results
  confidence: 0.6
  content: b1 = 0.1822
b2 = 0.3366
b3 =-0.1394
x = 111.4
Half-life : Half-life 
  argument_relation: explains
  translation_status: inferred
  translation_confidence: 0.45

**Row 4:**
  paper_id: doi:10.3390/ijerph7031036
  claim_id: doi:10.3390/ijerph7031036-TBL-C004
  claim_type: finding
  statement: b1 = 0.1607 b2 = 0.3551 b3 =-0.1111 x = 121.3 Half-life : Half-life 
  node_type: EMPIRICAL_FINDING
  article_type_family: unknown
  environment_variable: half-life half-life
  outcome_variable: half-life half-life
  environment_candidates: ['half-life half-life']
  outcome_candidates: ['half-life half-life']
  environment_canonical_id: env.inferred.design_factor
  outcome_canonical_id: out.inferred.general
  environment_resolution_confidence: 0.25
  outcome_resolution_confidence: 0.25
  environment_resolution_match_type: domain_inferred
  outcome_resolution_match_type: domain_inferred
  environment_node_id: env.unresolved.half_life_half_life
  outcome_node_id: out.unresolved.half_life_half_life
  effect_direction: positive
  edge_type: COHERENCE_SUPPORT
  needs_verification: true
  relation_type_hint: explains
  relation_strength_hint: 0.4
  relation_provenance_hint: argument:default_contextual
  argument_relation_type: table_claim
  source_section: table
  source_page_start: 8
  source_page_end: 8
  source_quote: b1 = 0.1607 b2 = 0.3551 b3 =-0.1111 x = 121.3 Half-life : Half-life 
  source_quote_hash: 24fdaf7ea4abf7bd
  source_table_id: TBL-20260214092226-005
  source_table_row: 0
  quality_flag: ok
  source: codex_pdfplumber
  evidence_level: pdf_table_extracted
  provenance_tier: pdf_confirmed
  requires_pdf_confirmation: no
  processed_at: 2026-02-14T08:22:29.714093+00:00
  article_type_classifier_version: paper_classifier_v2
  article_type_confidence: 0.5455
  article_type_diagnostics: downgraded_to_unknown_low_confidence
  article_type_margin: 1.5000
  article_type_needs_review: true
  article_type_predicted_family: empirical_v2
  article_type_runner_up: observational_field
  article_type_signals: section:results
  confidence: 0.6
  content: b1 = 0.1607
b2 = 0.3551
b3 =-0.1111
x = 121.3
Half-life : Half-life 
  argument_relation: explains
  translation_status: inferred
  translation_confidence: 0.45

**Row 5:**
  paper_id: doi:10.20944/preprints201907.0323.v1
  claim_id: doi:10.20944/preprints201907.0323.v1-TBL-C001
  claim_type: finding
  statement: Deviation Contributors: Temperature (Chua et al., 2006; Fang et al., 2004; Kamaruzzaman and Sabrani, 2011; Seppanen, Fisk and Lei, 2006; Wargocki et al., 2006).; Direct Mental Effects: Lowering the rate of performance and productivity. Distraction
  node_type: EMPIRICAL_FINDING
  article_type_family: unknown
  environment_variable: deviation contributors temperature
  outcome_variable: productivity
  environment_candidates: ['deviation contributors temperature']
  outcome_candidates: ['productivity']
  environment_canonical_id: env.generic.thermal
  outcome_canonical_id: behav.productivity
  environment_resolution_confidence: 0.35
  outcome_resolution_confidence: 1.0
  environment_resolution_match_type: generic_keyword
  outcome_resolution_match_type: exact
  environment_node_id: env.generic.thermal
  outcome_node_id: out.behav.productivity
  effect_direction: negative
  edge_type: DISCONFIRMS_PREDICTION
  needs_verification: true
  relation_type_hint: contradicts
  relation_strength_hint: 0.62
  relation_provenance_hint: argument:negative_direction_effect
  argument_relation_type: table_claim
  source_section: table
  source_page_start: 10
  source_page_end: 10
  source_quote: Deviation Contributors: Temperature (Chua et al., 2006; Fang et al., 2004; Kamaruzzaman and Sabrani, 2011; Seppanen, Fisk and Lei, 2006; Wargocki et al., 2006).; Direct Mental Effects: Lowering the rate of performance and productivity. Distraction
  source_quote_hash: 89b70c6aca6f7c40
  source_table_id: TBL-20260214092258-001
  source_table_row: 0
  quality_flag: ok
  source: codex_pdfplumber
  evidence_level: pdf_table_extracted
  provenance_tier: pdf_confirmed
  requires_pdf_confirmation: no
  processed_at: 2026-02-14T08:23:05.809658+00:00
  article_type_classifier_version: paper_classifier_v2
  article_type_confidence: 0.4545
  article_type_diagnostics: downgraded_to_unknown_low_confidence
  article_type_margin: 0.5000
  article_type_needs_review: true
  article_type_predicted_family: narrative_review
  article_type_runner_up: empirical_v2
  article_type_signals: title_pattern:(?<!systematic\s)review(?!\s+of\s+the\s+literature)
  confidence: 0.6
  content: Deviation Contributors: Temperature
(Chua et al., 2006; Fang et al., 2004;
Kamaruzzaman and Sabrani, 2011;
Seppanen, Fisk and Lei, 2006;
Wargocki et al., 2006).; Direct Mental Effects: Lowering the rate of performance and
productivity.
Distraction
  argument_relation: contradicts
  translation_status: inferred
  translation_confidence: 0.45

**Row 6:**
  paper_id: sha256:bae8d5930451
  claim_id: sha256:bae8d5930451-TBL-C001
  claim_type: effect
  statement: : showed effect size of 2004.00 (r) on T hereappearstobewidespreadbeliefthatceilingheight can affect the quality of indoor consumption experi- ences. Fischl and Ga¨rling (2004) found that ceiling height ranked among the top three architectural details that influ- enced consumers’ psychological well-...
  node_type: EMPIRICAL_FINDING
  article_type_family: unknown
  environment_variable: ceiling height
  outcome_variable: well-being
  environment_candidates: ['ceiling height']
  outcome_candidates: ['well-being', 'health']
  environment_canonical_id: env.v1_090.ceiling_height
  outcome_canonical_id: health.wellbeing
  environment_resolution_confidence: 1.0
  outcome_resolution_confidence: 1.0
  environment_resolution_match_type: exact
  outcome_resolution_match_type: exact
  environment_node_id: env.v1_090.ceiling_height
  outcome_node_id: out.health.wellbeing
  effect_direction: positive
  edge_type: CONFIRMS_PREDICTION
  needs_verification: true
  relation_type_hint: supports
  relation_strength_hint: 0.52
  relation_provenance_hint: argument:verify_or_test
  argument_relation_type: table_claim
  source_section: table
  source_page_start: 1
  source_page_end: 1
  source_quote: : showed effect size of 2004.00 (r) on T hereappearstobewidespreadbeliefthatceilingheight can affect the quality of indoor consumption experi- ences. Fischl and Ga¨rling (2004) found that ceiling height ranked among the top three architectural details that influ- enced consumers’ psychological well-...
  source_quote_hash: 8e68a61353f1c4fc
  source_table_id: TBL-20260214092318-001
  source_table_row: 0
  quality_flag: ok
  source: codex_pdfplumber
  evidence_level: pdf_table_extracted
  provenance_tier: pdf_confirmed
  requires_pdf_confirmation: no
  processed_at: 2026-02-14T08:23:21.827426+00:00
  article_type_classifier_version: paper_classifier_v2
  article_type_confidence: 0.0000
  article_type_diagnostics: downgraded_to_unknown_low_confidence
  article_type_margin: 0.0000
  article_type_needs_review: true
  article_type_predicted_family: unknown
  article_type_runner_up: theoretical
  confidence: 0.7
  content: : showed effect size of 2004.00 (r) on T
hereappearstobewidespreadbeliefthatceilingheight
can affect the quality of indoor consumption experi-
ences. Fischl and Ga¨rling (2004) found that ceiling height
ranked among the top three architectural details that influ-
enced consumers’ psychological well-...
  argument_relation: supports
  translation_status: exact
  translation_confidence: 0.95

**Row 7:**
  paper_id: sha256:bae8d5930451
  claim_id: sha256:bae8d5930451-TBL-C002
  claim_type: finding
  statement: APPENDIX A FIGUREA1 SAMPLEPHOTOOFROOMWITHHIGHSALIENCE, HIGHCEILINGHEIGHT: APPENDIX C FIGUREC1 SAMPLEPRODUCT(COFFEE-TABLE)USEDINEXPERIMENT2
  node_type: EMPIRICAL_FINDING
  article_type_family: unknown
  environment_variable: appendix figurea1 samplephotoofroomwithhighsalience
  outcome_variable: appendix figurea1 samplephotoofroomwithhighsalience
  environment_candidates: ['appendix figurea1 samplephotoofroomwithhighsalience']
  outcome_candidates: ['appendix figurea1 samplephotoofroomwithhighsalience']
  environment_canonical_id: env.generic.spatial_layout
  outcome_canonical_id: out.inferred.general
  environment_resolution_confidence: 0.35
  outcome_resolution_confidence: 0.25
  environment_resolution_match_type: generic_keyword
  outcome_resolution_match_type: domain_inferred
  environment_node_id: env.generic.spatial_layout
  outcome_node_id: out.unresolved.appendix_figurea1_samplephotoofroomwithhighsalience
  effect_direction: positive
  edge_type: COHERENCE_SUPPORT
  needs_verification: true
  relation_type_hint: explains
  relation_strength_hint: 0.4
  relation_provenance_hint: argument:default_contextual
  argument_relation_type: table_claim
  source_section: table
  source_page_start: 12
  source_page_end: 12
  source_quote: APPENDIX A FIGUREA1 SAMPLEPHOTOOFROOMWITHHIGHSALIENCE, HIGHCEILINGHEIGHT: APPENDIX C FIGUREC1 SAMPLEPRODUCT(COFFEE-TABLE)USEDINEXPERIMENT2
  source_quote_hash: 814a9f337f56402d
  source_table_id: TBL-20260214092321-005
  source_table_row: 0
  quality_flag: ok
  source: codex_pdfplumber
  evidence_level: pdf_table_extracted
  provenance_tier: pdf_confirmed
  requires_pdf_confirmation: no
  processed_at: 2026-02-14T08:23:22.441188+00:00
  article_type_classifier_version: paper_classifier_v2
  article_type_confidence: 0.0000
  article_type_diagnostics: downgraded_to_unknown_low_confidence
  article_type_margin: 0.0000
  article_type_needs_review: true
  article_type_predicted_family: unknown
  article_type_runner_up: theoretical
  confidence: 0.6
  content: APPENDIX A
FIGUREA1
SAMPLEPHOTOOFROOMWITHHIGHSALIENCE,
HIGHCEILINGHEIGHT: APPENDIX C
FIGUREC1
SAMPLEPRODUCT(COFFEE-TABLE)USEDINEXPERIMENT2
  argument_relation: explains
  translation_status: inferred
  translation_confidence: 0.45

**Row 8:**
  paper_id: doi:10.1111/joid.12179
  claim_id: doi:10.1111/joid.12179-TBL-C001
  claim_type: finding
  statement: Table1.IVEIgroupPresenceQuestionnaireresults: Questionsonsenseofpresence SD D N A SA; : Mean(SD)
  node_type: EMPIRICAL_FINDING
  article_type_family: unknown
  environment_variable: table1 iveigrouppresencequestionnaireresults questionsonsenseofpresence
  outcome_variable: table1 iveigrouppresencequestionnaireresults questionsonsenseofpresence
  environment_candidates: ['table1 iveigrouppresencequestionnaireresults questionsonsenseofpresence']
  outcome_candidates: ['table1 iveigrouppresencequestionnaireresults questionsonsenseofpresence']
  environment_canonical_id: env.inferred.design_factor
  outcome_canonical_id: out.inferred.general
  environment_resolution_confidence: 0.25
  outcome_resolution_confidence: 0.25
  environment_resolution_match_type: domain_inferred
  outcome_resolution_match_type: domain_inferred
  environment_node_id: env.unresolved.table1_iveigrouppresencequestionnaireresults_questionsonsenseofpresence
  outcome_node_id: out.unresolved.table1_iveigrouppresencequestionnaireresults_questionsonsenseofpresence
  effect_direction: positive
  edge_type: COHERENCE_SUPPORT
  needs_verification: true
  relation_type_hint: explains
  relation_strength_hint: 0.4
  relation_provenance_hint: argument:default_contextual
  argument_relation_type: table_claim
  source_section: table
  source_page_start: 11
  source_page_end: 11
  source_quote: Table1.IVEIgroupPresenceQuestionnaireresults: Questionsonsenseofpresence SD D N A SA; : Mean(SD)
  source_quote_hash: 090b5f8f8e8662a2
  source_table_id: TBL-20260214092339-006
  source_table_row: 0
  quality_flag: ok
  source: codex_pdfplumber
  evidence_level: pdf_table_extracted
  provenance_tier: pdf_confirmed
  requires_pdf_confirmation: no
  processed_at: 2026-02-14T08:23:40.840359+00:00
  article_type_classifier_version: paper_classifier_v2
  article_type_confidence: 0.5455
  article_type_diagnostics: downgraded_to_unknown_low_confidence
  article_type_margin: 1.5000
  article_type_needs_review: true
  article_type_predicted_family: empirical_v2
  article_type_runner_up: observational_field
  article_type_signals: section:results
  confidence: 0.6
  content: Table1.IVEIgroupPresenceQuestionnaireresults: Questionsonsenseofpresence SD D N A SA; : Mean(SD)
  argument_relation: explains
  translation_status: inferred
  translation_confidence: 0.45

**Row 9:**
  paper_id: doi:10.1111/joid.12179
  claim_id: doi:10.1111/joid.12179-TBL-C002
  claim_type: finding
  statement: Table1.IVEIgroupPresenceQuestionnaireresults: IntheVR-generatedworld,Ihadasenseof“beingthere” 2 9 6 32 6 3.56(1.01) Somehow, Ifeltthatthevirtualworldsurroundedme 1 4 4 41 5 3.82(0.77) Ihadasenseofactinginthevirtualspace,ratherthanoperatingsomethingfromoutside 1 9 15 27 5 3.40(0.89) Ifeltpresentinthe...
  node_type: EMPIRICAL_FINDING
  article_type_family: unknown
  environment_variable: table1 iveigrouppresencequestionnaireresults inthevr-generatedworld
  outcome_variable: table1 iveigrouppresencequestionnaireresults inthevr-generatedworld
  environment_candidates: ['table1 iveigrouppresencequestionnaireresults inthevr-generatedworld']
  outcome_candidates: ['table1 iveigrouppresencequestionnaireresults inthevr-generatedworld']
  environment_canonical_id: env.inferred.design_factor
  outcome_canonical_id: out.inferred.general
  environment_resolution_confidence: 0.25
  outcome_resolution_confidence: 0.25
  environment_resolution_match_type: domain_inferred
  outcome_resolution_match_type: domain_inferred
  environment_node_id: env.unresolved.table1_iveigrouppresencequestionnaireresults_inthevr_generatedworld
  outcome_node_id: out.unresolved.table1_iveigrouppresencequestionnaireresults_inthevr_generatedworld
  effect_direction: positive
  edge_type: COHERENCE_SUPPORT
  needs_verification: true
  relation_type_hint: explains
  relation_strength_hint: 0.4
  relation_provenance_hint: argument:default_contextual
  argument_relation_type: table_claim
  source_section: table
  source_page_start: 11
  source_page_end: 11
  source_quote: Table1.IVEIgroupPresenceQuestionnaireresults: IntheVR-generatedworld,Ihadasenseof“beingthere” 2 9 6 32 6 3.56(1.01) Somehow, Ifeltthatthevirtualworldsurroundedme 1 4 4 41 5 3.82(0.77) Ihadasenseofactinginthevirtualspace,ratherthanoperatingsomethingfromoutside 1 9 15 27 5 3.40(0.89) Ifeltpresentinthe...
  source_quote_hash: b94bc80b1178072f
  source_table_id: TBL-20260214092339-006
  source_table_row: 1
  quality_flag: ok
  source: codex_pdfplumber
  evidence_level: pdf_table_extracted
  provenance_tier: pdf_confirmed
  requires_pdf_confirmation: no
  processed_at: 2026-02-14T08:23:42.638377+00:00
  article_type_classifier_version: paper_classifier_v2
  article_type_confidence: 0.5455
  article_type_diagnostics: downgraded_to_unknown_low_confidence
  article_type_margin: 1.5000
  article_type_needs_review: true
  article_type_predicted_family: empirical_v2
  article_type_runner_up: observational_field
  article_type_signals: section:results
  confidence: 0.6
  content: Table1.IVEIgroupPresenceQuestionnaireresults: IntheVR-generatedworld,Ihadasenseof“beingthere” 2 9 6 32 6 3.56(1.01)
Somehow, Ifeltthatthevirtualworldsurroundedme 1 4 4 41 5 3.82(0.77)
Ihadasenseofactinginthevirtualspace,ratherthanoperatingsomethingfromoutside 1 9 15 27 5 3.40(0.89)
Ifeltpresentinthe...
  argument_relation: explains
  translation_status: inferred
  translation_confidence: 0.45

**Row 10:**
  paper_id: doi:10.1145/2079216.2079270
  claim_id: doi:10.1145/2079216.2079270-TBL-C001
  claim_type: finding
  statement: Visualproperties: Tactual properties
  node_type: EMPIRICAL_FINDING
  article_type_family: unknown
  environment_variable: visualproperties tactual properties
  outcome_variable: visualproperties tactual properties
  environment_candidates: ['visualproperties tactual properties']
  outcome_candidates: ['visualproperties tactual properties']
  environment_canonical_id: env.inferred.design_factor
  outcome_canonical_id: out.inferred.general
  environment_resolution_confidence: 0.25
  outcome_resolution_confidence: 0.25
  environment_resolution_match_type: domain_inferred
  outcome_resolution_match_type: domain_inferred
  environment_node_id: env.unresolved.visualproperties_tactual_properties
  outcome_node_id: out.unresolved.visualproperties_tactual_properties
  effect_direction: positive
  edge_type: COHERENCE_SUPPORT
  needs_verification: true
  relation_type_hint: explains
  relation_strength_hint: 0.4
  relation_provenance_hint: argument:default_contextual
  argument_relation_type: table_claim
  source_section: table
  source_page_start: 2
  source_page_end: 2
  source_quote: Visualproperties: Tactual properties
  source_quote_hash: f4382001cf99d535
  source_table_id: TBL-20260214092358-001
  source_table_row: 0
  quality_flag: ok
  source: codex_pdfplumber
  evidence_level: pdf_table_extracted
  provenance_tier: pdf_confirmed
  requires_pdf_confirmation: no
  processed_at: 2026-02-14T08:23:59.566056+00:00
  article_type_classifier_version: paper_classifier_v2
  article_type_confidence: 0.0000
  article_type_diagnostics: downgraded_to_unknown_low_confidence
  article_type_margin: 0.0000
  article_type_needs_review: true
  article_type_predicted_family: unknown
  article_type_runner_up: theoretical
  confidence: 0.6
  content: Visualproperties: Tactual properties
  argument_relation: explains
  translation_status: inferred
  translation_confidence: 0.45

**Row 11:**
  paper_id: doi:10.1145/2079216.2079270
  claim_id: doi:10.1145/2079216.2079270-TBL-C002
  claim_type: finding
  statement: Visualproperties: Auditoryproperties
  node_type: EMPIRICAL_FINDING
  article_type_family: unknown
  environment_variable: visualproperties auditoryproperties
  outcome_variable: visualproperties auditoryproperties
  environment_candidates: ['visualproperties auditoryproperties']
  outcome_candidates: ['visualproperties auditoryproperties']
  environment_canonical_id: env.inferred.design_factor
  outcome_canonical_id: out.inferred.general
  environment_resolution_confidence: 0.25
  outcome_resolution_confidence: 0.25
  environment_resolution_match_type: domain_inferred
  outcome_resolution_match_type: domain_inferred
  environment_node_id: env.unresolved.visualproperties_auditoryproperties
  outcome_node_id: out.unresolved.visualproperties_auditoryproperties
  effect_direction: positive
  edge_type: COHERENCE_SUPPORT
  needs_verification: true
  relation_type_hint: explains
  relation_strength_hint: 0.4
  relation_provenance_hint: argument:default_contextual
  argument_relation_type: table_claim
  source_section: table
  source_page_start: 2
  source_page_end: 2
  source_quote: Visualproperties: Auditoryproperties
  source_quote_hash: ea51d39aff59d40c
  source_table_id: TBL-20260214092358-001
  source_table_row: 1
  quality_flag: ok
  source: codex_pdfplumber
  evidence_level: pdf_table_extracted
  provenance_tier: pdf_confirmed
  requires_pdf_confirmation: no
  processed_at: 2026-02-14T08:23:59.885808+00:00
  article_type_classifier_version: paper_classifier_v2
  article_type_confidence: 0.0000
  article_type_diagnostics: downgraded_to_unknown_low_confidence
  article_type_margin: 0.0000
  article_type_needs_review: true
  article_type_predicted_family: unknown
  article_type_runner_up: theoretical
  confidence: 0.6
  content: Visualproperties: Auditoryproperties
  argument_relation: explains
  translation_status: inferred
  translation_confidence: 0.45

**Row 12:**
  paper_id: doi:10.1145/2079216.2079270
  claim_id: doi:10.1145/2079216.2079270-TBL-C003
  claim_type: finding
  statement: Visualproperties: Olfactory properties
  node_type: EMPIRICAL_FINDING
  article_type_family: unknown
  environment_variable: visualproperties olfactory properties
  outcome_variable: visualproperties olfactory properties
  environment_candidates: ['visualproperties olfactory properties']
  outcome_candidates: ['visualproperties olfactory properties']
  environment_canonical_id: env.inferred.design_factor
  outcome_canonical_id: out.inferred.general
  environment_resolution_confidence: 0.25
  outcome_resolution_confidence: 0.25
  environment_resolution_match_type: domain_inferred
  outcome_resolution_match_type: domain_inferred
  environment_node_id: env.unresolved.visualproperties_olfactory_properties
  outcome_node_id: out.unresolved.visualproperties_olfactory_properties
  effect_direction: positive
  edge_type: COHERENCE_SUPPORT
  needs_verification: true
  relation_type_hint: explains
  relation_strength_hint: 0.4
  relation_provenance_hint: argument:default_contextual
  argument_relation_type: table_claim
  source_section: table
  source_page_start: 2
  source_page_end: 2
  source_quote: Visualproperties: Olfactory properties
  source_quote_hash: 1c5677421b166809
  source_table_id: TBL-20260214092358-001
  source_table_row: 2
  quality_flag: ok
  source: codex_pdfplumber
  evidence_level: pdf_table_extracted
  provenance_tier: pdf_confirmed
  requires_pdf_confirmation: no
  processed_at: 2026-02-14T08:24:00.856577+00:00
  article_type_classifier_version: paper_classifier_v2
  article_type_confidence: 0.0000
  article_type_diagnostics: downgraded_to_unknown_low_confidence
  article_type_margin: 0.0000
  article_type_needs_review: true
  article_type_predicted_family: unknown
  article_type_runner_up: theoretical
  confidence: 0.6
  content: Visualproperties: Olfactory properties
  argument_relation: explains
  translation_status: inferred
  translation_confidence: 0.45

**Row 13:**
  paper_id: doi:10.3390/ijerph14070773
  claim_id: doi:10.3390/ijerph14070773-TBL-C001
  claim_type: finding
  statement: : Material 5; Tactile experiment: Dummy
  node_type: EMPIRICAL_FINDING
  article_type_family: unknown
  environment_variable: material tactile experiment
  outcome_variable: material tactile experiment
  environment_candidates: ['material tactile experiment']
  outcome_candidates: ['material tactile experiment']
  environment_canonical_id: env.inferred.design_factor
  outcome_canonical_id: out.inferred.general
  environment_resolution_confidence: 0.25
  outcome_resolution_confidence: 0.25
  environment_resolution_match_type: domain_inferred
  outcome_resolution_match_type: domain_inferred
  environment_node_id: env.unresolved.material_tactile_experiment
  outcome_node_id: out.unresolved.material_tactile_experiment
  effect_direction: positive
  edge_type: COHERENCE_SUPPORT
  needs_verification: true
  relation_type_hint: explains
  relation_strength_hint: 0.4
  relation_provenance_hint: argument:default_contextual
  argument_relation_type: table_claim
  source_section: table
  source_page_start: 4
  source_page_end: 4
  source_quote: : Material 5; Tactile experiment: Dummy
  source_quote_hash: 010c30df596eb637
  source_table_id: TBL-20260214094658-001
  source_table_row: 0
  quality_flag: ok
  source: codex_pdfplumber
  evidence_level: pdf_table_extracted
  provenance_tier: pdf_confirmed
  requires_pdf_confirmation: no
  processed_at: 2026-02-14T08:47:17.189448+00:00
  article_type_classifier_version: paper_classifier_v2
  article_type_confidence: 0.5455
  article_type_diagnostics: downgraded_to_unknown_low_confidence
  article_type_margin: 1.5000
  article_type_needs_review: true
  article_type_predicted_family: empirical_v2
  article_type_runner_up: observational_field
  article_type_signals: section:results
  confidence: 0.6
  content: : Material
5; Tactile experiment: Dummy
  argument_relation: explains
  translation_status: inferred
  translation_confidence: 0.45

**Row 14:**
  paper_id: doi:10.3390/ijerph14070773
  claim_id: doi:10.3390/ijerph14070773-TBL-C002
  claim_type: finding
  statement: Fitting the sensors: Rest (60 s)
  node_type: EMPIRICAL_FINDING
  article_type_family: unknown
  environment_variable: fitting sensors rest
  outcome_variable: fitting sensors rest
  environment_candidates: ['fitting sensors rest']
  outcome_candidates: ['fitting sensors rest']
  environment_canonical_id: env.inferred.design_factor
  outcome_canonical_id: out.inferred.general
  environment_resolution_confidence: 0.25
  outcome_resolution_confidence: 0.25
  environment_resolution_match_type: domain_inferred
  outcome_resolution_match_type: domain_inferred
  environment_node_id: env.unresolved.fitting_sensors_rest
  outcome_node_id: out.unresolved.fitting_sensors_rest
  effect_direction: positive
  edge_type: COHERENCE_SUPPORT
  needs_verification: true
  relation_type_hint: explains
  relation_strength_hint: 0.4
  relation_provenance_hint: argument:default_contextual
  argument_relation_type: table_claim
  source_section: table
  source_page_start: 4
  source_page_end: 4
  source_quote: Fitting the sensors: Rest (60 s)
  source_quote_hash: 537fef70b7d5e77c
  source_table_id: TBL-20260214094658-001
  source_table_row: 2
  quality_flag: ok
  source: codex_pdfplumber
  evidence_level: pdf_table_extracted
  provenance_tier: pdf_confirmed
  requires_pdf_confirmation: no
  processed_at: 2026-02-14T08:47:17.681082+00:00
  article_type_classifier_version: paper_classifier_v2
  article_type_confidence: 0.5455
  article_type_diagnostics: downgraded_to_unknown_low_confidence
  article_type_margin: 1.5000
  article_type_needs_review: true
  article_type_predicted_family: empirical_v2
  article_type_runner_up: observational_field
  article_type_signals: section:results
  confidence: 0.6
  content: Fitting the
sensors: Rest
(60 s)
  argument_relation: explains
  translation_status: inferred
  translation_confidence: 0.45

**Row 15:**
  paper_id: doi:10.3390/ijerph14070801
  claim_id: doi:10.3390/ijerph14070801-TBL-C001
  claim_type: finding
  statement: TTaacctitliele e exxppeerirmimenentt: DDuummmmyy
  node_type: EMPIRICAL_FINDING
  article_type_family: unknown
  environment_variable: ttaacctitliele exxppeerirmimenentt dduummmmyy
  outcome_variable: ttaacctitliele exxppeerirmimenentt dduummmmyy
  environment_candidates: ['ttaacctitliele exxppeerirmimenentt dduummmmyy']
  outcome_candidates: ['ttaacctitliele exxppeerirmimenentt dduummmmyy']
  environment_canonical_id: env.generic.daylight
  outcome_canonical_id: out.inferred.general
  environment_resolution_confidence: 0.42
  outcome_resolution_confidence: 0.25
  environment_resolution_match_type: generic_keyword
  outcome_resolution_match_type: domain_inferred
  environment_node_id: env.unresolved.ttaacctitliele_exxppeerirmimenentt_dduummmmyy
  outcome_node_id: out.unresolved.ttaacctitliele_exxppeerirmimenentt_dduummmmyy
  effect_direction: positive
  edge_type: COHERENCE_SUPPORT
  needs_verification: true
  relation_type_hint: explains
  relation_strength_hint: 0.4
  relation_provenance_hint: argument:default_contextual
  argument_relation_type: table_claim
  source_section: table
  source_page_start: 3
  source_page_end: 3
  source_quote: TTaacctitliele e exxppeerirmimenentt: DDuummmmyy
  source_quote_hash: a3bb4276bf74a29c
  source_table_id: TBL-20260214095012-001
  source_table_row: 0
  quality_flag: ok
  source: codex_pdfplumber
  evidence_level: pdf_table_extracted
  provenance_tier: pdf_confirmed
  requires_pdf_confirmation: no
  processed_at: 2026-02-14T08:50:14.790556+00:00
  article_type_classifier_version: paper_classifier_v2
  article_type_confidence: 0.5455
  article_type_diagnostics: downgraded_to_unknown_low_confidence
  article_type_margin: 1.5000
  article_type_needs_review: true
  article_type_predicted_family: empirical_v2
  article_type_runner_up: observational_field
  article_type_signals: section:results
  confidence: 0.6
  content: TTaacctitliele e exxppeerirmimenentt: DDuummmmyy
  argument_relation: explains
  translation_status: inferred
  translation_confidence: 0.45

**Row 16:**
  paper_id: doi:10.3390/ijerph14070801
  claim_id: doi:10.3390/ijerph14070801-TBL-C002
  claim_type: finding
  statement: FFititttiningg t thhee sseennssoorrss: Rest Rest (60 s) (60 s)
  node_type: EMPIRICAL_FINDING
  article_type_family: unknown
  environment_variable: ffititttiningg thhee sseennssoorrss
  outcome_variable: ffititttiningg thhee sseennssoorrss
  environment_candidates: ['ffititttiningg thhee sseennssoorrss']
  outcome_candidates: ['ffititttiningg thhee sseennssoorrss']
  environment_canonical_id: env.inferred.design_factor
  outcome_canonical_id: out.inferred.general
  environment_resolution_confidence: 0.25
  outcome_resolution_confidence: 0.25
  environment_resolution_match_type: domain_inferred
  outcome_resolution_match_type: domain_inferred
  environment_node_id: env.unresolved.ffititttiningg_thhee_sseennssoorrss
  outcome_node_id: out.unresolved.ffititttiningg_thhee_sseennssoorrss
  effect_direction: positive
  edge_type: COHERENCE_SUPPORT
  needs_verification: true
  relation_type_hint: explains
  relation_strength_hint: 0.4
  relation_provenance_hint: argument:default_contextual
  argument_relation_type: table_claim
  source_section: table
  source_page_start: 3
  source_page_end: 3
  source_quote: FFititttiningg t thhee sseennssoorrss: Rest Rest (60 s) (60 s)
  source_quote_hash: a50d0ae379201884
  source_table_id: TBL-20260214095012-001
  source_table_row: 3
  quality_flag: ok
  source: codex_pdfplumber
  evidence_level: pdf_table_extracted
  provenance_tier: pdf_confirmed
  requires_pdf_confirmation: no
  processed_at: 2026-02-14T08:50:15.122340+00:00
  article_type_classifier_version: paper_classifier_v2
  article_type_confidence: 0.5455
  article_type_diagnostics: downgraded_to_unknown_low_confidence
  article_type_margin: 1.5000
  article_type_needs_review: true
  article_type_predicted_family: empirical_v2
  article_type_runner_up: observational_field
  article_type_signals: section:results
  confidence: 0.6
  content: FFititttiningg t thhee
sseennssoorrss: Rest
Rest
(60 s)
(60 s)
  argument_relation: explains
  translation_status: inferred
  translation_confidence: 0.45

**Row 17:**
  paper_id: doi:10.3390/ijerph14070801
  claim_id: doi:10.3390/ijerph14070801-TBL-C003
  claim_type: finding
  statement: : Instruction Instruction (return hand) (return hand)
  node_type: EMPIRICAL_FINDING
  article_type_family: unknown
  environment_variable: instruction
  outcome_variable: instruction instruction return
  environment_candidates: ['instruction instruction return']
  outcome_candidates: ['instruction instruction return']
  environment_canonical_id: env.ae.hazard_indicators
  outcome_canonical_id: out.inferred.general
  environment_resolution_confidence: 0.8696
  outcome_resolution_confidence: 0.25
  environment_resolution_match_type: fuzzy
  outcome_resolution_match_type: domain_inferred
  environment_node_id: env.ae.hazard_indicators
  outcome_node_id: out.unresolved.instruction_instruction_return
  effect_direction: positive
  edge_type: COHERENCE_SUPPORT
  needs_verification: true
  relation_type_hint: explains
  relation_strength_hint: 0.4
  relation_provenance_hint: argument:default_contextual
  argument_relation_type: table_claim
  source_section: table
  source_page_start: 3
  source_page_end: 3
  source_quote: : Instruction Instruction (return hand) (return hand)
  source_quote_hash: fcbfa8684874ab6a
  source_table_id: TBL-20260214095012-002
  source_table_row: 0
  quality_flag: ok
  source: codex_pdfplumber
  evidence_level: pdf_table_extracted
  provenance_tier: pdf_confirmed
  requires_pdf_confirmation: no
  processed_at: 2026-02-14T08:50:15.336881+00:00
  article_type_classifier_version: paper_classifier_v2
  article_type_confidence: 0.5455
  article_type_diagnostics: downgraded_to_unknown_low_confidence
  article_type_margin: 1.5000
  article_type_needs_review: true
  article_type_predicted_family: empirical_v2
  article_type_runner_up: observational_field
  article_type_signals: section:results
  confidence: 0.6
  content: : Instruction
Instruction
(return hand)
(return hand)
  argument_relation: explains
  translation_status: inferred
  translation_confidence: 0.45

**Row 18:**
  paper_id: doi:10.3390/ijerph14070801
  claim_id: doi:10.3390/ijerph14070801-TBL-C004
  claim_type: finding
  statement: : Instruction Instruction (open eyes) (open eyes
  node_type: EMPIRICAL_FINDING
  article_type_family: unknown
  environment_variable: instruction
  outcome_variable: instruction instruction open
  environment_candidates: ['instruction instruction open']
  outcome_candidates: ['instruction instruction open']
  environment_canonical_id: env.ae.hazard_indicators
  outcome_canonical_id: out.inferred.general
  environment_resolution_confidence: 0.8696
  outcome_resolution_confidence: 0.25
  environment_resolution_match_type: fuzzy
  outcome_resolution_match_type: domain_inferred
  environment_node_id: env.ae.hazard_indicators
  outcome_node_id: out.unresolved.instruction_instruction_open
  effect_direction: positive
  edge_type: COHERENCE_SUPPORT
  needs_verification: true
  relation_type_hint: explains
  relation_strength_hint: 0.4
  relation_provenance_hint: argument:default_contextual
  argument_relation_type: table_claim
  source_section: table
  source_page_start: 3
  source_page_end: 3
  source_quote: : Instruction Instruction (open eyes) (open eyes
  source_quote_hash: 84028f0311c224d6
  source_table_id: TBL-20260214095012-003
  source_table_row: 0
  quality_flag: ok
  source: codex_pdfplumber
  evidence_level: pdf_table_extracted
  provenance_tier: pdf_confirmed
  requires_pdf_confirmation: no
  processed_at: 2026-02-14T08:50:15.573585+00:00
  article_type_classifier_version: paper_classifier_v2
  article_type_confidence: 0.5455
  article_type_diagnostics: downgraded_to_unknown_low_confidence
  article_type_margin: 1.5000
  article_type_needs_review: true
  article_type_predicted_family: empirical_v2
  article_type_runner_up: observational_field
  article_type_signals: section:results
  confidence: 0.6
  content: : Instruction
Instruction
(open eyes)
(open eyes
  argument_relation: explains
  translation_status: inferred
  translation_confidence: 0.45

**Row 19:**
  paper_id: doi:10.3390/buildings14040957
  claim_id: doi:10.3390/buildings14040957-TBL-C001
  claim_type: finding
  statement: Common: Indicators Criterion; χ2: - Inad; df: - dition,byscr; χ2/df: <3 utinizingthec; RMSEA: <0.10 orrelations
  node_type: EMPIRICAL_FINDING
  article_type_family: unknown
  environment_variable: indicators
  outcome_variable: common indicators criterion
  environment_candidates: ['common indicators criterion']
  outcome_candidates: ['common indicators criterion']
  environment_canonical_id: env.ae.hazard_indicators
  outcome_canonical_id: out.inferred.general
  environment_resolution_confidence: 0.7407
  outcome_resolution_confidence: 0.25
  environment_resolution_match_type: fuzzy
  outcome_resolution_match_type: domain_inferred
  environment_node_id: env.ae.hazard_indicators
  outcome_node_id: out.unresolved.common_indicators_criterion
  effect_direction: positive
  edge_type: COHERENCE_SUPPORT
  needs_verification: true
  relation_type_hint: explains
  relation_strength_hint: 0.4
  relation_provenance_hint: argument:default_contextual
  argument_relation_type: table_claim
  source_section: table
  source_page_start: 16
  source_page_end: 16
  source_quote: Common: Indicators Criterion; χ2: - Inad; df: - dition,byscr; χ2/df: <3 utinizingthec; RMSEA: <0.10 orrelations
  source_quote_hash: bce0724eba841616
  source_table_id: TBL-20260214095023-002
  source_table_row: 0
  quality_flag: ok
  source: codex_pdfplumber
  evidence_level: pdf_table_extracted
  provenance_tier: pdf_confirmed
  requires_pdf_confirmation: no
  processed_at: 2026-02-14T08:50:24.325696+00:00
  article_type_classifier_version: paper_classifier_v2
  article_type_confidence: 0.4545
  article_type_diagnostics: downgraded_to_unknown_low_confidence
  article_type_margin: 0.5000
  article_type_needs_review: true
  article_type_predicted_family: case_study
  article_type_runner_up: empirical_v2
  article_type_signals: title_pattern:case\s+study
  confidence: 0.6
  content: Common: Indicators Criterion; χ2: -
Inad; df: -
dition,byscr; χ2/df: <3
utinizingthec; RMSEA: <0.10
orrelations
  argument_relation: explains
  translation_status: inferred
  translation_confidence: 0.45

**Row 20:**
  paper_id: doi:10.3390/buildings14040957
  claim_id: doi:10.3390/buildings14040957-TBL-C002
  claim_type: finding
  statement: Common: Value; χ2: 719.73s5a tisf; df: actio3n88s tillp; χ2/df: lays1a.8p5a6r tial; RMSEA: med0i.a0t5i1n gr
  node_type: EMPIRICAL_FINDING
  article_type_family: unknown
  environment_variable: common value s5a
  outcome_variable: common value s5a
  environment_candidates: ['common value s5a']
  outcome_candidates: ['common value s5a']
  environment_canonical_id: env.inferred.design_factor
  outcome_canonical_id: out.inferred.general
  environment_resolution_confidence: 0.25
  outcome_resolution_confidence: 0.25
  environment_resolution_match_type: domain_inferred
  outcome_resolution_match_type: domain_inferred
  environment_node_id: env.unresolved.common_value_s5a
  outcome_node_id: out.unresolved.common_value_s5a
  effect_direction: positive
  edge_type: COHERENCE_SUPPORT
  needs_verification: true
  relation_type_hint: explains
  relation_strength_hint: 0.4
  relation_provenance_hint: argument:default_contextual
  argument_relation_type: table_claim
  source_section: table
  source_page_start: 16
  source_page_end: 16
  source_quote: Common: Value; χ2: 719.73s5a tisf; df: actio3n88s tillp; χ2/df: lays1a.8p5a6r tial; RMSEA: med0i.a0t5i1n gr
  source_quote_hash: 837bd68a321b90da
  source_table_id: TBL-20260214095023-002
  source_table_row: 1
  quality_flag: ok
  source: codex_pdfplumber
  evidence_level: pdf_table_extracted
  provenance_tier: pdf_confirmed
  requires_pdf_confirmation: no
  processed_at: 2026-02-14T08:50:24.558234+00:00
  article_type_classifier_version: paper_classifier_v2
  article_type_confidence: 0.4545
  article_type_diagnostics: downgraded_to_unknown_low_confidence
  article_type_margin: 0.5000
  article_type_needs_review: true
  article_type_predicted_family: case_study
  article_type_runner_up: empirical_v2
  article_type_signals: title_pattern:case\s+study
  confidence: 0.6
  content: Common: Value; χ2: 719.73s5a tisf; df: actio3n88s tillp; χ2/df: lays1a.8p5a6r tial; RMSEA: med0i.a0t5i1n gr
  argument_relation: explains
  translation_status: inferred
  translation_confidence: 0.45

### SAMPLE: 20 UNSTRUCTURED rows (no environment_variable)


**Row 1:**
  paper_id: doi:10.3389/fnhum.2017.00477
  claim_id: disc:doi:10.3389/fnhum.2017.00477:xref:ebaf48a5a8:gramannk_2017
  claim_type: inter_article_relation
  statement: GramannK(2017)Walkingthrough In recent years, advancements in neuroscientific methods have made it possible to study
  node_type: EMPIRICAL_FINDING
  article_type_family: unknown
  edge_type: INTERPRETS_AS
  needs_verification: true
  relation_type_hint: explains
  relation_strength_hint: 0.35
  argument_relation_type: mentions
  citation_text: GramannK(2017)
  citation_match_confidence: 0.0
  citation_match_type: unresolved
  source_section: introduction
  source_page_start: 1
  source_page_end: 1
  source_quote: GramannK(2017)Walkingthrough In recent years, advancements in neuroscientific methods have made it possible to study
  source_quote_hash: ebaf48a5a8e1df6c
  quality_flag: needs_citation_resolution
  source: pdf_discourse_scan
  evidence_level: pdf_discourse_extracted
  provenance_tier: pdf_confirmed
  requires_pdf_confirmation: no
  processed_at: 2026-02-14T08:21:24.854022+00:00
  article_type_classifier_version: paper_classifier_v2
  article_type_confidence: 0.4545
  article_type_diagnostics: downgraded_to_unknown_low_confidence
  article_type_margin: 0.5000
  article_type_needs_review: true
  article_type_predicted_family: thought_piece
  article_type_runner_up: empirical_v2
  article_type_signals: title_pattern:perspective
  confidence: 0.45
  content: GramannK(2017)Walkingthrough In recent years, advancements in neuroscientific methods have made it possible to study
  argument_relation: explains

**Row 2:**
  paper_id: doi:10.3389/fnhum.2017.00477
  claim_id: disc:doi:10.3389/fnhum.2017.00477:xref:20d4d9f28a:edelstein_2008
  claim_type: inter_article_relation
  statement: usingneuroscientifictools(Edelstein,2008;Nandaetal.,2013).Historically,architecturalstudies
  node_type: EMPIRICAL_FINDING
  article_type_family: unknown
  edge_type: INTERPRETS_AS
  needs_verification: true
  relation_type_hint: explains
  relation_strength_hint: 0.35
  argument_relation_type: mentions
  citation_text: Edelstein,2008
  citation_match_confidence: 0.0
  citation_match_type: unresolved
  source_section: introduction
  source_page_start: 1
  source_page_end: 1
  source_quote: usingneuroscientifictools(Edelstein,2008;Nandaetal.,2013).Historically,architecturalstudies
  source_quote_hash: 20d4d9f28a6ae0b3
  quality_flag: needs_citation_resolution
  source: pdf_discourse_scan
  evidence_level: pdf_discourse_extracted
  provenance_tier: pdf_confirmed
  requires_pdf_confirmation: no
  processed_at: 2026-02-14T08:21:24.865861+00:00
  article_type_classifier_version: paper_classifier_v2
  article_type_confidence: 0.4545
  article_type_diagnostics: downgraded_to_unknown_low_confidence
  article_type_margin: 0.5000
  article_type_needs_review: true
  article_type_predicted_family: thought_piece
  article_type_runner_up: empirical_v2
  article_type_signals: title_pattern:perspective
  confidence: 0.45
  content: usingneuroscientifictools(Edelstein,2008;Nandaetal.,2013).Historically,architecturalstudies
  argument_relation: explains

**Row 3:**
  paper_id: doi:10.3389/fnhum.2017.00477
  claim_id: disc:doi:10.3389/fnhum.2017.00477:xref:dfc3e0f36e:10.3389_fnhum
  claim_type: inter_article_relation
  statement: doi:10.3389/fnhum.2017.00477 werebasedonphilosophicalconstructsoranalysisofbehavioralpatternstorelatehumanresponses
  node_type: EMPIRICAL_FINDING
  article_type_family: unknown
  edge_type: INTERPRETS_AS
  needs_verification: true
  relation_type_hint: explains
  relation_strength_hint: 0.35
  argument_relation_type: mentions
  citation_text: 10.3389/fnhum
  citation_doi: 10.3389/fnhum
  citation_match_confidence: 0.0
  citation_match_type: unresolved
  source_section: introduction
  source_page_start: 1
  source_page_end: 1
  source_quote: doi:10.3389/fnhum.2017.00477 werebasedonphilosophicalconstructsoranalysisofbehavioralpatternstorelatehumanresponses
  source_quote_hash: dfc3e0f36ee42536
  quality_flag: needs_citation_resolution
  source: pdf_discourse_scan
  evidence_level: pdf_discourse_extracted
  provenance_tier: pdf_confirmed
  requires_pdf_confirmation: no
  processed_at: 2026-02-14T08:21:24.919273+00:00
  article_type_classifier_version: paper_classifier_v2
  article_type_confidence: 0.4545
  article_type_diagnostics: downgraded_to_unknown_low_confidence
  article_type_margin: 0.5000
  article_type_needs_review: true
  article_type_predicted_family: thought_piece
  article_type_runner_up: empirical_v2
  article_type_signals: title_pattern:perspective
  confidence: 0.45
  content: doi:10.3389/fnhum.2017.00477 werebasedonphilosophicalconstructsoranalysisofbehavioralpatternstorelatehumanresponses
  argument_relation: explains

**Row 4:**
  paper_id: doi:10.3389/fnhum.2017.00477
  claim_id: disc:doi:10.3389/fnhum.2017.00477:theory:ART:a012f181c7
  claim_type: theory_link
  statement: FrontiersinHumanNeuroscience|www.frontiersin.org 1 September2017|Volume11|Article477
  node_type: THEORETICAL_PROPOSITION
  article_type_family: unknown
  edge_type: INTERPRETS_AS
  needs_verification: true
  relation_type_hint: explains
  relation_strength_hint: 0.4
  argument_relation_type: cites
  theory_name: ART
  source_section: introduction
  source_page_start: 1
  source_page_end: 1
  source_quote: FrontiersinHumanNeuroscience|www.frontiersin.org 1 September2017|Volume11|Article477
  source_quote_hash: a012f181c7c44e2d
  quality_flag: ok
  source: pdf_discourse_scan
  evidence_level: pdf_discourse_extracted
  provenance_tier: pdf_confirmed
  requires_pdf_confirmation: no
  processed_at: 2026-02-14T08:21:24.919304+00:00
  article_type_classifier_version: paper_classifier_v2
  article_type_confidence: 0.4545
  article_type_diagnostics: downgraded_to_unknown_low_confidence
  article_type_margin: 0.5000
  article_type_needs_review: true
  article_type_predicted_family: thought_piece
  article_type_runner_up: empirical_v2
  article_type_signals: title_pattern:perspective
  confidence: 0.62
  content: FrontiersinHumanNeuroscience|www.frontiersin.org 1 September2017|Volume11|Article477
  argument_relation: explains

**Row 5:**
  paper_id: doi:10.3389/fnhum.2017.00477
  claim_id: disc:doi:10.3389/fnhum.2017.00477:xref:a012f181c7:september2017
  claim_type: inter_article_relation
  statement: FrontiersinHumanNeuroscience|www.frontiersin.org 1 September2017|Volume11|Article477
  node_type: EMPIRICAL_FINDING
  article_type_family: unknown
  edge_type: INTERPRETS_AS
  needs_verification: true
  relation_type_hint: explains
  relation_strength_hint: 0.35
  argument_relation_type: mentions
  citation_text: September2017
  citation_match_confidence: 0.0
  citation_match_type: unresolved
  source_section: introduction
  source_page_start: 1
  source_page_end: 1
  source_quote: FrontiersinHumanNeuroscience|www.frontiersin.org 1 September2017|Volume11|Article477
  source_quote_hash: a012f181c7c44e2d
  quality_flag: needs_citation_resolution
  source: pdf_discourse_scan
  evidence_level: pdf_discourse_extracted
  provenance_tier: pdf_confirmed
  requires_pdf_confirmation: no
  processed_at: 2026-02-14T08:21:24.953401+00:00
  article_type_classifier_version: paper_classifier_v2
  article_type_confidence: 0.4545
  article_type_diagnostics: downgraded_to_unknown_low_confidence
  article_type_margin: 0.5000
  article_type_needs_review: true
  article_type_predicted_family: thought_piece
  article_type_runner_up: empirical_v2
  article_type_signals: title_pattern:perspective
  confidence: 0.45
  content: FrontiersinHumanNeuroscience|www.frontiersin.org 1 September2017|Volume11|Article477
  argument_relation: explains

**Row 6:**
  paper_id: doi:10.3389/fnhum.2017.00477
  claim_id: disc:doi:10.3389/fnhum.2017.00477:xref:9fc1b3113e:edelsteinandmacagn
  claim_type: inter_article_relation
  statement: tothedesignunderinvestigation(EdelsteinandMacagno,2012, activeforshapeswithrectilinearfeatures(Nasretal.,2014),the
  node_type: EMPIRICAL_FINDING
  article_type_family: unknown
  edge_type: INTERPRETS_AS
  needs_verification: true
  relation_type_hint: explains
  relation_strength_hint: 0.35
  argument_relation_type: mentions
  citation_text: EdelsteinandMacagno,2012
  citation_match_confidence: 0.0
  citation_match_type: unresolved
  source_section: introduction
  source_page_start: 2
  source_page_end: 2
  source_quote: tothedesignunderinvestigation(EdelsteinandMacagno,2012, activeforshapeswithrectilinearfeatures(Nasretal.,2014),the
  source_quote_hash: 9fc1b3113e618dcc
  quality_flag: needs_citation_resolution
  source: pdf_discourse_scan
  evidence_level: pdf_discourse_extracted
  provenance_tier: pdf_confirmed
  requires_pdf_confirmation: no
  processed_at: 2026-02-14T08:21:25.011653+00:00
  article_type_classifier_version: paper_classifier_v2
  article_type_confidence: 0.4545
  article_type_diagnostics: downgraded_to_unknown_low_confidence
  article_type_margin: 0.5000
  article_type_needs_review: true
  article_type_predicted_family: thought_piece
  article_type_runner_up: empirical_v2
  article_type_signals: title_pattern:perspective
  confidence: 0.45
  content: tothedesignunderinvestigation(EdelsteinandMacagno,2012, activeforshapeswithrectilinearfeatures(Nasretal.,2014),the
  argument_relation: explains

**Row 7:**
  paper_id: doi:10.3389/fnhum.2017.00477
  claim_id: disc:doi:10.3389/fnhum.2017.00477:xref:932abab04a:behaviors_2013
  claim_type: inter_article_relation
  statement: they cannot clearly specify the reasons for different behaviors 2013) and the representation of object identity and location
  node_type: EMPIRICAL_FINDING
  article_type_family: unknown
  edge_type: INTERPRETS_AS
  needs_verification: true
  relation_type_hint: explains
  relation_strength_hint: 0.35
  argument_relation_type: mentions
  citation_text: behaviors 2013)
  citation_match_confidence: 0.0
  citation_match_type: unresolved
  source_section: introduction
  source_page_start: 2
  source_page_end: 2
  source_quote: they cannot clearly specify the reasons for different behaviors 2013) and the representation of object identity and location
  source_quote_hash: 932abab04a7cc092
  quality_flag: needs_citation_resolution
  source: pdf_discourse_scan
  evidence_level: pdf_discourse_extracted
  provenance_tier: pdf_confirmed
  requires_pdf_confirmation: no
  processed_at: 2026-02-14T08:21:25.029395+00:00
  article_type_classifier_version: paper_classifier_v2
  article_type_confidence: 0.4545
  article_type_diagnostics: downgraded_to_unknown_low_confidence
  article_type_margin: 0.5000
  article_type_needs_review: true
  article_type_predicted_family: thought_piece
  article_type_runner_up: empirical_v2
  article_type_signals: title_pattern:perspective
  confidence: 0.45
  content: they cannot clearly specify the reasons for different behaviors 2013) and the representation of object identity and location
  argument_relation: explains

**Row 8:**
  paper_id: doi:10.3389/fnhum.2017.00477
  claim_id: disc:doi:10.3389/fnhum.2017.00477:xref:b38b417c1f:cichy_et_al._2011
  claim_type: inter_article_relation
  statement: inbuiltenvironments.Oflate,neuroscientificstudieshavebeen (Cichy et al., 2011).
  node_type: EMPIRICAL_FINDING
  article_type_family: unknown
  edge_type: INTERPRETS_AS
  needs_verification: true
  relation_type_hint: explains
  relation_strength_hint: 0.35
  argument_relation_type: mentions
  citation_text: Cichy et al., 2011)
  citation_match_confidence: 0.0
  citation_match_type: unresolved
  source_section: introduction
  source_page_start: 2
  source_page_end: 2
  source_quote: inbuiltenvironments.Oflate,neuroscientificstudieshavebeen (Cichy et al., 2011).
  source_quote_hash: b38b417c1f2647bd
  quality_flag: needs_citation_resolution
  source: pdf_discourse_scan
  evidence_level: pdf_discourse_extracted
  provenance_tier: pdf_confirmed
  requires_pdf_confirmation: no
  processed_at: 2026-02-14T08:21:25.035901+00:00
  article_type_classifier_version: paper_classifier_v2
  article_type_confidence: 0.4545
  article_type_diagnostics: downgraded_to_unknown_low_confidence
  article_type_margin: 0.5000
  article_type_needs_review: true
  article_type_predicted_family: thought_piece
  article_type_runner_up: empirical_v2
  article_type_signals: title_pattern:perspective
  confidence: 0.45
  content: inbuiltenvironments.Oflate,neuroscientificstudieshavebeen (Cichy et al., 2011).
  argument_relation: explains

**Row 9:**
  paper_id: doi:10.3389/fnhum.2017.00477
  claim_id: disc:doi:10.3389/fnhum.2017.00477:theory:ART:7ad87aa583
  claim_type: theory_link
  statement: (Vartanianetal.,2013).Severalneuroarchitecturalstudieshave studies used a quantitative method to describe forms and their
  node_type: THEORETICAL_PROPOSITION
  article_type_family: unknown
  edge_type: INTERPRETS_AS
  needs_verification: true
  relation_type_hint: explains
  relation_strength_hint: 0.4
  argument_relation_type: cites
  theory_name: ART
  source_section: introduction
  source_page_start: 2
  source_page_end: 2
  source_quote: (Vartanianetal.,2013).Severalneuroarchitecturalstudieshave studies used a quantitative method to describe forms and their
  source_quote_hash: 7ad87aa583d36f55
  quality_flag: ok
  source: pdf_discourse_scan
  evidence_level: pdf_discourse_extracted
  provenance_tier: pdf_confirmed
  requires_pdf_confirmation: no
  processed_at: 2026-02-14T08:21:25.036016+00:00
  article_type_classifier_version: paper_classifier_v2
  article_type_confidence: 0.4545
  article_type_diagnostics: downgraded_to_unknown_low_confidence
  article_type_margin: 0.5000
  article_type_needs_review: true
  article_type_predicted_family: thought_piece
  article_type_runner_up: empirical_v2
  article_type_signals: title_pattern:perspective
  confidence: 0.62
  content: (Vartanianetal.,2013).Severalneuroarchitecturalstudieshave studies used a quantitative method to describe forms and their
  argument_relation: explains

**Row 10:**
  paper_id: doi:10.3389/fnhum.2017.00477
  claim_id: disc:doi:10.3389/fnhum.2017.00477:xref:557c2e6c34:choo_et_al._2017
  claim_type: inter_article_relation
  statement: investigated different architectural styles (Choo et al., 2017), role in architectural design.
  node_type: EMPIRICAL_FINDING
  article_type_family: unknown
  edge_type: INTERPRETS_AS
  needs_verification: true
  relation_type_hint: explains
  relation_strength_hint: 0.35
  argument_relation_type: mentions
  citation_text: Choo et al., 2017)
  citation_match_confidence: 0.0
  citation_match_type: unresolved
  source_section: introduction
  source_page_start: 2
  source_page_end: 2
  source_quote: investigated different architectural styles (Choo et al., 2017), role in architectural design.
  source_quote_hash: 557c2e6c3423a0bd
  quality_flag: needs_citation_resolution
  source: pdf_discourse_scan
  evidence_level: pdf_discourse_extracted
  provenance_tier: pdf_confirmed
  requires_pdf_confirmation: no
  processed_at: 2026-02-14T08:21:25.067492+00:00
  article_type_classifier_version: paper_classifier_v2
  article_type_confidence: 0.4545
  article_type_diagnostics: downgraded_to_unknown_low_confidence
  article_type_margin: 0.5000
  article_type_needs_review: true
  article_type_predicted_family: thought_piece
  article_type_runner_up: empirical_v2
  article_type_signals: title_pattern:perspective
  confidence: 0.45
  content: investigated different architectural styles (Choo et al., 2017), role in architectural design.
  argument_relation: explains

**Row 11:**
  paper_id: doi:10.3389/fnhum.2017.00477
  claim_id: disc:doi:10.3389/fnhum.2017.00477:theory:ART:53247ad7c3
  claim_type: theory_link
  statement: embodiment(Vecchiatoetal.,2015),contours(Vartanianetal., and curvature forms as differentiating aspects (Dazkir, 2009;
  node_type: THEORETICAL_PROPOSITION
  article_type_family: unknown
  edge_type: INTERPRETS_AS
  needs_verification: true
  relation_type_hint: explains
  relation_strength_hint: 0.4
  argument_relation_type: cites
  theory_name: ART
  source_section: introduction
  source_page_start: 2
  source_page_end: 2
  source_quote: embodiment(Vecchiatoetal.,2015),contours(Vartanianetal., and curvature forms as differentiating aspects (Dazkir, 2009;
  source_quote_hash: 53247ad7c3eca281
  quality_flag: ok
  source: pdf_discourse_scan
  evidence_level: pdf_discourse_extracted
  provenance_tier: pdf_confirmed
  requires_pdf_confirmation: no
  processed_at: 2026-02-14T08:21:25.067528+00:00
  article_type_classifier_version: paper_classifier_v2
  article_type_confidence: 0.4545
  article_type_diagnostics: downgraded_to_unknown_low_confidence
  article_type_margin: 0.5000
  article_type_needs_review: true
  article_type_predicted_family: thought_piece
  article_type_runner_up: empirical_v2
  article_type_signals: title_pattern:perspective
  confidence: 0.62
  content: embodiment(Vecchiatoetal.,2015),contours(Vartanianetal., and curvature forms as differentiating aspects (Dazkir, 2009;
  argument_relation: explains

**Row 12:**
  paper_id: doi:10.3389/fnhum.2017.00477
  claim_id: disc:doi:10.3389/fnhum.2017.00477:xref:53247ad7c3:dazkir_2009
  claim_type: inter_article_relation
  statement: embodiment(Vecchiatoetal.,2015),contours(Vartanianetal., and curvature forms as differentiating aspects (Dazkir, 2009;
  node_type: EMPIRICAL_FINDING
  article_type_family: unknown
  edge_type: INTERPRETS_AS
  needs_verification: true
  relation_type_hint: explains
  relation_strength_hint: 0.35
  argument_relation_type: mentions
  citation_text: Dazkir, 2009
  citation_match_confidence: 0.0
  citation_match_type: unresolved
  source_section: introduction
  source_page_start: 2
  source_page_end: 2
  source_quote: embodiment(Vecchiatoetal.,2015),contours(Vartanianetal., and curvature forms as differentiating aspects (Dazkir, 2009;
  source_quote_hash: 53247ad7c3eca281
  quality_flag: needs_citation_resolution
  source: pdf_discourse_scan
  evidence_level: pdf_discourse_extracted
  provenance_tier: pdf_confirmed
  requires_pdf_confirmation: no
  processed_at: 2026-02-14T08:21:25.116297+00:00
  article_type_classifier_version: paper_classifier_v2
  article_type_confidence: 0.4545
  article_type_diagnostics: downgraded_to_unknown_low_confidence
  article_type_margin: 0.5000
  article_type_needs_review: true
  article_type_predicted_family: thought_piece
  article_type_runner_up: empirical_v2
  article_type_signals: title_pattern:perspective
  confidence: 0.45
  content: embodiment(Vecchiatoetal.,2015),contours(Vartanianetal., and curvature forms as differentiating aspects (Dazkir, 2009;
  argument_relation: explains

**Row 13:**
  paper_id: doi:10.3389/fnhum.2017.00477
  claim_id: disc:doi:10.3389/fnhum.2017.00477:theory:ART:761193747a
  claim_type: theory_link
  statement: 2013), height and enclosure (Vartanian et al., 2015), built vs.
  node_type: THEORETICAL_PROPOSITION
  article_type_family: unknown
  edge_type: INTERPRETS_AS
  needs_verification: true
  relation_type_hint: explains
  relation_strength_hint: 0.4
  argument_relation_type: cites
  theory_name: ART
  source_section: introduction
  source_page_start: 2
  source_page_end: 2
  source_quote: 2013), height and enclosure (Vartanian et al., 2015), built vs.
  source_quote_hash: 761193747a7bfa8c
  quality_flag: ok
  source: pdf_discourse_scan
  evidence_level: pdf_discourse_extracted
  provenance_tier: pdf_confirmed
  requires_pdf_confirmation: no
  processed_at: 2026-02-14T08:21:25.116337+00:00
  article_type_classifier_version: paper_classifier_v2
  article_type_confidence: 0.4545
  article_type_diagnostics: downgraded_to_unknown_low_confidence
  article_type_margin: 0.5000
  article_type_needs_review: true
  article_type_predicted_family: thought_piece
  article_type_runner_up: empirical_v2
  article_type_signals: title_pattern:perspective
  confidence: 0.62
  content: 2013), height and enclosure (Vartanian et al., 2015), built vs.
  argument_relation: explains

**Row 14:**
  paper_id: doi:10.3389/fnhum.2017.00477
  claim_id: disc:doi:10.3389/fnhum.2017.00477:xref:761193747a:vartanian_et_al._2
  claim_type: inter_article_relation
  statement: 2013), height and enclosure (Vartanian et al., 2015), built vs.
  node_type: EMPIRICAL_FINDING
  article_type_family: unknown
  edge_type: INTERPRETS_AS
  needs_verification: true
  relation_type_hint: explains
  relation_strength_hint: 0.35
  argument_relation_type: mentions
  citation_text: Vartanian et al., 2015)
  citation_match_confidence: 0.0
  citation_match_type: unresolved
  source_section: introduction
  source_page_start: 2
  source_page_end: 2
  source_quote: 2013), height and enclosure (Vartanian et al., 2015), built vs.
  source_quote_hash: 761193747a7bfa8c
  quality_flag: needs_citation_resolution
  source: pdf_discourse_scan
  evidence_level: pdf_discourse_extracted
  provenance_tier: pdf_confirmed
  requires_pdf_confirmation: no
  processed_at: 2026-02-14T08:21:25.175734+00:00
  article_type_classifier_version: paper_classifier_v2
  article_type_confidence: 0.4545
  article_type_diagnostics: downgraded_to_unknown_low_confidence
  article_type_margin: 0.5000
  article_type_needs_review: true
  article_type_predicted_family: thought_piece
  article_type_runner_up: empirical_v2
  article_type_signals: title_pattern:perspective
  confidence: 0.45
  content: 2013), height and enclosure (Vartanian et al., 2015), built vs.
  argument_relation: explains

**Row 15:**
  paper_id: doi:10.3389/fnhum.2017.00477
  claim_id: disc:doi:10.3389/fnhum.2017.00477:theory:ART:1b4738cdce
  claim_type: theory_link
  statement: Nandaetal.,2013;Vartanianetal.,2013;Nasretal.,2014).
  node_type: THEORETICAL_PROPOSITION
  article_type_family: unknown
  edge_type: INTERPRETS_AS
  needs_verification: true
  relation_type_hint: explains
  relation_strength_hint: 0.4
  argument_relation_type: cites
  theory_name: ART
  source_section: introduction
  source_page_start: 2
  source_page_end: 2
  source_quote: Nandaetal.,2013;Vartanianetal.,2013;Nasretal.,2014).
  source_quote_hash: 1b4738cdcee92b48
  quality_flag: ok
  source: pdf_discourse_scan
  evidence_level: pdf_discourse_extracted
  provenance_tier: pdf_confirmed
  requires_pdf_confirmation: no
  processed_at: 2026-02-14T08:21:25.175768+00:00
  article_type_classifier_version: paper_classifier_v2
  article_type_confidence: 0.4545
  article_type_diagnostics: downgraded_to_unknown_low_confidence
  article_type_margin: 0.5000
  article_type_needs_review: true
  article_type_predicted_family: thought_piece
  article_type_runner_up: empirical_v2
  article_type_signals: title_pattern:perspective
  confidence: 0.62
  content: Nandaetal.,2013;Vartanianetal.,2013;Nasretal.,2014).
  argument_relation: explains

**Row 16:**
  paper_id: doi:10.3389/fnhum.2017.00477
  claim_id: disc:doi:10.3389/fnhum.2017.00477:xref:4e5756942f:roe_et_al._2013
  claim_type: inter_article_relation
  statement: natural environment (Roe et al., 2013; Banaei et al., 2015), Accordingtoapreviousstudy,formsofbuiltplacesaremore
  node_type: EMPIRICAL_FINDING
  article_type_family: unknown
  edge_type: INTERPRETS_AS
  needs_verification: true
  relation_type_hint: explains
  relation_strength_hint: 0.35
  argument_relation_type: mentions
  citation_text: Roe et al., 2013
  citation_match_confidence: 0.3
  citation_match_type: author_year_ambiguous
  source_section: introduction
  source_page_start: 2
  source_page_end: 2
  source_quote: natural environment (Roe et al., 2013; Banaei et al., 2015), Accordingtoapreviousstudy,formsofbuiltplacesaremore
  source_quote_hash: 4e5756942f5bf282
  quality_flag: ok
  source: pdf_discourse_scan
  evidence_level: pdf_discourse_extracted
  provenance_tier: pdf_confirmed
  requires_pdf_confirmation: no
  processed_at: 2026-02-14T08:21:25.278590+00:00
  article_type_classifier_version: paper_classifier_v2
  article_type_confidence: 0.4545
  article_type_diagnostics: downgraded_to_unknown_low_confidence
  article_type_margin: 0.5000
  article_type_needs_review: true
  article_type_predicted_family: thought_piece
  article_type_runner_up: empirical_v2
  article_type_signals: title_pattern:perspective
  confidence: 0.45
  content: natural environment (Roe et al., 2013; Banaei et al., 2015), Accordingtoapreviousstudy,formsofbuiltplacesaremore
  argument_relation: explains

**Row 17:**
  paper_id: doi:10.3389/fnhum.2017.00477
  claim_id: disc:doi:10.3389/fnhum.2017.00477:xref:4e5756942f:banaei_et_al._2015
  claim_type: inter_article_relation
  statement: natural environment (Roe et al., 2013; Banaei et al., 2015), Accordingtoapreviousstudy,formsofbuiltplacesaremore
  node_type: EMPIRICAL_FINDING
  article_type_family: unknown
  edge_type: INTERPRETS_AS
  needs_verification: true
  relation_type_hint: explains
  relation_strength_hint: 0.35
  argument_relation_type: mentions
  citation_text: Banaei et al., 2015)
  citation_match_confidence: 0.0
  citation_match_type: unresolved
  source_section: introduction
  source_page_start: 2
  source_page_end: 2
  source_quote: natural environment (Roe et al., 2013; Banaei et al., 2015), Accordingtoapreviousstudy,formsofbuiltplacesaremore
  source_quote_hash: 4e5756942f5bf282
  quality_flag: needs_citation_resolution
  source: pdf_discourse_scan
  evidence_level: pdf_discourse_extracted
  provenance_tier: pdf_confirmed
  requires_pdf_confirmation: no
  processed_at: 2026-02-14T08:21:25.302600+00:00
  article_type_classifier_version: paper_classifier_v2
  article_type_confidence: 0.4545
  article_type_diagnostics: downgraded_to_unknown_low_confidence
  article_type_margin: 0.5000
  article_type_needs_review: true
  article_type_predicted_family: thought_piece
  article_type_runner_up: empirical_v2
  article_type_signals: title_pattern:perspective
  confidence: 0.45
  content: natural environment (Roe et al., 2013; Banaei et al., 2015), Accordingtoapreviousstudy,formsofbuiltplacesaremore
  argument_relation: explains

**Row 18:**
  paper_id: doi:10.3389/fnhum.2017.00477
  claim_id: disc:doi:10.3389/fnhum.2017.00477:xref:122b8c00e0:shin_et_al._2014
  claim_type: inter_article_relation
  statement: lighting (Shin et al., 2014), color (Küller et al., 2009), or the complicated and contain more form features than curvature
  node_type: EMPIRICAL_FINDING
  article_type_family: unknown
  edge_type: INTERPRETS_AS
  needs_verification: true
  relation_type_hint: explains
  relation_strength_hint: 0.35
  argument_relation_type: mentions
  citation_text: Shin et al., 2014)
  citation_match_confidence: 0.3
  citation_match_type: author_year_ambiguous
  source_section: introduction
  source_page_start: 2
  source_page_end: 2
  source_quote: lighting (Shin et al., 2014), color (Küller et al., 2009), or the complicated and contain more form features than curvature
  source_quote_hash: 122b8c00e0af4f09
  quality_flag: ok
  source: pdf_discourse_scan
  evidence_level: pdf_discourse_extracted
  provenance_tier: pdf_confirmed
  requires_pdf_confirmation: no
  processed_at: 2026-02-14T08:21:25.405416+00:00
  article_type_classifier_version: paper_classifier_v2
  article_type_confidence: 0.4545
  article_type_diagnostics: downgraded_to_unknown_low_confidence
  article_type_margin: 0.5000
  article_type_needs_review: true
  article_type_predicted_family: thought_piece
  article_type_runner_up: empirical_v2
  article_type_signals: title_pattern:perspective
  confidence: 0.45
  content: lighting (Shin et al., 2014), color (Küller et al., 2009), or the complicated and contain more form features than curvature
  argument_relation: explains

**Row 19:**
  paper_id: doi:10.3389/fnhum.2017.00477
  claim_id: disc:doi:10.3389/fnhum.2017.00477:xref:636ae89f29:banaei_et_al._2017
  claim_type: inter_article_relation
  statement: impactofthebuiltenvironmentonhumanmemory(Sternberg, and rectilinear geometries (Banaei et al., 2017).
  node_type: EMPIRICAL_FINDING
  article_type_family: unknown
  edge_type: INTERPRETS_AS
  needs_verification: true
  relation_type_hint: explains
  relation_strength_hint: 0.35
  argument_relation_type: mentions
  target_paper_id: doi:10.3389/fnhum.2017.00477
  citation_text: Banaei et al., 2017)
  citation_match_confidence: 0.75
  citation_match_type: author_year_unique
  source_section: introduction
  source_page_start: 2
  source_page_end: 2
  source_quote: impactofthebuiltenvironmentonhumanmemory(Sternberg, and rectilinear geometries (Banaei et al., 2017).
  source_quote_hash: 636ae89f29490452
  quality_flag: ok
  source: pdf_discourse_scan
  evidence_level: pdf_discourse_extracted
  provenance_tier: pdf_confirmed
  requires_pdf_confirmation: no
  processed_at: 2026-02-14T08:21:25.484115+00:00
  article_type_classifier_version: paper_classifier_v2
  article_type_confidence: 0.4545
  article_type_diagnostics: downgraded_to_unknown_low_confidence
  article_type_margin: 0.5000
  article_type_needs_review: true
  article_type_predicted_family: thought_piece
  article_type_runner_up: empirical_v2
  article_type_signals: title_pattern:perspective
  confidence: 0.45
  content: impactofthebuiltenvironmentonhumanmemory(Sternberg, and rectilinear geometries (Banaei et al., 2017).
  argument_relation: explains

**Row 20:**
  paper_id: doi:10.3389/fnhum.2017.00477
  claim_id: disc:doi:10.3389/fnhum.2017.00477:xref:0e031ff855:oed_2016
  claim_type: inter_article_relation
  statement: figureofthebodyasdistinguishedfromtheface’’(OED,2016). features as linear solids, curved linear solids, and surfaces and
  node_type: EMPIRICAL_FINDING
  article_type_family: unknown
  edge_type: INTERPRETS_AS
  needs_verification: true
  relation_type_hint: explains
  relation_strength_hint: 0.35
  argument_relation_type: mentions
  citation_text: OED,2016)
  citation_match_confidence: 0.3
  citation_match_type: author_year_ambiguous
  source_section: introduction
  source_page_start: 2
  source_page_end: 2
  source_quote: figureofthebodyasdistinguishedfromtheface’’(OED,2016). features as linear solids, curved linear solids, and surfaces and
  source_quote_hash: 0e031ff855e1d48b
  quality_flag: ok
  source: pdf_discourse_scan
  evidence_level: pdf_discourse_extracted
  provenance_tier: pdf_confirmed
  requires_pdf_confirmation: no
  processed_at: 2026-02-14T08:21:25.560950+00:00
  article_type_classifier_version: paper_classifier_v2
  article_type_confidence: 0.4545
  article_type_diagnostics: downgraded_to_unknown_low_confidence
  article_type_margin: 0.5000
  article_type_needs_review: true
  article_type_predicted_family: thought_piece
  article_type_runner_up: empirical_v2
  article_type_signals: title_pattern:perspective
  confidence: 0.45
  content: figureofthebodyasdistinguishedfromtheface’’(OED,2016). features as linear solids, curved linear solids, and surfaces and
  argument_relation: explains

================================================================================
## PART 2: DATABASE MODEL SCHEMAS
================================================================================


### Schema from `src/cmr/models.py`

class TemplateRecord(Base):
    """
    """
    __tablename__ = "templates"
    id = Column(Integer, primary_key=True)
    template_id = Column(String, unique=True, nullable=False)
    # e.g. "COLLABORATIVE_CREATIVITY_ARCHITECTURE_001"
    display_id = Column(String, unique=True, nullable=False)
    # e.g. "CREA4"
    name = Column(String, nullable=False)
    series = Column(String, nullable=False)
    # e.g. "CREA", "L", "MAT", "T"
    generation = Column(Integer, nullable=False)
    # 1 = T/M/AX series; 2 = domain series
    # Classification from Doc 67
    dedup_status = Column(String, nullable=False)
    # "active" | "superseded" | "residual" | "reference" | "gap"
    superseded_by = Column(String, nullable=True)
    # display_id of superseding template, if applicable
    # Metadata
    pe_contribution = Column(String, nullable=False)
    # "predictive" | "explanatory" | "organizational"
    maturity = Column(String, nullable=False)
    # "established" | "supported" | ... | "speculative"
    calibration_status = Column(String, nullable=False)
    # "substantial" | "partial" | "protocol" | "uncalibrated"
    practical_accessibility = Column(String, nullable=False)
    # "A" | "B" | "C" | "D"
    ecological_validation = Column(Boolean, default=False)
    # File reference
    json_path = Column(String, nullable=False)
    # Relative path to JSON file in data/templates/
    # Source documents
    source_docs = Column(String, nullable=False)
    # Comma-separated doc numbers, e.g. "55,58,65"
    # method: def __repr__(self) -> str:

class CMREvaluation(Base):
    """A single evaluation run: paper OR building assessment."""
    __tablename__ = "cmr_evaluations"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=func.now())
    evaluation_type = Column(String, nullable=False)
    # "paper" | "building" | "design_review"
    target_description = Column(Text, nullable=False)
    # Free text: paper citation, building name, design brief
    status = Column(String, default="in_progress")
    # "in_progress" | "complete" | "failed"
    # For building evaluations
    building_context = Column(JSON, nullable=True)
    # {climate: str, building_type: str, occupant_profile: {...}}
    # Relationships
    template_activations = relationship(
    domain_scores = relationship("CMRDomainScore", back_populates="evaluation")
    overall_scores = relationship("CMROverallScore", back_populates="evaluation")

class CMRTemplateActivation(Base):
    """Which templates were activated for this evaluation and why."""
    __tablename__ = "cmr_template_activations"
    id = Column(Integer, primary_key=True)
    evaluation_id = Column(Integer, ForeignKey("cmr_evaluations.id"))
    template_display_id = Column(String, ForeignKey("templates.display_id"))
    activation_reason = Column(Text)
    # Why this template was activated for this evaluation
    # Inputs provided
    inputs = Column(JSON, nullable=False)
    # {parameter_name: value, ...} matching template's inputs_required
    # Computed outputs
    outputs = Column(JSON, nullable=True)
    # {output_name: value, ...} from template computation
    wis_score = Column(Float, nullable=True)
    # Wellbeing Impact Score (0-100) converted from template output
    wis_confidence = Column(Float, nullable=True)
    # Confidence interval half-width
    # Interaction adjustments
    interaction_adjustments = Column(JSON, nullable=True)
    # [{with_template: str, adjustment_type: str, factor: float}, ...]
    # Relationships
    evaluation = relationship("CMREvaluation", back_populates="template_activations")

class CMRDomainScore(Base):
    """Aggregated domain-level scores."""
    __tablename__ = "cmr_domain_scores"
    id = Column(Integer, primary_key=True)
    evaluation_id = Column(Integer, ForeignKey("cmr_evaluations.id"))
    domain = Column(String, nullable=False)
    # "A1" through "A10"
    wis_score = Column(Float, nullable=False)
    wis_confidence = Column(Float, nullable=False)
    n_templates_activated = Column(Integer, nullable=False)
    template_ids = Column(String)  # Comma-separated
    # Aggregation details
    aggregation_method = Column(String, default="weighted_average")
    weight_basis = Column(String, default="calibration_confidence")
    # Relationships
    evaluation = relationship("CMREvaluation", back_populates="domain_scores")

class CMROverallScore(Base):
    """Overall assessment score."""
    __tablename__ = "cmr_overall_scores"
    id = Column(Integer, primary_key=True)
    evaluation_id = Column(Integer, ForeignKey("cmr_evaluations.id"))
    wis_geometric_mean = Column(Float, nullable=False)
    wis_confidence = Column(Float, nullable=False)
    n_domains_assessed = Column(Integer, nullable=False)
    # Flags
    severe_deficit_domains = Column(String, nullable=True)
    # Domains with WIS < 30
    data_gaps = Column(String, nullable=True)
    # Domains with insufficient input data
    # Relationships
    evaluation = relationship("CMREvaluation", back_populates="overall_scores")

class ReductionClaim(Base):
    """Maps a Tier 2 theory construct to Tier 1 template mechanisms."""
    __tablename__ = "reduction_claims"
    id = Column(Integer, primary_key=True)
    # The Tier 2 construct being reduced
    tier2_theory = Column(String, nullable=False)
    # e.g. "ART", "SRT", "Biophilia"
    tier2_construct = Column(String, nullable=False)
    # e.g. "Soft Fascination", "Prospect", "Being Away"
    # The reduction
    reduction_type = Column(String, nullable=False)
    # "full" | "partial" | "irreducible_residual"
    template_mappings = Column(JSON, nullable=False)
    # [{template_id: str, mechanism: str, coverage: float}, ...]
    # coverage: 0-1, how much of the construct this template explains
    irreducible_residual = Column(Text, nullable=True)
    # What cannot be reduced to template mechanisms
    confidence = Column(String, nullable=False)
    # "high" | "moderate" | "low"
    source_panel = Column(String, nullable=True)
    # e.g. "T2-A" for ART reduction panel
    # Staging link reconciliation
    staging_links_reconciled = Column(Integer, default=0)
    staging_links_total = Column(Integer, default=0)

class PaperRecord(Base):
    """History record for processed paper evaluations."""
    __tablename__ = "cmr_paper_records"
    id = Column(Integer, primary_key=True)
    citation = Column(Text, nullable=True)
    doi = Column(String, nullable=True)
    evaluated_at = Column(DateTime, default=func.now(), nullable=False)
    n_claims = Column(Integer, nullable=False, default=0)
    n_matched = Column(Integer, nullable=False, default=0)
    n_unmatched = Column(Integer, nullable=False, default=0)
    n_contradictions = Column(Integer, nullable=False, default=0)
    n_confirmations = Column(Integer, nullable=False, default=0)
    n_gaps = Column(Integer, nullable=False, default=0)
    aggregate_voi = Column(Float, nullable=False, default=0.0)
    proposals_generated = Column(Integer, nullable=False, default=0)
    # Denormalized list for quick template-to-paper lookup.
    matched_template_ids = Column(JSON, nullable=False, default=list)


### Schema from `src/models/__init__.py`


### Schema from `src/models/epistemic_status.py`


### Schema from `src/models/propositional_content.py`


### Schema from `src/models/provenance.py`


### Schema from `src/models/theory_models.py`


### Schema from `src/queue/models.py`


### Schema from `src/services/web_persistence.py`


### Grep for Belief/Constraint/Bridge/ReductionClaim definitions


**Belief:**
  src/services/stability_engine.py:55: class BeliefStabilityInfo:
  src/services/belief_validator.py:40: class BeliefValidator:
  src/services/web_of_belief.py:100: class BeliefStatus(Enum):
  src/services/web_of_belief.py:145: class BeliefKind(Enum):
  src/services/web_of_belief.py:566: class Belief:
  src/services/cross_layer_query.py:37: class BeliefSummary:
  src/services/abstraction_levels.py:70: class BeliefRole(Enum):
  src/services/scalable_coherence.py:70: class BeliefCluster:
  src/services/social_epistemology.py:375: class BeliefProvenance:
  src/services/gold_standard.py:366: class BeliefMatch:
  src/services/edge_justification.py:48: class BeliefSummary:
  src/services/epistemic_causal_bridge.py:84: class BeliefStatus(Enum):
  src/services/epistemic_causal_bridge.py:206: class Belief:
  src/services/epistemic_causal_bridge.py:485: class BeliefScope:
  src/services/epistemic_causal_bridge.py:1109: class BeliefChange:
  src/services/validation.py:221: class BeliefCoherenceAssessment:

**Constraint:**
  src/services/web_of_belief.py:1351: class Constraint:
  src/services/cross_layer_query.py:50: class ConstraintSummary:
  src/services/scalable_coherence.py:105: class ConstraintNode:
  src/services/scalable_coherence.py:150: class ConstraintNetwork:
  src/services/graph_api.py:160: class ConstraintInfo:

**Bridge:**
  src/services/bridge_warrants.py:64: class BridgeType(Enum):
  src/services/bridge_warrants.py:80: class BridgeStatus(Enum):
  src/services/bridge_warrants.py:173: class BridgeWarrant:
  src/services/bridge_warrants.py:278: class BridgeRegistry:
  src/services/outcome_taxonomy.py:752: class BridgeCandidate:
  src/services/epistemic_causal_bridge.py:1292: class BridgeError(Exception):

**ReductionClaim:**
  src/cmr/models.py:180: class ReductionClaim(Base):

**TemplateRecord:**
  src/cmr/models.py:21: class TemplateRecord(Base):

**CMREvaluation:**
  src/cmr/models.py:77: class CMREvaluation(Base):

================================================================================
## PART 3: TEMPLATE INPUT/OUTPUT VOCABULARY
================================================================================


### Feature-to-template mappings (from src/cmr/)


**Found `FEATURE_TO_TEMPLATE` in `src/cmr/feature_mapping.py`**
  58: FEATURE_TO_TEMPLATE_INPUT: Dict[str, Dict[str, str]] = {
  59:     "VF3": {
  60:         "ceiling_height_m": "ceiling_height_m",
  61:         "floor_area_m2": "floor_area_m2",
  62:     },
  63:     "L1": {
  64:         "cv_luminance": "luminance_contrast_cv",
  65:     },
  66:     "L2": {
  67:         "medi_lux": "illuminance_lux",
  68:         "exposure_duration_hours": "daylight_exposure_hours",
  69:         "time_of_day": "time_of_day",
  70:     },
  71:     "L3": {
  72:         "circadian_score": "l2_score",
  73:         "view_score": "view_score",
  74:         "luminance_contrast_score": "l1_score",
  75:         "cct_score": "l4_score",
  76:         "dynamic_variation_score": "l5_score",
  77:     },
  78:     "L4": {
  79:         "cct_kelvin": "cct_kelvin",
  80:         "time_of_day": "time_of_day",
  81:         "context_type": "context_type",
  82:     },
  83:     "L5": {
  84:         "has_daylight_variation": "has_daylight_variation",
  85:         "has_designed_dynamics": "has_designed_dynamics",
  86:         "static_exposure_hours": "static_exposure_hours",
  87:         "change_rate_hz": "change_rate_hz",
  88:     },
  89:     "CREA2": {
  90:         "noise_db": "ambient_noise_dba",
  91:         "ambient_lux": "illuminance_lux",
  92:         "baseline_creativity": "baseline_creativity",
  93:     },
  94:     "MAT1": {
  95:         "surface_effusivity": "surface_effusivity",
  96:         "contact_temperature_c": "contact_temperature_c",
  97:         "climate": "climate_context",
  98:     },
  99:     "MAT2": {
  100:         "operative_temperature_c": "operative_temp_c",
  101:         "running_mean_outdoor_c": "running_mean_outdoor_c",
  102:         "ventilation_type": "ventilation_type",
  103:     },
  104:     "MAT4": {
  105:         "material_type": "primary_material",
  106:         "surface_ratio": "natural_material_ratio",
  107:     },
  108:     "SOC2": {
  109:         "shared_area_ratio": "shared_area_ratio",
  110:         "phone_booths_per_worker": "phone_booths_per_worker",
  111:         "quiet_rooms_per_worker": "quiet_rooms_per_worker",
  112:         "visual_privacy_score": "visual_privacy_score",
  113:         "acoustic_privacy_stc": "acoustic_privacy_stc",
  114:     },
  115:     "SC1": {
  116:         "integration_normalized": "spatial_integration_score",
  117:         "intelligibility": "layout_legibility",

**Found `SYNONYM` in `src/cmr/template_matching.py`**
  89: _SYNONYM_GROUPS = [
  90:     {"daylight", "illuminance", "light_level", "lux"},
  91:     {"noise", "ambient_noise", "ambient_noise_dba"},
  92:     {"nature_view", "has_nature_view", "view_quality", "green_view"},
  93:     {"creative_thinking", "creative_output", "creativity"},
  94:     {"stress_reduction", "stress", "cortisol_reduction"},
  95: ]

**Found `FEATURE_MAP` in `src/cmr/lifespan_moderation.py`**
  314: FEATURE_MAPPINGS = {
  315:     "VF3": {
  316:         "ceiling_height_m": "ceiling_height_m",
  317:         "floor_area_m2": "floor_area_m2",
  318:     },
  319:     "L1": {
  320:         "illuminance_lux": "illuminance_lux",
  321:         "cv_luminance": "cv_luminance",
  322:     },
  323:     "L2": {
  324:         "m_edi_lux": "m_edi_lux",
  325:     },
  326:     "SOC2": {
  327:         "acoustic_isolation_db": "acoustic_isolation_db",
  328:         "visual_privacy_index": "visual_privacy_index",
  329:         "density_m2_per_person": "density_m2_per_person",
  330:     },
  331:     "VIEW1": {
  332:         "view_content": "view_content",
  333:         "view_layers": "view_layers",
  334:         "view_sky_fraction": "view_sky_fraction",
  335:         "has_nature_view": "has_nature_view",
  336:         "view_distance_m": "view_distance_m",
  337:     },
  338:     "CREA2": {
  339:         "ambient_noise_dba": "ambient_noise_dba",
  340:         "ceiling_height_m": "ceiling_height_m",
  341:         "illuminance_lux": "illuminance_lux",
  342:     },
  343: }
  344: 
  345: 
  346: def get_feature_mapping(template_id: str) -> Dict[str, str]:

**Found `SYNONYM` in `src/cmr/claim_extraction.py`**
  85: _SYNONYMS = {
  86:     "nature views": "has_nature_view",
  87:     "view of nature": "has_nature_view",
  88:     "nature view": "has_nature_view",
  89:     "high ceilings": "ceiling_height_m",
  90:     "ceiling height": "ceiling_height_m",
  91:     "noise": "ambient_noise_dba",
  92:     "ambient noise": "ambient_noise_dba",
  93:     "stress": "stress",
  94:     "stress levels": "stress",
  95:     "recovery time": "recovery_time",
  96:     "recovery times": "recovery_time",
  97:     "pain medication": "pain_medication_use",
  98:     "pain medication use": "pain_medication_use",
  99: }
  100: 
  101: _RELATION_PATTERN = re.compile(

**Found `FEATURE_TO_TEMPLATE` in `src/cmr/validation.py`**
  8: from src.cmr.feature_mapping import STANDARD_BUILDING_FEATURES, FEATURE_TO_TEMPLATE_INPUT
  9: 
  10: 
  11: RANGE_CONFIG: Dict[str, Tuple[float, float, float, float]] = {

### Template JSON sample: first 3 template files


**data/templates/AX1.json:**
template_id: BRECVEMA_ARCH_001
display_id: AX1
version: 1.0.0
name: Anterior Insula as Salience Hub for Physical and Social Pain
description: Cross-framework template demonstrating shared neural substrate for physical pain and social distress...
source_panel_doc: 02-15_20_Panel_V_Social_Brain_V1_0.md
domain_tags:
  [6 items]
    cross_framework
    interoceptive
    neuromodulatory
    ... +3 more
key_references:
  [3 items]
    citation: Singer, T., et al. (2004). Empathy for pain involves the affective but not sensory components of pai...
    doi: 10.1126/science.1093535
    year: 2004
    citation: Eisenberger, N. I., Lieberman, M. D., & Williams, K. D. (2003). Does rejection hurt? An fMRI study o...
    doi: 10.1126/science.1089134
    year: 2003
    citation: Craig, A. D. (2009). How do you feel—now? The anterior insula and human awareness. Nature Reviews Ne...
    doi: 10.1038/nrn2555
    year: 2009
causal_links:
  [3 items]
    link_id: AX1.L1
    from_level: environmental
    to_level: neural
    activity: couples
    direction: positive
    mechanism_summary: Physical pain OR social exclusion signals both activate anterior insula via distinct input pathways
    edge_confidence: strong
    link_id: AX1.L2
    from_level: neural
    to_level: affective
    activity: amplifies
    direction: positive
    mechanism_summary: Insula generates unified negative affect signal regardless of pain source (physical/social)
    edge_confidence: strong
    link_id: AX1.L3
    from_level: affective
    to_level: behavioral
    activity: biases
    direction: positive
    mechanism_summary: Shared affect pathway explains why social isolation mimics physical pain in behavioral avoidance
    edge_confidence: moderate
interaction_template_ids:
  [3 items]
    T5
    T12
    AWE_HIGH_PE_ACCOMMODATION_001
overall_maturity: established
bridging_quality: strong
prior_confidence: 0.85
updated_at_iso: 2026-02-16T18:30:00Z
short_description: Anterior Insula as Salience Hub for Physical and Social Pain
age_band_modifiers:
  toddler_0_3:
    speed: 0.45
    vision: 0.7
    hearing: 0.85
    motor: 0.5
    olfaction: 0.9
  age_3_6:
    speed: 0.6
    vision: 0.8
    hearing: 0.9
    motor: 0.65
    olfaction: 0.95
  age_6_9:
    speed: 0.72
    vision: 0.88
    hearing: 0.94
    motor: 0.78
    olfaction: 0.97
  age_9_12:
    speed: 0.82
    vision: 0.94
    hearing: 0.97
    motor: 0.87
    olfaction: 0.98
  age_12_16:
    speed: 0.9
    vision: 0.97
    hearing: 0.98
    motor: 0.93
    olfaction: 0.99
  emerging_adult_16_25:
    speed: 0.97
    vision: 1.0
    hearing: 1.0
    motor: 0.98
    olfaction: 1.0
  young_20_40:
    speed: 1.0
    vision: 1.0
    hearing: 1.0
    motor: 1.0
    olfaction: 1.0
  middle_40_65:
    speed: 0.88
    vision: 0.9
    hearing: 0.92
    motor: 0.9
    olfaction: 0.85
  older_65_80:
    speed: 0.72
    vision: 0.7
    hearing: 0.75
    motor: 0.7
    olfaction: 0.5
  frail_80_plus:
    speed: 0.55
    vision: 0.5
    hearing: 0.55
    motor: 0.5
    olfaction: 0.25
vulnerability_index:
  formula: speed * vision * hearing * motor * olfaction
  interpretation: lower product indicates higher vulnerability
  reference_band: young_20_40
universal_design_thresholds:
  min_ambient_illuminance_lux: 300
  max_rt60_speech_s: 0.4
  min_snr_db: 15
  min_cof: 0.55
  max_riser_mm: 170
  min_contrast_ratio: 0.7
  min_wayfinding_channels: 3
challenge_gradient_available: False
lifespan_sensitivity_multiplier:
  model: u_curve_piecewise
  reference: age_25_50
  by_age_range:
    age_0_6: 1.6
    age_6_12: 1.35
    age_12_25: 1.15
    age_25_50: 1.0
    age_50_65: 1.2
    age_65_80: 1.45
    age_80_plus: 1.7
  boundary_rule:
    range: 16-25
    method: linear_interpolation_to_adult_baseline

**data/templates/AX10.json:**
template_id: AX_ATTENTION_MEDIATION_010
display_id: AX10
name: Environmental feature → attention capture → downstream effect
structural_pattern: stimulus_salience → attention_allocation → processing_depth
higher_order_principle: Effects require attention; unattended features have minimal impact.
framework_ids:
  [2 items]
    ATTENTION_RESTORATION
    PREDICTIVE_PROCESSING
causal_links:
  [2 items]
    from_entity: environmental_feature
    activity: attention_capture
    to_entity: processing_allocation
    change_produced: feature enters processing stream
    level: environmental
    bridging_to: cognitive
    bridging_quality: strong
    maturity: established
    evidence_base: Corbetta & Shulman 2002
    scope_conditions: Bottom-up salience or top-down goals
    interactions:
      ...
    from_entity: processing_allocation
    activity: effect_amplification
    to_entity: effect_magnitude
    change_produced: attention modulates effect size
    level: cognitive
    bridging_to: psychological
    bridging_quality: strong
    maturity: established
    evidence_base: Lavie 2005
    scope_conditions: Perceptual load limits capacity
    interactions:
      ...
scope_conditions:
  [3 items]
    Many effects mediated by attention
    Inattentional blindness limits processing
    Background effects smaller than focal
moderators:
  [3 items]
    Perceptual load
    Goal relevance
    Feature salience
interactions:
  [1 items]
    All templates with attention-dependent effects
overall_maturity: established
key_references:
  [2 items]
    id: Corbetta_Shulman_2002
    citation: Corbetta & Shulman (2002)
    id: Lavie_2005
    citation: Lavie (2005)
version: 1.0.0
short_description: Effects require attention; unattended features have minimal impact
age_band_modifiers:
  toddler_0_3:
    speed: 0.45
    vision: 0.7
    hearing: 0.85
    motor: 0.5
    olfaction: 0.9
  age_3_6:
    speed: 0.6
    vision: 0.8
    hearing: 0.9
    motor: 0.65
    olfaction: 0.95
  age_6_9:
    speed: 0.72
    vision: 0.88
    hearing: 0.94
    motor: 0.78
    olfaction: 0.97
  age_9_12:
    speed: 0.82
    vision: 0.94
    hearing: 0.97
    motor: 0.87
    olfaction: 0.98
  age_12_16:
    speed: 0.9
    vision: 0.97
    hearing: 0.98
    motor: 0.93
    olfaction: 0.99
  emerging_adult_16_25:
    speed: 0.97
    vision: 1.0
    hearing: 1.0
    motor: 0.98
    olfaction: 1.0
  young_20_40:
    speed: 1.0
    vision: 1.0
    hearing: 1.0
    motor: 1.0
    olfaction: 1.0
  middle_40_65:
    speed: 0.88
    vision: 0.9
    hearing: 0.92
    motor: 0.9
    olfaction: 0.85
  older_65_80:
    speed: 0.72
    vision: 0.7
    hearing: 0.75
    motor: 0.7
    olfaction: 0.5
  frail_80_plus:
    speed: 0.55
    vision: 0.5
    hearing: 0.55
    motor: 0.5
    olfaction: 0.25
vulnerability_index:
  formula: speed * vision * hearing * motor * olfaction
  interpretation: lower product indicates higher vulnerability
  reference_band: young_20_40
universal_design_thresholds:
  min_ambient_illuminance_lux: 300
  max_rt60_speech_s: 0.4
  min_snr_db: 15
  min_cof: 0.55
  max_riser_mm: 170
  min_contrast_ratio: 0.7
  min_wayfinding_channels: 3
challenge_gradient_available: False
lifespan_sensitivity_multiplier:
  model: u_curve_piecewise
  reference: age_25_50
  by_age_range:
    age_0_6: 1.6
    age_6_12: 1.35
    age_12_25: 1.15
    age_25_50: 1.0
    age_50_65: 1.2
    age_65_80: 1.45
    age_80_plus: 1.7
  boundary_rule:
    range: 16-25
    method: linear_interpolation_to_adult_baseline
developmental_challenge_benefit: False

**data/templates/AX11.json:**
template_id: AX_CHRONIC_ACUTE_011
display_id: AX11
name: Exposure duration → acute vs chronic pathway → different outcomes
structural_pattern: temporal_pattern → pathway_selection → duration_specific_effect
higher_order_principle: Brief and sustained exposures often operate through different mechanisms.
framework_ids:
  [1 items]
    NEUROMODULATORY
causal_links:
  [2 items]
    from_entity: exposure_duration
    activity: pathway_differentiation
    to_entity: mechanism_activation
    change_produced: acute vs chronic pathways engaged
    level: environmental
    bridging_to: physiological
    bridging_quality: strong
    maturity: established
    evidence_base: McEwen 2007 (stress); Kaplan 1995 (restoration)
    scope_conditions: Acute: minutes-hours; Chronic: days-years
    interactions:
      ...
    from_entity: mechanism_activation
    activity: outcome_production
    to_entity: observed_effect
    change_produced: duration-appropriate outcome
    level: physiological
    bridging_to: clinical
    bridging_quality: strong
    maturity: established
    evidence_base: Sterling 2012
    scope_conditions: Acute recovery vs chronic adaptation
    interactions:
      ...
scope_conditions:
  [3 items]
    Acute stress is adaptive; chronic stress is pathological
    Acute restoration from brief nature contact; chronic from living environment
    Different measurement approaches needed
moderators:
  [3 items]
    Recovery opportunities
    Baseline state
    Cumulative load
interactions:
  [3 items]
    NM_THREAT_HPA_001
    PP_CULTURAL_PRIOR_CALIBRATION_001
    ALLOSTATIC_MASTER_001
overall_maturity: established
key_references:
  [2 items]
    id: McEwen_2007
    citation: McEwen (2007)
    id: Sterling_2012
    citation: Sterling (2012)
version: 1.0.0
short_description: Brief and sustained exposures often operate through different mechanisms
age_band_modifiers:
  toddler_0_3:
    speed: 0.45
    vision: 0.7
    hearing: 0.85
    motor: 0.5
    olfaction: 0.9
  age_3_6:
    speed: 0.6
    vision: 0.8
    hearing: 0.9
    motor: 0.65
    olfaction: 0.95
  age_6_9:
    speed: 0.72
    vision: 0.88
    hearing: 0.94
    motor: 0.78
    olfaction: 0.97
  age_9_12:
    speed: 0.82
    vision: 0.94
    hearing: 0.97
    motor: 0.87
    olfaction: 0.98
  age_12_16:
    speed: 0.9
    vision: 0.97
    hearing: 0.98
    motor: 0.93
    olfaction: 0.99
  emerging_adult_16_25:
    speed: 0.97
    vision: 1
    hearing: 1
    motor: 0.98
    olfaction: 1
  young_20_40:
    speed: 1
    vision: 1
    hearing: 1
    motor: 1
    olfaction: 1
  middle_40_65:
    speed: 0.88
    vision: 0.9
    hearing: 0.92
    motor: 0.9
    olfaction: 0.85
  older_65_80:
    speed: 0.72
    vision: 0.7
    hearing: 0.75
    motor: 0.7
    olfaction: 0.5
  frail_80_plus:
    speed: 0.55
    vision: 0.5
    hearing: 0.55
    motor: 0.5
    olfaction: 0.25
vulnerability_index:
  formula: speed * vision * hearing * motor * olfaction
  interpretation: lower product indicates higher vulnerability
  reference_band: young_20_40
universal_design_thresholds:
  min_ambient_illuminance_lux: 300
  max_rt60_speech_s: 0.4
  min_snr_db: 15
  min_cof: 0.55
  max_riser_mm: 170
  min_contrast_ratio: 0.7
  min_wayfinding_channels: 3
challenge_gradient_available: False
lifespan_sensitivity_multiplier:
  model: u_curve_piecewise
  reference: age_25_50
  by_age_range:
    age_0_6: 1.6
    age_6_12: 1.35
    age_12_25: 1.15
    age_25_50: 1
    age_50_65: 1.2
    age_65_80: 1.45
    age_80_plus: 1.7
  boundary_rule:
    range: 16-25
    method: linear_interpolation_to_adult_baseline
developmental_challenge_benefit: False

================================================================================
## PART 4: WEB OF BELIEF SAMPLE
================================================================================


### Attempting to query web of belief for sample beliefs/constraints

Could not query web of belief: cannot import name 'get_or_create_master_web' from 'src.services.web_persistence' (/Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/services/web_persistence.py)
Falling back to file inspection...

**Found DB: ae.db** (8.3 MB)
  Tables: ['processing_queue', 'sqlite_sequence', 'articles', 'findings', 'seven_panel', 'user_api_keys', 'api_usage_events', 'ui_events', 'users', 'sessions', 'audit_log', 'rules', 'rule_evidence', 'theories', 'theory_claims', 'theory_assumptions', 'theory_boundaries', 'predictions', 'prediction_evidence', 'theory_papers', 'theory_testing_papers', 'theory_confidence_history', 'prediction_confidence_history', 'schema_version', 'article_essence', 'templates', 'cmr_evaluations', 'reduction_claims', 'cmr_template_activations', 'cmr_domain_scores', 'cmr_overall_scores', 'web_metadata', 'beliefs', 'constraints', 'bridges', 'paper_integrations', 'paper_publication', 'entrenchment_snapshots', 'entrenchment_events', 'coherence_history', 'local_coherence_history', 'belief_merge_log', 'paper_quality', 'web_snapshots', 'coherence_alerts', 'cmr_paper_records', 'cmr_update_proposals']

  **processing_queue** (8 rows)
  Columns: ['id', 'job_id', 'job_type', 'params', 'status', 'priority', 'result', 'error', 'created_at', 'started_at', 'completed_at', 'updated_at']
    (1, 'x1', 'L0_harvest', '{"q": 1}', 'failed', 100, None, "L0_harvest requires a non-empty 'query' parameter", '2025-12-03 00:12:16', '2025-12-03T02:53:29.195929', '2025-12-03T02:53:29.197185', None)
    (2, 'jobL0_1764730460', 'L0_harvest', '{"query": "biophilic design", "limit": 1}', 'complete', 100, 'l0_harvested:1', None, '2025-12-03 02:54:20', '2025-12-03T02:54:25.979846', '2025-12-03T02:54:26.858535', None)
    (3, 'jobL2_1764730517', 'L2_extract', '{"article_ids": ["29b77e1e9ea2b9bdc8629c9f13b0eb67f1fc338c"], "topic": "biophilic design"}', 'complete', 100, 'l2_extracted:0', None, '2025-12-03 02:55:17', '2025-12-03T04:25:00.638862', '2025-12-03T04:25:00.641699', None)

  **sqlite_sequence** (4 rows)
  Columns: ['name', 'seq']
    ('ui_events', 89963)
    ('processing_queue', 10)
    ('findings', 5)

  **articles** (53 rows)
  Columns: ['article_id', 'title', 'abstract', 'doi', 'corpus_id', 'authors', 'year', 'venue', 'full_text', 'sections', 'text_length', 'is_open_access', 'citation_count', 'url_pdf', 'ingested_at', 'created_at']
    ('29b77e1e9ea2b9bdc8629c9f13b0eb67f1fc338c', "Effects of Biophilic Design Interventions on University Students' Cognitive Performance: An Audio-Visual Experimental Study in an Immersive Virtual Office Environment", 'The human-nature connection should be a key component in the design of supportive and comfortable indoor environments. An interest in introducing Nature Based Solutions indoor via Biophilic Design (BD) intervention recently emerged. Related benefits for work efficiency have been iden...
    ('demo:article:001', 'Demo Article: Sleep and Memory Consolidation', 'A small synthetic abstract for UI preview purposes.', '10.1234/demo.sleep.2025', 'demo-corpus-001', 'Doe, J.; Smith, A.', 2025, 'Journal of Demo Science', '', '', 0, 1, 12, 'https://example.com/demo.pdf', '2025-12-30T15:01:28.242155', '2025-12-30T15:01:28.242155')
    ('paper-1', 'Effects of biophilic design on occupant wellbeing and performance in built environments: Study 1', 'This study investigates the impact of biophilic on occupant wellbeing and performance in office environments. \nWe conducted a field study with n=50 participants across 2 different buildings. \nResults showed significant positive effects on stress reduction (p<0.05, d=0.30) and cognitive performance (p<0.01, d=0.25). \nPhysiological measurements confirmed these findings, with cortisol...

  **findings** (3 rows)
  Columns: ['id', 'finding_level', 'consequent', 'antecedents', 'operational_measure', 'measure_type', 'measure_direction', 'p_value', 'effect_size', 'sample_size', 'job_id', 'paper_id', 'created_at', 'effect_size_type', 'ci_lower', 'ci_upper']
    (1, 'primary', 'memory_recall', 'sleep_duration', 'recall_score', 'behavioral', 'positive', 0.03, 0.42, 120, 'demo-job-001', 'demo:article:001', '2025-12-30T15:01:28.242155', None, None, None)
    (4, 'meso', 'Higher sustained attention scores are associated with high daylight conditions in open-plan offices.', '["High daylight conditions"]', None, None, 'positive', 0.03, 0.5, 120, 'l2-demo-20260102231138', 'sha256:cccebafd8cbd', '2026-01-02T17:42:07.728497+00:00', "Cohen's d", 0.2, 0.8)
    (5, 'meso', 'Lower stress ratings are associated with high daylight conditions in open-plan offices.', '["High daylight conditions"]', None, None, 'negative', 0.04, -0.4, 120, 'l2-demo-20260102231138', 'sha256:cccebafd8cbd', '2026-01-02T17:42:07.728497+00:00', None, None, None)

  **seven_panel** (0 rows)
  Columns: ['article_id', 'hypothesis', 'population_context', 'manipulations_measures', 'findings_effect', 'limitations_confounds', 'design_type', 'stats_effect_sizes']

  **user_api_keys** (1 rows)
  Columns: ['user_id', 'provider', 'enc_key', 'created_at']
    ('1', 'openai', b'gAAAAABpjSbLUloEpAsypJjaFnbUdBV-c1IjyRZ47jg1klo-wBAHwBTU30ss9dFZsXqP8LOPt6T92AfUst0xmCUNYOxjKC9J4oGOnOTXn1_1586q_tM1onE=', '2026-02-12 01:03:07')

  **api_usage_events** (0 rows)
  Columns: ['id', 'user_id', 'provider', 'model', 'tokens_in', 'tokens_out', 'cost_usd', 'created_at']

  **ui_events** (89963 rows)
  Columns: ['id', 'timestamp', 'user_hash', 'surface', 'action', 'detail_json']
    (1, '2025-12-03T00:10:23', 'tech_lead', 'control_room', 'view', '{"auto_refresh": false}')
    (2, '2025-12-30T09:13:47', 'davidusa', 'control_room', 'view', '{"auto_refresh": true}')
    (3, '2025-12-30T09:13:53', 'davidusa', 'control_room', 'view', '{"auto_refresh": true}')

  **users** (0 rows)
  Columns: ['user_id', 'email', 'hashed_password', 'name', 'role', 'created_at', 'last_login', 'is_active', 'preferences']

  **sessions** (0 rows)
  Columns: ['session_id', 'user_id', 'token', 'created_at', 'expires_at', 'is_valid']

  **audit_log** (0 rows)
  Columns: ['id', 'user_id', 'action', 'resource', 'details', 'ip_address', 'timestamp']

  **rules** (115 rows)
  Columns: ['rule_id', 'rule', 'confidence', 'triangulation_score', 'contradiction_count', 'job_id', 'created_at']
    ('rule-l2-demo-20260102231138-1', 'High daylight conditions -> Higher sustained attention scores are associated with high daylight conditions in open-plan offices.', 0.5, 0.0, 0, 'l2-demo-20260102231138', '2026-01-02T17:42:07.728497+00:00')
    ('rule-l2-demo-20260102231138-2', 'High daylight conditions -> Lower stress ratings are associated with high daylight conditions in open-plan offices.', 0.5, 0.0, 0, 'l2-demo-20260102231138', '2026-01-02T17:42:07.728497+00:00')
    ('abstract_10.1038/s41598-025-19113-4_1', 'Virtual plants in VR office environment -> No effect on path steering performance (NULL finding). Study challenges previous positive findings on biophilic design + cognition.', 0.25, None, 0, 'abstract_batch_2026-02-11', '2026-02-11 07:32:28')

  **rule_evidence** (2 rows)
  Columns: ['id', 'rule_id', 'article_id', 'passage', 'page_number', 'stance', 'created_at']
    (3, 'rule-l2-demo-20260102231138-1', 'sha256:cccebafd8cbd', None, None, 'supporting', '2026-01-02 17:42:07')
    (4, 'rule-l2-demo-20260102231138-2', 'sha256:cccebafd8cbd', None, None, 'supporting', '2026-01-02 17:42:07')

  **theories** (0 rows)
  Columns: ['theory_id', 'name', 'aliases', 'originators', 'year_introduced', 'domain', 'scope_description', 'level', 'overall_confidence', 'confidence_rationale', 'quantitative_precision', 'parent_theories', 'child_theories', 'compatible_theories', 'competing_theories', 'replication_status', 'extraction_source', 'extracted_by', 'version', 'created_at', 'updated_at']

  **theory_claims** (0 rows)
  Columns: ['claim_id', 'theory_id', 'statement', 'formalization', 'necessity', 'testability', 'created_at']

  **theory_assumptions** (0 rows)
  Columns: ['assumption_id', 'theory_id', 'statement', 'dependent_claims', 'violation_consequence', 'created_at']

  **theory_boundaries** (0 rows)
  Columns: ['boundary_id', 'theory_id', 'condition_description', 'evidence_for_boundary', 'mechanism_of_failure', 'confidence_penalty', 'created_at']

  **predictions** (0 rows)
  Columns: ['prediction_id', 'source_theory_id', 'statement', 'prediction_type', 'antecedent_env_conditions', 'antecedent_population', 'antecedent_temporal', 'antecedent_state', 'consequent_outcome', 'consequent_direction', 'consequent_magnitude', 'consequent_mechanism', 'relation_type', 'derivation_chain', 'auxiliary_assumptions', 'quantitative_point_estimate', 'quantitative_ci_lower', 'quantitative_ci_upper', 'functional_form', 'generality', 'applicable_populations', 'applicable_contexts', 'known_exceptions', 'testing_status', 'overall_support', 'test_summary', 'prior_confidence', 'current_confidence', 'theory_contribution', 'derivation_contribution', 'empirical_contribution', 'uncertainty_type', 'maps_to_edge_id', 'maps_to_nodes', 'contributes_prior', 'prior_weight', 'extraction_source', 'created_at', 'updated_at']

  **prediction_evidence** (0 rows)
  Columns: ['id', 'prediction_id', 'paper_id', 'finding_id', 'test_type', 'result', 'test_strength', 'conditions_met', 'notes', 'confidence_delta', 'created_at']

  **theory_papers** (0 rows)
  Columns: ['id', 'theory_id', 'paper_id', 'contribution_type', 'contribution_description', 'created_at']

  **theory_testing_papers** (0 rows)
  Columns: ['id', 'theory_id', 'paper_id', 'prediction_id', 'tests_explicitly', 'prediction_tested', 'result', 'theory_update_direction', 'theory_update_magnitude', 'notes', 'created_at']

  **theory_confidence_history** (0 rows)
  Columns: ['id', 'theory_id', 'old_confidence', 'new_confidence', 'change_reason', 'triggered_by', 'created_at']

  **prediction_confidence_history** (0 rows)
  Columns: ['id', 'prediction_id', 'old_confidence', 'new_confidence', 'change_reason', 'triggered_by', 'created_at']

  **schema_version** (1 rows)
  Columns: ['version', 'applied_at', 'description']
    ('20.8.0', '2026-01-10 02:42:39', 'Theory system schema: theories, claims, assumptions, boundaries, predictions, evidence, confidence history')

  **article_essence** (0 rows)
  Columns: ['article_id', 'hypothesis', 'population_context', 'manipulations_measures', 'findings_effect', 'limitations_confounds', 'design_type', 'stats_effect_sizes', 'article_type', 'extraction_template']

  **templates** (150 rows)
  Columns: ['id', 'template_id', 'display_id', 'name', 'series', 'generation', 'dedup_status', 'superseded_by', 'pe_contribution', 'maturity', 'calibration_status', 'practical_accessibility', 'ecological_validation', 'json_path', 'source_docs']
    (1, 'BRECVEMA_ARCH_001', 'AX1', 'Anterior Insula as Salience Hub for Physical and Social Pain', 'AX', 1, 'gap', None, 'organizational', 'established', 'uncalibrated', 'B', 0, 'data/templates/AX1.json', '20')
    (2, 'AX_ATTENTION_MEDIATION_010', 'AX10', 'Environmental feature → attention capture → downstream effect', 'AX', 1, 'gap', None, 'explanatory', 'established', 'uncalibrated', 'B', 0, 'data/templates/AX10.json', '')
    (3, 'AX_CHRONIC_ACUTE_011', 'AX11', 'Exposure duration → acute vs chronic pathway → different outcomes', 'AX', 1, 'gap', None, 'explanatory', 'established', 'uncalibrated', 'B', 0, 'data/templates/AX11.json', '')

  **cmr_evaluations** (46 rows)
  Columns: ['id', 'created_at', 'evaluation_type', 'target_description', 'status', 'building_context']
    (1, '2026-02-17 13:33:08', 'building', 'Unnamed Building', 'complete', '{"building_type": "research_institute", "climate_zone": "3C", "occupant_profile": {"age": 35, "cultural_context": "Western"}}')
    (2, '2026-02-17 13:55:13', 'building', 'Salk Institute', 'complete', '{"building_type": "research_institute", "climate_zone": "3C", "building_name": "Salk Institute", "occupant_profile": {"age": 35, "cultural_context": "Western"}}')
    (3, '2026-02-17 13:55:23', 'building', 'Unnamed Building', 'complete', '{"building_type": "research_institute", "climate_zone": "3C", "occupant_profile": {"age": 35, "cultural_context": "Western"}}')

  **reduction_claims** (0 rows)
  Columns: ['id', 'tier2_theory', 'tier2_construct', 'reduction_type', 'template_mappings', 'irreducible_residual', 'confidence', 'source_panel', 'staging_links_reconciled', 'staging_links_total']

  **cmr_template_activations** (582 rows)
  Columns: ['id', 'evaluation_id', 'template_display_id', 'activation_reason', 'inputs', 'outputs', 'wis_score', 'wis_confidence', 'interaction_adjustments']
    (1, 1, 'CB2', 'auto: sufficient input features', '{"measured_features": {"ceiling_height_m": 3.0, "floor_area_m2": 25.0, "illuminance_lux": 400, "ambient_noise_dba": 45}, "occupant_profile": {"age": 35, "cultural_context": "Western"}}', '{"wis": 50.0}', 50.0, 5.0, '[]')
    (2, 1, 'COL1', 'auto: sufficient input features', '{"measured_features": {"ceiling_height_m": 3.0, "floor_area_m2": 25.0, "illuminance_lux": 400, "ambient_noise_dba": 45}, "occupant_profile": {"age": 35, "cultural_context": "Western"}}', '{"wis": 50.0}', 50.0, 5.0, '[]')
    (3, 1, 'COL2', 'auto: sufficient input features', '{"measured_features": {"ceiling_height_m": 3.0, "floor_area_m2": 25.0, "illuminance_lux": 400, "ambient_noise_dba": 45}, "occupant_profile": {"age": 35, "cultural_context": "Western"}}', '{"wis": 50.0}', 50.0, 5.0, '[]')

  **cmr_domain_scores** (327 rows)
  Columns: ['id', 'evaluation_id', 'domain', 'wis_score', 'wis_confidence', 'n_templates_activated', 'template_ids', 'aggregation_method', 'weight_basis']
    (1, 1, 'CB', 50.0, 0.2, 1, 'CB2', 'weighted_average', 'calibration_confidence')
    (2, 1, 'COL', 50.0, 0.4, 2, 'COL1,COL2', 'weighted_average', 'calibration_confidence')
    (3, 1, 'CREA', 50.0, 2.8, 4, 'CREA1,CREA2,CREA3,CREA4', 'weighted_average', 'calibration_confidence')

  **cmr_overall_scores** (46 rows)
  Columns: ['id', 'evaluation_id', 'wis_geometric_mean', 'wis_confidence', 'n_domains_assessed', 'severe_deficit_domains', 'data_gaps']
    (1, 1, 49.99999999999999, 30.0, 6, '', '')
    (2, 2, 49.99999999999999, 30.0, 6, '', '')
    (3, 3, 49.99999999999999, 30.0, 6, '', '')

  **web_metadata** (0 rows)
  Columns: ['web_id', 'name', 'description', 'created_at', 'updated_at', 'version', 'n_beliefs', 'n_constraints', 'coherence_score', 'is_master']

  **beliefs** (0 rows)
  Columns: ['belief_id', 'web_id', 'content', 'level', 'status', 'credence_value', 'credence_uncertainty', 'credence_n_supporting', 'credence_n_contradicting', 'credence_n_observations', 'theory_id', 'entrenchment', 'domain', 'attribute_id', 'outcome_type', 'scope', 'environment_id', 'outcome_id', 'evidence_cluster_id', 'tags', 'paper_ids', 'epistemic_v2', 'created_at', 'updated_at']

  **constraints** (0 rows)
  Columns: ['constraint_id', 'web_id', 'source_id', 'target_id', 'constraint_type', 'strength', 'bidirectional', 'evidence_ids', 'warrant_type', 'provenance', 'created_at']

  **bridges** (0 rows)
  Columns: ['bridge_id', 'web_id', 'source_domain', 'target_domain', 'bridge_type', 'warrant_statement', 'assumed_mechanism', 'confidence', 'confidence_source', 'status', 'source_beliefs', 'target_beliefs', 'evidence_for', 'evidence_against', 'failure_record', 'voi_flag', 'created_at', 'updated_at']

  **paper_integrations** (0 rows)
  Columns: ['integration_id', 'web_id', 'paper_id', 'run_id', 'n_beliefs_added', 'n_beliefs_updated', 'n_constraints_added', 'coherence_before', 'coherence_after', 'status', 'integrated_at']

  **paper_publication** (0 rows)
  Columns: ['paper_id', 'publication_year', 'publication_date', 'first_seen_at', 'source', 'created_at', 'updated_at']

  **entrenchment_snapshots** (0 rows)
  Columns: ['snapshot_id', 'web_id', 'belief_id', 'paper_id', 'timeline_type', 'as_of_date', 'entrenchment', 'connectivity', 'level_weight', 'coherence_contrib', 'constraint_count', 'status', 'credence_value', 'credence_uncertainty', 'created_at']

  **entrenchment_events** (0 rows)
  Columns: ['event_id', 'web_id', 'belief_id', 'paper_id', 'timeline_type', 'occurred_at', 'delta', 'event_type', 'reason', 'source_paper_id', 'constraint_id', 'created_at']

  **coherence_history** (0 rows)
  Columns: ['history_id', 'web_id', 'coherence_score', 'n_beliefs', 'n_constraints', 'recorded_at', 'triggered_by']

  **local_coherence_history** (0 rows)
  Columns: ['history_id', 'web_id', 'theory_id', 'local_coherence', 'n_beliefs', 'n_constraints', 'recorded_at']

  **belief_merge_log** (0 rows)
  Columns: ['merge_id', 'web_id', 'belief_id', 'merge_type', 'conflict_type', 'old_credence', 'new_credence', 'source_paper_id', 'merge_reason', 'auto_resolved', 'requires_review', 'merged_at']

  **paper_quality** (0 rows)
  Columns: ['paper_id', 'sample_size_score', 'methodology_score', 'journal_impact_factor', 'citation_count', 'preregistered', 'replication_status', 'overall_quality', 'institution', 'author_h_index', 'publication_year', 'ecological_validity_score', 'created_at', 'updated_at']

  **web_snapshots** (0 rows)
  Columns: ['snapshot_id', 'web_id', 'snapshot_data', 'n_beliefs', 'n_constraints', 'coherence_score', 'snapshot_reason', 'created_at']

  **coherence_alerts** (0 rows)
  Columns: ['alert_id', 'web_id', 'alert_type', 'severity', 'message', 'coherence_before', 'coherence_after', 'triggered_by', 'acknowledged', 'created_at']

  **cmr_paper_records** (4 rows)
  Columns: ['id', 'citation', 'doi', 'evaluated_at', 'n_claims', 'n_matched', 'n_unmatched', 'n_contradictions', 'n_confirmations', 'n_gaps', 'aggregate_voi', 'proposals_generated', 'matched_template_ids']
    (1, None, None, '2026-02-17 18:40:55', 2, 2, 0, 1, 0, 0, 0.65, 3, '["CREA2", "VF3", "VIEW1"]')
    (2, None, None, '2026-02-17 18:40:55', 2, 2, 0, 1, 0, 0, 0.65, 3, '["CREA2", "VF3", "VIEW1"]')
    (3, 'Ulrich, R.S. (1984). View through a window may influence recovery from surgery.', '10.1126/science.6143402', '2026-02-17 19:25:10', 2, 2, 0, 0, 0, 0, 0.6, 2, '["VIEW1"]')

  **cmr_update_proposals** (0 rows)
  Columns: ['id', 'proposal_id', 'proposal_type', 'template_id', 'parameter_name', 'current_value', 'proposed_value', 'evidence_summary', 'paper_citation', 'effect_size', 'sample_n', 'confidence', 'impact_assessment', 'requires_human_review', 'status', 'created_at', 'updated_at', 'reviewed_by', 'review_notes']

**Found DB: alerts.db** (0.0 MB)
  Tables: ['watches', 'alerts']

  **watches** (0 rows)
  Columns: ['watch_id', 'name', 'target_type', 'target_id', 'conditions', 'notify_webhook', 'notify_email', 'notify_in_app', 'cooldown_minutes', 'last_triggered', 'retention_days', 'created_at', 'created_by', 'enabled', 'description']

  **alerts** (0 rows)
  Columns: ['alert_id', 'watch_id', 'alert_type', 'severity', 'status', 'entity_type', 'entity_id', 'entity_content', 'old_value', 'new_value', 'change_description', 'triggered_at', 'delivered_at', 'acknowledged_at', 'acknowledged_by', 'context']

**Found DB: data/web_persistence.db** (83.0 MB)
  Tables: ['web_metadata', 'beliefs', 'constraints', 'bridges', 'paper_integrations', 'sqlite_sequence', 'paper_publication', 'entrenchment_snapshots', 'entrenchment_events', 'coherence_history', 'local_coherence_history', 'belief_merge_log', 'paper_quality', 'web_snapshots', 'coherence_alerts']

  **web_metadata** (1 rows)
  Columns: ['web_id', 'name', 'description', 'created_at', 'updated_at', 'version', 'n_beliefs', 'n_constraints', 'coherence_score', 'is_master']
    ('master:web:accumulated', 'Master Accumulated Web', 'Accumulated web of belief from all processed papers', '2026-02-13T18:32:32.365982+00:00', '2026-02-17T18:17:15.970855+00:00', 3307, 12628, 28314, 0.41604, 1)

  **beliefs** (12628 rows)
  Columns: ['belief_id', 'web_id', 'content', 'level', 'status', 'credence_value', 'credence_uncertainty', 'credence_n_supporting', 'credence_n_contradicting', 'credence_n_observations', 'theory_id', 'entrenchment', 'domain', 'attribute_id', 'outcome_type', 'scope', 'environment_id', 'outcome_id', 'evidence_cluster_id', 'tags', 'paper_ids', 'epistemic_v2', 'created_at', 'updated_at']
    ('pdf:doi:10.17863/cam.41365:doi:10.17863/cam.41365-TBL-C003', 'master:web:accumulated', ': Location C; Microphone 1: 52.4 dB(A); Microphone 2: 51.3 dB(A); Microphone 3: 52.4 dB(A); Microphone 4: 51.6 dB(A)', 'empirical', 'tentative', 0.6000000000000001, 0.11338934190276817, 0, 0, 7, None, 0.5, 'realtime_pdf', None, None, None, 'env.unresolved.location_microphone_microphone', 'out.unresolved.location_microphone_microphone', None, '["source:pdf", "provenance:pdf_confirmed", "requires_pdf_confirma...
    ('pdf:doi:10.17863/cam.41365:doi:10.17863/cam.41365-TBL-C004', 'master:web:accumulated', 'age: 18.2 – 18.5; age: 76 – 82; age: 1009.3 – 1018.9', 'empirical', 'established', 0.8500000000000001, 0.11338934190276817, 0, 0, 7, None, 0.5, 'realtime_pdf', None, None, None, 'env.unresolved.age_age_age', 'out.unresolved.age_age_age', None, '["source:pdf", "provenance:pdf_confirmed", "requires_pdf_confirmation:false"]', '["doi:10.17863/cam.41365"]', None, '2026-02-17T18:17:15.597310+00:00', '2026-02-17T1...
    ('pdf:doi:10.17863/cam.41365:doi:10.17863/cam.41365-TBL-C005', 'master:web:accumulated', 'age: 17.0 – 19.2; age: 70 - 84; age: 1008.0 – 1020.2', 'empirical', 'established', 0.8500000000000001, 0.11338934190276817, 0, 0, 7, None, 0.5, 'realtime_pdf', None, None, None, 'env.unresolved.age_age_age', 'out.unresolved.age_age_age', None, '["source:pdf", "provenance:pdf_confirmed", "requires_pdf_confirmation:false"]', '["doi:10.17863/cam.41365"]', None, '2026-02-17T18:17:15.597322+00:00', '2026-02-17T1...

  **constraints** (28314 rows)
  Columns: ['constraint_id', 'web_id', 'source_id', 'target_id', 'constraint_type', 'strength', 'bidirectional', 'evidence_ids', 'warrant_type', 'provenance', 'created_at']
    ('c:arg:4daef552f12bce54de2f', 'master:web:accumulated', 'rt:doi:10.1371/journal.pone.0307934:abstract_rule', 'pdf:zotero:F4X7UZLU:zotero:F4X7UZLU-TBL-C018', 'explains', 0.48000000000000004, 0, '["doi:10.1371/journal.pone.0307934"]', 'cross_paper_alignment', 'cross_paper:shared_env_out|argument:default_contextual|temporal:maturation_lag_9', '2026-02-17T18:17:25.319211+00:00')
    ('c:arg:91dbe0830eff46e2c523', 'master:web:accumulated', 'rt:doi:10.1371/journal.pone.0307934:abstract_rule', 'pdf:zotero:F4X7UZLU:zotero:F4X7UZLU-TBL-C017', 'explains', 0.48000000000000004, 0, '["doi:10.1371/journal.pone.0307934"]', 'cross_paper_alignment', 'cross_paper:shared_env_out|argument:default_contextual|temporal:maturation_lag_9', '2026-02-17T18:17:25.322629+00:00')
    ('c:arg:df6247f791d7daa33536', 'master:web:accumulated', 'rt:doi:10.1371/journal.pone.0307934:abstract_rule', 'pdf:zotero:F4X7UZLU:zotero:F4X7UZLU-TBL-C016', 'explains', 0.48000000000000004, 0, '["doi:10.1371/journal.pone.0307934"]', 'cross_paper_alignment', 'cross_paper:shared_env_out|argument:default_contextual|temporal:maturation_lag_9', '2026-02-17T18:17:25.323235+00:00')

  **bridges** (1555 rows)
  Columns: ['bridge_id', 'web_id', 'source_domain', 'target_domain', 'bridge_type', 'warrant_statement', 'assumed_mechanism', 'confidence', 'confidence_source', 'status', 'source_beliefs', 'target_beliefs', 'evidence_for', 'evidence_against', 'failure_record', 'voi_flag', 'created_at', 'updated_at']
    ('bridge:environmental_psychology_architectural_perception_08c459e6', 'master:web:accumulated', 'environmental_psychology', 'architectural_perception', 'analogical', 'Finding from environmental_psychology may transfer to architectural_perception', None, 0.35, 'default', 'hypothesized', '["pdf:doi:10.1080/17508975.2020.1732859:doi:10.1080/17508975.2020.1732859-TBL-C004"]', '["rt:doi:10.1080/17508975.2020.1732859:abstract_rule"]', '[]', '[]', None, 0, '2026-02-14T02:49:18.895651+00:00', '2026-02-1...
    ('bridge:affect_architectural_perception_eb9eed1e', 'master:web:accumulated', 'affect', 'architectural_perception', 'functional', 'Finding from affect may transfer to architectural_perception', None, 0.5, 'default', 'hypothesized', '["pdf:doi:10.1080/17508975.2020.1732859:doi:10.1080/17508975.2020.1732859-TBL-C012"]', '["rt:doi:10.1080/17508975.2020.1732859:abstract_rule"]', '[]', '[]', None, 0, '2026-02-14T02:49:18.895756+00:00', '2026-02-14T02:49:19.091182+00:00')
    ('bridge:cognition_architectural_perception_5c859125', 'master:web:accumulated', 'cognition', 'architectural_perception', 'analogical', 'Finding from cognition may transfer to architectural_perception', None, 0.35, 'default', 'hypothesized', '["rt:doi:10.1186/s41235-020-00243-4:abstract_rule"]', '["rt:doi:10.1186/s41235-020-00243-4:abstract_rule"]', '[]', '[]', None, 0, '2026-02-14T02:49:49.724337+00:00', '2026-02-14T02:49:49.844136+00:00')

  **paper_integrations** (3300 rows)
  Columns: ['integration_id', 'web_id', 'paper_id', 'run_id', 'n_beliefs_added', 'n_beliefs_updated', 'n_constraints_added', 'coherence_before', 'coherence_after', 'status', 'integrated_at']
    (1, 'master:web:accumulated', 'doi:10.1109/HiPC56025.2022.00044', None, 1, 0, 0, 0.41604, 0.5, 'active', '2026-02-13T18:32:32.373058+00:00')
    (2, 'master:web:accumulated', 'doi:10.1109/ICMCIS52405.2021.9486392', None, 1, 0, 0, 0.41604, 0.5, 'active', '2026-02-13T18:32:32.383992+00:00')
    (3, 'master:web:accumulated', 'doi:10.1109/JSEN.2018.2839558', None, 1, 0, 0, 0.41604, 0.5, 'active', '2026-02-13T18:32:32.394944+00:00')

  **sqlite_sequence** (6 rows)
  Columns: ['name', 'seq']
    ('belief_merge_log', 46057)
    ('coherence_history', 3301)
    ('entrenchment_snapshots', 50851)

  **paper_publication** (1172 rows)
  Columns: ['paper_id', 'publication_year', 'publication_date', 'first_seen_at', 'source', 'created_at', 'updated_at']
    ('doi:10.1109/HiPC56025.2022.00044', None, None, '2026-02-13T18:32:32.366427+00:00', None, '2026-02-13T18:32:32.366857+00:00', '2026-02-13T18:34:43.618991+00:00')
    ('doi:10.1109/ICMCIS52405.2021.9486392', None, None, '2026-02-13T18:32:32.376724+00:00', None, '2026-02-13T18:32:32.377201+00:00', '2026-02-13T18:34:43.761154+00:00')
    ('doi:10.1109/JSEN.2018.2839558', None, None, '2026-02-13T18:32:32.387575+00:00', None, '2026-02-13T18:32:32.387984+00:00', '2026-02-13T18:34:43.907435+00:00')

  **entrenchment_snapshots** (50851 rows)
  Columns: ['snapshot_id', 'web_id', 'belief_id', 'paper_id', 'timeline_type', 'as_of_date', 'entrenchment', 'connectivity', 'level_weight', 'coherence_contrib', 'constraint_count', 'status', 'credence_value', 'credence_uncertainty', 'created_at']
    (1, 'master:web:accumulated', 'rt:doi:10.1109/HiPC56025.2022.00044:abstract_rule', 'doi:10.1109/HiPC56025.2022.00044', 'system', '2026-02-13T18:32:32.366427+00:00', 0.1725, 0.0, 0.3, 0.275, 0, 'tentative', 0.5, 0.45, '2026-02-13T18:32:32.372460+00:00')
    (2, 'master:web:accumulated', 'rt:doi:10.1109/ICMCIS52405.2021.9486392:abstract_rule', 'doi:10.1109/ICMCIS52405.2021.9486392', 'system', '2026-02-13T18:32:32.376724+00:00', 0.1725, 0.0, 0.3, 0.275, 0, 'tentative', 0.5, 0.45, '2026-02-13T18:32:32.383421+00:00')
    (3, 'master:web:accumulated', 'rt:doi:10.1109/JSEN.2018.2839558:abstract_rule', 'doi:10.1109/JSEN.2018.2839558', 'system', '2026-02-13T18:32:32.387575+00:00', 0.14775, 0.0, 0.3, 0.1925, 0, 'tentative', 0.35, 0.45, '2026-02-13T18:32:32.394386+00:00')

  **entrenchment_events** (40182 rows)
  Columns: ['event_id', 'web_id', 'belief_id', 'paper_id', 'timeline_type', 'occurred_at', 'delta', 'event_type', 'reason', 'source_paper_id', 'constraint_id', 'created_at']
    (1, 'master:web:accumulated', 'rt:doi:10.1038/s41598-022-20649-y:abstract_rule', 'doi:10.1038/s41598-022-20649-y', 'system', '2026-02-13T18:34:33.962330+00:00', 0.09399222663354112, 'integration', 'paper_integration', 'doi:10.1038/s41598-022-20649-y', None, '2026-02-13T18:34:34.089314+00:00')
    (2, 'master:web:accumulated', 'rt:doi:10.1109/HiPC56025.2022.00044:abstract_rule', 'doi:10.1109/HiPC56025.2022.00044', 'system', '2026-02-13T18:34:43.618487+00:00', 0.019770292269908063, 'integration', 'paper_integration', 'doi:10.1109/HiPC56025.2022.00044', None, '2026-02-13T18:34:43.747315+00:00')
    (3, 'master:web:accumulated', 'rt:doi:10.1109/ICMCIS52405.2021.9486392:abstract_rule', 'doi:10.1109/ICMCIS52405.2021.9486392', 'system', '2026-02-13T18:34:43.760743+00:00', 0.019770292269908063, 'integration', 'paper_integration', 'doi:10.1109/ICMCIS52405.2021.9486392', None, '2026-02-13T18:34:43.894009+00:00')

  **coherence_history** (3301 rows)
  Columns: ['history_id', 'web_id', 'coherence_score', 'n_beliefs', 'n_constraints', 'recorded_at', 'triggered_by']
    (1, 'master:web:accumulated', 0.5, 1, 0, '2026-02-13T18:32:32.371658+00:00', 'save')
    (2, 'master:web:accumulated', 0.5, 2, 0, '2026-02-13T18:32:32.382704+00:00', 'save')
    (3, 'master:web:accumulated', 0.5, 3, 0, '2026-02-13T18:32:32.393682+00:00', 'save')

  **local_coherence_history** (0 rows)
  Columns: ['history_id', 'web_id', 'theory_id', 'local_coherence', 'n_beliefs', 'n_constraints', 'recorded_at']

  **belief_merge_log** (46057 rows)
  Columns: ['merge_id', 'web_id', 'belief_id', 'merge_type', 'conflict_type', 'old_credence', 'new_credence', 'source_paper_id', 'merge_reason', 'auto_resolved', 'requires_review', 'merged_at']
    (1, 'master:web:accumulated', 'rt:doi:10.1109/HiPC56025.2022.00044:abstract_rule', 'new', None, None, 0.5, 'doi:10.1109/HiPC56025.2022.00044', 'New belief added', 1, 0, '2026-02-13T18:32:32.369291+00:00')
    (2, 'master:web:accumulated', 'rt:doi:10.1109/ICMCIS52405.2021.9486392:abstract_rule', 'new', None, None, 0.5, 'doi:10.1109/ICMCIS52405.2021.9486392', 'New belief added', 1, 0, '2026-02-13T18:32:32.379725+00:00')
    (3, 'master:web:accumulated', 'rt:doi:10.1109/JSEN.2018.2839558:abstract_rule', 'new', None, None, 0.35, 'doi:10.1109/JSEN.2018.2839558', 'New belief added', 1, 0, '2026-02-13T18:32:32.390357+00:00')

  **paper_quality** (0 rows)
  Columns: ['paper_id', 'sample_size_score', 'methodology_score', 'journal_impact_factor', 'citation_count', 'preregistered', 'replication_status', 'overall_quality', 'institution', 'author_h_index', 'publication_year', 'ecological_validity_score', 'created_at', 'updated_at']

  **web_snapshots** (0 rows)
  Columns: ['snapshot_id', 'web_id', 'snapshot_data', 'n_beliefs', 'n_constraints', 'coherence_score', 'snapshot_reason', 'created_at']

  **coherence_alerts** (690 rows)
  Columns: ['alert_id', 'web_id', 'alert_type', 'severity', 'message', 'coherence_before', 'coherence_after', 'triggered_by', 'acknowledged', 'created_at']
    (1, 'master:web:accumulated', 'sharp_decline', 'warning', 'Coherence dropped by 0.143 after integrating doi:10.1038/s41598-022-20649-y', 0.41604, 0.27330119142850307, 'doi:10.1038/s41598-022-20649-y', 0, '2026-02-14T08:25:18.236342+00:00')
    (2, 'master:web:accumulated', 'sharp_decline', 'warning', 'Coherence dropped by 0.143 after integrating doi:10.1080/17508975.2020.1732859', 0.41604, 0.2733030162831068, 'doi:10.1080/17508975.2020.1732859', 0, '2026-02-14T08:25:36.788993+00:00')
    (3, 'master:web:accumulated', 'sharp_decline', 'warning', 'Coherence dropped by 0.143 after integrating doi:10.1371/journal.pone.0307934', 0.41604, 0.2732869877899075, 'doi:10.1371/journal.pone.0307934', 0, '2026-02-14T08:25:56.050058+00:00')

**Found DB: data/production/rebuild_backup_20260213_193206/web_persistence.db** (12.6 MB)
  Tables: ['web_metadata', 'beliefs', 'constraints', 'bridges', 'paper_integrations', 'sqlite_sequence', 'paper_publication', 'entrenchment_snapshots', 'entrenchment_events', 'coherence_history', 'local_coherence_history', 'belief_merge_log', 'paper_quality', 'web_snapshots', 'coherence_alerts']

  **web_metadata** (1 rows)
  Columns: ['web_id', 'name', 'description', 'created_at', 'updated_at', 'version', 'n_beliefs', 'n_constraints', 'coherence_score', 'is_master']
    ('master:web:accumulated', 'Master Accumulated Web', 'Accumulated web of belief from all processed papers', '2026-02-11T14:41:28.361421+00:00', '2026-02-13T18:32:05.053213+00:00', 4599, 4730, 30, 0.2763500000000001, 1)

  **beliefs** (4730 rows)
  Columns: ['belief_id', 'web_id', 'content', 'level', 'status', 'credence_value', 'credence_uncertainty', 'credence_n_supporting', 'credence_n_contradicting', 'credence_n_observations', 'theory_id', 'entrenchment', 'domain', 'attribute_id', 'outcome_type', 'scope', 'environment_id', 'outcome_id', 'evidence_cluster_id', 'tags', 'paper_ids', 'created_at', 'updated_at', 'epistemic_v2']
    ('rt:doi:10.3389/fpsyg.2018.01129:abstract_rule', 'master:web:accumulated', 'Abstract-provisional: noise -> mood (positive)', 'empirical', 'tentative', 0.5, 0.45, 0, 0, 0, None, 0.5, 'realtime_abstract', None, None, None, 'env.noise', 'out.mood', None, '["source:abstract", "provenance:abstract_provisional", "requires_pdf_confirmation:true"]', '["doi:10.3389/fpsyg.2018.01129"]', '2026-02-13T18:32:01.683724+00:00', '2026-02-13T18:32:02.986841+00:00', None)
    ('rt:doi:10.3389/fpsyg.2023.1192842:abstract_rule', 'master:web:accumulated', 'Abstract-provisional: unspecified_environment -> mood (unknown)', 'empirical', 'tentative', 0.35, 0.45, 0, 0, 0, None, 0.5, 'realtime_abstract', None, None, None, 'env.unspecified_environment', 'out.mood', None, '["source:abstract", "provenance:abstract_provisional", "requires_pdf_confirmation:true"]', '["doi:10.3389/fpsyg.2023.1192842"]', '2026-02-13T18:32:01.683733+00:00', '2026-02-13T18:32:02.987387+00:00', None)
    ('rt:doi:10.3389/fpsyg.2023.1232318:abstract_rule', 'master:web:accumulated', 'Abstract-provisional: noise -> productivity (positive)', 'empirical', 'tentative', 0.5, 0.45, 0, 0, 0, None, 0.5, 'realtime_abstract', None, None, None, 'env.noise', 'out.productivity', None, '["source:abstract", "provenance:abstract_provisional", "requires_pdf_confirmation:true"]', '["doi:10.3389/fpsyg.2023.1232318"]', '2026-02-13T18:32:01.683742+00:00', '2026-02-13T18:32:02.988059+00:00', None)

  **constraints** (30 rows)
  Columns: ['constraint_id', 'web_id', 'source_id', 'target_id', 'constraint_type', 'strength', 'bidirectional', 'evidence_ids', 'warrant_type', 'provenance', 'created_at']
    ('c_b_abstract_10.1016/j.plaphy.2025.110154_1_biophilia', 'master:web:accumulated', 'b_theory_biophilia', 'b_abstract_10.1016/j.plaphy.2025.110154_1', 'explains', 0.6, 1, '[]', None, None, '2026-02-13T18:32:04.688902+00:00')
    ('c_b_abstract_10.1038/s41598-025-19113-4_1_biophilia', 'master:web:accumulated', 'b_theory_biophilia', 'b_abstract_10.1038/s41598-025-19113-4_1', 'explains', 0.6, 1, '[]', None, None, '2026-02-13T18:32:04.689489+00:00')
    ('c_b_abstract_10.1038/s41598-025-95771-8_1_art', 'master:web:accumulated', 'b_theory_art', 'b_abstract_10.1038/s41598-025-95771-8_1', 'explains', 0.6, 1, '[]', None, None, '2026-02-13T18:32:04.690029+00:00')

  **bridges** (0 rows)
  Columns: ['bridge_id', 'web_id', 'source_domain', 'target_domain', 'bridge_type', 'warrant_statement', 'assumed_mechanism', 'confidence', 'confidence_source', 'status', 'source_beliefs', 'target_beliefs', 'evidence_for', 'evidence_against', 'failure_record', 'voi_flag', 'created_at', 'updated_at']

  **paper_integrations** (4596 rows)
  Columns: ['integration_id', 'web_id', 'paper_id', 'run_id', 'n_beliefs_added', 'n_beliefs_updated', 'n_constraints_added', 'coherence_before', 'coherence_after', 'status', 'integrated_at']
    (1, 'master:web:accumulated', 'doi:10.3389/fpsyg.2023.1143618', None, 1, 0, 0, 0.41604, 0.2763500000000001, 'active', '2026-02-13T15:29:40.031217+00:00')
    (2, 'master:web:accumulated', 'doi:10.3389/fpubh.2022.842750', None, 1, 0, 0, 0.41604, 0.2763500000000001, 'active', '2026-02-13T15:29:40.163628+00:00')
    (3, 'master:web:accumulated', 'doi:10.3390/urbansci9060221', None, 1, 0, 0, 0.41604, 0.2763500000000001, 'active', '2026-02-13T15:29:40.290721+00:00')

  **sqlite_sequence** (7 rows)
  Columns: ['name', 'seq']
    ('coherence_history', 4597)
    ('belief_merge_log', 4602)
    ('coherence_alerts', 4596)

  **paper_publication** (4607 rows)
  Columns: ['paper_id', 'publication_year', 'publication_date', 'first_seen_at', 'source', 'created_at', 'updated_at']
    ('doi:10.1109/TIM.2024.3451583', None, None, '2026-02-13T15:28:32.138269+00:00', None, '2026-02-13T15:28:32.139022+00:00', '2026-02-13T15:28:32.139022+00:00')
    ('doi:10.1145/3610977.3637484', None, None, '2026-02-13T15:28:32.145788+00:00', None, '2026-02-13T15:28:32.146178+00:00', '2026-02-13T15:28:32.146178+00:00')
    ('doi:10.1155/2019/3476490', None, None, '2026-02-13T15:28:32.150826+00:00', None, '2026-02-13T15:28:32.151206+00:00', '2026-02-13T15:28:32.151206+00:00')

  **entrenchment_snapshots** (4607 rows)
  Columns: ['snapshot_id', 'web_id', 'belief_id', 'paper_id', 'timeline_type', 'as_of_date', 'entrenchment', 'connectivity', 'level_weight', 'coherence_contrib', 'constraint_count', 'status', 'credence_value', 'credence_uncertainty', 'created_at']
    (1, 'master:web:accumulated', 'rt:doi:10.3389/fpsyg.2023.1143618:abstract_rule', 'doi:10.3389/fpsyg.2023.1143618', 'system', '2026-02-13T15:29:39.917988+00:00', 0.1725, 0.0, 0.3, 0.275, 0, 'tentative', 0.5, 0.45, '2026-02-13T15:29:40.030613+00:00')
    (2, 'master:web:accumulated', 'rt:doi:10.3389/fpubh.2022.842750:abstract_rule', 'doi:10.3389/fpubh.2022.842750', 'system', '2026-02-13T15:29:40.041527+00:00', 0.1725, 0.0, 0.3, 0.275, 0, 'tentative', 0.5, 0.45, '2026-02-13T15:29:40.162939+00:00')
    (3, 'master:web:accumulated', 'rt:doi:10.3390/urbansci9060221:abstract_rule', 'doi:10.3390/urbansci9060221', 'system', '2026-02-13T15:29:40.174124+00:00', 0.1725, 0.0, 0.3, 0.275, 0, 'tentative', 0.5, 0.45, '2026-02-13T15:29:40.289960+00:00')

  **entrenchment_events** (3 rows)
  Columns: ['event_id', 'web_id', 'belief_id', 'paper_id', 'timeline_type', 'occurred_at', 'delta', 'event_type', 'reason', 'source_paper_id', 'constraint_id', 'created_at']
    (1, 'master:web:accumulated', 'rt:doi:10.3390/ijerph20021082:abstract_rule', 'doi:10.3390/ijerph20021082', 'system', '2026-02-13T16:13:03.336241+00:00', 0.0, 'integration', 'paper_integration', 'doi:10.3390/ijerph20021082', None, '2026-02-13T16:13:04.710419+00:00')
    (2, 'master:web:accumulated', 'rt:doi:10.1257/app.20220532:abstract_rule', 'doi:10.1257/app.20220532', 'system', '2026-02-13T16:21:19.416207+00:00', 0.0, 'integration', 'paper_integration', 'doi:10.1257/app.20220532', None, '2026-02-13T16:21:20.927306+00:00')
    (3, 'master:web:accumulated', 'rt:doi:10.1038/s41598-019-46099-7:abstract_rule', 'doi:10.1038/s41598-019-46099-7', 'system', '2026-02-13T17:48:42.475536+00:00', 0.0, 'integration', 'paper_integration', 'doi:10.1038/s41598-019-46099-7', None, '2026-02-13T17:48:45.533331+00:00')

  **coherence_history** (4597 rows)
  Columns: ['history_id', 'web_id', 'coherence_score', 'n_beliefs', 'n_constraints', 'recorded_at', 'triggered_by']
    (1, 'master:web:accumulated', 0.2763500000000001, 120, 30, '2026-02-11T14:46:21.799412+00:00', 'save')
    (2, 'master:web:accumulated', 0.2763500000000001, 129, 30, '2026-02-13T15:29:40.028973+00:00', 'save')
    (3, 'master:web:accumulated', 0.2763500000000001, 130, 30, '2026-02-13T15:29:40.161177+00:00', 'save')

  **local_coherence_history** (22980 rows)
  Columns: ['history_id', 'web_id', 'theory_id', 'local_coherence', 'n_beliefs', 'n_constraints', 'recorded_at']
    (1, 'master:web:accumulated', 'ceiling-priming', 0.5, 1, 0, '2026-02-13T15:29:40.030096+00:00')
    (2, 'master:web:accumulated', 'ART', 0.5, 1, 0, '2026-02-13T15:29:40.030096+00:00')
    (3, 'master:web:accumulated', 'biophilia', 0.5, 1, 0, '2026-02-13T15:29:40.030096+00:00')

  **belief_merge_log** (4602 rows)
  Columns: ['merge_id', 'web_id', 'belief_id', 'merge_type', 'conflict_type', 'old_credence', 'new_credence', 'source_paper_id', 'merge_reason', 'auto_resolved', 'requires_review', 'merged_at']
    (1, 'master:web:accumulated', 'rt:doi:10.3389/fpsyg.2023.1143618:abstract_rule', 'new', None, None, 0.5, 'doi:10.3389/fpsyg.2023.1143618', 'New belief added', 1, 0, '2026-02-13T15:29:39.923821+00:00')
    (2, 'master:web:accumulated', 'rt:doi:10.3389/fpubh.2022.842750:abstract_rule', 'new', None, None, 0.5, 'doi:10.3389/fpubh.2022.842750', 'New belief added', 1, 0, '2026-02-13T15:29:40.046168+00:00')
    (3, 'master:web:accumulated', 'rt:doi:10.3390/urbansci9060221:abstract_rule', 'new', None, None, 0.5, 'doi:10.3390/urbansci9060221', 'New belief added', 1, 0, '2026-02-13T15:29:40.179664+00:00')

  **paper_quality** (0 rows)
  Columns: ['paper_id', 'sample_size_score', 'methodology_score', 'journal_impact_factor', 'citation_count', 'preregistered', 'replication_status', 'overall_quality', 'institution', 'author_h_index', 'publication_year', 'ecological_validity_score', 'created_at', 'updated_at']

  **web_snapshots** (0 rows)
  Columns: ['snapshot_id', 'web_id', 'snapshot_data', 'n_beliefs', 'n_constraints', 'coherence_score', 'snapshot_reason', 'created_at']

  **coherence_alerts** (4596 rows)
  Columns: ['alert_id', 'web_id', 'alert_type', 'severity', 'message', 'coherence_before', 'coherence_after', 'triggered_by', 'acknowledged', 'created_at']
    (1, 'master:web:accumulated', 'sharp_decline', 'warning', 'Coherence dropped by 0.140 after integrating doi:10.3389/fpsyg.2023.1143618', 0.41604, 0.2763500000000001, 'doi:10.3389/fpsyg.2023.1143618', 0, '2026-02-13T15:29:40.029374+00:00')
    (2, 'master:web:accumulated', 'sharp_decline', 'warning', 'Coherence dropped by 0.140 after integrating doi:10.3389/fpubh.2022.842750', 0.41604, 0.2763500000000001, 'doi:10.3389/fpubh.2022.842750', 0, '2026-02-13T15:29:40.161596+00:00')
    (3, 'master:web:accumulated', 'sharp_decline', 'warning', 'Coherence dropped by 0.140 after integrating doi:10.3390/urbansci9060221', 0.41604, 0.2763500000000001, 'doi:10.3390/urbansci9060221', 0, '2026-02-13T15:29:40.288528+00:00')

**Found DB: data/image_pool/image_pool.db** (0.1 MB)
  Tables: ['images', 'download_log', 'sqlite_sequence', 'tags']

  **images** (13 rows)
  Columns: ['image_id', 'source', 'source_id', 'source_url', 'local_path', 'thumbnail_path', 'query_used', 'width', 'height', 'photographer', 'photographer_url', 'license_type', 'attribution', 'feature_tags', 'context_tags', 'user_tags', 'feature_scores', 'downloaded_at', 'tagged_at', 'notes']
    ('img_9f2e6d8d821e', 'unsplash', 'yWwob8kwOCk', 'https://unsplash.com/photos/hallway-between-glass-panel-doors-yWwob8kwOCk', 'data/image_pool/images/img_9f2e6d8d821e.jpg', 'data/image_pool/thumbnails/thumb_img_9f2e6d8d821e.jpg', 'modern office interior', 2301, 1536, 'Nastuh Abootalebi', 'https://unsplash.com/@sunday_digital', 'Unsplash License', 'Photo by Nastuh Abootalebi on Unsplash', '[]', '[]', '[]', '{}', '2026-01-30T07:54:42.428371', None, '')
    ('img_111deefed193', 'unsplash', 'U2BI3GMnSSE', 'https://unsplash.com/photos/man-and-woman-sitting-on-table-U2BI3GMnSSE', 'data/image_pool/images/img_111deefed193.jpg', 'data/image_pool/thumbnails/thumb_img_111deefed193.jpg', 'modern office interior', 5000, 3335, 'LYCS Architecture', 'https://unsplash.com/@lycs', 'Unsplash License', 'Photo by LYCS Architecture on Unsplash', '[]', '[]', '[]', '{}', '2026-01-30T07:54:44.523237', None, '')
    ('img_121e2910416e', 'unsplash', 'FV3GConVSss', 'https://unsplash.com/photos/black-floor-lamp-on-living-room-sofa-FV3GConVSss', 'data/image_pool/images/img_121e2910416e.jpg', 'data/image_pool/thumbnails/thumb_img_121e2910416e.jpg', 'modern office interior', 3762, 2508, 'Toa Heftiba', 'https://unsplash.com/@heftiba', 'Unsplash License', 'Photo by Toa Heftiba on Unsplash', '[]', '[]', '[]', '{}', '2026-01-30T07:54:45.770103', None, '')

  **download_log** (9 rows)
  Columns: ['id', 'query', 'source', 'count_requested', 'count_downloaded', 'timestamp']
    (1, 'cozy reading nook', 'unsplash', 5, 5, '2026-01-28T07:16:08.302563')
    (2, 'open plan office', 'pexels', 5, 5, '2026-01-28T07:16:18.319336')
    (3, 'interior room of building', 'unsplash', 20, 15, '2026-01-29T14:33:27.836614')

  **sqlite_sequence** (1 rows)
  Columns: ['name', 'seq']
    ('download_log', 9)

  **tags** (0 rows)
  Columns: ['tag_id', 'tag_name', 'tag_category', 'description', 'created_at']

================================================================================
## PART 5: WHAT THE PIPELINE CONSUMES
================================================================================


### Paper eval claim structure (from src/cmr/)


**Found `def match_claims` in `src/cmr/template_matching.py`**
  61: 
  62: 
  63: def match_claims_via_reduction(claims: list[dict], template_index: dict[str, dict]) -> list[dict]:
  64:     results: list[dict] = []
  65:     for claim in claims:
  66:         match_info: list[dict] = []
  67:         reduction_key = _reduce_construct_from_claim(claim)
  68:         if reduction_key:
  69:             reduction = reduce_construct(*reduction_key)
  70:             if reduction:
  71:                 for mapping in reduction.get("template_mappings", []):
  72:                     tid = mapping.get("template_id")
  73:                     if not tid:
  74:                         continue
  75:                     coverage = float(mapping.get("coverage", 0.0) or 0.0)
  76:                     match_info.append(
  77:                         {
  78:                             "template_id": tid,
  79:                             "match_type": "reduction",
  80:                             "confidence": min(1.0, max(0.0, coverage)),
  81:                             "rationale": mapping.get("mechanism", "") or reduction.get("irreducible_residual", ""),
  82:                         }
  83:                     )
  84:         results.append({"claim": claim, "matches": match_info})
  85:     return results
  86: 
  87: 
  88: 
  89: _SYNONYM_GROUPS = [
  90:     {"daylight", "illuminance", "light_level", "lux"},
  91:     {"noise", "ambient_noise", "ambient_noise_dba"},
  92:     {"nature_view", "has_nature_view", "view_quality", "green_view"},
  93:     {"creative_thinking", "creative_output", "creativity"},
  94:     {"stress_reduction", "stress", "cortisol_reduction"},
  95: ]
  96: 
  97: 
  98: def _normalize_term(value: str | None) -> str:
  99:     return str(value or "").strip().lower().replace("_", " ")
  100: 
  101: 
  102: def _expand_term_candidates(term: str) -> set[str]:
  ...

**Found `structured_claims` in `src/cmr/process_paper.py`**
  265:     evaluation = evaluate_paper(
  266:         paper_text="",
  267:         structured_claims=claims,
  268:         citation=citation,
  269:         doi=doi,
  270:         db_path=db_path,
  271:     )
  272: 
  273:     # Extract key metrics
  274:     n_claims = evaluation.get("n_claims_extracted", 0)
  275:     n_matched = evaluation.get("n_claims_matched", 0)
  276:     n_unmatched = evaluation.get("n_claims_unmatched", 0)
  277:     template_system_updates = evaluation.get("template_system_updates", [])
  278:     report = evaluation.get("report", {})
  279:     summary = report.get("summary", {})
  280:     recommendations = report.get("recommendations", [])
  281:     prioritized = evaluation.get("prioritized_findings", [])
  282: 
  283:     n_contradictions = summary.get("contradictions", 0)
  284:     n_confirmations = summary.get("confirmations", 0)
  285:     n_gaps = summary.get("gaps", 0)
  286:     aggregate_voi = float(summary.get("aggregate_voi", 0.0))
  287: 
  288:     # Step 2: Convert template_system_updates to formal proposals
  289:     proposals_generated = []
  290:     for update in template_system_updates:
  291:         proposal = _convert_update_to_proposal(
  292:             update=update,
  293:             citation=citation,
  294:             db_path=db_path,
  295:             persist=persist_proposals,
  296:         )
  297:         if proposal is not None:
  298:             proposals_generated.append(proposal)
  299: 
  300:     # Step 3: Extract effect data and accumulate evidence
  301:     extracted_claims = evaluation.get("claims", [])
  302:     effect_data = _extract_effect_data_from_claims(extracted_claims)
  303:     evidence_accumulated, accumulation_proposals = _accumulate_evidence_by_template(
  304:         effect_data=effect_data,
  305:         template_values=template_values,
  306:         db_path=db_path,
  ...

**Found `def process_paper` in `src/cmr/process_paper.py`**
  223: 
  224: 
  225: def process_paper(
  226:     claims: list[dict],
  227:     citation: str,
  228:     doi: Optional[str] = None,
  229:     db_path: str = "ae.db",
  230:     persist_proposals: bool = True,
  231:     include_raw_evaluation: bool = False,
  232:     template_values: Optional[dict[str, dict]] = None,
  233: ) -> ProcessingResult:
  234:     """
  235:     Process a paper through the full CMR pipeline.
  236: 
  237:     This is the MAIN ENTRY POINT for paper processing. It:
  238:     1. Evaluates the paper claims against templates
  239:     2. Generates formal update proposals from findings
  240:     3. Accumulates evidence for meta-analysis (if effect data present)
  241:     4. Records the paper in history
  242: 
  243:     Args:
  244:         claims: List of structured claim dicts with keys like:
  245:             - description: Text description of the claim
  246:             - iv: Independent variable
  247:             - dv: Dependent variable
  248:             - direction: Effect direction (increase/decrease)
  249:             - effect_size: Cohen's d or similar (optional)
  250:             - sample_n: Sample size (optional)
  251:         citation: Paper citation string (e.g., "Ulrich 1984")
  252:         doi: DOI if available
  253:         db_path: Path to SQLite database
  254:         persist_proposals: Whether to save proposals to database
  255:         include_raw_evaluation: Whether to include raw evaluation in result
  256:         template_values: Optional dict mapping template_id to current parameter values
  257:             (used for evidence accumulation comparison)
  258: 
  259:     Returns:
  260:         ProcessingResult with summary and generated proposals
  261:     """
  262:     template_values = template_values or {}
  263: 
  264:     # Step 1: Run paper evaluation
  ...

**Found `structured_claims` in `src/cmr/api.py`**
  82: class PaperEvaluationRequest(BaseModel):
  83:     paper_text: str = ""
  84:     structured_claims: list[dict[str, Any]] | None = None
  85:     citation: str | None = None
  86:     doi: str | None = None
  87:     db_path: str | None = None
  88: 
  89: 
  90: class PaperEvaluationResponse(BaseModel):
  91:     status: str
  92:     pipeline_type: str
  93:     paper_summary: str
  94:     n_claims_extracted: int
  95:     n_claims_matched: int
  96:     n_claims_unmatched: int
  97:     findings: list[dict[str, Any]] = Field(default_factory=list)
  98:     template_system_updates: list[dict[str, Any]] = Field(default_factory=list)
  99:     report: dict[str, Any] = Field(default_factory=dict)
  100: 
  101: 
  102: class CompareRequest(BaseModel):
  103:     building_a: BuildingEvaluationRequest
  104:     building_b: BuildingEvaluationRequest
  105:     label_a: str = "Current"
  106:     label_b: str = "Proposed"
  107: 
  108: 
  109: class CompareResponse(BaseModel):
  110:     label_a: str
  111:     label_b: str
  112:     overall_a: float
  113:     overall_b: float
  114:     overall_delta: float
  115:     domain_deltas: list[dict[str, Any]] = Field(default_factory=list)
  116:     top_improvements: list[dict[str, Any]] = Field(default_factory=list)
  117:     top_regressions: list[dict[str, Any]] = Field(default_factory=list)
  118: 
  119: 
  120: class SensitivityRequest(BaseModel):
  121:     baseline: BuildingEvaluationRequest
  122:     feature_variations: dict[str, list[Any]] = Field(default_factory=dict)
  123:     top_k: int = Field(default=5, ge=1, le=20)
  ...

**Found `def evaluate_paper` in `src/cmr/api.py`**
  335: 
  336:     @app.post("/evaluate/paper", response_model=PaperEvaluationResponse)
  337:     def evaluate_paper_endpoint(request: PaperEvaluationRequest) -> PaperEvaluationResponse:
  338:         db_path = _resolve_db_path(request.db_path, default_db_path)
  339:         create_tables(db_path)
  340:         payload = _as_dict(request)
  341:         if not payload.get("paper_text") and not payload.get("structured_claims"):
  342:             raise HTTPException(status_code=422, detail="Provide paper_text or structured_claims.")
  343:         result = evaluate_paper(
  344:             paper_text=payload.get("paper_text", ""),
  345:             structured_claims=payload.get("structured_claims"),
  346:             citation=payload.get("citation"),
  347:             doi=payload.get("doi"),
  348:             db_path=db_path,
  349:         )
  350:         return PaperEvaluationResponse(
  351:             status=result.get("status", "complete"),
  352:             pipeline_type=result.get("pipeline_type", "paper_evaluation"),
  353:             paper_summary=result.get("paper_summary", ""),
  354:             n_claims_extracted=int(result.get("n_claims_extracted", 0)),
  355:             n_claims_matched=int(result.get("n_claims_matched", 0)),
  356:             n_claims_unmatched=int(result.get("n_claims_unmatched", 0)),
  357:             findings=result.get("findings", []),
  358:             template_system_updates=result.get("template_system_updates", []),
  359:             report=result.get("report", {}),
  360:         )
  361: 
  362:     @app.post("/compare", response_model=CompareResponse)
  363:     def compare_endpoint(request: CompareRequest) -> CompareResponse:
  364:         first = _as_dict(request.building_a)
  365:         second = _as_dict(request.building_b)
  366:         db_a = _resolve_db_path(first.get("db_path"), default_db_path)
  367:         db_b = _resolve_db_path(second.get("db_path"), default_db_path)
  368:         create_tables(db_a)
  369:         create_tables(db_b)
  370:         _validate_minimum_building_inputs(first.get("measured_features", {}))
  371:         _validate_minimum_building_inputs(second.get("measured_features", {}))
  372: 
  373:         result_a = evaluate_building(
  374:             building_context=first.get("building_context", {}),
  375:             measured_features=first.get("measured_features", {}),
  376:             occupant_profile=_normalize_occupant_profile(first.get("occupant_profile", {})),
  ...

**Found `structured_claims` in `src/cmr/cli.py`**
  427: 
  428: 
  429: def _load_structured_claims(args: argparse.Namespace) -> list[dict] | None:
  430:     if args.claims:
  431:         payload = json.loads(args.claims)
  432:         if isinstance(payload, list):
  433:             return payload
  434:         raise ValueError("--claims must be a JSON array")
  435: 
  436:     if args.file:
  437:         with open(args.file, "r", encoding="utf-8") as handle:
  438:             payload = json.load(handle)
  439:         if isinstance(payload, list):
  440:             return payload
  441:         if isinstance(payload, dict) and isinstance(payload.get("claims"), list):
  442:             return payload["claims"]
  443:         raise ValueError("--file JSON must be an array or object with a 'claims' array")
  444: 
  445:     return None
  446: 
  447: 
  448: def run_evaluate_paper(args: argparse.Namespace) -> int:
  449:     """Execute the evaluate-paper subcommand."""
  450:     if not args.claims and not args.file and not args.text:
  451:         print(
  452:             "Error: provide at least one input source (--claims, --file, or --text).",
  453:             file=sys.stderr,
  454:         )
  455:         return 2
  456: 
  457:     try:
  458:         structured_claims = _load_structured_claims(args)
  459:         evaluation = evaluate_paper(
  460:             paper_text=args.text or "",
  461:             structured_claims=structured_claims,
  462:             db_path=args.db_path,
  463:         )
  464:         report = generate_paper_report(evaluation)
  465:     except Exception as exc:
  466:         print(f"Error during paper evaluation: {exc}", file=sys.stderr)
  467:         return 1
  468: 
  ...

**Found `structured_claims` in `src/cmr/paper_eval.py`**
  29: def _extract_claims(
  30:     paper_text: str,
  31:     structured_claims: list[dict] | None,
  32: ) -> tuple[list[dict], dict[str, Any]]:
  33:     if structured_claims:
  34:         claims = extract_claims_structured(structured_claims)
  35:         return claims, {"mode": "provided", "count": len(claims)}
  36: 
  37:     claims = extract_claims_from_text(paper_text or "")
  38:     if claims:
  39:         return claims, {"mode": "text_extraction", "count": len(claims)}
  40: 
  41:     # Backward-compatible fallback used by existing tests.
  42:     return (
  43:         [
  44:             {
  45:                 "claim_id": "placeholder_claim_1",
  46:                 "text": (paper_text or "")[:240],
  47:                 "iv": None,
  48:                 "dv": None,
  49:                 "source": "placeholder_extractor",
  50:                 "direction": "unknown",
  51:             }
  52:         ],
  53:         {"mode": "placeholder", "count": 1},
  54:     )
  55: 
  56: 
  57: def _load_active_templates(session: Session) -> list[TemplateRecord]:
  58:     return (
  59:         session.query(TemplateRecord)
  60:         .filter(TemplateRecord.dedup_status == "active")
  61:         .all()
  62:     )
  63: 
  64: 
  65: def _trace_mechanisms(claim_matches: list[dict], template_index: dict[str, dict]) -> list[dict]:
  66:     traced_claims: list[dict] = []
  67:     for entry in claim_matches:
  68:         claim = entry.get("claim", {})
  69:         traced_templates: list[dict[str, Any]] = []
  70:         for match in entry.get("matches", []):
  ...

**Found `extract_claims` in `src/cmr/paper_eval.py`**
  9: from sqlalchemy.orm import Session
  10: 
  11: from src.cmr.claim_extraction import extract_claims_from_text, extract_claims_structured
  12: from src.cmr.convergence import assess_convergence, check_composition_failures
  13: from src.cmr.mechanism_tracing import trace_claim
  14: from src.cmr.models import TemplateRecord, create_tables, get_session
  15: from src.cmr.paper_history import create_paper_record
  16: from src.cmr.template_matching import build_template_index, match_claims_to_templates
  17: from src.cmr.voi_scoring import aggregate_paper_voi, score_voi
  18: from src.services.web_persistence import WebPersistenceService
  19: 
  20: 
  21: @dataclass
  22: class PaperEvalStep:
  23:     step: int
  24:     name: str
  25:     status: str
  26:     details: dict[str, Any]
  27: 
  28: 
  29: def _extract_claims(
  30:     paper_text: str,
  31:     structured_claims: list[dict] | None,
  32: ) -> tuple[list[dict], dict[str, Any]]:
  33:     if structured_claims:
  34:         claims = extract_claims_structured(structured_claims)
  35:         return claims, {"mode": "provided", "count": len(claims)}
  36: 
  37:     claims = extract_claims_from_text(paper_text or "")
  38:     if claims:
  39:         return claims, {"mode": "text_extraction", "count": len(claims)}
  40: 
  41:     # Backward-compatible fallback used by existing tests.
  42:     return (
  43:         [
  44:             {
  45:                 "claim_id": "placeholder_claim_1",
  46:                 "text": (paper_text or "")[:240],
  47:                 "iv": None,
  48:                 "dv": None,
  49:                 "source": "placeholder_extractor",
  50:                 "direction": "unknown",
  ...

**Found `def evaluate_paper` in `src/cmr/paper_eval.py`**
  440: 
  441: 
  442: def evaluate_paper(
  443:     paper_text: str = "",
  444:     structured_claims: list[dict] | None = None,
  445:     *,
  446:     citation: str | None = None,
  447:     doi: str | None = None,
  448:     db_path: str = "ae.db",
  449:     session: Session | None = None,
  450:     web_service: WebPersistenceService | None = None,
  451: ) -> dict:
  452:     """Full paper evaluation pipeline (Doc 68 Part 3.2 Steps 1-7)."""
  453:     own_session = session is None
  454:     session = session or get_session(db_path)
  455:     create_tables(db_path)
  456: 
  457:     steps: list[PaperEvalStep] = []
  458: 
  459:     try:
  460:         # Step 1: claim extraction
  461:         claims, step1_details = _extract_claims(paper_text, structured_claims)
  462:         steps.append(PaperEvalStep(1, "claim_extraction", "complete", step1_details))
  463:         web_query_summary = _query_web_for_claims(
  464:             claims,
  465:             db_path=db_path,
  466:             web_service=web_service,
  467:         )
  468: 
  469:         # Step 2: template matching
  470:         templates = _load_active_templates(session)
  471:         template_maturity_by_id = {template.display_id: template.maturity for template in templates}
  472:         template_index = build_template_index(templates)
  473:         claim_matches = match_claims_to_templates(claims, template_index)
  474:         total_matches = sum(len(item.get("matches", [])) for item in claim_matches)
  475:         steps.append(
  476:             PaperEvalStep(
  477:                 2,
  478:                 "template_matching",
  479:                 "complete",
  480:                 {
  481:                     "templates_indexed": len(template_index),
  ...

**Found `extract_claims` in `src/cmr/claim_extraction.py`**
  327: 
  328: 
  329: def extract_claims_structured(claims: list[dict]) -> list[dict]:
  330:     """
  331:     Validate and normalize pre-structured claims.
  332: 
  333:     Required fields: independent_var / iv, dependent_var / dv.
  334:     Optional: direction, effect_size, sample_n, context.
  335:     """
  336:     normalized: list[dict] = []
  337:     seen_keys: dict[tuple[str, str, str], int] = {}
  338: 
  339:     for claim in claims:
  340:         if not isinstance(claim, dict):
  341:             continue
  342: 
  343:         iv = claim.get("independent_var") or claim.get("independent_variable") or claim.get("iv")
  344:         dv = claim.get("dependent_var") or claim.get("dependent_variable") or claim.get("dv")
  345:         if not iv or not dv:
  346:             continue
  347: 
  348:         raw_direction = claim.get("direction")
  349:         direction = _normalize_direction(raw_direction)
  350:         iv_text = str(iv).strip()
  351:         dv_text = str(dv).strip()
  352:         context = str(claim.get("context") or "")
  353:         relationship = str(claim.get("relationship") or claim.get("direction") or "reported_effect")
  354:         description = str(claim.get("description") or f"{iv_text} {relationship} {dv_text}")
  355:         effect_size = _safe_float(claim.get("effect_size"))
  356:         sample_n = _safe_int(claim.get("sample_n"))
  357:         warnings: list[str] = []
  358: 
  359:         if raw_direction is not None and str(raw_direction).strip() and direction == "unknown":
  360:             warnings.append("invalid_direction")
  361:         if effect_size is not None and abs(effect_size) > 3.0:
  362:             warnings.append("effect_size_outlier")
  363:         if sample_n is not None and sample_n < 10:
  364:             warnings.append("small_sample_n")
  365: 
  366:         dedupe_key = (_normalize(iv_text), _normalize(dv_text), direction)
  367:         existing_index = seen_keys.get(dedupe_key)
  368:         if existing_index is not None:
  ...

**Found `def extract_claims` in `src/cmr/claim_extraction.py`**
  327: 
  328: 
  329: def extract_claims_structured(claims: list[dict]) -> list[dict]:
  330:     """
  331:     Validate and normalize pre-structured claims.
  332: 
  333:     Required fields: independent_var / iv, dependent_var / dv.
  334:     Optional: direction, effect_size, sample_n, context.
  335:     """
  336:     normalized: list[dict] = []
  337:     seen_keys: dict[tuple[str, str, str], int] = {}
  338: 
  339:     for claim in claims:
  340:         if not isinstance(claim, dict):
  341:             continue
  342: 
  343:         iv = claim.get("independent_var") or claim.get("independent_variable") or claim.get("iv")
  344:         dv = claim.get("dependent_var") or claim.get("dependent_variable") or claim.get("dv")
  345:         if not iv or not dv:
  346:             continue
  347: 
  348:         raw_direction = claim.get("direction")
  349:         direction = _normalize_direction(raw_direction)
  350:         iv_text = str(iv).strip()
  351:         dv_text = str(dv).strip()
  352:         context = str(claim.get("context") or "")
  353:         relationship = str(claim.get("relationship") or claim.get("direction") or "reported_effect")
  354:         description = str(claim.get("description") or f"{iv_text} {relationship} {dv_text}")
  355:         effect_size = _safe_float(claim.get("effect_size"))
  356:         sample_n = _safe_int(claim.get("sample_n"))
  357:         warnings: list[str] = []
  358: 
  359:         if raw_direction is not None and str(raw_direction).strip() and direction == "unknown":
  360:             warnings.append("invalid_direction")
  361:         if effect_size is not None and abs(effect_size) > 3.0:
  362:             warnings.append("effect_size_outlier")
  363:         if sample_n is not None and sample_n < 10:
  364:             warnings.append("small_sample_n")
  365: 
  366:         dedupe_key = (_normalize(iv_text), _normalize(dv_text), direction)
  367:         existing_index = seen_keys.get(dedupe_key)
  368:         if existing_index is not None:
  ...

### Building eval feature structure

  126: def evaluate_building(
  127:     building_context: dict,
  128:     measured_features: dict,
  129:     occupant_profile: dict,
  130:     *,
  131:     db_path: str = "ae.db",
  132:     session: Session | None = None,
  133:     template_records: Iterable[TemplateRecord] | None = None,
  134:     web_service: WebPersistenceService | None = None,
  135: ) -> dict:
  136:     """Run Steps 1-9 of the building evaluation pipeline."""
  137: 
  138:     session = session or get_session(db_path)
  139:     models.Base.metadata.create_all(session.get_bind())
  140:     template_wis_overrides = building_context.get("template_wis_overrides", {})
  141:     declared_data_gaps = building_context.get("data_gaps", [])
  142: 
  143:     evaluation = CMREvaluation(
  144:         evaluation_type="building",
  145:         target_description=building_context.get(
  146:             "target_description",
  147:             building_context.get("building_name", "Unnamed Building"),
  148:         ),
  149:         status="in_progress",
  150:         building_context={**building_context, "occupant_profile": occupant_profile},
  151:     )
  152:     session.add(evaluation)
  153:     session.flush()
  154: 
  155:     templates = _select_templates(session, template_records=template_records)
