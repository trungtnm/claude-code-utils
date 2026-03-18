---
name: recipe
description: >-
  Pre-built workflow sequences for common development patterns. Chains ccu commands
  in the right order, skipping completed phases. Use for new-feature, bug-fix,
  refactor, or spike workflows. Triggers on recipe, workflow, new feature pipeline,
  bug fix workflow, guided development, end-to-end feature.
domain: project-management
role: guide
triggers:
  - recipe
  - workflow
  - new feature
  - bug fix
  - refactor
  - spike
  - guided
  - end-to-end
---

# Workflow Recipes

One command to go from "I have an idea" to "it's shipped." Each recipe chains ccu commands in the optimal order, checking prerequisites and skipping completed phases.

## Available Recipes

### new-feature

Full lifecycle for a new feature from idea to shipped.

**Sequence:**
1. **Discuss** — `/t:discuss` for requirements gathering
   - Skip if: `.ccu/REQUIREMENTS.md` already has requirements for this feature
2. **Plan** — `/planning` to decompose into beads
   - Skip if: beads already exist for this feature (check `br list`)
3. **Review beads** — `/review-beads` to optimize before work
   - Skip if: beads have already been reviewed (check bead comments for review notes)
4. **Execute** — `/t:auto` for single-agent or `/orchestrator` for multi-agent
   - Skip completed beads automatically
5. **Quality** — `/t:peer-review` + `/ubs` for quality gates
6. **Wrap up** — `/t:commit` + `/t:done`

### bug-fix

Fast path for diagnosing and fixing a bug.

**Sequence:**
1. **Understand** — Read the bug report (from `$ARGUMENTS` or ask user)
2. **Investigate** — Use `/t:rootfix` approach to find root cause
3. **Track** — Create bead if one doesn't exist:
   ```bash
   br create --actor "$ACTOR" "Fix: {summary}" --type bug --priority 1
   ```
4. **Fix** — Implement with TDD (RED: write failing test for the bug, GREEN: fix, REFACTOR)
5. **Verify** — Run tests, lint, typecheck. Record evidence to `.ccu/EVIDENCE.md`
6. **Commit** — `/t:commit` with enriched Context: section
7. **Close** — Close bead and sync

### refactor

Safe refactoring with verification gates.

**Sequence:**
1. **Scope** — Clarify refactor scope (from `$ARGUMENTS` or `/t:discuss`)
2. **Baseline** — Snapshot current test results: `npm test 2>&1 | tail -10`
3. **Track** — Create bead:
   ```bash
   br create --actor "$ACTOR" "Refactor: {scope}" --type task --labels refactor
   ```
4. **Implement** — Refactor in small committed increments
5. **Verify after each increment** — re-run tests, ensure no regressions vs baseline
6. **Evidence** — Record to `.ccu/EVIDENCE.md`
7. **Commit** — `/t:commit`

### spike

Time-boxed investigation to answer a technical question.

**Sequence:**
1. **Frame the question** — from `$ARGUMENTS` or ask user
2. **Track** — Create spike bead:
   ```bash
   br create --actor "$ACTOR" "Spike: {question}" --type task --labels spike --priority 1
   ```
3. **Time box** — Set expectation: ~30 minutes max
4. **Investigate** — Read code, run experiments, check docs, try approaches
5. **Record findings** — Append to `.ccu/DECISIONS.md`:
   ```markdown
   ## D{N} — Spike: {question}
   - **date:** {today}
   - **decision:** {answer/recommendation}
   - **rationale:** {evidence from investigation}
   - **alternatives:** {other options considered}
   ```
6. **Close** — `br close {ID} --reason "Finding: {one-line answer}"`
7. **Present** — Summarize findings and recommend next steps

### hotfix

Emergency fast path when production is down. Skip all ceremony — just fix and ship.

**Sequence:**
1. **Understand** — Read the error from `$ARGUMENTS`
2. **Fix** — Implement the fix. Write a regression test if time permits, but the fix takes priority.
3. **Verify** — Run tests + typecheck. This step is mandatory, no skip.
4. **Commit + Push** — `hotfix: {summary}` prefix. Push immediately.
5. **Track retroactively** — After the fix is live, create a bead:
   ```bash
   br create --actor "$ACTOR" "Hotfix: {summary}" --type bug --priority 0
   br close --actor "$ACTOR" {ID} --reason "Hotfix deployed"
   ```

No bead creation before the fix. No evidence logging. No TDD requirement. No peer review. Speed and correctness only.

## How to Use

```
/recipe                                           # Ask which recipe to run
/recipe new-feature                               # Full lifecycle pipeline
/recipe bug-fix auth crash on login               # Bug fix with context
/recipe hotfix 500 error on /api/users endpoint   # Emergency, skip ceremony
/recipe refactor extract auth into middleware      # Safe refactor with baseline
/recipe spike "Can we use SQLite instead of Postgres?"
```

Everything after the recipe name is context that flows through all steps — it scopes the investigation, names the bead, and focuses the fix. Be specific: `/recipe bug-fix high priority, auth module, user reports 500 on login` is better than `/recipe bug-fix auth`.

If no recipe name is given, ask the user which workflow they want.

## Pre-Flight

Before executing step 1 of any recipe, verify the environment:

```
Pre-flight check:
- [ ] .ccu/ exists (create if not, warn if skipped)
- [ ] br CLI available (warn what will be skipped without it)
- [ ] git status clean (suggest commit or stash if dirty)
- [ ] Tests pass baseline (for refactor recipe only)
```

Report all issues at once. Do not block execution — inform what will be degraded and proceed unless the user says stop.

## Recipe Execution Rules

### Resume from Interruption

Before starting a recipe, check `.ccu/CHECKPOINT.md` for in-progress recipe state. If found:
- Report: "Found interrupted recipe: {name}, step {N}. Completed steps: {list}."
- Offer to resume at the interrupted step or start fresh.

To resume, skip all completed steps and continue from the interrupted step.

### Step Execution

For each step in the recipe:
1. **Check prerequisites** — is the step's input available?
2. **Check skip condition** — is this step already done?
3. **If skipped** — report: "Skipping step N ({name}) — already completed"
4. **If not skipped** — execute the step
5. **Write checkpoint** — update `.ccu/CHECKPOINT.md` with recipe state:
   ```
   recipe: {name}
   step: {current step number}
   completed: [{list of completed step numbers}]
   context: {$ARGUMENTS}
   ```
6. **On failure** — stop, report what happened, suggest fix

## Graceful Degradation

- **No `br`** — skip bead creation/tracking, use git commits as tracking
- **No `.ccu/`** — skip checkpoint and evidence steps, still chain the commands
- **No Agent Mail** — use `/t:auto` instead of `/orchestrator`
