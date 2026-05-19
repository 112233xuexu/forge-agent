# Forge Agent Stabilization Audit

This document freezes random feature expansion and records what must be stabilized before more runtime functionality is added.

## Current operating rule

Forge is being repositioned as an AI butler for ordinary users:

```text
普通人不用学软件，也能一句话把事情办完。
```

That product direction requires a clean codebase. A simple front end may hide thousands of connectors in the future, but the backend cannot become a monolith.

No new runtime features should be added until the core architecture is clarified and the current codebase is reviewed file by file.

## Final product target

Forge Agent is not only a memory system, not only an automation CLI, and not only a safety framework.

The product target is:

```text
simple request -> clear plan -> confirm important actions -> execute through apps/tools -> record result -> recover/correct when possible -> remember useful preferences for next time
```

The named benchmark directions are now:

1. **OpenHuman**: ordinary-user AI entry point, many connected apps, simple personal assistant framing.
2. **OpenClaw**: self-hosted agent execution, tool access, automation, messaging/workflow entry points, and practical task execution.
3. **Hermes Agent**: persistent memory, self-improvement, experience-to-skill loops, and long-running agent continuity.

Forge should match the useful parts of all three, then exceed them on:

- lower user learning cost,
- lower user time cost,
- visible memory governance,
- human-readable confirmation,
- recoverable operations,
- work records,
- skill lifecycle discipline,
- ordinary-user understandability,
- and maintainable backend structure.

## What must stop now

Do not continue by adding features directly into already-heavy files.

The immediate hotspots are:

- `src/forge_agent/entrypoint.py`
- `src/forge_agent/cli.py`
- `src/forge_agent/memory.py`

But the cleanup scope is larger than those files. The whole project needs a file-by-file review before broad app connectors or front-end work begins.

## Current architecture issues

### 1. `entrypoint.py` became an ask orchestration file

Status:

The first stabilization extraction has already moved ask parsing, ask service assembly, and ask presentation into dedicated modules.

Target:

| Module | Responsibility |
|---|---|
| `ask_options.py` | Parse and validate ask-specific flags. |
| `ask_service.py` | Build the ask plan and attach memory/tool/risk metadata. |
| `ask_presenter.py` | Render JSON and human-readable ask output. |
| `entrypoint.py` | Route CLI entrypoint only. |

Remaining rule:

Do not expand `entrypoint.py` again.

### 2. `cli.py` is still a monolithic command router

Current responsibilities include:

- Parser construction for all commands.
- Command dispatch.
- Memory command handling.
- History handling.
- Schedule handling.
- Content generation handling.
- Skills handling.
- Approvals handling.
- Organizer handling.
- Error envelope formatting.

Problem:

Every new feature expands this file. This will become unmaintainable once app connectors, front-end task schemas, ordinary-user cards, and workflow handlers grow.

Target split:

| New module | Responsibility |
|---|---|
| `commands/memory.py` | Memory CLI parser and handlers. |
| `commands/ask.py` | Ask CLI parser and handlers, if moved out of wrapper. |
| `commands/tools.py` | Tool/app capability CLI. |
| `commands/skills.py` | Skill CLI. |
| `commands/approvals.py` | Approval CLI. |
| `commands/organize.py` | File organizer CLI. |
| `cli.py` | Compose command parsers and dispatch only. |

### 3. `memory.py` is being split but is not done

Original responsibilities included:

- Memory item dataclass.
- Memory recall dataclass.
- Store initialization.
- JSONL persistence.
- Palace file creation.
- CRUD-like operations.
- Status transitions.
- Search.
- Recall scoring.
- Sensitive memory gating.
- Scope/wing filtering.
- Audit append/read.
- Doctor/status reporting.
- Export bundle.

Status:

The extraction has started:

| Module | Status |
|---|---|
| `memory_models.py` | Extracted. |
| `memory_audit.py` | Extracted. |
| `memory_recall.py` | Extracted. |
| `memory_store.py` | Not yet extracted. |
| `memory_governance.py` | Not yet extracted. |
| `memory_service.py` | Not yet extracted. |

Rule:

Do not add memory features until the extraction PR is tested and merged.

### 4. Product wording must stay ordinary-user-first

The product should not lead with engineering terms such as:

- rollback,
- audit,
- permission manifest,
- trust kernel,
- tool registry,
- vector search,
- agent framework.

Internally those may exist. Externally, the product should use language like:

| Internal term | User-facing language |
|---|---|
| permission | What I can see or change |
| approval | You confirm before I do it |
| rollback | Restore / undo |
| audit log | What I did |
| memory | What I remember about you |
| tool | An app I can use for you |
| risk | What this may affect |
| skill | How I should do this next time |

## Full codebase cleanup requirement

The whole project must be audited, not just the files touched most recently.

For each source file, the cleanup pass must record:

1. What the file currently does.
2. Whether that responsibility is still correct.
3. Whether the file is user-facing, domain logic, persistence, presentation, test support, or legacy.
4. Whether it mixes responsibilities.
5. What public API must remain stable.
6. What tests protect it.
7. Whether it should be kept, split, renamed, deprecated, or deleted.
8. Whether product wording is ordinary-user-friendly.
9. Whether it moves Forge toward lower learning cost and lower time cost.

## What should be preserved

The recent work is not wasted. These pieces should be kept:

### Memory Palace foundation

Keep:

- `memory add`
- `memory list`
- `memory show`
- `memory search`
- `memory forget`
- `memory quarantine`
- `memory restore`
- `memory export`
- `memory doctor`
- `memory recall`
- bounded recall
- scoring
- recall reasons
- `last_used_at`
- sensitive default exclusion
- explicit sensitive opt-in
- scope/wing filters
- memory audit

Reason:

This supports long-term context and visible memory, one of Forge's strongest product pillars.

### Ask memory controls

Keep:

- `ask --no-memory`
- `ask --memory-limit`
- `ask --include-sensitive-memory`
- `ask --memory-scope`
- `ask --memory-wing`
- `metadata.memory_used`
- `metadata.memory_policy`

Reason:

This makes memory use visible and controllable, while still supporting ordinary-user personalization.

### Approval, recovery, and evidence patterns

Keep:

- approval ledger
- dry-run organizer
- approved organize operation
- rollback/recovery manifest
- operation history
- skill lifecycle states

Reason:

These patterns should become user-facing as:

```text
I will show you first.
You confirm before I do it.
I keep a record.
You can restore when possible.
```

## What should be paused

Pause these until the architecture is cleaned up:

- New memory commands.
- New agent execution pipeline logic.
- New tool/app connector runtime code.
- New UI/TUI/Web UI.
- New semantic retrieval.
- New content generation features.
- New GitHub automation features.
- New email/calendar integrations.

## Stabilization plan

### Phase S1: Product positioning and benchmark correction

Goal:

Clarify the product direction before more code changes.

Actions:

- Make docs ordinary-user-first.
- Include OpenHuman, OpenClaw, and Hermes Agent as named benchmark directions.
- Add product positioning around lowering learning cost and time cost.

Exit criteria:

- The repo clearly states who Forge is for.
- The repo clearly states why ordinary users should care.
- The repo avoids leading with engineering jargon.

### Phase S2: Extract ask orchestration

Goal:

Make `entrypoint.py` thin again.

Status:

Completed and merged in PR #41.

Exit criteria:

- `entrypoint.py` only routes.
- Existing ask tests still pass.
- No new product behavior is introduced.

### Phase S3: Extract memory internals

Goal:

Keep memory functionality but split responsibilities.

Actions:

- Move dataclasses/constants out of `memory.py`.
- Move audit helpers out of `memory.py`.
- Move recall scoring/filtering out of `memory.py`.
- Keep the public `MemoryStore` API stable during the first extraction.

Exit criteria:

- Existing memory tests still pass.
- Public CLI behavior unchanged.
- `memory.py` becomes a compatibility/service layer instead of a monolith.

### Phase S4: Full codebase cleanup audit

Goal:

Review the entire project file by file before more feature work.

Actions:

- Add a codebase cleanup plan.
- Inventory every source and test file.
- Mark each file as keep/split/rename/deprecate/delete.
- Record test coverage for each critical path.
- Identify product-language mismatches.

Exit criteria:

- Every source file has an assigned responsibility.
- Every major command path has a test owner.
- No new feature work starts from unclear code.

### Phase S5: Split CLI handlers

Goal:

Make new features possible without growing `cli.py` further.

Actions:

- Extract memory command parser/handler.
- Extract approvals command parser/handler.
- Extract skills command parser/handler.
- Extract organizer command parser/handler.

Exit criteria:

- `cli.py` becomes command composition and dispatch.
- Existing CLI tests still pass.

### Phase S6: Resume product feature work

Only after S1-S5 should larger runtime features continue.

Next feature after stabilization:

- ordinary-user task card schema,
- then app-backed workflow prototypes.

## Immediate next PR sequence

1. **PR A: product positioning docs**
   - `README.md`
   - `PRODUCT_POSITIONING.md`
   - `COMPETITIVE_BENCHMARK.md`
   - `STABILIZATION_AUDIT.md`
   - `CODEBASE_CLEANUP_PLAN.md`

2. **PR B: finish memory extraction with no behavior change**
   - Keep public `MemoryStore` API stable.
   - Run memory tests and CI.

3. **PR C: full codebase cleanup audit**
   - File-by-file inventory.
   - Responsibility map.
   - Test ownership map.

4. **PR D: CLI handler extraction with no behavior change**
   - Split command handlers.
   - Preserve JSON output contracts.

5. **PR E: ordinary-user task card schema**
   - Only after cleanup.

## Decision rule during stabilization

A change is allowed only if it does one of these:

- Clarifies ordinary-user product direction.
- Reduces file responsibility.
- Preserves existing behavior while improving structure.
- Adds tests that protect existing behavior.
- Improves OpenHuman/OpenClaw/Hermes benchmark accuracy.
- Reduces future user learning cost or time cost.

A change is not allowed if it:

- Adds a new runtime feature before cleanup.
- Adds a new command before cleanup.
- Expands `entrypoint.py`, `cli.py`, or `memory.py` further.
- Changes behavior without a stabilization reason.
- Makes the project look more impressive but harder to maintain.
- Uses engineering jargon as the product message.
