# Panel Consultation: Formal Epistemic Calculus

**Panel ID**: P-ARCH4-EPISTEMIC-CALCULUS
**Date**: 2026-02-12
**Convener**: Claude Code for Professor David Kirsh
**Purpose**: Develop AND vet implementation plan for ARCH-4

---

## Panel Composition

### Core Theorists (Constructed Voices)

| Panelist | Expertise | Why Included |
|----------|-----------|--------------|
| **Wolfgang Spohn** | Ranking theory, belief revision | Inventor of the ranking formalism we're adopting |
| **John Pollock** | Defeasible reasoning, epistemology | Inventor of defeater taxonomy and warrant theory |
| **Susan Haack** | Foundherentism | The epistemology we claim to implement |
| **Judea Pearl** | Causal inference, do-calculus | Must ensure epistemic-causal bridge is coherent |

### Implementation Experts (Constructed Voices)

| Panelist | Expertise | Why Included |
|----------|-----------|--------------|
| **Leslie Lamport** | TLA+, formal specification | Will verify our formal spec is rigorous |
| **Barbara Liskov** | Software architecture, ADTs | Will ensure clean implementation |
| **Robin Milner** | Type theory, process algebra | Formal semantics perspective |

### Domain Integration

| Panelist | Expertise | Why Included |
|----------|-----------|--------------|
| **Clark Glymour** | Formal epistemology, causation | Bridges philosophy and computation |
| **Henry Kyburg** | Probability, epistemology | Alternative perspective on uncertainty |

---

## Materials Provided to Panel

1. **Current system state**: `src/services/web_of_belief.py` (1900 lines)
2. **Draft specification**: `docs/EPISTEMIC_CALCULUS_SPEC_2026-02-12.md`
3. **Panel critique**: `docs/PANEL_RUTHLESS_REVIEW_2026-02-12.md` (the 4/10 score)
4. **Recent fixes**: Defeater search, widened uncertainty, removed level weights

---

## Panel Process

### Round 1: Individual Critique of Draft Spec

Each panelist reviews the draft specification and provides:
1. What's correct and should be kept
2. What's wrong and must be fixed
3. What's missing and must be added
4. Specific implementation recommendations

### Round 2: Cross-Panelist Dialogue

Panelists respond to each other's critiques. Key tensions:
- Spohn vs. Pollock: How do ranks and defeaters interact?
- Pearl vs. Haack: How does epistemic justification constrain causal claims?
- Lamport vs. Liskov: Formal spec vs. practical architecture

### Round 3: Synthesis

Unified implementation plan with panel consensus or documented dissent.

---

## ROUND 1: INDIVIDUAL RESPONSES

### Wolfgang Spohn (Ranking Theory)

**On the draft specification**:

Your mapping of my ranking theory is partially correct but has significant issues.

**What's correct**:
1. Using ordinal ranks rather than cardinal probabilities — yes, this avoids false precision
2. The conditionalization rule you cite is correct
3. Recognizing that ranks represent *degrees of disbelief* (κ(B) = how firmly ¬B is held)

**What's wrong**:

1. **You've inverted the semantics**. In my theory, κ(B) = 0 means B is not disbelieved (it might be believed or suspended). You write "lower = more entrenched" but that's backwards. Lower rank means *less disbelieved*, not more believed. The belief/disbelief asymmetry is crucial.

   **Fix**: Define clearly:
   - κ(B) = rank of B = degree of disbelief in B
   - B is believed iff κ(¬B) > 0 (the negation is disbelieved)
   - B is disbelieved iff κ(B) > 0
   - B is suspended iff κ(B) = κ(¬B) = 0

2. **You haven't addressed the ranking function's domain**. Ranks apply to *propositions*, not to what you call "beliefs." A belief in your system is a complex object with content, source, scope, etc. The rank should apply to the propositional content, not the belief object.

   **Fix**: Separate:
   - `Belief` = the complex object (content, source, scope, evidence)
   - `rank(content)` = the epistemic status of the proposition

3. **Conditional ranks need care**. Your formula κ(B|E) = κ(B∧E) - κ(E) is correct, but you haven't specified how to compute κ(B∧E) for complex beliefs. Do you have a language for combining propositions?

**What's missing**:

1. **The regularity assumption**. For ranks to work, you need: κ(⊥) = ∞ and κ(⊤) = 0. Have you defined your logical language?

2. **Iterated revision**. My theory handles sequences of evidence. Your `Credence.update()` is a single step. How do you track revision history?

3. **Reasons and ranking**. I've written about how ranks connect to reasons (see my 2012 book, Chapter 6). Your defeater framework (from Pollock) needs to integrate with ranks. Specifically: a reason for B should *lower* κ(B); a defeater should *raise* it.

**Implementation recommendation**:

Start with a simplified ranking:
```python
class RankedProposition:
    content: str  # The propositional content
    rank: int     # κ(content) — degree of disbelief, 0 = not disbelieved
    neg_rank: int # κ(¬content) — if > 0, content is believed
```

Then define:
```python
def is_believed(self) -> bool:
    return self.neg_rank > 0

def is_disbelieved(self) -> bool:
    return self.rank > 0

def belief_strength(self) -> int:
    """How firmly believed (if believed at all)."""
    return self.neg_rank if self.is_believed() else 0
```

**Verdict**: Good start, but you need to get the semantics right before coding.

---

### John Pollock (Defeasible Reasoning)

**On the draft specification**:

I'm pleased you're taking defeaters seriously. Your recent implementation (`find_defeaters_for_belief`) is a step in the right direction. But you've conflated several distinct concepts.

**What's correct**:
1. The distinction between rebutting and undercutting defeaters — essential
2. Recognizing that warrant requires surviving defeat
3. The DEFEATER_INDICATORS you implemented catch real defeater language

**What's wrong**:

1. **Defeaters aren't just contradictions**. Your implementation searches for "contrary evidence." But an undercutting defeater doesn't contradict the conclusion — it attacks the inference.

   Example:
   - Belief: "This object looks red, so it is red"
   - Undercutter: "The lighting is red"

   The undercutter doesn't say the object isn't red. It says the inference from appearance to reality is blocked.

   **Fix**: Classify defeaters by what they attack:
   - Rebutters: Attack conclusion (opposite finding)
   - Undercutters: Attack inference (methodological critique, scope violation)

2. **You're missing defeater defeaters**. Defeaters can themselves be defeated. Your system does one-level defeat. But:
   - A rebuts B
   - C rebuts A
   - Therefore B is reinstated

   This is called "reinstatement" and it's crucial for handling conflicting evidence properly.

   **Fix**: Implement recursive defeat checking:
   ```python
   def is_warranted(belief, depth=0, seen=None):
       if seen is None: seen = set()
       if belief.id in seen: return False  # Circular
       seen.add(belief.id)

       # Get prima facie support
       supporters = get_supporters(belief)
       if not supporters and not is_observational(belief):
           return False  # No support, not grounded

       # Check for undefeated defeaters
       defeaters = get_defeaters(belief)
       for d in defeaters:
           if is_warranted(d, depth+1, seen.copy()):
               # Defeater is warranted, so belief is defeated
               # Unless the defeater is itself defeated...
               defeater_defeaters = get_defeaters(d)
               reinstated = any(is_warranted(dd, depth+2, seen.copy())
                               for dd in defeater_defeaters)
               if not reinstated:
                   return False

       return True
   ```

3. **Degrees of defeat are missing**. Not all defeaters are equal. A methodological critique from a Nature paper defeats more strongly than one from a preprint. Your ranks (from Spohn) should integrate with defeat strength.

**What's missing**:

1. **Inference rules**. You have support/contradict constraints, but not explicit inference rules. My OSCAR system had explicit rules like:
   - Perception: If it appears that P, then defeasibly P
   - Induction: If all observed Fs are Gs, then defeasibly all Fs are Gs
   - Statistical syllogism: If most Fs are Gs and X is F, then defeasibly X is G

   Your domain (environmental psychology) should have domain-specific inference rules.

2. **Priority ordering**. When two rules conflict, which wins? You need:
   - Specificity (more specific beats less specific)
   - Recency (later evidence beats earlier, sometimes)
   - Reliability (better methods beat worse)

**Implementation recommendation**:

Extend your constraint types:
```python
class ConstraintType(Enum):
    SUPPORTS = "supports"           # Prima facie reason
    EXPLAINS = "explains"           # Explanatory support
    REBUTS = "rebuts"              # Attacks conclusion
    UNDERCUTS = "undercuts"        # Attacks inference
    REINSTATES = "reinstates"      # Defeats a defeater
```

Add defeat strength:
```python
@dataclass
class DefeatRelation:
    defeater_id: str
    target_id: str
    defeat_type: Literal["rebuts", "undercuts"]
    strength: int  # Integrates with Spohn ranks
    attack_point: str  # What specifically is attacked
```

**Verdict**: You've made a good start with defeater search. Now formalize it.

---

### Susan Haack (Foundherentism)

**On the draft specification**:

I appreciate that you've removed the crypto-foundationalist level weights. That was the right move. But I'm concerned that adding Spohn's ranking theory might reintroduce hierarchy through the back door.

**What's correct**:
1. Removing fixed weights for epistemic levels — good
2. Recognizing that entrenchment emerges from structure — correct
3. Adding defeater search — addresses the one-sidedness I worried about

**What's wrong**:

1. **Spohn's ranks aren't foundherentist**. Ranking theory is a form of *probabilism* (qualitative probability). It doesn't capture the crossword puzzle nature of foundherentism where clues (experience) AND entries (beliefs) mutually constrain.

   In my view:
   - Beliefs support each other (coherence) AND
   - Experience provides independent constraint (foundational element)

   Spohn's ranks only capture *degrees* of belief, not the *structure* of justification.

   **Fix**: Keep my original metaphor. The rank should emerge from:
   - How well the belief fits with others (coherence)
   - How directly it connects to experience (grounding)
   - Both together, not one metric

2. **You've lost the crossword structure**. Your web has beliefs and constraints. But in a crossword:
   - CLUES constrain entries (experience → belief)
   - ENTRIES constrain each other (belief → belief)
   - A good solution satisfies both

   Your system doesn't distinguish these. All constraints are belief→belief.

   **Fix**: Add explicit experiential grounding:
   ```python
   class Belief:
       # ... existing fields ...
       experiential_basis: List[ExperientialClaim]  # The "clues"

   class ExperientialClaim:
       source: str  # Paper, observation, etc.
       directness: float  # How directly observed vs. inferred
       content: str
   ```

3. **Coherence needs explication**. You compute "coherence contribution" but what IS coherence? I distinguish:
   - Consistency (no contradictions)
   - Connectedness (beliefs relate to each other)
   - Comprehensiveness (covers the domain)

   Your coherence seems to be just connectedness. That's not enough.

**What's missing**:

1. **The experiential constraint**. My foundherentism requires experience to play a special (but not foundational) role. Where is experience in your system? Papers aren't experience — they're reports of experience.

2. **Degrees of directness**. An observational belief (I saw X) differs from an inferential belief (X probably causes Y). This affects justification structure, not just level labels.

**Implementation recommendation**:

Don't fully adopt Spohn. Instead:
1. Keep ranks for degree of belief
2. Add explicit grounding metric (how connected to experience)
3. Compute entrenchment from BOTH coherence AND grounding
4. Make the crossword structure explicit

```python
def compute_justification(belief_id: str) -> JustificationStatus:
    coherence = compute_coherence_contribution(belief_id)  # Existing
    grounding = compute_experiential_grounding(belief_id)  # New

    # Foundherentist combination
    if grounding == 0 and coherence == 0:
        return JustificationStatus.UNJUSTIFIED
    elif grounding > 0 and coherence > 0:
        return JustificationStatus.WELL_JUSTIFIED  # Both support
    elif grounding > 0:
        return JustificationStatus.GROUNDED_ONLY  # Experience but isolated
    else:
        return JustificationStatus.COHERENT_ONLY  # Connected but floating
```

**Verdict**: Don't let formalization lose the philosophical substance.

---

### Judea Pearl (Causal Inference)

**On the draft specification**:

The epistemic-causal bridge section interests me. You propose:

> P(Y | do(X=x)) is trustworthy iff the BN edge X→Y is supported by warranted beliefs

This is in the right direction, but imprecise.

**What's correct**:
1. Separating epistemic confidence from causal computation
2. Recognizing that BN structure needs justification
3. Using warrant (not just credence) for structural claims

**What's wrong**:

1. **Trustworthiness isn't binary**. A causal effect estimate has *uncertainty* that should propagate from epistemic uncertainty. If you're 70% confident in edge X→Y, your causal estimate should reflect that.

   **Fix**: Define confidence-weighted causal inference:
   ```
   P(Y | do(X=x), confidence) = Σ_G P(Y | do(X=x), G) × P(G | beliefs)
   ```
   Where G ranges over possible graph structures and P(G | beliefs) comes from your epistemic layer.

2. **You conflate edge existence and edge strength**. The BN has two components:
   - Structure: Which edges exist (qualitative)
   - Parameters: CPT values (quantitative)

   Your epistemic layer currently only addresses structure. What about parameters?

3. **Identifiability depends on the whole graph**. Even if each edge is warranted, the causal effect might not be identifiable (confounders, selection bias). Your system doesn't check identifiability.

**What's missing**:

1. **Graph uncertainty**. The epistemic layer should output a *distribution* over graphs, not a single graph. This is Bayesian structure learning.

2. **Sensitivity analysis**. When edges are uncertain, how sensitive is the causal conclusion? I developed bounds for this.

3. **Transportability to new populations**. Even a well-supported effect might not transport. See my work with Bareinboim.

**Implementation recommendation**:

Add graph confidence layer:
```python
class GraphConfidence:
    """Epistemic confidence in BN structure."""

    def edge_confidence(self, source: str, target: str) -> float:
        """Confidence in edge existence, from warranted beliefs."""
        supporting = self.get_warranted_support(source, target)
        defeating = self.get_warranted_defeaters(source, target)
        return self.compute_net_confidence(supporting, defeating)

    def structure_confidence(self) -> float:
        """Confidence in overall graph structure."""
        return min(self.edge_confidence(e) for e in self.edges)

    def causal_effect_bounds(self, X: str, Y: str) -> Tuple[float, float]:
        """Bounds on P(Y|do(X)) given structural uncertainty."""
        # Implementation using partial identification theory
        pass
```

**Verdict**: Good direction. Make the epistemic→causal bridge quantitative.

---

### Leslie Lamport (Formal Specification)

**On the draft specification**:

You mention TLA+ for formal specification. Good. Let me tell you what a real specification requires.

**What's correct**:
1. Identifying invariants (groundedness, consistency, rank coherence)
2. Recognizing the need for provable properties
3. Attempting to define "correctness"

**What's wrong**:

1. **Your invariants are informal**. "Every warranted belief is supported by warranted beliefs" — what does "supported" mean precisely? This isn't a specification; it's a wish.

   **Fix**: Define formally. In TLA+:
   ```tla
   Warranted(b) ==
     \/ b.level = "observational"  \* Grounded
     \/ \E s \in Supporters(b):
          /\ Warranted(s)
          /\ ~\E d \in Defeaters(b):
               /\ Defeats(d, b)
               /\ Warranted(d)
   ```

2. **No state machine**. What are the states? What are the transitions? A specification defines:
   - State space (all possible web configurations)
   - Initial state (empty web or seed beliefs)
   - Actions (add belief, add constraint, revise, etc.)
   - Invariants (properties that hold in all reachable states)

3. **Termination not addressed**. Your coherence computation might not terminate. Warrant computation with reinstatement might cycle. You need progress guarantees.

**What's missing**:

1. **Safety properties**: What bad things never happen?
   - Inconsistency: No belief is both warranted and defeated
   - Circularity: No belief's warrant depends on itself

2. **Liveness properties**: What good things eventually happen?
   - If evidence E supports B, eventually rank(B) decreases
   - If defeater D defeats B, eventually B loses warrant

3. **Refinement relation**: How does the specification relate to the code?

**Implementation recommendation**:

Write actual TLA+ before coding:

```tla
---------------------------- MODULE EpistemicWeb ----------------------------
EXTENDS Naturals, FiniteSets

CONSTANTS Beliefs, MaxRank

VARIABLES
    ranks,        \* ranks[b] = rank of belief b
    constraints,  \* set of (source, target, type) tuples
    warranted     \* set of warranted beliefs

TypeInvariant ==
    /\ ranks \in [Beliefs -> 0..MaxRank]
    /\ constraints \subseteq (Beliefs \times Beliefs \times {"supports", "rebuts", "undercuts"})
    /\ warranted \subseteq Beliefs

Consistency ==
    \A b \in Beliefs: ~(b \in warranted /\ Rebutter(b) \in warranted)

Groundedness ==
    \A b \in warranted:
        b.level = "observational" \/
        \E s \in warranted: (s, b, "supports") \in constraints

\* ... more specification ...
=============================================================================
```

**Verdict**: No code until you have a real specification.

---

### Barbara Liskov (Software Architecture)

**On the draft specification**:

I see the theoretical ambitions. Now let me address practical architecture.

**What's correct**:
1. Wanting to separate concerns (ranking vs. defeat vs. warrant)
2. Recognizing the current god objects are problematic

**What's wrong**:

1. **The Belief class is still overloaded**. Your spec adds MORE to it (rank, neg_rank, experiential_basis). This is wrong. Decompose:

   ```python
   class PropositionalContent:
       """What the belief is about."""
       statement: str
       domain: Domain

   class EpistemicStatus:
       """Current epistemic standing."""
       rank: int
       neg_rank: int
       warrant_status: WarrantStatus

   class Provenance:
       """Where this came from."""
       sources: List[Source]
       grounding: List[ExperientialClaim]

   class Belief:
       """Composite: content + status + provenance."""
       id: str
       content: PropositionalContent
       status: EpistemicStatus
       provenance: Provenance
   ```

2. **Rank computation should be a separate service**. Don't embed Spohn's conditionalization in the Credence class. Make it a RankingService that takes the web state and returns ranks.

3. **Warrant computation should be separate too**. WarrantService that takes web + ranks and computes warrant.

**What's missing**:

1. **Clear interfaces**. What can each module see? What can it modify?

2. **Immutability where possible**. Ranks should be computed, not mutated in place.

3. **Event sourcing**. Instead of mutating state, record events: BeliefAdded, ConstraintAdded, EvidenceReceived. Compute current state from events. This gives you history for free.

**Implementation recommendation**:

```python
# services/ranking_service.py
class RankingService:
    """Computes Spohn ranks from web state."""

    def compute_ranks(self, web: WebOfBelief) -> Dict[str, RankPair]:
        """Pure function: web state → ranks."""
        pass

    def conditionalize(self,
                       current_ranks: Dict[str, RankPair],
                       evidence: Evidence,
                       firmness: int) -> Dict[str, RankPair]:
        """Spohn conditionalization."""
        pass

# services/warrant_service.py
class WarrantService:
    """Computes warrant status using Pollock's framework."""

    def compute_warrant(self,
                        web: WebOfBelief,
                        ranks: Dict[str, RankPair]) -> Set[str]:
        """Returns set of warranted belief IDs."""
        pass

    def get_defeat_chain(self, belief_id: str) -> DefeatChain:
        """Explain why a belief is/isn't warranted."""
        pass
```

**Verdict**: Decompose first, formalize second, implement third.

---

## ROUND 2: CROSS-PANELIST DIALOGUE

### Spohn → Pollock

**Spohn**: John, your defeaters need to integrate with ranks. I propose: a defeater D for belief B should *raise* κ(B) by the firmness of D. Specifically:

```
κ_new(B) = κ_old(B) + κ(¬D) if D rebuts B
κ_new(B) = κ_old(B) + κ(inference blocked) if D undercuts
```

**Pollock**: Wolfgang, I agree they should integrate, but your formulation misses reinstatement. If D defeats B, and E defeats D, then B should return to its original rank, not stay elevated. The defeat relation is non-monotonic.

**Spohn**: Hmm. Perhaps we need *conditional ranks* on the defeat structure:
```
κ(B | D undefeated) = κ(B) + defeat_strength(D)
κ(B | D defeated) = κ(B)
```

**Resolution**: Implement tiered rank computation:
1. Base rank from evidence (Spohn)
2. Defeat adjustment (Pollock)
3. Reinstatement check (recursive)

---

### Haack → Spohn

**Haack**: Wolfgang, I worry that ranks lose the structural information I care about. Two beliefs could have the same rank for very different reasons:
- Belief A: rank 2, well-grounded in experience, isolated
- Belief B: rank 2, poorly grounded, but highly coherent

Your ranks don't distinguish these. In my foundherentism, both grounding AND coherence matter.

**Spohn**: Susan, ranks CAN encode both. Define composite rank:
```
κ(B) = f(κ_grounding(B), κ_coherence(B))
```
Where f is some combination function. The rank is a summary, but you can track components.

**Haack**: But then why not just track the components? The single rank loses information.

**Resolution**: Keep both:
- Report ranks for comparison and formal properties
- Report components (grounding, coherence) for explanation
- The foundherentist structure is in the components; the rank summarizes for computation

---

### Pearl → Haack

**Pearl**: Susan, your grounding concept maps to what I call "identification" — can we estimate the effect from the available evidence? A causal claim is well-grounded if the graph structure allows identification.

**Haack**: Judea, that's interesting. So grounding in epistemics is analogous to identifiability in causation?

**Pearl**: Yes. And your coherence is analogous to my graph consistency — do the conditional independencies hold?

**Resolution**: Explicit bridge:
```
Epistemic Grounding ←→ Causal Identifiability
Epistemic Coherence ←→ Causal Graph Consistency
Epistemic Warrant ←→ Causal Effect Estimate Confidence
```

---

### Lamport → All

**Lamport**: This dialogue is productive, but informal. We need to nail down:
1. What is the STATE SPACE?
2. What are the TRANSITIONS?
3. What are the INVARIANTS?

I propose we define these before any more theoretical discussion.

**Panel**: Agreed. Let's synthesize.

---

## ROUND 3: SYNTHESIS — Implementation Plan

### Agreed Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     EPISTEMIC LAYER                              │
├──────────────────┬──────────────────┬──────────────────────────┤
│  RANKING SERVICE │  WARRANT SERVICE │  GROUNDING SERVICE       │
│  (Spohn)         │  (Pollock)       │  (Haack)                 │
│                  │                  │                          │
│  - Compute ranks │  - Check defeat  │  - Track experiential    │
│  - Conditionalize│  - Reinstatement │    basis                 │
│  - Combine with  │  - Warrant status│  - Compute grounding     │
│    defeat adj.   │                  │    metric                │
└────────┬─────────┴────────┬─────────┴────────┬─────────────────┘
         │                  │                  │
         └──────────────────┼──────────────────┘
                            │
                            ▼
              ┌─────────────────────────────┐
              │    EPISTEMIC-CAUSAL BRIDGE  │
              │    (Pearl integration)      │
              │                             │
              │  - Edge confidence from     │
              │    warrant + rank           │
              │  - Structure uncertainty    │
              │  - Identifiability check    │
              └──────────────┬──────────────┘
                             │
                             ▼
              ┌─────────────────────────────┐
              │      CAUSAL LAYER (BN)      │
              │      (Pearl do-calculus)    │
              └─────────────────────────────┘
```

### Agreed State Space (Lamport)

```tla
STATE ==
    [beliefs: SET(Belief),
     constraints: SET(Constraint),
     ranks: Belief -> Nat,
     warranted: SET(Belief),
     grounding: Belief -> GroundingStatus]

INITIAL ==
    [beliefs: {},
     constraints: {},
     ranks: λb. ∞,  \* No belief, so disbelief is infinite
     warranted: {},
     grounding: λb. UNGROUNDED]
```

### Agreed Invariants

| ID | Invariant | Source |
|----|-----------|--------|
| INV-1 | Consistency: ¬(warranted(B) ∧ warranted(rebutter(B))) | Pollock |
| INV-2 | Groundedness: warranted(B) → grounded(B) ∨ supported_by_warranted(B) | Haack |
| INV-3 | RankCoherence: supports(A,B) ∧ warranted(A) → rank(B) ≤ rank(A) + δ | Spohn |
| INV-4 | DefeatAsymmetry: defeats(D,B) → rank(D) < rank(B) | Pollock |
| INV-5 | BridgeCoherence: edge_confident(X,Y) → warranted(belief supporting X→Y) | Pearl |

### Implementation Phases (Liskov-approved decomposition)

#### Phase 1: Data Model Refactoring (1 sprint)

| Task | Description | Owner |
|------|-------------|-------|
| P1.1 | Split Belief into Content + Status + Provenance | Engineering |
| P1.2 | Create RankPair dataclass (rank, neg_rank) | Engineering |
| P1.3 | Create GroundingStatus enum and ExperientialClaim | Engineering |
| P1.4 | Update WebOfBelief to use new model | Engineering |
| P1.5 | Migration script for existing data | Engineering |

#### Phase 2: Ranking Service (1 sprint)

| Task | Description | Owner |
|------|-------------|-------|
| P2.1 | Create RankingService class | Engineering |
| P2.2 | Implement base rank computation from evidence | Engineering |
| P2.3 | Implement Spohn conditionalization | Engineering |
| P2.4 | Implement defeat-adjusted ranks | Engineering |
| P2.5 | Property-based tests for rank coherence | Engineering |
| P2.6 | Panel review: Spohn | Panel |

#### Phase 3: Warrant Service (1 sprint)

| Task | Description | Owner |
|------|-------------|-------|
| P3.1 | Create WarrantService class | Engineering |
| P3.2 | Implement prima facie warrant | Engineering |
| P3.3 | Implement rebutting defeat | Engineering |
| P3.4 | Implement undercutting defeat | Engineering |
| P3.5 | Implement reinstatement (recursive) | Engineering |
| P3.6 | Property-based tests for consistency invariant | Engineering |
| P3.7 | Panel review: Pollock | Panel |

#### Phase 4: Grounding Service (1 sprint)

| Task | Description | Owner |
|------|-------------|-------|
| P4.1 | Create GroundingService class | Engineering |
| P4.2 | Implement experiential basis tracking | Engineering |
| P4.3 | Implement grounding metric computation | Engineering |
| P4.4 | Implement coherence contribution (existing, refactored) | Engineering |
| P4.5 | Combine into foundherentist justification status | Engineering |
| P4.6 | Panel review: Haack | Panel |

#### Phase 5: Epistemic-Causal Bridge (1 sprint)

| Task | Description | Owner |
|------|-------------|-------|
| P5.1 | Create GraphConfidenceService | Engineering |
| P5.2 | Implement edge confidence from warrant + rank | Engineering |
| P5.3 | Implement structure uncertainty quantification | Engineering |
| P5.4 | Add identifiability check (basic) | Engineering |
| P5.5 | Panel review: Pearl | Panel |

#### Phase 6: Formal Verification (1 sprint)

| Task | Description | Owner |
|------|-------------|-------|
| P6.1 | Write TLA+ specification | Engineering + Lamport |
| P6.2 | Model check safety properties | Engineering |
| P6.3 | Model check liveness properties | Engineering |
| P6.4 | Document refinement relation to code | Engineering |
| P6.5 | Final panel review: All | Panel |

### Panel Sign-Off

| Panelist | Approves Plan? | Conditions |
|----------|---------------|------------|
| Spohn | YES | Ensure rank semantics are correct (degree of DISbelief) |
| Pollock | YES | Include reinstatement; classify defeater types properly |
| Haack | YES | Keep grounding + coherence separation visible |
| Pearl | YES | Bridge must output uncertainty, not just point estimates |
| Lamport | YES | TLA+ spec before Phase 3 coding ideally |
| Liskov | YES | Decomposition looks clean; maintain separation |

### Dissent Record

**Kyburg** (minority view): "Ranking theory is just qualitative probability. You'd be better off with actual probabilities and Bayesian updating. Spohn's framework is elegant but unnecessary if you have real probability theory."

**Response**: Noted. We're choosing ranks because they avoid the precision problem (what does P=0.73 mean?) and integrate better with defeasibility. Probabilities may be added later as an alternative computation.

---

## Next Steps

1. [ ] Professor Kirsh reviews and approves this plan
2. [ ] Engineering estimates effort for each phase
3. [ ] Phase 1 begins: Data model refactoring
4. [ ] Schedule individual panel reviews at end of each phase

---

*Panel consultation complete. Plan developed AND vetted.*
*P-ARCH4-EPISTEMIC-CALCULUS | 2026-02-12*
