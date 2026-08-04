---
description: Write a session handoff note to .ccu/HANDOFF.md so the next session can resume
argument-hint: [scope]
---

Write a session handoff note to `.ccu/HANDOFF.md` so the next session can resume where you left off. Use this when you're ending a session mid-work — not finished, just pausing.

**Scope: `$ARGUMENTS`**

If a scope is provided above, focus the handoff on that context. Otherwise, cover everything from this session.

## Steps

1. **Gather state** — Collect what the next session needs:
   - `git log --oneline -10` — recent commits from this session
   - `git diff --stat` — any uncommitted changes
   - `git status` — working tree state
   - `br list --status in_progress --json 2>/dev/null` — beads currently claimed
   - `.ccu/CAPTURES.md` — any untriaged ideas

2. **Record outcome in CM** — If `cm` is installed, record a partial outcome and feed back any dead ends as anti-patterns (skip silently if unavailable):
   ```bash
   cm outcome partial <rule-ids-used> --summary "Session paused: <reason>" 2>/dev/null
   ```
   If any approaches failed during this session, mark them so CM learns:
   ```bash
   cm mark <bullet-id> --harmful --reason "<what failed and why>" 2>/dev/null
   ```
   CM now carries "what was done" (via CASS session indexing) and "dead ends" (via anti-pattern learning). You don't need to duplicate that in the handoff note.

3. **Write handoff to `.ccu/HANDOFF.md`** — Overwrite it with the latest handoff:
   ```markdown
   # Session Handoff — {date} {time}

   ## Decisions Made
   - {key choice and WHY — the most valuable part for the next session}

   ## Next Action
   {ONE clear recommendation for what the next session should do first}

   ## Open Questions
   - {anything unresolved that needs human input}

   ## In-Progress Beads
   - {bead-id}: {current state, what's left}
   ```

4. **Record decisions** — If any architectural decisions were made this session that aren't yet recorded, append each as a new `##` section to `.ccu/DECISIONS.md` (create the file if it doesn't exist).

5. **Confirm** — Tell the user: "Handoff written to {location}. Next session can run `/t:recover` to pick up where you left off."

## Rules

- **Do NOT close beads** — this is a pause, not a finish. Beads stay in_progress.
- **Lean on CM for dead ends** — feed failed approaches to `cm mark --harmful` instead of writing them in the handoff. CM persists across all sessions; a handoff note only reaches the next one.
- **One next action** — don't give a menu. Pick the single best thing to do next.
- **Initialize .ccu/ if needed** — if it doesn't exist, create it before writing.

## What goes where

| Information | Where it lives | Why |
|-------------|---------------|-----|
| What was done (commits, files) | **CASS** — auto-indexed from session log | Searchable forever, no manual effort |
| Dead ends / failed approaches | **CM** — `cm mark --harmful` | Becomes anti-pattern, warns all future agents |
| Architectural decisions | **`.ccu/DECISIONS.md`** | Append-only log, committed to git |
| Next action + open questions | **`.ccu/HANDOFF.md`** | Carries forward intent for next session |
| In-progress bead state | **`.ccu/HANDOFF.md`** + **br** | br tracks status, handoff adds context |
