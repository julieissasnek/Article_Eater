---
name: academic-presentation
description: |
  **Academic Presentation Design Service**: Content strategy, narrative architecture, and visual design principles for academic, teaching, and science communication presentations. Grounded in research from Tufte, Mayer, Feynman, Pinker, Rosling, and Doumont.
  - MANDATORY TRIGGERS: presentation design, slide content, academic talk, lecture slides, conference talk, research presentation, science communication slides, teaching presentation
  - USE ALONGSIDE the pptx skill (which handles technical creation). This skill handles WHAT to put on slides and WHY. The pptx skill handles HOW to build the .pptx file.
---

# Academic Presentation Design Service

**Purpose**: Transform raw intellectual content into presentations that preserve depth while achieving clarity. This service provides the content strategy layer — narrative architecture, evidence display, cognitive load management, and visual rhetoric. Use it alongside the `pptx` skill (which handles the technical .pptx creation).

**When to use**: Before creating any academic, research, teaching, or science communication presentation. Read this FIRST, design your content strategy, THEN use the `pptx` skill for implementation.

---

## Core Philosophy: The Anti-Bullet-Point Manifesto

The default presentation mode — title + bullet points on white background — is the intellectual equivalent of reading your paper aloud. It adds nothing that a printed handout wouldn't provide better. The great science communicators (Feynman, Pinker, Rosling, Tufte) share one trait: they never default to bullets.

The goal is **assertion-evidence structure** (Garner & Alley, 2013): each slide makes a specific claim supported by visual evidence, not a topic label followed by sentence fragments.

### What We're Fighting Against

1. **Bullet-point disease**: Slides that are just indented text. Audiences read ahead, tune out the speaker, and retain nothing (Mayer, 2009).
2. **TED-ification**: Oversimplified narratives with emotional hooks but no intellectual substance. Style over content.
3. **Data-free claims**: Assertions without evidence, mechanisms without data, conclusions without warrants.
4. **Visual noise**: Clip art, gratuitous animations, decorative elements that consume attention without conveying information (Tufte, 2006).

### What We're Building Toward

Presentations where every slide earns its place by advancing an argument, presenting evidence, or scaffolding a difficult concept. Where the visual channel carries information the verbal channel cannot, and vice versa. Where the audience leaves having understood something they didn't before — not just having been entertained.

---

## The Seven Principles

### Principle 1: Assertion-Evidence Structure (Garner, Alley, Tufte)

Every content slide should have:
- **A sentence headline** (not a topic label) that states the slide's claim
- **Visual evidence** that supports the claim (data, diagram, image, comparison)

Bad: "Open Office Results" (topic label)
Good: "Open offices reduce face-to-face interaction by 70%" (assertion)
Better: "Open offices reduce face-to-face interaction by 70%" + chart showing before/after data from Bernstein & Turban (2018)

**Implementation**:
- Title area: 1-2 line assertion in 28-36pt, left-aligned
- Body area: visual evidence (chart, diagram, annotated image, comparison)
- Source citation: small text (10-12pt) at bottom with author/year
- Speaker notes: the full explanation, qualifications, and additional context

### Principle 2: Scaffolded Complexity (Feynman, Bruner)

Feynman's genius was not simplification — it was *layered explanation*. He started with what the audience already knew, built one new concept at a time, and never moved forward until the current layer was solid.

**The Feynman Staircase**:
1. **Anchor**: Connect to something the audience already understands
2. **Introduce one new idea**: Not two, not three — one
3. **Make it concrete**: Show an example before stating the abstraction
4. **Test it**: Present a prediction or consequence the audience can verify
5. **Build**: Use the new idea as a stepping stone to the next

**Implementation**:
- For complex systems: use a "zoom" structure (overview → component → detail → back to overview)
- For theoretical arguments: use the claim-evidence-implication triplet
- For empirical findings: show the phenomenon first, then the explanation
- Number your build steps when accumulating toward a complex conclusion
- Use visual continuity (persistent elements, consistent spatial mapping) to show how new information connects to what came before

### Principle 3: Data-Ink Maximization (Tufte)

Tufte's data-ink ratio: maximize the proportion of ink devoted to data, minimize decorative elements. Every pixel should earn its place.

**Tufte's Rules**:
- Remove chartjunk (3D effects, grid lines, gradient fills, shadows on data elements)
- Use small multiples instead of animation or sequential slides when comparing conditions
- Label data directly instead of using legends (Tufte, 2001)
- Show the data at the highest resolution the audience can absorb

**For Academic Presentations Specifically**:
- Show actual data points, not just bar heights (use strip plots or bee swarm overlays)
- Include confidence intervals or standard errors — your audience can handle them
- When presenting meta-analyses, use forest plots (the standard format exists because it works)
- For effect sizes: show them visually. A Cohen's d of 0.8 means the distributions overlap by ~69%. Show that.

**Implementation**:
- Clean chart backgrounds (white or very light gray, no gradient)
- Thin, muted grid lines (if any) — never darker than the data
- Direct labels on data series (not legends requiring eye movement)
- Remove all default PowerPoint chart decorations (shadows, bevels, 3D)
- Use color functionally: to distinguish groups or highlight key comparisons

### Principle 4: Narrative Threading (Pinker, Sacks)

Pinker's writing advice applies directly to talks: the audience needs a coherent thread connecting every slide. They should always know where they are in the argument and why this slide matters right now.

**The Pinker Thread**:
- Every presentation tells ONE story (even if it has multiple acts)
- Each slide should connect to the previous one via a visible logical link
- The audience should never wonder "why is the speaker showing me this?"
- Use signpost slides sparingly but effectively (not "Outline" slides — those are useless)

**Narrative Structures for Academic Talks**:
1. **Problem → Mechanism → Solution → Evidence → Implications** (empirical work)
2. **Phenomenon → Failed Explanation → Better Explanation → Predictions** (theoretical work)
3. **Question → Approach → Three Key Findings → Synthesis → Open Questions** (dissertation/job talk)
4. **Historical Puzzle → Progressive Refinement → Current State → What's Next** (review/keynote)

**Implementation**:
- Opening slide: pose a QUESTION or show a PHENOMENON (not "My Research")
- Transition slides: brief (one line) stating what the next section addresses and why
- Call-back slides: visually reference earlier slides when building on them (e.g., dim earlier elements while highlighting the new addition)
- Closing slide: return to the opening question and show how the talk answered it

### Principle 5: Cognitive Load Management (Mayer, Sweller)

Mayer's multimedia learning principles are not suggestions — they are experimentally validated design constraints (Mayer, 2009; Clark & Mayer, 2016):

- **Contiguity**: Place text near the graphic it describes (not in a separate text box across the slide)
- **Redundancy**: Do NOT put your full spoken script on the slide. The audience will read it instead of listening, splitting attention and reducing comprehension.
- **Signaling**: Use visual cues (arrows, highlights, numbered steps) to direct attention
- **Segmenting**: Break complex processes into discrete steps, one per slide if necessary
- **Modality**: Use spoken words + graphics, NOT written words + graphics (this is the strongest finding in multimedia learning research)

**The Deadly Sin**: Reading your slides aloud. If the slide contains exactly what you're saying, one channel is redundant and the audience processes neither well.

**Implementation**:
- Slide text: key phrases, labels, and data — NOT full sentences that duplicate your narration
- Speaker notes: your full script (for rehearsal and archive purposes)
- Annotations on diagrams: integrated labels, not separate text boxes
- Maximum 6 distinct visual elements per slide (Miller's 7 +/- 2 applies to visual attention too)
- Complex figures: reveal progressively (build animations), not all at once

### Principle 6: Drama Through Data (Rosling, Kahneman)

Rosling didn't animate data for spectacle — he animated it because temporal revelation creates understanding that static display cannot. The audience experiences the PROCESS of change, not just the endpoint.

**When to Use Temporal Revelation**:
- Time series data (the natural case — show change over time)
- Before/after comparisons (show before, pause, reveal after)
- Surprising results (set up the expectation, then show the data)
- Accumulation arguments (add evidence piece by piece until the conclusion is inescapable)

**When NOT to Use Animation**:
- Bullet points appearing one by one (this is not drama, it's a reading speed limiter)
- Decorative transitions between slides (distracting, not informative)
- Any case where the audience needs to see the full picture to understand the comparison

**Kahneman's Framing Insight**: How you present a number changes what it means. "21% improvement" is abstract. "In a class of 30, that's 6 additional students reaching proficiency" is concrete. Always translate statistics into human-scale consequences.

**Implementation**:
- Large stat callouts (60-72pt) with contextualizing labels below
- Side-by-side or before/after layouts for comparisons
- Progressive data builds for accumulation arguments
- Human-scale translations in speaker notes or subtitle text

### Principle 7: Intellectual Honesty in Visual Rhetoric (Tufte, Mayo)

Academic presentations have a special obligation: the visual rhetoric must not overstate the evidence. This is where popular science communication often fails — the desire to tell a clean story overrides the messiness of actual data.

**Rules**:
- Always show uncertainty (error bars, confidence intervals, credible intervals)
- Always show the full distribution, not just the mean
- Always label axes with units
- Never truncate axes to exaggerate effects (or if you must, make it visually obvious)
- When composing across studies: make the composition EXPLICIT. Show the individual studies, then show the composition, then state the novel inference and label it as such
- Distinguish clearly between: (a) what the data show, (b) what the theory predicts, and (c) what you're proposing

**The Tufte Standard**: Could a thoughtful skeptic reconstruct your argument from your slides alone? If not, they're not carrying enough information.

**Implementation**:
- Use different visual treatments for data (solid), theory (dashed), and speculation (dotted/lighter)
- When citing studies: show n, effect size, and study quality indicator (at minimum)
- For composed arguments: use spatial layout to show which pieces come from which sources
- Include "limitations" or "open questions" slides — they build credibility, not weakness

---

## Slide Type Templates

### Type 1: Title Slide
- Presentation title (36-44pt, bold)
- Subtitle or framing question (18-24pt)
- Author, affiliation, date, venue
- Optional: a single arresting image or data visualization that encapsulates the talk's question
- AVOID: institutional logos cluttering the visual space (put them on the last slide if required)

### Type 2: Assertion-Evidence Slide (the workhorse)
- Sentence headline stating the claim (28-32pt)
- Visual evidence body (chart, diagram, annotated image, comparison)
- Source citation (10-12pt, bottom)
- Speaker notes with full explanation

### Type 3: Mechanism/Process Slide
- Numbered steps or flow diagram
- Spatial layout showing causal flow (left-to-right or top-to-bottom)
- Color coding for different types of elements (input, process, output)
- Each step: brief label + icon or small illustration

### Type 4: Data Comparison Slide
- Side-by-side or before/after layout
- Matched scales and axes for fair comparison
- Highlight the key difference with color or annotation
- Statistical annotation (effect size, p-value, CI) integrated into the chart

### Type 5: Composition/Integration Slide
- Shows how multiple independent findings combine
- Visually distinct sources (color-coded by study/theory)
- The novel inference clearly labeled and visually separated
- Arrow or connection notation showing the logical composition

### Type 6: Signpost/Transition Slide
- One line stating what's next and why
- Optional: visual progress indicator (where are we in the argument?)
- Distinct background color (darker) to signal structural shift
- AVOID: detailed outlines or agendas (these waste time and no one remembers them)

### Type 7: Key Takeaway / Summary Slide
- 2-3 major assertions (not a recap of all slides)
- Each assertion paired with its strongest piece of evidence
- Visual callback to earlier slides where the evidence appeared
- Clear statement of what's new / what the audience should remember

### Type 8: Open Questions / Future Directions Slide
- Genuine open questions (not just "more research needed")
- Specific predictions that would confirm or disconfirm the argument
- Potential collaborations or next experiments
- This slide builds credibility — it shows intellectual honesty

---

## Color and Typography for Academic Context

### Color Principles
- **Functional color**: Every color distinction should encode information (groups, categories, emphasis)
- **Accessible palettes**: Ensure colorblind-safe combinations (avoid red-green as sole distinguisher)
- **Institutional neutrality**: Dark backgrounds (navy, charcoal) convey seriousness; avoid corporate pastels

### Recommended Academic Palettes

| Context | Primary | Secondary | Accent | Data Colors |
|---------|---------|-----------|--------|-------------|
| **Cognitive Science** | `1B2A4A` (midnight) | `F4F4F4` (off-white) | `E8913A` (amber) | `3B82F6`, `10B981`, `F59E0B`, `EF4444` |
| **Neuroscience** | `0F1729` (deep navy) | `E2E8F0` (slate) | `06B6D4` (cyan) | `8B5CF6`, `EC4899`, `14B8A6`, `F97316` |
| **Environmental Psych** | `1A3C34` (forest) | `F0F4F0` (sage white) | `D4A843` (gold) | `2D9CDB`, `27AE60`, `E74C3C`, `9B59B6` |
| **General Academic** | `1E293B` (slate) | `F8FAFC` (near-white) | `3B82F6` (blue) | `10B981`, `F59E0B`, `EF4444`, `8B5CF6` |

### Typography for Readability
- **Headers**: Georgia, Cambria, or Palatino (serif conveys authority in academic context)
- **Body/Labels**: Calibri, Segoe UI, or Source Sans Pro (clean sans-serif for data)
- **Minimum sizes**: Title 32pt, body 18pt, labels 14pt, citations 10pt
- **Back row test**: Will someone 15 meters away be able to read this? If not, increase size.

---

## The Presentation Design Workflow

### Step 1: Argument Architecture (before touching slides)
1. Write your talk as a **3-paragraph abstract**: opening question, method/approach, key findings
2. Identify the **one sentence** the audience should remember (your thesis)
3. Outline the **logical chain**: what must the audience understand at step N to follow step N+1?
4. Count your steps. For a 20-minute talk: 12-15 slides. For 45 minutes: 25-35 slides. For 60 minutes: 30-40 slides.

### Step 2: Storyboard (sketch, not design)
1. For each step in the argument, write a sentence headline
2. Below each headline, note what VISUAL would best support it (chart, diagram, image, comparison, process)
3. Flag where you need data, where you need diagrams, and where a conceptual illustration would help
4. Identify your "anchor slides" — the 3-4 most important slides that carry the core argument

### Step 3: Evidence Assembly
1. Gather data visualizations, figures from papers, photographs
2. For each: can it be used directly (with citation), or does it need to be remade for clarity?
3. Remake figures that are cluttered, low-resolution, or don't match your visual style
4. Ensure every empirical claim has a visual evidence source

### Step 4: Build and Iterate
1. Create slides using the `pptx` skill for technical implementation
2. Apply the seven principles during construction
3. Read through the speaker notes as a continuous narrative — does the argument flow?
4. **Cut ruthlessly**: if a slide doesn't advance the argument, remove it

### Step 5: Rehearsal Check
1. Can you explain each slide in under 90 seconds?
2. Does the transition between slides feel natural (logical connectors)?
3. Are there any slides where you'd say "as you can see..." but the audience can't actually see?
4. Time the full presentation. Academic talks almost ALWAYS run long. Budget 70% of your slot for content, 30% for questions and pacing.

---

## Anti-Patterns to Avoid

1. **The Literature Review Slide**: A slide listing 15 citations in small text. Instead, show 2-3 key studies with visual data and mention the rest verbally.

2. **The Methodology Paragraph**: A slide of dense text describing your methods. Instead, show a visual pipeline/flowchart with brief labels.

3. **The Acknowledgments Slide** (at the start): Nobody needs to see your funding sources before they know what you did. Put acknowledgments at the end.

4. **The Outline Slide**: "First I'll talk about X, then Y, then Z." The audience will forget this in 30 seconds. Instead, use your opening to pose a QUESTION that creates forward momentum.

5. **The Wall of Equations**: Unless your audience is mathematicians, show one equation at a time, build it up, and explain each term with an example.

6. **The Apologetic Slide**: "I know this is hard to read but..." If you know it, fix it. Never present unreadable content.

7. **Decorative Clip Art**: Stock photos of people shaking hands, light bulbs, or arrows. If an image doesn't carry information, it's noise.

---

## Quality Checklist

Before finalizing any academic presentation, verify:

- [ ] Every content slide has a sentence headline (assertion, not topic)
- [ ] Every assertion is supported by visual evidence on the same slide
- [ ] No slide duplicates what the speaker will say verbatim
- [ ] Data visualizations show uncertainty (error bars, CIs)
- [ ] Color serves a functional purpose (not just decoration)
- [ ] Minimum font size is 14pt (nothing smaller)
- [ ] The logical chain from slide 1 to the conclusion is unbroken
- [ ] Speaker notes contain the full narrative
- [ ] Sources are cited (author, year minimum) for all data shown
- [ ] The opening slide poses a question or shows a phenomenon
- [ ] There are no bullet-point-only slides (every slide has a visual element)
- [ ] The "back row test" passes — readable from 15 meters

---

## References

- Clark, R. C., & Mayer, R. E. (2016). *E-learning and the science of instruction* (4th ed.). Wiley.
- Doumont, J.-L. (2009). *Trees, maps, and theorems*. Principiae.
- Garner, J. K., & Alley, M. P. (2013). How the design of presentation slides affects audience comprehension. *International Journal of Engineering Education*, 29(6), 1564-1573.
- Mayer, R. E. (2009). *Multimedia learning* (2nd ed.). Cambridge University Press.
- Mayer, R. E. (2014). *The Cambridge handbook of multimedia learning* (2nd ed.). Cambridge University Press.
- Pinker, S. (2014). *The sense of style: The thinking person's guide to writing in the 21st century*. Viking.
- Reynolds, G. (2019). *Presentation Zen: Simple ideas on presentation design and delivery* (3rd ed.). New Riders.
- Rosling, H., Rosling, O., & Rosling Ronnlund, A. (2018). *Factfulness*. Flatiron Books.
- Sweller, J. (2011). Cognitive load theory. In J. Mestre & B. Ross (Eds.), *Psychology of learning and motivation* (Vol. 55, pp. 37-76). Academic Press.
- Tufte, E. R. (2001). *The visual display of quantitative information* (2nd ed.). Graphics Press.
- Tufte, E. R. (2006). *Beautiful evidence*. Graphics Press.
