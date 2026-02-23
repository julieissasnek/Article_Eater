"""
Batch Processor for Article Eater Extraction Pipeline (Sprint D Task D.10).

Orchestrates the extraction of claims from triaged papers using the Claim Extraction Engine (D.6).
Focuses on high precision by filtering for high-confidence papers and using rigorous extraction logic.
"""

import json
import re
import time
import argparse
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple
import pandas as pd
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.extraction.row_classifier_codex import normalize_ocr_text
from src.extraction.table_semantics_codex import build_table_content_profile

# Import D.6 Claim Extraction Engine
try:
    from src.extraction.claim_extractor import extract_claims_from_paper
except ImportError as e:
    import traceback
    traceback.print_exc()
    print(f"WARNING: Could not import ClaimExtractor: {e}")
    extract_claims_from_paper = None

# Paths
TRIAGE_PATH = "data/production/paper_triage.json"
TABLES_PATH = "data/production/table_classifications.json"
CONTENT_CSV_PATH = "data/production/realtime_pdf_confirmed_rows.csv"
OUTPUT_PATH = "data/production/batch_15_extraction_results.jsonl"
STRUCTURED_OUTPUT_PATH = "data/production/structured_claims_ag.json"


class BatchProcessor:
    def __init__(
        self,
        limit: int = None,
        dry_run: bool = False,
        method: str = "llm",
        structured_output_path: str = STRUCTURED_OUTPUT_PATH,
    ):
        self.limit = limit
        self.dry_run = dry_run
        self.method = method # "llm" or "rule_based"
        self.structured_output_path = structured_output_path
        self.stats = {
            "processed": 0,
            "claims_extracted": 0,
            "claims_kept": 0,
            "errors": 0,
            "skipped": 0,
            "tables_skipped_ocr": 0,
            "tables_skipped_semantic": 0,
            "tables_transformed_matrix": 0,
            "tables_transformed_stepwise": 0,
        }
        self.reconstructed_tables = {} # To store CSV-reconstructed tables
        self._all_kept_claims: list[dict[str, Any]] = []

    def _load_triage_papers(self, triage_data: dict) -> list[dict[str, Any]]:
        """Support both list-style and map-style triage payloads."""
        if isinstance(triage_data, dict) and isinstance(triage_data.get("papers"), list):
            return [p for p in triage_data["papers"] if isinstance(p, dict)]
        if isinstance(triage_data, list):
            return [p for p in triage_data if isinstance(p, dict)]
        if isinstance(triage_data, dict):
            out: list[dict[str, Any]] = []
            for paper_id, info in triage_data.items():
                if not isinstance(info, dict):
                    continue
                out.append(
                    {
                        "paper_id": paper_id,
                        "triage_type": info.get("triage_type") or info.get("type"),
                        "extractable": info.get("extractable", True),
                        "confidence": info.get("confidence"),
                    }
                )
            return out
        return []

    def load_data(self):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Loading triage data...")
        with open(TRIAGE_PATH, 'r') as f:
            triage_data = json.load(f)
            self.triage_papers = self._load_triage_papers(triage_data)
        
        # Create a set of paper_ids from triage data for filtering
        valid_triage_pids = {p.get('paper_id') for p in self.triage_papers if p.get('paper_id')}

        print(f"[{datetime.now().strftime('%H:%M:%S')}] Loading table classifications...")
        self.table_data = {}
        if Path(TABLES_PATH).exists():
            with open(TABLES_PATH, 'r') as f:
                raw_tables = json.load(f)
                
                # Handle list vs dict format for tables
                if isinstance(raw_tables, list):
                    table_list = raw_tables
                elif isinstance(raw_tables, dict) and 'tables' in raw_tables and isinstance(raw_tables['tables'], list):
                    # Format: {"tables": [...]}
                    table_list = raw_tables['tables']
                elif isinstance(raw_tables, dict):
                    # Format: {"TBL-1": {...}, "TBL-2": {...}}
                    # In this case, the table_id is the key, not inside the dict value.
                    # We need to preserve the key as table_id.
                    for tid, t_data in raw_tables.items():
                        pid = t_data.get('paper_id')
                        if pid and pid in valid_triage_pids: # Only add if paper is in triage
                            if pid not in self.table_data: self.table_data[pid] = []
                            # Add table_id to the table data itself for consistency
                            t_data['table_id'] = tid
                            self.table_data[pid].append(t_data)
                    table_list = [] # Clear to avoid double processing
                else:
                    table_list = []

                # Process list format tables (if any)
                for t in table_list:
                    pid = t.get('paper_id')
                    if pid and pid in valid_triage_pids: # Only add if paper is in triage
                        if pid not in self.table_data: self.table_data[pid] = []
                        self.table_data[pid].append(t)

        # Load content CSV to reconstruct full tables
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Loading content CSV for table reconstruction...")
        
        try:
            # Read only legitimate columns to avoid parsing errors
            # We need: paper_id, source_table_id, source_table_row, source_quote
            df = pd.read_csv(
                CONTENT_CSV_PATH, 
                usecols=['paper_id', 'source_table_id', 'source_table_row', 'source_quote'],
                dtype={'source_table_row': 'Int64', 'source_quote': str}
            )
            
            # Filter for rows belonging to our target papers and having a table ID
            df = df[df['paper_id'].isin(valid_triage_pids) & df['source_table_id'].notna()]
            
            # Group by paper and table
            for (pid, tid), group in df.groupby(['paper_id', 'source_table_id']):
                # Sort by row index
                sorted_rows = group.sort_values('source_table_row')['source_quote'].tolist()
                valid_rows = [r for r in sorted_rows if pd.notna(r) and len(str(r)) > 1]
                
                if pid not in self.reconstructed_tables:
                    self.reconstructed_tables[pid] = {}
                self.reconstructed_tables[pid][tid] = valid_rows
                
            print(f"Reconstructed {sum(len(t) for t in self.reconstructed_tables.values())} tables from CSV.")
            
        except Exception as e:
            print(f"Warning: Failed to reconstruct tables from CSV: {e}")

        print(f"[{datetime.now().strftime('%H:%M:%S')}] Loading content CSV (columns only)...")
        # Load header first to check available columns
        header_df = pd.read_csv(CONTENT_CSV_PATH, nrows=0)
        available_cols = set(header_df.columns)
        
        # Determine which columns we can actually use
        desired_cols = ['paper_id', 'title', 'abstract', 'article_type_predicted_family']
        use_cols = [c for c in desired_cols if c in available_cols]
        
        # Always need paper_id
        if 'paper_id' not in use_cols:
            raise ValueError("CSV missing required 'paper_id' column")

        self.df = pd.read_csv(
            CONTENT_CSV_PATH, 
            usecols=use_cols, 
            low_memory=False
        )
        
        # Backfill missing columns with empty strings so logic downstream doesn't break
        for col in desired_cols:
            if col not in self.df.columns:
                self.df[col] = ""

        
        # Create lookup for paper metadata
        self.metadata_lookup = {}
        # Iterate over unique papers to build metadata dict
        # (A bit slow but robust)
        unique_ids = self.df['paper_id'].unique()
        for pid in unique_ids:
            subset = self.df[self.df['paper_id'] == pid].iloc[0]
            self.metadata_lookup[pid] = {
                "title": str(subset.get('title', '')),
                "abstract": str(subset.get('abstract', '')),
                "article_type": str(subset.get('article_type_predicted_family', ''))
            }


    def get_target_papers(self) -> List[str]:
        """
        Filter papers to find high-quality candidates for extraction.
        Criteria:
        1. Triage type is 'empirical' or 'meta_analysis'
        2. Marked as 'extractable'
        3. Has classified tables
        """
        targets = []
        for p in self.triage_papers:
            pid = p['paper_id']
            
            # Strict filtering for high precision
            is_empirical = p.get('triage_type') in ['empirical', 'meta_analysis']
            is_extractable = p.get('extractable', False)
            has_tables = pid in self.table_data and len(self.table_data[pid]) > 0
            
            if is_empirical and is_extractable and has_tables:
                targets.append(pid)
        
        print(f"Found {len(targets)} candidate papers (Empirical + Extractable + Has Tables).")
        
        if self.limit:
            targets = targets[:self.limit]
            print(f"Limiting processing to first {self.limit} papers.")
            
        return targets

    def _clean_ocr_text(self, text: str) -> str:
        """Fix common OCR garbage using Codex normalization + numeric specific fixes."""
        text = normalize_ocr_text(text)
        if not text:
            return ""
            
        # Restore critical numeric fixes from previous iterations
        text = text.replace('¼', '=').replace('ð', '(').replace('Þ', ')')
        text = text.replace('po0', 'p<0').replace('po.', 'p<.').replace('po1', 'p<1')
        
        # Swaps colons for decimals between digits (e.g., 7:03 -> 7.03)
        text = re.sub(r'(?<=\d):(?=\d)', '.', text)
        
        # Swaps semicolons for commas between digits (e.g., 1;120 -> 1,120)
        text = re.sub(r'(?<=\d);(?=\d)', ',', text)
        
        return text

    def _ocr_quality_check(self, text: str) -> dict[str, Any]:
        """Detect major OCR corruption before extraction."""
        text = text or ""
        issues: list[str] = []

        doubled = re.findall(r'(.)\1{2,}', text)
        if len(doubled) > 2:
            issues.append("character_doubling")

        if len(text) > 30 and ' ' not in text:
            issues.append("concatenated_words")

        consonant_clusters = re.findall(r'[bcdfghjklmnpqrstvwxyz]{4,}', text.lower())
        if len(consonant_clusters) > 2:
            issues.append("column_interleaving")

        non_ascii = sum(1 for c in text if ord(c) > 127)
        if non_ascii / max(len(text), 1) > 0.1:
            issues.append("encoding_corruption")

        return {
            "clean": len(issues) == 0,
            "issues": issues,
            "confidence": max(0.0, 1.0 - 0.3 * len(issues)),
        }

    def _table_passes_ocr_gate(self, table: Dict[str, Any]) -> bool:
        rows = table.get("rows", []) or []
        if not rows:
            return False
        failures = 0
        for row in rows:
            row_text = row.get("text") or row.get("source_quote") or row.get("statement") or ""
            qc = self._ocr_quality_check(row_text)
            if not qc["clean"]:
                failures += 1
        # Allow some noise but skip heavily corrupted tables.
        return (failures / max(1, len(rows))) <= 0.35

    def _parse_colon_columns(self, text: str) -> dict[int, str]:
        """Parse row format like 'col_1: X; col_2: Y; col_3: Z'."""
        cols: dict[int, str] = {}
        matches = re.findall(r'col_(\d+)\s*:\s*([^;]+)', text or "", flags=re.IGNORECASE)
        for idx, val in matches:
            try:
                cols[int(idx)] = val.strip()
            except ValueError:
                continue
        return cols

    def _extract_caption_dv(self, table: Dict[str, Any], metadata: Dict[str, Any]) -> str | None:
        """Find likely DV phrase from caption/context before row parsing."""
        candidates = [
            table.get("sample_content", ""),
            metadata.get("title", ""),
            metadata.get("abstract", ""),
        ]
        patterns = [
            re.compile(r'predicting\s+([a-z0-9 _\-]+?)\s+from', re.IGNORECASE),
            re.compile(r'effects?\s+on\s+([a-z0-9 _\-]+)', re.IGNORECASE),
            re.compile(r'([a-z0-9 _\-]+?)\s+by\s+condition', re.IGNORECASE),
            re.compile(r'impact\s+on\s+([a-z0-9 _\-]+)', re.IGNORECASE),
        ]
        for text in candidates:
            for pattern in patterns:
                m = pattern.search(str(text))
                if m:
                    phrase = m.group(1).strip(" .,:;")
                    if 3 <= len(phrase) <= 80:
                        return phrase
        return None

    def _looks_like_correlation_matrix(self, table: Dict[str, Any]) -> bool:
        if str(table.get("type", "")).upper() == "RESULTS_CORRELATION":
            return True
        rows = table.get("rows", []) or []
        if len(rows) < 3:
            return False
        sample = " ".join((r.get("text", "") or "") for r in rows[:6]).lower()
        if "correlation" in sample or "pearson" in sample:
            return True
        numeric_hits = len(re.findall(r'(?<!\d)-?0?\.\d{2,3}(?!\d)', sample))
        return numeric_hits >= 4 and "col_1" in sample and "col_2" in sample

    def _transform_correlation_matrix(self, table: Dict[str, Any]) -> List[dict[str, str]]:
        """Convert matrix cells into relation sentences claim_extractor can parse."""
        rows = table.get("rows", []) or []
        parsed = [self._parse_colon_columns(r.get("text") or r.get("source_quote") or "") for r in rows]
        parsed = [p for p in parsed if p]
        if len(parsed) < 2:
            return rows

        # Build row index -> variable map from first column labels.
        row_idx_to_var: dict[int, str] = {}
        data_rows: list[Tuple[int, dict[int, str]]] = []
        for p in parsed:
            label = p.get(1, "")
            m = re.match(r'^\s*\(?(\d{1,2})\)?[.\s-]+(.+?)\s*$', label)
            if m:
                row_idx_to_var[int(m.group(1))] = m.group(2).strip()
                data_rows.append((int(m.group(1)), p))
            elif label:
                row_id = len(data_rows) + 1
                row_idx_to_var[row_id] = label.strip()
                data_rows.append((row_id, p))

        if not data_rows:
            return rows

        # Column map from first parsed row (header-like) where values may be "1", "2", etc.
        header = parsed[0]
        col_to_var: dict[int, str] = {}
        for cidx, value in header.items():
            if cidx == 1:
                continue
            token = str(value).strip()
            if re.fullmatch(r'\(?\d{1,2}\)?', token):
                idx = int(re.sub(r'\D', '', token))
                mapped = row_idx_to_var.get(idx)
                if mapped:
                    col_to_var[cidx] = mapped
            elif token and len(token) < 80:
                col_to_var[cidx] = token

        synthetic_rows: list[dict[str, str]] = []
        for row_idx, prow in data_rows:
            row_var = row_idx_to_var.get(row_idx)
            if not row_var:
                continue
            for cidx, raw in prow.items():
                if cidx == 1:
                    continue
                col_var = col_to_var.get(cidx)
                if not col_var or col_var == row_var:
                    continue
                text = str(raw).strip()
                m = re.search(r'(?<!\d)(-?0?\.\d{2,3})(?!\d)', text)
                if not m:
                    continue
                rval = m.group(1)
                synthetic_rows.append(
                    {
                        "text": f"{row_var} was associated with {col_var} (r = {rval}).",
                        "source_quote": f"{row_var} was associated with {col_var} (r = {rval}).",
                    }
                )

        return synthetic_rows if synthetic_rows else rows

    def _looks_like_stepwise_regression(self, table: Dict[str, Any]) -> bool:
        if str(table.get("type", "")).upper() == "RESULTS_REGRESSION":
            return True
        joined = " ".join((r.get("text", "") or "") for r in table.get("rows", [])[:12]).lower()
        signals = ["step", "model", "beta", "β", "r2", "r²", "predictor"]
        return sum(1 for s in signals if s in joined) >= 3

    def _transform_stepwise_regression(self, table: Dict[str, Any], metadata: Dict[str, Any]) -> List[dict[str, str]]:
        rows = table.get("rows", []) or []
        dv = self._extract_caption_dv(table, metadata) or "outcome"
        synthetic: list[dict[str, str]] = []

        for row in rows:
            text = row.get("text") or row.get("source_quote") or ""
            cols = self._parse_colon_columns(text)
            if not cols:
                continue
            predictor = cols.get(1, "").strip()
            if not predictor or len(predictor) < 3:
                continue
            if re.search(r'^(model|step|constant|intercept)\b', predictor, re.IGNORECASE):
                continue

            joined = " ".join(cols.get(k, "") for k in sorted(cols))
            beta_match = re.search(r'(?:β|beta)\s*=?\s*([-+]?\d*\.?\d+)', joined, re.IGNORECASE)
            p_match = re.search(r'\bp\s*[<=>]\s*([.\d]+)', joined, re.IGNORECASE)
            t_match = re.search(r'\bt\s*\(?\d*\)?\s*=?\s*([-+]?\d*\.?\d+)', joined, re.IGNORECASE)
            if not (beta_match or p_match or t_match):
                continue

            parts = [f"{predictor} predicted {dv}"]
            if beta_match:
                parts.append(f"beta = {beta_match.group(1)}")
            if t_match:
                parts.append(f"t = {t_match.group(1)}")
            if p_match:
                parts.append(f"p = {p_match.group(1).strip('.,;')}")
            sentence = ", ".join(parts) + "."
            synthetic.append({"text": sentence, "source_quote": sentence})

        return synthetic if synthetic else rows

    def _claim_passes_precision_gate(self, claim: Dict[str, Any]) -> bool:
        """Precision-first gate from Doc71: reject forced/ambiguous matches."""
        iv = str(claim.get("iv") or "").strip().lower()
        dv = str(claim.get("dv") or "").strip().lower()
        if not iv or not dv:
            return False
        if iv == dv:
            return False

        iv_conf = claim.get("iv_confidence")
        dv_conf = claim.get("dv_confidence")
        iv_conf_val = float(iv_conf) if iv_conf is not None else 0.0
        dv_conf_val = float(dv_conf) if dv_conf is not None else 0.0
        if iv_conf_val < 0.4 or dv_conf_val < 0.4:
            return False
        if iv_conf_val < 0.5 and dv_conf_val < 0.5:
            return False
        if max(iv_conf_val, dv_conf_val) < 0.6 and claim.get("effect_size") is None and claim.get("p_value") is None:
            return False

        quote = str(claim.get("source_quote") or "")
        if not self._ocr_quality_check(quote)["clean"] and claim.get("effect_size") is None:
            return False
        return True

    def _write_structured_output(self, output_path: str | None = None) -> None:
        """Emit D10-style structured_claims JSON in addition to JSONL stream output."""
        output_path = output_path or self.structured_output_path
        summary = {
            "extraction_date": datetime.now().isoformat(),
            "method": self.method,
            "papers_processed": self.stats["processed"],
            "claims_extracted": self.stats["claims_extracted"],
            "claims_kept": self.stats["claims_kept"],
            "errors": self.stats["errors"],
            "tables_skipped_ocr": self.stats["tables_skipped_ocr"],
            "tables_skipped_semantic": self.stats["tables_skipped_semantic"],
            "tables_transformed_matrix": self.stats["tables_transformed_matrix"],
            "tables_transformed_stepwise": self.stats["tables_transformed_stepwise"],
            "claims_with_effect_size": sum(1 for c in self._all_kept_claims if c.get("effect_size") is not None),
            "claims_with_sample_n": sum(1 for c in self._all_kept_claims if c.get("sample_n") is not None),
            "claims": self._all_kept_claims,
        }
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=True)

    def _is_statistical_table(self, table: Dict[str, Any]) -> bool:
        """
        Check if a table contains extractable statistical content using Codex semantic profiling.
        """
        profile = build_table_content_profile(table)
        return profile.get('extractable', False)

    def run(self):
        if not extract_claims_from_paper:
            print("CRITICAL: ClaimExtractor module not available. Aborting.")
            return

        self.load_data()
        targets = self.get_target_papers()
        
        if not targets:
            print("No targets found.")
            return

        print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting batch extraction...")
        
        # Open in append mode? Or write? For a "run", let's clear if it's a fresh start, 
        # but here we'll use 'w' to ensure clean pilot results.
        mode = 'w'
        
        with open(OUTPUT_PATH, mode) as f_out:
            for pid in targets:
                try:
                    print(f"Processing {pid}...", end="", flush=True)
                    
                    tables = self.table_data.get(pid, [])
                    metadata = self.metadata_lookup.get(pid, {})
                    
                    if not tables:
                        print(" Skipped (No tables loaded)")
                        self.stats['skipped'] += 1
                        continue

                    # Enrich tables with reconstructed content if available
                    enriched_tables = []
                    for tbl in tables:
                        tid = tbl.get('table_id')
                        if pid in self.reconstructed_tables and tid and tid in self.reconstructed_tables[pid]:
                            csv_rows = self.reconstructed_tables[pid][tid]
                            # Clean and reconstruct
                            clean_rows = [self._clean_ocr_text(r) for r in csv_rows]
                            
                            # Override or add 'rows' with high-quality CSV data
                            tbl['rows'] = [{"text": r, "source_quote": r} for r in clean_rows]
                            tbl['source_type'] = 'csv_reconstruction'

                        if not self._table_passes_ocr_gate(tbl):
                            self.stats["tables_skipped_ocr"] += 1
                            continue

                        # Filter for statistical content
                        if not self._is_statistical_table(tbl):
                            self.stats["tables_skipped_semantic"] += 1
                            continue

                        # Table-type aware transformations to improve parsing.
                        if self._looks_like_correlation_matrix(tbl):
                            tbl["rows"] = self._transform_correlation_matrix(tbl)
                            self.stats["tables_transformed_matrix"] += 1
                        elif self._looks_like_stepwise_regression(tbl):
                            tbl["rows"] = self._transform_stepwise_regression(tbl, metadata)
                            self.stats["tables_transformed_stepwise"] += 1

                        enriched_tables.append(tbl)
                    
                    if not enriched_tables:
                        print(" Skipped (No statistical tables found)")
                        self.stats['skipped'] += 1
                        continue
                        
                    print(f" (Tables: {len(enriched_tables)}/{len(tables)})", end="", flush=True)

                    # Call D.6 Engine
                    # We pass the method (llm or rule_based)
                    if self.method == "llm":
                        # Lazy init service
                        if not hasattr(self, "llm_service"):
                            from src.extraction.llm_extraction_service import LLMExtractionService
                            model_id = getattr(self, "model_id", "gpt-4o")
                            print(f"[{datetime.now().strftime('%H:%M:%S')}] Initializing LLM Service with model: {model_id}")
                            self.llm_service = LLMExtractionService(model_id)

                        claims = []
                        for table in enriched_tables:
                            # Construct context
                            table_text = f"Table {table.get('table_id')}:\n" + "\n".join(r.get("text") or "" for r in table.get("rows", []))
                            extracted = self.llm_service.extract_claims_from_text(table_text)
                            
                            for c in extracted:
                                c['paper_id'] = pid
                                c['source_table_id'] = table.get('table_id')
                                c['extraction_confidence'] = float(c.get('confidence', 0.5))
                                c['extraction_method'] = f"llm_{getattr(self, 'model_id', 'unknown')}"
                                # Generate ID if missing
                                if 'claim_id' not in c:
                                    import uuid
                                    c['claim_id'] = f"{pid}_{str(uuid.uuid4())[:8]}"
                                claims.append(c)

                    else:
                        # Standard rule-based path
                        claims = extract_claims_from_paper(
                            paper_id=pid,
                            tables=enriched_tables,
                            paper_context=metadata,
                            vocabulary=None, # Use default
                            method=self.method
                        )
                    
                    if claims:
                        kept_claims = [c for c in claims if self._claim_passes_precision_gate(c)]
                        rejected = len(claims) - len(kept_claims)

                        # Write each claim as a JSONL line
                        for claim in kept_claims:
                            # Add metadata identifying this batch run
                            claim['batch_id'] = "batch_15_pilot"
                            claim['processed_at'] = datetime.now().isoformat()
                            
                            f_out.write(json.dumps(claim) + "\n")
                            self._all_kept_claims.append(claim)
                        
                        count = len(claims)
                        kept = len(kept_claims)
                        print(f" Extracted {count} claims ({kept} kept, {rejected} rejected).")
                        self.stats['claims_extracted'] += count
                        self.stats['claims_kept'] += kept
                    else:
                        print(" No claims found.")
                    
                    self.stats['processed'] += 1
                    
                    # Rate limiting for LLM
                    if self.method == "llm" and not self.dry_run:
                        time.sleep(1.0) 

                except Exception as e:
                    print(f" ERROR: {e}")
                    self.stats['errors'] += 1
                    import traceback
                    traceback.print_exc()

        print("\nBatch Processing Complete.")
        print(f"Papers Processed: {self.stats['processed']}")
        print(f"Total Claims Extracted: {self.stats['claims_extracted']}")
        print(f"Claims Kept (precision gate): {self.stats['claims_kept']}")
        print(f"Errors: {self.stats['errors']}")
        print(f"Results saved to {OUTPUT_PATH}")
        self._write_structured_output()
        print(f"Structured output saved to {self.structured_output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run batch extraction (Sprint D.10).")
    parser.add_argument("--limit", type=int, help="Limit number of papers to process (e.g. 5 for pilot)")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode (no API calls)")
    parser.add_argument("--method", choices=["llm", "rule_based"], default="rule_based", help="Extraction method (default: rule_based for safety)")
    parser.add_argument("--model", default="gpt-4o", help="LLM model ID if method=llm (e.g. gpt-4o, claude-sonnet)")
    parser.add_argument("--structured-output", default=STRUCTURED_OUTPUT_PATH, help="Path to combined structured claims JSON")
    
    args = parser.parse_args()
    
    processor = BatchProcessor(
        limit=args.limit,
        method=args.method,
        structured_output_path=args.structured_output,
    )
    # Inject model choice if LLM method selected (hacky but works for now without big refactor)
    if args.method == "llm":
        processor.model_id = args.model
        
    processor.run()
