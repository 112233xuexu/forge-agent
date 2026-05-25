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
