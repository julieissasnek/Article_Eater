
# Article Eater v20.7.9 — RuleGraph v2 in-panel rule search

## Overview

This sprint makes the RuleGraph v2 / subject panel in the Admin Control
Room more useful for scientific inspection by adding **rule-level
filters**:

- Free-text search over rule text, subject_scope summary, and moderators
  summary.
- Age-band filter derived from subject_scope.demographics.age_band.
- Trait filter derived from subject_scope.traits_measured[].name.

These combine with the existing paper_id filter and detail modal, so you
can quickly focus on, say, *all rules involving young adults with SPS*
or *all rules mentioning "prospect-refuge"*.

## Changes

1. **Admin GUI (HTML) — additional filter controls**

   - `src/gui/templates/admin.html`:
       - In `#tab-rulegraphv2`, below the paper filter row, a new row of
         controls:

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
         </div>
         ```

       - The existing paper filter + Reload row remains unchanged and
         sits above this new filter row.

2. **Admin GUI JS — rule-level filters + integrated rendering**

   - `src/gui/static/admin.js` (RuleGraph v2 section):

       - Still uses a cached `rg2Events` array (data from
         `GET /api/admin/rulegraph_v2`).

       - New helper functions:

         ```js
         function collectAgeBands(events){{ ... }}
         function collectTraits(events){{ ... }}
         ```

         - `collectAgeBands` walks all rules and pulls distinct
           `rule.subject_scope.demographics.age_band`.
         - `collectTraits` walks all rules and pulls distinct
           `rule.subject_scope.traits_measured[].name`.

       - New filter-population functions:

         ```js
         function populateAgeBandFilter(events){{ ... }}
         function populateTraitFilter(events){{ ... }}
         ```

         - Both clear their `<select>` elements, add an "All ..." opt,
           then add sorted bands/traits.
         - Preserve the current selection when possible.

       - Updated `loadRulegraphV2()`:

         ```js
         async function loadRulegraphV2(){{
           const data = await getJ('/api/admin/rulegraph_v2');
           rg2Events = data.events || [];
           populatePaperFilter(rg2Events);
           populateAgeBandFilter(rg2Events);
           populateTraitFilter(rg2Events);
           renderRulegraphSummary(rg2Events);
         }}
         ```

       - New `ruleMatchesFilters(ev, rule)` function applies the full
         filter state to a single rule:

         ```js
         function ruleMatchesFilters(ev, rule){{
           // paperId filter
           // text search across rule_text + subject_scope_summary + moderators_summary
           // age band filter via rule.subject_scope.demographics.age_band
           // trait filter via rule.subject_scope.traits_measured[].name
         }}
         ```

         - Paper filter: if set and `ev.paper_id` != filter → reject.
         - Text search: case-insensitive substring over:
           `rule.rule_text + subject_scope_summary + moderators_summary`.
         - Age band filter: compares against `scope.demographics.age_band`.
         - Trait filter: requires at least one trait name exactly
           matching the selected trait.

       - Updated `renderRulegraphSummary(events)`:

         ```js
         function renderRulegraphSummary(events){{
           const container = $('#rulegraphV2Summary');
           ...
           const visibleEvents = [];

           (events || []).forEach(ev => {{
             const keptRules = [];
             (ev.rules || []).forEach(rule => {{
               if (ruleMatchesFilters(ev, rule)){{
                 keptRules.push(rule);
               }}
             }});
             if (keptRules.length){{
               visibleEvents.push({{
                 paper_id: ev.paper_id,
                 rules_count: keptRules.length,
                 rules: keptRules,
               }});
             }}
           }});

           if (!visibleEvents.length){{
             container.textContent = 'No rules match the current filters.';
             return;
           }}

           // For each event, render card + up to 5 kept rules, each
           // with Details button (unchanged).
         }}
         ```

         - So now the filter logic works at **rule** granularity, not
           just event (paper) granularity.
         - Events that have no rules matching the active filters are
           dropped entirely from the view.

       - Updated filter bindings:

         ```js
         function bindRulegraphFilters(){{
           const paperSel = $('#rg2PaperFilter');
           const searchInput = $('#rg2RuleSearch');
           const ageSel = $('#rg2AgeBandFilter');
           const traitSel = $('#rg2TraitFilter');

           if (paperSel){{
             paperSel.addEventListener('change', () => {{
               renderRulegraphSummary(rg2Events);
             }});
           }}
           if (searchInput){{
             searchInput.addEventListener('input', () => {{
               renderRulegraphSummary(rg2Events);
             }});
           }}
           if (ageSel){{
             ageSel.addEventListener('change', () => {{
               renderRulegraphSummary(rg2Events);
             }});
           }}
           if (traitSel){{
             traitSel.addEventListener('change', () => {{
               renderRulegraphSummary(rg2Events);
             }});
           }}
         }}
         ```

         - Called at the end of the RuleGraph v2 section alongside
           `bindRulegraphModal()`.

       - The existing detail modal logic (`openRuleDetail`, modal show/hide)
         is preserved unchanged and remains wired to the **Details**
         button per rule.

3. **Backend**

   - `src/services/admin_service.py` is unchanged from v20.7.8 for this
     sprint.
   - All new behaviour is implemented on the client side using the
     existing `GET /api/admin/rulegraph_v2` and
     `GET /api/admin/rulegraph_v2/{{paper_id}}` endpoints.

## Compatibility

- All changes are additive and UI-only. API surfaces from v20.7.8 are
  unchanged.
- If there are no age bands or trait names present in the underlying
  data, the corresponding filters simply contain only their "All ..."
  options but remain functional.
- Free-text search is case-insensitive and operates over plain strings,
  so it is robust to minor changes in the underlying rule structure as
  long as `rule_text`, `subject_scope_summary`, and
  `moderators_summary` remain present.

