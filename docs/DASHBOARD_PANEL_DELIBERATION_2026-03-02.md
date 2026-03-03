# Human Dashboard Panel Deliberation — ATLAS System

**Date**: 2026-03-02  
**Context**: ATLAS (Article Eater) needs a human dashboard showing Overseer state, HITL tasks, pipeline status, and recommendations.  
**Panel**: 6 experts from dashboard design, cognitive science, epistemic systems, SRE, HCI, and academic research.

---

## Panel Question: What should the ATLAS Human Dashboard show?

### Panel Member 1 — UX Dashboard Architect (Former Tableau, now AI startup)

> "Your system has a classic monitoring challenge: too much data, not enough actionable guidance. Based on best practices:
>
> **Three views, not one dashboard:**
> 1. **Mission Control** (daily glance, 30s): AESHI score, papers processed today, HITL queue depth, violations count, belief growth trend
> 2. **Operations** (when investigating): pipeline stage status, extraction queue, API quotas, per-service health from `health_check()`
> 3. **Research Command** (for David): theory coverage gaps, VOI-ranked next papers, cross-theory tension alerts, new T3 beliefs
>
> **Progressive disclosure**: Start with 5 numbers that answer 'Is the system healthy?' then drill down. Never show 20 panels at once."

### Panel Member 2 — Cognitive Scientist (Expert in cognitive load)

> "David is a UCSD Cognitive Science professor — he'll notice cognitive overload immediately. Key principles:
>
> 1. **Attention budget**: The dashboard gets 60 seconds/day. Every widget must justify its attentional cost.
> 2. **Signal/noise ratio**: Show ONLY items that require human action. The Overseer should pre-filter.
> 3. **Recommendation framing**: Don't show 'HITL queue: 23 items.' Show: 'Action needed: 5 high-priority papers. Fastest path: paste these 5 DOIs into Elicit (~10 min).'
> 4. **Temporal structure**: Morning briefing (what happened overnight), action items (what to do now), forecast (what's coming).
>
> The dashboard is a **cognitive prosthesis**, not a data dump."

### Panel Member 3 — Epistemic Systems Designer (Haack school)

> "This system is unique because the dashboard itself should be epistemically transparent. Show:
>
> 1. **Belief web health**: Coherence trends, orphan beliefs, theory coverage percentage
> 2. **Provenance gaps**: How many beliefs lack anchors? Which theories have shallow evidence?
> 3. **Predictive value**: What questions CAN the system answer well vs. poorly? Show confidence zones.
> 4. **Meta-epistemic status**: 'The system knows about 13 theories across 1,083 papers with 33,000 findings. Coverage of predictive processing: 87%. Coverage of circadian mechanisms: 12%'
>
> The most powerful insight: **what does the system NOT know?**"

### Panel Member 4 — Site Reliability Engineer

> "From an ops standpoint, the dashboard needs:
>
> 1. **Service health matrix**: Green/yellow/red for every service from `orchestrator.health_check()`
> 2. **Latency budget**: Show per-step timing from enrichment metadata — highlight any step exceeding 500ms
> 3. **Queue depths**: HITL queue (23), extraction queue, integration queue
> 4. **API quota status**: OpenAlex ($0.01/query budget), CORE (rate limits), PMC (daily caps)
> 5. **Alert feed**: Last 10 Overseer alerts with severity, time, and resolution status
>
> Use **traffic light colors** (red/yellow/green) for status. Humans process these instantly."

### Panel Member 5 — HCI Researcher (Human-AI interaction specialist)

> "The key design choice: is this a **monitoring dashboard** or a **collaboration interface**?
>
> For ATLAS, it's both. But prioritize collaboration:
> 1. **Recommendation cards**: 'Based on current gaps, these 3 papers would most improve the EN. Here's how to get them.'
> 2. **Natural language queries**: Let David ask 'What happened today?' and see a narrative summary
> 3. **Human feedback integration**: When David acquires a paper, the dashboard should let him mark DOIs as 'acquired' in the HITL DB
> 4. **Session continuity**: Show what AG and Claude did since last visit — like a changelog but human-readable
>
> The interaction model should be: **David tells the system what he did, the system tells David what to do next.**"

### Panel Member 6 — Academic Research Lab Manager

> "As someone who manages research infrastructure for students and faculty:
>
> 1. **Student view**: Simplified read-only view showing what the system knows, organized by theory
> 2. **Export capability**: Generate reports for lab meetings, publication planning
> 3. **Teaching mode**: Show how a question flows through the system — input → extraction search → belief lookup → enrichment → answer. This IS a teaching tool.
> 4. **Audit trail**: Who asked what questions, which papers were added, what beliefs changed — for reproducibility
>
> David's students need to understand the system, not just use it."

---

## Panel Consensus: ATLAS Dashboard Requirements

### Tier 1 — Must Have (Phase 1)

| Widget | Data Source | Purpose |
|--------|-----------|---------|
| AESHI score (big number) | Overseer | System health at a glance |
| HITL action queue | `hitl_needed.json` | Papers needing human acquisition |
| Pipeline status | Nightly pipeline log | Which stages ran, which failed |
| Service health matrix | `orchestrator.health_check()` | 9 services: green/yellow/red |
| Belief growth chart | Web of Belief | Beliefs over time, by theory |
| Agent activity feed | MESSAGE_BOARD | What AG and Claude did recently |

### Tier 2 — Important (Phase 2)

| Widget | Data Source | Purpose |
|--------|-----------|---------|
| Theory coverage radar | Extraction analysis | 13 T1.5 theories: how well covered? |
| Recommendation cards | Overseer + gap predictor | "Next 3 papers to get" with action links |
| Enrichment latency dashboard | Orchestrator metadata | Per-step timing, budget usage |
| Tension/conflict alerts | Argumentation engine | Cross-theory contradictions |

### Tier 3 — Nice to Have (Phase 3)

| Widget | Data Source | Purpose |
|--------|-----------|---------|
| Natural language query bar | QA handler | "What does the system know about biophilia?" |
| Student teaching view | System walkthrough | Pipeline flow visualization |
| Export/report generator | Multiple | Lab meeting reports |

### Implementation: Streamlit Dashboard (recommended)

The existing codebase already has Streamlit installed (it's in the venv). A single `scripts/atlas_dashboard.py` using Streamlit would:
- Require zero deployment infrastructure
- Run locally with `streamlit run scripts/atlas_dashboard.py`
- Support real-time data from JSON files, SQLite, and Python imports
- Be naturally extensible with tabs for each view

---

## Best Practices to Follow

1. **60-second rule**: Everything visible on first load in 60 seconds
2. **Action > Information**: Every panel should end with "What should I do?"
3. **Progressive disclosure**: Summary → details on click
4. **Traffic lights**: Red/yellow/green for all status indicators
5. **Temporal structure**: "Since last visit..." framing
6. **Cognitive load**: Max 5-7 widgets on first view

---

*Shared with Claude via MESSAGE_BOARD (Msg 007).*
