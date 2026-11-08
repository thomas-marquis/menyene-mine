.PHONY: help install lint format typecheck test test-unit test-integration run run-frontend db-migrate db-upgrade clean ci-local

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
	@echo "  run-frontend - Start frontend development server"
	@echo "  db-migrate  - Create new database migration"
	@echo "  db-upgrade  - Apply database migrations"
	@echo "  clean       - Clean build artifacts"
	@echo "  all         - Run lint, format, typecheck, and tests"
	@echo "  ci-local    - Test CI pipeline locally with act"

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

# Run frontend development server
run-frontend:
	@if command -v nvm &> /dev/null; then \
		nvm use 24 2>/dev/null || echo "Node 24 not installed, using default"; \
	fi
	cd mm-webapp && npm run dev

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

# Test CI pipeline locally with act
# Note: Requires act to be installed (./bin/act) and Docker running
# First run: ./bin/act -P ubuntu-latest=node:18-buster-slim
# Then run: make ci-local
ci-local:
	./bin/act pull_request -j test --bind
