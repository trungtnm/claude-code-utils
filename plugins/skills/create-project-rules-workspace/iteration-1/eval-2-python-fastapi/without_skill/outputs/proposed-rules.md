# Coding Standards — Inventory API (Python / FastAPI)

These rules apply to all code in the `inventory-api` project. Follow them for every change.

---

## 1. Python Version and Language

- **Target Python 3.11+**. Use modern syntax: `X | Y` union types, `match` statements, `StrEnum`, `tomllib`, etc. where appropriate.
- All source files must be valid UTF-8 with no BOM.
- Prefer `from __future__ import annotations` at the top of every module to enable postponed evaluation of annotations.

## 2. Code Formatting and Linting

- **Ruff** is the sole linter and formatter. Configuration lives in `pyproject.toml`.
- Line length: **88 characters** (already configured).
- Run `ruff check --fix .` and `ruff format .` before every commit. All Ruff warnings must be resolved — no `# noqa` unless accompanied by a comment explaining why.
- Do not introduce additional linters (flake8, black, isort). Ruff replaces all of them.

## 3. Type Safety

- **mypy strict mode** is enabled (`strict = true` in `pyproject.toml`). All code must pass `mypy .` with zero errors.
- Every function and method must have complete type annotations for all parameters and the return type. No `Any` unless unavoidable and justified with a comment.
- Use `typing` or `collections.abc` types for generic containers: `Sequence`, `Mapping`, `Iterable` — not `list`, `dict` in annotations where an interface suffices.
- Pydantic models count as typed; keep `model_config` explicit rather than relying on defaults.

## 4. Project Structure

```
app/
  main.py          # FastAPI app factory and startup
  db.py            # Engine, session, Base
  models.py        # SQLAlchemy ORM models
  schemas/         # Pydantic request/response schemas (one file per domain)
  routes/          # APIRouter modules (one file per domain)
  services/        # Business logic (one file per domain)
  dependencies.py  # FastAPI dependency callables (get_db, auth, etc.)
tests/
  conftest.py      # Shared fixtures
  test_<module>.py # One test file per module
alembic/           # Database migrations
```

Rules:
- **Routes** contain only HTTP plumbing: parse request, call service, return response. No direct database queries in route handlers.
- **Services** contain business logic and database access. They receive a `AsyncSession` parameter — never import the session directly.
- **Schemas** define Pydantic models for request bodies, response bodies, and query parameters. Never return an ORM model directly from a route.
- Keep each domain (products, inventory) in its own file within `routes/`, `schemas/`, and `services/`.

## 5. FastAPI Conventions

- Use `APIRouter` in every route module. Mount routers in `main.py` with a `/api/` prefix.
- Use **lifespan context manager** instead of the deprecated `@app.on_event("startup")` / `@app.on_event("shutdown")` pattern.
- All route handlers must be `async def`. Do not mix sync and async handlers.
- Use FastAPI's `Depends()` for database sessions, authentication, and shared logic.
- Define explicit `response_model` on every route. Use `status_code` parameter for non-200 responses.
- Return appropriate HTTP status codes: `201` for creation, `204` for deletion, `404` for not found, `422` is automatic for validation errors.

## 6. Pydantic v2 Schemas

- Inherit from `pydantic.BaseModel`. Use `model_config = ConfigDict(from_attributes=True)` on response schemas that map from ORM models.
- Name schemas with a suffix indicating purpose: `ProductCreate`, `ProductRead`, `ProductUpdate`.
- Use `Annotated` types with `Field()` for validation constraints (min, max, regex, etc.).
- Never use `Optional[X]` — use `X | None` instead (Python 3.11+ syntax).
- Keep default values explicit. If a field can be `None`, declare `field: str | None = None`.

## 7. SQLAlchemy 2.0 and Database

- Use **SQLAlchemy 2.0 style** exclusively: `Mapped`, `mapped_column`, `DeclarativeBase`. Do not use legacy `Column()` / `relationship()` from 1.x style.
- Example migration from current code:
  ```python
  # Before (legacy)
  id = Column(Integer, primary_key=True)
  name = Column(String, nullable=False)

  # After (2.0 style)
  id: Mapped[int] = mapped_column(primary_key=True)
  name: Mapped[str] = mapped_column(String, nullable=False)
  ```
- Use `async` engine and `AsyncSession` for all database operations.
- Always use explicit column types in `mapped_column` — do not rely on type inference for database DDL.
- Use `datetime.datetime` with timezone-aware values (`datetime.now(UTC)`). Never use `datetime.utcnow()` — it is deprecated in Python 3.12+.
- For monetary values (e.g., `price`), use `Numeric(precision=10, scale=2)` instead of `Float` to avoid floating-point rounding.
- Database migrations are managed via **Alembic**. Every schema change requires a migration — never rely on `create_all()` outside of development.

## 8. Dependency Injection

- Define a `get_db` async generator in `dependencies.py` that yields an `AsyncSession` and properly closes it.
- Inject `db: AsyncSession = Depends(get_db)` into route handlers, then pass it to service functions.
- Never create sessions inside service functions.

## 9. Error Handling

- Raise `fastapi.HTTPException` with clear `detail` messages for expected error cases (not found, conflict, forbidden).
- For unexpected errors, let FastAPI's default 500 handler manage them — do not catch `Exception` broadly.
- Use custom exception handlers registered via `app.exception_handler()` only when you need a non-standard response shape.
- Never expose internal tracebacks or database errors to the client.

## 10. Testing

- Use **pytest** with **pytest-asyncio** (`asyncio_mode = "auto"` in `pyproject.toml`).
- Use **httpx.AsyncClient** with `ASGITransport` to test the FastAPI app, not `TestClient` (which is sync).
- Test structure mirrors source: `tests/test_products.py` tests `routes/products.py`, etc.
- Each test must be independent — use fixtures for database setup/teardown. Use a transactional test pattern (rollback after each test).
- Cover: all happy-path routes, all validation error cases, all 404/conflict cases, and service-layer business logic.
- Minimum expectation: every route handler has at least one positive and one negative test.
- Name tests descriptively: `test_create_product_returns_201`, `test_create_product_duplicate_sku_returns_409`.

## 11. Configuration and Environment

- Use **pydantic-settings** (`BaseSettings`) for configuration. Load from environment variables and `.env` files.
- Never hardcode secrets, database URLs, or API keys.
- `.env` files must be in `.gitignore`. Provide a `.env.example` with placeholder values.
- Required settings: `DATABASE_URL`, `DEBUG`, `ALLOWED_ORIGINS`.

## 12. Async Discipline

- All I/O operations (database, HTTP calls, file reads) must be `async`.
- Never call blocking I/O inside an `async def` function without `asyncio.to_thread()`.
- Use `httpx.AsyncClient` for outbound HTTP requests (already a dependency).

## 13. Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Files/modules | snake_case | `inventory_service.py` |
| Classes | PascalCase | `InventoryItem` |
| Functions/methods | snake_case | `get_product_by_sku` |
| Constants | UPPER_SNAKE_CASE | `MAX_RESTOCK_QUANTITY` |
| Route paths | kebab-case | `/api/products/{product_id}/stock-levels` |
| Pydantic schemas | PascalCase + purpose suffix | `ProductCreate`, `ProductRead` |
| SQLAlchemy tables | plural snake_case | `products`, `inventory_items` |

## 14. API Design

- Follow REST conventions: `GET` for reads, `POST` for creates, `PUT`/`PATCH` for updates, `DELETE` for deletes.
- Use plural nouns for resource paths: `/api/products`, `/api/inventory`.
- Use path parameters for resource identity: `/api/products/{product_id}`.
- Use query parameters for filtering, sorting, and pagination.
- Implement pagination on all list endpoints. Use `limit`/`offset` or cursor-based pagination.
- Return consistent response envelopes for list endpoints: `{"items": [...], "total": N}`.

## 15. Security

- Validate all input via Pydantic schemas — never trust raw request data.
- Use parameterized queries (SQLAlchemy handles this) — never construct raw SQL with string interpolation.
- Set CORS origins explicitly — never use `allow_origins=["*"]` in production.
- Add rate limiting middleware for public endpoints.

## 16. Logging

- Use Python's `logging` module with structured log messages.
- Create module-level loggers: `logger = logging.getLogger(__name__)`.
- Log at appropriate levels: `DEBUG` for development tracing, `INFO` for request lifecycle, `WARNING` for recoverable issues, `ERROR` for failures.
- Never use `print()` for application logging.

## 17. Documentation

- All public functions, classes, and modules must have docstrings (Google style).
- FastAPI route handlers should use the `summary` and `description` parameters for OpenAPI documentation.
- Keep `README.md` updated with setup instructions, environment requirements, and how to run migrations.

## 18. Git and Workflow

- Write clear, imperative commit messages: `Add stock level endpoint`, not `added stuff`.
- Keep commits atomic — one logical change per commit.
- Never commit `.env`, `__pycache__/`, `.mypy_cache/`, or IDE configuration files.
- Required in `.gitignore`: `.env`, `__pycache__/`, `*.pyc`, `.mypy_cache/`, `.ruff_cache/`, `*.db`.
