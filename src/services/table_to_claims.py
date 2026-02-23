"""
Article Eater V23 — Table to Claims Integration
Sprint 3.0 — 2026-02-09

Integrates extracted tables into the claim extraction pipeline.
Converts table data (ArticleMetadata, RCTStudyFact) into structured claims.
"""

import json
import logging
import re
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

from src.services.table_extractor import (
    ExtractedTable,
    TableType,
    ExtractionMethod,
    get_table_extractor,
    extracted_table_to_article_metadata,
    extracted_table_to_rct_facts,
)

logger = logging.getLogger(__name__)


@dataclass
class TableClaim:
    """A claim derived from an extracted table."""
    claim_id: str
    claim_type: str  # "finding", "methodology", "sample", "effect"
    content: str
    source_table_id: str
    source_row: int
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_claim_schema(self) -> Dict[str, Any]:
        """Convert to AE claim schema format."""
        return {
            "schema": "ae.claim.v1",
            "claim_id": self.claim_id,
            "claim_text": self.content,
            "claim_type": self.claim_type,
            "source": {
                "type": "table",
                "table_id": self.source_table_id,
                "row": self.source_row,
            },
            "confidence": self.confidence,
            "metadata": self.metadata,
        }


@dataclass
class TableExtractionResult:
    """Result of table extraction from a paper."""
    paper_id: str
    pdf_path: str
    tables: List[ExtractedTable]
    claims: List[TableClaim]
    extraction_time_s: float
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "paper_id": self.paper_id,
            "pdf_path": self.pdf_path,
            "n_tables": len(self.tables),
            "n_claims": len(self.claims),
            "extraction_time_s": self.extraction_time_s,
            "tables": [t.to_dict() for t in self.tables],
            "claims": [c.to_dict() for c in self.claims],
            "errors": self.errors,
        }


class TableClaimGenerator:
    """
    Generates structured claims from extracted tables.

    Converts different table types to appropriate claim types:
    - STUDY_CHARACTERISTICS → methodology, sample claims
    - RESULTS → effect, finding claims
    - QUALITY_ASSESSMENT → methodology claims
    - DEMOGRAPHICS → sample claims
    """

    def __init__(self, paper_id: str = "unknown"):
        self.paper_id = paper_id
        self._claim_counter = 0

    def _generate_claim_id(self) -> str:
        self._claim_counter += 1
        return f"{self.paper_id}-TBL-C{self._claim_counter:03d}"

    def generate_claims(self, table: ExtractedTable) -> List[TableClaim]:
        """Generate claims from an extracted table based on its type."""
        claims: List[TableClaim]
        if table.table_type == TableType.RESULTS:
            claims = self._claims_from_results(table)
        elif table.table_type == TableType.STUDY_CHARACTERISTICS:
            claims = self._claims_from_characteristics(table)
        elif table.table_type == TableType.DEMOGRAPHICS:
            claims = self._claims_from_demographics(table)
        elif table.table_type == TableType.QUALITY_ASSESSMENT:
            claims = self._claims_from_quality(table)
        else:
            claims = self._claims_from_generic(table)

        # Fallback for partially parsed tables that do not satisfy typed converters.
        if not claims:
            return self._claims_from_generic(table)
        return claims

    def _claims_from_results(self, table: ExtractedTable) -> List[TableClaim]:
        """Generate finding/effect claims from results table."""
        claims = []
        facts = extracted_table_to_rct_facts(table)

        for idx, fact in enumerate(facts):
            # Main effect claim
            if fact.effect_size is not None and fact.outcome_measure:
                effect_text = f"{fact.citation}: "
                if fact.intervention:
                    effect_text += f"{fact.intervention} "
                effect_text += f"showed effect size of {fact.effect_size:.2f} ({fact.effect_size_type}) "
                effect_text += f"on {fact.outcome_measure}"

                if fact.ci_lower is not None and fact.ci_upper is not None:
                    effect_text += f" (95% CI: [{fact.ci_lower:.2f}, {fact.ci_upper:.2f}])"
                if fact.p_value is not None:
                    p_str = f"p = {fact.p_value:.3f}" if fact.p_value >= 0.001 else "p < .001"
                    effect_text += f", {p_str}"

                claims.append(TableClaim(
                    claim_id=self._generate_claim_id(),
                    claim_type="effect",
                    content=effect_text,
                    source_table_id=table.table_id,
                    source_row=idx,
                    confidence=0.85 if fact.ci_lower is not None else 0.70,
                    metadata={
                        "citation": fact.citation,
                        "effect_size": fact.effect_size,
                        "effect_size_type": fact.effect_size_type,
                        "ci_lower": fact.ci_lower,
                        "ci_upper": fact.ci_upper,
                        "p_value": fact.p_value,
                        "sample_size": fact.sample_size,
                        "intervention": fact.intervention,
                        "control": fact.control,
                        "outcome": fact.outcome_measure,
                    }
                ))

            # Significance finding claim
            if fact.p_value is not None and fact.outcome_measure:
                sig_text = f"{fact.citation}: "
                if fact.p_value < 0.05:
                    sig_text += f"Statistically significant effect on {fact.outcome_measure}"
                else:
                    sig_text += f"No statistically significant effect on {fact.outcome_measure}"

                claims.append(TableClaim(
                    claim_id=self._generate_claim_id(),
                    claim_type="finding",
                    content=sig_text,
                    source_table_id=table.table_id,
                    source_row=idx,
                    confidence=0.90,
                    metadata={
                        "citation": fact.citation,
                        "p_value": fact.p_value,
                        "significant": fact.p_value < 0.05,
                    }
                ))

        return claims

    def _claims_from_characteristics(self, table: ExtractedTable) -> List[TableClaim]:
        """Generate methodology/sample claims from study characteristics."""
        claims = []

        for idx in range(len(table.rows)):
            metadata = extracted_table_to_article_metadata(table, idx)
            if not metadata:
                continue

            # Methodology claim
            method_text = f"{metadata.citation}: {metadata.study_type} study"
            if metadata.sample_size:
                method_text += f" with N={metadata.sample_size}"
            if metadata.setting != "Not specified":
                method_text += f" in {metadata.setting} setting"

            claims.append(TableClaim(
                claim_id=self._generate_claim_id(),
                claim_type="methodology",
                content=method_text,
                source_table_id=table.table_id,
                source_row=idx,
                confidence=0.90,
                metadata={
                    "citation": metadata.citation,
                    "study_type": metadata.study_type,
                    "sample_size": metadata.sample_size,
                    "setting": metadata.setting,
                }
            ))

            # Sample claim if population specified
            if metadata.population != "Not specified":
                sample_text = f"{metadata.citation}: Studied {metadata.population}"
                if metadata.sample_size:
                    sample_text += f" (N={metadata.sample_size})"

                claims.append(TableClaim(
                    claim_id=self._generate_claim_id(),
                    claim_type="sample",
                    content=sample_text,
                    source_table_id=table.table_id,
                    source_row=idx,
                    confidence=0.90,
                    metadata={
                        "citation": metadata.citation,
                        "population": metadata.population,
                        "sample_size": metadata.sample_size,
                    }
                ))

            # Intervention claim if specified
            if metadata.intervention:
                intervention_text = f"{metadata.citation}: Intervention was {metadata.intervention}"

                claims.append(TableClaim(
                    claim_id=self._generate_claim_id(),
                    claim_type="finding",
                    content=intervention_text,
                    source_table_id=table.table_id,
                    source_row=idx,
                    confidence=0.85,
                    metadata={
                        "citation": metadata.citation,
                        "intervention": metadata.intervention,
                    }
                ))

        return claims

    def _claims_from_demographics(self, table: ExtractedTable) -> List[TableClaim]:
        """Generate sample claims from demographics table."""
        claims = []
        headers_lower = [h.lower() for h in table.headers]

        for idx, row in enumerate(table.rows):
            # Build demographic description
            demo_parts = []

            for i, h in enumerate(headers_lower):
                if i >= len(row) or not row[i]:
                    continue
                val = row[i]

                if "group" in h or "condition" in h:
                    demo_parts.insert(0, f"{val} group")
                elif "n" == h or "sample" in h:
                    demo_parts.append(f"N={val}")
                elif "age" in h:
                    demo_parts.append(f"age: {val}")
                elif "female" in h or "gender" in h or "sex" in h:
                    demo_parts.append(f"gender: {val}")

            if demo_parts:
                claims.append(TableClaim(
                    claim_id=self._generate_claim_id(),
                    claim_type="sample",
                    content="; ".join(demo_parts),
                    source_table_id=table.table_id,
                    source_row=idx,
                    confidence=0.85,
                    metadata={"row_data": dict(zip(table.headers, row))}
                ))

        return claims

    def _claims_from_quality(self, table: ExtractedTable) -> List[TableClaim]:
        """Generate methodology claims from quality assessment table."""
        claims = []
        headers_lower = [h.lower() for h in table.headers]

        for idx, row in enumerate(table.rows):
            # Find citation and quality rating
            citation = ""
            quality = ""

            for i, h in enumerate(headers_lower):
                if i >= len(row):
                    continue
                if "citation" in h or "study" in h or "author" in h:
                    citation = row[i]
                elif "overall" in h or "quality" in h or "rating" in h or "risk" in h:
                    quality = row[i]

            if citation and quality:
                claims.append(TableClaim(
                    claim_id=self._generate_claim_id(),
                    claim_type="methodology",
                    content=f"{citation}: Study quality assessed as {quality}",
                    source_table_id=table.table_id,
                    source_row=idx,
                    confidence=0.80,
                    metadata={
                        "citation": citation,
                        "quality_rating": quality,
                    }
                ))

        return claims

    def _claims_from_generic(self, table: ExtractedTable) -> List[TableClaim]:
        """Generate generic claims from unknown table types."""
        claims = []

        # Create one claim per row with all data
        for idx, row in enumerate(table.rows):
            row_data = dict(zip(table.headers, row))
            content_parts = [f"{k}: {v}" for k, v in row_data.items() if v]

            if content_parts:
                claims.append(TableClaim(
                    claim_id=self._generate_claim_id(),
                    claim_type="finding",
                    content="; ".join(content_parts[:5]),  # Limit to 5 fields
                    source_table_id=table.table_id,
                    source_row=idx,
                    confidence=0.60,
                    metadata={"row_data": row_data}
                ))

        return claims


class PipelineTableIntegrator:
    """
    Integrates table extraction into the Article Eater pipeline.

    Can be called from pipeline.py to:
    1. Extract tables from PDF
    2. Generate claims from tables
    3. Return structured results for inclusion in pipeline output
    """

    def __init__(
        self,
        api_client: Optional[Any] = None,
        extraction_method: ExtractionMethod = ExtractionMethod.AI_API,
        model: str = "claude-3-haiku-20240307"
    ):
        self.extractor = get_table_extractor(extraction_method, api_client, model)
        self.api_client = api_client

    def extract_and_convert(
        self,
        pdf_path: Path,
        paper_id: str = "unknown",
        pages: Optional[List[int]] = None
    ) -> TableExtractionResult:
        """
        Extract tables from PDF and convert to claims.

        Args:
            pdf_path: Path to PDF file
            paper_id: Paper identifier for claim IDs
            pages: Specific pages to extract (None for all)

        Returns:
            TableExtractionResult with tables and claims
        """
        import time
        start_time = time.time()
        errors = []
        tables = []
        claims = []

        try:
            # Extract tables
            tables = self.extractor.extract_tables(pdf_path, pages)
            logger.info(f"Extracted {len(tables)} tables from {pdf_path}")

            # Generate claims from each table
            generator = TableClaimGenerator(paper_id)
            for table in tables:
                try:
                    table_claims = generator.generate_claims(table)
                    claims.extend(table_claims)
                    logger.debug(f"Generated {len(table_claims)} claims from table {table.table_id}")
                except Exception as e:
                    error_msg = f"Failed to generate claims from table {table.table_id}: {e}"
                    logger.warning(error_msg)
                    errors.append(error_msg)

            # Deduplicate near-identical claims emitted from overlapping table detections.
            deduped: Dict[Tuple[str, str], TableClaim] = {}
            for claim in claims:
                norm_text = re.sub(r"\s+", " ", claim.content.strip().lower())
                key = (claim.claim_type, norm_text)
                existing = deduped.get(key)
                if not existing or claim.confidence > existing.confidence:
                    deduped[key] = claim
            claims = list(deduped.values())

        except Exception as e:
            error_msg = f"Table extraction failed for {pdf_path}: {e}"
            logger.error(error_msg)
            errors.append(error_msg)

        extraction_time = time.time() - start_time

        return TableExtractionResult(
            paper_id=paper_id,
            pdf_path=str(pdf_path),
            tables=tables,
            claims=claims,
            extraction_time_s=extraction_time,
            errors=errors
        )

    def merge_with_text_claims(
        self,
        table_claims: List[TableClaim],
        text_claims: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Merge table-derived claims with text-extracted claims.
        Deduplicates based on content similarity.
        """
        merged = list(text_claims)
        existing_content = {c.get("claim_text", c.get("content", "")).lower() for c in text_claims}

        for tc in table_claims:
            # Simple deduplication - check for exact content match
            if tc.content.lower() not in existing_content:
                merged.append(tc.to_claim_schema())
                existing_content.add(tc.content.lower())
            else:
                logger.debug(f"Skipping duplicate table claim: {tc.content[:50]}...")

        return merged


def extract_tables_for_pipeline(
    pdf_path: Path,
    paper_id: str,
    api_client: Optional[Any] = None,
    extraction_method: ExtractionMethod = ExtractionMethod.AI_API
) -> Tuple[List[ExtractedTable], List[Dict[str, Any]]]:
    """
    Convenience function for pipeline integration.

    Returns:
        Tuple of (tables, claims_as_dicts)
    """
    integrator = PipelineTableIntegrator(api_client, extraction_method)
    result = integrator.extract_and_convert(pdf_path, paper_id)

    claims_dicts = [c.to_claim_schema() for c in result.claims]
    return result.tables, claims_dicts


def export_tables_jsonl(tables: List[ExtractedTable], output_path: Path) -> int:
    """Export extracted tables to JSONL file."""
    with open(output_path, 'w') as f:
        for table in tables:
            f.write(json.dumps(table.to_dict()) + '\n')
    return len(tables)


def export_table_claims_jsonl(claims: List[TableClaim], output_path: Path) -> int:
    """Export table-derived claims to JSONL file."""
    with open(output_path, 'w') as f:
        for claim in claims:
            f.write(json.dumps(claim.to_claim_schema()) + '\n')
    return len(claims)
