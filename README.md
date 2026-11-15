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

1. Copy `config/local/.env.example` to `config/local/.env`
2. Set `AI_ENABLED=true`
3. Add your `MISTRAL_API_KEY`
4. Configure `AI_MODEL` and `AI_MAX_DRAFTS` as needed

```bash
AI_ENABLED=true
MISTRAL_API_KEY=your_api_key_here
AI_MODEL=mistral-medium
AI_MAX_DRAFTS=1
```

The system automatically switches between mock and real AI based on configuration. All prompts are loaded from Jinja2 templates in the `config/{environment}/prompts/` directory.

## Environment

The project uses a structured configuration system with environment-specific settings.

### Configuration Structure

```
config/
└── local/                  # Local development environment (default)
    ├── .env                # Environment variables (DO NOT COMMIT)
    ├── .env.example        # Example environment variables
    ├── prompts/            # Jinja2 prompt templates
    │   ├── recipe_generation.jinja
    │   ├── prompt_validation.jinja
    │   └── system.jinja
    └── settings.yaml       # All settings with env var placeholders
```

### Configuration Path

The configuration directory path can be specified via the `MENYENEMINE_CONFIG_PATH` environment variable.
Default: `config/local`

```bash
# Use default config path
export MENYENEMINE_CONFIG_PATH=config/local

# Or specify a custom path
export MENYENEMINE_CONFIG_PATH=/path/to/your/config
```

### Setup

1. Copy `.env.example` to `.env` in the config/local directory:
   ```bash
   cp config/local/.env.example config/local/.env
   ```

2. Edit `config/local/.env` with your secret values:
   ```bash
   MISTRAL_API_KEY=your_api_key_here
   ```

3. Edit `config/local/settings.yaml` to configure your settings:
   ```yaml
   ai:
     enabled: true
     model: mistral-medium
     max_drafts: 1
     mistral_api_key: $MISTRAL_API_KEY  # Resolved from .env or environment
   
   judge:
     enabled: true
     temperature: 0.3
   ```

### Custom Environments

To create a new environment (e.g., `production`):

1. Create the environment directory:
   ```bash
   mkdir -p config/production/prompts
   ```

2. Copy templates and settings:
   ```bash
   cp config/local/prompts/*.jinja config/production/prompts/
   cp config/local/settings.yaml config/production/
   ```

3. Edit `config/production/settings.yaml` with production settings

4. Set the config path:
   ```bash
   export MENYENEMINE_CONFIG_PATH=config/production
   ```

### Settings with Environment Variables

The `settings.yaml` file supports environment variable placeholders:
- `$VAR_NAME` - Simple syntax
- `${VAR_NAME}` - Braced syntax (useful when followed by non-word characters)

Example:
```yaml
ai:
  mistral_api_key: $MISTRAL_API_KEY
  model: mistral-medium

judge:
  model: ${JUDGE_MODEL:-mistral-medium}  # With default value
```

These placeholders are resolved from:
1. Environment variables
2. Values from `.env` file in the config directory

### Prompt Customization

All AI prompts are stored as Jinja2 templates in `config/{environment}/prompts/`. You can:
- Modify existing prompts
- Add new prompt templates
- Create environment-specific variations

The system automatically loads prompts from the appropriate environment directory.
