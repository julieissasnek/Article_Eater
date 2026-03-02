# Expert Decisions Log — Updated 2026-03-02

*Created: 2026-03-02*
*Status: ACTIVELY MAINTAINED*
*Last updated: 2026-03-02 08:30 UTC*

---

## Decision 1: Root-Domain Belief Decomposition
**Panel**: #5 (Env Psychologist), #7 (Lighting), #11 (ML Expert)
**Question**: When T3 merges findings to "luminous" instead of "luminous.color_temp", should we split or keep the aggregated belief?
**Recommendation**: Split. Root-domain beliefs lose specificity. The classifier should attempt sub-classification before falling back to root.
**Status**: ✅ IMPLEMENTED — Added 60+ semantic map entries in S1-2. Established beliefs rose 519→596.

## Decision 2: Cross-Modal Generalization
**Panel**: #5, #6 (Neuroscientist), #9 (Affect)
**Question**: Can VR forest + real forest + forest image generalize?
**Recommendation**: DEFER — requires empirical comparison of effect sizes across modalities. For now, treat as separate contexts in T3.
**Status**: ✅ FRAMEWORK BUILT — `cross_modal_analysis()` method added to `GeneralizationEngine`. Detects direction consistency across modalities but does not auto-merge yet. Rules to be finalized with more data.

## Decision 3: Contested Belief Adjudication (Wood→Attention)
**Panel**: #2 (Epistemologist), #5, #18 (Research Methodologist)
**Question**: Wood→Attention has 30 studies split 15/15. Moderator, artifact, or genuine inconsistency?
**Recommendation**: Likely moderator effect (wood type, attention measure, exposure duration). Needs formal moderator analysis.
**Status**: ✅ FRAMEWORK BUILT — `analyze_moderators()` with I² heterogeneity calculation added. Shows fragmentation rather than true contestation for "Wood" beliefs. Needs more data to identify specific moderators.

## Decision 4: Cortisol Access Level
**Panel**: #6, #15 (Physiologist)
**Question**: Cortisol is classified AUTONOMIC but is neuroendocrine (HPA axis → crosses levels).
**Recommendation**: Keep as AUTONOMIC for now. Add note. Consider adding NEUROENDOCRINE level in future.
**Status**: ✅ NOTED — low priority. Physiologist (#15) recommends adding NEUROENDOCRINE level in Wave 4+.

## Decision 5: Publication Bias in T3
**Panel**: #18
**Question**: Should T3 weight by sample size? Implement trim-and-fill?
**Recommendation**: Phase 1: Weight by sqrt(N). Phase 2: Add funnel plot asymmetry detection.
**Status**: ✅ PHASE 1 IMPLEMENTED — sqrt(N) weighting in `_form_specific_belief()`, sample-size confidence bonus in `_compute_confidence()`. Phase 2 deferred.

## Decision 6: Multisensory Node
**Panel**: #5, #6
**Question**: Add "multisensory" taxonomy node or tag each modality separately?
**Recommendation**: Tag separately. Multisensory interactions emerge from T3 belief combinations, not single nodes.
**Status**: ✅ DECIDED — no node needed.

## Decision 7: Field Reviewer Normalization
**Panel**: #4 (Data), #18
**Question**: Is normalizing `<0.001` → 0.001 losing inequality information?
**Recommendation**: Store both `p_value_original` (string) and `p_value` (float). Field reviewer should add original preservation.
**Status**: ✅ IMPLEMENTED — `p_value_original` preserved in `field_reviewer.py`.

## Decision 8: Embedding Fallback (#11)
**Panel**: #11 (ML Expert)
**Question**: How to handle the 28% unclassified IVs?
**Recommendation**: Add sentence embedding–based fallback classification.
**Status**: ✅ IMPLEMENTED — TF-IDF cosine similarity fallback (Stage 4) added to `iv_dv_classifier.py`. **Classification rate: 71.9% → 89.8% (+17.9pp)**. 1,170 IVs recovered from unclassified. 133 taxonomy nodes indexed.

## Decision 9: Event Bus (#16)
**Panel**: #16 (Expert System Designer)
**Question**: Should subsystems communicate via event bus instead of direct imports?
**Recommendation**: Architecture change — decouple with pub/sub pattern.
**Status**: 📋 WAVE 4+ — significant refactoring required.

## Decision 10: I² Heterogeneity (#18)
**Panel**: #18 (Research Methodologist)
**Question**: Should T3 compute heterogeneity statistics for each belief?
**Recommendation**: Yes — compute I² for beliefs with ≥3 studies.
**Status**: ✅ IMPLEMENTED — I² calculation added to `analyze_moderators()`.

## Decision 11: Defeasibility Tracking (#2)
**Panel**: #2 (Epistemologist)
**Question**: When a belief gets contested, should we track which evidence defeated it?
**Recommendation**: Yes — this is core to Haack's foundherentism framework.
**Status**: ✅ IMPLEMENTED — `defeaters` list, `status_history` list, and `record_defeat()` method added to `GeneralizationEngine`.

## Decision 12: DAG Visualization (#13)
**Panel**: #13 (Bayesian Network Expert)
**Question**: Generate force-directed graph from T3 established beliefs?
**Recommendation**: Yes — visual inspection helps validate belief network structure.
**Status**: 📋 WAVE 4 — requires visualization library integration.

## Decision 13: NLP Preprocessing (#12)
**Panel**: #12 (NLP Specialist)
**Question**: Should the classifier lemmatize and expand abbreviations before matching?
**Recommendation**: Yes — lemmatize, expand abbreviations, handle multi-word entities.
**Status**: ✅ IMPLEMENTED — `nlp_preprocessing.py` created with 90+ domain-specific abbreviations (CCT, IAQ, SBS, etc.), lemmatization, and text normalization. Wired into classifier Stage 0.

## Decision 14: Effect Size Standardization (#18)
**Panel**: #18 (Research Methodologist)
**Question**: Different papers report r, d, η², OR — should we standardize before aggregation?
**Recommendation**: Yes — convert all to Cohen's d as canonical metric.
**Status**: ✅ IMPLEMENTED — `effect_size_converter.py` created with 7 conversion methods (r→d, η²→d, OR→d, f²→d, g→d, R²→d). Magnitude interpretation included.
