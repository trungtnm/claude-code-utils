---
description: File detailed Beads epics and issues from a plan, or a single rich bead from an enriched capture. Authoritative source for bead structure and templates — other skills (e.g. triage) delegate here.
argument-hint: <plan-description-or-context>
---

# File Beads Epics and Issues

This skill is the **single source of truth for bead structure** in this project. It covers two entry modes:

- **Plan mode** (default): convert a multi-workstream plan into epics + child issues with dependencies. Use when invoked directly with a plan or planning doc.
- **Single-bead mode**: produce one self-contained bead from an already-enriched context (a capture + investigation + answered questions). Use when invoked by the `triage` skill, or when the user has a single concrete task to file. Skip Steps 3, 5, 7 in this mode.

Other skills (notably [[triage]]) MUST delegate to this skill rather than embedding their own bead templates, so the template stays consistent.

## Step 1: Understand the Plan

First, review the plan context provided: `$ARGUMENTS`

If no specific plan is provided, ask the user to share the plan or point to a planning document (check `.ccu/artifacts/` directory for recent plans).

In **single-bead mode**, `$ARGUMENTS` will be a structured object from the caller (title, context, what-to-change, acceptance criteria, technical notes). Skip discovery and proceed directly to Step 4 using the appropriate template tier.

## Self-Documentation Principle

Every bead must be **self-contained for a worker with zero prior context**. A worker should be able to read a single bead and understand not just *what* to build, but *why* it exists, *how* it serves the project, and *what tradeoffs were considered*.

Self-documenting beads include:
- **The "why"** — project context that connects this task to overarching goals
- **Reasoning / justification** — why this approach was chosen, what alternatives were considered
- **Considerations** — constraints, edge cases, related decisions from planning
- **Context lineage** — references to discovery or approach docs in `.ccu/artifacts/<dir>/` that informed this bead
- **Risk annotation** — for HIGH-risk components, prefix with `⚠ HIGH RISK: <reason>` and explicit "investigate before coding" guidance (read docs, validate API surface, test assumptions before deep implementation)

Workers should never need to read `.ccu/artifacts/` to understand a bead. Push context forward — don't require backward lookups.

## Step 2: Analyze and Structure

Before filing any issues, analyze the plan for:

1. **Major workstreams** - These become epics
2. **Individual tasks** - These become issues under epics
3. **Dependencies** - What must complete before other work can start?
4. **Parallelization opportunities** - What can be worked on simultaneously?
5. **Technical risks** - Which components are novel or external? These need `⚠ HIGH RISK` annotations so workers investigate before coding.

## Step 3: File Epics First

Create epics for major workstreams using:

```bash
br create "Epic: <title>" -t epic -p <priority> --json
```

Epics should:

- Have clear, descriptive titles
- Include acceptance criteria in the description
- Be scoped to deliverable milestones

## Step 4: File Detailed Issues

For each epic (plan mode) or each enriched capture (single-bead mode), create the issue with:

```bash
br create "<task title>" -t <type> -p <priority> --deps <parent-epic-id> --json
```

### Template Tiers

Match template depth to the task — don't ceremonially pad small beads, but don't under-document risky ones either.

**Tier 1 — Minimal** (small scope, well-trodden path, no design decisions). Required sections:
- Project context (1 sentence — why this exists)
- What to change (specific files/behaviors)
- Acceptance criteria (verifiable checklist)

**Tier 2 — Standard** (default for most beads). All of Tier 1, plus:
- Reasoning / justification (why this approach, what alternatives were considered)
- Considerations (constraints, edge cases, related decisions)
- Technical notes (existing patterns, relevant files, gotchas)

**Tier 3 — High-risk** (novel infra, external dependencies, security/billing/data-loss surface, anything where being wrong is expensive). All of Tier 2, plus:
- `⚠ HIGH RISK: <reason>` prefix in the description
- **Investigate before coding** section listing what to validate before writing the implementation (read docs, prototype the risky API surface, confirm assumptions)
- Explicit rollback / blast-radius notes if the change is destructive

When in doubt, escalate one tier. The cost of over-documenting a bead is a few extra minutes; the cost of under-documenting one is a stuck or wrong worker.

### Required fields (all tiers)

- **Clear title** - Action-oriented (e.g., "Implement X", "Add Y", "Configure Z")
- **Type** - `task`, `bug`, `feature`, or `epic`
- **Priority** - see Step 6
- **Dependencies** - Link to blocking issues with `--deps bd-<id>` (plan mode only)

## Step 5: Map Dependencies Carefully

For each issue, consider:

- Does this depend on another issue completing first?
- Can this be worked on in parallel with siblings?
- Are there cross-epic dependencies?

Use `--deps bd-X,bd-Y` for multiple dependencies.

## Example: Self-Documenting Bead (Tier 3 — High-risk)

This example shows a fully-loaded Tier 3 bead. A Tier 1 bead would have just Project Context + What to Change + Acceptance Criteria.

```markdown
# Implement rate limiting middleware for public API

⚠ HIGH RISK: Token-bucket implementation depends on Redis MULTI/EXEC atomicity
under concurrent load — validate the Lua script handles race conditions before
relying on it for billing-tier enforcement.

## Project Context

Our public API currently has no rate limiting, which is the #1 blocker for
launching to external developers. This task directly enables the "Developer
Platform" epic by making the API safe for third-party consumption.

## Reasoning / Justification

Chose token-bucket algorithm over sliding window because:
- Our Redis instance already supports atomic MULTI/EXEC (no extra infra)
- Token bucket handles burst traffic better for our webhook-heavy use case
- Alternative: sliding window was simpler but penalizes legitimate bursts

## Investigate Before Coding

- Confirm Redis Lua script atomicity guarantees match our cluster config
- Test bucket refill behavior under simulated burst traffic
- Verify that auth middleware exposes `req.user` early enough in the chain

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
- See `.ccu/artifacts/<dir>/approach.md` for the rejected alternatives and full risk analysis
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
br list --json
br ready --json
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