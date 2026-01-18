# Manual Patching Guide for Outcome Resolver

If automatic patching didn't work, apply these changes manually:

## 1. Add Import

At the top of the file with claim building, add:
```python
from lib.outcome_resolver import resolve_or_queue
```

## 2. Add Helper Function

After imports, add:
```python
def _resolve_outcome_id(raw_id, paper_id=None):
    """Resolve outcome ID through Outcome_Contractor."""
    try:
        result = resolve_or_queue(str(raw_id), paper_id=paper_id)
        return result['canonical_id']
    except Exception:
        return str(raw_id)
```

## 3. Wrap Outcome IDs

Find where outcomes are built into claims. Change:

```python
# OLD
"outcomes": [{"id": out_id, "role": "DV", ...} for out_id in outcomes]

# NEW  
"outcomes": [{"id": _resolve_outcome_id(out_id, paper_id), "role": "DV", ...} for out_id in outcomes]
```

Or if it's a loop:
```python
# OLD
for outcome in outcomes:
    claim["constructs"]["outcomes"].append({
        "id": outcome.get("id"),
        ...
    })

# NEW
for outcome in outcomes:
    claim["constructs"]["outcomes"].append({
        "id": _resolve_outcome_id(outcome.get("id"), paper_id),
        ...
    })
```

## Files to Check


### src/services/rulegraph_v2_builder.py
Functions: build_rulegraph_v2_rules
Relevant lines:
  Line 111: "outcomes": [],...

### app/cli/article_eater_contract_cli.py

### lib/combined_resolver.py
Functions: resolve_claim_constructs
Relevant lines:
  Line 52: 'outcomes': [],...

### app/tasks/pipeline.py
Functions: _run_from_contract_bundle_impl
Relevant lines:
  Line 217: constructs = finding.get("constructs") or {}...
  Line 246: "outcomes": [],...

### _archive/chatgpt_patch_20251231T060217Z/pipeline.py
Functions: run_from_contract_bundle
Relevant lines:
  Line 232: "outcomes": [],...
