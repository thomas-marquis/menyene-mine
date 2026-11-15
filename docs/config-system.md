# Configuration System

This document describes the configuration system for menyene-mine, which provides:
- Environment-specific configuration
- Jinja2-templated prompts
- Centralized settings management

## Directory Structure

```
config/
├── .env                    # Environment variables (DO NOT COMMIT)
├── .env.example            # Example environment variables
├── __init__.py             # Config loading utilities
├── local/                  # Local development environment
│   ├── prompts/            # Jinja2 prompt templates
│   │   ├── system.jinja         # System prompt for recipe generation
│   │   ├── recipe_generation.jinja  # Recipe generation prompt
│   │   ├── prompt_validation.jinja  # Prompt validation prompt
│   │   └── recipe_validation.jinja  # Recipe validation prompt
│   └── settings.yaml       # Local-specific settings
└── (other environments)/   # Additional environments (e.g., production, staging)
```

## Environment Variables

The system uses a `.env` file in the `config/` directory. Copy `.env.example` to `.env` and configure your settings:

```bash
# Application
APP_NAME=menyene-mine
DEBUG=False
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
DATABASE_URL=sqlite+aiosqlite:///./menyene_mine.db

# Environment
ENVIRONMENT=local

# AI Configuration
AI_ENABLED=False
MISTRAL_API_KEY=your_api_key_here
AI_MODEL=mistral-medium
AI_MAX_DRAFTS=1
AI_TEMPERATURE=0.7

# LLM Judge Configuration
JUDGE_ENABLED=true
JUDGE_MODEL=
JUDGE_TEMPERATURE=0.3
JUDGE_MAX_TOKENS=500
```

## Environments

The system supports multiple environments through the `ENVIRONMENT` variable. Each environment can have its own:
- Prompt templates
- Settings
- Configuration

### Creating a New Environment

1. Create a new directory under `config/`:
   ```bash
   mkdir config/production
   ```

2. Create the `prompts/` subdirectory:
   ```bash
   mkdir config/production/prompts
   ```

3. Copy or create your environment-specific prompts:
   ```bash
   cp config/local/prompts/*.jinja config/production/prompts/
   ```

4. Create a `settings.yaml` for the environment:
   ```yaml
   # config/production/settings.yaml
   ai:
     enabled: true
     model: mistral-large
     max_drafts: 1
     temperature: 0.5
   
   judge:
     enabled: true
     temperature: 0.2
   ```

5. Set the environment variable:
   ```bash
   echo "ENVIRONMENT=production" >> config/.env
   ```

## Jinja2 Prompt Templates

All AI prompts are stored as Jinja2 templates, allowing for:
- Dynamic prompt generation
- Environment-specific customization
- Variable substitution
- Template inheritance

### Available Templates

| Template                  | Purpose                             | Variables                                                                         |
| ------------------------- | ----------------------------------- | --------------------------------------------------------------------------------- |
| `system.jinja`            | System prompt for recipe generation | `recipe_type`, `dietary_restrictions`, `cuisine_type`                             |
| `recipe_generation.jinja` | User prompt for generation          | `prompt`, `num_recipes`, `constraints`, `preferences`                             |
| `prompt_validation.jinja` | Validates user prompts              | `prompt`, `strict_mode`                                                           |
| `recipe_validation.jinja` | Validates generated recipes         | `original_prompt`, `recipe`, `strict_mode`, `min_ingredients`, `min_instructions` |

### Template Syntax

Templates use standard Jinja2 syntax:

```jinja
{# Comments look like this #}
{{ variable }}  {# Variable substitution #}
{% if condition %}  {# Conditionals #}
  {{ variable }}
{% endif %}

{%- if recipe_type %}  {# Trim whitespace #}
You are an expert chef specializing in {{ recipe_type }} recipes.
{%- endif %}
```

### Example: Adding a New Template

1. Create a new file in `config/local/prompts/`:
   ```bash
   touch config/local/prompts/meal_planning.jinja
   ```

2. Add your template content:
   ```jinja
   {# Meal planning prompt #}
   Create a meal plan for {{ days }} days with {{ servings }} servings per meal.
   
   {%- if dietary_restrictions %}
   Dietary restrictions: {{ dietary_restrictions|join(', ') }}
   {%- endif %}
   
   {%- if budget %}
   Budget: {{ budget }}
   {%- endif %}
   
   Generate a detailed meal plan with:
   - Breakfast, lunch, and dinner for each day
   - Snack ideas
   - A consolidated grocery list
   ```

3. Use the template in your code:
   ```python
   from src.config import get_prompt_loader

   loader = get_prompt_loader()
   prompt = loader.render("meal_planning", days=7, servings=2, dietary_restrictions=["vegetarian"])
   ```

## Configuration Loading

The system provides utilities for loading configuration and prompts:

### ConfigLoader

```python
from src.config import ConfigLoader, get_config_loader

# Create a loader for a specific environment
loader = ConfigLoader(env="local")

# Load YAML configuration
settings = loader.load_yaml("settings")

# Load environment variables
env_vars = loader.load_env()

# Get global loader
config_loader = get_config_loader()
```

### PromptLoader

```python
from src.config import PromptLoader, get_prompt_loader

# Create a loader
loader = PromptLoader()

# List available templates
templates = loader.list_templates()

# Load a template
template = loader.load("system")

# Render a template with context
rendered = loader.render("recipe_generation", prompt="Make a cake", num_recipes=1)

# Get raw template content
raw = loader.get_raw("system")

# Get global loader
prompt_loader = get_prompt_loader()
```

## Settings Management

Application settings are managed through Pydantic's `BaseSettings` with automatic environment variable loading:

```python
from src.config import Settings, get_settings

# Get settings (cached)
settings = get_settings()

# Access settings
print(settings.ai_enabled)
print(settings.mistral_api_key)
print(settings.judge_enabled)

# Reset settings cache (for testing)
from src.config import reset_settings

reset_settings()
```

### Settings Hierarchy

Settings are loaded from multiple sources in this order (later sources override earlier ones):

1. Default values in the `Settings` class
2. Environment variables from `config/.env`
3. Explicitly set values when creating a `Settings` instance

## Dependency Injection

The system integrates with FastAPI's dependency injection:

```python
from src.di import get_ai_recipe_generator, get_llm_judge
from fastapi import Depends


@app.post("/generate")
async def generate_recipe(
    prompt: str,
    generator: RecipeGenerator = Depends(get_ai_recipe_generator),
    judge: LLMJudge = Depends(get_llm_judge),
):
    # Validate prompt
    is_valid, error = await judge.validate_prompt(prompt)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)

    # Generate recipe
    recipes = await generator.generate_recipes(prompt)
    return recipes
```

## Best Practices

1. **Environment Separation**: Keep environment-specific configuration separate
2. **Template Organization**: Group related templates together
3. **Variable Naming**: Use descriptive variable names in templates
4. **Default Values**: Provide sensible defaults in templates
5. **Validation**: Validate template rendering output
6. **Testing**: Test templates with various inputs

## Testing Configuration

```python
import pytest
from src.config import get_prompt_loader, reset_loaders


@pytest.fixture(autouse=True)
def reset_config():
    """Reset config before each test."""
    reset_loaders()
    yield


def test_prompt_rendering():
    loader = get_prompt_loader()
    prompt = loader.render("system")
    assert "expert chef" in prompt.lower()
```

## Troubleshooting

### Prompt Not Found

**Error**: `FileNotFoundError: Template not found`

**Solution**: 
- Check that the template exists in the correct environment directory
- Verify the environment name is correct
- Ensure the template has the `.jinja` extension

### Environment Variables Not Loading

**Error**: Environment variables from `.env` are not being loaded

**Solution**:
- Ensure `.env` is in the `config/` directory
- Check that the file has proper permissions
- Verify the file format (KEY=value)

### Template Rendering Errors

**Error**: `UndefinedError: 'variable' is not defined`

**Solution**:
- Check that all variables used in the template are passed to `render()`
- Verify variable names match exactly (case-sensitive)
- Use default values in templates: `{{ variable|default("default_value") }}`
