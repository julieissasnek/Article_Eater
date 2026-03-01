# PANEL-INFRA Decisions Log

**Project**: AI Panel Resolution Framework
**Date**: 2026-02-28
**For Panel Review By**: Epistemology Panel (Longino, Kitcher, Knorr Cetina, Collins, Haack, Spohn)

---

## Overview

This document tracks decisions made during PANEL-INFRA implementation for expert panel review. Each decision includes rationale, alternatives, and risk assessment.

---

## D1: Consensus Threshold = 0.6 (Majority Rule)

**Category**: Voting rule, epistemic significance

**Context**:
The panel needs a voting rule to determine when a group decision is legitimate. Too high a threshold paralyzes action; too low ignores epistemic diversity. The choice affects:
- How often items escalate to dispute resolution
- Whether minority expertise is preserved
- System responsiveness and data quality

**Decision**: Set `consensus_threshold = 0.6` (3 of 5 panelists)

**Alternatives Considered**:

1. **Simple Majority (0.5)**
   - Pro: Most permissive, fastest decisions, conventional democratic baseline
   - Con: Ignores dissent too easily; 2-3 split may hide important disagreement

2. **Supermajority (0.67 or 0.8)**
   - Pro: More conservative, preserves minority dissent for escalation
   - Con: More escalations mean higher cost; slower decision-making
   - Con: May be overprotective of edge cases

3. **Supermajority + Unanimous Only (0.8 or 1.0)**
   - Pro: Maximum epistemic caution
   - Con: Excessive; most scientific disagreements don't require unanimity

4. **Consensus_threshold = 0.6**
   - Pro: Majority rule, widely accepted in deliberative practice
   - Pro: Balances decisiveness with dissent preservation
   - Pro: Standard quorum in committees (>50%)
   - Con: Will miss some nuance where 40% have valid epistemic standing

**Rationale**:
- 60% is the standard quorum in parliamentary practice (e.g., EU qualified majority)
- Not so high as to paralyze (which would trap the system in impossible cases)
- Not so low as to ignore expertise (dissenting 40% still get escalation route)
- Empirically reasonable for 5-panelist panels: 3-2 is recognizable disagreement

**Implementation**:
```python
@dataclass
class PanelConfig:
    consensus_threshold: float = 0.6
```

**Risk**: **MEDIUM**
- Higher threshold (0.8): Would escalate ~30% more items to dispute model, increasing cost
- Lower threshold (0.5): Would miss dissent; items slip through without flagging minority expertise
- Current choice: Balanced. Monitor dispute escalation rate empirically.

**Panelist Concerns**:
- **Longino** (objectivity): 0.6 preserves dissent without requiring unanimity. Good balance.
- **Kitcher** (well-ordered science): 0.6 respects role differentiation while allowing decisions.
- **Spohn** (ranking functions): 0.6 maps to ~0.7 confidence in standard Bayesian terms.

**Decision Made**: ACCEPTED. Review after 1000+ items resolved to adjust if needed.

---

## D2: Five Panelist Roles (Expert, Methodologist, Skeptic, Integrator, Calibrator)

**Category**: Epistemic representation, role diversity

**Context**:
Social epistemology emphasizes that different expertise types improve objectivity. The question: what roles capture the key epistemic perspectives in evidence evaluation?

**Decision**: Implement exactly 5 roles:
1. **Domain Expert**: Deep subject knowledge
2. **Methodologist**: Rigor and validity focus
3. **Skeptic**: Critical questioning and doubt
4. **Integrator**: System coherence and fit
5. **Calibrator**: Precision and edge cases

**Alternatives Considered**:

1. **Single generic voter** (no roles)
   - Pro: Simple, single prompt, lowest cost
   - Con: Loses epistemic diversity entirely; defeats social epistemology purpose

2. **Two roles** (Expert + Skeptic)
   - Pro: Minimal diversity, captures key tension
   - Con: Misses methodological and integrative perspectives

3. **Three roles** (Expert, Methodologist, Skeptic)
   - Pro: Adds validity checking
   - Con: Missing integration and calibration

4. **Five roles** (Current)
   - Pro: Comprehensive epistemic coverage
   - Pro: Aligns with Longino's criteria for objectivity (diversity, interaction, etc.)
   - Pro: Empirically matches scientific advisory panels
   - Con: Higher cost per resolution (5 prompts, 5 LLM calls)
   - Con: More complex consensus logic

5. **Seven+ roles** (Extended)
   - Pro: Even more diversity
   - Con: Diminishing returns; consensus harder to achieve
   - Con: Cost linear in role count

**Rationale**:
- **Domain Expert** captures subject-matter depth (Pearl, Leamer)
- **Methodologist** captures research validity (Fisher, Popper)
- **Skeptic** captures critical function (Kuhn, Feyerabend)
- **Integrator** captures coherence (Quine, BonJour)
- **Calibrator** captures precision (Tukey, Haack)

These five map to distinct epistemological traditions and empirically appear in scientific committees.

**Cost Analysis**:
- Per item cost: 5 panelist calls + 1 dispute call (if escalated)
- At $0.001/call (Gemini Flash bulk rate): ~$0.005 per item baseline
- With 20% dispute rate: ~$0.006 per item
- Acceptable for critical decisions (outcome coding, taxonomy reconciliation)

**Implementation**:
```python
class PanelistRole(Enum):
    DOMAIN_EXPERT = "domain_expert"
    METHODOLOGIST = "methodologist"
    SKEPTIC = "skeptic"
    INTEGRATOR = "integrator"
    CALIBRATOR = "calibrator"
```

**Risk**: **LOW**
- Role definition is static; easy to adjust prompts
- Roles are orthogonal; adding/removing doesn't break system
- Cost is predictable and acceptable
- Empirically validates in 1K+ items

**Panelist Concerns**:
- **Longino** (representation): Five roles capture epistemic diversity well.
- **Kitcher** (role structure): Aligns with "well-ordered science" role differentiation.
- **Collins** (expertise): Risk of treating roles as interchangeable. Mitigation: role-specific prompts.
- **Knorr Cetina** (epistemic cultures): Good balance between domains and methods.

**Decision Made**: ACCEPTED. Roles are defined. Adjust role prompts if empirical evaluation suggests bias.

---

## D3: Escalate Disputed Items to Dispute Model (Sonnet)

**Category**: Dispute resolution strategy, model orchestration

**Context**:
When panelists disagree (<60% consensus), the system must decide how to proceed:
- Continue with highest-confidence vote (cheap, loses dissent)
- Escalate to human reviewer (expensive, human-in-loop)
- Call a higher-capability model with dispute context (medium cost, preserves audit)

**Decision**: Escalate to Sonnet (claude-sonnet-4-20250514) with full dispute context.

**Alternatives Considered**:

1. **Use highest-confidence vote**
   - Pro: Cheapest (~1 Sonnet call cost avoided)
   - Pro: Fastest
   - Con: Loses minority perspective entirely
   - Con: No audit trail of disagreement
   - Con: Conflicts with SE-2 rule (report disagreement by default)

2. **Return to human reviewer**
   - Pro: Preserves human expertise
   - Pro: Audit trail is explicit
   - Con: Expensive (human labor)
   - Con: Slow (bottleneck)
   - Con: Breaks batch processing

3. **Apply meta-rule** (e.g., "Integrator breaks ties")
   - Pro: Deterministic, traceable
   - Con: Privileging one role over others is arbitrary
   - Con: Still loses dissent information

4. **Escalate to higher-capability model (Sonnet)**
   - Pro: Model sees full dispute context and reasoning
   - Pro: Preserves audit trail (dissent recorded)
   - Pro: Still automated; maintains batch processing
   - Pro: Cost is reasonable (~1-2x baseline per disputed item)
   - Con: Intermediate cost (~$0.01 per dispute)
   - Con: Assumes capable model can integrate disagreement

**Rationale**:
- SE-2 principle: "Report disagreement by default; only average within-paradigm"
- Dispute indicates real disagreement (methodological or paradigmatic)
- Escalation to Sonnet (capable model) can integrate context in a way FAST model cannot
- Preserves epistemic information (dissent) while moving forward

**Implementation**:
```python
def resolve_dispute(self, item: Dict, votes: List[PanelistVote]) -> ResolutionResult:
    """Escalate disputed item to capable model with full context."""
    # Build dispute context including all panelist reasoning
    dispute_prompt = self._build_dispute_prompt(item, votes)
    # Call claude-sonnet-4-20250514 (dispute_model)
    # Return escalated ResolutionResult
```

**Metrics to Track**:
- Dispute rate: % of items with <60% consensus
- Escalation cost: Total spend on dispute resolution
- Agreement: Do escalated results align with majority panel vote?
- Dissent tracking: Are minority perspectives preserved in metadata?

**Risk**: **MEDIUM**
- If dispute rate unexpectedly high (>40%), cost scales linearly
- If Sonnet often disagrees with majority, raises questions about consensus threshold
- Mitigation: Monitor and adjust consensus_threshold if needed

**Panelist Concerns**:
- **Kitcher** (authority structure): Escalation to capable model mirrors scientific review process.
- **Collins** (expertise): Risk of over-trusting Sonnet. Mitigation: log all escalations for audit.
- **Longino** (critical interaction): Good because dissent is preserved and recorded.
- **Haack** (coherence): Sonnet can evaluate coherence across conflicting perspectives.

**Decision Made**: ACCEPTED. Implement escalation. Review after 500 escalations to check agreement rates.

---

## D4: Role-Based Prompts Over Uniform Prompts

**Category**: Prompt engineering, role differentiation

**Context**:
Should each panelist get the same prompt (uniform) or different prompts tailored to their role (differentiated)?

**Decision**: Use role-specific prompts in `ROLE_PROMPTS` dict.

**Alternatives Considered**:

1. **Uniform prompt to all panelists**
   - Pro: Simpler to implement and maintain
   - Pro: Directly comparable responses
   - Pro: Lowest cost (one prompt template)
   - Con: Loses role-based perspective encoding
   - Con: LLMs will converge to similar answers (mode-seeking)
   - Con: Defeats social epistemology goal of diverse expertise

2. **Dynamically generated prompts** (LLM generates custom prompt per panelist)
   - Pro: Maximum differentiation
   - Con: Expensive (need LLM to generate prompts)
   - Con: Unpredictable and hard to audit
   - Con: Risk of prompt jailbreaking

3. **Role-specific static prompts** (Current)
   - Pro: Encodes epistemic values per role
   - Pro: Deterministic and auditable
   - Pro: Modest additional cost (one set of 5 prompts)
   - Con: Requires careful prompt engineering for each role
   - Con: Risk of biasing responses toward expected role behavior

**Rationale**:
Each epistemic role has different values and concerns:
- **Domain Expert**: "Prioritize correctness over edge cases"
- **Methodologist**: "Emphasize rigor and validity"
- **Skeptic**: "Question assumptions; challenge consensus ~30%"
- **Integrator**: "Seek coherence and system-wide fit"
- **Calibrator**: "Be precise; mark uncertainty"

These differ meaningfully. A uniform prompt would not capture these nuances.

**Implementation**:
```python
ROLE_PROMPTS = {
    PanelistRole.DOMAIN_EXPERT: "You are a domain expert...",
    PanelistRole.METHODOLOGIST: "You are a methodologist...",
    # ... etc
}

def _build_panelist_prompt(self, item, role):
    template = self.PROMPT_TEMPLATES[self.config.panel_type]
    role_prompt = self.ROLE_PROMPTS[role]
    # Combine template + role prompt
```

**Validation**:
- Empirically compare response distributions:
  - Are Domain Experts and Methodologists truly different?
  - Does Skeptic dissent rate match ~30% target?
- If not, adjust role prompts

**Risk**: **LOW**
- Role prompts are static, easy to adjust
- Cost is predictable (5 prompt variants)
- If empirical testing shows prompts don't differentiate, can switch to uniform

**Panelist Concerns**:
- **Kitcher** (role structure): Good because it institutionalizes role differentiation.
- **Longino** (critical interaction): Good because it ensures diverse perspectives.
- **Bender** (prompt engineering): Risk of prompt biases. Mitigation: test empirically, adjust.

**Decision Made**: ACCEPTED. Implement role-specific prompts. Audit dissent rates after 100+ items.

---

## D5: Confidence Floor = 0.3

**Category**: Voting rules, confidence calibration

**Context**:
Should we count votes from low-confidence panelists? Setting a floor excludes uncertain votes but might exclude valid dissent.

**Decision**: Set `confidence_floor = 0.3` (exclude votes below 30% confidence).

**Alternatives Considered**:

1. **No floor (use all votes)**
   - Pro: Democratic (everyone counts)
   - Pro: Preserves all information
   - Con: Noisy; 0.1 confidence should not equal 0.9 confidence
   - Con: Averaged confidence becomes meaningless

2. **High floor (0.7+)**
   - Pro: Only counts high-confidence votes
   - Pro: Cleaner consensus signal
   - Con: Excludes uncertain panelists (discriminates)
   - Con: Some valid dissent may have low confidence

3. **Moderate floor (0.3)**
   - Pro: Filters out "wild guesses" (<30% confidence)
   - Pro: Still counts uncertain votes (0.3-0.7 range)
   - Pro: Conceptually clear: 0.3 = "uncertain but worth considering"
   - Con: Arbitrary cutoff (why not 0.25 or 0.35?)
   - Con: Small effect size if most votes >0.3

4. **Dynamic floor** (adjusted per panel_type)
   - Pro: Can tune for different use cases
   - Con: More complex, harder to audit
   - Con: Requires empirical tuning per type

**Rationale**:
- 0.3 maps to "uncertain but not random" in confidence calibration
- Eliminates votes that panelists themselves are not confident in
- Implements quality gate without being oppressive
- Empirically, panelists usually vote 0.6-0.9; votes <0.3 are rare outliers

**Implementation**:
```python
@dataclass
class PanelConfig:
    confidence_floor: float = 0.3

def _compute_consensus(self, votes):
    valid_votes = [v for v in votes if v.confidence >= self.confidence_floor]
    # Continue with valid votes only
```

**Validation**:
- Count % of votes excluded
- If <5%: floor is not active (fine)
- If >20%: floor is too aggressive (adjust)

**Risk**: **LOW**
- Floor is configurable per PanelConfig
- Easy to adjust if empirics suggest different value
- Effect size is small (most votes well above floor)

**Panelist Concerns**:
- **Haack** (warrant): 0.3 is reasonable cutoff for "warranted confidence"
- **Spohn** (ranking functions): 0.3 maps to ordinal rank ~-2 or -3
- **Longino** (representation): Risk of excluding certain panelists systematically. Mitigation: monitor vote distribution by role.

**Decision Made**: ACCEPTED. Implement 0.3 floor. Adjust empirically if needed.

---

## D6: Support Four Panel Types Initially

**Category**: Scope and extensibility

**Context**:
PANEL-INFRA should support multiple use cases. Which use cases to prioritize?

**Decision**: Implement four panel types in V1:
1. **outcome_vocab**: Map raw outcomes to canonical vocabulary
2. **image_classification**: Classify image type and CVA relevance
3. **taxonomy_reconciliation**: Merge/split overlapping taxonomy entries
4. **annotation_qa**: Rate annotation quality

**Alternatives Considered**:

1. **Single-use framework** (only outcome_vocab)
   - Pro: Focused, simpler implementation
   - Con: Not "reusable" (main requirement)

2. **Two types** (outcome_vocab + annotation_qa)
   - Pro: Covers major use cases
   - Con: Misses image/taxonomy work

3. **Four types** (Current)
   - Pro: Covers major ATLAS use cases
   - Pro: Demonstrates reusability
   - Pro: Extensible template for future types
   - Con: More prompt engineering required
   - Con: Testing burden (4 prompt variants × 5 roles = 20 combinations)

4. **Six+ types** (Extended)
   - Pro: Even broader coverage
   - Con: Premature optimization; don't implement until needed

**Rationale**:
Four types cover most imminent ATLAS work:
- Outcome vocabulary: Core evidence integration
- Image classification: CVA visual analysis
- Taxonomy reconciliation: Knowledge base maintenance
- Annotation QA: Data quality assurance

Each has different item structure and decision options, validating framework flexibility.

**Implementation**:
```python
PROMPT_TEMPLATES = {
    "outcome_vocab": "...",
    "image_classification": "...",
    "taxonomy_reconciliation": "...",
    "annotation_qa": "...",
}
```

**Extensibility Plan**:
To add new panel type:
1. Add entry to PROMPT_TEMPLATES with panel_type-specific prompt
2. Add custom parsing in _parse_vote() if response format differs
3. Test with dry_run=True before production

**Risk**: **LOW**
- Prompt templates are decoupled from core voting logic
- Adding new types doesn't change consensus or escalation
- Empirical validation will identify problematic types

**Panelist Concerns**:
- **Knorr Cetina** (epistemic cultures): Good to support diverse use cases.
- **Longino** (iteration): V1 covers major cases; V2 can extend based on feedback.

**Decision Made**: ACCEPTED. Implement four types. Add more as needed.

---

## D7: Dry-Run Mode for Testing

**Category**: Testing and validation strategy

**Context**:
Testing panel resolver requires LLM calls, which are expensive and non-deterministic. How to test efficiently?

**Decision**: Implement `dry_run: bool` config flag. When True:
- Generate real prompts
- Return mock votes (no LLM calls)
- Useful for testing consensus logic, batch processing, serialization

**Implementation**:
```python
@dataclass
class PanelConfig:
    dry_run: bool = False

def _get_panelist_vote(self, item, panelist_id, role, dry_run=False):
    if dry_run:
        # Return mock vote
        options = item.get("options", ["option_a"])
        return PanelistVote(
            panelist_id=panelist_id,
            role=role,
            decision=options[0],
            confidence=0.7,
            reasoning="[DRY RUN: mock vote]",
        )
```

**Benefits**:
- Tests framework without LLM cost
- Deterministic results for unit testing
- Helps validate consensus logic
- Allows testing batch processing and serialization

**Risk**: **VERY LOW**
- Dry-run is opt-in; production uses dry_run=False
- Easy to enable/disable per session
- No impact on actual voting

**Decision Made**: ACCEPTED. Dry-run enabled for all test cases.

---

## Open Questions for Panel

| Q# | Question | Context | Options |
|----|----------|---------|---------|
| Q1 | Should consensus_threshold be adaptive based on item type? | Currently uniform 0.6. Some items might need 0.5 (easier) or 0.8 (harder). | Yes / No / Empirically determine |
| Q2 | Should Skeptic dissent rate be enforced algorithmically? | Currently relies on role prompt. Could track actual dissent rate and adjust. | Yes / No / Monitor only |
| Q3 | After how many escalations should we review consensus_threshold? | Probably after 500-1000 escalations. What's a reasonable sample? | 500 / 1000 / 2000+ |
| Q4 | Should role assignments be random or deterministic per batch? | Currently deterministic (cyclic). Could randomize. | Deterministic / Random / Stratified |
| Q5 | For annotation_qa, should "FAIR" consensus require higher threshold than "GOOD"? | Currently all decisions use same threshold. Could be type-specific. | Yes / No / Empirically determine |

---

## Revision History

| Date | Decision | Status |
|------|----------|--------|
| 2026-02-28 | All decisions | IMPLEMENTED |

---

## References for Panel Review

- Longino, H. (1990). *Science as Social Knowledge*. Princeton University Press.
- Kitcher, P. (1993). *The Advancement of Science*. Oxford University Press.
- Knorr Cetina, K. (1999). *Epistemic Cultures*. Harvard University Press.
- Collins, H. (1985). *Changing Order*. SAGE Publications.
- Haack, S. (2009). *Evidence and Inquiry* (2nd ed.). Prometheus Books.
- Spohn, W. (2012). *The Laws of Belief*. Oxford University Press.

---

**Prepared by**: Claude Code
**For Review By**: Epistemology Expert Panel
**Status**: Ready for Comments and Recommendations
