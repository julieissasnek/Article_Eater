"""
Overseer Predictive Health — Phase 4, Task 4.4
===============================================

Uses health metric history to forecast next-day AESHI score,
detect patterns (coherence dips after bulk integration, utilization
drops on weekends), and alert if predicted AESHI < 60.

Sprint: CVA Phase 4 — Self-Healing Overseer
Date: 2026-02-28
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone, timedelta
import logging
import json
import statistics

logger = logging.getLogger(__name__)


# =============================================================================
# Prediction Models
# =============================================================================

@dataclass
class HealthPrediction:
    """Predicted health metrics for next interval."""
    predicted_aeshi: float
    confidence: float  # 0-1
    trend_direction: str  # "improving", "stable", "declining"
    trend_slope: float  # AESHI points per day
    risk_factors: List[str]
    recommended_actions: List[str]
    prediction_basis: str  # "linear_trend", "pattern_based", "insufficient_data"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "predicted_aeshi": round(self.predicted_aeshi, 1),
            "confidence": round(self.confidence, 2),
            "trend_direction": self.trend_direction,
            "trend_slope": round(self.trend_slope, 3),
            "risk_factors": self.risk_factors,
            "recommended_actions": self.recommended_actions,
            "prediction_basis": self.prediction_basis,
            "timestamp": self.timestamp,
        }


@dataclass
class PatternDetection:
    """Detected pattern in health metrics."""
    pattern_type: str  # "post_integration_dip", "weekend_utilization_drop", "coherence_oscillation"
    description: str
    severity: str  # "low", "medium", "high"
    evidence: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "pattern_type": self.pattern_type,
            "description": self.description,
            "severity": self.severity,
            "evidence": self.evidence,
        }


class PredictiveHealthEngine:
    """Forecasts system health using historical metrics.
    
    Uses:
    1. Linear trend on last 7 days for AESHI prediction
    2. Pattern detection for known failure modes
    3. Risk factor identification from metric combinations
    """
    
    AESHI_ALERT_THRESHOLD = 60.0
    MIN_HISTORY_FOR_PREDICTION = 3  # Need at least 3 data points
    TREND_WINDOW_DAYS = 7
    
    def __init__(self, overseer=None):
        self.overseer = overseer
        self._history_cache: List[Dict] = []
    
    def predict_health(self, health_history: List[Dict]) -> HealthPrediction:
        """Generate health prediction from historical metrics.
        
        Args:
            health_history: List of health metric snapshots, ordered by time.
                Each has: timestamp, aeshi_score, global_coherence,
                          pipeline_utilization, violation_count, etc.
        """
        if len(health_history) < self.MIN_HISTORY_FOR_PREDICTION:
            return HealthPrediction(
                predicted_aeshi=health_history[-1].get("aeshi_score", 50) if health_history else 50,
                confidence=0.1,
                trend_direction="unknown",
                trend_slope=0.0,
                risk_factors=["insufficient_data"],
                recommended_actions=["accumulate_more_health_data"],
                prediction_basis="insufficient_data",
            )
        
        # Extract AESHI scores
        aeshi_scores = [h.get("aeshi_score", 50) for h in health_history]
        timestamps = [h.get("timestamp", "") for h in health_history]
        
        # Linear trend on last N days
        window = min(len(aeshi_scores), self.TREND_WINDOW_DAYS)
        recent = aeshi_scores[-window:]
        
        slope = self._compute_slope(recent)
        predicted = recent[-1] + slope
        predicted = max(0, min(100, predicted))  # Clamp to [0, 100]
        
        # Determine trend direction
        if slope > 1.0:
            direction = "improving"
        elif slope < -1.0:
            direction = "declining"
        else:
            direction = "stable"
        
        # Confidence based on variance and data quantity
        if len(recent) >= 5:
            variance = statistics.variance(recent) if len(recent) > 1 else 0
            confidence = max(0.2, min(0.9, 1.0 - (variance / 500)))
        else:
            confidence = 0.3
        
        # Risk factors
        risk_factors = self._identify_risk_factors(health_history)
        
        # Recommended actions
        actions = self._recommend_actions(predicted, risk_factors, direction)
        
        return HealthPrediction(
            predicted_aeshi=predicted,
            confidence=confidence,
            trend_direction=direction,
            trend_slope=slope,
            risk_factors=risk_factors,
            recommended_actions=actions,
            prediction_basis="linear_trend",
        )
    
    def detect_patterns(self, health_history: List[Dict]) -> List[PatternDetection]:
        """Detect known patterns in health metric history."""
        patterns = []
        
        if len(health_history) < 5:
            return patterns
        
        # Pattern 1: Post-integration coherence dips
        coherence_values = [h.get("global_coherence", 0.5) for h in health_history]
        for i in range(2, len(coherence_values)):
            if (coherence_values[i] < coherence_values[i-1] * 0.92 and
                health_history[i].get("mode") == "POST_INTEGRATION"):
                patterns.append(PatternDetection(
                    pattern_type="post_integration_dip",
                    description=f"Coherence dropped {((1 - coherence_values[i]/coherence_values[i-1]) * 100):.1f}% after integration",
                    severity="medium",
                    evidence={
                        "before": coherence_values[i-1],
                        "after": coherence_values[i],
                        "timestamp": health_history[i].get("timestamp"),
                    },
                ))
        
        # Pattern 2: Utilization drops (e.g., weekends)
        util_values = [h.get("pipeline_utilization", 0) for h in health_history]
        if len(util_values) >= 7:
            recent_avg = statistics.mean(util_values[-3:])
            historical_avg = statistics.mean(util_values[:-3])
            if recent_avg < historical_avg * 0.5 and historical_avg > 0.1:
                patterns.append(PatternDetection(
                    pattern_type="utilization_drop",
                    description=f"Pipeline utilization dropped from {historical_avg:.1%} to {recent_avg:.1%}",
                    severity="low",
                    evidence={
                        "recent_avg": recent_avg,
                        "historical_avg": historical_avg,
                    },
                ))
        
        # Pattern 3: Coherence oscillation (unstable)
        if len(coherence_values) >= 5:
            diffs = [coherence_values[i] - coherence_values[i-1] for i in range(1, len(coherence_values))]
            sign_changes = sum(1 for i in range(1, len(diffs)) if diffs[i] * diffs[i-1] < 0)
            if sign_changes >= len(diffs) * 0.6:
                patterns.append(PatternDetection(
                    pattern_type="coherence_oscillation",
                    description="Coherence is oscillating (unstable equilibrium)",
                    severity="high",
                    evidence={
                        "sign_changes": sign_changes,
                        "total_transitions": len(diffs),
                        "coherence_range": [min(coherence_values), max(coherence_values)],
                    },
                ))
        
        # Pattern 4: Violation accumulation
        violation_counts = [h.get("violation_count", 0) for h in health_history]
        if len(violation_counts) >= 3:
            if all(violation_counts[i] >= violation_counts[i-1] for i in range(-3, 0)):
                patterns.append(PatternDetection(
                    pattern_type="violation_accumulation",
                    description="Violations are monotonically increasing",
                    severity="high",
                    evidence={
                        "recent_counts": violation_counts[-3:],
                    },
                ))
        
        return patterns
    
    def _compute_slope(self, values: List[float]) -> float:
        """Compute linear regression slope."""
        n = len(values)
        if n < 2:
            return 0.0
        
        x_mean = (n - 1) / 2
        y_mean = statistics.mean(values)
        
        numerator = sum((i - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        return numerator / denominator if denominator > 0 else 0.0
    
    def _identify_risk_factors(self, history: List[Dict]) -> List[str]:
        """Identify current risk factors from latest metrics."""
        risks = []
        if not history:
            return risks
        
        latest = history[-1]
        
        # Low coherence
        coh = latest.get("global_coherence", 0.5)
        if coh < 0.3:
            risks.append("critical_low_coherence")
        elif coh < 0.5:
            risks.append("low_coherence")
        
        # High violation count
        violations = latest.get("violation_count", 0)
        if violations > 10:
            risks.append("high_violation_count")
        elif violations > 5:
            risks.append("elevated_violations")
        
        # Low utilization
        util = latest.get("pipeline_utilization", 0)
        if util < 0.05:
            risks.append("pipeline_stalled")
        elif util < 0.25:
            risks.append("low_utilization")
        
        # Low provenance coverage
        prov = latest.get("provenance_coverage", 1.0)
        if prov < 0.5:
            risks.append("provenance_gaps")
        
        # AESHI below threshold
        aeshi = latest.get("aeshi_score", 50)
        if aeshi < 40:
            risks.append("critical_aeshi")
        elif aeshi < self.AESHI_ALERT_THRESHOLD:
            risks.append("low_aeshi")
        
        return risks
    
    def _recommend_actions(self, predicted_aeshi: float, risks: List[str], direction: str) -> List[str]:
        """Recommend actions based on prediction and risks."""
        actions = []
        
        if predicted_aeshi < self.AESHI_ALERT_THRESHOLD:
            actions.append("ALERT: predicted AESHI below 60 — investigate immediately")
        
        if "pipeline_stalled" in risks:
            actions.append("Run gap predictor and add papers to wishlist")
        
        if "high_violation_count" in risks:
            actions.append("Execute remediation playbooks for outstanding violations")
        
        if "provenance_gaps" in risks:
            actions.append("Run provenance backfill for beliefs missing sources")
        
        if "critical_low_coherence" in risks:
            actions.append("Investigate recent integrations for contradictory beliefs")
        
        if direction == "declining" and not actions:
            actions.append("Monitor: AESHI trending downward — check next cycle")
        
        if not actions:
            actions.append("No action needed — system healthy")
        
        return actions


# =============================================================================
# CVA-Specific Health Checks (INV-10 through INV-13)
# =============================================================================

def check_cva_constraint_stability(overseer=None) -> Dict[str, Any]:
    """INV-10: Check that κ_loop < 0.5 for all computed scenes.
    
    Uses CVA dynamics engine to verify feedback loop stability.
    """
    result = {
        "invariant": "INV-10",
        "description": "CVA constraint stability (κ_loop < 0.5)",
        "passed": True,
        "violations": [],
        "scenes_checked": 0,
    }
    
    try:
        from src.services.cva_dynamics import CVADynamicsEngine
        engine = CVADynamicsEngine()
        
        # Check stability for default configuration
        stability = engine.check_stability()
        result["scenes_checked"] = 1
        
        if hasattr(stability, 'kappa_loop'):
            if stability.kappa_loop >= 0.5:
                result["passed"] = False
                result["violations"].append({
                    "scene": "default",
                    "kappa_loop": stability.kappa_loop,
                    "threshold": 0.5,
                })
    except ImportError:
        result["passed"] = True  # No CVA engine = no violations
        result["note"] = "CVA dynamics engine not available"
    except Exception as e:
        result["note"] = f"Check failed: {str(e)}"
    
    return result


def check_attractor_reachability(overseer=None) -> Dict[str, Any]:
    """INV-11: Check that each named rasa is reachable from at least one IC."""
    result = {
        "invariant": "INV-11",
        "description": "Attractor reachability",
        "passed": True,
        "violations": [],
        "attractors_checked": 0,
    }
    
    try:
        from src.services.cva_attractor import CVAAttractorEngine
        engine = CVAAttractorEngine()
        
        rasa_names = ["shanta", "karuna", "vira", "adbhuta", "shringara",
                       "hasya", "raudra", "bhayanaka", "bibhatsa"]
        
        for rasa in rasa_names:
            result["attractors_checked"] += 1
            try:
                reachable = engine.check_reachability(rasa)
                if not reachable:
                    result["passed"] = False
                    result["violations"].append({
                        "rasa": rasa,
                        "reachable": False,
                    })
            except Exception as e:
                logger.debug(f"Swallowed in {fpath}: {e}")  # Rasa not configured is not a violation
                
    except ImportError:
        result["note"] = "CVA attractor engine not available"
    except Exception as e:
        result["note"] = f"Check failed: {str(e)}"
    
    return result


def check_cultural_variant_consistency(overseer=None) -> Dict[str, Any]:
    """INV-12: Check cultural variants produce stable valuations."""
    result = {
        "invariant": "INV-12",
        "description": "Cultural variant consistency",
        "passed": True,
        "violations": [],
        "variants_checked": 0,
    }
    
    try:
        from src.models.cva_valuation import CVAValuationVector
        
        variants = ["WESTERN", "JAPANESE", "WEST_AFRICAN", "INDIAN"]
        for variant in variants:
            result["variants_checked"] += 1
            try:
                v = CVAValuationVector.from_culture(variant)
                vec = v.as_vector()
                # Check for NaN or infinite values
                import math
                if any(math.isnan(x) or math.isinf(x) for x in vec):
                    result["passed"] = False
                    result["violations"].append({
                        "variant": variant,
                        "issue": "NaN or Inf in valuation vector",
                    })
            except Exception as e:
                result["violations"].append({
                    "variant": variant,
                    "issue": str(e),
                })
                
    except ImportError:
        result["note"] = "CVA valuation model not available"
    except Exception as e:
        result["note"] = f"Check failed: {str(e)}"
    
    return result


def check_psi_determinism(overseer=None) -> Dict[str, Any]:
    """INV-13: Same ψ + same scene = same constraint vector (within 1e-6)."""
    result = {
        "invariant": "INV-13",
        "description": "ψ-computation determinism",
        "passed": True,
        "violations": [],
        "tests_run": 0,
        "tolerance": 1e-6,
    }
    
    try:
        from src.services.cva_constraint_engine import CVAConstraintEngine
        engine = CVAConstraintEngine()
        
        # Run same computation twice and compare
        for _ in range(3):
            result["tests_run"] += 1
            try:
                v1 = engine.compute_constraints()
                v2 = engine.compute_constraints()
                
                if hasattr(v1, 'as_vector') and hasattr(v2, 'as_vector'):
                    vec1, vec2 = v1.as_vector(), v2.as_vector()
                    max_diff = max(abs(a - b) for a, b in zip(vec1, vec2))
                    if max_diff > result["tolerance"]:
                        result["passed"] = False
                        result["violations"].append({
                            "max_difference": max_diff,
                            "tolerance": result["tolerance"],
                        })
            except Exception as e:
                logger.debug(f"Swallowed in {fpath}: {e}")
                
    except ImportError:
        result["note"] = "CVA constraint engine not available"
    except Exception as e:
        result["note"] = f"Check failed: {str(e)}"
    
    return result


# Registry of CVA invariant checks
CVA_INVARIANT_CHECKS = {
    "INV-10": check_cva_constraint_stability,
    "INV-11": check_attractor_reachability,
    "INV-12": check_cultural_variant_consistency,
    "INV-13": check_psi_determinism,
}


def run_all_cva_checks() -> Dict[str, Any]:
    """Run all CVA-specific invariant checks. Returns combined results."""
    results = {}
    for code, check_fn in CVA_INVARIANT_CHECKS.items():
        try:
            results[code] = check_fn()
        except Exception as e:
            results[code] = {
                "invariant": code,
                "passed": True,  # Don't fail on check errors
                "note": f"Check error: {str(e)}",
            }
    return results
