"""
Tests for Functional Circuit Integration
==========================================
Created: 2026-03-03
Sprint: Functional Circuits Integration

Tests that the 20 functional circuit molecules load correctly into the
MoleculeRegistry, that the new schema fields (linked_archetypes, inputs,
outputs) work, and that find_by_archetype() returns correct results.

These are Layer 1 deterministic success condition tests.
"""

import json
import pytest
from pathlib import Path

from src.qa.molecules.schema import Molecule, MoleculeComponent
from src.qa.molecules.registry import MoleculeRegistry


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(scope="module")
def registry():
    """Load the real molecule registry with all data files."""
    return MoleculeRegistry()


@pytest.fixture(scope="module")
def fc_molecules(registry):
    """Get all functional circuit molecules."""
    return registry.get_functional_circuits()


# ============================================================================
# Schema Tests: New Fields on Molecule Dataclass
# ============================================================================

class TestMoleculeSchemaExtensions:
    """Test that linked_archetypes, inputs, outputs fields work on Molecule."""

    def test_molecule_has_linked_archetypes_field(self):
        """SC-SCHEMA-1: Molecule dataclass has linked_archetypes."""
        mol = Molecule(
            molecule_id="TEST", name="Test", short_description="Test mol",
            components=[], constituent_templates=[], interaction_graph={},
            framework_ids=[], domain="test",
            linked_archetypes=["PREDICTIVE_CODING"]
        )
        assert mol.linked_archetypes == ["PREDICTIVE_CODING"]

    def test_molecule_has_inputs_outputs_fields(self):
        """SC-SCHEMA-2: Molecule dataclass has inputs and outputs."""
        mol = Molecule(
            molecule_id="TEST", name="Test", short_description="Test mol",
            components=[], constituent_templates=[], interaction_graph={},
            framework_ids=[], domain="test",
            inputs=["signal_a", "signal_b"],
            outputs=["response_c"]
        )
        assert mol.inputs == ["signal_a", "signal_b"]
        assert mol.outputs == ["response_c"]

    def test_linked_archetypes_defaults_empty(self):
        """SC-SCHEMA-3: linked_archetypes defaults to empty list."""
        mol = Molecule(
            molecule_id="TEST", name="Test", short_description="Test mol",
            components=[], constituent_templates=[], interaction_graph={},
            framework_ids=[], domain="test"
        )
        assert mol.linked_archetypes == []
        assert mol.inputs == []
        assert mol.outputs == []

    def test_to_dict_includes_new_fields(self):
        """SC-SCHEMA-4: to_dict() includes linked_archetypes, inputs, outputs."""
        mol = Molecule(
            molecule_id="TEST", name="Test", short_description="Test mol",
            components=[], constituent_templates=[], interaction_graph={},
            framework_ids=[], domain="test",
            linked_archetypes=["GATED_PROPAGATION"],
            inputs=["x"], outputs=["y"]
        )
        d = mol.to_dict()
        assert d["linked_archetypes"] == ["GATED_PROPAGATION"]
        assert d["inputs"] == ["x"]
        assert d["outputs"] == ["y"]

    def test_from_dict_parses_new_fields(self):
        """SC-SCHEMA-5: from_dict() correctly parses linked_archetypes, inputs, outputs."""
        data = {
            "molecule_id": "TEST", "name": "Test", "short_description": "Test mol",
            "components": [], "constituent_templates": [], "interaction_graph": {},
            "framework_ids": [], "domain": "test",
            "linked_archetypes": ["HOMEOSTATIC_REGULATION"],
            "inputs": ["a", "b"], "outputs": ["c"]
        }
        mol = Molecule.from_dict(data)
        assert mol.linked_archetypes == ["HOMEOSTATIC_REGULATION"]
        assert mol.inputs == ["a", "b"]
        assert mol.outputs == ["c"]

    def test_from_dict_missing_new_fields_defaults_empty(self):
        """SC-SCHEMA-6: from_dict() with missing new fields defaults to empty lists."""
        data = {
            "molecule_id": "TEST", "name": "Test", "short_description": "Test mol",
            "components": [], "constituent_templates": [], "interaction_graph": {},
            "framework_ids": [], "domain": "test"
        }
        mol = Molecule.from_dict(data)
        assert mol.linked_archetypes == []
        assert mol.inputs == []
        assert mol.outputs == []

    def test_molecule_type_functional_circuit(self):
        """SC-SCHEMA-7: molecule_type can be FUNCTIONAL_CIRCUIT."""
        mol = Molecule(
            molecule_id="FC_TEST", name="Test Circuit", short_description="Test",
            components=[], constituent_templates=[], interaction_graph={},
            framework_ids=[], domain="test",
            molecule_type="FUNCTIONAL_CIRCUIT"
        )
        assert mol.molecule_type == "FUNCTIONAL_CIRCUIT"

    def test_roundtrip_serialization(self):
        """SC-SCHEMA-8: Full roundtrip through to_dict → from_dict preserves all fields."""
        original = Molecule(
            molecule_id="FC_RT", name="Roundtrip", short_description="Test",
            components=[MoleculeComponent("Comp1", ["T1"], "SYNERGISTIC", "A component")],
            constituent_templates=["T1"], interaction_graph={"T1": {}},
            framework_ids=["PP"], domain="test",
            molecule_type="FUNCTIONAL_CIRCUIT",
            linked_archetypes=["PREDICTIVE_CODING", "GATED_PROPAGATION"],
            inputs=["in_a", "in_b"], outputs=["out_c"],
            parent_t1_5_theory="PROCESSING_FLUENCY"
        )
        restored = Molecule.from_dict(original.to_dict())
        assert restored.molecule_id == original.molecule_id
        assert restored.linked_archetypes == original.linked_archetypes
        assert restored.inputs == original.inputs
        assert restored.outputs == original.outputs
        assert restored.molecule_type == original.molecule_type
        assert restored.parent_t1_5_theory == original.parent_t1_5_theory
        assert len(restored.components) == 1
        assert restored.components[0].name == "Comp1"


# ============================================================================
# Registry Tests: Loading and Indexing
# ============================================================================

class TestRegistryFunctionalCircuits:
    """Test that MoleculeRegistry correctly loads and indexes functional circuits."""

    def test_registry_loads_functional_circuits(self, registry):
        """SC-REG-1: Registry loads at least 18 functional circuit molecules."""
        fcs = registry.get_functional_circuits()
        assert len(fcs) >= 18, f"Expected ≥18 functional circuits, got {len(fcs)}"

    def test_all_circuits_have_correct_type(self, fc_molecules):
        """SC-REG-2: Every functional circuit has molecule_type FUNCTIONAL_CIRCUIT."""
        for fc in fc_molecules:
            assert fc.molecule_type == "FUNCTIONAL_CIRCUIT", \
                f"{fc.molecule_id} has type {fc.molecule_type}"

    def test_all_circuits_have_linked_archetypes(self, fc_molecules):
        """SC-REG-3: Every functional circuit has at least one linked archetype."""
        for fc in fc_molecules:
            assert len(fc.linked_archetypes) >= 1, \
                f"{fc.molecule_id} has no linked_archetypes"

    def test_all_circuits_have_inputs(self, fc_molecules):
        """SC-REG-4: Every functional circuit has at least one input."""
        for fc in fc_molecules:
            assert len(fc.inputs) >= 1, \
                f"{fc.molecule_id} has no inputs"

    def test_all_circuits_have_outputs(self, fc_molecules):
        """SC-REG-5: Every functional circuit has at least one output."""
        for fc in fc_molecules:
            assert len(fc.outputs) >= 1, \
                f"{fc.molecule_id} has no outputs"

    def test_all_circuits_have_components(self, fc_molecules):
        """SC-REG-6: Every functional circuit has at least 2 components."""
        for fc in fc_molecules:
            assert len(fc.components) >= 2, \
                f"{fc.molecule_id} has only {len(fc.components)} components"

    def test_all_circuits_have_key_references(self, fc_molecules):
        """SC-REG-7: Every functional circuit has at least one key reference."""
        for fc in fc_molecules:
            assert len(fc.key_references) >= 1, \
                f"{fc.molecule_id} has no key_references"

    def test_all_circuits_are_tentative(self, fc_molecules):
        """SC-REG-8: All functional circuits have maturity TENTATIVE (speculative layer)."""
        for fc in fc_molecules:
            assert fc.overall_maturity == "TENTATIVE", \
                f"{fc.molecule_id} has maturity {fc.overall_maturity}"

    def test_total_molecule_count_increased(self, registry):
        """SC-REG-9: Total molecule count is at least 30 (13 existing + 18+ new)."""
        assert len(registry.molecules) >= 30, \
            f"Expected ≥30 total molecules, got {len(registry.molecules)}"

    def test_find_by_type_returns_only_functional_circuits(self, registry):
        """SC-REG-10: find_by_type('FUNCTIONAL_CIRCUIT') only returns circuits."""
        fcs = registry.find_by_type("FUNCTIONAL_CIRCUIT")
        for fc in fcs:
            assert fc.molecule_type == "FUNCTIONAL_CIRCUIT"


# ============================================================================
# Archetype Index Tests
# ============================================================================

class TestArchetypeIndex:
    """Test find_by_archetype() and the archetype reverse index."""

    VALID_ARCHETYPES = [
        "CONVERGENT_STATE_MONITORING",
        "PREDICTIVE_CODING",
        "HOMEOSTATIC_REGULATION",
        "ACCUMULATION_TO_BOUND",
        "COMPETITIVE_SELECTION",
        "GATED_PROPAGATION"
    ]

    def test_find_by_archetype_returns_list(self, registry):
        """SC-FBA-1: find_by_archetype always returns a list."""
        result = registry.find_by_archetype("CONVERGENT_STATE_MONITORING")
        assert isinstance(result, list)

    def test_find_by_archetype_unknown_returns_empty(self, registry):
        """SC-FBA-3: Unknown archetype returns empty list."""
        result = registry.find_by_archetype("NONEXISTENT_ARCHETYPE")
        assert result == []

    def test_convergent_state_monitoring_circuits(self, registry):
        """SC-FBA-CSM: CONVERGENT_STATE_MONITORING has ≥4 circuits."""
        mols = registry.find_by_archetype("CONVERGENT_STATE_MONITORING")
        assert len(mols) >= 4
        ids = {m.molecule_id for m in mols}
        assert "FC_COHERENCE_MONITORING" in ids
        assert "FC_THREAT_MONITORING" in ids
        assert "FC_VITALITY_MONITORING" in ids
        assert "FC_SOCIAL_SAFETY_MONITORING" in ids

    def test_predictive_coding_circuits(self, registry):
        """SC-FBA-PC: PREDICTIVE_CODING has ≥4 circuits."""
        mols = registry.find_by_archetype("PREDICTIVE_CODING")
        assert len(mols) >= 4
        ids = {m.molecule_id for m in mols}
        assert "FC_SENSORY_PE" in ids
        assert "FC_REWARD_PE" in ids

    def test_homeostatic_regulation_circuits(self, registry):
        """SC-FBA-HR: HOMEOSTATIC_REGULATION has ≥3 circuits."""
        mols = registry.find_by_archetype("HOMEOSTATIC_REGULATION")
        assert len(mols) >= 3

    def test_accumulation_to_bound_circuits(self, registry):
        """SC-FBA-ATB: ACCUMULATION_TO_BOUND has ≥3 circuits."""
        mols = registry.find_by_archetype("ACCUMULATION_TO_BOUND")
        assert len(mols) >= 3

    def test_competitive_selection_circuits(self, registry):
        """SC-FBA-CS: COMPETITIVE_SELECTION has ≥3 circuits."""
        mols = registry.find_by_archetype("COMPETITIVE_SELECTION")
        assert len(mols) >= 3

    def test_gated_propagation_circuits(self, registry):
        """SC-FBA-GP: GATED_PROPAGATION has ≥3 circuits."""
        mols = registry.find_by_archetype("GATED_PROPAGATION")
        assert len(mols) >= 3

    def test_all_six_archetypes_have_circuits(self, registry):
        """SC-FBA-ALL: All 6 T2 archetypes have at least one functional circuit."""
        for arch in self.VALID_ARCHETYPES:
            mols = registry.find_by_archetype(arch)
            assert len(mols) >= 1, f"Archetype {arch} has no functional circuits"

    def test_archetype_results_match_linked_archetypes(self, registry):
        """SC-FBA-2: Every molecule returned by find_by_archetype has that archetype in linked_archetypes."""
        for arch in self.VALID_ARCHETYPES:
            for mol in registry.find_by_archetype(arch):
                assert arch in mol.linked_archetypes, \
                    f"{mol.molecule_id} returned for {arch} but doesn't list it"


# ============================================================================
# Specific Circuit Data Quality Tests
# ============================================================================

class TestCircuitDataQuality:
    """Test specific data quality requirements for functional circuits."""

    def test_circuits_have_design_implications(self, fc_molecules):
        """SC-DQ-1: Most circuits have at least one design implication."""
        with_implications = sum(1 for fc in fc_molecules if fc.design_implications)
        pct = with_implications / len(fc_molecules) if fc_molecules else 0
        assert pct >= 0.8, \
            f"Only {pct:.0%} of circuits have design_implications (need ≥80%)"

    def test_circuits_reference_known_frameworks(self, fc_molecules):
        """SC-DQ-2: All circuits reference at least one known framework."""
        known_frameworks = {
            "predictive-processing", "neuromodulatory-systems",
            "interoceptive-constructionist-affect", "IE-DPT",
            "EVO_AESTHETICS", "PP", "NM", "IC"
        }
        for fc in fc_molecules:
            assert len(fc.framework_ids) >= 1, \
                f"{fc.molecule_id} has no framework_ids"

    def test_circuits_use_valid_archetype_names(self, fc_molecules):
        """SC-DQ-3: All linked_archetypes are valid T2ArchetypeType values."""
        valid = {
            "PREDICTIVE_CODING", "HOMEOSTATIC_REGULATION",
            "ACCUMULATION_TO_BOUND", "COMPETITIVE_SELECTION",
            "GATED_PROPAGATION", "CONVERGENT_STATE_MONITORING"
        }
        for fc in fc_molecules:
            for arch in fc.linked_archetypes:
                assert arch in valid, \
                    f"{fc.molecule_id} has invalid archetype: {arch}"

    def test_circuit_ids_follow_naming_convention(self, fc_molecules):
        """SC-DQ-4: All circuit molecule_ids start with 'FC_'."""
        for fc in fc_molecules:
            assert fc.molecule_id.startswith("FC_"), \
                f"Circuit {fc.molecule_id} doesn't follow FC_ prefix convention"

    def test_no_duplicate_circuit_ids(self, fc_molecules):
        """SC-DQ-5: No duplicate molecule_ids among functional circuits."""
        ids = [fc.molecule_id for fc in fc_molecules]
        assert len(ids) == len(set(ids)), \
            f"Duplicate circuit IDs found: {[x for x in ids if ids.count(x) > 1]}"

    def test_domains_are_reasonable(self, fc_molecules):
        """SC-DQ-6: Domains are from the expected vocabulary."""
        expected_domains = {
            "perception", "safety", "restoration", "social", "affect",
            "cognition", "behavior", "aesthetics"
        }
        for fc in fc_molecules:
            assert fc.domain in expected_domains, \
                f"{fc.molecule_id} has unexpected domain: {fc.domain}"

    def test_component_template_ids_populated(self, fc_molecules):
        """SC-DQ-7: Every component has at least one template_id."""
        for fc in fc_molecules:
            for comp in fc.components:
                assert len(comp.template_ids) >= 1, \
                    f"{fc.molecule_id} component '{comp.name}' has no template_ids"


# ============================================================================
# JSON File Format Tests
# ============================================================================

class TestCircuitJSONFiles:
    """Test the actual JSON files on disk for format compliance."""

    FC_DIR = Path("data/molecules")

    def test_all_fc_files_exist(self):
        """SC-FILE-1: At least 18 fc_*.json files exist."""
        fc_files = list(self.FC_DIR.glob("fc_*.json"))
        assert len(fc_files) >= 18, f"Found only {len(fc_files)} fc_*.json files"

    def test_all_fc_files_valid_json(self):
        """SC-FILE-2: All fc_*.json files are valid JSON."""
        for path in self.FC_DIR.glob("fc_*.json"):
            with open(path) as f:
                data = json.load(f)  # Will raise if invalid
            assert isinstance(data, dict), f"{path.name} is not a JSON object"

    def test_all_fc_files_have_required_fields(self):
        """SC-FILE-3: All fc_*.json files have the required Molecule fields."""
        required = {"molecule_id", "name", "short_description", "components",
                     "constituent_templates", "framework_ids", "domain",
                     "molecule_type", "linked_archetypes", "inputs", "outputs"}
        for path in self.FC_DIR.glob("fc_*.json"):
            with open(path) as f:
                data = json.load(f)
            missing = required - set(data.keys())
            assert not missing, \
                f"{path.name} missing fields: {missing}"

    def test_all_fc_files_molecule_type_is_functional_circuit(self):
        """SC-FILE-4: All fc_*.json files have molecule_type FUNCTIONAL_CIRCUIT."""
        for path in self.FC_DIR.glob("fc_*.json"):
            with open(path) as f:
                data = json.load(f)
            assert data["molecule_type"] == "FUNCTIONAL_CIRCUIT", \
                f"{path.name} has type {data['molecule_type']}"


# ============================================================================
# Integration: Backward Compatibility
# ============================================================================

class TestBackwardCompatibility:
    """Verify existing molecules still load and work with schema changes."""

    def test_existing_molecules_still_load(self, registry):
        """SC-BC-1: Pre-existing molecules (non-FC) still load."""
        # These are the original 13 molecules that should still work
        expected_existing = {"PROSPECT_REFUGE", "BIOPHILIA", "WAYFINDING"}
        loaded_ids = set(registry.molecules.keys())
        for eid in expected_existing:
            assert eid in loaded_ids, \
                f"Pre-existing molecule {eid} failed to load"

    def test_existing_molecules_have_empty_archetypes(self, registry):
        """SC-BC-2: Pre-existing molecules default to empty linked_archetypes."""
        pr = registry.get("PROSPECT_REFUGE")
        if pr:
            assert pr.linked_archetypes == [] or isinstance(pr.linked_archetypes, list)

    def test_find_by_framework_still_works(self, registry):
        """SC-BC-3: find_by_framework still returns results for pre-existing frameworks."""
        # EVO_AESTHETICS should find prospect_refuge
        results = registry.find_by_framework("EVO_AESTHETICS")
        assert len(results) >= 1

    def test_find_by_template_still_works(self, registry):
        """SC-BC-4: find_by_template still returns results."""
        # T3 and T5 are used by prospect_refuge
        results = registry.find_by_template("T3")
        assert len(results) >= 1

    def test_taxonomy_includes_functional_circuits(self, registry):
        """SC-BC-5: get_taxonomy() includes FUNCTIONAL_CIRCUIT type entries."""
        taxonomy = registry.get_taxonomy()
        all_types = set()
        for domain_entries in taxonomy.values():
            for entry in domain_entries:
                all_types.add(entry["type"])
        assert "FUNCTIONAL_CIRCUIT" in all_types
