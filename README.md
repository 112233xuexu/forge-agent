# Forge Agent

Forge Agent is an experimental local-first automation agent for ordinary users, solo operators, and open-source maintainers. Users submit goals through a single `forge-agent do` entrypoint, while the runtime direction is to coordinate session state, memory, tool routing, scheduling, approvals, recovery, governance, audit trails, and release evidence.

The project is being developed toward a usable open-source core and a future commercial desktop/pro product. The near-term focus is not hype: it is a reliable local CLI, transparent task history, approval-gated actions, public demos, and evidence-backed release claims.

## Product promise

Describe a goal once. Forge Agent should plan the work, ask before risky actions, record evidence, and let the user resume later.

## Current status

- Package version: `1.0.0rc10`.
- CLI entrypoint: `forge-agent`.
- License: MIT.
- Repository visibility: public.
- Release honesty: this source release does not claim signed installers, production telemetry, or broad field reliability.
- Commercial direction: open-source local core first, desktop/pro layer later.

## What is included

- Python runtime and CLI package under `src/forge_agent`.
- Product, MVP, commercialization, and architecture documentation.
- GitHub Actions smoke CI.
- Security policy and contribution guide.
- Roadmap issues for MVP, demo, and security hardening.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
forge-agent --help
forge-agent do "draft a project status note"
```

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
forge-agent --help
forge-agent do "draft a project status note"
```

## Validation

```bash
python -m compileall src tests
python -m pytest -q
```

## Roadmap

- [MVP Roadmap](docs/MVP_ROADMAP.md)
- [Product Strategy](docs/PRODUCT_STRATEGY.md)
- [Commercialization Plan](docs/COMMERCIALIZATION_PLAN.md)
- [Architecture](docs/ARCHITECTURE.md)
- [OpenAI OSS Application Notes](docs/OPENAI_OSS_APPLICATION.md)

## OpenAI Codex for OSS fit

Forge Agent is being structured as a real maintainer workflow project: public repository, visible roadmap, CI, security policy, issue triage, release evidence, and a clear reason for Codex assistance. Codex would be used for PR review, issue triage, test expansion, security hardening, and release workflow maintenance.

## Repository owner

Maintained by `jiangmingyue` / `112233xuexu`.
