# Forge Agent Stabilization Audit

This document freezes random feature expansion and records what must be stabilized before more runtime functionality is added.

## Current operating rule

No new runtime features should be added until the core architecture is clarified.

The project has useful pieces, but recent development moved too quickly. Several core files now contain too many responsibilities. Continuing to add features directly into these files will make Forge harder to maintain and harder to position against OpenClaw and Hermes Agent.

## Final product target

Forge Agent is not only a memory system.

The precise benchmark targets are:

1. **OpenClaw**: self-hosted agent execution, tool access, automation, messaging/workflow entry points, and practical task execution.
2. **Hermes Agent**: persistent memory, self-improvement, experience-to-skill loops, and long-running agent continuity.

Forge should match the useful parts of both, then exceed them on:

- Visible memory governance.
- Human-controlled execution.
- Approval-first safety.
- Reversible operations.
- Local-first auditability.
- Skill lifecycle discipline.
- Ordinary-user understandability.

## What must stop now

Do not continue by adding features directly into:

- `src/forge_agent/entrypoint.py`
- `src/forge_agent/cli.py`
- `src/forge_agent/memory.py`

These files are still functional, but their responsibilities are now too broad.

## Current architecture issues

### 1. `entrypoint.py` has become an ask orchestration file

Current responsibilities include:

- Console entrypoint wrapping.
- Global option parsing.
- `ask` option parsing.
- Ask validation.
- BrainAdapter invocation.
- Memory recall policy.
- Memory policy metadata construction.
- Human output formatting.
- JSON output formatting.

Problem:

`entrypoint.py` should be a thin entrypoint, not the home of ask policy and memory orchestration.

Target split:

| New module | Responsibility |
|---|---|
| `ask_options.py` | Parse and validate ask-specific flags. |
| `ask_service.py` | Build the ask plan and attach memory/tool/risk metadata. |
| `ask_presenter.py` | Render JSON and human-readable ask output. |
| `entrypoint.py` | Route CLI entrypoint only. |

### 2. `cli.py` is becoming a monolithic command router

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

Every new feature expands this file. This will become unmaintainable once tool registry, risk policy, demo scenarios, and memory management commands grow.

Target split:

| New module | Responsibility |
|---|---|
| `commands/memory.py` | Memory CLI parser and handlers. |
| `commands/ask.py` | Ask CLI parser and handlers, if moved out of wrapper. |
| `commands/tools.py` | Tool registry CLI. |
| `commands/skills.py` | Skill CLI. |
| `commands/approvals.py` | Approval CLI. |
| `commands/organize.py` | File organizer CLI. |
| `cli.py` | Compose command parsers and dispatch only. |

### 3. `memory.py` mixes model, storage, governance, retrieval, and audit

Current responsibilities include:

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

Problem:

The memory layer is currently strong, but if update/import/dedupe/stats/aging/compaction are added here directly, the file will become another monolith.

Target split:

| New module | Responsibility |
|---|---|
| `memory_models.py` | `MemoryItem`, `MemoryRecall`, constants. |
| `memory_store.py` | Read/write JSONL, basic persistence. |
| `memory_governance.py` | forget/quarantine/restore/sensitive policy. |
| `memory_recall.py` | Search, scoring, filters, recall result. |
| `memory_audit.py` | Audit log append/read/export. |
| `memory_service.py` | Public high-level memory API. |

### 4. Product direction drifted from named competitors to generic categories

The benchmark document initially drifted toward broad categories such as general assistants, coding agents, and workflow tools.

That is too vague.

The precise target must be:

- Match OpenClaw on execution breadth and self-hosted agent workflows.
- Match Hermes Agent on persistent memory and self-improving skill loops.
- Exceed both on governance, auditability, rollback, and user control.

Benchmark docs must keep OpenClaw and Hermes Agent as named references, not just abstract market categories.

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

This is a real differentiator against opaque memory systems.

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

This makes memory use visible and controllable, which is central to the product thesis.

### Approval, rollback, and evidence patterns

Keep:

- approval ledger
- dry-run organizer
- approved organize operation
- rollback manifest
- operation history
- skill lifecycle states

Reason:

This is the start of Forge's advantage over autonomous but unsafe execution agents.

## What should be paused

Pause these until the architecture is cleaned up:

- New memory commands.
- New agent execution pipeline logic.
- New tool registry runtime code.
- New UI/TUI/Web UI.
- New semantic retrieval.
- New content generation features.
- New GitHub automation features.

## Stabilization plan

### Phase S1: Documentation and benchmark correction

Goal:

Clarify the product direction before more code changes.

Actions:

- Keep `docs/COMPETITIVE_BENCHMARK.md` focused on OpenClaw and Hermes Agent.
- Add this stabilization audit.
- Add a concise architecture map.

Exit criteria:

- The repo clearly states what Forge is trying to beat and why.
- The repo clearly states what must be refactored before new features.

### Phase S2: Extract ask orchestration

Goal:

Make `entrypoint.py` thin again.

Actions:

- Move ask flag parsing into `ask_options.py`.
- Move memory-aware plan assembly into `ask_service.py`.
- Move ask output rendering into `ask_presenter.py`.
- Keep behavior and tests unchanged.

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

### Phase S4: Split CLI handlers

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

### Phase S5: Resume feature work

Only after S1-S4 should new runtime features continue.

Next feature after stabilization:

- v2.7 Agent Execution Pipeline.

## OpenClaw/Hermes benchmark correction

### OpenClaw match targets

Forge must eventually match:

- Self-hosted local/server deployment.
- Long-running agent workflows.
- Tool execution.
- Messaging or command entry points.
- File/system task execution.
- Coding/GitHub workflows.
- Skill or plugin extensibility.

Forge should exceed:

- Safer default execution.
- Stronger approval gates.
- Better audit logs.
- More visible tool risk metadata.
- Rollback-first file operations.
- Less hidden authority.

### Hermes Agent match targets

Forge must eventually match:

- Persistent memory.
- Experience accumulation.
- Self-improving skill loops.
- Skill creation and refinement.
- Multi-environment operation.
- Low-cost self-hosted use.

Forge should exceed:

- More visible memory storage.
- Stronger forget/quarantine/restore semantics.
- Explicit sensitive memory policy.
- Exportable memory bundles.
- Governed skill lifecycle instead of uncontrolled self-modification.

## Immediate next PR sequence

Do not start `v2.7 Agent Execution Pipeline` directly.

Use this sequence first:

1. **PR A: stabilization documents**
   - `COMPETITIVE_BENCHMARK.md`
   - `STABILIZATION_AUDIT.md`

2. **PR B: ask extraction with no behavior change**
   - Extract `ask_options.py`.
   - Extract `ask_service.py`.
   - Preserve tests.

3. **PR C: memory extraction with no behavior change**
   - Extract memory models/audit/recall helpers.
   - Preserve public `MemoryStore` API.

4. **PR D: CLI handler extraction with no behavior change**
   - Split command handlers.
   - Preserve JSON output contracts.

5. **PR E: v2.7 Agent Execution Pipeline**
   - Only after architecture is stable.

## Decision rule during stabilization

A change is allowed only if it does one of these:

- Clarifies product direction.
- Reduces file responsibility.
- Preserves existing behavior while improving structure.
- Adds tests that protect existing behavior.
- Improves OpenClaw/Hermes benchmark accuracy.

A change is not allowed if it:

- Adds a new feature.
- Adds a new command.
- Expands `entrypoint.py`, `cli.py`, or `memory.py` further.
- Changes behavior without a stabilization reason.
- Makes the project look more impressive but harder to maintain.
