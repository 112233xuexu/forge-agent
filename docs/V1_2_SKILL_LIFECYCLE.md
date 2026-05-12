# v1.2 Skill Lifecycle

## Purpose

Forge Agent's differentiator is not just that it can create a skill. The skill must become a reusable, auditable, and controllable asset.

v1.2 adds explicit skill lifecycle states and CLI controls so ordinary users and maintainers can decide which skills are trusted, promoted, deprecated, or quarantined.

## Lifecycle states

```text
draft -> tested -> validated -> promoted
```

Risk/retirement states:

```text
deprecated
quarantined
```

## Automatic rules

- A newly auto-created skill starts as `draft`.
- First successful use moves it to `tested`.
- Three successful uses move it to `validated`.
- Three failures with no successes move it to `quarantined`.
- `deprecated` and `quarantined` skills are not automatically matched for future work.

## CLI controls

List skills:

```bash
forge-agent skills
forge-agent skills list
forge-agent skills list --json
```

Show one skill:

```bash
forge-agent skills show <skill_id>
```

Change status:

```bash
forge-agent skills test <skill_id>
forge-agent skills validate <skill_id>
forge-agent skills promote <skill_id> --reason "works reliably"
forge-agent skills deprecate <skill_id> --reason "replaced by better skill"
forge-agent skills quarantine <skill_id> --reason "unsafe behavior"
```

## What gets recorded

Each skill records:

- status;
- uses;
- success count;
- failure count;
- last used timestamp;
- lifecycle log;
- triggers;
- steps.

The generated skill markdown file includes lifecycle metadata so the user can inspect what the agent learned.

## Why this matters

This turns skills from invisible runtime artifacts into manageable product assets. It also supports future cloud skill-library work: only validated or promoted skills should be eligible for sharing.

## Validation

```bash
python -m pytest -q tests/test_skills_lifecycle.py
```
