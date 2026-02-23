# Pricing Table Extraction Methods

Date: 2026-02-18  
Owner: David

## Critical Definition

In this document, "table extraction" means:
- the full article-type semantic output record needed for rule generation,
- not literal syntactic PDF tables.

Target output is article-type-appropriate content for Web/BN rule synthesis:
- hypothesis/question
- method/design/stimuli/subjects
- findings/results/effect info
- theory/mechanism/limitations
- links to prior work and contradiction/corroboration relations

## Single Operator Instruction

Tell any agent exactly this:

`Follow docs/Pricing_Table_extraction_methods.md for role <ROLE> and execute it.`

Valid role values:
- `CODEX`
- `CC`
- `AG`

## Role Notes

- `CC`: may switch tiers mid-session with:
  - `/model opus` (upper)
  - `/model sonnet` (balanced)
  - `/model haiku` (low)
- `CODEX`: model tier is selected at process launch; use profile-driven ladder runs for fair comparison.
- `AG`: cannot spawn a second full conversational AG instance. For parallel model comparison, use `scripts/run_llm_table_ladder_agent.py` as the benchmark agent.
- `AG`: use AG-native model switch mechanism and/or AG profile file, but keep the same ladder run contract and output schema.

## Universal Prompt (Use As-Is)

```text
You are executing the pricing/quality benchmark for article-semantic extraction.
Do NOT optimize for literal table-grid detection.

ROLE = <ROLE> where ROLE is one of: CODEX, CC, AG.

Read these files first:
1) docs/SprintD_Agent_Prompts.md
2) docs/LLM_LADDER_AGENT_PROTOCOL.md
3) scripts/run_llm_table_ladder_agent.py
4) scripts/run_llm_table_pilot.py
5) scripts/audit_rule_type_coverage.py
6) docs/ARTICLE_SEMANTIC_EXTRACTION_AND_RULE_TYPES_RETHINK_2026-02-18.md

Role-specific profile file:
- CODEX: config/llm_table_pilot_profiles.codex.json
- CC: config/llm_table_pilot_profiles.cc.json
- AG: config/llm_table_pilot_profiles.ag.json

If the role-specific profile file does not exist, create it with three tiers:
- upper_<role>, balanced_<role>, low_<role>
- fields required: name, provider, model

Run the detached ladder benchmark for extraction quality/cost:

python3 scripts/run_llm_table_ladder_agent.py start \
  --profiles <role-specific-profile-file> \
  --n-pdfs 5 \
  --variants strict_gate \
  --mode parallel \
  --detach \
  --tag <role-ladder>

Then run:
python3 scripts/run_llm_table_ladder_agent.py status --manifest <manifest_path>
python3 scripts/run_llm_table_ladder_agent.py summarize --manifest <manifest_path>

Then run rule-type coverage audit on your semantic output claims JSON:

python3 scripts/audit_rule_type_coverage.py \
  --claims <structured_claims_json_path> \
  --triage data/production/paper_triage.json \
  --out-json data/production/rule_type_audit/<role>_<run_id>.json

Report exactly:
1) manifest path
2) ladder_summary.json path
3) ladder_summary.md path
4) best_by_precision_proxy row
5) full runs table with columns:
   profile, variant, claims, mapped_both_pct, suspect_claims_pct, unknown_direction_pct, precision_proxy
6) rule_type_audit json path
7) candidate_missing_rule_types list
8) family_coverage table

Rules:
- Keep same queue snapshot, n-pdfs, and variants for comparability.
- Do not change extraction logic during benchmark runs.
- Do not modify unrelated files.
- If ROLE=CC, model selection can happen mid-session via `/model` without restarting, but output files and metrics format must remain identical.
- Treat literal PDF table detection as a legacy substep; final evaluation target is article-type semantic completeness + rule-type coverage.
```

## Known Working Codex Profile

- `config/llm_table_pilot_profiles.codex.json`

## Minimum Required References

- `docs/SprintD_Agent_Prompts.md`
- `docs/LLM_LADDER_AGENT_PROTOCOL.md`
- `docs/ARTICLE_SEMANTIC_EXTRACTION_AND_RULE_TYPES_RETHINK_2026-02-18.md`
- `scripts/run_llm_table_ladder_agent.py`
- `scripts/run_llm_table_pilot.py`
- `scripts/audit_rule_type_coverage.py`
