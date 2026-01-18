"""
Article Eater - Evidence Integration
====================================

Integrates extracted PDF data into the refined epistemic state.
Demonstrates the full pipeline: PDF -> Extraction -> Epistemic Update
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from src.services.pdf_extraction import PDFExtractor, ExtractedPaper, TheoryReference
from src.services.refined_epistemic import (
    RefinedEpistemicState,
    SemanticBelief,
    SemanticStatus,
    RefinedDependency,
    DependencyType,
    create_refined_neuroarchitecture
)
from src.services.web_of_belief import (
    WebOfBelief,
    Belief,
    EpistemicLevel,
    BeliefStatus,
    Credence,
    UncertainQuantity,
    create_neuroarchitecture_web
)


@dataclass
class IntegrationResult:
    """Result of integrating a paper into epistemic state."""
    paper_title: str
    beliefs_added: int
    beliefs_updated: int
    theories_affected: List[str]
    new_stubs: List[str]
    coherence_before: float
    coherence_after: float
    

class EvidenceIntegrator:
    """Integrates extracted papers into epistemic state."""
    
    # Map extracted theory names to epistemic state belief IDs
    THEORY_TO_BELIEF = {
        'ART': 'ART_core',
        'SRT': 'SRT_core',
        'Biophilia': 'biophilia_hypothesis',
        'Perceptual_Fluency': 'perceptual_fluency',
        'Predictive_Processing': 'predictive_processing',
        'Embodied_Cognition': 'embodied_cognition'
    }
    
    def __init__(self, state: RefinedEpistemicState = None):
        self.state = state or self._create_extended_state()
        self.integration_history: List[IntegrationResult] = []
    
    def _create_extended_state(self) -> RefinedEpistemicState:
        """Create epistemic state with all theories from corpus."""
        state = create_refined_neuroarchitecture()
        
        # Add additional theories found in corpus
        
        # Biophilia hypothesis
        state.add_synthetic_belief(
            "biophilia_hypothesis",
            "Humans have an innate tendency to affiliate with nature and other living things",
            credence=0.65
        )
        
        # Perceptual fluency
        state.add_synthetic_belief(
            "perceptual_fluency",
            "Ease of perceptual processing generates positive affect and preference",
            credence=0.72
        )
        
        # Predictive processing
        state.add_framework_belief(
            "predictive_processing",
            "The brain minimizes prediction error through hierarchical inference",
            initial_credence=0.78
        )
        
        # Embodied cognition
        state.add_framework_belief(
            "embodied_cognition",
            "Cognition is shaped by bodily interactions with the environment",
            initial_credence=0.70
        )
        
        # Curvature preference
        state.add_synthetic_belief(
            "curvature_preference",
            "Humans prefer curved over angular forms in architecture",
            credence=0.68
        )
        
        # Add some evidential dependencies
        state.add_evidential_dependency("curvature_preference", "perceptual_fluency", 0.6)
        state.add_evidential_dependency("biophilia_hypothesis", "ART_core", 0.5)
        state.add_evidential_dependency("biophilia_hypothesis", "SRT_core", 0.5)
        
        return state
    
    def integrate_paper(self, paper: ExtractedPaper) -> IntegrationResult:
        """Integrate a single paper into the epistemic state."""
        coherence_before = self.state.global_coherence()
        beliefs_added = 0
        beliefs_updated = 0
        theories_affected = []
        new_stubs = []
        
        # Create belief for the paper's main finding
        paper_id = f"paper_{hash(paper.title) % 10000}"
        
        if paper.abstract:
            finding_content = paper.abstract[:200]
        else:
            finding_content = f"Finding from {paper.title[:50]}"
        
        # Determine if this finding supports or contradicts theories
        supports = {}
        contradicts = {}
        
        for theory_ref in paper.theories_referenced:
            theory_belief = self.THEORY_TO_BELIEF.get(theory_ref.theory_name)
            if theory_belief and theory_belief in self.state.beliefs:
                theories_affected.append(theory_ref.theory_name)
                
                if theory_ref.relation in ['supports', 'tests']:
                    # Testing generally provides positive evidence (if published)
                    supports[theory_belief] = theory_ref.strength * 0.7
                elif theory_ref.relation == 'contradicts':
                    contradicts[theory_belief] = theory_ref.strength * 0.7
        
        # Add evidence to state
        if supports or contradicts:
            updates = self.state.add_evidence(
                paper_id,
                finding_content,
                supports=supports,
                contradicts=contradicts
            )
            beliefs_added = 1
            beliefs_updated = len(updates.get('belief_updates', []))
        else:
            # This is a stub - finding without clear theory connection
            self.state.add_synthetic_belief(
                paper_id,
                finding_content,
                credence=0.6,
                peripheral=True
            )
            new_stubs.append(paper_id)
            beliefs_added = 1
        
        # Add effect size information if available
        for i, es in enumerate(paper.effect_sizes[:3]):  # Limit to first 3
            if es.effect_type == 'd' and abs(es.value) > 0.2:
                # Meaningful effect size
                es_id = f"{paper_id}_es_{i}"
                es_content = f"Effect size d={es.value:.2f} for {es.outcome[:30]}"
                
                self.state.add_synthetic_belief(
                    es_id,
                    es_content,
                    credence=0.65,
                    peripheral=True
                )
                beliefs_added += 1
        
        coherence_after = self.state.global_coherence()
        
        result = IntegrationResult(
            paper_title=paper.title[:50],
            beliefs_added=beliefs_added,
            beliefs_updated=beliefs_updated,
            theories_affected=theories_affected,
            new_stubs=new_stubs,
            coherence_before=coherence_before,
            coherence_after=coherence_after
        )
        
        self.integration_history.append(result)
        return result
    
    def integrate_corpus(self, papers: List[ExtractedPaper]) -> Dict[str, Any]:
        """Integrate all papers and return summary."""
        initial_coherence = self.state.global_coherence()
        initial_beliefs = len(self.state.beliefs)
        
        for paper in papers:
            self.integrate_paper(paper)
        
        final_coherence = self.state.global_coherence()
        final_beliefs = len(self.state.beliefs)
        
        # Theory credences after integration
        theory_credences = {}
        for theory_name, belief_id in self.THEORY_TO_BELIEF.items():
            if belief_id in self.state.beliefs:
                theory_credences[theory_name] = self.state.beliefs[belief_id].credence
        
        # Count stubs
        stubs = sum(len(r.new_stubs) for r in self.integration_history)
        
        return {
            'papers_integrated': len(papers),
            'beliefs_initial': initial_beliefs,
            'beliefs_final': final_beliefs,
            'coherence_initial': initial_coherence,
            'coherence_final': final_coherence,
            'theory_credences': theory_credences,
            'total_stubs': stubs,
            'integration_history': [
                {
                    'title': r.paper_title,
                    'beliefs_added': r.beliefs_added,
                    'theories': r.theories_affected
                }
                for r in self.integration_history
            ]
        }
    
    def report(self) -> str:
        """Generate human-readable report of epistemic state."""
        lines = [
            "# Epistemic State Report",
            f"## After integrating {len(self.integration_history)} papers",
            "",
            "### Theory Credences",
            ""
        ]
        
        # Sort by credence
        theory_beliefs = []
        for theory_name, belief_id in self.THEORY_TO_BELIEF.items():
            if belief_id in self.state.beliefs:
                b = self.state.beliefs[belief_id]
                theory_beliefs.append((theory_name, b.credence, b.semantic_status.value))
        
        for name, cred, status in sorted(theory_beliefs, key=lambda x: -x[1]):
            bar = "█" * int(cred * 20)
            lines.append(f"  {name:25} [{cred:.2f}] {bar}")
        
        lines.append("")
        lines.append("### Global Coherence")
        coh = self.state.global_coherence()
        lines.append(f"  {coh:.3f}")
        
        lines.append("")
        lines.append("### Belief Counts by Status")
        
        by_status = {}
        for b in self.state.beliefs.values():
            s = b.semantic_status.value
            by_status[s] = by_status.get(s, 0) + 1
        
        for status, count in sorted(by_status.items(), key=lambda x: -x[1]):
            lines.append(f"  {status:20}: {count}")
        
        # Tensions
        tensions = self.state.find_tensions()
        if tensions:
            lines.append("")
            lines.append("### Detected Tensions")
            for t in tensions[:5]:
                lines.append(f"  {t['beliefs'][0]} vs {t['beliefs'][1]}: {t['coherence']:.3f}")
        
        return "\n".join(lines)


def run_integration_demo():
    """Run complete integration demo with extracted PDFs."""
    print("="*70)
    print("ARTICLE EATER - EVIDENCE INTEGRATION DEMO")
    print("="*70)
    
    # Load extraction results
    with open('/home/claude/article_eater/data/extraction_results.json') as f:
        data = json.load(f)
    
    # Reconstruct papers (simplified)
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
    
    print(f"\nLoaded {len(papers)} papers from extraction results\n")
    
    # Create integrator and process
    integrator = EvidenceIntegrator()
    
    print("Initial state:")
    print(f"  Beliefs: {len(integrator.state.beliefs)}")
    print(f"  Coherence: {integrator.state.global_coherence():.3f}")
    
    print("\nIntegrating papers...")
    summary = integrator.integrate_corpus(papers)
    
    print("\n" + "="*70)
    print("INTEGRATION SUMMARY")
    print("="*70)
    print(f"Papers integrated: {summary['papers_integrated']}")
    print(f"Beliefs: {summary['beliefs_initial']} -> {summary['beliefs_final']}")
    print(f"Coherence: {summary['coherence_initial']:.3f} -> {summary['coherence_final']:.3f}")
    print(f"Stubs (unattached findings): {summary['total_stubs']}")
    
    print("\n" + "="*70)
    print("THEORY CREDENCES AFTER INTEGRATION")
    print("="*70)
    for theory, cred in sorted(summary['theory_credences'].items(), key=lambda x: -x[1]):
        bar = "█" * int(cred * 30)
        print(f"{theory:25} [{cred:.2f}] {bar}")
    
    print("\n" + "="*70)
    print("FULL REPORT")
    print("="*70)
    print(integrator.report())
    
    return integrator


if __name__ == "__main__":
    integrator = run_integration_demo()
