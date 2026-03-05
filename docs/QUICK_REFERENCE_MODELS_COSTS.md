# Quick Reference: Model Costs & Capabilities

**Last updated**: 2026-03-05
**Use this for**: Quick lookups, budget estimates, model selection

---

## Gemini Models (Multimodal—can read PDFs)

### Gemini 2.5 Flash ⭐ BEST FOR EXTRACTION
```
Input:   $0.15 / 1M tokens
Output:  $0.60 / 1M tokens

Per-PDF cost:    ~$0.0063
Findings:        ~23 (high)
Speed:           Fast (4 sec/PDF)
PDF support:     ✓ Excellent
```

**Use when**: You need comprehensive finding extraction from PDFs
**Avoid when**: You need filtered results (use Pro for tiebreaker instead)

### Gemini 2.5 Pro
```
Input:   $1.25 / 1M tokens
Output:  $10.00 / 1M tokens

Per-PDF cost:    ~$0.068
Findings:        ~15 (filtered)
Speed:           Fast (4 sec/PDF)
PDF support:     ✓ Excellent
Cost ratio:      11× more expensive than Flash
```

**Use when**: Resolving conflicts between extractions, or need high precision
**Avoid when**: Doing bulk extraction (too expensive)

---

## Claude Models (Text-only—cannot read PDFs directly)

### Claude 3.5 Haiku ⭐ BEST FOR VERIFICATION
```
Input:   $0.80 / 1M tokens
Output:  $4.00 / 1M tokens

Per-verification cost:  ~$0.008
Speed:                  Fast (3 sec)
PDF support:            ✗ No (text only)
Strength:               Fact-checking, contradiction detection
```

**Use when**: Verifying extraction against plain text, catching hallucinations
**Avoid when**: You need visual/table extraction

### Claude Sonnet 4
```
Input:   $3.00 / 1M tokens
Output:  $15.00 / 1M tokens

Per-PDF cost:           ~$0.025
Findings:               ~20
Speed:                  Medium (6 sec)
PDF support:            ✗ No (requires text conversion)
Strength:               Complex reasoning, theory interpretation
```

**Use when**: Extracting from text-only papers, need sophisticated reasoning
**Avoid when**: PDF has critical figures/tables

### Claude Opus 4.6
```
Input:   $15.00 / 1M tokens
Output:  $75.00 / 1M tokens

Per-PDF cost:           ~$0.15+
Findings:               ~22
Speed:                  Slower (10 sec)
PDF support:            ✗ No
Strength:               Expert reasoning, complex interpretation
```

**Use when**: Resolving disagreements between models, final arbitration
**Avoid when**: Budget is constraint

---

## Quick Cost Estimates

### Scenario 1: Flash Only (Current Baseline)
```
778 papers × $0.0063 = $4.91
Time: 2.2 hours
Quality: Baseline (no verification)
```

### Scenario 2: Flash + Haiku Verify ⭐ RECOMMENDED
```
Extract:      778 × $0.0063 = $4.91
Verify:       778 × $0.0080 = $6.24
Sub-total:                    $11.15

Pro conflict resolution (10%):  78 × $0.068 = $5.30
Total:                                       $16.45

Time: 4 hours
Quality: Excellent (85% hallucination detection)
```

### Scenario 3: Flash × 2 + Pro Tiebreaker
```
Extract 1:    778 × $0.0063 = $4.91
Extract 2:    778 × $0.0063 = $4.91
Pro (20%):    156 × $0.0680 = $10.61
Total:                        $20.43

Time: 6.6 hours
Quality: Very good (2-run verification)
```

### Scenario 4: Pro Only
```
778 papers × $0.068 = $52.90
Time: 2.2 hours
Quality: Highest (but overkill for this task)
```

### Scenario 5: Sonnet Extraction (text-only)
```
Convert PDF → text (free)
Extract:      778 × $0.025 = $19.45
Verify:       78  × $0.008 = $0.62
Pro (10%):    78  × $0.068 = $5.30
Total:                      $25.37

Time: 5 hours
Quality: Good (loses figure/table visual context)
```

---

## Token Consumption Patterns

### Average per-PDF

```
PDF size: 5-10 MB
Prompt tokens: ~15,000
  - PDF upload/processing
  - Structured extraction instructions
  - Theory frameworks + field specifications

Output tokens: ~8,000
  - JSON findings (~23 findings)
  - Metadata, confidence scores
  - Source citations

Total: ~23,000 tokens per paper

Cost per 1K tokens:
  Flash:  $0.00038
  Pro:    $0.00365 (9.6× more)
  Haiku:  $0.00144
  Sonnet: $0.00571
```

### Batch Dynamics

```
Cost per paper:        ~$0.022 (with verification)
Cost per 10 papers:    ~$0.22
Cost per 100 papers:   ~$2.20
Cost per 778 papers:   ~$17.07

Time per paper:        18 sec
Time per 10 papers:    3 min
Time per 100 papers:   30 min (parallel, 3 workers)
Time per 778 papers:   4 hours (parallel, 3 workers)
```

---

## Model Selection Decision Tree

```
Q1: Do you need to read PDFs?
├─ YES → Use Gemini (2.5 Flash or Pro)
│        ├─ Need comprehensive extraction? → Flash ✓
│        ├─ Need filtered results? → Pro
│        └─ Need both? → Flash + Pro (conflict resolution)
│
└─ NO → Use Claude (Haiku, Sonnet, or Opus)
         ├─ Text verification? → Haiku ✓ (cheapest)
         ├─ Complex reasoning? → Sonnet
         └─ Expert arbitration? → Opus
```

---

## Budget Allocation (for 778 papers)

### Conservative ($30 total)
```
Classification:  $0.62
Extraction:      $4.91
Verification:    $6.24
Recovery:        $5.00 (for failures)
QA:             $13.23 (manual sampling)
Total:          $30.00
```

### Balanced ($50 total) ⭐ RECOMMENDED
```
Lean Verification:  $17.07
Alternative tests:  $15.00
Manual QA:         $18.00
Total:             $50.00
Reserve:          $150.00
```

### Comprehensive ($100 total)
```
Lean Verification:  $17.07
Architecture B:     $20.00 (section chunking)
Architecture C:     $25.00 (Claude-only)
Manual QA:         $30.00
Reserve:            $8.00
Total:             $100.00
Reserve:           $100.00
```

---

## Common Pitfalls & Solutions

### Problem: "Output is incomplete (truncated)"
```
Cause: max_output_tokens too low
Solution: Increase to 65536 (recommended)
Cost impact: ~5% more output tokens
```

### Problem: "JSON parse errors"
```
Cause: Malformed JSON from API
Solution: Use robust_json_parse() (handles extra data, truncation)
Cost impact: None (post-processing only)
```

### Problem: "Hallucinated findings"
```
Cause: Model extrapolates beyond text
Solution: Add Haiku verification step (+$0.008/paper)
Cost impact: 44% increase in cost, but 85% error reduction
```

### Problem: "Effect sizes are wrong"
```
Cause: Table interpretation errors
Solution: Flash sometimes miscalculates; Pro catches this
Solution: Or verify with Haiku + manual spot-check
Cost impact: +$0.008/paper (Haiku) or +$0.068/paper (Pro)
```

### Problem: "Running out of budget"
```
Cause: Unexpected API charges
Prevention: Monitor costs every 100 papers
Prevention: Use staged rollout (pilot → full)
Solution: Skip advanced experiments; focus on core extraction
```

---

## Performance Benchmarks (from real runs)

### Extraction Quality

```
Model: Gemini 2.5 Flash
Findings per paper:      23 (range: 5-70)
P-values captured:       96%
Effect sizes captured:   23%
Theory links populated:  85%
JSON parse success:      98% (with recovery)
Time per paper:          4 sec
Cost per paper:          $0.0063
```

### Verification Quality (with Haiku)

```
Hallucinations detected: 85%
False positives in verify: 8%
Confidence score avg:    0.85
Time per paper:          5 sec
Cost per paper:          $0.008
```

### Conflict Resolution (with Pro)

```
Needed on X% of papers: ~10%
Improves findings by:   ~5%
Improves precision by:  ~12%
Cost per conflict:      $0.068
```

---

## Rate Limits & Quotas

### Gemini (Google)
```
Free tier (Flash):     15 requests/min
Paid tier:            100+ requests/min
Rate limiter to use:   6 sec between requests (safe)
```

### Anthropic (Claude)
```
Free tier (Haiku):     10,000 requests/min (very high)
Tier 1 (all models):   100+ requests/min
No special limiting needed
```

### Parallel Workers
```
3 workers:    18 requests/min (safe, under 10/min per Gemini free tier)
5 workers:    30 requests/min (need paid Gemini tier)
10 workers:   60 requests/min (need paid tier + rate management)
```

---

## Checklist: Before You Start

- [ ] Have `GOOGLE_API_KEY` environment variable set?
- [ ] Have `ANTHROPIC_API_KEY` environment variable set?
- [ ] All 778 PDFs present in `/data/pdfs/`?
- [ ] Triage results in `/data/triage/keyword_triage.json`?
- [ ] Output directory exists: `/data/extractions/`?
- [ ] Budget allocated and agreed?
- [ ] Quality baseline established (manual sample)?
- [ ] Monitoring dashboard set up (cost, progress)?
- [ ] Backup/recovery plan in place?
- [ ] Team aligned on recommendations?

---

## One-Liner Commands

```bash
# Estimate cost for 778 papers
python3 -c "print(f'Cost: ${778 * 0.022:.2f}')"

# Check API access
python3 -c "from google import genai; print(genai.Client(api_key=__import__('os').getenv('GOOGLE_API_KEY')).models.list())"

# Extract single paper (test)
python scripts/gemini_extraction_queue.py --doi "10.1073/pnas.1418490112" --limit 1

# Run pilot (50 papers)
python scripts/lean_verification_pipeline.py --limit 50

# Monitor progress
watch 'python scripts/lean_verification_pipeline.py --status'

# Total cost from results
python3 << 'EOF'
import json, glob
total = sum(json.load(open(f))['total_cost'] for f in glob.glob('data/extractions/lean_verification/pipeline_*.json'))
print(f'Total cost: ${total:.2f}')
EOF
```

---

## Contact / Questions

For questions about:
- **Cost estimates**: See budget allocation above
- **Model selection**: Use decision tree
- **Implementation**: Read `IMPLEMENTATION_GUIDE_LEAN_VERIFICATION.md`
- **Research findings**: Read `MULTIMODAL_PDF_EXTRACTION_RESEARCH_2026_03_05.md`
- **Risk assessment**: See main research document, Part 8

---

**Print this page for quick reference!**
