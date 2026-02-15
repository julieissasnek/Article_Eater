# Characterization of Staging Theory-Links (1,361 rows)

Date: 2026-02-15
Source file: `data/review/tranche80_confirmed_rows.csv`
Filter used: `claim_type == "theory_link"`

## 1) Theory counts and edge-label counts

Total theory-link rows: **1361**

### Theory distribution

- `ART`: 1251
- `biophilia`: 102
- `SRT`: 3
- `embodied_cognition`: 4
- `predictive_processing`: 1

Note: prior high-level summary (ART 1251 / biophilia 102 / SRT 3) captures the major buckets but omits 5 additional rows (`embodied_cognition` + `predictive_processing`).

### Distinct `edge_type` labels (all theory-link rows)

- `COHERENCE_SUPPORT`: 1282
- `THEORETICALLY_PREDICTS`: 53
- `CONFIRMS_PREDICTION`: 17
- `PROPOSES_MECHANISM`: 4
- `DISCONFIRMS_PREDICTION`: 2
- `THEORY_TENSION`: 2
- `SUBSUMES_THEORY`: 1

### `edge_type` by theory

- `ART`: `COHERENCE_SUPPORT` 1176, `THEORETICALLY_PREDICTS` 51, `CONFIRMS_PREDICTION` 17, `PROPOSES_MECHANISM` 4, `THEORY_TENSION` 2, `SUBSUMES_THEORY` 1
- `biophilia`: `COHERENCE_SUPPORT` 98, `DISCONFIRMS_PREDICTION` 2, `THEORETICALLY_PREDICTS` 2
- `SRT`: `COHERENCE_SUPPORT` 3
- `embodied_cognition`: `COHERENCE_SUPPORT` 4
- `predictive_processing`: `COHERENCE_SUPPORT` 1

### Supporting relation labels in the same rows

- `argument_relation_type`: `cites` 1288, `tests` 53, `supports` 17, `contradicts` 2, `extends` 1
- `relation_type_hint`: `explains` 1342, `supports` 17, `contradicts` 2
- `argument_scheme`: `argument_from_expert_opinion` 1343, `causal_argument` 18

## 2) Schema/field characterization

Header width: **59 columns**.

### Columns populated for all theory-link rows (36/59)

`paper_id`, `claim_id`, `claim_type`, `node_id`, `statement`, `ae_confidence`, `node_type`, `article_type_family`, `template_version`, `edge_id`, `edge_type`, `source_node_id`, `target_node_id`, `weight`, `evidence_basis`, `needs_verification`, `justification`, `relation_type_hint`, `relation_strength_hint`, `argument_relation_type`, `causal_level`, `argument_scheme`, `theory_name`, `source_section`, `source_page_start`, `source_page_end`, `source_quote`, `source_quote_hash`, `quality_flag`, `source`, `evidence_level`, `provenance_tier`, `requires_pdf_confirmation`, `source_zone`, `extraction_difficulty`, `processed_at`.

### Columns empty across all theory-link rows (23/59)

`environment_variable`, `outcome_variable`, `environment_candidates`, `outcome_candidates`, `environment_canonical_id`, `outcome_canonical_id`, `environment_resolution_confidence`, `outcome_resolution_confidence`, `environment_resolution_match_type`, `outcome_resolution_match_type`, `environment_node_id`, `outcome_node_id`, `effect_direction`, `relation_provenance_hint`, `target_paper_id`, `citation_text`, `citation_doi`, `citation_context`, `citation_match_confidence`, `citation_match_type`, `source_table_id`, `source_table_row`, `article_type_needs_review`.

### Process/provenance profile

- `source`: `pdf_discourse_scan` for all 1361 rows.
- `provenance_tier`: `pdf_confirmed` for all 1361 rows.
- `evidence_level`: `pdf_discourse_extracted` for all 1361 rows.
- `article_type_family`: `unknown` for all 1361 rows.
- `quality_flag`: `needs_article_type_verification` 692, `ok` 669.
- `source_zone`: `introduction` 497, `methods` 425, `conclusion` 177, `discussion` 171, `related_work` 52, `results` 39.

## 3) Mapping to integrated papers (1,170-paper corpus)

Integrated paper universe (from `data/web_persistence.db`, `paper_integrations`): **1170 distinct `paper_id`**.

Within theory-link staging rows:

- Distinct linked papers: **36**
- Linked papers that are in integrated set: **27/36**
- Theory-link rows referencing integrated papers: **975/1361**

### Top 10 most-linked paper IDs

1. `doi:10.3390/buildings14103293` — 120 (integrated: yes)
2. `doi:10.1037/aca0000150` — 108 (integrated: no)
3. `doi:10.3390/f13122073` — 104 (integrated: yes)
4. `doi:10.1145/2556288.2557008` — 87 (integrated: no)
5. `doi:10.1111/sjop.12171` — 76 (integrated: yes)
6. `doi:10.3390/buildings13082000` — 72 (integrated: yes)
7. `doi:10.1038/s41598-022-27141-7` — 72 (integrated: yes)
8. `doi:10.1080/23744731.2022.2049639` — 70 (integrated: yes)
9. `zotero:6TNNU66U` — 64 (integrated: yes)
10. `doi:10.37547/tajiir/volume06issue08-06` — 62 (integrated: no)

## 4) Template-ID references vs theory-name-only rows

Question: do rows reference specific template IDs (`T1`, `T2`, etc.)?

Result:

- Rows with explicit template-like references detected: **4/1361**
- All detected hits were `T1` mentions (same paper: `doi:10.3390/f13122073`)
- The large majority of rows are theory-name driven (`theory_name` field) and do not carry explicit template IDs.

## 5) Interpretation for Tier-2 reduction work

- The staging set is strongly skewed toward ART and `COHERENCE_SUPPORT` relations.
- The data is rich in discourse provenance fields but sparse in structured env/outcome/citation linkage for these rows.
- There is nontrivial alignment gap to integrated corpus IDs (386 rows currently reference paper IDs outside integrated set).
- If Tier-2 reduction panels need template-grounded reconciliation, template-ID capture must be strengthened (currently 4/1361 rows).
