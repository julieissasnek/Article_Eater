# Meta-Review Implementation Guide

**Quick Reference for LLM Generation Pipeline**
**Date**: 2026-03-04

## Before Running LLM Meta-Review Generation

1. **Read the full spec**: `/contracts/META_REVIEW_SPEC.md` (814 lines, ~6,500 words)
   - Pay special attention to Sections 3 (Quality Criteria) and 8 (Forbidden Patterns)

2. **Check model allocation** (Section 7.1):
   - High-stakes clusters: use Claude Opus 4.6
   - Low-stakes clusters: use Gemini 2.0 Flash
   - Decision matrix based on n_papers + usage frequency

3. **Review the prompt template** (Section 7.2):
   - Use the provided prompt structure exactly
   - Include all 5 critical constraints (hallucination prevention, confidence calibration, quantification requirement, specificity, scope conditions)
   - Include the quality gate checklist before returning JSON

## Key Quality Criteria (Must Pass ALL)

### SC-MR-1: Non-Trivial Belief Statement
- Must include: effect size OR CI OR sample size OR evidence count
- No vague claims like "Light affects mood"
- Minimum 150 characters, maximum 500 characters

### SC-MR-2: Evidence-Grounded Mechanisms
- Every mechanism must have evidence_count >= 1 OR confidence = "speculative"
- Each mechanism needs a multi-step causal pathway (not single-hop)
- Must cite theory with author(s) and year

### SC-MR-3: Justified Confidence Level
- HIGH: >= 10 studies, >= 90% direction agreement, medium+ effect, low heterogeneity
- MOD_HIGH: 5-9 studies, 75-89% agreement, small-medium effect
- MODERATE: 3-4 studies OR direction agreement 60-74% OR small effect OR single team
- LOW: <= 2 studies OR highly heterogeneous OR unmeasured confounds

### SC-MR-4: Testable Research Needs
- Each research need must answer a specific, measurable question
- Must cite which current gap it addresses (from heterogeneity, scope, confounds)
- VOI rank (1-5) must be justified

### SC-MR-5: Quantified Heterogeneity
- If heterogeneity = "high", must include I² OR effect size range OR subset analyses
- Cannot say "findings vary" without numbers
- Must point to specific moderators (population, method, setting)

### SC-MR-6: Explicit Scope Conditions
- MUST include: population (age range), setting type, minimum one of (duration, intensity, dosage)
- MUST list explicit exclusions (who/where effect does NOT apply)
- Cannot say "applies broadly" or "varies"

### SC-MR-7: Effect Size with Uncertainty
- Report pooled estimate WITH 95% CI (e.g., "d = 0.38, CI [0.21, 0.55]")
- OR report range + median if heterogeneous (e.g., "d range 0.19-0.62, Mdn = 0.42")
- OR explicit "not available: reason"
- Never bare point estimates

### SC-MR-8: Cited Theory Links
- Format: "Theory Name (Author, Year)"
- Example: "Attention Restoration Theory (Kaplan & Kaplan, 1989)"
- Cannot cite "neural mechanisms" or "cognitive processes"

## Forbidden Patterns (Will REJECT)

1. ❌ **Unqualified hedging**: "Perhaps X might affect Y in some cases"
   - ✅ Correct: "X→Y is LOW confidence (ω=0.41) because only 2 studies, single team"

2. ❌ **Treating all studies equal**: "7 studies show effect, 1 shows null, evidence mixed"
   - ✅ Correct: "7 studies (median N=58) show effect; 1 post-hoc sub-analysis (N=12) null. High-N studies consistent"

3. ❌ **Defaulting to MODERATE**: "Confidence is moderate due to limitations"
   - ✅ Correct: "MOD_HIGH confidence (ω=0.73) because: 7 studies, 86% agreement, low heterogeneity"

4. ❌ **Vague mechanisms**: "Works through neural mechanisms" or "attention and emotion"
   - ✅ Correct: "Pathway: Light → melatonin suppression → cortisol reduction. Supported by circadian physiology (Czeisler & Gooley, 2007)"

5. ❌ **Ignoring contradictions**: "All studies agree, confirming robustness"
   - ✅ Correct: "7/8 studies show effect. 1 study (Smith et al., 2019, N=40) tested in 35°C heat with ventilation uncontrolled, confounding temperature with light"

6. ❌ **Generic research needs**: "More research needed" or "Future studies should investigate"
   - ✅ Correct: "Rank 1: Does effect persist in outdoor settings (temperature uncontrolled)? All 7 current studies are indoor"

7. ❌ **Circular scope**: "Applies to people in various settings"
   - ✅ Correct: "Applies to: adults 20-65 in office, climate-controlled 18-24°C. Does NOT apply to outdoor settings (temperature confound), shift workers (circadian abnormality)"

## Validation Checklist (Before Persistence)

- [ ] belief_statement > 150 characters AND < 500 characters
- [ ] belief_statement contains at least one of: effect size, CI, sample size, evidence count
- [ ] confidence_level assignment follows calibration table (Section 2.1.3)
- [ ] Every mechanism has evidence_count >= 1 OR confidence = "speculative"
- [ ] Every mechanism is multi-step causal pathway with theory citation
- [ ] Every research_need is testable as standalone study
- [ ] If heterogeneity = "high", heterogeneity_assessment includes numbers (I², ranges, subsets)
- [ ] scope_conditions specifies: population, setting, + one of (duration, intensity, dosage)
- [ ] effect_size_summary includes CI OR explicit "not available: reason"
- [ ] Every theory_link includes "Author, Year"
- [ ] No unsourced causal claims in mechanisms or latent_variables
- [ ] confidence_level, effect_size_summary, n_papers are internally consistent

## System Health Monitoring

Check these metrics regularly:

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Cluster completeness | >= 95% | < 95% |
| Quality gate pass rate | >= 92% | < 92% |
| High-confidence well-evidenced clusters | >= 85% | < 85% |
| Heterogeneity visibility (high HET clusters) | >= 88% | < 88% |

If any metric is below threshold:
1. Sample 20 failing meta-reviews
2. Check which quality criterion is failing most often
3. Adjust LLM prompt or trigger manual review

## Files to Keep in Sync

- `contracts/META_REVIEW_SPEC.md` — authority document (don't edit lightly)
- `contracts/success_conditions.json` — system health metrics (update if spec changes)
- `src/qa/cluster_meta_review.py` — data model (must implement all spec fields)
- This guide — keep updated with spec changes

## Questions Before You Start?

1. Is the cluster already assigned a meta-review (not all clusters need regeneration)?
2. How many clusters are "high-stakes" vs "low-stakes" by your allocation criteria?
3. Do you have fallback procedures if LLM generation fails >8% of clusters?
4. Who will do spot-check QA on first 50 generated meta-reviews before full batch?

---

**Last Updated**: 2026-03-04  
**Authority**: META_REVIEW_SPEC.md Section 7
