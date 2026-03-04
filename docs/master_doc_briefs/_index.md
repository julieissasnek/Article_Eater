# Master Doc Brief Index

**Generated**: 2026-03-04
**Total MDBs**: 0 (initial deployment — no sessions have completed since protocol launch)
**Coverage**: Ready to collect MDBs from future sessions

---

## Upcoming MDBs (Expected Next Sessions)

The following work items are candidates for MDB documentation in upcoming sessions:

| Expected Date | Likely Agent | Topic | Notes |
|---|---|---|---|
| 2026-03-05+ | AG | H12 V3 Re-extraction (59+1,002 articles) | Large handoff from CW. Should document extraction process, decision on which prompts to use, results/metrics. |
| 2026-03-05+ | CW | RV5-4 Vision Attributes Integration | Audit of AG's 12 new vision attributes for CVA integration. Document which attributes integrated, any modifications made, integration points. |
| 2026-03-05+ | Either | DB Vocabulary Alignment | Re-extraction will produce new environment/outcome IDs. Probably needs MDB to document schema migration, backfill process. |
| 2026-03-10+ | AG | CVA-IMPL Phase 3-4 Continuation | Continuation of existing work. Document progress on visual attribute integration. |

---

## Index Format

Once sessions begin and MDBs are produced, they'll appear in a table like this:

| Date | Agent | Topic | Status | Master Doc Impact | Key Metrics | Notes |
|---|---|---|---|---|---|---|
| 2026-02-28 | CW | Extraction Field Validator | FINAL | Part III.2, IV.1 | 50 rules, 1,009 articles scored, 0.786 mean quality | Low-risk, straightforward validation gate |
| 2026-03-01 | AG | Vision Attributes Batch 1 | FINAL | Part VI, VII | 12 attributes, 120 tests pass | All CPU-efficient, ready for CVA integration |
| 2026-03-04 | CC | Overseer Critical Fixes | FINAL | Part III.3 | 3 bugs fixed, AESHI 65→70 | Medium-risk SQL issue, now resolved |

---

## How to Use This Index

### For agents (Creating MDBs):
1. If your work is significant, create an MDB in this directory
2. Name it: `MDB_{AGENT}_{DATE}_{TOPIC}.md`
3. Include all required sections from the template
4. This index will be regenerated weekly to reflect new MDBs

### For CW (Integration Steward):
1. Check this index weekly for new MDBs (Monday AM)
2. Read each FINAL-status MDB
3. Integrate content into appropriate Part of master document
4. Mark MDB status as "INTEGRATED" in an update to this file

### For David (System Owner):
1. Scan this index to see what work has been completed since last review
2. Check "Master Doc Impact" column to see where documentation needs updating
3. Review any MDBs with "PANEL REVIEW NEEDED" flag (would appear in the main index once sessions produce them)

---

## Regeneration Schedule

This index is regenerated:
- **Weekly** (Monday AM by CW) — captures new MDBs from prior week
- **After each multi-session sprint** — full audit of all MDBs
- **Pre-release** — comprehensive review before version tag

To regenerate manually:
```bash
python3 scripts/regenerate_mdb_index.py
```

(This script is planned for future development. Manual updates for now.)

---

## Status Legend

- **DRAFT** — MDB created but not finalized (agent still filling in sections)
- **FINAL** — MDB complete and ready for integration
- **INTEGRATED** — CW has read and incorporated into master document
- **ARCHIVED** — Old MDB, superseded by newer work (kept for historical reference)

---

## Notes for Future Development

1. **Auto-linking**: Eventually, MDB files should link directly to code artifacts (GitHub URLs) and figure dependencies
2. **Consistency checking**: A linter should verify all required MDB sections are complete
3. **Master doc map**: A visualization showing which Parts depend on which MDBs
4. **Backfill**: Any significant work done before 2026-03-04 could be retroactively documented with "archived" MDBs for institutional memory

---

**Last updated**: 2026-03-04 (Initial deployment)
**Next update**: 2026-03-10 (or whenever first post-protocol MBDs are created)
