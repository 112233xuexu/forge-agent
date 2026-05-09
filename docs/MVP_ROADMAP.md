# MVP Roadmap

Forge Agent should move from RC10 source release to a usable product through small, public, evidence-backed milestones.

## Phase 0: Public foundation

Status: in progress.

- Public MIT-licensed repository.
- README, contribution guide, security policy, architecture notes.
- Installable Python package skeleton.
- GitHub Actions smoke CI.
- Roadmap issue and OpenAI OSS application notes.

## Phase 1: Usable local CLI

Goal: a user can install the package and run useful local automation without understanding the internals.

Tasks:

- Normalize the full RC10 source tree into normal tracked files.
- Keep the `forge-agent do` interface stable.
- Add `forge-agent init` to create a workspace.
- Add `forge-agent tasks` to list local task history.
- Add `forge-agent approve` for approval-gated actions.
- Add tests for CLI flows and state persistence.

Exit criteria:

- Fresh clone installs with `pip install -e .`.
- `forge-agent do "create a project status note"` produces a persisted task record.
- `forge-agent doctor` reports environment health.
- CI passes on push.

## Phase 2: Ordinary-user desktop MVP

Goal: non-technical users can use the product without a terminal.

Tasks:

- Wire desktop UI to local Python runtime.
- Show task inbox, approvals, run history, and audit trail.
- Add safe defaults for local workspace storage.
- Add screenshots and a short demo video.
- Keep installer claims honest until signing and notarization are real.

Exit criteria:

- Desktop source builds in CI or documented local builder.
- User can submit a goal and see task status.
- Demo assets are checked in or linked from release notes.

## Phase 3: Commercialization readiness

Goal: prove that Forge Agent can become a product, not just a code archive.

Tasks:

- Define paid/pro boundaries.
- Add connector architecture notes.
- Create example workflows for creators, small businesses, and open-source maintainers.
- Add telemetry-free local analytics for task success/failure counts.
- Add exportable audit report.

Exit criteria:

- Three end-to-end examples run from docs.
- Product strategy and pricing hypothesis are public.
- First external feedback issue is captured.

## Phase 4: OpenAI OSS application strengthening

Goal: make the repository credible for the Codex for Open Source application.

Tasks:

- Keep GitHub activity visible through commits and issues.
- Add labeled good-first-issue tasks.
- Document how Codex would help maintain the project.
- Add test coverage and security-focused issues.
- Avoid exaggerated claims about adoption or production readiness.

Exit criteria:

- README has a clean project pitch.
- Public roadmap issues exist.
- CI and tests are visible.
- Application text is ready and honest.
