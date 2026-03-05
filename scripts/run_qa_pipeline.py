#!/usr/bin/env python3
"""
QA Pipeline Entry Point
=======================
Single unified entry point for question-to-answer enrichment.

Usage:
  python scripts/run_qa_pipeline.py --question "What is ART?"
  python scripts/run_qa_pipeline.py --question "Show me all theories" --verbose
  python scripts/run_qa_pipeline.py --question "How does coherence warrant work?" --json

This script:
  1. Accepts a question from CLI (--question flag)
  2. Imports and invokes ArbitraryQAHandler.answer()
  3. Enriches the answer using optional services (prose revision, etc.)
  4. Prints structured response with:
     - Question classification
     - Answer text
     - Credence score (if available)
     - Source citations
     - Processing timing
  5. Reports success/failure with helpful error messages
  6. Supports --verbose for debug output and --json for machine-readable output

Author: Claude Code (Article Eater CMR System)
Date: March 2026
"""

import argparse
import json
import logging
import sys
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, Any

# Setup repo root
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Setup logging
def setup_logging(verbose: bool = False):
    """Configure logging based on verbosity flag."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )
    return logging.getLogger(__name__)


logger = setup_logging()


# ============================================================================
# QA Handler Loading
# ============================================================================

def load_qa_handler():
    """
    Load the ArbitraryQAHandler with graceful degradation.

    Returns:
        ArbitraryQAHandler instance or None if import fails

    Raises:
        ImportError: If core QA dependencies are unavailable
    """
    try:
        from src.services.arbitrary_qa_handler import ArbitraryQAHandler
        logger.debug("Loading ArbitraryQAHandler...")
        handler = ArbitraryQAHandler()
        logger.info("ArbitraryQAHandler loaded successfully")
        return handler

    except ImportError as e:
        logger.error(f"Failed to import ArbitraryQAHandler: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to initialize ArbitraryQAHandler: {e}")
        raise


# ============================================================================
# Answer Enrichment
# ============================================================================

def try_enrich_answer(answer: Dict[str, Any]) -> Dict[str, Any]:
    """
    Attempt to enrich answer using available services.

    Services tried (graceful degradation):
    - Prose revision service (for grammar, clarity, structure)
    - Circuit QA service (for functional circuit integration)

    Args:
        answer: Raw answer dict from ArbitraryQAHandler

    Returns:
        Enriched answer dict (or original if enrichment unavailable)
    """
    try:
        from src.services.prose_revision_service import ProseRevisionService

        prose_reviewer = ProseRevisionService(context="qa_response")
        if prose_reviewer and hasattr(answer, 'get') and 'answer' in answer:
            original_text = answer.get('answer', '')
            revised_text = prose_reviewer.revise(original_text)
            if revised_text:
                answer['answer'] = revised_text
                answer['enriched_with_prose_revision'] = True
                logger.info("Answer enriched with prose revision")

    except ImportError:
        logger.debug("Prose revision service not available (optional)")
    except Exception as e:
        logger.warning(f"Prose enrichment failed (continuing): {e}")

    return answer


# ============================================================================
# Response Formatting
# ============================================================================

def format_response_for_console(answer: Dict[str, Any], question: str, elapsed_ms: float) -> str:
    """
    Format answer as human-readable console output.

    Args:
        answer: Answer dict from handler
        question: Original question
        elapsed_ms: Processing time in milliseconds

    Returns:
        Formatted string for console output
    """
    lines = []

    # Header
    lines.append("=" * 80)
    lines.append("QA PIPELINE RESULT")
    lines.append("=" * 80)

    # Question
    lines.append(f"\nQuestion: {question}")

    # Classification (if available)
    if isinstance(answer, dict):
        classification = answer.get('classification')
        if classification:
            lines.append(f"Classification: {classification}")

        # Answer text
        answer_text = answer.get('answer')
        if answer_text:
            lines.append(f"\nAnswer:\n{answer_text}")

        # Credence (if available)
        credence = answer.get('credence')
        if credence is not None:
            lines.append(f"\nCredence: {credence:.2f}")

        # Sources (if available)
        sources = answer.get('sources')
        if sources:
            lines.append(f"\nSources ({len(sources)}):")
            for source in sources[:5]:  # Limit to first 5 for console
                if isinstance(source, dict):
                    title = source.get('title', 'Unknown')
                    doi = source.get('doi', 'N/A')
                    lines.append(f"  - {title} ({doi})")
                else:
                    lines.append(f"  - {source}")
            if len(sources) > 5:
                lines.append(f"  ... and {len(sources) - 5} more sources")

        # Enrichment info
        if answer.get('enriched_with_prose_revision'):
            lines.append("\nNote: Answer was enriched with prose revision service")

    else:
        lines.append(f"\nAnswer: {answer}")

    # Timing
    lines.append(f"\nProcessing time: {elapsed_ms:.1f}ms")

    # Footer
    lines.append("=" * 80)

    return "\n".join(lines)


def format_response_for_json(
    answer: Dict[str, Any],
    question: str,
    elapsed_ms: float,
    success: bool = True,
    error: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Format answer as JSON for machine-readable output.

    Args:
        answer: Answer dict from handler
        question: Original question
        elapsed_ms: Processing time in milliseconds
        success: Whether processing succeeded
        error: Error message (if failed)

    Returns:
        Dict ready for JSON serialization
    """
    result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "success": success,
        "question": question,
        "processing_time_ms": elapsed_ms,
    }

    if success:
        if isinstance(answer, dict):
            result.update({
                "classification": answer.get('classification'),
                "answer": answer.get('answer'),
                "credence": answer.get('credence'),
                "sources": answer.get('sources', []),
                "enriched": {
                    "prose_revision": answer.get('enriched_with_prose_revision', False),
                },
            })
        else:
            result["answer"] = str(answer)
    else:
        result["error"] = error

    return result


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point for QA pipeline."""

    parser = argparse.ArgumentParser(
        description="QA Pipeline: Single entry point for question answering",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--question",
        type=str,
        required=True,
        help="The question to answer (e.g., 'What is ART?' or 'Show me all theories')",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose debug output",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as machine-readable JSON instead of human-friendly text",
    )
    parser.add_argument(
        "--no-enrichment",
        action="store_true",
        help="Skip optional answer enrichment services (faster)",
    )

    args = parser.parse_args()

    # Reconfigure logger if verbose
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info("=" * 80)
    logger.info("QA PIPELINE STARTING")
    logger.info(f"Question: {args.question}")
    logger.info(f"Verbose: {args.verbose}")
    logger.info(f"JSON output: {args.json}")
    logger.info("=" * 80)

    start_time = time.time()
    answer = None
    error_msg = None

    try:
        # Load QA handler
        logger.debug("Loading QA handler...")
        handler = load_qa_handler()

        # Process question
        logger.debug(f"Processing question: {args.question}")
        answer = handler.answer(args.question)

        # Enrich answer (optional)
        if not args.no_enrichment:
            logger.debug("Attempting answer enrichment...")
            answer = try_enrich_answer(answer)

        logger.info("Question processing completed successfully")

    except Exception as e:
        logger.error(f"Failed to process question: {e}", exc_info=args.verbose)
        error_msg = str(e)
        answer = None

    # Calculate elapsed time
    elapsed_ms = (time.time() - start_time) * 1000

    # Output results
    if args.json:
        output = format_response_for_json(
            answer or {},
            args.question,
            elapsed_ms,
            success=(error_msg is None),
            error=error_msg,
        )
        print(json.dumps(output, indent=2, default=str))
    else:
        if error_msg:
            print(f"\nERROR: {error_msg}\n", file=sys.stderr)
            print("=" * 80)
            print("QA PIPELINE FAILED")
            print("=" * 80)
            return 1
        else:
            print(format_response_for_console(answer or {}, args.question, elapsed_ms))

    return 0 if error_msg is None else 1


if __name__ == "__main__":
    sys.exit(main())
