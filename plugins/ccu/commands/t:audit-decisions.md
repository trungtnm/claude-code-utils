---
description: Mine recent session history for undocumented decisions and record them in .ccu/DECISIONS.md
argument-hint: [timeframe, e.g. today or 7d]
---

Mine recent session history for undocumented decisions. Uses CASS to search actual conversation data for decision-making moments, then documents them in `.ccu/DECISIONS.md`.

## Steps

1. **Search sessions for decision signals** — Use CASS to find decision-making moments in recent sessions for this workspace:

   ```bash
   # Decision-making language patterns
   cass search "chose OR decided OR picked OR instead of OR over OR rather than" \
     --robot --workspace "$(pwd)" --days 7 --limit 20 --fields summary

   # Architecture/design deliberation
   cass search "because OR rationale OR tradeoff OR trade-off OR alternative" \
     --robot --workspace "$(pwd)" --days 7 --limit 20 --fields summary

   # Explicit choices
   cass search "will use OR going with OR let me use OR I'll implement" \
     --robot --workspace "$(pwd)" --days 7 --limit 20 --fields summary

   # Deliberate omissions
   cass search "skip OR defer OR not yet OR later OR out of scope OR won't" \
     --robot --workspace "$(pwd)" --days 7 --limit 20 --fields summary
   ```

   If CASS is not available, fall back to reading the current session's conversation context + `git log --oneline -20` + changed files.

2. **Expand context around hits** — For each CASS search hit that looks like a real decision (not just incidental word usage), expand context to understand the full deliberation:

   ```bash
   cass expand /path/to/session.jsonl -n {line} -C 5 --json
   ```

   Look for the pattern: *problem/need → alternatives considered → choice made → rationale*.

3. **Categorize decisions** — Group found decisions by type:
   - **Technology/library**: "used React Flow over D3 because..."
   - **Schema/data model**: "normalized into separate table because..."
   - **API/interface**: "REST over tRPC because..."
   - **Architecture pattern**: "feature-based directory structure because..."
   - **Naming convention**: "use-<resource> hooks because..."
   - **Trade-off/scope**: "skipped pagination — dataset is <100 items"
   - **Deliberate omission**: "no auth yet — waiting for auth bead"

4. **Cross-reference DECISIONS.md** — Read existing `.ccu/DECISIONS.md` (create if missing). Skip any decisions already documented. Only capture NEW undocumented ones.

5. **Write decisions** — Append each new decision to `.ccu/DECISIONS.md`:
   ```
   ---
   ## D{NNN} — {short title}
   - **date:** {YYYY-MM-DD}
   - **context:** {what prompted this decision}
   - **decision:** {what was decided}
   - **rationale:** {why this over alternatives}
   - **alternatives:** {what else was considered}
   - **source:** {session ID or "current session"}
   - **bead:** {bead-id if applicable}
   - **agent:** {agent name if in multi-agent session}
   ```

6. **Notify the team** — If Agent Mail is available and other agents are active, send a summary to the coordination thread:
   ```
   "Decision audit: documented N new decisions. Key choices:
   [list 2-3 most impactful]. See .ccu/DECISIONS.md for details."
   ```

7. **Report** — Summarize: how many sessions searched, how many decision moments found, how many new decisions documented.

## Arguments

- No args: audit last 7 days for this workspace
- `today`: audit today's sessions only
- `<session-id>`: audit a specific session
- `--all-projects`: audit across all workspaces

$ARGUMENTS

## Rules

- **Mine, don't fabricate** — Only document decisions found in actual session data or visible in code. Don't invent rationale.
- **CASS first, self-reflection second** — Always try CASS search before falling back to reviewing your own memory or code.
- **Capture the WHY** — The decision itself is visible in the code. The value of documentation is the *rationale* and *alternatives considered*.
- **Be specific** — "Used React Flow" is not a decision entry. "Used React Flow over D3 for the dependency graph because it handles interactive node positioning out of the box and integrates with React state" is.
- **Include deliberate omissions** — What was intentionally skipped is as important as what was built. "No pagination — dataset is <100 items" saves the next agent from building unnecessary pagination.
- **Number sequentially** — Continue from the last D{NNN} in DECISIONS.md. Don't restart numbering.
- **Deduplicate** — If the same decision appears in multiple sessions, document it once with the earliest source.
- **One entry per decision** — Don't bundle multiple decisions into one entry.
