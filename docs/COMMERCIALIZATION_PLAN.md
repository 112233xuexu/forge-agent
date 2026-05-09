# Commercialization Plan

## Positioning

Forge Agent should be positioned as a trustworthy local-first AI operations assistant for people who need work completed, not just answered. The commercial angle is reliability: task state, approvals, evidence, auditability, and resumability.

## Beachhead market

Start with open-source maintainers and solo operators because they already understand GitHub, release checks, issues, and automation pain.

Recommended beachhead workflows:

1. Issue triage and response drafting.
2. Release checklist automation.
3. Changelog and release-note drafting.
4. Local workspace status summaries.
5. Approval-gated file and repository maintenance.

## Product packaging

### Open-source edition

- Local CLI runtime.
- Local workspace and task ledger.
- Basic desktop shell source.
- Release-gate scripts and documentation.

### Pro edition candidate

- Packaged desktop app.
- Managed model/provider configuration.
- Managed connector templates.
- Encrypted sync and backup.
- Rich audit exports.
- Priority support and setup templates.

### Team edition candidate

- Shared workspaces.
- Admin policy controls.
- Role-based approvals.
- Organization audit reports.
- Deployment playbooks.

## Business milestones

### Milestone 1: Credible open-source project

- Public repo.
- Clear README.
- License and security policy.
- CI passing.
- Roadmap issues.
- OpenAI OSS application submitted.

### Milestone 2: First useful workflow

- `forge-agent init`.
- `forge-agent do` with persisted task history.
- `forge-agent tasks`.
- One workflow example that a maintainer can run.

### Milestone 3: Desktop demo

- Screenshot-ready UI.
- Local runtime bridge.
- Demo video or GIF.
- Honest release notes.

### Milestone 4: First users

- Ask 5 maintainers or operators to try one workflow.
- Convert feedback into issues.
- Track install friction and task success.

## Risks

- Overclaiming readiness before the product is actually usable.
- Trying to build every connector too early.
- Desktop packaging complexity.
- Security risk from agent tool execution.
- Lack of public usage signals for OSS grant/application review.

## Risk controls

- Keep local-first, approval-gated defaults.
- Write down unsupported claims in release notes.
- Add tests before broadening tool execution.
- Treat security and auditability as product features.
- Build one complete workflow before adding many half-finished features.
