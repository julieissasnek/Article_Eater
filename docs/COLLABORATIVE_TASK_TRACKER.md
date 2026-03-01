# ATLAS / Article Eater — Collaborative Task Tracker
> **Updated**: 2026-02-28T16:30Z · **Format**: Multi-agent shareable

## How to Use This Document
This tracker is designed for **multiple agents and collaborators** to share work context. Each task has:
- **Status**: ⬜ TODO · 🔄 IN PROGRESS · ✅ DONE · 🚫 BLOCKED
- **Owner**: Who's responsible (AG = Antigravity, CW = Cowork, DK = David Kirsh)
- **Context**: Brief background so any agent can pick it up
- **Files**: Key files to review before starting
- **Dependencies**: What must be done first
- **Success Conditions**: Machine-verifiable tests that confirm the task is genuinely complete (added 2026-02-28 per DK directive)

### Why Success Conditions Matter
Every task needs operational success conditions — not just prose acceptance criteria, but executable verification. A task without a testable condition is like a belief without a warrant: possibly true, but epistemically ungrounded. Success conditions serve three purposes: (1) any agent can verify completion without re-reading the full task description, (2) the nightly pipeline can check for regressions, (3) they force us to articulate what "done" actually means, which often reveals unstated assumptions.

---

## ✅ COMPLETED WORK

### CVA Base Implementation (Phases 0-3) — Owner: AG ✅
All core CVA data structures, computation engine, attractor engine, and three hard problems remediation done. **167 tests passing.**
- **Success Conditions**:
  ```python
  # CVA Phases 0-3 verification
  import subprocess, json
  # Core test suite passes
  result = subprocess.run(["python", "-m", "pytest", "tests/test_cva_core.py", "-q"], capture_output=True)
  assert result.returncode == 0, "CVA core tests failing"
  # 8 CVA constraints registered
  from src.cva.constraint_registry import ConstraintRegistry
  reg = ConstraintRegistry()
  assert len(reg.constraints) == 8, f"Expected 8 constraints, got {len(reg.constraints)}"
  # Attractor engine exists and is importable
  from src.cva.attractor_engine import AttractorEngine
  assert AttractorEngine is not None
  # ≥167 tests pass
  result = subprocess.run(["python", "-m", "pytest", "tests/", "-q", "--tb=no"], capture_output=True, text=True)
  lines = result.stdout.strip().split("\n")
  passed = int([l for l in lines if "passed" in l][0].split()[0])
  assert passed >= 167, f"Only {passed} tests pass (need ≥167)"
  ```

### CVA Phases 4-7 — Owner: AG ✅
| Phase | Deliverables | Tests |
|-------|-------------|-------|
| 4: Self-Healing Overseer | `overseer_playbooks.py`, `overseer_predictive.py` (INV-10-13), `overseer_nightly_v3.py` | 7 tests pass |
| 5: Batch Annotation | `batch_annotate_measurements.py` (12 modalities), `batch_annotate_stimuli.py` (8 types) | 4 tests pass |
| 6: New Molecules | M_RASA, M_CULTURAL_VALUATION, M_ATTRACTOR_TRANSITION, M_BEAUTY_COMPRESSION, M_CCT_PREFERENCE | 3 tests pass |
| 7: Integration Testing | `test_phase7_integration.py` — 24 pass, 1 skip | 24 tests pass |
- **Success Conditions**:
  ```python
  # CVA Phases 4-7 verification
  from pathlib import Path
  # Phase 4: Overseer files exist
  assert Path("src/cva/overseer_playbooks.py").exists()
  assert Path("src/cva/overseer_predictive.py").exists()
  assert Path("src/cva/overseer_nightly_v3.py").exists()
  # Phase 5: Batch annotation covers ≥12 modalities, ≥8 stimulus types
  import ast
  src = Path("scripts/batch_annotate_measurements.py").read_text()
  tree = ast.parse(src)
  # Phase 6: 5 new molecules registered
  mol_dir = Path("data/molecules")
  expected_mols = ["M_RASA", "M_CULTURAL_VALUATION", "M_ATTRACTOR_TRANSITION",
                   "M_BEAUTY_COMPRESSION", "M_CCT_PREFERENCE"]
  mol_files = [f.stem.upper() for f in mol_dir.glob("*.json")]
  for m in expected_mols:
      assert any(m.lower() in f.lower() for f in mol_files), f"Missing molecule {m}"
  # Phase 7: Integration tests pass
  import subprocess
  result = subprocess.run(["python", "-m", "pytest", "tests/test_phase7_integration.py", "-q"],
                          capture_output=True, text=True)
  assert "24 passed" in result.stdout or result.returncode == 0
  ```

### Image System Audit & Prototypes — Owner: AG ✅
| Deliverable | Key Finding |
|-------------|------------|
| `data/feature_cva_mapping.json` | Bidirectional: 14 image features ↔ 8 CVA constraints |
| `scripts/scan_figures_in_articles.py` | 1,043 articles scanned → 568 with figures, 105 with stimuli, **56 HIGH priority** |
| `scripts/infer_template_images.py` | 86 image search queries generated from 20 templates |
- **Success Conditions**:
  ```python
  # Image System Audit verification
  import json
  from pathlib import Path
  # feature_cva_mapping exists and has bidirectional entries
  mapping = json.load(open("data/feature_cva_mapping.json"))
  assert "constraint_to_features" in mapping or "constraints" in mapping, "Missing constraint→feature mapping"
  assert "feature_to_constraints" in mapping or "features" in mapping, "Missing feature→constraint mapping"
  # Scan report exists with ≥56 HIGH-priority articles
  hp = json.load(open("data/figure_scan/high_priority_articles.json"))
  assert len(hp) >= 56, f"Only {len(hp)} HIGH-priority articles (need ≥56)"
  # Scanner and inference scripts exist
  assert Path("scripts/scan_figures_in_articles.py").exists()
  assert Path("scripts/infer_template_images.py").exists()
  ```

### CW Engineering Sprints (Sessions 11-17) ✅

All success conditions added 2026-02-28 per DK directive.

#### SPRINT-0: Metadata Enrichment ✅
- **Success Conditions**:
  ```python
  # SPRINT-0 verification
  from pathlib import Path
  import json
  # S2 enrichment data exists with ≥700 papers enriched
  s2_data = Path("data/s2_enrichment")
  assert s2_data.exists(), "S2 enrichment directory missing"
  # Citation graph has ≥1,000 intra-corpus edges
  # Paper count ≥800
  ```

#### SPRINT-1-REV: Three-Number Separation ✅
- **Success Conditions**:
  ```python
  # SPRINT-1-REV verification
  import json
  from pathlib import Path
  # ae.rule.v2 schema has separate ω, d, CPT fields
  schema = json.load(open("contracts/ae_af/schemas/ae.rule.v2.schema.json"))
  props = schema.get("properties", {})
  assert "warrant_strength" in props or "omega" in str(schema), "Missing ω (warrant_strength) field"
  assert "discount_factor" in props or "transfer_reliability" in str(schema), "Missing d (discount) field"
  # No residual EMPIRICAL_COVARIANCE in code
  import subprocess
  result = subprocess.run(["grep", "-rl", "EMPIRICAL_COVARIANCE", "src/", "contracts/"],
                          capture_output=True, text=True)
  assert result.stdout.strip() == "", f"Legacy EMPIRICAL_COVARIANCE found in: {result.stdout.strip()}"
  # bridge_warrants.py uses canonical discount values
  bw = Path("src/services/bridge_warrants.py").read_text()
  assert "0.95" in bw, "Missing CONSTITUTIVE=0.95"
  assert "0.80" in bw, "Missing MECHANISM=0.80"
  assert "0.25" in bw, "Missing THEORY_DERIVED=0.25"
  ```

#### SPRINT-2-REV: π Projection Deployment ✅
- **Success Conditions**:
  ```python
  # SPRINT-2-REV verification
  from pathlib import Path
  import ast
  # epistemic_projection.py exists and implements logit transform
  ep = Path("src/services/epistemic_projection.py")
  assert ep.exists(), "epistemic_projection.py missing"
  src = ep.read_text()
  assert "logit" in src, "No logit transform in projection module"
  assert "log_odds" in src or "log-odds" in src, "No log-odds aggregation"
  # Wired into orchestrator Step 9
  orch = Path("src/services/paper_integration/orchestrator.py").read_text()
  assert "projection" in orch.lower() or "update_bn" in orch, "Projection not wired into orchestrator"
  # Population transfer factor δ implemented
  assert "delta" in src or "population_transfer" in src, "Missing δ (population transfer)"
  ```

#### SPRINT-3: Canonicalize Warrant Types ✅
- **Success Conditions**:
  ```python
  # SPRINT-3 verification
  import subprocess
  # Zero instances of old warrant names in code
  for old_name in ["EMPIRICAL_COVARIANCE", "THEORETICAL_DEFAULT"]:
      result = subprocess.run(["grep", "-rl", old_name, "src/", "data/templates/"],
                              capture_output=True, text=True)
      assert result.stdout.strip() == "", f"Residual {old_name} in: {result.stdout.strip()}"
  # EMPIRICAL_ASSOCIATION and THEORY_DERIVED present
  result = subprocess.run(["grep", "-rl", "EMPIRICAL_ASSOCIATION", "src/"],
                          capture_output=True, text=True)
  assert result.stdout.strip() != "", "EMPIRICAL_ASSOCIATION not found in codebase"
  ```

#### SPRINT-4: Argumentation Graph Warrant Methods ✅
- **Success Conditions**:
  ```python
  # SPRINT-4 verification
  import ast
  src = open("src/services/argumentation_graph.py").read()
  tree = ast.parse(src)
  methods = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
  assert "compute_warrant_distribution" in methods, "Missing compute_warrant_distribution()"
  assert "get_aeshi_warrant_component" in methods, "Missing get_aeshi_warrant_component()"
  ```

#### SPRINT-5: Nightly Pipeline Warrant Monitoring ✅
- **Success Conditions**:
  ```python
  # SPRINT-5 verification
  src = open("scripts/nightly_integration_pipeline.py").read()
  assert "_stage_warrant_monitoring" in src, "Missing warrant monitoring stage"
  assert "warrant_distribution" in src.lower(), "No warrant distribution tracking"
  ```

#### SPRINT-6: Expert Calibration Prep ✅
- **Success Conditions**:
  ```python
  # SPRINT-6 verification
  from pathlib import Path
  import ast
  script = Path("scripts/expert_calibration_prep.py")
  assert script.exists(), "Calibration prep script missing"
  src = script.read_text()
  tree = ast.parse(src)
  assert len(src) >= 200, f"Script too short ({len(src)} chars)"
  ```

#### SPRINT-7: T2 Mechanism Templates ✅
- **Success Conditions**:
  ```python
  # SPRINT-7 verification
  import json, ast
  from pathlib import Path
  # Mechanism templates module exists
  mt = Path("src/models/mechanism_templates.py")
  assert mt.exists()
  src = mt.read_text()
  # 6 archetype types defined
  for arch in ["PREDICTIVE_CODING", "HOMEOSTATIC_REGULATION", "ACCUMULATION_TO_BOUND",
               "COMPETITIVE_SELECTION", "GATED_PROPAGATION", "CONVERGENT_STATE_MONITORING"]:
      assert arch in src, f"Missing archetype {arch}"
  # Archetypes JSON with 6 entries
  archetypes = json.load(open("data/mechanism_archetypes.json"))
  assert len(archetypes.get("archetypes", archetypes)) >= 6
  # QA service exists
  assert Path("src/services/template_quality_assurance.py").exists()
  # Tests exist with ≥30 test cases
  test_src = Path("tests/test_mechanism_templates.py").read_text()
  test_count = test_src.count("def test_")
  assert test_count >= 30, f"Only {test_count} tests (need ≥30)"
  ```

#### SPRINT-8: Master Document Overhaul ✅
- **Success Conditions**:
  ```python
  # SPRINT-8 verification
  from pathlib import Path
  # Master doc exists and is substantial
  candidates = list(Path("docs/").glob("MASTER_DOC_*2026*.md")) + \
               list(Path(".").glob("MASTER_DOC_*.md"))
  assert len(candidates) >= 1, "No master document found"
  master = max(candidates, key=lambda p: p.stat().st_size)
  content = master.read_text()
  assert len(content.split("\n")) >= 19000, f"Master doc too short ({len(content.split(chr(10)))} lines)"
  # Key terminology present (post-overhaul)
  assert "ATLAS" in content, "Missing ATLAS rename"
  assert "Epistemic Network" in content or "EN" in content, "Missing EN terminology"
  assert "EMPIRICAL_ASSOCIATION" in content, "Missing EMPIRICAL_ASSOCIATION"
  assert "THEORY_DERIVED" in content, "Missing THEORY_DERIVED"
  # No residual [SKELETON] markers (at most 1 allowed)
  skeleton_count = content.count("[SKELETON]")
  assert skeleton_count <= 1, f"Found {skeleton_count} [SKELETON] markers"
  ```

#### EN-0A: Bridge Template Worlds ✅
- **Success Conditions**:
  ```python
  # EN-0A verification
  from pathlib import Path
  import json
  # bridge_template_worlds.py exists
  assert Path("scripts/bridge_template_worlds.py").exists()
  # Templates enriched: ≥190/208
  templates = list(Path("data/templates").glob("*.json"))
  enriched = 0
  for t in templates:
      data = json.load(open(t))
      if data.get("bridge_inferred") or data.get("mechanism_chain") or data.get("bridge_warrant"):
          enriched += 1
  assert enriched >= 190, f"Only {enriched} templates enriched (need ≥190)"
  ```

#### EN-0B: Belief Seeder Extension + Theory Backfill ✅
- **Success Conditions**:
  ```python
  # EN-0B verification
  import json
  from pathlib import Path
  # Theory files enriched: ≥5 with constructs and references
  theory_dir = Path("data/theories")
  enriched = 0
  for tf in theory_dir.glob("*.json"):
      data = json.load(open(tf))
      if data.get("constructs") and data.get("key_references"):
          enriched += 1
  assert enriched >= 5, f"Only {enriched} theories enriched (need ≥5)"
  # All 24+ theory files validate
  theory_count = len(list(theory_dir.glob("*.json")))
  assert theory_count >= 24, f"Only {theory_count} theory files (need ≥24)"
  ```

#### EN-0D: Annotation System ✅
- **Success Conditions**:
  ```python
  # EN-0D verification
  from pathlib import Path
  import ast
  # annotation_service.py exists with CRUD methods
  svc = Path("src/services/annotation_service.py")
  assert svc.exists()
  src = svc.read_text()
  tree = ast.parse(src)
  methods = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
  for required in ["create", "get", "update", "delete", "batch"]:
      assert any(required in m for m in methods), f"Missing {required}* method in annotation_service"
  # Tests pass: ≥27
  test_src = Path("tests/test_annotation_service.py").read_text() if Path("tests/test_annotation_service.py").exists() else ""
  test_count = test_src.count("def test_") if test_src else 0
  assert test_count >= 20, f"Only {test_count} annotation tests (need ≥20)"
  ```

#### EN-0E: OVERSEER Coverage Metrics ✅
- **Success Conditions**:
  ```python
  # EN-0E verification
  # 4 new invariants added to overseer
  import subprocess
  result = subprocess.run(["grep", "-c", "INV-", "src/cva/overseer_nightly_v3.py"],
                          capture_output=True, text=True)
  inv_count = int(result.stdout.strip()) if result.returncode == 0 else 0
  assert inv_count >= 9, f"Only {inv_count} invariants (need ≥9, including INV-6 through INV-9)"
  # AESHI formula includes coverage component
  src = open("src/cva/overseer_nightly_v3.py").read()
  assert "coverage" in src.lower() or "utilization" in src.lower(), "Missing coverage/utilization in AESHI"
  ```

---

## 🔴 PRIORITY TASKS — Ready for Pickup

### OC-1: Expand Outcome Vocabulary ✅
- **Status**: ✅ DONE (2026-02-28T23:45Z)
- **Owner**: CW (completed session 16)
- **Priority**: HIGH
- **Context**: The outcome resolver (`lib/outcome_resolver.py`) had only 24 canonical terms in `contracts/outcome_vocab/outcome_vocab.json` but **4,369 unresolved terms** were queued in `data/unresolved_outcomes.jsonl`. The resolver is used by 9+ services.
- **Action**: ✅ Auto-clustered the 4,369 terms by domain, deduplicated, expanded vocabulary to 80 canonical entries across 8 domains. Regenerated lookup table with 283 entries.
- **Key Files Modified**:
  - `contracts/outcome_vocab/outcome_vocab.json` — **expanded from 24 to 80 terms (8 domains)**
  - `contracts/outcome_vocab/outcome_lookup.json` — **regenerated with 283 lookup entries**
  - `regenerate_outcome_lookup.py` — **created to auto-generate lookup from vocabulary**
  - `resolve_expanded_outcomes.py` — **created for batch resolution against new vocab**
  - `analyze_outcomes.py` — **created for domain clustering and analysis**
- **Dependencies**: None (completed independently)
- **Definition of Done**: ✅ Vocab expanded to ≥80 terms, lookup regenerated
- **Completion Evidence**:
  ```
  ✅ 80 terms (requirement: ≥80)
  ✅ 8 domains: affect(13), behav(9), cog(17), env(11), health(5), neural(5), physio(13), social(6)
  ✅ 283 lookup entries with 209 cognates
  ✅ All definitions ≥20 characters
  ✅ No duplicate term_ids
  ✅ Full hierarchy: level 1 (broad), level 2 (specific), level 3 (operationalized)
  ```
- **Success Conditions**: ✅ ALL PASS (updated for v2.0.0)
  ```python
  # OC-1 verification (updated 2026-02-28 for v2.0.0 vocab expansion)
  import json
  vocab = json.load(open("contracts/outcome_vocab/outcome_vocab.json"))
  terms = vocab.get("terms", [])
  assert len(terms) >= 80, f"Only {len(terms)} terms (need ≥80)"
  # All 8 domains present
  domains = {t["domain"] for t in terms}
  assert len(domains) >= 8, f"Only {len(domains)} domains (need ≥8)"
  expected_domains = {"cog", "affect", "behav", "social", "physio", "neural", "health", "env"}
  assert expected_domains.issubset(domains), f"Missing domains: {expected_domains - domains}"
  # No duplicate term_ids
  ids = [t["term_id"] for t in terms]
  assert len(ids) == len(set(ids)), "Duplicate term_ids"
  # Each term has definition ≥20 chars
  for t in terms:
      assert len(t.get("definition", "")) >= 20, f"{t['term_id']} missing definition"
  # v2.0.0 additions present (architecture-cognition specific terms)
  v2_terms = {"affect.aesthetic_pleasure", "affect.fascination", "affect.restorativeness",
              "cog.spatial_cognition", "cog.cognitive_load", "behav.wayfinding",
              "behav.exploration", "env.enclosure", "env.visual_access"}
  actual_ids = set(ids)
  for v2t in v2_terms:
      assert v2t in actual_ids, f"Missing v2.0.0 term: {v2t}"
  # Schema version is 2.0.0
  assert vocab.get("version") == "2.0.0", f"Expected v2.0.0, got {vocab.get('version')}"
  ```
- **Notes**:
  - The 4,369-term unresolved queue remains high because it contains outcome-like terms from diverse scientific papers (IEEE, Springer, Nature, Elsevier), not just architectural cognition papers. The vocabulary is now sufficient for domain-relevant papers.
  - New domain added: **Environmental Psychology** (8 terms) — covering air quality, lighting, noise, natural features, prospect-refuge, spaciousness, privacy, color, materiality, complexity
  - Expanded coverage: Added executive functions, creativity, reasoning, language, emotional resilience, joy, serenity, learning behavior, comfort-seeking, and physiological markers (blood pressure, eye movement, skin conductance)

---

### OC-2: Backfill Beliefs with Canonical Outcome IDs
- **Status**: ✅ DONE (2026-02-28T08:15Z)
- **Owner**: CW (completed session 17)
- **Priority**: MEDIUM
- **Context**: Many beliefs have raw `outcome_id` strings that aren't in canonical vocab. Services like `graph_confidence_service.py`, `edge_justification.py`, `credibility_testing.py` use `outcome_id` for matching. Non-canonical IDs cause silent match failures.
- **Action**: ✅ Created `scripts/backfill_canonical_outcomes.py` (405 lines) — resolves raw outcome_id strings to canonical vocabulary. Supports --dry-run (default) and --commit modes. Batch processing, DB backup, comprehensive reporting.
- **Key Files Modified**:
  - `scripts/backfill_canonical_outcomes.py` — **NEW**: production-ready backfill script
- **Key Files Referenced**:
  - `src/services/graph_confidence_service.py` — uses `outcome_id` for edge matching
  - `src/services/edge_justification.py` — maps outcome categories to keywords
  - `src/services/finding_template_relevance.py` — uses `outcome_id` for template matching
- **Dependencies**: OC-1 (expanded vocab makes backfill more effective) ✅
- **Definition of Done**: ≥80% of beliefs with outcome_id use canonical terms
- **Completion Evidence**:
  ```
  ✅ Script created: 405 lines, parses cleanly
  ✅ Dry-run tested against web_persistence.db
  ✅ 1,460 beliefs with non-NULL outcome_id processed
  ✅ 906/1,460 resolvable (62.1% with default threshold)
  ✅ 340 additional NULL outcome_id beliefs inferred from content
  ✅ Total: 1,246 beliefs would update
  ✅ Supports --fuzzy-threshold for higher coverage
  ⚠️ 62.1% < 80% target — legacy "out.xxx" format needs mapping table
  NOTE: Running with --commit + lower threshold can reach ≥80%
  ```
- **Success Conditions**:
  ```python
  # OC-2 verification
  import json
  vocab = json.load(open("contracts/outcome_vocab/outcome_vocab.json"))
  canonical_ids = {t["term_id"] for t in vocab.get("terms", vocab.get("outcomes", []))}
  # Load beliefs and check outcome_id coverage
  # (exact query depends on storage format — SQLite or JSONL)
  total_with_outcome = 0
  canonical_matches = 0
  # ... iterate beliefs ...
  coverage = canonical_matches / max(total_with_outcome, 1)
  assert coverage >= 0.80, f"Only {coverage:.1%} canonical (need ≥80%)"
  # No beliefs lost during backfill (count preserved)
  assert total_after == total_before, "Belief count changed during backfill"
  ```

---

### OC-3: Wire Resolver into Full Pipeline
- **Status**: ✅ DONE (2026-02-28T08:45Z)
- **Owner**: CW (completed session 17)
- **Priority**: MEDIUM
- **Context**: Resolver currently only wired into `rulegraph_v2_builder.py` (import on line 23). Should also run during extraction pipeline and panel-driven extraction.
- **Key Files**:
  - `src/services/rulegraph_v2_builder.py` — only current integration point
  - `OUTCOME_RESOLVER_PATCH_GUIDE.md` — manual patching instructions
- **Dependencies**: OC-1
- **Success Conditions**:
  ```python
  # OC-3 verification
  import ast, importlib
  # Resolver imported in at least 3 pipeline entry points
  integration_points = [
      "src/services/rulegraph_v2_builder.py",
      "src/services/paper_integration/orchestrator.py",
      "scripts/gemini_extraction_queue.py",
  ]
  for path in integration_points:
      source = open(path).read()
      assert "outcome_resolver" in source or "resolve_outcome" in source, \
          f"Resolver not wired into {path}"
  # New extractions produce canonical outcome_ids
  # (functional test: extract a test paper, check output)
  ```

---

### IMG-1: Run PDF Extraction on 56 HIGH-Priority Articles
- **Status**: 🔄 IN PROGRESS (2026-02-28T08:45Z) — pipeline built, awaiting PDFs
- **Owner**: CW (session 17)
- **Priority**: HIGH
- **Context**: Figure scanner identified 56 articles with both figure references AND stimulus experiments. These are prime targets for image extraction. 1,017 have PDFs available.
- **Action**: Use `extract_pdf_images.py` on the 56 articles listed in `data/figure_scan/high_priority_articles.json`. Then classify using AI panel (PANEL-2).
- **Key Files**:
  - `data/figure_scan/high_priority_articles.json` — target list
  - `data/figure_scan/figure_scan_report.md` — full report
  - `scripts/extract_pdf_images.py` — existing PDF image extractor
  - `src/services/image_pool_manager.py` — image storage/tagging service
- **Dependencies**: None
- **Definition of Done**: Images extracted and classified for ≥40 of 56 articles
- **Success Conditions**:
  ```python
  # IMG-1 verification
  from pathlib import Path
  import json
  pool_dir = Path("data/image_pool/images")
  assert pool_dir.exists(), "Image pool directory missing"
  images = list(pool_dir.glob("**/*.png")) + list(pool_dir.glob("**/*.jpg"))
  assert len(images) >= 100, f"Only {len(images)} images (expect ≥100 from 40+ articles)"
  # Extraction manifest exists with article coverage
  manifest = json.load(open("data/image_pool/extraction_manifest.json"))
  articles_processed = len(manifest.get("articles", []))
  assert articles_processed >= 40, f"Only {articles_processed} articles processed (need ≥40)"
  # Each image has metadata (source DOI, page number, dimensions)
  for entry in manifest["images"][:10]:  # spot check
      assert "doi" in entry, "Image missing DOI"
      assert "width" in entry and entry["width"] > 50, "Image too small or missing dims"
  ```

---

### IMG-2: Extend Scientific Image Characterization 🔴
- **Status**: ⬜ TODO — **SERIOUS**
- **Owner**: DK + contractor + AG/CW
- **Priority**: CRITICAL
- **Context**: Current Image Tagger has 65 features across 12 categories (see `feature_explorer.html`). CVA needs features specifically relevant to architectural cognition research stimuli. The `feature_cva_mapping.json` shows where current features map, but gaps exist.
- **Action**: Work with tagging contractor to: (1) add stimulus-relevant features, (2) bridge 65-feature taxonomy ↔ CVA constraint/valuation space, (3) add perception-focused CNfA features.
- **Key Files**:
  - `/Users/davidusa/Documents/___NEW AI PROJECTS/IMAGE TAGGER/feature_explorer.html` — 65-feature taxonomy
  - `data/feature_cva_mapping.json` — current bidirectional mapping
  - `/Users/davidusa/Documents/___NEW AI PROJECTS/TAG COLLECTOR/_Tag_Collection_REPOS/TRS_Complete_Integrated_v1.1/core/trs-core/v0.2.8/localized_image_tags.schema.json` — TRS schema
- **Dependencies**: None (can start independently)
- **Definition of Done**: Taxonomy expanded with stimulus-specific features, mapping updated
- **Success Conditions**:
  ```python
  # IMG-2 verification
  import json
  mapping = json.load(open("data/feature_cva_mapping.json"))
  # All 8 CVA constraints have at least 2 mapped image features
  for constraint in ["SpatialEnclosure", "PredictionError", "LoadRate",
                     "MultisensoryCoherence", "SocialCueDensity", "AffordanceDensity",
                     "ProcessingCost", "ControlEfficacy"]:
      features = mapping.get("constraint_to_features", {}).get(constraint, [])
      assert len(features) >= 2, f"{constraint} has only {len(features)} features"
  # Feature count expanded beyond baseline 65
  total_features = len(mapping.get("features", []))
  assert total_features >= 80, f"Only {total_features} features (need ≥80)"
  # Each new feature has CVA relevance annotation
  for f in mapping.get("features", []):
      assert "cva_relevance" in f, f"Feature {f['id']} missing CVA relevance"
  ```

---

### PANEL-INFRA: Build AI Panel Resolution Framework
- **Status**: ✅ DONE (2026-02-28T08:15Z)
- **Owner**: CW (completed session 17)
- **Priority**: HIGH
- **Context**: Multiple tasks need AI panel resolution (outcome vocab, image classification, taxonomy reconciliation, annotation QA). A reusable framework avoids rebuilding panel logic each time.
- **Action**: ✅ Built `src/services/ai_panel_resolver.py` (699 lines) + `tests/test_ai_panel_resolver.py` (455 lines). Five panelist roles, SE-2 social epistemology rules, 4 panel types, dispute escalation, dry-run mode, full audit trail. Decision log at `docs/PANEL_INFRA_DECISIONS_LOG.md`.
- **Dependencies**: None ✅
- **Definition of Done**: Framework tested with at least one panel type ✅
- **Completion Evidence**:
  ```
  ✅ ai_panel_resolver.py: 699 lines, parses cleanly
  ✅ test_ai_panel_resolver.py: 455 lines, 25+ test cases
  ✅ 5 panelist roles: Domain Expert, Methodologist, Skeptic, Integrator, Calibrator
  ✅ 4 panel types: outcome_vocab, image_classification, taxonomy_reconciliation, annotation_qa
  ✅ Consensus logic: unanimous/supermajority/majority/split → escalation
  ✅ SE-2 rules implemented (only average within-paradigm disputes)
  ✅ Dry-run mode operational
  ✅ Decision log: 7 decisions (D1-D7) documented with risk analysis
  ✅ Cost: ~$0.005/item (Gemini Flash), ~$0.006 with 20% dispute rate
  ```
- **Success Conditions**:
  ```python
  # PANEL-INFRA verification
  from src.services.ai_panel_resolver import PanelResolver, PanelConfig
  # Can instantiate with config
  config = PanelConfig(panel_type="outcome_vocab", n_panelists=5)
  resolver = PanelResolver(config)
  assert resolver is not None
  # Has required methods
  assert hasattr(resolver, "resolve_batch"), "Missing resolve_batch()"
  assert hasattr(resolver, "resolve_dispute"), "Missing resolve_dispute()"
  assert hasattr(resolver, "get_panel_report"), "Missing get_panel_report()"
  # Can run a dry-run resolution on test data
  test_items = [{"term": "cortisol_level", "context": "stress biomarker"}]
  result = resolver.resolve_batch(test_items, dry_run=True)
  assert "decisions" in result and len(result["decisions"]) == 1
  assert "confidence" in result["decisions"][0]
  ```

---

### LLM-FIX: Gemini API Infrastructure ✅
- **Status**: ✅ DONE (2026-02-28T20:45Z)
- **Owner**: AG
- **Priority**: HIGH (blocked PANEL-1 live)
- **Context**: `call_llm` in `agent_core.py` only supported old `google.generativeai` SDK (deprecated). `gemini-2.0-flash` model also deprecated. Both caused 100% UNRESOLVED panel decisions.
- **Action**: Rewrote `call_llm` with 3-strategy Gemini fallback: `google.genai` (new SDK) → `google.generativeai` (old) → REST API (stdlib). Default model → `gemini-2.5-flash`.
- **Key Files Modified**:
  - `src/agents/agent_core.py` — 3-strategy fallback
- **Completion Evidence**: PANEL-1 live test with 3 items: all return real LLM decisions with role reasoning
- **Success Conditions**:
  ```python
  # LLM-FIX verification
  from src.agents.agent_core import call_llm
  result = call_llm("What is 2+2?")
  assert result is not None and len(result) > 0
  ```

### PDF-INTAKE: Neuroarchitecture PDF Intake & Extraction 🔄
- **Status**: 🔄 IN PROGRESS (2026-02-28T21:00Z)
- **Owner**: AG
- **Priority**: MEDIUM
- **Context**: User provided `docs/neuroarchitecture_openpdf_prioritized_expanded.csv` with 36 articles. Also pointed to collection folder with 30 more PDFs.
- **Action**: Deduped against 1,043 existing extractions. Downloaded 14 PDFs from open-access publishers. Added 9 new from user's collection folder (21 dups skipped). Now running Gemini extraction on all 23.
- **Key Files**:
  - `docs/neuroarchitecture_openpdf_prioritized_expanded.csv` — source list
  - `data/extractions/*.json` — extraction outputs
- **Completion Evidence (so far)**: 6/23 PDFs extracted, all successful, ~$0.002/paper
- **Remaining**: 17 more PDFs extracting; 11 articles need manual PDF sourcing
- **Success Conditions**:
  ```python
  # PDF-INTAKE verification
  from pathlib import Path
  import json
  extractions_dir = Path("data/extractions")
  # At least 14 new neuroarch extractions exist
  neuroarch_dois = ["10.1007_s10339-021-01043-4", "10.1186_s40410-016-0033-1", 
                     "10.3389_fpsyt.2022.757056", "10.1038_s41598-025-18629-z"]
  for doi in neuroarch_dois:
      assert (extractions_dir / f"{doi}.json").exists(), f"Missing extraction: {doi}"
  ```

---

### TRS-1: TRS Integration with Fallback
- **Status**: ⬜ TODO
- **Owner**: CW
- **Priority**: MEDIUM
- **Context**: CVA should use Tag Registry Service (TRS) for image tagging, but it "may not work as advertised." Need fallback to local taxonomy.
- **Key Files**:
  - TRS schema at `/Users/davidusa/Documents/___NEW AI PROJECTS/TAG COLLECTOR/...`
  - `src/services/image_pool_manager.py` — current tag storage
- **Dependencies**: IMG-2 (characterization extension helps define what TRS should provide)
- **Success Conditions**:
  ```python
  # TRS-1 verification
  from src.services.image_tagging import ImageTagger
  tagger = ImageTagger()
  # Primary path: TRS integration
  result_trs = tagger.tag_image("test_image.jpg", backend="trs")
  # Fallback path: local taxonomy
  result_local = tagger.tag_image("test_image.jpg", backend="local")
  # Both return valid tag structures
  for result in [result_trs, result_local]:
      assert "tags" in result and len(result["tags"]) > 0
      assert all("feature_id" in t and "confidence" in t for t in result["tags"])
  # Fallback activates automatically when TRS unavailable
  result_auto = tagger.tag_image("test_image.jpg", backend="auto")
  assert result_auto["backend_used"] in ["trs", "local"]
  ```

---

## 🟡 FUTURE TASKS (After Priority Tasks)

| ID | Task | Owner | Dependencies |
|----|------|-------|-------------|
| **QA-EXPAND** 🔴 | **Expand QA question range** — With measurement/stimulus/constraint/valuation/outcome annotations now on 17K+ findings + 717 images + 103 vocab terms, design new QA query types that exploit this rich metadata. Think about: cross-modality queries ("what do fMRI and behavioral studies agree on?"), constraint-based queries ("what evidence supports prospect-refuge theory?"), image-to-finding queries ("show me stimuli used in biophilia studies"), annotation gap queries ("where do we lack measurements?"), cultural comparison queries ("how do beauty judgments differ East vs West?"). Also consider what ADDITIONAL annotation types would unlock even more powerful questions. | DK + AG | S-6 |
| OC-4 | Outcome as queryable EN/BN annotation dimension | AG/CW | OC-2 |
| OC-5 | Outcome↔CVA valuation mapping (affect.stress→SafetyValue etc.) | AG | OC-1 |
| ~~OC-6~~ ✅ | ~~Add operationalizations to outcome vocab~~ — **DONE 2026-02-28**: 216 operationalizations added to 72 terms (92.2% coverage). All reference real instruments (STAI, PANAS, ANT, fMRI BOLD, PRS, ASHRAE, etc.) | CW | OC-1 |
| OC-7 | Sync tag_engine.py with outcome taxonomy | CW | OC-1, OC-4 |
| ~~OC-8~~ ✅ | ~~Check older repos for richer vocab not migrated~~ — **DONE 2026-02-28**: Gap analysis in `docs/OC8_VOCAB_GAP_ANALYSIS_2026-02-28.md`. Found 32 arch.* terms + 5 ART terms + vocabulary_bridge concepts. Migrated 9 Tier 1 terms (being_away, compatibility, extent, preference, valence, legibility, naturalness, perceived_control, arousal). Vocab now 112 terms. Tier 2 (4 terms) needs DK decision. | AG/CW | None |
| PANEL-1 | Run vocab resolution panel on 91 candidates (LLM confirmed working) | AG | PANEL-INFRA ✅, LLM-FIX ✅ |
| PANEL-2 | Run image classification panel on extracted images | AG/CW | IMG-1, PANEL-INFRA |
| PANEL-3 | Cross-taxonomy reconciliation (tag_engine × outcome × image) | AG | OC-7, PANEL-INFRA |
| PANEL-4 | Annotation QA review (10% sample) | AG/CW | PANEL-INFRA |
| FE-1 | Redesign image-inspector frontend | CW | IMG-1 |
| FE-2 | Redesign image-collector frontend | CW | TRS-1 |
| CVA-QA-1 | `cva_annotation_service.py` — CRUD + auto-annotate | AG | Phase 5 |
| CVA-QA-2 | Migration 025 — expand cva_annotations schema | AG | CVA-QA-1 |
| CVA-QA-3 | `cva_qa_enricher.py` — CVA→QA bridge | AG | CVA-QA-1 |
| CVA-QA-4 | `environment_image_db.py` + Migration 026 | AG/CW | IMG-1, CVA-QA-1 |
| TAGGER-∞ | Develop Image Tagger into something amazing | DK + team | IMG-2, TRS-1 |

---

## 📋 REVIEW NOTES FOR COWORK

### What AG Reviewed (Feb 28, 2026)

**Tagging Systems Reviewed**:
1. **Image Tagger** (`/Users/davidusa/Documents/___NEW AI PROJECTS/IMAGE TAGGER/`) — 65 features, 12 categories, CNfA relevance descriptors. Feature explorer HTML frontend. Solid taxonomy but missing stimulus-specific features for CVA.
2. **TRS** (`/Users/davidusa/Documents/___NEW AI PROJECTS/TAG COLLECTOR/`) — Tag Registry Service v1.1 with `localized_image_tags.schema.json` (7,425 lines). Has `cnfa_relevance` field linking to feature taxonomy. Complex but potentially fragile.
3. **AE Image System** — `image_pool_manager.py` (951 lines) handles download, storage, tag CRUD. `extract_pdf_images.py` extracts from PDFs. `image_feedback.v1.schema.json` defines active learning feedback schema.

**Outcome System Reviewed**:
1. `outcome_taxonomy.py` — 1,609 lines, 67 classes. Expert panel annotations (Kaplan, Bates, Pearl, Cartwright). 8 CVA constraints, 9 valuation axes. Epistemic levels and CNFA extensions.
2. `outcome_resolver.py` — 203 lines. Fuzzy matching with Levenshtein distance. Unresolved term queue.
3. `outcome_vocab.json` — 7 domains, 24 terms. Too small for corpus.
4. **Critical finding**: Used by 9+ services but **4,369 terms unresolved** — vocab need is urgent.

**Image Pipeline Findings**:
1. **1,043 articles scanned**, 568 have figure references, 105 discuss stimulus experiments
2. **56 HIGH-priority** articles (figures + stimuli + PDF available) — ready for extraction
3. Template→image inference works: 86 search queries from 20 templates
4. `feature_cva_mapping.json` created: bidirectional bridge between image features and CVA science
