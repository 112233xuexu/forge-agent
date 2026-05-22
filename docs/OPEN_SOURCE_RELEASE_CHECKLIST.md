# Open-source release checklist

Use this checklist before announcing a public Forge Agent release.

## Repository basics

- [ ] README explains the ordinary-user product thesis clearly.
- [ ] LICENSE is present and accurate.
- [ ] SECURITY.md explains how to report vulnerabilities.
- [ ] CONTRIBUTING.md explains local setup and tests.
- [ ] CODE_OF_CONDUCT.md is present.
- [ ] CI runs on supported Python versions.
- [ ] RC10 compatibility tests run in CI.

## Install and run

- [ ] `python -m pip install -e . pytest` works from a clean checkout.
- [ ] `python -m compileall src tests` passes.
- [ ] `python -m pytest -q` passes or documented subset passes.
- [ ] `forge-agent demo --kind file-organizer --json` runs locally.
- [ ] `forge-agent ask "organize my invoices by month" --json` runs locally.

## Honesty checks

- [ ] The project does not claim production readiness.
- [ ] The project does not claim live app connectors that are not implemented.
- [ ] The project does not claim a background daemon if one is not shipped.
- [ ] Screenshots/GIFs match actual command output.
- [ ] Release notes distinguish working features from compatibility layers.

## RC10 migration checks

- [ ] Compatibility modules are additive unless an integration test covers replacement behavior.
- [ ] Existing CLI/task-card behavior remains compatible.
- [ ] `ask` metadata includes RC10 memory/context fields when memory is enabled.
- [ ] State, planner, gateway, workflow, skill, governance, desktop adapter, HTTP adapter, and benchmark tests pass.

## Suggested release assets

- [ ] Short demo GIF or screenshot.
- [ ] Example JSON output for `forge-agent ask`.
- [ ] Example file-organizer manifest.
- [ ] Short architecture diagram or Mermaid graph.
- [ ] Known limitations section.
