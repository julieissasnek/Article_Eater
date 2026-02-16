---------------------------- MODULE EpistemicWeb ----------------------------
(*
 * TLA+ Specification for Epistemic Web (ARCH-4 Phase P6)
 *
 * This specification formally defines the state space, actions, and invariants
 * for the epistemic web system implementing Spohn ranking, Pollock defeat,
 * Haack grounding, and Pearl causal bridge.
 *
 * Per panel consultation (2026-02-12), Lamport requirements:
 * - STATE SPACE: All possible web configurations
 * - INITIAL STATE: Empty web or seed beliefs
 * - ACTIONS: Add belief, add constraint, revise, update ranks, etc.
 * - INVARIANTS: Properties in all reachable states
 * - PROGRESS: Termination guarantees
 *
 * Invariants to verify:
 * - INV-1: Consistency — ¬(warranted(B) ∧ warranted(rebutter(B)))
 * - INV-2: Groundedness — warranted → grounded ∨ supported_by_warranted
 * - INV-3: RankCoherence — supports(A,B) ∧ warranted(A) → rank(B) ≤ rank(A) + δ
 * - INV-4: DefeatAsymmetry — defeats(D,B) → rank(D) < rank(B)
 * - INV-5: BridgeCoherence — edge_confident(X,Y) → warranted(belief supporting X→Y)
 *
 * References:
 * - Lamport, L. (2002). Specifying Systems. Addison-Wesley.
 * - Spohn, W. (2012). The Laws of Belief.
 * - Pollock, J.L. (1995). Cognitive Carpentry.
 * - Haack, S. (1993). Evidence and Inquiry.
 *)

EXTENDS Naturals, FiniteSets, Sequences

CONSTANTS
    Beliefs,        \* Set of possible belief IDs
    MaxRank,        \* Maximum rank value (e.g., 100)
    SupportPenalty  \* δ in INV-3 (e.g., 1)

VARIABLES
    ranks,          \* ranks[b] ∈ [0..MaxRank] × [0..MaxRank] (rank, neg_rank)
    constraints,    \* Set of (source, target, type) tuples
    warranted,      \* Set of currently warranted beliefs
    grounded,       \* Set of currently grounded beliefs
    defeated,       \* Set of currently defeated beliefs
    causalEdges     \* Set of (cause, effect, confidence) tuples

-----------------------------------------------------------------------------
(*
 * TYPE INVARIANTS
 *)

TypeInvariant ==
    /\ ranks \in [Beliefs -> (0..MaxRank) \X (0..MaxRank)]
    /\ constraints \subseteq (Beliefs \X Beliefs \X {"supports", "contradicts", "rebuts", "undercuts"})
    /\ warranted \subseteq Beliefs
    /\ grounded \subseteq Beliefs
    /\ defeated \subseteq Beliefs
    /\ causalEdges \subseteq (Beliefs \X Beliefs \X (0..100))

-----------------------------------------------------------------------------
(*
 * HELPER OPERATORS
 *)

\* Get rank of belief (κ(B))
Rank(b) == ranks[b][1]

\* Get negation rank (κ(¬B))
NegRank(b) == ranks[b][2]

\* Belief is believed iff neg_rank > rank
Believed(b) == NegRank(b) > Rank(b)

\* Belief is disbelieved iff rank > neg_rank
Disbelieved(b) == Rank(b) > NegRank(b)

\* Belief is suspended iff rank = neg_rank
Suspended(b) == Rank(b) = NegRank(b)

\* Get supporters of belief b
Supporters(b) == {s \in Beliefs : <<s, b, "supports">> \in constraints}

\* Get rebuttters of belief b
Rebutters(b) == {r \in Beliefs : <<r, b, "rebuts">> \in constraints}

\* Get undercutters of belief b
Undercutters(b) == {u \in Beliefs : <<u, b, "undercuts">> \in constraints}

\* Get all defeaters of belief b
Defeaters(b) == Rebutters(b) \cup Undercutters(b)

\* Is b observational (self-grounded)?
Observational(b) == b \in grounded /\ Supporters(b) = {}

-----------------------------------------------------------------------------
(*
 * INVARIANTS (INV-1 through INV-5)
 *)

\* INV-1: Consistency
\* ¬(warranted(B) ∧ warranted(rebutter(B)))
\* No belief and its rebutter can both be warranted
Consistency ==
    \A b \in Beliefs :
        b \in warranted =>
            \A r \in Rebutters(b) : r \notin warranted

\* INV-2: Groundedness
\* warranted(B) → grounded(B) ∨ ∃s ∈ Supporters(B) : warranted(s)
\* Warranted beliefs must be grounded or supported by warranted beliefs
Groundedness ==
    \A b \in Beliefs :
        b \in warranted =>
            \/ b \in grounded
            \/ \E s \in Supporters(b) : s \in warranted

\* INV-3: RankCoherence
\* supports(A,B) ∧ warranted(A) → rank(B) ≤ rank(A) + δ
\* Supported beliefs can't have much higher rank than their warranted supporters
RankCoherence ==
    \A a, b \in Beliefs :
        (<<a, b, "supports">> \in constraints /\ a \in warranted) =>
            Rank(b) <= Rank(a) + SupportPenalty

\* INV-4: DefeatAsymmetry
\* defeats(D,B) → rank(D) < rank(B) (when D is effective)
\* A defeater must have lower rank than what it defeats
DefeatAsymmetry ==
    \A d, b \in Beliefs :
        (d \in Defeaters(b) /\ d \in warranted) =>
            Rank(d) < Rank(b)

\* INV-5: BridgeCoherence
\* edge_confident(X,Y) → ∃b : b supports edge(X,Y) ∧ warranted(b)
\* Confident causal edges must have warranted belief support
\* (Simplified: edges with confidence > 50 must have warranted support)
BridgeCoherence ==
    \A <<x, y, conf>> \in causalEdges :
        conf > 50 =>
            \E b \in Beliefs :
                (b \in warranted /\ <<b, x, "supports">> \in constraints)

\* Combined Safety Invariant
Safety ==
    /\ TypeInvariant
    /\ Consistency
    /\ Groundedness
    /\ RankCoherence
    /\ DefeatAsymmetry
    /\ BridgeCoherence

-----------------------------------------------------------------------------
(*
 * INITIAL STATE
 *)

Init ==
    /\ ranks = [b \in Beliefs |-> <<0, 0>>]  \* All beliefs suspended initially
    /\ constraints = {}
    /\ warranted = {}
    /\ grounded = {}
    /\ defeated = {}
    /\ causalEdges = {}

-----------------------------------------------------------------------------
(*
 * ACTIONS
 *)

\* Add a new belief with initial rank
AddBelief(b, rank, negRank, isGrounded) ==
    /\ ranks' = [ranks EXCEPT ![b] = <<rank, negRank>>]
    /\ grounded' = IF isGrounded THEN grounded \cup {b} ELSE grounded
    /\ UNCHANGED <<constraints, warranted, defeated, causalEdges>>

\* Add a support constraint
AddSupport(source, target) ==
    /\ constraints' = constraints \cup {<<source, target, "supports">>}
    /\ UNCHANGED <<ranks, warranted, grounded, defeated, causalEdges>>

\* Add a rebut constraint (defeat)
AddRebut(defeater, target) ==
    /\ constraints' = constraints \cup {<<defeater, target, "rebuts">>}
    /\ UNCHANGED <<ranks, warranted, grounded, defeated, causalEdges>>

\* Update warrant status based on current state
UpdateWarrant(b) ==
    LET
        hasSupport == Supporters(b) /= {} \/ b \in grounded
        hasUndefeatedDefeater == \E d \in Defeaters(b) : d \in warranted /\ d \notin defeated
    IN
        IF hasSupport /\ ~hasUndefeatedDefeater
        THEN /\ warranted' = warranted \cup {b}
             /\ defeated' = defeated \ {b}
        ELSE /\ warranted' = warranted \ {b}
             /\ IF hasUndefeatedDefeater
                THEN defeated' = defeated \cup {b}
                ELSE defeated' = defeated
    /\ UNCHANGED <<ranks, constraints, grounded, causalEdges>>

\* Conditionalize on evidence (Spohn)
Conditionalize(b, firmness, supports) ==
    LET
        adjustedRank == IF supports
                        THEN <<Rank(b) - firmness, NegRank(b) + firmness>>
                        ELSE <<Rank(b) + firmness, NegRank(b) - firmness>>
        clampedRank == <<IF adjustedRank[1] < 0 THEN 0
                         ELSE IF adjustedRank[1] > MaxRank THEN MaxRank
                         ELSE adjustedRank[1],
                         IF adjustedRank[2] < 0 THEN 0
                         ELSE IF adjustedRank[2] > MaxRank THEN MaxRank
                         ELSE adjustedRank[2]>>
    IN
        /\ ranks' = [ranks EXCEPT ![b] = clampedRank]
        /\ UNCHANGED <<constraints, warranted, grounded, defeated, causalEdges>>

\* Add a causal edge with confidence
AddCausalEdge(cause, effect, confidence) ==
    /\ causalEdges' = causalEdges \cup {<<cause, effect, confidence>>}
    /\ UNCHANGED <<ranks, constraints, warranted, grounded, defeated>>

\* Remove a belief
RemoveBelief(b) ==
    /\ ranks' = [x \in Beliefs |-> IF x = b THEN <<0, 0>> ELSE ranks[x]]
    /\ constraints' = {c \in constraints : c[1] /= b /\ c[2] /= b}
    /\ warranted' = warranted \ {b}
    /\ grounded' = grounded \ {b}
    /\ defeated' = defeated \ {b}
    /\ causalEdges' = {e \in causalEdges : e[1] /= b /\ e[2] /= b}

-----------------------------------------------------------------------------
(*
 * NEXT STATE RELATION
 *)

Next ==
    \/ \E b \in Beliefs, r \in 0..MaxRank, nr \in 0..MaxRank, g \in BOOLEAN :
        AddBelief(b, r, nr, g)
    \/ \E s, t \in Beliefs :
        AddSupport(s, t)
    \/ \E d, t \in Beliefs :
        AddRebut(d, t)
    \/ \E b \in Beliefs :
        UpdateWarrant(b)
    \/ \E b \in Beliefs, f \in 1..5, s \in BOOLEAN :
        Conditionalize(b, f, s)
    \/ \E c, e \in Beliefs, conf \in 0..100 :
        AddCausalEdge(c, e, conf)
    \/ \E b \in Beliefs :
        RemoveBelief(b)

-----------------------------------------------------------------------------
(*
 * SPECIFICATION
 *)

Spec == Init /\ [][Next]_<<ranks, constraints, warranted, grounded, defeated, causalEdges>>

-----------------------------------------------------------------------------
(*
 * LIVENESS PROPERTIES
 *)

\* Eventually, if a belief has evidence, its rank should decrease
\* (weak fairness on evidence processing)
EventualRankDecrease ==
    \A b \in Beliefs :
        (Supporters(b) /= {}) ~> (Rank(b) < MaxRank)

\* Eventually, if a belief is defeated, it should not be warranted
EventualDefeatEffect ==
    \A b \in Beliefs :
        (\E d \in Defeaters(b) : d \in warranted) ~> (b \notin warranted)

-----------------------------------------------------------------------------
(*
 * REFINEMENT MAPPING
 *
 * Python implementation should satisfy:
 *
 * ranks <-> Dict[str, RankPair] in ranking_service.py
 *   - Rank(b) = ranks[b].rank
 *   - NegRank(b) = ranks[b].neg_rank
 *
 * constraints <-> Set of Constraint in web_of_belief.py
 *   - Type mapping: SUPPORTS, CONTRADICTS, etc.
 *
 * warranted <-> Set[str] from warrant_service.compute_warrant().warranted
 *
 * grounded <-> Set[str] from grounding_service.compute_grounding().grounded_beliefs
 *
 * defeated <-> Set[str] from warrant_service.compute_warrant().defeated
 *
 * causalEdges <-> Dict[(str,str), EdgeConfidence] from graph_confidence_service
 *)

=============================================================================
