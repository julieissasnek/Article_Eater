# Secrets and Keys Model

This document explains how Article Eater handles encryption keys, admin
access tokens, and API keys for LLM providers. It is intended for TAs and
operators who deploy the system in development and production.

## 1. AE_MASTER_KEY (encryption for user API keys)

### What it is

`AE_MASTER_KEY` is a base64-encoded key used to encrypt per-user provider
API keys before they are stored in the SQLite database.

Code reference: `app/security/keys.py`.

- `set_key(user_id, provider, raw_key)`:
  - Encrypts `raw_key` with a Fernet cipher derived from `AE_MASTER_KEY`.
  - Stores the ciphertext in `user_api_keys`.
- `get_key(user_id, provider)`:
  - Decrypts the stored ciphertext using the same Fernet cipher.

### Default behaviour

If `AE_MASTER_KEY` is **not** set in the environment:

- The code generates a fresh random Fernet key at process startup:
  - `os.urandom(32)` → base64-encoded; saved to `os.environ["AE_MASTER_KEY"]`.
- This means:
  - Keys can be written and read **within the same process**.
  - If the process restarts and `AE_MASTER_KEY` is missing again, a new
    random key will be generated and previously stored API keys will no
    longer be decryptable.

This default is acceptable for local development and short-lived demos,
but it is **not suitable** for production or long-running deployments.

### Recommended practice

- For any deployment where you care about continuity of encrypted keys,
  explicitly set a stable `AE_MASTER_KEY`:

  - Generate a key once (e.g., with Python):

    ```python
    import base64, os
    print(base64.urlsafe_b64encode(os.urandom(32)).decode())
    ```

  - Set it in the environment before starting any process:

    ```bash
    export AE_MASTER_KEY="base64-string-from-above"
    ```

- Do **not** commit the value of `AE_MASTER_KEY` to version control.
- Use your platform’s secret store (GitHub Actions secrets, Docker
  secrets, etc.) to provide it to the container / VM.

If you later rotate `AE_MASTER_KEY`, any keys encrypted with the old
value will no longer be decryptable. Plan rotations carefully.

## 2. AE_ADMIN_TOKEN (admin guard)

### What it is

`AE_ADMIN_TOKEN` is an application-level secret used by the admin guard.

Code reference: `src/security/admin_guard.py`.

- The `admin_required` dependency checks an HTTP header:

  - Header: `X-Admin-Token`
  - Env var: `AE_ADMIN_TOKEN`

- Behaviour:

  - If `AE_ADMIN_TOKEN` is empty, or the header is missing/mismatched,
    the request fails with `401 admin token required`.
  - On success, an audit record is appended to `logs/admin_audit.log`.

### Recommended practice

- Set a non-trivial `AE_ADMIN_TOKEN` for any shared deployment:

  ```bash
  export AE_ADMIN_TOKEN="some-long-random-string"
  ```

- Pass the token in HTTP requests that need admin access, e.g.:

  ```bash
  curl -H "X-Admin-Token: $AE_ADMIN_TOKEN" http://localhost:8000/api/admin/...
  ```

- Never expose `AE_ADMIN_TOKEN` in client-side JavaScript or public
  configuration. It should only be used from trusted environments
  (e.g., your browser via a secure admin UI, or internal scripts).

## 3. Provider API keys (LLM access)

### What they are

Provider-specific API keys are used by the LLM client to call language
models.

Code reference: `app/services/llm.py`.

- `OPENAI_API_KEY`:
  - Used to call OpenAI chat models via `/v1/chat/completions`.
- `GOOGLE_API_KEY` or `GEMINI_API_KEY`:
  - Used to call Gemini models via the Google Generative Language API.
- Additional providers (e.g., Anthropic) may be wired in the future via
  similar environment variables.

### Behaviour

- If `OPENAI_API_KEY` is missing, `LLMClient.complete_openai(...)`
  asserts and will raise an error.
- If `GOOGLE_API_KEY` and `GEMINI_API_KEY` are both missing,
  `LLMClient.complete_gemini(...)` asserts and will raise an error.

### Recommended practice

- For local development:

  ```bash
  export OPENAI_API_KEY="sk-..."
  export GOOGLE_API_KEY="AIza..."
  # or export GEMINI_API_KEY="..."
  ```

- For production:

  - Store provider keys in your platform’s secret store.
  - Provide them as environment variables to the Article Eater process.
  - Never hard-code API keys in the repo.

## 4. Summary checklist for TAs / operators

Before running Article Eater in a shared environment:

1. **Set AE_MASTER_KEY** to a stable base64-encoded 32-byte key.
2. **Set AE_ADMIN_TOKEN** to a strong random string.
3. **Set provider API keys**:
   - `OPENAI_API_KEY`
   - `GOOGLE_API_KEY` or `GEMINI_API_KEY`
4. Confirm that:
   - `/healthz` returns `{"status": "ok"}`.
   - `/ui/config` shows `engine_use_mocks: false` in production.
   - Admin endpoints (e.g., RuleGraph v2 tools) are only reachable when
     sending the correct `X-Admin-Token` header.

## 5. .env vs .env.example
...
