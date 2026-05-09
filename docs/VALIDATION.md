# Forge Agent RC10 Validation Update

## Scope

Validated the original uploaded RC10 source package, not only the lightweight public GitHub skeleton.

## Commands run

```bash
python -m compileall -q src tests
pytest --collect-only -q
pytest -q tests/test_system.py
pytest -q tests/test_skill_growth.py
pytest -q tests/test_user_goal.py
pytest -q tests/test_cli.py::PalaceTraverseCliTests::test_inspect_memory_scorecard_history_and_regression_cli \
  tests/test_cli.py::PalaceTraverseCliTests::test_inspect_memory_scorecard_trend_cli \
  tests/test_cli.py::PalaceTraverseCliTests::test_inspect_palace_traverse_cli \
  tests/test_cli.py::PalaceTraverseCliTests::test_memory_sweep_alias_rooms_cli \
  tests/test_cli.py::CliVersionTests::test_cli_version_flag_outputs_package_version \
  tests/test_cli.py::CliVersionTests::test_gateway_release_guard_apply_rolls_back_current_release
```

## Results

- Compile check: passed.
- Test collection: 517 tests collected.
- `tests/test_system.py`: initially failed on a stale version assertion expecting `1.0.0rc7`; after updating the assertion to `1.0.0rc10`, passed 20/20.
- `tests/test_skill_growth.py`: passed 5/5.
- `tests/test_user_goal.py`: passed 57/57.
- Selected CLI tail tests: passed 6/6.
- Full `tests/test_cli.py` did not complete within the interactive timeout. Individual and grouped CLI subsets passed; no explicit assertion failure was observed in the timed run.

## Confirmed architecture from source reading

The source includes real components for:

- ordinary-user goal entry (`run_user_goal`, autopilot, inbox, single-entry paths);
- skill growth (`SkillGrowthEngine`, `SkillDefinition`, trace-to-skill promotion);
- skill reuse and `skill_reuse_success` accounting;
- memory continuity, freshness, guardrails, quarantine, ranking, recovery, and verdicts;
- gateway, scheduler, webhook, HTTP delivery, idempotency, and signing policy;
- governance, release gates, proof drills, ultimate gate, and desktop bridge;
- desktop-shell source and release environment checks.

## Current judgment

The project already contains the core of the original vision: a self-growing ordinary-user agent runtime. The main problem is productization and public-repo normalization, not absence of core logic.

## Next engineering step

Normalize the original RC10 source into the public GitHub repository while preserving the simple ordinary-user surface:

```bash
forge-agent init
forge-agent do "..."
forge-agent tasks
forge-agent skills
forge-agent doctor
```

Then wire that simple surface to the real RC10 runtime/skill-growth engine instead of the temporary lightweight facade.
