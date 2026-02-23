# Configuration Guide – Article Eater

This document explains how Article Eater reads configuration and how to set it
up for different environments (development, staging, production).

Article Eater now exposes a central `Settings` object in
`src/config/settings.py`. All other modules should import configuration from
there rather than calling `os.getenv` directly.

---

## 1. Where configuration comes from

1. **Environment variables**

   Environment variables are the primary source of configuration. For example:

   - `AE_ENV`
   - `AE_LLM_PROVIDER`
   - `AE_GRAPH_BACKEND`
   - `AE_SECRET_KEY`
   - `AE_SESSION_COOKIE_SECURE`
   - `AE_LOG_LEVEL`

2. **`config/.env` file (optional)**

   For local development, you can create a `config/.env` file by copying
   `config/.env.example`. Simple `KEY=VALUE` lines in that file will be loaded
   into `os.environ` when `get_settings()` is called, unless the variable is
   already defined in the process environment.

3. **Defaults**

   If neither environment variables nor `config/.env` define a value, sensible
   defaults are applied for local development (e.g., `env=dev`,
   `graph_backend=jsonl`, `llm_provider=fake`).

---

## 2. Core settings

### `AE_ENV`

Environment name. One of:

- `dev` (default)
- `staging`
- `prod`

This controls, for example, whether session cookies are marked `Secure` by
default.

### `AE_LLM_PROVIDER`

Identifier for the LLM provider to use. Typical values might be:

- `fake` (for offline tests and smoke checks)
- `openai`
- `vertex`
- `bedrock`

The core engine does not hard-code any one provider; it simply passes this
value to the layer that owns LLM integration.

### `AE_GRAPH_BACKEND`

Specifies which graph backend is used:

- `jsonl` – the built-in JSONL fallback
- `neo4j` – an external Neo4j instance (requires additional configuration)

### `AE_SECRET_KEY`

Secret key used for signing session cookies and other cryptographic operations.
In production this **must** be a long, random value and kept secret. The
default value in `settings.py` is **for development only**.

### `AE_SESSION_COOKIE_SECURE`

Boolean flag controlling whether session cookies are marked `Secure`. Defaults
to `true` when `AE_ENV=prod`, otherwise `false`.

### `AE_LOG_LEVEL`

Log verbosity (e.g., `DEBUG`, `INFO`, `WARNING`, `ERROR`). Defaults to `INFO`.

---

## 3. Example: local development

1. Copy the example file:

   ```bash
   cp config/.env.example config/.env
   ```

2. Optionally edit `config/.env` to adjust settings (e.g., `AE_LOG_LEVEL=DEBUG`).

3. Start your app or run scripts as usual. The settings module will read the
   `.env` file and environment variables, then expose a `Settings` object via
   `get_settings()`.

---

## 4. Example: staging / production

For staging and production environments, you typically **do not** use
`config/.env`. Instead:

- Define environment variables in your process manager, container, or cloud
  platform (e.g., Kubernetes, Docker Compose, systemd).
- Ensure that `AE_ENV` is set to `staging` or `prod`.
- Set a strong `AE_SECRET_KEY`.
- Set `AE_GRAPH_BACKEND` to `neo4j` if you are using an external graph DB.
- Configure logging (`AE_LOG_LEVEL`) and other deployment-level settings.

The `Settings` object remains the single source of truth for runtime code.
