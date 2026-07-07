## Project Summary

**task-queue** is a lightweight TypeScript/Express service that exposes a REST API for submitting and querying background jobs via BullMQ backed by Redis. It uses Zod for request validation, Vitest for testing, and ESLint for linting. The codebase is small (3 source files) with no existing CLAUDE.md or quality conventions.

## Where should these rules live?

- **A) Create a `CLAUDE.md`** at the project root (recommended — no existing one, and the project is small enough that a single file covers everything)

---

## Proposed Rules

### 1. Coding Standards

- Strict TypeScript — no `any`, no `ts-ignore` without a comment explaining why
- Named exports only, no default exports
- Explicit return types on all exported functions and route handlers
- Max ~50 lines per function — extract a named helper if longer
- Prefer `interface` over `type` for object shapes
- Import order: Node built-ins, then external packages (`express`, `bullmq`, `ioredis`, `zod`), then local modules (`./redis`, `./routes`)
- All Zod schemas defined as named `const` at module scope, not inline in handlers
- No classes unless the domain requires stateful instances — prefer plain functions and objects

### 2. Testing Rules

**Philosophy:**
- Tests prove behavior, not implementation — test what the API returns, not how BullMQ is called internally
- Every test must be able to fail meaningfully — if it can't catch a real bug, delete it

**What to test:**
- Route handlers: valid input produces correct job response, invalid input returns 400 with Zod errors, missing job returns 404
- Zod schemas: valid payloads pass, invalid payloads fail with correct error shape
- Happy path + at least 2 edge cases + at least 1 error path per route

**What NOT to test:**
- Express wiring (`app.use` calls), Redis connection setup
- BullMQ internals — mock the Queue at the boundary, don't test BullMQ itself

**Mocking boundaries:**
- Mock `Queue` (external dependency on Redis) — use a fake or stub that records `.add()` and `.getJob()` calls
- Do NOT mock Zod validation — let it run against real schemas
- Use `supertest` or similar to test routes through Express, not by calling handler functions directly

**Test naming:**
- Pattern: `it("[expected behavior] when [condition]")`
- Example: `it("returns 400 with validation errors when payload is missing type field")`
- Example: `it("returns 404 when job ID does not exist")`
- No vague names like `it("works")` or `it("handles edge case")`

**Anti-patterns to reject:**
- Tests that only assert `toBeDefined()` or `not.toBeNull()`
- Tests that compute expected values the same way the code does
- Snapshot tests on API response bodies
- Mocking Zod (the schema under test) instead of letting it validate

**Running tests:**
- `pnpm test` via Vitest — all tests must pass before committing
- Test files co-located: `routes.test.ts` next to `routes.ts`

### 3. Code Organization

- One module = one file unless it exceeds ~400 lines — this project is small, keep it flat
- Test files co-located: `foo.test.ts` next to `foo.ts` in `src/`
- No grab-bag `utils.ts` — name files by what they do (e.g., `validation.ts`, `redis.ts`)
- Keep route handlers thin: validation at the top, then delegate to a service function if logic grows beyond simple queue operations
- If workers are added later, put them in `src/workers/` — separate from API route code

### 4. Quality Gates

**Automated (must pass before commit):**
- `pnpm lint` — zero ESLint warnings, no rule disabling without a comment
- `pnpm build` — zero TypeScript errors
- `pnpm test` — all Vitest tests pass, no `.skip` on pre-existing tests

**Manual:**
- Read the module you are changing before writing code
- Run `pnpm test` for the modules you touched
- If you changed a Zod schema, verify that both valid and invalid inputs are covered in tests

### 5. Error Handling

- Use Zod `.safeParse()` at the API boundary — never `.parse()` in route handlers (avoid uncaught ZodError)
- Consistent error response shape: `{ error: string | object }` with appropriate HTTP status codes (400 for validation, 404 for not found, 500 for unexpected)
- Wrap all `queue.add()` and `queue.getJob()` calls in try/catch — Redis may be unavailable
- On Redis/BullMQ failure: return 503 with `{ error: "Service temporarily unavailable" }` — never expose internal error details to clients
- Log enough context to reproduce: job type, job ID, error message and stack

### 6. Operational Rules

**Resilience:**
- No single failed job submission may crash the Express process — all async route handlers must catch errors
- Redis connection: handle `ioredis` connection errors and reconnection — do not let unhandled rejection kill the process
- Graceful shutdown on SIGINT/SIGTERM: close the Express server, then close the Redis connection and BullMQ queue

**Configuration:**
- Redis URL via `REDIS_URL` env var — validate on boot (fail fast if Redis is unreachable)
- Port via `PORT` env var with fallback to 3000
- No hardcoded secrets or connection strings in source code

**Performance:**
- BullMQ queue operations should complete in <100ms under normal load — if Redis latency spikes, the 503 fallback catches it
- Do not load full job data when only status is needed — use `job.getState()` without fetching logs/stacktrace

### 7. API Rules

- Validate all incoming request bodies with Zod at the handler level — already in place, maintain this pattern for any new routes
- Consistent error response format: `{ error: string | object }` with HTTP status codes (400, 404, 503)
- Never trust client input — `req.params.id` should be validated (e.g., non-empty string) before querying BullMQ
- All new endpoints must follow the same pattern: parse with Zod, handle business logic, return consistent response shape
- Document expected request/response shapes as Zod schemas — they serve as the living API documentation

### 8. Security Rules

- Secrets (Redis URL, any future API keys) in environment variables, never committed to source
- Add `.env` to `.gitignore` — do not commit `.env` files
- Never expose internal error stacks or Redis connection details in API responses
- Validate and sanitize `req.params.id` before passing to BullMQ — prevent injection of unexpected values
- If this service becomes publicly accessible: add rate limiting to POST `/api/tasks` to prevent queue flooding
