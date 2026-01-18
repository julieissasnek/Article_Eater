
# Article Eater v20.7.10 — RuleGraph v2 BN skeleton export

## Overview

This sprint adds a **BN export** affordance to the Admin Control Room's
RuleGraph v2 / subject panel.

- A new button, **"Export BN (JSON)"**, appears next to the rule-level
  filters.
- When clicked, the backend re-applies the current filter state
  (paper_id, free-text search, age band, trait) and returns a **minimal
  BN skeleton**:
    - subject attribute nodes (age bands, traits)
    - rule nodes
    - edges from subject attributes to rules
    - plus the full filtered rule payloads, ready for downstream BN
      tooling.

No CPDs or outcome nodes are constructed yet; this is a structural,
subject-keyed skeleton suitable as a starting point for BN builder
scripts.

## Changes

1. **Admin GUI (HTML) — Export button**

   - `src/gui/templates/admin.html`:

       - In the RuleGraph v2 tab's second filter row (search, age band,
         trait), we add an **Export BN (JSON)** button:

         ```html
         <div style="margin-bottom:.5rem;">
           <label for="rg2RuleSearch">Search:</label>
           <input id="rg2RuleSearch" type="text"
                  placeholder="Search rule text, scope, traits, age band..."
                  style="min-width:220px;">
           <label for="rg2AgeBandFilter" style="margin-left:.5rem;">Age band:</label>
           <select id="rg2AgeBandFilter">
             <option value="">All age bands</option>
           </select>
           <label for="rg2TraitFilter" style="margin-left:.5rem;">Trait:</label>
           <select id="rg2TraitFilter">
             <option value="">All traits</option>
           </select>
           <button id="rg2ExportBn" class="btn" style="margin-left:.5rem;">Export BN (JSON)</button>
         </div>
         ```

2. **Admin GUI JS — BN export wiring**

   - `src/gui/static/admin.js` (RuleGraph v2 section):

       - The existing rule-level filters and rendering logic from
         v20.7.9 are preserved.

       - New function `bindRulegraphExport()`:

         ```js
         function bindRulegraphExport(){
           const btn = $('#rg2ExportBn');
           if (!btn) return;
           btn.addEventListener('click', async () => {
             try{
               const paperSel = $('#rg2PaperFilter');
               const searchInput = $('#rg2RuleSearch');
               const ageSel = $('#rg2AgeBandFilter');
               const traitSel = $('#rg2TraitFilter');

               const payload = {
                 paper_id: paperSel ? (paperSel.value || '') : '',
                 text_filter: searchInput ? (searchInput.value || '') : '',
                 age_band: ageSel ? (ageSel.value || '') : '',
                 trait: traitSel ? (traitSel.value || '') : '',
               };

               const res = await fetch('/api/admin/rulegraph_v2/export_bn', {
                 method: 'POST',
                 headers: {
                   'Content-Type': 'application/json',
                 },
                 credentials: 'same-origin',
                 body: JSON.stringify(payload),
               });
               if (!res.ok){
                 throw new Error('Export failed with status ' + res.status);
               }
               const data = await res.json();
               const blob = new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'});
               const url = URL.createObjectURL(blob);
               const a = document.createElement('a');
               const ts = new Date().toISOString().replace(/[:.]/g, '-');
               a.href = url;
               a.download = 'article_eater_bn_export_' + ts + '.json';
               document.body.appendChild(a);
               a.click();
               document.body.removeChild(a);
               URL.revokeObjectURL(url);
             } catch(err){
               console.error(err);
               alert('Failed to export BN skeleton: ' + err);
             }
           });
         }
         ```

       - At the end of the RuleGraph v2 section, after wiring the
         reload button and the existing filter + modal bindings, we
         now call:

         ```js
         const reloadRG2 = $('#reloadRulegraphV2');
         if (reloadRG2) reloadRG2.addEventListener('click', () => {
           loadRulegraphV2().catch(console.error);
         });
         bindRulegraphFilters();
         bindRulegraphModal();
         bindRulegraphExport();
         ```

       - The rest of the RuleGraph v2 JS (collecting bands/traits,
         ruleMatchesFilters, renderRulegraphSummary, loadRulegraphV2,
         openRuleDetail) remains as in v20.7.9.

3. **Admin API — BN skeleton export endpoint**

   - `src/services/admin_service.py`:

       - New endpoint:

         ```python
         @router.post('/rulegraph_v2/export_bn', response_class=JSONResponse)
         def export_rulegraph_v2_bn(payload: dict, ok: bool = Depends(admin_required)):
             ...
         ```

       - Filter handling:

         - Extracts filters from the JSON payload:

           ```python
           paper_id_filter = (payload or {}).get('paper_id') or ''
           text_filter = (payload or {}).get('text_filter') or ''
           age_filter = (payload or {}).get('age_band') or ''
           trait_filter = (payload or {}).get('trait') or ''
           ```

         - Uses `get_graph_service().get_all_events()` and iterates
           over `type == 'rulegraph_v2'` events only.

         - For each rule:

             - Builds `scope = rule['subject_scope']` (default `{}`)
               and `moderators = rule['subject_moderators']` (default
               `[]`).

             - Computes text summaries using the existing helpers:

               ```python
               scope_summary = _summarize_scope(scope)
               moderators_summary = _summarize_moderators(moderators)
               text = (rule_text or '') + ' ' + scope_summary + ' ' + moderators_summary
               ```

             - Applies the **same conceptual filters** as the frontend:

               - `paper_id` (if filter set)
               - free-text substring over the combined `text`
               - `age_band` via `subject_scope.demographics.age_band`
               - trait name via `subject_scope.traits_measured[].name`

             - If a rule passes all filters, it is added to
               `filtered_rules` along with its core payload (rule_id,
               paper_id, rule_text, subject_scope, subject_moderators,
               summaries, evidence, provenance, graph_version, status).

             - `age_bands`, `traits`, and `paper_ids` sets are updated
               based on the rule's subject_scope.

       - BN skeleton construction:

         - Subject attribute nodes:

           ```python
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
           ```

         - Rule nodes:

           ```python
           node_id = f'rule:{paper_id}:{rid}' if rid else f'rule:{paper_id}'
           nodes.append({
               'id': node_id,
               'type': 'rule',
               'label': rid or 'rule',
               'paper_id': paper_id,
           })
           ```

         - Edges from subject attributes to rules:

           ```python
           if band:
               edges.add(('age_band:' + band, node_id, 'subject_scope'))
           for t in scope.get('traits_measured') or []:
               name = (t or {}).get('name')
               if name:
                   edges.add(('trait:' + name, node_id, 'subject_scope'))
           ```

         - The `edges` set is then converted into a sorted list of
           edge dicts:

           ```python
           edge_list = []
           for src, dst, etype in sorted(edges):
               edge_list.append({
                   'from': src,
                   'to': dst,
                   'type': etype,
               })
           ```

       - Final response payload:

         ```python
         result = {
             'bn_version': '0.1',
             'generator': 'article_eater_rulegraph_v2',
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
         ```

         - This is the JSON object that is downloaded by the frontend
           as `article_eater_bn_export_<timestamp>.json`.

## Compatibility

- All changes are additive:

  - Existing endpoints (`/api/admin/rulegraph_v2` and
    `/api/admin/rulegraph_v2/{{paper_id}}`) are unchanged.
  - Existing RuleGraph v2 UI behaviour from v20.7.9 is preserved.

- The BN skeleton export is read-only and only touches the in-memory
  view of `data/graph.jsonl` via `get_graph_service().get_all_events()`.
  No mutations are performed.

- If filters are very restrictive and match no rules, the export will
  still succeed but return an object with `rules_count == 0` and empty
  `nodes` and `edges`.

