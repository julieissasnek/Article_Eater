"""
Tests for table_extractor.py
Sprint 3.0 — 2026-02-08
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

from src.services.table_extractor import (
    ExtractionMethod,
    TableType,
    ExtractedCell,
    ExtractedTable,
    AIExtractionPrompt,
    AITableExtractor,
    PdfPlumberTableExtractor,
    HybridTableExtractor,
    get_table_extractor,
    extracted_table_to_article_metadata,
    extracted_table_to_rct_facts,
)


class TestExtractedTable:
    """Tests for ExtractedTable dataclass."""

    def test_create_basic_table(self):
        """Test creating a basic extracted table."""
        table = ExtractedTable(
            table_id="TBL-001",
            page_number=1,
            table_type=TableType.STUDY_CHARACTERISTICS,
            headers=["Study", "N", "Intervention"],
            rows=[
                ["Ulrich 1984", "46", "Window view"],
                ["Lohr 1996", "96", "Indoor plants"]
            ]
        )

        assert table.table_id == "TBL-001"
        assert table.page_number == 1
        assert table.table_type == TableType.STUDY_CHARACTERISTICS
        assert len(table.headers) == 3
        assert len(table.rows) == 2

    def test_table_to_dict(self):
        """Test converting table to dictionary."""
        table = ExtractedTable(
            table_id="TBL-001",
            page_number=1,
            table_type=TableType.RESULTS,
            headers=["Study", "Effect Size"],
            rows=[["Study A", "0.52"]]
        )

        d = table.to_dict()
        assert d["table_id"] == "TBL-001"
        assert d["table_type"] == "results"
        assert d["extraction_method"] == "ai_api"

    def test_table_to_markdown(self):
        """Test converting table to markdown."""
        table = ExtractedTable(
            table_id="TBL-001",
            page_number=1,
            table_type=TableType.RESULTS,
            title="Results Summary",
            headers=["Study", "N", "Effect"],
            rows=[
                ["Ulrich 1984", "46", "0.74"],
                ["Lohr 1996", "96", "0.52"]
            ],
            caption="Effect sizes are Cohen's d"
        )

        md = table.to_markdown()
        assert "### Results Summary" in md
        assert "| Study | N | Effect |" in md
        assert "| Ulrich 1984 | 46 | 0.74 |" in md
        assert "*Effect sizes are Cohen's d*" in md

    def test_table_to_markdown_no_title(self):
        """Test markdown without title."""
        table = ExtractedTable(
            table_id="TBL-001",
            page_number=1,
            table_type=TableType.RESULTS,
            headers=["A", "B"],
            rows=[["1", "2"]]
        )

        md = table.to_markdown()
        assert "| A | B |" in md
        assert "| 1 | 2 |" in md


class TestTableType:
    """Tests for TableType enum."""

    def test_all_types_defined(self):
        """Test all expected table types exist."""
        assert TableType.STUDY_CHARACTERISTICS
        assert TableType.RESULTS
        assert TableType.DEMOGRAPHICS
        assert TableType.INTERVENTION
        assert TableType.OUTCOMES
        assert TableType.QUALITY_ASSESSMENT
        assert TableType.UNKNOWN

    def test_type_values(self):
        """Test table type values."""
        assert TableType.STUDY_CHARACTERISTICS.value == "study_characteristics"
        assert TableType.RESULTS.value == "results"
        assert TableType.DEMOGRAPHICS.value == "demographics"


class TestAITableExtractor:
    """Tests for AITableExtractor."""

    def test_init_without_client(self):
        """Test initialization without API client."""
        extractor = AITableExtractor()
        assert extractor.api_client is None
        assert extractor.model == "claude-3-haiku-20240307"

    def test_init_with_client(self):
        """Test initialization with API client."""
        mock_client = Mock()
        extractor = AITableExtractor(api_client=mock_client, model="claude-3-5-sonnet")
        assert extractor.api_client == mock_client
        assert extractor.model == "claude-3-5-sonnet"

    def test_generate_table_id(self):
        """Test table ID generation."""
        extractor = AITableExtractor()
        id1 = extractor._generate_table_id()
        id2 = extractor._generate_table_id()

        assert id1.startswith("TBL-")
        assert id2.startswith("TBL-")
        assert id1 != id2  # Should be unique

    def test_looks_like_table_true(self):
        """Test detection of table-like content."""
        extractor = AITableExtractor()

        # Content with consistent columns
        content = """Study          N        Effect
Ulrich 1984    46       0.74
Lohr 1996      96       0.52
Berman 2008    38       0.45"""

        assert extractor._looks_like_table(content) is True

    def test_looks_like_table_false(self):
        """Test detection of non-table content."""
        extractor = AITableExtractor()

        content = """This is just a paragraph of text.
It doesn't have any table-like structure.
Just normal prose without columns."""

        assert extractor._looks_like_table(content) is False

    def test_guess_table_type_results(self):
        """Test guessing results table type."""
        extractor = AITableExtractor()

        content = """Study    Effect Size    95% CI         p-value
Ulrich   0.74 (d)       [0.28, 1.20]   0.020"""

        table_type = extractor._guess_table_type(content)
        assert table_type == TableType.RESULTS

    def test_guess_table_type_demographics(self):
        """Test guessing demographics table type."""
        extractor = AITableExtractor()

        content = """Group        Age (M±SD)    % Female    Education
Intervention 35.2 ± 8.4    52.1%       College"""

        table_type = extractor._guess_table_type(content)
        assert table_type == TableType.DEMOGRAPHICS

    def test_guess_table_type_quality(self):
        """Test guessing quality assessment table type."""
        extractor = AITableExtractor()

        content = """Study    Risk of Bias    Randomization    Blinding
Ulrich   Low risk        Low              High"""

        table_type = extractor._guess_table_type(content)
        assert table_type == TableType.QUALITY_ASSESSMENT

    def test_guess_table_type_study_characteristics(self):
        """Test guessing study characteristics table type."""
        extractor = AITableExtractor()

        content = """Study    Study Design    Sample Size    Population    Setting
Ulrich   RCT             N = 46         Patients      Hospital"""

        table_type = extractor._guess_table_type(content)
        assert table_type == TableType.STUDY_CHARACTERISTICS

    def test_guess_table_type_unknown(self):
        """Test unknown table type."""
        extractor = AITableExtractor()

        content = """Column A    Column B    Column C
Value 1     Value 2     Value 3"""

        table_type = extractor._guess_table_type(content)
        assert table_type == TableType.UNKNOWN

    def test_rule_based_extract(self):
        """Test fallback rule-based extraction."""
        extractor = AITableExtractor()

        content = """Study          N        Effect
Ulrich 1984    46       0.74
Lohr 1996      96       0.52"""

        table = extractor._rule_based_extract(
            content, page=1, table_type=TableType.RESULTS
        )

        assert table is not None
        assert len(table.headers) >= 2
        assert len(table.rows) >= 1
        assert table.confidence == 0.5
        assert table.extraction_method == ExtractionMethod.PDFPLUMBER

    def test_rule_based_extract_empty(self):
        """Test rule-based extraction with insufficient content."""
        extractor = AITableExtractor()

        table = extractor._rule_based_extract(
            "Short", page=1, table_type=TableType.UNKNOWN
        )

        assert table is None

    def test_extraction_prompts_defined(self):
        """Test all extraction prompts are defined."""
        assert TableType.STUDY_CHARACTERISTICS in AITableExtractor.EXTRACTION_PROMPTS
        assert TableType.RESULTS in AITableExtractor.EXTRACTION_PROMPTS
        assert TableType.QUALITY_ASSESSMENT in AITableExtractor.EXTRACTION_PROMPTS
        assert TableType.DEMOGRAPHICS in AITableExtractor.EXTRACTION_PROMPTS

    def test_extraction_prompt_structure(self):
        """Test extraction prompt has required fields."""
        prompt = AITableExtractor.EXTRACTION_PROMPTS[TableType.RESULTS]

        assert isinstance(prompt, AIExtractionPrompt)
        assert prompt.system_prompt
        assert prompt.extraction_prompt
        assert prompt.output_schema
        assert prompt.table_type == TableType.RESULTS

    def test_parse_ai_response_study_characteristics(self):
        """Test parsing AI response for study characteristics."""
        extractor = AITableExtractor()

        data = {
            "table_title": "Study Characteristics",
            "headers": ["Citation", "Type", "N"],
            "studies": [
                {
                    "citation": "Ulrich (1984)",
                    "study_type": "RCT",
                    "sample_size": 46,
                    "population": "Post-surgery patients",
                    "setting": "Hospital",
                    "intervention": "Window view"
                }
            ]
        }

        table = extractor._parse_ai_response(
            data, page=1, table_type=TableType.STUDY_CHARACTERISTICS
        )

        assert table.title == "Study Characteristics"
        assert len(table.rows) == 1
        assert "Ulrich (1984)" in table.rows[0][0]

    def test_parse_ai_response_results(self):
        """Test parsing AI response for results."""
        extractor = AITableExtractor()

        data = {
            "table_title": "Results",
            "headers": [],
            "results": [
                {
                    "citation": "Ulrich (1984)",
                    "outcome": "Hospital stay",
                    "effect_size": 0.74,
                    "effect_size_type": "d",
                    "ci_lower": 0.28,
                    "ci_upper": 1.20,
                    "p_value": 0.020
                }
            ]
        }

        table = extractor._parse_ai_response(
            data, page=1, table_type=TableType.RESULTS
        )

        assert len(table.rows) == 1
        assert "0.74 (d)" in table.rows[0][2]  # Effect size
        assert "[0.28, 1.20]" in table.rows[0][3]  # CI
        assert "0.020" in table.rows[0][4]  # p-value


class TestPdfPlumberTableExtractor:
    """Tests for PdfPlumberTableExtractor."""

    def test_init(self):
        """Test initialization."""
        extractor = PdfPlumberTableExtractor()
        # Should initialize even if pdfplumber not installed
        assert extractor._table_counter == 0

    def test_generate_table_id(self):
        """Test table ID generation."""
        extractor = PdfPlumberTableExtractor()
        id1 = extractor._generate_table_id()
        id2 = extractor._generate_table_id()

        assert id1.startswith("TBL-")
        assert id1 != id2

    def test_guess_type_results(self):
        """Test guessing results table type."""
        extractor = PdfPlumberTableExtractor()
        content = "effect size p-value confidence interval"
        assert extractor._guess_type_from_content(content) == TableType.RESULTS

    def test_guess_type_demographics(self):
        """Test guessing demographics table type."""
        extractor = PdfPlumberTableExtractor()
        content = "age gender female male demographic baseline"
        assert extractor._guess_type_from_content(content) == TableType.DEMOGRAPHICS

    def test_guess_type_quality(self):
        """Test guessing quality assessment table type."""
        extractor = PdfPlumberTableExtractor()
        content = "risk of bias low risk high risk cochrane"
        assert extractor._guess_type_from_content(content) == TableType.QUALITY_ASSESSMENT


class TestHybridTableExtractor:
    """Tests for HybridTableExtractor."""

    def test_init(self):
        """Test initialization."""
        extractor = HybridTableExtractor()
        assert extractor.ai_extractor is not None
        assert extractor.plumber_extractor is not None

    def test_init_with_client(self):
        """Test initialization with API client."""
        mock_client = Mock()
        extractor = HybridTableExtractor(api_client=mock_client)
        assert extractor.ai_extractor.api_client == mock_client


class TestGetTableExtractor:
    """Tests for factory function."""

    def test_get_ai_extractor(self):
        """Test getting AI extractor."""
        extractor = get_table_extractor(ExtractionMethod.AI_API)
        assert isinstance(extractor, AITableExtractor)

    def test_get_pdfplumber_extractor(self):
        """Test getting pdfplumber extractor."""
        extractor = get_table_extractor(ExtractionMethod.PDFPLUMBER)
        assert isinstance(extractor, PdfPlumberTableExtractor)

    def test_get_hybrid_extractor(self):
        """Test getting hybrid extractor."""
        extractor = get_table_extractor(ExtractionMethod.HYBRID)
        assert isinstance(extractor, HybridTableExtractor)

    def test_get_extractor_with_client(self):
        """Test getting extractor with API client."""
        mock_client = Mock()
        extractor = get_table_extractor(
            ExtractionMethod.AI_API,
            api_client=mock_client,
            model="claude-3-5-sonnet"
        )
        assert extractor.api_client == mock_client
        assert extractor.model == "claude-3-5-sonnet"


class TestConversionFunctions:
    """Tests for conversion to export engine types."""

    def test_extracted_table_to_article_metadata(self):
        """Test converting table to ArticleMetadata."""
        table = ExtractedTable(
            table_id="TBL-001",
            page_number=1,
            table_type=TableType.STUDY_CHARACTERISTICS,
            headers=["Citation", "Type", "N", "Population", "Setting"],
            rows=[
                ["Ulrich (1984)", "RCT", "46", "Post-surgery patients", "Hospital"],
                ["Lohr (1996)", "RCT", "96", "Office workers", "Lab"]
            ]
        )

        metadata = extracted_table_to_article_metadata(table, row_index=0)

        assert metadata is not None
        assert metadata.citation == "Ulrich (1984)"
        assert metadata.year == 1984
        assert metadata.sample_size == 46
        assert metadata.study_type == "RCT"
        assert metadata.setting == "Hospital"

    def test_extracted_table_to_article_metadata_second_row(self):
        """Test converting second row."""
        table = ExtractedTable(
            table_id="TBL-001",
            page_number=1,
            table_type=TableType.STUDY_CHARACTERISTICS,
            headers=["Citation", "Type", "N"],
            rows=[
                ["Ulrich (1984)", "RCT", "46"],
                ["Lohr (1996)", "RCT", "96"]
            ]
        )

        metadata = extracted_table_to_article_metadata(table, row_index=1)

        assert metadata is not None
        assert metadata.citation == "Lohr (1996)"
        assert metadata.year == 1996
        assert metadata.sample_size == 96

    def test_extracted_table_to_article_metadata_invalid_row(self):
        """Test with invalid row index."""
        table = ExtractedTable(
            table_id="TBL-001",
            page_number=1,
            table_type=TableType.STUDY_CHARACTERISTICS,
            headers=["Citation"],
            rows=[["Ulrich (1984)"]]
        )

        metadata = extracted_table_to_article_metadata(table, row_index=5)
        assert metadata is None

    def test_extracted_table_to_rct_facts(self):
        """Test converting table to RCT facts."""
        table = ExtractedTable(
            table_id="TBL-001",
            page_number=1,
            table_type=TableType.RESULTS,
            headers=["Citation", "N", "Intervention", "Control", "Outcome", "Effect Size", "95% CI", "p-value"],
            rows=[
                ["Ulrich (1984)", "46", "Tree view", "Brick wall", "Hospital stay", "0.74 (d)", "[0.28, 1.20]", "0.020"],
                ["Lohr (1996)", "96", "Plants", "No plants", "Stress", "0.52 (d)", "[0.11, 0.93]", "0.014"]
            ]
        )

        facts = extracted_table_to_rct_facts(table)

        assert len(facts) == 2

        # Check first fact
        fact1 = facts[0]
        assert fact1.citation == "Ulrich (1984)"
        assert fact1.sample_size == 46
        assert fact1.intervention == "Tree view"
        assert fact1.control == "Brick wall"
        assert fact1.outcome_measure == "Hospital stay"
        assert fact1.effect_size == 0.74
        assert fact1.effect_size_type == "d"
        assert fact1.ci_lower == 0.28
        assert fact1.ci_upper == 1.20
        assert fact1.p_value == 0.020

        # Check second fact
        fact2 = facts[1]
        assert fact2.citation == "Lohr (1996)"
        assert fact2.sample_size == 96

    def test_extracted_table_to_rct_facts_with_small_p(self):
        """Test handling of p < .001."""
        table = ExtractedTable(
            table_id="TBL-001",
            page_number=1,
            table_type=TableType.RESULTS,
            headers=["Citation", "p-value"],
            rows=[["Study A", "<.001"]]
        )

        facts = extracted_table_to_rct_facts(table)
        assert len(facts) == 1
        assert facts[0].p_value == 0.001

    def test_extracted_table_to_rct_facts_wrong_type(self):
        """Test with non-results table type."""
        table = ExtractedTable(
            table_id="TBL-001",
            page_number=1,
            table_type=TableType.DEMOGRAPHICS,
            headers=["Group", "Age"],
            rows=[["Treatment", "35.2"]]
        )

        facts = extracted_table_to_rct_facts(table)
        assert len(facts) == 0


class TestExtractionMethod:
    """Tests for ExtractionMethod enum."""

    def test_all_methods_defined(self):
        """Test all extraction methods exist."""
        assert ExtractionMethod.AI_API
        assert ExtractionMethod.PDFPLUMBER
        assert ExtractionMethod.HYBRID

    def test_method_values(self):
        """Test extraction method values."""
        assert ExtractionMethod.AI_API.value == "ai_api"
        assert ExtractionMethod.PDFPLUMBER.value == "pdfplumber"
        assert ExtractionMethod.HYBRID.value == "hybrid"


class TestAIExtractionPrompt:
    """Tests for AIExtractionPrompt dataclass."""

    def test_create_prompt(self):
        """Test creating extraction prompt."""
        prompt = AIExtractionPrompt(
            system_prompt="You are a helpful assistant.",
            extraction_prompt="Extract the table.",
            output_schema={"type": "object"},
            table_type=TableType.RESULTS
        )

        assert prompt.system_prompt == "You are a helpful assistant."
        assert prompt.extraction_prompt == "Extract the table."
        assert prompt.output_schema == {"type": "object"}
        assert prompt.table_type == TableType.RESULTS
        assert prompt.examples == []


class TestExtractedCell:
    """Tests for ExtractedCell dataclass."""

    def test_create_cell(self):
        """Test creating extracted cell."""
        cell = ExtractedCell(
            row=0,
            col=1,
            text="Sample text",
            is_header=True
        )

        assert cell.row == 0
        assert cell.col == 1
        assert cell.text == "Sample text"
        assert cell.is_header is True
        assert cell.spans_rows == 1
        assert cell.spans_cols == 1

    def test_cell_spanning(self):
        """Test cell with spanning."""
        cell = ExtractedCell(
            row=0,
            col=0,
            text="Merged cell",
            spans_rows=2,
            spans_cols=3
        )

        assert cell.spans_rows == 2
        assert cell.spans_cols == 3


class TestIntegrationWithExportEngine:
    """Integration tests with export engine types."""

    def test_full_pipeline_study_characteristics(self):
        """Test full pipeline from extraction to export engine types."""
        # Create a realistic extracted table
        table = ExtractedTable(
            table_id="TBL-20260208-001",
            page_number=3,
            table_type=TableType.STUDY_CHARACTERISTICS,
            title="Table 1. Study Characteristics",
            headers=["Citation", "Study Design", "Sample Size", "Population", "Setting", "Intervention"],
            rows=[
                ["Ulrich (1984)", "RCT", "46", "Post-cholecystectomy patients", "Suburban hospital", "Window view of trees"],
                ["Kaplan & Kaplan (1989)", "Observational", "200+", "General population", "Various", "Natural environments"],
                ["Lohr et al. (1996)", "RCT", "96", "University students", "Windowless lab", "Indoor plants"],
            ],
            confidence=0.85,
            extraction_method=ExtractionMethod.AI_API,
            caption="RCT = Randomized Controlled Trial"
        )

        # Convert each row to ArticleMetadata
        for i in range(len(table.rows)):
            metadata = extracted_table_to_article_metadata(table, i)
            assert metadata is not None
            assert metadata.citation in ["Ulrich (1984)", "Kaplan & Kaplan (1989)", "Lohr et al. (1996)"]

    def test_full_pipeline_results(self):
        """Test full pipeline for results table."""
        table = ExtractedTable(
            table_id="TBL-20260208-002",
            page_number=5,
            table_type=TableType.RESULTS,
            title="Table 2. Effect Sizes",
            headers=["Citation", "N", "Intervention", "Control", "Outcome", "Effect Size", "95% CI", "p-value"],
            rows=[
                ["Ulrich (1984)", "46", "Tree view", "Brick wall", "Hospital stay (days)", "0.74 (d)", "[0.28, 1.20]", "0.020"],
                ["Lohr (1996)", "96", "Plants present", "No plants", "Self-reported stress", "0.52 (d)", "[0.11, 0.93]", "0.014"],
            ],
            confidence=0.90,
            extraction_method=ExtractionMethod.AI_API
        )

        # Convert to RCT facts
        facts = extracted_table_to_rct_facts(table)

        assert len(facts) == 2

        # Verify markdown export works
        md = table.to_markdown()
        assert "Table 2. Effect Sizes" in md
        assert "Ulrich (1984)" in md
