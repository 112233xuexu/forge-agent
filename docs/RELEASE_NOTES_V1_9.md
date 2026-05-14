# Forge Agent v1.9.0: Brain Adapter planning layer

Forge Agent is now an ordinary-user local automation MVP with a deterministic Brain Adapter planning layer.

## Highlights

- v1.1 real dry-run-first organize command
- v1.2 skill lifecycle controls
- v1.3 rollback for approved organize operations
- v1.4 operation history
- v1.5 schedule registry
- v1.6 PPT/report local artifact generation
- v1.7 news brief template generation
- v1.8 video storyboard generation
- v1.9 Brain Adapter planning with `forge-agent ask`

## New in v1.9

- `forge-agent ask "..." --json`
- `BrainAdapter` and `BrainPlan`
- Ask-aware CLI entrypoint wrapper
- Structured plan fields:
  - goal
  - intent
  - next step
  - safety level
  - suggested command
  - confidence
  - notes
  - metadata
- Brain Adapter tests
- CI smoke coverage for `forge-agent ask`
- Documentation: `docs/V1_9_BRAIN_ADAPTER.md`

## Product principle

```text
Brain suggests. Forge Agent governs.
```

The Brain Adapter suggests a structured plan. Forge Agent remains responsible for preview, approval, evidence, history, rollback, and skill lifecycle behavior.

## Validation

```bash
python -m compileall src tests
python -m pytest -q tests/test_public_runtime.py tests/test_organizer.py tests/test_skills_lifecycle.py tests/test_product_packs.py tests/test_brain_adapter.py
forge-agent demo --kind file-organizer --json
forge-agent organize ./invoices --json
forge-agent ask "organize my receipts" --json
```

## Honest limitations

- Brain Adapter is deterministic and local first.
- Provider-backed planning is not included yet.
- There is no hidden background work.
- News, PPT/report, and storyboard are template/local artifact surfaces first.
- Schedule registry stores schedule records but does not yet run a background daemon.

## Suggested GitHub Release fields

Tag: `v1.9.0-brain-adapter`

Title: `Forge Agent v1.9.0: Brain Adapter planning layer`

Target: `main`
