#!/usr/bin/env python3
"""
Article Eater ↔ Article Finder contract CLI (v1).

Implements:
  ./bin/article_eater eat --in <JOB_IN_DIR> --out <JOB_OUT_DIR> --profile <fast|standard|deep> --hitl <off|auto|required>

This file is the missing "glue" that the contract *schemas/examples* pack does not include.
It produces schema-shaped outputs so Article Finder can integrate reliably.

NOTE: This is a contract-compliance entrypoint. If you already have a deeper AE pipeline,
wire it at the TODO section in cmd_eat().
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

# Ensure repo root is importable when invoked via installer or scripts.
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# --- CHATGPT_PATCH_AE_AF_WIRING_V1 BEGIN ---
def _try_run_real_pipeline(in_dir: Path, out_dir: Path, profile: str, hitl: str):
    """Best-effort bridge into app.tasks.pipeline.run_from_contract_bundle."""
    try:
        from app.tasks.pipeline import run_from_contract_bundle  # type: ignore
        return run_from_contract_bundle(in_dir=in_dir, out_dir=out_dir, profile=profile, hitl=hitl)
    except Exception as e:
        return {"_error": "pipeline_bridge_failed: %s: %s" % (e.__class__.__name__, str(e))}
# --- CHATGPT_PATCH_AE_AF_WIRING_V1 END ---

from app.tasks.pipeline import run_from_contract_bundle


def _utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_json(p: Path) -> Dict[str, Any]:
    return json.loads(p.read_text(encoding="utf-8"))


def _write_json(p: Path, obj: Any) -> None:
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_jsonl(p: Path, rows: List[Dict[str, Any]]) -> None:
    with p.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def _audit_event(run_id: str, paper_id: str, stage: str, event: str, data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "schema": "ae.audit_event.v1",
        "ts": _utc_now(),
        "run_id": run_id,
        "paper_id": paper_id,
        "stage": stage,
        "event": event,
        "data": data,
    }


def _review_item(run_id: str, paper_id: str, item_id: str, severity: str, question: str, context: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "schema": "ae.review_item.v1",
        "paper_id": paper_id,
        "run_id": run_id,
        "item_id": item_id,
        "severity": severity,
        "question": question,
        "context": context,
    }


def _fallback_outputs(paper_id: str, pdf_sha256: str, run_id: str, profile: str, hitl: str, reason: str):
    result = {
        "schema": "ae.result.v1",
        "paper_id": paper_id,
        "pdf_sha256": pdf_sha256,
        "run_id": run_id,
        "status": "PARTIAL_SUCCESS",
        "profile": profile,
        "hitl": hitl,
        "summary": {
            "n_claims": 0,
            "n_rules": 0,
            "n_effect_sizes": 0,
            "n_population_records": 0,
            "n_environment_factors": 0,
        },
        "artifacts": {
            "claims_jsonl": "claims.jsonl",
            "rules_jsonl": "rules.jsonl",
            "provenance_json": "provenance.json",
            "audit_log_jsonl": "audit.log.jsonl",
        },
        "quality": {"confidence": 0.0, "blocking_issues": [reason], "warnings": []},
        "errors": [],
    }
    prov = {
        "schema": "ae.provenance.v1",
        "paper_id": paper_id,
        "run_id": run_id,
        "created_at": _utc_now(),
        "inputs": {"pdf_sha256": pdf_sha256},
        "environment": {"python": sys.version.split()[0], "platform": sys.platform},
        "models": [],
        "tools": [{"name": "ae.contract_cli", "version": "v1"}],
    }
    review = [
        _review_item(
            run_id,
            paper_id,
            "rev01",
            "blocking",
            "Wire contract CLI into the real AE extraction pipeline (claims/rules).",
            {"reason": reason},
        )
    ]
    return result, [], [], prov, review


def cmd_eat(args) -> int:
    in_dir = Path(args.in_dir).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    pdf_path = in_dir / "paper.pdf"
    paper_path = in_dir / "paper.json"

    if not pdf_path.exists() or not paper_path.exists():
        paper_id = "unknown"
        pdf_sha = "0" * 64
        run_id = f"ae.run.{_dt.datetime.now(_dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
        audits: List[Dict[str, Any]] = []
        audits.append(_audit_event(run_id, paper_id, "ingest", "fail", {"missing": [str(pdf_path), str(paper_path)]}))
        result, claims, rules, prov, review = _fallback_outputs(
            paper_id,
            pdf_sha,
            run_id,
            args.profile,
            args.hitl,
            "input_validation_failed",
        )
        result["status"] = "FAIL"
        result["errors"] = [{"code": "missing_inputs", "message": "paper.pdf and paper.json are required"}]
        _write_json(out_dir / "result.json", result)
        _write_jsonl(out_dir / "claims.jsonl", claims)
        _write_jsonl(out_dir / "rules.jsonl", rules)
        _write_json(out_dir / "provenance.json", prov)
        _write_jsonl(out_dir / "audit.log.jsonl", audits)
        _write_jsonl(out_dir / "review_items.jsonl", review)
        return 2

    try:
        # Sprint 2.0.3: Build web options dict from CLI flags
        web_options = {
            "enabled": getattr(args, "web_enabled", True),
            "seek_equilibrium": getattr(args, "web_equilibrium", True),
            "max_iterations": getattr(args, "web_max_iterations", 10),
            "convergence_threshold": getattr(args, "web_convergence_threshold", 0.001),
        }
        export_options = {
            "manifest": getattr(args, "export_manifest", True),
            "bn_state": getattr(args, "export_bn", True),
            "cluster_stats": getattr(args, "export_cluster_stats", True),
            "bn_edges": getattr(args, "export_bn_edges", True),
        }

        summary = run_from_contract_bundle(
            in_dir=in_dir,
            out_dir=out_dir,
            profile=args.profile,
            hitl=args.hitl,
            web_options=web_options,
            export_options=export_options,
        )
    except Exception as exc:
        paper = _load_json(paper_path)
        paper_id = paper.get("paper_id", "unknown")
        pdf_sha = _sha256_file(pdf_path)
        run_id = f"ae.run.{_dt.datetime.now(_dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
        audits: List[Dict[str, Any]] = []
        audits.append(_audit_event(run_id, paper_id, "extract", "fail", {"reason": str(exc)}))
        result, claims, rules, prov, review = _fallback_outputs(
            paper_id,
            pdf_sha,
            run_id,
            args.profile,
            args.hitl,
            "pipeline_exception",
        )
        result["status"] = "FAIL"
        result["errors"] = [{"code": "pipeline_exception", "message": str(exc)}]
        _write_json(out_dir / "result.json", result)
        _write_jsonl(out_dir / "claims.jsonl", claims)
        _write_jsonl(out_dir / "rules.jsonl", rules)
        _write_json(out_dir / "provenance.json", prov)
        _write_jsonl(out_dir / "audit.log.jsonl", audits)
        _write_jsonl(out_dir / "review_items.jsonl", review)
        return 2

    return 0 if summary["status"] != "FAIL" else 2


def main() -> int:
    ap = argparse.ArgumentParser(prog="article_eater")
    sub = ap.add_subparsers(dest="cmd", required=True)

    eat = sub.add_parser("eat", help="Process an AF input bundle into an AE output bundle")
    eat.add_argument("--in", dest="in_dir", required=True)
    eat.add_argument("--out", dest="out_dir", required=True)
    eat.add_argument("--profile", choices=["fast", "standard", "deep"], default="standard")
    eat.add_argument("--hitl", choices=["off", "auto", "required"], default="auto")

    # Sprint 2.0.3: Web of Belief output flags
    web_group = eat.add_argument_group("Web of Belief Options")
    web_group.add_argument(
        "--web", "--enable-web",
        dest="web_enabled", action="store_true", default=True,
        help="Enable Web of Belief integration (default: enabled)"
    )
    web_group.add_argument(
        "--no-web", "--disable-web",
        dest="web_enabled", action="store_false",
        help="Disable Web of Belief integration"
    )
    web_group.add_argument(
        "--web-equilibrium",
        dest="web_equilibrium", action="store_true", default=True,
        help="Seek equilibrium in web (default: enabled)"
    )
    web_group.add_argument(
        "--no-web-equilibrium",
        dest="web_equilibrium", action="store_false",
        help="Skip equilibrium seeking (faster)"
    )
    web_group.add_argument(
        "--web-max-iterations",
        dest="web_max_iterations", type=int, default=10,
        help="Max iterations for equilibrium (default: 10)"
    )
    web_group.add_argument(
        "--web-convergence-threshold",
        dest="web_convergence_threshold", type=float, default=0.001,
        help="Convergence threshold for equilibrium (default: 0.001)"
    )

    # Sprint 2.0.3: Export control flags
    export_group = eat.add_argument_group("Export Options")
    export_group.add_argument(
        "--export-manifest",
        dest="export_manifest", action="store_true", default=True,
        help="Generate manifest.json with checksums (default: enabled)"
    )
    export_group.add_argument(
        "--no-export-manifest",
        dest="export_manifest", action="store_false",
        help="Skip manifest generation"
    )
    export_group.add_argument(
        "--export-bn",
        dest="export_bn", action="store_true", default=True,
        help="Export incremental BN state (default: enabled)"
    )
    export_group.add_argument(
        "--no-export-bn",
        dest="export_bn", action="store_false",
        help="Skip BN state export"
    )
    export_group.add_argument(
        "--export-cluster-stats",
        dest="export_cluster_stats", action="store_true", default=True,
        help="Export coherence cluster statistics (default: enabled)"
    )
    export_group.add_argument(
        "--no-export-cluster-stats",
        dest="export_cluster_stats", action="store_false",
        help="Skip cluster stats export"
    )
    export_group.add_argument(
        "--export-bn-edges",
        dest="export_bn_edges", action="store_true", default=True,
        help="Export BN edges with uncertainty bounds (default: enabled)"
    )
    export_group.add_argument(
        "--no-export-bn-edges",
        dest="export_bn_edges", action="store_false",
        help="Skip BN edges export"
    )

    eat.set_defaults(func=cmd_eat)

    args = ap.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
