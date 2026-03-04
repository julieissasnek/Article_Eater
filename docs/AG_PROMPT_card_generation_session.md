# AG Prompt: Session Card Generation (Opus Polish)

**Date**: 2026-03-04
**Priority**: HIGH — David wants card generation running NOW
**Coordination**: File-based claims at `data/session_card_claims.json`

---

## Your Task

Generate ATLAS cards using your own Opus model — zero API cost. You are the writing agent. You read prompts, you write the tab content, you save cards.

## Setup (Run Once)

```python
import sys
sys.path.insert(0, ".")

from src.qa.session_card_writer import SessionCardWriter
from src.qa.card_tab_generators import register_llm_generators
from src.qa.card_generation_orchestrator import CardGenerationOrchestrator

# Initialize
writer = SessionCardWriter(base_dir=".")

# Check queue
status = writer.get_queue_status()
print(f"Cards waiting: {status}")
```

## Generation Loop

For each card:

### Step 1: Get next card prompt
```python
prompt = writer.get_next_card_prompt(terminal_id="AG-OPUS-1")
if prompt is None:
    print("Queue empty — all cards claimed or generated")
else:
    print(f"Generating: {prompt.card_id}")
    print(f"Card type: {prompt.card_type}")
    print(f"Tabs needed: {prompt.tab_names}")
```

### Step 2: Read the prompt and write each tab

The prompt object contains `tab_prompts: Dict[str, Tuple[str, str]]` — a mapping from tab_name to (system_prompt, user_prompt). For each tab:

1. Read the system prompt (epistemic norms, writing style, tab-specific instructions)
2. Read the user prompt (evidence context, source data)
3. Write the tab content as publication-quality prose
4. Include a ```json ... ``` block with structured data

### Step 3: Submit the response
```python
tab_responses = {
    "overview": "Your generated overview prose...\n```json\n{...}\n```",
    "mechanism": "Your generated mechanism prose...\n```json\n{...}\n```",
    "evidence": "Your generated evidence prose...\n```json\n{...}\n```",
    "sources": "Your generated sources prose...\n```json\n{...}\n```",
    # ... all tabs
}

result = writer.accept_card_response(
    card_id=prompt.card_id,
    tab_responses=tab_responses,
    terminal_id="AG-OPUS-1",
)
print(f"Card saved: {result}")
```

### Step 4: Repeat

Continue until queue is empty or you hit your target count.

## Coordination Rules

1. **Use terminal_id "AG-OPUS-1"** consistently
2. **Claims are file-based** at `data/session_card_claims.json` — any terminal can read it
3. **Do NOT claim more than 20 cards at once** — leave work for other terminals
4. **If a card fails quality gate**, note the error and move on — don't retry endlessly
5. **Check MESSAGE_BOARD** before starting — CW may have updated priorities

## Quality Standards

- Every tab must have prose_health ≥ 6.0 (production quality)
- Opus is the writing model — no drafts, no [DRAFT] markers
- Confidence language must match omega score precisely
- Scope conditions for all empirical claims
- Defeater status for high-credence claims (ω > 0.70)
- Sources tab: per-paper method details with stimulus descriptions

## What to Generate First

Priority order:
1. T1 Framework cards (10 cards) — highest value, most complex
2. T1.5 Domain Theory cards (13 cards) — theoretical synthesis
3. Molecule cards (18 cards) — latent variable explanations
4. Competition cards — debate framing
5. T2 Mechanism cards — largest volume, moderate complexity

## If You Finish Early

1. Run `python scripts/backfill_stimulus_descriptions.py` to see stimulus coverage
2. Check `python scripts/check_opus_queue.py` for any batch Pass 2 cards waiting
3. Post completion report to `.agent_coord/MESSAGE_BOARD.md`
