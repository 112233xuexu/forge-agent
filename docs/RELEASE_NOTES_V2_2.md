# Forge Agent v2.2.0: CLI reliability

v2.2 continues product hardening by making Forge Agent's CLI more predictable for humans and automation.

## What changed

- `forge-agent organize <missing> --json` now returns a structured JSON error.
- `forge-agent organize-rollback --json` now returns a structured JSON error when no previous operation exists.
- File-related CLI errors use a shared helper for more consistent output.
- Human organize output now includes skipped file counts when applicable.
- CI now includes CLI JSON error coverage.

## Product meaning

v2.2 improves scriptability and reliability:

```text
JSON requested -> JSON success or JSON error -> stable automation behavior
```

## Validation

```bash
python -m pytest -q tests/test_cli_json_errors.py
python -m compileall src tests
forge-agent organize /missing/path --json
forge-agent --workspace /tmp/empty organize-rollback --json
```

## Honest limitations

- v2.2 does not yet make every CLI error structured.
- The current scope focuses on file-related organize and rollback failures.
- Broader JSON error consistency for history, schedules, skills, approvals, and content commands remains future work.
