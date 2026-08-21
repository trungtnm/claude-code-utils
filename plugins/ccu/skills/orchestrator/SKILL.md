---
name: orchestrator
description: Plan and coordinate multi-agent bead execution. Use when starting a new epic, dispatching workers per bead, or monitoring parallel work progress.
---

# Orchestrator

Coordinate the work; do not implement production changes. Spawn one worker subagent per bead, scheduled by the dependency graph. Every agent works in the user's tree, on the current branch; Agent Mail file reservations are the only lock between them, and a peer [[auto]] session may be working the same tree. Beads, commits, and `.ccu/` files hold durable state.

When running in Codex, read [CODEX.md](../../CODEX.md) first and translate `Task(...)`, `TaskList`, `TaskOutput`, `SendMessage`, and `AskUserQuestion` to the Codex collaboration mechanism. Before spawning a worker, tester, or reviewer in Codex, include the matching persona from `../../agents/` in the delegated task.

## Roles

| Role | Agent type | Responsibility |
| --- | --- | --- |
| Coder | `worker`, one per bead | Implements the bead with TDD and unit tests |
| Tester | `tester`, one per epic | Black-box functional, integration, and e2e tests after all beads verify |
| Reviewer | `reviewer`, one per epic | Integrated quality sweep, then documentation |

Coders own production logic. The tester and reviewer never edit it; they report defects back.

## Prerequisites

1. Require `.ccu/artifacts/<dir>/execution-plan.md` from [[plan-beads]]. Run [[review-beads]] first when bead quality is unverified.
2. Resolve the actor: `ACTOR="${BR_ACTOR:-assistant}"`.
3. Register with Agent Mail and record `ORCH_NAME` per [[agent-mail]].
4. Record the baseline: `git rev-parse --short HEAD`. If `git status --porcelain` shows a dirty tree, tell the user before dispatching.
5. Create the epic context file `.ccu/artifacts/<dir>/epic-context.md`. Workers read it before starting and append learnings after each bead.

## Admission

Re-read `br ready --json` and `br show <bead-id>` immediately before every dispatch; the plan describes, the graph schedules. Rank candidates with `bv --robot-priority` and `bv --robot-triage --graph-root <epic-id>`.

Require `## Coordination Resources` on every bead; backfill a missing block before dispatch. Compare each candidate with active workers across planned files, database access, ports, lockfiles, and other declared exclusive resources, using the syntax and conflict matrix in [admission.md](references/admission.md).

Treat `## Files` as the best-known admission footprint, not an edit boundary. Conflicting beads run sequentially; when they also lack a dependency edge, add one with `br dep add`.

## Dispatch

For each admitted bead:

1. Claim it: `br update --actor "$ACTOR" <bead-id> --status in_progress --json`. A refusal is a hard stop: do not spawn; refresh the graph and reschedule.
2. Fill [worker-prompt.md](templates/worker-prompt.md) and spawn a background worker: `Task(subagent_type="worker", model="opus", prompt=<filled template>)`. The prompt carries the single bead id, the literal repo root (the mail project key), `ORCH_NAME`, and the epic thread id.
3. Record the worker's mail name and harness agent id when it reports in; mail addressing and `SendMessage` addressing differ, and you need both.

Cap concurrency at 3 workers. All workers share one git index and one build/test environment; beyond 3, gate runs collide. When a bead closes, re-run `br ready` and dispatch what it freed.

## Worker authority

Tell the worker to follow the bead's acceptance criteria, gates, and the evidence it discovers. It may make minimal necessary changes that `## Files`, `## Interfaces`, or the technical notes omitted or misstated, and must record the actual scope and reason in its report. It stops only for:

- an active-peer collision (a failed reservation);
- a new exclusive resource;
- an irreversible action;
- a required change to an acceptance criterion.

Assign failures by causality. A failure caused by the worker's change is its responsibility even when the failing file was absent from `## Files`. An independent failure is recorded, not fixed.

## Monitoring

Progress arrives on two channels; durable state arbitrates both:

| Source | Read with | Role |
| --- | --- | --- |
| Agent Mail | `fetch_inbox`, `search_messages` | Live progress while workers run |
| Task result | worker's final message, `TaskOutput` | The bead report |
| Beads and git | `bv --robot-triage`, `br show <id> --json`, `git log --grep="Bead:"` | Ground truth |

A worker that mails `COMPLETE` without a commit is not complete. A mailed reply never restarts a finished agent: resume live agents with `SendMessage`, respawn exited ones with the decision or rejection referenced in the prompt. Message semantics and reservation-conflict handling are in [[agent-mail]].

Resolve coordination questions yourself when the plan, the bead, or project convention answers them. Escalate to the user with `AskUserQuestion` only for a required acceptance-criteria change, an irreversible action, an external blocker, or a bead that fails verification three times. Include the evidence and the options in the question.

## Verification

Worker reports are inputs; re-run the evidence yourself per [verification.md](references/verification.md).

| Phase | Trigger | Action |
| --- | --- | --- |
| Bead | Every completion report | Commit exists, scope judged by necessity and causality, smells read in context, bead closed, report complete |
| Tester | All implementation beads verified | Spawn one `tester` from [tester-prompt.md](templates/tester-prompt.md) |
| Bug routing | Tester reports `[BUG]` beads | Respawn a fix-scoped worker per bug bead; the fixer un-skips the exposing test in its fix commit |
| Review | All bug beads closed or user-deferred | Spawn one `reviewer` from [reviewer-prompt.md](templates/reviewer-prompt.md) |

Skip the tester only when the epic adds no behavior surface (docs-only, config-only, or a contract-preserving refactor already covered by existing tests); note the skip in a comment on the epic bead. Skip the review sweep for epics under 3 beads; still have documentation written for any user-facing surface.

## Completion

When `bv --robot-triage --graph-root <epic-id>` shows zero open beads:

1. Broadcast the epic summary to every participating agent on the epic thread, then confirm no reservations remain held (stale-lock handling in [[agent-mail]]).
2. Write `.ccu/artifacts/<dir>/summary.md` (bead summaries, deliverables, learnings) and regenerate the HTML index:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/markdown-html-viewer/scripts/md2html.py" .ccu/artifacts/<dir>/
   ```

3. Close the epic: `br close --actor "$ACTOR" <epic-id> --reason "All beads complete"`.
4. Commit bead state:

   ```bash
   br sync --flush-only
   git add .beads/ && git commit -m "epic(<epic-id>): close all beads" -- .beads/
   ```

The epic's code commits are already on the current branch. Pushing or opening a PR is the user's call.
