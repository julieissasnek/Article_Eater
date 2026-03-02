# Theory Tier Architecture Specification — Updated 2026-03-01

## Purpose

This document defines the multi-level explanatory structure of Article Eater. It is intended as the authoritative reference for the master doc's theory tier section.

---

## The Five Levels

```
T1 ─── 10 Framework Theories ──── neurally grounded, cross-domain
  │         (PP, SN, DP, DT, NM, IC, MS, EC, CB, MSI)
  │
  ├──► T2 ─── ~166 CMR Templates ──── specific mechanism chains
  │         (Arch. Feature → Neural Process → Psych. Outcome)
  │
  │         composed into ▼
  │
  │    Molecules ─── Latent Variables ──── compositional effect bundles
  │         (18 defined; expandable via factor analysis)
  │
  │         ◄── T1.5 is a SUBSET of molecules
  │
  ├──► T1.5 ── 4 Domain Theories ──── author-attributed, formally reduced
  │         (ART=Kaplan, SRT=Ulrich, Biophilia=Wilson, P-R=Appleton)
  │
  └──► T3 ─── Empirical Beliefs ──── ground-level evidence in Web of Belief
            (specific env→outcome claims supported by multiple articles)
```

---

## Tier Definitions

### T1: Framework Theories (10)

Neurally grounded, cross-domain frameworks. The **only** fundamental explanatory level. Every architectural effect must operate through one or more T1 frameworks.

**Admission criteria** (all three required):
1. **Mechanistic specificity** — connects to identified neural substrates
2. **Cross-domain generativity** — generates predictions across multiple architectural domains
3. **Convergent multi-method evidence** — supported by fMRI, EEG, lesion, computational, and behavioral data

| Abbrev | Framework | Example Neural Substrate |
|--------|-----------|--------------------------|
| PP | Predictive Processing | Hierarchical cortical prediction error |
| SN | Spatial Navigation / Cognitive Mapping | Hippocampal place cells, grid cells |
| DP | Dual-Process Evaluation | Amygdala (Sys1) vs dlPFC (Sys2) |
| DT | DMN/TPN Dynamics | Default mode ↔ task-positive switching |
| NM | Neuromodulatory Systems | VTA dopamine, HPA cortisol |
| IC | Interoceptive / Constructionist Affect | Anterior insula, body budget |
| MS | Memory Systems | Hippocampal episodic binding |
| EC | Embodied Cognition | Premotor action simulation |
| CB | Chronobiological Regulation | ipRGC → SCN circadian clock |
| MSI | Multisensory Integration | Superior colliculus, STS |

**Canonical file**: `schemas/theory/tier1_frameworks.json`

---

### T2: CMR Templates (~166 Mechanism Chains)

The atomic unit of mechanistic explanation. Each template encodes one specific causal pathway:

```
Architectural Feature  →  Neural/Cognitive Process  →  Psychological Outcome
     (from_entity)            (activity)                 (change_produced)
```

Every template declares which T1 frameworks it invokes. Templates are composed by molecules.

**Canonical file**: `schemas/theory/tier2_mechanisms.json`
**Data**: `data/templates/*.json`

---

### Molecules: Latent Variables (18, expandable)

**This is the key conceptual update from this session.**

Molecules are **latent variables** — they are not directly observed but inferred from patterns of T2 template co-activation across empirical findings. A molecule defines how a set of mechanism chains combine (additively, synergistically, or as prerequisites) to produce an integrated architectural effect.

**Ontological status**: Molecules occupy a position analogous to latent factors in psychometrics:
- **Observed indicators** = individual template activations in findings
- **Latent factor** = the molecule — a hidden construct explaining template co-occurrence
- **Factor loadings** = the template's contribution weight within the molecule

**Relationship to T1.5**: All T1.5 domain theories *are* molecules, but not all molecules are T1.5. T1.5 = molecules with (a) established authorship, (b) published construct definitions, and (c) canonical citations in the literature. Other molecules are system-defined composites or computationally discovered.

**Discoverability**: New molecules can be found by:
1. Building a template co-occurrence matrix from the finding corpus
2. Running exploratory factor analysis or non-negative matrix factorization
3. Comparing discovered factors against existing hand-defined molecules
4. Naming and validating novel factors as candidate molecules

**Current molecules** (18):
- 4 are T1.5 theories: ART, SRT, Biophilia, Prospect-Refuge
- 14 are system composites: Goldilocks Principle, M_Beauty_Compression, Wayfinding, Creative Environments, Social Architecture, Awe Architecture, Circadian Architecture, Cognitive Load Architecture, Multisensory Design, Allostatic Regulation, M_Rasa, M_Attractor_Transition, M_CCT_Preference, M_Cultural_Valuation

**Canonical file**: `schemas/theory/molecule_taxonomy.json`
**Data**: `data/molecules/*.json`

---

### T1.5: Domain Theories (4)

Phenomenological organizing schemas. They are **explained BY** T1 frameworks, not explanatory themselves. They are a strict subset of molecules with literature provenance.

Each T1.5 theory has:
- A published originator and canonical citations
- Named constructs (e.g., ART's "Soft Fascination," "Being Away")
- Formal reductions showing what % of each construct is explained by T1-grounded templates
- An irreducible residual acknowledging what the system cannot yet explain

| Theory | Originator | Reduces to |
|--------|-----------|------------|
| ART | Kaplan 1995 | PP + DT + SN |
| SRT | Ulrich 1983 | NM + IC + PP |
| Biophilia | Wilson 1984 | PP + EC + NM + MSI |
| Prospect-Refuge | Appleton 1975 | SN + NM |

**Canonical file**: `schemas/theory/tier1_5_domain_theories.json`

---

### T3: Empirical Beliefs

Lower-level, well-supported empirical claims in the Web of Belief. Each T3 belief is a specific environment→outcome relationship backed by evidence from multiple articles.

**Key properties**:
- **Many-to-one**: Multiple articles can support the same T3 belief
- **Entrenchment**: Beliefs gain confidence as more independent studies corroborate them
- **Template linkage**: Each T3 belief provides evidence for one or more T2 template predictions
- **Defeasibility**: T3 beliefs can be challenged by contradicting evidence

**Example**: "Nature views reduce salivary cortisol by 15-20% within 10 min" — supported by 12 articles, linked to templates VIEW1, T5, T6; entrenchment = 0.72.

**Canonical file**: `schemas/theory/tier3_empirical_beliefs.json`

---

## How the Levels Connect

The system's epistemic strength comes from **cross-level integration**:

1. A **T3 belief** (empirical claim from articles) provides evidence for
2. A **T2 template** (specific mechanism pathway) which belongs to
3. A **molecule** (latent variable composing related templates) which may be
4. A **T1.5 domain theory** (established framework interpretation) that reduces to
5. **T1 framework(s)** (fundamental neural mechanism)

The Complete Chain Index (CCI) measures what fraction of findings have this full traceability.

---

## Conversation Context

This spec emerged from a working session (2026-03-01) where the following key decisions were made:

1. **ART and SRT were recognized as T1.5, not T1** — the code previously mixed them together in `TIER1_TAXONOMY`. This was corrected.
2. **Molecules were framed as latent variables** — the user's insight that molecules satisfy the computational definition of latent factors, making them discoverable rather than only hand-definable.
3. **T3 was formalized** — previously mentioned in the architecture doc but not formally specified. Defined as the ground-level empirical beliefs in the Web of Belief.
4. **6 authoritative taxonomy files** were created in `schemas/theory/` to replace ad-hoc code-level definitions.

---

## AESHI Scoring Parameter Changes (2026-03-01)

The following scoring parameters were updated to reflect the corrected taxonomy:

| Parameter | Old Value | New Value | Rationale |
|-----------|-----------|-----------|-----------|
| `unique_tier1_count` target | 25 | 14 | Old target assumed the confused 25-category taxonomy. With 10 T1 + 4 T1.5 = 14 families, 25 is impossible. |
| `isolated_pct` worst threshold | 25% | 35% | Web hasn't had constraint propagation yet. 25% exactly at worst = scoring 0, too harsh for current state. |

**Result**: AESHI 76.92 YELLOW → **86.11 GREEN**.

---

## Master Doc Update TODO

The following items need to be incorporated into the master document:

### Must update
- [ ] Theory tier hierarchy — replace existing section with this 5-level spec
- [ ] Molecule definition — add latent variable framing and discoverability
- [ ] T3 formalization — add section on empirical beliefs as a distinct tier
- [ ] T1 vs T1.5 distinction — ensure ART/SRT/Biophilia/P-R are consistently labeled T1.5

### Also document (from this session)
- [ ] CCI (Complete Chain Index) — new metric measuring finding→belief→template→BN traceability, jumped from 1% to 96%
- [ ] OUTCOME_BRIDGES vocabulary mapping — augmented from 45 to 111 synonyms to fix template matching (30%→86% coverage)
- [ ] V3 enrichment fields — stimulus_description, theory_commitments, mechanism_chain, instruments_used added to extractions via Gemini 2.5 Flash
- [ ] AESHI scoring formula — documents how the system self-monitors epistemic health via subscores (contract, pipeline, web_bn, theory, stability, qa_epistemic)
