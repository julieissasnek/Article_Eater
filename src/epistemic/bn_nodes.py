"""
Epistemic BN Node Definitions (Sprint T2-2.1).

Defines the 10 epistemic variables for the Bayesian network integration.
These variables enable reasoning about epistemic states, prediction errors,
and source quality within the causal model.

References:
- CNFA: Cognitive Neuroscience of Architecture
- PE: Prediction Error (predictive processing framework)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum


# =============================================================================
# VARIABLE TYPE ENUM
# =============================================================================

class VariableType(str, Enum):
    """Types of BN variables."""
    CONTINUOUS = "continuous"
    BINARY = "binary"
    CATEGORICAL = "categorical"


# =============================================================================
# EPISTEMIC VARIABLE DATACLASS
# =============================================================================

@dataclass
class EpistemicVariable:
    """
    An epistemic variable in the Bayesian network.

    Extends the basic Variable concept with epistemic metadata
    for integration with the web of belief.
    """
    var_id: str
    name: str
    description: str
    var_type: VariableType = VariableType.CONTINUOUS
    domain: Tuple[float, float] = (0.0, 1.0)
    categories: Optional[List[str]] = None

    # Epistemic metadata
    is_observable: bool = False  # Can be directly measured?
    is_latent: bool = True       # Inferred from other variables?
    default_value: float = 0.5

    # Integration with web of belief
    supporting_belief_pattern: Optional[str] = None  # Regex for matching beliefs

    def to_dict(self) -> Dict:
        return {
            "var_id": self.var_id,
            "name": self.name,
            "description": self.description,
            "var_type": self.var_type.value,
            "domain": list(self.domain),
            "is_observable": self.is_observable,
            "is_latent": self.is_latent,
            "default_value": self.default_value,
        }


# =============================================================================
# EPISTEMIC BN VARIABLES (Task 2.1)
# =============================================================================

# Environmental epistemic variables
ENVIRONMENTAL_LEGIBILITY = EpistemicVariable(
    var_id="environmental_legibility",
    name="Environmental Legibility",
    description="How well the environment supports belief formation and spatial understanding",
    domain=(0.0, 1.0),
    is_observable=False,
    is_latent=True,
    default_value=0.5,
    supporting_belief_pattern=r"legib|wayfind|spatial.*layout|comprehens"
)

BELIEF_COHERENCE = EpistemicVariable(
    var_id="belief_coherence",
    name="Belief Coherence",
    description="Internal consistency of the environmental mental model",
    domain=(0.0, 1.0),
    is_observable=False,
    is_latent=True,
    default_value=0.5,
    supporting_belief_pattern=r"coherenc|consisten|integrat"
)

EPISTEMIC_FLUENCY = EpistemicVariable(
    var_id="epistemic_fluency",
    name="Epistemic Fluency",
    description="Speed and ease of forming coherent interpretations of the environment",
    domain=(0.0, 1.0),
    is_observable=False,
    is_latent=True,
    default_value=0.5,
    supporting_belief_pattern=r"fluenc|process.*ease|cognitive.*load"
)

EPISTEMIC_AFFECT = EpistemicVariable(
    var_id="epistemic_affect",
    name="Epistemic Affect",
    description="Hedonic signal from epistemic processing (positive=understanding, negative=confusion)",
    domain=(-1.0, 1.0),  # Note: bipolar scale
    is_observable=True,  # Can be measured via self-report
    is_latent=False,
    default_value=0.0,
    supporting_belief_pattern=r"curiosity|interest|confus|frustra|satisf"
)

# Prediction Error variables (from predictive processing framework)
FUNCTIONAL_PE = EpistemicVariable(
    var_id="functional_PE",
    name="Functional Prediction Error",
    description="Affordance mismatch - when space doesn't support expected activities",
    domain=(0.0, 1.0),
    is_observable=False,
    is_latent=True,
    default_value=0.0,  # No PE is default
    supporting_belief_pattern=r"affordanc|function|purpose|use|activity"
)

NAVIGATIONAL_PE = EpistemicVariable(
    var_id="navigational_PE",
    name="Navigational Prediction Error",
    description="Spatial model mismatch - when layout doesn't match expectations",
    domain=(0.0, 1.0),
    is_observable=False,
    is_latent=True,
    default_value=0.0,
    supporting_belief_pattern=r"wayfind|lost|disorient|route|layout|navigat"
)

SOCIAL_PE = EpistemicVariable(
    var_id="social_PE",
    name="Social Prediction Error",
    description="Social script mismatch - when social norms/behaviors don't fit expectations",
    domain=(0.0, 1.0),
    is_observable=False,
    is_latent=True,
    default_value=0.0,
    supporting_belief_pattern=r"social.*norm|belong|appropriat|behavior|etiquette"
)

# Source quality and claim assessment variables
SOURCE_QUALITY = EpistemicVariable(
    var_id="source_quality",
    name="Source Quality",
    description="Composite evidence quality score for a claim",
    domain=(0.0, 1.0),
    is_observable=True,  # Computed from study metadata
    is_latent=False,
    default_value=0.5,
    supporting_belief_pattern=None  # Applies to all claims
)

CLAIM_ACCEPTANCE = EpistemicVariable(
    var_id="claim_acceptance",
    name="Claim Acceptance",
    description="Posterior probability of accepting a claim given evidence",
    domain=(0.0, 1.0),
    is_observable=False,
    is_latent=True,
    default_value=0.5,
    supporting_belief_pattern=None
)

CLAIM_COHERENCE = EpistemicVariable(
    var_id="claim_coherence",
    name="Claim Coherence",
    description="How well a claim fits the existing web of belief",
    domain=(0.0, 1.0),
    is_observable=False,
    is_latent=True,
    default_value=0.5,
    supporting_belief_pattern=None
)


# =============================================================================
# SOURCE QUALITY COMPONENT VARIABLES (Task 2.3)
# =============================================================================

# These variables feed into the source_quality composite score

METHODOLOGICAL_RIGOR = EpistemicVariable(
    var_id="methodological_rigor",
    name="Methodological Rigor",
    description="Quality of study design (randomization, blinding, sample size, pre-registration)",
    domain=(0.0, 1.0),
    is_observable=True,  # Extracted from paper metadata
    is_latent=False,
    default_value=0.5,
    supporting_belief_pattern=r"random|blind|sample.*size|pre.*regist|control|RCT"
)

THEORETICAL_COMMITMENT = EpistemicVariable(
    var_id="theoretical_commitment",
    name="Theoretical Commitment",
    description="Degree of a priori theoretical commitment in study design (potential bias)",
    domain=(0.0, 1.0),
    is_observable=True,  # Inferred from author affiliations, framing
    is_latent=False,
    default_value=0.5,  # Neutral default
    supporting_belief_pattern=r"confirm|bias|theor.*driven|hypothesis.*confirm"
)

INDEPENDENCE_OF_EVIDENCE = EpistemicVariable(
    var_id="independence_of_evidence",
    name="Independence of Evidence",
    description="Are studies independent or from same lab/paradigm cluster?",
    domain=(0.0, 1.0),
    is_observable=True,  # Computed from author overlap, citation network
    is_latent=False,
    default_value=0.5,
    supporting_belief_pattern=r"independent|replicat|different.*lab|cross.*lab"
)

REPLICATION_STATUS = EpistemicVariable(
    var_id="replication_status",
    name="Replication Status",
    description="Has the finding been replicated? (Failed=0, Unreplicated=0.5, Replicated=1)",
    domain=(0.0, 1.0),
    is_observable=True,  # From replication databases, meta-analyses
    is_latent=False,
    default_value=0.5,  # Unreplicated default
    supporting_belief_pattern=r"replicat|reproduc|confirm|fail.*replicat"
)

# Source quality component registry
SOURCE_QUALITY_COMPONENTS: Dict[str, EpistemicVariable] = {
    "methodological_rigor": METHODOLOGICAL_RIGOR,
    "theoretical_commitment": THEORETICAL_COMMITMENT,
    "independence_of_evidence": INDEPENDENCE_OF_EVIDENCE,
    "replication_status": REPLICATION_STATUS,
}


# =============================================================================
# VARIABLE REGISTRY
# =============================================================================

EPISTEMIC_VARIABLES: Dict[str, EpistemicVariable] = {
    "environmental_legibility": ENVIRONMENTAL_LEGIBILITY,
    "belief_coherence": BELIEF_COHERENCE,
    "epistemic_fluency": EPISTEMIC_FLUENCY,
    "epistemic_affect": EPISTEMIC_AFFECT,
    "functional_PE": FUNCTIONAL_PE,
    "navigational_PE": NAVIGATIONAL_PE,
    "social_PE": SOCIAL_PE,
    "source_quality": SOURCE_QUALITY,
    "claim_acceptance": CLAIM_ACCEPTANCE,
    "claim_coherence": CLAIM_COHERENCE,
}


def get_epistemic_variable(var_id: str) -> Optional[EpistemicVariable]:
    """Get an epistemic variable by ID."""
    return EPISTEMIC_VARIABLES.get(var_id)


def list_epistemic_variables() -> List[str]:
    """List all epistemic variable IDs."""
    return list(EPISTEMIC_VARIABLES.keys())


def get_pe_variables() -> List[EpistemicVariable]:
    """Get all prediction error variables."""
    return [
        FUNCTIONAL_PE,
        NAVIGATIONAL_PE,
        SOCIAL_PE,
    ]


def get_environmental_variables() -> List[EpistemicVariable]:
    """Get all environmental epistemic variables."""
    return [
        ENVIRONMENTAL_LEGIBILITY,
        BELIEF_COHERENCE,
        EPISTEMIC_FLUENCY,
        EPISTEMIC_AFFECT,
    ]


def get_source_quality_variables() -> List[EpistemicVariable]:
    """Get all source quality related variables."""
    return [
        SOURCE_QUALITY,
        CLAIM_ACCEPTANCE,
        CLAIM_COHERENCE,
    ]


def get_source_quality_component_variables() -> List[EpistemicVariable]:
    """Get all source quality component variables (inputs to source_quality)."""
    return [
        METHODOLOGICAL_RIGOR,
        THEORETICAL_COMMITMENT,
        INDEPENDENCE_OF_EVIDENCE,
        REPLICATION_STATUS,
    ]
