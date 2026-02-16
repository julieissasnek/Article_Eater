"""
Tests for rule_to_claim_mapper (Sprint 6 Bridge).

Verifies that ae.rule.v2 rules from PDF extraction are correctly
converted to Sprint 6 ClaimV2 objects with proper NodeType assignment.
"""

import pytest
import json
from pathlib import Path

from src.epistemic.extraction.rule_to_claim_mapper import (
    map_rule_type_to_node_type,
    rule_to_claim_v2,
    rule_to_edge_v2,
    convert_rules_to_sprint6,
    load_and_convert_rules_jsonl,
    extract_statement_from_rule,
    RULE_TYPE_TO_NODE_TYPE,
)
from src.epistemic.node_types import NodeType
from src.epistemic.contracts.claim_v2 import ClaimV2


# =============================================================================
# MAPPING TESTS
# =============================================================================

class TestRuleTypeMapping:
    """Test rule_type to NodeType mapping."""

    def test_edge_maps_to_empirical_finding(self):
        """Edge rules → EMPIRICAL_FINDING."""
        assert map_rule_type_to_node_type("edge") == NodeType.EMPIRICAL_FINDING

    def test_presumption_maps_to_theoretical_proposition(self):
        """Presumption rules → THEORETICAL_PROPOSITION."""
        assert map_rule_type_to_node_type("presumption") == NodeType.THEORETICAL_PROPOSITION

    def test_association_maps_to_empirical_finding(self):
        """Association rules → EMPIRICAL_FINDING."""
        assert map_rule_type_to_node_type("association") == NodeType.EMPIRICAL_FINDING

    def test_constraint_maps_to_conceptual_constraint(self):
        """Constraint rules → CONCEPTUAL_CONSTRAINT."""
        assert map_rule_type_to_node_type("constraint") == NodeType.CONCEPTUAL_CONSTRAINT

    def test_rebuttal_maps_to_methodological_critique(self):
        """Rebuttal rules → METHODOLOGICAL_CRITIQUE."""
        assert map_rule_type_to_node_type("rebuttal") == NodeType.METHODOLOGICAL_CRITIQUE

    def test_cpd_hint_returns_none(self):
        """BN metadata rules → None (not a node)."""
        assert map_rule_type_to_node_type("cpd_hint") is None

    def test_prior_returns_none(self):
        """Prior rules → None (not a node)."""
        assert map_rule_type_to_node_type("prior") is None


# =============================================================================
# STATEMENT EXTRACTION TESTS
# =============================================================================

class TestStatementExtraction:
    """Test statement extraction from rule structure."""

    def test_positive_relationship(self):
        """Positive polarity generates correct statement."""
        rule = {
            "lhs": [{"var": "env.lighting_colour", "state": "present"}],
            "rhs": [{"var": "cog.thermal_comfort_perception", "state": "affected"}],
            "polarity": "positive",
        }
        statement = extract_statement_from_rule(rule)
        assert "lighting colour" in statement.lower()
        assert "thermal comfort perception" in statement.lower()
        assert "positively affects" in statement

    def test_negative_relationship(self):
        """Negative polarity generates correct statement."""
        rule = {
            "lhs": [{"var": "env.noise", "state": "present"}],
            "rhs": [{"var": "cog.concentration", "state": "affected"}],
            "polarity": "negative",
        }
        statement = extract_statement_from_rule(rule)
        assert "negatively affects" in statement

    def test_null_relationship(self):
        """Null polarity generates correct statement."""
        rule = {
            "lhs": [{"var": "env.color", "state": "present"}],
            "rhs": [{"var": "cog.memory", "state": "affected"}],
            "polarity": "null",
        }
        statement = extract_statement_from_rule(rule)
        assert "has no effect on" in statement

    def test_multiple_lhs_variables(self):
        """Multiple LHS variables are joined."""
        rule = {
            "lhs": [
                {"var": "env.light", "state": "present"},
                {"var": "env.temperature", "state": "present"},
            ],
            "rhs": [{"var": "aff.comfort", "state": "affected"}],
            "polarity": "positive",
        }
        statement = extract_statement_from_rule(rule)
        assert "light" in statement.lower()
        assert "temperature" in statement.lower()
        assert "and" in statement.lower()


# =============================================================================
# CLAIM CONVERSION TESTS
# =============================================================================

class TestRuleToClaimConversion:
    """Test conversion of rules to ClaimV2."""

    def test_edge_rule_becomes_claim(self):
        """Edge rule converts to ClaimV2."""
        rule = {
            "schema": "ae.rule.v2",
            "rule_id": "test_paper#r01",
            "paper_id": "test_paper",
            "rule_type": "edge",
            "lhs": [{"var": "env.daylight", "state": "present"}],
            "rhs": [{"var": "aff.mood", "state": "affected"}],
            "polarity": "positive",
            "ae_confidence": 0.75,
            "causal_level": "association",
        }
        claim = rule_to_claim_v2(rule)

        assert claim is not None
        assert claim.node_type == NodeType.EMPIRICAL_FINDING.value
        assert claim.node_id == "test_paper#r01"
        assert claim.paper_id == "test_paper"
        assert claim.ae_confidence == 0.75
        assert claim.causal_level == "association"
        assert "daylight" in claim.statement.lower()

    def test_presumption_rule_becomes_theoretical_proposition(self):
        """Presumption rule converts to THEORETICAL_PROPOSITION."""
        rule = {
            "rule_id": "theory_paper#r01",
            "paper_id": "theory_paper",
            "rule_type": "presumption",
            "lhs": [{"var": "theory.biophilia", "state": "present"}],
            "rhs": [{"var": "aff.wellbeing", "state": "affected"}],
            "polarity": "positive",
            "ae_confidence": 0.55,
        }
        claim = rule_to_claim_v2(rule)

        assert claim is not None
        assert claim.node_type == NodeType.THEORETICAL_PROPOSITION.value
        assert claim.evidence_level == "theoretical"

    def test_rebuttal_rule_becomes_critique(self):
        """Rebuttal rule converts to METHODOLOGICAL_CRITIQUE."""
        rule = {
            "rule_id": "critique_paper#r01",
            "paper_id": "critique_paper",
            "rule_type": "rebuttal",
            "lhs": [{"var": "theory.biophilia_hypothesis", "state": "present"}],
            "rhs": [{"var": "misc.theoretical_validity", "state": "affected"}],
            "polarity": "negative",
            "ae_confidence": 0.55,
        }
        claim = rule_to_claim_v2(rule)

        assert claim is not None
        assert claim.node_type == NodeType.METHODOLOGICAL_CRITIQUE.value
        assert claim.evidence_level == "critique"

    def test_cpd_hint_returns_none(self):
        """BN metadata rules don't become claims."""
        rule = {
            "rule_id": "bn_only#r01",
            "paper_id": "bn_paper",
            "rule_type": "cpd_hint",
            "lhs": [],
            "rhs": [],
            "polarity": "unknown",
            "ae_confidence": 0.5,
        }
        claim = rule_to_claim_v2(rule)
        assert claim is None

    def test_argumentative_metadata_preserved(self):
        """Panel additions (argument_scheme, etc.) are preserved."""
        rule = {
            "rule_id": "arg_paper#r01",
            "paper_id": "arg_paper",
            "rule_type": "edge",
            "lhs": [{"var": "env.x", "state": "present"}],
            "rhs": [{"var": "cog.y", "state": "affected"}],
            "polarity": "positive",
            "ae_confidence": 0.6,
            "argument_scheme": "causal_argument",
            "critical_questions": ["Is the causal mechanism plausible?"],
            "contrast_class": "no_exposure",
            "difference_maker": "environmental_exposure",
        }
        claim = rule_to_claim_v2(rule)

        assert claim.argument_scheme == "causal_argument"
        assert "Is the causal mechanism plausible?" in claim.critical_questions
        assert claim.contrast_class == "no_exposure"
        assert claim.difference_maker == "environmental_exposure"


# =============================================================================
# EDGE CONVERSION TESTS
# =============================================================================

class TestRuleToEdgeConversion:
    """Test conversion of rules to BN edges."""

    def test_edge_rule_creates_bn_edge(self):
        """Edge rule creates BN edge."""
        rule = {
            "rule_id": "edge_test#r01",
            "paper_id": "edge_paper",
            "rule_type": "edge",
            "lhs": [{"var": "env.light", "state": "present"}],
            "rhs": [{"var": "cog.alertness", "state": "affected"}],
            "polarity": "positive",
            "strength": {"kind": "effect_size", "value": 0.4},
            "bn_mapping": {
                "node_suggestions": ["env.light", "cog.alertness"],
                "discretization_hint": "low/med/high",
            },
        }
        edge = rule_to_edge_v2(rule)

        assert edge is not None
        assert edge.source_node_id == "bn:env.light"
        assert edge.target_node_id == "bn:cog.alertness"
        assert edge.weight == 0.4  # From effect size

    def test_presumption_rule_no_edge(self):
        """Presumption rules don't create BN edges."""
        rule = {
            "rule_id": "presump#r01",
            "paper_id": "theory_paper",
            "rule_type": "presumption",
            "lhs": [{"var": "theory.x", "state": "present"}],
            "rhs": [{"var": "aff.y", "state": "affected"}],
            "polarity": "positive",
        }
        edge = rule_to_edge_v2(rule)
        assert edge is None


# =============================================================================
# BATCH CONVERSION TESTS
# =============================================================================

class TestBatchConversion:
    """Test batch conversion of rules."""

    def test_convert_multiple_rules(self):
        """Batch conversion handles multiple rules."""
        rules = [
            {
                "rule_id": "paper1#r01",
                "paper_id": "paper1",
                "rule_type": "edge",
                "lhs": [{"var": "env.x", "state": "present"}],
                "rhs": [{"var": "cog.y", "state": "affected"}],
                "polarity": "positive",
                "ae_confidence": 0.6,
            },
            {
                "rule_id": "paper2#r01",
                "paper_id": "paper2",
                "rule_type": "presumption",
                "lhs": [{"var": "theory.a", "state": "present"}],
                "rhs": [{"var": "aff.b", "state": "affected"}],
                "polarity": "positive",
                "ae_confidence": 0.5,
            },
            {
                "rule_id": "paper3#r01",
                "paper_id": "paper3",
                "rule_type": "cpd_hint",  # Should be skipped
                "lhs": [],
                "rhs": [],
                "polarity": "unknown",
                "ae_confidence": 0.5,
            },
        ]

        result = convert_rules_to_sprint6(rules)

        assert result.total_claims == 2  # edge + presumption
        assert result.skipped_bn_metadata == 1  # cpd_hint
        assert len(result.errors) == 0

        # Check node type distribution
        summary = result.summary()
        assert summary["node_type_distribution"]["empirical_finding"] == 1
        assert summary["node_type_distribution"]["theoretical_proposition"] == 1


# =============================================================================
# REAL DATA TESTS
# =============================================================================

class TestRealDataConversion:
    """Test conversion with real PDF extraction data."""

    @pytest.fixture
    def rules_file(self):
        """Path to real rules file."""
        path = Path(__file__).parent.parent / "data" / "rules.jsonl"
        if not path.exists():
            pytest.skip(f"Rules file not found: {path}")
        return path

    def test_load_and_convert_real_rules(self, rules_file):
        """Load and convert real rules from JSONL."""
        result = load_and_convert_rules_jsonl(str(rules_file))

        # Should have at least some claims
        assert result.total_claims > 0

        # Should have no errors
        assert len(result.errors) == 0

        # Check distribution
        summary = result.summary()
        print(f"\n=== Real Data Conversion Summary ===")
        print(f"Total claims: {summary['total_claims']}")
        print(f"Total edges: {summary['total_edges']}")
        print(f"Skipped (BN metadata): {summary['skipped_bn_metadata']}")
        print(f"Node type distribution: {summary['node_type_distribution']}")

        # All node types should be valid
        for claim in result.claims:
            assert claim.node_type in [nt.value for nt in NodeType]

    def test_real_rules_have_valid_statements(self, rules_file):
        """Real rules produce valid statements."""
        result = load_and_convert_rules_jsonl(str(rules_file))

        for claim in result.claims[:10]:  # Check first 10
            assert claim.statement
            assert len(claim.statement) > 10
            assert "affects" in claim.statement or "effect" in claim.statement.lower()

    def test_real_rules_preserve_paper_ids(self, rules_file):
        """Real rules preserve paper IDs."""
        result = load_and_convert_rules_jsonl(str(rules_file))

        for claim in result.claims:
            assert claim.paper_id
            assert "doi:" in claim.paper_id or "sha256:" in claim.paper_id


# =============================================================================
# NODE TYPE COVERAGE TEST
# =============================================================================

class TestNodeTypeCoverage:
    """Verify all expected rule types are mapped."""

    def test_all_rule_types_have_mapping(self):
        """All ae.rule.v2 rule_type values have a mapping."""
        expected_rule_types = [
            "edge", "cpd_hint", "prior", "constraint",
            "interaction", "rebuttal", "presumption",
            "association", "contrast"
        ]

        for rt in expected_rule_types:
            # Should not raise KeyError
            result = map_rule_type_to_node_type(rt)
            # Either maps to a NodeType or None (for BN metadata)
            assert result is None or isinstance(result, NodeType)
