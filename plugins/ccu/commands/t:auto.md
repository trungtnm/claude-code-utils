---
description: Work the backlog autonomously as a single agent, bead by bead
---

Work the backlog autonomously as a single agent. Proceed meticulously through your assigned beads, working systematically and tracking your progress via beads. When you're not sure what to do next, use the bv tool mentioned in AGENTS.md, CLAUDE.md to prioritize the best beads to work on next; pick the next one that you can usefully work on and get started. Multi-agent execution is not this command's job — that's what `/hdr-orchestrator` and `/orchestrator` are for. Use /effort max.

## Steps

0. **Baseline and session branch** -- You work directly in the user's tree:

   ```bash
   git rev-parse --short HEAD       # note the baseline commit before you start
   git status --porcelain           # if the tree is dirty, tell the user before you begin
   ```

   **Never work or commit directly on `main`/`master`.** Check the current branch and branch off if needed:

   ```bash
   current=$(git rev-parse --abbrev-ref HEAD)
   if [ "$current" = "main" ] || [ "$current" = "master" ]; then
     git checkout -b "auto/$(date +%Y%m%d-%H%M)"   # session branch off the default branch
   fi
   ```

   - If you're already on a non-default branch, **stay on it**.
   - Report the session branch name to the user along with the baseline commit.

0.1. **Load project context** -- Before doing anything else, build situational awareness by reading (skip any that don't exist):
   - `CLAUDE.md` or `AGENTS.md` — project conventions, rules, architecture, coding patterns
   - `README.md` — what the project is, tech stack, how it works
   - `.ccu/DECISIONS.md` and `.ccu/EVIDENCE.md` — recent architectural decisions and completed-bead evidence
   - `.ccu/HANDOFF.md` — most recent handoff, if the last session paused mid-work
   - `.ccu/CAPTURES.md` — pending ideas
   - `git log --oneline -15` — recent activity and direction
   This context shapes how you implement every bead. Without it, you risk writing code that violates project conventions or duplicates existing work.

0.2. **Load procedural memory** -- Query CM for relevant rules and anti-patterns (skip if `cm` is not installed):
   ```bash
   cm context "general development" --json --limit 10 2>/dev/null
   ```
   If CM returns results, keep the `relevantBullets` and `antiPatterns` in mind throughout the session. Reference rule IDs (e.g., "Following b-8f3a2c...") when a rule influences your decisions. This is how the team's accumulated knowledge flows into your work.

1. **Assess work** -- Use `bv` (Beads Viewer) to survey the backlog and identify the highest-priority beads you can usefully work on. If no beads exist, check `.ccu/CAPTURES.md` for untriaged items and process them.

2. **Pick and start** -- Pick the next bead using `br ready --json 2>/dev/null` (which returns only unblocked beads with all dependencies met). Then claim it with `br update <id> --status in_progress`.

   **Verify bead state before acting.** Before starting work on a bead:
   - Run `br show <id> --json 2>/dev/null` to confirm it's still open/ready (a previous session may have closed it)
   - If the bead is already closed, **skip it** and pick the next ready bead

   **Respect the dependency graph.** If `br` returns an error like `"cannot claim blocked issue"`, that bead has unmet dependencies. Do NOT work on it or "prepare code ahead." Instead:
   - Run `br show <id> --json 2>/dev/null` to see which bead is blocking it
   - Either work on the blocker first, or pick a different ready bead
   - If ALL remaining beads are blocked by unmet dependencies, stop and report the blocked graph to the user

3. **Execute** -- Work through the bead's requirements systematically and meticulously. Track progress with bead comments and status updates.

   **Commit discipline:** one commit per bead with the bead id in the message; stage your named files and commit with a pathspec so unrelated in-progress files are never swept in:
   ```bash
   git add <your files> && git commit -m "<type>(<scope>): <description> [<bead-id>]" -- <your files>
   ```

4. **Capture decisions** -- If you made technology, schema, API, or architecture choices during this bead, append each as a new `##` section to `.ccu/DECISIONS.md` (create the file if it doesn't exist):
   - Include date, context, decision, rationale, and alternatives considered.
   - Don't defer all decision documentation to `/t:audit-decisions` — capture the obvious ones inline while the context is fresh.

   Also append evidence for completed beads to `.ccu/EVIDENCE.md` (one `##` section per bead) with commit hash, files changed, and verification results.

5. **Record outcome** -- After completing a bead, record the outcome so CM can learn from it (skip if `cm` is not installed):
   ```bash
   cm outcome success <rule-ids-that-helped> 2>/dev/null   # or 'failure' if bead was blocked
   ```
   If any CM rules were particularly helpful or harmful during the bead, leave inline feedback:
   ```bash
   cm mark <bullet-id> --helpful 2>/dev/null
   cm mark <bullet-id> --harmful --reason "<why>" 2>/dev/null
   ```

6. **Loop** -- When a bead is complete:
   a. Re-check bead state with `br show <id> --json 2>/dev/null` — if it's somehow already closed, skip closing (don't treat "already closed" as an error, just move on)
   b. If still open, close it with `br close <id> --reason "..."`
   c. Sync beads (`br sync --flush-only 2>/dev/null`)
   d. Return to step 1. Repeat until no actionable work remains.

   If every remaining bead is blocked by an unmet dependency, stop and report the blocked graph to the user — there is no one else working the backlog, so waiting cannot unblock anything.

7. **Wrap up the session** -- When no actionable work remains:

    a. **Commit bead state**:
       ```bash
       br sync --flush-only            # export shared DB → .beads/issues.jsonl (do NOT hide errors here — a failed flush must not be committed silently)
       git add .beads/ && git commit -m "chore(beads): sync session state" -- .beads/   # skip if nothing changed
       ```
    b. Confirm nothing you worked on is left uncommitted: `git status --porcelain` — every completed bead should already have its own commit from step 3.
    c. Report the session summary to the user: beads completed (per-bead ✓/✗ with commit hashes), beads left open/blocked, the session branch name, and the commit range (`<baseline>..HEAD`). Your commits live on the session branch, not `main` — whether to push, open a PR, or merge back into `main` is the user's call; do not push or merge without being asked.

## Rules

- **Fully autonomous** -- Never ask the user for permission to continue or proceed to the next bead. You decide what to work on and when. The only reason to stop is when all beads are done, all remaining beads are blocked, or you hit a genuine ambiguity that requires human input (not "should I keep going?").
- **Track everything** -- Every task you work on must have a bead. Update status and add comments as you go.
- **Use bv for prioritization** -- When uncertain what to do next, run bv to find the highest-value ready beads.
- **Never bypass blocked beads** -- If a bead is blocked, it is blocked for a reason (unmet dependency). Working "ahead" on blocked beads creates wasted effort and dependency violations. Work on the blocker or pick something else.
- **Never commit on `main`/`master`** -- All work happens on a session branch (Step 0). If you ever find yourself on the default branch mid-session (e.g. someone switched branches externally), stop and re-run the Step 0 branch check before committing anything.
- **Commit per bead, named paths only** -- One commit per bead with the bead id in the message; stage named files and commit with a pathspec (never `git add -A`) so unrelated files are never swept into your commit.
- **Bead comments are a point-in-time audit trail, NOT ground truth for PR/branch/merge state** -- Before reporting that a PR is open or merged (or a branch landed), confirm against git/GitHub — `gh pr view <n> --json state,mergedAt`, `gh pr list --head <branch>`, `git log --oneline <branch>`. Never repeat a comment's PR claim as current fact; if you can't confirm, report it as unverified.
- **Use /effort max** -- Apply maximum effort to all work.
