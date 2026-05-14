# Changelog

## v2.1.0-file-safety

Hardens approved file organization by preventing destination overwrites and making skipped files visible in JSON and manifests.

### Added

- Destination-collision protection for approved organize operations.
- `OrganizeResult.skipped_files` for skipped file evidence.
- `skipped_files` in operation manifests.
- `skipped_files` in the latest `organize-manifest.json`.
- Test coverage for skipped-file JSON and manifest output.
- Documentation: `docs/RELEASE_NOTES_V2_1.md`.

### Product meaning

v2.1 improves trust for ordinary users.

```text
safe preview -> explicit approval -> no overwrite -> visible skipped file evidence
```

### Honest limitation

v2.1 reports skipped files but does not yet provide an interactive conflict-resolution UI.

## v2.0.0-product-hardening

Hardens the v1.9 ordinary-user MVP with better CLI consistency, input validation, user-facing error handling, and stronger deterministic Brain Adapter tests.

### Added

- `forge-agent --workspace <path> ask "topic" --json`.
- `forge-agent --workspace=<path> ask "topic" --json`.
- `forge-agent ask --help` usage output.
- Structured JSON error output for missing `ask` requests.
- Entry-point tests for friendly CLI error handling.
- Workspace-aware `ask` tests.
- Ask validation tests.
- Expanded Brain Adapter stability tests, including fallback, metadata, safety level, report, and Chinese storyboard planning.
- Documentation: `docs/RELEASE_NOTES_V2_0.md`.

### Product meaning

v2.0 focuses on making the existing product harder rather than expanding the product surface.

```text
clear input -> clear plan -> clear safety boundary -> clear error when something is wrong
```

### Honest limitation

v2.0 is still local-first. Provider-backed planning, signed installers, background scheduling, and rendered binary artifacts remain future work.

## v1.9.0-brain-adapter

Adds a local Brain Adapter planning layer for ordinary-language requests.

### Added

- `forge-agent ask "topic" --json`.
- `BrainAdapter` and `BrainPlan` for deterministic local planning.
- Ask-aware CLI entrypoint wrapper.
- Structured plan fields including intent, next step, safety level, suggested command, confidence, notes, and metadata.
- Brain Adapter tests and CI smoke coverage.
- Documentation: `docs/V1_9_BRAIN_ADAPTER.md`.

### Product principle

```text
Brain suggests. Forge Agent governs.
```

The Brain Adapter suggests a structured plan. Forge Agent remains responsible for preview, approval, evidence, history, rollback, and skill lifecycle behavior.

### Honest limitation

This is a local deterministic planning layer first. It does not yet add provider-backed planning, hidden background work, or autonomous execution.

## v1.8.0-video-storyboard

Adds a local video/storyboard skill pack for ordinary users who need a simple content-production starting point.

### Added

- `forge-agent make storyboard "topic"`.
- Markdown storyboard artifact generation.
- 30-second video structure template.
- Asset checklist for screen recording, captions, voiceover, and title cards.

### Honest limitation

This does not yet render video, generate voiceover, or run FFmpeg. It creates a production-ready storyboard template first.

## v1.7.0-news-brief

Adds a local news brief template skill pack.

### Added

- `forge-agent make news "topic"`.
- Offline news brief artifact generation.
- Monitoring checklist and briefing structure.

### Honest limitation

This does not yet fetch live news. Later versions should add web sources, citations, deduplication, and scheduled delivery.

## v1.6.0-content-artifacts

Adds local PPT/report artifact generation.

### Added

- `forge-agent make ppt "topic"`.
- `forge-agent make report "topic"`.
- Artifact index under `.forge-agent/artifacts/index.jsonl`.
- Markdown output artifacts as deterministic local first versions.

### Honest limitation

This does not yet render `.pptx`, `.docx`, or `.pdf`. Later versions should connect document renderers.

## v1.5.0-schedule-registry

Adds a visible local schedule registry for future automations.

### Added

- `forge-agent schedule add "every day 9am" forge-agent organize ~/Downloads`.
- `forge-agent schedule list`.
- `forge-agent schedule pause <task_id>`.
- `forge-agent schedule resume <task_id>`.
- Schedule storage under `.forge-agent/schedules.jsonl`.

### Honest limitation

This stores schedules and state safely. It does not yet run a background daemon.

## v1.4.0-operation-history

Adds a local operation history surface.

### Added

- `forge-agent history list`.
- `forge-agent history show <operation_id>`.
- History reads operation manifests under `.forge-agent/operations`.
- Tests for history listing and manifest inspection.

## v1.3.0-rollback

This upgrade adds rollback support for approved organize operations so ordinary users can undo file moves safely.

### Added

- `forge-agent organize-rollback` to rollback the latest approved organize operation.
- `forge-agent organize-rollback --operation-id <operation_id>` for targeted rollback.
- Operation manifests under `.forge-agent/operations/`.
- Latest operation pointer: `.forge-agent/operations/latest-organize.json`.
- Safe rollback rules that skip instead of overwriting when the original path already exists.
- Rollback metadata in operation manifests: `rolled_back_at`, `restored_files`, and `skipped_files`.
- Tests for rollback restoration and safe skip behavior.
- Documentation: `docs/V1_3_ROLLBACK.md`.

### Product meaning

Forge Agent now supports a safer ordinary-user loop: dry-run, explicit approval, execution, evidence, and rollback.

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
python -m pytest -q tests/test_public_runtime.py tests/test_organizer.py tests/test_skills_lifecycle.py tests/test_product_packs.py
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
