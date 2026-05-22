# Release notes: v0.10.0 RC10 compatibility

This release candidate moves Forge Agent from a CLI MVP toward a larger local-first ordinary-user agent runtime.

## Highlights

- Rewritten README with a 3-minute quickstart.
- RC10 compatibility migration in tested slices.
- New memory engine and memory hardening modules.
- Palace graph and context builder.
- Ask integration now attaches RC10 memory/context metadata while preserving existing `memory_used` output.
- Checkpoint/session models and extended StateStore persistence.
- Tool registry, simple planner, gateway, and CompatRuntime.
- Workflow model and local workflow executor.
- Reusable skill lifecycle compatibility layer.
- Governance verdicts and ledger replay.
- Desktop/client adapter and HTTP payload adapter.
- Compatibility benchmark harness.
- RC10 compatibility CI workflow.
- Open-source readiness docs, demo script, roadmap, architecture overview, code of conduct, and issue templates.

## User-visible behavior

The stable public CLI remains the main user path:

```bash
forge-agent ask "organize my invoices by month" --json
forge-agent demo --kind file-organizer
forge-agent organize ./invoices
forge-agent organize ./invoices --approve
forge-agent organize-rollback
forge-agent history list
forge-agent skills
```

The ask path now has RC10 memory/context metadata in addition to the existing task-card output.

## Compatibility notes

This release does not bulk-overwrite the existing runtime. Most RC10 modules are additive compatibility layers. Default behavior changes only where tests cover compatibility.

## What this release does not claim

- No production autonomous agent behavior.
- No broad live app connectors by default.
- No OAuth flows.
- No signed desktop installer.
- No production web server.
- No background daemon.

## Verification

Run:

```bash
python -m compileall src tests
python -m pytest -q
```

For the RC10 compatibility slice:

```bash
python -m pytest -q tests/test_memory_engine_pipeline.py tests/test_memory_hardening_pipeline.py tests/test_palace_graph_compat.py tests/test_context_builder_compat.py tests/test_ask_rc10_context_integration.py tests/test_rc10_state_compat.py tests/test_state_store_extended_compat.py tests/test_planner_registry_compat.py tests/test_gateway_runtime_compat.py tests/test_desktop_adapter_compat.py tests/test_http_adapter_compat.py tests/test_workflow_compat.py tests/test_workflow_executor_compat.py tests/test_runtime_execution_compat.py tests/test_skill_lifecycle_compat.py tests/test_governance_compat.py tests/test_runtime_policy_compat.py tests/test_benchmark_compat.py
```

## Recommended tag

After PR #59 is merged and CI is green:

```text
v0.10.0-rc10-compat
```
