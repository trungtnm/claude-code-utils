---
name: session-state
description: >-
  Manages the .ccu/ artifact directory for session continuity, evidence logging,
  decision tracking, and crash recovery. Use when initializing a project session,
  writing evidence after bead completion, recording architectural decisions, or
  preparing session handoffs. Triggers on .ccu, session state, evidence, checkpoint,
  handoff, decisions.
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

The `.ccu/` directory is the session memory layer for ccu-managed projects. It stores state that survives context resets and session boundaries — the bridge between "in-memory conversation" and "committed to git."

## Why This Exists

AI coding sessions die — terminals close, context fills up, connections drop. Without disk-resident state, the next session starts blind. `.ccu/` solves this by externalizing session memory to markdown files that any future session can read.

## Quick Reference

```bash
# Initialize (usually done by t:prime)
mkdir -p .ccu

# Check state
cat .ccu/SESSION.md          # Where am I?
cat .ccu/CHECKPOINT.md        # What was I doing when the session ended?
cat .ccu/HANDOFF.md           # What did the last session leave me?
cat .ccu/EVIDENCE.md          # What's been completed?
cat .ccu/DECISIONS.md         # What choices were made and why?
cat .ccu/CAPTURES.md          # What ideas are queued?
```

## Artifact Schema

Six files, split into ephemeral (gitignored) and persistent (committed):

### Ephemeral (gitignored)

| File | Purpose | Written By |
|------|---------|-----------|
| `SESSION.md` | Current phase, active beads, last action | `t:prime`, `t:auto`, `t:next` |
| `CHECKPOINT.md` | Resumable state for crash recovery | `t:auto`, orchestrator, planning |
| `CAPTURES.md` | Ad-hoc ideas queue | `t:capture` |
| `HANDOFF.md` | Session handoff (decisions, dead ends, next action) | `t:handoff` |

### Persistent (committed)

| File | Purpose | Written By |
|------|---------|-----------|
| `EVIDENCE.md` | Structured post-bead completion records | worker agent |
| `DECISIONS.md` | Append-only architectural decisions | `t:discuss`, planning, worker |

Read `references/SCHEMAS.md` for exact file formats.

## Initialization

When initializing `.ccu/` (typically via `t:prime`):

1. Create `.ccu/` directory
2. Create empty files: `SESSION.md`, `CHECKPOINT.md`, `CAPTURES.md`, `HANDOFF.md`, `EVIDENCE.md`, `DECISIONS.md`
3. Ensure the project's `.gitignore` includes:
   ```
   # ccu session artifacts (ephemeral)
   .ccu/SESSION.md
   .ccu/CHECKPOINT.md
   .ccu/CAPTURES.md
   .ccu/HANDOFF.md
   ```
4. Write initial SESSION.md with current phase

If `.ccu/` already exists, read existing state — don't overwrite.

## Cleanup

When ending a session (`t:done`):
- Clear SESSION.md and CHECKPOINT.md (write empty or delete)
- Clear HANDOFF.md (session is done, not handed off)
- Do NOT touch EVIDENCE.md or DECISIONS.md (these are permanent)
- Warn if CAPTURES.md has unchecked items

## Graceful Degradation

Every command and skill that reads `.ccu/` must check if it exists first. If not:
- Skip the read (don't error)
- Optionally create it (if the command's role includes initialization)
- Never fail because `.ccu/` is missing

## Rules

- **EVIDENCE.md and DECISIONS.md are append-only** — never remove or modify existing entries
- **One owner per write** — SESSION.md is written by the active command, not by workers
- **Ephemeral means ephemeral** — gitignored files can be deleted without data loss
- **Persistent means committed** — EVIDENCE.md and DECISIONS.md should be committed to git
