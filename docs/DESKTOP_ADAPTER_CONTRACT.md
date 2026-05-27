# Desktop Adapter Contract

This document defines the stable local response shape that a desktop shell, Tauri frontend, or other local UI can consume.

The desktop adapter is intentionally small. It wraps `CompatRuntime` and exposes a stable request/response envelope so the UI does not need to know about planners, workflow internals, governance internals, or memory internals.

## Contract version

Current version:

```text
desktop.v1
```

The version is returned in every response as `schema_version`.

## Request envelope

Minimum request:

```json
{
  "action": "plan",
  "text": "Summarize these notes",
  "inputs": {
    "notes": "hello"
  }
}
```

Supported actions:

- `health` or `ping`: check local readiness.
- `plan`: create a plan without executing it.
- `execute`: execute the request.
- `run`: accepted as a runtime action alias.

Optional fields:

- `request_id`: client-generated id. If omitted, Forge creates one.
- `user_id`: defaults to `desktop-user`.
- `session_id`: optional session continuity key.
- `options.execute`: forces execution when true.
- `options.govern`: enables governance checks when true.

## Response envelope

Every response includes:

```json
{
  "schema_version": "desktop.v1",
  "kind": "desktop_response",
  "request_id": "desk_example",
  "status": "planned",
  "text": "...",
  "needs_confirmation": true,
  "next_actions": ["execute"],
  "payload": {},
  "created_at": "..."
}
```

Stable top-level fields:

- `schema_version`: response contract version.
- `kind`: always `desktop_response` for this adapter.
- `request_id`: request correlation id.
- `status`: high-level status such as `ok`, `planned`, `completed`, or `unsupported`.
- `text`: short user-facing summary.
- `needs_confirmation`: true when the UI should ask the user before executing.
- `next_actions`: simple UI action hints, such as `execute` or `plan`.
- `payload`: structured runtime details for advanced UI panels.
- `created_at`: response timestamp.

## Confirmation flow

For a normal user request, the desktop shell should use this flow:

1. Send `action=plan` with the user's text.
2. Show `text` and any simple plan details from `payload`.
3. If `needs_confirmation` is true and `next_actions` contains `execute`, show a confirm button.
4. On confirm, send the same text/inputs with `action=execute`.
5. Show the completion result.

The UI should treat `payload` as optional detail and rely on the stable top-level fields for the primary interaction.

## Non-goals

The desktop shell should not expose internal names such as gateway, governance ledger, memory palace, or workflow executor to ordinary users. Those remain backend implementation details.
