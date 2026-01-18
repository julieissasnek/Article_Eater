# Admin Policy (RBAC) — Article Eater

## Roles
- **admin**: manage prompts, confidence weights, providers; run migrations.
- **researcher**: submit/monitor jobs; annotate rules.
- **viewer**: read-only.

## AuthZ
- /api/admin/* requires header **X-Admin-Token** == env **AE_ADMIN_TOKEN**.
- All admin writes are audited to `logs/admin_audit.log`.

## Change Control
- Prompt/weight edits are versioned into `archive/admin_edits/` by the app.