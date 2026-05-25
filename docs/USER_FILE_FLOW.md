# User file flow

Forge Agent can route plain `do` requests into the safe local file organizer.

## Preview first

```bash
forge-agent do --preview --human "organize folder ./invoices"
```

Preview mode prepares a plan and does not move files.

## Execute

```bash
forge-agent do --execute --human "organize folder ./invoices"
```

Execute mode uses the existing file organizer. It can move invoice or receipt files into month folders and records an operation manifest.

## JSON output

```bash
forge-agent do --preview "organize folder ./invoices"
forge-agent do --execute "organize folder ./invoices"
```

Omit `--human` to keep structured JSON output for tests or scripts.

## Safety notes

- Preview does not move files.
- Execute is limited to the local folder path in the request.
- The flow reuses the organizer manifest and rollback support.
- Missing folder paths return an input-required result.
