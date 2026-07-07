# Execution Plan: <Feature Name>

Epic: <epic-id>
Generated: <date>

## Tracks

| Track | Agent       | Beads (in order)               | File Scope        |
| ----- | ----------- | ------------------------------ | ----------------- |
| 1     | BlueLake    | {id-1} → {id-2} → {id-3}      | `packages/sdk/**` |
| 2     | GreenCastle | {id-4} → {id-5}               | `packages/cli/**` |
| 3     | RedStone    | {id-6} → {id-7} → {id-8}      | `apps/server/**`  |

## Track Details

### Track 1: BlueLake - <track-description>

**File scope**: `packages/sdk/**`
**Beads**:

1. `{id-1}`: <title> - <brief description>
2. `{id-2}`: <title> - <brief description>
3. `{id-3}`: <title> - <brief description>

### Track 2: GreenCastle - <track-description>

**File scope**: `packages/cli/**`
**Beads**:

1. `{id-4}`: <title> - <brief description>
2. `{id-5}`: <title> - <brief description>

### Track 3: RedStone - <track-description>

**File scope**: `apps/server/**`
**Beads**:

1. `{id-6}`: <title> - <brief description>
2. `{id-7}`: <title> - <brief description>
3. `{id-8}`: <title> - <brief description>

## Cross-Track Dependencies

- Track 1 (frontend) blocked by {id-6} (Track 3/backend API endpoint)
- Track 2 can start after {id-2} (Track 1) completes
- Track 3 (backend) has no blockers - can start immediately

## High-Risk Components

Beads carrying `⚠ HIGH RISK` annotations from Phase 2 — workers should investigate before coding:

- {id-N} ({Track}): <reason — what is novel or external>
- (Remove this section if no HIGH-risk items.)
