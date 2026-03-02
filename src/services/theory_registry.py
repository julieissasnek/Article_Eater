"""
Article Eater - Theory Registry Service
Sprint TH-1: Theory Data Model & Registry

Manages the storage, retrieval, and updating of theories and predictions
in the database. Provides the core API for theory system operations.
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
from contextlib import contextmanager
import logging

from src.models.theory_models import (
    Theory, TheoryClaim, TheoryAssumption, TheoryBoundary,
    Prediction, PredictionEvidence, Originator, DerivationStep,
    TheoryLevel, PredictionType, Direction, Magnitude, TestingStatus,
    SupportLevel, ReplicationStatus,
    Necessity, Testability, RelationType, Generality, UncertaintyType
)

logger = logging.getLogger(__name__)


class TheoryRegistry:
    """
    Central registry for theoretical frameworks and their predictions.
    
    Provides CRUD operations for theories, predictions, and evidence,
    as well as query and analysis capabilities.
    """
    
    def __init__(self, db_path: str):
        """
        Initialize the theory registry.
        
        Args:
            db_path: Path to the SQLite database (use ":memory:" for in-memory)
        """
        self.db_path = Path(db_path) if db_path != ":memory:" else db_path
        self._is_memory = (db_path == ":memory:")
        self._persistent_conn = None
        
        # For in-memory databases, keep a persistent connection
        if self._is_memory:
            self._persistent_conn = sqlite3.connect(":memory:")
            self._persistent_conn.row_factory = sqlite3.Row
            self._persistent_conn.execute("PRAGMA foreign_keys = ON")
        
        self._ensure_schema()
    
    @contextmanager
    def _get_connection(self):
        """Get a database connection with proper settings."""
        if self._is_memory and self._persistent_conn:
            # For in-memory, reuse the persistent connection
            yield self._persistent_conn
            # Don't close - keep it alive
        else:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()
    
    def _ensure_schema(self):
        """Ensure theory tables exist in the database."""
        # Try multiple paths to find the schema
        possible_paths = [
            Path(__file__).parent.parent.parent / "db" / "sql" / "017_theories.sql",
        ]
        
        schema_path = None
        for path in possible_paths:
            if path.exists():
                schema_path = path
                break
        
        if schema_path:
            with self._get_connection() as conn:
                with open(schema_path) as f:
                    conn.executescript(f.read())
                conn.commit()  # Explicit commit for in-memory
        else:
            # Create schema inline as fallback
            self._create_schema_inline()
    
    # ================================================================
    # THEORY OPERATIONS
    # ================================================================
    
    def add_theory(self, theory: Theory) -> str:
        """
        Add a new theory to the registry.
        
        Args:
            theory: Theory object to add
            
        Returns:
            theory_id of the added theory
        """
        now = datetime.now(timezone.utc).isoformat()
        
        with self._get_connection() as conn:
            # Insert main theory record
            conn.execute("""
                INSERT INTO theories (
                    theory_id, name, aliases, originators, year_introduced,
                    domain, scope_description, level,
                    overall_confidence, confidence_rationale, quantitative_precision,
                    parent_theories, child_theories, compatible_theories, competing_theories,
                    replication_status, extraction_source, extracted_by, version,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                theory.theory_id,
                theory.name,
                json.dumps(theory.aliases),
                json.dumps([o.to_dict() for o in theory.originators]),
                theory.year_introduced,
                json.dumps(theory.domain),
                theory.scope_description,
                theory.level.value,
                theory.overall_confidence,
                theory.confidence_rationale,
                theory.quantitative_precision,
                json.dumps(theory.parent_theories),
                json.dumps(theory.child_theories),
                json.dumps(theory.compatible_theories),
                json.dumps(theory.competing_theories),
                theory.replication_status.value,
                theory.extraction_source,
                theory.extracted_by,
                theory.version,
                now,
                now,
            ))
            
            # Insert core claims
            for claim in theory.core_claims:
                self._add_claim(conn, claim)
            
            # Insert assumptions
            for assumption in theory.assumptions:
                self._add_assumption(conn, assumption)
            
            # Insert boundary conditions
            for boundary in theory.boundary_conditions:
                self._add_boundary(conn, boundary)
            
            # Insert predictions
            for pred in theory.explicit_predictions:
                self._add_prediction(conn, pred)
            for pred in theory.derived_predictions:
                self._add_prediction(conn, pred)
        
        logger.info(f"Added theory: {theory.theory_id} ({theory.name})")
        return theory.theory_id
    
    def _add_claim(self, conn: sqlite3.Connection, claim: TheoryClaim):
        """Add a theory claim."""
        conn.execute("""
            INSERT INTO theory_claims (claim_id, theory_id, statement, formalization, necessity, testability, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            claim.claim_id,
            claim.theory_id,
            claim.statement,
            claim.formalization,
            claim.necessity.value,
            claim.testability.value,
            datetime.now(timezone.utc).isoformat(),
        ))
    
    def _add_assumption(self, conn: sqlite3.Connection, assumption: TheoryAssumption):
        """Add a theory assumption."""
        conn.execute("""
            INSERT INTO theory_assumptions (assumption_id, theory_id, statement, dependent_claims, violation_consequence, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            assumption.assumption_id,
            assumption.theory_id,
            assumption.statement,
            json.dumps(assumption.dependent_claims),
            assumption.violation_consequence,
            datetime.now(timezone.utc).isoformat(),
        ))
    
    def _add_boundary(self, conn: sqlite3.Connection, boundary: TheoryBoundary):
        """Add a theory boundary condition."""
        conn.execute("""
            INSERT INTO theory_boundaries (boundary_id, theory_id, condition_description, evidence_for_boundary, mechanism_of_failure, confidence_penalty, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            boundary.boundary_id,
            boundary.theory_id,
            boundary.condition_description,
            json.dumps(boundary.evidence_for_boundary),
            boundary.mechanism_of_failure,
            boundary.confidence_penalty,
            datetime.now(timezone.utc).isoformat(),
        ))
    
    def _add_prediction(self, conn: sqlite3.Connection, pred: Prediction):
        """Add a prediction."""
        now = datetime.now(timezone.utc).isoformat()
        conn.execute("""
            INSERT INTO predictions (
                prediction_id, source_theory_id, statement, prediction_type,
                antecedent_env_conditions, antecedent_population, antecedent_temporal, antecedent_state,
                consequent_outcome, consequent_direction, consequent_magnitude, consequent_mechanism,
                relation_type, derivation_chain, auxiliary_assumptions,
                quantitative_point_estimate, quantitative_ci_lower, quantitative_ci_upper, functional_form,
                generality, applicable_populations, applicable_contexts, known_exceptions,
                testing_status, overall_support, test_summary,
                prior_confidence, current_confidence, theory_contribution, derivation_contribution, empirical_contribution,
                uncertainty_type, maps_to_edge_id, maps_to_nodes, contributes_prior, prior_weight,
                extraction_source, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            pred.prediction_id,
            pred.source_theory_id,
            pred.statement,
            pred.prediction_type.value,
            json.dumps(pred.antecedent_env_conditions),
            json.dumps(pred.antecedent_population),
            json.dumps(pred.antecedent_temporal) if pred.antecedent_temporal else None,
            json.dumps(pred.antecedent_state),
            pred.consequent_outcome,
            pred.consequent_direction.value,
            pred.consequent_magnitude.value,
            pred.consequent_mechanism,
            pred.relation_type.value,
            json.dumps([s.to_dict() for s in pred.derivation_chain]),
            json.dumps(pred.auxiliary_assumptions),
            pred.quantitative.point_estimate if pred.quantitative else None,
            pred.quantitative.ci_lower if pred.quantitative else None,
            pred.quantitative.ci_upper if pred.quantitative else None,
            pred.quantitative.functional_form if pred.quantitative else None,
            pred.generality.value,
            json.dumps(pred.applicable_populations),
            json.dumps(pred.applicable_contexts),
            json.dumps(pred.known_exceptions),
            pred.testing_status.value,
            pred.overall_support.value,
            pred.test_summary,
            pred.prior_confidence,
            pred.current_confidence,
            pred.theory_contribution,
            pred.derivation_contribution,
            pred.empirical_contribution,
            pred.uncertainty_type.value,
            pred.maps_to_edge_id,
            json.dumps(pred.maps_to_nodes),
            1 if pred.contributes_prior else 0,
            pred.prior_weight,
            pred.extraction_source,
            now,
            now,
        ))
    
    def get_theory(self, theory_id: str) -> Optional[Theory]:
        """
        Retrieve a theory by ID.
        
        Args:
            theory_id: ID of the theory to retrieve
            
        Returns:
            Theory object or None if not found
        """
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM theories WHERE theory_id = ?",
                (theory_id,)
            ).fetchone()
            
            if not row:
                return None
            
            # Build theory object
            theory = self._row_to_theory(row)
            
            # Load claims
            claims = conn.execute(
                "SELECT * FROM theory_claims WHERE theory_id = ?",
                (theory_id,)
            ).fetchall()
            theory.core_claims = [self._row_to_claim(r) for r in claims]
            
            # Load assumptions
            assumptions = conn.execute(
                "SELECT * FROM theory_assumptions WHERE theory_id = ?",
                (theory_id,)
            ).fetchall()
            theory.assumptions = [self._row_to_assumption(r) for r in assumptions]
            
            # Load boundaries
            boundaries = conn.execute(
                "SELECT * FROM theory_boundaries WHERE theory_id = ?",
                (theory_id,)
            ).fetchall()
            theory.boundary_conditions = [self._row_to_boundary(r) for r in boundaries]
            
            # Load predictions
            predictions = conn.execute(
                "SELECT * FROM predictions WHERE source_theory_id = ?",
                (theory_id,)
            ).fetchall()
            for pred_row in predictions:
                pred = self._row_to_prediction(pred_row)
                if pred.prediction_type == PredictionType.EXPLICIT:
                    theory.explicit_predictions.append(pred)
                else:
                    theory.derived_predictions.append(pred)
            
            return theory
    
    def _row_to_theory(self, row: sqlite3.Row) -> Theory:
        """Convert a database row to a Theory object."""
        return Theory(
            theory_id=row['theory_id'],
            name=row['name'],
            aliases=json.loads(row['aliases']) if row['aliases'] else [],
            originators=[Originator(**o) for o in json.loads(row['originators'])] if row['originators'] else [],
            year_introduced=row['year_introduced'],
            domain=json.loads(row['domain']) if row['domain'] else [],
            scope_description=row['scope_description'],
            level=TheoryLevel(row['level']),
            overall_confidence=row['overall_confidence'] or 0.5,
            confidence_rationale=row['confidence_rationale'],
            quantitative_precision=row['quantitative_precision'] or 'low',
            parent_theories=json.loads(row['parent_theories']) if row['parent_theories'] else [],
            child_theories=json.loads(row['child_theories']) if row['child_theories'] else [],
            compatible_theories=json.loads(row['compatible_theories']) if row['compatible_theories'] else [],
            competing_theories=json.loads(row['competing_theories']) if row['competing_theories'] else [],
            replication_status=ReplicationStatus(row['replication_status']) if row['replication_status'] else ReplicationStatus.MODERATE,
            extraction_source=row['extraction_source'],
            extracted_by=row['extracted_by'],
            version=row['version'] or 1,
            created_at=row['created_at'],
            updated_at=row['updated_at'],
        )
    
    def _row_to_claim(self, row: sqlite3.Row) -> TheoryClaim:
        """Convert a database row to a TheoryClaim object."""
        return TheoryClaim(
            claim_id=row['claim_id'],
            theory_id=row['theory_id'],
            statement=row['statement'],
            formalization=row['formalization'],
            necessity=Necessity(row['necessity']),
            testability=Testability(row['testability']),
            created_at=row['created_at'],
        )
    
    def _row_to_assumption(self, row: sqlite3.Row) -> TheoryAssumption:
        """Convert a database row to a TheoryAssumption object."""
        return TheoryAssumption(
            assumption_id=row['assumption_id'],
            theory_id=row['theory_id'],
            statement=row['statement'],
            dependent_claims=json.loads(row['dependent_claims']) if row['dependent_claims'] else [],
            violation_consequence=row['violation_consequence'],
            created_at=row['created_at'],
        )
    
    def _row_to_boundary(self, row: sqlite3.Row) -> TheoryBoundary:
        """Convert a database row to a TheoryBoundary object."""
        return TheoryBoundary(
            boundary_id=row['boundary_id'],
            theory_id=row['theory_id'],
            condition_description=row['condition_description'],
            evidence_for_boundary=json.loads(row['evidence_for_boundary']) if row['evidence_for_boundary'] else [],
            mechanism_of_failure=row['mechanism_of_failure'],
            confidence_penalty=row['confidence_penalty'] or 0.0,
            created_at=row['created_at'],
        )
    
    def _row_to_prediction(self, row: sqlite3.Row) -> Prediction:
        """Convert a database row to a Prediction object."""
        from src.models.theory_models import QuantitativePrediction
        
        quant = None
        if row['quantitative_point_estimate'] is not None:
            quant = QuantitativePrediction(
                point_estimate=row['quantitative_point_estimate'],
                ci_lower=row['quantitative_ci_lower'],
                ci_upper=row['quantitative_ci_upper'],
                functional_form=row['functional_form'],
            )
        
        derivation_chain = []
        if row['derivation_chain']:
            for step_dict in json.loads(row['derivation_chain']):
                derivation_chain.append(DerivationStep(**step_dict))
        
        return Prediction(
            prediction_id=row['prediction_id'],
            source_theory_id=row['source_theory_id'],
            statement=row['statement'],
            prediction_type=PredictionType(row['prediction_type']),
            antecedent_env_conditions=json.loads(row['antecedent_env_conditions']) if row['antecedent_env_conditions'] else [],
            antecedent_population=json.loads(row['antecedent_population']) if row['antecedent_population'] else [],
            antecedent_temporal=json.loads(row['antecedent_temporal']) if row['antecedent_temporal'] else None,
            antecedent_state=json.loads(row['antecedent_state']) if row['antecedent_state'] else [],
            consequent_outcome=row['consequent_outcome'],
            consequent_direction=Direction(row['consequent_direction']),
            consequent_magnitude=Magnitude(row['consequent_magnitude']),
            consequent_mechanism=row['consequent_mechanism'],
            relation_type=RelationType(row['relation_type']),
            derivation_chain=derivation_chain,
            auxiliary_assumptions=json.loads(row['auxiliary_assumptions']) if row['auxiliary_assumptions'] else [],
            quantitative=quant,
            generality=Generality(row['generality']),
            applicable_populations=json.loads(row['applicable_populations']) if row['applicable_populations'] else [],
            applicable_contexts=json.loads(row['applicable_contexts']) if row['applicable_contexts'] else [],
            known_exceptions=json.loads(row['known_exceptions']) if row['known_exceptions'] else [],
            testing_status=TestingStatus(row['testing_status']),
            overall_support=SupportLevel(row['overall_support']),
            test_summary=row['test_summary'],
            prior_confidence=row['prior_confidence'] or 0.5,
            current_confidence=row['current_confidence'] or 0.5,
            theory_contribution=row['theory_contribution'] or 0.0,
            derivation_contribution=row['derivation_contribution'] or 0.0,
            empirical_contribution=row['empirical_contribution'] or 0.0,
            uncertainty_type=UncertaintyType(row['uncertainty_type']) if row['uncertainty_type'] else UncertaintyType.EPISTEMIC,
            maps_to_edge_id=row['maps_to_edge_id'],
            maps_to_nodes=json.loads(row['maps_to_nodes']) if row['maps_to_nodes'] else [],
            contributes_prior=bool(row['contributes_prior']),
            prior_weight=row['prior_weight'] or 1.0,
            extraction_source=row['extraction_source'],
            created_at=row['created_at'],
            updated_at=row['updated_at'],
        )
    
    def list_theories(self, level: Optional[TheoryLevel] = None, min_confidence: float = 0.0) -> List[Theory]:
        """
        List all theories, optionally filtered.
        
        Args:
            level: Filter by theory level
            min_confidence: Minimum confidence threshold
            
        Returns:
            List of Theory objects (without predictions loaded)
        """
        with self._get_connection() as conn:
            query = "SELECT * FROM theories WHERE overall_confidence >= ?"
            params = [min_confidence]
            
            if level:
                query += " AND level = ?"
                params.append(level.value)
            
            query += " ORDER BY overall_confidence DESC"
            
            rows = conn.execute(query, params).fetchall()
            return [self._row_to_theory(r) for r in rows]
    
    def update_theory_confidence(
        self,
        theory_id: str,
        new_confidence: float,
        reason: str,
        triggered_by: Optional[str] = None
    ):
        """
        Update a theory's confidence with audit trail.
        
        Args:
            theory_id: ID of theory to update
            new_confidence: New confidence value (0.0-1.0)
            reason: Explanation for the change
            triggered_by: Paper or prediction ID that caused the update
        """
        with self._get_connection() as conn:
            # Get current confidence
            row = conn.execute(
                "SELECT overall_confidence FROM theories WHERE theory_id = ?",
                (theory_id,)
            ).fetchone()
            
            if not row:
                raise ValueError(f"Theory not found: {theory_id}")
            
            old_confidence = row['overall_confidence']
            
            # Record history
            conn.execute("""
                INSERT INTO theory_confidence_history (theory_id, old_confidence, new_confidence, change_reason, triggered_by, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (theory_id, old_confidence, new_confidence, reason, triggered_by, datetime.now(timezone.utc).isoformat()))
            
            # Update theory
            conn.execute("""
                UPDATE theories SET overall_confidence = ?, updated_at = ? WHERE theory_id = ?
            """, (new_confidence, datetime.now(timezone.utc).isoformat(), theory_id))
        
        logger.info(f"Updated theory {theory_id} confidence: {old_confidence:.3f} -> {new_confidence:.3f}")
    
    # ================================================================
    # PREDICTION OPERATIONS
    # ================================================================
    
    def get_prediction(self, prediction_id: str) -> Optional[Prediction]:
        """Retrieve a prediction by ID."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM predictions WHERE prediction_id = ?",
                (prediction_id,)
            ).fetchone()
            
            if not row:
                return None
            
            return self._row_to_prediction(row)
    
    def get_predictions_for_theory(self, theory_id: str) -> List[Prediction]:
        """Get all predictions for a theory."""
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM predictions WHERE source_theory_id = ? ORDER BY prediction_type, prediction_id",
                (theory_id,)
            ).fetchall()
            return [self._row_to_prediction(r) for r in rows]
    
    def get_untested_predictions(self, limit: int = 100) -> List[Prediction]:
        """Get predictions that have not been empirically tested."""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM predictions 
                WHERE testing_status = 'untested'
                ORDER BY prior_confidence DESC
                LIMIT ?
            """, (limit,)).fetchall()
            return [self._row_to_prediction(r) for r in rows]
    
    def get_theory_boundaries(self, theory_id: str) -> List[Dict]:
        """
        Get boundary conditions for a theory.
        
        Args:
            theory_id: ID of the theory
            
        Returns:
            List of boundary condition dicts
        """
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT boundary_id, condition_description, evidence_for_boundary,
                       mechanism_of_failure, confidence_penalty
                FROM theory_boundaries
                WHERE theory_id = ?
            """, (theory_id,)).fetchall()
            
            return [
                {
                    'boundary_id': row[0],
                    'condition_description': row[1],
                    'evidence_for_boundary': row[2],
                    'mechanism_of_failure': row[3],
                    'confidence_penalty': row[4] or 0.0
                }
                for row in rows
            ]
    
    def search_predictions(
        self,
        outcome_variable: Optional[str] = None,
        direction: Optional[Direction] = None,
        min_confidence: float = 0.0,
        testing_status: Optional[TestingStatus] = None,
    ) -> List[Prediction]:
        """
        Search predictions by various criteria.
        
        Args:
            outcome_variable: Filter by outcome (partial match)
            direction: Filter by predicted direction
            min_confidence: Minimum current confidence
            testing_status: Filter by testing status
            
        Returns:
            List of matching Predictions
        """
        with self._get_connection() as conn:
            query = "SELECT * FROM predictions WHERE current_confidence >= ?"
            params: List[Any] = [min_confidence]
            
            if outcome_variable:
                query += " AND consequent_outcome LIKE ?"
                params.append(f"%{outcome_variable}%")
            
            if direction:
                query += " AND consequent_direction = ?"
                params.append(direction.value)
            
            if testing_status:
                query += " AND testing_status = ?"
                params.append(testing_status.value)
            
            query += " ORDER BY current_confidence DESC"
            
            rows = conn.execute(query, params).fetchall()
            return [self._row_to_prediction(r) for r in rows]
    
    def add_prediction_evidence(self, evidence: PredictionEvidence):
        """
        Add evidence linking a study to a prediction test.
        
        Also updates the prediction's testing status and confidence.
        """
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO prediction_evidence (
                    prediction_id, paper_id, finding_id, test_type, result, 
                    test_strength, conditions_met, notes, confidence_delta, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                evidence.prediction_id,
                evidence.paper_id,
                evidence.finding_id,
                evidence.test_type.value,
                evidence.result.value,
                evidence.test_strength.value,
                1 if evidence.conditions_met else 0,
                evidence.notes,
                evidence.confidence_delta,
                datetime.now(timezone.utc).isoformat(),
            ))
            
            # Update prediction status
            self._update_prediction_from_evidence(conn, evidence.prediction_id)
    
    def _update_prediction_from_evidence(self, conn: sqlite3.Connection, prediction_id: str):
        """Update a prediction's status based on accumulated evidence."""
        # Get all evidence for this prediction
        evidence_rows = conn.execute("""
            SELECT result, test_strength, test_type FROM prediction_evidence
            WHERE prediction_id = ?
        """, (prediction_id,)).fetchall()
        
        if not evidence_rows:
            return
        
        # Count results
        supports = sum(1 for e in evidence_rows if e['result'] == 'supports')
        contradicts = sum(1 for e in evidence_rows if e['result'] == 'contradicts')
        nulls = sum(1 for e in evidence_rows if e['result'] == 'null')
        partial = sum(1 for e in evidence_rows if e['result'] == 'partial')
        total = len(evidence_rows)
        
        # Determine testing status
        if total >= 3:
            testing_status = TestingStatus.WELL_TESTED
        else:
            testing_status = TestingStatus.PARTIALLY_TESTED
        
        # Determine support level
        support_ratio = (supports + 0.5 * partial) / total
        if support_ratio >= 0.8:
            support = SupportLevel.STRONGLY_SUPPORTED
        elif support_ratio >= 0.6:
            support = SupportLevel.SUPPORTED
        elif support_ratio >= 0.4:
            support = SupportLevel.MIXED
        elif contradicts >= supports:
            support = SupportLevel.DISCONFIRMED if contradicts > 2 else SupportLevel.UNSUPPORTED
        else:
            support = SupportLevel.UNSUPPORTED
        
        # Update prediction
        conn.execute("""
            UPDATE predictions 
            SET testing_status = ?, overall_support = ?, updated_at = ?
            WHERE prediction_id = ?
        """, (testing_status.value, support.value, datetime.now(timezone.utc).isoformat(), prediction_id))
    
    def update_prediction_confidence(
        self,
        prediction_id: str,
        new_confidence: float,
        reason: str,
        triggered_by: Optional[str] = None
    ):
        """Update a prediction's confidence with audit trail."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT current_confidence FROM predictions WHERE prediction_id = ?",
                (prediction_id,)
            ).fetchone()
            
            if not row:
                raise ValueError(f"Prediction not found: {prediction_id}")
            
            old_confidence = row['current_confidence']
            
            # Record history
            conn.execute("""
                INSERT INTO prediction_confidence_history (prediction_id, old_confidence, new_confidence, change_reason, triggered_by, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (prediction_id, old_confidence, new_confidence, reason, triggered_by, datetime.now(timezone.utc).isoformat()))
            
            # Update prediction
            conn.execute("""
                UPDATE predictions SET current_confidence = ?, updated_at = ? WHERE prediction_id = ?
            """, (new_confidence, datetime.now(timezone.utc).isoformat(), prediction_id))
    
    # ================================================================
    # ANALYSIS OPERATIONS
    # ================================================================
    
    def get_theory_statistics(self) -> Dict[str, Any]:
        """Get summary statistics about the theory registry."""
        with self._get_connection() as conn:
            stats = {}
            
            # Theory counts by level
            level_counts = conn.execute("""
                SELECT level, COUNT(*) as count FROM theories GROUP BY level
            """).fetchall()
            stats['theories_by_level'] = {r['level']: r['count'] for r in level_counts}
            stats['total_theories'] = sum(stats['theories_by_level'].values())
            
            # Prediction counts by status
            status_counts = conn.execute("""
                SELECT testing_status, COUNT(*) as count FROM predictions GROUP BY testing_status
            """).fetchall()
            stats['predictions_by_status'] = {r['testing_status']: r['count'] for r in status_counts}
            stats['total_predictions'] = sum(stats['predictions_by_status'].values())
            
            # Average confidence
            avg_conf = conn.execute("""
                SELECT AVG(overall_confidence) as avg_conf FROM theories
            """).fetchone()
            stats['average_theory_confidence'] = round(avg_conf['avg_conf'] or 0, 3)
            
            # High-VOI predictions (untested, high prior confidence)
            high_voi = conn.execute("""
                SELECT COUNT(*) as count FROM predictions 
                WHERE testing_status = 'untested' AND prior_confidence > 0.6
            """).fetchone()
            stats['high_voi_predictions'] = high_voi['count']
            
            return stats
    
    def find_predictions_for_query(
        self,
        independent_var: str,
        dependent_var: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[Prediction, float]]:
        """
        Find predictions relevant to a specific query.
        
        This is a simplified version of the Theory Matcher component.
        
        Args:
            independent_var: The IV in the query
            dependent_var: The DV in the query
            context: Optional context constraints
            
        Returns:
            List of (Prediction, relevance_score) tuples
        """
        # Get all predictions that mention the outcome
        predictions = self.search_predictions(outcome_variable=dependent_var)
        
        results = []
        for pred in predictions:
            # Simple relevance scoring
            relevance = 0.0
            
            # Check if outcome matches
            if dependent_var.lower() in pred.consequent_outcome.lower():
                relevance += 0.5
            
            # Check if antecedent mentions IV
            antecedent_text = json.dumps(pred.antecedent_env_conditions).lower()
            if independent_var.lower() in antecedent_text:
                relevance += 0.3
            
            # Check statement for both
            statement_lower = pred.statement.lower()
            if independent_var.lower() in statement_lower:
                relevance += 0.1
            if dependent_var.lower() in statement_lower:
                relevance += 0.1
            
            # Weight by prediction confidence
            relevance *= pred.current_confidence
            
            if relevance > 0.1:
                results.append((pred, relevance))
        
        # Sort by relevance
        results.sort(key=lambda x: x[1], reverse=True)
        return results
    
    def get_competing_predictions(self, prediction_id: str) -> List[Prediction]:
        """
        Find predictions from competing theories that address the same outcome.
        """
        pred = self.get_prediction(prediction_id)
        if not pred:
            return []
        
        # Get the source theory's competing theories
        theory = self.get_theory(pred.source_theory_id)
        if not theory:
            return []
        
        competing_preds = []
        for competing_id in theory.competing_theories:
            competing_theory = self.get_theory(competing_id)
            if competing_theory:
                for cp in competing_theory.all_predictions:
                    # Check if it addresses the same outcome
                    if pred.consequent_outcome.lower() in cp.consequent_outcome.lower():
                        competing_preds.append(cp)
        
        return competing_preds


# ============================================================
# CONVENIENCE FUNCTIONS
# ============================================================

def get_registry(db_path: str = "ae.db") -> TheoryRegistry:
    """Get a TheoryRegistry instance."""
    return TheoryRegistry(db_path)
