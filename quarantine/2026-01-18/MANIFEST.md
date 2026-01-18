# Quarantine Manifest — 2026-01-18

**Reason**: Post-Quinean housekeeping. These backup files were created by previous editing sessions and are no longer needed in the active codebase. Per governance rules, files are quarantined rather than deleted.

**Action taken by**: Claude Code (Opus 4.5)

---

## Files Quarantined

| Original Path | Reason | Date of Backup |
|---------------|--------|----------------|
| `app/tasks/pipeline.py.backup_20260102_092616` | Superseded by current pipeline.py | 2026-01-02 |
| `app/tasks/pipeline.py.backup_20260102_183140` | Superseded by current pipeline.py | 2026-01-02 |
| `lib/combined_resolver.py.backup_20260102_183140` | Superseded by current combined_resolver.py | 2026-01-02 |
| `src/services/rulegraph_v2_builder.py.backup_20260102_092616` | Superseded by current rulegraph_v2_builder.py | 2026-01-02 |
| `src/services/rulegraph_v2_builder.py.backup_20260102_183140` | Superseded by current rulegraph_v2_builder.py | 2026-01-02 |
| `README_v18_3.md.backup` | Old README version, superseded | Unknown |

---

## Recovery

To restore any file:
```bash
git mv quarantine/2026-01-18/<filename> <original_path>
git commit -m "Restore <filename> from quarantine"
```

Or to view without restoring:
```bash
cat quarantine/2026-01-18/<filename>
```

---

## Governance Reference

Per `Project_Constitution.md`:
> No deletions of kept files; obsolete files are moved under `quarantine/YYYY-MM-DD/` via PRs.
