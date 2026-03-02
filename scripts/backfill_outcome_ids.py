#!/usr/bin/env python3
"""
Backfill outcome_ids for beliefs with empty or NULL outcome_id.

This script builds a comprehensive mapping from raw consequent text to canonical
outcome_ids using the outcome vocabulary (terms, cognates, operationalizations).

It uses:
  1. Exact string matching (normalized)
  2. Token overlap matching
  3. Fuzzy substring matching (difflib)
  4. Confidence scoring based on match quality

Usage:
  python scripts/backfill_outcome_ids.py --dry-run
  python scripts/backfill_outcome_ids.py --commit
"""

import sqlite3
import json
import re
from pathlib import Path

from src.services.db_locator import get_web_db
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from difflib import SequenceMatcher
from collections import defaultdict
import sys


@dataclass
class VocabEntry:
    """Single vocabulary entry with all its aliases."""
    outcome_id: str
    name: str
    domain: str
    cognates: List[str]
    operationalizations: List[str]
    all_aliases: List[str]  # Complete list of name + cognates + operationalizations


class OutcomeVocabularyBuilder:
    """Build comprehensive mapping from text to outcome_ids."""

    def __init__(self, vocab_path: str):
        self.vocab_path = vocab_path
        self.vocab = self._load_vocab()
        self.vocab_entries = self._build_entries()
        self.lookup_map = self._build_lookup_map()

    def _load_vocab(self) -> dict:
        """Load the outcome vocabulary JSON."""
        with open(self.vocab_path, 'r') as f:
            return json.load(f)

    def _build_entries(self) -> Dict[str, VocabEntry]:
        """Build VocabEntry for each term in the vocabulary."""
        entries = {}
        for term in self.vocab['terms']:
            term_id = term['term_id']
            name = term['name']
            domain = term['domain']
            cognates = term.get('cognates', [])
            ops = term.get('operationalizations', [])

            # Combine all text aliases (case-insensitive)
            all_aliases = [name.lower()] + [c.lower() for c in cognates] + [o.lower() for o in ops]
            # Remove duplicates while preserving lowercase
            all_aliases = list(set(all_aliases))

            entries[term_id] = VocabEntry(
                outcome_id=term_id,
                name=name,
                domain=domain,
                cognates=cognates,
                operationalizations=ops,
                all_aliases=all_aliases
            )

        return entries

    def _build_lookup_map(self) -> Dict[str, str]:
        """Build fast lookup: normalized_text -> outcome_id."""
        lookup = {}
        for oid, entry in self.vocab_entries.items():
            for alias in entry.all_aliases:
                normalized = self._normalize(alias)
                if normalized:  # Skip empty strings
                    lookup[normalized] = oid
        return lookup

    def _normalize(self, text: str) -> str:
        """Normalize text for matching: lowercase, strip, remove punctuation."""
        if not text:
            return ""
        # Remove common punctuation, keep internal spaces
        text = text.lower().strip()
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text

    def _token_overlap(self, text1: str, text2: str) -> float:
        """Calculate token-level Jaccard similarity."""
        tokens1 = set(self._normalize(text1).split())
        tokens2 = set(self._normalize(text2).split())
        if not tokens1 or not tokens2:
            return 0.0
        intersection = len(tokens1 & tokens2)
        union = len(tokens1 | tokens2)
        return intersection / union if union > 0 else 0.0

    def _fuzzy_ratio(self, text1: str, text2: str) -> float:
        """Calculate fuzzy match ratio using SequenceMatcher."""
        norm1 = self._normalize(text1)
        norm2 = self._normalize(text2)
        return SequenceMatcher(None, norm1, norm2).ratio()

    def match(self, consequent_text: str) -> Tuple[Optional[str], float, str]:
        """
        Find best matching outcome_id for consequent text.

        Returns:
            (outcome_id, confidence, match_type) or (None, 0.0, "no_match")
        """
        if not consequent_text or not consequent_text.strip():
            return None, 0.0, "empty"

        norm_text = self._normalize(consequent_text)

        # Strategy 1: Exact match on normalized text
        if norm_text in self.lookup_map:
            outcome_id = self.lookup_map[norm_text]
            return outcome_id, 1.0, "exact"

        # Strategy 2: Try each vocabulary entry with fuzzy matching
        best_match = None
        best_score = 0.0
        best_type = "no_match"

        for oid, entry in self.vocab_entries.items():
            for alias in entry.all_aliases:
                # Token overlap
                token_score = self._token_overlap(consequent_text, alias)
                # Fuzzy similarity
                fuzzy_score = self._fuzzy_ratio(consequent_text, alias)
                # Combined (weighted average)
                combined = 0.4 * token_score + 0.6 * fuzzy_score

                if combined > best_score:
                    best_score = combined
                    best_match = oid
                    # Determine match type based on score
                    if combined >= 0.85:
                        best_type = "high_confidence"
                    elif combined >= 0.70:
                        best_type = "medium_confidence"
                    elif combined >= 0.50:
                        best_type = "low_confidence"

        # Only accept matches above a threshold
        threshold = 0.50
        if best_score >= threshold:
            return best_match, best_score, best_type

        return None, 0.0, "no_match"


class BackfillProcessor:
    """Process beliefs and backfill outcome_ids."""

    def __init__(self, db_path: str, vocab_builder: OutcomeVocabularyBuilder):
        self.db_path = db_path
        self.vocab_builder = vocab_builder

    def get_unmapped_beliefs(self) -> List[Tuple[str, str]]:
        """Get all beliefs with empty outcome_id.
        Returns: [(belief_id, content), ...]
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT belief_id, content
            FROM beliefs
            WHERE outcome_id IS NULL OR outcome_id = ''
            ORDER BY belief_id
        """)
        results = cursor.fetchall()
        conn.close()
        return results

    def process_belief(self, belief_id: str, content: str) -> Optional[Tuple[str, float, str]]:
        """
        Process single belief and return outcome mapping.
        Returns: (outcome_id, confidence, match_type) or None if no match
        """
        outcome_id, confidence, match_type = self.vocab_builder.match(content)
        return (outcome_id, confidence, match_type) if outcome_id else None

    def get_statistics(self) -> dict:
        """Get current database statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM beliefs")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM beliefs WHERE outcome_id IS NULL OR outcome_id = ''")
        unmapped = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM beliefs WHERE outcome_id IS NOT NULL AND outcome_id != ''")
        mapped = cursor.fetchone()[0]

        conn.close()

        return {
            'total': total,
            'mapped': mapped,
            'unmapped': unmapped,
            'unmapped_pct': 100.0 * unmapped / total if total > 0 else 0.0
        }

    def run_dry_run(self) -> dict:
        """Dry run: show what would be updated without modifying DB."""
        print("\n" + "=" * 100)
        print("DRY RUN: Scanning unmapped beliefs")
        print("=" * 100 + "\n")

        unmapped = self.get_unmapped_beliefs()
        results_by_type = defaultdict(int)
        high_confidence_matches = []
        medium_confidence_matches = []
        low_confidence_matches = []
        no_matches = []

        print(f"Processing {len(unmapped)} unmapped beliefs...\n")

        for belief_id, content in unmapped:
            match_result = self.process_belief(belief_id, content)

            if match_result:
                outcome_id, confidence, match_type = match_result
                results_by_type[match_type] += 1

                # Collect by confidence for reporting
                entry = (belief_id, content[:70], outcome_id, confidence)
                if match_type == "exact":
                    high_confidence_matches.append(entry)
                elif match_type == "high_confidence":
                    high_confidence_matches.append(entry)
                elif match_type == "medium_confidence":
                    medium_confidence_matches.append(entry)
                elif match_type == "low_confidence":
                    low_confidence_matches.append(entry)
            else:
                results_by_type["no_match"] += 1
                no_matches.append((belief_id, content[:70]))

        # Report
        print("MATCH RESULTS")
        print("-" * 100)
        print(f"Exact matches:           {results_by_type['exact']:5d}")
        print(f"High confidence (0.85+): {results_by_type['high_confidence']:5d}")
        print(f"Medium confidence (0.70-0.85): {results_by_type['medium_confidence']:5d}")
        print(f"Low confidence (0.50-0.70):    {results_by_type['low_confidence']:5d}")
        print(f"No match:                {results_by_type['no_match']:5d}")
        print("-" * 100)
        total_matched = sum(results_by_type.values()) - results_by_type['no_match']
        print(f"TOTAL TO BACKFILL:       {total_matched:5d}")
        print()

        # Show sample matches
        if high_confidence_matches:
            print("SAMPLE HIGH-CONFIDENCE MATCHES (first 5):")
            print("-" * 100)
            for bid, content, oid, conf in high_confidence_matches[:5]:
                print(f"  {bid[:20]:20s} -> {oid:25s} (conf={conf:.3f})")
                print(f"    Content: {content}")
            print()

        if medium_confidence_matches:
            print("SAMPLE MEDIUM-CONFIDENCE MATCHES (first 5):")
            print("-" * 100)
            for bid, content, oid, conf in medium_confidence_matches[:5]:
                print(f"  {bid[:20]:20s} -> {oid:25s} (conf={conf:.3f})")
                print(f"    Content: {content}")
            print()

        if low_confidence_matches:
            print("SAMPLE LOW-CONFIDENCE MATCHES (first 5):")
            print("-" * 100)
            for bid, content, oid, conf in low_confidence_matches[:5]:
                print(f"  {bid[:20]:20s} -> {oid:25s} (conf={conf:.3f})")
                print(f"    Content: {content}")
            print()

        if no_matches:
            print("UNMATCHED BELIEFS (cannot map):")
            print("-" * 100)
            for bid, content in no_matches:
                print(f"  {bid[:20]:20s}")
                print(f"    Content: {content}")
            print()

        stats_before = self.get_statistics()
        print("DATABASE STATISTICS")
        print("-" * 100)
        print(f"Current state:")
        print(f"  Total beliefs:        {stats_before['total']:,}")
        print(f"  Mapped:               {stats_before['mapped']:,} ({100-stats_before['unmapped_pct']:.1f}%)")
        print(f"  Unmapped:             {stats_before['unmapped']:,} ({stats_before['unmapped_pct']:.1f}%)")
        print()
        print(f"After backfill (projected):")
        projected_mapped = stats_before['mapped'] + total_matched
        projected_unmapped = stats_before['unmapped'] - total_matched
        projected_pct = 100.0 * projected_unmapped / stats_before['total'] if stats_before['total'] > 0 else 0.0
        print(f"  Mapped:               {projected_mapped:,} ({100-projected_pct:.1f}%)")
        print(f"  Unmapped:             {projected_unmapped:,} ({projected_pct:.1f}%)")
        print(f"  Improvement:          {stats_before['unmapped_pct'] - projected_pct:.1f} percentage points")
        print()

        return {
            'total_beliefs': len(unmapped),
            'results_by_type': dict(results_by_type),
            'total_matched': total_matched,
            'stats_before': stats_before,
            'projected_unmapped': projected_unmapped
        }

    def run_commit(self) -> dict:
        """Actually update the database with mapped outcome_ids."""
        print("\n" + "=" * 100)
        print("COMMIT MODE: Updating database")
        print("=" * 100 + "\n")

        unmapped = self.get_unmapped_beliefs()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        updated_count = 0
        update_list = []

        for belief_id, content in unmapped:
            match_result = self.process_belief(belief_id, content)
            if match_result:
                outcome_id, confidence, match_type = match_result
                update_list.append((outcome_id, belief_id))
                updated_count += 1

        # Perform batch update
        if update_list:
            cursor.executemany(
                "UPDATE beliefs SET outcome_id = ? WHERE belief_id = ?",
                update_list
            )
            conn.commit()
            print(f"Updated {updated_count} beliefs with outcome_ids")
        else:
            print("No matches found, no updates made")

        # Final statistics
        stats_after = self.get_statistics()
        print()
        print("DATABASE STATISTICS (after commit)")
        print("-" * 100)
        print(f"Total beliefs:        {stats_after['total']:,}")
        print(f"Mapped:               {stats_after['mapped']:,} ({100-stats_after['unmapped_pct']:.1f}%)")
        print(f"Unmapped:             {stats_after['unmapped']:,} ({stats_after['unmapped_pct']:.1f}%)")
        print()

        conn.close()
        return {
            'updated': updated_count,
            'stats_after': stats_after
        }


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Backfill outcome_ids for beliefs with empty outcome_id'
    )
    parser.add_argument(
        '--db',
        default=str(get_web_db()),
        help='Path to SQLite database (default: data/web_persistence.db)'
    )
    parser.add_argument(
        '--vocab',
        default='contracts/outcome_vocab/outcome_vocab.json',
        help='Path to outcome vocabulary (default: contracts/outcome_vocab/outcome_vocab.json)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run in dry-run mode (no database changes)'
    )
    parser.add_argument(
        '--commit',
        action='store_true',
        help='Actually update the database'
    )

    args = parser.parse_args()

    # Validate paths
    if not Path(args.db).exists():
        print(f"Error: Database not found: {args.db}", file=sys.stderr)
        sys.exit(1)

    if not Path(args.vocab).exists():
        print(f"Error: Vocabulary not found: {args.vocab}", file=sys.stderr)
        sys.exit(1)

    # Build vocabulary and processor
    print("Loading outcome vocabulary...")
    builder = OutcomeVocabularyBuilder(args.vocab)
    print(f"  Loaded {len(builder.vocab_entries)} vocabulary terms")
    print(f"  Built {len(builder.lookup_map)} indexed aliases\n")

    processor = BackfillProcessor(args.db, builder)

    # Run mode
    if args.dry_run:
        processor.run_dry_run()
    elif args.commit:
        # Run dry-run first to show what will happen
        processor.run_dry_run()
        print("\n" + "=" * 100)
        response = input("Proceed with commit? (yes/no): ")
        if response.lower() == 'yes':
            processor.run_commit()
        else:
            print("Commit cancelled.")
    else:
        print("Please specify --dry-run or --commit")
        sys.exit(1)


if __name__ == '__main__':
    main()
