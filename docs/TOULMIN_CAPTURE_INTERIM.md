# ⚠️ SUPERSEDED — See (newer version exists) for current version

# TOULMIN RAW MATERIAL CAPTURE — INTERIM INSTRUCTION
## Applies to: MULTI-I and all subsequent panels until TJ-07 is complete
## Placed in: docs/ — Cowork reads this alongside panel clearance documents
## February 22, 2026

---

# WHAT THIS IS

The full Toulmin justification layer (defined in OPUS_REVIEW_GUIDE_ADDENDUM_
TOULMIN.md) requires a schema extension (TJ-01) and panel meta-prompt update
(TJ-07) that are not yet complete. Until those are done, panels will not
produce inline Toulmin justification in the calibrated JSON.

However, the Crucible debates ALREADY PRODUCE all the raw material needed
for Toulmin justification. The problem is that the current panel output
format compresses this material into one-line descriptions and discards it.

This interim instruction ensures the raw material is CAPTURED and RETAINED
so that retroactive Toulmin extraction is efficient rather than speculative.

---

# INSTRUCTION TO COWORK

When producing panel outputs (MULTI-I and onward), add the following section
AFTER the calibrated JSON block for each template and BEFORE the next
template's section:

```markdown
### Toulmin Raw Material — [TEMPLATE_ID]

**Evidence cited in debate (retain for justification.data):**
For each mechanism step that was discussed, list:
- Step N: [finding] — [source] — [paradigm] — [effect size if stated] — [n if stated]
- Step N: [finding] — [source] — ...

**Disputes (retain for justification.rebuttal and competing_accounts):**
- [Expert A] vs [Expert B] on [which step/parameter]:
  [A's position in 1-2 sentences]
  [B's position in 1-2 sentences]
  [Resolution or unresolved — state which]

**Scope conditions agreed (retain for justification.qualifier):**
- [What conditions must hold for this template's claims]
- [What timescale mismatches were identified]
- [What population restrictions apply]

**Convergence argument (retain for justification.backing):**
- [Why did the panel find the evidence convincing — what independent
  lines converged?]
```

# RULES

1. This section is a structured appendix, not a replacement for any existing
   output. All existing mandatory fields (JSON, IC2/AX4, cross-template refs,
   residual gaps) remain required.

2. The raw material section should be CONCISE — not a transcript of the full
   debate, but the specific content that would populate Toulmin fields. Think
   of it as pre-extraction: the panel is doing the work of identifying which
   debate content maps to which Toulmin field, saving the retroactive pass
   from having to reconstruct it.

3. If a mechanism step was NOT debated (intermediate steps that the panel
   accepted without discussion), write: "Step N: not debated — accepted
   without dispute." This is still useful — it tells the retroactive pass
   that no rebuttal or competing account exists for that step.

4. If the panel cannot fit this section within context limits (MUSIC-I and
   CROSSCUT-I are the most likely to be tight), prioritize retaining
   dispute content and scope conditions over evidence lists. Evidence can
   be reconstructed from references; disputes and qualifier conditions
   cannot.

---

# WHY THIS MATTERS

Without this section, retroactive Toulmin extraction (TJ-03 through TJ-06,
and equivalents for later panels) must reconstruct justification content
from the compressed panel debate narrative. With it, the extraction is
mechanical: copy structured content into JSON fields. The difference is
hours of careful reading vs. minutes of reformatting.

---

*TOULMIN_CAPTURE_INTERIM.md — CMR Project*
*Effective until TJ-07 (forward integration) replaces this with native Toulmin production*
