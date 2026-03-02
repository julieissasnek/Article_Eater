"""Tests for theory link extraction module.

Tests cover:
1. Prompt generation with all theories listed
2. JSON parsing with valid input
3. JSON error handling
4. Theory ID validation
5. Theory roster completeness
"""

import json
import pytest

from prompts.theory_link_extraction import (
    generate_theory_link_prompt,
    parse_theory_link_response,
    THEORY_ROSTER_SUMMARY,
    get_theory_roster,
    validate_theory_roster,
)


class TestTheoryRoster:
    """Test theory roster loading and validation."""

    def test_theory_roster_loaded(self):
        """Theory roster should load successfully."""
        roster = get_theory_roster()
        assert len(roster) > 0, "Theory roster should not be empty"
        assert isinstance(roster, dict), "Theory roster should be a dict"

    def test_theory_roster_summary_contains_all_theories(self):
        """Theory roster summary should list all loaded theories."""
        roster = get_theory_roster()
        summary = THEORY_ROSTER_SUMMARY

        # Each theory_id should appear in the summary
        for theory_id in roster.keys():
            assert theory_id in summary, f"Theory {theory_id} missing from roster summary"

    def test_validate_theory_roster(self):
        """Validation function should report roster stats."""
        stats = validate_theory_roster()
        assert "total_theories" in stats
        assert "theory_ids" in stats
        assert stats["total_theories"] > 0
        assert isinstance(stats["theory_ids"], list)

    def test_theory_roster_summary_is_not_empty(self):
        """Theory roster summary should be substantive."""
        assert len(THEORY_ROSTER_SUMMARY) > 100, "Roster summary should be detailed"
        assert "CANONICAL THEORY ROSTER" in THEORY_ROSTER_SUMMARY


class TestPromptGeneration:
    """Test prompt generation."""

    def test_generate_theory_link_prompt_basic(self):
        """Should generate a valid prompt with all required components."""
        paper_text = "This is a test paper about natural light and mood."
        findings = [
            {
                "finding_id": "f1",
                "content": "Natural light increases mood valence",
            }
        ]

        prompt = generate_theory_link_prompt(paper_text, findings)

        assert isinstance(prompt, str), "Prompt should be a string"
        assert len(prompt) > 500, "Prompt should be substantive"
        assert "CANONICAL THEORY ROSTER" in prompt
        assert "natural light" in prompt.lower()
        assert '"finding_id": "f1"' in prompt

    def test_generate_theory_link_prompt_contains_examples(self):
        """Prompt should include few-shot examples."""
        paper_text = "Test paper."
        findings = [{"finding_id": "f1", "content": "Test finding"}]

        prompt = generate_theory_link_prompt(paper_text, findings)

        # Check for few-shot examples
        assert "PROCESSING_FLUENCY" in prompt
        assert "how-actually" in prompt
        assert "how-plausibly" in prompt

    def test_generate_theory_link_prompt_truncates_long_papers(self):
        """Long paper texts should be truncated to manage prompt size."""
        long_paper = "x" * 10000  # Very long text
        findings = [{"finding_id": "f1", "content": "Test"}]

        prompt = generate_theory_link_prompt(long_paper, findings)

        # Prompt should be reasonable size (not 10KB+ of repeated chars)
        assert len(prompt) < 15000, "Prompt should be truncated for very long papers"


class TestResponseParsing:
    """Test parsing of LLM responses."""

    def test_parse_valid_response_single_link(self):
        """Should parse a valid single-link response."""
        response = json.dumps({
            "theory_links": [
                {
                    "finding_id": "f1",
                    "theory_id": "PROCESSING_FLUENCY",
                    "from_variable": "visual_complexity",
                    "to_variable": "aesthetic_preference",
                    "from_level": "T1.5",
                    "to_level": "T1.5",
                    "activity": "supports",
                    "maturity": "how-actually",
                }
            ]
        })

        links = parse_theory_link_response(response)

        assert len(links) == 1
        assert links[0]["finding_id"] == "f1"
        assert links[0]["theory_id"] == "PROCESSING_FLUENCY"
        assert links[0]["activity"] == "supports"

    def test_parse_valid_response_multiple_links(self):
        """Should parse multiple theory links."""
        response = json.dumps({
            "theory_links": [
                {
                    "finding_id": "f1",
                    "theory_id": "PROCESSING_FLUENCY",
                    "activity": "supports",
                    "maturity": "how-actually",
                },
                {
                    "finding_id": "f2",
                    "theory_id": "BIOPHILIA",
                    "activity": "extends",
                    "maturity": "how-plausibly",
                },
            ]
        })

        links = parse_theory_link_response(response)

        assert len(links) == 2
        assert links[0]["theory_id"] == "PROCESSING_FLUENCY"
        assert links[1]["theory_id"] == "BIOPHILIA"

    def test_parse_empty_array(self):
        """Should handle finding with no theory links."""
        response = json.dumps({"theory_links": []})

        links = parse_theory_link_response(response)

        assert links == []

    def test_parse_response_with_markdown_code_blocks(self):
        """Should handle responses wrapped in markdown code blocks."""
        json_content = json.dumps({
            "theory_links": [
                {
                    "finding_id": "f1",
                    "theory_id": "PROCESSING_FLUENCY",
                    "activity": "supports",
                    "maturity": "how-actually",
                }
            ]
        })

        # Test with ```json wrapper
        response_with_json_block = f"```json\n{json_content}\n```"
        links = parse_theory_link_response(response_with_json_block)
        assert len(links) == 1

        # Test with ``` wrapper
        response_with_block = f"```\n{json_content}\n```"
        links = parse_theory_link_response(response_with_block)
        assert len(links) == 1

    def test_parse_invalid_json_raises_error(self):
        """Should raise ValueError on invalid JSON."""
        response = "This is not JSON at all"

        with pytest.raises(ValueError, match="Failed to parse JSON"):
            parse_theory_link_response(response)

    def test_parse_non_object_root_raises_error(self):
        """Should raise ValueError if root is not an object."""
        response = json.dumps([1, 2, 3])

        with pytest.raises(ValueError, match="Response root must be an object"):
            parse_theory_link_response(response)

    def test_parse_non_array_theory_links_raises_error(self):
        """Should raise ValueError if theory_links is not an array."""
        response = json.dumps({
            "theory_links": "not_an_array"
        })

        with pytest.raises(ValueError, match="theory_links must be an array"):
            parse_theory_link_response(response)

    def test_parse_invalid_theory_id_raises_error(self):
        """Should raise ValueError for unknown theory_id."""
        response = json.dumps({
            "theory_links": [
                {
                    "finding_id": "f1",
                    "theory_id": "NONEXISTENT_THEORY",
                    "activity": "supports",
                    "maturity": "how-actually",
                }
            ]
        })

        with pytest.raises(ValueError, match="invalid theory_id"):
            parse_theory_link_response(response)

    def test_parse_invalid_activity_raises_error(self):
        """Should raise ValueError for invalid activity."""
        response = json.dumps({
            "theory_links": [
                {
                    "finding_id": "f1",
                    "theory_id": "PROCESSING_FLUENCY",
                    "activity": "invalid_activity",
                    "maturity": "how-actually",
                }
            ]
        })

        with pytest.raises(ValueError, match="invalid activity"):
            parse_theory_link_response(response)

    def test_parse_invalid_maturity_raises_error(self):
        """Should raise ValueError for invalid maturity."""
        response = json.dumps({
            "theory_links": [
                {
                    "finding_id": "f1",
                    "theory_id": "PROCESSING_FLUENCY",
                    "activity": "supports",
                    "maturity": "invalid_maturity",
                }
            ]
        })

        with pytest.raises(ValueError, match="invalid maturity"):
            parse_theory_link_response(response)

    def test_parse_missing_required_field_raises_error(self):
        """Should raise ValueError if required fields missing."""
        response = json.dumps({
            "theory_links": [
                {
                    "finding_id": "f1",
                    "theory_id": "PROCESSING_FLUENCY",
                    # Missing activity and maturity
                }
            ]
        })

        with pytest.raises(ValueError, match="missing required field"):
            parse_theory_link_response(response)

    def test_parse_invalid_tier_level_raises_error(self):
        """Should raise ValueError for invalid tier levels."""
        response = json.dumps({
            "theory_links": [
                {
                    "finding_id": "f1",
                    "theory_id": "PROCESSING_FLUENCY",
                    "activity": "supports",
                    "maturity": "how-actually",
                    "from_level": "INVALID_LEVEL",
                }
            ]
        })

        with pytest.raises(ValueError, match="invalid from_level"):
            parse_theory_link_response(response)


class TestEndToEnd:
    """Integration tests."""

    def test_generate_and_parse_roundtrip(self):
        """Generated prompts should accept valid responses."""
        paper_text = "A study on spatial proportion and cognitive performance."
        findings = [
            {
                "finding_id": "f1",
                "content": "Ceiling height increases focus duration",
            }
        ]

        prompt = generate_theory_link_prompt(paper_text, findings)

        # Create a realistic response
        response = json.dumps({
            "theory_links": [
                {
                    "finding_id": "f1",
                    "theory_id": "PROCESSING_FLUENCY",
                    "activity": "supports",
                    "maturity": "how-plausibly",
                    "rationale": "Ceiling height may influence cognitive fluency",
                }
            ]
        })

        links = parse_theory_link_response(response)

        assert len(links) == 1
        assert links[0]["finding_id"] == "f1"
        assert "f1" in prompt  # Prompt should reference the finding

    def test_all_canonical_theories_usable(self):
        """All canonical theories should be valid for parsing."""
        roster = get_theory_roster()

        for theory_id in list(roster.keys())[:5]:  # Test subset
            response = json.dumps({
                "theory_links": [
                    {
                        "finding_id": "f1",
                        "theory_id": theory_id,
                        "activity": "supports",
                        "maturity": "how-actually",
                    }
                ]
            })

            # Should not raise error
            links = parse_theory_link_response(response)
            assert len(links) == 1
            assert links[0]["theory_id"] == theory_id
