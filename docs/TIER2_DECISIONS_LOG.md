# Epistemic Tier 2 — Implementation Decisions Log

**Started**: Friday, February 14, 2026
**Purpose**: Track all implementation decisions for panel review

---

## Decision Format (Enhanced)

Each decision is tracked with:

| Field | Description |
|-------|-------------|
| **ID** | Unique identifier (D{sprint}.{number}) |
| **Decision** | What was decided |
| **Context** | Why this decision arose |
| **Alternatives** | Other options considered |
| **Rationale** | Why this choice was made |
| **Risk** | What could go wrong (Low/Medium/High) |
| **Dependencies** | Other decisions this depends on or affects |
| **Panelist Concerns** | Which expert voices should review this |

---

## Risk Legend

- **Low**: Easily reversible, local impact, no data migration
- **Medium**: Requires refactoring, affects multiple files, may need migration
- **High**: Architectural impact, hard to reverse, affects external interfaces

---

## Sprint 0 Decisions

### D0.1: Place new enums in `web_of_belief.py`
- **Context**: Task 0.1 mapping found all core enums there
- **Alternatives**: Create new `enums.py` file
- **Rationale**: Consistency with existing codebase; all epistemic enums co-located
- **Risk**: Low — file organization only
- **Dependencies**: None
- **Panelist Concerns**: Simon (modularity)

### D0.2: Extend `ConstraintType` for link types
- **Context**: No separate `LinkType` enum exists
- **Alternatives**: Create new `LinkType` enum
- **Rationale**: `ConstraintType` already serves this role; less refactoring
- **Risk**: Low — enum extension is additive
- **Dependencies**: None
- **Panelist Concerns**: Liskov (interface design)

### D0.3: Accept 19 pre-existing test failures
- **Context**: Baseline shows failures unrelated to Tier 2
- **Alternatives**: Fix them first
- **Rationale**: Out of scope; failures are API wiring issues, not epistemic logic
- **Risk**: Low — tracked separately, doesn't affect Tier 2 work
- **Dependencies**: None
- **Panelist Concerns**: None (engineering decision)

---

## Sprint 1 Decisions

### D1.1: Create new `NodeDomain` enum (not extend existing)
- **Context**: No domain enum existed; only `domain: str` field
- **Alternatives**: Extend EpistemicLevel or BeliefKind
- **Rationale**: Clean separation of concerns; NodeDomain is about knowledge area, not epistemic position or functional role
- **Risk**: Low — new enum, no existing code affected
- **Dependencies**: None
- **Panelist Concerns**: Haack (domain vs. level distinction)

### D1.2: Add `node_domain: Optional[NodeDomain]` field, keep legacy `domain: str`
- **Context**: Backward compatibility with existing serialized data
- **Alternatives**: Replace domain field entirely
- **Rationale**: Gradual migration; existing code continues to work
- **Risk**: Low — additive change
- **Dependencies**: D1.1
- **Panelist Concerns**: Simon (migration strategy)

### D1.3: Place all Tier 2 enums in web_of_belief.py
- **Context**: All existing enums are there
- **Alternatives**: Create new epistemic_enums.py
- **Rationale**: Consistency; avoid import complexity
- **Risk**: Low — file grows but remains cohesive
- **Dependencies**: D0.1
- **Panelist Concerns**: Liskov (module cohesion)

### D1.4: Add epistemic link types to ConstraintType (not new enum)
- **Context**: ConstraintType already serves as link type enum
- **Alternatives**: Create separate LinkType enum
- **Rationale**: Less refactoring; existing edge code expects ConstraintType
- **Risk**: Medium — ConstraintType grows; may need splitting later
- **Dependencies**: D0.2
- **Panelist Concerns**: Liskov (single responsibility)

### D1.5: Default confidence for EPISTEMIC_COHERENCE_WARRANT = 0.55
- **Context**: Coherence alone is moderate evidence
- **Alternatives**: Higher (0.70) or lower (0.40)
- **Rationale**: Middle ground; coherence without scrutiny is informative but not definitive
- **Risk**: Medium — affects downstream probability calculations
- **Dependencies**: None
- **Panelist Concerns**: Spohn (rank calibration), Haack (coherence weight)

### D1.6: Default confidence for ARGUMENTATIVE_WARRANT = 0.70
- **Context**: Survived adversarial scrutiny
- **Alternatives**: Same as mechanism (0.60)
- **Rationale**: Higher because adversarial testing is strong epistemic filter
- **Risk**: Medium — may overweight adversarial studies
- **Dependencies**: None
- **Panelist Concerns**: Pollock (defeat resilience), Longino (social epistemics)

### D1.7: Default confidence for EPISTEMIC_VIGILANCE_WARRANT = 0.65
- **Context**: Source quality evaluation
- **Alternatives**: Same as coherence (0.55)
- **Rationale**: Slightly higher; explicit quality check adds confidence
- **Risk**: Medium — depends on quality assessment accuracy
- **Dependencies**: None
- **Panelist Concerns**: Cartwright (source reliability)

### D1.8: Add GENERALIZABILITY_WARRANT to ConstraintType (Sprint 4b prep)
- **Context**: Type A → Type B claims need explicit link
- **Alternatives**: Defer to Sprint 4b
- **Rationale**: Pre-emptive; schema change now avoids migration later
- **Risk**: Low — unused until Sprint 4b
- **Dependencies**: D1.4
- **Panelist Concerns**: None (forward planning)

### D1.9: Forward-reference enums in Belief fields with Optional['EnumName']
- **Context**: Enums defined before Belief class but used in type hints
- **Alternatives**: String literals only
- **Rationale**: Type safety with forward references; IDE support
- **Risk**: Low — Python typing convention
- **Dependencies**: D1.1, D1.3
- **Panelist Concerns**: None (engineering decision)

### D1.10: Include Sprint 4b fields in Belief now (claim_type, effect_pathway, etc.)
- **Context**: Sprint 4b runs parallel to 2-4
- **Alternatives**: Add later in Sprint 4b
- **Rationale**: Avoid schema change mid-sprint; all fields optional so no breakage
- **Risk**: Low — optional fields, no serialization impact
- **Dependencies**: D1.1, D1.3
- **Panelist Concerns**: Simon (planning ahead vs. YAGNI)

---

## Sprint 2 Decisions

### D2.1: Create separate `src/epistemic/` module for BN infrastructure
- **Context**: Need to add epistemic BN nodes, edges, and monitors
- **Alternatives**: Add to `epistemic_causal_bridge.py`
- **Rationale**: Clean separation; epistemic_causal_bridge.py already 132KB; new module enables future isolation
- **Risk**: Low — new module, no existing code affected
- **Dependencies**: None
- **Panelist Concerns**: Simon (modularity)

### D2.2: EpistemicVariable dataclass with `supporting_belief_pattern` regex field
- **Context**: Need to connect BN variables to web of belief nodes
- **Alternatives**: Hard-coded mapping table
- **Rationale**: Pattern matching allows flexible, extensible belief-to-variable mapping
- **Risk**: Medium — regex patterns may need tuning for coverage
- **Dependencies**: D2.1
- **Panelist Concerns**: Haack (belief-variable grounding)

### D2.3: Create stub nodes for external BN connections
- **Context**: Environmental edges target `overall_wellbeing`, `wayfinding_success`, `allostatic_regulation` which may not exist yet
- **Alternatives**: Skip edges until full BN integration
- **Rationale**: Stub nodes enable testing edge wiring now; will be replaced by actual nodes later
- **Risk**: Low — stubs are placeholders; clearly marked for replacement
- **Dependencies**: D2.1
- **Panelist Concerns**: None (engineering decision)

### D2.4: PE edges have negative weight (reduce epistemic affect)
- **Context**: Prediction errors are negative signals in predictive processing
- **Alternatives**: All positive weights, handle sign in structural equations
- **Rationale**: Explicit negative weight makes causal direction clear in edge definition
- **Risk**: Medium — weight signs must be respected in downstream computations
- **Dependencies**: D2.1
- **Panelist Concerns**: Pearl (structural equation semantics)

### D2.5: All epistemic edges default to `personal_epistemic` pathway type
- **Context**: Epistemic variables are interpretation-mediated by definition
- **Alternatives**: Mixed pathway; case-by-case tagging
- **Rationale**: Epistemic processing inherently requires conscious interpretation
- **Risk**: Low — consistent default; exceptions can override
- **Dependencies**: D1.9 (pathway_type on Edge)
- **Panelist Concerns**: Haack (subpersonal vs. personal distinction)

### D2.6: Edge weights as explicit floats in EpistemicEdge dataclass
- **Context**: Need edge strength for structural equations
- **Alternatives**: Separate weight table; infer from variable types
- **Rationale**: Co-locate weight with edge for clarity; easier to audit and adjust
- **Risk**: Medium — weights are approximations; need calibration against data
- **Dependencies**: D2.1
- **Panelist Concerns**: Pearl (weight calibration), Cartwright (effect size)

### D2.7: Define local PathwayType enum in bn_edges.py
- **Context**: Needed for PATHWAY_DEFAULTS lookup table
- **Alternatives**: Import from web_of_belief.py
- **Rationale**: Avoid circular import issues; enum is simple and self-contained
- **Risk**: Low — duplicate definition but values are identical
- **Dependencies**: D1.9
- **Panelist Concerns**: None (engineering decision)

### D2.8: Default source quality weights (rigor=0.40, independence=0.25, replication=0.20, commitment=0.15)
- **Context**: Need to weight source quality components
- **Alternatives**: Equal weights; literature-derived weights
- **Rationale**: Methodological rigor most impactful; commitment penalty smallest (nuanced)
- **Risk**: Medium — weights are approximations; may need domain-specific adjustment
- **Dependencies**: D2.1
- **Panelist Concerns**: Cartwright (weight justification), Haack (commitment vs. quality)

### D2.9: Theoretical commitment inverted in source quality (high commitment = lower quality)
- **Context**: A priori theoretical commitment can bias study design
- **Alternatives**: Positive influence; separate bias metric
- **Rationale**: Confirmation bias literature supports penalty for high commitment
- **Risk**: Medium — oversimplifies; some commitment enables hypothesis testing
- **Dependencies**: D2.8
- **Panelist Concerns**: Longino (social epistemics), Pollock (theory-ladenness)

---

## Sprint 3 Decisions

### D3.1: Coherence drift threshold = 0.1 (10% change)
- **Context**: Need to distinguish meaningful vs. noise changes in entrenchment
- **Alternatives**: 0.05 (more sensitive), 0.2 (less sensitive)
- **Rationale**: 10% is significant enough to warrant attention but not so small as to flood with false positives
- **Risk**: Medium — may need tuning based on actual web behavior
- **Dependencies**: None
- **Panelist Concerns**: Haack (coherence significance)

### D3.2: Asymmetry ratio threshold = 3.0
- **Context**: When is entrenchment disproportionate to direct evidence?
- **Alternatives**: 2.0 (strict), 5.0 (lenient)
- **Rationale**: 3x entrenchment vs. evidence suggests coherence-driven credence
- **Risk**: Medium — depends on how entrenchment and evidence are normalized
- **Dependencies**: D2.8 (source quality weights)
- **Panelist Concerns**: Spohn (rank calibration)

### D3.3: Independence computed as 1 - (largest_cluster / total)
- **Context**: Need simple metric for lab independence
- **Alternatives**: Network-based clustering; author co-citation analysis
- **Rationale**: Simple heuristic that captures dominant-lab problem
- **Risk**: Low — easy to refine later; captures main concern
- **Dependencies**: None
- **Panelist Concerns**: Longino (social epistemics)

### D3.4: Diversity normalized to min(total, 5) paradigms/methods
- **Context**: How to normalize diversity across different evidence counts
- **Alternatives**: Fixed normalization (e.g., always divide by 5)
- **Rationale**: Accounts for small evidence bases; 5 distinct approaches is rich
- **Risk**: Low — normalization constant can be adjusted
- **Dependencies**: None
- **Panelist Concerns**: None (engineering decision)

### D3.5: Adversarial precision_boost = 1.5x counter-evidence weight
- **Context**: How much to amplify skeptical review
- **Alternatives**: 2.0x (aggressive), 1.2x (mild)
- **Rationale**: 50% boost simulates "careful skeptic" not "hostile critic"
- **Risk**: Medium — affects which beliefs appear vulnerable
- **Dependencies**: None
- **Panelist Concerns**: Pollock (defeat sensitivity)

### D3.6: Vulnerability score = (pre - post) / pre
- **Context**: Need to quantify how much entrenchment dropped
- **Alternatives**: Absolute difference; log ratio
- **Rationale**: Proportional drop is more interpretable than absolute
- **Risk**: Low — straightforward metric
- **Dependencies**: D3.5
- **Panelist Concerns**: None (engineering decision)

---

## Panel-Approved Revisions (2026-02-14)

*Consensus from simulated panel deliberation on Sprints 1-3 decisions*

### D-PANEL.1: Coherence warrant scales with link count
- **Context**: Panel review of D1.5 (EPISTEMIC_COHERENCE_WARRANT = 0.55)
- **Panel consensus**: Haack and Spohn agreed that coherence strength should scale with the number of supporting links
- **Decision**: Base 0.55 + sqrt-scaled boost, capped at 0.75
- **Implementation**: `compute_coherence_warrant(link_count)` returns 0.55 + min(0.15, 0.05 * sqrt(link_count))
- **Risk**: Low — enhancement to existing value; fully backward compatible
- **Dependencies**: D1.5 (supersedes fixed value)
- **Panelist Concerns**: Haack (cumulative coherence), Spohn (rank-sum)

### D-PANEL.2: Vigilance warrant scales with source quality
- **Context**: Panel review of D1.7 (EPISTEMIC_VIGILANCE_WARRANT = 0.65 fixed)
- **Panel consensus**: Cartwright argued fixed value is inappropriate; warrant should reflect actual source quality
- **Decision**: Linear scaling from 0.50 (quality=0) to 0.75 (quality=1)
- **Implementation**: `compute_vigilance_warrant(source_quality)` returns 0.50 + 0.25 * source_quality
- **Risk**: Low — enhancement to existing value; fully backward compatible
- **Dependencies**: D1.7 (supersedes fixed value), D2.8 (uses source quality computation)
- **Panelist Concerns**: Cartwright (evidence calibration)

### D-PANEL.3: Revised source quality weights
- **Context**: Panel review of D2.8 (original: rigor=0.40, independence=0.25)
- **Panel consensus**: Cartwright argued independence underweighted given replication crisis; Haack concurred
- **Decision**: Rebalance weights: rigor=0.35, independence=0.30, replication=0.20, commitment=0.15
- **Implementation**: Updated DEFAULT_SOURCE_QUALITY_WEIGHTS in source_quality.py
- **Risk**: Medium — affects existing source quality scores; all claims may need recalculation
- **Dependencies**: D2.8 (supersedes original weights)
- **Panelist Concerns**: Cartwright (replication crisis), Haack (weight balance)

### D-PANEL.4: Context-dependent commitment penalty
- **Context**: Panel review of D2.9 (commitment always inverted)
- **Panel consensus**: Longino and Pollock agreed confirmatory vs. exploratory distinction matters
- **Decision**: Full penalty for confirmatory studies (1.0x), half penalty for exploratory (0.5x), no penalty for replications/meta-analyses (0.0x)
- **Implementation**: StudyType enum with COMMITMENT_PENALTY_MULTIPLIER lookup; `compute_source_quality_context()` function
- **Risk**: Medium — requires study type classification; backward compatible via UNKNOWN type
- **Dependencies**: D2.9 (extends inversion logic)
- **Panelist Concerns**: Longino (social epistemics), Pollock (theory-ladenness)

---

## Sprint 4 Decisions

### D4.1: ArgumentativeMetadata dataclass with extended fields
- **Context**: Task 4.1 needs to capture argumentative structure
- **Alternatives**: Simple dict; minimal fields only
- **Rationale**: Dataclass provides type safety; extended fields enable rich analysis
- **Risk**: Low — extraction metadata only; doesn't affect core logic
- **Dependencies**: None
- **Panelist Concerns**: Pollock (defeat reasoning), Walton (argumentation schemes)

### D4.2: Regex-based theory reference extraction
- **Context**: Need to identify which theories a paper supports/challenges
- **Alternatives**: LLM-based extraction; hardcoded theory list
- **Rationale**: Regex is fast, interpretable, and can be incrementally improved
- **Risk**: Medium — may miss novel phrasings; can be tuned
- **Dependencies**: None
- **Panelist Concerns**: None (engineering decision)

### D4.3: SourceQualityMetadata with StudyDesign enum
- **Context**: Task 4.2 needs structured study design classification
- **Alternatives**: Free-text; simplified binary (good/bad)
- **Rationale**: Enum provides consistent hierarchy aligned with Cochrane GRADE
- **Risk**: Low — extraction metadata only
- **Dependencies**: None
- **Panelist Concerns**: Cartwright (evidence hierarchy)

### D4.4: Keyword-based pathway classification with mixed default
- **Context**: Task 4.3 needs to classify effect pathways
- **Alternatives**: LLM classification; require explicit annotation
- **Rationale**: Fast, interpretable, defaults to MIXED when uncertain (conservative)
- **Risk**: Low — classification can be overridden manually
- **Dependencies**: D1.4 (PathwayType enum)
- **Panelist Concerns**: None (conservative default handles uncertainty)

### D4.5: PE indicators required before subtype classification
- **Context**: Task 4.4 must distinguish PE claims from non-PE claims
- **Alternatives**: Classify all claims into PE subtypes
- **Rationale**: Only claims with explicit PE indicators get subtype; others return None
- **Risk**: Low — prevents false positives
- **Dependencies**: D1.6 (PESubtype enum)
- **Panelist Concerns**: None (conservative approach)

---

## Open Questions

*Questions requiring panel consultation*

| Q# | Question | Context | Options |
|----|----------|---------|---------|
