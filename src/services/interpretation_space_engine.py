"""
Interpretation Space Engine

Generates interpretive questions from T2 mechanism templates.

This engine realizes the R₁-R₄ closure operators by creating question sets
that guide users through definitional, evidential, applied, and dialectical
interrogation of each template's mechanism.

Each template generates exactly 4 question types:
  1. Definitional: "What is [mechanism]?" (R₁: definition/concept)
  2. Evidential: "What evidence supports [mechanism]?" (R₂: warrant chain)
  3. Applied: "What are the design implications?" (R₃: application)
  4. Dialectical: "What debates exist about [mechanism]?" (R₄: alternatives)

The generated questions are stored in data/interpretation_space/questions.json
as a searchable registry, enabling question-driven exploration of the template
library.

Module design:
  - QuestionRecord: Serializable question dataclass
  - InterpretationSpaceEngine: Core generation logic
  - CLI interface for standalone execution
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import sys

LOGGER = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# Data Models
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class QuestionRecord:
    """
    A single generated question from an interpretation space query.

    Fields:
      id: Unique identifier (template_id::question_type::index)
      text: The question itself
      type: One of "definitional", "evidential", "applied", "dialectical"
      source_template: The template_id this question was generated from
      mechanism_name: The mechanism being interrogated (extracted from template)
      generated_date: ISO timestamp when question was created
      template_name: Full template name for context
      confidence: How confident we are in this question (0.0-1.0)
    """
    id: str
    text: str
    type: str
    source_template: str
    mechanism_name: str
    generated_date: str
    template_name: str = ""
    confidence: float = 0.8

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return asdict(self)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> QuestionRecord:
        """Reconstruct from dict."""
        return QuestionRecord(**d)


@dataclass
class CoverageStats:
    """Statistics on interpretation space coverage."""
    total_templates: int
    templates_with_questions: int
    total_questions_generated: int
    coverage_percentage: float
    questions_by_type: Dict[str, int] = field(default_factory=dict)
    last_generation_date: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return asdict(self)


# ═══════════════════════════════════════════════════════════════════════════
# Interpretation Space Engine
# ═══════════════════════════════════════════════════════════════════════════

class InterpretationSpaceEngine:
    """
    Generates interpretation space questions from T2 mechanism templates.

    Reads template JSON files from data/templates/, extracts mechanism names
    and theory links, and generates 4 question types per template.

    Storage: Generated questions are persisted to data/interpretation_space/questions.json
    """

    def __init__(self, repo_root: Optional[Path] = None):
        """
        Initialize the engine.

        Args:
          repo_root: Root of Article_Eater repo. If None, infers from __file__.
        """
        if repo_root is None:
            # Infer from this file's location: src/services/interpretation_space_engine.py
            repo_root = Path(__file__).parent.parent.parent

        self.repo_root = repo_root
        self.templates_dir = repo_root / "data" / "templates"
        self.output_dir = repo_root / "data" / "interpretation_space"
        self.questions_file = self.output_dir / "questions.json"

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.questions: Dict[str, QuestionRecord] = {}
        self.template_index: Dict[str, Dict[str, Any]] = {}

    def load_existing_questions(self) -> int:
        """
        Load previously generated questions from disk.

        Returns:
          Number of questions loaded
        """
        if self.questions_file.exists():
            try:
                with open(self.questions_file, 'r') as f:
                    data = json.load(f)
                    questions_list = data.get('questions', [])
                    self.questions = {
                        q['id']: QuestionRecord.from_dict(q)
                        for q in questions_list
                    }
                    LOGGER.info(f"Loaded {len(self.questions)} existing questions")
                    return len(self.questions)
            except Exception as e:
                LOGGER.error(f"Error loading questions: {e}")
        return 0

    def discover_templates(self) -> int:
        """
        Discover all template JSON files in data/templates/.

        Returns:
          Number of templates found
        """
        if not self.templates_dir.exists():
            LOGGER.warning(f"Templates directory not found: {self.templates_dir}")
            return 0

        template_files = sorted(self.templates_dir.glob("*.json"))
        LOGGER.info(f"Discovered {len(template_files)} template files")

        for template_file in template_files:
            try:
                with open(template_file, 'r') as f:
                    template_data = json.load(f)
                    template_id = template_data.get('template_id', template_file.stem)
                    self.template_index[template_id] = template_data
            except Exception as e:
                LOGGER.error(f"Error reading {template_file}: {e}")

        return len(self.template_index)

    def extract_mechanism_name(self, template_data: Dict[str, Any]) -> str:
        """
        Extract mechanism name from template.

        Tries multiple fields in order of preference:
          1. mechanism_chain[0].description (for causal chain templates)
          2. higher_order_principle
          3. name
          4. template_id
        """
        # Try mechanism chain
        mechanism_chain = template_data.get('mechanism_chain', [])
        if mechanism_chain and len(mechanism_chain) > 0:
            first_step = mechanism_chain[0]
            description = first_step.get('description', '')
            if description:
                # Extract first phrase before "->" or ":"
                parts = description.split('→')
                if len(parts) > 0:
                    return parts[0].strip()

        # Try higher-order principle
        hop = template_data.get('higher_order_principle', '')
        if hop:
            return hop[:80]  # Truncate to reasonable length

        # Fallback to name
        name = template_data.get('name', '')
        if name:
            return name[:80]

        # Last resort
        return template_data.get('template_id', 'unknown')

    def generate_questions_for_template(
        self, template_id: str, template_data: Dict[str, Any]
    ) -> List[QuestionRecord]:
        """
        Generate the 4 question types for a single template.

        Args:
          template_id: The template identifier
          template_data: The template JSON object

        Returns:
          List of 4 QuestionRecord objects
        """
        questions = []
        mechanism = self.extract_mechanism_name(template_data)
        template_name = template_data.get('name', template_id)
        now = datetime.now(timezone.utc).isoformat()

        # Define question templates for each type
        question_templates = [
            {
                'type': 'definitional',
                'template': 'What is {mechanism}? How is it defined or conceptualized in {template}?',
                'description': 'R₁ closure: concept and definition'
            },
            {
                'type': 'evidential',
                'template': 'What evidence or empirical findings support the mechanism of {mechanism}?',
                'description': 'R₂ closure: warrant chain and evidence'
            },
            {
                'type': 'applied',
                'template': 'What are the design implications of {mechanism}? How should understanding this mechanism change design practice?',
                'description': 'R₃ closure: application to design'
            },
            {
                'type': 'dialectical',
                'template': 'What debates, controversies, or competing explanations surround {mechanism}?',
                'description': 'R₄ closure: alternatives and critiques'
            }
        ]

        for idx, q_spec in enumerate(question_templates):
            question_text = q_spec['template'].format(
                mechanism=mechanism,
                template=template_name
            )

            question_id = f"{template_id}::{q_spec['type']}::{idx}"

            question = QuestionRecord(
                id=question_id,
                text=question_text,
                type=q_spec['type'],
                source_template=template_id,
                mechanism_name=mechanism,
                generated_date=now,
                template_name=template_name,
                confidence=0.8
            )
            questions.append(question)

        return questions

    def generate_all_questions(self, refresh: bool = False) -> int:
        """
        Generate questions for all templates.

        Args:
          refresh: If True, regenerate all questions. If False, skip templates
                   that already have questions.

        Returns:
          Total number of questions now in memory
        """
        if not refresh:
            # Load existing
            self.load_existing_questions()

        # Discover templates if not already done
        if not self.template_index:
            self.discover_templates()

        initial_count = len(self.questions)
        newly_generated = 0

        for template_id, template_data in self.template_index.items():
            # Skip if already has questions (unless refreshing)
            existing_for_template = [
                q for q in self.questions.values()
                if q.source_template == template_id
            ]

            if existing_for_template and not refresh:
                continue

            # Generate questions
            new_questions = self.generate_questions_for_template(
                template_id, template_data
            )
            for q in new_questions:
                self.questions[q.id] = q
                newly_generated += 1

        LOGGER.info(
            f"Generated {newly_generated} new questions "
            f"({initial_count} existing, {len(self.questions)} total)"
        )

        return len(self.questions)

    def save_questions(self) -> Path:
        """
        Save generated questions to data/interpretation_space/questions.json.

        Returns:
          Path to saved file
        """
        output_data = {
            'metadata': {
                'generated_at': datetime.now(timezone.utc).isoformat(),
                'total_questions': len(self.questions),
                'source': 'InterpretationSpaceEngine'
            },
            'questions': [q.to_dict() for q in self.questions.values()]
        }

        with open(self.questions_file, 'w') as f:
            json.dump(output_data, f, indent=2)

        LOGGER.info(f"Saved {len(self.questions)} questions to {self.questions_file}")
        return self.questions_file

    def get_questions_by_type(self, question_type: str) -> List[QuestionRecord]:
        """
        Retrieve all questions of a specific type.

        Args:
          question_type: One of "definitional", "evidential", "applied", "dialectical"

        Returns:
          List of matching questions
        """
        return [
            q for q in self.questions.values()
            if q.type == question_type
        ]

    def get_questions_for_template(self, template_id: str) -> List[QuestionRecord]:
        """
        Retrieve all questions generated from a specific template.

        Args:
          template_id: The template identifier

        Returns:
          List of 4 questions (one per type)
        """
        return [
            q for q in self.questions.values()
            if q.source_template == template_id
        ]

    def get_coverage_stats(self) -> CoverageStats:
        """
        Compute interpretation space coverage statistics.

        Returns:
          CoverageStats object with detailed metrics
        """
        total_templates = len(self.template_index)
        templates_with_questions = len(set(
            q.source_template for q in self.questions.values()
        ))

        questions_by_type = {}
        for question_type in ['definitional', 'evidential', 'applied', 'dialectical']:
            questions_by_type[question_type] = len(
                self.get_questions_by_type(question_type)
            )

        coverage_pct = (
            (templates_with_questions / total_templates * 100)
            if total_templates > 0 else 0.0
        )

        return CoverageStats(
            total_templates=total_templates,
            templates_with_questions=templates_with_questions,
            total_questions_generated=len(self.questions),
            coverage_percentage=coverage_pct,
            questions_by_type=questions_by_type,
            last_generation_date=datetime.now(timezone.utc).isoformat()
        )

    def print_coverage_report(self) -> None:
        """Print human-readable coverage report to stdout."""
        stats = self.get_coverage_stats()

        print("\n" + "="*70)
        print("INTERPRETATION SPACE COVERAGE REPORT")
        print("="*70)
        print(f"Total Templates:           {stats.total_templates}")
        print(f"Templates with Questions:  {stats.templates_with_questions}")
        print(f"Coverage:                  {stats.coverage_percentage:.1f}%")
        print(f"Total Questions:           {stats.total_questions_generated}")
        print()
        print("Questions by Type:")
        for qtype, count in sorted(stats.questions_by_type.items()):
            print(f"  {qtype:15s}: {count:4d}")
        print("="*70 + "\n")


# ═══════════════════════════════════════════════════════════════════════════
# CLI Interface
# ═══════════════════════════════════════════════════════════════════════════

def main():
    """
    Command-line interface for interpretation space generation.

    Usage:
      python -m src.services.interpretation_space_engine [--refresh] [--report]
    """
    import argparse

    parser = argparse.ArgumentParser(
        description='Generate interpretation space questions from templates'
    )
    parser.add_argument(
        '--refresh',
        action='store_true',
        help='Regenerate all questions (overwrite existing)'
    )
    parser.add_argument(
        '--report',
        action='store_true',
        help='Print coverage report after generation'
    )
    parser.add_argument(
        '--repo-root',
        type=Path,
        default=None,
        help='Path to Article_Eater repo root'
    )

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create engine
    engine = InterpretationSpaceEngine(repo_root=args.repo_root)

    # Generate
    print("Discovering templates...")
    engine.discover_templates()

    print(f"Generating interpretation space questions...")
    count = engine.generate_all_questions(refresh=args.refresh)

    # Save
    engine.save_questions()

    # Report
    if args.report:
        engine.print_coverage_report()

    print(f"\nSuccess: Generated {count} questions")
    print(f"Saved to: {engine.questions_file}")


if __name__ == '__main__':
    main()
