# Forge Agent

Forge Agent is a local-first AI butler for ordinary users.

```text
普通人不用学软件，也能一句话把事情办完。
```

The goal is not to expose tools, APIs, scopes, prompts, registries, or agent internals. The goal is a simple workflow:

```text
plain request -> understandable plan -> confirmation when needed -> local execution -> evidence -> recovery/reuse
```

Forge is early-stage, but it already has a working CLI, local memory, approval-gated file organization, rollback evidence, task cards, skill lifecycle foundations, and RC10 compatibility layers for a larger runtime.

## What problem does it solve?

Ordinary users should not need to learn every app, CLI flag, automation rule, or recovery process just to finish routine work.

Forge aims to let a user say things like:

```text
Organize this folder of invoices by month.
Turn these notes into a clean report.
Remember how I like project reports formatted.
Show me what you will do before changing files.
Restore the last file organization if it was wrong.
```

Internally Forge can use memory, skills, workflow plans, confirmations, local tools, history, and recovery paths. Externally it should stay understandable.

## 3-minute quickstart

Requirements: Python 3.11+.

```bash
git clone https://github.com/112233xuexu/forge-agent.git
cd forge-agent
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e . pytest
forge-agent --help
```

Windows PowerShell:

```powershell
git clone https://github.com/112233xuexu/forge-agent.git
cd forge-agent
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e . pytest
forge-agent --help
```

Run the safe local demo:

```bash
forge-agent demo --kind file-organizer
```

Preview a task card:

```bash
forge-agent ask "organize my invoices by month" --json
```

Try the ordinary-user `do` entrypoint:

```bash
forge-agent do --preview --human "Summarize these notes: ship update"
forge-agent do --explain --human "Rewrite 'Need approval' in a warmer tone"
forge-agent do --execute --human "Summarize these notes: ship update"
```

`do` without flags keeps the legacy local task-record behavior. `--preview`, `--explain`, and `--execute` use the user-goal runner path. Add `--human` for a short ordinary-language summary; omit it to keep structured JSON output.

Run the RC10 compatibility smoke tests:

```bash
python -m pytest -q \
  tests/test_memory_engine_pipeline.py \
  tests/test_memory_hardening_pipeline.py \
  tests/test_palace_graph_compat.py \
  tests/test_context_builder_compat.py \
  tests/test_ask_rc10_context_integration.py \
  tests/test_rc10_state_compat.py \
  tests/test_state_store_extended_compat.py \
  tests/test_planner_registry_compat.py \
  tests/test_gateway_runtime_compat.py \
  tests/test_desktop_adapter_compat.py \
  tests/test_http_adapter_compat.py \
  tests/test_workflow_compat.py \
  tests/test_workflow_executor_compat.py \
  tests/test_runtime_execution_compat.py \
  tests/test_skill_lifecycle_compat.py \
  tests/test_governance_compat.py \
  tests/test_runtime_policy_compat.py \
  tests/test_benchmark_compat.py
```

## Current user-facing commands

Ask / preview:

```bash
forge-agent ask "organize my invoices by month" --json
forge-agent --workspace .forge-agent ask "make a project status deck" --json
forge-agent ask --help
```

Ordinary-user goal entrypoint:

```bash
forge-agent do "capture this goal in my local task ledger"
forge-agent do --preview --human "Summarize these notes: ship update"
forge-agent do --explain --human "Rewrite 'Need approval' in a warmer tone"
forge-agent do --execute --human "Summarize these notes: ship update"
forge-agent do --preview "Summarize these notes: ship update"
```

Dry-run-first file organization:

```bash
forge-agent organize ./invoices
forge-agent organize ./invoices --approve
forge-agent organize-rollback
```

Memory, skills, history, approvals, and schedules:

```bash
forge-agent memory --help
forge-agent skills
forge-agent history list
forge-agent approvals list
forge-agent schedule list
forge-agent doctor
```

Content templates:

```bash
forge-agent make ppt "project update"
forge-agent make report "monthly validation report"
forge-agent make news "AI agent ecosystem"
forge-agent make storyboard "30-second product demo"
```

## What works today

- Local CLI entrypoint: `forge-agent`.
- Brain Adapter planning through `forge-agent ask`.
- Ordinary-user `do --preview/--explain/--execute` path backed by `UserGoalRunner`.
- `do --human` for concise ordinary-language output.
- Ordinary-user task-card preview.
- Visible local Memory Palace with bounded recall and ask-time filters.
- Dry-run-first file organizer.
- Approval-gated organize execution.
- Rollback for approved organize operations.
- Operation history.
- Local skill lifecycle controls.
- Local content skill packs.
- Structured JSON errors for supported file-related failures.
- RC10 compatibility slices for memory, state, planner, gateway, workflow, execution, governance, context graph, desktop/client payloads, HTTP payloads, and benchmark smoke checks.

## RC10 compatibility migration

PR #59 migrates a larger RC10 runtime into the public repo in tested slices instead of bulk-overwriting current code.

Added or wired:

- memory engine and memory hardening;
- palace graph and context builder;
- ask replacement wiring for RC10 memory/context metadata;
- checkpoint/session models and extended `StateStore` persistence;
- tool registry, simple planner, gateway, and `CompatRuntime`;
- workflow model and local workflow executor;
- skill lifecycle compatibility layer;
- governance verdicts and ledger replay;
- desktop/client adapter and pure HTTP payload adapter;
- compatibility benchmark harness;
- dedicated RC10 compatibility CI workflow.

The first real replacement wiring is in `ask_service.py`: existing `MemoryStore.recall()` results are promoted into RC10 `MemoryRecallHit`, `memory_verdict`, `context_packs`, and `context_focus_path` metadata while preserving the old `memory_used` output shape.

The next user-facing replacement is `forge-agent do --preview/--explain/--execute`, which starts the zero-config user-goal runner path without breaking legacy `do` task records.

## What is intentionally not claimed yet

Forge Agent is not production-autonomous yet.

Current limitations:

- No broad live app connectors are enabled by default.
- No OAuth flows are shipped.
- No signed desktop installer is shipped.
- No production background daemon is shipped.
- `http_adapter.py` normalizes payloads but does not run a server.
- `desktop_adapter.py` normalizes local client requests but does not automate the OS.
- Content commands generate local structured artifacts/templates; they do not claim full rendered media production.
- RC10 compatibility layers are being wired into public behavior only when tests protect the change.

## Architecture

```text
CLI / ask presenter
  -> ask service
  -> Brain Adapter / SimplePlanner
  -> memory recall + RC10 memory engine
  -> context builder / palace graph
  -> task card preview

UserGoalRunner
  -> SkillLibrary match
  -> SimplePlanner fallback
  -> GovernanceEngine
  -> WorkflowExecutor when execution is requested

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

See `docs/ARCHITECTURE_OVERVIEW.md` for details.

## Project docs

- `docs/ARCHITECTURE_OVERVIEW.md`
- `docs/CAPABILITIES.md`
- `docs/USER_FILE_FLOW.md`
- `docs/OPEN_SOURCE_RELEASE_CHECKLIST.md`
- `docs/PRO_APPLICATION_READY.md`
- `docs/STABILIZATION_AUDIT.md`
- `docs/CODEBASE_CLEANUP_PLAN.md`
- `docs/RC10_MEMORY_MIGRATION.md`
- `docs/RC10_ADAPTER_MIGRATION.md`
- `docs/ORDINARY_USER_DEMO.md`
- `docs/DEMO_OUTPUT_SAMPLE.json`

## Development

Install editable dependencies:

```bash
python -m pip install -e . pytest
```

Compile and test:

```bash
python -m compileall src tests
python -m pytest -q
```

Run only RC10 compatibility tests:

```bash
python -m pytest -q tests/test_memory_engine_pipeline.py tests/test_memory_hardening_pipeline.py tests/test_palace_graph_compat.py tests/test_context_builder_compat.py tests/test_ask_rc10_context_integration.py tests/test_rc10_state_compat.py tests/test_state_store_extended_compat.py tests/test_planner_registry_compat.py tests/test_gateway_runtime_compat.py tests/test_desktop_adapter_compat.py tests/test_http_adapter_compat.py tests/test_workflow_compat.py tests/test_workflow_executor_compat.py tests/test_runtime_execution_compat.py tests/test_skill_lifecycle_compat.py tests/test_governance_compat.py tests/test_runtime_policy_compat.py tests/test_benchmark_compat.py
```

## Contributing

Please read:

- `CONTRIBUTING.md`
- `CODE_OF_CONDUCT.md`
- `SECURITY.md`

Project rule: do not bulk-copy archive code over the public repo. Migrate in tested slices, preserve CLI behavior, and update docs/tests with each behavior change.

## License

MIT. See `LICENSE`.
