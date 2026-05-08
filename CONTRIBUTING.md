# Contributing

Thanks for considering a contribution to Forge Agent.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -e .
python -m pytest --collect-only -q
```

## Expectations

- Keep release claims evidence-backed. Do not claim signed installers, production telemetry, or field reliability without checked-in evidence.
- Add or update tests for behavior changes.
- Keep generated artifacts, local databases, credentials, and signing material out of commits.
- Prefer small pull requests with clear motivation and validation notes.

## Useful checks

```bash
python -m compileall src tests
python -m pytest -q tests/test_cli.py tests/test_gateway.py tests/test_runtime.py
python -m pytest -q
```
