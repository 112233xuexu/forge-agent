# Forge Agent

Forge Agent is a local-first automation agent for ordinary users. The goal is simple: the user gives one plain-language command, while Forge Agent finds or creates the needed skill, asks before risky actions, records evidence, reuses the skill next time, and can roll back approved file operations.

Forge Agent is being built as a zero-configuration skill autopilot, not another expert-only agent framework.

## Why it is different

Many agent projects expose skills, tools, providers, sandboxes, gateways, and registries directly to the user. Forge Agent's product direction is to hide that complexity by default:

```text
plain command -> intent -> local skill search -> auto-create skill if missing -> approval when risky -> execute in safe scope -> audit ledger -> rollback -> skill reuse
```

v1.9 adds a local planning layer:

```text
ordinary request -> Brain Adapter plan -> Forge preview -> approval when needed -> evidence/history -> rollback where supported
```

The product rule is:

```text
Brain suggests. Forge Agent governs.
```

## 60-second demo

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

The demo creates a safe sandbox and proves automatic skill creation, approval, file organization, evidence, and skill reuse. No real user files are touched by the demo.

## Product commands

Brain Adapter planning:

```bash
forge-agent ask "organize my invoices by month" --json
forge-agent ask "make a project status deck" --json
```

Real dry-run-first file organization:

```bash
forge-agent organize ./invoices
forge-agent organize ./invoices --approve
forge-agent organize-rollback
```

Operation history:

```bash
forge-agent history list
forge-agent history show <operation_id>
```

Schedule registry:

```bash
forge-agent schedule add "every day 9am" forge-agent organize ~/Downloads
forge-agent schedule list
forge-agent schedule pause <task_id>
forge-agent schedule resume <task_id>
```

Content skill packs:

```bash
forge-agent make ppt "project status update"
forge-agent make report "monthly validation report"
forge-agent make news "AI agent ecosystem"
forge-agent make storyboard "30-second product demo"
```

Skill lifecycle:

```bash
forge-agent skills
forge-agent skills show <skill_id>
forge-agent skills promote <skill_id>
forge-agent skills quarantine <skill_id>
```

## Current capability map

- v1.1: real dry-run-first organize command.
- v1.2: skill lifecycle controls.
- v1.3: rollback for approved organize operations.
- v1.4: operation history.
- v1.5: schedule registry.
- v1.6: PPT/report artifact generation.
- v1.7: news brief template generation.
- v1.8: video storyboard generation.
- v1.9: Brain Adapter planning layer with `forge-agent ask`.

The v1.4-v1.9 features are local deterministic product surfaces first. They do not yet claim full live news retrieval, real background daemon execution, `.pptx` rendering, voiceover generation, video rendering, or provider-backed autonomous execution.

See also:

- [Ordinary-user demo guide](docs/ORDINARY_USER_DEMO.md)
- [v1.1 organize command](docs/V1_1_ORGANIZE_COMMAND.md)
- [v1.2 skill lifecycle](docs/V1_2_SKILL_LIFECYCLE.md)
- [v1.3 rollback](docs/V1_3_ROLLBACK.md)
- [v1.4-v1.8 product expansion](docs/V1_4_TO_V1_8_PRODUCT_EXPANSION.md)
- [v1.9 Brain Adapter](docs/V1_9_BRAIN_ADAPTER.md)
- [Demo output sample](docs/DEMO_OUTPUT_SAMPLE.json)
- [Release candidate notes](docs/RELEASE_CANDIDATE.md)
- [OpenAI OSS / Pro readiness notes](docs/PRO_APPLICATION_READY.md)

## Everyday commands

```bash
forge-agent init
forge-agent ask "organize my invoices by month" --json
forge-agent do "draft a project status note"
forge-agent organize ./invoices
forge-agent organize ./invoices --approve
forge-agent organize-rollback
forge-agent history list
forge-agent schedule list
forge-agent make ppt "project update"
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
- Brain Adapter: local deterministic planning through `forge-agent ask`.
- Release honesty: this source release does not claim signed installers, production telemetry, live-news retrieval, provider-backed autonomous execution, or broad field reliability.

## What is included

- Local runtime and CLI under `src/forge_agent`.
- Local Brain Adapter with deterministic planning.
- Local skill store with automatic skill creation, lifecycle, and reuse.
- Approval ledger for risky actions.
- Deterministic file organizer demo.
- Real dry-run-first organize command.
- Rollback support for approved organize operations.
- Operation history and schedule registry.
- Local content skill packs for PPT outline, report, news brief, and storyboard artifacts.
- Product, MVP, commercialization, architecture, validation, and competitive-analysis docs.
- GitHub Actions smoke CI and tests for the public runtime/demo/organizer/lifecycle/product/brain path.

## Validation

```bash
python -m compileall src tests
python -m pytest -q tests/test_public_runtime.py tests/test_organizer.py tests/test_skills_lifecycle.py tests/test_product_packs.py tests/test_brain_adapter.py
forge-agent demo --kind file-organizer --json
forge-agent organize ./invoices --json
forge-agent ask "organize my receipts" --json
```

GitHub Actions validates Python 3.11 and 3.12, compile checks, public runtime/demo tests, organizer tests, skill lifecycle tests, product pack tests, Brain Adapter tests, the file-organizer demo, real organizer dry-run, rollback behavior, schedule registry, content artifacts, `forge-agent ask`, and demo evidence files.

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
