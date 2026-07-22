# Execution Plan: <Feature Name>

Epic: <epic-id>
Generated: <date>

> The orchestrator dispatches **one worker per ready bead** (`br ready` + `bv`), capped at 3
> concurrent workers. This document is the map — the live graph is the schedule.

## Beads

| Bead    | Title                    | Files (reservation list)         | Depends on      | Risk |
| ------- | ------------------------ | -------------------------------- | --------------- | ---- |
| {id-1}  | <title>                  | `src/db/migrations/*.sql`        | —               | LOW  |
| {id-2}  | <title>                  | `apps/server/routes/users.ts`    | {id-1}          | MED  |
| {id-3}  | <title>                  | `packages/sdk/client.ts`         | {id-2}          | LOW  |
| {id-4}  | <title>                  | `apps/web/pages/users.tsx`       | {id-2}          | HIGH |

Each bead's `## Files` block is the worker's Agent Mail reservation list — the complete touch
list. Beads with no dependency path between them MUST have disjoint Files sets.

## Entry Points (ready at start)

Per `br ready --json` at planning time:

- {id-1}: <title> — no blockers, dispatch immediately

## Parallel Waves (from bv --robot-plan)

- Wave 1: {id-1}
- Wave 2: {id-2}
- Wave 3: {id-3}, {id-4} (disjoint files — safe to run concurrently)

## Sequencing Caveats

- <anything the graph can't express: e.g. "{id-3} and {id-4} both read the generated API types —
  regenerate before dispatching either", or "run DB migrations locally before wave 2">
- (Remove this section if none.)

## High-Risk Components

Beads carrying `⚠ HIGH RISK` annotations from Phase 2 — workers should investigate before coding:

- {id-4}: <reason — what is novel or external>
- (Remove this section if no HIGH-risk items.)
