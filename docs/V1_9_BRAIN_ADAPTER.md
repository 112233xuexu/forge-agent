# v1.9 Brain Adapter

## Purpose

v1.9 adds a planning layer for ordinary-language requests.

The important product rule is simple:

```text
Brain suggests. Forge Agent governs.
```

The brain adapter turns a user request into a structured local plan. It does not replace Forge Agent's preview, approval, evidence, history, rollback, or skill lifecycle behavior.

## Command

```bash
forge-agent ask "organize my invoices by month" --json
```

Example JSON fields:

```json
{
  "goal": "organize my invoices by month",
  "intent": "organize_files",
  "next_step": "preview organize plan",
  "needs_user_approval": false,
  "confidence": 0.75,
  "notes": ["dry run first"]
}
```

## MVP scope

- Provider-neutral `BrainAdapter` interface.
- Deterministic local planning for tests and offline demos.
- `forge-agent ask` command for plan preview.
- Existing v1.1-v1.8 commands remain unchanged.

## Supported local intents

- `organize_files`
- `make_ppt`
- `make_report`
- `make_news`
- `make_storyboard`
- `local_task`
- `unknown`

## Non-goals

- No provider lock-in.
- No hidden automation.
- No claim that a model is the safety boundary.

## Product loop

```text
ordinary request -> structured plan -> preview -> approval when needed -> evidence -> history -> rollback where supported
```

## Validation

```bash
python -m pytest -q tests/test_brain_adapter.py
```
