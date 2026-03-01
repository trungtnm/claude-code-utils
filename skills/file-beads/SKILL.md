---
description: File detailed Beads epics and issues from a plan
argument-hint: <plan-description-or-context>
---

# File Beads Epics and Issues from Plan

You are tasked with converting a plan into a comprehensive set of Beads epics and issues. Follow these steps carefully:

## Step 1: Understand the Plan

First, review the plan context provided: `$ARGUMENTS`

If no specific plan is provided, ask the user to share the plan or point to a planning document (check `history/` directory for recent plans).

## Self-Documentation Principle

Every bead must be **self-contained for a worker with zero prior context**. A worker should be able to read a single bead and understand not just *what* to build, but *why* it exists, *how* it serves the project, and *what tradeoffs were considered*.

Self-documenting beads include:
- **The "why"** — project context that connects this task to overarching goals
- **Reasoning / justification** — why this approach was chosen, what alternatives were considered
- **Considerations** — constraints, edge cases, related decisions from planning
- **Context lineage** — references to discovery, approach docs, or spike learnings that informed this bead

Workers should never need to read `history/` artifacts to understand a bead. Push context forward — don't require backward lookups.

## Step 2: Analyze and Structure

Before filing any issues, analyze the plan for:

1. **Major workstreams** - These become epics
2. **Individual tasks** - These become issues under epics
3. **Dependencies** - What must complete before other work can start?
4. **Parallelization opportunities** - What can be worked on simultaneously?
5. **Technical risks** - What needs spikes or investigation first?

## Step 3: File Epics First

Create epics for major workstreams using:

```bash
bd create "Epic: <title>" -t epic -p <priority> --json
```

Epics should:

- Have clear, descriptive titles
- Include acceptance criteria in the description
- Be scoped to deliverable milestones

## Step 4: File Detailed Issues

For each epic, create child issues with:

```bash
bd create "<task title>" -t <type> -p <priority> --deps <parent-epic-id> --json
```

Each issue MUST include:

- **Clear title** - Action-oriented (e.g., "Implement X", "Add Y", "Configure Z")
- **Project context** - How this task serves overarching goals (1-2 sentences connecting to the bigger picture)
- **Detailed description** - What exactly needs to be done
- **Reasoning / justification** - Why this approach? What alternatives were considered and why rejected?
- **Acceptance criteria** - How do we know it's done?
- **Considerations** - Constraints, edge cases, related decisions from planning that affect implementation
- **Technical notes** - Implementation hints, gotchas, relevant files
- **Dependencies** - Link to blocking issues with `--deps bd-<id>`

## Step 5: Map Dependencies Carefully

For each issue, consider:

- Does this depend on another issue completing first?
- Can this be worked on in parallel with siblings?
- Are there cross-epic dependencies?

Use `--deps bd-X,bd-Y` for multiple dependencies.

## Example: Self-Documenting Bead

Here's an example showing how a well-documented bead gives workers everything they need:

```markdown
# Implement rate limiting middleware for public API

## Project Context

Our public API currently has no rate limiting, which is the #1 blocker for
launching to external developers. This task directly enables the "Developer
Platform" epic by making the API safe for third-party consumption.

## Reasoning / Justification

Chose token-bucket algorithm over sliding window because:
- Our Redis instance already supports atomic MULTI/EXEC (no extra infra)
- Token bucket handles burst traffic better for our webhook-heavy use case
- Alternative: sliding window was simpler but penalizes legitimate bursts

## Considerations

- Must be applied AFTER auth middleware (needs user ID for per-user limits)
- Free tier: 100 req/min, Pro tier: 1000 req/min (from product spec in approach.md)
- Edge case: webhook retry storms can exhaust limits — consider exempting internal IPs
- Related decision: Phase 2 chose Redis over in-memory because of multi-instance deploy

## Acceptance Criteria

- [ ] Rate limiter middleware at `src/middleware/rate-limit.ts`
- [ ] Token bucket algorithm with configurable limits per tier
- [ ] Returns `429 Too Many Requests` with `Retry-After` header
- [ ] Unit tests covering burst scenarios and tier differences

## Technical Notes

- Existing auth middleware at `src/middleware/auth.ts` extracts `req.user`
- Redis client already configured in `src/lib/redis.ts`
- See `.spikes/api-platform/rate-limit-test/` for working prototype
```

Compare this with a minimal bead that says "Add rate limiting to API" — the self-documenting version lets a worker start immediately without reading discovery or approach docs.

## Step 6: Set Priorities Thoughtfully

- `0` - Critical path blockers, security issues
- `1` - Core functionality, high business value
- `2` - Standard work items (default)
- `3` - Nice-to-haves, polish
- `4` - Backlog, future considerations

## Step 7: Verify the Graph

After filing all issues, run:

```bash
bd list --json
bd ready --json
```

Verify:

- All epics have child issues
- Dependencies form a valid DAG (no cycles)
- Ready work exists (some issues have no blockers)
- Priorities make sense for execution order

## Output Format

After completing, provide:

1. Summary of epics created
2. Summary of issues per epic
3. Dependency graph overview (what unblocks what)
4. Suggested starting points (ready issues)
5. Parallelization opportunities