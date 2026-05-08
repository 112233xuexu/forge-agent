# Security Policy

Forge Agent is an experimental agent runtime and desktop source tree. Treat it as pre-GA software unless your own deployment has completed independent security review.

## Reporting a vulnerability

Please do not open a public issue for exploitable vulnerabilities. Contact the repository owner privately with:

- a concise description of the issue;
- affected files or commands;
- reproduction steps;
- impact assessment;
- any proposed fix.

## Operator guidance

- Do not commit API keys, signing certificates, private customer data, or production telemetry.
- Use runtime-provided secrets for gateway auth and HMAC signing.
- Run the release environment and GA readiness checks before making production-ready claims.
- Review desktop bundling, sidecar execution, and update/distribution channels before shipping installers.
