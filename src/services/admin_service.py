from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import JSONResponse
from pathlib import Path
import yaml
from collections import defaultdict
import json
import io
import zipfile
import tempfile
import subprocess
import sys

from src.services.service_locator import get_graph_service
from src.tools import bn_export_to_csv, bn_suggest_outcome_templates

from src.security.admin_guard import admin_required


router = APIRouter()


SUBJECT_OVERRIDES_PATH = Path("data") / "rulegraph_v2_subject_overrides.json"
SUBJECT_VOCAB_PATH = Path("config") / "subject_vocab.json"

BN_EXPORT_VERSION = "0.2"
BN_EXPORT_GENERATOR = "article_eater_rulegraph_v2"



def _default_subject_vocab() -> dict:
    """Return a small built-in subject vocab used as a fallback.

    This is intentionally minimal and can be overridden by editing
    config/subject_vocab.json.
    """
    return {
        "demographics": {
            "age_band": ["18-25", "26-40", "41-65", "65+"],
            "education_band": ["HS_or_less", "Some_college", "Undergrad", "Grad"],
        },
        "clinical_status": {
            "population": ["healthy", "anxiety", "depression", "ADHD", "ASD", "MCI"],
        },
        "culture": {
            "region": [
                "North_America",
                "Western_Europe",
                "India",
                "East_Asia",
                "Middle_East",
                "Latin_America",
                "Global",
            ],
            "self_construal_profile": [
                "independent",
                "interdependent",
                "mixed",
                "unknown",
            ],
        },
    }


def _load_subject_vocab() -> dict:
    """Load the subject vocab from config/subject_vocab.json, with a safe fallback."""
    if not SUBJECT_VOCAB_PATH.exists():
        return _default_subject_vocab()
    try:
        raw = SUBJECT_VOCAB_PATH.read_text(encoding="utf-8")
        data = json.loads(raw) if raw.strip() else {}
        if isinstance(data, dict) and data:
            return data
        return _default_subject_vocab()
    except Exception:
        # Fail soft and use defaults if the vocab file is corrupt.
        return _default_subject_vocab()


def _load_subject_overrides() -> dict:
    """Load per-rule subject_scope/subject_moderators overrides.

    Keys are "<paper_id>::<rule_id>".
    """
    if not SUBJECT_OVERRIDES_PATH.exists():
        return {}
    try:
        raw = SUBJECT_OVERRIDES_PATH.read_text(encoding="utf-8")
        data = json.loads(raw) if raw.strip() else {}
        if isinstance(data, dict):
            return data
        return {}
    except Exception:
        # If the overrides file is corrupt, fail soft and ignore overrides.
        return {}


def _save_subject_overrides(overrides: dict) -> None:
    """Persist per-rule subject overrides to disk."""
    SUBJECT_OVERRIDES_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUBJECT_OVERRIDES_PATH.write_text(
        json.dumps(overrides, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _apply_subject_overrides_to_rule(paper_id: str, rule: dict, overrides: dict) -> dict:
    """Return a copy of rule with subject overrides (if any) applied.

    We do not mutate the original rule; instead we construct a shallow copy
    and replace subject_scope / subject_moderators when an override exists.
    """
    if not isinstance(rule, dict):
        return rule
    key = f"{paper_id}::{rule.get('rule_id')}"
    ov = overrides.get(key) or {}
    scope = ov.get('subject_scope')
    moderators = ov.get('subject_moderators')
    out = dict(rule)
    if scope is not None:
        out['subject_scope'] = scope
    if moderators is not None:
        out['subject_moderators'] = moderators
    return out


PROMPTS_DIR = Path('prompts')
CONF_PATH = Path('confidence_config.yml')

@router.get('/prompts', response_class=JSONResponse)
def get_prompts(ok: bool = Depends(admin_required)):
    PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
    items = []
    for p in PROMPTS_DIR.glob('*'):
        if p.is_file():
            try: c = p.read_text(encoding='utf-8', errors='ignore')
            except Exception: c = ''
            items.append({'name': p.name, 'content': c})
    return {'prompts': items}

@router.get('/confidence', response_class=JSONResponse)
def get_confidence(ok: bool = Depends(admin_required)):
    if not CONF_PATH.exists():
        default = {'RCT_Weights': {'N_weight':0.4,'p_weight':0.3,'d_weight':0.3},
                   'Meta_Weights': {'k_weight':0.3,'CI_weight':0.5,'I2_weight':0.2}}
        return {'config': default}
    data = yaml.safe_load(CONF_PATH.read_text(encoding='utf-8', errors='ignore')) or {}
    return {'config': data}

@router.post('/confidence/update')
def update_confidence(payload: dict, ok: bool = Depends(admin_required)):
    with open(CONF_PATH, 'w') as f:
        yaml.safe_dump(payload, f, sort_keys=False)
    return {'status':'ok'}

@router.post('/prompts/update')
def update_prompt(payload: dict, ok: bool = Depends(admin_required)):
    """Create or update a prompt file used by the Prompt Workshop UI.

    Payload shape:
      - name: filename (e.g. 'ruthless_prompt.md')
      - content: prompt text
    """
    # Support both legacy `prompt_name` and current `name`.
    name = (payload or {}).get('name') or (payload or {}).get('prompt_name')
    content = (payload or {}).get('content') or ''
    if not name:
        raise HTTPException(status_code=400, detail='name is required')
    PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
    path = PROMPTS_DIR / name
    path.write_text(content, encoding='utf-8')
    return {'status': 'ok', 'name': name}

def _summarize_scope(scope: dict) -> str:
    if not scope:
        return 'no subject_scope'
    bits = []
    demo = scope.get('demographics') or {}
    cult = scope.get('culture') or {}
    clin = scope.get('clinical_status') or {}
    traits = scope.get('traits_measured') or []

    if demo:
        band = demo.get('age_band') or 'age_band=unknown'
        n = demo.get('sample_size')
        n_str = f"n={n}" if n is not None else 'n=?'
        ed = demo.get('education_band') or 'education_band=unknown'
        bits.append(f"{band}, {ed}, {n_str}")
    if cult:
        region = cult.get('region') or 'region=unknown'
        countries = cult.get('countries') or []
        if countries:
            bits.append(f"{region}, {', '.join(countries)}")
        else:
            bits.append(region)
    if clin:
        pop = clin.get('population') or 'population=unknown'
        bits.append(pop)
    if traits:
        names = [t.get('name') for t in traits if isinstance(t, dict) and t.get('name')]
        if names:
            bits.append('traits: ' + ', '.join(sorted(set(names))))
    return ' | '.join(bits) if bits else 'no subject_scope'

def _summarize_moderators(moderators: list) -> str:
    if not moderators:
        return 'no moderators'
    dims = defaultdict(list)
    for m in moderators:
        if not isinstance(m, dict):
            continue
        dim = m.get('dimension') or 'other'
        attr = m.get('moderator') or m.get('attribute') or '<?>'
        dims[dim].append(attr)
    parts = []
    for dim, attrs in dims.items():
        uniq = sorted(set(attrs))
        parts.append(f"{dim}: {', '.join(uniq)}")
    return ' | '.join(parts)





@router.post('/run_v2_smoke', response_class=JSONResponse)
def run_v2_smoke(ok: bool = Depends(admin_required)):
    """Run the offline v2 pipeline smoke test and surface its result in the Admin UI.

    This calls `scripts/offline_pipeline_v2_smoke.py` in a subprocess so that:
    - subject-aware Seven-Panel v2 + RuleGraph v2 plumbing is exercised end-to-end;
    - results are visible to admins without requiring shell access.

    Returns a small JSON payload with status, return code, and the tail of stdout/stderr.
    """
    try:
        cmd = [sys.executable, "scripts/offline_pipeline_v2_smoke.py"]
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        status = "ok" if proc.returncode == 0 else "failed"
        # Trim logs so we don't flood the Admin UI.
        stdout_tail = proc.stdout[-4000:] if proc.stdout else ""
        stderr_tail = proc.stderr[-4000:] if proc.stderr else ""
        return {
            "status": status,
            "returncode": proc.returncode,
            "stdout": stdout_tail,
            "stderr": stderr_tail,
        }
    except Exception as exc:
        return {
            "status": "error",
            "error": str(exc),
        }


@router.get('/rulegraph_v2/subject_vocab', response_class=JSONResponse)
def get_rulegraph_subject_vocab(ok: bool = Depends(admin_required)):
    """Expose subject vocab so the Admin UI can populate suggestion lists."""
    return _load_subject_vocab()


@router.get('/rulegraph_v2', response_class=JSONResponse)
def get_rulegraph_v2(ok: bool = Depends(admin_required)):
    """Return a summary view of subject-aware RuleGraph v2 events.

    This powers the Admin UI's 'Subject Rules (RuleGraph v2)' tab and is
    deliberately compact and read-only.

    In addition to per-paper rule summaries, this endpoint now exposes
    subject typing coverage metrics so the Admin UI can show how many rules
    have age bands, culture regions, etc.
    """
    store = get_graph_service()
    events = store.get_all_events()
    overrides = _load_subject_overrides()
    out_events = []

    # Coverage metrics per paper and global
    coverage_by_paper: dict[str, dict[str, int]] = {}
    global_totals = {
        'rules_total': 0,
        'with_age_band': 0,
        'with_culture_region': 0,
        'with_clinical_population': 0,
        'with_traits': 0,
        'with_moderators': 0,
    }

    for ev in events:
        if ev.get('type') != 'rulegraph_v2':
            continue
        paper_id = ev.get('paper_id', '<unknown>')
        rules = ev.get('rules') or []
        rule_summaries = []
        paper_cov = coverage_by_paper.setdefault(paper_id, {
            'rules_total': 0,
            'with_age_band': 0,
            'with_culture_region': 0,
            'with_clinical_population': 0,
            'with_traits': 0,
            'with_moderators': 0,
        })
        for r in rules:
            if not isinstance(r, dict):
                continue
            effective = _apply_subject_overrides_to_rule(paper_id, r, overrides)
            scope = effective.get('subject_scope') or {}
            moderators = effective.get('subject_moderators') or []

            demo = (scope.get('demographics') or {})
            cult = (scope.get('culture') or {})
            clin = (scope.get('clinical_status') or {})
            traits = scope.get('traits_measured') or []

            has_age_band = bool(demo.get('age_band'))
            has_culture_region = bool(cult.get('region'))
            has_clinical_population = bool((clin.get('population') or '').strip())
            has_traits = any((t or {}).get('name') for t in traits)
            has_mods = bool(moderators)

            # Update coverage counters
            paper_cov['rules_total'] += 1
            global_totals['rules_total'] += 1
            if has_age_band:
                paper_cov['with_age_band'] += 1
                global_totals['with_age_band'] += 1
            if has_culture_region:
                paper_cov['with_culture_region'] += 1
                global_totals['with_culture_region'] += 1
            if has_clinical_population:
                paper_cov['with_clinical_population'] += 1
                global_totals['with_clinical_population'] += 1
            if has_traits:
                paper_cov['with_traits'] += 1
                global_totals['with_traits'] += 1
            if has_mods:
                paper_cov['with_moderators'] += 1
                global_totals['with_moderators'] += 1

            has_overrides = f"{paper_id}::{r.get('rule_id')}" in overrides
            rule_summaries.append({
                'rule_id': r.get('rule_id'),
                'rule_text': r.get('rule_text'),
                'subject_scope_summary': _summarize_scope(scope),
                'moderators_summary': _summarize_moderators(moderators),
                'subject_scope': scope,
                'subject_moderators': moderators,
                'has_overrides': has_overrides,
            })
        out_events.append({
            'paper_id': paper_id,
            'rules_count': len(rule_summaries),
            'rules': rule_summaries,
        })

    def _pct(num: int, den: int) -> float:
        return float(num) / float(den) if den else 0.0

    coverage_summary = {
        'global': {
            'rules_total': global_totals['rules_total'],
            'with_age_band': global_totals['with_age_band'],
            'with_culture_region': global_totals['with_culture_region'],
            'with_clinical_population': global_totals['with_clinical_population'],
            'with_traits': global_totals['with_traits'],
            'with_moderators': global_totals['with_moderators'],
            'pct_with_age_band': _pct(global_totals['with_age_band'], global_totals['rules_total']),
            'pct_with_culture_region': _pct(global_totals['with_culture_region'], global_totals['rules_total']),
            'pct_with_clinical_population': _pct(global_totals['with_clinical_population'], global_totals['rules_total']),
            'pct_with_traits': _pct(global_totals['with_traits'], global_totals['rules_total']),
            'pct_with_moderators': _pct(global_totals['with_moderators'], global_totals['rules_total']),
        },
        'by_paper': {},
    }
    for pid, cov in coverage_by_paper.items():
        rt = cov['rules_total']
        coverage_summary['by_paper'][pid] = {
            **cov,
            'pct_with_age_band': _pct(cov['with_age_band'], rt),
            'pct_with_culture_region': _pct(cov['with_culture_region'], rt),
            'pct_with_clinical_population': _pct(cov['with_clinical_population'], rt),
            'pct_with_traits': _pct(cov['with_traits'], rt),
            'pct_with_moderators': _pct(cov['with_moderators'], rt),
        }

    return {
        'events': out_events,
        'coverage': coverage_summary,
        'subject_vocab': _load_subject_vocab(),
    }


@router.get('/rulegraph_v2/{paper_id}', response_class=JSONResponse)
def get_rulegraph_v2_for_paper(paper_id: str, ok: bool = Depends(admin_required)):
    """Return full RuleGraph v2 rules for a single paper_id.

    This is used by the Admin UI detail modal to show the complete
    subject_scope / subject_moderators (and any other fields) for a
    specific rule.
    """
    store = get_graph_service()
    events = store.get_all_events()
    overrides = _load_subject_overrides()
    rules = []
    for ev in events:
        if ev.get('type') != 'rulegraph_v2':
            continue
        if ev.get('paper_id') != paper_id:
            continue
        for r in ev.get('rules') or []:
            if not isinstance(r, dict):
                continue
            effective = _apply_subject_overrides_to_rule(paper_id, r, overrides)
            scope_raw = r.get('subject_scope') or {}
            moderators_raw = r.get('subject_moderators') or []
            scope_eff = effective.get('subject_scope') or {}
            moderators_eff = effective.get('subject_moderators') or []
            key = f"{paper_id}::{r.get('rule_id')}"
            has_overrides = key in overrides

            rules.append({
                'rule_id': r.get('rule_id'),
                'rule_text': r.get('rule_text'),
                'subject_scope_summary': _summarize_scope(scope_eff),
                'moderators_summary': _summarize_moderators(moderators_eff),
                'subject_scope': scope_eff,
                'subject_moderators': moderators_eff,
                'subject_scope_original': scope_raw,
                'subject_moderators_original': moderators_raw,
                'has_overrides': has_overrides,
                'evidence': r.get('evidence'),
                'provenance': r.get('provenance'),
                'graph_version': r.get('graph_version'),
                'status': r.get('status'),
            })
    return {'paper_id': paper_id, 'rules_count': len(rules), 'rules': rules}



@router.post('/rulegraph_v2/export_bn', response_class=JSONResponse)

def build_rulegraph_v2_bn_export(events: list, overrides: dict | None, payload: dict | None) -> dict:
    """Pure helper that constructs a BN skeleton from rulegraph_v2 events.

    This is factored out so that tests can exercise the subject-aware BN
    pipeline without needing to spin up the full FastAPI app.
    """
    overrides = overrides or {}
    payload = payload or {}

    paper_id_filter = (payload.get('paper_id') or '').strip()
    text_filter = (payload.get('text_filter') or '').strip()
    age_filter = (payload.get('age_band') or '').strip()
    trait_filter = (payload.get('trait') or '').strip()
    text_filter_lower = text_filter.lower() if text_filter else ''

    nodes = []
    edges = set()
    filtered_rules = []
    age_bands = set()
    traits = set()
    clinical_pops = set()
    culture_regions = set()
    self_construals = set()
    education_bands = set()
    moderator_keys = set()
    paper_ids = set()

    for ev in events:
        if ev.get('type') != 'rulegraph_v2':
            continue
        paper_id = ev.get('paper_id') or '<unknown>'
        if paper_id_filter and paper_id != paper_id_filter:
            continue
        for r in ev.get('rules') or []:
            if not isinstance(r, dict):
                continue
            effective = _apply_subject_overrides_to_rule(paper_id, r, overrides)
            scope = effective.get('subject_scope') or {}
            moderators = effective.get('subject_moderators') or []
            scope_summary = _summarize_scope(scope)
            moderators_summary = _summarize_moderators(moderators)
            text = (r.get('rule_text') or '') + ' ' + scope_summary + ' ' + moderators_summary

            if text_filter_lower and text_filter_lower not in text.lower():
                continue

            demo = (scope.get('demographics') or {})
            band = demo.get('age_band') or ''
            if age_filter and (not band or band != age_filter):
                continue

            trait_names = []
            for t in scope.get('traits_measured') or []:
                name = (t or {}).get('name')
                if name:
                    trait_names.append(name)
                    traits.add(name)
            if trait_filter and trait_filter not in trait_names:
                continue

            pop = (scope.get('clinical_status') or {}).get('population') or ''
            region = (scope.get('culture') or {}).get('region') or ''
            self_construal = (scope.get('culture') or {}).get('self_construal_profile') or ''
            edu_band = demo.get('education_band') or ''

            rule_id = r.get('rule_id') or ''
            rule_node_id = f'rule:{paper_id}:{rule_id}'

            filtered_rules.append({
                'paper_id': paper_id,
                'rule_id': rule_id,
                'rule_text': r.get('rule_text'),
                'subject_scope': scope,
                'subject_moderators': moderators,
                'scope_summary': scope_summary,
                'moderators_summary': moderators_summary,
                'rule_node_id': rule_node_id,
            })
            paper_ids.add(paper_id)

            if band:
                age_bands.add(band)
                edges.add((f'age_band:{band}', rule_node_id, 'subject_scope'))
            if pop:
                clinical_pops.add(pop)
                edges.add((f'clinical_pop:{pop}', rule_node_id, 'subject_scope'))
            if region:
                culture_regions.add(region)
                edges.add((f'culture_region:{region}', rule_node_id, 'subject_scope'))
            if self_construal:
                self_construals.add(self_construal)
                edges.add((f'self_construal:{self_construal}', rule_node_id, 'subject_scope'))
            if edu_band:
                education_bands.add(edu_band)
                edges.add((f'education_band:{edu_band}', rule_node_id, 'subject_scope'))
            for name in trait_names:
                edges.add((f'trait:{name}', rule_node_id, 'subject_scope'))

            for m in moderators:
                dim = (m or {}).get('dimension')
                attr = (m or {}).get('attribute')
                if not dim or not attr:
                    continue
                key = f'{dim}|{attr}'
                moderator_keys.add(key)
                edges.add((f'mod:{key}', rule_node_id, 'subject_moderator'))

    for band in sorted(age_bands):
        nodes.append({
            'id': f'age_band:{band}',
            'type': 'subject_age_band',
            'label': band,
        })
    for name in sorted(traits):
        nodes.append({
            'id': f'trait:{name}',
            'type': 'subject_trait',
            'label': name,
        })
    for pop in sorted(clinical_pops):
        nodes.append({
            'id': f'clinical_pop:{pop}',
            'type': 'subject_clinical_pop',
            'label': pop,
        })
    for region in sorted(culture_regions):
        nodes.append({
            'id': f'culture_region:{region}',
            'type': 'subject_culture_region',
            'label': region,
        })
    for sc in sorted(self_construals):
        nodes.append({
            'id': f'self_construal:{sc}',
            'type': 'subject_self_construal',
            'label': sc,
        })
    for edu in sorted(education_bands):
        nodes.append({
            'id': f'education_band:{edu}',
            'type': 'subject_education_band',
            'label': edu,
        })
    for key in sorted(moderator_keys):
        nodes.append({
            'id': f'mod:{key}',
            'type': 'subject_moderator',
            'label': key,
        })

    for rule in filtered_rules:
        nodes.append({
            'id': rule['rule_node_id'],
            'type': 'rule',
            'label': rule['rule_text'] or rule['rule_node_id'],
        })

    edge_list = [{'from': s, 'to': t, 'type': kind} for (s, t, kind) in sorted(edges)]

    result = {
        'bn_version': BN_EXPORT_VERSION,
        'generator': BN_EXPORT_GENERATOR,
        'filters': {
            'paper_id': paper_id_filter or None,
            'text_filter': text_filter or None,
            'age_band': age_filter or None,
            'trait': trait_filter or None,
        },
        'meta': {
            'rules_count': len(filtered_rules),
            'papers': sorted(paper_ids),
        },
        'nodes': nodes,
        'edges': edge_list,
        'rules': filtered_rules,
    }
    return result


@router.post('/rulegraph_v2/export_bn', response_class=JSONResponse)
def export_rulegraph_v2_bn(payload: dict, ok: bool = Depends(admin_required)):
    """Export a BN skeleton from the current RuleGraph v2 store."""
    store = get_graph_service()
    events = store.get_all_events()
    overrides = _load_subject_overrides()
    export = build_rulegraph_v2_bn_export(events, overrides, payload)
    return JSONResponse(content=export)


@router.post('/rulegraph_v2/{paper_id}/{rule_id}/subject', response_class=JSONResponse)
def update_rulegraph_v2_subject(paper_id: str, rule_id: str, payload: dict, ok: bool = Depends(admin_required)):
    """Update curated subject info (scope + moderators) for a single rule.

    The payload is expected to contain optional `subject_scope` and
    `subject_moderators` entries. If both are empty, any existing override
    for this rule is removed.
    """
    overrides = _load_subject_overrides()
    key = f"{paper_id}::{rule_id}"
    scope = payload.get('subject_scope') or {}
    moderators = payload.get('subject_moderators') or []

    if not scope and not moderators:
        overrides.pop(key, None)
    else:
        overrides[key] = {
            'subject_scope': scope,
            'subject_moderators': moderators,
        }
    _save_subject_overrides(overrides)
    return {'status': 'ok', 'paper_id': paper_id, 'rule_id': rule_id}

@router.post('/bn_playground/summary', response_class=JSONResponse)
def bn_playground_summary(payload: dict, ok: bool = Depends(admin_required)):
    """Summarize a BN export JSON for the BN Playground UI.

    Expects a payload with:
      - export_json: stringified JSON produced by /rulegraph_v2/export_bn

    Returns a compact summary of:
      - node type counts
      - outcome family distribution
      - top subject-parent type patterns
    """
    raw = (payload or {}).get('export_json')
    if not raw:
        raise HTTPException(status_code=400, detail='export_json is required')
    try:
        export = json.loads(raw)
    except Exception:
        raise HTTPException(status_code=400, detail='export_json must be valid JSON')

    nodes = export.get('nodes') or []
    rules = export.get('rules') or []
    edges = export.get('edges') or []

    # Node type counts
    node_counts = defaultdict(int)
    for n in nodes:
        ntype = (n or {}).get('type') or 'unknown'
        node_counts[ntype] += 1

    # Build index for parents (reuse bn_suggest_outcome_templates helpers)
    nodes_by_id, edges_by_to = bn_suggest_outcome_templates._build_index(export)

    family_counts = defaultdict(int)
    family_examples = {}
    pattern_counts = defaultdict(int)

    for r in rules:
        paper_id = r.get('paper_id') or '<unknown>'
        rid = r.get('rule_id') or ''
        text_bits = [
            r.get('rule_text') or '',
            r.get('subject_scope_summary') or '',
            r.get('moderators_summary') or '',
        ]
        joined = ' '.join(text_bits)
        family = bn_suggest_outcome_templates._heuristic_outcome_family(joined)
        family_counts[family] += 1

        rule_node_id = bn_suggest_outcome_templates._rule_node_id(r)
        parent_info = bn_suggest_outcome_templates._collect_parents_for_rule(
            rule_node_id, nodes_by_id, edges_by_to
        )

        combo = tuple(sorted(parent_info.get('subject_parent_types') or []))
        pattern_counts[combo] += 1

        if family not in family_examples:
            family_examples[family] = {
                'paper_id': paper_id,
                'rule_id': rid,
                'rule_text': (r.get('rule_text') or '').strip(),
                'subject_parent_ids': parent_info.get('subject_parent_ids') or [],
                'moderator_parent_ids': parent_info.get('moderator_parent_ids') or [],
                'recommended_parent_nodes': parent_info.get('recommended_parent_nodes') or [],
            }

    # Outcome families summary
    outcome_families = []
    for fam, count in sorted(family_counts.items(), key=lambda kv: kv[1], reverse=True):
        outcome_families.append({
            'family': fam,
            'count': count,
            'example': family_examples.get(fam),
        })

    # Top subject-parent type patterns
    subject_parent_type_patterns_top = []
    for combo, count in sorted(pattern_counts.items(), key=lambda kv: kv[1], reverse=True)[:10]:
        subject_parent_type_patterns_top.append({
            'subject_parent_types': list(combo),
            'count': count,
        })

    result = {
        'bn_version': export.get('bn_version'),
        'rules_count': len(rules),
        'node_counts': dict(node_counts),
        'outcome_families': outcome_families,
        'subject_parent_type_patterns_top': subject_parent_type_patterns_top,
    }
    return JSONResponse(content=result)


@router.post('/bn_playground/export_pack')
def bn_playground_export_pack(payload: dict, ok: bool = Depends(admin_required)):
    """Generate a zipped CSV pack (nodes/edges/rules/outcome templates)
    from a BN export JSON.

    Input payload:
      - export_json: stringified JSON produced by /rulegraph_v2/export_bn

    Returns:
      - application/zip response containing:
        - nodes.csv
        - edges.csv
        - rules.csv
        - bn_outcome_templates.csv
    """
    raw = (payload or {}).get('export_json')
    if not raw:
        raise HTTPException(status_code=400, detail='export_json is required')
    try:
        export = json.loads(raw)
    except Exception:
        raise HTTPException(status_code=400, detail='export_json must be valid JSON')

    # Use a temporary directory to generate CSV files via existing helpers.
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        csv_dir = tmp_path / 'csv'
        csv_dir.mkdir(parents=True, exist_ok=True)

        # Generate core CSVs
        bn_export_to_csv.write_nodes_csv(export, csv_dir)
        bn_export_to_csv.write_edges_csv(export, csv_dir)
        bn_export_to_csv.write_rules_csv(export, csv_dir)

        # Outcome templates CSV
        out_templates = csv_dir / 'bn_outcome_templates.csv'
        bn_suggest_outcome_templates.write_outcome_templates_csv(export, out_templates)

        # Pack into an in-memory ZIP
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
            for name in ['nodes.csv', 'edges.csv', 'rules.csv', 'bn_outcome_templates.csv']:
                p = csv_dir / name
                if p.is_file():
                    zf.write(p, name)
        buf.seek(0)

    headers = {
        'Content-Disposition': 'attachment; filename="bn_export_pack.zip"'
    }
    return Response(content=buf.read(), media_type='application/zip', headers=headers)
