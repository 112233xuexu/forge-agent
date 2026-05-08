# Forge Agent

Forge Agent is an experimental self-growing agent runtime for ordinary-user automation. Users submit goals through a single `forge-agent do` entrypoint, while the runtime coordinates session state, memory, tool routing, scheduling, recovery, governance, audit trails, and release evidence.

This repository is intended as an open-source release of the Forge Agent RC10 source tree.

## What is included

- Python runtime and CLI package under `src/forge_agent`.
- Desktop shell source based on Tauri.
- Tests, release check scripts, and release evidence reports.
- Documentation for architecture, operator usage, desktop release, and validation.

## Status

- Package version: `1.0.0rc10`.
- CLI entrypoint: `forge-agent`.
- License: MIT.
- Release honesty: this source release does not claim signed installers or production field reliability.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
forge-agent --help
```

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
forge-agent --help
```

## Validation

Useful local checks:

```bash
python -m compileall src tests
python -m pytest --collect-only -q
python -m pytest -q
```

The RC10 source package collected 517 pytest tests in the prepared environment. Full release evidence is preserved in the release notes and installer report files from the source package.

## Open-source roadmap

- Keep release claims evidence-backed.
- Improve the public demo and screenshots.
- Harden desktop packaging and signing evidence.
- Expand examples for agent runtime, governance, and gateway workflows.
- Use Codex-style review to triage issues, write tests, and improve security posture.

## Repository owner

Maintained by `jiangmingyue` / `112233xuexu`.
