# v1.1 Ordinary User MVP: real organize command

## Purpose

The `v1.1` upgrade turns the safe file-organizer demo into a real ordinary-user command while preserving the most important safety rule: **dry-run by default**.

## Command

Preview a plan without moving files:

```bash
forge-agent organize ./invoices
```

Move files only after explicit approval:

```bash
forge-agent organize ./invoices --approve
```

JSON output:

```bash
forge-agent organize ./invoices --json
forge-agent organize ./invoices --approve --json
```

Custom output folder:

```bash
forge-agent organize ./invoices --output ./organized-invoices --approve
```

## What it does

- Scans the selected folder for invoice/receipt-like files.
- Detects months from filenames or text, for example `2026-05`.
- Plans moves into month folders.
- Creates an approval request in the workspace approval ledger.
- In dry-run mode, moves nothing.
- With `--approve`, moves files and writes `organize-manifest.json`.
- Uses the local skill store so similar tasks can reuse the same skill.

## Safety model

Default behavior is preview-only. Real files are moved only when the user passes `--approve`.

The command records:

- planned files;
- approval id;
- skill id;
- moved files;
- manifest path.

## Tests

```bash
python -m pytest -q tests/test_organizer.py tests/test_public_runtime.py
```

## Product meaning

This is the first step from "demo candidate" toward a real user-facing MVP. The product promise remains:

```text
plain command -> automatic skill -> approval -> safe execution -> evidence -> reuse
```
