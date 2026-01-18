# EnvKit v0.2 Enhancement Spec

## Context for ChatGPT

You created EnvKit v0.1 — a shell-first dev environment manager. I've had it reviewed by Claude and a simulated expert panel. Below are the specific enhancements needed. Please implement them.

## Current EnvKit v0.1 Structure

```
EnvKit_Bootstrap_Pack_v0.1/
├── AGENTS.md                    # AI safety contract (minimal)
├── PROJECT_CONSTITUTION.md      # 5 principles
├── README.md
├── bin/
│   ├── prod_smoke.sh            # One truth command
│   └── release_and_smoke.sh     # Release gate
├── deconcat.py                  # LLM file utility
├── envkit/
│   ├── __init__.py
│   ├── cli.py                   # Minimal CLI
│   └── requirements.txt
├── envkit.yml                   # Per-repo config
├── envkit_bootstrap.sh          # Idempotent setup
└── templates/
    ├── codex_config.toml        # OpenAI Codex settings
    └── codex_default.rules      # Codex exec policy
```

## What's Good (Keep These)

1. **Archive before replace** — `_archive/envkit/<timestamp>/`
2. **One truth command** — `./bin/prod_smoke.sh`
3. **Idempotent bootstrap** — Run N times, same result
4. **Fingerprint-based rebuild** — Only rebuild when inputs change
5. **deconcat.py** — Practical LLM utility

---

## Required Enhancements

### 1. VERSION GOVERNANCE

**Problem:** EnvKit reads `VERSION.txt` but doesn't manage it.

**Solution:** Add version auto-increment and propagation.

Create `bin/version.sh`:

```bash
#!/usr/bin/env bash
# Usage: ./bin/version.sh [bump|check|set X.Y.Z]

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION_FILE="$ROOT/VERSION.txt"

current() {
  [[ -f "$VERSION_FILE" ]] && cat "$VERSION_FILE" | tr -d ' \r\n\t' || echo "0.0.0"
}

bump_patch() {
  local v="$(current)"
  local major=$(echo "$v" | cut -d. -f1)
  local minor=$(echo "$v" | cut -d. -f2)
  local patch=$(echo "$v" | cut -d. -f3)
  echo "$major.$minor.$((patch + 1))"
}

case "${1:-check}" in
  check)
    echo "$(current)"
    ;;
  bump)
    new="$(bump_patch)"
    echo "$new" > "$VERSION_FILE"
    echo "Bumped: $(current) → $new"
    ;;
  set)
    echo "$2" > "$VERSION_FILE"
    echo "Set: $2"
    ;;
  *)
    echo "Usage: $0 [check|bump|set X.Y.Z]"
    exit 1
    ;;
esac
```

Add to `envkit.yml`:

```yaml
versioning:
  file: "VERSION.txt"
  auto_bump_on_commit: true
  propagate_to:
    - "src/__init__.py:__version__"
    - "package.json:version"
```

---

### 2. TEST INTEGRATION

**Problem:** `prod_smoke.sh` only checks health endpoints, not tests.

**Solution:** Add test runner before smoke.

Update `envkit.yml`:

```yaml
testing:
  enabled: true
  command: "pytest tests/ -v"        # or "npm test" or custom
  required_before:
    - commit
    - release
  on_failure: "block"                # block | warn | ignore
```

Create `bin/test.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# Read test command from envkit.yml
TEST_CMD="$(grep -A1 'testing:' envkit.yml | grep 'command:' | sed 's/.*command:\s*"\(.*\)"/\1/' || echo "")"

if [[ -z "$TEST_CMD" ]]; then
  echo "No test command configured in envkit.yml"
  exit 0
fi

echo "== RUNNING TESTS =="
echo "Command: $TEST_CMD"
eval "$TEST_CMD"
```

Update `prod_smoke.sh` to call tests first:

```bash
# Add after fingerprint check, before rebuild
if [[ -x "./bin/test.sh" ]]; then
  ./bin/test.sh || { echo "Tests failed, aborting."; exit 1; }
fi
```

---

### 3. CHANGELOG AUTOMATION

**Problem:** No changelog tracking.

**Solution:** Auto-append to CHANGELOG.md on version bump.

Create `bin/changelog.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

CHANGELOG="$ROOT/CHANGELOG.md"
VERSION="$(./bin/version.sh check)"
DATE="$(date +%Y-%m-%d)"
MSG="${1:-No description}"

# Create if doesn't exist
if [[ ! -f "$CHANGELOG" ]]; then
  echo "# Changelog" > "$CHANGELOG"
  echo "" >> "$CHANGELOG"
fi

# Prepend new entry (after header)
ENTRY="## [$VERSION] - $DATE

- $MSG
"

# Insert after first line
head -2 "$CHANGELOG" > "$CHANGELOG.tmp"
echo "$ENTRY" >> "$CHANGELOG.tmp"
tail -n +3 "$CHANGELOG" >> "$CHANGELOG.tmp"
mv "$CHANGELOG.tmp" "$CHANGELOG"

echo "Changelog updated: $VERSION - $MSG"
```

---

### 4. AI CONTEXT DOCUMENT

**Problem:** AGENTS.md has rules but no project situational awareness.

**Solution:** Auto-generate `context.md` that gives AI understanding of project state.

Create `bin/context.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

CONTEXT="$ROOT/.aidev/context.md"
mkdir -p "$(dirname "$CONTEXT")"

VERSION="$(./bin/version.sh check 2>/dev/null || echo 'unknown')"
LAST_MODIFIED="$(date -r VERSION.txt +%Y-%m-%d 2>/dev/null || date +%Y-%m-%d)"

# Count files
PY_COUNT="$(find . -name '*.py' -not -path './.venv/*' -not -path './_archive/*' 2>/dev/null | wc -l | tr -d ' ')"
SH_COUNT="$(find . -name '*.sh' 2>/dev/null | wc -l | tr -d ' ')"

# Recent git commits (if git repo)
RECENT_COMMITS=""
if [[ -d ".git" ]]; then
  RECENT_COMMITS="$(git log --oneline -5 2>/dev/null || echo 'No git history')"
fi

cat > "$CONTEXT" << EOF
# Project Context (Auto-Generated)

Generated: $(date +%Y-%m-%d\ %H:%M:%S)

## Current State
- Version: $VERSION
- Last modified: $LAST_MODIFIED
- Python files: $PY_COUNT
- Shell scripts: $SH_COUNT

## Directory Structure
\`\`\`
$(find . -maxdepth 2 -type f -not -path './_archive/*' -not -path './.git/*' -not -name '*.pyc' | head -30 | sort)
\`\`\`

## Recent Changes
\`\`\`
$RECENT_COMMITS
\`\`\`

## Key Commands
- \`./bin/prod_smoke.sh\` — verify everything works
- \`./bin/test.sh\` — run test suite
- \`./bin/version.sh bump\` — increment version
- \`./bin/release.sh\` — create release

## Conventions
- Archive before replacing (never delete)
- Increment version on code changes
- Run tests before commit
- Use fingerprinting to avoid unnecessary rebuilds
EOF

echo "Context generated: $CONTEXT"
```

---

### 5. MULTI-AI SUPPORT

**Problem:** Only Codex templates exist.

**Solution:** Add Claude templates alongside Codex, plus a Claude-specific bootstrap workflow.

---

#### 5a. Claude Instructions

Create `templates/claude_instructions.md`:

```markdown
# Claude Instructions for This Project

## Before Any Action
1. Read `.aidev/context.md` for project state
2. Read `AGENTS.md` for safety rules
3. Check current version: `./bin/version.sh check`

## Safe Commands (Always OK)
- `./bin/prod_smoke.sh`
- `./bin/test.sh`
- `./bin/version.sh check`
- `cat`, `ls`, `find`, `grep`
- `python -m pytest`

## Commands Requiring Care
- `./bin/version.sh bump` — changes VERSION.txt
- `git commit` — permanent
- `pip install` — changes environment

## Forbidden
- `rm -rf`
- `git reset --hard`
- `git clean -fd`
- Any command with `sudo`

## On Error
1. Capture full error output
2. Check if it matches known patterns in `.aidev/known_errors.yaml`
3. If auto-fix exists, apply it
4. If not, report diagnosis and stop
```

---

#### 5b. Claude Safe Commands

Create `templates/claude_safe_commands.yaml`:

```yaml
# Claude computer use command whitelist

always_allowed:
  - "./bin/prod_smoke.sh"
  - "./bin/test.sh"
  - "./bin/version.sh"
  - "./bin/context.sh"
  - "./bin/changelog.sh"
  - "./envkit_bootstrap.sh"
  - "cat"
  - "ls"
  - "find"
  - "grep"
  - "head"
  - "tail"
  - "wc"
  - "diff"
  - "python -c"
  - "python -m pytest"
  - "python -m py_compile"
  - "pip list"
  - "pip show"
  - "git status"
  - "git log"
  - "git diff"
  - "docker ps"
  - "docker compose ps"

prompt_before:
  - "git commit"
  - "git push"
  - "git pull"
  - "pip install"
  - "./bin/version.sh bump"
  - "./bin/release.sh"
  - "docker compose up"
  - "docker compose down"

forbidden:
  - "rm -rf"
  - "rm -r"
  - "sudo"
  - "git reset --hard"
  - "git clean"
  - "curl | bash"
  - "wget | bash"
  - "eval"
  - "> /dev"
  - "mkfs"
  - "dd if="
```

---

#### 5c. Claude Session Bootstrap

Create `bin/claude_start.sh` — A script Claude runs at the start of any session:

```bash
#!/usr/bin/env bash
# Claude session bootstrap — run this first in any Claude session
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "═══════════════════════════════════════════════════════════════════"
echo "  CLAUDE SESSION BOOTSTRAP"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "Project: $(basename "$ROOT")"
echo "Path: $ROOT"
echo ""

# Version
if [[ -f "VERSION.txt" ]]; then
  echo "Version: $(cat VERSION.txt | tr -d ' \r\n\t')"
else
  echo "Version: (no VERSION.txt)"
fi

# Git status
if [[ -d ".git" ]]; then
  BRANCH="$(git branch --show-current 2>/dev/null || echo 'unknown')"
  CHANGES="$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')"
  echo "Git: branch=$BRANCH, uncommitted=$CHANGES"
fi

# Test status
echo ""
echo "Running quick health check..."
if [[ -x "./bin/test.sh" ]]; then
  if ./bin/test.sh >/dev/null 2>&1; then
    echo "Tests: ✓ passing"
  else
    echo "Tests: ✗ FAILING — run ./bin/test.sh for details"
  fi
else
  echo "Tests: (no test.sh configured)"
fi

# Regenerate context
if [[ -x "./bin/context.sh" ]]; then
  ./bin/context.sh >/dev/null 2>&1
  echo ""
  echo "AI context regenerated: .aidev/context.md"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "  READY"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "Key commands:"
echo "  ./bin/prod_smoke.sh     — verify everything works"
echo "  ./bin/test.sh           — run test suite"
echo "  ./bin/version.sh bump   — increment version"
echo "  ./bin/release.sh        — create release"
echo ""
echo "Read .aidev/context.md for project state."
echo "Read AGENTS.md for safety rules."
echo ""
```

---

#### 5d. Claude Error Diagnosis Script

Create `bin/claude_diagnose.sh` — Claude runs this when something fails:

```bash
#!/usr/bin/env bash
# Claude error diagnosis — analyzes error output against known patterns
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

ERROR_INPUT="${1:-}"
KNOWN_ERRORS="$ROOT/.aidev/known_errors.yaml"

if [[ -z "$ERROR_INPUT" ]]; then
  echo "Usage: ./bin/claude_diagnose.sh 'error message or output'"
  echo ""
  echo "Analyzes error against known patterns in .aidev/known_errors.yaml"
  exit 1
fi

echo "═══════════════════════════════════════════════════════════════════"
echo "  ERROR DIAGNOSIS"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "Input: $ERROR_INPUT"
echo ""

if [[ ! -f "$KNOWN_ERRORS" ]]; then
  echo "No known_errors.yaml found. Cannot diagnose."
  exit 1
fi

# Simple pattern matching (Claude can do more sophisticated analysis)
MATCHED=0

# Check each pattern
while IFS= read -r pattern; do
  pattern="$(echo "$pattern" | sed 's/.*pattern: "\(.*\)"/\1/')"
  [[ -z "$pattern" ]] && continue
  
  if echo "$ERROR_INPUT" | grep -qi "$pattern"; then
    MATCHED=1
    echo "MATCHED PATTERN: $pattern"
    
    # Extract diagnosis and fix from yaml (simplified)
    grep -A3 "pattern: \"$pattern\"" "$KNOWN_ERRORS" | grep -E '(diagnosis|auto_fix|manual_fix):' || true
    echo ""
  fi
done < <(grep 'pattern:' "$KNOWN_ERRORS")

if [[ $MATCHED -eq 0 ]]; then
  echo "No known pattern matched."
  echo ""
  echo "Suggestions:"
  echo "  1. Search error message online"
  echo "  2. Check if dependency is missing: pip list | grep <name>"
  echo "  3. Check environment: python --version, which python"
  echo "  4. Add new pattern to .aidev/known_errors.yaml if you solve it"
fi
```

---

#### 5e. Claude Memory File

Create `.aidev/claude_memory.md` — Claude updates this file to persist learnings across sessions:

```markdown
# Claude Memory — Project-Specific Learnings

This file is updated by Claude to remember things across sessions.
Human can review and edit.

## Installation Notes
<!-- Claude: Add any installation quirks discovered -->

## Common Issues & Fixes
<!-- Claude: Add issues you've solved -->

## User Preferences
<!-- Claude: Note any user preferences about code style, workflow, etc. -->

## Session Log
<!-- Claude: Brief note after each session -->

---
*Last updated: (Claude fills this in)*
```

---

#### 5f. Updated AGENTS.md for Multi-AI

Update `AGENTS.md` to work with both Codex and Claude:

```markdown
# Repo Agent Contract

This contract applies to ALL AI assistants working on this repository:
- OpenAI Codex / ChatGPT
- Anthropic Claude
- Any other AI agent

## Golden Command
```
./bin/prod_smoke.sh
```
When in doubt, run this. It verifies everything works.

## Safety Rules (All AIs)

1. **No deletions.** Archive before replacing. Use `_archive/` directory.

2. **Minimal changes.** Make the smallest change that solves the problem.

3. **Reversible only.** Every change must be reversible.

4. **Test first.** Run `./bin/test.sh` before committing.

5. **Version always.** Bump version on any code change: `./bin/version.sh bump`

6. **No bypass.** Do not skip release gates or tests.

## Provider-Specific

### For Claude (Anthropic)
- Run `./bin/claude_start.sh` at session start
- Read `.aidev/context.md` for project state
- Update `.aidev/claude_memory.md` with learnings
- Use `./bin/claude_diagnose.sh` for error analysis

### For Codex (OpenAI)
- Follow `templates/codex_config.toml` settings
- Follow `templates/codex_default.rules` for command approval

## Forbidden Commands (All AIs)

```
rm -rf, rm -r (use archive instead)
sudo (never)
git reset --hard (destructive)
git clean (destructive)
curl | bash, wget | bash (unsafe)
eval (unsafe)
```

## On Error

1. Capture full error output
2. Run `./bin/claude_diagnose.sh "error message"` (Claude) or check patterns manually (Codex)
3. If auto-fix exists in `.aidev/known_errors.yaml`, apply it
4. If not, report diagnosis to human and STOP

## Session Checklist

### Start of Session
- [ ] Read AGENTS.md (this file)
- [ ] Read .aidev/context.md
- [ ] Run ./bin/prod_smoke.sh
- [ ] Note current version

### End of Session
- [ ] Run tests: ./bin/test.sh
- [ ] Bump version if code changed: ./bin/version.sh bump
- [ ] Update .aidev/claude_memory.md (Claude only)
- [ ] Summary for human
```

---

#### 5g. Concatenate Script for Claude

Create `bin/concat_for_claude.sh` — Prepares project files for pasting into Claude:

```bash
#!/usr/bin/env bash
# Concatenate key project files for Claude context
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

OUTPUT="${1:-/tmp/project_context.txt}"

echo "Concatenating project files for Claude..."

{
  echo "═══════════════════════════════════════════════════════════════════"
  echo "PROJECT CONTEXT FOR CLAUDE"
  echo "Generated: $(date)"
  echo "═══════════════════════════════════════════════════════════════════"
  echo ""
  
  # Key files to include
  FILES=(
    "AGENTS.md"
    ".aidev/context.md"
    ".aidev/claude_memory.md"
    "VERSION.txt"
    "envkit.yml"
  )
  
  for f in "${FILES[@]}"; do
    if [[ -f "$ROOT/$f" ]]; then
      echo ""
      echo "----- FILE PATH: $f"
      echo "----- CONTENT START -----"
      cat "$ROOT/$f"
      echo ""
      echo "----- CONTENT END -----"
    fi
  done
  
  echo ""
  echo "═══════════════════════════════════════════════════════════════════"
  echo "DIRECTORY STRUCTURE"
  echo "═══════════════════════════════════════════════════════════════════"
  find . -maxdepth 3 -type f \
    -not -path './_archive/*' \
    -not -path './.git/*' \
    -not -path './.venv/*' \
    -not -path './releases/*' \
    -not -name '*.pyc' \
    | sort
    
} > "$OUTPUT"

echo "Created: $OUTPUT"
echo "Size: $(wc -l < "$OUTPUT") lines"
echo ""
echo "Paste this into Claude or use: cat $OUTPUT | pbcopy"
```

---

### 6. FINGERPRINT FROM CONFIG

**Problem:** Fingerprint files are hardcoded in `prod_smoke.sh`.

**Solution:** Read from `envkit.yml`.

Update `prod_smoke.sh` to read fingerprint config:

```bash
# Replace hardcoded file list with:
FP_FILES="$(grep -A20 'fingerprint:' envkit.yml | grep -A10 'files:' | grep '^\s*-' | sed 's/^\s*-\s*"\(.*\)"/\1/' | tr '\n' ' ')"
FP_DIRS="$(grep -A20 'fingerprint:' envkit.yml | grep -A10 'dirs:' | grep '^\s*-' | sed 's/^\s*-\s*"\(.*\)"/\1/' | tr '\n' ' ')"

FP="$(
  ( \
    for f in $FP_FILES; do
      [[ -f "$f" ]] && shasum -a 256 "$f" 2>/dev/null
    done
    for d in $FP_DIRS; do
      [[ -d "$d" ]] && find "$d" -type f -print0 2>/dev/null | LC_ALL=C sort -z | xargs -0 shasum -a 256 2>/dev/null
    done
  ) | shasum -a 256 | awk '{print $1}'
)"
```

---

### 7. RELEASE ARTIFACTS

**Problem:** No versioned release archives.

**Solution:** Create `bin/release.sh` that produces distributable artifacts.

```bash
#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

VERSION="$(./bin/version.sh check)"
RELEASES_DIR="$ROOT/releases"
RELEASE_ZIP="$RELEASES_DIR/v${VERSION}.zip"

echo "== CREATING RELEASE v$VERSION =="

# Run tests first
./bin/test.sh || { echo "Tests failed, aborting release."; exit 1; }

# Create releases directory
mkdir -p "$RELEASES_DIR"

# Check if release already exists
if [[ -f "$RELEASE_ZIP" ]]; then
  echo "ERROR: Release v$VERSION already exists."
  echo "Bump version first: ./bin/version.sh bump"
  exit 1
fi

# Create zip (exclude dev files)
zip -r "$RELEASE_ZIP" . \
  -x "*.pyc" \
  -x "*__pycache__*" \
  -x "*.git*" \
  -x "_archive/*" \
  -x "releases/*" \
  -x ".venv/*" \
  -x "*.db"

echo "Created: $RELEASE_ZIP"
echo "Size: $(du -h "$RELEASE_ZIP" | cut -f1)"

# Update changelog
./bin/changelog.sh "Release v$VERSION"

echo "OK: Release v$VERSION complete"
```

---

### 8. KNOWN ERROR PATTERNS

**Problem:** No self-diagnosis.

**Solution:** Add known error database.

Create `.aidev/known_errors.yaml`:

```yaml
# Known error patterns and fixes

errors:
  - pattern: "No module named 'flask'"
    diagnosis: "Flask not installed"
    auto_fix: "pip install flask"
    
  - pattern: "externally-managed-environment"
    diagnosis: "System Python is locked (PEP 668)"
    auto_fix: "python3 -m venv .venv && source .venv/bin/activate"
    
  - pattern: "Address already in use"
    diagnosis: "Port already occupied"
    auto_fix: "lsof -ti:${PORT} | xargs kill -9"
    
  - pattern: "SSL: CERTIFICATE_VERIFY_FAILED"
    diagnosis: "macOS SSL certificates not installed"
    manual_fix: "Run /Applications/Python*/Install Certificates.command"
    
  - pattern: "ModuleNotFoundError"
    diagnosis: "Missing Python dependency"
    auto_fix: "pip install -r requirements.txt"
    
  - pattern: "command not found: docker"
    diagnosis: "Docker not installed or not in PATH"
    manual_fix: "Install Docker Desktop from docker.com"
    
  - pattern: "Cannot connect to the Docker daemon"
    diagnosis: "Docker daemon not running"
    manual_fix: "Start Docker Desktop application"
```

---

### 9. UNIFIED CLI

**Problem:** CLI is minimal (only smoke/release).

**Solution:** Expand `envkit/cli.py`:

```python
#!/usr/bin/env python3
"""
EnvKit CLI — Unified development environment commands.

Usage:
    envkit smoke          Run prod smoke test
    envkit test           Run test suite
    envkit release        Create versioned release
    envkit version        Show current version
    envkit bump           Increment patch version
    envkit context        Generate AI context document
    envkit status         Show project health
    envkit claude-start   Bootstrap Claude session
    envkit diagnose       Diagnose error (Claude)
    envkit concat         Prepare files for Claude
"""
from __future__ import annotations
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def run(script: str, *args) -> int:
    cmd = [str(ROOT / "bin" / script)] + list(args)
    return subprocess.call(cmd)

def cmd_smoke(args):
    return run("prod_smoke.sh")

def cmd_test(args):
    return run("test.sh")

def cmd_release(args):
    return run("release.sh")

def cmd_version(args):
    return run("version.sh", "check")

def cmd_bump(args):
    return run("version.sh", "bump")

def cmd_context(args):
    return run("context.sh")

def cmd_claude_start(args):
    return run("claude_start.sh")

def cmd_diagnose(args):
    error_msg = args.error if hasattr(args, 'error') and args.error else ""
    return run("claude_diagnose.sh", error_msg)

def cmd_concat(args):
    return run("concat_for_claude.sh")

def cmd_status(args):
    print("== PROJECT STATUS ==")
    run("version.sh", "check")
    print()
    
    # Check if tests pass
    print("Tests: ", end="", flush=True)
    result = subprocess.run([str(ROOT / "bin" / "test.sh")], 
                          capture_output=True, text=True)
    print("✓ passing" if result.returncode == 0 else "✗ failing")
    
    # Check git status
    if (ROOT / ".git").exists():
        result = subprocess.run(["git", "status", "--porcelain"], 
                              capture_output=True, text=True, cwd=ROOT)
        changes = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
        print(f"Git: {changes} uncommitted changes")
    
    return 0

def main() -> int:
    parser = argparse.ArgumentParser(description="EnvKit CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    subparsers.add_parser("smoke", help="Run prod smoke test")
    subparsers.add_parser("test", help="Run test suite")
    subparsers.add_parser("release", help="Create versioned release")
    subparsers.add_parser("version", help="Show current version")
    subparsers.add_parser("bump", help="Increment patch version")
    subparsers.add_parser("context", help="Generate AI context")
    subparsers.add_parser("status", help="Show project health")
    subparsers.add_parser("claude-start", help="Bootstrap Claude session")
    
    diagnose_parser = subparsers.add_parser("diagnose", help="Diagnose error")
    diagnose_parser.add_argument("error", nargs="?", default="", help="Error message")
    
    subparsers.add_parser("concat", help="Prepare files for Claude")
    
    args = parser.parse_args()
    
    commands = {
        "smoke": cmd_smoke,
        "test": cmd_test,
        "release": cmd_release,
        "version": cmd_version,
        "bump": cmd_bump,
        "context": cmd_context,
        "status": cmd_status,
        "claude-start": cmd_claude_start,
        "diagnose": cmd_diagnose,
        "concat": cmd_concat,
    }
    
    return commands[args.command](args)

if __name__ == "__main__":
    sys.exit(main())
```

---

## Updated envkit.yml Template

```yaml
# envkit.yml — per-repo configuration

project:
  name: "MyProject"
  
runtime:
  kind: "python"   # docker_compose | python | node | mixed

versioning:
  file: "VERSION.txt"
  auto_bump_on_commit: true

testing:
  enabled: true
  command: "pytest tests/ -v"
  required_before:
    - commit
    - release
  on_failure: "block"

health:
  endpoints:
    - "http://localhost:8000/health"

fingerprint:
  files:
    - "requirements.txt"
    - "VERSION.txt"
  dirs:
    - "src"
    - "app"

ai:
  providers:
    - codex
    - claude
  context_file: ".aidev/context.md"
  known_errors: ".aidev/known_errors.yaml"
```

---

## Updated Directory Structure

```
project/
├── .aidev/
│   ├── context.md              # Auto-generated project state
│   ├── known_errors.yaml       # Error patterns + fixes
│   └── claude_memory.md        # Claude's persistent learnings (NEW)
│
├── bin/
│   ├── prod_smoke.sh           # One truth command (updated)
│   ├── release_and_smoke.sh
│   ├── test.sh                 # Run test suite (NEW)
│   ├── version.sh              # Version management (NEW)
│   ├── changelog.sh            # Changelog automation (NEW)
│   ├── context.sh              # Generate AI context (NEW)
│   ├── release.sh              # Create versioned release (NEW)
│   ├── claude_start.sh         # Claude session bootstrap (NEW)
│   ├── claude_diagnose.sh      # Claude error diagnosis (NEW)
│   └── concat_for_claude.sh    # Prepare files for Claude (NEW)
│
├── envkit/
│   ├── __init__.py
│   ├── cli.py                  # Full CLI (updated)
│   └── requirements.txt
│
├── releases/                   # Versioned artifacts (NEW)
│   └── v1.0.0.zip
│
├── templates/
│   ├── codex_config.toml       # OpenAI Codex settings
│   ├── codex_default.rules     # Codex exec policy
│   ├── claude_instructions.md  # Claude instructions (NEW)
│   └── claude_safe_commands.yaml # Claude command whitelist (NEW)
│
├── _archive/                   # Archive directory
│
├── AGENTS.md                   # Multi-AI contract (updated)
├── CHANGELOG.md                # Change history (NEW)
├── PROJECT_CONSTITUTION.md
├── README.md
├── VERSION.txt
├── deconcat.py
├── envkit.yml                  # Config (updated)
└── envkit_bootstrap.sh         # Bootstrap (updated)
```

---

## Summary of Changes

| Addition | Purpose |
|----------|---------|
| `bin/version.sh` | Version management (check/bump/set) |
| `bin/test.sh` | Run test suite from config |
| `bin/changelog.sh` | Auto-update changelog |
| `bin/context.sh` | Generate AI context document |
| `bin/release.sh` | Create versioned release zips |
| `bin/claude_start.sh` | Claude session bootstrap |
| `bin/claude_diagnose.sh` | Claude error analysis against known patterns |
| `bin/concat_for_claude.sh` | Prepare project files for Claude context |
| `.aidev/context.md` | AI situational awareness |
| `.aidev/known_errors.yaml` | Self-diagnosis patterns |
| `.aidev/claude_memory.md` | Claude's persistent learnings across sessions |
| `templates/claude_instructions.md` | Claude-specific guidelines |
| `templates/claude_safe_commands.yaml` | Claude command whitelist |
| `releases/` | Versioned distributable artifacts |
| `CHANGELOG.md` | Change history |
| Updated `AGENTS.md` | Multi-AI contract (Codex + Claude) |
| Updated `envkit/cli.py` | Full CLI with all commands |
| Updated `envkit.yml` | Versioning, testing, AI config |
| Updated `prod_smoke.sh` | Read fingerprint from config |

---

## Claude-Specific Workflow

### Session Start
```bash
./bin/claude_start.sh
```
This:
1. Shows project version and status
2. Runs quick health check
3. Regenerates `.aidev/context.md`
4. Displays key commands

### During Session
- Follow `AGENTS.md` rules
- Use `./bin/claude_diagnose.sh "error"` when things fail
- Run `./bin/test.sh` before major changes

### Session End
- Update `.aidev/claude_memory.md` with learnings
- Bump version if code changed: `./bin/version.sh bump`
- Run final smoke: `./bin/prod_smoke.sh`

### Sharing Context with Claude
```bash
./bin/concat_for_claude.sh
cat /tmp/project_context.txt | pbcopy
# Paste into Claude conversation
```

---

## Implementation Request

Please implement all the above changes and provide:

1. Updated `envkit_bootstrap.sh` that installs all new scripts
2. All new `bin/*.sh` scripts:
   - `version.sh`
   - `test.sh`
   - `changelog.sh`
   - `context.sh`
   - `release.sh`
   - `claude_start.sh`
   - `claude_diagnose.sh`
   - `concat_for_claude.sh`
3. Updated `envkit/cli.py` with full command set
4. Updated `envkit.yml` template
5. New template files:
   - `templates/claude_instructions.md`
   - `templates/claude_safe_commands.yaml`
6. New `.aidev/` files:
   - `known_errors.yaml`
   - `claude_memory.md` (template)
7. Updated `AGENTS.md` for multi-AI support
8. `CHANGELOG.md` template

Package as `EnvKit_Bootstrap_Pack_v0.2.zip`.
