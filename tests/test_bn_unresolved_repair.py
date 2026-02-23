from __future__ import annotations

from scripts.bn_unresolved_repair import make_node_id, make_typed_alias_node_id, match_alias_rule


def test_make_node_id_preserves_prefix_and_blocks_kind_mismatch() -> None:
    assert make_node_id("env", "env.ae.daylighting") == "env.ae.daylighting"
    assert make_node_id("out", "out.cog.performance") == "out.cog.performance"
    assert make_node_id("out", "affect.stress") == "out.affect.stress"
    assert make_node_id("env", "out.cog.performance") == ""


def test_make_typed_alias_node_id_preserves_family_and_adds_suffix() -> None:
    node_id = make_typed_alias_node_id("out", "out.cog.performance", "human_spatial_navigation")
    assert node_id.startswith("out.cog.performance.")
    assert node_id.endswith("human_spatial_navigation")


def test_make_typed_alias_node_id_supports_unknown_namespace() -> None:
    node_id = make_typed_alias_node_id("env", "env.unknown", "raw_unmapped_term")
    assert node_id == "env.unknown.raw_unmapped_term"


def test_make_typed_alias_node_id_force_hash_suffix_for_fallback() -> None:
    node_id = make_typed_alias_node_id(
        "env",
        "env.unknown",
        "raw_unmapped_term",
        force_hash_suffix=True,
    )
    assert node_id.startswith("env.unknown.raw_unmapped_term_")


def test_match_alias_rule_requires_existing_target_unless_overridden() -> None:
    rules = [
        {
            "id": "env_navigation_to_legibility",
            "kind": "env",
            "canonical_id": "env.cognitive.legibility",
            "anchors_any": ["navigation", "navigational"],
            "tokens_all": [],
            "tokens_none": [],
            "max_tokens": 6,
            "max_noise_tokens": 1,
            "confidence": 0.93,
        }
    ]

    miss = match_alias_rule(
        "human_spatial_navigation",
        "env",
        rules,
        existing_node_ids=set(),
        require_existing_targets=True,
        max_term_tokens=8,
        max_noise_tokens=1,
    )
    assert miss[0] == ""

    hit = match_alias_rule(
        "human_spatial_navigation",
        "env",
        rules,
        existing_node_ids=set(),
        require_existing_targets=False,
        max_term_tokens=8,
        max_noise_tokens=1,
    )
    assert hit[0] == "env.cognitive.legibility"
    assert hit[1] == "alias_rule"


def test_match_alias_rule_respects_negative_tokens() -> None:
    rules = [
        {
            "id": "env_view_window_to_outdoors",
            "kind": "env",
            "canonical_id": "env.ae.view_to_outdoors",
            "anchors_any": ["view", "views", "window", "windows"],
            "tokens_all": [],
            "tokens_none": ["review", "reviews"],
            "max_tokens": 6,
            "max_noise_tokens": 1,
            "confidence": 0.9,
        }
    ]
    existing = {"env.ae.view_to_outdoors"}

    blocked = match_alias_rule(
        "depression_preliminary_review",
        "env",
        rules,
        existing_node_ids=existing,
        require_existing_targets=True,
        max_term_tokens=8,
        max_noise_tokens=1,
    )
    assert blocked[0] == ""

    allowed = match_alias_rule(
        "col_view_using",
        "env",
        rules,
        existing_node_ids=existing,
        require_existing_targets=True,
        max_term_tokens=8,
        max_noise_tokens=1,
    )
    assert allowed[0] == "env.ae.view_to_outdoors"
    assert allowed[1] == "alias_rule"


def test_match_alias_rule_reports_conflict_for_multiple_targets() -> None:
    rules = [
        {
            "id": "env_navigation",
            "kind": "env",
            "canonical_id": "env.cognitive.legibility",
            "anchors_any": ["navigation"],
            "tokens_all": [],
            "tokens_none": [],
            "max_tokens": 8,
            "max_noise_tokens": 1,
            "confidence": 0.9,
        },
        {
            "id": "env_nature",
            "kind": "env",
            "canonical_id": "env.ae.nature_imagery",
            "anchors_any": ["nature"],
            "tokens_all": [],
            "tokens_none": [],
            "max_tokens": 8,
            "max_noise_tokens": 1,
            "confidence": 0.9,
        },
    ]
    existing = {"env.cognitive.legibility", "env.ae.nature_imagery"}
    conflict = match_alias_rule(
        "navigation_beyond_nature",
        "env",
        rules,
        existing_node_ids=existing,
        require_existing_targets=True,
        max_term_tokens=8,
        max_noise_tokens=1,
    )
    assert conflict[0] == ""
    assert conflict[1] == "alias_conflict"
