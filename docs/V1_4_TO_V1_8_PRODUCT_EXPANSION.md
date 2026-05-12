# v1.4-v1.8 Product Expansion

## Purpose

Forge Agent must not remain a file organizer. File organization is the first trust-building skill pack, but the product direction is a general ordinary-user automation system.

This expansion adds local, reviewable product surfaces for:

- v1.4 Operation History
- v1.5 Scheduler Registry
- v1.6 PPT / Report generation
- v1.7 News Brief template
- v1.8 Video Storyboard template

These are deterministic local implementations first. Later releases can connect model providers, browser/web search, slide rendering, TTS, FFmpeg, and desktop notifications.

## v1.4 History

```bash
forge-agent history list
forge-agent history show <operation_id>
```

History reads operation manifests under `.forge-agent/operations` and gives the user a single place to inspect what happened.

## v1.5 Schedule registry

```bash
forge-agent schedule add "every day 9am" forge-agent organize ~/Downloads
forge-agent schedule list
forge-agent schedule pause <task_id>
forge-agent schedule resume <task_id>
```

v1.5 stores schedules safely. It does not yet run a background daemon. This is intentional: the schedule contract is visible before automatic execution is enabled.

## v1.6 PPT / Report maker

```bash
forge-agent make ppt "project status update"
forge-agent make report "monthly validation report"
```

The current implementation writes Markdown artifacts under `.forge-agent/artifacts`. Later versions can render `.pptx`, `.docx`, and `.pdf`.

## v1.7 News brief

```bash
forge-agent make news "AI agent ecosystem"
```

The current version creates an offline news brief template. It does not claim live news retrieval. Later versions should add web sources, citations, deduplication, and schedule integration.

## v1.8 Video storyboard

```bash
forge-agent make storyboard "30-second Forge Agent product demo"
```

The current version creates a storyboard and production checklist. Later versions can add script generation, TTS, subtitles, and FFmpeg rendering.

## Product meaning

The product loop expands from one skill pack into a multi-skill ordinary-user automation surface:

```text
plain command -> skill pack -> preview/template -> approval when risky -> artifact/history -> reuse/schedule
```

## Validation

```bash
python -m pytest -q tests/test_product_packs.py
```
