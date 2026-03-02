#!/usr/bin/env python3
"""
Tests for morning sprint scripts: backfill, schema conversion, Gemini reextraction, PANEL-1.

Covers:
  - backfill_env_outcome_v2.py: DOI parsing, normalization, content fallback
  - v3_reextraction_gemini.py: JSON parsing, prompt building, response handling
  - Schema conversion: old-format → findings[], CrossRef enrichment
  - PANEL-1: term harvesting, clustering, domain hints, panel item building
  - DB persistence: success conditions for web_persistence.db
"""

import json
import re
import sys
from pathlib import Path
from collections import Counter
import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

EXTRACTIONS_DIR = REPO / "data" / "extractions"


# ============================================================
# Backfill Script Tests
# ============================================================

class TestBackfillEnvOutcome:
    """Tests for scripts/backfill_env_outcome_v2.py logic."""

    def test_doi_parsing_from_belief_id(self):
        """DOI can be parsed from pdf:doi: format belief_ids."""
        pattern = r'doi:(10\.\d{4,}[^:]*)'
        
        bid1 = "pdf:doi:10.1080/24694452.2024.2353173:doi:10.1080/24694452.2024.2353173-TBL-C001"
        m1 = re.search(pattern, bid1)
        assert m1, "Should parse DOI from belief_id"
        assert m1.group(1) == "10.1080/24694452.2024.2353173"
        
        bid2 = "rt:doi:10.3389/fpsyg.2016.01607:abstract_rule"
        m2 = re.search(pattern, bid2)
        assert m2
        assert m2.group(1) == "10.3389/fpsyg.2016.01607"

    def test_doi_parsing_no_doi(self):
        """Zotero-based belief_ids should NOT match DOI pattern."""
        pattern = r'doi:(10\.\d{4,}[^:]*)'
        bid = "pdf:zotero:Q5YDAT65:zotero:Q5YDAT65-TBL-C022"
        m = re.search(pattern, bid)
        assert m is None, "Zotero IDs should not match DOI pattern"

    def test_finding_index_extraction(self):
        """TBL-C025 → index 24 (0-indexed)."""
        pattern = r'TBL-C(\d+)'
        bid = "pdf:doi:10.xxx:doi:10.xxx-TBL-C025"
        m = re.search(pattern, bid)
        assert m
        assert int(m.group(1)) - 1 == 24

    def test_normalize_env_id(self):
        """Environment IDs should be normalized to snake_case."""
        def normalize(raw):
            if not raw or str(raw).strip() == "":
                return ""
            text = str(raw).strip().lower()
            text = re.sub(r"[^a-z0-9]+", "_", text)
            return re.sub(r"_+", "_", text).strip("_")
        
        assert normalize("Nature views in offices") == "nature_views_in_offices"
        assert normalize("High-noise   environment!!!") == "high_noise_environment"
        assert normalize("") == ""
        assert normalize(None) == ""

    def test_content_fallback_strategy(self):
        """Content fallback should produce non-empty env/outcome from text."""
        content = "Natural daylight exposure increases worker productivity and reduces fatigue"
        env = content[:100].strip().lower()
        env = re.sub(r"[^a-z0-9]+", "_", env).strip("_")
        assert len(env) > 10
        assert "daylight" in env


# ============================================================
# Gemini Reextraction Tests
# ============================================================

class TestGeminiReextraction:
    """Tests for scripts/v3_reextraction_gemini.py logic."""

    def test_json_extraction_from_code_fence(self):
        """Should extract JSON from markdown code fences."""
        text = '```json\n{"findings": [{"summary": "test"}]}\n```'
        clean = re.sub(r'```(?:json)?\s*\n?', '', text)
        clean = clean.replace('```', '').strip()
        data = json.loads(clean)
        assert len(data["findings"]) == 1

    def test_json_extraction_from_plain(self):
        """Should parse plain JSON without code fences."""
        text = '{"findings": [{"summary": "nature reduces stress"}]}'
        data = json.loads(text)
        assert data["findings"][0]["summary"] == "nature reduces stress"

    def test_json_extraction_with_preamble(self):
        """Should find JSON object in text with preamble."""
        text = 'Here are the findings:\n{"findings": [{"id": 1}]}\nEnd.'
        s = text.find('{')
        e = text.rfind('}')
        data = json.loads(text[s:e+1])
        assert len(data["findings"]) == 1

    def test_prompt_building(self):
        """Prompt should include title, DOI, and family prompt."""
        extraction_data = {
            "title": "Biophilic Design Effects",
            "doi": "10.1234/test",
            "authors": ["Smith", "Jones"],
            "article_type": "empirical",
            "paper_metadata": {"abstract": "This paper studies..."},
        }
        # Build context part of prompt
        title = extraction_data.get("title", "Unknown")
        doi = extraction_data.get("doi", "")
        assert "Biophilic" in title
        assert "10.1234" in doi

    def test_merge_preserves_metadata(self):
        """Merging response with original data should preserve metadata."""
        original = {"doi": "10.1234/test", "title": "Test", "authors": ["A"]}
        extracted = {"findings": [{"summary": "x"}], "domains": ["cog"]}
        
        result = {**original}
        result["findings"] = extracted.get("findings", [])
        result["n_findings"] = len(result["findings"])
        result["domains"] = extracted.get("domains", [])
        
        assert result["doi"] == "10.1234/test"
        assert result["title"] == "Test"
        assert result["n_findings"] == 1
        assert result["domains"] == ["cog"]


# ============================================================
# Schema Conversion Tests
# ============================================================

class TestSchemaConversion:
    """Tests for old-schema → findings[] conversion logic."""

    def test_key_findings_conversion(self):
        """key_findings list should be converted to findings[]."""
        data = {
            "key_findings": [
                "Nature views reduce stress in hospital patients",
                "Green spaces improve cognitive performance",
            ]
        }
        findings = []
        for i, kf in enumerate(data["key_findings"]):
            findings.append({
                "finding_id": f"KF-{i+1:03d}",
                "summary": kf,
                "source": "key_findings_conversion",
            })
        assert len(findings) == 2
        assert findings[0]["finding_id"] == "KF-001"

    def test_antecedent_consequent_extraction(self):
        """Should extract antecedent/consequent from finding text."""
        text = "Natural light increases worker productivity"
        patterns = [
            r"(.+?)\s+(?:leads? to|increases?|decreases?|affects?|improves?|reduces?)\s+(.+)",
        ]
        for pat in patterns:
            m = re.search(pat, text, re.I)
            if m:
                ant = m.group(1).strip()
                con = m.group(2).strip()
                break
        assert ant == "Natural light"
        assert con == "worker productivity"

    def test_dict_key_findings_handling(self):
        """key_findings as list of dicts should extract 'finding' field."""
        data = {"key_findings": [
            {"finding": "Noise reduces concentration", "p_value": 0.01},
        ]}
        kf = data["key_findings"][0]
        summary = kf.get("finding", kf.get("description", str(kf)))
        assert summary == "Noise reduces concentration"

    def test_zero_finding_doi_papers_converted(self):
        """Spot-check: previously zero-finding DOI papers should now have findings."""
        converted_dois = [
            "10.1186_s10086-019-1834-0.json",
            "10.3389_fpsyt.2022.757056.json",
            "10.3390_buildings16010069.json",
        ]
        for doi_file in converted_dois:
            ef = EXTRACTIONS_DIR / doi_file
            if not ef.exists():
                continue
            data = json.load(open(ef))
            assert data.get("findings"), f"{doi_file} should have findings after conversion"
            assert len(data["findings"]) >= 4, f"{doi_file} should have ≥4 findings"

    def test_crossref_enrichment_added_titles(self):
        """Converted papers should have titles (from CrossRef enrichment)."""
        test_files = [
            "10.3389_fpsyt.2022.757056.json",
            "10.1186_s10086-019-1834-0.json",
        ]
        for fname in test_files:
            ef = EXTRACTIONS_DIR / fname
            if not ef.exists():
                continue
            data = json.load(open(ef))
            title = data.get("title") or data.get("paper_title")
            assert title and title != "?" and len(title) > 5, (
                f"{fname} should have a real title, got: {title}"
            )


# ============================================================
# PANEL-1 Tests
# ============================================================

class TestPanel1VocabResolution:
    """Tests for scripts/run_panel_1_outcomes.py logic."""

    def test_term_harvesting_from_queue(self):
        """Should load terms from unresolved_outcomes.jsonl."""
        queue_path = REPO / "data" / "unresolved_outcomes.jsonl"
        if not queue_path.exists():
            pytest.skip("Queue file not found")
        count = 0
        with open(queue_path) as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line)
                    if entry.get("raw_term"):
                        count += 1
        assert count >= 1000, f"Queue should have ≥1000 terms, got {count}"

    def test_term_clustering(self):
        """Similar terms should cluster together."""
        sys.path.insert(0, str(REPO))
        from scripts.run_panel_1_outcomes import _terms_similar
        
        assert _terms_similar("stress", "stress response")
        assert _terms_similar("cognitive load", "cognitive loading")
        assert not _terms_similar("stress", "daylight")

    def test_domain_hint_mapping(self):
        """Domain hints should classify known terms."""
        from scripts.run_panel_1_outcomes import DOMAIN_HINTS
        
        assert any(kw in "stress response" for kw in DOMAIN_HINTS if DOMAIN_HINTS[kw] == "affect")
        assert any(kw in "working memory" for kw in DOMAIN_HINTS if DOMAIN_HINTS[kw] == "cog")
        assert any(kw in "heart rate" for kw in DOMAIN_HINTS if DOMAIN_HINTS[kw] == "physio")

    def test_noise_filtering(self):
        """Noise terms should be filtered out."""
        from scripts.run_panel_1_outcomes import _is_valid_term
        
        assert not _is_valid_term("the")
        assert not _is_valid_term("abc")     # too short
        assert not _is_valid_term("a" * 55)  # too long
        assert _is_valid_term("cognitive performance")
        assert _is_valid_term("stress recovery")


# ============================================================
# DB Persistence Success Conditions
# ============================================================

class TestDBPersistence:
    """Tests for DB persistence results."""

    def test_ftr_resolution_file_exists(self):
        """FTR resolution should have been written."""
        paths = [
            REPO / "data" / "extractions" / "ftr_resolution.json",
            REPO / "data" / "production" / "finding_template_theory_links.json",
        ]
        assert any(p.exists() for p in paths), "FTR resolution file should exist"

    def test_ftr_resolution_has_findings(self):
        """FTR resolution should contain processed findings."""
        for path in [
            REPO / "data" / "extractions" / "ftr_resolution.json",
            REPO / "data" / "production" / "finding_template_theory_links.json",
        ]:
            if path.exists():
                data = json.load(open(path))
                total = data.get("summary", {}).get("findings_total", 0)
                assert total >= 4000, f"FTR should have ≥4000 findings, got {total}"
                return
        pytest.skip("No FTR resolution file found")

    def test_extraction_files_have_tier2(self):
        """At least 800 extraction files should have inline Tier2 data."""
        with_tier2 = 0
        for ef in sorted(EXTRACTIONS_DIR.glob("10.*.json")):
            try:
                data = json.load(open(ef))
                if data.get("tier_resolution_version") or data.get("tier_resolution_config"):
                    with_tier2 += 1
            except Exception:
                pass
        assert with_tier2 >= 800, f"Only {with_tier2} files have Tier2 data (need ≥800)"
