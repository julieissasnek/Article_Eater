#!/usr/bin/env python3
"""
PDF EXTRACTION MODULE
=====================

A self-contained module for extracting structured findings from scientific PDFs.
Designed for batch processing with quality control and queue management.

USAGE:
    from src.extraction.pdf_extraction_module import ExtractionPipeline

    pipeline = ExtractionPipeline(
        pdf_dir="/path/to/pdfs",
        output_dir="/path/to/outputs"
    )

    # Process a batch
    pipeline.process_batch(batch_size=50)

    # Resume from where you left off
    pipeline.resume()

    # Check status
    pipeline.status()

    # Get results ready for BN/Web integration
    ready = pipeline.get_ready_for_integration()

CONTRACTS:
    - ExtractionRequest: What goes into the pipeline
    - ExtractionResult: What comes out
    - QueueItem: State tracking for each paper
    - QualityReport: Evaluation results

QUEUE STATES:
    PENDING -> CLASSIFYING -> EXTRACTING -> EVALUATING ->
        -> ACCEPTED (ready for BN/Web)
        -> REQUEUED (needs retry)
        -> FAILED (manual review needed)

Author: Article Eater Pipeline
Date: 2026-02-24
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional
import hashlib
import fcntl
import socket

try:
    from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
except ImportError:
    pass  # We will handle missing tenacity via an error message if it's not installed

# ---------------------------------------------------------------------------
# ROBUST JSON PARSING — salvages partial/malformed Gemini outputs
# ---------------------------------------------------------------------------

RAW_FAILURES_DIR = Path(os.environ.get("AE_RAW_FAILURES_DIR", "data/extractions/raw_failures"))


def robust_json_parse(text: str) -> Optional[dict]:
    """
    Try increasingly aggressive strategies to extract valid JSON.

    Handles:
    1. Normal JSON (fast path)
    2. "Extra data" — Gemini outputs two JSON blobs; take first balanced one
    3. "Unterminated string" — output truncated; close open strings/arrays/objects
    4. Trailing commas, missing quotes, etc.
    """
    if not text or not text.strip():
        return None

    text = text.strip()

    # Strip markdown code fences
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        text = text.strip()

    # Strategy 1: Direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Strategy 2: Balanced-brace extraction (for "Extra data" errors)
    first_brace = text.find("{")
    if first_brace >= 0:
        depth = 0
        in_string = False
        escape = False
        for i, ch in enumerate(text[first_brace:], start=first_brace):
            if escape:
                escape = False
                continue
            if ch == "\\" and in_string:
                escape = True
                continue
            if ch == '"' and not escape:
                in_string = not in_string
                continue
            if in_string:
                continue
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    candidate = text[first_brace:i+1]
                    try:
                        return json.loads(candidate)
                    except json.JSONDecodeError:
                        break

    # Strategy 3: Truncation repair — close open structures
    repaired = text
    if repaired.count('"') % 2 != 0:
        last_quote = repaired.rfind('"')
        if last_quote > 0:
            repaired = repaired[:last_quote+1]

    open_braces = repaired.count("{") - repaired.count("}")
    open_brackets = repaired.count("[") - repaired.count("]")
    repaired = repaired.rstrip()
    if repaired.endswith(","):
        repaired = repaired[:-1]
    repaired += "]" * max(0, open_brackets) + "}" * max(0, open_braces)

    try:
        return json.loads(repaired)
    except json.JSONDecodeError:
        pass

    # Strategy 4: Remove trailing garbage after last complete finding
    last_finding_end = max(repaired.rfind("},"), repaired.rfind("}\n"))
    if last_finding_end > 0:
        truncated = repaired[:last_finding_end+1]
        open_b = truncated.count("{") - truncated.count("}")
        open_br = truncated.count("[") - truncated.count("]")
        truncated += "]" * max(0, open_br) + "}" * max(0, open_b)
        try:
            return json.loads(truncated)
        except json.JSONDecodeError:
            pass

    return None


def save_raw_failure(doi: str, raw_text: str, error: str):
    """Save raw Gemini output for failed extractions."""
    RAW_FAILURES_DIR.mkdir(parents=True, exist_ok=True)
    doi_safe = doi.replace("/", "_")
    raw_file = RAW_FAILURES_DIR / f"{doi_safe}.txt"
    meta_file = RAW_FAILURES_DIR / f"{doi_safe}.meta.json"
    raw_file.write_text(raw_text)
    meta_file.write_text(json.dumps({
        "doi": doi, "error": error,
        "raw_chars": len(raw_text),
        "saved_at": datetime.now(timezone.utc).isoformat(),
    }, indent=2))
    return raw_file


# ---------------------------------------------------------------------------
# PROCESS LOCKING (for multi-process safety)
# ---------------------------------------------------------------------------

class WorkClaimer:
    """
    Distributed work claiming for parallel agent execution.

    Design:
    - Each agent has a unique ID
    - Agents CLAIM papers before processing (atomic via file lock)
    - Claims have timestamps for timeout/recovery
    - Multiple agents can run simultaneously on different papers
    - Stale claims (agent died) can be reclaimed after timeout
    """

    CLAIM_TIMEOUT_SECONDS = 600  # 10 minutes - reclaim if agent dies

    def __init__(self, claims_file: Path, agent_id: Optional[str] = None):
        self.claims_file = claims_file
        self.lock_file = claims_file.with_suffix(".lock")
        self.agent_id = agent_id or f"{socket.gethostname()}_{os.getpid()}_{datetime.now().strftime('%H%M%S')}"

    def _read_claims(self) -> dict:
        """Read current claims (under lock)."""
        if self.claims_file.exists():
            try:
                with open(self.claims_file) as f:
                    return json.load(f)
            except Exception:
                return {"claims": {}, "completed": set()}
        return {"claims": {}, "completed": set()}

    def _write_claims(self, data: dict):
        """Write claims (under lock)."""
        # Convert sets to lists for JSON
        if isinstance(data.get("completed"), set):
            data["completed"] = list(data["completed"])
        with open(self.claims_file, "w") as f:
            json.dump(data, f, indent=2)

    def _with_lock(self, func):
        """Execute function with file lock."""
        lock_fd = open(self.lock_file, "w")
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_EX)
            return func()
        finally:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
            lock_fd.close()

    def claim_papers(self, dois: list[str], max_claims: int = 10) -> list[str]:
        """
        Claim papers for processing. Returns list of successfully claimed DOIs.

        Args:
            dois: List of DOIs to try to claim
            max_claims: Maximum papers to claim at once

        Returns:
            List of DOIs successfully claimed by this agent
        """
        def _do_claim():
            data = self._read_claims()
            claims = data.get("claims", {})
            completed = set(data.get("completed", []))

            now = datetime.now(timezone.utc)
            claimed = []

            for doi in dois:
                if len(claimed) >= max_claims:
                    break

                # Skip if already completed
                if doi in completed:
                    continue

                # Check if already claimed
                if doi in claims:
                    claim = claims[doi]
                    claim_time = datetime.fromisoformat(claim["claimed_at"])
                    age_seconds = (now - claim_time).total_seconds()

                    # If claimed by us, skip (already working on it)
                    if claim["agent_id"] == self.agent_id:
                        continue

                    # If claim is stale, reclaim it
                    if age_seconds < self.CLAIM_TIMEOUT_SECONDS:
                        continue  # Still valid, skip

                # Claim this paper
                claims[doi] = {
                    "agent_id": self.agent_id,
                    "claimed_at": now.isoformat(),
                    "host": socket.gethostname(),
                }
                claimed.append(doi)

            data["claims"] = claims
            self._write_claims(data)
            return claimed

        return self._with_lock(_do_claim)

    def release_paper(self, doi: str, completed: bool = True):
        """Release a paper after processing."""
        def _do_release():
            data = self._read_claims()
            claims = data.get("claims", {})
            completed_set = set(data.get("completed", []))

            # Remove from claims
            if doi in claims:
                del claims[doi]

            # Add to completed if successful
            if completed:
                completed_set.add(doi)

            data["claims"] = claims
            data["completed"] = list(completed_set)
            self._write_claims(data)

        self._with_lock(_do_release)

    def heartbeat(self, dois: list[str]):
        """Update claim timestamps to prevent timeout."""
        def _do_heartbeat():
            data = self._read_claims()
            claims = data.get("claims", {})
            now = datetime.now(timezone.utc).isoformat()

            for doi in dois:
                if doi in claims and claims[doi]["agent_id"] == self.agent_id:
                    claims[doi]["claimed_at"] = now

            data["claims"] = claims
            self._write_claims(data)

        self._with_lock(_do_heartbeat)

    def get_status(self) -> dict:
        """Get current claim status."""
        def _do_status():
            data = self._read_claims()
            claims = data.get("claims", {})
            completed = set(data.get("completed", []))

            now = datetime.now(timezone.utc)
            active_agents = {}
            stale_claims = []

            for doi, claim in claims.items():
                agent = claim["agent_id"]
                claim_time = datetime.fromisoformat(claim["claimed_at"])
                age = (now - claim_time).total_seconds()

                if age > self.CLAIM_TIMEOUT_SECONDS:
                    stale_claims.append(doi)
                else:
                    if agent not in active_agents:
                        active_agents[agent] = {"count": 0, "host": claim.get("host", "unknown")}
                    active_agents[agent]["count"] += 1

            return {
                "active_agents": active_agents,
                "total_claimed": len(claims),
                "stale_claims": len(stale_claims),
                "completed": len(completed),
                "this_agent": self.agent_id,
            }

        return self._with_lock(_do_status)

    def reclaim_stale(self) -> int:
        """Reclaim papers from dead agents. Returns count reclaimed."""
        def _do_reclaim():
            data = self._read_claims()
            claims = data.get("claims", {})

            now = datetime.now(timezone.utc)
            reclaimed = 0

            for doi in list(claims.keys()):
                claim = claims[doi]
                claim_time = datetime.fromisoformat(claim["claimed_at"])
                age = (now - claim_time).total_seconds()

                if age > self.CLAIM_TIMEOUT_SECONDS:
                    del claims[doi]
                    reclaimed += 1

            data["claims"] = claims
            self._write_claims(data)
            return reclaimed

        return self._with_lock(_do_reclaim)


# ---------------------------------------------------------------------------
# CONTRACTS
# ---------------------------------------------------------------------------

class QueueStatus(str, Enum):
    """Pipeline queue states."""
    PENDING = "pending"
    CLASSIFYING = "classifying"
    EXTRACTING = "extracting"
    EVALUATING = "evaluating"
    ACCEPTED = "accepted"          # Ready for BN/Web integration
    REQUEUED = "requeued"          # Failed quality check, will retry
    FAILED = "failed"              # Manual review needed
    INTEGRATED = "integrated"      # Already in BN/Web


class ArticleType(str, Enum):
    """Supported article types with dedicated extraction templates."""
    EMPIRICAL = "empirical"
    META_ANALYSIS = "meta_analysis"
    SYSTEMATIC_REVIEW = "systematic_review"
    NARRATIVE_REVIEW = "narrative_review"
    THEORETICAL = "theoretical"
    QUALITATIVE = "qualitative"
    METHODS = "methods"
    UNKNOWN = "unknown"


@dataclass
class ExtractionRequest:
    """Contract: Input to the extraction pipeline."""
    doi: str
    pdf_path: str
    priority: int = 5              # 1=highest, 10=lowest
    force_article_type: Optional[str] = None  # Override classification
    extract_images: bool = True
    max_retries: int = 2


@dataclass
class Finding:
    """Contract: A single extracted finding."""
    id: int
    antecedent: str
    consequent: str
    direction: str                 # increase|decrease|no_effect|mixed|unclear
    claim_type: str                # causal|associational|moderated|null

    # Statistics (HIGH priority)
    p_value: Optional[str] = None
    effect_size: Optional[float] = None
    effect_size_type: Optional[str] = None
    sample_size: Optional[int] = None
    confidence_interval: Optional[list] = None

    # Theory links (MEDIUM priority)
    theory_links: list = field(default_factory=list)
    mechanism: Optional[str] = None

    # Source
    measure_type: Optional[str] = None
    source: Optional[str] = None
    quote: Optional[str] = None


@dataclass
class Stimulus:
    """Contract: Extracted stimulus description."""
    type: str                      # photograph|rendering|VR|video|physical_space|audio
    description: str
    n_stimuli: Optional[int] = None
    source: Optional[str] = None


@dataclass
class TableInfo:
    """Contract: Extracted table information."""
    table_id: str
    description: str
    key_stats: list = field(default_factory=list)


@dataclass
class ExtractionResult:
    """Contract: Output from the extraction pipeline."""
    doi: str
    article_type: ArticleType
    title: Optional[str] = None
    n_participants: Optional[int] = None
    study_design: Optional[str] = None

    findings: list = field(default_factory=list)
    stimuli: list = field(default_factory=list)
    tables: list = field(default_factory=list)

    domains: list = field(default_factory=list)
    overall_theory_links: list = field(default_factory=list)
    limitations: list = field(default_factory=list)

    # Extraction metadata
    extraction_cost: float = 0.0
    extraction_time: float = 0.0
    model_used: str = "gemini-2.5-flash"

    # Image extraction
    extracted_images: list = field(default_factory=list)


@dataclass
class QualityReport:
    """Contract: Quality evaluation of extraction."""
    doi: str
    passed: bool
    overall_score: float           # 0.0 to 1.0

    # Field coverage
    has_antecedent_consequent: float
    has_direction: float
    has_statistics: float          # p_value or effect_size
    has_theory_links: float
    has_quotes: float

    # Issues
    issues: list = field(default_factory=list)

    # Recommendation
    action: str = "accept"         # accept|requeue|fail


@dataclass
class QueueItem:
    """Contract: State tracking for each paper in the queue."""
    doi: str
    pdf_path: str
    status: QueueStatus = QueueStatus.PENDING
    priority: int = 5

    # Classification
    article_type: Optional[ArticleType] = None
    classification_confidence: float = 0.0

    # Extraction
    extraction_result: Optional[dict] = None

    # Quality
    quality_report: Optional[dict] = None

    # Tracking
    attempts: int = 0
    max_retries: int = 2
    total_cost: float = 0.0

    # Timestamps
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: Optional[str] = None
    completed_at: Optional[str] = None

    # Error tracking
    last_error: Optional[str] = None
    error_history: list = field(default_factory=list)


# ---------------------------------------------------------------------------
# QUALITY THRESHOLDS
# ---------------------------------------------------------------------------

QUALITY_THRESHOLDS = {
    "empirical": {
        "min_findings": 1,
        "require_statistics": 0.5,    # At least 50% of findings need stats
        "require_direction": 0.9,     # 90% need direction
        "min_score": 0.6,
    },
    "meta_analysis": {
        "min_findings": 1,
        "require_statistics": 0.8,
        "require_direction": 0.9,
        "min_score": 0.7,
    },
    "systematic_review": {
        "min_findings": 1,
        "require_statistics": 0.0,    # Stats optional
        "require_direction": 0.7,
        "min_score": 0.5,
    },
    "narrative_review": {
        "min_findings": 1,
        "require_statistics": 0.0,
        "require_direction": 0.5,
        "min_score": 0.4,
    },
    "theoretical": {
        "min_findings": 0,            # May have no empirical findings
        "require_statistics": 0.0,
        "require_direction": 0.3,
        "min_score": 0.3,
    },
    "default": {
        "min_findings": 0,
        "require_statistics": 0.0,
        "require_direction": 0.5,
        "min_score": 0.4,
    }
}


# ---------------------------------------------------------------------------
# FIELD WEIGHTS FOR QUALITY SCORING
# ---------------------------------------------------------------------------

FIELD_WEIGHTS = {
    # CRITICAL - extraction fails without these
    "antecedent": 0.15,
    "consequent": 0.15,
    "direction": 0.15,

    # HIGH - needed for BN edge weights
    "p_value": 0.10,
    "effect_size": 0.10,
    "sample_size": 0.05,

    # MEDIUM - for theory linking
    "theory_links": 0.10,
    "mechanism": 0.05,

    # LOW - supplementary
    "quote": 0.10,
    "source": 0.05,
}


# ---------------------------------------------------------------------------
# EXTRACTION PIPELINE
# ---------------------------------------------------------------------------

class ExtractionPipeline:
    """
    Main extraction pipeline with queue management.

    Workflow:
    1. Load PDFs and create queue
    2. Classify article type
    3. Extract with appropriate template
    4. Evaluate quality
    5. Accept, requeue, or fail
    6. Store for BN/Web integration
    """

    def __init__(
        self,
        pdf_dir: str | Path,
        output_dir: str | Path,
        api_key: Optional[str] = None,
        model: str = "gemini-2.5-flash",
    ):
        self.pdf_dir = Path(pdf_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.model = model
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

        # Queue persistence
        self.queue_file = self.output_dir / "extraction_queue.json"
        self.claims_file = self.output_dir / "work_claims.json"
        self.results_dir = self.output_dir / "results"
        self.results_dir.mkdir(exist_ok=True)
        self.images_dir = self.output_dir / "images"
        self.images_dir.mkdir(exist_ok=True)

        # Load or create queue
        self.queue: dict[str, QueueItem] = {}
        self._load_queue()

        # Lazy-load client
        self._client = None

        # Process identification and work claiming
        self.agent_id = f"{socket.gethostname()}_{os.getpid()}_{datetime.now().strftime('%H%M%S')}"
        self.claimer = WorkClaimer(self.claims_file, agent_id=self.agent_id)

    @property
    def client(self):
        """Lazy-load Gemini client."""
        if self._client is None:
            from google import genai
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    # -----------------------------------------------------------------------
    # QUEUE MANAGEMENT
    # -----------------------------------------------------------------------

    def _load_queue(self):
        """Load queue from disk."""
        if self.queue_file.exists():
            with open(self.queue_file) as f:
                data = json.load(f)
            for doi, item_data in data.get("items", {}).items():
                item_data["status"] = QueueStatus(item_data["status"])
                if item_data.get("article_type"):
                    item_data["article_type"] = ArticleType(item_data["article_type"])
                self.queue[doi] = QueueItem(**item_data)

    def _save_queue(self):
        """Save queue to disk."""
        items = {}
        for doi, item in self.queue.items():
            item_dict = asdict(item)
            item_dict["status"] = item.status.value
            if item.article_type:
                item_dict["article_type"] = item.article_type.value
            items[doi] = item_dict

        data = {
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "stats": self._get_stats(),
            "items": items,
        }
        with open(self.queue_file, "w") as f:
            json.dump(data, f, indent=2)

    def _get_stats(self) -> dict:
        """Get queue statistics."""
        stats = {s.value: 0 for s in QueueStatus}
        for item in self.queue.values():
            stats[item.status.value] += 1
        stats["total"] = len(self.queue)
        return stats

    def add_to_queue(self, request: ExtractionRequest) -> QueueItem:
        """Add a paper to the queue."""
        if request.doi in self.queue:
            return self.queue[request.doi]

        item = QueueItem(
            doi=request.doi,
            pdf_path=request.pdf_path,
            priority=request.priority,
            max_retries=request.max_retries,
        )
        self.queue[request.doi] = item
        self._save_queue()
        return item

    def scan_pdfs(self, source_file: Optional[Path] = None) -> int:
        """
        Scan PDF directory and add papers to queue.

        Args:
            source_file: Optional JSON file with DOIs to process
                        (e.g., extraction results with 'unknown' papers)

        Returns:
            Number of papers added
        """
        added = 0

        if source_file and source_file.exists():
            # Load DOIs from source file
            with open(source_file) as f:
                data = json.load(f)

            dois = []
            for r in data.get("results", []):
                # Add papers marked as 'unknown' or not yet processed
                if r.get("article_type") == "unknown" or r.get("status") == "failed":
                    dois.append(r["doi"])

            for doi in dois:
                pdf_path = self.pdf_dir / (doi.replace("/", "_") + ".pdf")
                if pdf_path.exists() and doi not in self.queue:
                    self.add_to_queue(ExtractionRequest(doi=doi, pdf_path=str(pdf_path)))
                    added += 1
        else:
            # Scan PDF directory
            for pdf_path in self.pdf_dir.glob("*.pdf"):
                doi = pdf_path.stem.replace("_", "/")
                if doi not in self.queue:
                    self.add_to_queue(ExtractionRequest(doi=doi, pdf_path=str(pdf_path)))
                    added += 1

        self._save_queue()
        return added

    # -----------------------------------------------------------------------
    # CLASSIFICATION
    # -----------------------------------------------------------------------

    def _classify_paper(self, item: QueueItem) -> ArticleType:
        """Classify article type."""
        from google.genai import types
        from google.genai.errors import APIError

        prompt = """Classify this paper. Return ONE word only:
empirical
meta_analysis
systematic_review
narrative_review
theoretical
qualitative
methods"""

        @retry(
            retry=retry_if_exception_type((APIError, Exception)),
            wait=wait_exponential(multiplier=1, min=4, max=60),
            stop=stop_after_attempt(5)
        )
        def _call_gemini_classify():
            with open(item.pdf_path, "rb") as f:
                uploaded = self.client.files.upload(file=f, config={"mime_type": "application/pdf"})

            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=[uploaded, prompt],
                    config=types.GenerateContentConfig(temperature=0.0, max_output_tokens=50),
                )
                text = response.text
                return text.strip().lower() if text else ArticleType.UNKNOWN.value
            finally:
                try:
                    self.client.files.delete(name=uploaded.name)
                except Exception:
                    pass

        try:
            text = _call_gemini_classify()

            # Parse response
            for article_type in ArticleType:
                if article_type.value in text:
                    return article_type

            # Handle variations
            if "meta" in text:
                return ArticleType.META_ANALYSIS
            if "systematic" in text:
                return ArticleType.SYSTEMATIC_REVIEW
            if "narrative" in text or "review" in text:
                return ArticleType.NARRATIVE_REVIEW

            return ArticleType.EMPIRICAL  # Default

        except Exception as e:
            item.last_error = f"Classification: {str(e)[:100]}"
            return ArticleType.UNKNOWN

    # -----------------------------------------------------------------------
    # EXTRACTION
    # -----------------------------------------------------------------------

    def _get_prompt(self, article_type: ArticleType) -> str:
        """Get extraction prompt for article type."""
        # Import prompts from existing module
        from scripts.gemini_extraction_queue import PROMPT_MAP
        return PROMPT_MAP.get(article_type.value, PROMPT_MAP["unknown"])

    def _extract_paper(self, item: QueueItem) -> ExtractionResult:
        """Extract findings from paper."""
        from google.genai import types
        from google.genai.errors import APIError
        
        prompt = self._get_prompt(item.article_type)
        start_time = time.time()

        @retry(
            retry=retry_if_exception_type((APIError, Exception)),
            wait=wait_exponential(multiplier=1, min=4, max=60),
            stop=stop_after_attempt(5)
        )
        def _call_gemini_extract():
            with open(item.pdf_path, "rb") as f:
                uploaded = self.client.files.upload(file=f, config={"mime_type": "application/pdf"})

            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=[uploaded, prompt],
                    config=types.GenerateContentConfig(temperature=0.1, max_output_tokens=131072),
                )
                return response
            finally:
                try:
                    self.client.files.delete(name=uploaded.name)
                except Exception:
                    pass

        try:
            response = _call_gemini_extract()

            # Parse JSON with robust recovery
            raw_text = response.text
            if not raw_text:
                item.last_error = "Extraction: API returned empty response (possible safety block)"
                raise ValueError("Empty response from API")

            data = robust_json_parse(raw_text)

            if data is None:
                # Save raw output for future salvage
                save_raw_failure(item.doi, raw_text, "robust_json_parse failed")
                item.last_error = f"JSON parse failed after robust recovery ({len(raw_text)} chars)"
                raise ValueError(item.last_error)

            # Calculate cost
            cost = 0.0
            if response.usage_metadata:
                m = response.usage_metadata
                # Gemini 2.5 Flash pricing
                cost = (m.prompt_token_count * 0.15 + m.candidates_token_count * 0.60) / 1_000_000

            return ExtractionResult(
                doi=item.doi,
                article_type=item.article_type,
                title=data.get("title"),
                n_participants=data.get("n_participants"),
                study_design=data.get("study_design"),
                findings=data.get("findings", []),
                stimuli=data.get("stimuli", []),
                tables=data.get("tables", []),
                domains=data.get("domains", []),
                overall_theory_links=data.get("overall_theory_links", []),
                limitations=data.get("limitations", []),
                extraction_cost=cost,
                extraction_time=time.time() - start_time,
                model_used=self.model,
            )

        except Exception as e:
            item.last_error = f"Extraction: {str(e)[:100]}"
            raise

    # -----------------------------------------------------------------------
    # QUALITY EVALUATION
    # -----------------------------------------------------------------------

    def _evaluate_quality(self, result: ExtractionResult) -> QualityReport:
        """Evaluate extraction quality."""
        findings = result.findings
        n = len(findings) if findings else 0

        if n == 0:
            return QualityReport(
                doi=result.doi,
                passed=False,
                overall_score=0.0,
                has_antecedent_consequent=0.0,
                has_direction=0.0,
                has_statistics=0.0,
                has_theory_links=0.0,
                has_quotes=0.0,
                issues=["No findings extracted"],
                action="requeue" if result.article_type == ArticleType.EMPIRICAL else "accept",
            )

        # Calculate field coverage
        has_ac = sum(1 for f in findings if f.get("antecedent") and f.get("consequent")) / n
        has_dir = sum(1 for f in findings if f.get("direction")) / n
        has_stats = sum(1 for f in findings if f.get("p_value") or f.get("effect_size")) / n
        has_theory = sum(1 for f in findings if f.get("theory_links")) / n
        has_quote = sum(1 for f in findings if f.get("quote")) / n

        # Calculate overall score
        score = (
            FIELD_WEIGHTS["antecedent"] * has_ac +
            FIELD_WEIGHTS["consequent"] * has_ac +
            FIELD_WEIGHTS["direction"] * has_dir +
            FIELD_WEIGHTS["p_value"] * has_stats +
            FIELD_WEIGHTS["effect_size"] * has_stats +
            FIELD_WEIGHTS["theory_links"] * has_theory +
            FIELD_WEIGHTS["quote"] * has_quote
        )

        # Normalize to 0-1
        max_score = sum(FIELD_WEIGHTS.values())
        score = score / max_score

        # Get thresholds for article type
        thresholds = QUALITY_THRESHOLDS.get(
            result.article_type.value,
            QUALITY_THRESHOLDS["default"]
        )

        # Check issues
        issues = []
        if has_ac < 0.8:
            issues.append(f"Low antecedent/consequent coverage: {has_ac:.0%}")
        if has_dir < thresholds["require_direction"]:
            issues.append(f"Low direction coverage: {has_dir:.0%}")
        if has_stats < thresholds["require_statistics"]:
            issues.append(f"Low statistics coverage: {has_stats:.0%}")

        # Determine action
        passed = score >= thresholds["min_score"] and len(issues) <= 1

        if passed:
            action = "accept"
        elif score >= thresholds["min_score"] * 0.7:
            action = "requeue"
        else:
            action = "fail"

        return QualityReport(
            doi=result.doi,
            passed=passed,
            overall_score=round(score, 3),
            has_antecedent_consequent=round(has_ac, 3),
            has_direction=round(has_dir, 3),
            has_statistics=round(has_stats, 3),
            has_theory_links=round(has_theory, 3),
            has_quotes=round(has_quote, 3),
            issues=issues,
            action=action,
        )

    # -----------------------------------------------------------------------
    # IMAGE EXTRACTION
    # -----------------------------------------------------------------------

    def _extract_images(self, item: QueueItem, min_size: int = 8000) -> list[dict]:
        """Extract images from PDF using PyMuPDF."""
        try:
            import fitz
        except ImportError:
            return []

        pdf_path = Path(item.pdf_path)
        if not pdf_path.exists():
            return []

        doi_safe = pdf_path.stem
        extracted = []

        try:
            with fitz.open(str(pdf_path)) as doc:
                for page_num in range(len(doc)):
                    page = doc[page_num]
            image_list = page.get_images(full=True)

            for img_index, img in enumerate(image_list):
                xref = img[0]
                try:
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]

                    if len(image_bytes) < min_size:
                        continue

                    img_filename = f"{doi_safe}_p{page_num + 1:02d}_img{img_index + 1:02d}.{base_image['ext']}"
                    img_path = self.images_dir / img_filename

                    with open(img_path, "wb") as f:
                        f.write(image_bytes)

                    extracted.append({
                        "page": page_num + 1,
                        "filename": img_filename,
                        "size_bytes": len(image_bytes),
                        "width": base_image.get("width"),
                        "height": base_image.get("height"),
                    })
                except Exception:
                    pass

        except Exception as e:
            # Catch broad exceptions from fitz to prevent hard crashes
            pass
            
        return extracted

    # -----------------------------------------------------------------------
    # MAIN PROCESSING
    # -----------------------------------------------------------------------

    def process_one(self, item: QueueItem, extract_images: bool = True) -> QueueItem:
        """Process a single paper through the pipeline."""
        item.attempts += 1
        item.updated_at = datetime.now(timezone.utc).isoformat()

        # PRE-FLIGHT CHECK
        try:
            import fitz
            with fitz.open(item.pdf_path) as doc:
                if doc.page_count == 0:
                    item.last_error = "PDF has 0 pages or is corrupted"
                    item.status = QueueStatus.FAILED
                    self._save_queue()
                    return item
        except ImportError:
            pass  # PyMuPDF not available, skip check
        except Exception as e:
            item.last_error = f"PDF corruption check failed: {str(e)}"
            item.status = QueueStatus.FAILED
            self._save_queue()
            return item

        try:
            # Step 1: Classify
            item.status = QueueStatus.CLASSIFYING
            self._save_queue()

            item.article_type = self._classify_paper(item)

            # Step 2: Extract
            item.status = QueueStatus.EXTRACTING
            self._save_queue()

            result = self._extract_paper(item)
            item.extraction_result = asdict(result)
            item.total_cost += result.extraction_cost

            # Step 2b: Extract images
            if extract_images:
                result.extracted_images = self._extract_images(item)
                item.extraction_result["extracted_images"] = result.extracted_images

            # Step 3: Evaluate quality
            item.status = QueueStatus.EVALUATING
            self._save_queue()

            quality = self._evaluate_quality(result)
            item.quality_report = asdict(quality)

            # Step 4: Route based on quality
            if quality.action == "accept":
                item.status = QueueStatus.ACCEPTED
                item.completed_at = datetime.now(timezone.utc).isoformat()

                # Save result to results directory
                result_file = self.results_dir / f"{item.doi.replace('/', '_')}.json"
                with open(result_file, "w") as f:
                    json.dump(item.extraction_result, f, indent=2)

                # --- INTEGRATION HOOK (Sprint INTEGRATION-1) ---
                # Trigger Paper Integration Pipeline for newly accepted papers.
                # Runs asynchronously: if integration fails, extraction is still saved.
                self._trigger_integration(item)

            elif quality.action == "requeue" and item.attempts < item.max_retries:
                item.status = QueueStatus.REQUEUED
                item.error_history.append(f"Attempt {item.attempts}: {quality.issues}")
            else:
                item.status = QueueStatus.FAILED
                item.completed_at = datetime.now(timezone.utc).isoformat()

        except Exception as e:
            item.error_history.append(f"Attempt {item.attempts}: {str(e)[:100]}")

            if item.attempts < item.max_retries:
                item.status = QueueStatus.REQUEUED
            else:
                item.status = QueueStatus.FAILED
                item.completed_at = datetime.now(timezone.utc).isoformat()

        self._save_queue()
        return item

    def process_batch(self, batch_size: int = 50, extract_images: bool = True) -> dict:
        """
        Process a batch of papers with distributed work claiming.

        Multiple agents can run simultaneously - each claims papers atomically.
        """
        # First, reclaim any stale work from dead agents
        reclaimed = self.claimer.reclaim_stale()
        if reclaimed:
            print(f"Reclaimed {reclaimed} papers from stale agents")

        # Get papers available to process (pending or requeued)
        available_dois = [
            item.doi for item in self.queue.values()
            if item.status in (QueueStatus.PENDING, QueueStatus.REQUEUED)
        ]

        if not available_dois:
            return {"processed": 0, "message": "No papers to process", "agent_id": self.agent_id}

        # Claim papers (atomic operation - won't conflict with other agents)
        claimed_dois = self.claimer.claim_papers(available_dois, max_claims=batch_size)

        if not claimed_dois:
            # All papers are claimed by other agents
            claim_status = self.claimer.get_status()
            return {
                "processed": 0,
                "message": "All papers claimed by other agents",
                "agent_id": self.agent_id,
                "active_agents": claim_status["active_agents"],
            }

        print(f"Agent {self.agent_id[:20]}... claimed {len(claimed_dois)} papers")

        results = {
            "processed": 0,
            "accepted": 0,
            "requeued": 0,
            "failed": 0,
            "agent_id": self.agent_id,
        }

        start_times_dict = {}
        total_costs = 0.0

        print(f"\n{'-'*95}")
        print(f"{'DOI':<25} | {'Started':<8} | {'Current':<8} | {'Processed':<9} | {'Cost':<7} | {'Mean Time':<9}")
        print(f"{'-'*95}")

        for i, doi in enumerate(claimed_dois):
            item = self.queue.get(doi)
            if not item:
                self.claimer.release_paper(doi, completed=False)
                continue

            start_t = time.time()

            try:
                processed = self.process_one(item, extract_images=extract_images)
                results["processed"] += 1
                
                # Fetch actual cost accumulated on this item
                total_costs += processed.total_cost

                if processed.status == QueueStatus.ACCEPTED:
                    results["accepted"] += 1
                    self.claimer.release_paper(doi, completed=True)
                elif processed.status == QueueStatus.REQUEUED:
                    results["requeued"] += 1
                    self.claimer.release_paper(doi, completed=False)
                else:
                    results["failed"] += 1
                    self.claimer.release_paper(doi, completed=True)  # Don't retry forever

            except Exception as e:
                self.claimer.release_paper(doi, completed=False)
                results["failed"] += 1
                
            elapsed_time = time.time() - start_t
            start_times_dict[doi] = elapsed_time
            
            mean_time = sum(start_times_dict.values()) / len(start_times_dict)
            num_started = len(claimed_dois)
            current_num = i + 1
            
            # Formatted table row output for this single PDF
            doi_disp = doi.split("/")[-1][:23] if "/" in doi else doi[:23]
            print(f"{doi_disp:<25} | {num_started:<8} | {current_num:<8} | {results['processed']:<9} | ${total_costs:<6.3f} | {mean_time:<8.1f}s")

            # Brief pause between papers
            time.sleep(0.5)

            # Heartbeat every 5 papers to prevent timeout
            if i % 5 == 0:
                remaining = claimed_dois[i:]
                self.claimer.heartbeat(remaining)

        print(f"{'-'*95}")
        print(f"\nBatch complete: {results}")
        return results

    def resume(self, batch_size: int = 50) -> dict:
        """Resume processing from where we left off."""
        return self.process_batch(batch_size=batch_size)

    def auto_resume(
        self,
        batch_size: int = 50,
        extract_images: bool = True,
        delay_seconds: int = 5,
        max_idle_rounds: int = 3,
    ) -> dict:
        """
        Continuously run `process_batch` until there are no more pending papers,
        or until we see several rounds with zero processing (other agents may own the queue).
        """
        rounds = 0
        idle_rounds = 0
        final_status: dict[str, Any] = {}

        while True:
            rounds += 1
            print(f"\nAuto-resume round {rounds}")
            results = self.process_batch(batch_size=batch_size, extract_images=extract_images)
            final_status = results

            pending = self.status().get("pending", 0)
            self._log_auto_round(rounds, results, pending)
            if results.get("processed", 0) == 0:
                idle_rounds += 1
            else:
                idle_rounds = 0

            if pending == 0:
                print("Auto-resume complete: queue is empty")
                break

            if idle_rounds >= max_idle_rounds:
                print("Auto-resume stopping: multiple rounds processed zero papers (others may own the queue).")
                break

            print(f"Waiting {delay_seconds}s before next batch...")
            time.sleep(delay_seconds)

        return final_status

    def _log_auto_round(self, round_number: int, results: dict[str, Any], pending: int):
        """Append auto-resume round data to a log and capture a status snapshot."""
        log_file = self.output_dir / "auto_resume.log"
        timestamp = datetime.now(timezone.utc).isoformat()
        line = (
            f"{timestamp} round={round_number} processed={results.get('processed',0)} "
            f"accepted={results.get('accepted',0)} requeued={results.get('requeued',0)} "
            f"failed={results.get('failed',0)} pending={pending}\n"
        )
        with open(log_file, "a") as f:
            f.write(line)

        snapshot = self.status()
        snapshot["auto_resume_round"] = round_number
        snapshot_file = self.output_dir / f"auto_resume_status_round{round_number}.json"
        with open(snapshot_file, "w") as f:
            json.dump(snapshot, f, indent=2)

    def status(self) -> dict:
        """Get current pipeline status including active agents."""
        stats = self._get_stats()

        # Calculate totals
        stats["ready_for_integration"] = stats.get(QueueStatus.ACCEPTED.value, 0)
        stats["needs_retry"] = stats.get(QueueStatus.REQUEUED.value, 0)
        stats["needs_review"] = stats.get(QueueStatus.FAILED.value, 0)

        # Get work claim status (shows all active agents)
        claim_status = self.claimer.get_status()
        stats["agents"] = {
            "this_agent": self.agent_id,
            "active": claim_status["active_agents"],
            "papers_claimed": claim_status["total_claimed"],
            "stale_claims": claim_status["stale_claims"],
        }

        # Get recent activity
        recent = sorted(
            [i for i in self.queue.values() if i.completed_at],
            key=lambda x: x.completed_at or "",
            reverse=True
        )[:5]

        stats["recent"] = [
            {"doi": i.doi, "status": i.status.value, "completed": i.completed_at}
            for i in recent
        ]

        return stats

    def reclaim_stale(self) -> int:
        """Reclaim papers from dead/crashed agents."""
        return self.claimer.reclaim_stale()

    def get_ready_for_integration(self) -> list[ExtractionResult]:
        """Get results ready for BN/Web integration."""
        ready = []
        for item in self.queue.values():
            if item.status == QueueStatus.ACCEPTED and item.extraction_result:
                ready.append(item.extraction_result)
        return ready

    def mark_integrated(self, dois: list[str]):
        """Mark papers as integrated into BN/Web."""
        for doi in dois:
            if doi in self.queue:
                self.queue[doi].status = QueueStatus.INTEGRATED
        self._save_queue()

    def _trigger_integration(self, item) -> None:
        """
        Trigger the Paper Integration Pipeline for a newly accepted paper.

        Sprint INTEGRATION-1: This fires the 14-step cascade that propagates
        the paper's findings through web of belief, BN, tags, molecules,
        provenance, QA cache, social epistemology, and VOI gaps.

        Non-blocking: if integration fails, the extraction result is already
        saved and can be integrated later via get_ready_for_integration().
        """
        try:
            from src.services.paper_integration.orchestrator import PaperIntegrationOrchestrator
            import sqlite3

            # Use the project's main database
            db_path = str(self.results_dir.parent / "ae.db")
            db_conn = sqlite3.connect(db_path)

            orchestrator = PaperIntegrationOrchestrator(
                db_conn=db_conn,
                template_dir=str(self.results_dir.parent / "data" / "templates"),
                molecule_dir=str(self.results_dir.parent / "data" / "molecules"),
                theory_dir=str(self.results_dir.parent / "data" / "theories"),
            )

            # Build extraction data from the item's extraction result
            extraction_data = item.extraction_result or {}

            # Map ExtractionResult fields to orchestrator's expected format
            claims = extraction_data.get("findings", [])
            rules = extraction_data.get("rules", []) or extraction_data.get("constraints", [])

            # Extract paper metadata for supersession
            metadata = {
                "publication_year": extraction_data.get("year"),
                "sample_size": extraction_data.get("sample_size"),
                "study_design": extraction_data.get("study_design", "observational"),
            }

            paper_id = item.doi.replace("/", "_") if item.doi else f"paper_{item.completed_at}"

            event = orchestrator.integrate_paper(
                paper_id=paper_id,
                extraction_data={"claims": claims, "rules": rules},
                paper_metadata=metadata,
            )

            if event.status.value == "COMPLETED":
                # Mark as integrated
                self.mark_integrated([item.doi])
                logger.info(
                    "Paper %s integrated: %d beliefs, %d constraints",
                    paper_id, len(event.beliefs_added), len(event.constraints_added),
                )
            else:
                logger.warning(
                    "Paper %s integration %s: %s",
                    paper_id, event.status.value, event.error_log,
                )

            db_conn.close()

        except ImportError:
            logger.debug("Paper integration pipeline not available; skipping auto-integration")
        except Exception as e:
            # Integration failure should NOT block extraction
            logger.warning("Auto-integration failed for %s: %s (extraction preserved)", item.doi, e)


# ---------------------------------------------------------------------------
# CLI INTERFACE
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="""
PDF Extraction Module - Extract structured findings from scientific PDFs

WORKFLOW:
  1. --scan    : Add PDFs to the queue
  2. --status  : Check queue status
  3. --resume  : Process a batch of papers
  4. --auto    : Continuously process batches until queue is drained
  5. Repeat --resume/--auto until all papers processed

MULTI-PROCESS SAFETY:
  The pipeline uses file locking to prevent conflicts.
  If a process crashes, use --unlock to release the lock.

EXAMPLES:
  # Initialize queue from existing extraction file
  python -m src.extraction.pdf_extraction_module --scan data/extractions/full_extraction.json

  # Check status
  python -m src.extraction.pdf_extraction_module --status

  # Process 50 papers
  python -m src.extraction.pdf_extraction_module --resume --batch 50

  # Continue later
  python -m src.extraction.pdf_extraction_module --resume
""",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--pdf-dir", type=str, help="Directory containing PDFs")
    parser.add_argument("--output-dir", type=str, default="data/extraction_pipeline",
                       help="Output directory for results")
    parser.add_argument("--scan", type=str, help="Scan PDFs from source file (JSON with DOIs)")
    parser.add_argument("--batch", type=int, default=50, help="Batch size (default: 50)")
    parser.add_argument("--resume", action="store_true", help="Resume processing")
    parser.add_argument("--auto", action="store_true", help="Automatically rerun resume until the queue is empty")
    parser.add_argument("--auto-delay", type=int, default=5,
                        help="Seconds to wait between auto-resume batches (default: 5)")
    parser.add_argument("--status", action="store_true", help="Show queue status")
    parser.add_argument("--reclaim", action="store_true", help="Reclaim papers from dead agents")
    parser.add_argument("--no-images", action="store_true", help="Skip image extraction")
    parser.add_argument("--model", type=str, default="gemini-2.5-flash", help="LLM to use (default: gemini-2.5-flash)")
    args = parser.parse_args()

    # Default PDF directory
    pdf_dir = args.pdf_dir or "/Users/davidusa/REPOS/Article_Finder_v3_2_3/data/pdfs"

    pipeline = ExtractionPipeline(
        pdf_dir=pdf_dir,
        output_dir=args.output_dir,
        model=args.model,
    )

    if args.reclaim:
        reclaimed = pipeline.reclaim_stale()
        print(f"Reclaimed {reclaimed} papers from stale agents")

    elif args.status:
        status = pipeline.status()
        print(json.dumps(status, indent=2))

    elif args.scan:
        source = Path(args.scan)
        added = pipeline.scan_pdfs(source_file=source)
        print(f"Added {added} papers to queue")
        status = pipeline.status()
        print(f"Queue status: {status['total']} total, {status['pending']} pending")

    elif args.resume:
        results = pipeline.process_batch(
            batch_size=args.batch,
            extract_images=not args.no_images
        )
        if "error" not in results:
            remaining = pipeline.status()["pending"]
            print(f"\nRemaining: {remaining} papers")
            if remaining > 0:
                print("Run --resume again to continue")
    elif args.auto:
        pipeline.auto_resume(
            batch_size=args.batch,
            extract_images=not args.no_images,
            delay_seconds=args.auto_delay,
        )

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
