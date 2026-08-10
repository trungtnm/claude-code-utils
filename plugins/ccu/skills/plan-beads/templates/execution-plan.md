# Execution Plan: <Feature Name>

Epic: <epic-id>
Generated: <date>

> The orchestrator dispatches **one worker per ready bead** (`br ready` + `bv`), capped at 3
> concurrent workers. This document is the map — the live graph is the schedule.

## Beads

| Bead | Title | Planned files | Resources | Depends on | Checkpoint | Risk |
| --- | --- | --- | --- | --- | --- | --- |
| {id-1} | <title> | `src/db/migrations/*.sql` | DB `app_test` (`schema-mutating`) | — | yes: schema | HIGH |
| {id-2} | <title> | `apps/server/routes/users.ts` | DB `app_test` (`read-write`) | {id-1} | yes: interface | MED |
| {id-3} | <title> | `packages/sdk/client.ts` | none | {id-2} | no | LOW |
| {id-4} | <title> | `apps/web/pages/users.tsx` | port `5174` | {id-2} | no | HIGH |

Treat `## Files` as the best-known footprint. Sequence parallel-ready beads when planned files,
schema-mutating database access, ports, lockfiles, or other exclusive resources conflict.

## Entry Points (ready at start)

Per `br ready --json` at planning time:

- {id-1}: <title> — no blockers, dispatch immediately

## Parallel Waves (from bv --robot-plan)

- Wave 1: {id-1}
- Wave 2: {id-2}
- Wave 3: {id-3}, {id-4} (no planned file or resource conflict)

## Sequencing Caveats

- <anything the graph can't express: e.g. "{id-3} and {id-4} both read the generated API types —
  regenerate before dispatching either", or "run DB migrations locally before wave 2">
- (Remove this section if none.)

## High-Risk Components

Beads carrying `⚠ HIGH RISK` annotations from Phase 2 — workers should investigate before coding:

- {id-4}: <reason — what is novel or external>
- (Remove this section if no HIGH-risk items.)
