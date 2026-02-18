# PDF Data Quality Report
**Date:** February 17, 2026
**Subject:** Quality Inspection of `realtime_pdf_confirmed_rows.csv`

## Executive Summary
A structural inspection of the "confirmed" PDF extraction dataset reveals a significant quality gap. While the system has successfully ingested a massive volume of text from PDFs (**171,840 rows**), the vast majority (**92.8%**) lack structured causal variables.

The dataset is effectively a **"Sentence Interest Store"**, not a **"Causal Table Store."**

## 1. Dataset Statistics
- **Source File:** `data/production/realtime_pdf_confirmed_rows.csv` (154 MB)
- **Total Rows:** 171,840
- **Unique Papers:** 386 (Average ~445 rows per paper)
- **Provenance:** 100% marked as `pdf_confirmed`

## 2. Structural Integrity
We analyzed the fill rates of critical columns required for causal reasoning:

| Column | Fill Rate | Count | Implication |
| :--- | :--- | :--- | :--- |
| **Statement** (Text) | **100.0%** | 171,840 | We have the raw assertions. |
| **Source Quote** | **100.0%** | 171,840 | Excellent traceability to source text. |
| **Environment Variable** | **7.2%** | 12,384 | **CRITICAL GAP**: Only ~12k rows are structured IVs. |
| **Outcome Variable** | **7.2%** | 12,384 | **CRITICAL GAP**: Only ~12k rows are structured DVs. |
| **Evidence Basis** | 45.1% | 77,468 | nearly half have some evidence type coded. |
| **Strength Hint** | 100.0% | 171,840 | Mostly low confidence (0.35–0.40). |

## 3. Findings

### Finding 1: High Recall, Low Structure
The extraction pipeline appears to be operating in a "High Recall" mode, grabbing every sentence that *might* be relevant (hence 445 rows/paper), rather than extracting only structured tables.

### Finding 2: The "7%" Gold Standard
Only **12,384 rows** contain the structural triplets (`Environment` -> `Outcome`) necessary for the Bayesian Network and Causal Graph to function automatically. The remaining **159,456 rows** are currently unstructured context.

### Finding 3: Traceability is High
The 100% coverage of `source_quote` means we can always audit *where* a claim came from, even if we don't know *what* variables it connects.

## 4. Recommendations for Sprint 13+

1.  **Filter for Graphing**: When building the Causal Graph, apply a strict filter `WHERE environment_variable IS NOT NULL`. Do not pollute the graph with the 92% unstructured rows.
2.  **Reprocess for Structure**: The 159k unstructured rows are a prime candidate for a secondary LLM pass ("Structure Extraction") to convert the `statement` text into `iv/dv` pairs.
3.  **Update Metrics**: Stop reporting "171k confirmed claims." Start reporting "**12k structured causal links** and 159k supporting statements."
