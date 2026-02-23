"""Codex-isolated batch extraction pipeline for Sprint D Task D.10.

This module intentionally uses separate defaults and output artifacts to avoid
contention with parallel implementations.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.extraction.claim_extractor import extract_claims_from_paper  # noqa: E402
from src.extraction.effect_size_converter import to_cohens_d  # noqa: E402
from src.extraction.table_classifier import EXTRACTABLE_TYPES  # noqa: E402
from src.extraction.table_semantics_codex import build_table_content_profile  # noqa: E402
from src.extraction.vocabulary import find_closest_dv, find_closest_iv, load_vocabulary  # noqa: E402


EXTRACTABLE_PAPER_TYPES = {"empirical", "review", "meta_analysis"}

_F_RE = re.compile(r"[Ff]\s*\(\s*([\d.]+)\s*,\s*([\d.]+)\s*\)\s*=\s*([-\d.]+)")
_T_RE = re.compile(r"[Tt]\s*\(\s*([\d.]+)\s*\)\s*=\s*([-\d.]+)")
_R_RE = re.compile(r"\br\s*=\s*([-\d.]+)")
_BETA_RE = re.compile(r"(?:β|beta)\s*=\s*([-\d.]+)", re.IGNORECASE)
_ETA_RE = re.compile(r"(?:η²|eta\s*squared|partial\s+eta)\s*=?\s*([\d.]+)", re.IGNORECASE)
_OR_RE = re.compile(r"(?:odds\s*ratio|OR)\s*=\s*([-\d.]+)", re.IGNORECASE)
_P_RE = re.compile(r"p\s*[<>=]\s*([\d.]+)", re.IGNORECASE)
_N_RE = re.compile(r"\b(?:N|n)\s*=\s*(\d+)\b")


def _normalize_stat_type(stat_type: str | None) -> str | None:
    if not stat_type:
        return None
    normalized = stat_type.strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "p_value": "p_value_only",
        "eta2": "eta_squared",
        "or": "odds_ratio",
        "d": "cohens_d",
    }
    return aliases.get(normalized, normalized)


def _load_triage(triage_path: str) -> dict[str, dict[str, Any]]:
    with open(triage_path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if isinstance(payload, dict) and isinstance(payload.get("papers"), list):
        out: dict[str, dict[str, Any]] = {}
        for paper in payload["papers"]:
            if not isinstance(paper, dict):
                continue
            paper_id = str(paper.get("paper_id") or "").strip()
            if not paper_id:
                continue
            out[paper_id] = {
                "type": paper.get("triage_type") or paper.get("type"),
                "confidence": paper.get("confidence"),
                "extractable": paper.get("extractable"),
                "title": paper.get("title"),
                "abstract": paper.get("abstract"),
            }
        return out

    if isinstance(payload, dict):
        out: dict[str, dict[str, Any]] = {}
        for paper_id, info in payload.items():
            if not isinstance(info, dict):
                continue
            out[str(paper_id)] = {
                "type": info.get("type") or info.get("triage_type"),
                "confidence": info.get("confidence"),
                "extractable": info.get("extractable"),
                "title": info.get("title"),
                "abstract": info.get("abstract"),
            }
        return out

    raise ValueError(f"Unsupported triage payload in {triage_path}")


def _load_table_classifications(table_class_path: str) -> dict[str, dict[str, Any]]:
    with open(table_class_path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if isinstance(payload, dict) and not isinstance(payload.get("tables"), list):
        return {str(tid): rec for tid, rec in payload.items() if isinstance(rec, dict)}

    tables: dict[str, dict[str, Any]] = {}
    items: list[Any]
    if isinstance(payload, dict) and isinstance(payload.get("tables"), list):
        items = payload["tables"]
    elif isinstance(payload, list):
        items = payload
    else:
        raise ValueError(f"Unsupported table classifications payload in {table_class_path}")

    for idx, rec in enumerate(items):
        if not isinstance(rec, dict):
            continue
        table_id = str(rec.get("table_id") or rec.get("source_table_id") or f"TBL-{idx:06d}")
        tables[table_id] = rec
    return tables


def _table_sort_key(row: dict[str, Any]) -> tuple[int, int]:
    row_index = row.get("row_index")
    if isinstance(row_index, int):
        return (0, row_index)
    return (1, int(row.get("_seq", 0)))


def _safe_int(value: str | int | None) -> int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    raw = str(value).strip()
    if not raw:
        return None
    try:
        return int(float(raw))
    except ValueError:
        return None


def _is_table_extractable(table_rec: dict[str, Any]) -> bool:
    extractable = table_rec.get("extractable")
    if isinstance(extractable, bool):
        return extractable
    table_type = str(table_rec.get("type") or "").strip()
    return table_type in EXTRACTABLE_TYPES


def _load_rows_from_csv(
    csv_path: str,
    allowed_papers: set[str],
    allowed_tables: set[str],
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, dict[str, str]]]:
    table_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    paper_context: dict[str, dict[str, str]] = {}

    with open(csv_path, "r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for seq, row in enumerate(reader):
            paper_id = (row.get("paper_id") or "").strip()
            if paper_id not in allowed_papers:
                continue

            table_id = (row.get("source_table_id") or "").strip()
            if table_id and table_id in allowed_tables:
                text = (
                    row.get("source_quote")
                    or row.get("statement")
                    or row.get("content")
                    or ""
                ).strip()
                table_rows[table_id].append(
                    {
                        "row_index": _safe_int(row.get("source_table_row")),
                        "text": text,
                        "source_quote": (row.get("source_quote") or "").strip(),
                        "_seq": seq,
                    }
                )

            if paper_id not in paper_context:
                paper_context[paper_id] = {
                    "title": (row.get("title") or "").strip(),
                    "abstract": (row.get("abstract") or "").strip(),
                    "article_type": (row.get("article_type_predicted_family") or "").strip(),
                }

    for rows in table_rows.values():
        rows.sort(key=_table_sort_key)
        for row in rows:
            row.pop("_seq", None)

    return table_rows, paper_context


def _postprocess_effect_size(claim: dict[str, Any]) -> dict[str, Any]:
    effect_size = claim.get("effect_size")
    effect_type = _normalize_stat_type(claim.get("effect_size_type"))
    sample_n = claim.get("sample_n")

    if effect_size is None and claim.get("p_value") and sample_n:
        try:
            converted = to_cohens_d(
                float(claim["p_value"]),
                "p_value_only",
                n=int(sample_n),
            )
            claim["effect_size"] = round(float(converted["d"]), 3)
            claim["effect_size_type"] = "cohens_d"
            claim["effect_conversion_method"] = converted["method"]
        except Exception:
            return claim
        return claim

    if effect_size is None or not effect_type:
        return claim

    if effect_type in {"cohens_d", "r_converted", "eta_squared_converted", "t_value_converted", "f_value_converted", "beta_converted"}:
        return claim

    convert_type = effect_type
    if convert_type == "p_value":
        convert_type = "p_value_only"

    try:
        kwargs: dict[str, Any] = {}
        if sample_n:
            kwargs["n"] = int(sample_n)
        converted = to_cohens_d(float(effect_size), convert_type, **kwargs)
        claim["effect_size"] = round(float(converted["d"]), 3)
        claim["effect_size_type"] = "cohens_d"
        claim["effect_conversion_method"] = converted["method"]
    except Exception:
        pass
    return claim


def _parse_stats(text: str) -> dict[str, float]:
    stats: dict[str, float] = {}

    def _to_float(token: str) -> float | None:
        cleaned = token.strip().strip(".,;:()[]{}")
        if not cleaned:
            return None
        try:
            return float(cleaned)
        except ValueError:
            return None

    match = _F_RE.search(text)
    if match:
        f_value = _to_float(match.group(3))
        df1 = _to_float(match.group(1))
        df2 = _to_float(match.group(2))
        if f_value is not None and df1 is not None and df2 is not None:
            stats["f_value"] = f_value
            stats["df1"] = df1
            stats["df2"] = df2

    match = _T_RE.search(text)
    if match:
        t_value = _to_float(match.group(2))
        df2 = _to_float(match.group(1))
        if t_value is not None and df2 is not None:
            stats["t_value"] = t_value
            stats["df2"] = df2

    match = _R_RE.search(text)
    if match:
        val = _to_float(match.group(1))
        if val is None:
            val = 0.0
        if -1 < val < 1:
            stats["r"] = val

    match = _BETA_RE.search(text)
    if match:
        val = _to_float(match.group(1))
        if val is None:
            val = 0.0
        if -1 < val < 1:
            stats["beta"] = val

    match = _ETA_RE.search(text)
    if match:
        val = _to_float(match.group(1))
        if val is None:
            val = -1.0
        if 0 <= val < 1:
            stats["eta_squared"] = val

    match = _OR_RE.search(text)
    if match:
        val = _to_float(match.group(1))
        if val is None:
            val = -1.0
        if val > 0:
            stats["odds_ratio"] = val

    match = _P_RE.search(text)
    if match:
        val = _to_float(match.group(1))
        if val is None:
            val = -1.0
        if 0 < val <= 1:
            stats["p_value_only"] = val

    match = _N_RE.search(text)
    if match:
        n = _to_float(match.group(1))
        if n is not None:
            stats["n"] = n

    return stats


def _extract_fallback_claims(
    paper_id: str,
    tables: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Conservative fallback extraction when D.6 returns no claims."""
    vocab = load_vocabulary()
    fallback_claims: list[dict[str, Any]] = []
    seq = 0

    for table in tables:
        table_id = table.get("table_id")
        table_text = " ".join((row.get("text") or "") for row in table.get("rows", []))
        table_iv, table_iv_conf = find_closest_iv(table_text, vocab)
        table_dv, table_dv_conf = find_closest_dv(table_text, vocab)

        for row in table.get("rows", []):
            row_text = (row.get("text") or "").strip()
            if len(row_text) < 16:
                continue

            stats = _parse_stats(row_text)
            has_core_stat = any(k in stats for k in ("f_value", "t_value", "r", "beta", "eta_squared", "odds_ratio"))
            has_sig_p = ("p_value_only" in stats) and (stats["p_value_only"] <= 0.05)
            if not (has_core_stat or has_sig_p):
                continue

            row_iv, row_iv_conf = find_closest_iv(row_text, vocab)
            row_dv, row_dv_conf = find_closest_dv(row_text, vocab)

            iv, iv_conf = row_iv, row_iv_conf
            dv, dv_conf = row_dv, row_dv_conf

            if not iv and table_iv and table_iv_conf >= 0.75:
                iv, iv_conf = table_iv, table_iv_conf
            if not dv and table_dv and table_dv_conf >= 0.75:
                dv, dv_conf = table_dv, table_dv_conf

            # Keep precision high: both sides must be reasonably mapped.
            if not iv or not dv or iv_conf < 0.6 or dv_conf < 0.6:
                continue

            effect_size = None
            effect_type = None
            for stat_key in ("r", "eta_squared", "beta", "t_value", "f_value", "odds_ratio", "p_value_only"):
                if stat_key not in stats:
                    continue
                try:
                    kwargs: dict[str, Any] = {}
                    if "df1" in stats:
                        kwargs["df1"] = int(stats["df1"])
                    if "df2" in stats:
                        kwargs["df2"] = int(stats["df2"])
                    if "n" in stats:
                        kwargs["n"] = int(stats["n"])
                    converted = to_cohens_d(stats[stat_key], stat_key, **kwargs)
                    effect_size = round(float(converted["d"]), 3)
                    effect_type = "cohens_d"
                    break
                except Exception:
                    continue

            direction = "unknown"
            if "r" in stats:
                direction = "increase" if stats["r"] > 0 else "decrease"
            elif "beta" in stats:
                direction = "increase" if stats["beta"] > 0 else "decrease"

            seq += 1
            fallback_claims.append(
                {
                    "claim_id": f"{paper_id}:{table_id}:CF{seq:03d}",
                    "paper_id": paper_id,
                    "iv": iv,
                    "iv_raw": row_text[:120],
                    "iv_mapped": True,
                    "iv_confidence": round(float(iv_conf), 2),
                    "dv": dv,
                    "dv_raw": row_text[:120],
                    "dv_mapped": True,
                    "dv_confidence": round(float(dv_conf), 2),
                    "direction": direction,
                    "effect_size": effect_size,
                    "effect_size_type": effect_type,
                    "sample_n": int(stats["n"]) if "n" in stats else None,
                    "p_value": stats.get("p_value_only"),
                    "context": None,
                    "source_table_id": table_id,
                    "source_page": table.get("page"),
                    "source_quote": row_text[:500],
                    "extraction_confidence": 0.62,
                    "vocabulary_mapped": True,
                    "extraction_method": "codex_precision_fallback",
                }
            )

    return fallback_claims


def run_batch_extraction_codex(
    csv_path: str = "data/production/realtime_pdf_confirmed_rows.csv",
    triage_path: str = "data/production/paper_triage.json",
    table_class_path: str = "data/production/table_classifications.json",
    output_path: str = "data/production/structured_claims_codex.json",
    semantic_profiles_path: str | None = "data/production/table_content_profiles_codex.for_d10.json",
    method: str = "rule_based",
    limit: int | None = None,
) -> dict[str, Any]:
    """Codex-isolated D10 orchestration."""
    triage = _load_triage(triage_path)
    eligible_papers = [
        paper_id
        for paper_id, rec in triage.items()
        if str(rec.get("type") or "").strip() in EXTRACTABLE_PAPER_TYPES
    ]
    if limit is not None:
        eligible_papers = eligible_papers[:limit]
    eligible_set = set(eligible_papers)

    table_classes = _load_table_classifications(table_class_path)
    extractable_tables = {
        table_id: rec
        for table_id, rec in table_classes.items()
        if str(rec.get("paper_id") or "").strip() in eligible_set and _is_table_extractable(rec)
    }
    extractable_table_ids = set(extractable_tables.keys())

    table_rows, csv_context = _load_rows_from_csv(
        csv_path=csv_path,
        allowed_papers=eligible_set,
        allowed_tables=extractable_table_ids,
    )

    tables_by_paper: dict[str, list[dict[str, Any]]] = defaultdict(list)
    semantic_profiles: dict[str, dict[str, Any]] = {}
    semantic_counts: Counter[str] = Counter()
    semantic_rejected = 0
    for table_id, rec in extractable_tables.items():
        paper_id = str(rec.get("paper_id") or "").strip()
        table_payload = {
            "table_id": table_id,
            "paper_id": paper_id,
            "page": rec.get("page"),
            "type": rec.get("type"),
            "sample_content": rec.get("sample_content") or "",
            "rows": table_rows.get(table_id, []),
        }
        semantic_profile = build_table_content_profile(table_payload)
        semantic_profiles[table_id] = semantic_profile
        semantic_counts.update([semantic_profile["semantic_type"]])
        if not semantic_profile["extractable"]:
            semantic_rejected += 1
            continue
        table_payload["semantic_profile"] = semantic_profile
        tables_by_paper[paper_id].append(table_payload)

    all_claims: list[dict[str, Any]] = []
    papers_processed = 0
    tables_processed = 0
    extraction_errors = 0

    for paper_id in eligible_papers:
        paper_tables = tables_by_paper.get(paper_id, [])
        if not paper_tables:
            continue
        paper_info = triage.get(paper_id, {})
        context = {
            "title": paper_info.get("title") or csv_context.get(paper_id, {}).get("title"),
            "abstract": paper_info.get("abstract") or csv_context.get(paper_id, {}).get("abstract"),
            "article_type": csv_context.get(paper_id, {}).get("article_type"),
        }
        claims: list[dict[str, Any]] = []
        try:
            claims = extract_claims_from_paper(
                paper_id=paper_id,
                tables=paper_tables,
                paper_context=context,
                vocabulary=None,
                method=method,
            )
        except Exception:
            extraction_errors += 1
        if not claims:
            claims = _extract_fallback_claims(paper_id=paper_id, tables=paper_tables)
        all_claims.extend(claims)
        papers_processed += 1
        tables_processed += len(paper_tables)

    deduped: list[dict[str, Any]] = []
    seen = set()
    for idx, claim in enumerate(all_claims, start=1):
        key = (
            claim.get("paper_id"),
            claim.get("iv") or claim.get("iv_raw"),
            claim.get("dv") or claim.get("dv_raw"),
            claim.get("direction"),
        )
        if key in seen:
            continue
        seen.add(key)
        if not claim.get("claim_id"):
            paper_id = claim.get("paper_id") or "unknown_paper"
            table_id = claim.get("source_table_id") or "UNKNOWN"
            claim["claim_id"] = f"{paper_id}:{table_id}:C{idx:03d}"
        deduped.append(_postprocess_effect_size(claim))

    claims_with_effect = sum(1 for c in deduped if c.get("effect_size") is not None)
    claims_with_sample_n = sum(1 for c in deduped if c.get("sample_n") is not None)
    new_variables_flagged = sum(
        1 for c in deduped if not c.get("iv_mapped", False) or not c.get("dv_mapped", False)
    )

    summary = {
        "extraction_date": datetime.now(timezone.utc).isoformat(),
        "method": method,
        "variant": "codex_isolated",
        "input_paths": {
            "csv_path": csv_path,
            "triage_path": triage_path,
            "table_class_path": table_class_path,
        },
        "papers_eligible": len(eligible_papers),
        "papers_processed": papers_processed,
        "tables_extractable": len(extractable_tables),
        "tables_rejected_by_semantics": semantic_rejected,
        "tables_processed": tables_processed,
        "papers_with_extraction_errors": extraction_errors,
        "claims_extracted": len(deduped),
        "claims_with_effect_size": claims_with_effect,
        "claims_with_sample_n": claims_with_sample_n,
        "new_variables_flagged": new_variables_flagged,
        "counts_by_direction": dict(Counter(c.get("direction", "unknown") for c in deduped)),
        "counts_by_semantic_type": dict(semantic_counts),
        "claims": deduped,
    }

    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, ensure_ascii=True)

    if semantic_profiles_path:
        profile_payload = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "table_count": len(semantic_profiles),
            "profiles": semantic_profiles,
        }
        profile_path = Path(semantic_profiles_path)
        profile_path.parent.mkdir(parents=True, exist_ok=True)
        with profile_path.open("w", encoding="utf-8") as handle:
            json.dump(profile_payload, handle, indent=2, ensure_ascii=True)

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Codex-isolated batch extraction pipeline.")
    parser.add_argument("--csv-path", default="data/production/realtime_pdf_confirmed_rows.csv")
    parser.add_argument("--triage-path", default="data/production/paper_triage.json")
    parser.add_argument("--table-class-path", default="data/production/table_classifications.json")
    parser.add_argument("--output-path", default="data/production/structured_claims_codex.json")
    parser.add_argument(
        "--semantic-profiles-path",
        default="data/production/table_content_profiles_codex.for_d10.json",
    )
    parser.add_argument("--method", choices=["rule_based", "llm"], default="rule_based")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    summary = run_batch_extraction_codex(
        csv_path=args.csv_path,
        triage_path=args.triage_path,
        table_class_path=args.table_class_path,
        output_path=args.output_path,
        semantic_profiles_path=args.semantic_profiles_path,
        method=args.method,
        limit=args.limit,
    )
    print(json.dumps({k: v for k, v in summary.items() if k != "claims"}, indent=2))


if __name__ == "__main__":
    main()
