---
name: session-state
description: >-
  Manages the .ccu/ directory for session continuity, evidence logging, decision
  tracking, and crash recovery. Use when initializing a project session, writing
  evidence after bead completion, recording architectural decisions, or preparing
  session handoffs. Triggers on .ccu, session state, evidence, checkpoint, handoff,
  decisions.
domain: project-management
role: specialist
triggers:
  - session
  - .ccu
  - evidence
  - decisions
  - checkpoint
  - handoff
  - session state
---

# Session State Management

Session state lives entirely in the project's local **`.ccu/` directory** — a single, in-repo layer with no external storage or sync. Everything is plain Markdown that git can track and any editor can browse.

## .ccu/ Files

| File | Purpose | Written By |
|------|---------|-----------|
| `CAPTURES.md` | Ad-hoc ideas queue (fast-write buffer) | `t:capture` |
| `DECISIONS.md` | Architectural decisions log (append-only) | `t:auto`, `t:done`, `t:handoff`, `t:audit-decisions` |
| `EVIDENCE.md` | Completed-bead evidence log (append-only) | `t:auto` |
| `HANDOFF.md` | Latest session handoff (overwritten each pause) | `t:handoff` |

`SESSION.md` and `CHECKPOINT.md` are legacy and should not be created or written to. If they exist from a prior session, ignore or delete them.

### .gitignore

`CAPTURES.md` is ephemeral and gitignored, as are the `artifacts/` working docs and the `brainstorm/` visual-companion scratch:

```
# ccu session artifacts (ephemeral)
.ccu/CAPTURES.md
.ccu/artifacts/
.ccu/brainstorm/
```

`DECISIONS.md`, `EVIDENCE.md`, and `HANDOFF.md` are **not** gitignored — they are durable project history and should be committed so every session shares them.

## Log Formats

Decisions and evidence are append-only logs: each new item is a new `##` section at the end of the file. Never rewrite or remove existing sections.

### Decisions (`.ccu/DECISIONS.md`)

One `##` section per decision:

```markdown
## D001 — Keep t: command prefix

**Date:** 2026-03-19
**Context:** {what prompted this}
**Decision:** {what was decided}
**Rationale:** {why}
**Alternatives:** {what else was considered}
```

### Evidence (`.ccu/EVIDENCE.md`)

One `##` section per completed bead:

```markdown
## {bead-id} — {bead title}

**Date:** {completion date}
**Commit:** {hash}
**Files changed:** {list}
**Lines:** +{added} / -{removed}
**Verification:**
- tests: {result}
- lint: {result}
- typecheck: {result}
**Actor:** {agent name or "user"}
```

### Handoff (`.ccu/HANDOFF.md`)

A single latest handoff — overwrite it each time a session pauses:

```markdown
# Session Handoff — {date} {time}

## Decisions Made
- {decision and why}

## Next Action
{ONE clear recommendation}

## Open Questions
- {unresolved items}

## In-Progress Beads
- {bead-id} — {title}: {state}
```

## Artifacts HTML index (`.ccu/artifacts/<dir>/`)

Longer-form working docs — discovery, approach, execution plans, designs, epic summaries — live in per-feature subdirectories under `.ccu/artifacts/<dir>/`, written by [[plan-beads]], [[brainstorming]], and [[orchestrator]]. These pile up as loose `.md` files that are tedious to read in a terminal.

**Convention: every `.ccu/artifacts/<dir>/` gets a browsable `index.html` viewer.** Whenever a skill writes or updates any `.md` in one of these directories, regenerate the viewer as the last step:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/markdown-html-viewer/scripts/md2html.py" .ccu/artifacts/<dir>/
```

Pointing the script at the **directory** produces a **single `index.html` with a document-switcher dropdown** in the header — one page that swaps between discovery / approach / execution-plan, each with its own TOC, Mermaid rendering, and callouts. `README.md` sorts first, the rest alphabetically.

- **Fetch mode is the default and the right choice here** — no `--inline`. The HTML `fetch()`es each `.md` at load, so the `.md` files stay the single live source: edit a doc, refresh the page, done. Nothing is baked into the HTML, so the index never goes stale between edits.
- **This is an intentional exception to the markdown-html-viewer skill's "ask how to build it" step.** For automated `.ccu/artifacts` generation, do **not** prompt the user for mode/layout — always use directory + fetch (switcher index). The ask only applies when a user directly invokes the viewer on their own docs.
- **Regenerate, don't append** — rerun the one command after each write; it rewrites `index.html` to include any new docs. Cheap and idempotent.
- **Viewing** — a fetch page can't be opened by double-click (`file://` blocks fetching siblings). Open it with the dev-browser helper: `"${CLAUDE_PLUGIN_ROOT}/skills/markdown-html-viewer/scripts/open_in_dev_browser.sh" .ccu/artifacts/<dir>/index.html`. Mention this path to the user when you hand off artifacts.
- **Gitignored** — `index.html` lives inside `.ccu/artifacts/`, which is already gitignored (local working files), so it needs no separate ignore entry and is never committed.

## Initialization

When initializing `.ccu/` (typically via `t:init`):

1. Create `.ccu/` directory if it doesn't exist
2. Create `CAPTURES.md` if it doesn't exist
3. Ensure `.gitignore` includes `.ccu/CAPTURES.md`, `.ccu/artifacts/`, and `.ccu/brainstorm/`

Do NOT create `SESSION.md` or `CHECKPOINT.md` — these are legacy.

## Cleanup

When ending a session (`t:done`):
- Warn if `CAPTURES.md` has unchecked items
- Do NOT clear or delete any `.ccu/` files (captures and cache persist across sessions)

## Graceful Degradation

- **No `.ccu/` directory** — create it, or skip if the command is read-only
- **No log file yet** — create it on first write (append to a fresh file)
- **Never fail** because a `.ccu/` file is missing — recreate what's needed and continue

## Rules

- **CAPTURES.md is the fast lane** — captures always go to `.ccu/CAPTURES.md` first (speed matters). During triage, items are promoted into beads or the decisions/evidence logs.
- **Logs are append-only** — never remove or modify existing decision/evidence sections.
- **Durable logs are committed** — `DECISIONS.md`, `EVIDENCE.md`, and `HANDOFF.md` go into git so all sessions share them.
