# COWORK SESSION TRANSFER DOCUMENT
## CMR Project — Panel Calibration Pipeline
## February 23, 2026
## For: New Cowork chat window continuation

---

# 1. IDENTITY AND ROLE

You are COWORK (Claude Opus 4.6) executing the CMR panel calibration pipeline. Your system ID in PROJECT_STATE.md is `COWORK`. You produce calibrated expert panel outputs for the Compositional Mechanistic Reasoning (CMR) system — a neuroscience-grounded framework for architectural design.

**Owner**: Professor David Kirsh, UCSD Cognitive Science

---

# 2. WHAT HAS BEEN COMPLETED

## Panels complete (3 of 8):

| Sprint | Panel | Templates | Lines | Experts | Refs | Output File |
|--------|-------|-----------|-------|---------|------|-------------|
| S-01 | SOCIAL-I | 11 | 1,513 | 12 | 43 | SOCIAL_I_Panel_Output.md |
| S-02 | MEMORY-I | 10 | 1,702 | 10 | 48 | MEMORY_I_Panel_Output.md |
| S-03 | MULTI-I | 9 | 1,647 | 9 | 30 | MULTI_I_Panel_Output.md |

All three have post-panel review documents written (REVIEW_*_post.md). Pre-panel review clearance documents exist for all three.

**MULTI-I notes**: Includes 9 Toulmin Raw Material appendices per the now-SUPERSEDED `TOULMIN_CAPTURE_INTERIM.md` approach. All 6 pre-panel constraints from Opus clearance were enforced (CT afferent ≤ CAPACITY, Ernst ≤ FUNCTIONAL, inverse effectiveness split, population-specific cultural conditioning, Pallasmaa ≤ 0.40, VISUAL-I partial-out).

## Panels remaining (5 of 8):

| Sprint | Panel | Templates | Status | Next Action |
|--------|-------|-----------|--------|-------------|
| S-04 | MUSIC-I | 13 | **NEXT** | Write PENDING_REVIEW, get clearance, execute |
| S-05 | THERMAL-I | 3 | PENDING | After MUSIC-I |
| S-06 | CREATIVE-I | 7 | PENDING | After THERMAL-I |
| S-07 | NEUROMOD-I | 10 | PENDING | After CREATIVE-I |
| S-08 | CROSSCUT-I | 15 | PENDING | After NEUROMOD-I |

---

# 3. CURRENT STATE — WHAT TO DO NEXT

**Phase 4 is ACTIVE.** The GATE OVERRIDE halt (which stopped work after MULTI-I) has been lifted. Resume the panel pipeline with S-04 MUSIC-I.

## CRITICAL NEW REQUIREMENT: Inline Toulmin Justification

Starting with MUSIC-I and all subsequent panels, every mechanism step in calibrated JSON MUST include an inline `justification` object. The TOULMIN_CAPTURE_INTERIM.md approach (raw material appendices after JSON blocks) is **SUPERSEDED**.

The justification object format per mechanism step:

```json
"justification": {
  "data": [
    {
      "finding": "<one-sentence description>",
      "source": "<APA short citation>",
      "paradigm": "<experimental paradigm>",
      "effect": "<effect size or key result>",
      "n": <sample size or null>,
      "design": "<study design>"
    }
  ],
  "backing": "<2-5 sentences: why warrant connecting data to claim is trustworthy>",
  "qualifier": "<2-5 sentences: scope conditions, timescale match, epistemic limits>",
  "rebuttal": "<2-5 sentences: Popperian falsification conditions>",
  "competing_accounts": [
    {
      "account": "<name>",
      "proponent": "<researcher>",
      "claim": "<one sentence>",
      "implication_for_template": "<what changes if correct>"
    }
  ],
  "depth_tier": "A|B|C"
}
```

**Depth tier rules:**
- **Tier A** (full): Steps with MECHANISM+ warrant, confidence > 0.55, contested steps, critical bridge points
- **Tier B** (standard): All other calibrated steps; min 2 data entries, backing, qualifier, rebuttal
- **Tier C** (stub): Steps < 0.40 in RESIDUAL GAPS; min 1 data entry, qualifier, rebuttal

**Consistency ceilings:**
- < 2 independent paradigms → confidence ≤ 0.50
- Active rebuttal condition → confidence ≤ 0.55
- Equally supported competing account → confidence ≤ 0.55
- Timescale mismatch → reduce confidence by 0.10–0.15
- Untested extrapolation → flag THEORETICAL_DEFAULT

Full specification: `docs/OPUS_REVIEW_GUIDE_ADDENDUM_TOULMIN.md`

---

# 4. S-04 MUSIC-I — EXECUTION DETAILS

## Status
- `pre_panel_review_cleared: false` → Must write PENDING_REVIEW_MUSIC_I.md first
- Sprint Task Brief location: `docs/SPRINT_TASK_BRIEF.md` (sole execution authority)
- Sprint section starts at approximately line 351

## Input files (7 required):
1. `TRANSFER_Feb21_Session8_CORRECTED.md` — project state
2. `GAP_PANEL_MASTER_PLAN_Feb21.md` — §3 MUSIC-I specification
3. `exemplar_panel_criteria.md` — style authority
4. `*GENERALIZED_PANEL_META_PROMPT_Feb21.md` — panel prompt template (TJ-07 updated with Toulmin requirements)
5. `MULTI_I_Panel_Output.md` — MSI interactions (MUSIC-I depends on MULTI-I)
6. `VISUAL_I_Panel_Output_Feb21.md` — VF2 visual rhythm template (coordinate bridge warrants with BRECVEMA rhythmic entrainment)
7. `OPUS_REVIEW_GUIDE.md` — calibration discipline cheat sheet

**Also read**: `OPUS_REVIEW_GUIDE_ADDENDUM_TOULMIN.md` for full Toulmin specification

## 13 Target templates:

| # | Template ID | Name | T1 Frameworks |
|---|-------------|------|---------------|
| 1 | BRECVEMA_MULTI_MECHANISM_001 | BRECVEMA multi-mechanism musical emotion | PP, EC, NM, IC |
| 2 | BRECVEMA_BRAINSTEM_001 | Acoustic features → brainstem reflex → startle/attention | PP, NM |
| 3 | BRECVEMA_RHYTHMIC_ENTRAINMENT_002 | Musical pulse → motor entrainment → rhythmic coordination | EC, PP |
| 4 | BRECVEMA_CONTAGION_003 | Musical expression → emotional contagion → mirrored affect | IC, EC |
| 5 | BRECVEMA_EXPECTANCY_004 | Musical structure → expectancy violation → aesthetic emotion | PP, NM |
| 6 | BRECVEMA_MEMORY_005 | Musical cue → episodic memory retrieval → emotion reactivation | MS, IC |
| 7 | NEURAL_MUSIC_EMOTION_ARCH_001 | Neural Architecture of Music-Evoked Emotion | PP, NM, IC |
| 8 | PLEASURABLE_SADNESS_001 | Paradox of Pleasurable Negative Emotions in Music | IC, PP |
| 9 | ACOUSTIC_EMOTION_MAPPING_001 | Acoustic Feature → Emotion Mapping (Bottom-Up Pathway) | PP, IC |
| 10 | MS_ACOUSTIC_ECOLOGY_001 | Acoustic Ecology and Soundscape Processing | MS, PP |
| 11 | AUD_SCENE_ANALYSIS_001 | Acoustic complexity → auditory scene analysis → cognitive load | MSI, PP |
| 12 | AUD_REVERBERATION_SPACE_003 | Room acoustics → auditory spatial perception → enclosure/safety | MSI, IC |
| 13 | AUDITORY_FRACTAL_SCALING_001 | Auditory 1/f Scaling — Biophilic Soundscape Statistics | PP |

## Proposed expert roster (10 experts):

| Expert | Institution | Primary |
|--------|------------|---------|
| Patrik Juslin | Uppsala | BRECVEMA_MULTI_MECHANISM_001 anchor; BRECVEMA originator |
| Stefan Koelsch | Bergen | NEURAL_MUSIC_EMOTION_ARCH_001 anchor |
| Nina Kraus | Northwestern | BRECVEMA_BRAINSTEM_001 anchor; subcortical auditory plasticity |
| Peter Vuust | Aarhus | BRECVEMA_EXPECTANCY_004 anchor; predictive coding + music |
| Jian Kang | UCL | MS_ACOUSTIC_ECOLOGY_001 anchor; ISO 12913 co-author |
| David Huron | Ohio State | BRECVEMA_EXPECTANCY_004 complement; ITPRA theory |
| Tuomas Eerola | Durham | PLEASURABLE_SADNESS_001 anchor; emotional contagion |
| Trevor Cox | Salford | AUD_REVERBERATION_SPACE_003 anchor; room acoustics |
| Shinichi Sato | (acoustics) | AUD_SCENE_ANALYSIS_001 complement |
| Richard Taylor | Oregon | AUDITORY_FRACTAL_SCALING_001 complement; 1/f statistics |

**Note**: This is the largest panel (13 templates). Pre-panel review may modify the roster.

---

# 5. EXECUTION PROTOCOL (APPLIES TO ALL SPRINTS)

## Step-by-step for each sprint:

1. **Read PROJECT_STATE.md** — check for claimed tasks, current phase status
2. **Read SPRINT_TASK_BRIEF.md** — find sprint section, check pre_panel_review_cleared
3. **If pre_panel_review_cleared: false** → Write PENDING_REVIEW_[PANEL_ID].md with:
   - Proposed expert roster analysis (flag gaps, overlaps, narrow expertise)
   - Scope ambiguities in template descriptions
   - Known dependency issues with prior panels
   - Wait for human to provide Opus clearance document
4. **After clearance** → Read all input files listed in sprint section
5. **Execute panel** following crash-resilience protocol:
   - Create output stub immediately → SAVE
   - Panel header + charge → SAVE
   - Panel composition (expert roster) → SAVE
   - Round table opening statements (every 2 statements → SAVE)
   - Crucible debates (after each → SAVE)
   - Calibrated JSON blocks WITH INLINE TOULMIN (after each → SAVE)
   - Residual gaps per template
   - CMR Integration Note with partial-out protocols
   - Gap Tracker Update Block
   - Full APA references
   - Update status to COMPLETE
6. **Write REVIEW_[PANEL_ID]_post.md** with flags
7. **Update PROJECT_STATE.md** — mark task COMPLETED in changelog

## Mandatory per-template outputs:
- Calibrated JSON with mechanism chain, population modifiers, architectural modifiers
- **Inline Toulmin justification per mechanism step** (NEW — replaces appendix approach)
- IC2 (Body Budget Prediction) interaction statement
- AX4 (Perceived Control) interaction statement
- Cross-template references where applicable
- Residual gaps

## Style:
- Bertrand Russell: clear, intelligent, accessible, no humor
- APA references with DOIs
- No emojis in prose
- Model: Claude Opus 4.6

---

# 6. KEY DOCUMENTS — AUTHORITY HIERARCHY

| Priority | Document | Purpose |
|----------|----------|---------|
| 1 | PROJECT_STATE.md | Coordination protocol — read BEFORE work, update AFTER |
| 2 | SPRINT_TASK_BRIEF.md | Sole execution authority for sprint sequence |
| 3 | OPUS_REVIEW_GUIDE.md | Calibration discipline (bridge warrant hierarchy, ceilings, red flags) |
| 4 | OPUS_REVIEW_GUIDE_ADDENDUM_TOULMIN.md | Full Toulmin justification specification |
| 5 | exemplar_panel_criteria.md | Style and quality authority |
| 6 | *GENERALIZED_PANEL_META_PROMPT_Feb21.md | Panel prompt template (TJ-07 updated) |
| 7 | GAP_PANEL_MASTER_PLAN_Feb21.md | Panel specifications and template lists |

---

# 7. KNOWN ISSUES AND WARNINGS

1. **SPRINT_TASK_BRIEF.md status table is stale** — Shows S-02 and S-03 as PENDING, but both are COMPLETE. CC updated the individual sprint sections but the overview table (lines 74-83) was not updated. The individual sprint status fields are authoritative.

2. **S-07 NEUROMOD-I**: A-06 added a mathematical integration note for ALLOSTATIC_MASTER_001 (additive weighted-sum, McEwen/Seeman sources, THEORETICAL_DEFAULT flags). Read the sprint brief carefully before executing.

3. **S-08 CROSSCUT-I**: Gemini audit (A-03) identified severe context window load — 1.5MB context for 15 templates. May require chunking strategy.

4. **Template count**: 53 calibrated as of MULTI-I completion (23 original + 11 SOCIAL-I + 10 MEMORY-I + 9 MULTI-I). MUSIC-I will add 13 → 66 total.

5. **Retroactive Toulmin** (Phase 5): TJ-03 (VISUAL-I) and TJ-04 (SPATIAL-I) done by AG. TJ-05 (LIGHT-I) done by CC. TJ-06 (STRESS-I) claimed by CC, in progress. These are parallel to panel pipeline and do not block your work.

6. **TOULMIN_CAPTURE_INTERIM.md** is SUPERSEDED (line 1 marked). Do NOT use the appendix approach. Use inline justification per mechanism step.

7. **The uploaded sprint brief file may read as 0 bytes** — if so, the cached version is available at:
   `/sessions/dreamy-intelligent-heisenberg/mnt/.claude/projects/-sessions-dreamy-intelligent-heisenberg/f3e6934a-2ef2-4784-987b-e034c862bf16/tool-results/toolu_01FqASkQQXTkWCQEBoBKXHkn.txt`
   However, `SPRINT_TASK_BRIEF.md` in docs/ should be the current version (CC consolidated files).

---

# 8. CORRECTION LOG

- **Model identification**: Always write "Claude Opus 4.6" in footers and review documents. Never write "Sonnet". This was corrected once during MEMORY-I session.
- **CROSSMODAL_CONGRUENCE_001 scope**: Corrected from "spatial navigation and social cognitive integration" to "multi-sensory spatial coherence" per Opus clearance. Sprint Task Brief description was erroneous.

---

# 9. IMMEDIATE ACTION

Upon starting the new session:

1. Read `docs/PROJECT_STATE.md` — verify Phase 4 ACTIVE, no conflicts
2. Read `docs/SPRINT_TASK_BRIEF.md` — S-04 MUSIC-I section (starts ~line 351)
3. Read `docs/OPUS_REVIEW_GUIDE_ADDENDUM_TOULMIN.md` — full Toulmin spec
4. Since `pre_panel_review_cleared: false`, write `docs/PENDING_REVIEW_MUSIC_I.md`
5. Wait for David to provide Opus clearance (PRE_PANEL_REVIEW_CLEARANCE_MUSIC_I.md)
6. Execute MUSIC-I with inline Toulmin justification per mechanism step
7. Write `docs/REVIEW_MUSIC_I_post.md`
8. Update PROJECT_STATE.md

After MUSIC-I: proceed to S-05 THERMAL-I (3 templates), then S-06 CREATIVE-I (7), S-07 NEUROMOD-I (10), S-08 CROSSCUT-I (15).

---

*TRANSFER_Cowork_Session_Feb23_2026.md — CMR Project*
*Generated by Cowork (Claude Opus 4.6), February 23, 2026*
