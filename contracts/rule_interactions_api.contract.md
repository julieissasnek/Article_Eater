# Contract: Interactions API

## Routes
- `GET /interactions/review` → pending interactions list.
- `POST /interactions/{id}/action` with body `{action: "resolve"|"ignore"|"prompt"}`.

## Behaviors
- `prompt`: generate `disambiguation_prompt`; queue L0 job with rich query payload when possible.
- `resolve`: mark as resolved.
- `ignore`: mark as ignored.

## Errors
- 404 when interaction is not found.
- 400 on unknown action.