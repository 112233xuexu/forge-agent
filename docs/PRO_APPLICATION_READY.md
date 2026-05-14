# OpenAI OSS / Pro application readiness

## Current readiness estimate

This repository is now a credible early-stage open-source application candidate with a working ordinary-user automation MVP plus a v2.0 product-hardening line.

Estimated readiness: **82%**.

The next lift toward 90% is external signal: stars, issues from real users, screenshots/GIFs, a tagged v2.0 release, and feedback from people trying the CLI on real folders.

## Why the project is eligible to discuss

Forge Agent is public, MIT-licensed, and maintained by the repository owner. It targets a real usability gap in open-source agent systems: ordinary users should not need to manually install skills, configure providers, or understand agent framework mechanics.

## Repository value proposition

Forge Agent is a zero-configuration skill autopilot for ordinary users. A user gives one command. The runtime finds or creates the required skill, asks approval before risky actions, records evidence, supports rollback for approved file operations, and reuses the skill next time.

v1.9 added a local Brain Adapter planning layer so ordinary-language requests can become structured plans while Forge Agent remains responsible for preview, approval, evidence, history, rollback, and skill lifecycle behavior.

v2.0 hardens that MVP with friendlier CLI errors, workspace-aware ask usage, ask validation, help output, JSON error output, and broader deterministic Brain Adapter tests.

```text
Brain suggests. Forge Agent governs.
```

## Demo proof

The public demo is:

```bash
forge-agent demo --kind file-organizer
```

It shows:

- ordinary-language user goal;
- automatic skill creation;
- approval before file movement;
- file organization inside a safe sandbox;
- `manifest.json` evidence;
- second-batch skill reuse with `reuse_proven: true`.

## MVP and hardening proof

The main branch now includes:

- v1.1 real dry-run-first organize command;
- v1.2 skill lifecycle controls;
- v1.3 rollback for approved organize operations;
- v1.4 operation history;
- v1.5 schedule registry;
- v1.6 PPT/report local artifact generation;
- v1.7 news brief template generation;
- v1.8 video storyboard generation;
- v1.9 Brain Adapter planning with `forge-agent ask`;
- v2.0 product hardening for CLI consistency, input validation, and stronger tests.

Useful validation commands:

```bash
forge-agent ask "organize my invoices by month" --json
forge-agent --workspace .forge-agent ask "make a project status deck" --json
forge-agent ask --help
forge-agent organize ./invoices
forge-agent organize ./invoices --approve
forge-agent organize-rollback
forge-agent make ppt "project status update"
```

## Suggested 500-character qualification text

I am the primary maintainer of Forge Agent, an MIT-licensed local-first automation agent for ordinary users. It turns plain-language requests into local plans and reusable skills, previews risky work, asks approval before file moves, records evidence, and supports rollback. v2.0 hardens CLI consistency, user-facing errors, ask validation, and deterministic planning tests. Codex would help review PRs, expand tests, and normalize the larger RC10 runtime.

## Suggested API credits text

I would use API credits to test planning, skill generation, PR review, issue triage, release-note drafting, and security-review workflows for Forge Agent. The goal is to improve the open-source runtime, strengthen ordinary-user automation, expand automated tests, and harden approval-gated operations before broader release.

## Honest limitations

- The project is early-stage and does not yet have strong public adoption metrics.
- The current Brain Adapter is deterministic and local; provider-backed planning is not yet included.
- Some product surfaces are templates first: news does not fetch live sources, PPT/report output is Markdown first, and storyboard does not render video.
- The schedule registry stores schedule records but does not yet run a background daemon.
- The larger RC10 runtime is still being normalized into the public repo.
- The project should not claim production readiness yet.

## Recommended before submitting

- Create a GitHub release: `v2.0.0-product-hardening` after the v2.0 evidence PR lands.
- Add a screenshot or short GIF of the demo and `forge-agent ask` output.
- Ask a few people to star or try the repository.
- Keep the application wording honest and focused on usability innovation, not exaggerated adoption.
