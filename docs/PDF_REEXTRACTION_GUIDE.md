# PDF Reextraction Guide

**Purpose**: Use Gemini 2.5 Flash multimodal to fill in empty/weak fields in 1,069 existing article extractions by analyzing the full PDFs.

**Target Fields to Fill**:
- `effect_size` and `effect_size_unit`
- `sample_size`
- `stimulus_description`
- `methodology` (detailed research design)
- `figure_references`
- `limitations`
- `author_affiliations`

---

## Prerequisites (Local Machine Only)

This reextraction MUST run on your local machine, not the sandbox, because Gemini API is blocked in sandboxes.

### 1. Python & Dependencies

```bash
# Ensure Python 3.9+
python3 --version

# Install Gemini SDK
pip install google-generativeai
```

### 2. Gemini API Key

Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey):

```bash
# Save your key as an environment variable
export GEMINI_API_KEY="your-key-here"

# Or create ~/.gemini_key and source it
echo "export GEMINI_API_KEY='your-key-here'" >> ~/.gemini_key
source ~/.gemini_key
```

### 3. PDF Mapping File

The script `scripts/build_pdf_doi_mapping.py` creates `data/pdf_doi_mapping.json`, which maps each of the 1,069 extraction DOIs to their corresponding PDF file path. This file was already created in the sandbox:

```bash
# File already exists at:
# Article_Eater_PostQuinean_v1/data/pdf_doi_mapping.json

# Contains 1,069 DOI → absolute PDF path mappings
# All PDFs found and mapped with 100% coverage
```

---

## Workflow

### Step 1: Copy the Repository to Your Local Machine

```bash
# Clone or sync the Article_Eater_PostQuinean_v1 repo
# Make sure you have:
# - scripts/reextract_from_pdfs.py
# - data/pdf_doi_mapping.json (created in sandbox)
# - data/extractions/*.json (all 1,069 existing extractions)
```

### Step 2: Configure Zotero Base Path

The PDF paths in `pdf_doi_mapping.json` are absolute paths from the sandbox. On your local machine, the Zotero directory structure may be different.

When you run the script, tell it where YOUR Zotero files are:

```bash
# Find your Zotero storage root
# Usually: /Users/YourName/Zotero/storage
# Or: /home/username/Zotero/storage
# Or: custom path you set in Zotero preferences

# Then run:
python3 scripts/reextract_from_pdfs.py \
  --zotero-base /Users/davidusa/Zotero/storage
```

**How it works**: The script will remap all PDF paths from the sandbox paths to your local paths automatically.

### Step 3: Try a Dry Run First

```bash
# See what would be reextracted (no API calls, no file changes)
python3 scripts/reextract_from_pdfs.py \
  --zotero-base /Users/davidusa/Zotero/storage \
  --limit 5 \
  --dry-run
```

Expected output:
```
[REEXTRACT] INFO ======================================================================
[REEXTRACT] INFO PDF Reextraction Pipeline (Gemini 2.5 Flash Multimodal)
[REEXTRACT] INFO ======================================================================
[REEXTRACT] INFO 📂 Loading PDF mapping from data/pdf_doi_mapping.json...
[REEXTRACT] INFO   Found mappings for 1069 DOIs
[REEXTRACT] INFO 🔄 Preparing to reextract 5 DOI(s)
[REEXTRACT] INFO 🤖 Initializing Gemini 2.5 Flash...
```

### Step 4: Run on a Small Batch First

```bash
# Extract 10 papers to test the process
python3 scripts/reextract_from_pdfs.py \
  --zotero-base /Users/davidusa/Zotero/storage \
  --limit 10
```

This will:
1. Load the first 10 DOIs from the mapping
2. Find their PDFs
3. Call Gemini 2.5 Flash for each PDF
4. Extract missing fields
5. Merge results back into `data/extractions/{DOI}.json`
6. Save progress to `data/reextraction_progress.json`

### Step 5: Check Progress and Results

```bash
# View progress
cat data/reextraction_progress.json | python3 -m json.tool | head -50

# Check a specific reextracted file
python3 << 'EOF'
import json

# Look at a reextracted extraction
with open("data/extractions/10.1002_ad.2031.json") as f:
    data = json.load(f)

# Check if new fields were added
print("Reextraction metadata:")
print(f"  reextraction_at: {data.get('reextraction_at')}")
print(f"  Fields filled: {data.get('reextraction_fields', [])}")
EOF
```

### Step 6: Run Full Batch

Once satisfied with a small batch, run the full reextraction:

```bash
# Full reextraction with 4 parallel workers
python3 scripts/reextract_from_pdfs.py \
  --zotero-base /Users/davidusa/Zotero/storage \
  --parallel 4

# Or resume a previous run
python3 scripts/reextract_from_pdfs.py \
  --zotero-base /Users/davidusa/Zotero/storage \
  --parallel 4 \
  --resume
```

---

## Command Reference

### `reextract_from_pdfs.py` Options

```bash
python3 scripts/reextract_from_pdfs.py [OPTIONS]

Options:
  --pdf-mapping PATH
      Path to PDF-DOI mapping JSON
      Default: data/pdf_doi_mapping.json

  --zotero-base PATH
      Base path for Zotero files (e.g., /Users/you/Zotero/storage)
      Use this to remap paths to your local system

  --limit N
      Limit reextraction to first N DOIs (0 = all)
      Default: 0

  --doi STRING
      Reextract only this specific DOI
      Example: --doi 10.1002/ad.2031

  --parallel N
      Number of parallel workers (1-8 recommended)
      Default: 1

  --dry-run
      Show what would be reextracted, don't modify files

  --resume
      Resume from progress file (data/reextraction_progress.json)

  --verbose
      Enable debug logging
```

### Usage Examples

```bash
# Dry run on 5 papers
python3 scripts/reextract_from_pdfs.py --limit 5 --dry-run

# Extract specific paper
python3 scripts/reextract_from_pdfs.py \
  --doi 10.1016/j.cognition.2022.105273

# Full batch with 4 workers, resumable
python3 scripts/reextract_from_pdfs.py \
  --parallel 4 \
  --resume

# Full batch, with all outputs
python3 scripts/reextract_from_pdfs.py \
  --parallel 4 \
  --verbose > reextraction_log.txt 2>&1
```

---

## Merge Strategy (Never Overwrites)

The script uses a conservative merge strategy:

```
For each field (effect_size, sample_size, etc.):
  IF (existing field is empty or missing) AND (Gemini found something):
    THEN: Use Gemini's result
  ELSE:
    KEEP existing value (never overwrite good data)
```

This ensures:
- Existing high-quality extractions are never downgraded
- Only gaps are filled
- You can safely rerun multiple times without data loss

---

## Output Structure

After reextraction, each extraction JSON will have:

```json
{
  "doi": "10.1002/ad.2031",
  "title": "...",
  "effect_size": "0.42",                    ← filled if empty
  "sample_size": 120,                       ← filled if empty
  "stimulus_description": "...",            ← filled if empty
  "methodology": "...",                     ← filled if empty
  "figure_references": [...],               ← filled if empty
  "limitations": [...],                     ← filled if empty
  "author_affiliations": [...],             ← filled if empty

  // Metadata tracking reextraction
  "reextraction_at": "2026-03-05T...",
  "reextraction_model": "gemini-2.5-flash",
  "reextraction_fields": ["effect_size", "sample_size", ...],

  // All existing fields preserved
  "findings": [...],
  "theory_links": [...]
}
```

---

## Monitoring & Troubleshooting

### Check Progress

```bash
# View completed/failed tasks
python3 << 'EOF'
import json
with open("data/reextraction_progress.json") as f:
    progress = json.load(f)

completed = len(progress.get("completed_tasks", []))
failed = len(progress.get("failed_dois", []))
print(f"Completed: {completed}")
print(f"Failed: {failed}")
print(f"Success rate: {100*completed/(completed+failed):.1f}%")

# Show first failure
if progress.get("failed_dois"):
    print(f"\nFirst failed DOI: {progress['failed_dois'][0]}")
EOF
```

### Common Issues

#### "PDF not found"
- **Cause**: --zotero-base path is wrong
- **Fix**: Check actual Zotero path, e.g., `ls /Users/you/Zotero/storage/ | head`

#### "GEMINI_API_KEY not set"
- **Cause**: Environment variable not exported
- **Fix**: `export GEMINI_API_KEY="..."` before running

#### "google-generativeai not installed"
- **Cause**: Gemini SDK not installed
- **Fix**: `pip install google-generativeai`

#### "Failed to parse Gemini response"
- **Cause**: Model returned non-JSON response
- **Fix**: Gemini may have rate-limited. Retry with --resume

### Resume from Failure

```bash
# If the script crashes, pick up where it left off
python3 scripts/reextract_from_pdfs.py \
  --zotero-base /Users/davidusa/Zotero/storage \
  --parallel 4 \
  --resume
```

The script skips already-completed DOIs automatically.

---

## Performance & Costs

### Estimated Costs

- **Per PDF**: ~$0.01-0.05 USD (Gemini 2.5 Flash is cheap)
- **1,069 papers**: ~$10-50 total
- **Time**: ~2-3 hours with 4 parallel workers (~30 min with 8 workers)

### Optimization Tips

```bash
# Use more workers to parallelize (network I/O bound)
python3 scripts/reextract_from_pdfs.py --parallel 8

# Or batch in smaller chunks to avoid timeouts
for i in {0..10}; do
  python3 scripts/reextract_from_pdfs.py --limit 100 --resume
done
```

---

## Integration with Web of Belief

After reextraction, the improved extractions can be re-integrated into the Web of Belief:

```bash
# In the Article_Eater environment, run:
python3 scripts/auto_ingest_pdfs.py --skip-integration

# Then integrate the improved extractions:
python3 -c "
from src.web_of_belief import WebOfBelief
from src.services.extraction_to_web import ExtractionToWebIntegrator
import json
from pathlib import Path

web = WebOfBelief()
integrator = ExtractionToWebIntegrator(web)

# Integrate all reextracted papers
for json_file in Path('data/extractions').glob('*.json'):
    if 'reextraction_at' in json.load(open(json_file)):
        extraction = json.load(open(json_file))
        integrator.integrate_extraction(extraction)
        print(f'Integrated {extraction[\"doi\"]}')
"
```

---

## Questions or Issues?

Check the progress file for details:

```bash
cat data/reextraction_progress.json | python3 -m json.tool
```

---

**Last Updated**: 2026-03-05
**Author**: Claude AI Assistant
**Gemini Model**: gemini-2.5-flash (multimodal)
