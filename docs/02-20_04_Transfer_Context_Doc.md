# ⚠️ SUPERSEDED — See TRANSFER_Feb21_Session8_CORRECTED.md for current version

# Transfer Context Document — February 20, 2026

## Session Summary
Today's session (across multiple chats due to compaction/crashes) rebuilt and enhanced two of three presentation decks for David's upcoming philosophy venue talk. The third deck (Implicit vs. Explicit) has not yet been touched.

---

## Deck 1: Article Eater (COMPLETE — V3)
**File:** `02-20_02_Article_Eater_24slides_V3.pptx`
**Build script:** `build_deck1.js` (pptxgenjs, ~82KB)

### What was done (V1→V2→V3):
- **V1 (22 slides):** Full rebuild from scratch using pptxgenjs. Removed all footers ("Kirsh —" running footers). Eliminated standalone Tier 1 frameworks slide. Combined 10 theoretical frameworks with derivation example. Rewrote Quinean Web slide with clearer mechanism-chain visualization. Rewrote daylight cascade slide with full mechanism chain.
- **V2 (22 slides):** Spacing/layout fixes throughout.
- **V3 (24 slides):** Removed Expert Panels slide (method not to be shared at this venue). Added 4 new slides from V5 docx paper:
  - **Slide 12 — Window Paradox:** One element activates 5 templates; net effect reverses seasonally (Prediction 9). Same window at same desk: positive in winter, negative in midsummer.
  - **Slide 13 — Nature Photos vs Real Nature:** Mechanism decomposition explains Kahn et al. (2008) effect size difference. What photos capture vs. what they miss.
  - **Slide 14 — Cross-Modal Compensation:** Quiet room needs MORE visual complexity. Three commitments beyond PP. Goldilocks Theory prediction.
  - **Slide 15 — Argumentation with Teeth:** Multi-channel hospital intervention d≈0.6–0.9. Gap: T055 acoustics highest credence but NOT addressed. VOI and defeasibility.

### Design system:
- Deep navy dark slides (title/closing), white content slides
- Card-based layout with left-border color coding
- Color palette: navy `0F1B2D`, accent1 `1B4F72`, accent2 `6B4226`, accent3 `2E7D32`, accent4 `5B2C6F`, accent5 `C2185B`
- Font: Georgia headers, Calibri body
- All 23 content slides have speaker notes

### Known issues:
- Nature Photos right card header has minor LibreOffice rendering overlap at 0.35" clearance — displays correctly in PowerPoint

---

## Deck 2: Goldilocks Principle (COMPLETE — V3)
**File:** `02-20_03_Goldilocks_Principle_41slides_V3.pptx`
**Build script for new slides:** `build_goldilocks_new.js`
**Merge script:** `merge_slides.py`

### What was done (V2→V3):
Original V2 was 37 slides (user-uploaded `02-19_02_Goldilocks_Principle_Presentation_V2.pptx`). Added 4 new slides inserted after slide 24 (Dark Room / Prospect-Refuge), creating a new argumentative block:

- **Slide 25 — The Kidd & Hayden Problem:** Their curiosity inverted-U uses infants/monkeys/rats (implicit processing only). Three problems for adults: (1) adults override implicit inverted-U via explicit goals/metacognition; (2) adult "implicit" processing operates on higher-level info (model selection, architectural grammar, not just spatial frequencies); (3) inverted-U WIDENS with expertise, shifting Goldilocks rightward. Infant curve is a floor, not a ceiling.
- **Slide 26 — Two Processing Channels:** Implicit channel (autonomic, affective, PE, attentional capture = what Kidd & PP capture) + Explicit channel (aesthetic judgment, semantic meaning, cultural norms, deliberate engagement = what they miss). Cultural set-point shifts may be partly explicit. Patient response is BOTH implicit AND explicit.
- **Slide 27 — Why Others Can't:** PP is subpersonal (dark room problem). SRT excludes cognition by design. Berlyne is stimulus-centered. ART requires effortless engagement. Goldilocks can incorporate explicit processing because it's *normative* — prescribes an optimum that includes what the person *thinks*.
- **Slide 28 — Cognitive Niche Engineering:** Clark & Chalmers extended mind → extended system has optimal operating parameters → design IS cognitive niche engineering → feedback loop (cultures construct niches → niches shape people → people reconstruct niches). Varanasi = cognitive niche in dynamic equilibrium.

### Method:
- New slides built with pptxgenjs (`build_goldilocks_new.js`)
- Merged into V2 using python-pptx (`merge_slides.py`) with XML reordering
- Same color palette/design as existing V2 deck
- All 4 new slides have full speaker notes

### Slide structure (41 total):
1-3: Title, Core Claim, Everyday Spaces
4-12: Evidence (7 channels with examples)
13-19: Berlyne's Framework (with examples)
20-24: PP Strengths & Limitations (with examples)
**25-28: NEW — Explicit Processing & Cognitive Niche block**
29-31: India Fieldwork
32-40: Applications (hospitals, offices, cross-modal, dynamic)
41: Closing summary

---

## Deck 3: Implicit vs. Explicit PP (NOT YET TOUCHED)
**Source:** `03_Implicit_vs_Explicit_PP_10min.pptx` (in uploads)
**Status:** No modifications requested yet. This is a 10-minute companion talk.

---

## Source Materials (in uploads)
- `02-18_01_Article_Eater_Philosopher_Presentation_V5.docx` — Full paper with all predictions, mechanism chains, template descriptions
- `02-18_02_article_eater_architecture_V4.jsx` — React component showing system architecture
- `02-19_01_Goldilocks_Principle_Article.docx` — Full Goldilocks paper (7 sections, references with GS counts)
- `02-19_02_Goldilocks_Principle_Presentation_V2.pptx` — Base Goldilocks deck
- `03_Implicit_vs_Explicit_PP_10min.pptx` — Third deck, unmodified

## Outputs Delivered
1. `02-20_01_Article_Eater_22slides_V1.pptx`
2. `02-20_01_Article_Eater_22slides_V2.pptx`
3. `02-20_02_Article_Eater_24slides_V3.pptx` ← current Article Eater
4. `02-20_03_Goldilocks_Principle_41slides_V3.pptx` ← current Goldilocks

---

## Key Intellectual Context for This Venue (Philosophy Audience)

### The central argument threading all three talks:
1. **Article Eater:** Compositional mechanistic reasoning generates testable predictions by chaining templates (each grounded in neuroscience). The system doesn't just describe — it derives novel, falsifiable predictions with effect sizes. Standout: window paradox (seasonal reversal), nature photos mechanism decomposition, cross-modal compensation.

2. **Goldilocks:** The inverted-U is not just Berlyne revisited — it's multi-channel, task-dependent, culturally parameterized, and normatively loaded. PP provides the best mechanism but can't explain the normative, task-specific, cultural, or explicit-processing features. The NEW slides (25-28) argue that the Goldilocks principle is uniquely able to incorporate explicit processing (because it's normative, not purely mechanistic) — PP, SRT, Berlyne, and ART all cannot without undermining their theoretical commitments. The cognitive niche argument (Clark & Chalmers) elevates this from applied design to philosophy of mind.

3. **Implicit vs. Explicit PP:** (Not yet revised) — 10-minute talk on how PP handles implicit vs. explicit processing channels.

### Recurring themes David wants emphasized:
- Explicit processing as a distinctive advantage of Goldilocks over competing frameworks
- The Kidd & Hayden limitation (infants/animals → can't generalize to adult explicit processing)
- Cultural parameterization (India fieldwork) as evidence against universal set-points
- Normative force: Goldilocks PRESCRIBES, PP only DESCRIBES
- Cross-modal compensation as a design-relevant prediction no other framework makes

---

## Technical Notes
- All decks built/modified using **pptxgenjs v4.0.1** (Node.js)
- Slide merging done via **python-pptx** with XML element manipulation
- QA rendered via **LibreOffice → PDF → pdftoppm** (minor rendering differences from PowerPoint expected)
- Widescreen 10" × 5.625" format throughout
- David's naming convention: `MM-DD_seq_Description_Version.ext`
