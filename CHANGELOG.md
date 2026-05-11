# Changelog

## v1.2.0-skill-lifecycle

This upgrade makes Forge Agent skills manageable assets rather than invisible runtime artifacts.

### Added

- Skill lifecycle states: `draft`, `tested`, `validated`, `promoted`, `deprecated`, `quarantined`.
- Automatic status changes from successful and failed skill usage.
- Manual CLI controls:
  - `forge-agent skills show <skill_id>`
  - `forge-agent skills test <skill_id>`
  - `forge-agent skills validate <skill_id>`
  - `forge-agent skills promote <skill_id>`
  - `forge-agent skills deprecate <skill_id>`
  - `forge-agent skills quarantine <skill_id>`
- Lifecycle logs in generated skill markdown files.
- Tests for automatic promotion, quarantine behavior, manual controls, and matching exclusion.
- CI smoke test for skill lifecycle CLI commands.
- Documentation: `docs/V1_2_SKILL_LIFECYCLE.md`.

### Product meaning

Skills can now be created, reused, tested, validated, promoted, deprecated, or quarantined. This is a required step toward a future skill cloud/library because only trusted skills should be shared.

## v1.1.0-ordinary-user-mvp

This upgrade turns Forge Agent's safe demo into a real dry-run-first ordinary-user command.

### Added

- Real file organization command: `forge-agent organize ./invoices`.
- Dry-run mode by default, moving no real files.
- Explicit `--approve` mode for actual file movement.
- Optional `--output` folder.
- JSON output for automation and review.
- Approval ledger records for real organize plans.
- `organize-manifest.json` for approved moves.
- Tests for dry-run and approved file movement.
- CI smoke test for real organizer dry-run behavior.
- Documentation: `docs/V1_1_ORGANIZE_COMMAND.md`.

### Safety model

The organizer never moves real files by default. It previews planned moves first and only moves invoice/receipt-like files when the user explicitly passes `--approve`.

### Validation target

```bash
python -m compileall src tests
python -m pytest -q tests/test_public_runtime.py tests/test_organizer.py tests/test_skills_lifecycle.py
forge-agent demo --kind file-organizer --json
forge-agent organize ./invoices --json
```

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
