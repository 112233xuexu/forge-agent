# Forge Agent v2.3.0: CLI JSON consistency

v2.3 continues the CLI reliability line by expanding structured JSON error output across more command groups.

## What changed

- `history show <missing> --json` now returns a structured JSON error.
- `schedule pause <missing> --json` now returns a structured JSON error.
- `schedule resume <missing> --json` now returns a structured JSON error.
- `skills --json show <missing>` now returns a structured JSON error.
- `skills --json promote <missing>` now returns a structured JSON error.
- `approvals decide <missing> --decision approved --json` now returns a structured JSON error.
- CI now covers history, schedule, skills, and approvals JSON failure behavior.

## Product meaning

v2.3 improves automation reliability beyond the v2.2 organize/rollback scope:

```text
JSON requested -> predictable JSON success or predictable JSON failure
```

## Validation

```bash
python -m pytest -q tests/test_cli_json_consistency.py tests/test_cli_skills_json_errors.py tests/test_cli_approvals_json_errors.py tests/test_cli_json_errors.py
python -m compileall src tests
```

## Honest limitations

- v2.3 improves multiple command groups, but does not yet guarantee every possible CLI failure is structured JSON.
- Argument-parser errors from `argparse` are still mostly default CLI text.
- Broader consistency for every edge case remains future work.
