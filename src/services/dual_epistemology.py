"""
Article Eater - Dual Epistemology Analysis
==========================================

Analyzes the same corpus through two epistemological frameworks:

1. FOUNDATIONALIST (Claude Code's approach)
   - Evidence flows upward to theories
   - Theories have confidence scores that update via propagation rules
   - More traditional Bayesian updating

2. COHERENTIST (Quinean approach)
   - Bidirectional constraint between all levels
   - Joint probability over theory-worlds
   - Reflective equilibrium
   - Semantic status matters (criterial vs synthetic)

The goal: Show how different philosophical assumptions lead to different
conclusions about the same evidence, and suggest different experiments.

This is pedagogically valuable for cognitive science students learning
that epistemological choices aren't neutral.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
from datetime import datetime
import json
import math
from collections import defaultdict

# Import both approaches
from src.services.refined_epistemic import (
    RefinedEpistemicState,
    SemanticStatus,
    DependencyType,
    create_refined_neuroarchitecture
)
from src.services.evidence_integration import EvidenceIntegrator
from src.services.pdf_extraction import PDFExtractor, ExtractedPaper


# =============================================================================
# FOUNDATIONALIST MODEL (Based on Claude Code's propagation.py)
# =============================================================================

@dataclass
class PropagationRules:
    """Rules for confidence propagation in foundationalist model."""
    evidence_to_prediction_weight: float = 0.7
    prediction_to_theory_weight: float = 0.5
    theory_to_prediction_weight: float = 0.3
    max_delta_per_update: float = 0.15
    min_confidence: float = 0.05
    max_confidence: float = 0.95
    
    def apply_bounds(self, delta: float) -> float:
        """Apply bounds to confidence delta."""
        return max(-self.max_delta_per_update, 
                   min(self.max_delta_per_update, delta))


@dataclass
class FoundationalistTheory:
    """A theory in the foundationalist model."""
    theory_id: str
    name: str
    confidence: float = 0.5
    evidence_count: int = 0
    supporting_evidence: int = 0
    contradicting_evidence: int = 0
    
    def update_with_evidence(self, supports: bool, strength: float, rules: PropagationRules):
        """Update confidence based on evidence."""
        self.evidence_count += 1
        
        if supports:
            self.supporting_evidence += 1
            delta = strength * rules.evidence_to_prediction_weight * rules.prediction_to_theory_weight
        else:
            self.contradicting_evidence += 1
            delta = -strength * rules.evidence_to_prediction_weight * rules.prediction_to_theory_weight
        
        bounded_delta = rules.apply_bounds(delta)
        self.confidence = max(rules.min_confidence, 
                             min(rules.max_confidence, 
                                 self.confidence + bounded_delta))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'theory_id': self.theory_id,
            'name': self.name,
            'confidence': self.confidence,
            'evidence_count': self.evidence_count,
            'support_ratio': self.supporting_evidence / max(1, self.evidence_count)
        }


class FoundationalistState:
    """Epistemic state in the foundationalist model."""
    
    def __init__(self):
        self.theories: Dict[str, FoundationalistTheory] = {}
        self.rules = PropagationRules()
        self.evidence_log: List[Dict[str, Any]] = []
        
        # Initialize theories
        self._init_theories()
    
    def _init_theories(self):
        """Initialize with same theories as coherentist model."""
        initial_theories = [
            ('ART', 'Attention Restoration Theory', 0.5),
            ('SRT', 'Stress Recovery Theory', 0.5),
            ('Biophilia', 'Biophilia Hypothesis', 0.5),
            ('Perceptual_Fluency', 'Perceptual Fluency', 0.5),
            ('Predictive_Processing', 'Predictive Processing', 0.5),
            ('Embodied_Cognition', 'Embodied Cognition', 0.5),
        ]
        
        for tid, name, conf in initial_theories:
            self.theories[tid] = FoundationalistTheory(tid, name, conf)
    
    def add_evidence(self, paper: ExtractedPaper) -> Dict[str, Any]:
        """Add evidence from a paper."""
        updates = []
        
        for theory_ref in paper.theories_referenced:
            theory_id = theory_ref.theory_name
            if theory_id in self.theories:
                theory = self.theories[theory_id]
                old_conf = theory.confidence
                
                # Determine if supporting (most published papers support what they test)
                supports = theory_ref.relation in ['supports', 'tests', 'cites']
                theory.update_with_evidence(supports, theory_ref.strength, self.rules)
                
                updates.append({
                    'theory': theory_id,
                    'old_confidence': old_conf,
                    'new_confidence': theory.confidence,
                    'relation': theory_ref.relation
                })
        
        self.evidence_log.append({
            'paper': paper.title[:50],
            'updates': updates
        })
        
        return {'updates': updates}
    
    def get_theory_credences(self) -> Dict[str, float]:
        """Get current theory credences."""
        return {tid: t.confidence for tid, t in self.theories.items()}
    
    def get_research_priorities(self) -> List[Tuple[str, float, str]]:
        """
        Get research priorities.
        
        In foundationalist model: prioritize theories with low evidence count
        or where support ratio is uncertain (near 0.5).
        """
        priorities = []
        
        for tid, theory in self.theories.items():
            # Priority based on: (1) low evidence count, (2) uncertain support ratio
            evidence_factor = 1.0 / (1 + theory.evidence_count * 0.2)
            
            support_ratio = theory.supporting_evidence / max(1, theory.evidence_count)
            uncertainty_factor = 1 - abs(support_ratio - 0.5) * 2  # Peaks at 0.5
            
            priority = evidence_factor * 0.6 + uncertainty_factor * 0.4
            
            reason = f"Evidence count: {theory.evidence_count}, Support ratio: {support_ratio:.2f}"
            priorities.append((tid, priority, reason))
        
        return sorted(priorities, key=lambda x: -x[1])


# =============================================================================
# COMPARATIVE ANALYSIS
# =============================================================================

@dataclass
class EpistemologicalComparison:
    """Results of comparing two epistemological frameworks."""
    
    # Theory credences
    foundationalist_credences: Dict[str, float] = field(default_factory=dict)
    coherentist_credences: Dict[str, float] = field(default_factory=dict)
    
    # Research priorities
    foundationalist_priorities: List[Tuple[str, float, str]] = field(default_factory=list)
    coherentist_priorities: List[Tuple[str, float, str]] = field(default_factory=list)
    
    # Key differences
    credence_divergences: List[Dict[str, Any]] = field(default_factory=list)
    priority_divergences: List[Dict[str, Any]] = field(default_factory=list)
    
    # Philosophical implications
    implications: List[str] = field(default_factory=list)


class DualEpistemologyAnalyzer:
    """
    Analyzes the same corpus through both epistemological lenses.
    """
    
    def __init__(self):
        self.foundationalist = FoundationalistState()
        self.coherentist = EvidenceIntegrator()
        self.papers_processed: List[str] = []
    
    def process_corpus(self, papers: List[ExtractedPaper]) -> EpistemologicalComparison:
        """Process papers through both frameworks."""
        
        for paper in papers:
            # Foundationalist update
            self.foundationalist.add_evidence(paper)
            
            # Coherentist update
            self.coherentist.integrate_paper(paper)
            
            self.papers_processed.append(paper.title[:50])
        
        return self.compare()
    
    def compare(self) -> EpistemologicalComparison:
        """Compare the two frameworks' conclusions."""
        
        comparison = EpistemologicalComparison()
        
        # Get credences
        comparison.foundationalist_credences = self.foundationalist.get_theory_credences()
        comparison.coherentist_credences = {
            tid: self.coherentist.state.beliefs[bid].credence
            for tid, bid in self.coherentist.THEORY_TO_BELIEF.items()
            if bid in self.coherentist.state.beliefs
        }
        
        # Get priorities
        comparison.foundationalist_priorities = self.foundationalist.get_research_priorities()
        comparison.coherentist_priorities = self._get_coherentist_priorities()
        
        # Find divergences
        comparison.credence_divergences = self._find_credence_divergences(comparison)
        comparison.priority_divergences = self._find_priority_divergences(comparison)
        
        # Generate implications
        comparison.implications = self._generate_implications(comparison)
        
        return comparison
    
    def _get_coherentist_priorities(self) -> List[Tuple[str, float, str]]:
        """Get research priorities from coherentist model (VOI-based)."""
        priorities = []
        
        for tid, bid in self.coherentist.THEORY_TO_BELIEF.items():
            if bid not in self.coherentist.state.beliefs:
                continue
            
            belief = self.coherentist.state.beliefs[bid]
            cred = belief.credence
            
            # VOI peaks at 0.5
            voi = cred * (1 - cred) * 4
            
            # Adjust for entrenchment (less entrenched = more revisable = higher VOI)
            voi *= (1 - belief.entrenchment * 0.5)
            
            reason = f"Credence: {cred:.2f}, Entrenchment: {belief.entrenchment:.2f}"
            priorities.append((tid, voi, reason))
        
        return sorted(priorities, key=lambda x: -x[1])
    
    def _find_credence_divergences(self, comparison: EpistemologicalComparison) -> List[Dict[str, Any]]:
        """Find theories where the two frameworks diverge."""
        divergences = []
        
        for tid in comparison.foundationalist_credences:
            if tid not in comparison.coherentist_credences:
                continue
            
            f_cred = comparison.foundationalist_credences[tid]
            c_cred = comparison.coherentist_credences[tid]
            diff = abs(f_cred - c_cred)
            
            if diff > 0.1:  # Meaningful divergence
                divergences.append({
                    'theory': tid,
                    'foundationalist': f_cred,
                    'coherentist': c_cred,
                    'difference': diff,
                    'direction': 'foundationalist higher' if f_cred > c_cred else 'coherentist higher'
                })
        
        return sorted(divergences, key=lambda x: -x['difference'])
    
    def _find_priority_divergences(self, comparison: EpistemologicalComparison) -> List[Dict[str, Any]]:
        """Find theories where research priority rankings differ."""
        f_ranking = {t: i for i, (t, _, _) in enumerate(comparison.foundationalist_priorities)}
        c_ranking = {t: i for i, (t, _, _) in enumerate(comparison.coherentist_priorities)}
        
        divergences = []
        for tid in f_ranking:
            if tid not in c_ranking:
                continue
            
            f_rank = f_ranking[tid]
            c_rank = c_ranking[tid]
            
            if abs(f_rank - c_rank) >= 2:  # Rank differs by 2+
                divergences.append({
                    'theory': tid,
                    'foundationalist_rank': f_rank + 1,
                    'coherentist_rank': c_rank + 1,
                    'rank_difference': abs(f_rank - c_rank)
                })
        
        return sorted(divergences, key=lambda x: -x['rank_difference'])
    
    def _generate_implications(self, comparison: EpistemologicalComparison) -> List[str]:
        """Generate philosophical implications of the differences."""
        implications = []
        
        # Check for systematic patterns
        f_mean = sum(comparison.foundationalist_credences.values()) / len(comparison.foundationalist_credences)
        c_mean = sum(comparison.coherentist_credences.values()) / len(comparison.coherentist_credences)
        
        if f_mean < c_mean - 0.05:
            implications.append(
                "The foundationalist model yields lower average credences. This is because "
                "it treats each piece of evidence independently, without the 'coherence bonus' "
                "that comes from theories supporting each other."
            )
        elif f_mean > c_mean + 0.05:
            implications.append(
                "The foundationalist model yields higher average credences. This may occur "
                "when the coherentist model detects tensions between theories that the "
                "foundationalist model doesn't track."
            )
        
        # Priority divergences
        if comparison.priority_divergences:
            top_divergence = comparison.priority_divergences[0]
            implications.append(
                f"The frameworks disagree most about {top_divergence['theory']}: "
                f"foundationalist ranks it #{top_divergence['foundationalist_rank']} "
                f"while coherentist ranks it #{top_divergence['coherentist_rank']}. "
                f"This suggests the frameworks would recommend different experiments."
            )
        
        # Credence divergences
        if comparison.credence_divergences:
            top = comparison.credence_divergences[0]
            if top['direction'] == 'coherentist higher':
                implications.append(
                    f"{top['theory']} shows higher credence in the coherentist model "
                    f"({top['coherentist']:.2f} vs {top['foundationalist']:.2f}). "
                    f"This may reflect coherence with other well-supported theories that "
                    f"the foundationalist model doesn't capture."
                )
            else:
                implications.append(
                    f"{top['theory']} shows lower credence in the coherentist model "
                    f"({top['coherentist']:.2f} vs {top['foundationalist']:.2f}). "
                    f"This may indicate tension with other beliefs in the web."
                )
        
        return implications
    
    def generate_report(self, comparison: EpistemologicalComparison) -> str:
        """Generate human-readable comparison report."""
        lines = [
            "# Dual Epistemology Analysis",
            f"## Comparing Foundationalist vs Coherentist Frameworks",
            f"### Corpus: {len(self.papers_processed)} papers",
            "",
            "---",
            "",
            "## 1. Theory Credences",
            "",
            "| Theory | Foundationalist | Coherentist | Difference |",
            "|--------|-----------------|-------------|------------|"
        ]
        
        for tid in comparison.foundationalist_credences:
            f_cred = comparison.foundationalist_credences.get(tid, 0)
            c_cred = comparison.coherentist_credences.get(tid, 0)
            diff = c_cred - f_cred
            arrow = "↑" if diff > 0.05 else "↓" if diff < -0.05 else "≈"
            lines.append(f"| {tid:20} | {f_cred:.2f} | {c_cred:.2f} | {arrow} {abs(diff):.2f} |")
        
        lines.extend([
            "",
            "## 2. Research Priority Rankings",
            "",
            "| Rank | Foundationalist | Coherentist |",
            "|------|-----------------|-------------|"
        ])
        
        for i in range(len(comparison.foundationalist_priorities)):
            f_theory = comparison.foundationalist_priorities[i][0] if i < len(comparison.foundationalist_priorities) else "-"
            c_theory = comparison.coherentist_priorities[i][0] if i < len(comparison.coherentist_priorities) else "-"
            lines.append(f"| {i+1} | {f_theory} | {c_theory} |")
        
        lines.extend([
            "",
            "## 3. Key Divergences",
            ""
        ])
        
        if comparison.credence_divergences:
            lines.append("### Credence Divergences")
            for d in comparison.credence_divergences[:3]:
                lines.append(f"- **{d['theory']}**: {d['direction']} by {d['difference']:.2f}")
        
        if comparison.priority_divergences:
            lines.append("")
            lines.append("### Priority Divergences")
            for d in comparison.priority_divergences[:3]:
                lines.append(f"- **{d['theory']}**: ranked #{d['foundationalist_rank']} (found.) vs #{d['coherentist_rank']} (coher.)")
        
        lines.extend([
            "",
            "## 4. Philosophical Implications",
            ""
        ])
        
        for impl in comparison.implications:
            lines.append(f"- {impl}")
        
        lines.extend([
            "",
            "---",
            "",
            "## 5. What This Means for Research",
            "",
            "The two frameworks would recommend different next studies:",
            ""
        ])
        
        # Top foundationalist priority
        f_top = comparison.foundationalist_priorities[0]
        lines.append(f"**Foundationalist recommendation:** Study {f_top[0]}")
        lines.append(f"  - Reason: {f_top[2]}")
        lines.append(f"  - Logic: Prioritize theories with least evidence (simple counting)")
        lines.append("")
        
        # Top coherentist priority  
        c_top = comparison.coherentist_priorities[0]
        lines.append(f"**Coherentist recommendation:** Study {c_top[0]}")
        lines.append(f"  - Reason: {c_top[2]}")
        lines.append(f"  - Logic: Prioritize where belief revision would most affect the web")
        
        lines.extend([
            "",
            "---",
            "",
            "## 6. Teaching Point",
            "",
            "This comparison demonstrates that **epistemological assumptions are not neutral**.",
            "The choice between foundationalism and coherentism affects:",
            "",
            "1. How we aggregate evidence",
            "2. Which theories we consider well-supported",
            "3. What research we prioritize",
            "4. How we handle findings that don't fit existing theories",
            "",
            "Neither framework is 'correct' — they embody different philosophical commitments",
            "about how knowledge is structured and justified.",
        ])
        
        return "\n".join(lines)


# =============================================================================
# DEMO
# =============================================================================

def run_dual_analysis():
    """Run the dual epistemology analysis on the corpus."""
    
    print("="*70)
    print("DUAL EPISTEMOLOGY ANALYSIS")
    print("Comparing Foundationalist vs Coherentist Frameworks")
    print("="*70)
    
    # Load papers
    with open('/home/claude/article_eater/data/extraction_results.json') as f:
        data = json.load(f)
    
    # Reconstruct papers
    from src.services.pdf_extraction import TheoryReference
    papers = []
    for p_data in data['papers']:
        paper = ExtractedPaper(filepath=p_data['filepath'])
        paper.title = p_data['title']
        paper.year = p_data.get('year')
        paper.paper_type = p_data['paper_type']
        paper.theories_referenced = [
            TheoryReference(
                theory_name=t['name'],
                relation=t['relation'],
                strength=t['strength']
            )
            for t in p_data.get('theories_referenced', [])
        ]
        papers.append(paper)
    
    print(f"\nLoaded {len(papers)} papers\n")
    
    # Run dual analysis
    analyzer = DualEpistemologyAnalyzer()
    comparison = analyzer.process_corpus(papers)
    
    # Generate and print report
    report = analyzer.generate_report(comparison)
    print(report)
    
    # Save report
    with open('/home/claude/article_eater/reports/dual_epistemology_report.md', 'w') as f:
        f.write(report)
    
    return analyzer, comparison


if __name__ == "__main__":
    analyzer, comparison = run_dual_analysis()
