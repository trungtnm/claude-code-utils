Recover session context after a crash, timeout, or new session start. Synthesize all available state into a briefing so you can resume immediately.

## Steps

1. **Gather state** — Read all available context sources (skip any that don't exist):
   - `.ccu/HANDOFF.md` — what the last session explicitly left for you
   - `.ccu/CHECKPOINT.md` — last known session state
   - `.ccu/SESSION.md` — what command was running
   - `.ccu/EVIDENCE.md` — what's been completed
   - `.ccu/CAPTURES.md` — pending ideas
   - `git log --oneline -10` — recent commits
   - `git status` — uncommitted changes
   - `br ready --json 2>/dev/null` — actionable beads (if br available)
   - `br list --status in_progress --json 2>/dev/null` — claimed beads
   - `bv --robot-triage 2>/dev/null | jq '.quick_ref'` — project health (if bv available)

2. **Synthesize briefing** — Present a structured recovery briefing:

   ```
   ## Recovery Briefing

   ### Last Session
   - Command: {from HANDOFF.md or CHECKPOINT.md}
   - Ended: {timestamp or "unknown"}

   ### What Was Done
   - {list from EVIDENCE.md, HANDOFF.md, recent commits}

   ### Decisions Made (from last session)
   - {from HANDOFF.md — decisions and WHY}

   ### Dead Ends (don't repeat these)
   - {from HANDOFF.md — approaches that were tried and abandoned}

   ### Current State
   - In-progress beads: {from br list}
   - Uncommitted changes: {from git status}
   - Untriaged captures: {count from CAPTURES.md}

   ### Recommended Next Action
   {ONE clear recommendation based on all available state}
   ```

3. **Offer continuation** — Ask:
   - "Resume where we left off" — pick up the recommended next action
   - "Show me the full state" — more detail before deciding
   - "Start fresh" — ignore prior state

## Rules

- **Read-only investigation** — do not modify any files or bead states. Just report.
- **Graceful degradation** — if `.ccu/` doesn't exist, use `git log` + `git status` + `br` only. If `br` isn't available either, use git alone. Always produce some briefing.
- **Be specific** — don't say "some work was done." Say exactly which beads, which commits, which files.
- **HANDOFF.md is the primary source** — if it exists, it was deliberately written by the previous session and should be the main source of truth. CHECKPOINT.md is the fallback for crashes.
