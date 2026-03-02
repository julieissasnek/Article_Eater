import pytest
from src.cmr.star_tracker import get_domain_star_progress, get_star_advancement_tracker


def test_star_tracker_loads_v22_scorecard() -> None:
    import os
    if not os.path.exists("docs/52_Registry_Addendum_V2_2.md"):
        pytest.skip("Scorecard file docs/52_Registry_Addendum_V2_2.md not yet created")
    tracker = get_star_advancement_tracker()
    assert tracker["domain_count"] == 10
    assert tracker["average_stars"] == 3.1
    assert tracker["global_blocker"] == "architectural-context validation is missing"


def test_a4_light_has_half_star_and_next_target() -> None:
    import os
    if not os.path.exists("docs/52_Registry_Addendum_V2_2.md"):
        pytest.skip("Scorecard file not yet created")
    progress = get_domain_star_progress("A4")
    assert progress is not None
    assert progress["domain_name"] == "Light & Luminance"
    assert progress["current_stars"] == 3.5
    assert progress["next_star_target"] == 4.0
    assert progress["stars_needed"] == 0.5
    assert "Validate L1 CV boundaries in field" in progress["what_needed_for_next_star"]


def test_a8_social_reports_cross_cultural_blocker() -> None:
    import os
    if not os.path.exists("docs/52_Registry_Addendum_V2_2.md"):
        pytest.skip("Scorecard file not yet created")
    progress = get_domain_star_progress("A8")
    assert progress is not None
    assert progress["current_stars"] == 3.5
    assert "cross-cultural generalization not validated" in progress["blockers"]
