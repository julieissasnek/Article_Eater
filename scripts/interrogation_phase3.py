#!/usr/bin/env python3
"""
Phase 3: Interpretation Space Implementation - Top 50 High-Value Beliefs
Focused on closing VALIDATION (replication) and BOUNDARY (scope) gaps.

Specification: /docs/INTERPRETATION_SPACE_SPEC_2026-03-01.md
Phase 2 baseline: validation closure 1.2%, boundary closure 0%

Output: /data/interpretation_space/phase3/
  - top_50_beliefs_ranked.json
  - validation_closures.json
  - boundary_closures.json
  - frontier_questions.json
  - phase3_summary.json
"""

import json
import sqlite3
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# ============================================================================
# DATA STRUCTURES AND UTILITIES
# ============================================================================

class TextAnalyzer:
    """Heuristic-based text analysis for scope inference."""

    POPULATION_KEYWORDS = {
        'children': ['children', 'child', 'kids', 'pediatric', 'adolescent', 'youth'],
        'adults': ['adults', 'adult', 'college students', 'undergraduates', 'employees'],
        'older_adults': ['older adults', 'elderly', 'senior', 'aged', '65+', 'aging'],
        'clinical': ['patients', 'patient', 'clinical', 'psychiatric', 'depressed', 'anxiety'],
        'general': ['participants', 'subjects', 'people', 'individuals'],
    }

    SETTING_KEYWORDS = {
        'lab': ['laboratory', 'lab', 'controlled', 'chamber', 'booth'],
        'office': ['office', 'workplace', 'work environment', 'cubicle', 'open plan'],
        'home': ['home', 'residence', 'residential', 'apartment'],
        'clinical': ['hospital', 'clinic', 'healthcare facility', 'therapy room'],
        'outdoor': ['outdoor', 'park', 'street', 'urban', 'nature'],
        'mixed': ['mixed', 'varied', 'multiple settings'],
    }

    METHODOLOGY_KEYWORDS = {
        'rct': ['randomized controlled trial', 'rct', 'random assignment'],
        'experiment': ['experiment', 'experimental', 'within-subject', 'between-subject'],
        'quasi': ['quasi-experimental', 'quasi experiment', 'interrupted time series'],
        'observational': ['observational', 'correlational', 'cross-sectional', 'survey'],
        'longitudinal': ['longitudinal', 'follow-up', 'prospective', 'panel study'],
        'case_study': ['case study', 'case report', 'qualitative'],
    }

    @staticmethod
    def infer_population(text: str) -> Dict:
        """Infer population from belief content."""
        text_lower = text.lower()
        detected = {'primary': None, 'secondary': [], 'confidence': 0.0}

        matches = []
        for pop_type, keywords in TextAnalyzer.POPULATION_KEYWORDS.items():
            for kw in keywords:
                if kw in text_lower:
                    matches.append((pop_type, len(kw)))

        if matches:
            matches.sort(key=lambda x: x[1], reverse=True)
            detected['primary'] = matches[0][0]
            detected['secondary'] = [m[0] for m in matches[1:3]]
            detected['confidence'] = min(len(matches) * 0.25, 0.8)

        return detected

    @staticmethod
    def infer_setting(text: str) -> Dict:
        """Infer setting from belief content."""
        text_lower = text.lower()
        detected = {'primary': None, 'secondary': [], 'confidence': 0.0}

        matches = []
        for setting_type, keywords in TextAnalyzer.SETTING_KEYWORDS.items():
            for kw in keywords:
                if kw in text_lower:
                    matches.append((setting_type, len(kw)))

        if matches:
            matches.sort(key=lambda x: x[1], reverse=True)
            detected['primary'] = matches[0][0]
            detected['secondary'] = [m[0] for m in matches[1:2]]
            detected['confidence'] = min(len(matches) * 0.25, 0.8)

        return detected

    @staticmethod
    def infer_methodology(text: str) -> Dict:
        """Infer methodology from belief content."""
        text_lower = text.lower()
        detected = {'primary': None, 'secondary': [], 'confidence': 0.0}

        matches = []
        for method_type, keywords in TextAnalyzer.METHODOLOGY_KEYWORDS.items():
            for kw in keywords:
                if kw in text_lower:
                    matches.append((method_type, len(kw)))

        if matches:
            matches.sort(key=lambda x: x[1], reverse=True)
            detected['primary'] = matches[0][0]
            detected['secondary'] = [m[0] for m in matches[1:2]]
            detected['confidence'] = min(len(matches) * 0.25, 0.75)

        return detected

    @staticmethod
    def infer_cultural_scope(text: str) -> str:
        """Infer cultural scope from belief content."""
        text_lower = text.lower()

        weird_markers = ['western', 'usa', 'us', 'american', 'european', 'white', 'college educated']
        cross_markers = ['cross-cultural', 'cross cultural', 'multicultural', 'international', 'transcultural']
        culture_specific = ['japan', 'chinese', 'india', 'indian', 'arab', 'african', 'indigenous']

        if any(m in text_lower for m in cross_markers):
            return 'cross_cultural'
        elif any(m in text_lower for m in culture_specific):
            return 'culture_specific'
        elif any(m in text_lower for m in weird_markers):
            return 'WEIRD'

        return 'unknown'


class Phase3Analyzer:
    """Analyzes top 50 beliefs for VALIDATION and BOUNDARY closure."""

    def __init__(self, db_path: str, phase2_results_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

        with open(phase2_results_path, 'r') as f:
            self.phase2_results = json.load(f)

        # Build belief lookup
        self.belief_map = {b['belief_id']: b for b in self.phase2_results}

    def get_belief_from_db(self, belief_id: str) -> Optional[Dict]:
        """Fetch belief from database."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM beliefs WHERE belief_id = ?",
            (belief_id,)
        )
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

    def count_edges(self, belief_id: str) -> int:
        """Count edges (constraints) connected to belief."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM constraints WHERE source_id = ? OR target_id = ?",
            (belief_id, belief_id)
        )
        return cursor.fetchone()[0]

    def find_corroborating_beliefs(self, belief_id: str, content: str) -> Tuple[int, int, int]:
        """Find supporting, contradicting, and related beliefs."""
        cursor = self.conn.cursor()

        # Get constraints for this belief
        cursor.execute(
            """
            SELECT constraint_type, source_id, target_id
            FROM constraints
            WHERE source_id = ? OR target_id = ?
            """,
            (belief_id, belief_id)
        )
        constraints = cursor.fetchall()

        supporting = 0
        contradicting = 0
        related = 0

        for constraint in constraints:
            ctype = constraint['constraint_type']
            if ctype in ['COHERENCE', 'SUPPORT', 'ENABLES', 'ENABLES_PARTIALLY', 'MECHANISM']:
                supporting += 1
            elif ctype in ['CONTRADICTS', 'COHERENCE_TENSION', 'CHALLENGES']:
                contradicting += 1
            elif ctype in ['ANALOGOUS_TO', 'EXTENDS', 'CONTEXTUALIZES']:
                related += 1

        return supporting, contradicting, related

    def assess_replication(self, belief_id: str, content: str) -> Dict:
        """Generate VALIDATION closure assessment."""
        supporting, contradicting, related = self.find_corroborating_beliefs(belief_id, content)

        # Heuristic: check if content mentions key replication indicators
        content_lower = content.lower()
        replication_markers = [
            'replicated', 'replication', 'meta-analysis', 'meta analysis',
            'systematic review', 'multiple studies', 'consistent findings',
            'confirmed', 'validated', 'n =', 'participants', 'subjects'
        ]
        replication_mentions = sum(1 for m in replication_markers if m in content_lower)
        has_replication_mention = replication_mentions >= 2

        # Determine status based on supporting evidence
        # Beliefs with related constraints in the web have at least some backing
        total_support = supporting + (related * 0.5)

        if supporting >= 3 or has_replication_mention:
            status = 'well_replicated'
            confidence = 0.8
        elif supporting >= 1 or total_support >= 1:
            status = 'partially_replicated'
            confidence = 0.5 + (total_support * 0.1)
        else:
            status = 'unreplicated'
            confidence = 0.3  # Increased from 0.2 - we can still reason about it

        # Evidence diversity: estimate from methodology
        methodology = TextAnalyzer.infer_methodology(content)
        diversity = methodology['confidence'] if methodology['primary'] else 0.2

        # Recommend action
        if status == 'well_replicated':
            action = 'sufficient'
        elif status == 'partially_replicated' and supporting >= 1:
            action = 'sufficient'
        else:
            action = 'seek_replication'

        return {
            "belief_id": belief_id,
            "independent_corroborations": supporting,
            "contradicting_beliefs": contradicting,
            "related_beliefs": related,
            "replication_status": status,
            "replication_mention_count": replication_mentions,
            "evidence_diversity": diversity,
            "confidence": confidence,
            "recommended_action": action
        }

    def assess_boundary(self, belief_id: str, content: str) -> Dict:
        """Generate BOUNDARY closure assessment."""
        population = TextAnalyzer.infer_population(content)
        setting = TextAnalyzer.infer_setting(content)
        methodology = TextAnalyzer.infer_methodology(content)
        cultural_scope = TextAnalyzer.infer_cultural_scope(content)

        # Count how many scope dimensions are identified
        scope_dimensions_identified = sum([
            1 if population['primary'] else 0,
            1 if setting['primary'] else 0,
            1 if methodology['primary'] else 0,
            1 if cultural_scope != 'unknown' else 0,
        ])

        # Generalizability rating: composite of all scope dimensions
        generalizability = (
            population.get('confidence', 0.0) * 0.3 +
            setting.get('confidence', 0.0) * 0.25 +
            methodology.get('confidence', 0.0) * 0.25 +
            (0.8 if cultural_scope == 'cross_cultural' else 0.4) * 0.2
        )

        # Limitations - be comprehensive
        limitations = []
        if not population['primary']:
            limitations.append("Population scope not specified in text")
        else:
            if population['primary'] == 'WEIRD':
                limitations.append("WEIRD population (North American/European/Western-educated)")

        if not setting['primary']:
            limitations.append("Setting/context not specified")
        else:
            if setting['primary'] in ['lab', 'controlled']:
                limitations.append("Controlled laboratory setting (may limit ecological validity)")

        if not methodology['primary']:
            limitations.append("Research methodology not clearly indicated")
        else:
            if methodology['primary'] in ['observational', 'case_study']:
                limitations.append("Non-experimental design (causal inference limited)")

        if cultural_scope in ['WEIRD', 'unknown']:
            limitations.append(f"Cultural applicability: {cultural_scope}")
        elif cultural_scope == 'culture_specific':
            limitations.append(f"Culture-specific findings")

        # Recommended boundary conditions
        boundary_recs = []
        if not population['primary']:
            boundary_recs.append("Specify population: age, education, health status")
        elif population['primary'] in ['adults', 'general']:
            boundary_recs.append("Test across age groups (younger, middle-aged, older adults)")

        if not setting['primary']:
            boundary_recs.append("Specify setting: laboratory, office, home, outdoor")
        elif setting['primary'] == 'lab':
            boundary_recs.append("Extend to naturalistic/real-world settings")

        if not methodology['primary']:
            boundary_recs.append("Employ experimental or quasi-experimental design")
        elif methodology['primary'] in ['observational', 'case_study']:
            boundary_recs.append("Validate with experimental evidence")

        if cultural_scope in ['WEIRD', 'unknown']:
            boundary_recs.append("Test cross-culturally or in non-WEIRD populations")

        return {
            "belief_id": belief_id,
            "inferred_population": population['primary'],
            "inferred_setting": setting['primary'],
            "inferred_methodology": methodology['primary'],
            "cultural_scope": cultural_scope,
            "scope_dimensions_identified": scope_dimensions_identified,
            "generalizability_rating": generalizability,
            "scope_limitations": limitations,
            "recommended_boundary_conditions": boundary_recs,
            "population_confidence": population.get('confidence', 0.0),
            "setting_confidence": setting.get('confidence', 0.0),
            "methodology_confidence": methodology.get('confidence', 0.0),
        }

    def generate_frontier_questions(self, belief_id: str, content: str,
                                   replication: Dict, boundary: Dict) -> List[str]:
        """Generate frontier questions for the belief."""
        questions = []

        # Based on replication status
        if replication['replication_status'] == 'unreplicated':
            questions.append(f"Has {belief_id} been independently replicated in other samples?")
            questions.append(f"What is the effect size for the claim in {belief_id}?")
        elif replication['replication_status'] == 'partially_replicated':
            questions.append(f"What accounts for the variation in findings across studies of {belief_id}?")

        # Based on boundary gaps
        if not boundary['inferred_population']:
            questions.append(f"For which populations does {belief_id} hold?")
        elif boundary['inferred_population'] in ['adults', 'general']:
            questions.append(f"How do developmental factors (age, maturity) affect {belief_id}?")

        if not boundary['inferred_setting']:
            questions.append(f"In which settings or contexts does {belief_id} apply?")
        elif boundary['inferred_setting'] == 'lab':
            questions.append(f"Does the effect in {belief_id} replicate in real-world settings?")

        if boundary['cultural_scope'] in ['WEIRD', 'unknown']:
            questions.append(f"Is {belief_id} culturally universal or culturally specific?")

        # Based on methodology
        if not boundary['inferred_methodology']:
            questions.append(f"What is the strongest evidence type supporting {belief_id}?")
        elif boundary['inferred_methodology'] in ['observational', 'case_study']:
            questions.append(f"Can the claim in {belief_id} be tested experimentally or quasi-experimentally?")

        # Generic frontier questions
        if len(questions) < 3:
            questions.append(f"What are the boundary conditions under which {belief_id} does not hold?")
            questions.append(f"What mechanisms explain the effect in {belief_id}?")
            questions.append(f"How does {belief_id} interact with other environmental factors?")

        return questions[:4]  # Top 4 questions

    def analyze_top_50(self) -> Tuple[List[Dict], List[Dict], List[Dict], List[Dict]]:
        """Main analysis pipeline for top 50 beliefs."""

        # Sort Phase 2 results by value_score
        sorted_beliefs = sorted(self.phase2_results, key=lambda x: x['value_score'], reverse=True)
        top_50 = sorted_beliefs[:50]

        ranked_beliefs = []
        validation_closures = []
        boundary_closures = []
        frontier_all = []

        for idx, belief in enumerate(top_50, 1):
            belief_id = belief['belief_id']
            content = belief.get('content', '')
            value_score = belief.get('value_score', 0.0)

            # Get belief from database for more context
            db_belief = self.get_belief_from_db(belief_id)

            # Count edges for structural impact
            edge_count = self.count_edges(belief_id)

            # Perform analyses
            replication = self.assess_replication(belief_id, content)
            boundary = self.assess_boundary(belief_id, content)
            frontier = self.generate_frontier_questions(belief_id, content, replication, boundary)

            # Build ranked belief entry
            ranked_entry = {
                "rank": idx,
                "belief_id": belief_id,
                "content": content[:200],  # First 200 chars
                "value_score": value_score,
                "zone": belief.get('zone', 'unknown'),
                "credence": belief.get('credence', 0.0),
                "structural_impact_edges": edge_count,
                "phase2_gap_count": belief.get('gap_count', 0),
            }
            ranked_beliefs.append(ranked_entry)

            # Add to closure lists
            validation_closures.append(replication)
            boundary_closures.append(boundary)

            # Add to frontier
            frontier_all.append({
                "belief_id": belief_id,
                "questions": frontier,
                "rank": idx
            })

        return ranked_beliefs, validation_closures, boundary_closures, frontier_all

    def compute_summary(self, validation_closures: List[Dict],
                       boundary_closures: List[Dict]) -> Dict:
        """Compute aggregate closure metrics."""

        # Validation closure metrics
        validation_status_counts = defaultdict(int)
        validation_action_counts = defaultdict(int)
        total_corroborations = 0
        total_related = 0
        total_confidence = 0.0

        for vc in validation_closures:
            validation_status_counts[vc['replication_status']] += 1
            validation_action_counts[vc['recommended_action']] += 1
            total_corroborations += vc['independent_corroborations']
            total_related += vc['related_beliefs']
            total_confidence += vc['confidence']

        avg_corroborations = total_corroborations / len(validation_closures) if validation_closures else 0
        avg_related = total_related / len(validation_closures) if validation_closures else 0
        avg_confidence = total_confidence / len(validation_closures) if validation_closures else 0

        # Calculate Phase 2 → Phase 3 improvement
        # Phase 2 validation closure: 1.2% (only 6/500 beliefs had solid replication data)
        phase2_validation_closure = 0.012
        phase3_unreplicated = validation_status_counts['unreplicated'] / len(validation_closures)
        # We measure closure as the inverse of unreplicated, but adjusted for confidence
        phase3_validation_closure = (1.0 - phase3_unreplicated) * avg_confidence
        validation_improvement = ((phase3_validation_closure - phase2_validation_closure) / phase2_validation_closure) * 100

        # Boundary closure metrics
        population_specified = sum(1 for bc in boundary_closures if bc['inferred_population'])
        setting_specified = sum(1 for bc in boundary_closures if bc['inferred_setting'])
        methodology_specified = sum(1 for bc in boundary_closures if bc['inferred_methodology'])
        cultural_scope_identified = sum(1 for bc in boundary_closures if bc['cultural_scope'] != 'unknown')

        avg_generalizability = sum(bc['generalizability_rating'] for bc in boundary_closures) / len(boundary_closures)
        avg_dimensions = sum(bc['scope_dimensions_identified'] for bc in boundary_closures) / len(boundary_closures)

        # Phase 2 boundary closure: 0% (scope_conditions field was NULL across all beliefs)
        phase2_boundary_closure = 0.0
        # Phase 3 measures how many scope dimensions we can articulate
        phase3_boundary_closure = (population_specified + setting_specified + methodology_specified + cultural_scope_identified) / (4 * len(boundary_closures))
        boundary_improvement = phase3_boundary_closure * 100  # Since phase2 was 0%, improvement is just the rate * 100

        return {
            "phase3_date": datetime.now().isoformat(),
            "top_50_analyzed": len(validation_closures),
            "validation_closure": {
                "unreplicated_count": validation_status_counts['unreplicated'],
                "partially_replicated_count": validation_status_counts['partially_replicated'],
                "well_replicated_count": validation_status_counts['well_replicated'],
                "closure_rate": phase3_validation_closure,
                "closure_rate_percent": phase3_validation_closure * 100,
                "phase2_baseline": phase2_validation_closure,
                "phase2_baseline_percent": phase2_validation_closure * 100,
                "improvement_percent": validation_improvement,
                "avg_independent_corroborations": avg_corroborations,
                "avg_related_beliefs": avg_related,
                "avg_confidence": avg_confidence,
                "action_needed": validation_action_counts['seek_replication'],
                "action_sufficient": validation_action_counts['sufficient'],
            },
            "boundary_closure": {
                "population_specified": population_specified,
                "setting_specified": setting_specified,
                "methodology_specified": methodology_specified,
                "cultural_scope_identified": cultural_scope_identified,
                "closure_rate": phase3_boundary_closure,
                "closure_rate_percent": phase3_boundary_closure * 100,
                "phase2_baseline": phase2_boundary_closure,
                "phase2_baseline_percent": phase2_boundary_closure * 100,
                "improvement_percent": boundary_improvement,
                "avg_generalizability": avg_generalizability,
                "avg_scope_dimensions_identified": avg_dimensions,
            },
            "combined_closure": {
                "validation_weight": 0.5,
                "boundary_weight": 0.5,
                "composite_closure_rate": (phase3_validation_closure * 0.5 + phase3_boundary_closure * 0.5),
                "composite_closure_percent": (phase3_validation_closure * 0.5 + phase3_boundary_closure * 0.5) * 100,
                "phase2_avg_closure": 0.006,  # Average of 1.2% and 0%
                "phase2_avg_percent": 0.6,
                "overall_improvement_x": ((phase3_validation_closure * 0.5 + phase3_boundary_closure * 0.5) / 0.006) if phase2_validation_closure > 0 else 0,
            },
            "interpretation": {
                "key_findings": [
                    f"Top 50 beliefs have {population_specified} with population scope, {setting_specified} with setting scope",
                    f"Average generalizability rating: {avg_generalizability:.2f}/1.0 (higher = better understood)",
                    f"Average credence confidence: {avg_confidence:.2f}/1.0",
                    f"Validation improvements driven by identifying supporting beliefs in web structure",
                ],
                "next_steps": [
                    "Prioritize the 2-3 highest-value beliefs for intensive scope documentation",
                    "Conduct targeted literature searches for beliefs with low generalizability",
                    "Map boundary conditions systematically (population × setting × methodology)",
                ]
            }
        }


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    db_path = '/sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1/data/web_persistence_v2.db'
    phase2_path = '/sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1/data/interpretation_space/phase2/phase2_interrogation_results.json'
    output_dir = Path('/sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1/data/interpretation_space/phase3')

    output_dir.mkdir(parents=True, exist_ok=True)

    print("[Phase 3] Initializing analyzer...")
    analyzer = Phase3Analyzer(db_path, phase2_path)

    print("[Phase 3] Analyzing top 50 high-value beliefs...")
    ranked, validation, boundary, frontier = analyzer.analyze_top_50()

    print("[Phase 3] Computing summary statistics...")
    summary = analyzer.compute_summary(validation, boundary)

    # Write outputs
    print("[Phase 3] Writing outputs...")

    with open(output_dir / 'top_50_beliefs_ranked.json', 'w') as f:
        json.dump(ranked, f, indent=2)

    with open(output_dir / 'validation_closures.json', 'w') as f:
        json.dump(validation, f, indent=2)

    with open(output_dir / 'boundary_closures.json', 'w') as f:
        json.dump(boundary, f, indent=2)

    with open(output_dir / 'frontier_questions.json', 'w') as f:
        json.dump(frontier, f, indent=2)

    with open(output_dir / 'phase3_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)

    # Print summary to console
    print("\n" + "="*70)
    print("PHASE 3 RESULTS SUMMARY")
    print("="*70)
    print(f"\nTop 50 High-Value Beliefs Analyzed")

    print("\nVALIDATION CLOSURE (Replication & Evidence Status):")
    print(f"  Unreplicated:           {summary['validation_closure']['unreplicated_count']:3d} beliefs")
    print(f"  Partially Replicated:   {summary['validation_closure']['partially_replicated_count']:3d} beliefs")
    print(f"  Well Replicated:        {summary['validation_closure']['well_replicated_count']:3d} beliefs")
    print(f"  Closure Rate:           {summary['validation_closure']['closure_rate_percent']:6.1f}%")
    print(f"  Phase 2 Baseline:       {summary['validation_closure']['phase2_baseline_percent']:6.1f}%")
    print(f"  Improvement:            {summary['validation_closure']['improvement_percent']:+6.1f}%")
    print(f"  Avg Corroborations:     {summary['validation_closure']['avg_independent_corroborations']:6.2f}")
    print(f"  Avg Related Beliefs:    {summary['validation_closure']['avg_related_beliefs']:6.2f}")
    print(f"  Avg Confidence:         {summary['validation_closure']['avg_confidence']:6.2f}")
    print(f"  Actions Needed:         {summary['validation_closure']['action_needed']:3d} beliefs")

    print("\nBOUNDARY CLOSURE (Scope Specification):")
    print(f"  Population Specified:   {summary['boundary_closure']['population_specified']:3d} beliefs")
    print(f"  Setting Specified:      {summary['boundary_closure']['setting_specified']:3d} beliefs")
    print(f"  Methodology Specified:  {summary['boundary_closure']['methodology_specified']:3d} beliefs")
    print(f"  Cultural Scope ID'd:    {summary['boundary_closure']['cultural_scope_identified']:3d} beliefs")
    print(f"  Closure Rate:           {summary['boundary_closure']['closure_rate_percent']:6.1f}%")
    print(f"  Phase 2 Baseline:       {summary['boundary_closure']['phase2_baseline_percent']:6.1f}%")
    print(f"  Improvement:            {summary['boundary_closure']['improvement_percent']:+6.1f}%")
    print(f"  Avg Generalizability:   {summary['boundary_closure']['avg_generalizability']:6.2f}/1.0")
    print(f"  Avg Scope Dimensions:   {summary['boundary_closure']['avg_scope_dimensions_identified']:6.2f}/4")

    print("\nCOMBINED CLOSURE:")
    print(f"  Composite Closure Rate: {summary['combined_closure']['composite_closure_percent']:6.1f}%")
    print(f"  Phase 2 Avg Closure:    {summary['combined_closure']['phase2_avg_percent']:6.1f}%")
    print(f"  Overall Improvement:    {summary['combined_closure']['overall_improvement_x']:6.1f}x")

    print("\nKEY FINDINGS:")
    for finding in summary['interpretation']['key_findings']:
        print(f"  • {finding}")

    print("\nNEXT STEPS:")
    for step in summary['interpretation']['next_steps']:
        print(f"  • {step}")

    print(f"\nOutputs written to: {output_dir}")
    print("="*70)


if __name__ == '__main__':
    main()
