# Article Eater: Comprehensive Web-of-Belief Health Diagnostic

**Purpose:** A single script that produces a complete health assessment of the Article Eater system. Combines the depth of the Sprint D.9 diagnostic with the post-rebuild comparison metrics, and adds critical checks that neither report included. Designed to be run by any agent (Opus, Claude Code, Codex, Antigravity) and produce an unambiguous pass/fail assessment with actionable detail.

**Output:** `web_health_report_YYYY-MM-DD.md`

---

## Section 1: Database Structural Integrity

**What it checks:** Can we even trust the container?

- List all tables present; flag any missing from expected schema
- Expected tables: `beliefs`, `constraints`, `bridges`, `paper_integrations`, `paper_publication`, `paper_quality`, `entrenchment_snapshots`, `entrenchment_events`, `coherence_history`, `local_coherence_history`, `belief_merge_log`, `web_snapshots`, `coherence_alerts`, `web_metadata`
- Row counts per table
- Schema version from `web_metadata` (if present)
- Foreign key integrity: any orphan references (e.g., constraints referencing belief IDs that don't exist)
- **PASS criteria:** All expected tables present, zero orphan references

---

## Section 2: Belief / Node Quality

**What it checks:** Are the nodes in the web legitimate scientific variables, or garbage?

### 2a. Basic counts
- Total belief nodes
- Beliefs with mapped IV (independent variable)
- Beliefs with mapped DV (dependent variable)
- Beliefs with BOTH IV and DV mapped
- Beliefs with NEITHER mapped

### 2b. Garbage detection (from D.9 — this was MISSING in post-rebuild reports)
- Nodes > 50 characters (likely OCR fragments or run-on text)
- Nodes containing doubled characters (OCR corruption pattern: `ttaaccttiillee`)
- Nodes in `env.unresolved.*` namespace — count and sample (10 worst)
- Nodes containing words from a stoplist irrelevant to architecture/neuroscience (e.g., "pharmacy," "war," "country," "prosocial" — terms that signal off-topic paper ingestion)
- Nodes with non-ASCII characters or encoding artifacts

### 2c. Vocabulary coverage
- Count of unique IV terms
- Count of unique DV terms
- Top 20 most-connected IVs (with degree)
- Top 20 most-connected DVs (with degree)
- IVs/DVs that appear in only ONE belief (singletons — potential noise)

**PASS criteria:** 0 garbage nodes, 0 unresolved env IDs, 0 beliefs with neither IV nor DV mapped, singleton ratio < 15%

---

## Section 3: Graph Connectivity

**What it checks:** Is the web a coherent structure or a bag of disconnected fragments?

- Number of connected components
- Size of largest component (nodes and % of total)
- Size distribution of non-largest components (histogram: 1-node, 2-5, 6-20, 21-100, 100+)
- Diameter of largest component (longest shortest path — measures integration depth)
- Average shortest path length in largest component
- Number of articulation points (nodes whose removal disconnects the graph — structural vulnerabilities)
- Number of bridge edges (edges whose removal disconnects the graph)

**PASS criteria:** 1 connected component; if >1, largest must contain >95% of nodes and no component smaller than 3 nodes

---

## Section 4: Constraint / Edge Quality

**What it checks:** Are the relationships between beliefs meaningful and properly weighted?

### 4a. Constraint layer breakdown
- Count by type: intra-paper coherence, replication links, scope extensions, contradictions, template bridges, domain bridges
- Contradictions: list all with belief pairs and direction trust scores
- Contradictions suppressed (low direction trust): count and threshold used
- Template bridges: count (CRITICAL — was 0 in both post-rebuild reports; should not be 0)
- Domain bridges: count and distribution across domain pairs

### 4b. Edge weight distribution (from D.9 — MISSING in post-rebuild reports)
- Mean credence across all constraints
- Credence distribution: histogram in 0.1 bins from 0.0 to 1.0
- Constraints with credence = 0.5 exactly (likely default/unestimated — flag count)
- Constraints with credence < 0.4 (low confidence — what are they?)
- Constraints with credence > 0.85 (high confidence — sample 10)
- Any constraints with credence outside [0, 1] (data corruption)

### 4c. Constraint density
- Constraints per belief (mean, median, min, max)
- Beliefs with 0 constraints (isolated — should not exist if graph is connected)
- Beliefs with >50 constraints (potential hub overload)

**PASS criteria:** 0 default-credence edges, template bridges > 0, no credence values outside [0,1], no beliefs with 0 constraints

---

## Section 5: Coherence Metrics

**What it checks:** Is the web internally consistent, and is coherence improving over time?

- Global coherence score (current)
- Coherence score from `coherence_history` — plot or list last 10 values with timestamps
- Local coherence: distribution across beliefs (mean, std, min, max)
- Beliefs with local coherence < 0.2 (incoherent with their neighbourhood — list top 10)
- Beliefs with local coherence > 0.8 (well-integrated — count)
- Any coherence alerts in `coherence_alerts` table

**PASS criteria:** Global coherence > 0.5, no beliefs with local coherence < 0.1, coherence trend non-decreasing over last 5 snapshots

---

## Section 6: Template Coverage

**What it checks:** Do the mechanistic templates have adequate empirical grounding in the web?

- Total templates referenced in web (unique template IDs)
- Expected template inventory: T1–T52, M1–M17, AX1–AX6, EC1–EC12 (87 total)
- Templates with 0 supporting beliefs (ungrounded templates)
- Templates with 1–2 supporting beliefs (weakly grounded)
- Templates with 3+ supporting beliefs (adequately grounded)
- Distribution of beliefs per template (histogram)
- Cross-template links: how many belief pairs span different templates?

**PASS criteria:** 0 ungrounded templates for any template in active use, >60% of templates adequately grounded (3+ beliefs)

---

## Section 7: Domain Coverage

**What it checks:** Are all 10 domains represented, or are some empirically empty?

- Belief count per domain
- Constraint count per domain
- Cross-domain constraint count (domain pairs)
- Domains with < 10 beliefs (underpopulated)
- Domain coverage rating vs. the four-star system in the structural framework

**PASS criteria:** All 10 domains have ≥10 beliefs, all cross-domain pairs with shared mechanisms have ≥1 bridge

---

## Section 8: Paper Integration Quality

**What it checks:** Are the source papers properly ingested and linked?

- Total papers in `paper_integrations`
- Papers with quality scores in `paper_quality`
- Distribution of paper quality scores (histogram)
- Papers contributing 0 beliefs to the web (ingested but not extracted)
- Papers contributing >20 beliefs (potential over-extraction or OCR duplication)
- Average beliefs per paper
- Papers with missing metadata (no DOI, no year, no authors)

**PASS criteria:** 0 papers contributing 0 beliefs, mean beliefs per paper between 2 and 15, <5% papers missing critical metadata

---

## Section 9: Claim Extraction Precision (the critical right-half diagnostic)

**What it checks:** Are extracted claims actually correct?

This is the section that the D.9 report identified as the core failure. It requires sampling and manual/automated verification.

### 9a. Automated checks
- Claims where IV == DV (self-referential — always wrong)
- Claims where effect direction is null or "unknown"
- Claims where the paper DOI resolves to a retracted paper
- Claims with duplicate IV+DV+paper combinations (extraction stuttering)

### 9b. Sample audit (requires human or LLM verification)
- Random sample of 20 claims
- For each: does the stated IV actually appear in the source paper?
- For each: does the stated DV actually appear in the source paper?
- For each: is the stated effect direction correct?
- **Precision** = correct claims / total sampled
- **Target:** Precision ≥ 0.85

**PASS criteria:** 0 self-referential claims, 0 null-direction claims, precision ≥ 0.85 on sample audit

---

## Section 10: Old vs. New Comparison (when applicable)

**What it checks:** Did the rebuild improve things?

Side-by-side table (as in the post-rebuild reports) comparing:

| Metric | Old DB | New DB | Δ | Direction |
|---|---|---|---|---|
| Beliefs | | | | |
| Constraints | | | | |
| Coherence | | | | |
| Connected components | | | | |
| Mapped beliefs (IV+DV) | | | | |
| Garbage-like beliefs | | | | |
| Unresolved env IDs | | | | |
| Default-credence edges | | | | |
| Template bridges | | | | |

**PASS criteria:** Every metric improved or held constant; no regression on any dimension

---

## Section 11: Executive Summary

Auto-generated from pass/fail results above:

```
ARTICLE EATER WEB HEALTH — [DATE]
==================================
Section 1  Database Integrity      [PASS/FAIL]
Section 2  Node Quality            [PASS/FAIL]  (garbage: N, unresolved: N)
Section 3  Graph Connectivity      [PASS/FAIL]  (components: N)
Section 4  Constraint Quality      [PASS/FAIL]  (default-credence: N, template bridges: N)
Section 5  Coherence               [PASS/FAIL]  (global: X.XXX)
Section 6  Template Coverage       [PASS/FAIL]  (ungrounded: N/87)
Section 7  Domain Coverage         [PASS/FAIL]  (underpopulated: N/10)
Section 8  Paper Integration       [PASS/FAIL]  (zero-belief papers: N)
Section 9  Extraction Precision    [PASS/FAIL]  (precision: X.XX)
Section 10 Old vs New              [PASS/FAIL/SKIP]

OVERALL: [PASS / FAIL — N sections failing]
```

---

## Implementation Notes

1. **Single entry point:** `python scripts/web_health_diagnostic.py [--old-db path] [--new-db path] [--claims-file path] [--output path]`
2. **Runtime:** Should complete in < 60 seconds on the production database
3. **Dependencies:** Only sqlite3, json, collections, statistics from stdlib; no external packages required
4. **Idempotent:** Read-only on all databases; never modifies data
5. **Agent-agnostic:** Any of the four agents can run it; output is self-contained markdown
6. **Exit code:** 0 if all sections pass, 1 if any section fails (for CI integration)

---

## What Was Missing From Each Previous Report

| Check | D.9 Report | Post-Rebuild Reports |
|---|---|---|
| Database schema integrity | ✓ (table list) | ✗ |
| Garbage node detection | ✓ | ✗ |
| OCR corruption patterns | ✓ | ✗ |
| Edge weight distribution | ✓ | ✗ |
| Default-credence count | ✓ | ✗ |
| Connected components | ✓ | ✓ |
| Old vs new comparison | ✗ | ✓ |
| Constraint layer breakdown | ✗ | ✓ |
| Template coverage | ✗ | ✗ |
| Domain coverage | ✗ | ✗ |
| Claim extraction precision | ✗ | ✗ |
| Paper integration quality | ✗ | ✗ |
| Coherence trend | ✗ | ✗ |
| Local coherence distribution | ✗ | ✗ |
| Articulation points / bridges | ✗ | ✗ |
| Executive summary with pass/fail | ✗ | ✗ |
