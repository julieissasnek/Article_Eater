# Smart Book: A Dependency-Aware Documentation System for ATLAS

**Date**: March 3, 2026
**Version**: 1.0
**Author**: Claude Code
**Status**: Design Document

---

## Executive Summary

The ATLAS master documentation (21 parts, §1–§147+) contains intricate cross-cutting concepts that appear in multiple sections: the T1.5 count (inconsistently stated as 4, 10, 12, or 13 across sections), the credence formula (legacy three-factor vs. current four-factor log-odds projection), warrant types and transfer reliabilities, AESHI scoring, Q-norms, epistemic levels, and architectural decisions. When one section changes—for example, updating the T1.5 count from 12 to 13—earlier sections that reference that count become stale and potentially misleading.

The **Smart Book** system is a machine-readable dependency manifest coupled with validation tooling that:

1. **Encodes structural dependencies** between sections (which section *defines* a concept and which sections *use* it)
2. **Tracks changes across the document** by flagging when dependent sections may need updates
3. **Prevents consistency violations** (e.g., one section claiming "13 T1.5 theories" while another claims "12")
4. **Maintains authoritative lineage** (which section is the canonical source for each concept)
5. **Preserves history** (previous values are recorded, not deleted, so the evolution of the document is visible)

This design document explains the precedents for this approach, the implementation architecture, and the maintenance protocols required to keep the manifest current as the ATLAS document evolves.

---

## Motivation: Why Dependency Tracking Matters

### The Problem

The ATLAS master doc is not a linear sequence of independent sections. It is a tightly woven argument where foundational concepts (e.g., warrant types, credence formulas) are defined early and then used, extended, and sometimes revisited in later sections. When a foundational concept changes, dependent sections become stale.

**Real example**: The T1.5 count inconsistency. Across the document, the number of T1.5 theories is stated as:
- §34 (and references): "13 T1.5 theories"
- Some sections: "12 T1.5 theories"
- Other sections: "10 T1.5 theories"
- Quarantine materials: "4 T1.5 theories"

This arose because:
1. The T1.5 taxonomy was refined over time, and the count changed from 4 → 10 → 12 → 13
2. Different parts of the document were written at different times
3. When the count was updated to 13, not all references were updated
4. There was no systematic way to find all places that needed updating

**Result**: A reader consulting §34 learns "13 theories," but consulting another section gets a different count, creating confusion and eroding credibility.

### The Vision

The Smart Book system makes dependencies explicit and checkable. Instead of a static text document, the master doc becomes a *knowledge graph* where:

- Each section declares the concepts it **defines** (makes authoritative)
- Each section declares the concepts it **uses** (and must stay consistent with the definition)
- A validator checks for inconsistencies on every change
- When a writer updates a section, the system alerts them: "You changed the T1.5 count to 14. This affects 8 other sections: §35, §40, §54, §78, §100, §115, §142, §147."

This is epistemic responsibility: the document is not authoritative unless it is *consistent*. The Smart Book makes consistency enforceable.

---

## Precedents and Related Systems

### 1. Literate Programming (Knuth, 1984)

Donald Knuth's literate programming paradigm (implemented in WEB, CWEB, Noweb) entangles code and documentation such that they cannot drift apart. A single source file is woven into both executable code and human-readable documentation. Changes to one automatically propagate to the other.

**Relevance**: The Smart Book applies this idea to documentation itself. Instead of a monolithic text file, the document is a collection of interdependent pieces that can be checked for consistency.

### 2. Sphinx Cross-References (Python Documentation)

The Sphinx documentation generator (used by Python, Django, NumPy, and hundreds of projects) maintains a cross-reference database (`objects.inv`) that tracks all definitions, references, and links across a multi-part documentation suite. When a function is renamed, Sphinx can detect broken cross-references.

**Relevance**: Sphinx is reference-based (links to definitions), while the Smart Book is concept-based (tracks which sections define and use concepts). But the core idea is the same: a machine-readable graph of dependencies.

### 3. Jupyter Book Structured Metadata

Jupyter Book (a system for publishing Jupyter notebooks as books) includes metadata fields for each chapter/section: title, numbering, internal references. Extensions like `jupyter-book-plugins` allow declaring dependencies between chapters and enforcing version compatibility.

**Relevance**: The Smart Book uses a similar metadata approach (DEPENDENCY_MANIFEST.json) but extends it to track semantic dependencies (definitions, uses, supersessions, counts).

### 4. Knowledge Graph Documentation (Semantic MediaWiki, DBpedia)

Semantic MediaWiki and knowledge graph systems like DBpedia represent documentation content as triples (subject–predicate–object). For example:

```
("T1.5 count", hasValue, 13)
("Credence formula", definedIn, "§48")
("AESHI", usedIn, ["§54", "§78", "§100"])
```

This makes it possible to query dependencies: "Show me all sections that reference the credence formula," or "List all concepts whose definition has changed in the last 30 days."

**Relevance**: The Smart Book uses a similar triple-like structure but encoded in JSON for simplicity and integration with Python tooling.

### 5. Configuration Management and Infrastructure-as-Code (Terraform, Ansible)

Modern infrastructure tools (Terraform, Ansible) track dependencies between resources explicitly. When you declare that resource A depends on resource B, the tool ensures B is created/updated before A, and when B changes, it can warn you that A might be affected.

**Relevance**: The validation script borrows this pattern: declaring dependencies upfront and using them to identify impact zones.

---

## System Architecture

### Components

#### 1. DEPENDENCY_MANIFEST.json

A machine-readable JSON file at `/docs/master_doc_parts/DEPENDENCY_MANIFEST.json` that encodes:

```json
{
  "document_metadata": {
    "title": "ATLAS Master Documentation",
    "version": "1.0",
    "last_updated": "2026-03-03",
    "total_sections": 147,
    "total_parts": 21
  },
  "concepts": {
    "T1_5_COUNT": {
      "name": "Number of Middle-Range Theories (T1.5 Level)",
      "canonical_value": 13,
      "type": "COUNT",
      "defined_in": "§34",
      "last_updated": "2026-02-27",
      "update_history": [
        {"value": 4, "date": "2025-08-15", "context": "Initial taxonomy"},
        {"value": 10, "date": "2025-11-20", "context": "First refinement"},
        {"value": 12, "date": "2026-01-10", "context": "Secondary refinement"},
        {"value": 13, "date": "2026-02-27", "context": "Final taxonomy update"}
      ],
      "used_in": ["§35", "§40", "§54", "§78", "§100", "§115", "§142", "§147"]
    },
    "CREDENCE_FORMULA_LOGODDS": {
      "name": "Four-Factor Log-Odds Projection Calculus",
      "type": "FORMULA",
      "defined_in": "§48",
      "components": ["transfer_reliability_d", "warrant_strength_ω", "population_transfer_δ", "lab_probability_p_lab"],
      "last_updated": "2026-02-27",
      "update_history": [
        {"formula": "three_factor_legacy", "date": "2025-06-01", "deprecated": true},
        {"formula": "four_factor_logodds", "date": "2026-02-27", "current": true}
      ],
      "used_in": ["§48A", "§49", "§50", "§51", "§52", "§53"],
      "notes": "Supersedes legacy three-factor formula; see §48 for migration notes"
    },
    "WARRANT_TYPES": {
      "name": "Seven Warrant Types with Transfer Reliabilities",
      "type": "TAXONOMY",
      "defined_in": "§48.1",
      "count": 7,
      "values": [
        {"type": "CONSTITUTIVE", "transfer_reliability": 0.95},
        {"type": "MECHANISM", "transfer_reliability": 0.80},
        {"type": "EMPIRICAL_ASSOCIATION", "transfer_reliability": 0.80},
        {"type": "FUNCTIONAL", "transfer_reliability": 0.65},
        {"type": "CAPACITY", "transfer_reliability": 0.55},
        {"type": "ANALOGICAL", "transfer_reliability": 0.40},
        {"type": "THEORY_DERIVED", "transfer_reliability": 0.25}
      ],
      "last_updated": "2026-02-27",
      "used_in": ["§48A", "§49", "§60", "§70", "§78"],
      "notes": "Transfer reliabilities are fixed by ATLAS design; not empirically measured"
    },
    "AESHI_SCORING": {
      "name": "AESHI Multi-Dimensional Scoring System",
      "type": "SCORING_SYSTEM",
      "defined_in": "§54",
      "dimensions": ["A", "E", "S", "H", "I"],
      "last_updated": "2026-02-15",
      "used_in": ["§55", "§78", "§100", "§115"]
    },
    "Q_NORMS": {
      "name": "Q-Norms (Quality-of-Evidence Standards)",
      "type": "STANDARD",
      "defined_in": "§60",
      "count": 7,
      "last_updated": "2026-02-20",
      "used_in": ["§61", "§62", "§70", "§78"]
    },
    "EPISTEMIC_LEVELS": {
      "name": "Four-Level Epistemic Hierarchy",
      "type": "HIERARCHY",
      "defined_in": "§33",
      "levels": ["T0", "T1", "T1.5", "T2"],
      "last_updated": "2026-01-15",
      "used_in": ["§34", "§35", "§40", "§54", "§100"]
    }
  },
  "section_dependencies": {
    "§34": {
      "section_title": "Middle-Range Theories: The T1.5 Level",
      "part": "PART_II_THEORETICAL",
      "status": "WRITTEN",
      "defines": ["T1_5_COUNT", "EPISTEMIC_LEVELS"],
      "uses": ["EPISTEMIC_LEVELS"],
      "extends": ["§33"],
      "notes": "Canonical source for T1.5 count; any updates here must be propagated to all dependent sections"
    },
    "§48": {
      "section_title": "The Projection Calculus: Log-Odds Formulation",
      "part": "PART_IV_CREDENCE",
      "status": "WRITTEN",
      "defines": ["CREDENCE_FORMULA_LOGODDS", "WARRANT_TYPES"],
      "uses": ["EPISTEMIC_LEVELS", "WARRANT_STRENGTH"],
      "supersedes": ["CREDENCE_FORMULA_LEGACY"],
      "notes": "Canonical source for credence formula; see migration notes in §48 for legacy three-factor handling"
    },
    "§54": {
      "section_title": "Domain Panels: Architecture and Exemplars",
      "part": "PART_VI_DOMAIN_PANELS",
      "status": "WRITTEN",
      "defines": ["AESHI_SCORING"],
      "uses": ["T1_5_COUNT", "WARRANT_TYPES", "CREDENCE_FORMULA_LOGODDS"],
      "notes": "Critical junction: uses multiple foundational concepts from earlier sections"
    },
    "§60": {
      "section_title": "[Expert Panel Section]",
      "part": "PART_VI_DOMAIN_PANELS",
      "status": "WRITTEN",
      "defines": ["Q_NORMS"],
      "uses": ["WARRANT_TYPES", "AESHI_SCORING"],
      "notes": "Calibration source for Q-norms based on warrant types"
    }
  },
  "dependency_types": {
    "DEFINES": "This section introduces or makes authoritative the concept",
    "USES": "This section references or applies the concept",
    "EXTENDS": "This section builds upon another by adding detail or refinement",
    "SUPERSEDES": "This section replaces an earlier approach with a new one",
    "COUNTS": "This section states a numerical count that must remain consistent"
  }
}
```

#### 2. Validation Script: scripts/validate_master_doc.py

A Python script that:

1. **Reads DEPENDENCY_MANIFEST.json** and loads the dependency graph
2. **Scans PART_*.md files** and extracts concept references using regex patterns
3. **Checks for consistency violations**:
   - Count mismatches (e.g., "13 T1.5 theories" vs. "12 T1.5 theories")
   - Stale references (section refers to a concept that's been superseded without acknowledgment)
   - Undefined concepts (a section uses a concept that's not defined anywhere)
   - Missing updates (a DEFINES section changed but USES sections were not updated)
4. **Outputs a detailed report** with violations, suggested updates, and risk assessments
5. **Supports multiple modes**:
   - `--mode=validate` (check-only, no changes)
   - `--mode=report` (generate HTML/Markdown report for manual review)
   - `--mode=suggest` (suggest fixes, to be approved by user)

#### 3. Integration Points

**Pre-commit hook**: Automatically run validation when PART_*.md files change. Prevent commits with consistency violations.

**CI/CD pipeline**: Nightly validation run; generate report and email to David if violations found.

**Interactive alerts**: When David modifies a file, the system warns: "You updated T1.5 count to 14. This affects 8 sections. Please review and update the following sections: ..."

---

## Dependency Types Explained

### DEFINES
Section that introduces a concept authoritatively. It is the canonical source. Only this section's value/definition is considered correct.

**Example**: §34 *defines* "T1.5 count = 13"

### USES
Section that references the concept. It must remain consistent with the DEFINES section.

**Example**: §35, §40, §54, §78 all *use* the T1.5 count and must state it as 13.

### EXTENDS
Section that builds on another section by adding detail, nuance, or refinement without replacing it.

**Example**: §35 *extends* §34 by providing detailed walkthroughs of T1.5 theories.

### SUPERSEDES
Section that replaces an earlier approach with a new one. Used when a fundamental concept is revised (e.g., legacy credence formula → new log-odds formula).

**Example**: §48 *supersedes* the legacy three-factor credence formula. Earlier sections using the legacy formula should reference this decision.

### COUNTS
A special case of DEFINES: a numerical value that must remain consistent across the document. The validator pays special attention to these.

**Example**: T1.5 count, number of warrant types (7), number of Q-norms (7), number of epistemic levels (4).

---

## Maintenance Protocol

### When Adding a New Concept

1. **Write the defining section** as usual in the PART_*.md file
2. **Add an entry to DEPENDENCY_MANIFEST.json** under `concepts`:
   ```json
   "NEW_CONCEPT": {
     "name": "...",
     "type": "...",
     "defined_in": "§XX",
     "last_updated": "YYYY-MM-DD",
     "used_in": [],
     "update_history": [{"value": "...", "date": "YYYY-MM-DD"}]
   }
   ```
3. **Run validation**: `python scripts/validate_master_doc.py --mode=validate`
4. **Commit both the markdown and the manifest** in a single commit

### When Updating an Existing Concept

1. **Update the defining section** in the PART_*.md file
2. **Update the manifest entry**:
   - Increment `last_updated`
   - Add new entry to `update_history`
   - Update `used_in` list if affected sections changed
3. **Run validation**: `python scripts/validate_master_doc.py --mode=report` to identify all affected sections
4. **Review affected sections manually** (the validator cannot fix them automatically; human judgment is required)
5. **Update dependent sections** if needed
6. **Commit**: Include in commit message which sections were affected, e.g., "§34: T1.5 count updated to 14; affected §35, §40, §54"

### When Superseding a Concept

1. **Create the new section** with the replacement concept
2. **Mark the old concept as superseded** in the manifest:
   ```json
   "CREDENCE_FORMULA_LEGACY": {
     "name": "...",
     "deprecated": true,
     "superseded_by": "CREDENCE_FORMULA_LOGODDS",
     "deprecation_date": "2026-02-27"
   }
   ```
3. **Update the DEFINES section** for the old concept to note the supersession
4. **Update dependent sections** to reference the new concept or add a note acknowledging the transition
5. **Preserve the old concept in the manifest** (do not delete)

---

## Machine-Readable Validation: The Validator Script

The validation script uses a combination of:

1. **Exact match checking** for counts:
   ```python
   if "13 T1.5 theories" in text and manifest["concepts"]["T1_5_COUNT"]["canonical_value"] == 12:
       raise ConsistencyViolation(f"Section {section} claims 13 T1.5 theories but manifest says 12")
   ```

2. **Regex pattern matching** for concept mentions:
   ```python
   patterns = {
       "T1_5_COUNT": r"(\d+)\s+T1\.5\s+theor(?:ies|y)",
       "WARRANT_TYPES": r"(?:seven|7)\s+warrant\s+types",
       "Q_NORMS": r"(?:seven|7)\s+Q-norms"
   }
   ```

3. **Dependency graph traversal** to compute impact:
   ```python
   def find_affected_sections(concept_name):
       return manifest["concepts"][concept_name]["used_in"]
   ```

4. **Heuristic assessment** of whether a section acknowledges a supersession:
   ```python
   if "CREDENCE_FORMULA_LEGACY" in text and "deprecated" in text:
       # Section acknowledges the transition; mark as OK
   else:
       # Section may be using outdated formula; flag for review
   ```

---

## Integration with Existing Infrastructure

### As a Reflex (Per David's Notes)

The Smart Book could integrate with the ATLAS operational infrastructure as a reflex (automated action):

1. **File watcher reflex**: Monitor PART_*.md files for changes
2. **On each change**: Run validation and generate a brief alert report
3. **Alert message**: "§34 updated: T1.5 count → 14. Sections §35, §40, §54, §78, §100, §115, §142, §147 may need updates."
4. **User action**: Writer reviews the alert, manually updates dependent sections, commits

This turns consistency-checking from a post-hoc process (fixing inconsistencies after the fact) into a real-time process (being warned *when* you make changes that create inconsistencies).

### As a Pre-Commit Hook

```bash
# .git/hooks/pre-commit
python scripts/validate_master_doc.py --mode=validate || exit 1
```

Prevents commits with consistency violations.

### As Part of the CI/CD Pipeline

Run nightly: generate a report of all dependencies and consistency status. Email to David weekly with a summary of any violations found.

---

## Why This Matters: Epistemically Responsible Documentation

The ATLAS system makes epistemic claims about how concepts relate to each other. The documentation is the artifact that captures those claims. If the documentation is internally inconsistent—one section says "13 T1.5 theories" and another says "12"—then the claims are undermined.

The Smart Book makes consistency a *structural requirement*, not a manual discipline. It shifts the burden from David (who has to manually remember to update every reference) to the system (which automatically tracks dependencies and warns when they might be violated).

This reflects a deeper principle: **knowledge systems are only authoritative if they are consistent**. The Smart Book is infrastructure for consistency.

---

## Future Extensions

### 1. Concept Genealogy
Track not just the current value but the *conceptual lineage* of each concept. For example, "T1.5 count evolved from 4 → 10 → 12 → 13 across the 2025–2026 development cycle." This makes the document's evolution visible and accountable.

### 2. Cross-Repo Dependencies
Extend the manifest to track dependencies between the ATLAS master doc and the Article_Eater code, or between ATLAS and BN_graphical. Example: "The credence formula defined in ATLAS §48 is implemented in web_of_belief.py:function:compute_credence()"

### 3. Panelist Review Integration
Link decisions in the manifest to expert panel reviews. Example: "Transfer reliability values were calibrated by panelists Mayo, Illari, and Cartwright. See expert_panel_session_2026-02-25.md."

### 4. Version-Aware Rendering
Build a tool that renders the master doc with version badges: "This section uses the log-odds credence formula (current as of 2026-02-27)." Readers can see at a glance which version of each concept they're reading.

### 5. Automated Documentation Queries
Implement a query interface: "Show me all sections that use warrant types." "List all superseded concepts." "Generate a consistency report for the past 30 days."

---

## Conclusion

The Smart Book system transforms the ATLAS master documentation from a static text artifact into a *living knowledge structure*. By making dependencies explicit and checkable, it:

- Prevents consistency violations from being missed
- Alerts writers when their changes affect other sections
- Preserves the history of conceptual changes
- Supports rapid iteration and refinement
- Maintains epistemic integrity

This is infrastructure for the kind of rigorous, accountable documentation that David's vision for ATLAS requires.

---

## References

Knuth, D. E. (1984). "Literate Programming." *The Computer Journal*, 27(2), 97–111.

Brandl, G. et al. (2007–2026). Sphinx Documentation Generator. https://www.sphinx-doc.org

Jupyter Development Team. (2020–2026). Jupyter Book. https://jupyterbook.org

Oren, D., & Brik, Y. (2015). "Knowledge Graphs in Web Search." *IEEE Internet Computing*, 19(3), 32–40.
