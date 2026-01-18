# Changelog


## [0.2.3] - 2025-12-25

### Added
- Changelog template enforcement for releases (requires filled sections).

### Changed
- Release flow now validates changelog before packaging.
- Defaults/docs updated to v0.2.2 where referenced.

### Fixed
- Changelog section parsing for existing versions.

### Notes
- Release v0.2.3


## [0.2.2] - 2025-12-25

- Release v0.2.2
- Release pack now emitted under `Releases/EnvKit_Bootstrap_Pack_vX.Y.Z.zip`.
- `./bin/prod_smoke.sh` handles endpoints more robustly and skips compose when absent.
- Version propagation handles filenames with spaces.


## [0.2.1] - 2025-12-25

- Release v0.2.1


## [0.2.1] - 2025-12-25

- Release v0.2.1

## [0.2.1] - 2025-12-25

### Added
- Default `testing.command` in `envkit.yml` pointing to `./bin/self_test.sh`.
- `bin/self_test.sh` for fast, safe pack validation.
- `bin/deploy_envkit.sh` for non-destructive deployment into a target repo.

### Changed
- `bin/test.sh` now parses quoted *and* unquoted YAML command scalars more robustly.


## [0.2.0] - 2025-12-25

### Added
- Version governance via `VERSION.txt` and `bin/version.sh`.
- Test runner stub `bin/test.sh` (configured via `envkit.yml`).
- Changelog helper `bin/changelog.sh`.
- AI context generator `bin/context.sh` that writes `.aidev/context.md`.
- Claude session helpers: `bin/claude_start.sh`, `bin/claude_diagnose.sh`.
- Claude support templates: `templates/claude_instructions.md`, `templates/claude_safe_commands.yaml`.
- Multi-AI support directory `.aidev/` with `known_errors.yaml` and `claude_memory.md`.

### Changed
- `envkit/cli.py` expanded with v0.2 commands (version, bump, context, claude-start, diagnose).
- `AGENTS.md` updated for multi-AI workflow.

## [0.1.0] - Initial

- EnvKit Bootstrap Pack v0.1.
