.PHONY: help install lint format typecheck test test-unit test-integration run db-migrate db-upgrade clean

# Default target
help:
	@echo "Available targets:"
	@echo "  install     - Install dependencies"
	@echo "  lint        - Run linter"
	@echo "  format      - Format code"
	@echo "  typecheck   - Run type checker"
	@echo "  test        - Run all tests"
	@echo "  test-unit   - Run unit tests"
	@echo "  test-integration - Run integration tests"
	@echo "  run         - Start development server"
	@echo "  db-migrate  - Create new database migration"
	@echo "  db-upgrade  - Apply database migrations"
	@echo "  clean       - Clean build artifacts"
	@echo "  all         - Run lint, format, typecheck, and tests"

# Install dependencies
install:
	uv sync

# Lint
lint:
	uv run ruff check .

# Format
format:
	uv run ruff check . --fix
	uv run ruff format .

# Type check
typecheck:
	uv run mypy .

# Tests
test: test-unit test-integration

test-unit:
	uv run pytest tests/unit/

test-integration:
	uv run behave tests/integration/features/

# Run development server
run:
	uv run uvicorn src.main:app --reload

# Database migrations
db-migrate:
	@echo "Enter migration message:"
	@read -r msg && uv run alembic revision --autogenerate -m "$$msg"

db-upgrade:
	uv run alembic upgrade head

# Clean
clean:
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf __pycache__
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Run all checks
all: lint format typecheck test-unit test-integration
