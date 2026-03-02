"""
Theory Guide Service — Structured Access to ATLAS Theory Guides

Loads and parses 12 HTML theory guides with progressive disclosure (Quick/Standard/Technical).
Provides fuzzy matching across theory names and aliases. Integrates with theory metadata JSONs
for constructs, maturity levels, and entrenchment scores.

Usage:
    service = TheoryGuideService()
    guide = service.get_guide("attention restoration theory", detail_level="quick")
    summary = service.get_theory_summary("ART")
    matches = service.search_theories("predictive processing")
"""

import json
import logging
import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Dict, List, Optional
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class TheoryGuideResult:
    """Structured result from theory guide query."""
    theory_id: str
    display_name: str
    detail_level: str  # quick, standard, technical
    content: str  # extracted text content
    constructs: List[str] = field(default_factory=list)
    maturity: str = ""
    atlas_status: str = ""
    guide_path: str = ""
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "theory_id": self.theory_id,
            "display_name": self.display_name,
            "detail_level": self.detail_level,
            "content": self.content,
            "constructs": self.constructs,
            "maturity": self.maturity,
            "atlas_status": self.atlas_status,
            "guide_path": self.guide_path,
            "metadata": self.metadata,
        }


# =============================================================================
# HTML Parsing
# =============================================================================

class _DetailLevelExtractor(HTMLParser):
    """Extract content at specific detail levels (quick/standard/technical)."""

    def __init__(self, target_level: str = "quick"):
        super().__init__()
        self.target_level = target_level
        self._in_target_div = False
        self._div_depth = 0
        self._parts = []
        self._tag_stack = []

        # Valid levels: quick, standard, technical
        # At technical level, we get all; at standard, we get quick+standard
        self.level_hierarchy = {"quick": 1, "standard": 2, "technical": 3}
        self._target_level_value = self.level_hierarchy.get(target_level, 3)

    def handle_starttag(self, tag, attrs):
        """Track which divs we're in and capture structure."""
        attrs_dict = dict(attrs)

        # Check if this is a detail-level div
        if tag == "div" and "class" in attrs_dict:
            class_str = attrs_dict["class"]
            if "quick-content" in class_str and self._target_level_value >= 1:
                self._in_target_div = True
                self._div_depth = 1
            elif "standard-content" in class_str and self._target_level_value >= 2:
                self._in_target_div = True
                self._div_depth = 1
            elif "technical-content" in class_str and self._target_level_value >= 3:
                self._in_target_div = True
                self._div_depth = 1

        if self._in_target_div:
            if tag == "div":
                self._div_depth += 1

            # Add structural markers for headings
            if tag in ("h1", "h2", "h3", "h4"):
                self._parts.append("\n")
            elif tag == "li":
                self._parts.append("\n• ")
            elif tag == "p":
                self._parts.append("\n")
            elif tag == "br":
                self._parts.append("\n")

        self._tag_stack.append(tag)

    def handle_endtag(self, tag):
        """Track end of tags."""
        if self._tag_stack and self._tag_stack[-1] == tag:
            self._tag_stack.pop()

        if self._in_target_div:
            if tag == "div":
                self._div_depth -= 1
                if self._div_depth == 0:
                    self._in_target_div = False
            elif tag in ("h1", "h2", "h3", "h4", "p"):
                self._parts.append("\n")

    def handle_data(self, data):
        """Extract text content."""
        if self._in_target_div:
            # Skip style/script content
            if self._tag_stack and self._tag_stack[-1] in ("style", "script"):
                return
            text = data.strip()
            if text:
                self._parts.append(text)
                self._parts.append(" ")

    def get_text(self) -> str:
        """Get extracted text with normalized whitespace."""
        text = "".join(self._parts)
        # Normalize multiple spaces and newlines
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        return text.strip()


class _TitleExtractor(HTMLParser):
    """Extract title from HTML."""

    def __init__(self):
        super().__init__()
        self.title = ""
        self._in_title = False
        self._in_h1 = False

    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self._in_title = True
        elif tag == "h1":
            self._in_h1 = True

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        elif tag == "h1":
            self._in_h1 = False

    def handle_data(self, data):
        if self._in_title or self._in_h1:
            self.title = data.strip()


# =============================================================================
# Theory Guide Service
# =============================================================================

class TheoryGuideService:
    """Load, parse, and serve theory guides with multiple detail levels."""

    def __init__(self, guides_dir: str = "docs/theory_guides", theories_dir: str = "data/theories"):
        """Initialize service and load all guides and metadata."""
        self.guides_dir = Path(guides_dir) if not Path(guides_dir).is_absolute() else Path(guides_dir)
        if not self.guides_dir.is_absolute():
            self.guides_dir = PROJECT_ROOT / self.guides_dir

        self.theories_dir = Path(theories_dir) if not Path(theories_dir).is_absolute() else Path(theories_dir)
        if not self.theories_dir.is_absolute():
            self.theories_dir = PROJECT_ROOT / self.theories_dir

        # Cache parsed guides: {(theory_id, detail_level): content_text}
        self._guide_cache: Dict[tuple, str] = {}

        # Cache loaded metadata
        self._metadata_cache: Dict[str, Dict] = {}

        # Build alias map from JSON files
        self._alias_map: Dict[str, str] = {}  # alias → theory_id
        self._theory_names: Dict[str, str] = {}  # theory_id → display_name
        self._guide_files: Dict[str, str] = {}  # theory_id → guide_basename

        self._load_guides_and_metadata()

    def _load_guides_and_metadata(self) -> None:
        """Scan guides directory and build alias/name maps."""
        if not self.guides_dir.exists():
            logger.warning(f"Guides directory not found: {self.guides_dir}")
            return

        # Hardcoded mapping of guide files to theory IDs
        # (These should match the actual guide filenames)
        guide_mapping = {
            "attention_restoration": "attention-restoration-theory",
            "attention-restoration": "attention-restoration-theory",
            "flow_theory": "flow-theory",
            "chronobiology": "chronobiological-regulation",
            "cognitive_map": "spatial-navigation",
            "cpted": "cpted",
            "episodic_memory": "memory-systems",
            "goldilocks_principle": "goldilocks-principle",
            "kaplan_preference": "stress-recovery-theory",
            "pad_model": "pad-model",
            "place_attachment": "place-attachment",
            "privacy_regulation": "privacy-regulation",
            "proxemics": "proxemics",
        }

        # Scan actual guide files
        for guide_file in self.guides_dir.glob("*_guide.html"):
            if guide_file.name == "index.html":
                continue

            basename = guide_file.stem.replace("_guide", "")

            # Try to determine theory ID from filename
            theory_id = None
            for alt_name, mapped_id in guide_mapping.items():
                if alt_name.replace("-", "_") == basename or alt_name == basename:
                    theory_id = mapped_id
                    break

            if not theory_id:
                # Use basename as fallback
                theory_id = basename.replace("_", "-")

            self._guide_files[theory_id] = basename

            # Try to load metadata JSON to get display name
            display_name = self._get_display_name(theory_id, basename)
            self._theory_names[theory_id] = display_name

            # Build aliases from theory name and abbreviations
            self._build_aliases_for_theory(theory_id, display_name)

    def _get_display_name(self, theory_id: str, guide_basename: str) -> str:
        """Get display name from metadata JSON or construct from filename."""
        # Try to load from metadata
        metadata = self._load_metadata(theory_id)
        if metadata and "name" in metadata:
            return metadata["name"]

        # Fall back to filename-based name
        parts = guide_basename.replace("_", " ").replace("-", " ")
        return " ".join(word.capitalize() for word in parts.split())

    def _build_aliases_for_theory(self, theory_id: str, display_name: str) -> None:
        """Build comprehensive alias map for a theory."""
        # Load metadata for abbreviations
        metadata = self._load_metadata(theory_id)

        # Primary alias from display name
        self._alias_map[display_name.lower()] = theory_id

        # Abbreviated forms
        if metadata:
            if "abbreviation" in metadata:
                self._alias_map[metadata["abbreviation"].lower()] = theory_id

            # Alternative names
            for name_variant in self._get_name_variants(display_name):
                self._alias_map[name_variant.lower()] = theory_id

    def _get_name_variants(self, name: str) -> List[str]:
        """Generate name variants for fuzzy matching."""
        variants = [name]

        # Remove "theory", "hypothesis", "model", "principle"
        for suffix in ("theory", "hypothesis", "model", "principle", "regulation"):
            if name.lower().endswith(suffix):
                variant = name[:-len(suffix)].strip()
                variants.append(variant)

        # Hyphenated variants
        if "-" in name:
            variants.append(name.replace("-", " "))
        if " " in name:
            variants.append(name.replace(" ", "-"))

        # Initials (e.g., "ART" for "Attention Restoration Theory")
        words = name.split()
        if len(words) >= 2:
            initials = "".join(w[0] for w in words)
            variants.append(initials)

        return variants

    def _load_metadata(self, theory_id: str) -> Optional[Dict[str, Any]]:
        """Load theory metadata JSON."""
        if theory_id in self._metadata_cache:
            return self._metadata_cache[theory_id]

        # Try multiple filename patterns
        patterns = [
            f"{theory_id}.json",
            f"{theory_id.replace('-', '_')}.json",
            f"{theory_id.replace('_', '-')}.json",
        ]

        for pattern in patterns:
            filepath = self.theories_dir / pattern
            if filepath.exists():
                try:
                    with open(filepath) as f:
                        data = json.load(f)
                    self._metadata_cache[theory_id] = data
                    return data
                except Exception as e:
                    logger.warning(f"Failed to load metadata for {theory_id}: {e}")

        # Also check for abbreviated form in tea_scores.json
        tea_path = self.theories_dir / "tea_scores.json"
        if tea_path.exists():
            try:
                with open(tea_path) as f:
                    tea_data = json.load(f)

                if "theories" in tea_data:
                    for theory in tea_data["theories"]:
                        if theory.get("theory_id") == theory_id:
                            self._metadata_cache[theory_id] = theory
                            return theory
            except Exception as e:
                logger.debug(f"Non-critical: {e}")

        return None

    def _load_guide_html(self, theory_id: str) -> Optional[str]:
        """Load HTML content of a guide."""
        if theory_id not in self._guide_files:
            return None

        guide_basename = self._guide_files[theory_id]
        guide_path = self.guides_dir / f"{guide_basename}_guide.html"

        if not guide_path.exists():
            logger.warning(f"Guide file not found: {guide_path}")
            return None

        try:
            return guide_path.read_text(encoding='utf-8', errors='replace')
        except Exception as e:
            logger.error(f"Failed to read guide {guide_path}: {e}")
            return None

    def _extract_content_at_level(self, html: str, detail_level: str) -> str:
        """Extract content at specific detail level from HTML."""
        cache_key = (html[:100], detail_level)  # Simple cache key
        if cache_key in self._guide_cache:
            return self._guide_cache[cache_key]

        extractor = _DetailLevelExtractor(target_level=detail_level)
        try:
            extractor.feed(html)
            content = extractor.get_text()
            self._guide_cache[cache_key] = content
            return content
        except Exception as e:
            logger.error(f"Failed to extract {detail_level} content: {e}")
            return ""

    def fuzzy_match(self, query: str, candidates: List[str], threshold: float = 0.6) -> Optional[str]:
        """Find best fuzzy match in candidate list."""
        if not candidates:
            return None

        query_lower = query.lower()
        best_match = None
        best_score = threshold

        for candidate in candidates:
            candidate_lower = candidate.lower()

            # Exact match has priority
            if query_lower == candidate_lower:
                return candidate

            # Check if query is substring
            if query_lower in candidate_lower or candidate_lower in query_lower:
                return candidate

            # Fuzzy match
            ratio = SequenceMatcher(None, query_lower, candidate_lower).ratio()
            if ratio > best_score:
                best_score = ratio
                best_match = candidate

        return best_match

    def get_guide(self, theory_name: str, detail_level: str = "quick") -> Optional[TheoryGuideResult]:
        """
        Get theory guide at specified detail level.

        Args:
            theory_name: Name, abbreviation, or alias for the theory
            detail_level: "quick", "standard", or "technical"

        Returns:
            TheoryGuideResult if found, None otherwise
        """
        if detail_level not in ("quick", "standard", "technical"):
            detail_level = "quick"

        # Find matching theory ID
        theory_name_lower = theory_name.lower()

        # Direct alias lookup
        if theory_name_lower in self._alias_map:
            theory_id = self._alias_map[theory_name_lower]
        else:
            # Fuzzy match against available theories
            available = list(self._theory_names.keys())
            matched = self.fuzzy_match(theory_name_lower, [t.lower() for t in available])
            if matched:
                theory_id = next(t for t in available if t.lower() == matched)
            else:
                logger.warning(f"No matching theory for: {theory_name}")
                return None

        # Load guide HTML
        html = self._load_guide_html(theory_id)
        if not html:
            return None

        # Extract content at detail level
        content = self._extract_content_at_level(html, detail_level)
        if not content:
            logger.warning(f"No content extracted at {detail_level} level for {theory_id}")
            return None

        # Load metadata
        metadata = self._load_metadata(theory_id)
        constructs = []
        maturity = ""
        atlas_status = ""

        if metadata:
            if "constructs" in metadata:
                constructs = [c.get("construct_name", "") for c in metadata.get("constructs", [])]
            maturity = metadata.get("maturity", "")
            atlas_status = metadata.get("status", "")

        guide_basename = self._guide_files.get(theory_id, "")
        guide_path = self.guides_dir / f"{guide_basename}_guide.html" if guide_basename else ""

        return TheoryGuideResult(
            theory_id=theory_id,
            display_name=self._theory_names.get(theory_id, theory_name),
            detail_level=detail_level,
            content=content,
            constructs=constructs,
            maturity=maturity,
            atlas_status=atlas_status,
            guide_path=str(guide_path),
            metadata=metadata,
        )

    def get_theory_metadata(self, theory_id: str) -> Optional[Dict[str, Any]]:
        """Get structured theory metadata from JSON."""
        return self._load_metadata(theory_id)

    def get_theory_summary(self, theory_name: str) -> Optional[Dict[str, Any]]:
        """Get combined guide + metadata for tooltip/popover display."""
        guide = self.get_guide(theory_name, detail_level="quick")
        if not guide:
            return None

        return {
            "theory_id": guide.theory_id,
            "display_name": guide.display_name,
            "content": guide.content,
            "constructs": guide.constructs,
            "maturity": guide.maturity,
            "atlas_status": guide.atlas_status,
            "metadata": guide.metadata,
        }

    def search_theories(self, query: str, max_results: int = 10) -> List[TheoryGuideResult]:
        """
        Fuzzy search across all theory names, aliases, constructs.

        Args:
            query: Search term
            max_results: Maximum results to return

        Returns:
            List of matching TheoryGuideResult objects (quick level)
        """
        query_lower = query.lower()
        matches = []
        scored = []

        for theory_id, display_name in self._theory_names.items():
            score = 0.0

            # Match on display name
            if query_lower in display_name.lower():
                score += 10
            ratio = SequenceMatcher(None, query_lower, display_name.lower()).ratio()
            score += ratio * 5

            # Match on aliases
            for alias in self._alias_map:
                if alias in query_lower or query_lower in alias:
                    score += 3

            # Match on constructs from metadata
            metadata = self._load_metadata(theory_id)
            if metadata:
                for construct in metadata.get("constructs", []):
                    construct_name = construct.get("construct_name", "").lower()
                    if query_lower in construct_name or construct_name in query_lower:
                        score += 2

            if score > 0:
                scored.append((theory_id, score))

        # Sort by score and get top results
        scored.sort(key=lambda x: x[1], reverse=True)

        for theory_id, _ in scored[:max_results]:
            guide = self.get_guide(theory_id, detail_level="quick")
            if guide:
                matches.append(guide)

        return matches

    def list_available_guides(self) -> List[str]:
        """Return list of theory names with available guides."""
        return sorted(self._theory_names.values())

    def get_tooltip_html(self, theory_name: str) -> Optional[str]:
        """Return compact HTML for tooltip/popover display in visualizations."""
        guide = self.get_guide(theory_name, detail_level="quick")
        if not guide:
            return None

        # Build minimal HTML
        constructs_html = ""
        if guide.constructs:
            constructs_html = f"<p><strong>Constructs:</strong> {', '.join(guide.constructs[:3])}</p>"

        status_badge = ""
        if guide.atlas_status:
            status_badge = f'<span style="background: #f0f0f0; padding: 2px 6px; border-radius: 3px; font-size: 0.8em;">{guide.atlas_status}</span>'

        html = f"""
        <div style="max-width: 300px; font-family: sans-serif; font-size: 0.9em; line-height: 1.4;">
            <h4 style="margin: 0 0 8px 0; color: #2e5d8a;">{guide.display_name}</h4>
            {status_badge}
            <p style="margin: 8px 0; color: #666;">{guide.content[:150]}...</p>
            {constructs_html}
        </div>
        """
        return html
