# Forge Agent Competitive Benchmark and Roadmap

This document turns the product direction into an explicit benchmark matrix.

Forge Agent is not only a memory system. The target is a controllable agent workspace that combines memory, planning, tools, approvals, reusable skills, auditability, and ordinary-user product experience.

## Product thesis

Forge Agent should compete on four layers at the same time:

1. **Memory**: visible, controllable, auditable long-term context.
2. **Action**: safe tool execution with preview, approval, and rollback.
3. **Skill**: repeated work becomes reusable, testable, promotable skills.
4. **Product**: ordinary users can understand, inspect, and trust what the agent is doing.

The intended differentiation is not simply "more memory" or "more tools". The intended differentiation is:

```text
memory palace + explainable recall + approval-aware execution + reusable skills + local-first auditability
```

## Current maturity snapshot

| Area | Current maturity | Notes |
|---|---:|---|
| Memory Palace | 70% | Strong foundation: add/list/show/search/forget/quarantine/restore/export/recall, sensitive opt-in, scoped recall. |
| Ask / planning | 45% | Basic intent planning exists; memory-aware metadata exists; execution pipeline is still shallow. |
| Tool execution | 35% | File organizer and content packs exist; tool registry and consistent execution contracts are incomplete. |
| Approval and safety | 50% | Approval ledger, dry-run, rollback, quarantine patterns exist; unified risk policy is incomplete. |
| Skill system | 45% | Skill lifecycle exists; reuse, stats, ranking, and promotion policy need deeper integration. |
| User experience | 25% | CLI works, but product experience is still developer-oriented. |
| Open-source credibility | 40% | CI and PR history are good; README, architecture docs, demo assets, contributing docs, and release packaging need work. |

## Competitive benchmark matrix

| Capability area | Benchmark expectation | Forge current state | Gap | Priority | Differentiation target |
|---|---|---|---|---|---|
| Long-term memory | Persistent memory, preferences, project context, recall | Local Memory Palace with visible JSONL storage and recall | Needs update/import/dedupe/merge/stats/aging/compaction | P0 | Memory is visible, editable, forgettable, quarantinable, exportable, and auditable. |
| Memory retrieval | Relevant context is retrieved without flooding prompts | Deterministic recall with score, reasons, limit, scope, wing, sensitive gate | Needs better ranking, synonyms, conflict detection, optional semantic retrieval | P0 | Every recalled memory has score, reasons, safety, and policy metadata. |
| Sensitive memory | Sensitive context should not leak by default | Sensitive memory excluded by default; explicit opt-in exists | Needs stronger policy docs, category labels, and audit review | P0 | Sensitive memory requires visible explicit opt-in and is never silently injected. |
| Agent planning | Natural-language goal becomes structured plan | `ask` maps goals to simple plan and memory metadata | Needs richer plan schema: risk, command suggestion, required approval, expected artifacts | P0 | Plans are inspectable before action, not hidden chain-of-action. |
| Safe execution | Agent can act but not dangerously | File organize supports dry-run, approval, rollback | Needs unified execution pipeline and risk policy across all tools | P0 | Every risky action has preview, approval record, operation manifest, and rollback path. |
| Tool system | Agent can use many practical tools | File organizer, content artifact generators, scheduler records | Needs formal tool registry, tool contracts, input validation, result envelope | P1 | Tools are local-first, auditable, and reversible where possible. |
| File workflows | Ordinary file chores can be handled safely | Organizer by month with rollback evidence | Needs more workflows: rename, dedupe, classify, archive, extract, convert | P1 | Safer than generic automation because it previews and can roll back. |
| Content workflows | Reports, PPT outlines, news briefs, storyboards | Basic content packs exist | Needs richer templates, export formats, screenshots/assets, style controls | P2 | Local reusable content packs that can become skills. |
| Skill memory | Repeated tasks become reusable procedures | Skill lifecycle exists: test/validate/promote/deprecate/quarantine | Needs skill ranking, reuse analytics, skill suggestions, compatibility checks | P1 | Skills are not opaque prompts; they have lifecycle, evidence, and promotion state. |
| Approval system | Human stays in control | Approval ledger exists | Needs policy engine, risk classes, approval UX, batch decisions | P0 | Approval is a first-class product primitive, not an afterthought. |
| Auditability | User can see what happened and why | Audit logs, operation history, memory audit exist | Needs unified audit view and export | P0 | One place to inspect memory, plan, approval, action, result, and rollback. |
| Rollback | Risky changes can be undone | Organizer rollback exists | Needs generalized rollback contract per tool | P1 | Reversibility is a core selling point. |
| Local-first trust | User data is inspectable and portable | Workspace JSON/JSONL approach exists | Needs import/export across all major subsystems | P1 | No hidden database required for core behavior. |
| Ordinary-user UX | Non-developers can understand and operate it | CLI is usable but technical | Needs TUI/Web UI, task panel, memory panel, approval panel, demo mode | P1 | Product explains itself through previews, policies, and visible state. |
| Developer UX | Easy to extend | Python package and tests exist | Needs plugin/tool API docs, examples, typing contracts | P2 | Extensions must inherit safety, audit, and approval contracts. |
| Open-source proof | Maintainers can trust project quality | CI, tests, PR sequence are strong | Needs README, architecture diagram, roadmap, contributing, security policy, release tags | P0 | The repo should look maintained, testable, and serious. |

## What Forge already does better than a generic agent wrapper

- Memory is not hidden: it is visible in local files.
- Memory can be forgotten, quarantined, restored, exported, and audited.
- Recall is bounded and explainable.
- Sensitive memory is excluded by default.
- Ask-time memory can be disabled or limited.
- Ask-time memory can be filtered by scope and wing.
- File actions can be previewed and rolled back.
- Skills have lifecycle states instead of being ungoverned prompt snippets.

## What Forge must still add before claiming product-level superiority

### P0: Required next work

1. **Agent Execution Pipeline**
   - Add a unified plan schema with risk, approval requirement, suggested command, expected side effects, and rollback availability.
   - Keep default mode as preview-first.
   - Connect ask -> plan -> approval -> tool execution -> operation history.

2. **Unified Risk Policy**
   - Define low/medium/high risk.
   - Require approval for file movement, deletion, external writes, and irreversible operations.
   - Return risk metadata in every plan and tool result.

3. **Memory Management Hardening**
   - Add memory update/edit.
   - Add memory move between wing/room/closet/drawer.
   - Add memory import for exported bundles.
   - Add memory stats and dedupe.

4. **Repository Product Packaging**
   - Rewrite README around the product thesis.
   - Add architecture diagram.
   - Add quickstart.
   - Add demo script.
   - Add roadmap and examples.

### P1: Strong product work

1. **Tool Registry**
   - Define tool metadata: name, risk, inputs, outputs, reversible, approval requirement.
   - Let ask suggest registered tools.
   - Standardize JSON envelopes.

2. **Generalized Rollback Contract**
   - Move rollback from file organizer-specific logic toward a common operation pattern.
   - Record rollback availability in every operation manifest.

3. **Skill Reuse Engine**
   - Recommend skills during ask.
   - Track skill usage, success, failure, and promotion evidence.
   - Use memory recall and skill recall separately.

4. **User-Facing Demo**
   - Add `forge-agent demo` scenarios for memory, file organization, approval, rollback, and skills.
   - Produce deterministic demo evidence for reviewers.

### P2: Expansion work

1. **TUI or Web UI**
   - Memory browser.
   - Task/plan panel.
   - Approval queue.
   - Operation history.
   - Skill library.

2. **Semantic Retrieval Option**
   - Optional embedding-backed recall while preserving deterministic fallback.
   - Keep recall explanations and safety gates.

3. **More Practical Tools**
   - File rename/dedupe/classify/archive.
   - Markdown report generator.
   - PPTX export.
   - Web form helper.
   - GitHub issue/PR helper.

## Near-term roadmap

### v2.7 Agent Execution Pipeline

Goal: turn `ask` from a simple planner into a safe execution proposal.

Deliverables:

- `BrainPlan` includes `risk`, `requires_approval`, `suggested_command`, `side_effects`, `rollback_available`, and `next_actions`.
- `forge-agent ask ... --json` returns execution-aware metadata.
- Tests verify that risky actions are preview-first.
- No automatic execution by default.

### v2.8 Tool Registry

Goal: make tool capabilities explicit and inspectable.

Deliverables:

- `tools.py` registry.
- Tool metadata schema.
- `forge-agent tools list/show`.
- Ask can suggest registered tools.

### v2.9 Unified Risk and Approval Policy

Goal: make safety consistent across tools.

Deliverables:

- Risk policy module.
- Risk classes.
- Approval requirements.
- Tests for low/medium/high risk behavior.

### v3.0 Product Packaging

Goal: make the repository credible to users, reviewers, and open-source program evaluators.

Deliverables:

- README rewrite.
- Architecture diagram.
- Quickstart.
- Demo walkthrough.
- Contributing guide.
- Security policy.
- Release tag.

## Decision rule for future development

A feature should be prioritized only if it improves at least one of these product claims:

1. Forge remembers better because memory is visible and controllable.
2. Forge acts safer because execution is previewed, approved, audited, and reversible.
3. Forge improves over time because repeated work becomes governed skills.
4. Forge is easier to trust because every plan, memory, approval, and operation is inspectable.
5. Forge is easier to adopt because it has a clear CLI, demo, docs, and local-first behavior.

If a feature does not strengthen one of these claims, it should wait.
