# OSS / Pro application readiness

## Current readiness estimate

Forge Agent is a stronger early-stage open-source application candidate after the RC10 compatibility migration work.

Estimated readiness: **91%** for an honest early-stage OSS/application review.

This is not a production-readiness claim. It means the repository now has a clearer product thesis, MIT license posture, deterministic local demo surfaces, tests, architecture docs, and a visible migration path from MVP CLI to a larger ordinary-user agent runtime.

## Product thesis

Forge Agent is an AI butler for ordinary users:

```text
普通人不用学软件，也能一句话把事情办完。
```

The product aims to reduce ordinary users' learning cost and time cost. Users should speak in outcomes; Forge should handle the software, explain important actions, ask before risky work, record what happened, and remember useful preferences.

## Public OpenAI plan context

I did not find a public official page listing separate hidden requirements for a "developer Pro" application. The official pricing page describes ChatGPT Pro as a higher-usage plan with expanded Codex, agent mode, deep research, memory, context, and GPT-5.5 Pro access. The repository should therefore avoid claiming it meets unpublished criteria. It should present concrete evidence: runnable code, tests, CI, documentation, a clear user problem, and honest limitations.

## Repository value proposition

Forge Agent is not trying to be another expert-only agent framework. Its open-source value is the ordinary-user workflow layer:

```text
plain request -> understandable plan -> memory/context -> confirmation when needed -> local execution -> evidence -> recovery/reuse
```

The repository now contains:

- local CLI and deterministic demos;
- ask/task-card preview behavior;
- Memory Palace and bounded recall;
- approval-gated file organizer workflow;
- operation history and rollback surfaces;
- skill lifecycle foundations;
- RC10 compatibility slices for memory, state, planner, gateway, workflow, execution, governance, context graph, desktop/client adapter, HTTP payload adapter, and smoke benchmark harness.

## What changed in RC10 migration PR #59

PR #59 migrated the larger RC10 runtime in tested slices rather than bulk-overwriting the public repo.

Added or wired:

- memory engine and memory hardening modules;
- palace graph and context builder;
- ask replacement wiring for RC10 memory/context metadata;
- RC10-compatible checkpoint/session models;
- extended `StateStore` persistence for documents, palace graphs, skill libraries, and ledger entries;
- planner, registry, gateway, runtime compatibility facade;
- workflow model and local workflow executor;
- reusable skill lifecycle compatibility layer;
- governance verdict and ledger replay layer;
- desktop/client adapter and HTTP payload adapter;
- compatibility benchmark/smoke harness;
- tests for each compatibility slice.

## Suggested short application text

Forge Agent is an MIT-licensed local-first AI butler for ordinary users. It turns plain requests into previewed, confirmable, recorded workflows. The repo includes a working CLI MVP, Memory Palace, approval-gated file organization, rollback evidence, skill lifecycle, and a tested RC10 compatibility migration for memory/state/planner/gateway/workflow/governance/runtime adapters.

## Suggested API credits / support text

I would use API credits and developer support to harden Forge Agent's planning, review, issue triage, documentation, test generation, and safety workflows. The goal is to make an open-source ordinary-user automation agent that explains actions clearly, asks before risky steps, records evidence, and lowers the amount of software knowledge a user needs.

## Honest limitations

- The project is still early-stage and should not claim production readiness.
- Public adoption signal is limited.
- Some surfaces remain local deterministic compatibility layers rather than live app integrations.
- The current scheduler stores records but is not a production daemon.
- Broad app connectors, OAuth flows, signed installers, telemetry, and external provider-backed autonomous execution are not complete.
- The RC10 migration is intentionally slice-based; some archive pieces remain outside the public repo until they can be reconciled safely.

## Evidence to show reviewers

Useful commands:

```bash
forge-agent demo --kind file-organizer
forge-agent ask "organize my invoices by month" --json
forge-agent organize ./invoices
forge-agent organize ./invoices --approve
forge-agent organize-rollback
forge-agent history list
forge-agent skills
```

Useful docs:

- `README.md`
- `docs/STABILIZATION_AUDIT.md`
- `docs/CODEBASE_CLEANUP_PLAN.md`
- `docs/ARCHITECTURE_OVERVIEW.md`
- `docs/RC10_MEMORY_MIGRATION.md`
- `docs/RC10_ADAPTER_MIGRATION.md`
- `docs/OPEN_SOURCE_RELEASE_CHECKLIST.md`

## Before public announcement

- Merge PR #59 after CI/test review.
- Refresh screenshots or GIFs for the file-organizer demo and ask preview.
- Tag a release after the RC10 compatibility migration lands.
- Keep the public wording honest: early-stage, local-first, ordinary-user focused, not production-autonomous.
- Invite a few real users to try the demo and report issues.