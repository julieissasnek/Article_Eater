"""Compare two D10 structured_claims JSON outputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _load(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _claim_key(claim: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        str(claim.get("paper_id") or ""),
        str(claim.get("iv") or claim.get("iv_raw") or ""),
        str(claim.get("dv") or claim.get("dv_raw") or ""),
        str(claim.get("direction") or "unknown"),
    )


def _summary(payload: dict[str, Any]) -> dict[str, Any]:
    claims = payload.get("claims", [])
    return {
        "claims_extracted": len(claims),
        "claims_with_effect_size": sum(1 for c in claims if c.get("effect_size") is not None),
        "claims_with_sample_n": sum(1 for c in claims if c.get("sample_n") is not None),
        "mapped_both": sum(1 for c in claims if c.get("iv_mapped") and c.get("dv_mapped")),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare two structured_claims outputs.")
    parser.add_argument("--a", required=True, help="Path to output A JSON")
    parser.add_argument("--b", required=True, help="Path to output B JSON")
    args = parser.parse_args()

    a = _load(args.a)
    b = _load(args.b)
    a_claims = a.get("claims", [])
    b_claims = b.get("claims", [])

    a_keys = {_claim_key(c) for c in a_claims}
    b_keys = {_claim_key(c) for c in b_claims}
    overlap = a_keys & b_keys

    report = {
        "a_path": str(Path(args.a)),
        "b_path": str(Path(args.b)),
        "a_summary": _summary(a),
        "b_summary": _summary(b),
        "overlap_claim_keys": len(overlap),
        "a_only_claim_keys": len(a_keys - b_keys),
        "b_only_claim_keys": len(b_keys - a_keys),
        "jaccard": round(len(overlap) / max(1, len(a_keys | b_keys)), 4),
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
