---
name: auto
description: Work the backlog autonomously, bead by bead — alone or as one interchangeable peer in a swarm
---

Work the backlog autonomously: pick the best ready bead, implement it, commit, close, repeat. Use `bv` to prioritize when the next bead is not obvious. Use /effort max.

You are a **fungible agent**: identical to every other `/auto` session on this repo, owning no domain and no role. Any peer can pick up any bead, including one you left in progress. Run this skill once and it is a solo agent; run it in N terminals and it is a swarm, with no change in behavior and no coordinator. [[orchestrator]] is the other multi-agent shape — one dispatcher, role-scoped subagents per bead — and it may be running in this same tree while you work.

Because every agent shares one working tree with no worktree isolation, **a file reservation is the only thing standing between you and a peer editing the same file**. Reserve before you edit. Follow [[agent-mail]] for the protocol; without the `mcp-agent-mail` server, say so once and work alone.

## Steps

0. **Register and find peers** — register with Agent Mail against the literal repo root, open your contact policy, and call `list_contacts()` per [[agent-mail]]. Filter out your own name. Report the peer count to the user in one line before going further; peers may include orchestrator workers whose reservations are live.

1. **Baseline and session branch** — you work directly in the user's tree:

   ```bash
   git rev-parse --short HEAD       # baseline commit
   git status --porcelain           # dirty tree → tell the user before starting
   ```

   Never work or commit on `main`/`master`. The branch is shared tree state, so decide by peer count:

   - **Peers active** — a peer already chose the branch. Stay on it. Never `git checkout` with peers active; you would move their tree out from under them mid-edit.
   - **No peers** — you are first. On the default branch, take `file_reservation_paths(paths=[".git/HEAD"], reason="session branch")` first: a peer that registered in the same second sees the lock, skips branching, and lands on your branch instead. Then branch, then release the lock.

     ```bash
     current=$(git rev-parse --abbrev-ref HEAD)
     if [ "$current" = "main" ] || [ "$current" = "master" ]; then
       git checkout -b "auto/$(date +%Y%m%d-%H%M)"
     fi
     ```

     If that reservation fails, a peer is branching right now: re-read the branch after it releases and stay on whatever it chose.

   Already on a non-default branch: stay on it. Report the session branch and baseline. If you find yourself back on the default branch mid-session, redo this step before committing anything.

2. **Load context** — read, skipping any that do not exist: `CLAUDE.md`/`AGENTS.md`, `README.md`, `CONTEXT.md` + a scan of `docs/adr/`, `git log --oneline -15`, and the unchecked count of `.ccu/CAPTURES.md` (the session-start read set in [[session-state]]). Do not load `.ccu/DECISIONS.md`; grep it when a specific "why" question arises and treat what it returns per the epistemics rule in [[session-state]]. If `cm` is installed, load procedural memory — `cm context "general development" --json --limit 10` — and keep the returned rules and anti-patterns in mind, referencing rule IDs when one shapes a decision.

3. **Pick, claim, reserve** — `br ready --json` lists unblocked beads; `bv` ranks them. Confirm the candidate is still open with `br show <id> --json` (a peer or a previous session may have closed it — skip closed ones), then claim it: `br update <id> --status in_progress`. A `cannot claim blocked issue` error means unmet dependencies: work the blocker or pick another ready bead; never prepare code ahead on a blocked bead. If no beads exist, triage `.ccu/CAPTURES.md`.

   Then reserve the paths the bead will touch, taken from its `## Files` block and your own investigation:

   ```
   file_reservation_paths(paths=[...], reason="<bead-id>")
   ```

   A failed reservation means a peer holds the path. Do not edit it. Release what you hold for this bead, drop the claim (`br update <id> --status open`), and return to the top of this step with a different bead — resolving per the conflict table in [[agent-mail]]. Post one message naming the bead you claimed, then move on without waiting for a reply.

4. **Execute** — implement the bead's requirements; track progress with bead comments and status updates. Reserve any additional path before you touch it. When evidence forces a deviation from the bead's plan (its `## Files`, `## Interfaces`, or technical notes turn out wrong or incomplete), pick the conservative option, keep going, and log it — `br comments add <id> "Deviation: <what> — <why>"` — so the plan's gap is visible instead of silently absorbed.

5. **Verify, then commit** — run the ladder in [[gates]]: lint and typecheck, the bead's `— verify:` commands, related integration only where the change crosses a boundary, then `build` once. Every acceptance criterion passes for real before you commit. A criterion you cannot run is a deviation to log (`br comments add`), not a box to tick. A failure on code you did not touch may be a peer's in-flight commit — assign it by causality per [[gates]] and report it rather than fix it.

   One commit per bead, bead id in the message. Peers stage and commit in this same index, so name your paths with a pathspec and never `git add -A`:

   ```bash
   git add <your files> && git commit -m "<type>(<scope>): <description> [<bead-id>]" -- <your files>
   ```

6. **Record** — for each technology, schema, API, or architecture choice made during the bead: if it meets the ADR gate, write `docs/adr/NNNN-slug.md` and add a one-line pointer entry to `.ccu/DECISIONS.md`; otherwise append a journal entry in the shared schema. The bead's close reason and commit carry the completion evidence — no separate evidence file. If `cm` is installed, record the outcome (`cm outcome success|failure <rule-ids>`) and mark notably helpful or harmful rules (`cm mark <bullet-id> --helpful` / `--harmful --reason "<why>"`).

7. **Loop** — re-check with `br show <id> --json` (already closed → move on, not an error), close with `br close <id> --reason "..."`, `release_file_reservations()`, and sync with `br sync --flush-only`. Read your inbox, handle anything that needs a reply, and return to step 3.

   When every remaining bead is blocked by an unmet dependency:

   - **No peers** — waiting cannot unblock anything. Stop and report the blocked graph.
   - **Peers active** — they are working the blockers. Re-check `br ready`, your inbox, and `git log` on a bounded interval. Stop after three consecutive checks with no new mail, no new commits, and no change in `br ready`, then report what is blocked and who holds it. A bead stuck `in_progress` whose holder has gone silent is a dead peer: reclaim it and force-release its reservations only after confirming its session ended.

8. **Wrap up** — when no actionable work remains:

   ```bash
   br sync --flush-only             # do NOT hide errors — a failed flush must not be committed silently
   git add .beads/ && git commit -m "chore(beads): sync session state" -- .beads/   # skip if nothing changed
   git status --porcelain           # nothing you worked on stays uncommitted
   ```

   Release every reservation you still hold — one you never release blocks the next session. Report per-bead ✓/✗ with commit hashes, beads left open or blocked, the session branch, the range `<baseline>..HEAD`, and the peers you saw. Pushing, opening a PR, or merging is the user's call; do not do it unasked.

   State where the full suite stands: CI runs it once on the PR, or — in a project with no CI — run it once here and report the result. Beads verified individually do not add up to a verified branch.

## Rules

- Never ask permission to continue or to start the next bead. Stop only when all work is done, everything remaining is blocked, or a genuine ambiguity needs human input.
- **Never reserve a path and then wait, and never send a message and wait for a reply.** Coordination is a means; shipping beads is the work. If a path is held, take a different bead rather than idling on it.
- Reserve before you edit, every time, including paths you discover mid-bead. This is the whole safety net.
- Own no domain. Any bead you can usefully work is yours to claim, and any bead you leave in progress is a peer's to resume.
- Every task gets a bead; update status and comments as you go.
- You write the unit tests that drive the bead's design. Functional, integration, and e2e tests belong to the `tester` agent, which this workflow never spawns — when a bead adds a public surface (a route, a CLI command, an exported API) that no `— verify:` command exercises, file a follow-up bead labelled `test` instead of writing those tests yourself. A bead is the unit any peer can pick up; a test written outside one is invisible.
- Bead comments are a point-in-time audit trail, not ground truth for PR/branch/merge state. Confirm against git or GitHub (`gh pr view <n> --json state,mergedAt`, `gh pr list --head <branch>`, `git log --oneline <branch>`) before reporting such state; if you cannot confirm, report it as unverified.
