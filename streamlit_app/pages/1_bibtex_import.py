"""
BibTeX Import Wizard for Article Eater.
Simple 3-step flow: Upload BibTeX → Match → Export
"""

import streamlit as st
from pathlib import Path
import sys
import json
import time
from datetime import datetime
from typing import List

# Add project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.services.bibtex_utils import (
    BibTeXEntry,
    PDFBibTeXMatcher,
    parse_bibtex_string,
    create_match_report,
)

# BIB-7: Ingestion service
try:
    from src.services.bibtex_ingestion import BibTeXIngestionService
    INGESTION_AVAILABLE = True
except ImportError:
    INGESTION_AVAILABLE = False

# PDF storage
try:
    from app.config.pdf_storage import get_config
    PDF_STORAGE_AVAILABLE = True
except ImportError:
    PDF_STORAGE_AVAILABLE = False


# -----------------------------------------------------------------------------
# AUTO-DISCOVER PDFS ON LOAD
# -----------------------------------------------------------------------------

def discover_pdfs() -> List[dict]:
    """Auto-discover PDFs from configured storage."""
    pdfs = []

    # Always scan Zotero directly (most reliable)
    zotero_path = Path.home() / "Zotero" / "storage"
    if zotero_path.exists():
        for pdf_path in zotero_path.glob("**/*.pdf"):
            pdfs.append({
                "path": str(pdf_path),
                "name": pdf_path.name,
                "source": "Zotero",
            })

    # Also check Article Eater data dir
    ae_path = Path(__file__).parent.parent.parent / "data" / "pdfs"
    if ae_path.exists():
        for pdf_path in ae_path.glob("**/*.pdf"):
            pdfs.append({
                "path": str(pdf_path),
                "name": pdf_path.name,
                "source": "AE",
            })

    return pdfs


# Force rescan on first load
if "pdfs_loaded" not in st.session_state:
    st.session_state.pdfs = discover_pdfs()
    st.session_state.pdfs_loaded = True

if "step" not in st.session_state:
    st.session_state.step = 1

if "entries" not in st.session_state:
    st.session_state.entries = []

if "matches" not in st.session_state:
    st.session_state.matches = []

if "unmatched" not in st.session_state:
    st.session_state.unmatched = []


# -----------------------------------------------------------------------------
# WIZARD UI
# -----------------------------------------------------------------------------

st.title("BibTeX Import")

# Progress indicator
cols = st.columns(3)
for i, (col, label) in enumerate(zip(cols, ["1. Upload BibTeX", "2. Review Matches", "3. Export"])):
    if st.session_state.step == i + 1:
        col.markdown(f"**→ {label}**")
    elif st.session_state.step > i + 1:
        col.markdown(f"~~{label}~~")
    else:
        col.markdown(f"{label}")

st.markdown("---")

# Show PDF count with refresh option
col1, col2 = st.columns([4, 1])
n_pdfs = len(st.session_state.pdfs)
col1.caption(f"{n_pdfs} PDFs available" + (f" (storage available: {PDF_STORAGE_AVAILABLE})" if n_pdfs == 0 else ""))
if col2.button("Rescan", key="rescan"):
    del st.session_state["pdfs_loaded"]  # Force reload
    st.rerun()


# =============================================================================
# STEP 1: UPLOAD BIBTEX
# =============================================================================

if st.session_state.step == 1:
    st.subheader("Upload your BibTeX file")
    st.caption("Export from Zotero: File → Export Library → BibTeX format")

    uploaded = st.file_uploader("Choose .bib file", type=["bib", "bibtex", "txt"])

    if uploaded:
        try:
            content = uploaded.read().decode("utf-8")
            entries = parse_bibtex_string(content)
            st.session_state.entries = entries
            st.success(f"Parsed {len(entries)} entries")

            # Show preview
            if entries:
                st.caption("Preview (first 5):")
                for e in entries[:5]:
                    st.text(f"  {e.cite_key}: {e.title[:60] if e.title else '(no title)'}...")

            if st.button("Next: Match to PDFs"):
                pdf_paths = [Path(p["path"]) for p in st.session_state.pdfs]
                n_pdfs = len(pdf_paths)

                st.info(f"Matching {n_pdfs} PDFs against {len(entries)} BibTeX entries. This may take a few minutes...")
                progress = st.progress(0, text=f"Matching 0/{n_pdfs} PDFs...")
                matcher = PDFBibTeXMatcher(entries)

                matched = []
                unmatched = []
                start_time = time.time()

                for i, pdf_path in enumerate(pdf_paths):
                    result = matcher.match_pdf(pdf_path)
                    if result:
                        matched.append(result)
                    else:
                        unmatched.append(pdf_path)

                    if i % 50 == 0 and i > 0:  # Update every 50 PDFs
                        elapsed = time.time() - start_time
                        rate = i / elapsed if elapsed > 0 else 1
                        remaining = int((n_pdfs - i) / rate) if rate > 0 else 0
                        mins, secs = divmod(remaining, 60)
                        time_str = f"{mins}m {secs}s" if mins > 0 else f"{secs}s"
                        progress.progress(i / n_pdfs, text=f"Matching {i}/{n_pdfs} PDFs... ({len(matched)} matches, ~{time_str} remaining)")

                elapsed_total = int(time.time() - start_time)
                progress.progress(1.0, text=f"Done: {len(matched)} matches found in {elapsed_total}s")

                st.session_state.matches = matched
                st.session_state.unmatched = [p.name for p in unmatched]
                st.session_state.step = 2
                st.rerun()

        except Exception as e:
            st.error(f"Failed to parse: {e}")


# =============================================================================
# STEP 2: REVIEW MATCHES
# =============================================================================

elif st.session_state.step == 2:
    st.subheader("Review matches")

    matches = st.session_state.matches
    entries = st.session_state.entries

    # Summary
    col1, col2, col3 = st.columns(3)
    col1.metric("Matched", len(matches))
    col2.metric("BibTeX entries", len(entries))
    col3.metric("Unmatched PDFs", len(st.session_state.unmatched))

    if matches:
        st.markdown("---")
        st.caption("Matched items:")

        for m in matches[:50]:
            conf = f"{m.confidence:.0%}"
            st.text(f"  [{conf}] {m.entry.cite_key} ← {m.pdf_path.name[:40]}")

        if len(matches) > 50:
            st.caption(f"  ... and {len(matches) - 50} more")

    col1, col2 = st.columns(2)
    if col1.button("← Back"):
        st.session_state.step = 1
        st.rerun()
    if col2.button("Next: Export →"):
        st.session_state.step = 3
        st.rerun()


# =============================================================================
# STEP 3: EXPORT
# =============================================================================

elif st.session_state.step == 3:
    st.subheader("Export")

    matches = st.session_state.matches

    if not matches:
        st.warning("No matches to export")
    else:
        st.markdown(f"**{len(matches)} matched items ready**")

        # Generate paper.json bundle
        papers = []
        for m in matches:
            paper = m.entry.to_paper_json()
            paper["pdf_path"] = str(m.pdf_path)
            paper["match_confidence"] = m.confidence
            papers.append(paper)

        papers_json = json.dumps(papers, indent=2, ensure_ascii=False)

        st.download_button(
            "Download paper.json bundle",
            data=papers_json,
            file_name=f"papers_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
        )

        # Also offer CSV
        csv_lines = ["cite_key,title,year,doi,pdf_path,confidence"]
        for m in matches:
            e = m.entry
            csv_lines.append(f'"{e.cite_key}","{e.title or ""}",{e.year or ""},"{e.doi or ""}","{m.pdf_path.name}",{m.confidence:.2f}')

        st.download_button(
            "Download CSV summary",
            data="\n".join(csv_lines),
            file_name=f"matches_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )

        # BIB-7: Direct pipeline ingestion
        st.markdown("---")
        st.subheader("Run Extraction Pipeline")

        if INGESTION_AVAILABLE:
            output_dir = st.text_input(
                "Output directory",
                value=str(Path.home() / "ae_outputs"),
                help="Where to save extraction results"
            )

            profile = st.selectbox(
                "Extraction profile",
                options=["standard", "thorough", "quick"],
                index=0,
            )

            if st.button("🚀 Run Pipeline on All Matches"):
                with st.spinner(f"Processing {len(matches)} papers..."):
                    try:
                        service = BibTeXIngestionService(
                            output_base=Path(output_dir),
                            profile=profile,
                        )

                        # Convert matches to paper dicts
                        papers = []
                        for m in matches:
                            paper = m.entry.to_paper_json()
                            paper["pdf_path"] = str(m.pdf_path)
                            papers.append(paper)

                        result = service.ingest_batch(papers)

                        st.success(f"✅ Processed {result.total} papers: {result.succeeded} succeeded, {result.failed} failed, {result.skipped} skipped")

                        # Show results
                        if result.results:
                            st.write("**Results:**")
                            for r in result.results[:20]:
                                icon = "✅" if r.status == "success" else ("⚠️" if r.status == "partial" else "❌")
                                claims_info = f" ({r.n_claims} claims)" if r.n_claims else ""
                                st.text(f"{icon} {r.paper_id}{claims_info}")
                            if len(result.results) > 20:
                                st.caption(f"... and {len(result.results) - 20} more")

                    except Exception as e:
                        st.error(f"Pipeline error: {e}")
        else:
            st.warning("Ingestion service not available. Install dependencies or check import.")

    if st.button("← Start over"):
        st.session_state.step = 1
        st.session_state.entries = []
        st.session_state.matches = []
        st.rerun()
