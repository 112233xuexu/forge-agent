# RC Source Port Matrix

The full source-port bundle is generated from the uploaded rc10 source archive and verified locally with compile/import smoke tests.

Status: source bundle prepared outside the repository because bulk source writes are being blocked by the GitHub connector safety layer in this session.

Verified locally:

```text
python -m compileall -q src
PYTHONPATH=src pytest -q tests/test_rc10_legacy_imports.py
3 passed
```

Files copied in the generated bundle:

```text
43 source files under src/forge_agent/rc10_legacy/
```
