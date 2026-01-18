
# Article Eater v20.7.15 — BN Export CSV Pack from BN Playground

## Overview

This sprint extends the BN Playground so that, in addition to showing a
text summary, it can generate and download a compact zipped CSV pack
for BN-Maker:

- nodes.csv
- edges.csv
- rules.csv
- bn_outcome_templates.csv

The pack is generated server-side using the same helpers as the CLI
tools and is keyed to whatever BN export JSON you load into the
Playground.

## 1. Backend: export_pack endpoint

- **File:** src/services/admin_service.py
- **Endpoint:** POST /api/admin/bn_playground/export_pack
- **Auth:** admin_required

Input payload:

- export_json: stringified JSON produced by
  /api/admin/rulegraph_v2/export_bn.

Behaviour:

1. Parses export_json into a Python dict.
2. Creates a temporary directory.
3. Uses bn_export_to_csv.{write_nodes_csv, write_edges_csv,
   write_rules_csv} to generate nodes.csv, edges.csv, and rules.csv.
4. Uses bn_suggest_outcome_templates.write_outcome_templates_csv to
   generate bn_outcome_templates.csv.
5. Packs the four CSVs into an in-memory ZIP and returns it as
   application/zip with Content-Disposition: attachment.

## 2. Frontend: BN Playground "Download CSV pack" button

- **Template:** src/gui/templates/admin.html
- **Script:** src/gui/static/admin.js

UI:

- In the BN Playground tab, next to "Analyze export", a new button
  appears:

  - "Download CSV pack" (id: bnPlaygroundDownload).

JS logic:

- In bindBnPlayground():

  - Stores the uploaded BN export JSON text in
    bnPlaygroundExportText.
  - "Analyze export" behaviour remains as in v20.7.14.
  - "Download CSV pack":
    - POSTs export_json to /api/admin/bn_playground/export_pack.
    - Receives application/zip as a blob.
    - Triggers a download as bn_export_pack.zip using a temporary
      <a download> element.
    - Writes status messages to the BN Playground output panel.

This gives Admins a fully in-GUI path from RuleGraph v2 to
BN-Maker-ready CSVs, without needing to run the CLI tools manually.
