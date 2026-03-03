"""
Tier Taxonomy Consistency Tests
================================

Verifies that all subsystems agree on the canonical tier taxonomy:
  T1  = 10 framework theories
  T1.5= 13 domain theories (loaded from schemas/theory/tier1_5_domain_theories.json)
  T2  = ~166 CMR templates
  Molecules = 18 latent variables
  T3  = dynamic (empirical beliefs — count varies)

SUCCESS CONDITIONS:
  1. Canonical JSON files exist and have correct counts
  2. Code that loads from JSON gets the right number
  3. No stale hardcoded "4 T1.5" strings in key code files
  4. T1 keywords in tag_engine use kebab-case IDs, not abbreviations
  5. QA catalog output includes all 13 T1.5 theories

Created: 2026-03-02
Sprint: QA System Quality → 9.5+
"""

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


# =============================================================================
# SUCCESS CONDITION 1: Canonical JSON files have correct counts
# =============================================================================

class TestCanonicalSchemas:
    """Verify canonical schema files exist and have correct entity counts."""

    def test_t1_frameworks_count(self):
        """T1: Exactly 10 framework theories."""
        path = ROOT / "schemas" / "theory" / "tier1_frameworks.json"
        assert path.exists(), f"Missing canonical T1 file: {path}"
        data = json.loads(path.read_text())
        # Frameworks are nested under 'frameworks' key
        frameworks = data.get("frameworks", data)
        # Filter out schema/metadata keys
        frameworks = {k: v for k, v in frameworks.items() if not k.startswith("$") and k not in ("title", "description", "version", "criteria")}
        assert len(frameworks) == 10, (
            f"Expected 10 T1 frameworks, got {len(frameworks)}: {list(frameworks.keys())}"
        )

    def test_t1_5_domain_theories_count(self):
        """T1.5: Exactly 13 domain theories."""
        path = ROOT / "schemas" / "theory" / "tier1_5_domain_theories.json"
        assert path.exists(), f"Missing canonical T1.5 file: {path}"
        data = json.loads(path.read_text())
        theories = data.get("domain_theories", {})
        assert len(theories) == 13, (
            f"Expected 13 T1.5 domain theories, got {len(theories)}: {list(theories.keys())}"
        )

    def test_t1_5_has_required_theories(self):
        """T1.5 must include all 13 canonical theories."""
        path = ROOT / "schemas" / "theory" / "tier1_5_domain_theories.json"
        data = json.loads(path.read_text())
        theories = data.get("domain_theories", {})
        required = {
            "ART", "SRT", "BIOPHILIA", "PROSPECT_REFUGE",
            "PRIVACY_REGULATION", "KAPLAN_PREFERENCE", "ADAPTIVE_THERMAL",
            "SPACE_SYNTAX", "SOUNDSCAPE", "PLACE_ATTACHMENT",
            "BRECVEMA", "FLOW", "GOLDILOCKS",
        }
        missing = required - set(theories.keys())
        assert not missing, f"Missing T1.5 theories: {missing}"

    def test_t1_5_goldilocks_provenance(self):
        """Goldilocks Principle must credit Berlyne as originator and Kirsh as extender."""
        path = ROOT / "schemas" / "theory" / "tier1_5_domain_theories.json"
        data = json.loads(path.read_text())
        goldilocks = data["domain_theories"]["GOLDILOCKS"]
        assert "Berlyne" in goldilocks["originator"], "Goldilocks must credit Berlyne"
        assert "Kirsh" in goldilocks["originator"], "Goldilocks must credit Kirsh"
        assert "subsumes" in goldilocks, "Goldilocks must declare it subsumes Berlyne"

    def test_t1_5_each_has_required_fields(self):
        """Every T1.5 theory must have name, originator, primary_t1_frameworks, coverage, maturity."""
        path = ROOT / "schemas" / "theory" / "tier1_5_domain_theories.json"
        data = json.loads(path.read_text())
        for tid, info in data.get("domain_theories", {}).items():
            for field in ["name", "originator", "primary_t1_frameworks", "coverage", "maturity"]:
                assert field in info, f"T1.5 theory {tid} missing field: {field}"
            assert len(info["primary_t1_frameworks"]) >= 2, (
                f"T1.5 theory {tid} needs ≥2 parent T1 frameworks, has {len(info['primary_t1_frameworks'])}"
            )

    def test_t1_frameworks_use_kebab_case_ids(self):
        """T1 framework IDs must be kebab-case (not abbreviations)."""
        path = ROOT / "schemas" / "theory" / "tier1_frameworks.json"
        data = json.loads(path.read_text())
        frameworks = data.get("frameworks", data)
        for key in frameworks:
            if key.startswith("$") or key in ("title", "description", "version", "criteria"):
                continue
            assert "-" in key, f"T1 framework ID '{key}' should be kebab-case"
            assert key == key.lower(), f"T1 framework ID '{key}' should be lowercase"


# =============================================================================
# SUCCESS CONDITION 2: Code dynamically loads correct counts
# =============================================================================

class TestDynamicLoading:
    """Verify code that loads from canonical JSONs gets right counts."""

    def test_qa_handler_catalog_has_13_t15(self):
        """QA catalog output must list 13 T1.5 domain theories."""
        from src.services.arbitrary_qa_handler import ArbitraryQAHandler
        handler = ArbitraryQAHandler()
        result = handler.answer("Show me all theories")
        # Find the T1.5 section
        t15_section = None
        for section in result.get("sections", []):
            if "T1.5" in section.get("heading", ""):
                t15_section = section
                break
        assert t15_section is not None, "Catalog must have a T1.5 section"
        assert "(13)" in t15_section["heading"], (
            f"T1.5 section heading should say (13), got: {t15_section['heading']}"
        )
        assert len(t15_section["items"]) == 13, (
            f"T1.5 section should have 13 items, got {len(t15_section['items'])}"
        )

    def test_qa_handler_catalog_has_10_t1(self):
        """QA catalog output must list 10 T1 framework theories."""
        from src.services.arbitrary_qa_handler import ArbitraryQAHandler
        handler = ArbitraryQAHandler()
        result = handler.answer("Show me all theories")
        t1_section = None
        for section in result.get("sections", []):
            if "T1 —" in section.get("heading", "") or "T1 —" in section.get("heading", ""):
                t1_section = section
                break
        assert t1_section is not None, "Catalog must have a T1 section"
        assert len(t1_section["items"]) == 10, (
            f"T1 section should have 10 items, got {len(t1_section['items'])}"
        )

    def test_qa_handler_uses_full_names_not_abbreviations(self):
        """T1 framework items must use full names, not abbreviation-first format."""
        from src.services.arbitrary_qa_handler import ArbitraryQAHandler
        handler = ArbitraryQAHandler()
        result = handler.answer("Show me all theories")
        t1_section = None
        for section in result.get("sections", []):
            heading = section.get("heading", "")
            if "T1" in heading and "T1.5" not in heading and "Framework" in heading:
                t1_section = section
                break
        if t1_section:
            for item in t1_section["items"]:
                # Abbreviation-first format is "**PP — ..." or "**SN — ..."
                # But "**DMN/TPN Dynamics**" is a valid full name, not abbreviation-first
                # True abbreviation-first would be "**PP**: ..." or "**SN — ..."
                assert not re.match(r'\*\*[A-Z]{2,4}\s*[—\-:]', item), (
                    f"T1 item uses abbreviation-first format: {item[:80]}"
                )


# =============================================================================
# SUCCESS CONDITION 3: No stale hardcoded "4 T1.5" in key code files
# =============================================================================

class TestNoStaleHardcoding:
    """Ensure key code files don't have stale T1.5=4 hardcoding."""

    @pytest.mark.parametrize("rel_path", [
        "src/services/arbitrary_qa_handler.py",
    ])
    def test_no_stale_4_t15_in_code(self, rel_path):
        """Code files must not hardcode '4 T1.5' or '4 domain theories'."""
        path = ROOT / rel_path
        if not path.exists():
            pytest.skip(f"File not found: {rel_path}")
        content = path.read_text()
        assert "4 T1.5" not in content, f"{rel_path} still has stale '4 T1.5'"
        assert "4 domain theor" not in content.lower(), f"{rel_path} still has stale '4 domain theories'"


# =============================================================================
# SUCCESS CONDITION 4: tag_engine uses kebab-case IDs
# =============================================================================

class TestTagEngineConsistency:
    """Verify tag_engine uses canonical IDs, not abbreviations."""

    def test_t1_keywords_use_kebab_case(self):
        """T1_KEYWORDS keys must be kebab-case canonical IDs."""
        from src.services.paper_integration.tag_engine import T1_KEYWORDS
        for key in T1_KEYWORDS:
            assert "-" in key, (
                f"T1_KEYWORDS key '{key}' should be kebab-case, not abbreviation"
            )
            assert key == key.lower(), (
                f"T1_KEYWORDS key '{key}' should be lowercase"
            )

    def test_t1_keywords_match_canonical_ids(self):
        """T1_KEYWORDS keys should be a subset of canonical T1 framework IDs."""
        from src.services.paper_integration.tag_engine import T1_KEYWORDS
        path = ROOT / "schemas" / "theory" / "tier1_frameworks.json"
        canonical = json.loads(path.read_text())
        frameworks = canonical.get("frameworks", canonical)
        canonical_ids = {k for k in frameworks if not k.startswith("$") and k not in ("title", "description", "version", "criteria")}
        tag_ids = set(T1_KEYWORDS.keys())
        unexpected = tag_ids - canonical_ids
        assert not unexpected, (
            f"T1_KEYWORDS has IDs not in canonical tier1_frameworks.json: {unexpected}"
        )


# =============================================================================
# SUCCESS CONDITION 5: T3 is never hardcoded
# =============================================================================

class TestT3Dynamic:
    """T3 (empirical beliefs) count should never be hardcoded."""

    def test_qa_handler_no_hardcoded_t3_count(self):
        """QA handler should not hardcode a specific T3 belief count."""
        path = ROOT / "src" / "services" / "arbitrary_qa_handler.py"
        content = path.read_text()
        # Should not have patterns like "12,000 T3" or "3,420 T3"
        matches = re.findall(r'\d{3,}[,\d]* T3', content)
        assert not matches, (
            f"QA handler hardcodes T3 count: {matches}. T3 is dynamic."
        )
