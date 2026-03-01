"""
Article Eater - Prediction Generator Service
Sprint PG-1 through PG-4: Theory-based prediction generation

Generates predictions for queries by:
1. Matching queries to relevant theories (PG-1)
2. Retrieving/generating predictions (PG-2)
3. Combining predictions from multiple theories (PG-3)
4. Integrating with empirical evidence (PG-4)
"""

import json
import math
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
import logging

from src.models.theory_models import (
    Theory, Prediction, Direction, Magnitude, TestingStatus
)
from src.services.theory_registry import TheoryRegistry

logger = logging.getLogger(__name__)


# ============================================================
# DATA STRUCTURES
# ============================================================

@dataclass
class Query:
    """A query about an environment-outcome relationship."""
    query_id: str
    independent_variable: str  # Environmental factor
    dependent_variable: str  # Outcome
    
    # Context
    population: Optional[str] = None
    environment_type: Optional[str] = None  # office, healthcare, residential, etc.
    temporal_frame: Optional[str] = None  # acute, chronic
    additional_conditions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'query_id': self.query_id,
            'independent_variable': self.independent_variable,
            'dependent_variable': self.dependent_variable,
            'population': self.population,
            'environment_type': self.environment_type,
            'temporal_frame': self.temporal_frame,
            'additional_conditions': self.additional_conditions,
        }


@dataclass
class TheoryMatch:
    """A theory matched to a query with relevance score."""
    theory: Theory
    relevance_score: float
    match_reasons: List[str] = field(default_factory=list)
    applicable_predictions: List[Prediction] = field(default_factory=list)
    boundary_violations: List[str] = field(default_factory=list)


@dataclass
class PriorDistribution:
    """A prior probability distribution for an effect."""
    mean: float
    variance: float
    ci_lower: float
    ci_upper: float
    
    # Sources
    source_theories: List[str] = field(default_factory=list)
    source_predictions: List[str] = field(default_factory=list)
    
    # Agreement
    n_agreeing: int = 0
    n_conflicting: int = 0
    conflict_flag: bool = False
    
    # Type
    prior_type: str = "uninformative"  # uninformative, theory_derived, analogical, empirical
    derivation_notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'mean': self.mean,
            'variance': self.variance,
            'ci_lower': self.ci_lower,
            'ci_upper': self.ci_upper,
            'source_theories': self.source_theories,
            'source_predictions': self.source_predictions,
            'n_agreeing': self.n_agreeing,
            'n_conflicting': self.n_conflicting,
            'conflict_flag': self.conflict_flag,
            'prior_type': self.prior_type,
            'derivation_notes': self.derivation_notes,
        }


@dataclass
class EmpiricalEvidence:
    """Empirical evidence for a query."""
    n_studies: int
    pooled_effect: Optional[float]
    pooled_se: Optional[float]
    heterogeneity: Optional[float]  # I²
    quality_summary: str  # high, moderate, low
    study_ids: List[str] = field(default_factory=list)


@dataclass
class PredictionOutput:
    """Complete output from prediction generation."""
    query: Query
    
    # Theory analysis
    relevant_theories: List[TheoryMatch]
    predictions_found: List[Tuple[Prediction, float]]  # (prediction, match_quality)
    prediction_agreement: str  # agreeing, conflicting, mixed
    
    # Prior
    prior_distribution: PriorDistribution
    
    # Empirical (if available)
    empirical_evidence: Optional[EmpiricalEvidence] = None
    
    # Posterior (if empirical evidence)
    posterior_mean: Optional[float] = None
    posterior_variance: Optional[float] = None
    posterior_ci: Optional[Tuple[float, float]] = None
    theory_weight: Optional[float] = None
    empirical_weight: Optional[float] = None
    
    # Summary
    overall_confidence: str = "low"  # high, medium, low, very_low
    limiting_factors: List[str] = field(default_factory=list)
    voi: float = 0.0  # Value of information for more research
    
    # Explanation
    narrative: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'query': self.query.to_dict(),
            'relevant_theories': [
                {
                    'theory_id': m.theory.theory_id,
                    'name': m.theory.name,
                    'relevance': m.relevance_score,
                    'reasons': m.match_reasons,
                }
                for m in self.relevant_theories
            ],
            'predictions_found': [
                {
                    'prediction_id': p.prediction_id,
                    'statement': p.statement,
                    'direction': p.consequent_direction.value,
                    'match_quality': q,
                }
                for p, q in self.predictions_found
            ],
            'prediction_agreement': self.prediction_agreement,
            'prior': self.prior_distribution.to_dict(),
            'posterior': {
                'mean': self.posterior_mean,
                'variance': self.posterior_variance,
                'ci': self.posterior_ci,
                'theory_weight': self.theory_weight,
                'empirical_weight': self.empirical_weight,
            } if self.posterior_mean else None,
            'overall_confidence': self.overall_confidence,
            'limiting_factors': self.limiting_factors,
            'voi': self.voi,
            'narrative': self.narrative,
        }


# ============================================================
# PREDICTION GENERATOR
# ============================================================

class PredictionGenerator:
    """
    Generates theory-derived predictions for environment-outcome queries.
    
    Implements the full prediction generation pipeline:
    1. Theory matching
    2. Prediction retrieval/generation
    3. Multi-theory combination
    4. Empirical integration
    """
    
    def __init__(self, registry: TheoryRegistry, findings_db=None):
        """
        Initialize the generator.
        
        Args:
            registry: TheoryRegistry for theory/prediction access
            findings_db: Optional database connection for empirical evidence
        """
        self.registry = registry
        self.findings_db = findings_db
        
        # Weights for relevance scoring
        self.domain_weight = 0.3
        self.variable_weight = 0.3
        self.prediction_weight = 0.3
        self.context_weight = 0.1
    
    def generate(self, query: Query) -> PredictionOutput:
        """
        Generate predictions for a query.
        
        Args:
            query: Query object specifying IV, DV, and context
            
        Returns:
            PredictionOutput with theory analysis, prior, and optionally posterior
        """
        logger.info(f"Generating predictions for: {query.independent_variable} → {query.dependent_variable}")
        
        # Step 1: Match theories
        theory_matches = self._match_theories(query)
        
        # Step 2: Retrieve/generate predictions
        predictions_with_quality = self._retrieve_predictions(query, theory_matches)
        
        # Step 3: Determine agreement
        agreement = self._assess_agreement(predictions_with_quality)
        
        # Step 4: Generate prior distribution
        prior = self._generate_prior(predictions_with_quality, agreement)
        
        # Step 5: Get empirical evidence (if available)
        empirical = self._get_empirical_evidence(query)
        
        # Step 6: Combine into posterior (if empirical available)
        posterior_mean = None
        posterior_variance = None
        posterior_ci = None
        theory_weight = None
        empirical_weight = None
        
        if empirical and empirical.pooled_effect is not None:
            posterior_mean, posterior_variance, theory_weight, empirical_weight = self._bayesian_update(
                prior, empirical
            )
            if posterior_variance:
                se = math.sqrt(posterior_variance)
                posterior_ci = (posterior_mean - 1.96 * se, posterior_mean + 1.96 * se)
        
        # Step 7: Assess confidence and VOI
        confidence, limiting_factors = self._assess_confidence(
            theory_matches, predictions_with_quality, prior, empirical
        )
        voi = self._calculate_voi(prior, empirical, predictions_with_quality)
        
        # Step 8: Generate narrative
        narrative = self._generate_narrative(
            query, theory_matches, predictions_with_quality, prior, empirical
        )
        
        return PredictionOutput(
            query=query,
            relevant_theories=theory_matches,
            predictions_found=predictions_with_quality,
            prediction_agreement=agreement,
            prior_distribution=prior,
            empirical_evidence=empirical,
            posterior_mean=posterior_mean,
            posterior_variance=posterior_variance,
            posterior_ci=posterior_ci,
            theory_weight=theory_weight,
            empirical_weight=empirical_weight,
            overall_confidence=confidence,
            limiting_factors=limiting_factors,
            voi=voi,
            narrative=narrative,
        )
    
    # ================================================================
    # STEP 1: THEORY MATCHING
    # ================================================================
    
    def _match_theories(self, query: Query) -> List[TheoryMatch]:
        """Match query to relevant theories."""
        theories = self.registry.list_theories()
        matches = []
        
        for theory in theories:
            # Load full theory with predictions
            full_theory = self.registry.get_theory(theory.theory_id)
            if not full_theory:
                continue
            
            relevance, reasons = self._compute_theory_relevance(query, full_theory)
            
            if relevance > 0.1:
                # Check boundary conditions
                boundary_violations = self._check_boundaries(query, full_theory)
                
                # Reduce relevance if boundaries violated
                if boundary_violations:
                    relevance *= 0.5
                
                matches.append(TheoryMatch(
                    theory=full_theory,
                    relevance_score=relevance,
                    match_reasons=reasons,
                    boundary_violations=boundary_violations,
                ))
        
        # Sort by relevance
        matches.sort(key=lambda m: m.relevance_score, reverse=True)
        return matches[:10]  # Top 10
    
    def _compute_theory_relevance(self, query: Query, theory: Theory) -> Tuple[float, List[str]]:
        """Compute relevance score for a theory."""
        relevance = 0.0
        reasons = []
        
        # Domain matching
        query_domains = self._extract_domains(query)
        domain_overlap = len(set(theory.domain) & set(query_domains))
        if domain_overlap > 0:
            domain_score = min(1.0, domain_overlap / 2)
            relevance += self.domain_weight * domain_score
            reasons.append(f"Domain overlap: {domain_overlap}")
        
        # Variable matching in predictions
        iv_lower = query.independent_variable.lower()
        dv_lower = query.dependent_variable.lower()
        
        for pred in theory.all_predictions:
            # Check outcome
            if dv_lower in pred.consequent_outcome.lower():
                relevance += self.variable_weight * 0.5
                reasons.append(f"Prediction addresses outcome: {pred.consequent_outcome}")
                break
        
        # Check if theory scope mentions variables
        scope = (theory.scope_description or "").lower()
        if iv_lower in scope or dv_lower in scope:
            relevance += self.variable_weight * 0.3
            reasons.append("Variables in theory scope")
        
        # Direct prediction matching
        for pred in theory.all_predictions:
            statement_lower = pred.statement.lower()
            if iv_lower in statement_lower and dv_lower in statement_lower:
                relevance += self.prediction_weight
                reasons.append(f"Direct prediction match: {pred.prediction_id}")
                break
        
        # Context matching
        if query.environment_type:
            if query.environment_type.lower() in str(theory.domain).lower():
                relevance += self.context_weight
                reasons.append("Context matches theory domain")
        
        # Weight by theory confidence
        relevance *= theory.overall_confidence
        
        return round(relevance, 3), reasons
    
    def _extract_domains(self, query: Query) -> List[str]:
        """Extract domain keywords from query."""
        domains = []
        
        # Map common terms to domains
        term_to_domain = {
            'attention': ['attention', 'cognition'],
            'stress': ['stress', 'health', 'physiology'],
            'mood': ['affect', 'emotion', 'wellbeing'],
            'productivity': ['performance', 'cognition'],
            'nature': ['natural_environments'],
            'light': ['lighting', 'circadian'],
            'noise': ['acoustics', 'stress'],
            'crowding': ['density', 'stress'],
        }
        
        for term in [query.independent_variable, query.dependent_variable]:
            term_lower = term.lower()
            for key, domain_list in term_to_domain.items():
                if key in term_lower:
                    domains.extend(domain_list)
        
        return list(set(domains))
    
    def _check_boundaries(self, query: Query, theory: Theory) -> List[str]:
        """Check if any boundary conditions are violated."""
        violations = []
        
        for boundary in theory.boundary_conditions:
            condition = boundary.condition_description.lower()
            
            # Check for temporal mismatches
            if 'chronic' in condition and query.temporal_frame == 'acute':
                violations.append(f"Temporal mismatch: {boundary.condition_description}")
            
            # Check for state requirements
            if 'fatigue' in condition and 'fatigue' not in str(query.additional_conditions).lower():
                # Note but don't necessarily violate
                pass
        
        return violations
    
    # ================================================================
    # STEP 2: PREDICTION RETRIEVAL
    # ================================================================
    
    def _retrieve_predictions(
        self, 
        query: Query, 
        theory_matches: List[TheoryMatch]
    ) -> List[Tuple[Prediction, float]]:
        """Retrieve predictions relevant to the query."""
        results = []
        seen_ids = set()
        
        for match in theory_matches:
            for pred in match.theory.all_predictions:
                if pred.prediction_id in seen_ids:
                    continue
                
                quality = self._compute_prediction_match(query, pred)
                
                if quality > 0.2:
                    results.append((pred, quality))
                    seen_ids.add(pred.prediction_id)
                    match.applicable_predictions.append(pred)
        
        # Sort by match quality
        results.sort(key=lambda x: x[1], reverse=True)
        return results
    
    def _compute_prediction_match(self, query: Query, pred: Prediction) -> float:
        """Compute how well a prediction matches the query."""
        quality = 0.0
        
        iv_lower = query.independent_variable.lower()
        dv_lower = query.dependent_variable.lower()
        statement_lower = pred.statement.lower()
        outcome_lower = pred.consequent_outcome.lower()
        
        # Outcome match
        if dv_lower in outcome_lower:
            quality += 0.4
        elif any(word in outcome_lower for word in dv_lower.split('_')):
            quality += 0.2
        
        # IV in antecedent or statement
        antecedent_text = json.dumps(pred.antecedent_env_conditions).lower()
        if iv_lower in antecedent_text:
            quality += 0.3
        elif iv_lower in statement_lower:
            quality += 0.2
        
        # Both in statement
        if iv_lower in statement_lower and dv_lower in statement_lower:
            quality += 0.2
        
        # Context match
        if query.environment_type:
            context_lower = query.environment_type.lower()
            contexts = json.dumps(pred.applicable_contexts).lower()
            if context_lower in contexts:
                quality += 0.1
        
        # Weight by prediction confidence
        quality *= pred.current_confidence
        
        return min(1.0, quality)
    
    # ================================================================
    # STEP 3: AGREEMENT ASSESSMENT
    # ================================================================
    
    def _assess_agreement(self, predictions: List[Tuple[Prediction, float]]) -> str:
        """Assess agreement among predictions."""
        if not predictions:
            return "none"
        
        directions = {}
        for pred, quality in predictions:
            direction = pred.consequent_direction
            if direction not in directions:
                directions[direction] = 0
            directions[direction] += quality
        
        if len(directions) == 1:
            return "agreeing"
        
        # Check for conflicts
        positive_weight = directions.get(Direction.POSITIVE, 0)
        negative_weight = directions.get(Direction.NEGATIVE, 0)
        null_weight = directions.get(Direction.NULL, 0)
        
        if positive_weight > 0 and negative_weight > 0:
            return "conflicting"
        
        return "mixed"
    
    # ================================================================
    # STEP 4: PRIOR GENERATION
    # ================================================================
    
    def _generate_prior(
        self, 
        predictions: List[Tuple[Prediction, float]],
        agreement: str
    ) -> PriorDistribution:
        """Generate prior distribution from predictions."""
        
        if not predictions:
            # Uninformative prior
            return PriorDistribution(
                mean=0.0,
                variance=1.0,
                ci_lower=-1.96,
                ci_upper=1.96,
                prior_type="uninformative",
                derivation_notes="No relevant theory predictions found",
            )
        
        # Compute weighted mean of predicted effects
        total_weight = 0.0
        weighted_sum = 0.0
        source_theories = set()
        source_predictions = []
        
        direction_weights = {
            Direction.POSITIVE: 1.0,
            Direction.NEGATIVE: -1.0,
            Direction.NULL: 0.0,
            Direction.INVERTED_U: 0.5,  # Assume positive at moderate levels
            Direction.COMPLEX: 0.0,
        }
        
        magnitude_values = {
            Magnitude.STRONG: 0.8,
            Magnitude.MODERATE: 0.4,
            Magnitude.WEAK: 0.2,
            Magnitude.UNSPECIFIED: 0.3,
        }
        
        for pred, quality in predictions:
            weight = quality * pred.current_confidence
            direction_sign = direction_weights.get(pred.consequent_direction, 0)
            magnitude_value = magnitude_values.get(pred.consequent_magnitude, 0.3)
            
            effect_estimate = direction_sign * magnitude_value
            
            weighted_sum += weight * effect_estimate
            total_weight += weight
            
            source_theories.add(pred.source_theory_id)
            source_predictions.append(pred.prediction_id)
        
        if total_weight == 0:
            mean = 0.0
        else:
            mean = weighted_sum / total_weight
        
        # Compute variance based on agreement and prediction count
        n_predictions = len(predictions)
        base_variance = 0.5  # Moderate uncertainty
        
        if agreement == "agreeing":
            variance = base_variance / math.sqrt(n_predictions)
        elif agreement == "conflicting":
            variance = base_variance * 2
        else:
            variance = base_variance
        
        # Confidence interval
        se = math.sqrt(variance)
        ci_lower = mean - 1.96 * se
        ci_upper = mean + 1.96 * se
        
        # Count agreements/conflicts
        positive_count = sum(1 for p, _ in predictions if p.consequent_direction == Direction.POSITIVE)
        negative_count = sum(1 for p, _ in predictions if p.consequent_direction == Direction.NEGATIVE)
        
        return PriorDistribution(
            mean=round(mean, 3),
            variance=round(variance, 3),
            ci_lower=round(ci_lower, 3),
            ci_upper=round(ci_upper, 3),
            source_theories=list(source_theories),
            source_predictions=source_predictions,
            n_agreeing=max(positive_count, negative_count),
            n_conflicting=min(positive_count, negative_count) if positive_count > 0 and negative_count > 0 else 0,
            conflict_flag=agreement == "conflicting",
            prior_type="theory_derived",
            derivation_notes=f"Derived from {n_predictions} predictions across {len(source_theories)} theories",
        )
    
    # ================================================================
    # STEP 5: EMPIRICAL EVIDENCE
    # ================================================================

    def _fetch_finding_by_iv_dv(
        self,
        iv: str,
        dv: str
    ) -> Optional[Dict[str, Any]]:
        """
        Query findings database to find empirical findings matching IV → DV.

        Supports multiple data sources:
        - SQLite database (findings table)
        - JSONL files in data/extracted_findings/
        - Dict-based findings collection

        Uses fuzzy matching on variable names (LIKE %name%).

        Args:
            iv: Independent variable name
            dv: Dependent variable name

        Returns:
            Best-matching finding dict or None
        """
        import json
        import sqlite3
        from pathlib import Path

        # Normalize variable names for matching
        iv_lower = iv.lower().strip()
        dv_lower = dv.lower().strip()

        best_finding = None
        best_score = 0.0

        # Case 1: SQLite database connection
        if self.findings_db is not None and isinstance(self.findings_db, sqlite3.Connection):
            try:
                cursor = self.findings_db.cursor()
                # Query findings table for antecedent → consequent matches
                query = """
                    SELECT id, antecedents, consequent, measure_direction,
                           effect_size, p_value, sample_size,
                           confidence_interval_lower, confidence_interval_upper
                    FROM findings
                    WHERE LOWER(consequent) LIKE ? OR LOWER(consequent) LIKE ?
                    LIMIT 20
                """
                # Use LIKE with wildcards for fuzzy matching
                cursor.execute(query, (f"%{dv_lower}%", f"%{dv_lower.replace('_', ' ')}%"))

                for row in cursor.fetchall():
                    finding_id, antecedents_raw, consequent, direction, effect, pval, n, ci_lower, ci_upper = row

                    # Parse antecedents (stored as JSON list or comma-separated)
                    antecedents = []
                    try:
                        antecedents = json.loads(antecedents_raw) if isinstance(antecedents_raw, str) else antecedents_raw
                    except (json.JSONDecodeError, TypeError):
                        if isinstance(antecedents_raw, str):
                            antecedents = [a.strip() for a in antecedents_raw.split(',')]

                    # Score based on antecedent match
                    for ant in antecedents:
                        ant_lower = ant.lower() if isinstance(ant, str) else str(ant).lower()
                        if iv_lower in ant_lower or ant_lower in iv_lower:
                            # Strong match
                            score = 1.0
                            if score > best_score:
                                best_score = score
                                best_finding = {
                                    'id': finding_id,
                                    'antecedents': antecedents,
                                    'consequent': consequent,
                                    'measure_direction': direction,
                                    'statistics': {
                                        'effect_size': effect,
                                        'p_value': pval,
                                        'sample_size': n,
                                        'ci_lower': ci_lower,
                                        'ci_upper': ci_upper,
                                    }
                                }
                            break

            except Exception as e:
                logger.warning(f"Error querying SQLite findings database: {e}")

        # Case 2: File-based findings (JSONL files in data/extracted_findings/)
        # Always try file-based search as fallback or primary method
        if best_score < 0.3:
            findings_dir = Path("data/extracted_findings")
            if not findings_dir.exists():
                findings_dir = Path(__file__).parents[2] / "data" / "extracted_findings"

            if findings_dir.exists():
                try:
                    for jsonl_file in findings_dir.glob("*.jsonl"):
                        try:
                            with open(jsonl_file, 'r') as f:
                                for line in f:
                                    if not line.strip():
                                        continue

                                    try:
                                        finding = json.loads(line.strip())
                                    except json.JSONDecodeError:
                                        continue

                                    consequent = finding.get('consequent', '').lower()
                                    antecedents = finding.get('antecedents', [])

                                    # Score consequent match
                                    if dv_lower in consequent or consequent in dv_lower:
                                        consequent_score = 1.0
                                    else:
                                        # Check for partial word matches
                                        dv_words = set(dv_lower.split('_'))
                                        consequent_words = set(consequent.split('_'))
                                        overlap = dv_words & consequent_words
                                        consequent_score = len(overlap) / max(len(dv_words), len(consequent_words), 1)

                                    if consequent_score < 0.3:
                                        continue

                                    # Score antecedent match
                                    antecedent_score = 0.0
                                    for ant in antecedents:
                                        ant_lower = ant.lower() if isinstance(ant, str) else str(ant).lower()
                                        if iv_lower in ant_lower or ant_lower in iv_lower:
                                            antecedent_score = 1.0
                                            break
                                        # Partial match
                                        iv_words = set(iv_lower.split('_'))
                                        ant_words = set(ant_lower.split('_'))
                                        overlap = iv_words & ant_words
                                        partial_score = len(overlap) / max(len(iv_words), len(ant_words), 1)
                                        if partial_score > antecedent_score:
                                            antecedent_score = partial_score

                                    # Combined score: weighted by both matches
                                    combined_score = (0.6 * consequent_score) + (0.4 * antecedent_score)

                                    if combined_score > best_score:
                                        best_score = combined_score
                                        best_finding = finding

                        except Exception as e:
                            logger.debug(f"Error reading {jsonl_file}: {e}")

                except Exception as e:
                    logger.warning(f"Error accessing findings directory: {e}")

        return best_finding if best_score > 0.3 else None
    
    def _get_empirical_evidence(self, query: Query) -> Optional[EmpiricalEvidence]:
        """
        Retrieve empirical evidence for the query by searching findings database.

        Attempts to find extraction data matching the IV and DV. Returns None
        only if no finding is available; returns EmpiricalEvidence even with
        sparse statistical data (e.g., from literature reviews).
        """
        # Try to fetch a finding matching the IV and DV
        finding = self._fetch_finding_by_iv_dv(
            query.independent_variable,
            query.dependent_variable
        )

        if not finding:
            return None

        # Convert finding dict to EmpiricalEvidence
        stats = finding.get('statistics', {})

        # Extract pooled effect from effect_size if available
        pooled_effect = stats.get('effect_size')
        pooled_se = None

        # Calculate SE from confidence interval if available
        if stats.get('ci_lower') is not None and stats.get('ci_upper') is not None:
            # 95% CI: ci_upper - ci_lower = 2 * 1.96 * SE
            ci_lower = stats.get('ci_lower', 0)
            ci_upper = stats.get('ci_upper', 0)
            if (ci_upper - ci_lower) > 0:
                pooled_se = (ci_upper - ci_lower) / (2 * 1.96)

        # Sample size and study count
        sample_size = stats.get('sample_size')
        n_studies = 1  # We found at least one finding/paper

        # Assess quality based on what's available
        quality = "low"

        # Check for statistical evidence
        if stats.get('p_value') is not None:
            if stats.get('p_value') < 0.05:
                quality = "high"
            else:
                quality = "moderate"
        elif sample_size is not None:
            if sample_size > 30:
                quality = "moderate"
        elif finding.get('article_type') == 'empirical':
            # Empirical studies (without stats) are higher quality than reviews
            quality = "moderate"

        # If direction is explicitly stated, it's evidence of some kind
        if finding.get('measure_direction') in ('positive', 'negative'):
            if quality == "low":
                quality = "low"  # Keep low if no other indicators

        return EmpiricalEvidence(
            n_studies=n_studies,
            pooled_effect=pooled_effect,
            pooled_se=pooled_se,
            heterogeneity=None,  # Not provided in findings
            quality_summary=quality,
            study_ids=[finding.get('paper_id', 'unknown')],
        )
    
    # ================================================================
    # STEP 6: BAYESIAN UPDATE
    # ================================================================
    
    def _bayesian_update(
        self,
        prior: PriorDistribution,
        empirical: EmpiricalEvidence
    ) -> Tuple[float, float, float, float]:
        """
        Perform Bayesian update of prior with empirical evidence.
        
        Returns: (posterior_mean, posterior_variance, theory_weight, empirical_weight)
        """
        if empirical.pooled_effect is None or empirical.pooled_se is None:
            return None, None, None, None
        
        # Prior parameters
        mu_prior = prior.mean
        sigma2_prior = prior.variance
        
        # Data parameters
        mu_data = empirical.pooled_effect
        sigma2_data = empirical.pooled_se ** 2
        
        # Precision (inverse variance)
        precision_prior = 1.0 / sigma2_prior if sigma2_prior > 0 else 0.01
        precision_data = 1.0 / sigma2_data if sigma2_data > 0 else 0.01
        precision_post = precision_prior + precision_data
        
        # Posterior mean (precision-weighted)
        mu_post = (precision_prior * mu_prior + precision_data * mu_data) / precision_post
        
        # Posterior variance
        sigma2_post = 1.0 / precision_post
        
        # Weights
        theory_weight = precision_prior / precision_post
        empirical_weight = precision_data / precision_post
        
        return (
            round(mu_post, 3),
            round(sigma2_post, 4),
            round(theory_weight, 3),
            round(empirical_weight, 3),
        )
    
    # ================================================================
    # STEP 7: CONFIDENCE ASSESSMENT
    # ================================================================
    
    def _assess_confidence(
        self,
        theory_matches: List[TheoryMatch],
        predictions: List[Tuple[Prediction, float]],
        prior: PriorDistribution,
        empirical: Optional[EmpiricalEvidence]
    ) -> Tuple[str, List[str]]:
        """Assess overall confidence and identify limiting factors."""
        limiting_factors = []
        confidence_score = 0.0
        
        # Theory coverage
        if not theory_matches:
            limiting_factors.append("No relevant theories found")
            confidence_score -= 0.3
        elif len(theory_matches) >= 2:
            confidence_score += 0.2
        
        # Prediction coverage
        if not predictions:
            limiting_factors.append("No predictions address this relationship")
            confidence_score -= 0.3
        elif len(predictions) >= 3:
            confidence_score += 0.2
        
        # Agreement
        if prior.conflict_flag:
            limiting_factors.append("Conflicting predictions from different theories")
            confidence_score -= 0.2
        elif prior.n_agreeing >= 2:
            confidence_score += 0.2
        
        # Prior uncertainty
        if prior.variance > 0.5:
            limiting_factors.append("High uncertainty in theory predictions")
            confidence_score -= 0.1
        
        # Empirical support
        if empirical:
            if empirical.n_studies >= 5:
                confidence_score += 0.3
            elif empirical.n_studies >= 2:
                confidence_score += 0.1
        else:
            limiting_factors.append("No empirical evidence available")
        
        # Map to category
        if confidence_score >= 0.5:
            confidence = "high"
        elif confidence_score >= 0.2:
            confidence = "medium"
        elif confidence_score >= -0.1:
            confidence = "low"
        else:
            confidence = "very_low"
        
        return confidence, limiting_factors
    
    def _calculate_voi(
        self,
        prior: PriorDistribution,
        empirical: Optional[EmpiricalEvidence],
        predictions: List[Tuple[Prediction, float]]
    ) -> float:
        """Calculate value of information for additional research."""
        voi = 0.0
        
        # High prior confidence + no empirical = high VOI (theory to test)
        if prior.prior_type == "theory_derived" and not empirical:
            avg_confidence = sum(p.current_confidence * q for p, q in predictions) / len(predictions) if predictions else 0
            voi += 0.3 * avg_confidence
        
        # Conflicting predictions = high VOI (adjudicate)
        if prior.conflict_flag:
            voi += 0.4
        
        # High uncertainty = moderate VOI
        if prior.variance > 0.4:
            voi += 0.2
        
        # Untested predictions from high-confidence theories
        untested_high_conf = sum(
            1 for p, _ in predictions 
            if p.testing_status == TestingStatus.UNTESTED and p.prior_confidence > 0.6
        )
        voi += 0.1 * min(3, untested_high_conf)
        
        return round(min(1.0, voi), 2)
    
    # ================================================================
    # STEP 8: NARRATIVE GENERATION
    # ================================================================
    
    def _generate_narrative(
        self,
        query: Query,
        theory_matches: List[TheoryMatch],
        predictions: List[Tuple[Prediction, float]],
        prior: PriorDistribution,
        empirical: Optional[EmpiricalEvidence]
    ) -> str:
        """Generate human-readable narrative explanation."""
        parts = []
        
        # Opening
        parts.append(f"Analysis of the relationship between {query.independent_variable} and {query.dependent_variable}:")
        
        # Theory coverage
        if theory_matches:
            theory_names = [m.theory.name for m in theory_matches[:3]]
            parts.append(f"\nRelevant theories: {', '.join(theory_names)}.")
        else:
            parts.append("\nNo well-matched theories found for this relationship.")
        
        # Prediction summary
        if predictions:
            directions = {}
            for pred, quality in predictions:
                d = pred.consequent_direction.value
                if d not in directions:
                    directions[d] = []
                directions[d].append(pred.source_theory_id.replace('theory:', ''))
            
            dir_summaries = []
            for d, theories in directions.items():
                dir_summaries.append(f"{d} effect ({', '.join(set(theories))})")
            
            parts.append(f"\nPredictions: {'; '.join(dir_summaries)}.")
        
        # Prior
        if prior.prior_type != "uninformative":
            direction = "positive" if prior.mean > 0.1 else "negative" if prior.mean < -0.1 else "near-null"
            magnitude = "strong" if abs(prior.mean) > 0.5 else "moderate" if abs(prior.mean) > 0.2 else "weak"
            parts.append(
                f"\nTheory-derived prior: {direction} effect, {magnitude} magnitude "
                f"(mean={prior.mean:.2f}, 95% CI [{prior.ci_lower:.2f}, {prior.ci_upper:.2f}])."
            )
        
        # Empirical
        if empirical:
            parts.append(
                f"\nEmpirical evidence: {empirical.n_studies} studies, "
                f"pooled effect = {empirical.pooled_effect:.2f}."
            )
        else:
            parts.append("\nNo direct empirical evidence available for this specific relationship.")
        
        return " ".join(parts)


# ============================================================
# CONVENIENCE FUNCTIONS
# ============================================================

def generate_prediction(
    registry: TheoryRegistry,
    iv: str,
    dv: str,
    context: Optional[Dict[str, Any]] = None
) -> PredictionOutput:
    """
    Convenience function to generate a prediction.
    
    Args:
        registry: TheoryRegistry instance
        iv: Independent variable (environmental factor)
        dv: Dependent variable (outcome)
        context: Optional context dict with population, environment_type, etc.
        
    Returns:
        PredictionOutput
    """
    context = context or {}
    
    query = Query(
        query_id=f"query:{iv}:{dv}",
        independent_variable=iv,
        dependent_variable=dv,
        population=context.get('population'),
        environment_type=context.get('environment_type'),
        temporal_frame=context.get('temporal_frame'),
        additional_conditions=context.get('conditions', []),
    )
    
    generator = PredictionGenerator(registry)
    return generator.generate(query)
