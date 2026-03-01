# Execution Plan: <Feature Name>

Epic: <epic-id>
Generated: <date>

## Tracks

| Track | Agent       | Beads (in order)      | File Scope        |
| ----- | ----------- | --------------------- | ----------------- |
| 1     | BlueLake    | bd-10 → bd-11 → bd-12 | `packages/sdk/**` |
| 2     | GreenCastle | bd-20 → bd-21         | `packages/cli/**` |
| 3     | RedStone    | bd-30 → bd-31 → bd-32 | `apps/server/**`  |

## Track Details

### Track 1: BlueLake - <track-description>

**File scope**: `packages/sdk/**`
**Beads**:

1. `bd-10`: <title> - <brief description>
2. `bd-11`: <title> - <brief description>
3. `bd-12`: <title> - <brief description>

### Track 2: GreenCastle - <track-description>

**File scope**: `packages/cli/**`
**Beads**:

1. `bd-20`: <title> - <brief description>
2. `bd-21`: <title> - <brief description>

### Track 3: RedStone - <track-description>

**File scope**: `apps/server/**`
**Beads**:

1. `bd-30`: <title> - <brief description>
2. `bd-31`: <title> - <brief description>
3. `bd-32`: <title> - <brief description>

## Cross-Track Dependencies

- Track 1 (frontend) blocked by bd-30 (Track 3/backend API endpoint)
- Track 2 can start after bd-11 (Track 1) completes
- Track 3 (backend) has no blockers - can start immediately

## Key Learnings (from Spikes)

Embedded in beads, but summarized here for orchestrator reference:

- <learning 1>
- <learning 2>
