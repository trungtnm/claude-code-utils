Register with MCP Agent Mail and introduce yourself to the other agents. Be sure to check your agent mail and to promptly respond if needed to any messages; then proceed meticulously with your next assigned beads, working on the tasks systematically and meticulously and tracking your progress via beads and agent mail messages. Don't get stuck in "communication purgatory" where nothing is getting done; be proactive about starting tasks that need to be done, but inform your fellow agents via messages when you do so and mark beads appropriately. When you're not sure what to do next, use the bv tool mentioned in AGENTS.md, CLAUDE.md to prioritize the best beads to work on next; pick the next one that you can usefully work on and get started. Make sure to acknowledge all communication requests from other agents and that you are aware of all active agents and their names. Use /effort max.

## Steps

1. **Register and introduce** -- Use MCP Agent Mail to register yourself and introduce yourself to the other agents. List your capabilities and availability.

2. **Check inbox** -- Fetch and read all pending messages. Acknowledge any contact requests and respond to any messages that need replies.

3. **Assess work** -- Use `bv` (Beads Viewer) to survey the backlog and identify the highest-priority beads you can usefully work on.

4. **Pick and start** -- Claim the next ready bead, update its status, and notify fellow agents via agent mail that you are starting work on it.

5. **Execute** -- Work through the bead's requirements systematically and meticulously. Track progress with bead comments and status updates.

6. **Communicate** -- Keep fellow agents informed of progress, blockers, and completions via agent mail. Respond promptly to any incoming messages between work steps.

7. **Write checkpoint** -- After completing (or attempting) each bead, update `.ccu/CHECKPOINT.md` if `.ccu/` exists:
   - Record which beads were completed this session (with commit hashes)
   - Record current in-progress bead and its state
   - Record remaining beads in queue
   This enables crash recovery via `/t:recover`.

8. **Loop** -- When a bead is complete, close it, sync, and return to step 2. Repeat until no actionable work remains.

## Rules

- **Action over coordination** -- Do not spend more time messaging than working. If there is clearly work to do, start it and inform others, rather than waiting for permission.
- **Stay responsive** -- Check inbox between tasks. Acknowledge all contact requests and messages promptly.
- **Track everything** -- Every task you work on must have a bead. Update status and add comments as you go.
- **Use bv for prioritization** -- When uncertain what to do next, run bv to find the highest-value ready beads.
- **Use /effort max** -- Apply maximum effort to all work.