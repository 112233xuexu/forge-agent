# Forge Agent Codebase Cleanup Plan

This plan turns the stabilization request into a concrete cleanup process.

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

1. **No new feature during cleanup.**
   Refactor only. Preserve behavior.

2. **One responsibility per module.**
   Do not let a file become parser + business logic + persistence + presentation.

3. **Public behavior stays stable.**
   Existing CLI commands, JSON shapes, and tests should continue to work unless a later product PR intentionally changes them.

4. **User-facing wording must be plain.**
   Technical internals can stay technical, but user-facing outputs should avoid unnecessary jargon.

5. **Every cleanup PR must have a test owner.**
   A refactor is not done until the relevant tests protect the behavior.

6. **Small PRs beat heroic rewrites.**
   Split, test, merge. Do not rewrite the entire project in one risky branch.

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
Action:
  - keep / split / rename / deprecate / delete
Priority:
  - P0 / P1 / P2
```

## Current known hotspots

### `src/forge_agent/entrypoint.py`

Current status:

- Ask extraction completed.
- Should remain thin.

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

- Keep for now.
- Later may attach task-card schema and app/tool suggestions.

### `src/forge_agent/ask_presenter.py`

Current responsibility:

- Render ask output and ask errors.

Action:

- Keep.
- Later make human output more ordinary-user friendly.

### `src/forge_agent/cli.py`

Current responsibility:

- Builds all command parsers and handles most command dispatch.

Problem:

- Too many responsibilities.
- Will become the next monolith if app connectors and ordinary-user task flows are added here.

Action:

- Split after memory extraction.
- Extract command modules under `src/forge_agent/commands/`.

Priority:

- P0.

### `src/forge_agent/memory.py`

Current responsibility:

- Public `MemoryStore` plus remaining persistence/governance/search/doctor/export logic.

Current extraction status:

- `memory_models.py` extracted.
- `memory_audit.py` extracted.
- `memory_recall.py` extracted.

Action:

- Finish current extraction PR.
- Keep public `MemoryStore` API stable.
- Do not add memory features until tests and CI pass.

Priority:

- P0.

### `src/forge_agent/memory_models.py`

Current responsibility:

- Memory dataclasses and constants.

Action:

- Keep.

### `src/forge_agent/memory_audit.py`

Current responsibility:

- Append/read memory audit rows.

Action:

- Keep.

### `src/forge_agent/memory_recall.py`

Current responsibility:

- Deterministic recall, scoring, tokenization, filters.

Action:

- Keep.
- Add direct tests if future recall logic changes.

### `src/forge_agent/brain.py`

Current responsibility:

- Local deterministic planner and `BrainPlan`.

Problem:

- Will need ordinary-user task-card output later.
- Should not become a full execution engine.

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

- Audit after CLI split.
- Keep behavior stable.
- Later use it as the first ordinary-user task-card demo.

Priority:

- P1.

### `src/forge_agent/skills.py`

Current responsibility:

- Skill store and lifecycle.

Product importance:

- Supports “do it like last time” and lower time cost.

Action:

- Audit after CLI split.
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

- Audit after CLI split.
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

## Test cleanup plan

The test suite should remain behavior-focused.

### P0 tests to preserve

- Ask parsing and validation.
- Ask workspace handling.
- Memory store behavior.
- Memory CLI behavior.
- File organizer dry-run and approved moves.
- Rollback evidence.
- JSON error contracts.
- Skill lifecycle.
- Approval flows.
- Demo smoke test.

### Future test additions

- Direct tests for `memory_recall.py`.
- Direct tests for `ask_options.py`.
- Direct tests for ordinary-user task-card schema.
- Direct tests for connector permission/explanation language when connectors arrive.

## PR sequence

### PR 1: product positioning docs

Status:

- In progress.

Includes:

- README positioning update.
- `PRODUCT_POSITIONING.md`.
- `COMPETITIVE_BENCHMARK.md` update.
- `STABILIZATION_AUDIT.md` update.
- This cleanup plan.

### PR 2: finish memory extraction

Includes:

- Current `memory_models.py` / `memory_audit.py` / `memory_recall.py` work.
- Run memory tests and CI.
- No product behavior changes.

### PR 3: codebase inventory

Includes:

- Full source file inventory.
- Test ownership map.
- Keep/split/rename/deprecate/delete decisions.

### PR 4: CLI handler split

Includes:

- Command module extraction.
- Preserve CLI behavior and JSON contracts.

### PR 5: ordinary-user task-card schema

Only after cleanup.

Includes:

- User-facing task schema.
- Ask output starts to align with:

```text
What you asked
What I will do
What this may affect
Confirm / cancel / edit
Result
Restore / correct when possible
```

## Definition of clean enough

The codebase is clean enough for new product work when:

1. `entrypoint.py` is thin.
2. `cli.py` is no longer the main business logic container.
3. `memory.py` is not a monolith.
4. Each major workflow has a clear owner module.
5. User-facing output has an ordinary-language owner.
6. Tests protect every high-value command path.
7. New connectors can be added without editing one giant file.
8. A future simple front end can call service modules without shelling through CLI-only logic.

## Non-goals during cleanup

Do not add:

- broad app integrations,
- desktop UI,
- OAuth flows,
- semantic memory retrieval,
- autonomous execution,
- new content generators,
- new scheduling behavior,
- or new public commands.

Cleanup first. Then product features.
