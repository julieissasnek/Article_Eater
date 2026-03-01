# Daily Doc Sync Scanner - Quick Reference

**Scanner Location**: `/sessions/practical-zen-darwin/mnt/REPOS/scripts/daily_doc_sync_scanner.py`

**State File**: `/sessions/practical-zen-darwin/mnt/REPOS/Article_Eater_PostQuinean_v1/data/doc_sync_state.json`

**Reports Directory**: `/sessions/practical-zen-darwin/mnt/REPOS/Article_Eater_PostQuinean_v1/docs/sync_reports/`

---

## Running the Scanner

### With Path Wrapper (Linux/Container Environment)

```bash
cat > /tmp/run_scanner.py << 'WRAPPED'
#!/usr/bin/env python3
import sys
import os
from pathlib import Path

original_ae_root = Path("/Users/davidusa/REPOS/Article_Eater_PostQuinean_v1")
actual_ae_root = Path("/sessions/practical-zen-darwin/mnt/REPOS/Article_Eater_PostQuinean_v1")
actual_scripts_dir = Path("/sessions/practical-zen-darwin/mnt/REPOS/scripts")

scanner_script = actual_scripts_dir / "daily_doc_sync_scanner.py"
script_content = scanner_script.read_text()

script_content = script_content.replace(
    'AE_ROOT = Path("/Users/davidusa/REPOS/Article_Eater_PostQuinean_v1")',
    f'AE_ROOT = Path("{actual_ae_root}")'
)
script_content = script_content.replace(
    'MASTER_PAPER = Path("/Users/davidusa/REPOS/NEURAL_EXPLANATIONS_ENVIRO_PSYCH_PAPER_2026-02-23.md")',
    f'MASTER_PAPER = Path("{actual_ae_root.parent}/NEURAL_EXPLANATIONS_ENVIRO_PSYCH_PAPER_2026-02-23.md")'
)

exec(script_content, {'__name__': '__main__', '__file__': str(scanner_script)})
WRAPPED

# Then run with desired options:
python3 /tmp/run_scanner.py [OPTIONS]
```

### Command Options

| Option | Effect | Runtime |
|--------|--------|---------|
| (none) | Incremental sync (since last state) | 2-5 sec |
| `--full-audit` | Re-scan entire docs/ tree | ~30 sec |
| `--since YYYY-MM-DD` | Find files modified after date | 5-10 sec |
| `--dry-run` | Don't update state file | Same + print info |

### Common Commands

```bash
# Daily incremental check (NEW and MODIFIED only)
python3 /tmp/run_scanner.py

# Check files changed since yesterday
python3 /tmp/run_scanner.py --since 2026-02-23

# Full audit without updating state (preview mode)
python3 /tmp/run_scanner.py --full-audit --dry-run

# Full audit and update state file
python3 /tmp/run_scanner.py --full-audit
```

---

## Output Files

### Report File
- **Name**: `SYNC_REPORT_YYYY-MM-DD.md`
- **Size**: 250-300 KB (first scan is larger)
- **Content**: 
  - Summary statistics (new, modified, unchanged counts)
  - Detailed file listings with coverage status
  - Key content excerpts for decision-relevant files
  - Integration recommendations sorted by file size

### State File
- **Name**: `doc_sync_state.json`
- **Size**: 89 KB (for ~1,500 files)
- **Format**: JSON manifest with paths and modification timestamps
- **Purpose**: Tracks file metadata for incremental scanning
- **Update**: Automatically updated by scanner (unless `--dry-run`)

---

## Reading the Reports

### File Status Tags

| Tag | Meaning | Action |
|-----|---------|--------|
| **NEW** | Not in state file yet | Review content |
| **MODIFIED** | Changed since last scan | Review changes |
| **UNCHANGED** | Same as last scan | Usually ignore |
| **COVERED** | Referenced in master paper | May be up-to-date |
| **NOT COVERED** | Not in master paper | Needs integration |

### Key Metrics

```
New: N          = Files discovered in this scan
Modified: M     = Files changed since last scan  
Unchanged: U    = Stable files (tracked for reference)
COVERED: C      = In master paper (373 files = 24%)
NOT COVERED: X  = Awaiting integration (1,163 files = 76%)
```

### Integration Recommendations

At end of report:

```
Priority for integration (sorted by size, larger = more content):
1. [File] ([Size])
2. [File] ([Size])
...
```

Focus on largest files first — they contain the most content.

---

## Decision-Relevant Content

The scanner highlights lines containing these keywords as potentially important:

- **Methodology**: decision, rationale, chose, rejected, alternative, design, architecture, specification
- **Expertise**: panel, expert, approval, consensus, deliberation
- **Validation**: constraint, ceiling, validated, confirmed
- **Outcomes**: result, improved, remediated, completed

When reviewing a new file, search for these terms to quickly identify design decisions.

---

## State File Management

### Viewing Current State

```bash
# Count tracked files
grep -c '"path":' /sessions/practical-zen-darwin/mnt/REPOS/Article_Eater_PostQuinean_v1/data/doc_sync_state.json

# List first 10 files
python3 -c "
import json
with open('/sessions/practical-zen-darwin/mnt/REPOS/Article_Eater_PostQuinean_v1/data/doc_sync_state.json') as f:
    data = json.load(f)
    for item in data[:10]:
        print(f'{item[\"path\"]}: {item[\"modified\"]}')"
```

### Resetting State (Advanced)

To force a fresh baseline:

```bash
rm /sessions/practical-zen-darwin/mnt/REPOS/Article_Eater_PostQuinean_v1/data/doc_sync_state.json
python3 /tmp/run_scanner.py --full-audit
```

---

## Scheduling (Future)

To run scanner automatically:

```bash
# Daily at 6 AM (add to crontab)
0 6 * * * python3 /tmp/run_scanner.py >> /var/log/doc_sync.log 2>&1

# Weekly on Sunday at 8 PM (full audit)
0 20 * * 0 python3 /tmp/run_scanner.py --full-audit >> /var/log/doc_sync_full.log 2>&1
```

---

## Troubleshooting

### "FileNotFoundError: /Users/davidusa/REPOS"

**Cause**: Script has hardcoded paths for native macOS environment  
**Solution**: Use the wrapper script above, which redirects to `/sessions/practical-zen-darwin/mnt/REPOS/`

### "State file not found"

**Cause**: First run or state file deleted  
**Solution**: Run `--full-audit` once to create initial state

### No new files reported (but you added some)

**Cause**: 
- Files not in monitored patterns (check MONITORED_PATTERNS in script)
- Files have recent modification dates (scanner uses file mtime)

**Solution**: Check if file path matches one of these patterns:
```
docs/*.md
docs/archive/*.md
scripts/*.py
src/cmr/*.py
src/epistemic/*.py
src/services/*.py
src/qa/*.py
src/extraction/*.py
contracts/**/*.json
contracts/**/*.md
```

---

## Integration Workflow

When a file is flagged "NOT COVERED":

1. **Read the file** — Understand its content and role
2. **Check decision keywords** — Identify design choices
3. **Add to master paper** — Reference in appropriate section
4. **Update state** — Re-run scanner to mark as covered
5. **Verify coverage** — Next report should show "COVERED"

**First priority files**:
- REMEDIATION_COMPLETION_2026_02_23.md
- CEILING_ADJUDICATION_COMPLETION_2026-02-23.md
- 02-15_01_Neuroscience_Panel_Tier1_Frameworks_V1.0.md
- 02-15_02_Neuroscience_Panel_Templates_and_Taxonomy_V1.0.md

---

## References

- **Baseline Audit Summary**: `BASELINE_AUDIT_SUMMARY_2026-02-24.md`
- **Full Report (Feb 24)**: `sync_reports/SYNC_REPORT_2026-02-24.md`
- **Scanner Source**: `/sessions/practical-zen-darwin/mnt/REPOS/scripts/daily_doc_sync_scanner.py`

---

**Last Updated**: 2026-02-24  
**Version**: 1.0
