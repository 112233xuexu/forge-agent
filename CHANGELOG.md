# Changelog

## v1.0.0-oss-demo-candidate

This is an open-source demo candidate for Forge Agent's ordinary-user skill autopilot direction.

### Added

- Ordinary-user file organizer demo: `forge-agent demo --kind file-organizer`.
- Local skill store with automatic skill creation and reuse.
- Plain-language approval ledger for risky actions.
- Demo evidence generation through `manifest.json`.
- Demo output sample for reviewers.
- CI validation for Python 3.11 and 3.12.
- Public documentation for project vision, competitive analysis, demo flow, release candidate, validation, and OpenAI OSS / Pro application readiness.

### Demonstrated product loop

```text
plain command -> automatic skill -> approval -> safe sandbox execution -> evidence -> skill reuse
```

### Validation target

```bash
python -m compileall src tests
python -m pytest -q tests/test_public_runtime.py
forge-agent demo --kind file-organizer --json
```

### Honest limitations

- This is not a production GA release.
- The file organizer demo runs in a generated sandbox and does not touch real user folders.
- The larger RC10 runtime is still being normalized into the public repository.
- Adoption metrics are still early.
