"""
Figure Suggestion Service — identifies relevant figures for topics/answers.

The ATLAS system has 42 publication-quality figures in docs/figures/. This service
maps topics/beliefs to relevant figures so answers can include visual aids.

Figures are indexed by: id, path, title, related_concepts (keywords), phase, priority.

Created: 2026-03-02
Author: Claude Code
"""

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum

logger = logging.getLogger(__name__)


class FigurePhase(Enum):
    """Phases of ATLAS documentation that figures support."""
    GOLDILOCKS = "goldilocks"
    ARCHITECTURE = "architecture"
    CREDENCE = "credence"
    DOMAIN_PANEL = "domain_panel"
    OPERATIONS = "operations"
    DASHBOARD = "dashboard"
    MATH_EXPLANATION = "math_explanation"


class FigurePriority(Enum):
    """Priority levels for figure inclusion."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class FigureMetadata:
    """Metadata for a single figure."""
    id: str
    title: str
    file_path: str
    related_concepts: List[str]
    phase: FigurePhase
    priority: FigurePriority
    description: str
    master_doc_section: Optional[str] = None
    generator_script: Optional[str] = None
    data_dependencies: List[str] = None

    def __post_init__(self):
        if self.data_dependencies is None:
            self.data_dependencies = []


class FigureSuggestionService:
    """Service for identifying and suggesting relevant figures."""

    # 42 figures from FIGURE_INDEX.md (2026-03-02)
    FIGURE_REGISTRY: Dict[str, FigureMetadata] = {
        # Goldilocks Paper Figures (10)
        'G-1': FigureMetadata(
            id='G-1',
            title='Four Traditions, 150 Years Apart, Found the Same Curve',
            file_path='docs/figures/figure_1_historical_timeline.svg',
            related_concepts=['historical_roots', 'complexity', 'goldilocks', 'four_traditions'],
            phase=FigurePhase.GOLDILOCKS,
            priority=FigurePriority.HIGH,
            description='Shows four independent research traditions converging on the same inverted-U curve',
            master_doc_section='§2',
            generator_script='scripts/generate_goldilocks_figures.py'
        ),
        'G-2': FigureMetadata(
            id='G-2',
            title='Two Free Parameters Predict Where Preference Peaks',
            file_path='docs/figures/figure_2_formal_model.svg',
            related_concepts=['formal_model', 'parameters', 'preference', 'optimization'],
            phase=FigurePhase.GOLDILOCKS,
            priority=FigurePriority.HIGH,
            description='Demonstrates how two parameters model the preference peak',
            master_doc_section='§3',
            generator_script='scripts/generate_goldilocks_figures.py'
        ),
        'G-3': FigureMetadata(
            id='G-3',
            title='Five Different Senses, Five Different Metrics — One Universal Shape',
            file_path='docs/figures/figure_3_cross_modal_evidence.svg',
            related_concepts=['cross_modal', 'senses', 'universality', 'visual', 'acoustic', 'thermal', 'tactile'],
            phase=FigurePhase.GOLDILOCKS,
            priority=FigurePriority.HIGH,
            description='Shows the same inverted-U shape across vision, sound, temperature, taste, touch',
            master_doc_section='§4',
            generator_script='scripts/generate_goldilocks_figures.py'
        ),
        'G-4': FigureMetadata(
            id='G-4',
            title='Fractal Dimension Peaks at D ≈ 1.3',
            file_path='docs/figures/figure_4_fractal_dimension.svg',
            related_concepts=['fractal_dimension', 'self_similarity', 'complexity_metric', 'natural_images'],
            phase=FigurePhase.GOLDILOCKS,
            priority=FigurePriority.HIGH,
            description='Fractal dimension of natural scenes shows optimal range around D=1.3',
            master_doc_section='§5',
            generator_script='scripts/generate_goldilocks_figures.py'
        ),
        'G-5': FigureMetadata(
            id='G-5',
            title='Three Brain Layers Converge at One Complexity Level',
            file_path='docs/figures/figure_5_boxology.svg',
            related_concepts=['brain', 'complexity', 'neuroscience', 'layers', 'convergence'],
            phase=FigurePhase.GOLDILOCKS,
            priority=FigurePriority.MEDIUM,
            description='Shows subcortical, cortical, and network-level processing optimal at same complexity',
            master_doc_section='§6',
            generator_script='scripts/generate_goldilocks_figures.py'
        ),
        'G-6': FigureMetadata(
            id='G-6',
            title='Same Inverted-U Shape, Different Peak Locations',
            file_path='docs/figures/figure_6_cultural_calibration.svg',
            related_concepts=['cultural_differences', 'calibration', 'individual_differences', 'adaptation'],
            phase=FigurePhase.GOLDILOCKS,
            priority=FigurePriority.MEDIUM,
            description='Demonstrates cultural variation in optimal complexity levels',
            master_doc_section='§7',
            generator_script='scripts/generate_goldilocks_figures.py'
        ),
        'G-7': FigureMetadata(
            id='G-7',
            title='What the Goldilocks Zone Feels Like From the Inside',
            file_path='docs/figures/figure_7_processing_fluency.svg',
            related_concepts=['processing_fluency', 'experience', 'subjective', 'ease', 'enjoyment'],
            phase=FigurePhase.GOLDILOCKS,
            priority=FigurePriority.MEDIUM,
            description='Subjective experience and processing fluency in the optimal complexity range',
            master_doc_section='§8',
            generator_script='scripts/generate_goldilocks_figures.py'
        ),
        'G-8': FigureMetadata(
            id='G-8',
            title='What Four Frameworks Together Still Cannot Explain',
            file_path='docs/figures/figure_8_intellectual_surplus.svg',
            related_concepts=['limitations', 'gaps', 'unexplained', 'intellectual_surplus', 'open_questions'],
            phase=FigurePhase.GOLDILOCKS,
            priority=FigurePriority.MEDIUM,
            description='Identifies what remains unexplained even with four theoretical frameworks',
            master_doc_section='§9',
            generator_script='scripts/generate_goldilocks_figures.py'
        ),
        'G-9': FigureMetadata(
            id='G-9',
            title='The Architect\'s Cheat Sheet: Target Ranges',
            file_path='docs/figures/figure_9_design_dashboard.svg',
            related_concepts=['design', 'parameters', 'targets', 'actionable', 'specification'],
            phase=FigurePhase.GOLDILOCKS,
            priority=FigurePriority.HIGH,
            description='Practical design parameters and target ranges for architects',
            master_doc_section='§10',
            generator_script='scripts/generate_goldilocks_figures.py'
        ),
        'G-10': FigureMetadata(
            id='G-10',
            title='From Plausible Theory to Validated Design Science',
            file_path='docs/figures/figure_10_research_agenda.svg',
            related_concepts=['research_agenda', 'validation', 'theory', 'evidence', 'next_steps'],
            phase=FigurePhase.GOLDILOCKS,
            priority=FigurePriority.MEDIUM,
            description='Research roadmap for validating the theory in practice',
            master_doc_section='§11',
            generator_script='scripts/generate_goldilocks_figures.py'
        ),

        # Master Doc — Phase 1: Architecture Overview (3)
        'M-1': FigureMetadata(
            id='M-1',
            title='Three Layers Turn Scattered Evidence Into Causal Predictions',
            file_path='docs/figures/m1_three_layer_architecture.svg',
            related_concepts=['architecture', 'layers', 'evidence', 'causality', 'prediction', 'system_design'],
            phase=FigurePhase.ARCHITECTURE,
            priority=FigurePriority.HIGH,
            description='System architecture showing three processing layers',
            master_doc_section='§1, §48A (PART_I, PART_IV)',
            generator_script='scripts/generate_master_doc_figures.py'
        ),
        'M-2': FigureMetadata(
            id='M-2',
            title='From 10 Foundational Frameworks to 3,420 Evidence-Backed Beliefs',
            file_path='docs/figures/m2_tier_hierarchy.svg',
            related_concepts=['tier', 'framework', 'hierarchy', 'evidence', 'belief', 'scale'],
            phase=FigurePhase.ARCHITECTURE,
            priority=FigurePriority.HIGH,
            description='Hierarchical structure from foundational frameworks to derived beliefs',
            master_doc_section='§50 (PART_IV)',
            generator_script='scripts/generate_master_doc_figures.py'
        ),
        'M-3': FigureMetadata(
            id='M-3',
            title='Every Belief Passes Through Seven Stages of Epistemic Scrutiny',
            file_path='docs/figures/m3_pipeline_flowchart.svg',
            related_concepts=['pipeline', 'validation', 'quality', 'epistemic', 'stages', 'process'],
            phase=FigurePhase.ARCHITECTURE,
            priority=FigurePriority.HIGH,
            description='Processing pipeline with seven validation stages',
            master_doc_section='§43–§47 (PART_IV)',
            generator_script='scripts/generate_master_doc_figures.py'
        ),

        # Master Doc — Phase 2: Credence Calculus (3)
        'M-4': FigureMetadata(
            id='M-4',
            title='Four Factors Determine How Lab Evidence Transfers to Real Buildings',
            file_path='docs/figures/m4_projection_formula.svg',
            related_concepts=['credence', 'transfer', 'projection', 'design_quality', 'evidence_strength', 'population_match'],
            phase=FigurePhase.CREDENCE,
            priority=FigurePriority.HIGH,
            description='Sensitivity analysis: how d, ω, δ affect transferred confidence',
            master_doc_section='§48 (PART_IV)',
            generator_script='scripts/generate_credence_figures.py'
        ),
        'M-5': FigureMetadata(
            id='M-5',
            title='Warrant Strength Decomposes Evidence Quality Into Four Testable Components',
            file_path='docs/figures/m5_warrant_strength.svg',
            related_concepts=['warrant', 'evidence_quality', 'components', 'decomposition', 'factors'],
            phase=FigurePhase.CREDENCE,
            priority=FigurePriority.HIGH,
            description='Breakdown of evidence quality into measurable warrant components',
            master_doc_section='§48.3B (PART_IV)',
            generator_script='scripts/generate_credence_figures.py'
        ),
        'M-6': FigureMetadata(
            id='M-6',
            title='Not All Evidence Transfers Equally: The Gap Between Lab and Real-World',
            file_path='docs/figures/m6_population_transfer.svg',
            related_concepts=['transfer', 'population_match', 'external_validity', 'gap', 'realism'],
            phase=FigurePhase.CREDENCE,
            priority=FigurePriority.MEDIUM,
            description='How population mismatch reduces transferability of lab findings',
            master_doc_section='§48.3A (PART_IV)',
            generator_script='scripts/generate_credence_figures.py'
        ),

        # Master Doc — Phase 3: Domain Panel Diagrams (12)
        'M-7': FigureMetadata(
            id='M-7',
            title='VISUAL-I: Fractal Dimension Peaks at D ≈ 1.3 Because Natural Scenes Cluster There',
            file_path='docs/figures/m7_visual_panel.svg',
            related_concepts=['visual', 'fractal', 'complexity', 'natural_images', 'preference'],
            phase=FigurePhase.DOMAIN_PANEL,
            priority=FigurePriority.MEDIUM,
            description='Visual domain panel: fractal dimension of visual scenes',
            master_doc_section='§60 (PART_VI)',
            generator_script='scripts/generate_domain_panel_figures.py'
        ),
        'M-8': FigureMetadata(
            id='M-8',
            title='LIGHT-I: Two Pathways — Image-Forming Vision and Non-Visual Regulation',
            file_path='docs/figures/m8_light_panel.svg',
            related_concepts=['light', 'vision', 'circadian', 'non_visual', 'melanopsin'],
            phase=FigurePhase.DOMAIN_PANEL,
            priority=FigurePriority.MEDIUM,
            description='Light domain: dual pathways of vision and circadian regulation',
            master_doc_section='§61 (PART_VI)',
            generator_script='scripts/generate_domain_panel_figures.py'
        ),
        'M-9': FigureMetadata(
            id='M-9',
            title='THERMAL-I: Adaptive Comfort Follows Culture, Not Just Physics',
            file_path='docs/figures/m9_thermal_panel.svg',
            related_concepts=['thermal', 'comfort', 'temperature', 'culture', 'adaptation'],
            phase=FigurePhase.DOMAIN_PANEL,
            priority=FigurePriority.MEDIUM,
            description='Thermal domain: cultural and adaptive factors in comfort',
            master_doc_section='§62 (PART_VI)',
            generator_script='scripts/generate_domain_panel_figures.py'
        ),
        'M-10': FigureMetadata(
            id='M-10',
            title='ACOUSTIC-I: Soundscape Quality Modulates the Noise-Annoyance Curve',
            file_path='docs/figures/m10_acoustic_panel.svg',
            related_concepts=['acoustic', 'sound', 'noise', 'soundscape', 'quality'],
            phase=FigurePhase.DOMAIN_PANEL,
            priority=FigurePriority.MEDIUM,
            description='Acoustic domain: soundscape quality effects on annoyance',
            master_doc_section='§63 (PART_VI)',
            generator_script='scripts/generate_domain_panel_figures.py'
        ),
        'M-11': FigureMetadata(
            id='M-11',
            title='MUSIC-I: Eight BRECVEMA Mechanisms With Different Temporal Signatures',
            file_path='docs/figures/m11_music_panel.svg',
            related_concepts=['music', 'emotion', 'brecvema', 'mechanisms', 'temporal'],
            phase=FigurePhase.DOMAIN_PANEL,
            priority=FigurePriority.LOW,
            description='Music domain: temporal signatures of emotion mechanisms',
            master_doc_section='§64 (PART_VI)',
            generator_script='scripts/generate_domain_panel_figures.py'
        ),
        'M-12': FigureMetadata(
            id='M-12',
            title='STRESS-I: Cortisol Dynamics Reveal Allostatic Load Before Symptoms',
            file_path='docs/figures/m12_stress_panel.svg',
            related_concepts=['stress', 'cortisol', 'allostatic_load', 'health', 'physiology'],
            phase=FigurePhase.DOMAIN_PANEL,
            priority=FigurePriority.MEDIUM,
            description='Stress domain: cortisol dynamics and allostatic load',
            master_doc_section='§65 (PART_VI)',
            generator_script='scripts/generate_domain_panel_figures.py'
        ),
        'M-13': FigureMetadata(
            id='M-13',
            title='SOCIAL-I: Proxemics Zones Define Optimal Density',
            file_path='docs/figures/m13_social_panel.svg',
            related_concepts=['social', 'proximity', 'density', 'crowding', 'interpersonal'],
            phase=FigurePhase.DOMAIN_PANEL,
            priority=FigurePriority.MEDIUM,
            description='Social domain: proxemics and optimal spatial density',
            master_doc_section='§66 (PART_VI)',
            generator_script='scripts/generate_domain_panel_figures.py'
        ),
        'M-14': FigureMetadata(
            id='M-14',
            title='MEMORY-I: Hippocampal Place Cells Map Architecture Into Cognitive Maps',
            file_path='docs/figures/m14_memory_panel.svg',
            related_concepts=['memory', 'hippocampus', 'place_cells', 'navigation', 'spatial'],
            phase=FigurePhase.DOMAIN_PANEL,
            priority=FigurePriority.MEDIUM,
            description='Memory domain: spatial representation in hippocampus',
            master_doc_section='§67 (PART_VI)',
            generator_script='scripts/generate_domain_panel_figures.py'
        ),
        'M-15': FigureMetadata(
            id='M-15',
            title='MULTI-I: Cross-Modal Interactions Are the Rule, Not the Exception',
            file_path='docs/figures/m15_multi_panel.svg',
            related_concepts=['multisensory', 'integration', 'cross_modal', 'interaction'],
            phase=FigurePhase.DOMAIN_PANEL,
            priority=FigurePriority.MEDIUM,
            description='Multisensory domain: cross-modal integration patterns',
            master_doc_section='§68 (PART_VI)',
            generator_script='scripts/generate_domain_panel_figures.py'
        ),
        'M-16': FigureMetadata(
            id='M-16',
            title='CREATIVE-I: Flow States Require Environmental Conditions',
            file_path='docs/figures/m16_creative_panel.svg',
            related_concepts=['creativity', 'flow', 'optimal_conditions', 'productivity'],
            phase=FigurePhase.DOMAIN_PANEL,
            priority=FigurePriority.MEDIUM,
            description='Creativity domain: environmental conditions for flow states',
            master_doc_section='§69 (PART_VI)',
            generator_script='scripts/generate_domain_panel_figures.py'
        ),
        'M-17': FigureMetadata(
            id='M-17',
            title='NEUROMOD-I: Three Neuromodulators Converge at the Complexity Optimum',
            file_path='docs/figures/m17_neuromod_panel.svg',
            related_concepts=['neuromodulation', 'dopamine', 'norepinephrine', 'acetylcholine'],
            phase=FigurePhase.DOMAIN_PANEL,
            priority=FigurePriority.MEDIUM,
            description='Neuromodulation domain: multiple transmitters converge at optimal complexity',
            master_doc_section='§70 (PART_VI)',
            generator_script='scripts/generate_domain_panel_figures.py'
        ),
        'M-18': FigureMetadata(
            id='M-18',
            title='CROSSCUT-I: Cross-Panel Interactions Form a Dense Network',
            file_path='docs/figures/m18_crosscut_panel.svg',
            related_concepts=['integration', 'interactions', 'network', 'cross_cutting'],
            phase=FigurePhase.DOMAIN_PANEL,
            priority=FigurePriority.MEDIUM,
            description='Cross-cutting interactions between domain panels',
            master_doc_section='§71 (PART_VI)',
            generator_script='scripts/generate_domain_panel_figures.py'
        ),

        # Master Doc — Phase 4: System Operations (3)
        'M-19': FigureMetadata(
            id='M-19',
            title='The Nightly Pipeline: 13 Stages of Evidence Maintenance',
            file_path='docs/figures/m19_nightly_pipeline.svg',
            related_concepts=['pipeline', 'operations', 'maintenance', 'evidence', 'automation'],
            phase=FigurePhase.OPERATIONS,
            priority=FigurePriority.MEDIUM,
            description='Automated nightly pipeline for evidence updates',
            master_doc_section='Overseer sections (PART_XVIII)',
            generator_script='scripts/generate_operations_figures.py'
        ),
        'M-20': FigureMetadata(
            id='M-20',
            title='The Recommendation Loop: From Gap to Article to Belief',
            file_path='docs/figures/m20_recommendation_loop.svg',
            related_concepts=['recommendations', 'feedback_loop', 'research_gaps', 'articles'],
            phase=FigurePhase.OPERATIONS,
            priority=FigurePriority.MEDIUM,
            description='Feedback loop for generating new research recommendations',
            master_doc_section='§47A–E (PART_IV)',
            generator_script='scripts/generate_operations_figures.py'
        ),
        'M-21': FigureMetadata(
            id='M-21',
            title='AESHI Score: Six Subscores Combine Into One System Health Number',
            file_path='docs/figures/m21_aeshi_score.svg',
            related_concepts=['health_score', 'aeshi', 'metrics', 'quality', 'system_evaluation'],
            phase=FigurePhase.OPERATIONS,
            priority=FigurePriority.MEDIUM,
            description='System health metric combining six subscores',
            master_doc_section='§53.8 (PART_IX)',
            generator_script='scripts/generate_operations_figures.py'
        ),

        # Master Doc — Phase 5: Data Dashboards (3)
        'M-22': FigureMetadata(
            id='M-22',
            title='Evidence Landscape: 3,420 Beliefs by Tier, Framework, and Confidence',
            file_path='docs/figures/m22_evidence_landscape.svg',
            related_concepts=['landscape', 'beliefs', 'confidence', 'distribution', 'overview'],
            phase=FigurePhase.DASHBOARD,
            priority=FigurePriority.MEDIUM,
            description='Overall distribution of beliefs across tiers and confidence levels',
            master_doc_section='PART_IX',
            generator_script='scripts/generate_dashboard_figures.py'
        ),
        'M-23': FigureMetadata(
            id='M-23',
            title='Warrant Type Distribution Across the Web of Belief',
            file_path='docs/figures/m23_warrant_distribution.svg',
            related_concepts=['warrant', 'types', 'distribution', 'network'],
            phase=FigurePhase.DASHBOARD,
            priority=FigurePriority.MEDIUM,
            description='Distribution of warrant types supporting the belief network',
            master_doc_section='PART_IX',
            generator_script='scripts/generate_dashboard_figures.py'
        ),
        'M-24': FigureMetadata(
            id='M-24',
            title='Schema Gaps: Where ATLAS Knows It Doesn\'t Know',
            file_path='docs/figures/m24_schema_gaps.svg',
            related_concepts=['gaps', 'gaps_in_knowledge', 'uncertainty', 'limitations'],
            phase=FigurePhase.DASHBOARD,
            priority=FigurePriority.MEDIUM,
            description='Identified gaps and areas of acknowledged uncertainty',
            master_doc_section='PART_IX',
            generator_script='scripts/generate_dashboard_figures.py'
        ),

        # Master Doc — Phase 6: Mathematical Explanation Figures (8)
        'M-25': FigureMetadata(
            id='M-25',
            title='How Study Design Quality and Evidence Strength Determine What Architects Can Trust',
            file_path='docs/figures/m25_sensitivity_analysis.svg',
            related_concepts=['sensitivity', 'design_quality', 'evidence_strength', 'transfer', 'confidence'],
            phase=FigurePhase.MATH_EXPLANATION,
            priority=FigurePriority.HIGH,
            description='Sensitivity analysis: how d and ω factors affect transferred confidence',
            master_doc_section='§48.1A (PART_IV)',
            generator_script='scripts/generate_math_figures.py'
        ),
        'M-26': FigureMetadata(
            id='M-26',
            title='Measuring Epistemic Health: How C* Reveals What the Web Gets Right and Where It Breaks',
            file_path='docs/figures/m26_coherence_visualization.svg',
            related_concepts=['coherence', 'epistemic_health', 'c_star', 'system_health'],
            phase=FigurePhase.MATH_EXPLANATION,
            priority=FigurePriority.HIGH,
            description='Coherence metric visualization showing system epistemic health',
            master_doc_section='§84.2A (PART_IX)',
            generator_script='scripts/generate_math_figures.py'
        ),
        'M-27': FigureMetadata(
            id='M-27',
            title='From Evidence to Confidence: How Quality, Reliability, and Population Match Combine',
            file_path='docs/figures/m27_credence_pipeline.svg',
            related_concepts=['credence', 'pipeline', 'quality', 'reliability', 'population_match'],
            phase=FigurePhase.MATH_EXPLANATION,
            priority=FigurePriority.HIGH,
            description='Step-by-step credence computation pipeline',
            master_doc_section='§48.3B (PART_IV)',
            generator_script='scripts/generate_math_figures.py'
        ),
        'M-28': FigureMetadata(
            id='M-28',
            title='The ATLAS Inference Engine: Six Algorithms That Make the Web Computable',
            file_path='docs/figures/m28_inference_engine.svg',
            related_concepts=['inference', 'algorithms', 'computation', 'engine'],
            phase=FigurePhase.MATH_EXPLANATION,
            priority=FigurePriority.HIGH,
            description='Six core algorithms powering ATLAS inference',
            master_doc_section='§129 (PART_XVII)',
            generator_script='scripts/generate_math_figures.py'
        ),
        'M-29': FigureMetadata(
            id='M-29',
            title='What Should ATLAS Investigate Next? Uncertainties by Impact and Network Reach',
            file_path='docs/figures/m29_voi_uncertainties.svg',
            related_concepts=['voi', 'value_of_information', 'priority', 'uncertainty'],
            phase=FigurePhase.MATH_EXPLANATION,
            priority=FigurePriority.MEDIUM,
            description='Value of information: which uncertainties matter most',
            master_doc_section='§129.6 (PART_XVII)',
            generator_script='scripts/generate_math_figures.py'
        ),
        'M-30': FigureMetadata(
            id='M-30',
            title='The Bridge from Lab to Building: Why Different Evidence Types Transfer Differently',
            file_path='docs/figures/m30_warrant_hierarchy.svg',
            related_concepts=['transfer', 'warrant', 'evidence_types', 'hierarchy', 'external_validity'],
            phase=FigurePhase.MATH_EXPLANATION,
            priority=FigurePriority.MEDIUM,
            description='Hierarchy of evidence types and their differential transferability',
            master_doc_section='§48.1A (PART_IV)',
            generator_script='scripts/generate_math_figures.py'
        ),
        'M-31': FigureMetadata(
            id='M-31',
            title='Why Some Claims Are Fragile and Others Robust: Serial Chains vs. Parallel Convergence',
            file_path='docs/figures/m31_serial_vs_parallel.svg',
            related_concepts=['robustness', 'fragility', 'serial', 'parallel', 'convergence'],
            phase=FigurePhase.MATH_EXPLANATION,
            priority=FigurePriority.MEDIUM,
            description='How warrant architecture (serial vs parallel) affects claim robustness',
            master_doc_section='§48.4–48.5 (PART_IV)',
            generator_script='scripts/generate_math_figures.py'
        ),
        'M-32': FigureMetadata(
            id='M-32',
            title='When Evidence Conflicts: How ATLAS Revises Beliefs While Protecting Core Commitments',
            file_path='docs/figures/m32_entrenchment_ordering.svg',
            related_concepts=['conflict', 'revision', 'entrenchment', 'belief_dynamics'],
            phase=FigurePhase.MATH_EXPLANATION,
            priority=FigurePriority.HIGH,
            description='Belief revision dynamics under conflicting evidence',
            master_doc_section='§129.5 (PART_XVII)',
            generator_script='scripts/generate_math_figures.py'
        ),
    }

    def __init__(self, figure_index_path: Optional[str] = None):
        """
        Initialize the figure suggestion service.

        Args:
            figure_index_path: Optional path to figure index JSON file
        """
        self._figure_index = self.FIGURE_REGISTRY
        self._concept_to_figures: Dict[str, List[str]] = self._build_concept_index()
        logger.info(f"Figure Suggestion Service initialized with {len(self._figure_index)} figures")

    def _build_concept_index(self) -> Dict[str, List[str]]:
        """Build reverse index from concepts to figure IDs."""
        concept_index = {}
        for fig_id, metadata in self._figure_index.items():
            for concept in metadata.related_concepts:
                if concept not in concept_index:
                    concept_index[concept] = []
                concept_index[concept].append(fig_id)
        return concept_index

    def suggest_figures(self, topic: str, beliefs: List[Dict[str, Any]] = None, max_figures: int = 5) -> List[FigureMetadata]:
        """
        Return relevant figures for a topic, ranked by relevance.

        Args:
            topic: Topic string or concept name
            beliefs: Optional list of belief dictionaries with 'concept' keys
            max_figures: Maximum number of figures to return

        Returns:
            List of FigureMetadata objects, ranked by relevance
        """
        # Collect all matching concepts
        matching_figure_ids = set()
        scores = {}  # figure_id -> relevance_score

        # Search by topic keywords
        topic_lower = topic.lower()
        keywords = [kw.strip() for kw in topic_lower.split()]

        # Direct keyword match in figure titles and concepts
        for fig_id, metadata in self._figure_index.items():
            score = 0
            title_lower = metadata.title.lower()

            # Keyword matches
            for keyword in keywords:
                if keyword in title_lower:
                    score += 2
                for concept in metadata.related_concepts:
                    if keyword in concept.lower():
                        score += 1

            if score > 0:
                matching_figure_ids.add(fig_id)
                scores[fig_id] = score

        # Add figures from beliefs if provided
        if beliefs:
            for belief in beliefs:
                if 'concept' in belief:
                    concept = belief['concept'].lower()
                    if concept in self._concept_to_figures:
                        for fig_id in self._concept_to_figures[concept]:
                            matching_figure_ids.add(fig_id)
                            scores[fig_id] = scores.get(fig_id, 0) + 1.5

        # Sort by relevance (score) then by priority
        sorted_figures = []
        for fig_id in sorted(matching_figure_ids, key=lambda x: (-scores.get(x, 0), -self._priority_value(self._figure_index[x].priority))):
            sorted_figures.append(self._figure_index[fig_id])

        return sorted_figures[:max_figures]

    def get_figure_metadata(self, figure_id: str) -> Optional[FigureMetadata]:
        """
        Get full metadata for a figure.

        Args:
            figure_id: Figure ID (e.g., 'M-25', 'G-1')

        Returns:
            FigureMetadata object or None if not found
        """
        return self._figure_index.get(figure_id)

    def get_figure_for_concept(self, concept: str) -> Optional[FigureMetadata]:
        """
        Get the best figure for a specific concept.

        Args:
            concept: Concept name (e.g., 'credence_projection', 'coherence')

        Returns:
            FigureMetadata for best matching figure
        """
        concept_lower = concept.lower().replace(' ', '_')

        # Direct lookup
        if concept_lower in self._concept_to_figures:
            figure_ids = self._concept_to_figures[concept_lower]
            # Return highest priority
            best_id = max(figure_ids, key=lambda x: -self._priority_value(self._figure_index[x].priority))
            return self._figure_index[best_id]

        # Fuzzy match on concepts
        for fig_id, metadata in self._figure_index.items():
            for fig_concept in metadata.related_concepts:
                if concept_lower in fig_concept.lower() or fig_concept.lower() in concept_lower:
                    return metadata

        return None

    def get_figures_by_phase(self, phase: FigurePhase) -> List[FigureMetadata]:
        """Get all figures for a specific documentation phase."""
        return [meta for meta in self._figure_index.values() if meta.phase == phase]

    def get_figures_by_priority(self, priority: FigurePriority) -> List[FigureMetadata]:
        """Get all figures with a specific priority level."""
        return [meta for meta in self._figure_index.values() if meta.priority == priority]

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the figure registry."""
        by_phase = {}
        by_priority = {}

        for metadata in self._figure_index.values():
            phase_name = metadata.phase.value
            priority_name = metadata.priority.value

            if phase_name not in by_phase:
                by_phase[phase_name] = 0
            by_phase[phase_name] += 1

            if priority_name not in by_priority:
                by_priority[priority_name] = 0
            by_priority[priority_name] += 1

        return {
            'total_figures': len(self._figure_index),
            'by_phase': by_phase,
            'by_priority': by_priority,
            'total_concepts': len(self._concept_to_figures),
        }

    # =========================================================================
    # Private Helper Methods
    # =========================================================================

    def _priority_value(self, priority: FigurePriority) -> int:
        """Convert priority to numeric value for sorting."""
        return {'high': 3, 'medium': 2, 'low': 1}.get(priority.value, 0)
