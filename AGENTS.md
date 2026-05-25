# AGENTS.md

Operational guide for agents and maintainers working on Forge Agent.

## Product direction

Forge Agent is a local-first AI butler for ordinary users.

The user should not need to understand tools, skills, plugins, registries, workflows, gateways, providers, or agent internals. The expected product path is:

```text
plain request -> understandable plan -> confirmation when needed -> local execution -> evidence -> recovery/reuse
```

## Non-negotiable rules

1. Do not bulk-copy archive code over the public repository.
2. Migrate in tested slices.
3. Preserve existing CLI behavior unless a test and release note cover the change.
4. Keep user-facing language simple.
5. Do not claim production autonomy, broad connectors, OAuth, a daemon, or desktop automation unless actually implemented.
6. Every meaningful development round must update `docs/PROJECT_PROGRESS.md`.
7. CI must pass before merging.

## Preferred workflow

1. Start from latest `main`.
2. Create a focused branch.
3. Make one coherent product improvement.
4. Add or update tests.
5. Update docs.
6. Open a PR.
7. Wait for `ci` and `rc10-compat`.
8. Fix failures before merging.
9. Record progress in `docs/PROJECT_PROGRESS.md`.

## Current architecture priorities

Highest priority:

- ordinary-user `do` path;
- skill matching, generation, persistence, and reuse;
- memory/context integration;
- clear confirmation for risky work;
- execution evidence and recovery;
- open-source install/demo quality.

Lower priority unless needed by the product path:

- broad connectors;
- desktop UI;
- hosted services;
- background daemons;
- large internal rewrites.

## User-facing language

Prefer:

- "what I will do" instead of "workflow plan";
- "what I remembered" instead of "memory metadata";
- "please confirm" instead of "approval gate";
- "restore" or "undo" instead of "rollback";
- "what happened" instead of "audit log".

Internal technical names are allowed in code and developer docs, but should not leak into ordinary-user output unless necessary.

## Testing expectations

Add tests for every behavior change. At minimum, run relevant targeted tests. Before merge, GitHub Actions should show:

- `ci`: success;
- `rc10-compat`: success.

## Progress log requirement

After each development round, append a short entry to `docs/PROJECT_PROGRESS.md` with:

- date/time if known;
- branch/PR;
- completed work;
- tests or CI status;
- next step.

Keep entries short and readable.