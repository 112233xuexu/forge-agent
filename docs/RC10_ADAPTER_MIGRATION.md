# RC10 adapter migration

This note records the adapter slices added after the main RC10 compatibility migration document.

## Added adapters

- `desktop_adapter.py` provides a local desktop/client request adapter around `CompatRuntime`.
- `http_adapter.py` provides a pure HTTP payload adapter. It does not run a web server.
- `benchmark.py` provides local compatibility smoke checks for runtime, memory/context, and state-store slices.

## Added persistence

- `session_state.py` now persists generic documents, palace graphs, skill libraries, and ledger entries in addition to sessions, messages, and checkpoints.

## Tests

- `tests/test_desktop_adapter_compat.py`
- `tests/test_http_adapter_compat.py`
- `tests/test_benchmark_compat.py`
- `tests/test_state_store_extended_compat.py`

These are additive compatibility layers and do not replace the existing public CLI/runtime behavior.
