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
- run a complete local user-flow demo with pass/fail checks
- run readiness checks with optional demo validation
- run a short product smoke check for capabilities and the user-flow demo

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

## Complete local demo

Run the full user flow demo:

```bash
forge-agent demo --kind user-flow
```

Structured output:

```bash
forge-agent demo --kind user-flow --json
```

The demo creates sample files in a sandbox, previews organization, executes organization, restores the latest organization, and reports explicit pass/fail checks plus final file state.

## Readiness with demo validation

Basic readiness:

```bash
forge-agent readiness
```

Readiness plus full local demo validation:

```bash
forge-agent readiness --run-demo
```

Structured output:

```bash
forge-agent readiness --run-demo --json
```

The demo validation path reports whether the local user-flow demo passed, including explicit checks and final file state.

## Product smoke check

Run a short local product smoke check:

```bash
forge-agent smoke
```

Structured output:

```bash
forge-agent smoke --json
```

The smoke check verifies that the public capability registry is populated and that the local user-flow demo passes. JSON output includes `diagnostics.problem_checks`, `diagnostics.problem_demo_checks`, and `diagnostics.suggested_command` to make failures easier to inspect in CI logs.
