# Mechanism QA — Future To-Do List

## Expert Vetting

- [ ] **Neuroscientist review of mechanism chains** — Have a team of 2–3 neuroscientists (environmental psychophysiology, olfactory neuroscience, attention/cognitive science) review ALL seeded mechanism chains for:
  - **Completeness**: are there missing steps in the causal chain?
  - **Accuracy**: is each step correctly described (neural pathway, receptor type, timing)?
  - **Reliability**: what is the evidence base for each step? RCT vs. observational vs. theoretical?
  - **Boundary conditions**: under what conditions does each step fail or reverse?
  - Deliverable: annotated chain diagrams with confidence ratings per link

- [ ] **Panel cross-reference** — For each mechanism chain, link back to the specific panel report sections that justify each step, using the `panel_reasoning_excerpt` field in templates

## Coverage Expansion

- [ ] **Seed remaining high-priority stimulus variables** — The `discover_modality_gaps.py` script identified 305 unseeded stimulus variables from templates. Priority order:
  - `nature_scene_exposure` (4× across templates)
  - `musical_structure` (3×) — acoustic environment
  - `ambient_noise_level` (2×) — DT1 pathway
  - `environmental_odor_molecules` (2×) — olfactory pathway
  - `cognitive_map_quality` (2×) — ART/wayfinding pathway

- [ ] **Seed remaining outcome variables** — 295 unseeded outcome variables. Priority:
  - `felt_emotion` (5×)
  - `CT_afferent_firing_rate` (2×) — haptic/affective touch
  - `tpn_deactivation` / `dmn_re_engagement` (2×each) — DT1 pathway outcomes

- [ ] **Add water, stone, daylight stimulus bundles** — Currently only wood (6 channels) and plants (2 channels) are seeded. Water (visual shimmer, acoustic, thermal), stone (haptic, visual, acoustic), and daylight (circadian, visual acuity, mood) all need modality-conditional channels

## Narrative Quality

- [ ] **Conditional modality ordering** — Currently visual is always first; consider query-adaptive ordering (if query mentions "smell", lead with olfactory)

- [ ] **Encounter scenario generator** — Given a specific architectural scenario (e.g., "open-plan office with wood panelling and potted plants"), automatically determine which stimulus channels are active (based on encounter conditions) and render only the relevant chains

- [ ] **Cross-material comparison** — Answer "do wood and plants share the same mechanism?" by showing overlapping and distinct channels side-by-side

## LLM Integration

- [ ] **Cheaper model for panel summarization** — Use gemini-1.5-flash or gpt-4o-mini for extractive summarization of panel docs; reserve full model for chain reasoning validation. Add `--model` flag to extraction scripts

- [ ] **LLM-assisted gap filling** — Use LLM to read panel docs and propose new mechanism nodes/constraints, then have human expert vet before seeding

## Progressive Disclosure

- [ ] **Full web UI for clickable deepening** — Current `<details>` tags work in HTML-rendering contexts; build a proper interactive viewer where each step and outcome is clickable, showing context-specific deeper explanations

- [ ] **Provenance drill-down** — Clicking on any mechanism step should show: (1) the panel reasoning excerpt, (2) the source papers, (3) the template it came from

- [ ] **Confidence annotations** — Show credence values and uncertainty ranges for each step, with tooltip explanations of what the numbers mean

## QA & Explanation — Next Steps

- [ ] **Query-adaptive modality ordering** — If the user's question mentions "smell" or "scent", lead with the olfactory chain. Detect query keywords and reorder encounter sections to match
- [ ] **Truncation-aware labelling** — Many node content strings are too long for the summary line. Add a `display_name` field to mechanism nodes so the label line reads clean without ever showing "..."
- [ ] **Negative-case explanations** — "Why doesn't a photograph of wood produce the same effect?" should render the chains with missing modality channels marked as INACTIVE, showing which pathways break
- [ ] **Dose–response rendering** — For outcome nodes with latency data, render a timeline diagram showing when each biomarker starts moving (GSR 30s → HR 2min → cortisol 15min)
- [ ] **Comparative queries** — "How does wood compare to plants?" should render two material columns side-by-side with shared vs distinct channels highlighted
- [ ] **Mechanism chain validation tests** — Unit tests that assert each chain traverses correctly and produces expected step count, preventing seeder regressions
- [ ] **Olfactory safety classification examples** — Expand the classification node content with more specific examples: specific predator urine compounds, specific food decay signals, specific smoke composition indicators
- [ ] **Hippocampal modulation rendering** — When the user asks "why does wood smoke sometimes feel safe and sometimes alarming?", the explanation should walk through the associative memory modulation path
- [ ] **Entry-sentence rewriting** — The opening sentence of each encounter section currently shows the entry node's content truncated to first sentence. Rewrite these to be narrative-appropriate (e.g., "The volatile compounds in the wood — alpha-pinene, cedrol — reach the olfactory bulb...")
- [ ] **ART visual chain detail** — The visual/ART chain currently jumps from "biophilic stimulus" to "soft fascination" without explaining the fractal processing step. Add a `visual_fractal_processing` node analogous to the olfactory safety classification
