# Ordinary-user demo: file organizer

## Goal

Show the Forge Agent product promise in one safe local demo:

> The user gives a normal command. Forge Agent creates or selects a skill, asks before risky file operations, records approval, organizes files, writes evidence, and proves skill reuse.

## Run it

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
forge-agent demo --kind file-organizer
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
forge-agent demo --kind file-organizer
```

JSON output:

```bash
forge-agent demo --kind file-organizer --json
```

## What it proves

The demo creates a sandbox workspace under `.forge-agent/demo-file-organizer`. It does not touch real user folders.

It then performs this loop:

1. Creates sample invoice, receipt, and non-invoice files.
2. Receives the ordinary-user goal: organize invoices and receipts by month and produce a list.
3. Creates or selects a reusable local skill.
4. Creates a plain-language approval request before moving files.
5. Records the approval decision in `approvals.jsonl`.
6. Moves invoice/receipt files into month folders.
7. Writes `manifest.json` with evidence.
8. Adds a second batch of similar files.
9. Reuses the same skill and reports `reuse_proven: true`.

## Why this is different

This demo is intentionally not a framework tutorial. The user does not install a skill, browse a marketplace, configure a provider, or learn a plugin system. The agent manages the skill lifecycle behind the command.

## Expected evidence

After running the demo, check:

- `.forge-agent/demo-file-organizer/manifest.json`
- `.forge-agent/demo-file-organizer/approvals.jsonl`
- `.forge-agent/demo-file-organizer/skills/index.jsonl`
- `.forge-agent/demo-file-organizer/organized/2026-01/`
- `.forge-agent/demo-file-organizer/organized/2026-02/`
- `.forge-agent/demo-file-organizer/organized/2026-03/`

The manifest should contain:

```json
{
  "created_skill": true,
  "reuse_proven": true
}
```

## Product interpretation

This is the smallest public proof of the Forge Agent direction:

```text
plain command -> auto skill -> approval -> safe execution -> evidence -> reuse
```

Future work should replace the deterministic demo executor with the fuller RC10 runtime and skill-growth engine while keeping this ordinary-user surface.
