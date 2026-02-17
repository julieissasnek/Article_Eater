
import csv
import os
from pathlib import Path

# Config
PDF_DIR = Path("/Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/data/production/pdf_repaired")
OUTPUT_QUEUE = Path("/Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/data/production/batch_15_pdf_repair_queue.csv")

def main():
    if not PDF_DIR.exists():
        print(f"Error: {PDF_DIR} does not exist.")
        return

    # List PDFs
    pdf_files = sorted([f for f in PDF_DIR.iterdir() if f.suffix.lower() == ".pdf"])
    print(f"Found {len(pdf_files)} PDFs in {PDF_DIR}")

    rows = []
    
    # Header from the main queue file inspection earlier:
    # paper_id,doi,title,year,venue,pdf_path,status,queued_at,processed_at,reason,source,resolved_pdf_path,...
    
    header = [
        "paper_id", "doi", "title", "year", "venue", "pdf_path", "status", 
        "queued_at", "processed_at", "reason", "source", "resolved_pdf_path",
        "n_tables", "n_claims", "error", 
        "article_type_classifier_version", "article_type_confidence", "article_type_diagnostics",
        "article_type_family", "article_type_margin", "article_type_needs_review",
        "article_type_predicted_family", "article_type_runner_up", "article_type_signals",
        "preprocess_cache_path", "preprocess_checked_at", "preprocess_cid_density",
        "preprocess_cid_hits", "preprocess_error", "preprocess_nonempty_pages",
        "preprocess_page_count", "preprocess_status", "preprocess_text_chars", "preprocess_warning_flags",
        "prior_n_claims", "prior_n_tables", "prior_status", "retry_error", "retry_status"
    ]

    for pdf in pdf_files:
        filename = pdf.name
        # Attempt to derive DOI/PaperID from filename
        # Format: doi_10.1068_p5292.pdf -> 10.1068/p5292
        # Format: zotero_IM8R9VRM.pdf -> zotero:IM8R9VRM
        
        if filename.startswith("doi_"):
            # strip .pdf
            stem = filename[:-4]
            # remove doi_ prefix
            stem = stem[4:]
            # replace first underscore with slash ? No, usually dots in DOIs are preserved, slashes become underscores in filenames.
            # actually usually standard filesystem sanitization replaces / with _
            # E.g. 10.1068/p5292 -> 10.1068_p5292
            # But wait, is it 10.1068/p5292 or 10.1068.p5292?
            # Let's assume standard substitution: / -> _
            # But we need to be careful about where the slash is.
            # Usually DOI is prefix/suffix. 10.xxxx/yyyy.
            # So the first underscore after the 10.xxxx part might be the slash.
            # Let's just use the filename as the ID if we are unsure, or try to reconstruct.
            # For extraction purposes, the paper_id is mainly a key.
            # Let's recreate it as best as possible.
            
            # Simple heuristic: replace all _ with / is probably wrong (some suffix might have underscores).
            # But typically DOI has one slash.
            # Let's check a known one: doi_10.1068_p5292.pdf -> 10.1068/p5292
            clean_doi = stem.replace("_", "/", 1) # Replace first underscore only?
            # 10.1068_p5292 -> 10.1068/p5292. Correct.
            
            paper_id = f"doi:{clean_doi}"
            doi = clean_doi
        elif filename.startswith("zotero_"):
             # zotero_IM8R9VRM.pdf
             stem = filename[:-4]
             key = stem.split("_")[1]
             paper_id = f"zotero:{key}"
             doi = ""
        else:
            paper_id = f"file:{filename}"
            doi = ""

        row = {k: "" for k in header}
        row["paper_id"] = paper_id
        row["doi"] = doi
        row["pdf_path"] = str(pdf)
        row["status"] = "queued_init" # Important: Must match the startswith('queued_') filter
        row["source"] = "manual_batch_15_repair"
        
        rows.append(row)

    print(f"Generated {len(rows)} rows.")
    
    with open(OUTPUT_QUEUE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"Wrote queue to {OUTPUT_QUEUE}")

if __name__ == "__main__":
    main()
