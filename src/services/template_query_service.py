"""
Template Query Service — Mechanistic Reasoning from Template Library
=====================================================================

Created: 2026-02-16
Purpose: Answer architectural design questions using template knowledge

ARCHITECTURAL REASONING: WHY TEMPLATES + ARTICLES + BN?
--------------------------------------------------------

The system has THREE knowledge representations, each serving a distinct purpose:

1. TEMPLATES (this service queries)
   - Encode MECHANISTIC VOCABULARY — the causal pathways that explain WHY
   - Distilled scientific consensus about mechanisms
   - Provide: causal_links (HOW), higher_order_principle (WHY),
              scope_conditions (WHEN), moderators (FOR WHOM)
   - Stable, curated, theory-grounded

2. ARTICLE NETWORK (WebOfBelief, extracted claims)
   - Encode EMPIRICAL EVIDENCE — specific findings from specific studies
   - Individual effect sizes, sample populations, methodological details
   - Provide: grounding for templates, specific numbers, replication status
   - Dynamic, grows as papers are processed

3. BAYESIAN NETWORK (BN integration)
   - Encode CONFIDENCE CALIBRATION — posterior beliefs given evidence
   - Integrates multiple sources, handles contradictions, computes uncertainty
   - Provide: calibrated confidence intervals, sensitivity to new evidence
   - Computational, updates with new claims

A COMPLETE ANSWER requires all three:
- Templates tell you WHAT MECHANISM is operating and WHY it works
- Articles tell you WHAT EVIDENCE supports it and HOW STRONG
- BN tells you HOW CONFIDENT you should be given ALL evidence

This service starts with templates because they provide the CONCEPTUAL STRUCTURE
that makes answers interpretable. "High ceilings increase creativity" is not
useful without knowing WHY (reduced enclosure-threat → broadened cognition)
and WHEN (creative tasks, not detail-oriented tasks).

Future integration should:
1. Query templates for mechanistic framework
2. Ground template claims in extracted article evidence
3. Pull BN posteriors for confidence calibration
4. Synthesize into coherent, evidence-grounded answer
"""

import json
import re
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from collections import defaultdict
from enum import Enum

logger = logging.getLogger(__name__)


@dataclass
class CausalPathway:
    """A single causal link from a template."""
    from_entity: str
    activity: str
    to_entity: str
    change_produced: str
    level: str
    bridging_to: str
    bridging_quality: str
    maturity: str
    evidence_base: str


@dataclass
class TemplateAnswer:
    """Structured answer from a single template."""
    template_id: str
    display_id: str
    name: str
    relevance_score: float

    # The core answer components
    how: List[CausalPathway]  # Mechanistic pathway
    why: str  # Higher-order principle
    when: List[str]  # Scope conditions
    for_whom: List[str]  # Moderators (individual/population differences)

    # Evidence and confidence
    maturity: str
    key_references: List[str]
    confidence: float  # Derived from maturity


@dataclass
class NeuroscienceDetail:
    """Deep neuroscience explanation for a causal link."""
    link_summary: str
    neural_substrate: str
    level_transition: str  # e.g., "environmental → neural"
    mechanism_detail: str
    evidence_base: str
    maturity: str
    research_needed: str


@dataclass
class ResearchGap:
    """A specific research gap that needs to be filled."""
    gap_type: str  # 'weak_link', 'missing_moderator', 'untested_boundary', 'replication_needed'
    description: str
    current_evidence: str
    proposed_study: str
    priority: str  # 'critical', 'high', 'medium', 'low'
    template_source: str


@dataclass
class RelatedTemplate:
    """A template related via interactions."""
    display_id: str
    name: str
    relationship: str  # How it relates to the main template
    relevance: str  # Why it matters for this query


@dataclass
class QueryResponse:
    """Complete response to a design question."""
    query: str
    headline: str

    # Multi-dimensional answer
    how: str  # Synthesized mechanism
    why: str  # Synthesized principle
    when: List[str]  # Aggregated conditions
    for_whom: List[str]  # Aggregated moderators

    # Supporting details
    relevant_templates: List[TemplateAnswer]
    causal_chain: str  # Human-readable pathway

    # Confidence and evidence
    overall_confidence: float
    maturity_distribution: Dict[str, int]
    key_evidence: List[str]

    # Level 3: Related templates
    related_templates: List[RelatedTemplate] = field(default_factory=list)

    # Level 4: Neuroscience depth
    neuroscience_details: List[NeuroscienceDetail] = field(default_factory=list)

    # Level 5: Research gaps
    research_gaps_detailed: List[ResearchGap] = field(default_factory=list)

    # Legacy fields
    caveats: List[str] = field(default_factory=list)
    research_gaps: List[str] = field(default_factory=list)  # Simple string version


class UserPersona(Enum):
    """User personas with different information needs."""
    ARCHITECT = "architect"           # Needs: design recommendations, thresholds, spatial implications
    RESEARCHER = "researcher"         # Needs: evidence quality, gaps, proposed studies, effect sizes
    FACILITIES = "facilities"         # Needs: practical changes, cost-benefit, implementation
    STUDENT = "student"               # Needs: clear explanations, principles, examples
    POLICY = "policy"                 # Needs: population-level effects, cost-effectiveness, standards
    CLINICIAN = "clinician"           # Needs: patient populations, therapeutic applications, contraindications


# Persona-specific question types
PERSONA_QUESTIONS = {
    UserPersona.ARCHITECT: [
        "How should I design...",
        "What dimensions/proportions...",
        "What materials should...",
        "How do I balance...",
    ],
    UserPersona.RESEARCHER: [
        "What is the evidence for...",
        "What studies support...",
        "What are the effect sizes...",
        "What research is needed...",
    ],
    UserPersona.FACILITIES: [
        "Will changing X improve...",
        "Is it worth investing in...",
        "What's the ROI of...",
        "How quickly will we see...",
    ],
    UserPersona.STUDENT: [
        "Why does X affect...",
        "How does X work...",
        "What is the mechanism...",
        "Can you explain...",
    ],
    UserPersona.POLICY: [
        "What are the population effects...",
        "Should we mandate...",
        "What standards should...",
        "What's the cost-benefit...",
    ],
    UserPersona.CLINICIAN: [
        "Which patients benefit from...",
        "Are there contraindications...",
        "What's the therapeutic dose...",
        "How does this interact with...",
    ],
}


class TemplateQueryService:
    """
    Query templates to answer architectural design questions.

    Provides mechanistic answers with:
    - HOW: Causal pathway from environment to outcome
    - WHY: Higher-order principle explaining the mechanism
    - WHEN: Scope conditions (contexts where effect applies)
    - FOR WHOM: Moderators (individual/population differences)

    Supports different user personas with customized answers:
    - ARCHITECT: Design recommendations, thresholds, spatial implications
    - RESEARCHER: Evidence quality, gaps, proposed studies
    - FACILITIES: Practical changes, ROI, implementation
    - STUDENT: Clear explanations, principles, examples
    - POLICY: Population effects, standards, cost-benefit
    - CLINICIAN: Patient populations, therapeutic applications
    """

    # Maturity → confidence mapping
    MATURITY_CONFIDENCE = {
        'established': 0.85,
        'supported': 0.70,
        'how-actually': 0.65,
        'how-plausibly': 0.50,
        'preliminary': 0.40,
        'how-possibly': 0.35,
        'speculative': 0.25
    }

    # Persona → emphasis mapping
    PERSONA_EMPHASIS = {
        UserPersona.ARCHITECT: {
            'primary': ['when', 'how'],  # Design conditions and mechanism
            'secondary': ['for_whom'],
            'include_thresholds': True,
            'include_neuroscience': False,
            'include_research_gaps': False,
            'vocabulary': 'design',
        },
        UserPersona.RESEARCHER: {
            'primary': ['neuroscience', 'research_gaps'],
            'secondary': ['how', 'why'],
            'include_thresholds': True,
            'include_neuroscience': True,
            'include_research_gaps': True,
            'vocabulary': 'scientific',
        },
        UserPersona.FACILITIES: {
            'primary': ['when', 'for_whom'],
            'secondary': ['how'],
            'include_thresholds': True,
            'include_neuroscience': False,
            'include_research_gaps': False,
            'vocabulary': 'practical',
        },
        UserPersona.STUDENT: {
            'primary': ['why', 'how'],
            'secondary': ['when'],
            'include_thresholds': False,
            'include_neuroscience': True,  # Educational
            'include_research_gaps': False,
            'vocabulary': 'educational',
        },
        UserPersona.POLICY: {
            'primary': ['for_whom', 'when'],
            'secondary': ['why'],
            'include_thresholds': True,
            'include_neuroscience': False,
            'include_research_gaps': True,  # For evidence-based policy
            'vocabulary': 'policy',
        },
        UserPersona.CLINICIAN: {
            'primary': ['for_whom', 'when'],
            'secondary': ['how', 'neuroscience'],
            'include_thresholds': True,
            'include_neuroscience': True,
            'include_research_gaps': True,
            'vocabulary': 'clinical',
        },
    }

    def __init__(self, templates_dir: str = "data/templates", annotation_service=None):
        self.templates_dir = Path(templates_dir)
        self.templates: Dict[str, Dict] = {}
        self.templates_by_id: Dict[str, Dict] = {}
        self.display_id_map: Dict[str, str] = {}  # display_id → template_id
        self.annotation_service = annotation_service  # Optional AnnotationService for EN-0D
        self._load_templates()

    def _load_templates(self):
        """Load all templates from disk."""
        if not self.templates_dir.exists():
            logger.warning(f"Templates directory not found: {self.templates_dir}")
            return

        for f in self.templates_dir.glob("*.json"):
            try:
                with open(f) as fp:
                    t = json.load(fp)
                    tid = t.get('template_id', f.stem)
                    did = t.get('display_id', '')
                    self.templates_by_id[tid] = t
                    self.templates[tid] = t
                    if did:
                        self.display_id_map[did] = tid
                        self.templates[did] = t  # Also index by display_id
            except Exception as e:
                logger.warning(f"Failed to load {f}: {e}")

        logger.info(f"Loaded {len(self.templates)} templates")

    def _normalize_text_field(self, value: Any, default: str = "?") -> str:
        if value is None:
            return default
        text = str(value).strip()
        return text if text else default

    def _first_present(self, mapping: Dict[str, Any], keys: List[str], default: str = "?") -> str:
        for key in keys:
            if key in mapping:
                text = self._normalize_text_field(mapping.get(key), default="")
                if text:
                    return text
        return default

    def _resolve_template(self, ref_id: str, templates: Dict[str, Dict]) -> Dict:
        """Resolve template by display_id or template_id across mixed template maps."""
        if ref_id in templates and isinstance(templates[ref_id], dict):
            return templates[ref_id]

        tid = self.display_id_map.get(ref_id)
        if tid and tid in templates and isinstance(templates[tid], dict):
            return templates[tid]

        for template in templates.values():
            if not isinstance(template, dict):
                continue
            if template.get('display_id') == ref_id or template.get('template_id') == ref_id:
                return template
        return {}

    def _compute_relevance(self, template: Dict, keywords: List[str]) -> float:
        """
        Compute relevance score for a template given query keywords.

        Simple keyword matching for now — should be replaced with
        semantic embeddings for production use.
        """
        causal_terms = []
        for link in template.get('causal_links', []):
            if not isinstance(link, dict):
                continue
            for key in (
                'from_entity',
                'to_entity',
                'from_variable',
                'to_variable',
                'activity',
                'from_level',
                'to_level',
            ):
                value = link.get(key)
                if value:
                    causal_terms.append(str(value))

        searchable = ' '.join([
            str(template.get('name', '')),
            str(template.get('display_id', '')),
            str(template.get('template_id', '')),
            str(template.get('structural_pattern', '')),
            str(template.get('higher_order_principle', '')),
            str(template.get('short_description', '')),
            ' '.join(template.get('framework_ids', []) if isinstance(template.get('framework_ids'), list) else []),
            ' '.join(causal_terms),
            ' '.join(template.get('scope_conditions', []) if isinstance(template.get('scope_conditions'), list) else []),
            ' '.join(template.get('moderators', []) if isinstance(template.get('moderators'), list) else []),
        ]).lower()

        searchable_tokens = set(re.findall(r'\b[\w\-]+\b', searchable))

        # Count keyword matches
        matches = 0.0
        for kw in keywords:
            kw_lower = kw.lower()
            if kw_lower in searchable_tokens:
                matches += 1.0
            elif kw_lower in searchable:
                matches += 0.5

        # Bonus for title/name matches
        name = template.get('name', '').lower()
        name_tokens = set(re.findall(r'\b[\w\-]+\b', name))
        name_matches = 0.0
        for kw in keywords:
            kw_lower = kw.lower()
            if kw_lower in name_tokens:
                name_matches += 2.0
            elif kw_lower in name:
                name_matches += 1.0

        return (matches + name_matches) / max(len(keywords), 1)

    def _extract_causal_pathway(self, template: Dict) -> List[CausalPathway]:
        """Extract causal links as structured pathways."""
        pathways = []
        for link in template.get('causal_links', []):
            if not isinstance(link, dict):
                continue
            from_entity = self._first_present(
                link,
                ['from_entity', 'from_variable', 'source', 'from', 'input'],
            )
            to_entity = self._first_present(
                link,
                ['to_entity', 'to_variable', 'target', 'to', 'output'],
            )
            activity = self._first_present(
                link,
                ['activity', 'relationship', 'relation', 'mechanism'],
                default='influences',
            )
            from_level = self._first_present(
                link,
                ['from_level', 'level', 'source_level'],
            )
            to_level = self._first_present(
                link,
                ['to_level', 'target_level', 'bridging_to'],
            )
            bridging_quality = self._first_present(
                link,
                ['bridging_quality', 'bridge_quality', 'bridging_to', 'bridging_strength'],
            )
            maturity = self._first_present(link, ['maturity', 'status'], default='unknown')
            evidence_base = self._first_present(
                link,
                ['evidence_base', 'key_evidence', 'notes', 'description'],
                default='',
            )
            change_produced = self._first_present(
                link,
                ['change_produced', 'notes', 'expected_change'],
                default='',
            )
            pathways.append(CausalPathway(
                from_entity=from_entity,
                activity=activity,
                to_entity=to_entity,
                change_produced=change_produced,
                level=from_level,
                bridging_to=to_level,
                bridging_quality=bridging_quality,
                maturity=maturity,
                evidence_base=evidence_base[:200],
            ))
        return pathways

    def _extract_scope_conditions(self, template: Dict) -> List[str]:
        """Extract scope conditions (WHEN the effect applies)."""
        scope = template.get('scope_conditions', [])
        if isinstance(scope, list):
            return [str(s) for s in scope]
        return []

    def _extract_moderators(self, template: Dict) -> List[str]:
        """Extract moderators (FOR WHOM / individual differences)."""
        mods = template.get('moderators', [])
        if isinstance(mods, list):
            return [str(m) for m in mods]
        return []

    def _extract_references(self, template: Dict) -> List[str]:
        """Extract key references as citation strings."""
        refs = []
        for ref in template.get('key_references', []):
            if isinstance(ref, dict):
                refs.append(ref.get('citation', str(ref))[:150])
            else:
                refs.append(str(ref)[:150])
        return refs

    def _get_confidence(self, template: Dict) -> float:
        """Convert maturity rating to confidence score."""
        maturity = template.get('maturity', template.get('overall_maturity', 'preliminary'))
        return self.MATURITY_CONFIDENCE.get(maturity, 0.40)

    def _build_template_answer(self, template: Dict, relevance: float) -> TemplateAnswer:
        """Build a structured answer from a single template."""
        return TemplateAnswer(
            template_id=template.get('template_id', '?'),
            display_id=template.get('display_id', '?'),
            name=template.get('name', '?'),
            relevance_score=relevance,
            how=self._extract_causal_pathway(template),
            why=template.get('higher_order_principle', template.get('structural_pattern', '')),
            when=self._extract_scope_conditions(template),
            for_whom=self._extract_moderators(template),
            maturity=template.get('maturity', template.get('overall_maturity', '?')),
            key_references=self._extract_references(template),
            confidence=self._get_confidence(template)
        )

    def _synthesize_causal_chain(self, answers: List[TemplateAnswer]) -> str:
        """Build human-readable causal chain from top answer."""
        if not answers or not answers[0].how:
            return "No causal pathway identified"

        chain_parts = []
        for pathway in answers[0].how:
            chain_parts.append(
                f"{pathway.from_entity} --[{pathway.activity}]--> {pathway.to_entity}"
            )
        return " → ".join(chain_parts) if len(chain_parts) <= 3 else \
               " → ".join(chain_parts[:2]) + f" → ... → {answers[0].how[-1].to_entity}"

    def _synthesize_how(self, answers: List[TemplateAnswer]) -> str:
        """Synthesize HOW explanation from top answers."""
        if not answers:
            return "Mechanism unknown"

        top = answers[0]
        if top.how:
            # Build narrative from causal links
            parts = []
            for p in top.how[:3]:
                parts.append(f"{p.from_entity} {p.activity} {p.to_entity}")
            return ". ".join(parts) + "."
        return "Mechanism not specified in template"

    def _synthesize_why(self, answers: List[TemplateAnswer]) -> str:
        """Synthesize WHY explanation from higher-order principles."""
        if not answers:
            return "Principle unknown"

        # Use the top answer's principle, truncate if needed
        why = answers[0].why
        if len(why) > 300:
            why = why[:297] + "..."
        return why

    def _aggregate_when(self, answers: List[TemplateAnswer]) -> List[str]:
        """Aggregate scope conditions across relevant templates."""
        all_when = []
        seen = set()
        for ans in answers[:3]:  # Top 3 templates
            for condition in ans.when:
                # Deduplicate similar conditions
                key = condition[:50].lower()
                if key not in seen:
                    seen.add(key)
                    all_when.append(condition)
        return all_when[:8]  # Limit to 8 conditions

    def _aggregate_for_whom(self, answers: List[TemplateAnswer]) -> List[str]:
        """Aggregate moderators across relevant templates."""
        all_whom = []
        seen = set()
        for ans in answers[:3]:
            for mod in ans.for_whom:
                key = mod[:50].lower()
                if key not in seen:
                    seen.add(key)
                    all_whom.append(mod)
        return all_whom[:8]

    def _compute_overall_confidence(self, answers: List[TemplateAnswer]) -> float:
        """Compute weighted confidence from relevant templates."""
        if not answers:
            return 0.0

        # Weight by relevance score
        total_weight = sum(a.relevance_score for a in answers)
        if total_weight == 0:
            return answers[0].confidence

        weighted_conf = sum(a.confidence * a.relevance_score for a in answers)
        return weighted_conf / total_weight

    def _identify_research_gaps(self, answers: List[TemplateAnswer]) -> List[str]:
        """Identify gaps where more research is needed (simple version)."""
        gaps = []

        for ans in answers[:3]:
            # Low maturity = research gap
            if ans.maturity in ['preliminary', 'how-possibly', 'speculative']:
                gaps.append(f"{ans.display_id}: Mechanism is {ans.maturity} — needs empirical validation")

            # Check for weak bridging in causal links
            for pathway in ans.how:
                if pathway.bridging_quality.lower() in ['weak', 'speculative']:
                    gaps.append(f"{ans.display_id}: {pathway.from_entity} → {pathway.to_entity} bridging is weak")

        return list(set(gaps))[:5]

    def _extract_neuroscience_details(self, answers: List[TemplateAnswer]) -> List[NeuroscienceDetail]:
        """
        Extract deep neuroscience explanations from causal links.

        Focuses on neural/circuit/cellular level mechanisms.
        """
        details = []
        neural_levels = {'neural', 'circuit', 'cellular', 'subcortical', 'neuroendocrine', 'molecular'}

        for ans in answers[:3]:
            for pathway in ans.how:
                # Check if this link involves neural mechanisms
                from_level = pathway.level.lower() if pathway.level else ''
                to_level = pathway.bridging_to.lower() if pathway.bridging_to else ''

                involves_neural = (
                    from_level in neural_levels or
                    to_level in neural_levels or
                    'amygdala' in pathway.from_entity.lower() or
                    'hippocamp' in pathway.from_entity.lower() or
                    'cortex' in pathway.from_entity.lower() or
                    'cortisol' in pathway.to_entity.lower() or
                    'dopamine' in str(pathway.evidence_base).lower()
                )

                if involves_neural or pathway.evidence_base:
                    # Determine what research is needed based on maturity
                    if pathway.maturity in ['preliminary', 'how-possibly']:
                        research_needed = f"Direct neuroimaging study needed to confirm {pathway.from_entity} → {pathway.to_entity} pathway"
                    elif pathway.maturity == 'supported':
                        research_needed = f"Replication with larger N and diverse populations needed"
                    elif pathway.bridging_quality.lower() in ['weak', 'moderate']:
                        research_needed = (
                            f"Mechanism linking {pathway.level} to {pathway.bridging_to} "
                            "level needs elucidation"
                        )
                    else:
                        research_needed = "Well-established; focus on boundary conditions"

                    details.append(NeuroscienceDetail(
                        link_summary=f"{pathway.from_entity} → {pathway.to_entity}",
                        neural_substrate=self._infer_neural_substrate(pathway),
                        level_transition=f"{pathway.level} → {pathway.bridging_to}",
                        mechanism_detail=pathway.evidence_base[:300] if pathway.evidence_base else "Not specified",
                        evidence_base=pathway.evidence_base[:200] if pathway.evidence_base else "",
                        maturity=pathway.maturity,
                        research_needed=research_needed
                    ))

        return details[:8]  # Limit to 8 details

    def _infer_neural_substrate(self, pathway: CausalPathway) -> str:
        """Infer the neural substrate from pathway entities and evidence."""
        text = f"{pathway.from_entity} {pathway.to_entity} {pathway.evidence_base}".lower()

        substrates = []
        if 'amygdala' in text:
            substrates.append("amygdala (threat/salience)")
        if 'hippocamp' in text:
            substrates.append("hippocampus (spatial/memory)")
        if 'prefrontal' in text or 'pfc' in text:
            substrates.append("prefrontal cortex (executive)")
        if 'insula' in text:
            substrates.append("insula (interoception)")
        if 'cortisol' in text or 'hpa' in text:
            substrates.append("HPA axis (stress)")
        if 'dopamine' in text:
            substrates.append("dopaminergic system (reward)")
        if 'vagal' in text or 'parasympathetic' in text:
            substrates.append("vagal/parasympathetic (restoration)")
        if 'place cell' in text or 'grid cell' in text:
            substrates.append("hippocampal place/grid cells (navigation)")
        if 'default mode' in text or 'dmn' in text:
            substrates.append("default mode network (internal focus)")

        return "; ".join(substrates) if substrates else "Not specified"

    def _extract_detailed_research_gaps(self, answers: List[TemplateAnswer], templates: Dict) -> List[ResearchGap]:
        """
        Extract detailed research gaps with proposed studies.
        """
        gaps = []

        for ans in answers[:3]:
            template = self._resolve_template(ans.display_id, templates)

            # Gap Type 1: Weak causal links
            for pathway in ans.how:
                if pathway.maturity in ['preliminary', 'how-possibly', 'speculative']:
                    gaps.append(ResearchGap(
                        gap_type='weak_link',
                        description=f"The link from {pathway.from_entity} to {pathway.to_entity} is {pathway.maturity}",
                        current_evidence=pathway.evidence_base[:150] if pathway.evidence_base else "Limited",
                        proposed_study=self._propose_study_for_link(pathway),
                        priority='high' if pathway.maturity == 'preliminary' else 'critical',
                        template_source=ans.display_id
                    ))
                elif pathway.bridging_quality.lower() in ['weak']:
                    gaps.append(ResearchGap(
                        gap_type='weak_link',
                        description=(
                            f"Bridging from {pathway.level} to {pathway.bridging_to} "
                            "level is weak"
                        ),
                        current_evidence=pathway.evidence_base[:150] if pathway.evidence_base else "Limited",
                        proposed_study=f"Multi-level study measuring both {pathway.level} and {pathway.bridging_to} outcomes simultaneously",
                        priority='high',
                        template_source=ans.display_id
                    ))

            # Gap Type 2: Missing moderator data
            calibration = template.get('calibration_parameters', {})
            if not calibration:
                gaps.append(ResearchGap(
                    gap_type='missing_moderator',
                    description=f"No calibration parameters for {ans.display_id}",
                    current_evidence="Qualitative moderators listed but no quantitative thresholds",
                    proposed_study="Dose-response study varying key parameters to establish thresholds",
                    priority='medium',
                    template_source=ans.display_id
                ))

            # Gap Type 3: Untested scope boundaries
            scope = template.get('scope_conditions', [])
            for condition in scope:
                if 'may' in condition.lower() or 'might' in condition.lower() or 'unclear' in condition.lower():
                    gaps.append(ResearchGap(
                        gap_type='untested_boundary',
                        description=f"Scope boundary uncertain: {condition[:100]}",
                        current_evidence="Theoretical prediction, not empirically tested",
                        proposed_study="Boundary condition experiment testing inside vs outside proposed scope",
                        priority='medium',
                        template_source=ans.display_id
                    ))

            # Gap Type 4: Cross-cultural replication
            mods = template.get('moderators', [])
            has_cultural = any('cultur' in str(m).lower() for m in mods)
            if has_cultural:
                gaps.append(ResearchGap(
                    gap_type='replication_needed',
                    description=f"Cultural moderation identified but cross-cultural replication lacking",
                    current_evidence="Most studies from Western, educated, industrialized populations",
                    proposed_study="Replicate core findings in East Asian, Middle Eastern, and Global South populations",
                    priority='medium',
                    template_source=ans.display_id
                ))

        # Deduplicate by description
        seen = set()
        unique_gaps = []
        for gap in gaps:
            key = gap.description[:50]
            if key not in seen:
                seen.add(key)
                unique_gaps.append(gap)

        return unique_gaps[:10]

    def _propose_study_for_link(self, pathway: CausalPathway) -> str:
        """Generate a proposed study design for a weak causal link."""
        from_e = pathway.from_entity
        to_e = pathway.to_entity

        # Detect study type based on level
        level = pathway.level.lower() if pathway.level else ''
        bridging = pathway.bridging_to.lower() if pathway.bridging_to else ''

        if 'neural' in level or 'neural' in bridging:
            return f"fMRI/EEG study: Manipulate {from_e}, measure {to_e} neural correlates. N≥30, within-subjects design."
        elif 'physiological' in level or 'physiological' in bridging:
            return f"Psychophysiology study: Manipulate {from_e}, measure {to_e} via HRV/cortisol/EDA. N≥50, randomized."
        elif 'behavioral' in level or 'behavioral' in bridging:
            return f"Behavioral experiment: Manipulate {from_e}, measure {to_e} behavioral outcomes. N≥100, between-subjects."
        elif 'environmental' in level:
            return f"Field study: Compare environments varying in {from_e}, measure {to_e}. N≥200, quasi-experimental with controls."
        else:
            return f"Controlled experiment: Systematically vary {from_e}, measure effect on {to_e}. Pre-register hypothesis."

    def _extract_related_templates(self, answers: List[TemplateAnswer], templates: Dict) -> List[RelatedTemplate]:
        """Extract related templates via interactions field."""
        related = []
        seen = set()

        for ans in answers[:3]:
            template = self._resolve_template(ans.display_id, templates)
            interactions = template.get('interactions', [])

            for ix in interactions:
                if isinstance(ix, dict):
                    ref_id = ix.get('display_id') or ix.get('template_id', '')
                    nature = ix.get('nature', '')
                elif isinstance(ix, str):
                    # Parse string format like "TEMPLATE_ID (T12)"
                    if '(' in ix:
                        ref_id = ix.split('(')[1].replace(')', '').strip()
                        nature = ix.split('(')[0].strip()
                    else:
                        ref_id = ix
                        nature = ""
                else:
                    continue

                if ref_id and ref_id not in seen:
                    seen.add(ref_id)
                    ref_template = self._resolve_template(ref_id, templates)
                    if ref_template:
                        related.append(RelatedTemplate(
                            display_id=ref_template.get('display_id', ref_id),
                            name=ref_template.get('name', '?')[:60],
                            relationship=nature[:150] if nature else "Related mechanism",
                            relevance=self._explain_relevance(ans.display_id, ref_id, nature)
                        ))

        return related[:8]

    def _explain_relevance(self, source_id: str, ref_id: str, nature: str) -> str:
        """Explain why a related template is relevant to the query."""
        if 'prerequisite' in nature.lower() or 'precursor' in nature.lower():
            return f"{ref_id} must occur before {source_id} mechanism activates"
        elif 'modulates' in nature.lower() or 'moderates' in nature.lower():
            return f"{ref_id} changes the strength/direction of {source_id} effect"
        elif 'opposite' in nature.lower() or 'antagonist' in nature.lower():
            return f"{ref_id} produces opposing effect — important for balance"
        elif 'parallel' in nature.lower() or 'converge' in nature.lower():
            return f"{ref_id} operates via parallel channel — may combine with {source_id}"
        else:
            return f"Mechanistically linked to {source_id}"

    # =========================================================================
    # Sprint QA-2: Architect Spec Sheet — Multi-Template Synthesis
    # =========================================================================

    def extract_calibrated_thresholds(self, template: Dict) -> List[Dict]:
        """
        Extract quantitative thresholds from a template's calibrated_parameters.

        Sprint QA-2: Addresses panel finding that architects need numbers
        (lux, dB, m², °C) not mechanism descriptions.

        Returns a list of threshold dicts, each with:
        - parameter: name of the parameter
        - value: the calibrated value
        - unit: measurement unit
        - range: [min, max] acceptable range
        - confidence: calibration confidence (0-1)
        - note: human-readable context
        - template_source: display_id of source template

        Design Decision DD-7: We use calibrated_parameters (panel-reviewed
        values) rather than mining numbers from free text. This ensures
        every threshold has a confidence level and provenance.
        """
        thresholds = []
        cal = template.get('calibrated_parameters', {})
        display_id = template.get('display_id', '?')

        for param_name, param_data in cal.items():
            if not isinstance(param_data, dict):
                continue
            thresholds.append({
                'parameter': param_name.replace('_', ' '),
                'value': param_data.get('value'),
                'unit': param_data.get('unit', ''),
                'range': param_data.get('range', []),
                'ci_95': param_data.get('ci_95', []),
                'confidence': param_data.get('confidence', 0.5),
                'bridge_warrant': param_data.get('bridge_warrant', ''),
                'note': param_data.get('note', ''),
                'template_source': display_id,
                'provenance': {
                    'calibration_panel': template.get('calibration_panel', 'unknown'),
                    'calibration_date': template.get('calibration_date', 'unknown'),
                    'calibration_status': template.get('calibration_status', 'unknown'),
                    'template_id': template.get('template_id', ''),
                },
            })

        return thresholds

    def query_for_building_type(
        self,
        building_type: str,
        keywords: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Find all templates applicable to a specific building type.

        Sprint QA-2: Addresses panel finding that architects need
        multi-template synthesis per room type.

        Args:
            building_type: e.g. 'healthcare', 'office', 'education'
            keywords: Optional additional filter keywords

        Returns:
            Dict with matched templates, combined thresholds, and
            mechanism chains organized by domain.

        Design Decision DD-8: We match building_type using substring
        matching to handle the heterogeneous building_types format
        (some are exact like 'healthcare', others are descriptive like
        'hospitals — highest priority, largest documented effect').
        """
        bt_lower = building_type.lower()
        matched_templates = []

        for tid, template in self.templates_by_id.items():
            building_types = template.get('building_types', [])
            if not building_types:
                continue

            # Substring match against building_types entries
            matches = any(
                bt_lower in bt.lower() or bt.lower() in bt_lower
                for bt in building_types
                if isinstance(bt, str)
            )
            # Also check for 'all' or 'all_occupied_buildings'
            has_all = any(
                bt.lower().startswith('all')
                for bt in building_types
                if isinstance(bt, str)
            )

            if matches or has_all:
                relevance = 1.0 if matches else 0.5
                # If keywords given, boost relevance for keyword matches
                if keywords:
                    kw_rel = self._compute_relevance(template, keywords)
                    relevance = max(relevance, kw_rel)
                matched_templates.append((relevance, template))

        # Sort by relevance descending
        matched_templates.sort(key=lambda x: -x[0])
        templates = [t for _, t in matched_templates]

        return {
            'building_type': building_type,
            'n_templates': len(templates),
            'templates': [
                {
                    'display_id': t.get('display_id', '?'),
                    'name': t.get('name', '?'),
                    'relevance': rel,
                }
                for rel, t in matched_templates[:20]
            ],
            'spec_sheet': self.multi_template_synthesis(templates[:10]),
        }

    def multi_template_synthesis(
        self,
        templates: List[Dict],
    ) -> Dict[str, Any]:
        """
        Synthesize a design spec sheet from multiple templates.

        Sprint QA-2: Core method that addresses the Architect panel's
        #1 gap — multi-template synthesis.

        Combines quantitative thresholds, mechanism chains, scope
        conditions, and moderators from all input templates into a
        single design specification.

        Design Decision DD-9: We organize the spec sheet by DOMAIN
        (acoustic, visual/light, air quality, spatial, biophilic, thermal)
        inferred from template display_id prefixes and content. This
        mirrors how architects organize their specifications.
        """
        # Collect all thresholds
        all_thresholds = []
        for t in templates:
            all_thresholds.extend(self.extract_calibrated_thresholds(t))

        # Collect all mechanism chains
        all_chains = []
        for t in templates:
            mc = t.get('mechanism_chain', [])
            if mc:
                all_chains.append({
                    'template': t.get('display_id', '?'),
                    'name': t.get('name', '?'),
                    'steps': mc,
                })

        # Collect all scope conditions and moderators
        all_scope = []
        all_moderators = []
        seen_scope = set()
        seen_mods = set()
        for t in templates:
            for sc in t.get('scope_conditions', []):
                sc_str = str(sc)
                if sc_str[:50].lower() not in seen_scope:
                    seen_scope.add(sc_str[:50].lower())
                    all_scope.append(sc_str)
            for mod in t.get('moderators', []):
                mod_str = str(mod)
                if mod_str[:50].lower() not in seen_mods:
                    seen_mods.add(mod_str[:50].lower())
                    all_moderators.append(mod_str)

        # Organize thresholds by domain
        domains = self._classify_thresholds_by_domain(all_thresholds, templates)

        # Build the spec sheet
        return {
            'thresholds_by_domain': domains,
            'n_thresholds': len(all_thresholds),
            'mechanism_chains': all_chains[:10],
            'scope_conditions': all_scope[:15],
            'moderators': all_moderators[:15],
            'n_templates_synthesized': len(templates),
            'template_ids': [t.get('display_id', '?') for t in templates],
            'confidence_summary': self._summarize_threshold_confidence(all_thresholds),
        }

    def _classify_thresholds_by_domain(
        self,
        thresholds: List[Dict],
        templates: List[Dict],
    ) -> Dict[str, List[Dict]]:
        """
        Classify thresholds into architectural domains.

        Design Decision DD-10: Domain classification uses template
        display_id prefixes (AUD_ → acoustic, CB_ → circadian/light)
        plus unit-based heuristics (dB → acoustic, lux → visual).
        """
        domains: Dict[str, List[Dict]] = {
            'acoustic': [],
            'visual_light': [],
            'air_quality': [],
            'spatial': [],
            'biophilic': [],
            'thermal': [],
            'other': [],
        }

        for threshold in thresholds:
            source = threshold.get('template_source', '').upper()
            unit = threshold.get('unit', '').lower()
            param = threshold.get('parameter', '').lower()

            # Classify by template prefix first
            if any(p in source for p in ['AUD', 'SOUND', 'NOISE', 'REVERB']):
                domains['acoustic'].append(threshold)
            elif any(p in source for p in ['CB', 'LIGHT', 'CIRCADIAN', 'VIEW']):
                domains['visual_light'].append(threshold)
            elif any(p in source for p in ['RESP', 'AIR', 'VENT', 'CO2']):
                domains['air_quality'].append(threshold)
            elif any(p in source for p in ['ENCL', 'SPATIAL', 'CEIL', 'PP']):
                domains['spatial'].append(threshold)
            elif any(p in source for p in ['BIO', 'NATURE', 'FRACTAL', 'PLANT']):
                domains['biophilic'].append(threshold)
            elif any(p in source for p in ['THERM', 'TEMP']):
                domains['thermal'].append(threshold)
            # Fall back to unit-based classification
            elif 'db' in unit or 'decibel' in unit or 'hz' in unit:
                domains['acoustic'].append(threshold)
            elif 'lux' in unit or 'kelvin' in unit or 'lumen' in unit:
                domains['visual_light'].append(threshold)
            elif 'ppm' in unit or 'cfm' in unit:
                domains['air_quality'].append(threshold)
            elif any(u in unit for u in ['meter', 'feet', 'ft', 'ratio']):
                domains['spatial'].append(threshold)
            elif '°' in unit or 'celsius' in unit or 'fahrenheit' in unit:
                domains['thermal'].append(threshold)
            else:
                domains['other'].append(threshold)

        # Remove empty domains
        return {k: v for k, v in domains.items() if v}

    def _summarize_threshold_confidence(
        self,
        thresholds: List[Dict],
    ) -> Dict[str, Any]:
        """Summarize confidence levels across all thresholds."""
        if not thresholds:
            return {'mean_confidence': 0.0, 'n_high': 0, 'n_medium': 0, 'n_low': 0}

        confidences = [t.get('confidence', 0.5) for t in thresholds]
        return {
            'mean_confidence': round(sum(confidences) / len(confidences), 3),
            'n_high': sum(1 for c in confidences if c >= 0.7),
            'n_medium': sum(1 for c in confidences if 0.4 <= c < 0.7),
            'n_low': sum(1 for c in confidences if c < 0.4),
            'strongest_warrant': max(
                (t.get('bridge_warrant', '') for t in thresholds),
                key=lambda w: {'MECHANISM': 3, 'EMPIRICAL': 2, 'ANALOGICAL': 1}.get(w, 0),
                default='',
            ),
        }

    # =========================================================================
    # Sprint QA-3: The Evidence Layer — Effect Sizes & Study Design
    # =========================================================================

    MATURITY_TO_STUDY_DESIGN = {
        'established': {'design': 'Multiple RCTs / Meta-analysis', 'badge': '🟢 STRONG', 'level': 5},
        'supported': {'design': 'RCT / Systematic review', 'badge': '🟢 MODERATE-STRONG', 'level': 4},
        'how-actually': {'design': 'Quasi-experimental / Strong observation', 'badge': '🟡 MODERATE', 'level': 3},
        'how-plausibly': {'design': 'Observational / Cross-sectional', 'badge': '🟠 PRELIMINARY', 'level': 2},
        'how-possibly': {'design': 'Case study / Expert opinion', 'badge': '🔴 WEAK', 'level': 1},
        'speculative': {'design': 'Theoretical only', 'badge': '🔴 THEORETICAL', 'level': 0},
        'preliminary': {'design': 'Pilot study / Single study', 'badge': '🟠 PRELIMINARY', 'level': 2},
        'calibrated': {'design': 'Panel-calibrated (study design varies)', 'badge': '🟡 CALIBRATED', 'level': 3},
        'uncalibrated': {'design': 'Uncalibrated (study design unknown)', 'badge': '⚪ UNCALIBRATED', 'level': 1},
    }

    EFFECT_SIZE_LABELS = {
        # Cohen's d benchmarks
        'd': [(0.2, 'small'), (0.5, 'medium'), (0.8, 'large'), (1.2, 'very large')],
        # Correlation r benchmarks
        'r': [(0.1, 'small'), (0.3, 'medium'), (0.5, 'large')],
        # Odds ratio benchmarks
        'or': [(1.5, 'small'), (2.5, 'medium'), (4.0, 'large')],
    }

    def extract_effect_sizes(self, template: Dict) -> List[Dict[str, Any]]:
        """
        Extract effect size data from template calibrated_parameters.

        Sprint QA-3: Addresses Researcher panel's #1 gap — "Where are the
        effect sizes?"

        Design Decision DD-17: We look for parameters whose names or units
        contain effect size indicators (d, Cohen's, ratio, proportion,
        odds, beta). Each gets a magnitude label (small/medium/large) per
        Cohen's benchmarks.
        """
        effect_sizes = []
        cal = template.get('calibrated_parameters', {})
        display_id = template.get('display_id', '?')

        for param_name, param_data in cal.items():
            if not isinstance(param_data, dict):
                continue

            unit = str(param_data.get('unit', '')).lower()
            name = param_name.lower()
            value = param_data.get('value')

            if value is None:
                continue

            # Detect effect size type
            es_type = None
            if "cohen" in unit or "cohen" in name or name.startswith('d_') or unit.startswith('d '):
                es_type = 'd'
            elif 'ratio' in unit or 'ratio' in name:
                es_type = 'or'
            elif 'proportion' in unit or 'fraction' in unit:
                es_type = 'r'  # Approximate
            elif 'beta' in unit or 'beta' in name:
                es_type = 'r'

            if es_type is None:
                continue

            # Classify magnitude
            magnitude = 'unknown'
            abs_value = abs(float(value))
            for threshold, label in self.EFFECT_SIZE_LABELS.get(es_type, []):
                if abs_value >= threshold:
                    magnitude = label

            effect_sizes.append({
                'parameter': param_name.replace('_', ' '),
                'value': value,
                'unit': param_data.get('unit', ''),
                'effect_type': es_type,
                'magnitude': magnitude,
                'ci_95': param_data.get('ci_95', []),
                'confidence': param_data.get('confidence', 0.5),
                'template_source': display_id,
                'provenance': {
                    'calibration_panel': template.get('calibration_panel', 'unknown'),
                    'calibration_date': template.get('calibration_date', 'unknown'),
                },
            })

        return effect_sizes

    def classify_study_design(self, template: Dict) -> Dict[str, Any]:
        """
        Infer study design level from template maturity and bridge warrant.

        Sprint QA-3: Provides study design "badges" for every template.
        Since templates don't have a dedicated study_design field, we
        infer from the maturity/calibration_status hierarchy.

        Design Decision DD-18: Maturity → study design mapping is an
        approximation. 'established' implies multiple RCTs exist.
        'how-plausibly' implies observational only. The badge system
        gives users a quick visual quality indicator.
        """
        maturity = template.get('calibration_status', 'uncalibrated').lower()
        bridge = template.get('bridge_warrant', '').lower()

        design = self.MATURITY_TO_STUDY_DESIGN.get(
            maturity,
            {'design': 'Unknown', 'badge': '⚪ UNKNOWN', 'level': 0}
        )

        # Upgrade if bridge warrant is EMPIRICAL (suggests direct evidence)
        if bridge == 'empirical' and design['level'] < 3:
            design = {
                'design': 'Empirical (study design varies)',
                'badge': '🟡 EMPIRICAL',
                'level': 3,
            }

        return {
            **design,
            'maturity_source': maturity,
            'bridge_warrant': bridge,
            'template_id': template.get('display_id', '?'),
            'provenance': {
                'calibration_panel': template.get('calibration_panel', 'unknown'),
                'calibration_date': template.get('calibration_date', 'unknown'),
            },
        }

    def compute_evidence_strength(
        self, templates: List[Dict]
    ) -> Dict[str, Any]:
        """
        Compute overall evidence strength from multiple templates.

        Sprint QA-3: Synthesizes maturity levels and effect sizes into
        a single evidence strength score for the entire answer.

        Design Decision DD-19: Evidence strength = weighted average of
        study design levels, with established (5) and supported (4)
        weighted higher. Provides a single 'evidence_strength' label
        that summarizes the credibility of the entire answer.
        """
        if not templates:
            return {
                'strength': 'insufficient',
                'badge': '⚪ NO EVIDENCE',
                'level': 0,
                'template_count': 0,
            }

        designs = [self.classify_study_design(t) for t in templates]
        levels = [d['level'] for d in designs]
        n_strong = sum(1 for l in levels if l >= 4)
        avg_level = sum(levels) / len(levels)

        # Determine badge
        if avg_level >= 4:
            badge = '🟢 STRONG EVIDENCE'
            strength = 'strong'
        elif avg_level >= 3:
            badge = '🟡 MODERATE EVIDENCE'
            strength = 'moderate'
        elif avg_level >= 2:
            badge = '🟠 PRELIMINARY EVIDENCE'
            strength = 'preliminary'
        else:
            badge = '🔴 WEAK EVIDENCE'
            strength = 'weak'

        # Extract effect sizes from all templates
        all_effects = []
        for t in templates:
            all_effects.extend(self.extract_effect_sizes(t))

        return {
            'strength': strength,
            'badge': badge,
            'level': round(avg_level, 1),
            'template_count': len(templates),
            'n_strong_evidence': n_strong,
            'study_designs': designs,
            'effect_sizes': all_effects,
            'n_effect_sizes': len(all_effects),
        }


    # =========================================================================

    # --- Clinician: GRADE Evidence Mapping (DD-11) ---

    MATURITY_TO_GRADE = {
        'established': 'HIGH',
        'supported': 'MODERATE',
        'how-actually': 'MODERATE',
        'how-plausibly': 'LOW',
        'preliminary': 'LOW',
        'how-possibly': 'VERY_LOW',
        'speculative': 'VERY_LOW',
    }

    GRADE_DESCRIPTIONS = {
        'HIGH': 'Further research very unlikely to change confidence in the estimate.',
        'MODERATE': 'Further research likely to change confidence and may change the estimate.',
        'LOW': 'Further research very likely to change the estimate.',
        'VERY_LOW': 'Any estimate is very uncertain.',
    }

    def map_to_grade(self, maturity: str) -> Dict[str, str]:
        """
        Map ATLAS maturity level to GRADE evidence rating.

        Sprint QA-4 — Clinician panel demanded GRADE ratings for
        clinical decision-making. Maturity levels map as:
        established → HIGH, supported → MODERATE, preliminary → LOW,
        speculative → VERY_LOW.

        Design Decision DD-11: Direct mapping without intermediate
        computation. The GRADE system requires structured assessment
        of risk of bias, inconsistency, indirectness, imprecision,
        and publication bias — which we cannot fully assess. This
        mapping provides an APPROXIMATE grade. All GRADE ratings
        carry a disclaimer.
        """
        grade = self.MATURITY_TO_GRADE.get(maturity.lower(), 'LOW')
        return {
            'grade': grade,
            'grade_description': self.GRADE_DESCRIPTIONS[grade],
            'maturity_source': maturity,
            'mapping_provenance': 'ATLAS maturity → GRADE mapping v1 (2026-02-27, panel-reviewed)',
            'disclaimer': (
                'ATLAS GRADE ratings are approximate mappings from template '
                'maturity levels. They do not include full GRADE methodology '
                '(risk of bias, imprecision, indirectness, inconsistency, '
                'publication bias). Use clinical judgment.'
            ),
        }

    # --- Facilities: Proxy Metric Translation (DD-12) ---

    SCIENTIFIC_TO_PROXY_METRICS = {
        # Scientific outcome → Facilities-measurable KPI
        'circadian entrainment': ['sick days per quarter', 'self-reported sleep quality score', 'absenteeism rate'],
        'circadian disruption': ['sick days per quarter', 'absenteeism rate'],
        'cortisol': ['self-reported stress survey', 'sick leave rate', 'turnover rate'],
        'stress': ['self-reported stress survey', 'sick leave rate', 'HR exit survey scores'],
        'attention restoration': ['task completion rate', 'error rate', 'self-reported focus score'],
        'cognitive performance': ['task completion rate', 'error rate', 'productivity index'],
        'creativity': ['idea generation count', 'patent/innovation metrics', 'brainstorm output'],
        'mood': ['satisfaction survey', 'NPS score', 'complaint frequency'],
        'sleep quality': ['absenteeism rate', 'morning productivity', 'self-reported sleep score'],
        'pain perception': ['analgesic demand', 'patient pain scores (VAS)', 'length of stay'],
        'recovery': ['length of stay', 'readmission rate', 'patient satisfaction'],
        'anxiety': ['self-reported anxiety survey', 'behavioral observation', 'heart rate variability'],
        'blood pressure': ['annual health screening results', 'hypertension prevalence'],
        'respiratory': ['sick building syndrome complaints', 'respiratory illness rate'],
        'thermal comfort': ['comfort survey scores', 'thermostat adjustment frequency', 'complaint rate'],
        'acoustic comfort': ['noise complaint rate', 'speech privacy satisfaction', 'focus time logged'],
        'wayfinding': ['time to destination', 'help desk queries', 'visitor satisfaction'],
        'social interaction': ['collaboration space usage', 'meeting frequency', 'team satisfaction'],
        'productivity': ['output per employee', 'billable hours', 'task completion rate'],
        'satisfaction': ['overall satisfaction survey', 'NPS score', 'retention rate'],
    }

    def translate_to_proxy_metrics(self, scientific_outcomes: List[str]) -> List[Dict[str, Any]]:
        """
        Translate scientific outcomes to facilities-measurable KPIs.

        Sprint QA-4 — Facilities panel said: "I can't measure circadian
        entrainment. Give me absenteeism rate."

        Design Decision DD-12: Static mapping table rather than LLM
        generation. Ensures consistency and allows facilities auditing
        of the translation. Table can be extended by domain experts.
        """
        translations = []
        for outcome in scientific_outcomes:
            outcome_lower = outcome.lower()
            matched_proxies = []
            for scientific, proxies in self.SCIENTIFIC_TO_PROXY_METRICS.items():
                if scientific in outcome_lower or outcome_lower in scientific:
                    matched_proxies.extend(proxies)

            if matched_proxies:
                # Deduplicate
                seen = set()
                unique = []
                for p in matched_proxies:
                    if p not in seen:
                        seen.add(p)
                        unique.append(p)
                translations.append({
                    'scientific_outcome': outcome,
                    'measurable_kpis': unique[:4],
                    'measurement_guidance': (
                        f'Track these KPIs for 90+ days before/after intervention '
                        f'to establish effect of changes related to {outcome}.'
                    ),
                })
            else:
                translations.append({
                    'scientific_outcome': outcome,
                    'measurable_kpis': ['custom survey required'],
                    'measurement_guidance': (
                        f'No standard proxy metric for "{outcome}". '
                        f'Design a custom pre/post survey.'
                    ),
                })

        return translations

    # --- Student: Technical Term Glossary (DD-13) ---

    GLOSSARY = {
        'circadian': 'Relating to the ~24-hour biological clock that regulates sleep, hormones, and body temperature.',
        'melanopic lux': 'A measure of light intensity weighted by its effect on melanopsin-containing retinal cells that regulate circadian rhythm (not the same as visual brightness).',
        'iprgc': 'Intrinsically photosensitive retinal ganglion cells — specialized light-sensing cells in the eye that signal "time of day" to the brain.',
        'scn': 'Suprachiasmatic nucleus — the brain\'s master clock, located in the hypothalamus. Receives light signals from ipRGC cells.',
        'cortisol': 'The primary stress hormone produced by the adrenal glands. Elevated cortisol impairs memory, immune function, and sleep.',
        'hpa axis': 'Hypothalamic-pituitary-adrenal axis — the body\'s central stress response system. Chronic activation causes health problems.',
        'amygdala': 'Almond-shaped brain structure that detects threats and triggers the fight-or-flight response. Activated by enclosed or threatening spaces.',
        'hippocampus': 'Brain structure crucial for memory formation and spatial navigation. Contains "place cells" that map environments.',
        'place cells': 'Neurons in the hippocampus that fire when an animal is in a specific location. They create a cognitive map of space.',
        'predictive processing': 'Theory that the brain constantly predicts sensory input and updates when surprised. Unexpected environments increase cognitive load.',
        'attention restoration': 'Theory (Kaplan, 1995) that natural environments restore directed attention capacity depleted by mental work.',
        'biophilia': 'The innate human tendency to seek connections with nature and other living systems (E.O. Wilson, 1984).',
        'prospect-refuge': 'Design principle: humans prefer spaces where they can see (prospect) without being seen (refuge). Reduces threat perception.',
        'enclosure-threat': 'Perception of being trapped in a small/confining space, triggering amygdala activation and stress response.',
        'entrenchment': 'In coherentist epistemology: how deeply connected a belief is within the web. Highly entrenched beliefs are harder to revise.',
        'credence': 'The degree of confidence (0-1) assigned to a belief based on evidence. 0 = certainly false, 1 = certainly true.',
        'reverberation time': 'Time (in seconds) for sound to decay by 60 dB after source stops (RT60). Key acoustic parameter for room design.',
        'cohen\'s d': 'A measure of effect size — the standardized difference between two group means. 0.2 = small, 0.5 = medium, 0.8 = large.',
        'rct': 'Randomized Controlled Trial — the gold standard study design where participants are randomly assigned to treatment or control groups.',
        'scope conditions': 'The specific circumstances under which a scientific finding applies. Outside these conditions, the effect may not hold.',
        'moderator': 'A variable that changes the strength or direction of an effect. Example: age moderates the effect of noise on concentration.',
        'bayesian network': 'A probabilistic graphical model representing relationships between variables. Used to compute updated confidence given new evidence.',
        'voi': 'Value of Information — how much a piece of missing evidence would change our conclusions if obtained. High VOI = high research priority.',
        'fractal dimension': 'A measure of spatial complexity. Natural scenes typically have fractal dimension 1.3-1.5, which humans find aesthetically pleasing.',
    }

    def get_glossary_for_terms(self, text: str) -> List[Dict[str, str]]:
        """
        Extract technical terms from text and provide definitions.

        Sprint QA-4 — Student panel said: "The moment I click into detail,
        I'm hit with jargon."

        Design Decision DD-13: Static glossary rather than LLM-generated
        definitions. Ensures accuracy and consistency. Terms are matched
        by substring presence in the answer text.
        """
        found = []
        text_lower = text.lower()
        for term, definition in self.GLOSSARY.items():
            if term in text_lower:
                found.append({
                    'term': term,
                    'definition': definition,
                })
        return found

    # --- Policy: Building Standards Cross-Reference (DD-14) ---

    STANDARDS_REGISTRY = {
        'daylight': [
            {'standard': 'EN 17037', 'requirement': 'Minimum daylight factor 2% for residential, 1.5% for non-residential', 'jurisdiction': 'EU'},
            {'standard': 'WELL v2 Light L01', 'requirement': 'Minimum 200 melanopic equivalent daylight illuminance (m-EDI) at workstations', 'jurisdiction': 'International'},
            {'standard': 'LEED v4.1 IEQ Credit', 'requirement': 'Daylight factor ≥2% in 75% of regularly occupied spaces', 'jurisdiction': 'International'},
        ],
        'light': [
            {'standard': 'EN 12464-1', 'requirement': 'Minimum illuminance levels by task type (500 lux writing/reading)', 'jurisdiction': 'EU'},
            {'standard': 'WELL v2 Light L03', 'requirement': 'Circadian lighting design with melanopic ratios', 'jurisdiction': 'International'},
        ],
        'noise': [
            {'standard': 'ANSI S12.60', 'requirement': 'Maximum 35 dB(A) background noise in classrooms', 'jurisdiction': 'US'},
            {'standard': 'WELL v2 Sound S01', 'requirement': 'Background noise ≤40 dB(A) in open offices', 'jurisdiction': 'International'},
            {'standard': 'BB93', 'requirement': 'Acoustic design of schools: RT60 ≤0.8s in classrooms', 'jurisdiction': 'UK'},
        ],
        'acoustic': [
            {'standard': 'WELL v2 Sound S04', 'requirement': 'Reverberation time limits by room type', 'jurisdiction': 'International'},
            {'standard': 'BREEAM Hea 05', 'requirement': 'Acoustic performance requirements for key spaces', 'jurisdiction': 'UK/International'},
        ],
        'air quality': [
            {'standard': 'ASHRAE 62.1', 'requirement': 'Minimum ventilation rates by occupancy type', 'jurisdiction': 'US'},
            {'standard': 'WELL v2 Air A01', 'requirement': 'CO₂ levels ≤800 ppm (densely occupied) or ≤600 ppm (low density)', 'jurisdiction': 'International'},
            {'standard': 'EN 16798-1', 'requirement': 'Indoor air quality categories I-IV with CO₂ limits', 'jurisdiction': 'EU'},
        ],
        'thermal': [
            {'standard': 'ASHRAE 55', 'requirement': 'Thermal comfort: operative temp 68-76°F (20-24°C) for sedentary work', 'jurisdiction': 'US'},
            {'standard': 'EN ISO 7730', 'requirement': 'PMV-PPD thermal comfort model, Category B: PPD<10%', 'jurisdiction': 'EU/International'},
            {'standard': 'WELL v2 Thermal T01', 'requirement': 'Meet ASHRAE 55 + seasonal adjustments', 'jurisdiction': 'International'},
        ],
        'biophilic': [
            {'standard': 'WELL v2 Mind M02', 'requirement': 'Access to nature: plants, views, or nature imagery in occupied spaces', 'jurisdiction': 'International'},
            {'standard': 'LEED v4.1 SS Credit', 'requirement': 'Quality views to nature from 75% of regularly occupied spaces', 'jurisdiction': 'International'},
        ],
        'view': [
            {'standard': 'EN 17037 Section 5', 'requirement': 'View quality assessment: layers, distance, environmental information', 'jurisdiction': 'EU'},
            {'standard': 'WELL v2 Light L04', 'requirement': 'View at least two types of content from 75% of workstations', 'jurisdiction': 'International'},
        ],
    }

    def find_relevant_standards(self, topics: List[str]) -> List[Dict[str, str]]:
        """
        Find building standards relevant to given topics.

        Sprint QA-4 — Policy panel said: "No mention of existing standards."

        Design Decision DD-14: Static registry of major international
        standards. Covers WELL v2, LEED v4.1, BREEAM, ASHRAE, EN/ISO.
        Extensible by adding entries to STANDARDS_REGISTRY.
        """
        matched = []
        seen_standards = set()
        for topic in topics:
            topic_lower = topic.lower()
            for key, standards in self.STANDARDS_REGISTRY.items():
                if key in topic_lower or topic_lower in key:
                    for std in standards:
                        std_id = std['standard']
                        if std_id not in seen_standards:
                            seen_standards.add(std_id)
                            matched.append(std)
        return matched

    # --- Clinician: Contraindication Registry (DD-15) ---

    CONTRAINDICATIONS = {
        'bright_light': [
            {'condition': 'Photosensitive epilepsy', 'risk': 'Seizure trigger', 'severity': 'critical'},
            {'condition': 'Migraine with aura', 'risk': 'May trigger or worsen episodes', 'severity': 'high'},
            {'condition': 'Bipolar disorder (manic phase)', 'risk': 'Bright light may exacerbate mania', 'severity': 'high'},
            {'condition': 'Retinal conditions (macular degeneration)', 'risk': 'Potential photodamage', 'severity': 'medium'},
        ],
        'high_contrast': [
            {'condition': 'Lewy body dementia', 'risk': 'Visual illusions/hallucinations from high-contrast patterns', 'severity': 'high'},
            {'condition': 'Autism spectrum (sensory sensitivity)', 'risk': 'Visual overstimulation', 'severity': 'medium'},
        ],
        'noise_masking': [
            {'condition': 'Hearing impairment', 'risk': 'Reduced speech intelligibility', 'severity': 'high'},
            {'condition': 'Tinnitus', 'risk': 'May worsen or interact with tinnitus frequency', 'severity': 'medium'},
            {'condition': 'PTSD (noise-triggered)', 'risk': 'Unexpected sound changes may trigger episodes', 'severity': 'high'},
        ],
        'open_plan': [
            {'condition': 'ADHD', 'risk': 'Increased distractibility', 'severity': 'high'},
            {'condition': 'Autism spectrum', 'risk': 'Sensory overload', 'severity': 'high'},
            {'condition': 'Social anxiety disorder', 'risk': 'Increased exposure anxiety', 'severity': 'medium'},
        ],
        'nature_exposure': [
            {'condition': 'Allergies (pollen, mold)', 'risk': 'Living plants may trigger reactions', 'severity': 'medium'},
            {'condition': 'Arachnophobia/entomophobia', 'risk': 'Indoor plants attract insects', 'severity': 'low'},
        ],
        'enclosed_space': [
            {'condition': 'Claustrophobia', 'risk': 'Panic response', 'severity': 'high'},
            {'condition': 'PTSD (confinement-related)', 'risk': 'Trauma trigger', 'severity': 'critical'},
        ],
    }

    def find_contraindications(self, intervention_keywords: List[str]) -> List[Dict[str, str]]:
        """
        Find clinical contraindications for environmental interventions.

        Sprint QA-4 — Clinician panel flagged the system as "clinically
        dangerous" without contraindication information.

        Design Decision DD-15: Static contraindication registry organized
        by intervention type. Every entry has a severity level (critical,
        high, medium, low). Critical contraindications should be shown
        prominently with a ⚠️ warning.
        """
        matched = []
        seen = set()
        for kw in intervention_keywords:
            # Normalize: 'bright light' → 'bright_light' for matching
            kw_lower = kw.lower().replace(' ', '_')
            kw_natural = kw.lower()
            for intervention, contras in self.CONTRAINDICATIONS.items():
                # Match intervention name to keyword (with and without underscores)
                if (kw_lower in intervention or intervention in kw_lower or
                    kw_natural in intervention.replace('_', ' ') or
                    intervention.replace('_', ' ') in kw_natural):
                    for contra in contras:
                        key = f"{contra['condition']}_{intervention}"
                        if key not in seen:
                            seen.add(key)
                            matched.append({
                                **contra,
                                'intervention': intervention.replace('_', ' '),
                            })

        # Sort by severity (critical first)
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        matched.sort(key=lambda x: severity_order.get(x['severity'], 9))

        # Add provenance disclaimer
        for m in matched:
            m['provenance'] = (
                'ATLAS contraindication registry v1 (2026-02-27). '
                'Based on published clinical literature. '
                'This is NOT a substitute for clinical assessment.'
            )

        return matched

    def query(
        self,
        query_text: str,
        keywords: Optional[List[str]] = None,
        min_relevance: float = 0.2,
        max_templates: int = 5
    ) -> QueryResponse:
        """
        Query the template library to answer a design question.

        Args:
            query_text: Natural language question
            keywords: Optional explicit keywords (auto-extracted if not provided)
            min_relevance: Minimum relevance score to include template
            max_templates: Maximum number of templates to include

        Returns:
            QueryResponse with HOW, WHY, WHEN, FOR WHOM
        """
        # Extract keywords if not provided
        if keywords is None:
            # Simple keyword extraction — should use NLP in production
            stop_words = {'the', 'a', 'an', 'is', 'are', 'do', 'does', 'what',
                         'when', 'where', 'who', 'how', 'why', 'and', 'or', 'for',
                         'in', 'on', 'at', 'to', 'of', 'with', 'by'}
            words = re.findall(r'\b\w+\b', query_text.lower())
            keywords = [w for w in words if w not in stop_words and len(w) > 2]

        # Score all templates
        scored = []
        seen_template_ids = set()
        for template in self.templates.values():
            if not isinstance(template, dict) or 'display_id' not in template:
                continue
            template_id = str(template.get('template_id', '')).strip()
            if not template_id or template_id in seen_template_ids:
                continue
            seen_template_ids.add(template_id)
            relevance = self._compute_relevance(template, keywords)
            if relevance >= min_relevance:
                scored.append((relevance, template))

        # Sort by relevance
        scored.sort(key=lambda x: -x[0])

        # Build answers from top templates
        answers = [
            self._build_template_answer(t, rel)
            for rel, t in scored[:max_templates]
        ]

        # Generate headline
        if answers:
            top = answers[0]
            headline = f"{top.name} (confidence: {top.confidence:.0%})"
        else:
            headline = "No relevant templates found"

        # Compute maturity distribution
        maturity_dist = defaultdict(int)
        for ans in answers:
            maturity_dist[ans.maturity] += 1

        # Aggregate evidence
        all_refs = []
        for ans in answers[:3]:
            all_refs.extend(ans.key_references[:2])

        # Extract deep details
        related = self._extract_related_templates(answers, self.templates)
        neuro_details = self._extract_neuroscience_details(answers)
        detailed_gaps = self._extract_detailed_research_gaps(answers, self.templates)

        # Build response
        return QueryResponse(
            query=query_text,
            headline=headline,
            how=self._synthesize_how(answers),
            why=self._synthesize_why(answers),
            when=self._aggregate_when(answers),
            for_whom=self._aggregate_for_whom(answers),
            relevant_templates=answers,
            causal_chain=self._synthesize_causal_chain(answers),
            overall_confidence=self._compute_overall_confidence(answers),
            maturity_distribution=dict(maturity_dist),
            key_evidence=all_refs[:6],
            related_templates=related,
            neuroscience_details=neuro_details,
            research_gaps_detailed=detailed_gaps,
            caveats=[
                "Template-based reasoning only — not grounded in specific article claims",
                "Confidence derived from maturity ratings, not Bayesian inference",
                "Scope conditions are necessary but may not be sufficient"
            ],
            research_gaps=self._identify_research_gaps(answers)
        )

    def format_response(
        self,
        response: QueryResponse,
        persona: UserPersona = None,
        level: int = 2
    ) -> str:
        """
        Format response as human-readable text, customized by persona and detail level.

        Args:
            response: The QueryResponse to format
            persona: User persona for customization (None = full response)
            level: Detail level 1-5 (1=headline, 5=full research gaps)
        """
        lines = []
        emphasis = self.PERSONA_EMPHASIS.get(persona, {}) if persona else {}

        # Level 1: Headline only
        lines.extend([
            f"QUERY: {response.query}",
            f"",
            f"HEADLINE: {response.headline}",
            f"CONFIDENCE: {response.overall_confidence:.0%}",
        ])

        if level < 2:
            return "\n".join(lines)

        # Level 2: Core answer (HOW, WHY, WHEN, FOR WHOM)
        primary = emphasis.get('primary', ['how', 'why', 'when', 'for_whom'])
        secondary = emphasis.get('secondary', [])

        # HOW
        if 'how' in primary or not persona:
            lines.extend([
                f"",
                f"═══ HOW (Mechanism) ═══",
                f"{response.how}",
                f"",
                f"Causal chain: {response.causal_chain}",
            ])

        # WHY
        if 'why' in primary or not persona:
            lines.extend([
                f"",
                f"═══ WHY (Principle) ═══",
                f"{response.why}",
            ])

        # WHEN
        if 'when' in primary or not persona:
            lines.extend([f"", f"═══ WHEN (Scope Conditions) ═══"])
            for condition in response.when[:5]:
                lines.append(f"  • {condition[:100]}{'...' if len(condition) > 100 else ''}")

        # FOR WHOM
        if 'for_whom' in primary or not persona:
            lines.extend([f"", f"═══ FOR WHOM (Moderators) ═══"])
            for mod in response.for_whom[:5]:
                lines.append(f"  • {mod[:100]}{'...' if len(mod) > 100 else ''}")

        # Evidence (always include at level 2+)
        lines.extend([f"", f"═══ EVIDENCE ═══"])
        for ref in response.key_evidence[:4]:
            lines.append(f"  • {ref[:100]}...")

        if level < 3:
            return "\n".join(lines)

        # Level 3: Related templates
        if response.related_templates:
            lines.extend([f"", f"═══ RELATED TEMPLATES ═══"])
            for rel in response.related_templates[:5]:
                lines.append(f"  [{rel.display_id}] {rel.name[:50]}")
                lines.append(f"      └─ {rel.relationship[:70]}...")

        if level < 4:
            return "\n".join(lines)

        # Level 4: Neuroscience details
        if (emphasis.get('include_neuroscience', True) or not persona) and response.neuroscience_details:
            lines.extend([f"", f"═══ NEUROSCIENCE DETAILS ═══"])
            for detail in response.neuroscience_details[:5]:
                lines.append(f"")
                lines.append(f"  ┌─ {detail.link_summary}")
                lines.append(f"  │ Level: {detail.level_transition}")
                if detail.neural_substrate:
                    lines.append(f"  │ Neural substrate: {detail.neural_substrate}")
                lines.append(f"  │ Maturity: {detail.maturity}")
                mech = detail.mechanism_detail[:120] + "..." if len(detail.mechanism_detail) > 120 else detail.mechanism_detail
                lines.append(f"  │ Mechanism: {mech}")
                lines.append(f"  └─ Research needed: {detail.research_needed[:80]}...")

        if level < 5:
            return "\n".join(lines)

        # Level 5: Detailed research gaps
        if (emphasis.get('include_research_gaps', True) or not persona) and response.research_gaps_detailed:
            lines.extend([f"", f"═══ RESEARCH GAPS (Detailed) ═══"])
            for gap in response.research_gaps_detailed[:6]:
                lines.append(f"")
                lines.append(f"  [{gap.priority.upper()}] {gap.gap_type}: {gap.description[:60]}...")
                lines.append(f"      Current evidence: {gap.current_evidence[:60]}...")
                lines.append(f"      Proposed study: {gap.proposed_study[:70]}...")
                lines.append(f"      Source: {gap.template_source}")

        # Caveats (always at end)
        lines.extend([f"", f"═══ CAVEATS ═══"])
        for caveat in response.caveats:
            lines.append(f"  ⚠ {caveat}")

        return "\n".join(lines)

    def format_for_persona(self, response: QueryResponse, persona: UserPersona) -> str:
        """
        Format response specifically for a user persona.

        Each persona gets a customized answer emphasizing what they need.
        """
        emphasis = self.PERSONA_EMPHASIS.get(persona, {})
        vocab = emphasis.get('vocabulary', 'general')

        lines = [f"[{persona.value.upper()} VIEW]", ""]

        # Persona-specific headline
        if persona == UserPersona.ARCHITECT:
            lines.append(f"DESIGN IMPLICATION: {response.headline}")
            lines.append(f"Confidence for design decision: {response.overall_confidence:.0%}")
        elif persona == UserPersona.RESEARCHER:
            lines.append(f"FINDING: {response.headline}")
            lines.append(f"Evidence strength: {response.overall_confidence:.0%} ({response.maturity_distribution})")
        elif persona == UserPersona.FACILITIES:
            lines.append(f"RECOMMENDATION: {response.headline}")
            lines.append(f"Confidence: {response.overall_confidence:.0%}")
        elif persona == UserPersona.STUDENT:
            lines.append(f"ANSWER: {response.headline}")
            lines.append(f"How certain are we? {response.overall_confidence:.0%}")
        elif persona == UserPersona.POLICY:
            lines.append(f"EVIDENCE SUMMARY: {response.headline}")
            lines.append(f"Strength of evidence: {response.overall_confidence:.0%}")
        elif persona == UserPersona.CLINICIAN:
            lines.append(f"CLINICAL RELEVANCE: {response.headline}")
            lines.append(f"Evidence level: {response.overall_confidence:.0%}")

        lines.append("")

        # Primary content based on persona
        primary = emphasis.get('primary', [])

        if 'how' in primary:
            lines.extend([
                "MECHANISM:",
                f"  {response.how}",
                ""
            ])

        if 'why' in primary:
            lines.extend([
                "PRINCIPLE:",
                f"  {response.why[:200]}...",
                ""
            ])

        if 'when' in primary:
            if persona == UserPersona.ARCHITECT:
                lines.append("DESIGN CONDITIONS:")
            elif persona == UserPersona.FACILITIES:
                lines.append("WHEN TO IMPLEMENT:")
            else:
                lines.append("CONDITIONS:")
            for w in response.when[:4]:
                lines.append(f"  • {w[:80]}...")
            lines.append("")

        if 'for_whom' in primary:
            if persona == UserPersona.CLINICIAN:
                lines.append("PATIENT POPULATIONS:")
            elif persona == UserPersona.POLICY:
                lines.append("AFFECTED POPULATIONS:")
            else:
                lines.append("WHO BENEFITS:")
            for w in response.for_whom[:4]:
                lines.append(f"  • {w[:80]}...")
            lines.append("")

        if 'neuroscience' in primary and response.neuroscience_details:
            if persona == UserPersona.STUDENT:
                lines.append("HOW IT WORKS IN THE BRAIN:")
            else:
                lines.append("NEURAL MECHANISM:")
            for detail in response.neuroscience_details[:3]:
                lines.append(f"  • {detail.link_summary}: {detail.neural_substrate or 'pathway TBD'}")
            lines.append("")

        if 'research_gaps' in primary and response.research_gaps_detailed:
            if persona == UserPersona.RESEARCHER:
                lines.append("RESEARCH OPPORTUNITIES:")
            else:
                lines.append("EVIDENCE GAPS:")
            for gap in response.research_gaps_detailed[:3]:
                lines.append(f"  [{gap.priority}] {gap.description[:60]}...")
                lines.append(f"      → {gap.proposed_study[:60]}...")
            lines.append("")

        # =====================================================================
        # Sprint QA-2/QA-4: Persona-specific enrichment (WIRED IN)
        # =====================================================================

        if persona == UserPersona.ARCHITECT:
            # QA-2: Inject quantitative thresholds from matched templates
            thresholds = []
            for ta in response.relevant_templates[:5]:
                template = self.templates_by_id.get(ta.template_id)
                if template:
                    thresholds.extend(self.extract_calibrated_thresholds(template))
            if thresholds:
                lines.append("QUANTITATIVE DESIGN THRESHOLDS:")
                for t in thresholds[:8]:
                    val = t['value']
                    unit_short = t['unit'][:40] if t['unit'] else ''
                    rng = f" (range: {t['range']})" if t['range'] else ''
                    conf = f"  [conf: {t['confidence']:.0%}]"
                    prov = f"  [source: {t['template_source']}, panel: {t['provenance']['calibration_panel']}]"
                    lines.append(f"  • {t['parameter']}: {val} {unit_short}{rng}{conf}")
                    lines.append(f"    {prov}")
                lines.append("")

        elif persona == UserPersona.CLINICIAN:
            # QA-4: GRADE evidence mapping
            maturities = [ta.maturity for ta in response.relevant_templates[:5]
                          if hasattr(ta, 'maturity') and ta.maturity]
            if maturities:
                lines.append("EVIDENCE GRADING (GRADE):")
                for mat in maturities:
                    grade_info = self.map_to_grade(mat)
                    lines.append(f"  • {mat} → {grade_info['grade']} — {grade_info['grade_description'][:60]}")
                lines.append(f"  ⚠️  {self.map_to_grade(maturities[0])['disclaimer'][:80]}...")
                lines.append("")

            # QA-4: Contraindications — extract intervention keywords from how
            intervention_kws = []
            for ta in response.relevant_templates[:3]:
                for pathway in ta.how[:2]:
                    for entity in getattr(pathway, 'entities', []):
                        intervention_kws.append(str(entity))
            # Add common intervention keywords from response text
            how_text = response.how.lower()
            for kw in ['light', 'noise', 'open plan', 'enclosed', 'nature', 'contrast']:
                if kw in how_text:
                    intervention_kws.append(kw)
            contras = self.find_contraindications(list(set(intervention_kws)))
            if contras:
                lines.append("⚠️  CONTRAINDICATIONS:")
                for c in contras[:5]:
                    severity_icon = '🔴' if c['severity'] == 'critical' else '🟠' if c['severity'] == 'high' else '🟡'
                    lines.append(f"  {severity_icon} {c['severity'].upper()}: {c['condition']} — {c['risk']}")
                    lines.append(f"    (intervention: {c['intervention']})")
                lines.append(f"  Provenance: {contras[0].get('provenance', 'ATLAS registry')[:60]}")
                lines.append("")

        elif persona == UserPersona.FACILITIES:
            # QA-4: Proxy metric translation
            # Extract scientific outcomes from the how field
            scientific_outcomes = []
            how_lower = response.how.lower()
            for outcome in self.SCIENTIFIC_TO_PROXY_METRICS.keys():
                if outcome in how_lower:
                    scientific_outcomes.append(outcome)
            if not scientific_outcomes:
                # Fallback: extract from template names
                for ta in response.relevant_templates[:3]:
                    for word in ta.name.lower().split():
                        if word in ['stress', 'mood', 'productivity', 'comfort', 'sleep']:
                            scientific_outcomes.append(word)
            if scientific_outcomes:
                translations = self.translate_to_proxy_metrics(list(set(scientific_outcomes)))
                lines.append("MEASURABLE KPIs (what to track):")
                for t in translations[:4]:
                    lines.append(f"  {t['scientific_outcome']}:")
                    for kpi in t['measurable_kpis'][:3]:
                        lines.append(f"    → {kpi}")
                    lines.append(f"    {t['measurement_guidance'][:60]}...")
                lines.append("")

        elif persona == UserPersona.RESEARCHER:
            # QA-3: Study design badges and effect sizes
            templates_raw = []
            for ta in response.relevant_templates[:5]:
                template = self.templates_by_id.get(ta.template_id)
                if template:
                    templates_raw.append(template)
            if templates_raw:
                evidence = self.compute_evidence_strength(templates_raw)
                lines.append(f"EVIDENCE STRENGTH: {evidence['badge']}")
                lines.append(f"  Based on {evidence['template_count']} templates, "
                             f"{evidence['n_strong_evidence']} with strong evidence")
                lines.append("")
                lines.append("STUDY DESIGN BADGES:")
                for sd in evidence['study_designs'][:5]:
                    lines.append(f"  {sd['badge']}  {sd['template_id']}: {sd['design']}")
                    lines.append(f"    Maturity: {sd['maturity_source']}, Warrant: {sd['bridge_warrant'] or 'none'}")
                lines.append("")
                if evidence['effect_sizes']:
                    lines.append(f"EFFECT SIZES ({evidence['n_effect_sizes']} found):")
                    for es in evidence['effect_sizes'][:6]:
                        lines.append(f"  • {es['parameter']}: {es['value']} {es['unit'][:30]} "
                                     f"({es['magnitude']}, {es['effect_type']})")
                        if es['ci_95']:
                            lines.append(f"    CI95: {es['ci_95']}")
                    lines.append("")

        elif persona == UserPersona.STUDENT:
            # QA-4: Glossary for jargon
            full_text = f"{response.how} {response.why} {' '.join(response.when)} {' '.join(response.for_whom)}"
            terms = self.get_glossary_for_terms(full_text)
            if terms:
                lines.append("📖 GLOSSARY:")
                for t in terms[:6]:
                    lines.append(f"  {t['term'].upper()}: {t['definition'][:100]}...")
                lines.append("")

        elif persona == UserPersona.POLICY:
            # QA-4: Standards cross-reference
            topics = []
            for ta in response.relevant_templates[:5]:
                did = ta.display_id.lower()
                for key in self.STANDARDS_REGISTRY.keys():
                    if key in did or key in ta.name.lower():
                        topics.append(key)
            # Also infer from response text
            for key in self.STANDARDS_REGISTRY.keys():
                if key in response.how.lower() or key in response.why.lower():
                    topics.append(key)
            if topics:
                standards = self.find_relevant_standards(list(set(topics)))
                if standards:
                    lines.append("APPLICABLE STANDARDS & CODES:")
                    for s in standards[:6]:
                        lines.append(f"  • {s['standard']} ({s['jurisdiction']})")
                        lines.append(f"    {s['requirement'][:70]}...")
                    lines.append("")

        # Evidence
        lines.append("KEY EVIDENCE:")
        for ref in response.key_evidence[:3]:
            lines.append(f"  • {ref[:80]}...")

        return "\n".join(lines)

    def enrich_response(
        self,
        response: QueryResponse,
        persona: UserPersona,
    ) -> Dict[str, Any]:
        """
        Return structured enrichment data for a persona + response.

        Unlike format_for_persona() which returns text, this returns
        machine-readable dicts for the Streamlit UI and API consumers.

        Sprint QA-2/QA-4 integration point — ensures sprint features
        are available both as formatted text AND structured data.

        Design Decision DD-16: Dual output (text + structured) so that
        Streamlit can render custom widgets (e.g., threshold tables,
        glossary popovers, contraindication alerts) while CLI users
        get formatted text.
        """
        enrichment: Dict[str, Any] = {
            'persona': persona.value,
            'query': response.query,
        }

        # All personas get evidence provenance
        enrichment['template_provenance'] = [
            {
                'template_id': ta.template_id,
                'display_id': ta.display_id,
                'maturity': ta.maturity,
                'relevance': ta.relevance_score,
                'key_references': ta.key_references[:3],
            }
            for ta in response.relevant_templates[:5]
        ]

        # QA-3: Evidence strength for ALL personas
        templates_raw = []
        for ta in response.relevant_templates[:5]:
            template = self.templates_by_id.get(ta.template_id)
            if template:
                templates_raw.append(template)
        if templates_raw:
            enrichment['evidence_strength'] = self.compute_evidence_strength(templates_raw)

        if persona == UserPersona.ARCHITECT:
            thresholds = []
            for ta in response.relevant_templates[:5]:
                template = self.templates_by_id.get(ta.template_id)
                if template:
                    thresholds.extend(self.extract_calibrated_thresholds(template))
            enrichment['thresholds'] = thresholds
            enrichment['n_thresholds'] = len(thresholds)

        elif persona == UserPersona.CLINICIAN:
            # GRADE ratings
            enrichment['grade_ratings'] = [
                {**self.map_to_grade(ta.maturity), 'template': ta.display_id}
                for ta in response.relevant_templates[:5]
                if hasattr(ta, 'maturity') and ta.maturity
            ]
            # Contraindications
            kws = set()
            how_text = response.how.lower()
            for kw in ['light', 'noise', 'open plan', 'enclosed', 'nature', 'contrast']:
                if kw in how_text:
                    kws.add(kw)
            enrichment['contraindications'] = self.find_contraindications(list(kws))

        elif persona == UserPersona.RESEARCHER:
            # QA-3: Full evidence layer
            enrichment['study_designs'] = enrichment.get('evidence_strength', {}).get('study_designs', [])
            enrichment['effect_sizes'] = enrichment.get('evidence_strength', {}).get('effect_sizes', [])
            enrichment['n_effect_sizes'] = len(enrichment.get('effect_sizes', []))

        elif persona == UserPersona.FACILITIES:
            outcomes = [k for k in self.SCIENTIFIC_TO_PROXY_METRICS.keys()
                        if k in response.how.lower()]
            enrichment['proxy_metrics'] = self.translate_to_proxy_metrics(outcomes)

        elif persona == UserPersona.STUDENT:
            full_text = f"{response.how} {response.why}"
            enrichment['glossary'] = self.get_glossary_for_terms(full_text)

        elif persona == UserPersona.POLICY:
            topics = set()
            for key in self.STANDARDS_REGISTRY.keys():
                if key in response.how.lower() or key in response.why.lower():
                    topics.add(key)
            enrichment['standards'] = self.find_relevant_standards(list(topics))

        # EN-0D: Inject annotations if service is available
        if self.annotation_service:
            try:
                template_ids = [
                    ta.display_id
                    for ta in response.relevant_templates[:5]
                    if hasattr(ta, 'display_id')
                ]
                annotations_data = []
                for tid in template_ids:
                    # Get SENSITIVITY_FLAGs for parameters
                    from src.services.annotation_service import AnnotationType
                    flags = self.annotation_service.get_parameter_sensitivity_flags(tid)
                    for f in flags:
                        annotations_data.append({
                            'type': 'SENSITIVITY_FLAG',
                            'target': f.target_id,
                            'content': f.content,
                            'confidence': f.confidence,
                        })
                    # Get OPEN_QUESTIONs
                    questions = self.annotation_service.get_template_annotations(
                        tid, types=[AnnotationType.OPEN_QUESTION]
                    )
                    for q in questions:
                        annotations_data.append({
                            'type': 'OPEN_QUESTION',
                            'target': q.target_id,
                            'content': q.content,
                        })
                if annotations_data:
                    enrichment['annotations'] = annotations_data
                    enrichment['n_annotations'] = len(annotations_data)
            except Exception as e:
                logger.debug(f"Annotation retrieval failed (non-fatal): {e}")

        return enrichment

    # =========================================================================
    # Sprint QA-5: Browse ↔ QA Integration
    # =========================================================================

    def generate_template_questions(
        self, template: Dict, max_questions: int = 5
    ) -> List[Dict[str, str]]:
        """
        Generate canonical questions that this template can answer.

        Sprint QA-5: Enables batch preprocessing — for each template,
        generate the questions a user might ask. These can be:
        1. Pre-computed at build time to populate a "suggested questions" UI
        2. Used as test queries for regression testing
        3. Indexed for search-as-you-type

        Design Decision DD-20: Generate questions from template structure
        (name, mechanism chain, scope conditions) rather than LLM. This is
        deterministic, auditable, and fast.
        """
        display_id = template.get('display_id', '?')
        name = template.get('name', 'Unknown')
        pattern = template.get('structural_pattern', '')
        principle = template.get('higher_order_principle', '')
        btypes = template.get('building_types', [])
        if isinstance(btypes, dict):
            btypes = list(btypes.keys())
        elif not isinstance(btypes, list):
            btypes = []
        mechanism = template.get('mechanism_chain', [])

        # Extract entities from mechanism chain
        entities = []
        if isinstance(mechanism, list):
            for step in mechanism:
                if isinstance(step, dict):
                    entities.append(step.get('from', ''))
                    entities.append(step.get('to', ''))
                elif isinstance(step, str):
                    entities.append(step)
        entities = [e.replace('_', ' ') for e in entities if e]

        questions = []

        # Q1: Direct "how does X affect Y?" from mechanism
        if len(entities) >= 2:
            questions.append({
                'question': f"How does {entities[0]} affect {entities[-1]}?",
                'type': 'mechanism',
                'template_source': display_id,
            })

        # Q2: "When does X matter?" from scope conditions
        if name:
            questions.append({
                'question': f"When does {name.lower()} matter?",
                'type': 'scope',
                'template_source': display_id,
            })

        # Q3: "What is the evidence for X?" — evidence query
        if name:
            questions.append({
                'question': f"What is the evidence for {name.lower()}?",
                'type': 'evidence',
                'template_source': display_id,
            })

        # Q4: Building type questions
        for bt in btypes[:2]:
            bt_clean = bt.replace('_', ' ') if isinstance(bt, str) else str(bt)
            questions.append({
                'question': f"How does this apply to {bt_clean}?",
                'type': 'application',
                'template_source': display_id,
            })

        # Q5: "What are the design implications of X?"
        if pattern:
            questions.append({
                'question': f"What are the design implications of {pattern.lower()[:60]}?",
                'type': 'design',
                'template_source': display_id,
            })

        return questions[:max_questions]

    def build_vocabulary_bridge(self) -> Dict[str, Any]:
        """
        Map Browse taxonomy (display_ids, domains, entities) to QA keywords.

        Sprint QA-5: The vocabulary bridge solves the problem that Browse
        and QA use different terminology. Browse has template IDs (CLE1, L4)
        and structured fields. QA has natural language keywords.

        Design Decision DD-21: Build a lookup table keyed by QA keywords
        that points to template display_ids. This enables:
        - "Did you mean template CLE1?" when user searches for "circadian"
        - Browse page showing related QA queries for each template
        """
        bridge: Dict[str, List[str]] = {}

        for tid, template in self.templates_by_id.items():
            if not isinstance(template, dict):
                continue

            display_id = template.get('display_id', tid)
            name = template.get('name', '').lower()
            pattern = template.get('structural_pattern', '').lower()
            principle = template.get('higher_order_principle', '').lower()

            # Extract keywords from template fields
            keywords = set()

            # From name
            for word in name.split():
                if len(word) > 3:  # Skip short words
                    keywords.add(word)

            # From mechanism_chain entities
            for step in template.get('mechanism_chain', []):
                if isinstance(step, dict):
                    for key in ['from', 'to']:
                        entity = step.get(key, '')
                        if entity:
                            keywords.add(entity.lower().replace('_', ' '))

            # From calibrated parameter names
            for param_name in template.get('calibrated_parameters', {}).keys():
                keywords.add(param_name.lower().replace('_', ' '))

            # Register each keyword → template mapping
            for kw in keywords:
                if kw not in bridge:
                    bridge[kw] = []
                if display_id not in bridge[kw]:
                    bridge[kw].append(display_id)

        return {
            'keyword_to_templates': bridge,
            'n_keywords': len(bridge),
            'n_templates_indexed': len(self.templates_by_id),
        }

    def get_related_templates_for_query(
        self,
        response: QueryResponse,
        max_related: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Find templates not in the response but related to the query topic.

        Sprint QA-5: Enables QA→Browse navigation. After answering a query,
        suggest other templates the user might want to browse.

        Design Decision DD-22: Use keyword overlap between the response's
        matched templates and all other templates to find neighbors. This is
        a simple but effective approach for small template libraries (<500).
        """
        # Collect entities from matched templates
        matched_ids = set(ta.template_id for ta in response.relevant_templates)
        matched_entities = set()

        for ta in response.relevant_templates:
            template = self.templates_by_id.get(ta.template_id, {})
            for step in template.get('mechanism_chain', []):
                if isinstance(step, dict):
                    matched_entities.add(step.get('from', '').lower())
                    matched_entities.add(step.get('to', '').lower())
            # Also add building types
            for bt in template.get('building_types', []):
                if isinstance(bt, str):
                    matched_entities.add(bt.lower())

        matched_entities.discard('')

        # Score all other templates by entity overlap
        candidates = []
        for tid, template in self.templates_by_id.items():
            if not isinstance(template, dict):
                continue
            if tid in matched_ids:
                continue

            template_entities = set()
            for step in template.get('mechanism_chain', []):
                if isinstance(step, dict):
                    template_entities.add(step.get('from', '').lower())
                    template_entities.add(step.get('to', '').lower())
            for bt in template.get('building_types', []):
                if isinstance(bt, str):
                    template_entities.add(bt.lower())
            template_entities.discard('')

            overlap = len(matched_entities & template_entities)
            if overlap > 0:
                candidates.append({
                    'template_id': tid,
                    'display_id': template.get('display_id', tid),
                    'name': template.get('name', ''),
                    'overlap_score': overlap,
                    'shared_entities': list(matched_entities & template_entities)[:5],
                    'maturity': template.get('calibration_status', ''),
                })

        candidates.sort(key=lambda x: -x['overlap_score'])
        return candidates[:max_related]

    def batch_generate_all_questions(self) -> List[Dict]:
        """
        Generate canonical questions for ALL templates.

        Sprint QA-5/Preprocessing: Produces a list of all questions
        that can be batch-processed for answers, enabling the
        "precompute all answers" workflow the user described.
        """
        all_questions = []
        for tid, template in self.templates_by_id.items():
            if not isinstance(template, dict):
                continue
            qs = self.generate_template_questions(template)
            all_questions.extend(qs)
        return all_questions

    # =========================================================================
    # Sprint QA-6: Creative Modes
    # =========================================================================

    def generate_grant_section(
        self, response: QueryResponse, funder: str = "NIH"
    ) -> Dict[str, Any]:
        """
        Generate a grant proposal evidence section from a QA response.

        Sprint QA-6: Composes structured grant text by synthesizing
        template evidence into the standard grant format (Significance,
        Innovation, Mechanism, Preliminary Data).

        Design Decision DD-23: Template-driven, not LLM-generated.
        The grant section cites actual template data, ensuring every
        claim is traceable to the evidence base.
        """
        templates_raw = []
        for ta in response.relevant_templates[:5]:
            template = self.templates_by_id.get(ta.template_id, {})
            if isinstance(template, dict):
                templates_raw.append(template)

        evidence_strength = self.compute_evidence_strength(templates_raw)
        effect_sizes = evidence_strength.get('effect_sizes', [])

        # Significance section
        significance = (
            f"This proposal addresses {response.query}, a question with "
            f"{evidence_strength['badge'].lower()} ({evidence_strength['template_count']} "
            f"converging lines of evidence). "
            f"The mechanism operates through: {response.how[:200]}"
        )

        # Innovation section
        gaps = response.research_gaps[:3] if response.research_gaps else [
            "Integration across architectural domains remains untested",
            "Dose-response relationships are poorly characterized",
        ]
        innovation = (
            f"Despite {evidence_strength['template_count']} templates documenting "
            f"this phenomenon, key gaps remain: {'; '.join(gaps[:2])}. "
            f"This project will fill these gaps through a novel integration of "
            f"environmental measurement with physiological monitoring."
        )

        # Preliminary data
        prelim_data = []
        for es in effect_sizes[:3]:
            prelim_data.append(
                f"{es['parameter']}: {es['value']} {es['unit'][:30]} "
                f"({es['magnitude']} effect, source: {es['template_source']})"
            )

        # References
        references = []
        for ta in response.relevant_templates[:5]:
            for ref in ta.key_references[:2]:
                references.append(ref)

        return {
            'funder': funder,
            'significance': significance,
            'mechanism': response.how[:300],
            'innovation': innovation,
            'preliminary_data': prelim_data,
            'effect_sizes': effect_sizes[:5],
            'evidence_badge': evidence_strength['badge'],
            'references': references[:10],
            'caveats': response.caveats[:3],
            'provenance': {
                'templates_used': [ta.display_id for ta in response.relevant_templates[:5]],
                'n_templates': evidence_strength['template_count'],
                'generated_from': 'ATLAS template library v1',
            },
        }

    def accelerate_systematic_review(
        self, topic: str
    ) -> Dict[str, Any]:
        """
        Generate systematic review components for a research topic.

        Sprint QA-6: Produces PICO components, search strategy,
        inclusion/exclusion criteria, and quality assessment framework
        from the template library.

        Design Decision DD-24: The template library IS effectively a
        curated systematic review of the built environment → wellbeing
        literature. We can extract its structure to accelerate a formal
        systematic review.
        """
        # First run a query to find relevant templates
        response = self.query(topic)

        templates_raw = []
        for ta in response.relevant_templates[:5]:
            template = self.templates_by_id.get(ta.template_id, {})
            if isinstance(template, dict):
                templates_raw.append(template)

        # Extract PICO components
        populations = set()
        interventions = set()
        outcomes = set()
        for t in templates_raw:
            for mod in t.get('moderators', []):
                if isinstance(mod, str):
                    populations.add(mod)
            for step in t.get('mechanism_chain', []):
                if isinstance(step, dict):
                    interventions.add(step.get('from', '').replace('_', ' '))
                    outcomes.add(step.get('to', '').replace('_', ' '))
        populations.discard('')
        interventions.discard('')
        outcomes.discard('')

        # Extract building types as settings
        settings = set()
        for t in templates_raw:
            btypes = t.get('building_types', [])
            if isinstance(btypes, dict):
                btypes = list(btypes.keys())
            for bt in (btypes if isinstance(btypes, list) else []):
                settings.add(str(bt).replace('_', ' '))

        # Search strategy
        search_terms = list(interventions)[:5] + list(outcomes)[:5]
        search_string = ' OR '.join(f'"{term}"' for term in search_terms[:8])

        # Inclusion/exclusion
        evidence = self.compute_evidence_strength(templates_raw)
        maturity_levels = [sd['maturity_source'] for sd in evidence.get('study_designs', [])]

        return {
            'topic': topic,
            'pico': {
                'population': list(populations)[:8],
                'intervention': list(interventions)[:8],
                'comparison': ['standard conditions', 'pre-intervention baseline'],
                'outcome': list(outcomes)[:8],
            },
            'settings': list(settings),
            'search_strategy': {
                'databases': ['PubMed', 'PsycINFO', 'Web of Science', 'Scopus', 'CINAHL'],
                'search_string': search_string,
                'n_existing_templates': len(templates_raw),
            },
            'inclusion_criteria': [
                'Peer-reviewed empirical study',
                'Measured built environment parameter as independent variable',
                'Human participants',
                f'Settings: {", ".join(list(settings)[:4])}',
            ],
            'exclusion_criteria': [
                'Reviews or commentaries (use for background only)',
                'Studies without quantitative outcome measures',
                'Non-Western settings (consider separately for generalizability)',
            ],
            'quality_assessment': {
                'tool': 'Modified Newcastle-Ottawa Scale',
                'maturity_levels_found': maturity_levels,
                'evidence_badge': evidence['badge'],
            },
            'existing_evidence': {
                'effect_sizes': evidence.get('effect_sizes', [])[:5],
                'key_references': [
                    ref for ta in response.relevant_templates[:3]
                    for ref in ta.key_references[:2]
                ],
            },
            'provenance': {
                'method': 'ATLAS template library systematic extraction',
                'templates_analyzed': len(templates_raw),
                'generated_from': 'ATLAS v1',
            },
        }

    DISCIPLINE_FRAMES = {
        'architecture': {
            'vocabulary': {
                'effect': 'design impact', 'mechanism': 'design principle',
                'variable': 'design parameter', 'outcome': 'occupant experience',
                'evidence': 'post-occupancy evaluation',
            },
            'framing': "From an architectural perspective",
        },
        'psychology': {
            'vocabulary': {
                'effect': 'cognitive/affective effect', 'mechanism': 'psychological process',
                'variable': 'environmental variable', 'outcome': 'behavioral outcome',
                'evidence': 'experimental evidence',
            },
            'framing': "From a psychological perspective",
        },
        'neuroscience': {
            'vocabulary': {
                'effect': 'neural response', 'mechanism': 'neural pathway',
                'variable': 'stimulus parameter', 'outcome': 'brain state change',
                'evidence': 'neuroimaging/electrophysiological evidence',
            },
            'framing': "From a neuroscience perspective",
        },
        'public_health': {
            'vocabulary': {
                'effect': 'health outcome', 'mechanism': 'exposure pathway',
                'variable': 'environmental determinant', 'outcome': 'population health indicator',
                'evidence': 'epidemiological evidence',
            },
            'framing': "From a public health perspective",
        },
        'environmental_design': {
            'vocabulary': {
                'effect': 'environmental impact', 'mechanism': 'design strategy',
                'variable': 'spatial parameter', 'outcome': 'user wellbeing metric',
                'evidence': 'design research evidence',
            },
            'framing': "From an environmental design perspective",
        },
    }

    def translate_across_disciplines(
        self, response: QueryResponse, target_discipline: str = 'architecture'
    ) -> Dict[str, Any]:
        """
        Translate a QA response into the vocabulary of a target discipline.

        Sprint QA-6: Addresses the interdisciplinary nature of the project.
        The same finding about "light → circadian entrainment → sleep quality"
        means different things to an architect, psychologist, and epidemiologist.

        Design Decision DD-25: Use a static vocabulary mapping per discipline.
        Each discipline gets: reframed headline, reframed mechanism,
        discipline-specific implications, and translated terminology.
        """
        frame = self.DISCIPLINE_FRAMES.get(
            target_discipline,
            self.DISCIPLINE_FRAMES['architecture']
        )
        vocab = frame['vocabulary']

        # Reframe headline
        headline = response.headline
        for generic, specific in vocab.items():
            headline = headline.replace(generic, specific)

        # Reframe mechanism
        mechanism = response.how
        for generic, specific in vocab.items():
            mechanism = mechanism.replace(generic, specific)

        # Discipline-specific implications
        implications = []
        if target_discipline == 'architecture':
            implications = [
                f"Design parameter: {response.when[0][:60]}..." if response.when else "No scope conditions specified",
                f"Confidence for code compliance: {response.overall_confidence:.0%}",
            ]
        elif target_discipline == 'psychology':
            implications = [
                f"Individual differences: {response.for_whom[0][:60]}..." if response.for_whom else "No moderators specified",
                f"Effect robustness: {response.overall_confidence:.0%}",
            ]
        elif target_discipline == 'neuroscience':
            if response.neuroscience_details:
                for nd in response.neuroscience_details[:2]:
                    implications.append(f"Neural substrate: {nd.neural_substrate or 'TBD'}")
            else:
                implications.append("Neural substrates not yet mapped for this template")
        elif target_discipline == 'public_health':
            implications = [
                f"Population scope: {', '.join(response.for_whom[:2])}" if response.for_whom else "General population",
                f"Evidence strength for policy: {response.overall_confidence:.0%}",
            ]

        return {
            'target_discipline': target_discipline,
            'framing': frame['framing'],
            'headline': headline,
            'mechanism': mechanism[:300],
            'implications': implications,
            'vocabulary_mapping': vocab,
            'original_confidence': response.overall_confidence,
            'provenance': {
                'translation_method': 'ATLAS discipline vocabulary mapping v1',
                'source_templates': [ta.display_id for ta in response.relevant_templates[:5]],
            },
        }


# =============================================================================

def ask(question: str, verbose: bool = True) -> QueryResponse:
    """
    Convenience function to query the template library.

    Usage:
        from src.services.template_query_service import ask
        response = ask("When do high ceilings increase creativity?")
    """
    service = TemplateQueryService()
    response = service.query(question)

    if verbose:
        print(service.format_response(response))

    return response


if __name__ == "__main__":
    # Demo query
    response = ask("When do high ceilings increase creativity and for whom?")
