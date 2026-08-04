# Rule Categories Reference

Full catalog of rule categories with examples. The skill reads the project and selects which categories apply. Each category includes example rules showing the level of specificity expected.

## Table of Contents

1. [Coding Standards](#1-coding-standards)
2. [Testing Rules](#2-testing-rules)
3. [Code Organization](#3-code-organization)
4. [Quality Gates](#4-quality-gates)
5. [Error Handling](#5-error-handling)
6. [Operational Rules](#6-operational-rules)
7. [Database Rules](#7-database-rules)
8. [API Rules](#8-api-rules)
9. [Security Rules](#9-security-rules)
10. [Domain-Specific Rules](#10-domain-specific-rules)

---

## 1. Coding Standards

Always include. Tailor to the project's language and framework.

**Areas to cover:**
- Type strictness (strict mode, `any` usage, type assertions)
- Export style (named vs default, barrel files)
- Function constraints (max length, single responsibility, purity)
- Import ordering (built-ins → external → internal → relative)
- Mutability preferences (readonly, const, immutable patterns)
- Class vs function preference
- Naming conventions (if not already defined)

**Example rules (TypeScript/Node.js project):**
```
- Strict mode always — no `any`, no `ts-ignore` without a comment explaining why
- No default exports — named exports only
- No barrel files (`index.ts` re-exports) — import directly from source
- Max ~50 lines per function — extract a named helper if longer
- Prefer `interface` over `type` for object shapes
- Explicit return types on exported functions
- No classes unless the domain requires stateful instances
```

**Example rules (Python project):**
```
- Type hints on all public functions (use `from __future__ import annotations`)
- No `# type: ignore` without a comment explaining why
- Prefer dataclasses or Pydantic models over raw dicts for structured data
- Max ~40 lines per function
- Imports: stdlib → third-party → local, separated by blank lines
- No wildcard imports (`from module import *`)
```

**Example rules (Go project):**
```
- `go vet` and `staticcheck` must pass with zero warnings
- No `interface{}` / `any` without a comment explaining why
- Error wrapping: use `fmt.Errorf("context: %w", err)`, not naked returns
- Max ~60 lines per function
- Table-driven tests for any function with >2 input variations
```

---

## 2. Testing Rules

Always include. This is the highest-value category — bad tests are the most common quality problem in AI-assisted codebases.

**Areas to cover:**
- Testing philosophy (behavior vs implementation)
- Test structure (AAA: Arrange/Act/Assert)
- What to test / what not to test
- Mocking boundaries (what to mock, what to test directly)
- Test naming convention with project-specific examples
- Coverage expectations (per-module shape, not % target)
- Anti-patterns to reject (with explanations of why)

**Example rules:**
```
Testing philosophy:
- Tests prove behavior, not implementation
- Every test must be able to fail meaningfully — if it can't catch a real bug, delete it
- No "status 200" tests — assert actual output values, not just "it didn't throw"

What to test:
- Business logic, edge cases, error paths
- Happy path + at least 2 edge cases + at least 1 error path per module

What NOT to test:
- Framework wiring, config loading happy path, simple type transforms
- Don't mock what you own — mock external boundaries only

Test naming:
- Pattern: it("[expected behavior] when [condition]")
- Example: it("returns pain_losing bucket when message contains SL keywords")
- No vague names: it("works correctly") or it("handles edge case")

Anti-patterns to reject:
- Snapshot tests for business logic
- Tests that assert only toBeDefined() or not.toBeNull()
- Tests that compute expected values the same way the code does
- Tests requiring specific execution order
- Mocking the function under test
```

---

## 3. Code Organization

Include for projects with 5+ source files.

**Areas to cover:**
- File size limits (when to split)
- Test file location (co-located vs separate directory)
- Utility file policy (no grab-bag helpers)
- Dependency direction (if the project has a pipeline or layer architecture)
- Import cycle prevention
- New code checklist

**Example rules:**
```
- One module = one file unless it exceeds ~400 lines
- Test files co-located: `foo.test.ts` next to `foo.ts`
- No grab-bag utility files — name them by what they do
- No circular imports — extract shared types if two modules need each other
- No abstraction layers "for future flexibility" — add indirection when you have 2+ implementations
```

---

## 4. Quality Gates

Include when the project has build tools, linters, or test runners set up.

**Areas to cover:**
- Automated checks (lint, build, test — must pass before commit)
- Manual checks (developer/agent responsibilities)
- CI/CD expectations (if applicable)

**Example rules:**
```
Automated (must pass before commit):
- `pnpm check` — zero warnings, no rule disabling without a comment
- `pnpm build` — zero TypeScript errors
- `pnpm test` — all tests pass, no .skip on pre-existing tests

Manual:
- Read the module you're changing before writing code
- Run tests for the modules you touched
- If you changed a shared type, grep for all usages
```

---

## 5. Error Handling

Include for projects with external I/O (APIs, databases, file systems, user input).

**Areas to cover:**
- Error representation (Result type, exceptions, error codes)
- When to throw vs return errors
- External call handling (timeouts, retries, fallbacks)
- Error logging requirements
- Graceful degradation policy

**Example rules:**
```
- Use Result<T, E> for business logic — don't throw for expected failures
- Throw only for unexpected errors (DB crash, missing env vars)
- All external API calls: timeout + catch + skip on failure
- Pipeline errors: log + skip, never crash the process
- Log enough context to reproduce: entity ID, step name, error stack
```

---

## 6. Operational Rules

Include for long-running services, pipelines, daemons, servers.

**Areas to cover:**
- Resilience (crash recovery, graceful shutdown)
- Timeouts on external calls (with specific values)
- Data integrity (transactions, idempotency, deduplication)
- Performance constraints (latency budgets, memory limits)
- Monitoring expectations

**Example rules:**
```
Resilience:
- No single-item failure may crash the process
- All external calls must have timeouts
- Graceful shutdown on SIGINT/SIGTERM

Data integrity:
- Multi-table writes must be in a transaction
- Always validate external input (API responses, user input) with schema validation
- Idempotent processing: same input twice must not create duplicates

Performance:
- Hot-path operations must complete in <Xms
- External API calls: Ys timeout, skip on timeout
- In-memory caches must have TTL to prevent unbounded growth
```

---

## 7. Database Rules

Include when the project uses a database.

**Areas to cover:**
- Schema definition tool and migration workflow
- Transaction requirements
- Query performance (indexes, avoiding full scans)
- Data retention and cleanup
- Connection management (pooling, timeouts)

**Example rules (Drizzle + PostgreSQL):**
```
- Schema in Drizzle ORM, migrations via drizzle-kit generate → migrate
- Multi-table writes: always in a transaction
- Queries on leads/interactions must use indexes — no full table scans
- Connection pooling with appropriate pool size
- Review generated migrations before applying
```

**Example rules (Prisma + PostgreSQL):**
```
- Schema in schema.prisma, migrations via prisma migrate dev
- Use transactions for multi-model writes
- Add @index() for any column used in WHERE or ORDER BY
- Use findMany with take/skip for pagination — never load unbounded result sets
```

---

## 8. API Rules

Include when the project exposes or consumes APIs.

**Areas to cover:**
- Input validation (at the boundary)
- Response format consistency
- Error response format
- Rate limiting (if exposing APIs)
- Authentication/authorization patterns
- API versioning strategy

**Example rules:**
```
- Validate all incoming request bodies with Zod at the handler level
- Consistent error response: { error: string, code: string, details?: unknown }
- Never trust client input — validate and sanitize at the boundary
- Rate limit all public endpoints
```

---

## 9. Security Rules

Include when the project handles user data, authentication, payments, or sensitive information.

**Areas to cover:**
- Secret management (env vars, no hardcoded secrets)
- Input sanitization
- Authentication patterns
- Authorization checks
- Data exposure prevention (no sensitive data in logs, responses, or error messages)

**Example rules:**
```
- Secrets in .env, never committed — validate on boot with Zod
- Never log sensitive data (passwords, tokens, PII) at any level
- Sanitize all user input before database queries
- Auth checks at the handler level, not buried in business logic
```

---

## 10. Domain-Specific Rules

Include when the project has unique domain constraints. These are the highest-value rules because they can't be derived from the tech stack alone — they come from understanding the business domain.

**Examples by domain:**

**Telegram bot / social automation:**
```
- Never exceed rate limits — account ban kills the project
- Reply delay: random jitter before every message
- Safety validator must block: links, profit claims, urgency language
- LLM failure = skip message, never send raw template
```

**Financial application:**
```
- All monetary calculations use decimal types, never floating point
- Audit trail for every state change on financial records
- Dual-entry bookkeeping: every debit has a matching credit
```

**Healthcare / compliance:**
```
- PII must be encrypted at rest
- Access logs for every patient record read
- Data retention: auto-delete after regulatory period
```

**Real-time system:**
```
- Latency budget: end-to-end < Xms
- No blocking I/O on the hot path
- Circuit breaker on all downstream service calls
```

The skill should identify domain constraints from the project docs (PRD, README, existing safety rules) and generate domain-specific rules that address real risks in that domain.
