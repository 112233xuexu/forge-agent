# RC10 memory, state, planner, gateway, and workflow migration

This branch moves runnable memory, state, planner, gateway, and workflow compatibility subsystems from the prepared RC10 source archive into the normal repository source tree.

## Added core memory modules

- `src/forge_agent/models.py` with `MemoryRecallHit`, the shared recall candidate model.
- `src/forge_agent/memory_guard.py` with local text normalization and task anchoring helpers.
- `src/forge_agent/memory_freshness.py` with deterministic freshness weighting.
- `src/forge_agent/memory_ranking.py` with query profiling and ranked recall output.
- `src/forge_agent/memory_resolution.py` with conflict suppression by semantic slot.
- `src/forge_agent/memory_verdict.py` with final adoption/rejection metadata.
- `src/forge_agent/memory_engine.py` with the composed public pipeline.

## Added memory hardening modules

- `src/forge_agent/memory_continuity.py` with focus digesting and drift comparison.
- `src/forge_agent/memory_soak.py` with contamination scoring and stable-window tracking.
- `src/forge_agent/memory_recovery.py` with guarded re-anchor decisions.
- `src/forge_agent/memory_quarantine.py` with off-focus/stale/conflict filtering.

## Added state compatibility base

- `src/forge_agent/models.py` now also includes RC10-compatible checkpoint/session primitives.
- `src/forge_agent/session_state.py` adds a deliberately small `StateStore` subset for sessions, messages, and checkpoints.

## Added planner and tool compatibility base

- `src/forge_agent/contracts.py` adds small Protocol contracts for channel/runtime/store/tool boundaries.
- `src/forge_agent/tool_registry.py` adds the RC10 callable tool registry subset.
- `src/forge_agent/normalization.py` adds the text token normalization subset needed by the planner.
- `src/forge_agent/planner.py` adds the stable simple planner subset for notes, follow-up, translation, and paraphrase tasks.
- `src/forge_agent/__init__.py` exports the migrated state/planner/runtime compatibility surfaces.

## Added gateway and runtime compatibility base

- `src/forge_agent/gateway.py` adds the local/webhook channel, session binding, envelope, reply, delivery, and planner routing subset.
- `src/forge_agent/runtime_compat.py` adds `CompatRuntime`, an isolated facade for state + planner + gateway integration tests.
- This does not replace the existing public `ForgeRuntime` in `src/forge_agent/runtime.py`.

## Added workflow compatibility base

- `src/forge_agent/workflow.py` adds workflow nodes, workflow bundles, argument resolution, dependency ordering, and readiness inspection.
- `src/forge_agent/workflow_executor.py` adds local registered-tool execution for workflow bundles and task plans.
- `CompatRuntime` now supports optional `execute=True`; default behavior remains planning-only.

## Why this is additive

The current public CLI and runtime already include later ordinary-user task-card work. This migration intentionally does not overwrite those files. The migrated subsystems are introduced as additive modules so follow-up PRs can connect them to `ask`, task planning, workspace state, and user-facing output without regressing the existing command registry.

The full RC10 runtime stack is larger than this PR. It includes skill lifecycle, palace graph, benchmarks, ledger replay, governance, HTTP adapters, and many persistence tables. Those pieces should continue to migrate as tested slices instead of one bulk replacement.

## Verification

The test coverage added by this branch includes:

- `tests/test_memory_engine_pipeline.py`
- `tests/test_memory_hardening_pipeline.py`
- `tests/test_rc10_state_compat.py`
- `tests/test_planner_registry_compat.py`
- `tests/test_gateway_runtime_compat.py`
- `tests/test_workflow_compat.py`
- `tests/test_workflow_executor_compat.py`
- `tests/test_runtime_execution_compat.py`

Run locally with:

```bash
python -m pytest tests/test_memory_engine_pipeline.py tests/test_memory_hardening_pipeline.py tests/test_rc10_state_compat.py tests/test_planner_registry_compat.py tests/test_gateway_runtime_compat.py tests/test_workflow_compat.py tests/test_workflow_executor_compat.py tests/test_runtime_execution_compat.py
```
