# ATLAS Staging Workflow — Sandbox-to-Native Bridge

**Date**: 2026-02-27
**Status**: Active

## The Problem

AI sandbox environments (Cowork VM, AG's sandbox) mount your repo and can read/modify code freely, but **cannot reliably write to SQLite databases**. This is a filesystem-level restriction (virtiofs/overlay mounts don't support the POSIX locking semantics SQLite requires for journaling and WAL mode).

This means:
- Code changes work fine (file writes succeed)
- Database operations fail (SystemSetup.setup(), safe_improve_web_health, overseer audits)
- The gap between "code is ready" and "code has been run" persists across sessions

## The Solution: Local Runner

`scripts/local_runner.py` is a thin executor that bridges sandboxed AI sessions and your native machine.

### How It Works

```
 Sandbox (Cowork/AG)              Your Mac (native)
 ┌──────────────────┐             ┌──────────────────┐
 │ 1. Writes code   │──(repo)──> │                   │
 │ 2. Queues command │──(JSON)──> │ local_runner.py   │
 │    to run_queue   │            │  reads queue      │
 │                   │ <─(JSON)── │  executes natively │
 │ 3. Reads results  │            │  writes results    │
 └──────────────────┘             └──────────────────┘
```

The shared medium is the git repo directory, which both sandbox and native can access.

### Setup (One Time)

```bash
# Option A: Cron (runs every 5 minutes)
crontab -e
# Add:
*/5 * * * * cd /Users/davidusa/REPOS/Article_Eater_PostQuinean_v1 && python scripts/local_runner.py once >> logs/local_runner.log 2>&1

# Option B: Manual watch mode (leave a terminal open)
cd /Users/davidusa/REPOS/Article_Eater_PostQuinean_v1
python scripts/local_runner.py watch
```

### Usage from Sandbox (AI writes this)

```python
# From any sandbox AI session:
import subprocess
subprocess.run([
    "python", "scripts/local_runner.py", "queue", "integrate",
    "--by", "cowork_session"
])
```

### Usage from Terminal (David runs this)

```bash
# Run integration directly (no queue)
python scripts/local_runner.py run integrate

# Run the full nightly pipeline
python scripts/local_runner.py run nightly

# Check what's queued
python scripts/local_runner.py status

# Process everything in the queue once
python scripts/local_runner.py once
```

### Available Commands

| Command | What It Does | Pre-backup? | Timeout |
|---------|-------------|-------------|---------|
| `backup_full` | Full snapshot of all databases | No (it IS the backup) | 120s |
| `backup_incremental` | Near-instant incremental (<100ms if unchanged) | No | 30s |
| `integrate` | SystemSetup.setup() — bulk integration | Yes | 600s |
| `web_health` | Connect isolated beliefs (AG's 3-strategy script) | Yes | 300s |
| `health` | Health check gauntlet | No | 120s |
| `nightly` | Full 9-stage nightly pipeline | Yes | 900s |
| `diagnose` | Database diagnostic report | No | 60s |
| `system_health` | Compute AESHI score | No | 120s |
| `system_map` | Generate architecture visualization | No | 120s |

### Safety Features

1. **Fixed allowlist**: Only the commands above can be executed. No arbitrary code execution.
2. **Pre-flight backup**: Commands that write to databases automatically run `--mode incremental` backup first.
3. **Full audit trail**: Every command logged to `data/run_queue.json` with timestamps, requestor, and results.
4. **Timeout protection**: Each command has a timeout; killed if exceeded.
5. **Dry-run support**: All commands support `--dry-run` for previewing.

## Immediate Actions Needed

Run these on your native Mac to bring the system current:

```bash
cd /Users/davidusa/REPOS/Article_Eater_PostQuinean_v1

# 1. Incremental backup first (near-instant)
python scripts/backup_databases.py --mode incremental

# 2. Integrate all 565 unprocessed articles (~4 minutes)
python scripts/local_runner.py run integrate

# 3. Connect isolated beliefs
python scripts/local_runner.py run web_health

# 4. Full health check
python scripts/local_runner.py run health

# 5. Generate architecture map
python scripts/local_runner.py run system_map
```

## Backup Strategy

| When | Mode | Command | Duration |
|------|------|---------|----------|
| Before any pipeline stage | Incremental | `--mode incremental` | <100ms |
| Nightly (cron) | Full | `--mode full` | ~6s |
| Before migrations | Tagged full | `--mode full --tag before_migration` | ~6s |
| After integration | Incremental | automatic (local_runner does this) | <100ms |

The incremental mode reads the SQLite header's change_counter (bytes 24-28) without opening a connection — no locks, no journal, no risk of corruption. If nothing changed, it returns in under 1 millisecond.
