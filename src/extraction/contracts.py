"""Versioned extraction artifact contracts and fail-fast validators."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


SCHEMA_VERSIONS = {
    "paper_triage": "1.0.0",
    "table_classifications": "1.0.0",
    "abstract_claims": "1.0.0",
    "caption_dv_lookup": "1.0.0",
    "structured_claims": "1.0.0",
}


@dataclass(frozen=True)
class ContractValidationResult:
    artifact: str
    version: str
    valid: bool
    errors: tuple[str, ...]
    warnings: tuple[str, ...]


def _is_nonempty_str(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _as_claim_list(payload: Any) -> list[dict[str, Any]] | None:
    if isinstance(payload, dict) and isinstance(payload.get("claims"), list):
        items = payload.get("claims", [])
        return [x for x in items if isinstance(x, dict)]
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    return None


def validate_paper_triage_payload(payload: Any) -> ContractValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(payload, dict):
        errors.append("payload must be a dict")
        return ContractValidationResult("paper_triage", SCHEMA_VERSIONS["paper_triage"], False, tuple(errors), tuple(warnings))

    if isinstance(payload.get("papers"), list):
        for idx, paper in enumerate(payload.get("papers", [])):
            if not isinstance(paper, dict):
                errors.append(f"papers[{idx}] must be a dict")
                continue
            if not _is_nonempty_str(paper.get("paper_id")):
                errors.append(f"papers[{idx}].paper_id must be non-empty string")
    else:
        # mapping style: {paper_id: {...}}
        for paper_id, paper in payload.items():
            if paper_id == "papers":
                continue
            if not isinstance(paper, dict):
                errors.append(f"{paper_id} must map to a dict")
                continue
            if not _is_nonempty_str(paper_id):
                errors.append("mapping key paper_id must be non-empty string")

    return ContractValidationResult("paper_triage", SCHEMA_VERSIONS["paper_triage"], not errors, tuple(errors), tuple(warnings))


def validate_table_classifications_payload(payload: Any) -> ContractValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(payload, dict):
        errors.append("payload must be a dict keyed by table_id")
        return ContractValidationResult(
            "table_classifications",
            SCHEMA_VERSIONS["table_classifications"],
            False,
            tuple(errors),
            tuple(warnings),
        )

    for table_id, rec in payload.items():
        if not _is_nonempty_str(table_id):
            errors.append("table_id key must be non-empty string")
            continue
        if not isinstance(rec, dict):
            errors.append(f"{table_id} must map to a dict record")
            continue
        if not _is_nonempty_str(rec.get("paper_id")):
            errors.append(f"{table_id}.paper_id must be non-empty string")
        if not _is_nonempty_str(rec.get("type")):
            errors.append(f"{table_id}.type must be non-empty string")
        if "extractable" in rec and not isinstance(rec.get("extractable"), bool):
            errors.append(f"{table_id}.extractable must be bool")
        if "confidence" in rec:
            try:
                float(rec.get("confidence"))
            except (TypeError, ValueError):
                errors.append(f"{table_id}.confidence must be numeric")

    return ContractValidationResult(
        "table_classifications",
        SCHEMA_VERSIONS["table_classifications"],
        not errors,
        tuple(errors),
        tuple(warnings),
    )


def validate_abstract_claims_payload(payload: Any) -> ContractValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    claims = _as_claim_list(payload)
    if claims is None:
        errors.append("payload must be {'claims': [...]} or claim list")
        return ContractValidationResult("abstract_claims", SCHEMA_VERSIONS["abstract_claims"], False, tuple(errors), tuple(warnings))

    for idx, claim in enumerate(claims):
        if not _is_nonempty_str(claim.get("paper_id")):
            errors.append(f"claims[{idx}].paper_id must be non-empty string")
        source = str(claim.get("source") or "").strip()
        if source and source not in {"abstract", "caption"}:
            warnings.append(f"claims[{idx}].source has unexpected value: {source}")

    return ContractValidationResult("abstract_claims", SCHEMA_VERSIONS["abstract_claims"], not errors, tuple(errors), tuple(warnings))


def validate_caption_dv_lookup_payload(payload: Any) -> ContractValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(payload, dict):
        errors.append("payload must be dict keyed by source_table_id")
        return ContractValidationResult("caption_dv_lookup", SCHEMA_VERSIONS["caption_dv_lookup"], False, tuple(errors), tuple(warnings))

    for table_id, rec in payload.items():
        if not _is_nonempty_str(table_id):
            errors.append("table_id key must be non-empty string")
            continue
        if isinstance(rec, str):
            if not rec.strip():
                errors.append(f"{table_id} string value must be non-empty")
            continue
        if not isinstance(rec, dict):
            errors.append(f"{table_id} must map to string or dict")
            continue
        dv = rec.get("dv")
        dv_raw = rec.get("dv_raw")
        if not (_is_nonempty_str(dv) or _is_nonempty_str(dv_raw)):
            errors.append(f"{table_id} must contain dv or dv_raw")
        if "confidence" in rec:
            try:
                float(rec.get("confidence"))
            except (TypeError, ValueError):
                errors.append(f"{table_id}.confidence must be numeric")

    return ContractValidationResult("caption_dv_lookup", SCHEMA_VERSIONS["caption_dv_lookup"], not errors, tuple(errors), tuple(warnings))


def validate_structured_claims_payload(payload: Any) -> ContractValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(payload, dict):
        errors.append("payload must be dict with claims list and summary")
        return ContractValidationResult("structured_claims", SCHEMA_VERSIONS["structured_claims"], False, tuple(errors), tuple(warnings))
    if not isinstance(payload.get("claims"), list):
        errors.append("claims must be a list")
        return ContractValidationResult("structured_claims", SCHEMA_VERSIONS["structured_claims"], False, tuple(errors), tuple(warnings))
    if not isinstance(payload.get("summary"), dict):
        errors.append("summary must be a dict")

    claims = [c for c in payload.get("claims", []) if isinstance(c, dict)]
    for idx, claim in enumerate(claims):
        if not _is_nonempty_str(claim.get("paper_id")):
            errors.append(f"claims[{idx}].paper_id must be non-empty string")
        if not _is_nonempty_str(claim.get("direction")):
            warnings.append(f"claims[{idx}].direction missing/empty")
        if not (_is_nonempty_str(claim.get("iv")) or _is_nonempty_str(claim.get("iv_raw"))):
            warnings.append(f"claims[{idx}] has no iv/iv_raw")
        if not (_is_nonempty_str(claim.get("dv")) or _is_nonempty_str(claim.get("dv_raw"))):
            warnings.append(f"claims[{idx}] has no dv/dv_raw")

    summary = payload.get("summary", {})
    for field in ("total_claims", "from_tables", "from_abstracts", "from_captions"):
        if field in summary:
            try:
                int(summary.get(field))
            except (TypeError, ValueError):
                errors.append(f"summary.{field} must be integer-like")

    return ContractValidationResult("structured_claims", SCHEMA_VERSIONS["structured_claims"], not errors, tuple(errors), tuple(warnings))


def validate_payload(artifact: str, payload: Any) -> ContractValidationResult:
    if artifact == "paper_triage":
        return validate_paper_triage_payload(payload)
    if artifact == "table_classifications":
        return validate_table_classifications_payload(payload)
    if artifact == "abstract_claims":
        return validate_abstract_claims_payload(payload)
    if artifact == "caption_dv_lookup":
        return validate_caption_dv_lookup_payload(payload)
    if artifact == "structured_claims":
        return validate_structured_claims_payload(payload)
    raise ValueError(f"Unknown artifact contract: {artifact}")


def assert_valid_payload(artifact: str, payload: Any, strict: bool = True) -> ContractValidationResult:
    result = validate_payload(artifact, payload)
    if strict and not result.valid:
        msg = "; ".join(result.errors[:8]) if result.errors else "unknown contract error"
        raise ValueError(f"{artifact} contract validation failed (v{result.version}): {msg}")
    return result
