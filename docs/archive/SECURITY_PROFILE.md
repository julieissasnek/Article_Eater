# Article Eater Security Profile

This document describes the intended security posture for Article Eater
in typical lab/teaching deployments, and what is required to harden it
for broader or internet-facing use.

## 1. Authentication and Admin Access

- API authentication is implemented via JWT bearer tokens in `app/auth.py`.
- The global `get_current_user` dependency in `app/main.py` currently
  allows anonymous access when no credentials are presented. This is by
  design for internal, firewalled deployments.
- All **administrative** endpoints in `src/services/admin_service.py` are
  protected via the `admin_required` dependency from
  `src/security/admin_guard.py`, which enforces a strong shared secret
  in the `X-Admin-Token` header (`AE_ADMIN_TOKEN` environment variable).

Recommended practice:

- Always set a non-trivial `AE_ADMIN_TOKEN` in production-like environments.
- Restrict access to the admin GUI to trusted users (e.g., via VPN,
  reverse proxy, or campus firewall).
- Treat any endpoint wired through `admin_required` as privileged and
  avoid exposing it on the public internet.

## 2. Lab / Teaching vs Production Profiles

- **Lab/teaching (default)**:
  - Anonymous read access to non-admin endpoints is acceptable.
  - Admin endpoints remain gated by `AE_ADMIN_TOKEN` and are typically
    reachable only to instructors or operators.
  - Authentication/authorization can be layered in front of Article
    Eater by running it behind a campus SSO or reverse proxy.

- **Internet-facing / multi-tenant (not the default)**:
  - All mutating and admin endpoints should be behind robust authN/Z
    (SSO, OAuth, etc.).
  - You should carefully review all routes in `app/routes` and
    `src/services` and consider switching to a stricter policy where
    anonymous access is disabled, except for `/healthz` and `/metrics`.
  - Require HTTPS termination and strict secret management for
    `AE_ADMIN_TOKEN` and any API keys.

## 3. Audit Logging

- The `admin_guard` module appends a simple JSON line to
  `logs/admin_audit.log` for each successful admin access.
- For hardened deployments, you may want to ship these logs to a central
  logging system or SIEM.

## 4. Next Security Steps

- Integrate with institutional SSO for user-level auth.
- Add role-based authorization (RBAC) for different admin profiles.
- Fully enumerate all public endpoints in `public_surface_ledger.json`
  and ensure they match the authenticated profile described above.
