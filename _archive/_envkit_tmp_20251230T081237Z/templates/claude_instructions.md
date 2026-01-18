# Claude Instructions

## Session Start
1. Run `./bin/claude_start.sh`
2. Read `AGENTS.md`
3. Read `.aidev/context.md`

## Safe Commands
- `./bin/prod_smoke.sh`
- `./bin/test.sh`
- `./bin/version.sh check`
- `cat`, `ls`, `find`, `grep`

## Require Care
- `./bin/version.sh bump`
- `git commit`
- `pip install`

## Forbidden
- `rm -rf`
- `sudo`
- `git reset --hard`

## On Error
Run: `./bin/claude_diagnose.sh "error message"`

## Session End
1. Update `.aidev/claude_memory.md`
2. `./bin/version.sh bump` if code changed
3. `./bin/prod_smoke.sh`
