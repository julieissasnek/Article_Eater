"""
Configuration for Article Eater Streamlit Interface
Sprint 3.0 — 2026-02-08
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
import os

# API Configuration
API_BASE_URL = os.environ.get("AE_API_URL", "http://localhost:8000")
API_VERSION = "v1"

# Page Configuration
PAGE_TITLE = "Article Eater V23"
PAGE_ICON = "📚"
LAYOUT = "wide"

# Theme colors (light cheerful aesthetic)
COLORS = {
    "primary": "#5B8FB9",      # Soft blue
    "secondary": "#7FC8A9",    # Mint green
    "accent": "#F5D491",       # Warm yellow
    "warning": "#E8A87C",      # Soft peach
    "danger": "#E27D60",       # Soft coral
    "success": "#85D2A3",      # Light green
    "background": "#FFF9F0",   # Warm cream
    "text": "#4A5568",         # Soft gray (not black)
    "card_bg": "#FFFFFF",      # White cards
    "border": "#E2E8F0",       # Light border
}

# Credence thresholds
CREDENCE_THRESHOLDS = {
    "high": 0.75,
    "moderate": 0.50,
    "low": 0.25,
}


@dataclass
class UserType:
    """Represents a user type with persona and common questions."""
    id: str
    name: str
    persona: Optional[str]
    description: str
    icon: str
    common_questions: List[str] = field(default_factory=list)


# User Types with Common Questions (per Cooper personas)
USER_TYPES: Dict[str, UserType] = {
    "practitioner": UserType(
        id="practitioner",
        name="Practitioner / Designer",
        persona="Marcus Williams, Healthcare Architect",
        description="Evidence-based design decisions for real-world projects",
        icon="🏗️",
        common_questions=[
            "What reduces stress in hospitals?",
            "Evidence for plants in offices?",
            "Windows vs skylights for wellbeing?",
            "Practical recommendations for waiting rooms",
            "What's the dosage for biophilic elements?",
            "Nature views — what counts as 'nature'?",
            "Cost-effective interventions ranked by evidence",
            "What should I avoid based on evidence?",
        ]
    ),
    "senior_researcher": UserType(
        id="senior_researcher",
        name="Senior Researcher",
        persona="Dr. Sarah Chen",
        description="Comprehensive literature reviews and evidence synthesis",
        icon="🔬",
        common_questions=[
            "What are the gaps in biophilic design research?",
            "Which findings have methodological concerns?",
            "What mechanisms explain nature-health links?",
            "ART vs SRT — evidence quality comparison?",
            "What would change if Ulrich 1984 were retracted?",
            "Cross-study heterogeneity for stress outcomes?",
            "Which findings are contested between communities?",
            "Temporal trends in the evidence base?",
            "What populations are understudied?",
            "Strongest and weakest evidence by domain?",
        ]
    ),
    "graduate_student": UserType(
        id="graduate_student",
        name="Graduate Student",
        persona="Jordan Taylor",
        description="Learning the field and finding thesis direction",
        icon="🎓",
        common_questions=[
            "How does ART theory work?",
            "What are the key papers on biophilia?",
            "What's contested in this field?",
            "Where should I focus my thesis?",
            "Explain the evidence hierarchy",
            "What's the difference between ART and SRT?",
            "Who are the major researchers?",
            "What methodologies are commonly used?",
            "Recent trends in the field?",
            "Entry points for a newcomer?",
        ]
    ),
    "systematic_reviewer": UserType(
        id="systematic_reviewer",
        name="Systematic Reviewer",
        persona=None,
        description="Comprehensive, reproducible evidence synthesis",
        icon="📋",
        common_questions=[
            "All evidence for stress reduction outcomes",
            "Studies with RCT methodology only",
            "Export all citations for nature exposure",
            "Cross-study comparison table for plants",
            "Quality assessment for biophilia studies",
            "Forest plot data for meta-analysis",
            "PRISMA-compatible evidence export",
        ]
    ),
    "quick_lookup": UserType(
        id="quick_lookup",
        name="Quick Lookup",
        persona=None,
        description="Fast answers to specific questions",
        icon="⚡",
        common_questions=[
            "Credence for 'plants reduce stress'?",
            "What supports the biophilia hypothesis?",
            "Is ART theory established or contested?",
            "Key finding on hospital gardens?",
            "How many studies on nature sounds?",
        ]
    ),
}


# Query Types (Pearl's ladder + Bates extensions)
QUERY_TYPES = {
    "WHAT": "What is X? What does Y show?",
    "WHY": "Why does X happen? What mechanism?",
    "COMPARE": "How does X compare to Y?",
    "GAPS": "What don't we know about X?",
    "CONTRADICT": "What contradicts X?",
    "CONTINGENT": "When does X apply? Scope conditions?",
    "HOW_CONFIDENT": "How confident are we about X?",
    "RELATED": "What's related to X?",
    "TRENDING": "What's gaining/losing support?",
    "CANONICAL": "What's the seminal work on X?",
}


# Epistemic Levels (cheerful colors)
EPISTEMIC_LEVELS = {
    "THEORETICAL": {"weight": 0.8, "color": "#5B8FB9"},   # Soft blue
    "INTERMEDIATE": {"weight": 0.5, "color": "#7FC8A9"},  # Mint green
    "EMPIRICAL": {"weight": 0.3, "color": "#85D2A3"},     # Light green
    "OBSERVATIONAL": {"weight": 0.2, "color": "#F5D491"}, # Warm yellow
}


# Belief Status (cheerful colors)
BELIEF_STATUS = {
    "ACCEPTED": {"icon": "✓", "color": "#85D2A3"},    # Light green
    "REJECTED": {"icon": "✗", "color": "#E27D60"},    # Soft coral
    "CONTESTED": {"icon": "⚡", "color": "#E8A87C"},  # Soft peach
    "STUB": {"icon": "?", "color": "#B8C5D0"},        # Light gray-blue
}


# Admin Statistics Keys
ADMIN_STATS = [
    "total_beliefs",
    "total_constraints",
    "total_papers",
    "total_communities",
    "overall_coherence",
    "average_credence",
    "contested_beliefs",
    "stub_beliefs",
]


def get_api_url(endpoint: str) -> str:
    """Construct full API URL for an endpoint."""
    return f"{API_BASE_URL}/api/{API_VERSION}/{endpoint.lstrip('/')}"


def credence_to_label(credence: float) -> str:
    """Convert credence value to human-readable label."""
    if credence >= CREDENCE_THRESHOLDS["high"]:
        return "High confidence"
    elif credence >= CREDENCE_THRESHOLDS["moderate"]:
        return "Moderate confidence"
    elif credence >= CREDENCE_THRESHOLDS["low"]:
        return "Low confidence"
    else:
        return "Very low confidence"


def credence_to_color(credence: float) -> str:
    """Convert credence value to display color (cheerful palette)."""
    if credence >= CREDENCE_THRESHOLDS["high"]:
        return "#85D2A3"  # Light green
    elif credence >= CREDENCE_THRESHOLDS["moderate"]:
        return "#7FC8A9"  # Mint
    elif credence >= CREDENCE_THRESHOLDS["low"]:
        return "#F5D491"  # Warm yellow
    else:
        return "#E8A87C"  # Soft peach
