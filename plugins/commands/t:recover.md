Recover session context after a crash, timeout, or new session start. Synthesize all available state into a briefing so you can resume immediately.

## Steps

1. **Gather state** — Read all available context sources (skip any that don't exist):

   **Obsidian vault** (primary source for handoffs and decisions):
   - Read `.ccu/config` to get the vault path
   - If configured, find the most recent handoff note: `ls -t {vault}/ccu/sessions/*-handoff.md 2>/dev/null | head -1`
   - Read recent decision notes: `ls -t {vault}/ccu/decisions/*.md 2>/dev/null | head -5`
   - Read recent evidence notes: `ls -t {vault}/ccu/evidence/*.md 2>/dev/null | head -3`

   **Fallback .ccu/ files** (for projects without Obsidian):
   - `.ccu/HANDOFF.md` — what the last session explicitly left for you (legacy location)
   - `.ccu/CAPTURES.md` — pending ideas

   **Git and tools** (always available):
   - `git log --oneline -10` — recent commits
   - `git status` — uncommitted changes
   - `br ready --json 2>/dev/null` — actionable beads (if br available)
   - `br list --status in_progress --json 2>/dev/null` — claimed beads
   - `bv --robot-triage 2>/dev/null | jq '.quick_ref'` — project health (if bv available)
   - `cm context "<next action from handoff>" --json --limit 10 2>/dev/null` — procedural memory (if cm available)

1.5. **Reality-check for staleness** — Before trusting handoff content, verify it matches current reality:
   - Check the handoff note's date from frontmatter or file modification time
   - If the handoff is >24h old, treat it as **stale** and flag: "Handoff note is N days old — cross-referencing with git..."
   - Cross-reference handoff claims against git state:
     - If handoff says "working on bead X" but `br show X --json 2>/dev/null` shows it's closed → **override**: "Bead X was completed since last handoff"
     - If handoff says "next action: Y" but git log shows Y was done → **override**: "Recommended action already completed"
   - When handoff is stale, **prefer git log + br status as ground truth**
   - Note staleness prominently in the briefing

2. **Synthesize briefing** — Present a structured recovery briefing:

   ```
   ## Recovery Briefing

   ### Last Session
   - Source: {Obsidian handoff note | .ccu/HANDOFF.md | git only}
   - Date: {from handoff frontmatter or "unknown"}

   ### What Was Done
   - {list from evidence notes, handoff, recent commits}

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
- **Obsidian first, .ccu/ fallback** — check Obsidian vault for handoff notes first. Fall back to `.ccu/HANDOFF.md` only if Obsidian is not configured or has no notes.
- **Graceful degradation** — if neither Obsidian nor `.ccu/` exist, use `git log` + `git status` + `br` only. Always produce some briefing.
- **Be specific** — don't say "some work was done." Say exactly which beads, which commits, which files.
- **Handoff note is the primary source** — if it exists, it was deliberately written by the previous session.
