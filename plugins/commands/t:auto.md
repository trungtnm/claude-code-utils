Register with MCP Agent Mail and introduce yourself to the other agents. Be sure to check your agent mail and to promptly respond if needed to any messages; then proceed meticulously with your next assigned beads, working on the tasks systematically and meticulously and tracking your progress via beads and agent mail messages. Don't get stuck in "communication purgatory" where nothing is getting done; be proactive about starting tasks that need to be done, but inform your fellow agents via messages when you do so and mark beads appropriately. When you're not sure what to do next, use the bv tool mentioned in AGENTS.md, CLAUDE.md to prioritize the best beads to work on next; pick the next one that you can usefully work on and get started. Make sure to acknowledge all communication requests from other agents and that you are aware of all active agents and their names. Use /effort max.

## Steps

0. **Load project context** -- Before doing anything else, build situational awareness by reading (skip any that don't exist):
   - `CLAUDE.md` or `AGENTS.md` — project conventions, rules, architecture, coding patterns
   - `README.md` — what the project is, tech stack, how it works
   - `.ccu/config` — check for `obsidian_vault:` path; if configured, read recent decision and evidence notes from `{vault}/ccu/decisions/` and `{vault}/ccu/evidence/`
   - Obsidian `{vault}/ccu/sessions/` — most recent handoff note (if Obsidian configured)
   - `.ccu/CAPTURES.md` — pending ideas
   - `git log --oneline -15` — recent activity and direction
   This context shapes how you implement every bead. Without it, you risk writing code that violates project conventions or duplicates existing work.

0.5. **Load procedural memory** -- Query CM for relevant rules and anti-patterns (skip if `cm` is not installed):
   ```bash
   cm context "general development" --json --limit 10 2>/dev/null
   ```
   If CM returns results, keep the `relevantBullets` and `antiPatterns` in mind throughout the session. Reference rule IDs (e.g., "Following b-8f3a2c...") when a rule influences your decisions. This is how the team's accumulated knowledge flows into your work.

1. **Register and discover peers** -- Follow this sequence to register and establish contacts with all other agents:

   a. **Register**: Call `macro_start_session` with `human_key` = absolute path to this repo, `program` = "claude-code", `model` = your model name. Save the returned `agent.name` — this is YOUR identity for the session.

   b. **Open contact policy**: Call `set_contact_policy` with your agent name and `policy` = "open". This ensures any peer's contact request is auto-accepted without your intervention.

   c. **Discover peers**: The Agent Mail archive stores agent directories on disk. Run:
      ```bash
      ls ~/.mcp_agent_mail_git_mailbox_repo/projects/$(echo "$PWD" | tr '/' '-' | sed 's/^-//' | tr '[:upper:]' '[:lower:]')/agents/ 2>/dev/null
      ```
      This returns one directory name per registered agent. Filter out your own name to get the peer list.

   d. **Handshake with each peer**: For every discovered peer, call `macro_contact_handshake` with `requester` = your name, `target` = peer name, `auto_accept` = true. This establishes bidirectional contact in one call.

   e. **Introduce yourself**: Send a message to thread `"coordination"` addressed to all discovered peers. Include: your agent name, which bead you plan to work on (from step 3), and your capabilities.

   f. **Second discovery pass**: After ~5 seconds, repeat steps (c) and (d) to catch agents that registered after your first pass. This handles the race condition where agents start at slightly different times.

2. **Check inbox** -- Fetch and read all pending messages with `include_bodies` = true. For any pending contact requests, call `respond_contact` with `accept` = true. Acknowledge and respond to any messages that need replies. If you discover new agent names in messages that you haven't handshaked with yet, repeat step 1d for them.

3. **Assess work** -- Use `bv` (Beads Viewer) to survey the backlog and identify the highest-priority beads you can usefully work on. If no beads exist, check `.ccu/CAPTURES.md` for untriaged items and process them.

4. **Pick and start** -- Pick the next bead using `br ready --json 2>/dev/null` (which returns only unblocked beads with all dependencies met). Then claim it with `br update <id> --status in_progress`.

   **CRITICAL: Always verify bead state before acting.** Beads can change state at any time because other agents are working concurrently. Before starting work on a bead:
   - Run `br show <id> --json 2>/dev/null` to confirm it's still open/ready (not already `done` or `in_progress` by another agent)
   - If the bead is already closed or claimed by another agent, **skip it** and pick the next ready bead
   - If `br update` fails with "cannot claim", do NOT proceed — pick a different bead

   **Respect the dependency graph.** If `br` returns an error like `"cannot claim blocked issue"`, that bead has unmet dependencies. Do NOT work on it or "prepare code ahead." Instead:
   - Run `br show <id> --json 2>/dev/null` to see which bead is blocking it
   - Either work on the blocker first, or pick a different ready bead
   - If ALL beads are blocked by other agents' in-progress work, **poll and wait** (see step 9)

   **Reserve files before editing.** After claiming the bead, determine which files you will modify (from the bead description, requirements, or codebase investigation). Then reserve them:
   ```
   file_reservation_paths(paths=["src/foo.ts", "src/bar.ts", ...], reason="{BEAD_ID}")
   ```
   If the reservation fails (another agent already holds those files), **do not proceed** — pick a different ready bead instead. File reservations are the mechanical safety net that prevents two agents from editing the same file simultaneously.

   Notify fellow agents via agent mail that you are starting work on the claimed bead.

5. **Execute** -- Work through the bead's requirements systematically and meticulously. Track progress with bead comments and status updates. If you discover you need to edit additional files not in your original reservation, reserve them first with `file_reservation_paths` before touching them.

6. **Communicate** -- Keep fellow agents informed of progress, blockers, and completions via agent mail. Respond promptly to any incoming messages between work steps.

7. **Capture decisions** -- If you made technology, schema, API, or architecture choices during this bead, write each as an individual note to the Obsidian vault (if configured via `.ccu/config`):
   - Write to `{vault}/ccu/decisions/{ID}-{slugified-title}.md` with YAML frontmatter (id, title, date, tags, project)
   - If Obsidian is not configured, append to `.ccu/DECISIONS.md` as fallback
   - Don't defer all decision documentation to `/t:audit-decisions` — capture the obvious ones inline while the context is fresh.

   Also write evidence for completed beads to `{vault}/ccu/evidence/{bead-id}-{slugified-title}.md` with commit hash, files changed, and verification results.

8. **Record outcome** -- After completing a bead, record the outcome so CM can learn from it (skip if `cm` is not installed):
   ```bash
   cm outcome success <rule-ids-that-helped> 2>/dev/null   # or 'failure' if bead was blocked
   ```
   If any CM rules were particularly helpful or harmful during the bead, leave inline feedback:
   ```bash
   cm mark <bullet-id> --helpful 2>/dev/null
   cm mark <bullet-id> --harmful --reason "<why>" 2>/dev/null
   ```

9. **Loop** -- When a bead is complete:
   a. Re-check bead state with `br show <id> --json 2>/dev/null` — if another agent already closed it, skip closing (don't treat "already closed" as an error, just move on)
   b. If still open, close it with `br close <id> --reason "..."`
   c. Release file reservations (`release_file_reservations()`)
   d. Sync beads (`br sync --flush-only 2>/dev/null`)
   e. Return to step 2. Repeat until no actionable work remains.

   **When all remaining beads are blocked** (waiting on other agents), do NOT ask the user whether to poll or wait. Instead, automatically:
   a. Check inbox for messages (other agents may have completed blockers)
   b. Run `br ready --json 2>/dev/null` to check if any beads became unblocked
   c. If still all blocked, wait ~30 seconds and repeat from (a)
   d. Continue this poll loop until a bead becomes ready, then immediately claim and start it
   e. **Only stop the loop when ALL beads are `done`** (no open, in_progress, or blocked beads remain)

   Never ask "Want me to keep polling?" or "Should I wait?" — you are autonomous. Just do it.

## Rules

- **Fully autonomous** -- Never ask the user for permission to continue, poll, or proceed to the next bead. You decide what to work on and when. The only reason to stop is when all beads are done or you hit a genuine ambiguity that requires human input (not "should I keep going?").
- **Action over coordination** -- Do not spend more time messaging than working. If there is clearly work to do, start it and inform others, rather than waiting for permission.
- **Stay responsive** -- Check inbox between tasks. Acknowledge all contact requests and messages promptly.
- **Track everything** -- Every task you work on must have a bead. Update status and add comments as you go.
- **Use bv for prioritization** -- When uncertain what to do next, run bv to find the highest-value ready beads.
- **Never bypass blocked beads** -- If a bead is blocked, it is blocked for a reason (unmet dependency). Working "ahead" on blocked beads creates merge conflicts, wasted effort, and dependency violations. Work on the blocker or pick something else.
- **Always reserve files before editing** -- Call `file_reservation_paths` after claiming a bead with the files you plan to edit. If reservation fails (another agent holds those files), pick a different bead. Reserve additional files as needed during execution. Release with `release_file_reservations()` when the bead is done. This is the mechanical safety net that prevents two agents from clobbering each other's work.
- **Use /effort max** -- Apply maximum effort to all work.