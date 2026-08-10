---
name: session-state
description: >-
  Defines the .ccu/ directory: which files exist, who writes them, and how
  recorded claims are trusted. Use when initializing a project session,
  recording architectural decisions, or handling recipe checkpoints. Triggers
  on .ccu, session state, decisions, checkpoint.
domain: project-management
role: specialist
triggers:
  - session
  - .ccu
  - decisions
  - checkpoint
  - session state
---

# Session State Management

Session state lives in the project's local `.ccu/` directory — plain Markdown, no external storage. `.ccu/` holds only session state and working documents. Project knowledge lives in structures with a real lifecycle, where being wrong becomes visible: ADRs and docs (drift from code is visible; prose rules in [[tech-doc]]), beads (statuses enforced by `br ready`), and git.

This file is the single authority for `.ccu/` file roles and formats. Commands and agents reference it; they do not restate formats.

## .ccu/ Files

| File | Role | Written by | Read at session start |
|------|------|-----------|----------------------|
| `CAPTURES.md` | Ad-hoc ideas queue (fast-write buffer) | `t:capture` | count unchecked items only |
| `CHECKPOINT.md` | Recipe progress; deleted by [[recipe]] when the recipe completes | recipe | only by recipe |
| `DECISIONS.md` | Append-only journal of dated decision claims; grep-on-demand only | `t:auto`, `t:discuss`, worker agents | never |
| `artifacts/<dir>/` | Discovery, design, and plan docs per feature/epic | [[brainstorming]], [[plan-beads]], [[orchestrator]] | on demand |
| `brainstorm/` | Visual-companion scratch | brainstorming | never |

`SESSION.md`, `HANDOFF.md`, `EVIDENCE.md`, and `REQUIREMENTS.md` are legacy. Do not create, write, or read them; delete them when encountered. Their former contents live where the lifecycle already is: session resume state in beads (`br ready`, in-progress beads and their comments) and git (branch, log); completed-work evidence in bead close reasons and commits; requirements in beads.

### .gitignore

```
# ccu session artifacts (ephemeral)
.ccu/CAPTURES.md
.ccu/artifacts/
.ccu/brainstorm/
```

`DECISIONS.md` is not gitignored — it is committed so every session shares the journal.

## The epistemics rule

Anything read from `DECISIONS.md` or from old bead comments is a claim made at a point in time, with the knowledge available then — including claims that were mistakes. Before relying on or repeating such a claim, verify it against the code, beads, or git; if you cannot verify it, label it unverified. This generalizes the bead-comment rule for PR/merge state: point-in-time records are audit trail, never ground truth.

## The promote rule

A decision that meets the ADR gate in [[grill-with-docs]] — hard to reverse, surprising without context, the result of a real trade-off (see its `ADR-FORMAT.md`) — is written as `docs/adr/NNNN-slug.md`. The `DECISIONS.md` entry for it is then a single line linking the ADR. Only decisions below that gate get a full journal entry. The ADR is the maintained record; the journal line is the pointer.

## Decisions journal (`.ccu/DECISIONS.md`)

Append-only: each decision is a new `##` section at the end. Never rewrite or remove existing sections. One schema, used by every writer:

```markdown
## 2026-08-07 — Serialise api integration tests (t:auto, ts-core-8adk)

**Context:** 5s default timeout measured against scheduler queueing, not work.
**Decision:** `fileParallelism: false` + `testTimeout: 20_000` in apps/api.
**Why:** parallelism bought 1.46x wall clock at 4.4x per-test latency inflation.
**Alternatives:** `maxWorkers: 4` — fastest, rejected: keeps the failure class alive.
```

Header: `## YYYY-MM-DD — <title> (<source command or bead>)`. Body: the four bold-keyed lines, at most ~10 lines total. An above-gate decision replaces the body with one line: `Promoted: docs/adr/NNNN-slug.md`.

## Recipe checkpoint (`.ccu/CHECKPOINT.md`)

Owned by [[recipe]] alone: written after each step, read when a recipe starts (to offer resume after an interruption), and deleted when the recipe completes. A checkpoint that outlives its recipe reads as a phantom interruption — deletion on completion is part of the recipe, not optional cleanup.

## Artifacts HTML index (`.ccu/artifacts/<dir>/`)

Longer-form working docs — discovery, approach, execution plans, designs, epic summaries — live in per-feature subdirectories under `.ccu/artifacts/<dir>/`. These pile up as loose `.md` files that are tedious to read in a terminal.

Every `.ccu/artifacts/<dir>/` gets a browsable `index.html` viewer. Whenever a skill writes or updates any `.md` in one of these directories, regenerate the viewer as the last step:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/markdown-html-viewer/scripts/md2html.py" .ccu/artifacts/<dir>/
```

Pointing the script at the directory produces a single `index.html` with a document-switcher dropdown — one page that swaps between discovery / approach / execution-plan, each with its own TOC, Mermaid rendering, and callouts. `README.md` sorts first, the rest alphabetically.

- Fetch mode is the default and the right choice here — no `--inline`. The HTML `fetch()`es each `.md` at load, so the `.md` files stay the single live source.
- This is an intentional exception to the markdown-html-viewer skill's "ask how to build it" step: for automated `.ccu/artifacts` generation, always use directory + fetch without prompting. The ask only applies when a user directly invokes the viewer on their own docs.
- Regenerate, don't append — rerun the one command after each write; cheap and idempotent.
- Viewing — a fetch page can't be opened by double-click (`file://` blocks fetching siblings). Open with: `"${CLAUDE_PLUGIN_ROOT}/skills/markdown-html-viewer/scripts/open_in_dev_browser.sh" .ccu/artifacts/<dir>/index.html`. Mention this path when handing off artifacts.
- `index.html` lives inside `.ccu/artifacts/`, already gitignored.

## Session-start read set

Commands that build situational awareness at session start read, skipping what doesn't exist:

1. `CONTEXT.md` and a scan of `docs/adr/` — the curated current truth
2. `README.md`, `CLAUDE.md`/`AGENTS.md` — conventions
3. `git log --oneline -15` — recent direction
4. `br ready --json`, `bv`, in-progress beads and their comments — actionable and resumable work

Do not load `DECISIONS.md` at session start. Grep it when a specific "why" question arises, and apply the epistemics rule to whatever it returns.

## Initialization

When initializing `.ccu/` (typically via `t:init`):

1. Create `.ccu/` if it doesn't exist
2. Create `CAPTURES.md` if it doesn't exist
3. Ensure `.gitignore` includes `.ccu/CAPTURES.md`, `.ccu/artifacts/`, and `.ccu/brainstorm/`
4. Delete legacy files (`SESSION.md`, `HANDOFF.md`, `EVIDENCE.md`, `REQUIREMENTS.md`) if present

## Graceful Degradation

- No `.ccu/` directory — create it, or skip if the command is read-only
- No `DECISIONS.md` yet — create it on first write
- Never fail because a `.ccu/` file is missing — recreate what's needed and continue

## Rules

- `CAPTURES.md` is the fast lane — captures always land there first; triage promotes them into beads.
- `DECISIONS.md` is append-only and committed; every writer uses the one schema above.
- Knowledge that must stay true belongs in ADRs, docs, or beads — never in a `.ccu/` log.
