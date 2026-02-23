"""CMR SQLAlchemy data models from Doc 68 Part 2."""

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
    create_engine,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.types import JSON

Base = declarative_base()


class TemplateRecord(Base):
    """
    DB index for template JSON files.

    Source of truth remains JSON. This table provides queryable metadata
    for efficient filtering and classification per Doc 67 deduplication map.

    Fields per Doc 68 Part 2.1 schema (verbatim).
    """

    __tablename__ = "templates"

    id = Column(Integer, primary_key=True)
    template_id = Column(String, unique=True, nullable=False)
    # e.g. "COLLABORATIVE_CREATIVITY_ARCHITECTURE_001"
    display_id = Column(String, unique=True, nullable=False)
    # e.g. "CREA4"
    name = Column(String, nullable=False)
    series = Column(String, nullable=False)
    # e.g. "CREA", "L", "MAT", "T"
    generation = Column(Integer, nullable=False)
    # 1 = T/M/AX series; 2 = domain series

    # Classification from Doc 67
    dedup_status = Column(String, nullable=False)
    # "active" | "superseded" | "residual" | "reference" | "gap"
    superseded_by = Column(String, nullable=True)
    # display_id of superseding template, if applicable

    # Metadata
    pe_contribution = Column(String, nullable=False)
    # "predictive" | "explanatory" | "organizational"
    maturity = Column(String, nullable=False)
    # "established" | "supported" | ... | "speculative"
    calibration_status = Column(String, nullable=False)
    # "substantial" | "partial" | "protocol" | "uncalibrated"
    practical_accessibility = Column(String, nullable=False)
    # "A" | "B" | "C" | "D"
    ecological_validation = Column(Boolean, default=False)

    # File reference
    json_path = Column(String, nullable=False)
    # Relative path to JSON file in data/templates/

    # Source documents
    source_docs = Column(String, nullable=False)
    # Comma-separated doc numbers, e.g. "55,58,65"

    def __repr__(self) -> str:
        return (
            f"<TemplateRecord(display_id={self.display_id!r}, "
            f"series={self.series!r}, generation={self.generation}, "
            f"dedup_status={self.dedup_status!r})>"
        )


class CMREvaluation(Base):
    """A single evaluation run: paper OR building assessment."""

    __tablename__ = "cmr_evaluations"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=func.now())
    evaluation_type = Column(String, nullable=False)
    # "paper" | "building" | "design_review"
    target_description = Column(Text, nullable=False)
    # Free text: paper citation, building name, design brief
    status = Column(String, default="in_progress")
    # "in_progress" | "complete" | "failed"

    # For building evaluations
    building_context = Column(JSON, nullable=True)
    # {climate: str, building_type: str, occupant_profile: {...}}

    # Relationships
    template_activations = relationship(
        "CMRTemplateActivation", back_populates="evaluation"
    )
    domain_scores = relationship("CMRDomainScore", back_populates="evaluation")
    overall_scores = relationship("CMROverallScore", back_populates="evaluation")


class CMRTemplateActivation(Base):
    """Which templates were activated for this evaluation and why."""

    __tablename__ = "cmr_template_activations"

    id = Column(Integer, primary_key=True)
    evaluation_id = Column(Integer, ForeignKey("cmr_evaluations.id"))
    template_display_id = Column(String, ForeignKey("templates.display_id"))

    activation_reason = Column(Text)
    # Why this template was activated for this evaluation

    # Inputs provided
    inputs = Column(JSON, nullable=False)
    # {parameter_name: value, ...} matching template's inputs_required

    # Computed outputs
    outputs = Column(JSON, nullable=True)
    # {output_name: value, ...} from template computation
    wis_score = Column(Float, nullable=True)
    # Wellbeing Impact Score (0-100) converted from template output
    wis_confidence = Column(Float, nullable=True)
    # Confidence interval half-width

    # Interaction adjustments
    interaction_adjustments = Column(JSON, nullable=True)
    # [{with_template: str, adjustment_type: str, factor: float}, ...]

    # Relationships
    evaluation = relationship("CMREvaluation", back_populates="template_activations")


class CMRDomainScore(Base):
    """Aggregated domain-level scores."""

    __tablename__ = "cmr_domain_scores"

    id = Column(Integer, primary_key=True)
    evaluation_id = Column(Integer, ForeignKey("cmr_evaluations.id"))
    domain = Column(String, nullable=False)
    # "A1" through "A10"

    wis_score = Column(Float, nullable=False)
    wis_confidence = Column(Float, nullable=False)
    n_templates_activated = Column(Integer, nullable=False)
    template_ids = Column(String)  # Comma-separated

    # Aggregation details
    aggregation_method = Column(String, default="weighted_average")
    weight_basis = Column(String, default="calibration_confidence")

    # Relationships
    evaluation = relationship("CMREvaluation", back_populates="domain_scores")


class CMROverallScore(Base):
    """Overall assessment score."""

    __tablename__ = "cmr_overall_scores"

    id = Column(Integer, primary_key=True)
    evaluation_id = Column(Integer, ForeignKey("cmr_evaluations.id"))

    wis_geometric_mean = Column(Float, nullable=False)
    wis_confidence = Column(Float, nullable=False)
    n_domains_assessed = Column(Integer, nullable=False)

    # Flags
    severe_deficit_domains = Column(String, nullable=True)
    # Domains with WIS < 30
    data_gaps = Column(String, nullable=True)
    # Domains with insufficient input data

    # Relationships
    evaluation = relationship("CMREvaluation", back_populates="overall_scores")


class ReductionClaim(Base):
    """Maps a Tier 2 theory construct to Tier 1 template mechanisms."""

    __tablename__ = "reduction_claims"

    id = Column(Integer, primary_key=True)

    # The Tier 2 construct being reduced
    tier2_theory = Column(String, nullable=False)
    # e.g. "ART", "SRT", "Biophilia"
    tier2_construct = Column(String, nullable=False)
    # e.g. "Soft Fascination", "Prospect", "Being Away"

    # The reduction
    reduction_type = Column(String, nullable=False)
    # "full" | "partial" | "irreducible_residual"
    template_mappings = Column(JSON, nullable=False)
    # [{template_id: str, mechanism: str, coverage: float}, ...]
    # coverage: 0-1, how much of the construct this template explains

    irreducible_residual = Column(Text, nullable=True)
    # What cannot be reduced to template mechanisms

    confidence = Column(String, nullable=False)
    # "high" | "moderate" | "low"
    source_panel = Column(String, nullable=True)
    # e.g. "T2-A" for ART reduction panel

    # Staging link reconciliation
    staging_links_reconciled = Column(Integer, default=0)
    staging_links_total = Column(Integer, default=0)


class CMRStagingTheoryLink(Base):
    """Staging table for template-level theory links extracted from causal links."""

    __tablename__ = "cmr_staging_theory_links"

    id = Column(Integer, primary_key=True)
    template_display_id = Column(String, nullable=False)
    template_id = Column(String, nullable=False)
    theory_id = Column(String, nullable=False)
    link_index = Column(Integer, nullable=False)

    from_variable = Column(String, nullable=True)
    to_variable = Column(String, nullable=True)
    from_level = Column(String, nullable=True)
    to_level = Column(String, nullable=True)
    activity = Column(String, nullable=True)
    maturity = Column(String, nullable=True)
    source_json_path = Column(String, nullable=False)
    loaded_at = Column(DateTime, default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "template_display_id",
            "theory_id",
            "link_index",
            name="uq_cmr_staging_theory_link",
        ),
    )


class PaperRecord(Base):
    """History record for processed paper evaluations."""

    __tablename__ = "cmr_paper_records"

    id = Column(Integer, primary_key=True)
    citation = Column(Text, nullable=True)
    doi = Column(String, nullable=True)
    evaluated_at = Column(DateTime, default=func.now(), nullable=False)

    n_claims = Column(Integer, nullable=False, default=0)
    n_matched = Column(Integer, nullable=False, default=0)
    n_unmatched = Column(Integer, nullable=False, default=0)
    n_contradictions = Column(Integer, nullable=False, default=0)
    n_confirmations = Column(Integer, nullable=False, default=0)
    n_gaps = Column(Integer, nullable=False, default=0)
    aggregate_voi = Column(Float, nullable=False, default=0.0)
    proposals_generated = Column(Integer, nullable=False, default=0)

    # Denormalized list for quick template-to-paper lookup.
    matched_template_ids = Column(JSON, nullable=False, default=list)


def get_engine(db_path: str = "ae.db"):
    """Create SQLAlchemy engine for the Article Eater database."""
    return create_engine(f"sqlite:///{db_path}", echo=False)


def get_session(db_path: str = "ae.db"):
    """Create a new database session."""
    engine = get_engine(db_path)
    Session = sessionmaker(bind=engine)
    return Session()


def create_tables(db_path: str = "ae.db"):
    """Create all CMR tables in the database."""
    engine = get_engine(db_path)
    Base.metadata.create_all(engine)


__all__ = [
    "Base",
    "TemplateRecord",
    "CMREvaluation",
    "CMRTemplateActivation",
    "CMRDomainScore",
    "CMROverallScore",
    "ReductionClaim",
    "CMRStagingTheoryLink",
    "PaperRecord",
    "get_engine",
    "get_session",
    "create_tables",
]
