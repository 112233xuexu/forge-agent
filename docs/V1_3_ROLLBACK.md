# v1.3 Undo / Rollback

## Purpose

Ordinary users will not trust an automation agent that moves files without a safe way back.

v1.3 adds rollback support for approved file-organization operations. This makes Forge Agent safer and more product-like: preview first, approve explicitly, execute, record evidence, and undo if needed.

## Commands

Run a dry-run preview first:

```bash
forge-agent organize ./invoices
```

Approve real movement:

```bash
forge-agent organize ./invoices --approve
```

Rollback the most recent approved organize operation:

```bash
forge-agent organize-rollback
```

Rollback a specific operation:

```bash
forge-agent organize-rollback --operation-id <operation_id>
```

JSON output:

```bash
forge-agent organize-rollback --json
```

## Evidence files

Approved organize operations write:

```text
.forge-agent/operations/organize-<operation_id>.json
.forge-agent/operations/latest-organize.json
.forge-agent/organize-manifest.json
```

The operation manifest records:

- operation id;
- source folder;
- output folder;
- skill id;
- approval id;
- moved files;
- rollback timestamp when rolled back;
- restored files;
- skipped files.

## Safety model

Rollback does not overwrite user files.

It restores a moved file only when:

1. the moved file still exists at its organized destination;
2. the original path is free.

It skips safely when:

- the moved file no longer exists;
- the original path already exists.

Skipped files are recorded in the manifest.

## Product loop

```text
plain command -> dry-run -> approval -> execution -> manifest -> rollback
```

## Validation

```bash
python -m pytest -q tests/test_organizer.py
```

The rollback tests cover:

- approved organize writes an operation manifest;
- rollback restores moved files;
- rollback skips instead of overwriting when the original path already exists.
