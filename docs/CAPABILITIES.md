# Capabilities

Show current local abilities:

```bash
forge-agent capabilities
```

Show structured output:

```bash
forge-agent capabilities --json
```

Current local abilities:

- summarize notes
- rewrite text
- translate text placeholder
- draft follow-up text
- preview and run safe folder organization for invoice or receipt files
- restore the latest file organization operation

## File organization through `do`

Preview first:

```bash
forge-agent do --preview --human "organize folder ./invoices"
```

Run after review:

```bash
forge-agent do --execute "organize folder ./invoices"
```

The preview mode does not move files. Execute mode uses the existing file organizer path with operation records and rollback support.

## Restore the latest file organization

Preview restore:

```bash
forge-agent do --preview --human "undo last organize"
```

Run restore:

```bash
forge-agent do --execute "undo last organize"
```

Preview mode explains what will be restored. Execute mode restores files from the latest file organization operation.
