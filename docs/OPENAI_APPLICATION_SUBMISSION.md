# OpenAI Codex for Open Source submission draft

## GitHub username

`112233xuexu`

## Repository

`https://github.com/112233xuexu/forge-agent`

## Maintainer role

Primary maintainer / repository owner.

## Qualification text, 500 characters max

I am the primary maintainer of Forge Agent, an MIT-licensed local-first agent runtime focused on the usability gap in open-source agents. Forge Agent lets ordinary users issue plain-language goals while the runtime automatically creates/reuses skills, asks approval before risky actions, and records evidence in a local ledger. Codex would help review PRs, expand tests, harden approval/security paths, and normalize the larger RC10 runtime.

## API credits use, 500 characters max

I would use API credits to test agent planning, skill generation, PR review, issue triage, release-note drafting, and security-review workflows for Forge Agent. The goal is to improve the open-source runtime, strengthen the ordinary-user demo, expand automated tests, and harden approval-gated execution before broader release.

## Reviewer notes

Forge Agent's public proof is the file-organizer demo:

```bash
forge-agent demo --kind file-organizer
```

It demonstrates a plain-language command, automatic skill creation, approval before risky file operations, safe sandbox execution, evidence output, and skill reuse.

The repository intentionally avoids claiming production readiness. It is an early open-source demo candidate with a clear roadmap, CI workflow, approval ledger, skill reuse proof, and honest limitations.
