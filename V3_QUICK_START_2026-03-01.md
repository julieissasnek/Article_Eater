# V3 Extraction Quick Start Guide

**Date**: 2026-03-01
**Status**: Ready to Deploy
**Scripts Created**: 2 production-ready Python scripts
**Documentation Created**: 2 comprehensive guides

---

## What Was Built

Two scripts to upgrade the Article_Eater corpus using OpenAI GPT-4o and v3 prompts:

### 1. v3_reextraction.py
**Purpose**: Re-extract 59 zero-finding articles
- **Input**: 59 articles with n_findings=0
- **Output**: Full findings arrays + v3 fields
- **Cost**: ~$4
- **Time**: ~15 minutes

```bash
# Test (dry-run)
python3 scripts/v3_reextraction.py --dry-run --limit 5

# Deploy (all 59)
python3 scripts/v3_reextraction.py
```

### 2. v3_surgical_update.py
**Purpose**: Add v3 fields to 1,002 existing articles
- **Input**: 1,002 articles with existing findings
- **Output**: Original findings + new v3 fields (theory_commitments, mechanism_chain, instruments_used, stimulus_description)
- **Cost**: ~$30
- **Time**: ~25 minutes

```bash
# Test (dry-run)
python3 scripts/v3_surgical_update.py --dry-run --limit 10

# Deploy (all 1,002)
python3 scripts/v3_surgical_update.py
```

---

## Corpus Status

| Type | Count | Action |
|------|-------|--------|
| Zero findings (Tier 1) | 60 | Run v3_reextraction.py |
| With findings (Tier 2+) | 1,002 | Run v3_surgical_update.py |
| **Total** | **1,062** | Both scripts |

---

## Deploy in 2 Minutes

### Prerequisites Check
```bash
# Verify dependencies
python3 -c "import openai; print('✓ OpenAI installed')"
cat .env | grep OPENAI_API_KEY | head -c 20
```

### Phase 1: Tier 1 (60 articles)
```bash
cd /sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1
python3 scripts/v3_reextraction.py
# Wait ~15 minutes
# Check: data/field_discovery/v3_reextraction_results.json
```

### Phase 2: Tier 2+ (1,002 articles)
```bash
python3 scripts/v3_surgical_update.py
# Wait ~25 minutes
# Check: data/field_discovery/v3_surgical_update_results.json
```

### Verify Results
```bash
# Quick check
python3 << 'EOF'
import json
from pathlib import Path
results1 = json.loads(Path("data/field_discovery/v3_reextraction_results.json").read_text())
results2 = json.loads(Path("data/field_discovery/v3_surgical_update_results.json").read_text())
print(f"Phase 1: {results1.get('success')} success, cost ${results1.get('total_cost'):.2f}")
print(f"Phase 2: {results2.get('success')} success, cost ${results2.get('total_cost'):.2f}")
