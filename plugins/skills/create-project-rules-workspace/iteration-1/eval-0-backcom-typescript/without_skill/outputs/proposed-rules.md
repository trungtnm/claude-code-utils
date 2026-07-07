# Proposed Project Rules — Backcom Social Listening Agent

## 1. Coding Standards

### TypeScript Rules

- **Strict mode always** (`strict: true` in tsconfig). No `any` type. No `// @ts-ignore` without an adjacent comment explaining the specific reason.
- Prefer `interface` over `type` for object shapes -- interfaces are extendable and produce clearer error messages.
- Explicit return types on all exported functions. Inferred return types are acceptable on internal/private functions.
- **Named exports only** -- no default exports. Named exports improve refactoring and grep-ability across the codebase.
- **No barrel files** (`index.ts` re-exports). Import directly from the source module.
- Prefer `readonly` for data that should not mutate after creation.
- No classes unless the domain genuinely requires stateful instances (e.g., `TelegramClient` wrapper). Prefer plain functions + types.
- Use `Result<T, E>` pattern for expected business logic failures. Reserve `throw` for truly unexpected errors (DB crash, network failure, missing env vars).

### Import Ordering

Imports must follow this order, with a blank line between each group:

1. Node built-ins (`node:fs`, `node:path`)
2. External packages (`drizzle-orm`, `zod`, `pino`, `telegram`)
3. Internal modules (`@/crm/operations`, `@/utils/logger`)
4. Relative imports (`./types`, `../schema`)

### Function Rules

- Maximum ~50 lines per function. If longer, extract a named helper.
- Single responsibility -- one function does one thing.
- Pure functions preferred. Side effects are pushed to the pipeline edges (listener entry, poster exit, CRM writes).
- No nested callbacks deeper than 2 levels. Extract or use async/await.

---

## 2. Naming Conventions

| What | Style | Example |
|---|---|---|
| Files | `kebab-case.ts` | `rule-engine.ts` |
| Types / Interfaces | `PascalCase` | `ScoredLead`, `IncomingMessage` |
| Functions / variables | `camelCase` | `classifyMessage`, `canReply` |
| Constants | `UPPER_SNAKE_CASE` | `BLOCKED_PATTERNS`, `MAX_RETRY` |
| DB columns | `snake_case` | `first_seen_at`, `telegram_user_id` |
| Config keys (YAML) | `snake_case` | `auto_reply_threshold` |
| Event types | `domain.action` | `reply.auto_posted`, `lead.created` |
| Test descriptions | `it("[expected behavior] when [condition]")` | `it("returns pain_losing bucket when message contains SL keywords")` |

---

## 3. Code Organization

### File Rules

- One module = one file, unless it exceeds ~400 lines. Then split by sub-concern.
- Test files co-located with source: `keyword.test.ts` next to `keyword.ts`.
- No `utils/helpers.ts` grab-bag files. If a utility serves one module, keep it there. If it serves 2+ modules, give it a descriptive name (`text-normalizer.ts`, not `helpers.ts`).

### Dependency Direction

Follow the pipeline flow. A module may import from upstream modules, never from downstream:

```
listeners -> classifiers -> scorers -> drafters -> gate -> poster -> crm -> timeline
```

- `types.ts` and `utils/` are shared foundations -- any module may import from them.
- No circular imports. If two modules need each other, extract the shared type into `types.ts`.

### Module Boundaries

Each module communicates through typed interfaces, never by reaching into another module's internals:

| Module | Boundary | Key Rule |
|---|---|---|
| Intake (listeners/) | Raw Telegram -> IncomingMessage | Source-specific noise MUST NOT leak downstream |
| Classification (classifiers/) | IncomingMessage -> ClassifiedMessage | Pure function of message content. No side effects |
| Scoring (scorers/) | ClassifiedMessage -> ScoredLead | Pure function of classified data + config. No DB access |
| Drafting (drafters/) | ScoredLead -> DraftReply | Template + LLM. No posting, no DB |
| Safety (utils/safety.ts) | DraftReply -> Result<true, reason> | Pure validation. No side effects |
| Gate (gate/) | DraftReply -> "auto" or "queue" or "blocked" | Rate limiter has state. Confidence gate is pure |
| Posting (poster/) | DraftReply -> PostResult | Only module that sends Telegram messages |
| CRM (crm/) | Pipeline results -> DB | Only module that writes to leads/interactions |
| Timeline (timeline/) | Events -> timeline_events table | Append-only. Non-blocking. Best-effort |

### What NOT to Create

- No `constants.ts` file. Constants live in the module that uses them, or in config YAML.
- No `interfaces/` directory. Types live in `types.ts` or co-located with their module.
- No abstraction layers "for future flexibility". Add indirection only when you have 2+ concrete implementations.

---

## 4. Testing Rules

### Philosophy

- Tests prove behavior, not implementation. Test what the code *does*, not how it does it internally.
- Every test must be able to fail meaningfully. If you cannot describe a scenario where the test catches a real bug, delete it.
- No "status 200" tests. Asserting that a function returns without throwing is not a test. Assert the actual output value, shape, or side effect.

### Test Structure (AAA Pattern)

- **Arrange** -- set up inputs and expected state
- **Act** -- call the function under test exactly once
- **Assert** -- verify output AND verify what did NOT happen when relevant (e.g., safety validator blocks -> verify no reply was sent)

### What to Test

- **DO test:** business logic (classifier, scorer, safety validator, template selection), edge cases (empty input, unicode, forex abbreviations like SL/TP/BE/PA/SMC/DD), error paths (LLM timeout -> skip behavior)
- **DO NOT test:** framework wiring, config file loading happy path, simple type transformations, private helper internals
- **DO NOT mock what you own.** If you control both sides, test them together. Mock only external boundaries (Telegram API, Claude API, database in unit tests).

### Coverage Rules

- No numeric coverage target. Coverage percentage incentivizes bad tests.
- Every module's test file must cover: the happy path, at least 2 edge cases, and at least 1 error path.
- Classifier and safety validator require exhaustive edge case coverage -- these are the highest-risk modules.

### Test Anti-Patterns (Reject These)

- Snapshot tests for business logic
- Tests that duplicate implementation logic (computing expected value the same way the code does)
- Tests that only assert `toBeDefined()` or `not.toBeNull()` -- assert the actual value
- Tests that require specific execution order
- Mocking the function under test itself

### Required Test Scenarios

- Classifier: keyword matching (exact, partial, multi-bucket, no match, forex abbreviations)
- Safety validator: blocked patterns (links, broker names, profit claims, urgency), clean passes, edge cases
- Scorer: bucket scoring, bonus/penalty application, threshold actions
- Pipeline integration: mock message -> classify -> score -> draft -> safety -> gate decision
- Deduplication: same user from multiple groups -> one lead
- LLM failure -> skip behavior (no raw template sent)
- Kill switch: all replies go to queue when active
- Rejection reason: mandatory reason on reject

---

## 5. Error Handling

- Use `Result<T, E>` pattern for business logic. Do not throw for expected failures.
- Throw only for unexpected errors (DB crash, network failure, missing env vars).
- All LLM calls: try/catch + 30-second timeout. **LLM failure = skip message entirely. Never send raw template text.** Identical template replies are a bot detection signal.
- Pipeline errors: log + skip message. NEVER crash the process.
- Safety validation failure: block reply + push to approval queue with SAFETY flag.
- Timeline event write failure: log error + continue (non-blocking, best-effort).
- Telegram FloodWait: log warning, back off. Never retry immediately.
- Database connection lost: retry with exponential backoff, alert after 3 consecutive failures.

---

## 6. Logging Rules

- Every pipeline step must log structured data: `logger.info({ step, messageId, groupId, accountId, ...context })`
- Sensitive data (full message text, user info) only at `debug` level.
- Error logs must include enough context to reproduce: messageId, groupId, accountId, step, error stack.
- Rate limit events: log at `info` level.
- Safety violations: log at `warn` level.
- Account health changes: log at `info` level.
- Kill switch events: log at `warn` level.

---

## 7. Config Rules

- No hardcoded magic numbers. Everything goes in `config/default.yaml`.
- Secrets (API keys, sessions, DATABASE_URL) go in `.env`. NEVER commit secrets.
- **Validate env on boot using Zod.** Never access raw `process.env` in business logic.
- Keywords and templates are separate YAML files. Target hot-reload without restart.
- Zod schema validates all config on load. Fail fast if config is invalid.
- Per-group config (Phase 4+): type, priority, rate_limit overrides, active_hours, assigned accounts.
- Per-account config (Phase 4+): persona, template_set, health thresholds.

---

## 8. Database Rules

- Schema defined with Drizzle ORM in `src/crm/schema.ts`.
- Migrations via `drizzle-kit generate` then `drizzle-kit migrate`.
- All write operations touching >1 table must be in a transaction.
- PostgreSQL connection pooling with appropriate pool size.
- Full text stored permanently -- no auto-delete retention policy.
- **Deduplication:** upsert by `telegram_user_id`. One lead per unique user, regardless of group count.
- **Idempotent processing:** same `message_id` must never create duplicate interactions.
- **Multi-account dedup (Phase 4+):** before replying, check if ANY account has already replied to this user for this message.
- Database queries must use indexes. No full table scans on `leads` or `interactions` tables.

---

## 9. Operational Rules

### Resilience

- No single message failure may crash the process. Catch at pipeline entry, log, skip, continue.
- All external calls (Telegram API, Claude API, database) must have timeouts.
- Telegram FloodWait -> log warning, back off, never retry immediately.
- Database connection lost -> retry with exponential backoff, alert after 3 failures.

### Data Integrity

- Every database write touching >1 table must be in a transaction.
- Never trust LLM output structure -- always validate with Zod before using.
- Never trust Telegram event payload shape -- validate/normalize at the listener boundary.
- Idempotent processing: same `message_id` processed twice must produce the same result, not duplicate records.

### Performance

- Keyword classifier must complete in <10ms. No async operations, no external calls.
- LLM calls must have a 30-second timeout. Skip on timeout, never block the pipeline.
- Database queries must use indexes. No full table scans on `leads` or `interactions` tables.
- In-memory dedup set (processed message IDs) must have a TTL to prevent unbounded memory growth.

---

## 10. Timeline Event Rules

- Every significant action MUST create a timeline event.
- Events are immutable -- never update or delete.
- Events are append-only in `timeline_events` table.
- Timeline writes are non-blocking -- failures do not break the pipeline.
- Event types follow `domain.action` naming: `message.received`, `message.classified`, `reply.auto_posted`, `lead.created`, etc.
- Events include: `occurred_at`, `entity_id` (lead_id), `actor_type`, `actor_id`, `payload`.
- Account health changes and kill switch activations are also timeline events.

---

## 11. Safety Rules -- NEVER Violate

These are hard rules enforced in code via `SafetyValidator`. All draft replies must pass before sending.

- **NEVER** claim profits or trading results
- **NEVER** send links (ref link, t.me, bit.ly) in public replies -- only in DMs
- **NEVER** mention broker or product names in public replies -- suggest DM if asked directly
- **NEVER** DM a user without prior engagement (user must reply to us first)
- **NEVER** exceed rate limits -- getting banned kills the project
- **NEVER** use urgency language ("hurry", "limited time", "limited spots")
- **NEVER** badmouth competitors
- **NEVER** promise specific cashback numbers in public replies
- **NEVER** send raw template text when LLM fails -- skip the message entirely
- **NFA disclaimer** on website and relevant Telegram bot screens
- Reply length: maximum 500 characters, 4-5 lines
- Reply delay: random jitter of 45-180 seconds before every reply to appear natural

---

## 12. Quality Gates

### Automated (Must Pass Before Commit)

| Gate | Command | Rule |
|---|---|---|
| Lint + Format | `pnpm check` | Biome lint + format. No warnings allowed. No rule disabling without a comment explaining why. |
| Type Check | `pnpm build` | TypeScript compilation with zero errors. No `// @ts-ignore` without an adjacent comment. |
| Tests | `pnpm test` | All tests pass. No `.skip` or `.todo` on pre-existing tests. Only on new work-in-progress tests. |

### Manual (Developer/Agent Responsibility)

- Read the module you are changing before writing code. Understand context first.
- Run tests for the modules you touched, not just the full suite.
- If you changed a type in `types.ts`, grep for all usages and verify nothing breaks downstream.
- Verify that new code follows module boundary rules and dependency direction.

---

## 13. UI Rules (Demo Dashboard + Landing Page)

The `ui/` directory contains two Vite + React + TypeScript + Tailwind CSS applications:

### Shared UI Standards

- **React 19** with functional components only. No class components.
- **TypeScript strict mode.** Props interfaces for all components.
- Use `clsx` + `tailwind-merge` for conditional class composition.
- Tailwind CSS 4.x for all styling. No inline styles. No CSS modules.
- Component files in PascalCase: `StatCard.tsx`, `Badge.tsx`.
- Page files in PascalCase: `Overview.tsx`, `LeadDetail.tsx`.
- Mock data isolated in `src/mock/` directory with typed exports.
- **ESLint** for linting (project uses eslint, not biome, for UI packages).
- Use `lucide-react` for icons. Do not mix icon libraries.
- Use `framer-motion` for animations. Keep animations subtle and purposeful.

### Component Organization

- Reusable UI primitives in `src/components/ui/` (Button, Badge, Card, Modal, Table, etc.)
- Page components in `src/pages/` organized by feature area (dashboard/, landing/, telegram/, tools/)
- Layout components in `src/layouts/` (DashboardLayout, LandingLayout)
- No component file should exceed ~300 lines. Extract sub-components when needed.

---

## 14. Vietnamese Language Rules

All Vietnamese text in the codebase **MUST** use proper diacritical marks. Vietnamese without diacritics is incorrect and ambiguous.

- Always write Vietnamese with full diacritics: `Ung vien` is wrong, `Ung vien` must be `ung vien` -> correct form is `ung vien` with marks, i.e. write the proper Vietnamese characters.
- This applies to: AI prompts, UI labels, user-facing strings, comments, seed data display values.
- Exception: programmatic slugs/keys used for lookup matching (e.g., `"ha_noi"` as a key) may omit diacritics if the system requires ASCII-safe identifiers.
- **No `\u` Unicode escapes in JSX text content.** Always write actual UTF-8 characters. If building text programmatically, use a JS expression: `<Text>{'Lo\u1EA1i'}</Text>`.

---

## 15. Project-Specific Conventions

### Pipeline Architecture

The core pipeline is a linear data transformation chain. Every new feature must respect this flow:

```
Listen -> Classify -> Score -> Draft Reply -> Safety Check -> Gate -> Post/Queue -> CRM -> Timeline
```

- Each step transforms the previous data type into the next.
- Steps must not skip ahead or reach back into earlier stages.
- New pipeline steps are inserted, not appended, at the appropriate position.

### Phase Discipline

- Never skip a phase. Each phase's data validates the next.
- Phase 1-3: single Telegram account only. Multi-account is Phase 4+.
- Listening is decoupled from replying. Phase 1 delivers value with zero ban risk.
- Do not build Phase 4+ features (accounts/, attribution/, dm/) until Phase 3 graduation criteria are met.

### Config-Driven Behavior

- Scoring thresholds, rate limits, cooldowns, jitter ranges -- all in YAML config, never hardcoded.
- Template content lives in `config/templates.yaml`, keyword buckets in `config/keywords.yaml`.
- Adding a keyword bucket or template variant should never require a code change.

### Build and Run Commands

```bash
pnpm install          # Install dependencies
pnpm dev              # Dev mode (tsx watch)
pnpm build            # Compile TypeScript
pnpm start            # Run compiled JS
pnpm test             # Run tests (vitest)
pnpm check            # Biome lint + format check
pnpm check:fix        # Auto-fix lint issues
pnpm db:generate      # Generate Drizzle migrations
pnpm db:migrate       # Run migrations
pnpm db:studio        # Open Drizzle Studio (DB browser)
```
