Write session state to `.ccu/HANDOFF.md` so the next session can resume where you left off. Use this when you're ending a session mid-work — not finished, just pausing.

**Scope: `$ARGUMENTS`**

If a scope is provided above, focus the handoff on that context. Otherwise, cover everything from this session.

## Steps

1. **Gather state** — Collect everything the next session needs to know:
   - `git log --oneline -10` — recent commits from this session
   - `git diff --stat` — any uncommitted changes
   - `git status` — working tree state
   - `br list --status in_progress --json 2>/dev/null` — beads currently claimed
   - `.ccu/EVIDENCE.md` — what was completed this session
   - `.ccu/CAPTURES.md` — any untriaged ideas

2. **Write HANDOFF.md** — Write to `.ccu/HANDOFF.md` following this structure:
   ```markdown
   # Session Handoff

   ## What Was Done
   - {bead-id}: {summary} (commit {hash})

   ## Decisions Made
   - {key choice and WHY — this is the most valuable part}

   ## Dead Ends (don't repeat these)
   - {approach tried and why it was abandoned}

   ## Next Action
   {ONE clear recommendation for what the next session should do first}

   ## Open Questions
   - {anything unresolved that needs human input}
   ```

3. **Update checkpoint** — Write `.ccu/CHECKPOINT.md` with current progress state.

4. **Commit evidence** — If `.ccu/EVIDENCE.md` or `.ccu/DECISIONS.md` have new entries, commit them:
   ```bash
   git add .ccu/EVIDENCE.md .ccu/DECISIONS.md 2>/dev/null
   git commit -m "docs: session handoff — evidence and decisions" 2>/dev/null
   ```

5. **Confirm** — Tell the user: "Handoff written. Next session can run `/t:recover` to pick up where you left off."

## Rules

- **Do NOT close beads** — this is a pause, not a finish. Beads stay in_progress.
- **Dead ends are gold** — the most valuable thing you can write is what NOT to try. The next session will waste hours rediscovering failures you already found.
- **One next action** — don't give a menu. Pick the single best thing to do next.
- **Initialize .ccu/ if needed** — if it doesn't exist, create it before writing.
