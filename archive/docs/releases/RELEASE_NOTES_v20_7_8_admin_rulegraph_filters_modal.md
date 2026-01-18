# Article Eater v20.7.8 — RuleGraph v2 filtering + detail modal

## Overview

This sprint enhances the Admin Control Room's RuleGraph v2 / subject
panel view with:

- A **paper_id filter** drop-down so admins can focus on rules for a
  particular paper.
- A **detail modal** that shows the full JSON payload for a single rule,
  including subject_scope, subject_moderators, and evidence/provenance.

The underlying extraction pipeline and JSONL store are unchanged.

## Changes

1. **Admin GUI (HTML & CSS)**

   - `src/gui/templates/admin.html`:
       - In the `#tab-rulegraphv2` section:
           - Replaced the simple Reload button with a small control bar:
             - `<select id="rg2PaperFilter">` with an "All papers" option.
             - A **Reload** button (`#reloadRulegraphV2`).
           - This allows the frontend to populate the filter with all
             known paper IDs and then re-render cards for a selected
             paper only.
       - Added a **detail modal** to the bottom of the page:
         - `#rg2DetailModal` containing:
             - `#rg2ModalTitle` (rule_id @ paper_id).
             - `#rg2ModalClose` button.
             - `#rg2ModalBody` (`<pre>` showing JSON-formatted rule data).
       - Extended inline CSS with modal styles:
           - `.modal`, `.modal.hidden`, `.modal-backdrop`,
             `.modal-content`, `.modal-header`, `.modal-body`.

2. **Admin GUI JS: RuleGraph v2 filtering + modal**

   - `src/gui/static/admin.js`:
       - Introduced `rg2Events` as an in-memory cache of the
         `GET /api/admin/rulegraph_v2` response.
       - Added `populatePaperFilter(events)`:
           - Extracts unique paper IDs from events.
           - Populates `#rg2PaperFilter` options ("All papers" + IDs).
       - Updated `renderRulegraphSummary(events)`:
           - Reads the current `#rg2PaperFilter` value.
           - If a paper ID is selected, filters `events` down to only
             those with that `paper_id`.
           - If filter yields no events, shows a short explanatory
             message.
           - For each visible event, renders a card as before, but now
             each rule includes a **Details** button that calls
             `openRuleDetail(paperId, ruleId)`.
       - Updated `loadRulegraphV2()`:
           - Fetches `/api/admin/rulegraph_v2`.
           - Stores `data.events` in `rg2Events`.
           - Calls `populatePaperFilter(rg2Events)` then
             `renderRulegraphSummary(rg2Events)`.
       - Added `openRuleDetail(paperId, ruleId)`:
           - Calls `GET /api/admin/rulegraph_v2/{paper_id}`.
           - Locates the matching rule by `rule_id`.
           - Populates `#rg2ModalTitle` and `#rg2ModalBody` with a
             pretty-printed `JSON.stringify(rule, null, 2)`.
           - Shows `#rg2DetailModal` by removing `.hidden`.
       - Added `bindRulegraphFilter()`:
           - On change of `#rg2PaperFilter`, re-renders cards using the
             cached `rg2Events`.
       - Added `bindRulegraphModal()`:
           - Wires `#rg2ModalClose` to hide the modal.
           - Hides the modal when clicking on the backdrop.
           - Hides the modal on `Escape` keypress.
       - Initialisation:
           - After wiring reload button, it calls both
             `bindRulegraphFilter()` and `bindRulegraphModal()`.

3. **Admin API: per-paper RuleGraph v2 detail endpoint**

   - `src/services/admin_service.py`:
       - Added new endpoint:

         ```python
         @router.get('/rulegraph_v2/{paper_id}', response_class=JSONResponse)
         def get_rulegraph_v2_for_paper(paper_id: str, ok: bool = Depends(admin_required)):
             ...
         ```

       - Behaviour:
           - Uses `get_graph_service().get_all_events()` and filters for:
               - `event['type'] == 'rulegraph_v2'`
               - `event['paper_id'] == paper_id`
           - Flattens matching rules into a list with:
               - `rule_id`
               - `rule_text`
               - `subject_scope_summary`
               - `moderators_summary`
               - full `subject_scope`
               - full `subject_moderators`
               - `evidence`
               - `provenance`
               - `graph_version`
               - `status`
           - Returns:

             ```json
             {
               "paper_id": "<paper_id>",
               "rules_count": <int>,
               "rules": [ ... ]
             }
             ```

       - The existing `GET /api/admin/rulegraph_v2` endpoint remains
         unchanged; it still returns a compact, multi-paper summary.

## Compatibility

- All changes are additive; no existing endpoints or GUI affordances
  were removed.
- The filter and modal are purely read-only views over existing
  `rulegraph_v2` events in `data/graph.jsonl`.
- The new endpoint path is:
  - `GET /api/admin/rulegraph_v2/{paper_id}`

