# SPRINT D PROGRESS CHECK + MAPPING PRECISION ANALYSIS
## Document 71 — February 18, 2026

---

## PART 1: STATS TO RERUN NOW

Run these inside the repo. Each is a specific command or short script. Together they tell us: which Sprint D tasks landed, what the current extraction quality is, and whether the vocabulary bridge is working.

---

### Check 1: Sprint D Completion Status

```bash
cat docs/DONE.md | grep "^D\."
```

**Why:** Shows which D.x tasks have been marked complete and by whom. The entire diagnosis depends on where we are.

---

### Check 2: Vocabulary Sheet Existence and Coverage

```bash
# Does the vocabulary exist?
ls -la data/vocabulary/variable_vocabulary.json

# If it exists, how many IVs and DVs?
python3 -c "
import json
v = json.load(open('data/vocabulary/variable_vocabulary.json'))
ivs = v.get('independent_variables', {})
dvs = v.get('dependent_variables', {})
print(f'IVs: {len(ivs)}')
print(f'DVs: {len(dvs)}')
total_syn = sum(len(x.get('synonyms',[])) for x in ivs.values())
total_syn += sum(len(x.get('synonyms',[])) for x in dvs.values())
print(f'Total synonyms: {total_syn}')
print(f'IV names: {sorted(ivs.keys())}')
print(f'DV names: {sorted(dvs.keys())}')
"
```

**Why:** D.1 is the foundation. If the vocabulary has 15 IVs with 5 synonyms each, that's 75 entry points. If it has 30 IVs with 20 synonyms each, that's 600. The mapping precision is DIRECTLY proportional to vocabulary coverage.

---

### Check 3: Paper Triage Results

```bash
# Does triage exist?
ls -la data/production/paper_triage.json

# If yes, distribution
python3 -c "
import json
t = json.load(open('data/production/paper_triage.json'))
if isinstance(t, list):
    from collections import Counter
    types = Counter(p.get('type') or p.get('article_type','unknown') for p in t)
else:
    types = {}
    for pid, info in t.items():
        tp = info.get('type') or info.get('article_type','unknown')
        types[tp] = types.get(tp, 0) + 1
print('Paper triage distribution:')
for k, v in sorted(types.items(), key=lambda x: -x[1]):
    print(f'  {k}: {v}')
print(f'Total: {sum(types.values())}')
"
```

**Why:** D.2 filters 386 papers down to the extractable ones. If triage classified 200 as empirical/review, we have a large extraction target. If only 40, the corpus may be sparser than we assumed.

---

### Check 4: Table Classification Results

```bash
ls -la data/production/table_classifications.json

python3 -c "
import json
t = json.load(open('data/production/table_classifications.json'))
from collections import Counter
types = Counter()
extractable = 0
garbage = 0
for tid, info in t.items():
    tp = info.get('type', 'unknown')
    types[tp] += 1
    if info.get('extractable'): extractable += 1
    if tp in ('GARBAGE','OTHER'): garbage += 1
print(f'Total tables classified: {len(t)}')
print(f'Extractable: {extractable}')
print(f'Garbage/Other: {garbage}')
print()
for k,v in sorted(types.items(), key=lambda x: -x[1]):
    print(f'  {k}: {v}')
"
```

**Why:** D.3 is the critical filter. If 80% of tables are classified GARBAGE or DEMOGRAPHICS, only 20% feed the extraction engine. That's fine — we want precision over recall.

---

### Check 5: Structured Claims Output

```bash
ls -la data/production/structured_claims.json

python3 -c "
import json
c = json.load(open('data/production/structured_claims.json'))
claims = c.get('claims', c if isinstance(c, list) else [])
print(f'Total claims: {len(claims)}')
mapped = sum(1 for x in claims if x.get('vocabulary_mapped') or (x.get('iv_mapped') and x.get('dv_mapped')))
has_es = sum(1 for x in claims if x.get('effect_size') is not None)
has_n = sum(1 for x in claims if x.get('sample_n') is not None)
print(f'Vocabulary-mapped (both IV+DV): {mapped} ({100*mapped/max(len(claims),1):.1f}%)')
print(f'Has effect size: {has_es} ({100*has_es/max(len(claims),1):.1f}%)')
print(f'Has sample N: {has_n} ({100*has_n/max(len(claims),1):.1f}%)')
# Top IVs
from collections import Counter
ivs = Counter(x.get('iv','?') for x in claims)
dvs = Counter(x.get('dv','?') for x in claims)
print(f'\\nTop 15 IVs:')
for k,v in ivs.most_common(15): print(f'  {k}: {v}')
print(f'\\nTop 15 DVs:')
for k,v in dvs.most_common(15): print(f'  {k}: {v}')
"
```

**Why:** This is THE number. If structured_claims.json has 500+ claims with real IVs and DVs from the vocabulary, Sprint D is working. If it has 50 claims or the top IVs are still garbage strings, the extraction engine needs debugging.

---

### Check 6: Gold Standard Match Rate

```bash
python3 -c "
import json, os, glob

# Load gold standard
gold_dir = 'data/gold_standard/'
gold_claims = 0
gold_papers = 0
for f in glob.glob(os.path.join(gold_dir, '*.json')):
    g = json.load(open(f))
    n = len(g.get('claims', []))
    gold_claims += n
    gold_papers += 1

# Load extractions if they exist
ext_path = 'data/production/structured_claims.json'
ext_claims = 0
if os.path.exists(ext_path):
    c = json.load(open(ext_path))
    claims = c.get('claims', c if isinstance(c, list) else [])
    ext_claims = len(claims)

print(f'Gold standard: {gold_papers} papers, {gold_claims} claims')
print(f'Extracted: {ext_claims} claims')
print()

# If extraction validation report exists
val_path = 'docs/extraction_validation_report.md'
if os.path.exists(val_path):
    print(open(val_path).read()[:500])
"
```

**Why:** The extraction_validation_report.md you uploaded showed 0/139 matched. If this number has moved AT ALL, that's progress.

---

### Check 7: Web of Belief V2 Status

```bash
# Does v2 exist?
ls -la data/web_persistence_v2.db 2>/dev/null || echo "V2 web not yet created"

# If yes, compare
python3 -c "
import sqlite3

for db, label in [('data/web_persistence.db','V1 (old)'), ('data/web_persistence_v2.db','V2 (new)')]:
    try:
        conn = sqlite3.connect(db)
        beliefs = conn.execute('SELECT COUNT(*) FROM beliefs').fetchone()[0]
        constraints = conn.execute('SELECT COUNT(*) FROM constraints').fetchone()[0]
        unresolved = conn.execute(\"SELECT COUNT(*) FROM beliefs WHERE environment_id LIKE 'env.unresolved%'\").fetchone()[0]
        coherence = conn.execute('SELECT coherence_score FROM web_metadata LIMIT 1').fetchone()
        coh = coherence[0] if coherence else 'N/A'
        print(f'{label}: {beliefs} beliefs, {constraints} constraints, {unresolved} unresolved ({100*unresolved/max(beliefs,1):.1f}%), coherence={coh}')
        conn.close()
    except Exception as e:
        print(f'{label}: {e}')
"
```

**Why:** The whole point of Sprint D is to replace garbage beliefs with real ones. If V2 exists and has 2,000 beliefs with 5% unresolved instead of 12,628 with 90% unresolved, we've won.

---

### Check 8: CMR Pipeline on Clean Claims

```bash
# Does the integration report exist?
ls -la data/production/cmr_integration_report.json 2>/dev/null

# Quick smoke test: feed one gold-standard claim through
python3 -c "
from src.cmr.process_paper import process_paper
result = process_paper(
    claims=[
        {'iv': 'has_nature_view', 'dv': 'recovery_time', 'direction': 'decrease',
         'effect_size': 0.71, 'sample_n': 46, 'description': 'Nature view reduces surgical recovery time'},
        {'iv': 'has_nature_view', 'dv': 'pain_medication_use', 'direction': 'decrease',
         'effect_size': 0.50, 'sample_n': 46, 'description': 'Nature view reduces analgesic doses'}
    ],
    citation='Ulrich (1984)',
    doi='10.1126/science.6143402'
)
print(f'Claims extracted: {result.n_claims}')
print(f'Claims matched: {result.n_matched}')
print(f'Contradictions: {result.n_contradictions}')
print(f'Confirmations: {result.n_confirmations}')
print(f'Templates matched: {result.matched_template_ids}')
print(f'Proposals: {result.proposals_generated}')
" 2>&1 | head -30
```

**Why:** This verifies the LEFT half (pipeline) still works on clean input. If Ulrich matches VIEW1 and produces sensible proposals, the pipeline is healthy. The question is whether Sprint D's extraction can produce inputs of this quality from raw PDFs.

---

## PART 2: WHY THE MAPPING PRECISION IS SO BAD — AND HOW TO FIX IT

The extraction_validation_report shows 0.00 precision, 0.00 recall. The full_csv_audit shows the "best" variable pairs are things like `social → social` and `wood → wood`. This isn't a tuning problem. It's an architectural problem. There are five distinct failure modes, each requiring a different fix.

---

### Failure Mode 1: Table Structure Blindness

**What happens:** pdfplumber extracts a table like:

```
| Variable | B    | SE   | β     | t    | p    |
|----------|------|------|-------|------|------|
| Ceiling  | 0.34 | 0.12 | 0.28  | 2.83 | .005 |
| Noise    |-0.21 | 0.09 |-0.19  |-2.33 | .02  |
| Daylight | 0.45 | 0.14 | 0.31  | 3.21 | .001 |
```

The extractor sees cell pairs and produces:
```
environment_variable: "ceiling"
outcome_variable: "ceiling"     # ← Same cell! IV = DV
```

or worse:
```
environment_variable: "0.34"    # ← a regression coefficient
outcome_variable: "0.12"       # ← a standard error
```

**Why it happens:** The extractor doesn't know which column is which. It doesn't know that in a regression table, column 1 = variable names (IVs), the DV is in the table CAPTION (not in the table at all), and columns 2-6 are statistics ABOUT the relationship, not variables.

**Fix: Table-Type-Aware Extraction Templates**

Instead of one extraction algorithm for all tables, define extraction TEMPLATES for each table type:

```python
EXTRACTION_TEMPLATES = {
    "regression": {
        "iv_location": "first_column",
        "dv_location": "caption",  # The DV is almost never IN a regression table
        "effect_column": "β or B",
        "significance_column": "p",
        "direction_rule": "sign of β"
    },
    "correlation_matrix": {
        "iv_location": "row_headers",
        "dv_location": "column_headers",
        "effect_column": "cell_value",  # The cell IS the effect size (r)
        "significance_column": "stars_or_note",
        "direction_rule": "sign of r"
    },
    "anova": {
        "iv_location": "source_column",
        "dv_location": "caption",
        "effect_column": "F or η²",
        "significance_column": "p",
        "direction_rule": "requires_post_hoc"  # ANOVA F-test doesn't give direction
    },
    "descriptive_by_condition": {
        "iv_location": "condition_column",
        "dv_location": "header_row",
        "effect_column": "computed_from_means",  # Must calculate d from M1, M2, SD
        "significance_column": "separate_test_table",
        "direction_rule": "M1 > M2 or M1 < M2"
    },
    "literature_review": {
        "iv_location": "varies_by_row",  # Each row is a different study
        "dv_location": "varies_by_row",
        "effect_column": "findings_column",
        "significance_column": "varies",
        "direction_rule": "parse_findings_text"
    }
}
```

The table classifier (D.3) identifies the type. Then the extraction engine (D.6) uses the matching template to know WHERE to find the IV, DV, and effect in each table type. This is the single highest-impact change.

---

### Failure Mode 2: The DV Is Not In The Table

This is the most consequential insight and the one I don't think the current Sprint D tasks fully address.

**In the majority of results tables, the dependent variable appears in the TABLE CAPTION or the preceding paragraph, not in the table itself.**

Example from a real paper:

> "Table 3. Multiple regression analysis predicting **creative performance** (AUT scores) from environmental variables."

| Predictor | B | SE | β | t | p |
|-----------|---|---|---|---|---|
| Ambient noise (dB) | 0.34 | 0.12 | 0.28 | 2.83 | .005 |
| Ceiling height (m) | 0.21 | 0.09 | 0.19 | 2.33 | .02 |
| Illuminance (lux) | 0.03 | 0.11 | 0.02 | 0.27 | .79 |

The DV "creative performance" appears ONLY in the caption. The table body contains only IVs and statistics. If the extractor looks only at cell content, it will never find the DV.

**Fix: Caption-First Extraction**

```python
def extract_dv_from_context(table_caption: str, preceding_paragraph: str, vocabulary: dict) -> tuple[str, float]:
    """
    ALWAYS check the caption first for the DV.
    
    Patterns to match:
    - "predicting X from..."          → X is the DV
    - "effects on X"                  → X is the DV  
    - "X as a function of..."         → X is the DV
    - "relationship between X and Y"  → both are candidates
    - "X scores by condition"         → X is the DV
    - "impact on X"                   → X is the DV
    - "X across groups/conditions"    → X is the DV
    """
```

The source_quote field in the CSV sometimes includes caption text. But often it doesn't — the caption is a separate PDF element. We may need to go back to the PDFs for the ~200 extractable papers and pull table captions specifically. This is an annoying but essential step.

**Recommendation for D.6:** The extraction engine's LLM prompt should ALWAYS include the table caption (if available) and should explicitly instruct: "The dependent variable is usually stated in the table caption, not in the table body. Look for phrases like 'predicting X', 'effects on X', 'X by condition' in the caption."

---

### Failure Mode 3: Synonym Coverage Is Too Thin

The current `_SYNONYMS` dict has 9 entries. The `_SYNONYM_GROUPS` has 5 groups. That's a total vocabulary of maybe 25 matchable terms. Environmental psychology uses hundreds of variable names.

Consider what a paper might actually say vs what the system can match:

| What the paper says | What the system needs | Can it match? |
|---|---|---|
| "daylighting" | illuminance_lux | ❌ Not in synonyms |
| "CCT" | cct_kelvin | ❌ |
| "RT60" | reverberation_time | ❌ |
| "SPL" | ambient_noise_dba | ❌ |
| "PANAS-positive" | mood | ❌ |
| "RAT scores" | creativity | ❌ |
| "salivary cortisol" | stress | ❌ |
| "thermal sensation vote" | thermal_comfort | ❌ |
| "Stroop task accuracy" | cognitive_load | ❌ |
| "prospect score" | spatial_openness | ❌ |
| "biophilic design index" | natural_material_ratio | ❌ |
| "view quality rating" | has_nature_view | ❌ |

**Fix: The vocabulary sheet (D.1) needs to be an order of magnitude larger.** Not 9 synonym mappings — 200+. And it needs to include:

1. **Measurement instrument names** → canonical DV: "PANAS" → mood, "PSS" → stress, "RAT" → creativity, "AUT" → creativity, "Stroop" → attention, "VAS" → (context-dependent), "SF-36" → well-being, "STAI" → stress
2. **Abbreviations** → canonical: "CCT" → cct_kelvin, "SPL" → ambient_noise_dba, "RT60" → reverberation_time, "IEQ" → indoor_environmental_quality, "POE" → post_occupancy_evaluation, "STC" → acoustic_privacy_stc
3. **Physiological markers** → canonical DV: "salivary cortisol" → stress, "heart rate variability" → physiological_arousal, "skin conductance" → physiological_arousal, "alpha asymmetry" → mood, "EEG theta" → cognitive_load
4. **Architectural feature variants** → canonical IV: "prospect" → spatial_openness, "refuge" → enclosure, "mystery" → visual_complexity, "legibility" → wayfinding_clarity, "complexity" → visual_complexity, "coherence" → visual_order
5. **Common phrasings in table headers**: "Group 1 / Group 2" → needs context, "Condition A / Condition B" → needs context, "Pre / Post" → direction marker, "Control / Experimental" → direction marker

---

### Failure Mode 4: Forced Matching Produces Confident Wrong Answers

From the audit:
```
environment_variable: "instruction"
environment_canonical_id: env.ae.hazard_indicators
environment_resolution_confidence: 0.87
```

The system matched "instruction" (an experimental protocol step) to "hazard_indicators" with 87% confidence. This is a fuzzy string match gone wrong — "instruction" partially matches "hazard indicators" at the character level.

**This is worse than no match.** A forced wrong match injects false information into the web of belief. An honest "unresolved" is infinitely better than a confident misclassification.

**Fix: Matching Threshold + Rejection Class**

```python
def resolve_variable(raw_term: str, vocabulary: dict, threshold: float = 0.70) -> dict:
    """
    Match a raw variable name to the canonical vocabulary.
    
    CRITICAL: If the best match is below threshold, return UNRESOLVED.
    Do NOT force a match. An honest "I don't know" is better than a 
    confident wrong answer.
    
    Returns:
        {
            "canonical": "illuminance_lux" or None,
            "confidence": 0.92,
            "match_type": "exact" | "synonym" | "fuzzy" | "unresolved",
            "raw_term": "daylight levels"
        }
    """
    # Step 1: Exact match against canonical names
    # Step 2: Exact match against all synonyms
    # Step 3: Fuzzy match (but ONLY above threshold)
    # Step 4: Return unresolved
```

Additional safeguards:
- **Blacklist common non-variable terms:** "instruction", "appendix", "figure", "table", "reference", "et al", author names, university names
- **Minimum term length:** Skip any candidate shorter than 3 characters or longer than 50 characters
- **Self-match detection:** If IV == DV after resolution, flag as EXTRACTION_ERROR, not a finding
- **Number detection:** If the "variable" is a number (e.g., "0.34", "2.83"), it's a statistic, not a variable name

---

### Failure Mode 5: OCR Corruption Is Not Detected Pre-Resolution

From the audit:
```
environment_variable: "ffititttiningg thhee sseennssoorrss"
environment_variable: "ttaacctitliele exxppeerirmimenentt dduummmmyy"
environment_variable: "csihpipless aobrsdtrera csttrbuicotluorge"
```

These are character-level OCR doublings. The first is "Fitting the sensors." The second is "Tactile experiment: Dummy." The third is completely garbled. These should be caught BEFORE any variable resolution is attempted.

**Fix: OCR Quality Gate**

```python
import re

def ocr_quality_check(text: str) -> dict:
    """Detect common OCR corruption patterns."""
    
    issues = []
    
    # Pattern 1: Doubled characters (e.g., "ttaaccttiillee" → "tactile")
    doubled = re.findall(r'(.)\1{2,}', text)
    if len(doubled) > 2:
        issues.append("character_doubling")
    
    # Pattern 2: No spaces in long text (concatenated words)
    if len(text) > 30 and ' ' not in text:
        issues.append("concatenated_words")
    
    # Pattern 3: Interleaved characters from multi-column extraction
    # Detected by: alternating pattern of real and garbage characters
    # Heuristic: compute ratio of consonant clusters > 3
    consonant_clusters = re.findall(r'[bcdfghjklmnpqrstvwxyz]{4,}', text.lower())
    if len(consonant_clusters) > 2:
        issues.append("column_interleaving")
    
    # Pattern 4: Non-ASCII ratio (garbled encoding)
    non_ascii = sum(1 for c in text if ord(c) > 127)
    if non_ascii / max(len(text), 1) > 0.1:
        issues.append("encoding_corruption")
    
    return {
        "clean": len(issues) == 0,
        "issues": issues,
        "confidence": max(0, 1.0 - 0.3 * len(issues))
    }
```

This gate should run BEFORE table classification. Corrupted tables are classified as GARBAGE regardless of content. This alone would have caught the 7,142 self-matching rows and the worst of the OCR artifacts.

---

### Summary: The Five Fixes Ranked by Impact

| Fix | Impact | Effort | Sprint D Task |
|-----|--------|--------|---------------|
| **1. Table-type-aware extraction** | ★★★★★ | Medium | D.6 (extraction engine) |
| **2. Caption-first DV extraction** | ★★★★★ | Low-Medium | D.6 (extraction engine) |
| **3. Vocabulary expansion to 200+ terms** | ★★★★ | Medium | D.1 (vocabulary sheet) |
| **4. Matching threshold + rejection class** | ★★★★ | Low | D.1 (vocabulary.py) |
| **5. OCR quality gate** | ★★★ | Low | D.3 (table classification) |

Fixes 1 and 2 are the game-changers. The current system treats all tables the same way and looks for the DV inside the table. In most results tables, the DV is in the caption and the table body contains only IVs and statistics. Getting this right would convert the precision from ~0% to ~60-70% overnight.

Fixes 3 and 4 are the next tier. A 9-entry synonym dictionary is absurdly small. And forced fuzzy matching that confidently maps "instruction" to "hazard_indicators" is actively harmful.

Fix 5 is defensive — it prevents garbage from entering the pipeline at all. Quick to implement, and would have prevented ~40% of the bad data.

---

### CONCRETE INSTRUCTION FOR CC AND CODEX

If Sprint D tasks D.1 and D.6 are still in progress, please incorporate these specific changes:

**For D.1 (vocabulary sheet):**
- Target: minimum 30 IVs, 25 DVs, 200+ total synonyms
- MUST include measurement instrument names (PANAS, PSS, RAT, AUT, STAI, VAS, SF-36, Stroop, n-back, etc.)
- MUST include abbreviations (CCT, SPL, RT60, STC, IEQ, PMV, PPD, etc.)
- MUST include physiological markers mapped to DVs (cortisol → stress, HRV → arousal, etc.)
- MUST include Kaplan ART terms (fascination, being-away, extent, compatibility) mapped to canonical IVs
- MUST include Appleton terms (prospect, refuge, mystery, complexity) mapped to canonical IVs
- find_closest_iv() and find_closest_dv() MUST have a rejection threshold — return None if best match < 0.65

**For D.3 (table classification):**
- Add OCR quality gate as pre-filter — corrupted tables → GARBAGE, no further processing
- Self-match detection: if every row has env_var == outcome_var, the table is not a results table

**For D.6 (extraction engine):**
- Table-type-aware extraction: use different extraction logic for regression vs ANOVA vs correlation vs descriptive vs literature review
- Caption-first DV extraction: the LLM prompt MUST instruct "Find the dependent variable in the table caption first, then in column headers, then in the table body — in that priority order"
- If using rule-based extraction: column 1 of a regression table = IVs, DV = from caption. Cell values in columns labeled β/B/r = effect sizes. Cells labeled p = significance.

---

## PART 3: ABSTRACT EXTRACTION — THE MISSING PIPELINE

Sprint D focused entirely on table extraction and neglected the single best data source we have: **abstracts**. This is a significant oversight that must be corrected.

### Why Abstracts Matter

Abstracts are:
- **Clean text** — no OCR corruption, no table parsing ambiguity, no column misalignment
- **Author-curated summaries** — researchers put their clearest statements of findings in the abstract
- **Nearly universal** — we have abstracts for almost all 386 papers (from the `articles` table in ae.db + Semantic Scholar API)
- **Multi-claim rich** — a typical empirical abstract contains 2-4 distinct findings, including null results
- **Already partially extracted** — the web has `abstract_rule` beliefs, but they're single-claim, no effect sizes, no sample N, credence = 0.5

### What the System Currently Does with Abstracts

The existing abstract extraction (visible in the web as `rt:doi:...:abstract_rule` beliefs) produces ONE claim per abstract at the crudest level:

```
content: "Abstract-provisional: noise → mood (positive)"
credence: 0.5
environment_id: env.noise
outcome_id: out.mood
```

This loses: the effect size, the sample N, null findings, multiple DVs, measurement instruments, moderators, and context. A typical abstract contains 3-5x more information than this extraction captures.

### What Abstracts Actually Contain (Worked Example)

**Abstract from Mehta, Zhu & Cheema (2012), doi:10.1086/665048:**

> "Results from five experiments demonstrate that a moderate (70 dB) versus low (50 dB) level of ambient noise enhances performance on creative tasks (RAT, n=65, Experiment 1) and increases the likelihood of choosing innovative products (n=93, Experiment 4). A high level of noise (85 dB), however, reduces creativity (n=65, Experiment 1). Process measures reveal that a moderate level of noise induces processing disfluency which activates abstract cognition, thereby enhancing creativity."

**Claims extractable:**
1. `ambient_noise_dba (70 vs 50) → creativity: positive, instrument=RAT, n=65`
2. `ambient_noise_dba (70 vs 50) → product_innovation_choice: positive, n=93`
3. `ambient_noise_dba (85 vs 50) → creativity: negative, n=65`
4. `ambient_noise_dba (moderate) → abstract_cognition: positive` (mechanism claim)

The current system extracts only claim 1, and without the effect size, N, or instrument.

### TASK D.14 — Abstract Claim Extraction (NEW)

**Assign to: CC or Codex · Estimated: 90–120 min · Dependency: D.1 (vocabulary) DONE**

Create `src/extraction/abstract_extractor.py`:

```python
def extract_claims_from_abstract(
    paper_id: str,
    title: str,
    abstract: str,
    vocabulary: dict,
    method: str = "llm"
) -> list[dict]:
    """Extract ALL structured claims from a paper abstract.
    
    Unlike table extraction (which requires table structure parsing),
    abstract extraction works on clean natural language prose.
    
    Returns claims in the same format as table extraction:
    [{iv, dv, direction, effect_size, sample_n, context, ...}]
    """
```

**LLM prompt for abstract extraction:**

```
You are extracting structured scientific claims from a research paper's
abstract. This paper studies how architectural or environmental features 
affect human outcomes (wellbeing, cognition, health, behavior, comfort).

TITLE: {title}
ABSTRACT: {abstract}

TASK: Extract EVERY causal or correlational finding stated in this abstract.
For each finding, identify:

1. Independent variable (what was manipulated, varied, or measured as predictor)
2. Dependent variable (what outcome was measured)
3. Direction: "positive" (IV↑ → DV↑), "negative" (IV↑ → DV↓), 
   "null" (no significant effect), "curvilinear" (inverted-U or U-shaped)
4. Effect size (if stated: d, r, η², β, OR, percentage, or descriptive)
5. Sample size (if stated: N=, n=, or "X participants")
6. Measurement instrument (if named: RAT, PANAS, cortisol, EEG, etc.)
7. Context (lab/field, population, setting)

MAP variables to the closest match from this vocabulary:

INDEPENDENT VARIABLES:
{formatted_iv_vocabulary}

DEPENDENT VARIABLES:
{formatted_dv_vocabulary}

CRITICAL RULES:
- Extract NULL findings too — "no significant effect on X" is a claim
- Extract CURVILINEAR findings — "moderate noise enhanced but high noise impaired" is TWO claims
- If the abstract mentions multiple experiments, extract from EACH
- If a finding has a specific comparison (70 dB vs 50 dB), note it in context
- If no vocabulary match exists, use a descriptive term and set mapped=false
- Do NOT extract: theoretical claims without data, citations of other work, 
  methodological descriptions without results

OUTPUT: JSON array of claims (same format as table extraction)
```

**Rule-based fallback for abstracts:**

Abstracts have predictable linguistic patterns. A rule-based extractor can catch 50-60% of claims using regex + vocabulary matching:

```python
# Patterns that signal a finding in abstract prose
FINDING_PATTERNS = [
    # "X significantly affected/influenced/predicted Y"
    r'(\w[\w\s]+?)\s+(?:significantly\s+)?(?:affected|influenced|predicted|improved|reduced|increased|decreased|enhanced|impaired)\s+(\w[\w\s]+)',
    
    # "significant effect of X on Y"
    r'(?:significant|positive|negative|no)\s+(?:effect|impact|influence)\s+of\s+(\w[\w\s]+?)\s+on\s+(\w[\w\s]+)',
    
    # "X was associated with Y"
    r'(\w[\w\s]+?)\s+(?:was|were|is|are)\s+(?:positively|negatively|significantly|not)?\s*(?:associated|correlated|related|linked)\s+(?:with|to)\s+(\w[\w\s]+)',
    
    # "higher/lower X led to better/worse Y"
    r'(?:higher|lower|greater|less|more|increased|decreased)\s+(\w[\w\s]+?)\s+(?:led to|resulted in|produced|caused)\s+(?:better|worse|higher|lower|improved|reduced)\s+(\w[\w\s]+)',
    
    # Effect size patterns
    r'[dDrRβη²]\s*=\s*([\d.]+)',
    r'[Nn]\s*=\s*(\d+)',
    r'p\s*[<>=]\s*([\d.]+)',
]
```

**Batch abstract extraction:**

```python
def batch_extract_abstracts(
    articles_db_path: str = "ae.db",
    csv_path: str = "data/production/realtime_pdf_confirmed_rows.csv",
    vocabulary_path: str = "data/vocabulary/variable_vocabulary.json",
    output_path: str = "data/production/abstract_claims.json"
) -> dict:
    """Extract claims from ALL available abstracts.
    
    Sources (in priority order):
    1. articles table in ae.db (has 53 papers with full abstracts)
    2. CSV rows with source_section='abstract' 
    3. Semantic Scholar API for DOIs missing from above
    
    Returns summary statistics and saves claims to output_path.
    """
```

### How Abstract Claims Complement Table Claims

Abstract claims and table claims serve different purposes and should be MERGED, not chosen between:

| Property | Abstract Claims | Table Claims |
|----------|----------------|--------------|
| **Coverage** | Nearly all 386 papers | Only papers with extractable tables (~150) |
| **Precision** | High — clean prose, no OCR | Variable — depends on table type |
| **Depth** | Key findings only (2-4/paper) | All findings including secondary (5-20/paper) |
| **Effect sizes** | Sometimes stated | Usually present in results tables |
| **Sample N** | Usually stated | Sometimes stated |
| **Null findings** | Often mentioned | Often omitted from tables |
| **Context** | Rich — population, setting, duration | Sparse — embedded in table structure |

**Merge strategy in D.10 (batch pipeline):**

```python
def merge_claim_sources(
    abstract_claims: list[dict],
    table_claims: list[dict]
) -> list[dict]:
    """Merge abstract-derived and table-derived claims.
    
    Rules:
    1. If same IV+DV+direction appears in both → keep BOTH, flag as corroborated
    2. If abstract has a claim not in tables → keep (tables may have missed it)
    3. If table has a claim not in abstract → keep (abstract may have omitted it)
    4. If same IV+DV with DIFFERENT directions → flag as CONFLICT for review
    5. For corroborated claims: prefer table's effect_size (more precise),
       prefer abstract's context description (richer)
    
    Each merged claim tracks its provenance:
    {
        "source": "abstract+table" | "abstract_only" | "table_only",
        "abstract_claim_id": "...",
        "table_claim_id": "...",
        "corroboration_status": "corroborated" | "unique" | "conflict"
    }
    """
```

**Expected yield from abstract extraction:**
- 386 papers × ~2.5 claims/abstract = ~950 claims
- Of these, ~70% should have clean IV/DV pairs (abstracts are unambiguous)
- ~40% will have effect sizes stated
- ~60% will have sample N stated
- Overlap with table claims: ~30-40% (providing corroboration)
- Unique abstract claims (not in tables): ~60% (expanding coverage)

This means abstract extraction alone could produce ~650 high-quality claims — MORE than the estimated yield from table extraction of the entire corpus. And it's faster, cleaner, and cheaper to implement.

### Integration with Existing Abstract Rules

The web of belief already has `abstract_rule` beliefs. The rebuild (D.11) should:
1. **DELETE** all existing `abstract_rule` beliefs (they're single-claim, no detail)
2. **REPLACE** with the multi-claim abstract extractions from D.14
3. Mark new beliefs with `provenance: "abstract_v2"` to distinguish from the old ones

### TASK D.15 — Abstract Claim Integration into Batch Pipeline (NEW)

**Assign to: Codex (since Codex owns D.10) · Estimated: 60 min · Dependency: D.14 + D.10 DONE**

Modify `src/extraction/batch_extract.py` to:
1. Run abstract extraction for ALL papers (not just triaged empirical ones — even review papers have useful abstracts)
2. Run table extraction for triaged empirical/review papers with extractable tables
3. Merge both claim sources using the merge strategy above
4. Output combined `data/production/structured_claims.json` with provenance tracking

Update `data/production/structured_claims.json` schema to include:
```json
{
    "claims": [...],
    "summary": {
        "total_claims": 2100,
        "from_abstracts": 950,
        "from_tables": 1400,
        "corroborated": 250,
        "abstract_only": 700,
        "table_only": 1150,
        "conflicts": 12
    }
}
```

---

*Document 71 — Sprint D Progress Diagnostics + Mapping Precision Analysis + Abstract Extraction*
*February 18, 2026*
