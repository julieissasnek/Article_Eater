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
import os
import re
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
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

    def __init__(self, templates_dir: str = "data/templates"):
        self.templates_dir = Path(templates_dir)
        self.templates: Dict[str, Dict] = {}
        self.templates_by_id: Dict[str, Dict] = {}
        self.display_id_map: Dict[str, str] = {}  # display_id → template_id
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

        # Evidence
        lines.append("KEY EVIDENCE:")
        for ref in response.key_evidence[:3]:
            lines.append(f"  • {ref[:80]}...")

        return "\n".join(lines)


# =============================================================================
# CONVENIENCE FUNCTION
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
