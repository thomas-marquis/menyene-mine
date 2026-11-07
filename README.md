# menyene-mine

A python project scaffolded with [TriStack](https://tristack.space).

## Stack

- **Framework:** fastapi
- **ORM / DB layer:** sqlalchemy
- **Database:** sqlite
- **Migrations:** alembic
- **Package manager:** uv


## Getting Started

```bash
# 1. Install dependencies

uv sync

# 2. Create and run a database migration

uv run alembic revision --autogenerate -m "initial"

uv run alembic upgrade head

# 3. Start the dev server

uv run uvicorn src.main:app --reload
```

## API Docs

When the dev server is running, interactive API docs are available at `/docs`.
## Environment

Copy `env.example` to `.env`; it is read automatically on startup.
