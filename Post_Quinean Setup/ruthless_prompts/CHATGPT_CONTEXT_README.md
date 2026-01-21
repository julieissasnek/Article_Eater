# ChatGPT Context Package for Ruthless System Review

**Date**: January 22, 2026
**Purpose**: Enable ChatGPT to run the same ruthless system review

---

## How to Use This Package

1. Upload the `chatgpt_context.zip` file to ChatGPT
2. Ask ChatGPT to read the files
3. Paste the contents of `RUTHLESS_SYSTEM_REVIEW_PROMPT_2026_01_22.md`
4. Request panel responses

---

## Files Included in chatgpt_context.zip

### Configuration & Governance
- `CLAUDE.md` - Project configuration and governance rules
- `Project_Constitution.md` - Core project rules (if exists)

### Core Engine (Priority 1)
- `src/services/web_of_belief.py` - THE key file (Quinean coherentist engine)
- `src/services/causal_classifier.py` - Three-tier causal classification
- `src/services/query_response.py` - Response generation with directional opposition

### Supporting Services (Priority 2)
- `src/services/reporting.py` - Gap analysis and reports
- `src/services/query_parser.py` - Natural language query parsing
- `src/services/bridge_warrants.py` - Knowledge transfer warrants

### API Routes (Priority 3)
- `app/routes/query.py` - Query API endpoints

### Schemas (Priority 4)
- `contracts/ae_af/schemas/ae.claim.v1.schema.json`
- `contracts/ae_af/schemas/ae.web_state.v1.schema.json`

### Documentation
- `Post_Quinean Setup/SYSTEM_OVERVIEW.md` - Architecture overview
- `Post_Quinean Setup/ruthless_prompts/RUTHLESS_SYSTEM_REVIEW_PROMPT_2026_01_22.md` - The prompt

---

## What ChatGPT Needs to Know

### System Overview
Article Eater V21.0.0 (Post-Quinean) is a knowledge extraction system for neuroarchitecture research using Quinean coherentist epistemology.

### Key Concepts
1. **Web of Belief**: All knowledge is revisable, no foundations
2. **Three-Tier Causal Classification**: CAUSAL/SUGGESTIVE/ASSOCIATIONAL
3. **Directional Opposition**: Contested evidence detected by X increases Y vs X decreases Y
4. **Bridge Warrants**: How knowledge transfers between contexts

### Review Focus Areas
1. Epistemological correctness (Pearl)
2. Evidence portability (Cartwright)
3. Cognitive load (Simon)
4. Information access (Bates)
5. Domain accuracy (Kaplan)
6. Formal rigor (Lamport)
7. Software design (Liskov, Brooks, Parnas)
8. Theory preservation (Naur)

---

## Token Considerations

The full context is approximately:
- web_of_belief.py: ~1500 lines (~30k tokens)
- causal_classifier.py: ~580 lines (~12k tokens)
- query_response.py: ~755 lines (~15k tokens)
- Other files: ~50k tokens total

**Total**: ~100k+ tokens

### For 8k context models
Include only:
- CLAUDE.md
- causal_classifier.py
- The prompt

### For 32k context models
Include:
- CLAUDE.md
- causal_classifier.py
- query_response.py
- reporting.py
- The prompt

### For 128k+ context models
Include all files in this package.

---

## Prompt Modification for ChatGPT

When running with ChatGPT, modify the prompt to:
1. Reference the uploaded files by name
2. Ask for one expert at a time if context is limited
3. Request specific file analysis rather than comprehensive review

Example:
```
I've uploaded the Article Eater codebase context. Please act as Dr. Judea Pearl
and review the causal_classifier.py file. Focus on:
1. Is the three-tier logic epistemically correct?
2. Is the quasi-experimental handling appropriate?
3. Are there missing causal patterns?
```
