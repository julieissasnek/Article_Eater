#!/usr/bin/env python3
"""
Extraction Coordinator v2 — PDF-First Architecture
===================================================
The PDF is the ground truth. Each PDF gets a unique ID (PDF-0001, PDF-0002, ...).
Metadata (DOI, title, authors) is discovered DURING extraction, not assumed before.

Commands:
    python3 scripts/extraction_coordinator.py status
    python3 scripts/extraction_coordinator.py claim <worker_id> [--n 5]
    python3 scripts/extraction_coordinator.py complete <worker_id> <pdf_id>
    python3 scripts/extraction_coordinator.py release <worker_id>
    python3 scripts/extraction_coordinator.py next [--n 10]

Worker IDs: "cowork", "ag", "cowork-scheduled", etc.
"""

import json
import os
import sys
import argparse
import glob
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INVENTORY_FILE = PROJECT_ROOT / "data" / "pdf_inventory.json"
QUEUE_FILE = PROJECT_ROOT / "data" / "gold_standard" / "EXTRACTION_QUEUE.json"
GS_DIR = PROJECT_ROOT / "data" / "gold_standard"

# Min/max PDF size for extraction (skip tiny/huge files)
MIN_PDF_BYTES = 50_000    # 50 KB
MAX_PDF_BYTES = 50_000_000  # 50 MB


def load_inventory():
    with open(INVENTORY_FILE) as f:
        return json.load(f)["inventory"]


def load_queue():
    if QUEUE_FILE.exists():
        with open(QUEUE_FILE) as f:
            return json.load(f)
    return {"metadata": {}, "stats": {}, "active_claims": [], "completed": [], "mismatches": []}


def save_queue(queue):
    queue["stats"]["last_updated"] = datetime.now().isoformat()
    with open(QUEUE_FILE, "w") as f:
        json.dump(queue, f, indent=2)


def get_extracted_pdf_ids():
    """Find PDF IDs that already have gold standard extractions."""
    extracted = set()
    skip = {"batch_progress.json", "comparison_report.json", "gold_standard_papers.json",
            "unmatched_dois.json", "doi_mismatches.json", "current_batch.json",
            "EXTRACTION_QUEUE.json", "AG_EXTRACTION_TASK.md"}
    for f in GS_DIR.iterdir():
        if f.suffix == ".json" and f.name not in skip:
            try:
                data = json.loads(f.read_text())
                if isinstance(data, dict) and "pdf_id" in data:
                    extracted.add(data["pdf_id"])
            except (json.JSONDecodeError, KeyError):
                pass
    return extracted


def get_extracted_paths():
    """Find PDF paths that already have extractions (for backward compat with old extractions)."""
    paths = set()
    skip = {"batch_progress.json", "comparison_report.json", "gold_standard_papers.json",
            "unmatched_dois.json", "doi_mismatches.json", "current_batch.json",
            "EXTRACTION_QUEUE.json", "AG_EXTRACTION_TASK.md"}
    for f in GS_DIR.iterdir():
        if f.suffix == ".json" and f.name not in skip:
            try:
                data = json.loads(f.read_text())
                if isinstance(data, dict):
                    # Match by DOI or title
                    if "doi" in data:
                        paths.add(data["doi"])
                    if "title" in data:
                        paths.add(data["title"].lower().strip()[:80])
            except:
                pass
    return paths


def get_claimed_ids(queue):
    return {c["pdf_id"] for c in queue.get("active_claims", [])}


def get_available(inventory, extracted_ids, claimed_ids):
    """Get PDF IDs that haven't been extracted or claimed, with valid size."""
    available = []
    for uid, info in sorted(inventory.items()):
        if uid in extracted_ids or uid in claimed_ids:
            continue
        size = info.get("size_bytes", 0)
        if size < MIN_PDF_BYTES or size > MAX_PDF_BYTES:
            continue
        if not os.path.exists(info.get("path", "")):
            continue
        available.append((uid, info))
    return available


def cmd_status(args):
    inventory = load_inventory()
    queue = load_queue()
    extracted_ids = get_extracted_pdf_ids()
    claimed_ids = get_claimed_ids(queue)
    available = get_available(inventory, extracted_ids, claimed_ids)

    # Count findings from existing extractions
    total_findings = 0
    total_extracted = 0
    skip = {"batch_progress.json", "comparison_report.json", "gold_standard_papers.json",
            "unmatched_dois.json", "doi_mismatches.json", "current_batch.json",
            "EXTRACTION_QUEUE.json", "AG_EXTRACTION_TASK.md"}
    for f in GS_DIR.iterdir():
        if f.suffix == ".json" and f.name not in skip:
            try:
                data = json.loads(f.read_text())
                if isinstance(data, dict) and ("doi" in data or "title" in data):
                    total_extracted += 1
                    total_findings += data.get("n_findings", len(data.get("findings", [])))
            except:
                pass

    valid_pdfs = sum(1 for uid, info in inventory.items()
                     if MIN_PDF_BYTES <= info.get("size_bytes", 0) <= MAX_PDF_BYTES)

    print("=" * 60)
    print("  EXTRACTION PIPELINE STATUS (v2 — PDF-First)")
    print("=" * 60)
    print(f"  Total PDFs in inventory:   {len(inventory)}")
    print(f"  Valid size (50KB-50MB):    {valid_pdfs}")
    print(f"  Already extracted:         {total_extracted}")
    print(f"  With pdf_id tracking:      {len(extracted_ids)}")
    print(f"  Currently claimed:         {len(claimed_ids)}")
    print(f"  Available (unclaimed):     {len(available)}")
    print(f"  Total findings extracted:  {total_findings}")
    print(f"  Last updated:              {queue.get('stats', {}).get('last_updated', 'never')}")
    print()

    if queue.get("active_claims"):
        print("  ACTIVE CLAIMS:")
        for c in queue["active_claims"]:
            print(f"    {c['worker']}: {c['pdf_id']} — {c.get('filename', '?')[:60]}")
        print()

    if available:
        print(f"  NEXT 5 AVAILABLE:")
        for uid, info in available[:5]:
            print(f"    {uid}: {info['filename'][:70]}")
            print(f"         ({info['size_bytes']/1024:.0f} KB, folder {info['folder']})")
        print()

    # Update stats
    queue["stats"]["total_pdfs"] = len(inventory)
    queue["stats"]["valid_pdfs"] = valid_pdfs
    queue["stats"]["extracted"] = total_extracted
    queue["stats"]["claimed"] = len(claimed_ids)
    queue["stats"]["remaining"] = len(available)
    queue["stats"]["total_findings"] = total_findings
    save_queue(queue)


def cmd_claim(args):
    inventory = load_inventory()
    queue = load_queue()
    extracted_ids = get_extracted_pdf_ids()
    claimed_ids = get_claimed_ids(queue)
    available = get_available(inventory, extracted_ids, claimed_ids)

    n = args.n or 5
    to_claim = available[:n]

    if not to_claim:
        print("No papers available to claim.")
        return

    new_claims = []
    for uid, info in to_claim:
        claim = {
            "pdf_id": uid,
            "pdf_path": info["path"],
            "filename": info["filename"],
            "worker": args.worker_id,
            "claimed_at": datetime.now().isoformat(),
            "status": "claimed"
        }
        queue["active_claims"].append(claim)
        new_claims.append(claim)

    save_queue(queue)

    print(f"Claimed {len(new_claims)} papers for worker '{args.worker_id}':")
    for c in new_claims:
        print(f"  {c['pdf_id']}: {c['filename'][:70]}")

    # JSON output for programmatic use
    print(f"\n--- JSON ---")
    print(json.dumps([{"pdf_id": c["pdf_id"], "pdf_path": c["pdf_path"], "filename": c["filename"]}
                       for c in new_claims], indent=2))


def run_image_extraction(pdf_id):
    """Automatically extract images from the PDF after extraction is complete."""
    import subprocess

    script = PROJECT_ROOT / "scripts" / "extract_stimulus_images.py"
    if not script.exists():
        print(f"  [WARN] Image extraction script not found: {script}")
        return

    # Get pages to render from the extraction JSON (if stimulus_figure_pages specified)
    json_path = GS_DIR / f"{pdf_id}.json"
    pages_arg = []
    if json_path.exists():
        try:
            data = json.loads(json_path.read_text())
            # Check for article-level stimulus_figure_pages
            figure_pages = data.get("stimulus_figure_pages", [])
            # Also check individual findings
            for finding in data.get("findings", []):
                stim = finding.get("stimulus_description", {})
                if isinstance(stim, dict):
                    fp = stim.get("stimulus_figure_pages", [])
                    if isinstance(fp, list):
                        figure_pages.extend(fp)
            figure_pages = sorted(set(figure_pages))
            if figure_pages:
                pages_arg = ["--pages", ",".join(str(p) for p in figure_pages)]
        except (json.JSONDecodeError, KeyError):
            pass

    # Run embedded image extraction
    cmd = [sys.executable, str(script), pdf_id] + pages_arg
    print(f"  [IMAGE] Extracting images: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120,
                                cwd=str(PROJECT_ROOT))
        if result.returncode == 0:
            # Count extracted images from output
            for line in result.stdout.split("\n"):
                if "Total images:" in line or "Embedded images extracted:" in line:
                    print(f"  [IMAGE] {line.strip()}")
            # Update the extraction JSON with image references
            _link_images_to_json(pdf_id)
        else:
            print(f"  [IMAGE] Warning: {result.stderr[:200]}")
    except subprocess.TimeoutExpired:
        print(f"  [IMAGE] Timed out after 120s")
    except Exception as e:
        print(f"  [IMAGE] Error: {e}")


def _link_images_to_json(pdf_id):
    """After image extraction, update the extraction JSON with image file references."""
    json_path = GS_DIR / f"{pdf_id}.json"
    manifest_path = GS_DIR / "stimulus_images" / pdf_id / "manifest.json"

    if not json_path.exists() or not manifest_path.exists():
        return

    try:
        with open(manifest_path) as f:
            manifest = json.load(f)
        with open(json_path) as f:
            data = json.load(f)

        n_images = manifest.get("total_images", 0)
        image_files = [img["filename"] for img in manifest.get("embedded_images", [])]
        image_files += [img["filename"] for img in manifest.get("rendered_pages", [])]

        # Add root-level image manifest
        data["stimulus_image_manifest"] = {
            "image_directory": f"stimulus_images/{pdf_id}/",
            "total_images": n_images,
            "image_files": image_files
        }

        # Update findings
        for finding in data.get("findings", []):
            stim = finding.get("stimulus_description")
            if stim and isinstance(stim, dict) and n_images > 0:
                stim["stimulus_image_available"] = True
                stim["stimulus_image_files"] = image_files

        with open(json_path, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"  [IMAGE] Linked {n_images} images to {pdf_id}.json")
    except Exception as e:
        print(f"  [IMAGE] Error linking images: {e}")


def cmd_complete(args):
    queue = load_queue()
    queue["active_claims"] = [
        c for c in queue["active_claims"]
        if not (c["pdf_id"] == args.pdf_id and c["worker"] == args.worker_id)
    ]
    queue["completed"].append({
        "pdf_id": args.pdf_id,
        "worker": args.worker_id,
        "completed_at": datetime.now().isoformat()
    })
    save_queue(queue)
    print(f"Marked {args.pdf_id} complete for worker '{args.worker_id}'")

    # Automatically extract and link stimulus images
    run_image_extraction(args.pdf_id)


def cmd_release(args):
    queue = load_queue()
    released = [c for c in queue["active_claims"] if c["worker"] == args.worker_id]
    queue["active_claims"] = [c for c in queue["active_claims"] if c["worker"] != args.worker_id]
    save_queue(queue)
    print(f"Released {len(released)} claims for worker '{args.worker_id}'")


def cmd_next(args):
    inventory = load_inventory()
    queue = load_queue()
    extracted_ids = get_extracted_pdf_ids()
    claimed_ids = get_claimed_ids(queue)
    available = get_available(inventory, extracted_ids, claimed_ids)

    n = args.n or 10
    for uid, info in available[:n]:
        print(json.dumps({"pdf_id": uid, "pdf_path": info["path"], "filename": info["filename"]}))


def main():
    parser = argparse.ArgumentParser(description="Extraction coordinator v2 (PDF-first)")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("status", help="Show extraction status")

    p_claim = sub.add_parser("claim", help="Claim papers for a worker")
    p_claim.add_argument("worker_id", help="Worker ID (cowork, ag, cowork-scheduled)")
    p_claim.add_argument("--n", type=int, default=5, help="Number to claim")

    p_complete = sub.add_parser("complete", help="Mark a paper as extracted")
    p_complete.add_argument("worker_id")
    p_complete.add_argument("pdf_id")

    p_release = sub.add_parser("release", help="Release all claims for a worker")
    p_release.add_argument("worker_id")

    p_next = sub.add_parser("next", help="List next N available papers")
    p_next.add_argument("--n", type=int, default=10)

    args = parser.parse_args()

    if args.command == "status":
        cmd_status(args)
    elif args.command == "claim":
        cmd_claim(args)
    elif args.command == "complete":
        cmd_complete(args)
    elif args.command == "release":
        cmd_release(args)
    elif args.command == "next":
        cmd_next(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
