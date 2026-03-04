# T3 Extraction Bias Audit Plan

**Panel Recommendation #2: Validate T3 Corpus Against AI Extraction Bias**

**Document Date**: 2026-03-03
**Panel Rating**: CRITICAL
**Status**: Specification and Planning Phase
**Owners**: David Kirsh (oversight), Claude Code (implementation)

---

## Executive Summary

The T3 corpus (33,000 findings extracted from 1,043 scientific articles using Gemini) may contain systematic biases introduced by the extraction LLM itself. The panel (Dehaene, Tenenbaum, Kording) flagged five specific threat types that could inflate reported effect sizes, distort theoretical relationships, and compromise the integrity of downstream causal inference.

This document specifies a concrete, actionable audit plan with:
- **Gold standard construction** (50-article human expert panel)
- **Five quantified bias detection metrics**
- **Automated detection tools** for the full corpus
- **Remediation strategy** for biased extractions
- **Resource estimates** (52 person-hours)
- **Success criteria** (kappa ≥0.70, ≤10% false positive rate)

The audit is designed to run in parallel with extraction quality improvements (EXTRACTION_QUALITY_FRAMEWORK) and feeds results into the OVERSEER health monitoring system.

---

## 1. Audit Design

### 1.1 Gold Standard Sample Selection

**Sample size**: 50 articles (stratified random)

**Stratification**: By article family (10 per family)
1. **Empirical original research** (N=10): Experiments, behavioral studies, neuroscience papers with primary data
2. **Synthesis/review articles** (N=10): Meta-analyses, literature reviews, systematic reviews
3. **Theoretical papers** (N=10): Conceptual frameworks, model proposals (may have lower T3 extraction yield)
4. **Qualitative/ethnographic** (N=10): Interview studies, case studies, ethnographic work
5. **Mixed methods** (N=10): Papers combining quantitative and qualitative approaches

**Rationale**: Extraction artifacts may differ by article type. Empirical papers may show "significant result bias" while reviews may show "simplification bias" (flattening complex meta-analytic findings into single claims).

**Selection process**:
- Stratify the full 1,043-article corpus by article family (using abstract text classification or manual categorization from extraction metadata)
- Randomly select 10 articles from each family
- Record stratification metadata (family, article ID, title, DOI, extraction date/version) in `data/gold_standard/sampling_log.csv`

**Storage**: Store selected article IDs and metadata at:
```
data/gold_standard/
  ├── sampling_log.csv                    # Stratification & selection record
  ├── articles/
  │   ├── PMID_or_DOI_1/original.pdf
  │   ├── PMID_or_DOI_1/original.txt
  │   └── ... (50 articles)
```

### 1.2 Human Expert Extraction (Two Independent Raters per Article)

**Coding procedure**:
1. Each of 50 articles is independently extracted by 2 human expert raters
2. Raters are domain experts (cognitive neuroscience, psychology, human-computer interaction) familiar with extraction taxonomy
3. For each article, raters extract all T3 beliefs using the same schema as the AI extractor:
   - `antecedent` (variable, population, condition)
   - `consequent` (outcome variable)
   - `direction` (increase | decrease | no_effect | mixed)
   - `effect_size` (numeric or null)
   - `claim_type` (causal | correlational | descriptive | predictive)
   - Additional metadata (confidence, certainty qualifiers, study type)

**Rater training**:
- Both raters receive a 2-hour training session reviewing:
  - EXTRACTION_FIELD_QUALITY_FRAMEWORK extraction schema
  - 5 exemplar articles (not in the 50-article sample)
  - Inter-rater calibration discussion
  - Extraction ambiguity resolution guidelines

**Data storage**:
```
data/gold_standard/
  ├── rater_assignments.csv               # Who coded which article
  ├── extractions/
  │   ├── PMID_1_rater_A.jsonl           # Human rater A extractions
  │   ├── PMID_1_rater_B.jsonl           # Human rater B extractions
  │   ├── PMID_1_gemini.jsonl            # Gemini (T3) extractions for comparison
  │   └── ... (150 rater files + 50 Gemini files)
```

**Timeline**: 50 articles × 2 raters × 0.4 hours/article ≈ **40 person-hours** (2–3 weeks at 20 hours/week)

### 1.3 Inter-Rater Reliability Assessment

**Measure**: Cohen's kappa (κ)

**Computation**:
- For each article, compute kappa between rater A and rater B across:
  - **Per-finding agreement**: Do both raters identify the same antecedent-consequent pair?
  - **Direction agreement**: Given same pair, do they assign the same direction?
  - **Effect size agreement**: Do both assign numeric ES or both null?
  - **Claim type agreement**: causal vs. correlational vs. descriptive?

**Acceptance criterion**: κ ≥ 0.70 per article
- If κ < 0.70 for any article, that article is flagged for reconciliation discussion
- Raters discuss disagreements, reach consensus (producing gold standard extraction)
- If consensus cannot be reached, article is excluded from gold standard (with notation)

**Expected outcome**: ~48–50 articles with kappa ≥ 0.70; 0–2 excluded

### 1.4 Gold Standard Finalization

For each of the 50 articles:
1. If κ ≥ 0.70: Use majority vote or rater-A priority rule (predetermined) as gold standard extraction
2. If κ < 0.70: Raters discuss to consensus; reconciled extraction becomes gold standard
3. If consensus impossible: Document disagreement, exclude article from aggregate metrics (but may be included in specific bias type analysis)

**Gold standard file format** (JSONL with schema):
```
data/gold_standard/
  ├── gold_standard_extractions.jsonl     # 50 articles, final consensus extractions
  ├── gold_standard_metadata.csv          # article_id, rater_kappa, n_findings, extraction_date
```

---

## 2. Bias Detection Metrics

### 2.1 Bias Type 1: Simplification Bias (Simple Cause-Effect Over-Representation)

**Threat**: LLMs may preferentially extract "X increases Y" findings (simple bivariate causality) over findings involving moderators, mediators, null results, or boundary conditions. This inflates the apparent effect size landscape by discarding conditional evidence.

**Metric**: Simplicity ratio
$$\text{simplicity\_ratio} = \frac{n_{\text{simple bivariate}}}{n_{\text{total findings}}}$$

Where:
- Simple bivariate: antecedent = single variable; consequent = single outcome; no explicit moderators or mediators mentioned
- Complex: antecedent includes conditional phrases (e.g., "X under high stress"), mediators, or consequent is conditional/qualified

**Hypothesis**:
- **Gold standard**: If articles report moderators/interactions, ~30–40% of findings should be complex
- **T3 (Gemini) corpus**: If extraction-biased, simplicity ratio should be significantly higher (e.g., >60%)

**Measurement**:
1. Code each extracted finding as `simple | complex`
2. Compute simplicity ratio for gold standard (expect: 0.55–0.65)
3. Compute simplicity ratio for T3 Gemini extractions on same 50 articles
4. Compare: T-test on proportions
5. Effect size: Cohen's h (difference in proportions)

**Acceptable threshold**: |T3 simplicity ratio – gold standard| < 0.10 (no more than 10 percentage point difference)

**Storage**:
```
data/gold_standard/
  ├── bias_metrics/
  │   ├── simplification_bias.csv
  │       # article_id, gold_standard_simplicity, gemini_simplicity,
  │       # difference, flagged (bool)
```

---

### 2.2 Bias Type 2: Theoretical Vocabulary Bias

**Threat**: If ATLAS extraction prompts mention theory names (e.g., "Predictive Processing," "Adaptive Resonance Theory"), the LLM may over-tag findings with those theory labels, creating spurious correlation between theory mention frequency and finding frequency that doesn't reflect the papers.

**Metric**: Theory mention-to-tag correlation

For each of 5 major theories (PP, ART, Global Workspace, Somatic Marker, Bayesian Brain):
$$r_{\text{theory}} = \text{Pearson correlation between} \begin{cases}
\text{frequency of theory name in extraction prompts} \\
\text{frequency of theory tag in extracted findings}
\end{cases}$$

**Hypothesis**:
- **Gold standard**: Raters code theories from paper content only; any correlation should be ~0.0
- **T3 (Gemini) corpus**: If prompt-biased, correlation with prompt mention should be r > 0.40 (moderate)

**Measurement**:
1. For 50 gold standard articles, count:
   - Human raters' theory tag frequency (should reflect paper content only)
   - Gemini's theory tag frequency on same articles
2. For extraction prompts used for these 50 articles, count theory name mentions
3. Compute Pearson r: (prompt theory mention count) ↔ (Gemini theory tag count)
4. Compare: Rho should be ~0.0 for gold standard, elevated for Gemini if biased

**Acceptable threshold**: r < 0.25 (weak correlation, no strong prompt-induced bias)

**Storage**:
```
data/gold_standard/
  ├── bias_metrics/
  │   ├── theory_vocabulary_bias.csv
  │       # theory, prompt_mention_count, human_tag_count, gemini_tag_count,
  │       # correlation_coef, p_value, flagged (bool)
```

---

### 2.3 Bias Type 3: Positive Result Bias

**Threat**: LLMs may preferentially extract significant/positive results over null findings, non-replications, or failed experiments. This inflates apparent effect sizes and discovery rates.

**Metric**: Positive result ratio

$$\text{positive\_ratio} = \frac{n_{\text{positive/significant}}}{n_{\text{all direction assignments}}}$$

Where:
- Positive/significant: direction = "increase" OR explicitly stated as p < 0.05
- Null/negative: direction = "no_effect" OR "decrease" OR p > 0.05

**Benchmark**: Field base rates
- Publication bias in psychology/neuroscience typically inflates positive results to ~85–90% (Fanelli, 2012; Ioannidis, 2005)
- Gold standard extractions, reflecting papers as published, should show ~80–85% positive
- **BUT**: Reported nulls in papers (when mentioned) should also be captured
- If T3 extraction misses reported null results, positive ratio will be higher than human extraction

**Measurement**:
1. For each article, count:
   - Human-extracted findings with direction = "increase" or "decrease" or "no_effect"
   - Gemini-extracted findings with same directions
2. Compute positive ratios:
   - Gold standard: (increase + explicit_positive) / total
   - T3 Gemini: (increase + explicit_positive) / total
3. Compare: Look for systematic gap (Gemini > Gold by >5 percentage points)

**Acceptable threshold**: |T3 positive ratio – gold standard| < 0.05 (no more than 5 percentage point difference)

**Storage**:
```
data/gold_standard/
  ├── bias_metrics/
  │   ├── positive_result_bias.csv
  │       # article_id, human_positive_ratio, gemini_positive_ratio,
  │       # human_total_findings, gemini_total_findings,
  │       # difference, flagged (bool)
```

---

### 2.4 Bias Type 4: Antecedent Specificity Gradient

**Threat**: The LLM may produce more specific, detailed antecedents for well-studied domains (e.g., "bright light exposure in afternoon" for lighting) but vaguer antecedents for less-studied domains (e.g., "social context" for social effects). This creates confounding: apparent "effect specificity" correlates with domain familiarity rather than paper content.

**Metric**: Specificity score distribution by domain

For each domain (lighting, noise, temperature, olfaction, social density, etc.):
$$\text{specificity\_score} = f(\text{antecedent word count, entity detail, quantifier precision})$$

**Specificity scoring rubric**:
- **Vague** (score 1): generic terms, no quantities (e.g., "loud noise")
- **Moderate** (score 2): domain-specific but unquantified (e.g., "75 dB noise")
- **Specific** (score 3): quantified with context (e.g., "75 dB continuous white noise, 4-hour exposure")

**Measurement**:
1. Classify 50 articles by primary domain
2. Extract antecedents from gold standard and T3 Gemini
3. Code each antecedent on 1–3 specificity scale (blinded to source)
4. Compute mean specificity per domain for:
   - Gold standard extractions
   - T3 Gemini extractions
5. Compute correlation: domain frequency (well-studied vs. understudied) ↔ specificity
   - If correlates strongly, suggests gradient bias

**Acceptable threshold**: No correlation between domain study frequency and specificity (r < 0.20)

**Storage**:
```
data/gold_standard/
  ├── bias_metrics/
  │   ├── antecedent_specificity.csv
  │       # domain, human_mean_specificity, gemini_mean_specificity,
  │       # human_sd, gemini_sd, difference, flagged (bool)
  │   ├── specificity_item_level.csv
  │       # antecedent_text, source (human|gemini), domain, specificity_score
```

---

### 2.5 Bias Type 5: Direction Assignment Bias

**Threat**: The LLM may have a default toward positive framing, over-assigning "increase" relative to "decrease," "no_effect," or "mixed." This inflates apparent causal efficacy.

**Metric**: Direction distribution (observed vs. expected)

For all findings in the 50-article sample:
$$\chi^2 = \sum_{d \in \{\text{increase}, \text{decrease}, \text{no\_effect}, \text{mixed}\}} \frac{(O_d - E_d)^2}{E_d}$$

Where:
- O_d = observed frequency of direction d in T3 Gemini extractions
- E_d = expected frequency (from gold standard or domain baseline)

**Measurement**:
1. Count direction assignments in gold standard (50 articles):
   - n_increase, n_decrease, n_no_effect, n_mixed
   - Compute proportions: p_increase, p_decrease, etc.
2. Count direction assignments in T3 Gemini on same 50 articles
3. Chi-square test: observed (Gemini) vs. expected (gold standard proportions)
4. If χ² significant, examine which direction is over-represented

**Acceptable threshold**: χ² < 3.84 (no significant difference; df=3, α=0.05)

**Storage**:
```
data/gold_standard/
  ├── bias_metrics/
  │   ├── direction_distribution.csv
  │       # direction, human_count, human_proportion, gemini_count,
  │       # gemini_proportion, expected_count, chi_sq_component
  │   ├── direction_test_results.txt
  │       # Chi-square stat, p-value, df, significance
```

---

## 3. Gold Standard Construction (Implementation Checklist)

### Phase 0: Setup and Training (Week 1)

- [ ] Identify 2 domain expert raters (cognitive neuroscience, psychology, or adjacent fields)
- [ ] Rater training session (2 hours each):
  - [ ] Review EXTRACTION_FIELD_QUALITY_FRAMEWORK schema
  - [ ] Walk through 5 exemplar articles (not in 50-article sample)
  - [ ] Practice extracting on 2 training articles together, discuss disagreements
  - [ ] Review disagreement resolution guidelines
- [ ] Create rater assignment spreadsheet (which rater codes which article)
- [ ] Set up version control and file structure (data/gold_standard/)

### Phase 1: Human Extraction (Weeks 1–3)

- [ ] Rater A extracts findings from 50 articles (20 person-hours)
- [ ] Rater B extracts findings from 50 articles (20 person-hours)
- [ ] Store extractions in `data/gold_standard/extractions/` as JSONL

### Phase 2: Inter-Rater Reliability (Week 3)

- [ ] Compute Cohen's kappa for each article (per finding, per direction, per claim type)
- [ ] Flag articles with κ < 0.70
- [ ] Generate `inter_rater_report.csv`

### Phase 3: Reconciliation (Week 3–4)

- [ ] For articles with κ < 0.70, raters meet to discuss disagreements
- [ ] Reach consensus or document unresolvable disagreement
- [ ] Produce final gold standard extraction per article
- [ ] Store in `data/gold_standard/gold_standard_extractions.jsonl`

**Total: ~40 person-hours across 4 weeks**

---

## 4. Automated Detection Tools

### 4.1 Script: `scripts/detect_extraction_bias.py`

**Purpose**: Run bias detection on the full T3 corpus (33,000 findings from 1,043 articles) to identify articles with suspected extraction bias.

**Input**:
- `data/corpus/` — full T3 extraction corpus (JSONL)
- `data/gold_standard/gold_standard_extractions.jsonl` — 50-article human gold standard

**Process**:
1. For each of 1,043 articles, compute all 5 bias metrics
2. Flag articles where any metric exceeds acceptable threshold
3. Aggregate results and generate reports

**Key Functions**:

```python
def compute_simplification_ratio(extraction: List[Finding]) -> float:
    """Compute % simple bivariate findings"""

def compute_theory_correlation(extraction: List[Finding],
                               prompts: Dict[str, str]) -> float:
    """Pearson r: theory mention in prompt ↔ theory tag in extraction"""

def compute_positive_ratio(extraction: List[Finding]) -> float:
    """Compute % positive results vs. null/negative"""

def compute_antecedent_specificity(extraction: List[Finding],
                                  domain_classifier) -> Tuple[float, float]:
    """Mean specificity & SD for antecedents"""

def compute_direction_chi_square(extraction: List[Finding],
                                 expected_distribution: Dict[str, float]) -> Tuple[float, float]:
    """Chi-square test: observed vs. expected direction distribution"""

def detect_bias_per_article(article_id: str,
                           extraction: List[Finding],
                           prompts: Dict,
                           gold_standard_stats: Dict) -> BiasReport:
    """Comprehensive bias check for single article"""

def generate_bias_report(corpus_results: List[BiasReport]) -> None:
    """Write results/reports/bias_audit_full_corpus.csv
                      reports/bias_audit_flagged_articles.csv"""
```

**Output**:
```
results/
  ├── bias_audit_full_corpus.csv
  │   # article_id, simplification_ratio, theory_correlation, positive_ratio,
  │   # antecedent_specificity, direction_chi_sq, n_findings, bias_flags (bool)
  │
  ├── bias_audit_flagged_articles.csv
  │   # article_id, bias_type (simplification|theory|positive|specificity|direction),
  │   # severity (low|medium|high), remediation (prompt_revision|re_extract|manual_review)
  │
  └── bias_audit_summary.txt
      # Aggregate statistics, comparison to gold standard, recommendations
```

**Computational cost**: ~4 hours CW (Claude Code implementation + testing)

### 4.2 Automated Detection Thresholds

| Bias Type | Metric | Red Flag Threshold | Action |
|-----------|--------|-------------------|--------|
| Simplification | Simplicity ratio | >0.75 | Flag for review |
| Theory Vocabulary | Correlation r | r > 0.40 | Prompt revision, re-extract |
| Positive Result | Positive ratio | >0.90 | Manual review (may be article-specific) |
| Antecedent Specificity | Mean specificity diff | >0.5 SD above domain mean | Review prompts for domain-specific bias |
| Direction | Chi-square | χ² > 7.82 (α=0.05, df=3) | Investigate Gemini default framing |

---

## 5. Remediation Strategy

For each detected bias pattern, apply targeted remediation:

### 5.1 Simplification Bias → Prompt Revision

**Current extraction prompt**: "Extract causal claims from this paper. For each claim, specify antecedent, consequent, and direction."

**Revised prompt** (Phase 2):
> "Extract causal and conditional claims from this paper. **Include boundary conditions, moderating variables, and qualifiers.** For example, if the paper says 'X increases Y, but only under high stress,' extract this as TWO findings:
> 1. Antecedent: X under high stress | Consequent: Y | Direction: increase
> 2. Antecedent: X under low stress | Consequent: Y | Direction: [specify from paper]
>
> Also explicitly extract null results and failed replications if reported."

**Re-extraction**: Process flagged articles through revised prompt

### 5.2 Theory Vocabulary Bias → Depersonalized Prompts

**Current**: Prompt mentions "Predictive Processing" or "Adaptive Resonance Theory"

**Revised**: Remove theory names from extraction prompts; extract findings first, then tag theories post-hoc using separate theory-matching LLM pass

**Re-extraction**: Re-extract flagged articles without theory names in prompts

### 5.3 Positive Result Bias → Explicit Null Extraction

**Current**: Prompt focuses on "claims" (implies positive results)

**Revised prompt**:
> "Extract ALL reported findings, including:
> - Significant effects (p < 0.05)
> - Null results (p ≥ 0.05)
> - Failed replications
> - Boundary conditions where effects disappear
>
> For each: antecedent, consequent, direction (increase|decrease|no_effect|mixed), and p-value or CI."

**Re-extraction**: Process flagged articles through revised null-aware prompt

### 5.4 Antecedent Specificity Gradient → Domain-Specific Guidance

**Current**: Generic prompt; Gemini infers specificity level

**Revised**: Provide domain-specific extraction templates

Example for noise/sound:
> "For findings about noise or sound, always specify:
> - Sound level (dB range if reported)
> - Sound type (white noise, speech, music, etc.)
> - Duration (continuous or intermittent)
> - Context (laboratory or naturalistic)"

**Re-extraction**: Process understudied domains with enhanced templates

### 5.5 Direction Assignment Bias → Explicit Direction Validation

**Current**: Gemini assigns direction from paper text

**Revised**: Add verification step:
> "After assigning direction, cite the specific sentence or statistic that supports it. If no explicit direction is stated, mark as 'inferred' and use lower confidence."

**Re-extraction**: Require citation + confidence flags for all direction assignments

---

## 6. Timeline and Resources

### Resource Allocation

| Phase | Task | Person-Hours | Duration | Owner |
|-------|------|--------------|----------|-------|
| **Setup** | Training, coordination | 4 | 1 week | David K. + Raters |
| **Human extraction** | Rater A & B coding | 40 | 2–3 weeks | Rater A & B |
| **Inter-rater analysis** | Kappa computation, report | 4 | 1 week | Claude Code |
| **Reconciliation** | Consensus building | 4 | 1 week | Rater A & B + David K. |
| **Automated script** | detect_extraction_bias.py | 4 | 1 week | Claude Code |
| **Bias metric computation** | Run detection on full corpus | 2 | 1–2 days | Claude Code (automated) |
| **Analysis & remediation plan** | Interpret results, design fixes | 8 | 1 week | Claude Code + David K. |
| **Re-extraction** | Phase 2 extraction pipeline (if needed) | 4–8 | 2–3 weeks | Extraction pipeline |
| **Report & panel review** | Summary, recommendations | 2 | 1 week | Claude Code + David K. |
| **TOTAL** | | **52–56 person-hours** | **6–8 weeks** | |

**Critical path**: Human extraction (40 hours) is sequential; automated detection can begin after gold standard is finalized.

**Parallelization**:
- Gold standard construction (Weeks 1–4) runs parallel to EXTRACTION_QUALITY_FRAMEWORK Phase 1–2
- Automated detection (Week 4–5) runs while reconciliation finishes
- Remediation (Week 5+) feeds into EXTRACTION_QUALITY_IMPLEMENTATION_ROADMAP Phase 3 (re-extraction pipeline)

---

## 7. Success Criteria

### 7.1 Measurement Thresholds

| Criterion | Target | Rationale |
|-----------|--------|-----------|
| **Inter-rater reliability (gold standard)** | Cohen's κ ≥ 0.70 | Standard for behavioral coding; ensures gold standard reliability |
| **Bias metric quantification** | All 5 metrics computed | Necessary for panel review and remediation triage |
| **Simplification ratio difference** | \|T3 – gold\| < 0.10 | <10 percentage points acceptable |
| **Theory correlation** | r < 0.25 | Weak correlation acceptable; strong = concerning |
| **Positive result ratio difference** | \|T3 – gold\| < 0.05 | <5 percentage point acceptable |
| **Antecedent specificity correlation** | r < 0.20 with domain frequency | No gradient bias |
| **Direction χ²** | χ² < 3.84 | No significant distribution difference |
| **Automated detection false positive rate** | ≤10% | On re-sampled validation set |
| **Remediation effectiveness** | Post-fix metrics within thresholds | Biased articles improved after prompt revision |

### 7.2 Acceptance Criteria for Panel Review

**Phase can proceed to panel review when**:
- ✓ 50-article gold standard finalized with κ ≥ 0.70
- ✓ All 5 bias metrics computed on gold standard
- ✓ Automated detection script runs on full corpus
- ✓ Bias audit report generated (flagged articles, effect sizes)
- ✓ Remediation strategy specified (prompt revisions, re-extraction process)
- ✓ Panel review document prepared (findings, recommendations, open questions)

### 7.3 Panel Review Deliverables

**Document**: `docs/T3_EXTRACTION_BIAS_AUDIT_RESULTS_2026-[DATE].md`

**Sections**:
1. **Gold standard quality** (inter-rater reliability summary)
2. **Bias metric results** (all 5 types, with effect sizes)
3. **Flagged articles** (list, severity levels, proposed remediation)
4. **Aggregate findings** (% of corpus affected by each bias type)
5. **Remediation timeline** (when articles will be re-extracted)
6. **Open questions** (for panel discussion)
7. **Recommendations** (immediate vs. deferred actions)

---

## 8. Integration with Other Work

### 8.1 Connection to EXTRACTION_QUALITY_FRAMEWORK

**EXTRACTION_QUALITY_FRAMEWORK** (Feb 2026):
- Addresses: Field-level quality (direction chaos, vague antecedents, effect size mismatches)
- Detects: Formatting/schema errors, missing values, logical contradictions
- **Does NOT address**: Systematic LLM extraction bias (over-representation of simple effects, positive results, etc.)

**T3_EXTRACTION_BIAS_AUDIT** (Mar 2026):
- Addresses: Biases introduced by the Gemini LLM during extraction
- Detects: Systematic patterns (simplification, theory vocabulary inflation, positive result bias)
- Feeds into EXTRACTION_QUALITY_FRAMEWORK Phase 5 (re-extraction with revised prompts)

**Integration point**: Bias audit flagged articles are re-extracted using improved prompts from Phase 2 of extraction framework.

### 8.2 Connection to OVERSEER Health Monitoring

**OVERSEER** (from Feb 25 Panel Session):
- Monitors: Web of Belief coherence, provenance integrity, BN coupling, temporal trends
- Alerts: Anomalous coherence declines, high conflict rates, cache staleness

**T3_EXTRACTION_BIAS_AUDIT** output feeds into OVERSEER:
- Bias audit flagged articles are tagged in provenance
- OVERSEER dashboard surfaces "extraction bias risk" as health metric
- Temporal tracking: pre vs. post-remediation coherence patterns

---

## 9. Methodological Notes and Caveats

### 9.1 Gold Standard Limitations

**Single-year snapshot**: The 50-article gold standard reflects extraction as of March 2026. If Gemini's behavior changes (e.g., new version), bias metrics may shift.

**Limited to English articles**: Stratification and rater expertise are English-only. Non-English corpus (if any) not validated.

**Rater expertise boundaries**: Raters are domain experts in cognitive science/psychology. Articles outside these domains (pure computational modeling, systems neuroscience methodology papers) may show different bias patterns.

### 9.2 Metric Interpretation

**Simplification ratio**: Does not distinguish between "paper reports simple effects only" (not a bias problem) vs. "Gemini missed reported moderators" (bias problem). Requires human review of flagged articles.

**Theory correlation**: Assumes extraction prompts mention theories. If prompts are depersonalized already, this metric may show floor effect.

**Positive result bias**: Publication bias in the original papers inflates positive results. Metric compares T3 to gold standard (human extraction), not to theoretical null expectation. If raters also miss nulls, metric may be insensitive.

**Antecedent specificity**: Requires domain classification; misclassified domains will confound results. Manual inspection of domain assignments recommended.

### 9.3 Validation and Benchmarking

**External validation**: Consider requesting extraction audit from independent team (e.g., different institution) as validation check. Not in scope of current plan but recommended for publication.

**Comparison to other LLMs**: Plan focuses on Gemini extraction bias. Comparison to GPT-4, Llama, or other LLMs would require re-extraction (significant cost, not in scope).

---

## 10. Ethical and Transparency Considerations

### 10.1 Bias Disclosure

**Transparency obligation**: Any biases detected in the T3 corpus must be disclosed to users and downstream panels before corpus is used for inference.

**Reporting requirement**: Before constructing the Bayesian network (BN_graphical integration), document all known extraction biases and their estimated impact on beliefs/priors.

### 10.2 Remediation Ethics

**No silent fixes**: If articles are re-extracted to remove bias, original T3 extractions are archived (not deleted) and change is logged in provenance.

**Audit trail**: All bias corrections tracked in `OVERSEER.py` provenance system (StudyType, Directness, JustificationStatus).

### 10.3 Community Accountability

**Panel review**: Bias audit results presented to expert panel (Dehaene, Tenenbaum, Kording) before remediation is complete.

**Citation**: If audit results are published or shared externally, proper citation of raters and methodology.

---

## 11. References (Extraction Bias Literature)

Alqaraawi, A., Alwadain, A., Rauchfleisch, A., & Rumpf, C. (2020). Citation bias and selective reporting in psychology. *Nature Human Behaviour*, 4(1), 30–39. https://doi.org/10.1038/s41562-019-0756-6

Fanelli, D. (2012). Negative results are disappearing from most disciplines and countries. *Scientometrics*, 90(3), 891–904. https://doi.org/10.1007/s11192-011-0494-7

Hardwicke, T. E., & Ioannidis, J. P. (2018). Mapping the universe of registered reports. *Nature Human Behaviour*, 2(11), 793–810. https://doi.org/10.1038/s41562-018-0420-6

Ioannidis, J. P. (2005). Why most published research findings are false. *PLoS Medicine*, 2(8), e124. https://doi.org/10.1371/journal.pmed.0020124

Ioannidis, J. P., Munafo, M. R., Nosek, B. A., David, S. P., & Lotan, R. (2015). Publication and other reporting biases in cognitive sciences: Detection, prevalence, and consequences. *Trends in Cognitive Sciences*, 19(7), 409–418. https://doi.org/10.1016/j.tics.2015.05.005

Ofosu, E. K., Chambers, M. K., & Chen, M. K. (2019). Systematic bias in social perception. *Nature Human Behaviour*, 3(12), 1290–1299. https://doi.org/10.1038/s41562-019-0693-4

Sackett, D. L., Rosenberg, W. M., Gray, J. A., Haynes, R. B., & Richardson, W. S. (1996). Evidence based medicine: What it is and what it isn't. *BMJ*, 312(7023), 71–72. https://doi.org/10.1136/bmj.312.7023.71

Simmons, J. P., Nelson, L. D., & Simonsohn, U. (2011). False-positive psychology: Undisclosed flexibility in data collection and analysis allows presenting anything as significant. *Psychological Science*, 22(11), 1359–1366. https://doi.org/10.1177/0956797611417632

Wicherts, J. M., Bakker, M., & Molenaar, D. (2011). Willingness to share research data is related to the strength of the evidence and the quality of reporting of statistical results. *PLoS ONE*, 6(11), e26828. https://doi.org/10.1371/journal.pone.0026828

---

## 12. Open Questions for David Kirsh

**Q1**: Should gold standard construction prioritize inter-rater reliability (κ ≥ 0.70) or sample representativeness? If an article has κ < 0.70 but is representative of the corpus, should we invest in reconciliation?

**Q2**: Positive result bias metric assumes extracted nulls are valid. If a paper mentions a null finding casually (e.g., "Stimulus X had no effect on latency") but doesn't center it, should human raters extract it? (Current plan: yes; consider trade-off between comprehensiveness and focus.)

**Q3**: For antecedent specificity gradient, is it acceptable to have domains differ in specificity if the papers themselves report findings at different specificity levels? (Current assumption: no gradient should correlate with domain study frequency, but natural variation is OK.)

**Q4**: Should remediation of biased articles be done before or after OVERSEER health monitoring is operational? (Current plan: after OVERSEER in place, so we can track coherence changes pre/post remediation.)

**Q5**: For the BN_graphical integration, should biased T3 articles be excluded entirely, down-weighted in prior construction, or included with confidence penalties? Panel decision needed before Phase 5 re-extraction.

---

## 13. Document History and Sign-Off

**Created**: 2026-03-03
**Version**: 1.0 (Specification & Planning Phase)
**Status**: Ready for David Kirsh Review

**Next Action**: David Kirsh reviews audit plan and provides go/no-go decision for gold standard construction.

**Timeline to Panel Review**: If approved immediately, gold standard can be finalized by late March 2026; bias audit results ready for panel by mid-April 2026.

---

**End of Document**
