# Source Deep Read Audit

## Summary

The original RC10 source package is much deeper than the current public repository surface. It is not merely a lightweight CLI skeleton. It already contains a substantial self-growing runtime with ordinary-user goal handling, skill growth, memory, scheduling, gateway adapters, governance, desktop bridge, release gates, and many tests.

The public repository should therefore stop treating Forge Agent as a new-from-scratch skeleton. The next development direction should be: **extract, normalize, productize, and simplify the existing RC10 core**.

## What the original source already has

### 1. Ordinary-user entrypoint

The original runtime includes `run_user_goal`, `continue_user_goal`, `run_user_goal_inbox`, `run_user_goal_autopilot`, `run_user_goal_single_entry`, and multiple proof/gate helpers. This already matches the product idea: users state a goal and the system handles lower-level runtime details.

### 2. Skill growth engine

The original package includes `skill_growth.py` with `SkillGrowthEngine`. It can inspect successful traces, classify the resulting skill kind, build templated steps, infer reusable inputs, create `SkillDefinition` records, upgrade existing skills, and validate skill candidates.

This is much closer to the intended vision than the temporary public skeleton.

### 3. Skill matching and capability routing

The original runtime contains skill gap inspection, capability route building, preferred-skill fallback, capability registry integration, skill plugin registration, skill reuse feedback, and route health accounting.

This means Forge Agent already has primitives for comparing itself to Hermes/OpenClaw-style systems. The task is to make them understandable and usable for ordinary users.

### 4. Memory system

The source contains memory modules for continuity, freshness, guardrails, quarantine, ranking, recovery, resolution, soak, verdicts, and scorecards. This is a meaningful differentiator if presented as ordinary-user memory controls instead of internal jargon.

### 5. Gateway and scheduler

The source includes local/webhook/http gateway paths, delivery contracts, idempotency, scheduler support, scheduled task handling, and inbox/resume paths.

### 6. Governance and release evidence

The source has extensive governance, stabilization, policy, incident, reconciliation, seal, graduation, and campaign machinery. It also includes release gates, proof drills, brutal validation reports, desktop release environment probes, and GA readiness checks.

This is valuable, but it is currently too operator-heavy for ordinary users.

### 7. Desktop path

The source includes a Tauri desktop shell and `desktop_bridge.py` with health, run-goal, continue-goal, status, history, operator snapshot, batch, and proof drill paths. This aligns with the ordinary-user target.

## What is missing from the current public repo

The current public repository has a clean README, docs, CLI skeleton, and local skill draft store, but it does not yet expose the real RC10 runtime modules. This creates a mismatch:

- The uploaded source is strong and complex.
- The public repository is simple and presentable.
- The next step is to merge them carefully, not to keep building only the skeleton.

## Key product judgment

Forge Agent's strongest path is not "copy Hermes Agent" or "copy OpenClaw". The original code already shows teacher alignment with Hermes/OpenClaw/MemPalace. The differentiator should be:

> Hide the agent framework. Expose a normal user command surface. Let the system find, create, validate, reuse, and explain skills automatically.

## Immediate engineering plan

1. Port the original `models.py`, `session_state.py`, `skill_growth.py`, `skill_utils.py`, `planner.py`, `tool_registry.py`, `plugin_registry.py`, and `builtin_tools.py` into the public repo.
2. Preserve the current public README and product docs, but make them point at the real runtime.
3. Replace the temporary lightweight `SkillStore` with adapters around the original `SkillGrowthEngine` and `SkillDefinition` model.
4. Keep the simplified CLI commands (`init`, `do`, `tasks`, `skills`, `doctor`) as the ordinary-user layer above the full runtime.
5. Add a demo focused on ordinary users, not agent researchers.
6. Add tests proving: command -> skill match/create -> approval if risky -> execution/result -> reusable skill.

## Honest risk

The RC10 source has a lot of internal gates and historical version layers. That is good evidence, but it also risks making the product feel complicated. The next phase must simplify the user surface while preserving the strong engine underneath.
