---
name: session-state
description: >-
  Manages the .ccu/ staging directory and Obsidian vault integration for session
  continuity, evidence logging, decision tracking, and crash recovery. Use when
  initializing a project session, writing evidence after bead completion, recording
  architectural decisions, or preparing session handoffs. Triggers on .ccu, session
  state, evidence, checkpoint, handoff, decisions.
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

Session state uses a two-layer architecture:

1. **`.ccu/` (staging layer)** — Fast, local, ephemeral. Quick-write buffer for captures and prime cache. Minimal footprint.
2. **Obsidian vault (persistence layer)** — Browsable, linkable, searchable. Decisions, evidence, handoffs, and session summaries live here as individual notes with frontmatter.

## Configuration

The Obsidian vault path is stored in `.ccu/config`:

```
obsidian_vault: ~/Obsidian
```

When reading this config:
1. Read `.ccu/config` and extract the `obsidian_vault:` value
2. Expand `~` to the user's home directory
3. The ccu subfolder is at `{vault}/ccu/` with subdirectories: `captures/`, `decisions/`, `evidence/`, `sessions/`

If `.ccu/config` does not exist or has no `obsidian_vault:` entry, **skip all Obsidian writes silently**. The .ccu/ staging layer still works standalone.

## .ccu/ Staging Layer

Minimal footprint — only two active files:

| File | Purpose | Written By |
|------|---------|-----------|
| `CAPTURES.md` | Ad-hoc ideas queue (fast-write buffer) | `t:capture` |
| `PRIME-CACHE.md` | Cached prime synthesis | `t:prime` |
| `config` | Vault path and settings | User/setup |

All other `.ccu/` files (`SESSION.md`, `CHECKPOINT.md`, `HANDOFF.md`) are deprecated and should not be created or written to. If they exist from a prior session, they can be ignored or deleted.

### .gitignore

```
# ccu session artifacts (ephemeral)
.ccu/CAPTURES.md
.ccu/PRIME-CACHE.md
```

Note: `.ccu/config` is NOT gitignored — it should be committed so all sessions share the same vault path.

## Obsidian Persistence Layer

### Folder Structure

```
~/Obsidian/ccu/
├── captures/        # Triaged captures as individual notes
├── decisions/       # One note per architectural decision
├── evidence/        # One note per completed bead
└── sessions/        # Handoff and session summary notes
```

### Writing to Obsidian

When a command needs to persist data to Obsidian, follow this pattern:

1. Read `.ccu/config` to get the vault path
2. If not configured, skip silently
3. Write a markdown file with YAML frontmatter to the appropriate subfolder
4. Use slugified filenames: `{ID}-{short-title}.md` (e.g., `D001-keep-t-command-prefix.md`)

### Frontmatter Convention

All Obsidian notes use YAML frontmatter for Dataview queryability:

```yaml
---
id: {identifier}
title: {human-readable title}
date: {YYYY-MM-DD}
tags: [{category}, {subcategory}]
project: {project name}
bead: {bead-id, if applicable}
---
```

### Decision Notes (`decisions/`)

One file per decision. Filename: `{ID}-{slugified-title}.md`

```markdown
---
id: D001
title: "Keep t: command prefix"
date: 2026-03-19
tags: [decision, architecture]
project: claude-code-utils
---

# D001 — {title}

**Date:** {YYYY-MM-DD}
**Context:** {what prompted this}
**Decision:** {what was decided}
**Rationale:** {why}
**Alternatives:** {what else was considered}
```

### Evidence Notes (`evidence/`)

One file per completed bead. Filename: `{bead-id}-{slugified-title}.md`

```markdown
---
id: {bead-id}
title: {bead title}
date: {completion date}
tags: [evidence, {type}]
project: {project name}
commit: {hash}
---

# {bead-id} — {title}

**Commit:** {hash}
**Files changed:** {list}
**Lines:** +{added} / -{removed}
**Verification:**
- tests: {result}
- lint: {result}
- typecheck: {result}
**Completed:** {ISO timestamp}
**Actor:** {agent name or "user"}
```

### Session Notes (`sessions/`)

One file per handoff. Filename: `{YYYY-MM-DD}-{HH-MM}-handoff.md`

```markdown
---
title: "Session handoff"
date: {YYYY-MM-DD}
tags: [session, handoff]
project: {project name}
---

# Session Handoff — {date}

## Decisions Made
- {decision and why}

## Next Action
{ONE clear recommendation}

## Open Questions
- {unresolved items}

## In-Progress Beads
- {bead-id} — {title}: {state}
```

## Initialization

When initializing `.ccu/` (typically via `t:prime`):

1. Create `.ccu/` directory if it doesn't exist
2. Create `CAPTURES.md` if it doesn't exist
3. Ensure `.gitignore` includes `.ccu/CAPTURES.md` and `.ccu/PRIME-CACHE.md`
4. If `.ccu/config` exists, verify the Obsidian vault path is accessible. Create `{vault}/ccu/` subdirectories if missing.

Do NOT create SESSION.md, CHECKPOINT.md, or HANDOFF.md — these are deprecated.

## Cleanup

When ending a session (`t:done`):
- Warn if CAPTURES.md has unchecked items
- Do NOT clear or delete any .ccu/ files (captures and cache persist across sessions)

## Graceful Degradation

- **No `.ccu/` directory** — create it, or skip if the command is read-only
- **No `.ccu/config`** — skip all Obsidian writes, use .ccu/ staging only
- **Obsidian vault path doesn't exist** — warn and skip Obsidian writes
- **Never fail** because Obsidian is not configured — it's an enhancement, not a requirement

## Rules

- **CAPTURES.md is the fast lane** — captures always go to .ccu/CAPTURES.md first (speed matters). During triage, important items flow to Obsidian.
- **Obsidian notes are append-only** — never remove or modify existing decision/evidence notes
- **Frontmatter is mandatory** — every Obsidian note needs YAML frontmatter for Dataview queries
- **Slugify filenames** — lowercase, hyphens, no spaces: `D001-keep-t-command-prefix.md`
- **Config is committed** — `.ccu/config` goes into git so all sessions share settings
