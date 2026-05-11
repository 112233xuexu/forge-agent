# Forge Agent

Forge Agent is a local-first automation agent for ordinary users. The goal is simple: the user gives one plain-language command, while Forge Agent finds or creates the needed skill, asks before risky actions, records evidence, and reuses the skill next time.

Forge Agent is being built as a zero-configuration skill autopilot, not another expert-only agent framework.

## Why it is different

Many agent projects expose skills, tools, providers, sandboxes, gateways, and registries directly to the user. Forge Agent's product direction is to hide that complexity by default:

```text
plain command -> intent -> local skill search -> auto-create skill if missing -> approval when risky -> execute in safe scope -> audit ledger -> skill reuse
```

## 60-second demo

Run the ordinary-user file organizer demo:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
forge-agent demo --kind file-organizer
```

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
forge-agent demo --kind file-organizer
```

The demo creates a safe sandbox and shows the core loop:

1. the user asks to organize invoices and receipts;
2. Forge Agent creates or selects a reusable skill;
3. Forge Agent records plain-language approval before moving files;
4. Forge Agent organizes files by month;
5. Forge Agent writes `manifest.json`;
6. Forge Agent runs a second batch to prove skill reuse with `reuse_proven: true`.

No real user files are touched by the demo.

## v1.1 real organize command

The v1.1 branch upgrades the demo into a real ordinary-user command. It is safe by default: dry-run previews the plan and moves nothing.

```bash
forge-agent organize ./invoices
forge-agent organize ./invoices --json
```

Move files only after explicit approval:

```bash
forge-agent organize ./invoices --approve
```

The command creates an approval record, uses the local skill store, and writes `organize-manifest.json` after approved moves.

See also:

- [Ordinary-user demo guide](docs/ORDINARY_USER_DEMO.md)
- [v1.1 organize command](docs/V1_1_ORGANIZE_COMMAND.md)
- [Demo output sample](docs/DEMO_OUTPUT_SAMPLE.json)
- [Release candidate notes](docs/RELEASE_CANDIDATE.md)
- [OpenAI OSS / Pro readiness notes](docs/PRO_APPLICATION_READY.md)

## Everyday commands

```bash
forge-agent init
forge-agent do "draft a project status note"
forge-agent organize ./invoices
forge-agent tasks
forge-agent skills
forge-agent approvals list
forge-agent doctor
```

## Current status

- Package version: `1.0.0rc10`.
- CLI entrypoint: `forge-agent`.
- License: MIT.
- Repository visibility: public.
- Demo: ordinary-user file organizer with approval ledger and skill reuse proof.
- v1.1 feature branch: real dry-run-first organize command.
- Release honesty: this source release does not claim signed installers, production telemetry, or broad field reliability.

## What is included

- Local runtime and CLI under `src/forge_agent`.
- Local skill store with automatic skill creation and reuse.
- Approval ledger for risky actions.
- Deterministic file organizer demo.
- Real dry-run-first organize command on the v1.1 feature branch.
- Product, MVP, commercialization, architecture, validation, and competitive-analysis docs.
- GitHub Actions smoke CI and tests for the public runtime/demo/organizer path.

## Validation

```bash
python -m compileall src tests
python -m pytest -q tests/test_public_runtime.py tests/test_organizer.py
forge-agent demo --kind file-organizer --json
forge-agent organize ./invoices --json
```

GitHub Actions validates Python 3.11 and 3.12, compile checks, public runtime/demo tests, organizer tests, the file-organizer demo, real organizer dry-run, and demo evidence files.

The original RC10 source package contains a larger runtime and test suite. The public repository is being normalized around the ordinary-user product surface first.

## Roadmap

- [Project Vision](docs/PROJECT_VISION.md)
- [Competitive Analysis](docs/COMPETITIVE_ANALYSIS.md)
- [MVP Roadmap](docs/MVP_ROADMAP.md)
- [Product Strategy](docs/PRODUCT_STRATEGY.md)
- [Commercialization Plan](docs/COMMERCIALIZATION_PLAN.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Validation](docs/VALIDATION.md)
- [OpenAI OSS Application Notes](docs/OPENAI_OSS_APPLICATION.md)

## OpenAI Codex for OSS fit

Forge Agent targets a real usability gap in open-source agent systems: skills, memory, gateways, and self-improvement are powerful, but ordinary users still face too much setup and skill-management friction. Codex would help review pull requests, triage issues, expand tests, harden approval/security paths, normalize the larger RC10 source tree, and maintain evidence-backed releases.

## Repository owner

Maintained by `jiangmingyue` / `112233xuexu`.
