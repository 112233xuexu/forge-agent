# Forge Agent Codebase Cleanup Plan

This plan turns the stabilization request into a concrete cleanup process and keeps it aligned with the current repository state.

The project should not keep adding product features on top of unclear code. Before broad app connectors, front-end work, or deeper agent execution are added, the codebase must be reviewed file by file and cleaned in behavior-preserving PRs.

## Product direction to protect

Forge Agent is an AI butler for ordinary users.

The goal is not to expose APIs, tools, registries, or agent internals. The goal is:

```text
The user says what they want.
Forge handles the software.
Important actions are explained first.
The work is recorded.
Useful preferences are remembered.
Mistakes can be recovered when possible.
```

The codebase must support that direction without becoming a tangled backend.

## Cleanup principles

1. **No blind feature expansion during cleanup.**
   Refactor and migrate only in tested slices. Preserve behavior unless the PR explicitly documents an intentional product change.

2. **One responsibility per module.**
   Do not let a file become parser + business logic + persistence + presentation.

3. **Public behavior stays stable.**
   Existing CLI commands, JSON shapes, and tests should continue to work unless a later product PR intentionally changes them.

4. **User-facing wording must be plain.**
   Technical internals can stay technical, but user-facing outputs should avoid unnecessary jargon.

5. **Every cleanup PR must have a test owner.**
   A refactor or migration is not done until the relevant tests protect the behavior.

6. **Small PRs beat heroic rewrites.**
   Split, test, merge. Do not rewrite the entire project in one risky branch.

7. **Archive migration must be reconciled.**
   The uploaded RC10 source archive is not a drop-in replacement for the current repo. Current repo cleanup and task-card work must be preserved.

## File-by-file audit template

Every source file should eventually receive an entry using this template:

```text
File:
Current responsibility:
Correct responsibility:
Layer:
  - entrypoint / CLI / service / domain / persistence / presentation / test / docs
Public API to preserve:
Known problems:
Product-language issues:
Tests that protect it:
Archive migration status:
Action:
  - keep / split / rename / deprecate / delete / migrate-slice
Priority:
  - P0 / P1 / P2
```

## Current known hotspots and resolved areas

### `src/forge_agent/entrypoint.py`

Current status:

- Ask extraction completed.
- Routes wrapper-owned ask command and delegates the rest to the mature CLI.

Action:

- Keep.
- Do not add new ask business logic here.

### `src/forge_agent/ask_options.py`

Current responsibility:

- Parse ask-specific flags.

Action:

- Keep.
- Add tests if ask flags grow.

### `src/forge_agent/ask_service.py`

Current responsibility:

- Build ask plan and attach memory recall metadata.

Action:

- Keep.
- Next integration point for migrated memory verdict metadata, after compatibility tests pass.

### `src/forge_agent/ask_presenter.py`

Current responsibility:

- Render ask output and ask errors.
- Already supports ordinary-user task-card output.

Action:

- Keep.
- Preserve plain language.

### `src/forge_agent/cli.py`

Current responsibility:

- Build top-level parser, create runtime, and delegate command routing to `commands.registry`.

Current status:

- No longer the main command monolith.

Action:

- Keep thin.
- Do not move command business logic back into this file.

### `src/forge_agent/commands/registry.py`

Current responsibility:

- Compose command parsers and route commands to handler modules.

Action:

- Keep.
- If command count grows, consider table-driven registry to reduce repeated `if` routing.

### `src/forge_agent/memory.py`

Current responsibility:

- Public `MemoryStore` plus remaining compatibility/service logic.

Current extraction status:

- `memory_models.py` extracted.
- `memory_audit.py` extracted.
- `memory_recall.py` extracted.
- PR #59 adds separate RC10 memory engine/hardening modules but does not wire them into `MemoryStore` by default.

Action:

- Keep public `MemoryStore` API stable.
- Do not bulk-replace with archive code.
- Later split store/governance/service only with tests.

Priority:

- P0.

### `src/forge_agent/models.py` from PR #59

Current responsibility:

- Shared migrated `MemoryRecallHit` model for the RC10 memory subsystem slice.

Known problem:

- Name may overlap with the broader RC10 archive `models.py` if future migration imports the full archive model layer.

Action:

- Keep for PR #59 if tests pass.
- Before migrating full archive models, decide whether to keep this file as a small shared model layer or rename it to `memory_types.py`.

Priority:

- P0 before next model-heavy migration.

### `src/forge_agent/memory_engine.py` and hardening modules from PR #59

Current responsibility:

- Additive RC10 memory pipeline and hardening logic.

Action:

- Keep isolated until runtime/session-state compatibility is audited.
- Do not wire into user-facing ask output until tests cover current/stale/focus cases.

Priority:

- P0.

### `src/forge_agent/brain.py`

Current responsibility:

- Local deterministic planner and `BrainPlan`.

Action:

- Keep for now.
- Later split planner model vs planner rules if it grows.

Priority:

- P1.

### `src/forge_agent/organizer.py`

Current responsibility:

- File organizer workflow and rollback-related behavior.

Product importance:

- This is the clearest proof of “preview, confirm, execute, record, recover.”

Action:

- Audit after memory migration.
- Keep behavior stable.
- Keep ordinary-user task-card alignment.

Priority:

- P1.

### `src/forge_agent/skills.py`

Current responsibility:

- Skill store and lifecycle.

Product importance:

- Supports “do it like last time” and lower time cost.

Action:

- Audit after memory migration.
- Separate lifecycle, persistence, and recommendation if it grows.

Priority:

- P1.

### `src/forge_agent/approvals.py`

Current responsibility:

- Approval ledger.

Product importance:

- Should become ordinary-user “you confirm before I do it.”

Action:

- Audit user-facing language.
- Keep internal approval terms where appropriate, but present plain language externally.

Priority:

- P1.

### `src/forge_agent/history.py`

Current responsibility:

- Operation history.

Product importance:

- Should become ordinary-user “what I did.”

Action:

- Keep.
- Later align history output with task-card result format.

Priority:

- P1.

### `src/forge_agent/scheduler.py`

Current responsibility:

- Schedule records.

Action:

- Keep.
- Do not deepen automation until confirmation/recovery model is clearer.

Priority:

- P2.

### `src/forge_agent/content_packs.py`

Current responsibility:

- Local content artifact templates.

Action:

- Keep.
- Later present as user-facing “make a report / make slides” workflows.

Priority:

- P2.

### `src/forge_agent/runtime.py`

Current responsibility:

- Local runtime/task operations.

Action:

- Audit before wiring migrated RC10 runtime/session-state modules.
- Ensure it does not duplicate ask_service, organizer, or skill logic.

Priority:

- P1.

### `src/forge_agent/file_organizer_demo.py`

Current responsibility:

- Demo orchestration.

Action:

- Keep.
- Later upgrade demo language from CLI evidence to ordinary-user task flow.

Priority:

- P1.

## Uploaded RC10 archive reconciliation notes

The archive contains more than the current visible public repo, including memory engine/hardening, gateway, governance, desktop, release, and legacy/demo material.

Observed during migration:

- The archive cannot be bulk copied over the repo without risking regressions.
- Some original archive memory tests are time-sensitive and can become stale under the current date.
- Current repo has later cleanup/task-card work that the archive does not fully represent.
- Migration should continue as tested slices with compatibility docs.

## Test cleanup plan

The test suite should remain behavior-focused.

### P0 tests to preserve

- Ask parsing and validation.
- Ask workspace handling.
- Task-card human output and JSON preservation.
- Memory store behavior.
- Memory CLI behavior.
- File organizer dry-run and approved moves.
- Restore/undo evidence.
- JSON error contracts.
- Skill lifecycle.
- Approval flows.
- Demo smoke test.
- PR #59 memory engine/hardening tests.

### Future test additions

- Direct tests for current/stale note focus cases in migrated memory engine.
- Direct tests for archive-to-current model compatibility.
- Direct tests for `ask_options.py` if flags grow.
- Direct tests for connector permission/explanation language when connectors arrive.

## PR sequence from the current state

### PR #59: RC10 memory subsystems

Status:

- Open.

Includes:

- Additive memory engine/hardening modules.
- Focused memory pipeline tests.
- Migration audit docs.

### Next PR: runtime/session compatibility

Includes:

- Compare archive `models.py`, `session_state.py`, `runtime.py`, `planner.py`, and gateway modules against current repo.
- Decide model naming before importing broad archive model classes.
- Preserve existing CLI/task-card behavior.

### Next PR: full codebase inventory

Includes:

- Source file inventory.
- Test ownership map.
- Keep/split/rename/deprecate/delete decisions.

### Next PR: user-facing integration

Only after compatibility checks.

Includes:

- Memory verdict metadata wired into ask planning.
- Ordinary-user phrasing for “what I remembered for this task.”

## Definition of clean enough

The codebase is clean enough for new product work when:

1. `entrypoint.py` is thin.
2. `cli.py` stays command composition rather than business logic.
3. `memory.py` is a compatibility/service layer, not a monolith.
4. Each major workflow has a clear owner module.
5. User-facing output has an ordinary-language owner.
6. Tests protect every high-value command path.
7. New connectors can be added without editing one giant file.
8. A future simple front end can call service modules without shelling through CLI-only logic.
9. RC10 archive modules are reconciled against the current repo before being wired in.

## Non-goals during cleanup

Do not add:

- broad app integrations,
- desktop UI,
- OAuth flows,
- autonomous execution,
- new content generators,
- new scheduling behavior,
- or new public commands.

Cleanup and migration compatibility first. Then product features.