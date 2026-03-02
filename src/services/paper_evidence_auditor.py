"""
Paper Evidence Auditor

Given a paper draft, automatically cross-references claims against ATLAS web-of-belief
and generates article search targets for evidence gaps.

This service is designed to be called whenever a paper is written—it provides
systematic feedback on what evidence is needed to support the paper's claims.

Usage:
    auditor = PaperEvidenceAuditor(db_path='ae.db')
    report = auditor.audit_paper('path/to/paper.md')
    targets = auditor.generate_search_targets(report)
    auditor.submit_to_pipeline(targets)

The output includes:
- Per-section evidence assessment (well-supported, partial, unsupported)
- Priority-ranked search targets
- Structured insertion into interpretation_space_suggestions table
"""

from dataclasses import dataclass, asdict, field
from typing import List, Dict, Optional, Tuple, Set
from datetime import datetime
from pathlib import Path
import sqlite3
import json
import re
from abc import ABC, abstractmethod

# ============================================================================
# Data Structures
# ============================================================================

@dataclass
class Claim:
    """An empirical or theoretical claim extracted from a paper."""
    claim_id: str
    section: str
    subsection: str
    claim_text: str
    claim_type: str  # FACTUAL, QUANTITATIVE, CAUSAL, COMPARATIVE
    evidence_keywords: List[str]
    evidence_confidence: float = 0.0  # Initially unknown

    def __hash__(self):
        return hash(self.claim_id)


@dataclass
class ClaimAssessment:
    """Assessment of a claim's support from ATLAS."""
    claim: Claim
    support_level: str  # WELL_SUPPORTED, PARTIALLY_SUPPORTED, UNSUPPORTED, CONTRADICTED
    atlas_beliefs: List[str] = field(default_factory=list)
    avg_warrant: float = 0.0
    confidence: float = 0.5
    notes: str = ""

    def to_dict(self):
        return {
            'claim_id': self.claim.claim_id,
            'section': self.claim.section,
            'claim_text': self.claim.claim_text,
            'support_level': self.support_level,
            'atlas_beliefs': self.atlas_beliefs,
            'avg_warrant': self.avg_warrant,
            'confidence': self.confidence,
            'notes': self.notes
        }


@dataclass
class SearchTarget:
    """An article search target to fill evidence gaps."""
    target_id: str
    section: str
    claim_id: str
    claim_summary: str
    search_query: str
    alternative_queries: List[str] = field(default_factory=list)
    expected_article_type: str = "empirical"  # empirical, meta-analysis, review, theoretical
    priority: str = "MEDIUM"
    priority_score: float = 0.5
    rationale: str = ""

    def to_dict(self):
        return asdict(self)


@dataclass
class EvidenceAuditReport:
    """Complete audit report for a paper."""
    paper_path: str
    paper_title: str
    audit_date: str
    total_claims: int
    assessments: List[ClaimAssessment] = field(default_factory=list)

    @property
    def well_supported(self) -> int:
        return sum(1 for a in self.assessments if a.support_level == "WELL_SUPPORTED")

    @property
    def partially_supported(self) -> int:
        return sum(1 for a in self.assessments if a.support_level == "PARTIALLY_SUPPORTED")

    @property
    def unsupported(self) -> int:
        return sum(1 for a in self.assessments if a.support_level == "UNSUPPORTED")

    @property
    def contradicted(self) -> int:
        return sum(1 for a in self.assessments if a.support_level == "CONTRADICTED")

    @property
    def overall_warrant(self) -> float:
        """Average warrant across all claims."""
        if not self.assessments:
            return 0.0
        return sum(a.avg_warrant for a in self.assessments) / len(self.assessments)

    def to_dict(self):
        return {
            'paper_path': self.paper_path,
            'paper_title': self.paper_title,
            'audit_date': self.audit_date,
            'total_claims': self.total_claims,
            'well_supported': self.well_supported,
            'partially_supported': self.partially_supported,
            'unsupported': self.unsupported,
            'contradicted': self.contradicted,
            'overall_warrant': self.overall_warrant,
            'assessments': [a.to_dict() for a in self.assessments]
        }


# ============================================================================
# Paper Parsing
# ============================================================================

class PaperParser(ABC):
    """Abstract base for paper format parsers."""

    @abstractmethod
    def parse_claims(self, paper_path: str) -> List[Claim]:
        """Extract claims from paper."""
        pass

    @abstractmethod
    def extract_title(self, paper_path: str) -> str:
        """Extract paper title."""
        pass


class MarkdownPaperParser(PaperParser):
    """Parser for Markdown paper drafts (like GOLDILOCKS_FULL_DRAFT)."""

    def parse_claims(self, paper_path: str) -> List[Claim]:
        """Extract claims from Markdown paper by identifying claim-like sentences."""
        with open(paper_path, 'r') as f:
            content = f.read()

        claims = []
        claim_id = 0

        # Split by sections (## or ###)
        section_pattern = r'^#+\s+(.+?)$'
        lines = content.split('\n')

        current_section = "introduction"
        current_subsection = ""

        for i, line in enumerate(lines):
            section_match = re.match(section_pattern, line)
            if section_match:
                section_text = section_match.group(1)
                # Parse section numbers if available
                current_section = section_text.split(":")[0].strip()
                current_subsection = section_text
                continue

            # Heuristic: claim-like sentences are often after colons, contain years/numbers, or reference studies
            if any(marker in line for marker in ["found", "showed", "demonstrates", "propose", "hypothesis", "effect size", "study"]):
                # Further filter to avoid trivial lines
                if len(line) > 50 and line.strip() and not line.startswith(">"):
                    # Determine claim type
                    claim_type = self._infer_claim_type(line)
                    keywords = self._extract_keywords(line)

                    claim = Claim(
                        claim_id=f"C{claim_id:03d}",
                        section=current_section,
                        subsection=current_subsection,
                        claim_text=line[:150].strip(),  # First 150 chars
                        claim_type=claim_type,
                        evidence_keywords=keywords
                    )
                    claims.append(claim)
                    claim_id += 1

        return claims

    def extract_title(self, paper_path: str) -> str:
        """Extract title from first H1."""
        with open(paper_path, 'r') as f:
            for line in f:
                match = re.match(r'^#\s+(.+?)$', line)
                if match:
                    return match.group(1)
        return "Untitled"

    def _infer_claim_type(self, line: str) -> str:
        """Infer claim type from sentence characteristics."""
        if any(word in line.lower() for word in ["study", "empirical", "data", "measured", "tested"]):
            if any(word in line for word in ["d =", "r =", "p <", "%", "R²"]):
                return "QUANTITATIVE"
            else:
                return "FACTUAL"
        elif any(word in line.lower() for word in ["more", "higher", "lower", "greater", "compared", "difference"]):
            return "COMPARATIVE"
        elif any(word in line.lower() for word in ["cause", "explain", "produce", "mechanism", "results in"]):
            return "CAUSAL"
        else:
            return "FACTUAL"

    def _extract_keywords(self, line: str) -> List[str]:
        """Extract keywords from claim sentence."""
        # Simple heuristic: extract capitalized sequences and quoted phrases
        keywords = []

        # Look for quoted phrases
        quoted = re.findall(r'"([^"]+)"', line)
        keywords.extend(quoted)

        # Look for proper nouns and author names
        proper_nouns = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', line)
        keywords.extend(proper_nouns[:5])  # Limit to 5

        # Add domain-relevant keywords
        domain_keywords = [
            "complexity", "preference", "stimulus", "arousal", "thermal", "acoustic",
            "fractal", "visual", "social", "inverted-U", "optimum", "optimal",
            "prediction error", "entropy", "aesthetic", "comfort", "fluency"
        ]
        for keyword in domain_keywords:
            if keyword.lower() in line.lower():
                keywords.append(keyword)

        return list(set(keywords))[:10]  # Return unique keywords, limit to 10


# ============================================================================
# ATLAS Belief Query
# ============================================================================

class AtlasBeliefQuerier:
    """Query ATLAS database for beliefs relevant to claims."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def find_supporting_beliefs(self, claim: Claim) -> Tuple[List[str], float]:
        """
        Query ATLAS for beliefs matching claim keywords.
        Returns (belief_ids, avg_credence).
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Build OR query for all keywords
            if not claim.evidence_keywords:
                return ([], 0.0)

            conditions = []
            for keyword in claim.evidence_keywords:
                conditions.append(f"content LIKE '%{keyword}%'")
                conditions.append(f"tags LIKE '%{keyword}%'")

            where_clause = " OR ".join(f"({cond})" for cond in conditions)

            query = f"""
            SELECT belief_id, credence_value
            FROM beliefs
            WHERE {where_clause}
            LIMIT 10
            """

            cursor.execute(query)
            results = cursor.fetchall()
            conn.close()

            if not results:
                return ([], 0.0)

            belief_ids = [r[0] for r in results]
            credences = [r[1] if r[1] is not None else 0.5 for r in results]
            avg_credence = sum(credences) / len(credences) if credences else 0.0

            return (belief_ids, avg_credence)

        except Exception as e:
            # Silent fail; database may not be populated
            return ([], 0.0)

    def assess_support_level(self, avg_credence: float, num_beliefs: int) -> Tuple[str, float]:
        """
        Heuristically determine support level from credence and belief count.
        Returns (support_level, confidence).
        """
        if avg_credence >= 0.65 and num_beliefs >= 2:
            return ("WELL_SUPPORTED", 0.85)
        elif avg_credence >= 0.45 or num_beliefs >= 1:
            return ("PARTIALLY_SUPPORTED", 0.65)
        else:
            return ("UNSUPPORTED", 0.75)


# ============================================================================
# Main Auditor Class
# ============================================================================

class PaperEvidenceAuditor:
    """
    Comprehensive paper evidence auditor.

    Usage:
        auditor = PaperEvidenceAuditor(db_path='ae.db')
        report = auditor.audit_paper('path/to/paper.md')
        targets = auditor.generate_search_targets(report)
        auditor.submit_to_pipeline(targets, db_path='ae.db')
    """

    def __init__(self, db_path: str, parser: Optional[PaperParser] = None):
        self.db_path = db_path
        self.parser = parser or MarkdownPaperParser()
        self.querier = AtlasBeliefQuerier(db_path)

    def audit_paper(self, paper_path: str) -> EvidenceAuditReport:
        """
        Full audit: parse paper, extract claims, assess against ATLAS.
        """
        # Extract basic metadata
        title = self.parser.extract_title(paper_path)
        audit_date = datetime.now().isoformat()

        # Extract claims
        claims = self.parser.parse_claims(paper_path)

        # Assess each claim
        assessments = []
        for claim in claims:
            beliefs, avg_credence = self.querier.find_supporting_beliefs(claim)
            support_level, confidence = self.querier.assess_support_level(
                avg_credence, len(beliefs)
            )

            assessment = ClaimAssessment(
                claim=claim,
                support_level=support_level,
                atlas_beliefs=beliefs,
                avg_warrant=avg_credence,
                confidence=confidence,
                notes=f"Found {len(beliefs)} ATLAS beliefs, avg credence {avg_credence:.2f}"
            )
            assessments.append(assessment)

        report = EvidenceAuditReport(
            paper_path=paper_path,
            paper_title=title,
            audit_date=audit_date,
            total_claims=len(claims),
            assessments=assessments
        )

        return report

    def generate_search_targets(self, report: EvidenceAuditReport) -> List[SearchTarget]:
        """
        Convert unsupported/partially-supported claims into search targets.
        """
        targets = []
        target_id = 0

        for assessment in report.assessments:
            if assessment.support_level in ["UNSUPPORTED", "PARTIALLY_SUPPORTED"]:
                claim = assessment.claim

                # Determine priority
                if assessment.support_level == "UNSUPPORTED":
                    priority = "HIGH"
                    priority_score = 0.90
                else:  # PARTIALLY_SUPPORTED
                    priority = "MEDIUM"
                    priority_score = 0.65

                # Adjust priority based on section importance
                if any(x in claim.section for x in ["2", "4", "5"]):  # Core sections
                    priority_score = min(0.95, priority_score + 0.05)
                elif any(x in claim.section for x in ["7", "8"]):  # Extension sections
                    priority_score = max(0.45, priority_score - 0.15)

                # Generate search queries
                queries = self._generate_search_queries(claim)

                target = SearchTarget(
                    target_id=f"ST{target_id:03d}",
                    section=claim.section,
                    claim_id=claim.claim_id,
                    claim_summary=claim.claim_text[:80],
                    search_query=queries[0] if queries else "unknown",
                    alternative_queries=queries[1:] if len(queries) > 1 else [],
                    expected_article_type=self._infer_article_type(claim),
                    priority=priority,
                    priority_score=priority_score,
                    rationale=f"Support {claim.claim_type.lower()} claim in section {claim.section}"
                )

                targets.append(target)
                target_id += 1

        return sorted(targets, key=lambda t: t.priority_score, reverse=True)

    def _generate_search_queries(self, claim: Claim) -> List[str]:
        """Generate search queries from claim keywords."""
        queries = []

        # Primary query: combine top keywords
        if len(claim.evidence_keywords) >= 2:
            primary = " ".join(claim.evidence_keywords[:3]) + " study"
            queries.append(primary)

        # Alternative queries with different phrasings
        if claim.claim_type == "QUANTITATIVE":
            queries.append(" ".join(claim.evidence_keywords[:2]) + " measurement")
            queries.append(" ".join(claim.evidence_keywords[:2]) + " meta-analysis")
        elif claim.claim_type == "COMPARATIVE":
            queries.append(" ".join(claim.evidence_keywords[:2]) + " comparison")
            queries.append(" ".join(claim.evidence_keywords[:2]) + " cross-cultural")
        elif claim.claim_type == "CAUSAL":
            queries.append(" ".join(claim.evidence_keywords[:2]) + " mechanism")
            queries.append(" ".join(claim.evidence_keywords[:2]) + " pathway")

        return [q for q in queries if q]  # Filter empty strings

    def _infer_article_type(self, claim: Claim) -> str:
        """Infer expected article type from claim."""
        if claim.claim_type in ["QUANTITATIVE", "COMPARATIVE"]:
            return "empirical"
        elif claim.claim_type == "CAUSAL":
            return "review"
        else:
            return "theoretical"

    def submit_to_pipeline(self, targets: List[SearchTarget], db_path: Optional[str] = None):
        """
        Insert search targets into interpretation_space_suggestions table.

        This is the canonical recommendation pipeline table used by the
        OVERSEER management layer and the continuous recommendation loop.
        """
        db_path = db_path or self.db_path
        if not targets:
            return 0

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Ensure table exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS interpretation_space_suggestions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'proposed',
                    description TEXT,
                    suggested_search TEXT,
                    priority_score REAL DEFAULT 0.5,
                    created_at TEXT,
                    updated_at TEXT,
                    resolved_at TEXT,
                    article_id TEXT
                )
            """)

            now = datetime.now().isoformat()
            count = 0
            for target in targets:
                cursor.execute("""
                    INSERT INTO interpretation_space_suggestions (
                        source, status, description, suggested_search,
                        priority_score, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    "paper_evidence_gap",
                    "proposed",
                    f"[Paper §{target.section}] {target.claim_summary}",
                    target.search_query,
                    target.priority_score,
                    now,
                    now,
                ))
                count += 1

            conn.commit()
            conn.close()
            return count

        except Exception as e:
            return 0

    def full_pipeline(self, paper_path: str) -> Dict:
        """
        Run complete audit → targets → submission pipeline.
        Returns summary dictionary.
        """
        report = self.audit_paper(paper_path)
        targets = self.generate_search_targets(report)
        submissions = self.submit_to_pipeline(targets)

        return {
            'paper': report.paper_title,
            'audit_date': report.audit_date,
            'claims_total': report.total_claims,
            'well_supported': report.well_supported,
            'partially_supported': report.partially_supported,
            'unsupported': report.unsupported,
            'overall_warrant': report.overall_warrant,
            'search_targets': len(targets),
            'submissions': submissions,
            'report': report
        }


# ============================================================================
# Command-line usage
# ============================================================================

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python paper_evidence_auditor.py <paper_path> [db_path]")
        sys.exit(1)

    paper_path = sys.argv[1]
    db_path = sys.argv[2] if len(sys.argv) > 2 else "ae.db"

    auditor = PaperEvidenceAuditor(db_path)
    result = auditor.full_pipeline(paper_path)

    print("\n" + "=" * 80)
    print("PAPER EVIDENCE AUDIT COMPLETE")
    print("=" * 80)
    print(f"\nPaper: {result['paper']}")
    print(f"Date: {result['audit_date']}")
    print(f"\nClaims: {result['claims_total']}")
    print(f"  Well-supported:      {result['well_supported']} ({100*result['well_supported']/result['claims_total']:.1f}%)")
    print(f"  Partially-supported: {result['partially_supported']} ({100*result['partially_supported']/result['claims_total']:.1f}%)")
    print(f"  Unsupported:         {result['unsupported']} ({100*result['unsupported']/result['claims_total']:.1f}%)")
    print(f"\nOverall Warrant: {result['overall_warrant']:.2f}")
    print(f"Search Targets: {result['search_targets']}")
    print(f"Submissions: {result['submissions']}")
