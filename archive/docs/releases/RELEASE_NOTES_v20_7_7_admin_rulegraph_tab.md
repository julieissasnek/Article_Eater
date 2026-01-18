# Article Eater v20.7.7 — Admin RuleGraph v2 / Subject Panel View

## Overview

This sprint wires a minimal, subject-aware RuleGraph v2 view into the
Admin Control Room, alongside the existing Prompt Workshop and
Confidence Engine tabs. It also formalises the prompt update endpoint
used by the admin GUI.

## Changes

1. **Admin GUI: new "Subject Rules (RuleGraph v2)" tab**

   - Edited `src/gui/templates/admin.html`:
       - Added a new tab header button:
         - **Subject Rules (RuleGraph v2)**
       - Added a new section:
         - `#tab-rulegraphv2` containing:
             - A short description of the subject-aware RuleGraph v2
               data stored in `data/graph.jsonl`.
             - A **Reload** button (`#reloadRulegraphV2`).
             - A container `#rulegraphV2Summary` that will display a
               list of subject-aware rule cards.
       - Added minimal inline CSS for:
         - `.rg2-card` rule cards,
         - `.rg2-meta` metadata line,
         - `.rg2-rule` rows,
         - `.rg2-rule-code` monospace summaries of scope and moderators.

2. **Admin GUI JS: rewritten `admin.js` with RuleGraph v2 support**

   - Replaced `src/gui/static/admin.js` with a clean, explicit
     implementation that supports:
       - Tab switching via `data-tab` attributes.
       - **Prompt Workshop**:
           - `GET /api/admin/prompts` to populate `#promptSelect`.
           - `POST /api/admin/prompts/update` to save the currently
             selected prompt (`name`, `content`).
       - **Confidence Engine**:
           - `GET /api/admin/confidence` to load the nested confidence
             configuration.
           - Recursive rendering of numeric values into labeled
             `<input type="number">` controls.
           - Reconstruction of a nested config object from
             `data-path` attributes.
           - `POST /api/admin/confidence/update` to persist edited
             weights.
       - **RuleGraph v2 / Subject Panel**:
           - `GET /api/admin/rulegraph_v2` to fetch a compact summary of
             all `rulegraph_v2` events.
           - Rendering logic that, for each event, shows:
               - `paper_id`.
               - Count of rules.
               - Up to 5 rules, each with:
                   - the rule text,
                   - a one-line **subject_scope** summary,
                   - a one-line **moderators** summary.
       - Initialisation:
           - On page load, the script calls:
               - `loadPrompts()` if `#promptSelect` exists.
               - `loadConfidence()` if `#confEditor` exists.
               - `loadRulegraphV2()` if `#rulegraphV2Summary` exists.

3. **Admin API: prompt update + RuleGraph v2 summary endpoint**

   - Extended `src/services/admin_service.py`:
       - Added imports:
           - `from collections import defaultdict`
           - `from src.services.service_locator import get_graph_service`
       - New endpoint:
           - `POST /api/admin/prompts/update`
               - Payload: `{"name": "...", "content": "..."}`
               - Writes `prompts/<name>` with the given content.
       - Helper functions:
           - `_summarize_scope(scope: dict) -> str`:
               - Builds a human-readable summary from:
                   - demographics (age_band, education_band, sample_size),
                   - culture (region, countries),
                   - clinical_status (population),
                   - traits_measured (trait names).
           - `_summarize_moderators(moderators: list) -> str`:
               - Groups moderators by `dimension` and lists distinct
                 attributes per dimension.
       - New endpoint:
           - `GET /api/admin/rulegraph_v2`
               - Uses `get_graph_service().get_all_events()` to collect
                 events.
               - Filters for `type == "rulegraph_v2"`.
               - For each such event, returns:
                   - `paper_id`
                   - `rules_count`
                   - `rules`: list of rule dicts with:
                       - `rule_id`
                       - `rule_text`
                       - `subject_scope_summary`
                       - `moderators_summary`
                       - full `subject_scope`
                       - full `subject_moderators`.

## Compatibility

- No existing public endpoints were removed or renamed.
- The new endpoints are additive:
    - `POST /api/admin/prompts/update`
    - `GET /api/admin/rulegraph_v2`
- The admin HTML and JS remain single-page and self-contained.
