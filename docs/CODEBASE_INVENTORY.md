# Forge Agent Codebase Inventory

This is the first file-by-file cleanup inventory for Forge Agent.

The purpose is to stop adding features on top of unclear code. Forge is being positioned as an AI butler for ordinary users. That means the backend may eventually connect many apps, but the codebase must remain understandable, testable, and easy to extend.

Product direction to protect:

```text
ordinary user request -> clear plan -> confirmation when important -> app/tool execution -> work record -> recovery when possible -> memory/skill reuse next time
```

## Inventory status

This is the initial inventory pass. It records the current responsibility, target responsibility, action, and priority for known source and test files.

A later cleanup PR should expand this into a stricter per-file checklist with line-level cleanup notes where needed.

## Source files

| File | Current responsibility | Target responsibility | Action | Priority | Test owner |
|---|---|---|---|---|---|
| `src/forge_agent/__init__.py` | Public package surface and version export. | Keep tiny public package surface. | Keep. | P2 | import/package smoke via CI. |
| `src/forge_agent/entrypoint.py` | Console entrypoint and ask routing after extraction. | Thin route-only entrypoint. | Keep thin; do not add product logic. | P0 | `test_entrypoint_*`. |
| `src/forge_agent/ask_options.py` | Ask-specific flag parsing. | Own ask option parsing and validation only. | Keep; direct tests added. | P1 | `test_ask_options.py`, `test_entrypoint_ask_validation.py`. |
| `src/forge_agent/ask_service.py` | Build ask plan and attach memory recall metadata. | Own ask orchestration service. | Keep; later attach ordinary-user task-card schema here, not in entrypoint. | P0 | `test_entrypoint_workspace.py`. |
| `src/forge_agent/ask_presenter.py` | Render ask output and ask errors. | Own ask presentation. | Keep; later improve user-facing wording. | P1 | `test_entrypoint_errors.py`. |
| `src/forge_agent/brain.py` | Deterministic planner and `BrainPlan`. | Planner model and local planning rules. | Keep; later split rules if planner grows. | P1 | `test_brain_adapter.py`. |
| `src/forge_agent/cli.py` | Builds most command parsers and handles many commands; memory command has been extracted. | Compose command parsers and dispatch only. | Continue splitting into `commands/*` modules. | P0 | CLI tests. |
| `src/forge_agent/cli_common.py` | Shared CLI JSON success/error/help helpers. | Common CLI presentation helpers. | Keep; avoid growing into business logic. | P1 | CLI tests. |
| `src/forge_agent/commands/__init__.py` | Commands package marker. | Commands package marker. | Keep. | P2 | import smoke via CI. |
| `src/forge_agent/commands/memory.py` | Memory command parser and handler. | Own memory CLI only. | Keep; do not add MemoryStore internals here. | P0 | `test_cli_memory.py`. |
| `src/forge_agent/memory.py` | Public `MemoryStore` plus remaining persistence/governance/search/export/doctor logic. | Public memory service/compatibility surface. | Keep API stable; continue extracting internals later. | P0 | `test_memory_store.py`, `test_cli_memory.py`. |
| `src/forge_agent/memory_models.py` | Memory dataclasses and constants. | Memory models only. | Keep. | P1 | memory tests. |
| `src/forge_agent/memory_audit.py` | Memory audit append/read helpers. | Memory audit helper module. | Keep. | P1 | memory tests. |
| `src/forge_agent/memory_recall.py` | Deterministic recall, scoring, tokenization, filters. | Recall algorithm module. | Keep; direct tests added. | P1 | `test_memory_recall.py`, memory store tests. |
| `src/forge_agent/approvals.py` | Approval ledger. | Internal approval records, user-facing “you confirm before I do it.” | Audit wording later; keep behavior now. | P1 | approval CLI/error tests. |
| `src/forge_agent/history.py` | Operation history. | Internal work record store, user-facing “what I did.” | Keep; later align with task-card result schema. | P1 | history/organizer tests. |
| `src/forge_agent/organizer.py` | File organizer workflow, dry-run, approved move, rollback evidence. | First proof workflow for preview-confirm-execute-record-restore. | Keep; later expose through ordinary-user task card. | P0 | organizer and rollback tests. |
| `src/forge_agent/file_organizer_demo.py` | Demo orchestration. | Ordinary-user demo scenario. | Keep; later make demo language less CLI/internal. | P1 | demo CI smoke. |
| `src/forge_agent/skills.py` | Skill store and lifecycle. | Skill memory/lifecycle for “do it like last time.” | Keep; later split persistence vs lifecycle vs recommendation. | P1 | `test_skills_lifecycle.py`. |
| `src/forge_agent/scheduler.py` | Schedule record store. | Future reminder/automation records. | Keep simple; do not deepen before confirmation model. | P2 | schedule smoke tests. |
| `src/forge_agent/content_packs.py` | Local PPT/report/news/storyboard templates. | User-facing content workflows. | Keep; later move toward app-backed document generation. | P2 | `test_product_packs.py`. |
| `src/forge_agent/runtime.py` | Runtime/task operations and public `ForgeRuntime`. | Local runtime service. | Audit after CLI split; avoid duplicating ask/tool logic. | P1 | `test_public_runtime.py`. |

## Immediate source cleanup decisions

### Keep stable now

- `entrypoint.py`
- `ask_options.py`
- `ask_service.py`
- `ask_presenter.py`
- `memory_models.py`
- `memory_audit.py`
- `memory_recall.py`
- `commands/memory.py`
- `cli_common.py`

These were created by stabilization work and should not be reworked again immediately unless tests reveal an issue.

### Current split status

`src/forge_agent/cli.py` is the major cleanup target.

Completed:

```text
src/forge_agent/commands/__init__.py
src/forge_agent/commands/memory.py
```

Remaining proposed split:

```text
src/forge_agent/commands/organize.py
src/forge_agent/commands/skills.py
src/forge_agent/commands/approvals.py
src/forge_agent/commands/history.py
src/forge_agent/commands/schedule.py
src/forge_agent/commands/make.py
```

Goal:

```text
cli.py composes commands; command modules own handlers.
```

### Later memory split target

`memory.py` is no longer the only memory file, but it still owns multiple behaviors.

Later possible split:

```text
memory_persistence.py
memory_governance.py
memory_palace.py
memory_export.py
memory_status.py
```

Do this only after CLI is split and tests are stable.

## Test files

| Test file | Protects | Action | Priority |
|---|---|---|---|
| `tests/test_public_runtime.py` | Public runtime behavior. | Keep; update only for intentional runtime changes. | P1 |
| `tests/test_organizer.py` | File organizer dry-run/approve behavior. | Keep; critical for ordinary-user recovery demo. | P0 |
| `tests/test_organizer_skipped_json.py` | Skipped-file JSON/manifest behavior. | Keep; protects safe file behavior. | P0 |
| `tests/test_rollback_evidence.py` | Rollback and operation evidence. | Keep; key recovery proof. | P0 |
| `tests/test_cli_json_errors.py` | JSON error contracts. | Keep; prevents automation-breaking text errors. | P0 |
| `tests/test_cli_json_consistency.py` | CLI JSON consistency. | Keep. | P0 |
| `tests/test_cli_skills_json_errors.py` | Skill CLI JSON errors. | Keep. | P1 |
| `tests/test_cli_approvals_json_errors.py` | Approval CLI JSON errors. | Keep. | P1 |
| `tests/test_cli_error_envelope.py` | CLI error envelope behavior. | Keep. | P1 |
| `tests/test_memory_store.py` | MemoryStore behavior. | Keep; expand if memory internals change. | P0 |
| `tests/test_cli_memory.py` | Memory CLI behavior. | Keep; critical before and after CLI split. | P0 |
| `tests/test_ask_options.py` | Ask options direct parsing behavior. | Keep. | P1 |
| `tests/test_memory_recall.py` | Memory recall direct scoring/filtering behavior. | Keep. | P1 |
| `tests/test_skills_lifecycle.py` | Skill lifecycle. | Keep; product pillar for repeated workflows. | P1 |
| `tests/test_product_packs.py` | Content pack generation. | Keep. | P2 |
| `tests/test_brain_adapter.py` | Local planner. | Keep; later expand for task-card schema. | P1 |
| `tests/test_entrypoint_errors.py` | Entrypoint/ask error handling. | Keep. | P0 |
| `tests/test_entrypoint_workspace.py` | Workspace-aware ask and memory use. | Keep. | P0 |
| `tests/test_entrypoint_ask_validation.py` | Ask validation and help behavior. | Keep. | P0 |

## Test coverage gaps

Add direct tests before changing these internals:

| Gap | Why it matters | Suggested file |
|---|---|---|
| CLI command module tests | Needed before/after splitting `cli.py`. | Existing CLI tests plus focused command tests. |
| Ordinary-user task-card schema | Needed before UI/app workflows. | `tests/test_task_card.py` |

## User-facing language audit

Current CLI output still uses many developer-facing words. That is acceptable for the current CLI, but the product-facing layer should later translate them.

| Current/internal wording | Product wording target |
|---|---|
| approval | confirm before I do it |
| rollback | restore / undo |
| audit | what I did |
| operation history | work history |
| skill | how I should do this next time |
| memory recall | what I remembered for this task |
| skipped files | files I was not sure about / files I left unchanged |

## Cleanup PR roadmap

### PR 1: Codebase inventory

Done.

Deliverable:

- `docs/CODEBASE_INVENTORY.md`.

### PR 2: Direct tests for extracted modules

Done.

Added behavior-preserving tests for:

- `ask_options.py`,
- `memory_recall.py`.

### PR 3: CLI command split, phase 1

In progress.

Extract memory command parser/handler first.

Reason:

Memory has strong tests and is a good first command extraction.

### PR 4: CLI command split, phase 2

Extract organizer/history/approvals/skills command handlers.

### PR 5: Ordinary-user task-card schema

Only after CLI is less monolithic.

## Definition of done for this cleanup stage

The cleanup stage is done when:

1. Every source file has a clear responsibility.
2. `cli.py` is no longer the command-handler monolith.
3. Memory internals are stable and tested.
4. Extracted modules have direct tests.
5. User-facing product wording has a clear owner.
6. Future app connectors can be added without editing one giant command file.
7. Future UI can call service modules directly instead of depending on CLI-only logic.
