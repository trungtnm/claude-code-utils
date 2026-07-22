Recover session context after a crash, timeout, or new session start. Synthesize all available state into a briefing so you can resume immediately.

## Steps

1. **Gather state** — Read all available context sources (skip any that don't exist):

   **`.ccu/` files** (primary source for handoffs, decisions, and evidence):
   - `.ccu/HANDOFF.md` — what the last session explicitly left for you
   - `.ccu/DECISIONS.md` — recent architectural decisions and why
   - `.ccu/EVIDENCE.md` — what recently completed beads verified
   - `.ccu/CAPTURES.md` — pending ideas

   **Git and tools** (always available):
   - `git log --oneline -10` — recent commits
   - `git status` — uncommitted changes
   - `br ready --json 2>/dev/null` — actionable beads (if br available)
   - `br list --status in_progress --json 2>/dev/null` — claimed beads
   - `bv --robot-triage 2>/dev/null | jq '.quick_ref'` — project health (if bv available)
   - `cm context "<next action from handoff>" --json --limit 10 2>/dev/null` — procedural memory (if cm available)

1.5. **Reality-check for staleness** — Before trusting handoff content, verify it matches current reality:
   - Check the handoff note's date from its heading or file modification time
   - If the handoff is >24h old, treat it as **stale** and flag: "Handoff note is N days old — cross-referencing with git..."
   - Cross-reference handoff claims against git state:
     - If handoff says "working on bead X" but `br show X --json 2>/dev/null` shows it's closed → **override**: "Bead X was completed since last handoff"
     - If handoff says "next action: Y" but git log shows Y was done → **override**: "Recommended action already completed"
   - When handoff is stale, **prefer git log + br status as ground truth**
   - Note staleness prominently in the briefing
   - **Never repeat a bead comment's claim about PR/branch/merge state as fact.** Bead comments are point-in-time notes and go stale the moment the branch moves. If a comment says a PR is open/merged/closed, confirm against git/GitHub before reporting it — `gh pr view <n> --json state,mergedAt` (or `gh pr list --head <branch>`), `git branch -a`, `git log --oneline <branch>`. If `gh` is unavailable or you cannot confirm, say the state is **unverified** rather than asserting it.

2. **Synthesize briefing** — Present a structured recovery briefing:

   ```
   ## Recovery Briefing

   ### Last Session
   - Source: {.ccu/HANDOFF.md | git only}
   - Date: {from handoff heading or "unknown"}

   ### What Was Done
   - {list from .ccu/EVIDENCE.md, handoff, recent commits}

   ### Decisions Made (from last session)
   - {from handoff — decisions and WHY}

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
- **`.ccu/` first** — check `.ccu/HANDOFF.md` and the other `.ccu/` logs for what the last session left behind.
- **Graceful degradation** — if `.ccu/` doesn't exist, use `git log` + `git status` + `br` only. Always produce some briefing.
- **Be specific** — don't say "some work was done." Say exactly which beads, which commits, which files.
- **Handoff note is the primary source** — if it exists, it was deliberately written by the previous session.
- **Git/GitHub is ground truth for PR, branch, and merge state — not bead comments.** Comments record what was true when written; verify with `gh`/`git` before claiming a PR is open or merged, and mark it unverified if you can't confirm.
