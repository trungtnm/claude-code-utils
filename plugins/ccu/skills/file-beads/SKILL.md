---
name: file-beads
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
- **Files forecast** — best-known Create/Modify/Test paths, including affected tests and generated files
- **Interfaces forecast** — exact known signatures this bead consumes from and produces for neighboring beads
- **Coordination resources** — database mode, ports, lockfiles, other exclusive resources, and expected-red set
- **Risk annotation** — for HIGH-risk components, prefix with `⚠ HIGH RISK: <reason>` and explicit "investigate before coding" guidance (read docs, validate API surface, test assumptions before deep implementation)

Workers should never need to read `.ccu/artifacts/` to understand a bead. Push context forward — don't require backward lookups.

**Beads are ALWAYS written in English.** Title, description, comments, and close reasons — regardless of the language the user planned or captured in (Vietnamese captures get translated when filed). Beads are executed by worker agents, and English keeps every bead unambiguous for any agent that picks it up. The ONE exception: literal user-facing copy quoted inside a bead (UI labels, error messages, seed data) stays in its product language, verbatim — e.g. a bead written in English may specify `label: "Ứng viên"` with full Vietnamese diacritics, because that exact string is the deliverable.

**Acceptance criteria and gates define completion.** Files, interfaces, and technical notes record the best plan available before implementation. Workers may correct those forecasts when repository evidence requires a minimal change, but they must report the actual scope and reason.

## Step 2: Analyze and Structure

Before filing any issues, analyze the plan for:

1. **Major workstreams** - These become epics
2. **Individual tasks** - These become issues under epics
3. **Dependencies** - What must complete before other work can start?
4. **Parallelization opportunities** - What can be worked on simultaneously?
5. **Technical risks** - Which components are novel or external? These need `⚠ HIGH RISK` annotations so workers investigate before coding.
6. **Test impact** - Which unit, integration, fixture, generated, and documentation files consume a changed symbol, schema, or interface? Assign each affected file to a bead.
7. **Coordination resources** - Which databases, ports, lockfiles, or other exclusive resources can serialize otherwise independent work?

### Bead Right-Sizing

A bead is the **smallest unit that carries its own test cycle and is worth an independent review gate** — a reviewer could meaningfully reject this bead while approving its neighbor. Fold setup, configuration, scaffolding, and docs into the bead whose deliverable needs them; split only at independently testable seams. If two beads can only be tested together, they are one bead.

## Creator Attribution (all modes, all tiers)

Every bead MUST record who created it, taken from the local git credentials — never invented, never left blank. Resolve the identity once before filing anything:

```bash
creator_name=$(git config user.name)
creator_email=$(git config user.email)
```

Pass both on **every** `br create` call: `--owner "$creator_email" --actor "$creator_name"`. If either git config value is empty, ask the user for their identity before filing — do not file anonymous beads.

## Step 3: File Epics First

Create epics for major workstreams using:

```bash
br create "Epic: <title>" -t epic -p <priority> --owner "$creator_email" --actor "$creator_name" --json
```

Epics should:

- Have clear, descriptive titles
- Include acceptance criteria in the description
- Be scoped to deliverable milestones
- Carry a **`## Global Constraints`** section: project-wide requirements copied **verbatim** from the design doc and CLAUDE.md — version floors, dependency limits, naming and copy rules (e.g., Vietnamese text must use full diacritics), platform requirements. One line each, exact values. Every child bead implicitly inherits this section; workers read the epic bead before starting (`br show <epic-id>`). Do NOT repeat constraints in each child bead — duplication drifts.
- Carry an **`## Orchestration Environment`** section with exact project pre-flight and cleanup commands. Include commands that prove service identity, database isolation, required ports, and persistent queue or scheduler cleanup when those resources exist.

Use this shape:

```markdown
## Orchestration Environment
- Pre-flight: `<command>` → <expected identity or state>
- Cleanup: `<command>` → <expected clean state>
```

## Step 4: File Detailed Issues

For each epic (plan mode) or each enriched capture (single-bead mode), create the issue with:

```bash
br create "<task title>" -t <type> -p <priority> --deps <parent-epic-id> --owner "$creator_email" --actor "$creator_name" --json
```

### Template Tiers

Match template depth to the task — don't ceremonially pad small beads, but don't under-document risky ones either.

**Tier 1 — Minimal** (small scope, well-trodden path, no design decisions). Required sections:
- Project context (1 sentence — why this exists)
- Files block (best-known Create/Modify/Test paths — see Structured Blocks)
- Coordination Resources block
- Acceptance criteria (executable checklist — each item names its verify command)

**Tier 2 — Standard** (default for most beads). All of Tier 1, plus:
- Interfaces block (Consumes/Produces — mandatory whenever the bead has dependents or cross-bead consumers)
- Reasoning / justification (why this approach, what alternatives were considered)
- Considerations (constraints, edge cases, related decisions)
- Technical notes (existing patterns, relevant files, gotchas). Lead with a reference implementation when one exists: `Reference: <path> — imitate its <aspect>`. Source code conveys structure and semantics that prose cannot; the remaining notes then describe only what differs from the reference. Write `Reference: none found` when the hunt came up empty, so workers know it wasn't skipped.

**Tier 3 — High-risk** (novel infra, external dependencies, security/billing/data-loss surface, anything where being wrong is expensive). All of Tier 2, plus:
- `⚠ HIGH RISK: <reason>` prefix in the description
- **Investigate before coding** section listing what to validate before writing the implementation (read docs, prototype the risky API surface, confirm assumptions)
- Explicit rollback / blast-radius notes if the change is destructive

When in doubt, escalate one tier. The cost of over-documenting a bead is a few extra minutes; the cost of under-documenting one is a stuck or wrong worker.

### Structured Blocks

**`## Files` (required, all tiers).** List exact known paths, split by action:

```markdown
## Files
- Create: `src/middleware/rate-limit.ts`
- Modify: `src/app.ts` (mount after auth middleware)
- Test:   `src/middleware/rate-limit.test.ts`
```

Include production, test, fixture, generated, configuration, and documentation paths that the plan already identifies. Do not use prose hints such as "somewhere in the API layer." Use this block as an admission forecast. Workers may expand it when repository evidence requires a minimal change.

When a bead changes or removes a shared symbol, schema, or interface, search its consumers before filing. Name the affected tests and fixtures here or assign them to another bead with an explicit dependency.

**`## Coordination Resources` (required, all tiers).** Declare every admission axis:

```markdown
## Coordination Resources
- Database: `app_test` (`read-write`)
- Ports: `none`
- Lockfiles: `pnpm-lock.yaml`
- Other: `none`
- Expected red: `@app/api typecheck`, `tests/session.integration.test.ts`
```

Use `none` for an empty axis. Mark database access `read-write` or `schema-mutating`. Record intentional expected red as an exact package, suite, or test set. A missing declaration blocks orchestration dispatch.

**`## Interfaces` (required Tier 2+; mandatory whenever the bead has dependents or cross-bead consumers).** Record the exact known names and types neighboring beads use:

```markdown
## Interfaces
- Consumes: `req.user: { id: string; tier: 'free' | 'pro' }` — set by a03-2 (auth middleware)
- Produces: `rateLimit(opts: { limits: Record<Tier, number> }): RequestHandler`
  — consumed by a03-7 (usage dashboard reads the `X-RateLimit-Remaining` header this sets)
```

Signatures must be exact: names, parameter types, and return types. Every `Consumes` must match a `Produces` declared on an upstream bead or an existing symbol named in Technical notes. Treat the block as the planned seam. A worker may correct it when implementation evidence requires a change and the acceptance criteria remain intact.

**Acceptance criteria must be executable.** Each criterion names the command or test that proves it, with the expected result:

```markdown
- [ ] Returns 429 with `Retry-After` header when over limit
      — verify: `npm test rate-limit -- -t "returns 429"` → PASS
- [ ] Free tier blocks at request 101/min
      — verify: `npm test rate-limit -- -t "free tier burst"` → PASS
```

A criterion with no way to check it ("signature verification implemented") is not finished being written.

When a bead deletes tests, add an acceptance criterion for a deleted-test property ledger. Require each removed behavior to name its replacement test, existing coverage, or reason it dies with the removed mechanism.

### No Placeholders — Bead Failures

These phrases mean the bead is not done being written. Never file a bead containing:

- "add appropriate error handling" / "add validation" / "handle edge cases" — name the cases and the expected behavior
- "TBD", "TODO", "figure out during implementation"
- "similar to bead X" / "same as above" — repeat the content; workers read beads independently and possibly out of order
- Acceptance criteria that no command or test can check
- References to types, functions, or endpoints not defined in any upstream bead's `Produces` and not existing in the codebase

### Required fields (all tiers)

- **English only** - Title and description in English, whatever language the plan or capture arrived in (quoted user-facing copy keeps its product language)
- **Clear title** - Action-oriented (e.g., "Implement X", "Add Y", "Configure Z")
- **Type** - `task`, `bug`, `feature`, or `epic`
- **Priority** - see Step 6
- **Creator** - `--owner "$creator_email" --actor "$creator_name"` from git credentials (see Creator Attribution)
- **Dependencies** - Link to blocking issues with `--deps bd-<id>` (plan mode only)
- **Coordination resources** - Declare database mode, ports, lockfiles, other exclusive resources, and the exact expected-red set

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

## Files

- Create: `src/middleware/rate-limit.ts`
- Modify: `src/app.ts` (mount after auth middleware)
- Test:   `src/middleware/rate-limit.test.ts`

## Coordination Resources

- Database: `none`
- Ports: `none`
- Lockfiles: `none`
- Other: `redis-rate-limit-test-keyspace`
- Expected red: `none`

## Interfaces

- Consumes: `req.user: { id: string; tier: 'free' | 'pro' }` — set by a03-2 (auth middleware)
- Consumes: `getRedis(): RedisClient` — existing, `src/lib/redis.ts`
- Produces: `rateLimit(opts: { limits: Record<'free' | 'pro', number> }): RequestHandler`
  — consumed by a03-7 (usage dashboard reads the `X-RateLimit-Remaining` header this sets)

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

- [ ] Returns `429 Too Many Requests` with `Retry-After` header when over limit
      — verify: `npm test rate-limit -- -t "returns 429"` → PASS
- [ ] Free tier blocks at request 101/min; Pro tier allows up to 1000/min
      — verify: `npm test rate-limit -- -t "tier limits"` → PASS
- [ ] Burst traffic within bucket capacity is not penalized
      — verify: `npm test rate-limit -- -t "burst"` → PASS
- [ ] Sets `X-RateLimit-Remaining` header on every response
      — verify: `npm test rate-limit -- -t "remaining header"` → PASS

## Technical Notes

- Reference: `src/middleware/request-logger.ts` — imitate its middleware shape, error passthrough, and header-setting pattern
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
- Every bead carries the creator's git identity (`owner` set from `git config user.email` — spot-check with `br show <id> --json`)
- Every bead is written in English (titles and descriptions — quoted product copy excepted)
- Dependencies form a valid DAG (no cycles)
- Every `Consumes` in a bead matches — verbatim — a `Produces` on one of its upstream beads, or an existing symbol named in its Technical notes
- Every bead has a complete `## Coordination Resources` block; parallel-ready beads do not conflict on any declared axis
- Every affected test, fixture, generated file, and integration suite has an owning bead
- Every intentional expected-red entry names an exact package, suite, or test
- No bead contains a phrase from the "No Placeholders — Bead Failures" list
- Ready work exists (some issues have no blockers)
- Priorities make sense for execution order

## Output Format

After completing, provide:

1. Summary of epics created
2. Summary of issues per epic
3. Dependency graph overview (what unblocks what)
4. Suggested starting points (ready issues)
5. Parallelization opportunities
