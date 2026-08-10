---
description: Work the backlog autonomously as a single agent, bead by bead
---

Work the backlog autonomously as a single agent: pick the best ready bead, implement it, commit, close, repeat. Use `bv` to prioritize when the next bead is not obvious. Multi-agent execution belongs to `/orchestrator`, not here. Use /effort max.

## Steps

0. **Baseline and session branch** — you work directly in the user's tree:

   ```bash
   git rev-parse --short HEAD       # baseline commit
   git status --porcelain           # dirty tree → tell the user before starting
   ```

   Never work or commit on `main`/`master`. On the default branch, branch off first:

   ```bash
   current=$(git rev-parse --abbrev-ref HEAD)
   if [ "$current" = "main" ] || [ "$current" = "master" ]; then
     git checkout -b "auto/$(date +%Y%m%d-%H%M)"
   fi
   ```

   Already on a non-default branch: stay on it. Report the session branch and baseline to the user. If you find yourself back on the default branch mid-session, redo this step before committing anything.

1. **Load context** — read, skipping any that do not exist: `CLAUDE.md`/`AGENTS.md`, `README.md`, `CONTEXT.md` + a scan of `docs/adr/`, `git log --oneline -15`, and the unchecked count of `.ccu/CAPTURES.md` (the session-start read set in [[session-state]]). Do not load `.ccu/DECISIONS.md`; grep it when a specific "why" question arises and treat what it returns per the epistemics rule in [[session-state]]. If `cm` is installed, load procedural memory — `cm context "general development" --json --limit 10` — and keep the returned rules and anti-patterns in mind, referencing rule IDs when one shapes a decision.

2. **Pick and claim** — `br ready --json` lists unblocked beads; `bv` ranks them. Confirm the candidate is still open with `br show <id> --json` (a previous session may have closed it — skip closed ones), then claim it: `br update <id> --status in_progress`. A `cannot claim blocked issue` error means unmet dependencies: work the blocker or pick another ready bead; never prepare code ahead on a blocked bead. If no beads exist, triage `.ccu/CAPTURES.md`.

3. **Execute** — implement the bead's requirements; track progress with bead comments and status updates. When evidence forces a deviation from the bead's plan (its `## Files`, `## Interfaces`, or technical notes turn out wrong or incomplete), pick the conservative option, keep going, and log it — `br comments add <id> "Deviation: <what> — <why>"` — so the plan's gap is visible instead of silently absorbed. One commit per bead, bead id in the message, named paths with a pathspec so unrelated in-progress files are never swept in (never `git add -A`):

   ```bash
   git add <your files> && git commit -m "<type>(<scope>): <description> [<bead-id>]" -- <your files>
   ```

4. **Record** — for each technology, schema, API, or architecture choice made during the bead: if it meets the ADR gate, write `docs/adr/NNNN-slug.md` and add a one-line pointer entry to `.ccu/DECISIONS.md`; otherwise append a journal entry in the shared schema. Both the gate and the schema are defined in [[session-state]] (promote rule). The bead's close reason and commit carry the completion evidence — no separate evidence file. If `cm` is installed, record the outcome (`cm outcome success|failure <rule-ids>`) and mark notably helpful or harmful rules (`cm mark <bullet-id> --helpful` / `--harmful --reason "<why>"`).

5. **Loop** — re-check with `br show <id> --json` (already closed → move on, not an error), close with `br close <id> --reason "..."`, sync with `br sync --flush-only`, and return to step 2. When every remaining bead is blocked by an unmet dependency, stop and report the blocked graph — no one else is working the backlog, so waiting cannot unblock anything.

6. **Wrap up** — when no actionable work remains:

   ```bash
   br sync --flush-only             # do NOT hide errors — a failed flush must not be committed silently
   git add .beads/ && git commit -m "chore(beads): sync session state" -- .beads/   # skip if nothing changed
   git status --porcelain           # nothing you worked on stays uncommitted
   ```

   Report per-bead ✓/✗ with commit hashes, beads left open or blocked, the session branch, and the range `<baseline>..HEAD`. Pushing, opening a PR, or merging is the user's call; do not do it unasked.

## Rules

- Never ask permission to continue or to start the next bead. Stop only when all work is done, everything remaining is blocked, or a genuine ambiguity needs human input.
- Every task gets a bead; update status and comments as you go.
- Bead comments are a point-in-time audit trail, not ground truth for PR/branch/merge state. Confirm against git or GitHub (`gh pr view <n> --json state,mergedAt`, `gh pr list --head <branch>`, `git log --oneline <branch>`) before reporting such state; if you cannot confirm, report it as unverified.
