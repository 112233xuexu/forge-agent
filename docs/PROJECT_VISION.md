# Project Vision

Forge Agent is not intended to be another expert-only agent framework. The core vision is an ordinary-user automation agent that removes setup burden.

## Original user problem

Many strong open-source agents are powerful, but ordinary people still face too much friction:

- they must understand installation and configuration;
- they must choose or install skills manually;
- they must provide API keys and provider settings;
- they must understand channels, sandboxes, permissions, and tool routing;
- they must learn the framework before getting value.

Forge Agent should reverse that experience: the user gives a command, and the agent figures out the rest.

## Product sentence

The user only says what they want. Forge Agent finds, creates, validates, remembers, and reuses the skill needed to do it.

## North-star workflow

1. User gives a natural-language command.
2. Forge Agent understands the goal and required capability.
3. It searches local skills first.
4. If no skill exists, it creates a draft skill from planning and tool use.
5. It runs the skill safely with approval gates.
6. It records evidence and outcome.
7. If the result succeeds, it promotes the skill for reuse.
8. In the future, it can publish or sync the skill to a cloud skill library.

## Key differentiator

OpenClaw-style and Hermes-style systems emphasize many channels, many tools, memory, skill hubs, and self-improvement. Forge Agent should compete by making those ideas usable for non-technical users through zero-configuration onboarding and automatic skill lifecycle management.

## Strategic direction

### Phase 1: Local skill lifecycle

- Local skill search.
- Skill draft creation when missing.
- Skill validation before promotion.
- Skill reuse across tasks.
- Human-readable skill files.

### Phase 2: Ordinary-user UX

- One command or desktop input.
- No manual skill installation for first-run value.
- Simple status, approvals, history, and rollback.
- Clear explanations in normal language.

### Phase 3: Shared/cloud skill library

- Optional cloud skill registry.
- Community-created skill submission.
- Ratings, verification, categories, and safety metadata.
- Local cache for offline usage.

### Phase 4: Commercial-grade trust

- Sandboxed execution.
- Permission model.
- Audit log.
- Signed/verified skills.
- Enterprise/team policy controls.

## Current honest status

The original RC10 source package already contains important primitives: memory modules, governance modules, planner, tool registry, gateway, scheduler, and skill growth code. The public repository is being rebuilt into a usable, documented, installable product surface. The project has not yet fully achieved the north-star workflow; the next development focus is to make the skill lifecycle real and visible.
