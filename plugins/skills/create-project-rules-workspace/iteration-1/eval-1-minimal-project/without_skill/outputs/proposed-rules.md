# Quality Guidelines & Coding Standards for `task-queue`

## Project Overview

- **Name:** task-queue v0.1.0
- **Runtime:** Node.js with ESM (`"type": "module"`)
- **Language:** TypeScript 5.4+
- **Framework:** Express 4.x
- **Key Libraries:** BullMQ (job queue), ioredis (Redis client), Zod (validation)
- **Tooling:** tsx (dev runner), vitest (testing), ESLint (linting), tsc (build)

---

## 1. TypeScript Rules

### Strict Mode
- Enable `"strict": true` in `tsconfig.json`. All strict family flags must remain on.
- Never use `any`. Use `unknown` and narrow with type guards, or use Zod's inferred types (`z.infer<typeof Schema>`).

### Type Safety
- All function parameters and return types must be explicitly typed for exported functions.
- Internal/private functions may rely on inference, but add annotations when the inferred type is not obvious.
- Use `as const` assertions for literal unions instead of manual enum-like objects.

### Module System
- Use ESM imports exclusively (`import`/`export`). No `require()` calls.
- Use `.js` extensions in import paths if required by the TypeScript/ESM configuration.
- Barrel files (`index.ts` re-exports) are allowed only at module boundaries, not within a single feature.

---

## 2. Express & API Rules

### Route Organization
- Each domain (e.g., tasks, workers, health) gets its own router file in `src/routes/` or `src/<domain>/router.ts`.
- Routers must be pure -- they receive dependencies via factory functions or parameters, not by importing singletons directly. The current pattern of importing `redis` and creating a `Queue` inside `routes.ts` should be refactored to dependency injection.

### Request Validation
- Every route that accepts a body, query, or params MUST validate input with a Zod schema before processing.
- Zod schemas live alongside or co-located with the route that uses them, in a `schemas.ts` file if there are more than two schemas per route file.
- Always use `.safeParse()`, never `.parse()` in route handlers (avoid throwing).

### Response Format
- All API responses follow a consistent envelope: `{ data: T }` for success, `{ error: string | object }` for failure.
- Always set explicit HTTP status codes. Do not rely on Express defaults.
- Return `res.status(...)` with `.json(...)` -- never send plain text from API routes.

### Error Handling
- Every `async` route handler must be wrapped in a try/catch or use an async error wrapper middleware to prevent unhandled promise rejections from crashing the server.
- Create a centralized Express error-handling middleware (`(err, req, res, next)`) registered after all routes.
- Never expose internal error details (stack traces, Redis connection strings) in API responses.

---

## 3. Redis & BullMQ Rules

### Connection Management
- A single Redis connection instance must be created and shared. Never create multiple `new Redis()` calls across files.
- The current duplication (Queue created in both `index.ts` and `routes.ts` with separate connections) must be eliminated. Create the Queue once and inject it.
- Redis configuration must come from environment variables. The fallback `redis://localhost:6379` is acceptable only for local development.

### Queue Configuration
- Queue names must be defined as constants in a shared config, not as inline strings.
- All jobs must define a `removeOnComplete` and `removeOnFail` policy to prevent unbounded Redis memory growth.
- Use BullMQ's built-in retry with exponential backoff. Define default retry options per queue.

### Worker Safety
- Workers (when added) must handle `failed` and `error` events. Unhandled worker errors crash the process.
- Workers must implement graceful shutdown: listen for `SIGTERM`/`SIGINT`, call `worker.close()`, and drain the queue.

---

## 4. Configuration & Environment

### Environment Variables
- Use a `.env` file for local development (add `.env` to `.gitignore`).
- Define a Zod schema to validate all required environment variables at startup. Fail fast with a clear message if any are missing.
- Required variables: `REDIS_URL`, `PORT`.
- Never commit secrets or credentials to the repository.

### Application Config
- Centralize configuration in a `src/config.ts` file that reads from `process.env`, validates with Zod, and exports typed config.
- The Express port (`3000`) must not be hardcoded -- read from `process.env.PORT`.

---

## 5. Project Structure

```
src/
  index.ts          # App entry point -- bootstrap only, no business logic
  config.ts         # Environment validation and typed config export
  redis.ts          # Single Redis connection factory
  queue.ts          # Queue creation and shared queue instances
  routes/
    tasks.ts        # Task-related routes
    health.ts       # Health check endpoint
  schemas/
    task.ts         # Zod schemas for task operations
  workers/
    taskWorker.ts   # BullMQ worker for processing tasks
  middleware/
    errorHandler.ts # Centralized error handling middleware
    validate.ts     # Generic Zod validation middleware
  types/
    index.ts        # Shared TypeScript types/interfaces
```

---

## 6. Testing Rules

### Framework
- Use vitest as the sole test runner. Tests must pass before merging.
- Test files live adjacent to source files as `<name>.test.ts` or in a `__tests__/` directory.

### Coverage Requirements
- Minimum 80% line coverage for `src/` (excluding `index.ts` bootstrap).
- All Zod schemas must have validation tests covering valid input, invalid input, and edge cases.
- All route handlers must have integration tests using `supertest`.

### Test Isolation
- Tests must not depend on a running Redis instance by default. Mock `ioredis` and BullMQ in unit tests.
- Integration tests that need Redis must use a dedicated test Redis database (e.g., DB index 1) or a testcontainers-based Redis.
- Each test must be independent -- no shared mutable state between tests.

### Test Naming
- Use descriptive test names: `it('returns 400 when task type is invalid')`, not `it('test1')`.
- Group related tests with `describe()` blocks matching the function or route under test.

---

## 7. Error Handling & Logging

### Logging
- Use a structured logger (e.g., `pino`) instead of `console.log`. Log JSON objects with context fields.
- Log levels: `error` for failures requiring action, `warn` for degraded states, `info` for operational events, `debug` for development diagnostics.
- Every log entry related to a job must include the `jobId`.

### Process Lifecycle
- The entry point must handle `SIGTERM` and `SIGINT` for graceful shutdown: close the Express server, close BullMQ queues/workers, then close the Redis connection.
- Use `process.on('unhandledRejection')` and `process.on('uncaughtException')` as safety nets -- log the error and exit with a non-zero code.

---

## 8. Code Style & Linting

### ESLint
- Extend `eslint:recommended` and `@typescript-eslint/recommended`.
- Enable `no-unused-vars` (error), `no-console` (warn -- prefer structured logger), `@typescript-eslint/no-explicit-any` (error).
- Enable `@typescript-eslint/consistent-type-imports` to enforce `import type` for type-only imports.

### Formatting
- Use a consistent formatter (Prettier or Biome). Configure it and enforce via CI.
- 2-space indentation, single quotes, no semicolons (or with semicolons -- pick one and enforce it project-wide).
- Maximum line length: 100 characters.

### Naming Conventions
- Files: `camelCase.ts` for modules, `PascalCase.ts` for classes.
- Variables/functions: `camelCase`.
- Types/interfaces: `PascalCase`. No `I` prefix on interfaces.
- Constants: `UPPER_SNAKE_CASE` for true compile-time constants, `camelCase` for runtime config.
- Zod schemas: `PascalCase` ending in `Schema` (e.g., `CreateTaskSchema`).

---

## 9. Git & CI

### Commit Messages
- Follow Conventional Commits: `type(scope): description` (e.g., `feat(queue): add retry with backoff`).
- Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `ci`.

### Branch Strategy
- Feature branches off `main`. Branch naming: `type/short-description` (e.g., `feat/task-retry`).
- Squash merge to `main`.

### CI Pipeline
- Required checks before merge: `lint`, `typecheck` (`tsc --noEmit`), `test` (vitest with coverage).
- Add a `typecheck` script to package.json: `"typecheck": "tsc --noEmit"`.

---

## 10. Security

- Never log or return `REDIS_URL` or other secrets in responses or logs.
- Validate and sanitize all user input at the API boundary using Zod.
- Set Express security headers (use `helmet` middleware).
- Rate-limit the task creation endpoint to prevent queue flooding.
- Set a `maxBodyLength` / payload size limit on `express.json()` (e.g., `express.json({ limit: '100kb' })`).

---

## 11. Dependency Management

- Pin major versions in `package.json` (use `^` for minor/patch, which is the current approach).
- Run `npm audit` in CI and fail on high/critical vulnerabilities.
- Keep `devDependencies` and `dependencies` properly separated -- never ship test tools to production.

---

## Summary of Immediate Action Items

| Priority | Issue | Action |
|----------|-------|--------|
| P0 | Duplicate Queue + Redis instances in `index.ts` and `routes.ts` | Create a single shared Queue instance and inject it |
| P0 | No async error handling in route handlers | Add try/catch or async wrapper middleware |
| P0 | Hardcoded port | Read from `process.env.PORT` |
| P1 | No graceful shutdown | Handle SIGTERM/SIGINT |
| P1 | No env validation | Add Zod-based config validation at startup |
| P1 | No health check endpoint | Add `GET /health` that pings Redis |
| P1 | `console.log` usage | Replace with structured logger |
| P2 | No test files exist | Add route and schema tests |
| P2 | No `tsconfig.json` in repo | Add with strict mode enabled |
| P2 | No error handling middleware | Add centralized Express error handler |
