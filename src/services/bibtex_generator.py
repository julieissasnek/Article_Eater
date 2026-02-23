"""
BibTeX Generator with Full Metadata Support.
Sprint 3.0.4-D — 2026-02-09

Comprehensive BibTeX generation for Article Eater exports:
- All BibTeX entry types (article, book, inproceedings, phdthesis, etc.)
- Proper LaTeX escaping and special character handling
- Unique cite key generation with collision handling
- Full metadata fields (abstract, keywords, ISSN, arXiv, etc.)
- WebOfBelief integration for belief-to-citation mapping
- Batch export with proper formatting

Builds on bibtex_utils.py (parsing) to provide generation counterpart.

Created: 2026-02-09
"""

from __future__ import annotations

import hashlib
import re
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# ENTRY TYPES
# =============================================================================


class BibTeXEntryType(Enum):
    """Standard BibTeX entry types."""
    ARTICLE = "article"            # Journal article
    BOOK = "book"                  # Book with publisher
    BOOKLET = "booklet"            # Printed work without publisher
    CONFERENCE = "conference"      # Alias for inproceedings
    INBOOK = "inbook"              # Part of a book (chapter/pages)
    INCOLLECTION = "incollection"  # Part of a book with own title
    INPROCEEDINGS = "inproceedings"  # Conference paper
    MANUAL = "manual"              # Technical documentation
    MASTERSTHESIS = "mastersthesis"  # Master's thesis
    MISC = "misc"                  # Fallback for anything else
    ONLINE = "online"              # Web resource (BibLaTeX)
    PHDTHESIS = "phdthesis"        # PhD thesis
    PROCEEDINGS = "proceedings"    # Conference proceedings volume
    TECHREPORT = "techreport"      # Technical report
    UNPUBLISHED = "unpublished"    # Unpublished work with author/title


# Required fields by entry type (BibTeX standard)
REQUIRED_FIELDS = {
    BibTeXEntryType.ARTICLE: {"author", "title", "journal", "year"},
    BibTeXEntryType.BOOK: {"author", "title", "publisher", "year"},  # or editor
    BibTeXEntryType.BOOKLET: {"title"},
    BibTeXEntryType.CONFERENCE: {"author", "title", "booktitle", "year"},
    BibTeXEntryType.INBOOK: {"author", "title", "chapter", "publisher", "year"},  # or pages
    BibTeXEntryType.INCOLLECTION: {"author", "title", "booktitle", "publisher", "year"},
    BibTeXEntryType.INPROCEEDINGS: {"author", "title", "booktitle", "year"},
    BibTeXEntryType.MANUAL: {"title"},
    BibTeXEntryType.MASTERSTHESIS: {"author", "title", "school", "year"},
    BibTeXEntryType.MISC: set(),  # No required fields
    BibTeXEntryType.ONLINE: {"title", "url"},
    BibTeXEntryType.PHDTHESIS: {"author", "title", "school", "year"},
    BibTeXEntryType.PROCEEDINGS: {"title", "year"},
    BibTeXEntryType.TECHREPORT: {"author", "title", "institution", "year"},
    BibTeXEntryType.UNPUBLISHED: {"author", "title", "note"},
}


# =============================================================================
# LATEX ESCAPING
# =============================================================================


# Characters that need escaping in BibTeX (order matters!)
# We use a list to maintain order - backslash must NOT be first
LATEX_SPECIAL_CHARS_ORDERED = [
    # Handle these first (they don't involve backslash in source)
    ("&", r"\&"),
    ("%", r"\%"),
    ("$", r"\$"),
    ("#", r"\#"),
    ("_", r"\_"),
    ("~", r"\textasciitilde{}"),
    ("^", r"\textasciicircum{}"),
    # Braces need special handling - only escape unmatched ones
    # For now, we skip brace escaping as BibTeX values are wrapped in braces
]

# Standalone backslash handling (only for actual backslashes in text)
BACKSLASH_REPLACEMENT = ("\\", r"\textbackslash{}")

# Unicode to LaTeX replacements
UNICODE_TO_LATEX = {
    # Accented characters
    "á": r"\'a", "à": r"\`a", "â": r"\^a", "ä": r"\"a", "ã": r"\~a", "å": r"\aa",
    "Á": r"\'A", "À": r"\`A", "Â": r"\^A", "Ä": r"\"A", "Ã": r"\~A", "Å": r"\AA",
    "é": r"\'e", "è": r"\`e", "ê": r"\^e", "ë": r"\"e",
    "É": r"\'E", "È": r"\`E", "Ê": r"\^E", "Ë": r"\"E",
    "í": r"\'i", "ì": r"\`i", "î": r"\^i", "ï": r"\"i",
    "Í": r"\'I", "Ì": r"\`I", "Î": r"\^I", "Ï": r"\"I",
    "ó": r"\'o", "ò": r"\`o", "ô": r"\^o", "ö": r"\"o", "õ": r"\~o", "ø": r"\o",
    "Ó": r"\'O", "Ò": r"\`O", "Ô": r"\^O", "Ö": r"\"O", "Õ": r"\~O", "Ø": r"\O",
    "ú": r"\'u", "ù": r"\`u", "û": r"\^u", "ü": r"\"u",
    "Ú": r"\'U", "Ù": r"\`U", "Û": r"\^U", "Ü": r"\"U",
    "ý": r"\'y", "ÿ": r"\"y",
    "Ý": r"\'Y", "Ÿ": r"\"Y",
    "ñ": r"\~n", "Ñ": r"\~N",
    "ç": r"\c{c}", "Ç": r"\c{C}",
    # Special letters
    "ß": r"\ss", "æ": r"\ae", "Æ": r"\AE", "œ": r"\oe", "Œ": r"\OE",
    "ł": r"\l", "Ł": r"\L",
    # Punctuation
    "–": "--", "—": "---",
    "…": r"\ldots",
    "'": "`", "'": "'", """: "``", """: "''",
    "°": r"$^\circ$",
    "±": r"$\pm$",
    "×": r"$\times$",
    "÷": r"$\div$",
    "≤": r"$\leq$",
    "≥": r"$\geq$",
    "≠": r"$\neq$",
    "≈": r"$\approx$",
    "∞": r"$\infty$",
    "α": r"$\alpha$",
    "β": r"$\beta$",
    "γ": r"$\gamma$",
    "δ": r"$\delta$",
    "μ": r"$\mu$",
    "σ": r"$\sigma$",
    "π": r"$\pi$",
}


def escape_latex(text: str, preserve_case: bool = False) -> str:
    """
    Escape special characters for BibTeX.

    Args:
        text: Raw text to escape
        preserve_case: If True, wrap in braces to preserve capitalization

    Returns:
        LaTeX-safe string
    """
    if not text:
        return ""

    result = text

    # First, escape special LaTeX characters that appear in the SOURCE text
    # We need to be careful not to escape characters that will be part of LaTeX commands
    for char, replacement in LATEX_SPECIAL_CHARS_ORDERED:
        if char in result:
            result = result.replace(char, replacement)

    # Then, convert Unicode to LaTeX
    # These conversions produce backslash commands which should NOT be re-escaped
    for char, replacement in UNICODE_TO_LATEX.items():
        if char in result:
            result = result.replace(char, replacement)

    # Handle remaining non-ASCII characters
    cleaned = []
    for char in result:
        if ord(char) > 127 and char not in UNICODE_TO_LATEX:
            # Try to decompose and remove diacritics
            normalized = unicodedata.normalize("NFD", char)
            base = "".join(c for c in normalized if unicodedata.category(c) != "Mn")
            cleaned.append(base if base else "?")
        else:
            cleaned.append(char)
    result = "".join(cleaned)

    # Preserve case by wrapping in braces if requested
    if preserve_case:
        # Find words that start with uppercase (excluding first word after space/punctuation)
        words = []
        for word in result.split():
            if word and word[0].isupper() and len(word) > 1:
                # Wrap acronyms and proper nouns
                if word.isupper() or any(c.isupper() for c in word[1:]):
                    words.append("{" + word + "}")
                else:
                    words.append(word)
            else:
                words.append(word)
        result = " ".join(words)

    return result


def clean_for_citekey(text: str) -> str:
    """
    Clean text for use in a citation key.

    Removes diacritics, special characters, and normalizes to ASCII.
    """
    if not text:
        return ""

    # Normalize Unicode and remove diacritics
    normalized = unicodedata.normalize("NFD", text)
    ascii_text = "".join(c for c in normalized if unicodedata.category(c) != "Mn")

    # Keep only alphanumeric characters
    cleaned = re.sub(r"[^a-zA-Z0-9]", "", ascii_text)

    return cleaned.lower()


# =============================================================================
# BIBTEX ENTRY DATA CLASS
# =============================================================================


@dataclass
class GeneratedBibTeXEntry:
    """
    A BibTeX entry ready for generation.

    Contains all possible BibTeX fields with proper typing.
    """
    # Core identification
    entry_type: BibTeXEntryType
    cite_key: str  # Will be auto-generated if empty

    # Required fields (vary by entry type)
    author: Optional[str] = None  # "Last1, First1 and Last2, First2"
    authors: List[str] = field(default_factory=list)  # Parsed list
    title: str = ""
    year: Optional[int] = None

    # Publication venue
    journal: Optional[str] = None  # For article
    booktitle: Optional[str] = None  # For inproceedings/incollection
    publisher: Optional[str] = None
    school: Optional[str] = None  # For thesis
    institution: Optional[str] = None  # For techreport
    organization: Optional[str] = None

    # Volume/issue/pages
    volume: Optional[str] = None
    number: Optional[str] = None  # Issue number
    pages: Optional[str] = None
    chapter: Optional[str] = None

    # Identifiers
    doi: Optional[str] = None
    isbn: Optional[str] = None
    issn: Optional[str] = None
    url: Optional[str] = None
    eprint: Optional[str] = None  # arXiv ID
    archiveprefix: Optional[str] = None  # "arXiv"
    primaryclass: Optional[str] = None  # arXiv category

    # Additional metadata
    abstract: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    note: Optional[str] = None
    annote: Optional[str] = None  # Annotation

    # Editor/address/edition
    editor: Optional[str] = None
    edition: Optional[str] = None
    address: Optional[str] = None

    # Series/howpublished
    series: Optional[str] = None
    howpublished: Optional[str] = None

    # Month (as string or number)
    month: Optional[str] = None

    # Custom fields
    custom_fields: Dict[str, str] = field(default_factory=dict)

    # Source tracking
    source_id: Optional[str] = None  # Link to original paper/belief

    def __post_init__(self):
        """Normalize fields after initialization."""
        # Convert authors list to author string if needed
        if self.authors and not self.author:
            self.author = " and ".join(self.authors)
        # Parse author string to list if needed
        elif self.author and not self.authors:
            self.authors = [a.strip() for a in re.split(r"\s+and\s+", self.author, flags=re.IGNORECASE)]

    def get_first_author_lastname(self) -> str:
        """Extract first author's last name for cite key generation."""
        if not self.authors and self.author:
            self.authors = [a.strip() for a in re.split(r"\s+and\s+", self.author, flags=re.IGNORECASE)]

        if not self.authors:
            return "unknown"

        first = self.authors[0]

        # Handle "Last, First" format
        if "," in first:
            return first.split(",")[0].strip()

        # Handle "First Last" format
        parts = first.split()
        if parts:
            return parts[-1]

        return "unknown"

    def is_valid(self) -> Tuple[bool, List[str]]:
        """
        Check if entry has all required fields for its type.

        Returns:
            Tuple of (is_valid, list of missing fields)
        """
        required = REQUIRED_FIELDS.get(self.entry_type, set())
        missing = []

        for field_name in required:
            value = getattr(self, field_name, None)
            if value is None or value == "" or value == []:
                missing.append(field_name)

        return len(missing) == 0, missing

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = {
            "entry_type": self.entry_type.value,
            "cite_key": self.cite_key,
        }

        # Add all non-empty fields
        for field_name in [
            "author", "title", "year", "journal", "booktitle", "publisher",
            "school", "institution", "organization", "volume", "number",
            "pages", "chapter", "doi", "isbn", "issn", "url", "eprint",
            "archiveprefix", "primaryclass", "abstract", "note", "annote",
            "editor", "edition", "address", "series", "howpublished", "month"
        ]:
            value = getattr(self, field_name, None)
            if value is not None and value != "":
                result[field_name] = value

        if self.keywords:
            result["keywords"] = self.keywords
        if self.authors:
            result["authors"] = self.authors
        if self.custom_fields:
            result["custom_fields"] = self.custom_fields
        if self.source_id:
            result["source_id"] = self.source_id

        return result


# =============================================================================
# CITE KEY GENERATOR
# =============================================================================


class CiteKeyGenerator:
    """
    Generates unique citation keys with collision handling.

    Key format: authorYear[suffix]
    Examples: smith2024, smith2024a, smith2024b
    """

    def __init__(self):
        self.used_keys: Set[str] = set()

    def generate(
        self,
        entry: GeneratedBibTeXEntry,
        style: str = "authoryear"
    ) -> str:
        """
        Generate a unique citation key for an entry.

        Args:
            entry: The BibTeX entry
            style: Key style ("authoryear", "authorTitle", "doi")

        Returns:
            Unique citation key
        """
        if style == "doi" and entry.doi:
            # DOI-based key (guaranteed unique)
            base = self._doi_to_key(entry.doi)
        elif style == "authorTitle":
            # Author + title words
            base = self._author_title_key(entry)
        else:
            # Default: author + year
            base = self._author_year_key(entry)

        # Ensure uniqueness
        key = base
        suffix_index = 0

        while key in self.used_keys:
            suffix_index += 1
            # Use lowercase letters a-z, then aa, ab, etc.
            suffix = self._index_to_suffix(suffix_index)
            key = f"{base}{suffix}"

        self.used_keys.add(key)
        return key

    def _author_year_key(self, entry: GeneratedBibTeXEntry) -> str:
        """Generate author + year key."""
        author = clean_for_citekey(entry.get_first_author_lastname())
        year = str(entry.year) if entry.year else "nodate"
        return f"{author}{year}"

    def _author_title_key(self, entry: GeneratedBibTeXEntry) -> str:
        """Generate author + title key."""
        author = clean_for_citekey(entry.get_first_author_lastname())

        # Get first meaningful word from title
        title_words = entry.title.split()
        stop_words = {"the", "a", "an", "of", "in", "on", "for", "and", "or", "to"}
        title_word = ""
        for word in title_words:
            cleaned = clean_for_citekey(word)
            if cleaned and cleaned not in stop_words:
                title_word = cleaned[:10]  # Limit length
                break

        return f"{author}{title_word}"

    def _doi_to_key(self, doi: str) -> str:
        """Convert DOI to citation key."""
        # Hash the DOI for a short unique key
        hash_val = hashlib.md5(doi.encode()).hexdigest()[:8]
        return f"doi{hash_val}"

    def _index_to_suffix(self, index: int) -> str:
        """Convert numeric index to alphabetic suffix."""
        if index <= 26:
            return chr(ord('a') + index - 1)
        else:
            # For indices > 26, use aa, ab, etc.
            first = (index - 1) // 26
            second = (index - 1) % 26
            return chr(ord('a') + first - 1) + chr(ord('a') + second)

    def reset(self):
        """Clear used keys (for new batch)."""
        self.used_keys.clear()

    def add_existing(self, keys: List[str]):
        """Register existing keys to avoid collisions."""
        self.used_keys.update(keys)


# =============================================================================
# BIBTEX GENERATOR
# =============================================================================


class FullBibTeXGenerator:
    """
    Comprehensive BibTeX generator with full metadata support.

    Features:
    - All BibTeX entry types
    - Proper LaTeX escaping
    - Unique cite key generation
    - Full metadata fields
    - Batch export with formatting options
    """

    def __init__(
        self,
        preserve_title_case: bool = True,
        include_abstract: bool = True,
        include_keywords: bool = True,
        include_doi: bool = True,
        include_url: bool = True,
        indent: str = "  ",
        key_style: str = "authoryear"
    ):
        """
        Initialize the generator.

        Args:
            preserve_title_case: Wrap title words in braces to preserve case
            include_abstract: Include abstract field
            include_keywords: Include keywords field
            include_doi: Include DOI field
            include_url: Include URL field
            indent: Indentation string for fields
            key_style: Citation key style ("authoryear", "authorTitle", "doi")
        """
        self.preserve_title_case = preserve_title_case
        self.include_abstract = include_abstract
        self.include_keywords = include_keywords
        self.include_doi = include_doi
        self.include_url = include_url
        self.indent = indent
        self.key_style = key_style

        self.key_generator = CiteKeyGenerator()

    def generate_entry(
        self,
        entry: GeneratedBibTeXEntry,
        auto_key: bool = True
    ) -> str:
        """
        Generate BibTeX string for a single entry.

        Args:
            entry: The entry to generate
            auto_key: Auto-generate cite key if empty

        Returns:
            BibTeX formatted string
        """
        # Generate cite key if needed
        cite_key = entry.cite_key
        if not cite_key and auto_key:
            cite_key = self.key_generator.generate(entry, self.key_style)
            entry.cite_key = cite_key

        # Start entry
        lines = [f"@{entry.entry_type.value}{{{cite_key},"]

        # Add fields in preferred order
        fields = self._collect_fields(entry)

        for field_name, value in fields:
            formatted = self._format_field(field_name, value)
            lines.append(f"{self.indent}{formatted},")

        # Close entry (remove trailing comma from last field, but only if we added fields)
        if fields and lines[-1].endswith(","):
            lines[-1] = lines[-1][:-1]
        lines.append("}")

        return "\n".join(lines)

    def generate_batch(
        self,
        entries: List[GeneratedBibTeXEntry],
        header_comment: Optional[str] = None
    ) -> str:
        """
        Generate BibTeX for multiple entries.

        Args:
            entries: List of entries
            header_comment: Optional comment to add at top

        Returns:
            Complete BibTeX file content
        """
        self.key_generator.reset()

        parts = []

        # Add header comment
        if header_comment:
            parts.append(f"% {header_comment}")
            parts.append(f"% Generated: {datetime.now(timezone.utc).isoformat()}")
            parts.append("")

        # Generate each entry
        for entry in entries:
            parts.append(self.generate_entry(entry))
            parts.append("")  # Blank line between entries

        return "\n".join(parts)

    def _collect_fields(self, entry: GeneratedBibTeXEntry) -> List[Tuple[str, str]]:
        """
        Collect non-empty fields in preferred order.

        Returns:
            List of (field_name, value) tuples
        """
        fields = []

        # Preferred field order
        field_order = [
            "author", "title", "year", "journal", "booktitle",
            "publisher", "school", "institution", "organization",
            "volume", "number", "pages", "chapter",
            "editor", "edition", "series",
            "month", "address",
            "doi", "isbn", "issn", "url",
            "eprint", "archiveprefix", "primaryclass",
            "keywords", "abstract",
            "note", "annote", "howpublished"
        ]

        # Add fields in order
        for field_name in field_order:
            value = self._get_field_value(entry, field_name)
            if value is not None:
                fields.append((field_name, value))

        # Add custom fields
        for key, value in entry.custom_fields.items():
            if value:
                fields.append((key, value))

        return fields

    def _get_field_value(
        self,
        entry: GeneratedBibTeXEntry,
        field_name: str
    ) -> Optional[str]:
        """Get formatted field value, respecting include flags."""
        # Check include flags
        if field_name == "abstract" and not self.include_abstract:
            return None
        if field_name == "keywords" and not self.include_keywords:
            return None
        if field_name == "doi" and not self.include_doi:
            return None
        if field_name == "url" and not self.include_url:
            return None

        # Get raw value
        value = getattr(entry, field_name, None)

        if value is None or value == "" or value == []:
            return None

        # Special handling for certain fields
        if field_name == "keywords" and isinstance(value, list):
            return ", ".join(value)

        if field_name == "year" and isinstance(value, int):
            return str(value)

        return str(value)

    def _format_field(self, field_name: str, value: str) -> str:
        """Format a field for BibTeX output."""
        # Fields that don't need braces
        numeric_fields = {"year", "volume", "number", "chapter"}

        # Escape LaTeX special characters
        if field_name == "title":
            escaped = escape_latex(value, preserve_case=self.preserve_title_case)
        elif field_name in {"doi", "url", "isbn", "issn", "eprint"}:
            # Don't escape identifiers
            escaped = value
        else:
            escaped = escape_latex(value, preserve_case=False)

        # Format based on field type
        if field_name in numeric_fields and escaped.isdigit():
            return f"{field_name} = {escaped}"
        else:
            # Wrap in braces
            return f"{field_name} = {{{escaped}}}"


# =============================================================================
# WEBOFBELIEF INTEGRATION
# =============================================================================


def entries_from_belief_sources(
    belief_sources: List[Dict[str, Any]],
    default_entry_type: BibTeXEntryType = BibTeXEntryType.ARTICLE
) -> List[GeneratedBibTeXEntry]:
    """
    Convert belief source metadata to BibTeX entries.

    Args:
        belief_sources: List of source dicts with paper metadata
        default_entry_type: Default entry type when not specified

    Returns:
        List of GeneratedBibTeXEntry objects
    """
    entries = []

    for source in belief_sources:
        # Determine entry type
        entry_type = default_entry_type
        source_type = source.get("type", "").lower()

        if "journal" in source and source.get("journal"):
            entry_type = BibTeXEntryType.ARTICLE
        elif "booktitle" in source or "conference" in source.get("type", "").lower():
            entry_type = BibTeXEntryType.INPROCEEDINGS
        elif "thesis" in source_type:
            if "phd" in source_type or "doctoral" in source_type:
                entry_type = BibTeXEntryType.PHDTHESIS
            else:
                entry_type = BibTeXEntryType.MASTERSTHESIS
        elif "book" in source_type:
            entry_type = BibTeXEntryType.BOOK
        elif "report" in source_type:
            entry_type = BibTeXEntryType.TECHREPORT

        # Extract authors
        authors = source.get("authors", [])
        if isinstance(authors, str):
            authors = [a.strip() for a in re.split(r"\s+and\s+|,\s*", authors)]

        # Create entry
        entry = GeneratedBibTeXEntry(
            entry_type=entry_type,
            cite_key=source.get("cite_key", ""),
            title=source.get("title", ""),
            authors=authors,
            year=source.get("year"),
            journal=source.get("journal"),
            booktitle=source.get("booktitle") or source.get("conference"),
            publisher=source.get("publisher"),
            school=source.get("school") or source.get("institution"),
            institution=source.get("institution"),
            volume=source.get("volume"),
            number=source.get("number") or source.get("issue"),
            pages=source.get("pages"),
            doi=source.get("doi"),
            isbn=source.get("isbn"),
            issn=source.get("issn"),
            url=source.get("url"),
            eprint=source.get("arxiv_id") or source.get("eprint"),
            abstract=source.get("abstract"),
            keywords=source.get("keywords", []),
            source_id=source.get("paper_id") or source.get("source_id"),
        )

        # Set arXiv prefix if eprint is set
        if entry.eprint:
            entry.archiveprefix = "arXiv"

        entries.append(entry)

    return entries


def entry_from_paper_json(paper: Dict[str, Any]) -> GeneratedBibTeXEntry:
    """
    Convert an AE paper.json format dict to BibTeX entry.

    Args:
        paper: Dict matching ae.paper.v1 schema

    Returns:
        GeneratedBibTeXEntry
    """
    # Determine entry type
    venue = paper.get("venue", "") or ""
    journal = paper.get("journal")

    if journal:
        entry_type = BibTeXEntryType.ARTICLE
    elif "conference" in venue.lower() or "proceedings" in venue.lower():
        entry_type = BibTeXEntryType.INPROCEEDINGS
    elif paper.get("arxiv_id"):
        entry_type = BibTeXEntryType.MISC
    else:
        entry_type = BibTeXEntryType.ARTICLE

    # Get authors
    authors = paper.get("authors", [])
    if not authors and paper.get("author_string"):
        authors = [a.strip() for a in paper["author_string"].split(",")]

    # Get cite key from bibtex_source if available
    cite_key = ""
    bibtex_source = paper.get("bibtex_source", {})
    if bibtex_source:
        cite_key = bibtex_source.get("cite_key", "")

    return GeneratedBibTeXEntry(
        entry_type=entry_type,
        cite_key=cite_key,
        title=paper.get("title", ""),
        authors=authors,
        year=paper.get("year"),
        journal=journal,
        booktitle=paper.get("venue") if not journal else None,
        volume=paper.get("volume"),
        number=paper.get("issue"),
        pages=paper.get("pages"),
        doi=paper.get("doi"),
        url=paper.get("url"),
        eprint=paper.get("arxiv_id"),
        abstract=paper.get("abstract"),
        keywords=paper.get("keywords", []),
        source_id=paper.get("paper_id"),
    )


# =============================================================================
# EXPORT FUNCTIONS
# =============================================================================


def export_to_bibtex(
    entries: List[GeneratedBibTeXEntry],
    output_path: Optional[Path] = None,
    **kwargs
) -> str:
    """
    Export entries to BibTeX format.

    Args:
        entries: List of entries to export
        output_path: Optional path to write file
        **kwargs: Options passed to FullBibTeXGenerator

    Returns:
        BibTeX content string
    """
    generator = FullBibTeXGenerator(**kwargs)
    content = generator.generate_batch(
        entries,
        header_comment="Article Eater V23 BibTeX Export"
    )

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
        logger.info(f"Exported {len(entries)} entries to {output_path}")

    return content


def export_papers_to_bibtex(
    papers: List[Dict[str, Any]],
    output_path: Optional[Path] = None,
    **kwargs
) -> str:
    """
    Export paper.json format papers to BibTeX.

    Args:
        papers: List of paper dicts (ae.paper.v1 format)
        output_path: Optional path to write file
        **kwargs: Options passed to FullBibTeXGenerator

    Returns:
        BibTeX content string
    """
    entries = [entry_from_paper_json(p) for p in papers]
    return export_to_bibtex(entries, output_path, **kwargs)


def export_sources_to_bibtex(
    sources: List[Dict[str, Any]],
    output_path: Optional[Path] = None,
    **kwargs
) -> str:
    """
    Export belief sources to BibTeX.

    Args:
        sources: List of source metadata dicts
        output_path: Optional path to write file
        **kwargs: Options passed to FullBibTeXGenerator

    Returns:
        BibTeX content string
    """
    entries = entries_from_belief_sources(sources)
    return export_to_bibtex(entries, output_path, **kwargs)


# =============================================================================
# VALIDATION
# =============================================================================


@dataclass
class BibTeXValidationResult:
    """Result of validating a BibTeX entry."""
    entry: GeneratedBibTeXEntry
    is_valid: bool
    missing_fields: List[str]
    warnings: List[str]


def validate_entries(
    entries: List[GeneratedBibTeXEntry]
) -> List[BibTeXValidationResult]:
    """
    Validate a list of BibTeX entries.

    Returns:
        List of validation results
    """
    results = []

    for entry in entries:
        is_valid, missing = entry.is_valid()

        warnings = []

        # Check for recommended fields
        if not entry.doi and not entry.url:
            warnings.append("No DOI or URL - may be hard to locate")

        if entry.year and (entry.year < 1900 or entry.year > datetime.now().year + 1):
            warnings.append(f"Suspicious year: {entry.year}")

        if entry.title and len(entry.title) < 10:
            warnings.append("Title seems too short")

        if not entry.authors and not entry.author:
            warnings.append("No authors specified")

        results.append(BibTeXValidationResult(
            entry=entry,
            is_valid=is_valid,
            missing_fields=missing,
            warnings=warnings
        ))

    return results


# =============================================================================
# CONVENIENCE SINGLETON
# =============================================================================


_generator: Optional[FullBibTeXGenerator] = None


def get_bibtex_generator(**kwargs) -> FullBibTeXGenerator:
    """Get or create BibTeX generator singleton."""
    global _generator
    if _generator is None or kwargs:
        _generator = FullBibTeXGenerator(**kwargs)
    return _generator
