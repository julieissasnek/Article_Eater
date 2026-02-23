# Rule Type Coverage Audit

- Claims file: `data/production/structured_claims_codex_semantic.json`
- Triage file: `data/production/paper_triage.json`
- Total claims: `72`
- Missing explicit claim_type: `72`

## Existing Claim Types
- `missing`: 72

## Inferred Candidate Rule Types
- `associational`: 53
- `population_scope`: 11
- `narrative_observation`: 7
- `moderated`: 1

## Candidate Missing Rule Types
- `narrative_observation`
- `population_scope`

## Coverage by Article Family
| article_type_family | claims | missing_claim_type | top_inferred_rule_type |
|---|---:|---:|---|
| unknown | 57 | 57 | associational |
| narrative_review | 8 | 8 | associational |
| phenomenological | 7 | 7 | associational |

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
- `narrative_observation` | `doi:10.1016/0272-4944(95)90013-6` | col_1: 88) =; col_2: 10.33, p c 0.01 and gender F(1, 88) = 14.57,
- `narrative_observation` | `doi:10.47611/jsrhs.v13i1.6257` | The present analysis employed Python libraries and tools to conduct an analysis of publicly available data: sourced from a study on affect and cognition in natural and commercia...
- `narrative_observation` | `doi:10.3390/ijerph182312510` | col_1: Anger; col_2: 1 (0) 1 (0) Z=1.469,p=0.142,r=0.229 angular>curved BF01=1.635
- `narrative_observation` | `doi:10.3390/ijerph182312510` | col_1: Sadness; col_2: 1 (1) 1 (0.5) Z=0.118,p=0.906,r=0.018 modern(cid:54)=classic BF01=5.08
- `narrative_observation` | `doi:10.1068/p5292` | dmark Main Effect; F(1,4)=12.28; p< 0.02: Landmark/Size in F(1,4)=12.17; p<; 48: teraction 0.0252
- `narrative_observation` | `doi:10.1068/p5292` | Landmark Main Effect; F: F(1,10)=5.20; p< 0.0458
- `narrative_observation` | `doi:10.1002/wcs.147` | Dimension: Roughness; Definition: Perceptual impression created by amplitude and frequency modulations in sound at high modulation rates, above about 20 Hz. Roughness notably de...

