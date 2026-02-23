# Health Check & Scheduled Testing Setup

**Date**: February 8, 2026
**Purpose**: Automated regression detection and system health monitoring

---

## Quick Start

```bash
# Run health check manually
./bin/scheduled_health_check.sh

# Run with macOS notification on failure
./bin/scheduled_health_check.sh --notify

# Run and create ruthless bundle if tests fail
./bin/scheduled_health_check.sh --bundle

# Full options
./bin/scheduled_health_check.sh --notify --bundle

# Run Web/BN health gates directly
python3 scripts/check_web_bn_health.py
python3 scripts/check_web_bn_health.py --json
```

Web/BN gate thresholds are configured in:
- `config/web_bn_health_thresholds.json`

---

## Output Files

| File | Purpose |
|------|---------|
| `logs/health_check_YYYY-MM-DD.log` | Daily log file |
| `logs/test_history.csv` | Historical test counts for trend analysis |
| `logs/latest_status.json` | Machine-readable current status |

---

## Schedule with Cron (Linux/macOS)

Edit crontab:
```bash
crontab -e
```

Add one of these lines:

```bash
# Daily at 3am
0 3 * * * /Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/bin/scheduled_health_check.sh --notify >> /tmp/ae_health.log 2>&1

# Every 6 hours
0 */6 * * * /Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/bin/scheduled_health_check.sh >> /tmp/ae_health.log 2>&1

# Weekly on Sunday at midnight (with bundle on failure)
0 0 * * 0 /Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/bin/scheduled_health_check.sh --notify --bundle >> /tmp/ae_health.log 2>&1
```

---

## Schedule with launchd (macOS - Recommended)

### Step 1: Create plist file

```bash
cat > ~/Library/LaunchAgents/com.articleeater.healthcheck.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.articleeater.healthcheck</string>

    <key>ProgramArguments</key>
    <array>
        <string>/Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/bin/scheduled_health_check.sh</string>
        <string>--notify</string>
    </array>

    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>

    <key>StandardOutPath</key>
    <string>/tmp/ae_health_stdout.log</string>

    <key>StandardErrorPath</key>
    <string>/tmp/ae_health_stderr.log</string>

    <key>WorkingDirectory</key>
    <string>/Users/davidusa/REPOS/Article_Eater_PostQuinean_v1</string>
</dict>
</plist>
EOF
```

### Step 2: Load the agent

```bash
launchctl load ~/Library/LaunchAgents/com.articleeater.healthcheck.plist
```

### Step 3: Verify it's loaded

```bash
launchctl list | grep articleeater
```

### To unload/stop

```bash
launchctl unload ~/Library/LaunchAgents/com.articleeater.healthcheck.plist
```

---

## GitHub Actions (CI/CD)

Create `.github/workflows/health_check.yml`:

```yaml
name: Article Eater Health Check

on:
  schedule:
    - cron: '0 9 * * *'  # Daily at 9am UTC
  push:
    branches: [main]
  workflow_dispatch:  # Manual trigger

jobs:
  health-check:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.13'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run tests
        run: |
          python -m pytest tests/ --tb=short -q

      - name: Upload test results
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: test-failure-logs
          path: logs/
```

---

## Interpreting Results

### Health Status

| Status | Meaning | Action |
|--------|---------|--------|
| HEALTHY | All tests pass, no regressions | None needed |
| DEGRADED | Tests pass but fewer than before | Investigate what changed |
| UNHEALTHY | Tests failing or files missing | Immediate attention |

### Test History Analysis

```bash
# View recent history
tail -10 logs/test_history.csv

# Find days with failures
grep -v ",0," logs/test_history.csv

# Plot trend (requires gnuplot)
gnuplot -e "set datafile separator ','; plot 'logs/test_history.csv' using 3 with lines title 'Passed'"
```

### Quick Status Check

```bash
# Current status
cat logs/latest_status.json | python -m json.tool

# One-liner health check
cat logs/latest_status.json | python -c "import sys,json; d=json.load(sys.stdin); print(f\"{d['health']}: {d['passed']}P/{d['failed']}F\")"
```

---

## Ruthless Review Integration

When health check fails, it can automatically create a bundle for external review:

```bash
# Manual: create bundle after seeing failures
./bin/ruthless_review.sh --test

# Automatic: health check creates bundle on failure
./bin/scheduled_health_check.sh --bundle
```

The bundle can then be uploaded to ChatGPT/Gemini for ruthless critique.

---

## Recommended Schedule

| Frequency | When | Flags | Purpose |
|-----------|------|-------|---------|
| Daily | 9am | `--notify` | Catch overnight breakage |
| Weekly | Sunday midnight | `--notify --bundle` | Deep review with external LLM |
| On commit | CI/CD | (GitHub Actions) | Prevent broken merges |

---

*Last updated: February 8, 2026*
