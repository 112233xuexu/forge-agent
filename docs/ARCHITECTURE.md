# Architecture

Forge Agent is organized around a small runtime core and a set of operator-facing release gates.

## Layers

1. CLI entrypoint: accepts ordinary-language goals and maintenance commands.
2. Runtime facade: records task requests and provides a stable public interface for future agent execution.
3. Memory and governance: the RC10 source package contains historical implementations for memory freshness, quarantine, recovery, governance ledgers, repair queues, and release stability controls.
4. Gateway and desktop shell: the RC10 package includes gateway/channel code and a Tauri desktop-shell source tree.
5. Validation: release scripts and evidence reports are preserved in the prepared source package.

## Current repository shape

The repository now exposes a clean open-source landing page, package metadata, smoke-tested public runtime facade, CI workflow, contribution guide, and security policy. The prepared RC10 source package remains available from the maintainer's generated source archive and can be normalized into regular repository files during follow-up maintenance.

## Maintainer priorities

- Keep public claims aligned with checked-in evidence.
- Move the full RC10 source tree into normal source files.
- Add small public demos and screenshots.
- Add focused tests for CLI, runtime, gateway, governance, and desktop packaging.
