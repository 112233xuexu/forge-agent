# Forge Agent

Forge Agent is an AI butler for ordinary users: people describe what they want in plain language, and Forge uses connected apps, long-term memory, clear confirmation, work records, and recovery paths to get the work done without forcing users to learn every tool.

In one sentence:

```text
普通人不用学软件，也能一句话把事情办完。
```

Forge is not meant to expose APIs, tools, scopes, prompts, or automation internals to the user. The product goal is a simple front end where the user says what they need:

```text
Use my email to send a follow-up to John.
Create a GitHub repository for this project. I do not know how GitHub works.
Organize this folder of invoices by month.
Turn these notes into a clean report.
Check whether I have important emails today.
Remember how I like project reports formatted.
```

Behind that simple request, Forge can use memory, skills, approvals, file operations, connected apps, and task history. But the user-facing flow should stay human:

```text
You ask.
Forge explains what it will do.
You confirm important actions.
Forge does the work.
Forge records what happened.
If possible, Forge can restore or correct the result.
```

## Core product promise

Forge is designed to reduce ordinary users' learning cost and time cost.

The user should not need to know:

- how GitHub works,
- how email APIs work,
- how Notion, Calendar, Drive, or Slack integrations work,
- how to batch organize files,
- how to configure agent tools,
- how to write prompts repeatedly,
- or how to recover from mistakes manually.

Forge should learn stable preferences and project context through a visible Memory Palace, then use that context to help users finish repeat work faster.

The public-facing product pillars are:

```text
simple use + long-term memory + connected apps + clear confirmation + work records + recovery
```

## Why it is different

Many agent projects expose skills, tools, providers, sandboxes, gateways, permissions, registries, and APIs directly to the user. Forge Agent's direction is to hide that complexity by default.

The user-facing flow should be:

```text
plain request -> understandable plan -> confirm if important -> execute -> show result -> remember useful preferences -> allow correction/recovery
```

The internal engineering flow can still be strict:

```text
intent -> memory recall -> skill/tool selection -> preview -> approval when needed -> execution evidence -> history -> recovery where supported -> skill reuse
```

The product rule is:

```text
Users speak in outcomes. Forge handles the software.
```

## User-facing language

Forge should avoid exposing engineering terms when ordinary language is clearer.

| Internal term | User-facing language |
|---|---|
| permission | What I can see or change |
| approval | You confirm before I do it |
| rollback | Restore / undo |
| audit log | What I did |
| memory | What I remember about you |
| tool | An app I can use for you |
| risk | What this may affect |
| skill | How I should do this next time |

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

The current demo creates a safe sandbox and proves automatic skill creation, approval, file organization, evidence, and skill reuse. No real user files are touched by the demo.

The demo is still CLI-first today. The product direction is a simpler front end where the same workflow appears as:

```text
I found 5 invoice files.
I can organize them by month.
This will move files but not change file contents.
Do you want me to continue?
```

## Product commands

Brain Adapter planning:

```bash
forge-agent ask "organize my invoices by month" --json
forge-agent --workspace .forge-agent ask "make a project status deck" --json
forge-agent ask --help
```

Real dry-run-first file organization:

```bash
forge-agent organize ./invoices
forge-agent organize ./invoices --approve
forge-agent organize-rollback
```

v2.1 file safety means approved organization skips existing destinations instead of overwriting them. Skipped files are exposed in JSON and manifests.

v2.2 CLI reliability means JSON mode returns structured JSON for supported file-related errors, not plain text.

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
- v2.0: product hardening for CLI consistency, input validation, error surfaces, and stronger tests.
- v2.1: file safety hardening for destination collisions and skipped-file evidence.
- v2.2: CLI reliability hardening for structured JSON errors.
- v2.5-v2.6: visible Memory Palace, bounded recall, sensitive memory opt-in, ask-time memory controls, and scoped memory retrieval.
- stabilization: ask extraction and memory extraction work to keep architecture maintainable before larger product features.

The current features are local deterministic product surfaces first. They do not yet claim full live news retrieval, real background daemon execution, `.pptx` rendering, voiceover generation, video rendering, broad app integrations, or provider-backed autonomous execution.

See also:

- [Product positioning](docs/PRODUCT_POSITIONING.md)
- [Competitive benchmark and roadmap](docs/COMPETITIVE_BENCHMARK.md)
- [Stabilization audit](docs/STABILIZATION_AUDIT.md)
- [Ordinary-user demo guide](docs/ORDINARY_USER_DEMO.md)
- [v1.1 organize command](docs/V1_1_ORGANIZE_COMMAND.md)
- [v1.2 skill lifecycle](docs/V1_2_SKILL_LIFECYCLE.md)
- [v1.3 rollback](docs/V1_3_ROLLBACK.md)
- [v1.4-v1.8 product expansion](docs/V1_4_TO_V1_8_PRODUCT_EXPANSION.md)
- [v1.9 Brain Adapter](docs/V1_9_BRAIN_ADAPTER.md)
- [v1.9 release notes](docs/RELEASE_NOTES_V1_9.md)
- [v2.0 hardening notes](docs/RELEASE_NOTES_V2_0.md)
- [v2.1 file safety notes](docs/RELEASE_NOTES_V2_1.md)
- [v2.2 CLI reliability notes](docs/RELEASE_NOTES_V2_2.md)
- [Demo output sample](docs/DEMO_OUTPUT_SAMPLE.json)
- [Release candidate notes](docs/RELEASE_CANDIDATE.md)
- [OpenAI OSS / Pro readiness notes](docs/PRO_APPLICATION_READY.md)

## Everyday commands

```bash
forge-agent init
forge-agent ask "organize my invoices by month" --json
forge-agent --workspace .forge-agent ask "make a project status deck" --json
forge-agent ask --help
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
- Product direction: ordinary-user AI butler that lowers learning cost and time cost.
- Demo: ordinary-user file organizer with approval ledger and skill reuse proof.
- Brain Adapter: local deterministic planning through `forge-agent ask`.
- Memory Palace: visible local memory with recall, audit, sensitive-memory controls, and ask-time filters.
- File safety: organize destination collisions are skipped rather than overwritten, and skipped files are visible in JSON/manifests.
- CLI reliability: supported file-related JSON mode failures return structured JSON errors.
- Release honesty: this source release does not claim signed installers, production telemetry, live-news retrieval, provider-backed autonomous execution, broad app integrations, or broad field reliability.

## What is included

- Local runtime and CLI under `src/forge_agent`.
- Local Brain Adapter with deterministic planning.
- Local Memory Palace with visible storage and controlled recall.
- Local skill store with automatic skill creation, lifecycle, and reuse.
- Approval ledger for risky actions.
- Deterministic file organizer demo.
- Real dry-run-first organize command.
- Rollback support for approved organize operations.
- Operation history and schedule registry.
- Local content skill packs for PPT outline, report, news brief, and storyboard artifacts.
- Product, MVP, commercialization, architecture, validation, and competitive-analysis docs.
- GitHub Actions smoke CI and tests for the public runtime/demo/organizer/lifecycle/product/brain/entrypoint path.

## Validation

```bash
python -m compileall src tests
python -m pytest -q tests/test_public_runtime.py tests/test_organizer.py tests/test_organizer_skipped_json.py tests/test_rollback_evidence.py tests/test_cli_json_errors.py tests/test_skills_lifecycle.py tests/test_product_packs.py tests/test_brain_adapter.py tests/test_entrypoint_errors.py tests/test_entrypoint_workspace.py tests/test_entrypoint_ask_validation.py
forge-agent demo --kind file-organizer --json
forge-agent organize ./invoices --json
forge-agent ask "organize my receipts" --json
forge-agent --workspace .forge-agent ask "organize my receipts" --json
forge-agent ask --help
```

GitHub Actions validates Python 3.11 and 3.12, compile checks, public runtime/demo tests, organizer tests, skipped-file JSON/manifest tests, rollback evidence tests, CLI JSON error tests, skill lifecycle tests, product pack tests, Brain Adapter tests, entrypoint hardening tests, the file-organizer demo, real organizer dry-run, rollback behavior, schedule registry, content artifacts, `forge-agent ask`, workspace-aware ask usage, ask validation, and demo evidence files.

The original RC10 source package contains a larger runtime and test suite. The public repository is being normalized around the ordinary-user product surface first.

## Roadmap

- [Product positioning](docs/PRODUCT_POSITIONING.md)
- [Competitive benchmark and roadmap](docs/COMPETITIVE_BENCHMARK.md)
- [Stabilization audit](docs/STABILIZATION_AUDIT.md)
- [Project Vision](docs/PROJECT_VISION.md)
- [Competitive Analysis](docs/COMPETITIVE_ANALYSIS.md)
- [MVP Roadmap](docs/MVP_ROADMAP.md)
- [Product Strategy](docs/PRODUCT_STRATEGY.md)
- [Commercialization Plan](docs/COMMERCIALIZATION_PLAN.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Validation](docs/VALIDATION.md)
- [OpenAI OSS Application Notes](docs/OPENAI_OSS_APPLICATION.md)

## OpenAI Codex for OSS fit

Forge Agent targets a real usability gap in open-source agent systems: existing systems can be powerful, but ordinary users still face too much setup, tool knowledge, app knowledge, and recovery risk. Codex would help review pull requests, triage issues, expand tests, harden confirmation/recovery paths, normalize the larger RC10 source tree, and maintain evidence-backed releases.

## Repository owner

Maintained by `jiangmingyue` / `112233xuexu`.
