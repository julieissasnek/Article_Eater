"""
Article Eater V23 — Table Extractor
Sprint 3.0 — 2026-02-08

Extracts tables from PDFs using AI/API as primary method.
Optional pdfplumber fallback for simple geometric tables.

Outputs structured ArticleMetadata and RCTStudyFact objects
compatible with the export engine generators.
"""

import json
import logging
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple

logger = logging.getLogger(__name__)


def _as_float(value: Any) -> Optional[float]:
    """Best-effort float coercion for LLM JSON fields."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if not text:
        return None
    text = text.replace(",", "")
    text = text.replace("−", "-")
    # Preserve leading sign and decimal only.
    m = re.search(r"[-+]?\d*\.?\d+", text)
    if not m:
        return None
    try:
        return float(m.group(0))
    except ValueError:
        return None


class ExtractionMethod(Enum):
    """Table extraction method."""
    AI_API = "ai_api"           # Primary: LLM-based extraction
    PDFPLUMBER = "pdfplumber"   # Fallback: geometric extraction
    HYBRID = "hybrid"           # Try AI first, fallback to pdfplumber


class TableType(Enum):
    """Types of tables we extract."""
    STUDY_CHARACTERISTICS = "study_characteristics"
    RESULTS = "results"
    DEMOGRAPHICS = "demographics"
    INTERVENTION = "intervention"
    OUTCOMES = "outcomes"
    QUALITY_ASSESSMENT = "quality_assessment"
    UNKNOWN = "unknown"


@dataclass
class ExtractedCell:
    """A single cell from an extracted table."""
    row: int
    col: int
    text: str
    is_header: bool = False
    spans_rows: int = 1
    spans_cols: int = 1


@dataclass
class ExtractedTable:
    """A table extracted from a PDF."""
    table_id: str
    page_number: int
    table_type: TableType
    title: Optional[str] = None
    caption: Optional[str] = None
    headers: List[str] = field(default_factory=list)
    rows: List[List[str]] = field(default_factory=list)
    raw_cells: List[ExtractedCell] = field(default_factory=list)
    confidence: float = 0.0
    extraction_method: ExtractionMethod = ExtractionMethod.AI_API
    source_file: Optional[str] = None
    extraction_notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "table_id": self.table_id,
            "page_number": self.page_number,
            "table_type": self.table_type.value,
            "title": self.title,
            "caption": self.caption,
            "headers": self.headers,
            "rows": self.rows,
            "confidence": self.confidence,
            "extraction_method": self.extraction_method.value,
            "source_file": self.source_file,
            "extraction_notes": self.extraction_notes
        }

    def to_markdown(self) -> str:
        """Convert table to markdown format."""
        if not self.headers and not self.rows:
            return ""

        lines = []
        if self.title:
            lines.append(f"### {self.title}")
            lines.append("")

        # Headers
        if self.headers:
            lines.append("| " + " | ".join(self.headers) + " |")
            lines.append("|" + "|".join(["---"] * len(self.headers)) + "|")

        # Rows
        for row in self.rows:
            # Pad row if needed
            padded = row + [""] * (len(self.headers) - len(row)) if self.headers else row
            lines.append("| " + " | ".join(str(cell) for cell in padded) + " |")

        if self.caption:
            lines.append("")
            lines.append(f"*{self.caption}*")

        return "\n".join(lines)


@dataclass
class AIExtractionPrompt:
    """Prompt configuration for AI-based table extraction."""
    system_prompt: str
    extraction_prompt: str
    output_schema: Dict[str, Any]
    table_type: TableType
    examples: List[Dict[str, Any]] = field(default_factory=list)


class TableExtractorBase(ABC):
    """Base class for table extractors."""

    @abstractmethod
    def extract_tables(
        self,
        pdf_path: Path,
        pages: Optional[List[int]] = None
    ) -> List[ExtractedTable]:
        """Extract all tables from a PDF."""
        pass

    @abstractmethod
    def extract_table_at(
        self,
        pdf_path: Path,
        page: int,
        region: Optional[Tuple[float, float, float, float]] = None
    ) -> Optional[ExtractedTable]:
        """Extract a specific table from a page."""
        pass


class AITableExtractor(TableExtractorBase):
    """
    AI/API-based table extractor.
    Uses LLM to understand and structure table content.
    """

    # Prompts for different table types
    EXTRACTION_PROMPTS = {
        TableType.STUDY_CHARACTERISTICS: AIExtractionPrompt(
            system_prompt="""You are a scientific research assistant specialized in extracting
structured data from research paper tables. Extract study characteristics accurately,
preserving all details about methodology, sample, and design.""",
            extraction_prompt="""Extract the study characteristics table from this content.
For each study/row, extract:
- Citation (author, year)
- Study type (RCT, quasi-experimental, observational, etc.)
- Sample size (N)
- Population description
- Setting (lab, field, hospital, etc.)
- Intervention/exposure
- Control condition
- Duration
- Country/location

Return as JSON with structure:
{
    "table_title": "string or null",
    "headers": ["list", "of", "column", "headers"],
    "studies": [
        {
            "citation": "Author (Year)",
            "study_type": "RCT",
            "sample_size": 46,
            "population": "description",
            "setting": "Hospital",
            "intervention": "description",
            "control": "description",
            "duration": "2 weeks",
            "country": "USA"
        }
    ]
}""",
            output_schema={
                "type": "object",
                "properties": {
                    "table_title": {"type": ["string", "null"]},
                    "headers": {"type": "array", "items": {"type": "string"}},
                    "studies": {"type": "array"}
                }
            },
            table_type=TableType.STUDY_CHARACTERISTICS
        ),

        TableType.RESULTS: AIExtractionPrompt(
            system_prompt="""You are a scientific research assistant specialized in extracting
statistical results from research paper tables. Extract effect sizes, confidence intervals,
and p-values accurately.""",
            extraction_prompt="""Extract the results table from this content.
For each result/row, extract:
- Study citation
- Outcome measure
- Effect size (with type: d, r, OR, RR, etc.)
- 95% CI (lower and upper bounds)
- p-value
- Sample size for this analysis
- Statistical test used
- Notes/comments

Return as JSON with structure:
{
    "table_title": "string or null",
    "headers": ["list", "of", "column", "headers"],
    "results": [
        {
            "citation": "Author (Year)",
            "outcome": "Stress reduction",
            "effect_size": 0.52,
            "effect_size_type": "d",
            "ci_lower": 0.11,
            "ci_upper": 0.93,
            "p_value": 0.014,
            "n": 96,
            "test": "t-test",
            "notes": "any additional notes"
        }
    ]
}""",
            output_schema={
                "type": "object",
                "properties": {
                    "table_title": {"type": ["string", "null"]},
                    "headers": {"type": "array", "items": {"type": "string"}},
                    "results": {"type": "array"}
                }
            },
            table_type=TableType.RESULTS
        ),

        TableType.QUALITY_ASSESSMENT: AIExtractionPrompt(
            system_prompt="""You are a scientific research assistant specialized in extracting
quality assessment and risk of bias data from research paper tables.""",
            extraction_prompt="""Extract the quality/risk of bias assessment table.
For each study, extract:
- Citation
- Overall quality rating (High/Moderate/Low or score)
- Assessment tool used (Cochrane RoB, GRADE, NOS, etc.)
- Individual domain ratings if available
- Notes/justification

Return as JSON with structure:
{
    "table_title": "string or null",
    "assessment_tool": "Cochrane Risk of Bias",
    "studies": [
        {
            "citation": "Author (Year)",
            "overall_rating": "Low risk",
            "domains": {
                "randomization": "Low",
                "blinding": "High",
                "attrition": "Low",
                "reporting": "Unclear"
            },
            "notes": "any justification"
        }
    ]
}""",
            output_schema={
                "type": "object",
                "properties": {
                    "table_title": {"type": ["string", "null"]},
                    "assessment_tool": {"type": "string"},
                    "studies": {"type": "array"}
                }
            },
            table_type=TableType.QUALITY_ASSESSMENT
        ),

        TableType.DEMOGRAPHICS: AIExtractionPrompt(
            system_prompt="""You are a scientific research assistant specialized in extracting
participant demographic data from research paper tables.""",
            extraction_prompt="""Extract the demographics/participant characteristics table.
For each group or study, extract:
- Group name or study citation
- Sample size
- Age (mean, SD, range)
- Gender distribution
- Other relevant demographics (education, ethnicity, health status, etc.)

Return as JSON with structure:
{
    "table_title": "string or null",
    "groups": [
        {
            "group_name": "Intervention" or "Study citation",
            "n": 48,
            "age_mean": 35.2,
            "age_sd": 8.4,
            "age_range": "22-55",
            "percent_female": 52.1,
            "other_demographics": {"education": "College+: 75%"}
        }
    ]
}""",
            output_schema={
                "type": "object",
                "properties": {
                    "table_title": {"type": ["string", "null"]},
                    "groups": {"type": "array"}
                }
            },
            table_type=TableType.DEMOGRAPHICS
        )
    }

    def __init__(
        self,
        api_client: Optional[Any] = None,
        model: str = "claude-3-haiku-20240307"
    ):
        """
        Initialize AI table extractor.

        Args:
            api_client: Anthropic API client (or compatible)
            model: Model to use for extraction
        """
        self.api_client = api_client
        self.model = model
        self._table_counter = 0

    def _generate_table_id(self) -> str:
        """Generate unique table ID."""
        self._table_counter += 1
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"TBL-{timestamp}-{self._table_counter:03d}"

    def extract_tables(
        self,
        pdf_path: Path,
        pages: Optional[List[int]] = None
    ) -> List[ExtractedTable]:
        """
        Extract all tables from a PDF using AI.

        Args:
            pdf_path: Path to PDF file
            pages: Specific pages to extract from (1-indexed), or None for all

        Returns:
            List of ExtractedTable objects
        """
        tables = []

        # First, get text/image content from PDF
        content = self._extract_pdf_content(pdf_path, pages)

        if not content:
            logger.warning(f"No content extracted from {pdf_path}")
            return tables

        # Detect tables in content
        detected = self._detect_tables_in_content(content)
        seen_fingerprints = set()

        for table_info in detected:
            extracted = self._extract_single_table(
                table_info["content"],
                table_info["page"],
                table_info.get("type_hint"),
                str(pdf_path)
            )
            if extracted:
                fingerprint = (
                    extracted.page_number,
                    tuple(h.strip().lower() for h in extracted.headers),
                    tuple(tuple(c.strip().lower() for c in row) for row in extracted.rows[:10]),
                )
                if fingerprint in seen_fingerprints:
                    continue
                seen_fingerprints.add(fingerprint)
                tables.append(extracted)

        return tables

    def extract_table_at(
        self,
        pdf_path: Path,
        page: int,
        region: Optional[Tuple[float, float, float, float]] = None
    ) -> Optional[ExtractedTable]:
        """Extract a specific table from a page."""
        content = self._extract_pdf_content(pdf_path, [page])
        if not content:
            return None

        # Extract from this specific content
        return self._extract_single_table(
            content[0] if content else "",
            page,
            source_file=str(pdf_path)
        )

    def _extract_pdf_content(
        self,
        pdf_path: Path,
        pages: Optional[List[int]] = None
    ) -> List[str]:
        """
        Extract text content from PDF pages.
        This is a simplified version - production would use proper PDF parsing.
        """
        content = []

        # Try pdfplumber for text extraction
        try:
            import pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                page_nums = pages if pages else range(1, len(pdf.pages) + 1)
                for page_num in page_nums:
                    if 1 <= page_num <= len(pdf.pages):
                        page = pdf.pages[page_num - 1]
                        text = page.extract_text() or ""
                        content.append(text)
        except ImportError:
            logger.warning("pdfplumber not installed, using fallback")
            # Fallback: try PyPDF2 or return empty
            try:
                import PyPDF2
                with open(pdf_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    page_nums = pages if pages else range(1, len(reader.pages) + 1)
                    for page_num in page_nums:
                        if 1 <= page_num <= len(reader.pages):
                            page = reader.pages[page_num - 1]
                            text = page.extract_text() or ""
                            content.append(text)
            except ImportError:
                logger.error("No PDF library available (pdfplumber or PyPDF2)")
                return []
        except Exception as e:
            logger.error(f"Error extracting PDF content: {e}")
            return []

        return content

    def _detect_tables_in_content(
        self,
        content: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Detect likely table regions in extracted content.
        Uses heuristics to identify table-like structures.
        """
        detected = []

        for page_num, page_content in enumerate(content, 1):
            seen_match_bins = set()
            # Look for table indicators
            table_patterns = [
                r"Table\s*\d+[.:]\s*(.+?)(?=\n|$)",  # Table 1: Title OR Table1: Title
                r"\bTable\s*\d+\b",  # Just "Table 1" OR "Table1"
                r"\bTable\s*[IVXLC]+\b",  # Roman numeral tables (e.g., Table IV)
                r"(?:Study|Author|Citation)\s*\|",  # Markdown-like tables
                r"^\s*\w+\s+\w+\s+\w+\s*\n\s*[-=]+",  # Underlined headers
            ]

            for pattern in table_patterns:
                matches = re.finditer(pattern, page_content, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    match_bin = match.start() // 40
                    if match_bin in seen_match_bins:
                        continue
                    seen_match_bins.add(match_bin)
                    # Extract surrounding context (table content)
                    start = max(0, match.start() - 100)
                    end = min(len(page_content), match.end() + 2000)
                    table_content = page_content[start:end]

                    # Guess table type from content
                    type_hint = self._guess_table_type(table_content)

                    detected.append({
                        "page": page_num,
                        "content": table_content,
                        "type_hint": type_hint,
                        "match": match.group()
                    })

            # Also check for tabular data without explicit "Table" label
            if self._looks_like_table(page_content) and not detected:
                detected.append({
                    "page": page_num,
                    "content": page_content,
                    "type_hint": TableType.UNKNOWN,
                    "match": "Tabular data"
                })

        return detected

    def _looks_like_table(self, content: str) -> bool:
        """Check if content looks like tabular data."""
        lines = content.strip().split('\n')
        if len(lines) < 3:
            return False

        # Check for consistent column-like structure
        # (lines with similar spacing patterns)
        column_counts = []
        for line in lines[:10]:  # Check first 10 lines
            # Count potential columns (separated by 2+ spaces or tabs)
            cols = len(re.split(r'\s{2,}|\t', line.strip()))
            if cols > 1:
                column_counts.append(cols)

        if not column_counts:
            return False

        # If most lines have similar column counts, likely a table
        from collections import Counter
        most_common = Counter(column_counts).most_common(1)
        if most_common and most_common[0][1] >= len(column_counts) * 0.5:
            return True

        return False

    def _guess_table_type(self, content: str) -> TableType:
        """Guess table type from content keywords."""
        content_lower = content.lower()

        type_keywords = {
            TableType.STUDY_CHARACTERISTICS: [
                "study design", "sample size", "population", "intervention",
                "setting", "participants", "methods", "n ="
            ],
            TableType.RESULTS: [
                "effect size", "p-value", "p value", "confidence interval",
                "ci", "mean difference", "odds ratio", "significant",
                "95%", "cohen"
            ],
            TableType.QUALITY_ASSESSMENT: [
                "risk of bias", "quality", "cochrane", "grade", "nos",
                "assessment", "low risk", "high risk", "unclear"
            ],
            TableType.DEMOGRAPHICS: [
                "age", "gender", "sex", "female", "male", "education",
                "baseline characteristics", "demographic"
            ]
        }

        scores = {}
        for table_type, keywords in type_keywords.items():
            score = sum(1 for kw in keywords if kw in content_lower)
            scores[table_type] = score

        best_type = max(scores, key=scores.get)
        if scores[best_type] >= 2:
            return best_type

        return TableType.UNKNOWN

    def _extract_single_table(
        self,
        content: str,
        page: int,
        type_hint: Optional[TableType] = None,
        source_file: Optional[str] = None
    ) -> Optional[ExtractedTable]:
        """
        Extract a single table using AI.

        If no API client is available, falls back to rule-based extraction.
        """
        table_type = type_hint or TableType.UNKNOWN

        # Try AI extraction if client available
        if self.api_client:
            try:
                return self._ai_extract_table(content, page, table_type, source_file)
            except Exception as e:
                logger.warning(f"AI extraction failed: {e}, trying fallback")

        # Fallback to rule-based extraction
        return self._rule_based_extract(content, page, table_type, source_file)

    def _ai_extract_table(
        self,
        content: str,
        page: int,
        table_type: TableType,
        source_file: Optional[str] = None
    ) -> Optional[ExtractedTable]:
        """Extract table using AI API."""
        prompt_config = self.EXTRACTION_PROMPTS.get(
            table_type,
            self.EXTRACTION_PROMPTS[TableType.STUDY_CHARACTERISTICS]
        )

        # Build the prompt
        full_prompt = f"""{prompt_config.extraction_prompt}

Content to extract from:
---
{content}
---

Return only valid JSON, no other text."""

        try:
            # Call API (assuming Anthropic-compatible client)
            response = self.api_client.messages.create(
                model=self.model,
                max_tokens=4000,
                system=prompt_config.system_prompt,
                messages=[{"role": "user", "content": full_prompt}]
            )

            # Parse response
            response_text = response.content[0].text
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return self._parse_ai_response(data, page, table_type, source_file)

        except Exception as e:
            logger.error(f"AI extraction error: {e}")
            raise

        return None

    def _parse_ai_response(
        self,
        data: Dict[str, Any],
        page: int,
        table_type: TableType,
        source_file: Optional[str] = None
    ) -> ExtractedTable:
        """Parse AI response into ExtractedTable."""
        headers = data.get("headers", [])
        rows = []

        # Convert structured data to rows based on table type
        if table_type == TableType.STUDY_CHARACTERISTICS:
            studies = data.get("studies", [])
            if not headers:
                headers = ["Citation", "Type", "N", "Population", "Setting", "Intervention"]
            for study in studies:
                rows.append([
                    study.get("citation", ""),
                    study.get("study_type", ""),
                    str(study.get("sample_size", "")),
                    study.get("population", ""),
                    study.get("setting", ""),
                    study.get("intervention", "")
                ])

        elif table_type == TableType.RESULTS:
            results = data.get("results", [])
            if not headers:
                headers = ["Citation", "Outcome", "Effect Size", "95% CI", "p-value"]
            for result in results:
                ci = ""
                ci_lower = _as_float(result.get("ci_lower"))
                ci_upper = _as_float(result.get("ci_upper"))
                if ci_lower is not None and ci_upper is not None:
                    ci = f"[{ci_lower:.2f}, {ci_upper:.2f}]"
                es = ""
                effect_size = _as_float(result.get("effect_size"))
                if effect_size is not None:
                    es_type = result.get("effect_size_type", "d")
                    es = f"{effect_size:.2f} ({es_type})"
                p = ""
                p_value = _as_float(result.get("p_value"))
                if p_value is not None:
                    p = f"{p_value:.3f}" if p_value >= 0.001 else "<.001"

                rows.append([
                    result.get("citation", ""),
                    result.get("outcome", ""),
                    es,
                    ci,
                    p
                ])

        elif table_type == TableType.QUALITY_ASSESSMENT:
            studies = data.get("studies", [])
            if not headers:
                headers = ["Citation", "Overall Rating", "Notes"]
            for study in studies:
                rows.append([
                    study.get("citation", ""),
                    study.get("overall_rating", ""),
                    study.get("notes", "")
                ])

        elif table_type == TableType.DEMOGRAPHICS:
            groups = data.get("groups", [])
            if not headers:
                headers = ["Group", "N", "Age (M±SD)", "% Female"]
            for group in groups:
                age = ""
                age_mean = _as_float(group.get("age_mean"))
                if age_mean is not None:
                    sd = _as_float(group.get("age_sd"))
                    age = f"{age_mean:.1f}" + (f" ± {sd:.1f}" if sd is not None else "")

                rows.append([
                    group.get("group_name", ""),
                    str(group.get("n", "")),
                    age,
                    f"{group.get('percent_female', '')}"
                ])

        return ExtractedTable(
            table_id=self._generate_table_id(),
            page_number=page,
            table_type=table_type,
            title=data.get("table_title"),
            headers=headers,
            rows=rows,
            confidence=0.85,  # AI extraction typically high confidence
            extraction_method=ExtractionMethod.AI_API,
            source_file=source_file
        )

    def _rule_based_extract(
        self,
        content: str,
        page: int,
        table_type: TableType,
        source_file: Optional[str] = None
    ) -> Optional[ExtractedTable]:
        """
        Fallback rule-based extraction when AI is not available.
        Uses regex and heuristics to parse table structure.
        """
        lines = [ln.strip() for ln in content.strip().split('\n') if ln.strip()]
        if len(lines) < 2:
            return None

        parsed_rows: List[List[str]] = []
        seen_row_keys = set()
        for line in lines:
            # Skip table caption lines to avoid polluting row extraction.
            if re.match(r"^\s*table\s*[0-9ivxlc]+\b", line, flags=re.IGNORECASE):
                continue

            if "|" in line:
                parts = [p.strip() for p in line.split("|") if p.strip()]
            elif re.search(r"\t|\s{2,}", line):
                parts = [p.strip() for p in re.split(r"\t|\s{2,}", line) if p.strip()]
            else:
                # Fallback for compacted PDF text where columns collapse to single spaces.
                m = re.match(r"^(.+?)\s+([-+]?\d[\d\.\,\-%\(\)]*(?:\s+.+)?)$", line)
                parts = [m.group(1).strip(), m.group(2).strip()] if m else []

            if len(parts) >= 2:
                # Keep compact table-like rows, reject long prose fragments.
                if len(line) > 140:
                    continue
                if sum(len(p.split()) for p in parts) > 18:
                    continue
                if any(len(p) > 80 for p in parts):
                    continue
                if len(parts[0].split()) > 10:
                    continue
                if len(parts[1].split()) > 10:
                    continue
                joined = " ".join(parts).lower()
                if re.search(r"\b(vol\.?|no\.?|copyright|issn|doi|page)\b", joined):
                    continue
                if "see table" in joined:
                    continue
                row_key = tuple(p.strip().lower() for p in parts)
                if row_key in seen_row_keys:
                    continue
                seen_row_keys.add(row_key)
                parsed_rows.append(parts[:8])
                if len(parsed_rows) >= 25:
                    break

        if not parsed_rows:
            return None

        max_cols = max(len(r) for r in parsed_rows)
        has_header = False
        first_row = parsed_rows[0]
        if first_row and not any(re.search(r"\d", cell) for cell in first_row):
            has_header = True

        if has_header:
            headers = first_row + [f"col_{i}" for i in range(len(first_row) + 1, max_cols + 1)]
            data_rows = parsed_rows[1:]
        else:
            headers = [f"col_{i}" for i in range(1, max_cols + 1)]
            data_rows = parsed_rows

        rows = []
        for row in data_rows:
            if not any(c.strip() for c in row):
                continue
            if not any(re.search(r"\d", c) for c in row):
                continue
            rows.append(row + [""] * (max_cols - len(row)))
        if not rows:
            return None

        return ExtractedTable(
            table_id=self._generate_table_id(),
            page_number=page,
            table_type=table_type,
            headers=headers,
            rows=rows,
            confidence=0.5,  # Lower confidence for rule-based
            extraction_method=ExtractionMethod.PDFPLUMBER,  # Actually rule-based
            source_file=source_file,
            extraction_notes=["Extracted using rule-based fallback"]
        )


class PdfPlumberTableExtractor(TableExtractorBase):
    """
    Geometric table extraction using pdfplumber.
    Better for well-formatted PDF tables with clear borders.
    """

    def __init__(self):
        self._table_counter = 0
        try:
            import pdfplumber
            self.pdfplumber = pdfplumber
        except ImportError:
            self.pdfplumber = None
            logger.warning("pdfplumber not installed. Install with: pip install pdfplumber")

    def _generate_table_id(self) -> str:
        self._table_counter += 1
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"TBL-{timestamp}-{self._table_counter:03d}"

    def extract_tables(
        self,
        pdf_path: Path,
        pages: Optional[List[int]] = None
    ) -> List[ExtractedTable]:
        """Extract tables using pdfplumber's geometric detection."""
        if not self.pdfplumber:
            logger.error("pdfplumber not available")
            return []

        tables = []

        try:
            with self.pdfplumber.open(pdf_path) as pdf:
                page_nums = pages if pages else range(1, len(pdf.pages) + 1)

                for page_num in page_nums:
                    if page_num < 1 or page_num > len(pdf.pages):
                        continue

                    page = pdf.pages[page_num - 1]
                    page_tables = page.extract_tables()

                    for tbl_idx, tbl in enumerate(page_tables):
                        if not tbl or len(tbl) < 2:
                            continue

                        # First row is typically headers
                        headers = [str(cell or "") for cell in tbl[0]]
                        rows = []
                        for row in tbl[1:]:
                            rows.append([str(cell or "") for cell in row])

                        # Skip degenerate tables where cells are effectively empty.
                        if not any(cell.strip() for cell in headers + [c for r in rows for c in r]):
                            continue

                        # Guess table type from content
                        all_content = " ".join(headers + [c for r in rows for c in r])
                        table_type = self._guess_type_from_content(all_content)

                        extracted = ExtractedTable(
                            table_id=self._generate_table_id(),
                            page_number=page_num,
                            table_type=table_type,
                            headers=headers,
                            rows=rows,
                            confidence=0.75,
                            extraction_method=ExtractionMethod.PDFPLUMBER,
                            source_file=str(pdf_path)
                        )
                        tables.append(extracted)

        except Exception as e:
            logger.error(f"pdfplumber extraction error: {e}")

        # Fallback to text heuristics when geometric detection fails.
        if not tables:
            heuristic = AITableExtractor(api_client=None)
            tables = heuristic.extract_tables(pdf_path, pages)

        return tables

    def extract_table_at(
        self,
        pdf_path: Path,
        page: int,
        region: Optional[Tuple[float, float, float, float]] = None
    ) -> Optional[ExtractedTable]:
        """Extract table from specific page/region."""
        tables = self.extract_tables(pdf_path, [page])
        return tables[0] if tables else None

    def _guess_type_from_content(self, content: str) -> TableType:
        """Guess table type from cell content."""
        content_lower = content.lower()

        if any(kw in content_lower for kw in ["effect size", "p-value", "ci", "odds ratio"]):
            return TableType.RESULTS
        if any(kw in content_lower for kw in ["risk of bias", "quality", "assessment"]):
            return TableType.QUALITY_ASSESSMENT
        if any(kw in content_lower for kw in ["age", "gender", "female", "male", "demographic"]):
            return TableType.DEMOGRAPHICS
        if any(kw in content_lower for kw in ["intervention", "control", "study design"]):
            return TableType.STUDY_CHARACTERISTICS

        return TableType.UNKNOWN


class HybridTableExtractor:
    """
    Combines AI and pdfplumber extraction.
    Uses pdfplumber for geometric detection, AI for semantic understanding.
    """

    def __init__(self, api_client: Optional[Any] = None, model: str = "claude-3-haiku-20240307"):
        self.ai_extractor = AITableExtractor(api_client, model)
        self.plumber_extractor = PdfPlumberTableExtractor()

    def extract_tables(
        self,
        pdf_path: Path,
        pages: Optional[List[int]] = None,
        prefer_ai: bool = True
    ) -> List[ExtractedTable]:
        """
        Extract tables using hybrid approach.

        Args:
            pdf_path: Path to PDF
            pages: Specific pages to extract
            prefer_ai: If True, try AI first; if False, try pdfplumber first
        """
        if prefer_ai:
            tables = self.ai_extractor.extract_tables(pdf_path, pages)
            if not tables:
                tables = self.plumber_extractor.extract_tables(pdf_path, pages)
        else:
            tables = self.plumber_extractor.extract_tables(pdf_path, pages)
            # Enhance with AI if available
            if self.ai_extractor.api_client:
                tables = self._enhance_with_ai(tables, pdf_path)

        return tables

    def _enhance_with_ai(
        self,
        tables: List[ExtractedTable],
        pdf_path: Path
    ) -> List[ExtractedTable]:
        """Enhance pdfplumber tables with AI semantic understanding."""
        enhanced = []
        for table in tables:
            # Use AI to better classify and structure
            content = table.to_markdown()
            try:
                ai_table = self.ai_extractor._extract_single_table(
                    content,
                    table.page_number,
                    table.table_type,
                    str(pdf_path)
                )
                if ai_table and ai_table.confidence > table.confidence:
                    ai_table.extraction_method = ExtractionMethod.HYBRID
                    enhanced.append(ai_table)
                else:
                    enhanced.append(table)
            except Exception:
                enhanced.append(table)

        return enhanced


# Convenience factory function
def get_table_extractor(
    method: ExtractionMethod = ExtractionMethod.AI_API,
    api_client: Optional[Any] = None,
    model: str = "claude-3-haiku-20240307"
) -> Union[AITableExtractor, PdfPlumberTableExtractor, HybridTableExtractor]:
    """
    Factory function to get appropriate table extractor.

    Args:
        method: Extraction method to use
        api_client: API client for AI extraction
        model: Model name for AI extraction

    Returns:
        Appropriate extractor instance
    """
    if method == ExtractionMethod.AI_API:
        return AITableExtractor(api_client, model)
    elif method == ExtractionMethod.PDFPLUMBER:
        return PdfPlumberTableExtractor()
    else:  # HYBRID
        return HybridTableExtractor(api_client, model)


# Conversion functions to export engine types
def extracted_table_to_article_metadata(
    table: ExtractedTable,
    row_index: int = 0
) -> Optional["ArticleMetadata"]:
    """
    Convert an extracted table row to ArticleMetadata.
    Imports ArticleMetadata from export_engine to avoid circular imports.
    """
    try:
        from src.services.export_engine import ArticleMetadata
    except ImportError:
        from export_engine import ArticleMetadata

    if row_index >= len(table.rows):
        return None

    row = table.rows[row_index]
    headers_lower = [h.lower() for h in table.headers]

    def get_value(keys: List[str], exact_match: bool = False) -> Optional[str]:
        """Get value from row by header key."""
        for key in keys:
            for i, h in enumerate(headers_lower):
                if i >= len(row):
                    continue
                if exact_match:
                    # Match exact header or header equals "key" with optional suffix
                    if h == key or h.startswith(key + " ") or h.startswith(key + "="):
                        return row[i]
                else:
                    # Standard substring match, but require word boundary for short keys
                    if len(key) <= 2:
                        # For short keys like "n", require exact match or word boundary
                        if h == key or re.search(rf'\b{re.escape(key)}\b', h):
                            return row[i]
                    elif key in h:
                        return row[i]
        return None

    # Parse citation for author/year
    citation = get_value(["citation", "study", "author"]) or ""
    year_match = re.search(r'\((\d{4})\)', citation)
    year = int(year_match.group(1)) if year_match else 0

    # Parse sample size - look for "N" or "sample size" columns specifically
    n_str = get_value(["sample size", "sample_size", "samplesize"]) or ""
    if not n_str:
        # Try exact match for "n" header
        for i, h in enumerate(headers_lower):
            if h == "n" and i < len(row):
                n_str = row[i]
                break
    n_match = re.search(r'\d+', n_str)
    sample_size = int(n_match.group()) if n_match else None

    return ArticleMetadata(
        article_id=f"{table.table_id}-R{row_index}",
        citation=citation,
        title=citation,  # Would need separate lookup
        authors=[citation.split("(")[0].strip()] if citation else [],
        year=year,
        study_type=get_value(["type", "design"]) or "Unknown",
        sample_size=sample_size,
        population=get_value(["population", "participants"]) or "Not specified",
        intervention=get_value(["intervention", "treatment"]),
        setting=get_value(["setting"]) or "Not specified"
    )


def extracted_table_to_rct_facts(
    table: ExtractedTable
) -> List["RCTStudyFact"]:
    """
    Convert an extracted results table to RCTStudyFact objects.
    """
    try:
        from src.services.export_engine import RCTStudyFact
    except ImportError:
        from export_engine import RCTStudyFact

    facts = []

    if table.table_type not in [TableType.RESULTS, TableType.STUDY_CHARACTERISTICS]:
        return facts

    headers_lower = [h.lower() for h in table.headers]

    def get_idx(keys: List[str], exact_short: bool = False) -> int:
        """Get column index by header key.

        Args:
            keys: List of keys to search for
            exact_short: If True, short keys (<=2 chars) require exact match
        """
        for key in keys:
            for i, h in enumerate(headers_lower):
                if len(key) <= 2 or exact_short:
                    # For short keys, require exact match or word boundary
                    if h == key or re.search(rf'\b{re.escape(key)}\b', h):
                        return i
                elif key in h:
                    return i
        return -1

    citation_idx = get_idx(["citation", "study", "author"])
    # For sample size, first try exact "n", then "sample"
    n_idx = -1
    for i, h in enumerate(headers_lower):
        if h == "n":
            n_idx = i
            break
    if n_idx == -1:
        n_idx = get_idx(["sample size", "sample_size", "sample"])
    intervention_idx = get_idx(["intervention", "treatment"])
    control_idx = get_idx(["control", "comparator"])
    outcome_idx = get_idx(["outcome", "measure"])
    es_idx = get_idx(["effect", "size", "cohen"])
    ci_idx = get_idx(["ci", "confidence", "interval"])
    p_idx = get_idx(["p-value", "p value", "significance"])

    for row_idx, row in enumerate(table.rows):
        def safe_get(idx: int) -> str:
            return row[idx] if 0 <= idx < len(row) else ""

        # Parse effect size
        es_str = safe_get(es_idx)
        es_match = re.search(r'(-?\d+\.?\d*)', es_str)
        effect_size = float(es_match.group(1)) if es_match else None

        es_type = "d"
        if "r" in es_str.lower():
            es_type = "r"
        elif "or" in es_str.lower():
            es_type = "OR"

        # Parse CI
        ci_str = safe_get(ci_idx)
        ci_match = re.search(r'\[?\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*\]?', ci_str)
        ci_lower = float(ci_match.group(1)) if ci_match else None
        ci_upper = float(ci_match.group(2)) if ci_match else None

        # Parse p-value
        p_str = safe_get(p_idx)
        if "<" in p_str:
            p_value = 0.001
        else:
            p_match = re.search(r'(\d+\.?\d*)', p_str)
            p_value = float(p_match.group(1)) if p_match else None

        # Parse N
        n_str = safe_get(n_idx)
        n_match = re.search(r'\d+', n_str)
        sample_size = int(n_match.group()) if n_match else None

        fact = RCTStudyFact(
            study_id=f"{table.table_id}-R{row_idx}",
            citation=safe_get(citation_idx),
            sample_size=sample_size,
            intervention=safe_get(intervention_idx) or None,
            control=safe_get(control_idx) or None,
            outcome_measure=safe_get(outcome_idx) or None,
            effect_size=effect_size,
            effect_size_type=es_type,
            ci_lower=ci_lower,
            ci_upper=ci_upper,
            p_value=p_value
        )
        facts.append(fact)

    return facts
