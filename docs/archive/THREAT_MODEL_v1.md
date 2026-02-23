# Threat Model v1 – Article Eater

This document provides a first-pass threat model for Article Eater. It is not a
formal security proof, but a shared mental model of what we are protecting, who
we are protecting it from, and how.

---

## 1. Roles and goals

### Roles

- **Admin**
  - Manages system-level settings, LLM keys, deployment configuration.
  - Can see and modify all ingested papers and derived artefacts.

- **Researcher**
  - Ingests papers, reviews Seven-Panel outputs, edits findings and rules.
  - Can see all research data but does not manage secrets or system
    configuration.

- **Student**
  - Uses curated views (e.g., exercises, limited rule editing).
  - May ingest limited paper sets for assignments, but with constrained access.

- **Guest**
  - Read-only access to selected demo content.
  - No access to admin or researcher functions.

### Assets to protect

- Ingested paper content (which may be pre-publication or sensitive).
- Derived research artefacts (graph store, calibrated confidence scores, user
  rules).
- LLM credentials and configuration.
- User accounts and sessions.

---

## 2. Adversaries

- **Casual attacker**
  - Tries obvious URLs and parameters to gain elevated access.
  - Might exploit missing authentication checks.

- **Curious student**
  - Has a valid student account but tries to access admin/researcher views.

- **External attacker**
  - Attempts credential stuffing, injection attacks, or misusing exposed
    endpoints.

We assume no nation-state-level adversary; the main concern is preventing
unintended data exposure, privilege escalation, and abuse of LLM resources.

---

## 3. Security boundaries

- Admin and researcher APIs must be protected by:
  - Strong authentication (session or token-based).
  - Explicit authorisation checks (e.g., `@require_roles("admin")`).

- Student and guest views must:
  - Never expose raw LLM keys or internal infrastructure details.
  - Only show data appropriate for their role.

- LLM calls must go through a single, well-defined layer (no “secret” back
  doors that bypass logging and rate limiting).

---

## 4. Current mitigations (design-level)

- Central configuration via `src/config/settings.py`:
  - Encourages explicit, environment-aware settings rather than ad-hoc
    `os.getenv` calls.

- Fallback JSONL graph store:
  - For local development and testing, avoids accidental exposure of shared
    databases.

- Health and smoke tests:
  - `scripts/sanity_check.py` and `scripts/offline_pipeline_smoke.py` make it
    easier to detect broken or incomplete deployments.

---

## 5. Gaps and future work

To move toward an internet-facing, production-ready deployment, we should:

1. **Unify authentication and authorisation**
   - Ensure that all admin/researcher endpoints are decorated with central
     `@require_roles(...)` and that there are no “unguarded” routes.

2. **Harden session management**
   - Enforce `Secure`, `HttpOnly`, and `SameSite` attributes on cookies based
     on `Settings`.
   - Consider short session lifetimes and CSRF protection on state-changing
     operations.

3. **Input validation and upload handling**
   - Strictly validate uploaded PDFs and user-provided text.
   - Avoid rendering un-sanitised HTML back to the browser.

4. **Logging and monitoring**
   - Introduce structured logging with log levels controlled by `Settings`.
   - Log security-relevant events (failed logins, permission errors).

5. **Rate limiting and LLM abuse prevention**
   - Add limits on how often certain endpoints (especially those that trigger
     LLM calls) can be called per user/IP.
   - Monitor usage volume to detect misconfiguration or abuse.

This document is a starting point. It should evolve with the system and be
reviewed whenever new features or deployment profiles are added.
