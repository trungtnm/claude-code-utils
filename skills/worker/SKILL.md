---
name: worker
description: Use when assigned beads to implement as part of an orchestrated epic. Defines the bead execution protocol for autonomous workers spawned by the orchestrator.
---

# Worker: Bead Execution Protocol

Autonomous protocol for workers implementing beads within an orchestrated epic.

**Announce at start:** "I'm using the worker skill to execute my assigned beads."

## Required Skills

Load these before starting work:

- `/skill coding-standards` - Code quality rules
- `/skill test-driven-development` - Write tests first, always

**If track needs isolation:** `/skill using-git-worktrees`

## Setup

```
1. Read {PROJECT_PATH}/AGENTS.md for tool preferences
2. Load required skills (above)
3. Note your assignment:
   - Agent name: {AGENT_NAME}
   - Track: {TRACK_NUMBER}
   - Beads (in order): {BEAD_LIST}
   - File scope: {FILE_SCOPE}
   - Epic thread: {EPIC_ID}
   - Track thread: track:{AGENT_NAME}:{EPIC_ID}
```

## Bead Execution Cycle

For EACH bead in your track:

### 1. Start Bead

```bash
# Register/update your identity
register_agent(name="{AGENT_NAME}", task_description="{BEAD_ID}")

# Read context from previous work
summarize_thread(thread_id="track:{AGENT_NAME}:{EPIC_ID}")

# Reserve your file scope
file_reservation_paths(paths=["{FILE_SCOPE}"], reason="{BEAD_ID}")

# Claim the bead
bd update {BEAD_ID} --status in_progress
```

### 2. Work on Bead

**Follow TDD strictly:**
1. Write failing test first (RED)
2. Implement minimal code to pass (GREEN)
3. Refactor while keeping tests green

**During work:**
- Use preferred tools from AGENTS.md
- Check inbox periodically: `fetch_inbox(agent_name="{AGENT_NAME}")`
- If blocked, report immediately (see Blockers below)

### 3. Verify Before Completion

Before closing, confirm:

```bash
# All tests pass
npm test  # or project-appropriate command

# No lint/type errors
npm run lint && npm run typecheck

# Build succeeds (if applicable)
npm run build
```

**Checklist from TDD:**
- [ ] All tests pass
- [ ] Output pristine (no errors, warnings)
- [ ] Edge cases covered

**If verification fails:** Fix issues, re-run verification. Do NOT close until green.

### 4. Complete Bead

```bash
# Close the bead
bd close {BEAD_ID} --reason "Summary of work done"

# Report to orchestrator
send_message(
  to=["{ORCHESTRATOR_NAME}"],
  thread_id="{EPIC_ID}",
  subject="[{BEAD_ID}] COMPLETE",
  body_md="Done: <summary>. Next: <next-bead-id>"
)

# Save context for your next bead
send_message(
  to=["{AGENT_NAME}"],
  thread_id="track:{AGENT_NAME}:{EPIC_ID}",
  subject="{BEAD_ID} Complete - Context for next",
  body_md="## Learnings\n- ...\n## Gotchas\n- ...\n## Next bead notes\n- ..."
)

# Release file reservations
release_file_reservations()
```

### 5. Next Bead

- Read your track thread for context from previous bead
- Loop back to "Start Bead" with next bead in track

## Track Completion

When all beads in your track are done:

```bash
send_message(
  to=["{ORCHESTRATOR_NAME}"],
  thread_id="{EPIC_ID}",
  subject="[Track {N}] COMPLETE",
  body_md="All beads done: <list>. Summary: ..."
)
```

Return a summary of all work completed.

## Handling Blockers

If blocked during work:

```bash
send_message(
  to=["{ORCHESTRATOR_NAME}"],
  thread_id="{EPIC_ID}",
  subject="[{BEAD_ID}] BLOCKED",
  body_md="Blocker: <description>. Need: <what you need>",
  importance="high"
)
```

Wait for orchestrator response before proceeding.

## Quick Reference

| Phase | Actions |
|-------|---------|
| Start | register_agent, summarize_thread, file_reservation_paths, bd update |
| Work | TDD cycle (RED→GREEN→REFACTOR), check inbox, report blockers |
| Verify | Run tests, lint, typecheck, build - all must pass |
| Complete | bd close, send_message (orchestrator + self), release_file_reservations |
| Next | Read track thread, loop to Start |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Skipping TDD | Always write failing test first |
| Closing without verification | Run tests, lint, build before `bd close` |
| Not reading track thread | Context from previous bead prevents re-discovery |
| Holding reservations too long | Release immediately after completing bead |
| Silent on blockers | Report blockers immediately with high importance |
| Not saving context | Future you needs learnings and gotchas |

## Red Flags

**Never:**
- Write production code without failing test first
- Close bead with failing tests or lint errors
- Skip reading track thread between beads
- Proceed when blocked without reporting
- Hold file reservations across multiple beads

**Always:**
- Follow TDD strictly
- Verify (tests, lint, build) before closing
- Check inbox periodically
- Report completion to orchestrator
- Save context to track thread
