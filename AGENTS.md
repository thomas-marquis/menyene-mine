# AGENTS.md

## Architecture

FastAPI REST API following hexagonal architecture.

**Structure under `src`:**
- `domain/` - Core business logic
  - `entities/` - Business objects (e.g., `item.py`) - MUST use dataclasses, NO external dependencies
  - `ports/` - Interfaces/abstract contracts (e.g., `item_repository.py`)
- `infra/` - Infrastructure concerns
  - `db.py` - Async SQLAlchemy session factory
  - `models/` - SQLAlchemy models (e.g., `item.py`)
  - `repositories/` - DB implementations (e.g., `item_repository.py`)
- `controllers/` - Delivery layer
  - `rest/` - REST API
    - `routes.py` - Route definitions
    - `schemas.py` - Pydantic request/response models
    - `middlewares.py` - Middleware components
- `use_cases/` - Application use cases (e.g., `item_use_cases.py`)
- `di.py` - Dependency injection setup
- `settings.py` - Pydantic Settings from `.env`
- `shared/` - Utilities (MUST NOT have external dependencies)
  - `logging.py` - Logging setup
- `resources/` - Static resources (at project root)
  - `templates/` - Jinja2 templates for formatting output (not for AI prompts)

**Structure under `tests`:**

The `tests` folder mirrors the `src` structure for unit tests, and has a separate `integration` folder for integration tests.

## Key Files

- `src/main.py` - App factory with lifespan
- `src/db.py` - Re-exports from `infra/db.py` for backward compatibility
- `src/config.py` - Re-exports from `settings.py` for backward compatibility
- `src/exceptions.py` - Exception handlers

## DI

Centralized in `src/di.py`. Uses FastAPI native DI + custom dependencies:
- `get_item_repository()` - Creates `ItemRepository` from session
- `get_item_use_cases()` - Creates `ItemUseCases` from repository

## Commands

Use `make` for common operations (see Makefile):

```bash
make install      # Install dependencies
make run          # Start dev server
make test         # Run all tests
make test-unit    # Run unit tests
make lint         # Run linter
make format       # Format code
make typecheck    # Run type checker
make all          # Run lint, format, typecheck, and tests
make db-migrate   # Create migration (prompts for message)
make db-upgrade   # Apply migrations
make clean        # Clean build artifacts
```

Direct commands:
```bash
uv sync
uv run uvicorn src.main:app --reload
uv run pytest [tests/unit/test_health.py]
uv run ruff check . && uv run ruff format --check .
uv run mypy .
uv run alembic revision --autogenerate -m "msg"
uv run alembic upgrade head
```

**Important**: Always run python commands or modules via `uv run` to ensure the correct environment is used.

## Testing

- **Unit tests**: pytest in `tests/unit/`
  - Naming: `test_should<action>_when_<condition>`
  - Structure: Use `# Given`, `# When`, `# Then` comments
- **Integration tests**: behave in `tests/integration/`
  - Feature files: `tests/integration/features/*.feature` (Gherkin)
  - Step definitions: `tests/integration/steps/*.py`
  - Configuration: `behave.ini`
  - Deps: behave, pytest, pytest-asyncio, pytest-mock

## Quality

Python 3.13, line-length 120, strict mypy. CI order: lint → format → typecheck → test.

**Import Rules:**
- **NEVER** import modules inside functions or methods
- All imports MUST be placed at the top of the file
- This ensures proper dependency management and static analysis

**Coding Style:**
- **ALWAYS** prefix internal (non-public) attributes and methods with underscore `_`
- This includes instance variables, class variables, and helper methods that are not part of the public API
- Example: `self._settings`, `self._llm`, `self._validate_input()`
- Use clear and meaningful objects and methods names instead of comments, this ensure the code is readable and looks human-written
- Place the exposed public API at the top of the class, and private methods below

**Dependency Injection:**
- **ALWAYS** make injected dependencies non-optional (no None default)
- This ensures dependencies are always provided and eliminates the need for None checks
- Only use optional dependencies when there's a true good reason (e.g., truly optional functionality)
- Example: `def __init__(self, llm: BaseChatModel, settings: Settings)` not `def __init__(self, llm: BaseChatModel | None = None)`
- **NEVER** inject the whole Settings object, only inject the specific values needed
- This reduces coupling and makes dependencies explicit
- Example: `def __init__(self, llm: BaseChatModel, max_retries: int = 3)` not `def __init__(self, llm: BaseChatModel, settings: Settings)`

**JSDoc Rules:**
- **ONLY** add JSDoc on component definitions, props/interface definitions, and exported-file-root-level functions
- **NEVER** add JSDoc on inner functions or private methods
- **NEVER** add inline comments to explain what code does - use meaningful names instead
- Use clear and descriptive names for variables, functions, and parameters that make the purpose obvious
- Example: Use `fetchRecipesFromServer` instead of `// This function fetches recipes from the server`

## Database

SQLite + aiosqlite async, SQLAlchemy ORM. Session via `AsyncSession` from `src/infra/db.py`.
