# AG Opus Queue Standing Order

**Last updated**: 2026-03-04
**Purpose**: Automated queue monitoring and Opus polish processing for AG sessions
**Trigger**: Session startup, periodic checks during long sessions

---

## Quick Start

When you (AG) start a session in Article_Eater_PostQuinean_v1:

```python
from scripts.check_opus_queue import check_opus_queue

status = check_opus_queue(".")
print(status["message"])

if status["opus_queued"] > 0:
    print(f"Alert: {status['opus_queued']} cards waiting for Opus polish")
```

---

## Standing Instructions

### 1. Check Queue at Startup

**When**: Every AG session start in this repo
**What**: Run the queue detector
**Why**: Opus queue accumulates when Polish (Pass 2) is not processed

```bash
python scripts/check_opus_queue.py
```

**Exit codes**:
- `0`: Queue is empty (no action needed)
- `1`: Queue has pending cards (process them)

### 2. Process Polish Queue (If Cards Are Waiting)

**Condition**: If `status["opus_queued"] > 0`

**Action**: Offer to run:
```bash
python scripts/batch_generate_cards.py --process-opus-queue --max-cards 50
```

**Guidance**:
- Run in background if David approves
- Process up to 50 cards per session (avoid hogging Opus quota)
- Track which cards are polished vs. remaining
- Report completion: "{N} cards polished, {M} remaining"

### 3. Check Pipeline Health (For Deeper Diagnostics)

**When**: If backlog is large (>50 cards) or queue seems stuck

**What**: Query the overseer health check:
```python
from src.services.overseer import OverseerService

overseer = OverseerService(
    overseer_db_path="data/overseer.db",
    web_db_path="data/web.db",
    web=None  # Optional; web can be None for read-only health check
)

health = overseer.check_two_pass_pipeline_health()
print(f"Status: {health['status']}")
print(f"Message: {health['message']}")
```

**Health statuses**:
- `"healthy"`: Normal pipeline flow, no intervention needed
- `"backlog"`: Queue_depth > 100, polish is slower than generation
- `"stalled"`: Oldest queued card is > 7 days old, possible blocker

---

## Pipeline Architecture (Two-Pass)

```
Article Integration (Paper → Web of Belief)
           ↓
    [Card Generation Orchestrator]
           ↓
    ┌─────────────────┐
    │  PASS 1         │
    │  (Sonnet)       │
    │  Generate base  │
    │  card content   │
    └─────────────────┘
           ↓
    [Queue for Polish]
    (stored in opus-model queue)
           ↓
    ┌─────────────────┐
    │  PASS 2         │
    │  (Opus)         │
    │  Polish content │
    │  refine prose   │
    └─────────────────┘
           ↓
    [Card Published]
```

**Key insight**: The Opus queue depth reflects how many cards are awaiting their final polish. A large backlog means:
- Pass 1 generation is outpacing Pass 2 polish
- Opus sessions (free via CW/CC/AG) are not running frequently enough
- Or there's a blocker preventing polish from completing

---

## Monitoring Rules

| Metric | Threshold | Action |
|--------|-----------|--------|
| `opus_queued` | > 0 | Offer to process |
| `opus_queued` | > 50 | Alert David, check staleness |
| `opus_queued` | > 100 | Log as BACKLOG (INV-16), escalate |
| Oldest card age | > 7 days | Log as STALLED (INV-16), investigate |

---

## Integration with OVERSEER

The overseer monitors this pipeline via **INV-16: Card two-pass pipeline health**.

When OVERSEER runs (nightly audit or POST_INTEGRATION), it calls:
```python
overseer.check_two_pass_pipeline_health()
```

This returns:
```python
{
    "opus_queue_depth": 5,           # Cards awaiting Opus polish
    "pass1_complete": 25,            # Cards past initial generation
    "pass2_complete": 20,            # Cards fully polished
    "total_tracked": 30,             # Total in pipeline
    "completion_pct": 66.7,          # % with both passes done
    "status": "healthy",             # "healthy" | "backlog" | "stalled"
    "oldest_queued_age_days": 0.5,   # Age of oldest waiting card
    "message": "..."                 # Human-readable summary
}
```

---

## When to Escalate to David

Ask David to review if:

1. **Queue is stalled** (oldest card > 7 days in queue)
   - Possible cause: batch_generate_cards.py never runs
   - Fix: Ensure AG or another session processes queue regularly

2. **Backlog accumulates** (> 100 cards)
   - Possible cause: Pass 1 is too fast, Pass 2 can't keep up
   - Fix: Reduce Pass 1 throttle or allocate more Opus sessions

3. **Polish is failing**
   - Look for errors in batch_generate_cards.py logs
   - Check OVERSEER violation INV-14 (queue depth) and INV-15 (staleness)

4. **Queue file is corrupted**
   - If check_opus_queue.py reports JSON error
   - Fix: Manually inspect data/materialized_views/cards/generation_queue.json

---

## Files Reference

| File | Purpose |
|------|---------|
| `scripts/check_opus_queue.py` | Queue detector; entry point for monitoring |
| `src/services/overseer.py::check_two_pass_pipeline_health()` | Detailed health metrics (INV-16) |
| `src/qa/card_generation_orchestrator.py` | Core pipeline; manages _queue object |
| `data/materialized_views/cards/generation_queue.json` | Persistent queue state |
| `scripts/batch_generate_cards.py` | Worker that processes queue |

---

## Example Session Workflow

```python
# 1. AG starts a session
from scripts.check_opus_queue import check_opus_queue
status = check_opus_queue(".")

# 2. Check result
if status["opus_queued"] > 0:
    print(f"Alert: {status['opus_queued']} cards in polish queue")

    # 3. Ask David (or auto-process if laptop idle)
    # 4. Run processor
    # os.system("python scripts/batch_generate_cards.py --process-opus-queue --max-cards 50")

    # 5. Report
    status = check_opus_queue(".")
    print(f"After processing: {status['opus_queued']} remaining")
```

---

## Troubleshooting

**Q: check_opus_queue.py says "Queue file not found"**
A: Pipeline hasn't been initialized. Run a full orchestrator init first.

**Q: Queue keeps growing every session**
A: No one is calling batch_generate_cards.py --process-opus-queue. Add to AG's periodic checks.

**Q: Status shows "stalled" but nothing is wrong**
A: Check if batch_generate_cards.py is silently failing. Review logs in data/logs/.

**Q: How do I reset a stuck queue?**
A: Do not delete generation_queue.json. Instead, use orchestrator.process_polish_queue(max_cards=1) to clear one card and see if it unblocks.
