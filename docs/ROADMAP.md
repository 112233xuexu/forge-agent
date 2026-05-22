# Roadmap

Forge Agent is an early-stage local-first AI butler for ordinary users.

This roadmap keeps the project honest: what works now, what is next, and what is intentionally not claimed yet.

## Now: local MVP and RC10 compatibility

Working or migrated in tested slices:

- CLI entrypoint and local deterministic demos.
- `forge-agent ask` task preview.
- Ordinary-user task cards.
- Local Memory Palace and bounded recall.
- Dry-run-first file organizer.
- Approval-gated organize execution.
- Rollback evidence for approved organize operations.
- Operation history.
- Local skill lifecycle controls.
- RC10 memory engine and hardening modules.
- RC10 palace graph and context builder.
- RC10 state, planner, gateway, runtime compatibility facade.
- RC10 workflow model and local executor.
- RC10 skill lifecycle compatibility layer.
- RC10 governance and ledger replay layer.
- Desktop/client adapter and pure HTTP payload adapter.
- Compatibility benchmark harness and CI workflow.

## Next: make it easier to use

Priorities:

1. Merge the RC10 compatibility PR after CI review.
2. Tag a release such as `v0.10.0-rc10-compat`.
3. Add screenshots or GIFs for ask preview and file organizer demo.
4. Add a short install video or terminal recording.
5. Improve README examples with real outputs.
6. Keep documentation honest about local-first status.

## Next: stronger runtime integration

Planned work:

- Wire RC10 governance into more public paths where tests protect behavior.
- Wire RC10 state checkpoints into selected workflows.
- Expand memory/context integration beyond `ask`.
- Persist and reuse workflow skills more directly.
- Add release notes for each public behavior change.

## Later: real app connectors

Potential connectors:

- email,
- calendar,
- files/cloud drive,
- notes/docs,
- GitHub,
- chat/workspace tools.

Rules before connectors:

- clear user confirmation,
- readable action preview,
- recovery or no-op path where possible,
- recorded evidence,
- no hidden broad permissions.

## Later: desktop and service surfaces

Possible surfaces:

- simple desktop UI,
- local tray app,
- local HTTP service,
- hosted demo mode.

Current repo only includes adapter layers. It does not yet ship a production web server, signed installer, or OS automation layer.

## Non-goals for now

- Do not claim production autonomous operation.
- Do not bulk-copy archive code over current public code.
- Do not add broad app connectors without confirmation and recovery design.
- Do not make the ordinary user learn internal terms like provider, registry, gateway, scope, or manifest.

## Success metric

A non-technical user should be able to say what they want, understand what Forge will do, confirm important changes, see what happened, and recover from mistakes where possible.
