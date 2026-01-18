#!/usr/bin/env bash
set -euo pipefail

# tools/apply_chatgpt_patch.sh
# One-shot apply script to wire AE contract CLI -> pipeline bridge -> extractor (best-effort).
#
# Run from repo root:
#   bash tools/apply_chatgpt_patch.sh

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

UTC="$(date -u +%Y%m%dT%H%M%SZ)"
ARCHIVE_DIR="$ROOT_DIR/_archive/chatgpt_patch_${UTC}"
mkdir -p "$ARCHIVE_DIR"

PY="${PYTHON:-python3}"
if [ -x "$ROOT_DIR/.venv/bin/python" ]; then
  PY="$ROOT_DIR/.venv/bin/python"
fi

echo "=== Applying AE<->AF wiring patch (Option 2) ==="
echo "Repo: $ROOT_DIR"
echo "Python: $PY"
echo "Archive: $ARCHIVE_DIR"
echo ""

# Back up touched files
for f in "app/tasks/pipeline.py" "app/cli/article_eater_contract_cli.py"; do
  if [ -f "$f" ]; then
    cp "$f" "$ARCHIVE_DIR/$(basename "$f")"
    echo "[backup] $f -> $ARCHIVE_DIR/$(basename "$f")"
  else
    echo "[warn] missing: $f"
  fi
done
echo ""

"$PY" - <<'PY'
import re
from pathlib import Path

ROOT = Path(".").resolve()
PATCH_TAG = "CHATGPT_PATCH_AE_AF_WIRING_V1"
BEGIN = "# --- %s BEGIN ---" % PATCH_TAG
END = "# --- %s END ---" % PATCH_TAG

def ensure_parent(p):
    p.parent.mkdir(parents=True, exist_ok=True)

def patch_pipeline():
    p = ROOT / "app/tasks/pipeline.py"
    ensure_parent(p)
    text = p.read_text(encoding="utf-8") if p.exists() else ""
    if BEGIN in text and END in text:
        print("PATCH: pipeline already patched")
        return
    block = '''
# --- CHATGPT_PATCH_AE_AF_WIRING_V1 BEGIN ---
"""
Contract wiring entrypoint for Article Finder to Article Eater.

This function is called by app/cli/article_eater_contract_cli.py when present.
It is intentionally defensive: it attempts to call the existing extraction pipeline
if available, but will degrade gracefully if the extractor signature differs.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import importlib
import hashlib

def _read_text_if_exists(p: Path) -> Optional[str]:
    try:
        if p.exists():
            return p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None
    return None

def _sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def _safe_import(module_name: str):
    try:
        return importlib.import_module(module_name)
    except Exception:
        return None

def _try_call_extractor(fulltext: str, meta: Dict[str, Any], profile: str) -> Dict[str, Any]:
    mod = _safe_import("app.services.extract_7panel")
    if mod is None:
        return {"_error": "extract_7panel_import_failed"}
    candidates = ["extract_7panel","extract","run_extract","run","main_extract"]
    last = None
    for name in candidates:
        fn = getattr(mod, name, None)
        if callable(fn):
            try:
                # Try a few common call patterns
                try:
                    return fn(fulltext=fulltext, meta=meta, profile=profile)  # type: ignore
                except TypeError:
                    pass
                try:
                    return fn(fulltext, meta)  # type: ignore
                except TypeError:
                    pass
                try:
                    return fn(fulltext)  # type: ignore
                except TypeError:
                    pass
                try:
                    return fn({"fulltext": fulltext, "meta": meta, "profile": profile})  # type: ignore
                except TypeError:
                    pass
            except Exception as e:
                last = e
                continue
    if last is not None:
        return {"_error": "extractor_call_failed: %s: %s" % (last.__class__.__name__, str(last))}
    return {"_error": "no_extractor_entrypoint_found"}

def run_from_contract_bundle(*, in_dir: Path, out_dir: Path, profile: str, hitl: str) -> Dict[str, Any]:
    """Reads AF input bundle and returns raw claims/rules lists (if extractor provides them)."""
    paper = json.loads((in_dir/"paper.json").read_text(encoding="utf-8"))
    paper_id = paper.get("paper_id","unknown")
    pdf_path = in_dir/"paper.pdf"
    pdf_sha256 = _sha256_file(pdf_path) if pdf_path.exists() else "0"*64

    fulltext = _read_text_if_exists(in_dir/"fulltext.txt")
    if fulltext is None:
        ing = _safe_import("app.pdf_ingest")
        fulltext = ""
        if ing is not None:
            for fn_name in ["pdf_to_text","extract_text","ingest_pdf","read_pdf_text"]:
                fn = getattr(ing, fn_name, None)
                if callable(fn):
                    try:
                        out = fn(str(pdf_path))  # type: ignore
                        if isinstance(out, str) and out.strip():
                            fulltext = out
                            break
                    except Exception:
                        continue

    meta = {
        "paper_id": paper_id,
        "title": paper.get("title"),
        "doi": paper.get("doi"),
        "year": paper.get("year"),
        "authors": paper.get("authors"),
        "pdf_sha256": pdf_sha256,
    }

    extracted = _try_call_extractor(fulltext, meta, profile)
    warnings: List[str] = []
    claims_raw: List[Dict[str, Any]] = []
    rules_raw: List[Dict[str, Any]] = []

    if isinstance(extracted, dict):
        if extracted.get("_error"):
            warnings.append(str(extracted["_error"]))
        if isinstance(extracted.get("claims"), list):
            claims_raw = [c for c in extracted["claims"] if isinstance(c, dict)]
        if isinstance(extracted.get("rules"), list):
            rules_raw = [r for r in extracted["rules"] if isinstance(r, dict)]
    elif isinstance(extracted, list):
        claims_raw = [c for c in extracted if isinstance(c, dict)]
    else:
        warnings.append("extractor_return_shape_unrecognized")

    return {
        "paper_id": paper_id,
        "pdf_sha256": pdf_sha256,
        "claims_raw": claims_raw,
        "rules_raw": rules_raw,
        "warnings": warnings,
        "has_fulltext": bool(fulltext and fulltext.strip()),
    }
# --- CHATGPT_PATCH_AE_AF_WIRING_V1 END ---
'''
    p.write_text(text.rstrip()+"\n\n"+block.lstrip(), encoding="utf-8")
    print("PATCH: pipeline patched")

def patch_contract_cli():
    p = ROOT / "app/cli/article_eater_contract_cli.py"
    if not p.exists():
        print("PATCH: contract cli missing; skipping")
        return
    text = p.read_text(encoding="utf-8")
    if PATCH_TAG in text:
        print("PATCH: contract cli already patched")
        return

    insert_block = '''
# --- CHATGPT_PATCH_AE_AF_WIRING_V1 BEGIN ---
def _try_run_real_pipeline(in_dir: Path, out_dir: Path, profile: str, hitl: str):
    """Best-effort bridge into app.tasks.pipeline.run_from_contract_bundle."""
    try:
        from app.tasks.pipeline import run_from_contract_bundle  # type: ignore
        return run_from_contract_bundle(in_dir=in_dir, out_dir=out_dir, profile=profile, hitl=hitl)
    except Exception as e:
        return {"_error": "pipeline_bridge_failed: %s: %s" % (e.__class__.__name__, str(e))}
# --- CHATGPT_PATCH_AE_AF_WIRING_V1 END ---
'''

    # Insert after typing import if present; else prepend
    m = re.search(r"(from typing[^\n]*\n)", text)
    idx = m.end() if m else 0
    text = text[:idx] + "\n" + insert_block + "\n" + text[idx:]

    # Try to inject a bridge call after a fallback audit marker, if present.
    if "real_pipeline_not_wired" in text and "_try_run_real_pipeline" in text:
        text = re.sub(
            r"(audits\.append\([^\)]*fallback[^\)]*\)\)\s*)",
            r"\1bridge = _try_run_real_pipeline(in_dir, out_dir, args.profile, args.hitl)\n"
            r"    _bridge = bridge if isinstance(bridge, dict) else {}\n"
            r"    _claims_raw = _bridge.get('claims_raw') or []\n"
            r"    _rules_raw = _bridge.get('rules_raw') or []\n",
            text,
            count=1
        )

    p.write_text(text, encoding="utf-8")
    print("PATCH: contract cli patched")

patch_pipeline()
patch_contract_cli()
PY

echo ""
echo "[ok] Patch applied. Running install + doctor if present."
echo ""

if [ -f "install_ae_envkit.sh" ]; then
  bash install_ae_envkit.sh || true
else
  echo "[warn] install_ae_envkit.sh not found; skipping."
fi

if [ -f "doctor.sh" ]; then
  bash doctor.sh || true
else
  echo "[warn] doctor.sh not found; skipping."
fi

echo ""
echo "Next smoke test:"
echo "  ./bin/article_eater eat --in contracts/ae_af/examples/input_bundle_minimal --out /tmp/ae_out_example --profile standard --hitl auto"
