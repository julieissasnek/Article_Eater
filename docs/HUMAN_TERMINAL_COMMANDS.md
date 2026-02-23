# HUMAN TERMINAL COMMANDS
## Tasks requiring macOS terminal (sandbox prevents AI execution)

---

### R-07: Load Extraction CSV → Database
```bash
cd /Users/davidusa/REPOS/Article_Eater_PostQuinean_v1 && python3 scripts/load_extraction_csv_to_db.py --verbose
```
**What it does**: Loads 172K extraction rows from CSV into `ae.db`.

---

### R-08: Seed Beliefs from Calibrated Templates
```bash
cd /Users/davidusa/REPOS/Article_Eater_PostQuinean_v1 && PYTHONPATH=. python3 scripts/seed_beliefs_from_templates.py --clear-existing
```
**What it does**: Seeds beliefs from 37 calibrated templates into the Web of Belief. `--clear-existing` wipes prior beliefs first.

**Run R-07 first, then R-08.**

---

### M-03b: Run Variable Migration (BLOCKED — wait for CC to finish M-01)
```bash
cd /Users/davidusa/REPOS/Article_Eater_PostQuinean_v1 && python3 scripts/migrate_variables.py --dry-run
```
Preview first with `--dry-run`, then run without flag to apply. Renames 346 variable references across 47 templates to canonical names.

---

### Variable Lint Check
```bash
cd /Users/davidusa/REPOS/Article_Eater_PostQuinean_v1 && python3 scripts/lint_variables.py
```
Reports any unregistered variable names in templates. After migration, all should PASS.

---

*Generated 2026-02-22 by OPUS/AG*
