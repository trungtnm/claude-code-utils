Register with MCP Agent Mail and introduce yourself to the other agents. Be sure to check your agent mail and to promptly respond if needed to any messages; then proceed meticulously with your next assigned beads, working on the tasks systematically and meticulously and tracking your progress via beads and agent mail messages. Don't get stuck in "communication purgatory" where nothing is getting done; be proactive about starting tasks that need to be done, but inform your fellow agents via messages when you do so and mark beads appropriately. When you're not sure what to do next, use the bv tool mentioned in AGENTS.md, CLAUDE.md to prioritize the best beads to work on next; pick the next one that you can usefully work on and get started. Make sure to acknowledge all communication requests from other agents and that you are aware of all active agents and their names. Use /effort max.

**Mode determination** — after Step 0 (you need the mail project key first), decide **solo** vs **multi-agent**:
- If `$ARGUMENTS` contains `--solo` or `solo` → **solo** (explicit).
- **Peer check first (do NOT skip):** are other agents already active on this repo? A concurrent Orchestrator epic or another `/t:auto` may be holding file reservations you must respect. Check via the Agent Mail API against the literal repo root (see Step 1c). **If any peer is active → run multi-agent** regardless of bead count — going solo would skip reservations and let you clobber their work.
- Otherwise, count ready beads: `br ready --json 2>/dev/null | jq 'length'`. If less than 5 **and no peers are active** → **solo** (not enough parallel work to justify coordination overhead).
- Otherwise → **multi-agent**.

Report the chosen mode to the user in one line (e.g., "Running in **solo** mode: 3 ready beads, no active peers.") before proceeding.

In **solo mode**, skip every step and sub-step marked **[Skip in solo mode]** below: no peer handshakes, inbox loop, messaging, or file reservations. You still use beads, `bv`, and `cm`. The **one exception** is the mode-determination peer check itself: it needs a single Agent Mail registration + `list_contacts` to confirm no peers are active. That check is what *lets* you choose solo safely — run it, and if it comes back empty (and beads < 5), proceed solo and make no further `mcp__mcp-agent-mail__*` calls.

## Steps

0. **Resolve the mail project key** -- You work directly in the user's tree, on the current branch. The only coordination anchor you need is the Agent Mail project key — the **literal repo root**:

   ```bash
   git rev-parse --show-toplevel    # e.g. /Users/you/code/myrepo — this is the Agent Mail project key
   git rev-parse --short HEAD       # note the baseline commit before you start
   git status --porcelain           # if the tree is dirty, tell the user before you begin
   ```

   **Two rules that make coordination safe, and break everything if ignored:**
   - **Agent Mail is keyed to the repo root** — and MCP calls don't expand shell vars, so paste the *literal* path (echo it first). Registering under a literal `$VAR` drops you into a private mailbox where you see no other agent's reservations and silently clobber their work.
   - **With no worktree, file reservations are the ONLY thing between you and another agent editing the same file.** In multi-agent mode, never touch a file you haven't reserved.

0.1. **Load project context** -- Before doing anything else, build situational awareness by reading (skip any that don't exist):
   - `CLAUDE.md` or `AGENTS.md` — project conventions, rules, architecture, coding patterns
   - `README.md` — what the project is, tech stack, how it works
   - `.ccu/DECISIONS.md` and `.ccu/EVIDENCE.md` — recent architectural decisions and completed-bead evidence
   - `.ccu/HANDOFF.md` — most recent handoff, if the last session paused mid-work
   - `.ccu/CAPTURES.md` — pending ideas
   - `git log --oneline -15` — recent activity and direction
   This context shapes how you implement every bead. Without it, you risk writing code that violates project conventions or duplicates existing work.

0.2. **Load procedural memory** -- Query CM for relevant rules and anti-patterns (skip if `cm` is not installed):
   ```bash
   cm context "general development" --json --limit 10 2>/dev/null
   ```
   If CM returns results, keep the `relevantBullets` and `antiPatterns` in mind throughout the session. Reference rule IDs (e.g., "Following b-8f3a2c...") when a rule influences your decisions. This is how the team's accumulated knowledge flows into your work.

1. **Register and discover peers** **[Skip in solo mode]** -- Follow this sequence to register and establish contacts with all other agents:

   a. **Register**: First `git rev-parse --show-toplevel` to read the literal repo-root path (MCP calls are not shell — `$VAR` will NOT expand inside them). Call `macro_start_session` with `human_key` = that **literal** path, `program` = "claude-code", `model` = your model name. Save the returned `agent.name` — this is YOUR identity for the session.

   b. **Open contact policy**: Call `set_contact_policy` with your agent name and `policy` = "open". This ensures any peer's contact request is auto-accepted without your intervention.

   c. **Discover peers via the API** (not the filesystem): call `list_contacts` (with your registered identity) to enumerate agents active on this project key. Filter out your own name to get the peer list. Peers may include workers from a running Orchestrator epic — their file reservations are live and you must respect them. (Use the API, never hand-derive the server's on-disk directory name — any slug mismatch would silently report "no peers" and leave you blind.)

   d. **Handshake with each peer**: For every discovered peer, call `macro_contact_handshake` with `requester` = your name, `target` = peer name, `auto_accept` = true. This establishes bidirectional contact in one call.

   e. **Introduce yourself**: Send a message to thread `"coordination"` addressed to all discovered peers. Include: your agent name, which bead you plan to work on (from step 3), and your capabilities.

   f. **Second discovery pass**: After ~5 seconds, repeat steps (c) and (d) to catch agents that registered after your first pass. This handles the race condition where agents start at slightly different times.

2. **Check inbox** **[Skip in solo mode]** -- Fetch and read all pending messages with `include_bodies` = true. For any pending contact requests, call `respond_contact` with `accept` = true. Acknowledge and respond to any messages that need replies. If you discover new agent names in messages that you haven't handshaked with yet, repeat step 1d for them.

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

   **Reserve files before editing.** **[Skip in solo mode]** After claiming the bead, determine which files you will modify (from the bead description, requirements, or codebase investigation). Then reserve them:
   ```
   file_reservation_paths(paths=["src/foo.ts", "src/bar.ts", ...], reason="{BEAD_ID}")
   ```
   If the reservation fails (another agent already holds those files), **do not proceed** — pick a different ready bead instead. With no worktree isolation, file reservations are the only mechanical safety net that prevents two agents from editing the same file simultaneously.

   **[Skip in solo mode]** Notify fellow agents via agent mail that you are starting work on the claimed bead.

5. **Execute** -- Work through the bead's requirements systematically and meticulously. Track progress with bead comments and status updates. **[Multi-agent mode]** If you discover you need to edit additional files not in your original reservation, reserve them first with `file_reservation_paths` before touching them.

   **Commit discipline (multi-agent mode):** other agents may be staging and committing in this same tree concurrently. NEVER `git add -A` or `git add .` — stage your named files only, and commit with a pathspec so nothing else is swept into your commit:
   ```bash
   git add <your files> && git commit -m "<type>(<scope>): <description> [<bead-id>]" -- <your files>
   ```

6. **Communicate** **[Skip in solo mode]** -- Keep fellow agents informed of progress, blockers, and completions via agent mail. Respond promptly to any incoming messages between work steps.

7. **Capture decisions** -- If you made technology, schema, API, or architecture choices during this bead, append each as a new `##` section to `.ccu/DECISIONS.md` (create the file if it doesn't exist):
   - Include date, context, decision, rationale, and alternatives considered.
   - Don't defer all decision documentation to `/t:audit-decisions` — capture the obvious ones inline while the context is fresh.

   Also append evidence for completed beads to `.ccu/EVIDENCE.md` (one `##` section per bead) with commit hash, files changed, and verification results.

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
   c. Release file reservations (`release_file_reservations()`) **[Skip in solo mode]**
   d. Sync beads (`br sync --flush-only 2>/dev/null`)
   e. Return to step 2. Repeat until no actionable work remains.

   **When all remaining beads are blocked** (waiting on other agents), do NOT ask the user whether to poll or wait. **In solo mode, skip this poll loop entirely** — there are no other agents to unblock anything. If every remaining bead is blocked by an unmet dependency, stop and report the blocked graph to the user. Otherwise (multi-agent mode), automatically:
   a. Check inbox for messages (other agents may have completed blockers)
   b. Run `br ready --json 2>/dev/null` to check if any beads became unblocked
   c. If still all blocked, wait ~30 seconds and repeat from (a)
   d. Continue this poll loop until a bead becomes ready, then immediately claim and start it
   e. **Only stop the loop when ALL beads are `done`** (no open, in_progress, or blocked beads remain)

   **Liveness guard (do NOT poll forever on a dead peer).** A bead stuck `in_progress`, held by an
   agent that has crashed, will never flip — and nothing times out on its own. Track how long you
   have been blocked with no forward motion (no new mail, no new commits, no `br ready` change).
   After a bounded budget (~10 minutes, or ~20 idle poll cycles), **stop and escalate to the user**:
   report which bead is stuck, who holds it, and that the holder shows no recent activity — offer
   to force-release its reservations (`force_release_file_reservation`) and reclaim the bead, or
   wait longer. This single case is the allowed exception to "never ask": you are not asking
   permission to work, you are reporting a stall you cannot resolve autonomously.

   Otherwise never ask "Want me to keep polling?" or "Should I wait?" — you are autonomous. Just do it.

10. **Wrap up the session** -- When no actionable work remains:

    a. Release every file reservation you still hold: `release_file_reservations()` **[Skip in solo mode]** — a reservation you never release blocks the next session.
    b. **Commit bead state**:
       ```bash
       br sync --flush-only            # export shared DB → .beads/issues.jsonl (do NOT hide errors here — a failed flush must not be committed silently)
       git add .beads/ && git commit -m "chore(beads): sync session state" -- .beads/   # skip if nothing changed
       ```
    c. Confirm nothing you worked on is left uncommitted: `git status --porcelain` — every completed bead should already have its own commit from step 5.
    d. Report the session summary to the user: beads completed (per-bead ✓/✗ with commit hashes), beads left open/blocked, and the commit range (`<baseline>..HEAD`). Your commits are already on the user's current branch — whether to push is their call; do not push without being asked.

## Rules

- **Fully autonomous** -- Never ask the user for permission to continue, poll, or proceed to the next bead. You decide what to work on and when. The only reason to stop is when all beads are done or you hit a genuine ambiguity that requires human input (not "should I keep going?").
- **Action over coordination** -- Do not spend more time messaging than working. If there is clearly work to do, start it and inform others, rather than waiting for permission.
- **Stay responsive** -- Check inbox between tasks. Acknowledge all contact requests and messages promptly.
- **Track everything** -- Every task you work on must have a bead. Update status and add comments as you go.
- **Use bv for prioritization** -- When uncertain what to do next, run bv to find the highest-value ready beads.
- **Never bypass blocked beads** -- If a bead is blocked, it is blocked for a reason (unmet dependency). Working "ahead" on blocked beads creates conflicts, wasted effort, and dependency violations. Work on the blocker or pick something else.
- **Always reserve files before editing** -- Call `file_reservation_paths` after claiming a bead with the files you plan to edit. If reservation fails (another agent holds those files), pick a different bead. Reserve additional files as needed during execution. Release with `release_file_reservations()` when the bead is done. With no worktree isolation, this is the ONLY mechanical safety net that prevents two agents from clobbering each other's work.
- **Coordinate on the repo root** -- Every Agent Mail call uses the **literal** repo-root path (`git rev-parse --show-toplevel`, echoed — never a raw `$VAR`). Mail keyed to any other path sees no peers and holds no useful locks.
- **Commit per bead, named paths only** -- One commit per bead with the bead id in the message; stage named files and commit with a pathspec (never `git add -A`) so a concurrent agent's staged files are never swept into your commit.
- **Use /effort max** -- Apply maximum effort to all work.
