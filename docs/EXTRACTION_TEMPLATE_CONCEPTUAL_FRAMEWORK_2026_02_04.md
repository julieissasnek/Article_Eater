# ⚠️ SUPERSEDED — See (newer version exists) for current version

# CONCEPTUAL FRAMEWORK EXTRACTION TEMPLATE v1.0

**Version**: 1.0.0
**Date**: February 4, 2026
**Derived From**: Panel discussion on non-causal theoretical contributions
**Panel Review**: Pearl, Cartwright, Simon, Bates, Kaplan

---

## PURPOSE

Conceptual framework papers provide **new ways of thinking** without necessarily proposing causal structures or falsifiable predictions. They uniquely contribute:
- New vocabulary and term definitions
- Conceptual distinctions (what must NOT be conflated)
- Taxonomy structures and organizing principles
- Integration of previously unconnected ideas
- Metatheoretical guidance on how to think about a domain

**These papers feed the TAXONOMY and TERM HARMONIZATION systems, not the BN structure directly.**

---

## WHAT THIS TEMPLATE CAPTURES

| Contribution Type | Output | System Fed |
|-------------------|--------|------------|
| New terms/vocabulary | `term_definition` rules | `outcome_lookup.json`, `environment_lookup.json` |
| Conceptual distinctions | `conceptual_constraint` rules | Term harmonization |
| Taxonomy structures | `taxonomy_structure` rules | Hierarchy definitions |
| Framework organization | `framework` rules | Research organization |
| Bridge grounding | `bridge_warrant` signals | `bridge_warrants.py` |
| Research framing | `research_direction` | VOI signals |

## WHAT THIS TEMPLATE DOES NOT CAPTURE

- Effect sizes (no empirical data)
- Causal edges (not proposed)
- CPD hints (no quantitative claims)
- Falsifiable predictions (may not be offered)

**For papers that DO propose causal structures, use the THEORETICAL template instead.**

---

## HUMAN-READABLE OUTPUT STRUCTURE

When constructing the human-readable extraction document for a **conceptual framework paper**, follow this structure:

### 1. INTRODUCTION SECTION

**Structure**: Conceptual Problem + Why New Framework + Positioning

```
## Introduction

**Conceptual Problem**: [What conceptual confusion or gap exists?]

**Why This Framework**:
- Current vocabulary is: [Inadequate / Conflated / Missing distinctions]
- This creates problems: [What goes wrong without this framework?]
- This framework provides: [What new conceptual resources?]

**Type of Contribution**:
[ ] New vocabulary/terms
[ ] Conceptual distinction
[ ] Taxonomy/organization
[ ] Integration of domains
[ ] Metatheoretical guidance
[ ] Reconceptualization

**Relationship to Existing Frameworks**:

| Existing Framework | Relationship |
|-------------------|--------------|
| [Framework A] | Extends / Replaces / Complements / Subsumes |
```

### 2. CORE CONCEPTUAL CONTRIBUTION

**Structure**: Key Terms → Distinctions → Organizing Principles

```
## Core Conceptual Contribution

### New Terms Introduced

| Term | Definition | Why Needed | Replaces/Distinguishes From |
|------|------------|------------|----------------------------|
| [Term 1] | [Definition] | [Gap it fills] | [Old term or conflation] |

### Key Distinctions

| Distinction | Category A | Category B | Why It Matters |
|-------------|------------|------------|----------------|
| [Name] | [Definition A] | [Definition B] | [Consequence of conflating] |

**Example of conflation problem**:
> [Concrete example of what goes wrong when distinction isn't made]

### Organizing Principles

**Framework Structure**:
```
[Visual representation of how concepts relate]

    PARENT CONCEPT
         │
    ┌────┴────┐
    │         │
  TYPE A    TYPE B
    │
  ┌─┴─┐
  │   │
 a1   a2
```

**Organizing Logic**: [What principle organizes these relationships?]
```

### 3. IMPLICATIONS SECTION

**Structure**: For Research → For Measurement → For Theory

```
## Implications

### For Research Design

| Old Approach | Problem | New Approach (per framework) |
|--------------|---------|------------------------------|
| [Old way] | [Why problematic] | [Framework's recommendation] |

### For Measurement

| Construct | Old Operationalization | Problem | Recommended Operationalization |
|-----------|----------------------|---------|-------------------------------|
| [Construct] | [Old measure] | [What it misses] | [Better measure] |

### For Theory Building

| Theoretical Question | Framework's Guidance |
|---------------------|---------------------|
| [Question] | [How to think about it] |

### What Questions Become Askable

This framework enables these new questions:
1. [Question 1] — Previously not articulable because [reason]
2. [Question 2] — Previously conflated with [other question]
```

### 4. DISCUSSION SECTION

**Structure**: Comparison → Limitations → Adoption Implications

```
## Discussion

### Comparison to Alternative Frameworks

| Alternative | Agreement | Disagreement | This Framework's Advantage |
|-------------|-----------|--------------|---------------------------|
| [Alternative] | [Shared] | [Differs] | [Why better] |

### Limitations of This Framework

| Limitation | Impact | Acknowledged? |
|------------|--------|---------------|
| [Limitation] | [Effect] | Yes/No |

### What This Framework Does NOT Address

1. ❌ [Out of scope 1]
2. ❌ [Out of scope 2]

### Adoption Implications

**If we adopt this framework**:
- Must revise: [What existing concepts need revision]
- Must distinguish: [What previously conflated things must be separated]
- Enables: [What new inferences become possible]
- Constrains: [What old inferences become invalid]
```

---

## TAXONOMY CONTRIBUTION GUIDANCE

**For new terms**, capture:

| Element | Required |
|---------|----------|
| Term name | ✅ |
| Definition (author's) | ✅ |
| Definition (canonical) | If differs from author's |
| Parent concept | For hierarchy |
| Sibling concepts | What it's distinguished from |
| Antonyms | For conflict detection |
| Synonyms | For term harmonization |

**For distinctions**, capture:

| Element | Required |
|---------|----------|
| Distinction name | ✅ |
| Category A definition | ✅ |
| Category B definition | ✅ |
| Mutual exclusivity? | Are A and B exclusive? |
| Exhaustive? | Do A and B cover all cases? |
| Diagnostic criteria | How to tell A from B |

---

## RULE CONVERSION: FROM FRAMEWORK TO QUINEAN WEB

Conceptual framework papers produce rules that update the **taxonomy and term systems**, not the BN structure directly.

### Rule Types from Conceptual Frameworks

| Framework Element | → Rule Type | Purpose |
|-------------------|-------------|---------|
| New term | `term_definition` | Add to vocabulary |
| Distinction | `conceptual_constraint` | Prevent conflation |
| Taxonomy structure | `taxonomy_structure` | Organize hierarchy |
| Framework | `framework` | Document organization |
| Bridge grounding | `bridge_warrant` | License transfer |

---

### COMPLETE CONVERSION EXAMPLES

**Example 1: New Term → Term Definition Rule**

*From Kirsh & Maglio (1994) on epistemic actions*:
```yaml
term:
  name: "epistemic_action"
  definition: "Physical action whose primary purpose is to change
               one's own computational state rather than the world"
  distinguishes_from: "pragmatic_action"
  examples: ["rotating Tetris piece to see if it fits",
             "pointing while counting"]
```

*Converted to rule*:
```yaml
rules:
  - rule_id: "kirsh_1994_term1"
    rule_type: "term_definition"

    term:
      name: "epistemic_action"
      canonical_id: "CONCEPT_EPISTEMIC_ACTION"

    definition:
      author: "Physical action whose primary purpose is to change
               one's own computational state rather than the world"
      canonical: null  # Author's definition is canonical

    taxonomy:
      parent: "ACTION"
      siblings: ["PRAGMATIC_ACTION"]
      children: []

    distinguishes_from:
      - term: "pragmatic_action"
        distinction: "Purpose is world-changing vs. mind-changing"
        diagnostic: "Would action be useful if world-state didn't change?"

    synonyms: ["complementary action", "cognitive action"]
    antonyms: ["pragmatic_action"]

    examples:
      positive: ["rotating Tetris piece mentally", "pointing while counting"]
      negative: ["moving Tetris piece to final position"]

    source_paper: "kirsh_maglio_1994"
    ae_confidence: 0.85  # Well-defined, influential

    # What this enables in the system
    system_implications:
      adds_to: "outcome_lookup.json"
      enables_coding: "Actions can be coded as epistemic vs. pragmatic"
      prevents_conflation: "All actions are NOT equivalent"
```

**Example 2: Conceptual Distinction → Constraint Rule**

*From attention literature distinguishing attention from awareness*:
```yaml
distinction:
  name: "attention_awareness_distinction"
  category_a:
    name: "attention"
    definition: "Selection mechanism for processing"
  category_b:
    name: "awareness"
    definition: "Conscious access to content"
  why_matters: "Can have attention without awareness (subliminal priming)
                and awareness without attention (inattentional blindness shows
                lack of awareness despite attention elsewhere)"
```

*Converted to rule*:
```yaml
rules:
  - rule_id: "koch_2006_distinction1"
    rule_type: "conceptual_constraint"

    constraint_type: "must_distinguish"

    concepts:
      - concept_a:
          name: "attention"
          canonical_id: "PROCESS_ATTENTION"
          definition: "Selection mechanism for processing"
      - concept_b:
          name: "awareness"
          canonical_id: "STATE_AWARENESS"
          definition: "Conscious access to content"

    relationship:
      mutually_exclusive: false  # Can have one without other
      exhaustive: false  # Other states exist

    diagnostic_criteria:
      a_without_b: "Subliminal priming: attention to stimulus, no awareness"
      b_without_a: "Gist perception: aware of scene, attention elsewhere"

    conflation_consequences:
      if_conflated: "Cannot explain dissociations in clinical/experimental data"
      errors_caused: ["Misinterpreting blindsight", "Confusing attention training with awareness training"]

    system_implications:
      coding_rule: "Code attention and awareness as SEPARATE variables"
      invalid_operations: "Do not average across attention/awareness measures"

    ae_confidence: 0.90  # Strong empirical support for dissociation
```

**Example 3: Taxonomy Structure → Taxonomy Rule**

*From Kaplan's ART components*:
```yaml
taxonomy:
  parent: "RESTORATIVE_QUALITY"
  children: ["BEING_AWAY", "FASCINATION", "EXTENT", "COMPATIBILITY"]
  relationship: "components"  # All four contribute
  organizing_principle: "Four necessary conditions for restoration"
```

*Converted to rule*:
```yaml
rules:
  - rule_id: "kaplan_1995_taxonomy1"
    rule_type: "taxonomy_structure"

    structure:
      parent:
        name: "restorative_quality"
        canonical_id: "ENV_RESTORATIVE_QUALITY"
        definition: "Environmental quality that enables attention restoration"

      children:
        - name: "being_away"
          canonical_id: "ENV_BEING_AWAY"
          definition: "Conceptual/physical distance from routine demands"
        - name: "fascination"
          canonical_id: "ENV_FASCINATION"
          definition: "Involuntary attention engagement"
        - name: "extent"
          canonical_id: "ENV_EXTENT"
          definition: "Scope and coherence sufficient for exploration"
        - name: "compatibility"
          canonical_id: "ENV_COMPATIBILITY"
          definition: "Match between environment affordances and purposes"

      relationship_type: "components"  # Not subtypes

    properties:
      mutually_exclusive: false  # Environment can have multiple
      exhaustive: true  # These are THE four (per ART)
      necessary: "all_required"  # For full restoration
      sufficient: "jointly"  # All four together → restoration

    source_theory: "Attention Restoration Theory"
    source_paper: "kaplan_1995"

    ae_confidence: 0.75  # Influential but components debated
```

**Example 4: Framework Organization → Framework Rule**

*From distributed cognition framework*:
```yaml
framework:
  name: "Distributed Cognition"
  core_claim: "Cognitive processes extend beyond individual brains
               to include body, tools, and social structures"
  components:
    - "internal_representations"
    - "external_representations"
    - "coordination_processes"
  organizing_principle: "Cognition is computation over representations
                         regardless of their physical substrate"
```

*Converted to rule*:
```yaml
rules:
  - rule_id: "hutchins_1995_framework1"
    rule_type: "framework"

    framework:
      name: "Distributed Cognition"
      canonical_id: "FRAMEWORK_DISTCOG"

    core_proposition:
      statement: "Cognitive processes extend beyond individual brains"
      type: "metatheoretical"
      falsifiable: false  # Framework, not hypothesis

    components:
      - name: "internal_representations"
        role: "Traditional locus of cognition"
      - name: "external_representations"
        role: "Cognitive artifacts, inscriptions, tools"
      - name: "coordination_processes"
        role: "How internal/external are coordinated"

    organizing_principle: "Unit of analysis is the cognitive system,
                           not the individual"

    methodological_implications:
      unit_of_analysis: "Task system, not person"
      must_include: "Tools, artifacts, environment"
      invalid_to: "Study cognition as purely internal"

    enables_questions:
      - "How do cognitive artifacts reduce mental load?"
      - "How does environment structure cognition?"

    disables_questions:
      - "What's the purely internal process?" (Ill-formed per framework)

    relationship_to_theories:
      extends: ["situated_cognition", "activity_theory"]
      contradicts: ["classical_cognitivism"]

    ae_confidence: 0.70  # Influential but contested
```

**Example 5: Bridge Warrant Grounding → Bridge Rule**

*From evolutionary psychology grounding*:
```yaml
bridge_grounding:
  claim: "Human responses to nature evolved in savanna environments,
          so findings about savanna-like features should transfer
          to modern humans"
  source_domain: "ancestral_environment"
  target_domain: "modern_humans"
  warrant_type: "evolutionary_continuity"
```

*Converted to rule*:
```yaml
rules:
  - rule_id: "orians_2001_bridge1"
    rule_type: "bridge_warrant"

    bridge:
      name: "savanna_hypothesis_bridge"

      source_domain:
        name: "ancestral_environment_responses"
        description: "Human responses to features common in EEA"

      target_domain:
        name: "modern_human_responses"
        description: "Contemporary humans in any environment"

      bridge_type: "EVOLUTIONARY"  # New type for frameworks

      warrant:
        claim: "Evolved preferences are conserved across time"
        mechanism: "Genetic inheritance of perceptual/affective responses"
        assumption: "Relevant selection pressures were consistent"

      confidence_factors:
        if_feature_was_fitness_relevant: 0.70
        if_feature_is_universal: 0.75
        if_response_is_automatic: 0.65

      limitations:
        - "Applies only to features present in EEA"
        - "Cultural variation may override"
        - "Learning can modify responses"

    ae_confidence: 0.60  # Plausible but hard to test directly
```

---

### CONFIDENCE SCORING FOR CONCEPTUAL FRAMEWORKS

| Factor | Impact | Rationale |
|--------|--------|-----------|
| **Adoption/influence** | | |
| Widely adopted in field | +0.15 | Community validation |
| Contested | -0.10 | Uncertain value |
| Novel/untested | 0 | Unknown |
| **Empirical grounding** | | |
| Distinctions empirically validated | +0.10 | Not just stipulation |
| Purely conceptual | 0 | Coherence only |
| **Clarity** | | |
| Clear definitions | +0.05 | Usable |
| Vague/ambiguous | -0.10 | Hard to apply |
| **Productivity** | | |
| Has enabled research | +0.10 | Proven utility |
| No track record | 0 | Unknown |

**Base confidence**: 0.65 for conceptual framework
**Range**: 0.45 (contested/vague) to 0.90 (influential/validated)

---

# THE TEMPLATE

---

## HEADER & METADATA

*Auto-populated from Zotero/BibTeX:*

| Field | Value |
|-------|-------|
| Citation (APA) | |
| DOI | |
| Title | |
| Authors | |
| Year | |
| Journal/Venue | |
| Abstract | [verbatim] |

*Manual classification:*

| Field | Value |
|-------|-------|
| Article type | CONCEPTUAL FRAMEWORK |
| Contribution type | [ ] Vocabulary [ ] Distinction [ ] Taxonomy [ ] Integration [ ] Metatheory [ ] Reconceptualization |
| Source depth | [ ] Full text [ ] Abstract only [ ] Metadata only |

---

## OUR SUMMARY

- Plain-language summary of conceptual contribution (1-3 sentences)
- Key terms or distinctions introduced
- What this enables that wasn't possible before

---

## CONCEPTUAL PROBLEM ADDRESSED

**Q: What conceptual confusion or gap does this address?**

| Element | Description |
|---------|-------------|
| Current state | [What's wrong with current thinking?] |
| Consequence | [What problems does this cause?] |
| This paper provides | [What new conceptual resources?] |

---

## NEW TERMS INTRODUCED

**Q: What new vocabulary does this paper offer?**

| Term | Author's Definition | Parent Concept | Distinguished From |
|------|--------------------|-----------------|--------------------|
| | | | |

**Q: Why is each term needed?**

| Term | Gap It Fills | What Goes Wrong Without It |
|------|--------------|---------------------------|
| | | |

---

## KEY DISTINCTIONS

**Q: What distinctions does this paper draw?**

| Distinction | Category A | Category B |
|-------------|------------|------------|
| | Definition: | Definition: |
| | Examples: | Examples: |

**Q: Are categories mutually exclusive?** Yes / No / Partial

**Q: Are categories exhaustive?** Yes / No

**Q: How do you tell A from B?**

| Diagnostic | A | B |
|------------|---|---|
| [Criterion 1] | [A's value] | [B's value] |

**Q: What goes wrong if conflated?**

| Conflation Error | Consequence |
|------------------|-------------|
| | |

---

## TAXONOMY STRUCTURE

**Q: What organizational structure does this propose?**

```
[Draw hierarchy or relationship structure]
```

| Element | Type | Relationship to Parent |
|---------|------|----------------------|
| | Superordinate / Coordinate / Subordinate | Is-a / Part-of / Component-of / Instance-of |

**Q: What organizing principle determines this structure?**

---

## FRAMEWORK COMPONENTS

**Q: What are the core components of this framework?**

| Component | Role | Necessary? | Sufficient? |
|-----------|------|------------|-------------|
| | | Yes/No | Alone / Jointly |

**Q: What is the organizing principle?**

---

## IMPLICATIONS

### For Research Design

| Current Practice | Problem | Recommended Practice |
|------------------|---------|---------------------|
| | | |

### For Measurement

| Construct | Current Operationalization | Problem | Recommended |
|-----------|---------------------------|---------|-------------|
| | | | |

### For Theory

| Question | How Framework Guides Thinking |
|----------|------------------------------|
| | |

---

## QUESTIONS ENABLED

**Q: What questions become askable with this framework?**

1. [Question] — Previously couldn't ask because [reason]
2. [Question] — Previously conflated with [other question]

---

## COMPARISON TO ALTERNATIVES

| Alternative | Agreement | Disagreement | This Framework's Advantage |
|-------------|-----------|--------------|---------------------------|
| | | | |

---

## OUR ASSESSMENT

**Strengths**
- [What this framework does well]

**Limitations**
- [What it doesn't address]

**Clarity**: Clear / Moderate / Vague
**Influence**: Widely adopted / Growing / Contested / Novel
**Empirical grounding**: Validated / Partially / Conceptual only

---

## Q&A SECTION

**Q: What new terms does this introduce?**
A:

**Q: What must NOT be conflated?**
A:

**Q: What does this framework enable?**
A:

**Q: What questions does this NOT address?**
A:

**Q: Should we adopt this framework?**
A: [Assessment of utility for Article Eater]

---

## MACHINE-READABLE DATA

```yaml
# ============================================
# HEADER
# ============================================
paper_id: ""
doi: ""
extraction_date: "YYYY-MM-DD"
article_type: "conceptual_framework"
contribution_type: "vocabulary|distinction|taxonomy|integration|metatheory|reconceptualization"
source_depth: "full_text|abstract|metadata"

# ============================================
# CONCEPTUAL PROBLEM
# ============================================
problem:
  current_state: ""
  consequence: ""
  this_provides: ""

# ============================================
# NEW TERMS (Bates)
# ============================================
terms:
  - term: ""
    canonical_id: ""
    definition_author: ""
    definition_canonical: ""
    parent_concept: ""
    distinguished_from: []
    synonyms: []
    antonyms: []
    examples_positive: []
    examples_negative: []
    why_needed: ""

# ============================================
# DISTINCTIONS
# ============================================
distinctions:
  - name: ""
    category_a:
      name: ""
      canonical_id: ""
      definition: ""
      examples: []
    category_b:
      name: ""
      canonical_id: ""
      definition: ""
      examples: []
    mutually_exclusive: true|false
    exhaustive: true|false
    diagnostic_criteria:
      - criterion: ""
        a_value: ""
        b_value: ""
    conflation_consequences: []

# ============================================
# TAXONOMY STRUCTURE
# ============================================
taxonomy:
  parent:
    name: ""
    canonical_id: ""
  children:
    - name: ""
      canonical_id: ""
      relationship: "is_a|part_of|component_of|instance_of"
  organizing_principle: ""
  mutually_exclusive: true|false
  exhaustive: true|false

# ============================================
# FRAMEWORK
# ============================================
framework:
  name: ""
  canonical_id: ""
  core_proposition: ""
  components:
    - name: ""
      role: ""
      necessary: true|false
      sufficient: "alone|jointly|neither"
  organizing_principle: ""
  methodological_implications:
    unit_of_analysis: ""
    must_include: []
    invalid_to: []

# ============================================
# IMPLICATIONS
# ============================================
implications:
  for_research:
    - current: ""
      problem: ""
      recommended: ""
  for_measurement:
    - construct: ""
      current: ""
      problem: ""
      recommended: ""
  for_theory:
    - question: ""
      guidance: ""

# ============================================
# QUESTIONS ENABLED
# ============================================
questions_enabled:
  - question: ""
    previously: "not_articulable|conflated_with"
    reason: ""

# ============================================
# RULES GENERATED
# ============================================
rules:
  # Term definitions
  - rule_id: ""
    rule_type: "term_definition"
    term:
      name: ""
      canonical_id: ""
    definition:
      author: ""
      canonical: ""
    taxonomy:
      parent: ""
      siblings: []
      children: []
    ae_confidence:

  # Conceptual constraints
  - rule_id: ""
    rule_type: "conceptual_constraint"
    constraint_type: "must_distinguish"
    concepts:
      - name: ""
        canonical_id: ""
      - name: ""
        canonical_id: ""
    conflation_consequences: []
    coding_rule: ""
    ae_confidence:

  # Taxonomy structures
  - rule_id: ""
    rule_type: "taxonomy_structure"
    parent:
      name: ""
      canonical_id: ""
    children: []
    relationship_type: "subtypes|components|instances"
    ae_confidence:

  # Framework rules
  - rule_id: ""
    rule_type: "framework"
    name: ""
    components: []
    organizing_principle: ""
    ae_confidence:

# ============================================
# QUALITY ASSESSMENT
# ============================================
quality:
  clarity: "clear|moderate|vague"
  influence: "widely_adopted|growing|contested|novel"
  empirical_grounding: "validated|partial|conceptual_only"
  our_confidence:
```

---

## CHANGELOG

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-04 | Initial template for conceptual framework papers |

---

**END OF CONCEPTUAL FRAMEWORK TEMPLATE**
