"""
BibTeX utilities for Article Finder / Article Eater integration.

Sprint BIB-2: Parse BibTeX files, extract metadata, match to PDFs, convert to paper.json format.

This module provides:
1. BibTeX parsing (no external dependencies)
2. Field extraction and normalization
3. Title/DOI-based matching for linking PDFs to BibTeX entries
4. Conversion to AE paper.json format

Created: 2026-02-08
"""

from __future__ import annotations

import hashlib
import re
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import json


# =============================================================================
# BIBTEX ENTRY DATA CLASS
# =============================================================================


@dataclass
class BibTeXEntry:
    """Represents a single BibTeX entry with normalized fields."""

    entry_type: str  # article, book, inproceedings, etc.
    cite_key: str  # The citation key (e.g., "smith2023attention")

    # Core fields
    title: Optional[str] = None
    author: Optional[str] = None  # Raw author string
    authors: List[str] = field(default_factory=list)  # Parsed author list
    year: Optional[int] = None
    publication_date: Optional[str] = None  # YYYY-MM-DD when available
    abstract: Optional[str] = None
    doi: Optional[str] = None

    # Publication info
    journal: Optional[str] = None
    booktitle: Optional[str] = None  # For conference papers
    volume: Optional[str] = None
    number: Optional[str] = None  # Issue number
    pages: Optional[str] = None
    publisher: Optional[str] = None

    # Identifiers
    isbn: Optional[str] = None
    issn: Optional[str] = None
    url: Optional[str] = None
    eprint: Optional[str] = None  # arXiv ID

    # File reference (Zotero often includes this)
    file: Optional[str] = None

    # Keywords/tags
    keywords: List[str] = field(default_factory=list)

    # Raw fields dict for anything else
    raw_fields: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "entry_type": self.entry_type,
            "cite_key": self.cite_key,
            "title": self.title,
            "author": self.author,
            "authors": self.authors,
            "year": self.year,
            "publication_date": self.publication_date,
            "abstract": self.abstract,
            "doi": self.doi,
            "journal": self.journal,
            "booktitle": self.booktitle,
            "volume": self.volume,
            "number": self.number,
            "pages": self.pages,
            "publisher": self.publisher,
            "isbn": self.isbn,
            "issn": self.issn,
            "url": self.url,
            "eprint": self.eprint,
            "file": self.file,
            "keywords": self.keywords,
        }

    def to_paper_json(self, paper_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Convert to AE paper.json format.

        Args:
            paper_id: Optional paper ID. If not provided, generated from cite_key.

        Returns:
            Dictionary matching the AE paper.json schema.
        """
        if paper_id is None:
            paper_id = self.cite_key or f"paper_{hashlib.md5((self.title or '').encode()).hexdigest()[:8]}"

        # Build author string for display
        author_str = ", ".join(self.authors) if self.authors else self.author

        # Determine publication venue
        venue = self.journal or self.booktitle or self.publisher

        return {
            "schema": "ae.paper.v1",
            "paper_id": paper_id,
            "title": self.title,
            "authors": self.authors,
            "author_string": author_str,
            "year": self.year,
            "publication_date": self.publication_date,
            "abstract": self.abstract,
            "doi": self.doi,
            "venue": venue,
            "journal": self.journal,
            "volume": self.volume,
            "issue": self.number,
            "pages": self.pages,
            "url": self.url or (f"https://doi.org/{self.doi}" if self.doi else None),
            "arxiv_id": self.eprint,
            "keywords": self.keywords,
            "bibtex_source": {
                "cite_key": self.cite_key,
                "entry_type": self.entry_type,
            },
            "metadata_complete": self._metadata_completeness(),
        }

    def _metadata_completeness(self) -> Dict[str, bool]:
        """Check which key metadata fields are present."""
        return {
            "has_title": bool(self.title),
            "has_authors": bool(self.authors or self.author),
            "has_year": self.year is not None,
            "has_abstract": bool(self.abstract),
            "has_doi": bool(self.doi),
            "has_venue": bool(self.journal or self.booktitle),
        }

    @property
    def normalized_title(self) -> str:
        """Get normalized title for matching."""
        return normalize_text(self.title or "")

    @property
    def first_author_lastname(self) -> Optional[str]:
        """Get first author's last name for matching."""
        if self.authors:
            # Assume "Last, First" or "First Last" format
            first = self.authors[0]
            if "," in first:
                return first.split(",")[0].strip().lower()
            else:
                parts = first.split()
                return parts[-1].lower() if parts else None
        elif self.author:
            # Parse from raw author string
            first_author = self.author.split(" and ")[0].strip()
            if "," in first_author:
                return first_author.split(",")[0].strip().lower()
            else:
                parts = first_author.split()
                return parts[-1].lower() if parts else None
        return None


# =============================================================================
# BIBTEX PARSER
# =============================================================================


class BibTeXParser:
    """
    Lightweight BibTeX parser with no external dependencies.

    Handles:
    - Standard BibTeX entry types (@article, @book, @inproceedings, etc.)
    - Nested braces in field values
    - String concatenation with #
    - @string definitions
    - LaTeX special characters (basic conversion)
    """

    def __init__(self):
        self.strings: Dict[str, str] = {}  # @string definitions
        self.entries: List[BibTeXEntry] = []

    def parse(self, content: str) -> List[BibTeXEntry]:
        """
        Parse BibTeX content and return list of entries.

        Args:
            content: Raw BibTeX file content

        Returns:
            List of BibTeXEntry objects
        """
        self.strings = {}
        self.entries = []

        # Remove comments (lines starting with %)
        lines = []
        for line in content.split("\n"):
            stripped = line.lstrip()
            if not stripped.startswith("%"):
                lines.append(line)
        content = "\n".join(lines)

        # Find all entries
        pattern = r'@(\w+)\s*\{([^,]*),(.+?)\n\s*\}'

        # More robust: find @ followed by type, then match braces
        pos = 0
        while pos < len(content):
            # Find next @
            at_pos = content.find("@", pos)
            if at_pos == -1:
                break

            # Extract entry type
            match = re.match(r'@(\w+)\s*\{', content[at_pos:])
            if not match:
                pos = at_pos + 1
                continue

            entry_type = match.group(1).lower()
            brace_start = at_pos + match.end() - 1  # Position of opening brace

            # Find matching closing brace
            brace_end = self._find_matching_brace(content, brace_start)
            if brace_end == -1:
                pos = at_pos + 1
                continue

            entry_content = content[brace_start + 1:brace_end]

            if entry_type == "string":
                self._parse_string_def(entry_content)
            elif entry_type in ("comment", "preamble"):
                pass  # Skip these
            else:
                entry = self._parse_entry(entry_type, entry_content)
                if entry:
                    self.entries.append(entry)

            pos = brace_end + 1

        return self.entries

    def parse_file(self, path: Path) -> List[BibTeXEntry]:
        """Parse a BibTeX file."""
        content = path.read_text(encoding="utf-8", errors="replace")
        return self.parse(content)

    def _find_matching_brace(self, content: str, start: int) -> int:
        """Find the position of the matching closing brace."""
        if content[start] != "{":
            return -1

        depth = 1
        pos = start + 1
        in_quotes = False

        while pos < len(content) and depth > 0:
            char = content[pos]

            if char == '"' and (pos == 0 or content[pos - 1] != "\\"):
                in_quotes = not in_quotes
            elif not in_quotes:
                if char == "{":
                    depth += 1
                elif char == "}":
                    depth -= 1

            pos += 1

        return pos - 1 if depth == 0 else -1

    def _parse_string_def(self, content: str) -> None:
        """Parse @string{name = "value"} definition."""
        match = re.match(r'\s*(\w+)\s*=\s*(.+)', content.strip())
        if match:
            name = match.group(1).lower()
            value = self._parse_field_value(match.group(2).strip())
            self.strings[name] = value

    def _parse_entry(self, entry_type: str, content: str) -> Optional[BibTeXEntry]:
        """Parse a single BibTeX entry."""
        # First item before comma is the cite key
        comma_pos = content.find(",")
        if comma_pos == -1:
            return None

        cite_key = content[:comma_pos].strip()
        fields_str = content[comma_pos + 1:]

        # Parse fields
        fields = self._parse_fields(fields_str)

        # Create entry
        entry = BibTeXEntry(
            entry_type=entry_type,
            cite_key=cite_key,
            raw_fields=fields,
        )

        # Map common fields
        entry.title = self._clean_latex(fields.get("title"))
        entry.author = fields.get("author")
        entry.abstract = self._clean_latex(fields.get("abstract"))
        entry.doi = self._clean_doi(fields.get("doi"))
        entry.journal = self._clean_latex(fields.get("journal"))
        entry.booktitle = self._clean_latex(fields.get("booktitle"))
        entry.volume = fields.get("volume")
        entry.number = fields.get("number") or fields.get("issue")
        entry.pages = fields.get("pages")
        entry.publisher = self._clean_latex(fields.get("publisher"))
        entry.isbn = fields.get("isbn")
        entry.issn = fields.get("issn")
        entry.url = fields.get("url")
        entry.eprint = fields.get("eprint") or fields.get("arxivid")
        entry.file = fields.get("file")

        # Parse year
        year_str = fields.get("year")
        if year_str:
            try:
                entry.year = int(re.sub(r'\D', '', year_str)[:4])
            except ValueError:
                pass

        # Parse publication date (optional)
        entry.publication_date = self._parse_publication_date(fields, entry.year)

        # Parse authors
        if entry.author:
            entry.authors = self._parse_authors(entry.author)

        # Parse keywords
        keywords_str = fields.get("keywords") or fields.get("tags")
        if keywords_str:
            entry.keywords = [k.strip() for k in re.split(r'[,;]', keywords_str) if k.strip()]

        return entry

    def _parse_publication_date(
        self,
        fields: Dict[str, str],
        year: Optional[int]
    ) -> Optional[str]:
        """Parse publication date as YYYY-MM-DD when available."""
        date_str = fields.get("date")
        if date_str:
            cleaned = self._clean_latex(date_str).strip()
            for fmt in (
                "%Y-%m-%d",
                "%Y/%m/%d",
                "%Y.%m.%d",
                "%d-%m-%Y",
                "%d/%m/%Y",
                "%d.%m.%Y",
                "%Y %b %d",
                "%Y %B %d",
                "%d %b %Y",
                "%d %B %Y",
            ):
                try:
                    parsed = datetime.strptime(cleaned, fmt)
                    return parsed.date().isoformat()
                except ValueError:
                    continue

        month_str = fields.get("month")
        day_str = fields.get("day")
        if year and month_str and day_str:
            month_num = self._parse_month(month_str)
            try:
                day_num = int(re.sub(r"\D", "", day_str)[:2])
            except ValueError:
                day_num = 0
            if month_num and day_num:
                try:
                    parsed = datetime(year, month_num, day_num)
                    return parsed.date().isoformat()
                except ValueError:
                    return None

        return None

    def _parse_month(self, month_str: str) -> Optional[int]:
        """Parse BibTeX month field to a numeric value."""
        if not month_str:
            return None
        normalized = self._clean_latex(month_str).strip().lower()
        normalized = re.sub(r"[{}\s\.]", "", normalized)

        if normalized.isdigit():
            val = int(normalized)
            if 1 <= val <= 12:
                return val
            return None

        month_map = {
            "jan": 1,
            "january": 1,
            "feb": 2,
            "february": 2,
            "mar": 3,
            "march": 3,
            "apr": 4,
            "april": 4,
            "may": 5,
            "jun": 6,
            "june": 6,
            "jul": 7,
            "july": 7,
            "aug": 8,
            "august": 8,
            "sep": 9,
            "sept": 9,
            "september": 9,
            "oct": 10,
            "october": 10,
            "nov": 11,
            "november": 11,
            "dec": 12,
            "december": 12,
        }
        return month_map.get(normalized)

    def _parse_fields(self, content: str) -> Dict[str, str]:
        """Parse field = value pairs from entry content."""
        fields = {}

        # Pattern: fieldname = value
        # Value can be quoted, braced, or a number/string reference
        pos = 0
        while pos < len(content):
            # Skip whitespace and commas
            while pos < len(content) and content[pos] in " \t\n\r,":
                pos += 1

            if pos >= len(content):
                break

            # Find field name
            match = re.match(r'(\w+)\s*=\s*', content[pos:])
            if not match:
                pos += 1
                continue

            field_name = match.group(1).lower()
            pos += match.end()

            # Parse value
            value, end_pos = self._parse_value(content[pos:])
            if value is not None:
                fields[field_name] = value
            pos += end_pos

        return fields

    def _parse_value(self, content: str) -> Tuple[Optional[str], int]:
        """Parse a field value, handling braces, quotes, and concatenation."""
        content = content.lstrip()
        if not content:
            return None, 0

        parts = []
        pos = 0

        while pos < len(content):
            # Skip whitespace
            while pos < len(content) and content[pos] in " \t\n\r":
                pos += 1

            if pos >= len(content):
                break

            char = content[pos]

            if char == "{":
                # Braced value
                end = self._find_matching_brace(content, pos)
                if end == -1:
                    break
                parts.append(content[pos + 1:end])
                pos = end + 1
            elif char == '"':
                # Quoted value
                end = content.find('"', pos + 1)
                while end != -1 and content[end - 1] == "\\":
                    end = content.find('"', end + 1)
                if end == -1:
                    break
                parts.append(content[pos + 1:end])
                pos = end + 1
            elif char.isdigit():
                # Numeric value
                match = re.match(r'\d+', content[pos:])
                if match:
                    parts.append(match.group())
                    pos += match.end()
                else:
                    break
            elif char.isalpha():
                # String reference
                match = re.match(r'\w+', content[pos:])
                if match:
                    ref = match.group().lower()
                    if ref in self.strings:
                        parts.append(self.strings[ref])
                    else:
                        parts.append(match.group())
                    pos += match.end()
                else:
                    break
            elif char == "#":
                # Concatenation operator
                pos += 1
            elif char == ",":
                # End of field
                break
            else:
                pos += 1

        if parts:
            return " ".join(parts), pos
        return None, pos

    def _parse_field_value(self, value: str) -> str:
        """Parse a simple field value for @string definitions."""
        value = value.strip()
        if value.startswith("{") and value.endswith("}"):
            return value[1:-1]
        if value.startswith('"') and value.endswith('"'):
            return value[1:-1]
        return value

    def _parse_authors(self, author_str: str) -> List[str]:
        """Parse author string into list of individual authors."""
        # Split by " and " (BibTeX convention)
        authors = re.split(r'\s+and\s+', author_str, flags=re.IGNORECASE)

        result = []
        for author in authors:
            author = author.strip()
            if not author:
                continue

            # Clean up LaTeX
            author = self._clean_latex(author)

            # Normalize "Last, First" to "First Last"
            if "," in author:
                parts = author.split(",", 1)
                if len(parts) == 2:
                    author = f"{parts[1].strip()} {parts[0].strip()}"

            result.append(author)

        return result

    def _clean_latex(self, text: Optional[str]) -> Optional[str]:
        """Clean LaTeX special characters from text."""
        if text is None:
            return None

        # Remove braces (used for capitalization preservation)
        text = re.sub(r'\{|\}', '', text)

        # Common LaTeX replacements
        replacements = [
            (r'\\&', '&'),
            (r"\\'e", 'é'),
            (r"\\'a", 'á'),
            (r"\\'i", 'í'),
            (r"\\'o", 'ó'),
            (r"\\'u", 'ú'),
            (r'\\"o', 'ö'),
            (r'\\"u', 'ü'),
            (r'\\"a', 'ä'),
            (r'\\ss', 'ß'),
            (r'\\~n', 'ñ'),
            (r'\\c{c}', 'ç'),
            (r'\\textemdash', '—'),
            (r'\\textendash', '–'),
            (r'---', '—'),
            (r'--', '–'),
            (r'~', ' '),  # Non-breaking space
            (r'\\%', '%'),
            (r'\\$', '$'),
            (r'\\_', '_'),
        ]

        for pattern, replacement in replacements:
            text = text.replace(pattern, replacement)

        # Remove remaining backslashes before letters
        text = re.sub(r'\\([a-zA-Z])', r'\1', text)

        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    def _clean_doi(self, doi: Optional[str]) -> Optional[str]:
        """Clean and normalize DOI."""
        if doi is None:
            return None

        # Remove URL prefix if present
        doi = re.sub(r'^https?://(dx\.)?doi\.org/', '', doi)

        # Remove common wrappers
        doi = doi.strip().strip('{}').strip()

        return doi if doi else None


# =============================================================================
# TEXT NORMALIZATION AND MATCHING
# =============================================================================


def normalize_text(text: str) -> str:
    """
    Normalize text for comparison.

    - Lowercase
    - Remove diacritics
    - Remove punctuation
    - Collapse whitespace
    """
    if not text:
        return ""

    # Lowercase
    text = text.lower()

    # Remove diacritics (é -> e, ü -> u, etc.)
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")

    # Remove punctuation except spaces
    text = re.sub(r'[^\w\s]', ' ', text)

    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def title_similarity(title1: str, title2: str) -> float:
    """
    Compute similarity between two titles.

    Returns a score from 0.0 to 1.0.
    """
    norm1 = normalize_text(title1)
    norm2 = normalize_text(title2)

    if not norm1 or not norm2:
        return 0.0

    # Use SequenceMatcher for similarity
    return SequenceMatcher(None, norm1, norm2).ratio()


def extract_doi_from_text(text: str) -> Optional[str]:
    """Extract DOI from text (filename, PDF text, etc.)."""
    # Common DOI patterns
    patterns = [
        r'10\.\d{4,}/[^\s]+',  # Standard DOI
        r'doi[:\s]*10\.\d{4,}/[^\s]+',  # With prefix
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            doi = match.group()
            # Clean up
            doi = re.sub(r'^doi[:\s]*', '', doi, flags=re.IGNORECASE)
            doi = doi.rstrip('.,;:)]')
            return doi

    return None


def extract_arxiv_id(text: str) -> Optional[str]:
    """Extract arXiv ID from text."""
    patterns = [
        r'arxiv[:\s]*(\d{4}\.\d{4,5})',  # New format: 2301.12345
        r'arxiv[:\s]*([\w-]+/\d{7})',  # Old format: hep-th/9901001
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)

    return None


# =============================================================================
# PDF-BIBTEX MATCHING
# =============================================================================


@dataclass
class MatchResult:
    """Result of matching a PDF to a BibTeX entry."""

    pdf_path: Path
    entry: BibTeXEntry
    confidence: float  # 0.0 to 1.0
    match_type: str  # "doi", "arxiv", "title", "filename", "manual"
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pdf_path": str(self.pdf_path),
            "cite_key": self.entry.cite_key,
            "confidence": self.confidence,
            "match_type": self.match_type,
            "details": self.details,
        }


class PDFBibTeXMatcher:
    """
    Match PDF files to BibTeX entries.

    Uses multiple strategies:
    1. DOI matching (highest confidence)
    2. arXiv ID matching
    3. Title similarity
    4. Filename analysis (author-year patterns)
    """

    def __init__(self, entries: List[BibTeXEntry]):
        self.entries = entries
        self._build_indices()

    def _build_indices(self) -> None:
        """Build lookup indices for faster matching."""
        self.doi_index: Dict[str, BibTeXEntry] = {}
        self.arxiv_index: Dict[str, BibTeXEntry] = {}
        self.title_index: Dict[str, BibTeXEntry] = {}

        for entry in self.entries:
            if entry.doi:
                # Normalize DOI for lookup
                doi_key = entry.doi.lower().strip()
                self.doi_index[doi_key] = entry

            if entry.eprint:
                self.arxiv_index[entry.eprint.lower()] = entry

            if entry.title:
                self.title_index[entry.normalized_title] = entry

    def match_pdf(
        self,
        pdf_path: Path,
        pdf_text: Optional[str] = None,
        min_title_similarity: float = 0.85,
    ) -> Optional[MatchResult]:
        """
        Attempt to match a PDF to a BibTeX entry.

        Args:
            pdf_path: Path to the PDF file
            pdf_text: Optional extracted text from the PDF (first page is usually enough)
            min_title_similarity: Minimum similarity score for title matching

        Returns:
            MatchResult if a match is found, None otherwise
        """
        filename = pdf_path.stem

        # Strategy 1: DOI from filename or text
        doi = extract_doi_from_text(filename)
        if not doi and pdf_text:
            doi = extract_doi_from_text(pdf_text[:2000])  # Check first 2000 chars

        if doi:
            doi_key = doi.lower().strip()
            if doi_key in self.doi_index:
                return MatchResult(
                    pdf_path=pdf_path,
                    entry=self.doi_index[doi_key],
                    confidence=0.99,
                    match_type="doi",
                    details={"matched_doi": doi},
                )

        # Strategy 2: arXiv ID from filename or text
        arxiv_id = extract_arxiv_id(filename)
        if not arxiv_id and pdf_text:
            arxiv_id = extract_arxiv_id(pdf_text[:2000])

        if arxiv_id:
            arxiv_key = arxiv_id.lower()
            if arxiv_key in self.arxiv_index:
                return MatchResult(
                    pdf_path=pdf_path,
                    entry=self.arxiv_index[arxiv_key],
                    confidence=0.95,
                    match_type="arxiv",
                    details={"matched_arxiv": arxiv_id},
                )

        # Strategy 3: Title similarity
        # Extract potential title from filename
        filename_clean = re.sub(r'[-_]', ' ', filename)
        filename_clean = re.sub(r'\d{4}', '', filename_clean)  # Remove year
        filename_clean = normalize_text(filename_clean)

        best_title_match = None
        best_title_score = 0.0

        for entry in self.entries:
            if entry.title:
                score = title_similarity(filename_clean, entry.title)
                if score > best_title_score and score >= min_title_similarity:
                    best_title_score = score
                    best_title_match = entry

        # Also try matching against PDF text title (usually in first 500 chars)
        if pdf_text:
            # First line is often the title
            first_lines = pdf_text[:500].split("\n")[:3]
            for line in first_lines:
                line = line.strip()
                if len(line) > 20:  # Reasonable title length
                    for entry in self.entries:
                        if entry.title:
                            score = title_similarity(line, entry.title)
                            if score > best_title_score and score >= min_title_similarity:
                                best_title_score = score
                                best_title_match = entry

        if best_title_match:
            return MatchResult(
                pdf_path=pdf_path,
                entry=best_title_match,
                confidence=best_title_score,
                match_type="title",
                details={"similarity_score": best_title_score},
            )

        # Strategy 4: Author-year pattern in filename
        # Pattern: "AuthorYear" or "Author_Year" or "Author et al Year"
        author_year_match = re.search(
            r'([A-Z][a-z]+)[\s_]*(?:et\s*al)?[\s_]*(\d{4})',
            pdf_path.stem
        )

        if author_year_match:
            author_name = author_year_match.group(1).lower()
            year = int(author_year_match.group(2))

            for entry in self.entries:
                if entry.year == year:
                    first_author = entry.first_author_lastname
                    if first_author and first_author.startswith(author_name[:3]):
                        return MatchResult(
                            pdf_path=pdf_path,
                            entry=entry,
                            confidence=0.7,
                            match_type="filename",
                            details={
                                "matched_author": author_name,
                                "matched_year": year,
                            },
                        )

        return None

    def match_all(
        self,
        pdf_paths: List[Path],
        get_pdf_text: Optional[callable] = None,
        min_title_similarity: float = 0.85,
    ) -> Tuple[List[MatchResult], List[Path]]:
        """
        Match multiple PDFs to BibTeX entries.

        Args:
            pdf_paths: List of PDF file paths
            get_pdf_text: Optional function to extract text from PDF
            min_title_similarity: Minimum similarity for title matching

        Returns:
            Tuple of (matched results, unmatched PDF paths)
        """
        matched = []
        unmatched = []

        for pdf_path in pdf_paths:
            pdf_text = None
            if get_pdf_text:
                try:
                    pdf_text = get_pdf_text(pdf_path)
                except Exception:
                    pass

            result = self.match_pdf(pdf_path, pdf_text, min_title_similarity)
            if result:
                matched.append(result)
            else:
                unmatched.append(pdf_path)

        return matched, unmatched

    def get_unmatched_entries(self, matched: List[MatchResult]) -> List[BibTeXEntry]:
        """Get BibTeX entries that weren't matched to any PDF."""
        matched_keys = {r.entry.cite_key for r in matched}
        return [e for e in self.entries if e.cite_key not in matched_keys]


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def parse_bibtex_file(path: Path) -> List[BibTeXEntry]:
    """Parse a BibTeX file and return list of entries."""
    parser = BibTeXParser()
    return parser.parse_file(path)


def parse_bibtex_string(content: str) -> List[BibTeXEntry]:
    """Parse BibTeX content string and return list of entries."""
    parser = BibTeXParser()
    return parser.parse(content)


def entries_to_paper_jsons(
    entries: List[BibTeXEntry],
    output_dir: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    """
    Convert BibTeX entries to AE paper.json format.

    Args:
        entries: List of BibTeXEntry objects
        output_dir: Optional directory to write individual paper.json files

    Returns:
        List of paper.json dictionaries
    """
    papers = []

    for entry in entries:
        paper = entry.to_paper_json()
        papers.append(paper)

        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)
            paper_file = output_dir / f"{entry.cite_key}_paper.json"
            paper_file.write_text(
                json.dumps(paper, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )

    return papers


def create_match_report(
    matched: List[MatchResult],
    unmatched_pdfs: List[Path],
    unmatched_entries: List[BibTeXEntry],
) -> Dict[str, Any]:
    """
    Create a summary report of matching results.

    Returns a dictionary suitable for JSON serialization.
    """
    return {
        "summary": {
            "total_pdfs": len(matched) + len(unmatched_pdfs),
            "total_bibtex_entries": len(matched) + len(unmatched_entries),
            "matched": len(matched),
            "unmatched_pdfs": len(unmatched_pdfs),
            "unmatched_entries": len(unmatched_entries),
        },
        "match_type_breakdown": {
            "doi": sum(1 for m in matched if m.match_type == "doi"),
            "arxiv": sum(1 for m in matched if m.match_type == "arxiv"),
            "title": sum(1 for m in matched if m.match_type == "title"),
            "filename": sum(1 for m in matched if m.match_type == "filename"),
        },
        "average_confidence": (
            sum(m.confidence for m in matched) / len(matched)
            if matched else 0.0
        ),
        "matches": [m.to_dict() for m in matched],
        "unmatched_pdfs": [str(p) for p in unmatched_pdfs],
        "unmatched_entries": [e.cite_key for e in unmatched_entries],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
