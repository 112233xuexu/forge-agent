# Demo script

Use this script to verify Forge Agent from a clean checkout.

## Install

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

## Preview a task

```bash
forge-agent ask "organize my invoices by month" --json
```

Expected result: a structured preview. This command should not change files.

## Run the safe demo

```bash
forge-agent demo --kind file-organizer
```

Expected result: Forge creates and uses a temporary sandbox. Real user files are not touched by the demo.

## Verify the RC10 compatibility slice

```bash
python -m pytest -q tests/test_memory_engine_pipeline.py tests/test_memory_hardening_pipeline.py tests/test_palace_graph_compat.py tests/test_context_builder_compat.py tests/test_ask_rc10_context_integration.py tests/test_rc10_state_compat.py tests/test_state_store_extended_compat.py tests/test_planner_registry_compat.py tests/test_gateway_runtime_compat.py tests/test_desktop_adapter_compat.py tests/test_http_adapter_compat.py tests/test_workflow_compat.py tests/test_workflow_executor_compat.py tests/test_runtime_execution_compat.py tests/test_skill_lifecycle_compat.py tests/test_governance_compat.py tests/test_runtime_policy_compat.py tests/test_benchmark_compat.py
```

Expected result: all selected tests pass.

## Honest demo notes

- Show only features that are actually wired.
- Do not claim production autonomy.
- Do not claim broad live app connectors yet.
- Keep screenshots and GIFs matched to real command output.
