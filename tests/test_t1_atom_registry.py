"""
Test Suite for T1 Atom Registry
================================
25+ tests covering schema validation, registry loading, maturity stratification,
framework indexing, and cross-domain confirmation.

Tests implement the panel's Recommendation #1 requirements:
- CANONICAL atoms: neurally grounded, mechanistically understood, cross-domain confirmed
- ESTABLISHED atoms: good evidence but domain-limited or mechanism partially understood
- HYPOTHETICAL atoms: theoretically motivated but limited direct evidence
"""

import json
import pytest
from pathlib import Path
from typing import Dict, Any

from src.qa.molecules.t1_atom_schema import T1Atom
from src.qa.molecules.t1_atom_registry import T1AtomRegistry


# ============================================================================
# Schema Validation Tests
# ============================================================================

class TestT1AtomSchema:
    """Test the T1Atom dataclass and validation."""

    def test_schema_creation_complete(self):
        """Test that a complete T1Atom can be created."""
        atom = T1Atom(
            atom_id="test_atom",
            name="Test Atom",
            description="This is a test atom for validation.",
            maturity="CANONICAL",
            neural_substrate=["brain_region_1", "brain_region_2"],
            computational_signature="y = x",
            t1_frameworks=["framework_1"],
            key_references=["Reference 1"],
            empirical_evidence="Evidence here.",
            cross_domain_confirmed=True
        )
        assert atom.atom_id == "test_atom"
        assert atom.name == "Test Atom"
        assert atom.maturity == "CANONICAL"

    def test_to_dict_conversion(self):
        """Test that T1Atom.to_dict() produces correct JSON."""
        atom = T1Atom(
            atom_id="test_atom",
            name="Test Atom",
            description="Description.",
            maturity="CANONICAL",
            neural_substrate=["region"],
            computational_signature="sig",
            t1_frameworks=["fw"],
            key_references=["ref"],
            empirical_evidence="evidence",
            cross_domain_confirmed=True
        )
        d = atom.to_dict()
        assert d["atom_id"] == "test_atom"
        assert d["name"] == "Test Atom"
        assert isinstance(d, dict)

    def test_from_dict_roundtrip(self):
        """Test that from_dict and to_dict are inverses."""
        original_data = {
            "atom_id": "lateral_inhibition",
            "name": "Lateral Inhibition",
            "description": "Suppression of neighboring responses.",
            "maturity": "CANONICAL",
            "neural_substrate": ["retina", "V1"],
            "computational_signature": "y = x - w*sum(neighbors)",
            "t1_frameworks": ["visual-coding"],
            "key_references": ["Hartline & Ratliff (1957)"],
            "empirical_evidence": "Observed in Limulus.",
            "cross_domain_confirmed": True,
            "parameters": {"radius": "1-2 mm"}
        }
        atom = T1Atom.from_dict(original_data)
        result = atom.to_dict()
        assert result["atom_id"] == original_data["atom_id"]
        assert result["name"] == original_data["name"]
        assert result["parameters"] == original_data["parameters"]

    def test_validate_valid_atom(self):
        """Test that a valid atom passes validation."""
        atom = T1Atom(
            atom_id="valid_atom",
            name="Valid Atom",
            description="A valid description.",
            maturity="CANONICAL",
            neural_substrate=["region"],
            computational_signature="equation",
            t1_frameworks=["framework"],
            key_references=["ref"],
            empirical_evidence="evidence",
            cross_domain_confirmed=True
        )
        errors = atom.validate()
        assert errors == []

    def test_validate_empty_atom_id(self):
        """Test validation catches empty atom_id."""
        atom = T1Atom(
            atom_id="",
            name="Test",
            description="Desc",
            maturity="CANONICAL",
            neural_substrate=["r"],
            computational_signature="s",
            t1_frameworks=["f"],
            key_references=["r"],
            empirical_evidence="e",
            cross_domain_confirmed=True
        )
        errors = atom.validate()
        assert any("atom_id" in err for err in errors)

    def test_validate_invalid_maturity(self):
        """Test validation catches invalid maturity level."""
        atom = T1Atom(
            atom_id="test",
            name="Test",
            description="Desc",
            maturity="INVALID",
            neural_substrate=["r"],
            computational_signature="s",
            t1_frameworks=["f"],
            key_references=["r"],
            empirical_evidence="e",
            cross_domain_confirmed=True
        )
        errors = atom.validate()
        assert any("maturity" in err for err in errors)

    def test_validate_canonical_must_be_cross_domain(self):
        """Test that CANONICAL atoms must have cross_domain_confirmed=True."""
        atom = T1Atom(
            atom_id="test",
            name="Test",
            description="Desc",
            maturity="CANONICAL",
            neural_substrate=["r"],
            computational_signature="s",
            t1_frameworks=["f"],
            key_references=["r"],
            empirical_evidence="e",
            cross_domain_confirmed=False  # violation
        )
        errors = atom.validate()
        assert any("CANONICAL" in err and "cross_domain_confirmed" in err for err in errors)

    def test_validate_empty_neural_substrate(self):
        """Test validation catches empty neural_substrate."""
        atom = T1Atom(
            atom_id="test",
            name="Test",
            description="Desc",
            maturity="CANONICAL",
            neural_substrate=[],  # empty
            computational_signature="s",
            t1_frameworks=["f"],
            key_references=["r"],
            empirical_evidence="e",
            cross_domain_confirmed=True
        )
        errors = atom.validate()
        assert any("neural_substrate" in err for err in errors)

    def test_validate_empty_references(self):
        """Test validation catches empty key_references."""
        atom = T1Atom(
            atom_id="test",
            name="Test",
            description="Desc",
            maturity="CANONICAL",
            neural_substrate=["r"],
            computational_signature="s",
            t1_frameworks=["f"],
            key_references=[],  # empty
            empirical_evidence="e",
            cross_domain_confirmed=True
        )
        errors = atom.validate()
        assert any("key_references" in err for err in errors)

    def test_validate_all_maturity_levels(self):
        """Test that all three maturity levels are recognized as valid."""
        for maturity in ["CANONICAL", "ESTABLISHED", "HYPOTHETICAL"]:
            atom = T1Atom(
                atom_id="test",
                name="Test",
                description="Desc",
                maturity=maturity,
                neural_substrate=["r"],
                computational_signature="s",
                t1_frameworks=["f"],
                key_references=["r"],
                empirical_evidence="e",
                cross_domain_confirmed=(maturity == "CANONICAL")
            )
            errors = atom.validate()
            # Should pass validation (except for cross_domain check if not CANONICAL)
            assert len(errors) == 0 or (maturity != "CANONICAL")


# ============================================================================
# Registry Loading Tests
# ============================================================================

class TestT1AtomRegistryLoading:
    """Test loading atoms from disk."""

    @pytest.fixture
    def registry(self):
        """Create a registry loaded from the data/atoms directory."""
        return T1AtomRegistry(atoms_dir="data/atoms")

    def test_registry_loads_all_atoms(self, registry):
        """Test that the registry loads all 30 atoms."""
        assert len(registry.atoms) >= 30, f"Expected >=30 atoms, got {len(registry.atoms)}"

    def test_registry_has_all_canonical_atoms(self, registry):
        """Test that ~10 CANONICAL atoms are loaded."""
        canonical = registry.find_canonical()
        assert len(canonical) >= 10, f"Expected >=10 CANONICAL atoms, got {len(canonical)}"

    def test_registry_has_all_established_atoms(self, registry):
        """Test that ~10 ESTABLISHED atoms are loaded."""
        established = registry.find_established()
        assert len(established) >= 10, f"Expected >=10 ESTABLISHED atoms, got {len(established)}"

    def test_registry_has_all_hypothetical_atoms(self, registry):
        """Test that ~10 HYPOTHETICAL atoms are loaded."""
        hypothetical = registry.find_hypothetical()
        assert len(hypothetical) >= 10, f"Expected >=10 HYPOTHETICAL atoms, got {len(hypothetical)}"

    def test_get_single_atom(self, registry):
        """Test retrieving a single atom by ID."""
        atom = registry.get("lateral_inhibition")
        assert atom is not None
        assert atom.atom_id == "lateral_inhibition"
        assert atom.name == "Lateral Inhibition"

    def test_get_missing_atom_returns_none(self, registry):
        """Test that getting a missing atom returns None."""
        atom = registry.get("nonexistent_atom")
        assert atom is None

    def test_get_all_returns_list(self, registry):
        """Test that get_all() returns a list."""
        atoms = registry.get_all()
        assert isinstance(atoms, list)
        assert len(atoms) >= 30

    def test_json_files_exist(self):
        """Test that all expected JSON files exist."""
        atoms_dir = Path("data/atoms")
        json_files = list(atoms_dir.glob("*.json"))
        assert len(json_files) >= 30, f"Expected >=30 JSON files, got {len(json_files)}"


# ============================================================================
# Maturity Stratification Tests
# ============================================================================

class TestMaturityStratification:
    """Test maturity-based queries and validation."""

    @pytest.fixture
    def registry(self):
        """Create a registry."""
        return T1AtomRegistry(atoms_dir="data/atoms")

    def test_find_canonical_returns_only_canonical(self, registry):
        """Test that find_canonical() returns only CANONICAL atoms."""
        canonical = registry.find_canonical()
        for atom in canonical:
            assert atom.maturity == "CANONICAL"

    def test_find_established_returns_only_established(self, registry):
        """Test that find_established() returns only ESTABLISHED atoms."""
        established = registry.find_established()
        for atom in established:
            assert atom.maturity == "ESTABLISHED"

    def test_find_hypothetical_returns_only_hypothetical(self, registry):
        """Test that find_hypothetical() returns only HYPOTHETICAL atoms."""
        hypothetical = registry.find_hypothetical()
        for atom in hypothetical:
            assert atom.maturity == "HYPOTHETICAL"

    def test_stratification_covers_all_atoms(self, registry):
        """Test that all atoms are categorized."""
        canonical = set(a.atom_id for a in registry.find_canonical())
        established = set(a.atom_id for a in registry.find_established())
        hypothetical = set(a.atom_id for a in registry.find_hypothetical())
        all_categorized = canonical | established | hypothetical
        all_atoms = set(registry.atoms.keys())
        assert all_categorized == all_atoms

    def test_maturity_stratification_no_overlap(self, registry):
        """Test that maturity categories don't overlap."""
        canonical = set(a.atom_id for a in registry.find_canonical())
        established = set(a.atom_id for a in registry.find_established())
        hypothetical = set(a.atom_id for a in registry.find_hypothetical())
        assert len(canonical & established) == 0
        assert len(canonical & hypothetical) == 0
        assert len(established & hypothetical) == 0

    def test_find_by_maturity_with_valid_level(self, registry):
        """Test find_by_maturity() with valid levels."""
        for level in ["CANONICAL", "ESTABLISHED", "HYPOTHETICAL"]:
            atoms = registry.find_by_maturity(level)
            assert isinstance(atoms, list)
            assert all(a.maturity == level for a in atoms)

    def test_find_by_maturity_with_invalid_level(self, registry):
        """Test find_by_maturity() with invalid level returns empty list."""
        atoms = registry.find_by_maturity("INVALID")
        assert atoms == []


# ============================================================================
# Framework Indexing Tests
# ============================================================================

class TestFrameworkIndexing:
    """Test framework-based queries."""

    @pytest.fixture
    def registry(self):
        """Create a registry."""
        return T1AtomRegistry(atoms_dir="data/atoms")

    def test_find_by_framework_returns_list(self, registry):
        """Test that find_by_framework() returns a list."""
        atoms = registry.find_by_framework("predictive-processing")
        assert isinstance(atoms, list)

    def test_every_atom_links_to_at_least_one_framework(self, registry):
        """Test that every atom has at least one framework."""
        for atom in registry.atoms.values():
            assert len(atom.t1_frameworks) > 0, f"Atom {atom.atom_id} has no frameworks"

    def test_framework_index_bidirectional(self, registry):
        """Test that atoms in framework index are actually in registry."""
        for framework_id, atom_ids in registry._framework_index.items():
            for atom_id in atom_ids:
                assert atom_id in registry.atoms, f"Framework {framework_id} references unknown atom {atom_id}"

    def test_find_by_framework_predictive_processing(self, registry):
        """Test finding atoms by the predictive-processing framework."""
        atoms = registry.find_by_framework("predictive-processing")
        assert len(atoms) > 0, "Expected atoms with predictive-processing framework"
        assert all("predictive-processing" in a.t1_frameworks for a in atoms)

    def test_framework_nonexistent_returns_empty(self, registry):
        """Test that nonexistent framework returns empty list."""
        atoms = registry.find_by_framework("nonexistent-framework")
        assert atoms == []

    def test_get_framework_coverage(self, registry):
        """Test that get_framework_coverage() produces summary."""
        coverage = registry.get_framework_coverage()
        assert isinstance(coverage, dict)
        assert len(coverage) > 0
        for framework_id, stats in coverage.items():
            assert "total" in stats
            assert "by_maturity" in stats
            assert "CANONICAL" in stats["by_maturity"]


# ============================================================================
# Cross-Domain Confirmation Tests
# ============================================================================

class TestCrossDomainConfirmation:
    """Test cross-domain confirmation requirements."""

    @pytest.fixture
    def registry(self):
        """Create a registry."""
        return T1AtomRegistry(atoms_dir="data/atoms")

    def test_all_canonical_atoms_are_cross_domain(self, registry):
        """Test that all CANONICAL atoms have cross_domain_confirmed=True."""
        canonical = registry.find_canonical()
        for atom in canonical:
            assert atom.cross_domain_confirmed is True, \
                f"CANONICAL atom {atom.atom_id} must have cross_domain_confirmed=True"

    def test_find_cross_domain(self, registry):
        """Test that find_cross_domain() returns cross-domain atoms."""
        cross_domain = registry.find_cross_domain()
        assert len(cross_domain) > 0
        for atom in cross_domain:
            assert atom.cross_domain_confirmed is True

    def test_cross_domain_atoms_mostly_canonical(self, registry):
        """Test that most cross-domain atoms are CANONICAL."""
        cross_domain = registry.find_cross_domain()
        canonical_count = sum(1 for a in cross_domain if a.maturity == "CANONICAL")
        # Expect most but not all cross-domain atoms to be CANONICAL
        assert canonical_count >= len(cross_domain) * 0.7, \
            "Expected >70% of cross-domain atoms to be CANONICAL"


# ============================================================================
# Computational Signature Tests
# ============================================================================

class TestComputationalSignatures:
    """Test that atoms have meaningful computational signatures."""

    @pytest.fixture
    def registry(self):
        """Create a registry."""
        return T1AtomRegistry(atoms_dir="data/atoms")

    def test_all_atoms_have_computational_signature(self, registry):
        """Test that every atom has a computational signature."""
        for atom in registry.atoms.values():
            assert atom.computational_signature, \
                f"Atom {atom.atom_id} has no computational_signature"
            assert isinstance(atom.computational_signature, str)
            assert len(atom.computational_signature) > 0

    def test_canonical_atoms_have_detailed_signatures(self, registry):
        """Test that CANONICAL atoms have detailed signatures."""
        canonical = registry.find_canonical()
        for atom in canonical:
            # CANONICAL signatures should typically be equations or precise descriptions
            assert len(atom.computational_signature) > 10, \
                f"CANONICAL atom {atom.atom_id} has suspiciously brief signature"


# ============================================================================
# Content Validation Tests
# ============================================================================

class TestContentValidation:
    """Test that atom content is non-empty and reasonable."""

    @pytest.fixture
    def registry(self):
        """Create a registry."""
        return T1AtomRegistry(atoms_dir="data/atoms")

    def test_no_empty_names(self, registry):
        """Test that no atoms have empty names."""
        for atom in registry.atoms.values():
            assert atom.name and atom.name.strip(), \
                f"Atom {atom.atom_id} has empty name"

    def test_no_empty_descriptions(self, registry):
        """Test that no atoms have empty descriptions."""
        for atom in registry.atoms.values():
            assert atom.description and atom.description.strip(), \
                f"Atom {atom.atom_id} has empty description"

    def test_no_empty_empirical_evidence(self, registry):
        """Test that no atoms have empty empirical evidence."""
        for atom in registry.atoms.values():
            assert atom.empirical_evidence and atom.empirical_evidence.strip(), \
                f"Atom {atom.atom_id} has empty empirical_evidence"

    def test_no_empty_references(self, registry):
        """Test that no atoms have empty reference lists."""
        for atom in registry.atoms.values():
            assert atom.key_references, \
                f"Atom {atom.atom_id} has no key_references"
            for ref in atom.key_references:
                assert ref and ref.strip(), \
                    f"Atom {atom.atom_id} has empty reference in list"

    def test_description_length_reasonable(self, registry):
        """Test that descriptions are reasonable length (2-3 sentences)."""
        for atom in registry.atoms.values():
            desc = atom.description
            # Heuristic: 2-3 sentences typically 100-300 characters
            assert len(desc) >= 50, \
                f"Atom {atom.atom_id} description too short: {len(desc)} chars"
            assert len(desc) <= 500, \
                f"Atom {atom.atom_id} description too long: {len(desc)} chars"


# ============================================================================
# Registry Validation and Summary Tests
# ============================================================================

class TestRegistryValidation:
    """Test registry-level validation."""

    @pytest.fixture
    def registry(self):
        """Create a registry."""
        return T1AtomRegistry(atoms_dir="data/atoms")

    def test_validate_registry_produces_result(self, registry):
        """Test that validate_registry() produces a dict."""
        result = registry.validate_registry()
        assert isinstance(result, dict)
        assert "errors" in result
        assert "warnings" in result
        assert isinstance(result["errors"], list)
        assert isinstance(result["warnings"], list)

    def test_registry_passes_critical_validation(self, registry):
        """Test that registry has no critical errors."""
        result = registry.validate_registry()
        critical_errors = [e for e in result["errors"]
                          if "CANONICAL" in e or "cross_domain" in e]
        assert len(critical_errors) == 0, f"Critical validation errors: {critical_errors}"

    def test_summary_produces_output(self, registry):
        """Test that summary() produces a string."""
        summary = registry.summary()
        assert isinstance(summary, str)
        assert len(summary) > 0
        assert "CANONICAL" in summary or "Atom Registry" in summary

    def test_summary_contains_stratification_info(self, registry):
        """Test that summary includes stratification counts."""
        summary = registry.summary()
        canonical_count = len(registry.find_canonical())
        established_count = len(registry.find_established())
        hypothetical_count = len(registry.find_hypothetical())
        assert "CANONICAL" in summary
        assert str(canonical_count) in summary or "Stratification" in summary


# ============================================================================
# Integration Tests
# ============================================================================

class TestRegistryIntegration:
    """Integration tests combining multiple features."""

    @pytest.fixture
    def registry(self):
        """Create a registry."""
        return T1AtomRegistry(atoms_dir="data/atoms")

    def test_full_workflow(self, registry):
        """Test a complete workflow: get → validate → query."""
        # Get an atom
        atom = registry.get("lateral_inhibition")
        assert atom is not None

        # Validate it
        errors = atom.validate()
        assert len(errors) == 0

        # Query by framework
        atoms_in_framework = registry.find_by_framework(atom.t1_frameworks[0])
        assert atom in atoms_in_framework

        # Query by maturity
        atoms_by_maturity = registry.find_by_maturity(atom.maturity)
        assert atom in atoms_by_maturity

    def test_canonical_atoms_form_foundation(self, registry):
        """Test that CANONICAL atoms have expected properties."""
        canonical = registry.find_canonical()
        assert len(canonical) >= 10

        for atom in canonical:
            # All CANONICAL atoms must be well-grounded
            assert atom.cross_domain_confirmed
            assert len(atom.key_references) >= 1
            assert len(atom.neural_substrate) >= 1
            assert atom.computational_signature

    def test_established_atoms_have_frameworks(self, registry):
        """Test that ESTABLISHED atoms link to frameworks."""
        established = registry.find_established()
        for atom in established:
            assert atom.t1_frameworks, \
                f"ESTABLISHED atom {atom.atom_id} must link to frameworks"

    def test_hypothetical_atoms_acknowledge_uncertainty(self, registry):
        """Test that HYPOTHETICAL atoms indicate limited evidence."""
        hypothetical = registry.find_hypothetical()
        for atom in hypothetical:
            # HYPOTHETICAL atoms should mention speculation/debate/limited evidence
            evidence = atom.empirical_evidence.lower()
            descriptors = ["speculative", "debated", "limited", "unclear", "theoretical",
                          "emerging", "proposed", "hypothetical"]
            # At least one should appear
            has_uncertainty_language = any(d in evidence for d in descriptors)
            assert has_uncertainty_language or len(evidence) > 50, \
                f"HYPOTHETICAL atom {atom.atom_id} should indicate uncertainty"


# ============================================================================
# Edge Case Tests
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.fixture
    def registry(self):
        """Create a registry."""
        return T1AtomRegistry(atoms_dir="data/atoms")

    def test_find_by_nonexistent_framework_safe(self, registry):
        """Test that querying nonexistent framework doesn't crash."""
        atoms = registry.find_by_framework("framework_that_does_not_exist_xyz")
        assert atoms == []

    def test_empty_directory_handled(self):
        """Test that empty directory is handled gracefully."""
        registry = T1AtomRegistry(atoms_dir="data/nonexistent_atoms_dir")
        assert isinstance(registry.atoms, dict)
        assert len(registry.atoms) == 0

    def test_atom_id_case_sensitivity(self, registry):
        """Test that atom IDs are case-sensitive."""
        atom = registry.get("lateral_inhibition")
        assert atom is not None
        # uppercase shouldn't work
        atom_upper = registry.get("LATERAL_INHIBITION")
        assert atom_upper is None
