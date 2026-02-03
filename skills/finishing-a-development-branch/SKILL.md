---
name: finishing-a-development-branch
description: Use when implementation is complete, all tests pass, and you need to decide how to integrate the work - guides completion of development work by presenting structured options for merge, PR, or cleanup
---

# Finishing a Development Branch

## Overview

Guide completion of development work by closing beads, notifying via Agent Mail, and handling git workflow.

**Core principle:** Close beads → Release reservations → Notify → Verify tests → Present options → Execute → Clean up.

**Announce at start:** "I'm using the finishing-a-development-branch skill to complete this work."

## The Process

### Step 1: Close YOUR Beads and Release Reservations

**If working on beads (check for `.beads/` directory):**

Close only the specific beads YOU were assigned (from your track assignment):
```bash
# Close YOUR assigned beads - use the specific IDs from your track
bd close <your-bead-id> --reason "Completed: <summary of work>"
```

**WARNING:** Do NOT run `bd list --status in_progress` and close everything - that includes beads other agents are actively working on!

**Release file reservations (if using Agent Mail):**
```python
release_file_reservations(
  project_key="<absolute-project-path>",
  agent_name="<YourAgentName>"
)
```

### Step 2: Notify Orchestrator (If Part of Epic)

**If working as part of an orchestrated epic:**

```python
# Report completion to orchestrator
send_message(
  project_key="<path>",
  sender_name="<YourAgentName>",
  to=["<OrchestratorName>"],
  thread_id="<epic-id>",
  subject="[Track N] COMPLETE",
  body_md="""
## Track Complete

### Beads Completed
- <bead-1>: <summary>
- <bead-2>: <summary>

### Deliverables
- <what was built>

### Learnings
- <key insights for future reference>
"""
)
```

**Save context for future agents (track thread):**
```python
send_message(
  project_key="<path>",
  sender_name="<YourAgentName>",
  to=["<YourAgentName>"],  # Self-message for track thread
  thread_id="track:<YourAgentName>:<epic-id>",
  subject="Track Complete - Final Context",
  body_md="## Learnings\n- ...\n## Gotchas\n- ...\n## Notes for future\n- ..."
)
```

### Step 3: Verify Tests

**Before presenting git options, verify tests pass:**

```bash
# Run project's test suite
npm test / cargo test / pytest / go test ./...
```

**If tests fail:**
```
Tests failing (<N> failures). Must fix before completing:

[Show failures]

Cannot proceed with merge/PR until tests pass.
```

Stop. Don't proceed to Step 4.

**If tests pass:** Continue to Step 4.

### Step 4: Determine Base Branch

```bash
# Try common base branches
git merge-base HEAD main 2>/dev/null || git merge-base HEAD master 2>/dev/null
```

Or ask: "This branch split from main - is that correct?"

### Step 5: Present Options

Present exactly these 4 options:

```
Implementation complete. What would you like to do?

1. Merge back to <base-branch> locally
2. Push and create a Pull Request
3. Keep the branch as-is (I'll handle it later)
4. Discard this work

Which option?
```

**Don't add explanation** - keep options concise.

### Step 6: Execute Choice

#### Option 1: Merge Locally

```bash
git checkout <base-branch>
git pull
git merge <feature-branch>
<test command>  # Verify tests on merged result
git branch -d <feature-branch>
```

Then: Cleanup worktree (Step 7)

#### Option 2: Push and Create PR

```bash
git push -u origin <feature-branch>

gh pr create --title "<title>" --body "$(cat <<'EOF'
## Summary
<2-3 bullets of what changed>

## Beads Completed
- <bead-id>: <title>

## Test Plan
- [ ] <verification steps>
EOF
)"
```

Then: Cleanup worktree (Step 7)

#### Option 3: Keep As-Is

Report: "Keeping branch <name>. Worktree preserved at <path>."

**Don't cleanup worktree.**

#### Option 4: Discard

**Confirm first:**
```
This will permanently delete:
- Branch <name>
- All commits: <commit-list>
- Worktree at <path>

Type 'discard' to confirm.
```

Wait for exact confirmation. If confirmed:
```bash
git checkout <base-branch>
git branch -D <feature-branch>
```

Then: Cleanup worktree (Step 7)

### Step 7: Cleanup Worktree

**For Options 1, 2, 4:**

```bash
git worktree list | grep $(git branch --show-current)
# If in worktree:
git worktree remove <worktree-path>
```

**For Option 3:** Keep worktree.

## Quick Reference

| Step | Action | Tools |
|------|--------|-------|
| 1 | Close beads + release reservations | `bd close`, `release_file_reservations()` |
| 2 | Notify orchestrator | `send_message()` to epic thread |
| 3 | Verify tests | Project test command |
| 4 | Determine base branch | `git merge-base` |
| 5 | Present 4 options | User choice |
| 6 | Execute choice | git commands |
| 7 | Cleanup worktree | `git worktree remove` |

| Option | Merge | Push | Keep Worktree | Cleanup Branch |
|--------|-------|------|---------------|----------------|
| 1. Merge locally | ✓ | - | - | ✓ |
| 2. Create PR | - | ✓ | ✓ | - |
| 3. Keep as-is | - | - | ✓ | - |
| 4. Discard | - | - | - | ✓ (force) |

## Common Mistakes

**Closing OTHER agents' beads**
- **Problem:** `bd list --status in_progress` shows ALL agents' work - closing them destroys parallel workers' progress
- **Fix:** Only close YOUR assigned bead IDs from your track assignment

**Skipping bead closure**
- **Problem:** Beads stay in_progress, block dependency graph
- **Fix:** Always close YOUR beads before git workflow

**Forgetting file reservations**
- **Problem:** Other agents blocked on stale reservations
- **Fix:** Always call `release_file_reservations()` before finishing

**No orchestrator notification**
- **Problem:** Orchestrator doesn't know track is complete
- **Fix:** Send completion message to epic thread

**Skipping test verification**
- **Problem:** Merge broken code, create failing PR
- **Fix:** Always verify tests before offering options

**No confirmation for discard**
- **Problem:** Accidentally delete work
- **Fix:** Require typed "discard" confirmation

## Red Flags

**Never:**
- Close beads you weren't assigned (destroys other agents' work!)
- Run `bd list --status in_progress` then close everything
- Skip closing YOUR beads when `.beads/` exists
- Leave file reservations held after work complete
- Proceed with failing tests
- Merge without verifying tests on result
- Delete work without confirmation

**Always:**
- Close all in_progress beads first
- Release file reservations
- Notify orchestrator (if in epic)
- Verify tests before offering options
- Get typed confirmation for Option 4

## Integration

**Called by:**
- **orchestrator** (worker completion) - After track beads complete
- **executing-plans** - After all batches complete

**Pairs with:**
- **using-git-worktrees** - Cleans up worktree created by that skill
- **orchestrator** - Receives completion notifications
- **beads** - Closes work items in dependency graph