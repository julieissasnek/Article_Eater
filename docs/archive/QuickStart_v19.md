# Quick Start


## Policy configuration (LLM-required, Gemini-first)
Edit `config/app.policy.json` to control provider order and eager behavior.
With `require_llm_for_panels=true` and `non_admin_fallback_allowed=false`, non-admin users must store an API key before a 7‑panel can be created (see `frontend/keys.html`). Admin can bypass by running jobs with `--user-id admin`.