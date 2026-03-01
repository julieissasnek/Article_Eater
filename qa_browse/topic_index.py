"""
TopicIndex — Data layer for the QA Browse System.

Loads all templates, molecules, MASTER_DOC sections, QA caches,
and citation data into a unified searchable index.

Usage:
    idx = TopicIndex()
    results = idx.search("biophilia")
    topic = idx.get_topic("VIEW1")
    section = idx.get_master_doc_section(48)
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ── Domain and Path Configuration (from config) ──

from .config import (
    PROJECT_ROOT,
    DATA_DIR,
    TEMPLATES_DIR,
    MOLECULES_DIR,
    QA_CACHE_DIR,
    ATTRIBUTES_DIR,
    EXTRACTIONS_DIR,
    MASTER_DOC_CANDIDATES,
    DOMAIN_CONFIG,
    TEMPLATE_DOMAIN_MAP,
    BRIDGE_WARRANT_LABELS,
)


# ── Data Classes ──

@dataclass
class MasterDocSection:
    """A parsed section from the MASTER_DOC."""
    section_num: str          # e.g. "48", "48.6", "50.3"
    title: str                # e.g. "The Core Credence Formula"
    level: int                # heading level: 2=##, 3=###
    content: str              # full markdown content
    executive_summary: str = ""   # extracted if present
    subsections: List[str] = field(default_factory=list)  # sub-section numbers
    part: str = ""            # e.g. "PART IV"
    start_line: int = 0


@dataclass
class TemplateData:
    """A loaded template from data/templates/.

    Fields map to the standard template JSON schema (ae.template.v2).
    The ``raw`` field preserves the original JSON for any fields not
    explicitly modelled here.
    """
    template_id: str
    display_id: str
    name: str
    panel: str
    confidence: float
    bridge_prior: float
    mechanism_chain: List[str]
    calibrated_parameters: Dict[str, Any]
    population_modifiers: Dict[str, Any]
    key_references: List[Any]
    interaction_templates: List[Any]
    cross_template_interactions: Dict[str, str]
    building_types: List[Any]
    architectural_modifiers: Dict[str, Any]
    status: str
    maturity: str
    tier: str
    bridge_warrant: str
    t1_frameworks: List[str]
    t1_5_parent_theories: Any
    panel_docs: List[str]
    year: Optional[int] = None
    journal: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MoleculeData:
    """A loaded molecule from data/molecules/.

    Molecules group related templates into explanatory units at the
    T1.5 level (e.g. Biophilia, ART, SRT, Prospect-Refuge).
    """
    molecule_id: str
    name: str
    short_description: str
    components: List[Dict[str, Any]]
    constituent_templates: List[str]
    interaction_graph: Dict[str, Any]
    framework_ids: List[str]
    domain: str = ""
    molecule_type: str = ""
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchResult:
    """A search result entry returned by ``TopicIndex.search()``."""
    result_type: str    # "template", "molecule", "section", "paper"
    id: str
    title: str
    snippet: str
    score: float
    confidence: Optional[float] = None
    domain: Optional[str] = None


class TopicIndex:
    """Central searchable index for all QA content."""

    def __init__(self):
        self.templates: Dict[str, TemplateData] = {}
        self.molecules: Dict[str, MoleculeData] = {}
        self.master_sections: Dict[str, MasterDocSection] = {}
        self.qa_caches: Dict[str, Dict] = {}
        self.domain_attributes: Dict[str, Dict] = {}
        self.citation_graph: Dict[str, Any] = {}
        self.paper_index: Dict[str, Dict] = {}  # DOI -> basic metadata

        # Derived indexes
        self._search_corpus: List[Tuple[str, str, str, str]] = []  # (type, id, title, text)
        self._template_by_domain: Dict[str, List[str]] = defaultdict(list)
        self._molecule_templates: Dict[str, List[str]] = defaultdict(list)

        self._load_all()

    def _load_all(self):
        """Load all data sources."""
        self._load_templates()
        self._load_molecules()
        self._load_master_doc()
        self._load_qa_caches()
        self._load_attributes()
        self._load_citation_graph()
        self._build_search_index()

    # ── Loaders ──

    def _load_templates(self):
        """Load all template JSONs."""
        if not TEMPLATES_DIR.exists():
            return
        for fpath in sorted(TEMPLATES_DIR.glob("*.json")):
            try:
                data = json.loads(fpath.read_text())
                tid = data.get("template_id", fpath.stem)
                did = data.get("display_id", fpath.stem)

                t = TemplateData(
                    template_id=tid,
                    display_id=did,
                    name=data.get("name", ""),
                    panel=data.get("panel", ""),
                    confidence=data.get("confidence", 0.0) or 0.0,
                    bridge_prior=data.get("bridge_prior", 0.0) or 0.0,
                    mechanism_chain=data.get("mechanism_chain", []),
                    calibrated_parameters=data.get("calibrated_parameters", {}),
                    population_modifiers=data.get("population_modifiers", {}),
                    key_references=data.get("key_references", []),
                    interaction_templates=data.get("interaction_templates", []),
                    cross_template_interactions=data.get("cross_template_interactions", {}),
                    building_types=data.get("building_types", []),
                    architectural_modifiers=data.get("architectural_modifiers", {}),
                    status=data.get("status", ""),
                    maturity=data.get("maturity", ""),
                    tier=data.get("tier", ""),
                    bridge_warrant=data.get("bridge_warrant", ""),
                    t1_frameworks=data.get("t1_frameworks", []),
                    t1_5_parent_theories=data.get("t1_5_parent_theories"),
                    panel_docs=data.get("panel_docs", []),
                    raw=data,
                )

                self.templates[did] = t
                # Also index by template_id
                if tid != did:
                    self.templates[tid] = t

                # Domain classification
                domain = self._classify_domain(tid)
                if domain:
                    self._template_by_domain[domain].append(did)

            except Exception:
                pass

    def _classify_domain(self, template_id: str) -> Optional[str]:
        """Classify a template into a domain based on its ID prefix."""
        for prefix, domain in sorted(TEMPLATE_DOMAIN_MAP.items(), key=lambda x: -len(x[0])):
            if template_id.startswith(prefix):
                return domain
        # Fallback: check T-series by looking at the template name
        t = self.templates.get(template_id)
        if t and t.name:
            name_lower = t.name.lower()
            for domain, cfg in DOMAIN_CONFIG.items():
                if domain in name_lower:
                    return domain
        return None

    def _load_molecules(self):
        """Load all molecule JSONs."""
        if not MOLECULES_DIR.exists():
            return
        for fpath in sorted(MOLECULES_DIR.glob("*.json")):
            try:
                data = json.loads(fpath.read_text())
                mid = data.get("molecule_id", fpath.stem)

                mol = MoleculeData(
                    molecule_id=mid,
                    name=data.get("name", ""),
                    short_description=data.get("short_description", ""),
                    components=data.get("components", []),
                    constituent_templates=data.get("constituent_templates", []),
                    interaction_graph=data.get("interaction_graph", {}),
                    framework_ids=data.get("framework_ids", []),
                    domain=data.get("domain", ""),
                    molecule_type=data.get("molecule_type", ""),
                    raw=data,
                )
                self.molecules[mid] = mol

                # Map molecule → templates
                for tid in mol.constituent_templates:
                    self._molecule_templates[mid].append(tid)

            except Exception:
                pass

    def _load_master_doc(self):
        """Parse MASTER_DOC into sections by heading."""
        master_path = None
        for candidate in MASTER_DOC_CANDIDATES:
            if candidate.exists():
                master_path = candidate
                break

        if not master_path:
            return

        text = master_path.read_text(errors="replace")
        lines = text.split("\n")

        current_section = None
        current_part = ""
        content_lines = []

        for i, line in enumerate(lines):
            # Track parts
            part_match = re.match(r"^## PART\s+([IVXLC]+):", line)
            if part_match:
                current_part = f"PART {part_match.group(1)}"

            # Match section headings: ## §N. Title or ### N.M Title
            sec_match = re.match(r"^(#{2,3})\s+(?:§\s*)?(\d+(?:\.\d+)?[a-z]?)\s*[.:]\s*(.*)", line)
            if sec_match:
                # Save previous section
                if current_section:
                    current_section.content = "\n".join(content_lines).strip()
                    # Extract executive summary if present
                    es_match = re.search(
                        r"### Executive Summary\s*\n+(.*?)(?=\n###|\n---|\Z)",
                        current_section.content, re.DOTALL
                    )
                    if es_match:
                        current_section.executive_summary = es_match.group(1).strip()
                    self.master_sections[current_section.section_num] = current_section

                level = len(sec_match.group(1))
                sec_num = sec_match.group(2)
                title = sec_match.group(3).strip()

                current_section = MasterDocSection(
                    section_num=sec_num,
                    title=title,
                    level=level,
                    content="",
                    part=current_part,
                    start_line=i + 1,
                )
                content_lines = [line]
            elif current_section:
                content_lines.append(line)

        # Save last section
        if current_section:
            current_section.content = "\n".join(content_lines).strip()
            self.master_sections[current_section.section_num] = current_section

    def _load_qa_caches(self):
        """Load QA cache files."""
        if not QA_CACHE_DIR.exists():
            return
        for fpath in QA_CACHE_DIR.glob("*_QA.json"):
            try:
                data = json.loads(fpath.read_text())
                mid = data.get("molecule_id", fpath.stem.replace("_QA", ""))
                self.qa_caches[mid] = data
            except Exception:
                pass

    def _load_attributes(self):
        """Load domain attribute definitions."""
        if not ATTRIBUTES_DIR.exists():
            return
        for fpath in ATTRIBUTES_DIR.glob("AD_*.json"):
            try:
                data = json.loads(fpath.read_text())
                self.domain_attributes[data.get("domain_id", fpath.stem)] = data
            except Exception:
                pass

    def _load_citation_graph(self):
        """Load citation graph for reference linking."""
        graph_path = EXTRACTIONS_DIR / "citation_graph.json"
        if graph_path.exists():
            try:
                self.citation_graph = json.loads(graph_path.read_text())
            except Exception:
                pass

        # Build lightweight paper index from extraction files
        if EXTRACTIONS_DIR.exists():
            for fpath in EXTRACTIONS_DIR.glob("10.*.json"):
                try:
                    data = json.loads(fpath.read_text())
                    doi = data.get("doi", fpath.stem.replace("_", "/", 1))
                    pm = data.get("paper_metadata", {})
                    self.paper_index[doi] = {
                        "title": pm.get("title") or pm.get("crossref_title") or data.get("title", ""),
                        "year": pm.get("year") or data.get("year"),
                        "authors": pm.get("authors", [])[:3],
                        "journal": pm.get("journal") or pm.get("crossref_journal"),
                        "citation_count": pm.get("citation_count") or pm.get("crossref_citation_count"),
                        "doi": doi,
                    }
                except Exception:
                    pass

    # ── Search ──

    def _build_search_index(self):
        """Build a flat search corpus for simple text matching."""
        self._search_corpus = []

        # Templates
        for tid, t in self.templates.items():
            if tid != t.display_id:
                continue  # Skip alias entries
            text = f"{t.name} {t.template_id} {t.display_id} {t.panel} "
            text += " ".join(str(s) for s in t.mechanism_chain[:3])
            refs_str = [
                r.get("doi", str(r)) if isinstance(r, dict) else str(r)
                for r in t.key_references[:3]
            ]
            text += " " + " ".join(refs_str)
            self._search_corpus.append(("template", tid, t.name, text))

        # Molecules
        for mid, m in self.molecules.items():
            text = f"{m.name} {m.short_description} {m.molecule_id}"
            self._search_corpus.append(("molecule", mid, m.name, text))

        # Master doc sections
        for snum, sec in self.master_sections.items():
            text = f"{sec.title} {sec.executive_summary[:300]}"
            self._search_corpus.append(("section", snum, f"§{snum}: {sec.title}", text))

        # Papers (top 200 by citation count)
        sorted_papers = sorted(
            self.paper_index.items(),
            key=lambda x: x[1].get("citation_count") or 0,
            reverse=True
        )
        for doi, p in sorted_papers[:200]:
            text = f"{p.get('title', '')} {' '.join(p.get('authors', []))} {p.get('journal', '')}"
            title = p.get("title", doi)
            self._search_corpus.append(("paper", doi, title, text))

    def search(self, query: str, limit: int = 20) -> List[SearchResult]:
        """Simple text search across all content."""
        if not query.strip():
            return []

        query_lower = query.lower()
        terms = query_lower.split()
        results = []

        for rtype, rid, title, text in self._search_corpus:
            text_lower = text.lower()
            title_lower = title.lower()

            # Score: exact phrase > all terms > partial
            score = 0
            if query_lower in title_lower:
                score += 10
            if query_lower in text_lower:
                score += 5
            term_hits = sum(1 for t in terms if t in text_lower)
            score += term_hits * 2

            if score > 0:
                # Build snippet
                snippet = ""
                if rtype == "template":
                    t = self.templates.get(rid)
                    if t:
                        snippet = t.mechanism_chain[0] if t.mechanism_chain else t.name
                        snippet = str(snippet)[:120]
                elif rtype == "molecule":
                    m = self.molecules.get(rid)
                    if m:
                        snippet = m.short_description[:120]
                elif rtype == "section":
                    sec = self.master_sections.get(rid)
                    if sec:
                        snippet = sec.executive_summary[:120] if sec.executive_summary else sec.title
                elif rtype == "paper":
                    p = self.paper_index.get(rid, {})
                    authors = ", ".join(p.get("authors", [])[:2])
                    snippet = f"{authors} ({p.get('year', '?')}) — {p.get('journal', '')}"

                conf = None
                domain = None
                if rtype == "template":
                    t = self.templates.get(rid)
                    if t:
                        conf = t.confidence
                        domain = self._classify_domain(t.template_id)

                results.append(SearchResult(
                    result_type=rtype,
                    id=rid,
                    title=title,
                    snippet=snippet,
                    score=score,
                    confidence=conf,
                    domain=domain,
                ))

        results.sort(key=lambda r: -r.score)
        return results[:limit]

    # ── Accessors ──

    def get_template(self, tid: str) -> Optional[TemplateData]:
        """Get a template by display_id or template_id."""
        return self.templates.get(tid)

    def get_molecule(self, mid: str) -> Optional[MoleculeData]:
        """Get a molecule by ID."""
        return self.molecules.get(mid)

    def get_master_doc_section(self, section_num: str) -> Optional[MasterDocSection]:
        """Get a parsed MASTER_DOC section."""
        return self.master_sections.get(str(section_num))

    def get_qa_cache(self, molecule_id: str) -> Optional[Dict]:
        """Get QA cache for a molecule (L1/L2/L3 summaries)."""
        return self.qa_caches.get(molecule_id)

    def get_domain_templates(self, domain: str) -> List[TemplateData]:
        """Get all templates in a domain."""
        tids = self._template_by_domain.get(domain, [])
        return [self.templates[tid] for tid in tids if tid in self.templates]

    def get_molecule_templates(self, molecule_id: str) -> List[TemplateData]:
        """Get all templates belonging to a molecule."""
        tids = self._molecule_templates.get(molecule_id, [])
        return [self.templates[tid] for tid in tids if tid in self.templates]

    def get_paper(self, doi: str) -> Optional[Dict]:
        """Get paper metadata by DOI."""
        return self.paper_index.get(doi)

    def get_related_templates(self, template_id: str) -> List[TemplateData]:
        """Get templates related via interaction_templates or cross_template_interactions."""
        t = self.get_template(template_id)
        if not t:
            return []

        related_ids = set()
        for it in t.interaction_templates:
            if isinstance(it, str):
                related_ids.add(it)
            elif isinstance(it, dict):
                related_ids.add(it.get("template_id", ""))

        for tid in t.cross_template_interactions:
            related_ids.add(tid)

        return [self.templates[tid] for tid in related_ids if tid in self.templates]

    # ── Stats ──

    def get_stats(self) -> Dict[str, Any]:
        """Get summary statistics."""
        unique_templates = set()
        for tid, t in self.templates.items():
            if tid == t.display_id:
                unique_templates.add(tid)

        return {
            "templates": len(unique_templates),
            "molecules": len(self.molecules),
            "master_doc_sections": len(self.master_sections),
            "qa_caches": len(self.qa_caches),
            "papers": len(self.paper_index),
            "citation_edges": len(self.citation_graph.get("edges", [])),
            "domains": {
                domain: len(tids)
                for domain, tids in sorted(self._template_by_domain.items())
            },
        }


# Singleton instance
_index: Optional[TopicIndex] = None


def get_index() -> TopicIndex:
    """Get or create the singleton TopicIndex."""
    global _index
    if _index is None:
        _index = TopicIndex()
    return _index
