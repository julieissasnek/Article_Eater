from pydantic import BaseModel, Field
from typing import Optional, List

class Stats(BaseModel):
    p_value: Optional[float] = None
    effect_size: Optional[float] = None
    effect_size_type: Optional[str] = None
    sample_size: Optional[int] = None
    ci_lower: Optional[float] = None
    ci_upper: Optional[float] = None

class SevenPanelItem(BaseModel):
    finding_text: str
    statistics: Stats
    quote: str
    page_span: str
    raw_abstract: Optional[str] = Field(None, description="The raw abstract text.")

class SevenPanelArtifact(BaseModel):
    items: List[SevenPanelItem] = Field(default_factory=list)
    provider: Optional[str] = None
    model: Optional[str] = None
    cost_usd: Optional[float] = None

class SubjectTrait(BaseModel):
    name: str
    scale: Optional[str] = None
    used_as_moderator: bool = False


class SubjectDemographics(BaseModel):
    age_mean: Optional[float] = None
    age_sd: Optional[float] = None
    age_range: Optional[str] = None
    age_band: Optional[str] = None
    sex_gender_distribution: Optional[dict] = None
    education_band: Optional[str] = None
    sample_size: Optional[int] = None


class SubjectCulture(BaseModel):
    countries: Optional[List[str]] = None
    region: Optional[str] = None
    self_construal_profile: Optional[str] = None


class SubjectClinicalStatus(BaseModel):
    population: Optional[str] = None
    key_inclusions: Optional[List[str]] = None
    key_exclusions: Optional[List[str]] = None


class SubjectScope(BaseModel):
    demographics: Optional[SubjectDemographics] = None
    culture: Optional[SubjectCulture] = None
    clinical_status: Optional[SubjectClinicalStatus] = None
    traits_measured: Optional[List[SubjectTrait]] = None
    notes: Optional[str] = None


class PanelSubjects(BaseModel):
    type: str = "panel_subjects"
    paper_id: str
    sample: SubjectScope
    traits_measured: Optional[List[SubjectTrait]] = None
    notes: Optional[str] = None


class PanelTask(BaseModel):
    task_id: str
    name: str
    activity_type: Optional[str] = None
    duration_min: Optional[float] = None
    setting: Optional[str] = None
    environment_type: Optional[str] = None
    relevance_tags: Optional[List[str]] = None
    notes: Optional[str] = None


class PanelContext(BaseModel):
    type: str = "panel_context"
    paper_id: str
    tasks: List[PanelTask]
    global_notes: Optional[str] = None


class Indicator(BaseModel):
    indicator_id: str
    name: str
    modality: Optional[str] = None
    instrument: Optional[str] = None
    timescale: Optional[str] = None
    interpretation: Optional[List[str]] = None
    notes: Optional[str] = None


class ConstructMapping(BaseModel):
    construct: str
    indicator_ids: List[str]
    notes: Optional[str] = None


class PanelMeasures(BaseModel):
    type: str = "panel_measures"
    paper_id: str
    indicators: Optional[List[Indicator]] = None
    construct_mappings: Optional[List[ConstructMapping]] = None
    notes: Optional[str] = None


class FindingV2(BaseModel):
    finding_id: str
    finding_text: str
    statistics: Optional[Stats] = None
    quote: Optional[str] = None
    page_span: Optional[str] = None
    task_id: Optional[str] = None
    indicator_ids: Optional[List[str]] = None
    raw_abstract: Optional[str] = None


class PanelFindingsV2(BaseModel):
    type: str = "panel_findings"
    paper_id: str
    items: List[FindingV2]


class ModerationPattern(BaseModel):
    finding_id: str
    moderator: str
    dimension: str
    levels_compared: Optional[List[str]] = None
    pattern: str
    stats_summary: Optional[str] = None
    evidence_snippet: Optional[str] = None
    section: Optional[str] = None


class PanelHeterogeneity(BaseModel):
    type: str = "panel_heterogeneity"
    paper_id: str
    moderation_patterns: Optional[List[ModerationPattern]] = None


class MechanismClaim(BaseModel):
    claim_id: str
    claim_text: str
    theory: Optional[str] = None
    phenomenon: Optional[str] = None
    role: Optional[str] = None
    strength: Optional[str] = None
    evidence_snippet: Optional[str] = None
    page_span: Optional[str] = None


class PanelMechanisms(BaseModel):
    type: str = "panel_mechanisms"
    paper_id: str
    mechanism_claims: Optional[List[MechanismClaim]] = None


class PanelLimits(BaseModel):
    type: str = "panel_limits"
    paper_id: str
    generalization_notes: Optional[List[str]] = None
    threats_to_validity: Optional[List[str]] = None
    future_work_notes: Optional[List[str]] = None

class SevenPanelV2Bundle(BaseModel):
    """Container for Seven-Panel v2 panels.

    This keeps the v2 staging payload together for downstream consumers
    (RuleGraph v2 builder, BN exporter, RAG), while leaving the classic
    SevenPanelArtifact API unchanged.
    """
    subjects: Optional[PanelSubjects] = None
    context: Optional[PanelContext] = None
    measures: Optional[PanelMeasures] = None
    findings: Optional[PanelFindingsV2] = None
    heterogeneity: Optional[PanelHeterogeneity] = None
    mechanisms: Optional[PanelMechanisms] = None
    limits: Optional[PanelLimits] = None

    provider: Optional[str] = None
    model: Optional[str] = None
    cost_usd: Optional[float] = None

