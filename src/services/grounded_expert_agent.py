"""
Grounded Expert Agent — Domain Expert with Source Citations
=============================================================

Created: 2026-02-16
Updated: 2026-02-16 — Added recursive explanatory depth
Purpose: A domain expert that answers questions using ONLY grounded sources

DESIGN PRINCIPLES:
1. NO MADE UP STUFF — everything must be traceable to a source document
2. CITABLE — every claim includes its source (panel doc, template, paper)
3. HUMBLE — admits when it doesn't know or evidence is weak
4. INTERACTIVE — can answer follow-up questions
5. RETRIEVABLE — finds relevant passages from source documents
6. RECURSIVE — can go deeper into WHY at each level

RECURSIVE EXPLANATION (NEW):
Theories explain WHY. The system provides progressive explanatory depth:

  LEVEL 0 (WHAT):  High ceilings increase creativity
  LEVEL 1 (HOW):   via reduced enclosure-threat → broadened cognition
  LEVEL 2 (WHY):   The brain has dual processing modes; spatial proportion
                   modulates which mode is active
  LEVEL 3 (NEURAL): Amygdala enclosure-threat assessment, DMN/TPN balance,
                    attentional scope regulation
  LEVEL 4 (THEORY): Predictive Processing — brain predicts spatial affordances;
                    enclosure violates predictions of action-space
  LEVEL 5 (EVOLUTIONARY): Why the brain evolved enclosure-sensitivity in the
                          first place (shelter-seeking, predator detection)

Each level references the level above it, creating a traceable chain.
The system follows template `interactions` to traverse this hierarchy.

SOURCE HIERARCHY:
1. Panel documents (docs/*.md) — primary source of expert reasoning
2. Templates (data/templates/*.json) — encoded mechanisms and calibration
3. Key references — cited papers in templates
4. Extracted claims — from WebOfBelief (when available)

WHAT THE AGENT WILL NOT DO:
- Make up mechanisms not in the templates
- Invent citations
- Claim certainty where evidence is weak
- Answer questions outside its knowledge base without saying so
"""

import json
import re
import sqlite3
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Tuple, Set
from collections import defaultdict

logger = logging.getLogger(__name__)

try:
    from src.services.incremental_bn import get_edge_estimate
except Exception:  # pragma: no cover - optional dependency path
    get_edge_estimate = None


from enum import Enum
from src.services.db_locator import resolve_web_db


class ExplanationLevel(Enum):
    """Levels of explanatory depth."""
    WHAT = 0       # Empirical finding: "X does Y"
    HOW = 1        # Mechanism: "via A → B → C"
    WHY = 2        # Principle: "because the brain operates in mode Z"
    NEURAL = 3     # Neural: "involving amygdala, prefrontal cortex..."
    THEORY = 4     # T1 Framework: "Predictive Processing explains this as..."
    EVOLUTIONARY = 5  # Deep why: "evolved to detect..."


@dataclass
class ExplanatoryLayer:
    """One layer of explanation."""
    level: ExplanationLevel
    explanation: str
    sources: List['SourcePassage']
    connects_to: Optional[str] = None  # Template ID that goes deeper
    framework: Optional[str] = None    # T1 framework if THEORY level


@dataclass
class RecursiveExplanation:
    """A multi-level explanation that recurses through WHY."""
    query: str
    layers: List[ExplanatoryLayer]
    deepest_level: ExplanationLevel
    chain: List[str]  # Template IDs traversed
    has_more_depth: bool  # Can we go even deeper?
    unexplored_branches: List[str]  # Related templates not yet explored


@dataclass
class SourcePassage:
    """A passage from a source document."""
    source_type: str  # 'panel', 'template', 'reference'
    source_id: str    # Document filename or template ID
    source_name: str  # Human-readable name
    content: str      # The actual passage
    relevance: float  # 0-1 relevance score
    section: str      # Section within document (if applicable)


@dataclass
class GroundedClaim:
    """A claim with its source grounding."""
    claim: str
    confidence: str  # 'high', 'moderate', 'low', 'speculative'
    sources: List[SourcePassage]
    caveats: List[str]


@dataclass
class ExpertResponse:
    """Response from the grounded expert agent."""
    query: str
    short_answer: str
    grounded_claims: List[GroundedClaim]
    source_summary: str  # "Based on Panel VF-I, Template VF3, and 2 papers"
    knowledge_gaps: List[str]  # What we don't know
    follow_up_questions: List[str]  # Questions the expert suggests
    confidence_statement: str  # Overall confidence with justification
    bn_calibration: Optional[Dict[str, Any]] = None  # BN posterior calibration if available


class GroundedExpertAgent:
    """
    A domain expert that answers questions using ONLY grounded sources.

    The agent has access to:
    - Panel documents (the original expert discussions)
    - Encoded templates (mechanisms, scope conditions, moderators)
    - Key references (cited papers)

    Everything the agent says can be traced back to a source.
    """

    def __init__(
        self,
        panels_dir: str = "docs",
        templates_dir: str = "data/templates",
        web_db_path: str | None = None,
        web_id: str = "master:web:accumulated",
    ):
        self.panels_dir = Path(panels_dir)
        self.templates_dir = Path(templates_dir)
        if web_db_path:
            self.web_db_path = Path(web_db_path)
        else:
            try:
                self.web_db_path = resolve_web_db(prefer="integrated")
            except Exception:
                self.web_db_path = Path("data/web_persistence.db")
        self.web_id = web_id

        # Knowledge base
        self.panels: Dict[str, str] = {}  # filename → content
        self.panel_index: Dict[str, List[str]] = defaultdict(list)  # keyword → [filenames]
        self.templates: Dict[str, Dict] = {}
        self.template_aliases: Dict[str, str] = {}  # alias/template_id/file stem -> canonical display_id
        self.template_index: Dict[str, List[str]] = defaultdict(list)
        self.empirical_claims: List[Dict[str, Any]] = []
        self.empirical_by_id: Dict[str, Dict[str, Any]] = {}
        self.empirical_index: Dict[str, List[int]] = defaultdict(list)
        self._empirical_loaded = False

        # Load knowledge
        self._load_panels()
        self._load_templates()
        self._build_index()

    def _load_panels(self):
        """Load all panel documents."""
        if not self.panels_dir.exists():
            logger.warning(f"Panels directory not found: {self.panels_dir}")
            return

        for f in self.panels_dir.glob("*Panel*.md"):
            try:
                content = f.read_text(encoding='utf-8')
                self.panels[f.name] = content
            except Exception as e:
                logger.warning(f"Failed to load panel {f}: {e}")

        logger.info(f"Loaded {len(self.panels)} panel documents")

    def _load_templates(self):
        """Load all templates."""
        if not self.templates_dir.exists():
            logger.warning(f"Templates directory not found: {self.templates_dir}")
            return

        for f in self.templates_dir.glob("*.json"):
            try:
                with open(f) as fp:
                    template = json.load(fp)
                    display_id = str(template.get('display_id') or template.get('template_id') or f.stem)
                    self.templates[display_id] = template

                    # Support mixed ID references across files (display_id vs template_id vs filename).
                    aliases = {
                        display_id,
                        str(template.get('template_id') or '').strip(),
                        f.stem,
                    }
                    for alias in aliases:
                        if not alias:
                            continue
                        existing = self.template_aliases.get(alias)
                        if existing and existing != display_id:
                            logger.debug(
                                "Template alias collision for %s: keeping %s, ignoring %s",
                                alias,
                                existing,
                                display_id,
                            )
                            continue
                        self.template_aliases[alias] = display_id
            except Exception as e:
                logger.warning(f"Failed to load template {f}: {e}")

        logger.info(f"Loaded {len(self.templates)} templates")

    def _resolve_template_id(self, template_ref: str) -> Optional[str]:
        """Resolve a template reference (display_id/template_id/file stem) to canonical display_id."""
        if not template_ref:
            return None
        if template_ref in self.templates:
            return template_ref
        return self.template_aliases.get(template_ref)

    def _build_index(self):
        """Build keyword index for retrieval."""
        # Index panels
        for filename, content in self.panels.items():
            # Extract words
            words = set(re.findall(r'\b\w{4,}\b', content.lower()))
            for word in words:
                self.panel_index[word].append(filename)

        # Index templates
        for tid, template in self.templates.items():
            searchable = ' '.join([
                str(template.get('name', '')),
                str(template.get('structural_pattern', '')),
                str(template.get('higher_order_principle', '')),
                str(template.get('short_description', '')),
            ]).lower()
            words = set(re.findall(r'\b\w{4,}\b', searchable))
            for word in words:
                self.template_index[word].append(tid)

    def _load_empirical_claims(self, max_claims: int = 5000) -> None:
        """Load empirical/observational beliefs from persisted WebOfBelief SQLite."""
        if self._empirical_loaded:
            return
        self._empirical_loaded = True

        if not self.web_db_path or not self.web_db_path.exists():
            return

        try:
            with sqlite3.connect(str(self.web_db_path)) as conn:
                rows = conn.execute(
                    """
                    SELECT belief_id, content, credence_value, paper_ids, environment_id, outcome_id
                    FROM beliefs
                    WHERE web_id = ? AND level IN ('empirical', 'observational')
                    ORDER BY credence_value DESC, updated_at DESC
                    LIMIT ?
                    """,
                    (self.web_id, max_claims),
                ).fetchall()
        except Exception as exc:
            logger.warning("Failed loading empirical claims from %s: %s", self.web_db_path, exc)
            return

        for row in rows:
            belief_id, content, credence, paper_ids_raw, environment_id, outcome_id = row
            paper_ids: List[str] = []
            if paper_ids_raw:
                try:
                    parsed = json.loads(paper_ids_raw)
                    if isinstance(parsed, list):
                        paper_ids = [str(p) for p in parsed if p]
                except Exception:
                    paper_ids = []

            entry = {
                "belief_id": str(belief_id or ""),
                "content": str(content or ""),
                "credence": float(credence or 0.0),
                "paper_ids": paper_ids,
                "environment_id": str(environment_id or ""),
                "outcome_id": str(outcome_id or ""),
            }
            idx = len(self.empirical_claims)
            self.empirical_claims.append(entry)
            if entry["belief_id"]:
                self.empirical_by_id[entry["belief_id"]] = entry

            searchable = " ".join(
                [
                    entry["content"],
                    entry["environment_id"],
                    entry["outcome_id"],
                    " ".join(entry["paper_ids"]),
                ]
            ).lower()
            words = set(re.findall(r"\b\w{4,}\b", searchable))
            for word in words:
                self.empirical_index[word].append(idx)

    def _retrieve_empirical_passages(
        self,
        keywords: List[str],
        max_passages: int = 5
    ) -> List[SourcePassage]:
        """Retrieve relevant empirical findings from persisted web beliefs."""
        self._load_empirical_claims()
        if not keywords or not self.empirical_claims:
            return []

        claim_scores: Dict[int, int] = defaultdict(int)
        for kw in keywords:
            for idx in self.empirical_index.get(kw, []):
                claim_scores[idx] += 1

        ranked = sorted(
            claim_scores.items(),
            key=lambda item: (-item[1], -self.empirical_claims[item[0]].get("credence", 0.0)),
        )[:max_passages]

        passages: List[SourcePassage] = []
        for idx, score in ranked:
            claim = self.empirical_claims[idx]
            paper_hint = claim["paper_ids"][0] if claim["paper_ids"] else "unknown_paper"
            passages.append(
                SourcePassage(
                    source_type="empirical",
                    source_id=claim["belief_id"],
                    source_name=f"Empirical belief ({paper_hint})",
                    content=claim["content"][:500],
                    relevance=score / len(keywords) if keywords else 0.0,
                    section=f"credence={claim['credence']:.2f}",
                )
            )
        return passages

    def _compute_bn_calibration(self, empirical_passages: List[SourcePassage]) -> Optional[Dict[str, Any]]:
        """
        Calibrate confidence using BN posterior estimates for matched env→outcome edges.

        Returns None when BN integration is unavailable.
        """
        if get_edge_estimate is None:
            return None
        if not empirical_passages:
            return None

        edge_posteriors: List[Dict[str, Any]] = []
        seen_edges: Set[Tuple[str, str]] = set()

        for passage in empirical_passages:
            claim = self.empirical_by_id.get(passage.source_id)
            if not claim:
                continue

            env_id = claim.get("environment_id", "")
            outcome_id = claim.get("outcome_id", "")
            if not env_id or not outcome_id:
                continue

            edge_key = (env_id, outcome_id)
            if edge_key in seen_edges:
                continue
            seen_edges.add(edge_key)

            try:
                posterior = get_edge_estimate(env_id, outcome_id)
            except Exception:
                posterior = None
            if posterior is None:
                continue

            edge_posteriors.append(
                {
                    "source": env_id,
                    "target": outcome_id,
                    "posterior": round(float(posterior), 4),
                }
            )

        if not edge_posteriors:
            return {
                "status": "no_matching_bn_edges",
                "n_edges_calibrated": 0,
                "edge_posteriors": [],
            }

        mean_posterior = sum(e["posterior"] for e in edge_posteriors) / len(edge_posteriors)
        return {
            "status": "calibrated",
            "n_edges_calibrated": len(edge_posteriors),
            "mean_posterior": round(mean_posterior, 4),
            "edge_posteriors": edge_posteriors[:5],
        }

    def _extract_keywords(self, query: str) -> List[str]:
        """Extract keywords from a query."""
        stop_words = {
            'what', 'when', 'where', 'which', 'who', 'whom', 'whose',
            'why', 'how', 'does', 'this', 'that', 'these', 'those',
            'about', 'from', 'with', 'have', 'been', 'being', 'would',
            'could', 'should', 'will', 'shall', 'might', 'must', 'need',
            'affect', 'effect', 'cause', 'make', 'help', 'work', 'does'
        }
        words = re.findall(r'\b\w{3,}\b', query.lower())
        return [w for w in words if w not in stop_words]

    def _retrieve_panel_passages(
        self,
        keywords: List[str],
        max_passages: int = 5
    ) -> List[SourcePassage]:
        """Retrieve relevant passages from panel documents."""
        passages = []

        # Score panels by keyword overlap
        panel_scores = defaultdict(int)
        for kw in keywords:
            for filename in self.panel_index.get(kw, []):
                panel_scores[filename] += 1

        # Get top panels
        top_panels = sorted(panel_scores.items(), key=lambda x: -x[1])[:3]

        for filename, score in top_panels:
            content = self.panels.get(filename, '')
            if not content:
                continue

            # Find relevant sections
            sections = re.split(r'\n##+ ', content)
            for section in sections:
                # Score section
                section_lower = section.lower()
                section_score = sum(1 for kw in keywords if kw in section_lower)

                if section_score > 0:
                    # Extract first few sentences
                    lines = section.split('\n')
                    title = lines[0] if lines else "Untitled section"
                    passage_content = '\n'.join(lines[1:6]) if len(lines) > 1 else section[:500]

                    passages.append(SourcePassage(
                        source_type='panel',
                        source_id=filename,
                        source_name=filename.replace('.md', '').replace('_', ' '),
                        content=passage_content[:500],
                        relevance=section_score / len(keywords) if keywords else 0,
                        section=title[:100]
                    ))

        # Sort by relevance and limit
        passages.sort(key=lambda x: -x.relevance)
        return passages[:max_passages]

    def _retrieve_template_content(
        self,
        keywords: List[str],
        max_templates: int = 3
    ) -> List[SourcePassage]:
        """Retrieve relevant content from templates."""
        passages = []

        # Score templates
        template_scores = defaultdict(int)
        for kw in keywords:
            for tid in self.template_index.get(kw, []):
                template_scores[tid] += 1

        # Get top templates
        top_templates = sorted(template_scores.items(), key=lambda x: -x[1])[:max_templates]

        for tid, score in top_templates:
            template = self.templates.get(tid, {})
            if not template:
                continue

            # Extract key content
            content_parts = []

            # Name and description
            content_parts.append(f"MECHANISM: {template.get('name', 'Unknown')}")

            # Structural pattern
            if template.get('structural_pattern'):
                content_parts.append(f"PATTERN: {template['structural_pattern'][:300]}")

            # Higher order principle
            if template.get('higher_order_principle'):
                content_parts.append(f"PRINCIPLE: {template['higher_order_principle'][:300]}")

            # Scope conditions
            if template.get('scope_conditions'):
                conditions = template['scope_conditions'][:3]
                content_parts.append(f"CONDITIONS: " + "; ".join(str(c)[:100] for c in conditions))

            # Moderators
            if template.get('moderators'):
                mods = template['moderators'][:3]
                content_parts.append(f"MODERATORS: " + "; ".join(str(m)[:100] for m in mods))

            # Calibration parameters (if available)
            if template.get('calibration_parameters'):
                content_parts.append("CALIBRATION: See template for quantitative parameters")

            passages.append(SourcePassage(
                source_type='template',
                source_id=tid,
                source_name=template.get('name', tid)[:60],
                content='\n'.join(content_parts),
                relevance=score / len(keywords) if keywords else 0,
                section=template.get('display_id', tid)
            ))

        return passages

    def _retrieve_references(
        self,
        template_ids: List[str],
        max_refs: int = 5
    ) -> List[SourcePassage]:
        """Retrieve key references from templates."""
        passages = []
        seen = set()

        for tid in template_ids:
            resolved_tid = self._resolve_template_id(tid) or tid
            template = self.templates.get(resolved_tid, {})
            refs = template.get('key_references', [])

            for ref in refs:
                if isinstance(ref, dict):
                    citation = ref.get('citation', str(ref))
                else:
                    citation = str(ref)

                # Deduplicate
                key = citation[:50]
                if key in seen:
                    continue
                seen.add(key)

                passages.append(SourcePassage(
                    source_type='reference',
                    source_id=citation[:50],
                    source_name=citation[:80],
                    content=citation,
                    relevance=0.8,  # References are inherently relevant
                    section='Bibliography'
                ))

        return passages[:max_refs]

    def _assess_confidence(
        self,
        passages: List[SourcePassage],
        templates_found: int
    ) -> Tuple[str, str]:
        """Assess overall confidence and provide justification."""
        panel_passages = [p for p in passages if p.source_type == 'panel']
        template_passages = [p for p in passages if p.source_type == 'template']
        empirical_passages = [p for p in passages if p.source_type == 'empirical']

        if templates_found == 0 and len(panel_passages) == 0 and len(empirical_passages) == 0:
            return 'low', "Limited evidence: no directly relevant templates, panel discussions, or empirical findings found"

        if templates_found >= 2 and len(panel_passages) >= 2:
            return 'high', f"Strong evidence: {templates_found} templates and {len(panel_passages)} panel sections support this"

        if len(empirical_passages) >= 3 and (templates_found >= 1 or len(panel_passages) >= 1):
            return 'high', (
                f"Strong evidence: {len(empirical_passages)} empirical findings plus "
                f"{templates_found} template(s)/{len(panel_passages)} panel section(s)"
            )

        if len(empirical_passages) >= 1 and templates_found == 0:
            return 'moderate', f"Moderate evidence: {len(empirical_passages)} empirical finding(s) from accumulated web"

        if templates_found >= 1 or len(panel_passages) >= 1:
            return 'moderate', f"Moderate evidence: {templates_found} template(s) and {len(panel_passages)} panel section(s)"

        return 'low', "Limited evidence found in knowledge base"

    def _maturity_to_claim_confidence(self, maturity: str) -> str:
        """Map template maturity labels into claim confidence buckets."""
        m = (maturity or '').strip().lower()
        if not m:
            return 'low'
        if m in {'established', 'high', 'validated'}:
            return 'high'
        if m in {'supported', 'supported_preliminary', 'provisional', 'moderate'}:
            return 'moderate'
        if m in {'preliminary', 'speculative', 'how-possibly', 'low'}:
            return 'low'
        if 'supported' in m:
            return 'moderate'
        return 'low'

    def _identify_knowledge_gaps(
        self,
        keywords: List[str],
        passages: List[SourcePassage]
    ) -> List[str]:
        """Identify what we don't know about this topic."""
        gaps = []

        # Check which keywords weren't well-covered
        covered_keywords = set()
        for passage in passages:
            for kw in keywords:
                if kw in passage.content.lower():
                    covered_keywords.add(kw)

        uncovered = set(keywords) - covered_keywords
        if uncovered:
            gaps.append(f"Limited information on: {', '.join(list(uncovered)[:3])}")

        # Check template maturity
        for passage in passages:
            if passage.source_type == 'template':
                template = self.templates.get(passage.source_id, {})
                maturity = template.get('overall_maturity', template.get('maturity', ''))
                if maturity in ['preliminary', 'speculative', 'how-possibly']:
                    gaps.append(f"{passage.source_id}: Mechanism is {maturity} — needs more research")

        # Check for calibration
        has_calibration = any(
            self.templates.get(p.source_id, {}).get('calibration_parameters')
            for p in passages if p.source_type == 'template'
        )
        if not has_calibration:
            gaps.append("Quantitative calibration (thresholds, dose-response) not yet established")

        return gaps[:5]

    def _suggest_follow_ups(
        self,
        query: str,
        passages: List[SourcePassage]
    ) -> List[str]:
        """Suggest follow-up questions based on what was found."""
        suggestions = []

        # Look for related templates
        template_ids = [p.source_id for p in passages if p.source_type == 'template']
        related = set()
        for tid in template_ids:
            template = self.templates.get(tid, {})
            interactions = template.get('interactions', [])
            for ix in interactions:
                if isinstance(ix, dict):
                    rel_id = ix.get('display_id', '')
                    if rel_id:
                        related.add(rel_id)

        if related:
            suggestions.append(f"How does this interact with {', '.join(list(related)[:3])}?")

        # Standard follow-ups based on content
        suggestions.extend([
            "What are the individual differences in response?",
            "What's the time course of this effect?",
            "Does this replicate in different populations/cultures?",
            "What's the minimum threshold for this effect?",
        ])

        return suggestions[:4]

    def ask(
        self,
        query: str,
        verbose: bool = False
    ) -> ExpertResponse:
        """
        Ask the expert agent a question.

        The agent will:
        1. Retrieve relevant passages from panels, templates, and references
        2. Construct a grounded answer with citations
        3. Identify knowledge gaps
        4. Suggest follow-up questions

        Args:
            query: The question to answer
            verbose: Whether to print the response

        Returns:
            ExpertResponse with grounded claims and source citations
        """
        keywords = self._extract_keywords(query)

        # Retrieve from all sources
        panel_passages = self._retrieve_panel_passages(keywords)
        template_passages = self._retrieve_template_content(keywords)
        empirical_passages = self._retrieve_empirical_passages(keywords)

        # Get references from relevant templates
        template_ids = [p.source_id for p in template_passages]
        reference_passages = self._retrieve_references(template_ids)

        # Combine all passages
        all_passages = panel_passages + template_passages + empirical_passages + reference_passages

        # Build grounded claims
        claims = []

        # Claim from templates (mechanism)
        if template_passages:
            top_template = template_passages[0]
            template = self.templates.get(top_template.source_id, {})

            claims.append(GroundedClaim(
                claim=f"The mechanism involves: {template.get('name', 'unknown mechanism')}",
                confidence=self._maturity_to_claim_confidence(
                    str(template.get('overall_maturity') or template.get('maturity') or '')
                ),
                sources=[top_template],
                caveats=[
                    f"Maturity: {template.get('overall_maturity') or template.get('maturity') or 'unknown'}"
                ]
            ))

            # Scope conditions
            if template.get('scope_conditions'):
                claims.append(GroundedClaim(
                    claim="This effect applies under specific conditions",
                    confidence='moderate',
                    sources=[top_template],
                    caveats=[str(c)[:100] for c in template.get('scope_conditions', [])[:3]]
                ))

            # Moderators
            if template.get('moderators'):
                claims.append(GroundedClaim(
                    claim="Individual differences and context modulate this effect",
                    confidence='moderate',
                    sources=[top_template],
                    caveats=[str(m)[:100] for m in template.get('moderators', [])[:3]]
                ))

        # Claim from panels (expert discussion)
        if panel_passages:
            claims.append(GroundedClaim(
                claim="Expert panel discussion provides additional context",
                confidence='high',
                sources=panel_passages[:2],
                caveats=["See panel document for full discussion"]
            ))

        # Claim from empirical findings (WebOfBelief accumulation)
        if empirical_passages:
            claims.append(
                GroundedClaim(
                    claim="Empirical findings in the accumulated web provide direct evidence for this topic",
                    confidence='moderate',
                    sources=empirical_passages[:3],
                    caveats=["Empirical evidence quality varies by source paper and extraction quality"],
                )
            )

        # Assess confidence
        conf_level, conf_statement = self._assess_confidence(
            all_passages, len(template_passages)
        )
        bn_calibration = self._compute_bn_calibration(empirical_passages)
        if bn_calibration and bn_calibration.get("n_edges_calibrated", 0) > 0:
            conf_statement = (
                f"{conf_statement}; BN calibration: {bn_calibration['n_edges_calibrated']} edge(s), "
                f"mean posterior {bn_calibration['mean_posterior']:.2f}"
            )

        # Generate short answer
        if template_passages:
            top = self.templates.get(template_passages[0].source_id, {})
            short_answer = top.get('short_description', top.get('name', 'See detailed response'))[:200]
        elif empirical_passages:
            short_answer = empirical_passages[0].content[:200]
        else:
            short_answer = "Limited information available on this specific question"

        # Source summary
        source_parts = []
        if panel_passages:
            source_parts.append(f"{len(panel_passages)} panel section(s)")
        if template_passages:
            source_parts.append(f"{len(template_passages)} template(s)")
        if empirical_passages:
            source_parts.append(f"{len(empirical_passages)} empirical claim(s)")
        if reference_passages:
            source_parts.append(f"{len(reference_passages)} reference(s)")
        source_summary = f"Based on: {', '.join(source_parts)}" if source_parts else "No direct sources found"

        response = ExpertResponse(
            query=query,
            short_answer=short_answer,
            grounded_claims=claims,
            source_summary=source_summary,
            knowledge_gaps=self._identify_knowledge_gaps(keywords, all_passages),
            follow_up_questions=self._suggest_follow_ups(query, all_passages),
            confidence_statement=conf_statement,
            bn_calibration=bn_calibration,
        )

        if verbose:
            print(self.format_response(response))

        return response

    # =========================================================================
    # T1 FRAMEWORK MAPPING
    # =========================================================================

    T1_FRAMEWORKS = {
        'PP': {
            'name': 'Predictive Processing',
            'explains': 'How the brain minimizes prediction error through hierarchical models',
            'key_concepts': ['prediction error', 'precision weighting', 'active inference'],
        },
        'SN': {
            'name': 'Spatial Navigation / Cognitive Mapping',
            'explains': 'How hippocampal place cells and grid cells encode space',
            'key_concepts': ['cognitive map', 'place cells', 'spatial memory'],
        },
        'DP': {
            'name': 'Dual-Process Theory',
            'explains': 'How System 1 (fast/intuitive) and System 2 (slow/deliberate) interact',
            'key_concepts': ['automatic processing', 'controlled processing', 'fluency'],
        },
        'DT': {
            'name': 'DMN/TPN Dynamics',
            'explains': 'How Default Mode and Task-Positive networks toggle',
            'key_concepts': ['mind-wandering', 'attentional focus', 'spontaneous thought'],
        },
        'NM': {
            'name': 'Neuromodulatory Systems',
            'explains': 'How dopamine, serotonin, norepinephrine regulate cognition/affect',
            'key_concepts': ['reward prediction', 'arousal', 'motivation'],
        },
        'IC': {
            'name': 'Interoceptive / Constructionist Affect',
            'explains': 'How bodily signals are integrated into emotional experience',
            'key_concepts': ['interoception', 'constructed emotion', 'allostasis'],
        },
        'MS': {
            'name': 'Memory Systems',
            'explains': 'How episodic, semantic, and procedural memory interact',
            'key_concepts': ['encoding', 'consolidation', 'retrieval'],
        },
        'EC': {
            'name': 'Embodied Cognition',
            'explains': 'How body and environment are part of the cognitive system',
            'key_concepts': ['affordances', 'extended mind', 'sensorimotor coupling'],
        },
        'CB': {
            'name': 'Chronobiology',
            'explains': 'How circadian rhythms regulate physiology and cognition',
            'key_concepts': ['circadian rhythm', 'melatonin', 'zeitgebers'],
        },
        'MSI': {
            'name': 'Multisensory Integration',
            'explains': 'How the brain combines information across sensory modalities',
            'key_concepts': ['cross-modal binding', 'temporal synchrony', 'spatial coincidence'],
        }
    }

    # =========================================================================
    # RECURSIVE EXPLANATION METHODS
    # =========================================================================

    def _identify_framework(self, template: Dict) -> Optional[str]:
        """Identify which T1 framework a template belongs to."""
        framework_ids = template.get('framework_ids', [])

        # Map common framework_ids to T1 codes
        mapping = {
            'predictive_processing': 'PP',
            'spatial_navigation': 'SN',
            'dual_process': 'DP',
            'dmn_tpn': 'DT',
            'neuromodulation': 'NM',
            'interoception': 'IC',
            'memory_systems': 'MS',
            'embodied_cognition': 'EC',
            'chronobiology': 'CB',
            'multisensory': 'MSI',
            # Also check display_id patterns
        }

        for fid in framework_ids:
            fid_lower = fid.lower()
            for key, code in mapping.items():
                if key in fid_lower:
                    return code

        # Check display_id
        display_id = template.get('display_id', '')
        for code in self.T1_FRAMEWORKS.keys():
            if display_id.startswith(code):
                return code

        return None

    def _extract_causal_chain(self, template: Dict) -> str:
        """Extract the causal chain from a template's causal_links."""
        links = template.get('causal_links', [])
        if not links:
            return ""

        chain_parts = []
        for link in links[:3]:  # Limit to first 3 links
            if isinstance(link, dict):
                from_e = link.get('from_entity', '?')
                to_e = link.get('to_entity', '?')
                activity = link.get('activity', '→')
                chain_parts.append(f"{from_e} --[{activity}]--> {to_e}")

        return ' | '.join(chain_parts)

    def _get_connected_templates(self, template: Dict) -> List[str]:
        """Get template IDs that this template connects to (interactions)."""
        interactions = template.get('interactions', [])
        connected: List[str] = []

        for ix in interactions:
            if isinstance(ix, dict):
                tid = ix.get('display_id', ix.get('template_id', ''))
                if tid:
                    resolved = self._resolve_template_id(str(tid))
                    connected.append(resolved or str(tid))
        # Preserve order while removing duplicates.
        return list(dict.fromkeys(connected))

    def _build_explanation_layer(
        self,
        level: ExplanationLevel,
        template: Dict,
        keywords: List[str]
    ) -> ExplanatoryLayer:
        """Build one layer of explanation from a template."""
        sources = []

        # Create source passage from template
        sources.append(SourcePassage(
            source_type='template',
            source_id=template.get('display_id', 'unknown'),
            source_name=template.get('name', 'Unknown')[:60],
            content=template.get('short_description', template.get('structural_pattern', ''))[:300],
            relevance=0.9,
            section=template.get('display_id', '')
        ))

        # Build explanation based on level
        if level == ExplanationLevel.WHAT:
            explanation = template.get('short_description', 'Effect described in template')

        elif level == ExplanationLevel.HOW:
            chain = self._extract_causal_chain(template)
            explanation = f"Via mechanism: {chain}" if chain else template.get('structural_pattern', '')[:200]

        elif level == ExplanationLevel.WHY:
            explanation = template.get('higher_order_principle', template.get('structural_pattern', ''))[:300]

        elif level == ExplanationLevel.NEURAL:
            # Look for neural-level content in causal_links
            neural_parts = []
            for link in template.get('causal_links', []):
                if isinstance(link, dict):
                    from_lvl = link.get('from_level', '')
                    to_lvl = link.get('to_level', '')
                    if 'neural' in from_lvl or 'neural' in to_lvl:
                        neural_parts.append(
                            f"{link.get('from_entity')} → {link.get('to_entity')} "
                            f"(bridging: {link.get('bridging_to', 'unknown')})"
                        )
            explanation = '; '.join(neural_parts) if neural_parts else "Neural mechanisms not specified in template"

        elif level == ExplanationLevel.THEORY:
            framework = self._identify_framework(template)
            if framework and framework in self.T1_FRAMEWORKS:
                fw = self.T1_FRAMEWORKS[framework]
                explanation = (
                    f"{fw['name']} explains: {fw['explains']}. "
                    f"Key concepts: {', '.join(fw['key_concepts'])}"
                )
            else:
                explanation = template.get('higher_order_principle', 'No T1 framework identified')

        else:  # EVOLUTIONARY
            explanation = "Evolutionary rationale not yet encoded in templates"

        connected = self._get_connected_templates(template)

        return ExplanatoryLayer(
            level=level,
            explanation=explanation,
            sources=sources,
            connects_to=connected[0] if connected else None,
            framework=self._identify_framework(template)
        )

    def ask_deeper(
        self,
        query: str,
        max_depth: int = 4,
        verbose: bool = False
    ) -> RecursiveExplanation:
        """
        Ask a question and get recursive explanatory depth.

        This method follows the chain of templates through their `interactions`
        field, building progressively deeper explanations.

        Args:
            query: The question to answer
            max_depth: Maximum explanation depth (0-5)
            verbose: Whether to print the explanation

        Returns:
            RecursiveExplanation with layered WHY chain
        """
        keywords = self._extract_keywords(query)

        # Find initial template
        template_passages = self._retrieve_template_content(keywords, max_templates=1)

        if not template_passages:
            return RecursiveExplanation(
                query=query,
                layers=[],
                deepest_level=ExplanationLevel.WHAT,
                chain=[],
                has_more_depth=False,
                unexplored_branches=[]
            )

        # Start building layers
        layers = []
        chain = []
        current_template_id = template_passages[0].source_id
        visited = set()
        unexplored = []

        for depth in range(min(max_depth + 1, 6)):
            if current_template_id in visited:
                break
            visited.add(current_template_id)

            template = self.templates.get(current_template_id)
            if not template:
                break

            chain.append(current_template_id)

            # Build layer for this depth
            level = ExplanationLevel(min(depth, 5))
            layer = self._build_explanation_layer(level, template, keywords)
            layers.append(layer)

            # Track unexplored branches
            connected = self._get_connected_templates(template)
            for tid in connected:
                if tid not in visited and tid not in unexplored:
                    unexplored.append(tid)

            # Move to next template in chain
            if layer.connects_to and layer.connects_to not in visited:
                current_template_id = layer.connects_to
            else:
                break

        # Determine if we can go deeper
        has_more = len(unexplored) > 0 or (layers and layers[-1].level.value < 5)

        result = RecursiveExplanation(
            query=query,
            layers=layers,
            deepest_level=layers[-1].level if layers else ExplanationLevel.WHAT,
            chain=chain,
            has_more_depth=has_more,
            unexplored_branches=unexplored[:5]
        )

        if verbose:
            print(self.format_recursive_explanation(result))

        return result

    def format_recursive_explanation(self, explanation: RecursiveExplanation) -> str:
        """Format a recursive explanation with visual depth indicators."""
        lines = [
            "═" * 76,
            "RECURSIVE EXPLANATION — WHY CHAIN",
            "═" * 76,
            "",
            f"QUERY: {explanation.query}",
            f"DEPTH: {len(explanation.layers)} levels (to {explanation.deepest_level.name})",
            f"CHAIN: {' → '.join(explanation.chain)}",
            "",
        ]

        level_labels = {
            ExplanationLevel.WHAT: "WHAT (empirical finding)",
            ExplanationLevel.HOW: "HOW (mechanism)",
            ExplanationLevel.WHY: "WHY (principle)",
            ExplanationLevel.NEURAL: "NEURAL (brain systems)",
            ExplanationLevel.THEORY: "THEORY (T1 framework)",
            ExplanationLevel.EVOLUTIONARY: "EVOLUTIONARY (deep why)",
        }

        for i, layer in enumerate(explanation.layers):
            indent = "  " * i
            lines.append(f"{'─' * (76 - i*2)}")
            lines.append(f"{indent}LEVEL {layer.level.value}: {level_labels.get(layer.level, str(layer.level))}")
            lines.append(f"{'─' * (76 - i*2)}")
            lines.append(f"{indent}")

            # Wrap explanation text
            explanation_lines = layer.explanation.split('. ')
            for el in explanation_lines[:3]:
                lines.append(f"{indent}  {el.strip()}")

            # Show sources
            for source in layer.sources[:1]:
                lines.append(f"{indent}")
                lines.append(f"{indent}  [{source.source_type.upper()}] {source.source_id}")

            # Show framework if present
            if layer.framework:
                fw = self.T1_FRAMEWORKS.get(layer.framework, {})
                lines.append(f"{indent}")
                lines.append(f"{indent}  T1 Framework: {fw.get('name', layer.framework)}")

            # Show connection to deeper level
            if layer.connects_to:
                lines.append(f"{indent}")
                lines.append(f"{indent}  ↓ Connects to: {layer.connects_to}")

            lines.append("")

        # Show unexplored branches
        if explanation.unexplored_branches:
            lines.append("─" * 76)
            lines.append("UNEXPLORED BRANCHES (related mechanisms not yet traced):")
            for branch in explanation.unexplored_branches[:3]:
                lines.append(f"  • {branch}")

        if explanation.has_more_depth:
            lines.append("")
            lines.append("NOTE: Deeper explanations available. Use ask_deeper(query, max_depth=5)")

        lines.append("")
        lines.append("═" * 76)

        return "\n".join(lines)

    def format_response(self, response: ExpertResponse) -> str:
        """Format the expert response with full source citations."""
        lines = [
            "═" * 76,
            f"EXPERT AGENT RESPONSE",
            "═" * 76,
            "",
            f"QUERY: {response.query}",
            "",
            f"SHORT ANSWER:",
            f"  {response.short_answer}",
            "",
            f"CONFIDENCE: {response.confidence_statement}",
            f"SOURCES: {response.source_summary}",
            "",
            "─" * 76,
            "GROUNDED CLAIMS (with citations)",
            "─" * 76,
        ]

        if response.bn_calibration:
            lines.extend(
                [
                    "BN CALIBRATION:",
                    f"  status={response.bn_calibration.get('status', 'unknown')}",
                    f"  edges={response.bn_calibration.get('n_edges_calibrated', 0)}",
                ]
            )
            if response.bn_calibration.get("mean_posterior") is not None:
                lines.append(f"  mean_posterior={response.bn_calibration['mean_posterior']:.2f}")
            lines.append("")

        for i, claim in enumerate(response.grounded_claims, 1):
            lines.append(f"")
            lines.append(f"[{i}] {claim.claim}")
            lines.append(f"    Confidence: {claim.confidence}")
            lines.append(f"    Sources:")
            for source in claim.sources[:2]:
                lines.append(f"      → [{source.source_type.upper()}] {source.source_name[:50]}")
                if source.section:
                    lines.append(f"        Section: {source.section[:50]}")
            if claim.caveats:
                lines.append(f"    Caveats:")
                for caveat in claim.caveats[:2]:
                    lines.append(f"      ⚠ {caveat[:60]}...")

        if response.knowledge_gaps:
            lines.extend([
                "",
                "─" * 76,
                "KNOWLEDGE GAPS (what we don't know)",
                "─" * 76,
            ])
            for gap in response.knowledge_gaps:
                lines.append(f"  ? {gap}")

        if response.follow_up_questions:
            lines.extend([
                "",
                "─" * 76,
                "SUGGESTED FOLLOW-UP QUESTIONS",
                "─" * 76,
            ])
            for q in response.follow_up_questions:
                lines.append(f"  → {q}")

        lines.extend([
            "",
            "═" * 76,
            "NOTE: All claims above are grounded in source documents.",
            "The agent does not make claims beyond its knowledge base.",
            "═" * 76,
        ])

        return "\n".join(lines)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def ask_expert(question: str, verbose: bool = True) -> ExpertResponse:
    """
    Ask the grounded expert agent a question.

    The agent answers ONLY from grounded sources (panels, templates, papers).
    No made-up stuff.

    Usage:
        from src.services.grounded_expert_agent import ask_expert
        response = ask_expert("When do high ceilings increase creativity?")
    """
    agent = GroundedExpertAgent()
    return agent.ask(question, verbose=verbose)


def explain_why(question: str, depth: int = 4, verbose: bool = True) -> RecursiveExplanation:
    """
    Get recursive explanatory depth on a question.

    The agent traces through mechanism chains, going from WHAT → HOW → WHY →
    NEURAL → THEORY, following template interactions.

    Args:
        question: The question to explain
        depth: How deep to go (0=WHAT, 1=HOW, 2=WHY, 3=NEURAL, 4=THEORY, 5=EVOLUTIONARY)
        verbose: Whether to print the explanation

    Usage:
        from src.services.grounded_expert_agent import explain_why
        explanation = explain_why("Why do high ceilings increase creativity?", depth=4)

    Returns:
        RecursiveExplanation with layered WHY chain, each level grounded in sources.
    """
    agent = GroundedExpertAgent()
    return agent.ask_deeper(question, max_depth=depth, verbose=verbose)


if __name__ == "__main__":
    print("\n" + "="*76)
    print("DEMO 1: Standard expert question")
    print("="*76)
    ask_expert("When do high ceilings increase creativity and for whom?")

    print("\n" + "="*76)
    print("DEMO 2: Recursive explanatory depth")
    print("="*76)
    explain_why("Why do high ceilings increase creativity?", depth=4)
