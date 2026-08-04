---
name: create-project-rules
description: "Generate tailored quality rules and coding standards for a specific project. Use when the user wants to create project rules, define coding standards, set up quality guidelines, add rules to AGENTS.md or CLAUDE.md, establish testing standards, or define operational rules for their codebase. Triggers on: 'create project rules', 'set up quality rules', 'define coding standards', 'add quality guidelines', 'establish project conventions', 'create AGENTS.md rules', 'create CLAUDE.md rules'. Should also trigger when users say things like 'I want rules before I start coding' or 'set up guardrails for this project'."
---

# Create Project Rules

Generate a tailored quality ruleset for any project by reading its codebase, understanding its domain, and producing rules that fit its specific tech stack, architecture, and constraints.

This is not a static reference — it's a generator. It reads the project, proposes rules immediately, and lets the user refine from there.

## How this differs from generic coding standards

Generic standards say "write clean code." Project rules say "keyword classifier must complete in <10ms, LLM calls get a 30s timeout, and safety validator tests need exhaustive edge case coverage." The value is in specificity — rules shaped by the actual project, not universal platitudes.

## Process

### Phase 1: Rapid project scan

Read the project's foundational documents to understand what you're working with. Do this silently — no need to narrate each file read.

**Read in order (skip if missing):**
1. `AGENTS.md` and `CLAUDE.md` — existing AI instructions and conventions (read either or both when present)
2. `README.md` — project purpose, tech stack
3. `docs/` directory — architecture docs, PRDs, existing design docs
4. `package.json` / `Cargo.toml` / `pyproject.toml` / `go.mod` — dependencies, scripts
5. Recent git history (`git log --oneline -15`) — what's been happening
6. Scan `src/` structure — how code is organized

**From the scan, identify:**
- Tech stack (language, framework, database, external APIs)
- Project domain (what does this software actually do?)
- Architecture pattern (monolith, microservices, pipeline, event-driven, etc.)
- Existing conventions (anything already in CLAUDE.md or config files like biome.json, eslint, prettier)
- External boundaries (APIs, databases, third-party services the code talks to)
- High-risk modules (security-sensitive, data-integrity-critical, performance-critical)

### Phase 2: Propose rules immediately

After the scan, present a complete proposed ruleset right away. Don't interview the user first — give them something concrete to react to. People refine better than they specify from scratch.

**Structure your proposal as:**

> **Project summary** (2-3 sentences confirming what you understood)
>
> **Where should these rules live?**
> - A) Add to the host instruction file (`AGENTS.md` in Codex, `CLAUDE.md` in Claude Code; recommended if it exists)
> - B) Create a separate `docs/QUALITY.md`
> - C) Both — compact rules in the host instruction file, full reference in `docs/QUALITY.md`
>
> **Proposed rules** (organized by category, see Rule Categories below)

Present ALL categories at once. The user will tell you what to change, remove, or expand. This is faster than asking section-by-section for simple projects, while still allowing deep refinement for complex ones.

### Phase 3: Refine on feedback

The user may:
- Accept everything → write the rules
- Ask to change specific sections → revise and re-present those sections
- Ask to go deeper on a topic → expand that section with more detail
- Remove sections → drop them
- Add concerns you didn't cover → add new rules

Keep iterating until the user approves. Then write the rules to the agreed location.

## Rule Categories

Not every project needs every category. Use your judgment from the project scan — a simple CLI tool doesn't need operational resilience rules, and a pure library doesn't need database rules.

Read `references/rule-categories.md` for the full catalog of rule categories with examples. Below is the summary of what's available:

| Category | When to include | Skip when |
|---|---|---|
| Coding standards | Always | Never skip |
| Testing rules | Always | Never skip |
| Code organization | Projects with 5+ files | Tiny scripts, single-file tools |
| Quality gates | Projects with build tools / linters | No tooling set up |
| Error handling | Projects with external I/O | Pure computation libraries |
| Operational rules | Long-running services, pipelines | CLI tools, libraries, scripts |
| Database rules | Projects using a database | No database |
| API rules | Projects exposing or consuming APIs | No API surface |
| Security rules | Projects handling user data, auth, payments | Internal tools with no user input |
| Domain-specific rules | Projects with domain constraints (compliance, safety, rate limits) | Generic CRUD apps |

### Tailoring rules to the tech stack

Rules should reference the project's actual tools, not generic advice:

- If the project uses **Biome** → reference `pnpm check` not "run your linter"
- If the project uses **Vitest** → reference vitest patterns, not Jest
- If the project uses **Drizzle ORM** → reference Drizzle migrations, not "run your migrations"
- If the project uses **Zod** → reference Zod validation, not "validate your inputs"
- If the project uses **Python/pytest** → reference pytest fixtures and markers
- If the project uses **Go** → reference `go vet`, `go test -race`, table-driven tests

Generic rules that could apply to any project are low-value. Every rule should feel like it was written *for this project*.

### Tailoring rules to existing conventions

If the project already has rules (in `AGENTS.md`, `CLAUDE.md`, linter configs, etc.), respect them:

- Don't duplicate rules that already exist — reference them
- Don't contradict existing conventions — ask the user if there's a conflict
- Fill gaps — focus on what's missing, not what's already covered
- If the host instruction file already has 200+ lines of rules, be selective about what you add. More rules ≠ better rules. Every rule you add should earn its place.

## Testing rules deserve special attention

Bad tests are worse than no tests — they create false confidence. When generating testing rules, always address these anti-patterns explicitly:

1. **Tests that assert nothing meaningful** — `expect(result).toBeDefined()` or just checking that a function doesn't throw
2. **Tests that mirror implementation** — computing the expected value the same way the code does
3. **Snapshot tests on business logic** — they pass until they don't, nobody reads the diff
4. **Vague test names** — `it("works")` instead of `it("returns error when API key is missing")`
5. **Mocking the function under test** — testing a mock instead of the real thing

For every project, testing rules should specify:
- What to test (business logic, edge cases, error paths)
- What NOT to test (framework wiring, type transformations, obvious getters)
- What boundaries to mock (external APIs, databases) vs. test directly (internal modules)
- Test naming convention with project-specific examples
- Minimum coverage shape: happy path + N edge cases + error path per module (not a % target)

## Writing the rules

When the user approves, write the rules to the agreed location:

**If writing to `AGENTS.md` or `CLAUDE.md`:**
- Preserve all existing content and section ordering
- Insert new sections in a logical position (conventions near conventions, operational rules near existing operational content)
- If the file is already long (300+ lines), keep new additions concise — bullet points, not paragraphs

**If writing to a separate file:**
- Use `docs/QUALITY.md` as the default path
- Include a brief reference in the host instruction file pointing to the file: `## Quality rules\nSee docs/QUALITY.md for the full project quality ruleset.`

**If writing to both:**
- The host instruction file gets the compact, actionable version (what an AI agent needs every session)
- docs/QUALITY.md gets the full version with rationale and examples

After writing, offer to commit the changes.

## Key principles

- **Specificity over generality** — "LLM calls get a 30s timeout" beats "add timeouts to external calls"
- **Project-shaped rules** — rules should reflect the actual architecture, not a generic template
- **Earn your place** — every rule should prevent a real problem. No filler rules
- **Propose first, ask second** — give the user a complete draft to react to, don't interview them to death
- **Respect what exists** — build on existing conventions, don't replace them
