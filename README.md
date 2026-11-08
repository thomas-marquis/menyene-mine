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

## Features

### Recipe Builder (AI-Powered)

The Recipe Builder tool allows you to generate recipe drafts from text prompts using AI:

1. **Generate Recipes**: Enter a prompt (e.g., "Create a quick vegetarian pasta recipe") and the AI will generate recipe ideas
2. **Manage Drafts**: View, filter, validate, or reject generated drafts
3. **Create Recipes**: Validate drafts to add them to your recipe catalog
4. **Track Status**: Drafts can be in three states: draft, validated, or rejected

**API Endpoints:**
- `POST /api/v1/recipe-drafts/generate` - Generate drafts from a prompt
- `GET /api/v1/recipe-drafts` - List all drafts (with status filtering)
- `GET /api/v1/recipe-drafts/stats` - Get draft statistics
- `GET /api/v1/recipe-drafts/{id}` - Get a specific draft
- `POST /api/v1/recipe-drafts/{id}/validate` - Validate a draft (creates a recipe)
- `POST /api/v1/recipe-drafts/{id}/reject` - Reject a draft
- `DELETE /api/v1/recipe-drafts/{id}` - Delete a draft

**Frontend Pages:**
- `/recipes/builder` - AI Recipe Builder form
- `/recipes/drafts` - List all drafts with tabs
- `/recipes/drafts/:id` - View and manage individual draft

### AI Configuration

The system uses a **mock AI generator** by default for testing. To enable real AI generation:

1. Copy `.env.example` to `.env`
2. Set `AI_ENABLED=true`
3. Add your `MISTRAL_API_KEY`
4. Configure `AI_MODEL` and `AI_MAX_DRAFTS` as needed

```bash
AI_ENABLED=true
MISTRAL_API_KEY=your_api_key_here
AI_MODEL=mistral-medium
AI_MAX_DRAFTS=10
```

The system automatically switches between mock and real AI based on configuration.

## Environment

Copy `.env.example` to `.env`; it is read automatically on startup.
