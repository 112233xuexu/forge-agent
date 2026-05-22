# Forge Agent Stabilization Audit

This document freezes random feature expansion and records what must be stabilized before more runtime functionality is added.

## Current operating rule

Forge is being repositioned as an AI butler for ordinary users:

```text
普通人不用学软件，也能一句话把事情办完。
```

The product target remains:

```text
simple request -> clear plan -> confirm important actions -> execute through apps/tools -> record result -> recover/correct when possible -> remember useful preferences for next time
```

The backend must stay maintainable while moving toward lower user learning cost and lower user time cost.

## Current repository status

This audit was refreshed after the RC10 source-archive migration work began.

| Area | Current status | Rule |
|---|---|---|
| Product positioning | Ordinary-user direction is the protected direction. | Keep user-facing language plain. |
| Ask wrapper | `entrypoint.py` routes ask and delegates parsing/service/presentation. | Do not expand `entrypoint.py` again. |
| CLI router | `cli.py` composes parsers through `commands/registry.py`; command handlers are already split into command modules. | Keep `cli.py` thin; avoid reintroducing command business logic. |
| Task cards | Ordinary-user task-card model and ask output work already landed before this migration. | Keep task-card wording ordinary-user-first. |
| Existing memory store | `memory.py` remains the public `MemoryStore` compatibility/service layer backed by `memory_models.py`, `memory_audit.py`, and `memory_recall.py`. | Preserve public CLI/API behavior. |
| RC10 memory subsystems | PR #59 migrates memory engine/hardening modules additively and does not wire them into runtime by default. | Do not blindly overwrite current stable runtime paths. |
| Source archive | The uploaded RC10 archive is larger than the visible public repo and includes desktop, gateway, governance, release, and legacy demos. | Migrate by tested slices, not by bulk copy. |

## What must not happen

Do not continue by adding features directly into already-heavy files.

Do not blindly paste the whole RC10 archive over the current repo. The current repository already contains later cleanup work that must be preserved, including the command registry and ordinary-user task-card changes.

Do not expose engineering jargon as the product message. Internally technical terms may exist, but external output should prefer ordinary-user language.

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

## Stabilization phases

### S1: Product positioning and benchmark correction

Status: done enough to protect direction; keep refining language as docs change.

Exit criteria:

- The repo clearly states who Forge is for.
- The repo clearly states why ordinary users should care.
- The repo avoids leading with engineering jargon.

### S2: Extract ask orchestration

Status: completed.

Current shape:

| Module | Responsibility |
|---|---|
| `ask_options.py` | Parse and validate ask-specific flags. |
| `ask_service.py` | Build the ask plan and attach memory/tool/risk metadata. |
| `ask_presenter.py` | Render JSON and human-readable ask output. |
| `entrypoint.py` | Route console entrypoint and wrapper-owned ask command. |

Rule: do not expand `entrypoint.py` again.

### S3: Extract memory internals and migrate RC10 memory subsystems

Status: in progress.

Already present on `main`:

- `memory_models.py`
- `memory_audit.py`
- `memory_recall.py`
- public `MemoryStore` compatibility/service layer in `memory.py`

Currently migrating in PR #59:

- memory engine pipeline,
- freshness/ranking/resolution/verdict modules,
- continuity/soak/recovery/quarantine hardening modules,
- focused tests and migration notes.

Exit criteria:

- Existing memory tests still pass.
- Public CLI behavior unchanged.
- Migrated modules are tested before being wired into runtime.
- No source-archive module overwrites current stable behavior without an explicit compatibility check.

### S4: Full codebase cleanup audit

Status: still required.

Actions:

- Inventory every source and test file.
- Mark each file as keep/split/rename/deprecate/delete.
- Record test coverage for each critical path.
- Identify product-language mismatches.
- Compare uploaded archive modules against current repo modules before migration.

Exit criteria:

- Every source file has an assigned responsibility.
- Every major command path has a test owner.
- No new feature work starts from unclear code.

### S5: Split CLI handlers

Status: completed enough for the current public repo.

Current shape:

- `cli.py` builds parser/runtime and delegates to `commands.registry`.
- `commands/registry.py` composes command parsers and dispatches handlers.
- command modules own domain-specific CLI handlers.

Remaining rule:

- Keep command handlers out of `cli.py`.
- Preserve CLI behavior and JSON contracts.

### S6: Resume product feature work

Status: not yet.

Larger runtime features should wait until the migrated RC10 modules are reconciled with the current repo and the full cleanup audit is current.

## Immediate PR sequence from here

1. **PR #59: RC10 memory subsystem migration**
   - Additive memory modules.
   - Focused tests.
   - Migration audit docs.
   - No default runtime wiring yet.

2. **Next PR: runtime/session-state reconciliation**
   - Compare RC10 `models.py`, `session_state.py`, `runtime.py`, `planner.py`, and `gateway.py` against current public modules.
   - Migrate compatibility models before wiring memory hardening into planning.

3. **Next PR: full codebase inventory**
   - Source file inventory.
   - Test ownership map.
   - Keep/split/rename/deprecate/delete decisions.

4. **Next PR: user-facing integration**
   - Wire memory verdicts into ask/task-card metadata only after compatibility tests pass.

## Decision rule during stabilization

A change is allowed only if it does one of these:

- Clarifies ordinary-user product direction.
- Reduces file responsibility.
- Preserves existing behavior while improving structure.
- Adds tests that protect existing behavior.
- Reduces future user learning cost or time cost.
- Migrates RC10 source in a tested, compatibility-preserving slice.

A change is not allowed if it:

- Blindly overwrites current repo code with archive code.
- Adds a new command before cleanup.
- Expands `entrypoint.py`, `cli.py`, or `memory.py` again.
- Changes behavior without a stabilization reason.
- Makes the project look more impressive but harder to maintain.
- Uses engineering jargon as the product message.