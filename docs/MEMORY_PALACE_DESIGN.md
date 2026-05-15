# Forge Agent Memory Palace Design

This document is a design note for v2.5. It does not change the current runtime behavior.

The goal is to study MemPalace-style long-term memory without turning Forge Agent into a clone. Forge Agent should learn from the strong parts of memory-palace systems while keeping its own product direction: ordinary-user safety, transparency, approval, evidence, rollback, and local-first control.

## Product goal

Forge Agent should support a controlled memory palace:

```text
plain request -> scoped memory retrieval -> plan -> preview -> approval -> execution -> evidence -> rollback -> learning
```

Memory should make the agent more useful across sessions, but memory must remain visible, editable, forgettable, auditable, and bounded.

## What to learn from MemPalace

MemPalace-style systems are valuable because they treat memory as an external, persistent, searchable vault instead of relying only on hidden model context.

Key ideas to adapt:

- Palace hierarchy: palace, wing, room, closet, drawer, memory item.
- Local-first persistent storage.
- Cross-session recall.
- Verbatim-first memory when exact evidence matters.
- Low wake-up context: retrieve only relevant memory instead of loading everything.
- Deterministic write path where possible.
- Runtime-discoverable memory commands.
- Agent diary or task diary for operation-level memory.

## Forge differentiation

Forge Agent should add stricter governance:

- Every stored memory is inspectable.
- Every memory can be forgotten.
- Memory writes are logged in an audit file.
- Memory has explicit scope.
- Sensitive memory can be marked or quarantined.
- Permanent memory should not be silently created by an LLM.
- Retrieval should be bounded and explainable.
- Memory connects to skills, approvals, history, manifests, and rollback evidence.

The rule is:

```text
Memory helps the agent remember, but Forge governs what memory can do.
```

## Local layout

Suggested workspace layout:

```text
.forge-agent/memory/
  palace.json
  index.jsonl
  audit.jsonl
  USER.md
  MEMORY.md
  wings/
    user/
    project/
    skills/
    operations/
    sessions/
```

Files:

- `palace.json`: high-level map of wings and default routing rules.
- `index.jsonl`: one line per memory item.
- `audit.jsonl`: append-only log of memory add, update, forget, quarantine, and retrieval events.
- `USER.md`: stable user preferences and long-term user rules.
- `MEMORY.md`: stable project context, decisions, and conventions.
- `wings/*`: optional folder-backed storage for readable memory groups.

## Hierarchy

```text
Palace -> Wing -> Room -> Closet -> Drawer -> Memory item
```

Suggested wings:

| Wing | Purpose |
|---|---|
| `user` | User preferences, stable facts, workflow habits |
| `project` | Project rules, architecture, roadmap decisions |
| `skills` | Skill usage lessons, success/failure notes, improvement ideas |
| `operations` | Approval records, manifests, rollback notes, safety evidence |
| `sessions` | Temporary context for recent sessions |

## Memory item schema

```json
{
  "id": "mem_...",
  "scope": "user/project/session/skill/operation",
  "wing": "project",
  "room": "roadmap",
  "closet": "v2.5",
  "drawer": "memory-palace",
  "content": "...",
  "source": "manual/runtime/skill/operation",
  "created_at": "...",
  "last_used_at": null,
  "confidence": 1.0,
  "safety": "normal/sensitive",
  "status": "active/forgotten/quarantined"
}
```

## v2.5 CLI target

Minimum controlled memory commands:

```bash
forge-agent memory add "..."
forge-agent memory list --json
forge-agent memory show <memory_id>
forge-agent memory forget <memory_id>
forge-agent memory search "query" --json
forge-agent memory palace --json
forge-agent memory audit --json
forge-agent memory doctor
```

Expected JSON envelope:

```json
{
  "ok": true,
  "memory": {
    "id": "mem_..."
  }
}
```

Error envelope:

```json
{
  "ok": false,
  "error": "not_found",
  "message": "memory not found: mem_..."
}
```

## Write policy

Memory writes should start conservative.

Allowed by default:

- User manually adds memory.
- Runtime writes operation memory for approved actions.
- Runtime writes skill lessons after successful local operations.

Requires explicit approval or future policy:

- LLM proposes permanent user memory.
- Imported skill writes memory.
- Sensitive memory is stored.
- Memory is promoted from session scope to user/project scope.

## Retrieval policy

Memory retrieval should be bounded.

Initial rule:

```text
Retrieve at most N active memories relevant to the command, include source metadata, and never inject forgotten or quarantined memories.
```

Suggested metadata in `BrainPlan` later:

```json
{
  "memory_used": [
    {
      "id": "mem_...",
      "wing": "project",
      "reason": "matched roadmap and v2.5"
    }
  ]
}
```

## Safety model

Memory must not bypass existing Forge safety systems.

- Memory does not execute actions.
- Memory does not approve actions.
- Memory cannot bypass dry-run.
- Memory cannot bypass rollback evidence.
- Memory can inform planning, skill selection, and user context only.

## v2.5 implementation boundary

v2.5 should be a foundation release, not a full MemPalace clone.

In scope:

- Local memory store.
- Palace hierarchy metadata.
- Add/list/show/forget/search commands.
- Audit log.
- JSON envelopes.
- Tests and release notes.

Out of scope for v2.5:

- Vector database.
- Embedding model.
- LLM-based memory extraction.
- Automatic sensitive memory inference.
- Full provider-backed memory injection.
- Skill marketplace.

## Future versions

### v2.6

- Bounded memory retrieval for `forge-agent ask`.
- Memory source explanation in BrainPlan metadata.
- SKILL.md import/export foundation.

### v2.7

- Optional provider-backed Brain Adapter.
- LLM proposes plan only.
- Forge still governs preview, approval, execution, evidence, and rollback.

### v2.8

- Learning loop.
- Detect repeated successful tasks.
- Propose reusable skills and memory updates.
- Require approval before permanent promotion.

### v3.0

- Memory palace + skills + brain + approvals + rollback + scheduler + demo evidence.
- Positioning: safer ordinary-user automation, not an expert-only agent framework.

## Design principle

```text
Competitors remember more.
Forge remembers safely, visibly, and usefully.
```
