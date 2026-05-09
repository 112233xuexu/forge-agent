# Forge Agent Product Strategy

## Product thesis

Forge Agent should become a local-first automation agent for non-technical users and small teams. The product promise is simple: users describe a goal once, Forge Agent plans the work, records evidence, asks for missing access or approval, and keeps a durable audit trail.

## Target users

1. Solo founders and creators who need repeatable admin, research, and publishing workflows.
2. Small businesses that need lightweight operations automation without hiring an engineering team.
3. Open-source maintainers who need issue triage, release checks, changelog drafting, and security review support.
4. Power users who want a local desktop agent with clear governance instead of opaque cloud-only automation.

## Core problem

Most AI tools answer one prompt at a time. Real work needs memory, handoffs, retry behavior, approvals, scheduled follow-up, release evidence, and a trustworthy log. Forge Agent should be positioned around workflow reliability rather than only chat quality.

## MVP promise

The first commercial-grade MVP should do five things well:

1. Accept a plain-language goal from CLI or desktop.
2. Convert the goal into a small plan with visible steps.
3. Execute safe local tools and ask for approval before risky actions.
4. Save task state, evidence, and audit history.
5. Resume interrupted work without losing context.

## Differentiation

- Local-first runtime and audit log.
- Explicit governance and release gates.
- Desktop shell for ordinary users.
- Open-source core with a future hosted/pro layer.
- Evidence-backed claims: every release claim should point to tests, reports, or reproducible commands.

## Commercial direction

### Open-source core

- CLI runtime.
- Local task ledger.
- Memory and governance primitives.
- Desktop source shell.
- Test and release evidence tooling.

### Paid/pro layer later

- Hosted sync and encrypted backups.
- Team workspaces.
- Managed connectors.
- Cloud execution workers.
- Advanced audit exports.
- Commercial support and deployment templates.

## Initial pricing hypothesis

- Free: local CLI and open-source desktop source.
- Pro: desktop app, managed connectors, cloud sync, priority model routing.
- Team: admin controls, audit exports, shared workspaces, SSO-ready deployment guidance.

## Success metrics

- Repository stars and watchers.
- Number of successful installs.
- CLI task completions per active user.
- Issues opened by real users.
- External PRs or discussions.
- Release checks passing on every commit.
- First public demo video and screenshots.

## OpenAI Codex for OSS fit

The project needs Codex-style help for real maintainer workflows: PR review, issue triage, test expansion, release-gate maintenance, security hardening, and documentation. The official Codex for Open Source form asks for public GitHub visibility, maintainer role, and a short justification of repository importance. Forge Agent should strengthen those signals by keeping the repository active, documented, tested, and transparent.
