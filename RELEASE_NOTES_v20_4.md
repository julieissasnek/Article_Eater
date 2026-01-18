
# v20.4 — Functional Worker, CI, Interactions, Policy Enforcement

- Implemented L0→L2 pipeline with real services (Semantic Scholar search, clustering, 7-panel extraction via policy-selected LLM).
- Added CI columns support (findings table) already present in 015b; kept intact.
- New policy loader and strict non-admin Gemini usage for panels.
- Rule interaction analysis + review API.
- Profile API-keys endpoint with minimal masking.
- CI v3 workflow (pytest). No deletions; all changes additive or in-place edits.