---
name: recipe
description: >-
  Pre-built workflow sequences for common development patterns. Chains ccu commands
  in the right order, skipping completed phases. Use for new-feature, bug-fix,
  refactor, hotfix, or quality-review workflows. Triggers on recipe, workflow,
  new feature pipeline, bug fix workflow, guided development, end-to-end feature.
domain: project-management
role: guide
triggers:
  - recipe
  - workflow
  - new feature
  - bug fix
  - refactor
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

### quality-review

Three-layer quality sweep with issue accumulator: find bugs, catch session mistakes, polish the experience, then fix everything before committing.

**Issue Accumulator:** Maintain a running markdown checklist of all issues found but NOT fixed across steps. Initialize as empty at recipe start. After each step, append any unfixed issues with their source step and severity:
```markdown
## Accumulated Unfixed Issues
- [ ] [peer-review/HIGH] Missing null check in parseConfig() — src/config.ts:42
- [ ] [fresh-eyes/MEDIUM] Duplicated validation logic between routes — src/api/auth.ts, src/api/users.ts
- [ ] [ubs/LOW] Unused import — src/utils.ts:3
```

**Sequence:**
1. **Peer review** — `/t:peer-review {$ARGUMENTS}` for deep bug/logic/security analysis
   - Skip if: no code changes exist (clean git status and no session changes)
   - After: append any issues found but not fixed to the accumulator
2. **Fresh eyes** — `/t:fresh-eyes` to re-read session changes with a fresh perspective
   - Skip if: no files were modified in this session
   - After: append any issues found but not fixed to the accumulator
3. **Polish** — `/t:polish {$ARGUMENTS}` for UI/UX refinement
   - Skip if: project has no UI (pure CLI tool, library, or backend-only)
   - After: append any issues found but not fixed to the accumulator
4. **Run UBS** — `ubs --diff --format=toon` as final static analysis gate
   - Skip if: `ubs` not installed
   - After: append any findings to the accumulator (exclude false positives)
5. **Final fix pass** — Review the full accumulated issues list. If no unfixed issues remain, skip this step.
   - Present the complete accumulator to the user with a summary: "{N} unfixed issues from {steps}."
   - Fix ALL issues that are fixable. Work through them systematically, highest severity first.
   - For issues that genuinely cannot or should not be fixed (false positives, intentional tradeoffs, out of scope), the user can explicitly defer them by marking with `[deferred: reason]`.
   - After fixing, re-run verification for the affected files: tests, lint, typecheck as applicable.
   - Repeat until the accumulator contains only deferred items or is empty.
6. **Commit fixes** — `/t:commit` if any fixes were made

## How to Use

```
/recipe                                           # Ask which recipe to run
/recipe new-feature                               # Full lifecycle pipeline
/recipe bug-fix auth crash on login               # Bug fix with context
/recipe hotfix 500 error on /api/users endpoint   # Emergency, skip ceremony
/recipe refactor extract auth into middleware      # Safe refactor with baseline
/recipe quality-review                            # Three-layer quality sweep
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
