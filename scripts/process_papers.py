#!/usr/bin/env python3
"""
MVP-2: Batch Paper Processing Script
=====================================

Processes multiple papers through Article Eater pipeline and accumulates results
into a persistent web of belief.

Usage:
    python scripts/process_papers.py --config scripts/process_config.yaml
    python scripts/process_papers.py --bundles /path/to/job_bundles --limit 10
    python scripts/process_papers.py --list papers.txt --bundles /path/to/bundles

Features:
- Iterates over job bundles or paper list
- Calls AE extraction pipeline on each paper
- Accumulates beliefs using WebAccumulator (MVP-1)
- Circuit breaker: pauses after N consecutive failures
- Progress tracking and summary report

Author: Claude Code (MVP-2)
Created: 2026-02-11
"""

import argparse
import json
import logging
import sys
import time
from dataclasses import dataclass, field

# Optional YAML support
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.tasks.pipeline import run_from_contract_bundle
from src.services.web_accumulator import get_accumulator, WebAccumulator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


@dataclass
class ProcessingConfig:
    """Configuration for batch processing."""

    # Input sources
    bundles_dir: Optional[Path] = None
    paper_list_file: Optional[Path] = None

    # Processing options
    profile: str = "standard"
    hitl: str = "auto"
    limit: Optional[int] = None
    skip_already_processed: bool = True

    # Output options
    output_dir: Optional[Path] = None
    accumulator_db: Optional[Path] = None
    accumulator_json: Optional[Path] = None

    # Circuit breaker
    max_consecutive_failures: int = 3
    pause_on_circuit_break: bool = True

    # Progress options
    progress_file: Optional[Path] = None
    verbose: bool = False

    @classmethod
    def from_yaml(cls, path: Path) -> 'ProcessingConfig':
        """Load configuration from YAML file."""
        if not HAS_YAML:
            raise ImportError(
                "PyYAML is required for YAML config files. "
                "Install with: pip install pyyaml"
            )
        with open(path) as f:
            data = yaml.safe_load(f)

        config = cls()

        # Input sources
        if data.get('bundles_dir'):
            config.bundles_dir = Path(data['bundles_dir'])
        if data.get('paper_list_file'):
            config.paper_list_file = Path(data['paper_list_file'])

        # Processing options
        config.profile = data.get('profile', 'standard')
        config.hitl = data.get('hitl', 'auto')
        config.limit = data.get('limit')
        config.skip_already_processed = data.get('skip_already_processed', True)

        # Output options
        if data.get('output_dir'):
            config.output_dir = Path(data['output_dir'])
        if data.get('accumulator_db'):
            config.accumulator_db = Path(data['accumulator_db'])
        if data.get('accumulator_json'):
            config.accumulator_json = Path(data['accumulator_json'])

        # Circuit breaker
        config.max_consecutive_failures = data.get('max_consecutive_failures', 3)
        config.pause_on_circuit_break = data.get('pause_on_circuit_break', True)

        # Progress options
        if data.get('progress_file'):
            config.progress_file = Path(data['progress_file'])
        config.verbose = data.get('verbose', False)

        return config


@dataclass
class ProcessingResult:
    """Result of processing a single paper."""
    paper_id: str
    success: bool
    status: str
    beliefs_added: int = 0
    constraints_added: int = 0
    duration_seconds: float = 0.0
    error_message: Optional[str] = None
    output_path: Optional[Path] = None


@dataclass
class BatchProgress:
    """Tracks progress of batch processing."""
    total: int = 0
    processed: int = 0
    succeeded: int = 0
    failed: int = 0
    skipped: int = 0
    beliefs_total: int = 0
    constraints_total: int = 0
    consecutive_failures: int = 0
    start_time: Optional[datetime] = None
    results: List[ProcessingResult] = field(default_factory=list)

    def record_success(self, result: ProcessingResult):
        """Record a successful processing."""
        self.processed += 1
        self.succeeded += 1
        self.beliefs_total += result.beliefs_added
        self.constraints_total += result.constraints_added
        self.consecutive_failures = 0
        self.results.append(result)

    def record_failure(self, result: ProcessingResult):
        """Record a failed processing."""
        self.processed += 1
        self.failed += 1
        self.consecutive_failures += 1
        self.results.append(result)

    def record_skip(self, paper_id: str, reason: str):
        """Record a skipped paper."""
        self.skipped += 1
        self.results.append(ProcessingResult(
            paper_id=paper_id,
            success=True,
            status=f"skipped: {reason}"
        ))

    def elapsed_seconds(self) -> float:
        """Get elapsed time in seconds."""
        if self.start_time is None:
            return 0.0
        return (datetime.now(timezone.utc) - self.start_time).total_seconds()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'total': self.total,
            'processed': self.processed,
            'succeeded': self.succeeded,
            'failed': self.failed,
            'skipped': self.skipped,
            'beliefs_total': self.beliefs_total,
            'constraints_total': self.constraints_total,
            'elapsed_seconds': self.elapsed_seconds(),
            'consecutive_failures': self.consecutive_failures,
            'results': [
                {
                    'paper_id': r.paper_id,
                    'success': r.success,
                    'status': r.status,
                    'beliefs_added': r.beliefs_added,
                    'constraints_added': r.constraints_added,
                    'duration_seconds': r.duration_seconds,
                    'error': r.error_message,
                    'output_path': str(r.output_path) if r.output_path else None
                }
                for r in self.results
            ]
        }


class BatchProcessor:
    """
    Batch processor for Article Eater pipeline.

    Processes multiple papers, accumulates beliefs, and provides progress tracking.
    """

    def __init__(
        self,
        config: ProcessingConfig,
        accumulator: Optional[WebAccumulator] = None
    ):
        self.config = config
        self.accumulator = accumulator or get_accumulator(
            db_path=config.accumulator_db,
            json_path=config.accumulator_json
        )
        self.progress = BatchProgress()
        self._circuit_broken = False

    def discover_bundles(self) -> List[Path]:
        """Discover job bundles to process."""
        bundles = []

        if self.config.bundles_dir:
            bundles_dir = self.config.bundles_dir
            if bundles_dir.exists():
                # Find all directories containing paper.json
                for bundle_dir in bundles_dir.iterdir():
                    if bundle_dir.is_dir():
                        paper_json = bundle_dir / "paper.json"
                        if paper_json.exists():
                            bundles.append(bundle_dir)

        if self.config.paper_list_file and self.config.paper_list_file.exists():
            # Read paper IDs from file and find matching bundles
            with open(self.config.paper_list_file) as f:
                paper_ids = [line.strip() for line in f if line.strip()]

            if self.config.bundles_dir:
                for paper_id in paper_ids:
                    # Try to find matching bundle
                    safe_id = self._make_safe_id(paper_id)
                    for bundle_dir in self.config.bundles_dir.iterdir():
                        if bundle_dir.is_dir() and safe_id in bundle_dir.name:
                            paper_json = bundle_dir / "paper.json"
                            if paper_json.exists() and bundle_dir not in bundles:
                                bundles.append(bundle_dir)
                                break

        # Apply limit
        if self.config.limit and len(bundles) > self.config.limit:
            bundles = bundles[:self.config.limit]

        return sorted(bundles)  # Sort for consistent ordering

    def _make_safe_id(self, paper_id: str) -> str:
        """Convert paper_id to safe format for filename matching."""
        return paper_id.replace(':', '_').replace('/', '_').replace('.', '_')[:50]

    def process_bundle(self, bundle_path: Path) -> ProcessingResult:
        """Process a single job bundle through the pipeline."""
        start_time = time.time()

        # Read paper.json for paper_id
        paper_json = bundle_path / "paper.json"
        with open(paper_json) as f:
            paper_meta = json.load(f)
        paper_id = paper_meta.get('paper_id', bundle_path.name)
        publication_year = paper_meta.get('year')

        try:
            # Create output directory
            if self.config.output_dir:
                output_dir = self.config.output_dir / bundle_path.name
            else:
                output_dir = bundle_path.parent / f"output_{bundle_path.name}"
            output_dir.mkdir(parents=True, exist_ok=True)

            # Run the extraction pipeline
            result = run_from_contract_bundle(
                in_dir=bundle_path,
                out_dir=output_dir,
                profile=self.config.profile,
                hitl=self.config.hitl
            )

            duration = time.time() - start_time

            # Check result status
            status = result.get('status', 'unknown')

            if status in ('SUCCESS', 'PARTIAL_SUCCESS'):
                # Accumulate into web of belief
                web_state_path = output_dir / "web_state.json"

                beliefs_added = 0
                constraints_added = 0

                if web_state_path.exists():
                    accum_result = self.accumulator.integrate_web_state_file(
                        web_state_path
                    )
                    if accum_result.get('status') == 'success':
                        beliefs_added = accum_result.get('beliefs_added', 0)
                        constraints_added = accum_result.get('constraints_added', 0)

                return ProcessingResult(
                    paper_id=paper_id,
                    success=True,
                    status=status,
                    beliefs_added=beliefs_added,
                    constraints_added=constraints_added,
                    duration_seconds=duration,
                    output_path=output_dir
                )
            else:
                return ProcessingResult(
                    paper_id=paper_id,
                    success=False,
                    status=status,
                    duration_seconds=duration,
                    error_message=result.get('error', 'Unknown error'),
                    output_path=output_dir
                )

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Error processing {paper_id}: {e}")
            return ProcessingResult(
                paper_id=paper_id,
                success=False,
                status='ERROR',
                duration_seconds=duration,
                error_message=str(e)
            )

    def run(self) -> BatchProgress:
        """Run batch processing on all discovered bundles."""
        bundles = self.discover_bundles()

        self.progress = BatchProgress(
            total=len(bundles),
            start_time=datetime.now(timezone.utc)
        )

        logger.info(f"Starting batch processing of {len(bundles)} papers")
        logger.info(f"Profile: {self.config.profile}, HITL: {self.config.hitl}")

        for i, bundle_path in enumerate(bundles):
            # Check circuit breaker
            if self.progress.consecutive_failures >= self.config.max_consecutive_failures:
                if self.config.pause_on_circuit_break:
                    logger.warning(
                        f"Circuit breaker triggered after "
                        f"{self.progress.consecutive_failures} consecutive failures"
                    )
                    self._circuit_broken = True
                    break

            # Read paper_id for logging
            paper_json = bundle_path / "paper.json"
            with open(paper_json) as f:
                paper_meta = json.load(f)
            paper_id = paper_meta.get('paper_id', bundle_path.name)

            # Check if already processed
            if self.config.skip_already_processed:
                stats = self.accumulator.get_stats()
                if paper_id in stats.papers_processed:
                    logger.info(f"[{i+1}/{len(bundles)}] Skipping {paper_id} (already processed)")
                    self.progress.record_skip(paper_id, "already processed")
                    continue

            logger.info(f"[{i+1}/{len(bundles)}] Processing {paper_id}")

            result = self.process_bundle(bundle_path)

            if result.success:
                self.progress.record_success(result)
                logger.info(
                    f"  SUCCESS: +{result.beliefs_added} beliefs, "
                    f"+{result.constraints_added} constraints"
                )
            else:
                self.progress.record_failure(result)
                logger.warning(f"  FAILED: {result.error_message}")

            # Save progress periodically
            if self.config.progress_file and (i + 1) % 10 == 0:
                self._save_progress()

        # Final progress save
        if self.config.progress_file:
            self._save_progress()

        # Log summary
        self._log_summary()

        return self.progress

    def _save_progress(self):
        """Save progress to file."""
        if self.config.progress_file:
            self.config.progress_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config.progress_file, 'w') as f:
                json.dump(self.progress.to_dict(), f, indent=2, default=str)

    def _log_summary(self):
        """Log processing summary."""
        elapsed = self.progress.elapsed_seconds()
        avg_time = elapsed / max(1, self.progress.processed)

        logger.info("=" * 60)
        logger.info("BATCH PROCESSING COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Total papers:     {self.progress.total}")
        logger.info(f"Processed:        {self.progress.processed}")
        logger.info(f"Succeeded:        {self.progress.succeeded}")
        logger.info(f"Failed:           {self.progress.failed}")
        logger.info(f"Skipped:          {self.progress.skipped}")
        logger.info("-" * 60)
        logger.info(f"Beliefs added:    {self.progress.beliefs_total}")
        logger.info(f"Constraints:      {self.progress.constraints_total}")
        logger.info("-" * 60)
        logger.info(f"Elapsed time:     {elapsed:.1f}s")
        logger.info(f"Avg per paper:    {avg_time:.1f}s")

        if self._circuit_broken:
            logger.warning("Processing stopped by circuit breaker")

        # Get final accumulator stats
        stats = self.accumulator.get_stats()
        logger.info("-" * 60)
        logger.info("ACCUMULATED WEB STATS:")
        logger.info(f"  Total beliefs:      {stats.total_beliefs}")
        logger.info(f"  Total constraints:  {stats.total_constraints}")
        logger.info(f"  Papers processed:   {len(stats.papers_processed)}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Batch process papers through Article Eater pipeline'
    )
    parser.add_argument(
        '--config',
        type=Path,
        help='Path to YAML configuration file'
    )
    parser.add_argument(
        '--bundles',
        type=Path,
        help='Directory containing job bundles'
    )
    parser.add_argument(
        '--list',
        type=Path,
        dest='paper_list',
        help='File containing paper IDs (one per line)'
    )
    parser.add_argument(
        '--output',
        type=Path,
        help='Output directory for results'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Maximum number of papers to process'
    )
    parser.add_argument(
        '--profile',
        choices=['fast', 'standard', 'deep'],
        default='standard',
        help='Processing profile'
    )
    parser.add_argument(
        '--hitl',
        choices=['off', 'auto', 'required'],
        default='auto',
        help='Human-in-the-loop mode'
    )
    parser.add_argument(
        '--max-failures',
        type=int,
        default=3,
        help='Circuit breaker: max consecutive failures before pause'
    )
    parser.add_argument(
        '--no-skip-processed',
        action='store_true',
        help='Re-process already processed papers'
    )
    parser.add_argument(
        '--progress-file',
        type=Path,
        help='File to save progress updates'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    # Load or build config
    if args.config:
        config = ProcessingConfig.from_yaml(args.config)
    else:
        config = ProcessingConfig()

    # Override with command-line arguments
    if args.bundles:
        config.bundles_dir = args.bundles
    if args.paper_list:
        config.paper_list_file = args.paper_list
    if args.output:
        config.output_dir = args.output
    if args.limit:
        config.limit = args.limit
    config.profile = args.profile
    config.hitl = args.hitl
    config.max_consecutive_failures = args.max_failures
    if args.no_skip_processed:
        config.skip_already_processed = False
    if args.progress_file:
        config.progress_file = args.progress_file
    config.verbose = args.verbose

    # Validate config
    if not config.bundles_dir:
        parser.error("--bundles or config.bundles_dir is required")

    if config.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Run batch processing
    processor = BatchProcessor(config)
    progress = processor.run()

    # Exit with error code if any failures
    if progress.failed > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
