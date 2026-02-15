"""
Auto-generated ClaimType adapter for BN_graphical <-> AE canonical ClaimType.
Canonical contract section: enums.ClaimType
"""

from __future__ import annotations

from typing import Dict

BN_TO_CANONICAL: Dict[str, str] = {
  "boundary": "moderated",
  "effect": "causal",
  "mechanism": "mechanistic",
  "null_result": "null",
  "replication": "descriptive"
}
CANONICAL_TO_BN: Dict[str, str] = {
  "associational": "effect",
  "causal": "effect",
  "descriptive": "replication",
  "mechanistic": "mechanism",
  "moderated": "boundary",
  "null": "null_result",
  "presumption": "boundary",
  "rebuttal": "boundary"
}
UNMAPPED_BN_VALUES = []


def bn_claim_to_canonical(value: str) -> str:
    key = value.strip().lower()
    if key not in BN_TO_CANONICAL:
        raise KeyError(f"No canonical ClaimType mapping for BN value: {value}")
    return BN_TO_CANONICAL[key]


def canonical_to_bn_claim(value: str) -> str:
    key = value.strip().lower()
    if key not in CANONICAL_TO_BN:
        raise KeyError(f"No BN ClaimType mapping for canonical value: {value}")
    return CANONICAL_TO_BN[key]


def test_migration_lossless() -> None:
    # Lossless subset: BN internal ClaimType values
    for bn_value, canonical in BN_TO_CANONICAL.items():
        bn_roundtrip = canonical_to_bn_claim(canonical)
        assert bn_roundtrip == bn_value


if __name__ == "__main__":
    test_migration_lossless()
    print("ClaimType adapter self-test passed.")
