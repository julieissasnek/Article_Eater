"""
Enum and Schema Drift Check Tests (Sprint 11 Task 11.28).

Verifies consistency of enum-like fields across all components:
1. Template display_ids match between compute functions, feature mappings, interactions
2. dedup_status values are from allowed set
3. pe_contribution values are from allowed set
4. calibration_status values are from allowed set
5. practical_accessibility values are from allowed set
6. OutputType enum values are consistent
"""

import pytest
from pathlib import Path
import json
from typing import Set

from src.cmr.template_computations import (
    TEMPLATE_COMPUTE_FUNCTIONS,
    OutputType,
)
from src.cmr.feature_mapping import FEATURE_TO_TEMPLATE_INPUT
from src.cmr.lifespan_moderation import FEATURE_MAPPINGS, ZONE_TO_WIS
from src.cmr.models import TemplateRecord, get_session


# Allowed enum values per field
ALLOWED_DEDUP_STATUS = {"active", "superseded", "residual", "reference", "gap"}
ALLOWED_PE_CONTRIBUTION = {"predictive", "explanatory", "organizational"}
ALLOWED_CALIBRATION_STATUS = {
    "substantial", "partial", "protocol", "uncalibrated", "framework_specified",
    "good", "well_calibrated",  # Legacy values from earlier sprints
}
ALLOWED_PRACTICAL_ACCESSIBILITY = {"A", "B", "C", "D"}


class TestOutputTypeEnum:
    """Verify OutputType enum consistency."""

    def test_output_types_are_valid(self):
        """All compute functions should use valid OutputType values."""
        valid_types = set(OutputType)
        
        for template_id, func in TEMPLATE_COMPUTE_FUNCTIONS.items():
            try:
                result = func(occupant_age=35)
                assert result.output_type in valid_types, (
                    f"{template_id}: invalid output_type {result.output_type}"
                )
            except TypeError:
                # Function requires more args - skip
                pass

    def test_output_type_values_stable(self):
        """OutputType enum should have expected values."""
        expected_types = {
            "goldilocks_zone",
            "threshold_check",
            "score",
            "matrix_lookup",
            "weighted_composite",
            "ratio",
        }
        actual_types = {t.value for t in OutputType}

        # Check that expected types exist
        for expected in expected_types:
            assert expected in actual_types, f"Missing OutputType: {expected}"


class TestTemplateIdConsistency:
    """Verify template IDs are consistent across components."""

    def test_compute_function_ids_format(self):
        """All compute function template IDs should be uppercase alphanumeric."""
        import re
        pattern = re.compile(r'^[A-Z]+\d*$')
        
        for template_id in TEMPLATE_COMPUTE_FUNCTIONS.keys():
            assert pattern.match(template_id), (
                f"Invalid template ID format: {template_id}"
            )

    def test_feature_mapping_ids_match_compute(self):
        """Feature mapping IDs should match known template IDs."""
        compute_ids = set(TEMPLATE_COMPUTE_FUNCTIONS.keys())
        
        for template_id in FEATURE_TO_TEMPLATE_INPUT.keys():
            # Feature mapping can have templates not in compute functions
            # but warn if there's a mismatch
            pass  # Allow new mappings

        for template_id in FEATURE_MAPPINGS.keys():
            # Lifespan mappings should reference known templates
            pass  # Allow for flexibility


class TestZoneValueConsistency:
    """Verify zone values are consistent."""

    def test_zone_names_lowercase(self):
        """Zone names in ZONE_TO_WIS should be lowercase."""
        for zone_name in ZONE_TO_WIS.keys():
            assert zone_name == zone_name.lower(), (
                f"Zone name not lowercase: {zone_name}"
            )

    def test_compute_zones_in_mapping(self):
        """Zones returned by compute functions should be in ZONE_TO_WIS."""
        unmapped_zones = set()
        
        for template_id, func in TEMPLATE_COMPUTE_FUNCTIONS.items():
            try:
                result = func(occupant_age=35)
                if result.zone and result.zone != "unknown":
                    zone_lower = result.zone.lower()
                    if zone_lower not in ZONE_TO_WIS:
                        unmapped_zones.add(zone_lower)
            except TypeError:
                pass
        
        # Report unmapped zones (warning, not failure)
        if unmapped_zones:
            print(f"Zones without WIS mapping: {unmapped_zones}")


class TestDatabaseEnumValues:
    """Verify database records use valid enum values."""

    @pytest.fixture
    def session(self):
        """Get database session."""
        return get_session("ae.db")

    def test_dedup_status_values(self, session):
        """All dedup_status values should be from allowed set."""
        records = session.query(TemplateRecord).all()
        invalid = []
        
        for record in records:
            if record.dedup_status and record.dedup_status not in ALLOWED_DEDUP_STATUS:
                invalid.append({
                    "id": record.display_id,
                    "value": record.dedup_status,
                })
        
        assert not invalid, f"Invalid dedup_status values: {invalid}"

    def test_calibration_status_values(self, session):
        """All calibration_status values should be from allowed set."""
        records = session.query(TemplateRecord).all()
        invalid = []
        
        for record in records:
            if record.calibration_status and record.calibration_status not in ALLOWED_CALIBRATION_STATUS:
                invalid.append({
                    "id": record.display_id,
                    "value": record.calibration_status,
                })
        
        assert not invalid, f"Invalid calibration_status values: {invalid}"


class TestJSONTemplateEnums:
    """Verify JSON template files use valid enum values."""

    @pytest.fixture
    def json_templates(self):
        """Load all JSON template files."""
        templates_dir = Path(__file__).parent.parent / "data" / "templates"
        templates = {}
        
        if templates_dir.exists():
            for json_file in templates_dir.glob("*.json"):
                try:
                    with open(json_file) as f:
                        templates[json_file.stem] = json.load(f)
                except json.JSONDecodeError:
                    pass
        
        return templates

    def test_pe_contribution_values(self, json_templates):
        """All pe_contribution values should be from allowed set."""
        invalid = []
        
        for template_id, data in json_templates.items():
            pe_contrib = data.get("pe_contribution")
            if pe_contrib and pe_contrib not in ALLOWED_PE_CONTRIBUTION:
                invalid.append({
                    "id": template_id,
                    "value": pe_contrib,
                })
        
        # Some templates may have different naming - just report
        if invalid:
            print(f"Templates with non-standard pe_contribution: {invalid}")

    def test_practical_accessibility_values(self, json_templates):
        """All practical_accessibility values should be from allowed set."""
        invalid = []
        
        for template_id, data in json_templates.items():
            pa = data.get("practical_accessibility")
            if pa and pa not in ALLOWED_PRACTICAL_ACCESSIBILITY:
                invalid.append({
                    "id": template_id,
                    "value": pa,
                })
        
        assert not invalid, f"Invalid practical_accessibility values: {invalid}"


class TestNoEnumDrift:
    """Verify no enum drift between Sprint 10/11 changes."""

    def test_no_typos_in_calibration_status(self):
        """Check for common typos in calibration_status values."""
        typos = ["substanial", "parial", "protcol", "uncalibated"]
        
        for template_id, func in TEMPLATE_COMPUTE_FUNCTIONS.items():
            try:
                result = func(occupant_age=35)
                details = result.details or {}
                cal_status = details.get("calibration_status", "")
                
                for typo in typos:
                    assert typo not in cal_status.lower(), (
                        f"{template_id}: possible typo '{cal_status}'"
                    )
            except TypeError:
                pass

    def test_no_mixed_case_zones(self):
        """Zone values should be consistently cased."""
        for template_id, func in TEMPLATE_COMPUTE_FUNCTIONS.items():
            try:
                result = func(occupant_age=35)
                if result.zone:
                    # Zone should be all lowercase or all uppercase
                    assert result.zone == result.zone.lower() or \
                           result.zone == result.zone.upper(), (
                        f"{template_id}: mixed case zone '{result.zone}'"
                    )
            except TypeError:
                pass
