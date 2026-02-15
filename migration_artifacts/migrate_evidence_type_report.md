# EvidenceType Migration Report

Canonical section: `enums.EvidenceType`

## Discovered values by source
- `article_finder_detected`: []
- `bn_enhanced_edge`: ['empirical', 'meta_analysis', 'replication_failure', 'replication_success', 'theoretical']
- `bn_literature_linker`: ['direct', 'indirect', 'meta', 'review', 'theoretical']
- `bn_mechanism_spec`: ['computational_model', 'correlational', 'experimental', 'neuroscientific', 'theoretical']
- `bn_sql_evidence_type`: ['empirical', 'meta_analysis', 'replication_failure', 'replication_success', 'theoretical']
- `bn_sql_mechanism_evidence_type`: ['computational_model', 'correlational', 'experimental', 'neuroscientific', 'theoretical']
- `tagging_csv`: ['computed', 'image_2d', 'image_3d', 'metadata', 'sensor']

## Value -> canonical mapping
- `computational_model` -> `computational_model`
- `correlational` -> `correlational`
- `direct` -> `observational`
- `empirical` -> `observational`
- `experimental` -> `experimental`
- `indirect` -> `observational`
- `meta` -> `meta_analysis`
- `meta_analysis` -> `meta_analysis`
- `neuroscientific` -> `neuroscientific`
- `replication_failure` -> `replication_failure`
- `replication_success` -> `replication_success`
- `review` -> `theoretical`
- `theoretical` -> `theoretical`

## Unmapped values by source
- `tagging_csv`: ['computed', 'image_2d', 'image_3d', 'metadata', 'sensor']

