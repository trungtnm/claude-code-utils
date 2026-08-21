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

When running in Codex, read [the Codex compatibility rules](../../CODEX.md)
before starting. Every `/name` reference below means the installed skill of that
name, which Codex invokes as `$name`.

One command to go from "I have an idea" to "it's shipped." Each recipe chains ccu workflows in the optimal order, checking prerequisites and skipping completed phases.

## Available Recipes

### new-feature

Full lifecycle for a new feature from idea to shipped.

**Sequence:**
1. **Discuss** — `/discuss` for requirements gathering
   - Skip if: open beads already cover this feature's requirements (check `br list`)
2. **Plan** — `/plan-beads` to decompose into beads
   - Skip if: beads already exist for this feature (check `br list`)
3. **Review beads** — `/review-beads` to optimize before work
   - Skip if: beads have already been reviewed (check bead comments for review notes)
4. **Execute** — `/auto` for self-scheduling agents (one terminal or several) or `/orchestrator` for a dispatched epic with tester and reviewer phases
   - Skip completed beads automatically
5. **Quality** — `/peer-review` + `/ubs` for quality gates
6. **Wrap up** — `/commit` + `/done`

### bug-fix

Fast path for diagnosing and fixing a bug.

**Sequence:**
1. **Understand** — Read the bug report (from `$ARGUMENTS` or ask user)
2. **Investigate** — Use `/rootfix` approach to find root cause
3. **Track** — Create bead if one doesn't exist:
   ```bash
   br create --actor "$ACTOR" "Fix: {summary}" --type bug --priority 1
   ```
4. **Fix** — Implement with TDD (RED: write failing test for the bug, GREEN: fix, REFACTOR)
5. **Verify** — Run the ladder in [[gates]]. Record the results in the bead's close reason (and the commit message)
6. **Commit** — `/commit` with enriched Context: section
7. **Close** — Close bead and sync

### refactor

Safe refactoring with verification gates.

**Sequence:**
1. **Scope** — Clarify refactor scope (from `$ARGUMENTS` or `/discuss`)
2. **Baseline** — Snapshot the suite covering the refactor target, not the whole repo — the scope [[gates]] stage 2 defines. A refactor is judged against that snapshot
3. **Track** — Create bead:
   ```bash
   br create --actor "$ACTOR" "Refactor: {scope}" --type task --labels refactor
   ```
4. **Implement** — Refactor in small committed increments
5. **Verify after each increment** — re-run tests, ensure no regressions vs baseline
6. **Evidence** — Record verification results in the bead's close reason and the commit message
7. **Commit** — `/commit`

### hotfix

Emergency fast path when production is down. Skip all ceremony — just fix and ship.

**Sequence:**
1. **Understand** — Read the error from `$ARGUMENTS`
2. **Fix** — Implement the fix. Write a regression test if time permits, but the fix takes priority.
3. **Verify** — Run the ladder in [[gates]]. This step is mandatory, no skip.
4. **Commit + Push** — `hotfix: {summary}` prefix. Push immediately.
5. **Track retroactively** — After the fix is live, create a bead:
   ```bash
   br create --actor "$ACTOR" "Hotfix: {summary}" --type bug --priority 0
   br close --actor "$ACTOR" {ID} --reason "Hotfix deployed"
   ```

No bead creation before the fix. No evidence logging. No TDD requirement. No peer review. Speed and correctness only.

### quality-review

Three-layer quality sweep with issue accumulator: find bugs, catch session mistakes, polish the experience, then fix everything before committing.

**Critical: review window includes committed work.** Recipes like `/auto` commit as they go, so by the time `quality-review` runs, the working tree is often clean. The recipe MUST review everything produced during the session — both committed and uncommitted — not just `git diff` against HEAD. Step 0 below computes that window once and feeds it into every subsequent step.

**Issue Accumulator:** Maintain a running markdown checklist of all issues found but NOT fixed across steps. Initialize as empty at recipe start. After each step, append any unfixed issues with their source step and severity:
```markdown
## Accumulated Unfixed Issues
- [ ] [peer-review/HIGH] Missing null check in parseConfig() — src/config.ts:42
- [ ] [fresh-eyes/MEDIUM] Duplicated validation logic between routes — src/api/auth.ts, src/api/users.ts
- [ ] [ubs/LOW] Unused import — src/utils.ts:3
```

**Sequence:**

0. **Compute review window** — Resolve a baseline commit and the file list to review. Run this once before any review step; export `REVIEW_BASE` and `REVIEW_FILES` for the rest of the recipe.

   ```bash
   # 1. Pick a baseline (most specific wins)
   if [ -n "$CCU_REVIEW_BASE" ]; then
     REVIEW_BASE="$CCU_REVIEW_BASE"                                # explicit override
   elif main_ref=$(git rev-parse --verify --quiet origin/main || git rev-parse --verify --quiet main); then
     REVIEW_BASE=$(git merge-base "$main_ref" HEAD)                # branch base
   else
     REVIEW_BASE=$(git log --since='2 hours ago' --pretty=format:%H | tail -1)
   fi

   # 2. Files changed in committed range + files dirty in working tree
   #    --diff-filter=ACMR drops deletions (no point scanning files that no longer exist)
   COMMITTED=$(git diff --name-only --diff-filter=ACMR "$REVIEW_BASE"...HEAD 2>/dev/null)
   WORKTREE=$(git diff --name-only --diff-filter=ACMR 2>/dev/null)
   UNTRACKED=$(git ls-files --others --exclude-standard 2>/dev/null)

   REVIEW_FILES=$(printf '%s\n%s\n%s\n' "$COMMITTED" "$WORKTREE" "$UNTRACKED" \
     | sort -u | grep -v '^$' | grep -Ev '^(node_modules|dist|build|\.next|target)/' )

   # 3. Comma-joined form for tools that take --files=
   REVIEW_FILES_CSV=$(printf '%s' "$REVIEW_FILES" | paste -sd, -)
   ```

   - If `REVIEW_FILES` is empty AND working tree is clean AND there are no commits since `REVIEW_BASE`: report "Nothing produced this session — skipping quality-review" and exit. This is the only legitimate empty-scan path.
   - Otherwise, proceed. Report: "Reviewing {N} files against baseline {short-sha}."

1. **Peer review** — `/peer-review {$ARGUMENTS}` for deep bug/logic/security analysis
   - Pass `REVIEW_FILES` as the explicit scope so peer-review covers committed work, not just dirty files
   - Skip if: `REVIEW_FILES` is empty
   - After: append any issues found but not fixed to the accumulator
2. **Fresh eyes** — `/fresh-eyes` to re-read session changes with a fresh perspective
   - Pass `REVIEW_FILES` as the explicit scope
   - Skip if: `REVIEW_FILES` is empty
   - After: append any issues found but not fixed to the accumulator
3. **Polish** — `/polish {$ARGUMENTS}` for UI/UX refinement
   - Skip if: project has no UI (pure CLI tool, library, or backend-only) OR `REVIEW_FILES` contains no UI files
   - After: append any issues found but not fixed to the accumulator
4. **Run UBS** — static analysis gate over the full review window, not just `--diff`:
   ```bash
   if command -v ubs >/dev/null && [ -n "$REVIEW_FILES_CSV" ]; then
     ubs --files="$REVIEW_FILES_CSV" --format=toon
   fi
   ```
   - Do **NOT** use `ubs --diff` here — it only sees the working tree, missing all committed work from this session.
   - Skip if: `ubs` not installed OR `REVIEW_FILES_CSV` is empty.
   - If ubs reports "nothing to scan" despite `REVIEW_FILES_CSV` being non-empty, that's a bug — surface it to the user rather than silently passing.
   - After: append any findings to the accumulator (exclude false positives).
5. **Final fix pass** — Review the full accumulated issues list. If no unfixed issues remain, skip this step.
   - Present the complete accumulator to the user with a summary: "{N} unfixed issues from {steps}."
   - Fix ALL issues that are fixable. Work through them systematically, highest severity first.
   - For issues that genuinely cannot or should not be fixed (false positives, intentional tradeoffs, out of scope), the user can explicitly defer them by marking with `[deferred: reason]`.
   - After fixing, re-run only the stages [[gates]] scopes to the affected files.
   - Repeat until the accumulator contains only deferred items or is empty.
6. **Commit fixes** — `/commit` if any fixes were made

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

When the recipe's last step completes, **delete `.ccu/CHECKPOINT.md`**. The checkpoint exists only to resume an interrupted recipe; one that outlives its recipe reads as a phantom interruption on the next run ([[session-state]] owns this file's role).

## Graceful Degradation

- **No `br`** — skip bead creation/tracking, use git commits as tracking
- **No `.ccu/`** — skip checkpoint and evidence steps, still chain the commands
- **No Agent Mail** — `/orchestrator` cannot dispatch; run a single `/auto`, which says so once and works alone
