# Ruthless System Review: Expert Panel Responses

**Date**: January 22, 2026
**Review Type**: Comprehensive Architecture & Governance Audit

---

## Pearl (Causality & Inference)

### Assessment: APPROVE with MEDIUM modifications

**Q1: Causal Classification Tier Logic**
The design-first approach is epistemically sound. Experimental design SHOULD take precedence over language because language can be misleading while proper randomization actually warrants causal inference. Making causal language alone yield SUGGESTIVE is conservative but correct—observational studies using causal language without identification strategy are making unwarranted claims.

**Q2: Quasi-Experimental Handling**
Yes, quasi-experimental designs CAN yield CAUSAL tier when combined with strong causal language. Natural experiments with clear discontinuities (regression discontinuity) have nearly experimental validity. The current implementation correctly treats them as "between" but could be more nuanced.

**Recommendation**: Add a confidence modifier for quasi-experimental + causal language: currently yields CAUSAL at 0.60-0.85 confidence, which is appropriate.

**Q3: Confounder Gap Detection**
The severity levels are appropriate. Abstract-only causal claims without confounder mention ARE more concerning because we can't verify methodology. However, note that absence of confounder MENTION doesn't mean absence of confounder CONTROL—authors often control without explicitly naming confounders.

**Recommendation** (MEDIUM): Consider adding pattern for implicit control: "adjusted model", "Model 2", "after including covariates".

**Q4: Directional Opposition**
This is EXACTLY right. Credence represents belief strength, not direction. Two studies can both be highly credible (high credence) while reaching opposite conclusions. Directional opposition is the correct model for scientific disagreement.

**Specific Concerns**:
- `src/services/causal_classifier.py:445-480`: The `_determine_tier_pearl` logic is correct but could use more comments explaining the epistemology.
- Missing: Detection of instrumental variable validity (exclusion restriction violations).

---

## Cartwright (Evidence Portability)

### Assessment: APPROVE with HIGH modifications

**Q1: Bridge Warrants**
The four types are a reasonable starting taxonomy, but I'm concerned about:
1. **Constitutive at 0.85 is too high**—definitional bridges can be contested (what counts as "stress"?)
2. **Missing type: Capacities**—some bridges work because an entity has a stable capacity, not because of mechanism

**Recommendation** (HIGH): Add `capacity` bridge type with default P(bridge) ≈ 0.55. Example: "Plants have the capacity to reduce stress" doesn't specify mechanism but references stable capacity.

**Q2: Scope Conditions**
"Under what conditions does X affect Y?" is good but incomplete. Should also ask:
- "In what populations has this been tested?"
- "What's the effect size range across contexts?"

**Recommendation** (MEDIUM): Expand scope follow-up to reference specific populations/settings from the evidence.

**Q3: Measurement Method Differences**
Self-report vs physiological is critical. Also need:
- **Behavioral vs self-report** (what people do vs what they say)
- **Short-term vs long-term measures** (acute vs chronic effects)
- **Objective vs subjective** (lux levels vs perceived brightness)

**Recommendation** (MEDIUM): Add these measurement categories to disagreement detection.

**Q4: Evidence Quality Asymmetry**
This distinction is CRITICAL and maintainable. An abstract-only claim vs a full-text meta-analysis is not symmetric disagreement—it's evidence quality difference. Keep this.

**Specific Concerns**:
- `src/services/query_response.py:409-520`: The `_identify_disagreement_reasons` function is good but should distinguish "quality asymmetry" as a separate category in output.

---

## Simon (Bounded Rationality)

### Assessment: APPROVE

**Q1: Three-Tier vs Four-Tier**
Three tiers with warnings is correct satisficing. A fourth tier would exceed cognitive capacity for most users. The warning system conveys the nuance without requiring users to learn another category. Well done.

**Q2: Follow-Up Structure**
Three follow-ups (deeper, scope, uncertainty) is cognitively appropriate. This matches the "magic number 7±2" research—three is easy to hold in working memory while making a decision. The structure covers the essential epistemic questions.

**Q3: Confidence Levels**
Four levels (High/Medium/Low/Unknown) is appropriate satisficing. More granularity would be false precision. Consider adding a "Contested" confidence level distinct from "Low"—contested evidence with high-credence opposing views is different from simply weak evidence.

**Recommendation** (LOW): Consider "Contested" as fifth confidence level.

**Q4: Stopping Rules**
I haven't reviewed the stopping rules in detail, but the existence of multiple criteria (saturation, diminishing returns, scope coverage) is correct. Single-criterion stopping would be suboptimal.

**Specific Concerns**:
- None critical. The satisficing approach is well-implemented.

---

## Bates (Information Science)

### Assessment: APPROVE with MEDIUM modifications

**Q1: Vocabulary Bridge**
The vocabulary expansion should be MORE transparent. Users need to see:
- Original query terms
- Expanded terms used
- Which expansions matched

Currently `vocabulary_used` is in the response but may not be prominently displayed.

**Recommendation** (MEDIUM): Ensure frontend displays vocabulary expansions prominently.

**Q2: Evidence Item Display**
Top 10 is reasonable. The fields (credence, source_depth, causal flags) provide good information scent. Consider adding:
- **Recency** (publication year)
- **Citation count** (if available)

**Q3: Contested Evidence Section**
This is excellent berry-picking support. Showing both sides with reasons for disagreement helps researchers navigate controversy efficiently.

**Q4: Follow-Up Query URLs**
Clickable follow-ups with pre-filled parameters is exactly right. This reduces cognitive overhead and supports exploratory search behavior.

**Specific Concerns**:
- `frontend/evidence-explorer.html`: Need to verify vocabulary expansion display.
- Missing: Faceted navigation for filtering by source depth, causal tier, etc.

**Recommendation** (MEDIUM): Add faceted filtering to evidence explorer.

---

## Kaplan (Domain Expert - Environmental Psychology)

### Assessment: APPROVE with HIGH modifications

**Q1: Neuroarchitecture Patterns**
The patterns are good but incomplete:
- Missing: `green building`, `WELL certification`, `LEED`, `biophilic design`
- Missing: `daylighting`, `glare`, `view quality`, `visual access`
- Missing: `thermal comfort`, `acoustic comfort`, `indoor air quality`

**Recommendation** (HIGH): Expand neuroarchitecture vocabulary significantly.

**Q2: Outcome Taxonomy**
The fallback is missing several key outcomes:
- `cog.creativity` (creative thinking)
- `behav.collaboration` (teamwork, communication)
- `physio.circadian` (circadian rhythm measures)
- `affect.satisfaction` (job/space satisfaction)

**Recommendation** (HIGH): Expand fallback outcomes.

**Q3: Domain Confounders**
Good list but missing:
- `occupant density` (crowding effects)
- `control/autonomy` (ability to adjust environment)
- `work type` (knowledge work vs routine tasks)
- `prior exposure` (habituation effects)

**Recommendation** (MEDIUM): Add domain confounders.

**Q4: ART/Prospect-Refuge Detection**
YES. The system should explicitly detect:
- ART components: "being away", "fascination", "extent", "compatibility"
- Prospect-refuge: "prospect", "refuge", "mystery", "complexity"
- Stress Recovery Theory: "Ulrich", "affective response"

**Recommendation** (HIGH): Add theoretical framework detection.

**Specific Concerns**:
- `src/services/causal_classifier.py:208-230`: Neuroarchitecture patterns need significant expansion.
- `src/services/reporting.py:98-101`: Fallback outcomes incomplete.

---

## Lamport (Formal Methods)

### Assessment: MODIFY (MEDIUM priority)

**Q1: State Consistency**
I see no explicit consistency model. The web of belief can be mutated during operations. Questions:
- What happens if a query is running while beliefs are being added?
- Is there read-write locking?
- What's the transaction boundary?

**Recommendation** (MEDIUM): Document consistency model. Consider copy-on-read for queries or explicit locking.

**Q2: Specification**
The JSON schemas are syntactically precise but lack semantic invariants. For example:
- What makes a belief_id valid?
- Can credence exceed 1.0?
- What's the relationship between contested flag and credence?

**Recommendation** (MEDIUM): Add semantic constraints to schemas or document invariants separately.

**Q3: Invariants**
Not documented. Key invariants should include:
- Belief IDs are unique
- Credence values in [0, 1]
- Source_depth is from enumerated set
- Paper_ids reference existing papers

**Recommendation** (HIGH): Document and enforce invariants.

---

## Liskov (Software Design)

### Assessment: APPROVE with LOW modifications

**Q1: Abstraction Boundaries**
The service boundaries are reasonably clean:
- `query_parser` → produces `ParseResult`
- `query_response` → consumes `ParseResult`, produces `QueryResponse`
- `web_of_belief` → data layer

Minor concern: `QueryResponseGenerator` reaches into `WebOfBelief.beliefs` directly rather than through an interface.

**Recommendation** (LOW): Consider adding query methods to WebOfBelief rather than direct dict access.

**Q2: Substitutability**
Components are reasonably substitutable. The use of dataclasses for data transfer is good. Services depend on interfaces (WebOfBelief API) not implementations.

**Q3: Type Safety**
Type hints are comprehensive. Good use of Optional, List, Dict. Consider using TypedDict for dictionary structures or Pydantic models consistently.

**Specific Concerns**:
- Some functions return `Dict[str, Any]` which loses type information.

---

## Brooks (Architecture)

### Assessment: APPROVE

**Q1: Conceptual Integrity**
The system has strong conceptual integrity around the Quinean metaphor. The "web of belief" is a coherent organizing principle. The extraction-to-web-to-query pipeline is clear.

**Q2: Essential vs Accidental Complexity**
Most complexity appears essential:
- Causal classification requires linguistic analysis (essential)
- Contested evidence requires direction detection (essential)
- Scope conditions require domain knowledge (essential)

Some accidental complexity:
- Multiple pattern lists could be consolidated
- Test fixtures are repetitive

**Q3: Second System Effect**
No obvious over-engineering. The three-tier (not four-tier) decision shows restraint. The follow-up structure (exactly 3) shows design discipline.

---

## Parnas (Module Design)

### Assessment: APPROVE with MEDIUM modifications

**Q1: Information Hiding**
Modules mostly hide implementation well. Concerns:
- `CausalClassification` exposes `matched_patterns` which is implementation detail
- `QueryResponse` has many fields that may not all be needed by consumers

**Recommendation** (LOW): Consider response profiles (minimal, standard, detailed).

**Q2: Secret Ownership**
Good secret ownership:
- Causal patterns owned by `causal_classifier.py`
- Disagreement detection owned by `query_response.py`
- Confounder keywords owned by `reporting.py`

Concern: Some keyword lists are duplicated (causal keywords appear in multiple files).

**Recommendation** (MEDIUM): Consolidate keyword lists into single source of truth.

**Q3: Documentation**
CLAUDE.md is excellent for AI agents but may not suit human developers. Missing:
- Architecture diagram
- Data flow diagram
- Decision log (why choices were made)

**Recommendation** (MEDIUM): Add visual documentation.

---

## Naur (Theory Building)

### Assessment: APPROVE with HIGH modifications

**Q1: Tacit Knowledge**
Significant tacit knowledge embedded:
- Why 0.5 credence threshold was replaced with directional opposition
- Why three tiers not four
- Why these specific neuroarchitecture patterns
- The Quinean commitment and what it means in practice

This knowledge exists in the expert panel review docs but is scattered.

**Recommendation** (HIGH): Create a "Theory of the System" document that captures the epistemological commitments and design rationale in one place.

**Q2: Theory Preservation**
The expert panel documents are valuable but:
- They're in `Post_Quinean Setup/` which suggests they're setup artifacts, not ongoing documentation
- They're dated, which is good, but they're not integrated into the main docs

**Recommendation** (HIGH): Integrate key decisions into persistent documentation. Create `docs/DESIGN_RATIONALE.md` that captures:
- Why Quinean not Bayesian
- Why three tiers
- Why directional opposition
- Why these patterns

---

## Summary of Recommendations

### CRITICAL (Must fix before production)
None identified.

### HIGH Priority
| Issue | Owner | Recommendation |
|-------|-------|----------------|
| Expand neuroarchitecture patterns | Kaplan | Add 20+ domain terms |
| Expand fallback outcomes | Kaplan | Add cog.creativity, behav.collaboration, physio.circadian |
| Add theoretical framework detection | Kaplan | ART, prospect-refuge, SRT |
| Document invariants | Lamport | Add to schemas or separate doc |
| Create Theory of the System doc | Naur | Consolidate rationale |
| Add capacity bridge type | Cartwright | New bridge warrant type |

### MEDIUM Priority
| Issue | Owner | Recommendation |
|-------|-------|----------------|
| Add implicit confounder control patterns | Pearl | "adjusted model", "Model 2" |
| Expand scope follow-up | Cartwright | Reference specific populations |
| Add measurement categories | Cartwright | Behavioral, temporal, objective |
| Vocabulary expansion display | Bates | Frontend prominence |
| Faceted filtering | Bates | Evidence explorer enhancement |
| Document consistency model | Lamport | Read-write behavior |
| Consolidate keyword lists | Parnas | Single source of truth |
| Visual documentation | Parnas | Architecture diagrams |

### LOW Priority
| Issue | Owner | Recommendation |
|-------|-------|----------------|
| Contested confidence level | Simon | Optional fifth level |
| Query methods on WebOfBelief | Liskov | Interface refinement |
| Response profiles | Parnas | Minimal/standard/detailed |

---

## Governance Assessment

### CLAUDE.md Review
- Comprehensive for AI agents
- Good decision automation preferences
- Missing: Human developer onboarding
- Missing: Contribution guidelines

### Test Coverage Assessment
- 238+ tests is substantial
- Missing: Integration tests for full pipeline
- Missing: Performance tests
- Missing: Chaos/resilience tests

### Security Assessment
- No obvious injection risks in current code
- Credential handling appears absent (good for research tool)
- Missing: Input validation documentation

---

## Final Verdict

**Overall Assessment**: APPROVE for research use

**Not Ready For**:
- Production deployment to general users
- Automated decision-making without human review

**Ready For**:
- Internal CNFA research use
- Supervised graduate student use
- Expert review and iteration

**Next Sprint Priorities**:
1. Expand neuroarchitecture vocabulary (Kaplan items)
2. Document invariants and consistency model (Lamport items)
3. Create Theory of the System document (Naur item)
4. Add capacity bridge type (Cartwright item)
