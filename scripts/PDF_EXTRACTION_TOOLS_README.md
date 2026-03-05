# PDF Extraction Tools

Two complementary tools for enriching article extractions with data from full PDFs.

## Scripts

### 1. `build_pdf_doi_mapping.py`

**Purpose**: Create a mapping from extraction DOIs to their corresponding PDF files.

**Status**: ✅ Complete and tested (100% coverage: 1,069/1,069 DOIs mapped)

**Usage**:
```bash
python3 scripts/build_pdf_doi_mapping.py                # Create mapping
python3 scripts/build_pdf_doi_mapping.py --dry-run      # Preview only
python3 scripts/build_pdf_doi_mapping.py --verbose      # Debug output
```

**Output**: `data/pdf_doi_mapping.json`

**Details**:
- Scans Zotero files (1,318 PDFs), HBE export (913 PDFs), All_PDFs (423 PDFs)
- Parses bib files for DOI→file associations
- Deduplicates (prefers Zotero main > HBE > All_PDFs)
- Reports coverage metrics
- No external BibTeX parser needed (uses regex)

**Coverage Report** (2026-03-05):
```
Total extractions:     1069
Mapped:                1069
Missing:               0
Coverage:              100.0%
```

---

### 2. `reextract_from_pdfs.py`

**Purpose**: Use Gemini 2.5 Flash multimodal to fill in empty fields in extractions.

**Status**: ✅ Complete (ready for David's local machine)

**Requirements**:
- `google-generativeai` installed (`pip install google-generativeai`)
- Gemini API key set (`export GEMINI_API_KEY="..."`)
- Python 3.9+

**Usage**:
```bash
# Dry run (no API calls)
python3 scripts/reextract_from_pdfs.py --limit 5 --dry-run

# Extract 10 papers
python3 scripts/reextract_from_pdfs.py --limit 10

# Full batch with 4 workers
python3 scripts/reextract_from_pdfs.py --parallel 4

# Resume from progress file
python3 scripts/reextract_from_pdfs.py --parallel 4 --resume

# Extract one specific DOI
python3 scripts/reextract_from_pdfs.py --doi 10.1016/j.example.2022.001

# Adjust Zotero base path for your machine
python3 scripts/reextract_from_pdfs.py \
  --zotero-base /Users/davidusa/Zotero/storage \
  --parallel 4
```

**Target Fields**:
1. `effect_size` / `effect_size_unit` — quantitative effect magnitude
2. `sample_size` — study N
3. `stimulus_description` — detailed stimuli/exposure descriptions
4. `methodology` — research design summary
5. `figure_references` — figure numbers + captions
6. `limitations` — acknowledged limitations
7. `author_affiliations` — institution/country info

**Options**:
```
--pdf-mapping PATH       Path to mapping JSON (default: data/pdf_doi_mapping.json)
--zotero-base PATH       Zotero base path for your system (remap paths)
--limit N                Limit to first N DOIs (0 = all)
--doi STRING             Extract only this DOI
--parallel N             Number of workers (default: 1)
--dry-run               Don't modify files
--resume                Pick up from progress file
--verbose               Debug logging
```

**Output**:
- Updated extraction JSONs with new fields filled
- Progress tracking in `data/reextraction_progress.json`
- Metadata: `reextraction_at`, `reextraction_model`, `reextraction_fields`

**Merge Strategy** (conservative):
- Never overwrites existing good data
- Only fills empty/missing fields
- Safe to rerun multiple times

**Estimated Costs**:
- Per paper: $0.01-0.05 USD
- 1,069 papers: $10-50 total
- Time: 2-3 hours (4 workers) or 30 min (8 workers)

---

## Getting Started

### Step 1: Generate Mapping (One Time)

```bash
# In the sandbox, this is already done
python3 scripts/build_pdf_doi_mapping.py

# Output: data/pdf_doi_mapping.json (100% coverage, 1,069 DOIs)
```

### Step 2: Run Reextraction on Your Local Machine

On your local machine with Gemini API access:

```bash
# 1. Get Gemini API key from Google AI Studio
#    https://aistudio.google.com/app/apikey

# 2. Set environment variable
export GEMINI_API_KEY="your-key-here"

# 3. Find your Zotero base path
ls ~/Zotero/storage | head
# Expected output: 12345, 12346, ... (numbered folders)

# 4. Try a dry run first
python3 scripts/reextract_from_pdfs.py \
  --zotero-base ~/Zotero/storage \
  --limit 5 \
  --dry-run

# 5. Extract a test batch
python3 scripts/reextract_from_pdfs.py \
  --zotero-base ~/Zotero/storage \
  --limit 10

# 6. Check progress
cat data/reextraction_progress.json | python3 -m json.tool | head

# 7. Run full batch
python3 scripts/reextract_from_pdfs.py \
  --zotero-base ~/Zotero/storage \
  --parallel 4
```

### Step 3: Integration (Optional)

After reextraction, re-integrate improved extractions into the Web of Belief:

```python
from src.web_of_belief import WebOfBelief
from src.services.extraction_to_web import ExtractionToWebIntegrator
import json
from pathlib import Path

web = WebOfBelief()
integrator = ExtractionToWebIntegrator(web)

# Integrate all reextracted papers
for json_file in Path('data/extractions').glob('*.json'):
    extraction = json.load(open(json_file))
    if 'reextraction_at' in extraction:
        integrator.integrate_extraction(extraction)
```

---

## Documentation

- **Full Guide**: `docs/PDF_REEXTRACTION_GUIDE.md`
- **Completion Report**: `docs/PDF_EXTRACTION_TOOLS_COMPLETION_2026-03-05.md`

---

## Troubleshooting

### "PDF not found"
- Check `--zotero-base` path is correct
- Verify `data/pdf_doi_mapping.json` has correct paths for your system

### "GEMINI_API_KEY not set"
- Run: `export GEMINI_API_KEY="your-key-here"`
- Verify with: `echo $GEMINI_API_KEY`

### "google-generativeai not installed"
- Run: `pip install google-generativeai`

### Script interrupted
- Use `--resume` flag to pick up where it left off
- Progress file: `data/reextraction_progress.json`

---

## Performance Notes

- **Network-bound**: More workers (4-8) recommended
- **Timeout**: 60 seconds per PDF (configurable)
- **Rate limit**: Respects Gemini API quotas
- **Progress**: Checkpoint every 5-10 completed tasks

---

## Quality Assurance

✅ Mapping: 100% coverage (1,069/1,069)
✅ Merge: Conservative (never overwrites)
✅ Safety: Progress tracking & resume support
✅ Error handling: PDFs, timeouts, API failures

---

## Author

Claude AI Assistant, 2026-03-05

For detailed documentation, see:
- `docs/PDF_REEXTRACTION_GUIDE.md`
- `docs/PDF_EXTRACTION_TOOLS_COMPLETION_2026-03-05.md`
