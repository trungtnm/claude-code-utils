---
name: planning
description: Use when asked to plan a feature, create a roadmap, or design an implementation approach. Triggers on requests for comprehensive plans, feature decomposition, or multi-phase implementation strategies.
---

# Feature Planning Pipeline

Generate quality plans through systematic discovery, synthesis, verification, and decomposition.

## IMPORTANT: Execution Mode

**This skill replaces Claude Code's built-in planning.** When this skill is active:

- Do **NOT** use `EnterPlanMode` — this skill IS the plan mode
- Do **NOT** use `TaskCreate`, `TaskUpdate`, or `TaskList` — use beads (`bd`) for task tracking instead
- Do **NOT** ask the user to approve a plan before executing — just run the pipeline phases sequentially
- Do **NOT** pause between phases to ask "should I continue?" — proceed through all 7 phases automatically
- The only user interaction should be `AskUserQuestion` when genuine ambiguity exists (e.g., choosing between approach options in Phase 2)

## Pipeline Overview

```
USER REQUEST → Discovery → Synthesis → Verification → Decomposition → Validation → Track Planning → Artifact Check → Ready Plan
```

| Phase             | Tool                                     | Output                              |
| ----------------- | ---------------------------------------- | ----------------------------------- |
| 1. Discovery      | Parallel Task(Explore), gkg              | Discovery Report                    |
| 2. Synthesis      | Task(Oracle)                             | Approach + Risk Map                 |
| 3. Verification   | Spikes via parallel Task() calls         | Validated Approach + Learnings      |
| 4. Decomposition  | file-beads skill                         | .beads/\*.md files                  |
| 5. Validation     | bv + Task(Oracle)                        | Validated dependency graph          |
| 6. Track Planning | bv --robot-plan                          | Execution plan with parallel tracks |
| 7. Artifact Check | Verify all files exist                   | Confirmed complete plan             |

## Completion Gate (MANDATORY)

**You are NOT done until ALL of these files exist:**

- [ ] `history/<feature>/discovery.md` (Phase 1)
- [ ] `history/<feature>/approach.md` (Phase 2)
- [ ] `.spikes/<feature>/` directory (Phase 3, if HIGH risk items exist)
- [ ] `.beads/*.md` decomposed work items (Phase 4)
- [ ] `history/<feature>/execution-plan.md` (Phase 6)

**After Phase 6, run Phase 7 to verify each file exists before reporting completion.**
**Missing ANY artifact = incomplete plan. Do not stop early.**

## Red Flags - You Are About to Skip Steps

- "Beads are filed, so the plan is done" → Beads without an execution plan force the orchestrator to re-analyze everything. File the execution plan.
- "The orchestrator can figure out tracks" → No. Track planning is YOUR job. The orchestrator consumes execution-plan.md, it doesn't create it.
- "I'll come back to the execution plan later" → You won't. Do it now.
- "Discovery is obvious, I'll skip to synthesis" → Discovery catches patterns you'd miss. Run the parallel explorers.
- "No HIGH risk items, so I can skip verification" → Correct, but you still need all other artifacts. Don't use this as an excuse to skip Phase 6.
- "The approach is clear from discovery, I don't need approach.md" → Write it anyway. It captures tradeoffs and risk maps that beads reference.

## Phase 1: Discovery (Parallel Exploration)

Launch parallel sub-agents to gather codebase intelligence:

```
Task(subagent_type="Explore") → Agent A: Architecture snapshot (gkg repo_map)
Task(subagent_type="Explore") → Agent B: Pattern search (find similar existing code)
Task(subagent_type="Explore") → Agent C: Constraints (package.json, tsconfig, deps)
WebSearch → External patterns ("how do similar projects do this?")
mcp__exa__get_code_context_exa → Library docs (if external integration needed)
```

Save to `history/<feature>/discovery.md` using the template at `templates/discovery.md`.

## Phase 2: Synthesis (Oracle)

Feed Discovery Report to Oracle for gap analysis:

```
Task(
  subagent_type="Oracle",
  prompt="Analyze gap between current codebase and feature requirements.
          Context: Discovery report attached. User wants: <feature>.
          Read history/<feature>/discovery.md for context."
)
```

Oracle produces:

1. **Gap Analysis** - What exists vs what's needed
2. **Approach Options** - 1-3 strategies with tradeoffs
3. **Risk Assessment** - LOW / MEDIUM / HIGH per component

### Risk Classification

| Level  | Criteria                      | Verification                 |
| ------ | ----------------------------- | ---------------------------- |
| LOW    | Pattern exists in codebase    | Proceed                      |
| MEDIUM | Variation of existing pattern | Interface sketch, type-check |
| HIGH   | Novel or external integration | Spike required               |

### Risk Indicators

```
Pattern exists in codebase? ─── YES → LOW base
                            └── NO  → MEDIUM+ base

External dependency? ─── YES → HIGH
                     └── NO  → Check blast radius

Blast radius >5 files? ─── YES → HIGH
                       └── NO  → MEDIUM
```

Save to `history/<feature>/approach.md` using the template at `templates/approach.md`.

## Phase 3: Verification (Risk-Based)

### For HIGH Risk Items → Create Spike Beads

Spikes are mini-plans executed via parallel Task() calls:

```bash
bd create "Spike: <question to answer>" -t epic -p 0
bd create "Spike: Test X" -t task --blocks <spike-epic>
bd create "Spike: Verify Y" -t task --blocks <spike-epic>
```

Use the spike template at `templates/spike.md`.

### Execute Spikes

Use parallel Task() calls:

1. `bv --robot-plan` to parallelize spikes
2. Launch multiple `Task(subagent_type="general-purpose")` calls in a single message
3. Workers write to `.spikes/<feature>/<spike-id>/`
4. Close with learnings: `bd close <id> --reason "<result>"`

### Aggregate Spike Results

```
Task(
  subagent_type="Oracle",
  prompt="Synthesize spike results and update approach.
          Context: Spikes completed. Results: ...
          Read history/<feature>/approach.md and update with validated learnings."
)
```

Update approach.md with validated learnings.

## Phase 4: Decomposition (file-beads skill)

Load the file-beads skill and create beads with embedded learnings:

```
Skill(skill="file-beads")
```

### Bead Requirements

Each bead MUST include:

- **Spike learnings** embedded in description (if applicable)
- **Reference to .spikes/ code** for HIGH risk items
- **Clear acceptance criteria**
- **File scope** for track assignment

### Example Bead with Learnings

```markdown
# Implement Stripe webhook handler

## Context

Spike bd-12 validated: Stripe SDK works with our Node version.
See `.spikes/billing-spike/webhook-test/` for working example.

## Learnings from Spike

- Must use `stripe.webhooks.constructEvent()` for signature verification
- Webhook secret stored in `STRIPE_WEBHOOK_SECRET` env var
- Raw body required (not parsed JSON)

## Acceptance Criteria

- [ ] Webhook endpoint at `/api/webhooks/stripe`
- [ ] Signature verification implemented
- [ ] Events: `checkout.session.completed`, `invoice.paid`
```

## Phase 5: Validation

### Dependency Ordering Rules

**Stack dependencies flow downward**: Database → Backend → Frontend

| If task does...              | It MUST be blocked by...                     |
| ---------------------------- | -------------------------------------------- |
| Frontend calls API endpoint  | Backend task implementing that endpoint      |
| Backend reads/writes DB      | Database migration/schema task               |
| Integration/E2E tests        | Both frontend AND backend tasks it exercises |
| UI displays data from API    | Backend task that provides that data         |

**Example**: "Add user list page" (frontend) is blocked by "Create GET /api/users endpoint" (backend)

```bash
# Correct dependency direction
bd dep add frontend-user-list backend-users-endpoint

# WRONG - frontend cannot be worked on until backend exists
# bd dep add backend-users-endpoint frontend-user-list  # inverted
```

### Run bv Analysis

```bash
bv --robot-suggest   # Find missing dependencies
bv --robot-insights  # Detect cycles, bottlenecks
bv --robot-priority  # Validate priorities
```

### Verify Stack Dependencies

After running `bv --robot-suggest`, manually verify:

1. **Every frontend task that calls an API** → blocked by that API's backend task
2. **Every backend task using new schema** → blocked by the migration task
3. **No frontend tasks** can start before their required backend tasks

### Fix Issues

```bash
bd dep add <from> <to>      # Add missing deps
bd dep remove <from> <to>   # Break cycles
bd update <id> --priority X # Adjust priorities
```

### Oracle Final Review

```
Task(
  subagent_type="Oracle",
  prompt="Review plan completeness and clarity.
          Context: Plan ready. Check for gaps, unclear beads, missing deps.
          Read .beads/ directory for all bead files."
)
```

## Phase 6: Track Planning (REQUIRED — orchestrator cannot run without this)

**Without `execution-plan.md`, the orchestrator has no tracks to assign. Your planning work is wasted until this file is committed.**

### Step 1: Get Parallel Tracks

```bash
bv --robot-plan 2>/dev/null | jq '.plan.tracks'
```

### Step 2: Assign File Scopes

For each track, determine the file scope based on beads in that track:

```bash
# For each bead, check which files it touches
bd show <bead-id>  # Look at description for file hints
```

**Rules:**

- File scopes must NOT overlap between tracks
- Use glob patterns: `packages/sdk/**`, `apps/server/**`
- If overlap unavoidable, merge into single track
- **Backend tracks before frontend tracks**: If frontend beads consume APIs from backend beads, backend must complete first (add cross-track deps)

### Step 3: Generate Agent Names

Assign unique adjective+noun names to each track:

- BlueLake, GreenCastle, RedStone, PurpleBear, etc.
- Names are memorable identifiers, NOT role descriptions

### Step 4: Create Execution Plan

Save to `history/<feature>/execution-plan.md` using the template at `templates/execution-plan.md`.

### Step 5: Validate Tracks

```bash
# No cycles in the graph
bv --robot-insights 2>/dev/null | jq '.Cycles'

# All beads assigned to tracks
bv --robot-plan 2>/dev/null | jq '.plan.unassigned'
```

## Phase 7: Artifact Verification (MANDATORY — final step)

**Run this check before declaring the plan complete:**

```bash
# Verify all required artifacts exist
ls history/<feature>/discovery.md
ls history/<feature>/approach.md
ls history/<feature>/execution-plan.md
ls .beads/*.md
```

**If ANY file is missing, go back to the relevant phase and create it.**
**Do NOT report plan completion with missing artifacts.**

## Quick Reference

### Tool Selection

| Need               | Tool                                    |
| ------------------ | --------------------------------------- |
| Codebase structure | `mcp__gkg__repo_map`                    |
| Find definitions   | `mcp__gkg__search_codebase_definitions` |
| Find usages        | `mcp__gkg__get_references`              |
| External patterns  | `WebSearch`                             |
| Library docs       | `mcp__exa__get_code_context_exa`        |
| Gap analysis       | `Task(subagent_type="Oracle")`          |
| Create beads       | `Skill(skill="file-beads")` + `bd create` |
| Validate graph     | `bv --robot-*`                          |

### Common Mistakes

- **Skipping discovery** → Plan misses existing patterns
- **No risk assessment** → Surprises during execution
- **No spikes for HIGH risk** → Blocked workers
- **Missing learnings in beads** → Workers re-discover same issues
- **No bv validation** → Broken dependency graph
- **Frontend before backend** → Frontend tasks calling APIs must be blocked by the backend tasks that implement those APIs
- **Parallel tracks with API coupling** → If Track A (frontend) consumes Track B (backend) APIs, add cross-track dependencies
- **Stopping after beads are filed** → execution-plan.md is required for orchestrator
