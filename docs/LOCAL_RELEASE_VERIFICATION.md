# Local release verification

## Verification date

2026-05-09

## Scope

Validated the local `forge-agent-pro-application-demo-candidate.zip` package before relying on it for the OSS/Pro application path.

## Commands run

```bash
python -m compileall -q src tests
python -m pytest -q \
  tests/test_ordinary_user_big_version.py \
  tests/test_skill_growth.py \
  tests/test_user_goal.py \
  tests/test_system.py \
  tests/test_desktop_shell_static.py
```

## Results

- Compile check: passed.
- Selected release-critical tests: 92 passed.
- Covered areas:
  - ordinary-user big-version CLI/demo tests;
  - skill growth;
  - user-goal execution path;
  - system/version checks;
  - desktop shell static checks.

## Important finding

The local candidate package's legacy CLI accepts the file-organizer demo command, but the `--json` flag is not accepted by that legacy argument surface. The public GitHub README/CI path is being normalized around the simpler public CLI where JSON mode is documented. Before claiming a fully stable release, the CLI surfaces must be reconciled so the candidate zip and public GitHub behavior match exactly.

## Current release judgment

The repository is credible for an early OSS demo candidate, but should still be described as an **OSS demo candidate**, not a production release.

## Next checklist

- Reconcile public GitHub CLI and local candidate CLI for `forge-agent demo --kind file-organizer --json`.
- Ensure CI runs green on the public repository.
- Keep release notes honest about current limitations.
- Use `release/v1.0.0-oss-demo-candidate` as the release-candidate branch.
