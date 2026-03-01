# Sprint QA Design Decisions Log — For Panel Review

**Purpose:** Track all significant design decisions made during QA sprint execution, with context and rationale. Each decision is tagged with a DD-# for reference in panel review.

---

## Sprint QA-1: The Honest Answer

### DD-1: Always Generate Search Prompts 🔬
**Decision:** Generate `open_questions.search_prompts` even when the answer is strong (diagnosis == "strong_but_improvable").
**Rationale:** A confident answer can still benefit from replication evidence. Omitting search prompts for strong answers implies the system is "done learning" — which contradicts the Quinean/holist philosophy of perpetual revisability.
**Alternative considered:** Only generate prompts for corpus_gap and analysis_gap.
**Risk:** Users may feel overwhelmed by suggestions on every answer.
**Panel question:** Should prompts be hidden by default in strong answers and shown only on user request?

### DD-2: Heuristic Credence Improvement Estimate 🔬
**Decision:** Estimate credence improvement as `min(0.95, credence + uncertainty * 0.4)` with uncertainty halved, rather than running full BN sensitivity analysis.
**Rationale:** The BN sensitivity module requires a live, initialized Bayesian Network which may not be available. A heuristic keeps the feature always-available. Full BN sensitivity is deferred to Sprint QA-3.
**Alternative considered:** Make the feature conditional on BN availability.
**Risk:** Heuristic may over- or under-estimate improvement, misleading users.
**Panel question:** Is 0.4 × uncertainty the right uplift factor? Should we calibrate this against historical data?

### DD-3: Threshold-Based Gap Classification 🔬
**Decision:** Classify gap types using simple thresholds (0 matches → corpus_gap, credence < 0.4 → analysis_gap, else strong_but_improvable) rather than the full `GapPredictor` pipeline.
**Rationale:** `GapPredictor` requires initialized web + edge justification service and can be slow. Classification must be fast and always work. The `GapPredictor` is used as an *enrichment* layer when available, not as the primary classifier.
**Alternative considered:** Always require GapPredictor.
**Risk:** Simple thresholds may misclassify edge cases (e.g., many beliefs but none causally relevant).
**Panel question:** Should we add a "relevance_gap" diagnosis for cases where many beliefs match keywords but none are actually relevant?

### DD-4: Google Scholar AI as Primary Search Target 🔬
**Decision:** Generate search prompts specifically for "Google Scholar AI" rather than generic academic databases.
**Rationale:** The user has explicitly identified Google Scholar AI as their primary acquisition tool. Prompts should be optimized for this specific interface.
**Alternative considered:** Generic search prompts adaptable to any database.
**Risk:** Coupling to a specific tool that may change or become unavailable.
**Panel question:** Should we also generate PubMed-structured queries (MeSH terms) as an alternative?

### DD-5: Open Questions in Detail + Deep Dive Only 🔬
**Decision:** Only attach `open_questions` to responses at detail and deep_dive levels, not headline or summary.
**Rationale:** Headlines and summaries are meant to be fast. Adding open questions would clutter them. Users seeking depth (detail/deep_dive) are the ones most likely to act on gap-filling suggestions.
**Alternative considered:** Include a one-line "corpus gap indicator" even in summary mode.
**Risk:** Users who only use summary mode will never see open questions.
**Panel question:** Should summary mode include a boolean `has_knowledge_gaps` flag that signals the user to drill deeper?

### DD-6: No-Results Response Always Gets Open Questions 🔬
**Decision:** `_no_results_response()` always includes `open_questions` even when `include_gaps=False`.
**Rationale:** A "no results" response is the strongest possible corpus gap signal. Withholding acquisition prompts when the user explicitly asked a question the system can't answer would be epistemically dishonest.
**Alternative considered:** Respect `include_gaps=False` even for no-results.
**Risk:** None significant. This is a user-facing improvement.

---

## Sprint QA-2: The Architect's Spec Sheet

### DD-7: Use calibrated_parameters Only (Not Free-Text Mining) 🔬
**Decision:** Extract thresholds exclusively from `calibrated_parameters` (panel-reviewed values with confidence levels) rather than regex-mining numbers from free-text descriptions.
**Rationale:** Every threshold needs provenance and confidence. Mining "300 lux" from a prose description loses the confidence level, the CI, and the bridge warrant type.
**Live result:** 100/208 templates have calibrated_parameters, yielding 34 thresholds for healthcare alone.
**Panel question:** Should we add a secondary "approximate thresholds" tier mined from text, clearly marked as unreviewed?

### DD-8: Substring Matching for Building Types 🔬
**Decision:** Match building_type queries using substring matching (e.g., "hospital" matches both "healthcare" and "hospitals — highest priority, largest documented effect").
**Rationale:** The `building_types` field is heterogeneous — some are one-word ("office"), others are descriptive phrases. Exact matching would miss most entries.
**Risk:** False positives (e.g., "school" matching "school_dormitories" when the user means classrooms).
**Panel question:** Should we implement a canonical building type taxonomy and normalize all entries?

### DD-9: Organize Spec Sheet by Architectural Domain 🔬
**Decision:** Group thresholds by domain (acoustic, visual/light, air quality, spatial, biophilic, thermal) rather than by template source.
**Rationale:** Architects organize specifications by domain (CSI MasterFormat), not by evidence source. Domain-organized output maps directly to their workflows.
**Alternative:** Organize by template, which better preserves mechanistic context.
**Panel question:** Should the spec sheet support both views (by-domain and by-template)?

### DD-10: Template Prefix + Unit Heuristic for Domain Classification 🔬
**Decision:** Classify thresholds by template display_id prefix (AUD_ → acoustic) with unit-based fallback (dB → acoustic).
**Rationale:** Most templates have domain-meaningful prefixes. Units provide a reliable secondary signal.
**Risk:** Templates with non-standard prefixes may be misclassified.
**Panel question:** The "other" domain caught 20/34 thresholds in the healthcare test. Should we add more domain categories or refine prefix matching?

## Sprint QA-4: The Last Mile

### DD-11: Approximate GRADE Mapping 🔬
**Decision:** Map ATLAS maturity levels directly to GRADE ratings (established→HIGH, supported→MODERATE, preliminary→LOW, speculative→VERY_LOW).
**Rationale:** Full GRADE methodology requires structured assessment of risk of bias, inconsistency, indirectness, imprecision, and publication bias — which we cannot automate. An approximate mapping with a disclaimer is better than no mapping.
**Panel question:** Should we flag when the GRADE rating would likely differ from the maturity-based approximation (e.g., when a "supported" finding has high heterogeneity)?

### DD-12: Static Proxy Metric Translation Table 🔬
**Decision:** Use a static mapping of 20 scientific outcomes → facilities KPIs rather than LLM-generated translations.
**Rationale:** Consistency and auditability. A facilities manager needs to trust that "circadian entrainment" always maps to "sick days per quarter" — not to a different metric each query.
**Panel question:** Are the 20 outcomes comprehensive enough? Should we add environment-specific KPIs (hospital vs. office)?

### DD-13: Static vs. LLM Glossary 🔬
**Decision:** 24-term static glossary matched by substring rather than LLM-generated definitions.
**Rationale:** Accuracy. An LLM might define "entrenchment" in the common sense rather than the coherentist epistemology sense.
**Risk:** Glossary won't adapt to new terms without manual updates.
**Panel question:** Should we auto-detect and flag terms NOT in the glossary as candidates for expert definition?

### DD-14: Standards Registry Scope 🔬
**Decision:** Cover WELL v2, LEED v4.1, BREEAM, ASHRAE, EN/ISO only. US, EU, UK, International jurisdictions.
**Rationale:** These are the most widely adopted standards. Country-specific codes (e.g., German DIN, Japanese JIS) are omitted for now.
**Panel question:** Which additional standards are essential for non-Western jurisdictions?

### DD-15: Contraindication Severity Levels 🔬
**Decision:** Four severity levels (critical, high, medium, low). Critical contraindications (e.g., photosensitive epilepsy with bright light) should be shown prominently.
**Rationale:** Clinical decision support must distinguish "might cause discomfort" from "might cause a seizure."
**Risk:** Static registry may miss newly discovered contraindications.
**Panel question:** Should critical contraindications block the recommendation entirely, or just add a warning?

## Sprint QA-3: The Evidence Layer

### DD-17: Effect Size Detection from calibrated_parameters 🔬
**Decision:** Detect effect types by scanning parameter names/units for Cohen's d, ratio, proportion, beta indicators. Classify magnitude per Cohen's benchmarks (d: 0.2/0.5/0.8/1.2, r: 0.1/0.3/0.5, OR: 1.5/2.5/4.0).
**Rationale:** No dedicated `effect_size` field exists. The calibrated_parameters contain embedded effect size data that can be reliably detected.
**Live test:** 4 effect sizes extracted for circadian query. `circadian entrainment=4.5` classified as large; `noradrenergic response=0.22` classified as small.
**Panel question:** Should we distinguish between within-subjects and between-subjects effect sizes in the magnitude classification?

### DD-18: Maturity → Study Design Badges 🔬
**Decision:** Map maturity levels to study design categories: established→Multiple RCTs (🟢), supported→RCT/SR (🟢), how-actually→Quasi-experimental (🟡), how-plausibly→Observational (🟠), how-possibly→Case study (🔴).
**Rationale:** Templates don't have a `study_design` field. Maturity is the closest proxy: "established" implies RCT evidence exists.
**Risk:** Some "established" findings rely on observational evidence.
**Panel question:** Should we add a manual override field to templates for cases where maturity doesn't match study design?

### DD-19: Evidence Strength Aggregation 🔬
**Decision:** Weighted average of study design levels across matched templates, collapsed into 4 tiers (strong/moderate/preliminary/weak).
**Rationale:** A single badge gives users immediate quality signal before reading details.
**Panel question:** Should we weight effect size magnitude into the aggregation?

## Sprint QA-5: Browse ↔ QA Integration

### DD-20: Deterministic Question Generation 🔬
**Decision:** Generate questions from template structure (name, mechanism chain, scope conditions, building types) rather than LLM.
**Rationale:** Deterministic, auditable, fast. 518 questions generated for 166 templates.
**Panel question:** Should we also generate "What if?" questions for creative exploration?

### DD-21: Vocabulary Bridge Lookup Table 🔬
**Decision:** 884-keyword → template_id mapping built from template names, mechanism chains, and calibrated parameter names.
**Rationale:** browse and QA use different vocabularies. The bridge enables "Did you mean template CLE1?" when users search for "circadian."

### DD-22: Entity Overlap for Related Templates 🔬
**Decision:** Find related templates by counting mechanism_chain entity overlap with matched templates.
**Rationale:** Simple, effective for <500 templates. Enables QA→Browse navigation.

## Sprint QA-6: Creative Modes

### DD-23: Template-Driven Grant Proposals 🔬
**Decision:** Grant sections cite actual template data (effect sizes, references, mechanism chains) rather than LLM-generated text.
**Rationale:** Every claim in the grant section is traceable to the evidence base.
**Panel question:** Should we generate NIH-specific vs. NSF-specific formats?

### DD-24: Template Library as Systematic Review Source 🔬
**Decision:** Extract PICO components, search strategies, and quality assessments directly from the template library.
**Rationale:** The template library IS effectively a curated systematic review. We can accelerate formal SRs by exporting its structure.

### DD-25: Static Discipline Vocabulary Mapping 🔬
**Decision:** 5-discipline vocabulary mapping (architecture, psychology, neuroscience, public health, environmental design) with discipline-specific framing and implications.
**Rationale:** The same finding means different things to different disciplines. Static mapping ensures consistent translation.

---

*This document is maintained by Gemini (Antigravity) and should be reviewed by the expert panels after each sprint.*
