# Final submission checklist for OpenAI Codex for Open Source

## Repository

- GitHub username: `112233xuexu`
- Repository: `https://github.com/112233xuexu/forge-agent`
- Maintainer role: primary maintainer / repository owner
- License: MIT
- Status: OSS demo candidate, not production GA

## Required repository evidence

- [x] Public README explains the project in ordinary language.
- [x] README includes a 60-second demo command.
- [x] Demo is deterministic and runs in a safe sandbox.
- [x] Demo proves automatic skill creation.
- [x] Demo proves approval before risky file operations.
- [x] Demo writes evidence to `manifest.json`.
- [x] Demo proves skill reuse with `reuse_proven: true`.
- [x] Approval ledger exists at `.forge-agent/demo-file-organizer/approvals.jsonl` after demo.
- [x] Skill index exists at `.forge-agent/demo-file-organizer/skills/index.jsonl` after demo.
- [x] CI workflow checks compile, tests, demo execution, and demo evidence.
- [x] Changelog and release-candidate notes exist.
- [x] Application submission text exists.

## Commands for reviewers

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
forge-agent demo --kind file-organizer
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
forge-agent demo --kind file-organizer
```

Validation commands:

```bash
python -m compileall src tests
python -m pytest -q tests/test_public_runtime.py
forge-agent demo --kind file-organizer --json
```

## Submission text

Use `docs/OPENAI_APPLICATION_SUBMISSION.md` for the application fields.

## Release tag recommendation

Create a GitHub Release manually if the GitHub UI is available:

- Tag: `v1.0.0-oss-demo-candidate`
- Title: `v1.0.0-oss-demo-candidate: ordinary-user skill autopilot demo`
- Body: copy from `docs/RELEASE_CANDIDATE.md` and `CHANGELOG.md`

## Honest limitations to keep in the application

- This is an early open-source demo candidate.
- The demo is sandboxed and does not touch real user files.
- The larger RC10 runtime is still being normalized into the public repository.
- The project does not yet have strong external usage metrics.

## Realistic readiness

Ready to submit as an early-stage OSS demo candidate. Success is not guaranteed because the official program favors critical open-source maintainers with visible ecosystem impact, but the repository now has a coherent product proof, demo, tests, CI workflow, and application narrative.
