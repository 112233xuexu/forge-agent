# RC10 memory migration

This branch moves runnable memory subsystems from the prepared RC10 source archive into the normal repository source tree.

## Added core modules

- `src/forge_agent/models.py` with `MemoryRecallHit`, the shared recall candidate model.
- `src/forge_agent/memory_guard.py` with local text normalization and task anchoring helpers.
- `src/forge_agent/memory_freshness.py` with deterministic freshness weighting.
- `src/forge_agent/memory_ranking.py` with query profiling and ranked recall output.
- `src/forge_agent/memory_resolution.py` with conflict suppression by semantic slot.
- `src/forge_agent/memory_verdict.py` with final adoption/rejection metadata.
- `src/forge_agent/memory_engine.py` with the composed public pipeline.

## Added hardening modules

- `src/forge_agent/memory_continuity.py` with focus digesting and drift comparison.
- `src/forge_agent/memory_soak.py` with contamination scoring and stable-window tracking.
- `src/forge_agent/memory_recovery.py` with guarded re-anchor decisions.
- `src/forge_agent/memory_quarantine.py` with off-focus/stale/conflict filtering.

## Why this is additive

The current public CLI and runtime already include later ordinary-user task-card work. This migration intentionally does not overwrite those files. The memory subsystems are introduced as additive modules so follow-up PRs can connect them to `ask`, task planning, workspace state, and user-facing output without regressing the existing command registry.

## Verification

The new `tests/test_memory_engine_pipeline.py` covers:

- anchored recall winning over unrelated memory,
- conflict resolution between stale and fresh facts in the same slot,
- limit handling for adopted memory context,
- verdict re-anchor safety when quarantine blocks adoption.

The new `tests/test_memory_hardening_pipeline.py` covers:

- continuity drift detection,
- memory soak risk scoring and stable low-risk windows,
- recovery re-anchor adoption,
- quarantine filtering for off-focus trace hits.

Run locally with:

```bash
python -m pytest tests/test_memory_engine_pipeline.py tests/test_memory_hardening_pipeline.py
```
