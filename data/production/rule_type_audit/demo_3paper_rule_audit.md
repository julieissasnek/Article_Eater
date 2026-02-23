# Rule Type Coverage Audit

- Claims file: `data/production/rule_type_audit/demo_3paper_semantic_claims.json`
- Triage file: `data/production/paper_triage.json`
- Total claims: `27`
- Missing explicit claim_type: `27`

## Existing Claim Types
- `missing`: 27

## Inferred Candidate Rule Types
- `associational`: 15
- `population_scope`: 11
- `moderated`: 1

## Candidate Missing Rule Types
- `population_scope`

## Coverage by Article Family
| article_type_family | claims | missing_claim_type | top_inferred_rule_type |
|---|---:|---:|---|
| unknown | 17 | 17 | population_scope |
| phenomenological | 7 | 7 | associational |
| narrative_review | 3 | 3 | associational |

## Example Missing-Rule Candidates
- `population_scope` | `doi:10.24382/5191` | Initial code: Influence of Environmental and External Factors; n of participants contributing: 6; n of transcript excerpts assigned: 9; Sample quote: This is necessary in case o...
- `population_scope` | `doi:10.24382/5191` | Initial code: Physical and Health Impacts; n of participants contributing: 11; n of transcript excerpts assigned: 17; Sample quote: Reduce any potential health effects like eyes...
- `population_scope` | `doi:10.24382/5191` | Initial code: Task Performance and Efficiency; n of participants contributing: 11; n of transcript excerpts assigned: 20; Sample quote: You cannot concentrate to do what you mus...
- `population_scope` | `doi:10.24382/5191` | Initial code: Architectural Impact on Light: Building Design's Impact on Illumination; n of participants contributing: 12; n of transcript excerpts assigned: 14; Sample quote: B...
- `population_scope` | `doi:10.24382/5191` | Initial code: Increasing Window Presence for Improved Light Inflow; n of participants contributing: 12; n of transcript excerpts assigned: 12; Sample quote: Restructuring of the...
- `population_scope` | `doi:10.24382/5191` | Initial code: Positive Impacts on Human Factors; n of participants contributing: 2; n of transcript excerpts assigned: 2; Sample quote: Make the work, help patient's health very...
- `population_scope` | `doi:10.24382/5191` | Subtheme: Influence of external and environmental factors; n of participants contributing: 7; n of transcript excerpts assigned: 7; Sample quote: There is adjacent one blocking ...
- `population_scope` | `doi:10.24382/5191` | Subtheme: Physical and health impacts; n of participants contributing: 9; n of transcript excerpts assigned: 14; Sample quote: Sometimes I must squint my eyes short for some tim...
- `population_scope` | `doi:10.24382/5191` | Subtheme: Psychological and emotional responses; n of participants contributing: 5; n of transcript excerpts assigned: 5; Sample quote: Sometimes affect my mood, to be honest, i...
- `population_scope` | `doi:10.24382/5191` | Subtheme: Task performance and efficiency; n of participants contributing: 11; n of transcript excerpts assigned: 14; Sample quote: Yes, the room is not adequately illuminated a...
- `population_scope` | `doi:10.24382/5191` | Subtheme: Architectural impact on light: Building design’s impact on illumination; n of participants contributing: 8; n of transcript excerpts assigned: 12; Sample quote: And be...

