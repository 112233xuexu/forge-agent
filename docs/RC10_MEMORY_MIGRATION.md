# RC10 memory core migration

This branch moves the first runnable memory-core slice from the prepared RC10 source archive into the normal repository source tree.

## Added modules

- `src/forge_agent/models.py` with `MemoryRecallHit`, the shared recall candidate model.
- `src/forge_agent/memory_guard.py` with local text normalization and task anchoring helpers.
- `src/forge_agent/memory_freshness.py` with deterministic freshness weighting.
- `src/forge_agent/memory_ranking.py` with query profiling and ranked recall output.
- `src/forge_agent/memory_resolution.py` with conflict suppression by semantic slot.
- `src/forge_agent/memory_verdict.py` with final adoption/rejection metadata.
- `src/forge_agent/memory_engine.py` with the composed public pipeline.

## Why this is additive

The current public CLI and runtime already include later ordinary-user task-card work. This migration intentionally does not overwrite those files. The memory core is introduced as an additive subsystem so follow-up PRs can connect it to `ask`, task planning, workspace state, and user-facing output without regressing the existing command registry.

## Verification

The new `tests/test_memory_engine_pipeline.py` covers:

- anchored recall winning over unrelated memory,
- conflict resolution between stale and fresh facts in the same slot,
- limit handling for adopted memory context,
- verdict re-anchor safety when quarantine blocks adoption.

Run locally with:

```bash
python -m pytest tests/test_memory_engine_pipeline.py
```
