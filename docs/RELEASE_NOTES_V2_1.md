# Forge Agent v2.1.0: File safety hardening

v2.1 continues product hardening after v2.0 by making approved file organization safer and more transparent.

## What changed

- Approved organize operations no longer overwrite an existing destination file.
- When a destination already exists, Forge Agent leaves the original source file in place.
- Skipped files are reported in `OrganizeResult.skipped_files`.
- Skipped files are written into operation manifests.
- Skipped files are also written into the latest `organize-manifest.json`.
- CI now includes skipped-file JSON/manifest coverage.

## Product meaning

v2.1 improves trust for ordinary users:

```text
safe preview -> explicit approval -> no overwrite -> visible skipped file evidence
```

## Validation

```bash
python -m pytest -q tests/test_organizer.py tests/test_organizer_skipped_json.py
forge-agent organize ./invoices --json
forge-agent organize ./invoices --approve --json
```

## Honest limitations

- v2.1 does not yet add a full conflict-resolution UI.
- Skipped files are reported, but the user must decide whether to rename, remove, or manually resolve conflicts.
- The organizer remains local-first and deterministic.
