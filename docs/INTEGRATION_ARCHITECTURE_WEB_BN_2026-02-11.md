# Integration Architecture: Epistemic Web + Bayesian Network

**Date**: 2026-02-11
**Author**: Terminal 1 (with Panel Consultation)
**Status**: DESIGN DOCUMENT — Pending Implementation

---

## Executive Summary

This document defines how two complementary graph structures should be integrated, visualized, and navigated:

1. **Epistemic Web of Belief** (Article_Eater) — Quinean coherentist network of beliefs connected by constraints
2. **Bayesian Causal Network** (BN_graphical) — Three-layer probabilistic model for predictions

The challenge: these are not the same graph, but they inform each other. A poorly designed integration will create confusion; a well-designed one enables powerful cross-layer reasoning.

---

## The Two Structures

### Structure A: Epistemic Web of Belief

**Location**: `Article_Eater_PostQuinean_v1/src/services/web_of_belief.py`

```
┌─────────────────────────────────────────────────────────────────────┐
│                    EPISTEMIC WEB OF BELIEF                          │
│                                                                     │
│  Organization: By epistemic level, theory, community                │
│                                                                     │
│  ┌─────────────┐     constraint      ┌─────────────┐               │
│  │   Belief    │◄──────────────────►│   Belief    │               │
│  │  (b_001)    │    (+0.8 support)   │  (b_002)    │               │
│  └─────────────┘                     └─────────────┘               │
│        │                                   │                        │
│        │ constraint                        │ constraint             │
│        │ (-0.3 tension)                    │ (+0.6 support)         │
│        ▼                                   ▼                        │
│  ┌─────────────┐                     ┌─────────────┐               │
│  │   Belief    │                     │   Belief    │               │
│  │  (b_003)    │                     │  (b_004)    │               │
│  └─────────────┘                     └─────────────┘               │
│                                                                     │
│  Attributes per belief:                                             │
│  - credence (0-1)                                                   │
│  - uncertainty                                                      │
│  - epistemic_level (THEORETICAL, EMPIRICAL, OBSERVATIONAL)          │
│  - status (ACCEPTED, TENTATIVE, SUSPENDED, REJECTED)                │
│  - entrenchment (emergent from connectivity)                        │
│  - theory_tags, community_associations                              │
│  - paper_sources (provenance)                                       │
└─────────────────────────────────────────────────────────────────────┘
```

**Key insight**: The web is about *justification*. Beliefs are justified by their coherence with other beliefs, weighted by constraints.

### Structure B: Bayesian Causal Network

**Location**: `BN_graphical/` repo

```
┌─────────────────────────────────────────────────────────────────────┐
│                    BAYESIAN CAUSAL NETWORK                          │
│                                                                     │
│  Organization: Three layers (Attributes → Mediators → Outcomes)     │
│                                                                     │
│  LAYER 1            LAYER 2              LAYER 3                    │
│  ATTRIBUTES         MEDIATORS            OUTCOMES                   │
│  ───────────        ─────────            ────────                   │
│  ┌─────────┐        ┌──────────┐         ┌────────────┐            │
│  │  wood   │───────►│ warmth   │────────►│  stress    │            │
│  │ coverage│        │          │         │            │            │
│  └─────────┘        └──────────┘    ┌───►└────────────┘            │
│                          │          │                               │
│  ┌─────────┐             │          │    ┌────────────┐            │
│  │ plants  │─────────────┼──────────┼───►│   focus    │            │
│  │         │             │          │    │            │            │
│  └─────────┘             ▼          │    └────────────┘            │
│                     ┌──────────┐    │                               │
│  ┌─────────┐        │cognitive │    │    ┌────────────┐            │
│  │daylight │───────►│  load    │────┴───►│satisfaction│            │
│  │         │        │          │         │            │            │
│  └─────────┘        └──────────┘         └────────────┘            │
│                                                                     │
│  Attributes per node:                                               │
│  - prior distribution (learned from data)                           │
│  - CPD (conditional probability distribution)                       │
│  - Goldilocks parameters (for inverted-U relationships)             │
│  - provenance (which beliefs/rules support this edge)               │
└─────────────────────────────────────────────────────────────────────┘
```

**Key insight**: The BN is about *prediction*. Given attribute values, what outcomes do we expect?

---

## The Integration Challenge

These are NOT the same graph:

| Aspect | Epistemic Web | Bayesian Network |
|--------|---------------|------------------|
| **Node meaning** | A belief (proposition) | A variable (measurable) |
| **Edge meaning** | Constraint (support/tension) | Causal influence |
| **Organization** | By epistemic level, theory | By causal layer |
| **Purpose** | Justification | Prediction |
| **Source** | Literature extraction | Model structure + data |

**The connection**: BN edges should be *informed by* beliefs in the epistemic web. A belief like "natural light reduces stress" corresponds to an edge from `daylight` to `stress` in the BN.

---

## Panel Consultation

### Panel Composition

For visualization and information architecture:
- **Dr. Ben Shneiderman** — Information visualization, Visual Information-Seeking Mantra
- **Dr. Herbert Simon** — Bounded rationality, satisficing, progressive disclosure
- **Dr. Judea Pearl** — Causal inference, do-calculus
- **Dr. Susan Haack** — Foundherentism, epistemic justification structure
- **Dr. Edward Tufte** — Data visualization, layering and separation

---

### Design Questions for Panel

**Q1**: How should users navigate between the epistemic web and the causal BN?

**Q2**: What is the visual representation of the connection between a belief and a BN edge?

**Q3**: How do we avoid cognitive overload when both structures are visible?

**Q4**: What filtering/focusing mechanisms are essential?

**Q5**: How should provenance chains be displayed (paper → belief → constraint → BN edge)?

---

## Panel Responses

### Dr. Ben Shneiderman (Information Visualization):

"Apply my Visual Information-Seeking Mantra: **Overview first, zoom and filter, then details on demand.**

**For this dual-structure problem:**

1. **Overview**: Show the BN as the primary view (3 layers, clean). The epistemic web is *metadata* about the BN, not a competing visualization.

2. **Zoom**: Clicking a BN edge reveals the beliefs that support it. This is your zoom operation.

3. **Filter**: Let users filter by theory (show only ART-related beliefs), by credence threshold, by paper source.

4. **Details on demand**: Drill into a single belief to see its full constraint network.

**Critical recommendation**: Do NOT show both graphs simultaneously at full fidelity. One must be primary; the other is context."

---

### Dr. Herbert Simon (Bounded Rationality):

"The user's cognitive budget is limited. They cannot hold two complex graphs in mind simultaneously.

**Design for satisficing:**

1. **Default view**: The BN (simple, 3 layers, actionable for prediction)
2. **Evidence view**: Toggle to see 'evidence strength' coloring on BN edges
3. **Deep dive**: Only enter the epistemic web when the user explicitly asks 'why?'

**Progressive disclosure tiers:**

| Tier | View | User Goal |
|------|------|-----------|
| T1 | BN only | 'What does the model predict?' |
| T2 | BN + edge confidence | 'How confident is this relationship?' |
| T3 | BN + belief summaries | 'What evidence supports this?' |
| T4 | Full epistemic web | 'Show me everything' (expert mode) |

**Never start at T4.** Most users will satisfice at T1 or T2."

---

### Dr. Judea Pearl (Causal Inference):

"The BN represents the causal structure. The epistemic web represents our *confidence* in that structure.

**Separation of concerns:**

1. **Structure**: The BN DAG (which edges exist)
2. **Parameters**: The CPDs (strength of edges)
3. **Justification**: The epistemic web (why we believe in these edges)

**Recommendation**: The BN should be the navigable interface. Each edge should have a 'justification panel' that shows:
- How many beliefs support this edge
- The aggregate credence
- Key conflicts or tensions
- Link to drill into the epistemic web for this edge

**Caution**: Do not confuse users about the direction of inference. The BN is for *forward* prediction (attributes → outcomes). The epistemic web is for *backward* justification (why we believe this)."

---

### Dr. Susan Haack (Foundherentism):

"In foundherentist epistemology, justification is neither purely foundational nor purely coherentist. It's crossword-puzzle-like: some beliefs are more directly experiential (like entries that match the clue), others are more theoretical (like entries that must cohere with crossing words).

**For this integration:**

1. **Respect epistemic levels**: OBSERVATIONAL beliefs (from direct measurement) should be visually distinct from THEORETICAL beliefs (from theory)

2. **Show entrenchment**: Some beliefs are more central to the web (higher entrenchment). These should be visually weighted—they're harder to revise.

3. **Display coherence, not just credence**: A belief's credence comes from coherence with other beliefs. Show the *sources* of credence, not just the number.

**Visualization suggestion**: When hovering over a BN edge, show a mini-coherence map—just the beliefs that bear on this edge, not the entire web. This is a 'local neighborhood' view."

---

### Dr. Edward Tufte (Data Visualization):

"Avoid chartjunk. Maximize the data-ink ratio.

**Principles for this integration:**

1. **Small multiples over animation**: Instead of animating between web and BN views, show them as small multiples (side-by-side at reduced scale).

2. **Layering and separation**: Use visual layers—the BN is the base layer, belief annotations are a hover layer, the full web is a modal layer.

3. **Color with purpose**:
   - BN layers: Green (attributes), Purple (mediators), Red (outcomes) — you have this
   - Edge confidence: Opacity (low confidence = faint line)
   - Belief status: Border style (dashed = tentative, solid = accepted)

4. **Micro/macro readings**: The same display should support quick scanning (macro) and detailed inspection (micro). This means avoiding visual clutter in the base state.

**Avoid**: Spaghetti graphs with everything connected to everything. If the full epistemic web must be shown, use hierarchical clustering or force-directed layout with strong clustering by theory."

---

## Synthesis: Proposed Architecture

Based on panel guidance, here is the proposed integration architecture:

### Layer Model

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                   PRIMARY VIEW: BN Causal Graph               │  │
│  │                                                               │  │
│  │   [Attributes] ────────► [Mediators] ────────► [Outcomes]     │  │
│  │                                                               │  │
│  │   Edge opacity = confidence (from epistemic web)              │  │
│  │   Click edge → Evidence Panel                                 │  │
│  │   Click node → Node Details                                   │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                           │                                         │
│                           │ click edge                              │
│                           ▼                                         │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                   EVIDENCE PANEL (slide-in)                   │  │
│  │                                                               │  │
│  │   Edge: daylight → stress                                     │  │
│  │   Confidence: 0.72 ± 0.15                                     │  │
│  │   Supporting beliefs: 5                                       │  │
│  │   Conflicting beliefs: 1                                      │  │
│  │                                                               │  │
│  │   Key evidence:                                               │  │
│  │   • "Natural light reduces cortisol" (0.81, Ulrich 1984)     │  │
│  │   • "Daylight improves mood" (0.75, Edwards 2002)            │  │
│  │                                                               │  │
│  │   [View in Epistemic Web] ← button to T4                      │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                           │                                         │
│                           │ click "View in Epistemic Web"           │
│                           ▼                                         │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                   EPISTEMIC WEB VIEW (modal/full-screen)      │  │
│  │                                                               │  │
│  │   Focus: Beliefs about daylight → stress                      │  │
│  │                                                               │  │
│  │   [Belief network visualization with constraints]             │  │
│  │                                                               │  │
│  │   Filters: [Theory ▼] [Level ▼] [Status ▼] [Paper ▼]         │  │
│  │                                                               │  │
│  │   [← Back to BN View]                                         │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Progressive Disclosure Tiers (per Simon)

| Tier | Name | Shows | User Question |
|------|------|-------|---------------|
| T1 | BN View | Causal graph only | "What does it predict?" |
| T2 | Confidence View | BN + edge opacity | "How sure are we?" |
| T3 | Evidence Panel | BN + belief summaries | "What's the evidence?" |
| T4 | Web View | Full epistemic web | "Show me everything" |

**Default**: T2 (BN with confidence-weighted edges)

### Navigation Patterns

```
                    T1: BN Only
                         │
                    toggle confidence
                         │
                         ▼
                    T2: BN + Confidence ◄──── DEFAULT ENTRY POINT
                         │
                    click edge
                         │
                         ▼
                    T3: Evidence Panel
                         │
                    "View in Web"
                         │
                         ▼
                    T4: Epistemic Web View
                         │
                    click belief
                         │
                         ▼
                    Belief Detail Modal
```

### Color Encoding (per Tufte)

| Element | Color | Meaning |
|---------|-------|---------|
| Attribute nodes | `#48bb78` (green) | Visual features (inputs) |
| Mediator nodes | `#667eea` (purple) | Psychological processes |
| Outcome nodes | `#fc8181` (red) | Measurable outcomes |
| Edge (high confidence) | Full opacity | Strong evidence |
| Edge (low confidence) | 30% opacity | Weak/uncertain evidence |
| Belief (ACCEPTED) | Solid border | Stable |
| Belief (TENTATIVE) | Dashed border | Under review |
| Belief (THEORETICAL) | Diamond shape | Theory-derived |
| Belief (EMPIRICAL) | Circle shape | Data-derived |
| Constraint (support) | Green line | Positive coherence |
| Constraint (tension) | Red line | Negative coherence |

### Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                          DATA ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌────────────────────┐         ┌────────────────────┐             │
│  │   ARTICLE_EATER    │         │    BN_GRAPHICAL    │             │
│  │                    │         │                    │             │
│  │  Papers → Beliefs  │         │  Structure + Data  │             │
│  │      │             │         │       │            │             │
│  │      ▼             │         │       ▼            │             │
│  │  WebOfBelief       │         │  PyMC Model        │             │
│  │      │             │         │       │            │             │
│  │      ▼             │         │       ▼            │             │
│  │  WebAccumulator    │         │  Predictions       │             │
│  │  (SQLite)          │         │  (API)             │             │
│  └────────────────────┘         └────────────────────┘             │
│           │                              │                          │
│           │ ae.rule.v1                   │ bn.prediction.v1         │
│           │                              │                          │
│           ▼                              ▼                          │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    INTEGRATION LAYER                          │  │
│  │                                                               │  │
│  │  BN_Edge_Justification:                                       │  │
│  │    - edge_id: "daylight_stress"                               │  │
│  │    - supporting_beliefs: ["b_001", "b_002", "b_005"]          │  │
│  │    - conflicting_beliefs: ["b_003"]                           │  │
│  │    - aggregate_credence: 0.72                                 │  │
│  │    - aggregate_uncertainty: 0.15                              │  │
│  │    - key_papers: ["ulrich_1984", "edwards_2002"]              │  │
│  │                                                               │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              │                                      │
│                              ▼                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    UNIFIED API                                │  │
│  │                                                               │  │
│  │  GET /graph                    → BN structure                 │  │
│  │  GET /graph/edge/{id}          → Edge details + justification │  │
│  │  GET /beliefs?edge={id}        → Beliefs for this edge        │  │
│  │  GET /web?focus={belief_ids}   → Epistemic web neighborhood   │  │
│  │  GET /provenance/{belief_id}   → Paper sources                │  │
│  │                                                               │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Key Schema: Edge Justification

This is the NEW schema that bridges the two structures:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "integration.edge_justification.v1",
  "title": "BN Edge Justification",
  "description": "Links a BN edge to its epistemic justification",

  "type": "object",
  "required": ["edge_id", "source_node", "target_node", "aggregate_credence"],
  "properties": {
    "edge_id": {
      "type": "string",
      "description": "BN edge identifier (e.g., 'daylight_stress')"
    },
    "source_node": {
      "type": "string",
      "description": "BN source node ID"
    },
    "target_node": {
      "type": "string",
      "description": "BN target node ID"
    },
    "aggregate_credence": {
      "type": "number",
      "minimum": 0,
      "maximum": 1,
      "description": "Weighted credence from supporting beliefs"
    },
    "aggregate_uncertainty": {
      "type": "number",
      "minimum": 0,
      "maximum": 1,
      "description": "Uncertainty in the aggregate"
    },
    "supporting_beliefs": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["belief_id", "credence", "content_summary"],
        "properties": {
          "belief_id": { "type": "string" },
          "credence": { "type": "number" },
          "content_summary": { "type": "string", "maxLength": 200 },
          "paper_id": { "type": "string" },
          "epistemic_level": {
            "type": "string",
            "enum": ["THEORETICAL", "EMPIRICAL", "OBSERVATIONAL"]
          }
        }
      }
    },
    "conflicting_beliefs": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["belief_id", "credence", "conflict_type"],
        "properties": {
          "belief_id": { "type": "string" },
          "credence": { "type": "number" },
          "conflict_type": {
            "type": "string",
            "enum": ["CONTRADICTS", "WEAKENS", "BOUNDARY_VIOLATION"]
          },
          "content_summary": { "type": "string" }
        }
      }
    },
    "net_support": {
      "type": "number",
      "description": "Supporting - conflicting evidence (can be negative)"
    },
    "key_theories": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Theories that bear on this edge (e.g., 'ART', 'SRT')"
    },
    "provenance": {
      "type": "object",
      "properties": {
        "n_papers": { "type": "integer" },
        "primary_papers": {
          "type": "array",
          "items": { "type": "string" },
          "maxItems": 5
        },
        "date_range": {
          "type": "object",
          "properties": {
            "earliest": { "type": "integer" },
            "latest": { "type": "integer" }
          }
        }
      }
    }
  }
}
```

---

## Implementation Phases

### Phase 1: Edge Justification Service (Article_Eater)

Create a service that, given a BN edge (source, target), returns the `EdgeJustification` object by querying the epistemic web.

**Location**: `Article_Eater/src/services/edge_justification.py`

```python
class EdgeJustificationService:
    def get_justification(self, source_var: str, target_var: str) -> EdgeJustification:
        """Find all beliefs that relate source_var to target_var."""
        pass

    def get_all_justifications(self) -> List[EdgeJustification]:
        """Generate justifications for all BN edges."""
        pass
```

### Phase 2: Integration API (New Service)

A lightweight service that exposes the unified API:

**Location**: New repo or shared service

```
GET /api/v1/integration/graph → BN structure with confidence
GET /api/v1/integration/edge/{id}/justification → EdgeJustification
GET /api/v1/integration/web/neighborhood?beliefs=b_001,b_002 → Web subgraph
```

### Phase 3: Frontend Integration (BN_graphical)

Modify `CausalGraphView.tsx` to:
1. Fetch edge confidence from integration API
2. Set edge opacity based on `aggregate_credence`
3. On edge click, show Evidence Panel with belief summaries
4. "View in Web" button opens epistemic web modal

### Phase 4: Epistemic Web Component (New)

Create a React component for epistemic web visualization:

**Location**: `BN_graphical/frontend-v2/src/features/epistemic/WebView.tsx`

Using React Flow (already in use) with:
- Clustering by theory (per Tufte)
- Node shapes by epistemic level (per Haack)
- Edge colors by constraint polarity

---

## Interaction Specifications

### I1: Hover on BN Edge

**Trigger**: Mouse hover on edge for 500ms
**Response**: Tooltip showing:
- Aggregate credence (e.g., "0.72 ± 0.15")
- Number of supporting beliefs
- Primary paper citation

### I2: Click on BN Edge

**Trigger**: Click on edge
**Response**: Evidence Panel slides in from right:
- Full `EdgeJustification` data
- Expandable list of supporting beliefs
- Expandable list of conflicts
- "View in Epistemic Web" button

### I3: Click "View in Epistemic Web"

**Trigger**: Click button in Evidence Panel
**Response**: Modal opens showing:
- Epistemic web focused on beliefs for this edge
- Beliefs highlighted, neighbors shown
- Filters for theory, level, status, paper

### I4: Click Belief in Web View

**Trigger**: Click on belief node in Web View
**Response**: Belief Detail Panel shows:
- Full content
- Credence with provenance
- Constraints (incoming/outgoing)
- Paper source with link
- "Related BN Edges" (reverse mapping)

### I5: Filter by Theory

**Trigger**: Select theory from dropdown
**Response**: Both views filter:
- BN: Dim edges not supported by this theory
- Web: Show only beliefs tagged with this theory

---

## Panel Sign-off

### Resolutions

| Question | Resolution | Source |
|----------|------------|--------|
| Q1: Navigation | BN primary → click → Evidence Panel → click → Web View | Shneiderman, Simon |
| Q2: Visual connection | Edge opacity = credence; click reveals beliefs | Pearl, Tufte |
| Q3: Cognitive overload | Progressive disclosure (T1-T4); never show both at full fidelity | Simon |
| Q4: Filtering | By theory, epistemic level, credence threshold, paper | Shneiderman |
| Q5: Provenance | Belief Detail Panel with paper source; "Related BN Edges" reverse link | Haack |

### Deferred Decisions

1. **Animation vs. Small Multiples**: Tufte suggests small multiples; current proposal uses modal. Revisit after user testing.

2. **Web Layout Algorithm**: Force-directed vs. hierarchical clustering. Recommend starting with theory-based clustering.

3. **Real-time Updates**: How to handle new beliefs being added during a session. Recommend polling with visual indicator.

---

## Action Items

### Immediate (Integration Foundation)

1. [ ] Create `integration.edge_justification.v1.schema.json` in contracts
2. [ ] Implement `EdgeJustificationService` in Article_Eater
3. [ ] Add `/edge/{id}/justification` endpoint to Article_Eater API

### Phase 2 (Frontend)

4. [ ] Modify `CausalGraphView.tsx` to fetch and display confidence
5. [ ] Create `EvidencePanel.tsx` component
6. [ ] Create `EpistemicWebView.tsx` component

### Phase 3 (Polish)

7. [ ] Implement filtering (theory, level, credence)
8. [ ] Add provenance links to papers
9. [ ] User testing and iteration

---

## Panel Members

**Panel P-VIS (Visualization Integration)**

| Member | Expertise | Key Contribution |
|--------|-----------|------------------|
| Dr. Ben Shneiderman | InfoVis | Overview+zoom+filter+details mantra |
| Dr. Herbert Simon | Cognitive Science | Progressive disclosure tiers |
| Dr. Judea Pearl | Causal Inference | Separation of structure/parameters/justification |
| Dr. Susan Haack | Epistemology | Foundherentist visual encoding |
| Dr. Edward Tufte | Data Visualization | Layering, color with purpose, data-ink ratio |

---

## PART II: Layer Interactions and Probing

### Panel Extension

The panel reconvened to address deeper questions about layer semantics:

**Q6**: How do the layers interact semantically (not just visually)?

**Q7**: How can a user probe the system to understand cross-layer implications?

**Q8**: What are the implications of the Web of Belief FOR the BN?

**Q9**: How can we predict gaps in the BN from argument structure in the Web?

---

### Dr. Judea Pearl (Layer Interaction Semantics):

"The relationship between the epistemic web and the BN is one of **justification to structure**. Let me be precise:

**Three types of implications from Web → BN:**

1. **Edge Existence**: If the web contains beliefs asserting 'X affects Y', there should be an edge X→Y in the BN. If the web has NO beliefs about X→Y, the edge is *unjustified* (though it may exist in the model from prior structure).

2. **Edge Direction**: The web may contain beliefs about causal direction. 'Light causes mood improvement' (forward) vs. 'Good mood makes people seek light' (reverse). These should inform BN edge direction. Conflicts here are important!

3. **Edge Strength (Priors)**: The aggregate credence of beliefs about X→Y should inform the prior probability that this edge is strong. High credence → expect strong relationship.

**User Probing Pattern:**
```
User: 'Why is there an edge from daylight to stress?'
System: 'Because the web contains 5 beliefs asserting this relationship:
         - Ulrich 1984: Natural light reduces cortisol (0.81 credence)
         - Edwards 2002: Daylight improves mood states (0.75 credence)
         ...'

User: 'Why is there NO edge from daylight to focus?'
System: 'The web contains only 1 belief about daylight→focus, with
         credence 0.45. Insufficient evidence to include edge.
         SUGGESTED GAP: Research daylight effects on cognitive performance.'
```

**Critical insight**: The BN should be *derivable* from the web, not independent of it."

---

### Dr. Susan Haack (Epistemic Implications):

"The web is not just data—it contains *arguments*. Arguments have structure: premises, inference patterns, and conclusions.

**Argument-to-BN Mapping:**

| Web Pattern | BN Implication |
|-------------|----------------|
| A supports B, B supports C | Mediation: A → B → C |
| A supports C, B supports C | Common effect: A → C ← B |
| A tensions B | Competing hypotheses: investigate |
| Theory T predicts X→Y | Add edge with theory provenance |
| X→Y lacks theoretical grounding | Flag as 'empirical only' |

**Probing Arguments:**

Users should be able to ask:
- 'What arguments support this edge?' (not just beliefs, but chains)
- 'What would happen if I rejected belief B?' (coherence propagation)
- 'Which edges have only empirical support vs. theoretical backing?'

**Gap Prediction from Arguments:**

If the web contains:
- Belief A: 'Plants reduce stress' (high credence)
- Belief B: 'Reduced stress improves focus' (high credence)
- NO belief about 'Plants improve focus' (MEDIATED claim)

Then the system should **predict** that plants→focus is a gap worth investigating. The argument structure (A→stress→focus) implies the compound claim should exist but doesn't.

**Formula for Argument-Implied Gaps:**
```
IF exists path A → X → Y in belief space
AND NOT exists direct belief A → Y
THEN suggest gap: 'Does A affect Y directly or only through X?'
```"

---

### Dr. Herbert Simon (User Probing):

"Users have bounded rationality. They can't hold the entire web and BN in mind. Probing must be **goal-directed**.

**Probing Modes:**

1. **Explanatory Mode**: 'Why does the BN have this edge?'
   - System traces back to supporting beliefs
   - Shows argument structure if present

2. **Counterfactual Mode**: 'What if this belief were false?'
   - System recalculates BN implications
   - Shows which edges would weaken or disappear

3. **Gap Discovery Mode**: 'Where should I look next?'
   - System analyzes argument structure
   - Identifies missing links (per Haack above)
   - Ranks by VOI (value of information)

4. **Consistency Mode**: 'Is the BN consistent with the web?'
   - System checks for orphan edges (no web support)
   - Checks for contradicted edges (web tensions)
   - Reports integrity score

**Probing Interface:**

Each mode should be a tab or toggle in the UI:
```
[Explain] [What If] [Find Gaps] [Check Consistency]
```

Not a single 'query' interface—users don't know what to ask. Offer structured probing."

---

### Dr. Nancy Cartwright (Enabling Conditions and Gaps):

"My work on 'capacities' is relevant here. A causal claim 'X causes Y' is only true under certain **enabling conditions**.

**Gap Prediction from Enabling Conditions:**

If the web contains:
- Belief: 'Natural light improves productivity (if thermal comfort maintained)'
- NO belief about: 'What happens when thermal comfort is NOT maintained'

Then this is a **conditional gap**. The BN edge daylight→productivity is only valid under certain conditions, and we don't know what happens outside those conditions.

**Enabling Condition Analysis:**

```
For each BN edge X → Y:
  1. Find beliefs with scope conditions
  2. Identify variables in scope conditions
  3. Check if those variables are in the BN
  4. If NOT in BN → GAP: 'Edge X→Y may require moderator Z'
```

**Example:**
- Web: 'Plants improve mood (in offices)'
- BN has: plants → mood
- Question: Does this hold in healthcare settings? Industrial settings?
- If web has no beliefs about other settings → SETTING GAP

**User Probe:**
```
User: 'Under what conditions is this edge valid?'
System: 'The edge plants→mood is supported by beliefs with these scope conditions:
         - Setting: offices (5 beliefs), healthcare (1 belief), industrial (0 beliefs)
         - Population: adults (4 beliefs), children (0 beliefs)
         GAPS: No evidence for industrial settings or children.'
```"

---

### Dr. Paul Thagard (Coherence and Gap Prediction):

"My work on explanatory coherence (ECHO) suggests that gaps appear where coherence is *locally low*.

**Coherence-Based Gap Detection:**

1. **Compute local coherence** for each BN edge (how well-connected are its supporting beliefs?)

2. **Identify coherence sinks**: Edges where supporting beliefs don't cohere with each other
   - This suggests the edge may be over-simplified
   - Or there are unresolved tensions

3. **Identify coherence gaps**: BN nodes with low total coherence
   - Few beliefs about this variable
   - Or beliefs conflict

**Predictable Gaps from Argument Analysis:**

| Pattern | Gap Type | User-Facing Message |
|---------|----------|---------------------|
| Path A→X→Y exists, direct A→Y missing | Mediation gap | 'Is the effect of A on Y direct or mediated?' |
| A→Y and B→Y, no A↔B | Interaction gap | 'Do A and B interact in affecting Y?' |
| Edge has only EMPIRICAL beliefs | Mechanism gap | 'What mechanism explains X→Y?' |
| Edge has only THEORETICAL beliefs | Validation gap | 'Has X→Y been empirically tested?' |
| Beliefs conflict on edge direction | Direction gap | 'Does X cause Y or Y cause X?' |
| Enabling conditions vary | Boundary gap | 'Under what conditions does X→Y hold?' |

**Gap Report Structure:**
```json
{
  "edge_id": "daylight_productivity",
  "gap_type": "mechanism_gap",
  "description": "The edge daylight→productivity has empirical support but no mechanistic explanation",
  "supporting_beliefs": ["b_001", "b_002", "b_003"],
  "missing": "No beliefs explain HOW daylight affects productivity",
  "suggested_search": "daylight productivity mechanism circadian alertness",
  "voi_score": 0.85
}
```"

---

## Cross-Layer Query Patterns

Based on panel input, here are the key query patterns users should be able to execute:

### Pattern 1: Web → BN Implication Query

**User asks**: "What does the web imply about the BN structure?"

**System response**:
```
WEB → BN STRUCTURAL IMPLICATIONS

Edges Strongly Supported (credence > 0.7):
  • daylight → stress (0.82, 5 beliefs)
  • plants → mood (0.78, 4 beliefs)
  • noise → cognitive_load (0.75, 3 beliefs)

Edges Weakly Supported (credence 0.3-0.7):
  • temperature → productivity (0.55, 2 beliefs, 1 conflict)
  • crowding → stress (0.48, 2 beliefs)

Edges in BN Without Web Support:
  ⚠️ wood_coverage → warmth (0 beliefs found)
  ⚠️ ceiling_height → cognitive_load (0 beliefs found)

Edges Implied by Web But Missing from BN:
  ➕ biophilia → restoration (3 beliefs, no edge)
  ➕ privacy → focus (2 beliefs, no edge)
```

### Pattern 2: Argument Chain Query

**User asks**: "What argument chains lead to this edge?"

**System response**:
```
ARGUMENT CHAINS FOR: daylight → productivity

Chain 1 (Mechanism: Circadian):
  daylight → circadian_regulation (0.85) → alertness (0.78) → productivity (0.72)
  Source: Boyce (2003), Veitch (2001)

Chain 2 (Mechanism: Mood):
  daylight → mood (0.81) → motivation (0.65) → productivity (0.68)
  Source: Edwards (2002), Heschong (1999)

Direct Claims:
  daylight → productivity (0.76, 3 beliefs, no mechanism specified)
  Source: Heschong (2002), Romm (1994)

GAPS IDENTIFIED:
  • Circadian and Mood chains both end at productivity
  • Do they interact? (No beliefs about alertness ↔ motivation)
  • Are they independent contributions? (Untested)
```

### Pattern 3: Gap Prediction Query

**User asks**: "What gaps can you predict from the argument structure?"

**System response**:
```
PREDICTED GAPS FROM ARGUMENT ANALYSIS

HIGH PRIORITY (VOI > 0.8):

1. Mediation Gap: plants → stress → focus
   The web shows plants reduce stress, and stress harms focus,
   but there's no direct evidence that plants improve focus.
   SUGGESTED SEARCH: "indoor plants cognitive performance attention"
   VOI: 0.87

2. Mechanism Gap: noise → productivity
   Multiple empirical beliefs but no mechanistic explanation.
   SUGGESTED SEARCH: "noise productivity mechanism distraction masking"
   VOI: 0.82

3. Boundary Gap: temperature → comfort
   All beliefs are for office settings, none for:
   - Healthcare, Retail, Industrial
   SUGGESTED SEARCH: "thermal comfort hospital retail factory"
   VOI: 0.79

MEDIUM PRIORITY (VOI 0.5-0.8):

4. Interaction Gap: daylight × view
   Both affect mood/stress, no beliefs about interaction.
   VOI: 0.71

5. Direction Gap: privacy → satisfaction
   2 beliefs say privacy increases satisfaction,
   1 belief says satisfied people seek more privacy.
   VOI: 0.65
```

### Pattern 4: Counterfactual Probe

**User asks**: "What if I removed belief B_001?"

**System response**:
```
COUNTERFACTUAL: Remove belief b_001 (Ulrich 1984: Nature views reduce stress)

IMPACT ON EPISTEMIC WEB:
  • Credence of 'nature → stress reduction' drops 0.82 → 0.65
  • 3 beliefs lose supporting constraint
  • Theory: SRT loses key founding claim
  • Entrenchment: 'nature → healing' cluster drops significantly

IMPACT ON BN:
  • Edge confidence: nature_view → stress drops 0.78 → 0.58
  • This edge would move from 'strongly supported' to 'weakly supported'
  • Downstream: stress → focus chain weakens

COHERENCE IMPACT:
  • Global coherence: 0.72 → 0.68
  • Local coherence (nature cluster): 0.81 → 0.63
  • Theories affected: SRT, Biophilia

RECOMMENDATION:
  This is a HIGH-ENTRENCHMENT belief. Removing it cascades widely.
  If challenging this belief, prepare alternative evidence for 12 dependent beliefs.
```

---

## Implementation: Gap Prediction Engine

Based on panel guidance (especially Haack and Thagard), here's the gap prediction algorithm:

### Algorithm: Argument-Based Gap Detection

```python
class GapPredictor:
    """Predict knowledge gaps from argument structure in the web."""

    def find_mediation_gaps(self) -> List[Gap]:
        """
        Find cases where A→X→Y exists but direct A→Y is missing.

        If A affects X, and X affects Y, does A affect Y?
        """
        gaps = []
        for path in self.web.find_two_hop_paths():
            a, x, y = path.source, path.intermediate, path.target
            direct = self.web.find_beliefs_connecting(a, y)
            if not direct:
                gaps.append(Gap(
                    gap_type="mediation",
                    description=f"Does {a} affect {y} directly, or only through {x}?",
                    implied_by=[path],
                    voi=self.compute_voi(a, y, mediator=x)
                ))
        return gaps

    def find_mechanism_gaps(self) -> List[Gap]:
        """
        Find edges with empirical support but no mechanistic explanation.
        """
        gaps = []
        for edge in self.bn.edges:
            beliefs = self.get_supporting_beliefs(edge)
            theoretical = [b for b in beliefs if b.level == 'THEORETICAL']
            empirical = [b for b in beliefs if b.level == 'EMPIRICAL']

            if empirical and not theoretical:
                gaps.append(Gap(
                    gap_type="mechanism",
                    description=f"What mechanism explains {edge.source} → {edge.target}?",
                    supporting_evidence=empirical,
                    voi=self.compute_voi_for_mechanism(edge)
                ))
        return gaps

    def find_boundary_gaps(self) -> List[Gap]:
        """
        Find edges where scope conditions are limited.
        """
        gaps = []
        for edge in self.bn.edges:
            beliefs = self.get_supporting_beliefs(edge)
            scope = self.aggregate_scope_conditions(beliefs)

            missing_settings = KNOWN_SETTINGS - scope.settings
            missing_populations = KNOWN_POPULATIONS - scope.populations

            if missing_settings or missing_populations:
                gaps.append(Gap(
                    gap_type="boundary",
                    description=f"Does {edge} hold in: {missing_settings}?",
                    scope_covered=scope,
                    scope_missing={"settings": missing_settings,
                                   "populations": missing_populations},
                    voi=self.compute_voi_for_generalization(edge, missing_settings)
                ))
        return gaps

    def find_direction_gaps(self) -> List[Gap]:
        """
        Find edges where causal direction is contested.
        """
        gaps = []
        for edge in self.bn.edges:
            beliefs = self.get_supporting_beliefs(edge)
            forward = [b for b in beliefs if b.direction == 'FORWARD']
            reverse = [b for b in beliefs if b.direction == 'REVERSE']

            if forward and reverse:
                gaps.append(Gap(
                    gap_type="direction",
                    description=f"Causal direction unclear: {edge.source} ↔ {edge.target}",
                    forward_evidence=forward,
                    reverse_evidence=reverse,
                    voi=self.compute_voi_for_direction(edge)
                ))
        return gaps
```

---

## Updated Panel Resolutions

| Question | Resolution | Source |
|----------|------------|--------|
| Q6: Layer interaction | Web provides justification (beliefs) for BN structure (edges); three types: existence, direction, strength | Pearl |
| Q7: User probing | Four modes: Explain, What-If, Find Gaps, Check Consistency | Simon |
| Q8: Web → BN implications | Aggregate credence → edge strength; missing beliefs → unjustified edges; argument chains → mediation structure | Pearl, Haack |
| Q9: Gap prediction | Six gap types from argument structure: mediation, mechanism, boundary, interaction, direction, validation | Haack, Thagard, Cartwright |

---

---

## PART III: Complete Layer Stack

The system has 12 distinct layers, each with specific responsibilities and interactions.

### Full Layer Inventory

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  LAYER 11: USER INTERFACE                                                   │
│  Streamlit MVP, BN_graphical React frontend                                 │
│  What users see and interact with                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│  LAYER 10: GRAPH EXPORT & VISUALIZATION                                     │
│  graph_api.py, graph_export.py, network_service.py                          │
│  GraphML, GEXF, vis.js output                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│  LAYER 9: BAYESIAN NETWORK (BN_graphical repo)                              │
│  PyMC model, three-layer causal structure                                   │
│  Attributes → Mediators → Outcomes                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│  LAYER 8: QUERY & REASONING                                                 │
│  query_engine.py, query_parser.py, interpretive_intelligence.py             │
│  voi_search.py, query_alerts.py                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  LAYER 7: SOCIAL EPISTEMOLOGY                                               │
│  social_epistemology.py, credibility_testing.py                             │
│  Communities, contestation, methodological diversity                        │
├─────────────────────────────────────────────────────────────────────────────┤
│  LAYER 6: EPISTEMIC-CAUSAL BRIDGE                                           │
│  epistemic_causal_bridge.py, bridge_warrants.py, causal_classifier.py       │
│  Quinean → Pearlian mapping, counterfactuals                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  LAYER 5: COHERENCE & ENTRENCHMENT                                          │
│  scalable_coherence.py, entrenchment_replay.py, stability_engine.py         │
│  Emergent entrenchment, constraint satisfaction                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  LAYER 4: EPISTEMIC WEB OF BELIEF                                           │
│  web_of_belief.py (1900+ lines) — THE CORE                                  │
│  web_persistence.py, web_accumulator.py                                     │
│  refined_epistemic.py, abstraction_levels.py                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  LAYER 3: THEORIES                                                          │
│  theory_registry.py, theory_matcher.py                                      │
│  ART, SRT, Biophilia, Environmental Psychology                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  LAYER 2: TAXONOMIES (VOCABULARY)                                           │
│  outcome_taxonomy.py, environment_taxonomy.py, vocabulary_bridge.py         │
│  Standardized terms for outcomes and environmental factors                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  LAYER 1: EXTRACTION                                                        │
│  extraction_to_web.py, table_extractor.py, scope_extractor.py               │
│  Claims → Beliefs mapper, scope parsing                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  LAYER 0: SOURCE DOCUMENTS                                                  │
│  PDF papers, Article Finder output                                          │
│  pdf_extraction.py, paper_lifecycle.py                                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Panel Consultation: Full Layer Interactions

### Extended Panel

For the full layer stack discussion:
- **Dr. Herbert Simon** — System architecture, modularity
- **Dr. Judea Pearl** — Causal layer interactions
- **Dr. Susan Haack** — Epistemic layer interactions
- **Dr. Helen Longino** — Social epistemology layer
- **Dr. Marcia Bates** — Information retrieval layers
- **Dr. David Marr** — Levels of analysis (computational, algorithmic, implementation)

---

### Dr. David Marr (Levels of Analysis):

"Your 12 layers conflate three distinct types of organization:

**Marr's Three Levels:**

1. **Computational Level**: What is the goal? What is being computed?
2. **Algorithmic Level**: How is it computed? What representations?
3. **Implementation Level**: How is it physically realized?

**Reorganizing Your Stack:**

| Your Layer | Marr Level | Purpose |
|------------|------------|---------|
| L0-1: Documents → Extraction | Implementation | Data input |
| L2-3: Taxonomies, Theories | Representation | Vocabulary |
| L4-5: Web, Coherence | Algorithmic | Belief revision |
| L6: Epistemic-Causal Bridge | Algorithmic | Causal inference |
| L7: Social Epistemology | Computational | Community credence |
| L8: Query | Computational | User goals |
| L9: BN | Algorithmic | Prediction |
| L10-11: Visualization | Implementation | Output |

**Key Insight**: Layers 4-7 are all ALGORITHMIC — they're different *representations* of the same underlying knowledge. Users shouldn't have to understand they're different layers; they should feel like one integrated system.

**Recommendation**: Present layers 4-7 as *views* into the same knowledge base, not separate systems."

---

### Dr. Herbert Simon (Modularity):

"The layer stack is too coupled. Information flows in too many directions.

**Current Flow Analysis:**

```
L0 → L1 → L4         (Papers → Extraction → Web)              ✓ Clean
L4 ↔ L5              (Web ↔ Coherence)                        ✓ Bidirectional OK
L4 → L6 → L9         (Web → Bridge → BN)                      ✓ Clean
L7 ↔ L4              (Social ↔ Web)                           ⚠️ Circular
L8 → L4,L7,L9        (Query → Multiple layers)                ⚠️ Fan-out
L9 → L4              (BN predictions → Web as beliefs)        ⚠️ Feedback loop
```

**Problematic Couplings:**

1. **L7 ↔ L4 (Social ↔ Web)**: Communities affect belief credence, and beliefs define communities. This is circular. Solution: Make communities a *view* into the web, not a separate layer.

2. **L8 → Multiple (Query fan-out)**: Queries touch too many layers directly. Solution: Query should go through ONE interface that coordinates layers internally.

3. **L9 → L4 (BN → Web)**: BN predictions become beliefs. This creates a feedback loop. Solution: Mark BN-derived beliefs distinctly; don't let them reinforce themselves.

**Recommended Architecture:**

```
┌────────────────────────────────────────────┐
│           UNIFIED KNOWLEDGE BASE           │
│  (Web + Coherence + Social + Bridge)       │
│                                            │
│  Single interface for all reads/writes     │
└────────────────────────────────────────────┘
        ▲                         │
        │ Extract                 │ Inform
        │                         ▼
┌───────────────┐         ┌───────────────┐
│   EXTRACTION  │         │   BN MODEL    │
│   (L0-L1)     │         │   (L9)        │
└───────────────┘         └───────────────┘
        ▲                         │
        │ Papers                  │ Predictions
        │                         ▼
┌───────────────┐         ┌───────────────┐
│    SOURCES    │         │    OUTPUT     │
│   (external)  │         │   (L10-L11)   │
└───────────────┘         └───────────────┘
```"

---

### Dr. Susan Haack (Epistemic Layer Interactions):

"The layers have different *epistemic statuses* that must be respected.

**Epistemic Status by Layer:**

| Layer | Epistemic Status | Can Revise? |
|-------|------------------|-------------|
| L0: Documents | Given (empirical base) | No |
| L1: Extraction | Interpreted | Yes (re-extract) |
| L2: Taxonomies | Conventional | Rarely |
| L3: Theories | Theoretical | With major revision |
| L4: Web beliefs | Mixed (all levels) | Continuously |
| L5: Coherence | Computed | Automatically |
| L6: Causal claims | Derived | When beliefs change |
| L7: Community views | Perspectival | Community-dependent |
| L9: BN predictions | Model-derived | When model changes |

**Interaction Rules:**

1. **Documents constrain extraction**: L0 → L1 is one-way. Extraction cannot change what the paper says.

2. **Extraction informs web, web informs extraction**: L1 ↔ L4. New web beliefs may suggest re-reading a paper. Circular but controlled.

3. **Theories organize beliefs**: L3 → L4. Theories provide structure but don't determine belief credence.

4. **Communities interpret, don't dictate**: L7 affects credence weighting but communities don't create beliefs ex nihilo.

5. **BN predictions are tentative**: L9 → L4 beliefs should be marked TENTATIVE and should not cite themselves as evidence.

**Critical Invariant**:
```
No belief's credence should depend solely on model predictions.
All beliefs must trace back to L0 (documents) eventually.
```"

---

### Dr. Helen Longino (Social Epistemology Layer):

"Layer 7 (Social Epistemology) is not truly separate — it's a *lens* through which other layers are viewed.

**Social Layer as Lens:**

```
Raw belief credence (L4)     →     Community-weighted credence
Coherence score (L5)         →     Within-community coherence
Causal claims (L6)           →     Community-contested causation
BN predictions (L9)          →     Community acceptance of model
```

**Community Interactions:**

| Community A View | Community B View | Resolution |
|------------------|------------------|------------|
| Belief B has credence 0.8 | Belief B has credence 0.4 | Report both |
| Theory T is central | Theory T is peripheral | Flag as contested |
| Causal claim X→Y is strong | X→Y is weak | Show community split |

**User Probing for Social Layer:**

```
User: 'How do different communities view this claim?'

System:
Community: ART (Attention Restoration Theory)
  - Credence: 0.82
  - Central to theory (entrenchment: high)
  - 5 researchers active

Community: SRT (Stress Recovery Theory)
  - Credence: 0.71
  - Supportive but not central
  - 3 researchers active

Community: Environmental Psychology (broad)
  - Credence: 0.75
  - Mainstream view
  - 12 researchers active

CONTESTED ASPECTS:
  - Mechanism (ART: attention, SRT: stress pathway)
  - Effect size (range: 0.3-0.6 across communities)
```"

---

### Dr. Marcia Bates (Information Retrieval Layers):

"Layers 0-1-2 form the **information retrieval substrate**. These should be invisible to users who think at the knowledge level (L4+).

**IR Layer Principle**: Users ask knowledge questions ('Does light affect mood?'), not document questions ('Which papers mention light and mood?').

**Layer Translation:**

```
Knowledge Query (L8)
    │
    ├──► Web Search (L4): Find beliefs about light→mood
    │
    ├──► Document Retrieval (L1): Which papers support these beliefs?
    │
    └──► Source Access (L0): [Available on request, not default]
```

**Interaction Pattern:**

1. **Default path**: Query → Beliefs → Summary
2. **Drill-down path**: Summary → Papers → Full text
3. **Expert path**: Query → Boolean search → Documents → Manual review

**Recommendation**: Don't expose L0-L2 in the primary interface. Show beliefs (L4) with provenance links. Only surface documents when user asks 'Show me the paper.'"

---

### Dr. Judea Pearl (Causal Layer Interactions):

"Layer 6 (Epistemic-Causal Bridge) and Layer 9 (BN) have a critical relationship that must be formalized.

**The Bridge Problem:**

The epistemic web (L4) contains *beliefs about causation*:
  - 'Light causes mood improvement' (a belief)

The BN (L9) contains *causal structure*:
  - light → mood (an edge in the DAG)

**These are not the same thing.** The belief is about the world; the edge is a model commitment.

**Interaction Rules:**

1. **Web → BN (Structure)**: Beliefs with causal content should inform BN structure.
   - If web has high-credence belief 'A causes B', BN should have edge A→B
   - If web has conflicting beliefs about direction, BN edge should be marked 'uncertain direction'

2. **Web → BN (Parameters)**: Belief credence should inform BN priors.
   - High credence about A→B strength → tighter prior on edge coefficient
   - Low credence → diffuse prior (let data speak)

3. **BN → Web (Predictions)**: BN predictions become beliefs, but:
   - Mark them as MODEL_DERIVED
   - Do not allow them to support the edges that generated them (no circular justification)

4. **BN → Web (Coherence Check)**: BN implications should be checked against web.
   - If BN predicts X but web has no beliefs about X, this is a GAP
   - If BN predicts X but web contradicts X, this is a CONFLICT

**Probing the Bridge:**

```
User: 'Is the BN consistent with the epistemic web?'

System:
CONSISTENCY CHECK RESULTS:

Edges Consistent with Web: 12/15
  ✓ daylight → stress (web credence: 0.82)
  ✓ plants → mood (web credence: 0.78)
  ...

Edges Lacking Web Support: 2/15
  ⚠️ wood_coverage → warmth (no beliefs found)
  ⚠️ ceiling_height → openness (1 belief, credence 0.35)

Edges Contradicted by Web: 1/15
  ❌ noise → creativity
     BN says: negative effect
     Web says: inverted-U (some noise helps)
     CONFLICT: Model simplifies non-linear relationship
```"

---

## Layer Interaction Matrix

Based on panel input, here is the authoritative interaction matrix:

```
        │ L0  │ L1  │ L2  │ L3  │ L4  │ L5  │ L6  │ L7  │ L8  │ L9  │ L10 │ L11 │
────────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┤
L0 Docs │  -  │  →  │     │     │     │     │     │     │     │     │     │     │
L1 Extr │     │  -  │  ←  │     │  →  │     │     │     │     │     │     │     │
L2 Tax  │     │  →  │  -  │  ↔  │  →  │     │     │     │     │     │     │     │
L3 Thry │     │     │  ↔  │  -  │  →  │     │     │     │     │     │     │     │
L4 Web  │     │  ←? │  ←  │  ←  │  -  │  ↔  │  →  │  ↔  │  ←  │  ↔  │  →  │     │
L5 Coh  │     │     │     │     │  ↔  │  -  │     │     │  ←  │     │  →  │     │
L6 Brdg │     │     │     │     │  ←  │     │  -  │     │  ←  │  →  │     │     │
L7 Soc  │     │     │     │     │  ↔  │     │     │  -  │  ←  │     │  →  │     │
L8 Qry  │     │     │     │     │  →  │  →  │  →  │  →  │  -  │  →  │     │  →  │
L9 BN   │     │     │     │     │  ↔  │     │  ←  │     │  ←  │  -  │  →  │     │
L10 Grph│     │     │     │     │  ←  │  ←  │     │  ←  │     │  ←  │  -  │  →  │
L11 UI  │     │     │     │     │     │     │     │     │  ←  │     │  ←  │  -  │
```

**Legend:**
- `→` : Layer A informs/feeds Layer B
- `←` : Layer A reads from Layer B
- `↔` : Bidirectional interaction
- `←?` : Potential feedback (re-extraction based on web)
- ` ` : No direct interaction

---

## User Probing Across Layers

### Cross-Layer Queries

Based on the panel recommendations, here are the cross-layer probing patterns:

**Query Type 1: Provenance Trace (L11 → L0)**
```
User: 'Where does this belief come from?'

System traces:
  Belief (L4) → Extraction (L1) → Paper (L0)

Response:
  Belief: "Natural light reduces stress"
  Extracted from: Ulrich (1984), p. 47
  Extraction method: Manual annotation
  Paper location: [PDF link]
```

**Query Type 2: Theory Grounding (L4 → L3)**
```
User: 'What theories support this?'

System traces:
  Belief (L4) → Theory associations (L3)

Response:
  Belief: "Natural light reduces stress"
  Theories:
    - SRT (Stress Recovery Theory): Central claim
    - ART (Attention Restoration Theory): Supportive
    - Biophilia: Consistent with evolutionary basis
```

**Query Type 3: Community Perspective (L4 → L7)**
```
User: 'Is this contested?'

System traces:
  Belief (L4) → Community credences (L7)

Response:
  Belief: "Natural light reduces stress"

  Community consensus: HIGH (all communities agree)

  ART community: 0.85 credence
  SRT community: 0.82 credence
  General EP: 0.78 credence

  No significant contestation.
```

**Query Type 4: Causal Implications (L4 → L6 → L9)**
```
User: 'What does this imply for the model?'

System traces:
  Belief (L4) → Causal Bridge (L6) → BN edge (L9)

Response:
  Belief: "Natural light reduces stress"

  Causal interpretation:
    Direction: FORWARD (light causes stress reduction)
    Mechanism: Via cortisol regulation (per SRT)

  BN implications:
    Edge: daylight → stress (negative coefficient)
    Current edge strength: -0.45
    Belief-implied strength: -0.38 to -0.52 (95% CI)

  Consistency: GOOD (BN matches belief)
```

**Query Type 5: Gap Discovery (L4 → L6 → L9 → L4)**
```
User: 'What gaps exist around this topic?'

System traces full loop:
  Starting belief (L4) → Related edges (L9) → Missing beliefs (L4)

Response:
  Topic: Natural light and stress

  GAPS IDENTIFIED:

  1. Mechanism Gap (L4):
     We know light reduces stress, but HOW?
     - Circadian pathway? (1 belief)
     - Vitamin D pathway? (0 beliefs)
     - Visual pathway? (0 beliefs)
     Suggested search: "daylight stress mechanism pathway"

  2. Boundary Gap (L4 via L6):
     Scope conditions are narrow:
     - Office settings: 4 beliefs
     - Healthcare: 1 belief
     - Residential: 0 beliefs
     Suggested search: "natural light stress home residential"

  3. Model Gap (L9 via L6):
     BN has edge daylight→stress but missing:
     - Interaction with artificial light
     - Time-of-day effects
     Suggested search: "circadian light timing stress"
```

---

## Recommended Layer Presentation to Users

Based on the panel's recommendation (Marr, Simon), users should NOT see 12 separate layers. Instead:

### User-Facing View: Three Modes

**Mode 1: KNOWLEDGE VIEW (Default)**
```
Shows: Answers to questions with confidence
Hides: L0-L3, L5, L6 (infrastructure)
Surfaces: L4 (beliefs), L7 (communities), L8 (queries)
```

**Mode 2: PREDICTION VIEW**
```
Shows: BN predictions with confidence intervals
Hides: L0-L6 (all epistemic layers)
Surfaces: L9 (BN), L10 (visualization)
Links to: Knowledge View for justification
```

**Mode 3: EXPERT VIEW**
```
Shows: Full layer access
Surfaces: All layers with explicit layer indicators
For: Researchers, debuggers, developers
```

### Cross-Mode Navigation

```
KNOWLEDGE VIEW                    PREDICTION VIEW
     │                                  │
     │ "What does the model             │ "Why does the model
     │  predict for this?"              │  predict this?"
     │                                  │
     └──────────────►◄──────────────────┘
                    │
                    │ "Show me everything"
                    ▼
              EXPERT VIEW
```

---

## Updated Panel Resolutions

| Question | Resolution | Source |
|----------|------------|--------|
| How many layers? | 12 technical layers, presented as 3 user modes | Marr, Simon |
| Layer coupling | Unify L4-L7 as 'Knowledge Base'; clean interfaces | Simon |
| L7 integration | Social as lens on L4, not separate data | Longino |
| L9 ↔ L4 feedback | BN predictions marked MODEL_DERIVED; no self-support | Pearl |
| User layer visibility | Hide infrastructure (L0-L3, L5-L6); show knowledge (L4, L7, L9) | Bates |
| Cross-layer probing | Five query types: Provenance, Theory, Community, Causal, Gap | All |

---

*Document created: 2026-02-11*
*Panel consultation: P-VIS (extended session) + P-LAYER (full stack review)*
*Status: APPROVED for implementation*
