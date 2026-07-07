# Proposed Project Rules: Inventory API

## Project Summary

This is a **Product Inventory Management API** built with FastAPI, SQLAlchemy 2.0, and PostgreSQL. It tracks stock levels, restocking events, and real-time availability across multiple warehouses. The project uses Pydantic v2 for validation, Alembic for migrations, Ruff for linting, and mypy in strict mode for type checking. It targets Python 3.11+.

## Where should these rules live?

- **A) Create CLAUDE.md** (recommended -- no CLAUDE.md exists yet, and this is a fresh project that would benefit from having AI-readable conventions from the start)

---

## Proposed Rules

### 1. Coding Standards

- Type hints on all functions (public and private) -- mypy strict mode is already enabled, keep it passing with zero errors
- No `# type: ignore` without an inline comment explaining why the suppression is necessary
- Prefer Pydantic models over raw dicts for all structured data crossing boundaries (request/response bodies, config, service inputs/outputs)
- Use SQLAlchemy 2.0-style `Mapped[]` type annotations on all model columns instead of legacy `Column()` without type hints -- e.g., `name: Mapped[str] = mapped_column(String, nullable=False)`
- Max ~40 lines per function -- extract a named helper if longer
- Imports ordered: stdlib, then third-party, then local (`app.*`), separated by blank lines -- Ruff enforces this via `isort` rules
- No wildcard imports (`from module import *`)
- Use `from __future__ import annotations` in all modules for forward-reference support
- Use `datetime.now(tz=datetime.UTC)` instead of deprecated `datetime.utcnow()`
- Use `Decimal` for monetary values (`price` field) -- never `Float` for prices. SQLAlchemy `Numeric` column type maps to `Decimal`

### 2. Testing Rules

**Testing philosophy:**
- Tests prove behavior, not implementation -- assert on response bodies and database state, not on internal function calls
- Every test must be able to fail meaningfully -- if removing a line of business logic wouldn't break any test, coverage is insufficient
- Use `pytest-asyncio` for all async endpoint and database tests

**What to test:**
- Every API endpoint: happy path + at least 2 edge cases (e.g., duplicate SKU, negative quantity) + at least 1 error path (e.g., product not found)
- Business logic: stock level calculations, restocking events, warehouse-level availability
- Database constraints: unique SKU enforcement, foreign key integrity, non-nullable fields

**What NOT to test:**
- FastAPI/Uvicorn wiring (e.g., that `include_router` works)
- SQLAlchemy ORM basics (e.g., that `relationship()` returns related objects)
- Simple Pydantic schema definitions with no custom validators

**Mocking boundaries:**
- Mock external HTTP calls (via `httpx`) when testing endpoints that call third-party services
- Use a real test database (SQLite in-memory or test PostgreSQL) for repository/model tests -- do not mock SQLAlchemy sessions for integration tests
- Use FastAPI's `TestClient` (or `httpx.AsyncClient` with `ASGITransport`) for endpoint tests

**Test naming:**
- Pattern: `test_[expected_behavior]_when_[condition]`
- Example: `test_returns_404_when_product_not_found`, `test_decrements_stock_when_order_placed`
- No vague names: `test_inventory()` or `test_it_works()`

**Test structure:**
- Follow AAA pattern: Arrange (set up data), Act (call endpoint/function), Assert (check result)
- One logical assertion per test -- multiple `assert` statements are fine if they verify one behavior

**Anti-patterns to reject:**
- Tests that only assert `response.status_code == 200` without checking the body
- Tests that compute expected values the same way the code does
- Tests that depend on execution order or shared mutable state between tests
- Mocking the function under test instead of its dependencies

### 3. Code Organization

- Maintain the router-based structure: `app/routes/` for endpoint handlers, `app/models.py` (or `app/models/`) for SQLAlchemy models, `app/schemas/` for Pydantic request/response models
- Separate concerns: route handlers should be thin -- delegate business logic to service functions in `app/services/`
- Database session management belongs in `app/db.py` -- use FastAPI's `Depends()` for session injection, never create sessions inside route handlers directly
- Test files in a top-level `tests/` directory mirroring the app structure: `tests/test_products.py`, `tests/test_inventory.py`
- No grab-bag utility files -- name helpers by what they do (e.g., `app/stock_calculator.py`, not `app/utils.py`)
- One SQLAlchemy model per logical entity -- split `models.py` into `app/models/` package if it exceeds ~200 lines

### 4. Quality Gates

**Automated (must pass before commit):**
- `ruff check .` -- zero warnings, no rule disabling without an inline comment
- `ruff format --check .` -- code must be formatted (line-length 88 per pyproject.toml)
- `mypy .` -- zero errors, strict mode enabled
- `pytest` -- all tests pass, no `@pytest.mark.skip` on pre-existing tests without a linked issue

**Manual:**
- Read the module you are changing before writing new code
- Run `pytest` for the modules you touched before declaring work complete
- If you changed a Pydantic schema or SQLAlchemy model, verify that Alembic migration is generated and reviewed

### 5. Error Handling

- Use FastAPI's `HTTPException` for expected client errors (400, 404, 409) -- always include a meaningful `detail` string
- Never return raw 500 errors to the client -- add a global exception handler that logs the full traceback and returns a generic error response
- All external HTTP calls via `httpx` must set explicit timeouts: `httpx.AsyncClient(timeout=10.0)` -- never use the default (no timeout)
- Log enough context to reproduce issues: entity ID, operation name, error traceback -- use Python's `logging` module with structured fields
- Database errors (IntegrityError, OperationalError) must be caught at the service layer and translated to appropriate HTTP responses -- never let raw SQLAlchemy exceptions leak to the client
- Use consistent error response format across all endpoints:
  ```json
  {"detail": "Human-readable message", "code": "PRODUCT_NOT_FOUND"}
  ```

### 6. Operational Rules

**Resilience:**
- Graceful shutdown on SIGINT/SIGTERM -- FastAPI/Uvicorn handles this by default, but ensure database connections are properly closed in a shutdown event handler
- No single request failure should crash the server process
- Health check endpoint at `/health` that verifies database connectivity

**Data integrity:**
- Multi-table writes (e.g., creating a product and initial inventory) must be wrapped in a SQLAlchemy transaction
- Validate all external input with Pydantic at the API boundary before it reaches the service or database layer
- Restocking operations should be idempotent when possible -- use unique constraints or conditional updates to prevent duplicate stock additions

**Performance:**
- API responses should target <100ms for single-entity lookups, <500ms for list endpoints
- Use SQLAlchemy's `selectinload` or `joinedload` to avoid N+1 queries when loading products with inventory
- Database connection pooling via SQLAlchemy's pool settings -- configure `pool_size`, `max_overflow`, and `pool_timeout`

### 7. Database Rules

- Schema managed via Alembic migrations -- never use `Base.metadata.create_all` in production (current `startup` event is acceptable only for development)
- Generate migrations with `alembic revision --autogenerate -m "description"`, then review the generated migration before applying
- Every column used in WHERE or ORDER BY clauses must have an index -- particularly `products.sku`, `inventory.product_id`, `inventory.warehouse`
- Use SQLAlchemy's `Numeric` type (not `Float`) for the `price` column to avoid floating-point precision issues
- Connection string and credentials via environment variables loaded with `python-dotenv` -- never hardcoded
- Multi-table writes must use explicit transactions via `async with session.begin()`

### 8. API Rules

- Validate all request bodies and query parameters with Pydantic v2 schemas -- define separate schemas for create, update, and response (e.g., `ProductCreate`, `ProductUpdate`, `ProductResponse`)
- Use FastAPI's dependency injection (`Depends()`) for database sessions, authentication, and shared logic -- never instantiate dependencies manually in handlers
- Consistent response format: list endpoints return `{"items": [...], "total": int}`, single-entity endpoints return the entity directly
- Use appropriate HTTP status codes: 201 for creation, 204 for deletion, 409 for conflicts (duplicate SKU), 422 for validation errors (FastAPI default)
- All list endpoints must support pagination (`limit` and `offset` query params) -- never return unbounded result sets
- Use FastAPI's built-in OpenAPI docs (`/docs`) -- keep endpoint descriptions and response models up to date so the auto-generated docs are useful

### 9. Security Rules

- Secrets (database URL, API keys) in `.env` file, loaded via `python-dotenv`, never committed to git -- validate required env vars on application startup
- Never log sensitive data (passwords, tokens, full database connection strings) at any log level
- Sanitize all user-provided strings before using in database queries -- SQLAlchemy's parameterized queries handle SQL injection, but watch for raw SQL usage
- Add `.env` and `*.pem` to `.gitignore`
- Rate limiting on public endpoints to prevent inventory scraping or abuse (consider `slowapi` or middleware-based approach)

### 10. Domain-Specific Rules (Inventory Management)

- **Stock quantity must never go negative** -- enforce at the database level with a CHECK constraint (`quantity >= 0`) and validate in the service layer before writes
- **SKU uniqueness is critical** -- the unique constraint on `products.sku` must be preserved; handle `IntegrityError` on duplicate SKU creation with a clear 409 response
- **Warehouse operations must be atomic** -- transferring stock between warehouses (decrement source, increment destination) must be a single transaction; partial transfers corrupt inventory data
- **Restocking events should be auditable** -- log or store restocking history (who, when, how much, which warehouse) for traceability
- **Real-time availability calculations** must account for all warehouses -- never cache warehouse-level quantities without a clear invalidation strategy
- **Concurrent stock updates** -- use optimistic locking (SQLAlchemy's `version_id_col`) or `SELECT ... FOR UPDATE` to prevent lost updates when multiple requests modify the same inventory item simultaneously
