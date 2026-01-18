# Article Eater System Overview
*Auto-generated: 2026-01-18 | Version: V21.0.0 (Post-Quinean)*

## What This System Does

Article Eater extracts evidence-backed rules from scientific papers about how built environments affect human cognition, emotion, and behavior. It transforms research literature into structured, queryable knowledge for neuroarchitecture research.

**End Goal**: Given an image or 3D model of a space → produce probabilistic predictions about its effects on humans, with full provenance to source papers.

## Architecture

### Track A: Extraction Pipeline
`PDF → Seven-Panel LLM Extraction → claims.jsonl + rules.jsonl`
Location: `app/tasks/pipeline.py`

### Track B: Quinean Web of Belief
`Claims → Beliefs → Coherence assessment → Tension detection`
Location: `src/services/web_of_belief.py` (1300+ lines)

### Track C: Theory Registry
`Theories → Predictions → Evidence → Confidence tracking`
Location: `src/services/theory_registry.py`

## Why This Approach Is Innovative

1. **Quinean Coherentism** - Not foundationalist accumulation; beliefs justify via coherence
2. **Bridge Warrants** - Explicit tracking of domain transfer assumptions
3. **Outcome Taxonomy** - Temporal dynamics (immediate states vs lasting structures)
4. **Full Provenance** - Every prediction traces to source papers

## Current State

- Version: V21.0.0 (Post-Quinean)
- Sprint 1: COMPLETE (extraction_to_web.py)
- Sprint 2: READY (pipeline integration)

## Regenerating This Document

To update this overview after significant changes:
```bash
# Manual: Review and update sections as needed
# Future: Script to auto-generate from code analysis
```

---

*See `CLAUDE.md` for detailed development guidance.*
*See `archive/docs/INDEX.md` for historical documentation.*
