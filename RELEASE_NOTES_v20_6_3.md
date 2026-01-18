# v20.6.3 — Engines Powered (Full LLM Integration)

**Date**: November 17, 2025  
**Type**: Engine Power-On Upgrade  
**Governance**: Strictly additive with archival

## What's New

### Real LLM-Powered Agents (No More Stubs!)

All three core agents now make actual LLM calls instead of printing placeholders:

1. **Agent_Finder** - Extracts Seven-Panel findings
   - Real LLM extraction via provider-agnostic core
   - JSON schema validation against `prompts/seven_panel_schema.json`
   - Returns complete `SevenPanelArtifact` with provider/model tracking

2. **Agent_Aggregator** - Clusters findings into rule candidates
   - Uses `prompts/prompt_aggregator.md` for instructions
   - Identifies semantic similarity, contradictions
   - Returns rule candidates with supporting evidence indices

3. **Agent_Linker** - Proposes cross-rule links
   - Uses `prompts/prompt_linker.md` for instructions
   - Identifies chaining, synergy, antagonism patterns
   - Returns link proposals with evidence

4. **BBN_Calibrator** - Delegates to existing calibrator
   - No change (already functional)
   - Produces advisory artifacts without mutation

### New Prompts

- `prompts/prompt_aggregator.md` - Clustering instructions
- `prompts/prompt_linker.md` - Link inference instructions

### Safe Upgrade Script

- `scripts/optional_archive_then_replace_agent_stubs_v2063.py`
- Archives old `agent_stubs.py` before replacement
- Governance-compliant (no deletions)

## Changes

### New Files (3)
1. `prompts/prompt_aggregator.md` - Aggregator instructions
2. `prompts/prompt_linker.md` - Linker instructions
3. `scripts/optional_archive_then_replace_agent_stubs_v2063.py` - Archive utility

### Replaced Files (1)
- `src/agents/agent_stubs.py` - Now contains real LLM calls
- Original archived to `archive/_replaced_20251117_181129/src/agents/`

### Deleted Files
- **Zero** (governance compliant ✓)

## Architecture

### Agent Flow

```
Paper + Abstract
    ↓
Agent_Finder (LLM)
    ↓
Seven-Panel Items (validated JSON)
    ↓
    ├─→ Agent_Aggregator (LLM) → Rule Candidates
    ├─→ Agent_Linker (LLM) → Links
    └─→ BBN_Calibrator (math) → Confidence Weights
```

### LLM Provider Support

All agents use `src/agents/agent_core.py`:
- Gemini (default)
- OpenAI
- Anthropic
- Mock (testing)

### Prompt Management

All prompts editable via Admin Control Room:
- `/admin` → Prompts tab
- Live editing without restart
- Versioned backups in `archive/admin_edits/`

## Testing

### Mock Mode (No API Keys Required)

```bash
export AE_LLM_PROVIDER=mock
python3 -c "
from src.agents.agent_stubs import Agent_Finder
result = Agent_Finder('test paper', 'test abstract')
print(f'Provider: {result.provider}')
print(f'Items: {len(result.items)}')
"
```

### Real Provider

```bash
export AE_LLM_PROVIDER=gemini
export GEMINI_API_KEY=your-key
# Same test as above - will make real LLM call
```

## Governance Compliance

✅ **No Deletions**: Original agent_stubs.py archived  
✅ **Additive Only**: 3 new files, 1 replaced (archived)  
✅ **Versioned**: release.keep.yml updated  
✅ **Documented**: Complete release notes

## Migration from v20.6.2

1. Extract v20.6.3 files (already done if using this bundle)
2. Verify `src/agents/agent_stubs.py` contains `call_llm()` calls
3. No configuration changes required
4. Test with mock provider first, then real provider

## Verification

```bash
# Check for real LLM calls
grep "call_llm" src/agents/agent_stubs.py
# Should show 3+ matches

# Check no print stubs remain
grep "print(" src/agents/agent_stubs.py | grep -v "#"
# Should show only comments

# Verify prompts exist
ls prompts/prompt_*.md
# Should show aggregator and linker prompts
```

## Status

**Engines**: ✅ Powered ON  
**Stubs**: ❌ Removed  
**LLM Calls**: ✅ Active  
**Governance**: ✅ Compliant

---

**Previous version**: v20.6.2 (RBAC + Schema Validation)  
**This version**: v20.6.3 (Engine Power-On)  
**Next steps**: Run extraction pipeline with real LLM
