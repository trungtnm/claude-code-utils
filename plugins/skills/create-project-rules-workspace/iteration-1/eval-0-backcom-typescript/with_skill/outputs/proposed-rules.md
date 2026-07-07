# Proposed Project Rules -- Backcom Social Listening Agent

## Project summary

Backcom is an automated social listening system on Telegram for the forex cashback model (Exness). It runs a multi-stage pipeline -- Listen, Classify, Score, Draft Reply, Safety, Gate, Post/Queue, CRM, Timeline -- targeting 90% automation with 10% human-in-the-loop. The backend is Node.js/TypeScript with PostgreSQL (Drizzle ORM), gramjs for Telegram MTProto, Claude API for LLM classification/customization, Zod for validation, Biome for linting, and Vitest for testing. Two React/Vite frontend apps exist under `ui/` (demo dashboard and landing page) using Tailwind CSS, Framer Motion, and ESLint.

The existing CLAUDE.md is comprehensive (300+ lines) covering architecture, conventions, error handling, safety rules, and common tasks. The rules below focus on **gaps not already covered** and sharpen areas that would benefit from more specificity.

## Where should these rules live?

- **A) Add to CLAUDE.md** (recommended) -- the file already exists and is the primary source of truth. These rules fill gaps without duplicating what is already there.
- B) Create a separate `docs/QUALITY.md`
- C) Both

---

## Proposed rules

### 1. Coding Standards

> CLAUDE.md already defines naming conventions, file naming, and strict mode. These rules cover gaps.

**TypeScript strictness:**
- No `any` -- use `unknown` + type narrowing when the type is truly unknown (e.g., parsing LLM responses)
- No `@ts-ignore` or `@ts-expect-error` without a comment explaining why and a tracking TODO
- Explicit return types on all exported functions -- inferred types are fine for local helpers
- No type assertions (`as Foo`) except at validated boundaries (after Zod `.parse()`)

**Function discipline:**
- Max ~50 lines per function -- extract a named helper if longer
- Pure functions for classifiers, scorers, and safety validators -- no side effects, no DB access (already implied by module boundaries, but worth enforcing explicitly)
- No default exports -- named exports only, import directly from source file
- No barrel files (`index.ts` re-exports) except for `src/mock/index.ts` in UI demo

**Import ordering:**
- Node built-ins (`node:fs`, `node:path`) > external packages (`drizzle-orm`, `zod`, `pino`) > internal modules (`@/crm/`, `@/classifiers/`) > relative (`./utils`)
- Biome enforces this -- do not override with manual sorting

**Immutability:**
- Prefer `const` everywhere; `let` only when mutation is genuinely needed
- Pipeline data objects (`IncomingMessage`, `ClassifiedMessage`, `ScoredLead`, `DraftReply`) are read-only once created -- never mutate in place, create new objects at each pipeline stage

### 2. Testing Rules

> CLAUDE.md lists what to test (classifier, scorer, safety, dedup, etc.) but does not define how to write good tests. These rules close that gap.

**Testing philosophy:**
- Tests prove behavior, not implementation -- assert on outputs and side effects, not internal state
- Every test must be able to fail meaningfully -- if flipping a line of business logic does not break a test, that test is worthless
- No "it works" or "it handles edge case" test names -- use the pattern: `it("[expected behavior] when [condition]")`
  - Good: `it("classifies as pain_losing when message contains drawdown keywords")`
  - Good: `it("skips message entirely when LLM call times out")`
  - Bad: `it("works correctly")`

**What to test (per module):**
- `classifiers/keyword.ts` -- happy path per bucket + negative (noise message) + edge cases (mixed-language, abbreviations like "SL" and "TP")
- `classifiers/llm.ts` -- mock Claude API response + timeout/failure path (must verify skip behavior, not fallback)
- `scorers/rule-engine.ts` -- each action threshold boundary (score at threshold, score at threshold-1, score at threshold+1)
- `utils/safety.ts` -- every blocked pattern individually + combined patterns + clean messages that should pass
- `crm/operations.ts` -- upsert idempotency (same user twice = one lead), multi-account dedup
- `gate/rate-limiter.ts` -- rate limit exhaustion, cooldown recovery, jitter within expected range

**What NOT to test:**
- Pino logger configuration, YAML file loading happy path, Drizzle schema definitions
- Framework wiring (`index.ts` pipeline assembly) -- test individual stages, not the glue
- Type transformations that TypeScript already enforces

**Mocking boundaries:**
- Mock: Telegram API (gramjs), Claude API (`@anthropic-ai/sdk`), PostgreSQL (use in-memory or test DB)
- Do NOT mock: internal modules (`keyword.ts`, `rule-engine.ts`, `safety.ts`) -- test them directly
- LLM mocks must return realistic structured responses that match Zod schemas, not dummy strings

**Anti-patterns to reject:**
- `expect(result).toBeDefined()` as the only assertion -- assert the actual value
- Snapshot tests for classifier output or scored leads -- use explicit value assertions
- Tests that compute expected score the same way `rule-engine.ts` does
- Tests that require execution order between test cases
- Mocking the function under test instead of its external dependencies

**Coverage shape (per module, not % target):**
- Happy path + at least 2 edge cases + at least 1 error/failure path
- Safety validator: exhaustive coverage of every blocked pattern -- this is the highest-stakes module

### 3. Code Organization

> CLAUDE.md defines the module structure. These rules govern how to extend it.

- One module = one file unless it exceeds ~400 lines, then split by logical sub-concern
- Test files co-located: `keyword.test.ts` next to `keyword.ts`
- No grab-bag utility files -- `utils/` files are named by what they do (`safety.ts`, `config.ts`, `logger.ts`), not `helpers.ts` or `misc.ts`
- No circular imports -- if two modules need each other's types, extract shared types to `src/types.ts`
- New pipeline stage checklist:
  1. Define input/output types in `src/types.ts`
  2. Implement as pure function where possible
  3. Add timeline event emission for significant actions
  4. Write tests (happy + edge + error paths)
  5. Wire into pipeline in `src/index.ts`
  6. Document in CLAUDE.md module boundaries table

**UI apps (`ui/demo/` and `ui/landing/`):**
- Components in `components/`, pages in `pages/`, layouts in `layouts/`
- Shared UI primitives in `components/ui/` (Button, Badge, Card, etc.)
- Mock data in `mock/` -- never import mock data in production builds
- Each page is self-contained -- no cross-page state leaking

### 4. Quality Gates

**Automated (must pass before commit):**
- `pnpm check` -- Biome lint + format, zero warnings, no rule disabling without a comment
- `pnpm build` -- zero TypeScript errors
- `pnpm test` -- all tests pass, no `.skip` on pre-existing tests (`.skip` on WIP tests in the same PR is acceptable temporarily)

**For UI apps:**
- `cd ui/demo && pnpm lint` -- ESLint must pass
- `cd ui/landing && pnpm lint` -- ESLint must pass
- `cd ui/demo && pnpm build` and `cd ui/landing && pnpm build` -- zero TypeScript errors

**Manual (agent/developer responsibilities):**
- Read the module you are changing before writing code -- understand the existing conventions
- Run tests for the modules you touched, not just the file you edited
- If you changed a shared type in `src/types.ts`, grep for all usages and verify compatibility
- If you changed `config/keywords.yaml` or `config/templates.yaml`, verify the Zod schema still validates

### 5. Error Handling

> CLAUDE.md already covers Result<T, E> pattern, LLM failure = skip, and pipeline resilience. These rules add specificity.

**Timeout values:**
- Claude API calls: 30s timeout -- skip message on timeout, do not retry
- PostgreSQL queries: 10s timeout -- log error, continue pipeline (except CRM writes which should retry once)
- Telegram API calls (posting replies): 15s timeout -- push to approval queue on timeout
- YAML config reload: 5s timeout -- keep previous config on failure, log warning

**Retry policy:**
- LLM calls: NO retry -- skip message entirely (cost + latency + identical retry likely fails too)
- DB writes (CRM upsert): retry once after 1s -- if second attempt fails, log error and continue
- Telegram message send: NO retry -- push to approval queue instead
- Config file watch: retry indefinitely with backoff (config is non-critical hot path)

**Error context in logs:**
- Every error log MUST include: `{ step, messageId, groupId, accountId, error: err.message, stack: err.stack }`
- Never log full message text at error level -- use `debug` level for message content

### 6. Operational Rules

> Backcom is a long-running service. These rules prevent the common failure modes.

**Resilience:**
- No single message failure may crash the process -- every pipeline step is wrapped in try/catch
- Graceful shutdown on SIGINT/SIGTERM: stop listening, flush pending timeline events, close DB pool, then exit
- If Telegram connection drops, reconnect with exponential backoff (gramjs handles this, but verify it is configured)
- Health check: log a heartbeat every 60s with message count, queue depth, active accounts

**Rate limiting (Telegram-specific):**
- Per-group reply cooldown: configurable in `config/default.yaml`, minimum 5 minutes between replies from same account
- Per-hour cap per account: configurable, default 10 replies/hour
- Daily cap per account: configurable, default 50 replies/day
- Jitter on auto-replies: 45-180s random delay (already specified in CLAUDE.md, enforced in code)
- If any rate limit is hit, push to approval queue -- never silently drop a scored lead

**Data integrity:**
- Multi-table writes (lead + interaction + timeline) must be in a transaction
- Deduplication by `telegram_user_id` for leads, by `message_id` for interactions
- Before auto-reply: check if ANY account has already replied to this user for this message (multi-account dedup)
- Idempotent processing: reprocessing the same message must not create duplicate records

### 7. Database Rules

> CLAUDE.md covers Drizzle basics. These rules add operational specifics.

- Schema defined in `src/crm/schema.ts` -- single source of truth, no raw SQL for schema changes
- Migration workflow: `pnpm db:generate` to create migration files, review the generated SQL, then `pnpm db:migrate`
- Never edit generated migration files -- if the migration is wrong, fix the schema and regenerate
- All queries on `leads` and `interactions` tables must use indexes -- no full table scans on tables that grow unboundedly
- Connection pool: use appropriate pool size (start with 10 connections for single-instance deployment)
- Query logging: log slow queries (>1s) at `warn` level in production
- Seed data (`scripts/seed-db.ts`): must be idempotent -- safe to run multiple times

### 8. API Rules

> Backcom consumes external APIs (Telegram MTProto, Claude API) and may expose internal APIs later.

**Claude API consumption:**
- Always validate LLM responses with Zod schema before using -- never trust raw LLM output
- Include system prompt version in logs for debugging classification drift
- Token usage logging: log input/output token counts per call for cost monitoring
- If LLM returns unparseable response: treat as LLM failure (skip message), do not attempt string manipulation fallback

**Telegram API consumption:**
- All Telegram API calls must handle `FloodWaitError` -- wait the specified duration, do not hammer
- Session persistence: gramjs sessions must be saved to disk, not just in-memory
- Message parsing: normalize Unicode, strip zero-width characters, handle edited messages vs new messages

### 9. Security Rules

> Backcom handles Telegram account credentials and user data. These are non-negotiable.

- Secrets (API keys, Telegram sessions, DATABASE_URL) in `.env` -- never committed, never logged
- Validate all env vars on boot with Zod -- fail fast with clear error message naming the missing variable
- Never log Telegram session strings, API keys, or user phone numbers at any level
- Never include PII (telegram_user_id, username, full message text) in error responses or external logs
- Telegram session files: store outside repo root, set restrictive file permissions
- Rate limit and safety validator cannot be disabled via config -- only via code change (prevents accidental misconfiguration)
- `.env.example` must exist and stay current -- but must never contain real values

### 10. Domain-Specific Rules: Telegram Social Listening + Forex Compliance

> These rules come from the project's specific domain constraints. Violating them risks account bans, legal issues, or destroyed trust.

**Account safety (ban prevention):**
- Never exceed Telegram rate limits -- getting banned kills the entire operation
- Reply delay: always apply random jitter (45-180s) before auto-posting -- synchronous replies are a bot detection signal
- Warm up new accounts 2-4 weeks before activating for auto-replies (manual lurking + occasional activity)
- If account health score drops below 50: route all replies to approval queue (kill switch)
- Monitor for `FloodWaitError` and `UserBannedInChannelError` -- these are early warning signals

**Content safety (compliance + trust):**
- ALL draft replies MUST pass `SafetyValidator` before sending -- no exceptions, no bypass
- Blocked content in public replies: links (ref links, t.me, bit.ly), broker names (Exness), profit claims, urgency language ("hurry", "limited time"), competitor criticism, specific cashback numbers
- LLM failure = skip message entirely -- never send raw template text (identical replies = bot detection signal)
- Reply templates: maximum 500 characters, 4-5 lines -- longer replies look like copypasta
- NFA disclaimer required on website and Telegram bot screens
- No unsolicited DMs -- user must reply to us first before any DM outreach

**Operator workflow:**
- Rejection in approval queue requires mandatory reason -- no silent rejections
- Rejection reasons feed back into template improvement and classifier tuning
- All significant actions create immutable timeline events -- this is the audit trail
- Template effectiveness tracking: measure reply-back rate per template variant per persona

**Vietnamese language (per global CLAUDE.md rules):**
- All Vietnamese text in the codebase MUST use proper diacritical marks
- This applies to: UI labels, user-facing strings, comments, seed data display values
- Exception: programmatic slugs/keys used for lookup matching may omit diacritics if ASCII-safe identifiers are required

---

## Summary of what these rules add beyond existing CLAUDE.md

| Category | What is new |
|---|---|
| Coding standards | `any` ban, no type assertions outside validated boundaries, import ordering, immutability of pipeline data objects |
| Testing rules | Complete testing philosophy, naming conventions, per-module test expectations, anti-patterns list, mocking boundaries |
| Code organization | New pipeline stage checklist, UI app organization rules, grab-bag file prohibition |
| Quality gates | Explicit commands to run before commit (backend + both UI apps), manual checklist |
| Error handling | Specific timeout values per external call, explicit retry policy per integration |
| Operational rules | Heartbeat logging, graceful shutdown checklist, rate limit escalation to approval queue |
| Database rules | Migration review process, slow query logging, idempotent seeds |
| API rules | LLM response validation enforcement, token usage logging, Telegram FloodWaitError handling |
| Security rules | Session file permissions, safety validator cannot be config-disabled, PII logging prohibition |
| Domain-specific | Account health kill switch threshold, warm-up period, template size limits, rejection reason enforcement |
