# Safe Update Procedure (Governance-Compliant)

Use `scripts/update_safe.py` to apply a new Article Eater release on top of an existing GitHub-cloned repo **without deleting anything**. Any file that would be overwritten is first copied to `quarantine/<timestamp>/...`.

## Typical usage

**Dry-run first (see what would change):**
```bash
python scripts/update_safe.py --source /path/to/Article_Eater_v20_2_1_full.zip --target /path/to/your/repo --dry-run
```

**Apply the update (backup/replace):**
```bash
python scripts/update_safe.py --source /path/to/Article_Eater_v20_2_1_full.zip --target /path/to/your/repo --apply --db ./ae.db
```

Use a concatenated TXT as the source:
```bash
python scripts/update_safe.py --source /path/to/Article_Eater_v20_2_1_full_concatenated.txt --target . --apply --db ./ae.db
```

## Guarantees
- **No deletions.** Any overwritten file is quarantined into `quarantine/<timestamp>/<relpath>`.
- **Additive.** Files not in the update are untouched.
- **Migrations.** If you pass `--db ./ae.db`, it runs `scripts/migrate_v20.py` afterward.
- **Concatenated TXT support.** Understands our standard marker format.

## Notes
- Local edits are preserved in `quarantine/` before overwrite (recoverable).
- CI/governance files from the update are applied additively; existing ones get quarantined backups.
- To revert, restore from the matching `quarantine/<timestamp>/` snapshot.