# v1.0.0-oss-demo-candidate

## Purpose

This release candidate exists to make Forge Agent reviewable as an open-source project and as an OpenAI Codex for OSS / Pro application candidate.

It is not a production GA release. It is a public demo candidate focused on one clear product proof:

> ordinary command -> automatic skill -> approval -> safe execution -> evidence -> reuse

## Main demo

```bash
forge-agent demo --kind file-organizer
```

JSON mode:

```bash
forge-agent demo --kind file-organizer --json
```

## What the demo proves

- The user gives a normal-language file organization goal.
- Forge Agent creates or selects a local reusable skill.
- Forge Agent records approval before moving files.
- Forge Agent organizes only sandbox files.
- Forge Agent writes `manifest.json` as evidence.
- Forge Agent runs a second similar batch and proves skill reuse with `reuse_proven: true`.

## CI validation

The GitHub Actions workflow validates:

- Python 3.11 and 3.12 setup.
- Editable package installation.
- Source/test compilation.
- Public runtime and demo tests.
- `forge-agent demo --kind file-organizer --json`.
- Manifest evidence: `created_skill`, `reuse_proven`, `moved_files`, approvals ledger, and skill index.

## Included product documents

- `docs/PROJECT_VISION.md`
- `docs/COMPETITIVE_ANALYSIS.md`
- `docs/ORDINARY_USER_DEMO.md`
- `docs/PRO_APPLICATION_READY.md`
- `docs/VALIDATION.md`

## Honest limitations

- This is an early OSS demo candidate.
- The deterministic demo runs in a sandbox and should not be confused with production file automation.
- The larger RC10 runtime is still being normalized into the public repo.
- Broad adoption metrics are not yet available.
- The project does not claim signed installers or production telemetry.

## Suggested release title

`v1.0.0-oss-demo-candidate: ordinary-user skill autopilot demo`

## Suggested release notes

Forge Agent v1.0.0-oss-demo-candidate introduces a public ordinary-user demo that demonstrates the project's core product loop: a plain-language command, automatic skill creation, approval before risky file operations, safe sandbox execution, evidence output, and skill reuse. This release candidate is designed for review, feedback, and OpenAI Codex for OSS application support.
