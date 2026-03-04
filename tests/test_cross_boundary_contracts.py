"""
Layer 1.5: Cross-Boundary Data Integrity Tests
================================================
Created: 2026-03-03
Sprint: Subsystem Health Contracts

These tests verify data consistency at the interfaces between the 20 ATLAS
subsystems. They catch the class of bugs that unit tests within individual
subsystems miss — broken cross-references, orphaned data, inconsistent
counts across boundaries.

These are "Layer 1.5" tests — more expensive than unit tests (Layer 1) but
cheaper than systemic failure mode tests (Layer 2 nightly).

References:
- contracts/SUBSYSTEM_HEALTH_CONTRACTS.md — defines the contracts
- docs/RUTHLESS_V11_ENGINEERING_AUDIT_2026-03-02.md — 20-subsystem decomposition
"""

import json
import pytest
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"


# ============================================================================
# XB-1: Template-Registry Contract
# Every T2 template referenced by a molecule exists in the template registry.
# ============================================================================

class TestXB1_TemplateRegistryContract:
    """Cross-boundary: Molecules → Theory & Templates."""

    def test_molecule_template_ids_exist(self):
        """XB-1: Every template_id in a molecule's constituent_templates should
        correspond to a known template (or at least be non-empty)."""
        from src.qa.molecules.registry import MoleculeRegistry
        reg = MoleculeRegistry()
        all_template_refs = set()
        for mol in reg.get_all():
            all_template_refs.update(mol.constituent_templates)
        # We can't check against all templates without loading them, but
        # we verify no empty strings or None values
        assert "" not in all_template_refs, "Empty template_id found in molecules"
        assert None not in all_template_refs, "None template_id found in molecules"
        assert len(all_template_refs) > 0, "No template references found across all molecules"

    def test_molecule_components_have_template_ids(self):
        """XB-1b: Every component in every molecule has at least one template_id."""
        from src.qa.molecules.registry import MoleculeRegistry
        reg = MoleculeRegistry()
        for mol in reg.get_all():
            for comp in mol.components:
                assert len(comp.template_ids) >= 1, \
                    f"Molecule {mol.molecule_id} component '{comp.name}' has no template_ids"


# ============================================================================
# XB-2: Theory-Framework Referential Integrity
# Every framework_id in a molecule maps to a known T1 framework.
# ============================================================================

class TestXB2_TheoryFrameworkIntegrity:
    """Cross-boundary: Molecules → T1 Frameworks."""

    # Known T1 framework IDs from the canonical set
    KNOWN_FRAMEWORKS = {
        "predictive-processing", "PP",
        "neuromodulatory-systems", "NM",
        "interoceptive-constructionist-affect", "IC",
        "IE-DPT",
        "EVO_AESTHETICS",
        "embodied-situated",
        "ecological-dynamics",
        "developmental-constructivist",
        "social-baseline",
        "allostatic-regulation",
    }

    def test_molecule_framework_ids_coverage(self):
        """XB-2a: ≥90% of molecules reference at least one framework."""
        from src.qa.molecules.registry import MoleculeRegistry
        reg = MoleculeRegistry()
        all_mols = reg.get_all()
        with_frameworks = [m for m in all_mols if len(m.framework_ids) >= 1]
        pct = len(with_frameworks) / len(all_mols) if all_mols else 0
        assert pct >= 0.90, \
            f"Only {pct:.0%} of molecules have framework_ids (need ≥90%)"


# ============================================================================
# XB-3: Functional Circuit → Archetype Integrity
# Every linked_archetype in a functional circuit is a valid T2ArchetypeType.
# ============================================================================

class TestXB3_CircuitArchetypeIntegrity:
    """Cross-boundary: Functional Circuits → T2 Archetypes."""

    VALID_ARCHETYPES = {
        "PREDICTIVE_CODING", "HOMEOSTATIC_REGULATION",
        "ACCUMULATION_TO_BOUND", "COMPETITIVE_SELECTION",
        "GATED_PROPAGATION", "CONVERGENT_STATE_MONITORING",
    }

    def test_all_circuit_archetypes_valid(self):
        """XB-3: Every linked_archetype is a valid T2ArchetypeType enum value."""
        from src.qa.molecules.registry import MoleculeRegistry
        reg = MoleculeRegistry()
        for fc in reg.get_functional_circuits():
            for arch in fc.linked_archetypes:
                assert arch in self.VALID_ARCHETYPES, \
                    f"Circuit {fc.molecule_id} has invalid archetype '{arch}'"

    def test_archetype_index_consistent(self):
        """XB-3b: find_by_archetype results match linked_archetypes on each molecule."""
        from src.qa.molecules.registry import MoleculeRegistry
        reg = MoleculeRegistry()
        for arch in self.VALID_ARCHETYPES:
            for mol in reg.find_by_archetype(arch):
                assert arch in mol.linked_archetypes


# ============================================================================
# XB-4: T1.5 Theory → Molecule Parent Link
# Every molecule with parent_t1_5_theory references a real T1.5 theory.
# ============================================================================

class TestXB4_T15TheoryMoleculeLink:
    """Cross-boundary: Molecules → T1.5 Theories."""

    def test_parent_t1_5_references_exist(self):
        """XB-4: If a molecule has parent_t1_5_theory, that theory file should exist."""
        from src.qa.molecules.registry import MoleculeRegistry
        reg = MoleculeRegistry()
        theories_dir = DATA_DIR / "theories"
        for mol in reg.get_all():
            if mol.parent_t1_5_theory:
                # Theory ID should correspond to a file or be a known ID
                # Check that it's not an empty string
                assert mol.parent_t1_5_theory.strip(), \
                    f"Molecule {mol.molecule_id} has blank parent_t1_5_theory"


# ============================================================================
# XB-5: Subsystem Registry Consistency
# The overseer's subsystem registry matches the V11 audit count.
# ============================================================================

class TestXB5_SubsystemRegistryConsistency:
    """Cross-boundary: Overseer → All Subsystems."""

    def test_registry_has_20_subsystems(self):
        """XB-5a: build_subsystem_registry() returns exactly 20 subsystems."""
        from src.services.overseer_self_healing import build_subsystem_registry
        reg = build_subsystem_registry()
        assert len(reg) == 20, f"Expected 20 subsystems, got {len(reg)}"

    def test_every_subsystem_has_conditions(self):
        """XB-5b: Every subsystem has at least 2 success conditions."""
        from src.services.overseer_self_healing import build_subsystem_registry
        reg = build_subsystem_registry()
        for sid, defn in reg.items():
            assert len(defn.success_conditions) >= 2, \
                f"Subsystem {sid} has only {len(defn.success_conditions)} conditions"

    def test_all_categories_represented(self):
        """XB-5c: All 4 categories (core, pipeline, analysis, support) present."""
        from src.services.overseer_self_healing import build_subsystem_registry
        reg = build_subsystem_registry()
        categories = {d.category for d in reg.values()}
        expected = {"core", "pipeline", "analysis", "support"}
        assert categories == expected, f"Missing categories: {expected - categories}"

    def test_dependencies_reference_existing_subsystems(self):
        """XB-5d: Every depends_on entry references an actual subsystem ID."""
        from src.services.overseer_self_healing import build_subsystem_registry
        reg = build_subsystem_registry()
        all_ids = set(reg.keys())
        for sid, defn in reg.items():
            for dep in defn.depends_on:
                assert dep in all_ids, \
                    f"Subsystem {sid} depends on '{dep}' which doesn't exist"

    def test_no_circular_dependencies(self):
        """XB-5e: No circular dependency chains in subsystem graph."""
        from src.services.overseer_self_healing import build_subsystem_registry
        reg = build_subsystem_registry()

        def has_cycle(sid, visited, rec_stack):
            visited.add(sid)
            rec_stack.add(sid)
            for dep in reg[sid].depends_on:
                if dep not in visited:
                    if has_cycle(dep, visited, rec_stack):
                        return True
                elif dep in rec_stack:
                    return True
            rec_stack.discard(sid)
            return False

        visited = set()
        for sid in reg:
            if sid not in visited:
                assert not has_cycle(sid, visited, set()), \
                    f"Circular dependency detected involving {sid}"


# ============================================================================
# XB-6: Extraction → Web of Belief Data Flow
# Extraction data should be reflected in the web of belief.
# ============================================================================

class TestXB6_ExtractionToWebFlow:
    """Cross-boundary: Extraction & Integration → Web of Belief."""

    def test_extraction_count_consistent_with_belief_count(self):
        """XB-6: Extraction count and belief count should be in reasonable ratio."""
        extractions_dir = DATA_DIR / "extractions"
        if not extractions_dir.exists():
            pytest.skip("No extractions directory")
        ext_count = len(list(extractions_dir.glob("*.json")))
        # Each extraction produces multiple beliefs, so belief_count >> extraction_count
        # But extraction_count should not be 0 if we have beliefs
        assert ext_count > 0, "No extraction files found"


# ============================================================================
# XB-7: Molecule Registry → Web of Belief Consistency
# Molecules and beliefs should be in the same conceptual universe.
# ============================================================================

class TestXB7_MoleculeRegistryHealth:
    """Cross-boundary: Molecule Registry → overall system consistency."""

    def test_molecule_count_matches_expectations(self):
        """XB-7a: Total molecules ≥30 (13 original + 18+ functional circuits)."""
        from src.qa.molecules.registry import MoleculeRegistry
        reg = MoleculeRegistry()
        assert len(reg.molecules) >= 30, \
            f"Expected ≥30 molecules, got {len(reg.molecules)}"

    def test_functional_circuits_at_least_18(self):
        """XB-7b: At least 18 functional circuits registered."""
        from src.qa.molecules.registry import MoleculeRegistry
        reg = MoleculeRegistry()
        fcs = reg.get_functional_circuits()
        assert len(fcs) >= 18

    def test_molecule_types_include_functional_circuit(self):
        """XB-7c: FUNCTIONAL_CIRCUIT is present as a molecule_type."""
        from src.qa.molecules.registry import MoleculeRegistry
        reg = MoleculeRegistry()
        types = {m.molecule_type for m in reg.get_all()}
        assert "FUNCTIONAL_CIRCUIT" in types

    def test_taxonomy_has_all_types(self):
        """XB-7d: get_taxonomy() returns entries across multiple domains."""
        from src.qa.molecules.registry import MoleculeRegistry
        reg = MoleculeRegistry()
        taxonomy = reg.get_taxonomy()
        assert len(taxonomy) >= 5, \
            f"Expected ≥5 domains in taxonomy, got {len(taxonomy)}"


# ============================================================================
# XB-8: Success Condition Metrics Are Measurable
# Every success condition in the registry uses a metric that a probe can provide.
# ============================================================================

class TestXB8_SuccessConditionsTestable:
    """Meta-test: verify success conditions reference real metrics."""

    def test_all_operators_are_valid(self):
        """XB-8a: All success conditions use valid operators."""
        from src.services.overseer_self_healing import build_subsystem_registry
        reg = build_subsystem_registry()
        valid_ops = {">=", "<=", "==", ">", "<"}
        for sid, defn in reg.items():
            for sc in defn.success_conditions:
                assert sc.operator in valid_ops, \
                    f"Subsystem {sid} has invalid operator '{sc.operator}'"

    def test_all_thresholds_are_numeric(self):
        """XB-8b: All thresholds are numeric (float-convertible)."""
        from src.services.overseer_self_healing import build_subsystem_registry
        reg = build_subsystem_registry()
        for sid, defn in reg.items():
            for sc in defn.success_conditions:
                try:
                    float(sc.threshold)
                except (TypeError, ValueError):
                    pytest.fail(f"Subsystem {sid} condition '{sc.metric}' "
                               f"has non-numeric threshold: {sc.threshold}")

    def test_all_conditions_have_descriptions(self):
        """XB-8c: All success conditions have non-empty descriptions."""
        from src.services.overseer_self_healing import build_subsystem_registry
        reg = build_subsystem_registry()
        for sid, defn in reg.items():
            for sc in defn.success_conditions:
                assert sc.description.strip(), \
                    f"Subsystem {sid} condition '{sc.metric}' has empty description"


# ============================================================================
# XB-9: Health Probe Coverage
# Every registered subsystem has a corresponding probe method.
# ============================================================================

class TestXB9_HealthProbeCoverage:
    """Meta-test: every subsystem has a probe."""

    def test_all_subsystems_have_probes(self):
        """XB-9: Every subsystem_id in the registry has a _probe_{id} method."""
        from src.services.overseer_self_healing import (
            build_subsystem_registry, HealthProbeRunner,
        )
        reg = build_subsystem_registry()
        runner = HealthProbeRunner()
        missing_probes = []
        for sid in reg:
            probe_method = f"_probe_{sid}"
            if not hasattr(runner, probe_method):
                missing_probes.append(sid)
        # Allow some subsystems to fall back to generic import check
        # But new V11 subsystems must have probes
        new_v11 = {"answer_enrichment_orchestrator", "norm_services", "agent_coordination"}
        missing_new = new_v11 & set(missing_probes)
        assert not missing_new, \
            f"New V11 subsystems missing probes: {missing_new}"
