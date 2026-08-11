---
name: next
description: Analyze all available state and recommend the single best next action
---

Analyze all available state and recommend the single best next action.

## Steps

1. **Read all state** — Gather context from all sources (skip any that don't exist):
   - `.ccu/CAPTURES.md` — pending captures (count unchecked)
   - `git status` — uncommitted work
   - `git log --oneline -5` — recent commits
   - `br list --status in_progress --json 2>/dev/null` — claimed but unfinished beads, plus their comments (the resume trail)
   - `br ready --json 2>/dev/null` — actionable beads
   - `bv --robot-next 2>/dev/null` — bv's recommendation

2. **Apply priority rules** — Evaluate in this order (first match wins):
   1. **Uncommitted changes?** -> "Commit your work first" (suggest `/commit`)
   2. **In-progress bead unclaimed?** -> "Resume bead {ID}" (it was started but not finished — its comments and git say where it stopped)
   3. **Blocked beads you can unblock?** -> "Unblock {ID} by doing {action}"
   4. **Untriaged captures (>3)?** -> "Triage your captures" (suggest `/triage`)
   5. **Ready beads exist?** -> "Work on bead {ID}" (highest priority from `br ready` or `bv --robot-next`)
   6. **No beads but captures?** -> "Triage captures to create beads" (suggest `/triage`)
   7. **Nothing actionable?** -> "All clear. Start new work with `/discuss` or capture ideas with `/capture`."

3. **Present recommendation** — Show ONE clear recommendation:
   ```
   **Recommended:** {what to do}
   **Why:** {one sentence}
   **Command:** `{the exact command to run}`
   ```
   Optionally show 2-3 alternatives if the user wants something different.

## Rules

- **One recommendation** — pick the best action, don't present a menu
- **Provide the command** — don't make the user figure out what to type
- **Graceful degradation** — works with just `git status` if nothing else is available
