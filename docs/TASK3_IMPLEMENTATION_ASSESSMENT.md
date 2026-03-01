# TASK 3: PUSHING THE ANALYSIS FORWARD — Implementation Assessment
## February 25, 2026 | Session 11

---

## Status Assessment

The transfer document (Session 10) specified three frontiers and a 10-step priority ordering.
Here is what can be done now, what requires CC, and what requires data preparation.

---

## Priority Steps From Transfer Document

| # | Step | Can Do Now? | Blocker |
|---|------|------------|---------|
| 1 | Update transfer doc | ✅ DONE (this session) | — |
| 2 | Domain content summary (node/edge lists) | ✅ CAN DO NOW | Requires reading panel outputs to extract structured node/edge inventory |
| 3 | Typed diff script | ❌ ASSIGN TO CC | Requires access to web snapshots from each panel stage |
| 4 | Run Algorithm 3 on all snapshots | ❌ BLOCKED by #3 | Requires snapshots + implemented Algorithm 3 |
| 5 | Run Level 1 testing (internal consistency) | ❌ BLOCKED by implementation | Requires Algorithm 1-6 implemented as running code |
| 6 | Run Level 2 testing (retrodiction) | ❌ BLOCKED by #5 + decision reconstruction | Requires pre-decision web states |
| 7 | Draft philosophical paper | ✅ DONE (this session) | — |
| 8 | Implement interval-valued credence propagation | ❌ ASSIGN TO CC | Extension of Algorithm 1 |
| 9 | Run parameter sensitivity analysis | ❌ BLOCKED by #5 | Requires running algorithms |
| 10 | Run Level 3 testing (CROSSCUT-I predictions) | ❌ BLOCKED by CROSSCUT-I execution | Must happen pre-panel |

---

## What Can Be Done Right Now: The Node and Edge Inventory

The single most productive thing we can do for Task 3 today is produce a structured inventory of the web's contents — every node, every edge, every edge type — in a format that can serve as input to the algorithms when they are implemented. This is Step 2 in the priority ordering, and it unblocks Steps 3–6.

### Approach

The node inventory should be compiled from:
- The MASTER_DOC (§60–71 panel descriptions, §90–95 template library)
- The panel output documents (each panel's calibrated templates)
- The transfer documents (which track working models, axioms, decisions)

The edge inventory should be compiled from:
- Reduction links: which T1.5 theories reduce to which T1 frameworks
- Bridge warrants: each template's warrant type
- Competition edges: from Crucible debates in each panel
- Cross-template interactions: from cross-panel flags
- Inheritance edges: from parameter sharing annotations
- Working model constraints: from Barrett-Craig and differential-mode adoption
- Axiom links: from AX parameter specifications
- Partial-outs: from double-counting resolutions

### Output Format

The inventory should be in JSON for direct algorithmic consumption:

```json
{
  "nodes": [
    {
      "id": "PP",
      "name": "Predictive Processing",
      "tier": "T1",
      "credence": 0.85,
      "panel_source": "pre-pipeline"
    },
    {
      "id": "PROSPECT_REFUGE",
      "name": "Prospect-Refuge Theory",
      "tier": "T1.5",
      "credence": 0.70,
      "reduces_to": ["PP", "DMN_PLACE"],
      "panel_source": "SPATIAL-I"
    },
    {
      "id": "VF3",
      "name": "Ceiling Height & Creativity (Affect Broadening)",
      "tier": "T2",
      "credence": 0.42,
      "bridge_warrant": "MECHANISM",
      "warrant_ceiling": 0.60,
      "panel_source": "VISUAL-I",
      "effect_size": "d = 0.40",
      "toulmin_summary": "Meyers-Levy & Zhu 2007; spatial volume → affect broadening → creative performance"
    }
  ],
  "edges": [
    {
      "source": "PP",
      "target": "PROSPECT_REFUGE",
      "type": "reduction",
      "subtype": null,
      "attenuation": 0.90
    },
    {
      "source": "VF3",
      "target": "EVIDENCE_MEYERS_LEVY_2007",
      "type": "bridge",
      "subtype": "MECHANISM",
      "attenuation": 0.75,
      "ceiling": 0.60
    }
  ]
}
```

### Scope

A full inventory requires reading all panel outputs — a substantial task requiring several hours. What we can produce NOW is:
1. The T1 framework nodes (10) with credences
2. The T1.5 domain theory nodes (10) with reduction links
3. The working model and axiom nodes (~10)
4. The reduction edge inventory (T1 → T1.5 → T2 chains)
5. A *template* for the T2 inventory that CC or Cowork can populate from panel outputs

This partial inventory (the skeleton of the graph) is enough to begin implementing and testing Algorithms 1–3 on the high-level structure, even before every T2 template is encoded.

---

## Assignments for CC

### Assignment 1: Typed Diff Script (Priority Step 3)

**Specification**: A Python script that takes two web states (JSON files as specified above) and produces:
- New nodes (in state 2 but not state 1)
- Removed nodes (in state 1 but not state 2)
- New edges
- Changed edges (same endpoints, different type or attenuation)
- Changed credences (same node, different credence value)
- Changed warrants (same node, different bridge warrant type)

**Input**: Two JSON files following the schema above.
**Output**: A structured diff report (JSON + human-readable markdown).

### Assignment 2: Algorithm Implementation (Priority Steps 5–6)

**Specification**: Implement Algorithms 1–3 in Python.
- Algorithm 1: Typed Credence Propagation (most important — this is the core computation)
- Algorithm 3: Typed Global Coherence Metric (needed for diagnostics and for Algorithm 4–5)
- Algorithm 2: Graded Competition Resolution (needed for competition edges)

**Input**: Web state JSON file.
**Output**: Updated credences, coherence score with decomposition.

**Testing**: Run on the partial inventory (T1 + T1.5 + axioms + working models, ~30 nodes) to verify convergence and reasonableness before scaling to full web.

### Assignment 3: Interval-Valued Extension (Priority Step 8)

**Specification**: Extend Algorithm 1 to accept interval-valued credences [c_lo, c_hi]. Implement interval arithmetic for the propagation rules. Test on the CMR graph and report whether output intervals are informatively narrow or vacuously wide.

---

## What Should Happen in the Next Session

1. **Produce the partial node/edge inventory** (T1 + T1.5 + axioms + working models + reduction edges) in JSON format.
2. **Delegate to CC**: Typed diff script (Assignment 1) and Algorithm implementation (Assignment 2).
3. **Seal CROSSCUT-I predictions** (Level 3 testing) before CROSSCUT-I execution — this is time-sensitive.
4. **Begin populating the T2 template inventory** from panel outputs — this is a large but straightforward extraction task that Cowork could assist with.

---

## Sealed CROSSCUT-I Predictions (For Level 3 Testing)

These predictions should be generated by the calculus once Algorithms 1–3 are implemented, but we can state informal predictions now based on the web's structure as understood by human analysis. These serve as a baseline:

**Prediction 1**: AX4 (Perceived Control) will be the LEAST contested axiom parameter in CROSSCUT-I, because it has already been elevated and calibrated across 17+ instances. The MOST contested will be AX_DOSE_RESPONSE (because dose-response functions differ substantially across domains — thermal comfort has tight optima, visual complexity has broad optima).

**Prediction 2**: ER_ECOLOGICAL_RATIONALITY_001 will NOT achieve EMPIRICAL_COVARIANCE. The ecological rationality concept (Gigerenzer) has strong theoretical support but the bridge to architectural cognition is at best FUNCTIONAL — the evidence base for ecological rationality in built environments is thin.

**Prediction 3**: Aesthetic Anchoring will be DEFERRED again (not promoted to formal T1.5 status). The theoretical appeal is strong but the empirical base for a distinct aesthetic anchoring mechanism is insufficient — it will be difficult to separate aesthetic anchoring from the combination of biophilia, fractal fluency, and awe that already covers most of the empirical territory.

**Prediction 4**: The awe templates (AX3) will produce the most cross-template interaction flags in the panel, because awe engages multiple systems simultaneously (NE arousal, DMN disruption, self-referential processing suppression) and these overlap with templates from STRESS-I, NEUROMOD-I, and VISUAL-I.

*These predictions are informal and based on human expert judgment. They should be compared with the formal predictions once the algorithms are running.*

---

*TASK3_IMPLEMENTATION_ASSESSMENT.md — CMR Project*
*February 25, 2026 (Session 11)*
*For session continuity and CC delegation*
