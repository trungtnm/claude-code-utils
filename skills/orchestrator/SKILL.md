---
name: orchestrator
description: Plan and coordinate multi-agent bead execution. Use when starting a new epic, assigning tracks to agents, or monitoring parallel work progress.
---

# Orchestrator Skill: Autonomous Multi-Agent Coordination

This skill spawns and monitors parallel worker agents that execute beads autonomously.

## Prerequisites

1. **Required**: Run `/skill planning` first to generate `history/<feature>/execution-plan.md`
2. **Recommended**: Run `/skill review-beads` to validate bead quality before spawning workers

## Architecture (Mode B: Autonomous)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              ORCHESTRATOR                                   │
│                              (This Agent)                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. Read execution-plan.md (from planning skill)                            │
│  2. Initialize Agent Mail                                                   │
│  3. Spawn worker subagents via Task()                                       │
│  4. Monitor progress via Agent Mail                                         │
│  5. Handle cross-track blockers                                             │
│  6. Announce completion                                                     │
└─────────────────────────────────────────────────────────────────────────────┘
           │
           │ Task() spawns parallel workers
           ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  BlueLake        │  │  GreenCastle     │  │  RedStone        │
│  Track 1         │  │  Track 2         │  │  Track 3         │
│  [a → b → c]     │  │  [x → y]         │  │  [m → n → o]     │
├──────────────────┤  ├──────────────────┤  ├──────────────────┤
│  For each bead:  │  │  For each bead:  │  │  For each bead:  │
│  • Reserve files │  │  • Reserve files │  │  • Reserve files │
│  • Do work       │  │  • Do work       │  │  • Do work       │
│  • Report mail   │  │  • Report mail   │  │  • Report mail   │
│  • Next bead     │  │  • Next bead     │  │  • Next bead     │
└──────────────────┘  └──────────────────┘  └──────────────────┘
           │                   │                   │
           └───────────────────┼───────────────────┘
                               ▼
                    ┌─────────────────────┐
                    │     Agent Mail      │
                    │  ─────────────────  │
                    │  Epic Thread:       │
                    │  • Progress reports │
                    │  • Bead completions │
                    │  • Blockers         │
                    │                     │
                    │  Track Threads:     │
                    │  • Bead context     │
                    │  • Learnings        │
                    └─────────────────────┘
```

---

## Phase 1: Read Execution Plan

The planning skill outputs `history/<feature>/execution-plan.md` with:

- Track assignments (agent name, beads, file scope)
- Cross-track dependencies
- Key learnings from spikes

```bash
# Read the execution plan
Read("history/<feature>/execution-plan.md")
```

Extract:

- `EPIC_ID` - the epic bead id
- `TRACKS` - array of {agent_name, beads[], file_scope}
- `CROSS_DEPS` - any cross-track dependencies

---

## Phase 2: Initialize Agent Mail

```bash
# Ensure project exists
ensure_project(human_key="<absolute-project-path>")

# Register orchestrator identity
register_agent(
  project_key="<path>",
  name="<OrchestratorName>",
  program="amp",
  model="<model>",
  task_description="Orchestrator for <epic-id>"
)
```

---

## Phase 3: Spawn Worker Subagents

**Spawn all workers in parallel using Task tool with `subagent_type="beads:task-agent"`.**

Workers follow the workflow defined in `agents/worker.md` which includes TDD, coding standards, and git commits.

```python
# Spawn Track 1 Worker
Task(
  subagent_type="beads:task-agent",
  description="Worker BlueLake: Track 1 - <track-description>",
  prompt="""
You are agent BlueLake working on Track 1 of epic <epic-id>.

## First Action
Read the worker workflow: Read("~/.claude/agents/worker.md")

This defines your complete workflow including:
- Bead handling with Agent Mail
- TDD methodology (mandatory)
- Coding standards (mandatory)
- Git commits after each bead

## Setup
Read {PROJECT_PATH}/AGENTS.md for tool preferences.

## Your Assignment
- Orchestrator: <OrchestratorName>
- Beads (in order): <bead-a>, <bead-b>, <bead-c>
- File scope: packages/sdk/**
- Epic thread: <epic-id>
- Track thread: track:BlueLake:<epic-id>

Follow the agent workflow for each bead.
Return a summary of all work completed.
"""
)

# Spawn Track 2 Worker (parallel)
Task(
  subagent_type="beads:task-agent",
  description="Worker GreenCastle: Track 2 - <track-description>",
  prompt="... (same structure, different track/beads/scope) ..."
)

# Spawn Track 3 Worker (parallel)
Task(
  subagent_type="beads:task-agent",
  description="Worker RedStone: Track 3 - <track-description>",
  prompt="... (same structure, different track/beads/scope) ..."
)
```

**Why `beads:task-agent` + agent file?** Workers read `agents/worker.md` for their workflow - self-contained, no skill loading required.

---

## Phase 4: Monitor Progress

While workers execute, monitor via:

### Check Epic Thread for Updates

```bash
search_messages(
  project_key="<path>",
  query="<epic-id>",
  limit=20
)
```

### Check for Blockers

```bash
fetch_inbox(
  project_key="<path>",
  agent_name="<OrchestratorName>",
  urgent_only=true,
  include_bodies=true
)
```

### Check Bead Status

```bash
bv --robot-triage --graph-root <epic-id> 2>/dev/null | jq '.quick_ref'
```

---

## Phase 5: Handle Cross-Track Issues

### If Worker Reports Blocker

```bash
# Read the blocker message
# Determine if it's:
# 1. Waiting on another track → message that worker
# 2. Needs decision → make decision and reply
# 3. External blocker → update bead status

reply_message(
  message_id=<blocker-msg-id>,
  body_md="Resolution: ..."
)
```

### If File Conflict

```bash
# Check who holds reservation
# Message holder to coordinate
send_message(
  to=["<Holder>"],
  thread_id="<epic-id>",
  subject="File conflict resolution",
  body_md="<Worker> needs <files>. Can you release?"
)
```

---

## Phase 6: Epic Completion

When all workers report track complete:

### Verify All Done

```bash
bv --robot-triage --graph-root <epic-id> 2>/dev/null | jq '.quick_ref.open_count'
# Should be 0
```

### Send Completion Summary

```bash
send_message(
  to=["BlueLake", "GreenCastle", "RedStone"],
  thread_id="<epic-id>",
  subject="[<epic-id>] EPIC COMPLETE",
  body_md="""
## Epic Complete: <title>

### Track Summaries
- Track 1 (BlueLake): <summary>
- Track 2 (GreenCastle): <summary>
- Track 3 (RedStone): <summary>

### Deliverables
- <what was built>

### Learnings
- <key insights>
"""
)
```

### Close Epic

```bash
bd close <epic-id> --reason "All tracks complete"
```

---

## Worker Prompt Template

Use this template when spawning workers:

```
You are agent {AGENT_NAME} working on Track {N} of epic {EPIC_ID}.

## First Action
Read the worker workflow: Read("~/.claude/agents/worker.md")

This defines your complete workflow including:
- Bead handling with Agent Mail
- TDD methodology (mandatory)
- Coding standards (mandatory)
- Git commits after each bead

## Setup
Read {PROJECT_PATH}/AGENTS.md for tool preferences.

## Your Assignment
- Orchestrator: {ORCHESTRATOR_NAME}
- Beads (in order): {BEAD_LIST}
- File scope: {FILE_SCOPE}
- Epic thread: {EPIC_ID}
- Track thread: track:{AGENT_NAME}:{EPIC_ID}

Follow the agent workflow for each bead.
Return a summary of all work completed.
```

**Why read agent file?** `agents/worker.md` is self-contained with the complete workflow. Workers read it directly - no skill loading that might be skipped.

---

## Quick Reference

| Phase      | Action                                        |
| ---------- | --------------------------------------------- |
| Read Plan  | `Read("history/<feature>/execution-plan.md")` |
| Initialize | `ensure_project`, `register_agent`            |
| Spawn      | `Task()` for each track (parallel)            |
| Monitor    | `fetch_inbox`, `search_messages`              |
| Resolve    | `reply_message` for blockers                  |
| Complete   | Verify all done, send summary, close epic     |