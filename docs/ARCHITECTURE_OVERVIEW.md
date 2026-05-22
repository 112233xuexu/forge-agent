# Architecture overview

Forge Agent is moving from a local CLI MVP toward an ordinary-user AI butler runtime.

The public product promise is simple:

```text
user request -> understandable plan -> confirmation if needed -> local execution -> evidence -> recovery/reuse
```

## Current layers

```text
CLI / ask presenter
  -> ask service
  -> Brain Adapter / SimplePlanner
  -> memory recall + RC10 memory engine
  -> context builder / palace graph
  -> task card preview

CompatRuntime
  -> gateway adapters
  -> state store
  -> planner
  -> optional governance
  -> optional workflow execution

Local tools
  -> ToolRegistry
  -> WorkflowExecutor
  -> ledger / skill lifecycle / benchmark harness
```

## Stable public behavior today

The existing CLI remains the public user path:

- `forge-agent ask`
- `forge-agent organize`
- `forge-agent organize-rollback`
- `forge-agent memory ...`
- `forge-agent skills ...`
- `forge-agent history ...`
- `forge-agent schedule ...`
- `forge-agent make ...`

These paths should remain backwards compatible unless a release note says otherwise.

## RC10 compatibility layers

PR #59 adds the larger RC10 runtime in tested slices:

- memory engine and hardening;
- palace graph and context builder;
- checkpoint/session models and state store;
- planner, tool registry, gateway, and runtime facade;
- workflow model and local executor;
- skill lifecycle;
- governance verdicts and ledger replay;
- desktop/client and HTTP payload adapters;
- compatibility benchmark harness.

Most RC10 layers are additive. The first real replacement wiring is in `ask_service.py`, where existing `MemoryStore.recall()` results are promoted into RC10 memory/context metadata while preserving the old `memory_used` output shape.

## What is intentionally not production yet

- No broad live app connectors are shipped by default.
- No OAuth setup is included.
- No production background daemon is included.
- No signed desktop installer is included.
- `http_adapter.py` normalizes payloads but does not run a web server.
- `desktop_adapter.py` normalizes local client requests but does not automate the OS.
- Compatibility layers should be wired into default behavior only after tests cover the change.

## Safety boundaries

Forge should ask before risky work, record what happened, and keep recovery paths visible. Internal engineering terms can exist in code, but user-facing output should prefer ordinary language:

- approval -> you confirm before I do it;
- rollback -> restore / undo;
- audit log -> what I did;
- memory -> what I remember about you;
- tool -> an app I can use for you.

## Contributor rule

Do not bulk-copy archive code over the public repo. Migrate in tested slices, preserve CLI behavior, and update docs/tests with each behavior change.
