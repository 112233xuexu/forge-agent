# Forge Agent Competitive Benchmark and Roadmap

This document defines Forge Agent's product direction and competitive benchmark.

Forge Agent is not only a memory system, not only a CLI tool, and not only a safety framework.

Forge Agent should become an **AI butler for ordinary users**:

```text
Users describe what they want in plain language.
Forge remembers useful context, understands the request, chooses the right connected app or local tool, explains important actions, asks before risky actions, records what happened, and helps recover when possible.
```

In Chinese:

```text
普通人不用学软件，也能一句话把事情办完。
```

The core product value is:

```text
reduce learning cost + reduce time cost + long-term memory + simple confirmation + work records + recovery
```

## Named competitors and benchmark targets

Forge should benchmark against three named directions.

| Benchmark | What it proves | Forge must learn from it | Forge should exceed it on |
|---|---|---|---|
| OpenHuman | Ordinary users want one AI entry point that can connect many apps. | Simple front end, multi-app ambition, personal assistant framing. | Clear confirmation, visible memory, understandable action plans, work records, recovery, less scary app authority. |
| OpenClaw | Self-hosted agents can execute real tools and workflows. | Tool execution, automation, local/server operation, extensibility. | Lower setup burden, safer defaults, ordinary-user language, recoverable workflows. |
| Hermes Agent | Persistent memory and self-improving skills matter. | Long-term memory, experience accumulation, skill creation/refinement. | Visible Memory Palace, editable/forgettable memory, governed skill lifecycle, user-readable explanations. |

Forge should not blindly race to connect the most apps first. Integration count is useful only after the product can explain actions clearly, ask for confirmation, keep records, and recover from mistakes.

## North Star

Forge succeeds when it turns this:

```text
The user spends 30 minutes learning an app or workflow.
```

into this:

```text
The user says one sentence, reviews one clear confirmation card, and gets the task done.
```

Example user requests:

```text
Use my email to send a follow-up to John.
Create a GitHub repository for this project. I do not know how GitHub works.
Organize this folder of invoices by month.
Turn these notes into a clean report.
Check whether I have important emails today.
Remember how I like project reports formatted.
```

The user should not need to understand APIs, OAuth scopes, tool registries, rollback manifests, audit logs, Git internals, or agent frameworks.

## Product pillars

| Pillar | User-facing promise | Internal capability |
|---|---|---|
| Simple use | Tell Forge what outcome you want. | Intent understanding and task planning. |
| Long-term memory | Forge remembers stable preferences and project context. | Memory Palace, scoped recall, sensitive-memory controls. |
| Connected apps | Forge can use apps for you. | Tool/app connectors, permissions, execution contracts. |
| Clear confirmation | Forge explains important actions before doing them. | Preview, approval, side-effect summaries. |
| Work records | Forge can show what it did. | Operation history, memory used, tool results. |
| Recovery | Forge helps undo or correct when possible. | Rollback/recovery recipes and skipped-file evidence. |
| Skill reuse | Forge learns repeated workflows. | Skill lifecycle, validation, promotion, quarantine. |

## User-facing language rule

Technical terms can exist internally, but user-facing product language must be plain.

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

## Current maturity snapshot

| Area | Current maturity | Notes |
|---|---:|---|
| Ordinary-user product clarity | 45% | New positioning is clearer, but UI and demos are still CLI-first. |
| Memory Palace | 70% | Strong foundation: add/list/show/search/forget/quarantine/restore/export/recall, sensitive opt-in, scoped recall. |
| Ask / planning | 45% | Basic intent planning exists; memory-aware metadata exists; execution pipeline is still shallow. |
| Tool execution | 35% | File organizer and content packs exist; app connectors and tool contracts are incomplete. |
| Confirmation and recovery | 50% | Approval ledger, dry-run, rollback, quarantine patterns exist; ordinary-user confirmation cards are not implemented yet. |
| Skill system | 45% | Skill lifecycle exists; reuse, stats, ranking, and promotion policy need deeper integration. |
| Front end | 10% | CLI exists; simple ordinary-user UI is not built yet. |
| Open-source credibility | 45% | CI and PR history are good; README and docs are improving; architecture cleanup still in progress. |
| Mature-product superiority | 25% | Direction is clearer, but app breadth, UI, and ordinary-user flows are behind OpenHuman-like products. |

## Competitive benchmark matrix

| Capability area | Benchmark expectation | Forge current state | Gap | Priority | Differentiation target |
|---|---|---|---|---|---|
| Ordinary-user input | User describes an outcome, not a tool procedure. | `ask` accepts plain text and maps simple intents. | Needs richer intent routing and front-end flow. | P0 | One input box for many apps and workflows. |
| App abstraction | User does not need to know the app's UI. | Local tools exist; broad app connectors do not. | Gmail/GitHub/Calendar/Drive/Notion-style connectors are missing. | P0 | Forge handles apps behind the scenes. |
| Action explanation | User understands what will happen before important changes. | Dry-run organizer and approval patterns exist. | Need universal confirmation cards and human wording. | P0 | “Here is what I will do; confirm before I do it.” |
| Long-term memory | Assistant remembers user/project/workflow context. | Memory Palace exists with recall and filters. | Needs editing, import, dedupe, stats, compaction, UI. | P0 | Visible, editable, forgettable, exportable memory. |
| Safety that users understand | Safety is not jargon; users know what may change. | Technical safety metadata exists. | Need user-facing “what this may affect” summaries. | P0 | Safe because the user understands and confirms. |
| Recovery | Mistakes can be corrected where possible. | File organizer rollback exists. | Need generalized recovery and simpler “restore” language. | P0 | “Restore to before I changed it.” |
| Work records | User can see what was done. | Operation history and memory audit exist. | Need unified ordinary-user history view. | P0 | Clear task record: request, plan, confirmation, result. |
| Skill reuse | Repeated work gets easier. | Skill lifecycle exists. | Need skill recommendation and user-facing “do it like last time.” | P1 | Lower time cost every time the user repeats work. |
| Multi-app workflows | Work spans email, GitHub, files, calendar, docs. | Mostly local file/content workflows. | Need connector architecture and staged integrations. | P1 | Start with a few high-quality connectors, not 100 weak ones. |
| Front end | Non-technical users can operate it. | CLI-first. | Need simple web/TUI/desktop-style task surface. | P0 | Input box + confirmation card + result + history + restore. |
| Code maintainability | Product can grow without becoming a mess. | Stabilization work has started. | Need full codebase cleanup before more features. | P0 | Clean modules before broad connectors. |

## Mature-product superiority acceptance bar

Forge cannot claim product-level superiority until these bars are met.

| Bar | Required evidence |
|---|---|
| Learning-cost reduction | A user can complete common tasks without learning the underlying app UI. |
| Time-cost reduction | A repeated workflow becomes faster through memory and skills. |
| OpenHuman benchmark | Forge has a simple ordinary-user surface and at least a few high-quality app-backed workflows. |
| OpenClaw benchmark | Forge can execute real tools/workflows with understandable plans and confirmation. |
| Hermes benchmark | Forge has visible persistent memory and governed skill improvement. |
| Memory advantage | User can inspect, edit, forget, quarantine, restore, export, recall, and filter memory. |
| Confirmation advantage | Important actions are explained in ordinary language before execution. |
| Recovery advantage | At least file workflows and one additional workflow family support recovery or clear irreversible warnings. |
| Work-record advantage | The user can review what Forge did, what it used, and what changed. |
| Codebase readiness | Core modules are clean enough to add connectors/UI without creating a monolith. |

## What Forge already has

- CLI task surface with `ask`.
- Local deterministic planning.
- Visible Memory Palace.
- Bounded and explainable recall.
- Sensitive memory excluded by default.
- Ask-time memory can be disabled, limited, or filtered.
- File actions can be previewed and rolled back.
- Approval ledger and operation history patterns.
- Skill lifecycle states.
- Content packs and file organizer demo.
- CI coverage for core paths.

## What Forge must add next

### P0: Positioning and cleanup

1. Finish product positioning updates.
2. Finish current memory extraction PR.
3. Add full codebase cleanup plan.
4. Avoid new feature work until the codebase is clean enough.

### P0: Ordinary-user flow

1. Define a standard task card:
   - what you asked,
   - what I will do,
   - what this may affect,
   - what I will not do,
   - confirm/cancel/edit,
   - result,
   - restore/correct if possible.
2. Make `ask` return this structure before deep app integrations.

### P0: First app-backed workflows

Do not chase 100 integrations first. Start with a few workflows that prove the product thesis:

1. Local files: organize, rename, classify, restore.
2. GitHub: create repo, write README, open issue/PR, explain GitHub in plain language.
3. Email/calendar: draft/send with confirmation, summarize important items, schedule with confirmation.

### P1: Front end

Build a simple surface:

```text
input box -> confirmation card -> progress -> result -> history -> restore/correct
```

### P1: Memory and skill hardening

Add memory edit/import/dedupe/stats and skill recommendation/reuse so repeated tasks take less time.

## Roadmap

### v2.7 Product flow schema

Goal: make every task understandable to ordinary users.

Deliverables:

- task card schema,
- user-facing wording,
- ask output aligned with the task card,
- tests for confirmation wording.

### v2.8 Codebase cleanup completion

Goal: make the project ready for connectors and UI.

Deliverables:

- memory extraction complete,
- CLI handler split,
- file-by-file codebase audit,
- no monolithic growth.

### v2.9 First connector-quality workflows

Goal: prove “I do not know this software; Forge helps me.”

Deliverables:

- GitHub workflow prototype,
- email/calendar safe workflow prototype or simulator,
- local file workflow improvements,
- ordinary-user confirmation cards.

### v3.0 Simple front end demo

Goal: make the value visible without reading source code.

Deliverables:

- one input box,
- confirmation cards,
- result view,
- history view,
- memory view,
- restore/correct action where supported.

## Decision rule for future development

A feature should be prioritized only if it improves at least one of these claims:

1. It reduces the user's learning cost.
2. It reduces the user's time cost.
3. It lets the user finish work without knowing the underlying app.
4. It makes memory useful without becoming hidden or scary.
5. It explains important actions in ordinary language.
6. It makes results reviewable or recoverable.
7. It keeps the codebase clean enough to scale to many apps.

If not, it should wait.
