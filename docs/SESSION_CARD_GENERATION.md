# Session Card Generation — Zero-Cost Opus Writing in CW/CC/AG

**Date**: 2026-03-04
**Status**: Active
**Cost Model**: Free (uses session agent's Opus allocation)

## Overview

This system enables **free card generation** for ATLAS by leveraging the session agent's own Opus model. No API calls are made — the session agent IS the LLM.

### The Problem Solved

Previously, `batch_generate_cards.py` made paid API calls even when run from a free session. This is wasteful:
- Free sessions already have Opus allocation
- The session agent can generate the content itself
- No API cost should be incurred

### The Solution

`SessionCardWriter` provides a simple interface:

1. **Agent requests prompt**: `python scripts/session_generate_cards.py --next-prompt`
2. **Agent sees prompt** and generates content in conversation
3. **Agent provides response** via `--accept-response`
4. **Script parses, validates, saves card** to disk

Total cost: **$0** (uses session's free Opus allocation)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ CardGenerationOrchestrator                                  │
│ (tracks queue, prioritization, staleness)                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ├─ API queue (Sonnet/Haiku Pass 1)
                       │  └─ batch_generate_cards.py
                       │
                       └─ Session queue (Opus Pass 2)
                          └─ SessionCardWriter
                             ├─ get_next_card_prompt()
                             │  └─ Agent reads → generates
                             │
                             ├─ accept_card_response()
                             │  └─ Parse, validate, save
                             │
                             └─ ClaimsRegistry
                                └─ Prevent duplicate work
```

## Key Components

### 1. SessionCardWriter (`src/qa/session_card_writer.py`)

Main class that manages card generation in sessions.

**Key Methods**:

```python
class SessionCardWriter:
    def get_next_card_prompt(
        terminal_id: str,
        card_type_filter: Optional[CardType]
    ) -> Optional[PromptForAgent]:
        """Get the next card prompt for the agent to process."""

    def accept_card_response(
        card_id: str,
        tab_responses: Dict[str, str],
        terminal_id: str
    ) -> Tuple[bool, str, Optional[Card]]:
        """Accept agent's generated content and save card."""

    def claim_cards(
        terminal_id: str,
        count: int,
        card_type_filter: Optional[CardType]
    ) -> List[str]:
        """Claim N cards for this terminal (prevents duplicates)."""

    def get_queue_status(self) -> Dict[str, Any]:
        """Show current queue depth and claim status."""
```

### 2. ClaimsRegistry

Prevents multiple terminals from processing the same card.

```python
@dataclass
class ClaimsRegistry:
    def load_from_file(path: Path) -> None:
        """Load existing claims from JSON."""

    def claim(card_id, card_type, entity_id, terminal_id) -> bool:
        """Try to claim a card. Returns False if already claimed."""

    def update_status(card_id, status, error) -> None:
        """Update claim status (claimed, in_progress, completed, failed)."""

    def get_claimed_card_ids(self) -> Set[str]:
        """Get all currently-claimed cards."""
```

### 3. PromptForAgent

Encapsulates a card prompt in Markdown format for agent display.

```python
@dataclass
class PromptForAgent:
    card_id: str
    card_type: CardType
    entity_id: str
    tabs_to_generate: List[str]
    system_prompt: str
    user_prompts: Dict[str, str]

    def to_markdown(self) -> str:
        """Format as readable Markdown (system prompt + each tab's user prompt)."""
```

### 4. Script: `session_generate_cards.py`

Command-line interface for agents to interact with the system.

**Commands**:
- `next-prompt` — Show next card to generate
- `status` — Show queue status
- `show-claims` — Show terminal claims
- `accept-response` — Accept generated card

---

## Usage Guide

### In a Session: Generate a Card

#### Step 1: Get the Next Prompt

```bash
python scripts/session_generate_cards.py next-prompt --terminal claude-1
```

This prints a card prompt like:

```
# Card Generation Prompt

**Card Type**: t1-framework
**Entity ID**: ecological_psychology
**Card ID**: t1-framework:ecological_psychology

**Tabs to Generate**: connections, debate, design, evidence, mechanism, overview

## System Prompt

[... epistemic writing norms ...]

## User Prompts

### overview
[... context about ecological psychology ...]

### mechanism
[... context about how it works ...]

[... etc. for each tab ...]

## Instructions

For each tab above:
1. Read the system prompt and user prompt
2. Generate the tab content (prose + optional JSON)
3. Respond in this format:

---

## YOUR RESPONSE

### overview
[Your prose here...]
```json
{}
```

### mechanism
[Your prose here...]
```json
{}
```

(etc. for each tab)
```

#### Step 2: Generate Content in Conversation

Read the prompts and generate tab content. For example:

```markdown
## YOUR RESPONSE

### overview

Ecological Psychology, pioneered by James Gibson, provides a foundational framework
for understanding how organisms directly perceive and interact with environmental
affordances. Gibson's core insight was that perception is not a passive reception of
sensory data but rather an active process of detecting action possibilities in the
environment. The theory has gained substantial empirical support across 340 findings
in 120 papers, with a confidence level (omega) of 0.78, indicating strong convergent
evidence.

The practical significance of this theory extends across multiple domains: it explains
why architectural environments feel more or less inviting, why some workplaces foster
productivity while others feel constraining, and how environmental design shapes
behavioral possibilities. The mechanism operates through direct perception: organisms
detect surfaces, openings, and textures as "walkable," "climbable," "graspable," etc.

Active debate centers on whether all affordances are directly perceived or whether
some require learning and cultural context. Gibson maintained that affordances are
objective properties of the environment, while contemporary research suggests the
perception-experience relationship is more nuanced. No significant defeaters exist to
the core finding, though scope conditions are important: affordance perception varies
with observer capabilities, developmental stage, and cultural background.

```json
{
  "theory_name": "Ecological Psychology",
  "n_findings": 340,
  "n_papers": 120,
  "omega": 0.78,
  "direction_consensus": "increase",
  "confidence_level": "high"
}
```

### mechanism

[... more content ...]
```

#### Step 3: Accept the Response

Save your response to a file (or have the agent save it):

```bash
python scripts/session_generate_cards.py accept-response \
  --card-id "t1-framework:ecological_psychology" \
  --response-file /tmp/my_response.txt \
  --terminal claude-1
```

The script will:
1. Parse each tab's prose and JSON
2. Validate prose quality
3. Save the card to `data/cards/t1-framework/ecological_psychology.json`
4. Update claim status to "completed"

---

## Parallel Terminal Workflow

When multiple agents run simultaneously in different sessions:

### Terminal 1 (Session 1)

```bash
python scripts/session_generate_cards.py next-prompt --terminal claude-1
# Gets: card1, card2, card3 (each claimed for claude-1)

python scripts/session_generate_cards.py accept-response \
  --card-id "t1-framework:ecological_psychology" \
  --response-file /tmp/card1.txt \
  --terminal claude-1
```

### Terminal 2 (Session 2 — runs in parallel)

```bash
python scripts/session_generate_cards.py next-prompt --terminal claude-2
# Gets: card4, card5, card6 (NOT claimed by claude-1)
# ClaimsRegistry prevents duplicate work
```

### Terminal 3 (Session 3 — parallel)

```bash
python scripts/session_generate_cards.py next-prompt --terminal claude-3
# Gets: card7, card8, card9
```

**Result**: Three agents work in parallel, each claiming their own cards, zero duplicate work.

---

## Integration with batch_generate_cards.py

The two-pass architecture:

**Pass 1 (Fast)**: Run from anywhere
```bash
python scripts/batch_generate_cards.py --tiered --max-cards 100
```
- Uses Haiku/Sonnet (cheap API calls)
- Generates draft prose + structured data
- Stores results in queue with `session_mode=False` for Sonnet cards
- Stores results in queue with `session_mode=True` for Opus cards

**Pass 2 (Polish)**: Run from sessions
```bash
# In CW/CC/AG session
python scripts/session_generate_cards.py next-prompt
# Agent rewrites Pass 1 draft to publication quality
python scripts/session_generate_cards.py accept-response --card-id "..." --response-file /tmp/card.txt
```

Cost breakdown:
- **Pass 1**: ~$20-30 for 4,000 cards (Haiku/Sonnet API calls)
- **Pass 2**: $0 (session Opus allocation)
- **Total**: ~$20-30 instead of ~$400 (API Opus for all cards)

---

## Quality Assurance

Each tab is validated:

1. **Prose health check**: Uses `ProseRevisionService` to score 0-10
   - ≥6.0 = Production-ready
   - 3.0-5.9 = Acceptable draft
   - <3.0 = Rejected

2. **Structured data validation**: JSON must be well-formed

3. **Card validation**: `Card.validate_tabs()` ensures all required tabs present

If any tab fails:
- Card is saved with error status
- Claim marked as "failed"
- Error logged for later review

---

## Queue Status and Monitoring

```bash
# Show status
python scripts/session_generate_cards.py status

# Output:
# === SESSION CARD GENERATION QUEUE STATUS ===
#
# Total queued for session: 4002
#   Unclaimed:              3998
#   Claimed by terminals:   4
#
# By card type:
#   t1-framework         :   10
#   t1_5-domain_theory   :   15
#   molecule             :   120
#   method               :   45
#   math                 :   60
#   ... (etc.)
```

Check terminal claims:

```bash
python scripts/session_generate_cards.py show-claims --verbose

# Output:
# === TERMINAL CLAIMS ===
#
# Terminal: claude-1
#   claimed      :   3
#   in_progress  :   0
#   completed    :   1
#   failed       :   0
#   Details:
#     t1-framework:ecological_psychology            claimed     2026-03-04T10:30:00Z
#     t1-framework:attention_restoration             claimed     2026-03-04T10:31:00Z
#     molecule:daylighting_perception                claimed     2026-03-04T10:32:00Z
#     t1-framework:stress_reduction                  completed   2026-03-04T10:35:00Z
```

---

## Data Files

### `data/generation_queue.json`

The priority queue of cards waiting for generation (both API and session modes).

```json
{
  "queue": [
    {
      "card_id": "t1-framework:ecological_psychology",
      "type": "t1-framework",
      "priority": 1,
      "model": "opus",
      "session_mode": true,
      "created_at": "2026-03-04T10:00:00Z"
    },
    ...
  ],
  "in_progress": ["t1-framework:stress_reduction"],
  "stats": { ... }
}
```

### `data/session_card_claims.json`

Tracks which terminal has claimed which card (prevents duplicates).

```json
{
  "claims": [
    {
      "card_id": "t1-framework:ecological_psychology",
      "card_type": "t1-framework",
      "entity_id": "ecological_psychology",
      "terminal_id": "claude-1",
      "claimed_at": "2026-03-04T10:30:00Z",
      "status": "claimed",
      "error": null
    },
    ...
  ],
  "saved_at": "2026-03-04T10:30:15Z"
}
```

### `data/cards/{card_type}/{entity_id}.json`

The final generated card.

```json
{
  "card_id": "t1-framework:ecological_psychology",
  "surface": {
    "entity_id": "ecological_psychology",
    "card_type": "t1-framework",
    "title": "Ecological Psychology (Gibson)",
    "summary": "Direct perception of affordances in the environment.",
    "tier": "a"
  },
  "body": {
    "created_at": "2026-03-04T10:35:00Z",
    "last_updated": "2026-03-04T10:35:00Z",
    "tabs": [
      {
        "tab_name": "overview",
        "prose": "Ecological Psychology, pioneered by James Gibson...",
        "structured_data": { ... }
      },
      ...
    ]
  },
  "iceberg": {
    "quality_scores": {
      "prose_health": 8.2,
      "completeness": 1.0
    },
    "agent_context": {
      "generated_by": "claude-1",
      "generation_time_ms": 45000,
      "model": "session"
    }
  }
}
```

---

## Agent Workflow (Detailed)

### 1. Agent (in session) Gets Next Card

```
python scripts/session_generate_cards.py next-prompt --terminal $TERMINAL_ID
```

**System does**:
- Load generation queue from `data/generation_queue.json`
- Load claims from `data/session_card_claims.json`
- Find next unclaimed card with `session_mode=true`
- Claim it for this terminal
- Build system prompt + user prompts for each tab
- Print `PromptForAgent.to_markdown()` output

### 2. Agent Reads Prompts and Generates Content

Agent sees something like:

```
# Card Generation Prompt

**Card Type**: t1-framework
**Entity ID**: ecological_psychology
**Card ID**: t1-framework:ecological_psychology

...

## System Prompt

[EPISTEMIC NORMS, VOICE, STYLE MECHANICS...]

## User Prompts

### overview
CARD TYPE: T1 Framework
ENTITY: Ecological Psychology (Gibson)
EVIDENCE BASE: 340 findings across 120 papers
CONFIDENCE: omega = 0.78 (HIGH)
DIRECTION: increase
...

### mechanism
...

### evidence
...

...

## YOUR RESPONSE

### overview
[Agent writes prose + optional JSON]

### mechanism
[Agent writes prose + optional JSON]

...
```

Agent generates each tab, following the system prompt and context.

### 3. Agent Saves Response

Agent saves response to a file (or provides it via API in future):

```
cat > /tmp/card_response.txt << 'EOF'
### overview
Ecological Psychology, pioneered by James Gibson, provides...

```json
{ "n_findings": 340, "n_papers": 120, "omega": 0.78 }
```

### mechanism
The mechanism operates through direct perception...

```json
{ "mechanism_chain": [...] }
```

### evidence
...

### design
...

### connections
...

### debate
...
EOF
```

### 4. Agent (or script) Submits Response

```bash
python scripts/session_generate_cards.py accept-response \
  --card-id "t1-framework:ecological_psychology" \
  --response-file /tmp/card_response.txt \
  --terminal $TERMINAL_ID
```

**System does**:
- Parse response into tab dictionary
- For each tab:
  - Extract prose + JSON using `_parse_llm_response()`
  - Check prose quality with `_check_prose_health()`
  - Build `CardTab` object
- Build `Card` object with Surface, Body, Iceberg
- Validate with `Card.validate_tabs()`
- Save to `data/cards/{card_type}/{entity_id}.json`
- Update claim status to "completed"
- Return success message

### 5. Repeat

Agent gets next card:

```
python scripts/session_generate_cards.py next-prompt --terminal $TERMINAL_ID
```

Continue until queue is empty.

---

## Success Conditions

| Condition | How to Verify |
|-----------|---------------|
| **SC-SCW-1**: Agent can read prompt | `--next-prompt` output is valid Markdown |
| **SC-SCW-2**: Agent can generate | Agent response has tabs, prose, JSON |
| **SC-SCW-3**: Script parses response | No parse errors in `accept-response` output |
| **SC-SCW-4**: Card saved to disk | File exists at `data/cards/{type}/{entity}.json` |
| **SC-SCW-5**: No duplicates | `show-claims` shows each card claimed by only 1 terminal |
| **SC-SCW-6**: Quality validation | Prose health scores logged; cards with <3.0 marked failed |

---

## Troubleshooting

### "No unclaimed cards in queue"

**Cause**: Queue is empty or all cards are claimed.

**Fix**: Run `status` to see what's queued:
```bash
python scripts/session_generate_cards.py status --verbose
```

Or populate queue with `populate_all_cards.py`:
```bash
cd /path/to/Article_Eater_PostQuinean_v1
python scripts/populate_all_cards.py --queue-only
```

### Card fails with prose_health < 3.0

**Cause**: Agent's prose was too short or poorly structured.

**Fix**: Agent should rewrite with more detail, clearer structure. Expected prose_health should be 6.0+.

### "Card already claimed" error

**Cause**: Another terminal has already claimed this card.

**Fix**: This is expected in parallel workflows. The system will automatically get the next unclaimed card.

### Claims file not persisting

**Cause**: Claims file path is not writable or doesn't exist.

**Fix**: Ensure `data/` directory exists and is writable:
```bash
mkdir -p data
chmod 755 data
```

### Card validation fails

**Cause**: Missing required tabs or invalid tab structure.

**Fix**: Check that agent generated all required tabs for the card type. Run with `--verbose` to see which tabs are missing.

---

## References

- **Main Implementation**: `src/qa/session_card_writer.py`
- **Script**: `scripts/session_generate_cards.py`
- **Prompt Builders**: `src/qa/card_tab_generators.py` (TAB_GENERATOR_CONFIG)
- **Queue Management**: `src/qa/card_generation_orchestrator.py`
- **Card Schema**: `src/qa/cards/card_schema.py`
- **Batch Generation (Pass 1)**: `scripts/batch_generate_cards.py`

---

## Version History

- **2026-03-04**: Initial implementation (this document)
  - SessionCardWriter class
  - ClaimsRegistry for parallel terminals
  - session_generate_cards.py script
  - Integration with batch_generate_cards.py (two-pass architecture)
