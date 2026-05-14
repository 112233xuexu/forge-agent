# Forge Agent v2.0.0: Product hardening

v2.0 hardens the v1.9 ordinary-user MVP instead of expanding the product surface.

## What changed

- Friendlier CLI error surface for local file problems.
- `forge-agent --workspace <path> ask "..." --json` now works consistently.
- `forge-agent --workspace=<path> ask "..." --json` also works.
- `forge-agent ask --help` now gives direct usage guidance.
- Empty `forge-agent ask` requests now return a clear error.
- `forge-agent ask --json` with no request returns a structured JSON error.
- Brain Adapter behavior is covered by broader deterministic tests.

## Product meaning

v2.0 makes Forge Agent feel more like a product for ordinary users:

```text
clear input -> clear plan -> clear safety boundary -> clear error when something is wrong
```

## Validation

```bash
python -m compileall src tests
python -m pytest -q tests/test_public_runtime.py tests/test_organizer.py tests/test_skills_lifecycle.py tests/test_product_packs.py tests/test_brain_adapter.py tests/test_entrypoint_errors.py tests/test_entrypoint_workspace.py tests/test_entrypoint_ask_validation.py
forge-agent ask --help
forge-agent --workspace /tmp/forge-agent-ci-ask ask "organize my receipts" --json
```

## Honest limitations

- v2.0 is still local-first.
- Provider-backed planning is not included yet.
- Some content outputs remain Markdown/template-first.
- The schedule registry records schedules but does not yet run as a background service.
