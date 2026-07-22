---
name: plan-beads
description: Use when asked to plan a feature, create a roadmap, or design an implementation approach. Triggers on requests for comprehensive plans, feature decomposition, or multi-phase implementation strategies.
---

# Feature Planning Pipeline

Generate quality plans through systematic discovery, synthesis, and decomposition.

## IMPORTANT: Execution Mode

**This skill replaces Claude Code's built-in planning.** When this skill is active:

- Do **NOT** use `EnterPlanMode` — this skill IS the plan mode
- Do **NOT** use `TaskCreate`, `TaskUpdate`, or `TaskList` — use beads (`br`) for task tracking instead
- Do **NOT** ask the user to approve a plan before executing — just run the pipeline phases sequentially
- Do **NOT** pause between phases to ask "should I continue?" — proceed through all 7 phases automatically
- The only user interaction should be `AskUserQuestion` when genuine ambiguity exists (e.g., choosing between approach options in Phase 2)

## Pipeline Overview

```
USER REQUEST → Discovery → Synthesis → Decomposition → Bead Review → Validation → Execution Planning → Artifact Check → Ready Plan
```

| Phase                 | Tool                                     | Output                              |
| --------------------- | ---------------------------------------- | ----------------------------------- |
| 1. Discovery          | Parallel Task(Explore), gkg              | Discovery Report                    |
| 2. Synthesis          | Task(Oracle)                             | Approach + Risk Map                 |
| 3. Decomposition      | file-beads skill                         | .beads/\*.md files                  |
| 4. Bead Review        | review-beads skill                       | Optimized, self-documented beads    |
| 5. Validation         | bv + bv --robot-triage + Task(Oracle)    | Validated dependency graph          |
| 6. Execution Planning | bv --robot-plan + br ready               | Bead-level execution plan           |
| 7. Artifact Check     | Verify all files exist                   | Confirmed complete plan             |

## Artifact Naming Convention

All planning artifacts live under `.ccu/artifacts/` in a per-feature subdirectory for easy retrospection:

```
.ccu/artifacts/<date>-<epic-id>-<slug>/
```

| Component    | Format         | Example            |
| ------------ | -------------- | ------------------ |
| `<date>`     | `YYYY-MM-DD`   | `2026-02-27`       |
| `<epic-id>`  | beads epic ID  | actual ID from `br create` (e.g., `a03`) |
| `<slug>`     | kebab-case title (3-5 words max) | `stripe-billing-integration` |

**Full example:** `.ccu/artifacts/2026-02-27-a03-stripe-billing/` (use the real bead ID assigned by `br`)

**Rules:**
- Date is the day planning **starts** (not when it finishes)
- Epic ID comes from the beads epic created during decomposition (Phase 3) — if unknown at Phase 1, use a placeholder like `draft` and rename the directory after the epic is created
- Slug should be meaningful enough to identify the feature at a glance in `ls .ccu/artifacts/`
- Use `<dir>` as shorthand in subsequent phases once the directory is established
- If brainstorming created a `<date>-draft-<slug>/design.md` already, reuse that directory and rename it at Phase 3 once the epic ID is known: `mv .ccu/artifacts/<date>-draft-<slug> .ccu/artifacts/<date>-<epic-id>-<slug>`

`.ccu/artifacts/` is gitignored — these are local working files, not part of the project's permanent record. Durable context belongs in commit messages, `.ccu/DECISIONS.md`, and bead descriptions.

**Browsable index:** after writing or updating any doc in the artifacts directory, regenerate its HTML viewer so the plan reads as one switchable page (discovery → approach → execution-plan) with live Mermaid and TOCs:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/markdown-html-viewer/scripts/md2html.py" .ccu/artifacts/<dir>/
```

Directory + default fetch mode → one `index.html` with a document switcher, each `.md` staying a live source. Do **not** ask the user how to build it — this automated case is the documented exception. See the "Artifacts HTML index" convention in [[session-state]].

## Completion Gate (MANDATORY)

**You are NOT done until ALL of these files exist:**

- [ ] `.ccu/artifacts/<dir>/discovery.md` (Phase 1)
- [ ] `.ccu/artifacts/<dir>/approach.md` (Phase 2)
- [ ] `.beads/*.md` decomposed work items (Phase 3)
- [ ] `.ccu/artifacts/<dir>/execution-plan.md` (Phase 6)

**After Phase 6, run Phase 7 to verify each file exists before reporting completion.**
**Missing ANY artifact = incomplete plan. Do not stop early.**

## Red Flags - You Are About to Skip Steps

- "Beads are filed, so the plan is done" → Beads without an execution plan force the orchestrator to re-analyze everything. File the execution plan.
- "The orchestrator can figure out the schedule" → It dispatches from `br ready` at runtime, but the execution plan (per-bead file scopes, risks, sequencing caveats) is YOUR job. The orchestrator consumes execution-plan.md, it doesn't create it.
- "I'll come back to the execution plan later" → You won't. Do it now.
- "Discovery is obvious, I'll skip to synthesis" → Discovery catches patterns you'd miss. Run the parallel explorers.
- "Beads look fine, I'll skip review" → Plan space is cheap. Spending 2 minutes reviewing beads saves hours of worker confusion. Run Phase 4.
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

Save to `.ccu/artifacts/<dir>/discovery.md` using the template at `templates/discovery.md`.

## Phase 2: Synthesis (Oracle)

Feed Discovery Report to Oracle for gap analysis:

```
Task(
  subagent_type="Oracle",
  prompt="Analyze gap between current codebase and feature requirements.
          Context: Discovery report attached. User wants: <feature>.
          Read .ccu/artifacts/<dir>/discovery.md for context."
)
```

Oracle produces:

1. **Gap Analysis** - What exists vs what's needed
2. **Approach Options** - 1-3 strategies with tradeoffs
3. **Risk Assessment** - LOW / MEDIUM / HIGH per component

### Risk Classification

Risk ratings are **annotations**, not gates. They flag novelty so workers know where to investigate before coding. There is no separate verification phase — workers handle HIGH-risk items inline.

| Level  | Criteria                      | Worker Guidance                  |
| ------ | ----------------------------- | -------------------------------- |
| LOW    | Pattern exists in codebase    | Proceed using established pattern |
| MEDIUM | Variation of existing pattern | Sketch interface, type-check before deep implementation |
| HIGH   | Novel or external integration | Investigate before coding — read docs, test API surface, validate assumptions |

### Risk Indicators

```
Pattern exists in codebase? ─── YES → LOW base
                            └── NO  → MEDIUM+ base

External dependency? ─── YES → HIGH
                     └── NO  → Check blast radius

Blast radius >5 files? ─── YES → HIGH
                       └── NO  → MEDIUM
```

HIGH-risk components surface in two places:
1. The Risk Map section of `approach.md`
2. The bead description for any task touching that component, prefixed with `⚠ HIGH RISK: <reason>`

Save to `.ccu/artifacts/<dir>/approach.md` using the template at `templates/approach.md`.

## Phase 3: Decomposition (file-beads skill)

Load the file-beads skill and create beads with risk annotations baked in:

```
Skill(skill="file-beads")
```

If brainstorming created a `<date>-draft-<slug>/` directory, rename it now to use the real epic ID:

```bash
mv .ccu/artifacts/<date>-draft-<slug> .ccu/artifacts/<date>-<epic-id>-<slug>
```

### Bead Requirements

Each bead MUST include:

- **English throughout** — beads are always written in English, whatever language the planning conversation used (see the language rule in [[file-beads]]; quoted user-facing product copy is the only exception)
- **Risk annotation** for HIGH-risk items: `⚠ HIGH RISK: <one-line reason>` near the top of the description, with explicit "investigate before coding" guidance
- **Reference to discovery/approach docs** for context lineage: `See .ccu/artifacts/<dir>/approach.md` so workers can drill into tradeoffs if needed
- **Clear acceptance criteria**
- **File scope** (`## Files` block) — each worker reserves exactly these paths via Agent Mail before editing

### Example Bead with Risk Annotation

```markdown
# Implement Stripe webhook handler

⚠ HIGH RISK: External integration with Stripe webhooks — validate signature
verification and event payload shapes against the live SDK before assuming
TypeScript types match runtime behavior.

## Context

Adding webhook ingestion for the billing epic (a03). See
`.ccu/artifacts/2026-02-27-a03-stripe-billing/approach.md` for the chosen
approach and rejected alternatives.

## Investigate Before Coding

- Read Stripe SDK docs for `webhooks.constructEvent()` — does our Node version
  support the signature verification flow?
- Confirm webhook secret env var (`STRIPE_WEBHOOK_SECRET`) is wired through our
  config loader
- Verify our HTTP framework gives us access to the raw request body (not parsed JSON)

## Acceptance Criteria

- [ ] Webhook endpoint at `/api/webhooks/stripe`
- [ ] Signature verification implemented
- [ ] Events: `checkout.session.completed`, `invoice.paid`
```

## Phase 4: Bead Review (Plan Space Optimization)

**Principle: Plan space is cheap, implementation space is expensive.** Changing a bead description takes seconds. Changing implemented code takes hours. Invest time here to save orders of magnitude later.

Invoke the review-beads skill to optimize all filed beads:

```
Skill(skill="review-beads")
```

### Review Focus Areas

1. **Self-documentation quality** — Can a worker with zero context implement each bead?
2. **Optimality** — Is this the right decomposition? Right scope? Best for users?
3. **User value** — Does every bead earn its place by delivering value?
4. **Completeness** — Are project context, reasoning, and considerations present?

### Exit Criteria

- [ ] Every bead is self-contained (worker needs no external docs to start)
- [ ] Every bead includes project context and reasoning
- [ ] No bead exists "just because" — each earns its place
- [ ] Review report generated with changes made

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
br dep add frontend-user-list backend-users-endpoint

# WRONG - frontend cannot be worked on until backend exists
# br dep add backend-users-endpoint frontend-user-list  # inverted
```

### Run bv Analysis

```bash
bv --robot-suggest   # Find missing dependencies
bv --robot-insights  # Detect cycles, bottlenecks
bv --robot-priority  # Validate priorities
bv --robot-triage --graph-root <epic-id> 2>/dev/null | jq '.quick_ref'  # Triage summary
```

### Plan Health Check

Verify the plan is structurally sound before proceeding to execution planning:

```bash
br ready --json      # Confirm entry points exist (some issues are unblocked)
br stats --json      # Open/closed/blocked counts — sanity check
br blocked --json    # Catch unexpectedly blocked beads
```

If `br ready` returns empty, the dependency graph has no entry points — fix it before continuing.
If `br blocked` shows beads that shouldn't be blocked, investigate missing or incorrect dependencies.

### Verify Stack Dependencies

After running `bv --robot-suggest`, manually verify:

1. **Every frontend task that calls an API** → blocked by that API's backend task
2. **Every backend task using new schema** → blocked by the migration task
3. **No frontend tasks** can start before their required backend tasks

### Fix Issues

```bash
br dep add <from> <to>      # Add missing deps
br dep remove <from> <to>   # Break cycles
br update <id> --priority X # Adjust priorities
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

## Phase 6: Execution Planning (REQUIRED — orchestrator cannot run without this)

**Without `execution-plan.md`, the orchestrator has no map of the epic. Your planning work is wasted until this file is written.**

There are no tracks and no pre-assigned agents: the orchestrator spawns **one worker per bead**, dispatching whatever `br ready` returns and letting `bv` rank it. Your job here is to write down what the graph alone can't tell a dispatcher — per-bead file scopes, risks, and sequencing caveats.

### Step 1: Snapshot the Dependency Graph

```bash
bv --robot-plan 2>/dev/null | jq '.'          # parallel waves the graph allows
br ready --json                               # entry points — beads dispatchable on day one
```

### Step 2: Confirm Per-Bead File Scopes

Every bead's `## Files` block (from [[file-beads]]) is the worker's reservation list:

```bash
# For each bead, confirm the ## Files block is complete
br show <bead-id>
```

**Rules:**

- **Beads that can run in parallel** (no dependency path between them) **must have disjoint `## Files` sets** — overlapping files would make the second worker's Agent Mail reservation fail on arrival
- If two independent beads must touch the same file, add an explicit dependency (`br dep add`) so they are sequenced — never leave the collision for the reservation to catch
- **Backend before frontend**: if a frontend bead consumes an API from a backend bead, the dependency must exist in the graph

### Step 3: Create Execution Plan

Save to `.ccu/artifacts/<dir>/execution-plan.md` using the template at `templates/execution-plan.md` — a bead-level table (id, files, depends-on, risk), the entry points, and any sequencing caveats.

### Step 4: Validate the Graph

```bash
# No cycles in the graph
bv --robot-insights 2>/dev/null | jq '.Cycles'

# Entry points exist
br ready --json | jq 'length'   # must be > 0

# No two parallel-eligible beads share files (manual check against the plan table)
```

## Phase 7: Artifact Verification (MANDATORY — final step)

**Run this check before declaring the plan complete:**

```bash
# Verify all required artifacts exist
ls .ccu/artifacts/<dir>/discovery.md
ls .ccu/artifacts/<dir>/approach.md
ls .ccu/artifacts/<dir>/execution-plan.md
ls .beads/*.md

# Generate the browsable HTML index (switcher, fetch mode) as the final artifact
python3 "${CLAUDE_PLUGIN_ROOT}/skills/markdown-html-viewer/scripts/md2html.py" .ccu/artifacts/<dir>/
ls .ccu/artifacts/<dir>/index.html
```

**If ANY file is missing, go back to the relevant phase and create it.**
**Do NOT report plan completion with missing artifacts.** Point the user at `.ccu/artifacts/<dir>/index.html` — open it via `open_in_dev_browser.sh` (fetch pages don't double-click open).

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
| Create beads       | `Skill(skill="file-beads")` + `br create` |
| Validate graph     | `bv --robot-*`                          |

### Common Mistakes

- **Skipping discovery** → Plan misses existing patterns
- **No risk assessment** → Workers go in blind on novel work
- **Missing risk annotations in beads** → Workers don't know to investigate before coding
- **No bv validation** → Broken dependency graph
- **Frontend before backend** → Frontend tasks calling APIs must be blocked by the backend tasks that implement those APIs
- **Parallel beads with API coupling** → If bead A (frontend) consumes bead B's (backend) APIs, add the dependency
- **Parallel beads sharing files** → Overlapping `## Files` on independent beads means a guaranteed reservation conflict; sequence them with `br dep add`
- **Stopping after beads are filed** → execution-plan.md is required for orchestrator
- **Forgetting to rename `<date>-draft-<slug>/`** → Phase 3 must rename to use the real epic ID
