"""
Article Eater - PDF Extraction Pipeline
========================================

Extracts structured information from CNFA research papers:
- Metadata (title, authors, year)
- Theories referenced
- Methods (temporal parameters, effect sizes)
- Findings (supports/contradicts theories)
- Claims suitable for epistemic state
"""

import pdfplumber
import re
import json
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class TemporalParameter:
    """Extracted temporal parameter from a study."""
    parameter_type: str  # onset, duration, peak, decay
    value: float
    unit: str  # seconds, minutes, hours, days
    context: str  # What manipulation/outcome
    confidence: float = 0.7  # How confident in extraction
    source_text: str = ""


@dataclass
class EffectSize:
    """Extracted effect size from a study."""
    outcome: str
    comparison: str
    effect_type: str  # d, r, eta_squared, etc.
    value: float
    ci_lower: Optional[float] = None
    ci_upper: Optional[float] = None
    n: Optional[int] = None
    p_value: Optional[float] = None
    source_text: str = ""


@dataclass
class TheoryReference:
    """Reference to a theory in the paper."""
    theory_name: str  # ART, SRT, Biophilia, etc.
    relation: str  # supports, contradicts, tests, extends, cites
    strength: float = 0.5  # How strongly related
    context: str = ""


@dataclass
class ExtractedFinding:
    """A finding extracted from the paper."""
    content: str
    finding_type: str  # main, secondary, null, unexpected
    theories_relevant: List[str] = field(default_factory=list)
    effect_sizes: List[EffectSize] = field(default_factory=list)
    temporal_params: List[TemporalParameter] = field(default_factory=list)
    confidence: float = 0.7


@dataclass
class PaperMetadata:
    """
    Bibliographic metadata for a paper, enriched from Semantic Scholar / CrossRef.

    This is the canonical citation metadata block used across the system:
    ExtractedPaper, ClaimV2, PaperIntegrationEvent, and setup() all reference it.
    Fields populated either from PDF extraction or from API enrichment.
    """
    doi: str = ""
    title: str = ""
    authors: List[str] = field(default_factory=list)
    year: Optional[int] = None
    journal: str = ""                           # venue / journal name
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    publisher: Optional[str] = None

    # Citation graph (from Semantic Scholar)
    citation_count: Optional[int] = None
    influential_citation_count: Optional[int] = None
    references: List[str] = field(default_factory=list)   # DOIs this paper cites
    cited_by: List[str] = field(default_factory=list)      # DOIs citing this paper
    semantic_scholar_id: Optional[str] = None              # S2 corpus ID

    # Enrichment tracking
    enriched: bool = False                      # True after API enrichment
    enriched_at: Optional[str] = None           # ISO timestamp of enrichment
    enrichment_source: Optional[str] = None     # "semantic_scholar" | "crossref"

    def to_dict(self) -> Dict[str, Any]:
        return {
            'doi': self.doi,
            'title': self.title,
            'authors': self.authors,
            'year': self.year,
            'journal': self.journal,
            'volume': self.volume,
            'issue': self.issue,
            'pages': self.pages,
            'publisher': self.publisher,
            'citation_count': self.citation_count,
            'influential_citation_count': self.influential_citation_count,
            'references': self.references,
            'cited_by': self.cited_by,
            'semantic_scholar_id': self.semantic_scholar_id,
            'enriched': self.enriched,
            'enriched_at': self.enriched_at,
            'enrichment_source': self.enrichment_source,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'PaperMetadata':
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class ExtractedPaper:
    """Complete extraction from a paper."""
    filepath: str
    title: str = ""
    authors: List[str] = field(default_factory=list)
    year: Optional[int] = None
    journal: str = ""
    doi: str = ""

    # Paper type
    paper_type: str = ""  # empirical, review, meta-analysis, theoretical

    # Bibliographic metadata (enriched from Semantic Scholar / CrossRef)
    paper_metadata: Optional[PaperMetadata] = None

    # Theories
    theories_referenced: List[TheoryReference] = field(default_factory=list)

    # Methods
    sample_size: Optional[int] = None
    study_design: str = ""  # RCT, within-subjects, between-subjects, etc.
    exposure_type: str = ""  # nature, indoor, VR, etc.
    exposure_duration: Optional[TemporalParameter] = None
    outcomes: List[str] = field(default_factory=list)

    # Findings
    findings: List[ExtractedFinding] = field(default_factory=list)
    effect_sizes: List[EffectSize] = field(default_factory=list)
    temporal_parameters: List[TemporalParameter] = field(default_factory=list)

    # Raw text for further analysis
    abstract: str = ""
    full_text: str = ""

    # Extraction metadata
    extraction_date: str = field(default_factory=lambda: datetime.now().isoformat())
    extraction_confidence: float = 0.5

    def to_dict(self) -> Dict[str, Any]:
        return {
            'filepath': self.filepath,
            'title': self.title,
            'authors': self.authors,
            'year': self.year,
            'journal': self.journal,
            'doi': self.doi,
            'paper_type': self.paper_type,
            'paper_metadata': self.paper_metadata.to_dict() if self.paper_metadata else None,
            'theories_referenced': [
                {'name': t.theory_name, 'relation': t.relation, 'strength': t.strength}
                for t in self.theories_referenced
            ],
            'sample_size': self.sample_size,
            'study_design': self.study_design,
            'n_findings': len(self.findings),
            'n_effect_sizes': len(self.effect_sizes),
            'n_temporal_params': len(self.temporal_parameters)
        }


class PDFExtractor:
    """Extract structured information from CNFA research papers."""
    
    # Theory detection patterns
    THEORY_PATTERNS = {
        'ART': [
            r'attention restoration theory',
            r'ART\b',
            r'Kaplan(?:\s+and\s+Kaplan)?.*attention',
            r'directed attention fatigue',
            r'soft fascination',
            r'restorative environment',
            r'being away',
            r'extent.*coherence',
            r'compatibility'
        ],
        'SRT': [
            r'stress recovery theory',
            r'SRT\b',
            r'Ulrich.*stress',
            r'psychophysiological stress recovery',
            r'autonomic stress',
            r'affective response',
            r'unthreatening natural',
        ],
        'Biophilia': [
            r'biophilia',
            r'biophilic',
            r'Wilson.*nature',
            r'innate.*nature',
            r'evolutionary.*preference',
            r'savanna hypothesis',
            r'prospect.*refuge'
        ],
        'Perceptual_Fluency': [
            r'perceptual fluency',
            r'processing fluency',
            r'ease of processing',
            r'visual complexity',
            r'fractal',
            r'golden ratio'
        ],
        'Predictive_Processing': [
            r'predictive processing',
            r'predictive coding',
            r'prediction error',
            r'free energy',
            r'active inference'
        ],
        'Embodied_Cognition': [
            r'embodied cognition',
            r'enactivism',
            r'4E cognition',
            r'affordance',
            r'action-perception'
        ]
    }
    
    # Temporal parameter patterns
    TEMPORAL_PATTERNS = [
        # Duration patterns
        (r'(\d+)[\s-]*(minute|min|minutes)', 'duration', 'minutes'),
        (r'(\d+)[\s-]*(hour|hr|hours)', 'duration', 'hours'),
        (r'(\d+)[\s-]*(second|sec|seconds)', 'duration', 'seconds'),
        (r'(\d+)[\s-]*(day|days)', 'duration', 'days'),
        # Onset/peak patterns
        (r'within\s+(\d+)\s*(min|hour|second)', 'onset', None),
        (r'after\s+(\d+)\s*(min|hour|second)', 'onset', None),
        (r'peak(?:ed)?\s+(?:at\s+)?(\d+)\s*(min|hour)', 'peak', None),
        # Duration exposure patterns
        (r'(\d+)[\s-]*(min|minute).*(?:walk|exposure|session)', 'exposure_duration', 'minutes'),
    ]
    
    # Effect size patterns
    EFFECT_PATTERNS = [
        # Cohen's d
        (r"[Cc]ohen'?s?\s*d\s*[=:]\s*([-]?\d+\.?\d*)", 'd'),
        (r'\bd\s*[=:]\s*([-]?\d+\.?\d*)', 'd'),
        (r'effect\s+size.*?d\s*[=:]\s*([-]?\d+\.?\d*)', 'd'),
        # Eta squared
        (r'[ηn]²?\s*[=:]\s*(0?\.\d+)', 'eta_squared'),
        (r'eta[\s-]*squared\s*[=:]\s*(0?\.\d+)', 'eta_squared'),
        (r'partial\s+[ηn]²?\s*[=:]\s*(0?\.\d+)', 'partial_eta_squared'),
        # Correlation
        (r'\br\s*[=:]\s*([-]?0?\.\d+)', 'r'),
        (r'correlation.*?r\s*[=:]\s*([-]?0?\.\d+)', 'r'),
        # F statistic
        (r'F\s*\(\s*\d+\s*,\s*\d+\s*\)\s*[=:]\s*(\d+\.?\d*)', 'F'),
        # t statistic  
        (r't\s*\(\s*\d+\s*\)\s*[=:]\s*([-]?\d+\.?\d*)', 't'),
        # p value
        (r'p\s*[<>=]\s*(0?\.\d+)', 'p'),
        (r'p\s*[<>=]\s*\.(\d+)', 'p'),
    ]
    
    def __init__(self):
        self.papers: List[ExtractedPaper] = []
    
    def extract_from_pdf(self, filepath: str) -> ExtractedPaper:
        """Extract structured information from a PDF."""
        paper = ExtractedPaper(filepath=filepath)
        
        try:
            with pdfplumber.open(filepath) as pdf:
                # Extract full text
                full_text_parts = []
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        full_text_parts.append(text)
                
                paper.full_text = "\n\n".join(full_text_parts)
                
                # Extract metadata from first page
                if full_text_parts:
                    self._extract_metadata(paper, full_text_parts[0])
                
                # Extract abstract
                paper.abstract = self._extract_abstract(paper.full_text)
                
                # Detect theories
                paper.theories_referenced = self._detect_theories(paper.full_text)
                
                # Classify paper type
                paper.paper_type = self._classify_paper_type(paper.full_text)
                
                # Extract temporal parameters
                paper.temporal_parameters = self._extract_temporal_params(paper.full_text)
                
                # Extract effect sizes
                paper.effect_sizes = self._extract_effect_sizes(paper.full_text)
                
                # Extract sample size
                paper.sample_size = self._extract_sample_size(paper.full_text)
                
                # Generate findings
                paper.findings = self._generate_findings(paper)
                
                # Calculate extraction confidence
                paper.extraction_confidence = self._calculate_confidence(paper)
                
        except Exception as e:
            logger.error(f"Error extracting from {filepath}: {e}")
            paper.extraction_confidence = 0.1
        
        self.papers.append(paper)
        return paper
    
    def _extract_metadata(self, paper: ExtractedPaper, first_page: str) -> None:
        """Extract title, authors, year from first page."""
        lines = first_page.split('\n')
        
        # Title is usually one of the first substantial lines
        for line in lines[:10]:
            line = line.strip()
            if len(line) > 30 and not re.match(r'^\d', line):
                if not any(x in line.lower() for x in ['journal', 'doi', 'received', 'accepted', '@']):
                    paper.title = line
                    break
        
        # Year
        year_match = re.search(r'\b(20\d{2}|19\d{2})\b', first_page)
        if year_match:
            paper.year = int(year_match.group(1))
        
        # DOI
        doi_match = re.search(r'(10\.\d{4,}/[^\s]+)', first_page)
        if doi_match:
            paper.doi = doi_match.group(1)
    
    def _extract_abstract(self, text: str) -> str:
        """Extract abstract section."""
        patterns = [
            r'Abstract[:\s]*\n?(.*?)(?=\n\s*(?:Keywords|Introduction|1\.|Background))',
            r'ABSTRACT[:\s]*\n?(.*?)(?=\n\s*(?:KEYWORDS|INTRODUCTION|1\.))',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                abstract = match.group(1).strip()
                # Clean up
                abstract = re.sub(r'\s+', ' ', abstract)
                return abstract[:2000]  # Limit length
        
        return ""
    
    def _detect_theories(self, text: str) -> List[TheoryReference]:
        """Detect which theories are referenced and how."""
        theories = []
        text_lower = text.lower()
        
        for theory_name, patterns in self.THEORY_PATTERNS.items():
            count = 0
            contexts = []
            
            for pattern in patterns:
                matches = re.findall(pattern, text_lower)
                count += len(matches)
                
                # Get context around matches
                for match in re.finditer(pattern, text_lower):
                    start = max(0, match.start() - 100)
                    end = min(len(text_lower), match.end() + 100)
                    contexts.append(text_lower[start:end])
            
            if count > 0:
                # Determine relation based on context
                relation = 'cites'
                if any('test' in c or 'examin' in c or 'investigat' in c for c in contexts):
                    relation = 'tests'
                if any('support' in c or 'confirm' in c or 'consistent' in c for c in contexts):
                    relation = 'supports'
                if any('contradict' in c or 'inconsistent' in c or 'failed' in c for c in contexts):
                    relation = 'contradicts'
                
                # Strength based on frequency
                strength = min(0.9, 0.3 + count * 0.1)
                
                theories.append(TheoryReference(
                    theory_name=theory_name,
                    relation=relation,
                    strength=strength,
                    context=contexts[0] if contexts else ""
                ))
        
        return theories
    
    def _classify_paper_type(self, text: str) -> str:
        """Classify paper as empirical, review, meta-analysis, or theoretical."""
        text_lower = text.lower()
        
        # Meta-analysis indicators
        if any(x in text_lower for x in ['meta-analysis', 'meta analysis', 'pooled effect', 'forest plot']):
            return 'meta-analysis'
        
        # Review indicators
        if any(x in text_lower for x in ['systematic review', 'literature review', 'scoping review']):
            return 'review'
        
        # Empirical indicators
        if any(x in text_lower for x in ['participants', 'subjects', 'n =', 'sample', 'experiment']):
            if any(x in text_lower for x in ['method', 'procedure', 'measure', 'anova', 't-test']):
                return 'empirical'
        
        # Theoretical
        if any(x in text_lower for x in ['theoretical framework', 'propose', 'model', 'hypothesis']):
            return 'theoretical'
        
        return 'unknown'
    
    def _extract_temporal_params(self, text: str) -> List[TemporalParameter]:
        """Extract temporal parameters from text."""
        params = []
        
        for pattern, param_type, default_unit in self.TEMPORAL_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                try:
                    value = float(match.group(1))
                    
                    # Determine unit
                    unit = default_unit
                    if len(match.groups()) > 1:
                        unit_match = match.group(2).lower()
                        if 'min' in unit_match:
                            unit = 'minutes'
                        elif 'hour' in unit_match or 'hr' in unit_match:
                            unit = 'hours'
                        elif 'sec' in unit_match:
                            unit = 'seconds'
                        elif 'day' in unit_match:
                            unit = 'days'
                    
                    # Get context
                    start = max(0, match.start() - 50)
                    end = min(len(text), match.end() + 50)
                    context = text[start:end]
                    
                    params.append(TemporalParameter(
                        parameter_type=param_type,
                        value=value,
                        unit=unit or 'unknown',
                        context=context,
                        source_text=match.group(0)
                    ))
                except (ValueError, IndexError):
                    continue
        
        return params
    
    def _extract_effect_sizes(self, text: str) -> List[EffectSize]:
        """Extract effect sizes from text."""
        effects = []
        
        for pattern, effect_type in self.EFFECT_PATTERNS:
            for match in re.finditer(pattern, text):
                try:
                    value = float(match.group(1))
                    
                    # Fix p-values that were captured without leading 0
                    if effect_type == 'p' and value > 1:
                        value = value / (10 ** len(str(int(value))))
                    
                    # Get context for outcome/comparison
                    start = max(0, match.start() - 100)
                    end = min(len(text), match.end() + 50)
                    context = text[start:end]
                    
                    effects.append(EffectSize(
                        outcome=context[:50],
                        comparison="",
                        effect_type=effect_type,
                        value=value,
                        source_text=match.group(0)
                    ))
                except (ValueError, IndexError):
                    continue
        
        return effects
    
    def _extract_sample_size(self, text: str) -> Optional[int]:
        """Extract sample size from text."""
        patterns = [
            r'[Nn]\s*[=:]\s*(\d+)',
            r'(\d+)\s*participants',
            r'(\d+)\s*subjects',
            r'sample\s+(?:size\s+)?(?:of\s+)?(\d+)',
        ]
        
        sizes = []
        for pattern in patterns:
            for match in re.finditer(pattern, text):
                try:
                    n = int(match.group(1))
                    if 5 < n < 10000:  # Reasonable range
                        sizes.append(n)
                except ValueError:
                    continue
        
        if sizes:
            # Return mode or max
            return max(set(sizes), key=sizes.count)
        return None
    
    def _generate_findings(self, paper: ExtractedPaper) -> List[ExtractedFinding]:
        """Generate findings from extracted information."""
        findings = []
        
        # Main finding from abstract
        if paper.abstract:
            findings.append(ExtractedFinding(
                content=paper.abstract[:500],
                finding_type='main',
                theories_relevant=[t.theory_name for t in paper.theories_referenced],
                effect_sizes=paper.effect_sizes[:3],
                confidence=0.7
            ))
        
        return findings
    
    def _calculate_confidence(self, paper: ExtractedPaper) -> float:
        """Calculate extraction confidence score."""
        score = 0.3  # Base
        
        if paper.title:
            score += 0.1
        if paper.year:
            score += 0.1
        if paper.abstract:
            score += 0.1
        if paper.theories_referenced:
            score += 0.1
        if paper.paper_type != 'unknown':
            score += 0.1
        if paper.effect_sizes:
            score += 0.1
        if paper.temporal_parameters:
            score += 0.1
        
        return min(0.95, score)
    
    def batch_extract(self, filepaths: List[str]) -> List[ExtractedPaper]:
        """Extract from multiple PDFs."""
        papers = []
        for fp in filepaths:
            paper = self.extract_from_pdf(fp)
            papers.append(paper)
            print(f"Extracted: {paper.title[:50]}... (conf={paper.extraction_confidence:.2f})")
        return papers
    
    def summary(self) -> Dict[str, Any]:
        """Summarize extracted papers."""
        if not self.papers:
            return {}
        
        theory_counts = {}
        for paper in self.papers:
            for t in paper.theories_referenced:
                theory_counts[t.theory_name] = theory_counts.get(t.theory_name, 0) + 1
        
        return {
            'n_papers': len(self.papers),
            'paper_types': {pt: sum(1 for p in self.papers if p.paper_type == pt) 
                          for pt in ['empirical', 'review', 'meta-analysis', 'theoretical', 'unknown']},
            'theory_references': theory_counts,
            'total_effect_sizes': sum(len(p.effect_sizes) for p in self.papers),
            'total_temporal_params': sum(len(p.temporal_parameters) for p in self.papers),
            'avg_confidence': sum(p.extraction_confidence for p in self.papers) / len(self.papers)
        }


if __name__ == "__main__":
    from pathlib import Path
    
    pdf_dir = Path("/home/claude/article_eater/data/pdfs")
    
    extractor = PDFExtractor()
    
    pdfs = list(pdf_dir.glob("*.pdf"))
    print(f"Found {len(pdfs)} PDFs")
    
    for pdf in pdfs[:5]:  # Process first 5
        paper = extractor.extract_from_pdf(str(pdf))
        print(f"\n{'='*60}")
        print(f"Title: {paper.title[:60]}...")
        print(f"Year: {paper.year}")
        print(f"Type: {paper.paper_type}")
        print(f"Theories: {[t.theory_name for t in paper.theories_referenced]}")
        print(f"Effect sizes: {len(paper.effect_sizes)}")
        print(f"Temporal params: {len(paper.temporal_parameters)}")
        print(f"Confidence: {paper.extraction_confidence:.2f}")
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(json.dumps(extractor.summary(), indent=2))
