# Smart Book: Dependency-Aware Documentation System

**Version**: 1.0
**Date**: March 3, 2026
**Status**: Operational

---

## Quick Start

The Smart Book system helps maintain consistency and detect dependencies across the ATLAS master documentation. It consists of three components:

1. **DEPENDENCY_MANIFEST.json** — Machine-readable specification of concepts, their definitions, and cross-section dependencies
2. **validate_master_doc.py** — Validation script that checks for consistency violations
3. **Design document** — Explains the precedents, architecture, and maintenance protocols

### Run a Quick Validation

```bash
cd /sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1
python scripts/validate_master_doc.py --mode=validate
```

Output shows violations grouped by severity (CRITICAL, HIGH, MEDIUM, LOW, INFO).

### Generate a Report

```bash
python scripts/validate_master_doc.py --mode=report --output=docs/VALIDATION_REPORT.md
```

Creates a markdown report of all violations for review or sharing.

### Get Suggested Fixes

```bash
python scripts/validate_master_doc.py --mode=suggest
```

Displays suggested actions for each violation.

---

## What It Checks

### 1. Numeric Constants (CRITICAL)

Ensures counts and fixed values are identical across all sections.

**Example**: T1.5 count must be 13 everywhere.

```
❌ VIOLATION: PART_VII_T15_REDUCTIONS says "1 T1.5 theory" but canonical value is 13
✓ FIX: Update PART_VII_T15_REDUCTIONS to state "13 T1.5 theories"
```

### 2. Stale References (HIGH)

Detects use of deprecated/superseded concepts without acknowledgment.

**Example**: Using legacy credence formula without noting it's deprecated.

```
❌ VIOLATION: PART_VI_DOMAIN_PANELS uses CREDENCE_FORMULA_LEGACY without "deprecated" note
✓ FIX: Either update to use CREDENCE_FORMULA_LOGODDS or add deprecation acknowledgment
```

### 3. Undefined Concepts (HIGH)

Ensures referenced concepts exist in the manifest.

```
❌ VIOLATION: §100 references undefined concept UNKNOWN_FACTOR
✓ FIX: Either define UNKNOWN_FACTOR in manifest or remove reference from §100
```

### 4. Missing Updates (MEDIUM)

Flags sections that may need review when foundational concepts change.

**Example**: When T1.5 count updated from 12→13, flags all sections that use it.

```
⚠ REVIEW: T1_5_COUNT updated on 2026-02-27. Sections §35, §40, §54, §78, §100, §115, §142, §147 may need review.
```

### 5. Dependency Completeness (MEDIUM)

Ensures critical concepts are properly defined in the manifest.

```
✓ All critical concepts (T1_5_COUNT, CREDENCE_FORMULA_LOGODDS, WARRANT_TYPES) are defined.
```

---

## Dependency Manifest Structure

### Top Level

```json
{
  "document_metadata": {
    "title": "ATLAS Master Documentation Dependency Manifest",
    "version": "1.0.0",
    "created": "2026-03-03",
    "total_parts": 21,
    "total_sections": 147
  },
  "concepts": { ... },
  "section_dependencies": { ... },
  "dependency_types": { ... },
  "validation_patterns": { ... }
}
```

### Concepts

Each concept specifies:
- **id**: Machine-readable identifier (e.g., `T1_5_COUNT`)
- **name**: Human-readable name
- **type**: Category (COUNT, FORMULA, TAXONOMY, SCORING_SYSTEM, etc.)
- **defined_in**: Section number where authoritative (e.g., §34)
- **canonical_value**: Current correct value
- **update_history**: List of all values this concept has had, with dates and rationale
- **used_in**: List of sections that reference this concept
- **critical**: Boolean indicating if this is essential to document integrity

**Example: T1.5 Count**

```json
{
  "id": "T1_5_COUNT",
  "name": "Number of Middle-Range Theories (T1.5 Level)",
  "type": "COUNT",
  "defined_in": "§34",
  "canonical_value": 13,
  "last_updated": "2026-02-27",
  "update_history": [
    {"value": 4, "date": "2025-08-15", "context": "Initial taxonomy"},
    {"value": 10, "date": "2025-11-20", "context": "First refinement"},
    {"value": 12, "date": "2026-01-10", "context": "Secondary refinement"},
    {"value": 13, "date": "2026-02-27", "context": "Final update"}
  ],
  "used_in": ["§35", "§40", "§54", "§78", "§100", "§115", "§142", "§147"],
  "critical": true
}
```

### Section Dependencies

Each section declares:
- **defines**: Concepts it makes authoritative
- **uses**: Concepts it references (must stay consistent with definitions)
- **extends**: Sections it builds upon
- **supersedes**: Concepts it replaces

**Example: §34 (Defines T1.5 Count)**

```json
{
  "section_number": "§34",
  "section_title": "Middle-Range Theories: The T1.5 Level",
  "status": "WRITTEN",
  "defines": ["T1_5_COUNT"],
  "uses": ["EPISTEMIC_LEVELS"],
  "extends": ["§33"]
}
```

**Example: §54 (Uses Multiple Concepts)**

```json
{
  "section_number": "§54",
  "section_title": "Domain Panels: Architecture and Exemplars",
  "status": "WRITTEN",
  "defines": ["AESHI_SCORING"],
  "uses": ["T1_5_COUNT", "WARRANT_TYPES", "CREDENCE_FORMULA_LOGODDS"],
  "critical": true
}
```

---

## Dependency Types

| Type | Meaning | Implication |
|------|---------|-------------|
| **DEFINES** | Section authoritatively introduces a concept | Only this section's value is correct; others must match |
| **USES** | Section references a concept defined elsewhere | Must stay consistent with DEFINES section |
| **EXTENDS** | Section builds on another with detail/refinement | Should be complementary and consistent |
| **SUPERSEDES** | Section replaces earlier approach | Old concept should be marked deprecated; transition explained |
| **COUNTS** | Numerical constant that must match everywhere | Special validator for numeric consistency |

---

## Maintenance Workflow

### When Adding a New Concept

1. Write the defining section in PART_*.md (e.g., §XX)
2. Add entry to `DEPENDENCY_MANIFEST.json` under `concepts`:
   ```json
   "NEW_CONCEPT": {
     "id": "NEW_CONCEPT",
     "name": "Human-readable name",
     "type": "COUNT|FORMULA|TAXONOMY|...",
     "defined_in": "§XX",
     "canonical_value": "...",
     "update_history": [{"value": "...", "date": "2026-03-03"}],
     "used_in": []
   }
   ```
3. Run validation:
   ```bash
   python scripts/validate_master_doc.py --mode=validate
   ```
4. Commit both markdown and manifest together

### When Updating an Existing Concept

1. Update the DEFINES section in PART_*.md
2. Update manifest entry:
   - Change `canonical_value`
   - Update `last_updated` date
   - Add entry to `update_history` with new value, date, and reason
   - Update `used_in` list if sections changed
3. Run validation to find affected sections:
   ```bash
   python scripts/validate_master_doc.py --mode=report
   ```
4. Manually review and update dependent sections
5. Commit with message noting affected sections:
   ```bash
   git commit -m "§34: T1.5 count 12→13; update §35, §40, §54, §78, §100, §115, §142, §147"
   ```

### When Superseding a Concept

1. Create the new section with replacement concept
2. Mark old concept as deprecated in manifest:
   ```json
   "CREDENCE_FORMULA_LEGACY": {
     "deprecated": true,
     "superseded_by": "CREDENCE_FORMULA_LOGODDS",
     "deprecation_date": "2026-02-27"
   }
   ```
3. Update DEFINES section for old concept to note supersession
4. Update dependent sections to:
   - Use new concept, OR
   - Add acknowledgment of deprecation (e.g., "deprecated" or "legacy" mention)
5. See §48 for example of how to document a transition (legacy three-factor → new log-odds formula)

---

## Integration with Workflows

### As a Pre-Commit Hook

```bash
# .git/hooks/pre-commit
#!/bin/bash
python scripts/validate_master_doc.py --mode=validate
if [ $? -ne 0 ]; then
  echo "Commit blocked: validation violations found."
  echo "Run: python scripts/validate_master_doc.py --mode=report"
  exit 1
fi
```

### As a CI/CD Pipeline Step

```yaml
# .github/workflows/validate-docs.yml
name: Validate ATLAS Docs
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: python scripts/validate_master_doc.py --mode=validate
```

### As a Reflex (Real-Time Alert)

Integrate with the ATLAS operational infrastructure to warn David when he edits a file:

```
📌 Alert: You modified PART_II_THEORETICAL.md
§34 updated: T1.5 count changed
→ This affects 8 sections: §35, §40, §54, §78, §100, §115, §142, §147
→ Run: python scripts/validate_master_doc.py --mode=report
```

---

## Validation Patterns

The manifest includes regex patterns for finding concept references in markdown files. These are used by the validator to identify inconsistencies.

**Example: T1.5 Count Pattern**

```json
"T1_5_COUNT": {
  "regex": "(?:^|\\s)(\\d+)\\s+T1\\.5\\s+theor(?:ies|y)",
  "flags": ["case_insensitive"],
  "expected_value": 13,
  "tolerance": 0
}
```

This matches:
- "13 T1.5 theories"
- "13 T1.5 theory"
- "the 13 T1.5 theories"

And flags any other number (1, 10, 12, 22, etc.) as a violation.

---

## Existing Issues Found

Running the validator on the current documentation found:

### CRITICAL
- PART_VII_T15_REDUCTIONS contains "1 T1.5 theory" (should be 13)
- PART_VII_T15_REDUCTIONS contains "22 T1.5 theories" (should be 13)

### MEDIUM
- T1_5_COUNT updated 2026-02-27; sections §35, §40, §54, §78, §100, §115, §142, §147 flagged for review
- CREDENCE_FORMULA_LOGODDS updated 2026-02-27; sections §48A, §49, §50, §51, §52, §53, §54 flagged for review

**Next step**: Run `python scripts/validate_master_doc.py --mode=suggest` to see recommended fixes.

---

## Future Extensions

### 1. Concept Genealogy
Track not just current value but lineage. Example: "T1.5 count: 4 (2025-08) → 10 (2025-11) → 12 (2026-01) → 13 (2026-02), final as of 2026-02-27"

### 2. Cross-Repo Dependencies
Track dependencies between ATLAS master doc and Article_Eater code, BN_graphical, etc.

Example: "CREDENCE_FORMULA_LOGODDS defined in ATLAS §48 is implemented in web_of_belief.py:function:compute_credence()"

### 3. Panelist Review Integration
Link decisions to expert panel sessions.

Example: "Transfer reliability values calibrated by panelists Mayo, Illari, Cartwright (2026-02-25 session)"

### 4. Version-Aware Rendering
Render master doc with version badges showing when each concept was last updated.

### 5. Automated Queries
Build interface for: "Show all sections using warrant types" or "List all superseded concepts" or "Generate consistency report for last 30 days"

---

## Questions & Support

**Q: What if a section needs to use an old (deprecated) concept?**
A: Add an explicit note acknowledging the deprecation. The validator will recognize keywords like "deprecated", "legacy", "note:", "transition", etc.

**Q: Can I add new concepts myself?**
A: Yes. Add to `DEPENDENCY_MANIFEST.json` under `concepts`, update `section_dependencies` for affected sections, and run `validate_master_doc.py --mode=validate` to check.

**Q: What if the validator is wrong about something?**
A: The regex patterns in `validation_patterns` can be refined. Edit the pattern or add context clues (e.g., change "13 T1.5 theories" → "thirteen T1.5 theories" if needed to avoid false matches).

**Q: How do I know which concept to update?**
A: Look at the violation message. It will say "Section X references concept Y which was last updated on DATE Z." Check the definition in §Z to see current value.

**Q: Should I commit the manifest file?**
A: Yes, absolutely. It's part of the documentation system. Commit it alongside changes to PART_*.md files.

---

## Technical Details

### Script Architecture

- **SmartBookValidator** class: Main validator engine
- **Violation** dataclass: Represents a single consistency issue
- **ViolationSeverity** enum: Severity levels (CRITICAL, HIGH, MEDIUM, LOW, INFO)
- **load_manifest()**: Load and parse DEPENDENCY_MANIFEST.json
- **discover_part_files()**: Find all PART_*.md files
- **validate_*()**: Individual validation check functions
- **print_violations()**: Display violations in color-coded format
- **generate_markdown_report()**: Export findings to markdown

### Performance

- Loads all 21 part files into memory: ~2–5 MB
- Regex pattern matching: ~100 ms per pattern × ~30 patterns = ~3 seconds total
- Typical run time: 3–5 seconds
- Output: Console (for validate/suggest) or markdown file (for report)

### Dependencies

- Python 3.7+
- Standard library only (json, re, sys, argparse, pathlib, dataclasses, enum, typing)
- No external dependencies

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-03 | Initial release: manifest, validator, design doc |

---

## References

- **Design Document**: SMART_BOOK_DESIGN_2026-03-03.md
- **Manifest**: master_doc_parts/DEPENDENCY_MANIFEST.json
- **Validator Script**: scripts/validate_master_doc.py
- **Example: §48 (Credence Formula Transition)**: Shows how to document a concept supersession
- **Example: §34 (T1.5 Count)**: Shows canonical source for numeric constant

---

**Last Updated**: March 3, 2026
**Status**: Operational, Ready for Integration
**Next Steps**: Integrate with pre-commit hook or CI/CD pipeline; review and fix CRITICAL violations found in current document
