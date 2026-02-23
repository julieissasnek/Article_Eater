# Article Eater Streamlit Control Room

This document describes the lightweight Streamlit GUI that lives at
`scripts/ae_streamlit_control_room.py`.

## Purpose

The Streamlit app provides a multi‑persona, read‑only control room on top of
the Article Eater backend. It is intended for:

- **Scientists** who want a quick Causal Explorer for the BN / RuleGraph.
- **Librarians / evidence curators** who will eventually use the Evidence
  Library view.
- **Engineers / admins** who want a thin facade over pipeline health and
  metrics.

## Running the app

From the repository root, after installing dependencies from
`requirements.txt`:

```bash
export AE_BASE_URL="http://localhost:8000"      # or wherever your backend runs
export AE_ROLES="scientist,librarian,engineer"  # gate visible personas
scripts/run_control_room.sh
```

The UI port is read from `contracts/ports.json` (see `ports.ui.host`).

## Personas and permissions

The personas are:

- **Overview (Admin)** – costs, API choices, high‑level status.
- **Causal Explorer (Scientist)** – interactive BN export with subject lenses.
- **Evidence Library** – article‑centric search scaffold.
- **Pipeline Health (Engineer)** – pipeline / governance scaffold.

Visibility is controlled by the `AE_ROLES` environment variable. For example:

- `AE_ROLES="scientist"` → only Causal Explorer.
- `AE_ROLES="admin,engineer"` → Overview + Pipeline Health.
- `AE_ROLES="scientist,librarian,engineer,admin"` → all personas.

In production, this env‑var‑based gating should be replaced with the real
authentication / RBAC layer used by your deployment.
