---
name: orchestrator
model: sonnet
description: Plan and coordinate multi-agent bead execution. Use when starting a new epic, dispatching workers per bead, or monitoring parallel work progress.
---

# Orchestrator Skill: Autonomous Multi-Agent Coordination

## Host compatibility

When running in Codex, read [the Codex compatibility rules](../../CODEX.md)
before using this workflow. Translate every `Task(...)`, `TaskList`,
`TaskOutput`, `SendMessage`, and `AskUserQuestion` example to the current Codex
collaboration or user-input mechanism. Before spawning a worker, tester, or
reviewer, read the matching persona under `../../agents/` and include its
constraints in the delegated task. Claude Code should use the native tool names
shown below.

This skill spawns and monitors parallel worker agents that execute beads autonomously — **one worker per bead**, scheduled by the dependency graph (`bv` / `br ready`), coordinated through Agent Mail file reservations. All work happens directly in the user's working tree, on the current branch.

## Model Requirements

| Role          | Model    | Why                                              |
| ------------- | -------- | ------------------------------------------------ |
| Orchestrator  | `sonnet`  | Coordinates and verifies mechanically (git/br checks, smell greps, checklist matching) — judgment calls are escalated to the user, not made here |
| Workers (coder) | `opus` | Implement code + unit tests, reason about architecture — heavy |
| Tester        | `opus`   | Designs exhaustive functional/edge-case tests against a real test DB — needs strong reasoning to find what the coders missed |
| Reviewer      | `opus`   | Integrated review + writes docs — holistic judgment |

**Role split:** each bead flows through the **coder** (worker agent) that implements it + writes unit tests via TDD. Once every implementation bead is verified, a single independent **tester** agent writes functional/integration/e2e tests against the epic's public surface, and finally a single **reviewer** agent does an integrated quality sweep and writes/updates documentation. Coders own production logic; the tester and reviewer never edit it (they report bugs back).

**If spawning orchestrator as a subagent:** `Task(subagent_type="general-purpose", model="sonnet", prompt="Run /skill orchestrator for epic <id>")`

## Prerequisites

1. **Required**: Run `/skill plan-beads` first to generate `.ccu/artifacts/<dir>/execution-plan.md`
2. **Recommended**: Run `/skill review-beads` to validate bead quality before spawning workers

## Architecture (Mode B: Autonomous)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              ORCHESTRATOR                                   │
│                              (This Agent)                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. Read execution-plan.md (from plan-beads skill)                          │
│  2. Register with Agent Mail + baseline beads + epic context file           │
│  3. Dispatch loop: br ready → spawn a coder PER READY BEAD (cap parallel)   │
│  4. Monitor: inbox (mail), Task results, beads (bv/br), commits (git)       │
│  5. Handle blockers + file-reservation conflicts                            │
│  5.5 Verify coder deliverables per bead (commit + bead closed)              │
│  5.6 Spawn ONE tester for the epic (functional/e2e, real test DB)           │
│  5.7 Route tester bug reports to fix-scoped coders                          │
│  5.8 Spawn reviewer — integrated sweep + docs                               │
│  6. Close epic, flush + commit beads                                        │
└─────────────────────────────────────────────────────────────────────────────┘
           │
           │ one worker per READY bead — all in the SAME working tree
           ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ WORKER (bead A)  │  │ WORKER (bead B)  │  │ WORKER (bead C)  │
├──────────────────┤  ├──────────────────┤  ├──────────────────┤
│ • Reserve Files  │  │ • Reserve Files  │  │ • Reserve Files  │
│ • TDD the bead   │  │ • TDD the bead   │  │ • TDD the bead   │
│ • Report (mail)  │  │ • Report (mail)  │  │ • Report (mail)  │
│ • Commit+close   │  │ • Commit+close   │  │ • Commit+close   │
│ • Release        │  │ • Release        │  │ • Release        │
└──────────────────┘  └──────────────────┘  └──────────────────┘
           │                   │                   │
           └───────────────────┼───────────────────┘
                               ▼
      ┌────────────────────────────────────────────────────────┐
      │                  COORDINATION BUS                      │
      │  ────────────────────────────────────────────────────  │
      │  Agent Mail   → inbox/send/reply: progress, blockers,  │
      │  (durable,      rejections — readable WHILE agents run │
      │   mid-run)      FILE RESERVATIONS: the ONLY lock that  │
      │                 stops two agents editing one file      │
      │                                                        │
      │  Task result  → each agent's structured FINAL report   │
      │  SendMessage  → resume a still-running spawned agent   │
      │  Beads (br)   → status, comments, bug beads            │
      │  bv           → ready order, cycles, critical path     │
      │  Git          → commits = evidence (current branch)    │
      │  .ccu/ files  → epic context notes                     │
      └────────────────────────────────────────────────────────┘
```

### Coordination — how conflicts are prevented

There is **no code isolation layer**. Every agent works in the same tree, so coordination carries the whole load:

- **Agent Mail file reservations = the lock.** A worker reserves its bead's `## Files` before touching them and releases on completion. A failed reservation means someone else holds those files — the worker must not proceed. This is the mechanical net; the plan's disjoint per-bead `## Files` blocks are the intent.
- **`bv` / `br ready` = the schedule.** Only beads whose dependencies are all closed are dispatched. Dependencies are the primary sequencing mechanism — two beads that must not run together should be linked with `br dep add`, not merely kept apart by file scopes.
- **Shared git index = commit discipline.** Parallel workers share one index. Workers must stage named paths only and commit with a pathspec (`git commit -m "..." -- <paths>`) so a concurrent worker's staged files are never swept into their commit. `git add -A` is forbidden.

**Critical:** Agent Mail is keyed to the **repo root** — and MCP calls don't expand shell vars, so you must paste the *literal* root path (`git rev-parse --show-toplevel`, echo it first). Reservations only collide if every agent registers under that same key.

### Coordination Primitives

| Need | Tool |
| ---- | ---- |
| Register identity | `macro_start_session(human_key="<literal repo root>", ...)` — auto-generates your name |
| Find dispatchable beads | `br ready --json` + `bv --robot-triage --graph-root <epic-id>` |
| Spawn coder/tester/reviewer | `Task(subagent_type=...)` |
| See progress **mid-run** | `fetch_inbox` / `search_messages` — workers mail reports as they land, before Task() returns |
| Receive the authoritative report | The agent's **final message** (returned as the Task result) |
| Send a rejection / decision | `send_message` (durable, survives the agent's exit) + `SendMessage` to resume a live agent |
| **File-conflict prevention** | `file_reservation_paths` per bead — the bead's `## Files` block is the reservation list |
| Durable audit trail | `br comments add` + git commits |
| Cross-bead context | `.ccu/artifacts/<dir>/epic-context.md` |
| Bug hand-off | Bug beads (`br create --labels bug`) + `[BUG]` section in tester's final report |

**Mail does not replace the Task result.** A subagent's run *ends* when it returns — so never tell a worker to "send a message and wait for a reply." Mail is for durable, observable-while-running state; `SendMessage` (or a fresh respawn) is the only thing that actually resumes a worker.

---

## Phase 1: Read Execution Plan

The [[plan-beads]] skill outputs `.ccu/artifacts/<dir>/execution-plan.md` with:

- The epic's bead list (id, title, `## Files` scope, dependencies, risk annotations)
- Entry points (beads ready at start, per `br ready`)
- High-risk components flagged for worker investigation

```bash
# Read the execution plan
Read(".ccu/artifacts/<dir>/execution-plan.md")
```

Extract:

- `EPIC_ID` - the epic bead id
- The per-bead file scopes (each bead's `## Files` block — also readable via `br show <id>`)
- Any noted risks or sequencing caveats

**The plan describes; the graph schedules.** Never dispatch from the plan document alone — `br ready` is the live source of what can run now.

---

## Phase 2: Initialize Agent Mail + Coordination State

### Register with Agent Mail

**Agent Mail tool calls are NOT shell — `$VAR` will not expand inside them.**
First read the literal repo root, then paste it into the call:

```bash
git rev-parse --show-toplevel      # e.g. /Users/you/code/myrepo — copy this absolute path
```

```
macro_start_session(
  human_key="/Users/you/code/myrepo",   # the LITERAL repo root you just echoed — NOT a "$VAR"
  program="claude-code",
  model="sonnet",
  task_description="Orchestrator for <epic-id>"
)
```

- ⚠️ Agent Mail enforces adjective+noun names (e.g. `TopazRiver`, `GreenCastle`). Do **NOT** pass a custom name — let it auto-generate, then capture the assigned `agent.name` from the response as `ORCH_NAME`. Every later mail call uses it.
- ⚠️ The `human_key` must be the **literal repo root**. Passing a `"$VAR"` string verbatim silently puts you in a private mailbox where no other agent's file reservations are visible — defeating the lock with no error.
- Set an open contact policy so workers' contact requests auto-accept: `set_contact_policy(agent_name=ORCH_NAME, policy="open")`.
- Check for peers already active on this repo (another `/t:auto` session may be running): `list_contacts()`. Their reservations are live and your workers must respect them.

### Baseline beads + epic context

```bash
# What's open before any work starts
bv --robot-triage --graph-root <epic-id> 2>/dev/null | jq '.quick_ref'

# Epic context file — workers read it before starting and append learnings after each bead
mkdir -p .ccu/artifacts/<dir>
touch .ccu/artifacts/<dir>/epic-context.md
```

Each worker registers its own Agent Mail identity and reports it back; you address it by that name for mail, and by the harness's agent id for `SendMessage`. Keep both.

### Record the starting point

```bash
git rev-parse --short HEAD   # baseline commit — everything after this is the epic's work
git status --porcelain       # warn the user if the tree is already dirty before starting
```

If the tree has uncommitted changes, tell the user before dispatching workers — worker commits will land on top of their in-progress state.

---

## Phase 3: Dispatch Loop — One Worker per Ready Bead

**The dependency graph drives dispatch.** Repeat until every implementation bead in the epic is done:

### Step 1: Find ready beads

```bash
br ready --json 2>/dev/null                                    # unblocked beads, deps all met
bv --robot-priority 2>/dev/null | jq '.'                       # which ready bead matters most
bv --robot-triage --graph-root <epic-id> 2>/dev/null | jq '.quick_ref'
```

Filter to beads belonging to this epic. `bv` ranks them (critical path, unblock count) — dispatch high-leverage beads first.

### Step 2: Check file-scope overlap before spawning

Two ready beads whose `## Files` blocks overlap must NOT run concurrently — the second worker's reservation would fail immediately. Compare the `## Files` of every candidate (`br show <id>`); if two overlap, dispatch one now and hold the other until the first closes. (If they overlap *and* have no dependency between them, that's a plan smell — consider `br dep add` to make the order explicit.)

### Step 3: Spawn workers (parallel, capped)

Spawn **one worker per dispatchable bead**, in parallel, as **background** tasks so you can read their mail mid-run (Phase 4) instead of blocking on each `Task()`.

**Cap concurrency at 3 workers.** All workers share one working tree, one git index, and one build/test environment — beyond ~3, gate runs start colliding and progress reverses. When a worker finishes and its bead closes, dispatch the next ready bead.

```
Task(subagent_type="worker", model="opus", prompt=<Worker Prompt Template below>)
```

Every worker prompt MUST carry: its **single assigned bead id**, the bead's `## Files` scope, the **literal** repo root (the mail project key — echo it, don't pass `$VAR`), and your `ORCH_NAME`. A worker that registers under the wrong key sees nobody's reservations.

### Step 4: On each bead completion

When a worker's bead is verified (Phase 5.5): re-run `br ready` — closing a bead typically unblocks others. Dispatch the newly ready beads (back to Step 1). The loop ends when the epic has no open implementation beads.

---

## Phase 4: Active Progress Monitoring (Loop)

**Do NOT fire-and-forget.** After spawning workers, enter a monitoring loop that actively checks progress, inspects code quality, and escalates to the user when needed.

### Monitoring Loop

Run this loop after every worker Task() returns OR periodically while workers are running in background:

```
REPEAT until all beads complete:
  1. Check inbox (mail) + finished agents' final reports; check bead progress
  2. Inspect recent commits for quality smells
  3. Escalate to user if issues found
  4. Handle blockers and reservation conflicts
  5. Dispatch newly ready beads (Phase 3, Step 4)
```

### Step 1: Check Inbox, Reports & Bead Status

Progress reaches you through two channels, and you need both:

**Agent Mail — the live channel.** Workers mail a report as the bead lands, so you see progress before their Task() returns:

```
# project_key is the LITERAL repo root you echoed in Phase 2 (MCP calls don't expand $VARs):
fetch_inbox(project_key="<repo-root>", agent_name=ORCH_NAME, urgent_only=false, include_bodies=true)
search_messages(project_key="<repo-root>", query="<epic-id>", limit=20)
```

Acknowledge what you read (`mark_message_read` / `acknowledge_message`) so the inbox stays a queue of things needing action, not a growing log.

**Task results — the authoritative channel.** Each Task() result IS the worker's final bead report; read it in full. For background agents, `TaskList` / `TaskOutput(task_id)` peek at progress, and the harness re-invokes you on completion.

**Durable state — the ground truth.** Never trust either channel over the repo itself:

```bash
bv --robot-triage --graph-root <epic-id> 2>/dev/null | jq '.quick_ref'
br show <bead-id> --json                             # per-bead status + deliverables comments
git log --grep="Bead:" --oneline | head -20          # commits landing in real time
```

A worker that mails "COMPLETE" but has no commit is **not** complete (Phase 5.5).

### Step 2: Inspect Recent Commits for Quality Smells

**After each worker reports a bead complete**, inspect their actual code — do NOT trust self-reports alone.

```bash
# Get the worker's commit
git log --grep="Bead: <bead-id>" --format="%H" | head -1

# Inspect the diff for quality smells
git show <commit-hash> --stat   # What files changed?
git show <commit-hash> -p       # Full diff
```

**Also check scope:** the commit's file list must stay inside the bead's `## Files` block. Files outside it mean the worker drifted — or swept up another worker's staged changes from the shared index. Either way, reject.

**Scan the diff for these red flags:**

| Smell | Pattern to grep for | Problem |
| ----- | ------------------- | ------- |
| Mock implementations | `mock`, `Mock`, `MOCK`, `jest.fn()`, `vi.fn()` in non-test files | Worker faked it instead of building it |
| Stubs / placeholders | `stub`, `Stub`, `STUB`, `not implemented`, `TODO`, `FIXME`, `placeholder` | Incomplete implementation |
| Hardcoded data | `hardcoded`, `hardcode`, large inline arrays/objects pretending to be real data | No actual integration |
| Skipped tests | `test.skip`, `it.skip`, `describe.skip`, `xit(`, `xdescribe(` | Tests deliberately bypassed |
| Empty implementations | Functions with only `return null`, `return []`, `return {}`, `// TODO` | Hollow code |

```bash
# Quick automated check on the commit diff
git show <commit-hash> -p | grep -iE '(mock|stub|placeholder|not.implemented|TODO|FIXME|hardcode|test\.skip|it\.skip|return null|return \[\]|return \{\})' | head -20
```

**If ANY smell is found in non-test production code:**
1. Do NOT accept the bead
2. Escalate to user (see Step 3)

**Exception — documented bug skips (tester commits only):** a `test.skip`/`it.skip` inside a TEST file whose test name begins with `EXPOSES BUG:` is the tester's bug-bounce mechanism (Phase 5.7), NOT a smell — but ONLY if a matching bug bead exists (`br list --labels bug --json`, title beginning `[BUG]`) referencing that test. Verify the bug bead exists before accepting; a skip without the marker or without a bug bead is an ordinary smell. Coder commits must never contain skips.

### Step 3: Escalate to User

**Use `AskUserQuestion` when any of these situations arise:**

#### Situation A: Quality Smell Detected

```
AskUserQuestion(questions=[{
  question: "Worker {AGENT_NAME} completed bead {BEAD_ID} but the code contains quality concerns:\n\n{SMELL_DETAILS}\n\nCommit: {HASH}\nFiles: {FILE_LIST}\n\nHow should we proceed?",
  header: "Quality",
  options: [
    {label: "Reject & rework", description: "Send worker back to redo with real implementation"},
    {label: "Accept as-is", description: "The mock/stub is intentional for this phase"},
    {label: "Let me review", description: "I'll check the code and decide"}
  ],
  multiSelect: false
}])
```

If user says **reject**, deliver the rework order on **both** channels:

```bash
# 1. Durable record — survives the worker's exit, readable by whoever picks the bead up
send_message(to=[WORKER_MAIL_NAME], thread_id="<epic-id>",
  subject="[<bead-id>] REJECTED — incomplete implementation",
  body_md="Your implementation contains mocks/stubs/placeholders in production code. This bead requires a REAL, complete implementation.\n\nSmells found:\n{SMELL_DETAILS}\n\nRedo with actual working code — no mocks, no stubs, no TODOs in production files. Re-run all gates, commit, and re-report.",
  importance="high")
```

```
# 2. Actually resume the worker (mail alone will NOT wake a finished agent)
SendMessage(to=<worker agent id>, content="[<bead-id>] REJECTED — see your inbox. Smells: {SMELL_DETAILS}. Redo with real working code, re-run all gates, commit, re-report.")
```

**If the worker's Task() has already returned, `SendMessage` cannot revive it** — respawn a fix-scoped worker with the rejection context in its prompt. The mailed rejection is what makes that respawn cheap: the new agent reads the thread and has the full history.

#### Situation B: Worker Stuck / No Progress

If a worker's Task() run completed without closing its bead and without a blocker report:

```
AskUserQuestion(questions=[{
  question: "Worker {AGENT_NAME} appears stuck on bead {BEAD_ID}.\n\nLast message: {LAST_MSG_SUMMARY}\nBead status: {STATUS}\n\nWhat should we do?",
  header: "Stuck",
  options: [
    {label: "Respawn worker", description: "Spawn a fresh worker for this bead"},
    {label: "Skip for now", description: "Dispatch other ready beads and revisit"},
    {label: "I'll intervene", description: "I'll handle this bead manually"}
  ],
  multiSelect: false
}])
```

#### Situation C: Worker Asks for Architectural Decision

If a worker message contains questions about approach, design, or asks "should I...":

```
AskUserQuestion(questions=[{
  question: "Worker {AGENT_NAME} needs a decision on bead {BEAD_ID}:\n\n> {WORKER_QUESTION}\n\nWhat's your call?",
  header: "Decision",
  options: [
    {label: "Option A", description: "{first option from worker}"},
    {label: "Option B", description: "{second option from worker}"},
    {label: "Let me respond directly", description: "I'll write a custom response"}
  ],
  multiSelect: false
}])
```

Then relay the user's decision back via `SendMessage` (or include it in the respawn prompt if the worker can't be continued).

---

## Phase 5: Handle Blockers & Reservation Conflicts

### If Worker Reports Blocker

Blockers surface three ways: a **high-importance mail** from the worker (fastest — arrives mid-run), the bead flipping to `blocked` with a `br` comment, and/or the worker's final report leading with `BLOCKED`.

```bash
# Read the blocker context (project_key = the LITERAL repo root from Phase 2)
fetch_inbox(project_key="<repo-root>", agent_name=ORCH_NAME, urgent_only=true, include_bodies=true)
br show <bead-id> --json    # status + the worker's "Blocked by: ..." comment

# Determine what it is:
# 1. Waiting on another bead → the dependency graph should already encode this;
#    if it doesn't, add it (`br dep add <blocked> <blocker>`) so bv sequences it,
#    then dispatch the blocked bead again once the blocker closes
# 2. Needs architectural decision → ESCALATE TO USER (do not decide yourself)
# 3. External blocker → ESCALATE TO USER

# Coordination you CAN resolve yourself:
reply_message(message_id=<blocker-msg-id>, body_md="Resolution: ...")
```

**A mailed reply does not restart a finished worker.** If its Task() already returned, `reply_message` records the resolution durably — but you still need `SendMessage` (live agent) or a respawn (exited agent) to make work resume.

**Rule: The orchestrator coordinates, it does NOT make architectural or implementation decisions.** When in doubt, escalate to the user. Bad autonomous decisions (like approving mocks) cost more time than a 30-second user check.

### If File Conflict

With no worktrees, a reservation conflict means two agents want the same file **right now**. The reservation is the only thing standing between them and a live overwrite — treat every conflict seriously.

A worker whose `file_reservation_paths` call fails must not proceed. When that happens:

```bash
# Who holds it? (another worker — or another session entirely)
file_reservation_paths(...)   # the failure names the holder
send_message(to=["<Holder>"], thread_id="<epic-id>",
  subject="File conflict: <files>",
  body_md="<Worker> needs <files> for <bead-id>. Can you release when your current bead lands?")
```

Then resolve the root cause:

- **Two beads genuinely need the same file** → the graph was wrong. Add the missing dependency (`br dep add`) and dispatch the second bead only after the first closes.
- **A worker drifted outside its `## Files` scope** → reject the commit (Phase 5.5) and have it reworked within scope.
- **The holder is a stale reservation from a dead agent** → `force_release_file_reservation` — but only after confirming the agent is actually gone (no recent mail, Task() returned).

---

## Phase 5.5: Verify Worker Deliverables

**When a worker reports a bead complete, verify FOUR things before accepting:**

### 1. Commit Exists

```bash
git log --grep="Bead: <bead-id>" --oneline
# Must return at least one commit
```

### 2. Commit Stays In Scope

```bash
git show <commit-hash> --stat
# Every file must be inside the bead's `## Files` block (or a test path for it).
# Out-of-scope files = scope drift OR another worker's staged files swept in — reject either way.
```

### 3. Bead Is Closed

```bash
br show <bead-id> --json
# Status must be "done"
```

### 4. Deliverables Reported

The worker's report (mailed and in its final message) MUST include: commit hash, test counts, bead status. If any field is missing, reject.

### On Failure — Reject and Reassign

Mail the rejection (durable), then resume the worker via `SendMessage` if it is still live, or respawn it fix-scoped if it is not:

```bash
# If commit missing:
send_message(to=[WORKER_MAIL_NAME], thread_id="<epic-id>",
  subject="[<bead-id>] REJECTED — no commit found",
  body_md="No commit with `Bead: <bead-id>` exists. Commit your work and re-report.", importance="high")

# If bead not closed:
send_message(to=[WORKER_MAIL_NAME], thread_id="<epic-id>",
  subject="[<bead-id>] REJECTED — bead not closed",
  body_md="Bead <bead-id> status is not 'done'. Run `br close <bead-id>` and re-report.", importance="high")

# If deliverables incomplete:
send_message(to=[WORKER_MAIL_NAME], thread_id="<epic-id>",
  subject="[<bead-id>] REJECTED — missing deliverables",
  body_md="Report must include: commit hash, test counts (N/M), bead status. Re-send.", importance="high")
```

Then: `SendMessage(to=<worker agent id>, ...)` to resume a live agent, or respawn a fix-scoped worker pointing at the mail thread.

**A verified bead unlocks the graph** — re-run `br ready` and dispatch what it freed (Phase 3, Step 4).

**Do NOT proceed to Phase 5.6 until ALL implementation beads pass verification.**

---

## Phase 5.6: Independent Testing (Per Epic)

**Once every implementation bead is verified, spawn ONE `tester` agent for the epic.** The tester writes functional (primary), integration, and e2e tests from a black-box perspective — the independent set of eyes that catches what the coders' own TDD missed.

**Proportionality gate — skip the tester when the epic adds no new behavior surface:** docs-only, config-only, or a pure refactor with contracts unchanged (existing tests still cover it). When skipping, note it in a comment on the epic bead (`br comments add <epic-id>`) so the reviewer knows the epic is untested by design. When in doubt, spawn the tester.

```
Task(subagent_type="tester", model="opus", prompt=<Tester Prompt Template below>)
```

**Key constraints the orchestrator enforces:**
- Tester touches ONLY test-file paths → never conflicts with coder file scope.
- Tester runs against a **real test database**, not mocks of the datastore. If the tester reports "no test-DB harness exists," treat setting one up as legitimate new infra — don't reject it. (Projects with no datastore — CLI, library, frontend-only — test against their real runtime instead; don't demand a DB.)
- Tester must NOT edit production code. If a tester's commit touches non-test files, reject it.
- Functional tests with rich **edge-case coverage** are the deliverable. A tester report showing only happy-path tests is incomplete — send it back to broaden coverage.

**Verify tester deliverables** (same rigor as Phase 5.5):
```bash
git log --grep="Bead: <test-bead-id>" --oneline   # commit exists
br show <test-bead-id> --json                     # status "done"
git show <hash> --stat                            # confirm ONLY test files changed
```

**Judge edge-case coverage by checklist matching, not intuition:** the tester posted a test-plan checklist as a bead comment (tester workflow step 3). Compare the delivered tests against that checklist — every item must be either delivered or explicitly explained. Happy-path-only = incomplete, send back. This is a mechanical comparison; you do not need to assess test quality yourself.

## Phase 5.7: Route Tester Bug Reports Back to Coders

When the tester's final report lists `[BUG]` entries — each backed by a **bug bead** (`br list --labels bug`) — the tester has NOT fixed them. You route each one to a coder.

**Lifecycle reality: by the time the tester runs, every original coder's Task() has returned.** The standard path is therefore a **fresh fix-scoped respawn**, not a message to a live agent:

```
Task(subagent_type="worker", model="opus", prompt="""
You are a fix-scoped coder for epic {EPIC_ID}.
Agent Mail project key: {literal repo root — echo it, don't pass $VAR}.
An independent tester found a defect in code committed for bead {BEAD_ID}.
Bug bead: {BUG_BEAD_ID} — read its comments for the full report: br show {BUG_BEAD_ID} --json

{FULL_BUG_REPORT from the bug bead}

Your job:
1. Reserve the production files you will touch (file_reservation_paths) before editing.
2. Reproduce via the failing test at {TEST_FILE}::{TEST_NAME} (currently `.skip` with an `EXPOSES BUG:` marker).
3. Fix the production code at ROOT CAUSE — no bandaids, do not weaken the test.
4. Un-skip the tester's failing test and make it pass.
5. Re-run all gates (tests, lint, typecheck, build), commit referencing `Bead: {BEAD_ID}` — stage named paths only, commit with `git commit -m "..." -- <paths>`.
6. Release your reservations, close the bug bead: `br close {BUG_BEAD_ID} --reason "fixed in <hash>"` — and report the fix commit hash in your final message.
""")
```

**The fixer un-skips.** The fix-scoped coder removes the `.skip` and shows the test passing in its own fix commit — no extra tester round-trip is needed just to re-activate the test.

After the fix lands:
1. Re-verify the fix commit (Phase 5.5 checks) and confirm the previously-skipped test now runs and passes.
2. Confirm the full suite is green before proceeding.

**Do NOT proceed to Phase 5.8 until every bug bead is either closed (fixed-and-green) or explicitly deferred with user sign-off.** Check: `br list --labels bug --json` — no open bug beads for this epic.

---

## Phase 5.8: Review & Documentation

**After all beads are verified, tested, and bug-free, spawn the `reviewer` agent** against the integrated result on the current branch. It does two things: (1) an integrated quality sweep that catches what per-bead TDD and independent testing miss, and (2) writes/updates the documentation for what the epic built — docs are only written now, against the final integrated code.

**Skip the review sweep if:** the epic is trivial (< 3 beads total). **Docs should still be written** for any user-facing surface unless the user opts out.

### Spawn Reviewer Agent

Spawn a single `reviewer` agent (definition auto-loaded via `subagent_type`) with access to all committed code:

```
Task(subagent_type="reviewer", model="opus", prompt="""
You are the final reviewer + documentarian for epic {EPIC_ID}.

## Change set
All commits from this epic (implementation + tests):
```bash
git log --grep="Bead:" --oneline | head -40
```
Read each diff with `git show <hash> -p`.

## Part 1 — Review (integrated, holistic)
Run UBS (`ubs --format=toon`), then check cross-bead consistency, integration gaps, fresh-eyes bugs, security basics, and remaining test-coverage gaps. If frontend: UI/UX consistency, accessibility, responsive edges. Do NOT fix production code — report issues for the orchestrator to route.
Output the Critical / Recommended / Nits / Verdict block.

## Part 2 — Documentation
Once the verdict is PASS (or criticals are acknowledged out-of-scope), write/update docs for the epic's public surface: README sections, feature/usage docs, API reference, CHANGELOG. Pull examples from the passing test suite. Keep docs accurate over exhaustive. Preserve Vietnamese diacritics. Commit docs with a `docs(<scope>):` message referencing a docs bead.

## Report
Your FINAL MESSAGE is your report — it must contain the review verdict + counts AND the list of doc files updated with the docs commit hash.
""")
```

### Handle Review Results

**If verdict is PASS:** Proceed to Phase 6.

**If verdict is NEEDS_FIXES with critical issues:** Escalate to user.

```
AskUserQuestion(questions=[{
  question: "Integrated review found issues in epic {EPIC_ID}:\n\n{CRITICAL_ISSUES}\n\nHow should we handle these?",
  header: "Review",
  options: [
    {label: "Fix critical only", description: "Spawn a worker to fix critical issues, skip nits"},
    {label: "Fix all", description: "Spawn a worker to fix critical + recommended issues"},
    {label: "Skip fixes", description: "Accept as-is and proceed to completion"},
    {label: "Let me review", description: "I'll look at the issues and decide"}
  ],
  multiSelect: false
}])
```

**If user says fix:** Spawn an opus worker to apply fixes, then re-run verification (Phase 5.5) on the fix commit.

---

## Phase 6: Epic Completion

When all beads are verified, tested, reviewed:

### Verify All Done

```bash
bv --robot-triage --graph-root <epic-id> 2>/dev/null | jq '.quick_ref.open_count'
# Should be 0
```

### Announce Completion

Broadcast the epic summary to every agent that took part, so the thread closes cleanly and any still-live peer (e.g. a concurrent `/t:auto` session) sees the epic is done and the files are released:

```bash
send_message(to=[<all worker/tester/reviewer agent names>], thread_id="<epic-id>",
  subject="[<epic-id>] EPIC COMPLETE",
  body_md="""
## Epic Complete: <title>

### Bead Summaries
- <bead-id> (<AgentName>): <summary>
- <bead-id> (<AgentName>): <summary>

### Deliverables
- <what was built>
""")
```

Then confirm no reservations are left dangling — a stale lock blocks the next session:

```bash
file_reservation_paths()   # list what's still held for this project
# force_release_file_reservation(...) only for agents confirmed gone
```

### Write Completion Summary

Write the epic summary to `.ccu/artifacts/<dir>/summary.md` — it outlives the mail thread and anchors your final report to the user:

```bash
Write(".ccu/artifacts/<dir>/summary.md", """
# Epic Complete: <title>

**Epic:** <epic-id>
**Date:** <completion-date>

## Bead Summaries
- <bead-id>: <summary>
- <bead-id>: <summary>

## Deliverables
- <what was built>

## Learnings
- <key insights>
""")
```

Then regenerate the artifacts HTML index so the epic's summary joins the plan docs in one switchable viewer:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/markdown-html-viewer/scripts/md2html.py" .ccu/artifacts/<dir>/
```

Directory + default fetch mode → one `index.html` switching across discovery / approach / execution-plan / summary. No build questions — the automated exception documented in [[session-state]]. Point the user at `index.html` (open via `open_in_dev_browser.sh`).

`.ccu/artifacts/` is gitignored, so this summary stays local. The durable record of the epic lives in:
- Commit messages from each bead (the actual work)
- `.beads/` JSONL exports (closed beads with reasons)
- `.ccu/DECISIONS.md` (architectural decisions made during the epic)

### Close Epic

```bash
ACTOR="${BR_ACTOR:-assistant}"
br close --actor "$ACTOR" <epic-id> --reason "All beads complete"
```

### Commit the Beads Database

```bash
br sync --flush-only                 # export the shared DB → .beads/issues.jsonl
git add .beads/
git commit -m "epic(<epic-id>): close all beads

All beads complete. See bead reasons for individual deliverables.

Epic: <epic-id>"
```

The epic's code commits are already on the current branch — there is nothing to merge. Whether and when to `git push` is the user's call; ask if unsure.

---

## Worker Prompt Template

Use this template when spawning workers with `subagent_type="worker"`:

```
You are the coder for bead {BEAD_ID} of epic {EPIC_ID}.

## Session environment (use EXACTLY these — do not re-derive them)
- Working directory: the repo root — you work directly in the user's tree, on the current branch
- Agent Mail project key: {LITERAL repo root — e.g. /Users/you/code/myrepo}  ← paste this literal path into every mail call, NOT "$VAR"
- Orchestrator (mail name): {ORCH_NAME}
- Epic thread: {EPIC_ID}

Registering Agent Mail under anything but the literal repo root hides every other agent's file
reservations from you, and you would clobber their work — there is NO other isolation layer.

## Setup
Read {PROJECT_PATH}/AGENTS.md for tool preferences.

## Your Assignment
- Bead: {BEAD_ID} — read it in full: br show {BEAD_ID} --json
- File scope: the bead's `## Files` block — you may ONLY create/modify files inside it
- Reserve those files via Agent Mail (file_reservation_paths) BEFORE editing; release when the bead lands.
  If the reservation FAILS, another agent holds the files — report the conflict to the orchestrator and STOP. Do not wait, do not proceed.
- Epic context file: .ccu/artifacts/{EPIC_DIR}/epic-context.md
  (read it before starting; append learnings after the bead)

## Implementation Rules (STRICT)
- Implement REAL, working code — no mocks, stubs, or placeholders in production files
- Mocks are ONLY acceptable in test files (*.test.*, *.spec.*)
- No `TODO`, `FIXME`, or `not implemented` comments in production code
- No hardcoded fake data pretending to be real integrations
- No `test.skip` or `it.skip` — all tests must run
- **Shared git index:** other workers are committing in this same tree. NEVER `git add -A` or `git add .`.
  Stage your named files only, and commit with a pathspec so nothing else is swept in:
  `git add <your files> && git commit -m "..." -- <your files>`
- If you cannot fully implement something, STOP — mark the bead blocked with a comment explaining WHY, do not fake it
- If you need a decision on approach, record the question in a bead comment and end your run asking for it — do not guess
- **Bead comments are a point-in-time audit trail, NOT ground truth for PR/branch/merge state.** Before reporting that a PR is open or merged (or a branch landed), confirm against git/GitHub — `gh pr view <n> --json state,mergedAt`, `gh pr list --head <branch>`, `git log --oneline <branch>`. Never repeat a comment's PR claim as current fact; if you can't confirm, report it as unverified.

## Deliverables Contract
Report on BOTH channels:
1. **Mail the orchestrator** ({ORCH_NAME}, thread {EPIC_ID}) as soon as the bead lands —
   this is how the orchestrator sees progress before your run ends.
2. **Record durably** (bead close reason + `br comments add`).

Every report carries: **commit hash** (`git log -1 --format='%h'`), **test counts** (N/M),
**bead status** (confirmed "done" via `br show`).

Orchestrator INSPECTS your code diff for quality smells (mocks, stubs, TODOs) and for
out-of-scope files. Missing any field OR smells OR scope drift = rejection and rework.

Do NOT mail a question and then wait for a reply — your run would end with the bead unfinished.
Record the question, make the best reasonable call, and flag it in your report.

Follow the worker workflow for the bead.
Your FINAL MESSAGE is your report to the orchestrator — end with the bead-report
block (bead → commit → tests → status) plus public surface and unit-level gaps.
```

**Note:** The worker agent definition (`~/.claude/agents/worker.md`) is automatically loaded via `subagent_type="worker"`. No explicit Read() needed.

---

## Tester Prompt Template

Use this template when spawning the tester with `subagent_type="tester"` (Phase 5.6):

```
You are the independent tester for epic {EPIC_ID}.

## Session environment (use EXACTLY these)
- Working directory: the repo root — the same tree the coders worked in, on the current branch
- Agent Mail project key: {LITERAL repo root}  ← paste this literal path into mail calls, NOT "$VAR"
- Orchestrator (mail name): {ORCH_NAME}
Register with Agent Mail and reserve the TEST files you create (test paths only — never
production files, so you cannot collide with a coder).

## Setup
Read {PROJECT_PATH}/CLAUDE.md for the test framework, test-DB setup, and commands.

## Your Assignment
- Epic under test: {EPIC_ID} — {EPIC_SUMMARY}
- Public surface to test: {PUBLIC_SURFACE from coders' final reports}
- Coder-flagged uncovered behaviors: {UNCOVERED_AT_UNIT}
- Epic context file: .ccu/artifacts/{EPIC_DIR}/epic-context.md (implementation learnings/gotchas)

## Rules (STRICT)
- Write functional tests FIRST and be exhaustive on edge cases — that is the deliverable.
- Run against a REAL test database in an isolated test environment — never mock the datastore.
- You may ONLY create/edit test files. NEVER edit production code.
- Stage named test files only; commit with `git commit -m "..." -- <test files>` (shared index).
- If a test exposes a real bug: keep the failing test as `.skip` with a test name beginning
  with `EXPOSES BUG:` (this marker exempts it from the skip-smell scan), then file a bug bead
  (`br create --labels bug --title "[BUG] ..."`) with a reproducible report. Do NOT fix it.
- All non-skipped tests must pass against the real implementation before you commit.

## Deliverables Contract
Your FINAL MESSAGE is your report to the orchestrator: commit hash (test files only),
functional/integration/e2e counts, edge cases covered, suite status, how the test DB is
provisioned, and any bug bead ids under a `[BUG]s found` section.

Follow the tester agent workflow.
```

**Note:** The tester agent definition is auto-loaded via `subagent_type="tester"`.

---

## Red Flags - STOP

- Never accept unverified work — self-reports are not proof
- Worker says "done" → verify commit exists via `git log --grep`
- Bead "closed" → confirm with `br show`, don't trust reports alone
- Proceeding to Phase 6 → ALL Phase 5.5 verifications must pass first
- Missing deliverables (no hash, no test counts) → reject immediately
- Skipping the Phase 6 `.beads/` commit → closed-bead state never recorded
- **Passing a `$VAR` verbatim into an MCP mail call → it does NOT expand; you register under a garbage key, land in a private mailbox, and see nobody's reservations. Echo the value first, paste the literal repo-root path**
- **Spawning a worker without reservation instructions → with no worktrees, the reservation IS the only thing preventing two agents from overwriting each other live**
- **Dispatching two ready beads with overlapping `## Files` → the second reservation fails on arrival; sequence them (and add the missing `br dep add`)**
- **More than 3 concurrent workers → shared index + shared build/test env starts thrashing**
- **A commit containing files outside the bead's `## Files` → scope drift or a swept-up index; reject**
- **Telling an agent to "send a message and wait for a reply" → deadlock. A subagent's run ENDS when it returns; use `SendMessage` or a respawn to resume it**
- **Mocks/stubs in production code → ALWAYS reject and escalate to user**
- **Worker asking "should I..." → ALWAYS escalate to user, do NOT decide for them**
- **Worker silent after Task() returns with an open bead → escalate as stuck**
- **Making architectural decisions yourself → STOP, you coordinate — escalate to user**
- **Tester commit touches production (non-test) files → reject; testers never edit logic**
- **Tester delivered only happy-path tests → send back; exhaustive edge cases are the deliverable**
- **Tester used mocks for the datastore → reject; functional tests must hit the real test DB**
- **Open `[BUG]` report unresolved → do NOT proceed to review/completion until fixed or deferred with user sign-off**
- **Docs written before code is integrated → docs come last, against final code**

---

## Quick Reference

| Phase        | Action                                        |
| ------------ | --------------------------------------------- |
| Read Plan    | `Read(".ccu/artifacts/<dir>/execution-plan.md")`     |
| Initialize   | `macro_start_session` (key = **literal** repo root, echoed) → `ORCH_NAME`; baseline beads (`bv`); epic context file |
| **Dispatch** | `br ready` + `bv --robot-priority` → spawn `worker` per ready bead (cap 3, check `## Files` overlap first) |
| **Monitor**  | Loop: `fetch_inbox` (live) + Task results, `bv --robot-triage`, `git log` |
| **Inspect**  | `git show <hash> -p`, grep for smells, check scope vs `## Files` |
| **Escalate** | `AskUserQuestion` for stuck/quality/decisions |
| Resolve      | `send_message`/`reply_message` (durable) + `SendMessage`/respawn (to actually resume) |
| **Conflicts** | `file_reservation_paths` failure → add the missing dep, sequence beads, or reject scope drift |
| **Verify**   | `git log --grep`, `git show --stat` (scope), `br show`, check report — then re-run `br ready` and dispatch |
| **Test**     | Spawn ONE `tester` for the epic (real test DB) after all beads verified |
| **Route bugs** | Respawn fix-scoped coder per open bug bead  |
| **Review+Docs** | Spawn `reviewer` for integrated sweep + docs |
| Complete     | Broadcast summary, release reservations, close epic |
| **Commit beads** | `br sync --flush-only && git add .beads/ && git commit` |
