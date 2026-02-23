#!/usr/bin/env python3
"""Run LLM-based table extraction pilot on a small PDF subset.

Purpose:
- Evaluate upper-bound extraction quality with expensive models.
- Compare method variants (strict authenticity gate vs no gate).
- Produce downgrade curve across model tiers.

Outputs:
- data/production/llm_pilot/<timestamp>_<profile>_<variant>.json
- data/production/llm_pilot/<timestamp>_summary.json
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import subprocess
import tempfile
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.sys.path.insert(0, str(PROJECT_ROOT))

from app.services.llm import LLMClient
from src.extraction.claim_extractor import extract_claims_from_table
from src.extraction.vocabulary import load_vocabulary
from src.services.table_extractor import AITableExtractor, ExtractedTable, TableType


DEFAULT_QUEUE_CSV = "data/production/realtime_pdf_completion_queue.csv"
DEFAULT_OUTPUT_DIR = "data/production/llm_pilot"
DEFAULT_PROFILES_PATH = "config/llm_table_pilot_profiles.json"
_PLACEHOLDER_RE = re.compile(r"\b(col(?:umn)?[_\s-]*\d+|row[_\s-]*\d+|cell[_\s-]*\d+|var[_\s-]*\d+|x\d+|y\d+)\b", re.IGNORECASE)
_LONG_TOKEN_RE = re.compile(r"\b[^\s]{40,}\b")


@dataclass(frozen=True)
class ModelProfile:
    name: str
    provider: str
    model: str


class _MsgText:
    def __init__(self, text: str):
        self.text = text


class _Resp:
    def __init__(self, text: str):
        self.content = [_MsgText(text)]


class _ChatAdapter:
    """Anthropic-like adapter around app.services.llm.LLMClient.

    AITableExtractor expects: api_client.messages.create(...).
    """

    def __init__(self, provider: str, codex_timeout_sec: int = 90):
        self.provider = provider.lower().strip()
        self.client = LLMClient()
        self.messages = self
        self.codex_timeout_sec = max(30, int(codex_timeout_sec))

    def _complete_with_codex_exec(
        self,
        model: str,
        system: str,
        user: str,
    ) -> str:
        """
        Use Codex CLI model directly (no external API key needed).

        This path uses the authenticated Codex session/model billing context.
        """
        prompt = (
            "You are a structured extraction assistant. "
            "Do not run shell commands. Return only the requested content.\n\n"
            f"SYSTEM:\n{system}\n\nUSER:\n{user}\n"
        )
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
            tmp_path = tmp.name
        cmd = [
            "codex",
            "exec",
            "-m",
            model,
            "-s",
            "read-only",
            "--skip-git-repo-check",
            "--output-last-message",
            tmp_path,
            "-",
        ]
        def _extract_json_fragment(raw: str) -> str:
            text = (raw or "").strip()
            if not text:
                return ""
            # Prefer full parse first.
            try:
                json.loads(text)
                return text
            except Exception:
                pass
            # Fall back to any parseable JSON object fragment.
            candidates = re.findall(r"\{[\s\S]*\}", text)
            for frag in reversed(candidates):
                frag = frag.strip()
                try:
                    json.loads(frag)
                    return frag
                except Exception:
                    continue
            return ""

        try:
            try:
                proc = subprocess.run(
                    cmd,
                    input=prompt.encode("utf-8"),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=str(PROJECT_ROOT),
                    check=False,
                    timeout=self.codex_timeout_sec,
                )
            except subprocess.TimeoutExpired as exc:
                raise RuntimeError(f"codex_exec_timeout: {self.codex_timeout_sec}s") from exc
            file_text = Path(tmp_path).read_text(encoding="utf-8", errors="ignore").strip()
            stdout_text = proc.stdout.decode("utf-8", errors="ignore").strip()
            stderr_text = proc.stderr.decode("utf-8", errors="ignore").strip()
            text = file_text or _extract_json_fragment(stdout_text) or stdout_text

            if proc.returncode != 0:
                # Codex CLI can emit non-zero with PATH/update warnings in constrained sandboxes.
                # If we still captured a valid JSON payload, salvage it.
                salvaged = _extract_json_fragment(text)
                if salvaged:
                    return salvaged
                stderr_preview = stderr_text[:1200]
                raise RuntimeError(f"codex_exec_failed: rc={proc.returncode}; stderr={stderr_preview}")
            return text
        finally:
            try:
                Path(tmp_path).unlink(missing_ok=True)
            except Exception:
                pass

    def create(
        self,
        model: str,
        max_tokens: int,
        system: str,
        messages: list[dict[str, Any]],
    ) -> _Resp:
        user_parts = []
        for msg in messages:
            if str(msg.get("role") or "").lower() != "user":
                continue
            user_parts.append(str(msg.get("content") or ""))
        user = "\n\n".join(user_parts)

        if self.provider == "openai":
            text = self.client.complete_openai(
                model=model,
                system=system,
                user=user,
                temperature=0.0,
                max_tokens=max_tokens,
            )
        elif self.provider in {"gemini", "google"}:
            text = self.client.complete_gemini(
                model=model,
                system=system,
                user=user,
                temperature=0.0,
                max_tokens=max_tokens,
            )
        elif self.provider == "ollama":
            text = self.client.complete_ollama(
                model=model,
                system=system,
                user=user,
                temperature=0.0,
                max_tokens=max_tokens,
            )
        elif self.provider in {"codex_exec", "codex"}:
            text = self._complete_with_codex_exec(
                model=model,
                system=system,
                user=user,
            )
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
        return _Resp(text)


def _load_profiles(path: str) -> list[ModelProfile]:
    p = Path(path)
    with p.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    out: list[ModelProfile] = []
    for item in payload.get("profiles", []):
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or "").strip()
        provider = str(item.get("provider") or "").strip()
        model = str(item.get("model") or "").strip()
        if not name or not provider or not model:
            continue
        out.append(ModelProfile(name=name, provider=provider, model=model))
    if not out:
        raise ValueError(f"No usable profiles in {path}")
    return out


def _looks_like_citation_or_prose(text: str) -> bool:
    t = text.lower()
    if re.search(r"\b(et al\.|frontiers in|journal|doi[:\s]|\(\d{4}\))", t):
        return True
    if len(text) > 220:
        return True
    return False


def _authenticity_gate(
    adapter: _ChatAdapter,
    model: str,
    table_excerpt: str,
) -> tuple[bool, float, str]:
    """Decide if candidate is a real data table vs prose/citation artifact."""
    system = (
        "You are validating whether extracted PDF content is a real data table. "
        "Reject references, prose paragraphs, bibliography fragments, and figure captions. "
        "Return strict JSON only."
    )
    user = f"""Decide if this is a real analyzable data table.

Content:
---
{table_excerpt[:4000]}
---

Return JSON:
{{
  "is_real_table": true/false,
  "confidence": 0.0-1.0,
  "reason": "short reason"
}}"""
    try:
        response = adapter.create(
            model=model,
            max_tokens=250,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        raw = response.content[0].text
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if not m:
            return False, 0.0, "non_json_gate_output"
        data = json.loads(m.group())
        return bool(data.get("is_real_table")), float(data.get("confidence", 0.0)), str(data.get("reason") or "")
    except Exception as exc:
        return False, 0.0, f"gate_error:{type(exc).__name__}"


def _select_pdfs(queue_csv_path: str, n: int) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    seen: set[str] = set()
    with open(queue_csv_path, "r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            paper_id = str(row.get("paper_id") or "").strip()
            pdf_raw = str(row.get("pdf_path") or "").strip()
            if not paper_id or not pdf_raw:
                continue
            pdf_path = Path(pdf_raw)
            if not pdf_path.is_absolute():
                pdf_path = (PROJECT_ROOT / pdf_path).resolve()
            if not pdf_path.exists() or paper_id in seen:
                continue
            seen.add(paper_id)
            out.append({"paper_id": paper_id, "pdf_path": str(pdf_path)})
            if len(out) >= n:
                break
    return out


def _table_type_to_d10_type(table_type: TableType) -> str:
    if table_type == TableType.RESULTS:
        return "RESULTS_DESCRIPTIVE"
    if table_type == TableType.STUDY_CHARACTERISTICS:
        return "LITERATURE_REVIEW"
    if table_type == TableType.QUALITY_ASSESSMENT:
        return "MODEL_FIT"
    if table_type == TableType.DEMOGRAPHICS:
        return "DEMOGRAPHICS"
    return "OTHER"


def _table_to_d10_payload(paper_id: str, table: ExtractedTable) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for ridx, row in enumerate(table.rows, start=1):
        parts = [f"col_{i + 1}: {str(cell).strip()}" for i, cell in enumerate(row) if str(cell or "").strip()]
        text = "; ".join(parts)
        if not text:
            continue
        rows.append({"row_index": ridx, "text": text, "source_quote": text})

    sample_content = table.to_markdown() or "\n".join(r.get("text") for r in rows[:5])
    return {
        "paper_id": paper_id,
        "table_id": table.table_id,
        "page": table.page_number,
        "type": _table_type_to_d10_type(table.table_type),
        "title": table.title,
        "sample_content": sample_content,
        "rows": rows,
    }


def _claim_is_suspect(claim: dict[str, Any]) -> bool:
    raw = " ".join(
        str(claim.get(k) or "")
        for k in ("iv_raw", "dv_raw", "source_quote")
    ).lower()
    if re.search(r"\b(et al\.|frontiers in|doi[:\s]|journal)\b", raw):
        return True
    if not claim.get("iv") or not claim.get("dv"):
        return True
    if str(claim.get("direction") or "unknown").lower() == "unknown":
        return True
    return False


def _claim_rejection_reasons(claim: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    iv = str(claim.get("iv") or "").strip()
    dv = str(claim.get("dv") or "").strip()
    iv_raw = str(claim.get("iv_raw") or "").strip()
    dv_raw = str(claim.get("dv_raw") or "").strip()
    quote = str(claim.get("source_quote") or "").strip()
    joined = " ".join([iv_raw, dv_raw, quote])

    if not iv or not dv:
        reasons.append("drop_unmapped_iv_or_dv")
    if iv and dv and iv == dv:
        reasons.append("drop_same_mapped_iv_dv")
    if not iv_raw or not dv_raw:
        reasons.append("drop_missing_raw_variable_text")
    if iv_raw and dv_raw and iv_raw.lower() == dv_raw.lower():
        reasons.append("drop_same_raw_iv_dv")
    if _PLACEHOLDER_RE.search(iv_raw) or _PLACEHOLDER_RE.search(dv_raw):
        reasons.append("drop_placeholder_column_label")
    if _LONG_TOKEN_RE.search(joined):
        reasons.append("drop_ocr_long_token_noise")
    if re.search(r"\b(et al\.|frontiers in|doi[:\s]|journal)\b", joined.lower()):
        reasons.append("drop_citation_like_noise")
    return reasons


def _run_profile_variant(
    profile: ModelProfile,
    variant: str,
    selected_pdfs: list[dict[str, str]],
    vocab: dict[str, Any],
    max_pages: int,
    codex_timeout_sec: int,
) -> dict[str, Any]:
    adapter = _ChatAdapter(profile.provider, codex_timeout_sec=codex_timeout_sec)
    extractor = AITableExtractor(api_client=adapter, model=profile.model)

    claims_out: list[dict[str, Any]] = []
    rejected_claims: list[dict[str, Any]] = []
    table_records: list[dict[str, Any]] = []
    counters = Counter()

    for item in selected_pdfs:
        paper_id = item["paper_id"]
        pdf_path = Path(item["pdf_path"])

        try:
            tables = extractor.extract_tables(pdf_path=pdf_path, pages=list(range(1, max_pages + 1)))
        except Exception as exc:
            counters["pdf_errors"] += 1
            table_records.append(
                {
                    "paper_id": paper_id,
                    "pdf_path": str(pdf_path),
                    "error": f"extract_tables_error:{type(exc).__name__}",
                    "tables": [],
                }
            )
            continue

        counters["tables_detected"] += len(tables)
        kept_tables: list[ExtractedTable] = []

        for table in tables:
            excerpt = (table.to_markdown() or "").strip()
            if not excerpt:
                excerpt = "\n".join(" | ".join(str(c) for c in r) for r in table.rows[:6])

            if variant == "strict_gate":
                is_table, gate_conf, gate_reason = _authenticity_gate(adapter, profile.model, excerpt)
                if not is_table or gate_conf < 0.6:
                    counters["gated_out"] += 1
                    table_records.append(
                        {
                            "paper_id": paper_id,
                            "table_id": table.table_id,
                            "page": table.page_number,
                            "kept": False,
                            "gate_confidence": gate_conf,
                            "gate_reason": gate_reason,
                            "type": table.table_type.value,
                            "confidence": table.confidence,
                        }
                    )
                    continue

            if variant == "heuristic_gate" and _looks_like_citation_or_prose(excerpt):
                counters["gated_out"] += 1
                table_records.append(
                    {
                        "paper_id": paper_id,
                        "table_id": table.table_id,
                        "page": table.page_number,
                        "kept": False,
                        "gate_confidence": 0.0,
                        "gate_reason": "heuristic_prose_or_citation",
                        "type": table.table_type.value,
                        "confidence": table.confidence,
                    }
                )
                continue

            kept_tables.append(table)
            table_records.append(
                {
                    "paper_id": paper_id,
                    "table_id": table.table_id,
                    "page": table.page_number,
                    "kept": True,
                    "type": table.table_type.value,
                    "confidence": table.confidence,
                }
            )

        counters["tables_kept"] += len(kept_tables)

        for table in kept_tables:
            payload = _table_to_d10_payload(paper_id=paper_id, table=table)
            if not payload["rows"]:
                counters["empty_tables"] += 1
                continue
            claims = extract_claims_from_table(payload, vocabulary=vocab, method="enhanced")
            for claim in claims:
                claim["pilot_profile"] = profile.name
                claim["pilot_variant"] = variant
                claim["pilot_model"] = profile.model
                reasons = _claim_rejection_reasons(claim)
                if reasons:
                    counters["claims_rejected"] += 1
                    for reason in reasons:
                        counters[reason] += 1
                    rejected_claims.append(
                        {
                            "claim_id": claim.get("claim_id"),
                            "paper_id": claim.get("paper_id"),
                            "source_table_id": claim.get("source_table_id"),
                            "iv_raw": claim.get("iv_raw"),
                            "dv_raw": claim.get("dv_raw"),
                            "source_quote": claim.get("source_quote"),
                            "reasons": reasons,
                        }
                    )
                    continue
                claims_out.append(claim)

    n_claims = len(claims_out)
    rejected_n = len(rejected_claims)
    mapped_both = sum(1 for c in claims_out if c.get("iv_mapped") and c.get("dv_mapped"))
    effect = sum(1 for c in claims_out if c.get("effect_size") is not None)
    unknown_dir = sum(1 for c in claims_out if str(c.get("direction") or "unknown").lower() == "unknown")
    suspect = sum(1 for c in claims_out if _claim_is_suspect(c))

    return {
        "profile": profile.name,
        "provider": profile.provider,
        "model": profile.model,
        "variant": variant,
        "papers": len(selected_pdfs),
        "counters": dict(counters),
        "metrics": {
            "claims": n_claims,
            "claims_rejected": rejected_n,
            "claims_pre_filter": n_claims + rejected_n,
            "mapped_both": mapped_both,
            "mapped_both_pct": round(100 * mapped_both / max(1, n_claims), 1),
            "effect_size": effect,
            "unknown_direction": unknown_dir,
            "unknown_direction_pct": round(100 * unknown_dir / max(1, n_claims), 1),
            "suspect_claims": suspect,
            "suspect_claims_pct": round(100 * suspect / max(1, n_claims), 1),
        },
        "claims": claims_out,
        "rejected_claims": rejected_claims[:200],
        "table_records": table_records,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run LLM table-extraction pilot benchmark.")
    parser.add_argument("--queue-csv", default=DEFAULT_QUEUE_CSV)
    parser.add_argument("--profiles", default=DEFAULT_PROFILES_PATH)
    parser.add_argument("--n-pdfs", type=int, default=5)
    parser.add_argument("--max-pages", type=int, default=10, help="Max pages to scan per PDF.")
    parser.add_argument(
        "--variants",
        default="strict_gate,no_gate",
        help="Comma-separated: strict_gate,heuristic_gate,no_gate",
    )
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--vocab-path", default="data/vocabulary/variable_vocabulary.json")
    parser.add_argument("--codex-timeout-sec", type=int, default=90)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    profiles = _load_profiles(args.profiles)
    selected_pdfs = _select_pdfs(args.queue_csv, args.n_pdfs)
    if not selected_pdfs:
        raise SystemExit("No PDFs selected. Check queue CSV and file paths.")

    vocab = load_vocabulary(args.vocab_path)

    run_ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    variants = [v.strip() for v in args.variants.split(",") if v.strip()]

    all_runs: list[dict[str, Any]] = []

    for profile in profiles:
        for variant in variants:
            result = _run_profile_variant(
                profile=profile,
                variant=variant,
                selected_pdfs=selected_pdfs,
                vocab=vocab,
                max_pages=args.max_pages,
                codex_timeout_sec=args.codex_timeout_sec,
            )
            out_path = output_dir / f"{run_ts}_{profile.name}_{variant}.json"
            out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
            summary = {
                "profile": profile.name,
                "provider": profile.provider,
                "model": profile.model,
                "variant": variant,
                "output": str(out_path),
                "metrics": result["metrics"],
                "counters": result["counters"],
            }
            all_runs.append(summary)
            print(json.dumps(summary, indent=2))

    summary_path = output_dir / f"{run_ts}_summary.json"
    summary_payload = {
        "run_ts": run_ts,
        "selected_pdfs": selected_pdfs,
        "profiles_path": args.profiles,
        "variants": variants,
        "runs": all_runs,
    }
    summary_path.write_text(json.dumps(summary_payload, indent=2), encoding="utf-8")
    print(f"Summary written: {summary_path}")


if __name__ == "__main__":
    main()
