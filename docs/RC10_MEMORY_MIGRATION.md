# RC10 compatibility migration

This branch moves runnable compatibility subsystems from the prepared RC10 source archive into the normal repository source tree.

## Added memory modules

- `memory_guard.py`, `memory_freshness.py`, `memory_ranking.py`, `memory_resolution.py`, `memory_verdict.py`, and `memory_engine.py` add the core memory pipeline.
- `memory_continuity.py`, `memory_soak.py`, `memory_recovery.py`, and `memory_quarantine.py` add memory hardening.

## Added palace graph and context builder base

- `palace_graph.py` adds an in-memory context graph with nodes, edges, path normalization, search, shortest paths, and recall-hit path filtering.
- `context_builder.py` converts recall hits into context packs with focus path, breadcrumbs, related paths, and ranked hits.
- This does not replace the existing `MemoryStore`; it gives future integration a tested context-path layer.

## Added state compatibility base

- `models.py` includes RC10-compatible checkpoint/session primitives.
- `session_state.py` adds a deliberately small `StateStore` subset for sessions, messages, and checkpoints.

## Added planner, gateway, and runtime compatibility base

- `contracts.py` adds small Protocol contracts for channel/runtime/store/tool boundaries.
- `tool_registry.py` adds the callable tool registry subset.
- `normalization.py` adds planner token normalization.
- `planner.py` adds the stable simple planner subset for notes, follow-up, translation, and paraphrase tasks.
- `gateway.py` adds local/webhook channel, session binding, envelope, reply, delivery, and planner routing.
- `runtime_compat.py` adds `CompatRuntime`, an isolated facade for state + planner + gateway tests.

## Added workflow, execution, and skill compatibility base

- `workflow.py` adds workflow nodes, workflow bundles, argument resolution, dependency ordering, and readiness inspection.
- `workflow_executor.py` adds local registered-tool execution for workflow bundles and task plans.
- `CompatRuntime` supports optional `execute=True`; default behavior remains planning-only.
- `skill_lifecycle.py` adds `TaskTrace`, `SkillDefinition`, `PromotionDecision`, `SkillLifecycleEngine`, and `SkillLibrary`.
- Repeated successful traces can promote to a reusable workflow skill.
- This does not replace the existing public `skills.py` / `SkillStore` path.

## Added governance and ledger compatibility base

- `governance.py` adds `GovernancePolicy`, `GovernanceVerdict`, `GovernanceEngine`, `LedgerEntry`, and ledger replay helpers.
- `CompatRuntime` supports optional `govern=True`; default behavior remains ungated.
- The governance layer can allow, pause for confirmation, or stop a plan before optional local execution.
- This does not replace existing approvals/history modules.

## Why this is additive

The current public CLI and runtime already include later ordinary-user task-card work. This migration intentionally does not overwrite those files. The migrated subsystems are introduced as additive modules so follow-up PRs can connect them to `ask`, task planning, workspace state, and user-facing output without regressing the existing command registry.

The full RC10 runtime stack is larger than this PR. It includes benchmarks, desktop bridge, HTTP adapters, and many persistence tables. Those pieces should continue to migrate as tested slices instead of one bulk replacement.

## Verification

The test coverage added by this branch includes:

- `tests/test_memory_engine_pipeline.py`
- `tests/test_memory_hardening_pipeline.py`
- `tests/test_palace_graph_compat.py`
- `tests/test_context_builder_compat.py`
- `tests/test_rc10_state_compat.py`
- `tests/test_planner_registry_compat.py`
- `tests/test_gateway_runtime_compat.py`
- `tests/test_workflow_compat.py`
- `tests/test_workflow_executor_compat.py`
- `tests/test_runtime_execution_compat.py`
- `tests/test_skill_lifecycle_compat.py`
- `tests/test_governance_compat.py`
- `tests/test_runtime_policy_compat.py`

Run locally with:

```bash
python -m pytest tests/test_memory_engine_pipeline.py tests/test_memory_hardening_pipeline.py tests/test_palace_graph_compat.py tests/test_context_builder_compat.py tests/test_rc10_state_compat.py tests/test_planner_registry_compat.py tests/test_gateway_runtime_compat.py tests/test_workflow_compat.py tests/test_workflow_executor_compat.py tests/test_runtime_execution_compat.py tests/test_skill_lifecycle_compat.py tests/test_governance_compat.py tests/test_runtime_policy_compat.py
```
