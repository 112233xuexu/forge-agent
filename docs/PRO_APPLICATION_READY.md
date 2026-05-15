# OpenAI OSS / Pro application readiness

## Current readiness estimate

This repository is now a stronger early-stage open-source application candidate with a working ordinary-user automation MVP, tagged v1.9/v2.0/v2.2 releases, v2.1 file-safety hardening, v2.2 CLI reliability hardening, and v2.3 JSON consistency work.

Estimated readiness: **88%**.

The next lift toward 90% is external signal: stars, issues from real users, screenshots/GIFs, a tagged v2.3 release, and feedback from people trying the CLI on real folders.

## Why the project is eligible to discuss

Forge Agent is public, MIT-licensed, and maintained by the repository owner. It targets a real usability gap in open-source agent systems: ordinary users should not need to manually install skills, configure providers, or understand agent framework mechanics.

## Repository value proposition

Forge Agent is a zero-configuration skill autopilot for ordinary users. A user gives one command. The runtime finds or creates the required skill, asks approval before risky actions, records evidence, supports rollback for approved file operations, and reuses the skill next time.

v1.9 added a local Brain Adapter planning layer so ordinary-language requests can become structured plans while Forge Agent remains responsible for preview, approval, evidence, history, rollback, and skill lifecycle behavior.

v2.0 hardened that MVP with friendlier CLI errors, workspace-aware ask usage, ask validation, help output, JSON error output, and broader deterministic Brain Adapter tests.

v2.1 hardened file safety by skipping existing destinations instead of overwriting, exposing skipped files in JSON/manifests, and preserving organize evidence during rollback.

v2.2 hardened CLI reliability by returning structured JSON errors for supported file-related failures when users request JSON output.

v2.3 expands JSON consistency across more command groups, including history, schedule, skills, and approvals missing-resource failures.

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
- v2.0 product hardening for CLI consistency, input validation, and stronger tests;
- v2.1 file safety for overwrite prevention and skipped-file evidence;
- v2.2 CLI reliability for structured JSON error output;
- v2.3 broader JSON consistency for history, schedule, skills, and approvals failure behavior.

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

Forge Agent is an MIT-licensed local-first automation agent for ordinary users. It has public releases, active PR history, CI on Python 3.11/3.12, Brain Adapter planning, approval-gated organize/rollback, manifests, v2.1 file safety, v2.2 CLI reliability, and v2.3 JSON consistency. It targets a key gap: making agent automation usable without expert setup.

## Suggested API credits text

I would use API credits for planning tests, skill generation, PR review, issue triage, release-note drafting, and security-review workflows for Forge Agent. The goal is to improve the open-source runtime, strengthen ordinary-user automation, expand automated tests, and harden approval-gated file operations before broader release.

## Honest limitations

- The project is early-stage and does not yet have strong public adoption metrics.
- The current Brain Adapter is deterministic and local; provider-backed planning is not yet included.
- Some product surfaces are templates first: news does not fetch live sources, PPT/report output is Markdown first, and storyboard does not render video.
- The schedule registry stores schedule records but does not yet run a background daemon.
- The larger RC10 runtime is still being normalized into the public repo.
- The project should not claim production readiness yet.

## Recommended follow-up after submitting

- Create a GitHub release: `v2.3.0-json-consistency` after the v2.3 docs PR lands.
- Add a screenshot or short GIF of the demo and `forge-agent ask` output.
- Ask a few people to star or try the repository.
- Keep the application wording honest and focused on usability innovation, not exaggerated adoption.
