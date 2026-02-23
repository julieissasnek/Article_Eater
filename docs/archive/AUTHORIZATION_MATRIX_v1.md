# Authorization Matrix v1 – Article Eater

This document summarises which roles are intended to access which HTTP/API
surfaces in the current Article Eater codebase (v20.7.3f design pass).

It is a *living* document and should be updated whenever new endpoints are
added or security policies change.

---

## 1. Roles

- **Admin**
  - Full system control.
  - Manages authentication, API keys, deployment configuration, and cost
    monitoring.
  - Can see all usage metrics and research data.

- **Researcher**
  - Ingests papers, reviews Seven-Panel outputs, edits findings and rules.
  - Can see research data but does not manage system-wide security settings.

- **Student**
  - Uses curated views and exercises.
  - May ingest a constrained set of papers, but with scoped access.

- **Guest**
  - Read-only demo access to selected, non-sensitive content.

---

## 2. Mechanisms

There are currently **two** main enforcement mechanisms in the repo (with a migration in progress toward JWT roles):

1. **JWT-based user accounts (FastAPI)**
   - Implemented in `app/auth.py` and used in `app/main.py`.
   - Endpoints can depend on `get_current_user` to determine who is calling.

2. **Header-based admin guard (X-Admin-Token)**
   - Implemented in `src/security/admin_guard.py` as `admin_required`.
   - Requires a header:
     - `X-Admin-Token: <token>`
   - Compares this to `AE_ADMIN_TOKEN` in the environment.

The second mechanism is now primarily a legacy / fallback guard. The preferred pattern for new privileged endpoints is to use JWT roles via the `require_admin` / `require_researcher_or_admin` dependencies in `app.auth`.

---

## 3. Endpoint overview (initial pass)

### 3.1 Health and metrics

- `GET /healthz`
- `GET /metrics`

**Intended roles:** any  
**Enforcement:** none (read-only, low risk)

These endpoints are safe to expose broadly and are used by tests and monitoring.

---

### 3.2 User profile

- `GET /profile/me` (implemented in `app/main.py`)

**Intended roles:** authenticated users (Admin, Researcher, Student)  
**Enforcement:**
- Depends on `get_current_user` (JWT)
- Returns 401 if no valid token

---

### 3.3 Usage – per-user

- `GET /usage/me` (in `app/routes/usage.py`)

**Intended roles:** authenticated users (Admin, Researcher, Student)  
**Enforcement (current pass):**
- No explicit role check.
- Records usage via `record_cost_event`.
- Returns last ~200 cost events for the requested `user_id` (default: `"anon"`).

**Future tightening:**
- Bind `user_id` to the caller’s identity via JWT rather than a free parameter.
- Optionally require authentication for non-`anon` queries.

---

### 3.4 Usage – admin summary

- `GET /usage/admin/summary` (in `app/routes/usage.py`)

**Intended roles:** Admin only  
**Enforcement (current pass):**
- Protected by `admin_required` (from `src.security.admin_guard`).
- Requires a valid `X-Admin-Token` header matching `AE_ADMIN_TOKEN`.

This is a **privileged endpoint**: it shows aggregated cost metrics across all
users and providers.

---

### 3.5 API key management

- `POST /profile/api-keys` (in `app/routes/keys.py`)

**Intended roles:** Admin (current pass), later possibly “self-service” for users  
**Enforcement (current pass):**
- Protected by `admin_required` and `X-Admin-Token` (as above).
- Allows storing encrypted API keys for a given `user_id` + `provider`.

**Future tightening:**
- Bind key operations to the authenticated JWT user instead of free-form
  `user_id`.
- Add read / delete endpoints with explicit role checks.

---

### 3.6 Rule interactions review

- `GET /interactions/review` (in `app/routes/interactions.py`)

**Intended roles:** Researcher, Admin  
**Enforcement (current pass):**
- No explicit guard; read-only view into `rule_interactions`.

**Future tightening:**
- Add a role-based guard (JWT or admin token) before exposing in a multi-user
  deployment.

---

## 4. Configuration touchpoints

Security-relevant configuration is centralised in:

- `src/config/settings.py`

Relevant fields:

- `env` – `"dev"`, `"staging"`, `"prod"`
- `secret_key` – used for JWT signing (`app/auth.py`)
- `log_level` – controls global logging level
- `session_cookie_secure` – future hook for cookie-based auth

Environment variables:

- `AE_ADMIN_TOKEN` – shared secret for `X-Admin-Token` usage.
- `AE_ENV` – environment name, affects CORS behaviour.
- `AE_LOG_LEVEL` – log verbosity (e.g., `DEBUG`, `INFO`).

---

## 5. Roadmap for tighter alignment

To converge toward a single, coherent auth model:

1. Migrate sensitive endpoints to **always** depend on `get_current_user` and
   derive role from the JWT user’s `role` field.
2. Use `admin_required` as a thin wrapper around `get_current_user` instead of
   a standalone header secret.
3. Remove (or drastically limit) unauthenticated access to anything that
   touches cost data, keys, or research artefacts.
4. Keep this matrix up to date as new endpoints and roles are introduced.

This matrix reflects the current state after the v20.7.3f design pass and
should be treated as part of the governance documentation.
